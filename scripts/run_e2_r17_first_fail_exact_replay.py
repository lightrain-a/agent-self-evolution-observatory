#!/usr/bin/env python3
from __future__ import annotations

import argparse, asyncio, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_diagnostic_witness import build_four_arm_evidence, make_diagnostic_stream
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter, PLAN_BASE_URL
from research_pipeline.e2_r17_mindmemos_updater import run_projection_update
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import (
    append_jsonl, atomic_json, bind_mindmemos, load_json, require, rows_by, sha_file,
    validate_actor_runtime, validate_updater_runtime, verify_eval,
)

ARMS=("win_c","first_fail")
REPS=(1,2)
CONTRACT_STATUS="FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY"
AUTH_STATUS="AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY"
UPDATE_SALT="E2-R17-SINGLE-CASE-FIRST-FAIL-EXACT-REPLAY-UPDATE-ORDER-v1"
EVAL_SALT="E2-R17-SINGLE-CASE-FIRST-FAIL-EXACT-REPLAY-EVAL-ORDER-v1"


def ordered(rep:int,salt:str,task:str="")->list[str]:
    return sorted(ARMS,key=lambda arm:hashlib.sha256(f"{salt}|e1-tsr-00|rep{rep}|{task}|{arm}".encode()).hexdigest())


def validate(cpath:Path,apath:Path)->tuple[dict[str,Any],dict[str,Any]]:
    c=load_json(cpath); a=load_json(apath); csha=sha_file(cpath)
    require(c.get("status")==CONTRACT_STATUS,"exact-replay contract drift")
    require(a.get("status")==AUTH_STATUS and a.get("contract_sha256")==csha,"exact-replay authorization drift")
    au=a.get("authority") or {}; require(au.get("scientific_experiment") is True and au.get("exact_replay") is True and au.get("updater") is True and au.get("heldout_evaluation") is True,"exact-replay execution authority absent")
    for k in ("analyzer","paper_promotion","submission","second_backbone","public_benchmark","e3_confirmation"): require(au.get(k) is False,f"exact-replay authority overbroad: {k}")
    scope=a.get("execution_scope") or {}; require(scope.get("phase")=="single_case_first_fail_exact_replay" and scope.get("case_stream")=="e1-tsr-00","exact-replay scope drift")
    require(scope.get("arms")==list(ARMS) and scope.get("replicates")==[1,2],"exact-replay arm/replicate drift")
    require(scope.get("allowed_task_ids")==c["heldout_task_ids"] and int(scope.get("exact_k"))==1 and scope.get("allow_noninitial_skill") is True,"exact-replay heldout scope drift")
    for label,item in c["bound_code"].items():
        p=ROOT/item["path"]; require(p.is_file() and sha_file(p)==item["sha256"],f"exact-replay bound code drift: {label}")
    for key in ("design","selector_freeze"):
        item=c[key]; p=ROOT/item["path"]; require(p.is_file() and sha_file(p)==item["sha256"],f"exact-replay {key} drift")
    return c,a


def acquire_lease(p:Path,csha:str,asha:str)->None:
    p.parent.mkdir(parents=True,exist_ok=True)
    d={"schema_version":"1.0","artifact_type":"e2-r17-first-fail-exact-replay-lineage-lease","status":"RUNNING_FIRST_FAIL_EXACT_REPLAY","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"pid":os.getpid(),"pgid":os.getpgrp(),"contract_sha256":csha,"authorization_sha256":asha,"exactly_once":True,"partial_effect_read":False}
    fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try: os.write(fd,(json.dumps(d,sort_keys=True)+"\n").encode()); os.fsync(fd)
    finally: os.close(fd)

def check_lease(p:Path,csha:str,asha:str)->None:
    d=load_json(p); require(d.get("status")=="RUNNING_FIRST_FAIL_EXACT_REPLAY" and int(d.get("pid"))==os.getpid(),"exact-replay lease owner drift"); require(d.get("contract_sha256")==csha and d.get("authorization_sha256")==asha,"exact-replay lease binding drift")
def seal(p:Path,status:str)->None:
    d=load_json(p); d["status"]=status; d["sealed_at_utc"]=datetime.now(timezone.utc).isoformat(timespec="seconds"); atomic_json(p,d)


def load_pools(c:dict[str,Any])->list[Any]:
    out=[]
    for row in c["pool_bindings"]:
        p=Path(row["path"]); require(p.is_file() and sha_file(p)==row["sha256"],f"pool drift {row['task_id']}"); pool=load_frozen_pool(p); require(pool.task_id==row["task_id"] and pool.pool_id==row["pool_id"],"pool identity drift"); out.append(pool)
    return out


def verify_exact_evidence(c:dict[str,Any],units:dict[str,list[Any]])->None:
    for arm in ARMS:
        expected=c["exact_evidence"][arm]["evidence_sha256s"]
        actual=[str(u.evidence_sha256) for u in units[arm]]
        require(actual==expected,f"exact-replay rendered evidence mismatch for {arm}")


def verify_update(cp:Path,csha:str,asha:str)->dict[str,Any]:
    r=load_json(cp); receipt=Path(r["update_receipt_path"]); skill=Path(r["skill_post_path"])
    require(receipt.is_file() and sha_file(receipt)==r["update_receipt_sha256"],"update receipt drift"); require(skill.is_file() and sha_file(skill)==r["skill_post_sha256"],"skill drift")
    d=load_json(receipt); require(d.get("contract_sha256")==csha and d.get("authorization_sha256")==asha,"update authority drift"); require(d.get("causal_purity_mode")=="arm_blinded_selected_evidence" and d.get("arm_metadata_visible_in_transcript") is False,"causal purity drift")
    return r


async def ensure_update(*,c:dict[str,Any],csha:str,asha:str,rep:int,arm:str,pools:list[Any],units:list[Any],initial:str,initial_sha:str,mind_head:str,requested:str,resolved:str,settings:ArkSettings,state:Path)->dict[str,Any]:
    cp=state/"checkpoints/update_completed.json"
    if cp.exists(): return verify_update(cp,csha,asha)
    update_dir=state/"update"
    if update_dir.exists() and any(update_dir.rglob("*")): raise RuntimeError(f"partial exact-replay update exists rep{rep}/{arm}")
    ledger_path=state/"checkpoints/provider_budget.sqlite3"; ledger=ProviderBudgetLedger(path=ledger_path,contract_sha256=csha,authorization_sha256=asha,total_limit=int(c["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(c["budget"]["max_provider_calls_per_unit"]),allow_create=not ledger_path.exists())
    stream=make_diagnostic_stream(stream_id=f"e1-tsr-00::exact-replay::rep{rep}::{arm}",initial_skill_sha256=initial_sha,pools=pools,arm=arm,units=units)
    adapter=MindMemOSArkPlanChatAdapter(settings=settings,requested_model=requested,required_resolved_model=resolved,max_parse_attempts=int(c["updater"]["max_parse_attempts"]),record_dir=update_dir/"provider_calls",provider_budget_ledger=ledger,provider_budget_unit_id=f"e1-tsr-00/exact-replay/rep{rep}/{arm}/update")
    result=await run_projection_update(stream=stream,pools=pools,initial_skill_md=initial,run_dir=update_dir,llm_adapter=adapter,mindmemos_commit=mind_head,contract_sha256=csha,authorization_sha256=asha,transcript_max_chars=int(c["updater"]["transcript_max_chars"]),blinded_evidence_units=units)
    receipts=adapter.public_receipts(); require(result.provider_calls==len(receipts) and result.provider_calls in (10,11),"exact-replay updater 10/11-call invariant failed"); require(all(x.get("provider_status")=="completed" and x.get("hidden_provider_retry_used") is False for x in receipts),"exact-replay updater retry/status drift")
    if result.provider_calls==11: require(sum(bool(x.get("parse_error")) for x in receipts)==1 and receipts[-1].get("task")=="skill_patch_apply" and int(receipts[-1].get("attempt"))==1 and not receipts[-1].get("parse_error"),"exact-replay correction path drift")
    else: require(not any(x.get("parse_error") for x in receipts),"exact-replay nominal update parse error")
    row={"status":"COMPLETED","replicate":rep,"arm":arm,"update_receipt_path":result.update_receipt_path,"update_receipt_sha256":result.update_receipt_sha256,"skill_post_path":result.skill_post_path,"skill_post_sha256":result.skill_post_sha256,"provider_calls":result.provider_calls,"provider_tokens":result.provider_total_tokens,"attempt0_success":result.provider_calls==10,"correction_required":result.provider_calls==11}; atomic_json(cp,row); return verify_update(cp,csha,asha)


def ensure_eval(*,c:dict[str,Any],auth:Path,identity:Path,actor_python:Path,actor_env:dict[str,str],rep:int,arm:str,task:str,state:Path,update:dict[str,Any])->dict[str,Any]:
    manifest=state/"checkpoints/completed_eval_tasks.jsonl"; existing=rows_by(manifest,"task_id")
    if task in existing: verify_eval(existing[task],state,update["skill_post_sha256"],update["update_receipt_sha256"]); return existing[task]
    eroot=state/"evaluation"/task
    if eroot.exists() and any(eroot.rglob("*")): raise RuntimeError(f"partial exact-replay eval exists rep{rep}/{arm}/{task}")
    summary=eroot/"evaluation_summary.json"; ledger=state/"checkpoints/provider_budget.sqlite3"
    cmd=[str(actor_python),str(ROOT/"scripts/run_e2_r17_actor_pool_first_fail_exact_replay.py"),"--env-file",c["env_file"],"--suite-root",c["suite"]["root"],"--mindmemos-root",c["mindmemos"]["root"],"--run-root",str(eroot),"--identity",str(identity),"--authorization",str(auth.resolve()),"--skill-source",str(Path(update["skill_post_path"]).parent),"--updater-receipt",update["update_receipt_path"],"--mode","e1","--model",c["actor"]["requested_model"],"--task-id",task,"--k","1","--prefix-ks","1","--max-turns",str(c["actor"]["max_turns"]),"--max-output-tokens",str(c["actor"]["max_output_tokens"]),"--concurrency","1","--provider-budget-ledger",str(ledger),"--provider-total-call-limit",str(c["budget"]["max_provider_calls_per_state"]),"--provider-per-unit-call-limit",str(c["budget"]["max_provider_calls_per_unit"]),"--output",str(summary)]
    r=subprocess.run(cmd,cwd=ROOT,env=actor_env,capture_output=True,text=True)
    if r.returncode!=0: atomic_json(state/"checkpoints"/f"eval_failure_{task}.json",{"status":"TECHNICAL_FAILURE","replicate":rep,"arm":arm,"task_id":task,"returncode":r.returncode,"stdout_tail":r.stdout[-3000:],"stderr_tail":r.stderr[-3000:],"provider_relaunch_authorized":False}); raise RuntimeError(f"exact-replay eval failed rep{rep}/{arm}/{task}")
    ref=eroot/"cases"/task/"rollout_0/r17_trajectory_ref.json"; require(summary.is_file() and ref.is_file(),"exact-replay actor missing output"); row={"task_id":task,"summary_path":str(summary),"summary_sha256":sha_file(summary),"trajectory_ref_path":str(ref),"trajectory_ref_sha256":sha_file(ref),"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}; verify_eval(row,state,update["skill_post_sha256"],update["update_receipt_sha256"]); append_jsonl(manifest,row); return row


async def main_async(args:argparse.Namespace)->dict[str,Any]:
    c,_=validate(args.contract,args.authorization); csha=sha_file(args.contract); asha=sha_file(args.authorization); lease=Path(c["lineage_lease_path"]); acquire_lease(lease,csha,asha); success=False
    try:
        updater_python,_=validate_updater_runtime({"runtime":c["updater_runtime"],"mindmemos":c["mindmemos"]}); require(Path(sys.executable)==updater_python,"exact-replay runner must use updater runtime")
        actor_python,actor_env=validate_actor_runtime({"runtime":c["actor_runtime"]}); actor_env["LITELLM_LOCAL_MODEL_COST_MAP"]="True"
        suite=Path(c["suite"]["root"]); require(sha_file(suite/"suite_manifest.json")==c["suite"]["suite_manifest_sha256"] and sha_file(suite/"r17_split_manifest.json")==c["suite"]["split_manifest_sha256"],"exact-replay suite drift")
        pools=load_pools(c); freeze=load_json(ROOT/c["selector_freeze"]["path"])
        units,evidence_receipts=build_four_arm_evidence(pools,selector_freeze=freeze,final_block_cap_tokens=int(c["renderer"]["final_block_cap_tokens"]),transcript_max_chars=int(c["updater"]["transcript_max_chars"])); verify_exact_evidence(c,units)
        mind=Path(c["mindmemos"]["root"]); head=subprocess.check_output(["git","-C",str(mind),"rev-parse","HEAD"],text=True).strip(); require(head==c["mindmemos"]["commit"] and not subprocess.check_output(["git","-C",str(mind),"status","--short"],text=True).strip(),"exact-replay MindMemOS drift"); bind_mindmemos(mind)
        identity=ROOT/c["model_identity"]["path"]; require(sha_file(identity)==c["model_identity"]["sha256"],"exact-replay identity drift"); ident=load_json(identity); require(ident.get("status")=="PASS_CURRENT_REVIEW_TRANCHE","identity not passing"); m=ident["requested_and_resolved"][c["updater"]["requested_model"]]; requested=str(m["requested"]); resolved=str(m["resolved"]); require(resolved==c["updater"]["resolved_model"]==c["actor"]["resolved_model"],"model drift")
        load_env_file(Path(c["env_file"])); raw=ArkSettings.from_env(required=True); require(raw.base_url.rstrip("/")==PLAN_BASE_URL,"non-Ark route"); settings=ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=300.0,max_retries=0)
        initial_path=Path(c["initial_skill"]["path"]); require(initial_path.is_file() and sha_file(initial_path)==c["initial_skill"]["sha256"],"initial skill drift"); initial=initial_path.read_text(encoding="utf-8"); initial_sha=sha_file(initial_path)
        run=Path(c["run_root"]); require(not run.exists(),"exact-replay run root must be fresh"); run.mkdir(parents=True)
        atomic_json(run/"exact_evidence_receipt.json",{"schema_version":"1.0","artifact_type":"e2-r17-first-fail-exact-replay-evidence-receipt","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"contract_sha256":csha,"authorization_sha256":asha,"case_stream":"e1-tsr-00","source_parent_s1_packet_identity_pass":True,"evidence_receipts":evidence_receipts,"partial_effect_read":False})
        summary_rows=[]
        for rep in REPS:
            updates={}
            for arm in ordered(rep,UPDATE_SALT):
                check_lease(lease,csha,asha); state=run/f"states/e1-tsr-00/replicate_{rep}"/arm; updates[arm]=await ensure_update(c=c,csha=csha,asha=asha,rep=rep,arm=arm,pools=pools,units=units[arm],initial=initial,initial_sha=initial_sha,mind_head=head,requested=requested,resolved=resolved,settings=settings,state=state)
            for task in c["heldout_task_ids"]:
                for arm in ordered(rep,EVAL_SALT,task):
                    check_lease(lease,csha,asha); state=run/f"states/e1-tsr-00/replicate_{rep}"/arm; ensure_eval(c=c,auth=args.authorization,identity=identity,actor_python=actor_python,actor_env=actor_env,rep=rep,arm=arm,task=task,state=state,update=updates[arm])
            for arm in ARMS:
                state=run/f"states/e1-tsr-00/replicate_{rep}"/arm; em=state/"checkpoints/completed_eval_tasks.jsonl"; erows=rows_by(em,"task_id"); require(list(erows)==c["heldout_task_ids"],f"completion drift rep{rep}/{arm}"); ledger=ProviderBudgetLedger(path=state/"checkpoints/provider_budget.sqlite3",contract_sha256=csha,authorization_sha256=asha,total_limit=int(c["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(c["budget"]["max_provider_calls_per_unit"]),allow_create=False); summary_rows.append({"replicate":rep,"arm":arm,"state_root":str(state),"skill_post_sha256":updates[arm]["skill_post_sha256"],"update_receipt_path":updates[arm]["update_receipt_path"],"update_receipt_sha256":updates[arm]["update_receipt_sha256"],"updater_calls":updates[arm]["provider_calls"],"eval_manifest_path":str(em),"eval_manifest_sha256":sha_file(em),"completed_heldout_tasks":len(erows),"provider_budget":ledger.snapshot().to_dict()})
        summary={"schema_version":"1.0","artifact_type":"e2-r17-single-case-first-fail-exact-replay-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED_PENDING_SEPARATE_EXACT_REPLAY_ANALYSIS","contract_sha256":csha,"authorization_sha256":asha,"case_stream":"e1-tsr-00","replicates":[1,2],"arms":list(ARMS),"rows":summary_rows,"new_learned_states":4,"heldout_tasks_per_state":18,"heldout_rollout_units":72,"inference_performed":False,"partial_effect_read":False,"analyzer_run":False,"paper_promotion_authority":False}; atomic_json(run/"summary/exact_replay_summary.json",summary); success=True; return summary
    finally:
        if lease.exists(): seal(lease,"COMPLETED_FIRST_FAIL_EXACT_REPLAY" if success else "FAIL_CLOSED_FIRST_FAIL_EXACT_REPLAY")


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--contract",type=Path,required=True); p.add_argument("--authorization",type=Path,required=True); a=p.parse_args(); payload=asyncio.run(main_async(a)); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
