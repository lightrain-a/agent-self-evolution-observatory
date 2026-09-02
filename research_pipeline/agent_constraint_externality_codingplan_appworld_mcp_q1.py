from __future__ import annotations

import json
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_codingplan_prereg import (
    MODEL_PROFILE,
    Q1_OUTPUT,
    V4_BUNDLE,
)
from research_pipeline.agent_constraint_externality_codingplan_qwen38_capability import (
    http_json,
    mcp_config,
    prepare_unit_runtime,
    start_daemon,
    terminate_process,
    units,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID,
    sha256_file,
    sha256_value,
)

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_SOURCE = ROOT / "research_pipeline/agent_constraint_externality_codingplan_mcp_bridge.py"
RUNNER_SOURCE = ROOT / "research_pipeline/agent_constraint_externality_codingplan_qwen38_capability.py"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def codingplan_used(base: str, token: str) -> int:
    summary = http_json(base, token, "/codingplan/usage/summary")
    return int(summary["primary_window"]["used"])


def qualify() -> dict[str, Any]:
    unit = units()[0]
    with tempfile.TemporaryDirectory(prefix="ace-codingplan-q1-") as directory:
        root = Path(directory)
        atom_home, workdir, progress, payload = prepare_unit_runtime(
            unit=unit,
            unit_root=root,
        )
        process = None
        stream_done = threading.Event()
        stream_error: list[str] = []
        try:
            process, base, token = start_daemon(
                atom_home=atom_home,
                workdir=workdir,
                log_path=root / "atomcode-daemon.log",
            )
            # Same scientific protocol as A0: the daemon boots without MCP, then the
            # isolated user-level MCP config is activated before GET /live creates
            # the session runtime. No /live/message call is permitted in Q1.
            (atom_home / "mcp.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            http_json(base, token, "/live/mode", method="POST", body={"mode": "build"})
            used_before = codingplan_used(base, token)

            def stream() -> None:
                request = urllib.request.Request(
                    base + "/live",
                    headers={"Authorization": "Bearer " + token},
                )
                try:
                    with urllib.request.urlopen(request, timeout=60) as response:
                        for _ in response:
                            if stream_done.is_set():
                                break
                except Exception as exc:  # connection closure after /live/stop is acceptable
                    if not stream_done.is_set():
                        stream_error.append(f"{type(exc).__name__}: {exc}")

            thread = threading.Thread(target=stream, daemon=True)
            thread.start()
            deadline = time.time() + 45
            while time.time() < deadline:
                if stream_error:
                    raise RuntimeError(stream_error[-1])
                if progress.is_file():
                    state = json.loads(progress.read_text(encoding="utf-8"))
                    if state.get("status") == "TOOLS_LISTED":
                        break
                time.sleep(0.1)
            else:
                raise RuntimeError("Q1 live session did not list AppWorld MCP tools.")

            # AtomCode 5.0.9 may return an empty body for /live/snapshot; the
            # stronger evidence is that the live session actually requested the
            # AppWorld MCP catalog (TOOLS_LISTED) before any /live/message call.
            used_after = codingplan_used(base, token)
            http_json(base, token, "/live/stop", method="POST", body={})
            stream_done.set()
            thread.join(timeout=2)

            state = json.loads(progress.read_text(encoding="utf-8"))
            payload_out: dict[str, Any] = {
                "schema_version": "ace-codingplan-appworld-mcp-q1-predispatch-v2",
                "object_id": OBJECT_ID,
                "status": "CODINGPLAN_APPWORLD_MCP_LIVE_PREDISPATCH_PASS",
                "atomcode_version": "5.0.9",
                "model_profile": MODEL_PROFILE,
                "appworld_bundle": V4_BUNDLE.name,
                "appworld_bundle_sha256": sha256_file(V4_BUNDLE),
                "bridge_source_sha256": sha256_file(BRIDGE_SOURCE),
                "runner_source_sha256": sha256_file(RUNNER_SOURCE),
                "protocol": (
                    "DAEMON_BOOT_WITHOUT_MCP_THEN_ACTIVATE_USER_MCP_THEN_GET_LIVE_"
                    "WAIT_TOOLS_LISTED_BEFORE_DISPATCH"
                ),
                "session_mcp_progress_status": state.get("status"),
                "session_mcp_tool_count": state.get("tool_count"),
                "live_session_seen": True,
                "scientific_dispatch_sent": False,
                "codingplan_model_requests": used_after - used_before,
                "codingplan_window_used_before": used_before,
                "codingplan_window_used_after": used_after,
                "scientific_outcomes_observed": 0,
            }
            if payload_out["codingplan_model_requests"] != 0:
                raise RuntimeError("Q1 predispatch qualification consumed a CodingPlan model request.")
            if payload_out["session_mcp_progress_status"] != "TOOLS_LISTED":
                raise RuntimeError("Q1 AppWorld MCP tools were not listed.")
            if not payload_out["live_session_seen"]:
                raise RuntimeError("Q1 live session was unavailable.")
            payload_out["content_sha256"] = sha256_value(payload_out)
            return payload_out
        finally:
            stream_done.set()
            if process is not None:
                terminate_process(process)


def main() -> None:
    payload = qualify()
    write_json(Q1_OUTPUT, payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "codingplan_model_requests": payload["codingplan_model_requests"],
                "mcp_tool_count": payload["session_mcp_tool_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
