from __future__ import annotations

import asyncio
import copy
import gc
from typing import Any, Sequence

import jax
import tensorstore as ts
from orbax.checkpoint._src.multihost import multihost
from orbax.checkpoint._src.serialization import replica_slices
from orbax.checkpoint._src.serialization import serialization
from orbax.checkpoint._src.serialization import type_handlers as th
from orbax.checkpoint._src.serialization import types

from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b2_leaf_batched_orbax import (
    DEFAULT_D2H_BATCH_BYTES,
    _array_nbytes,
    _groups_by_bytes,
    _single_fragment_fingerprint,
)
from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_writeback_cache import (
    reclaim_completed_ocdbt_data_blobs,
    snapshot_ocdbt_data_blobs,
)


class WritebackAwareLeafBatchedArrayHandler(th.ArrayHandler):
    """B3: B2 leaf-batched D2H plus post-write OCDBT cache reclamation."""

    def __init__(self, *, d2h_batch_bytes: int = DEFAULT_D2H_BATCH_BYTES, **kwargs: Any):
        super().__init__(**kwargs)
        self.d2h_batch_bytes = int(d2h_batch_bytes)
        self.fingerprints: list[dict[str, Any]] = []
        self.batch_manifest: list[dict[str, Any]] = []
        self.reclamation_manifest: list[dict[str, Any]] = []

    async def serialize(
        self,
        values: Sequence[jax.Array],
        infos: Sequence[types.ParamInfo],
        args: Sequence[types.SaveArgs] | None = None,
    ):
        args = list(args or [types.SaveArgs()] * len(values))
        th.check_input_arguments(values, infos, args)
        th.check_array_values(values, infos)
        if not values:
            self.fingerprints = []
            self.batch_manifest = []
            self.reclamation_manifest = []
            return []

        self._ext_metadata = {}
        arrays: list[jax.Array] = []
        for value, info in zip(values, infos):
            if jax.dtypes.issubdtype(value.dtype, jax.dtypes.prng_key):
                arrays.append(jax.random.key_data(value))
                self._ext_metadata[info.name] = {
                    th.array_metadata_lib.RANDOM_KEY_IMPL: str(jax.random.key_impl(value))
                }
            else:
                arrays.append(value)

        pinned = [info.enable_pinned_host_transfer for info in infos]
        if not (all(pinned) or not any(pinned)):
            raise RuntimeError("mixed pinned-host transfer settings are not supported")

        groups = _groups_by_bytes(arrays, self.d2h_batch_bytes)
        all_array_metadatas = []
        all_fingerprints: list[dict[str, Any]] = []
        batch_manifest: list[dict[str, Any]] = []
        reclamation_manifest: list[dict[str, Any]] = []

        parent_dirs = {str(info.parent_dir) for info in infos}
        if len(parent_dirs) != 1 or infos[0].parent_dir is None:
            raise RuntimeError(f"B3 requires one item parent dir: {parent_dirs}")
        item_root = infos[0].parent_dir

        for batch_index, indices in enumerate(groups):
            before_blobs = snapshot_ocdbt_data_blobs(item_root)
            batch_arrays = [arrays[i] for i in indices]
            batch_infos = [infos[i] for i in indices]
            batch_args = [args[i] for i in indices]
            batch_device_bytes = sum(_array_nbytes(v) for v in batch_arrays)

            host_values = replica_slices.transfer_arrays_to_host(
                batch_arrays,
                self._replica_id,
                self._use_replica_parallel,
                enable_pinned_host_transfer=batch_infos[0].enable_pinned_host_transfer,
            )
            batch_fingerprints = [
                _single_fragment_fingerprint(value, info)
                for value, info in zip(host_values, batch_infos)
            ]

            write_coros = []
            sharding_txn = ts.Transaction()
            batch_metadatas = []
            for value, info, arg in zip(host_values, batch_infos, batch_args):
                write_spec = self._get_array_write_spec(
                    info,
                    value,
                    use_ocdbt=info.is_ocdbt_checkpoint,
                    process_index=th.get_process_index_for_subdir(info.is_ocdbt_checkpoint),
                    arg=arg,
                )
                write_coros.append(
                    serialization.async_serialize_from_host(
                        value,
                        write_spec.json,
                        primary_host=self._primary_host,
                        context=info.ts_context,
                        transaction=None,
                        byte_limiter=info.byte_limiter,
                    )
                )
                if self._enable_write_sharding_file and value.sharding is not None:
                    write_coros.append(self._serialize_sharding(value.sharding, info, sharding_txn))
                batch_metadatas.append(write_spec.metadata)

            # D0 ordering invariant: all TensorStore writes complete first.
            await asyncio.gather(*write_coros)
            # Sharding transaction completion is also before any cache advice.
            await sharding_txn.commit_async()
            reclaimed = reclaim_completed_ocdbt_data_blobs(item_root, before_blobs)

            all_array_metadatas.extend(batch_metadatas)
            all_fingerprints.extend(batch_fingerprints)
            reclamation_manifest.append(
                {
                    "batch_index": batch_index,
                    "reclaimed_blob_count": len(reclaimed),
                    "reclaimed_bytes": sum(int(x["size"]) for x in reclaimed),
                    "blobs": reclaimed,
                }
            )
            batch_manifest.append(
                {
                    "batch_index": batch_index,
                    "leaf_indices": list(indices),
                    "leaf_count": len(indices),
                    "device_bytes": batch_device_bytes,
                }
            )
            del host_values, batch_fingerprints, write_coros, batch_metadatas, reclaimed
            gc.collect()

        if self._array_metadata_store is not None:
            await self._array_metadata_store.write(
                checkpoint_dir=item_root,
                array_metadatas=all_array_metadatas,
                process_index=multihost.process_index(),
            )

        self.fingerprints = all_fingerprints
        self.batch_manifest = batch_manifest
        self.reclamation_manifest = reclamation_manifest
        return []


def clone_global_registry_with_writeback_aware_leaf_batched_array_handler(
    *, d2h_batch_bytes: int = DEFAULT_D2H_BATCH_BYTES,
) -> tuple[types.TypeHandlerRegistry, WritebackAwareLeafBatchedArrayHandler]:
    default = th.GLOBAL_TYPE_HANDLER_REGISTRY.get(jax.Array)
    if not isinstance(default, th.ArrayHandler):
        raise RuntimeError(f"unexpected default jax.Array handler: {type(default)}")
    handler = WritebackAwareLeafBatchedArrayHandler(
        d2h_batch_bytes=d2h_batch_bytes,
        metadata_key=default._metadata_key,
        primary_host=default._primary_host,
        replica_id=default._replica_id,
        use_replica_parallel=default._use_replica_parallel,
        enable_write_sharding_file=default._enable_write_sharding_file,
        array_metadata_store=default._array_metadata_store,
    )
    registry = copy.copy(th.GLOBAL_TYPE_HANDLER_REGISTRY)
    registry._type_registry = list(th.GLOBAL_TYPE_HANDLER_REGISTRY._type_registry)
    registry._typestr_registry = dict(th.GLOBAL_TYPE_HANDLER_REGISTRY._typestr_registry)
    registry.add(jax.Array, handler, override=True, ignore_warnings=True)
    return registry, handler
