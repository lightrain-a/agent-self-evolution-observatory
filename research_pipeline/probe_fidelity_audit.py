from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .alfworld_react_scaffold import task_family_from_gamefile
from .p0_a1 import _candidate
from .p0_alfworld_adapter import normalized_edit_distance
from .p0_common import load_json


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _auc(labels: list[int], scores: list[float]) -> float:
    pos = [score for label, score in zip(labels, scores) if label == 1]
    neg = [score for label, score in zip(labels, scores) if label == 0]
    if not pos or not neg:
        return 0.5
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p > n else 0.5 if p == n else 0.0
    return wins / (len(pos) * len(neg))


def _standardized_mean_difference_loo(features: list[list[float]], labels: list[int]) -> float:
    predictions: list[float] = []
    for holdout in range(len(features)):
        train_x = [row for index, row in enumerate(features) if index != holdout]
        train_y = [label for index, label in enumerate(labels) if index != holdout]
        if len(set(train_y)) < 2:
            return 0.5
        dims = len(train_x[0])
        mu = [_mean([row[j] for row in train_x]) for j in range(dims)]
        sd = []
        for j in range(dims):
            variance = _mean([(row[j] - mu[j]) ** 2 for row in train_x])
            value = math.sqrt(variance)
            sd.append(value if value >= 1e-9 else 1.0)
        z = [[(row[j] - mu[j]) / sd[j] for j in range(dims)] for row in train_x]
        positive = [row for row, label in zip(z, train_y) if label == 1]
        negative = [row for row, label in zip(z, train_y) if label == 0]
        weights = [
            _mean([row[j] for row in positive]) - _mean([row[j] for row in negative])
            for j in range(dims)
        ]
        test = features[holdout]
        predictions.append(sum(((test[j] - mu[j]) / sd[j]) * weights[j] for j in range(dims)))
    return _auc(labels, predictions)


def build(run_dir: Path, config_path: Path) -> dict[str, Any]:
    config = load_json(config_path)
    eval_rows = _read_jsonl(run_dir / "candidate-evaluation.jsonl")
    patch_rows = _read_jsonl(run_dir / "candidate-patches.jsonl")
    raw_rows = _read_jsonl(run_dir / "raw-traces.jsonl")
    patches = {str(row["candidate_id"]): row for row in patch_rows}
    candidates = [_candidate(row, config) for row in eval_rows]
    candidate_ids = [row.candidate_id for row in candidates]
    labels = [int(row.harmful) for row in candidates]

    baseline = {
        str(row["trace"]["task_id"]): row["trace"]
        for row in raw_rows
        if row.get("role") == "behavior-probe-baseline"
    }
    candidate_probe: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in raw_rows:
        if row.get("role") != "candidate-probe":
            continue
        candidate_id = str(row.get("candidate_id") or "")
        if candidate_id in set(candidate_ids):
            candidate_probe[candidate_id][str(row["trace"]["task_id"])] = row["trace"]

    probe_rows: list[dict[str, Any]] = []
    per_candidate_vectors: dict[str, list[float]] = {candidate_id: [] for candidate_id in candidate_ids}
    for task_id, before in baseline.items():
        action_scores: list[float] = []
        length_scores: list[float] = []
        invalid_scores: list[float] = []
        success_losses: list[float] = []
        for candidate_id in candidate_ids:
            after = candidate_probe[candidate_id].get(task_id)
            if after is None:
                raise ValueError(f"candidate {candidate_id} missing fixed probe {task_id}")
            action = normalized_edit_distance(list(before["actions"]), list(after["actions"]))
            length = abs(float(after["steps"]) - float(before["steps"])) / max(float(before.get("step_cap") or 50), 1.0)
            invalid = float(after.get("invalid_choice_rate") or 0.0) - float(before.get("invalid_choice_rate") or 0.0)
            success_loss = float(float(before.get("success") or 0.0) > float(after.get("success") or 0.0))
            action_scores.append(action)
            length_scores.append(length)
            invalid_scores.append(invalid)
            success_losses.append(success_loss)
            per_candidate_vectors[candidate_id].append(action)
        probe_rows.append({
            "task_id": task_id,
            "task_family": str(before.get("task_family") or task_family_from_gamefile(task_id)),
            "baseline_success": float(before.get("success") or 0.0),
            "action_distance_auc": _auc(labels, action_scores),
            "length_change_auc": _auc(labels, length_scores),
            "invalid_change_auc": _auc(labels, invalid_scores),
            "success_loss_events": int(sum(success_losses)),
            "mean_action_distance_harmful": _mean([score for score, label in zip(action_scores, labels) if label == 1]),
            "mean_action_distance_nonharmful": _mean([score for score, label in zip(action_scores, labels) if label == 0]),
        })

    aggregate_features: list[list[float]] = []
    for candidate in candidates:
        patch = patches[candidate.candidate_id]
        probe_vector = per_candidate_vectors[candidate.candidate_id]
        aggregate_features.append([
            float(candidate.current_task_gain),
            float(candidate.behavior_drift),
            float(patch.get("edit_size") or 0.0) / 16.0,
            _mean(probe_vector),
            max(probe_vector) if probe_vector else 0.0,
        ])
    panel_auc = _standardized_mean_difference_loo(aggregate_features, labels)
    best_probe_auc = max((float(row["action_distance_auc"]) for row in probe_rows), default=0.5)
    minimum_auc = 0.65
    pass_panel = panel_auc >= minimum_auc or best_probe_auc >= minimum_auc
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "artifact_kind": "probe-fidelity-development-audit",
        "run_dir": str(run_dir),
        "candidate_count": len(candidates),
        "harmful_candidates": int(sum(labels)),
        "harmful_prevalence": _mean([float(label) for label in labels]),
        "fixed_probe_count": len(probe_rows),
        "probe_rows": probe_rows,
        "aggregate_panel_leave_one_candidate_out_auc": panel_auc,
        "best_single_probe_action_auc": best_probe_auc,
        "minimum_fidelity_auc": minimum_auc,
        "fidelity_pass": pass_panel,
        "diagnosis": (
            "At least one fixed-probe signal clears the development fidelity threshold; freeze the representation and validate it on a fresh candidate batch before scientific use."
            if pass_panel else
            "The fixed probe panel does not predict hidden harmful regression on this development batch; replace or learn the probe panel before another A-1 scientific launch."
        ),
        "scientific_role": "development/repair evidence only; this batch may be used to design the next probe panel but cannot validate a panel selected from itself",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit whether fixed behavior probes predict hidden harmful updates.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build(args.run_dir, args.config)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
