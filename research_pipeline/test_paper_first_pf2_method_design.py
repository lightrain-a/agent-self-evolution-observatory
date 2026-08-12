from __future__ import annotations

import unittest

from .paper_first_pf2_method_design import build_pf2_method_design, validate_pf2_method_design


class PaperFirstPF2MethodDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_pf2_method_design()

    def test_revised_problem_enters_method_design_but_not_experiment_design(self) -> None:
        self.assertEqual(validate_pf2_method_design(self.state), [])
        self.assertEqual(self.state["paper_id"], "repair-surface-identifiability-under-persistent-agent-updates")
        self.assertEqual(self.state["method_status"], "METHOD_DESIGN_DRAFT_AWAITING_INDEPENDENT_PREMORTEM")
        authority = self.state["authority"]
        self.assertTrue(authority["paper_problem_authorized"])
        self.assertTrue(authority["method_design_authorized"])
        self.assertFalse(authority["method_frozen"])
        self.assertFalse(authority["experiment_blueprint_authorized_to_design"])
        self.assertFalse(authority["local_validation_authorized"])
        self.assertFalse(authority["p0_authorized"])
        self.assertFalse(authority["gpu_authorized"])
        self.assertFalse(authority["full_experiment_authorized"])
        self.assertFalse(authority["premature_pf_f0_used"])

    def test_core_output_is_identification_or_abstention_not_forced_routing(self) -> None:
        states = self.state["certificate_states"]
        self.assertEqual(set(states), {"IDENTIFIED", "UNIDENTIFIABLE", "PROBE_MORE", "OUT_OF_SCOPE"})
        identified = self.state["formal_objects"]["identified_surface"].lower()
        self.assertTrue("for every" in identified or "all compatible" in identified)
        self.assertIn("PI(E)", self.state["formal_objects"]["partial_identification_set"])
        self.assertIn("abstention", self.state["method"]["stage_5_commit_boundary"])

    def test_non_identifiability_is_load_bearing_and_separates_diagnosis_from_prescription(self) -> None:
        claim = self.state["non_identifiability_claim"]
        self.assertIn("identical failed trajectories", claim["statement"])
        self.assertIn("different minimal sufficient repair surfaces", claim["statement"])
        self.assertEqual(len(claim["proof_obligation"]), 3)
        collision = self.state["why_this_is_not_existing_repair_localization"]["Diagnosis_Is_Not_Prescription"]
        self.assertIn("responsibility need not equal prescription", collision)

    def test_generic_causal_methods_are_primary_same_information_baselines(self) -> None:
        by = {row["name"]: row for row in self.state["same_information_baselines"]}
        self.assertIn("generic-partial-identification", by)
        self.assertIn("generic-active-diagnosis", by)
        self.assertIn("identical causal variables", by["generic-partial-identification"]["access"])
        self.assertIn("not smuggled in as novelty", by["generic-active-diagnosis"]["role"])
        stop_rules = " ".join(self.state["method_stop_rules_before_local_validation"])
        self.assertIn("generic partial-identification", stop_rules)
        self.assertIn("generic active diagnosis", stop_rules)

    def test_hidden_persistent_repair_outcomes_cannot_be_opened_before_certificate(self) -> None:
        assumptions = {row["id"]: row["text"] for row in self.state["assumptions"]}
        self.assertIn("hidden persistent repair outcomes cannot be opened", assumptions["A6-no-hidden-outcome-peeking"].lower())
        self.assertIn("non-committing sandbox/replay interventions", assumptions["A5-probe-reversibility"].lower())
        self.assertTrue(any("hidden persistent repair outcomes" in rule for rule in self.state["method_stop_rules_before_local_validation"]))

    def test_pf4_pf6_remain_secondary_invariants(self) -> None:
        invariants = self.state["cross_cutting_invariants"]
        self.assertIn("secondary invariant only", invariants["PF-4_diagnosability"])
        self.assertIn("secondary risk analysis only", invariants["PF-6_failure_quality"])


if __name__ == "__main__":
    unittest.main()
