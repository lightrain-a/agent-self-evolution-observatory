from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .a2_sequence_qualification import _auc, _fit_mean_difference, _mean, _oracle_round, _score


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _feature(row: dict[str, Any], call_scale: float, *, add_success: bool) -> list[float]:
    base = [
        float(row.get("marginal_gain") or 0.0),
        float(row.get("probe_regression") or 0.0),
        float(row.get("disagreement") or 0.0),
        float(row.get("cumulative_calls") or 0.0) / max(call_scale, 1.0),
    ]
    return [float(row.get("success") or 0.0), *base] if add_success else base


def _loo_auc(sequences: list[dict[str, Any]], *, add_success: bool) -> float:
    call_scale = _mean([float(sequence["rounds"][0]["cumulative_calls"]) for sequence in sequences])
    labels: list[int] = []
    scores: list[float] = []
    for holdout, sequence in enumerate(sequences):
        train_x: list[list[float]] = []
        train_y: list[int] = []
        for index, train_sequence in enumerate(sequences):
            if index == holdout:
                continue
            best = _oracle_round(train_sequence)
            for row in train_sequence["rounds"][:-1]:
                train_x.append(_feature(row, call_scale, add_success=add_success))
                train_y.append(1 if best > int(row["round"]) else 0)
        if len(set(train_y)) < 2:
            return 0.5
        model = _fit_mean_difference(train_x, train_y)
        best = _oracle_round(sequence)
        for row in sequence["rounds"][:-1]:
            labels.append(1 if best > int(row["round"]) else 0)
            scores.append(_score(model, _feature(row, call_scale, add_success=add_success)))
    return _auc(labels, scores)


def _tiny_auc(sequences: list[dict[str, Any]], *, add_success: bool, n: int = 5) -> float:
    selected = sequences[: min(n, len(sequences))]
    call_scale = _mean([float(sequence["rounds"][0]["cumulative_calls"]) for sequence in sequences])
    features: list[list[float]] = []
    labels: list[int] = []
    for sequence in selected:
        best = _oracle_round(sequence)
        for row in sequence["rounds"][:-1]:
            features.append(_feature(row, call_scale, add_success=add_success))
            labels.append(1 if best > int(row["round"]) else 0)
    if len(set(labels)) < 2:
        return 0.5
    model = _fit_mean_difference(features, labels)
    return _auc(labels, [_score(model, feature) for feature in features])


def analyze(sequences: list[dict[str, Any]]) -> dict[str, Any]:
    if len(sequences) < 9:
        return {
            "schema_version": "1.0",
            "artifact_kind": "A2-R2-development-audit",
            "decision": "INCONCLUSIVE",
            "reason": "requires-complete-nine-sequence-development-batch",
            "sequence_count": len(sequences),
            "scientific_result_available": False,
        }
    base_loo = _loo_auc(sequences, add_success=False)
    repaired_loo = _loo_auc(sequences, add_success=True)
    base_tiny = _tiny_auc(sequences, add_success=False)
    repaired_tiny = _tiny_auc(sequences, add_success=True)
    increment = repaired_loo - base_loo
    passed = repaired_loo >= 0.65 and repaired_tiny >= 0.95 and increment >= 0.10
    return {
        "schema_version": "1.0",
        "artifact_kind": "A2-R2-development-audit",
        "repair_id": "A2-R2-add-current-success-state",
        "changed_variable": "controller representation only: add current task success to the existing marginal_gain/probe_regression/disagreement/cumulative_calls feature vector",
        "deployment_observability": "current task success is already observed after each update round and is not a hidden/future label",
        "sequence_count": len(sequences),
        "base_leave_one_sequence_out_auc": base_loo,
        "repaired_leave_one_sequence_out_auc": repaired_loo,
        "incremental_auc": increment,
        "base_tiny_training_auc": base_tiny,
        "repaired_tiny_training_auc": repaired_tiny,
        "development_gate": {
            "minimum_repaired_loo_auc": 0.65,
            "minimum_repaired_tiny_auc": 0.95,
            "minimum_incremental_auc": 0.10,
            "pass": passed,
        },
        "pass": passed,
        "decision": "DEVELOPMENT-PASS" if passed else "DEVELOPMENT-FAIL",
        "scientific_result_available": False,
        "authorization_effect": "block-only",
        "independent_validation_required": True,
        "next_action": "freeze-plus-success-feature-and-run-fresh-seed-disjoint-task-qualification" if passed else "keep-A2-screening-blocked-and-revise-controller-representation",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="A2-R2 development audit for adding current task success to the controller state.")
    parser.add_argument("--sequences", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = analyze(_read_jsonl(args.sequences))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.output.with_suffix(args.output.suffix + ".tmp")
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
