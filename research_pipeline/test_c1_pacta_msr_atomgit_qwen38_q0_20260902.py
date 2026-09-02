from __future__ import annotations

from pathlib import Path

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q0_20260902 as q


def test_model_and_interface_are_frozen():
    assert q.PROFILE == "AtomGit-qwen3.8-27b"
    assert q.MODEL == "qwen3.8-27b"
    assert q.CONTEXT_WINDOW == 262144
    assert q.FIRST_BUDGETS == (512, 1024, 2048, 4096)
    assert q.SOURCE_BUDGETS == (4096, 16384, 32768)


def test_config_disables_agent_surfaces(tmp_path: Path):
    p = tmp_path / "c.toml"
    q.write_config(p, 512)
    s = p.read_text()
    assert 'default_provider = "AtomGit-qwen3.8-27b"' in s
    assert 'model = "qwen3.8-27b"' in s
    assert "max_tokens = 512" in s
    assert "retry_max_attempts = 1" in s
    assert "subagent.enabled = false" in s
    assert "tools.todo.enabled = false" in s
    assert "max_rounds = 1" in s
    assert "enabled = false" in s


def test_first_action_fixtures_are_non_scientific_and_parse_targeted():
    rows = q.first_action_fixtures()
    assert len(rows) == 20
    assert len({x["fixture_id"] for x in rows}) == 20
    joined = "\n".join(m["content"] for x in rows for m in x["messages"])
    assert "ATOMGIT_Q0_MARKER_01" in joined
    for forbidden in ("astropy__astropy-7606", "django__django-14855", "pylint-dev__pylint-4551"):
        assert forbidden not in joined


def test_long_fixtures_match_frozen_grid():
    rows = q.long_fixtures()
    assert len(rows) == 6
    assert {(x["history_pairs"], x["line_count"]) for x in rows} == {(h, n) for h in (0, 12, 24) for n in (160, 320)}
    assert all(x["expected"].startswith("cat <<'EOF' > /tmp/") for x in rows)


def test_source_long_command_is_deterministic():
    a = q.long_command("x", 160)
    b = q.long_command("x", 160)
    assert a == b
    assert q.sha256_text(a) == q.sha256_text(b)
    assert a.count("_LINE_") == 160


def test_q0_source_contains_no_scientific_stage_execution_surface():
    source = Path(q.__file__).read_text()
    for forbidden in ("execute_trajectory(", "SUCCESSFUL_SI", "FAILED_SI", "def shadow_phase(", "def final(", "future_task_executions +="):
        assert forbidden not in source


def test_atomcode_invocation_flags_are_hardcoded():
    source = Path(q.__file__).read_text()
    for flag in ("--no-tools", "--ephemeral", "--no-telemetry", "--output-format"):
        assert flag in source
    assert "--dangerously-skip-permissions" not in source


def test_contract_exists_and_is_pre_provider():
    assert q.CONTRACT.is_file()
    text = q.CONTRACT.read_text()
    assert '"status": "FROZEN_PRE_PROVIDER"' in text
    assert '"scientific_source_tasks_used": 0' in text
