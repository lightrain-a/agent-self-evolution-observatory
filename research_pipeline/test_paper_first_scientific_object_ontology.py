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
        axes = current_lane_axes(["skill_harness", "embodied", "safety_reliability"])
        self.assertEqual(axes["object"], ["skill_harness"])
        self.assertEqual(axes["context"], ["embodied"])
        self.assertEqual(axes["property"], ["safety_reliability"])
        self.assertEqual(axes["unknown"], [])

    def test_world_model_can_pass_shadow_support_without_live_activation(self) -> None:
        rows = [
            self.row(1, "Self-evolving world model", ["embodied"]),
            self.row(2, "Federated world model", ["memory_continual"]),
            self.row(3, "Continual world-model optimization", ["autonomous_science"]),
            self.row(4, "World modeling for agents", ["runtime_deployment"]),
            self.row(5, "Adaptive world action model", ["embodied"]),
        ]
        audit = audit_candidate_object(rows, "world_model")
        self.assertTrue(audit["evidence_gate_pass"])
        self.assertEqual(audit["status"], "SHADOW_READY_FOR_PREREGISTRATION")
        self.assertFalse(audit["activation_authorized"])
        self.assertFalse(audit["scientific_authority"])

    def test_single_existing_lane_absorption_blocks_shadow_readiness(self) -> None:
        rows = [self.row(i, "Adaptive world model", ["embodied"]) for i in range(1, 7)]
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

    def test_object_purity_hold_prevents_automatic_lane_creation(self) -> None:
        rows = [self.row(i, "Autonomous policy evolution and strategy optimization", ["skill_harness"] if i < 4 else ["runtime_deployment"]) for i in range(1, 7)]
        audit = audit_candidate_object(rows, "policy_strategy_control")
        self.assertTrue(audit["evidence_gate_pass"])
        self.assertEqual(audit["status"], "HOLD_OBJECT_PURITY_REVIEW")
        self.assertFalse(audit["activation_authorized"])

    def test_full_shadow_audit_has_zero_scientific_authority(self) -> None:
        state = audit_scientific_object_ontology([])
        self.assertEqual(state["status"], "SHADOW_AUDIT_ONLY")
        self.assertFalse(state["policy"]["scientific_authority"])
        self.assertFalse(state["policy"]["automatic_lane_activation"])
        self.assertEqual(state["summary"]["activation_authorized"], 0)


if __name__ == "__main__":
    unittest.main()
