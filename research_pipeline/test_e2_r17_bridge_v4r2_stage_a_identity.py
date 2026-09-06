from __future__ import annotations

import types
import unittest

from scripts.qualify_e2_r17_bridge_v4r2_stage_a_identity import (
    IDENTITY_STATUS,
    build_payload,
    qualify_once,
)


class FakeClient:
    def __init__(self, result=None, error=None):
        self.settings = types.SimpleNamespace(max_retries=0)
        self.result = result
        self.error = error
        self.calls = []

    def respond(self, prompt, **kwargs):
        self.calls.append((prompt, kwargs))
        if self.error is not None:
            raise self.error
        return dict(self.result or {})


class BridgeV4R2StageAIdentityTests(unittest.TestCase):
    def test_exact_identity_pass_is_non_scientific_and_single_call(self) -> None:
        client = FakeClient(
            result={
                "text": "BRIDGE_V4R2_STAGE_A_IDENTITY_OK",
                "resolved_model": "deepseek-v4-pro-ga-260813",
                "status": "completed",
                "usage": {"input_tokens": 10, "output_tokens": 1},
                "response_id": "resp_fake",
            }
        )
        row = qualify_once(client)
        self.assertEqual(row["status"], "PASS")
        self.assertEqual(len(client.calls), 1)
        kwargs = client.calls[0][1]
        self.assertEqual(kwargs["model"], "deepseek-v4-pro")
        self.assertEqual(kwargs["max_output_tokens"], 8192)
        self.assertEqual(kwargs["thinking"], "disabled")
        self.assertEqual(kwargs["temperature"], 0)
        self.assertFalse(kwargs["allow_thinking_compatibility_fallback"])
        payload = build_payload(
            row=row,
            route="https://ark.cn-beijing.volces.com/api/plan/v3",
            source_default_model="whatever",
        )
        self.assertEqual(payload["status"], IDENTITY_STATUS)
        self.assertEqual(payload["scientific_tranche"], "E2-R17-BRIDGE-V4R2-STAGE-A")
        self.assertFalse(payload["scientific_experiment"])
        self.assertTrue(payload["authority"]["preexecution_identity_qualification"])
        self.assertFalse(payload["authority"]["provider_scientific_io"])
        self.assertFalse(payload["authority"]["search_pool_acquisition"])

    def test_resolved_model_drift_holds(self) -> None:
        row = qualify_once(
            FakeClient(
                result={
                    "text": "BRIDGE_V4R2_STAGE_A_IDENTITY_OK",
                    "resolved_model": "deepseek-v4-pro-future-release",
                    "status": "completed",
                    "usage": {},
                    "response_id": "resp_fake",
                }
            )
        )
        self.assertEqual(row["status"], "HOLD_IDENTITY_DRIFT")

    def test_text_drift_holds(self) -> None:
        row = qualify_once(
            FakeClient(
                result={
                    "text": "extra words",
                    "resolved_model": "deepseek-v4-pro-ga-260813",
                    "status": "completed",
                    "usage": {},
                    "response_id": "resp_fake",
                }
            )
        )
        self.assertEqual(row["status"], "HOLD_IDENTITY_DRIFT")

    def test_quota_failure_is_fail_closed_without_retry(self) -> None:
        client = FakeClient(error=RuntimeError("429 AccountQuotaExceeded"))
        row = qualify_once(client)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(row["status"], "HOLD_PROVIDER_QUOTA")
        self.assertFalse(row["automatic_retry_authorized"])


if __name__ == "__main__":
    unittest.main()
