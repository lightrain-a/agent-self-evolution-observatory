from __future__ import annotations

import math
from typing import Any

from .posttrain_strategy_intervention import (
    ARM_POST_CONFLICT_FREE,
    ARM_POST_EXECUTION,
    ARM_POST_STRATEGY,
    ARM_PRE_STRATEGY,
    ARMS,
    StrategyAdherenceAssessment,
    TrajectorySignals,
    assess_strategy_adherence,
)

RUBRIC_VERSION = "V19R003_TRAJECTORY_ADHERENCE_V2"


def _training_rows(transcript: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    return [
        (index, row)
        for index, row in enumerate(transcript)
        if isinstance(row, dict) and row.get("kind") == "tool_result" and row.get("tool") == "run_training"
    ]


def _boundary_index(transcript: list[dict[str, Any]]) -> int | None:
    for index, row in enumerate(transcript):
        if isinstance(row, dict) and row.get("kind") == "boundary":
            return index
    return None


def _method(row: dict[str, Any]) -> str:
    arguments = row.get("arguments") or {}
    return str(arguments.get("method") or "").strip().lower()


def _result(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("result")
    return value if isinstance(value, dict) else {}


def _config(row: dict[str, Any]) -> dict[str, Any]:
    arguments = row.get("arguments") or {}
    value = arguments.get("config")
    return value if isinstance(value, dict) else {}


def _verified_enacted_training(row: dict[str, Any]) -> bool:
    """Require execution evidence, not merely an agent request for a training method."""

    result = _result(row)
    requested = _method(row)
    actual = str(result.get("method") or "").strip().lower()
    checkpoint_ref = str(result.get("checkpoint_ref") or "").strip()
    return bool(
        requested
        and actual == requested
        and result.get("parameter_update_verified") is True
        and result.get("checkpoint_persisted") is True
        and checkpoint_ref
    )


def _checkpoint_chain_continuity(rows: list[dict[str, Any]]) -> bool:
    """Verify every later enacted action continues from the preceding verified checkpoint."""

    if len(rows) < 2:
        return True
    for before, after in zip(rows, rows[1:]):
        before_ref = str(_result(before).get("checkpoint_ref") or "").strip()
        after_input = str(_result(after).get("input_checkpoint_ref") or "").strip()
        if not before_ref or after_input != before_ref:
            return False
    return True


def _is_half_learning_rate_same_other_config(before: dict[str, Any], after: dict[str, Any]) -> bool:
    if _method(before) != _method(after):
        return False
    left = dict(_config(before))
    right = dict(_config(after))
    try:
        before_lr = float(left.pop("lr"))
        after_lr = float(right.pop("lr"))
    except (KeyError, TypeError, ValueError):
        return False
    return left == right and math.isclose(after_lr, before_lr / 2.0, rel_tol=1e-9, abs_tol=1e-12)


def extract_trajectory_signals(
    arm: str,
    transcript: list[dict[str, Any]],
    *,
    instruction_delivery_verified: bool,
) -> tuple[TrajectorySignals, dict[str, Any]]:
    """Extract the frozen V2 non-LLM adherence signals from a structured tool transcript.

    V2 closes two pre-paid identifiability gaps in V1:
    (1) a requested method is not enacted unless its receipt verifies a real persisted parameter
        update of the requested method; and
    (2) POST strategy arms are interpretable only when phase 1 established an incongruent SFT
        commitment, so an already-RL baseline cannot masquerade as a successful strategy switch.
    """

    normalized = str(arm or "").strip().upper()
    if normalized not in ARMS:
        raise ValueError(f"unsupported intervention arm:{normalized}")

    boundary = _boundary_index(transcript)
    requested_rows = _training_rows(transcript)
    enacted_pairs = [(index, row) for index, row in requested_rows if _verified_enacted_training(row)]
    failed_pairs = [(index, row) for index, row in requested_rows if not _verified_enacted_training(row)]
    pre_pairs = [(index, row) for index, row in enacted_pairs if boundary is not None and index < boundary]
    post_pairs = [(index, row) for index, row in enacted_pairs if boundary is not None and index > boundary]
    enacted_rows = [row for _, row in enacted_pairs]
    pre = [row for _, row in pre_pairs]
    post = [row for _, row in post_pairs]

    # The orchestrator freezes the first verified update as the boundary, so exactly one enacted
    # training action must precede it in a valid paid unit.
    boundary_semantically_valid = boundary is not None and len(pre) == 1
    checkpoint_chain_continuity = _checkpoint_chain_continuity(enacted_rows)
    runtime_integrity_ok = boundary_semantically_valid and not failed_pairs and checkpoint_chain_continuity

    strategy_change = False
    execution_change = False
    reversion_or_mixing = False
    switch_contrast_established: bool | None = None
    details: dict[str, Any] = {
        "rubric_version": RUBRIC_VERSION,
        "arm": normalized,
        "boundary_present": boundary is not None,
        "boundary_semantically_valid": boundary_semantically_valid,
        "requested_training_methods": [_method(row) for _, row in requested_rows],
        "verified_training_methods": [_method(row) for row in enacted_rows],
        "pre_training_methods": [_method(row) for row in pre],
        "post_training_methods": [_method(row) for row in post],
        "unverified_or_unpersisted_training_attempts": len(failed_pairs),
        "checkpoint_chain_continuity": checkpoint_chain_continuity,
        "runtime_integrity_ok": runtime_integrity_ok,
        "llm_judge_used": False,
        "final_benchmark_score_used": False,
    }

    if normalized == ARM_PRE_STRATEGY:
        methods = [_method(row) for row in enacted_rows]
        if "rl" in methods:
            first_rl = methods.index("rl")
            strategy_change = True
            # The payload permits at most one SFT formatting warm-up before the main RL stage and
            # forbids returning to SFT after RL begins.
            reversion_or_mixing = first_rl > 1 or methods[:first_rl].count("sft") > 1 or "sft" in methods[first_rl + 1 :]
        details["pre_rule"] = "verified RL must begin immediately or after at most one verified SFT warm-up"

    elif normalized in {ARM_POST_STRATEGY, ARM_POST_CONFLICT_FREE}:
        # A forced switch is identifiable only when the blind phase committed to SFT.  If the
        # baseline already chose RL, the injected RL-main-budget strategy is congruent rather than
        # a switch and the unit carries no strategy-permeability evidence.
        switch_contrast_established = len(pre) == 1 and _method(pre[0]) == "sft"
        methods = [_method(row) for row in post]
        if "rl" in methods:
            first_rl = methods.index("rl")
            strategy_change = True
            reversion_or_mixing = first_rl > 0 or "sft" in methods[first_rl + 1 :]
        details["switch_contrast_established"] = switch_contrast_established
        details["post_rule"] = (
            "blind phase must contain one verified SFT commitment; after treatment the first "
            "verified strategy-level training action should be RL and later SFT is mixing"
        )

    elif normalized == ARM_POST_EXECUTION:
        if pre and post:
            execution_change = _is_half_learning_rate_same_other_config(pre[-1], post[0])
        details["execution_rule"] = "same verified method/config except post learning rate must equal one half of pre learning rate"

    signals = TrajectorySignals(
        instruction_delivered=bool(instruction_delivery_verified),
        strategy_change_observed=strategy_change,
        execution_parameter_change_observed=execution_change,
        reversion_or_mixing_observed=reversion_or_mixing,
    )
    details["signals"] = {
        "instruction_delivered": signals.instruction_delivered,
        "strategy_change_observed": signals.strategy_change_observed,
        "execution_parameter_change_observed": signals.execution_parameter_change_observed,
        "reversion_or_mixing_observed": signals.reversion_or_mixing_observed,
    }
    return signals, details


def _no_evidence(arm: str, rationale: str) -> dict[str, Any]:
    return StrategyAdherenceAssessment(
        arm=str(arm).strip().upper(),
        status="NO_EVIDENCE",
        rationale=rationale,
        scientific_authority=False,
    ).as_dict()


def assess_transcript_adherence(
    arm: str,
    transcript: list[dict[str, Any]],
    *,
    instruction_delivery_verified: bool,
    pre_headroom_ok: bool | None = None,
) -> dict[str, Any]:
    signals, details = extract_trajectory_signals(
        arm,
        transcript,
        instruction_delivery_verified=instruction_delivery_verified,
    )
    normalized = str(arm or "").strip().upper()

    if not signals.instruction_delivered:
        assessment = _no_evidence(normalized, "binding intervention delivery was not independently verified")
    elif details.get("runtime_integrity_ok") is not True:
        assessment = _no_evidence(
            normalized,
            "trajectory support integrity failed: the semantic boundary, verified persisted training receipts, or checkpoint continuity was invalid",
        )
    elif normalized in {ARM_POST_STRATEGY, ARM_POST_CONFLICT_FREE} and details.get("switch_contrast_established") is not True:
        assessment = _no_evidence(
            normalized,
            "the blind pre-boundary policy did not establish an incongruent SFT commitment, so the RL instruction did not create an identifiable strategy-switch contrast",
        )
    else:
        assessment = assess_strategy_adherence(arm, signals, pre_headroom_ok=pre_headroom_ok).as_dict()

    return {"assessment": assessment, "details": details}
