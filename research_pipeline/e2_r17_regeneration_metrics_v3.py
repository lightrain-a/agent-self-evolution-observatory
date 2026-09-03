from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import fmean
from typing import Mapping


@dataclass(frozen=True)
class ProspectiveRegenerationMetrics:
    task_ids: tuple[str, ...]
    d_cross_state: float
    d_within_actor: float
    e_real: float
    informative_two_success_tasks: int
    same_state_separation_tasks: int
    exact_one_sided_p: float
    observed_excess_positive: bool
    randomization_pass: bool
    bounded_localization_pass: bool
    state_sha_alias: bool
    task_contributions: dict[str, float]


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
    digest = str(value)
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return digest


def _task_excess(a1: int, a2: int, b1: int, b2: int) -> tuple[float, float, float]:
    d_x = 0.25 * (
        abs(a1 - b1)
        + abs(a1 - b2)
        + abs(a2 - b1)
        + abs(a2 - b2)
    )
    d_a = 0.5 * (abs(a1 - a2) + abs(b1 - b2))
    return d_x, d_a, d_x - d_a


def exact_conditional_randomization_p(*, informative_tasks: int, separation_tasks: int) -> float:
    """One-sided exact conditional randomization p-value for fresh 2x2 actor draws.

    Under the task-wise null p_A(q)=p_B(q), conditionally iid Bernoulli actor
    executions imply that, conditional on exactly two successes among the four
    fresh observations for a task, all C(4,2)=6 label configurations are equally
    likely. Two configurations put both successes in one state and contribute
    E_REAL(q)=1; four split successes across states and contribute -1/2. Therefore
    X=#separation tasks | n2 ~ Binomial(n2, 1/3), and larger X is exactly
    equivalent to larger aggregate E_REAL conditional on the observed task totals.

    Tasks with 0, 1, 3, or 4 total successes have E_REAL(q)=0 for every label
    arrangement and are conditionally uninformative for the state-label test.
    """

    n = int(informative_tasks)
    x = int(separation_tasks)
    if n < 0 or x < 0 or x > n:
        raise ValueError("invalid informative/separation task counts")
    if n == 0:
        return 1.0
    return sum(
        math.comb(n, k) * (1.0 / 3.0) ** k * (2.0 / 3.0) ** (n - k)
        for k in range(x, n + 1)
    )


def compute_prospective_regeneration_metrics(
    *,
    ff_r1_rep1: Mapping[str, int | float],
    ff_r1_rep2: Mapping[str, int | float],
    ff_r2_rep1: Mapping[str, int | float],
    ff_r2_rep2: Mapping[str, int | float],
    ff_r1_sha256: str,
    ff_r2_sha256: str,
    alpha: float = 0.05,
) -> ProspectiveRegenerationMetrics:
    """Compute M3R3 from four fully post-freeze actor observation vectors.

    All A1/A2/B1/B2 observations used here must be newly generated after the M3R3
    protocol is frozen. Historical outcome-consumed actor observations are not
    accepted by this interface.

    The exact randomization inference is conditional on the fixed 18-task panel
    and assumes conditionally iid/independent stationary Bernoulli actor draws
    within each frozen state/task under the null. It does not create population
    inference across tasks or streams.
    """

    if not (0.0 < float(alpha) < 1.0):
        raise ValueError("alpha must be in (0,1)")
    sha_a = _sha256(ff_r1_sha256, name="ff_r1_sha256")
    sha_b = _sha256(ff_r2_sha256, name="ff_r2_sha256")
    alias = sha_a == sha_b

    a1 = _binary_map(ff_r1_rep1, name="ff_r1_rep1")
    a2 = _binary_map(ff_r1_rep2, name="ff_r1_rep2")
    b1 = _binary_map(ff_r2_rep1, name="ff_r2_rep1")
    b2 = _binary_map(ff_r2_rep2, name="ff_r2_rep2")
    task_set = set(a1)
    for name, values in (("ff_r1_rep2", a2), ("ff_r2_rep1", b1), ("ff_r2_rep2", b2)):
        if set(values) != task_set:
            raise ValueError(f"task set differs for {name}")
    task_ids = tuple(sorted(task_set))

    cross_terms: list[float] = []
    within_terms: list[float] = []
    contributions: dict[str, float] = {}
    informative = 0
    separation = 0

    for task_id in task_ids:
        dx, da, e = _task_excess(a1[task_id], a2[task_id], b1[task_id], b2[task_id])
        cross_terms.append(dx)
        within_terms.append(da)
        contributions[task_id] = 0.0 if alias else e
        total = a1[task_id] + a2[task_id] + b1[task_id] + b2[task_id]
        if total == 2:
            informative += 1
            if e == 1.0:
                separation += 1

    d_x = fmean(cross_terms)
    d_a = fmean(within_terms)
    e_real = 0.0 if alias else fmean(contributions.values())
    p_value = 1.0 if alias else exact_conditional_randomization_p(
        informative_tasks=informative,
        separation_tasks=separation,
    )
    positive = e_real > 0.0
    randomization_pass = p_value <= float(alpha)
    return ProspectiveRegenerationMetrics(
        task_ids=task_ids,
        d_cross_state=d_x,
        d_within_actor=d_a,
        e_real=e_real,
        informative_two_success_tasks=informative,
        same_state_separation_tasks=separation,
        exact_one_sided_p=p_value,
        observed_excess_positive=positive,
        randomization_pass=randomization_pass,
        bounded_localization_pass=(not alias and positive and randomization_pass),
        state_sha_alias=alias,
        task_contributions=contributions,
    )


__all__ = [
    "ProspectiveRegenerationMetrics",
    "exact_conditional_randomization_p",
    "compute_prospective_regeneration_metrics",
]
