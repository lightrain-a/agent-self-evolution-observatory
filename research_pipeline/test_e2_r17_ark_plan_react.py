from __future__ import annotations

import asyncio
import json
import unittest

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM, _render_messages, _responses_tools


class ArkPlanReactTests(unittest.TestCase):
    def settings(self) -> ArkSettings:
        return ArkSettings(
            api_key="test-key",
            base_url="https://ark.cn-beijing.volces.com/api/plan/v3",
            default_model="ark-code-latest",
            timeout_seconds=30,
            max_retries=0,
        )

    def test_chat_tool_schema_is_converted_to_responses_schema(self) -> None:
        tools = _responses_tools(
            [
                {
                    "type": "function",
                    "function": {
                        "name": "shell",
                        "description": "Run commands",
                        "parameters": {
                            "type": "object",
                            "properties": {"commands": {"type": "array", "items": {"type": "string"}}},
                            "required": ["commands"],
                        },
                    },
                }
            ]
        )
        self.assertEqual(tools[0]["type"], "function")
        self.assertEqual(tools[0]["name"], "shell")
        self.assertNotIn("function", tools[0])
        self.assertEqual(tools[0]["parameters"]["required"], ["commands"])

    def test_transcript_preserves_tool_call_and_result_binding(self) -> None:
        prompt = _render_messages(
            [
                {"role": "system", "content": "system"},
                {"role": "user", "content": "task"},
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {"name": "shell", "arguments": '{"commands":["pwd"]}'},
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "call-1", "name": "shell", "content": "/tmp"},
            ]
        )
        self.assertIn("ASSISTANT_FUNCTION_CALL id=call-1 name=shell", prompt)
        self.assertIn('{")', prompt.replace('{"commands":["pwd"]}', '{")'))
        self.assertIn("FUNCTION_RESULT_BINDING call_id=call-1 name=shell", prompt)
        self.assertIn("/tmp", prompt)

    def test_function_call_is_mapped_back_to_mindmemos_message(self) -> None:
        llm = ArkPlanReactLLM(
            settings=self.settings(),
            requested_model="deepseek-v4-pro",
            required_resolved_model="deepseek-v4-pro-ga-260813",
        )
        llm.client.respond = lambda *args, **kwargs: {
            "requested_model": "deepseek-v4-pro",
            "resolved_model": "deepseek-v4-pro-ga-260813",
            "text": "",
            "function_calls": [
                {
                    "type": "function_call",
                    "call_id": "call-7",
                    "name": "shell",
                    "arguments": json.dumps({"commands": ["pwd"]}),
                }
            ],
            "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
            "response_id": "resp-secret",
            "status": "completed",
        }
        message = asyncio.run(
            llm(
                [{"role": "user", "content": "use the tool"}],
                [
                    {
                        "type": "function",
                        "function": {
                            "name": "shell",
                            "description": "Run",
                            "parameters": {"type": "object", "properties": {}},
                        },
                    }
                ],
            )
        )
        self.assertEqual(message["role"], "assistant")
        self.assertEqual(message["tool_calls"][0]["id"], "call-7")
        self.assertEqual(message["tool_calls"][0]["function"]["name"], "shell")
        receipts = llm.public_receipts()
        self.assertEqual(receipts[0]["resolved_model"], "deepseek-v4-pro-ga-260813")
        self.assertEqual(receipts[0]["provider_retry_limit"], 0)
        self.assertNotEqual(receipts[0]["response_id_sha256"], "resp-secret")
        self.assertNotIn("resp-secret", json.dumps(receipts))

    def test_resolved_model_drift_is_fatal(self) -> None:
        llm = ArkPlanReactLLM(
            settings=self.settings(),
            requested_model="deepseek-v4-pro",
            required_resolved_model="deepseek-v4-pro-ga-260813",
        )
        llm.client.respond = lambda *args, **kwargs: {
            "resolved_model": "other-model",
            "text": "done",
            "function_calls": [],
            "usage": {},
            "response_id": "x",
            "status": "completed",
        }
        with self.assertRaisesRegex(RuntimeError, "resolved-model-drift"):
            asyncio.run(llm([{"role": "user", "content": "x"}], []))


if __name__ == "__main__":
    unittest.main()
