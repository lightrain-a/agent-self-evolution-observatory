from __future__ import annotations

import argparse,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_evidence_acquisition import build_provisional_evidence_plan,build_substrate_preflight_request,compile_evidence_designs,compile_evidence_reviews,compile_substrate_preflight,compile_harness_implementation_receipts,evidence_design_prompt,evidence_review_prompt
from .paper_first_problem_discovery_contract import audit_shadow_problem_candidate
from .problem_search_control_snapshot import compute_control_snapshot
from .problem_search_stage_runner import _ark_with_provider_receipt,_normalize,_parse_archived_evidence_design_json,_problem_falsifier_eligible

DEFAULT_JSON=PROJECT_ROOT/"generated"/"paper-first-evidence-migration-state.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"paper-first-evidence-migration-state.js"
SCHEMA_VERSION="1.0"

POLICY={
 "scientific_authority":False,
 "legacy_terminal_run_is_immutable":True,
 "migration_is_new_zero_authority_control_transaction":True,
 "migration_reuses_only_frozen_parent_formulations_and_primary_registry":True,
 "no_generator_or_search_model_calls":True,
 "bounded_evidence_design_model_calls_are_allowed":True,
 "bounded_evidence_design_model_call_has_zero_scientific_authority":True,
 "independent_evidence_contract_review_required_before_execution":True,
 "evidence_designer_cannot_self_review":True,
 "bounded_substrate_preflight_required_after_contract_review":True,
 "contract_review_clear_does_not_authorize_execution":True,
 "frozen_scientific_fields_are_compiler_owned":True,
 "outcome_labels_are_compiler_owned":True,
 "current_machine_contract_reaudits_parent_formulations":True,
 "only_current_exact_reduction_uncertainty_can_migrate":True,
 "migration_cannot_rewrite_parent_terminal_artifacts":True,
 "migration_cannot_authorize_problem_gate_paper_design_method_p0_gpu":True,
 "migrated_candidates_enter_bounded_evidence_design_only":True,
 "residual_evidence_cannot_auto_certify_novelty":True,
}
AUTHORITY={"live_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}

def _now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _load(path:Path)->dict[str,Any]:
 p=json.loads(path.read_text(encoding="utf-8"));
 if not isinstance(p,dict):raise ValueError(f"expected JSON object:{path}")
 return p
def _sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def _manifest(source_run:Path)->str:
 files=[source_run/"frozen-primary-evidence-pool.json",source_run/"machine-audit.json",source_run/"shadow-terminal-current-source-gate.json"]+sorted(source_run.glob("formulate-p*.json"))
 qual=source_run/"shadow-run-qualification.json"
 if qual.exists():files.append(qual)
 preflight=source_run/"problem-falsifier-preflight.json"
 if preflight.exists():files.append(preflight)
 if any(not p.is_file() for p in files):raise ValueError("legacy migration source artifacts incomplete")
 rows=[{"name":p.name,"sha256":_sha(p)} for p in sorted(files,key=lambda x:x.name)]
 return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def compile_legacy_reduction_migration(*,source_run:Path,project_root:Path=PROJECT_ROOT)->dict[str,Any]:
 terminal=_load(source_run/"shadow-terminal-current-source-gate.json")
 if terminal.get("status")!="SHADOW_TERMINAL_COMPLETE":raise ValueError("legacy migration requires an immutable terminal-complete parent run")
 if (source_run/"evidence-acquisition-plan.json").exists():raise ValueError("parent already contains evidence-acquisition semantics; legacy migration forbidden")
 pool=_load(source_run/"frozen-primary-evidence-pool.json");records=[r for r in pool.get("records") or [] if isinstance(r,dict)];registry={str(r.get("ref")):r for r in records if r.get("ref")}
 if not registry:raise ValueError("legacy migration requires the frozen parent primary registry")
 control=compute_control_snapshot(project_root=project_root)
 pending=[];blocked=[];ready=[];seen=set();formulated=0
 for path in sorted(source_run.glob("formulate-p*.json"),key=lambda p:int(re.search(r"p(\d+)$",p.stem).group(1)) if re.search(r"p(\d+)$",p.stem) else 10**9):
  payload=_load(path);part=int(payload.get("part") or 0);source_rows=[]
  source_rows.extend([x for x in payload.get("candidates") or [] if isinstance(x,dict)])
  source_rows.extend([(x.get("candidate") or x) for x in payload.get("reduction_pending") or [] if isinstance(x,dict)])
  for idx,raw in enumerate(source_rows,1):
   candidate=_normalize(dict(raw),registry);cid=str(candidate.get("candidate_id") or "").strip() or f"LEGACY-P{part:02d}-C{idx:02d}"
   if cid in seen:raise ValueError(f"duplicate legacy candidate id:{cid}")
   seen.add(cid);candidate["candidate_id"]=cid;formulated+=1
   audit=audit_shadow_problem_candidate(candidate,primary_evidence_by_ref=registry,require_primary_registry=True,require_semantic_review=False)
   row={"candidate_id":cid,"source_artifact":path.name,"candidate":candidate,"audit":audit,"scientific_authority":False}
   if audit.get("passed") is True:ready.append(row)
   elif _problem_falsifier_eligible(candidate,audit):
    pending.append(row)
   else:blocked.append(row)
 machine={"schema_version":"1.0-evidence-migration","scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},"problem_falsifier_queue":[{"candidate_id":r["candidate_id"],"title":r["candidate"].get("title"),"discovery_lane":r["candidate"].get("discovery_lane"),"source_branch_id":r["candidate"].get("source_branch_id"),"blockers":list((r["audit"] or {}).get("blockers") or []),"exact_prediction":r["candidate"].get("exact_prediction"),"strongest_same_information_baseline":r["candidate"].get("strongest_same_information_baseline"),"cheapest_problem_falsifier":r["candidate"].get("cheapest_problem_falsifier"),"scientific_authority":False} for r in pending]}
 evidence=build_provisional_evidence_plan(machine,run_id=f"evidence-migration-{source_run.name}")
 support_by_id={}
 preflight_path=source_run/"problem-falsifier-preflight.json"
 if preflight_path.exists():
  preflight=_load(preflight_path)
  for row in preflight.get("rows") or []:
   if not isinstance(row,dict):continue
   cid=str(row.get("candidate_id") or "").strip()
   if cid:support_by_id[cid]={"disposition":str(row.get("disposition") or ""),"required_unit":str(row.get("required_unit") or "")[:2200],"asset_audit":str(row.get("asset_audit") or "")[:2600],"primary_refs":[str(x) for x in row.get("primary_refs") or []],"reopen_only_if":str(row.get("reopen_only_if") or "")[:2200],"scientific_authority":False}
 for entry in evidence.get("entries") or []:
  if isinstance(entry,dict):entry["prior_support"]=support_by_id.get(str(entry.get("candidate_id") or ""),{"disposition":"NO_PRIOR_SUPPORT_RECEIPT","scientific_authority":False})
 source_manifest=_manifest(source_run)
 migration_id="legacy-reduction-"+hashlib.sha256((source_run.name+source_manifest+control["control_snapshot_sha256"]).encode()).hexdigest()[:16]
 return {"schema_version":SCHEMA_VERSION,"generated_at":_now(),"migration_id":migration_id,"source_run_id":source_run.name,"source_manifest_sha256":source_manifest,"current_control_snapshot_sha256":control["control_snapshot_sha256"],"status":"LEGACY_REDUCTION_EVIDENCE_MIGRATION_READY" if pending else "LEGACY_REDUCTION_EVIDENCE_MIGRATION_EMPTY","policy":dict(POLICY),"summary":{"source_formulated":formulated,"current_machine_ready":len(ready),"current_reduction_pending":len(pending),"current_blocked":len(blocked),"provisional_problem_candidates":int((evidence.get("summary") or {}).get("provisional_problem_candidates") or 0),"evidence_design_selected":int((evidence.get("summary") or {}).get("design_selected") or 0),"evidence_design_pending":int((evidence.get("summary") or {}).get("design_pending") or 0),"evidence_deferred_by_portfolio_budget":int((evidence.get("summary") or {}).get("deferred_by_portfolio_budget") or 0),"evidence_review_pending":0,"evidence_review_clear":0,"evidence_review_revise":0,"evidence_review_blocked":0,"evidence_substrate_preflight_pending":0,"evidence_substrate_ready":0,"evidence_harness_implementation_pending":0,"evidence_substrate_hold":0,"evidence_execution_ready":0,"evidence_execution_completed":0,"evidence_reduction_supported":0,"evidence_residual_survives":0,"evidence_branch_repair_ready":0,"scientific_authority":0,"problem_gate_authorized":0,"paper_design_authorized":0,"method_authorized":0,"p0_authorized":0,"gpu_authorized":0},"machine_projection":{"ready":ready,"reduction_pending":pending,"blocked":blocked},"evidence_plan":evidence,"scientific_authority":False,"authority":dict(AUTHORITY)}

def public_migration_summary(state:dict[str,Any])->dict[str,Any]:
 s=state.get("summary") or {}
 return {"schema_version":SCHEMA_VERSION,"generated_at":state.get("generated_at"),"migration_id":str(state.get("migration_id") or ""),"source_run_id":str(state.get("source_run_id") or ""),"source_manifest_sha256":str(state.get("source_manifest_sha256") or ""),"current_control_snapshot_sha256":str(state.get("current_control_snapshot_sha256") or ""),"status":str(state.get("status") or "NOT_RUN"),"policy":dict(POLICY),"summary":{k:int(s.get(k) or 0) for k in ("source_formulated","current_machine_ready","current_reduction_pending","current_blocked","provisional_problem_candidates","evidence_design_selected","evidence_design_pending","evidence_deferred_by_portfolio_budget","evidence_review_pending","evidence_review_clear","evidence_review_revise","evidence_review_blocked","evidence_substrate_preflight_pending","evidence_substrate_ready","evidence_harness_implementation_pending","evidence_substrate_hold","evidence_execution_ready","evidence_execution_completed","evidence_reduction_supported","evidence_residual_survives","evidence_branch_repair_ready","scientific_authority","problem_gate_authorized","paper_design_authorized","method_authorized","p0_authorized","gpu_authorized")},"scientific_authority":False,"authority":dict(AUTHORITY)}

def write_legacy_reduction_migration(*,source_run:Path,private_out:Path,public_json:Path=DEFAULT_JSON,public_js:Path=DEFAULT_JS)->dict[str,Any]:
 state=compile_legacy_reduction_migration(source_run=source_run);private_out.parent.mkdir(parents=True,exist_ok=True);private_out.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 public=public_migration_summary(state);public_json.parent.mkdir(parents=True,exist_ok=True);public_json.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");public_js.write_text("window.PAPER_FIRST_EVIDENCE_MIGRATION = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return public

def _sync_evidence_summary(state:dict[str,Any])->dict[str,Any]:
 evidence_summary=(state.get("evidence_plan") or {}).get("summary") or {};summary=state.get("summary") or {}
 mapping={"provisional_problem_candidates":"provisional_problem_candidates","design_selected":"evidence_design_selected","design_pending":"evidence_design_pending","deferred_by_portfolio_budget":"evidence_deferred_by_portfolio_budget","review_pending":"evidence_review_pending","review_clear":"evidence_review_clear","review_revise":"evidence_review_revise","review_blocked":"evidence_review_blocked","substrate_preflight_pending":"evidence_substrate_preflight_pending","substrate_ready":"evidence_substrate_ready","substrate_implementation_pending":"evidence_harness_implementation_pending","substrate_hold":"evidence_substrate_hold","execution_ready":"evidence_execution_ready","execution_completed":"evidence_execution_completed","reduction_supported":"evidence_reduction_supported","residual_survives":"evidence_residual_survives","branch_repair_ready":"evidence_branch_repair_ready"}
 for source,target in mapping.items():summary[target]=int(evidence_summary.get(source) or 0)
 state["summary"]=summary;state["generated_at"]=_now();return state

def design_legacy_reduction_migration(*,private_state_path:Path,part:int=1,model:str="ark-code-latest",public_json:Path=DEFAULT_JSON,public_js:Path=DEFAULT_JS)->dict[str,Any]:
 state=_load(private_state_path)
 if state.get("scientific_authority") is not False or (state.get("policy") or {}).get("migrated_candidates_enter_bounded_evidence_design_only") is not True:raise ValueError("invalid zero-authority evidence migration state")
 current_control=compute_control_snapshot(project_root=PROJECT_ROOT)["control_snapshot_sha256"]
 if str(state.get("current_control_snapshot_sha256") or "")!=current_control:raise ValueError("evidence migration control snapshot drift; re-prepare continuation before model design")
 plan=state.get("evidence_plan") or {};prompt,candidate_ids=evidence_design_prompt(plan,part=part,batch_size=2);root=private_state_path.parent;stem=f"evidence-design-p{part}"
 res=_ark_with_provider_receipt(run_root=root,stem=stem,requested_model=model,context={"part":part,"candidate_ids":candidate_ids,"control_snapshot_sha256":current_control},prompt=prompt,max_output_tokens=5200,temperature=0.0)
 raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,raw_sha=_parse_archived_evidence_design_json(root,stem,raw,resolved);compiled=compile_evidence_designs(plan,payload,part=part,design_model=resolved);state["evidence_plan"]=compiled;state=_sync_evidence_summary(state)
 private_state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 artifact={"schema_version":"1.0","generated_at":_now(),"migration_id":state.get("migration_id"),"source_run_id":state.get("source_run_id"),"part":part,"candidate_ids":candidate_ids,"requested_model":model,"resolved_model":resolved,"raw_sha256":raw_sha,"plan_summary":compiled.get("summary") or {},"scientific_authority":False,"authority":dict(AUTHORITY)}
 (root/f"{stem}.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 public=public_migration_summary(state);public_json.parent.mkdir(parents=True,exist_ok=True);public_json.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");public_js.write_text("window.PAPER_FIRST_EVIDENCE_MIGRATION = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
 return {"status":public.get("status"),"migration_id":public.get("migration_id"),"part":part,"candidate_ids":candidate_ids,"resolved_model":resolved,"raw_sha256":raw_sha,"summary":public.get("summary") or {},"scientific_authority":False}

def review_legacy_reduction_design(*,private_state_path:Path,part:int=1,model:str="glm-5.2",public_json:Path=DEFAULT_JSON,public_js:Path=DEFAULT_JS)->dict[str,Any]:
 state=_load(private_state_path);current_control=compute_control_snapshot(project_root=PROJECT_ROOT)["control_snapshot_sha256"]
 if str(state.get("current_control_snapshot_sha256") or "")!=current_control:raise ValueError("evidence migration control snapshot drift; re-prepare continuation before independent review")
 plan=state.get("evidence_plan") or {};root=private_state_path.parent;stem=f"evidence-review-p{part}";prompt,candidate_ids=evidence_review_prompt(plan,part=part,batch_size=2);res=_ark_with_provider_receipt(run_root=root,stem=stem,requested_model=model,context={"part":part,"candidate_ids":candidate_ids,"control_snapshot_sha256":current_control},prompt=prompt,max_output_tokens=4200,temperature=0.0)
 raw=str(res.get("text") or "");resolved=str(res.get("resolved_model") or model);payload,raw_sha=_parse_archived_evidence_design_json(root,stem,raw,resolved);compiled=compile_evidence_reviews(plan,payload,part=part,reviewer_model=resolved);state["evidence_plan"]=compiled;state=_sync_evidence_summary(state);private_state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 artifact={"schema_version":"1.0","generated_at":_now(),"migration_id":state.get("migration_id"),"source_run_id":state.get("source_run_id"),"part":part,"candidate_ids":candidate_ids,"requested_model":model,"resolved_model":resolved,"raw_sha256":raw_sha,"plan_summary":compiled.get("summary") or {},"scientific_authority":False,"authority":dict(AUTHORITY)};(root/f"{stem}.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 public=public_migration_summary(state);public_json.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");public_js.write_text("window.PAPER_FIRST_EVIDENCE_MIGRATION = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return {"status":public.get("status"),"migration_id":public.get("migration_id"),"part":part,"candidate_ids":candidate_ids,"resolved_model":resolved,"raw_sha256":raw_sha,"summary":public.get("summary") or {},"scientific_authority":False}

def write_legacy_substrate_request(*,private_state_path:Path,request_out:Path)->dict[str,Any]:
 state=_load(private_state_path);current_control=compute_control_snapshot(project_root=PROJECT_ROOT)["control_snapshot_sha256"]
 if str(state.get("current_control_snapshot_sha256") or "")!=current_control:raise ValueError("evidence migration control snapshot drift; re-prepare continuation before substrate preflight")
 request=build_substrate_preflight_request(state.get("evidence_plan") or {});request["migration_id"]=state.get("migration_id");request["current_control_snapshot_sha256"]=current_control;request_out.parent.mkdir(parents=True,exist_ok=True);request_out.write_text(json.dumps(request,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");return request

def apply_legacy_substrate_preflight(*,private_state_path:Path,receipt_path:Path,public_json:Path=DEFAULT_JSON,public_js:Path=DEFAULT_JS)->dict[str,Any]:
 state=_load(private_state_path);current_control=compute_control_snapshot(project_root=PROJECT_ROOT)["control_snapshot_sha256"]
 if str(state.get("current_control_snapshot_sha256") or "")!=current_control:raise ValueError("evidence migration control snapshot drift; re-prepare continuation before substrate preflight")
 receipts=_load(receipt_path);compiled=compile_substrate_preflight(state.get("evidence_plan") or {},receipts);state["evidence_plan"]=compiled;state=_sync_evidence_summary(state);private_state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 root=private_state_path.parent;artifact={"schema_version":"1.0","generated_at":_now(),"migration_id":state.get("migration_id"),"receipt_sha256":_sha(receipt_path),"summary":compiled.get("summary") or {},"scientific_authority":False,"authority":dict(AUTHORITY)};(root/"evidence-substrate-preflight.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 public=public_migration_summary(state);public_json.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");public_js.write_text("window.PAPER_FIRST_EVIDENCE_MIGRATION = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return public

def apply_legacy_harness_receipts(*,private_state_path:Path,receipt_path:Path,public_json:Path=DEFAULT_JSON,public_js:Path=DEFAULT_JS)->dict[str,Any]:
 state=_load(private_state_path);current_control=compute_control_snapshot(project_root=PROJECT_ROOT)["control_snapshot_sha256"]
 if str(state.get("current_control_snapshot_sha256") or "")!=current_control:raise ValueError("evidence migration control snapshot drift; re-prepare continuation before harness receipt")
 receipts=_load(receipt_path);compiled=compile_harness_implementation_receipts(state.get("evidence_plan") or {},receipts);state["evidence_plan"]=compiled;state=_sync_evidence_summary(state);private_state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 root=private_state_path.parent;artifact={"schema_version":"1.0","generated_at":_now(),"migration_id":state.get("migration_id"),"receipt_sha256":_sha(receipt_path),"summary":compiled.get("summary") or {},"scientific_authority":False,"authority":dict(AUTHORITY)};(root/"evidence-harness-implementation.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 public=public_migration_summary(state);public_json.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");public_js.write_text("window.PAPER_FIRST_EVIDENCE_MIGRATION = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return public

def replay_legacy_reduction_design(*,private_state_path:Path,raw_path:Path,part:int=1,resolved_model:str="archived-provider-response",public_json:Path=DEFAULT_JSON,public_js:Path=DEFAULT_JS)->dict[str,Any]:
 state=_load(private_state_path);current_control=compute_control_snapshot(project_root=PROJECT_ROOT)["control_snapshot_sha256"]
 if str(state.get("current_control_snapshot_sha256") or "")!=current_control:raise ValueError("evidence migration control snapshot drift; re-prepare continuation before replay")
 plan=state.get("evidence_plan") or {};root=private_state_path.parent;stem=f"evidence-design-p{part}";raw=raw_path.read_text(encoding="utf-8");payload,raw_sha=_parse_archived_evidence_design_json(root,stem,raw,resolved_model);compiled=compile_evidence_designs(plan,payload,part=part,design_model=resolved_model);state["evidence_plan"]=compiled;state=_sync_evidence_summary(state);private_state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 candidate_ids=[str(row.get("candidate_id") or "") for row in payload.get("designs") or [] if isinstance(row,dict)];artifact={"schema_version":"1.0","generated_at":_now(),"migration_id":state.get("migration_id"),"source_run_id":state.get("source_run_id"),"part":part,"candidate_ids":candidate_ids,"response_origin":"ARCHIVED_PROVIDER_RESPONSE_REPLAY","resolved_model":resolved_model,"raw_sha256":raw_sha,"plan_summary":compiled.get("summary") or {},"provider_called":False,"scientific_authority":False,"authority":dict(AUTHORITY)};(root/f"{stem}.json").write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 public=public_migration_summary(state);public_json.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");public_js.write_text("window.PAPER_FIRST_EVIDENCE_MIGRATION = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return {"status":public.get("status"),"migration_id":public.get("migration_id"),"part":part,"candidate_ids":candidate_ids,"response_origin":"ARCHIVED_PROVIDER_RESPONSE_REPLAY","raw_sha256":raw_sha,"summary":public.get("summary") or {},"provider_called":False,"scientific_authority":False}

def load_public_migration(path:Path=DEFAULT_JSON)->dict[str,Any]:
 try:return _load(path)
 except (OSError,json.JSONDecodeError,ValueError):return {"schema_version":SCHEMA_VERSION,"status":"NOT_RUN","policy":dict(POLICY),"summary":{},"scientific_authority":False,"authority":dict(AUTHORITY)}

def validate_public_migration(state:dict[str,Any])->list[str]:
 errors=[];s=state.get("summary") or {};p=state.get("policy") or {}
 if state.get("scientific_authority") is not False or p.get("legacy_terminal_run_is_immutable") is not True or p.get("migration_cannot_rewrite_parent_terminal_artifacts") is not True or p.get("migrated_candidates_enter_bounded_evidence_design_only") is not True or p.get("independent_evidence_contract_review_required_before_execution") is not True or p.get("evidence_designer_cannot_self_review") is not True or p.get("bounded_substrate_preflight_required_after_contract_review") is not True or p.get("contract_review_clear_does_not_authorize_execution") is not True or p.get("frozen_scientific_fields_are_compiler_owned") is not True or p.get("outcome_labels_are_compiler_owned") is not True:errors.append("legacy evidence migration must remain immutable-parent zero-authority reviewed control")
 if any(int(s.get(k) or 0)!=0 for k in ("scientific_authority","problem_gate_authorized","paper_design_authorized","method_authorized","p0_authorized","gpu_authorized")):errors.append("legacy evidence migration cannot authorize downstream science")
 if int(s.get("current_machine_ready") or 0)+int(s.get("current_reduction_pending") or 0)+int(s.get("current_blocked") or 0)!=int(s.get("source_formulated") or 0):errors.append("legacy evidence migration routing accounting mismatch")
 if int(s.get("provisional_problem_candidates") or 0)!=int(s.get("current_reduction_pending") or 0):errors.append("legacy evidence migration must cover every current reduction-pending candidate")
 for k in ("source_manifest_sha256","current_control_snapshot_sha256"):
  v=str(state.get(k) or "")
  if state.get("status")!="NOT_RUN" and not re.fullmatch(r"[0-9a-f]{64}",v):errors.append("legacy evidence migration digest invalid:"+k)
 return sorted(set(errors))

def main()->None:
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="command",required=True)
 prepare=sub.add_parser("prepare");prepare.add_argument("--source-run",type=Path,required=True);prepare.add_argument("--private-out",type=Path,required=True)
 design=sub.add_parser("design");design.add_argument("--private-state",type=Path,required=True);design.add_argument("--part",type=int,default=1);design.add_argument("--model",default="ark-code-latest")
 review=sub.add_parser("review");review.add_argument("--private-state",type=Path,required=True);review.add_argument("--part",type=int,default=1);review.add_argument("--model",default="glm-5.2")
 substrate_req=sub.add_parser("substrate-request");substrate_req.add_argument("--private-state",type=Path,required=True);substrate_req.add_argument("--out",type=Path,required=True)
 substrate_apply=sub.add_parser("substrate-apply");substrate_apply.add_argument("--private-state",type=Path,required=True);substrate_apply.add_argument("--receipts",type=Path,required=True)
 harness_apply=sub.add_parser("harness-apply");harness_apply.add_argument("--private-state",type=Path,required=True);harness_apply.add_argument("--receipts",type=Path,required=True)
 replay=sub.add_parser("design-replay");replay.add_argument("--private-state",type=Path,required=True);replay.add_argument("--raw",type=Path,required=True);replay.add_argument("--part",type=int,default=1);replay.add_argument("--resolved-model",default="archived-provider-response")
 a=ap.parse_args()
 if a.command=="prepare":result=write_legacy_reduction_migration(source_run=a.source_run,private_out=a.private_out)
 elif a.command=="design":result=design_legacy_reduction_migration(private_state_path=a.private_state,part=a.part,model=a.model)
 elif a.command=="review":result=review_legacy_reduction_design(private_state_path=a.private_state,part=a.part,model=a.model)
 elif a.command=="substrate-request":result=write_legacy_substrate_request(private_state_path=a.private_state,request_out=a.out)
 elif a.command=="substrate-apply":result=apply_legacy_substrate_preflight(private_state_path=a.private_state,receipt_path=a.receipts)
 elif a.command=="harness-apply":result=apply_legacy_harness_receipts(private_state_path=a.private_state,receipt_path=a.receipts)
 else:result=replay_legacy_reduction_design(private_state_path=a.private_state,raw_path=a.raw,part=a.part,resolved_model=a.resolved_model)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
