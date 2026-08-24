from __future__ import annotations

import unittest

from .research_reasoning_layer import (
    build_literature_delta,
    build_proximity_projection,
    build_research_reasoning_layer_state,
    build_scientific_object_matrix,
    route_analysis_ambiguity,
    route_literature_depth,
)


class ResearchReasoningLayerTest(unittest.TestCase):
    def delta(self, **updates) -> dict:
        raw = {
            "source_ref": "paper:1", "scientific_object": "persistent update routing",
            "failure_mode": "same failure has multiple repair surfaces", "intervention": "repair surface",
            "substrate": "persistent agent", "observable": "held-out repair utility",
            "strongest_baseline": "fixed repair surface", "key_claim": "routing changes repair outcome",
            "evidence_type": "paired empirical",
        }
        raw.update(updates)
        return build_literature_delta(raw)

    def test_literature_delta_does_not_create_research_item(self) -> None:
        delta = self.delta()
        self.assertEqual(delta["status"], "DELTA_COMPLETE")
        self.assertFalse(delta["research_item_authority"])
        self.assertFalse(delta["scientific_authority"])

    def test_depth_router_is_selective(self) -> None:
        self.assertEqual(route_literature_depth(self.delta())["mode"], "FAST_SCAN")
        deep = route_literature_depth(self.delta(local_collision="nearest local STOP", implementation_decisive=True))
        self.assertEqual(deep["mode"], "DEEP_REVIEW")
        self.assertIn("local-collision", deep["reasons"])

    def test_object_matrix_is_collision_surface_not_novelty_authority(self) -> None:
        matrix = build_scientific_object_matrix([self.delta(), self.delta(source_ref="paper:2")])
        self.assertEqual(matrix["summary"]["rows"], 2)
        self.assertEqual(matrix["summary"]["duplicate_signatures"], 1)
        self.assertFalse(matrix["novelty_authority"])

    def test_proximity_uses_supplied_audited_distance_without_truth_verdict(self) -> None:
        state = build_proximity_projection("C1", [
            {"ref": "paper:A", "object_type": "prior-work", "distance": 0.2},
            {"ref": "stop:B", "object_type": "stop-branch", "distance": 0.1},
            {"ref": "failure:C", "object_type": "failure-asset", "distance": 0.3},
        ])
        self.assertEqual(state["nearest"][0]["ref"], "stop:B")
        self.assertEqual(state["novelty_verdict"], "NOT_AUTHORIZED")

    def test_analysis_ensemble_only_when_analysis_has_degrees_of_freedom(self) -> None:
        deterministic = route_analysis_ambiguity({"analysis_id": "AUC", "deterministic_metric": True, "researcher_degrees_of_freedom": ["threshold"]})
        self.assertEqual(deterministic["route"], "SINGLE_DETERMINISTIC_ANALYSIS")
        interpretive = route_analysis_ambiguity({"analysis_id": "failure-coding", "researcher_degrees_of_freedom": ["taxonomy", "case inclusion"]})
        self.assertEqual(interpretive["route"], "INDEPENDENT_ANALYSIS_ENSEMBLE")
        self.assertGreaterEqual(interpretive["minimum_independent_trajectories"], 3)
        self.assertFalse(interpretive["consensus_is_scientific_authority"])

    def test_reasoning_layer_contracts_are_zero_authority(self) -> None:
        state = build_research_reasoning_layer_state()
        self.assertEqual(state["status"], "REASONING_CONTRACTS_INSTALLED")
        self.assertEqual(state["summary"]["contracts"], 6)
        self.assertEqual(state["summary"]["automatic_scientific_authority"], 0)


if __name__ == "__main__":
    unittest.main()
