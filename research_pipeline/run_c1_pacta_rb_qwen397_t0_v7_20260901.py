#!/usr/bin/env python3
"""T0-v7: continue only the seven untouched ReasoningBank source trajectories after the v6 timeout-template compatibility stop."""
from __future__ import annotations
import argparse,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import yaml
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json,sha256_file
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime_v7 import Container,ROOTFUL_DOCKER_HOST,SOURCE_MAX_COMPLETION_TOKENS,PACTA_FIRST_DECISION_BUDGET,execute_trajectory
from research_pipeline.run_c1_pacta_rb_qwen397_t05_images_20260901 import SPECS,image_repo

OFFICIAL=Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
OFFICIAL_COMMIT="ed80611788292ea739f1effd31f16c53823b8a0d"
CONFIG=OFFICIAL/"third_party/src/minisweagent/config/extra/swebench.yaml"
CONFIG_SHA256="d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41"
POOL=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1/fresh-pool.json")
SOURCE_BUDGET_Q0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-source-budget-q0-20260901-v2/qualification-result.json")
SOURCE_BUDGET_Q0_SHA256="668848d930db9087617fbe839c11d77ca3d57e75a2787a32605ce13ddb530e25"
DEFAULT=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t0-rootful-source-20260901-v7")
MODEL="qwen3.5-397b-a17b"
PRIOR_VALID_COUNT=2
CONSUMED_SOURCES=("pydata__xarray-4966","scikit-learn__scikit-learn-14496","psf__requests-1766","matplotlib__matplotlib-24627")
FUTURES={
"sphinx-doc__sphinx-8593":"sphinx-doc__sphinx-7748",
"mwaskom__seaborn-3187":"mwaskom__seaborn-3069",
"sympy__sympy-15599":"sympy__sympy-18189",
"astropy__astropy-7166":"astropy__astropy-14096",
"django__django-13449":"django__django-11400",
"pylint-dev__pylint-7080":"pylint-dev__pylint-8898",
"pytest-dev__pytest-5840":"pytest-dev__pytest-5809"}

def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def require_key():
    k=os.environ.get("AA_API_KEY","")
    if not k:raise RuntimeError("STOP_PROVIDER_CREDENTIAL_NOT_CONFIGURED")
    return k

def verify_frozen()->dict[str,Any]:
    if sha256_file(SOURCE_BUDGET_Q0)!=SOURCE_BUDGET_Q0_SHA256:raise RuntimeError("source budget Q0 hash drift")
    q=json.loads(SOURCE_BUDGET_Q0.read_text())
    if q.get("decision")!="SOURCE_TRAJECTORY_BUDGET_16384_QUALIFIED" or q.get("qualified")!=6 or q.get("source_trajectory_output_budget")!=SOURCE_MAX_COMPLETION_TOKENS:raise RuntimeError("source budget Q0 not qualified")
    if q.get("pacta_first_decision_budget")!=PACTA_FIRST_DECISION_BUDGET:raise RuntimeError("first-decision budget drift")
    if sha256_file(CONFIG)!=CONFIG_SHA256:raise RuntimeError("official config drift")
    head=subprocess.run(["git","-C",str(OFFICIAL),"rev-parse","HEAD"],text=True,capture_output=True,check=True).stdout.strip()
    if head!=OFFICIAL_COMMIT:raise RuntimeError("carrier commit drift")
    return q

def pool_units():return {u["source_task_id"]:u for u in json.loads(POOL.read_text())["units"]}
def digest_map():return {instance:amd64 for instance,_idx,amd64 in SPECS}
def append_jsonl(path:Path,row:dict[str,Any]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8") as h:h.write(json.dumps(row,sort_keys=True)+"\n");h.flush();os.fsync(h.fileno())

def prepare(root:Path)->dict[str,Any]:
    if root.exists():raise RuntimeError(f"T0-v7 root exists; no overwrite/retry: {root}")
    verify_frozen();units=pool_units();digests=digest_map();root.mkdir(parents=True)
    if any(source in FUTURES for source in CONSUMED_SOURCES):raise AssertionError("consumed source leaked into v7")
    schedule=[]
    for seq,instance in enumerate(FUTURES,1):
        u=units[instance];schedule.append({"sequence":seq,"source_task_id":instance,"future_task_id":FUTURES[instance],"repository":u["task_family"],"task_sha256":u["source_task_sha256"],"base_commit":u["source_base_commit"],"digest_ref":f"docker.1ms.run/{image_repo(instance)}@sha256:{digests[instance]}","logical_attempts":1,"selected_memory":"","future_task_executed":False})
    contract={"schema_version":1,"created_at_utc":now(),"experiment":"C1-PACTA-RB-QWEN397-T0-v7-20260901","status":"FROZEN_BEFORE_SOURCE_POLICY","model":MODEL,"source_max_completion_tokens":SOURCE_MAX_COMPLETION_TOKENS,"pacta_first_decision_budget_unchanged":PACTA_FIRST_DECISION_BUDGET,"docker_host":ROOTFUL_DOCKER_HOST,"official_commit":OFFICIAL_COMMIT,"official_config_sha256":CONFIG_SHA256,"source_budget_q0_sha256":SOURCE_BUDGET_Q0_SHA256,"scheduled_source_units":7,"prior_valid_trajectories":PRIOR_VALID_COUNT,"consumed_excluded_sources":list(CONSUMED_SOURCES),"replacement":False,"top_up":False,"logical_attempts_per_source":1,"timeout_template_repair":"Use frozen official AgentConfig.timeout_template when swebench.yaml omits it; keep the 60-second environment timeout unchanged.","rate_limit_transport_recovery":{"max_retries":2,"backoff_seconds":[60,120],"only_when_no_model_content":True},"maximum_total_valid_original_pool_after_v7":9,"writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0,"future_task_executions":0,"forbidden":["rerun consumed source","replacement source","writer","binder","shadow","gate","random_gate","final","future_policy","future_evaluator","model_switch"]}
    atomic_json(root/"contract.json",contract);atomic_json(root/"acquisition-schedule.json",{"schema_version":1,"created_at_utc":now(),"status":"FROZEN","schedule":schedule,"scheduled_count":7,"selection":"all seven untouched fixed units","consumed_sources_excluded":list(CONSUMED_SOURCES),"replacement":False,"top_up":False})
    return {"scheduled":7,"contract_sha256":sha256_file(root/"contract.json"),"schedule_sha256":sha256_file(root/"acquisition-schedule.json")}

def prelaunch(root:Path)->dict[str,Any]:
    if not (root/"contract.json").is_file():raise RuntimeError("prepare first")
    if (root/"prelaunch-qualification.json").exists():raise RuntimeError("prelaunch exists; no overwrite")
    rows=[]
    for item in json.loads((root/"acquisition-schedule.json").read_text())["schedule"]:
        p=root/"prelaunch"/item["source_task_id"];passed=False;error=None;c=None
        try:c=Container(item["digest_ref"],item["base_commit"],p);passed=True
        except Exception as e:error=f"{type(e).__name__}: {e}"
        finally:
            if c is not None:c.cleanup()
        rows.append({"source_task_id":item["source_task_id"],"pass":passed,"error":error,"normalization_path":str(p/"exact-base-normalization.json") if passed else None,"normalization_sha256":sha256_file(p/"exact-base-normalization.json") if passed else None})
    result={"schema_version":1,"created_at_utc":now(),"status":"T0_V7_PRELAUNCH_PASS" if all(r["pass"] for r in rows) else "STOP_T0_V7_PRELAUNCH","qualified":sum(r["pass"] for r in rows),"total":7,"provider_calls":0,"rows":rows};atomic_json(root/"prelaunch-qualification.json",result);return result

def acquire(root:Path)->dict[str,Any]:
    key=require_key();q=verify_frozen();pre=json.loads((root/"prelaunch-qualification.json").read_text())
    if pre.get("status")!="T0_V7_PRELAUNCH_PASS" or pre.get("qualified")!=7:raise RuntimeError("prelaunch not qualified")
    config=yaml.safe_load(CONFIG.read_text());units=pool_units();schedule=json.loads((root/"acquisition-schedule.json").read_text())["schedule"];rows=[];stop_reason=None
    for item in schedule:
        instance=item["source_task_id"]
        row=execute_trajectory(instance,units[instance]["source_task"],item["digest_ref"],root/f"source-{instance}",config,key,MODEL,MODEL,item["base_commit"]);rows.append(row);append_jsonl(root/"acquisition-journal.jsonl",row)
        print(json.dumps({"instance":instance,"validity":row["validity_status"],"terminal":row["terminal_status"],"logical_calls":row["provider_logical_calls"],"transport_attempts":row["provider_transport_attempts"]}),flush=True)
        if row.get("failure_layer") is not None:
            stop_reason=f"{instance}:{row['failure_layer']}";break
    valid=[r for r in rows if r["validity_status"]=="TRAJECTORY_BACKED_VALID"]
    cumulative_valid=PRIOR_VALID_COUNT+len(valid)
    if len(rows)<7:decision="STOP_T0_V7_PROVIDER_OR_IMPLEMENTATION_FAILURE"
    elif len(valid)==7:decision="SOURCE_TRAJECTORY_POOL_PARTIAL_9_STOP_BEFORE_PACTA"
    elif cumulative_valid>=6:decision="SOURCE_TRAJECTORY_POOL_PARTIAL_STOP_BEFORE_PACTA"
    else:decision="HOLD_FRESH_SUPPORT_INSUFFICIENT_AFTER_ACQUISITION"
    result={"schema_version":1,"created_at_utc":now(),"decision":decision,"rows":rows,"source_logical_attempts":len(rows),"N_valid_trajectory_v7":len(valid),"prior_valid_trajectory_count":PRIOR_VALID_COUNT,"cumulative_valid_original_pool":cumulative_valid,"N_valid_repository_v7":len({units[r["source_task_id"]]["task_family"] for r in valid}),"maximum_total_valid_original_pool_after_consumed_exclusion":9,"full_6_plus_5_design_recovered":False,"stop_reason":stop_reason,"source_budget":SOURCE_MAX_COMPLETION_TOKENS,"pacta_first_decision_budget":PACTA_FIRST_DECISION_BUDGET,"writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0,"future_task_executions":0,"claim_authority":"NO_NEW_PACTA_EFFECT_EVIDENCE","active_manuscript":"R9"};atomic_json(root/"support-audit.json",result);return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=DEFAULT);ap.add_argument("--phase",choices=("prepare","prelaunch","acquire"),required=True);a=ap.parse_args();r=prepare(a.root) if a.phase=="prepare" else prelaunch(a.root) if a.phase=="prelaunch" else acquire(a.root);print(json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
