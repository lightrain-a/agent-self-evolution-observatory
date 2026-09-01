from __future__ import annotations

import unittest
from unittest.mock import patch

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    ArkCompatibilityError,
    ArkReasoningBankClient,
    ArkReasoningBankSettings,
)


class FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = ""

    def json(self) -> dict:
        return self._payload


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.headers: dict[str, str] = {}
        self.responses = list(responses)
        self.requests: list[dict] = []

    def post(self, endpoint: str, *, json: dict, timeout: float) -> FakeResponse:
        self.requests.append({"endpoint": endpoint, "json": json, "timeout": timeout})
        return self.responses.pop(0)


def settings(**kwargs) -> ArkReasoningBankSettings:
    base = {
        "api_key": "SECRET_SENTINEL",
        "base_url": "https://ark.example/api/plan/v3",
        "model": "ark-code-latest",
        "timeout_seconds": 7.0,
        "max_retries": 0,
    }
    base.update(kwargs)
    return ArkReasoningBankSettings(**base)


def success_payload() -> dict:
    return {
        "id": "resp-secret-receipt",
        "status": "completed",
        "model": "ark-code-latest",
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": "OK"}],
            }
        ],
        "usage": {"input_tokens": 3, "output_tokens": 1},
    }


class ReasoningBankArkProviderTest(unittest.TestCase):
    def test_safe_summary_never_exports_key(self) -> None:
        summary = settings().safe_summary()
        self.assertTrue(summary["configured"])
        self.assertNotIn("api_key", summary)
        self.assertNotIn("SECRET_SENTINEL", str(summary))
        self.assertFalse(summary["secret_value_exported"])

    def test_structured_messages_and_sampling_fields_are_forwarded_without_semantic_rewrite(self) -> None:
        session = FakeSession([FakeResponse(200, success_payload())])
        client = ArkReasoningBankClient(settings(), session=session)
        messages = [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "second"},
            {"role": "user", "content": "third"},
        ]
        result = client.create_response(
            input_items=messages,
            instructions="system",
            temperature=0.2,
            top_p=0.8,
            top_k=40,
            seed=42,
            stop=["END"],
            max_output_tokens=19,
            thinking="disabled",
        )
        body = session.requests[0]["json"]
        self.assertEqual(body["input"], messages)
        self.assertEqual(body["instructions"], "system")
        self.assertEqual(body["temperature"], 0.2)
        self.assertEqual(body["top_p"], 0.8)
        self.assertEqual(body["top_k"], 40)
        self.assertEqual(body["seed"], 42)
        self.assertEqual(body["stop"], ["END"])
        self.assertEqual(body["thinking"], {"type": "disabled"})
        self.assertEqual(body["max_output_tokens"], 19)
        self.assertEqual(result["text"], "OK")
        self.assertEqual(result["raw_text"], "OK")
        self.assertRegex(result["raw_payload_sha256"], r"^[0-9a-f]{64}$")

    def test_raw_text_preserves_memory_induction_split_boundaries(self) -> None:
        payload = success_payload()
        payload["output"][0]["content"][0]["text"] = "  first\n\nsecond  "
        session = FakeSession([FakeResponse(200, payload)])
        client = ArkReasoningBankClient(settings(), session=session)
        result = client.create_response(input_items="probe")
        self.assertEqual(result["text"], "first\n\nsecond")
        self.assertEqual(result["raw_text"], "  first\n\nsecond  ")

    def test_none_max_output_tokens_omits_provider_parameter(self) -> None:
        session = FakeSession([FakeResponse(200, success_payload())])
        client = ArkReasoningBankClient(settings(), session=session)
        client.create_response(input_items="probe", max_output_tokens=None)
        self.assertNotIn("max_output_tokens", session.requests[0]["json"])

    def test_function_result_continuation_preserves_call_identity(self) -> None:
        session = FakeSession([FakeResponse(200, success_payload())])
        client = ArkReasoningBankClient(settings(), session=session)
        client.continue_function_call(
            previous_response_id="response-1",
            call_id="call-1",
            output='{"recorded":731}',
            instructions="finish",
        )
        body = session.requests[0]["json"]
        self.assertEqual(body["previous_response_id"], "response-1")
        self.assertEqual(
            body["input"],
            [{"type": "function_call_output", "call_id": "call-1", "output": '{"recorded":731}'}],
        )
        self.assertTrue(body["store"])

    @patch("research_pipeline.asset_first_stri_reasoningbank_ark_provider.time.sleep", return_value=None)
    def test_retry_reuses_identical_body_only_for_server_failure(self, _sleep) -> None:
        session = FakeSession(
            [
                FakeResponse(503, {"error": {"message": "temporary"}}),
                FakeResponse(200, success_payload()),
            ]
        )
        client = ArkReasoningBankClient(settings(max_retries=1), session=session)
        result = client.create_response(input_items="probe")
        self.assertEqual(len(session.requests), 2)
        self.assertEqual(session.requests[0]["json"], session.requests[1]["json"])
        self.assertEqual(result["transport_attempts"], 2)

    def test_client_error_is_not_retried_and_safe_receipt_has_no_key(self) -> None:
        session = FakeSession([FakeResponse(400, {"error": {"message": "unsupported"}})])
        client = ArkReasoningBankClient(settings(max_retries=2), session=session)
        with self.assertRaises(ArkCompatibilityError) as caught:
            client.create_response(input_items="probe", seed=42)
        receipt = caught.exception.safe_receipt()
        self.assertEqual(len(session.requests), 1)
        self.assertEqual(receipt["status_code"], 400)
        self.assertNotIn("SECRET_SENTINEL", str(receipt))
        self.assertFalse(receipt["credential_material_present"])

    def test_function_call_parser_keeps_provider_arguments_verbatim(self) -> None:
        payload = {
            "id": "r",
            "model": "ark-code-latest",
            "status": "completed",
            "output": [
                {
                    "type": "function_call",
                    "call_id": "call-7",
                    "name": "record_probe",
                    "arguments": '{"value":731}',
                }
            ],
        }
        normalized = ArkReasoningBankClient.normalize(payload, "ark-code-latest")
        self.assertEqual(normalized["function_calls"][0]["arguments"], '{"value":731}')


class ReasoningBankArkLiveArtifactTest(unittest.TestCase):
    ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
    GENERATED = ROOT / "generated"

    def load(self, name: str) -> dict:
        return __import__("json").loads((self.GENERATED / name).read_text(encoding="utf-8"))

    def test_failure_repair_chain_is_preserved(self) -> None:
        q0 = self.load("asset-first-stri-reasoningbank-ark-provider-qualification-result-20260829.json")
        q0b = self.load("asset-first-stri-reasoningbank-ark-provider-identity-resolution-result-20260829.json")
        q0c = self.load("asset-first-stri-reasoningbank-ark-tool-continuation-causal-result-20260829.json")
        self.assertEqual(q0["decision"], "ARK_BACKEND_NOT_YET_QUALIFIED_LOCALIZE_AND_REPAIR")
        self.assertTrue(all(row["ok"] for row in q0["receipts"]))
        self.assertFalse(q0["required_semantics"]["provider_model_identifier"])
        self.assertFalse(q0["seed_semantics"]["same_seed_equal"])
        self.assertFalse(q0["seed_semantics"]["claim_independent_seeded_repeats_authorized"])
        self.assertEqual(q0b["decision"], "ARK_DIRECT_MODEL_NOT_QUALIFIED")
        self.assertTrue(q0b["checks"]["all_resolved_model_direct"])
        self.assertFalse(q0b["checks"]["continuation_exact"])
        self.assertEqual(q0c["decision"], "ARK_CAUSAL_TOOL_CONTINUATION_QUALIFIED")
        self.assertTrue(all(q0c["checks"].values()))

    def test_final_backend_contract_is_direct_and_unseeded(self) -> None:
        final = self.load("asset-first-stri-reasoningbank-ark-provider-final-adjudication-20260829.json")
        self.assertEqual(
            final["decision"],
            "ARK_BACKEND_QUALIFIED_WITH_DIRECT_MODEL_AND_UNSEEDED_PAIRED_REPEATS",
        )
        backend = final["frozen_backend"]
        self.assertEqual(backend["requested_model"], "doubao-seed-evolving")
        self.assertEqual(backend["resolved_model"], "doubao-seed-evolving")
        self.assertEqual(backend["temperature"], 0)
        self.assertEqual(backend["seed"], "omitted")
        self.assertFalse(final["next_authorized_stage"]["memory_induction_execution"])
        self.assertFalse(final["next_authorized_stage"]["p1_behavioral_execution"])

    def test_deepseek_failure_repair_chain_and_final_contract(self) -> None:
        q1 = self.load(
            "asset-first-stri-reasoningbank-deepseek-provider-qualification-result-20260829.json"
        )
        q1b = self.load(
            "asset-first-stri-reasoningbank-deepseek-direct-causal-result-20260829.json"
        )
        final = self.load(
            "asset-first-stri-reasoningbank-deepseek-provider-final-adjudication-20260829.json"
        )
        self.assertEqual(q1["decision"], "ARK_DEEPSEEK_PRO_BACKEND_NOT_QUALIFIED")
        self.assertTrue(q1["checks"]["all_requests_succeeded"])
        self.assertFalse(q1["checks"]["causal_tool_result_consumed"])
        self.assertEqual(
            q1b["decision"], "ARK_DEEPSEEK_PRO_DIRECT_CAUSAL_QUALIFIED"
        )
        self.assertTrue(all(q1b["checks"].values()))
        self.assertEqual(
            final["decision"],
            "ARK_DEEPSEEK_PRO_BACKEND_QUALIFIED_WITH_DIRECT_VERSION_AND_UNSEEDED_PAIRED_REPEATS",
        )
        backend = final["frozen_backend"]
        self.assertEqual(backend["requested_model"], "deepseek-v4-pro-ga-260813")
        self.assertEqual(backend["resolved_model"], "deepseek-v4-pro-ga-260813")
        self.assertEqual(backend["behavior"]["temperature"], 0.0)
        self.assertEqual(backend["memory_induction"]["temperature"], 1.0)
        self.assertEqual(backend["judge"]["temperature"], 0.0)
        self.assertEqual(backend["retrieval_top_k"], 1)
        self.assertEqual(backend["workers"], 1)
        self.assertFalse(final["next_authorized_stage"]["memory_induction_execution"])
        self.assertFalse(final["next_authorized_stage"]["p1_behavioral_execution"])

    def test_live_artifacts_do_not_serialize_api_key_field(self) -> None:
        names = (
            "asset-first-stri-reasoningbank-ark-provider-qualification-result-20260829.json",
            "asset-first-stri-reasoningbank-ark-provider-identity-resolution-result-20260829.json",
            "asset-first-stri-reasoningbank-ark-tool-continuation-causal-result-20260829.json",
            "asset-first-stri-reasoningbank-ark-provider-final-adjudication-20260829.json",
            "asset-first-stri-reasoningbank-deepseek-provider-qualification-result-20260829.json",
            "asset-first-stri-reasoningbank-deepseek-provider-qualification-adjudication-20260829.json",
            "asset-first-stri-reasoningbank-deepseek-direct-causal-result-20260829.json",
            "asset-first-stri-reasoningbank-deepseek-provider-final-adjudication-20260829.json",
        )
        def visit(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotEqual(key.lower(), "api_key")
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        for name in names:
            visit(self.load(name))


if __name__ == "__main__":
    unittest.main()
