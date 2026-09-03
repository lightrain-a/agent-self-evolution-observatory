#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MCP_PROTOCOL_VERSION = "2025-11-25"
TOOL_NAME = "submit_output"
VALID_KINDS = {"bash_action", "text"}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def text_result(text: str, *, is_error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--progress", type=Path, required=True)
    args = parser.parse_args()
    progress = args.progress.resolve()
    call_count = 0

    def persist(status: str, **extra: Any) -> None:
        payload = {
            "schema_version": 1,
            "created_at_utc": now(),
            "status": status,
            "tool_name": TOOL_NAME,
            "tool_count": 1,
            "call_count": call_count,
            **extra,
        }
        atomic_json(progress, payload)

    persist("PROCESS_READY")
    for raw in sys.stdin:
        try:
            message = json.loads(raw)
        except Exception:
            continue
        method = message.get("method")
        request_id = message.get("id")
        if method == "initialize":
            persist("MCP_INITIALIZED")
            send({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "c1-controlled-output", "version": "1.0"},
                    "instructions": (
                        "This server is the only permitted output channel. Do not use host shell, filesystem, "
                        "web, coding, agent, AtomGit, or any other tools. Call submit_output exactly once."
                    ),
                },
            })
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            persist("TOOLS_LISTED")
            send({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [{
                        "name": TOOL_NAME,
                        "description": (
                            "Submit exactly one controlled model output without executing it. "
                            "Use kind=bash_action for a shell action string and kind=text for ordinary text."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "kind": {"type": "string", "enum": ["bash_action", "text"]},
                                "content": {"type": "string", "minLength": 1},
                            },
                            "required": ["kind", "content"],
                            "additionalProperties": False,
                        },
                        "annotations": {
                            "readOnlyHint": True,
                            "destructiveHint": False,
                            "idempotentHint": False,
                            "openWorldHint": False,
                        },
                    }]
                },
            })
        elif method == "tools/call":
            params = message.get("params") or {}
            name = str(params.get("name", ""))
            arguments = params.get("arguments") or {}
            if name != TOOL_NAME:
                persist("UNKNOWN_TOOL_ATTEMPT", attempted_tool=name)
                send({"jsonrpc": "2.0", "id": request_id, "result": text_result("Unknown tool", is_error=True)})
                continue
            call_count += 1
            if call_count != 1:
                persist("TOOL_CALL_CAP_EXCEEDED", attempted_tool=name)
                send({"jsonrpc": "2.0", "id": request_id, "result": text_result("Exactly one output is allowed", is_error=True)})
                continue
            kind = arguments.get("kind")
            content = arguments.get("content")
            if kind not in VALID_KINDS or not isinstance(content, str) or not content.strip():
                persist("MALFORMED_OUTPUT", kind=kind, content_type=type(content).__name__)
                send({"jsonrpc": "2.0", "id": request_id, "result": text_result("Malformed output", is_error=True)})
                continue
            persist(
                "OUTPUT_CAPTURED",
                kind=kind,
                content=content,
                content_sha256=sha_text(content),
                content_bytes=len(content.encode("utf-8")),
            )
            send({"jsonrpc": "2.0", "id": request_id, "result": text_result("OUTPUT_ACCEPTED")})
        elif request_id is not None:
            send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "method not found"}})


if __name__ == "__main__":
    main()
