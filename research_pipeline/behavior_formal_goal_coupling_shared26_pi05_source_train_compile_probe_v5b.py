from __future__ import annotations

import argparse
import dataclasses
import functools
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
EXPECTED_CHILD_COMMIT = "0d05f46ef40a6a0ff0a9b61f078835a71fececde"
EXPECTED_BATCH_SIZE = 64
EXPECTED_SEED = 42
EXPECTED_ACTION_HORIZON = 32
EXPECTED_EPISODE_COUNT = 5200
EXPECTED_NUM_WORKERS = 0
EXPECTED_MEM_FRACTION = "0.9"
EXPECTED_TRAIN_SCRIPT_SHA256 = "9e1ac351c8f491d0c5307963d11ab07b008548da2bcd29a4670e88622eae6507"
MAX_GPU_USED_BEFORE_MIB = 4096


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def gpu_snapshot() -> dict:
    text = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
        text=True,
    ).strip()
    rows = []
    for line in text.splitlines():
        index, name, total, used, util = [x.strip() for x in line.split(",", 4)]
        rows.append({
            "index": int(index), "name": name, "memory_total_mib": int(total),
            "memory_used_mib": int(used), "utilization_gpu_percent": int(util),
        })
    return {"gpus": rows}


def cgroup_snapshot() -> dict:
    row = next(x for x in Path("/proc/self/cgroup").read_text().splitlines() if x.startswith("0::"))
    cg = Path("/sys/fs/cgroup") / row.split("::", 1)[1].lstrip("/")
    return {
        "path": str(cg),
        "memory_max": (cg / "memory.max").read_text().strip(),
        "memory_swap_max": (cg / "memory.swap.max").read_text().strip(),
        "pids_max": (cg / "pids.max").read_text().strip(),
    }


def memory_analysis_dict(analysis) -> dict:
    if analysis is None:
        return {}
    out = {}
    for name in (
        "argument_size_in_bytes", "output_size_in_bytes", "alias_size_in_bytes",
        "temp_size_in_bytes", "host_argument_size_in_bytes", "host_output_size_in_bytes",
        "host_alias_size_in_bytes", "host_temp_size_in_bytes",
    ):
        if hasattr(analysis, name):
            value = getattr(analysis, name)
            try:
                value = int(value)
            except Exception:
                value = str(value)
            out[name] = value
    out["repr"] = str(analysis)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority", type=Path, required=True)
    ap.add_argument("--openpi-child-root", type=Path, required=True)
    ap.add_argument("--params-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()

    authority = json.loads(args.authority.read_text())
    if authority.get("status") != "AUTHORIZED_PI05_SOURCE_NATIVE_09_COMPILE_ONLY_MEMORY_PROBE_V5B":
        raise RuntimeError("compile-probe authority inactive")
    if authority.get("object_id") != OBJECT_ID:
        raise RuntimeError("object drift")
    if args.receipt.exists():
        raise RuntimeError(f"probe receipt already exists: {args.receipt}")

    required_env = authority["required_launch_environment"]
    for key, expected in required_env.items():
        if os.environ.get(key) != str(expected):
            raise RuntimeError(f"environment drift {key}: {os.environ.get(key)!r}/{expected!r}")

    child_root = args.openpi_child_root.resolve()
    params_root = args.params_root.resolve()
    child_commit = subprocess.check_output(["git", "-C", str(child_root), "rev-parse", "HEAD"], text=True).strip()
    if child_commit != EXPECTED_CHILD_COMMIT:
        raise RuntimeError(f"child commit drift: {child_commit}")
    train_script = child_root / "scripts/b1k/train_b1k.py"
    if sha256_file(train_script) != EXPECTED_TRAIN_SCRIPT_SHA256:
        raise RuntimeError("source train script SHA drift")

    before = gpu_snapshot()
    if len(before["gpus"]) != 1 or before["gpus"][0]["memory_used_mib"] > MAX_GPU_USED_BEFORE_MIB:
        raise RuntimeError(f"GPU not idle enough for compile probe: {before}")

    receipt = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-source-train-compile-probe-v5b-result-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_SOURCE_NATIVE_09_COMPILE_PROBE_STARTED",
        "authority_sha256": sha256_file(args.authority),
        "openpi_child_commit": child_commit,
        "source_train_script_sha256": EXPECTED_TRAIN_SCRIPT_SHA256,
        "xla_python_client_mem_fraction": os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"],
        "gpu_before": before,
        "cgroup": cgroup_snapshot(),
        "batch_accessed": False,
        "train_state_initialized": False,
        "source_train_step_lowered": False,
        "source_train_step_compiled": False,
        "source_train_step_executed": False,
        "optimizer_update_executed": False,
        "parameter_update_executed": False,
        "loss_value_read": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_training_started": False,
        "scientific_authority": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    try:
        os.chdir(child_root)
        sys.path.insert(0, str(child_root))
        sys.path.insert(0, str(child_root / "src"))

        import jax
        import openpi.shared.array_typing as at
        import openpi.training.config as config_lib
        import openpi.training.data_loader as data_loader
        import openpi.training.sharding as sharding
        import openpi.training.weight_loaders as weight_loaders
        from scripts.b1k import train_b1k

        devices = jax.devices()
        if len(devices) != 1 or devices[0].platform != "gpu":
            raise RuntimeError(f"expected one JAX GPU: {devices}")

        source_config = config_lib.get_config(CONFIG_NAME)
        config = dataclasses.replace(
            source_config,
            exp_name="shared26-seed42-run1",
            weight_loader=weight_loaders.CheckpointWeightLoader(str(params_root)),
            wandb_enabled=False,
            resume=False,
            overwrite=True,
            num_workers=EXPECTED_NUM_WORKERS,
        )
        episodes = list(config.data.base_config.dataset_kwargs.get("episodes", []))
        if not (
            config.batch_size == EXPECTED_BATCH_SIZE
            and config.seed == EXPECTED_SEED
            and config.model.action_horizon == EXPECTED_ACTION_HORIZON
            and len(episodes) == EXPECTED_EPISODE_COUNT
            and len(set(episodes)) == EXPECTED_EPISODE_COUNT
            and config.num_workers == EXPECTED_NUM_WORKERS
        ):
            raise RuntimeError("frozen config drift")

        mesh = sharding.make_mesh(config.fsdp_devices)
        data_sharding = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec(sharding.DATA_AXIS))
        replicated_sharding = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec())

        loader = data_loader.create_b1k_data_loader(
            config, sharding=data_sharding, shuffle=True, num_batches=1, skip_norm_stats=False
        )
        batch = next(iter(loader))
        receipt["batch_accessed"] = True
        receipt["gpu_after_batch"] = gpu_snapshot()
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

        rng = jax.random.key(config.seed)
        train_rng, init_rng = jax.random.split(rng)
        train_state, train_state_sharding = train_b1k.init_train_state(config, init_rng, mesh, resume=False)
        jax.block_until_ready(train_state)
        receipt["train_state_initialized"] = True
        receipt["gpu_after_state"] = gpu_snapshot()
        try:
            receipt["jax_memory_after_state"] = {k: int(v) if isinstance(v, (int, float)) else v for k, v in devices[0].memory_stats().items()}
        except Exception:
            receipt["jax_memory_after_state"] = None
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

        ptrain_step = jax.jit(
            functools.partial(train_b1k.train_step, config),
            in_shardings=(replicated_sharding, train_state_sharding, data_sharding),
            out_shardings=(train_state_sharding, replicated_sharding),
            donate_argnums=(1,),
        )

        # OpenPI explicitly provides this context for JAX tracing operations. It disables
        # runtime annotation checks only; the numerical source train_step body is unchanged.
        with at.disable_typechecking():
            with sharding.set_mesh(mesh):
                lowered = ptrain_step.lower(train_rng, train_state, batch)
            receipt["source_train_step_lowered"] = True
            args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            compiled = lowered.compile()
        receipt["source_train_step_compiled"] = True
        receipt["compiled_memory_analysis"] = memory_analysis_dict(compiled.memory_analysis())
        receipt["gpu_after_compile"] = gpu_snapshot()
        receipt["status"] = "PI05_SOURCE_NATIVE_09_COMPILE_ONLY_MEMORY_PROBE_PASS"
        receipt["next_gate"] = "ADJUDICATE_COMPILED_MEMORY_PLAN_BEFORE_ANY_EXECUTION"
        receipt["generated_at"] = datetime.now(timezone.utc).isoformat()
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": receipt["status"], "memory": receipt["compiled_memory_analysis"]}, sort_keys=True))
        return 0
    except Exception as exc:
        receipt["status"] = "PI05_SOURCE_NATIVE_09_COMPILE_ONLY_MEMORY_PROBE_HOLD"
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        receipt["gpu_after_error"] = gpu_snapshot()
        receipt["next_gate"] = "COMPILE_PROBE_FAILURE_ADJUDICATION_NO_AUTOMATIC_EXECUTION"
        receipt["generated_at"] = datetime.now(timezone.utc).isoformat()
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": receipt["status"], "error": receipt["error"]}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
