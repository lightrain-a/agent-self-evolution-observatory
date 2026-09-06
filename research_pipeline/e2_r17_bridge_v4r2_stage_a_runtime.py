from __future__ import annotations

import hashlib, json, os, sqlite3, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import ActorRolloutConfig, atomic_json, file_sha256, freeze_nested_pools, run_actor_rollout
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM, PLAN_BASE_URL
from research_pipeline.e2_r17_bridge_v4r2_execution_plan import SCREEN, search_units, stage_stream_ids, update_tasks
from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import (
    CONTROL_PLANE_REVISION,
    PRODUCTION_PUBLIC_KEY_SHA256,
    sha256_file as capability_sha256_file,
    verify_document,
)
from research_pipeline.e2_r17_bridge_v4r2_stage_a_support import evaluate_screen_support
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef
from scripts.run_e2_r17_actor_pool import load_mindmemos
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime

CONTRACT_STATUS="FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT"
AUTH_STATUS="AUTHORIZED_E2_R17_BRIDGE_V4R2_STAGE_A_STRUCTURAL_REQUIRES_SIGNED_CAPABILITY"
IDENTITY_STATUS="PASS_BRIDGE_V4R2_STAGE_A_MODEL_IDENTITY"
RUNNING="RUNNING_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH"
FAIL="FAIL_CLOSED_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH"


def sha(path: Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path: Path)->dict[str,Any]:return json.loads(path.read_text(encoding="utf-8"))
def req(v:bool,m:str)->None:
    if not v: raise RuntimeError(m)
def append(path:Path,row:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
def rows(path:Path)->list[dict[str,Any]]:return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []


def validate(contract_path:Path,auth_path:Path,capability_path:Path,root:Path)->tuple[dict[str,Any],dict[str,Any],dict[str,Any],str,str,str,dict[str,Path]]:
    c,a=load(contract_path),load(auth_path); cs,ahs=sha(contract_path),sha(auth_path)
    req(c.get("status")==CONTRACT_STATUS,"Stage-A contract drift");req(a.get("status")==AUTH_STATUS,"Stage-A auth drift");req(a.get("contract_sha256")==cs,"Stage-A auth/contract drift");req(a.get("control_plane_revision")==CONTROL_PLANE_REVISION,"Stage-A auth control-plane revision drift");req(a.get("authority_requires_external_signed_capability") is True,"Stage-A structural authorization does not require external signed capability");req(a.get("production_public_key_sha256")==PRODUCTION_PUBLIC_KEY_SHA256,"Stage-A auth production trust-root drift")
    au=a.get("authority") or {}; expected_authority={"scientific_experiment":True,"provider_io":True,"search_pool_acquisition":True,"support_inspection":True,"free_updater":False,"deterministic_state_materialization":False,"actor_evaluation":False,"screen_outcome_opening":False,"validation_opening":False,"analysis":False,"paper_promotion":False};req(au==expected_authority,"Stage-A authorization authority surface drift")
    for label,item in c["bound_code"].items():
        p=root/item["path"];req(p.is_file() and sha(p)==item["sha256"],f"bound code drift:{label}")
    for label,item in (("protocol",c["protocol"]),("m3r4",c["m3r4_eligibility"]),("identity",c["model_identity"])):
        p=root/item["path"];req(p.is_file() and sha(p)==item["sha256"],f"{label} drift")
    review=root/c["protocol"]["review_path"];req(review.is_file() and sha(review)==c["protocol"]["review_sha256"],"protocol review drift")
    ident=load(root/c["model_identity"]["path"]);req(ident.get("status")==IDENTITY_STATUS,"identity status drift"); mr=ident["requested_and_resolved"][c["actor"]["requested_model"]];req(mr["resolved"]==c["actor"]["required_resolved_model"],"resolved model drift");req(ident.get("provider_retry_limit")==0,"identity retry drift")
    suite=Path(c["suite"]["root"])
    for n,key in (("suite_manifest.json","suite_manifest_sha256"),("bridge_split_manifest.json","split_manifest_sha256"),("bridge_metadata.json","metadata_sha256")):req(sha(suite/n)==c["suite"][key],f"suite drift:{n}")
    mind=Path(c["mindmemos"]["root"]);head=subprocess.check_output(["git","-C",str(mind),"rev-parse","HEAD"],text=True).strip();req(head==c["mindmemos"]["commit"],"MindMemOS drift")
    skill=Path(c["initial_skill"]["path"]);req(skill.is_file() and sha(skill)==c["initial_skill"]["sha256"],"initial skill drift")
    expected=[u.unit_id for u in search_units(SCREEN)];req(c["search"]["unit_ids"]==expected and len(expected)==384,"search order drift")
    scope=a.get("execution_scope") or {};required_scope_keys={"contract_sha256","allowed_unit_ids","allowed_task_ids","exact_k","required_resolved_model","identity_artifact_sha256","required_skill_pre_sha256","max_turns","max_output_tokens","automatic_retry","run_root","lineage_lease_path","consumption_marker_path","provider_budget"};req(set(scope)==required_scope_keys,"Stage-A authorization execution-scope surface drift");req(a.get("single_use") is True,"Stage-A authorization must be single-use");req(scope.get("allowed_unit_ids")==expected,"auth unit scope drift");req(scope.get("allowed_task_ids")==c["search"]["task_ids"],"auth task scope drift");req(scope.get("contract_sha256")==cs,"scope contract drift");req(int(scope.get("exact_k",-1))==8,"auth K drift");req(scope.get("required_resolved_model")==c["actor"]["required_resolved_model"],"auth resolved-model drift");req(scope.get("identity_artifact_sha256")==c["model_identity"]["sha256"],"auth identity drift");req(scope.get("required_skill_pre_sha256")==c["initial_skill"]["sha256"],"auth initial-skill drift");req(int(scope.get("max_turns",-1))==c["actor"]["max_turns"],"auth max-turns drift");req(int(scope.get("max_output_tokens",-1))==c["actor"]["max_output_tokens"],"auth output-token drift");req(scope.get("automatic_retry") is False,"auth retry policy drift");req(scope.get("run_root")==c["run_root"] and scope.get("lineage_lease_path")==c["lineage_lease_path"],"auth lineage path drift");req(scope.get("consumption_marker_path")==c["signed_capability_control"]["consumption_marker_path"],"auth consumption-marker path drift")
    pb=scope.get("provider_budget") or {};req(pb.get("required") is True,"auth provider budget missing");req(int(pb.get("total_limit",-1))==c["budget"]["search_provider_call_ceiling"],"auth total budget drift");req(int(pb.get("per_unit_limit",-1))==c["budget"]["per_search_unit_call_ceiling"],"auth per-unit budget drift")
    capdoc=load(capability_path); expected_cap={"contract_sha256":cs,"preflight_sha256":a["preflight_sha256"],"review_receipt_sha256":a["independent_review"]["sha256"],"structural_authorization_sha256":ahs,"runner_sha256":c["bound_code"]["runner"]["sha256"],"runtime_sha256":c["bound_code"]["runtime"]["sha256"],"support_sha256":c["bound_code"]["support"]["sha256"],"identity_sha256":c["model_identity"]["sha256"],"run_root":c["run_root"],"lineage_lease_path":c["lineage_lease_path"],"consumption_marker_path":c["signed_capability_control"]["consumption_marker_path"]};cap=verify_document(capdoc,expected_payload_fields=expected_cap);caps=capability_sha256_file(capability_path)
    return c,a,cap,cs,ahs,caps,{"suite":suite,"mind":mind,"identity":root/c["model_identity"]["path"],"skill":skill}


def claim_count(path:Path)->int:
    if not path.exists():return 0
    db=sqlite3.connect(f"file:{path}?mode=ro",uri=True)
    try:return int(db.execute("select count(*) from claims").fetchone()[0])
    finally:db.close()


def consume_capability(*,marker_path:Path,capability_sha256:str,capability_id:str,contract_sha256:str,authorization_sha256:str)->None:
    marker_path.parent.mkdir(parents=True,exist_ok=True)
    payload={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-capability-consumption","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"capability_sha256":capability_sha256,"capability_id":capability_id,"contract_sha256":contract_sha256,"authorization_sha256":authorization_sha256,"consumed_before_provider_io":True}
    raw=(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode("utf-8")
    fd=os.open(marker_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:os.write(fd,raw);os.fsync(fd)
    finally:os.close(fd)


async def run_stage_a(*,root:Path,contract_path:Path,auth_path:Path,signed_capability_path:Path,env_file:Path,stop_before_provider_io:bool=False,preflight_output:Path|None=None)->int:
    c,a,cap,cs,ahs,caps,s=validate(contract_path,auth_path,signed_capability_path,root); runtime_python,_=validate_runtime({"runtime":c["runtime"]});req(Path(sys.executable).resolve()==runtime_python.resolve(),"Stage-A runner must execute under the exact frozen actor runtime Python")
    req(env_file.resolve()==Path(c["env_file"]).resolve(),"Stage-A env-file path drift");load_env_file(env_file); src=ArkSettings.from_env(required=True);req(src.base_url.rstrip("/")==PLAN_BASE_URL,"non-Ark Plan route")
    settings=ArkSettings(api_key=src.api_key,base_url=src.base_url,default_model=src.default_model,timeout_seconds=300,max_retries=0)
    if stop_before_provider_io:
        req(preflight_output is not None and not preflight_output.exists(),"preflight output not fresh")
        out={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-actual-path-preflight","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"PASS_BRIDGE_V4R2_STAGE_A_ACTUAL_PATH_STOPPED_BEFORE_PROVIDER_IO","contract_sha256":cs,"authorization_sha256":ahs,"signed_capability_sha256":caps,"capability_id":cap["capability_id"],"capability_verified":True,"capability_consumed":False,"search_units":384,"streams":6,"tasks":48,"search_k":8,"provider_calls":0,"provider_claims":0,"support_inspected":False,"updater_calls":0,"heldout_actor_calls":0,"validation_open":False,"next_gate":"EXECUTE_EXACT_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SEQUENCE"};atomic_json(preflight_output,out);print(json.dumps(out,indent=2,sort_keys=True));return 0
    rr=Path(c["run_root"]);leasep=Path(c["lineage_lease_path"]);markerp=Path(c["signed_capability_control"]["consumption_marker_path"]);req(not rr.exists() and not leasep.exists() and not markerp.exists(),"Stage-A root/lease/capability marker not fresh");consume_capability(marker_path=markerp,capability_sha256=caps,capability_id=str(cap["capability_id"]),contract_sha256=cs,authorization_sha256=ahs);rr.mkdir(parents=True)
    lease={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-lineage-lease","status":RUNNING,"created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"contract_sha256":cs,"authorization_sha256":ahs,"signed_capability_sha256":caps,"capability_id":cap["capability_id"],"capability_consumption_marker_path":str(markerp),"capability_consumption_marker_sha256":sha(markerp),"exactly_once":True,"completed_search_units":0,"support_inspected":False,"updater_calls":0,"heldout_actor_calls":0};atomic_json(leasep,lease)
    budgetp=rr/"provider_budget.sqlite3";budget=ProviderBudgetLedger(path=budgetp,contract_sha256=cs,authorization_sha256=ahs,total_limit=c["budget"]["search_provider_call_ceiling"],per_unit_limit=c["budget"]["per_search_unit_call_ceiling"],allow_create=True)
    manifest=rr/"completed_search_units.jsonl";ReactAgentFactory,SpreadsheetBenchEnv=load_mindmemos(s["mind"]);meta={str(x["id"]):x for x in load(s["suite"]/"bridge_metadata.json")};evsrc=[s["mind"]/"src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",s["mind"]/"src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py"]
    units=search_units(SCREEN);initial_dir=s["skill"].parent
    try:
        for seq,u in enumerate(units):
            ur=rr/"units"/f"{seq:03d}_{u.stream_id}_{u.task_id}_k{u.candidate_index}";req(not ur.exists(),f"preexisting unit:{u.unit_id}");env=SpreadsheetBenchEnv(s["suite"],ur);case={x.id:x for x in env.load_cases("all")}[u.task_id]
            adapter=ArkPlanReactLLM(settings=settings,requested_model=c["actor"]["requested_model"],required_resolved_model=c["actor"]["required_resolved_model"],max_output_tokens=c["actor"]["max_output_tokens"],temperature=0,thinking="disabled",provider_budget_ledger=budget,provider_budget_unit_id=u.unit_id)
            factory=ReactAgentFactory(adapter,max_turns=c["actor"]["max_turns"],skill_sources=[initial_dir],python_path=str(runtime_python));cfg=ActorRolloutConfig(requested_model=c["actor"]["requested_model"],required_resolved_model=c["actor"]["required_resolved_model"],max_turns=c["actor"]["max_turns"],skill_source=str(initial_dir),skill_pre_sha256=c["initial_skill"]["sha256"],failure_family=str(meta[u.task_id].get("primary_failure_family") or ""),experiment_mode="bridge_v4r2_stage_a_search",contract_sha256=cs,authorization_sha256=ahs)
            ref=await run_actor_rollout(env=env,case=case,rollout_index=u.candidate_index-1,agent_factory=factory,adapter=adapter,config=cfg,evaluator_sources=evsrc);refp=Path(ref.trajectory_path).with_name("r17_trajectory_ref.json")
            append(manifest,{"sequence":seq,"unit_id":u.unit_id,"stream_id":u.stream_id,"task_id":u.task_id,"candidate_index":u.candidate_index,"trajectory_ref_path":str(refp),"trajectory_ref_sha256":file_sha256(refp),"provider_claim_count":ref.provider_budget_claim_count});lease["completed_search_units"]=seq+1;atomic_json(leasep,lease)
        done=rows(manifest);req(len(done)==384 and [x["unit_id"] for x in done]==[u.unit_id for u in units],"completed search order drift")
        bytask:dict[str,list[TrajectoryRef]]={}
        for x in done:
            rp=Path(x["trajectory_ref_path"]);req(rp.is_file() and file_sha256(rp)==x["trajectory_ref_sha256"],"trajectory ref drift");ref=TrajectoryRef(**load(rp));ref.validate();tp=Path(ref.trajectory_path);req(tp.is_file() and file_sha256(tp)==ref.trajectory_sha256,"trajectory drift");bytask.setdefault(x["task_id"],[]).append(ref)
        bystream:dict[str,tuple[SearchPool,...]]={};pm=[]
        for sid in stage_stream_ids(SCREEN):
            ps=[]
            for tid in update_tasks(sid):
                rs=sorted(bytask[tid],key=lambda r:r.rollout_index);req(len(rs)==8 and [r.rollout_index for r in rs]==list(range(8)),f"rollout geometry:{tid}");pr=rr/"sealed_pools"/sid/tid;pool=freeze_nested_pools(task_dir=pr,trajectories=rs,prefix_ks=(8,))[8];ps.append(pool);pp=pr/"pool_k8.json";pm.append({"stream_id":sid,"task_id":tid,"pool_id":pool.pool_id,"pool_path":str(pp),"pool_sha256":file_sha256(pp),"mixed_pool":pool.mixed_pool})
            bystream[sid]=tuple(ps)
        support=evaluate_screen_support(bystream);status="PASS_BRIDGE_V4R2_STAGE_A_SCREEN_SUPPORT" if support.all_streams_qualified else "HOLD_BRIDGE_V4R2_STAGE_A_INSUFFICIENT_MIXED_SUPPORT"
        sr={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-screen-support","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":status,"contract_sha256":cs,"authorization_sha256":ahs,"signed_capability_sha256":caps,"capability_consumption_marker_sha256":sha(markerp),"search_units":384,"streams":6,"tasks":48,"pool_manifest":pm,"support":support.to_dict(),"provider_budget":budget.snapshot().to_dict(),"support_inspected":True,"updater_calls":0,"deterministic_state_materializations":0,"heldout_actor_calls":0,"screen_outcomes_opened":False,"validation_open":False,"replacement_allowed":False,"next_gate":"SEPARATE_BRIDGE_V4R2_SCREEN_STATE_GENERATION_CONTRACT" if support.all_streams_qualified else "HOLD_BRIDGE_V4R2_NO_REPLACEMENT_NO_STATE_GENERATION"};sp=rr/"stage_a_support.json";atomic_json(sp,sr)
        lease.update({"status":"COMPLETED_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SUPPORT_PASS" if support.all_streams_qualified else "COMPLETED_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SUPPORT_HOLD","sealed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"completed_search_units":384,"support_inspected":True,"support_status":status,"support_receipt_path":str(sp),"support_receipt_sha256":sha(sp)});atomic_json(leasep,lease)
        final={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-run-summary","status":"COMPLETED_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_PENDING_SEPARATE_SUPPORT_DECISION","contract_sha256":cs,"authorization_sha256":ahs,"signed_capability_sha256":caps,"capability_consumption_marker_sha256":sha(markerp),"completed_search_units":384,"support_status":status,"support_receipt_path":str(sp),"support_receipt_sha256":sha(sp),"provider_budget":budget.snapshot().to_dict(),"scientific_method_effect_read":False,"updater_calls":0,"heldout_actor_calls":0,"validation_open":False};atomic_json(rr/"run_summary.json",final);print(json.dumps(final,indent=2,sort_keys=True));return 0
    except Exception as e:
        lease.update({"status":FAIL,"failed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"error_type":type(e).__name__,"error":str(e)[:1600],"automatic_retry_authorized":False,"support_inspected":False,"updater_calls":0,"heldout_actor_calls":0});atomic_json(leasep,lease);raise
