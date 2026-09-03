from __future__ import annotations

import argparse
import dataclasses
import fcntl
import functools
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
EXP_NAME = "shared26-seed42-practical-b16-run1"
PARENT_COMMIT = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
CONFIG_SHA = "4a50bb5f3579ed0035e19d2fc2a5d33821c0cc115c6e8c441eac497e74b02e99"
PRACTICAL_PREREG_SHA = "382449b4320bacd85f736c0df9342f9677b3c755f2daeedcd680212aed2a503a"
SYNTHETIC_BATCH16_RESULT_SHA = "3914b1f2a3fd5e7964524eac7f625b64b4f089c0048a12dc5ebe9b79ba9bd86e"
BASE_RECEIPT_SHA = "8e0f977e0641960ee3e082a19a57f52f994a817bbf981cbb2f7007ea3104a4ed"
NORM_SHA = "5e4159ec0986ad9fc87cc9a265eed9ac67fc9d2d0df233db6130acf0ebff52ce"
TOKEN_SHA = "8986bb4f423f07f8c7f70d0dbe3526fb2316056c17bae71b1ea975e77a168fc6"
PROJECTION_INFO_SHA = "9955a58511fdba468ca10b6929c9051f6d693e3915cdc58d66c1cd1ce04a45e1"
BATCH = 16
SEED = 42
ACTION_HORIZON = 32
EPISODES = 5200
NUM_UPDATES = 50_000
TERMINAL_LABEL = 49_999
FSDP = 1
NUM_WORKERS = 0
EXPECTED_MEMORY_MAX = 40 * 1024**3
REQUIRED_ENV = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "TOKENIZERS_PARALLELISM": "false",
    "JAX_PLATFORMS": "cuda",
    "XLA_PYTHON_CLIENT_MEM_FRACTION": "0.9",
    "HF_HUB_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"{label} missing: {path}")
    got = sha(path)
    if got != expected:
        raise RuntimeError(f"{label} SHA drift: {got}/{expected}")


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


@contextmanager
def lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open("a+")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        f.seek(0); f.truncate(); f.write(f"pid={os.getpid()}\n"); f.flush(); os.fsync(f.fileno())
        yield
    finally:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN); f.close()


def scope_snapshot() -> dict:
    rows = Path("/proc/self/cgroup").read_text().splitlines()
    ids = [r.split(":", 2)[2] for r in rows if r.startswith("0::")]
    if len(ids) != 1:
        raise RuntimeError(f"cgroup-v2 drift: {ids}")
    cg = Path("/sys/fs/cgroup") / ids[0].lstrip("/")
    mm = (cg / "memory.max").read_text().strip(); sm = (cg / "memory.swap.max").read_text().strip()
    if mm == "max" or int(mm) != EXPECTED_MEMORY_MAX:
        raise RuntimeError(f"formal batch16 requires MemoryMax exactly 40G, got {mm}")
    if sm != "0":
        raise RuntimeError(f"formal batch16 requires MemorySwapMax=0, got {sm}")
    if set(os.sched_getaffinity(0)) != set(range(64)):
        raise RuntimeError("CPU affinity drift")
    return {"cgroup": str(cg), "memory_max_bytes": int(mm), "memory_swap_max_bytes": 0, "cpu_affinity": "0-63"}


def gpu_snapshot() -> dict:
    lines = subprocess.check_output([
        "nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
        "--format=csv,noheader,nounits",
    ], text=True).strip().splitlines()
    out = []
    for line in lines:
        i, name, total, used, util = [x.strip() for x in line.split(",", 4)]
        out.append({"index": int(i), "name": name, "memory_total_mib": int(total), "memory_used_mib": int(used), "utilization_gpu_percent": int(util)})
    return {"gpus": out}


def host_snapshot() -> dict:
    out = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        if key in {"MemTotal", "MemAvailable", "MemFree", "SwapTotal", "SwapFree"}:
            out[key + "_kib"] = int(rest.strip().split()[0])
    out["process_rss_kib"] = int(Path("/proc/self/status").read_text().split("VmRSS:", 1)[1].splitlines()[0].strip().split()[0])
    return out


def portable_child(root: Path) -> dict:
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != PARENT_COMMIT:
        raise RuntimeError(f"portable parent drift: {head}")
    cfg_sha = sha(root / "src/openpi/training/config.py")
    if cfg_sha != CONFIG_SHA:
        raise RuntimeError(f"portable config SHA drift: {cfg_sha}")
    changed = sorted(line[3:] for line in subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True).splitlines() if line.strip())
    if changed != ["src/openpi/training/config.py"]:
        raise RuntimeError(f"portable changed-path drift: {changed}")
    return {"parent_commit": head, "config_sha256": cfg_sha, "changed_paths": changed}


def main() -> int:
    ap = argparse.ArgumentParser()
    for name in [
        "authority", "preregistration", "synthetic_batch16_result", "real_data_smoke", "dataset_seal", "base_receipt",
        "openpi_child_root", "params_root", "projection_root", "norm_stats", "tokenizer", "progress", "result",
    ]:
        ap.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    a = ap.parse_args(); p = {k: getattr(a, k).resolve() for k in vars(a)}
    if p["result"].exists() or p["progress"].exists():
        raise RuntimeError("formal batch16 result/progress already exists; exactly-once launch cannot be replayed")

    auth = json.loads(p["authority"].read_text())
    if auth.get("status") != "AUTHORIZED_PI05_PRACTICAL_BATCH16_FORMAL_TRAINING":
        raise RuntimeError("formal training authority not active")
    if auth.get("runner_sha256") != sha(Path(__file__).resolve()):
        raise RuntimeError("formal runner SHA binding drift")
    require(p["preregistration"], PRACTICAL_PREREG_SHA, "practical prereg")
    require(p["synthetic_batch16_result"], SYNTHETIC_BATCH16_RESULT_SHA, "synthetic batch16 result")
    synth = json.loads(p["synthetic_batch16_result"].read_text())
    if synth.get("status") != "PI05_PRACTICAL_BATCH16_SYNTHETIC_FULL_STEP_PASS":
        raise RuntimeError("synthetic batch16 gate not PASS")
    smoke_sha = sha(p["real_data_smoke"])
    if smoke_sha != auth.get("real_data_smoke_sha256"):
        raise RuntimeError("real-data smoke SHA binding drift")
    smoke = json.loads(p["real_data_smoke"].read_text())
    if smoke.get("status") != "PI05_PRACTICAL_BATCH16_REAL_DATA_ZERO_UPDATE_PASS" or smoke.get("optimizer_update"):
        raise RuntimeError("real-data smoke not PASS")
    seal_sha = sha(p["dataset_seal"])
    if seal_sha != auth.get("dataset_seal_sha256"):
        raise RuntimeError("dataset seal SHA binding drift")
    seal = json.loads(p["dataset_seal"].read_text())
    if seal.get("status") != "WHOLE_MANIFEST_FINAL_SEAL_PASS" or seal.get("verified_file_count") != 1380 or seal.get("verified_bytes") != 236480375583:
        raise RuntimeError("dataset seal not PASS")
    require(p["base_receipt"], BASE_RECEIPT_SHA, "base receipt")
    require(p["projection_root"] / "meta/info.json", PROJECTION_INFO_SHA, "projection info")
    require(p["norm_stats"], NORM_SHA, "norm stats")
    require(p["tokenizer"], TOKEN_SHA, "tokenizer")
    for key, value in REQUIRED_ENV.items():
        if os.environ.get(key) != value:
            raise RuntimeError(f"environment drift {key}={os.environ.get(key)!r}/{value!r}")
    if Path(os.environ.get("OPENPI_DATA_HOME", "")).resolve() != Path(auth["openpi_data_home"]).resolve():
        raise RuntimeError("OPENPI_DATA_HOME drift")
    scope = scope_snapshot(); child = portable_child(p["openpi_child_root"])
    before_gpu = gpu_snapshot(); before_host = host_snapshot()
    if len(before_gpu["gpus"]) != 1 or "A100" not in before_gpu["gpus"][0]["name"] or before_gpu["gpus"][0]["memory_used_mib"] > 1024 or before_gpu["gpus"][0]["utilization_gpu_percent"] > 25:
        raise RuntimeError(f"GPU not admitted: {before_gpu}")

    checkpoint_dir = p["openpi_child_root"] / "outputs/checkpoints" / CONFIG_NAME / EXP_NAME
    if checkpoint_dir.exists():
        raise RuntimeError(f"fresh formal checkpoint directory already exists: {checkpoint_dir}")

    with lock(Path("/data/wyt/.formal-goal-pi05-practical-batch16-formal-train.lock")):
        started = {
            "schema_version": "behavior-formal-goal-coupling-shared26-pi05-practical-batch16-formal-training-progress-v1",
            "object_id": OBJECT_ID, "child_id": CHILD_ID, "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "PI05_PRACTICAL_BATCH16_FORMAL_TRAINING_STARTED", "exp_name": EXP_NAME,
            "batch_size": BATCH, "seed": SEED, "target_optimizer_updates": NUM_UPDATES,
            "completed_optimizer_updates": 0, "last_completed_loop_label": None,
            "terminal_checkpoint_label_for_scientific_evaluation": TERMINAL_LABEL,
            "authority_sha256": sha(p["authority"]), "real_data_smoke_sha256": smoke_sha,
            "dataset_seal_sha256": seal_sha, "portable_openpi": child, "resource_scope": scope,
            "gpu_before": before_gpu, "host_before": before_host,
            "loss_values_read_or_reported": False, "policy_outcomes_read": False,
            "scientific_training_started": True, "formal_training_authorized": True,
        }
        atomic_json(p["progress"], started)
        status = "PI05_PRACTICAL_BATCH16_FORMAL_TRAINING_HOLD"
        error = None; completed_updates = 0; last_label = None; terminal_present = False
        try:
            root = p["openpi_child_root"]; os.chdir(root); sys.path.insert(0, str(root)); sys.path.insert(0, str(root / "src"))
            import jax
            import openpi.models.model as model_lib
            import openpi.training.checkpoints as checkpoints
            import openpi.training.config as config_lib
            import openpi.training.data_loader as data_loader
            import openpi.training.sharding as sharding
            import openpi.training.weight_loaders as weight_loaders
            from scripts.b1k import train_b1k

            jax.config.update("jax_compilation_cache_dir", str(Path("~/.cache/jax").expanduser()))

            class DirectDeviceCheckpointWeightLoader:
                def __init__(self, path: str): self.path = path
                def load(self, params):
                    loaded = model_lib.restore_params(self.path, restore_type=jax.Array)
                    if not all(isinstance(x, jax.Array) for x in jax.tree.leaves(loaded)):
                        raise RuntimeError("non-jax checkpoint leaf")
                    return weight_loaders._merge_params(loaded, params, missing_regex=".*lora.*")

            devices = jax.devices()
            if len(devices) != 1 or devices[0].platform != "gpu":
                raise RuntimeError(f"CUDA device drift: {devices}")
            src = config_lib.get_config(CONFIG_NAME)
            cfg = dataclasses.replace(
                src, exp_name=EXP_NAME, weight_loader=DirectDeviceCheckpointWeightLoader(str(p["params_root"])),
                batch_size=BATCH, num_workers=NUM_WORKERS, wandb_enabled=False, resume=False, overwrite=False,
            )
            episodes = list(cfg.data.base_config.dataset_kwargs.get("episodes", []))
            if (
                src.batch_size != 64 or cfg.batch_size != BATCH or cfg.seed != SEED or cfg.num_train_steps != NUM_UPDATES
                or cfg.model.action_horizon != ACTION_HORIZON or cfg.fsdp_devices != FSDP or cfg.num_workers != 0
                or cfg.val_log_interval is not None or len(episodes) != EPISODES or len(set(episodes)) != EPISODES
            ):
                raise RuntimeError("formal batch16 config drift")
            if Path(cfg.checkpoint_dir).resolve() != checkpoint_dir.resolve():
                raise RuntimeError(f"checkpoint-dir drift: {cfg.checkpoint_dir}/{checkpoint_dir}")

            mesh = sharding.make_mesh(cfg.fsdp_devices)
            ds = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec(sharding.DATA_AXIS))
            rs = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec())
            rng = jax.random.key(cfg.seed); train_rng, init_rng = jax.random.split(rng)

            # State-first resource realization: no real batch is decoded until direct-device state restore is complete.
            state, state_sharding = train_b1k.init_train_state(cfg, init_rng, mesh, resume=False)
            jax.block_until_ready(state)
            if int(jax.device_get(state.step)) != 0:
                raise RuntimeError("formal state did not initialize at step0")

            loader = data_loader.create_b1k_data_loader(cfg, sharding=ds, shuffle=True, skip_norm_stats=False)
            data_iter = iter(loader); batch = next(data_iter)
            manager, resuming = checkpoints.initialize_checkpoint_dir(checkpoint_dir, keep_period=cfg.keep_period, overwrite=False, resume=False)
            if resuming:
                raise RuntimeError("unexpected formal resume state")
            ptrain = jax.jit(
                functools.partial(train_b1k.train_step, cfg),
                in_shardings=(rs, state_sharding, ds),
                out_shardings=(state_sharding, rs),
                donate_argnums=(1,),
            )

            for label in range(NUM_UPDATES):
                with sharding.set_mesh(mesh):
                    state, info = ptrain(train_rng, state, batch)
                del info
                completed_updates = label + 1; last_label = label
                if label < NUM_UPDATES - 1:
                    batch = next(data_iter)
                if label % 100 == 0 or label == TERMINAL_LABEL:
                    current_step = int(jax.device_get(state.step))
                    if current_step != completed_updates:
                        raise RuntimeError(f"train step drift label={label} state_step={current_step}")
                    prog = dict(started); prog.update({
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "status": "PI05_PRACTICAL_BATCH16_FORMAL_TRAINING_RUNNING",
                        "completed_optimizer_updates": completed_updates,
                        "last_completed_loop_label": last_label,
                        "checkpoint_labels_present": list(manager.all_steps()),
                    }); atomic_json(p["progress"], prog)
                if (label % cfg.save_interval == 0 and label > 0) or label == TERMINAL_LABEL:
                    checkpoints.save_state(manager, state, loader, label)

            manager.wait_until_finished()
            if int(jax.device_get(state.step)) != NUM_UPDATES:
                raise RuntimeError(f"terminal state step drift: {jax.device_get(state.step)}")
            labels = tuple(manager.all_steps()); terminal_present = TERMINAL_LABEL in labels
            if not terminal_present:
                raise RuntimeError(f"terminal checkpoint {TERMINAL_LABEL} missing: {labels}")
            status = "PI05_PRACTICAL_BATCH16_FORMAL_TRAINING_COMPLETE"
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        finally:
            result = {
                "schema_version": "behavior-formal-goal-coupling-shared26-pi05-practical-batch16-formal-training-result-v1",
                "object_id": OBJECT_ID, "child_id": CHILD_ID, "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": status, "exp_name": EXP_NAME, "batch_size": BATCH, "seed": SEED,
                "target_optimizer_updates": NUM_UPDATES, "completed_optimizer_updates": completed_updates,
                "last_completed_loop_label": last_label, "terminal_checkpoint_label": TERMINAL_LABEL,
                "terminal_checkpoint_present": terminal_present, "checkpoint_dir": str(checkpoint_dir),
                "error": error, "loss_values_read_or_reported": False, "validation_executed": False,
                "wandb_enabled": False, "policy_rollouts_started": False, "policy_outcomes_read": False,
                "scientific_training_started": completed_updates > 0, "formal_training_authorized": True,
                "next_gate": "PI05_TERMINAL_CHECKPOINT_49999_CONTENT_ADDRESS_AND_SERVING_QUALIFICATION" if status.endswith("COMPLETE") else "FORMAL_TRAINING_FAILURE_EXACT_STATE_ADJUDICATION",
            }
            atomic_json(p["result"], result)
        print(json.dumps({"status": status, "completed_optimizer_updates": completed_updates, "last_label": last_label, "terminal_present": terminal_present, "error": error}, sort_keys=True))
        return 0 if status.endswith("COMPLETE") else 2


if __name__ == "__main__":
    raise SystemExit(main())
