from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

R35 = Path("generated/d2-failure-memory-provenance-r35-fresh-confirmatory-reopen-gate.json")


class TestFreshConfirmatoryReopenGateR35(unittest.TestCase):
    def setUp(self) -> None:
        self.d = json.loads(R35.read_text(encoding="utf-8"))

    def test_r19_and_27_unit_shortcuts_are_closed(self) -> None:
        self.assertEqual(self.d["status"], "WAIT_FOR_NEW_PROVENANCE_BEARING_SUBSTRATE_NO_CONFIRMATORY_EXECUTION_AUTHORITY")
        rules = self.d["hard_non_reopen_rules"]
        self.assertTrue(all(v is False for v in rules.values()))
        same = self.d["same_asset_27_adjudication"]
        self.assertEqual(same["fully_unexposed_templates"], 27)
        self.assertEqual(same["medium_variance_two_sided_80pct_reference_n"], 32)
        self.assertFalse(same["fresh_confirmatory_eligible_under_current_gate"])
        self.assertFalse(same["such_exploratory_design_may_upgrade_B1_confirmatory_claims"])

    def test_all_six_reopen_stages_fail_closed_now(self) -> None:
        gate = self.d["fresh_substrate_reopen_gate"]
        self.assertFalse(gate["gate_pass_now"])
        self.assertIsNone(gate["qualified_substrate_now"])
        self.assertEqual([x["id"] for x in gate["ordered_stages"]], [
            "G1_RELEASE", "G2_PROVENANCE_SCHEMA", "G3_EXACT_INFORMATION",
            "G4_FRESH_CAPACITY", "G5_SUPPORT_AND_PREREGISTRATION", "G6_AUTHORITY",
        ])
        self.assertTrue(all(x["passed_now"] is False for x in gate["ordered_stages"]))
        self.assertTrue(all(v is False for v in self.d["authority"].values()))

    def test_story_is_closed_at_design_level_not_effect_level(self) -> None:
        story = self.d["paper_story"]
        self.assertEqual(story["closed_design_loop"], "phenomenon -> causal identification -> PSMG provenance-separated governance")
        self.assertTrue(story["PSMG_design_frozen"])
        self.assertFalse(story["PSMG_effect_validated"])
        self.assertTrue(story["experiment_volume_is_not_a_gate_relaxation_reason"])

    def test_parent_receipts_are_content_addressed(self) -> None:
        for bind in self.d["parent_bindings"].values():
            p = Path(bind["path"])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), bind["sha256"])

    def test_public_receipt_has_no_private_paths(self) -> None:
        text = R35.read_text(encoding="utf-8")
        for needle in ["/data/", "/home/", "wyt@", "192.168.", "source_message_ref", "source_message_sha256"]:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
