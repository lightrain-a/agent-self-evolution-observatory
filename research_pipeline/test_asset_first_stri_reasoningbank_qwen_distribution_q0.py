"""Provider-free tests for Qwen STRI Q0 qualification."""

from __future__ import annotations

from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_q0 as q0
from research_pipeline.asset_first_stri_reasoningbank_qwen_provider import (
    QwenChatClient,
    QwenChatSettings,
)


class FakeResponse:
    status_code = 200
    text = ""

    @staticmethod
    def json() -> dict:
        return {
            "id": "response-id",
            "object": "chat.completion",
            "model": q0.MODEL,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Q0_BASE_OK"},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 9, "completion_tokens": 3, "total_tokens": 12},
        }


class FakeSession:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self.body: dict | None = None

    def post(self, endpoint: str, *, json: dict, timeout: float) -> FakeResponse:
        self.body = json
        return FakeResponse()


def test_q0_probe_plan_is_exactly_once_and_provider_free() -> None:
    plan = q0.probe_plan()
    assert len(plan) == 10
    assert [row["ordinal"] for row in plan] == list(range(1, 11))
    assert all(row["attempt_count"] == 1 for row in plan)
    assert q0.MAX_RETRIES == 0
    assert q0.MODEL == "qwen3-coder-next"
    assert q0.RECOMMENDED_TEMPERATURE == 1.0
    assert q0.RECOMMENDED_TOP_P == 0.95
    assert q0.RECOMMENDED_TOP_K == 40


def test_q0_contract_does_not_open_benchmark_or_source_authority(tmp_path, monkeypatch) -> None:
    d0 = tmp_path / "d0.json"
    q0.write_json(d0, {
        "execution_complete": True,
        "decision": "D0_PRIMARY_FOUR_REPOSITORY_EVALUATOR_FEASIBILITY_PASS",
    })
    monkeypatch.setattr(q0, "ROOT", tmp_path)
    monkeypatch.setattr(q0, "D0_INDEX", d0)
    contract = q0.contract_payload()
    assert contract["qualification_gate"]["single_choice_n1_required"] is True
    boundary = contract["scientific_boundary"]
    assert boundary["q1_stochasticity_qualification_authorized"] is False
    assert boundary["source_generation_authorized"] is False
    assert boundary["confirmatory_execution_authorized"] is False


def test_provider_forwards_top_k_and_hashes_raw_response() -> None:
    session = FakeSession()
    client = QwenChatClient(
        QwenChatSettings(
            api_key="SECRET_SENTINEL",
            base_url="https://example.invalid/api/v1",
            model=q0.MODEL,
            timeout_seconds=1.0,
            max_retries=0,
        ),
        session=session,
    )
    result = client.create_response(
        input_items="probe",
        temperature=1.0,
        top_p=0.95,
        top_k=40,
    )
    assert session.body is not None
    assert session.body["top_k"] == 40
    assert session.body["n"] == 1
    assert session.body["stream"] is False
    assert result["raw_payload_sha256"]
    assert result["choice_count"] == 1
    assert "SECRET_SENTINEL" not in str(result)


def test_public_success_hashes_response_identity_and_excludes_secret() -> None:
    row = q0.public_success(
        "probe",
        {
            "response_id": "private-response-id",
            "status": "completed",
            "requested_model": q0.MODEL,
            "resolved_model": q0.MODEL,
            "raw_text": "OK",
            "function_calls": [],
            "usage": {"output_tokens": 1},
            "raw_payload_sha256": "a" * 64,
            "response_metadata": {"model": q0.MODEL},
            "transport_attempts": 1,
        },
        0.25,
    )
    assert row["response_id_present"] is True
    assert row["response_id_sha256"] != "private-response-id"
    assert "private-response-id" not in str(row)
    assert row["credential_material_present"] is False


def test_classification_never_equates_acceptance_with_honoring() -> None:
    success = {
        "status": "SUCCESS",
        "text": "arbitrary",
    }
    assert q0.classify(success) == "unresolved"
    assert q0.classify(success, exact_text="different") == "ignored"
    assert q0.classify(success, exact_text="arbitrary") == "honored"
    unsupported = {
        "status": "UNSUPPORTED_OR_FAILED",
        "failure": {"status_code": 400},
    }
    assert q0.classify(unsupported) == "unsupported"
