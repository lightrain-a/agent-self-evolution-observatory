from __future__ import annotations

import unittest

from .methodology_controls import build_methodology_controls_state


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


if __name__ == "__main__":
    unittest.main()
