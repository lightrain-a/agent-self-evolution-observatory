#!/usr/bin/env python3
"""Exactly-once, measurement-only completion of Repair2 V3 pair 29."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime

CONTRACT_STATUS="FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_PAIR29_RECOVERY_M1_MEASUREMENT_ONLY"
PREFLIGHT_STATUS="PREFLIGHT_ONLY_E2_R17_DEEPSEEK_V2_REPAIR2_PAIR29_RECOVERY_M1"
AUTHORIZED_STATUS="AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_PAIR29_RECOVERY_M1_MEASUREMENT_ONLY"
ARMS=("win_c","mrw")

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def obj(p:Path)->dict[str,Any]:
 x=json.loads(p.read_text()); req(isinstance(x,dict),f"object expected: {p}"); return x
def lines(p:Path)->list[dict[str,Any]]:
 return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def req(x:bool,m:str)->None:
 if not x: raise RuntimeError(m)
def atom(p:Path,x:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_name(f".{p.name}.{os.getpid()}.tmp")
 with t.open("w") as f: json.dump(x,f,indent=2,sort_keys=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
 os.replace(t,p)
def append(p:Path,x:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("a") as f: f.write(json.dumps(x,sort_keys=True)+"\n"); f.flush(); os.fsync(f.fileno())

def validate(cp:Path,ap:Path,execution:bool)->tuple[dict[str,Any],dict[str,Any],str,str]:
 c,a=obj(cp),obj(ap); cs,aus=sha(cp),sha(ap)
 req(c.get("status")==CONTRACT_STATUS,"pair29 contract not frozen")
 req(a.get("status") in ({AUTHORIZED_STATUS} if execution else {PREFLIGHT_STATUS,AUTHORIZED_STATUS}),"pair29 authorization status")
 req(a.get("contract_sha256")==cs and Path(a.get("contract_path","")).resolve()==cp.resolve(),"authorization/contract bind")
 au=a.get("authority") or {}
 req(au.get("measurement_only") is True and au.get("updater") is False and au.get("analyzer") is False,"authority drift")
 req(au.get("paper_promotion") is False and au.get("public_benchmark") is False,"scope escalation")
 if execution: req(au.get("scientific_experiment") is True,"execution authority absent")
 req(c["measurement"]["new_updater_calls"]==0 and c["measurement"]["replayed_updater_calls"]==0,"updater authority")
 req(c["measurement"]["measurement_states"]==2 and c["measurement"]["heldout_evaluations"]==7,"measurement cardinality")
 req(c["measurement"]["unique_429_logical_unit_recoveries"]==1 and c["measurement"]["never_started_measurements"]==6,"recovery classification")
 req(c["measurement"]["partial_effect_read"] is False,"outcome boundary")
 for key in ("pia_adjudication","canonical_lineage","duplicate_quarantine","recovery_set"):
  b=c["pia1"][key]; p=ROOT/b["path"]; req(p.is_file() and sha(p)==b["sha256"],f"PIA drift: {key}")
 req(obj(ROOT/c["pia1"]["pia_adjudication"]["path"]).get("status")=="PIA1_PASS_V3_RESUME_CANONICAL_V1_PERMANENTLY_QUARANTINED","PIA not passing")
 req(obj(ROOT/c["pia1"]["duplicate_quarantine"]["path"]).get("scientific_inclusion") is False,"duplicate quarantine absent")
 parent=c["parent_v3_provenance"]
 for key in ("contract","authorization"):
  p=Path(parent[f"{key}_path"]); req(p.is_file() and sha(p)==parent[f"{key}_sha256"],f"parent {key} drift")
 req(a.get("parent_v3_provenance")==parent,"auth parent provenance")
 scope=a.get("execution_scope") or {}
 req(scope.get("measurement_child")=="E2-R17-DEEPSEEK-V2-REPAIR2-PAIR29-RECOVERY-M1","child identity")
 req(scope.get("allowed_modes")==["e1"] and scope.get("exact_k")==1,"mode/K")
 req(scope.get("allowed_measurements")==c["allowed_measurements"],"allowed set drift")
 req(scope.get("learned_states")==c["learned_states"],"state scope drift")
 req(scope.get("required_resolved_model")==c["actor"]["resolved_model"],"model drift")
 req(scope.get("identity_artifact_sha256")==c["model_identity"]["sha256"],"identity drift")
 req(scope.get("provider_budget")==c["provider_budget"],"budget scope drift")
 req(len(c["allowed_measurements"])==7 and len({(x["arm"],x["task_id"]) for x in c["allowed_measurements"]})==7,"allowed set count")
 req(sum(x["classification"]=="explicit_429_logical_unit_recovery" for x in c["allowed_measurements"])==1,"unique 429 count")
 for s in c["learned_states"]:
  sk,up,uc=Path(s["skill_post_path"]),Path(s["update_receipt_path"]),Path(s["update_completed_path"])
  req(sha(sk)==s["skill_post_sha256"] and sha(up)==s["update_receipt_sha256"] and sha(uc)==s["update_completed_sha256"],f"state drift: {s['arm']}")
  u=obj(up); req(u.get("status")=="COMPLETED" and u.get("skill_post_sha256")==s["skill_post_sha256"],f"receipt drift: {s['arm']}")
  req(u.get("contract_sha256")==parent["contract_sha256"] and u.get("authorization_sha256")==parent["authorization_sha256"],f"receipt provenance: {s['arm']}")
  req(s["parent_claim_count"]+s["child_provider_total_limit"]==191,f"residual budget: {s['arm']}")
 for b in c["bound_code"].values():
  p=ROOT/b["path"]; req(p.is_file() and sha(p)==b["sha256"],f"code drift: {p}")
 return c,a,cs,aus

def runtime(c:dict[str,Any])->tuple[Path,dict[str,str]]:
 py,env=validate_actor_runtime({"runtime":c["actor_runtime"]}); env["LITELLM_LOCAL_MODEL_COST_MAP"]="True"; return py,env

def command(c:dict[str,Any],ap:Path,state:dict[str,Any],task:str,root:Path,ledger:Path,out:Path,py:Path,pre:bool)->list[str]:
 q=[str(py),str(ROOT/c["bound_code"]["measurement_actor"]["path"]),"--env-file",c["env_file"],"--suite-root",c["suite"]["root"],"--mindmemos-root",c["mindmemos"]["root"],"--run-root",str(root),"--identity",str(ROOT/c["model_identity"]["path"]),"--authorization",str(ap),"--skill-source",str(Path(state["skill_post_path"]).parent),"--updater-receipt",state["update_receipt_path"],"--mode","e1","--model",c["actor"]["requested_model"],"--task-id",task,"--k","1","--prefix-ks","1","--max-turns",str(c["actor"]["max_turns"]),"--max-output-tokens",str(c["actor"]["max_output_tokens"]),"--concurrency","1","--provider-budget-ledger",str(ledger),"--provider-total-call-limit",str(state["child_provider_total_limit"]),"--provider-per-unit-call-limit","11","--output",str(out)]
 if pre:q.append("--stop-before-provider-io")
 return q

def preflight(a:argparse.Namespace)->dict[str,Any]:
 c,_,cs,aus=validate(a.contract,a.authorization,False); req(not a.run_root.exists(),"preflight root exists"); a.run_root.mkdir(parents=True)
 py,env=runtime(c); states={x["arm"]:x for x in c["learned_states"]}; rr=[]
 for m in c["allowed_measurements"]:
  s=states[m["arm"]]; ur=a.run_root/m["arm"]/m["task_id"]; out=ur/"pre-provider-stop.json"; led=ur/"provider_budget.sqlite3"
  z=subprocess.run(command(c,a.authorization,s,m["task_id"],ur/"actor",led,out,py,True),cwd=ROOT,env=env,text=True,capture_output=True)
  req(z.returncode==0,f"actual actor-path preflight failed: {m['arm']}/{m['task_id']}")
  x=obj(out); req(x.get("status")=="STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO" and x.get("provider_claims")==0 and x.get("provider_calls")==0,"pre-provider boundary")
  snap=ProviderBudgetLedger(path=led,contract_sha256=cs,authorization_sha256=aus,total_limit=s["child_provider_total_limit"],per_unit_limit=11,allow_create=False).snapshot()
  req(snap.total_claimed==0,"preflight provider claim")
  rr.append({"arm":m["arm"],"task_id":m["task_id"],"classification":m["classification"],"status":x["status"],"provider_claims":0,"provider_calls":0,"receipt_path":str(out),"receipt_sha256":sha(out)})
 req(len(rr)==7,"preflight count")
 x={"schema_version":"1.0","artifact_type":"e2-r17-pair29-actual-actor-path-preflight","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"PASS_ACTUAL_ACTOR_AUTHORIZATION_PATH_PREFLIGHT_7_OF_7","contract_sha256":cs,"authorization_sha256":aus,"heldout_combinations":7,"unique_429_recovery":1,"never_started_measurements":6,"provider_claims":0,"provider_calls":0,"partial_effect_read":False,"units":rr}
 atom(a.output,x); return x

def lock(p:Path,cs:str,aus:str)->int:
 p.parent.mkdir(parents=True,exist_ok=True); fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 os.write(fd,(json.dumps({"pid":os.getpid(),"pgid":os.getpgrp(),"contract_sha256":cs,"authorization_sha256":aus,"exactly_once":True},sort_keys=True)+"\n").encode()); os.fsync(fd); return fd

def execute(a:argparse.Namespace)->dict[str,Any]:
 c,_,cs,aus=validate(a.contract,a.authorization,True); req(not a.run_root.exists(),"recovery run root exists"); a.run_root.mkdir(parents=True)
 fd=lock(a.run_root/".exclusive.lock",cs,aus); py,env=runtime(c); states={x["arm"]:x for x in c["learned_states"]}; ledgers={}
 start={"schema_version":"1.0","artifact_type":"e2-r17-pair29-recovery-start","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"PAIR29_RECOVERY_START_WRITTEN_BEFORE_PROVIDER_IO","pid":os.getpid(),"pgid":os.getpgrp(),"contract_sha256":cs,"authorization_sha256":aus,"new_updater_calls":0,"replayed_updater_calls":0,"heldout_evaluations":7,"unique_429_logical_unit_recoveries":1,"provider_claims_before_start":0,"provider_calls_before_start":0,"partial_effect_read":False,"exactly_once":True}
 atom(a.run_root/"run-start-receipt.json",start); man=a.run_root/"checkpoints/completed_measurements.jsonl"; done=[]
 try:
  for m in c["allowed_measurements"]:
   s=states[m["arm"]]
   if m["arm"] not in ledgers:
    lp=a.run_root/"states"/m["arm"]/ "provider_budget.sqlite3"
    ledgers[m["arm"]]=(lp,ProviderBudgetLedger(path=lp,contract_sha256=cs,authorization_sha256=aus,total_limit=s["child_provider_total_limit"],per_unit_limit=11,allow_create=True))
   lp,ledger=ledgers[m["arm"]]; before=ledger.snapshot().total_claimed; ur=a.run_root/"states"/m["arm"]/"evaluation"/m["task_id"]; out=ur/"evaluation_summary.json"
   z=subprocess.run(command(c,a.authorization,s,m["task_id"],ur,lp,out,py,False),cwd=ROOT,env=env,text=True,capture_output=True)
   after=ledger.snapshot().total_claimed
   if z.returncode!=0:
    failure={"schema_version":"1.0","artifact_type":"e2-r17-pair29-recovery-failure","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"STOP_AND_ADJUDICATE_PAIR29_RECOVERY","classification":"PROVIDER_CONTACT_NO_AUTOMATIC_RETRY" if after>before else "PRE_PROVIDER_LOCAL_IMPLEMENTATION_FAILURE","arm":m["arm"],"task_id":m["task_id"],"provider_claims_before":before,"provider_claims_after":after,"returncode":z.returncode,"automatic_retry":False,"partial_effect_read":False}
    atom(a.run_root/"failure.json",failure); raise RuntimeError(f"pair29 recovery stopped: {m['arm']}/{m['task_id']}")
   req(out.is_file(),"actor completed without summary"); x=obj(out)
   req(x.get("status")=="COMPLETED" and x.get("k")==1 and x.get("skill_pre_sha256")==s["skill_post_sha256"] and x.get("updater_receipt_sha256")==s["update_receipt_sha256"],"actor summary drift")
   req(len(x.get("tasks") or [])==1 and x["tasks"][0].get("task_id")==m["task_id"] and x["tasks"][0].get("scores_withheld_from_measurement_summary") is True,"measurement outcome sealing")
   ref=ur/"cases"/m["task_id"]/"rollout_0/r17_trajectory_ref.json"; req(ref.is_file(),"trajectory ref missing")
   row={"arm":m["arm"],"task_id":m["task_id"],"classification":m["classification"],"summary_path":str(out),"summary_sha256":sha(out),"trajectory_ref_path":str(ref),"trajectory_ref_sha256":sha(ref),"skill_post_sha256":s["skill_post_sha256"],"update_receipt_sha256":s["update_receipt_sha256"],"provider_claims_before":before,"provider_claims_after":after,"partial_effect_read":False}
   append(man,row); done.append(row)
  req(len(done)==7,"recovery completion count")
  tasks=c["heldout"]["task_ids"]; combined={}; by={(x["arm"],x["task_id"]):x for x in done}
  for arm in ARMS:
   s=states[arm]; parent={x["task_id"]:x for x in lines(Path(s["parent_completed_eval_manifest_path"]))}; outm=a.run_root/"combined"/arm/"completed_eval_tasks.jsonl"
   for tid in tasks:
    if tid in parent: append(outm,parent[tid])
    else:
     x=by[(arm,tid)]; append(outm,{"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"task_id":tid,"summary_path":x["summary_path"],"summary_sha256":x["summary_sha256"],"trajectory_ref_path":x["trajectory_ref_path"],"trajectory_ref_sha256":x["trajectory_ref_sha256"]})
   req(len(lines(outm))==18,"combined manifest count"); combined[arm]={"path":str(outm),"sha256":sha(outm)}
  pair={"schema_version":"1.0","artifact_type":"e2-r17-repair2-pair29-measurement-recovery-pair-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED","unit_id":"e1-msp-01/rep0","stream_id":"e1-msp-01","replicate":0,"source":"repair2_v3_pair29_recovered","contract_sha256":cs,"authorization_sha256":aus,"new_updater_calls":0,"replayed_updater_calls":0,"new_heldout_evaluations":7,"combined_heldout_evaluations":36,"partial_effect_read":False,"analyzer_run":False,"arms":combined}
  pp=a.run_root/"summary/e1-msp-01-rep0.json"; atom(pp,pair)
  valid={"unit_id":"e1-msp-01/rep0","stream_id":"e1-msp-01","replicate_id":0,"source":"repair2_v3_pair29_recovered","pair_summary_path":str(pp),"pair_summary_sha256":sha(pp),"arms":{}}
  for arm in ARMS:
   s=states[arm]; valid["arms"][arm]={"state_root":s["state_root"],"skill_sha256":s["skill_post_sha256"],"update_receipt_sha256":s["update_receipt_sha256"],"eval_manifest_path":combined[arm]["path"],"eval_manifest_sha256":combined[arm]["sha256"],"updater_calls":s["updater_calls"],"attempt0_success":s["attempt0_success"],"correction_required":s["correction_required"],"measurement_recovery_contract_sha256":cs,"measurement_recovery_authorization_sha256":aus}
  vp=a.run_root/"summary/recovered_valid_pair.json"; atom(vp,valid)
  final={"schema_version":"1.0","artifact_type":"e2-r17-repair2-pair29-measurement-recovery-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"PAIR29_MEASUREMENT_RECOVERY_PASS","contract_sha256":cs,"authorization_sha256":aus,"new_updater_calls":0,"replayed_updater_calls":0,"new_heldout_evaluations":7,"unique_429_logical_unit_recoveries":1,"completed_pairs_after_recovery":29,"learned_states_after_recovery":58,"heldout_units_after_recovery":1044,"partial_effect_read":False,"analyzer_run":False,"completed_measurement_manifest":str(man),"completed_measurement_manifest_sha256":sha(man),"pair_summary_path":str(pp),"pair_summary_sha256":sha(pp),"recovered_valid_pair_path":str(vp),"recovered_valid_pair_sha256":sha(vp),"next_state":"GLOBAL_LINEAGE_LEASE_AND_CONTINUATION_V2"}
  rp=a.run_root/"summary/pair29_recovery_summary.json"; atom(rp,final); final["run_summary_path"]=str(rp); final["run_summary_sha256"]=sha(rp); atom(a.output,final); return final
 finally: os.close(fd)

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("--contract",type=Path,required=True); p.add_argument("--authorization",type=Path,required=True); p.add_argument("--run-root",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--stage",choices=("actual-path-preflight","execute"),required=True); a=p.parse_args()
 x=preflight(a) if a.stage=="actual-path-preflight" else execute(a); print(json.dumps({k:x.get(k) for k in ("status","contract_sha256","authorization_sha256","provider_calls","partial_effect_read","new_heldout_evaluations","completed_pairs_after_recovery")},indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
