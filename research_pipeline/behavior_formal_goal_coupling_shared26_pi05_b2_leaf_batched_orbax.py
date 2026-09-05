from __future__ import annotations

import asyncio
import copy
import gc
import hashlib
from typing import Any, Sequence

import jax
import numpy as np
import tensorstore as ts
from orbax.checkpoint._src.metadata import sharding as sharding_metadata
from orbax.checkpoint._src.multihost import multihost
from orbax.checkpoint._src.serialization import replica_slices
from orbax.checkpoint._src.serialization import serialization
from orbax.checkpoint._src.serialization import type_handlers as th
from orbax.checkpoint._src.serialization import types


DEFAULT_D2H_BATCH_BYTES = 8_000_000_000


def _array_nbytes(value: jax.Array) -> int:
    return int(np.prod(value.shape, dtype=np.int64)) * int(np.dtype(value.dtype).itemsize)


def _groups_by_bytes(values: Sequence[jax.Array], limit_bytes: int) -> list[list[int]]:
    if limit_bytes <= 0:
        raise ValueError("limit_bytes must be positive")
    groups: list[list[int]] = []
    current: list[int] = []
    current_bytes = 0
    for i, value in enumerate(values):
        nbytes = _array_nbytes(value)
        if nbytes > limit_bytes:
            raise ValueError(f"single leaf exceeds D2H batch limit: index={i} bytes={nbytes} limit={limit_bytes}")
        if current and current_bytes + nbytes > limit_bytes:
            groups.append(current)
            current = []
            current_bytes = 0
        current.append(i)
        current_bytes += nbytes
    if current:
        groups.append(current)
    return groups


def _single_fragment_fingerprint(rslices: replica_slices.ReplicaSlices, info: types.ParamInfo) -> dict[str, Any]:
    fragments = rslices.to_fragments().fragments
    if len(fragments) != 1:
        raise RuntimeError(f"B2 qualification requires one full local fragment per array: {info.name} fragments={len(fragments)}")
    fragment = fragments[0]
    arr = np.asarray(fragment.value)
    if tuple(arr.shape) != tuple(rslices.global_shape):
        raise RuntimeError(f"B2 fragment is not full array: {info.name} {arr.shape}/{rslices.global_shape}")
    if not arr.flags.c_contiguous:
        raise RuntimeError(f"B2 host fragment is not C contiguous: {info.name}")
    raw = memoryview(arr).cast("B")
    digest = hashlib.sha256(raw).hexdigest()
    return {
        "name": info.name,
        "shape": list(arr.shape),
        "dtype": str(arr.dtype),
        "nbytes": int(arr.nbytes),
        "sha256": digest,
    }


class LeafBatchedArrayHandler(th.ArrayHandler):
    """Orbax JAX-array handler with bounded leaf-batched D2H staging.

    The TensorStore/OCDBT write specs and per-array destinations remain the
    standard Orbax ones. Only the lifetime of host staging is changed: leaves
    are transferred and fully written in deterministic byte-bounded groups.
    ArrayMetadataStore is written exactly once after all groups complete.
    """

    def __init__(self, *, d2h_batch_bytes: int = DEFAULT_D2H_BATCH_BYTES, **kwargs: Any):
        super().__init__(**kwargs)
        self.d2h_batch_bytes = int(d2h_batch_bytes)
        self.fingerprints: list[dict[str, Any]] = []
        self.batch_manifest: list[dict[str, Any]] = []

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

        for batch_index, indices in enumerate(groups):
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

            await asyncio.gather(*write_coros)
            await sharding_txn.commit_async()

            all_array_metadatas.extend(batch_metadatas)
            all_fingerprints.extend(batch_fingerprints)
            batch_manifest.append(
                {
                    "batch_index": batch_index,
                    "leaf_indices": list(indices),
                    "leaf_count": len(indices),
                    "device_bytes": batch_device_bytes,
                }
            )
            del host_values, batch_fingerprints, write_coros, batch_metadatas
            gc.collect()

        if self._array_metadata_store is not None:
            parent_dirs = {str(info.parent_dir) for info in infos}
            if len(parent_dirs) != 1 or infos[0].parent_dir is None:
                raise RuntimeError(f"unexpected array metadata parent dirs: {parent_dirs}")
            await self._array_metadata_store.write(
                checkpoint_dir=infos[0].parent_dir,
                array_metadatas=all_array_metadatas,
                process_index=multihost.process_index(),
            )

        self.fingerprints = all_fingerprints
        self.batch_manifest = batch_manifest
        return []


def clone_global_registry_with_leaf_batched_array_handler(
    *, d2h_batch_bytes: int = DEFAULT_D2H_BATCH_BYTES,
) -> tuple[types.TypeHandlerRegistry, LeafBatchedArrayHandler]:
    default = th.GLOBAL_TYPE_HANDLER_REGISTRY.get(jax.Array)
    if not isinstance(default, th.ArrayHandler):
        raise RuntimeError(f"unexpected default jax.Array handler: {type(default)}")
    handler = LeafBatchedArrayHandler(
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
