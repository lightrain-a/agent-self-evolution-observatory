from __future__ import annotations

import unittest

import scripts.run_e2_r17_v3_1_review as review_harness


class ReviewHarnessAcknowledgementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_schema = review_harness.schema

    def tearDown(self) -> None:
        review_harness.schema = self.original_schema

    def test_historical_repair_ack_field_still_passes(self) -> None:
        expected = "a" * 64
        review_harness.schema = lambda: {
            "repair_sha256_acknowledged": "",
            "paper_claim_authority": False,
        }
        missing = review_harness.validate_review_schema(
            {"repair_sha256_acknowledged": expected, "paper_claim_authority": False},
            expected,
        )
        self.assertEqual(missing, [])

    def test_draft_contract_ack_field_passes_without_legacy_field(self) -> None:
        expected = "b" * 64
        review_harness.schema = lambda: {
            "draft_contract_sha256_acknowledged": "",
            "paper_claim_authority": False,
        }
        missing = review_harness.validate_review_schema(
            {"draft_contract_sha256_acknowledged": expected, "paper_claim_authority": False},
            expected,
        )
        self.assertEqual(missing, [])

    def test_wrong_ack_is_fail_closed(self) -> None:
        expected = "c" * 64
        review_harness.schema = lambda: {
            "draft_contract_sha256_acknowledged": "",
            "paper_claim_authority": False,
        }
        missing = review_harness.validate_review_schema(
            {"draft_contract_sha256_acknowledged": "d" * 64, "paper_claim_authority": False},
            expected,
        )
        self.assertIn("draft_contract_sha256_acknowledged_exact", missing)

    def test_schema_without_ack_field_is_rejected(self) -> None:
        expected = "e" * 64
        review_harness.schema = lambda: {"paper_claim_authority": False}
        missing = review_harness.validate_review_schema(
            {"paper_claim_authority": False},
            expected,
        )
        self.assertIn("sha256_acknowledgement_field_missing_from_schema", missing)


if __name__ == "__main__":
    unittest.main()
