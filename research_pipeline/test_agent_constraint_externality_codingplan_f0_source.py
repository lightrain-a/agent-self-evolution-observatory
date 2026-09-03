from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_codingplan_f0_source import (
    ADDENDUM,
    AUTH,
    CONTRACT,
    MODEL_ID,
    MODEL_PROFILE,
    PROVIDER,
    Q1,
    SELECTION,
)
from research_pipeline.agent_constraint_externality_f0_execute import enumerate_source_units
from research_pipeline.agent_constraint_externality_runner_core import sha256_value


class CodingPlanMiMo25ProF0SourceTest(unittest.TestCase):
    def _verified(self, path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        claimed = payload["content_sha256"]
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        return payload

    def test_user_authorization_is_f0_only(self):
        payload = self._verified(AUTH)
        self.assertEqual(payload["status"], "USER_AUTHORIZED_F0_AFTER_MIMO25PRO_CAPABILITY_PASS")
        self.assertTrue(payload["authority"]["f0"])
        self.assertFalse(payload["authority"]["p1"])
        self.assertFalse(payload["authority"]["toolsandbox"])
        self.assertFalse(payload["authority"]["appworld_ul"])
        self.assertFalse(payload["authority"]["paper_claim"])

    def test_transport_addendum_preserves_scientific_variables(self):
        payload = self._verified(ADDENDUM)
        self.assertEqual(payload["status"], "F0_SELECTED_BACKBONE_TRANSPORT_COMPATIBILITY_ADDENDUM_PASS")
        self.assertEqual(payload["legacy_preselection_harness_field"], "APPWORLD_FUNCTION_CALLING_V1")
        self.assertEqual(payload["selected_backbone_harness"], "ATOMCODE_CODINGPLAN_MCP_V1")
        self.assertEqual(payload["scientific_variables_changed"], [])

    def test_q1_is_real_mcp_zero_request_predispatch(self):
        payload = self._verified(Q1)
        self.assertEqual(payload["status"], "F0_CODINGPLAN_MIMO25PRO_MCP_PREDISPATCH_PASS")
        self.assertEqual(payload["codingplan_model_requests"], 0)
        self.assertFalse(payload["scientific_dispatch_sent"])
        self.assertEqual(payload["session_mcp_progress_status"], "TOOLS_LISTED")

    def test_contract_binds_selected_backbone_and_keeps_probe_closed(self):
        selection = self._verified(SELECTION)
        payload = self._verified(CONTRACT)
        self.assertEqual(payload["status"], "F0_CODINGPLAN_MIMO25PRO_SOURCE_AUTHORIZED")
        self.assertEqual(payload["selected_backbone_content_sha256"], selection["content_sha256"])
        self.assertEqual(payload["model"]["provider"], PROVIDER)
        self.assertEqual(payload["model"]["profile"], MODEL_PROFILE)
        self.assertEqual(payload["model"]["id"], MODEL_ID)
        self.assertTrue(payload["authority"]["source"])
        self.assertTrue(payload["authority"]["repair_generation"])
        self.assertFalse(payload["authority"]["probe"])
        self.assertFalse(payload["authority"]["p1"])
        self.assertTrue(payload["execution_policy"]["probe_only_after_repair_manifest_frozen_and_committed"])

    def test_source_panel_is_exactly_eight_disjoint_units(self):
        units = enumerate_source_units()
        self.assertEqual(len(units), 8)
        self.assertEqual(len({unit.unit_id for unit in units}), 8)
        self.assertTrue(all(unit.stage == "F0_SOURCE" for unit in units))


if __name__ == "__main__":
    unittest.main()
