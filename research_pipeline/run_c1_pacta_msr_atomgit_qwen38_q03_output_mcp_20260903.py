#!/usr/bin/env python3
"""Q0.3 controlled-output MCP qualification for AtomGit/AtomCode Qwen3.8.

This is non-scientific provider-interface qualification only.  It exposes one
MCP output-capture tool and denies every other AtomCode/native tool.  No real
PACTA source/future task is reachable from this runner.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_codingplan_prereg import (
    BASE_URL,
    CONTEXT_WINDOW,
    MODEL_ID,
    MODEL_PROFILE,
)
from research_pipeline.agent_constraint_externality_codingplan_qwen38_capability import (
    ATOMCODE_BIN,
    codingplan_usage,
    http_json,
    terminate_process,
    wait_file,
)
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file, sha256_text
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q0_20260902 import serialize_messages
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q02_budget_20260902 import realistic_fixtures

ROOT = Path(__file__).resolve().parents[1]
SERVER_MODULE = "research_pipeline.c1_pacta_msr_atomgit_qwen38_output_mcp"
SERVER_SOURCE = ROOT / "research_pipeline/c1_pacta_msr_atomgit_qwen38_output_mcp.py"
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q03-output-mcp-contract-20260903.json"
DEFAULT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q03-output-mcp-20260903-v1")
ALLOWED_TOOL = "mcp__c1output__submit_output"
MAX_OUTPUT_TOKENS = 32768
DAEMON_ROUND_CAP = 2
LIVE_TIMEOUT_SECONDS = 180
FIXTURE_COUNT = 12


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", buffering=1) as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def atomcode_config() -> str:
    system_prompt = (
        "You are a controlled model-output policy inside an offline research qualification. "
        "The only permitted tool is the c1output MCP submit_output tool. Never use host coding, shell, "
        "filesystem, list_directory, web, agent, AtomGit, memory, skill, or any other tool. "
        "Do not execute commands. Call submit_output exactly once with the requested kind and content."
    )
    return f'''default_provider = "{MODEL_PROFILE}"
default_model = "{MODEL_PROFILE}"
auto_update = false
auto_commit = false
[provider_accounts.AtomGit]
provider = "openai"
base_url = "{BASE_URL}"
[models."{MODEL_PROFILE}"]
account = "AtomGit"
model = "{MODEL_ID}"
context_window = {CONTEXT_WINDOW}
max_tokens = {MAX_OUTPUT_TOKENS}
retry_max_attempts = 1
system_prompt = {json.dumps(system_prompt)}
[loop_config]
max_rounds = {DAEMON_ROUND_CAP}
[coding]
max_rounds = {DAEMON_ROUND_CAP}
shell_guard_policy = "prompt"
[tools.todo]
enabled = false
[lsp]
enabled = false
[subagent]
enabled = false
[ui]
ai_session_naming = false
[network.proxy]
mode = "follow_system"
'''


def agents_md() -> str:
    return (
        "# Controlled output qualification\n"
        "This workspace contains no task environment. Never inspect the host. The ONLY allowed tool is "
        "`mcp__c1output__submit_output`. Never call list_directory, shell, filesystem, web, coding, agent, "
        "AtomGit, memory, skill, or any other tool. Submit exactly one output and stop.\n"
    )


def mcp_config(progress: Path) -> dict[str, Any]:
    return {
        "mcpServers": {
            "c1output": {
                "command": str(Path(sys.executable).resolve()),
                "args": ["-m", SERVER_MODULE, "--progress", str(progress.resolve())],
                "env": {"PYTHONPATH": str(ROOT)},
                "timeout_ms": 30000,
                "trust": True,
            }
        }
    }


def start_daemon(atom_home: Path, workdir: Path, log_path: Path) -> tuple[subprocess.Popen[Any], str, str]:
    port = free_port()
    env = os.environ.copy()
    env.update(
        {
            "ATOMCODE_HOME": str(atom_home.resolve()),
            "ATOMCODE_SUBAGENT": "0",
            "ATOMCODE_AI_SESSION_NAMING": "0",
            "ATOMCODE_TURN_MAX_ROUNDS": str(DAEMON_ROUND_CAP),
            "ATOMCODE_LOOP_MAX_ROUNDS": str(DAEMON_ROUND_CAP),
        }
    )
    log = log_path.open("wb")
    process = subprocess.Popen(
        [str(ATOMCODE_BIN), "daemon", "--port", str(port), "--idle-timeout", "0", "--no-telemetry"],
        cwd=workdir,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    log.close()
    try:
        token_path = atom_home / f"daemon-{port}.json"
        wait_file(token_path, 20)
        token = str(json.loads(token_path.read_text(encoding="utf-8"))["token"])
        base = f"http://127.0.0.1:{port}"
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                if http_json(base, token, "/health", timeout=3).get("status") == "ok":
                    return process, base, token
            except Exception:
                pass
            time.sleep(0.1)
        raise RuntimeError("Q03 daemon health timeout")
    except Exception:
        terminate_process(process)
        raise


def action_exact_fixtures() -> list[dict[str, Any]]:
    rows = []
    for i in range(1, 5):
        expected = f'grep -rn "Q03_ACTION_MARKER_{i:02d}" synthetic/ | head -n {i + 1}'
        messages = [
            {"role": "system", "content": "Synthetic MiniSWEAgent transport fixture. Do not execute anything."},
            {"role": "user", "content": f"The exact next shell action is: {expected}"},
        ]
        rows.append({"fixture_id": f"action-exact-{i}", "kind": "bash_action", "messages": messages, "expected": expected, "exact": True})
    return rows


def action_realistic_fixtures() -> list[dict[str, Any]]:
    source = realistic_fixtures()
    picks = [source[0], source[2], source[4], source[5]]
    return [
        {
            "fixture_id": "action-" + row["fixture_id"],
            "kind": "bash_action",
            "messages": row["messages"],
            "expected": None,
            "exact": False,
            "history_pairs": row["history_pairs"],
            "serialized_chars": row["serialized_chars"],
        }
        for row in picks
    ]


def text_exact_fixtures() -> list[dict[str, Any]]:
    rows = []
    for i in range(1, 5):
        expected = f"Q03_TEXT_OK_{i}"
        messages = [
            {"role": "system", "content": "Synthetic text-output transport fixture. No tools may execute."},
            {"role": "user", "content": f"Return exactly this text output: {expected}"},
        ]
        rows.append({"fixture_id": f"text-exact-{i}", "kind": "text", "messages": messages, "expected": expected, "exact": True})
    return rows


def fixtures() -> list[dict[str, Any]]:
    rows = action_exact_fixtures() + action_realistic_fixtures() + text_exact_fixtures()
    if len(rows) != FIXTURE_COUNT or len({row["fixture_id"] for row in rows}) != FIXTURE_COUNT:
        raise AssertionError("Q03 fixture geometry")
    return rows


def instruction_for(row: dict[str, Any]) -> str:
    conversation = serialize_messages(row["messages"])
    kind = row["kind"]
    return (
        "This is a non-scientific controlled-output qualification. Do NOT inspect or modify the host and do NOT "
        "execute any command. Read the serialized experimental conversation below and determine the requested next "
        f"output. Call ONLY `{ALLOWED_TOOL}` exactly once with `kind={kind}`. The `content` argument must contain "
        + ("only the shell command, without THOUGHT or markdown fences." if kind == "bash_action" else "only the requested ordinary text.")
        + " Do not answer in plain text and do not call any other tool.\n\n"
        + conversation
    )


def prepare_fixture(root: Path, row: dict[str, Any]) -> tuple[Path, Path, Path]:
    unit_root = root / "fixtures" / row["fixture_id"]
    if unit_root.exists():
        raise RuntimeError(f"Q03 fixture root exists: {unit_root}")
    unit_root.mkdir(parents=True)
    atom_home = unit_root / "atomcode-home"
    workdir = unit_root / "workdir"
    progress = unit_root / "output-progress.json"
    atom_home.mkdir()
    workdir.mkdir()
    auth_source = Path.home() / ".atomcode/auth.toml"
    if not auth_source.is_file():
        raise RuntimeError("Q03 AtomCode auth.toml missing")
    shutil.copy2(auth_source, atom_home / "auth.toml")
    os.chmod(atom_home / "auth.toml", 0o600)
    (atom_home / "config.toml").write_text(atomcode_config(), encoding="utf-8")
    (workdir / "AGENTS.md").write_text(agents_md(), encoding="utf-8")
    return atom_home, workdir, progress


def run_live_fixture(root: Path, row: dict[str, Any]) -> dict[str, Any]:
    atom_home, workdir, progress = prepare_fixture(root, row)
    unit_root = atom_home.parent
    events_path = unit_root / "live-events.jsonl"
    process: subprocess.Popen[Any] | None = None
    stream_done = threading.Event()
    stream_errors: list[str] = []
    events: "queue.Queue[dict[str, Any]]" = queue.Queue()
    try:
        process, base, token = start_daemon(atom_home, workdir, unit_root / "atomcode-daemon.log")
        (atom_home / "mcp.json").write_text(json.dumps(mcp_config(progress), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        http_json(base, token, "/live/mode", method="POST", body={"mode": "build"})

        def stream() -> None:
            request = urllib.request.Request(base + "/live", headers={"Authorization": "Bearer " + token})
            try:
                with urllib.request.urlopen(request, timeout=LIVE_TIMEOUT_SECONDS + 30) as response:
                    for raw in response:
                        if stream_done.is_set():
                            break
                        line = raw.decode("utf-8", "replace").strip()
                        if not line.startswith("data:"):
                            continue
                        try:
                            event = json.loads(line[5:].strip())
                        except Exception:
                            continue
                        append_jsonl(events_path, event)
                        events.put(event)
            except Exception as exc:
                if not stream_done.is_set():
                    stream_errors.append(f"{type(exc).__name__}: {exc}")
                    events.put({"type": "stream_exception", "message": stream_errors[-1]})

        thread = threading.Thread(target=stream, daemon=True)
        thread.start()
        deadline = time.time() + 60
        while time.time() < deadline:
            if stream_errors:
                raise RuntimeError(stream_errors[-1])
            if progress.is_file():
                state = json.loads(progress.read_text(encoding="utf-8"))
                if state.get("status") == "TOOLS_LISTED" and state.get("tool_count") == 1:
                    break
            time.sleep(0.1)
        else:
            raise RuntimeError("Q03 MCP tool catalog not ready")

        usage_before = codingplan_usage(base, token)
        submit = http_json(
            base,
            token,
            "/live/message",
            method="POST",
            body={"message": instruction_for(row), "provider": MODEL_PROFILE, "client_input_id": "c1-q03-output-mcp"},
        )
        if submit.get("accepted") is not True:
            raise RuntimeError(f"Q03 live submit rejected: {submit}")

        tool_names: list[str] = []
        token_events: list[dict[str, Any]] = []
        prohibited_tool = None
        error_message = None
        captured = False
        deadline = time.time() + LIVE_TIMEOUT_SECONDS
        while time.time() < deadline:
            try:
                event = events.get(timeout=0.5)
            except queue.Empty:
                continue
            kind = event.get("type")
            if kind == "tokens":
                token_events.append(event)
            elif kind == "permission_request":
                name = str(event.get("tool_name", ""))
                allow = name == ALLOWED_TOOL
                http_json(base, token, "/live/permission", method="POST", body={"decision": "allow" if allow else "deny", "tool_name": name}, timeout=10)
                if not allow:
                    prohibited_tool = name
                    try:
                        http_json(base, token, "/live/stop", method="POST", body={}, timeout=10)
                    except Exception:
                        pass
                    break
            elif kind == "tool_start":
                name = str(event.get("name", ""))
                tool_names.append(name)
                if name != ALLOWED_TOOL:
                    prohibited_tool = name
                    try:
                        http_json(base, token, "/live/stop", method="POST", body={}, timeout=10)
                    except Exception:
                        pass
                    break
                if len(tool_names) > 1:
                    error_message = "more_than_one_allowed_tool_call"
                    try:
                        http_json(base, token, "/live/stop", method="POST", body={}, timeout=10)
                    except Exception:
                        pass
                    break
            elif kind == "tool_result" and str(event.get("name", "")) == ALLOWED_TOOL:
                captured = True
                try:
                    http_json(base, token, "/live/stop", method="POST", body={}, timeout=10)
                except Exception:
                    pass
                break
            elif kind == "error":
                error_message = str(event.get("message", "AtomCode live error"))
                break
            elif kind == "stream_exception":
                error_message = str(event.get("message", "stream exception"))
                break
        else:
            error_message = "live_fixture_timeout"
            try:
                http_json(base, token, "/live/stop", method="POST", body={}, timeout=10)
            except Exception:
                pass

        deadline = time.time() + 5
        while time.time() < deadline:
            if progress.is_file():
                state = json.loads(progress.read_text(encoding="utf-8"))
                if state.get("status") in {"OUTPUT_CAPTURED", "TOOL_CALL_CAP_EXCEEDED", "UNKNOWN_TOOL_ATTEMPT", "MALFORMED_OUTPUT"}:
                    break
            time.sleep(0.05)
        state = json.loads(progress.read_text(encoding="utf-8")) if progress.is_file() else {}
        time.sleep(0.4)
        usage_after = codingplan_usage(base, token)
        content = state.get("content") if state.get("status") == "OUTPUT_CAPTURED" else None
        exact_pass = True
        if row.get("exact"):
            exact_pass = content == row.get("expected")
        semantic_pass = isinstance(content, str) and bool(content.strip())
        if row["kind"] == "bash_action" and isinstance(content, str):
            semantic_pass = semantic_pass and "```" not in content and not content.lstrip().startswith("THOUGHT:")
        model_round_count = len(token_events)
        passed = (
            captured
            and prohibited_tool is None
            and error_message is None
            and tool_names == [ALLOWED_TOOL]
            and state.get("status") == "OUTPUT_CAPTURED"
            and state.get("call_count") == 1
            and state.get("kind") == row["kind"]
            and semantic_pass
            and exact_pass
            and model_round_count == 1
        )
        result = {
            "schema_version": 1,
            "created_at_utc": now(),
            "fixture_id": row["fixture_id"],
            "requested_kind": row["kind"],
            "exact_required": bool(row.get("exact")),
            "expected_sha256": sha256_text(row["expected"]) if row.get("expected") is not None else None,
            "captured_kind": state.get("kind"),
            "captured_content": content,
            "captured_content_sha256": state.get("content_sha256"),
            "captured_content_bytes": state.get("content_bytes"),
            "tool_names": tool_names,
            "prohibited_tool": prohibited_tool,
            "error_message": error_message,
            "model_round_count": model_round_count,
            "prompt_tokens": sum(int(e.get("prompt", 0)) for e in token_events),
            "completion_tokens": sum(int(e.get("completion", 0)) for e in token_events),
            "codingplan_usage_before": usage_before,
            "codingplan_usage_after": usage_after,
            "bridge_progress_sha256": sha256_file(progress) if progress.is_file() else None,
            "live_events_sha256": sha256_file(events_path) if events_path.is_file() else None,
            "pass": passed,
            "scientific_source_tasks_used": 0,
        }
        atomic_json(unit_root / "fixture-result.json", result)
        return result
    finally:
        stream_done.set()
        if process is not None:
            terminate_process(process)


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("Q03 root exists; no overwrite")
    if not ATOMCODE_BIN.is_file() or not Path.home().joinpath(".atomcode/auth.toml").is_file():
        raise RuntimeError("Q03 AtomCode binary/auth missing")
    if not SERVER_SOURCE.is_file() or not CONTRACT.is_file():
        raise RuntimeError("Q03 source/contract missing")
    root.mkdir(parents=True)
    rows = fixtures()
    payload = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q03_PREPARE_PASS",
        "atomcode_version": subprocess.run([str(ATOMCODE_BIN), "--version"], text=True, capture_output=True, check=True).stdout.strip(),
        "model_profile": MODEL_PROFILE,
        "model_id": MODEL_ID,
        "allowed_tool": ALLOWED_TOOL,
        "fixture_count": len(rows),
        "action_exact_count": 4,
        "action_realistic_count": 4,
        "text_exact_count": 4,
        "realistic_histories": [row.get("history_pairs") for row in rows if row.get("history_pairs")],
        "server_source_sha256": sha256_file(SERVER_SOURCE),
        "contract_sha256": sha256_file(CONTRACT),
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_calls": 0,
    }
    atomic_json(root / "prepare.json", payload)
    return payload


def run_panel(root: Path) -> dict[str, Any]:
    if not (root / "prepare.json").is_file():
        raise RuntimeError("Q03 prepare first")
    if (root / "q03-result.json").exists():
        raise RuntimeError("Q03 result exists; no retry/overwrite")
    rows: list[dict[str, Any]] = []
    for i, row in enumerate(fixtures(), 1):
        result = run_live_fixture(root, row)
        rows.append(result)
        print(json.dumps({"i": i, "fixture": row["fixture_id"], "pass": result["pass"], "tool": result["tool_names"], "prohibited": result["prohibited_tool"], "rounds": result["model_round_count"]}), flush=True)
        if not result["pass"]:
            break
    passed = len(rows) == FIXTURE_COUNT and all(row["pass"] for row in rows)
    payload = {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ATOMGIT_QWEN38_Q03_CONTROLLED_OUTPUT_MCP_PASS" if passed else "STOP_ATOMGIT_QWEN38_Q03_CONTROLLED_OUTPUT_MCP",
        "pass": passed,
        "attempted": len(rows),
        "qualified": sum(bool(row["pass"]) for row in rows),
        "total": FIXTURE_COUNT,
        "allowed_tool": ALLOWED_TOOL,
        "prohibited_tool_attempts": sum(row.get("prohibited_tool") is not None for row in rows),
        "model_round_total": sum(int(row.get("model_round_count") or 0) for row in rows),
        "rows": rows,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "shadow_calls": 0,
        "final_calls": 0,
        "next_if_pass": "Prospectively create an entirely new fresh3 PACTA-MSR substrate; never reuse retired fresh2 tasks.",
    }
    atomic_json(root / "q03-result.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--phase", choices=("prepare", "run"), required=True)
    args = parser.parse_args()
    result = prepare(args.root) if args.phase == "prepare" else run_panel(args.root)
    print(json.dumps({k: result.get(k) for k in ["status", "pass", "attempted", "qualified", "total", "fixture_count"] if k in result}, sort_keys=True))


if __name__ == "__main__":
    main()
