from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_codingplan_mimo25pro_live import (
    CATALOG_B1,
    CONTEXT_WINDOW,
    CONTRACT_OUTPUT,
    MODEL_ID,
    MODEL_PROFILE,
    Q1_OUTPUT,
    SEARCH_STATE,
    atomcode_config,
    units,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_file, sha256_value


class Mimo25ProLiveCapabilityB3Tests(unittest.TestCase):
    def _verified(self, path: Path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        claimed = payload["content_sha256"]
        unsigned = dict(payload); unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        return payload

    def test_final_ladder_selects_mimo25pro(self):
        state = self._verified(SEARCH_STATE)
        self.assertEqual(state["status"], "CAPABILITY_BACKBONE_SEARCH_CONTINUE_MIMO25PRO_NEXT")
        self.assertEqual(state["remaining_frozen_order"], ["mimo-v2.5-pro"])
        self.assertEqual(state["next_candidate"], {"model_id": MODEL_ID, "profile": MODEL_PROFILE})
        self.assertFalse(state["authority"]["f0"])

    def test_catalog_limits_are_real_and_uninvented(self):
        catalog = self._verified(CATALOG_B1)
        row = next(x for x in catalog["models"] if x["model_id"] == MODEL_ID)
        self.assertEqual(row["profile"], MODEL_PROFILE)
        self.assertEqual(row["context_window"], CONTEXT_WINDOW)
        self.assertEqual(CONTEXT_WINDOW, 1000000)
        self.assertIsNone(row["max_tokens"])
        config = atomcode_config()
        self.assertIn("context_window = 1000000", config)
        self.assertNotIn("max_tokens", config)
        self.assertNotIn("reasoning_effort", config)
        self.assertIn("retry_max_attempts = 1", config)

    def test_q1_zero_request_real_mcp(self):
        q1 = self._verified(Q1_OUTPUT)
        self.assertEqual(q1["status"], "CODINGPLAN_MIMO25PRO_LIVE_MCP_PREDISPATCH_PASS")
        self.assertEqual(q1["codingplan_model_requests"], 0)
        self.assertEqual(q1["codingplan_window_used_before"], q1["codingplan_window_used_after"])
        self.assertEqual(q1["session_mcp_progress_status"], "TOOLS_LISTED")
        self.assertGreater(q1["session_mcp_tool_count"], 0)
        self.assertFalse(q1["scientific_dispatch_sent"])

    def test_contract_freezes_same_gate_and_no_f0(self):
        contract = self._verified(CONTRACT_OUTPUT)
        state = self._verified(SEARCH_STATE)
        q1 = self._verified(Q1_OUTPUT)
        self.assertEqual(contract["status"], "CODINGPLAN_MIMO25PRO_CAPABILITY_B3_AUTHORIZED")
        self.assertEqual(contract["backbone_search_state_sha256"], state["content_sha256"])
        self.assertEqual(contract["q1_predispatch_sha256"], q1["content_sha256"])
        self.assertEqual(contract["model"]["profile"], MODEL_PROFILE)
        self.assertEqual(contract["model"]["id"], MODEL_ID)
        self.assertEqual(contract["model"]["context_window"], 1000000)
        self.assertEqual(contract["model"]["max_output_tokens_control"], "PROVIDER_MANAGED_UNSET_BY_OFFICIAL_CODINGPLAN_CATALOG")
        self.assertEqual(contract["harness"]["model_round_cap_per_episode"], 20)
        self.assertEqual(contract["harness"]["appworld_tool_call_cap"], 16)
        self.assertFalse(contract["harness"]["retry_allowed"])
        self.assertFalse(contract["harness"]["replacement_allowed"])
        self.assertFalse(contract["authority"]["f0"])

    def test_eight_units_and_q1_binds_runner(self):
        rows = units()
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row.unit_id for row in rows}), 8)
        self.assertTrue(all(MODEL_ID in row.unit_id for row in rows))
        q1 = self._verified(Q1_OUTPUT)
        from research_pipeline import agent_constraint_externality_codingplan_mimo25pro_live as runner
        self.assertEqual(q1["runner_source_sha256"], sha256_file(Path(runner.__file__)))


if __name__ == "__main__":
    unittest.main()
