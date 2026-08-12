from __future__ import annotations

import unittest

from .ark_provider import ArkResponsesClient, ArkSettings


class _Response:
    status_code = 200
    text = ""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class ArkProviderTest(unittest.TestCase):
    def client(self) -> ArkResponsesClient:
        return ArkResponsesClient(ArkSettings(api_key="test", max_retries=0))

    def test_incomplete_reasoning_only_response_reports_length_and_tokens(self) -> None:
        client = self.client()
        client.session.post = lambda *args, **kwargs: _Response({
            "id": "resp_test",
            "status": "incomplete",
            "model": "deepseek-v4-pro-260425",
            "incomplete_details": {"reason": "length"},
            "output": [{"type": "reasoning", "summary": []}],
            "usage": {
                "output_tokens": 1200,
                "output_tokens_details": {"reasoning_tokens": 1200},
            },
        })
        with self.assertRaisesRegex(
            RuntimeError,
            r"Ark response incomplete before assistant output; reason=length; requested_model=deepseek-v4-pro; resolved_model=deepseek-v4-pro-260425; output_tokens=1200; reasoning_tokens=1200",
        ):
            client.respond("x", model="deepseek-v4-pro", max_output_tokens=1200, thinking="enabled")

    def test_completed_response_without_assistant_output_is_not_mislabeled_as_length(self) -> None:
        client = self.client()
        client.session.post = lambda *args, **kwargs: _Response({
            "id": "resp_test",
            "status": "completed",
            "model": "deepseek-v4-pro-260425",
            "output": [],
            "usage": {"output_tokens": 0},
        })
        with self.assertRaisesRegex(
            RuntimeError,
            r"contained neither assistant output_text nor function_call; status=completed",
        ):
            client.respond("x", model="deepseek-v4-pro")

    def test_normal_output_text_still_passes(self) -> None:
        client = self.client()
        client.session.post = lambda *args, **kwargs: _Response({
            "id": "resp_test",
            "status": "completed",
            "model": "deepseek-v4-pro-260425",
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "ok"}]}],
            "usage": {"output_tokens": 1, "output_tokens_details": {"reasoning_tokens": 0}},
        })
        result = client.respond("x", model="deepseek-v4-pro")
        self.assertEqual(result["text"], "ok")
        self.assertEqual(result["resolved_model"], "deepseek-v4-pro-260425")


if __name__ == "__main__":
    unittest.main()
