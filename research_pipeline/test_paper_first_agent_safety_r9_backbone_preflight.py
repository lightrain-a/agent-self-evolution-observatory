from __future__ import annotations

import copy
import json
import unittest

from .paper_first_agent_safety_r9_backbone_preflight import (
    BACKBONE_MODEL_ID,
    BACKBONE_MODEL_REVISION,
    DEFAULT_JSON,
    EXPECTED_DEVELOPMENT_IDS,
    EXPECTED_QUALIFICATION_IDS,
    validate_preregistration,
)


class BackbonePreflightPreregistrationTest(unittest.TestCase):
    def state(self) -> dict:
        return json.loads(DEFAULT_JSON.read_text(encoding="utf-8"))

    def test_generated_preregistration_is_valid(self) -> None:
        state = self.state()
        self.assertEqual(validate_preregistration(state), [])
        self.assertEqual(state["candidate_selection"]["model_id"], BACKBONE_MODEL_ID)
        self.assertEqual(state["candidate_selection"]["exact_revision"], BACKBONE_MODEL_REVISION)
        self.assertEqual(state["probe_selection"]["development_safety_ids"], list(EXPECTED_DEVELOPMENT_IDS))
        self.assertEqual(state["probe_selection"]["fresh_qualification_ids"], list(EXPECTED_QUALIFICATION_IDS))
        self.assertFalse(state["asset_gate"]["weight_download_authorized"])
        self.assertFalse(state["asset_gate"]["model_inference_authorized"])

    def test_contract_identity_ignores_receipt_timestamp(self) -> None:
        state = self.state()
        state["generated_at"] = "2099-01-01T00:00:00+00:00"
        self.assertEqual(validate_preregistration(state), [])

    def test_rejects_backbone_fallback_shopping(self) -> None:
        state = self.state()
        state["candidate_selection"]["fallback_forbidden"] = False
        self.assertTrue(any("fallback" in e for e in validate_preregistration(state)))

    def test_rejects_execution_authority_before_asset_gate(self) -> None:
        state = self.state()
        state["authority"]["model_loading"] = True
        self.assertTrue(any("over-authorizes" in e for e in validate_preregistration(state)))

    def test_rejects_guard_axis_change(self) -> None:
        state = self.state()
        state["frozen_axes"]["safety_substrate"]["guard_retuning_forbidden"] = False
        self.assertTrue(any("guard axis" in e for e in validate_preregistration(state)))

    def test_rejects_probe_replacement(self) -> None:
        state = self.state()
        state["probe_selection"]["development_safety_ids"] = [37, 12, 5]
        self.assertTrue(any("panel drift" in e for e in validate_preregistration(state)))

    def test_rejects_asset_download_authority(self) -> None:
        state = self.state()
        state["asset_gate"]["weight_download_authorized"] = True
        self.assertTrue(any("asset gate" in e for e in validate_preregistration(state)))


if __name__ == "__main__":
    unittest.main()
