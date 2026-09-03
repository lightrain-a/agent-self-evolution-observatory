from __future__ import annotations

import copy
import unittest

from research_pipeline.failure_memory_romerl_exact_information_adapter_r38 import (
    ExactInformationError,
    TREATMENT_FIELD,
    build_exact_information_pair,
)


class TestFailureMemoryRoMeRLExactInformationAdapterR38(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            {
                "memory_id": "m-success",
                "query": "task alpha",
                "content": "Use the verified command sequence.",
                "metadata": {"success": True, "memory_role": "best_success", "q_value": 0.91},
                "similarity": 0.84,
                "q_estimate": 0.91,
            },
            {
                "memory_id": "m-failure",
                "query": "task beta",
                "content": "Avoid the stale-file branch.",
                "metadata": {"success": False, "memory_role": "best_failure", "q_value": 0.72},
                "similarity": 0.79,
                "q_estimate": 0.72,
            },
        ]

    def test_only_executor_visible_difference_is_raw_provenance(self) -> None:
        pair = build_exact_information_pair(self.rows)
        hidden = pair["content_only_provenance_hidden"]
        raw = pair["raw_provenance_exact_information"]
        self.assertEqual(len(hidden), len(raw))
        for left, right in zip(hidden, raw):
            self.assertEqual(left["position"], right["position"])
            self.assertEqual(left["content"], right["content"])
            self.assertNotIn(TREATMENT_FIELD, left)
            self.assertIn(TREATMENT_FIELD, right)
            self.assertEqual(set(right) - set(left), {TREATMENT_FIELD})

    def test_retrieval_order_and_cardinality_are_not_changed(self) -> None:
        pair = build_exact_information_pair(self.rows)
        audit = pair["audit"]
        self.assertTrue(audit["post_retrieval_only"])
        self.assertTrue(audit["retrieval_cardinality_preserved"])
        self.assertTrue(audit["retrieval_order_preserved"])
        self.assertTrue(audit["actionable_content_identical"])
        self.assertEqual(audit["input_row_count"], 2)
        self.assertEqual(audit["output_row_count_per_arm"], 2)

    def test_q_role_similarity_and_memory_id_are_not_treatment_information(self) -> None:
        pair = build_exact_information_pair(self.rows)
        for arm in [pair["content_only_provenance_hidden"], pair["raw_provenance_exact_information"]]:
            for row in arm:
                for forbidden in ["memory_id", "query", "similarity", "q_estimate", "metadata", "memory_role", "q_value"]:
                    self.assertNotIn(forbidden, row)
        self.assertFalse(pair["audit"]["q_or_role_exposed_to_executor"])

    def test_raw_provenance_is_truthful_boolean_from_metadata_success(self) -> None:
        pair = build_exact_information_pair(self.rows)
        observed = [x[TREATMENT_FIELD] for x in pair["raw_provenance_exact_information"]]
        self.assertEqual(observed, [True, False])

    def test_input_rows_are_not_mutated(self) -> None:
        before = copy.deepcopy(self.rows)
        build_exact_information_pair(self.rows)
        self.assertEqual(self.rows, before)

    def test_missing_or_non_boolean_provenance_fails_closed(self) -> None:
        bad_rows = copy.deepcopy(self.rows)
        del bad_rows[0]["metadata"]["success"]
        with self.assertRaises(ExactInformationError):
            build_exact_information_pair(bad_rows)
        bad_rows = copy.deepcopy(self.rows)
        bad_rows[0]["metadata"]["success"] = 1
        with self.assertRaises(ExactInformationError):
            build_exact_information_pair(bad_rows)


if __name__ == "__main__":
    unittest.main()
