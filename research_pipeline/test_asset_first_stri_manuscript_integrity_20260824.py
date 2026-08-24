from __future__ import annotations

import unittest

from .asset_first_stri_manuscript_integrity_20260824 import build


class STRIR19ManuscriptIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()

    def test_submission_critical_surface_passes(self) -> None:
        audit = self.result["audit"]
        self.assertEqual(audit["status"], "PASS_POST_DRAFT_INTEGRITY")
        self.assertTrue(audit["pass"])
        self.assertEqual(audit["hard_blockers"], [])
        self.assertEqual(audit["editorial_blockers"], [])

    def test_inventory_and_claim_scope_are_explicit(self) -> None:
        manifest = self.result["manifest"]
        inventory = manifest["content_inventory"]
        self.assertTrue(inventory["scope_is_submission_critical_not_full_token_inventory"])
        self.assertEqual((inventory["facts"], inventory["citations"], inventory["numbers"], inventory["tables"], inventory["claims"]), (4, 7, 18, 2, 4))
        self.assertEqual(manifest["expected_claim_ids"], ["N1", "N2", "N3", "R19-BOUNDARY"])
        self.assertIn("does not claim token-level enumeration", manifest["audit_scope"])

    def test_receipt_has_zero_authority(self) -> None:
        receipt = self.result["receipt"]
        self.assertEqual(len(receipt["receipt_sha256"]), 64)
        self.assertFalse(receipt["scientific_authority"])
        self.assertFalse(receipt["experiment_authority"])
        self.assertFalse(receipt["gpu_authority"])
        self.assertFalse(receipt["submission_authority"])


if __name__ == "__main__":
    unittest.main()
