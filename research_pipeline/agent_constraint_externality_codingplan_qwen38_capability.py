from __future__ import annotations

import argparse
import json
import os
import queue
import shutil
import socket
import subprocess
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import evaluate_arm_from_materialized_state
from research_pipeline.agent_constraint_externality_capability_execute import capability_gate
from research_pipeline.agent_constraint_externality_codingplan_prereg import (
    ATOMCODE_BINARY_SHA256, BASE_URL, CAPABILITY_FAMILIES, CONTEXT_WINDOW,
    CONTRACT_OUTPUT, MAX_OUTPUT_TOKENS, MODEL_ID, MODEL_PROFILE, MODEL_ROUND_CAP,
    PROVIDER, Q0_OUTPUT, Q1_OUTPUT, REASONING_EFFORT, REPEATS, RETRY_MAX_ATTEMPTS,
    TOOL_CALL_CAP, V4_BUNDLE, V4_QUAL,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID, EpisodeUnit, RunnerError, sha256_file, sha256_value,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
ATOMCODE_BIN = Path.home() / ".local/bin/atomcode"
APPWORLD_PYTHON = ROOT / "runtimes/appworld-constraint-externality-py312/bin/python"
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
EXECUTION_ID = "CODINGPLAN-QWEN38-27B-CAPABILITY-A0"
LEDGER_SCHEMA = "ace-codingplan-capability-ledger-a0-v1"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-a0-result-20260902.json"


class CodingPlanHarnessError(RunnerError):
    pass


class CodingPlanInterfaceStop(CodingPlanHarnessError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path, status: str | None = None) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("object_id") != OBJECT_ID:
        raise CodingPlanHarnessError(f"Object mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise CodingPlanHarnessError(f"Unexpected status in {path}: {payload.get('status')}")
    claimed = payload.get("content_sha256")
    if claimed is not None:
        unsigned = dict(payload); unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise CodingPlanHarnessError(f"Content hash mismatch: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", buffering=1) as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush(); os.fsync(handle.fileno())


def ledger_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def ledger_states(path: Path) -> dict[str, str]:
    states: dict[str, str] = {}
    for row in ledger_rows(path):
        uid, event = row["unit_id"], row["event"]
        if event == "DISPATCH":
            if uid in states: raise CodingPlanHarnessError(f"Duplicate dispatch: {uid}")
            states[uid] = "UNKNOWN_AFTER_DISPATCH"
        elif event in {"COMPLETION", "FAILURE"}:
            if states.get(uid) != "UNKNOWN_AFTER_DISPATCH": raise CodingPlanHarnessError(f"Terminal without dispatch: {uid}")
            states[uid] = event
        else: raise CodingPlanHarnessError(f"Unknown ledger event: {event}")
    return states


def units() -> list[EpisodeUnit]:
    rows = [EpisodeUnit(namespace="capability", key=(MODEL_ID, f, r), stage="CODINGPLAN_QWEN38_CAPABILITY_A0", family_id=f, repeat=r) for f in CAPABILITY_FAMILIES for r in REPEATS]
    if len(rows) != 8 or len({row.unit_id for row in rows}) != 8: raise CodingPlanHarnessError("Expected eight unique units.")
    return rows


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0)); return int(sock.getsockname()[1])


def http_json(base: str, token: str, path: str, *, method: str = "GET", body: dict[str, Any] | None = None, timeout: float = 20.0) -> Any:
    headers = {"Authorization": "Bearer " + token}; data = None
    if body is not None:
        headers["Content-Type"] = "application/json"; data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response: return json.load(response)


def codingplan_usage(base: str, token: str) -> dict[str, Any]:
    window = http_json(base, token, "/codingplan/usage/summary")["primary_window"]
    return {k: window.get(k) for k in ("used", "remaining", "limit", "next_reset_at")}


def atomcode_config() -> str:
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
retry_max_attempts = {RETRY_MAX_ATTEMPTS}
reasoning_effort = "{REASONING_EFFORT}"
system_prompt = "Complete the task using only AppWorld MCP tools. Preserve unrelated state. Batch independent AppWorld tool calls in the same model round whenever possible. When finished, return a concise completion message."
[loop_config]
max_rounds = {MODEL_ROUND_CAP}
[coding]
max_rounds = {MODEL_ROUND_CAP}
shell_guard_policy = "prompt"
[tools.todo]
enabled = false
[ui]
ai_session_naming = false
'''


def agents_md() -> str:
    return '''# Scientific AppWorld capability run\nThe user message is an AppWorld benchmark task, not software engineering.\nUse only tools whose names begin with `mcp__appworld__`. Never use host coding, shell, file, web, memory, AtomGit, task/team/subagent, skill, or code-graph tools. Do not inspect or modify the host workspace. Preserve unrelated AppWorld state. Batch independent AppWorld tool calls in the same model round whenever possible because CodingPlan quota is request-count limited, not token limited.\n'''

def mcp_config(*, unit: EpisodeUnit, unit_root: Path, progress: Path, task_id: str) -> dict[str, Any]:
    args = [
        "-m", "research_pipeline.agent_constraint_externality_codingplan_mcp_bridge",
        "--appworld-root", str(APPWORLD_ROOT), "--bundle", str(V4_BUNDLE),
        "--family-id", unit.family_id, "--repeat", str(unit.repeat),
        "--runtime-root", str(unit_root / "appworld"), "--task-id", task_id,
        "--experiment-name", "ace-codingplan-qwen38-capability-a0",
        "--progress", str(progress), "--tool-call-cap", str(TOOL_CALL_CAP),
    ]
    return {"mcpServers": {"appworld": {
        "command": str(APPWORLD_PYTHON), "args": args, "env": {"PYTHONPATH": str(ROOT)},
        "timeout_ms": 30000, "trust": True,
    }}}


def wait_file(path: Path, timeout: float) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.is_file(): return
        time.sleep(0.1)
    raise CodingPlanInterfaceStop(f"Timed out waiting for {path}")


def wait_mcp_ready(base: str, token: str, timeout: float = 45.0) -> dict[str, Any]:
    deadline = time.time() + timeout; last: Any = None
    while time.time() < deadline:
        try:
            data = http_json(base, token, "/mcp/status", timeout=5); last = data
            servers = {row["name"]: row for row in data.get("servers", [])}; appworld = servers.get("appworld")
            if appworld and appworld.get("status") == "connected" and int(appworld.get("tool_count", 0)) > 0 and "appworld" not in data.get("blocked", []): return data
        except Exception as exc: last = f"{type(exc).__name__}: {exc}"
        time.sleep(0.2)
    raise CodingPlanInterfaceStop(f"AppWorld MCP not ready: {last}")


def terminate_process(process: subprocess.Popen[Any], timeout: float = 10.0) -> None:
    if process.poll() is not None: return
    process.terminate()
    try: process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill(); process.wait(timeout=5)


def run_live_turn(*, base: str, token: str, instruction: str, progress_path: Path, before_submit: Any, timeout_seconds: float = 360.0) -> dict[str, Any]:
    events: "queue.Queue[dict[str, Any]]" = queue.Queue(); stream_errors: list[str] = []; stop_stream = threading.Event()
    def stream() -> None:
        request = urllib.request.Request(base + "/live", headers={"Authorization": "Bearer " + token})
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds + 30) as response:
                for raw in response:
                    if stop_stream.is_set(): break
                    line = raw.decode("utf-8", "replace").strip()
                    if not line.startswith("data:"): continue
                    try: event = json.loads(line[5:].strip())
                    except Exception: continue
                    events.put(event)
        except Exception as exc:
            stream_errors.append(f"{type(exc).__name__}: {exc}"); events.put({"type": "stream_exception", "message": stream_errors[-1]})
    thread = threading.Thread(target=stream, daemon=True); thread.start()
    # GET /live creates the session runtime. Do not dispatch until that runtime has
    # actually initialized and listed the AppWorld MCP tools.
    ready_deadline = time.time() + 60
    while time.time() < ready_deadline:
        if stream_errors: raise CodingPlanInterfaceStop(stream_errors[-1])
        if progress_path.is_file():
            progress = read_json(progress_path)
            if progress.get("status") == "TOOLS_LISTED": break
        time.sleep(0.1)
    else: raise CodingPlanInterfaceStop("Session MCP tools were not listed before first model request.")
    pre_submit = before_submit()
    submit = http_json(base, token, "/live/message", method="POST", body={"message": instruction, "provider": MODEL_PROFILE, "client_input_id": "ace-codingplan-capability"})
    if submit.get("accepted") is not True:
        stop_stream.set(); raise CodingPlanInterfaceStop(f"Live submit rejected: {submit}")
    tool_names: list[str] = []; tool_results: list[dict[str, Any]] = []; token_events: list[dict[str, int]] = []; final_text: list[str] = []
    stop_reason = None; terminal_message = None; saw_running = False; prohibited_tool = None; error_message = None; deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try: event = events.get(timeout=0.5)
        except queue.Empty: continue
        kind = event.get("type")
        if kind == "reasoning": continue
        if kind == "text": final_text.append(str(event.get("content", "")))
        elif kind == "tokens": token_events.append({"prompt": int(event.get("prompt", 0)), "completion": int(event.get("completion", 0)), "total": int(event.get("total", 0))})
        elif kind == "permission_request":
            name = str(event.get("tool_name", "")); allow = name.startswith("mcp__appworld__")
            try: http_json(base, token, "/live/permission", method="POST", body={"decision": "allow" if allow else "deny", "tool_name": name}, timeout=10)
            except Exception as exc: error_message = f"permission_response_failed:{type(exc).__name__}:{exc}"; break
            if not allow:
                prohibited_tool = name
                try: http_json(base, token, "/live/stop", method="POST", body={}, timeout=10)
                except Exception: pass
                break
        elif kind == "tool_start":
            name = str(event.get("name", "")); tool_names.append(name)
            if not name.startswith("mcp__appworld__"):
                prohibited_tool = name
                try: http_json(base, token, "/live/stop", method="POST", body={}, timeout=10)
                except Exception: pass
                break
            if len(tool_names) > TOOL_CALL_CAP:
                stop_reason = "appworld_tool_call_cap"
                try: http_json(base, token, "/live/stop", method="POST", body={}, timeout=10)
                except Exception: pass
                break
        elif kind == "tool_result": tool_results.append({"name": str(event.get("name", "")), "success": bool(event.get("success"))})
        elif kind == "error": error_message = str(event.get("message", "AtomCode live error")); break
        elif kind == "stream_exception": error_message = str(event.get("message", "stream exception")); break
        elif kind == "state":
            running = bool(event.get("running")); saw_running = saw_running or running
            if not running and saw_running:
                stop_reason = str(event.get("stop_reason") or "unknown"); terminal_message = event.get("message"); break
    if stop_reason is None and prohibited_tool is None and error_message is None:
        try: http_json(base, token, "/live/stop", method="POST", body={}, timeout=10)
        except Exception: pass
        error_message = "live_turn_timeout"
    stop_stream.set(); text = "".join(final_text)
    return {
        "submit": submit, "tool_names": tool_names, "tool_results": tool_results,
        "model_round_count": len(token_events), "prompt_tokens_total": sum(row["prompt"] for row in token_events),
        "completion_tokens_total": sum(row["completion"] for row in token_events), "stop_reason": stop_reason,
        "terminal_message": terminal_message, "prohibited_tool": prohibited_tool, "error_message": error_message,
        "final_text_sha256": sha256_value(text), "final_text_bytes": len(text.encode("utf-8")), "stream_errors": stream_errors, "pre_submit": pre_submit,
    }

def prepare_unit_runtime(*, unit: EpisodeUnit, unit_root: Path) -> tuple[Path, Path, Path, dict[str, Any]]:
    atom_home = unit_root / "atomcode-home"; workdir = unit_root / "atomcode-workdir"; progress = unit_root / "bridge-progress.json"
    atom_home.mkdir(parents=True, exist_ok=False); workdir.mkdir(parents=True, exist_ok=False)
    auth_source = Path.home() / ".atomcode/auth.toml"
    if not auth_source.is_file(): raise CodingPlanInterfaceStop("AtomCode auth.toml missing.")
    shutil.copy2(auth_source, atom_home / "auth.toml"); os.chmod(atom_home / "auth.toml", 0o600)
    (atom_home / "config.toml").write_text(atomcode_config(), encoding="utf-8")
    (workdir / "AGENTS.md").write_text(agents_md(), encoding="utf-8")
    task_id = "acecpa0" + unit.family_id.lower().replace("-", "") + f"r{unit.repeat}_1"
    return atom_home, workdir, progress, mcp_config(unit=unit, unit_root=unit_root, progress=progress, task_id=task_id)


def start_daemon(*, atom_home: Path, workdir: Path, log_path: Path) -> tuple[subprocess.Popen[Any], str, str]:
    port = free_port(); env = os.environ.copy()
    env.update({"ATOMCODE_HOME": str(atom_home), "ATOMCODE_SUBAGENT": "0", "ATOMCODE_AI_SESSION_NAMING": "0", "ATOMCODE_TURN_MAX_ROUNDS": str(MODEL_ROUND_CAP), "ATOMCODE_LOOP_MAX_ROUNDS": str(MODEL_ROUND_CAP)})
    log = log_path.open("wb")
    process = subprocess.Popen([str(ATOMCODE_BIN), "daemon", "--port", str(port), "--idle-timeout", "0", "--no-telemetry"], cwd=workdir, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    token_path = atom_home / f"daemon-{port}.json"; wait_file(token_path, 20); token = str(read_json(token_path)["token"]); base = f"http://127.0.0.1:{port}"
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            if http_json(base, token, "/health", timeout=3).get("status") == "ok": break
        except Exception: pass
        time.sleep(0.1)
    else:
        terminate_process(process); raise CodingPlanInterfaceStop("AtomCode daemon health check failed.")
    return process, base, token


def dispatch_row(*, unit: EpisodeUnit, arm: dict[str, Any], progress: dict[str, Any], usage: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": LEDGER_SCHEMA, "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "DISPATCH", "unit_id": unit.unit_id,
        "unit": {"family_id": unit.family_id, "repeat": unit.repeat, "stage": unit.stage}, "provider": PROVIDER, "model_profile": MODEL_PROFILE,
        "model_id": MODEL_ID, "harness": "ATOMCODE_CODINGPLAN_MCP_V1", "prompt_sha256": sha256_value(arm["task_instruction"]),
        "initial_snapshot_sha256": progress["initial_snapshot_sha256"], "tool_call_cap": TOOL_CALL_CAP, "model_round_cap": MODEL_ROUND_CAP,
        "codingplan_window_before": usage, "dispatch_time_ns": time.time_ns(), "attempt": 1, "retry_allowed": False, "replacement_allowed": False}


def execute_panel(*, runtime_root: Path, ledger_path: Path) -> None:
    verified(CONTRACT_OUTPUT, "CODINGPLAN_QWEN38_CAPABILITY_A0_AUTHORIZED"); verified(Q0_OUTPUT, "CODINGPLAN_MCP_Q0_PASS"); verified(Q1_OUTPUT, "CODINGPLAN_APPWORLD_MCP_LIVE_PREDISPATCH_PASS"); verified(V4_QUAL, "CAPABILITY_SUBSTRATE_V4_PUBLIC_REACHABILITY_WITH_HEADROOM_PASS")
    if sha256_file(ATOMCODE_BIN) != ATOMCODE_BINARY_SHA256: raise CodingPlanInterfaceStop("AtomCode binary hash drifted from Q0.")
    spec = load_protected_spec(V4_BUNDLE); families = {row["family_id"]: row for row in spec["families"]}; states = ledger_states(ledger_path)
    for unit in units():
        state = states.get(unit.unit_id)
        if state == "COMPLETION": continue
        if state is not None: raise CodingPlanInterfaceStop(f"Refusing replay of dispatched unit {unit.unit_id}: {state}")
        family = families[unit.family_id]; arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
        if int(arm["matching"]["tool_budget"]) != TOOL_CALL_CAP: raise CodingPlanInterfaceStop("V4 tool budget drifted from 16.")
        unit_root = runtime_root / unit.unit_id.replace(":", "_").replace("|", "_")
        if unit_root.exists(): raise CodingPlanInterfaceStop(f"Refusing overwrite: {unit_root}")
        unit_root.mkdir(parents=True); atom_home, workdir, progress_path, mcp_payload = prepare_unit_runtime(unit=unit, unit_root=unit_root)
        process: subprocess.Popen[Any] | None = None; live: dict[str, Any] | None = None; usage_before: dict[str, Any] = {}; usage_after: dict[str, Any] = {}
        try:
            process, base, token = start_daemon(atom_home=atom_home, workdir=workdir, log_path=unit_root / "atomcode-daemon.log")
            # Avoid two MCP instances: daemon boots with no mcp.json; only the live
            # session created below sees this newly activated user-level MCP config.
            (atom_home / "mcp.json").write_text(json.dumps(mcp_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            http_json(base, token, "/live/mode", method="POST", body={"mode": "build"})
            def before_submit() -> dict[str, Any]:
                progress = read_json(progress_path)
                if progress.get("status") != "TOOLS_LISTED": raise CodingPlanInterfaceStop(f"Session MCP catalog not frozen: {progress.get('status')}")
                usage = codingplan_usage(base, token)
                if int(usage["remaining"]) < MODEL_ROUND_CAP + 5: raise CodingPlanInterfaceStop("Insufficient CodingPlan rolling-window headroom.")
                append_jsonl(ledger_path, dispatch_row(unit=unit, arm=arm, progress=progress, usage=usage))
                return {"usage_before": usage}
            live = run_live_turn(base=base, token=token, instruction=arm["task_instruction"], progress_path=progress_path, before_submit=before_submit)
            usage_before = dict(live["pre_submit"]["usage_before"]); time.sleep(0.3); usage_after = codingplan_usage(base, token)
            if live["prohibited_tool"]:
                append_jsonl(ledger_path, {"schema_version": LEDGER_SCHEMA, "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "FAILURE", "unit_id": unit.unit_id, "failure_class": "HARNESS_CONTAMINATION_NON_APPWORLD_TOOL", "message": str(live["prohibited_tool"]), "model_round_count": live["model_round_count"], "codingplan_window_after": usage_after, "time_ns": time.time_ns(), "retry_attempted": False})
                raise CodingPlanInterfaceStop(f"Non-AppWorld tool attempted: {live['prohibited_tool']}")
            if live["error_message"] or live["stop_reason"] in {"provider_error", "timeout", "rate_limited", "prompt_rejected", "policy_denied", "runtime_stopped"}:
                message = str(live["error_message"] or live["stop_reason"])
                append_jsonl(ledger_path, {"schema_version": LEDGER_SCHEMA, "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "FAILURE", "unit_id": unit.unit_id, "failure_class": "CODINGPLAN_INTERFACE_STOP", "message": message[:400], "model_round_count": live["model_round_count"], "codingplan_window_after": usage_after, "time_ns": time.time_ns(), "retry_attempted": False})
                raise CodingPlanInterfaceStop(message)
        finally:
            if process is not None: terminate_process(process)
        deadline = time.time() + 15
        while time.time() < deadline:
            if progress_path.is_file():
                progress = read_json(progress_path)
                if progress.get("status") in {"CLOSED_STATE_SAVED", "STATE_SAVED_AFTER_TOOL", "TOOL_CALL_CAP_EXCEEDED"}: break
            time.sleep(0.1)
        if live is None: raise CodingPlanInterfaceStop("No live result after dispatch.")
        progress = read_json(progress_path); measurement_root = unit_root / "measurement-full-dbs"
        evaluation = evaluate_arm_from_materialized_state(arm=arm, source_db_root=Path(progress["source_db_root"]), changes_db_root=Path(progress["changes_db_root"]), measurement_db_root=measurement_root)
        normal_completion = live["stop_reason"] == "stopped" and int(progress.get("tool_call_count", 0)) <= TOOL_CALL_CAP
        append_jsonl(ledger_path, {"schema_version": LEDGER_SCHEMA, "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "COMPLETION", "unit_id": unit.unit_id,
            "tool_loop_completed": normal_completion, "atomcode_stop_reason": live["stop_reason"], "appworld_tool_call_count": int(progress.get("tool_call_count", 0)),
            "model_round_count": int(live["model_round_count"]), "prompt_tokens_total": int(live["prompt_tokens_total"]), "completion_tokens_total": int(live["completion_tokens_total"]),
            "target_success": bool(evaluation["target_success"]), "non_target_preservation": float(evaluation["non_target_preservation"]), "malformed_tool_calls": 0,
            "final_text_sha256": live["final_text_sha256"], "final_text_bytes": live["final_text_bytes"], "codingplan_window_before": usage_before, "codingplan_window_after": usage_after,
            "bridge_progress_sha256": sha256_file(progress_path), "measurement_content_sha256": evaluation["measurement"]["content_sha256"], "time_ns": time.time_ns()})
        states = ledger_states(ledger_path)

def adjudicate(*, ledger_path: Path) -> dict[str, Any]:
    rows = ledger_rows(ledger_path); states = ledger_states(ledger_path); expected = units()
    missing = [unit.unit_id for unit in expected if states.get(unit.unit_id) != "COMPLETION"]
    if missing: raise CodingPlanInterfaceStop("Incomplete CodingPlan panel: " + ", ".join(missing))
    completions = [row for row in rows if row["event"] == "COMPLETION"]
    if len(completions) != 8: raise CodingPlanInterfaceStop("Expected exactly eight completion rows.")
    measurements = [{"tool_loop_completed": bool(row["tool_loop_completed"]), "target_success": bool(row["target_success"]), "non_target_preservation": float(row["non_target_preservation"]), "malformed_tool_calls": int(row["malformed_tool_calls"])} for row in completions]
    gate = capability_gate(measurements)
    result: dict[str, Any] = {
        "schema_version": "ace-codingplan-qwen38-capability-a0-result-v1", "object_id": OBJECT_ID, "execution_id": EXECUTION_ID,
        "status": gate["verdict"], "provider": PROVIDER, "model_profile": MODEL_PROFILE, "model_id": MODEL_ID,
        "harness": "ATOMCODE_CODINGPLAN_MCP_V1", "gate": gate, "valid_capability_measurements": 8, "agent_episode_count": 8,
        "appworld_tool_call_total": sum(int(row["appworld_tool_call_count"]) for row in completions),
        "model_round_count": sum(int(row["model_round_count"]) for row in completions),
        "prompt_tokens_total": sum(int(row["prompt_tokens_total"]) for row in completions),
        "completion_tokens_total": sum(int(row["completion_tokens_total"]) for row in completions),
        "codingplan_window_first_before": completions[0]["codingplan_window_before"], "codingplan_window_last_after": completions[-1]["codingplan_window_after"],
        "scientific_outcomes_observed": 0, "f0_executed": False, "ledger_sha256": sha256_file(ledger_path),
        "authority": {"f0": False, "f0_reason": "CodingPlan capability selection requires separate human F0 authorization even if PASS.", "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False},
    }
    result["content_sha256"] = sha256_value(result); return result


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--runtime-root", type=Path, required=True); parser.add_argument("--ledger", type=Path, required=True); parser.add_argument("--result-output", type=Path, default=RESULT_OUTPUT); args = parser.parse_args()
    execute_panel(runtime_root=args.runtime_root, ledger_path=args.ledger); result = adjudicate(ledger_path=args.ledger); write_json(args.result_output, result)
    print(json.dumps({"status": result["status"], "model_round_count": result["model_round_count"], "appworld_tool_call_total": result["appworld_tool_call_total"], "target_success_rate": result["gate"]["target_success_rate"], "tool_loop_completion_rate": result["gate"]["tool_loop_completion_rate"], "f0_authorized": False}, sort_keys=True))


if __name__ == "__main__": main()
