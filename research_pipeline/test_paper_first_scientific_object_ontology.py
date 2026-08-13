from __future__ import annotations

import unittest

from .paper_first_scientific_object_ontology import audit_candidate_object, audit_scientific_object_ontology, current_lane_axes, load_scientific_object_config


class ScientificObjectOntologyTest(unittest.TestCase):
    def row(self, idx: int, text: str, lanes: list[str], *, facts: bool = True, failure: bool = True) -> dict:
        return {
            "ref": f"arXiv:test-{idx}",
            "title": text,
            "abstract": text,
            "primary_source_verified": True,
            "lane_keys": lanes,
            "empirical_facts": ([{"text": "result"}] if facts else []),
            "typed_evidence": {
                "operational_assumptions": [],
                "measured_failures": ([{"text": "failure"}] if failure else []),
                "boundary_observations": [],
            },
        }

    def test_current_taxonomy_is_split_into_object_context_property_axes(self) -> None:
        axes = current_lane_axes(["skill_harness", "world_model", "parametric_model_state", "embodied", "safety_reliability"])
        self.assertEqual(axes["object"], ["skill_harness", "world_model", "parametric_model_state"])
        self.assertEqual(axes["context"], ["embodied"])
        self.assertEqual(axes["property"], ["safety_reliability"])
        self.assertEqual(axes["unknown"], [])

    def test_active_world_model_must_pass_support_and_purity_regression(self) -> None:
        rows = [
            self.row(1, "Self-evolving world model", ["world_model", "embodied"]),
            self.row(2, "Self-improving world model", ["world_model", "memory_continual"]),
            self.row(3, "Continual world model optimization", ["world_model", "autonomous_science"]),
            self.row(4, "Closed-loop refinement of the world model", ["world_model", "runtime_deployment"]),
            self.row(5, "World model framework that revises deployment state", ["world_model", "embodied"]),
        ]
        audit = audit_candidate_object(rows, "world_model")
        self.assertTrue(audit["evidence_gate_pass"])
        self.assertTrue(audit["purity_gate_pass"])
        self.assertTrue(audit["ownership_gate_pass"])
        self.assertTrue(audit["active_object_lane"])
        self.assertEqual(audit["status"], "ACTIVE_OBJECT_LANE_VALIDATED")
        self.assertFalse(audit["activation_authorized"])
        self.assertFalse(audit["scientific_authority"])

    def test_single_other_lane_absorption_blocks_active_object_validation(self) -> None:
        rows = [self.row(i, "Self-evolving world model", ["world_model", "embodied"]) for i in range(1, 7)]
        audit = audit_candidate_object(rows, "world_model")
        self.assertFalse(audit["evidence_gate_pass"])
        self.assertGreater(audit["observed"]["maximum_single_existing_lane_collision"], 0.85)

    def test_parametric_candidate_excludes_explicit_frozen_weight_realizations(self) -> None:
        rows = [
            self.row(1, "We update the LoRA parameters from agent experience", ["runtime_deployment"]),
            self.row(2, "The model weights remain fixed and adaptation uses skills", ["skill_harness"]),
        ]
        config = load_scientific_object_config()
        config["support_gate"] = {**config["support_gate"], "minimum_reviewed_primary_refs": 1, "minimum_empirical_fact_supported_refs": 1, "minimum_measured_failure_supported_refs": 1}
        audit = audit_candidate_object(rows, "parametric_model_state", config=config)
        self.assertEqual(audit["observed"]["reviewed_primary_refs"], 1)
        self.assertEqual(audit["support_refs"], ["arXiv:test-1"])

    def test_support_gate_does_not_substitute_for_object_purity_gate(self) -> None:
        rows = [
            self.row(1, "Autonomous policy evolution", ["skill_harness"]),
            self.row(2, "Policy self-improvement from execution evidence", ["runtime_deployment"]),
            self.row(3, "Persistent runtime state and control policy", ["safety_reliability"]),
            self.row(4, "Policy optimization for a memory summarizer", ["memory_continual"]),
            self.row(5, "Policy optimization for harness editing", ["skill_harness"]),
            self.row(6, "Policy optimization for a robot controller", ["embodied"]),
        ]
        audit = audit_candidate_object(rows, "policy_strategy_control")
        self.assertTrue(audit["evidence_gate_pass"])
        self.assertFalse(audit["purity_gate_pass"])
        self.assertEqual(audit["observed"]["direct_object_primary_refs"], 3)
        self.assertEqual(audit["status"], "HOLD_OBJECT_PURITY_INSUFFICIENT")
        self.assertFalse(audit["activation_authorized"])

    def test_mixed_ownership_blocks_candidate_after_support_and_purity_pass(self) -> None:
        rows = [self.row(i, "Autonomous policy evolution under bounded feedback", ["skill_harness"] if i < 4 else ["runtime_deployment"]) for i in range(1, 7)]
        audit = audit_candidate_object(rows, "policy_strategy_control")
        self.assertTrue(audit["evidence_gate_pass"])
        self.assertTrue(audit["purity_gate_pass"])
        self.assertFalse(audit["ownership_gate_pass"])
        self.assertEqual(audit["object_ownership"], "mixed")
        self.assertEqual(audit["status"], "HOLD_OBJECT_OWNERSHIP_MIXED")
        self.assertFalse(audit["activation_authorized"])

    def test_full_shadow_audit_has_zero_scientific_authority(self) -> None:
        state = audit_scientific_object_ontology([])
        self.assertEqual(state["status"], "SHADOW_AUDIT_ONLY")
        self.assertFalse(state["policy"]["scientific_authority"])
        self.assertFalse(state["policy"]["automatic_lane_activation"])
        self.assertTrue(state["policy"]["support_and_object_purity_are_independent_gates"])
        self.assertTrue(state["policy"]["support_purity_and_ownership_are_independent_gates"])
        self.assertTrue(state["policy"]["ownership_requires_same_agent_persistent_state"])
        self.assertTrue(state["policy"]["external_target_artifacts_do_not_establish_agent_self_evolution"])
        self.assertTrue(state["policy"]["active_object_lanes_must_continue_to_pass_purity_regression"])
        self.assertEqual(state["summary"]["activation_authorized"], 0)


if __name__ == "__main__":
    unittest.main()
