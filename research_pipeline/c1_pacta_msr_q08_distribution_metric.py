from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

CALIBRATION_SEED = 20260903
CALIBRATION_REPLICATES = 200_000
UNITS = 8
SAMPLES_PER_BRANCH = 6
CANDIDATE_THRESHOLDS = (0.15, 0.20, 0.25)
MAX_NULL_GATE_RATE = 0.05
MIN_CANONICAL_ALT_GATE_RATE = 0.45
NULL_SUPPORT_SIZES = (2, 4, 8)


@dataclass(frozen=True)
class CalibrationRow:
    threshold: float
    null_gate_rates: dict[str, float]
    worst_null_gate_rate: float
    canonical_alt_gate_rate: float
    passes: bool


def _counts(values: Sequence[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return out


def exact_match_mmd2_unbiased(x: Sequence[str], y: Sequence[str]) -> float:
    """Unbiased exact-match-kernel MMD^2 for two categorical samples.

    The kernel is k(a,b)=1[a==b].  Unlike plug-in empirical TV, the null
    expectation is zero even when the common categorical distribution is
    diffuse, so an arm is not rewarded merely for producing lower sample
    overlap under higher stochastic entropy.
    """
    n = len(x)
    m = len(y)
    if n < 2 or m < 2:
        raise ValueError("unbiased MMD^2 requires at least two samples per branch")
    cx = _counts(x)
    cy = _counts(y)
    within_x = sum(v * (v - 1) for v in cx.values()) / (n * (n - 1))
    within_y = sum(v * (v - 1) for v in cy.values()) / (m * (m - 1))
    cross = 2.0 * sum(cx.get(k, 0) * cy.get(k, 0) for k in set(cx) | set(cy)) / (n * m)
    return float(within_x + within_y - cross)


def _mmd_from_multinomial_counts(cx: np.ndarray, cy: np.ndarray, n: int) -> np.ndarray:
    within_x = (cx * (cx - 1)).sum(axis=-1) / (n * (n - 1))
    within_y = (cy * (cy - 1)).sum(axis=-1) / (n * (n - 1))
    cross = 2.0 * (cx * cy).sum(axis=-1) / (n * n)
    return within_x + within_y - cross


def _draw_arm(rng: np.random.Generator, p: np.ndarray, q: np.ndarray, reps: int) -> np.ndarray:
    cx = rng.multinomial(SAMPLES_PER_BRANCH, p, size=(reps, UNITS))
    cy = rng.multinomial(SAMPLES_PER_BRANCH, q, size=(reps, UNITS))
    return _mmd_from_multinomial_counts(cx, cy, SAMPLES_PER_BRANCH)


def _gate_rate(d_select: np.ndarray, threshold: float) -> float:
    means = d_select.mean(axis=1)
    positive = (d_select > 0).sum(axis=1)
    negative = (d_select < 0).sum(axis=1)
    return float(((means >= threshold) & (positive > negative)).mean())


def calibrate_threshold() -> dict:
    """Outcome-independent synthetic calibration for the fresh-successor P0.

    Null families vary only categorical concentration/support.  A valid metric
    should not generate a positive selection signal simply because one arm is
    more diffuse.  The canonical alternative is a predeclared two-action mass
    swap: p=(2/3,1/3) versus q=(1/3,2/3), whose population exact-match MMD^2
    equals 2/9.  A2 remains null under (1/2,1/2).

    The selected threshold is the smallest predeclared candidate with worst
    null gate rate <=5% and canonical-alternative gate rate >=45%.
    """
    rng = np.random.default_rng(CALIBRATION_SEED)

    null_pairs: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for support in NULL_SUPPORT_SIZES:
        p = np.ones(support, dtype=float) / support
        a2 = _draw_arm(rng, p, p, CALIBRATION_REPLICATES)
        a3 = _draw_arm(rng, p, p, CALIBRATION_REPLICATES)
        null_pairs[support] = (a2, a3)

    p0 = np.array([0.5, 0.5], dtype=float)
    p_alt = np.array([2.0 / 3.0, 1.0 / 3.0], dtype=float)
    q_alt = np.array([1.0 / 3.0, 2.0 / 3.0], dtype=float)
    alt_a2 = _draw_arm(rng, p0, p0, CALIBRATION_REPLICATES)
    alt_a3 = _draw_arm(rng, p_alt, q_alt, CALIBRATION_REPLICATES)
    alt_d = alt_a3 - alt_a2

    rows: list[CalibrationRow] = []
    selected: float | None = None
    for threshold in CANDIDATE_THRESHOLDS:
        null_rates = {
            str(support): _gate_rate(a3 - a2, threshold)
            for support, (a2, a3) in null_pairs.items()
        }
        worst_null = max(null_rates.values())
        alt_rate = _gate_rate(alt_d, threshold)
        passes = worst_null <= MAX_NULL_GATE_RATE and alt_rate >= MIN_CANONICAL_ALT_GATE_RATE
        rows.append(
            CalibrationRow(
                threshold=threshold,
                null_gate_rates=null_rates,
                worst_null_gate_rate=worst_null,
                canonical_alt_gate_rate=alt_rate,
                passes=passes,
            )
        )
        if selected is None and passes:
            selected = threshold

    if selected is None:
        raise RuntimeError("Q08_SYNTHETIC_CALIBRATION_NO_CANDIDATE_PASS")

    return {
        "schema_version": 1,
        "status": "Q08_UNBIASED_MMD2_SYNTHETIC_CALIBRATION_PASS",
        "seed": CALIBRATION_SEED,
        "replicates": CALIBRATION_REPLICATES,
        "units": UNITS,
        "samples_per_branch": SAMPLES_PER_BRANCH,
        "kernel": "exact_match_indicator",
        "estimator": "unbiased_MMD2_collision_U_statistic",
        "null_support_sizes": list(NULL_SUPPORT_SIZES),
        "canonical_alternative": {
            "A2_success": [0.5, 0.5],
            "A2_failure": [0.5, 0.5],
            "A3_success": [2.0 / 3.0, 1.0 / 3.0],
            "A3_failure": [1.0 / 3.0, 2.0 / 3.0],
            "population_A3_MMD2": 2.0 / 9.0,
            "population_A2_MMD2": 0.0,
            "population_D_select": 2.0 / 9.0,
        },
        "candidate_thresholds": list(CANDIDATE_THRESHOLDS),
        "selection_rule": {
            "choose": "smallest predeclared candidate passing both constraints",
            "max_worst_null_gate_rate": MAX_NULL_GATE_RATE,
            "min_canonical_alternative_gate_rate": MIN_CANONICAL_ALT_GATE_RATE,
            "gate": "mean_D_select >= threshold AND positive_D_select_units > negative_D_select_units",
        },
        "rows": [asdict(row) for row in rows],
        "selected_mean_D_select_threshold": selected,
        "scientific_provider_calls": 0,
        "scientific_outcomes_read": 0,
    }


def write_calibration(path: Path) -> dict:
    result = calibrate_threshold()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    out = root / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-q08-unbiased-mmd2-calibration-20260903.json"
    print(json.dumps(write_calibration(out), sort_keys=True))
