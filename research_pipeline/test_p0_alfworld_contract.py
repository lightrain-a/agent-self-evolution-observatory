from __future__ import annotations

import unittest

from .p0_alfworld_contract import (
    balanced_hidden_assignments,
    behavior_probe_features,
    build_a1_row,
    build_a2_round,
    estimate_a1_episodes,
    estimate_a2_episodes,
)
from .p0_common import load_json
from .p0_runner import config_path


def trace(task: str, success: float, actions: list[str], invalid: int = 0, calls: int | None = None):
    return {
        "task_id": task,
        "success": success,
        "actions": actions,
        "invalid_actions": invalid,
        "model_calls": calls if calls is not None else len(actions),
    }


class AlfworldContractTest(unittest.TestCase):
    def test_balanced_hidden_assignment_is_deterministic_and_balanced(self):
        candidates = [f"u{i:02d}" for i in range(24)]
        tasks = [f"h{i:02d}" for i in range(24)]
        first = balanced_hidden_assignments(candidates, tasks, 8, 42)
        second = balanced_hidden_assignments(reversed(candidates), reversed(tasks), 8, 42)
        self.assertEqual(first, second)
        counts = {task: 0 for task in tasks}
        for chosen in first.values():
            self.assertEqual(len(chosen), 8)
            for task in chosen:
                counts[task] += 1
        self.assertLessEqual(max(counts.values()) - min(counts.values()), 1)

    def test_behavior_features_are_matched_and_interpretable(self):
        before = [trace("a", 1, ["look", "open fridge"]), trace("b", 1, ["look", "take apple"])]
        after = [trace("a", 1, ["look", "open fridge"]), trace("b", 0, ["inventory", "look", "take apple"], 1)]
        base, updated = behavior_probe_features(before, after)
        self.assertEqual(base["action_sequence_distance"], 0.0)
        self.assertGreater(updated["action_sequence_distance"], 0.0)
        self.assertGreater(updated["invalid_action_rate"], base["invalid_action_rate"])
        self.assertEqual(base["instruction_choice_shift"], 0.0)
        self.assertGreater(updated["instruction_choice_shift"], 0.0)

    def test_a1_row_keeps_hidden_truth_matched(self):
        row = build_a1_row(
            "u1",
            trace("current", 0, ["look"]),
            trace("current", 1, ["look", "take apple"]),
            0.12,
            [trace("p1", 1, ["look"])],
            [trace("p1", 1, ["look", "inventory"])],
            [trace("h2", 0, ["look"]), trace("h1", 1, ["look"])],
            [trace("h1", 0, ["look"]), trace("h2", 0, ["look"])],
        )
        self.assertEqual(row["current_task_gain"], 1.0)
        self.assertEqual(row["hidden_task_ids"], ["h1", "h2"])
        self.assertEqual(row["hidden_before"], [1.0, 0.0])
        self.assertEqual(row["hidden_after"], [0.0, 0.0])

    def test_a2_round_uses_same_sequence_and_independent_probe_truth(self):
        row = build_a2_round(
            2,
            trace("task", 0, ["look"]),
            trace("task", 1, ["look", "take apple"], calls=2),
            [trace("p1", 1, ["look"]), trace("p2", 1, ["look"])],
            [trace("p1", 1, ["look"]), trace("p2", 0, ["inventory", "look"])],
            17,
        )
        self.assertEqual(row["marginal_gain"], 1.0)
        self.assertEqual(row["probe_regression"], 0.5)
        self.assertEqual(row["regression"], 1.0)
        self.assertEqual(row["cumulative_calls"], 17)

    def test_a1_resource_plan_fits_frozen_cap(self):
        config = load_json(config_path("update-trust-region"))
        estimate = estimate_a1_episodes(config)
        self.assertEqual(estimate["total"], 460)
        self.assertEqual(estimate["worst_case_total"], 472)
        self.assertLessEqual(estimate["worst_case_total"], config["resource_cap"]["episodes"])

    def test_a2_resource_plan_fits_frozen_cap(self):
        config = load_json(config_path("budgeted-evolution-controller"))
        estimate = estimate_a2_episodes(config)
        self.assertEqual(estimate["total"], 366)
        self.assertLessEqual(estimate["total"], config["resource_cap"]["episodes"])


if __name__ == "__main__":
    unittest.main()
