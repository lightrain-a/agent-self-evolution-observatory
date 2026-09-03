from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_backbone_search import (
    CATALOG_OUTPUT,
    DEEPSEEK_CLOSEOUT,
    EXPECTED_REMAINING,
    SEARCH_STATE_OUTPUT,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_value


class CapabilityBackboneSearchB1Tests(unittest.TestCase):
    def _verified(self, path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        claimed = payload["content_sha256"]
        unsigned = dict(payload)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        return payload

    def test_catalog_refresh_is_zero_request_and_has_frozen_order(self):
        payload = self._verified(CATALOG_OUTPUT)
        self.assertEqual(
            payload["status"],
            "CODINGPLAN_ACCOUNT_CATALOG_REFRESH_PASS_ZERO_MODEL_REQUESTS",
        )
        self.assertEqual(payload["codingplan_model_request_delta"], 0)
        self.assertEqual(
            [row["model_id"] for row in payload["models"]],
            ["GLM-5.2", "deepseek-v4-flash", "mimo-v2.5", "mimo-v2.5-pro", "qwen3.8-27b"],
        )
        glm = payload["models"][0]
        self.assertEqual(glm["profile"], "AtomGit-GLM-5.2")
        self.assertEqual(glm["context_window"], 200000)
        self.assertIsNone(glm["max_tokens"])
        self.assertFalse(payload["authority"]["f0"])

    def test_deepseek_floor_is_closed_without_cap_relaxation(self):
        payload = self._verified(DEEPSEEK_CLOSEOUT)
        self.assertEqual(payload["status"], "CODINGPLAN_DEEPSEEK_LIVE_B0_FLOOR_CLOSEOUT")
        self.assertEqual(payload["verdict"], "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP")
        self.assertEqual(payload["gate"]["tool_loop_completion_rate"], 0.625)
        self.assertEqual(payload["gate"]["target_success_rate"], 0.875)
        self.assertEqual(payload["tool_loop_completed_measurements"], 5)
        self.assertEqual(payload["tool_loop_incomplete_measurements"], 3)
        self.assertEqual(payload["accounting"]["scientific_model_round_count"], 72)
        self.assertEqual(payload["accounting"]["codingplan_account_window_request_delta"], 72)
        self.assertEqual(payload["accounting"]["account_level_unattributed_request_count"], 0)
        self.assertIn("not relaxed", payload["interpretation_boundary"])
        self.assertFalse(payload["authority"]["f0"])

    def test_remaining_candidate_ladder_is_frozen_before_glm(self):
        payload = self._verified(SEARCH_STATE_OUTPUT)
        self.assertEqual(payload["status"], "CAPABILITY_BACKBONE_SEARCH_CONTINUE_GLM52_NEXT")
        self.assertEqual(tuple(payload["remaining_frozen_order"]), EXPECTED_REMAINING)
        self.assertEqual(payload["next_candidate"], {"model_id": "GLM-5.2", "profile": "AtomGit-GLM-5.2"})
        self.assertIn("STOP_AT_FIRST_CAPABILITY_PASS", payload["selection_policy"])
        self.assertIn("FLOOR_OR_CEILING_ADVANCES_ONLY", payload["stop_rule"])
        self.assertFalse(payload["authority"]["f0"])


if __name__ == "__main__":
    unittest.main()
