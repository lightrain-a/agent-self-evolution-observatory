from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import jax
import numpy as np
import torch

import openpi.training.config as config_lib
import openpi.training.data_loader as data_loader

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
RUNTIME_ROOT = Path("/data/wyt/behavior-2026-shared26-v3.0-rgb-runtime-repair2")
OFFICIAL_REPO_ID = "behavior-1k/2026-challenge-demos"
DATASET_REVISION = "4f50b44796641a4d526a19d9aeadc8aa51e2f2c2"
ASSET_ID = "b1k_shared26_frozen"
REQUIRED_RGB = {
    "observation.rgb.zed_link_camera_0",
    "observation.rgb.left_realsense_link_camera_0",
    "observation.rgb.right_realsense_link_camera_0",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def shape_list(value) -> list[int]:
    return [int(x) for x in np.asarray(value).shape]


def main() -> int:
    parser = argparse.ArgumentParser(description="CPU-only offline sample-schema qualification for shared26 RGB runtime view")
    parser.add_argument("--frozen-child", type=Path, required=True)
    parser.add_argument("--projection-receipt", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.receipt.exists():
        raise FileExistsError(f"refusing to overwrite receipt: {args.receipt}")
    if os.environ.get("HF_HUB_OFFLINE") != "1":
        raise RuntimeError("HF_HUB_OFFLINE=1 is mandatory for repair2 qualification")

    projection = json.loads(args.projection_receipt.read_text(encoding="utf-8"))
    if projection.get("status") != "RGB_RUNTIME_PROJECTION_PASS":
        raise ValueError("RGB runtime projection receipt is not PASS")
    if Path(projection["runtime_root"]) != RUNTIME_ROOT:
        raise ValueError("runtime projection root drift")

    frozen = json.loads(args.frozen_child.read_text(encoding="utf-8"))
    expected_episodes = frozen["child_config"]["dataset_kwargs"]["episodes"]
    if len(expected_episodes) != 5200 or len(set(expected_episodes)) != 5200:
        raise ValueError("frozen episode subset drift")

    lock_path = RUNTIME_ROOT.parent / f".{RUNTIME_ROOT.name}.sample-qualification.lock"
    with lock_path.open("a+") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"another sample qualification actor holds {lock_path}") from exc

        cfg = config_lib.get_config(CONFIG_NAME)
        data_cfg = cfg.data.create(cfg.assets_dirs, cfg.model)
        static_checks = {
            "config_name": cfg.name == CONFIG_NAME,
            "seed_42": cfg.seed == 42,
            "batch_64": cfg.batch_size == 64,
            "steps_50000": cfg.num_train_steps == 50_000,
            "action_horizon_32": cfg.model.action_horizon == 32,
            "official_repo_id": data_cfg.repo_id == OFFICIAL_REPO_ID,
            "asset_id": data_cfg.asset_id == ASSET_ID,
            "runtime_root": Path(data_cfg.dataset_root) == RUNTIME_ROOT,
            "dataset_revision": data_cfg.dataset_kwargs.get("revision") == DATASET_REVISION,
            "download_videos_false": data_cfg.dataset_kwargs.get("download_videos") is False,
            "episode_subset_exact": data_cfg.dataset_kwargs.get("episodes") == expected_episodes,
            "z_score": data_cfg.use_quantile_norm is False,
            "prompt_from_task": data_cfg.prompt_from_task is True,
            "cpu_only_jax": all(device.platform == "cpu" for device in jax.devices()),
            "torch_cuda_unavailable": torch.cuda.is_available() is False,
            "data_symlink": (RUNTIME_ROOT / "data").is_symlink(),
            "videos_symlink": (RUNTIME_ROOT / "videos").is_symlink(),
        }
        if not all(static_checks.values()):
            raise RuntimeError(f"repair2 static check failed: {static_checks}")

        dataset = data_loader.create_b1k_dataset(data_cfg, cfg.model.action_horizon)
        base = dataset._dataset if hasattr(dataset, "_dataset") else dataset
        video_keys = set(base.meta.video_keys)
        depth_keys = set(base.meta.depth_keys)
        loaded_episodes = set(int(x) for x in base.reader.hf_dataset.unique("episode_index"))

        sample_dataset = data_loader.TransformedDataset(
            dataset,
            [
                *data_cfg.repack_transforms.inputs,
                *data_cfg.data_transforms.inputs,
            ],
        )
        sample = sample_dataset[0]
        state_shape = shape_list(sample["state"])
        action_shape = shape_list(sample["actions"])
        image_shapes = {key: shape_list(value) for key, value in sample["image"].items()}
        image_dtypes = {key: str(np.asarray(value).dtype) for key, value in sample["image"].items()}
        prompt = sample.get("prompt")

        sample_checks = {
            "metadata_video_keys_exact_rgb": video_keys == REQUIRED_RGB,
            "metadata_depth_keys_empty": not depth_keys,
            "loaded_episode_set_exact": loaded_episodes == set(expected_episodes),
            "selected_episode_count_5200": len(base.episodes) == 5200,
            "state_shape_23": state_shape == [23],
            "actions_shape_32x23": action_shape == [32, 23],
            "three_model_images": set(image_shapes) == {"base_0_rgb", "left_wrist_0_rgb", "right_wrist_0_rgb"},
            "all_images_uint8": all(dtype == "uint8" for dtype in image_dtypes.values()),
            "prompt_present": isinstance(prompt, str) and bool(prompt),
        }
        passed = all(sample_checks.values())
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    receipt = {
        "schema_version": "behavior-formal-goal-coupling-shared26-pi05-rgb-sample-qualification-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "status": "PI05_RGB_SAMPLE_SCHEMA_QUALIFICATION_PASS" if passed else "PI05_RGB_SAMPLE_SCHEMA_QUALIFICATION_HOLD",
        "frozen_child_path": str(args.frozen_child),
        "frozen_child_sha256": sha256_file(args.frozen_child),
        "projection_receipt_path": str(args.projection_receipt),
        "projection_receipt_sha256": sha256_file(args.projection_receipt),
        "hf_hub_offline": True,
        "static_checks": static_checks,
        "sample_checks": sample_checks,
        "dataset_frame_count": len(base),
        "loaded_unique_episode_count": len(loaded_episodes),
        "metadata_video_keys": sorted(video_keys),
        "metadata_depth_keys": sorted(depth_keys),
        "state_shape": state_shape,
        "actions_shape": action_shape,
        "image_shapes": image_shapes,
        "image_dtypes": image_dtypes,
        "prompt_nonempty": bool(prompt),
        "sample_index": 0,
        "scientific_outcome": False,
        "model_checkpoint_weight_downloaded": False,
        "model_loaded": False,
        "gpu_used": False,
        "training_started": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_authority": False,
        "next_gate_if_pass": "CPU_ONLY_SOURCE_FAITHFUL_NORMALIZATION",
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "dataset_frame_count": receipt["dataset_frame_count"],
        "loaded_unique_episode_count": receipt["loaded_unique_episode_count"],
        "state_shape": receipt["state_shape"],
        "actions_shape": receipt["actions_shape"],
        "metadata_video_keys": receipt["metadata_video_keys"],
    }, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
