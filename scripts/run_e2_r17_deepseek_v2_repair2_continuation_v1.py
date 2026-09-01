#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_mindmemos_ark_adapter import PLAN_BASE_URL
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_repair2_manifest import validate_quarantine
from research_pipeline.e2_r17_repair2_v3_manifest import validate_valid_rows_v3
from research_pipeline.e2_r17_search_projection_runner import ProjectionName
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v3 import (
 ARMS,REPLICATES,EVAL_ORDER_SALT,UPDATE_ORDER_SALT,acquire_lock,append_jsonl,
 canonical_sha,ensure_update,load_stream_pools,ordered_arms,rows_by)
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_v31_provider_runtime_pilot import bind_mindmemos,evidence_units,validate_updater_runtime
from scripts.run_e2_r17_e1_b_transition_runtime_pilot import atomic_json,load_json,require,sha_file

STATUS="AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V1"
CONTRACT_STATUS="FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V1"
BOUNDARY_UNIT="e1-ioc-00/rep1"
ACTOR=ROOT/"scripts/run_e2_r17_actor_pool_repair2_continuation_v1.py"

def utc()->str: return datetime.now(timezone.utc).isoformat(timespec="seconds")

def atomic_jsonl(path:Path, rows:list[dict[str,Any]])->None:
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_name(path.name+".tmp")
 with tmp.open("w",encoding="utf-8") as h:
  for row in rows: h.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
  h.flush(); os.fsync(h.fileno())
 os.replace(tmp,path)

def validate_contract_auth(cp:Path,ap:Path)->tuple[dict[str,Any],dict[str,Any]]:
 c,a=load_json(cp),load_json(ap)
 require(c.get("status")==CONTRACT_STATUS,"continuation contract not frozen")
 require(a.get("status")==STATUS,"continuation authorization invalid")
 require(a.get("contract_sha256")==sha_file(cp),"authorization/contract mismatch")
 au=a.get("authority") or {}; sc=a.get("execution_scope") or {}
 require(au.get("scientific_experiment") is True and au.get("repair2_continuation_v1") is True,"continuation authority absent")
 require(au.get("analyzer") is False and au.get("public_benchmark") is False,"analyzer/public benchmark forbidden")
 require(all(au.get(k) is False for k in ("gpt_scientific_execution","kimi_scientific_execution","qwen_scientific_execution")),"second backbone forbidden")
 require(sc.get("continuation_version")=="repair2_continuation_v1","continuation version drift")
 require(sc.get("allowed_modes")==["e1"] and sc.get("allowed_task_ids")==c["heldout"]["task_ids"],"actor scope drift")
 require(int(sc.get("exact_k"))==1 and sc.get("allow_noninitial_skill") is True,"K/learned-skill scope drift")
 require(sc.get("completed_unit_replay") is False and sc.get("partial_effect_read") is False,"replay/outcome boundary drift")
 require((int(sc["remaining_pairs"]),int(sc["remaining_new_learned_states"]),int(sc["remaining_heldout_units"]))==(31,60,1092),"remaining cardinality drift")
 for k in ("scientific_design_changed","prompt_changed","model_changed","task_order_changed","correction_budget_changed","analysis_changed","inherited_provider_replay","partial_effect_read"):
  require(c.get(k) is False,f"{k} must remain false")
 require((int(c["budget"]["max_provider_calls_per_state"]),int(c["budget"]["max_provider_calls_per_unit"]))==(191,11),"provider budget drift")
 require(int(c["updater"]["max_parse_attempts"])==2,"correction policy drift")
 return c,a

def validate_evidence(c:dict[str,Any])->tuple[dict[str,Any],dict[str,Any]]:
 ev=c["continuation_evidence"]
 for label,item in ev.items():
  p=ROOT/item["path"]; require(p.is_file() and sha_file(p)==item["sha256"],f"evidence drift: {label}")
 ia,im,rs=(load_json(ROOT/ev[x]["path"]) for x in ("interruption_audit","inheritance_manifest","remaining_set"))
 require(ia.get("status")=="PASS_CONTINUATION_BOUNDARY_PROVEN","clean boundary not proven")
 require(all(ia["boundary_assertions"].get(k) is True for k in ("NO_PARTIAL_PROVIDER_CLAIM","NO_PARTIAL_LEARNED_STATE","NO_PARTIAL_HELDOUT_UNIT","NO_AMBIGUOUS_COMPLETION")),"boundary assertion drift")
 require(ia.get("partial_effect_read") is False and ia.get("analyzer_run") is False,"audit opened outcome")
 require(im.get("status")=="PASS_IMMUTABLE_INHERITANCE_17_PAIRS_PLUS_CLEAN_PARTIAL_PAIR","inheritance not passing")
 require(im.get("replay_provider") is False and im.get("recompute_provider") is False and im.get("mutation")=="forbidden","inheritance policy drift")
 require(im.get("partial_effect_read") is False and im.get("scientific_scores_read") is False,"inheritance opened outcome")
 require((int(im["completed_pair_count"]),int(im["total_immutable_learned_states"]),int(im["total_immutable_heldout_units"]))==(17,36,636),"inheritance cardinality drift")
 require(rs.get("status")=="PASS_REMAINING_SET_EXACT_PARTITION","remaining proof not passing")
 require(rs.get("intersection")==[] and rs.get("union_equals_frozen_design") is True and rs.get("first_continuation_unit")==BOUNDARY_UNIT,"set proof drift")
 require((int(rs["remaining_pairs"]),int(rs["remaining_new_learned_states"]),int(rs["remaining_heldout_units"]))==(31,60,1092),"remaining counts drift")
 return im,rs

def verify_eval(row:dict[str,Any],skill_sha:str,receipt_sha:str)->None:
 sp,rp=Path(row["summary_path"]),Path(row["trajectory_ref_path"])
 require(sp.is_file() and sha_file(sp)==row["summary_sha256"],"eval summary SHA drift")
 summary=load_json(sp)
 require(summary.get("status")=="COMPLETED" and int(summary.get("k"))==1,"eval status/K drift")
 require(summary.get("skill_pre_sha256")==skill_sha and summary.get("updater_receipt_sha256")==receipt_sha,"eval learned-state binding drift")
 require([str(x["task_id"]) for x in summary.get("tasks") or []]==[row["task_id"]],"eval task drift")
 require(rp.is_file() and sha_file(rp)==row["trajectory_ref_sha256"],"trajectory-ref SHA drift")
 ref=load_json(rp); trajectory=Path(ref["trajectory_path"])
 require(trajectory.is_file() and sha_file(trajectory)==ref["trajectory_sha256"],"trajectory SHA drift")
 # Deliberately do not inspect score fields.

def ensure_eval(*,contract:dict[str,Any],auth_path:Path,identity_path:Path,actor_python:Path,
 actor_env:dict[str,str],stream_id:str,arm:str,task_id:str,state_root:Path,
 update:dict[str,Any],ledger_path:Path,total_limit:int)->dict[str,Any]:
 manifest=state_root/"checkpoints/completed_eval_tasks.jsonl"; existing=rows_by(manifest,"task_id")
 if task_id in existing:
  verify_eval(existing[task_id],update["skill_post_sha256"],update["update_receipt_sha256"]); return existing[task_id]
 eval_root=state_root/"evaluation"/task_id; summary_path=eval_root/"evaluation_summary.json"
 if eval_root.exists() and any(eval_root.rglob("*")): raise RuntimeError(f"partial ambiguous eval: {stream_id}/{arm}/{task_id}; no auto-rerun")
 cmd=[str(actor_python),str(ACTOR),"--env-file",contract["env_file"],"--suite-root",contract["suite"]["root"],
  "--mindmemos-root",contract["mindmemos"]["root"],"--run-root",str(eval_root),"--identity",str(identity_path),
  "--authorization",str(auth_path),"--skill-source",str(Path(update["skill_post_path"]).parent),
  "--updater-receipt",update["update_receipt_path"],"--mode","e1","--model",contract["actor"]["requested_model"],
  "--task-id",task_id,"--k","1","--prefix-ks","1","--max-turns",str(contract["actor"]["max_turns"]),
  "--max-output-tokens",str(contract["actor"]["max_output_tokens"]),"--concurrency","1",
  "--provider-budget-ledger",str(ledger_path),"--provider-total-call-limit",str(total_limit),
  "--provider-per-unit-call-limit",str(contract["budget"]["max_provider_calls_per_unit"]),"--output",str(summary_path)]
 result=subprocess.run(cmd,cwd=ROOT,env=actor_env,capture_output=True,text=True)
 if result.returncode:
  atomic_json(state_root/"checkpoints"/f"eval_failure_{task_id}.json",{"status":"TECHNICAL_FAILURE","stream_id":stream_id,
   "arm":arm,"task_id":task_id,"returncode":result.returncode,"stdout_tail":result.stdout[-3000:],
   "stderr_tail":result.stderr[-3000:],"provider_relaunch_authorized":False})
  raise RuntimeError(f"heldout evaluation technical failure: {stream_id}/{arm}/{task_id}")
 require(summary_path.is_file(),"actor returned without eval summary")
 ref=eval_root/"cases"/task_id/"rollout_0/r17_trajectory_ref.json"; require(ref.is_file(),"actor returned without trajectory ref")
 row={"task_id":task_id,"summary_path":str(summary_path),"summary_sha256":sha_file(summary_path),
  "trajectory_ref_path":str(ref),"trajectory_ref_sha256":sha_file(ref),"completed_at_utc":utc()}
 verify_eval(row,update["skill_post_sha256"],update["update_receipt_sha256"]); append_jsonl(manifest,row); return row

def normalize_inherited(row:dict[str,Any])->dict[str,Any]:
 pair=Path(row["pair_summary_path"]); require(pair.is_file() and sha_file(pair)==row["pair_summary_sha256"],f"pair drift: {row['unit_id']}")
 arms={}
 for arm in ARMS:
  x=row["arms"][arm]; receipt,skill,manifest=Path(x["update_receipt_path"]),Path(x["skill_path"]),Path(x["eval_manifest_path"])
  require(receipt.is_file() and sha_file(receipt)==x["update_receipt_sha256"],f"receipt drift: {row['unit_id']}/{arm}")
  require(skill.is_file() and sha_file(skill)==x["skill_sha256"],f"skill drift: {row['unit_id']}/{arm}")
  require(manifest.is_file() and sha_file(manifest)==x["eval_manifest_sha256"],f"manifest drift: {row['unit_id']}/{arm}")
  arms[arm]={"state_root":x["state_root"],"skill_sha256":x["skill_sha256"],"update_receipt_path":x["update_receipt_path"],
   "update_receipt_sha256":x["update_receipt_sha256"],"eval_manifest_path":x["eval_manifest_path"],
   "eval_manifest_sha256":x["eval_manifest_sha256"],"updater_calls":int(x["updater_calls"]),
   "attempt0_success":bool(x.get("attempt0_success")),"correction_required":bool(x.get("correction_required"))}
 return {"unit_id":row["unit_id"],"stream_id":row["stream_id"],"replicate_id":int(row["replicate_id"]),
  "source":row["source"],"execution_segment":"v3_pre_exit_inherited","pair_summary_path":row["pair_summary_path"],
  "pair_summary_sha256":row["pair_summary_sha256"],"arms":arms}

def boundary_update(boundary:dict[str,Any],arm:str)->dict[str,Any]:
 x=boundary["arms"][arm]; receipt,skill,checkpoint=Path(x["update_receipt_path"]),Path(x["skill_path"]),Path(x["update_checkpoint_path"])
 require(receipt.is_file() and sha_file(receipt)==x["update_receipt_sha256"],f"boundary receipt drift: {arm}")
 require(skill.is_file() and sha_file(skill)==x["skill_sha256"],f"boundary skill drift: {arm}")
 require(checkpoint.is_file() and sha_file(checkpoint)==x["update_checkpoint_sha256"],f"boundary checkpoint drift: {arm}")
 return {"status":"COMPLETED","stream_id":"e1-ioc-00","execution_stream_id":"e1-ioc-00::rep1","replicate":1,"arm":arm,
  "update_receipt_path":x["update_receipt_path"],"update_receipt_sha256":x["update_receipt_sha256"],
  "skill_post_path":x["skill_path"],"skill_post_sha256":x["skill_sha256"],"provider_calls":int(x["updater_calls"]),
  "attempt0_success":bool(x.get("attempt0_success")),"correction_required":bool(x.get("correction_required")),
  "correction_success":bool(x.get("correction_required")),"correction_failure":False}

async def main_async(args:argparse.Namespace)->dict[str,Any]:
 c,a=validate_contract_auth(args.contract,args.authorization); csha,asha=sha_file(args.contract),sha_file(args.authorization)
 inherit,remaining=validate_evidence(c)
 updater_python,_=validate_updater_runtime({"runtime":c["updater_runtime"],"mindmemos":c["mindmemos"]})
 require(Path(sys.executable)==updater_python,"runner must use dedicated updater runtime")
 actor_python,actor_env=validate_actor_runtime({"runtime":c["actor_runtime"]}); actor_env["LITELLM_LOCAL_MODEL_COST_MAP"]="True"
 for label,item in c["bound_code"].items():
  p=ROOT/item["path"]; require(p.is_file() and sha_file(p)==item["sha256"],f"bound code drift: {label}")
 suite=Path(c["suite"]["root"]); split_path=suite/"r17_split_manifest.json"
 require(sha_file(suite/"suite_manifest.json")==c["suite"]["suite_manifest_sha256"] and sha_file(split_path)==c["suite"]["split_manifest_sha256"],"suite/split drift")
 split=load_json(split_path); require(list(split["e1_update_streams"])==c["streams"],"stream order drift")
 require([str(x) for x in split["e1_common_heldout_probe"]]==c["heldout"]["task_ids"],"heldout order drift")
 frozen=[f"{stream}/rep{rep}" for stream in c["streams"] for rep in REPLICATES]
 require(remaining["frozen_design_order"]==frozen,"frozen order drift")
 require(remaining["completed_set"]==[r["unit_id"] for r in inherit["completed_pairs"]],"completed set drift")
 require(remaining["remaining_set"]==[r["unit_id"] for r in remaining["per_unit"]],"remaining rows drift")
 require(set(remaining["completed_set"]).isdisjoint(remaining["remaining_set"]),"completed/remaining overlap")
 require(set(remaining["completed_set"])|set(remaining["remaining_set"])==set(frozen),"design partition incomplete")
 support_path=ROOT/c["e1_a_support"]["path"]; require(support_path.is_file() and sha_file(support_path)==c["e1_a_support"]["sha256"],"support drift")
 support=load_json(support_path); require(support.get("status")=="PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT","support not passing")
 qi=c["technical_quarantine"]; quarantine=validate_quarantine(ROOT/qi["path"],qi["sha256"])
 mind=Path(c["mindmemos"]["root"]); head=subprocess.check_output(["git","-C",str(mind),"rev-parse","HEAD"],text=True).strip()
 require(head==c["mindmemos"]["commit"],"MindMemOS commit drift")
 require(not subprocess.check_output(["git","-C",str(mind),"status","--short"],text=True).strip(),"MindMemOS dirty")
 bind_mindmemos(mind)
 identity_path=ROOT/c["model_identity"]["path"]; require(identity_path.is_file() and sha_file(identity_path)==c["model_identity"]["sha256"],"identity drift")
 identity=load_json(identity_path); require(identity.get("status")=="PASS_CURRENT_REVIEW_TRANCHE","identity not qualified")
 model=identity["requested_and_resolved"][c["updater"]["requested_model"]]; requested,resolved=str(model["requested"]),str(model["resolved"])
 require(resolved==c["updater"]["resolved_model"]==c["actor"]["resolved_model"],"resolved model drift")
 load_env_file(Path(c["env_file"])); raw=ArkSettings.from_env(required=True); require(raw.base_url.rstrip("/")==PLAN_BASE_URL,"non-Ark route")
 settings=ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=300,max_retries=0)
 initial=Path(c["initial_skill"]["path"]); require(initial.is_file() and sha_file(initial)==c["initial_skill"]["sha256"],"initial skill drift")
 initial_text,initial_sha=initial.read_text(encoding="utf-8"),sha_file(initial)
 root=Path(c["run_root"]); lock=root/".exclusive.lock"; lockfd=acquire_lock(lock,csha,asha); success=False
 units_path=root/"checkpoints/completed_replicates.jsonl"; valid_path=Path(c["valid_replicate_manifest"]["path"])
 completed,valid=rows_by(units_path,"unit_id"),rows_by(valid_path,"unit_id")
 require(not completed and not valid,"new child manifests must start empty")
 try:
  for source in inherit["completed_pairs"]:
   vr=normalize_inherited(source); append_jsonl(valid_path,vr); valid[vr["unit_id"]]=vr
   cr={"unit_id":vr["unit_id"],"stream_id":vr["stream_id"],"replicate":vr["replicate_id"],
    "summary_path":vr["pair_summary_path"],"summary_sha256":vr["pair_summary_sha256"],"source":vr["source"],
    "execution_segment":"v3_pre_exit_inherited","provider_replay":False,"completed_at_utc":utc()}
   append_jsonl(units_path,cr); completed[cr["unit_id"]]=cr
  require(set(completed)==set(remaining["completed_set"]),"runtime inherited set drift")
  validate_valid_rows_v3(list(valid.values()),streams=c["streams"],quarantine=quarantine,require_complete=False)

  boundary=inherit["partial_boundary"]; require(boundary.get("unit_id")==BOUNDARY_UNIT,"boundary unit drift")
  bstream,brep="e1-ioc-00",1; updates={arm:boundary_update(boundary,arm) for arm in ARMS}
  broot=root/"boundary/states"/bstream/"replicate_1"
  for task in c["heldout"]["task_ids"]:
   for arm in ordered_arms(bstream,brep,EVAL_ORDER_SALT,task):
    x=boundary["arms"][arm]; old={str(r["task_id"]) for r in x["heldout_tasks"]}
    if task in old: continue
    state=broot/arm; residual=191-int(x["parent_claim_count"])
    require(residual==int(a["execution_scope"]["boundary_learned_states_by_arm"][arm]["child_total_limit"]),f"boundary residual drift: {arm}")
    ensure_eval(contract=c,auth_path=args.authorization,identity_path=identity_path,actor_python=actor_python,actor_env=actor_env,
     stream_id=f"{bstream}::rep1",arm=arm,task_id=task,state_root=state,update=updates[arm],
     ledger_path=state/"checkpoints/provider_budget.sqlite3",total_limit=residual)
  states=[]; varms={}
  for arm in ARMS:
   x=boundary["arms"][arm]; old=rows_by(Path(x["eval_manifest_path"]),"task_id")
   state=broot/arm; new=rows_by(state/"checkpoints/completed_eval_tasks.jsonl","task_id")
   require(set(old).isdisjoint(new),f"boundary replay: {arm}")
   combined={**old,**new}; require(set(combined)==set(c["heldout"]["task_ids"]),f"boundary incomplete: {arm}")
   ordered=[combined[t] for t in c["heldout"]["task_ids"]]
   for row in ordered: verify_eval(row,updates[arm]["skill_post_sha256"],updates[arm]["update_receipt_sha256"])
   cm=state/"checkpoints/combined_eval_tasks.jsonl"; atomic_jsonl(cm,ordered)
   residual=191-int(x["parent_claim_count"])
   led=ProviderBudgetLedger(path=state/"checkpoints/provider_budget.sqlite3",contract_sha256=csha,authorization_sha256=asha,total_limit=residual,per_unit_limit=11,allow_create=False)
   snap=led.snapshot().to_dict()
   states.append({"arm":arm,"update_receipt_sha256":updates[arm]["update_receipt_sha256"],"skill_post_sha256":updates[arm]["skill_post_sha256"],
    "completed_heldout_tasks":18,"eval_manifest_path":str(cm),"eval_manifest_sha256":sha_file(cm),
    "provider_budget":{"v3_parent_claims":int(x["parent_claim_count"]),"continuation_child":snap,
    "combined_claims":int(x["parent_claim_count"])+int(snap["total_claimed"]),"original_total_limit":191}})
   varms[arm]={"state_root":x["state_root"],"skill_sha256":x["skill_sha256"],"update_receipt_path":x["update_receipt_path"],
    "update_receipt_sha256":x["update_receipt_sha256"],"eval_manifest_path":str(cm),"eval_manifest_sha256":sha_file(cm),
    "updater_calls":int(x["updater_calls"]),"attempt0_success":bool(x.get("attempt0_success")),
    "correction_required":bool(x.get("correction_required")),"continuation_child_ledger_path":str(state/"checkpoints/provider_budget.sqlite3"),
    "v3_parent_claims":int(x["parent_claim_count"])}
  evidence_old=Path(inherit["v3_run_root"])/"states"/bstream/"evidence_windows.json"; require(evidence_old.is_file(),"boundary evidence missing")
  bsummary={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-replicated-paired-unit","created_at_utc":utc(),
   "status":"COMPLETED","unit_id":BOUNDARY_UNIT,"stream_id":bstream,"execution_stream_id":f"{bstream}::rep1","replicate":1,
   "evidence_windows_sha256":sha_file(evidence_old),"update_order":ordered_arms(bstream,1,UPDATE_ORDER_SALT),
   "heldout_task_ids":c["heldout"]["task_ids"],"states":states,"mrw_executed":True,"primary_control":"win_c",
   "provider_replay":False,"partial_effect_read":False,"paper_promotion_authority":False}
  bsp=root/"summary/replicates/e1-ioc-00-rep1.json"; atomic_json(bsp,bsummary)
  bvalid={"unit_id":BOUNDARY_UNIT,"stream_id":bstream,"replicate_id":1,"source":"repair2_v3_fresh",
   "execution_segment":"continuation_v1_boundary_completion","pair_summary_path":str(bsp),"pair_summary_sha256":sha_file(bsp),"arms":varms}
  append_jsonl(valid_path,bvalid); valid[BOUNDARY_UNIT]=bvalid
  bc={"unit_id":BOUNDARY_UNIT,"stream_id":bstream,"replicate":1,"summary_path":str(bsp),"summary_sha256":sha_file(bsp),
   "source":"repair2_v3_fresh","execution_segment":"continuation_v1_boundary_completion","provider_replay":False,"completed_at_utc":utc()}
  append_jsonl(units_path,bc); completed[BOUNDARY_UNIT]=bc

  rset=list(remaining["remaining_set"]); require(rset[0]==BOUNDARY_UNIT,"first continuation unit changed")
  for stream in c["streams"]:
   pools=load_stream_pools(c,stream,split,support)
   wins,mrws,receipts=evidence_units(pools,final_block_cap_tokens=int(c["renderer"]["final_block_cap_tokens"]),
    transcript_max_chars=int(c["updater"]["transcript_max_chars"]))
   sroot=root/"states"/stream; ep=sroot/"evidence_windows.json"
   wsha,msha=canonical_sha([u.__dict__ for u in wins]),canonical_sha([u.__dict__ for u in mrws])
   epayload={"stream_id":stream,"win_c_evidence_bundle_sha256":wsha,"mrw_evidence_bundle_sha256":msha,
    "receipts":receipts,"mrw_provider_execution_authorized":True,"primary_control":"fresh_contemporaneous_win_c",
    "replicates_per_stream":4}
   inputs={"win_c":(wins,ProjectionName.WINNER_ONLY),"mrw":(mrws,ProjectionName.MIXED_REJECTED_WITNESS)}
   for rep in REPLICATES:
    uid=f"{stream}/rep{rep}"
    if uid not in rset or uid==BOUNDARY_UNIT: continue
    require(uid not in completed,f"completed replay attempted: {uid}")
    if not ep.exists(): atomic_json(ep,epayload)
    else:
     old=load_json(ep); require(old.get("win_c_evidence_bundle_sha256")==wsha and old.get("mrw_evidence_bundle_sha256")==msha,"evidence drift")
    rr=sroot/f"replicate_{rep}"; execid=f"{stream}::rep{rep}"; updates={}
    for arm in ordered_arms(stream,rep,UPDATE_ORDER_SALT):
     state=rr/arm; lp=state/"checkpoints/provider_budget.sqlite3"
     ledger=ProviderBudgetLedger(path=lp,contract_sha256=csha,authorization_sha256=asha,total_limit=191,per_unit_limit=11,allow_create=not lp.exists())
     units,projection=inputs[arm]
     updates[arm]=await ensure_update(contract=c,contract_sha=csha,auth_sha=asha,base_stream_id=stream,
      execution_stream_id=execid,replicate=rep,arm=arm,pools=pools,evidence_units_for_arm=units,
      projection=projection,initial_skill=initial_text,initial_sha=initial_sha,mind_head=head,
      requested=requested,resolved=resolved,settings=settings,state_root=state,ledger=ledger)
    for task in c["heldout"]["task_ids"]:
     for arm in ordered_arms(stream,rep,EVAL_ORDER_SALT,task):
      state=rr/arm
      ensure_eval(contract=c,auth_path=args.authorization,identity_path=identity_path,actor_python=actor_python,
       actor_env=actor_env,stream_id=execid,arm=arm,task_id=task,state_root=state,update=updates[arm],
       ledger_path=state/"checkpoints/provider_budget.sqlite3",total_limit=191)
    repstates=[]; arms={}
    for arm in ARMS:
     state=rr/arm; em=state/"checkpoints/completed_eval_tasks.jsonl"; erows=rows_by(em,"task_id")
     require(set(erows)==set(c["heldout"]["task_ids"]),f"heldout incomplete: {uid}/{arm}")
     for row in erows.values(): verify_eval(row,updates[arm]["skill_post_sha256"],updates[arm]["update_receipt_sha256"])
     led=ProviderBudgetLedger(path=state/"checkpoints/provider_budget.sqlite3",contract_sha256=csha,authorization_sha256=asha,total_limit=191,per_unit_limit=11,allow_create=False)
     repstates.append({"arm":arm,"update_receipt_sha256":updates[arm]["update_receipt_sha256"],
      "skill_post_sha256":updates[arm]["skill_post_sha256"],"completed_heldout_tasks":18,
      "eval_manifest_path":str(em),"eval_manifest_sha256":sha_file(em),"provider_budget":led.snapshot().to_dict()})
     arms[arm]={"state_root":str(state),"skill_sha256":updates[arm]["skill_post_sha256"],
      "update_receipt_path":updates[arm]["update_receipt_path"],"update_receipt_sha256":updates[arm]["update_receipt_sha256"],
      "eval_manifest_path":str(em),"eval_manifest_sha256":sha_file(em),"updater_calls":int(updates[arm]["provider_calls"]),
      "attempt0_success":bool(updates[arm].get("attempt0_success")),"correction_required":bool(updates[arm].get("correction_required"))}
    summary={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-replicated-paired-unit","created_at_utc":utc(),
     "status":"COMPLETED","unit_id":uid,"stream_id":stream,"execution_stream_id":execid,"replicate":rep,
     "pool_ids":[p.pool_id for p in pools],"evidence_windows_sha256":sha_file(ep),
     "update_order":ordered_arms(stream,rep,UPDATE_ORDER_SALT),"heldout_task_ids":c["heldout"]["task_ids"],
     "states":repstates,"mrw_executed":True,"primary_control":"win_c","provider_replay":False,
     "partial_effect_read":False,"paper_promotion_authority":False}
    sp=root/"summary/replicates"/f"{stream}-rep{rep}.json"; atomic_json(sp,summary)
    vr={"unit_id":uid,"stream_id":stream,"replicate_id":rep,"source":"repair2_v3_fresh",
     "execution_segment":"continuation_v1_new_pair","pair_summary_path":str(sp),"pair_summary_sha256":sha_file(sp),"arms":arms}
    append_jsonl(valid_path,vr); valid[uid]=vr
    cr={"unit_id":uid,"stream_id":stream,"replicate":rep,"summary_path":str(sp),"summary_sha256":sha_file(sp),
     "source":"repair2_v3_fresh","execution_segment":"continuation_v1_new_pair","provider_replay":False,"completed_at_utc":utc()}
    append_jsonl(units_path,cr); completed[uid]=cr

  require(set(completed)==set(frozen),"continuation did not complete 48 pairs")
  validate_valid_rows_v3(list(valid.values()),streams=c["streams"],quarantine=quarantine,require_complete=True)
  reliability={arm:{"attempt0_success_count":0,"correction_required_count":0,"correction_success_count":0,
   "correction_failure_count":0} for arm in ARMS}
  for row in valid.values():
   for arm in ARMS:
    if row["arms"][arm].get("correction_required"):
     reliability[arm]["correction_required_count"]+=1; reliability[arm]["correction_success_count"]+=1
    else: reliability[arm]["attempt0_success_count"]+=1
  final={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-repair2-continuation-v1-summary",
   "created_at_utc":utc(),"status":"COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION",
   "contract_sha256":csha,"authorization_sha256":asha,"original_v3_contract_sha256":c["v3_parent"]["contract_sha256"],
   "original_v3_authorization_sha256":c["v3_parent"]["authorization_sha256"],"paired_replicate_units":48,
   "inherited_complete_pairs":17,"continuation_boundary_pairs":1,"continuation_new_pairs":30,
   "learned_states":96,"heldout_tasks_per_state":18,"heldout_rollout_units":1728,
   "provider_claims_before_continuation":609,"completed_unit_replay":False,"partial_effect_read":False,
   "inference_performed":False,"paper_promotion_authority":False,
   "completed_replicate_manifest":str(units_path),"completed_replicate_manifest_sha256":sha_file(units_path),
   "valid_replicate_manifest":str(valid_path),"valid_replicate_manifest_sha256":sha_file(valid_path),
   "runtime_reliability":reliability,"repair1_quarantined_patch_apply_failures":{"win_c":0,"mrw":1}}
  atomic_json(root/"summary/deepseek_v2_repair2_continuation_v1_summary.json",final); success=True; return final
 finally:
  os.close(lockfd)
  if success: lock.unlink(missing_ok=True)

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("--contract",type=Path,required=True); p.add_argument("--authorization",type=Path,required=True)
 out=asyncio.run(main_async(p.parse_args())); print(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True))
 return 0 if out["status"]=="COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION" else 2

if __name__=="__main__": raise SystemExit(main())
