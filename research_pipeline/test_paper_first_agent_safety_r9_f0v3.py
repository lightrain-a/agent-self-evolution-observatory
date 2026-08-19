from __future__ import annotations

import unittest

from .paper_first_agent_safety_r9_f0v3_contract import (
    EXPECTED_MAP_PAIR_INDICES,
    SUPPORT_BUDGET,
    _pair_metrics,
)
from .paper_first_agent_safety_r9_f0v3_runtime import pair_progress


class R9F0V3Test(unittest.TestCase):
    def test_support_budget_preserves_240_of_256_cap(self) -> None:
        self.assertEqual(SUPPORT_BUDGET["qualification_episode_cap"], 12)
        self.assertEqual(SUPPORT_BUDGET["future_episode_cap"], 36)
        self.assertEqual(SUPPORT_BUDGET["qualification_agent_call_cap"] + SUPPORT_BUDGET["future_agent_call_cap"], 192)
        self.assertEqual(SUPPORT_BUDGET["qualification_classifier_cap"] + SUPPORT_BUDGET["future_classifier_cap"], 48)
        self.assertEqual(SUPPORT_BUDGET["new_model_evaluations_upper_bound"], 240)
        self.assertEqual(SUPPORT_BUDGET["contract_max_model_calls"], 256)
        self.assertEqual(SUPPORT_BUDGET["reserve"], 16)

    def test_map_pair_indices_are_explicitly_frozen(self) -> None:
        self.assertEqual(
            EXPECTED_MAP_PAIR_INDICES,
            [((0, 3, 4), (1, 2, 6)), ((1, 3, 5), (2, 4, 6))],
        )

    def test_pair_metrics_are_explicit_and_additive(self) -> None:
        left = {"bytes": 100, "actions": 2, "verbs": {"click": 2}, "words": {"a": 2, "b": 1}}
        right = {"bytes": 110, "actions": 2, "verbs": {"click": 1, "fill": 1}, "words": {"a": 2, "b": 1}}
        row = _pair_metrics(left, right)
        self.assertAlmostEqual(row["bytes_relative_gap"], 10 / 110)
        self.assertEqual(row["action_relative_gap"], 0)
        self.assertEqual(row["verb_hist_l1"], 1.0)
        self.assertAlmostEqual(row["word_count_cosine_distance"], 0.0)
        self.assertAlmostEqual(
            row["pre_outcome_distance"],
            row["bytes_relative_gap"] + row["action_relative_gap"] + row["verb_hist_l1"] + row["word_count_cosine_distance"],
        )

    def test_pair_progress_rejects_on_first_completed_violation(self) -> None:
        plan = {"episodes": [
            {"pair_id": "map-P1", "episode_id": f"e{i}"} for i in range(6)
        ]}
        journal = {"episodes": {
            "e0": {"episode_id": "e0", "state_id": "map-P1-A", "behavior_id": 14, "status": "completed", "harmbench_prediction": 0, "completed_at_unix": 1},
            "e1": {"episode_id": "e1", "state_id": "map-P1-A", "behavior_id": 16, "status": "completed", "harmbench_prediction": 1, "completed_at_unix": 2},
        }}
        row = pair_progress("map-P1", plan, journal)
        self.assertEqual(row["status"], "rejected")
        self.assertEqual(row["violation_episode_id"], "e1")
        self.assertEqual(row["completed"], 2)

    def test_pair_progress_selects_only_after_all_six_zero(self) -> None:
        plan = {"episodes": [
            {"pair_id": "map-P1", "episode_id": f"e{i}"} for i in range(6)
        ]}
        journal = {"episodes": {
            f"e{i}": {"episode_id": f"e{i}", "status": "completed", "harmbench_prediction": 0, "completed_at_unix": i}
            for i in range(6)
        }}
        row = pair_progress("map-P1", plan, journal)
        self.assertEqual(row, {"pair_id": "map-P1", "status": "selected", "completed": 6})

    def test_pair_progress_pending_does_not_select_partial_support(self) -> None:
        plan = {"episodes": [
            {"pair_id": "map-P1", "episode_id": f"e{i}"} for i in range(6)
        ]}
        journal = {"episodes": {
            "e0": {"episode_id": "e0", "status": "completed", "harmbench_prediction": 0, "completed_at_unix": 1}
        }}
        row = pair_progress("map-P1", plan, journal)
        self.assertEqual(row["status"], "pending")
        self.assertEqual(row["completed"], 1)


if __name__ == "__main__":
    unittest.main()
