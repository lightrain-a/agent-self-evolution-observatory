from __future__ import annotations

import inspect
import json
from pathlib import Path

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q02_budget_20260902 as q


def test_parent_evidence_is_exact_and_failure_class_is_bound():
    assert q.verify_parent() == q.EXPECTED
    t0 = json.loads(q.T0_CLOSEOUT.read_text())
    assert t0["status"] == "HOLD_ATOMGIT_MSR_SOURCE_SUPPORT_INSUFFICIENT_REAL_TASK_OUTPUT_TRUNCATION"
    assert t0["failure_differential"]["call_10"]["completion_tokens"] == 16384


def test_budget_ladder_and_timeout_are_frozen():
    assert q.BUDGETS == (32768, 65536)
    assert q.TIMEOUT_SECONDS == 900
    assert q.FIRST_DECISION_BUDGET == 2048
    assert 16384 not in q.BUDGETS


def test_realistic_panel_is_new_synthetic_and_six_fixed_histories():
    rows = q.realistic_fixtures()
    assert len(rows) == 6
    assert [x["history_pairs"] for x in rows] == [18, 24, 30, 36, 42, 48]
    assert len({x["messages_sha256"] for x in rows}) == 6
    assert all(x["serialized_chars"] > 30000 for x in rows)
    text = json.dumps(rows, ensure_ascii=False)
    for real_id in (
        "matplotlib__matplotlib-25479",
        "sympy__sympy-13974",
        "django__django-14855",
        "scikit-learn__scikit-learn-25747",
        "pylint-dev__pylint-4551",
        "pydata__xarray-4629",
        "astropy__astropy-7606",
        "psf__requests-2317",
        "pytest-dev__pytest-7982",
        "sphinx-doc__sphinx-7590",
    ):
        assert real_id not in text


def test_invocation_is_ephemeral_no_tools_zero_retry_and_detects_truncation():
    src = inspect.getsource(q.invoke)
    for flag in ("--no-tools", "--ephemeral", "--no-telemetry", "jsonl"):
        assert flag in src
    assert "timeout=TIMEOUT_SECONDS" in src
    assert '"provider_retries": 0' in src
    assert "output_truncation" in src
    assert "MaxRounds" in src
    assert "for attempt" not in src


def test_candidate_requires_both_panels_and_strictly_below_budget():
    src = inspect.getsource(q.run_candidate)
    assert "a_pass" in src and "b_pass" in src
    assert "0 < completion < budget" in src
    assert "parse_action" in src
    assert "exact_action_match" in src
    assert "output_truncation_event" in src


def test_run_stops_at_first_passing_budget():
    src = inspect.getsource(q.run)
    assert "if result[\"pass\"]" in src
    assert "selected = budget" in src
    assert "break" in src


def test_no_scientific_or_downstream_surface():
    src = Path(q.__file__).read_text(encoding="utf-8")
    for marker in (
        "execute_trajectory(",
        "future_task_id",
        "writer_phase(",
        "binder_phase(",
        "shadow_phase(",
        "final_measurement(",
        "AA_API_KEY",
    ):
        assert marker not in src
    assert '"scientific_source_tasks_used": 0' in src
    assert '"future_task_executions": 0' in src


def test_contract_forbids_retired_pool_reuse_and_timeout_growth():
    c = json.loads(q.CONTRACT.read_text())
    assert c["candidate_budget_ladder"] == [32768, 65536]
    assert c["model_condition"]["invocation_timeout_seconds"] == 900
    joined = " ".join(c["forbidden"])
    assert "retired ten-pair" in joined
    assert "change 900s timeout" in joined
