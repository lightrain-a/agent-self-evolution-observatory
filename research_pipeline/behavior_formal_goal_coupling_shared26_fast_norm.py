from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from openpi.shared import normalize

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
RUNTIME_ROOT = Path("/data/wyt/behavior-2026-shared26-v3.0-rgb-runtime-repair2")
BATCH_SIZE = 64
ACTION_HORIZON = 32
EXPECTED_DATASET_FRAMES = 50_852_705
EXPECTED_INCLUDED_STARTS = 50_852_672
EXPECTED_ACTION_VECTORS = 1_627_285_504
STATE_WIDTH_RAW = 61
STATE_WIDTH = 23
ACTION_WIDTH = 23
DELTA_MAPPINGS = (
    (tuple(range(3, 7)), tuple(range(3, 7))),
    (tuple(range(7, 14)), tuple(range(7, 14))),
    (tuple(range(15, 22)), tuple(range(15, 22))),
)


@dataclass
class Moments:
    count: int
    sum: np.ndarray
    sumsq: np.ndarray

    @classmethod
    def empty(cls, width: int) -> "Moments":
        return cls(0, np.zeros(width, dtype=np.float64), np.zeros(width, dtype=np.float64))

    def update(self, values: np.ndarray) -> None:
        values64 = np.asarray(values, dtype=np.float64)
        values64 = values64.reshape(-1, values64.shape[-1])
        self.count += values64.shape[0]
        self.sum += values64.sum(axis=0, dtype=np.float64)
        self.sumsq += np.square(values64).sum(axis=0, dtype=np.float64)

    def stats(self) -> tuple[np.ndarray, np.ndarray]:
        if self.count < 2:
            raise ValueError("insufficient values")
        mean = self.sum / self.count
        variance = np.maximum(0.0, self.sumsq / self.count - np.square(mean))
        return mean, np.sqrt(variance)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fixed_list_to_numpy(column, width: int) -> np.ndarray:
    arr = column.combine_chunks()
    if not hasattr(arr, "offsets") or not hasattr(arr, "values"):
        raise TypeError(f"expected Arrow list column, got {arr.type}")
    offsets = arr.offsets.to_numpy(zero_copy_only=False)
    lengths = np.diff(offsets)
    if lengths.size and not np.all(lengths == width):
        raise ValueError(f"list width drift: expected {width}, observed {np.unique(lengths).tolist()}")
    values = arr.values.to_numpy(zero_copy_only=False)
    return np.asarray(values).reshape(len(arr), width)


def transform_state(raw_state: np.ndarray) -> np.ndarray:
    raw_state = np.asarray(raw_state)
    if raw_state.ndim != 2 or raw_state.shape[1] != STATE_WIDTH_RAW:
        raise ValueError(f"raw state shape drift: {raw_state.shape}")
    result = np.concatenate(
        [
            raw_state[:, 0:3],
            raw_state[:, 53:57],
            raw_state[:, 3:10],
            raw_state[:, 24:26].sum(axis=-1, keepdims=True),
            raw_state[:, 28:35],
            raw_state[:, 49:51].sum(axis=-1, keepdims=True),
        ],
        axis=-1,
    )
    if result.shape[1] != STATE_WIDTH:
        raise RuntimeError(f"transformed state width drift: {result.shape}")
    return result


def transformed_action_horizon(raw_actions: np.ndarray, state: np.ndarray, start_count: int, t: int) -> np.ndarray:
    if not (0 <= t < ACTION_HORIZON):
        raise ValueError(t)
    if start_count < 0 or start_count > len(raw_actions):
        raise ValueError("invalid start_count")
    indices = np.arange(start_count, dtype=np.int64) + t
    np.minimum(indices, len(raw_actions) - 1, out=indices)
    actions = np.asarray(raw_actions[indices]).copy()
    for action_indices, state_indices in DELTA_MAPPINGS:
        actions[:, action_indices] -= state[:start_count, state_indices]
    return actions


def accumulate_episode(
    raw_state: np.ndarray,
    raw_actions: np.ndarray,
    start_count: int,
    state_moments: Moments,
    action_moments: Moments,
) -> None:
    if raw_actions.shape != (len(raw_state), ACTION_WIDTH):
        raise ValueError(f"action shape drift: {raw_actions.shape}")
    state = transform_state(raw_state)
    state_moments.update(state[:start_count])
    for t in range(ACTION_HORIZON):
        action_moments.update(transformed_action_horizon(raw_actions, state, start_count, t))


def brute_force_episode(raw_state: np.ndarray, raw_actions: np.ndarray, start_count: int) -> tuple[np.ndarray, np.ndarray]:
    state = transform_state(raw_state)[:start_count]
    actions = np.stack(
        [transformed_action_horizon(raw_actions, transform_state(raw_state), start_count, t) for t in range(ACTION_HORIZON)],
        axis=1,
    )
    return state, actions


def file_key_from_episode_row(row: dict) -> tuple[int, int]:
    return int(row["data/chunk_index"]), int(row["data/file_index"])


def data_path_from_key(root: Path, key: tuple[int, int]) -> Path:
    chunk, file_idx = key
    return root / f"data/chunk-{chunk:03d}/file-{file_idx:03d}.parquet"


def process_dataset(runtime_root: Path, metadata, expected_episodes: list[int]) -> tuple[Moments, Moments, dict]:
    episode_rows = {episode: metadata.episodes[episode] for episode in expected_episodes}
    file_to_episodes: dict[tuple[int, int], list[int]] = {}
    for episode in expected_episodes:
        file_to_episodes.setdefault(file_key_from_episode_row(episode_rows[episode]), []).append(episode)

    state_moments = Moments.empty(STATE_WIDTH)
    action_moments = Moments.empty(ACTION_WIDTH)
    total_frames = 0
    included_remaining = EXPECTED_INCLUDED_STARTS
    processed_episodes: list[int] = []
    processed_files: list[str] = []
    trailing_dropped_by_episode: dict[str, int] = {}

    for file_key in sorted(file_to_episodes):
        path = data_path_from_key(runtime_root, file_key)
        if not path.is_file():
            raise FileNotFoundError(path)
        table = pq.read_table(path, columns=["episode_index", "observation.state", "action"])
        episode_ids = table.column("episode_index").combine_chunks().to_numpy(zero_copy_only=False).astype(np.int64)
        raw_states = fixed_list_to_numpy(table.column("observation.state"), STATE_WIDTH_RAW)
        raw_actions = fixed_list_to_numpy(table.column("action"), ACTION_WIDTH)
        processed_files.append(str(path.relative_to(runtime_root)))

        boundaries = np.flatnonzero(np.r_[True, episode_ids[1:] != episode_ids[:-1], True])
        observed_groups: dict[int, tuple[int, int]] = {}
        for start, end in zip(boundaries[:-1], boundaries[1:], strict=True):
            ep = int(episode_ids[start])
            if np.any(episode_ids[start:end] != ep):
                raise RuntimeError("episode rows not contiguous")
            observed_groups[ep] = (int(start), int(end))

        for episode in file_to_episodes[file_key]:
            if episode not in observed_groups:
                raise RuntimeError(f"selected episode {episode} absent from {path}")
            start, end = observed_groups[episode]
            length = end - start
            expected_length = int(episode_rows[episode]["length"])
            if length != expected_length:
                raise RuntimeError(f"episode length drift for {episode}: {length} != {expected_length}")
            total_frames += length
            start_count = min(length, included_remaining)
            if start_count > 0:
                accumulate_episode(
                    raw_states[start:end],
                    raw_actions[start:end],
                    start_count,
                    state_moments,
                    action_moments,
                )
                included_remaining -= start_count
            dropped = length - start_count
            if dropped:
                trailing_dropped_by_episode[str(episode)] = dropped
            processed_episodes.append(episode)

    if processed_episodes != expected_episodes:
        raise RuntimeError("selected episode traversal order drift")
    if total_frames != EXPECTED_DATASET_FRAMES:
        raise RuntimeError(f"dataset frame count drift: {total_frames}")
    if included_remaining != 0:
        raise RuntimeError(f"did not consume expected included starts: {included_remaining}")
    if state_moments.count != EXPECTED_INCLUDED_STARTS:
        raise RuntimeError(f"state count drift: {state_moments.count}")
    if action_moments.count != EXPECTED_ACTION_VECTORS:
        raise RuntimeError(f"action count drift: {action_moments.count}")

    audit = {
        "data_file_count": len(processed_files),
        "processed_files": processed_files,
        "processed_episode_count": len(processed_episodes),
        "dataset_frame_count": total_frames,
        "included_start_count": state_moments.count,
        "action_vector_count": action_moments.count,
        "trailing_dropped_by_episode": trailing_dropped_by_episode,
    }
    return state_moments, action_moments, audit


def main() -> int:
    parser = argparse.ArgumentParser(description="Source-equivalent state/action-only z-score statistics for frozen shared26")
    parser.add_argument("--frozen-child", type=Path, required=True)
    parser.add_argument("--sample-qualification", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.receipt.exists() or args.output_dir.exists():
        raise FileExistsError("refusing to overwrite normalization output or receipt")
    if os.environ.get("HF_HUB_OFFLINE") != "1":
        raise RuntimeError("HF_HUB_OFFLINE=1 required")

    sample_q = json.loads(args.sample_qualification.read_text(encoding="utf-8"))
    if sample_q.get("status") != "PI05_RGB_SAMPLE_SCHEMA_QUALIFICATION_PASS":
        raise ValueError("repair2 sample qualification is not PASS")
    frozen = json.loads(args.frozen_child.read_text(encoding="utf-8"))
    expected_episodes = frozen["child_config"]["dataset_kwargs"]["episodes"]
    if len(expected_episodes) != 5200 or len(set(expected_episodes)) != 5200:
        raise ValueError("frozen episode subset drift")

    from lerobot.datasets import LeRobotDatasetMetadata

    lock_path = args.output_dir.parent / ".behavior-formal-goal-shared26-fast-norm.lock"
    with lock_path.open("a+") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"normalization actor already holds {lock_path}") from exc
        metadata = LeRobotDatasetMetadata("behavior-1k/2026-challenge-demos", root=RUNTIME_ROOT)
        state_moments, action_moments, audit = process_dataset(RUNTIME_ROOT, metadata, expected_episodes)
        state_mean, state_std = state_moments.stats()
        action_mean, action_std = action_moments.stats()

        norm_stats = {
            "state": normalize.NormStats(mean=state_mean, std=state_std, q01=None, q99=None),
            "actions": normalize.NormStats(mean=action_mean, std=action_std, q01=None, q99=None),
        }
        normalize.save(args.output_dir, norm_stats)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    norm_path = args.output_dir / "norm_stats.json"
    receipt = {
        "schema_version": "behavior-formal-goal-coupling-shared26-fast-norm-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "status": "SOURCE_EQUIVALENT_ZSCORE_NORMALIZATION_COMPLETE",
        "frozen_child_path": str(args.frozen_child),
        "frozen_child_sha256": sha256_file(args.frozen_child),
        "sample_qualification_path": str(args.sample_qualification),
        "sample_qualification_sha256": sha256_file(args.sample_qualification),
        "runtime_root": str(RUNTIME_ROOT),
        "batch_size": BATCH_SIZE,
        "drop_last": True,
        "action_horizon": ACTION_HORIZON,
        **audit,
        "state_mean": state_mean.tolist(),
        "state_std": state_std.tolist(),
        "actions_mean": action_mean.tolist(),
        "actions_std": action_std.tolist(),
        "q01_q99": "omitted/null because frozen B1K child uses z-score normalization (use_quantile_norm=false); these fields are operationally unused",
        "norm_stats_path": str(norm_path),
        "norm_stats_sha256": sha256_file(norm_path),
        "rgb_decode_skipped": True,
        "reason_rgb_decode_can_be_skipped": "Pinned compute_norm_stats accumulates only state/actions; R1Pro state extraction and mapped delta actions are independent of image tensors.",
        "network_access_used": False,
        "model_checkpoint_weight_downloaded": False,
        "model_loaded": False,
        "gpu_used": False,
        "training_started": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_authority": False,
        "next_gate": "INSTALL_NORM_ASSET_AND_ZERO_UPDATE_B1K_DATALOADER_SMOKE",
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "included_start_count": receipt["included_start_count"],
        "action_vector_count": receipt["action_vector_count"],
        "norm_stats_sha256": receipt["norm_stats_sha256"],
        "trailing_dropped_by_episode": receipt["trailing_dropped_by_episode"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
