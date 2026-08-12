from __future__ import annotations

import unittest

from .paper_first_pf2_method_adjudication import build_pf2_method_adjudication, validate_pf2_method_adjudication


class PaperFirstPF2MethodAdjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_pf2_method_adjudication()

    def test_same_information_equivalence_stops_current_method_thesis(self) -> None:
        self.assertEqual(validate_pf2_method_adjudication(self.state), [])
        self.assertEqual(self.state["decision"], "STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL")
        self.assertTrue(self.state["same_information_stop"]["triggered"])
        self.assertEqual(self.state["same_information_stop"]["baseline"], "generic-partial-identification")
        self.assertFalse(self.state["authority"]["method_thesis_active"])

    def test_problem_survives_only_as_problem_and_protocol(self) -> None:
        self.assertEqual(self.state["paper_problem_status"], "SURVIVES_AS_PROBLEM_AND_EVALUATION_PROTOCOL_ONLY")
        self.assertIn("repair-surface non-identifiability", self.state["what_survives"]["problem"])
        self.assertIn("evaluation protocol", self.state["what_survives"]["protocol"])

    def test_two_independent_ai_reviews_are_advisory_not_authority(self) -> None:
        reviewers = self.state["reviewers"]
        self.assertEqual(set(reviewers), {"deepseek_v4_pro", "glm_5_2"})
        self.assertEqual(reviewers["deepseek_v4_pro"]["verdict"], "REVISE_METHOD_DESIGN")
        self.assertEqual(reviewers["glm_5_2"]["verdict"], "STOP_METHOD_THESIS")
        self.assertTrue(all(row["authority"] == "advisory-only" for row in reviewers.values()))
        self.assertFalse(self.state["review_synthesis"]["ai_is_authority"])

    def test_no_experiment_or_rescue_is_authorized(self) -> None:
        authority = self.state["authority"]
        for key in ("experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized", "full_experiment_authorized", "premature_pf_f0_used", "new_method_auto_authorized"):
            self.assertFalse(authority[key], key)
        closed = " ".join(self.state["what_is_closed"])
        self.assertIn("direct router", closed)
        self.assertIn("generic partial-identification", closed)


if __name__ == "__main__":
    unittest.main()
