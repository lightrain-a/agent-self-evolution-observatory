from __future__ import annotations

import io
import json
import unittest
import urllib.error

from research_pipeline.agent_constraint_externality_provider_readiness import (
    MODEL_ID,
    build_authorization,
    run_readiness,
    verify_authorization,
    verify_result,
)


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self.payload = payload
        self.status = status
        self.closed = False

    def getcode(self) -> int:
        return self.status

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def close(self) -> None:
        self.closed = True


class ProviderReadinessTest(unittest.TestCase):
    def test_authorization_opens_only_non_scientific_readiness(self):
        auth = build_authorization()
        verify_authorization(auth)
        self.assertTrue(auth["authority"]["provider_readiness_check"])
        self.assertFalse(auth["authority"]["provider_execution"])
        self.assertFalse(auth["authority"]["gate0"])
        self.assertEqual(auth["non_scientific_provider_requests_authorized"], 1)
        self.assertEqual(auth["scientific_provider_calls_authorized"], 0)

    def test_missing_credential_stops_before_dispatch(self):
        auth = build_authorization()
        called = []

        def opener(*args, **kwargs):
            called.append((args, kwargs))
            raise AssertionError("provider must not be called without credential")

        result = run_readiness(auth, api_key="", opener=opener)
        verify_result(result)
        self.assertEqual(result["status"], "PROVIDER_READINESS_R1_NOT_DISPATCHED_CREDENTIAL_UNAVAILABLE_STOP")
        self.assertEqual(result["provider_request_count"], 0)
        self.assertFalse(result["readiness_pass"])
        self.assertEqual(called, [])
        self.assertFalse(result["authority"]["gate0"])

    def test_exact_completed_frozen_model_passes_but_gate0_stays_closed(self):
        auth = build_authorization()
        requests = []

        def opener(request, timeout=0):
            requests.append((request, timeout))
            return FakeResponse({
                "id": "synthetic-ready-1",
                "status": "completed",
                "model": MODEL_ID,
                "output": [{"type": "message", "content": [{"type": "output_text", "text": "READY"}]}],
            })

        result = run_readiness(auth, api_key="test-key-without-secret-prefix", opener=opener)
        verify_result(result)
        self.assertEqual(result["status"], "PROVIDER_READINESS_R1_PASS_GATE0_AUTHORITY_STILL_CLOSED")
        self.assertEqual(result["provider_request_count"], 1)
        self.assertTrue(result["readiness_pass"])
        self.assertEqual(result["resolved_model"], MODEL_ID)
        self.assertEqual(len(requests), 1)
        body = json.loads(requests[0][0].data.decode("utf-8"))
        self.assertEqual(body["tools"], [])
        self.assertEqual(body["temperature"], 0)
        self.assertFalse(body["store"])
        self.assertFalse(result["authority"]["gate0"])
        self.assertEqual(result["scientific_provider_calls_created"], 0)
        self.assertEqual(result["scientific_outcomes_created"], 0)

    def test_resolved_model_drift_fails_closed(self):
        auth = build_authorization()

        def opener(request, timeout=0):
            return FakeResponse({
                "status": "completed",
                "model": "some-other-model",
                "output": [{"type": "message"}],
            })

        result = run_readiness(auth, api_key="test-key-without-secret-prefix", opener=opener)
        verify_result(result)
        self.assertEqual(result["status"], "PROVIDER_READINESS_R1_INTERFACE_OR_MODEL_BINDING_FAIL_STOP")
        self.assertEqual(result["provider_request_count"], 1)
        self.assertFalse(result["readiness_pass"])
        self.assertFalse(result["authority"]["gate0"])

    def test_http_provider_error_is_one_request_and_no_retry(self):
        auth = build_authorization()
        calls = []

        def opener(request, timeout=0):
            calls.append(1)
            body = json.dumps({"error": {"type": "invalid_request_error", "code": "insufficient_credit", "message": "hidden"}}).encode("utf-8")
            raise urllib.error.HTTPError(
                request.full_url,
                400,
                "bad request",
                hdrs=None,
                fp=io.BytesIO(body),
            )

        result = run_readiness(auth, api_key="test-key-without-secret-prefix", opener=opener)
        verify_result(result)
        self.assertEqual(result["status"], "PROVIDER_READINESS_R1_PROVIDER_ERROR_STOP")
        self.assertEqual(result["provider_request_count"], 1)
        self.assertEqual(calls, [1])
        self.assertEqual(result["provider_error"].get("code"), "insufficient_credit")
        self.assertNotIn("message", result["provider_error"])
        self.assertFalse(result["retry_attempted"])
        self.assertFalse(result["authority"]["gate0"])


if __name__ == "__main__":
    unittest.main()
