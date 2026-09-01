"""Task-blocked preregistered statistics for Qwen STRI behavioral distributions."""
from __future__ import annotations

import hashlib
import math
import random
from itertools import combinations
from statistics import mean
from typing import Iterable, Mapping, Sequence

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_edit_targets import (
    jaccard_distance,
)

AtomSet = set[tuple[str, str]]


def within_mean(values: Sequence[AtomSet]) -> float:
    if len(values) < 2:
        raise ValueError("within-arm statistic requires at least two values")
    return mean(jaccard_distance(a, b) for a, b in combinations(values, 2))


def cross_mean(left: Sequence[AtomSet], right: Sequence[AtomSet]) -> float:
    if not left or not right:
        raise ValueError("cross-arm statistic requires nonempty arms")
    return mean(jaccard_distance(a, b) for a in left for b in right)


def task_statistic(left: Sequence[AtomSet], right: Sequence[AtomSet]) -> float:
    return 2.0 * cross_mean(left, right) - within_mean(left) - within_mean(right)


def task_statistics(blocks: Mapping[str, Mapping[str, Sequence[AtomSet]]],
                    left: str, right: str, minimum: int = 4) -> dict[str, float]:
    return {
        task_id: task_statistic(arms[left], arms[right])
        for task_id, arms in sorted(blocks.items())
        if len(arms.get(left, [])) >= minimum and len(arms.get(right, [])) >= minimum
    }


def seed_from_contract(experiment_id: str, manifest_sha256: str,
                       analysis_label: str) -> int:
    digest = hashlib.sha256(
        f"{experiment_id}||{manifest_sha256}||{analysis_label}".encode()
    ).digest()
    return int.from_bytes(digest[:8], "big")


def permutation_test(
    blocks: Mapping[str, Mapping[str, Sequence[AtomSet]]],
    *,
    left: str = "A",
    right: str = "D",
    minimum: int = 4,
    replicates: int = 100_000,
    seed: int,
) -> dict[str, object]:
    eligible = {
        task_id: (list(arms[left]), list(arms[right]))
        for task_id, arms in sorted(blocks.items())
        if len(arms.get(left, [])) >= minimum and len(arms.get(right, [])) >= minimum
    }
    if not eligible:
        raise ValueError("no analyzable task blocks")
    observed_by_task = {task: task_statistic(a, d) for task, (a, d) in eligible.items()}
    observed = mean(observed_by_task.values())
    rng = random.Random(seed)
    exceed = 0
    for _ in range(replicates):
        permuted: list[float] = []
        for a, d in eligible.values():
            pooled = a + d
            selected = set(rng.sample(range(len(pooled)), len(a)))
            pa = [value for index, value in enumerate(pooled) if index in selected]
            pd = [value for index, value in enumerate(pooled) if index not in selected]
            permuted.append(task_statistic(pa, pd))
        if mean(permuted) >= observed:
            exceed += 1
    p_value = (exceed + 1) / (replicates + 1)
    return {
        "observed_global_T": observed,
        "per_task_T": observed_by_task,
        "analyzable_task_count": len(eligible),
        "replicates": replicates,
        "exceedance_count": exceed,
        "monte_carlo_p_value": p_value,
        "monte_carlo_standard_error": math.sqrt(p_value * (1.0 - p_value) / (replicates + 1)),
        "rng_seed": seed,
        "task_blocked": True,
    }


def bootstrap_ci(values: Mapping[str, float], *, replicates: int = 100_000,
                 seed: int, alpha: float = .05) -> dict[str, object]:
    ordered = [value for _, value in sorted(values.items())]
    if not ordered:
        raise ValueError("no task statistics")
    rng = random.Random(seed)
    draws = sorted(mean(rng.choices(ordered, k=len(ordered))) for _ in range(replicates))

    def quantile(probability: float) -> float:
        position = probability * (len(draws) - 1)
        lower = int(math.floor(position))
        upper = int(math.ceil(position))
        if lower == upper:
            return draws[lower]
        weight = position - lower
        return draws[lower] * (1 - weight) + draws[upper] * weight

    return {
        "estimate": mean(ordered),
        "confidence_level": 1 - alpha,
        "lower": quantile(alpha / 2),
        "upper": quantile(1 - alpha / 2),
        "replicates": replicates,
        "rng_seed": seed,
        "resampling_unit": "task",
    }


def fisher_exact_two_sided(valid_a: int, failed_a: int,
                           valid_d: int, failed_d: int) -> float:
    if min(valid_a, failed_a, valid_d, failed_d) < 0:
        raise ValueError("counts must be nonnegative")
    row_a, row_d = valid_a + failed_a, valid_d + failed_d
    valid_total, total = valid_a + valid_d, row_a + row_d
    if total == 0:
        return 1.0

    def probability(x: int) -> float:
        return (math.comb(valid_total, x)
                * math.comb(total - valid_total, row_a - x)
                / math.comb(total, row_a))

    low = max(0, row_a - (total - valid_total))
    high = min(row_a, valid_total)
    observed = probability(valid_a)
    return min(1.0, sum(probability(x) for x in range(low, high + 1)
                        if probability(x) <= observed + 1e-15))


def missingness_gate(*, planned_a: int, valid_a: int,
                     planned_d: int, valid_d: int) -> dict[str, object]:
    failed_a, failed_d = planned_a - valid_a, planned_d - valid_d
    if min(failed_a, failed_d) < 0 or min(planned_a, planned_d) <= 0:
        raise ValueError("invalid planned/valid counts")
    rate_a, rate_d = failed_a / planned_a, failed_d / planned_d
    p_value = fisher_exact_two_sided(valid_a, failed_a, valid_d, failed_d)
    difference = abs(rate_a - rate_d)
    hold = p_value < .05 and difference > .10
    return {
        "planned_A": planned_a, "valid_A": valid_a, "failed_A": failed_a,
        "planned_D": planned_d, "valid_D": valid_d, "failed_D": failed_d,
        "failure_rate_A": rate_a, "failure_rate_D": rate_d,
        "absolute_failure_rate_difference": difference,
        "fisher_exact_two_sided_p": p_value,
        "decision": "MISSINGNESS_ARM_IMBALANCED" if hold else "MISSINGNESS_GATE_PASS",
        "causal_interpretation_authorized": not hold,
    }


def paired_task_sign_flip(differences: Mapping[str, float], *, replicates: int = 100_000,
                          seed: int) -> dict[str, object]:
    ordered = [float(value) for _, value in sorted(differences.items())]
    if not ordered:
        raise ValueError("no paired task differences")
    observed = mean(ordered)
    rng = random.Random(seed)
    exceed = 0
    for _ in range(replicates):
        permuted = mean(value if rng.getrandbits(1) else -value for value in ordered)
        if abs(permuted) >= abs(observed):
            exceed += 1
    p_value = (exceed + 1) / (replicates + 1)
    return {
        "observed_mean_task_difference": observed,
        "per_task_differences": dict(sorted(differences.items())),
        "task_count": len(ordered), "replicates": replicates,
        "two_sided_monte_carlo_p_value": p_value,
        "monte_carlo_standard_error": math.sqrt(p_value * (1.0 - p_value) / (replicates + 1)),
        "rng_seed": seed, "resampling_unit": "task", "paired": True,
    }


def high_relevance_set(rows: Iterable[Mapping[str, object]], count: int = 12) -> list[str]:
    ordered = sorted(rows, key=lambda row: (-float(row["top1_relevance"]),
                                            str(row["task_sha256"])))
    return [str(row["instance_id"]) for row in ordered[:count]]
