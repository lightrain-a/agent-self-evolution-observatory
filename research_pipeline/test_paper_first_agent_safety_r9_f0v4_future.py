from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_f0v4_future_contract import FUTURE_BUDGET
from .paper_first_agent_safety_r9_f0v4_future_runtime import summarize_future


class R9F0V4FutureTest(unittest.TestCase):
    def test_future_budget_preserves_selected_support_cap(self) -> None:
        self.assertEqual(FUTURE_BUDGET["future_behavior_episodes"], 36)
        self.assertEqual(FUTURE_BUDGET["agent_model_calls_upper_bound"], 144)
        self.assertEqual(FUTURE_BUDGET["classifier_evaluations_upper_bound"], 36)
        self.assertEqual(FUTURE_BUDGET["future_model_evaluations_upper_bound"], 180)
        self.assertEqual(FUTURE_BUDGET["support_model_evaluations_actual"], 15)
        self.assertEqual(FUTURE_BUDGET["combined_v4_model_evaluations_upper_bound_after_selection"], 195)
        self.assertEqual(FUTURE_BUDGET["v4_contract_max_model_calls"], 256)
        self.assertEqual(FUTURE_BUDGET["reserve_after_selected_support"], 61)

    def test_summary_extracts_first_violation_and_censoring(self) -> None:
        states = ["mA", "mB", "rA", "rB"]
        seeds = [11, 23, 37]
        episodes = {}
        for sid in states:
            for seed in seeds:
                for step in (1, 2, 3):
                    pred = 0
                    if sid == "mB" and seed == 11 and step >= 2:
                        pred = 1
                    eid = f"{sid}-{seed}-{step}"
                    episodes[eid] = {
                        "episode_id": eid,
                        "phase": "future",
                        "status": "completed",
                        "state_id": sid,
                        "branch_seed": seed,
                        "future_step": step,
                        "harmbench_prediction": pred,
                    }
        contract = {
            "frozen_contract_sha256": "c",
            "selected_states": [{"state_id": sid} for sid in states],
            "state_pairs": [
                {"pair_id": "map", "left": "mA", "right": "mB"},
                {"pair_id": "reddit", "left": "rA", "right": "rB"},
            ],
        }
        plan = {"plan_sha256": "p"}
        journal = {"episodes": episodes, "counters": {"completed_episodes": 36}}
        with tempfile.TemporaryDirectory() as tmp:
            row = summarize_future(Path(tmp), contract, plan, journal)
        self.assertEqual(row["survival"]["mB"]["11"]["first_violation_step"], 2)
        self.assertTrue(row["survival"]["mB"]["11"]["event_observed"])
        self.assertEqual(row["survival"]["mA"]["11"]["first_violation_step"], None)
        self.assertTrue(row["survival"]["mA"]["11"]["censored_at_horizon"])
        self.assertEqual(row["survival"]["mA"]["11"]["survival_time"], 3)


if __name__ == "__main__":
    unittest.main()
