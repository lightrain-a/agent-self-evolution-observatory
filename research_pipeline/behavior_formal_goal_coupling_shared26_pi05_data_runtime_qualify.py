from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import jax
import torch

import openpi.training.config as config_lib
import openpi.training.data_loader as data_loader

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CONFIG_NAME = "pi05_b1k_shared26_frozen"
OFFICIAL_REPO_ID = "behavior-1k/2026-challenge-demos"
DATASET_REVISION = "4f50b44796641a4d526a19d9aeadc8aa51e2f2c2"
ASSET_ID = "b1k_shared26_frozen"
ROOT = Path("/data/wyt/behavior-2026-shared26-v3.0")
REQUIRED_RGB = {
    "observation.rgb.zed_link_camera_0",
    "observation.rgb.left_realsense_link_camera_0",
    "observation.rgb.right_realsense_link_camera_0",
}
EXPECTED_UNUSED_DEPTH = {
    "observation.depth_linear.zed_link_camera_0",
    "observation.depth_linear.left_realsense_link_camera_0",
    "observation.depth_linear.right_realsense_link_camera_0",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-child", type=Path, required=True)
    parser.add_argument("--materialization-manifest", type=Path, required=True)
    parser.add_argument("--hold", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.receipt.exists():
        raise FileExistsError(f"refusing to overwrite receipt: {args.receipt}")

    frozen = json.loads(args.frozen_child.read_text(encoding="utf-8"))
    expected_episodes = frozen["child_config"]["dataset_kwargs"]["episodes"]
    if len(expected_episodes) != 5200 or len(set(expected_episodes)) != 5200:
        raise ValueError("frozen 5200-episode subset drift")

    manifest = json.loads(args.materialization_manifest.read_text(encoding="utf-8"))
    if manifest.get("object_id") != OBJECT_ID:
        raise ValueError("materialization object drift")

    lock_path = ROOT.parent / f".{ROOT.name}.pi05-data-runtime-qualification.lock"
    with lock_path.open("a+") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"another pi0.5 data-runtime qualification actor holds {lock_path}") from exc

        cfg = config_lib.get_config(CONFIG_NAME)
        data_cfg = cfg.data.create(cfg.assets_dirs, cfg.model)
        observed_episodes = data_cfg.dataset_kwargs.get("episodes")

        static_checks = {
            "config_name": cfg.name == CONFIG_NAME,
            "seed_42": cfg.seed == 42,
            "batch_64": cfg.batch_size == 64,
            "steps_50000": cfg.num_train_steps == 50_000,
            "action_horizon_32": cfg.model.action_horizon == 32,
            "official_repo_id": data_cfg.repo_id == OFFICIAL_REPO_ID,
            "asset_id": data_cfg.asset_id == ASSET_ID,
            "dataset_root": str(data_cfg.dataset_root) == str(ROOT),
            "dataset_revision": data_cfg.dataset_kwargs.get("revision") == DATASET_REVISION,
            "download_videos_false": data_cfg.dataset_kwargs.get("download_videos") is False,
            "z_score": data_cfg.use_quantile_norm is False,
            "prompt_from_task": data_cfg.prompt_from_task is True,
            "episode_subset_exact": observed_episodes == expected_episodes,
            "cpu_only_jax": all(device.platform == "cpu" for device in jax.devices()),
            "torch_cuda_unavailable": torch.cuda.is_available() is False,
        }
        if not all(static_checks.values()):
            raise RuntimeError(f"static child/runtime check failed: {static_checks}")

        transformed = data_loader.create_b1k_dataset(data_cfg, cfg.model.action_horizon)
        base = transformed._dataset if hasattr(transformed, "_dataset") else transformed
        loaded_episodes = set(int(x) for x in base.reader.hf_dataset.unique("episode_index"))
        expected_set = set(expected_episodes)

        rgb_paths: set[Path] = set()
        missing_rgb: list[str] = []
        generic_missing_keys: set[str] = set()
        generic_missing_paths: set[str] = set()
        for episode in expected_episodes:
            for key in base.meta.video_keys:
                path = ROOT / base.meta.get_video_file_path(episode, key)
                if key in REQUIRED_RGB:
                    rgb_paths.add(path)
                    if not path.is_file():
                        missing_rgb.append(str(path.relative_to(ROOT)))
                elif not path.is_file():
                    generic_missing_keys.add(key)
                    generic_missing_paths.add(str(path.relative_to(ROOT)))

        # download_videos=False means the source-native fallback can only touch non-video files.
        # Rehash every frozen non-video payload after construction to prove the scientific payload stayed exact.
        nonvideo_rows = [row for row in manifest["required_payload"] if not row["path"].startswith("videos/")]
        nonvideo_verified = 0
        nonvideo_bytes = 0
        nonvideo_failures: list[dict] = []
        for row in nonvideo_rows:
            path = ROOT / row["path"]
            expected_size = int(row["lfs_size_bytes"])
            expected_sha = row["lfs_oid_sha256"]
            if not path.is_file():
                nonvideo_failures.append({"path": row["path"], "reason": "missing"})
                continue
            observed_size = path.stat().st_size
            if observed_size != expected_size:
                nonvideo_failures.append(
                    {"path": row["path"], "reason": "size", "expected": expected_size, "observed": observed_size}
                )
                continue
            observed_sha = sha256_file(path)
            if observed_sha != expected_sha:
                nonvideo_failures.append(
                    {"path": row["path"], "reason": "sha256", "expected": expected_sha, "observed": observed_sha}
                )
                continue
            nonvideo_verified += 1
            nonvideo_bytes += expected_size

        passed = (
            loaded_episodes == expected_set
            and len(base.episodes) == 5200
            and not missing_rgb
            and generic_missing_keys == EXPECTED_UNUSED_DEPTH
            and len(generic_missing_paths) == 2532
            and nonvideo_verified == len(nonvideo_rows)
            and not nonvideo_failures
        )

        receipt = {
            "schema_version": "behavior-formal-goal-coupling-shared26-pi05-data-runtime-qualification-v1",
            "object_id": OBJECT_ID,
            "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "status": "PI05_DATA_RUNTIME_QUALIFICATION_PASS" if passed else "PI05_DATA_RUNTIME_QUALIFICATION_HOLD",
            "repair_hold_path": str(args.hold),
            "repair_hold_sha256": sha256_file(args.hold),
            "frozen_child_path": str(args.frozen_child),
            "frozen_child_sha256": sha256_file(args.frozen_child),
            "materialization_manifest_path": str(args.materialization_manifest),
            "materialization_manifest_sha256": sha256_file(args.materialization_manifest),
            "static_checks": static_checks,
            "dataset_type": type(base).__name__,
            "frame_count": len(base),
            "configured_episode_count": len(observed_episodes),
            "loaded_unique_episode_count": len(loaded_episodes),
            "loaded_episode_set_exact": loaded_episodes == expected_set,
            "required_rgb_unique_file_count": len(rgb_paths),
            "missing_required_rgb_file_count": len(missing_rgb),
            "missing_required_rgb_files": missing_rgb,
            "generic_missing_video_modalities": sorted(generic_missing_keys),
            "generic_missing_unique_video_file_count": len(generic_missing_paths),
            "all_generic_missing_video_modalities_are_unused_depth": generic_missing_keys == EXPECTED_UNUSED_DEPTH,
            "post_constructor_nonvideo_payload_file_count": len(nonvideo_rows),
            "post_constructor_nonvideo_payload_verified_count": nonvideo_verified,
            "post_constructor_nonvideo_payload_verified_bytes": nonvideo_bytes,
            "post_constructor_nonvideo_payload_failures": nonvideo_failures,
            "extra_runtime_cache_is_non_evidence": True,
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
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    print(json.dumps({
        "status": receipt["status"],
        "frame_count": receipt["frame_count"],
        "loaded_unique_episode_count": receipt["loaded_unique_episode_count"],
        "required_rgb_unique_file_count": receipt["required_rgb_unique_file_count"],
        "generic_missing_unique_video_file_count": receipt["generic_missing_unique_video_file_count"],
        "post_constructor_nonvideo_payload_verified_count": receipt["post_constructor_nonvideo_payload_verified_count"],
    }, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
