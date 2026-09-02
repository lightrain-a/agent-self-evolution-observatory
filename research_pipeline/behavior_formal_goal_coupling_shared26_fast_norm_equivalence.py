from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

import openpi.training.config as config_lib
import openpi.training.data_loader as data_loader

import behavior_formal_goal_coupling_shared26_fast_norm as fast_norm

OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL"
CONFIG_NAME = "pi05_b1k_shared26_frozen"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fast_state_actions(base, relative_index: int) -> tuple[np.ndarray, np.ndarray]:
    item = base.reader.hf_dataset[relative_index]
    ep_idx = int(item["episode_index"].item())
    abs_idx = int(item["index"].item())
    query_indices, _ = base.reader._get_query_indices(abs_idx, ep_idx)
    query = base.reader._query_hf_dataset(query_indices)
    raw_state = np.asarray(item["observation.state"], dtype=np.float32).reshape(1, -1)
    state = fast_norm.transform_state(raw_state)[0]
    actions = np.asarray(query["action"], dtype=np.float32).copy()
    for action_indices, state_indices in fast_norm.DELTA_MAPPINGS:
        actions[:, action_indices] -= state[list(state_indices)]
    return state, actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Real-data equivalence check for accelerated shared26 z-score normalization")
    parser.add_argument("--frozen-child", type=Path, required=True)
    parser.add_argument("--repair2-sample", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.receipt.exists():
        raise FileExistsError(args.receipt)
    if os.environ.get("HF_HUB_OFFLINE") != "1":
        raise RuntimeError("HF_HUB_OFFLINE=1 required")

    frozen = json.loads(args.frozen_child.read_text(encoding="utf-8"))
    episodes = frozen["child_config"]["dataset_kwargs"]["episodes"]
    repair2 = json.loads(args.repair2_sample.read_text(encoding="utf-8"))
    if repair2.get("status") != "PI05_RGB_SAMPLE_SCHEMA_QUALIFICATION_PASS":
        raise ValueError("repair2 sample qualification not PASS")

    cfg = config_lib.get_config(CONFIG_NAME)
    data_cfg = cfg.data.create(cfg.assets_dirs, cfg.model)
    dataset = data_loader.create_b1k_dataset(data_cfg, cfg.model.action_horizon)
    base = dataset._dataset if hasattr(dataset, "_dataset") else dataset
    full_dataset = data_loader.TransformedDataset(
        dataset,
        [*data_cfg.repack_transforms.inputs, *data_cfg.data_transforms.inputs],
    )

    offsets: dict[int, int] = {}
    cursor = 0
    for ep in episodes:
        offsets[ep] = cursor
        cursor += int(base.meta.episodes[ep]["length"])
    if cursor != fast_norm.EXPECTED_DATASET_FRAMES:
        raise RuntimeError(f"frame count drift: {cursor}")

    representative_episodes = episodes[::200]
    if len(representative_episodes) != 26:
        raise RuntimeError("expected one representative episode per frozen task")
    indices: list[tuple[int, int, str]] = []
    for ep in representative_episodes:
        length = int(base.meta.episodes[ep]["length"])
        indices.append((ep, offsets[ep], "first"))
        indices.append((ep, offsets[ep] + length - 1, "last"))

    rows = []
    max_state_abs = 0.0
    max_action_abs = 0.0
    for ep, idx, boundary in indices:
        full = full_dataset[idx]
        fast_state, fast_actions = fast_state_actions(base, idx)
        full_state = np.asarray(full["state"])
        full_actions = np.asarray(full["actions"])
        state_abs = float(np.max(np.abs(full_state.astype(np.float64) - fast_state.astype(np.float64))))
        action_abs = float(np.max(np.abs(full_actions.astype(np.float64) - fast_actions.astype(np.float64))))
        max_state_abs = max(max_state_abs, state_abs)
        max_action_abs = max(max_action_abs, action_abs)
        rows.append(
            {
                "episode": ep,
                "relative_index": idx,
                "boundary": boundary,
                "state_max_abs": state_abs,
                "actions_max_abs": action_abs,
                "state_shape": list(full_state.shape),
                "actions_shape": list(full_actions.shape),
            }
        )

    passed = max_state_abs == 0.0 and max_action_abs == 0.0
    receipt = {
        "schema_version": "behavior-formal-goal-coupling-shared26-fast-norm-equivalence-v1",
        "object_id": OBJECT_ID,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "status": "FAST_NORM_REAL_SOURCE_EQUIVALENCE_PASS" if passed else "FAST_NORM_REAL_SOURCE_EQUIVALENCE_HOLD",
        "frozen_child_sha256": sha256_file(args.frozen_child),
        "repair2_sample_sha256": sha256_file(args.repair2_sample),
        "representative_task_count": 26,
        "comparison_sample_count": len(rows),
        "coverage": "first and last frame of the first selected episode for each frozen task; last-frame cases exercise 32-step end padding",
        "max_state_abs_difference": max_state_abs,
        "max_actions_abs_difference": max_action_abs,
        "comparisons": rows,
        "hf_hub_offline": True,
        "model_checkpoint_weight_downloaded": False,
        "model_loaded": False,
        "gpu_used": False,
        "training_started": False,
        "policy_rollouts_started": False,
        "policy_outcomes_read": False,
        "scientific_authority": False,
        "next_gate_if_pass": "FULL_ACCELERATED_ZSCORE_NORMALIZATION",
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "comparison_sample_count": len(rows),
        "max_state_abs_difference": max_state_abs,
        "max_actions_abs_difference": max_action_abs,
    }, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
