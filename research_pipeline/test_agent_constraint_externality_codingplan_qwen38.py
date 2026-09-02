from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_codingplan_qwen38_capability import (
    TOOL_CAP,
    build_addendum,
    units,
)
from research_pipeline.agent_constraint_externality_codingplan_qwen38_provider import (
    ATOMCODE_PROVIDER_PROFILE,
    CONTEXT_WINDOW,
    MAX_OUTPUT_TOKENS,
    PROVIDER_ID,
    RESOLVED_MODEL,
    RETRY_MAX_ATTEMPTS,
    AtomCodeCodingPlanQwen38Client,
    write_experiment_config,
)
from research_pipeline.agent_constraint_externality_runner_core import function_calls


class CodingPlanQwen38CapabilityTest(unittest.TestCase):
    def test_experiment_config_freezes_large_request_limits_without_retry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            write_experiment_config(path)
            text = path.read_text(encoding="utf-8")
            self.assertIn(f'context_window = {CONTEXT_WINDOW}', text)
            self.assertIn(f'max_tokens = {MAX_OUTPUT_TOKENS}', text)
            self.assertIn(f'retry_max_attempts = {RETRY_MAX_ATTEMPTS}', text)
            self.assertIn('max_rounds = 1', text)
            self.assertEqual(CONTEXT_WINDOW, 262144)
            self.assertEqual(MAX_OUTPUT_TOKENS, 65536)
            self.assertEqual(RETRY_MAX_ATTEMPTS, 1)

    def test_fake_one_request_maps_multiple_actions_and_preserves_qwen_identity(self) -> None:
        message = json.dumps(
            {
                "decision": "act",
                "actions": [
                    {"action_id": "A001", "arguments": {}},
                    {"action_id": "A002", "arguments": {}},
                ],
            }
        )
        calls = []

        def runner(command, **kwargs):
            calls.append(command)
            stdout = "\n".join(
                [
                    json.dumps(
                        {
                            "type": "run.started",
                            "provider": ATOMCODE_PROVIDER_PROFILE,
                            "model": RESOLVED_MODEL,
                        }
                    ),
                    json.dumps({"type": "message.delta", "text": message}),
                    json.dumps(
                        {
                            "type": "usage",
                            "prompt_tokens": 100,
                            "completion_tokens": 20,
                            "total_tokens": 120,
                            "cached_tokens": 0,
                        }
                    ),
                ]
            )
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            provider = AtomCodeCodingPlanQwen38Client(
                config_path=root / "config.toml",
                workdir=root / "empty",
                runner=runner,
            )
            receipt = provider.create_response(
                model=RESOLVED_MODEL,
                instructions="complete task",
                input_items=[{"role": "user", "content": "inspect both"}],
                tools=[
                    {
                        "type": "function",
                        "name": "alpha",
                        "description": "alpha",
                        "parameters": {"type": "object", "properties": {}, "required": []},
                    },
                    {
                        "type": "function",
                        "name": "beta",
                        "description": "beta",
                        "parameters": {"type": "object", "properties": {}, "required": []},
                    },
                ],
                temperature=0.0,
            )
            mapped = function_calls(receipt.output)
            self.assertEqual([row["name"] for row in mapped], ["alpha", "beta"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(receipt.provider, PROVIDER_ID)
            self.assertEqual(receipt.resolved_model, RESOLVED_MODEL)
            self.assertEqual(receipt.usage["codingplan_requests"], 1)
            self.assertIn("--no-tools", calls[0])
            self.assertIn("--ephemeral", calls[0])

    def test_full_panel_and_gate_are_unchanged(self) -> None:
        panel = units()
        self.assertEqual(len(panel), 8)
        self.assertEqual(len({row.unit_id for row in panel}), 8)
        self.assertTrue(all(RESOLVED_MODEL in row.unit_id for row in panel))
        self.assertEqual(TOOL_CAP, 16)
        qualification = {
            "content_sha256": "a" * 64,
        }
        addendum = build_addendum(qualification)
        self.assertEqual(addendum["panel"]["episodes"], 8)
        self.assertEqual(addendum["panel"]["tool_call_cap"], 16)
        self.assertFalse(addendum["panel"]["reuse_other_model_measurements"])
        self.assertEqual(addendum["gate"]["tool_loop_completion_min"], 0.75)
        self.assertEqual(addendum["gate"]["target_success_min"], 0.50)
        self.assertEqual(addendum["gate"]["target_success_max"], 0.875)
        self.assertEqual(addendum["gate"]["non_target_preservation_min"], 0.85)
        self.assertFalse(addendum["authority"]["f0"])


if __name__ == "__main__":
    unittest.main()
