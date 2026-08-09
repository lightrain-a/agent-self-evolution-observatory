from __future__ import annotations

from typing import Any, Iterable

from .p0_common import balanced_assignments, mean, rounded

TRACE_KEYS = {"task_id", "success", "actions", "invalid_actions", "model_calls"}


def validate_trace(trace: dict[str, Any]) -> None:
    missing = sorted(TRACE_KEYS - set(trace))
    if missing:
        raise ValueError(f"trace missing required keys: {', '.join(missing)}")
    if not isinstance(trace["actions"], list):
        raise ValueError("trace.actions must be a list")
    invalid = int(trace["invalid_actions"])
    if invalid < 0 or invalid > len(trace["actions"]):
        raise ValueError("trace.invalid_actions must be between 0 and len(actions)")
    if int(trace["model_calls"]) < 0:
        raise ValueError("trace.model_calls must be non-negative")


def _normalized_edit_distance(left: list[str], right: list[str]) -> float:
    if not left and not right:
        return 0.0
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1] / max(len(left), len(right), 1)


def _by_task(traces: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for trace in traces:
        validate_trace(trace)
        task_id = str(trace["task_id"])
        if task_id in result:
            raise ValueError(f"duplicate trace for task {task_id}")
        result[task_id] = trace
    return result


def behavior_probe_features(
    baseline_traces: Iterable[dict[str, Any]],
    updated_traces: Iterable[dict[str, Any]],
) -> tuple[dict[str, float], dict[str, float]]:
    before = _by_task(baseline_traces)
    after = _by_task(updated_traces)
    if set(before) != set(after) or not before:
        raise ValueError("behavior probes must use the same non-empty task set before and after an update")

    task_ids = sorted(before)
    before_invalid = mean(
        int(before[t]["invalid_actions"]) / max(len(before[t]["actions"]), 1) for t in task_ids
    )
    after_invalid = mean(
        int(after[t]["invalid_actions"]) / max(len(after[t]["actions"]), 1) for t in task_ids
    )
    sequence_shift = mean(
        _normalized_edit_distance(list(before[t]["actions"]), list(after[t]["actions"])) for t in task_ids
    )
    first_action_shift = mean(
        float((before[t]["actions"][:1] or [""])[0] != (after[t]["actions"][:1] or [""])[0]) for t in task_ids
    )
    baseline_length = mean(len(before[t]["actions"]) for t in task_ids)
    updated_length = mean(len(after[t]["actions"]) for t in task_ids)

    return (
        {
            "action_sequence_distance": 0.0,
            "invalid_action_rate": rounded(before_invalid),
            "instruction_choice_shift": 0.0,
            "plan_length": rounded(baseline_length),
        },
        {
            "action_sequence_distance": rounded(sequence_shift),
            "invalid_action_rate": rounded(after_invalid),
            "instruction_choice_shift": rounded(first_action_shift),
            "plan_length": rounded(updated_length),
        },
    )


def balanced_hidden_assignments(
    candidate_ids: Iterable[str],
    task_ids: Iterable[str],
    per_candidate: int,
    seed: int,
) -> dict[str, list[str]]:
    return balanced_assignments(list(candidate_ids), list(task_ids), per_candidate, seed)


def build_a1_row(
    candidate_id: str,
    current_before: dict[str, Any],
    current_after: dict[str, Any],
    edit_size: float,
    probe_before: Iterable[dict[str, Any]],
    probe_after: Iterable[dict[str, Any]],
    hidden_before: Iterable[dict[str, Any]],
    hidden_after: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    validate_trace(current_before)
    validate_trace(current_after)
    if current_before["task_id"] != current_after["task_id"]:
        raise ValueError("current task must be identical before and after the candidate update")
    probe_features_before, probe_features_after = behavior_probe_features(probe_before, probe_after)
    hidden_before_map = _by_task(hidden_before)
    hidden_after_map = _by_task(hidden_after)
    if set(hidden_before_map) != set(hidden_after_map) or not hidden_before_map:
        raise ValueError("hidden evaluation must use the same non-empty task subset before and after")
    hidden_ids = sorted(hidden_before_map)
    return {
        "candidate_id": str(candidate_id),
        "current_task_gain": rounded(float(current_after["success"]) - float(current_before["success"])),
        "edit_size": rounded(edit_size),
        "probe_features_before": probe_features_before,
        "probe_features_after": probe_features_after,
        "hidden_before": [float(hidden_before_map[t]["success"]) for t in hidden_ids],
        "hidden_after": [float(hidden_after_map[t]["success"]) for t in hidden_ids],
        "hidden_task_ids": hidden_ids,
    }


def build_a2_round(
    round_index: int,
    previous_task_trace: dict[str, Any] | None,
    current_task_trace: dict[str, Any],
    probe_baseline: Iterable[dict[str, Any]],
    probe_current: Iterable[dict[str, Any]],
    cumulative_calls: int,
) -> dict[str, Any]:
    validate_trace(current_task_trace)
    if previous_task_trace is not None:
        validate_trace(previous_task_trace)
        if previous_task_trace["task_id"] != current_task_trace["task_id"]:
            raise ValueError("A-2 consecutive rounds must evaluate the same task")
    baseline = _by_task(probe_baseline)
    current = _by_task(probe_current)
    if set(baseline) != set(current) or not baseline:
        raise ValueError("A-2 probe regression requires one matched non-empty probe set")
    task_ids = sorted(baseline)
    base_success = mean(float(baseline[t]["success"]) for t in task_ids)
    current_success = mean(float(current[t]["success"]) for t in task_ids)
    _, shifted = behavior_probe_features(baseline.values(), current.values())
    previous_success = float(previous_task_trace["success"]) if previous_task_trace is not None else 0.0
    return {
        "round": int(round_index),
        "marginal_gain": rounded(float(current_task_trace["success"]) - previous_success),
        "probe_regression": rounded(max(0.0, base_success - current_success)),
        "disagreement": shifted["action_sequence_distance"],
        "cumulative_calls": int(cumulative_calls),
        "success": float(current_task_trace["success"]),
        "regression": float(current_success < base_success - 0.02),
    }


def estimate_a1_episodes(config: dict[str, Any], candidate_count: int | None = None) -> dict[str, int]:
    scope = config.get("scope") or {}
    target = scope.get("candidate_updates_target") or [20, 24]
    candidates = int(candidate_count if candidate_count is not None else max(target))
    discovery = int(scope.get("discovery_failures_target", 20))
    discovery_cap = int(scope.get("discovery_episode_cap", discovery))
    probes = int(scope.get("behavior_probes", 8))
    hidden_pool = int(scope.get("hidden_original_tasks_target", 24))
    hidden_each = int(scope.get("hidden_tasks_per_candidate", 8))
    baseline = discovery + probes + hidden_pool
    candidate_eval = candidates * (1 + probes + hidden_each)
    return {
        "baseline": baseline,
        "candidate_evaluation": candidate_eval,
        "total": baseline + candidate_eval,
        "worst_case_total": discovery_cap + probes + hidden_pool + candidate_eval,
    }


def estimate_a2_episodes(config: dict[str, Any]) -> dict[str, int]:
    scope = config.get("scope") or {}
    splits = scope.get("sequence_splits") or {"discovery": 8, "calibration": 8, "hidden": 12}
    sequences = sum(int(value) for value in splits.values())
    rounds = int(scope.get("max_update_rounds", 4))
    probes = int(scope.get("behavior_probes", 2))
    baseline_probes = probes
    per_sequence = 1 + rounds * (1 + probes)
    total = baseline_probes + sequences * per_sequence
    return {"sequences": sequences, "per_sequence": per_sequence, "baseline_probes": baseline_probes, "total": total}
