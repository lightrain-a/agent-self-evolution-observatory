"""Pilot-A-only simulation precision appendix for the frozen N=24, K=6 design."""
from __future__ import annotations

import random
from statistics import mean
from typing import Any, Mapping, Sequence

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_analysis import (
    AtomSet, task_statistic,
)

SEPARATION_GRID = (0.05, 0.10, 0.15, 0.20, 0.25)
N_TASKS = 24
K = 6
DEFAULT_REPLICATES = 20_000


def percentile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower, upper = int(position), min(int(position) + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def precision_simulation(
    pilot_a: Mapping[str, Sequence[AtomSet]],
    *,
    seed: int,
    replicates: int = DEFAULT_REPLICATES,
) -> dict[str, Any]:
    pools = [list(values) for _, values in sorted(pilot_a.items())]
    if len(pools) != 4 or any(len(values) < 4 for values in pools):
        raise ValueError("precision simulation requires four pilot tasks with >=4 valid A draws")
    rng = random.Random(seed)
    null_global = []
    for _ in range(replicates):
        per_task = []
        for task_index in range(N_TASKS):
            pool = pools[task_index % len(pools)]
            left = rng.choices(pool, k=K)
            right = rng.choices(pool, k=K)
            per_task.append(task_statistic(left, right))
        null_global.append(mean(per_task))
    critical = percentile(null_global, .95)
    power = {
        f"{effect:.2f}": sum(value + effect > critical for value in null_global) / replicates
        for effect in SEPARATION_GRID
    }
    mde80 = next((effect for effect in SEPARATION_GRID
                  if power[f"{effect:.2f}"] >= .80), None)
    power_limited = mde80 is None or mde80 > .20
    return {
        "design": {"N_tasks": N_TASKS, "K_per_arm": K,
                   "primary_analysis": "task-blocked cross-minus-within T"},
        "pilot_information_used": "repeated A same-state EditTargetSets only",
        "pilot_A_D_effect_used": False,
        "synthetic_separation_grid": list(SEPARATION_GRID),
        "synthetic_effect_model": (
            "additive shift in global cross-minus-within T over the empirically "
            "simulated same-state task-blocked null distribution"
        ),
        "null_replicates": replicates, "rng_seed": seed,
        "one_sided_alpha": .05, "null_critical_T_95": critical,
        "power_by_synthetic_T": power, "MDE80": mde80,
        "POWER_LIMITED": power_limited,
        "null_claim_boundary": (
            "If POWER_LIMITED, a null permits only: no detectable behavioral "
            "distribution shift larger than the qualified precision range."
        ),
        "changes_N_or_K": False,
    }
