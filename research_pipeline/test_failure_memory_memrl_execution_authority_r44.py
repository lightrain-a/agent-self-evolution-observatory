from __future__ import annotations

import unittest

from .failure_memory_memrl_execution_authority_r44 import build, validate


class MemRLExecutionAuthorityR44Test(unittest.TestCase):
    def setUp(self) -> None:
        self.d = build()

    def test_authority_is_bounded_and_non_scientific(self) -> None:
        self.assertTrue(self.d["authority"]["execution"])
        self.assertTrue(self.d["authority"]["local_gpu"])
        self.assertFalse(self.d["authority"]["external_provider_spend"])
        self.assertFalse(self.d["authority"]["scientific_belief"])
        self.assertFalse(self.d["authority"]["paper_claim_expansion"])
        self.assertFalse(self.d["authority"]["submission"])
        self.assertTrue(all(value is False for value in self.d["hard_limits"].values()))

    def test_scope_matches_frozen_transaction(self) -> None:
        scope = self.d["authorized_scope"]
        self.assertEqual(scope["source_build"]["exact_selected_source_tasks"], 128)
        self.assertEqual(scope["utilization_qualification"]["exact_clusters"], 8)
        self.assertEqual(scope["primary_confirmatory"]["exact_clusters"], 32)
        self.assertEqual(validate(self.d), [])


if __name__ == "__main__":
    unittest.main()
