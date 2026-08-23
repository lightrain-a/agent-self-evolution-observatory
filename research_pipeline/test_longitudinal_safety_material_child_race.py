from __future__ import annotations

import copy
import unittest

from .longitudinal_safety_material_child_race import build_material_child_race, validate_material_child_race


class LongitudinalSafetyMaterialChildRaceTest(unittest.TestCase):
    def test_all_three_material_parent_vectors_are_mutated_and_reduced(self) -> None:
        state = build_material_child_race(generated_at="2026-08-24T02:30:00+08:00")
        self.assertEqual(validate_material_child_race(state), [])
        self.assertEqual(state["summary"]["material_parents"], 3)
        self.assertEqual(state["summary"]["children_generated"], 3)
        self.assertEqual(state["summary"]["children_reduced_before_execution"], 3)
        self.assertEqual(state["summary"]["survivors"], 0)
        self.assertEqual(state["summary"]["debate_eligible"], 0)
        self.assertEqual(state["summary"]["provider_calls_authorized"], 0)
        self.assertEqual(state["summary"]["gpu_authorized"], 0)
        self.assertEqual(
            {row["parent_id"] for row in state["children"]},
            {
                "verified-risk-predicate-grammar",
                "version-differential-active-diagnosis",
                "counterfactual-correction-production-grammar",
            },
        )
        self.assertTrue(all(row["decision"].startswith("STOP_") for row in state["children"]))

    def test_same_information_reduction_is_mandatory(self) -> None:
        state = build_material_child_race(generated_at="2026-08-24T02:30:00+08:00")
        broken = copy.deepcopy(state)
        broken["children"][0]["strongest_reduction"]["same_information"] = ""
        self.assertIn(
            "child-reduction-incomplete:goal-queryable-transition-successor-model",
            validate_material_child_race(broken),
        )

    def test_child_cannot_be_promoted_by_manual_edit(self) -> None:
        state = build_material_child_race(generated_at="2026-08-24T02:30:00+08:00")
        broken = copy.deepcopy(state)
        broken["children"][1]["problem_gate_eligible"] = True
        broken["summary"]["problem_gate_eligible"] = 1
        errors = validate_material_child_race(broken)
        self.assertIn("illegal-promotion", errors)
        self.assertIn("child-promotion:version-contrastive-repair-transport-operator", errors)

    def test_object_change_is_not_enough_without_irreducible_prediction(self) -> None:
        state = build_material_child_race(generated_at="2026-08-24T02:30:00+08:00")
        for child in state["children"]:
            self.assertTrue(child["material_change"])
            self.assertTrue(child["scientific_object"])
            self.assertTrue(child["strongest_reduction"]["exact_reduction"])
            self.assertTrue(child["cheapest_falsifier"])
            self.assertTrue(child["reopen_condition"])
            self.assertFalse(child["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
