from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import gc
import hashlib
import json
from pathlib import Path
from typing import Any

import jax
import numpy as np
import orbax.checkpoint as ocp
import tensorstore as ts
from etils import epath
from orbax.checkpoint._src.serialization import tensorstore_utils as ts_utils
from orbax.checkpoint._src.serialization import type_handlers as th
from orbax.checkpoint._src.serialization import types

from research_pipeline.behavior_formal_goal_coupling_shared26_pi05_b1_serial_item_checkpoint_save import (
    atomic_json,
    cgroup_snapshot,
    gpu_snapshot,
    host_snapshot,
    sha256_file,
)

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CHILD_ID = "SUCC-C-BEHAVIOR2026-SHARED26-PI05-PRACTICAL-SINGLE-GPU-BATCH"
SAVE_LABEL = 10000
EXPECTED_MACHINE_ID = "6fd433c546c241218ccd29813f304aee"
EXPECTED_MEMORY_MAX_GIB = 52
EXPECTED_MEMORY_MAX_BYTES = EXPECTED_MEMORY_MAX_GIB * 1024**3
EXPECTED_TRAIN_LEAVES = 156
EXPECTED_TRAIN_NBYTES = 40_241_206_476
EXPECTED_PARAMS_LEAVES = 51
EXPECTED_PARAMS_NBYTES = 13_413_735_488


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def require_binding(authority: dict[str, Any], key: str, path: Path) -> str:
    binding = authority.get("bindings", {}).get(key)
    if not isinstance(binding, dict):
        raise RuntimeError(f"missing authority binding: {key}")
    actual = sha256_file(path)
    if binding.get("path") != str(path) or binding.get("sha256") != actual:
        raise RuntimeError(f"authority binding drift: {key}")
    return actual


def _fingerprint(arr: np.ndarray) -> str:
    arr = np.asarray(arr)
    if not arr.flags.c_contiguous:
        arr = np.ascontiguousarray(arr)
    return hashlib.sha256(memoryview(arr).cast("B")).hexdigest()


async def verify_disk_item(parent: Path, rows: list[dict[str, Any]], expected_count: int, expected_bytes: int) -> dict[str, Any]:
    ctx = ts_utils.get_ts_context(use_ocdbt=True)
    verified = 0
    total = 0
    largest = 0
    for row in rows:
        name = row.get("name")
        if not isinstance(name, str) or not name:
            raise RuntimeError(f"invalid fingerprint name: {name!r}")
        info = types.ParamInfo(
            name=name,
            path=epath.Path(parent) / name,
            parent_dir=epath.Path(parent),
            is_ocdbt_checkpoint=True,
            use_zarr3=False,
            ts_context=ctx,
        )
        t = await ts.open(ts.Spec(th.get_json_tspec_read(info, use_ocdbt=True)), open=True, context=ctx)
        arr = np.asarray(await t.read())
        if list(arr.shape) != row.get("shape") or str(arr.dtype) != row.get("dtype") or int(arr.nbytes) != int(row.get("nbytes", -1)):
            raise RuntimeError(f"disk leaf metadata drift: {name}")
        digest = _fingerprint(arr)
        if digest != row.get("sha256"):
            raise RuntimeError(f"disk leaf SHA drift: {name}")
        verified += 1
        total += int(arr.nbytes)
        largest = max(largest, int(arr.nbytes))
        del arr, t
        gc.collect()
    if verified != expected_count or total != expected_bytes:
        raise RuntimeError(f"disk aggregate drift: {parent.name} {verified}/{total}")
    return {"verified_leaves": verified, "verified_bytes": total, "largest_leaf_bytes": largest}


def tree_array_stats(tree) -> dict[str, Any]:
    leaves = jax.tree.leaves(tree)
    count = 0
    total = 0
    arrays = 0
    for leaf in leaves:
        if hasattr(leaf, "shape") and hasattr(leaf, "dtype"):
            count += 1
            total += int(np.prod(leaf.shape, dtype=np.int64)) * int(np.dtype(leaf.dtype).itemsize)
            if isinstance(leaf, jax.Array):
                arrays += 1
    return {"leaf_count": count, "nbytes": total, "jax_array_leaves": arrays, "tree_leaf_count": len(leaves)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["disk", "restore"], required=True)
    ap.add_argument("--authority", type=Path, required=True)
    ap.add_argument("--save-result", type=Path, required=True)
    ap.add_argument("--disk-result", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)
    args = ap.parse_args()
    p = {k: Path(v).resolve() if isinstance(v, Path) else v for k, v in vars(args).items()}

    authority = load_json(p["authority"])
    if authority.get("status") != "AUTHORIZED_PI05_B2_LEAF_BATCHED_CHECKPOINT_QUALIFICATION_231":
        raise RuntimeError("B2 authority status drift")
    if authority.get("formal_run3_authorized") is not False:
        raise RuntimeError("run3 unexpectedly authorized")
    if Path("/etc/machine-id").read_text().strip() != EXPECTED_MACHINE_ID:
        raise RuntimeError("B2 verification may run only on host231")
    require_binding(authority, "save_runner", Path(authority["bindings"]["save_runner"]["path"]))
    require_binding(authority, "verify_runner", Path(authority["bindings"]["verify_runner"]["path"]))

    save_result = load_json(p["save_result"])
    if save_result.get("status") != "PI05_B2_CHECKPOINT_SAVE_QUALIFICATION_PASS" or save_result.get("checkpoint_save_completed") is not True:
        raise RuntimeError("B2 save result not PASS")
    if save_result.get("manager_steps") != [SAVE_LABEL]:
        raise RuntimeError("B2 manager step drift")
    if save_result.get("policy_outcomes_read") is not False or save_result.get("optimizer_update_executed") is not False:
        raise RuntimeError("B2 save scientific boundary drift")

    if p["result"].exists():
        raise RuntimeError(f"B2 verification result already exists: {p['result']}")
    step_dir = p["output_root"] / str(SAVE_LABEL)
    if not step_dir.is_dir():
        raise RuntimeError("B2 completed checkpoint step missing")

    scope_before = cgroup_snapshot(EXPECTED_MEMORY_MAX_BYTES)
    initial = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-b2-checkpoint-verify-v1",
        "object_id": OBJECT_ID,
        "child_id": CHILD_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": f"PI05_B2_{p['mode'].upper()}_VERIFY_STARTED",
        "mode": p["mode"],
        "authority_sha256": sha256_file(p["authority"]),
        "save_result_sha256": sha256_file(p["save_result"]),
        "memory_max_gib": EXPECTED_MEMORY_MAX_GIB,
        "memory_swap_max_gib": 0,
        "resource_scope_before": scope_before,
        "host_before": host_snapshot(),
        "dataset_accessed": False,
        "forward_pass_executed": False,
        "backward_pass_executed": False,
        "optimizer_update_executed": False,
        "real_scientific_optimizer_updates": 0,
        "loss_values_read_or_reported": False,
        "policy_outcomes_read": False,
        "formal_run3_authorized": False,
    }
    atomic_json(p["result"], initial)

    status = f"PI05_B2_{p['mode'].upper()}_VERIFY_HOLD"
    error = None
    evidence: dict[str, Any] = {}
    try:
        if p["mode"] == "disk":
            fps = save_result.get("fingerprints") or {}
            train_rows = fps.get("train_state") or []
            params_rows = fps.get("params") or []
            train = asyncio.run(verify_disk_item(step_dir / "train_state", train_rows, EXPECTED_TRAIN_LEAVES, EXPECTED_TRAIN_NBYTES))
            params = asyncio.run(verify_disk_item(step_dir / "params", params_rows, EXPECTED_PARAMS_LEAVES, EXPECTED_PARAMS_NBYTES))
            evidence = {"train_state": train, "params": params, "exact_per_leaf_sha256_match": True}
            status = "PI05_B2_DISK_VERIFY_PASS"
        else:
            disk = load_json(p["disk_result"])
            if disk.get("status") != "PI05_B2_DISK_VERIFY_PASS" or disk.get("evidence", {}).get("exact_per_leaf_sha256_match") is not True:
                raise RuntimeError("B2 disk verification not PASS")
            gpu = gpu_snapshot()
            if len(gpu["gpus"]) != 1:
                raise RuntimeError(f"expected exactly one GPU: {gpu}")
            g0 = gpu["gpus"][0]
            if "A100" not in g0["name"] or g0["memory_total_mib"] < 80_000 or g0["memory_used_mib"] > 1024:
                raise RuntimeError(f"restore GPU admission failed: {g0}")
            train_cp = ocp.Checkpointer(ocp.PyTreeCheckpointHandler(restore_concurrent_gb=8))
            train = train_cp.restore(step_dir / "train_state")
            train_cp.close()
            train_stats = tree_array_stats(train)
            if train_stats["leaf_count"] != EXPECTED_TRAIN_LEAVES or train_stats["nbytes"] != EXPECTED_TRAIN_NBYTES:
                raise RuntimeError(f"standard train_state restore aggregate drift: {train_stats}")
            if not isinstance(train, dict) or "step" not in train or int(np.asarray(jax.device_get(train["step"]))) != 0:
                raise RuntimeError("standard restore state.step drift")

            params_cp = ocp.Checkpointer(ocp.PyTreeCheckpointHandler(restore_concurrent_gb=8))
            params = params_cp.restore(step_dir / "params")
            params_cp.close()
            params_stats = tree_array_stats(params)
            if params_stats["leaf_count"] != EXPECTED_PARAMS_LEAVES or params_stats["nbytes"] != EXPECTED_PARAMS_NBYTES:
                raise RuntimeError(f"standard params restore aggregate drift: {params_stats}")
            jax.block_until_ready((train, params))
            evidence = {
                "standard_orbax_restore": True,
                "state_step": 0,
                "train_state": train_stats,
                "params": params_stats,
                "gpu_after_restore": gpu_snapshot(),
            }
            status = "PI05_B2_STANDARD_RESTORE_PASS"

        after = cgroup_snapshot(EXPECTED_MEMORY_MAX_BYTES)
        evidence["resource_scope_after"] = after
        if int(after["memory_peak_bytes"]) >= EXPECTED_MEMORY_MAX_BYTES:
            raise RuntimeError(f"verification cgroup peak reached/exceeded ceiling: {after['memory_peak_bytes']}")
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

    final = dict(initial)
    final.update({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "evidence": evidence,
        "error": error,
        "dataset_accessed": False,
        "forward_pass_executed": False,
        "backward_pass_executed": False,
        "optimizer_update_executed": False,
        "real_scientific_optimizer_updates": 0,
        "loss_values_read_or_reported": False,
        "policy_outcomes_read": False,
        "formal_run3_authorized": False,
        "next_gate": "PI05_B2_STANDARD_RESTORE" if status == "PI05_B2_DISK_VERIFY_PASS" else ("SEPARATE_FORMAL_RUN3_AUTHORITY_DESIGN_ONLY" if status == "PI05_B2_STANDARD_RESTORE_PASS" else "STOP_B2_NO_AUTOMATIC_RETRY"),
    })
    atomic_json(p["result"], final)
    print(json.dumps({"status": status, "error": error, "evidence": evidence}, sort_keys=True, default=str))
    return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
