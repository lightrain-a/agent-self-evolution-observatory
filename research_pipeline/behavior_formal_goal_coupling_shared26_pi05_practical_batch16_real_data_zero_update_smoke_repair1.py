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
EXP_NAME = "shared26-seed42-practical-b16-run1"
PARENT_COMMIT = "0cc8e355f7bac0976db1cc3139b1ff0379feea60"
CONFIG_SHA = "4a50bb5f3579ed0035e19d2fc2a5d33821c0cc115c6e8c441eac497e74b02e99"
PRACTICAL_PREREG_SHA = "382449b4320bacd85f736c0df9342f9677b3c755f2daeedcd680212aed2a503a"
SYNTHETIC_BATCH16_RESULT_SHA = "3914b1f2a3fd5e7964524eac7f625b64b4f089c0048a12dc5ebe9b79ba9bd86e"
BASE_RECEIPT_SHA = "8e0f977e0641960ee3e082a19a57f52f994a817bbf981cbb2f7007ea3104a4ed"
NORM_SHA = "5e4159ec0986ad9fc87cc9a265eed9ac67fc9d2d0df233db6130acf0ebff52ce"
TOKEN_SHA = "8986bb4f423f07f8c7f70d0dbe3526fb2316056c17bae71b1ea975e77a168fc6"
PROJECTION_INFO_SHA = "9955a58511fdba468ca10b6929c9051f6d693e3915cdc58d66c1cd1ce04a45e1"
CONSUMED_SMOKE_SHA = "ac5a84f884c4619d508179a74ea597a3de6553b1b853cf5a7c17068e9329b938"
CONSUMED_SMOKE_AUTH_SHA = "769131998d297ab04c7e2cc3a1d107a7ba9c31a9655802048ad4eaafb6ce5e22"
FFMPEG_QUAL_SHA = "25e744ac85ce7811ce78483e353d68da651cd3d3149f24d8c64fd263c32561ca"
FFMPEG_LIBRARY_DIR = "/data/wyt/formal-goal-ffmpeg6-runtime-v1/usr/lib/x86_64-linux-gnu"
BATCH = 16
SEED = 42
ACTION_HORIZON = 32
EPISODES = 5200
FSDP = 1
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


def write_receipt(path: Path, payload: dict) -> None:
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


def gpu_snapshot() -> dict:
    lines = subprocess.check_output([
        "nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
        "--format=csv,noheader,nounits",
    ], text=True).strip().splitlines()
    rows = []
    for line in lines:
        i, name, total, used, util = [x.strip() for x in line.split(",", 4)]
        rows.append({"index": int(i), "name": name, "memory_total_mib": int(total), "memory_used_mib": int(used), "utilization_gpu_percent": int(util)})
    return {"gpus": rows}


def host_snapshot() -> dict:
    out = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        if ":" in line:
            key, rest = line.split(":", 1)
            if key in {"MemTotal", "MemAvailable", "MemFree", "SwapTotal", "SwapFree"}:
                out[key + "_kib"] = int(rest.strip().split()[0])
    out["process_rss_kib"] = int(Path("/proc/self/status").read_text().split("VmRSS:", 1)[1].splitlines()[0].strip().split()[0])
    return out


def scope_snapshot() -> dict:
    rows = Path("/proc/self/cgroup").read_text().splitlines()
    ids = [row.split(":", 2)[2] for row in rows if row.startswith("0::")]
    if len(ids) != 1:
        raise RuntimeError(f"cgroup-v2 drift: {ids}")
    cg = Path("/sys/fs/cgroup") / ids[0].lstrip("/")
    mm = (cg / "memory.max").read_text().strip(); sm = (cg / "memory.swap.max").read_text().strip()
    if mm == "max" or int(mm) != EXPECTED_MEMORY_MAX:
        raise RuntimeError(f"real-data smoke requires MemoryMax exactly 40G, got {mm}")
    if sm != "0":
        raise RuntimeError(f"real-data smoke requires MemorySwapMax=0, got {sm}")
    if set(os.sched_getaffinity(0)) != set(range(64)):
        raise RuntimeError("CPU affinity drift")
    return {"cgroup": str(cg), "memory_max_bytes": int(mm), "memory_swap_max_bytes": 0, "cpu_affinity": "0-63"}


def jax_mem(device) -> dict | None:
    try:
        d = device.memory_stats()
    except Exception:
        return None
    if d is None:
        return None
    return {str(k): v for k, v in d.items() if isinstance(v, (int, float, str, bool)) or v is None}


def portable_child(root: Path) -> dict:
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if head != PARENT_COMMIT:
        raise RuntimeError(f"portable parent drift: {head}")
    cfg = sha(root / "src/openpi/training/config.py")
    if cfg != CONFIG_SHA:
        raise RuntimeError(f"portable config SHA drift: {cfg}")
    changed = sorted(line[3:] for line in subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True).splitlines() if line.strip())
    if changed != ["src/openpi/training/config.py"]:
        raise RuntimeError(f"portable changed-path drift: {changed}")
    return {"parent_commit": head, "config_sha256": cfg, "changed_paths": changed}


def tree_metadata(tree) -> list[dict]:
    import jax
    rows = []
    for path, value in jax.tree_util.tree_flatten_with_path(tree)[0]:
        rows.append({"path": jax.tree_util.keystr(path), "shape": list(value.shape), "dtype": str(value.dtype)})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    for name in [
        "authority", "preregistration", "synthetic_batch16_result", "dataset_seal", "base_receipt",
        "consumed_smoke", "consumed_smoke_authority", "ffmpeg_runtime_qualification",
        "openpi_child_root", "params_root", "projection_root", "norm_stats", "tokenizer", "receipt",
    ]:
        ap.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    a = ap.parse_args(); p = {k: getattr(a, k).resolve() for k in vars(a)}
    if p["receipt"].exists():
        raise RuntimeError(f"exactly-once real-data batch16 smoke repair1 receipt exists: {p['receipt']}")
    auth = json.loads(p["authority"].read_text())
    if auth.get("status") != "AUTHORIZED_PI05_PRACTICAL_BATCH16_REAL_DATA_ZERO_UPDATE_SMOKE_REPAIR1_FFMPEG6":
        raise RuntimeError("real-data smoke repair1 authority not active")
    if auth.get("runner_sha256") != sha(Path(__file__).resolve()):
        raise RuntimeError("runner SHA binding drift")
    require(p["preregistration"], PRACTICAL_PREREG_SHA, "practical prereg")
    require(p["synthetic_batch16_result"], SYNTHETIC_BATCH16_RESULT_SHA, "synthetic batch16 result")
    require(p["consumed_smoke"], CONSUMED_SMOKE_SHA, "consumed real-data smoke HOLD")
    require(p["consumed_smoke_authority"], CONSUMED_SMOKE_AUTH_SHA, "consumed real-data smoke authority")
    require(p["ffmpeg_runtime_qualification"], FFMPEG_QUAL_SHA, "FFmpeg6 runtime qualification")
    consumed = json.loads(p["consumed_smoke"].read_text())
    if consumed.get("status") != "PI05_PRACTICAL_BATCH16_REAL_DATA_ZERO_UPDATE_HOLD" or not consumed.get("state_ready") or consumed.get("batch_ready") or consumed.get("optimizer_update") or consumed.get("forward_pass") or consumed.get("backward_pass"):
        raise RuntimeError("consumed smoke lineage drift")
    consumed_error = str(consumed.get("error") or "")
    if "Could not load libtorchcodec" not in consumed_error or "libavdevice.so.60" not in consumed_error:
        raise RuntimeError("consumed smoke is not the frozen FFmpeg runtime failure")
    ffmpeg_qual = json.loads(p["ffmpeg_runtime_qualification"].read_text())
    if ffmpeg_qual.get("status") != "PI05_FFMPEG6_USER_RUNTIME_QUALIFICATION_PASS" or ffmpeg_qual.get("library_dir") != FFMPEG_LIBRARY_DIR:
        raise RuntimeError("FFmpeg6 qualification drift")
    if any(int(row.get("missing_count", -1)) != 0 for row in ffmpeg_qual.get("ldd_closure", {}).values()):
        raise RuntimeError("FFmpeg6 dependency closure is incomplete")
    decode = ffmpeg_qual.get("torchcodec_decode") or {}
    if decode.get("frame_shape") != [3, 480, 480] or decode.get("frame_dtype") != "torch.uint8":
        raise RuntimeError("FFmpeg6 TorchCodec decode qualification drift")
    synth = json.loads(p["synthetic_batch16_result"].read_text())
    if synth.get("status") != "PI05_PRACTICAL_BATCH16_SYNTHETIC_FULL_STEP_PASS" or synth.get("synthetic_step_after") != 1:
        raise RuntimeError("synthetic batch16 PASS drift")
    seal_sha = sha(p["dataset_seal"])
    if seal_sha != auth.get("dataset_seal_sha256"):
        raise RuntimeError("dataset seal SHA binding drift")
    seal = json.loads(p["dataset_seal"].read_text())
    if seal.get("status") != "WHOLE_MANIFEST_FINAL_SEAL_PASS" or seal.get("verified_file_count") != 1380 or seal.get("verified_bytes") != 236480375583:
        raise RuntimeError("dataset seal not PASS")
    require(p["base_receipt"], BASE_RECEIPT_SHA, "base receipt")
    require(p["projection_root"] / "meta/info.json", PROJECTION_INFO_SHA, "RGB projection info")
    require(p["norm_stats"], NORM_SHA, "norm stats")
    require(p["tokenizer"], TOKEN_SHA, "tokenizer")
    for key, value in REQUIRED_ENV.items():
        if os.environ.get(key) != value:
            raise RuntimeError(f"environment drift {key}={os.environ.get(key)!r}/{value!r}")
    ld_library_path = [str(Path(x).resolve()) for x in os.environ.get("LD_LIBRARY_PATH", "").split(":") if x]
    if str(Path(FFMPEG_LIBRARY_DIR).resolve()) not in ld_library_path:
        raise RuntimeError(f"FFmpeg6 runtime not present in LD_LIBRARY_PATH: {ld_library_path}")
    if Path(os.environ.get("OPENPI_DATA_HOME", "")).resolve() != Path(auth["openpi_data_home"]).resolve():
        raise RuntimeError("OPENPI_DATA_HOME drift")
    scope = scope_snapshot(); child = portable_child(p["openpi_child_root"])
    before_gpu = gpu_snapshot(); before_host = host_snapshot()
    if len(before_gpu["gpus"]) != 1 or "A100" not in before_gpu["gpus"][0]["name"] or before_gpu["gpus"][0]["memory_used_mib"] > 1024 or before_gpu["gpus"][0]["utilization_gpu_percent"] > 25:
        raise RuntimeError(f"GPU not admitted: {before_gpu}")

    initial = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-practical-batch16-real-data-zero-update-smoke-repair1-v1",
        "object_id": OBJECT_ID, "child_id": CHILD_ID, "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PI05_PRACTICAL_BATCH16_REAL_DATA_ZERO_UPDATE_REPAIR1_STARTED", "batch_size": BATCH,
        "authority_sha256": sha(p["authority"]), "dataset_seal_sha256": seal_sha, "portable_openpi": child,
        "consumed_smoke_sha256": CONSUMED_SMOKE_SHA, "consumed_smoke_authority_sha256": CONSUMED_SMOKE_AUTH_SHA,
        "ffmpeg_runtime_qualification_sha256": FFMPEG_QUAL_SHA, "ffmpeg_library_dir": FFMPEG_LIBRARY_DIR,
        "resource_scope": scope, "gpu_before": before_gpu, "host_before": before_host,
        "state_ready": False, "batch_ready": False, "behavior_dataset_accessed": False,
        "forward_pass": False, "backward_pass": False, "optimizer_update": False, "checkpoint_written": False,
        "loss_value_read": False, "policy_outcomes_read": False, "formal_training_authorized": False,
    }
    with lock(Path("/data/wyt/.formal-goal-pi05-practical-batch16-real-data-zero-update-smoke-repair1.lock")):
        write_receipt(p["receipt"], initial)
        status = "PI05_PRACTICAL_BATCH16_REAL_DATA_ZERO_UPDATE_REPAIR1_HOLD"; error = None
        state_ready = batch_ready = False; gpu_state = gpu_batch = None; host_state = host_batch = None; jm_state = jm_batch = None; metadata = None
        try:
            root = p["openpi_child_root"]; os.chdir(root); sys.path.insert(0, str(root)); sys.path.insert(0, str(root / "src"))
            import jax
            import openpi.models.model as model_lib
            import openpi.training.config as config_lib
            import openpi.training.data_loader as data_loader
            import openpi.training.sharding as sharding
            import openpi.training.weight_loaders as weight_loaders
            from scripts.b1k import train_b1k

            class DirectDeviceCheckpointWeightLoader:
                def __init__(self, path: str): self.path = path
                def load(self, params):
                    loaded = model_lib.restore_params(self.path, restore_type=jax.Array)
                    if not all(isinstance(x, jax.Array) for x in jax.tree.leaves(loaded)):
                        raise RuntimeError("non-jax checkpoint leaf")
                    return weight_loaders._merge_params(loaded, params, missing_regex=".*lora.*")

            devices = jax.devices();
            if len(devices) != 1 or devices[0].platform != "gpu": raise RuntimeError(f"CUDA device drift: {devices}")
            device = devices[0]
            src = config_lib.get_config(CONFIG_NAME)
            cfg = dataclasses.replace(src, exp_name=EXP_NAME, weight_loader=DirectDeviceCheckpointWeightLoader(str(p["params_root"])), batch_size=BATCH, num_workers=0, wandb_enabled=False, resume=False, overwrite=True)
            episodes = list(cfg.data.base_config.dataset_kwargs.get("episodes", []))
            if src.batch_size != 64 or cfg.batch_size != 16 or cfg.seed != SEED or cfg.num_train_steps != 50_000 or cfg.model.action_horizon != ACTION_HORIZON or cfg.fsdp_devices != FSDP or len(episodes) != EPISODES or len(set(episodes)) != EPISODES:
                raise RuntimeError("batch16 config drift")
            mesh = sharding.make_mesh(cfg.fsdp_devices)
            ds = jax.sharding.NamedSharding(mesh, jax.sharding.PartitionSpec(sharding.DATA_AXIS))
            rng = jax.random.key(cfg.seed); _train_rng, init_rng = jax.random.split(rng)
            state, _state_sharding = train_b1k.init_train_state(cfg, init_rng, mesh, resume=False); jax.block_until_ready(state)
            if int(jax.device_get(state.step)) != 0: raise RuntimeError("step-0 drift")
            state_ready = True; gpu_state = gpu_snapshot(); host_state = host_snapshot(); jm_state = jax_mem(device)
            loader = data_loader.create_b1k_data_loader(cfg, sharding=ds, shuffle=True, num_batches=1, skip_norm_stats=False)
            batch = next(iter(loader)); jax.block_until_ready(batch)
            if batch[1].shape[0] != BATCH or tuple(batch[1].shape[1:]) != (ACTION_HORIZON, 23):
                raise RuntimeError(f"action shape drift: {batch[1].shape}")
            batch_ready = True; gpu_batch = gpu_snapshot(); host_batch = host_snapshot(); jm_batch = jax_mem(device); metadata = tree_metadata(batch)
            status = "PI05_PRACTICAL_BATCH16_REAL_DATA_ZERO_UPDATE_REPAIR1_PASS"
            del batch, loader, state
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        finally:
            final = dict(initial); final.update({
                "generated_at": datetime.now(timezone.utc).isoformat(), "status": status,
                "state_ready": state_ready, "batch_ready": batch_ready, "behavior_dataset_accessed": batch_ready,
                "batch_tree_metadata": metadata, "gpu_after_state": gpu_state, "gpu_after_batch": gpu_batch,
                "host_after_state": host_state, "host_after_batch": host_batch, "jax_after_state": jm_state, "jax_after_batch": jm_batch,
                "error": error, "forward_pass": False, "backward_pass": False, "optimizer_update": False,
                "checkpoint_written": False, "loss_value_read": False, "policy_outcomes_read": False,
                "scientific_training_started": False, "formal_training_authorized": False,
                "next_gate": "FREEZE_PRACTICAL_BATCH16_FORMAL_TRAINING_AUTHORITY" if status.endswith("PASS") else "REAL_DATA_BATCH16_REPAIR1_PRETRAINING_REVIEW",
            }); write_receipt(p["receipt"], final)
        print(json.dumps({"status": status, "state_ready": state_ready, "batch_ready": batch_ready, "error": error}, sort_keys=True))
        return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
