from __future__ import annotations

import unittest

from .behavior_formal_goal_coupling_distribution import summarize_distribution


def _row(size: int, edges: int, *, branch: int = 0, unbound: int = 0) -> dict:
    return {
        "atomic_goal_count": size,
        "shared_argument_edge_count": edges,
        "largest_connected_component_size": min(size, max(1, edges + 1)),
        "goal_logic_depth": 1 + (size % 3),
        "branch_operator_count": branch,
        "unbound_variable_count": unbound,
    }


class BehaviorFormalGoalCouplingDistributionTest(unittest.TestCase):
    def varied_rows(self) -> list[dict]:
        rows = []
        for _ in range(10):
            for size in (2, 3, 4, 5):
                for edges in (0, 1, 2):
                    rows.append(_row(size, edges))
        return rows

    def test_varied_structure_passes_frozen_gate(self) -> None:
        result = summarize_distribution(self.varied_rows())
        self.assertEqual(result["nontrivial_task_count"], 120)
        self.assertTrue(result["gates"]["pass"])
        self.assertLess(abs(result["shared_argument_edge_vs_atomic_goal_spearman"]), 0.90)

    def test_branch_fraction_over_30_percent_holds(self) -> None:
        rows = self.varied_rows()
        for row in rows[:37]:
            row["branch_operator_count"] = 1
        result = summarize_distribution(rows)
        self.assertGreater(result["branch_bearing_task_fraction"], 0.30)
        self.assertFalse(result["gates"]["branch_overapproximation_not_dominant"])
        self.assertFalse(result["gates"]["pass"])

    def test_near_perfect_size_redundancy_holds(self) -> None:
        rows = [_row(2 + (i % 5), 2 + (i % 5)) for i in range(120)]
        result = summarize_distribution(rows)
        self.assertGreaterEqual(abs(result["shared_argument_edge_vs_atomic_goal_spearman"]), 0.90)
        self.assertFalse(result["gates"]["coupling_not_almost_redundant_with_size"])
        self.assertFalse(result["gates"]["pass"])

    def test_dominant_zero_coupling_holds(self) -> None:
        rows = [_row(2 + (i % 4), 0 if i < 115 else 1) for i in range(120)]
        result = summarize_distribution(rows)
        self.assertGreaterEqual(result["shared_argument_edge_count_dominant_value_fraction"], 0.90)
        self.assertFalse(result["gates"]["shared_argument_edge_count_has_variance"])

    def test_parser_or_unbound_error_is_fail_closed(self) -> None:
        rows = self.varied_rows()
        rows[0]["unbound_variable_count"] = 1
        result = summarize_distribution(rows, parser_error_tasks=1)
        self.assertFalse(result["gates"]["parser_errors_zero"])
        self.assertFalse(result["gates"]["unbound_variable_tasks_zero"])
        self.assertFalse(result["gates"]["pass"])


if __name__ == "__main__":
    unittest.main()
