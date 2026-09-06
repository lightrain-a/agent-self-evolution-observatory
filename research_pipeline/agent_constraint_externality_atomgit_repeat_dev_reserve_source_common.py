from __future__ import annotations

import json
import os
import shutil
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_dev_source as src
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_reserve_build import (
    CONTRACT_OUTPUT as RESERVE_CONTRACT,
    OUTPUT_BUNDLE,
    QUAL_OUTPUT as RESERVE_QUAL,
    load_reserve_spec,
)
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_PYTHON = src.APPWORLD_PYTHON
MODEL_PROFILE = src.MODEL_PROFILE
MODEL_ID = src.MODEL_ID
PROVIDER = src.PROVIDER
BASE_URL = src.BASE_URL
MODEL_ROUND_CAP = src.MODEL_ROUND_CAP
TOOL_CALL_CAP = src.TOOL_CALL_CAP
SHARED_RESERVE = 100
MIN_REMAINING = MODEL_ROUND_CAP + SHARED_RESERVE + 5
EXECUTION_ID = "ACE-ATOMGIT-REPEAT-DEV-RESERVE-SOURCE-20260906"
BRIDGE = ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_dev_reserve_source_mcp_bridge.py"
PROTOCOL_AUDIT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-protocol-audit-20260906.json"
Q1_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-q1-20260906.json"
PREFLIGHT_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-preflight-20260906.json"
READINESS_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-readiness-20260906.json"
AUTH_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-human-authorization-20260906.json"
EXEC_CONTRACT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-execution-contract-20260906.json"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-result-20260906.json"
OP_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-operational-state-20260906.json"
RUN_ROOT = Path("/data/wyt/agent-constraint-externality/runs/atomgit-repeat-dev-reserve-source-20260906-v1")
LEDGER = RUN_ROOT / "source-ledger.jsonl"
live = src.live
trajectory_audit = src.trajectory_audit


class Stop(RuntimeError):
    pass


def readj(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def writej(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verified(path: Path, status: str) -> dict[str, Any]:
    payload = readj(path)
    if payload.get("object_id") != OBJECT_ID or payload.get("status") != status:
        raise Stop(f"identity/status mismatch: {path}")
    claimed = payload.get("content_sha256")
    if claimed:
        unsigned = dict(payload); unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise Stop(f"content hash mismatch: {path}")
    return payload


def reserve_contract() -> dict[str, Any]:
    return verified(RESERVE_CONTRACT, "ATOMGIT_REPEAT_DEV_RESERVE_STATIC_READY_EXECUTION_CLOSED")


def spec() -> dict[str, Any]:
    payload = load_reserve_spec()
    if len(payload.get("families", [])) != 16:
        raise Stop("reserve family cardinality drift")
    return payload


def family_index() -> dict[str, dict[str, Any]]:
    rows = list(spec()["families"])
    out = {row["family_id"]: row for row in rows}
    if len(out) != 16:
        raise Stop("duplicate reserve family id")
    return out


def ranked_ids() -> dict[str, list[str]]:
    ranked = reserve_contract()["reserve"]["ranked_source_order_by_category"]
    out = {cat: [row["family_id"] for row in ranked[cat]] for cat in ("FG", "TNF")}
    if any(len(out[cat]) != 8 or len(set(out[cat])) != 8 for cat in out):
        raise Stop("ranked reserve geometry drift")
    if set(out["FG"]) & set(out["TNF"]):
        raise Stop("reserve category overlap")
    return out


def patch_live() -> None:
    src.patch_live()
    live.EXECUTION_ID = EXECUTION_ID


def config() -> str:
    return src.config().replace(
        "Complete only the target-local AppWorld development source task",
        "Complete only the target-local AppWorld reserve source task",
    )


def agents() -> str:
    return (
        "# Agent Constraint Externality reserve source\n"
        "Use only mcp__appworld__* tools. Any ~/ path is inside AppWorld, never the host. "
        "Never use native read/write/edit/bash/web/memory/agent/skill tools. Complete only the target task.\n"
    )


def mcp(family_id: str, root: Path, progress: Path, trajectory: Path, task_id: str) -> dict[str, Any]:
    args = [
        "-m", "research_pipeline.agent_constraint_externality_atomgit_repeat_dev_reserve_source_mcp_bridge",
        "--bundle", str(OUTPUT_BUNDLE), "--family-id", family_id,
        "--runtime-root", str(root / "appworld"), "--task-id", task_id,
        "--experiment-name", "ace-atomgit-repeat-dev-reserve-source",
        "--progress", str(progress), "--trajectory", str(trajectory),
        "--tool-call-cap", str(TOOL_CALL_CAP),
    ]
    return {"mcpServers": {"appworld": {"command": str(APPWORLD_PYTHON), "args": args, "env": {"PYTHONPATH": str(ROOT)}, "timeout_ms": 30000, "trust": True}}}


def prepare_unit(family_id: str, root: Path) -> tuple[Path, Path, Path, Path, dict[str, Any]]:
    atom = root / "atomcode-home"; work = root / "atomcode-workdir"
    progress = root / "bridge-progress.json"; trajectory = root / "trajectory.jsonl"
    atom.mkdir(parents=True, exist_ok=False); work.mkdir(parents=True, exist_ok=False)
    auth = Path.home() / ".atomcode/auth.toml"
    if not auth.is_file():
        raise Stop("AtomCode auth.toml missing")
    shutil.copy2(auth, atom / "auth.toml"); os.chmod(atom / "auth.toml", 0o600)
    (atom / "config.toml").write_text(config(), encoding="utf-8")
    (work / "AGENTS.md").write_text(agents(), encoding="utf-8")
    task_id = "aceresdev" + family_id.lower().replace("-", "") + "_1"
    return atom, work, progress, trajectory, mcp(family_id, root, progress, trajectory, task_id)


def unit_id(family_id: str) -> str:
    return f"repeatdevreserve:{MODEL_ID}|{family_id}|1"


def usage() -> dict[str, Any]:
    patch_live()
    with tempfile.TemporaryDirectory(prefix="ace-repeat-dev-reserve-usage-") as d:
        root = Path(d); atom = root / "atom"; work = root / "work"; atom.mkdir(); work.mkdir()
        auth = Path.home() / ".atomcode/auth.toml"
        if not auth.is_file(): raise Stop("AtomCode auth.toml missing")
        shutil.copy2(auth, atom / "auth.toml"); os.chmod(atom / "auth.toml", 0o600)
        (atom / "config.toml").write_text(config(), encoding="utf-8")
        proc = None
        try:
            proc, base, token = live.start_daemon(atom_home=atom, workdir=work, log_path=root / "daemon.log")
            return dict(live.codingplan_usage(base, token))
        finally:
            if proc is not None: live.terminate_process(proc)


def qualify_q1() -> dict[str, Any]:
    patch_live(); first = ranked_ids()["FG"][0]
    with tempfile.TemporaryDirectory(prefix="ace-repeat-dev-reserve-q1-") as d:
        root = Path(d); atom, work, progress, trajectory, payload = prepare_unit(first, root)
        proc = None; done = threading.Event(); errors: list[str] = []
        try:
            proc, base, token = live.start_daemon(atom_home=atom, workdir=work, log_path=root / "daemon.log")
            (atom / "mcp.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            live.http_json(base, token, "/live/mode", method="POST", body={"mode": "build"})
            before = int(live.codingplan_usage(base, token)["used"])
            def stream() -> None:
                request = urllib.request.Request(base + "/live", headers={"Authorization": "Bearer " + token})
                try:
                    with urllib.request.urlopen(request, timeout=60) as response:
                        for _ in response:
                            if done.is_set(): break
                except Exception as exc:
                    if not done.is_set(): errors.append(f"{type(exc).__name__}: {exc}")
            thread = threading.Thread(target=stream, daemon=True); thread.start(); deadline = time.time() + 45
            while time.time() < deadline:
                if errors: raise Stop(errors[-1])
                if progress.is_file() and readj(progress).get("status") == "TOOLS_LISTED": break
                time.sleep(.1)
            else: raise Stop("Q1 did not list AppWorld tools")
            after_usage = dict(live.codingplan_usage(base, token)); after = int(after_usage["used"])
            live.http_json(base, token, "/live/stop", method="POST", body={}); done.set(); thread.join(timeout=2)
            state = readj(progress)
            session_jsonls = list((atom / "sessions").glob("*/*.jsonl")) if (atom / "sessions").exists() else []
            trajectory_rows = 0
            if trajectory.is_file():
                trajectory_rows = sum(1 for line in trajectory.read_text(encoding="utf-8").splitlines() if line.strip())
            if state.get("status") != "TOOLS_LISTED" or int(state.get("tool_count", 0)) <= 0 or session_jsonls or trajectory_rows:
                raise Stop("Q1 crossed zero-model-request boundary")
            result = {
                "schema_version": "ace-repeat-dev-reserve-source-q1-v1", "object_id": OBJECT_ID,
                "status": "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_MCP_PREDISPATCH_PASS",
                "family_id": first, "model_profile": MODEL_PROFILE, "model_id": MODEL_ID,
                "codingplan_model_requests": 0, "live_message_submit_count": 0,
                "atomcode_session_jsonl_count": 0, "trajectory_tool_event_count": 0,
                "codingplan_usage_before_used": before, "codingplan_usage_after": after_usage,
                "account_usage_delta_observed_unattributed": after - before,
                "account_usage_delta_is_not_request_attribution": True,
                "bundle_sha256": sha256_file(OUTPUT_BUNDLE), "bridge_sha256": sha256_file(BRIDGE),
                "common_sha256": sha256_file(Path(__file__)), "scientific_dispatch_sent": False,
                "scientific_outcomes_observed": 0,
            }
            result["content_sha256"] = sha256_value(result); return result
        finally:
            done.set()
            if proc is not None: live.terminate_process(proc)


def preflight(executor_path: Path) -> dict[str, Any]:
    contract = reserve_contract()
    qual = verified(RESERVE_QUAL, "ATOMGIT_REPEAT_DEV_RESERVE_STATIC_QUALIFICATION_PASS_AUTHORITY_CLOSED")
    audit = verified(PROTOCOL_AUDIT, "ATOMGIT_REPEAT_DEV_RESERVE_PROTOCOL_AUDIT_PASS_EXECUTION_CLOSED")
    if contract["protected_bundle"]["sha256"] != sha256_file(OUTPUT_BUNDLE): raise Stop("bundle binding drift")
    if qual["protected_bundle_sha256"] != sha256_file(OUTPUT_BUNDLE): raise Stop("qualification bundle drift")
    if audit["reserve_bundle_sha256"] != sha256_file(OUTPUT_BUNDLE): raise Stop("audit bundle drift")
    q1 = qualify_q1(); writej(Q1_OUTPUT, q1)
    out = {
        "schema_version": "ace-repeat-dev-reserve-source-preflight-v1", "object_id": OBJECT_ID,
        "status": "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_PREFLIGHT_PASS_AUTHORITY_CLOSED",
        "reserve_contract_content_sha256": contract["content_sha256"],
        "reserve_qualification_content_sha256": qual["content_sha256"],
        "protocol_audit_content_sha256": audit["content_sha256"],
        "bundle_sha256": sha256_file(OUTPUT_BUNDLE), "q1_content_sha256": q1["content_sha256"],
        "executor_sha256": sha256_file(executor_path), "common_sha256": sha256_file(Path(__file__)),
        "bridge_sha256": sha256_file(BRIDGE), "ranked_family_ids": ranked_ids(),
        "maximum_source_dispatches": 16, "selected_needed": {"FG": 3, "TNF": 3},
        "shared_quota_reserve": SHARED_RESERVE, "minimum_remaining_before_each_dispatch": MIN_REMAINING,
        "provider_requests_created": 0, "scientific_topology_outcomes_observed": 0,
        "authority": {"reserve_source_execution": False, "repair_generation": False, "development_repeat_qualification": False},
    }
    out["content_sha256"] = sha256_value(out); writej(PREFLIGHT_OUTPUT, out)
    readiness = {
        "schema_version": "ace-repeat-dev-reserve-source-readiness-v1", "object_id": OBJECT_ID,
        "status": "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_READY_AWAITING_SEPARATE_HUMAN_AUTHORITY",
        "preflight_content_sha256": out["content_sha256"], "bundle_sha256": sha256_file(OUTPUT_BUNDLE),
        "executor_sha256": out["executor_sha256"], "common_sha256": out["common_sha256"],
        "bridge_sha256": out["bridge_sha256"],
        "model": {"provider": PROVIDER, "profile": MODEL_PROFILE, "id": MODEL_ID},
        "source_selection": {
            "ranked_family_ids": ranked_ids(), "needed_per_category": 3,
            "target_success": "eligibility attrition; continue within frozen reserve",
            "semantic_failure": "eligible; select first three per category",
            "technical_invalidity_after_dispatch": "hard stop no replay no skip",
            "outside_reserve_replacement": False,
        },
        "quota": {"rolling_limit": 500, "shared_reserve": SHARED_RESERVE, "minimum_remaining_before_dispatch": MIN_REMAINING},
        "provider_requests_created": 0,
        "authority": {"reserve_source_execution": False, "repair_generation": False, "development_repeat_qualification": False},
        "next_required_action": "Separate human authority for reserve source acquisition only.",
    }
    readiness["content_sha256"] = sha256_value(readiness); writej(READINESS_OUTPUT, readiness)
    return readiness
