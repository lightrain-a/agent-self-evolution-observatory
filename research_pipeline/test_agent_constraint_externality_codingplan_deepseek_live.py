from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_codingplan_deepseek_live import (
    CONTEXT_WINDOW,
    CONTRACT_OUTPUT,
    MAX_OUTPUT_TOKENS,
    MODEL_ID,
    MODEL_PROFILE,
    MODEL_ROUND_CAP,
    Q1_OUTPUT,
    RETRY_MAX_ATTEMPTS,
    SELECTION_OUTPUT,
    TOOL_CALL_CAP,
    atomcode_config,
    units,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_file, sha256_value


class DeepSeekLiveCapabilityB0Tests(unittest.TestCase):
    def _verified(self, path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        claimed = payload["content_sha256"]
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        return payload

    def test_selection_is_outcome_blind_and_prior_deepseek_is_void(self):
        payload = self._verified(SELECTION_OUTPUT)
        self.assertEqual(
            payload["status"],
            "CODINGPLAN_MIDDLE_BACKBONE_DEEPSEEK_V4_FLASH_SELECTED_OUTCOME_BLIND",
        )
        self.assertEqual(payload["deepseek_valid_scientific_measurements_before_b0"], 0)
        self.assertTrue(payload["deepseek_prior_attempts"])
        self.assertFalse(payload["authority"]["f0"])

    def test_q1_lists_real_appworld_tools_with_zero_model_requests(self):
        payload = self._verified(Q1_OUTPUT)
        self.assertEqual(payload["status"], "CODINGPLAN_DEEPSEEK_LIVE_MCP_PREDISPATCH_PASS")
        self.assertEqual(payload["codingplan_model_requests"], 0)
        self.assertEqual(payload["codingplan_window_used_before"], payload["codingplan_window_used_after"])
        self.assertEqual(payload["session_mcp_progress_status"], "TOOLS_LISTED")
        self.assertGreater(payload["session_mcp_tool_count"], 0)
        self.assertFalse(payload["scientific_dispatch_sent"])

    def test_contract_freezes_same_panel_and_gate_without_f0(self):
        payload = self._verified(CONTRACT_OUTPUT)
        self.assertEqual(payload["status"], "CODINGPLAN_DEEPSEEK_LIVE_CAPABILITY_B0_AUTHORIZED")
        self.assertEqual(payload["selection_sha256"], self._verified(SELECTION_OUTPUT)["content_sha256"])
        self.assertEqual(payload["q1_predispatch_sha256"], self._verified(Q1_OUTPUT)["content_sha256"])
        self.assertEqual(payload["model"]["profile"], MODEL_PROFILE)
        self.assertEqual(payload["model"]["id"], MODEL_ID)
        self.assertEqual(payload["model"]["context_window"], CONTEXT_WINDOW)
        self.assertEqual(payload["model"]["max_output_tokens"], MAX_OUTPUT_TOKENS)
        self.assertEqual(payload["model"]["retry_max_attempts"], RETRY_MAX_ATTEMPTS)
        self.assertEqual(payload["harness"]["model_round_cap_per_episode"], MODEL_ROUND_CAP)
        self.assertEqual(payload["harness"]["appworld_tool_call_cap"], TOOL_CALL_CAP)
        self.assertEqual(payload["panel"]["episodes"], 8)
        self.assertFalse(payload["harness"]["retry_allowed"])
        self.assertFalse(payload["harness"]["replacement_allowed"])
        self.assertFalse(payload["authority"]["f0"])

    def test_exact_eight_units_and_provider_managed_reasoning(self):
        rows = units()
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row.unit_id for row in rows}), 8)
        self.assertTrue(all(MODEL_ID in row.unit_id for row in rows))
        config = atomcode_config()
        self.assertIn("context_window = 512000", config)
        self.assertIn("max_tokens = 128000", config)
        self.assertNotIn("reasoning_effort", config)
        self.assertIn("ai_session_naming = false", config)

    def test_q1_binds_current_runner_source(self):
        payload = self._verified(Q1_OUTPUT)
        from research_pipeline import agent_constraint_externality_codingplan_deepseek_live as runner
        self.assertEqual(payload["runner_source_sha256"], sha256_file(runner.Path(runner.__file__)))


if __name__ == "__main__":
    unittest.main()
