from __future__ import annotations

import inspect
import json

from research_pipeline import c1_pacta_msr_atomgit_qwen38_fresh4_controlled_source_runtime as rt


def test_fresh4_source_transport_constants_are_frozen():
    assert rt.PROVIDER_ID == "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_FRESH4_CONTROLLED_OUTPUT_SOURCE_V1"
    assert rt.BRIDGE_SCHEMA == "c1-controlled-output-mcp-full-minisweagent-turn-v1"
    assert rt.ALLOWED_TOOL == "mcp__c1output__submit_output"
    assert rt.SOURCE_OUTPUT_KIND == "text"
    assert rt.SOURCE_MAX_COMPLETION_TOKENS == 32768
    assert rt.PACTA_FIRST_DECISION_BUDGET == 2048
    assert rt.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS == 900


def test_fresh4_source_instruction_preserves_complete_minisweagent_turn():
    messages = [
        {"role": "system", "content": "Return THOUGHT then exactly one fenced bash command."},
        {"role": "user", "content": "Synthetic task."},
    ]
    prompt = rt.source_instruction(messages, "synthetic-step-1")
    assert rt.ALLOWED_TOOL in prompt
    assert "kind=text" in prompt
    assert "complete next assistant response" in prompt
    assert "THOUGHT" in prompt
    assert "exactly one fenced bash command" in prompt
    assert "do not inspect the host" in prompt
    assert "external frozen Docker runner" in prompt


def test_fresh4_source_provider_uses_live_mcp_not_headless_cli():
    src = inspect.getsource(rt.Fresh4ControlledSourceProvider.call)
    assert "/live/message" in src
    assert "/live/permission" in src
    assert "/live/stop" in src
    assert "mcp.json" in src
    assert "--no-tools" not in src
    assert "subprocess.run" not in src
    assert 'state.get("kind") == SOURCE_OUTPUT_KIND' in src


def test_fresh4_provider_denies_non_output_tools_and_requires_one_round():
    src = inspect.getsource(rt.Fresh4ControlledSourceProvider.call)
    assert "prohibited_tool = name" in src
    assert '"decision": "allow" if allow else "deny"' in src
    assert "len(tool_names) > 1" in src
    assert "model_round_count == 1" in src
    assert "state.get(\"call_count\") == 1" in src


def test_fresh4_bind_changes_only_provider_transport_globals():
    rt.bind()
    assert rt.base.AtomCodeSourceProvider is rt.Fresh4ControlledSourceProvider
    assert rt.base.PROVIDER_ID == rt.PROVIDER_ID
    assert rt.base.BRIDGE_SCHEMA == rt.BRIDGE_SCHEMA
    assert rt.base.SOURCE_MAX_COMPLETION_TOKENS == 32768
    assert rt.base.PACTA_FIRST_DECISION_BUDGET == 2048
    assert rt.base.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS == 900


def test_fresh4_execute_reuses_fresh3_trajectory_loop():
    src = inspect.getsource(rt.execute_trajectory)
    assert "base.execute_trajectory" in src
    assert "bind()" in src


def test_source_transport_amendment_is_pre_source_and_zero_provider():
    path = rt.Path(__file__).resolve().parents[1] / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-source-transport-amendment-20260903.json"
    contract = json.loads(path.read_text())
    assert contract["status"] == "FROZEN_PRE_SOURCE_OUTCOME"
    assert contract["source_output_channel"]["kind"] == "text"
    assert contract["source_output_channel"]["command_execution_by_bridge"] is False
    assert contract["source_output_channel"]["host_native_tools_allowed"] is False
    assert contract["source_output_channel"]["model_rounds_per_logical_output"] == 1
    assert contract["provider_calls"] == 0
    assert contract["scientific_source_calls"] == 0
