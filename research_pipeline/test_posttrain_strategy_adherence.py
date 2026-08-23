from __future__ import annotations

import unittest

from .posttrain_strategy_adherence import RUBRIC_VERSION, assess_transcript_adherence
from .posttrain_strategy_intervention import (
    ARM_POST_CONFLICT_FREE,
    ARM_POST_EXECUTION,
    ARM_POST_STRATEGY,
    ARM_PRE_STRATEGY,
    BOUNDARY_MARKER,
)


def training(
    method: str,
    *,
    lr: float = 0.001,
    checkpoint: str | None = None,
    input_ref: str | None = None,
    verified: bool = True,
    persisted: bool = True,
    actual_method: str | None = None,
    **extra,
):
    config = {"lr": lr, "steps": 1, "examples": 2, **extra}
    result = {
        "method": (actual_method or method).upper(),
        "parameter_update_verified": verified,
        "checkpoint_persisted": persisted,
    }
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
    def test_v2_is_frozen_before_paid_probe(self) -> None:
        self.assertEqual("V19R003_TRAJECTORY_ADHERENCE_V2", RUBRIC_VERSION)

    def test_pre_allows_one_verified_sft_warmup_then_verified_rl(self) -> None:
        transcript = [
            training("sft", checkpoint="c1"),
            boundary(),
            training("rl", checkpoint="c2", input_ref="c1"),
        ]
        result = assess_transcript_adherence(
            ARM_PRE_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=None
        )
        self.assertEqual("ADHERED_UNCALIBRATED", result["assessment"]["status"])
        self.assertTrue(result["details"]["signals"]["strategy_change_observed"])
        self.assertTrue(result["details"]["runtime_integrity_ok"])
        self.assertFalse(result["details"]["llm_judge_used"])

    def test_pre_direct_verified_rl_is_clean_headroom(self) -> None:
        transcript = [training("rl", checkpoint="c1"), boundary()]
        result = assess_transcript_adherence(
            ARM_PRE_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=None
        )
        self.assertEqual("ADHERED_UNCALIBRATED", result["assessment"]["status"])

    def test_pre_rl_then_sft_is_mixing(self) -> None:
        transcript = [
            training("rl", checkpoint="c1"),
            boundary(),
            training("sft", checkpoint="c2", input_ref="c1"),
        ]
        result = assess_transcript_adherence(
            ARM_PRE_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=None
        )
        self.assertEqual("PARTIAL_OR_REVERTED_UNCALIBRATED", result["assessment"]["status"])

    def test_post_strategy_requires_incongruent_sft_commitment(self) -> None:
        clean_switch = [
            training("sft", checkpoint="c1"),
            boundary(),
            training("rl", checkpoint="c2", input_ref="c1"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_STRATEGY, clean_switch, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("ADHERED", result["assessment"]["status"])
        self.assertTrue(result["details"]["switch_contrast_established"])

        already_rl = [
            training("rl", checkpoint="c1"),
            boundary(),
            training("rl", checkpoint="c2", input_ref="c1"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_STRATEGY, already_rl, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NO_EVIDENCE", result["assessment"]["status"])
        self.assertFalse(result["details"]["switch_contrast_established"])

    def test_post_strategy_sft_after_treatment_is_not_adhered(self) -> None:
        transcript = [
            training("sft", checkpoint="c1"),
            boundary(),
            training("sft", checkpoint="c2", input_ref="c1"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NOT_ADHERED", result["assessment"]["status"])

    def test_requested_rl_without_verified_persisted_update_is_no_evidence(self) -> None:
        transcript = [
            training("sft", checkpoint="c1"),
            boundary(),
            training("rl", checkpoint="c2", input_ref="c1", verified=False),
        ]
        result = assess_transcript_adherence(
            ARM_POST_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NO_EVIDENCE", result["assessment"]["status"])
        self.assertEqual(1, result["details"]["unverified_or_unpersisted_training_attempts"])

    def test_requested_method_must_match_executed_method_receipt(self) -> None:
        transcript = [
            training("sft", checkpoint="c1"),
            boundary(),
            training("rl", checkpoint="c2", input_ref="c1", actual_method="sft"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NO_EVIDENCE", result["assessment"]["status"])

    def test_post_execution_requires_exact_half_lr_same_config_and_continuity(self) -> None:
        good = [
            training("sft", lr=0.001, checkpoint="c1"),
            boundary(),
            training("sft", lr=0.0005, checkpoint="c2", input_ref="c1"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_EXECUTION, good, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("ADHERED", result["assessment"]["status"])

        wrong_config = [
            training("sft", lr=0.001, checkpoint="c1"),
            boundary(),
            training("sft", lr=0.0005, checkpoint="c2", input_ref="c1", examples=3),
        ]
        result = assess_transcript_adherence(
            ARM_POST_EXECUTION, wrong_config, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NOT_ADHERED", result["assessment"]["status"])

        rollback = [
            training("sft", lr=0.001, checkpoint="c1"),
            boundary(),
            training("sft", lr=0.0005, checkpoint="c2", input_ref="base_model"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_EXECUTION, rollback, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NO_EVIDENCE", result["assessment"]["status"])
        self.assertFalse(result["details"]["checkpoint_chain_continuity"])

    def test_conflict_free_requires_switch_contrast_and_checkpoint_continuity(self) -> None:
        good = [
            training("sft", checkpoint="c1"),
            boundary(),
            training("rl", input_ref="c1", checkpoint="c2"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_CONFLICT_FREE, good, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("ADHERED", result["assessment"]["status"])

        rollback = [
            training("sft", checkpoint="c1"),
            boundary(),
            training("rl", input_ref="base_model", checkpoint="c2"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_CONFLICT_FREE, rollback, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NO_EVIDENCE", result["assessment"]["status"])

        already_rl = [
            training("rl", checkpoint="c1"),
            boundary(),
            training("rl", input_ref="c1", checkpoint="c2"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_CONFLICT_FREE, already_rl, instruction_delivery_verified=True, pre_headroom_ok=True
        )
        self.assertEqual("NO_EVIDENCE", result["assessment"]["status"])

    def test_boundary_without_verified_preupdate_is_no_evidence(self) -> None:
        transcript = [training("sft", checkpoint="c1", verified=False), boundary()]
        result = assess_transcript_adherence(
            ARM_PRE_STRATEGY, transcript, instruction_delivery_verified=True, pre_headroom_ok=None
        )
        self.assertEqual("NO_EVIDENCE", result["assessment"]["status"])
        self.assertFalse(result["details"]["boundary_semantically_valid"])

    def test_missing_delivery_never_counts_as_adherence(self) -> None:
        transcript = [
            training("sft", checkpoint="c1"),
            boundary(),
            training("rl", checkpoint="c2", input_ref="c1"),
        ]
        result = assess_transcript_adherence(
            ARM_POST_STRATEGY, transcript, instruction_delivery_verified=False, pre_headroom_ok=True
        )
        self.assertEqual("NO_EVIDENCE", result["assessment"]["status"])


if __name__ == "__main__":
    unittest.main()
