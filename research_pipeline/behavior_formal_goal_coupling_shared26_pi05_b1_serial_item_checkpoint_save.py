from __future__ import annotations

import argparse
import dataclasses
import fcntl
import gc
import hashlib
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CHILD_ID = "SUCC-C-BEHAVIOR2026-SHARED26-PI05-PRACTICAL-SINGLE-GPU-BATCH"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
EXP_NAME = "shared26-seed42-checkpoint-save-qualification"
EXPECTED_PARENT_COMMIT = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
EXPECTED_CONFIG_SHA256 = "4a50bb5f3579ed0035e19d2fc2a5d33821c0cc115c6e8c441eac497e74b02e99"
EXPECTED_BASE_RECEIPT_SHA256 = "8e0f977e0641960ee3e082a19a57f52f994a817bbf981cbb2f7007ea3104a4ed"
EXPECTED_BASE_OBJECT_COUNT = 20
EXPECTED_BASE_BYTES = 12_441_721_931
EXPECTED_NORM_SHA256 = "5e4159ec0986ad9fc87cc9a265eed9ac67fc9d2d0df233db6130acf0ebff52ce"
BATCH = 16
SEED = 42
SAVE_LABEL = 10000
LIMITER_GB = 8


@contextmanager
def exclusive_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()}\n")
        handle.flush()
        os.fsync(handle.fileno())
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


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


def cgroup_snapshot(expected_memory_max_bytes: int) -> dict:
    rows = Path("/proc/self/cgroup").read_text(encoding="utf-8").splitlines()
    unified = [row.split(":", 2)[2] for row in rows if row.startswith("0::")]
    if len(unified) != 1:
        raise RuntimeError(f"expected one cgroup-v2 path, got {unified}")
    cgroup = Path("/sys/fs/cgroup") / unified[0].lstrip("/")
    def read(name: str):
        p = cgroup / name
        return p.read_text(encoding="utf-8").strip() if p.exists() else None
    memory_max = read("memory.max")
    swap_max = read("memory.swap.max")
    if memory_max in (None, "max") or int(memory_max) != expected_memory_max_bytes:
        raise RuntimeError(f"checkpoint qualification MemoryMax drift: {memory_max}")
    if swap_max != "0":
        raise RuntimeError(f"checkpoint qualification requires MemorySwapMax=0, got {swap_max}")
    affinity = set(os.sched_getaffinity(0))
    if affinity != set(range(64)):
        raise RuntimeError(f"CPU affinity drift: {sorted(affinity)}")
    events = {}
    if (cgroup / "memory.events").exists():
        for line in (cgroup / "memory.events").read_text().splitlines():
            k, v = line.split()
            events[k] = int(v)
    return {
        "path": str(cgroup),
        "memory_current_bytes": int(read("memory.current") or 0),
        "memory_peak_bytes": int(read("memory.peak") or 0),
        "memory_max_bytes": int(memory_max),
        "memory_swap_max_bytes": 0,
        "memory_events": events,
        "cpu_affinity": "0-63",
    }


def host_snapshot() -> dict:
    vals = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        if ":" not in line:
            continue
        k, rest = line.split(":", 1)
        if k in {"MemTotal", "MemAvailable", "MemFree", "SwapTotal", "SwapFree"}:
            vals[k + "_kib"] = int(rest.strip().split()[0])
    vals["process_rss_kib"] = int(Path("/proc/self/status").read_text().split("VmRSS:", 1)[1].splitlines()[0].strip().split()[0])
    return vals


def gpu_snapshot() -> dict:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
        text=True,
    ).strip().splitlines()
    rows = []
    for line in out:
        idx, name, total, used, util = [x.strip() for x in line.split(",", 4)]
        rows.append({"index": int(idx), "name": name, "memory_total_mib": int(total), "memory_used_mib": int(used), "utilization_gpu_percent": int(util)})
    return {"gpus": rows}


def tree_bytes(path: Path) -> tuple[int, int]:
    count = 0
    total = 0
    if path.exists():
        for p in path.rglob("*"):
            if p.is_file():
                count += 1
                total += p.stat().st_size
    return count, total


def validate_base(receipt_path: Path, params_root: Path) -> tuple[str, int, int]:
    receipt_sha = sha256_file(receipt_path)
    if receipt_sha != EXPECTED_BASE_RECEIPT_SHA256:
        raise RuntimeError(f"base receipt SHA drift: {receipt_sha}")
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("status") != "PI05_BASE_TRANSPORT_REPAIR1_COMPLETE":
        raise RuntimeError("base receipt not COMPLETE")
    count = 0
    total = 0
    for row in receipt.get("objects", []):
        p = params_root / row["relative_path"]
        if not p.is_file() or p.stat().st_size != int(row["size"]):
            raise RuntimeError(f"base object missing/size drift: {row['relative_path']}")
        if sha256_file(p) != row["local_sha256"]:
            raise RuntimeError(f"base object SHA drift: {row['relative_path']}")
        count += 1
        total += int(row["size"])
    if count != EXPECTED_BASE_OBJECT_COUNT or total != EXPECTED_BASE_BYTES:
        raise RuntimeError(f"base object aggregate drift: {count}/{total}")
    return receipt_sha, count, total


def fingerprint_tree(tree, *, normalize_flax: bool) -> dict:
    import numpy as np
    import jax
    if normalize_flax:
        import flax.serialization
        tree = flax.serialization.to_state_dict(tree)
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
            raw = json.dumps(leaf, sort_keys=True, default=repr).encode("utf-8")
            rows.append({"index": i, "path": key, "kind": type(leaf).__name__, "sha256": hashlib.sha256(raw).hexdigest()})
            continue
        arr = np.ascontiguousarray(arr)
        u8 = arr.view(np.uint8).reshape(-1)
        digest = hashlib.sha256(memoryview(u8)).hexdigest()
        rows.append({
            "index": i,
            "path": key,
            "kind": "array",
            "shape": list(arr.shape),
            "dtype": str(arr.dtype),
            "nbytes": int(arr.nbytes),
            "sha256": digest,
        })
        del u8, arr
        gc.collect()
    return {"treedef": str(treedef), "leaf_count": len(rows), "leaves": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority", type=Path, required=True)
    ap.add_argument("--parent-failure-adjudication", type=Path, required=True)
    ap.add_argument("--review", type=Path, required=True)
    ap.add_argument("--source-adjudication", type=Path, required=True)
    ap.add_argument("--openpi-child-root", type=Path, required=True)
    ap.add_argument("--params-root", type=Path, required=True)
    ap.add_argument("--base-receipt", type=Path, required=True)
    ap.add_argument("--norm-stats", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()

    paths = {k: Path(v).resolve() for k, v in vars(args).items()}
    expected_memory_max_gib = 96
    expected_memory_max_bytes = 96 * 1024**3
    status_prefix = "PI05_B1_SERIAL_ITEM_CHECKPOINT_SAVE_STAGE"
    authority_path = paths["authority"]
    parent_failure_path = paths["parent_failure_adjudication"]
    review_path = paths["review"]
    source_adjudication_path = paths["source_adjudication"]
    child_root = paths["openpi_child_root"]
    params_root = paths["params_root"]
    base_receipt = paths["base_receipt"]
    norm_path = paths["norm_stats"]
    output_root = paths["output_root"]
    receipt_path = paths["receipt"]
    lock_path = Path("/data/wyt/.formal-goal-pi05-b1-serial-item-checkpoint-save.lock")

    if receipt_path.exists():
        raise RuntimeError(f"qualification receipt already exists: {receipt_path}")
    if output_root.exists():
        raise RuntimeError(f"qualification output root must be fresh: {output_root}")

    with exclusive_lock(lock_path):
        authority = json.loads(authority_path.read_text())
        if authority.get("status") != "AUTHORIZED_PI05_B1_SERIAL_ITEM_CHECKPOINT_QUALIFICATION":
            raise RuntimeError("B1 qualification authority is not active")
        if authority.get("runner_sha256") != sha256_file(Path(__file__).resolve()):
            raise RuntimeError("runner SHA binding drift")
        if authority.get("parent_failure_adjudication_sha256") != sha256_file(parent_failure_path):
            raise RuntimeError("parent failure adjudication SHA binding drift")
        if authority.get("independent_review_sha256") != sha256_file(review_path):
            raise RuntimeError("B1 independent review SHA binding drift")
        if authority.get("source_adjudication_sha256") != sha256_file(source_adjudication_path):
            raise RuntimeError("B1 source adjudication SHA binding drift")
        parent_failure = json.loads(parent_failure_path.read_text())
        if parent_failure.get("status") != "PI05_CHECKPOINT_SAVE_96G_RESOURCE_CHILD_LIMITER_LEAF_SIZE_HOLD":
            raise RuntimeError("B1 parent failure status drift")
        if parent_failure.get("scientific_boundary", {}).get("formal_run3_authorized") is not False:
            raise RuntimeError("run3 authority unexpectedly open")
        review = json.loads(review_path.read_text())
        if review.get("verdict") != "APPROVE_B1_FIRST" or review.get("run3_authorized_now") is not False:
            raise RuntimeError("B1 independent review verdict drift")
        source_adjudication = json.loads(source_adjudication_path.read_text())
        if source_adjudication.get("status") != "PI05_B1_SERIAL_ITEM_CHECKPOINT_SOURCE_DESIGN_READY":
            raise RuntimeError("B1 source design status drift")
        if source_adjudication.get("formal_run3_authorized") is not False:
            raise RuntimeError("run3 unexpectedly authorized by source design")
        scope = authority.get("resource_scope", {})
        if int(scope.get("memory_max_gib", -1)) != expected_memory_max_gib or int(scope.get("pytree_save_concurrent_gb", -1)) != LIMITER_GB:
            raise RuntimeError("B1 resource scope drift")
        if sha256_file(norm_path) != EXPECTED_NORM_SHA256:
            raise RuntimeError("norm_stats SHA drift")

        child_head = subprocess.check_output(["git", "-C", str(child_root), "rev-parse", "HEAD"], text=True).strip()
        if child_head != EXPECTED_PARENT_COMMIT:
            raise RuntimeError(f"portable child parent drift: {child_head}")
        changed = sorted(line[3:] for line in subprocess.check_output(["git", "-C", str(child_root), "status", "--porcelain"], text=True).splitlines() if line.strip())
        if changed != ["src/openpi/training/config.py"]:
            raise RuntimeError(f"portable child changed-path drift: {changed}")
        config_sha = sha256_file(child_root / "src/openpi/training/config.py")
        if config_sha != EXPECTED_CONFIG_SHA256:
            raise RuntimeError(f"portable config SHA drift: {config_sha}")

        base_sha, base_count, base_bytes = validate_base(base_receipt, params_root)
        scope_before = cgroup_snapshot(expected_memory_max_bytes)
        host_before = host_snapshot()
        gpu_before = gpu_snapshot()
        if len(gpu_before["gpus"]) != 1:
            raise RuntimeError(f"expected exactly one GPU: {gpu_before}")
        g0 = gpu_before["gpus"][0]
        if "A100" not in g0["name"] or g0["memory_total_mib"] < 80_000 or g0["memory_used_mib"] > 1024:
            raise RuntimeError(f"GPU admission failed: {g0}")

        initial = {
            "schema_version": "behavior-formal-goal-coupling-shared26-pi05-b1-serial-item-checkpoint-save-stage-v1",
            "object_id": OBJECT_ID,
            "child_id": CHILD_ID,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": status_prefix + "_STARTED",
            "authority_path": str(authority_path),
            "authority_sha256": sha256_file(authority_path),
            "parent_failure_adjudication_path": str(parent_failure_path),
            "parent_failure_adjudication_sha256": sha256_file(parent_failure_path),
            "independent_review_path": str(review_path),
            "independent_review_sha256": sha256_file(review_path),
            "source_adjudication_path": str(source_adjudication_path),
            "source_adjudication_sha256": sha256_file(source_adjudication_path),
            "runner_sha256": sha256_file(Path(__file__).resolve()),
            "host": "67",
            "expected_memory_max_gib": expected_memory_max_gib,
            "enable_async_checkpointing": False,
            "pytree_save_concurrent_gb": LIMITER_GB,
            "pytree_restore_concurrent_gb": LIMITER_GB,
            "serial_large_items": True,
            "norm_stats_sha256": EXPECTED_NORM_SHA256,
            "batch_size_configured": BATCH,
            "seed": SEED,
            "save_label": SAVE_LABEL,
            "base_receipt_sha256": base_sha,
            "base_object_count_rehashed": base_count,
            "base_bytes_rehashed": base_bytes,
            "portable_openpi_parent_commit": child_head,
            "portable_openpi_config_sha256": config_sha,
            "resource_scope_before": scope_before,
            "host_before": host_before,
            "gpu_before": gpu_before,
            "train_state_ready": False,
            "checkpoint_save_started": False,
            "checkpoint_save_completed": False,
            "checkpoint_restore_completed": False,
            "dataset_accessed": False,
            "forward_pass_executed": False,
            "backward_pass_executed": False,
            "optimizer_update_executed": False,
            "real_scientific_optimizer_updates": 0,
            "policy_outcomes_read": False,
            "loss_values_read_or_reported": False,
            "formal_training_authorized": False,
        }
        atomic_json(receipt_path, initial)

        status = status_prefix + "_HOLD"
        error = None
        state_ready = False
        save_started = False
        save_completed = False
        restore_completed = False
        resolved_checkpointer_type = None
        manager_steps = []
        output_files = 0
        output_bytes = 0
        state_step_after_restore = None
        state_signature_before = None
        state_signature_after = None
        fingerprints = None
        save_events = []
        snapshots = {}
        try:
            os.chdir(child_root)
            sys.path.insert(0, str(child_root))
            sys.path.insert(0, str(child_root / "src"))

            import jax

            def state_signature(tree):
                leaves, treedef = jax.tree.flatten(tree)
                payload = {
                    "treedef": str(treedef),
                    "leaves": [
                        {
                            "shape": list(getattr(x, "shape", ())),
                            "dtype": str(getattr(x, "dtype", type(x).__name__)),
                        }
                        for x in leaves
                    ],
                }
                return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

            import openpi.models.model as model_lib
            import openpi.shared.normalize as normalize
            import openpi.training.checkpoints as checkpoints
            import openpi.training.config as config_lib
            import openpi.training.sharding as sharding
            import openpi.training.weight_loaders as weight_loaders
            from scripts.b1k import train_b1k

            class DirectDeviceCheckpointWeightLoader:
                def __init__(self, params_path: str):
                    self.params_path = params_path
                def load(self, params):
                    loaded = model_lib.restore_params(self.params_path, restore_type=jax.Array)
                    if not all(isinstance(x, jax.Array) for x in jax.tree.leaves(loaded)):
                        raise RuntimeError("direct-device restore returned non-JAX leaves")
                    return weight_loaders._merge_params(loaded, params, missing_regex=".*lora.*")

            @dataclasses.dataclass
            class DataConfigStub:
                norm_stats: object
                asset_id: object

            class LoaderStub:
                def __init__(self, stats):
                    self._stats = stats
                def data_config(self):
                    return DataConfigStub(norm_stats=self._stats, asset_id="b1k_shared26_frozen")

            devices = jax.devices()
            if len(devices) != 1 or devices[0].platform != "gpu":
                raise RuntimeError(f"JAX GPU device drift: {devices}")

            src = config_lib.get_config(CONFIG_NAME)
            cfg = dataclasses.replace(
                src,
                exp_name=EXP_NAME,
                weight_loader=DirectDeviceCheckpointWeightLoader(str(params_root)),
                batch_size=BATCH,
                num_workers=0,
                wandb_enabled=False,
                resume=False,
                overwrite=False,
            )
            if src.batch_size != 64 or cfg.batch_size != BATCH or cfg.seed != SEED or cfg.num_train_steps != 50_000 or cfg.model.action_horizon != 32 or cfg.fsdp_devices != 1:
                raise RuntimeError("practical batch16 config drift")

            mesh = sharding.make_mesh(cfg.fsdp_devices)
            rng = jax.random.key(cfg.seed)
            _train_rng, init_rng = jax.random.split(rng)
            state, _state_sharding = train_b1k.init_train_state(cfg, init_rng, mesh, resume=False)
            jax.block_until_ready(state)
            if int(jax.device_get(state.step)) != 0:
                raise RuntimeError("step-0 state drift")
            state_signature_before = state_signature(state)
            state_ready = True
            snapshots["after_state"] = {"cgroup": cgroup_snapshot(expected_memory_max_bytes), "host": host_snapshot(), "gpu": gpu_snapshot()}
            split_train_state, split_params = checkpoints._split_params(state)
            fingerprints = {
                "train_state": fingerprint_tree(split_train_state, normalize_flax=True),
                "params": fingerprint_tree({"params": split_params}, normalize_flax=False),
            }
            snapshots["after_fingerprint"] = {"cgroup": cgroup_snapshot(expected_memory_max_bytes), "host": host_snapshot(), "gpu": gpu_snapshot()}
            progress = dict(initial)
            progress.update({"generated_at": datetime.now(timezone.utc).isoformat(), "status": status_prefix + "_FINGERPRINTED", "train_state_ready": True, "fingerprints": fingerprints, "snapshots": snapshots})
            atomic_json(receipt_path, progress)

            import orbax.checkpoint as ocp
            from orbax.checkpoint._src.handlers import checkpoint_handler

            class BlockingHandler(checkpoint_handler.CheckpointHandler):
                def __init__(self, name, inner):
                    self.name = name
                    self.inner = inner
                def save(self, directory, *args, **kwargs):
                    start = time.monotonic_ns()
                    try:
                        return self.inner.save(directory, *args, **kwargs)
                    finally:
                        save_events.append({"item": self.name, "start_ns": start, "end_ns": time.monotonic_ns()})
                def restore(self, directory, *args, **kwargs):
                    return self.inner.restore(directory, *args, **kwargs)
                def metadata(self, directory):
                    return self.inner.metadata(directory)
                def finalize(self, directory):
                    return self.inner.finalize(directory)
                def close(self):
                    return self.inner.close()

            output_root.mkdir(parents=True, exist_ok=False)
            inner_train_state = ocp.PyTreeCheckpointHandler(save_concurrent_gb=LIMITER_GB, restore_concurrent_gb=LIMITER_GB)
            inner_params = ocp.PyTreeCheckpointHandler(save_concurrent_gb=LIMITER_GB, restore_concurrent_gb=LIMITER_GB)
            expected_limiter_bytes = LIMITER_GB * 1_000_000_000
            if inner_train_state._save_concurrent_bytes != expected_limiter_bytes or inner_params._save_concurrent_bytes != expected_limiter_bytes:
                raise RuntimeError("8GB save limiter resolution drift")
            if inner_train_state._restore_concurrent_bytes != expected_limiter_bytes or inner_params._restore_concurrent_bytes != expected_limiter_bytes:
                raise RuntimeError("8GB restore limiter resolution drift")
            manager = ocp.CheckpointManager(
                output_root,
                item_handlers={
                    "assets": checkpoints.CallbackHandler(),
                    "train_state": BlockingHandler("train_state", inner_train_state),
                    "params": BlockingHandler("params", inner_params),
                },
                options=ocp.CheckpointManagerOptions(
                    max_to_keep=1,
                    keep_period=cfg.keep_period,
                    create=False,
                    enable_async_checkpointing=False,
                ),
            )
            if isinstance(manager._checkpointer, ocp.AsyncCheckpointer):
                raise RuntimeError("B1 manager resolved to AsyncCheckpointer")
            resolved_checkpointer_type = type(manager._checkpointer).__name__
            save_started = True
            progress.update({"generated_at": datetime.now(timezone.utc).isoformat(), "status": status_prefix + "_SAVE_STARTED", "checkpoint_save_started": True})
            atomic_json(receipt_path, progress)

            norm_stats = normalize.load(norm_path.parent)
            checkpoints.save_state(manager, state, LoaderStub(norm_stats), SAVE_LABEL)
            manager.wait_until_finished()
            save_completed = True
            manager_steps = list(manager.all_steps())
            if manager_steps != [SAVE_LABEL]:
                raise RuntimeError(f"completed checkpoint label drift: {manager_steps}")
            large_events = [x for x in save_events if x["item"] in {"train_state", "params"}]
            if len(large_events) != 2:
                raise RuntimeError(f"expected two large-item save events: {large_events}")
            first, second = sorted(large_events, key=lambda x: x["start_ns"])
            if second["start_ns"] < first["end_ns"]:
                raise RuntimeError("B1 large-item save intervals overlapped")
            step_dir = output_root / str(SAVE_LABEL)
            item_names = sorted(p.name for p in step_dir.iterdir())
            if item_names != ["_CHECKPOINT_METADATA", "assets", "params", "train_state"]:
                raise RuntimeError(f"checkpoint item-name drift: {item_names}")
            tmp_paths = [str(p) for p in output_root.rglob("*orbax-checkpoint-tmp*")]
            if tmp_paths:
                raise RuntimeError(f"temporary checkpoint paths remain after barrier: {tmp_paths[:8]}")
            asset = step_dir / "assets" / "b1k_shared26_frozen" / "norm_stats.json"
            if not asset.is_file() or sha256_file(asset) != EXPECTED_NORM_SHA256:
                raise RuntimeError("checkpoint norm asset drift")
            output_files, output_bytes = tree_bytes(output_root)
            snapshots["after_save"] = {"cgroup": cgroup_snapshot(expected_memory_max_bytes), "host": host_snapshot(), "gpu": gpu_snapshot()}
            manager.close()
            status = status_prefix + "_PASS"
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            try:
                snapshots["after_error"] = {"cgroup": cgroup_snapshot(expected_memory_max_bytes), "host": host_snapshot(), "gpu": gpu_snapshot()}
            except Exception:
                pass
        finally:
            if output_root.exists():
                output_files, output_bytes = tree_bytes(output_root)
            final = dict(initial)
            final.update({
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "train_state_ready": state_ready,
                "checkpoint_save_started": save_started,
                "checkpoint_save_completed": save_completed,
                "checkpoint_restore_completed": False,
                "manager_steps": manager_steps,
                "resolved_checkpointer_type": resolved_checkpointer_type,
                "checkpoint_file_count": output_files,
                "checkpoint_bytes": output_bytes,
                "state_signature_before": state_signature_before,
                "fingerprints": fingerprints,
                "save_events": save_events,
                "serial_large_item_overlap": False if len(save_events) >= 2 else None,
                "snapshots": snapshots,
                "error": error,
                "dataset_accessed": False,
                "forward_pass_executed": False,
                "backward_pass_executed": False,
                "optimizer_update_executed": False,
                "real_scientific_optimizer_updates": 0,
                "policy_outcomes_read": False,
                "loss_values_read_or_reported": False,
                "formal_training_authorized": False,
                "next_gate": "B1_CPU_NUMPY_RESTORE_VALUE_VERIFICATION" if status.endswith("PASS") else "B1_FAILURE_ADJUDICATION_NO_AUTOMATIC_RETRY",
            })
            atomic_json(receipt_path, final)

        print(json.dumps({"status": status, "save_completed": save_completed, "checkpoint_bytes": output_bytes, "error": error}, sort_keys=True))
        return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
