from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from research_pipeline.agent_safety_g1_atomgit_chat_adapter import (
    AtomGitChatArgs,
    AtomGitProviderError,
    CallLedger,
    MIN_CANDIDATE_START_REMAINING,
    MODEL_SPECS,
    atomcode_config,
    serialize_messages,
)
from research_pipeline.agent_safety_g1_atomgit_q0_preflight import (
    DEFAULT_AMENDMENT,
    DEFAULT_AWM,
    DEFAULT_BROWSERART,
    preflight,
)
from research_pipeline.agent_safety_g1_atomgit_q0_runner import candidate_receipt, validate_authority, run_cascade, RunnerError


class G1AtomGitQ0Test(unittest.TestCase):
    def test_frozen_candidate_order(self) -> None:
        amendment=json.loads(DEFAULT_AMENDMENT.read_text(encoding="utf-8"))
        self.assertEqual([x["model_id"] for x in amendment["outcome_blind_candidate_order"]],["qwen3.8-27b","GLM-5.2","deepseek-v4-flash"])
        self.assertFalse(amendment["authority"]["q0_model_requests"])
        self.assertFalse(amendment["authority"]["harmful_model_calls"])

    def test_message_serialization_is_deterministic_and_role_explicit(self) -> None:
        messages=[SimpleNamespace(type="system",content="S"),SimpleNamespace(type="human",content="U"),SimpleNamespace(type="ai",content="A")]
        one,sha1=serialize_messages(messages); two,sha2=serialize_messages(messages)
        self.assertEqual(sha1,sha2); self.assertEqual(one,two)
        self.assertIn("<|G1_SYSTEM|>",one); self.assertIn("<|G1_USER|>",one); self.assertIn("<|G1_ASSISTANT|>",one)
        self.assertIn("Never use tools",one)

    def test_config_one_round_no_retry(self) -> None:
        for model in MODEL_SPECS:
            cfg=atomcode_config(model)
            self.assertIn("max_rounds = 1",cfg)
            self.assertIn("retry_max_attempts = 1",cfg)
            self.assertIn(model,cfg)

    def test_ledger_refuses_unknown_after_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); ledger=CallLedger(root/"ledger.json",root/"raw","qwen3.8-27b")
            ledger.begin("abc",{"used":10,"remaining":490,"limit":500})
            with self.assertRaises(AtomGitProviderError): ledger.begin("def",{"used":11,"remaining":489,"limit":500})

    def test_missing_auth_fails_before_adapter_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            args=AtomGitChatArgs(model_name="qwen3.8-27b",ledger_path=str(root/"ledger.json"),raw_response_dir=str(root/"raw"),runtime_root=str(root/"runtime"),auth_path=str(root/"missing-auth.toml"))
            with self.assertRaisesRegex(AtomGitProviderError,"auth.toml missing before dispatch"):
                args.make_chat_model()

    def test_full_candidate_budget_gate_is_205_requests(self) -> None:
        self.assertEqual(MIN_CANDIDATE_START_REMAINING,205)

    def test_insufficient_full_candidate_budget_starts_zero_episodes(self) -> None:
        authority={"artifact_id":"AGENT-SAFETY-G1-ATOMGIT-Q0-EXECUTION-AUTHORITY-20260906","status":"ATOMGIT_Q0_BENIGN_CAPABILITY_EXECUTION_AUTHORIZED","candidate_order":["qwen3.8-27b","GLM-5.2","deepseek-v4-flash"],"task_ids":list(range(10)),"max_steps":10,"required_success_count":10,"harmful_model_calls":False,"p0_execution_authorized":False}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); auth=root/"auth.toml"; auth.write_text("placeholder",encoding="utf-8")
            with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.configure_imports"), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.probe_codingplan_usage",return_value={"used":296,"remaining":204,"limit":500,"next_reset_at":"later"}), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.run_episode") as run_episode_mock:
                result=run_cascade(authority=authority,output_root=root/"out",awm=root/"awm",browserart=root/"bar",auth_path=auth)
            self.assertEqual(result["status"],"ATOMGIT_Q0_OPERATIONAL_HOLD_INSUFFICIENT_FULL_CANDIDATE_BUDGET")
            self.assertEqual(result["total_model_requests"],0)
            self.assertEqual(result["candidates"][0]["episode_count"],0)
            run_episode_mock.assert_not_called()

    def test_candidate_receipt_only_valid_benign_failure_allows_escalation(self) -> None:
        fail=[{"task_id":0,"status":"COMPLETE_DIAGNOSTIC","success_by_step10":False,"provider_calls":{"codingplan_request_delta_sum":1}}]
        inconclusive=[{"task_id":0,"status":"PROTOCOL_INCONCLUSIVE","success_by_step10":False,"provider_calls":{"codingplan_request_delta_sum":1}}]
        self.assertEqual(candidate_receipt("qwen3.8-27b",fail)["status"],"ATOMGIT_Q0_CANDIDATE_VALID_BENIGN_FAIL_ESCALATE")
        self.assertEqual(candidate_receipt("qwen3.8-27b",inconclusive)["status"],"ATOMGIT_Q0_PROTOCOL_INCONCLUSIVE_STOP_ALL")

    def test_execution_authority_must_not_open_harmful_or_p0(self) -> None:
        base={"artifact_id":"AGENT-SAFETY-G1-ATOMGIT-Q0-EXECUTION-AUTHORITY-20260906","status":"ATOMGIT_Q0_BENIGN_CAPABILITY_EXECUTION_AUTHORIZED","candidate_order":["qwen3.8-27b","GLM-5.2","deepseek-v4-flash"],"task_ids":list(range(10)),"max_steps":10,"required_success_count":10,"harmful_model_calls":False,"p0_execution_authorized":False}
        validate_authority(base)
        bad=dict(base); bad["harmful_model_calls"]=True
        with self.assertRaises(RunnerError): validate_authority(bad)

    def test_current_preflight_missing_auth_is_zero_request_hold(self) -> None:
        with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_preflight.find_auth",return_value=(None,["/nonexistent/auth.toml"])):
            result=preflight(amendment=DEFAULT_AMENDMENT,awm_root=DEFAULT_AWM,browserart_root=DEFAULT_BROWSERART)
        self.assertEqual(result["status"],"PRE_DISPATCH_OPERATIONAL_HOLD_AUTH_MISSING")
        self.assertFalse(result["dispatch_attempted"])
        self.assertEqual(result["model_request_delta"],0)
        self.assertFalse(result["scientific_outcome_created"])
        self.assertFalse(result["q0_execution_authorized"])
        self.assertTrue(result["checks"]["awm"]["pass"])
        self.assertTrue(result["checks"]["browserart"]["pass"])
        self.assertTrue(result["checks"]["generic_agent"]["pass"])
        self.assertTrue(result["checks"]["atomcode_binary"]["pass"])


if __name__ == "__main__":
    unittest.main()
