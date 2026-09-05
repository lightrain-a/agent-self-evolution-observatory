from __future__ import annotations

import argparse
import dataclasses
import fcntl
import hashlib
import json
import os
import subprocess
import sys
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
BATCH = 16
SEED = 42
SAVE_LABEL = 10000
MEMORY_MAX_BYTES = 40 * 1024**3


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


def cgroup_snapshot() -> dict:
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
    if memory_max in (None, "max") or int(memory_max) != MEMORY_MAX_BYTES:
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority", type=Path, required=True)
    ap.add_argument("--adjudication", type=Path, required=True)
    ap.add_argument("--openpi-child-root", type=Path, required=True)
    ap.add_argument("--params-root", type=Path, required=True)
    ap.add_argument("--base-receipt", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()

    paths = {k: Path(v).resolve() for k, v in vars(args).items()}
    authority_path = paths["authority"]
    adjudication_path = paths["adjudication"]
    child_root = paths["openpi_child_root"]
    params_root = paths["params_root"]
    base_receipt = paths["base_receipt"]
    output_root = paths["output_root"]
    receipt_path = paths["receipt"]
    lock_path = Path("/data/wyt/.formal-goal-pi05-step0-checkpoint-save-qualification.lock")

    if receipt_path.exists():
        raise RuntimeError(f"qualification receipt already exists: {receipt_path}")
    if output_root.exists():
        raise RuntimeError(f"qualification output root must be fresh: {output_root}")

    with exclusive_lock(lock_path):
        authority = json.loads(authority_path.read_text())
        if authority.get("status") != "AUTHORIZED_PI05_STEP0_CHECKPOINT_SAVE_40G_QUALIFICATION":
            raise RuntimeError("qualification authority is not active")
        if authority.get("runner_sha256") != sha256_file(Path(__file__).resolve()):
            raise RuntimeError("runner SHA binding drift")
        if authority.get("adjudication_sha256") != sha256_file(adjudication_path):
            raise RuntimeError("run2 adjudication SHA binding drift")
        adjudication = json.loads(adjudication_path.read_text())
        if adjudication.get("status") != "PI05_FORMAL_RUN2_CHECKPOINT10000_HARD_EXIT_NO_EXACT_STATE_RECOVERY":
            raise RuntimeError("run2 adjudication status drift")
        if adjudication.get("scientific_disposition", {}).get("run3_formal_training_authorized") is not False:
            raise RuntimeError("run3 authority unexpectedly open")

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
        scope_before = cgroup_snapshot()
        host_before = host_snapshot()
        gpu_before = gpu_snapshot()
        if len(gpu_before["gpus"]) != 1:
            raise RuntimeError(f"expected exactly one GPU: {gpu_before}")
        g0 = gpu_before["gpus"][0]
        if "A100" not in g0["name"] or g0["memory_total_mib"] < 80_000 or g0["memory_used_mib"] > 1024:
            raise RuntimeError(f"GPU admission failed: {g0}")

        initial = {
            "schema_version": "behavior-formal-goal-coupling-shared26-pi05-step0-checkpoint-save-qualification-v1",
            "object_id": OBJECT_ID,
            "child_id": CHILD_ID,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "PI05_STEP0_CHECKPOINT_SAVE_40G_STARTED",
            "authority_path": str(authority_path),
            "authority_sha256": sha256_file(authority_path),
            "adjudication_path": str(adjudication_path),
            "adjudication_sha256": sha256_file(adjudication_path),
            "runner_sha256": sha256_file(Path(__file__).resolve()),
            "host": "67",
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

        status = "PI05_STEP0_CHECKPOINT_SAVE_40G_HOLD"
        error = None
        state_ready = False
        save_started = False
        save_completed = False
        restore_completed = False
        manager_steps = []
        output_files = 0
        output_bytes = 0
        state_step_after_restore = None
        snapshots = {}
        try:
            os.chdir(child_root)
            sys.path.insert(0, str(child_root))
            sys.path.insert(0, str(child_root / "src"))

            import jax
            import openpi.models.model as model_lib
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
                norm_stats: object = None
                asset_id: object = None

            class LoaderStub:
                def data_config(self):
                    return DataConfigStub()

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
            state_ready = True
            snapshots["after_state"] = {"cgroup": cgroup_snapshot(), "host": host_snapshot(), "gpu": gpu_snapshot()}
            progress = dict(initial)
            progress.update({"generated_at": datetime.now(timezone.utc).isoformat(), "status": "PI05_STEP0_CHECKPOINT_SAVE_40G_STATE_READY", "train_state_ready": True, "snapshots": snapshots})
            atomic_json(receipt_path, progress)

            manager, resuming = checkpoints.initialize_checkpoint_dir(output_root, keep_period=cfg.keep_period, overwrite=False, resume=False)
            if resuming:
                raise RuntimeError("unexpected checkpoint qualification resume")
            save_started = True
            progress.update({"generated_at": datetime.now(timezone.utc).isoformat(), "status": "PI05_STEP0_CHECKPOINT_SAVE_40G_SAVE_STARTED", "checkpoint_save_started": True})
            atomic_json(receipt_path, progress)

            checkpoints.save_state(manager, state, LoaderStub(), SAVE_LABEL)
            manager.wait_until_finished()
            save_completed = True
            manager_steps = list(manager.all_steps())
            if SAVE_LABEL not in manager_steps:
                raise RuntimeError(f"completed checkpoint label missing: {manager_steps}")
            output_files, output_bytes = tree_bytes(output_root)
            snapshots["after_save"] = {"cgroup": cgroup_snapshot(), "host": host_snapshot(), "gpu": gpu_snapshot()}
            progress.update({
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "PI05_STEP0_CHECKPOINT_SAVE_40G_SAVE_COMPLETE",
                "checkpoint_save_completed": True,
                "manager_steps": manager_steps,
                "checkpoint_file_count": output_files,
                "checkpoint_bytes": output_bytes,
                "snapshots": snapshots,
            })
            atomic_json(receipt_path, progress)

            restored = checkpoints.restore_state(manager, state, LoaderStub(), step=SAVE_LABEL)
            jax.block_until_ready(restored)
            state_step_after_restore = int(jax.device_get(restored.step))
            if state_step_after_restore != 0:
                raise RuntimeError(f"restored state-step drift: {state_step_after_restore}")
            restore_completed = True
            snapshots["after_restore"] = {"cgroup": cgroup_snapshot(), "host": host_snapshot(), "gpu": gpu_snapshot()}
            status = "PI05_STEP0_CHECKPOINT_SAVE_40G_PASS"
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            try:
                snapshots["after_error"] = {"cgroup": cgroup_snapshot(), "host": host_snapshot(), "gpu": gpu_snapshot()}
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
                "checkpoint_restore_completed": restore_completed,
                "manager_steps": manager_steps,
                "checkpoint_file_count": output_files,
                "checkpoint_bytes": output_bytes,
                "restored_state_step": state_step_after_restore,
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
                "next_gate": "ASYNC_CHECKPOINT_OVERLAP_DIAGNOSTIC_OR_BARRIER_REPAIR_ADJUDICATION" if status.endswith("PASS") else "CHECKPOINT_SAVE_RESOURCE_FAILURE_ADJUDICATION_NO_FORMAL_RESTART",
            })
            atomic_json(receipt_path, final)

        print(json.dumps({"status": status, "save_completed": save_completed, "restore_completed": restore_completed, "checkpoint_bytes": output_bytes, "error": error}, sort_keys=True))
        return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
