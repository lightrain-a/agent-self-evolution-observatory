from __future__ import annotations

import unittest

from research_pipeline.behavior_formal_goal_coupling_demo_horizon_v1_1 import (
    EXPOSED_TASK_INDICES,
    fixed_effect_edge_fit,
    frozen_matched_pairs,
    matched_pair_corroboration,
    stratified_permutation_pvalue,
)


def synthetic_structure() -> list[dict]:
    rows = []
    for i in range(100):
        goal = 2 + (i % 8)
        edge = (i // 8) % max(goal, 2)
        rows.append(
            {
                "activity": f"task_{i:03d}",
                "atomic_goal_count": goal,
                "shared_argument_edge_count": edge,
                "goal_logic_depth": 1 + ((i // 32) % 2),
                "branch_operator_count": 0,
                "quantifier_count": i % 3,
            }
        )
    rows[0]["activity"] = "turning_on_radio"
    rows[0]["atomic_goal_count"] = 1
    rows[0]["shared_argument_edge_count"] = 0
    return rows


def synthetic_outcomes(structure: list[dict], sign: float = 1.0) -> list[dict]:
    out = []
    for task_index, row in enumerate(structure):
        if task_index in EXPOSED_TASK_INDICES:
            continue
        edge = float(row["shared_argument_edge_count"])
        goal = float(row["atomic_goal_count"])
        log_horizon = 4.0 + 0.05 * goal + sign * 0.08 * edge + 0.002 * ((task_index % 5) - 2)
        out.append(
            {
                "task_index": task_index,
                "activity": row["activity"],
                "atomic_goal_count": int(goal),
                "shared_argument_edge_count": int(edge),
                "branch_operator_count": int(row["branch_operator_count"]),
                "log_median_episode_length_frames": log_horizon,
            }
        )
    return out


class DemoHorizonTest(unittest.TestCase):
    def test_pair_selection_is_deterministic_and_excludes_exposed_task(self):
        rows = synthetic_structure()
        a = frozen_matched_pairs(rows, 16)
        b = frozen_matched_pairs(rows, 16)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 16)
        used = []
        for pair in a:
            self.assertNotIn(pair["low_task_index"], EXPOSED_TASK_INDICES)
            self.assertNotIn(pair["high_task_index"], EXPOSED_TASK_INDICES)
            self.assertEqual(pair["atomic_goal_count"], rows[pair["low_task_index"]]["atomic_goal_count"])
            self.assertGreater(pair["edge_gap"], 0)
            self.assertLessEqual(
                abs(pair["low_goal_logic_depth"] - pair["high_goal_logic_depth"]), 1
            )
            used.extend((pair["low_task_index"], pair["high_task_index"]))
        self.assertEqual(len(used), len(set(used)))

    def test_fixed_effect_fit_recovers_positive_edge_effect(self):
        rows = synthetic_structure()
        outcomes = synthetic_outcomes(rows, sign=1.0)
        fit = fixed_effect_edge_fit(outcomes)
        self.assertGreater(fit["beta_edge"], 0.07)
        self.assertLess(fit["beta_edge"], 0.09)
        self.assertEqual(fit["n_tasks"], 98)

    def test_stratified_permutation_detects_synthetic_effect(self):
        rows = synthetic_structure()
        outcomes = synthetic_outcomes(rows, sign=1.0)
        result = stratified_permutation_pvalue(outcomes, permutations=2500, seed=123)
        self.assertGreater(result["observed_beta_edge"], 0.07)
        self.assertLess(result["two_sided_p"], 0.01)

    def test_matched_pair_direction_tracks_positive_effect(self):
        rows = synthetic_structure()
        outcomes = synthetic_outcomes(rows, sign=1.0)
        pairs = frozen_matched_pairs(rows, 16)
        result = matched_pair_corroboration(outcomes, pairs)
        self.assertEqual(result["pair_count"], 16)
        self.assertGreater(result["positive_pair_count"], result["negative_pair_count"])
        self.assertGreater(result["mean_high_minus_low_log_median_frames"], 0.0)

    def test_negative_synthetic_effect_is_not_misread_as_positive(self):
        rows = synthetic_structure()
        outcomes = synthetic_outcomes(rows, sign=-1.0)
        fit = fixed_effect_edge_fit(outcomes)
        self.assertLess(fit["beta_edge"], -0.07)


if __name__ == "__main__":
    unittest.main()
