from __future__ import annotations

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh4_probe_specs_20260903 as p


def test_fresh4_probe_geometry_and_zero_provider():
    result = p.prepare()
    assert result["status"] == "FRESH4_MSR_10_PROBE_COMMANDS_FROZEN_PRE_SOURCE_OUTCOME"
    assert len(result["rows"]) == 10
    assert len({row["future_task_id"] for row in result["rows"]}) == 10
    assert result["provider_calls"] == 0
    assert result["scientific_source_tasks_used"] == 0
    assert result["future_task_executions"] == 0


def test_fresh4_probe_pool_and_salt_are_new():
    result = p.prepare()
    assert result["fresh_pool_sha256"] == "9582877385413807dea6316c25585d5714662cce17f83fa298934229dc4f0927"
    assert result["token_salt"] == "C1-PACTA-MSR-FRESH4-PROBE-TOKEN-v1"
    assert all(row["runtime_binding"] == "DEFERRED_UNTIL_FRESH4_20_RUNTIME_READY" for row in result["rows"])


def test_fresh4_probes_are_branch_memory_blind_read_only():
    result = p.prepare()
    for row in result["rows"]:
        assert row["branch_blind"] is True
        assert row["memory_blind"] is True
        assert row["read_only"] is True
        assert row["provider_calls"] == 0
        assert row["future_task_executions"] == 0
        assert row["command"].startswith("git status --short; git grep -n -I")
        assert len(row["tokens"]) == 3
