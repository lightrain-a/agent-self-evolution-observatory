from __future__ import annotations

import copy
import json
import unittest

from .asset_first_stri_paper_revision import (
    OUTPUT_REL,
    build_asset_first_stri_paper_revision,
    validate_asset_first_stri_paper_revision,
)
from .config import PROJECT_ROOT


class AssetFirstSTRIPaperRevisionTest(unittest.TestCase):
    def current_receipt(self) -> dict:
        return json.loads((PROJECT_ROOT / OUTPUT_REL).read_text(encoding="utf-8"))

    def test_current_receipt_is_content_addressed_and_claim_preserving(self) -> None:
        state = self.current_receipt()
        self.assertEqual(state["status"], "READY_PAPER_REVISION")
        self.assertEqual(state["parent"]["inherited_claims"], {"N1": "SUPPORTED", "N2": "SUPPORTED", "N3": "SUPPORTED"})
        self.assertTrue(state["scope"]["paper_architecture_only"])
        self.assertFalse(state["scope"]["scientific_execution"])
        self.assertFalse(state["scope"]["new_evidence"])
        self.assertFalse(state["scope"]["claim_expansion"])
        self.assertTrue(state["scope"]["claims_unchanged"])
        self.assertEqual(state["qa"]["scientific_paper"]["status"], "PASS")
        self.assertEqual(state["qa"]["iclr2027"]["status"], "PASS")
        self.assertEqual((state["qa"]["iclr2027"]["main_text_pages"], state["qa"]["iclr2027"]["main_text_page_limit"]), (9, 9))
        self.assertEqual(state["qa"]["independent_source_compile"]["status"], "PASS")
        self.assertTrue(state["qa"]["source_compile_matches_active_pdf_text_and_pages"])
        self.assertTrue(all(state["qa"]["source_zip_source_bindings"].values()))
        self.assertEqual(validate_asset_first_stri_paper_revision(state, require_visual_pass=False), [])

    def test_visual_review_is_required_for_public_delivery_authority(self) -> None:
        state = self.current_receipt()
        state["qa"]["visual_inspection"] = {"status": "PENDING_MANUAL_VISUAL_REVIEW", "pages": [], "scope": "layout"}
        errors = validate_asset_first_stri_paper_revision(state, require_visual_pass=True)
        self.assertTrue(any("visual inspection" in error for error in errors))

    def test_claim_expansion_or_execution_authority_invalidates_revision(self) -> None:
        state = self.current_receipt()
        drift = copy.deepcopy(state)
        drift["scope"]["claim_expansion"] = True
        drift["authority"]["experiment"] = True
        errors = validate_asset_first_stri_paper_revision(drift, require_visual_pass=False)
        self.assertTrue(any("scope mismatch:claim_expansion" in error for error in errors))
        self.assertTrue(any("authority mismatch:experiment" in error for error in errors))

    def test_delivery_digest_drift_invalidates_revision(self) -> None:
        state = self.current_receipt()
        drift = copy.deepcopy(state)
        drift["delivery"]["pdf"]["sha256"] = "0" * 64
        errors = validate_asset_first_stri_paper_revision(drift, require_visual_pass=False)
        self.assertTrue(any("delivery digest drift:pdf" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
