#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json, require, sha_file

CONTRACT_STATUS="FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY"
AUTH_STATUS="AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY_MEASUREMENT"
ORDER_SALT="E2-R17-SINGLE-CASE-FROZEN-STATE-STABILITY-EVAL-ORDER-v1"


def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); os.replace(t,p)
def append(path:Path,d:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8") as h: h.write(json.dumps(d,ensure_ascii=False,sort_keys=True)+"\n"); h.flush(); os.fsync(h.fileno())
def rows(path:Path,key:str)->dict[str,dict[str,Any]]:
    out={}
    if not path.exists(): return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r=json.loads(line); v=str(r[key]); require(v not in out,f"duplicate {key}: {v}"); out[v]=r
    return out
def ordered(rep:int,task:str)->list[str]: return sorted(("win_c","first_fail"),key=lambda arm:hashlib.sha256(f"{ORDER_SALT}|{rep}|{task}|{arm}".encode()).hexdigest())

def validate(cpath:Path,apath:Path)->tuple[dict[str,Any],dict[str,Any]]:
    c=load_json(cpath); a=load_json(apath); csha=sha_file(cpath)
    require(c.get("status")==CONTRACT_STATUS,"stability contract drift"); require(a.get("status")==AUTH_STATUS and a.get("contract_sha256")==csha,"stability authorization drift")
    au=a.get("authority") or {}; require(au.get("scientific_experiment") is True and au.get("measurement_only") is True,"stability measurement authority absent")
    for k in ("updater","analyzer","second_backbone","public_benchmark","e3_confirmation","paper_promotion","submission"): require(au.get(k) is False,f"stability authority overbroad: {k}")
    scope=a.get("execution_scope") or {}; require(scope.get("measurement_child")=="E2-R17-SINGLE-CASE-FIRST-FAIL-STABILITY","stability child drift"); require(scope.get("measurement_replicates")==[1,2],"stability replicate drift"); require(scope.get("allowed_task_ids")==c["heldout_task_ids"],"stability task scope drift")
    require(scope.get("learned_states")==c["learned_states"],"stability learned-state scope drift")
    for label,item in c["bound_code"].items(): p=ROOT/item["path"]; require(p.is_file() and sha_file(p)==item["sha256"],f"stability bound code drift: {label}")
    for state in c["learned_states"]:
        skill=Path(state["skill_post_path"]); receipt=Path(state["update_receipt_path"]); require(skill.is_file() and sha_file(skill)==state["skill_post_sha256"],f"stability skill drift: {state['arm']}"); require(receipt.is_file() and sha_file(receipt)==state["update_receipt_sha256"],f"stability parent receipt drift: {state['arm']}")
    return c,a

def acquire_lease(p:Path,csha:str,asha:str)->None:
    p.parent.mkdir(parents=True,exist_ok=True); d={"schema_version":"1.0","artifact_type":"e2-r17-single-case-first-fail-stability-lineage-lease","status":"RUNNING_FIRST_FAIL_STABILITY","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"pid":os.getpid(),"pgid":os.getpgrp(),"contract_sha256":csha,"authorization_sha256":asha,"exactly_once":True,"partial_effect_read":False}; fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try: os.write(fd,(json.dumps(d,sort_keys=True)+"\n").encode()); os.fsync(fd)
    finally: os.close(fd)
def check_lease(p:Path,csha:str,asha:str)->None:
    d=load_json(p); require(d.get("status")=="RUNNING_FIRST_FAIL_STABILITY" and int(d.get("pid"))==os.getpid(),"stability lease owner drift"); require(d.get("contract_sha256")==csha and d.get("authorization_sha256")==asha,"stability lease binding drift")
def seal(p:Path,status:str)->None:
    d=load_json(p); d["status"]=status; d["sealed_at_utc"]=datetime.now(timezone.utc).isoformat(timespec="seconds"); atomic(p,d)

def verify_eval(row:dict[str,Any],state:dict[str,Any])->None:
    sp=Path(row["summary_path"]); rp=Path(row["trajectory_ref_path"]); require(sp.is_file() and sha_file(sp)==row["summary_sha256"],"stability eval summary drift"); require(rp.is_file() and sha_file(rp)==row["trajectory_ref_sha256"],"stability eval ref drift"); sd=load_json(sp); require(sd.get("status")=="COMPLETED" and int(sd.get("k"))==1,"stability eval status/K drift"); require(sd.get("skill_pre_sha256")==state["skill_post_sha256"] and sd.get("updater_receipt_sha256")==state["update_receipt_sha256"],"stability learned-state binding drift"); ref=load_json(rp); traj=Path(ref["trajectory_path"]); require(traj.is_file() and sha_file(traj)==ref["trajectory_sha256"],"stability trajectory drift")
    # Outcome embargo: do not read the heldout score.
def ensure_eval(*,c:dict[str,Any],auth:Path,identity:Path,actor_python:Path,actor_env:dict[str,str],rep:int,arm:str,task:str,state_binding:dict[str,Any],root:Path)->dict[str,Any]:
    state=root/f"replicate_{rep}"/arm; manifest=state/"completed_eval_tasks.jsonl"; existing=rows(manifest,"task_id")
    if task in existing: verify_eval(existing[task],state_binding); return existing[task]
    eroot=state/"evaluation"/task
    if eroot.exists() and any(eroot.rglob("*")): raise RuntimeError(f"partial ambiguous stability eval: rep{rep}/{arm}/{task}")
    ledger=state/"provider_budget.sqlite3"; summary=eroot/"evaluation_summary.json"; skill_dir=str(Path(state_binding["skill_post_path"]).parent)
    cmd=[str(actor_python),str(ROOT/"scripts/run_e2_r17_actor_pool_single_case_stability.py"),"--env-file",c["env_file"],"--suite-root",c["suite"]["root"],"--mindmemos-root",c["mindmemos"]["root"],"--run-root",str(eroot),"--identity",str(identity),"--authorization",str(auth.resolve()),"--skill-source",skill_dir,"--updater-receipt",state_binding["update_receipt_path"],"--mode","e1","--model",c["actor"]["requested_model"],"--task-id",task,"--k","1","--prefix-ks","1","--max-turns",str(c["actor"]["max_turns"]),"--max-output-tokens",str(c["actor"]["max_output_tokens"]),"--concurrency","1","--provider-budget-ledger",str(ledger),"--provider-total-call-limit","191","--provider-per-unit-call-limit","11","--output",str(summary)]
    r=subprocess.run(cmd,cwd=ROOT,env=actor_env,capture_output=True,text=True)
    if r.returncode!=0: atomic(state/f"eval_failure_{task}.json",{"status":"TECHNICAL_FAILURE","replicate":rep,"arm":arm,"task_id":task,"returncode":r.returncode,"stdout_tail":r.stdout[-3000:],"stderr_tail":r.stderr[-3000:],"provider_relaunch_authorized":False}); raise RuntimeError(f"stability eval failed rep{rep}/{arm}/{task}")
    ref=eroot/"cases"/task/"rollout_0/r17_trajectory_ref.json"; require(summary.is_file() and ref.is_file(),"stability actor missing output"); row={"task_id":task,"summary_path":str(summary),"summary_sha256":sha_file(summary),"trajectory_ref_path":str(ref),"trajectory_ref_sha256":sha_file(ref),"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}; verify_eval(row,state_binding); append(manifest,row); return row

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--authorization",type=Path,required=True); a=ap.parse_args(); c,_=validate(a.contract,a.authorization); csha=sha_file(a.contract); asha=sha_file(a.authorization); lease=Path(c["lineage_lease_path"]); acquire_lease(lease,csha,asha); success=False
    try:
        run=Path(c["run_root"]); require(not run.exists(),"stability run root must be fresh"); run.mkdir(parents=True)
        actor_python,actor_env=validate_actor_runtime({"runtime":c["actor_runtime"]}); actor_env["LITELLM_LOCAL_MODEL_COST_MAP"]="True"; identity=ROOT/c["model_identity"]["path"]; require(identity.is_file() and sha_file(identity)==c["model_identity"]["sha256"],"stability identity drift")
        states={x["arm"]:x for x in c["learned_states"]}; require(set(states)=={"win_c","first_fail"},"stability state set drift")
        for rep in c["measurement_replicates"]:
            for task in c["heldout_task_ids"]:
                for arm in ordered(rep,task): check_lease(lease,csha,asha); ensure_eval(c=c,auth=a.authorization,identity=identity,actor_python=actor_python,actor_env=actor_env,rep=rep,arm=arm,task=task,state_binding=states[arm],root=run)
        rows_out=[]
        for rep in c["measurement_replicates"]:
            for arm in ("win_c","first_fail"):
                state=run/f"replicate_{rep}"/arm; em=state/"completed_eval_tasks.jsonl"; erows=rows(em,"task_id"); require(list(erows)==c["heldout_task_ids"],f"stability completion drift rep{rep}/{arm}"); ledger=ProviderBudgetLedger(path=state/"provider_budget.sqlite3",contract_sha256=csha,authorization_sha256=asha,total_limit=191,per_unit_limit=11,allow_create=False); rows_out.append({"replicate":rep,"arm":arm,"eval_manifest_path":str(em),"eval_manifest_sha256":sha_file(em),"completed_heldout_tasks":len(erows),"provider_budget":ledger.snapshot().to_dict()})
        summary={"schema_version":"1.0","artifact_type":"e2-r17-single-case-first-fail-stability-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED_PENDING_SEPARATE_STABILITY_ANALYSIS","contract_sha256":csha,"authorization_sha256":asha,"case_stream":"e1-tsr-00","measurement_replicates":[1,2],"arms":["win_c","first_fail"],"rows":rows_out,"new_learned_states":0,"measurement_states":4,"heldout_rollout_units":72,"inference_performed":False,"partial_effect_read":False,"analyzer_run":False,"paper_promotion_authority":False}; atomic(run/"summary/stability_summary.json",summary); success=True; print(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)); return 0
    finally:
        if lease.exists(): seal(lease,"COMPLETED_FIRST_FAIL_STABILITY" if success else "FAIL_CLOSED_FIRST_FAIL_STABILITY")
if __name__=="__main__": raise SystemExit(main())
