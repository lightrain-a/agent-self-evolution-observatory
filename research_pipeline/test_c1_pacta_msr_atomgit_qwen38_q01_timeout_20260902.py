from __future__ import annotations

import inspect
from pathlib import Path

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q01_timeout_20260902 as q


def test_parent_hashes_are_exact_and_q0_geometry_is_frozen():
    observed = q.verify_parent()
    assert observed == q.EXPECTED
    assert q.SOURCE_BUDGET == 16384
    assert q.FIRST_DECISION_BUDGET == 2048
    fixtures = q.parent.long_fixtures()
    assert len(fixtures) == 6
    assert [(x["history_pairs"], x["line_count"]) for x in fixtures] == [
        (0, 160), (0, 320), (12, 160), (12, 320), (24, 160), (24, 320)
    ]


def test_single_variable_timeout_amendment_only():
    assert q.SOURCE_TIMEOUT_SECONDS == 900
    assert q.SAMPLING_TIMEOUT_SECONDS == 300
    src = inspect.getsource(q.source_budget)
    assert "SOURCE_BUDGET" in src
    assert "SOURCE_TIMEOUT_SECONDS" in src
    assert "32768" not in src
    assert "4096" not in src


def test_sampling_remains_diagnostic_and_uses_parent_first_action_surface():
    src = inspect.getsource(q.sampling)
    assert "parent.first_action_fixtures()[:2]" in src
    assert "FIRST_DECISION_BUDGET" in src
    assert "SAMPLING_TIMEOUT_SECONDS" in src
    assert "pass_requirement" in src


def test_runner_has_no_real_science_execution_surface():
    src = Path(q.__file__).read_text(encoding="utf-8")
    forbidden = [
        "execute_trajectory(",
        "future_task_executions = 1",
        "writer_phase(",
        "binder_phase(",
        "shadow_phase(",
        "final(",
        "docker run",
        "AA_API_KEY",
    ]
    for marker in forbidden:
        assert marker not in src
    assert 'scientific_source_tasks_used": 0' in src
    assert 'future_task_executions": 0' in src


def test_contract_exists_and_binds_timeout_ceiling():
    assert q.CONTRACT.is_file()
    text = q.CONTRACT.read_text(encoding="utf-8")
    assert '"old_invocation_timeout_seconds": 300' in text
    assert '"new_invocation_timeout_seconds": 900' in text
    assert '"source_output_budget": 16384' in text
    assert '"timeout above 900 seconds"' in text
