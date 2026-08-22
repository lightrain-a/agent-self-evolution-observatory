from __future__ import annotations

import fcntl, hashlib, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .reopened_scientific_experiment_blueprint import REVIEW_PASS as BLUEPRINT_REVIEW_PASS, validate_reopen_blueprint_review, validate_reopen_experiment_blueprint

SCHEMA_VERSION="1.0"
STATUS="LOCAL_VALIDATION_AUTHORIZED_PRE_EXPERIMENT_COMPILER_REQUIRED"
AUTHORITY_SCOPE="BOUNDED_LOCAL_F0_PREPARATION_ONLY"
ZERO_AUTHORITY={"scientific":False,"method":False,"experiment_blueprint":False,"experiment":False,"p0":False,"gpu":False,"submission":False}

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _digest(v:Any)->str: return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _text(v:Any)->str: return str(v or "").strip()
def _slug(v:str)->str: return re.sub(r"[^A-Za-z0-9_.-]+","-",v).strip("-")[:180] or "unknown"

def authorization_identity(r:Mapping[str,Any])->dict[str,Any]:
 return {"contract_id":r.get("contract_id"),"contract_sha256":r.get("contract_sha256"),"blueprint_sha256":r.get("blueprint_sha256"),"blueprint_review_sha256":r.get("blueprint_review_sha256"),"external_authority_ref_sha256":r.get("external_authority_ref_sha256"),"authorized_at":r.get("authorized_at"),"authority_scope":r.get("authority_scope"),"authorized_budget":r.get("authorized_budget") or {},"status":r.get("status"),"local_validation_authorized":r.get("local_validation_authorized")}

def build_local_validation_authorization(*,blueprint:Mapping[str,Any],blueprint_review:Mapping[str,Any],external_authority_ref:str,authorized_at:str,authorized_budget:Mapping[str,Any])->dict[str,Any]:
 if not validate_reopen_experiment_blueprint(blueprint): raise RuntimeError("valid frozen experiment blueprint required")
 if not validate_reopen_blueprint_review(blueprint_review) or blueprint_review.get("status")!=BLUEPRINT_REVIEW_PASS: raise RuntimeError("blueprint review PASS required before local-validation authorization")
 if _text(blueprint_review.get("blueprint_sha256"))!=_text(blueprint.get("blueprint_sha256")): raise RuntimeError("local-validation blueprint/review lineage mismatch")
 ref=_text(external_authority_ref); at=_text(authorized_at)
 if not ref or not at: raise RuntimeError("external human/PI authority reference and authorization timestamp required")
 budget=dict(authorized_budget) if isinstance(authorized_budget,Mapping) else {}; frozen=(blueprint.get("blueprint_spec") or {}).get("budget") or {}; sample=(blueprint.get("blueprint_spec") or {}).get("sample_plan") or {}
 for k in ("max_provider_calls","max_gpu_hours"):
  val=float(budget.get(k) or 0); cap=float(frozen.get(k) or 0)
  if val<=0 or val>cap: raise RuntimeError(f"local-validation authorized budget exceeds blueprint cap:{k}")
 units=int(budget.get("max_units") or 0); unit_cap=int(sample.get("requested_units") or 0)
 if units<=0 or units>unit_cap: raise RuntimeError("local-validation authorized max_units exceeds blueprint cap")
 row={"schema_version":SCHEMA_VERSION,"receipt_type":"reopen-local-validation-authorization","contract_id":_text(blueprint.get("contract_id")),"contract_sha256":_text(blueprint.get("contract_sha256")),"blueprint_sha256":_text(blueprint.get("blueprint_sha256")),"blueprint_review_sha256":_text(blueprint_review.get("blueprint_review_sha256")),"external_authority_ref":ref,"external_authority_ref_sha256":hashlib.sha256(ref.encode()).hexdigest(),"authorized_at":at,"authority_scope":AUTHORITY_SCOPE,"authorized_budget":{"max_units":units,"max_provider_calls":int(budget["max_provider_calls"]),"max_gpu_hours":float(budget["max_gpu_hours"])},"status":STATUS,"local_validation_authorized":True,"pre_experiment_compiler_required":True,"pre_experiment_compiler_input_eligible":True,"execution_authorized":False,"experiment_authority_required_after_compiler":True,"single_writer_experiment_lease_required":True,"p0_escalation_requires_separate_authority":True,"full_experiment_authorized":False,**{f"{k}_authority":False for k in ("scientific","method","experiment_blueprint","experiment","p0","gpu","submission")}}
 row["local_validation_authorization_sha256"]=_digest(authorization_identity(row)); return row

def validate_local_validation_authorization(r:Mapping[str,Any])->bool:
 if r.get("receipt_type")!="reopen-local-validation-authorization" or r.get("status")!=STATUS or r.get("authority_scope")!=AUTHORITY_SCOPE:return False
 ref=_text(r.get("external_authority_ref"))
 if not ref or hashlib.sha256(ref.encode()).hexdigest()!=_text(r.get("external_authority_ref_sha256")):return False
 b=r.get("authorized_budget") or {}
 if not isinstance(b,Mapping) or int(b.get("max_units") or 0)<=0 or int(b.get("max_provider_calls") or 0)<=0 or float(b.get("max_gpu_hours") or 0)<=0:return False
 if r.get("local_validation_authorized") is not True or r.get("pre_experiment_compiler_required") is not True or r.get("pre_experiment_compiler_input_eligible") is not True:return False
 if r.get("execution_authorized") is not False or r.get("experiment_authority_required_after_compiler") is not True or r.get("single_writer_experiment_lease_required") is not True:return False
 if r.get("p0_escalation_requires_separate_authority") is not True or r.get("full_experiment_authorized") is not False:return False
 if any(r.get(f"{k}_authority") is not False for k in ("scientific","method","experiment_blueprint","experiment","p0","gpu","submission")):return False
 return r.get("local_validation_authorization_sha256")==_digest(authorization_identity(r))

def _directory(root:Path)->Path:
 root=Path(root); return root if root.name=="scientific-contract-local-validation-authority" else root/"scientific-contract-local-validation-authority"
def publish_local_validation_authorization(root:Path,receipt:Mapping[str,Any])->dict[str,Any]:
 if not validate_local_validation_authorization(receipt): raise RuntimeError("invalid local-validation authorization receipt")
 d=_directory(root); d.mkdir(parents=True,exist_ok=True); cid=_text(receipt.get("contract_id")); path=d/f"{_slug(cid)}.json"; lock=d/f".{_slug(cid)}.lock"
 with lock.open("a+",encoding="utf-8") as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX); ledger=json.loads(path.read_text()) if path.exists() else {"schema_version":SCHEMA_VERSION,"contract_id":cid,"contract_sha256":_text(receipt.get("contract_sha256")),"events":[],"authority":{"local_validation":False,**ZERO_AUTHORITY}}
  if _text(ledger.get("contract_sha256"))!=_text(receipt.get("contract_sha256")): raise RuntimeError("local-validation authority ledger contract SHA mismatch")
  sha=_text(receipt.get("local_validation_authorization_sha256"))
  for e in ledger.get("events") or []:
   pr=e.get("receipt") or {} if isinstance(e,Mapping) else {}
   if isinstance(pr,Mapping) and _text(pr.get("local_validation_authorization_sha256"))==sha:return ledger
  at=_text(receipt.get("authorized_at")); ev={"event_type":"reopen-local-validation-authorization","receipt":dict(receipt),"recorded_at":at,"local_validation_authority":False,"execution_authorized":False,"experiment_authority":False,"p0_authority":False,"gpu_authority":False}; ev["event_id"]=_digest([cid,len(ledger.get("events") or []),sha,at])[:24]; ledger.setdefault("events",[]).append(ev); ledger["updated_at"]=at
  errs=validate_local_validation_authority_ledger(ledger)
  if errs: raise RuntimeError(errs)
  tmp=path.with_suffix('.json.tmp'); tmp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'); os.replace(tmp,path); return ledger

def validate_local_validation_authority_ledger(ledger:Mapping[str,Any])->list[str]:
 errs=[]
 expected={"local_validation":False,**ZERO_AUTHORITY}
 if (ledger.get("authority") or {})!=expected:errs.append("local-validation-authority-ledger-must-not-own-execution-authority")
 cid=_text(ledger.get("contract_id")); csha=_text(ledger.get("contract_sha256")); seen=set()
 for i,e in enumerate(ledger.get("events") or []):
  if not isinstance(e,Mapping) or e.get("event_type")!="reopen-local-validation-authorization":errs.append("local-validation-authority-event-invalid");continue
  r=e.get("receipt") or {}; sha=_text(r.get("local_validation_authorization_sha256"))
  if not isinstance(r,Mapping) or not validate_local_validation_authorization(r):errs.append("local-validation-authorization-receipt-invalid");continue
  if _text(r.get("contract_id"))!=cid or _text(r.get("contract_sha256"))!=csha:errs.append("local-validation-authority-contract-lineage-mismatch")
  if sha in seen:errs.append("local-validation-authority-duplicate-receipt")
  if _text(e.get("event_id"))!=_digest([cid,i,sha,_text(e.get("recorded_at"))])[:24]:errs.append("local-validation-authority-event-id-invalid")
  if e.get("local_validation_authority") is True or e.get("execution_authorized") is True or e.get("experiment_authority") is True or e.get("p0_authority") is True or e.get("gpu_authority") is True:errs.append("local-validation-authority-event-execution-leak")
  seen.add(sha)
 return list(dict.fromkeys(errs))

def public_local_validation_authorization(root:Path,contract_id:str)->dict[str,Any]:
 empty={"status":"LOCAL_VALIDATION_AUTHORIZATION_REQUIRED","contract_id":contract_id,"authorization_sha256":"","external_authority_ref_sha256":"","authorized_budget":{},"local_validation_authorized":False,"pre_experiment_compiler_required":True,"pre_experiment_compiler_input_eligible":False,"execution_authorized":False,"validation_errors":[],"authority":{"local_validation":False,**ZERO_AUTHORITY}}
 path=_directory(root)/f"{_slug(contract_id)}.json"
 if not path.exists():return empty
 try:ledger=json.loads(path.read_text())
 except Exception:return {**empty,"status":"LOCAL_VALIDATION_AUTHORITY_LEDGER_INVALID","validation_errors":["local-validation-authority-ledger-unreadable"]}
 errs=validate_local_validation_authority_ledger(ledger)
 if errs:return {**empty,"status":"LOCAL_VALIDATION_AUTHORITY_LEDGER_INVALID","validation_errors":errs}
 receipts=[e.get("receipt") or {} for e in ledger.get("events") or [] if isinstance(e,Mapping) and isinstance(e.get("receipt"),Mapping)]; r=receipts[-1] if receipts else {}
 if not r:return empty
 return {**empty,"status":STATUS,"authorization_sha256":_text(r.get("local_validation_authorization_sha256")),"external_authority_ref_sha256":_text(r.get("external_authority_ref_sha256")),"authorized_budget":dict(r.get("authorized_budget") or {}),"local_validation_authorized":True,"pre_experiment_compiler_input_eligible":True,"execution_authorized":False}
