from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import fmean
from typing import Mapping


ARMS = ("ff_hist", "ff_r1", "ff_r2", "win_common")


@dataclass(frozen=True)
class RegenerationMetricsV2:
    task_ids: tuple[str, ...]
    d_cross_state: float
    d_within_actor: float
    e_real: float
    regeneration_localization_support: bool
    new_success_rates: dict[str, float]
    new_success_counts: dict[str, int]
    new_ff_minus_common_win: dict[str, float]
    new_ff_r1_gt_ff_r2: bool
    family_diagnostics: dict[str, dict[str, float]]
    state_sha_alias: bool


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


def _sha256(value: str, *, name: str) -> str:
    value = str(value)
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _family(task_id: str) -> str:
    parts = task_id.split("-")
    if len(parts) < 4:
        raise ValueError(f"unrecognized controlled task id: {task_id}")
    return parts[2]


def compute_regeneration_metrics_v2(
    *,
    original_ff_r1: Mapping[str, int | float],
    original_ff_r2: Mapping[str, int | float],
    new_scores: Mapping[str, Mapping[str, int | float]],
    ff_r1_sha256: str,
    ff_r2_sha256: str,
) -> RegenerationMetricsV2:
    """Compute the repaired M3R cross-state vs within-state actor diagnostic.

    A1/B1 are the already-completed first actor observations from exact-evidence
    replay. A2/B2 are the single prospectively authorized frozen-state
    remeasurements.  For each task q,

        D_X(q) = 1/4 * (|A1-B1| + |A1-B2| + |A2-B1| + |A2-B2|)
        D_A(q) = 1/2 * (|A1-A2| + |B1-B2|)
        E_REAL = mean_q D_X(q) - mean_q D_A(q)

    Under exchangeable conditional actor realizations with Bernoulli success
    probabilities p_A(q), p_B(q), E[E_REAL] = mean_q (p_A(q)-p_B(q))^2.

    The helper contains no provider logic.  Byte-identical states are the same
    treatment, so an A/B SHA alias forces E_REAL to zero exactly.
    """

    sha_a = _sha256(ff_r1_sha256, name="ff_r1_sha256")
    sha_b = _sha256(ff_r2_sha256, name="ff_r2_sha256")
    alias = sha_a == sha_b

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

    cross_terms: list[float] = []
    within_terms: list[float] = []
    family_cross: dict[str, list[float]] = defaultdict(list)
    family_within: dict[str, list[float]] = defaultdict(list)

    for task_id in task_ids:
        a2 = fresh["ff_r1"][task_id]
        b2 = fresh["ff_r2"][task_id]
        cross = 0.25 * (
            abs(a1[task_id] - b1[task_id])
            + abs(a1[task_id] - b2)
            + abs(a2 - b1[task_id])
            + abs(a2 - b2)
        )
        within = 0.5 * (
            abs(a1[task_id] - a2)
            + abs(b1[task_id] - b2)
        )
        cross_terms.append(cross)
        within_terms.append(within)
        fam = _family(task_id)
        family_cross[fam].append(cross)
        family_within[fam].append(within)

    d_x = fmean(cross_terms)
    d_a = fmean(within_terms)
    e_real = 0.0 if alias else d_x - d_a

    success_counts = {arm: sum(values[t] for t in task_ids) for arm, values in fresh.items()}
    n = len(task_ids)
    success_rates = {arm: count / n for arm, count in success_counts.items()}
    win_rate = success_rates["win_common"]
    ff_contrasts = {
        arm: success_rates[arm] - win_rate
        for arm in ("ff_hist", "ff_r1", "ff_r2")
    }

    families = sorted(set(family_cross) | set(family_within))
    family_diagnostics = {}
    for fam in families:
        fam_dx = fmean(family_cross[fam])
        fam_da = fmean(family_within[fam])
        family_diagnostics[fam] = {
            "d_cross_state": fam_dx,
            "d_within_actor": fam_da,
            "e_real": 0.0 if alias else fam_dx - fam_da,
        }

    return RegenerationMetricsV2(
        task_ids=task_ids,
        d_cross_state=d_x,
        d_within_actor=d_a,
        e_real=e_real,
        regeneration_localization_support=(not alias and e_real > 0.0),
        new_success_rates=success_rates,
        new_success_counts=success_counts,
        new_ff_minus_common_win=ff_contrasts,
        new_ff_r1_gt_ff_r2=success_rates["ff_r1"] > success_rates["ff_r2"],
        family_diagnostics=family_diagnostics,
        state_sha_alias=alias,
    )


__all__ = ["ARMS", "RegenerationMetricsV2", "compute_regeneration_metrics_v2"]
