from __future__ import annotations

import inspect
import json
from pathlib import Path

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q04_plain_text_bridge_20260903 as q04
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q05_downstream_budget_20260903 as q05
from research_pipeline.c1_pacta_rb_qwen397 import sha256_text


def messages_sha(fx):
    return sha256_text(json.dumps(fx["messages"], ensure_ascii=False, sort_keys=True))


def test_q05_ladders_are_frozen_and_do_not_retain_failed_writer_ceiling():
    assert q05.WRITER_BUDGETS == (4096, 8192)
    assert q05.BINDER_BUDGETS == (512, 1024, 2048, 4096)
    assert 2048 not in q05.WRITER_BUDGETS


def test_q05_parent_verification_binds_q04_failure_layer():
    parent = q05.verify_parent()
    assert parent["q04_prepare_sha256"] == q05.Q04_PREPARE_SHA
    assert parent["q04_result_sha256"] == q05.Q04_RESULT_SHA
    result = json.loads(q05.Q04_RESULT.read_text())
    failed = result["rows"][-1]
    assert failed["fixture_id"] == "q04-writer-05"
    assert failed["output_truncation"] is True
    assert failed["tool_event_count"] == 0
    assert failed["usage"]["completion_tokens"] == 2048


def test_q05_reuses_exact_q04_target_messages():
    prep = json.loads(q05.Q04_PREPARE.read_text())
    expected = {row["fixture_id"]: row["messages_sha256"] for row in prep["fixtures"]}
    fixtures = q04.fixtures()
    assert len(fixtures) == 12
    for fx in fixtures:
        assert messages_sha(fx) == expected[fx["fixture_id"]]


def test_q05_preserves_q04_bridge_and_final_format_logic():
    assert q04.BRIDGE_SCHEMA == "c1-ordinary-json-plain-text-bridge-v1"
    src = inspect.getsource(q05._run_panel)
    assert "q04.call" in src
    assert "max_tokens" in src
    assert "messages" not in src or "messages" not in src.replace("fx[\"max_tokens\"]", "")


def test_q05_budget_selection_stops_after_first_pass_by_construction():
    src = inspect.getsource(q05.run)
    assert "if res[\"pass\"]:" in src
    assert "break" in src
    assert src.count("break") >= 2


def test_q05_contains_no_fresh3_scientific_task_or_source_artifact_dependency():
    src = inspect.getsource(q05)
    for forbidden in (
        "fresh3-source-20260903",
        "source_trajectory.json",
        "acquisition-journal",
        "support-audit",
        "psf__requests-6028",
        "pydata__xarray-6938",
    ):
        assert forbidden not in src


def test_q05_has_no_downstream_scientific_execution_surface():
    src = inspect.getsource(q05)
    for forbidden in ("execute_trajectory(", "writer_phase(", "binder_phase(", "shadow_phase(", "final_measurement("):
        assert forbidden not in src
    assert "writer_scientific_calls" in src
    assert "binder_scientific_calls" in src


def test_contract_declares_no_source_outcome_use():
    contract = json.loads(q05.CONTRACT.read_text())
    assert contract["fresh3_source_outcomes_used_for_design"] is False
    assert contract["scientific_source_tasks_used_as_q05_fixtures"] == 0
    assert contract["writer"]["candidate_max_tokens"] == [4096, 8192]
    assert contract["binder"]["candidate_max_tokens"] == [512, 1024, 2048, 4096]
