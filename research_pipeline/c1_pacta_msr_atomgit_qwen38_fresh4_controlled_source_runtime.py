"""Fresh4 source runtime using the Q0.3 controlled-output MCP transport.

The already-executed fresh3 MiniSWEAgent/Docker trajectory loop is reused unchanged.
Only the provider object is rebound.  Each logical model output is one AtomCode live
model round and one trusted MCP `submit_output(kind=text)` call that captures the
complete MiniSWEAgent assistant turn without executing it.  Any host/native tool is
denied and stops the logical call.
"""
from __future__ import annotations

import json
import os
import queue
import re
import shutil
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

from research_pipeline import c1_pacta_msr_atomgit_qwen38_fresh3_bridge_source_runtime as base
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q03_output_mcp_20260903 as q03
from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes, atomic_json, sha256_file, sha256_text
from research_pipeline.run_c1_pacta_msr_atomgit_qwen38_q0_20260902 import serialize_messages

PROVIDER_ID = "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_FRESH4_CONTROLLED_OUTPUT_SOURCE_V1"
BRIDGE_SCHEMA = "c1-controlled-output-mcp-full-minisweagent-turn-v1"
ALLOWED_TOOL = "mcp__c1output__submit_output"
SOURCE_OUTPUT_KIND = "text"
SOURCE_MAX_COMPLETION_TOKENS = 32768
PACTA_FIRST_DECISION_BUDGET = 2048
ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS = 900
SAMPLING_CONTROL = "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9"


def now() -> str:
    return base.now()


def safe_label(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", label)[:120]


def source_instruction(messages: list[dict[str, str]], label: str) -> str:
    conversation = serialize_messages(messages)
    return (
        "You are producing exactly the next assistant turn for an offline controlled MiniSWEAgent coding trajectory. "
        "The EXPERIMENTAL_CONVERSATION below is the complete task and environment history; do not inspect the host "
        "workspace and do not execute commands yourself. Follow the system message inside that conversation. "
        f"Call ONLY `{ALLOWED_TOOL}` exactly once with kind=text. The content argument must be exactly the complete "
        "next assistant response, including its THOUGHT section and exactly one fenced bash command as required by "
        "the conversation. The bash command is only a proposed action; an external frozen Docker runner will execute "
        "it after capture. Do not answer in plain text and do not call any other tool.\n\n"
        f"LOGICAL_LABEL: {label}\n\n{conversation}"
    )


class Fresh4ControlledSourceProvider:
    def __init__(self, *, root: Path, config_path: Path, workdir: Path) -> None:
        self.root = root
        self.config_path = config_path
        self.workdir = workdir
        self.calls = 0
        self.transport_attempts = 0
        self.prompt_tokens = 0
        self.output_tokens = 0
        self.workdir.mkdir(parents=True, exist_ok=True)
        if not q03.ATOMCODE_BIN.is_file():
            raise RuntimeError("STOP_FRESH3_BRIDGE_SOURCE_FRESH4_ATOMCODE_BINARY_MISSING")
        auth = Path.home() / ".atomcode/auth.toml"
        if not auth.is_file():
            raise RuntimeError("STOP_FRESH3_BRIDGE_SOURCE_FRESH4_ATOMCODE_AUTH_MISSING")

    def call(self, messages: list[dict[str, str]], label: str) -> dict[str, Any]:
        self.calls += 1
        self.transport_attempts += 1
        logical = self.calls
        prompt = source_instruction(messages, label)
        stem = f"{logical:04d}"
        request_path = self.root / "raw" / f"request-{stem}.json"
        response_path = self.root / "raw" / f"response-{stem}.stdout.jsonl"
        stderr_path = self.root / "raw" / f"response-{stem}.stderr.txt"
        call_root = self.root / "controlled-output-calls" / f"{stem}__{safe_label(label)}"
        if call_root.exists():
            raise RuntimeError("STOP_FRESH3_BRIDGE_SOURCE_FRESH4_CALL_ROOT_EXISTS")
        call_root.mkdir(parents=True)
        atom_home = call_root / "atomcode-home"
        live_workdir = call_root / "workdir"
        progress = call_root / "output-progress.json"
        atom_home.mkdir(); live_workdir.mkdir()
        auth_source = Path.home() / ".atomcode/auth.toml"
        shutil.copy2(auth_source, atom_home / "auth.toml"); os.chmod(atom_home / "auth.toml", 0o600)
        (atom_home / "config.toml").write_text(q03.atomcode_config(), encoding="utf-8")
        (live_workdir / "AGENTS.md").write_text(q03.agents_md(), encoding="utf-8")
        safe = {
            "schema_version": 1,
            "timestamp_utc": now(),
            "provider_id": PROVIDER_ID,
            "bridge_schema": BRIDGE_SCHEMA,
            "label": label,
            "logical_call": logical,
            "transport_attempt": 1,
            "provider_retries": 0,
            "profile": q03.MODEL_PROFILE,
            "resolved_model_expected": q03.MODEL_ID,
            "max_tokens": SOURCE_MAX_COMPLETION_TOKENS,
            "atomcode_live_timeout_seconds": ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS,
            "sampling_control": SAMPLING_CONTROL,
            "output_kind": SOURCE_OUTPUT_KIND,
            "allowed_tool": ALLOWED_TOOL,
            "prompt_sha256": sha256_text(prompt),
            "authorization_material_persisted": False,
        }
        request_sha = atomic_bytes(
            request_path,
            (json.dumps(safe, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(),
        )
        process = None
        stream_done = threading.Event()
        stream_errors: list[str] = []
        events: "queue.Queue[dict[str, Any]]" = queue.Queue()
        tool_names: list[str] = []
        token_events: list[dict[str, Any]] = []
        prohibited_tool: str | None = None
        error_message: str | None = None
        captured = False
        try:
            process, live_base, token = q03.start_daemon(
                atom_home=atom_home,
                workdir=live_workdir,
                log_path=call_root / "atomcode-daemon.log",
            )
            (atom_home / "mcp.json").write_text(
                json.dumps(q03.mcp_config(progress), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            q03.http_json(live_base, token, "/live/mode", method="POST", body={"mode": "build"})

            def stream() -> None:
                request = urllib.request.Request(live_base + "/live", headers={"Authorization": "Bearer " + token})
                try:
                    with urllib.request.urlopen(request, timeout=ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS + 30) as response:
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
                            q03.append_jsonl(response_path, event)
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
                raise RuntimeError("controlled output MCP catalog not ready")

            submit = q03.http_json(
                live_base,
                token,
                "/live/message",
                method="POST",
                body={"message": prompt, "provider": q03.MODEL_PROFILE, "client_input_id": f"c1-fresh4-source-{logical}"},
            )
            if submit.get("accepted") is not True:
                raise RuntimeError(f"live submit rejected: {submit}")

            deadline = time.time() + ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS
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
                    q03.http_json(
                        live_base,
                        token,
                        "/live/permission",
                        method="POST",
                        body={"decision": "allow" if allow else "deny", "tool_name": name},
                        timeout=10,
                    )
                    if not allow:
                        prohibited_tool = name
                        try: q03.http_json(live_base, token, "/live/stop", method="POST", body={}, timeout=10)
                        except Exception: pass
                        break
                elif kind == "tool_start":
                    name = str(event.get("name", "")); tool_names.append(name)
                    if name != ALLOWED_TOOL:
                        prohibited_tool = name
                        try: q03.http_json(live_base, token, "/live/stop", method="POST", body={}, timeout=10)
                        except Exception: pass
                        break
                    if len(tool_names) > 1:
                        error_message = "more_than_one_allowed_tool_call"
                        try: q03.http_json(live_base, token, "/live/stop", method="POST", body={}, timeout=10)
                        except Exception: pass
                        break
                elif kind == "tool_result" and str(event.get("name", "")) == ALLOWED_TOOL:
                    captured = True
                    try: q03.http_json(live_base, token, "/live/stop", method="POST", body={}, timeout=10)
                    except Exception: pass
                    break
                elif kind == "error":
                    error_message = str(event.get("message", "AtomCode live error")); break
                elif kind == "stream_exception":
                    error_message = str(event.get("message", "stream exception")); break
            else:
                error_message = "controlled_output_live_timeout"
                try: q03.http_json(live_base, token, "/live/stop", method="POST", body={}, timeout=10)
                except Exception: pass

            deadline = time.time() + 5
            while time.time() < deadline:
                if progress.is_file():
                    state = json.loads(progress.read_text(encoding="utf-8"))
                    if state.get("status") in {"OUTPUT_CAPTURED", "TOOL_CALL_CAP_EXCEEDED", "UNKNOWN_TOOL_ATTEMPT", "MALFORMED_OUTPUT"}:
                        break
                time.sleep(0.05)
            stream_done.set(); thread.join(timeout=2)
            state = json.loads(progress.read_text(encoding="utf-8")) if progress.is_file() else {}
            content = state.get("content") if state.get("status") == "OUTPUT_CAPTURED" else None
            model_round_count = len(token_events)
            self.prompt_tokens += sum(int(event.get("prompt", 0)) for event in token_events)
            self.output_tokens += sum(int(event.get("completion", 0)) for event in token_events)
            passed = (
                captured
                and prohibited_tool is None
                and error_message is None
                and tool_names == [ALLOWED_TOOL]
                and state.get("status") == "OUTPUT_CAPTURED"
                and state.get("call_count") == 1
                and state.get("kind") == SOURCE_OUTPUT_KIND
                and isinstance(content, str)
                and bool(content.strip())
                and model_round_count == 1
            )
        except Exception as exc:
            error_message = error_message or f"{type(exc).__name__}:{exc}"
            content = None
            model_round_count = len(token_events)
            passed = False
        finally:
            stream_done.set()
            if process is not None:
                q03.terminate_process(process)
            daemon_log = call_root / "atomcode-daemon.log"
            atomic_bytes(stderr_path, daemon_log.read_bytes() if daemon_log.is_file() else b"")
            if not response_path.exists():
                atomic_bytes(response_path, b"")

        stdout_sha = sha256_file(response_path)
        stderr_sha = sha256_file(stderr_path)
        receipt = {
            **safe,
            "request_sha256": request_sha,
            "stdout_sha256": stdout_sha,
            "stderr_sha256": stderr_sha,
            "persisted_before_parse": True,
            "parse_status": "CONTROLLED_OUTPUT_CAPTURED" if passed else "CONTROLLED_OUTPUT_FAILED",
            "tool_names": tool_names,
            "prohibited_tool": prohibited_tool,
            "error_message": error_message,
            "model_round_count": model_round_count,
            "codingplan_requests": model_round_count,
            "prompt_tokens": sum(int(event.get("prompt", 0)) for event in token_events),
            "completion_tokens": sum(int(event.get("completion", 0)) for event in token_events),
            "bridge_progress_sha256": sha256_file(progress) if progress.is_file() else None,
            "captured_content_sha256": sha256_text(content) if isinstance(content, str) else None,
            "model_content_observed": bool(content or token_events or tool_names),
            "pass": passed,
        }
        atomic_json(self.root / "calls" / f"{stem}.json", receipt)
        if not passed:
            raise RuntimeError("STOP_FRESH3_BRIDGE_SOURCE_FRESH4_CONTROLLED_OUTPUT_PROVIDER")
        return {"content": content, "provider": receipt}


def bind() -> None:
    base.AtomCodeSourceProvider = Fresh4ControlledSourceProvider
    base.PROVIDER_ID = PROVIDER_ID
    base.BRIDGE_SCHEMA = BRIDGE_SCHEMA
    base.SOURCE_MAX_COMPLETION_TOKENS = SOURCE_MAX_COMPLETION_TOKENS
    base.PACTA_FIRST_DECISION_BUDGET = PACTA_FIRST_DECISION_BUDGET
    base.ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS = ATOMCODE_SUBPROCESS_TIMEOUT_SECONDS
    base.SAMPLING_CONTROL = SAMPLING_CONTROL


def execute_trajectory(**kwargs: Any) -> dict[str, Any]:
    bind()
    return base.execute_trajectory(**kwargs)
