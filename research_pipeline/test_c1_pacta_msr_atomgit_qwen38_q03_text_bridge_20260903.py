from __future__ import annotations

import inspect
import json
import tempfile
from pathlib import Path

import pytest
import yaml

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q03_text_bridge_20260903 as q03
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime_v7 import parse_action


def test_q03_constants_freeze_exact_provider_condition() -> None:
    assert q03.PROFILE == "AtomGit-qwen3.8-27b"
    assert q03.MODEL == "qwen3.8-27b"
    assert q03.MAX_TOKENS == 32768
    assert q03.TIMEOUT_SECONDS == 900
    assert q03.BRIDGE_SCHEMA == "c1-minisweagent-ordinary-json-text-bridge-v1"
    assert q03.ATOMCODE_SOURCE_COMMIT == "52ca5e6cbe8a295ce6c016b8a79d21ac1444f6b1"


def test_bridge_system_prompt_explicitly_forbids_native_tool_runtime() -> None:
    text = q03.BRIDGE_SYSTEM_PROMPT.lower()
    assert "never invoke native tools" in text
    assert "function calls" in text
    assert "inert data" in text
    assert "exactly one ordinary json object" in text
    assert "assistant_message" in text


def test_experiment_config_disables_agent_tools_and_retries() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "config.toml"
        q03.write_config(path)
        text = path.read_text()
    assert 'default_provider = "AtomGit-qwen3.8-27b"' in text
    assert 'model = "qwen3.8-27b"' in text
    assert "max_tokens = 32768" in text
    assert "retry_max_attempts = 1" in text
    assert "max_rounds = 1" in text
    assert "tools.todo.enabled = false" in text
    assert q03.BRIDGE_SYSTEM_PROMPT in json.loads(text.split("system_prompt = ", 1)[1].splitlines()[0])


def test_fixture_geometry_is_twelve_and_synthetic() -> None:
    rows = q03.fixtures()
    assert len(rows) == 12
    assert [r["panel"] for r in rows[:6]] == ["A"] * 6
    assert [r["panel"] for r in rows[6:]] == ["B"] * 6
    assert [r["history_pairs"] for r in rows[6:]] == [6, 12, 18, 24, 30, 36]
    serialized = json.dumps(rows, ensure_ascii=False)
    for forbidden in (
        "pydata__xarray-3677",
        "matplotlib__matplotlib-20488",
        "sympy__sympy-16450",
        "scikit-learn__scikit-learn-25931",
        "psf__requests-5414",
        "sphinx-doc__sphinx-11445",
        "pytest-dev__pytest-7490",
        "astropy__astropy-14995",
        "django__django-15503",
        "pylint-dev__pylint-6903",
        "Confusing (broken?) colormap name handling",
    ):
        assert forbidden not in serialized


def test_target_messages_use_official_minisweagent_templates() -> None:
    config = yaml.safe_load(q03.CONFIG.read_text())
    task = "Synthetic repository task only. Inspect a synthetic helper."
    messages = q03.target_initial_messages(task, config)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "exactly ONE bash code block" in messages[0]["content"]
    assert "Task Instructions" in messages[1]["content"]


def test_history_messages_are_valid_target_agent_transcript() -> None:
    config = yaml.safe_load(q03.CONFIG.read_text())
    messages = q03.history_fixture(config, 6, "synthetic")
    assert len(messages) == 14
    for index in range(2, len(messages), 2):
        assert messages[index]["role"] == "assistant"
        parse_action(messages[index]["content"])
        assert messages[index + 1]["role"] == "user"
        assert "SYNTHETIC_OBSERVATION" in messages[index + 1]["content"]


def test_bridge_prompt_treats_target_conversation_as_data() -> None:
    fx = q03.fixtures()[0]
    prompt = q03.bridge_prompt(fx["messages"], fx["fixture_id"])
    assert "inert target conversation" in prompt
    assert q03.BRIDGE_SCHEMA in prompt
    assert "Never invoke any native AtomCode tool" in prompt
    assert '"assistant_message"' in prompt


def test_jsonl_parser_detects_native_tool_runtime_events_and_truncation() -> None:
    stdout = "\n".join(
        [
            json.dumps({"type": "run.started", "model": "qwen3.8-27b"}),
            json.dumps({"type": "message.delta", "text": "{\"assistant_message\":\"x\"}"}),
            json.dumps({"type": "tool.completed", "name": "list_directory"}),
            json.dumps({"type": "retry", "kind": "output_truncation"}),
            json.dumps({"type": "usage", "prompt_tokens": 1, "completion_tokens": 2}),
        ]
    )
    parsed = q03.parse_jsonl(stdout)
    assert parsed["started"]["model"] == "qwen3.8-27b"
    assert len(parsed["tool_events"]) == 1
    assert parsed["output_truncation"] is True
    assert len(parsed["usage_rows"]) == 1


def test_extract_bridge_message_requires_exact_single_key_and_minisweagent_action() -> None:
    message = "THOUGHT: inspect first.\n\n```bash\ngrep -n synthetic src/module.py\n```"
    raw = json.dumps({"assistant_message": message})
    assert q03.extract_bridge_message(raw) == message
    with pytest.raises(ValueError):
        q03.extract_bridge_message(json.dumps({"assistant_message": message, "extra": 1}))
    with pytest.raises(ValueError):
        q03.extract_bridge_message(json.dumps({"assistant_message": "no thought\n```bash\nls\n```"}))


def test_call_path_has_zero_retry_and_raw_persistence_before_parse() -> None:
    source = inspect.getsource(q03.call_fixture)
    assert "for attempt" not in source
    assert "while" not in source
    assert '"provider_retries": 0' in source
    assert '"--no-tools"' in source
    assert '"--ephemeral"' in source
    assert '"--no-telemetry"' in source
    persist_index = source.index("stdout_sha = atomic_bytes")
    parse_index = source.index("parsed = parse_jsonl")
    assert persist_index < parse_index


def test_run_stops_on_first_failed_fixture_no_replacement() -> None:
    source = inspect.getsource(q03.run_panel)
    assert "if not row[\"pass\"]" in source
    assert "break" in source
    assert "replacement" not in source.lower()
    assert "reroll" not in source.lower()


def test_q03_has_no_scientific_or_downstream_execution_surface() -> None:
    source = inspect.getsource(q03)
    for forbidden in (
        "execute_trajectory(",
        "writer_twins_valid(",
        "binder_phase(",
        "shadow_phase(",
        "final_measurement(",
    ):
        assert forbidden not in source
    assert '"scientific_source_tasks_used": 0' in source
    assert '"fresh3_created": False' in source
