from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

import research_pipeline.agent_constraint_externality_codingplan_qwen38_capability as live
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_build import (
    CONTRACT_OUTPUT as STATIC_CONTRACT,
    OUTPUT_BUNDLE,
    QUAL_OUTPUT as STATIC_QUAL,
    load_dev_spec,
)
from research_pipeline.agent_constraint_externality_direct_sfq_a0_cases import evaluate_case_from_state
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_PYTHON = Path(
    "/data/wyt/agent-self-evolution-observatory/worktrees/agent-constraint-externality-20260831/runtimes/appworld-constraint-externality-py312/bin/python"
)
MODEL_PROFILE = "AtomGit-mimo-v2.5-pro"
MODEL_ID = "mimo-v2.5-pro"
PROVIDER = "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY"
BASE_URL = "https://llm-api.atomgit.com/v1"
MODEL_ROUND_CAP = 56
TOOL_CALL_CAP = 80
MIN_REMAINING = MODEL_ROUND_CAP + 5
EXECUTION_ID = "ACE-ATOMGIT-REPEAT-DEV-SOURCE-20260906"
BRIDGE = ROOT / "research_pipeline/agent_constraint_externality_atomgit_repeat_dev_source_mcp_bridge.py"
REVIEW = ROOT / "consultations/agent-constraint-externality-atomgit-repeat-dev-exact-review-closeout-20260906.md"
Q1_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-source-q1-20260906.json"
PREFLIGHT_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-source-preflight-20260906.json"
AUTH_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-source-human-authorization-20260906.json"
EXEC_CONTRACT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-source-execution-contract-20260906.json"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-source-result-20260906.json"
RUN_ROOT = Path("/data/wyt/agent-constraint-externality/runs/atomgit-repeat-dev-source-20260906-v1")
LEDGER = RUN_ROOT / "source-ledger.jsonl"


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


def families() -> list[dict[str, Any]]:
    spec = load_dev_spec()
    rows = list(spec["families"])
    if len(rows) != 6 or len({row["family_id"] for row in rows}) != 6:
        raise Stop("repeat-development family geometry drift")
    return rows


def config() -> str:
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
context_window = 1000000
retry_max_attempts = 1
system_prompt = "Complete only the target-local AppWorld development source task using mcp__appworld__ tools. Any ~/ path is AppWorld virtual state. Never use native host tools. Preserve unrelated state."
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


def agents() -> str:
    return (
        "# Agent Constraint Externality development source\n"
        "Use only mcp__appworld__* tools. Any ~/ path is inside AppWorld, never the host. "
        "Never use native read/write/edit/bash/web/memory/agent/skill tools. Complete only the target task.\n"
    )


def mcp(family_id: str, root: Path, progress: Path, trajectory: Path, task_id: str) -> dict[str, Any]:
    args = [
        "-m", "research_pipeline.agent_constraint_externality_atomgit_repeat_dev_source_mcp_bridge",
        "--bundle", str(OUTPUT_BUNDLE), "--family-id", family_id,
        "--runtime-root", str(root / "appworld"), "--task-id", task_id,
        "--experiment-name", "ace-atomgit-repeat-dev-source",
        "--progress", str(progress), "--trajectory", str(trajectory),
        "--tool-call-cap", str(TOOL_CALL_CAP),
    ]
    return {"mcpServers": {"appworld": {"command": str(APPWORLD_PYTHON), "args": args, "env": {"PYTHONPATH": str(ROOT)}, "timeout_ms": 30000, "trust": True}}}


def patch_live() -> None:
    live.MODEL_PROFILE = MODEL_PROFILE
    live.MODEL_ID = MODEL_ID
    live.MODEL_ROUND_CAP = MODEL_ROUND_CAP
    live.TOOL_CALL_CAP = TOOL_CALL_CAP
    live.EXECUTION_ID = EXECUTION_ID


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
    task_id = "acerepdev" + family_id.lower().replace("-", "") + "_1"
    return atom, work, progress, trajectory, mcp(family_id, root, progress, trajectory, task_id)


def unit_id(family_id: str) -> str:
    return f"repeatdevsource:{MODEL_ID}|{family_id}|1"


def usage() -> dict[str, Any]:
    patch_live()
    with tempfile.TemporaryDirectory(prefix="ace-repeat-dev-usage-") as d:
        root = Path(d); atom = root / "atom"; work = root / "work"; atom.mkdir(); work.mkdir()
        shutil.copy2(Path.home() / ".atomcode/auth.toml", atom / "auth.toml"); os.chmod(atom / "auth.toml", 0o600)
        (atom / "config.toml").write_text(config(), encoding="utf-8")
        proc = None
        try:
            proc, base, token = live.start_daemon(atom_home=atom, workdir=work, log_path=root / "daemon.log")
            return dict(live.codingplan_usage(base, token))
        finally:
            if proc is not None:
                live.terminate_process(proc)


def trajectory_audit(path: Path, expected_calls: int) -> dict[str, Any]:
    if not path.is_file():
        raise Stop("source trajectory missing")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    dispatch_rows = [row for row in rows if row.get("event") == "TOOL_DISPATCH"]
    complete_rows = [row for row in rows if row.get("event") == "TOOL_COMPLETION"]
    dispatch = {row["tool_id"]: row for row in dispatch_rows}
    complete = {row["tool_id"]: row for row in complete_rows}
    rejected = [row for row in rows if row.get("event") == "TOOL_REJECTED"]
    if (
        rejected
        or len(dispatch_rows) != expected_calls
        or len(complete_rows) != expected_calls
        or len(dispatch) != expected_calls
        or len(complete) != expected_calls
        or set(dispatch) != set(complete)
    ):
        raise Stop("source trajectory has rejected/dangling/duplicate tool unit")
    if sorted(int(row["index"]) for row in dispatch.values()) != list(range(1, expected_calls + 1)):
        raise Stop("source trajectory index geometry drift")
    for tool_id, row in dispatch.items():
        if complete[tool_id].get("tool_name") != row.get("tool_name"):
            raise Stop("source trajectory tool-name binding drift")
    return {"tool_call_count": expected_calls, "trajectory_sha256": sha256_file(path), "row_count": len(rows), "all_tool_dispatches_closed": True}


def qualify_q1() -> dict[str, Any]:
    patch_live(); family = families()[0]
    with tempfile.TemporaryDirectory(prefix="ace-repeat-dev-q1-") as d:
        root = Path(d); atom, work, progress, trajectory, payload = prepare_unit(family["family_id"], root)
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
            after = int(live.codingplan_usage(base, token)["used"])
            live.http_json(base, token, "/live/stop", method="POST", body={}); done.set(); thread.join(timeout=2)
            state = readj(progress)
            if after != before or state.get("status") != "TOOLS_LISTED" or int(state.get("tool_count", 0)) <= 0:
                raise Stop("Q1 crossed zero-model-request boundary")
            result = {"schema_version": "ace-repeat-dev-source-q1-v1", "object_id": OBJECT_ID, "status": "ATOMGIT_REPEAT_DEV_SOURCE_MCP_PREDISPATCH_PASS", "family_id": family["family_id"], "model_profile": MODEL_PROFILE, "model_id": MODEL_ID, "codingplan_model_requests": 0, "codingplan_usage": live.codingplan_usage(base, token), "bundle_sha256": sha256_file(OUTPUT_BUNDLE), "bridge_sha256": sha256_file(BRIDGE), "runner_sha256": sha256_file(Path(__file__)), "scientific_dispatch_sent": False, "scientific_outcomes_observed": 0}
            result["content_sha256"] = sha256_value(result); return result
        finally:
            done.set()
            if proc is not None: live.terminate_process(proc)


def preflight() -> dict[str, Any]:
    static = verified(STATIC_CONTRACT, "ATOMGIT_REPEAT_DEV_STATIC_DESIGN_READY_ZERO_PROVIDER")
    qual = verified(STATIC_QUAL, "ATOMGIT_REPEAT_DEV_STATIC_QUALIFICATION_PASS_EXECUTION_CLOSED")
    if static["protected_bundle"]["sha256"] != sha256_file(OUTPUT_BUNDLE): raise Stop("bundle binding drift")
    if qual["protected_bundle_sha256"] != sha256_file(OUTPUT_BUNDLE): raise Stop("qualification bundle drift")
    if not REVIEW.is_file(): raise Stop("exact-code review closeout missing")
    q1 = qualify_q1(); writej(Q1_OUTPUT, q1)
    out = {"schema_version": "ace-repeat-dev-source-preflight-v1", "object_id": OBJECT_ID, "status": "ATOMGIT_REPEAT_DEV_SOURCE_PREFLIGHT_PASS_AUTHORITY_CLOSED", "static_contract_content_sha256": static["content_sha256"], "static_qualification_content_sha256": qual["content_sha256"], "bundle_sha256": sha256_file(OUTPUT_BUNDLE), "q1_content_sha256": q1["content_sha256"], "review_closeout_sha256": sha256_file(REVIEW), "family_ids": [row["family_id"] for row in families()], "source_count": 6, "replacement_or_top_up": False, "provider_requests_created": 0, "authority": {"source_execution": False, "repair_generation": False, "development_repeat_qualification": False}}
    out["content_sha256"] = sha256_value(out); writej(PREFLIGHT_OUTPUT, out); return out


def execute() -> dict[str, Any]:
    patch_live(); auth = verified(AUTH_OUTPUT, "USER_AUTHORIZED_ATOMGIT_REPEAT_DEV_SIX_SOURCE_ONLY"); contract = verified(EXEC_CONTRACT, "ATOMGIT_REPEAT_DEV_SIX_SOURCE_EXECUTION_AUTHORIZED")
    if not auth["authority"]["source_execution"] or auth["authority"]["repair_generation"]: raise Stop("source authority scope drift")
    if contract.get("human_authorization_content_sha256") != auth.get("content_sha256"):
        raise Stop("source authorization binding drift")
    if contract.get("runner_sha256") != sha256_file(Path(__file__)):
        raise Stop("source runner SHA drift")
    if contract.get("bridge_sha256") != sha256_file(BRIDGE):
        raise Stop("source bridge SHA drift")
    if contract.get("protected_bundle_sha256") != sha256_file(OUTPUT_BUNDLE):
        raise Stop("source bundle SHA drift")
    if contract.get("model", {}).get("id") != MODEL_ID or contract.get("model", {}).get("profile") != MODEL_PROFILE:
        raise Stop("source model binding drift")
    if contract.get("panel", {}).get("family_ids") != [row["family_id"] for row in families()]:
        raise Stop("source family-order binding drift")
    RUN_ROOT.mkdir(parents=True, exist_ok=True); states = live.ledger_states(LEDGER)
    for family in families():
        uid = unit_id(family["family_id"]); state = states.get(uid)
        if state == "COMPLETION": continue
        if state is not None: raise Stop(f"replay forbidden after dispatch: {uid}:{state}")
        quota = usage()
        if int(quota["remaining"]) < MIN_REMAINING:
            return {"status": "ATOMGIT_REPEAT_DEV_SOURCE_QUOTA_HOLD", "next_family": family["family_id"], "codingplan_usage": quota}
        root = RUN_ROOT / family["family_id"].lower()
        if root.exists(): raise Stop(f"unit root already exists: {root}")
        root.mkdir(); atom, work, progress, trajectory, payload = prepare_unit(family["family_id"], root); proc = None
        case = family["source_case"]
        try:
            proc, base, token = live.start_daemon(atom_home=atom, workdir=work, log_path=root / "atomcode-daemon.log")
            (atom / "mcp.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            live.http_json(base, token, "/live/mode", method="POST", body={"mode": "build"})
            def before_submit() -> dict[str, Any]:
                state0 = readj(progress)
                if state0.get("status") != "TOOLS_LISTED": raise Stop("MCP tools not listed")
                q = dict(live.codingplan_usage(base, token))
                if int(q["remaining"]) < MIN_REMAINING: raise Stop("quota changed below per-source headroom")
                live.append_jsonl(LEDGER, {"schema_version": "ace-repeat-dev-source-ledger-v1", "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "DISPATCH", "unit_id": uid, "family_id": family["family_id"], "case_id": case["case_id"], "provider": PROVIDER, "model_profile": MODEL_PROFILE, "model_id": MODEL_ID, "prompt_sha256": sha256_value(case["task_instruction"]), "initial_snapshot_sha256": state0["initial_snapshot_sha256"], "bundle_sha256": sha256_file(OUTPUT_BUNDLE), "codingplan_window_before": q, "attempt": 1, "retry_allowed": False, "replacement_allowed": False, "time_ns": time.time_ns()}); return {"usage_before": q}
            result = live.run_live_turn(base=base, token=token, instruction=case["task_instruction"], progress_path=progress, before_submit=before_submit, timeout_seconds=480)
            after = dict(live.codingplan_usage(base, token))
            if result["prohibited_tool"] or result["error_message"] or result["stop_reason"] != "stopped":
                live.append_jsonl(LEDGER, {"schema_version": "ace-repeat-dev-source-ledger-v1", "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "FAILURE", "unit_id": uid, "family_id": family["family_id"], "failure_class": "SOURCE_INTERFACE_OR_AGENT_LOOP_INVALID", "message": str(result["prohibited_tool"] or result["error_message"] or result["stop_reason"])[:400], "codingplan_window_after": after, "retry_attempted": False, "time_ns": time.time_ns()}); return {"status": "ATOMGIT_REPEAT_DEV_SOURCE_INVALID_STOP", "family_id": family["family_id"]}
        finally:
            if proc is not None: live.terminate_process(proc)
        state1 = readj(progress); calls = int(state1.get("tool_call_count", 0))
        if calls <= 0:
            live.append_jsonl(LEDGER, {"schema_version": "ace-repeat-dev-source-ledger-v1", "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "FAILURE", "unit_id": uid, "family_id": family["family_id"], "failure_class": "SOURCE_ZERO_TOOL_NON_SEMANTIC_STOP", "message": "Target requires AppWorld state mutation but the agent executed zero AppWorld tools.", "retry_attempted": False, "time_ns": time.time_ns()})
            return {"status": "ATOMGIT_REPEAT_DEV_SOURCE_INVALID_STOP", "family_id": family["family_id"]}
        try:
            audit = trajectory_audit(trajectory, calls)
            target_success = bool(evaluate_case_from_state(case, source_db_root=Path(state1["source_db_root"]), changes_db_root=Path(state1["changes_db_root"]), measurement_root=root / "measurement-full-dbs"))
        except Exception as exc:
            live.append_jsonl(LEDGER, {"schema_version": "ace-repeat-dev-source-ledger-v1", "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "FAILURE", "unit_id": uid, "family_id": family["family_id"], "failure_class": "SOURCE_TRAJECTORY_OR_EVALUATOR_INVALID", "message": f"{type(exc).__name__}: {exc}"[:400], "retry_attempted": False, "time_ns": time.time_ns()})
            return {"status": "ATOMGIT_REPEAT_DEV_SOURCE_INVALID_STOP", "family_id": family["family_id"]}
        completion = {"schema_version": "ace-repeat-dev-source-ledger-v1", "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "COMPLETION", "unit_id": uid, "family_id": family["family_id"], "case_id": case["case_id"], "target_success": target_success, "usable_semantic_failure": not target_success, "tool_loop_completed": True, "appworld_tool_call_count": calls, "model_round_count": int(result["model_round_count"]), "prompt_tokens_total": int(result["prompt_tokens_total"]), "completion_tokens_total": int(result["completion_tokens_total"]), "trajectory_sha256": audit["trajectory_sha256"], "trajectory_row_count": audit["row_count"], "all_tool_dispatches_closed": True, "bridge_progress_sha256": sha256_file(progress), "codingplan_window_after": after, "time_ns": time.time_ns()}
        live.append_jsonl(LEDGER, completion); states = live.ledger_states(LEDGER)
        if target_success:
            return {"status": "ATOMGIT_REPEAT_DEV_SOURCE_SUPPORT_FAIL_SUCCESS_STOP", "family_id": family["family_id"], "completed": len([r for r in live.ledger_rows(LEDGER) if r.get("event") == "COMPLETION"])}
    rows = [row for row in live.ledger_rows(LEDGER) if row.get("event") == "COMPLETION"]
    if len(rows) != 6 or not all(row.get("usable_semantic_failure") for row in rows): raise Stop("six-source terminal geometry invalid")
    result = {"schema_version": "ace-repeat-dev-source-result-v1", "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "status": "ATOMGIT_REPEAT_DEV_SIX_SOURCE_SEMANTIC_FAILURE_PASS_REPAIR_CLOSED", "family_count": 6, "completed_source_count": 6, "semantic_failure_count": 6, "target_success_count": 0, "scientific_model_round_count": sum(int(row["model_round_count"]) for row in rows), "appworld_tool_call_total": sum(int(row["appworld_tool_call_count"]) for row in rows), "ledger_sha256": sha256_file(LEDGER), "source_trajectory_sha256_by_family": {row["family_id"]: row["trajectory_sha256"] for row in rows}, "repair_generation_executed": False, "topology_execution_executed": False, "authority": {"source_execution_closed": True, "repair_generation": False, "development_repeat_qualification": False, "rq1_rq2": False, "paper_claim": False}}
    result["content_sha256"] = sha256_value(result); writej(RESULT_OUTPUT, result); return result


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--preflight", action="store_true"); parser.add_argument("--execute", action="store_true"); parser.add_argument("--usage-only", action="store_true"); args = parser.parse_args()
    if sum((args.preflight, args.execute, args.usage_only)) != 1: raise SystemExit("choose exactly one action")
    if args.usage_only: print(json.dumps({"status": "ZERO_REQUEST_USAGE_PROBE", "usage": usage(), "model_requests": 0}, sort_keys=True)); return
    payload = preflight() if args.preflight else execute(); print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
