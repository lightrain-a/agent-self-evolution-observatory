from __future__ import annotations

import copy
import unittest

from .ai4ai_strategy_reopen_contradiction import (
    build_ai4ai_strategy_reopen_contradiction,
    validate_ai4ai_strategy_reopen_contradiction,
)


class AI4AIStrategyReopenContradictionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = build_ai4ai_strategy_reopen_contradiction(generated_at="2026-08-24T00:00:00+00:00")

    def test_endpoint_is_supported_but_reopen_is_not(self) -> None:
        summary = self.payload["summary"]
        self.assertEqual(self.payload["status"], "HOLD_SUPPORT_LEAD_NO_SCIENTIFIC_REOPEN")
        self.assertEqual(summary["outcome_independent_endpoint_supported"], 1)
        self.assertEqual(summary["recognition_positive_units_verified"], 0)
        self.assertEqual(summary["compute_search_matched"], 0)
        self.assertEqual(summary["contradictory_evidence_sufficient"], 0)
        self.assertEqual(summary["scientific_reopen_authorized"], 0)
        self.assertEqual(validate_ai4ai_strategy_reopen_contradiction(self.payload), [])

    def test_reasoning_effort_is_explicitly_compute_confounded(self) -> None:
        delta = self.payload["source_facts"]["aggregate_effort_delta"]
        self.assertEqual(delta["lowest_to_highest_effort_learning_touch_share"], [0.08, 0.64])
        self.assertEqual(delta["codex_median_evaluations_per_task"], [4, 16])
        self.assertEqual(delta["codex_median_output_tokens"], [11000, 109000])
        tests = {row["key"]: row for row in self.payload["qualification_tests"]}
        self.assertFalse(tests["MATCHED_COMPUTE_SEARCH_AND_ACTION_SUPPORT"]["pass"])

    def test_task_instruction_cannot_substitute_for_recognition_positive_prefix(self) -> None:
        tests = {row["key"]: row for row in self.payload["qualification_tests"]}
        recognition = tests["INDEPENDENT_RECOGNITION_POSITIVE_PREFIX"]
        self.assertFalse(recognition["pass"])
        self.assertIn("not equivalent", recognition["reason"])
        self.assertIn("recognition-positive", self.payload["reopen_path"]["decisive_intervention"])

    def test_manual_reopen_or_execution_authority_is_rejected(self) -> None:
        for key in ("scientific_reopen_authorized", "problem_gate_eligible", "provider_calls_authorized", "gpu_authorized", "sealed_v19_units_consumed"):
            broken = copy.deepcopy(self.payload)
            broken["summary"][key] = 1
            self.assertTrue(validate_ai4ai_strategy_reopen_contradiction(broken), key)

    def test_manual_recognition_upgrade_is_rejected(self) -> None:
        broken = copy.deepcopy(self.payload)
        by_key = {row["key"]: row for row in broken["qualification_tests"]}
        by_key["INDEPENDENT_RECOGNITION_POSITIVE_PREFIX"]["pass"] = True
        broken["summary"]["recognition_positive_units_verified"] = 1
        self.assertTrue(validate_ai4ai_strategy_reopen_contradiction(broken))


if __name__ == "__main__":
    unittest.main()
