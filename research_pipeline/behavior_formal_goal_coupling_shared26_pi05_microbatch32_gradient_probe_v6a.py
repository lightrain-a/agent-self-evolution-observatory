from __future__ import annotations

import argparse
import dataclasses
import fcntl
import functools
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
EXPECTED_CHILD_COMMIT = "0d05f46ef40a6a0ff0a9b61f078835a71fececde"
EXPECTED_EXP_NAME = "shared26-seed42-run1"
EXPECTED_RESOURCE_ADMISSION_SHA256 = "b7c010d45c21a83db57567a2fe599d59bf2933c327423d1bc4cd2e265e376275"
EXPECTED_MODEL_LOAD_SHA256 = "fda2c02b5d8ec3e9acd491c9d197ba251e78cfc5e7d5486112c9a13bf655da0c"
EXPECTED_DATALOADER_SMOKE_SHA256 = "91e6e138bbe353fbf8774ea894c43cb9f6e7169b1f2dd0356456f62400babbd2"
EXPECTED_TOKENIZER_RESULT_SHA256 = "18ca3f4a11f23d58a0e14eb2ebc13838b5717f959ba788557de19439b74ce0dc"
EXPECTED_BASE_RECEIPT_SHA256 = "8e0f977e0641960ee3e082a19a57f52f994a817bbf981cbb2f7007ea3104a4ed"
EXPECTED_NORM_SHA256 = "5e4159ec0986ad9fc87cc9a265eed9ac67fc9d2d0df233db6130acf0ebff52ce"
EXPECTED_TOKENIZER_SHA256 = "8986bb4f423f07f8c7f70d0dbe3526fb2316056c17bae71b1ea975e77a168fc6"
EXPECTED_BASE_OBJECT_COUNT = 20
EXPECTED_BASE_BYTES = 12_441_721_931
EXPECTED_EPISODE_COUNT = 5200
EXPECTED_GLOBAL_BATCH_SIZE = 64
PROBE_BATCH_SIZE = 32
EXPECTED_ACTION_HORIZON = 32
EXPECTED_FSDP_DEVICES = 1
EXPECTED_SEED = 42
EXPECTED_SOURCE_NUM_WORKERS = 8
RESOURCE_REPAIR_NUM_WORKERS = 0
REQUIRED_THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "TOKENIZERS_PARALLELISM": "false",
    "JAX_PLATFORMS": "cuda",
    "XLA_PYTHON_CLIENT_MEM_FRACTION": "0.9",
    "XLA_PYTHON_CLIENT_PREALLOCATE": "true",
}
MAX_GPU_USED_BEFORE_MIB = 8192
MAX_GPU_UTIL_BEFORE_PERCENT = 25
MAX_SCOPE_MEMORY_BYTES = 72 * 1024**3


def validate_resource_scope() -> dict:
    rows = Path("/proc/self/cgroup").read_text(encoding="utf-8").splitlines()
    unified = [row.split(":", 2)[2] for row in rows if row.startswith("0::")]
    if len(unified) != 1:
        raise RuntimeError(f"microbatch32-v6a requires one cgroup-v2 path, got {unified}")
    cgroup = Path("/sys/fs/cgroup") / unified[0].lstrip("/")
    memory_max_text = (cgroup / "memory.max").read_text(encoding="utf-8").strip()
    swap_max_text = (cgroup / "memory.swap.max").read_text(encoding="utf-8").strip()
    if memory_max_text == "max":
        raise RuntimeError("microbatch32-v6a must run inside a finite MemoryMax scope")
    memory_max = int(memory_max_text)
    if memory_max > MAX_SCOPE_MEMORY_BYTES:
        raise RuntimeError(f"microbatch32-v6a MemoryMax too large: {memory_max} > {MAX_SCOPE_MEMORY_BYTES}")
    if swap_max_text != "0":
        raise RuntimeError(f"microbatch32-v6a requires MemorySwapMax=0, observed {swap_max_text}")
    return {"cgroup": str(cgroup), "memory_max_bytes": memory_max, "memory_swap_max_bytes": 0}


def validate_jax_cuda_preflight() -> dict:
    expected_affinity = set(range(64))
    observed_affinity = set(os.sched_getaffinity(0))
    if observed_affinity != expected_affinity:
        raise RuntimeError(f"microbatch32-v6a CPU affinity drift: {sorted(observed_affinity)}")

    import jax

    devices = jax.devices()
    if len(devices) != 1 or devices[0].platform != "gpu":
        raise RuntimeError(f"microbatch32-v6a expected exactly one CUDA-backed JAX device, got {devices}")
    threads = None
    for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
        if line.startswith("Threads:"):
            threads = int(line.split(":", 1)[1].strip())
            break
    if threads is None:
        raise RuntimeError("microbatch32-v6a could not read current thread count")
    if threads >= 512:
        raise RuntimeError(f"microbatch32-v6a JAX CUDA preflight thread count unsafe: {threads}")
    return {
        "devices": [str(device) for device in devices],
        "platforms": [device.platform for device in devices],
        "cpu_affinity": "0-63",
        "allowed_cpu_count": len(observed_affinity),
        "thread_count_after_cuda_client_init": threads,
    }


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
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_sha(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"{label} missing: {path}")
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(f"{label} SHA drift: {observed}/{expected}")


def atomic_copy_verified(source: Path, destination: Path, expected_sha: str) -> None:
    require_sha(source, expected_sha, "source asset")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        require_sha(destination, expected_sha, "existing destination asset")
        return
    fd, tmp_name = tempfile.mkstemp(prefix=destination.name + ".", suffix=".tmp", dir=destination.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        shutil.copyfile(source, tmp)
        require_sha(tmp, expected_sha, "temporary copied asset")
        os.replace(tmp, destination)
    finally:
        if tmp.exists():
            tmp.unlink()


def gpu_snapshot() -> dict:
    output = subprocess.check_output(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
            "--format=csv,noheader,nounits",
        ],
        text=True,
    ).strip().splitlines()
    rows = []
    for line in output:
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
    keep = {}
    for key, value in stats.items():
        if isinstance(value, (int, float, str, bool)) or value is None:
            keep[str(key)] = value
    return keep


def validate_base_checkpoint(receipt_path: Path, params_root: Path) -> tuple[int, int]:
    require_sha(receipt_path, EXPECTED_BASE_RECEIPT_SHA256, "base checkpoint receipt")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("status") != "PI05_BASE_TRANSPORT_REPAIR1_COMPLETE":
        raise RuntimeError("base checkpoint receipt is not COMPLETE")
    if receipt.get("verified_object_count") != EXPECTED_BASE_OBJECT_COUNT or receipt.get("verified_bytes") != EXPECTED_BASE_BYTES:
        raise RuntimeError("base checkpoint receipt count/bytes drift")
    count = 0
    total = 0
    for row in receipt["objects"]:
        path = params_root / row["relative_path"]
        if not path.is_file() or path.stat().st_size != int(row["size"]):
            raise RuntimeError(f"base checkpoint object missing/size drift: {row['relative_path']}")
        if sha256_file(path) != row["local_sha256"]:
            raise RuntimeError(f"base checkpoint object SHA drift: {row['relative_path']}")
        count += 1
        total += int(row["size"])
    if count != EXPECTED_BASE_OBJECT_COUNT or total != EXPECTED_BASE_BYTES:
        raise RuntimeError("full base checkpoint rehash drift")
    return count, total


def write_receipt(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--failure-adjudication", type=Path, required=True)
    parser.add_argument("--adapter-qualification", type=Path, required=True)
    parser.add_argument("--resource-admission", type=Path, required=True)
    parser.add_argument("--model-load-result", type=Path, required=True)
    parser.add_argument("--dataloader-smoke", type=Path, required=True)
    parser.add_argument("--tokenizer-result", type=Path, required=True)
    parser.add_argument("--base-receipt", type=Path, required=True)
    parser.add_argument("--openpi-child-root", type=Path, required=True)
    parser.add_argument("--params-root", type=Path, required=True)
    parser.add_argument("--tokenizer-source", type=Path, required=True)
    parser.add_argument("--openpi-data-home", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    authority_path = args.authority.resolve()
    failure_adjudication_path = args.failure_adjudication.resolve()
    adapter_qualification_path = args.adapter_qualification.resolve()
    resource_path = args.resource_admission.resolve()
    model_load_path = args.model_load_result.resolve()
    dataloader_path = args.dataloader_smoke.resolve()
    tokenizer_result_path = args.tokenizer_result.resolve()
    base_receipt_path = args.base_receipt.resolve()
    child_root = args.openpi_child_root.resolve()
    params_root = args.params_root.resolve()
    tokenizer_source = args.tokenizer_source.resolve()
    openpi_data_home = args.openpi_data_home.resolve()
    receipt_path = args.receipt.resolve()
    lock_path = Path("/data/wyt/.formal-goal-pi05-microbatch32-gradient-probe-v6a.lock")

    if receipt_path.exists():
        raise RuntimeError(f"microbatch32-v6a dry-step receipt already exists; exactly-once child attempt cannot be relaunched: {receipt_path}")

    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    if authority.get("status") != "AUTHORIZED_PI05_MICROBATCH32_NO_UPDATE_GRADIENT_PROBE_V6A":
        raise RuntimeError("microbatch32-v6a dry-step authority is not active")
    if authority.get("object_id") != OBJECT_ID:
        raise RuntimeError("microbatch32-v6a authority object drift")
    failure_sha = sha256_file(failure_adjudication_path)
    if authority.get("parent_failure_adjudication_sha256") != failure_sha:
        raise RuntimeError("microbatch32-v6a authority does not bind the supplied failure adjudication")
    adapter_qualification_sha = sha256_file(adapter_qualification_path)
    if authority.get("resource_adapter_qualification_sha256") != adapter_qualification_sha:
        raise RuntimeError("microbatch32-v6a authority does not bind the supplied adapter qualification")
    runner_binding = authority.get("runner") or {}
    if Path(runner_binding.get("path", "")).name != Path(__file__).name or runner_binding.get("sha256") != sha256_file(Path(__file__).resolve()):
        raise RuntimeError("microbatch32-v6a runner content-address binding drift")
    adapter = authority.get("resource_only_adapter") or {}
    if adapter.get("source_num_workers") != EXPECTED_SOURCE_NUM_WORKERS or adapter.get("num_workers") != RESOURCE_REPAIR_NUM_WORKERS:
        raise RuntimeError("microbatch32-v6a authority DataLoader adapter drift")
    require_sha(resource_path, EXPECTED_RESOURCE_ADMISSION_SHA256, "resource admission")
    require_sha(model_load_path, EXPECTED_MODEL_LOAD_SHA256, "model-load result")
    require_sha(dataloader_path, EXPECTED_DATALOADER_SMOKE_SHA256, "normalized dataloader smoke")
    require_sha(tokenizer_result_path, EXPECTED_TOKENIZER_RESULT_SHA256, "tokenizer result")
    require_sha(tokenizer_source, EXPECTED_TOKENIZER_SHA256, "tokenizer source")

    child_commit = subprocess.check_output(["git", "-C", str(child_root), "rev-parse", "HEAD"], text=True).strip()
    if child_commit != EXPECTED_CHILD_COMMIT:
        raise RuntimeError(f"OpenPI child commit drift: {child_commit}")

    if os.environ.get("HF_HUB_OFFLINE") != "1" or os.environ.get("TRANSFORMERS_OFFLINE") != "1":
        raise RuntimeError("dry-step must run with HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1")
    for key, expected in REQUIRED_THREAD_ENV.items():
        if os.environ.get(key) != expected:
            raise RuntimeError(f"microbatch32-v6a requires {key}={expected}, observed {os.environ.get(key)!r}")
    env_data_home = Path(os.environ.get("OPENPI_DATA_HOME", "")).resolve()
    if env_data_home != openpi_data_home:
        raise RuntimeError(f"OPENPI_DATA_HOME mismatch: {env_data_home}/{openpi_data_home}")

    resource_scope = validate_resource_scope()
    jax_cuda_preflight = validate_jax_cuda_preflight()
    require_sha(base_receipt_path, EXPECTED_BASE_RECEIPT_SHA256, "base checkpoint receipt")
    base_object_count, base_bytes = EXPECTED_BASE_OBJECT_COUNT, EXPECTED_BASE_BYTES
    before_gpu = gpu_snapshot()
    if len(before_gpu["gpus"]) != 1:
        raise RuntimeError(f"dry-step host must expose exactly one GPU, got {len(before_gpu['gpus'])}")
    gpu0 = before_gpu["gpus"][0]
    if "A100" not in gpu0["name"] or gpu0["memory_total_mib"] < 80_000:
        raise RuntimeError(f"unexpected dry-step GPU: {gpu0}")
    if gpu0["memory_used_mib"] > MAX_GPU_USED_BEFORE_MIB or gpu0["utilization_gpu_percent"] > MAX_GPU_UTIL_BEFORE_PERCENT:
        raise RuntimeError(f"dry-step GPU not idle enough; no attempt consumed: {gpu0}")

    tokenizer_cache = openpi_data_home / "big_vision" / "paligemma_tokenizer.model"
    atomic_copy_verified(tokenizer_source, tokenizer_cache, EXPECTED_TOKENIZER_SHA256)

    checkpoint_dir = child_root / "outputs" / "checkpoints" / CONFIG_NAME / EXPECTED_EXP_NAME
    if checkpoint_dir.exists():
        raise RuntimeError(f"formal training checkpoint directory already exists: {checkpoint_dir}")

    initial = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-dry-step-microbatch32-v6a-result-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_MICROBATCH32_NO_UPDATE_GRADIENT_PROBE_V6A_STARTED",
        "attempt_count_under_microbatch32_v6a_authority": 1,
        "attempt_is_exactly_once": True,
        "prior_resource_attempts_consumed": True,
        "failure_adjudication_path": str(failure_adjudication_path),
        "failure_adjudication_sha256": failure_sha,
        "adapter_qualification_path": str(adapter_qualification_path),
        "adapter_qualification_sha256": adapter_qualification_sha,
        "authority_path": str(authority_path),
        "authority_sha256": sha256_file(authority_path),
        "resource_admission_sha256": EXPECTED_RESOURCE_ADMISSION_SHA256,
        "model_load_result_sha256": EXPECTED_MODEL_LOAD_SHA256,
        "dataloader_smoke_sha256": EXPECTED_DATALOADER_SMOKE_SHA256,
        "tokenizer_result_sha256": EXPECTED_TOKENIZER_RESULT_SHA256,
        "base_receipt_sha256": EXPECTED_BASE_RECEIPT_SHA256,
        "openpi_child_commit": child_commit,
        "base_object_count_rehashed": base_object_count,
        "base_bytes_rehashed": base_bytes,
        "tokenizer_cache": str(tokenizer_cache),
        "tokenizer_sha256": EXPECTED_TOKENIZER_SHA256,
        "gpu_before": before_gpu,
        "resource_scope": resource_scope,
        "jax_cuda_preflight": jax_cuda_preflight,
        "source_num_workers": EXPECTED_SOURCE_NUM_WORKERS,
        "resource_repair_num_workers": RESOURCE_REPAIR_NUM_WORKERS,
        "scientific_global_batch_size": EXPECTED_GLOBAL_BATCH_SIZE,
        "resource_probe_microbatch_size": PROBE_BATCH_SIZE,
        "microbatch_is_scientific_batch_change": False,
        "thread_environment": dict(REQUIRED_THREAD_ENV),
        "dry_gradient_execution_started": False,
        "dry_gradient_execution_completed": False,
        "loss_value_retained_or_reported": False,
        "optimizer_update": False,
        "parameter_update": False,
        "checkpoint_written": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_training_started": False,
        "formal_training_authorized": False,
        "scientific_authority": False,
    }

    with exclusive_lock(lock_path):
        # The STARTED receipt is written before any gradient computation. A hard crash/OOM therefore consumes
        # the exactly-once dry-step attempt and must be adjudicated rather than silently relaunched.
        write_receipt(receipt_path, initial)
        status = "PI05_MICROBATCH32_NO_UPDATE_GRADIENT_PROBE_V6A_HOLD"
        error = None
        train_state_ready = False
        batch_ready = False
        dry_gradient_execution_started = False
        dry_gradient_execution_completed = False
        gradient_leaf_count = None
        gradient_element_count = None
        gpu_after_state = None
        gpu_after_gradient = None
        jax_memory_after_state = None
        jax_memory_after_gradient = None

        try:
            os.chdir(child_root)
            sys.path.insert(0, str(child_root))
            sys.path.insert(0, str(child_root / "src"))

            import flax.nnx as nnx
            import jax
            import jax.numpy as jnp
            import openpi.shared.array_typing as at
            import openpi.training.config as config_lib
            import openpi.training.data_loader as data_loader
            import openpi.training.sharding as sharding
            import openpi.training.weight_loaders as weight_loaders
            from scripts.b1k import train_b1k

            devices = jax.devices()
            if len(devices) != 1 or devices[0].platform != "gpu":
                raise RuntimeError(f"expected one JAX GPU device, got {devices}")
            device = devices[0]

            source_config = config_lib.get_config(CONFIG_NAME)
            if source_config.num_workers != EXPECTED_SOURCE_NUM_WORKERS:
                raise RuntimeError(f"source num_workers drift: {source_config.num_workers}/{EXPECTED_SOURCE_NUM_WORKERS}")
            if source_config.batch_size != EXPECTED_GLOBAL_BATCH_SIZE:
                raise RuntimeError(f"source global batch drift: {source_config.batch_size}/{EXPECTED_GLOBAL_BATCH_SIZE}")
            config = dataclasses.replace(
                source_config,
                exp_name=EXPECTED_EXP_NAME,
                weight_loader=weight_loaders.CheckpointWeightLoader(str(params_root)),
                wandb_enabled=False,
                resume=False,
                overwrite=True,
                num_workers=RESOURCE_REPAIR_NUM_WORKERS,
                batch_size=PROBE_BATCH_SIZE,
            )
            if config.num_workers != RESOURCE_REPAIR_NUM_WORKERS:
                raise RuntimeError("resource-only num_workers adapter did not apply")
            episodes = list(config.data.base_config.dataset_kwargs.get("episodes", []))
            if (
                config.seed != EXPECTED_SEED
                or config.batch_size != PROBE_BATCH_SIZE
                or config.model.action_horizon != EXPECTED_ACTION_HORIZON
                or config.fsdp_devices != EXPECTED_FSDP_DEVICES
                or config.num_train_steps != 50_000
                or len(episodes) != EXPECTED_EPISODE_COUNT
                or len(set(episodes)) != EXPECTED_EPISODE_COUNT
            ):
                raise RuntimeError("frozen shared26 training configuration drift")

            mesh = sharding.make_mesh(config.fsdp_devices)
            data_sharding = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec(sharding.DATA_AXIS))
            replicated_sharding = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec())

            source_loader = data_loader.create_b1k_data_loader(
                config,
                sharding=data_sharding,
                shuffle=True,
                num_batches=1,
                skip_norm_stats=False,
            )
            batch = next(iter(source_loader))
            batch_ready = True

            rng = jax.random.key(config.seed)
            train_rng, init_rng = jax.random.split(rng)
            train_state, train_state_sharding = train_b1k.init_train_state(config, init_rng, mesh, resume=False)
            jax.block_until_ready(train_state)
            if int(jax.device_get(train_state.step)) != 0:
                raise RuntimeError("dry-step train state did not initialize at step 0")
            train_state_ready = True
            gpu_after_state = gpu_snapshot()
            jax_memory_after_state = jax_memory_snapshot(device)

            @at.typecheck
            def dry_gradient_only(
                config_arg,
                rng_arg: at.KeyArrayLike,
                state,
                batch_arg,
            ):
                model = nnx.merge(state.model_def, state.params)
                model.train()

                @at.typecheck
                def loss_fn(model_arg, rng_inner: at.KeyArrayLike, observation, actions):
                    chunked_loss = model_arg.compute_loss(rng_inner, observation, actions, train=True)
                    return jnp.mean(chunked_loss)

                folded_rng = jax.random.fold_in(rng_arg, state.step)
                observation, actions = batch_arg
                diff_state = nnx.DiffState(0, config_arg.trainable_filter)
                _discarded_loss, grads = nnx.value_and_grad(loss_fn, argnums=diff_state)(
                    model, folded_rng, observation, actions
                )
                del _discarded_loss
                return grads

            pdry = jax.jit(
                functools.partial(dry_gradient_only, config),
                in_shardings=(replicated_sharding, train_state_sharding, data_sharding),
                out_shardings=None,
                donate_argnums=(1,),
            )

            dry_gradient_execution_started = True
            started_payload = dict(initial)
            started_payload.update(
                {
                    "status": "PI05_MICROBATCH32_NO_UPDATE_GRADIENT_PROBE_V6A_GRADIENT_STARTED",
                    "batch_ready": True,
                    "train_state_ready": True,
                    "gpu_after_state": gpu_after_state,
                    "jax_memory_after_state": jax_memory_after_state,
                    "dry_gradient_execution_started": True,
                }
            )
            write_receipt(receipt_path, started_payload)

            grads = pdry(train_rng, train_state, batch)
            jax.tree.map(lambda x: x.block_until_ready(), grads)
            dry_gradient_execution_completed = True
            leaves = jax.tree.leaves(grads)
            gradient_leaf_count = len(leaves)
            gradient_element_count = int(sum(np.prod(tuple(x.shape), dtype=np.int64) for x in leaves))
            gpu_after_gradient = gpu_snapshot()
            jax_memory_after_gradient = jax_memory_snapshot(device)
            status = "PI05_MICROBATCH32_NO_UPDATE_GRADIENT_PROBE_V6A_PASS"

            # Do not inspect numerical gradient values. No optimizer/update function is called anywhere in this runner.
            del grads
            del batch
            del source_loader
            del train_state
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            try:
                gpu_after_gradient = gpu_snapshot()
            except Exception:
                pass
        finally:
            final = dict(initial)
            final.update(
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "status": status,
                    "batch_ready": batch_ready,
                    "train_state_ready": train_state_ready,
                    "dry_gradient_execution_started": dry_gradient_execution_started,
                    "dry_gradient_execution_completed": dry_gradient_execution_completed,
                    "gradient_leaf_count": gradient_leaf_count,
                    "gradient_element_count": gradient_element_count,
                    "gradient_numerical_values_read": False,
                    "loss_value_retained_or_reported": False,
                    "gpu_after_state": gpu_after_state,
                    "gpu_after_gradient_or_error": gpu_after_gradient,
                    "jax_memory_after_state": jax_memory_after_state,
                    "jax_memory_after_gradient": jax_memory_after_gradient,
                    "error": error,
                    "dataset_batch_accessed": batch_ready,
                    "tokenizer_executed": batch_ready,
                    "model_forward_executed": dry_gradient_execution_completed,
                    "backward_gradient_executed": dry_gradient_execution_completed,
                    "optimizer_update": False,
                    "parameter_update": False,
                    "checkpoint_written": False,
                    "policy_rollouts_started": False,
                    "policy_outcomes_read": False,
                    "scientific_training_started": False,
                    "formal_training_authorized": False,
                    "next_gate": (
                        "QUALIFY_RNG_PRESERVING_GLOBAL64_AS_32X2_GRADIENT_ACCUMULATION"
                        if status == "PI05_MICROBATCH32_NO_UPDATE_GRADIENT_PROBE_V6A_PASS"
                        else "MICROBATCH32_V6A_FAILURE_ADJUDICATION_OR_FALLBACK_TO_MICROBATCH16"
                    ),
                }
            )
            write_receipt(receipt_path, final)

        print(
            json.dumps(
                {
                    "status": status,
                    "batch_ready": batch_ready,
                    "train_state_ready": train_state_ready,
                    "dry_gradient_execution_started": dry_gradient_execution_started,
                    "dry_gradient_execution_completed": dry_gradient_execution_completed,
                    "gradient_leaf_count": gradient_leaf_count,
                    "gradient_element_count": gradient_element_count,
                    "error": error,
                },
                sort_keys=True,
            )
        )
        return 0 if status == "PI05_MICROBATCH32_NO_UPDATE_GRADIENT_PROBE_V6A_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
