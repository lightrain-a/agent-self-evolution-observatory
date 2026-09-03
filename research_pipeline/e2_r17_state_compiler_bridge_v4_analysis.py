from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, Sequence


@dataclass(frozen=True)
class DirectionalGate:
    mean_value: float
    positive_units: int
    total_units: int
    min_positive_units: int
    passed: bool


@dataclass(frozen=True)
class DiagnosisClassification:
    score_only_mean_advantage: float
    scope_matched_mean_advantage: float
    label: str
    trajectory_conditioned_diagnosis_supported: bool


def _values(values: Iterable[float], *, expected: int | None = None) -> tuple[float, ...]:
    xs = tuple(float(x) for x in values)
    if not xs:
        raise ValueError("at least one value is required")
    if expected is not None and len(xs) != expected:
        raise ValueError(f"expected exactly {expected} values, got {len(xs)}")
    return xs


def directional_gate(values: Iterable[float], *, min_positive_units: int, expected_units: int) -> DirectionalGate:
    """Frozen finite-unit gate used independently for each scientific question."""

    xs = _values(values, expected=expected_units)
    positives = sum(x > 0.0 for x in xs)
    avg = mean(xs)
    return DirectionalGate(
        mean_value=avg,
        positive_units=positives,
        total_units=len(xs),
        min_positive_units=int(min_positive_units),
        passed=avg > 0.0 and positives >= int(min_positive_units),
    )


def generator_method_gate(generator_contrasts: Iterable[float]) -> DirectionalGate:
    """Raw complete-method gate; generic controls do not enter this decision."""

    return directional_gate(generator_contrasts, min_positive_units=4, expected_units=6)


def diagnosis_control_classification(
    score_only_advantages: Iterable[float],
    scope_matched_advantages: Iterable[float],
) -> DiagnosisClassification:
    """Classify interpretation without vetoing the raw generator-method gate.

    SCORE_ONLY_GENERIC_MAX asks whether maximal generic advice already explains
    the compiled-state utility. SCOPE_MATCHED_GENERIC_MAX additionally conditions
    on trajectory-derived repair-block cardinality. Passing both supports benefit
    beyond score pattern and repair cardinality; failing them narrows the method
    interpretation but does not erase an independently observed complete-method
    contrast.
    """

    score = _values(score_only_advantages, expected=6)
    scope = _values(scope_matched_advantages, expected=6)
    score_mean = mean(score)
    scope_mean = mean(scope)

    if score_mean > 0.0 and scope_mean > 0.0:
        label = "TRAJECTORY_CONDITIONED_DIAGNOSIS_SUPPORTED_BEYOND_REPAIR_CARDINALITY"
        supported = True
    elif score_mean > 0.0:
        label = "SCOPE_OR_SPARSITY_CANONICALIZATION_ONLY"
        supported = False
    else:
        label = "GENERIC_CANONICALIZATION_NOT_REJECTED"
        supported = False
    return DiagnosisClassification(
        score_only_mean_advantage=score_mean,
        scope_matched_mean_advantage=scope_mean,
        label=label,
        trajectory_conditioned_diagnosis_supported=supported,
    )


def first_realization_generator_contrast(compiled_utility: float, free_a_utility: float) -> float:
    """Primary deployed-realization estimand: deterministic compiler vs first FREE state."""

    return float(compiled_utility) - float(free_a_utility)


def realization_averaged_sensitivity(
    compiled_utility: float,
    free_a_utility: float,
    free_b_utility: float,
) -> float:
    """Prespecified two-realization sensitivity; never a primary validation gate."""

    return float(compiled_utility) - 0.5 * (float(free_a_utility) + float(free_b_utility))


def _binary_vector(values: Sequence[float], *, name: str) -> tuple[float, ...]:
    xs = tuple(float(x) for x in values)
    if not xs:
        raise ValueError(f"{name} must be non-empty")
    if any(x not in (0.0, 1.0) for x in xs):
        raise ValueError(f"{name} must contain binary outcomes only")
    return xs


def cross_state_disagreement(
    a1: Sequence[float],
    a2: Sequence[float],
    b1: Sequence[float],
    b2: Sequence[float],
) -> float:
    """D_X: mean cross-state pair disagreement using the already-frozen two actor realizations."""

    a1v = _binary_vector(a1, name="a1")
    a2v = _binary_vector(a2, name="a2")
    b1v = _binary_vector(b1, name="b1")
    b2v = _binary_vector(b2, name="b2")
    n = len(a1v)
    if any(len(x) != n for x in (a2v, b1v, b2v)):
        raise ValueError("all actor-outcome vectors must have equal length")
    return mean(
        0.25 * (
            abs(a1v[i] - b1v[i])
            + abs(a1v[i] - b2v[i])
            + abs(a2v[i] - b1v[i])
            + abs(a2v[i] - b2v[i])
        )
        for i in range(n)
    )


def within_state_actor_disagreement(
    a1: Sequence[float],
    a2: Sequence[float],
    b1: Sequence[float],
    b2: Sequence[float],
) -> float:
    """D_A: average within-frozen-state actor disagreement for FREE A and FREE B."""

    a1v = _binary_vector(a1, name="a1")
    a2v = _binary_vector(a2, name="a2")
    b1v = _binary_vector(b1, name="b1")
    b2v = _binary_vector(b2, name="b2")
    n = len(a1v)
    if any(len(x) != n for x in (a2v, b1v, b2v)):
        raise ValueError("all actor-outcome vectors must have equal length")
    return mean(
        0.5 * (abs(a1v[i] - a2v[i]) + abs(b1v[i] - b2v[i]))
        for i in range(n)
    )


def excess_state_realization_disagreement(
    *,
    free_a_skill_sha256: str,
    free_b_skill_sha256: str,
    a1: Sequence[float],
    a2: Sequence[float],
    b1: Sequence[float],
    b2: Sequence[float],
) -> float:
    """D_X-D_A, with byte-identical FREE states collapsed to exact zero.

    For binary outcomes and exchangeable conditional actor realizations, the
    expectation of D_X-D_A is the mean squared difference in the two frozen-state
    success propensities. It is used only as state-realization localization, not
    as a population variance-component estimate or proof of a variance bottleneck.
    """

    for digest in (free_a_skill_sha256, free_b_skill_sha256):
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("skill SHA must be a lowercase SHA-256 hex digest")
    if free_a_skill_sha256 == free_b_skill_sha256:
        return 0.0
    return cross_state_disagreement(a1, a2, b1, b2) - within_state_actor_disagreement(a1, a2, b1, b2)


def realization_localization_gate(excess_by_stream: Iterable[float]) -> DirectionalGate:
    """Six-stream development localization gate; does not gate the complete-method claim."""

    return directional_gate(excess_by_stream, min_positive_units=4, expected_units=6)


__all__ = [
    "DirectionalGate",
    "DiagnosisClassification",
    "directional_gate",
    "generator_method_gate",
    "diagnosis_control_classification",
    "first_realization_generator_contrast",
    "realization_averaged_sensitivity",
    "cross_state_disagreement",
    "within_state_actor_disagreement",
    "excess_state_realization_disagreement",
    "realization_localization_gate",
]
