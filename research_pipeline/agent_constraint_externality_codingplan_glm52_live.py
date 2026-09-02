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

from research_pipeline.agent_constraint_externality_appworld_runtime import evaluate_arm_from_materialized_state
from research_pipeline.agent_constraint_externality_capability_execute import capability_gate
import research_pipeline.agent_constraint_externality_codingplan_qwen38_capability as live
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, EpisodeUnit, RunnerError, sha256_file, sha256_value
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_PYTHON = ROOT / "runtimes/appworld-constraint-externality-py312/bin/python"
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
V4_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
V4_QUAL = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r4-20260902.json"
SEARCH_STATE = GENERATED / "agent-constraint-externality-capability-backbone-search-state-b1-20260903.json"
CATALOG_B1 = GENERATED / "agent-constraint-externality-codingplan-catalog-b1-20260903.json"
DEEPSEEK_CLOSEOUT = GENERATED / "agent-constraint-externality-codingplan-deepseek-live-capability-b0-closeout-20260903.json"
MODEL_PROFILE = "AtomGit-GLM-5.2"
MODEL_ID = "GLM-5.2"
PROVIDER = "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY"
BASE_URL = "https://llm-api.atomgit.com/v1"
CONTEXT_WINDOW = 200000
MAX_OUTPUT_TOKENS = None
RETRY_MAX_ATTEMPTS = 1
MODEL_ROUND_CAP = 20
TOOL_CALL_CAP = 16
CAPABILITY_FAMILIES = ("ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06")
REPEATS = (1, 2)
EXECUTION_ID = "CODINGPLAN-GLM52-CAPABILITY-B1"
STAGE = "CODINGPLAN_GLM52_CAPABILITY_B1"
LEDGER_SCHEMA = "ace-codingplan-glm52-live-capability-b1-ledger-v1"
SELECTION_OUTPUT = SEARCH_STATE
Q1_OUTPUT = GENERATED / "agent-constraint-externality-codingplan-glm52-live-mcp-q1-predispatch-20260903.json"
CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-codingplan-glm52-capability-b1-contract-20260903.json"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-codingplan-glm52-capability-b1-result-20260903.json"

class GLM52LiveStop(RunnerError):
    pass

def _patch_live_constants() -> None:
    live.MODEL_PROFILE = MODEL_PROFILE
    live.TOOL_CALL_CAP = TOOL_CALL_CAP
    live.MODEL_ROUND_CAP = MODEL_ROUND_CAP

def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _verified(path: Path, status: str | None = None) -> dict[str, Any]:
    payload = _read(path)
    if payload.get("object_id") != OBJECT_ID:
        raise GLM52LiveStop(f"Object mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise GLM52LiveStop(f"Unexpected status in {path}: {payload.get('status')}")
    claimed = payload.get("content_sha256")
    if claimed is not None:
        unsigned = dict(payload); unsigned.pop("content_sha256", None)
        if claimed != sha256_value(unsigned):
            raise GLM52LiveStop(f"Content hash mismatch: {path}")
    return payload

def units() -> list[EpisodeUnit]:
    rows = [EpisodeUnit(namespace="capability", key=(MODEL_ID, family, repeat), stage=STAGE, family_id=family, repeat=repeat) for family in CAPABILITY_FAMILIES for repeat in REPEATS]
    if len(rows) != 8 or len({row.unit_id for row in rows}) != 8:
        raise GLM52LiveStop("Expected exactly eight unique GLM-5.2 units.")
    return rows

def atomcode_config() -> str:
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
context_window = {CONTEXT_WINDOW}
retry_max_attempts = {RETRY_MAX_ATTEMPTS}
system_prompt = "Complete the task using only AppWorld MCP tools. Preserve unrelated state. Batch independent AppWorld tool calls in the same model round whenever possible. When finished, return a concise completion message."
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

def agents_md() -> str:
    return '''# Scientific AppWorld capability run\nThe user message is an AppWorld benchmark task, not software engineering.\nUse only tools whose names begin with `mcp__appworld__`. Never use host coding, shell, file, web, memory, AtomGit, task/team/subagent, skill, or code-graph tools. Do not inspect or modify the host workspace. Preserve unrelated AppWorld state. Batch independent AppWorld tool calls in the same model round whenever possible because CodingPlan quota is request-count limited, not token limited.\n'''

def mcp_config(*, unit: EpisodeUnit, unit_root: Path, progress: Path, task_id: str) -> dict[str, Any]:
    args = ["-m", "research_pipeline.agent_constraint_externality_codingplan_mcp_bridge", "--appworld-root", str(APPWORLD_ROOT), "--bundle", str(V4_BUNDLE), "--family-id", unit.family_id, "--repeat", str(unit.repeat), "--runtime-root", str(unit_root / "appworld"), "--task-id", task_id, "--experiment-name", "ace-codingplan-glm52-live-capability-b1", "--progress", str(progress), "--tool-call-cap", str(TOOL_CALL_CAP)]
    return {"mcpServers": {"appworld": {"command": str(APPWORLD_PYTHON), "args": args, "env": {"PYTHONPATH": str(ROOT)}, "timeout_ms": 30000, "trust": True}}}

def prepare_unit_runtime(*, unit: EpisodeUnit, unit_root: Path) -> tuple[Path, Path, Path, dict[str, Any]]:
    unit_root = unit_root.resolve(); atom_home = unit_root / "atomcode-home"; workdir = unit_root / "atomcode-workdir"; progress = unit_root / "bridge-progress.json"
    atom_home.mkdir(parents=True, exist_ok=False); workdir.mkdir(parents=True, exist_ok=False)
    auth_source = Path.home() / ".atomcode/auth.toml"
    if not auth_source.is_file(): raise GLM52LiveStop("AtomCode auth.toml missing.")
    shutil.copy2(auth_source, atom_home / "auth.toml"); os.chmod(atom_home / "auth.toml", 0o600)
    (atom_home / "config.toml").write_text(atomcode_config(), encoding="utf-8"); (workdir / "AGENTS.md").write_text(agents_md(), encoding="utf-8")
    task_id = "aceglmb1" + unit.family_id.lower().replace("-", "") + f"r{unit.repeat}_1"
    return atom_home, workdir, progress, mcp_config(unit=unit, unit_root=unit_root, progress=progress, task_id=task_id)

def build_selection() -> dict[str, Any]:
    state = _verified(SEARCH_STATE, "CAPABILITY_BACKBONE_SEARCH_CONTINUE_GLM52_NEXT")
    catalog = _verified(CATALOG_B1, "CODINGPLAN_ACCOUNT_CATALOG_REFRESH_PASS_ZERO_MODEL_REQUESTS")
    closeout = _verified(DEEPSEEK_CLOSEOUT, "CODINGPLAN_DEEPSEEK_LIVE_B0_FLOOR_CLOSEOUT")
    if state.get("next_candidate") != {"model_id": MODEL_ID, "profile": MODEL_PROFILE}:
        raise GLM52LiveStop("Frozen backbone ladder does not select GLM-5.2 next.")
    if state.get("remaining_frozen_order") != ["GLM-5.2", "mimo-v2.5", "mimo-v2.5-pro"]:
        raise GLM52LiveStop("Frozen backbone ladder order drifted.")
    glm = next((row for row in catalog.get("models", []) if row.get("model_id") == MODEL_ID), None)
    if glm is None or glm.get("profile") != MODEL_PROFILE:
        raise GLM52LiveStop("GLM-5.2 is absent from the frozen account catalog.")
    if glm.get("context_window") != CONTEXT_WINDOW or glm.get("max_tokens") is not None:
        raise GLM52LiveStop("GLM-5.2 catalog runtime limits drifted.")
    if closeout.get("verdict") != "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP":
        raise GLM52LiveStop("DeepSeek predecessor is not frozen at floor.")
    return state

def qualify_q1() -> dict[str, Any]:
    _patch_live_constants(); unit = units()[0]
    with tempfile.TemporaryDirectory(prefix="ace-glm52-live-q1-") as directory:
        root = Path(directory); atom_home, workdir, progress, mcp_payload = prepare_unit_runtime(unit=unit, unit_root=root)
        process = None; stream_done = threading.Event(); stream_error: list[str] = []
        try:
            process, base, token = live.start_daemon(atom_home=atom_home, workdir=workdir, log_path=root / "atomcode-daemon.log")
            (atom_home / "mcp.json").write_text(json.dumps(mcp_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            live.http_json(base, token, "/live/mode", method="POST", body={"mode": "build"})
            used_before = int(live.codingplan_usage(base, token)["used"])
            def stream() -> None:
                request = urllib.request.Request(base + "/live", headers={"Authorization": "Bearer " + token})
                try:
                    with urllib.request.urlopen(request, timeout=60) as response:
                        for _ in response:
                            if stream_done.is_set(): break
                except Exception as exc:
                    if not stream_done.is_set(): stream_error.append(f"{type(exc).__name__}: {exc}")
            thread = threading.Thread(target=stream, daemon=True); thread.start(); deadline = time.time() + 45
            while time.time() < deadline:
                if stream_error: raise GLM52LiveStop(stream_error[-1])
                if progress.is_file() and _read(progress).get("status") == "TOOLS_LISTED": break
                time.sleep(0.1)
            else: raise GLM52LiveStop("GLM-5.2 Q1 did not list AppWorld MCP tools.")
            used_after = int(live.codingplan_usage(base, token)["used"])
            live.http_json(base, token, "/live/stop", method="POST", body={}); stream_done.set(); thread.join(timeout=2)
            state = _read(progress)
            payload: dict[str, Any] = {
                "schema_version": "ace-codingplan-glm52-live-mcp-q1-v1", "object_id": OBJECT_ID,
                "status": "CODINGPLAN_GLM52_LIVE_MCP_PREDISPATCH_PASS", "model_profile": MODEL_PROFILE, "model_id": MODEL_ID,
                "protocol": "DAEMON_BOOT_WITHOUT_MCP_THEN_ACTIVATE_APPWORLD_MCP_THEN_GET_LIVE_WAIT_TOOLS_LISTED_WITHOUT_LIVE_MESSAGE",
                "session_mcp_progress_status": state.get("status"), "session_mcp_tool_count": int(state.get("tool_count", 0)),
                "codingplan_window_used_before": used_before, "codingplan_window_used_after": used_after, "codingplan_model_requests": used_after - used_before,
                "scientific_dispatch_sent": False, "scientific_outcomes_observed": 0, "runner_source_sha256": sha256_file(Path(__file__)),
                "transport_source_sha256": sha256_file(ROOT / "research_pipeline/agent_constraint_externality_codingplan_qwen38_capability.py"),
                "bridge_source_sha256": sha256_file(ROOT / "research_pipeline/agent_constraint_externality_codingplan_mcp_bridge.py"), "bundle_sha256": sha256_file(V4_BUNDLE),
            }
            if payload["codingplan_model_requests"] != 0 or payload["session_mcp_progress_status"] != "TOOLS_LISTED" or payload["session_mcp_tool_count"] <= 0:
                raise GLM52LiveStop("GLM-5.2 Q1 predispatch did not pass fail-closed checks.")
            payload["content_sha256"] = sha256_value(payload); return payload
        finally:
            stream_done.set()
            if process is not None: live.terminate_process(process)

def build_contract(selection: dict[str, Any], q1: dict[str, Any]) -> dict[str, Any]:
    _verified(V4_QUAL, "CAPABILITY_SUBSTRATE_V4_PUBLIC_REACHABILITY_WITH_HEADROOM_PASS")
    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-glm52-capability-b1-contract-v1", "object_id": OBJECT_ID, "execution_id": EXECUTION_ID,
        "status": "CODINGPLAN_GLM52_CAPABILITY_B1_AUTHORIZED", "backbone_search_state_sha256": selection["content_sha256"], "q1_predispatch_sha256": q1["content_sha256"],
        "model": {"profile": MODEL_PROFILE, "id": MODEL_ID, "context_window": CONTEXT_WINDOW, "max_output_tokens_control": "PROVIDER_MANAGED_UNSET_BY_OFFICIAL_CODINGPLAN_CATALOG", "retry_max_attempts": RETRY_MAX_ATTEMPTS, "sampling_control": "PROVIDER_MANAGED_NO_REASONING_EFFORT_CONTROL_ADVERTISED"},
        "harness": {"id": "ATOMCODE_CODINGPLAN_MCP_V1", "transport_reused_from_frozen_qwen_a0": True, "appworld_mcp_native": True, "ai_session_naming": False, "subagents": False, "model_round_cap_per_episode": MODEL_ROUND_CAP, "appworld_tool_call_cap": TOOL_CALL_CAP, "retry_allowed": False, "replacement_allowed": False},
        "panel": {"family_ids": list(CAPABILITY_FAMILIES), "repeats": list(REPEATS), "episodes": 8, "arm": "LOW", "reuse_prior_glm52_measurements": False},
        "gate": {"tool_loop_completion_min": 0.75, "target_success_min": 0.50, "target_success_max": 0.875, "non_target_preservation_min": 0.85, "malformed_tool_calls_required": 0},
        "substrate": {"bundle": str(V4_BUNDLE.relative_to(ROOT)), "bundle_sha256": sha256_file(V4_BUNDLE), "v4_qualification_sha256": sha256_file(V4_QUAL)},
        "execution_policy": {"durable_dispatch_before_model_request": True, "unknown_after_dispatch_replay": False, "partial_outcome_redesign": False, "stop_on_first_failure": True},
        "authority": {"capability_b1": True, "f0": False, "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False}, "scientific_outcomes_observed": 0,
    }
    payload["content_sha256"] = sha256_value(payload); return payload

def freeze() -> dict[str, Any]:
    selection = build_selection()
    q1 = qualify_q1(); _write(Q1_OUTPUT, q1)
    contract = build_contract(selection, q1); _write(CONTRACT_OUTPUT, contract)
    return {"selection": selection, "q1": q1, "contract": contract}

def _dispatch_row(unit: EpisodeUnit, arm: dict[str, Any], progress: dict[str, Any], usage: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": LEDGER_SCHEMA, "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "DISPATCH", "unit_id": unit.unit_id,
        "unit": {"family_id": unit.family_id, "repeat": unit.repeat, "stage": unit.stage}, "provider": PROVIDER, "model_profile": MODEL_PROFILE, "model_id": MODEL_ID,
        "harness": "ATOMCODE_CODINGPLAN_MCP_V1", "prompt_sha256": sha256_value(arm["task_instruction"]), "initial_snapshot_sha256": progress["initial_snapshot_sha256"],
        "tool_call_cap": TOOL_CALL_CAP, "model_round_cap": MODEL_ROUND_CAP, "codingplan_window_before": usage, "dispatch_time_ns": time.time_ns(),
        "attempt": 1, "retry_allowed": False, "replacement_allowed": False,
    }

def execute_panel(*, runtime_root: Path, ledger_path: Path) -> None:
    _patch_live_constants()
    _verified(SELECTION_OUTPUT, "CAPABILITY_BACKBONE_SEARCH_CONTINUE_GLM52_NEXT")
    _verified(Q1_OUTPUT, "CODINGPLAN_GLM52_LIVE_MCP_PREDISPATCH_PASS")
    _verified(CONTRACT_OUTPUT, "CODINGPLAN_GLM52_CAPABILITY_B1_AUTHORIZED")
    _verified(V4_QUAL, "CAPABILITY_SUBSTRATE_V4_PUBLIC_REACHABILITY_WITH_HEADROOM_PASS")
    spec = load_protected_spec(V4_BUNDLE); families = {row["family_id"]: row for row in spec["families"]}
    runtime_root = runtime_root.resolve(); ledger_path = ledger_path.resolve(); states = live.ledger_states(ledger_path)
    for unit in units():
        state = states.get(unit.unit_id)
        if state == "COMPLETION": continue
        if state is not None: raise GLM52LiveStop(f"Refusing replay of dispatched unit {unit.unit_id}: {state}")
        family = families[unit.family_id]; arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
        if int(arm["matching"]["tool_budget"]) != TOOL_CALL_CAP: raise GLM52LiveStop("V4 tool budget drifted from 16.")
        unit_root = runtime_root / unit.unit_id.replace(":", "_").replace("|", "_")
        if unit_root.exists(): raise GLM52LiveStop(f"Refusing overwrite: {unit_root}")
        unit_root.mkdir(parents=True); atom_home, workdir, progress_path, mcp_payload = prepare_unit_runtime(unit=unit, unit_root=unit_root)
        process = None; live_result: dict[str, Any] | None = None; usage_before: dict[str, Any] = {}; usage_after: dict[str, Any] = {}
        try:
            process, base, token = live.start_daemon(atom_home=atom_home, workdir=workdir, log_path=unit_root / "atomcode-daemon.log")
            (atom_home / "mcp.json").write_text(json.dumps(mcp_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            live.http_json(base, token, "/live/mode", method="POST", body={"mode": "build"})
            def before_submit() -> dict[str, Any]:
                progress = _read(progress_path)
                if progress.get("status") != "TOOLS_LISTED": raise GLM52LiveStop(f"Session MCP catalog not frozen: {progress.get('status')}")
                usage = live.codingplan_usage(base, token)
                if int(usage["remaining"]) < MODEL_ROUND_CAP + 5: raise GLM52LiveStop("Insufficient CodingPlan rolling-window headroom.")
                live.append_jsonl(ledger_path, _dispatch_row(unit, arm, progress, usage)); return {"usage_before": usage}
            live_result = live.run_live_turn(base=base, token=token, instruction=arm["task_instruction"], progress_path=progress_path, before_submit=before_submit)
            usage_before = dict(live_result["pre_submit"]["usage_before"]); time.sleep(0.3); usage_after = live.codingplan_usage(base, token)
            if live_result["prohibited_tool"]:
                live.append_jsonl(ledger_path, {"schema_version": LEDGER_SCHEMA, "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "FAILURE", "unit_id": unit.unit_id, "failure_class": "HARNESS_CONTAMINATION_NON_APPWORLD_TOOL", "message": str(live_result["prohibited_tool"]), "model_round_count": live_result["model_round_count"], "codingplan_window_after": usage_after, "time_ns": time.time_ns(), "retry_attempted": False})
                raise GLM52LiveStop(f"Non-AppWorld tool attempted: {live_result['prohibited_tool']}")
            if live_result["error_message"] or live_result["stop_reason"] in {"provider_error", "timeout", "rate_limited", "prompt_rejected", "policy_denied", "runtime_stopped"}:
                message = str(live_result["error_message"] or live_result["stop_reason"])
                live.append_jsonl(ledger_path, {"schema_version": LEDGER_SCHEMA, "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "FAILURE", "unit_id": unit.unit_id, "failure_class": "CODINGPLAN_INTERFACE_STOP", "message": message[:400], "model_round_count": live_result["model_round_count"], "codingplan_window_after": usage_after, "time_ns": time.time_ns(), "retry_attempted": False})
                raise GLM52LiveStop(message)
        finally:
            if process is not None: live.terminate_process(process)
        if live_result is None: raise GLM52LiveStop("No live result after dispatch.")
        deadline = time.time() + 15
        while time.time() < deadline:
            if progress_path.is_file():
                progress = _read(progress_path)
                if progress.get("status") in {"CLOSED_STATE_SAVED", "STATE_SAVED_AFTER_TOOL", "TOOL_CALL_CAP_EXCEEDED"}: break
            time.sleep(0.1)
        progress = _read(progress_path)
        evaluation = evaluate_arm_from_materialized_state(arm=arm, source_db_root=Path(progress["source_db_root"]), changes_db_root=Path(progress["changes_db_root"]), measurement_db_root=unit_root / "measurement-full-dbs")
        normal_completion = live_result["stop_reason"] == "stopped" and int(progress.get("tool_call_count", 0)) <= TOOL_CALL_CAP
        live.append_jsonl(ledger_path, {
            "schema_version": LEDGER_SCHEMA, "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "event": "COMPLETION", "unit_id": unit.unit_id,
            "tool_loop_completed": normal_completion, "atomcode_stop_reason": live_result["stop_reason"], "appworld_tool_call_count": int(progress.get("tool_call_count", 0)),
            "model_round_count": int(live_result["model_round_count"]), "prompt_tokens_total": int(live_result["prompt_tokens_total"]), "completion_tokens_total": int(live_result["completion_tokens_total"]),
            "target_success": bool(evaluation["target_success"]), "non_target_preservation": float(evaluation["non_target_preservation"]), "malformed_tool_calls": 0,
            "final_text_sha256": live_result["final_text_sha256"], "final_text_bytes": live_result["final_text_bytes"], "codingplan_window_before": usage_before, "codingplan_window_after": usage_after,
            "bridge_progress_sha256": sha256_file(progress_path), "measurement_content_sha256": evaluation["measurement"]["content_sha256"], "time_ns": time.time_ns(),
        })
        states = live.ledger_states(ledger_path)

def adjudicate(*, ledger_path: Path) -> dict[str, Any]:
    rows = live.ledger_rows(ledger_path); states = live.ledger_states(ledger_path)
    missing = [unit.unit_id for unit in units() if states.get(unit.unit_id) != "COMPLETION"]
    if missing: raise GLM52LiveStop("Incomplete GLM-5.2 panel: " + ", ".join(missing))
    completions = [row for row in rows if row["event"] == "COMPLETION"]
    if len(completions) != 8: raise GLM52LiveStop("Expected exactly eight completion rows.")
    measurements = [{"tool_loop_completed": bool(row["tool_loop_completed"]), "target_success": bool(row["target_success"]), "non_target_preservation": float(row["non_target_preservation"]), "malformed_tool_calls": int(row["malformed_tool_calls"])} for row in completions]
    gate = capability_gate(measurements)
    result: dict[str, Any] = {
        "schema_version": "ace-codingplan-glm52-capability-b1-result-v1", "object_id": OBJECT_ID, "execution_id": EXECUTION_ID, "status": gate["verdict"],
        "provider": PROVIDER, "model_profile": MODEL_PROFILE, "model_id": MODEL_ID, "harness": "ATOMCODE_CODINGPLAN_MCP_V1", "gate": gate,
        "valid_capability_measurements": 8, "agent_episode_count": 8, "appworld_tool_call_total": sum(int(row["appworld_tool_call_count"]) for row in completions),
        "model_round_count": sum(int(row["model_round_count"]) for row in completions), "prompt_tokens_total": sum(int(row["prompt_tokens_total"]) for row in completions),
        "completion_tokens_total": sum(int(row["completion_tokens_total"]) for row in completions), "codingplan_window_first_before": completions[0]["codingplan_window_before"],
        "codingplan_window_last_after": completions[-1]["codingplan_window_after"], "scientific_outcomes_observed": 0, "f0_executed": False,
        "ledger_sha256": sha256_file(ledger_path), "backbone_search_state_sha256": _read(SELECTION_OUTPUT)["content_sha256"], "contract_sha256": _read(CONTRACT_OUTPUT)["content_sha256"],
        "authority": {"f0": False, "f0_reason": "Capability selection never self-authorizes F0.", "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False},
    }
    result["content_sha256"] = sha256_value(result); return result

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--freeze", action="store_true"); parser.add_argument("--runtime-root", type=Path); parser.add_argument("--ledger", type=Path); parser.add_argument("--result-output", type=Path, default=RESULT_OUTPUT); args = parser.parse_args()
    if args.freeze:
        artifacts = freeze(); print(json.dumps({"selection_status": artifacts["selection"]["status"], "q1_status": artifacts["q1"]["status"], "q1_model_requests": artifacts["q1"]["codingplan_model_requests"], "contract_status": artifacts["contract"]["status"], "f0_authorized": False}, sort_keys=True)); return
    if args.runtime_root is None or args.ledger is None: raise SystemExit("--runtime-root and --ledger are required unless --freeze is used")
    execute_panel(runtime_root=args.runtime_root, ledger_path=args.ledger); result = adjudicate(ledger_path=args.ledger.resolve()); _write(args.result_output.resolve(), result)
    print(json.dumps({"status": result["status"], "model_round_count": result["model_round_count"], "appworld_tool_call_total": result["appworld_tool_call_total"], "target_success_rate": result["gate"]["target_success_rate"], "tool_loop_completion_rate": result["gate"]["tool_loop_completion_rate"], "f0_authorized": False}, sort_keys=True))

if __name__ == "__main__": main()
