from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import fmean
from typing import Mapping


@dataclass(frozen=True)
class ProspectiveRegenerationMetricsV4:
    task_ids: tuple[str, ...]
    d_cross_state: float
    d_within_actor: float
    e_real: float
    informative_two_success_tasks: int
    same_state_separation_tasks: int
    exact_one_sided_p: float
    observed_excess_positive: bool
    raw_randomization_pass: bool
    within_task_iid_stationarity_qualified: bool
    cross_task_factorization_qualified: bool
    inference_assumptions_qualified: bool
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


def _strict_bool(value: bool, *, name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{name} must be bool")
    return value


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
    """Mechanical Binomial tail used by the M3R4 conditional test.

    For one informative task with exactly two successes among four post-freeze
    observations, the equal-propensity iid null makes all C(4,2)=6 state-label
    allocations equiprobable: 2/6 place both successes in one state and 4/6
    split them. Thus the same-state-separation indicator has conditional success
    probability 1/3.

    The aggregate X|n2 ~ Binomial(n2,1/3) law additionally requires the
    informative task-block indicators to factorize/behave independently across
    tasks conditional on the fixed panel and per-task totals. Equal p(q) across
    tasks and exchangeability of task identities are NOT required. This helper
    computes the tail mechanically; the caller must separately qualify the
    inferential assumptions before promoting it as an exact p-value.
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


def compute_prospective_regeneration_metrics_v4(
    *,
    ff_r1_rep1: Mapping[str, int | float],
    ff_r1_rep2: Mapping[str, int | float],
    ff_r2_rep1: Mapping[str, int | float],
    ff_r2_rep2: Mapping[str, int | float],
    ff_r1_sha256: str,
    ff_r2_sha256: str,
    within_task_iid_stationarity_qualified: bool,
    cross_task_factorization_qualified: bool,
    alpha: float = 0.05,
) -> ProspectiveRegenerationMetricsV4:
    """Compute M3R4 from four fully post-freeze actor observation vectors.

    All A1/A2/B1/B2 observations must be generated after M3R4 is frozen.
    Historical outcome-consumed actor observations are excluded by interface.

    The observed E_REAL statistic is descriptive without stochastic assumptions.
    The squared-propensity identity and exact Binomial conditional test require:
      1) conditionally iid/independent stationary Bernoulli actor draws within
         each frozen state/task block under the null; and
      2) conditional factorization/independence across informative task blocks,
         so their 1/3 separation indicators multiply to a Binomial law.

    These assumptions do not require a common success probability across tasks
    or exchangeability of task identities. If either qualification is false,
    the numerical tail is retained for audit continuity but cannot produce the
    inferential PASS label.
    """

    if not (0.0 < float(alpha) < 1.0):
        raise ValueError("alpha must be in (0,1)")
    within_ok = _strict_bool(
        within_task_iid_stationarity_qualified,
        name="within_task_iid_stationarity_qualified",
    )
    across_ok = _strict_bool(
        cross_task_factorization_qualified,
        name="cross_task_factorization_qualified",
    )
    assumptions_ok = within_ok and across_ok

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
    raw_randomization_pass = p_value <= float(alpha)
    bounded_pass = (
        not alias
        and positive
        and raw_randomization_pass
        and assumptions_ok
    )

    return ProspectiveRegenerationMetricsV4(
        task_ids=task_ids,
        d_cross_state=d_x,
        d_within_actor=d_a,
        e_real=e_real,
        informative_two_success_tasks=informative,
        same_state_separation_tasks=separation,
        exact_one_sided_p=p_value,
        observed_excess_positive=positive,
        raw_randomization_pass=raw_randomization_pass,
        within_task_iid_stationarity_qualified=within_ok,
        cross_task_factorization_qualified=across_ok,
        inference_assumptions_qualified=assumptions_ok,
        bounded_localization_pass=bounded_pass,
        state_sha_alias=alias,
        task_contributions=contributions,
    )


__all__ = [
    "ProspectiveRegenerationMetricsV4",
    "exact_conditional_randomization_p",
    "compute_prospective_regeneration_metrics_v4",
]
