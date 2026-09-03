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
PORTABLE_PARENT_COMMIT = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
PORTABLE_CONFIG_SHA = "4a50bb5f3579ed0035e19d2fc2a5d33821c0cc115c6e8c441eac497e74b02e99"
PREREG_SHA = "382449b4320bacd85f736c0df9342f9677b3c755f2daeedcd680212aed2a503a"
EXHAUSTION_SHA = "96fc40fa4f54f628bb64a021cd9c4e651f48621dc82f4bce99bfcc3a88cb7431"
DIRECT_RESULT_SHA = "5f27f14cfce284f1a75acefafbf9c404556f527b5037007ee8f119df3ddc90df"
BASE_RECEIPT_SHA = "8e0f977e0641960ee3e082a19a57f52f994a817bbf981cbb2f7007ea3104a4ed"
EXPECTED_BASE_OBJECTS = 20
EXPECTED_BASE_BYTES = 12_441_721_931
BATCH = 16
SEED = 42
ACTION_HORIZON = 32
EPISODES = 5200
FSDP = 1
EXPECTED_MEMORY_MAX = 32 * 1024**3
REQUIRED_ENV = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "TOKENIZERS_PARALLELISM": "false",
    "JAX_PLATFORMS": "cuda",
    "XLA_PYTHON_CLIENT_MEM_FRACTION": "0.9",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"{label} missing: {path}")
    got = sha(path)
    if got != expected:
        raise RuntimeError(f"{label} SHA drift: {got}/{expected}")


def write_receipt(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


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


def resource_scope() -> dict:
    rows = Path("/proc/self/cgroup").read_text(encoding="utf-8").splitlines()
    unified = [row.split(":", 2)[2] for row in rows if row.startswith("0::")]
    if len(unified) != 1:
        raise RuntimeError(f"expected one cgroup-v2 path, got {unified}")
    cg = Path("/sys/fs/cgroup") / unified[0].lstrip("/")
    memory_max = (cg / "memory.max").read_text(encoding="utf-8").strip()
    swap_max = (cg / "memory.swap.max").read_text(encoding="utf-8").strip()
    if memory_max == "max" or int(memory_max) != EXPECTED_MEMORY_MAX:
        raise RuntimeError(f"synthetic batch16 gate requires MemoryMax exactly 32G, got {memory_max}")
    if swap_max != "0":
        raise RuntimeError(f"synthetic batch16 gate requires MemorySwapMax=0, got {swap_max}")
    affinity = set(os.sched_getaffinity(0))
    if affinity != set(range(64)):
        raise RuntimeError(f"CPU affinity drift: {sorted(affinity)}")
    return {
        "cgroup": str(cg),
        "memory_max_bytes": int(memory_max),
        "memory_swap_max_bytes": 0,
        "cpu_affinity": "0-63",
    }


def host_memory_snapshot() -> dict:
    out = {}
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        if key in {"MemTotal", "MemAvailable", "MemFree", "SwapTotal", "SwapFree"}:
            out[key + "_kib"] = int(rest.strip().split()[0])
    out["process_rss_kib"] = int(
        Path("/proc/self/status").read_text(encoding="utf-8").split("VmRSS:", 1)[1].splitlines()[0].strip().split()[0]
    )
    return out


def gpu_snapshot() -> dict:
    lines = subprocess.check_output(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
            "--format=csv,noheader,nounits",
        ],
        text=True,
    ).strip().splitlines()
    rows = []
    for line in lines:
        i, name, total, used, util = [x.strip() for x in line.split(",", 4)]
        rows.append(
            {
                "index": int(i),
                "name": name,
                "memory_total_mib": int(total),
                "memory_used_mib": int(used),
                "utilization_gpu_percent": int(util),
            }
        )
    return {"gpus": rows}


def jax_memory_snapshot(device) -> dict | None:
    try:
        stats = device.memory_stats()
    except Exception:
        return None
    if stats is None:
        return None
    return {str(k): v for k, v in stats.items() if isinstance(v, (int, float, str, bool)) or v is None}


def validate_portable_child(root: Path) -> dict:
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != PORTABLE_PARENT_COMMIT:
        raise RuntimeError(f"portable parent drift: {head}")
    config_sha = sha(root / "src/openpi/training/config.py")
    if config_sha != PORTABLE_CONFIG_SHA:
        raise RuntimeError(f"portable config SHA drift: {config_sha}")
    changed = sorted(
        line[3:]
        for line in subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True).splitlines()
        if line.strip()
    )
    if changed != ["src/openpi/training/config.py"]:
        raise RuntimeError(f"portable changed-path drift: {changed}")
    return {"parent_commit": head, "config_sha256": config_sha, "changed_paths": changed}


def validate_checkpoint(receipt_path: Path, params_root: Path) -> dict:
    require(receipt_path, BASE_RECEIPT_SHA, "base checkpoint receipt")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("status") != "PI05_BASE_TRANSPORT_REPAIR1_COMPLETE":
        raise RuntimeError("base checkpoint receipt status drift")
    rows = receipt.get("objects") or []
    if len(rows) != EXPECTED_BASE_OBJECTS:
        raise RuntimeError("base checkpoint object-count drift")
    total = 0
    for row in rows:
        path = params_root / row["relative_path"]
        if not path.is_file() or path.stat().st_size != int(row["size"]):
            raise RuntimeError(f"base checkpoint object missing/size drift: {row['relative_path']}")
        if sha(path) != row["local_sha256"]:
            raise RuntimeError(f"base checkpoint SHA drift: {row['relative_path']}")
        total += int(row["size"])
    all_files = [p for p in params_root.rglob("*") if p.is_file()]
    if len(all_files) != EXPECTED_BASE_OBJECTS or total != EXPECTED_BASE_BYTES:
        raise RuntimeError(f"base checkpoint total drift files={len(all_files)} bytes={total}")
    return {"object_count": len(rows), "bytes": total}


def main() -> int:
    ap = argparse.ArgumentParser()
    for name in [
        "authority",
        "preregistration",
        "exhaustion_adjudication",
        "portable_direct_device_result",
        "base_receipt",
        "openpi_child_root",
        "params_root",
        "receipt",
    ]:
        ap.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    args = ap.parse_args()
    paths = {name: getattr(args, name).resolve() for name in vars(args)}
    receipt_path = paths["receipt"]
    if receipt_path.exists():
        raise RuntimeError(f"exactly-once synthetic practical-batch16 receipt exists: {receipt_path}")

    authority = json.loads(paths["authority"].read_text(encoding="utf-8"))
    if authority.get("status") != "AUTHORIZED_PI05_PRACTICAL_BATCH16_SYNTHETIC_FULL_STEP_RESOURCE_GATE":
        raise RuntimeError("batch16 authority is not active")
    if authority.get("runner_sha256") != sha(Path(__file__).resolve()):
        raise RuntimeError("runner SHA binding drift")
    require(paths["preregistration"], PREREG_SHA, "practical-batch preregistration")
    require(paths["exhaustion_adjudication"], EXHAUSTION_SHA, "accumulation exhaustion adjudication")
    require(paths["portable_direct_device_result"], DIRECT_RESULT_SHA, "portable direct-device result")
    prereg = json.loads(paths["preregistration"].read_text(encoding="utf-8"))
    if prereg.get("status") != "PREREGISTERED_PRACTICAL_SINGLE_GPU_BATCH_LADDER_NO_OUTCOME_ACCESS":
        raise RuntimeError("practical prereg status drift")
    if prereg.get("batch_resource_ladder", [None])[0] != {
        "priority": 1,
        "physical_batch": 16,
        "effective_optimizer_batch": 16,
        "gradient_accumulation": 1,
    }:
        raise RuntimeError("batch16 ladder drift")
    exhaustion = json.loads(paths["exhaustion_adjudication"].read_text(encoding="utf-8"))
    if exhaustion.get("status") != "PI05_SINGLE_A100_FP32_ACCUMULATION_LADDER_EXHAUSTED":
        raise RuntimeError("accumulation exhaustion status drift")
    direct = json.loads(paths["portable_direct_device_result"].read_text(encoding="utf-8"))
    if direct.get("status") != "PI05_PORTABLE_DIRECT_DEVICE_NO_UPDATE_MODEL_LOAD_PASS" or direct.get("initialized_step") != 0:
        raise RuntimeError("portable direct-device result drift")
    for key, value in REQUIRED_ENV.items():
        if os.environ.get(key) != value:
            raise RuntimeError(f"environment drift {key}={os.environ.get(key)!r}/{value!r}")

    scope = resource_scope()
    portable = validate_portable_child(paths["openpi_child_root"])
    checkpoint = validate_checkpoint(paths["base_receipt"], paths["params_root"])
    before_gpu = gpu_snapshot()
    if len(before_gpu["gpus"]) != 1:
        raise RuntimeError(f"expected one GPU, got {before_gpu}")
    gpu0 = before_gpu["gpus"][0]
    if "A100" not in gpu0["name"] or gpu0["memory_total_mib"] < 80_000:
        raise RuntimeError(f"unexpected GPU: {gpu0}")
    if gpu0["memory_used_mib"] > 1024 or gpu0["utilization_gpu_percent"] > 25:
        raise RuntimeError(f"GPU busy; no attempt consumed: {gpu0}")
    host_before = host_memory_snapshot()

    initial = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-practical-batch16-synthetic-full-step-result-v1",
        "object_id": OBJECT_ID,
        "child_id": CHILD_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_PRACTICAL_BATCH16_SYNTHETIC_FULL_STEP_STARTED",
        "physical_batch": BATCH,
        "effective_optimizer_batch": BATCH,
        "gradient_accumulation": 1,
        "authority_sha256": sha(paths["authority"]),
        "preregistration_sha256": PREREG_SHA,
        "exhaustion_adjudication_sha256": EXHAUSTION_SHA,
        "portable_direct_device_result_sha256": DIRECT_RESULT_SHA,
        "portable_openpi": portable,
        "checkpoint": checkpoint,
        "resource_scope": scope,
        "gpu_before": before_gpu,
        "host_memory_before": host_before,
        "train_state_ready": False,
        "synthetic_full_step_started": False,
        "synthetic_full_step_completed": False,
        "synthetic_optimizer_update_executed": False,
        "real_scientific_optimizer_updates": 0,
        "loss_value_retained_or_reported": False,
        "gradient_numerical_values_inspected": False,
        "behavior_dataset_accessed": False,
        "checkpoint_written": False,
        "policy_outcomes_read": False,
        "formal_training_authorized": False,
    }

    lock_path = Path("/data/wyt/.formal-goal-pi05-practical-batch16-synthetic-full-step.lock")
    with exclusive_lock(lock_path):
        write_receipt(receipt_path, initial)
        status = "PI05_PRACTICAL_BATCH16_SYNTHETIC_FULL_STEP_HOLD"
        error = None
        state_ready = False
        step_after = None
        gpu_after_state = None
        gpu_after_step = None
        jax_after_state = None
        jax_after_step = None
        host_after_state = None
        host_after_step = None
        full_step_started = False
        full_step_completed = False
        try:
            root = paths["openpi_child_root"]
            os.chdir(root)
            sys.path.insert(0, str(root))
            sys.path.insert(0, str(root / "src"))

            import jax
            import openpi.models.model as model_lib
            import openpi.training.config as config_lib
            import openpi.training.sharding as sharding
            import openpi.training.weight_loaders as weight_loaders
            from scripts.b1k import train_b1k

            class DirectDeviceCheckpointWeightLoader:
                def __init__(self, params_path: str):
                    self.params_path = params_path

                def load(self, params):
                    loaded = model_lib.restore_params(self.params_path, restore_type=jax.Array)
                    leaves = jax.tree.leaves(loaded)
                    if not leaves or not all(isinstance(x, jax.Array) for x in leaves):
                        raise RuntimeError("direct-device restore returned non-jax.Array leaves")
                    return weight_loaders._merge_params(loaded, params, missing_regex=".*lora.*")

            devices = jax.devices()
            if len(devices) != 1 or devices[0].platform != "gpu":
                raise RuntimeError(f"expected one CUDA device, got {devices}")
            device = devices[0]
            source_config = config_lib.get_config(CONFIG_NAME)
            config = dataclasses.replace(
                source_config,
                exp_name=EXP_NAME,
                weight_loader=DirectDeviceCheckpointWeightLoader(str(paths["params_root"])),
                batch_size=BATCH,
                num_workers=0,
                wandb_enabled=False,
                resume=False,
                overwrite=True,
            )
            episodes = list(config.data.base_config.dataset_kwargs.get("episodes", []))
            if (
                source_config.batch_size != 64
                or config.batch_size != BATCH
                or config.seed != SEED
                or config.num_train_steps != 50_000
                or config.model.action_horizon != ACTION_HORIZON
                or config.fsdp_devices != FSDP
                or len(episodes) != EPISODES
                or len(set(episodes)) != EPISODES
            ):
                raise RuntimeError("practical-batch16 config drift")

            mesh = sharding.make_mesh(config.fsdp_devices)
            data_sharding = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec(sharding.DATA_AXIS))
            replicated_sharding = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec())
            rng = jax.random.key(config.seed)
            train_rng, init_rng = jax.random.split(rng)
            state, state_sharding = train_b1k.init_train_state(config, init_rng, mesh, resume=False)
            jax.block_until_ready(state)
            if int(jax.device_get(state.step)) != 0:
                raise RuntimeError("step-0 state drift")
            state_ready = True
            gpu_after_state = gpu_snapshot()
            jax_after_state = jax_memory_snapshot(device)
            host_after_state = host_memory_snapshot()

            fake_batch = (config.model.fake_obs(batch_size=BATCH), config.model.fake_act(batch_size=BATCH))
            fake_batch = jax.tree.map(lambda x: jax.device_put(x, data_sharding), fake_batch)
            ptrain = jax.jit(
                functools.partial(train_b1k.train_step, config),
                in_shardings=(replicated_sharding, state_sharding, data_sharding),
                out_shardings=(state_sharding, replicated_sharding),
                donate_argnums=(1,),
            )
            progress = dict(initial)
            progress.update(
                {
                    "status": "PI05_PRACTICAL_BATCH16_SYNTHETIC_FULL_STEP_UPDATE_STARTED",
                    "train_state_ready": True,
                    "synthetic_full_step_started": True,
                    "gpu_after_state": gpu_after_state,
                    "jax_memory_after_state": jax_after_state,
                    "host_memory_after_state": host_after_state,
                }
            )
            write_receipt(receipt_path, progress)
            full_step_started = True

            new_state, info = ptrain(train_rng, state, fake_batch)
            jax.block_until_ready(new_state)
            step_after = int(jax.device_get(new_state.step))
            if step_after != 1:
                raise RuntimeError(f"synthetic train step did not advance 0->1: {step_after}")
            full_step_completed = True
            gpu_after_step = gpu_snapshot()
            jax_after_step = jax_memory_snapshot(device)
            host_after_step = host_memory_snapshot()
            status = "PI05_PRACTICAL_BATCH16_SYNTHETIC_FULL_STEP_PASS"
            del info, new_state, state, fake_batch
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            try:
                gpu_after_step = gpu_snapshot()
                host_after_step = host_memory_snapshot()
            except Exception:
                pass
        finally:
            final = dict(initial)
            final.update(
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "status": status,
                    "train_state_ready": state_ready,
                    "synthetic_full_step_started": full_step_started,
                    "synthetic_full_step_completed": full_step_completed,
                    "synthetic_step_after": step_after,
                    "synthetic_optimizer_update_executed": full_step_completed,
                    "real_scientific_optimizer_updates": 0,
                    "gpu_after_state": gpu_after_state,
                    "gpu_after_step_or_error": gpu_after_step,
                    "jax_memory_after_state": jax_after_state,
                    "jax_memory_after_step": jax_after_step,
                    "host_memory_after_state": host_after_state,
                    "host_memory_after_step_or_error": host_after_step,
                    "error": error,
                    "loss_value_retained_or_reported": False,
                    "gradient_numerical_values_inspected": False,
                    "behavior_dataset_accessed": False,
                    "checkpoint_written": False,
                    "policy_outcomes_read": False,
                    "scientific_training_started": False,
                    "formal_training_authorized": False,
                    "next_gate": (
                        "FREEZE_PRACTICAL_BATCH16_REAL_DATA_TRAINING_IMPLEMENTATION"
                        if status.endswith("PASS")
                        else "PRACTICAL_BATCH16_RESOURCE_ADJUDICATION_THEN_BATCH8"
                    ),
                }
            )
            write_receipt(receipt_path, final)

        print(
            json.dumps(
                {
                    "status": status,
                    "train_state_ready": state_ready,
                    "synthetic_full_step_completed": full_step_completed,
                    "synthetic_step_after": step_after,
                    "error": error,
                },
                sort_keys=True,
            )
        )
        return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
