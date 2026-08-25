from __future__ import annotations

import unittest

from .asset_first_stri_r2_manuscript_gate_20260825 import build


class STRIR2ManuscriptGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build()

    def test_mechanism_closure_is_complete(self) -> None:
        self.assertTrue(self.state["pass"])
        self.assertEqual(self.state["decision"], "PASS_R2_MECHANISM_SPINE_DRAFT_KEEP_R19_CANONICAL")
        self.assertTrue(all(self.state["closure_gate"].values()))
        self.assertTrue(all(self.state["evidence_binding"].values()))

    def test_draft_is_scoped_and_within_page_budget(self) -> None:
        m = self.state["manuscript"]
        self.assertLessEqual(m["main_pages"], 9)
        self.assertTrue(m["all_citations_in_bib"])
        self.assertEqual(m["forbidden_claim_hits"], [])
        self.assertFalse(m["r19_canonical_overwritten"])
        self.assertEqual(self.state["promotion_status"], "DRAFT_ONLY_DO_NOT_REPLACE_R19")

    def test_no_authority_escalation(self) -> None:
        self.assertFalse(self.state["claim_expansion"])
        self.assertFalse(self.state["scientific_authority"])
        self.assertFalse(self.state["experiment_authority"])
        self.assertFalse(self.state["gpu_authority"])
        self.assertFalse(self.state["submission_authority"])


if __name__ == "__main__":
    unittest.main()
