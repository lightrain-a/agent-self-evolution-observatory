import unittest
from unittest.mock import patch

from research_pipeline.failure_memory_reasoningbank_live_support_r11 import (
    validate_all_shopping,
    validate_smokes,
)


class TestReasoningBankLiveSupportR11(unittest.TestCase):
    def test_all_shopping_accepts_one_site_per_task(self):
        raw = [
            {"task_id": 1, "sites": ["shopping"]},
            {"task_id": 2, "sites": ["shopping"]},
        ]
        got = validate_all_shopping(raw, ["1", "2"])
        self.assertEqual(got, {"1": ["shopping"], "2": ["shopping"]})

    def test_all_shopping_rejects_cross_site(self):
        raw = [{"task_id": 1, "sites": ["shopping", "reddit"]}]
        with self.assertRaises(ValueError):
            validate_all_shopping(raw, ["1"])

    def test_smoke_rejects_evaluator_call(self):
        reset = {
            "reset_pass": True,
            "env_closed": True,
            "action_executed": False,
            "scientific_outcome_opened": False,
        }
        evaluator = {
            **reset,
            "evaluator_constructed": True,
            "evaluator_called": True,
            "task_sites": ["shopping"],
        }
        with self.assertRaises(ValueError):
            validate_smokes(reset, evaluator)

    def test_smoke_accepts_zero_action_zero_outcome(self):
        reset = {
            "reset_pass": True,
            "env_closed": True,
            "action_executed": False,
            "scientific_outcome_opened": False,
        }
        evaluator = {
            **reset,
            "evaluator_constructed": True,
            "evaluator_called": False,
            "task_sites": ["shopping"],
        }
        validate_smokes(reset, evaluator)


if __name__ == "__main__":
    unittest.main()
