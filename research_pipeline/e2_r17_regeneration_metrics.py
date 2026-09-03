from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import fmean
from typing import Mapping


ARMS = ("ff_hist", "ff_r1", "ff_r2", "win_common")


@dataclass(frozen=True)
class RegenerationMetrics:
    task_ids: tuple[str, ...]
    d_between_state: float
    d_within_actor: float
    d_regeneration_minus_actor: float
    regeneration_support: bool
    new_success_rates: dict[str, float]
    new_success_counts: dict[str, int]
    new_ff_minus_common_win: dict[str, float]
    new_ff_r1_gt_ff_r2: bool
    family_diagnostics: dict[str, dict[str, float]]


def _binary_map(values: Mapping[str, int | float], *, name: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for task_id, raw in values.items():
        value = float(raw)
        if value not in (0.0, 1.0):
            raise ValueError(f"{name}/{task_id} must be binary")
        out[str(task_id)] = int(value)
    if not out:
        raise ValueError(f"{name} must be non-empty")
    return out


def _family(task_id: str) -> str:
    # Controlled-suite task IDs are r17-b<block>-<family>-p<profile>.
    parts = task_id.split("-")
    if len(parts) < 4:
        raise ValueError(f"unrecognized controlled task id: {task_id}")
    return parts[2]


def compute_regeneration_metrics(
    *,
    original_ff_r1: Mapping[str, int | float],
    original_ff_r2: Mapping[str, int | float],
    new_scores: Mapping[str, Mapping[str, int | float]],
) -> RegenerationMetrics:
    """Compute the frozen M3R between-state versus within-state diagnostic.

    ``original_ff_r1`` and ``original_ff_r2`` are the already-completed first
    actor observations from exact-evidence replay. ``new_scores`` contains one
    contemporaneous frozen-state actor remeasurement for all four states:
    ff_hist, ff_r1, ff_r2, and win_common.

    The function contains no file I/O and no provider logic. It exists so the
    statistic is testable and frozen before any M3R execution authority.
    """

    a1 = _binary_map(original_ff_r1, name="original_ff_r1")
    b1 = _binary_map(original_ff_r2, name="original_ff_r2")
    if set(new_scores) != set(ARMS):
        raise ValueError(f"new_scores arms must be exactly {ARMS}")
    fresh = {arm: _binary_map(new_scores[arm], name=f"new/{arm}") for arm in ARMS}

    task_set = set(a1)
    if set(b1) != task_set:
        raise ValueError("original FF_R1/FF_R2 task sets differ")
    for arm, values in fresh.items():
        if set(values) != task_set:
            raise ValueError(f"new task set differs for {arm}")
    task_ids = tuple(sorted(task_set))

    between_terms: list[float] = []
    within_terms: list[float] = []
    family_between: dict[str, list[float]] = defaultdict(list)
    family_within: dict[str, list[float]] = defaultdict(list)

    for task_id in task_ids:
        a2 = fresh["ff_r1"][task_id]
        b2 = fresh["ff_r2"][task_id]
        between = abs((a1[task_id] + a2) / 2.0 - (b1[task_id] + b2) / 2.0)
        within = 0.5 * (abs(a1[task_id] - a2) + abs(b1[task_id] - b2))
        between_terms.append(between)
        within_terms.append(within)
        fam = _family(task_id)
        family_between[fam].append(between)
        family_within[fam].append(within)

    d_u = fmean(between_terms)
    d_a = fmean(within_terms)
    delta = d_u - d_a

    success_counts = {arm: sum(values[t] for t in task_ids) for arm, values in fresh.items()}
    n = len(task_ids)
    success_rates = {arm: count / n for arm, count in success_counts.items()}
    win_rate = success_rates["win_common"]
    ff_contrasts = {
        arm: success_rates[arm] - win_rate
        for arm in ("ff_hist", "ff_r1", "ff_r2")
    }

    families = sorted(set(family_between) | set(family_within))
    family_diagnostics = {
        fam: {
            "d_between_state": fmean(family_between[fam]),
            "d_within_actor": fmean(family_within[fam]),
            "d_regeneration_minus_actor": fmean(family_between[fam]) - fmean(family_within[fam]),
        }
        for fam in families
    }

    return RegenerationMetrics(
        task_ids=task_ids,
        d_between_state=d_u,
        d_within_actor=d_a,
        d_regeneration_minus_actor=delta,
        regeneration_support=delta > 0.0,
        new_success_rates=success_rates,
        new_success_counts=success_counts,
        new_ff_minus_common_win=ff_contrasts,
        new_ff_r1_gt_ff_r2=success_rates["ff_r1"] > success_rates["ff_r2"],
        family_diagnostics=family_diagnostics,
    )


__all__ = ["ARMS", "RegenerationMetrics", "compute_regeneration_metrics"]
