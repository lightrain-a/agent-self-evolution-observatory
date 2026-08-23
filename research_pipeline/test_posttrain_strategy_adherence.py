from __future__ import annotations

import unittest

from .posttrain_strategy_adherence import assess_transcript_adherence
from .posttrain_strategy_intervention import (
    ARM_POST_CONFLICT_FREE,
    ARM_POST_EXECUTION,
    ARM_POST_STRATEGY,
    ARM_PRE_STRATEGY,
    BOUNDARY_MARKER,
)


def training(method: str, *, lr: float = 0.001, checkpoint: str | None = None, input_ref: str | None = None, **extra):
    config = {"lr": lr, "steps": 1, "examples": 2, **extra}
    result = {"parameter_update_verified": True}
    if checkpoint is not None:
        result["checkpoint_ref"] = checkpoint
    if input_ref is not None:
        result["input_checkpoint_ref"] = input_ref
    return {
        "kind": "tool_result",
        "tool": "run_training",
        "arguments": {"method": method, "stage": method, "config": config},
        "result": result,
    }


def boundary():
    return {"kind": "boundary", "marker": BOUNDARY_MARKER, "verification": "orchestrator_parameter_update_verified"}


class TrajectoryAdherenceRubricTest(unittest.TestCase):
    def test_pre_allows_one_sft_warmup_then_rl(self) -> None:
        transcript = [training("sft", checkpoint="c1"), boundary(), training("rl", checkpoint="c2", input_ref="c1")]
        result = assess_transcript_adherence(
            ARM_PRE_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=None
        )
        self.assertEqual("ADHERED_UNCALIBRATED", result["assessment"]["status"])
        self.assertTrue(result["details"]["signals"]["strategy_change_observed"])
        self.assertFalse(result["details"]["llm_judge_used"])

    def test_pre_repeated_sft_before_rl_is_mixing(self) -> None:
        transcript = [training("sft"), training("sft"), boundary(), training("rl")]
        result = assess_transcript_adherence(
            ARM_PRE_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=None
        )
        self.assertEqual("PARTIAL_OR_REVERTED_UNCALIBRATED", result["assessment"]["status"])

    def test_post_strategy_clean_rl_after_boundary_adheres(self) -> None:
        transcript = [training("sft", checkpoint="c1"), boundary(), training("rl", checkpoint="c2", input_ref="c1")]
        result = assess_transcript_adherence(
            ARM_POST_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("ADHERED", result["assessment"]["status"])

    def test_post_strategy_sft_then_rl_is_partial_mixing(self) -> None:
        transcript = [training("sft"), boundary(), training("sft"), training("rl")]
        result = assess_transcript_adherence(
            ARM_POST_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("PARTIAL_OR_REVERTED", result["assessment"]["status"])

    def test_post_execution_requires_exact_half_lr_and_same_other_config(self) -> None:
        good = [training("sft", lr=0.001), boundary(), training("sft", lr=0.0005)]
        result = assess_transcript_adherence(
            ARM_POST_EXECUTION, good, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("ADHERED", result["assessment"]["status"])

        bad = [training("sft", lr=0.001), boundary(), training("sft", lr=0.0005, examples=3)]
        result = assess_transcript_adherence(
            ARM_POST_EXECUTION, bad, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NOT_ADHERED", result["assessment"]["status"])

    def test_conflict_free_requires_checkpoint_continuity(self) -> None:
        good = [training("sft", checkpoint="c1"), boundary(), training("rl", input_ref="c1", checkpoint="c2")]
        result = assess_transcript_adherence(
            ARM_POST_CONFLICT_FREE, good, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("ADHERED", result["assessment"]["status"])
        self.assertTrue(result["details"]["checkpoint_continuity_verified"])

        bad = [training("sft", checkpoint="c1"), boundary(), training("rl", input_ref="base_model", checkpoint="c2")]
        result = assess_transcript_adherence(
            ARM_POST_CONFLICT_FREE, bad, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NOT_ADHERED", result["assessment"]["status"])
        self.assertFalse(result["details"]["checkpoint_continuity_verified"])

    def test_missing_delivery_never_counts_as_adherence(self) -> None:
        transcript = [training("sft"), boundary(), training("rl")]
        result = assess_transcript_adherence(
            ARM_POST_STRATEGY, transcript, instruction_delivery_verified=False, pre_headroom_ok=True
        )
        self.assertEqual("NO_EVIDENCE", result["assessment"]["status"])


if __name__ == "__main__":
    unittest.main()
