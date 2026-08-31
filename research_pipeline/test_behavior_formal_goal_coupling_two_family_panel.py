from __future__ import annotations

import unittest
from pathlib import Path

from research_pipeline.behavior_formal_goal_coupling_two_family_panel import (
    EXPECTED_PAIR_COUNT,
    EXPECTED_RESULT_ROWS,
    FAMILIES,
    PUBLIC_EVAL_INSTANCES,
    analyze,
    load_structure,
    strict_matched_pairs,
)

STRUCTURE = Path("generated/behavior-formal-goal-coupling-challenge100-structure-projection-20260828.json")


def synthetic_rows(pairs: list[dict], high_minus_low: float) -> list[dict]:
    rows = []
    for pair in pairs:
        for family_index, family in enumerate(FAMILIES):
            family_offset = 0.01 * family_index
            for instance in PUBLIC_EVAL_INSTANCES:
                base = 0.65 + family_offset + 0.001 * instance
                rows.append(
                    {
                        "task_index": pair["low_task_index"],
                        "family": family,
                        "instance_index": instance,
                        "q_score": base,
                    }
                )
                rows.append(
                    {
                        "task_index": pair["high_task_index"],
                        "family": family,
                        "instance_index": instance,
                        "q_score": base + high_minus_low,
                    }
                )
    return rows


class TwoFamilyPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.structure = load_structure(STRUCTURE)
        cls.pairs = strict_matched_pairs(cls.structure)

    def test_strict_panel_is_13_disjoint_exact_matches(self):
        self.assertEqual(len(self.pairs), EXPECTED_PAIR_COUNT)
        task_ids = []
        for pair in self.pairs:
            lo = self.structure[pair["low_task_index"]]
            hi = self.structure[pair["high_task_index"]]
            self.assertNotEqual(lo["shared_argument_edge_count"], hi["shared_argument_edge_count"])
            for key in ("atomic_goal_count", "branch_operator_count", "goal_logic_depth", "quantifier_count"):
                self.assertEqual(lo[key], hi[key], (pair["pair_id"], key))
            self.assertGreater(pair["high_edge"], pair["low_edge"])
            task_ids.extend([pair["low_task_index"], pair["high_task_index"]])
        self.assertEqual(len(task_ids), len(set(task_ids)))
        self.assertEqual(len(task_ids), 26)
        self.assertNotIn(0, task_ids)
        self.assertNotIn(1, task_ids)

    def test_negative_synthetic_panel_supports_frozen_direction(self):
        rows = synthetic_rows(self.pairs, -0.20)
        self.assertEqual(len(rows), EXPECTED_RESULT_ROWS)
        result = analyze(rows, self.pairs)
        self.assertEqual(result["status"], "TWO_FAMILY_STRICT_PANEL_SUPPORT")
        self.assertLess(result["primary"]["observed_mean"], 0)
        self.assertLess(result["primary"]["two_sided_p"], 0.05)
        self.assertTrue(result["primary"]["pass"])

    def test_positive_synthetic_panel_does_not_support_negative_prediction(self):
        result = analyze(synthetic_rows(self.pairs, 0.20), self.pairs)
        self.assertEqual(result["status"], "TWO_FAMILY_STRICT_PANEL_NOT_SUPPORTED")
        self.assertGreater(result["primary"]["observed_mean"], 0)
        self.assertFalse(result["primary"]["pass"])

    def test_incomplete_matrix_fails_closed(self):
        rows = synthetic_rows(self.pairs, -0.20)
        with self.assertRaises(ValueError):
            analyze(rows[:-1], self.pairs)


if __name__ == "__main__":
    unittest.main()
