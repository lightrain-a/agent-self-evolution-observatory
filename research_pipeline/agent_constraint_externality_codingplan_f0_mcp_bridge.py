from __future__ import annotations

import argparse
import json
import os
import signal
import sys
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    prepare_appworld_runtime_root,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.appworld_constraint_compiler import load_protected_spec

MCP_PROTOCOL_VERSION = "2025-11-25"


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
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


def _text_result(text: str, *, is_error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def _tool_annotation(name: str) -> dict[str, bool]:
    leaf = name.split("__", 1)[-1]
    read_only = leaf.startswith(("show_", "search_", "directory_exists", "file_exists", "get_", "list_", "check_"))
    return {"readOnlyHint": read_only, "destructiveHint": not read_only}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appworld-root", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--family-id", required=True)
    parser.add_argument("--coupling-level", choices=["INDEPENDENT", "LOW", "HIGH"], required=True)
    parser.add_argument("--instruction-file", type=Path, required=True)
    parser.add_argument("--source-target-only", action="store_true")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--trajectory", type=Path, required=True)
    parser.add_argument("--tool-call-cap", type=int, required=True)
    args = parser.parse_args()

    instruction = args.instruction_file.read_text(encoding="utf-8")
    spec = load_protected_spec(args.bundle)
    family = next(row for row in spec["families"] if row["family_id"] == args.family_id)
    base_arm = next(row for row in family["arms"] if row["coupling_level"] == args.coupling_level)
    arm = dict(base_arm)
    arm["task_instruction"] = instruction
    if args.source_target_only:
        arm["constraints"] = [row for row in base_arm["constraints"] if row["role"] == "TARGET"]
    materialized = prepare_appworld_runtime_root(
        args.appworld_root,
        args.runtime_root,
        family=family,
        arm=arm,
        task_id=args.task_id,
    )
    world = AppWorldToolWorld(
        runtime_root=args.runtime_root,
        task_id=args.task_id,
        experiment_name=args.experiment_name,
        seed=args.seed,
        allowed_apps=set(family["fixture"]["apps"]),
        max_interactions=args.tool_call_cap,
    )
    tools_by_name = {row["name"]: row for row in world.tools}
    call_count = 0
    closed = False

    def persist(status: str, **extra: Any) -> None:
        payload: dict[str, Any] = {
            "schema_version": "ace-codingplan-f0-appworld-mcp-progress-v1",
            "family_id": args.family_id,
            "coupling_level": args.coupling_level,
            "source_target_only": args.source_target_only,
            "seed": args.seed,
            "task_id": args.task_id,
            "status": status,
            "tool_call_count": call_count,
            "tool_call_cap": args.tool_call_cap,
            "source_db_root": str(world.source_db_root),
            "changes_db_root": str(world.output_db_root),
            "initial_snapshot_sha256": materialized["initial_snapshot_sha256"],
            "instruction_sha256": materialized["instruction_sha256"],
            **extra,
        }
        payload["content_sha256"] = sha256_value(payload)
        _write_json_atomic(args.progress, payload)

    def close_world(*_: Any) -> None:
        nonlocal closed
        if closed:
            return
        closed = True
        try:
            world.save_state()
            persist("CLOSED_STATE_SAVED")
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
    persist("PROCESS_READY", tool_count=len(tools_by_name))

    try:
        for line in sys.stdin:
            try:
                message = json.loads(line)
            except Exception:
                continue
            method = message.get("method")
            request_id = message.get("id")
            if method == "initialize":
                persist("MCP_INITIALIZED", tool_count=len(tools_by_name))
                _send({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": MCP_PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "ace-f0-appworld", "version": "1.0"},
                        "instructions": "Use only these AppWorld task-environment tools. Preserve unrelated state.",
                    },
                })
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                tools = [
                    {
                        "name": row["name"],
                        "description": row.get("description", ""),
                        "inputSchema": row["parameters"],
                        "annotations": _tool_annotation(row["name"]),
                    }
                    for row in world.tools
                ]
                persist("TOOLS_LISTED", tool_count=len(tools))
                _send({"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}})
            elif method == "tools/call":
                params = message.get("params") or {}
                name = str(params.get("name", ""))
                arguments = params.get("arguments") or {}
                if name not in tools_by_name:
                    _send({"jsonrpc": "2.0", "id": request_id, "result": _text_result(f"Unknown AppWorld tool: {name}", is_error=True)})
                    continue
                call_count += 1
                if call_count > args.tool_call_cap:
                    _append_jsonl(args.trajectory, {
                        "index": call_count,
                        "tool_name": name,
                        "arguments": arguments,
                        "arguments_sha256": sha256_value(arguments),
                        "executed": False,
                        "failure": "TOOL_CALL_CAP_EXCEEDED",
                    })
                    persist("TOOL_CALL_CAP_EXCEEDED", attempted_tool=name)
                    _send({"jsonrpc": "2.0", "id": request_id, "result": _text_result("AppWorld tool-call cap exceeded.", is_error=True)})
                    continue
                try:
                    output = world.execute(name, dict(arguments))
                    world.save_state()
                    text = str(output)
                    is_error = text.lstrip().startswith("Execution failed")
                    _append_jsonl(args.trajectory, {
                        "index": call_count,
                        "tool_name": name,
                        "arguments": arguments,
                        "arguments_sha256": sha256_value(arguments),
                        "executed": True,
                        "result": text,
                        "result_sha256": sha256_value(text),
                        "result_error": is_error,
                    })
                    persist("STATE_SAVED_AFTER_TOOL", last_tool=name, last_tool_arguments_sha256=sha256_value(arguments), last_tool_result_error=is_error)
                    _send({"jsonrpc": "2.0", "id": request_id, "result": _text_result(text, is_error=is_error)})
                except Exception as exc:
                    try:
                        world.save_state()
                    except Exception:
                        pass
                    _append_jsonl(args.trajectory, {
                        "index": call_count,
                        "tool_name": name,
                        "arguments": arguments,
                        "arguments_sha256": sha256_value(arguments),
                        "executed": True,
                        "failure_class": type(exc).__name__,
                        "failure_message": str(exc)[:300],
                    })
                    persist("TOOL_EXECUTION_FAILED", last_tool=name, last_tool_arguments_sha256=sha256_value(arguments), failure_class=type(exc).__name__, message=str(exc)[:300])
                    _send({"jsonrpc": "2.0", "id": request_id, "result": _text_result(f"{type(exc).__name__}: {exc}", is_error=True)})
            elif request_id is not None:
                _send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "method not found"}})
    finally:
        close_world()


if __name__ == "__main__":
    main()
