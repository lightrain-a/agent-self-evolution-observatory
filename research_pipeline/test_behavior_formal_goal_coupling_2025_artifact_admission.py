from __future__ import annotations

import unittest

from .behavior_formal_goal_coupling_2025_artifact_admission import inspect_candidate


TASKS = [f"task_{i:02d}" for i in range(50)]


def q(value: float = 0.5):
    return {"q_score": {"final": value}}


class BehaviorFormalGoalCoupling2025ArtifactAdmissionTest(unittest.TestCase):
    def test_explicit_full_task_instance_records_are_eligible(self) -> None:
        payload = {"results": []}
        for task in TASKS:
            for instance in range(10):
                payload["results"].append({"task": task, "instance": instance, **q()})
        result = inspect_candidate(payload, TASKS)
        self.assertEqual(result.status, "ELIGIBLE_FULL_STANDARD_PUBLIC")
        self.assertEqual(result.format, "FULL_TASK_INSTANCE_ROLLOUT")
        self.assertEqual(result.rollout_count, 500)

    def test_task_keyed_ten_rollouts_are_eligible(self) -> None:
        payload = {"task_results": {task: [q() for _ in range(10)] for task in TASKS}}
        result = inspect_candidate(payload, TASKS)
        self.assertEqual(result.status, "ELIGIBLE_FULL_STANDARD_PUBLIC")
        self.assertEqual(result.format, "FULL_TASK_INSTANCE_ROLLOUT")

    def test_exact_task_aggregate_requires_explicit_denominator_ten(self) -> None:
        payload = {"task_results": {task: {**q(), "num_rollouts": 10} for task in TASKS}}
        result = inspect_candidate(payload, TASKS)
        self.assertEqual(result.status, "ELIGIBLE_FULL_STANDARD_PUBLIC")
        self.assertEqual(result.format, "FULL_TASK_AGGREGATE_DENOM10")

    def test_aggregate_without_denominator_is_ineligible(self) -> None:
        payload = {"task_results": {task: q() for task in TASKS}}
        result = inspect_candidate(payload, TASKS)
        self.assertEqual(result.status, "INELIGIBLE_SCHEMA_OR_COVERAGE")

    def test_partial_submission_is_ineligible(self) -> None:
        payload = {"results": []}
        for task in TASKS[:-1]:
            for instance in range(10):
                payload["results"].append({"task_id": task, "instance_idx": instance, **q()})
        result = inspect_candidate(payload, TASKS)
        self.assertEqual(result.status, "INELIGIBLE_SCHEMA_OR_COVERAGE")
        self.assertEqual(result.task_count, 49)

    def test_duplicate_task_instance_is_ineligible(self) -> None:
        payload = {"results": []}
        for task in TASKS:
            for instance in range(10):
                payload["results"].append({"task": task, "instance": instance, **q()})
        payload["results"].append({"task": TASKS[0], "instance": 0, **q()})
        result = inspect_candidate(payload, TASKS)
        self.assertEqual(result.status, "INELIGIBLE_SCHEMA_OR_COVERAGE")

    def test_out_of_range_q_is_ineligible(self) -> None:
        payload = {"results": []}
        for task in TASKS:
            for instance in range(10):
                value = 1.2 if task == TASKS[0] and instance == 0 else 0.5
                payload["results"].append({"task": task, "instance": instance, **q(value)})
        result = inspect_candidate(payload, TASKS)
        self.assertEqual(result.status, "INELIGIBLE_SCHEMA_OR_COVERAGE")

    def test_schema_paths_redact_numeric_values(self) -> None:
        payload = {"results": [{"task": TASKS[0], "instance": 0, **q(0.913742)}]}
        result = inspect_candidate(payload, TASKS)
        joined = "\n".join(result.schema_paths)
        self.assertNotIn("0.913742", joined)
        self.assertNotIn("<0.913742>", joined)


if __name__ == "__main__":
    unittest.main()
