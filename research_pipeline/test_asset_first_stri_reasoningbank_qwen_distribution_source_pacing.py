from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_source_pacing as pacing


def test_rate_limit_failure_requires_nonambiguous_provider_terminal() -> None:
    receipt = {
        "execution_status": "TERMINAL_PROVIDER_OR_POLICY_FAILURE",
        "trajectory": {
            "model_call_count": 12,
            "accepted_response_count": 11,
            "failure": {
                "failure_layer": "provider",
                "ambiguous_generation_reissued": False,
                "safe_receipt": {
                    "status_code": 400,
                    "detail": {"error": {"code": "rate_limit_exceeded"}},
                },
            },
        },
        "container_cleanup_receipt": {"accepted": True},
    }
    assert pacing.rate_limit_failure(receipt) == {
        "error_code": "rate_limit_exceeded",
        "status_code": 400,
        "model_call_count": 12,
        "accepted_response_count": 11,
    }
    receipt["trajectory"]["failure"]["ambiguous_generation_reissued"] = True
    with pytest.raises(RuntimeError, match="ambiguous"):
        pacing.rate_limit_failure(receipt)


def test_require_pacing_is_transport_only_and_content_addressed(monkeypatch, tmp_path: Path) -> None:
    source_contract = tmp_path / "source-contract.json"
    source_contract.write_text(json.dumps({"frozen": True}), encoding="utf-8")
    contract = tmp_path / "pacing-contract.json"
    payload = {
        "decision": "QWEN_SOURCE_PROVIDER_PACING_REPAIR_AUTHORIZED",
        "source_contract_sha256": pacing.sha256_file(source_contract),
        "repair": {
            "active_from_source_ordinal": 8,
            "target_input_tokens_per_minute": 400_000,
            "algorithm": "transport-only-test",
            "request_payload_changed": False,
            "sampling_changed": False,
        },
    }
    contract.write_text(json.dumps(payload), encoding="utf-8")
    expected = pacing.sha256_file(contract)
    monkeypatch.setattr(pacing, "SOURCE_CONTRACT", source_contract)
    monkeypatch.setattr(pacing, "CONTRACT", contract)
    monkeypatch.setattr(pacing, "EXPECTED_CONTRACT_SHA256", expected)

    assert pacing.require_pacing(7) is None
    active = pacing.require_pacing(8)
    assert active == {
        "active_from_source_ordinal": 8,
        "target_input_tokens_per_minute": 400_000,
        "contract_sha256": expected,
        "algorithm": "transport-only-test",
    }


def test_require_pacing_fails_closed_when_active_contract_absent(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(pacing, "CONTRACT", tmp_path / "missing.json")
    with pytest.raises(RuntimeError, match="PACING_REPAIR_REQUIRED"):
        pacing.require_pacing(8)
