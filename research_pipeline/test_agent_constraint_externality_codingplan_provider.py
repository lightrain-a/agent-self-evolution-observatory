from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_codingplan_provider import (
    ATOMCODE_PROVIDER_PROFILE,
    CONTEXT_WINDOW,
    MAX_OUTPUT_TOKENS,
    RETRY_MAX_ATTEMPTS,
    RESOLVED_MODEL,
    AtomCodeCodingPlanClient,
    _extract_json_object,
    _message_text_from_jsonl,
    write_experiment_config,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    AppendOnlyLedger,
    DictionaryWorld,
    EpisodeUnit,
    run_episode,
)


class CodingPlanProviderTest(unittest.TestCase):
    def test_experiment_config_freezes_request_efficient_limits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            write_experiment_config(path)
            text = path.read_text(encoding="utf-8")
            self.assertIn(f'context_window = {CONTEXT_WINDOW}', text)
            self.assertIn(f'max_tokens = {MAX_OUTPUT_TOKENS}', text)
            self.assertIn(f'retry_max_attempts = {RETRY_MAX_ATTEMPTS}', text)
            self.assertIn('max_rounds = 1', text)
            self.assertEqual(RETRY_MAX_ATTEMPTS, 1)
            self.assertEqual(CONTEXT_WINDOW, 512000)
            self.assertEqual(MAX_OUTPUT_TOKENS, 128000)

    def test_wrapped_tool_call_response_is_accepted(self) -> None:
        parsed = _extract_json_object(json.dumps({"tool_call_response":{"type":"tool_calls","calls":[{"tool_id":"T001","arguments":{}}]}}))
        self.assertEqual(parsed["type"], "tool_calls")
        self.assertEqual(parsed["calls"][0]["tool_id"], "T001")

    def test_jsonl_requires_exactly_one_usage_request(self) -> None:
        stdout = "\n".join([
            json.dumps({"type":"run.started","provider":ATOMCODE_PROVIDER_PROFILE,"model":RESOLVED_MODEL}),
            json.dumps({"type":"message.delta","text":"{\\\"type\\\":\\\"final\\\",\\\"message\\\":\\\"ok\\\"}"}),
            json.dumps({"type":"usage","prompt_tokens":1,"completion_tokens":1,"total_tokens":2,"cached_tokens":0}),
        ])
        text, meta = _message_text_from_jsonl(stdout)
        self.assertIn('final', text)
        self.assertEqual(meta["usage"]["total_tokens"], 2)

    def test_fake_atomcode_bridge_preserves_provider_provenance(self) -> None:
        message = json.dumps({"type":"tool_calls","calls":[{"tool_id":"T001","arguments":{"key":"x","value":1}}]})
        final = json.dumps({"type":"final","message":"done"})
        outputs = [message, final]
        calls = []

        def runner(command, **kwargs):
            calls.append(command)
            body = outputs.pop(0)
            stdout = "\n".join([
                json.dumps({"type":"run.started","provider":ATOMCODE_PROVIDER_PROFILE,"model":RESOLVED_MODEL}),
                json.dumps({"type":"message.delta","text":body}),
                json.dumps({"type":"usage","prompt_tokens":10,"completion_tokens":2,"total_tokens":12,"cached_tokens":0}),
            ])
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            provider = AtomCodeCodingPlanClient(
                config_path=root/"config.toml",
                workdir=root/"empty",
                runner=runner,
            )
            ledger = AppendOnlyLedger(root/"ledger.jsonl")
            unit = EpisodeUnit(namespace="capability", key=(RESOLVED_MODEL,"ACE-TEST",1), stage="TEST", family_id="ACE-TEST", repeat=1)
            world = DictionaryWorld()
            result = run_episode(
                unit=unit,
                instruction="set x to 1",
                snapshot_sha256="0"*64,
                repair_sha256=None,
                world=world,
                provider=provider,
                ledger=ledger,
                model=RESOLVED_MODEL,
                max_tool_calls=16,
            )
            self.assertEqual(world.state["x"], 1)
            self.assertEqual(result["provider_request_count"], 2)
            self.assertEqual(len(calls), 2)
            dispatch = ledger.rows()[0]
            self.assertEqual(dispatch["provider"], provider.provider_id)
            self.assertEqual(dispatch["base_url"], provider.base_url)
            self.assertTrue(all("--no-tools" in command for command in calls))
            self.assertTrue(all("--ephemeral" in command for command in calls))


if __name__ == "__main__":
    unittest.main()
