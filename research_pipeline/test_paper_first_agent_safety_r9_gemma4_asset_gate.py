from __future__ import annotations

import json
import unittest

from .paper_first_agent_safety_r9_gemma4_asset_gate import DEFAULT_OUTPUT, validate_download_authorization


class Gemma4AssetGateTest(unittest.TestCase):
    def state(self) -> dict:
        return json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))

    def test_generated_download_authorization_is_valid(self) -> None:
        state = self.state()
        self.assertEqual(validate_download_authorization(state), [])
        self.assertTrue(state["authority"]["model_weight_download"])
        self.assertFalse(state["authority"]["model_loading"])
        self.assertFalse(state["authority"]["model_inference"])
        self.assertTrue(state["transport_policy"]["mirror_may_transport_bytes_but_never_establish_provenance"])

    def test_receipt_timestamp_does_not_change_authorization_identity(self) -> None:
        state = self.state(); state["generated_at"] = "2099-01-01T00:00:00+00:00"
        self.assertEqual(validate_download_authorization(state), [])

    def test_rejects_model_loading_authority(self) -> None:
        state = self.state(); state["authority"]["model_loading"] = True
        self.assertTrue(any("over-authorizes" in e for e in validate_download_authorization(state)))

    def test_rejects_mirror_as_provenance(self) -> None:
        state = self.state(); state["transport_policy"]["mirror_may_transport_bytes_but_never_establish_provenance"] = False
        self.assertTrue(any("transport provenance" in e for e in validate_download_authorization(state)))

    def test_rejects_partial_manifest_verification(self) -> None:
        state = self.state(); state["verification_contract"]["verify_every_manifest_file"] = False
        self.assertTrue(any("verification contract" in e for e in validate_download_authorization(state)))


if __name__ == "__main__":
    unittest.main()
