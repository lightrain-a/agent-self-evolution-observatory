from __future__ import annotations

import fcntl, hashlib, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .reopened_scientific_contract import validate_reopened_scientific_contract
from .reopened_scientific_method_design import REVIEW_PASS as METHOD_REVIEW_PASS, validate_reopen_method_design, validate_reopen_method_review

SCHEMA_VERSION="1.0"
BLUEPRINT_STATUS="REOPEN_EXPERIMENT_BLUEPRINT_FROZEN_AWAITING_INDEPENDENT_REVIEW"
REVIEW_PASS="REOPEN_BLUEPRINT_REVIEW_PASS_LOCAL_VALIDATION_AUTHORIZATION_ELIGIBLE"
REVIEW_BLOCK="REOPEN_BLUEPRINT_REVIEW_BLOCKED"
REVIEWER_ROLE="INDEPENDENT_EXPERIMENT_BLUEPRINT_REVIEWER"
ZERO_AUTHORITY={"scientific":False,"method":False,"experiment_blueprint":False,"local_validation":False,"experiment":False,"p0":False,"gpu":False,"submission":False}
REQUIRED_FIELDS=("experiment_id","registered_prediction","unit_definition","qualification_rule","arms","truth_source","metrics","same_information_baselines","sample_plan","statistical_plan","budget","go_stop_rules","compute_graph","observability_recovery","outcome_semantics","provider_plan","gpu_plan","p0_escalation_rule")
REVIEW_CHECKS=("method_alignment_pass","registered_prediction_falsifiable_pass","qualification_outcome_independent_pass","truth_source_external_or_frozen_pass","same_information_baselines_matched_pass","statistical_resolution_precommitted_pass","budget_within_method_cap_pass","compute_graph_complete_pass","observability_recovery_pass","outcome_semantics_typed_pass","local_scope_only_pass","p0_escalation_requires_separate_authority_pass")

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _digest(v:Any)->str: return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _text(v:Any)->str: return str(v or "").strip()
def _slug(v:str)->str: return re.sub(r"[^A-Za-z0-9_.-]+","-",v).strip("-")[:180] or "unknown"

def blueprint_identity(r:Mapping[str,Any])->dict[str,Any]:
 return {"contract_id":r.get("contract_id"),"contract_sha256":r.get("contract_sha256"),"method_design_sha256":r.get("method_design_sha256"),"method_review_sha256":r.get("method_review_sha256"),"blueprint_spec_sha256":r.get("blueprint_spec_sha256"),"status":r.get("status")}

def build_reopen_experiment_blueprint(*,contract:Mapping[str,Any],method_design:Mapping[str,Any],method_review:Mapping[str,Any],blueprint_spec:Mapping[str,Any])->dict[str,Any]:
 if not validate_reopened_scientific_contract(contract): raise RuntimeError("valid reopened scientific contract required")
 if not validate_reopen_method_design(method_design): raise RuntimeError("valid frozen method design required")
 if not validate_reopen_method_review(method_review) or method_review.get("status")!=METHOD_REVIEW_PASS: raise RuntimeError("independent method review PASS required before experiment blueprint")
 if _text(method_design.get("contract_sha256"))!=_text(contract.get("contract_sha256")) or _text(method_review.get("method_design_sha256"))!=_text(method_design.get("method_design_sha256")): raise RuntimeError("blueprint method/contract lineage mismatch")
 spec=dict(blueprint_spec) if isinstance(blueprint_spec,Mapping) else {}; missing=[f for f in REQUIRED_FIELDS if not spec.get(f)]
 if missing: raise RuntimeError("blueprint fields missing: "+",".join(missing))
 if spec.get("selection_before_outcome") is not True or spec.get("core_method_frozen") is not True: raise RuntimeError("blueprint must freeze outcome-independent selection and core method")
 arms=spec.get("arms") or []; metrics=spec.get("metrics") or []; baselines=spec.get("same_information_baselines") or []
 if not isinstance(arms,list) or len(arms)<2: raise RuntimeError("blueprint requires at least two arms")
 if not isinstance(metrics,list) or not metrics: raise RuntimeError("blueprint requires metrics")
 if not isinstance(baselines,list) or len(baselines)<2: raise RuntimeError("blueprint requires at least two same-information baselines")
 sample=spec.get("sample_plan") or {}; stats=spec.get("statistical_plan") or {}; budget=spec.get("budget") or {}
 if not isinstance(sample,Mapping) or any(int(sample.get(k) or 0)<=0 for k in ("requested_units","minimum_qualified_units","replicates_per_arm")): raise RuntimeError("blueprint sample plan must be positive and explicit")
 if int(sample.get("minimum_qualified_units"))>int(sample.get("requested_units")): raise RuntimeError("minimum qualified units cannot exceed requested units")
 if not isinstance(stats,Mapping) or not _text(stats.get("estimator")) or not _text(stats.get("test")) or float(stats.get("alpha") or 0)<=0 or float(stats.get("alpha") or 0)>=1: raise RuntimeError("blueprint statistical plan is incomplete")
 method_budget=(method_design.get("method_spec") or {}).get("resource_budget") or {}
 for k in ("max_provider_calls","max_gpu_hours"):
  if float(budget.get(k) or 0)<=0 or float(budget.get(k) or 0)>float(method_budget.get(k) or 0): raise RuntimeError(f"blueprint budget exceeds frozen method cap:{k}")
 if int(sample.get("requested_units"))>int(method_budget.get("max_local_units") or 0): raise RuntimeError("blueprint requested units exceed frozen method cap")
 rules=spec.get("go_stop_rules") or []
 if not isinstance(rules,list) or len(rules)<2: raise RuntimeError("blueprint requires explicit GO/STOP rules")
 normalized={k:spec[k] for k in REQUIRED_FIELDS}; normalized.update({"selection_before_outcome":True,"core_method_frozen":True,"phase":"LOCAL_F0_ONLY","pre_experiment_compiler_target":True})
 row={"schema_version":SCHEMA_VERSION,"receipt_type":"reopen-experiment-blueprint","contract_id":_text(contract.get("contract_id")),"contract_sha256":_text(contract.get("contract_sha256")),"method_design_sha256":_text(method_design.get("method_design_sha256")),"method_review_sha256":_text(method_review.get("method_review_sha256")),"blueprint_spec":normalized,"blueprint_spec_sha256":_digest(normalized),"status":BLUEPRINT_STATUS,"blueprint_frozen":True,"local_validation_authorization_review_eligible":False,"pre_experiment_compiler_input_eligible":False,"execution_authorized":False,**{f"{k}_authority":False for k in ("scientific","method","experiment_blueprint","local_validation","experiment","p0","gpu","submission")}}
 row["blueprint_sha256"]=_digest(blueprint_identity(row)); return row

def validate_reopen_experiment_blueprint(r:Mapping[str,Any])->bool:
 if r.get("receipt_type")!="reopen-experiment-blueprint" or r.get("status")!=BLUEPRINT_STATUS or r.get("blueprint_frozen") is not True:return False
 spec=r.get("blueprint_spec") or {}
 if not isinstance(spec,Mapping) or any(not spec.get(k) for k in REQUIRED_FIELDS) or r.get("blueprint_spec_sha256")!=_digest(dict(spec)):return False
 if r.get("local_validation_authorization_review_eligible") is not False or r.get("pre_experiment_compiler_input_eligible") is not False or r.get("execution_authorized") is not False:return False
 if any(r.get(f"{k}_authority") is not False for k in ("scientific","method","experiment_blueprint","local_validation","experiment","p0","gpu","submission")):return False
 return r.get("blueprint_sha256")==_digest(blueprint_identity(r))

def review_identity(r:Mapping[str,Any])->dict[str,Any]:
 return {"contract_id":r.get("contract_id"),"contract_sha256":r.get("contract_sha256"),"blueprint_sha256":r.get("blueprint_sha256"),"reviewer_ref_sha256":r.get("reviewer_ref_sha256"),"reviewed_at":r.get("reviewed_at"),"checks":r.get("checks") or {},"failed_checks":r.get("failed_checks") or [],"status":r.get("status"),"local_validation_authorization_review_eligible":r.get("local_validation_authorization_review_eligible")}

def build_reopen_blueprint_review(*,blueprint:Mapping[str,Any],review_packet:Mapping[str,Any])->dict[str,Any]:
 if not validate_reopen_experiment_blueprint(blueprint): raise RuntimeError("valid frozen experiment blueprint required")
 p=dict(review_packet) if isinstance(review_packet,Mapping) else {}
 if _text(p.get("reviewer_role"))!=REVIEWER_ROLE: raise RuntimeError(f"reviewer_role must be {REVIEWER_ROLE}")
 ref=_text(p.get("reviewer_ref")); at=_text(p.get("reviewed_at")); checks0=p.get("checks") or {}
 if not ref or not at: raise RuntimeError("independent blueprint reviewer reference and timestamp required")
 if not isinstance(checks0,Mapping) or set(checks0.keys())!=set(REVIEW_CHECKS): raise RuntimeError("blueprint review checks must match required set exactly")
 checks={k:checks0.get(k) is True for k in REVIEW_CHECKS}; failed=[k for k in REVIEW_CHECKS if not checks[k]]; passed=not failed
 if not _text(p.get("risk_analysis")) or not _text(p.get("failure_if_blocked")): raise RuntimeError("blueprint review risk_analysis and failure_if_blocked required")
 row={"schema_version":SCHEMA_VERSION,"receipt_type":"reopen-blueprint-review","contract_id":_text(blueprint.get("contract_id")),"contract_sha256":_text(blueprint.get("contract_sha256")),"blueprint_sha256":_text(blueprint.get("blueprint_sha256")),"reviewer_role":REVIEWER_ROLE,"reviewer_ref":ref,"reviewer_ref_sha256":hashlib.sha256(ref.encode()).hexdigest(),"reviewed_at":at,"checks":checks,"failed_checks":failed,"risk_analysis_sha256":hashlib.sha256(_text(p.get("risk_analysis")).encode()).hexdigest(),"failure_if_blocked_sha256":hashlib.sha256(_text(p.get("failure_if_blocked")).encode()).hexdigest(),"status":REVIEW_PASS if passed else REVIEW_BLOCK,"pass":passed,"local_validation_authorization_review_eligible":passed,"pre_experiment_compiler_input_eligible":passed,"execution_authorized":False,"review_pass_does_not_authorize_local_validation":True,**{f"{k}_authority":False for k in ("scientific","method","experiment_blueprint","local_validation","experiment","p0","gpu","submission")}}
 row["blueprint_review_sha256"]=_digest(review_identity(row)); return row

def validate_reopen_blueprint_review(r:Mapping[str,Any])->bool:
 if r.get("receipt_type")!="reopen-blueprint-review" or r.get("status") not in {REVIEW_PASS,REVIEW_BLOCK}:return False
 checks=r.get("checks") or {}; failed=[k for k in REVIEW_CHECKS if checks.get(k) is not True] if isinstance(checks,Mapping) else ["invalid"]
 if set(checks.keys())!=set(REVIEW_CHECKS) or list(r.get("failed_checks") or [])!=failed:return False
 passed=not failed
 if r.get("pass") is not passed or r.get("status")!=(REVIEW_PASS if passed else REVIEW_BLOCK):return False
 if r.get("local_validation_authorization_review_eligible") is not passed or r.get("pre_experiment_compiler_input_eligible") is not passed or r.get("execution_authorized") is not False:return False
 ref=_text(r.get("reviewer_ref"));
 if not ref or hashlib.sha256(ref.encode()).hexdigest()!=_text(r.get("reviewer_ref_sha256")):return False
 if r.get("review_pass_does_not_authorize_local_validation") is not True:return False
 if any(r.get(f"{k}_authority") is not False for k in ("scientific","method","experiment_blueprint","local_validation","experiment","p0","gpu","submission")):return False
 return r.get("blueprint_review_sha256")==_digest(review_identity(r))

def _directory(root:Path)->Path:
 root=Path(root); return root if root.name=="scientific-contract-experiment-blueprints" else root/"scientific-contract-experiment-blueprints"
def _sha(r:Mapping[str,Any])->str:
 return _text(r.get("blueprint_sha256")) if r.get("receipt_type")=="reopen-experiment-blueprint" else _text(r.get("blueprint_review_sha256"))
def publish_reopen_blueprint_receipt(root:Path,receipt:Mapping[str,Any])->dict[str,Any]:
 valid=validate_reopen_experiment_blueprint(receipt) if receipt.get("receipt_type")=="reopen-experiment-blueprint" else validate_reopen_blueprint_review(receipt)
 if not valid: raise RuntimeError("invalid reopen blueprint receipt")
 d=_directory(root); d.mkdir(parents=True,exist_ok=True); cid=_text(receipt.get("contract_id")); path=d/f"{_slug(cid)}.json"; lock=d/f".{_slug(cid)}.lock"
 with lock.open("a+",encoding="utf-8") as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX); ledger=json.loads(path.read_text()) if path.exists() else {"schema_version":SCHEMA_VERSION,"contract_id":cid,"contract_sha256":_text(receipt.get("contract_sha256")),"events":[],"authority":dict(ZERO_AUTHORITY)}
  if _text(ledger.get("contract_sha256"))!=_text(receipt.get("contract_sha256")):raise RuntimeError("blueprint ledger contract SHA mismatch")
  rs=_sha(receipt)
  for e in ledger.get("events") or []:
   pr=e.get("receipt") or {} if isinstance(e,Mapping) else {}
   if isinstance(pr,Mapping) and _sha(pr)==rs:return ledger
  if receipt.get("receipt_type")=="reopen-blueprint-review":
   bshas={_text((e.get("receipt") or {}).get("blueprint_sha256")) for e in ledger.get("events") or [] if isinstance(e,Mapping) and (e.get("receipt") or {}).get("receipt_type")=="reopen-experiment-blueprint"}
   if _text(receipt.get("blueprint_sha256")) not in bshas:raise RuntimeError("blueprint review requires prior frozen blueprint")
  at=_text(receipt.get("reviewed_at")) or _now(); ev={"event_type":_text(receipt.get("receipt_type")),"receipt":dict(receipt),"recorded_at":at,"execution_authorized":False,"experiment_authority":False,"p0_authority":False,"gpu_authority":False}; ev["event_id"]=_digest([cid,len(ledger.get("events") or []),ev["event_type"],rs,at])[:24]; ledger.setdefault("events",[]).append(ev); ledger["updated_at"]=at
  errs=validate_reopen_blueprint_ledger(ledger)
  if errs:raise RuntimeError(errs)
  tmp=path.with_suffix('.json.tmp'); tmp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'); os.replace(tmp,path); return ledger

def validate_reopen_blueprint_ledger(ledger:Mapping[str,Any])->list[str]:
 errs=[]
 if (ledger.get("authority") or {})!=ZERO_AUTHORITY:errs.append("reopen-blueprint-ledger-authority-leak")
 bshas=set(); seen=set(); cid=_text(ledger.get("contract_id")); csha=_text(ledger.get("contract_sha256"))
 for i,e in enumerate(ledger.get("events") or []):
  if not isinstance(e,Mapping):errs.append("reopen-blueprint-event-not-object");continue
  r=e.get("receipt") or {}; rt=_text(r.get("receipt_type")); rs=_sha(r); valid=validate_reopen_experiment_blueprint(r) if rt=="reopen-experiment-blueprint" else validate_reopen_blueprint_review(r) if rt=="reopen-blueprint-review" else False
  if not valid:errs.append("reopen-blueprint-receipt-invalid");continue
  if _text(r.get("contract_id"))!=cid or _text(r.get("contract_sha256"))!=csha:errs.append("reopen-blueprint-contract-lineage-mismatch")
  if rs in seen:errs.append("reopen-blueprint-duplicate-receipt")
  if rt=="reopen-experiment-blueprint":bshas.add(rs)
  elif _text(r.get("blueprint_sha256")) not in bshas:errs.append("reopen-blueprint-review-missing-prior-blueprint")
  if _text(e.get("event_id"))!=_digest([cid,i,rt,rs,_text(e.get("recorded_at"))])[:24]:errs.append("reopen-blueprint-event-id-invalid")
  if e.get("execution_authorized") is True or e.get("experiment_authority") is True or e.get("p0_authority") is True or e.get("gpu_authority") is True:errs.append("reopen-blueprint-event-authority-leak")
  seen.add(rs)
 return list(dict.fromkeys(errs))

def public_reopen_blueprint_summary(root:Path,contract_id:str)->dict[str,Any]:
 empty={"status":"REOPEN_EXPERIMENT_BLUEPRINT_REQUIRED","contract_id":contract_id,"blueprint_sha256":"","blueprint_review_sha256":"","local_validation_authorization_review_eligible":False,"pre_experiment_compiler_input_eligible":False,"execution_authorized":False,"failed_checks":[],"validation_errors":[],"authority":dict(ZERO_AUTHORITY)}
 path=_directory(root)/f"{_slug(contract_id)}.json"
 if not path.exists():return empty
 try:ledger=json.loads(path.read_text())
 except Exception:return {**empty,"status":"REOPEN_BLUEPRINT_LEDGER_INVALID","validation_errors":["reopen-blueprint-ledger-unreadable"]}
 errs=validate_reopen_blueprint_ledger(ledger)
 if errs:return {**empty,"status":"REOPEN_BLUEPRINT_LEDGER_INVALID","validation_errors":errs}
 bs=[e.get("receipt") or {} for e in ledger.get("events") or [] if isinstance(e,Mapping) and (e.get("receipt") or {}).get("receipt_type")=="reopen-experiment-blueprint"]; rs=[e.get("receipt") or {} for e in ledger.get("events") or [] if isinstance(e,Mapping) and (e.get("receipt") or {}).get("receipt_type")=="reopen-blueprint-review"]; b=bs[-1] if bs else {}; r=rs[-1] if rs else {}; status=_text(r.get("status")) if r else BLUEPRINT_STATUS if b else empty["status"]
 return {**empty,"status":status,"blueprint_sha256":_text(b.get("blueprint_sha256")),"blueprint_review_sha256":_text(r.get("blueprint_review_sha256")),"local_validation_authorization_review_eligible":r.get("local_validation_authorization_review_eligible") is True,"pre_experiment_compiler_input_eligible":r.get("pre_experiment_compiler_input_eligible") is True,"execution_authorized":False,"failed_checks":list(r.get("failed_checks") or []),"reviewer_ref_sha256":_text(r.get("reviewer_ref_sha256"))}
