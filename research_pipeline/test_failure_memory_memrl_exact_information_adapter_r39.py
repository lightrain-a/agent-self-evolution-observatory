from __future__ import annotations

import copy
import unittest

from research_pipeline.failure_memory_memrl_exact_information_adapter_r39 import (
    MemRLExactInformationError,
    TREATMENT_FIELD,
    build_memrl_exact_information_pair,
)


class DummyMeta:
    def __init__(self, success: bool) -> None:
        self.model_extra = {"success": success, "full_content": "not executor metadata"}

    def model_dump(self):
        return {"type": "procedure"}


class TestFailureMemoryMemRLExactInformationAdapterR39(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            {
                "memory_id": "mem-success",
                "content": "Task: alpha\n\nUse the verified sequence.",
                "metadata": {"success": True, "q_value": 1.0, "memory_role": "source"},
                "similarity": 0.81,
                "q_estimate": 0.75,
                "score": 1.2,
                "task_id": "17",
            },
            {
                "memory_id": "mem-failure",
                "content": "Task: beta\n\nAvoid the stale branch.",
                "metadata": DummyMeta(False),
                "similarity": 0.77,
                "q_estimate": -0.25,
                "score": 0.4,
                "task_id": "23",
            },
        ]

    def test_only_raw_source_outcome_differs_between_executor_views(self) -> None:
        pair = build_memrl_exact_information_pair(self.rows)
        hidden = pair["content_only_provenance_hidden"]
        raw = pair["raw_provenance_exact_information"]
        self.assertEqual(len(hidden), 2)
        self.assertEqual(len(raw), 2)
        for left, right in zip(hidden, raw):
            self.assertEqual(left["position"], right["position"])
            self.assertEqual(left["content"], right["content"])
            self.assertEqual(set(right) - set(left), {TREATMENT_FIELD})
        self.assertEqual([x[TREATMENT_FIELD] for x in raw], [True, False])

    def test_retrieval_and_nonprovenance_signals_are_not_executor_visible(self) -> None:
        pair = build_memrl_exact_information_pair(self.rows)
        forbidden = {"memory_id", "metadata", "similarity", "q_estimate", "score", "task_id", "q_value", "memory_role"}
        for arm in [pair["content_only_provenance_hidden"], pair["raw_provenance_exact_information"]]:
            for row in arm:
                self.assertFalse(forbidden & set(row))
        audit = pair["audit"]
        self.assertTrue(audit["post_retrieval_only"])
        self.assertTrue(audit["retrieval_membership_preserved"])
        self.assertTrue(audit["retrieval_order_preserved"])
        self.assertTrue(audit["actionable_content_identical"])
        self.assertTrue(audit["similarity_q_score_role_and_ids_hidden_from_executor"])
        self.assertEqual(len(audit["frozen_selected_sha256"]), 64)

    def test_input_selected_payload_is_not_mutated(self) -> None:
        before = copy.deepcopy(self.rows)
        build_memrl_exact_information_pair(self.rows)
        self.assertEqual(self.rows[0], before[0])
        self.assertEqual(self.rows[1]["memory_id"], before[1]["memory_id"])
        self.assertEqual(self.rows[1]["content"], before[1]["content"])

    def test_missing_or_coerced_provenance_fails_closed(self) -> None:
        bad = copy.deepcopy(self.rows)
        bad[0]["metadata"].pop("success")
        with self.assertRaises(MemRLExactInformationError):
            build_memrl_exact_information_pair(bad)
        bad = copy.deepcopy(self.rows)
        bad[0]["metadata"]["success"] = 1
        with self.assertRaises(MemRLExactInformationError):
            build_memrl_exact_information_pair(bad)

    def test_missing_content_or_id_fails_closed(self) -> None:
        bad = copy.deepcopy(self.rows)
        bad[0]["content"] = ""
        with self.assertRaises(MemRLExactInformationError):
            build_memrl_exact_information_pair(bad)
        bad = copy.deepcopy(self.rows)
        bad[0]["memory_id"] = None
        with self.assertRaises(MemRLExactInformationError):
            build_memrl_exact_information_pair(bad)


if __name__ == "__main__":
    unittest.main()
