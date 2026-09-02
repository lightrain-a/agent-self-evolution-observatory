from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_source as source
from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_source_resume as resume


def _rate_limit_terminal() -> dict:
    return {
        "execution_status": "TERMINAL_PROVIDER_OR_POLICY_FAILURE",
        "trajectory": {
            "failure": {
                "failure_layer": "provider",
                "ambiguous_generation_reissued": False,
                "safe_receipt": {
                    "detail": {"error": {"code": "rate_limit_exceeded"}},
                },
            },
        },
        "container_cleanup_receipt": {"accepted": True},
    }


def test_resume_probe_is_single_synthetic_nonbenchmark_request() -> None:
    request = resume.probe_request()
    assert request == {
        "model": "qwen3-coder-next",
        "messages": [
            {"role": "system", "content": "Synthetic provider liveness check only. Follow the user exactly."},
            {"role": "user", "content": "Return exactly SOURCE_RESUME_OK and nothing else."},
        ],
        "temperature": 0.0,
        "top_p": 1.0,
        "max_completion_tokens": 16,
        "n": 1,
        "stream": False,
    }


def test_rate_limit_hold_freezes_only_next_untouched_source_gate(monkeypatch, tmp_path: Path) -> None:
    source_contract = tmp_path / "source-contract.json"
    source_index = tmp_path / "source-index.json"
    source_dir = tmp_path / "source-trajectories"
    source_dir.mkdir()
    plan = [
        {"ordinal": ordinal, "instance_id": f"org__task-{ordinal:02d}"}
        for ordinal in range(1, 33)
    ]
    source_contract.write_text(json.dumps({"source_plan": plan}), encoding="utf-8")
    trigger = _rate_limit_terminal()
    trigger.update({"instance_id": "org__task-03"})
    trigger_path = source_dir / "03-org-task-03.json"
    trigger_path.write_text(json.dumps(trigger), encoding="utf-8")
    source_index.write_text(json.dumps({
        "execution_complete": False,
        "completed_count": 3,
        "inflight": None,
        "journal": [{
            "ordinal": 3,
            "receipt_sha256": resume.sha256_file(trigger_path),
        }],
    }), encoding="utf-8")
    monkeypatch.setattr(resume, "ROOT", tmp_path)
    monkeypatch.setattr(resume, "SOURCE_CONTRACT", source_contract)
    monkeypatch.setattr(resume, "SOURCE_INDEX", source_index)
    monkeypatch.setattr(resume, "SOURCE_DIR", source_dir)

    payload = resume.contract_payload(3)
    assert payload["trigger_ordinal"] == 3
    assert payload["trigger_failure_code"] == "rate_limit_exceeded"
    assert payload["next_untouched_ordinal"] == 4
    assert payload["remaining_untouched_ordinals"] == list(range(4, 33))
    policy = payload["execution_policy"]
    assert policy["synthetic_nonbenchmark_probe_count"] == 1
    assert policy["attempt_count"] == 1
    assert policy["automatic_retry"] is False
    assert policy["source_trigger_retry"] is False
    assert policy["source_task_replacement"] is False
    boundary = payload["scientific_boundary"]
    assert boundary["trigger_source_receipt_permanently_retained"] is True
    assert boundary["trigger_source_reexecution_authorized"] is False
    assert boundary["next_untouched_source_execution_authorized"] is False
    assert boundary["remaining_source_outcomes_observed"] is False


def test_source_runner_requires_resume_gate_after_rate_limit(monkeypatch) -> None:
    calls: list[tuple[int, Path]] = []
    monkeypatch.setattr(
        source,
        "require_resume_gate",
        lambda ordinal, path: calls.append((ordinal, path)) or {"decision": resume.QUALIFIED_DECISION},
    )
    contract = {"source_plan": [
        {"ordinal": 1, "instance_id": "org__task-1"},
        {"ordinal": 2, "instance_id": "org__task-2"},
        {"ordinal": 3, "instance_id": "org__task-3"},
        {"ordinal": 4, "instance_id": "org__task-4"},
    ]}
    result = source.require_resume_if_last_terminal(contract, {3: _rate_limit_terminal()})
    assert result == {"decision": resume.QUALIFIED_DECISION}
    assert calls == [(3, source.receipt_path(contract["source_plan"][2]))]


def test_source_runner_never_requires_resume_after_completed_prefix(monkeypatch) -> None:
    monkeypatch.setattr(
        source,
        "require_resume_gate",
        lambda *_args, **_kwargs: pytest.fail("resume gate must not run for a completed prefix"),
    )
    contract = {"source_plan": [{"ordinal": 1, "instance_id": "org__task-1"}]}
    assert source.require_resume_if_last_terminal(
        contract, {1: {"execution_status": "COMPLETED"}},
    ) is None


def test_non_rate_limit_terminal_remains_fail_closed(monkeypatch) -> None:
    receipt = _rate_limit_terminal()
    receipt["trajectory"]["failure"]["safe_receipt"]["detail"]["error"]["code"] = "other"
    monkeypatch.setattr(
        source,
        "require_resume_gate",
        lambda *_args, **_kwargs: pytest.fail("non-rate-limit failures must not use this repair"),
    )
    contract = {"source_plan": [{"ordinal": 1, "instance_id": "org__task-1"}]}
    with pytest.raises(RuntimeError, match="NOT_RATE_LIMIT_RESUMABLE"):
        source.require_resume_if_last_terminal(contract, {1: receipt})


def test_require_resume_gate_fails_closed_without_result(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(resume, "result_path", lambda _ordinal: tmp_path / "missing.json")
    with pytest.raises(RuntimeError, match="QUALIFICATION_REQUIRED"):
        resume.require_resume_gate(3, tmp_path / "trigger.json")
