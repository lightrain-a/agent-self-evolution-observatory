from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


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


def _standardize_fit(rows: list[list[float]]) -> tuple[list[float], list[float], list[list[float]]]:
    dims = len(rows[0]) if rows else 0
    mu = [_mean([row[j] for row in rows]) for j in range(dims)]
    sd = []
    for j in range(dims):
        variance = _mean([(row[j] - mu[j]) ** 2 for row in rows])
        value = math.sqrt(variance)
        sd.append(value if value >= 1e-9 else 1.0)
    z = [[(row[j] - mu[j]) / sd[j] for j in range(dims)] for row in rows]
    return mu, sd, z


def _mean_difference_fit(features: list[list[float]], labels: list[int]) -> dict[str, Any]:
    if len(set(labels)) < 2:
        raise ValueError("mean-difference classifier requires both classes")
    mu, sd, z = _standardize_fit(features)
    positive = [row for row, label in zip(z, labels) if label == 1]
    negative = [row for row, label in zip(z, labels) if label == 0]
    dims = len(z[0])
    weights = [
        _mean([row[j] for row in positive]) - _mean([row[j] for row in negative])
        for j in range(dims)
    ]
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
        model = _mean_difference_fit(train_x, train_y)
        scores.append(_score(model, features[holdout]))
    return scores


def _leave_one_group_out_auc(features: list[list[float]], labels: list[int], groups: list[str]) -> float | None:
    scores: list[float | None] = [None] * len(features)
    for group in sorted(set(groups)):
        train_index = [index for index, value in enumerate(groups) if value != group]
        test_index = [index for index, value in enumerate(groups) if value == group]
        train_y = [labels[index] for index in train_index]
        if len(set(train_y)) < 2:
            return None
        model = _mean_difference_fit([features[index] for index in train_index], train_y)
        for index in test_index:
            scores[index] = _score(model, features[index])
    if any(score is None for score in scores):
        return None
    return _auc(labels, [float(score) for score in scores])


def _perfect_threshold_exists(labels: list[int], scores: list[float]) -> bool:
    candidates = sorted(set(scores))
    thresholds = [candidates[0] - 1.0] if candidates else [0.0]
    thresholds += [(a + b) / 2.0 for a, b in zip(candidates, candidates[1:])]
    thresholds += [candidates[-1] + 1.0] if candidates else []
    return any(all((score >= threshold) == bool(label) for label, score in zip(labels, scores)) for threshold in thresholds)


def _a1_features(updates: list[dict[str, Any]]) -> tuple[list[list[float]], list[str]]:
    surfaces = sorted({str(row.get("surface") or "") for row in updates})
    targets = sorted({str(row.get("target") or "") for row in updates})
    names = ["current_gain", "raw_behavior_drift"] + [f"surface={x}" for x in surfaces] + [f"target={x}" for x in targets]
    features: list[list[float]] = []
    for row in updates:
        features.append(
            [float(row.get("gain") or 0.0), float(row.get("drift") or 0.0)]
            + [1.0 if str(row.get("surface") or "") == x else 0.0 for x in surfaces]
            + [1.0 if str(row.get("target") or "") == x else 0.0 for x in targets]
        )
    return features, names


def audit_a1(decision: dict[str, Any]) -> dict[str, Any]:
    updates = list(((decision.get("a1") or {}).get("updates")) or [])
    if len(updates) < 12:
        raise ValueError("A1-R1 requires at least 12 frozen updates")
    labels = [int(row.get("harmful") or 0) for row in updates]
    features, names = _a1_features(updates)
    raw_features = [row[:2] for row in features]
    context_features = [row[2:] for row in features]
    loo_auc = _auc(labels, _loo_scores(features, labels))
    raw_only_loo_auc = _auc(labels, _loo_scores(raw_features, labels))
    context_only_loo_auc = _auc(labels, _loo_scores(context_features, labels))
    surface_group_auc = _leave_one_group_out_auc(features, labels, [str(row.get("surface") or "") for row in updates])
    target_group_auc = _leave_one_group_out_auc(features, labels, [str(row.get("target") or "") for row in updates])

    tiny_n = 12
    tiny_x = features[:tiny_n]
    tiny_y = labels[:tiny_n]
    tiny_model = _mean_difference_fit(tiny_x, tiny_y)
    tiny_scores = [_score(tiny_model, row) for row in tiny_x]
    tiny_auc = _auc(tiny_y, tiny_scores)
    tiny_perfect = _perfect_threshold_exists(tiny_y, tiny_scores)
    pass_representability = loo_auc > 0.65
    pass_tiny = tiny_auc >= 0.95 and tiny_perfect
    incremental_signal = loo_auc - max(raw_only_loo_auc, context_only_loo_auc)
    context_not_sufficient = context_only_loo_auc < 0.65
    pass_robustness = context_not_sufficient and incremental_signal >= 0.05
    return {
        "repair_id": "A1-R1-contextual-divergence",
        "changed_variable": "representation only: add frozen update-surface and update-target context to current gain + raw drift",
        "feature_names": names,
        "learner": "fixed standardized class-mean-difference linear score; no hyperparameter search",
        "frozen_updates": len(updates),
        "harmful_updates": sum(labels),
        "leave_one_update_out_auc": loo_auc,
        "raw_only_leave_one_update_out_auc": raw_only_loo_auc,
        "context_only_leave_one_update_out_auc": context_only_loo_auc,
        "incremental_auc_over_best_ablation": incremental_signal,
        "leave_one_surface_out_auc": surface_group_auc,
        "leave_one_target_out_auc": target_group_auc,
        "representability_threshold": 0.65,
        "representability_pass": pass_representability,
        "context_only_leakage_check_pass": context_not_sufficient,
        "representation_incrementality_pass": pass_robustness,
        "tiny_real_subset": {
            "selection": "first 12 frozen updates in canonical order",
            "n": tiny_n,
            "harmful": sum(tiny_y),
            "training_auc": tiny_auc,
            "perfect_separating_threshold_exists": tiny_perfect,
            "pass": pass_tiny,
        },
        "pass": pass_representability and pass_tiny and pass_robustness,
        "scientific_role": "offline pre-experiment repair evidence only; does not constitute an A-1 method result",
    }


def _a2_sequence_rows(evaluations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [row for row in evaluations if row.get("stage") == "a2-sequences"]
    base_rows = [row for row in rows if row.get("context_id") == "base"]
    if not base_rows:
        raise ValueError("A2-R1 missing base evaluations")
    base_reward = _mean([float(row.get("reward") or 0.0) for row in base_rows])
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    sequence_ids: set[int] = set()
    for row in rows:
        match = re.fullmatch(r"s(\d+)-r(\d+)", str(row.get("context_id") or ""))
        if not match:
            continue
        sequence_id, round_id = int(match.group(1)), int(match.group(2))
        grouped[(sequence_id, round_id)].append(row)
        sequence_ids.add(sequence_id)
    output: list[dict[str, Any]] = []
    for sequence_id in sorted(sequence_ids):
        previous = base_reward
        rounds: list[dict[str, Any]] = []
        for round_id in range(1, 5):
            group = grouped.get((sequence_id, round_id)) or []
            if not group:
                raise ValueError(f"A2-R1 incomplete sequence s{sequence_id:02d}, round {round_id}")
            reward = _mean([float(row.get("reward") or 0.0) for row in group])
            rounds.append({
                "round": round_id,
                "reward": reward,
                "marginal_gain": reward - previous,
                "probe_regression": max(0.0, previous - reward),
            })
            previous = reward
        utilities = [row["reward"] - 0.02 * row["round"] for row in rounds]
        best_round = max(range(4), key=lambda index: utilities[index]) + 1
        output.append({"sequence": sequence_id, "best_round": best_round, "rounds": rounds})
    return output


def _entropy(labels: list[int]) -> float:
    counts = Counter(labels)
    total = len(labels)
    return -sum((count / total) * math.log2(count / total) for count in counts.values()) if total else 0.0


def _a2_feature(round_row: dict[str, Any]) -> list[float]:
    return [
        float(round_row["marginal_gain"]),
        float(round_row["probe_regression"]),
        float(round_row["reward"]),
        float(round_row["round"]) / 4.0,
    ]


def _fit_a2_model(sequences: list[dict[str, Any]], excluded_sequence: int | None = None) -> dict[str, Any]:
    features: list[list[float]] = []
    labels: list[int] = []
    for sequence in sequences:
        if excluded_sequence is not None and int(sequence["sequence"]) == excluded_sequence:
            continue
        for row in sequence["rounds"][:-1]:
            features.append(_a2_feature(row))
            labels.append(1 if int(sequence["best_round"]) > int(row["round"]) else 0)
    return _mean_difference_fit(features, labels)


def _select_round(model: dict[str, Any], sequence: dict[str, Any]) -> int:
    for row in sequence["rounds"][:-1]:
        if _score(model, _a2_feature(row)) < 0.0:
            return int(row["round"])
    return 4


def _tuned_simple_round(train: list[dict[str, Any]], test: dict[str, Any]) -> int:
    grid = [-0.05, 0.0, 0.01, 0.02, 0.05, 0.10]
    best_threshold = grid[0]
    best_utility = -1e9
    for threshold in grid:
        utilities: list[float] = []
        for sequence in train:
            chosen = 4
            for row in sequence["rounds"][1:]:
                if float(row["marginal_gain"]) < threshold:
                    chosen = max(1, int(row["round"]) - 1)
                    break
            selected = sequence["rounds"][chosen - 1]
            utilities.append(float(selected["reward"]) - 0.02 * chosen)
        score = _mean(utilities)
        if score > best_utility:
            best_utility, best_threshold = score, threshold
    chosen = 4
    for row in test["rounds"][1:]:
        if float(row["marginal_gain"]) < best_threshold:
            chosen = max(1, int(row["round"]) - 1)
            break
    return chosen


def audit_a2(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    sequences = _a2_sequence_rows(evaluations)
    best_rounds = [int(sequence["best_round"]) for sequence in sequences]
    entropy = _entropy(best_rounds)
    jackknife_entropies = [_entropy(best_rounds[:index] + best_rounds[index + 1:]) for index in range(len(best_rounds))]
    jackknife_archetypes = [len(set(best_rounds[:index] + best_rounds[index + 1:])) for index in range(len(best_rounds))]

    loo_labels: list[int] = []
    loo_scores: list[float] = []
    learned_rounds: list[int] = []
    heuristic_rounds: list[int] = []
    for sequence in sequences:
        holdout = int(sequence["sequence"])
        train = [row for row in sequences if int(row["sequence"]) != holdout]
        model = _fit_a2_model(sequences, excluded_sequence=holdout)
        for row in sequence["rounds"][:-1]:
            loo_labels.append(1 if int(sequence["best_round"]) > int(row["round"]) else 0)
            loo_scores.append(_score(model, _a2_feature(row)))
        learned_rounds.append(_select_round(model, sequence))
        heuristic_rounds.append(_tuned_simple_round(train, sequence))
    loo_auc = _auc(loo_labels, loo_scores)
    disagreements = sum(a != b for a, b in zip(learned_rounds, heuristic_rounds))
    disagreement_details = [
        {"sequence": int(sequence["sequence"]), "oracle_round": int(sequence["best_round"]), "learned_round": learned, "heuristic_round": heuristic}
        for sequence, learned, heuristic in zip(sequences, learned_rounds, heuristic_rounds)
        if learned != heuristic
    ]
    def utility(sequence: dict[str, Any], round_id: int) -> float:
        row = sequence["rounds"][round_id - 1]
        return float(row["reward"]) - 0.02 * round_id
    learned_regrets = [utility(sequence, int(sequence["best_round"])) - utility(sequence, chosen) for sequence, chosen in zip(sequences, learned_rounds)]
    heuristic_regrets = [utility(sequence, int(sequence["best_round"])) - utility(sequence, chosen) for sequence, chosen in zip(sequences, heuristic_rounds)]

    tiny_sequences = sequences[:5]
    tiny_x: list[list[float]] = []
    tiny_y: list[int] = []
    for sequence in tiny_sequences:
        for row in sequence["rounds"][:-1]:
            tiny_x.append(_a2_feature(row))
            tiny_y.append(1 if int(sequence["best_round"]) > int(row["round"]) else 0)
    tiny_model = _mean_difference_fit(tiny_x, tiny_y)
    tiny_scores = [_score(tiny_model, row) for row in tiny_x]
    tiny_auc = _auc(tiny_y, tiny_scores)
    tiny_perfect = _perfect_threshold_exists(tiny_y, tiny_scores)

    target_pass = entropy >= 0.6 and len(set(best_rounds)) >= 3 and min(jackknife_entropies, default=0.0) >= 0.6 and min(jackknife_archetypes, default=0) >= 3
    disagreement_pass = disagreements >= 1 and loo_auc >= 0.65
    tiny_pass = tiny_auc >= 0.95 and tiny_perfect
    return {
        "repair_id": "A2-R1-sequence-archetype-qualification",
        "changed_variable": "qualification/splitting only; preserve frozen sequence outcomes and cost-aware optimal-round definition",
        "sequence_count": len(sequences),
        "optimal_round_counts": dict(sorted(Counter(best_rounds).items())),
        "optimal_round_entropy_bits": entropy,
        "minimum_entropy_bits": 0.6,
        "archetypes_present": sorted(set(best_rounds)),
        "jackknife_min_entropy_bits": min(jackknife_entropies, default=0.0),
        "jackknife_min_archetypes": min(jackknife_archetypes, default=0),
        "target_variation_pass": target_pass,
        "leave_one_sequence_out_continue_stop_auc": loo_auc,
        "learned_selected_rounds": learned_rounds,
        "tuned_simple_selected_rounds": heuristic_rounds,
        "controller_baseline_disagreement_sequences": disagreements,
        "controller_baseline_disagreement_details": disagreement_details,
        "learned_mean_oracle_regret": _mean(learned_regrets),
        "tuned_simple_mean_oracle_regret": _mean(heuristic_regrets),
        "learned_exact_oracle_rounds": sum(a == b for a, b in zip(learned_rounds, best_rounds)),
        "tuned_simple_exact_oracle_rounds": sum(a == b for a, b in zip(heuristic_rounds, best_rounds)),
        "baseline_disagreement_pass": disagreement_pass,
        "tiny_real_subset": {
            "selection": "first 5 frozen sequences in canonical order",
            "binary_examples": len(tiny_y),
            "continue_labels": sum(tiny_y),
            "training_auc": tiny_auc,
            "perfect_separating_threshold_exists": tiny_perfect,
            "pass": tiny_pass,
        },
        "diagnosis": "The prior no-label-variation result was caused by an unstratified calibration split; the frozen sequence pool itself contains cost-aware early/late archetypes.",
        "pass": target_pass and disagreement_pass and tiny_pass,
        "scientific_role": "offline pre-experiment repair evidence only; does not constitute an A-2 controller result",
    }


def build(round1_root: Path) -> dict[str, Any]:
    a12 = round1_root / "a12"
    decision = _read_json(a12 / "decision.json")
    evaluations = _read_jsonl(a12 / "evaluations.jsonl")
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "round1_root": str(round1_root),
        "a1": audit_a1(decision),
        "a2": audit_a2(evaluations),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Cheap offline A1-R1/A2-R1 pre-experiment repairs from frozen canonical Round-1 artifacts.")
    parser.add_argument("--round1-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build(args.round1_root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
