from __future__ import annotations

import unittest

from .paper_first_design_adjudication import build_paper_first_design_adjudication


class PaperFirstDesignAdjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_paper_first_design_adjudication()
        cls.rows = {row["id"]: row for row in cls.state["rows"]}

    def test_only_pf2_advances_to_method_design(self) -> None:
        self.assertEqual(self.state["summary"]["reviewed"], 4)
        self.assertEqual(self.state["summary"]["advance_to_method_design"], 1)
        self.assertEqual(self.rows["PF-2"]["verdict"], "ADVANCE_TO_METHOD_DESIGN")
        self.assertEqual(self.rows["PF-1"]["verdict"], "REVISE_PAPER_PROBLEM")
        self.assertEqual(self.rows["PF-4"]["verdict"], "MERGE_AS_CROSS_CUTTING_INVARIANT")
        self.assertEqual(self.rows["PF-6"]["verdict"], "STOP_STANDALONE_MERGE_RISK_AXIS")

    def test_no_premature_f0_or_ai_vote_has_scientific_authority(self) -> None:
        self.assertFalse(self.state["policy"]["local_validation_authorized"])
        self.assertFalse(self.state["policy"]["p0_authorized"])
        self.assertFalse(self.state["policy"]["full_experiment_authorized"])
        self.assertFalse(self.state["advisory_review"]["scientific_authority"])
        for row in self.state["rows"]:
            self.assertFalse(row["premature_f0_used_as_scientific_evidence"])
            self.assertFalse(row["advisory_ai_used_as_authority"])
            self.assertFalse(row["local_validation_authorized"])
            self.assertFalse(row["full_experiment_authorized"])

    def test_pf2_current_exhaustive_surface_trial_is_not_accepted_as_method(self) -> None:
        pf2 = self.rows["PF-2"]
        self.assertEqual(pf2["current_method_disposition"], "REVISE_BEFORE_FREEZE")
        self.assertIn("oracle protocol", pf2["current_method_problem"])
        self.assertTrue(any("generic multiclass" in baseline for baseline in pf2["strongest_same_information_baselines"]))
        self.assertTrue(any("hidden" in item.lower() for item in pf2["method_design_requirements"]))

    def test_pf1_redefines_generic_plasticity_as_fixed_operator_evolvability_debt(self) -> None:
        pf1 = self.rows["PF-1"]
        self.assertIn("evolvability debt", pf1["irreducible_boundary"])
        self.assertTrue(any("Freeze the future evolution operator" in item for item in pf1["required_problem_revision"]))
        self.assertTrue(any("non-weight" in item for item in pf1["required_problem_revision"]))

    def test_pf4_and_pf6_do_not_survive_as_current_standalone_methods(self) -> None:
        self.assertEqual(self.rows["PF-4"]["current_method_disposition"], "STOP_STANDALONE_CERTIFICATE")
        self.assertEqual(self.rows["PF-4"]["merge_target"], "PF-2 causal-repair-surface-ownership")
        self.assertEqual(self.rows["PF-6"]["current_method_disposition"], "STOP_STANDALONE_TRANSPORT_MATRIX")
        self.assertIn("PF-2", self.rows["PF-6"]["merge_target"])


if __name__ == "__main__":
    unittest.main()
