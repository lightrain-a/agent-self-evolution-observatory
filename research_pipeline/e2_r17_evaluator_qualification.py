from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class EvaluatorQualificationDecision:
    status: str
    task_count: int
    repeats_per_task: int
    total_successes: int
    successful_task_count: int
    exactly_stable_task_count: int
    all_provider_calls_completed: bool
    nondegenerate_headroom: bool
    multi_task_competence: bool
    endpoint_stability: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def decide_evaluator_qualification(
    *,
    scores_by_task: Mapping[str, Sequence[float]],
    provider_statuses: Sequence[str],
    expected_task_count: int = 6,
    expected_repeats: int = 3,
    required_successful_tasks: int = 2,
    required_stable_tasks: int = 5,
) -> EvaluatorQualificationDecision:
    if len(scores_by_task) != expected_task_count:
        raise ValueError("evaluator qualification task-count drift")
    normalized: dict[str, tuple[int, ...]] = {}
    for task_id, raw_scores in scores_by_task.items():
        if len(raw_scores) != expected_repeats:
            raise ValueError(f"evaluator qualification repeat-count drift: {task_id}")
        scores = tuple(int(value) for value in raw_scores)
        if any(float(value) not in (0.0, 1.0) for value in raw_scores):
            raise ValueError(f"evaluator qualification score must be binary: {task_id}")
        normalized[str(task_id)] = scores

    total = sum(sum(scores) for scores in normalized.values())
    successful_tasks = sum(any(scores) for scores in normalized.values())
    stable_tasks = sum(len(set(scores)) == 1 for scores in normalized.values())
    expected_provider_calls_lower_bound = expected_task_count * expected_repeats
    if len(provider_statuses) < expected_provider_calls_lower_bound:
        raise ValueError("evaluator qualification contains too few provider receipts")
    all_completed = all(status == "completed" for status in provider_statuses)
    nondegenerate = 0 < total < expected_task_count * expected_repeats
    multi_task = successful_tasks >= required_successful_tasks
    stable = stable_tasks >= required_stable_tasks
    passed = all_completed and nondegenerate and multi_task and stable
    return EvaluatorQualificationDecision(
        status=(
            "PASS_HOSTED_EVALUATOR_DEVELOPMENT_QUALIFICATION"
            if passed
            else "FAIL_HOSTED_EVALUATOR_DEVELOPMENT_QUALIFICATION"
        ),
        task_count=expected_task_count,
        repeats_per_task=expected_repeats,
        total_successes=total,
        successful_task_count=successful_tasks,
        exactly_stable_task_count=stable_tasks,
        all_provider_calls_completed=all_completed,
        nondegenerate_headroom=nondegenerate,
        multi_task_competence=multi_task,
        endpoint_stability=stable,
    )


__all__ = [
    "EvaluatorQualificationDecision",
    "decide_evaluator_qualification",
]
