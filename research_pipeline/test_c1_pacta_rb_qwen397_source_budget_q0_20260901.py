from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from research_pipeline import run_c1_pacta_rb_qwen397_source_budget_q0_20260901 as q0


def test_source_budget_is_separate_from_pacta_first_decision_budget():
    assert q0.SOURCE_OUTPUT_BUDGET == 4096
    assert q0.FIRST_DECISION_BUDGET == 512
    assert q0.SOURCE_OUTPUT_BUDGET != q0.FIRST_DECISION_BUDGET


def test_fixture_grid_is_frozen_and_long_action_capable():
    config = yaml.safe_load(q0.CONFIG.read_text())
    rows = q0.fixtures(config)
    assert len(rows) == 12
    assert {(r["history_pairs"], r["line_count"]) for r in rows} == {
        (h, n) for h in (0, 4, 12, 24) for n in (80, 160, 320)
    }
    longest = max(rows, key=lambda r: len(r["expected_action"]))
    assert longest["line_count"] == 320
    assert len(longest["expected_action"]) > 12000
    assert "for " not in longest["expected_action"]
    assert longest["expected_action"].count("_LINE_") == 320


def test_expected_action_is_deterministic():
    a = q0.make_expected_command("fixture", 80)
    b = q0.make_expected_command("fixture", 80)
    assert a == b
    assert a.startswith("cat <<'EOF' > /tmp/fixture.txt\n")
    assert a.endswith("\nEOF")
    assert a.count("fixture_LINE_") == 80


def test_parent_q0_hashes_are_explicit():
    assert len(q0.Q0_BINDING_SHA256) == 64
    assert len(q0.Q0_QUALIFICATION_SHA256) == 64
    assert q0.Q0_BINDING_SHA256 != q0.Q0_QUALIFICATION_SHA256


def test_qualification_contains_no_scientific_source_task_ids():
    source = Path(q0.__file__).read_text()
    for task_id in (
        "pydata__xarray-4966",
        "scikit-learn__scikit-learn-14496",
        "psf__requests-1766",
        "matplotlib__matplotlib-24627",
        "sphinx-doc__sphinx-8593",
        "mwaskom__seaborn-3187",
        "sympy__sympy-15599",
        "astropy__astropy-7166",
        "django__django-13449",
        "pylint-dev__pylint-7080",
        "pytest-dev__pytest-5840",
    ):
        assert task_id not in source


def test_run_is_exactly_once_at_root_boundary(tmp_path: Path):
    root = tmp_path / "exists"
    root.mkdir()
    with pytest.raises(RuntimeError, match="no overwrite/retry"):
        q0.run(root)


def test_pass_rule_requires_exact_action_and_stop():
    source = Path(q0.__file__).read_text()
    assert 'finish_reason == "stop"' in source
    assert "action == fixture[\"expected_action\"]" in source
    assert '"provider_retries": 0' in source
    assert '"scientific_source_tasks_used": 0' in source
    assert '"v5_source_task_replayed": False' in source
