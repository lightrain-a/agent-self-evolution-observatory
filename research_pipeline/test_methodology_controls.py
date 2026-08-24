from __future__ import annotations

import copy
import unittest

from .methodology_controls import (
    C1_GATE_ID,
    adjudicate_c1_executable_closure_gate,
    build_methodology_controls_state,
    load_c1_executable_closure_candidate,
)


class MethodologyControlsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.state = build_methodology_controls_state()
        self.by_key = {row["key"]: row for row in self.state["controls"]}

    def test_controls_fill_three_distinct_methodological_gaps_without_new_layer(self) -> None:
        self.assertEqual(self.state["summary"]["controls"], 3)
        self.assertEqual(self.state["summary"]["primary_components_added"], 0)
        self.assertEqual(self.state["summary"]["functional_layers_added"], 0)
        self.assertEqual(set(self.by_key), {"exploration-frontier", "experimental-design-integrity", "reproducibility-readiness"})

    def test_exploration_frontier_is_portfolio_level_not_pairwise_collision(self) -> None:
        row = self.by_key["exploration-frontier"]
        self.assertEqual(row["owner_component"], "wide-search-ideation")
        self.assertTrue(row["rules"]["portfolio_level_collapse_is_distinct_from_pairwise_collision"])
        self.assertTrue(row["rules"]["quality_and_diversity_are_joint_objectives"])
        self.assertIn("quality-thresholded diversity yield", row["measures"])

    def test_preregistration_and_contamination_are_same_design_integrity_control(self) -> None:
        row = self.by_key["experimental-design-integrity"]
        self.assertEqual(row["owner_component"], "protocol-and-replay")
        self.assertTrue(row["rules"]["outcome_contingent_redesign_requires_new_contract"])
        self.assertTrue(row["rules"]["contaminated_runs_cannot_support_method_or_principle_claims"])
        self.assertEqual(len(row["contamination_classes"]), 3)

    def test_reproducibility_requires_independent_reexecution(self) -> None:
        row = self.by_key["reproducibility-readiness"]
        self.assertEqual(row["owner_component"], "literature-evidence-integrity")
        self.assertTrue(row["rules"]["claim_traceability_is_not_equivalent_to_reproducibility"])
        self.assertTrue(row["rules"]["reproduction_must_execute_without_copying_checked_in_results"])
        self.assertIn("independent reproduction report", row["required_artifacts"])

    def test_c1_revision_program_passes_only_the_zero_authority_d0_design_gate(self) -> None:
        candidate = load_c1_executable_closure_candidate()
        result = adjudicate_c1_executable_closure_gate(candidate)
        self.assertEqual(result["gate"], C1_GATE_ID)
        self.assertTrue(result["eligible_for_d0_design"], result["errors"])
        self.assertFalse(any(result["authority"].values()))
        registered = self.state["reviewer_gates"]["c1_executable_closure_v3"]
        self.assertTrue(registered["candidate_loaded"])
        self.assertTrue(registered["candidate_adjudication"]["eligible_for_d0_design"])
        self.assertFalse(self.state["summary"]["c1_reviewer_gate_downstream_authority"])

    def test_c1_gate_fails_closed_if_a_baseline_reenters_novelty(self) -> None:
        candidate = copy.deepcopy(load_c1_executable_closure_candidate())
        candidate["proposed_novel_component_ids"].append("neutral-metadata-memory")
        result = adjudicate_c1_executable_closure_gate(candidate)
        self.assertFalse(result["eligible_for_d0_design"])
        self.assertTrue(any("novelty set" in error or "re-enter" in error for error in result["errors"]))
        self.assertFalse(any(result["authority"].values()))

    def test_c1_gate_fails_closed_on_provider_authority_or_unreceipted_evidence(self) -> None:
        candidate = copy.deepcopy(load_c1_executable_closure_candidate())
        candidate["d0_contract"]["provider_call_budget"] = 1
        candidate["evidence_trigger_contract"]["evidence_receipt_required_before_branch_authority"] = False
        candidate["evidence_trigger_contract"]["evidence_receipt_contract"]["content_addressed"] = False
        result = adjudicate_c1_executable_closure_gate(candidate)
        self.assertFalse(result["eligible_for_d0_design"])
        self.assertTrue(any("provider-call budget" in error for error in result["errors"]))
        self.assertTrue(any("without an evidence receipt" in error for error in result["errors"]))
        self.assertTrue(any("not content-addressed" in error for error in result["errors"]))
        self.assertFalse(any(result["authority"].values()))


if __name__ == "__main__":
    unittest.main()
