from __future__ import annotations

import inspect
import json
import tempfile
from pathlib import Path

import pytest

from research_pipeline import c1_pacta_msr_atomgit_qwen38_source_runtime as rt
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_source_20260902 as run
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q0_20260902 import write_config


def test_atomgit_source_runtime_freezes_qualified_q0_values():
    assert rt.SOURCE_MAX_COMPLETION_TOKENS == 16384
    assert rt.PACTA_FIRST_DECISION_BUDGET == 2048
    assert rt.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS == 900
    assert rt.SAMPLING_CONTROL == "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9"
    assert rt.PROVIDER_ID == "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_HEADLESS_SOURCE_V1"


def test_source_runtime_contains_no_aa_provider_or_other_model_path():
    source = inspect.getsource(rt)
    assert "AA_API_KEY" not in source
    assert "AA_BASE_URL" not in source
    assert "api.aa.com.cn" not in source
    assert "deepseek" not in source.lower()
    assert "glm" not in source.lower()


def test_atomcode_source_call_is_ephemeral_no_tools_and_zero_wrapper_retry():
    source = inspect.getsource(rt.AtomCodeSourceProvider.call)
    for flag in ("--no-tools", "--ephemeral", "--no-telemetry", "jsonl"):
        assert flag in source
    assert "timeout=ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS" in source
    assert '"provider_retries": 0' in source
    assert "for attempt" not in source
    assert "while" not in source


def test_source_provider_persists_raw_stdout_before_jsonl_parse():
    source = inspect.getsource(rt.AtomCodeSourceProvider.call)
    persist_index = source.index("stdout_sha = atomic_bytes")
    parse_index = source.index("_message_text_from_jsonl")
    assert persist_index < parse_index


def test_q0_provider_config_is_byte_reproducible():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "provider.toml"
        write_config(path, rt.SOURCE_MAX_COMPLETION_TOKENS)
        assert path.read_bytes() == run.Q0_PROVIDER_CONFIG.read_bytes()
        assert sha256_file(path) == run.Q0_PROVIDER_CONFIG_SHA


def test_verify_binds_exact_fresh_pool_runtime_and_q0_receipts():
    rows, q0 = run.verify()
    assert len(rows) == 10
    assert len({row["source_task_id"] for row in rows}) == 10
    assert len({row["task_family"] for row in rows}) == 10
    assert q0["status"] == "ATOMGIT_QWEN38_Q0_PASS_AFTER_TIMEOUT_REPAIR"
    assert q0["first_decision_budget"] == 2048
    assert q0["source_trajectory_budget"] == 16384
    assert q0["atomcode_subprocess_timeout_seconds"] == 900
    assert all(row["digest_ref"].startswith("docker.1ms.run/") for row in rows)


def test_source_schedule_is_fixed_ten_unique_units_and_never_executes_future():
    rows, _ = run.verify()
    schedule = run.schedule(rows)
    assert len(schedule) == 10
    assert [x["sequence"] for x in schedule] == list(range(1, 11))
    assert len({x["source_task_id"] for x in schedule}) == 10
    assert len({x["future_task_id"] for x in schedule}) == 10
    assert all(x["future_task_executed"] is False for x in schedule)
    assert all(x["logical_attempts"] == 1 for x in schedule)
    assert schedule == run.schedule(rows)


def test_smoke_task_is_synthetic_and_disjoint_from_all_real_source_prompts():
    pool = json.loads(run.POOL.read_text())
    source_prompts = {str(x["source_task"]) for x in pool["units"]}
    assert run.SMOKE_TASK not in source_prompts
    assert run.SMOKE_MARKER in run.SMOKE_TASK
    assert "runtime_smoke_marker.py" in run.SMOKE_TASK
    assert run.SMOKE_STEP_LIMIT == 16


def test_prepare_and_prelaunch_are_zero_provider_by_construction():
    prepare_src = inspect.getsource(run.prepare)
    prelaunch_src = inspect.getsource(run.prelaunch)
    assert "execute_trajectory(" not in prepare_src
    assert "AtomCodeSourceProvider" not in prepare_src
    assert "execute_trajectory(" not in prelaunch_src
    assert "AtomCodeSourceProvider" not in prelaunch_src
    assert '"provider_calls": 0' in prelaunch_src


def test_acquire_cannot_start_before_smoke_pass(tmp_path: Path):
    (tmp_path / "smoke-result.json").write_text(json.dumps({"status": "STOP_ATOMGIT_MSR_MULTISTEP_SMOKE"}))
    with pytest.raises(RuntimeError, match="smoke not passed"):
        run.acquire(tmp_path)


def test_execute_trajectory_has_exactly_once_root_guard(tmp_path: Path):
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(RuntimeError, match="exactly-once unit root exists"):
        rt.execute_trajectory(
            instance="synthetic",
            task="synthetic",
            digest_ref="unused",
            unit_root=existing,
            config={"agent": {}},
            provider_config_path=tmp_path / "unused.toml",
            provider_workdir=tmp_path / "workdir",
            base_commit="0" * 40,
        )


def test_source_validity_does_not_require_terminal_success():
    source = inspect.getsource(rt.execute_trajectory)
    validity_line = next(line for line in source.splitlines() if "valid =" in line)
    assert "failure_layer is None" in validity_line
    assert "provider.calls >= 1" in validity_line
    assert "terminal" not in validity_line


def test_t0_runner_has_no_downstream_scientific_stage_execution_surface():
    source = inspect.getsource(run)
    for forbidden in (
        "writer_twins_valid(",
        "binder_phase(",
        "shadow_phase(",
        "build_final_schedule(",
        "final_measurement(",
    ):
        assert forbidden not in source
    assert '"future_task_executions": 0' in source
    assert '"writer_calls": 0' in source
    assert '"binder_calls": 0' in source
    assert '"probe_calls": 0' in source
    assert '"shadow_calls": 0' in source
    assert '"final_calls": 0' in source


def test_smoke_requires_real_multistep_loop_marker_and_submit():
    source = inspect.getsource(run.smoke)
    assert "terminal_status" in source and '"Submitted"' in source
    assert "marker_file_action" in source
    assert "marker_seen" in source
    assert "2 <= int(run.get(\"provider_logical_calls\") or 0) <= SMOKE_STEP_LIMIT" in source
