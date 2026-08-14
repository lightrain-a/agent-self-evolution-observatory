from __future__ import annotations

import argparse,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_evidence_acquisition import build_provisional_evidence_plan
from .paper_first_problem_discovery_contract import audit_shadow_problem_candidate
from .problem_search_control_snapshot import compute_control_snapshot
from .problem_search_stage_runner import _normalize,_problem_falsifier_eligible

DEFAULT_JSON=PROJECT_ROOT/"generated"/"paper-first-evidence-migration-state.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"paper-first-evidence-migration-state.js"
SCHEMA_VERSION="1.0"

POLICY={
 "scientific_authority":False,
 "legacy_terminal_run_is_immutable":True,
 "migration_is_new_zero_authority_control_transaction":True,
 "migration_reuses_only_frozen_parent_formulations_and_primary_registry":True,
 "no_generator_or_search_model_calls":True,
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
 source_manifest=_manifest(source_run)
 migration_id="legacy-reduction-"+hashlib.sha256((source_run.name+source_manifest+control["control_snapshot_sha256"]).encode()).hexdigest()[:16]
 return {"schema_version":SCHEMA_VERSION,"generated_at":_now(),"migration_id":migration_id,"source_run_id":source_run.name,"source_manifest_sha256":source_manifest,"current_control_snapshot_sha256":control["control_snapshot_sha256"],"status":"LEGACY_REDUCTION_EVIDENCE_MIGRATION_READY" if pending else "LEGACY_REDUCTION_EVIDENCE_MIGRATION_EMPTY","policy":dict(POLICY),"summary":{"source_formulated":formulated,"current_machine_ready":len(ready),"current_reduction_pending":len(pending),"current_blocked":len(blocked),"provisional_problem_candidates":int((evidence.get("summary") or {}).get("provisional_problem_candidates") or 0),"evidence_design_selected":int((evidence.get("summary") or {}).get("design_selected") or 0),"evidence_design_pending":int((evidence.get("summary") or {}).get("design_pending") or 0),"evidence_deferred_by_portfolio_budget":int((evidence.get("summary") or {}).get("deferred_by_portfolio_budget") or 0),"evidence_execution_ready":0,"evidence_execution_completed":0,"evidence_reduction_supported":0,"evidence_residual_survives":0,"evidence_branch_repair_ready":0,"scientific_authority":0,"problem_gate_authorized":0,"paper_design_authorized":0,"method_authorized":0,"p0_authorized":0,"gpu_authorized":0},"machine_projection":{"ready":ready,"reduction_pending":pending,"blocked":blocked},"evidence_plan":evidence,"scientific_authority":False,"authority":dict(AUTHORITY)}

def public_migration_summary(state:dict[str,Any])->dict[str,Any]:
 s=state.get("summary") or {}
 return {"schema_version":SCHEMA_VERSION,"generated_at":state.get("generated_at"),"migration_id":str(state.get("migration_id") or ""),"source_run_id":str(state.get("source_run_id") or ""),"source_manifest_sha256":str(state.get("source_manifest_sha256") or ""),"current_control_snapshot_sha256":str(state.get("current_control_snapshot_sha256") or ""),"status":str(state.get("status") or "NOT_RUN"),"policy":dict(POLICY),"summary":{k:int(s.get(k) or 0) for k in ("source_formulated","current_machine_ready","current_reduction_pending","current_blocked","provisional_problem_candidates","evidence_design_selected","evidence_design_pending","evidence_deferred_by_portfolio_budget","evidence_execution_ready","evidence_execution_completed","evidence_reduction_supported","evidence_residual_survives","evidence_branch_repair_ready","scientific_authority","problem_gate_authorized","paper_design_authorized","method_authorized","p0_authorized","gpu_authorized")},"scientific_authority":False,"authority":dict(AUTHORITY)}

def write_legacy_reduction_migration(*,source_run:Path,private_out:Path,public_json:Path=DEFAULT_JSON,public_js:Path=DEFAULT_JS)->dict[str,Any]:
 state=compile_legacy_reduction_migration(source_run=source_run);private_out.parent.mkdir(parents=True,exist_ok=True);private_out.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 public=public_migration_summary(state);public_json.parent.mkdir(parents=True,exist_ok=True);public_json.write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");public_js.write_text("window.PAPER_FIRST_EVIDENCE_MIGRATION = "+json.dumps(public,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8");return public

def load_public_migration(path:Path=DEFAULT_JSON)->dict[str,Any]:
 try:return _load(path)
 except (OSError,json.JSONDecodeError,ValueError):return {"schema_version":SCHEMA_VERSION,"status":"NOT_RUN","policy":dict(POLICY),"summary":{},"scientific_authority":False,"authority":dict(AUTHORITY)}

def validate_public_migration(state:dict[str,Any])->list[str]:
 errors=[];s=state.get("summary") or {};p=state.get("policy") or {}
 if state.get("scientific_authority") is not False or p.get("legacy_terminal_run_is_immutable") is not True or p.get("migration_cannot_rewrite_parent_terminal_artifacts") is not True or p.get("migrated_candidates_enter_bounded_evidence_design_only") is not True:errors.append("legacy evidence migration must remain immutable-parent zero-authority control")
 if any(int(s.get(k) or 0)!=0 for k in ("scientific_authority","problem_gate_authorized","paper_design_authorized","method_authorized","p0_authorized","gpu_authorized")):errors.append("legacy evidence migration cannot authorize downstream science")
 if int(s.get("current_machine_ready") or 0)+int(s.get("current_reduction_pending") or 0)+int(s.get("current_blocked") or 0)!=int(s.get("source_formulated") or 0):errors.append("legacy evidence migration routing accounting mismatch")
 if int(s.get("provisional_problem_candidates") or 0)!=int(s.get("current_reduction_pending") or 0):errors.append("legacy evidence migration must cover every current reduction-pending candidate")
 for k in ("source_manifest_sha256","current_control_snapshot_sha256"):
  v=str(state.get(k) or "")
  if state.get("status")!="NOT_RUN" and not re.fullmatch(r"[0-9a-f]{64}",v):errors.append("legacy evidence migration digest invalid:"+k)
 return sorted(set(errors))

def main()->None:
 ap=argparse.ArgumentParser();ap.add_argument("--source-run",type=Path,required=True);ap.add_argument("--private-out",type=Path,required=True);a=ap.parse_args();print(json.dumps(write_legacy_reduction_migration(source_run=a.source_run,private_out=a.private_out),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
