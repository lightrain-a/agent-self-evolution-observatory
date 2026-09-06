from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_build import OUTPUT_BUNDLE as FROZEN_BUNDLE, load_dev_spec
from research_pipeline.agent_constraint_externality_runner_core import sha256_file, sha256_value
import research_pipeline.agent_constraint_externality_sq0_build as sq0_build

MCP_PROTOCOL_VERSION = "2025-11-25"
SCHEMA_VERSION = "ace-atomgit-repeat-dev-source-mcp-progress-v1"
TRAJECTORY_SCHEMA = "ace-atomgit-repeat-dev-source-trajectory-v1"
APPWORLD_SUBSTRATE = Path(
    "/data/wyt/agent-self-evolution-observatory/worktrees/agent-constraint-externality-20260831/cache/substrates/appworld-official-20260831"
)
APPWORLD_VERSION_SHA256 = "911fc0c48cb0c70601db5775a9bef1b740dc4cc9f9b46389b9f0563fe7eb94d7"


def _write_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", buffering=1) as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _text(text: str, *, error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": error}


def _annotation(name: str) -> dict[str, bool]:
    leaf = name.split("__", 1)[-1]
    read_only = leaf.startswith(("show_", "search_", "get_", "list_", "check_", "directory_exists", "file_exists"))
    return {"readOnlyHint": read_only, "destructiveHint": not read_only}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--family-id", required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--trajectory", type=Path, required=True)
    parser.add_argument("--tool-call-cap", type=int, required=True)
    args = parser.parse_args()

    if sha256_file(args.bundle) != sha256_file(FROZEN_BUNDLE):
        raise SystemExit("Repeat-development protected bundle SHA drift")
    spec = load_dev_spec()
    family = next((row for row in spec["families"] if row["family_id"] == args.family_id), None)
    if family is None:
        raise SystemExit("Unknown repeat-development family")
    case = family["source_case"]

    version_path = APPWORLD_SUBSTRATE / "data" / "version.txt"
    if not version_path.is_file() or sha256_file(version_path) != APPWORLD_VERSION_SHA256:
        raise SystemExit("Frozen AppWorld substrate identity mismatch")
    sq0_build.APPWORLD_ROOT = APPWORLD_SUBSTRATE
    materialized = sq0_build.materialize_case(case, args.runtime_root, args.task_id)
    world = AppWorldToolWorld(
        runtime_root=args.runtime_root,
        task_id=args.task_id,
        experiment_name=args.experiment_name,
        seed=1,
        allowed_apps=set(case["fixture"]["apps"]),
        max_interactions=args.tool_call_cap,
    )
    tools = {row["name"]: row for row in world.tools}
    calls = 0
    closed = False

    def persist(status: str, **extra: Any) -> None:
        payload: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "family_id": args.family_id,
            "case_id": case["case_id"],
            "task_id": args.task_id,
            "status": status,
            "tool_call_count": calls,
            "tool_call_cap": args.tool_call_cap,
            "source_db_root": str(world.source_db_root),
            "changes_db_root": str(world.output_db_root),
            "initial_snapshot_sha256": materialized["initial_snapshot_sha256"],
            "instruction_sha256": materialized["instruction_sha256"],
            "trajectory_path": str(args.trajectory),
            **extra,
        }
        payload["content_sha256"] = sha256_value(payload)
        _write_atomic(args.progress, payload)

    def close_world(*_: Any) -> None:
        nonlocal closed
        if closed:
            return
        closed = True
        try:
            world.save_state()
            persist("CLOSED_STATE_SAVED", trajectory_sha256=sha256_file(args.trajectory) if args.trajectory.is_file() else None)
        except Exception as exc:
            try:
                persist("CLOSE_SAVE_FAILED", failure_class=type(exc).__name__, message=str(exc)[:300])
            except Exception:
                pass
        finally:
            try:
                world.close()
            except Exception:
                pass

    signal.signal(signal.SIGTERM, lambda *_: (close_world(), sys.exit(0)))
    signal.signal(signal.SIGINT, lambda *_: (close_world(), sys.exit(0)))
    persist("PROCESS_READY", tool_count=len(tools))

    try:
        for line in sys.stdin:
            try:
                message = json.loads(line)
            except Exception:
                continue
            method, request_id = message.get("method"), message.get("id")
            if method == "initialize":
                persist("MCP_INITIALIZED", tool_count=len(tools))
                _send({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": MCP_PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "ace-repeat-dev-source-appworld", "version": "1.0"},
                        "instructions": "Use only these AppWorld tools to complete the target-only development source task. Do not use host tools.",
                    },
                })
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                rows = [
                    {
                        "name": row["name"],
                        "description": row.get("description", ""),
                        "inputSchema": row["parameters"],
                        "annotations": _annotation(row["name"]),
                    }
                    for row in world.tools
                ]
                persist("TOOLS_LISTED", tool_count=len(rows))
                _send({"jsonrpc": "2.0", "id": request_id, "result": {"tools": rows}})
            elif method == "tools/call":
                params = message.get("params") or {}
                name = str(params.get("name", ""))
                arguments = params.get("arguments") or {}
                if name not in tools:
                    _send({"jsonrpc": "2.0", "id": request_id, "result": _text(f"Unknown AppWorld tool: {name}", error=True)})
                    continue
                calls += 1
                tool_id = f"{args.family_id}:tool:{calls}"
                dispatch = {
                    "schema_version": TRAJECTORY_SCHEMA,
                    "event": "TOOL_DISPATCH",
                    "tool_id": tool_id,
                    "index": calls,
                    "tool_name": name,
                    "arguments": arguments,
                    "arguments_sha256": sha256_value(arguments),
                    "time_ns": time.time_ns(),
                }
                _append_jsonl(args.trajectory, dispatch)
                if calls > args.tool_call_cap:
                    _append_jsonl(args.trajectory, {
                        "schema_version": TRAJECTORY_SCHEMA,
                        "event": "TOOL_REJECTED",
                        "tool_id": tool_id,
                        "index": calls,
                        "reason": "TOOL_CALL_CAP_EXCEEDED",
                        "time_ns": time.time_ns(),
                    })
                    persist("TOOL_CALL_CAP_EXCEEDED", attempted_tool=name, trajectory_sha256=sha256_file(args.trajectory))
                    _send({"jsonrpc": "2.0", "id": request_id, "result": _text("AppWorld tool-call cap exceeded.", error=True)})
                    continue
                try:
                    output = world.execute(name, dict(arguments))
                    world.save_state()
                    text = str(output)
                    is_error = text.lstrip().startswith("Execution failed")
                    _append_jsonl(args.trajectory, {
                        "schema_version": TRAJECTORY_SCHEMA,
                        "event": "TOOL_COMPLETION",
                        "tool_id": tool_id,
                        "index": calls,
                        "tool_name": name,
                        "result": text,
                        "result_sha256": sha256_value(text),
                        "result_error": is_error,
                        "time_ns": time.time_ns(),
                    })
                    persist(
                        "STATE_SAVED_AFTER_TOOL",
                        last_tool=name,
                        last_tool_arguments_sha256=sha256_value(arguments),
                        last_tool_result_error=is_error,
                        trajectory_sha256=sha256_file(args.trajectory),
                    )
                    _send({"jsonrpc": "2.0", "id": request_id, "result": _text(text, error=is_error)})
                except Exception as exc:
                    try:
                        world.save_state()
                    except Exception:
                        pass
                    _append_jsonl(args.trajectory, {
                        "schema_version": TRAJECTORY_SCHEMA,
                        "event": "TOOL_COMPLETION",
                        "tool_id": tool_id,
                        "index": calls,
                        "tool_name": name,
                        "failure_class": type(exc).__name__,
                        "failure_message": str(exc)[:300],
                        "result_error": True,
                        "time_ns": time.time_ns(),
                    })
                    persist(
                        "TOOL_EXECUTION_FAILED",
                        last_tool=name,
                        last_tool_arguments_sha256=sha256_value(arguments),
                        failure_class=type(exc).__name__,
                        message=str(exc)[:300],
                        trajectory_sha256=sha256_file(args.trajectory),
                    )
                    _send({"jsonrpc": "2.0", "id": request_id, "result": _text(f"{type(exc).__name__}: {exc}", error=True)})
            elif request_id is not None:
                _send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "method not found"}})
    finally:
        close_world()


if __name__ == "__main__":
    main()
