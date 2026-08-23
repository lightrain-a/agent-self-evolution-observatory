from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .posttrain_strategy_intervention import (
    ARM_POST_CONFLICT_FREE,
    ARM_POST_EXECUTION,
    ARM_POST_STRATEGY,
    ARM_PRE_STRATEGY,
)

PRE_CLEAN = "ADHERED_UNCALIBRATED"
ADHERED = "ADHERED"
RESIDUAL_STATUSES = frozenset({"NOT_ADHERED", "PARTIAL_OR_REVERTED"})
INTERPRETABLE_STATUSES = frozenset({PRE_CLEAN, ADHERED, *RESIDUAL_STATUSES, "NO_EVIDENCE"})


@dataclass(frozen=True)
class SequentialGateDecision:
    decision: str
    next_arm: str | None
    stop_paid_expansion: bool
    reopen_exact_reduction_adjudication: bool
    problem_gate_pass: bool
    rationale: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "next_arm": self.next_arm,
            "stop_paid_expansion": self.stop_paid_expansion,
            "reopen_exact_reduction_adjudication": self.reopen_exact_reduction_adjudication,
            "problem_gate_pass": self.problem_gate_pass,
            "rationale": self.rationale,
        }


def _normalize(status: str | None) -> str | None:
    if status is None:
        return None
    normalized = str(status).strip().upper()
    if normalized not in INTERPRETABLE_STATUSES:
        raise ValueError(f"unsupported adherence status:{normalized}")
    return normalized


def adjudicate_sequential_paid_gate(
    *,
    pre_strategy: str | None = None,
    post_strategy: str | None = None,
    post_execution: str | None = None,
    post_conflict_free: str | None = None,
) -> SequentialGateDecision:
    """Pre-registered cost-minimizing decision gate for the V19R-003 paid falsifier.

    The function never grants ProblemGate.  The strongest surviving result only reopens a fresh
    exact-reduction adjudication.  Arms are purchased sequentially so a reduction-dominating
    result stops later API expenditure immediately.
    """

    pre = _normalize(pre_strategy)
    post = _normalize(post_strategy)
    execution = _normalize(post_execution)
    conflict_free = _normalize(post_conflict_free)

    if pre is None:
        return SequentialGateDecision(
            "AUTHORIZE_PRE_STRATEGY_ONLY",
            ARM_PRE_STRATEGY,
            False,
            False,
            False,
            "Headroom must be established before any post-lock-in arm is purchased.",
        )
    if pre != PRE_CLEAN:
        return SequentialGateDecision(
            "STOP_PRE_HEADROOM_NOT_ESTABLISHED",
            None,
            True,
            False,
            False,
            "PRE_STRATEGY was not cleanly enacted, so post-lock-in failure would be uninterpretable.",
        )

    if post is None:
        return SequentialGateDecision(
            "AUTHORIZE_POST_STRATEGY_ONLY",
            ARM_POST_STRATEGY,
            False,
            False,
            False,
            "PRE headroom passed; purchase only the matched post-lock-in strategy arm next.",
        )
    if post == ADHERED:
        return SequentialGateDecision(
            "STOP_SOURCE_REDUCTION_SUFFICIENT",
            None,
            True,
            False,
            False,
            "The same strategy remains enactable after lock-in once initiation is externally supplied; the source missing-spontaneity-not-capability reduction is sufficient.",
        )
    if post == "NO_EVIDENCE":
        return SequentialGateDecision(
            "STOP_POST_STRATEGY_UNINTERPRETABLE",
            None,
            True,
            False,
            False,
            "The matched post-lock-in arm did not yield interpretable treatment-delivery evidence; controls cannot rescue it.",
        )
    if post not in RESIDUAL_STATUSES:
        raise ValueError(f"POST_STRATEGY status is not valid after clean PRE:{post}")

    if execution is None:
        return SequentialGateDecision(
            "AUTHORIZE_POST_EXECUTION_ONLY",
            ARM_POST_EXECUTION,
            False,
            False,
            False,
            "A PRE-vs-POST strategy residual exists; test generic post-boundary intervention executability before buying the strategy-conflict control.",
        )
    if execution != ADHERED:
        return SequentialGateDecision(
            "STOP_GENERIC_POST_BOUNDARY_CONTROL_FAILED",
            None,
            True,
            False,
            False,
            "The execution-level post-boundary control was not cleanly enacted, so the apparent strategy residual reduces to generic intervention/continuation failure.",
        )

    if conflict_free is None:
        return SequentialGateDecision(
            "AUTHORIZE_POST_CONFLICT_FREE_ONLY",
            ARM_POST_CONFLICT_FREE,
            False,
            False,
            False,
            "Generic post-boundary intervention works; purchase the conflict-free strategy extension as the final reduction control.",
        )
    if conflict_free == ADHERED:
        return SequentialGateDecision(
            "STOP_ORDINARY_STRATEGY_CONFLICT_REDUCTION",
            None,
            True,
            False,
            False,
            "A conflict-free strategy extension is enactable after lock-in, so failure of the matched strategy is explained by ordinary strategy conflict/rollback semantics rather than a general permeability boundary.",
        )
    if conflict_free == "NO_EVIDENCE":
        return SequentialGateDecision(
            "STOP_CONFLICT_FREE_CONTROL_UNINTERPRETABLE",
            None,
            True,
            False,
            False,
            "The final strategy-level control lacks interpretable treatment-delivery evidence; no positive residual is licensed.",
        )
    if conflict_free in RESIDUAL_STATUSES:
        return SequentialGateDecision(
            "REOPEN_EXACT_REDUCTION_ADJUDICATION",
            None,
            True,
            True,
            False,
            "PRE headroom holds, matched POST strategy enactment fails or reverts, generic execution intervention remains enactable, and even the conflict-free post-lock-in strategy extension fails or reverts. This residual warrants a fresh exact-reduction adjudication but does not itself pass ProblemGate.",
        )
    raise ValueError(f"unexpected POST_CONFLICT_FREE status:{conflict_free}")
