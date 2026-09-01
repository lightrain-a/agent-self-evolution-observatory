from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Protocol, Sequence


class CaseResult(Protocol):
    case_id: str
    score: float
    rollout: int
    messages: list[dict[str, Any]]


class Arm(str, Enum):
    LL = "L/L"
    HH = "H/H"
    HL_SHADOW = "H/L-shadow"
    HH_HARDMINE = "H/H-hardmine"


@dataclass(frozen=True)
class ComputePolicy:
    low_k: int = 1
    high_k: int = 4
    hardmine_replay_multiplier: int = 2

    def __post_init__(self) -> None:
        if self.low_k != 1:
            raise ValueError("F1 low compute is frozen at K=1")
        if self.high_k <= self.low_k:
            raise ValueError("high_k must exceed low_k")
        if self.hardmine_replay_multiplier < 1:
            raise ValueError("hardmine replay multiplier must be >=1")


@dataclass(frozen=True)
class SelectedDeployment:
    selected: CaseResult
    all_subruns: tuple[CaseResult, ...]

    @property
    def rescued(self) -> bool:
        """Whether best-of-K deployment succeeded despite at least one failed subrun."""
        return self.selected.score >= 1.0 and any(row.score < 1.0 for row in self.all_subruns)

    @property
    def selected_failure(self) -> bool:
        return self.selected.score < 1.0


@dataclass(frozen=True)
class FeedbackPacket:
    arm: Arm
    deployed: CaseResult
    updater_cases: tuple[CaseResult, ...]
    shadow: CaseResult | None
    rescued_failure_count_hidden_from_updater: int


def select_best_of_k(results: Sequence[CaseResult], expected_k: int) -> SelectedDeployment:
    """Deterministic best-of-K: highest score, then lowest rollout index.

    All subruns remain receipts. Only ``selected`` is the deployed trajectory.
    """
    if len(results) != expected_k:
        raise ValueError(f"expected exactly K={expected_k} results, got {len(results)}")
    case_ids = {str(row.case_id) for row in results}
    if len(case_ids) != 1:
        raise ValueError("best-of-K subruns must belong to one case")
    rollout_ids = [int(row.rollout) for row in results]
    if len(set(rollout_ids)) != len(rollout_ids):
        raise ValueError("duplicate rollout ids")
    selected = min(results, key=lambda row: (-float(row.score), int(row.rollout)))
    return SelectedDeployment(selected=selected, all_subruns=tuple(sorted(results, key=lambda row: int(row.rollout))))


def route_feedback(
    *,
    arm: Arm,
    deployment: SelectedDeployment,
    shadow: CaseResult | None,
    policy: ComputePolicy,
) -> FeedbackPacket:
    """Route exactly the information allowed by the frozen Compute-Shielding contract.

    Crucial invariant: failed, non-selected high-C subruns are *never* updater input.
    Thus H/H-hardmine can only replay failures that remain visible after high-C
    selection; it cannot recreate failures that best-of-K rescued. H/L-shadow is
    the only arm that introduces an independently executed K=1 counterfactual.
    """
    deployed = deployment.selected
    hidden = sum(1 for row in deployment.all_subruns if row.score < 1.0 and row is not deployed)

    if arm is Arm.LL:
        if len(deployment.all_subruns) != policy.low_k:
            raise ValueError("L/L requires low-K deployment")
        if shadow is not None:
            raise ValueError("L/L must not receive shadow feedback")
        updater = (deployed,)
    elif arm is Arm.HH:
        if len(deployment.all_subruns) != policy.high_k:
            raise ValueError("H/H requires high-K deployment")
        if shadow is not None:
            raise ValueError("H/H must not receive shadow feedback")
        updater = (deployed,)
    elif arm is Arm.HL_SHADOW:
        if len(deployment.all_subruns) != policy.high_k:
            raise ValueError("H/L-shadow requires high-K deployment")
        if shadow is None:
            raise ValueError("H/L-shadow requires one independent K=1 shadow")
        if str(shadow.case_id) != str(deployed.case_id):
            raise ValueError("shadow case must match deployed case")
        updater = (shadow,)
    elif arm is Arm.HH_HARDMINE:
        if len(deployment.all_subruns) != policy.high_k:
            raise ValueError("H/H-hardmine requires high-K deployment")
        if shadow is not None:
            raise ValueError("hardmine must not receive shadow feedback")
        if deployed.score < 1.0:
            updater = tuple(deployed for _ in range(policy.hardmine_replay_multiplier))
        else:
            updater = (deployed,)
    else:
        raise ValueError(f"unsupported arm {arm}")

    # Defend against accidental leakage of non-selected high-C failure trajectories.
    selected_ids = {id(row) for row in updater}
    forbidden = [
        row for row in deployment.all_subruns
        if row is not deployed and row.score < 1.0 and id(row) in selected_ids
    ]
    if forbidden:
        raise RuntimeError("rescued non-selected failure leaked into updater")

    return FeedbackPacket(
        arm=arm,
        deployed=deployed,
        updater_cases=updater,
        shadow=shadow,
        rescued_failure_count_hidden_from_updater=hidden,
    )


def online_success(packet: FeedbackPacket) -> bool:
    return packet.deployed.score >= 1.0


def visible_failure_count(packet: FeedbackPacket) -> int:
    return sum(1 for row in packet.updater_cases if row.score < 1.0)


def summarize_packets(packets: Iterable[FeedbackPacket]) -> dict[str, Any]:
    rows = list(packets)
    return {
        "cases": len(rows),
        "online_successes": sum(online_success(row) for row in rows),
        "updater_visible_failures": sum(visible_failure_count(row) for row in rows),
        "rescued_failures_hidden": sum(row.rescued_failure_count_hidden_from_updater for row in rows),
    }
