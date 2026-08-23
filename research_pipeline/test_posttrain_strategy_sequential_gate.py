from __future__ import annotations

import unittest

from .posttrain_strategy_intervention import (
    ARM_POST_CONFLICT_FREE,
    ARM_POST_EXECUTION,
    ARM_POST_STRATEGY,
    ARM_PRE_STRATEGY,
)
from .posttrain_strategy_sequential_gate import adjudicate_sequential_paid_gate


class SequentialPaidGateTest(unittest.TestCase):
    def test_starts_with_pre_only(self) -> None:
        d = adjudicate_sequential_paid_gate()
        self.assertEqual(d.next_arm, ARM_PRE_STRATEGY)
        self.assertFalse(d.stop_paid_expansion)
        self.assertFalse(d.problem_gate_pass)

    def test_failed_pre_stops_all_later_spend(self) -> None:
        for status in ("NOT_ADHERED", "PARTIAL_OR_REVERTED", "NO_EVIDENCE", "ADHERED"):
            d = adjudicate_sequential_paid_gate(pre_strategy=status)
            self.assertEqual(d.decision, "STOP_PRE_HEADROOM_NOT_ESTABLISHED")
            self.assertTrue(d.stop_paid_expansion)
            self.assertIsNone(d.next_arm)

    def test_clean_pre_buys_only_post_strategy(self) -> None:
        d = adjudicate_sequential_paid_gate(pre_strategy="ADHERED_UNCALIBRATED")
        self.assertEqual(d.next_arm, ARM_POST_STRATEGY)
        self.assertFalse(d.stop_paid_expansion)

    def test_clean_post_enactment_stops_on_source_reduction(self) -> None:
        d = adjudicate_sequential_paid_gate(
            pre_strategy="ADHERED_UNCALIBRATED",
            post_strategy="ADHERED",
        )
        self.assertEqual(d.decision, "STOP_SOURCE_REDUCTION_SUFFICIENT")
        self.assertTrue(d.stop_paid_expansion)
        self.assertFalse(d.reopen_exact_reduction_adjudication)

    def test_post_residual_buys_execution_control_only(self) -> None:
        for status in ("NOT_ADHERED", "PARTIAL_OR_REVERTED"):
            d = adjudicate_sequential_paid_gate(
                pre_strategy="ADHERED_UNCALIBRATED",
                post_strategy=status,
            )
            self.assertEqual(d.next_arm, ARM_POST_EXECUTION)
            self.assertFalse(d.stop_paid_expansion)

    def test_failed_execution_control_stops_before_conflict_free_spend(self) -> None:
        for status in ("NOT_ADHERED", "PARTIAL_OR_REVERTED", "NO_EVIDENCE", "ADHERED_UNCALIBRATED"):
            d = adjudicate_sequential_paid_gate(
                pre_strategy="ADHERED_UNCALIBRATED",
                post_strategy="NOT_ADHERED",
                post_execution=status,
            )
            self.assertEqual(d.decision, "STOP_GENERIC_POST_BOUNDARY_CONTROL_FAILED")
            self.assertTrue(d.stop_paid_expansion)
            self.assertIsNone(d.next_arm)

    def test_execution_control_pass_buys_conflict_free_only(self) -> None:
        d = adjudicate_sequential_paid_gate(
            pre_strategy="ADHERED_UNCALIBRATED",
            post_strategy="PARTIAL_OR_REVERTED",
            post_execution="ADHERED",
        )
        self.assertEqual(d.next_arm, ARM_POST_CONFLICT_FREE)
        self.assertFalse(d.stop_paid_expansion)

    def test_conflict_free_adherence_stops_on_ordinary_conflict_reduction(self) -> None:
        d = adjudicate_sequential_paid_gate(
            pre_strategy="ADHERED_UNCALIBRATED",
            post_strategy="NOT_ADHERED",
            post_execution="ADHERED",
            post_conflict_free="ADHERED",
        )
        self.assertEqual(d.decision, "STOP_ORDINARY_STRATEGY_CONFLICT_REDUCTION")
        self.assertFalse(d.reopen_exact_reduction_adjudication)

    def test_full_residual_only_reopens_adjudication_never_problem_gate(self) -> None:
        for status in ("NOT_ADHERED", "PARTIAL_OR_REVERTED"):
            d = adjudicate_sequential_paid_gate(
                pre_strategy="ADHERED_UNCALIBRATED",
                post_strategy="PARTIAL_OR_REVERTED",
                post_execution="ADHERED",
                post_conflict_free=status,
            )
            self.assertEqual(d.decision, "REOPEN_EXACT_REDUCTION_ADJUDICATION")
            self.assertTrue(d.reopen_exact_reduction_adjudication)
            self.assertTrue(d.stop_paid_expansion)
            self.assertFalse(d.problem_gate_pass)

    def test_no_evidence_controls_never_produce_positive_residual(self) -> None:
        d = adjudicate_sequential_paid_gate(
            pre_strategy="ADHERED_UNCALIBRATED",
            post_strategy="NOT_ADHERED",
            post_execution="ADHERED",
            post_conflict_free="NO_EVIDENCE",
        )
        self.assertEqual(d.decision, "STOP_CONFLICT_FREE_CONTROL_UNINTERPRETABLE")
        self.assertFalse(d.reopen_exact_reduction_adjudication)


if __name__ == "__main__":
    unittest.main()
