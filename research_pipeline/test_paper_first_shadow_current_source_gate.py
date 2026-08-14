from __future__ import annotations

import unittest

from .paper_first_shadow_current_source_gate import REVIEWER, compile_terminal, normalize_receipt


class ShadowCurrentSourceGateTest(unittest.TestCase):
    def shadow_final(self):
        return {
            "rows": [
                {"candidate_id": "S1", "search_primitive": "IDENTIFIABILITY_GAP", "shadow_clear": True, "live_problem_gate_compatible": False},
                {"candidate_id": "S2", "search_primitive": "CONTRADICTION", "shadow_clear": False, "live_problem_gate_compatible": False},
            ]
        }

    def test_missing_current_source_receipt_is_not_pass(self):
        state = compile_terminal(self.shadow_final(), [])
        self.assertEqual(state["status"], "SHADOW_TERMINAL_INCOMPLETE_CURRENT_SOURCE_REVIEW")
        self.assertEqual((state["summary"]["semantic_shadow_clear"], state["summary"]["current_source_missing"], state["summary"]["terminal_shadow_survivors"]), (1, 1, 0))
        self.assertEqual(state["summary"]["live_paper_design_eligible"], 0)

    def test_blocking_receipt_completes_terminal_with_zero_survivors(self):
        review = normalize_receipt({"reviewer": REVIEWER, "raw_sha256": "a" * 64, "verdict": "BLOCK", "reduction_class": "VALID_HARD_VETO", "sources": [{"url": "https://arxiv.org/abs/2605.10114", "title": "closest work"}]}, candidate_id="S1")
        state = compile_terminal(self.shadow_final(), [review])
        self.assertEqual(state["status"], "SHADOW_TERMINAL_COMPLETE")
        self.assertEqual((state["summary"]["current_source_blocked"], state["summary"]["terminal_shadow_survivors"]), (1, 0))
        self.assertFalse(state["scientific_authority"])

    def test_current_source_clear_stays_shadow_only(self):
        review = normalize_receipt({"reviewer": REVIEWER, "raw_sha256": "b" * 64, "verdict": "CLEAR", "reduction_class": "NONE", "sources": []}, candidate_id="S1")
        state = compile_terminal(self.shadow_final(), [review])
        self.assertEqual(state["summary"]["terminal_shadow_survivors"], 1)
        self.assertEqual(state["summary"]["live_problem_gate_compatible_survivors"], 0)
        self.assertEqual(state["summary"]["live_paper_design_eligible"], 0)
        self.assertFalse(state["authority"]["paper_design"])

    def test_unresolved_or_hard_reduction_forces_block(self):
        for reduction_class in ("NEEDS_EXACT_REDUCTION_TEST", "VALID_HARD_VETO"):
            with self.subTest(reduction_class=reduction_class):
                review = normalize_receipt({"reviewer": REVIEWER, "raw_sha256": "c" * 64, "verdict": "CLEAR", "reduction_class": reduction_class}, candidate_id="S1")
                self.assertEqual(review["verdict"], "BLOCK")

    def test_missing_or_misattributed_provenance_is_not_complete(self):
        for payload in (
            {"reviewer": REVIEWER, "raw_sha256": "not-a-sha", "verdict": "CLEAR", "reduction_class": "NONE"},
            {"reviewer": "other-reviewer", "raw_sha256": "d" * 64, "verdict": "CLEAR", "reduction_class": "NONE"},
        ):
            with self.subTest(payload=payload):
                review = normalize_receipt(payload, candidate_id="S1")
                self.assertEqual(review["status"], "invalid-provenance")
                self.assertEqual(review["verdict"], "BLOCK")
                self.assertFalse(review["provenance_valid"])


if __name__ == "__main__":
    unittest.main()
