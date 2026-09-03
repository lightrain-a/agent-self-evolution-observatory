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
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_v4_build import (
    CONTRACT_OUTPUT as STATIC_CONTRACT, OUTPUT_BUNDLE, QUAL_OUTPUT as STATIC_QUAL,
    TOOL_CALL_CAP, load_cases,
)
from research_pipeline.agent_constraint_externality_sq0_v4_cases import evaluate_case_from_state

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_PYTHON = ROOT / "runtimes/appworld-constraint-externality-py312/bin/python"
SELECTION = GENERATED / "agent-constraint-externality-capability-backbone-selection-final-20260903.json"
TRANSPORT_RESULT = GENERATED / "agent-constraint-externality-sq0-v2r1-transport-result-20260903.json"
V3_CLOSEOUT = GENERATED / "agent-constraint-externality-sq0-v3-closeout-20260903.json"
V3_ROOT_CAUSE = GENERATED / "agent-constraint-externality-sq0-v3-root-cause-20260903.json"
MODEL_PROFILE = "AtomGit-mimo-v2.5-pro"
MODEL_ID = "mimo-v2.5-pro"
PROVIDER = "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY"
BASE_URL = "https://llm-api.atomgit.com/v1"
CONTEXT_WINDOW = 1_000_000
RETRY_MAX_ATTEMPTS = 1
MODEL_ROUND_CAP = 56
CASE_COUNT = 12
EXECUTION_ID = "CODINGPLAN-MIMO25PRO-SQ0-SEMANTIC-FAILURE-V4"
AUTH_OUTPUT = GENERATED / "agent-constraint-externality-sq0-v4-human-authorization-20260903.json"
Q1_OUTPUT = GENERATED / "agent-constraint-externality-sq0-v4-mimo25pro-mcp-q1-predispatch-20260903.json"
EXEC_CONTRACT = GENERATED / "agent-constraint-externality-sq0-v4-mimo25pro-execution-contract-20260903.json"
RESULT_OUTPUT = GENERATED / "agent-constraint-externality-sq0-v4-mimo25pro-result-20260903.json"


class SQ0Stop(RuntimeError):
    pass


def _read(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding="utf-8"))
def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")

def _verified(path: Path, status: str | None = None) -> dict[str, Any]:
    x=_read(path)
    if x.get("object_id") != OBJECT_ID: raise SQ0Stop(f"Object mismatch: {path}")
    if status is not None and x.get("status") != status: raise SQ0Stop(f"Status mismatch: {path}: {x.get('status')}")
    claimed=x.get("content_sha256")
    if claimed is not None:
        u=dict(x); u.pop("content_sha256",None)
        if claimed != sha256_value(u): raise SQ0Stop(f"Content hash mismatch: {path}")
    return x

def _patch_live() -> None:
    live.MODEL_PROFILE=MODEL_PROFILE; live.TOOL_CALL_CAP=TOOL_CALL_CAP; live.MODEL_ROUND_CAP=MODEL_ROUND_CAP

def _config() -> str:
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
system_prompt = "This is an AppWorld simulation. Complete the target-local SQ0-V4 task using only tools whose names begin mcp__appworld__. Any path beginning ~/ is virtual AppWorld state and MUST be accessed through mcp__appworld__file_system__ tools; never call native read_file, write_file, edit_file, bash, web, skill, task, agent, or other host tools. Preserve unrelated AppWorld state. Batch independent AppWorld tool calls when safe."
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

def _agents() -> str:
    return "# SQ0-V4 AppWorld target-failure qualification\nUse only `mcp__appworld__*` tools. Any `~/` path is inside AppWorld, never the host. Never use read_file, write_file, edit_file, bash, web, memory, agent, skill, task/team, or AtomGit tools. Complete only the user target task and preserve unrelated state.\n"

def _mcp(case_id: str, root: Path, progress: Path, task_id: str) -> dict[str, Any]:
    args=["-m","research_pipeline.agent_constraint_externality_sq0_v4_mcp_bridge","--bundle",str(OUTPUT_BUNDLE),"--case-id",case_id,"--runtime-root",str(root/"appworld"),"--task-id",task_id,"--experiment-name","ace-sq0-mimo25pro-v4","--progress",str(progress),"--tool-call-cap",str(TOOL_CALL_CAP)]
    return {"mcpServers":{"appworld":{"command":str(APPWORLD_PYTHON),"args":args,"env":{"PYTHONPATH":str(ROOT)},"timeout_ms":30000,"trust":True}}}

def _prepare(case_id: str, root: Path) -> tuple[Path,Path,Path,dict[str,Any]]:
    root=root.resolve(); atom=root/"atomcode-home"; work=root/"atomcode-workdir"; progress=root/"bridge-progress.json"
    atom.mkdir(parents=True,exist_ok=False); work.mkdir(parents=True,exist_ok=False)
    auth=Path.home()/".atomcode/auth.toml"
    if not auth.is_file(): raise SQ0Stop("AtomCode auth.toml missing.")
    shutil.copy2(auth,atom/"auth.toml"); os.chmod(atom/"auth.toml",0o600)
    (atom/"config.toml").write_text(_config(),encoding="utf-8"); (work/"AGENTS.md").write_text(_agents(),encoding="utf-8")
    task_id="acesq0"+case_id.lower().replace("-","")+"_1"
    return atom,work,progress,_mcp(case_id,root,progress,task_id)

def _unit_id(case_id: str) -> str: return f"sq0v4:{MODEL_ID}|{case_id}|1"

def _freeze_inputs() -> tuple[dict[str,Any],dict[str,Any],dict[str,Any]]:
    static=_verified(STATIC_CONTRACT,"SQ0_V4_STATIC_DESIGN_READY")
    qual=_verified(STATIC_QUAL,"SQ0_V4_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS")
    selected=_verified(SELECTION,"CAPABILITY_BACKBONE_SELECTED_MIMO25PRO_PASS")
    stopped=_verified(TRANSPORT_RESULT,"SQ0_V2R1_TRANSPORT_QUALIFICATION_PASS")
    v3_closeout=_verified(V3_CLOSEOUT,"SQ0_V3_TOO_EASY_FUTILITY_CLOSEOUT")
    v3_root=_verified(V3_ROOT_CAUSE,"SQ0_V3_TNF_TOO_EASY_FG_NEAR_TARGET_WINDOW")
    if selected.get("selected_backbone",{}).get("model_id") != MODEL_ID: raise SQ0Stop("Selected backbone drifted.")
    if stopped.get("native_tool_attempts") != [] or stopped.get("prohibited_tool") is not None: raise SQ0Stop("V2-R1 transport qualification is not clean.")
    if v3_closeout.get("authority",{}).get("sq0_v4_execution") is not False or v3_root.get("authority",{}).get("sq0_v4_execution") is not False:
        raise SQ0Stop("V3 closeout must not pre-authorize V4 execution.")
    if static.get("v3_closeout_content_sha256") != v3_closeout.get("content_sha256") or static.get("v3_root_cause_content_sha256") != v3_root.get("content_sha256"):
        raise SQ0Stop("V4 static design is not bound to the frozen V3 closeout/root cause.")
    return static,qual,selected

def qualify_q1() -> dict[str,Any]:
    _patch_live(); case=load_cases()[0]
    with tempfile.TemporaryDirectory(prefix="ace-sq0-q1-") as d:
        root=Path(d); atom,work,progress,mcp=_prepare(case["case_id"],root); proc=None; done=threading.Event(); errors=[]
        try:
            proc,base,token=live.start_daemon(atom_home=atom,workdir=work,log_path=root/"atomcode-daemon.log")
            (atom/"mcp.json").write_text(json.dumps(mcp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            live.http_json(base,token,"/live/mode",method="POST",body={"mode":"build"})
            used_before=int(live.codingplan_usage(base,token)["used"])
            def stream() -> None:
                req=urllib.request.Request(base+"/live",headers={"Authorization":"Bearer "+token})
                try:
                    with urllib.request.urlopen(req,timeout=60) as resp:
                        for _ in resp:
                            if done.is_set(): break
                except Exception as exc:
                    if not done.is_set(): errors.append(f"{type(exc).__name__}: {exc}")
            th=threading.Thread(target=stream,daemon=True); th.start(); deadline=time.time()+45
            while time.time()<deadline:
                if errors: raise SQ0Stop(errors[-1])
                if progress.is_file() and _read(progress).get("status")=="TOOLS_LISTED": break
                time.sleep(.1)
            else: raise SQ0Stop("SQ0 Q1 did not list AppWorld MCP tools.")
            used_after=int(live.codingplan_usage(base,token)["used"]); live.http_json(base,token,"/live/stop",method="POST",body={}); done.set(); th.join(timeout=2)
            state=_read(progress); payload={"schema_version":"ace-sq0-v4-mimo25pro-q1-v1","object_id":OBJECT_ID,"status":"SQ0_V4_MIMO25PRO_MCP_PREDISPATCH_PASS","case_id":case["case_id"],"model_profile":MODEL_PROFILE,"model_id":MODEL_ID,"session_mcp_progress_status":state.get("status"),"session_mcp_tool_count":int(state.get("tool_count",0)),"codingplan_window_used_before":used_before,"codingplan_window_used_after":used_after,"codingplan_model_requests":used_after-used_before,"scientific_dispatch_sent":False,"scientific_outcomes_observed":0,"runner_source_sha256":sha256_file(Path(__file__)),"bridge_source_sha256":sha256_file(ROOT/"research_pipeline/agent_constraint_externality_sq0_v4_mcp_bridge.py"),"bundle_sha256":sha256_file(OUTPUT_BUNDLE)}
            if payload["codingplan_model_requests"]!=0 or payload["session_mcp_progress_status"]!="TOOLS_LISTED" or payload["session_mcp_tool_count"]<=0: raise SQ0Stop("SQ0 Q1 crossed zero-request boundary.")
            payload["content_sha256"]=sha256_value(payload); return payload
        finally:
            done.set()
            if proc is not None: live.terminate_process(proc)

def freeze() -> dict[str,Any]:
    static,qual,selected=_freeze_inputs(); q1=qualify_q1(); _write(Q1_OUTPUT,q1)
    auth={"schema_version":"ace-sq0-human-authorization-v1","object_id":OBJECT_ID,"status":"USER_AUTHORIZED_SQ0_V4_AFTER_V3_FUTILITY_CLOSEOUT_AND_STATIC_PASS","authorization_basis":"USER_CONTINUATION_AFTER_SQ0_V3_FUTILITY_CLOSEOUT_AND_SQ0_V4_STATIC_PASS","selected_backbone_content_sha256":selected["content_sha256"],"static_contract_content_sha256":static["content_sha256"],"static_qualification_content_sha256":qual["content_sha256"],"authority":{"sq0_v4_execution":True,"f0_r1":False,"probe":False,"p1":False,"toolsandbox":False,"appworld_ul":False,"paper_claim":False},"scientific_outcomes_observed":0}
    auth["content_sha256"]=sha256_value(auth); _write(AUTH_OUTPUT,auth)
    inherited_transport=_verified(TRANSPORT_RESULT,"SQ0_V2R1_TRANSPORT_QUALIFICATION_PASS")
    contract={"schema_version":"ace-sq0-v4-mimo25pro-execution-contract-v1","object_id":OBJECT_ID,"execution_id":EXECUTION_ID,"status":"SQ0_V4_MIMO25PRO_EXECUTION_AUTHORIZED","human_authorization_content_sha256":auth["content_sha256"],"q1_content_sha256":q1["content_sha256"],"static_contract_content_sha256":static["content_sha256"],"static_qualification_content_sha256":qual["content_sha256"],"selected_backbone_content_sha256":selected["content_sha256"],"inherited_transport_result_content_sha256":inherited_transport["content_sha256"],"transport_inherited_without_new_model_request":True,"model":{"profile":MODEL_PROFILE,"id":MODEL_ID,"context_window":CONTEXT_WINDOW,"retry_max_attempts":RETRY_MAX_ATTEMPTS},"harness":{"id":"ATOMCODE_CODINGPLAN_MCP_V1","sq0_bridge":True,"tool_call_cap":TOOL_CALL_CAP,"model_round_cap_per_case":MODEL_ROUND_CAP,"retry_allowed":False,"replacement_allowed":False,"ai_session_naming":False,"subagents":False},"panel":{"development_iteration":4,"case_count":CASE_COUNT,"case_ids":[c["case_id"] for c in load_cases()],"one_episode_per_case":True,"confirmatory_reuse":False},"gate":{"usable_failure_rate_min":0.75,"usable_failure_rate_max":0.90,"non_semantic_failure_invalidates_qualification":True},"execution_policy":{"durable_dispatch_before_model_request":True,"unknown_after_dispatch_replay":False,"partial_outcome_redesign":False,"aggregate_read_only_after_all_terminal_or_futility_proven":True,"futility_early_stop":{"acceptable_final_failure_counts":[9,10],"stop_too_easy_if_target_success_count_exceeds":3,"stop_too_hard_if_usable_failure_count_exceeds":10,"undispatched_cases_are_never_replaced":True}},"authority":{"sq0_v4_execution":True,"f0_r1":False,"probe":False,"p1":False,"toolsandbox":False,"appworld_ul":False,"paper_claim":False},"scientific_outcomes_observed":0}
    contract["content_sha256"]=sha256_value(contract); _write(EXEC_CONTRACT,contract)
    return {"authorization":auth,"q1":q1,"contract":contract}

def _dispatch(case: dict[str,Any],progress:dict[str,Any],usage:dict[str,Any])->dict[str,Any]:
    return {"schema_version":"ace-sq0-v4-exactly-once-ledger-v1","object_id":OBJECT_ID,"execution_id":EXECUTION_ID,"event":"DISPATCH","unit_id":_unit_id(case["case_id"]),"case_id":case["case_id"],"kind":case["kind"],"provider":PROVIDER,"model_profile":MODEL_PROFILE,"model_id":MODEL_ID,"harness":"ATOMCODE_CODINGPLAN_MCP_V1","prompt_sha256":sha256_value(case["task_instruction"]),"initial_snapshot_sha256":progress["initial_snapshot_sha256"],"tool_call_cap":TOOL_CALL_CAP,"model_round_cap":MODEL_ROUND_CAP,"codingplan_window_before":usage,"dispatch_time_ns":time.time_ns(),"attempt":1,"retry_allowed":False,"replacement_allowed":False}

def _futility_status(completions:list[dict[str,Any]])->str|None:
    if any(bool(r.get("non_semantic_failure")) for r in completions):
        return "SQ0_V4_QUALIFICATION_INVALID_NON_SEMANTIC_FAILURE_STOP"
    successes=sum(bool(r.get("target_success")) for r in completions)
    failures=sum(bool(r.get("usable_target_failure")) for r in completions)
    if successes>3:
        return "SQ0_V4_FUTILITY_TOO_EASY_STOP"
    if failures>10:
        return "SQ0_V4_FUTILITY_TOO_HARD_STOP"
    return None

def execute(*,runtime_root:Path,ledger_path:Path)->None:
    _patch_live(); _verified(EXEC_CONTRACT,"SQ0_V4_MIMO25PRO_EXECUTION_AUTHORIZED"); cases=load_cases(); states=live.ledger_states(ledger_path); runtime_root=runtime_root.resolve(); ledger_path=ledger_path.resolve()
    for case in cases:
        uid=_unit_id(case["case_id"]); state=states.get(uid)
        if state=="COMPLETION": continue
        if state is not None: raise SQ0Stop(f"Refusing replay of dispatched SQ0 unit {uid}: {state}")
        root=runtime_root/case["case_id"].lower();
        if root.exists(): raise SQ0Stop(f"Refusing overwrite: {root}")
        root.mkdir(parents=True); atom,work,progress,mcp=_prepare(case["case_id"],root); proc=None; result=None; before={}; after={}
        try:
            proc,base,token=live.start_daemon(atom_home=atom,workdir=work,log_path=root/"atomcode-daemon.log"); (atom/"mcp.json").write_text(json.dumps(mcp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); live.http_json(base,token,"/live/mode",method="POST",body={"mode":"build"})
            def before_submit()->dict[str,Any]:
                progress_state=_read(progress)
                if progress_state.get("status")!="TOOLS_LISTED": raise SQ0Stop("SQ0 MCP tools not listed before dispatch.")
                usage=live.codingplan_usage(base,token)
                if int(usage["remaining"]) < MODEL_ROUND_CAP+5: raise SQ0Stop("Insufficient CodingPlan window headroom.")
                live.append_jsonl(ledger_path,_dispatch(case,progress_state,usage)); return {"usage_before":usage}
            result=live.run_live_turn(base=base,token=token,instruction=case["task_instruction"],progress_path=progress,before_submit=before_submit,timeout_seconds=480)
            before=dict(result["pre_submit"]["usage_before"]); time.sleep(.3); after=live.codingplan_usage(base,token)
            if result["prohibited_tool"] or result["error_message"]:
                live.append_jsonl(ledger_path,{"schema_version":"ace-sq0-v4-exactly-once-ledger-v1","object_id":OBJECT_ID,"execution_id":EXECUTION_ID,"event":"FAILURE","unit_id":uid,"case_id":case["case_id"],"failure_class":"HARNESS_OR_PROVIDER_INTERFACE_STOP","message":str(result["prohibited_tool"] or result["error_message"])[:400],"codingplan_window_after":after,"time_ns":time.time_ns(),"retry_attempted":False}); raise SQ0Stop("SQ0 interface/harness failure after dispatch.")
        finally:
            if proc is not None: live.terminate_process(proc)
        if result is None: raise SQ0Stop("SQ0 live result missing.")
        deadline=time.time()+15
        while time.time()<deadline:
            if progress.is_file() and _read(progress).get("status") in {"CLOSED_STATE_SAVED","STATE_SAVED_AFTER_TOOL","TOOL_CALL_CAP_EXCEEDED"}: break
            time.sleep(.1)
        ps=_read(progress); tool_count=int(ps.get("tool_call_count",0)); normal=result["stop_reason"]=="stopped" and tool_count<=TOOL_CALL_CAP
        target=evaluate_case_from_state(case,source_db_root=Path(ps["source_db_root"]),changes_db_root=Path(ps["changes_db_root"]),measurement_root=root/"measurement-full-dbs")
        nonsemantic=not normal; usable_failure=normal and not target
        live.append_jsonl(ledger_path,{"schema_version":"ace-sq0-v4-exactly-once-ledger-v1","object_id":OBJECT_ID,"execution_id":EXECUTION_ID,"event":"COMPLETION","unit_id":uid,"case_id":case["case_id"],"kind":case["kind"],"tool_loop_completed":normal,"target_success":bool(target),"usable_target_failure":usable_failure,"non_semantic_failure":nonsemantic,"atomcode_stop_reason":result["stop_reason"],"appworld_tool_call_count":tool_count,"model_round_count":int(result["model_round_count"]),"prompt_tokens_total":int(result["prompt_tokens_total"]),"completion_tokens_total":int(result["completion_tokens_total"]),"codingplan_window_before":before,"codingplan_window_after":after,"bridge_progress_sha256":sha256_file(progress),"time_ns":time.time_ns()}); states=live.ledger_states(ledger_path)
        completions=[r for r in live.ledger_rows(ledger_path) if r.get("event")=="COMPLETION"]
        if _futility_status(completions) is not None:
            return

def adjudicate(ledger_path:Path)->dict[str,Any]:
    rows=live.ledger_rows(ledger_path); states=live.ledger_states(ledger_path); cases=load_cases(); expected={_unit_id(c["case_id"]) for c in cases}
    if any(state not in {"COMPLETION","FAILURE"} for state in states.values()): raise SQ0Stop("SQ0 ledger has unknown-after-dispatch state.")
    completions=[r for r in rows if r["event"]=="COMPLETION"]
    failures_rows=[r for r in rows if r["event"]=="FAILURE"]
    if failures_rows:
        status="SQ0_V4_QUALIFICATION_INVALID_NON_SEMANTIC_FAILURE_STOP"
    else:
        futility=_futility_status(completions)
        if set(states)==expected and len(completions)==CASE_COUNT:
            invalid=[r["unit_id"] for r in completions if r["non_semantic_failure"]]
            failure_count=sum(bool(r["usable_target_failure"]) for r in completions); rate=failure_count/CASE_COUNT
            if invalid: status="SQ0_V4_QUALIFICATION_INVALID_NON_SEMANTIC_FAILURE_STOP"
            elif 0.75<=rate<=0.90: status="SQ0_V4_TARGET_FAILURE_QUALIFICATION_PASS"
            elif rate<0.75: status="SQ0_V4_TARGET_CHALLENGE_TOO_EASY_STOP"
            else: status="SQ0_V4_TARGET_CHALLENGE_TOO_HARD_STOP"
        elif futility in {"SQ0_V4_FUTILITY_TOO_EASY_STOP","SQ0_V4_FUTILITY_TOO_HARD_STOP","SQ0_V4_QUALIFICATION_INVALID_NON_SEMANTIC_FAILURE_STOP"}:
            status=futility
        else:
            raise SQ0Stop("Incomplete SQ0-V4 panel without preregistered futility proof.")
    invalid=[r["unit_id"] for r in completions if r.get("non_semantic_failure")]
    failure_count=sum(bool(r.get("usable_target_failure")) for r in completions); success_count=sum(bool(r.get("target_success")) for r in completions); completed=len(completions); remaining=CASE_COUNT-completed
    observed_rate=failure_count/completed if completed else None
    max_final_failures=failure_count+remaining; min_final_failures=failure_count
    result={"schema_version":"ace-sq0-v4-mimo25pro-result-v1","object_id":OBJECT_ID,"execution_id":EXECUTION_ID,"status":status,"provider":PROVIDER,"model_profile":MODEL_PROFILE,"model_id":MODEL_ID,"harness":"ATOMCODE_CODINGPLAN_MCP_V1","planned_case_count":CASE_COUNT,"completed_case_count":completed,"remaining_undispatched_case_count":remaining,"usable_target_failure_count":failure_count,"observed_usable_target_failure_rate":observed_rate,"target_success_count":success_count,"possible_final_failure_count_interval":[min_final_failures,max_final_failures],"acceptable_final_failure_counts":[9,10],"futility_proven":status.startswith("SQ0_V4_FUTILITY_") or status=="SQ0_V4_QUALIFICATION_INVALID_NON_SEMANTIC_FAILURE_STOP","non_semantic_failure_units":invalid+[r["unit_id"] for r in failures_rows],"scientific_model_round_count":sum(int(r.get("model_round_count",0)) for r in completions),"appworld_tool_call_total":sum(int(r.get("appworld_tool_call_count",0)) for r in completions),"prompt_tokens_total":sum(int(r.get("prompt_tokens_total",0)) for r in completions),"completion_tokens_total":sum(int(r.get("completion_tokens_total",0)) for r in completions),"ledger_sha256":sha256_file(ledger_path),"development_only":True,"development_iteration":4,"confirmatory_reuse":False,"scientific_effects_observed":0,"authority":{"sq0_v4_closed":True,"f0_r1":False,"probe":False,"p1":False,"toolsandbox":False,"appworld_ul":False,"paper_claim":False}}
    result["content_sha256"]=sha256_value(result); return result

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument("--freeze",action="store_true"); p.add_argument("--runtime-root",type=Path); p.add_argument("--ledger",type=Path); p.add_argument("--result-output",type=Path,default=RESULT_OUTPUT); a=p.parse_args()
    if a.freeze:
        x=freeze(); print(json.dumps({"authorization":x["authorization"]["status"],"q1":x["q1"]["status"],"q1_model_requests":x["q1"]["codingplan_model_requests"],"contract":x["contract"]["status"],"sq0_authorized":True,"f0_r1_authorized":False},sort_keys=True)); return
    if a.runtime_root is None or a.ledger is None: raise SystemExit("--runtime-root and --ledger required")
    execute(runtime_root=a.runtime_root,ledger_path=a.ledger); result=adjudicate(a.ledger.resolve()); _write(a.result_output.resolve(),result)
    print(json.dumps({"status":result["status"],"usable_target_failure_count":result["usable_target_failure_count"],"observed_usable_target_failure_rate":result["observed_usable_target_failure_rate"],"completed_case_count":result["completed_case_count"],"scientific_model_round_count":result["scientific_model_round_count"],"f0_r1_authorized":False},sort_keys=True))

if __name__=="__main__": main()
