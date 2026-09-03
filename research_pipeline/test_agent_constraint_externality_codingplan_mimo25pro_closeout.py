from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_codingplan_mimo25pro_closeout import (
    CLOSEOUT,
    FINAL_SELECTION,
    RESULT,
    RUNTIME_LEDGER,
    build_closeout,
    build_final_selection,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_file, sha256_value


class MiMo25ProCapabilityCloseoutTest(unittest.TestCase):
    def test_result_is_first_frozen_ladder_pass(self) -> None:
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "CAPABILITY_CALIBRATION_PASS")
        self.assertEqual(result["model_id"], "mimo-v2.5-pro")
        self.assertEqual(result["model_profile"], "AtomGit-mimo-v2.5-pro")
        self.assertEqual(result["gate"]["target_success_rate"], 0.875)
        self.assertEqual(result["gate"]["tool_loop_completion_rate"], 0.875)
        self.assertEqual(result["gate"]["non_target_preservation_rate"], 1.0)
        self.assertEqual(result["gate"]["malformed_tool_call_count"], 0)
        unsigned = dict(result); unsigned.pop("content_sha256")
        self.assertEqual(result["content_sha256"], sha256_value(unsigned))
        self.assertEqual(result["ledger_sha256"], sha256_file(RUNTIME_LEDGER))

    def test_closeout_separates_scientific_rounds_from_account_window(self) -> None:
        closeout = build_closeout()
        self.assertEqual(closeout["status"], "CODINGPLAN_MIMO25PRO_B3_PASS_CLOSEOUT")
        self.assertEqual(closeout["verdict"], "CAPABILITY_CALIBRATION_PASS")
        self.assertEqual(closeout["valid_capability_measurements"], 8)
        self.assertEqual(closeout["tool_loop_completed_measurements"], 7)
        self.assertEqual(closeout["target_success_measurements"], 7)
        self.assertEqual(closeout["accounting"]["scientific_model_round_count"], 77)
        self.assertEqual(closeout["accounting"]["codingplan_account_window_request_delta"], 78)
        self.assertEqual(closeout["accounting"]["account_level_unattributed_request_count"], 1)
        self.assertFalse(closeout["authority"]["f0"])

    def test_final_selection_freezes_only_mimo25pro_and_not_f0(self) -> None:
        closeout = build_closeout()
        selection = build_final_selection(closeout)
        self.assertEqual(selection["status"], "CAPABILITY_BACKBONE_SELECTED_MIMO25PRO_PASS")
        self.assertEqual(selection["remaining_candidate_order"], [])
        self.assertEqual(
            selection["selected_backbone"],
            {
                "model_id": "mimo-v2.5-pro",
                "model_profile": "AtomGit-mimo-v2.5-pro",
                "provider": "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY",
                "harness": "ATOMCODE_CODINGPLAN_MCP_V1",
            },
        )
        self.assertTrue(selection["authority"]["backbone_selected"])
        self.assertFalse(selection["authority"]["f0"])

    def test_frozen_artifacts_are_content_addressed(self) -> None:
        for path in (CLOSEOUT, FINAL_SELECTION):
            payload = json.loads(path.read_text(encoding="utf-8"))
            unsigned = dict(payload); unsigned.pop("content_sha256")
            self.assertEqual(payload["content_sha256"], sha256_value(unsigned))


if __name__ == "__main__":
    unittest.main()
