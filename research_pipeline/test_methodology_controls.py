from __future__ import annotations

import copy
import unittest

from .methodology_controls import (
    C1_GATE_ID,
    adjudicate_c1_d0b_claim_binding_observation,
    adjudicate_c1_d0b_structural_observation,
    adjudicate_c1_d0b1_intervention_identifiability,
    adjudicate_c1_executable_closure_gate,
    build_methodology_controls_state,
    load_c1_d0b_claim_binding_observation,
    load_c1_d0b_structural_observation,
    load_c1_d0b1_intervention_identifiability_observation,
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
        self.assertEqual(self.state["summary"]["registered_reviewer_gates"], 4)

    def test_c1_d0b_structural_receipt_audit_is_go_but_semantic_authority_stays_hold(self) -> None:
        observation = load_c1_d0b_structural_observation()
        result = adjudicate_c1_d0b_structural_observation(observation)
        self.assertTrue(result["structurally_feasible"], result["errors"])
        self.assertFalse(result["semantic_authority"])
        self.assertFalse(any(result["authority"].values()))
        self.assertEqual(observation["paired_sources_structurally_bound"], 24)
        self.assertEqual(observation["residual_claim_ids_bound"], 423)
        self.assertEqual(observation["semantic_validity_adjudicated_claims"], 0)
        self.assertEqual(observation["nonzero_branch_authority_receipts"], 0)
        registered = self.state["reviewer_gates"]["c1_d0b_receipt_structure"]
        self.assertTrue(registered["observation_loaded"])
        self.assertTrue(registered["observation_adjudication"]["structurally_feasible"])
        self.assertFalse(self.state["summary"]["c1_d0b_semantic_authority"])
        self.assertFalse(self.state["summary"]["c1_d0b_downstream_authority"])

    def test_c1_d0b_claim_binding_correction_preserves_envelope_but_blocks_semantic_upgrade(self) -> None:
        observation = load_c1_d0b_claim_binding_observation()
        result = adjudicate_c1_d0b_claim_binding_observation(observation)
        self.assertTrue(result["envelope_feasible"], result["errors"])
        self.assertFalse(result["claim_binding_ready"])
        self.assertFalse(result["semantic_authority"])
        self.assertFalse(any(result["authority"].values()))
        self.assertEqual(observation["receipt_envelopes_packet_bound"], 24)
        self.assertEqual(observation["candidate_memory_atoms"], 423)
        self.assertEqual(observation["certified_branch_residual_atoms"], 0)
        self.assertEqual(observation["claim_specific_evidence_refs_bound"], 0)
        self.assertEqual(observation["per_claim_validity_adjudicated_atoms"], 0)
        self.assertTrue(observation["packet_level_evidence_binding"])
        self.assertFalse(observation["claim_level_evidence_binding"])
        registered = self.state["reviewer_gates"]["c1_d0b_claim_binding_v2"]
        self.assertTrue(registered["observation_loaded"])
        self.assertTrue(registered["observation_adjudication"]["envelope_feasible"])
        self.assertFalse(self.state["summary"]["c1_d0b_claim_binding_ready"])
        self.assertFalse(self.state["summary"]["c1_d0b_claim_binding_semantic_authority"])
        self.assertFalse(self.state["summary"]["c1_d0b_claim_binding_downstream_authority"])

    def test_c1_d0b_claim_binding_gate_fails_closed_on_fake_claim_or_semantic_readiness(self) -> None:
        observation = copy.deepcopy(load_c1_d0b_claim_binding_observation())
        observation["certified_branch_residual_atoms"] = 1
        observation["claim_specific_evidence_refs_bound"] = 1
        observation["claim_level_evidence_binding"] = True
        observation["semantic_validity_adjudicated"] = True
        observation["authority"]["provider"] = True
        result = adjudicate_c1_d0b_claim_binding_observation(observation)
        self.assertFalse(result["envelope_feasible"])
        self.assertTrue(any("certified_branch_residual_atoms" in error for error in result["errors"]))
        self.assertTrue(any("claim_specific_evidence_refs_bound" in error for error in result["errors"]))
        self.assertTrue(any("claim-level evidence binding" in error for error in result["errors"]))
        self.assertTrue(any("semantic validity" in error for error in result["errors"]))
        self.assertTrue(any("downstream authority" in error for error in result["errors"]))
        self.assertFalse(result["claim_binding_ready"])
        self.assertFalse(result["semantic_authority"])
        self.assertFalse(any(result["authority"].values()))

    def test_c1_d0b1_operational_contrast_go_keeps_atom_level_causal_purity_on_hold(self) -> None:
        observation = load_c1_d0b1_intervention_identifiability_observation()
        result = adjudicate_c1_d0b1_intervention_identifiability(observation)
        self.assertTrue(result["operational_contrast_identifiable"], result["errors"])
        self.assertFalse(result["causal_atom_purity_certified"])
        self.assertFalse(result["semantic_authority"])
        self.assertFalse(any(result["authority"].values()))
        self.assertEqual(observation["pairs"], 24)
        self.assertEqual(observation["same_pre_writer_trajectory_projection_pairs"], 24)
        self.assertEqual(observation["same_resolved_writer_model_within_pair"], 24)
        self.assertEqual(observation["temperature_zero_pairs"], 24)
        self.assertEqual(observation["branch_memory_content_changed_pairs"], 24)
        self.assertEqual(observation["explicit_decoding_seed_bound_pairs"], 0)
        self.assertEqual(observation["same_condition_same_trajectory_replication_bound_pairs"], 0)
        self.assertEqual(observation["f0c_tasks_complete"], 8)
        self.assertTrue(observation["f0c_gate_pass"])
        self.assertEqual(observation["certified_branch_residual_atoms"], 0)
        self.assertEqual(observation["claim_specific_evidence_refs_bound"], 0)
        registered = self.state["reviewer_gates"]["c1_d0b1_intervention_identifiability"]
        self.assertTrue(registered["observation_loaded"])
        self.assertTrue(registered["observation_adjudication"]["operational_contrast_identifiable"])
        self.assertTrue(self.state["summary"]["c1_d0b1_operational_contrast_identifiable"])
        self.assertFalse(self.state["summary"]["c1_d0b1_causal_atom_purity_certified"])
        self.assertFalse(self.state["summary"]["c1_d0b1_semantic_authority"])
        self.assertFalse(self.state["summary"]["c1_d0b1_downstream_authority"])

    def test_c1_d0b1_gate_fails_closed_on_fake_atom_level_causal_upgrade(self) -> None:
        observation = copy.deepcopy(load_c1_d0b1_intervention_identifiability_observation())
        observation["atom_level_causal_residual_purity_certified"] = True
        observation["certified_branch_residual_atoms"] = 1
        observation["authority"]["provider"] = True
        result = adjudicate_c1_d0b1_intervention_identifiability(observation)
        self.assertFalse(result["operational_contrast_identifiable"])
        self.assertTrue(any("atom-level causal residual purity" in error for error in result["errors"]))
        self.assertTrue(any("certified_branch_residual_atoms" in error for error in result["errors"]))
        self.assertTrue(any("downstream authority" in error for error in result["errors"]))
        self.assertFalse(result["causal_atom_purity_certified"])
        self.assertFalse(result["semantic_authority"])
        self.assertFalse(any(result["authority"].values()))

    def test_c1_d0b_structural_gate_fails_closed_on_fake_semantic_or_branch_authority(self) -> None:
        observation = copy.deepcopy(load_c1_d0b_structural_observation())
        observation["semantic_validity_adjudicated_claims"] = 1
        observation["supported_claims"] = 1
        observation["nonzero_branch_authority_receipts"] = 1
        observation["authority"]["provider"] = True
        result = adjudicate_c1_d0b_structural_observation(observation)
        self.assertFalse(result["structurally_feasible"])
        self.assertTrue(any("semantic_validity_adjudicated_claims" in error for error in result["errors"]))
        self.assertTrue(any("supported_claims" in error for error in result["errors"]))
        self.assertTrue(any("nonzero_branch_authority_receipts" in error for error in result["errors"]))
        self.assertTrue(any("downstream authority" in error for error in result["errors"]))
        self.assertFalse(result["semantic_authority"])
        self.assertFalse(any(result["authority"].values()))

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
