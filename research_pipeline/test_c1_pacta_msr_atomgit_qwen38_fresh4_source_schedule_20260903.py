from __future__ import annotations

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh4_source_schedule_20260903 as s


def test_fresh4_source_schedule_is_ten_exactly_once_units():
    result = s.prepare()
    assert result["status"] == "FRESH4_SOURCE_SCHEDULE_FROZEN_PRE_SOURCE_OUTCOME"
    assert len(result["rows"]) == 10
    assert [row["sequence"] for row in result["rows"]] == list(range(1, 11))
    assert len({row["source_task_id"] for row in result["rows"]}) == 10
    assert all(row["logical_attempts"] == 1 for row in result["rows"])
    assert all(row["replacement"] is False for row in result["rows"])
    assert all(row["future_task_executed"] is False for row in result["rows"])


def test_fresh4_source_schedule_binds_controlled_output_q03():
    result = s.prepare()
    assert result["bridge_schema"] == "c1-controlled-output-mcp-submit-output-v1"
    assert result["allowed_tool"] == "mcp__c1output__submit_output"
    assert result["action_kind"] == "bash_action"
    assert result["host_tools_allowed"] is False
    assert result["source_max_completion_tokens"] == 32768
    assert result["atomcode_subprocess_timeout_seconds"] == 900
    assert result["first_decision_budget"] == 2048


def test_fresh4_schedule_is_zero_provider_and_runtime_deferred():
    result = s.prepare()
    assert result["provider_calls"] == 0
    assert result["scientific_source_tasks_used"] == 0
    assert result["future_task_executions"] == 0
    assert all(row["runtime_binding"] == "DEFERRED_UNTIL_FRESH4_20_RUNTIME_READY" for row in result["rows"])


def test_fresh4_source_gate_forbids_replacement_top_up():
    result = s.prepare()
    assert "all 10 provenance-valid" in result["source_gate"]
    assert "retires the entire fresh4 pool" in result["source_gate"]
    assert "no replacement or top-up" in result["source_gate"]
