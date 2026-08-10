from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
from typing import Any

from .alfworld_react_scaffold import task_family_from_gamefile
from .p0_common import load_json, load_jsonl

FEATURE_KEYS = (
    "action_sequence_distance",
    "invalid_action_rate",
    "instruction_choice_shift",
    "plan_length",
)


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


def _fit(features: list[list[float]], labels: list[int]) -> dict[str, Any]:
    if len(set(labels)) < 2:
        raise ValueError("A1-R2 classifier requires both harmful and non-harmful updates")
    dims = len(features[0])
    mu = [_mean([row[j] for row in features]) for j in range(dims)]
    sd: list[float] = []
    for j in range(dims):
        variance = _mean([(row[j] - mu[j]) ** 2 for row in features])
        value = math.sqrt(variance)
        sd.append(value if value >= 1e-9 else 1.0)
    z = [[(row[j] - mu[j]) / sd[j] for j in range(dims)] for row in features]
    pos = [row for row, label in zip(z, labels) if label]
    neg = [row for row, label in zip(z, labels) if not label]
    weights = [_mean([row[j] for row in pos]) - _mean([row[j] for row in neg]) for j in range(dims)]
    return {"mu": mu, "sd": sd, "weights": weights}


def _score(model: dict[str, Any], feature: list[float]) -> float:
    return sum(
        ((feature[j] - model["mu"][j]) / model["sd"][j]) * model["weights"][j]
        for j in range(len(feature))
    )


def _loo_scores(features: list[list[float]], labels: list[int]) -> list[float]:
    scores: list[float] = []
    for holdout in range(len(features)):
        train_x = [row for index, row in enumerate(features) if index != holdout]
        train_y = [label for index, label in enumerate(labels) if index != holdout]
        if len(set(train_y)) < 2:
            return [0.0] * len(features)
        model = _fit(train_x, train_y)
        scores.append(_score(model, features[holdout]))
    return scores


def _leave_one_group_out_auc(features: list[list[float]], labels: list[int], groups: list[str]) -> float | None:
    scores: list[float | None] = [None] * len(features)
    for group in sorted(set(groups)):
        train_idx = [index for index, value in enumerate(groups) if value != group]
        test_idx = [index for index, value in enumerate(groups) if value == group]
        train_y = [labels[index] for index in train_idx]
        if len(set(train_y)) < 2:
            return None
        model = _fit([features[index] for index in train_idx], train_y)
        for index in test_idx:
            scores[index] = _score(model, features[index])
    return _auc(labels, [float(score) for score in scores]) if all(score is not None for score in scores) else None


def _perfect_threshold(labels: list[int], scores: list[float]) -> bool:
    values = sorted(set(scores))
    if not values:
        return False
    thresholds = [values[0] - 1.0] + [(a + b) / 2.0 for a, b in zip(values, values[1:])] + [values[-1] + 1.0]
    return any(all((score >= threshold) == bool(label) for label, score in zip(labels, scores)) for threshold in thresholds)


def _exact_label_permutation_p(features: list[list[float]], labels: list[int], observed_auc: float) -> float:
    n = len(labels)
    positives = sum(labels)
    if positives <= 0 or positives >= n:
        return 1.0
    exceed = 0
    total = 0
    for chosen in itertools.combinations(range(n), positives):
        perm = [0] * n
        for index in chosen:
            perm[index] = 1
        auc = _auc(perm, _loo_scores(features, perm))
        total += 1
        if auc + 1e-12 >= observed_auc:
            exceed += 1
    return exceed / total if total else 1.0


def _rows(evaluation_path: Path, patch_path: Path, config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[int], list[list[float]], list[list[float]], list[str]]:
    evaluations = load_jsonl(evaluation_path)
    patches = {str(row["candidate_id"]): row for row in load_jsonl(patch_path)}
    scales = (config.get("analysis") or {}).get("feature_scales") or {}
    weights = (config.get("analysis") or {}).get("drift_weights") or {}
    records: list[dict[str, Any]] = []
    labels: list[int] = []
    raw_features: list[list[float]] = []
    vector_features: list[list[float]] = []
    groups: list[str] = []
    for row in evaluations:
        candidate_id = str(row["candidate_id"])
        patch = patches.get(candidate_id) or {}
        before = row.get("probe_features_before") or {}
        after = row.get("probe_features_after") or {}
        vector = []
        weighted = 0.0
        total_weight = 0.0
        for key in FEATURE_KEYS:
            scale = float(scales.get(key, 1.0)) or 1.0
            delta = abs(float(after.get(key, 0.0)) - float(before.get(key, 0.0))) / scale
            vector.append(delta)
            weight = float(weights.get(key, 0.25))
            weighted += weight * delta
            total_weight += weight
        hidden_before = [float(value) for value in row.get("hidden_before") or []]
        hidden_after = [float(value) for value in row.get("hidden_after") or []]
        hidden_delta = _mean([after_value - before_value for before_value, after_value in zip(hidden_before, hidden_after)])
        harmful = int(hidden_delta < -0.02)
        source = str(patch.get("source_task_id") or "")
        family = task_family_from_gamefile(source) if source else "unknown"
        current_gain = float(row.get("current_task_gain") or 0.0)
        raw = [current_gain, weighted / total_weight if total_weight else weighted]
        component = [current_gain] + vector
        records.append({"candidate_id": candidate_id, "source_task_family": family, "harmful": harmful, "hidden_delta": hidden_delta, "raw_behavior_drift": raw[1], "component_drift": dict(zip(FEATURE_KEYS, vector))})
        labels.append(harmful)
        raw_features.append(raw)
        vector_features.append(component)
        groups.append(family)
    return records, labels, raw_features, vector_features, groups


def analyze(evaluation_path: Path, patch_path: Path, config_path: Path) -> dict[str, Any]:
    config = load_json(config_path)
    records, labels, raw_features, vector_features, groups = _rows(evaluation_path, patch_path, config)
    if len(records) < 16:
        return {"pass": False, "decision": "INCONCLUSIVE", "reason": "requires-all-16-screening-candidates", "candidate_count": len(records), "scientific_result_available": False}
    harmful = sum(labels)
    if harmful < 4 or harmful >= len(labels):
        return {"pass": False, "decision": "INCONCLUSIVE", "reason": "insufficient-harmful-label-variation", "candidate_count": len(records), "harmful_candidates": harmful, "scientific_result_available": False}

    raw_auc = _auc(labels, _loo_scores(raw_features, labels))
    vector_scores = _loo_scores(vector_features, labels)
    vector_auc = _auc(labels, vector_scores)
    family_loo_auc = _leave_one_group_out_auc(vector_features, labels, groups)
    increment = vector_auc - raw_auc

    tiny_n = 12
    tiny_x = vector_features[:tiny_n]
    tiny_y = labels[:tiny_n]
    tiny_model = _fit(tiny_x, tiny_y)
    tiny_scores = [_score(tiny_model, row) for row in tiny_x]
    tiny_auc = _auc(tiny_y, tiny_scores)
    tiny_perfect = _perfect_threshold(tiny_y, tiny_scores)
    permutation_p = _exact_label_permutation_p(vector_features, labels, vector_auc)

    representability_pass = vector_auc > 0.65
    incrementality_pass = increment >= 0.05
    family_generalization_pass = family_loo_auc is not None and family_loo_auc >= 0.60
    tiny_pass = tiny_auc >= 0.95 and tiny_perfect
    chance_pass = permutation_p <= 0.10
    passed = representability_pass and incrementality_pass and family_generalization_pass and tiny_pass and chance_pass
    return {
        "schema_version": "1.0",
        "artifact_kind": "pre-experiment-repair-audit",
        "repair_id": "A1-R2-component-wise-divergence",
        "changed_variable": "representation only: replace one global weighted drift scalar with the frozen component-wise probe-divergence vector; source task family is used only for held-out-group auditing, not as a model feature",
        "candidate_count": len(records),
        "harmful_candidates": harmful,
        "raw_scalar_leave_one_update_out_auc": raw_auc,
        "component_vector_leave_one_update_out_auc": vector_auc,
        "incremental_auc_over_raw_scalar": increment,
        "leave_one_source_task_family_out_auc": family_loo_auc,
        "exact_label_permutation_p": permutation_p,
        "tiny_real_subset": {"selection": "first 12 frozen screening candidates", "n": tiny_n, "harmful": sum(tiny_y), "training_auc": tiny_auc, "perfect_threshold_exists": tiny_perfect, "pass": tiny_pass},
        "gates": {
            "representability": {"threshold": 0.65, "pass": representability_pass},
            "incrementality": {"threshold": 0.05, "pass": incrementality_pass},
            "leave_one_family_generalization": {"threshold": 0.60, "pass": family_generalization_pass},
            "chance_control": {"maximum_p": 0.10, "pass": chance_pass},
            "tiny_overfit": {"pass": tiny_pass},
        },
        "candidate_records": records,
        "pass": passed,
        "decision": "QUALIFICATION-PASS" if passed else "QUALIFICATION-FAIL",
        "scientific_result_available": False,
        "pilot_registry_write_forbidden": True,
        "next_action": "unlock-A1-screening-repair-gate" if passed else "do-not-launch-formal-P0; revise-or-simplify-representation",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="A1-R2 component-wise divergence audit on a completed A-1 screening run.")
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--patches", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = analyze(args.evaluation, args.patches, args.config)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.output.with_suffix(args.output.suffix + ".tmp")
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
