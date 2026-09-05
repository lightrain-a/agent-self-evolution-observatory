from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_NORM_SHA256 = "5e4159ec0986ad9fc87cc9a265eed9ac67fc9d2d0df233db6130acf0ebff52ce"
SAVE_LABEL = 10000
LIMITER_GB = 8
MEMORY_MAX_GIB = 96
EXPECTED_PYTHON = "3.11.16"
EXPECTED_JAX = "0.5.3"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def cgroup_snapshot() -> dict:
    rows = Path("/proc/self/cgroup").read_text().splitlines()
    rel = [r.split(":", 2)[2] for r in rows if r.startswith("0::")]
    if len(rel) != 1:
        raise RuntimeError(f"cgroup-v2 path drift: {rel}")
    cg = Path("/sys/fs/cgroup") / rel[0].lstrip("/")
    def read(name):
        p = cg / name
        return p.read_text().strip() if p.exists() else None
    expected = MEMORY_MAX_GIB * 1024**3
    if read("memory.max") in (None, "max") or int(read("memory.max")) != expected:
        raise RuntimeError(f"MemoryMax drift: {read('memory.max')}")
    if read("memory.swap.max") != "0":
        raise RuntimeError(f"MemorySwapMax drift: {read('memory.swap.max')}")
    if set(os.sched_getaffinity(0)) != set(range(64)):
        raise RuntimeError("CPU affinity drift")
    return {
        "path": str(cg),
        "memory_current_bytes": int(read("memory.current") or 0),
        "memory_peak_bytes": int(read("memory.peak") or 0),
        "memory_max_bytes": expected,
        "memory_swap_max_bytes": 0,
    }


def tree_bytes(path: Path) -> tuple[int, int]:
    files = [p for p in path.rglob("*") if p.is_file()]
    return len(files), sum(p.stat().st_size for p in files)


def fingerprint_tree(tree) -> dict:
    import jax
    import numpy as np
    path_leaves, treedef = jax.tree_util.tree_flatten_with_path(tree)
    rows = []
    for i, (keypath, leaf) in enumerate(path_leaves):
        key = jax.tree_util.keystr(keypath)
        if leaf is None:
            rows.append({"index": i, "path": key, "kind": "none", "sha256": hashlib.sha256(b"null").hexdigest()})
            continue
        try:
            arr = np.asarray(leaf)
        except Exception:
            raw = json.dumps(leaf, sort_keys=True, default=repr).encode()
            rows.append({"index": i, "path": key, "kind": type(leaf).__name__, "sha256": hashlib.sha256(raw).hexdigest()})
            continue
        arr = np.ascontiguousarray(arr)
        u8 = arr.view(np.uint8).reshape(-1)
        rows.append({
            "index": i,
            "path": key,
            "kind": "array",
            "shape": list(arr.shape),
            "dtype": str(arr.dtype),
            "nbytes": int(arr.nbytes),
            "sha256": hashlib.sha256(memoryview(u8)).hexdigest(),
        })
        del u8, arr
        gc.collect()
    return {"treedef": str(treedef), "leaf_count": len(rows), "leaves": rows}


def compare(expected: dict, actual: dict) -> tuple[bool, str | None]:
    if expected.get("treedef") != actual.get("treedef"):
        return False, "treedef mismatch"
    if expected.get("leaf_count") != actual.get("leaf_count"):
        return False, "leaf_count mismatch"
    for a, b in zip(expected.get("leaves", []), actual.get("leaves", [])):
        for key in ("index", "path", "kind", "shape", "dtype", "nbytes", "sha256"):
            if a.get(key) != b.get(key):
                return False, f"leaf={a.get('index')} field={key} mismatch"
    return True, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority", type=Path, required=True)
    ap.add_argument("--runner", type=Path, required=True)
    ap.add_argument("--reference-receipt", type=Path, required=True)
    ap.add_argument("--save-receipt", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)
    args = ap.parse_args()
    paths = {k: Path(v).resolve() for k, v in vars(args).items()}
    if paths["result"].exists():
        raise RuntimeError("B1 final result already exists")
    authority = json.loads(paths["authority"].read_text())
    if authority.get("status") != "AUTHORIZED_PI05_B1_SPLIT_HARNESS_QUALIFICATION_REPAIR1":
        raise RuntimeError("B1 split-harness authority inactive")
    if authority.get("runner_sha256") != sha256_file(paths["runner"]):
        raise RuntimeError("B1 save runner SHA drift")
    if authority.get("verifier_sha256") != sha256_file(Path(__file__).resolve()):
        raise RuntimeError("B1 verifier SHA drift")
    reference = json.loads(paths["reference_receipt"].read_text())
    if reference.get("status") != "PI05_B1_SPLIT_REFERENCE_PASS":
        raise RuntimeError(f"split reference not PASS: {reference.get('status')}")
    saved = json.loads(paths["save_receipt"].read_text())
    if saved.get("status") != "PI05_B1_SPLIT_SAVE_STAGE_PASS":
        raise RuntimeError(f"B1 split save stage not PASS: {saved.get('status')}")
    if saved.get("manager_steps") != [SAVE_LABEL] or saved.get("checkpoint_save_completed") is not True:
        raise RuntimeError("B1 split save-stage completion drift")
    if saved.get("reference_receipt_sha256") != sha256_file(paths["reference_receipt"]):
        raise RuntimeError("save-stage reference receipt binding drift")
    if reference.get("qualification_run_id") != authority.get("qualification_run_id") or saved.get("qualification_run_id") != authority.get("qualification_run_id"):
        raise RuntimeError("split qualification run-id drift")
    if reference.get("state_signature_before") != saved.get("state_signature_before"):
        raise RuntimeError("F/S deterministic step0 structure signature drift")
    expected = reference.get("fingerprints") or {}
    if set(expected) != {"train_state", "params"}:
        raise RuntimeError("reference fingerprints incomplete")
    initial = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-b1-split-harness-checkpoint-qualification-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_B1_SPLIT_HARNESS_RESTORE_VERIFY_STARTED",
        "qualification_run_id": authority.get("qualification_run_id"),
        "authority_sha256": sha256_file(paths["authority"]),
        "reference_receipt_sha256": sha256_file(paths["reference_receipt"]),
        "save_receipt_sha256": sha256_file(paths["save_receipt"]),
        "verifier_sha256": sha256_file(Path(__file__).resolve()),
        "real_scientific_optimizer_updates": 0,
        "behavior_dataset_accessed": False,
        "forward_pass_executed": False,
        "backward_pass_executed": False,
        "optimizer_update_executed": False,
        "loss_values_read_or_reported": False,
        "policy_outcomes_read": False,
        "formal_run3_authorized": False,
    }
    atomic_json(paths["result"], initial)
    status = "PI05_B1_SPLIT_HARNESS_CHECKPOINT_QUALIFICATION_HOLD"
    error = None
    actual = {}
    comparisons = {}
    try:
        import jax
        import numpy as np
        if platform.python_version() != EXPECTED_PYTHON:
            raise RuntimeError(f"Python runtime drift: {platform.python_version()}")
        if jax.__version__ != EXPECTED_JAX:
            raise RuntimeError(f"JAX runtime drift: {jax.__version__}")
        import orbax.checkpoint as ocp
        from orbax.checkpoint import args as ocp_args
        if jax.default_backend() != "cpu":
            raise RuntimeError(f"restore verifier backend drift: {jax.default_backend()}")
        scope = cgroup_snapshot()
        step_dir = paths["output_root"] / str(SAVE_LABEL)
        names = sorted(p.name for p in step_dir.iterdir())
        if names != ["_CHECKPOINT_METADATA", "assets", "params", "train_state"]:
            raise RuntimeError(f"checkpoint item-name drift: {names}")
        tmp = list(paths["output_root"].rglob("*orbax-checkpoint-tmp*"))
        if tmp:
            raise RuntimeError(f"temporary checkpoint paths remain: {[str(x) for x in tmp[:8]]}")
        asset = step_dir / "assets" / "b1k_shared26_frozen" / "norm_stats.json"
        if not asset.is_file() or sha256_file(asset) != EXPECTED_NORM_SHA256:
            raise RuntimeError("normalization asset drift")

        def restore_numpy(item_dir: Path):
            handler = ocp.PyTreeCheckpointHandler(restore_concurrent_gb=LIMITER_GB)
            md = handler.metadata(item_dir)
            restore_args = jax.tree.map(lambda _: ocp.RestoreArgs(restore_type=np.ndarray), md)
            return ocp.Checkpointer(handler).restore(item_dir, args=ocp_args.PyTreeRestore(restore_args=restore_args))

        for name in ("train_state", "params"):
            restored = restore_numpy(step_dir / name)
            actual[name] = fingerprint_tree(restored)
            ok, why = compare(expected[name], actual[name])
            comparisons[name] = {"match": ok, "error": why}
            if not ok:
                raise RuntimeError(f"{name} exact-value roundtrip mismatch: {why}")
            del restored
            gc.collect()
        files, bytes_ = tree_bytes(paths["output_root"])
        status = "PI05_B1_SPLIT_HARNESS_CHECKPOINT_QUALIFICATION_PASS"
        final_scope = cgroup_snapshot()
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        files, bytes_ = tree_bytes(paths["output_root"]) if paths["output_root"].exists() else (0, 0)
        try: final_scope = cgroup_snapshot()
        except Exception: final_scope = None
    final = dict(initial)
    final.update({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "manager_steps": saved.get("manager_steps"),
        "checkpoint_file_count": files,
        "checkpoint_bytes": bytes_,
        "fingerprint_comparisons": comparisons,
        "restored_fingerprints": actual,
        "normalization_asset_sha256": EXPECTED_NORM_SHA256,
        "resource_scope_after_verify": final_scope,
        "checkpoint_save_completed": True,
        "checkpoint_restore_completed": status.endswith("PASS"),
        "exact_value_roundtrip_verified": status.endswith("PASS"),
        "error": error,
        "next_gate": "SEPARATE_FORMAL_RUN3_B1_AUTHORITY_DESIGN" if status.endswith("PASS") else "B1_SPLIT_HARNESS_FAILURE_ADJUDICATION_B2_REVIEW_ONLY",
    })
    atomic_json(paths["result"], final)
    print(json.dumps({"status": status, "comparisons": comparisons, "checkpoint_bytes": bytes_, "error": error}, sort_keys=True))
    return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
