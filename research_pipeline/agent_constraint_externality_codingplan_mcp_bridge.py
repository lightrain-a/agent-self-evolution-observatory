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


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def text_result(text: str, *, is_error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def tool_annotation(name: str) -> dict[str, bool]:
    leaf = name.split("__", 1)[-1]
    read_only_prefixes = (
        "show_", "search_", "directory_exists", "file_exists", "get_", "list_", "check_"
    )
    read_only = leaf.startswith(read_only_prefixes)
    return {"readOnlyHint": read_only, "destructiveHint": not read_only}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appworld-root", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--family-id", required=True)
    parser.add_argument("--repeat", type=int, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--tool-call-cap", type=int, required=True)
    args = parser.parse_args()

    spec = load_protected_spec(args.bundle)
    family = next(row for row in spec["families"] if row["family_id"] == args.family_id)
    arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
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
        seed=1100 + args.repeat,
        allowed_apps=set(family["fixture"]["apps"]),
        max_interactions=args.tool_call_cap,
    )
    tools_by_name = {row["name"]: row for row in world.tools}
    call_count = 0
    closed = False

    def persist(status: str, **extra: Any) -> None:
        payload: dict[str, Any] = {
            "schema_version": "ace-codingplan-appworld-mcp-progress-v1",
            "family_id": args.family_id,
            "repeat": args.repeat,
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
        write_json_atomic(args.progress, payload)

    def close_world(*_: Any) -> None:
        nonlocal closed
        if closed:
            return
        closed = True
        try:
            world.save_state()
            persist("CLOSED_STATE_SAVED")
        except Exception as exc:  # best-effort terminal durability; never print secrets
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
                send({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": MCP_PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "ace-appworld", "version": "1.0"},
                        "instructions": (
                            "These are the only task-environment tools. Use AppWorld tools to complete "
                            "the user's task; do not use host coding, shell, filesystem, web, agent, or AtomGit tools."
                        ),
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
                        "annotations": tool_annotation(row["name"]),
                    }
                    for row in world.tools
                ]
                persist("TOOLS_LISTED", tool_count=len(tools))
                send({"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}})
            elif method == "tools/call":
                params = message.get("params") or {}
                name = str(params.get("name", ""))
                arguments = params.get("arguments") or {}
                if name not in tools_by_name:
                    send({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": text_result(f"Unknown AppWorld tool: {name}", is_error=True),
                    })
                    continue
                call_count += 1
                if call_count > args.tool_call_cap:
                    persist("TOOL_CALL_CAP_EXCEEDED", attempted_tool=name)
                    send({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": text_result("AppWorld tool-call cap exceeded.", is_error=True),
                    })
                    continue
                try:
                    output = world.execute(name, dict(arguments))
                    # Scientific durability: persist AppWorld's official changes after every tool.
                    world.save_state()
                    is_error = str(output).lstrip().startswith("Execution failed")
                    persist(
                        "STATE_SAVED_AFTER_TOOL",
                        last_tool=name,
                        last_tool_arguments_sha256=sha256_value(arguments),
                        last_tool_result_error=is_error,
                    )
                    send({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": text_result(str(output), is_error=is_error),
                    })
                except Exception as exc:
                    try:
                        world.save_state()
                    except Exception:
                        pass
                    persist(
                        "TOOL_EXECUTION_FAILED",
                        last_tool=name,
                        last_tool_arguments_sha256=sha256_value(arguments),
                        failure_class=type(exc).__name__,
                        message=str(exc)[:300],
                    )
                    send({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": text_result(f"{type(exc).__name__}: {exc}", is_error=True),
                    })
            elif request_id is not None:
                send({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": "method not found"},
                })
    finally:
        close_world()


if __name__ == "__main__":
    main()
