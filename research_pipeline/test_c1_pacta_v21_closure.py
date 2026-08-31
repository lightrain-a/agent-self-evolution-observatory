from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper_drafts" / "c1-manuscript-strengthening-20260825"


class TestC1PactaV21Closure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.closure = json.loads((PAPER / "c1-pacta-v21-pilot-closure-20260831.json").read_text())
        cls.audit = json.loads((PAPER / "c1-pacta-v21-claim-audit-20260831.json").read_text())
        cls.asset = json.loads((ROOT / "research_pipeline" / "c1_pacta_v21_first_action_availability_failure_asset_20260831.json").read_text())["asset"]
        cls.registry = json.loads((ROOT / "research_pipeline" / "external_failure_assets.json").read_text())

    def test_qualification_and_fresh_execution(self):
        self.assertEqual(self.closure["qualification"]["status"], "PASS_MEASUREMENT_QUALIFICATION")
        self.assertEqual(self.closure["fresh_pool"]["pilot_ids"], [354, 242, 270, 438, 508, 262])
        self.assertEqual(self.closure["binder"]["completed_calls"], 12)
        self.assertEqual(self.closure["shadow"]["completed_calls"], 144)
        self.assertEqual(self.closure["gate"]["open_ids"], [242, 270])
        self.assertEqual(self.closure["gate"]["geometry_verdict"], "PASS_NON_DEGENERATE")

    def test_final_measurement_fail_closed(self):
        final = self.closure["final_policy"]
        self.assertEqual(final["complete_calls"], 49)
        self.assertEqual(final["failed_calls"], 1)
        self.assertEqual(final["unattempted_calls"], 238)
        self.assertFalse(final["action_key_present"])
        self.assertFalse(final["first_action_identifiable"])
        self.assertTrue(final["raw_response_retained"])
        self.assertEqual(final["retry_topup_imputation_replacement"], 0)

    def test_effect_and_claims_withheld(self):
        self.assertTrue(all(value is None for key, value in self.closure["effects"].items() if key != "reason"))
        authority = self.closure["claim_authority"]
        self.assertFalse(authority["preliminary_mechanism_effect_signal"])
        self.assertFalse(authority["selection_criterion_supported"])
        self.assertFalse(authority["selection_criterion_negative"])
        self.assertEqual(authority["active_manuscript"], "R9")
        self.assertEqual(self.audit["status"], "PASS_CLAIM_BOUNDARIES")

    def test_research_os_writeback(self):
        self.assertEqual(self.asset["layer"], "measurement")
        self.assertFalse(self.asset["scientific_authority"])
        entry = {
            "source_path": "research_pipeline/c1_pacta_v21_first_action_availability_failure_asset_20260831.json",
            "source_key": "asset",
        }
        self.assertEqual(self.registry["assets"].count(entry), 1)


if __name__ == "__main__":
    unittest.main()
