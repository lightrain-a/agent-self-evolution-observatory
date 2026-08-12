from __future__ import annotations

import hashlib, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGES=("problem","substrate","f0-identifiability","p0-support","p0-method","p1-replication","paper-experiment")
FAILURES={
 "FAIL_PROBLEM":(True,"stop-or-reframe"),"FAIL_SUBSTRATE":(False,"change-substrate"),
 "FAIL_TARGET_DEGENERACY":(False,"repair-target-construction"),"FAIL_REPRESENTATION":(False,"atomic-representation-repair"),
 "FAIL_BASELINE_CEILING":(True,"simplify-or-merge"),"SUPPORT_INSUFFICIENT":(False,"hold-method-inference"),
 "METHOD_FAIL":(True,"merge-stop-or-pivot"),"IMPLEMENTATION_ERROR":(False,"repair-execution-only"),
 "RUNTIME_ERROR":(False,"repair-runtime-only"),"PROVENANCE_INCONCLUSIVE":(False,"repair-provenance-or-rerun"),
 "BUDGET_STOP":(False,"replan-cost-before-rerun"),
}
POLICY={
 "schema_version":"2.1","paper_novelty_precedes_method_design":True,"method_design_precedes_experiment_plan":True,
 "local_validation_precedes_full_experiment":True,"core_method_change_returns_to_paper_design":True,
 "full_experiment_requires_frozen_method_and_experiment_blueprint":True,
 "support_and_method_are_distinct":True,"p0_method_requires_frozen_support_pass":True,
 "support_insufficient_is_not_method_fail":True,"one_load_bearing_repair_per_child":True,
 "max_representation_or_objective_repairs_per_substrate":2,"second_backbone_cannot_rescue_failed_substrate_or_f0":True,
 "raw_trace_is_mandatory_for_gpu_runs":True,"pre_model_load_audit_required":True,"f0_required_before_p0_support":True,
}
PASS_TOKENS={"pass","support-pass","support_qualification_pass","consensus_support_pass","consensus_full_pass","method-pass","qualified"}
PREDECESSOR_EVIDENCE={"substrate":"problem_evidence","f0-identifiability":"substrate_evidence","p0-support":"f0_evidence","p0-method":"support_evidence","p1-replication":"method_evidence","paper-experiment":"p1_evidence"}

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _slug(s:str): return re.sub(r"[^A-Za-z0-9_.-]+","-",s).strip("-")[:140] or "unknown"
def _sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def _atomic(p:Path,row:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); os.replace(t,p)

def infer_stage(config:dict[str,Any])->str:
 g=config.get("governance") or {}; explicit=str(g.get("scientific_stage") or "").strip().lower()
 if explicit:
  if explicit not in STAGES: raise ValueError(f"unknown scientific_stage: {explicit}")
  return explicit
 phase=str(config.get("phase") or "").lower()
 if any(x in phase for x in ("screen","qualif","support")): return "p0-support"
 if phase=="p0": return "p0-method"
 if phase=="p1": return "p1-replication"
 return "f0-identifiability"

def repair_budget_path(root:Path,idea_id:str)->Path: return root/"governance"/"repair-budget"/f"{_slug(idea_id)}.json"
def evaluate_repair_budget(root:Path,idea_id:str,substrate_id:str)->dict[str,Any]:
 path=repair_budget_path(root,idea_id); payload={}
 if path.exists():
  try: payload=json.loads(path.read_text(encoding="utf-8"))
  except (OSError,json.JSONDecodeError): payload={}
 repairs=[r for r in payload.get("repairs") or [] if str(r.get("substrate_id"))==substrate_id]
 load=[r for r in repairs if str(r.get("repair_kind")) in {"representation","objective"}]; limit=int(POLICY["max_representation_or_objective_repairs_per_substrate"])
 return {"idea_id":idea_id,"substrate_id":substrate_id,"path":str(path),"representation_or_objective_repairs":len(load),"limit":limit,"remaining":max(0,limit-len(load)),"exhausted":len(load)>=limit,"launch_allowed":len(load)<limit,"repairs":repairs}

def record_repair(root:Path,idea_id:str,substrate_id:str,repair_kind:str,changed_assumption:str,evidence_id:str="")->dict[str,Any]:
 if repair_kind not in {"representation","objective","substrate","runtime","provenance"}: raise ValueError(repair_kind)
 path=repair_budget_path(root,idea_id); payload={"schema_version":"2.0","idea_id":idea_id,"repairs":[]}
 if path.exists(): payload=json.loads(path.read_text(encoding="utf-8"))
 row={"repair_id":hashlib.sha256(f"{idea_id}|{substrate_id}|{repair_kind}|{changed_assumption}|{len(payload.get('repairs') or [])}".encode()).hexdigest()[:20],"substrate_id":substrate_id,"repair_kind":repair_kind,"changed_assumption":changed_assumption,"evidence_id":evidence_id,"recorded_at":_now()}
 payload.setdefault("repairs",[]).append(row); _atomic(path,payload); return row

def _evidence_path(config:dict[str,Any],root:Path,field:str)->Path|None:
 raw=str(((config.get("governance") or {}).get(field) or "")).strip()
 if not raw: return None
 p=Path(raw).expanduser(); return p if p.is_absolute() else root/p

def _support_pass(row:dict[str,Any])->bool:
 vals=[row.get("status"),row.get("decision"),row.get("result"),(row.get("support_consensus") or {}).get("status")]
 for v in vals:
  if isinstance(v,dict): v=v.get("decision") or v.get("status")
  token=str(v or "").strip().lower().replace(" ","_")
  if token in PASS_TOKENS or token.replace("_","-") in PASS_TOKENS: return True
 if row.get("pass") is True: return True
 checks=row.get("check_updates") or {}
 if checks and str(row.get("authorization_effect") or "") in {"unblock","may-unblock"}:
  return all(isinstance(v,dict) and v.get("pass") is True for v in checks.values())
 return bool(row.get("remaining_replication_authorized") or row.get("formal_method_experiment_authorized"))

def evaluate_stage_contract(idea_id:str,config:dict[str,Any],root:Path)->dict[str,Any]:
 stage=infer_stage(config); gov=config.get("governance") or {}; substrate=str(gov.get("substrate_id") or idea_id)
 budget=evaluate_repair_budget(root,idea_id,substrate); field=PREDECESSOR_EVIDENCE.get(stage); evidence_path=_evidence_path(config,root,field) if field else None
 predecessor={"required":bool(field),"field":field or "","pass":not bool(field),"path":str(evidence_path) if evidence_path else ""}
 if field:
  if evidence_path is None or not evidence_path.exists(): predecessor.update({"pass":False,"reason":f"{field}-missing"})
  else:
   try:
    row=json.loads(evidence_path.read_text(encoding="utf-8")); ok=_support_pass(row); predecessor.update({"pass":ok,"reason":f"{field}-pass" if ok else f"{field}-not-pass","sha256":_sha(evidence_path)})
   except (OSError,json.JSONDecodeError): predecessor.update({"pass":False,"reason":f"{field}-invalid"})
 blockers=[]
 if not predecessor["pass"]: blockers.append(str(predecessor.get("reason")))
 if budget["exhausted"] and stage in {"f0-identifiability","p0-support","p0-method"}: blockers.append("repair-budget-exhausted-for-substrate")
 support=predecessor if field=="support_evidence" else {"required":False,"pass":True,"path":""}
 return {"schema_version":"2.0","idea_id":idea_id,"stage":stage,"stage_index":STAGES.index(stage),"predecessor_authorization":predecessor,"support_authorization":support,"repair_budget":budget,"execution_authorized":not blockers,"blockers":blockers,"policy":POLICY}

def build_governance_state()->dict[str,Any]:
 return {"schema_version":"2.1","generated_at":_now(),"policy":POLICY,"paper_first_macro_stages":["paper-problem-and-evidence","paper-novelty-contract","principle-and-method-design","experiment-blueprint","economy-and-compile","local-validation","method-freeze","full-experiment","paper-evidence"],"stages":[{"index":i,"key":k} for i,k in enumerate(STAGES)],"predecessor_evidence":PREDECESSOR_EVIDENCE,"failure_classes":{k:{"belief_authority":v[0],"next_action":v[1]} for k,v in FAILURES.items()}}

def write_governance_state(json_path:Path,js_path:Path)->dict[str,Any]:
 row=build_governance_state(); _atomic(json_path,row); js_path.parent.mkdir(parents=True,exist_ok=True)
 js_path.write_text("window.RESEARCH_GOVERNANCE_V2 = "+json.dumps(row,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
 return row
