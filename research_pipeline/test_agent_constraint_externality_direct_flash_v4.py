from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_direct_flash_v4 import (
    AUTH_OUTPUT,
    CATALOG_OUTPUT,
    CONTRACT_OUTPUT,
    MODEL_ID,
    TOOL_CALL_CAP,
    units,
    verified,
)


class DirectFlashV4RequalificationTest(unittest.TestCase):
    def test_catalog_and_contract_are_content_addressed(self) -> None:
        catalog = verified(CATALOG_OUTPUT, "DIRECT_QWEN37FLASH_CATALOG_V4_R1_PASS")
        contract = verified(CONTRACT_OUTPUT, "DIRECT_QWEN37FLASH_CAPABILITY_V4_R1_AUTHORIZED")
        self.assertEqual(catalog["model_id"], MODEL_ID)
        self.assertTrue(catalog["model_available"])
        self.assertEqual(contract["execution"]["tool_call_cap"], TOOL_CALL_CAP)
        self.assertEqual(TOOL_CALL_CAP, 16)
        self.assertEqual(contract["harness"], "APPWORLD_DIRECT_FUNCTION_CALLING_V4")

    def test_user_continue_authorizes_only_capability_requalification(self) -> None:
        auth = verified(AUTH_OUTPUT, "USER_CONTINUE_AUTHORIZED_DIRECT_QWEN37FLASH_V4_REQUALIFICATION")
        self.assertTrue(auth["authority"]["direct_flash_capability_v4_r1"])
        self.assertFalse(auth["authority"]["new_source_failure_qualification"])
        self.assertFalse(auth["authority"]["f0_r1"])
        self.assertFalse(auth["authority"]["p1"])

    def test_exact_eight_units_and_no_historical_measurement_reuse(self) -> None:
        rows = units()
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row.unit_id for row in rows}), 8)
        contract = json.loads(CONTRACT_OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(contract["panel"]["episode_count"], 8)
        self.assertFalse(contract["panel"]["historical_invalid_flash_measurements_reused"])
        self.assertEqual(contract["model_id"], MODEL_ID)
        self.assertFalse(contract["authority"]["source_failure_qualification"])
        self.assertFalse(contract["authority"]["f0_r1"])


if __name__ == "__main__":
    unittest.main()
