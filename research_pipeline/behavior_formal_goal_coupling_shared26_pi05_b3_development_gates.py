from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import inspect
import json
import os
from pathlib import Path
import shutil

import jax.numpy as jnp
import numpy as np
import orbax.checkpoint as ocp

from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_terminal_gate import classify_save_result
from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_writeback_aware_orbax import (
    WritebackAwareLeafBatchedArrayHandler,
    clone_global_registry_with_writeback_aware_leaf_batched_array_handler,
)
from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_writeback_cache import (
    reclaim_completed_ocdbt_data_blobs,
    snapshot_ocdbt_data_blobs,
)
import research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_writeback_aware_orbax as b3_serializer
import research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b3_writeback_cache as b3_cache


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def d0_static_and_path_gate(root: Path) -> dict:
    serializer_src = inspect.getsource(WritebackAwareLeafBatchedArrayHandler.serialize)
    gather_i = serializer_src.index("await asyncio.gather(*write_coros)")
    commit_i = serializer_src.index("await sharding_txn.commit_async()")
    reclaim_i = serializer_src.index("reclaim_completed_ocdbt_data_blobs(item_root, before_blobs)")
    next_stage_i = serializer_src.index("del host_values")
    if not (gather_i < commit_i < reclaim_i < next_stage_i):
        raise RuntimeError("D0 serializer ordering invariant failed")

    cache_src = inspect.getsource(reclaim_completed_ocdbt_data_blobs)
    if cache_src.index("os.fsync(fd)") > cache_src.index("os.posix_fadvise"):
        raise RuntimeError("D0 durability-before-fadvise invariant failed")

    case = root / "d0_path"
    data = case / "ocdbt.process_0" / "d"
    data.mkdir(parents=True)
    manifest = case / "ocdbt.process_0" / "manifest.ocdbt"
    manifest.write_bytes(b"manifest-sentinel")
    before = snapshot_ocdbt_data_blobs(case)
    if before:
        raise RuntimeError("D0 initial blob snapshot not empty")
    valid = data / ("a" * 32)
    valid.write_bytes(b"x" * 65536)
    events = reclaim_completed_ocdbt_data_blobs(case, before)
    if len(events) != 1 or events[0]["relative_to_item"] != f"ocdbt.process_0/d/{'a'*32}":
        raise RuntimeError(f"D0 safe path event drift: {events}")
    if manifest.read_bytes() != b"manifest-sentinel":
        raise RuntimeError("D0 manifest changed")

    malformed = data / "manifest.ocdbt"
    malformed.write_bytes(b"unsafe")
    malformed_rejected = False
    try:
        snapshot_ocdbt_data_blobs(case)
    except RuntimeError:
        malformed_rejected = True
    malformed.unlink()
    if not malformed_rejected:
        raise RuntimeError("D0 malformed data filename not fail-closed")

    symlink = data / ("b" * 32)
    symlink.symlink_to(manifest)
    symlink_rejected = False
    try:
        snapshot_ocdbt_data_blobs(case)
    except RuntimeError:
        symlink_rejected = True
    symlink.unlink()
    if not symlink_rejected:
        raise RuntimeError("D0 symlink target not fail-closed")

    return {
        "status": "PASS",
        "serializer_order": ["tensorstore_write_await", "sharding_commit", "reclaim", "host_buffer_release"],
        "durability_before_fadvise": True,
        "manifest_excluded": True,
        "malformed_filename_rejected": True,
        "symlink_rejected": True,
        "safe_event": events[0],
    }


def d1_cpu_ocdbt_roundtrip(root: Path) -> dict:
    ckpt = root / "d1_roundtrip"
    item = {
        "a": jnp.arange(220_000, dtype=jnp.float32),
        "b": jnp.arange(180_000, dtype=jnp.float32) + 1,
        "c": jnp.arange(160_000, dtype=jnp.float32) + 2,
        "d": jnp.arange(80_000, dtype=jnp.float32) + 3,
    }
    registry, array_handler = clone_global_registry_with_writeback_aware_leaf_batched_array_handler(
        d2h_batch_bytes=1_000_000
    )
    writer = ocp.Checkpointer(ocp.PyTreeCheckpointHandler(type_handler_registry=registry))
    writer.save(ckpt, args=ocp.args.PyTreeSave(item))
    writer.close()

    reader = ocp.Checkpointer(ocp.PyTreeCheckpointHandler())
    restored = reader.restore(ckpt, args=ocp.args.PyTreeRestore())
    reader.close()
    exact = all(np.array_equal(np.asarray(item[k]), np.asarray(restored[k])) for k in item)
    if not exact:
        raise RuntimeError("D1 standard Orbax restore mismatch")

    tmp_paths = [str(x) for x in root.rglob("*orbax-checkpoint-tmp*")]
    if tmp_paths:
        raise RuntimeError(f"D1 tmp residue remains: {tmp_paths}")
    if len(array_handler.batch_manifest) < 2:
        raise RuntimeError("D1 did not exercise multiple leaf batches")

    final_blob_stats = snapshot_ocdbt_data_blobs(ckpt)
    reclaimed = [b for batch in array_handler.reclamation_manifest for b in batch["blobs"]]
    if not reclaimed:
        raise RuntimeError("D1 did not exercise OCDBT reclamation")
    changed_after_advice = []
    for row in reclaimed:
        rel = Path(row["relative_to_item"])
        name = rel.name
        final = final_blob_stats.get(name)
        if final is None or final.size != int(row["size"]) or final.mtime_ns != int(row["mtime_ns"]):
            changed_after_advice.append(name)
    if changed_after_advice:
        raise RuntimeError(f"D0/D1 advised blob later changed: {changed_after_advice}")
    if any("manifest" in row["relative_to_item"] or "METADATA" in row["relative_to_item"] for row in reclaimed):
        raise RuntimeError("D1 reclamation touched metadata/manifest")

    return {
        "status": "PASS",
        "standard_orbax_restore": True,
        "exact_array_equality": True,
        "batch_count": len(array_handler.batch_manifest),
        "reclamation_batch_count": len(array_handler.reclamation_manifest),
        "reclaimed_blob_count": len(reclaimed),
        "reclaimed_bytes": sum(int(x["size"]) for x in reclaimed),
        "advised_blobs_unchanged_through_final_checkpoint": True,
        "manifest_or_metadata_advised": False,
        "tmp_residue": [],
    }


def d3_terminal_poll_gate(root: Path) -> dict:
    p = root / "d3_result.json"
    cases = []
    cases.append(("ABSENT", classify_save_result(p), "WAIT"))
    statuses = [
        ("PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_STARTED", "WAIT"),
        ("PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_SAVE_STARTED", "WAIT"),
        ("PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_HOLD", "HOLD"),
        ("PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_PASS", "PASS"),
        ("UNKNOWN", "HOLD"),
    ]
    for status, expected in statuses:
        p.write_text(json.dumps({"status": status}))
        cases.append((status, classify_save_result(p), expected))
    p.write_text("not-json")
    cases.append(("INVALID_JSON", classify_save_result(p), "HOLD"))
    p.unlink()
    bad = [c for c in cases if c[1] != c[2]]
    if bad:
        raise RuntimeError(f"D3 terminal gate failures: {bad}")
    return {
        "status": "PASS",
        "cases": [{"input": a, "actual": b, "expected": c} for a, b, c in cases],
        "only_terminal_pass_unlocks_downstream": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-root", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)
    args = ap.parse_args()
    root = args.work_root.resolve()
    result = args.result.resolve()
    if root.exists():
        raise RuntimeError(f"development work root already exists: {root}")
    root.mkdir(parents=True)
    payload = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-b3-development-gates-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_B3_D0_D1_D3_HOLD",
        "scope": "CPU_STATIC_SYNTHETIC_ONLY_NO_MODEL_NO_SCIENTIFIC_DATA",
        "D0": None,
        "D1": None,
        "D3": None,
        "model_loaded": False,
        "scientific_data_accessed": False,
        "formal_run3_authorized": False,
    }
    try:
        payload["D0"] = d0_static_and_path_gate(root)
        payload["D1"] = d1_cpu_ocdbt_roundtrip(root)
        payload["D3"] = d3_terminal_poll_gate(root)
        payload["status"] = "PI05_B3_D0_D1_D3_PASS"
    except Exception as exc:
        payload["error"] = f"{type(exc).__name__}: {exc}"
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    payload["source_sha256"] = {
        "serializer": sha256_file(Path(inspect.getsourcefile(b3_serializer)).resolve()),
        "cache": sha256_file(Path(inspect.getsourcefile(b3_cache)).resolve()),
    }
    atomic_json(result, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"].endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
