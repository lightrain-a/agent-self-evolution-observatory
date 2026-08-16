from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from .p0_alfworld_adapter import ALFWorldGameRunner, load_config


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _strip_instance(tokens: list[str]) -> str:
    values = [re.sub(r"[^a-z0-9_-]+", "", token.lower()) for token in tokens]
    values = [token for token in values if token]
    while values and values[-1].isdigit():
        values.pop()
    return "_".join(values)


def action_skeleton(action: str) -> str:
    parts = str(action or "").strip().lower().split()
    if not parts:
        return ""
    verb = parts[0]
    if verb == "go" and len(parts) >= 3 and parts[1] == "to":
        return f"go|{_strip_instance(parts[2:])}"
    if verb in {"open", "close", "examine", "toggle"}:
        return f"{verb}|{_strip_instance(parts[1:])}"
    if verb == "take" and "from" in parts:
        idx = parts.index("from")
        return f"take|*|{_strip_instance(parts[idx + 1:])}"
    if verb in {"move", "put"} and "to" in parts:
        idx = parts.index("to")
        return f"place|*|{_strip_instance(parts[idx + 1:])}"
    if verb in {"clean", "cool", "heat", "slice"} and "with" in parts:
        idx = parts.index("with")
        return f"{verb}|*|{_strip_instance(parts[idx + 1:])}"
    if verb in {"inventory", "look"}:
        return verb
    return f"{verb}|{_strip_instance(parts[1:])}"


def memory_action_skeletons(memory_text: str) -> set[str]:
    result: set[str] = set()
    for line in str(memory_text or "").splitlines():
        match = re.match(r"^\s*\d+\.\s+(.+?)\s*$", line)
        if not match:
            continue
        skeleton = action_skeleton(match.group(1))
        if skeleton:
            result.add(skeleton)
    return result


def action_family(action: str | None) -> str:
    if action is None:
        return "terminal"
    value = str(action).strip().split(" ", 1)[0].lower() if str(action).strip() else ""
    return {
        "go": "navigate",
        "examine": "inspect",
        "open": "container",
        "close": "container",
        "take": "take",
        "move": "place",
        "put": "place",
        "clean": "transform",
        "cool": "transform",
        "heat": "transform",
        "slice": "transform",
        "toggle": "toggle",
    }.get(value, value or "other")


def longest_common_prefix(left: list[str], right: list[str]) -> int:
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return min(len(left), len(right))


def state_phase(prefix: list[str], target_family: str) -> str:
    verbs = [action.split(" ", 1)[0].lower() for action in prefix]
    acquired = "take" in verbs
    transform = next((name for name in ("clean", "cool", "heat") if name in target_family), None)
    transformed = bool(transform and transform in verbs)
    placed = any(verb in {"move", "put"} for verb in verbs)
    if placed:
        return "post_place_or_recovery"
    if not acquired:
        return "pre_acquire"
    if transform and not transformed:
        return "post_acquire_pre_transform"
    if transform and transformed:
        return "post_transform_pre_place"
    return "post_acquire_pre_place"


def _source_target_relation(source: str, target: str) -> str:
    return "same" if source == target else "cross"


def _verify_sources(contract: dict[str, Any]) -> None:
    for key, row in (contract.get("source_artifacts") or {}).items():
        path = Path(str(row.get("path") or ""))
        expected = str(row.get("sha256") or "")
        if not path.is_file():
            raise RuntimeError(f"missing source artifact:{key}:{path}")
        actual = _sha(path)
        if actual != expected:
            raise RuntimeError(f"source artifact sha drift:{key}:expected={expected}:actual={actual}")


def _local_game(run_dir: Path, task: str) -> str:
    data_root = run_dir.parents[1] / "alfworld"
    normalized = str(task).replace("\\", "/")
    if "/alfworld/" in normalized:
        return str(data_root / normalized.split("/alfworld/", 1)[1])
    return normalized


def build_preoutcome_rows(run_dir: Path, config: Path, contract: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw_path = Path(contract["source_artifacts"]["raw_traces"]["path"])
    main_path = Path(contract["source_artifacts"]["main_table"]["path"])
    memory_path = Path(contract["source_artifacts"]["source_memories"]["path"])
    raw = _read_jsonl(raw_path)
    main = {row["unit_id"]: row for row in csv.DictReader(main_path.open(encoding="utf-8"))}
    memories = {row["memory_id"]: row for row in _read_jsonl(memory_path)}
    if len(raw) != 216 or len(main) != 72:
        raise RuntimeError(f"frozen table shape mismatch:raw={len(raw)} main={len(main)}")
    by: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in raw:
        by[str(row["unit_id"])][str(row["arm"])] = row
    runner = ALFWorldGameRunner(load_config(config))
    rows: list[dict[str, Any]] = []
    bad_prefix_actions = 0
    unresolved_memories: list[str] = []
    empty_skeleton_memories: list[str] = []
    for uid in sorted(main):
        arms = by[uid]
        retrieved = list(arms["retrieved"]["actions"])
        placebo = list(arms["placebo"]["actions"])
        divergence = longest_common_prefix(retrieved, placebo)
        prefix = retrieved[:divergence]
        metadata = main[uid]
        memory_id = str(metadata["memory_id"])
        memory = memories.get(memory_id)
        if memory is None:
            unresolved_memories.append(memory_id)
            skeletons: set[str] = set()
        else:
            skeletons = memory_action_skeletons(str(memory.get("text") or ""))
            if not skeletons:
                empty_skeleton_memories.append(memory_id)
        game = _local_game(run_dir, str(metadata["target_task_id"]))
        env = runner.build_env("eval_out_of_distribution", [game])
        try:
            _, info = env.reset()
            done = False
            for action in prefix:
                commands = list((info.get("admissible_commands") or [[]])[0])
                bad_prefix_actions += int(action not in commands)
                _, _, dones, info = env.step([action])
                done = bool(dones[0])
                if done:
                    break
            commands = [] if done else list((info.get("admissible_commands") or [[]])[0])
        finally:
            close = getattr(env, "close", None)
            if callable(close):
                close()
        command_skeletons = [action_skeleton(command) for command in commands]
        matching = sum(skeleton in skeletons for skeleton in command_skeletons)
        total = len(commands)
        target_family = str(metadata["target_family"])
        source_family = str(metadata["source_family"])
        phase_name = state_phase(prefix, target_family)
        retrieved_action = retrieved[divergence] if divergence < len(retrieved) else None
        placebo_action = placebo[divergence] if divergence < len(placebo) else None
        controlled_delta = int(metadata["controlled_delta"])
        rows.append(
            {
                "unit_id": uid,
                "memory_id": memory_id,
                "source_family": source_family,
                "target_family": target_family,
                "source_target_relation": _source_target_relation(source_family, target_family),
                "evaluation_role": str(metadata["evaluation_role"]),
                "nonzero": int(controlled_delta != 0),
                "controlled_delta": controlled_delta,
                "phase": phase_name,
                "retrieved_action_family": action_family(retrieved_action),
                "placebo_action_family": action_family(placebo_action),
                "first_divergence_fraction": divergence / max(1, max(len(retrieved), len(placebo))),
                "prediv_admissible_count": total,
                "memory_consistent_count": matching,
                "memory_consistent_fraction": matching / total if total else 0.0,
            }
        )
    support = {
        "units": len(rows),
        "bad_prefix_actions": bad_prefix_actions,
        "unresolved_memory_ids": sorted(set(unresolved_memories)),
        "empty_skeleton_memory_ids": sorted(set(empty_skeleton_memories)),
    }
    return rows, support


def _feature_spec(train: list[dict[str, Any]], categorical: list[str], numeric: list[str]) -> dict[str, Any]:
    categories = {column: sorted({str(row[column]) for row in train}) for column in categorical}
    numeric_stats: dict[str, tuple[float, float]] = {}
    for column in numeric:
        values = [float(row[column]) for row in train]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        scale = math.sqrt(variance) or 1.0
        numeric_stats[column] = (mean, scale)
    return {"categorical": categorical, "numeric": numeric, "categories": categories, "numeric_stats": numeric_stats}


def _encode(row: dict[str, Any], spec: dict[str, Any]) -> list[float]:
    vector = [1.0]
    for column in spec["categorical"]:
        value = str(row[column])
        vector.extend(1.0 if value == category else 0.0 for category in spec["categories"][column])
    for column in spec["numeric"]:
        mean, scale = spec["numeric_stats"][column]
        vector.append((float(row[column]) - mean) / scale)
    return vector


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _fit_logistic(x: list[list[float]], y: list[int], *, steps: int, learning_rate: float, l2: float) -> list[float]:
    if not x or len(set(y)) != 2:
        raise RuntimeError("logistic fit requires nonempty two-class training data")
    width = len(x[0])
    weights = [0.0] * width
    positives = sum(y)
    negatives = len(y) - positives
    class_weight = {1: len(y) / (2.0 * positives), 0: len(y) / (2.0 * negatives)}
    weight_sum = sum(class_weight[target] for target in y)
    for _ in range(steps):
        gradient = [0.0] * width
        for row, target in zip(x, y):
            probability = _sigmoid(sum(weight * value for weight, value in zip(weights, row)))
            residual = (probability - target) * class_weight[target]
            for index, value in enumerate(row):
                gradient[index] += residual * value
        for index in range(width):
            gradient[index] /= weight_sum
            if index:
                gradient[index] += l2 * weights[index]
            weights[index] -= learning_rate * gradient[index]
    return weights


def _predict(weights: list[float], x: list[list[float]]) -> list[float]:
    return [_sigmoid(sum(weight * value for weight, value in zip(weights, row))) for row in x]


def _roc_auc(y: list[int], score: list[float]) -> float:
    positives = [value for target, value in zip(y, score) if target == 1]
    negatives = [value for target, value in zip(y, score) if target == 0]
    if not positives or not negatives:
        raise RuntimeError("ROC-AUC requires both classes")
    wins = 0.0
    for positive in positives:
        for negative in negatives:
            wins += 1.0 if positive > negative else 0.5 if positive == negative else 0.0
    return wins / (len(positives) * len(negatives))


def _average_precision(y: list[int], score: list[float]) -> float:
    pairs = sorted(zip(score, y), key=lambda item: item[0], reverse=True)
    positives = sum(y)
    if not positives:
        return 0.0
    seen_positive = 0
    total = 0.0
    for rank, (_, target) in enumerate(pairs, start=1):
        if target:
            seen_positive += 1
            total += seen_positive / rank
    return total / positives


def _brier(y: list[int], score: list[float]) -> float:
    return sum((probability - target) ** 2 for target, probability in zip(y, score)) / len(y)


def _metrics(y: list[int], probability: list[float]) -> dict[str, float]:
    return {
        "roc_auc": _roc_auc(y, probability),
        "average_precision": _average_precision(y, probability),
        "brier": _brier(y, probability),
    }


def evaluate(rows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    split = contract["frozen_split"]
    train = [row for row in rows if row["evaluation_role"] == split["train_role"]]
    test = [row for row in rows if row["evaluation_role"] == split["test_role"]]
    y_train = [int(row["nonzero"]) for row in train]
    y_test = [int(row["nonzero"]) for row in test]
    baseline = contract["same_information_baseline"]
    categorical = list(baseline["categorical_features"])
    baseline_numeric = list(baseline["numeric_features"])
    augmented_numeric = baseline_numeric + [str(baseline["augmented_only_feature"])]
    optimizer = baseline["optimizer"]
    base_spec = _feature_spec(train, categorical, baseline_numeric)
    aug_spec = _feature_spec(train, categorical, augmented_numeric)
    base_train = [_encode(row, base_spec) for row in train]
    base_test = [_encode(row, base_spec) for row in test]
    aug_train = [_encode(row, aug_spec) for row in train]
    aug_test = [_encode(row, aug_spec) for row in test]
    base_weights = _fit_logistic(
        base_train,
        y_train,
        steps=int(optimizer["steps"]),
        learning_rate=float(optimizer["learning_rate"]),
        l2=float(optimizer["l2"]),
    )
    aug_weights = _fit_logistic(
        aug_train,
        y_train,
        steps=int(optimizer["steps"]),
        learning_rate=float(optimizer["learning_rate"]),
        l2=float(optimizer["l2"]),
    )
    base_probability = _predict(base_weights, base_test)
    aug_probability = _predict(aug_weights, aug_test)
    base_metrics = _metrics(y_test, base_probability)
    aug_metrics = _metrics(y_test, aug_probability)
    inverse_overlap = [1.0 - float(row["memory_consistent_fraction"]) for row in test]
    positive_overlap = [float(row["memory_consistent_fraction"]) for row in test if row["nonzero"]]
    zero_overlap = [float(row["memory_consistent_fraction"]) for row in test if not row["nonzero"]]
    return {
        "train_units": len(train),
        "test_units": len(test),
        "train_positive_units": int(sum(y_train)),
        "future_positive_units": int(sum(y_test)),
        "baseline": base_metrics,
        "augmented": aug_metrics,
        "augmented_auc_advantage": aug_metrics["roc_auc"] - base_metrics["roc_auc"],
        "inverse_overlap_univariate_auc": _roc_auc(y_test, inverse_overlap),
        "future_overlap_fraction": {
            "positive_mean": sum(positive_overlap) / len(positive_overlap) if positive_overlap else None,
            "zero_mean": sum(zero_overlap) / len(zero_overlap) if zero_overlap else None,
            "min": min(float(row["memory_consistent_fraction"]) for row in test),
            "max": max(float(row["memory_consistent_fraction"]) for row in test),
        },
    }


def run(run_dir: Path, output_dir: Path, config: Path, contract_path: Path) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    _verify_sources(contract)
    rows, support = build_preoutcome_rows(run_dir, config, contract)
    evaluation = evaluate(rows, contract)
    support_gates = contract["support_gates"]
    support_checks = {
        "total_units": len(rows) == int(support_gates["total_units"]),
        "prefix_replay": int(support["bad_prefix_actions"]) <= int(support_gates["prefix_replay_bad_actions_max"]),
        "all_memory_ids_resolved": not support["unresolved_memory_ids"],
        "candidate_feature_finite_all_units": all(math.isfinite(float(row["memory_consistent_fraction"])) for row in rows),
        "future_positive_units": int(evaluation["future_positive_units"]) >= int(support_gates["future_positive_units_min"]),
        "split_shape": (
            int(evaluation["train_units"]) == int(contract["frozen_split"]["expected_train_units"])
            and int(evaluation["test_units"]) == int(contract["frozen_split"]["expected_test_units"])
        ),
    }
    support_pass = all(support_checks.values())
    gate = contract["decision_gates"]
    decision_checks = {
        "future_augmented_roc_auc": float(evaluation["augmented"]["roc_auc"]) >= float(gate["future_augmented_roc_auc_min"]),
        "future_augmented_auc_advantage": float(evaluation["augmented_auc_advantage"]) >= float(gate["future_augmented_auc_advantage_over_same_information_baseline_min"]),
        "future_augmented_brier_noninferiority": float(evaluation["augmented"]["brier"]) <= float(evaluation["baseline"]["brier"]),
        "future_inverse_overlap_univariate_auc": float(evaluation["inverse_overlap_univariate_auc"]) >= float(gate["future_inverse_overlap_univariate_auc_min"]),
    }
    decision_pass = support_pass and all(decision_checks.values())
    decisions = contract["decisions"]
    if not support_pass:
        decision = str(decisions["support_failure"])
    elif decision_pass:
        decision = str(decisions["all_decision_gates_pass"])
    else:
        decision = str(decisions["otherwise"])
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "preoutcome-features.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "schema_version": "1.0",
        "contract_id": contract["contract_id"],
        "contract_sha256": _sha(contract_path),
        "candidate_id": contract["candidate_id"],
        "decision": decision,
        "support_pass": support_pass,
        "decision_pass": decision_pass,
        "support": support,
        "support_checks": support_checks,
        "evaluation": evaluation,
        "decision_checks": decision_checks,
        "scientific_authority": False,
        "scientific_update": "ZERO_AUTHORITY_REDUCTION_FALSIFIER_ONLY",
        "authority": contract["authority"],
        "policy": contract["policy"],
    }
    (output_dir / "decision.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "contract_sha256": result["contract_sha256"],
        "output_feature_sha256": _sha(output_dir / "preoutcome-features.csv"),
        "decision_sha256": _sha(output_dir / "decision.json"),
        "cpu_only": True,
        "model_calls": 0,
        "gpu_calls": 0,
        "source_artifacts": contract["source_artifacts"],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.run_dir, args.output_dir, args.config, args.contract)
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "support_pass": result["support_pass"],
                "decision_pass": result["decision_pass"],
                "evaluation": result["evaluation"],
                "decision_checks": result["decision_checks"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
