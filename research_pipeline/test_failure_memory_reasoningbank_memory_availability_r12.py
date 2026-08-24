import unittest
from unittest.mock import patch

from research_pipeline.failure_memory_reasoningbank_memory_availability_r12 import (
    historical_sets,
    source_ids,
)


class TestReasoningBankMemoryAvailabilityR12(unittest.TestCase):
    def test_source_ids_require_36_unique(self):
        with self.assertRaises(ValueError):
            source_ids({"cohort": [{"source_task_id": "1"}] * 36})

    def test_historical_sets_include_r6_excluded_writer_pair(self):
        r6 = {
            "source_execution": {"memories_sha256": "a2a04f2fa6569b42c515662ef899c495d87b21fc3d70f803976a752b45aa345f"},
            "information_equivalence": {"eligible_pair_ids": [str(i) for i in range(23)], "excluded_pair_id": "159"},
        }
        r4 = {
            "provenance": {"memory_generation_sha256": "02623a2fdad5c87e17ecf175afe26df1d64cb8ac06a623ed3f1da99d1da15bf3"},
            "candidate_pairs": {"outcome_blind_candidate_task_ids": ["1", "2", "3", "4", "5", "6"]},
        }
        r6_ids, r4_ids = historical_sets(r6, r4)
        self.assertIn("159", r6_ids)
        self.assertEqual(len(r6_ids), 24)
        self.assertEqual(len(r4_ids), 6)

    def test_historical_digest_drift_fails_closed(self):
        r6 = {"source_execution": {"memories_sha256": "bad"}, "information_equivalence": {}}
        r4 = {"provenance": {"memory_generation_sha256": "bad"}, "candidate_pairs": {}}
        with self.assertRaises(ValueError):
            historical_sets(r6, r4)


if __name__ == "__main__":
    unittest.main()
