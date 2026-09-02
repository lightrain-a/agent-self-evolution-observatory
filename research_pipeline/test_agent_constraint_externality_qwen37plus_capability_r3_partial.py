from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_qwen37plus_capability_r3_partial import (
    ALLOWED_ALIAS,
    FG_REVALIDATION,
    PARTIAL_CONTRACT,
    build_fg_revalidation,
    build_partial_contract,
    tnf_units,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_value


class Qwen37PlusCapabilityR3PartialTests(unittest.TestCase):
    def test_only_four_tnf_units_are_rerun(self) -> None:
        units = tnf_units()
        self.assertEqual(len(units), 4)
        self.assertEqual(len({u.unit_id for u in units}), 4)
        self.assertTrue(all("ACE-TNF-" in u.unit_id for u in units))
        self.assertTrue(all(u.stage == "CAPABILITY_CALIBRATION_R3_PARTIAL_TNF" for u in units))

    def test_four_fg_units_revalidate_under_v2_without_provider_calls(self) -> None:
        payload = build_fg_revalidation()
        self.assertEqual(payload["status"], "R2_FG_V2_MEASUREMENT_REVALIDATION_PASS")
        self.assertEqual(payload["preserved_unit_count"], 4)
        self.assertEqual(payload["provider_requests_added"], 0)
        self.assertEqual(len(payload["rows"]), 4)
        for row in payload["rows"]:
            self.assertIn("ACE-FG-", row["unit_id"])
            self.assertTrue(row["v2_measurement_only_revalidation"])
            self.assertFalse(row["provider_reexecution"])
            self.assertTrue(row["tool_loop_completed"])
            self.assertTrue(row["target_success"])
            self.assertEqual(row["non_target_preservation"], 1.0)

    def test_partial_contract_preserves_fg_and_reruns_only_tnf(self) -> None:
        revalidation = build_fg_revalidation()
        # build_partial_contract expects the persisted revalidation file for its file hash.
        FG_REVALIDATION.write_text(json.dumps(revalidation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        contract = build_partial_contract(revalidation)
        self.assertEqual(contract["status"], "QWEN37PLUS_CAPABILITY_R3_PARTIAL_AUTHORIZED")
        self.assertEqual(contract["preserved_unit_count"], 4)
        self.assertEqual(contract["rerun_unit_count"], 4)
        self.assertEqual(contract["final_gate_measurement_count"], 8)
        self.assertTrue(all("ACE-FG-" in unit for unit in contract["preserved_units"]))
        self.assertTrue(all("ACE-TNF-" in unit for unit in contract["rerun_units"]))
        self.assertFalse(contract["model_switch"])
        self.assertFalse(contract["threshold_change"])
        self.assertFalse(contract["replacement"])
        self.assertFalse(contract["f0_authorized"])
        claimed = contract["content_sha256"]
        unsigned = dict(contract); unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))


if __name__ == "__main__":
    unittest.main()
