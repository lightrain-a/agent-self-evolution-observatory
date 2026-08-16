from __future__ import annotations

import copy
import unittest

from .asset_first_stri_public_status import (
    build_asset_first_stri_public_status,
    validate_asset_first_stri_public_status,
)


class AssetFirstSTRIPublicStatusTest(unittest.TestCase):
    def test_current_artifacts_compile_to_ready_narrow_iclr(self) -> None:
        state = build_asset_first_stri_public_status()
        self.assertEqual(state["status"], "READY_NARROW_ICLR")
        self.assertEqual(state["paper_id"], "STRI")
        self.assertEqual(state["summary"]["paper_ready"], 1)
        self.assertEqual(state["summary"]["claims_supported"], 3)
        self.assertEqual(state["summary"]["claims_total"], 3)
        self.assertEqual(state["summary"]["qa_checks_passed"], state["summary"]["qa_checks_total"])
        self.assertFalse(state["scientific_authority"])
        self.assertFalse(any(state["authority"].values()))
        self.assertEqual(validate_asset_first_stri_public_status(state), [])

    def test_ready_projection_cannot_leak_canonical_problem_gate_authority(self) -> None:
        state = build_asset_first_stri_public_status()
        drift = copy.deepcopy(state)
        drift["summary"]["canonical_problem_gate_pass_added"] = 1
        drift["authority"]["canonical_problem_gate"] = True
        errors = validate_asset_first_stri_public_status(drift)
        self.assertTrue(any("authority" in error for error in errors))

    def test_missing_ready_gate_cannot_keep_ready_status(self) -> None:
        state = build_asset_first_stri_public_status()
        drift = copy.deepcopy(state)
        drift["gates"]["current_source"] = False
        errors = validate_asset_first_stri_public_status(drift)
        self.assertTrue(any("every cross-validated" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
