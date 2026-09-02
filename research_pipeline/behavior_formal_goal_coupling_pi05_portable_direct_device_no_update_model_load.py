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
CONFIG_NAME = "pi05_b1k_shared26_frozen"
EXPECTED_PARENT_COMMIT = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
EXPECTED_FINAL_CONFIG_SHA256 = "4a50bb5f3579ed0035e19d2fc2a5d33821c0cc115c6e8c441eac497e74b02e99"
EXPECTED_BASE_RECEIPT_SHA256 = "8e0f977e0641960ee3e082a19a57f52f994a817bbf981cbb2f7007ea3104a4ed"
EXPECTED_BASE_OBJECT_COUNT = 20
EXPECTED_BASE_BYTES = 12_441_721_931
EXPECTED_EXP_NAME = "shared26-seed42-run1"


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


def host_memory_snapshot() -> dict:
    values = {}
    for line in Path('/proc/meminfo').read_text(encoding='utf-8').splitlines():
        if ':' not in line:
            continue
        key, rest = line.split(':', 1)
        if key in {'MemTotal', 'MemAvailable', 'MemFree', 'SwapTotal', 'SwapFree'}:
            values[key + '_kib'] = int(rest.strip().split()[0])
    user_slice = Path(f'/sys/fs/cgroup/user.slice/user-{os.getuid()}.slice/memory.current')
    values['user_slice_memory_current_bytes'] = int(user_slice.read_text().strip()) if user_slice.exists() else None
    values['process_rss_kib'] = int(Path('/proc/self/status').read_text().split('VmRSS:',1)[1].splitlines()[0].strip().split()[0])
    return values


def qualification_scope_snapshot() -> dict:
    rows = Path('/proc/self/cgroup').read_text(encoding='utf-8').splitlines()
    unified = [row.split(':', 2)[2] for row in rows if row.startswith('0::')]
    if len(unified) != 1:
        raise RuntimeError(f'direct-device qualification requires one cgroup-v2 path, got {unified}')
    cgroup = Path('/sys/fs/cgroup') / unified[0].lstrip('/')
    memory_max = (cgroup / 'memory.max').read_text(encoding='utf-8').strip()
    swap_max = (cgroup / 'memory.swap.max').read_text(encoding='utf-8').strip()
    if memory_max == 'max' or int(memory_max) > 20 * 1024**3:
        raise RuntimeError(f'direct-device qualification MemoryMax drift: {memory_max}')
    if swap_max != '0':
        raise RuntimeError(f'direct-device qualification requires MemorySwapMax=0, got {swap_max}')
    affinity = set(os.sched_getaffinity(0))
    if affinity != set(range(64)):
        raise RuntimeError(f'direct-device qualification CPU affinity drift: {sorted(affinity)}')
    return {'cgroup': str(cgroup), 'memory_max_bytes': int(memory_max), 'memory_swap_max_bytes': 0, 'cpu_affinity': '0-63'}


def gpu_snapshot() -> dict:
    command = [
        "nvidia-smi",
        "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
        "--format=csv,noheader,nounits",
    ]
    output = subprocess.check_output(command, text=True).strip().splitlines()
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


def validate_local_checkpoint(receipt_path: Path, params_root: Path) -> tuple[str, int, int]:
    if sha256_file(receipt_path) != EXPECTED_BASE_RECEIPT_SHA256:
        raise RuntimeError("base asset receipt SHA drift")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("status") != "PI05_BASE_TRANSPORT_REPAIR1_COMPLETE":
        raise RuntimeError("base asset receipt is not COMPLETE")
    if receipt.get("verified_object_count") != EXPECTED_BASE_OBJECT_COUNT or receipt.get("verified_bytes") != EXPECTED_BASE_BYTES:
        raise RuntimeError("base asset receipt count/byte drift")
    total = 0
    count = 0
    for row in receipt["objects"]:
        path = params_root / row["relative_path"]
        if not path.is_file() or path.stat().st_size != int(row["size"]):
            raise RuntimeError(f"checkpoint object missing/size drift: {row['relative_path']}")
        if sha256_file(path) != row["local_sha256"]:
            raise RuntimeError(f"checkpoint object SHA drift: {row['relative_path']}")
        count += 1
        total += int(row["size"])
    if count != EXPECTED_BASE_OBJECT_COUNT or total != EXPECTED_BASE_BYTES:
        raise RuntimeError("local checkpoint full rehash count/byte drift")
    return sha256_file(receipt_path), count, total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--openpi-child-root", type=Path, required=True)
    parser.add_argument("--params-root", type=Path, required=True)
    parser.add_argument("--base-receipt", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--host-exit-adjudication", type=Path, required=True)
    parser.add_argument("--static-qualification", type=Path, required=True)
    parser.add_argument("--portable-child-equivalence", type=Path, required=True)
    parser.add_argument("--portable-env-qualification", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    child_root = args.openpi_child_root.resolve()
    params_root = args.params_root.resolve()
    base_receipt = args.base_receipt.resolve()
    authority_path = args.authority.resolve()
    host_exit_adjudication = args.host_exit_adjudication.resolve()
    static_qualification = args.static_qualification.resolve()
    portable_child_equivalence = args.portable_child_equivalence.resolve()
    portable_env_qualification = args.portable_env_qualification.resolve()
    receipt_path = args.receipt.resolve()
    lock_path = Path("/data/wyt/.formal-goal-pi05-portable-direct-device-no-update-model-load.lock")
    if receipt_path.exists():
        raise RuntimeError(f"direct-device model-load receipt already exists; exactly-once qualification cannot be replayed: {receipt_path}")

    with exclusive_lock(lock_path):
        authority = json.loads(authority_path.read_text(encoding="utf-8"))
        if authority.get("status") != "AUTHORIZED_PI05_PORTABLE_DIRECT_DEVICE_NO_UPDATE_MODEL_LOAD_QUALIFICATION":
            raise RuntimeError("portable direct-device model-load authority is not active")
        if authority.get("runner_sha256") != sha256_file(Path(__file__).resolve()):
            raise RuntimeError("direct-device model-load runner content-address binding drift")
        parent = authority.get("parent_8x8_host_exit_adjudication") or {}
        static = authority.get("static_qualification") or {}
        if sha256_file(host_exit_adjudication) != parent.get("sha256"):
            raise RuntimeError("8x8 host-exit adjudication SHA drift")
        if sha256_file(static_qualification) != static.get("sha256"):
            raise RuntimeError("direct-device static qualification SHA drift")
        if json.loads(static_qualification.read_text(encoding="utf-8")).get("status") != "PI05_DIRECT_DEVICE_CHECKPOINT_LOADER_STATIC_QUALIFIED":
            raise RuntimeError("direct-device static qualification is not PASS")
        portable_child = authority.get("portable_child_equivalence") or {}
        portable_env = authority.get("portable_env_qualification") or {}
        if sha256_file(portable_child_equivalence) != portable_child.get("sha256"):
            raise RuntimeError("portable child-equivalence SHA drift")
        if sha256_file(portable_env_qualification) != portable_env.get("sha256"):
            raise RuntimeError("portable environment qualification SHA drift")
        if json.loads(portable_child_equivalence.read_text(encoding="utf-8")).get("status") != "PORTABLE_OPENPI_CHILD_CONTENT_EQUIVALENCE_PASS":
            raise RuntimeError("portable child-equivalence is not PASS")
        if json.loads(portable_env_qualification.read_text(encoding="utf-8")).get("status") != "PORTABLE_OPENPI_FROZEN_ENVIRONMENT_PASS":
            raise RuntimeError("portable environment qualification is not PASS")
        portable_head = subprocess.check_output(["git", "-C", str(child_root), "rev-parse", "HEAD"], text=True).strip()
        if portable_head != EXPECTED_PARENT_COMMIT:
            raise RuntimeError(f"portable OpenPI parent drift: {portable_head}")
        status_lines = subprocess.check_output(["git", "-C", str(child_root), "status", "--porcelain"], text=True).splitlines()
        changed_paths = sorted(line[3:] for line in status_lines if line.strip())
        if changed_paths != ["src/openpi/training/config.py"]:
            raise RuntimeError(f"portable OpenPI changed-path drift: {changed_paths}")
        portable_config_sha256 = sha256_file(child_root / "src/openpi/training/config.py")
        if portable_config_sha256 != EXPECTED_FINAL_CONFIG_SHA256:
            raise RuntimeError(f"portable OpenPI config SHA drift: {portable_config_sha256}/{EXPECTED_FINAL_CONFIG_SHA256}")

        base_receipt_sha, object_count, total_bytes = validate_local_checkpoint(base_receipt, params_root)
        resource_scope = qualification_scope_snapshot()
        host_before = host_memory_snapshot()
        before_gpu = gpu_snapshot()
        if len(before_gpu["gpus"]) != 1:
            raise RuntimeError(f"qualification host must expose exactly one GPU, got {len(before_gpu['gpus'])}")
        gpu0 = before_gpu["gpus"][0]
        if "A100" not in gpu0["name"] or gpu0["memory_total_mib"] < 80_000:
            raise RuntimeError(f"unexpected qualification GPU: {gpu0}")
        if gpu0["memory_used_mib"] > 8_192 or gpu0["utilization_gpu_percent"] > 25:
            raise RuntimeError(f"qualification GPU is not sufficiently idle: {gpu0}")

        os.chdir(child_root)
        sys.path.insert(0, str(child_root))
        sys.path.insert(0, str(child_root / "src"))

        import jax
        import openpi.models.model as model_lib
        from openpi.training import config as config_lib
        from openpi.training import sharding
        from openpi.training import weight_loaders
        from scripts.b1k import train_b1k

        class DirectDeviceCheckpointWeightLoader:
            def __init__(self, params_path: str):
                self.params_path = params_path
                self.audit = None

            def load(self, params):
                loaded = model_lib.restore_params(self.params_path, restore_type=jax.Array)
                leaves = jax.tree.leaves(loaded)
                if not leaves or not all(isinstance(x, jax.Array) for x in leaves):
                    raise RuntimeError('direct-device restore returned non-jax.Array checkpoint leaves')
                self.audit = {
                    'restored_leaf_count': len(leaves),
                    'all_restored_leaves_are_jax_array': True,
                    'restore_type': 'jax.Array',
                    'restored_devices': sorted({str(x.device) for x in leaves}),
                }
                return weight_loaders._merge_params(loaded, params, missing_regex='.*lora.*')

        devices = jax.devices()
        if len(devices) != 1 or devices[0].platform != "gpu":
            raise RuntimeError(f"expected one JAX GPU device, got {devices}")

        config = config_lib.get_config(CONFIG_NAME)
        direct_loader = DirectDeviceCheckpointWeightLoader(str(params_root))
        config = dataclasses.replace(
            config,
            exp_name=EXPECTED_EXP_NAME,
            weight_loader=direct_loader,
            wandb_enabled=False,
            resume=False,
            overwrite=True,
        )
        if config.seed != 42 or config.batch_size != 64 or config.num_train_steps != 50_000 or config.model.action_horizon != 32:
            raise RuntimeError("frozen child training config drift")
        if config.fsdp_devices != 1:
            raise RuntimeError("frozen fsdp_devices drift")

        model_load_attempted = True
        status = "PI05_PORTABLE_DIRECT_DEVICE_NO_UPDATE_MODEL_LOAD_HOLD"
        error = None
        train_state_ready = False
        step = None
        after_gpu = None
        try:
            rng = jax.random.key(config.seed)
            _train_rng, init_rng = jax.random.split(rng)
            mesh = sharding.make_mesh(config.fsdp_devices)
            train_state, _train_state_sharding = train_b1k.init_train_state(config, init_rng, mesh, resume=False)
            jax.block_until_ready(train_state)
            step = int(jax.device_get(train_state.step))
            if step != 0:
                raise RuntimeError(f"unexpected initialized train step: {step}")
            train_state_ready = True
            after_gpu = gpu_snapshot()
            status = "PI05_PORTABLE_DIRECT_DEVICE_NO_UPDATE_MODEL_LOAD_PASS"
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            try:
                after_gpu = gpu_snapshot()
            except Exception:
                after_gpu = None

        host_after = host_memory_snapshot()
        receipt = {
            "schema_version": "behavior-formal-goal-coupling-pi05-portable-direct-device-no-update-model-load-result-v1",
            "object_id": OBJECT_ID,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "authority_path": str(authority_path),
            "authority_sha256": sha256_file(authority_path),
            "openpi_child_root": str(child_root),
            "portable_openpi_parent_commit": portable_head,
            "portable_openpi_changed_paths": changed_paths,
            "portable_openpi_config_sha256": portable_config_sha256,
            "canonical_69_child_commit": "0d05f46ef40a6a0ff0a9b61f078835a71fececde",
            "config_name": CONFIG_NAME,
            "exp_name": EXPECTED_EXP_NAME,
            "local_checkpoint_root": str(params_root),
            "base_asset_receipt": str(base_receipt),
            "base_asset_receipt_sha256": base_receipt_sha,
            "base_object_count_rehashed": object_count,
            "base_bytes_rehashed": total_bytes,
            "qualification_visible_device_count": len(devices),
            "qualification_devices": [str(device) for device in devices],
            "fsdp_devices": config.fsdp_devices,
            "global_batch_size": config.batch_size,
            "resource_scope": resource_scope,
            "host_memory_before": host_before,
            "host_memory_after_ready_or_error": host_after,
            "gpu_before": before_gpu,
            "gpu_after_ready_or_error": after_gpu,
            "checkpoint_restore_adapter": "OpenPI restore_params(..., restore_type=jax.Array) with one-device replicated sharding; no np.ndarray released-checkpoint staging",
            "direct_device_loader_audit": direct_loader.audit,
            "model_load_attempted": model_load_attempted,
            "train_state_ready": train_state_ready,
            "initialized_step": step,
            "error": error,
            "dataset_accessed": False,
            "tokenizer_executed": False,
            "forward_pass_executed": False,
            "loss_computed": False,
            "backward_pass_executed": False,
            "optimizer_update": False,
            "checkpoint_written": False,
            "policy_rollouts_started": False,
            "policy_outcomes_read": False,
            "model_checkpoint_weight_downloaded": True,
            "model_loaded": train_state_ready,
            "gpu_used": True,
            "training_started": False,
            "formal_training_topology_authorized": False,
            "scientific_authority": False,
            "next_gate": "STREAMING_ACCUM8X8_PORTABLE_DIRECT_DEVICE_REPAIR_AUTHORITY" if train_state_ready else "PORTABLE_DIRECT_DEVICE_MODEL_LOAD_FAILURE_REVIEW",
        }
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({k: receipt[k] for k in ["status", "train_state_ready", "initialized_step", "error", "next_gate"]}, sort_keys=True))
        return 0 if train_state_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
