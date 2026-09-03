from __future__ import annotations

import inspect
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from research_pipeline import c1_pacta_msr_atomgit_qwen38_output_mcp as server
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q03_output_mcp_20260903 as q03


def test_q03_fixture_geometry_is_frozen_and_synthetic():
    rows = q03.fixtures()
    assert len(rows) == 12
    assert sum(r["kind"] == "bash_action" and r["exact"] for r in rows) == 4
    assert sum(r["kind"] == "bash_action" and not r["exact"] for r in rows) == 4
    assert sum(r["kind"] == "text" and r["exact"] for r in rows) == 4
    text = "\n".join(q03.instruction_for(r) for r in rows)
    for real_id in ("pydata__xarray-3677", "matplotlib__matplotlib-20488", "psf__requests-5414"):
        assert real_id not in text
    assert "SYNQ02_" in text


def test_q03_only_allows_controlled_output_tool():
    assert q03.ALLOWED_TOOL == "mcp__c1output__submit_output"
    config = q03.atomcode_config()
    agents = q03.agents_md()
    assert "list_directory" in config
    assert "Never use host" in config
    assert q03.ALLOWED_TOOL in agents
    assert "Never call list_directory" in agents


def test_q03_daemon_round_cap_and_output_budget_are_fixed():
    assert q03.DAEMON_ROUND_CAP == 2
    assert q03.MAX_OUTPUT_TOKENS == 32768
    assert q03.LIVE_TIMEOUT_SECONDS == 180
    config = q03.atomcode_config()
    assert "max_tokens = 32768" in config
    assert "max_rounds = 2" in config
    assert "retry_max_attempts = 1" in config


def test_q03_prepare_has_no_model_dispatch_surface():
    src = inspect.getsource(q03.prepare)
    assert "/live/message" not in src
    assert "run_live_fixture" not in src
    assert '"scientific_source_tasks_used": 0' in src


def test_q03_server_schema_is_output_only():
    assert server.TOOL_NAME == "submit_output"
    assert server.VALID_KINDS == {"bash_action", "text"}
    src = inspect.getsource(server)
    assert "subprocess" not in src
    assert "os.system" not in src
    assert "OUTPUT_CAPTURED" in src
    assert "TOOL_CALL_CAP_EXCEEDED" in src


def test_q03_server_captures_one_output_without_execution():
    with tempfile.TemporaryDirectory() as td:
        progress = Path(td) / "progress.json"
        proc = subprocess.Popen(
            [sys.executable, "-m", "research_pipeline.c1_pacta_msr_atomgit_qwen38_output_mcp", "--progress", str(progress)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        assert proc.stdin is not None and proc.stdout is not None
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "submit_output", "arguments": {"kind": "bash_action", "content": "ls -la"}}},
        ]
        for msg in messages:
            proc.stdin.write(json.dumps(msg) + "\n")
            proc.stdin.flush()
            if "id" in msg:
                json.loads(proc.stdout.readline())
        state = json.loads(progress.read_text())
        assert state["status"] == "OUTPUT_CAPTURED"
        assert state["call_count"] == 1
        assert state["kind"] == "bash_action"
        assert state["content"] == "ls -la"
        proc.terminate()
        proc.wait(timeout=5)


def test_q03_second_output_is_rejected():
    src = inspect.getsource(server.main)
    assert "if call_count != 1" in src
    assert "Exactly one output is allowed" in src


def test_q03_contract_forbids_fresh2_reuse():
    contract = json.loads(q03.CONTRACT.read_text())
    assert contract["fresh2_reuse"] is False
    assert contract["scientific_source_tasks_used"] == 0
    assert contract["fixtures"]["real_scientific_tasks"] == 0
    assert "reuse any fresh2 source/future task" in contract["forbidden"]
