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
    DEFAULT_NETWORK_ADDENDUM,
    DEFAULT_AWM,
    DEFAULT_BROWSERART,
    load_network_addendum,
    preflight,
)
from research_pipeline.agent_safety_g1_atomgit_q0_runner import (
    BROWSER_NETWORK_ADDENDUM_ID,
    BROWSER_NETWORK_MODE,
    EXPECTED_BROWSER_RUNTIME_PYTHON,
    browser_chromium_kwargs,
    candidate_receipt,
    validate_authority,
    run_cascade,
    validate_browser_runtime,
    RunnerError,
)


class G1AtomGitQ0Test(unittest.TestCase):
    def test_frozen_candidate_order(self) -> None:
        amendment=json.loads(DEFAULT_AMENDMENT.read_text(encoding="utf-8"))
        self.assertEqual([x["model_id"] for x in amendment["outcome_blind_candidate_order"]],["qwen3.8-27b","GLM-5.2","deepseek-v4-flash"])
        self.assertFalse(amendment["authority"]["q0_model_requests"])
        self.assertFalse(amendment["authority"]["harmful_model_calls"])

    def authority(self) -> dict:
        return {"artifact_id":"AGENT-SAFETY-G1-ATOMGIT-Q0-EXECUTION-AUTHORITY-20260906","status":"ATOMGIT_Q0_BENIGN_CAPABILITY_EXECUTION_AUTHORIZED","candidate_order":["qwen3.8-27b","GLM-5.2","deepseek-v4-flash"],"task_ids":list(range(10)),"max_steps":10,"required_success_count":10,"harmful_model_calls":False,"p0_execution_authorized":False,"browser_network_mode":BROWSER_NETWORK_MODE,"browser_network_addendum_id":BROWSER_NETWORK_ADDENDUM_ID}

    def test_network_addendum_is_uniform_and_zero_authority(self) -> None:
        addendum=load_network_addendum(DEFAULT_NETWORK_ADDENDUM)
        self.assertEqual(addendum["runtime_contract"]["browser_network_mode"],BROWSER_NETWORK_MODE)
        self.assertTrue(addendum["runtime_contract"]["same_proxy_endpoint_for_all_ten_tasks"])
        self.assertFalse(addendum["runtime_contract"]["task_specific_proxy_or_route_override"])
        self.assertFalse(addendum["authority"]["q0_model_requests"])
        self.assertFalse(addendum["authority"]["harmful_model_calls"])

    def test_frozen_browser_runtime_is_required(self) -> None:
        with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.sys.executable",str(EXPECTED_BROWSER_RUNTIME_PYTHON)):
            validate_browser_runtime()
        with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.sys.executable","/usr/bin/python3"):
            with self.assertRaisesRegex(RunnerError,"frozen BrowserGym runtime python"):
                validate_browser_runtime()

    def test_browser_proxy_is_explicit_uniform_chromium_binding(self) -> None:
        self.assertEqual(browser_chromium_kwargs("http://127.0.0.1:7897"),{"proxy":{"server":"http://127.0.0.1:7897"}})
        with self.assertRaisesRegex(RunnerError,"explicit browser proxy URL required"):
            browser_chromium_kwargs("")

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
        authority=self.authority()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); auth=root/"auth.toml"; auth.write_text("placeholder",encoding="utf-8")
            with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.validate_browser_runtime"), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.configure_imports"), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.probe_codingplan_usage",return_value={"used":296,"remaining":204,"limit":500,"next_reset_at":"later"}), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.run_episode") as run_episode_mock:
                result=run_cascade(authority=authority,output_root=root/"out",awm=root/"awm",browserart=root/"bar",auth_path=auth,browser_proxy="http://127.0.0.1:7897")
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
        base=self.authority()
        validate_authority(base)
        bad=dict(base); bad["harmful_model_calls"]=True
        with self.assertRaises(RunnerError): validate_authority(bad)
        bad_network=dict(base); bad_network["browser_network_mode"]="TASK_SPECIFIC_PROXY"
        with self.assertRaisesRegex(RunnerError,"browser-network mode drift"): validate_authority(bad_network)

    def test_uniform_proxy_is_forwarded_to_every_started_episode(self) -> None:
        authority=self.authority()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); auth=root/"auth.toml"; auth.write_text("placeholder",encoding="utf-8")
            calls=[]
            def fake_episode(task_id,**kwargs):
                calls.append((task_id,kwargs["model_id"],kwargs["browser_proxy"]))
                return {"task_id":task_id,"status":"COMPLETE_DIAGNOSTIC","success_by_step10":True,"provider_calls":{"codingplan_request_delta_sum":1}}
            with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.validate_browser_runtime"), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.configure_imports"), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.probe_codingplan_usage",return_value={"used":0,"remaining":500,"limit":500,"next_reset_at":"later"}), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_runner.run_episode",side_effect=fake_episode):
                result=run_cascade(authority=authority,output_root=root/"out",awm=root/"awm",browserart=root/"bar",auth_path=auth,browser_proxy="http://127.0.0.1:7897")
            self.assertEqual(result["selected_primary"],"qwen3.8-27b")
            self.assertEqual(len(calls),10)
            self.assertEqual({row[2] for row in calls},{"http://127.0.0.1:7897"})
            self.assertTrue(result["same_proxy_for_all_candidates_and_tasks"])
            self.assertFalse(result["task_specific_proxy_override"])

    def test_current_preflight_missing_auth_is_zero_request_hold(self) -> None:
        network_pass={"mode":BROWSER_NETWORK_MODE,"proxy_endpoint":"http://127.0.0.1:7897","requests":[],"pass":True,"task_specific_override":False,"provider_calls":0}
        with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_preflight.find_auth",return_value=(None,["/nonexistent/auth.toml"])), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_preflight.probe_browser_proxy",return_value=network_pass):
            result=preflight(amendment=DEFAULT_AMENDMENT,awm_root=DEFAULT_AWM,browserart_root=DEFAULT_BROWSERART,browser_proxy="http://127.0.0.1:7897")
        self.assertEqual(result["status"],"PRE_DISPATCH_OPERATIONAL_HOLD_AUTH_MISSING")
        self.assertFalse(result["dispatch_attempted"])
        self.assertEqual(result["model_request_delta"],0)
        self.assertFalse(result["scientific_outcome_created"])
        self.assertFalse(result["q0_execution_authorized"])
        self.assertTrue(result["checks"]["awm"]["pass"])
        self.assertTrue(result["checks"]["browserart"]["pass"])
        self.assertTrue(result["checks"]["generic_agent"]["pass"])
        self.assertTrue(result["checks"]["atomcode_binary"]["pass"])
        self.assertTrue(result["checks"]["browser_network_addendum"]["pass"])
        self.assertTrue(result["checks"]["browser_network"]["pass"])

    def test_missing_browser_proxy_holds_before_auth(self) -> None:
        with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_preflight.find_auth",return_value=(None,["/nonexistent/auth.toml"])), mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_preflight.probe_browser_proxy",return_value={"mode":BROWSER_NETWORK_MODE,"proxy_endpoint":None,"requests":[],"pass":False,"reason":"browser proxy is not configured"}):
            result=preflight(amendment=DEFAULT_AMENDMENT,awm_root=DEFAULT_AWM,browserart_root=DEFAULT_BROWSERART)
        self.assertEqual(result["status"],"PRE_DISPATCH_OPERATIONAL_HOLD_BROWSER_NETWORK_UNAVAILABLE")
        self.assertEqual(result["model_request_delta"],0)
        self.assertFalse(result["q0_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
