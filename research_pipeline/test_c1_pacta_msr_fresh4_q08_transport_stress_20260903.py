from __future__ import annotations

import inspect
import json

import pytest

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q03_output_mcp_20260903 as q03
from research_pipeline import run_c1_pacta_msr_fresh4_q08_transport_stress_20260903 as run
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_q08_stress_inputs_are_content_addressed() -> None:
    observed = run.verify_inputs()
    assert observed == run.EXPECTED


def test_q08_stress_is_eight_turns_and_exceeds_fresh3_six_call_failure() -> None:
    assert run.LOGICAL_OUTPUTS == 8
    assert run.NONFINAL_OUTPUTS == 7
    assert run.LIVE_TIMEOUT_SECONDS == 900
    assert run.LOGICAL_OUTPUTS > 6


def test_q08_stress_uses_same_controlled_output_envelope() -> None:
    assert q03.MODEL_PROFILE == "AtomGit-qwen3.8-27b"
    assert q03.MODEL_ID == "qwen3.8-27b"
    assert q03.MAX_OUTPUT_TOKENS == 32768
    assert q03.ALLOWED_TOOL == "mcp__c1output__submit_output"
    source = inspect.getsource(run.run_stress)
    assert "q03.run_live_fixture" in source
    assert '"kind": "text"' in source
    assert "q03.LIVE_TIMEOUT_SECONDS = LIVE_TIMEOUT_SECONDS" in source


def test_blueprint_contains_no_fresh4_scientific_task_text() -> None:
    bp = run.blueprint()
    pool = json.loads(run.FRESH4_POOL.read_text())
    task_texts = {u["source_task"] for u in pool["units"]} | {u["future_task"] for u in pool["units"]}
    serialized = json.dumps(bp, sort_keys=True)
    assert all(text not in serialized for text in task_texts)
    assert bp["scientific_source_tasks_used"] == 0


def test_nonfinal_requires_thought_and_one_fenced_bash() -> None:
    source = inspect.getsource(run.run_stress)
    assert '"THOUGHT:" in content' in source
    assert "parse_action(content)" in source


def test_final_requires_exact_ordinary_json_finish_object() -> None:
    assert run.FINAL_OBJECT == {"decision": "finish", "message": "FRESH4_TRANSPORT_FINAL_OK"}
    source = inspect.getsource(run.run_stress)
    assert "json.loads(content.strip())" in source
    assert 'set(parsed) == {"decision", "message"}' in source
    assert "parsed == FINAL_OBJECT" in source


def test_source_root_existing_blocks_prepare_and_run(tmp_path, monkeypatch) -> None:
    fake_source = tmp_path / "source"
    fake_source.mkdir()
    monkeypatch.setattr(run, "SOURCE_ROOT", fake_source)
    with pytest.raises(RuntimeError, match="SOURCE_ALREADY_STARTED"):
        run.prepare(tmp_path / "stress")


def test_no_retry_or_scientific_execution_surface() -> None:
    source = inspect.getsource(run)
    assert "for attempt" not in source
    assert "execute_trajectory(" not in source
    assert "docker" not in source.lower()
    assert '"scientific_source_tasks_used": 0' in source
    assert "writer_phase(" not in source
    assert "shadow_phase(" not in source
