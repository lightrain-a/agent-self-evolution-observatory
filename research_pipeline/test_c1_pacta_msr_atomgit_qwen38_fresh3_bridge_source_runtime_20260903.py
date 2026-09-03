from __future__ import annotations

import inspect
import json

from research_pipeline import c1_pacta_msr_atomgit_qwen38_fresh3_bridge_source_runtime as rt


def test_provider_condition_is_q02_plus_q03_bridge() -> None:
    assert rt.SOURCE_MAX_COMPLETION_TOKENS == 32768
    assert rt.PACTA_FIRST_DECISION_BUDGET == 2048
    assert rt.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS == 900
    assert rt.BRIDGE_SCHEMA == "c1-minisweagent-ordinary-json-text-bridge-v1"
    assert rt.PROVIDER_ID == "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_HEADLESS_FRESH3_JSON_BRIDGE_SOURCE_V1"


def test_provider_call_uses_q03_bridge_not_direct_target_prompt() -> None:
    source = inspect.getsource(rt.AtomCodeSourceProvider.call)
    assert "bridge_prompt(messages, label)" in source
    assert "extract_bridge_message(parsed[\"text\"])" in source
    assert "serialize_messages" not in source
    assert '"--no-tools"' in source
    assert '"--ephemeral"' in source
    assert '"provider_retries": 0' in source


def test_provider_fails_closed_on_native_tool_runtime_event() -> None:
    source = inspect.getsource(rt.AtomCodeSourceProvider.call)
    assert 'len(parsed["tool_events"])' in source
    assert 'parsed["tool_events"]' in source
    assert "STOP_FRESH3_BRIDGE_SOURCE_RUNTIME_INVARIANT" in source
    assert "STOP_FRESH3_BRIDGE_SOURCE_PROVIDER_NONZERO" in source
    assert "STOP_FRESH3_BRIDGE_SOURCE_JSON_PARSE" in source


def test_provider_persists_raw_response_before_bridge_parse() -> None:
    source = inspect.getsource(rt.AtomCodeSourceProvider.call)
    persist = source.index("stdout_sha = atomic_bytes")
    parse = source.index("parsed = parse_jsonl")
    assert persist < parse


def test_targeted_container_clean_never_hides_tracked_or_nonbuild_dirt() -> None:
    source = inspect.getsource(rt.Fresh3Container._normalize)
    assert 'self._git("diff", "--name-only")' in source
    assert 'self._git("diff", "--cached", "--name-only")' in source
    assert 'self._git("ls-files", "--others", "--exclude-standard")' in source
    assert 'path == "build" or path.startswith("build/")' in source
    assert 'self._git("clean", "-fd", "--", "build")' in source
    assert "-fdx" not in source
    assert "STOP_FRESH3_NON_BUILD_UNTRACKED_DIRT" in source


def test_execute_loop_preserves_minisweagent_semantics_and_exactly_once_root() -> None:
    source = inspect.getsource(rt.execute_trajectory)
    assert "exactly-once unit root exists" in source
    assert "initial_messages(task, config)" in source
    assert "parse_action(content)" in source
    assert "render_timeout_observation" in source
    assert "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT" in source
    assert "Fresh3Container(digest_ref, base_commit, unit_root)" in source


def test_validity_is_provenance_based_not_terminal_success() -> None:
    source = inspect.getsource(rt.execute_trajectory)
    line = next(line for line in source.splitlines() if "valid =" in line)
    assert "failure_layer is None" in line
    assert "provider.calls >= 1" in line
    assert "terminal" not in line


def test_no_other_model_or_raw_credential_path() -> None:
    source = inspect.getsource(rt).lower()
    assert "aa_api_key" not in source
    assert "api.aa.com.cn" not in source
    assert "deepseek" not in source
    assert "glm" not in source
