from __future__ import annotations

import math
from typing import Any

from .posttrain_strategy_intervention import (
    ARM_POST_CONFLICT_FREE,
    ARM_POST_EXECUTION,
    ARM_POST_STRATEGY,
    ARM_PRE_STRATEGY,
    ARMS,
    TrajectorySignals,
    assess_strategy_adherence,
)

RUBRIC_VERSION = "V19R003_TRAJECTORY_ADHERENCE_V1"


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


def _config(row: dict[str, Any]) -> dict[str, Any]:
    arguments = row.get("arguments") or {}
    value = arguments.get("config")
    return value if isinstance(value, dict) else {}


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
    """Extract frozen non-LLM adherence signals from a structured tool transcript."""

    normalized = str(arm or "").strip().upper()
    if normalized not in ARMS:
        raise ValueError(f"unsupported intervention arm:{normalized}")
    boundary = _boundary_index(transcript)
    rows = _training_rows(transcript)
    pre = [row for index, row in rows if boundary is None or index < boundary]
    post = [row for index, row in rows if boundary is not None and index > boundary]

    strategy_change = False
    execution_change = False
    reversion_or_mixing = False
    details: dict[str, Any] = {
        "rubric_version": RUBRIC_VERSION,
        "arm": normalized,
        "boundary_present": boundary is not None,
        "pre_training_methods": [_method(row) for row in pre],
        "post_training_methods": [_method(row) for row in post],
        "llm_judge_used": False,
        "final_benchmark_score_used": False,
    }

    if normalized == ARM_PRE_STRATEGY:
        methods = [_method(row) for _, row in rows]
        if "rl" in methods:
            first_rl = methods.index("rl")
            # Entering RL is observable enactment even when it happens too late; lateness/repeated
            # SFT is represented separately as mixing rather than collapsed into NOT_ADHERED.
            strategy_change = True
            # The payload permits one small SFT formatting warm-up, but not repeated SFT or a
            # return to SFT after the main RL stage has begun.
            reversion_or_mixing = first_rl > 1 or methods[:first_rl].count("sft") > 1 or "sft" in methods[first_rl + 1 :]
        details["pre_rule"] = "RL must begin immediately or after at most one SFT warm-up"

    elif normalized in {ARM_POST_STRATEGY, ARM_POST_CONFLICT_FREE}:
        methods = [_method(row) for row in post]
        if "rl" in methods:
            first_rl = methods.index("rl")
            strategy_change = True
            reversion_or_mixing = first_rl > 0 or "sft" in methods[first_rl + 1 :]
        if normalized == ARM_POST_CONFLICT_FREE and strategy_change:
            last_pre_ref = None
            if pre:
                last_pre_ref = (pre[-1].get("result") or {}).get("checkpoint_ref")
            first_rl_row = next((row for row in post if _method(row) == "rl"), None)
            rl_input_ref = (first_rl_row.get("result") or {}).get("input_checkpoint_ref") if first_rl_row else None
            continuity = bool(last_pre_ref and rl_input_ref == last_pre_ref)
            strategy_change = strategy_change and continuity
            details["checkpoint_continuity_verified"] = continuity
            details["pre_boundary_checkpoint_ref"] = last_pre_ref
            details["post_rl_input_checkpoint_ref"] = rl_input_ref
        details["post_rule"] = "first post-boundary strategy-level training action should be RL; later SFT is mixing"

    elif normalized == ARM_POST_EXECUTION:
        if pre and post:
            execution_change = _is_half_learning_rate_same_other_config(pre[-1], post[0])
        details["execution_rule"] = "same method/config except post learning rate must equal one half of pre learning rate"

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
    assessment = assess_strategy_adherence(arm, signals, pre_headroom_ok=pre_headroom_ok)
    return {"assessment": assessment.as_dict(), "details": details}
