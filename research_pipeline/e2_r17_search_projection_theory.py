from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Iterable, Mapping, Sequence


BinaryOutcome = tuple[int, ...]
ScoreOutcome = tuple[float, ...]


@dataclass(frozen=True)
class BinaryProjectionStats:
    acting_k: float
    acting_precommitted: float
    visible_failure_precommitted: float
    visible_failure_winner: float
    rescue_censoring_mass: float

    @property
    def acting_gain(self) -> float:
        return self.acting_k - self.acting_precommitted

    @property
    def visibility_gap(self) -> float:
        return self.visible_failure_precommitted - self.visible_failure_winner


@dataclass(frozen=True)
class ContinuousProjectionStats:
    acting_gain: float
    integrated_threshold_censoring: float


@dataclass(frozen=True)
class BinaryEvidenceStats:
    """Evidence quantities induced by best-of-K winner selection.

    Binary outcomes use 1=success and 0=failure. The acting selector serves a
    successful trajectory whenever one exists. `winner_failure_visibility`
    measures the probability that winner-only learning observes failure.
    `pool_failure_availability` measures whether the generated pool contains any
    failed trajectory, and `mixed_pool_mass` measures whether the same pool
    contains both success and failure evidence.
    """

    acting_success: float
    winner_failure_visibility: float
    pool_failure_availability: float
    mixed_pool_mass: float


def _validate_distribution(items: Iterable[tuple[Sequence[float], float]]) -> list[tuple[tuple[float, ...], float]]:
    rows = [(tuple(float(v) for v in outcome), float(probability)) for outcome, probability in items]
    if not rows:
        raise ValueError("distribution must be non-empty")
    width = len(rows[0][0])
    if width < 1 or any(len(outcome) != width for outcome, _ in rows):
        raise ValueError("all outcomes must have the same positive width")
    if any(probability < 0 for _, probability in rows):
        raise ValueError("probabilities must be non-negative")
    total = sum(probability for _, probability in rows)
    if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise ValueError(f"probabilities must sum to one, observed {total}")
    return rows


def binary_projection_stats(joint: Mapping[BinaryOutcome, float]) -> BinaryProjectionStats:
    """Compute the exact rescue-censoring quantities for an arbitrary joint law.

    Rollout 0 is the precommitted rollout. No independence or exchangeability is
    assumed. The acting selector succeeds iff any rollout succeeds.
    """
    rows = _validate_distribution(joint.items())
    if any(any(value not in (0.0, 1.0) for value in outcome) for outcome, _ in rows):
        raise ValueError("binary outcomes must contain only zero or one")

    acting_k = sum(max(outcome) * probability for outcome, probability in rows)
    acting_pre = sum(outcome[0] * probability for outcome, probability in rows)
    visible_pre = sum((outcome[0] == 0.0) * probability for outcome, probability in rows)
    visible_win = sum((max(outcome) == 0.0) * probability for outcome, probability in rows)
    rescue = sum(
        (outcome[0] == 0.0 and max(outcome) == 1.0) * probability
        for outcome, probability in rows
    )
    return BinaryProjectionStats(
        acting_k=acting_k,
        acting_precommitted=acting_pre,
        visible_failure_precommitted=visible_pre,
        visible_failure_winner=visible_win,
        rescue_censoring_mass=rescue,
    )


def binary_evidence_stats(joint: Mapping[BinaryOutcome, float]) -> BinaryEvidenceStats:
    """Compute winner-visible and pool-available failure evidence exactly.

    No independence or exchangeability is assumed. For nested pools, the
    pointwise events imply that acting success and mixed-pool support are
    non-decreasing with K, while winner-visible failure is non-increasing.
    """
    rows = _validate_distribution(joint.items())
    if any(any(value not in (0.0, 1.0) for value in outcome) for outcome, _ in rows):
        raise ValueError("binary outcomes must contain only zero or one")

    acting = sum((max(outcome) == 1.0) * probability for outcome, probability in rows)
    winner_failure = sum((max(outcome) == 0.0) * probability for outcome, probability in rows)
    pool_failure = sum((min(outcome) == 0.0) * probability for outcome, probability in rows)
    mixed = sum(
        (min(outcome) == 0.0 and max(outcome) == 1.0) * probability
        for outcome, probability in rows
    )
    return BinaryEvidenceStats(
        acting_success=acting,
        winner_failure_visibility=winner_failure,
        pool_failure_availability=pool_failure,
        mixed_pool_mass=mixed,
    )


def gamma_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return (1.0 - p) - (1.0 - p) ** k


def winner_failure_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return (1.0 - p) ** k


def pool_failure_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return 1.0 - p**k


def mixed_pool_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return 1.0 - p**k - (1.0 - p) ** k


def hidden_failed_branch_count_iid(p: float, k: int) -> float:
    """Expected failed branches omitted when the served winner succeeds."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return k * ((1.0 - p) - (1.0 - p) ** k)


def p_star(k: int) -> float:
    if k <= 1:
        raise ValueError("an interior rescue-censoring peak requires k > 1")
    return 1.0 - k ** (-1.0 / (k - 1))


def continuous_projection_stats(
    support: Mapping[ScoreOutcome, float],
) -> ContinuousProjectionStats:
    """Verify the continuous layer-cake identity on a finite-support joint law.

    For each atom r, the threshold-censoring integral equals max(r)-r[0]
    exactly. Summing over atoms yields the population identity without any
    rollout-independence assumption.
    """
    rows = _validate_distribution(support.items())
    if any(any(value < 0.0 or value > 1.0 for value in outcome) for outcome, _ in rows):
        raise ValueError("scores must lie in [0, 1]")

    acting_gain = sum((max(outcome) - outcome[0]) * probability for outcome, probability in rows)
    integrated = sum(
        max(0.0, max(outcome) - outcome[0]) * probability
        for outcome, probability in rows
    )
    return ContinuousProjectionStats(
        acting_gain=acting_gain,
        integrated_threshold_censoring=integrated,
    )


def gated_projection_factorization(
    rows: Iterable[tuple[bool, float, float]],
) -> tuple[float, float, float]:
    """Return (ATE, event mass, conditional diagnostic advantage).

    Each row is (mixed_event, probability, future_value_difference). The
    alternative projection is required to equal winner-only outside the mixed
    event; this function rejects violations. Under that gate, ATE = mass * delta.
    """
    normalized = [(bool(mixed), float(prob), float(diff)) for mixed, prob, diff in rows]
    if not normalized:
        raise ValueError("rows must be non-empty")
    if any(prob < 0 for _, prob, _ in normalized):
        raise ValueError("probabilities must be non-negative")
    total = sum(prob for _, prob, _ in normalized)
    if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise ValueError("probabilities must sum to one")
    if any((not mixed) and not isclose(diff, 0.0, abs_tol=1e-12) for mixed, _, diff in normalized):
        raise ValueError("gated projections must be identical outside the mixed event")

    ate = sum(prob * diff for _, prob, diff in normalized)
    mass = sum(prob for mixed, prob, _ in normalized if mixed)
    delta = (
        sum(prob * diff for mixed, prob, diff in normalized if mixed) / mass
        if mass > 0
        else 0.0
    )
    return ate, mass, delta
