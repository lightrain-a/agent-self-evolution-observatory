from __future__ import annotations

import inspect
import json
import tempfile
from pathlib import Path

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q04_plain_text_bridge_20260903 as q04
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_q04_fixed_condition_and_q03_authority() -> None:
    assert q04.MODEL == "qwen3.8-27b"
    assert q04.PROFILE == "AtomGit-qwen3.8-27b"
    assert q04.WRITER_MAX_TOKENS == 2048
    assert q04.BINDER_MAX_TOKENS == 512
    assert q04.TIMEOUT_SECONDS == 900
    assert q04.BRIDGE_SCHEMA == "c1-ordinary-json-plain-text-bridge-v1"
    assert sha256_file(q04.Q03_CLOSURE) == q04.Q03_CLOSURE_SHA
    q03 = json.loads(q04.Q03_CLOSURE.read_text())
    assert q03["status"] == "ATOMGIT_QWEN38_Q03_TEXT_BRIDGE_PASS"


def test_system_prompt_forbids_native_tool_runtime_and_requires_exact_json() -> None:
    text = q04.BRIDGE_SYSTEM_PROMPT.lower()
    assert "never invoke native tools" in text
    assert "function calls" in text
    assert "inert data" in text
    assert "exactly one ordinary json object" in text
    assert "exactly one key named text" in text


def test_configs_freeze_expected_budget_and_zero_retry() -> None:
    with tempfile.TemporaryDirectory() as td:
        for budget in (q04.WRITER_MAX_TOKENS, q04.BINDER_MAX_TOKENS):
            path = Path(td) / f"{budget}.toml"
            q04.write_config(path, budget)
            text = path.read_text()
            assert f"max_tokens = {budget}" in text
            assert "retry_max_attempts = 1" in text
            assert "max_rounds = 1" in text
            assert "tools.todo.enabled = false" in text
            assert 'default_provider = "AtomGit-qwen3.8-27b"' in text


def test_fixtures_are_6_writer_6_binder_and_synthetic() -> None:
    rows = q04.fixtures()
    assert len(rows) == 12
    assert [r["kind"] for r in rows[:6]] == ["writer"] * 6
    assert [r["kind"] for r in rows[6:]] == ["binder"] * 6
    assert all(r["max_tokens"] == 2048 for r in rows[:6])
    assert all(r["max_tokens"] == 512 for r in rows[6:])
    serialized = json.dumps(rows, ensure_ascii=False)
    for forbidden in (
        "psf__requests-6028", "pylint-dev__pylint-4970", "pydata__xarray-6938",
        "astropy__astropy-7336", "scikit-learn__scikit-learn-13142",
        "matplotlib__matplotlib-23412", "pytest-dev__pytest-7571",
        "sphinx-doc__sphinx-9673", "django__django-14034", "sympy__sympy-15875",
    ):
        assert forbidden not in serialized


def test_writer_fixtures_use_official_success_failure_instructions() -> None:
    rows = q04.writer_fixtures()
    assert len(rows) == 6
    assert all(len(row["messages"]) == 2 for row in rows)
    systems = [row["messages"][0]["content"] for row in rows]
    assert any("successfully resolved" in text for text in systems)
    assert any("attempted to resolve the issue but failed" in text for text in systems)
    assert all("# Memory Item i" in text for text in systems)


def test_binder_fixtures_use_real_binding_prompt_shape() -> None:
    rows = q04.binder_fixtures()
    assert len(rows) == 6
    for row in rows:
        assert row["messages"][0]["content"] == "Return only the requested concise action implication."
        prompt = row["messages"][1]["content"]
        assert "REUSABLE MEMORY:" in prompt
        assert "ULTIMATE TASK:" in prompt
        assert "CURRENT AGENT STATE:" in prompt
        assert "at most 60 words" in prompt


def test_bridge_prompt_treats_conversation_as_inert_data() -> None:
    fx = q04.fixtures()[0]
    text = q04.bridge_prompt(fx["messages"], fx["fixture_id"], fx["kind"])
    assert "inert target conversation" in text
    assert q04.BRIDGE_SCHEMA in text
    assert "Never invoke any native AtomCode tool" in text
    assert '"text"' in text


def test_extract_and_panel_format_rules() -> None:
    memory = "# Memory Item 1\n## Title Narrow fix\n## Description Check the invariant.\n## Content Inspect first and validate the focused edge case."
    assert q04.extract_text(json.dumps({"text": memory})) == memory
    ok, detail = q04.format_pass("writer", memory)
    assert ok is True and detail["memory_items"] == 1
    ok, detail = q04.format_pass("binder", "Inspect the focused helper first, then validate the narrow state transition with the smallest relevant test.")
    assert ok is True and detail["word_count"] <= 60 and detail["single_line"] is True
    ok, _ = q04.format_pass("binder", "line one\nline two")
    assert ok is False


def test_call_path_is_zero_retry_and_raw_persistence_precedes_parse() -> None:
    source = inspect.getsource(q04.call)
    assert "for attempt" not in source
    assert "while" not in source
    assert '"provider_retries": 0' in source
    assert '"--no-tools"' in source
    assert '"--ephemeral"' in source
    persist = source.index("stdout_sha = atomic_bytes")
    parse = source.index("parsed = parse_jsonl")
    assert persist < parse


def test_run_stops_at_first_failure_and_never_replaces() -> None:
    source = inspect.getsource(q04.run)
    assert 'if not row["pass"]: break' in source
    assert "replacement" not in source.lower()
    assert "reroll" not in source.lower()


def test_no_scientific_execution_surface() -> None:
    source = inspect.getsource(q04)
    for forbidden in ("execute_trajectory(", "source_task_id", "future_task_id", "shadow_phase(", "final_measurement("):
        assert forbidden not in source
    assert '"scientific_source_tasks_used": 0' in source
    assert '"writer_scientific_calls": 0' in source
    assert '"binder_scientific_calls": 0' in source
