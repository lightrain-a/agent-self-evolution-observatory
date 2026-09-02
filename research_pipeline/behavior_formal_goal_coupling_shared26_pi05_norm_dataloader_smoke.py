from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
EXPECTED_CHILD_COMMIT = "0d05f46ef40a6a0ff0a9b61f078835a71fececde"
EXPECTED_NORM_SHA256 = "5e4159ec0986ad9fc87cc9a265eed9ac67fc9d2d0df233db6130acf0ebff52ce"
EXPECTED_DATASET_ROOT = "/data/wyt/behavior-2026-shared26-v3.0-rgb-runtime-repair2"
EXPECTED_REPO_ID = "behavior-1k/2026-challenge-demos"
EXPECTED_ASSET_ID = "b1k_shared26_frozen"
EXPECTED_BATCH_SIZE = 64
EXPECTED_ACTION_HORIZON = 32
EXPECTED_STATE_DIM = 23
EXPECTED_ACTION_DIM = 23
EXPECTED_EPISODE_COUNT = 5200


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def atomic_copy_verified(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if sha256_file(destination) != EXPECTED_NORM_SHA256:
            raise RuntimeError(f"existing norm asset differs from frozen SHA: {destination}")
        return
    fd, tmp_name = tempfile.mkstemp(prefix=destination.name + ".", suffix=".tmp", dir=destination.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        shutil.copyfile(source, tmp)
        if sha256_file(tmp) != EXPECTED_NORM_SHA256:
            raise RuntimeError("copied norm asset failed SHA verification")
        os.replace(tmp, destination)
    finally:
        if tmp.exists():
            tmp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--openpi-child-root", type=Path, required=True)
    parser.add_argument("--norm-source", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    child_root = args.openpi_child_root.resolve()
    norm_source = args.norm_source.resolve()
    receipt_path = args.receipt.resolve()
    lock_path = Path("/data/wyt/.behavior-2026-shared26-v3.0.pi05-norm-dataloader-smoke.lock")

    with exclusive_lock(lock_path):
        import subprocess

        child_commit = subprocess.check_output(["git", "-C", str(child_root), "rev-parse", "HEAD"], text=True).strip()
        if child_commit != EXPECTED_CHILD_COMMIT:
            raise RuntimeError(f"OpenPI child commit drift: {child_commit}")
        if not norm_source.is_file() or sha256_file(norm_source) != EXPECTED_NORM_SHA256:
            raise RuntimeError("frozen normalization asset missing or SHA mismatch")

        sys.path.insert(0, str(child_root / "src"))
        import jax
        import torch
        import openpi.training.config as config_lib
        import openpi.training.data_loader as data_loader
        import openpi.transforms as transforms

        jax_platforms = [device.platform for device in jax.devices()]
        if set(jax_platforms) != {"cpu"}:
            raise RuntimeError(f"zero-update smoke must be CPU-only, got {jax_platforms}")
        if torch.cuda.is_available():
            raise RuntimeError("zero-update smoke must not expose CUDA")

        config = config_lib.get_config(CONFIG_NAME)
        provisional = config.data.create(config.assets_dirs, config.model)
        if provisional.asset_id != EXPECTED_ASSET_ID:
            raise RuntimeError(f"asset_id drift: {provisional.asset_id}")
        asset_path = Path(config.assets_dirs) / EXPECTED_ASSET_ID / "norm_stats.json"
        atomic_copy_verified(norm_source, asset_path)
        if sha256_file(asset_path) != EXPECTED_NORM_SHA256:
            raise RuntimeError("installed norm asset SHA mismatch")

        data_config = config.data.create(config.assets_dirs, config.model)
        episodes = list(data_config.dataset_kwargs.get("episodes", []))
        if len(episodes) != EXPECTED_EPISODE_COUNT or len(set(episodes)) != EXPECTED_EPISODE_COUNT:
            raise RuntimeError("frozen episode subset drift")
        if data_config.dataset_root != EXPECTED_DATASET_ROOT:
            raise RuntimeError(f"dataset root drift: {data_config.dataset_root}")
        if data_config.repo_id != EXPECTED_REPO_ID:
            raise RuntimeError(f"repo_id drift: {data_config.repo_id}")
        if data_config.use_quantile_norm:
            raise RuntimeError("B1K child unexpectedly uses quantile normalization")
        if data_config.norm_stats is None:
            raise RuntimeError("normalization stats were not loaded from the frozen asset")
        if config.batch_size != EXPECTED_BATCH_SIZE or config.model.action_horizon != EXPECTED_ACTION_HORIZON:
            raise RuntimeError("batch size or action horizon drift")

        dataset = data_loader.create_b1k_dataset(data_config=data_config, action_horizon=config.model.action_horizon)
        # Deliberately stop before model transforms/tokenization. This is a data-only smoke.
        transformed = data_loader.TransformedDataset(
            dataset,
            [
                *data_config.repack_transforms.inputs,
                *data_config.data_transforms.inputs,
                transforms.Normalize(data_config.norm_stats, use_quantiles=False),
            ],
        )
        loader = data_loader.TorchDataLoader(
            transformed,
            local_batch_size=config.batch_size,
            sharding=None,
            shuffle=False,
            num_batches=1,
            num_workers=0,
            seed=config.seed,
            framework="pytorch",
        )
        batch = next(iter(loader))

        state = np.asarray(batch["state"])
        actions = np.asarray(batch["actions"])
        if state.shape != (EXPECTED_BATCH_SIZE, EXPECTED_STATE_DIM):
            raise RuntimeError(f"state batch shape mismatch: {state.shape}")
        if actions.shape != (EXPECTED_BATCH_SIZE, EXPECTED_ACTION_HORIZON, EXPECTED_ACTION_DIM):
            raise RuntimeError(f"actions batch shape mismatch: {actions.shape}")
        if not np.isfinite(state).all() or not np.isfinite(actions).all():
            raise RuntimeError("normalized state/actions contain non-finite values")

        image_shapes = {key: list(np.asarray(value).shape) for key, value in batch["image"].items()}
        image_dtypes = {key: str(np.asarray(value).dtype) for key, value in batch["image"].items()}
        expected_image_keys = {"base_0_rgb", "left_wrist_0_rgb", "right_wrist_0_rgb"}
        if set(image_shapes) != expected_image_keys:
            raise RuntimeError(f"unexpected image keys: {sorted(image_shapes)}")

        receipt = {
            "schema_version": "behavior-formal-goal-coupling-shared26-pi05-norm-dataloader-smoke-v1",
            "object_id": OBJECT_ID,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "PI05_NORMALIZED_DATALOADER_ZERO_UPDATE_PASS",
            "openpi_child_commit": child_commit,
            "config_name": CONFIG_NAME,
            "dataset_root": data_config.dataset_root,
            "repo_id": data_config.repo_id,
            "asset_id": data_config.asset_id,
            "episode_count": len(episodes),
            "batch_size": config.batch_size,
            "action_horizon": config.model.action_horizon,
            "norm_source": str(norm_source),
            "norm_stats_sha256": EXPECTED_NORM_SHA256,
            "installed_norm_asset": str(asset_path),
            "installed_norm_asset_sha256": sha256_file(asset_path),
            "jax_platforms": jax_platforms,
            "torch_cuda_available": False,
            "state_shape": list(state.shape),
            "actions_shape": list(actions.shape),
            "state_finite": True,
            "actions_finite": True,
            "image_shapes": image_shapes,
            "image_dtypes": image_dtypes,
            "model_transforms_executed": False,
            "tokenizer_executed": False,
            "model_checkpoint_weight_downloaded": False,
            "model_loaded": False,
            "gpu_used": False,
            "training_started": False,
            "optimizer_update": False,
            "policy_rollouts_started": False,
            "policy_outcomes_read": False,
            "scientific_authority": False,
            "next_gate": "CONTENT_ADDRESS_PI05_BASE_MODEL_ASSETS_AND_NO_UPDATE_MODEL_LOAD_QUALIFICATION",
        }
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({k: receipt[k] for k in ["status", "episode_count", "batch_size", "state_shape", "actions_shape", "norm_stats_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
