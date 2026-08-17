from __future__ import annotations

import unittest

from .paper_first_static_procedural_prior_contradiction_principle_readjudication import build_readjudication
from .principle_adjudication import audit_dead_end_counter_explanation


class StaticProceduralPriorContradictionPrincipleReadjudicationTest(unittest.TestCase):
    def test_treatment_surface_mismatch_closes_only_current_contradiction(self) -> None:
        state = build_readjudication()
        self.assertTrue(state["principle_dead_end_certified"])
        self.assertFalse(state["experiment_run_for_this_readjudication"])
        self.assertFalse(state["broader_procedural_artifact_sign_heterogeneity_falsified"])
        counter = state["principle_diagnosis"]["counter_explanation"]
        self.assertEqual(counter["type"], "NECESSARY_ASSUMPTION_REFUTED")
        self.assertEqual(counter["necessary_assumption_id"], "shared-static-procedural-artifact-treatment")
        self.assertTrue(counter["necessity_established"])
        self.assertTrue(counter["assumption_refuted"])
        self.assertEqual(audit_dead_end_counter_explanation(counter)["blockers"], [])
        self.assertIn("inference-time", counter["statement"])
        self.assertIn("supervised fine-tuning", counter["statement"])
        self.assertIn("identical static-procedural-artifact intervention", counter["reopen_condition"])

    def test_reopen_requires_matched_treatment_not_only_matched_headroom(self) -> None:
        state = build_readjudication()
        counter = state["principle_diagnosis"]["counter_explanation"]
        self.assertIn("same frozen executor", counter["opposite_search_seed"])
        self.assertIn("base/headroom", counter["opposite_search_seed"])
        self.assertIn("does not make two different interventions estimate the same causal effect", " ".join(counter["alternative_explanations_ruled_out"]))
        auth = state["authority"]
        self.assertFalse(auth["automatic_problem_gate_authority"])
        self.assertFalse(auth["automatic_method_authority"])
        self.assertFalse(auth["automatic_p0_authority"])
        self.assertFalse(auth["automatic_gpu_authority"])


if __name__ == "__main__":
    unittest.main()
