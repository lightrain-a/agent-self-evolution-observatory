from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld
from research_pipeline.agent_constraint_externality_runner_core import sha256_file, sha256_value

SERVER_NAME = "ace-appworld"
SERVER_VERSION = "1"
DEFAULT_PROTOCOL = "2024-11-05"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def send(value: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def mcp_tools(world: AppWorldToolWorld) -> list[dict[str, Any]]:
    return [
        {
            "name": row["name"],
            "description": row.get("description", ""),
            "inputSchema": row["parameters"],
        }
        for row in world.tools
    ]


class ScientificAppWorldMcpServer:
    def __init__(
        self,
        *,
        runtime_root: Path,
        task_id: str,
        experiment_name: str,
        seed: int,
        allowed_apps: set[str],
        tool_call_cap: int,
        state_manifest: Path,
        initial_snapshot_sha256: str,
        instruction_sha256: str,
        family_id: str,
    ) -> None:
        self.runtime_root = runtime_root
        self.task_id = task_id
        self.experiment_name = experiment_name
        self.tool_call_cap = tool_call_cap
        self.state_manifest = state_manifest
        self.initial_snapshot_sha256 = initial_snapshot_sha256
        self.instruction_sha256 = instruction_sha256
        self.family_id = family_id
        self.tool_call_count = 0
        self.cap_reached = False
        self.executed_tool_names: list[str] = []
        with contextlib.redirect_stdout(sys.stderr):
            self.world = AppWorldToolWorld(
                runtime_root=runtime_root,
                task_id=task_id,
                experiment_name=experiment_name,
                seed=seed,
                allowed_apps=allowed_apps,
                max_interactions=tool_call_cap,
            )
            # Ensure no-op changes files exist even if the model never calls a tool.
            self.world.save_state()
        self.allowed_tool_names = {row["name"] for row in self.world.tools}
        self._persist_state(status="READY")

    def _persist_state(self, *, status: str) -> None:
        output_root = self.world.output_db_root
        changes = {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in sorted(output_root.glob("*.jsonl"))
        }
        payload: dict[str, Any] = {
            "schema_version": "ace-codingplan-appworld-mcp-state-v1",
            "status": status,
            "family_id": self.family_id,
            "task_id": self.task_id,
            "experiment_name": self.experiment_name,
            "runtime_root": str(self.runtime_root),
            "source_db_root": str(self.world.source_db_root),
            "changes_db_root": str(output_root),
            "initial_snapshot_sha256": self.initial_snapshot_sha256,
            "instruction_sha256": self.instruction_sha256,
            "tool_call_cap": self.tool_call_cap,
            "tool_call_count": self.tool_call_count,
            "cap_reached": self.cap_reached,
            "executed_tool_names": list(self.executed_tool_names),
            "changes": changes,
        }
        payload["content_sha256"] = sha256_value(payload)
        write_json(self.state_manifest, payload)

    def list_tools(self) -> list[dict[str, Any]]:
        return mcp_tools(self.world)

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in self.allowed_tool_names:
            return {
                "content": [{"type": "text", "text": f"Unknown AppWorld tool: {name}"}],
                "isError": True,
            }
        if self.tool_call_count >= self.tool_call_cap:
            self.cap_reached = True
            self._persist_state(status="TOOL_CALL_CAP_REACHED")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Scientific AppWorld tool-call cap ({self.tool_call_cap}) reached; "
                            "no additional AppWorld action was executed."
                        ),
                    }
                ],
                "isError": True,
            }
        self.tool_call_count += 1
        self.executed_tool_names.append(name)
        try:
            with contextlib.redirect_stdout(sys.stderr):
                output = self.world.execute(name, arguments)
                self.world.save_state()
            self._persist_state(status="RUNNING")
            return {
                "content": [{"type": "text", "text": str(output)}],
                "isError": False,
            }
        except Exception as exc:  # retain exact-once state; never retry the action.
            with contextlib.suppress(Exception):
                with contextlib.redirect_stdout(sys.stderr):
                    self.world.save_state()
            self._persist_state(status="TOOL_EXECUTION_ERROR")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"AppWorld tool execution failed: {type(exc).__name__}: {str(exc)[:500]}",
                    }
                ],
                "isError": True,
            }

    def close(self) -> None:
        with contextlib.suppress(Exception):
            with contextlib.redirect_stdout(sys.stderr):
                self.world.save_state()
        self._persist_state(status="CLOSED")
        with contextlib.suppress(Exception):
            with contextlib.redirect_stdout(sys.stderr):
                self.world.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--allowed-app", action="append", default=[])
    parser.add_argument("--tool-call-cap", type=int, required=True)
    parser.add_argument("--state-manifest", type=Path, required=True)
    parser.add_argument("--initial-snapshot-sha256", required=True)
    parser.add_argument("--instruction-sha256", required=True)
    parser.add_argument("--family-id", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ScientificAppWorldMcpServer(
        runtime_root=args.runtime_root,
        task_id=args.task_id,
        experiment_name=args.experiment_name,
        seed=args.seed,
        allowed_apps=set(args.allowed_app),
        tool_call_cap=args.tool_call_cap,
        state_manifest=args.state_manifest,
        initial_snapshot_sha256=args.initial_snapshot_sha256,
        instruction_sha256=args.instruction_sha256,
        family_id=args.family_id,
    )
    try:
        for line in sys.stdin:
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(request, dict) or "id" not in request:
                continue
            request_id = request["id"]
            method = request.get("method")
            try:
                if method == "initialize":
                    version = (
                        request.get("params", {}).get("protocolVersion") or DEFAULT_PROTOCOL
                    )
                    result = {
                        "protocolVersion": version,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    }
                elif method == "tools/list":
                    result = {"tools": server.list_tools()}
                elif method == "tools/call":
                    params = request.get("params") or {}
                    name = params.get("name")
                    arguments = params.get("arguments") or {}
                    if not isinstance(name, str) or not isinstance(arguments, dict):
                        result = {
                            "content": [{"type": "text", "text": "Malformed tools/call."}],
                            "isError": True,
                        }
                    else:
                        result = server.call_tool(name, arguments)
                elif method == "ping":
                    result = {}
                else:
                    result = {}
                send({"jsonrpc": "2.0", "id": request_id, "result": result})
            except Exception as exc:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32000,
                            "message": f"{type(exc).__name__}: {str(exc)[:500]}",
                        },
                    }
                )
    finally:
        server.close()


if __name__ == "__main__":
    main()
