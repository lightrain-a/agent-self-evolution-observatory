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

import numpy as np

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CHILD_ID = "SUCC-C-BEHAVIOR2026-SHARED26-PI05-SINGLE-GPU-ACCUMULATION"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
EXP_NAME = "shared26-seed42-run1"
PORTABLE_PARENT_COMMIT = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
PORTABLE_CONFIG_SHA = "4a50bb5f3579ed0035e19d2fc2a5d33821c0cc115c6e8c441eac497e74b02e99"
PORTABLE_DIRECT_RESULT_SHA = "5f27f14cfce284f1a75acefafbf9c404556f527b5037007ee8f119df3ddc90df"
PREREG_SHA = "0d0a88b20f15d3a0fa2e8721da865bd5488cc39c43523a518608063c8a51a8d7"
HOST_EXIT_ADJ_SHA = "7fce8b714c2b46c1561930c34f0c2e5b67987ddaa63e4868f42f752e076afad8"
DATA_ORDER_SHA = "a218a76893b8e97dc849eb2d7dd63cf3a7516acbc0d0ded3822e20a0a211446d"
CONSUMED_ATTEMPT_SHA = "9e7602d8e1783818881ab24d9dc3cb0b385db43eea56834d21c805e229349193"
INTERRUPTION_ADJUDICATION_SHA = "de5d5eb61350bf2112990244aa5450db07406a113938b9f729efd3a75b202542"
SOURCE_BATCH = 64
MICRO = 8
K = 8
EFFECTIVE = 64
ACTION_HORIZON = 32
FSDP = 1
SEED = 42
EPISODES = 5200
TRAINABLE_ELEMENTS = 3_353_433_872
GRAD_BYTES = 13_413_735_488
MAX_GPU_USED = 1024
MAX_GPU_UTIL = 25
MAX_HOST_MEM = 20 * 1024**3
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
        index, name, total, used, util = [part.strip() for part in line.split(",", 4)]
        rows.append(
            {
                "index": int(index),
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
    return {
        str(k): v
        for k, v in stats.items()
        if isinstance(v, (int, float, str, bool)) or v is None
    }


def resource_scope() -> dict:
    rows = Path("/proc/self/cgroup").read_text(encoding="utf-8").splitlines()
    unified = [row.split(":", 2)[2] for row in rows if row.startswith("0::")]
    if len(unified) != 1:
        raise RuntimeError(f"unexpected cgroup paths: {unified}")
    cgroup = Path("/sys/fs/cgroup") / unified[0].lstrip("/")
    memory_max_text = (cgroup / "memory.max").read_text(encoding="utf-8").strip()
    swap_max_text = (cgroup / "memory.swap.max").read_text(encoding="utf-8").strip()
    if memory_max_text == "max" or int(memory_max_text) > MAX_HOST_MEM:
        raise RuntimeError(f"synthetic gate requires MemoryMax<=20G, got {memory_max_text}")
    if swap_max_text != "0":
        raise RuntimeError(f"synthetic gate requires MemorySwapMax=0, got {swap_max_text}")
    affinity = set(os.sched_getaffinity(0))
    if affinity != set(range(64)):
        raise RuntimeError(f"CPU affinity drift: {sorted(affinity)}")
    return {
        "cgroup": str(cgroup),
        "memory_max_bytes": int(memory_max_text),
        "memory_swap_max_bytes": 0,
        "cpu_affinity": "0-63",
    }


def validate_portable_child(root: Path) -> dict:
    parent = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if parent != PORTABLE_PARENT_COMMIT:
        raise RuntimeError(f"portable parent drift: {parent}")
    config_path = root / "src/openpi/training/config.py"
    if sha(config_path) != PORTABLE_CONFIG_SHA:
        raise RuntimeError("portable config SHA drift")
    changed = []
    for line in subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True).splitlines():
        if line.strip():
            changed.append(line[3:])
    if changed != ["src/openpi/training/config.py"]:
        raise RuntimeError(f"portable changed-path drift: {changed}")
    return {"parent_commit": parent, "config_sha256": PORTABLE_CONFIG_SHA, "changed_paths": changed}


def main() -> int:
    ap = argparse.ArgumentParser()
    for name in [
        "authority",
        "preregistration",
        "host_exit_adjudication",
        "data_order_qualification",
        "portable_direct_device_result",
        "consumed_attempt_result",
        "interruption_adjudication",
        "openpi_child_root",
        "params_root",
        "receipt",
    ]:
        ap.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    args = ap.parse_args()
    paths = {name: getattr(args, name).resolve() for name in vars(args)}
    receipt_path = paths["receipt"]
    if receipt_path.exists():
        raise RuntimeError(f"exactly-once synthetic 8x8 receipt exists: {receipt_path}")

    authority = json.loads(paths["authority"].read_text(encoding="utf-8"))
    if authority.get("status") != "AUTHORIZED_PI05_SYNTHETIC_FUSED_ACCUM8X8_DIRECT_DEVICE_REPAIR1_HOST67":
        raise RuntimeError("repair1 authority is not active")
    if authority.get("object_id") != OBJECT_ID or authority.get("child_id") != CHILD_ID:
        raise RuntimeError("authority object drift")
    if authority.get("runner_sha256") != sha(Path(__file__).resolve()):
        raise RuntimeError("runner SHA binding drift")

    require(paths["consumed_attempt_result"], CONSUMED_ATTEMPT_SHA, "consumed synthetic attempt1 result")
    require(paths["interruption_adjudication"], INTERRUPTION_ADJUDICATION_SHA, "synthetic attempt1 interruption adjudication")
    consumed = json.loads(paths["consumed_attempt_result"].read_text(encoding="utf-8"))
    adjudication = json.loads(paths["interruption_adjudication"].read_text(encoding="utf-8"))
    if consumed.get("status") != "PI05_SYNTHETIC_FUSED_ACCUM8X8_DIRECT_DEVICE_STARTED":
        raise RuntimeError("consumed attempt1 last durable status drift")
    if consumed.get("micro_gradients_completed") != 0 or consumed.get("optimizer_update") is not False:
        raise RuntimeError("consumed attempt1 scientific boundary drift")
    if adjudication.get("status") != "PI05_SYNTHETIC_FUSED_ACCUM8X8_ATTEMPT1_PRE_GRADIENT_HOST_RESOURCE_INTERRUPTION":
        raise RuntimeError("attempt1 interruption adjudication drift")
    require(paths["preregistration"], PREREG_SHA, "accumulation preregistration")
    require(paths["host_exit_adjudication"], HOST_EXIT_ADJ_SHA, "8x8 host-exit adjudication")
    require(paths["data_order_qualification"], DATA_ORDER_SHA, "8x8 data-order qualification")
    require(paths["portable_direct_device_result"], PORTABLE_DIRECT_RESULT_SHA, "portable direct-device result")
    direct = json.loads(paths["portable_direct_device_result"].read_text(encoding="utf-8"))
    if direct.get("status") != "PI05_PORTABLE_DIRECT_DEVICE_NO_UPDATE_MODEL_LOAD_PASS":
        raise RuntimeError("portable direct-device result not PASS")
    if direct.get("initialized_step") != 0 or not direct.get("train_state_ready") or direct.get("optimizer_update"):
        raise RuntimeError("portable direct-device result invariants failed")
    audit = direct.get("direct_device_loader_audit") or {}
    if not audit.get("all_restored_leaves_are_jax_array") or audit.get("restored_leaf_count") != 51:
        raise RuntimeError("portable direct-device loader audit drift")

    prereg = json.loads(paths["preregistration"].read_text(encoding="utf-8"))
    candidate = prereg["microbatch_resource_ladder"][1]
    if candidate != {"priority": 2, "physical_micro_batch": 8, "accumulation_steps": 8, "effective_batch": 64}:
        raise RuntimeError(f"8x8 ladder drift: {candidate}")
    order = json.loads(paths["data_order_qualification"].read_text(encoding="utf-8"))
    if order.get("status") != "PI05_ACCUM_8X8_DATA_ORDER_QUALIFICATION_PASS" or not order.get("sampler_groups_exactly_equal"):
        raise RuntimeError("8x8 data-order gate not PASS")

    for key, value in REQUIRED_ENV.items():
        if os.environ.get(key) != value:
            raise RuntimeError(f"environment drift {key}={os.environ.get(key)!r}/{value!r}")
    scope = resource_scope()
    portable = validate_portable_child(paths["openpi_child_root"])

    before_gpu = gpu_snapshot()
    if len(before_gpu["gpus"]) != 1:
        raise RuntimeError(f"expected one GPU, got {before_gpu}")
    gpu0 = before_gpu["gpus"][0]
    if "A100" not in gpu0["name"] or gpu0["memory_total_mib"] < 80_000:
        raise RuntimeError(f"unexpected GPU: {gpu0}")
    if gpu0["memory_used_mib"] > MAX_GPU_USED or gpu0["utilization_gpu_percent"] > MAX_GPU_UTIL:
        raise RuntimeError(f"GPU busy; no attempt consumed: {gpu0}")

    initial = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-synthetic-fused-accum8x8-direct-device-result-v1",
        "object_id": OBJECT_ID,
        "child_id": CHILD_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_SYNTHETIC_FUSED_ACCUM8X8_DIRECT_DEVICE_REPAIR1_STARTED",
        "candidate_priority": 2,
        "physical_micro_batch": MICRO,
        "accumulation_steps": K,
        "effective_batch": EFFECTIVE,
        "synthetic_resource_gate": True,
        "dataset_accessed": False,
        "policy_outcomes_read": False,
        "authority_sha256": sha(paths["authority"]),
        "portable_direct_device_result_sha256": PORTABLE_DIRECT_RESULT_SHA,
        "portable_openpi": portable,
        "resource_scope": scope,
        "gpu_before": before_gpu,
        "micro_gradients_completed": 0,
        "accumulated_gradient_complete": False,
        "gradient_numerical_values_read": False,
        "loss_value_retained_or_reported": False,
        "optimizer_update": False,
        "parameter_update": False,
        "checkpoint_written": False,
        "scientific_training_started": False,
        "formal_training_authorized": False,
    }

    lock_path = Path("/data/wyt/.formal-goal-pi05-synthetic-fused-accum8x8-direct-device-repair1.lock")
    with exclusive_lock(lock_path):
        write_receipt(receipt_path, initial)
        status = "PI05_SYNTHETIC_FUSED_ACCUM8X8_DIRECT_DEVICE_REPAIR1_HOLD"
        error = None
        state_ready = False
        done = 0
        accumulator = None
        leaf_count = None
        element_count = None
        byte_count = None
        gpu_after_state = None
        gpu_after_each_micro = []
        jax_after_state = None
        jax_after_each_micro = []
        try:
            root = paths["openpi_child_root"]
            os.chdir(root)
            sys.path.insert(0, str(root))
            sys.path.insert(0, str(root / "src"))

            import flax.nnx as nnx
            import jax
            import jax.numpy as jnp
            import openpi.models.model as model_lib
            import openpi.shared.array_typing as at
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
            if source_config.batch_size != SOURCE_BATCH or source_config.seed != SEED:
                raise RuntimeError("source config batch/seed drift")
            config = dataclasses.replace(
                source_config,
                exp_name=EXP_NAME,
                weight_loader=DirectDeviceCheckpointWeightLoader(str(paths["params_root"])),
                batch_size=MICRO,
                num_workers=0,
                wandb_enabled=False,
                resume=False,
                overwrite=True,
            )
            episodes = list(config.data.base_config.dataset_kwargs.get("episodes", []))
            if (
                config.seed != SEED
                or config.num_train_steps != 50_000
                or config.model.action_horizon != ACTION_HORIZON
                or config.fsdp_devices != FSDP
                or len(episodes) != EPISODES
                or len(set(episodes)) != EPISODES
            ):
                raise RuntimeError("scientific config drift")

            mesh = sharding.make_mesh(config.fsdp_devices)
            rng = jax.random.key(config.seed)
            train_rng, init_rng = jax.random.split(rng)
            state, _state_sharding = train_b1k.init_train_state(config, init_rng, mesh, resume=False)
            jax.block_until_ready(state)
            if int(jax.device_get(state.step)) != 0:
                raise RuntimeError("step-0 state drift")
            state_ready = True
            gpu_after_state = gpu_snapshot()
            jax_after_state = jax_memory_snapshot(device)

            synthetic_batch = (
                config.model.fake_obs(batch_size=MICRO),
                config.model.fake_act(batch_size=MICRO),
            )

            @at.typecheck
            def grad_scaled(config_arg, rng_arg: at.KeyArrayLike, state_arg, batch_arg):
                model = nnx.merge(state_arg.model_def, state_arg.params)
                model.train()

                @at.typecheck
                def loss_fn(model_arg, inner_rng: at.KeyArrayLike, observation, actions):
                    chunked_loss = model_arg.compute_loss(inner_rng, observation, actions, train=True)
                    return jnp.mean(chunked_loss)

                observation, actions = batch_arg
                diff_state = nnx.DiffState(0, config_arg.trainable_filter)
                discarded_loss, grads = nnx.value_and_grad(loss_fn, argnums=diff_state)(
                    model, rng_arg, observation, actions
                )
                del discarded_loss
                return jax.tree.map(lambda x: x / K, grads)

            @at.typecheck
            def grad_accumulate(config_arg, rng_arg: at.KeyArrayLike, state_arg, batch_arg, accum):
                grads = grad_scaled(config_arg, rng_arg, state_arg, batch_arg)
                return jax.tree.map(lambda a, b: a + b, accum, grads)

            pfirst = jax.jit(functools.partial(grad_scaled, config))
            paccum = jax.jit(functools.partial(grad_accumulate, config), donate_argnums=(3,))

            for index in range(K):
                progress = dict(initial)
                progress.update(
                    {
                        "status": "PI05_SYNTHETIC_FUSED_ACCUM8X8_DIRECT_DEVICE_REPAIR1_MICRO_GRADIENT_STARTED",
                        "train_state_ready": True,
                        "micro_gradient_index_started": index,
                        "micro_gradients_completed": done,
                        "gpu_after_state": gpu_after_state,
                        "jax_memory_after_state": jax_after_state,
                        "gpu_after_each_completed_micro": gpu_after_each_micro,
                        "jax_memory_after_each_completed_micro": jax_after_each_micro,
                    }
                )
                write_receipt(receipt_path, progress)
                micro_rng = jax.random.fold_in(train_rng, index)
                if index == 0:
                    accumulator = pfirst(micro_rng, state, synthetic_batch)
                else:
                    accumulator = paccum(micro_rng, state, synthetic_batch, accumulator)
                jax.tree.map(lambda x: x.block_until_ready(), accumulator)
                done += 1
                gpu_after_each_micro.append(gpu_snapshot())
                jax_after_each_micro.append(jax_memory_snapshot(device))

            leaves = jax.tree.leaves(accumulator)
            leaf_count = len(leaves)
            element_count = int(sum(np.prod(tuple(x.shape), dtype=np.int64) for x in leaves))
            byte_count = int(
                sum(np.prod(tuple(x.shape), dtype=np.int64) * np.dtype(x.dtype).itemsize for x in leaves)
            )
            if element_count != TRAINABLE_ELEMENTS or byte_count != GRAD_BYTES:
                raise RuntimeError(
                    f"accumulator structure drift elements={element_count}/{TRAINABLE_ELEMENTS} bytes={byte_count}/{GRAD_BYTES}"
                )
            status = "PI05_SYNTHETIC_FUSED_ACCUM8X8_DIRECT_DEVICE_REPAIR1_PASS"
            del accumulator, synthetic_batch, state
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        finally:
            final = dict(initial)
            final.update(
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "status": status,
                    "train_state_ready": state_ready,
                    "micro_gradients_completed": done,
                    "accumulated_gradient_complete": status.endswith("PASS"),
                    "accumulator_leaf_count": leaf_count,
                    "accumulator_element_count": element_count,
                    "accumulator_bytes": byte_count,
                    "gpu_after_state": gpu_after_state,
                    "jax_memory_after_state": jax_after_state,
                    "gpu_after_each_completed_micro": gpu_after_each_micro,
                    "jax_memory_after_each_completed_micro": jax_after_each_micro,
                    "error": error,
                    "dataset_accessed": False,
                    "gradient_numerical_values_read": False,
                    "loss_value_retained_or_reported": False,
                    "optimizer_update": False,
                    "parameter_update": False,
                    "checkpoint_written": False,
                    "scientific_training_started": False,
                    "formal_training_authorized": False,
                    "next_gate": (
                        "REAL_DATA_STREAMING_ACCUM8X8_IMPLEMENTATION_AUTHORITY"
                        if status.endswith("PASS")
                        else "ACCUM8X8_SYNTHETIC_RESOURCE_FAILURE_ADJUDICATION"
                    ),
                }
            )
            write_receipt(receipt_path, final)

        print(
            json.dumps(
                {
                    "status": status,
                    "micro_gradients_completed": done,
                    "accumulator_element_count": element_count,
                    "error": error,
                },
                sort_keys=True,
            )
        )
        return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
