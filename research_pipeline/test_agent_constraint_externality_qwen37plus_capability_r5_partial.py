from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_qwen37plus_capability_r5_partial import (
    ALLOWED_ALIAS,
    R5_CONTRACT,
    TNF_FAMILIES,
    TOOL_CAP,
    units,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_value


class Qwen37PlusCapabilityR5PartialTest(unittest.TestCase):
    def test_scope_is_only_four_correction_affected_tnf_units(self) -> None:
        rows = units()
        self.assertEqual(len(rows), 4)
        self.assertEqual({row.family_id for row in rows}, set(TNF_FAMILIES))
        self.assertTrue(all(row.stage == "CAPABILITY_CALIBRATION_R5_PARTIAL_TNF" for row in rows))
        self.assertTrue(all("ACE-FG" not in row.unit_id for row in rows))
        self.assertTrue(all(ALLOWED_ALIAS in row.unit_id for row in rows))

    def test_contract_preserves_fg_and_changes_only_qualified_tool_budget(self) -> None:
        payload = json.loads(Path(R5_CONTRACT).read_text(encoding="utf-8"))
        claimed = payload["content_sha256"]
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        self.assertEqual(payload["status"], "QWEN37PLUS_CAPABILITY_R5_PARTIAL_TNF_ONLY_AUTHORIZED")
        self.assertEqual(payload["preserve_fg_measurements"], 4)
        self.assertEqual(payload["rerun_tnf_measurements"], 4)
        self.assertEqual(payload["tool_call_cap"], TOOL_CAP)
        self.assertEqual(TOOL_CAP, 16)
        self.assertFalse(payload["model_switch"])
        self.assertFalse(payload["replacement"])
        self.assertFalse(payload["application_retry"])
        self.assertEqual(payload["provider_max_retries"], 0)
        self.assertFalse(payload["threshold_change"])


if __name__ == "__main__":
    unittest.main()
