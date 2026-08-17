from __future__ import annotations

import unittest

from .ark_provider import ArkResponsesClient, ArkSettings


class _Response:
    text = ""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

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
            r"Ark response incomplete before assistant output; response_id=resp_test; reason=length; requested_model=deepseek-v4-pro; resolved_model=deepseek-v4-pro-260425; output_tokens=1200; reasoning_tokens=1200",
        ) as caught:
            client.respond("x", model="deepseek-v4-pro", max_output_tokens=1200, thinking="enabled")
        self.assertEqual("resp_test", caught.exception.response_id)
        self.assertEqual("incomplete", caught.exception.response_status)

    def test_incomplete_response_is_not_reposted_when_client_retries_are_enabled(self) -> None:
        client = ArkResponsesClient(ArkSettings(api_key="test", max_retries=2))
        calls = []

        def post(*args, **kwargs):
            calls.append(kwargs["json"])
            return _Response({
                "id": "resp_once",
                "status": "incomplete",
                "model": "glm-5.3-260817",
                "incomplete_details": {"reason": "length"},
                "output": [],
                "usage": {"output_tokens": 4096},
            })

        client.session.post = post
        with self.assertRaisesRegex(RuntimeError, "response_id=resp_once"):
            client.respond("x", model="glm-5.3")
        self.assertEqual(1, len(calls))

    def test_retrieve_response_uses_get_only(self) -> None:
        client = self.client()
        gets = []
        client.session.post = lambda *args, **kwargs: self.fail("retrieve must not POST")
        client.session.get = lambda url, **kwargs: gets.append(url) or _Response({
            "id": "resp_existing",
            "status": "completed",
            "model": "glm-5.3-260817",
            "output": [{"type": "message", "content": [{"type": "output_text", "text": "done"}]}],
            "usage": {"output_tokens": 3},
        })
        result = client.retrieve_response("resp_existing")
        self.assertEqual([client.endpoint + "/resp_existing"], gets)
        self.assertEqual("completed", result["status"])
        self.assertEqual("done", result["text"])

    def test_poll_response_reuses_same_receipt_until_terminal(self) -> None:
        client = self.client()
        gets = []
        payloads = [
            {"id": "resp_existing", "status": "in_progress", "model": "glm-5.3-260817", "output": []},
            {"id": "resp_existing", "status": "completed", "model": "glm-5.3-260817", "output": [{"type": "message", "content": [{"type": "output_text", "text": "done"}]}]},
        ]
        client.session.post = lambda *args, **kwargs: self.fail("poll must not POST")
        client.session.get = lambda url, **kwargs: gets.append(url) or _Response(payloads.pop(0))
        result = client.poll_response("resp_existing", max_polls=2)
        self.assertEqual(2, len(gets))
        self.assertEqual("completed", result["status"])
        self.assertEqual(2, result["poll_count"])
        self.assertEqual("done", result["text"])

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
            r"contained neither assistant output_text nor function_call; response_id=resp_test; status=completed",
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
        self.assertFalse(result["thinking_compatibility_fallback"])

    def test_unsupported_disabled_thinking_retries_once_without_thinking(self) -> None:
        client = self.client()
        calls = []

        def post(*args, **kwargs):
            calls.append(dict(kwargs["json"]))
            if len(calls) == 1:
                return _Response({
                    "error": {
                        "code": "InvalidParameter",
                        "message": "thinking.type `disabled` is not supported by this model",
                    }
                }, status_code=400)
            return _Response({
                "id": "resp_glm",
                "status": "completed",
                "model": "glm-5.3-260817",
                "output": [{"type": "message", "content": [{"type": "output_text", "text": "ok"}]}],
                "usage": {"output_tokens": 1},
            })

        client.session.post = post
        result = client.respond("x", model="glm-5.3", thinking="disabled")
        self.assertEqual(2, len(calls))
        self.assertEqual({"type": "disabled"}, calls[0]["thinking"])
        self.assertNotIn("thinking", calls[1])
        self.assertEqual("glm-5.3-260817", result["resolved_model"])
        self.assertEqual("disabled", result["thinking_requested"])
        self.assertIsNone(result["thinking_effective"])
        self.assertTrue(result["thinking_compatibility_fallback"])

    def test_strict_mode_can_disable_thinking_compatibility_repost(self) -> None:
        client = self.client()
        calls = []
        client.session.post = lambda *args, **kwargs: calls.append(dict(kwargs["json"])) or _Response(
            {"error": {"code":"InvalidParameter","message":"thinking.type `disabled` is not supported by this model"}}, status_code=400
        )
        with self.assertRaisesRegex(RuntimeError, "thinking.type"):
            client.respond("x", model="glm-5.3", thinking="disabled", allow_thinking_compatibility_fallback=False)
        self.assertEqual(1, len(calls))
        self.assertEqual({"type":"disabled"}, calls[0]["thinking"])

    def test_other_400_does_not_trigger_thinking_compatibility_retry(self) -> None:
        client = self.client()
        calls = []
        client.session.post = lambda *args, **kwargs: calls.append(kwargs["json"]) or _Response(
            {"error": {"message": "invalid max_output_tokens"}}, status_code=400
        )
        with self.assertRaisesRegex(RuntimeError, "invalid max_output_tokens"):
            client.respond("x", model="glm-5.3", thinking="disabled")
        self.assertEqual(1, len(calls))


if __name__ == "__main__":
    unittest.main()
