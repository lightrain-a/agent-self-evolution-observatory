from __future__ import annotations

import inspect
import json
import tempfile
from pathlib import Path

import pytest

from research_pipeline import c1_pacta_msr_atomgit_qwen38_fresh2_source_runtime as rt
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh2_source_20260903 as run
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q0_20260902 import write_config


def test_fresh2_provider_constants_match_q02() -> None:
    assert rt.SOURCE_MAX_COMPLETION_TOKENS == 32768
    assert rt.PACTA_FIRST_DECISION_BUDGET == 2048
    assert rt.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS == 900
    assert rt.SAMPLING_CONTROL == "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9"
    assert rt.PROVIDER_ID == "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_HEADLESS_FRESH2_SOURCE_V1"


def test_provider_contains_no_aa_or_rescue_model_path() -> None:
    source = inspect.getsource(rt)
    assert "AA_API_KEY" not in source
    assert "AA_BASE_URL" not in source
    assert "api.aa.com.cn" not in source
    assert "deepseek" not in source.lower()
    assert "glm" not in source.lower()


def test_provider_is_ephemeral_no_tools_zero_retry() -> None:
    source = inspect.getsource(rt.AtomCodeSourceProvider.call)
    for flag in ("--no-tools", "--ephemeral", "--no-telemetry", "jsonl"):
        assert flag in source
    assert "timeout=ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS" in source
    assert '"provider_retries": 0' in source
    assert "for attempt" not in source


def test_nonzero_jsonl_audit_records_consumed_truncation() -> None:
    stdout = "\n".join(
        [
            json.dumps({"type": "run.started", "model": "qwen3.8-27b"}),
            json.dumps({"type": "reasoning.delta", "text": "reasoning"}),
            json.dumps({"type": "usage", "prompt_tokens": 100, "completion_tokens": 32768}),
            json.dumps({"type": "retry", "kind": "output_truncation", "attempt": 1}),
            json.dumps({"type": "error", "message": "max rounds (1) reached"}),
        ]
    )
    row = rt._nonzero_jsonl_diagnostics(stdout)
    assert row["started_model"] == "qwen3.8-27b"
    assert row["model_content_observed"] is True
    assert row["output_truncation"] is True
    assert row["usage"]["completion_tokens"] == 32768
    assert row["error_messages"] == ["max rounds (1) reached"]


def test_provider_persists_raw_stdout_before_parse() -> None:
    source = inspect.getsource(rt.AtomCodeSourceProvider.call)
    persist_index = source.index("stdout_sha = atomic_bytes")
    parse_index = source.index("_message_text_from_jsonl")
    assert persist_index < parse_index


def test_q02_provider_config_is_byte_reproducible() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "provider.toml"
        write_config(path, rt.SOURCE_MAX_COMPLETION_TOKENS)
        assert path.read_bytes() == run.Q02_PROVIDER_CONFIG.read_bytes()
        assert sha256_file(path) == run.Q02_PROVIDER_CONFIG_SHA


def test_verify_binds_fresh2_runtime_q02_schedule_probe_and_contract() -> None:
    rows, q02 = run.verify()
    assert len(rows) == 10
    assert len({row["source_task_id"] for row in rows}) == 10
    assert len({row["task_family"] for row in rows}) == 10
    assert q02["status"] == "ATOMGIT_QWEN38_Q02_SOURCE_BUDGET_PASS"
    assert q02["selected_source_budget"] == 32768
    assert q02["first_decision_budget"] == 2048
    assert q02["invocation_timeout_seconds"] == 900
    runtime = json.loads(run.RUNTIME.read_text())
    assert runtime["status"] == "FRESH2_MSR_20_RUNTIME_READY_AFTER_TARGETED_BUILD_CLEAN"
    assert runtime["source_qualified"] == 10 and runtime["future_qualified"] == 10
    assert sha256_file(run.FROZEN_SCHEDULE) == run.FROZEN_SCHEDULE_SHA
    assert sha256_file(run.PROBE_SPECS) == run.PROBE_SPECS_SHA
    assert sha256_file(run.EXECUTION_CONTRACT) == run.EXECUTION_CONTRACT_SHA


def test_schedule_is_exactly_the_frozen_order_with_runtime_binding() -> None:
    rows, _ = run.verify()
    schedule = run.schedule(rows)
    expected = [row["source_task_id"] for row in json.loads(run.FROZEN_SCHEDULE.read_text())["rows"]]
    assert [row["source_task_id"] for row in schedule] == expected
    assert [row["sequence"] for row in schedule] == list(range(1, 11))
    assert all(row["logical_attempts"] == 1 for row in schedule)
    assert all(row["future_task_executed"] is False for row in schedule)
    assert all(row["replacement"] is False for row in schedule)
    assert all(row["digest_ref"].startswith("docker.1ms.run/") for row in schedule)


def test_smoke_is_synthetic_and_disjoint_from_real_source_prompts() -> None:
    pool = json.loads(run.POOL.read_text())
    source_prompts = {str(unit["source_task"]) for unit in pool["units"]}
    assert run.SMOKE_TASK not in source_prompts
    assert run.SMOKE_MARKER in run.SMOKE_TASK
    assert "runtime_smoke_marker.py" in run.SMOKE_TASK
    assert run.SMOKE_STEP_LIMIT == 16


def test_prepare_and_prelaunch_are_zero_provider_by_construction() -> None:
    prepare_src = inspect.getsource(run.prepare)
    prelaunch_src = inspect.getsource(run.prelaunch)
    assert "execute_trajectory(" not in prepare_src
    assert "AtomCodeSourceProvider" not in prepare_src
    assert "execute_trajectory(" not in prelaunch_src
    assert "AtomCodeSourceProvider" not in prelaunch_src
    assert '"provider_calls": 0' in prelaunch_src


def test_acquire_cannot_start_before_smoke_pass(tmp_path: Path) -> None:
    (tmp_path / "smoke-result.json").write_text(json.dumps({"status": "STOP_FRESH2_ATOMGIT_MSR_MULTISTEP_SMOKE"}))
    with pytest.raises(RuntimeError, match="smoke not passed"):
        run.acquire(tmp_path)


def test_execute_trajectory_is_exactly_once(tmp_path: Path) -> None:
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


def test_source_validity_is_provenance_not_terminal_success() -> None:
    source = inspect.getsource(rt.execute_trajectory)
    validity_line = next(line for line in source.splitlines() if "valid =" in line)
    assert "failure_layer is None" in validity_line
    assert "provider.calls >= 1" in validity_line
    assert "terminal" not in validity_line


def test_source_gate_has_no_partial_support_or_replacement() -> None:
    source = inspect.getsource(run.acquire)
    assert "SOURCE_POOL_PARTIAL_STOP" not in source
    assert "FRESH2_ATOMGIT_MSR_SOURCE_POOL_10_QUALIFIED" in source
    assert "HOLD_FRESH2_ATOMGIT_MSR_SOURCE_POOL_RETIRED_OR_INCOMPLETE" in source
    assert '"replacement": False' in source
    assert '"top_up": False' in source


def test_t0_runner_exposes_no_downstream_scientific_stages() -> None:
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


def test_smoke_requires_multistep_marker_and_submit() -> None:
    source = inspect.getsource(run.smoke)
    assert "terminal_status" in source and '"Submitted"' in source
    assert "marker_file_action" in source
    assert "marker_seen" in source
    assert "2 <= int(run.get(\"provider_logical_calls\") or 0) <= SMOKE_STEP_LIMIT" in source
