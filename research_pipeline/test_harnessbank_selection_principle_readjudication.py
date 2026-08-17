from __future__ import annotations

import unittest

from research_pipeline.harnessbank_selection_principle_readjudication import build_readjudication
from research_pipeline.principle_adjudication import audit_dead_end_counter_explanation


class HarnessBankSelectionPrincipleReadjudicationTest(unittest.TestCase):
    def test_current_pa03_is_closed_by_scoped_selection_bias_reduction(self) -> None:
        state = build_readjudication()
        self.assertEqual("PA-03-HARNESS-SELECTION-INVERSION", state["candidate_id"])
        self.assertEqual("STOP_REDUCTION_SELECTION_BIAS_ABSORBS_CURRENT_PHENOMENON", state["status"])
        self.assertTrue(state["principle_dead_end_certified"])
        self.assertFalse(state["experiment_run_for_this_readjudication"])
        counter = state["principle_diagnosis"]["counter_explanation"]
        self.assertEqual("SAME_INFORMATION_REDUCTION", counter["type"])
        self.assertTrue(counter["same_information_or_scope_matched"])
        self.assertTrue(counter["same_information_reduction_verified"])
        self.assertTrue(counter["positive_support"])
        self.assertEqual([], audit_dead_end_counter_explanation(counter)["blockers"])
        self.assertFalse(state["authority"]["automatic_gpu_authority"])
        self.assertFalse(state["authority"]["automatic_problem_gate_authority"])

    def test_reopen_requires_lineage_level_residual(self) -> None:
        state = build_readjudication()
        reopen = state["principle_diagnosis"]["counter_explanation"]["reopen_condition"]
        self.assertIn("selected-versus-rejected gene histories", reopen)
        self.assertIn("selection-aware/winner's-curse baseline", reopen)


if __name__ == "__main__":
    unittest.main()
