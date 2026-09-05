from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np
import orbax.checkpoint as ocp

from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_writeback_aware_orbax import (
    clone_global_registry_with_writeback_aware_leaf_batched_array_handler,
)
from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_writeback_cache import (
    self_cgroup_memory_snapshot,
)

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
EXPECTED_MACHINE_ID = "c4046d3ca4454a958f5de081aac4dc2e"
SYNTHETIC_SEED = 20260905
LEAF_COUNT = 6
LEAF_ELEMENTS = 16_777_216
LEAF_BYTES = LEAF_ELEMENTS * 4
TOTAL_BYTES = LEAF_COUNT * LEAF_BYTES
D2H_BATCH_BYTES = 128 * 1024**2
MEMORY_MAX_BYTES = 2 * 1024**3
MIN_SINGLE_FILE_DROP_BYTES = 1 * 1024**2
MIN_TOTAL_FILE_DROP_BYTES = 64 * 1024**2


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_binding(authority: dict[str, Any], key: str, path: Path) -> str:
    binding = authority.get("bindings", {}).get(key)
    if not isinstance(binding, dict):
        raise RuntimeError(f"D2 missing authority binding: {key}")
    actual = sha256_file(path)
    if binding.get("path") != str(path) or binding.get("sha256") != actual:
        raise RuntimeError(f"D2 authority binding drift: {key}")
    return actual


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def sha_array(value: Any) -> str:
    arr = np.asarray(value)
    return hashlib.sha256(memoryview(np.ascontiguousarray(arr)).cast("B")).hexdigest()


def cgroup_limits() -> dict[str, int]:
    rel = None
    for line in Path("/proc/self/cgroup").read_text().splitlines():
        if line.startswith("0::"):
            rel = line.split("::", 1)[1].lstrip("/")
            break
    if rel is None:
        raise RuntimeError("D2 requires cgroup v2")
    cg = Path("/sys/fs/cgroup") / rel
    raw_max = (cg / "memory.max").read_text().strip()
    raw_swap = (cg / "memory.swap.max").read_text().strip()
    return {
        "memory_max": -1 if raw_max == "max" else int(raw_max),
        "memory_swap_max": -1 if raw_swap == "max" else int(raw_swap),
    }


def tree_bytes(root: Path) -> tuple[int, int]:
    files = 0
    total = 0
    for path in root.rglob("*"):
        if path.is_file():
            files += 1
            total += path.stat().st_size
    return files, total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority", type=Path, required=True)
    ap.add_argument("--serializer", type=Path, required=True)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--development-review", type=Path, required=True)
    ap.add_argument("--d0d1d3", type=Path, required=True)
    ap.add_argument("--work-root", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)
    args = ap.parse_args()

    authority_path = args.authority.resolve()
    serializer_path = args.serializer.resolve()
    cache_path = args.cache.resolve()
    development_review_path = args.development_review.resolve()
    d0d1d3_path = args.d0d1d3.resolve()
    root = args.work_root.resolve()
    result = args.result.resolve()
    if Path("/etc/machine-id").read_text().strip() != EXPECTED_MACHINE_ID:
        raise RuntimeError("D2 may run only on host69 machine-id")

    authority = json.loads(authority_path.read_text())
    if authority.get("status") != "AUTHORIZED_PI05_B3_D2_OFFLINE_CACHE_ACCOUNTING":
        raise RuntimeError("D2 authority status drift")
    if authority.get("formal_run3_authorized") is not False:
        raise RuntimeError("D2 authority illegally opens run3")
    if authority.get("model_execution_authorized") is not False:
        raise RuntimeError("D2 authority illegally opens model execution")
    require_binding(authority, "runner", Path(__file__).resolve())
    require_binding(authority, "serializer", serializer_path)
    require_binding(authority, "cache", cache_path)
    require_binding(authority, "development_review", development_review_path)
    require_binding(authority, "d0d1d3", d0d1d3_path)
    frozen = authority.get("frozen_d2", {})
    expected = {
        "synthetic_seed": SYNTHETIC_SEED,
        "leaf_count": LEAF_COUNT,
        "leaf_bytes": LEAF_BYTES,
        "synthetic_total_bytes": TOTAL_BYTES,
        "d2h_batch_bytes": D2H_BATCH_BYTES,
        "memory_max_bytes": MEMORY_MAX_BYTES,
        "memory_swap_max_bytes": 0,
        "min_single_file_drop_bytes": MIN_SINGLE_FILE_DROP_BYTES,
        "min_total_file_drop_bytes": MIN_TOTAL_FILE_DROP_BYTES,
    }
    if authority.get("work_root") != str(root) or authority.get("result") != str(result):
        raise RuntimeError("D2 authority output-path drift")
    if frozen != expected:
        raise RuntimeError(f"D2 frozen contract drift: {frozen}")

    if root.exists() or result.exists():
        raise RuntimeError("D2 is single-shot: work root/result already exists")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"D2 must be CPU-only: {jax.devices()}")
    limits = cgroup_limits()
    if limits != {"memory_max": MEMORY_MAX_BYTES, "memory_swap_max": 0}:
        raise RuntimeError(f"D2 cgroup drift: {limits}")

    root.mkdir(parents=True)
    ckpt = root / "checkpoint"
    payload: dict[str, Any] = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-b3-d2-cache-accounting-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_B3_D2_CACHE_ACCOUNTING_HOLD",
        "scope": "SYNTHETIC_CPU_ONLY_NO_MODEL_NO_SCIENTIFIC_DATA",
        "authority_sha256": sha256_file(authority_path),
        "synthetic_seed": SYNTHETIC_SEED,
        "leaf_count": LEAF_COUNT,
        "leaf_bytes": LEAF_BYTES,
        "synthetic_total_bytes": TOTAL_BYTES,
        "synthetic_d2h_batch_bytes": D2H_BATCH_BYTES,
        "expected_batch_count": 3,
        "cgroup_limits": limits,
        "pass_thresholds": {
            "min_single_file_drop_bytes": MIN_SINGLE_FILE_DROP_BYTES,
            "min_total_file_drop_bytes": MIN_TOTAL_FILE_DROP_BYTES,
        },
        "model_loaded": False,
        "scientific_data_accessed": False,
        "formal_run3_authorized": False,
    }
    try:
        payload["memory_baseline"] = self_cgroup_memory_snapshot()
        rng = np.random.default_rng(SYNTHETIC_SEED)
        item = {}
        source_sha = {}
        for i in range(LEAF_COUNT):
            host = rng.random(LEAF_ELEMENTS, dtype=np.float32)
            value = jnp.asarray(host)
            del host
            item[f"leaf_{i:02d}"] = value
            source_sha[f"leaf_{i:02d}"] = sha_array(value)
        payload["memory_after_arrays"] = self_cgroup_memory_snapshot()

        registry, handler = clone_global_registry_with_writeback_aware_leaf_batched_array_handler(
            d2h_batch_bytes=D2H_BATCH_BYTES
        )
        writer = ocp.Checkpointer(
            ocp.PyTreeCheckpointHandler(
                save_concurrent_gb=1,
                restore_concurrent_gb=1,
                type_handler_registry=registry,
            )
        )
        writer.save(ckpt, args=ocp.args.PyTreeSave(item))
        writer.close()
        payload["memory_after_save"] = self_cgroup_memory_snapshot()
        payload["batch_manifest"] = handler.batch_manifest
        payload["reclamation_manifest"] = handler.reclamation_manifest
        if len(handler.batch_manifest) != 3:
            raise RuntimeError(f"D2 batch count drift: {handler.batch_manifest}")
        if any(int(x["device_bytes"]) > D2H_BATCH_BYTES for x in handler.batch_manifest):
            raise RuntimeError("D2 synthetic batch exceeded frozen 128MiB")

        drops = []
        for batch in handler.reclamation_manifest:
            for blob in batch["blobs"]:
                before = int(blob["memory_after_fsync"]["memory_stat"]["file"])
                after = int(blob["memory_after_fadvise"]["memory_stat"]["file"])
                drops.append(max(0, before - after))
        total_drop = sum(drops)
        max_drop = max(drops, default=0)
        payload["cache_endpoint"] = {
            "event_count": len(drops),
            "positive_event_count": sum(x > 0 for x in drops),
            "max_file_drop_bytes": max_drop,
            "total_file_drop_bytes": total_drop,
            "single_threshold_pass": max_drop >= MIN_SINGLE_FILE_DROP_BYTES,
            "total_threshold_pass": total_drop >= MIN_TOTAL_FILE_DROP_BYTES,
        }
        if max_drop < MIN_SINGLE_FILE_DROP_BYTES or total_drop < MIN_TOTAL_FILE_DROP_BYTES:
            raise RuntimeError(
                f"D2 cache endpoint below frozen threshold: max={max_drop} total={total_drop}"
            )

        del item
        gc.collect()
        payload["memory_after_source_release"] = self_cgroup_memory_snapshot()
        reader = ocp.Checkpointer(ocp.PyTreeCheckpointHandler(restore_concurrent_gb=1))
        restored = reader.restore(ckpt, args=ocp.args.PyTreeRestore())
        reader.close()
        restored_sha = {key: sha_array(value) for key, value in restored.items()}
        exact = source_sha == restored_sha
        payload["standard_orbax_restore"] = True
        payload["source_sha256"] = source_sha
        payload["restored_sha256"] = restored_sha
        payload["exact_sha256_roundtrip"] = exact
        if not exact:
            raise RuntimeError("D2 standard Orbax restore SHA mismatch")
        payload["memory_after_restore"] = self_cgroup_memory_snapshot()

        tmp_paths = [str(x) for x in root.rglob("*orbax-checkpoint-tmp*")]
        if tmp_paths:
            raise RuntimeError(f"D2 temporary checkpoint residue: {tmp_paths[:8]}")
        files, bytes_on_disk = tree_bytes(ckpt)
        payload["checkpoint_file_count"] = files
        payload["checkpoint_bytes"] = bytes_on_disk
        payload["tmp_residue"] = []
        payload["status"] = "PI05_B3_D2_CACHE_ACCOUNTING_PASS"
    except Exception as exc:
        payload["error"] = f"{type(exc).__name__}: {exc}"
        try:
            payload["memory_after_error"] = self_cgroup_memory_snapshot()
        except Exception:
            pass
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_json(result, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"].endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
