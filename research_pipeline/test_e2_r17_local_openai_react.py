from __future__ import annotations

import asyncio
from types import SimpleNamespace
import unittest

from research_pipeline.e2_r17_local_openai_react import LocalOpenAIReactLLM


class _Message:
    def __init__(self, payload):
        self.payload = payload

    def model_dump(self, *, exclude_none=True):
        del exclude_none
        return dict(self.payload)


class _Completions:
    def __init__(self, response):
        self.response = response
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


class LocalOpenAIReactLLMTest(unittest.TestCase):
    def _adapter(self, resolved_model="local-qwen", raw_tool_call_id="call-1"):
        response = SimpleNamespace(
            model=resolved_model,
            choices=[
                SimpleNamespace(
                    message=_Message(
                        {
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": raw_tool_call_id,
                                    "type": "function",
                                    "function": {
                                        "name": "add",
                                        "arguments": '{"a":7,"b":5}',
                                    },
                                }
                            ],
                        }
                    ),
                    finish_reason="tool_calls",
                )
            ],
            usage=SimpleNamespace(
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
            ),
            id="raw-private-id",
            system_fingerprint="fp-test",
        )
        adapter = LocalOpenAIReactLLM(
            base_url="http://127.0.0.1:18080",
            requested_model="local-qwen",
            required_resolved_model="local-qwen",
            max_output_tokens=256,
            seed=1717,
        )
        completions = _Completions(response)
        adapter.client = SimpleNamespace(
            chat=SimpleNamespace(completions=completions)
        )
        return adapter, completions

    def test_tool_call_and_receipt_are_public_and_fail_closed(self):
        adapter, completions = self._adapter()
        messages = [{"role": "user", "content": "add"}]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "add",
                    "parameters": {"type": "object"},
                },
            }
        ]
        message = asyncio.run(adapter(messages, tools))
        self.assertEqual(message["role"], "assistant")
        self.assertEqual(message["tool_calls"][0]["function"]["name"], "add")
        self.assertRegex(message["tool_calls"][0]["id"], r"^call_[0-9a-f]{24}$")
        self.assertNotEqual(message["tool_calls"][0]["id"], "call-1")
        self.assertEqual(completions.kwargs["temperature"], 0.0)
        self.assertEqual(completions.kwargs["top_p"], 1.0)
        self.assertEqual(completions.kwargs["seed"], 1717)
        self.assertEqual(completions.kwargs["parallel_tool_calls"], False)
        self.assertEqual(
            completions.kwargs["extra_body"],
            {"chat_template_kwargs": {"enable_thinking": False}},
        )
        receipts = adapter.public_receipts()
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]["resolved_model"], "local-qwen")
        self.assertEqual(receipts[0]["provider_retry_limit"], 0)
        self.assertFalse(receipts[0]["hidden_provider_retry_used"])
        self.assertEqual(
            receipts[0]["tool_call_id_policy"],
            "sha256(request_payload):tool_index",
        )
        self.assertNotIn("raw-private-id", str(receipts))
        self.assertEqual(adapter.public_budget_claims(), [])

    def test_transport_tool_call_ids_are_canonicalized(self):
        first, _ = self._adapter(raw_tool_call_id="server-random-a")
        second, _ = self._adapter(raw_tool_call_id="server-random-b")
        messages = [{"role": "user", "content": "add"}]
        tools = [{"type": "function", "function": {"name": "add", "parameters": {}}}]
        first_message = asyncio.run(first(messages, tools))
        second_message = asyncio.run(second(messages, tools))
        self.assertEqual(first_message, second_message)

    def test_resolved_model_drift_is_rejected_before_receipt(self):
        adapter, _ = self._adapter(resolved_model="wrong-model")
        with self.assertRaisesRegex(RuntimeError, "resolved-model-drift"):
            asyncio.run(adapter([{"role": "user", "content": "x"}], []))
        self.assertEqual(adapter.public_receipts(), [])


if __name__ == "__main__":
    unittest.main()
