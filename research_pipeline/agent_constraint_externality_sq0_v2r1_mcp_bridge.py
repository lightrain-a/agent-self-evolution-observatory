from __future__ import annotations

import argparse
import json
import os
import signal
import sys
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld
from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.agent_constraint_externality_sq0_v2r1_build import load_cases
from research_pipeline.agent_constraint_externality_sq0_build import materialize_case

MCP_PROTOCOL_VERSION = "2025-11-25"


def _write_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _text(text: str, error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": error}


def _annotation(name: str) -> dict[str, bool]:
    leaf = name.split("__", 1)[-1]
    read_only = leaf.startswith(("show_", "search_", "get_", "list_", "check_", "directory_exists", "file_exists"))
    return {"readOnlyHint": read_only, "destructiveHint": not read_only}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--case-id", required=True)
    p.add_argument("--runtime-root", type=Path, required=True)
    p.add_argument("--task-id", required=True)
    p.add_argument("--experiment-name", required=True)
    p.add_argument("--progress", type=Path, required=True)
    p.add_argument("--tool-call-cap", type=int, required=True)
    args = p.parse_args()
    case = next((r for r in load_cases(args.bundle) if r["case_id"] == args.case_id), None)
    if case is None:
        raise SystemExit("Unknown SQ0 case")
    materialized = materialize_case(case, args.runtime_root, args.task_id)
    world = AppWorldToolWorld(runtime_root=args.runtime_root, task_id=args.task_id, experiment_name=args.experiment_name, seed=1, allowed_apps=set(case["fixture"]["apps"]), max_interactions=args.tool_call_cap)
    tools = {row["name"]: row for row in world.tools}
    calls = 0
    closed = False

    def persist(status: str, **extra: Any) -> None:
        payload = {"schema_version": "ace-sq0-v2r1-mcp-progress-v1", "case_id": args.case_id, "task_id": args.task_id, "status": status,
            "tool_call_count": calls, "tool_call_cap": args.tool_call_cap, "source_db_root": str(world.source_db_root), "changes_db_root": str(world.output_db_root),
            "initial_snapshot_sha256": materialized["initial_snapshot_sha256"], "instruction_sha256": materialized["instruction_sha256"], **extra}
        payload["content_sha256"] = sha256_value(payload); _write_atomic(args.progress, payload)

    def close_world(*_: Any) -> None:
        nonlocal closed
        if closed: return
        closed = True
        try:
            world.save_state(); persist("CLOSED_STATE_SAVED")
        except Exception as exc:
            try: persist("CLOSE_SAVE_FAILED", failure_class=type(exc).__name__, message=str(exc)[:300])
            except Exception: pass
        finally:
            try: world.close()
            except Exception: pass

    signal.signal(signal.SIGTERM, lambda *_: (close_world(), sys.exit(0)))
    signal.signal(signal.SIGINT, lambda *_: (close_world(), sys.exit(0)))
    persist("PROCESS_READY", tool_count=len(tools))
    try:
        for line in sys.stdin:
            try: msg = json.loads(line)
            except Exception: continue
            method, rid = msg.get("method"), msg.get("id")
            if method == "initialize":
                persist("MCP_INITIALIZED", tool_count=len(tools))
                _send({"jsonrpc":"2.0","id":rid,"result":{"protocolVersion":MCP_PROTOCOL_VERSION,"capabilities":{"tools":{}},"serverInfo":{"name":"ace-sq0-v2r1-appworld","version":"1.0"},"instructions":"Use only these AppWorld tools to complete the target-local SQ0-V2R1 task. Do not use host tools."}})
            elif method == "notifications/initialized": continue
            elif method == "tools/list":
                rows=[{"name":r["name"],"description":r.get("description",""),"inputSchema":r["parameters"],"annotations":_annotation(r["name"])} for r in world.tools]
                persist("TOOLS_LISTED", tool_count=len(rows)); _send({"jsonrpc":"2.0","id":rid,"result":{"tools":rows}})
            elif method == "tools/call":
                params=msg.get("params") or {}; name=str(params.get("name","")); arguments=params.get("arguments") or {}
                if name not in tools:
                    _send({"jsonrpc":"2.0","id":rid,"result":_text(f"Unknown AppWorld tool: {name}",True)}); continue
                calls += 1
                if calls > args.tool_call_cap:
                    persist("TOOL_CALL_CAP_EXCEEDED", attempted_tool=name); _send({"jsonrpc":"2.0","id":rid,"result":_text("AppWorld tool-call cap exceeded.",True)}); continue
                try:
                    output=world.execute(name,dict(arguments)); world.save_state(); err=str(output).lstrip().startswith("Execution failed")
                    persist("STATE_SAVED_AFTER_TOOL",last_tool=name,last_tool_arguments_sha256=sha256_value(arguments),last_tool_result_error=err)
                    _send({"jsonrpc":"2.0","id":rid,"result":_text(str(output),err)})
                except Exception as exc:
                    try: world.save_state()
                    except Exception: pass
                    persist("TOOL_EXECUTION_FAILED",last_tool=name,last_tool_arguments_sha256=sha256_value(arguments),failure_class=type(exc).__name__,message=str(exc)[:300])
                    _send({"jsonrpc":"2.0","id":rid,"result":_text(f"{type(exc).__name__}: {exc}",True)})
            elif rid is not None:
                _send({"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":"method not found"}})
    finally: close_world()


if __name__ == "__main__": main()
