from __future__ import annotations

import unittest

from .asset_first_stri_r2_manuscript_integrity_20260825 import build


class STRIR2ManuscriptIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()
        cls.manifest = cls.result["manifest"]
        cls.audit = cls.result["audit"]
        cls.receipt = cls.result["receipt"]

    def test_submission_critical_surface_passes(self) -> None:
        self.assertEqual(self.audit["status"], "PASS_POST_DRAFT_INTEGRITY")
        self.assertTrue(self.audit["pass"])
        self.assertEqual(self.audit["hard_blockers"], [])
        self.assertEqual(self.audit["editorial_blockers"], [])
        self.assertEqual(self.audit["prose_lint"]["warning_count"], 0)

    def test_inventory_and_claims_are_bound(self) -> None:
        inv = self.manifest["content_inventory"]
        self.assertEqual(inv["facts"], 6)
        self.assertEqual(inv["citations"], 8)
        self.assertEqual(inv["numbers"], 24)
        self.assertEqual(inv["tables"], 4)
        self.assertEqual(inv["claims"], 7)
        self.assertEqual(len(self.manifest["expected_claim_ids"]), 7)
        self.assertTrue(all(row["supported"] for row in self.manifest["claims"]))

    def test_receipt_has_zero_authority(self) -> None:
        self.assertEqual(len(self.receipt["receipt_sha256"]), 64)
        self.assertFalse(self.receipt["scientific_authority"])
        self.assertFalse(self.receipt["experiment_authority"])
        self.assertFalse(self.receipt["gpu_authority"])
        self.assertFalse(self.receipt["submission_authority"])


if __name__ == "__main__":
    unittest.main()
