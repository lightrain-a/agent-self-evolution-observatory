from __future__ import annotations

import unittest

from research_pipeline.e2_r17_evaluator_qualification import (
    decide_evaluator_qualification,
)


class EvaluatorQualificationDecisionTest(unittest.TestCase):
    def test_pass_requires_headroom_competence_stability_and_completed_calls(self):
        decision = decide_evaluator_qualification(
            scores_by_task={
                "a": [1, 1, 1],
                "b": [1, 1, 1],
                "c": [0, 0, 0],
                "d": [0, 0, 0],
                "e": [0, 0, 0],
                "f": [0, 1, 0],
            },
            provider_statuses=["completed"] * 18,
        )
        self.assertEqual(
            decision.status,
            "PASS_HOSTED_EVALUATOR_DEVELOPMENT_QUALIFICATION",
        )
        self.assertEqual(decision.total_successes, 7)
        self.assertEqual(decision.successful_task_count, 3)
        self.assertEqual(decision.exactly_stable_task_count, 5)

    def test_floor_fails(self):
        decision = decide_evaluator_qualification(
            scores_by_task={key: [0, 0, 0] for key in "abcdef"},
            provider_statuses=["completed"] * 18,
        )
        self.assertEqual(
            decision.status,
            "FAIL_HOSTED_EVALUATOR_DEVELOPMENT_QUALIFICATION",
        )
        self.assertFalse(decision.nondegenerate_headroom)
        self.assertFalse(decision.multi_task_competence)

    def test_instability_fails(self):
        decision = decide_evaluator_qualification(
            scores_by_task={
                "a": [1, 0, 1],
                "b": [1, 0, 1],
                "c": [1, 0, 1],
                "d": [1, 0, 1],
                "e": [1, 0, 1],
                "f": [0, 0, 0],
            },
            provider_statuses=["completed"] * 18,
        )
        self.assertFalse(decision.endpoint_stability)

    def test_incomplete_provider_call_fails(self):
        decision = decide_evaluator_qualification(
            scores_by_task={
                "a": [1, 1, 1],
                "b": [1, 1, 1],
                "c": [0, 0, 0],
                "d": [0, 0, 0],
                "e": [0, 0, 0],
                "f": [0, 0, 0],
            },
            provider_statuses=["completed"] * 17 + ["incomplete"],
        )
        self.assertFalse(decision.all_provider_calls_completed)
        self.assertTrue(decision.endpoint_stability)
        self.assertEqual(
            decision.status,
            "FAIL_HOSTED_EVALUATOR_DEVELOPMENT_QUALIFICATION",
        )


if __name__ == "__main__":
    unittest.main()
