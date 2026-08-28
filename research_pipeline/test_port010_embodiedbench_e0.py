from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .port010_embodiedbench_e0 import (
    complexbench_calibration,
    complexbench_edit_chain_check,
    complexbench_edit_graph_calibration,
    binding_features,
    constraint_graph_features,
    preregistration_contract,
    project_raw_dataset,
    summarize_projection,
    validate_projection,
)


class Port010EmbodiedBenchE0Test(unittest.TestCase):
    def test_binding_features_are_deterministic_and_longest_phrase_safe(self) -> None:
        text = "Move both red cups to the left of the blue bowl, then place one behind it without moving the green plate."
        first = binding_features(text)
        second = binding_features(text)
        self.assertEqual(first, second)
        self.assertEqual(first["spatial_relation_count"], 2)  # to the left of; behind
        self.assertEqual(first["ordering_dependency_count"], 1)  # then
        self.assertGreaterEqual(first["quantifier_constraint_count"], 2)  # both; one
        self.assertGreaterEqual(first["referential_dependency_count"], 1)  # it
        self.assertEqual(first["negation_exclusion_count"], 1)  # without
        self.assertGreaterEqual(first["attribute_binding_count"], 3)  # red; blue; green
        self.assertGreater(first["binding_load_v1"], first["binding_load_core"])

    def test_orange_is_not_assumed_to_be_color_binding(self) -> None:
        feat = binding_features("Move the orange from the table to the sink.")
        self.assertEqual(feat["attribute_binding_count"], 0)

    def test_projection_strips_all_outcome_bearing_fields(self) -> None:
        source = [{
            "model_name": "m",
            "eval_set": "base",
            "episode_id": 1,
            "instruction": "Put the red cup on the left table.",
            "success": 1.0,
            "input": "hidden prompt",
            "trajectory": [{"action_success": 1.0, "env_feedback": "ok"}],
        }]
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "raw.json"
            p.write_text(json.dumps(source), encoding="utf-8")
            out = project_raw_dataset("EB-Habitat", p)
        self.assertEqual(out["record_count"], 1)
        row = out["records"][0]
        self.assertEqual(set(row), {"environment", "model_name", "eval_set", "episode_id", "instruction", "instruction_sha256", "features"})
        self.assertFalse(out["outcome_fields_projected"])
        validate_projection(out)

    def test_validator_rejects_outcome_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "forbidden outcome-bearing key"):
            validate_projection({"safe": {"success": 0.0}})

    def test_complexbench_calibration_tracks_known_constraint_structure(self) -> None:
        rows = [
            {"instruction_en": "Write a response.", "constraint_dimensions": ["Helpfulness"], "composition_types": [], "scoring_questions": [{"dep": []}]},
            {"instruction_en": "Write exactly two short bullet points.", "constraint_dimensions": ["Length", "Bullets"], "composition_types": ["And"], "scoring_questions": [{"dep": []}, {"dep": [0]}]},
            {"instruction_en": "First move the red object to the left, then move the blue object behind it without touching the green object.", "constraint_dimensions": ["Order", "Spatial", "Exclusion"], "composition_types": ["And", "Dependency"], "scoring_questions": [{"dep": []}, {"dep": [0]}, {"dep": [0, 1]}]},
            {"instruction_en": "Move both red objects to the left of the blue object, then place one behind it, and never move the green object.", "constraint_dimensions": ["Order", "Spatial", "Quantity", "Exclusion"], "composition_types": ["And", "Dependency", "Selection"], "scoring_questions": [{"dep": []}, {"dep": [0]}, {"dep": [0, 1]}, {"dep": [0, 1, 2]}]},
        ]
        result = complexbench_calibration(rows)
        self.assertEqual(result["records"], 4)
        self.assertEqual(result["role"], "DEVELOPMENT_CALIBRATION_NOT_HOLDOUT")
        self.assertIsNotNone(result["diagnostics"]["raw_v1_dependency_edges_spearman"])
        self.assertIn("initial_gate_failed", result["audit_trail"])

    def test_complexbench_edit_chain_check_requires_higher_three_chain_density(self) -> None:
        two = ["Move the red cup left, then put it on the table.", "Move both cups behind the bowl."]
        three = [
            "First move both red cups to the left of the blue bowl, then place one behind it, and finally move the green plate without touching the bowl.",
            "Move the red object left, then put the blue object behind it, then place both next to the green object without moving the yellow one.",
        ]
        result = complexbench_edit_chain_check(two, three)
        self.assertTrue(result["gate"]["three_chain_median_gt_two_chain"])

    def test_constraint_graph_recovers_explicit_entity_dependency_chain(self) -> None:
        two_chain = "Change the cat to a white dog. Add a collar on the white dog. Delete the keyboard."
        three_chain = "Change the boat to a white sailboat. Add a sail on the white sailboat. Change the content of the sail to a smile face."
        two = constraint_graph_features(two_chain)
        three = constraint_graph_features(three_chain)
        self.assertEqual(two["constraint_clause_count_v2"], 3)
        self.assertEqual(three["constraint_clause_count_v2"], 3)
        self.assertEqual(two["text_dependency_depth_v2"], 2)
        self.assertEqual(three["text_dependency_depth_v2"], 3)
        self.assertGreater(three["adjacent_dependency_edges_v2"], two["adjacent_dependency_edges_v2"])

    def test_constraint_graph_does_not_invent_chain_in_single_clause(self) -> None:
        feat = constraint_graph_features("Move the red cup to the left table.")
        self.assertEqual(feat["constraint_clause_count_v2"], 1)
        self.assertEqual(feat["adjacent_dependency_edges_v2"], 0)
        self.assertEqual(feat["text_dependency_depth_v2"], 1)
        self.assertEqual(feat["has_text_dependency_v2"], 0)

    def test_graph_calibration_recovers_chain_structure(self) -> None:
        two = [
            "Change the cat to a white dog. Add a collar on the white dog. Delete the keyboard.",
            "Change the cup to a glass mug. Add juice in the glass mug. Delete the plate.",
        ]
        three = [
            "Change the boat to a white sailboat. Add a sail on the white sailboat. Change the content of the sail to a smile face.",
            "Replace the horse with a brown cow. Add a bell on the cow. Change the bell to gold.",
        ]
        result = complexbench_edit_graph_calibration(two, three)
        self.assertEqual(result["role"], "DEVELOPMENT_CHAIN_RECOVERY_NOT_HOLDOUT")
        self.assertGreater(result["three_chain_depth_median"], result["two_chain_depth_median"])
        self.assertTrue(result["development_gate"]["three_depth_median_gt_two"])

    def test_summary_uses_labels_only_for_construct_gate(self) -> None:
        projections = [{
            "records": [
                {"environment": "EB-Habitat", "model_name": "m", "eval_set": "base", "episode_id": "1", "instruction": "Move the cup.", "instruction_sha256": "a", "features": {"binding_load_v1": 1, "binding_density_v1_1": 10.0, "token_count": 10, "adjacent_dependency_edges_v2": 0, "text_dependency_depth_v2": 1, "has_text_dependency_v2": 0}},
                {"environment": "EB-Habitat", "model_name": "m", "eval_set": "complex_instruction", "episode_id": "2", "instruction": "Move the cup. Put the cup on the table.", "instruction_sha256": "b", "features": {"binding_load_v1": 4, "binding_density_v1_1": 33.3333333333, "token_count": 12, "adjacent_dependency_edges_v2": 2, "text_dependency_depth_v2": 3, "has_text_dependency_v2": 1}},
            ]
        }]
        summary = summarize_projection(projections)
        self.assertEqual(summary["rollout_records"], 2)
        self.assertEqual(summary["unique_tasks"], 2)
        self.assertEqual(summary["environment_summary"][0]["complex_minus_base_edge_median"], 2)
        self.assertEqual(summary["environment_summary"][0]["complex_minus_base_depth_median"], 2)

    def test_contract_has_zero_authority_and_vwe_is_not_rescue_evidence(self) -> None:
        c = preregistration_contract()
        self.assertFalse(c["scientific_authority"])
        self.assertFalse(c["execution_authority"])
        self.assertFalse(c["outcome_access_authorized"])
        self.assertIn("ConstraintGraph-v2", c["primary_predictor"])
        self.assertIn("can never rescue", c["vwe_rule"])
        self.assertEqual(c["discovery_environments"], ["EB-Habitat", "EB-Manipulation"])
        self.assertEqual(c["heldout_environments"], ["EB-Navigation", "EB-ALFRED"])


if __name__ == "__main__":
    unittest.main()
