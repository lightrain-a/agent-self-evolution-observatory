from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class EvidenceStats:
    attempts: int = 0
    retirement_eligible: int = 0

    def merge(self, other: "EvidenceStats") -> "EvidenceStats":
        return EvidenceStats(
            attempts=self.attempts + other.attempts,
            retirement_eligible=self.retirement_eligible + other.retirement_eligible,
        )


def merge_stats(parts: Iterable[EvidenceStats]) -> EvidenceStats:
    total = EvidenceStats()
    for part in parts:
        total = total.merge(part)
    return total


def threshold_gate(stats: EvidenceStats, *, min_attempts: int) -> bool:
    """True means the lifecycle unit is retirement-eligible.

    This theorem helper intentionally isolates the count/eligibility structure that
    the released Skill-SP pruning gate instantiates in the P0/P1 high-score regime.
    """
    if min_attempts <= 0:
        raise ValueError("min_attempts must be positive")
    return stats.attempts >= min_attempts and stats.retirement_eligible == stats.attempts


def quotient_class_decision(parts: Sequence[EvidenceStats], *, min_attempts: int) -> bool:
    """Aggregate evidence at the semantic class before applying the lifecycle gate."""
    return threshold_gate(merge_stats(parts), min_attempts=min_attempts)


def native_class_decision(parts: Sequence[EvidenceStats], *, min_attempts: int) -> bool:
    """Apply the gate per identity; the semantic class retires only when all members retire."""
    if not parts:
        raise ValueError("semantic class must contain at least one identity")
    return all(threshold_gate(part, min_attempts=min_attempts) for part in parts)


def lifecycle_homomorphism_holds(parts: Sequence[EvidenceStats], *, min_attempts: int) -> bool:
    """Representation invariance criterion for one partition of one semantic class.

    The lifecycle decision commutes with evidence aggregation exactly when applying
    the gate after quotient aggregation equals applying it independently to every
    identity and then projecting retirement back to the semantic class.
    """
    return quotient_class_decision(parts, min_attempts=min_attempts) == native_class_decision(parts, min_attempts=min_attempts)


def balanced_attempt_partition(total_evidence: int, multiplicity: int) -> tuple[int, ...]:
    if total_evidence < 0:
        raise ValueError("total_evidence must be nonnegative")
    if multiplicity <= 0:
        raise ValueError("multiplicity must be positive")
    q, r = divmod(total_evidence, multiplicity)
    return tuple(q + (1 if i < r else 0) for i in range(multiplicity))


def balanced_eligible_partition(total_evidence: int, multiplicity: int) -> tuple[EvidenceStats, ...]:
    return tuple(EvidenceStats(attempts=n, retirement_eligible=n) for n in balanced_attempt_partition(total_evidence, multiplicity))


def threshold_fragmentation_window(*, multiplicity: int, min_attempts: int) -> tuple[int, int] | None:
    """Closed integer window where quotient retires but a balanced native split does not."""
    if multiplicity <= 0 or min_attempts <= 0:
        raise ValueError("multiplicity and min_attempts must be positive")
    if multiplicity == 1:
        return None
    return min_attempts, multiplicity * min_attempts - 1


def balanced_full_retirement_threshold(*, multiplicity: int, min_attempts: int) -> int:
    if multiplicity <= 0 or min_attempts <= 0:
        raise ValueError("multiplicity and min_attempts must be positive")
    return multiplicity * min_attempts


def balanced_retirement_lag(*, multiplicity: int, min_attempts: int) -> int:
    return balanced_full_retirement_threshold(multiplicity=multiplicity, min_attempts=min_attempts) - min_attempts


def arbitrary_partition_fragmented(parts: Sequence[EvidenceStats], *, min_attempts: int) -> bool:
    """General partition condition for a representation-only lifecycle divergence.

    A fragmentation defect is present exactly when class-level aggregate evidence
    passes the gate while at least one identity-local bucket fails it.
    """
    return quotient_class_decision(parts, min_attempts=min_attempts) and not native_class_decision(parts, min_attempts=min_attempts)


def theorem_summary() -> dict:
    return {
        "name": "Lifecycle aggregation homomorphism criterion",
        "criterion": "For a semantic class partitioned into identity-local evidence statistics s_1,...,s_k, representation invariance of the class lifecycle decision is equivalent to g(s_1 ⊕ ... ⊕ s_k) = AND_j g(s_j), where ⊕ is sufficient-statistic aggregation and g is the per-unit retirement gate.",
        "threshold_corollary": "If every evidence item is retirement-eligible, attempts are additive, and g(s)=1[attempts(s)>=M], then quotient/canonical retirement occurs at N>=M. Under a balanced k-way exact refinement, native full-class retirement occurs at N>=kM; hence the fragmentation window is M<=N<kM and the retirement lag is (k-1)M.",
        "general_partition_corollary": "For an arbitrary evidence partition, divergence occurs iff total class evidence passes g after aggregation while at least one identity-local bucket fails g.",
        "important_boundary": "Additive or mergeable sufficient statistics do not by themselves guarantee representation invariance: a nonlinear lifecycle decision applied before aggregation can still violate the homomorphism criterion.",
        "repair": "A quotient-credit or semantic-credit ledger aggregates sufficient statistics at semantic-class level before the lifecycle gate, making the class decision independent of exact identity multiplicity for this mechanism.",
        "claim_scope": "Stage-local lifecycle theorem. It does not assert endogenous prevalence, task utility, or cross-system generality.",
        "scientific_authority": False,
    }
