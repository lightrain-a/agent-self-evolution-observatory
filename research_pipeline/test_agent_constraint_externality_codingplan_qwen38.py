from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_codingplan_prereg import (
    CONTEXT_WINDOW,
    CONTRACT_OUTPUT,
    MAX_OUTPUT_TOKENS,
    MODEL_ID,
    MODEL_ROUND_CAP,
    Q0_OUTPUT,
    Q1_OUTPUT,
    REASONING_EFFORT,
    RETRY_MAX_ATTEMPTS,
    TOOL_CALL_CAP,
)
from research_pipeline.agent_constraint_externality_codingplan_qwen38_capability import (
    agents_md,
    atomcode_config,
    ledger_states,
    prepare_unit_runtime,
    units,
)
from research_pipeline.agent_constraint_externality_codingplan_qwen38_closeout import (
    OUTPUT as CLOSEOUT_OUTPUT,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_value


class CodingPlanQwen38CapabilityTests(unittest.TestCase):
    def test_q0_is_content_addressed_and_mcp_only(self) -> None:
        q0 = json.loads(Q0_OUTPUT.read_text(encoding="utf-8"))
        claimed = q0["content_sha256"]
        unsigned = dict(q0); unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        self.assertEqual(q0["status"], "CODINGPLAN_MCP_Q0_PASS")
        self.assertEqual(q0["mcp_tool_names"], ["mcp__appworld__set_value"])
        self.assertEqual(q0["non_mcp_tool_calls"], 0)

    def test_q1_is_zero_request_real_appworld_mcp_predispatch(self) -> None:
        q1 = json.loads(Q1_OUTPUT.read_text(encoding="utf-8"))
        claimed = q1["content_sha256"]
        unsigned = dict(q1); unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        self.assertEqual(q1["status"], "CODINGPLAN_APPWORLD_MCP_LIVE_PREDISPATCH_PASS")
        self.assertFalse(q1["scientific_dispatch_sent"])
        self.assertEqual(q1["codingplan_model_requests"], 0)
        self.assertEqual(q1["session_mcp_progress_status"], "TOOLS_LISTED")
        self.assertGreater(q1["session_mcp_tool_count"], 0)

    def test_contract_freezes_large_context_and_no_retry(self) -> None:
        contract = json.loads(CONTRACT_OUTPUT.read_text(encoding="utf-8"))
        claimed = contract["content_sha256"]
        unsigned = dict(contract); unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        self.assertEqual(contract["status"], "CODINGPLAN_QWEN38_CAPABILITY_A0_AUTHORIZED")
        self.assertEqual(contract["model"]["id"], MODEL_ID)
        self.assertEqual(contract["model"]["context_window"], CONTEXT_WINDOW)
        self.assertEqual(contract["model"]["max_output_tokens"], MAX_OUTPUT_TOKENS)
        self.assertEqual(contract["model"]["reasoning_effort"], REASONING_EFFORT)
        self.assertEqual(contract["model"]["retry_max_attempts"], RETRY_MAX_ATTEMPTS)
        self.assertEqual(RETRY_MAX_ATTEMPTS, 1)
        self.assertEqual(contract["substrate"]["tool_call_cap"], TOOL_CALL_CAP)
        self.assertEqual(contract["panel"]["model_round_cap_per_episode"], MODEL_ROUND_CAP)
        self.assertFalse(contract["authority"]["f0"])
        self.assertEqual(contract["q1_appworld_mcp_predispatch_sha256"], json.loads(Q1_OUTPUT.read_text(encoding="utf-8"))["content_sha256"])

    def test_closeout_separates_scientific_rounds_from_account_window_requests(self) -> None:
        closeout = json.loads(CLOSEOUT_OUTPUT.read_text(encoding="utf-8"))
        claimed = closeout["content_sha256"]
        unsigned = dict(closeout); unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        self.assertEqual(closeout["status"], "CODINGPLAN_QWEN38_CAPABILITY_A0_CLOSEOUT_CEILING_STOP")
        self.assertEqual(closeout["scientific_verdict"], "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP")
        accounting = closeout["execution_accounting"]
        self.assertEqual(accounting["scientific_model_round_count"], 69)
        self.assertEqual(accounting["codingplan_account_window_request_delta"], 70)
        self.assertEqual(accounting["account_level_unattributed_request_count"], 1)
        self.assertEqual(len(accounting["inter_unit_account_window_gaps"]), 1)
        self.assertFalse(closeout["strict_direct_api_comparison"])
        self.assertFalse(closeout["authority"]["f0"])

    def test_exact_eight_unit_panel(self) -> None:
        rows = units()
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row.unit_id for row in rows}), 8)
        self.assertTrue(all(MODEL_ID in row.unit_id for row in rows))

    def test_atomcode_profile_disables_auxiliary_naming_and_uses_max_output(self) -> None:
        config = atomcode_config()
        self.assertIn(f"context_window = {CONTEXT_WINDOW}", config)
        self.assertIn(f"max_tokens = {MAX_OUTPUT_TOKENS}", config)
        self.assertIn(f"retry_max_attempts = {RETRY_MAX_ATTEMPTS}", config)
        self.assertIn(f'reasoning_effort = "{REASONING_EFFORT}"', config)
        self.assertIn("ai_session_naming = false", config)
        self.assertIn(f"max_rounds = {MODEL_ROUND_CAP}", config)
        instructions = agents_md()
        self.assertIn("mcp__appworld__", instructions)
        self.assertIn("Never use host coding", instructions)
        self.assertIn("Batch independent AppWorld tool calls", instructions)

    def test_relative_episode_root_is_canonicalized_before_atomcode_start(self) -> None:
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            try:
                atom_home, workdir, progress, _ = prepare_unit_runtime(
                    unit=units()[0], unit_root=Path("relative-episode")
                )
                self.assertTrue(atom_home.is_absolute())
                self.assertTrue(workdir.is_absolute())
                self.assertTrue(progress.is_absolute())
                self.assertTrue(str(atom_home).startswith(str(Path(directory).resolve())))
            finally:
                os.chdir(original)

    def test_codingplan_ledger_is_exactly_once(self) -> None:
        unit = units()[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.jsonl"
            path.write_text(json.dumps({"event":"DISPATCH","unit_id":unit.unit_id}) + "\n", encoding="utf-8")
            self.assertEqual(ledger_states(path)[unit.unit_id], "UNKNOWN_AFTER_DISPATCH")
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"event":"COMPLETION","unit_id":unit.unit_id}) + "\n")
            self.assertEqual(ledger_states(path)[unit.unit_id], "COMPLETION")


if __name__ == "__main__":
    unittest.main()
