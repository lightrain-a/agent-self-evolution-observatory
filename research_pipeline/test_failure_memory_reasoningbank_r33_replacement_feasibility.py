from __future__ import annotations

import json
import unittest
from pathlib import Path

R33 = Path("generated/d2-failure-memory-provenance-l2b-r33-replacement-feasibility.json")


class TestR33ReplacementFeasibility(unittest.TestCase):
    def test_same_asset_capacity_is_27_and_not_authorized(self) -> None:
        d = json.loads(R33.read_text(encoding="utf-8"))
        self.assertEqual(d["status"], "R33_SAME_ASSET_FULLY_UNEXPOSED_CAPACITY_27_NEW_SUBSTRATE_PREFERRED")
        cap = d["same_asset_capacity"]
        self.assertEqual(cap["fully_unexposed_templates_remaining"], 27)
        self.assertFalse(cap["can_supply_fresh_35_task_cohort"])
        self.assertFalse(cap["can_supply_medium_variance_80pct_reference_n"])
        self.assertEqual(cap["medium_variance_80pct_reference_n"], 32)
        self.assertEqual(cap["shortfall_vs_medium_variance_80pct_reference"], 5)
        self.assertEqual(cap["shortfall_vs_35_task_target"], 8)
        self.assertFalse(cap["remaining_units_are_automatically_authorized_as_R33"])
        self.assertTrue(all(v is False for v in d["authority"].values()))

    def test_selection_is_exposure_only_and_outcome_blind(self) -> None:
        d = json.loads(R33.read_text(encoding="utf-8"))
        s = d["exposure_only_selection"]
        self.assertEqual(s["eligible_template_universe"], 36)
        self.assertEqual(len(s["all_exposed_templates_excluded"]), 9)
        self.assertTrue(s["selection_uses_only_template_identity_and_scientific_exposure"])
        self.assertFalse(s["selection_uses_terminal_scores"])
        self.assertFalse(s["selection_uses_task_deltas"])
        self.assertFalse(s["selection_uses_p_values"])
        self.assertFalse(s["selection_uses_subgroups"])

    def test_power_sensitivity_does_not_make_unconditional_80pct_claim(self) -> None:
        d = json.loads(R33.read_text(encoding="utf-8"))
        p = d["power_sensitivity_only"]
        self.assertEqual([x["approx_two_sided_power"] for x in p["scenarios"]], [0.973637, 0.738302, 0.495496])
        self.assertFalse(p["unconditional_80pct_power_claim"])
        self.assertEqual(d["recommended_replacement_direction"]["preferred"], "NEW_TASK_UNIVERSE_OR_NEW_SUBSTRATE_WITH_NATIVE_OR_AUDITABLE_PROVENANCE_SURFACE")

    def test_public_receipt_has_no_private_paths(self) -> None:
        text = R33.read_text(encoding="utf-8")
        for needle in ["/data/", "/home/", "wyt@", "192.168.", "source_message_ref", "source_message_sha256"]:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
