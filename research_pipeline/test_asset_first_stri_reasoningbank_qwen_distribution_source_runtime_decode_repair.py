from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_source as source


def test_invalid_attempt_registry_zero_scientific_attempt_is_valid(monkeypatch, tmp_path: Path) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({
        "decision": "QWEN_SOURCE_INVALID_ATTEMPT_REGISTRY_ACTIVE",
        "invalid_attempts": [{
            "ordinal": 9,
            "instance_id": "sympy__sympy-13031",
            "scientific_attempt_count_consumed": 0,
            "authorized_replay_ordinal": 9,
            "archive_path": "generated/invalid.json",
            "invalid_attempt_receipt_sha256": "a" * 64,
        }],
    }), encoding="utf-8")
    monkeypatch.setattr(source, "INVALID_ATTEMPT_REGISTRY", registry)
    rows = source.invalid_attempt_records()
    assert len(rows) == 1
    assert rows[0]["scientific_attempt_count_consumed"] == 0


def test_invalid_attempt_registry_rejects_consumed_scientific_attempt(monkeypatch, tmp_path: Path) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({
        "decision": "QWEN_SOURCE_INVALID_ATTEMPT_REGISTRY_ACTIVE",
        "invalid_attempts": [{"scientific_attempt_count_consumed": 1}],
    }), encoding="utf-8")
    monkeypatch.setattr(source, "INVALID_ATTEMPT_REGISTRY", registry)
    with pytest.raises(RuntimeError, match="consumed a scientific attempt"):
        source.invalid_attempt_records()


def test_same_source_replay_requires_byte_exact_archive_and_repair_gate(monkeypatch, tmp_path: Path) -> None:
    generated = tmp_path / "generated"
    generated.mkdir()
    archive = generated / "invalid.json"
    archive.write_text("invalid-attempt\n", encoding="utf-8")
    archive_sha = source.sha256_file(archive)
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({
        "decision": "QWEN_SOURCE_INVALID_ATTEMPT_REGISTRY_ACTIVE",
        "invalid_attempts": [{
            "ordinal": 9,
            "instance_id": "sympy__sympy-13031",
            "scientific_attempt_count_consumed": 0,
            "authorized_replay_ordinal": 9,
            "archive_path": "generated/invalid.json",
            "invalid_attempt_receipt_sha256": archive_sha,
        }],
    }), encoding="utf-8")
    result_path = tmp_path / "repair-result.json"
    result_path.write_text(json.dumps({
        "decision": "QWEN_SOURCE_RUNTIME_INVALID_ATTEMPT_ARCHIVED_REPLAY_GATE_OPEN",
        "authorized_replay_ordinal": 9,
        "invalid_attempt_receipt_sha256": archive_sha,
        "scientific_attempt_count_consumed": 0,
    }), encoding="utf-8")
    receipt_dir = tmp_path / "source"
    receipt_dir.mkdir()
    monkeypatch.setattr(source, "ROOT", tmp_path)
    monkeypatch.setattr(source, "INVALID_ATTEMPT_REGISTRY", registry)
    monkeypatch.setattr(source, "RUNTIME_REPAIR_RESULT", result_path)
    monkeypatch.setattr(source, "RECEIPT_DIR", receipt_dir)
    result = source.require_invalid_replay_gate(9)
    assert result["authorized_replay_ordinal"] == 9
    assert source.require_invalid_replay_gate(10) is None
