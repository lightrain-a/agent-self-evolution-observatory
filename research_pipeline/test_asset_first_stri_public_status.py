from __future__ import annotations

import copy
import unittest

from .asset_first_stri_public_status import (
    build_asset_first_stri_public_status,
    validate_asset_first_stri_public_status,
)


class AssetFirstSTRIPublicStatusTest(unittest.TestCase):
    def forced_ready_projection(self) -> dict:
        state = build_asset_first_stri_public_status()
        state["status"] = "READY_NARROW_ICLR"
        state["submission_status"] = "READY_TO_SUBMIT_PENDING_HUMAN_AUTHOR_SIGNOFF_AND_OPENREVIEW"
        state["track"] = "ASSET_FIRST_PAPER_READY"
        state["summary"]["paper_ready"] = 1
        for key in state["gates"]:
            state["gates"][key] = True
        return state

    def test_current_artifacts_are_ready_only_after_paper_quality_v2_closes(self) -> None:
        state = build_asset_first_stri_public_status()
        self.assertEqual(state["status"], "READY_NARROW_ICLR")
        self.assertEqual(state["submission_status"], "READY_TO_SUBMIT_PENDING_HUMAN_AUTHOR_SIGNOFF_AND_OPENREVIEW")
        self.assertEqual(state["paper_id"], "STRI")
        self.assertEqual(state["summary"]["paper_ready"], 1)
        self.assertEqual(state["summary"]["paper_quality_v2_passed"], 1)
        self.assertEqual(state["summary"]["paper_quality_source_binding"], 1)
        self.assertTrue(state["gates"]["paper_quality_source_binding"])
        self.assertEqual(state["summary"]["paper_quality_evidence_debt"], 0)
        self.assertEqual(state["summary"]["paper_quality_main_visualizations"], 4)
        self.assertIn("failure", state["summary"]["paper_quality_main_visual_roles"])
        self.assertEqual(state["summary"]["paper_quality_missing_ids"], [])
        self.assertEqual(state["summary"]["claims_supported"], 3)
        self.assertEqual(state["summary"]["claims_total"], 3)
        self.assertEqual(state["summary"]["qa_checks_passed"], state["summary"]["qa_checks_total"])
        self.assertEqual(state["summary"]["official_qa_checks_passed"], state["summary"]["official_qa_checks_total"])
        self.assertEqual((state["summary"]["main_text_pages"], state["summary"]["main_text_page_limit"]), (9, 9))
        self.assertEqual(state["summary"]["supplement_ready"], 1)
        self.assertEqual(state["summary"]["supplement_unit_tests"], "13/13 PASS")
        self.assertEqual(state["summary"]["human_signoff_pending"], 1)
        self.assertEqual(state["summary"]["new_gpu_evidence_required"], 0)
        self.assertTrue(state["gates"]["public_download_assets"])
        self.assertEqual(
            state["submission_handoff"]["downloads"],
            {
                "tex": "downloads/STRI-ICLR2027.tex",
                "pdf": "downloads/STRI-ICLR2027.pdf",
                "source_zip": "downloads/STRI-ICLR2027-source.zip",
            },
        )
        self.assertTrue(all(len(value) == 64 for value in state["submission_handoff"]["download_sha256"].values()))
        self.assertFalse(state["scientific_authority"])
        self.assertFalse(any(state["authority"].values()))
        self.assertEqual(validate_asset_first_stri_public_status(state), [])

    def test_ready_projection_cannot_leak_canonical_problem_gate_authority(self) -> None:
        state = self.forced_ready_projection()
        drift = copy.deepcopy(state)
        drift["summary"]["canonical_problem_gate_pass_added"] = 1
        drift["authority"]["canonical_problem_gate"] = True
        errors = validate_asset_first_stri_public_status(drift)
        self.assertTrue(any("authority" in error for error in errors))

    def test_missing_ready_gate_cannot_keep_ready_status(self) -> None:
        state = self.forced_ready_projection()
        drift = copy.deepcopy(state)
        drift["gates"]["current_source"] = False
        errors = validate_asset_first_stri_public_status(drift)
        self.assertTrue(any("every cross-validated" in error for error in errors))

    def test_missing_official_supplement_gate_cannot_keep_ready_status(self) -> None:
        state = self.forced_ready_projection()
        drift = copy.deepcopy(state)
        drift["gates"]["anonymous_supplement"] = False
        drift["summary"]["supplement_ready"] = 0
        errors = validate_asset_first_stri_public_status(drift)
        self.assertTrue(any("paper-ready/submission gate" in error or "supplement" in error for error in errors))

    def test_public_download_urls_are_fail_closed(self) -> None:
        state = self.forced_ready_projection()
        drift = copy.deepcopy(state)
        drift["submission_handoff"]["downloads"]["pdf"] = "private/internal.pdf"
        errors = validate_asset_first_stri_public_status(drift)
        self.assertTrue(any("download URLs" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
