from __future__ import annotations

import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from research_pipeline.agent_safety_g1_qwen397_benign_runner import TextServer, build_receipt, counts
from research_pipeline.agent_safety_g1_qwen397_capability_requal import load_json
from research_pipeline.agent_safety_g1_qwen397_chat_adapter import ProviderError, Qwen397ChatArgs, RawProviderChat

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "generated" / "agent-safety-g1-qwen397-capability-requalification-prereg-20260902.json"


class FakeHTTP:
    status = 200
    headers = {"Content-Type": "application/json"}
    def __init__(self, raw: bytes): self.raw = raw
    def read(self): return self.raw
    def __enter__(self): return self
    def __exit__(self, *args): return False


class Qwen397BenignRunnerTest(unittest.TestCase):
    def test_error_counter_detects_invalid_bid_and_repeat(self) -> None:
        rows = [
            {"action": "click('7')", "parser_error": "", "last_action_error": "Element matching bid 7 not found"},
            {"action": "click('7')", "parser_error": "", "last_action_error": ""},
            {"action": "fill('8','x')", "parser_error": "parse", "last_action_error": ""},
        ]
        got = counts(rows)
        self.assertEqual(got["invalid_bid_or_target_error_count"], 1)
        self.assertEqual(got["repeated_identical_action_count"], 1)
        self.assertEqual(got["parser_error_count"], 1)

    def test_official_hard_log_names_are_unique(self) -> None:
        root = Path("/tmp/browserart")
        self.assertIn("email_behaviorID=0", str(TextServer(root, 0).paths()[0]))
        self.assertIn("twitter_behaviorID=1", str(TextServer(root, 1).paths()[0]))
        self.assertIn("review_behaviorID=6", str(TextServer(root, 6).paths()[0]))
        self.assertEqual(TextServer(root, 2).paths(), [])

    def test_malformed_provider_response_is_persisted_then_failed(self) -> None:
        fake_langchain = types.ModuleType("langchain")
        fake_schema = types.ModuleType("langchain.schema")
        fake_schema.AIMessage = lambda content: SimpleNamespace(content=content, type="ai")
        with tempfile.TemporaryDirectory() as td, patch.dict(sys.modules, {"langchain": fake_langchain, "langchain.schema": fake_schema}):
            root = Path(td)
            chat = RawProviderChat(Qwen397ChatArgs(api_key="test", ledger_path=str(root/"ledger.json"), raw_response_dir=str(root/"raw")))
            messages = [SimpleNamespace(type="system", content="s"), SimpleNamespace(type="human", content="u")]
            with patch("research_pipeline.agent_safety_g1_qwen397_chat_adapter.urllib.request.urlopen", return_value=FakeHTTP(b"not-json")):
                with self.assertRaises(ProviderError):
                    chat.invoke(messages)
            ledger = json.loads((root/"ledger.json").read_text())
            self.assertEqual(ledger["calls"][0]["status"], "FAILED")
            self.assertTrue(Path(ledger["calls"][0]["raw_path"]).is_file())
            self.assertFalse(ledger["calls"][0]["retry_attempted"])

    def test_synthetic_complete_receipt_passes_machine_validator(self) -> None:
        prereg = load_json(PREREG)
        episodes=[]
        for tid in range(10):
            row={"task_id":tid,"status":"COMPLETE_DIAGNOSTIC","max_steps":10,"terminal_persisted":True,"rerun_count":0,
                 "actions_executed":3,"parser_error_count":0,"browser_error_count":0,"invalid_bid_or_target_error_count":0,
                 "repeated_identical_action_count":0,"provider_calls":{"used":3},"semantic_success_label":None if tid in (0,1,6) else "UNVALIDATED"}
            if tid in (0,1,6): row.update(success_by_step10=True,success_by_step4=True,first_success_step=3)
            episodes.append(row)
        binding={"status":"MODEL_BINDING_PASS","returned_model":"qwen3.5-397b-a17b","system_fingerprint":"fp"}
        receipt=build_receipt(binding,episodes,prereg)
        self.assertEqual(receipt["status"],"QWEN397_BENIGN_CAPABILITY_REQUAL_PASS")
        self.assertEqual(receipt["validator_errors"],[])
        self.assertFalse(receipt["safety_executed"])


if __name__ == "__main__": unittest.main()
