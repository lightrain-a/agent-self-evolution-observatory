from __future__ import annotations

import inspect
import json

import pytest

from research_pipeline import c1_pacta_msr_atomgit_qwen38_fresh4_controlled_source_runtime as controlled
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh4_source_20260903 as run
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_frozen_fresh4_source_inputs_match_hashes() -> None:
    for path, expected in (
        (run.POOL, run.POOL_SHA),
        (run.Q02_CLOSURE, run.Q02_CLOSURE_SHA),
        (run.Q02_RESULT, run.Q02_RESULT_SHA),
        (run.Q03_CLOSURE, run.Q03_CLOSURE_SHA),
        (run.FROZEN_SCHEDULE, run.FROZEN_SCHEDULE_SHA),
        (run.PROBE_SPECS, run.PROBE_SPECS_SHA),
        (run.TRANSPORT_AMENDMENT, run.TRANSPORT_AMENDMENT_SHA),
        (run.EXECUTION_CONTRACT, run.EXECUTION_CONTRACT_SHA),
        (run.CONFIG, run.CONFIG_SHA),
    ):
        assert sha256_file(path) == expected


def test_fresh4_geometry_is_ten_pairs_nine_repositories() -> None:
    pool = json.loads(run.POOL.read_text())
    assert pool["candidate_count"] == 10
    assert pool["repository_count"] == 9
    assert pool["prior_exclusion_count"] == 89
    ids = [x for u in pool["units"] for x in (u["source_task_id"], u["future_task_id"])]
    assert len(ids) == 20 and len(set(ids)) == 20
    repos = [u["task_family"] for u in pool["units"]]
    assert repos.count("sphinx-doc/sphinx") == 2
    assert len(set(repos)) == 9


def test_schedule_rebind_preserves_frozen_order_and_no_replacement() -> None:
    pool = json.loads(run.POOL.read_text())
    rows = [{**u, "digest_ref": f"sha256:{i:064x}"} for i, u in enumerate(pool["units"], 1)]
    schedule = run.schedule(rows)
    frozen = json.loads(run.FROZEN_SCHEDULE.read_text())["rows"]
    assert [x["source_task_id"] for x in schedule] == [x["source_task_id"] for x in frozen]
    assert [x["sequence"] for x in schedule] == list(range(1, 11))
    assert all(x["replacement"] is False for x in schedule)
    assert all(x["future_task_executed"] is False for x in schedule)


def test_controlled_output_transport_is_the_only_source_provider() -> None:
    assert controlled.PROVIDER_ID == "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_FRESH4_CONTROLLED_OUTPUT_SOURCE_V1"
    assert controlled.ALLOWED_TOOL == "mcp__c1output__submit_output"
    assert controlled.SOURCE_OUTPUT_KIND == "text"
    assert controlled.SOURCE_MAX_COMPLETION_TOKENS == 32768
    assert controlled.PACTA_FIRST_DECISION_BUDGET == 2048
    assert controlled.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS == 900
    src = inspect.getsource(controlled.source_instruction)
    assert "Call ONLY" in src
    assert "do not inspect the host" in src


def test_invalid_runtime_sha_fails_before_source_inputs() -> None:
    with pytest.raises(RuntimeError, match="RUNTIME_SHA_FORMAT"):
        run.verify("bad")


def test_prelaunch_has_no_provider_execution() -> None:
    src = inspect.getsource(run.prelaunch)
    assert "execute_trajectory(" not in src
    assert "Fresh3Container" in src
    assert '"provider_calls": 0' in src


def test_smoke_is_required_before_acquire() -> None:
    acquire = inspect.getsource(run.acquire)
    assert "smoke not passed" in acquire
    assert "FRESH4_ATOMGIT_MSR_MULTISTEP_SMOKE_PASS" in acquire


def test_acquire_is_exactly_once_hard_gate_without_topup() -> None:
    src = inspect.getsource(run.acquire)
    assert "if run.get(\"failure_layer\") is not None" in src
    assert "break" in src
    assert "len(results) == 10 and len(valid) == 10" in src
    assert '"replacement": False' in src
    assert '"top_up": False' in src
    assert "FRESH4_ATOMGIT_MSR_SOURCE_POOL_10_QUALIFIED" in src
    assert "HOLD_FRESH4_ATOMGIT_MSR_SOURCE_POOL_RETIRED_OR_INCOMPLETE" in src


def test_source_runner_exposes_no_downstream_method_stages() -> None:
    src = inspect.getsource(run)
    for forbidden in ("writer_phase(", "binder_phase(", "shadow_phase(", "final_measurement("):
        assert forbidden not in src
    assert '"future_task_executions": 0' in src
