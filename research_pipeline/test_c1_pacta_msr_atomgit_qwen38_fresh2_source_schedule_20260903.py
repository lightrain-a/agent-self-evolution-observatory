from __future__ import annotations

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh2_source_schedule_20260903 as mod
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_inputs_are_content_addressed():
    assert sha256_file(mod.POOL) == mod.POOL_SHA
    assert sha256_file(mod.SPLIT) == mod.SPLIT_SHA
    assert sha256_file(mod.PROBES) == mod.PROBES_SHA
    assert sha256_file(mod.Q02) == mod.Q02_SHA


def test_schedule_is_ten_unique_exactly_once_sources():
    out = mod.prepare()
    assert len(out["rows"]) == 10
    assert [row["sequence"] for row in out["rows"]] == list(range(1, 11))
    assert len({row["source_task_id"] for row in out["rows"]}) == 10
    assert all(row["logical_attempts"] == 1 for row in out["rows"])
    assert all(row["replacement"] is False for row in out["rows"])
    assert all(row["future_task_executed"] is False for row in out["rows"])


def test_source_parameters_are_q02_frozen_values():
    out = mod.prepare()
    assert out["source_max_completion_tokens"] == 32768
    assert out["atomcode_subprocess_timeout_seconds"] == 900
    assert out["first_decision_budget"] == 2048
    assert "no replacement" in out["source_gate"]


def test_schedule_is_outcome_blind_and_runtime_deferred():
    a = mod.prepare()
    b = mod.prepare()
    assert a["rows"] == b["rows"]
    assert a["provider_calls"] == 0
    assert a["scientific_source_tasks_used"] == 0
    assert all(row["runtime_binding"] == "DEFERRED_UNTIL_FRESH2_20_RUNTIME_READY" for row in a["rows"])
