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
        self.assertEqual(state["summary"]["paper_quality_content_addressed_completion"], 1)
        self.assertEqual(state["summary"]["paper_quality_content_addressed_files"], 14)
        self.assertTrue(state["gates"]["paper_quality_content_addressed_completion"])
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
        self.assertEqual(state["summary"]["skillrl_p0e_experimental_stop_valid"], 1)
        self.assertEqual(state["summary"]["skillrl_p0e_principle_dead_end"], 0)
        self.assertEqual(state["summary"]["skillrl_p0e_stage2_locked"], 1)
        self.assertEqual(state["summary"]["skillrl_p0e_new_gpu_authorized"], 0)
        self.assertEqual(state["summary"]["skillrl_p0e_calibration_success"], 18)
        self.assertEqual(state["summary"]["skillrl_p0e_paired_units"], 24)
        p0e = state["claim_boundary"]["skillrl_p0e"]
        self.assertEqual(p0e["experimental_realization"], "STOP_FIXED_POLICY_DYNAMIC_BRIDGE")
        self.assertEqual(p0e["principle_disposition"], "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED")
        self.assertFalse(p0e["persistent_principle_dead_end_certified"])
        self.assertTrue(p0e["stage2_locked"])
        self.assertFalse(p0e["new_gpu_authorized"])
        self.assertTrue(p0e["broader_n1_n2_n3_unchanged"])
        self.assertTrue(state["gates"]["public_download_assets"])
        handoff = state["submission_handoff"]
        self.assertEqual(handoff["recorded_author_guide_abstract_deadline_aoe"], "2026-09-18")
        self.assertEqual(handoff["recorded_author_guide_full_paper_deadline_aoe"], "2026-09-25")
        self.assertTrue(handoff["official_source_conflict"])
        self.assertEqual(handoff["official_source_conflict_status"], "HUMAN_VERIFICATION_REQUIRED")
        self.assertEqual(handoff["conflicting_official_dates"]["dates_cfp_conference_pages"], {"abstract": "2026-09-11", "full_paper": "2026-09-16"})
        self.assertEqual(handoff["operational_safe_abstract_deadline_aoe"], "2026-09-11")
        self.assertEqual(handoff["operational_safe_full_paper_deadline_aoe"], "2026-09-16")
        self.assertTrue(handoff["author_membership_freezes_at_abstract_deadline"])
        self.assertTrue(handoff["title_freezes_at_full_paper_deadline"])
        self.assertEqual(
            handoff["downloads"],
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

    def test_official_deadline_conflict_and_fail_safe_rules_are_fail_closed(self) -> None:
        state = self.forced_ready_projection()
        drift = copy.deepcopy(state)
        drift["submission_handoff"]["official_source_conflict"] = False
        drift["submission_handoff"]["operational_safe_abstract_deadline_aoe"] = "2026-09-18"
        errors = validate_asset_first_stri_public_status(drift)
        self.assertTrue(any("deadline conflict/fail-safe policy drift" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
