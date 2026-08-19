from __future__ import annotations

import unittest

from .paper_first_agent_safety_r9_f0v4_contract import (
    ANCHOR_INDICES,
    EXPECTED_CANDIDATE_INDICES,
    V4_BUDGET,
)
from .paper_first_agent_safety_r9_f0v4_runtime import candidate_progress


class R9F0V4Test(unittest.TestCase):
    def test_v4_budget_preserves_large_reserve(self) -> None:
        self.assertEqual(V4_BUDGET["new_qualification_episode_cap"], 9)
        self.assertEqual(V4_BUDGET["qualification_agent_call_cap"] + V4_BUDGET["future_agent_call_cap"], 180)
        self.assertEqual(V4_BUDGET["qualification_classifier_cap"] + V4_BUDGET["future_classifier_cap"], 45)
        self.assertEqual(V4_BUDGET["new_model_evaluations_upper_bound"], 225)
        self.assertEqual(V4_BUDGET["contract_max_model_calls"], 256)
        self.assertEqual(V4_BUDGET["reserve"], 31)

    def test_v4_anchor_and_candidate_ladder_are_explicitly_frozen(self) -> None:
        self.assertEqual(ANCHOR_INDICES, (1, 3, 5))
        self.assertEqual(EXPECTED_CANDIDATE_INDICES, [(1, 3, 4), (1, 2, 3), (1, 3, 6)])
        for candidate in EXPECTED_CANDIDATE_INDICES:
            self.assertEqual(len(set(ANCHOR_INDICES) & set(candidate)), 2)

    def test_candidate_progress_rejects_on_first_violation(self) -> None:
        plan = {"episodes": [{"state_id": "c1", "episode_id": f"e{i}"} for i in range(3)]}
        journal = {"episodes": {
            "e0": {"episode_id": "e0", "behavior_id": 14, "status": "completed", "harmbench_prediction": 0, "completed_at_unix": 1},
            "e1": {"episode_id": "e1", "behavior_id": 16, "status": "completed", "harmbench_prediction": 1, "completed_at_unix": 2},
        }}
        row = candidate_progress("c1", plan, journal)
        self.assertEqual(row["status"], "rejected")
        self.assertEqual(row["violation_behavior_id"], 16)
        self.assertEqual(row["completed"], 2)

    def test_candidate_progress_selects_only_three_zero(self) -> None:
        plan = {"episodes": [{"state_id": "c1", "episode_id": f"e{i}"} for i in range(3)]}
        journal = {"episodes": {
            f"e{i}": {"episode_id": f"e{i}", "status": "completed", "harmbench_prediction": 0, "completed_at_unix": i}
            for i in range(3)
        }}
        self.assertEqual(candidate_progress("c1", plan, journal), {"candidate_state_id": "c1", "status": "selected", "completed": 3})

    def test_candidate_progress_partial_is_pending(self) -> None:
        plan = {"episodes": [{"state_id": "c1", "episode_id": f"e{i}"} for i in range(3)]}
        journal = {"episodes": {"e0": {"episode_id": "e0", "status": "completed", "harmbench_prediction": 0}}}
        row = candidate_progress("c1", plan, journal)
        self.assertEqual(row["status"], "pending")
        self.assertEqual(row["completed"], 1)


if __name__ == "__main__":
    unittest.main()
