from __future__ import annotations

import fcntl, hashlib, json, os, re
from pathlib import Path
from typing import Any, Mapping

from .reopened_local_f0_completion import SIGNAL, validate_adjudication
from .reopened_scientific_experiment_blueprint import validate_reopen_experiment_blueprint, validate_reopen_blueprint_review

SCHEMA_VERSION="1.0"
STATUS="P0_LIFECYCLE_AUTHORIZED_CONFIRMATORY_PLAN_REQUIRED"
ZERO_AUTHORITY={"scientific":False,"experiment":False,"gpu":False,"submission":False}

def _text(v:Any)->str:return str(v or "").strip()
def _digest(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _slug(v:str)->str:return re.sub(r"[^A-Za-z0-9_.-]+","-",v).strip("-")[:180] or "unknown"
def identity(r:Mapping[str,Any])->dict[str,Any]:
 return {k:r.get(k) for k in ("contract_id","contract_sha256","evidence_adjudication_sha256","blueprint_sha256","blueprint_review_sha256","external_authority_ref_sha256","authorized_at","p0_budget","status")}

def build_p0_authorization(*,adjudication:Mapping[str,Any],blueprint:Mapping[str,Any],blueprint_review:Mapping[str,Any],external_authority_ref:str,authorized_at:str,p0_budget:Mapping[str,Any])->dict[str,Any]:
 if not validate_adjudication(adjudication) or adjudication.get("status")!=SIGNAL:raise RuntimeError("valid local-F0 screening signal adjudication required for P0 authorization review")
 if not validate_reopen_experiment_blueprint(blueprint) or not validate_reopen_blueprint_review(blueprint_review):raise RuntimeError("valid blueprint/review required")
 if _text(adjudication.get("blueprint_sha256"))!=_text(blueprint.get("blueprint_sha256")) or _text(adjudication.get("blueprint_review_sha256"))!=_text(blueprint_review.get("blueprint_review_sha256")):raise RuntimeError("P0 authorization blueprint lineage mismatch")
 ref=_text(external_authority_ref); at=_text(authorized_at)
 if not ref or not at:raise RuntimeError("external P0 scientific authority reference and timestamp required")
 budget=dict(p0_budget or {}); units=int(budget.get("max_units") or 0); calls=int(budget.get("max_provider_calls") or 0); gpu=float(budget.get("max_gpu_hours") or 0)
 if units<=0 or calls<=0 or gpu<0:raise RuntimeError("positive P0 units/provider-call budget and nonnegative GPU-hour cap required")
 local=(blueprint.get("blueprint_spec") or {}).get("sample_plan") or {}; local_units=int(local.get("requested_units") or 0)
 if units<max(1,local_units):raise RuntimeError("P0 max_units must not be smaller than frozen local-F0 requested units")
 r={"schema_version":SCHEMA_VERSION,"receipt_type":"reopen-p0-lifecycle-authorization","contract_id":_text(adjudication.get("contract_id")),"contract_sha256":_text(adjudication.get("contract_sha256")),"evidence_adjudication_sha256":_text(adjudication.get("evidence_adjudication_sha256")),"blueprint_sha256":_text(blueprint.get("blueprint_sha256")),"blueprint_review_sha256":_text(blueprint_review.get("blueprint_review_sha256")),"external_authority_ref":ref,"external_authority_ref_sha256":hashlib.sha256(ref.encode()).hexdigest(),"authorized_at":at,"p0_budget":{"max_units":units,"max_provider_calls":calls,"max_gpu_hours":gpu},"status":STATUS,"p0_lifecycle_authorized":True,"confirmatory_p0_plan_required":True,"fresh_pre_experiment_compiler_required":True,"fresh_experiment_lease_required":True,"local_f0_lease_reuse_forbidden":True,"local_f0_run_reuse_forbidden":True,"p0_execution_authorized":False,"claim_update_authorized":False,"method_verdict_authorized":False,"full_experiment_authorized":False,"scientific_authority":False,"experiment_authority":False,"gpu_authority":False,"submission_authority":False}
 r["p0_authorization_sha256"]=_digest(identity(r))
 if not validate_p0_authorization(r):raise RuntimeError("generated P0 authorization receipt invalid")
 return r

def validate_p0_authorization(r:Mapping[str,Any])->bool:
 if r.get("receipt_type")!="reopen-p0-lifecycle-authorization" or r.get("status")!=STATUS:return False
 ref=_text(r.get("external_authority_ref"))
 if not ref or hashlib.sha256(ref.encode()).hexdigest()!=_text(r.get("external_authority_ref_sha256")):return False
 if r.get("p0_lifecycle_authorized") is not True or r.get("confirmatory_p0_plan_required") is not True or r.get("fresh_pre_experiment_compiler_required") is not True or r.get("fresh_experiment_lease_required") is not True:return False
 if r.get("local_f0_lease_reuse_forbidden") is not True or r.get("local_f0_run_reuse_forbidden") is not True:return False
 if any(r.get(k) is not False for k in ("p0_execution_authorized","claim_update_authorized","method_verdict_authorized","full_experiment_authorized","scientific_authority","experiment_authority","gpu_authority","submission_authority")):return False
 b=r.get("p0_budget") or {}
 if int(b.get("max_units") or 0)<=0 or int(b.get("max_provider_calls") or 0)<=0 or float(b.get("max_gpu_hours") or 0)<0:return False
 return _text(r.get("p0_authorization_sha256"))==_digest(identity(r))

def _dir(root:Path)->Path:
 root=Path(root);return root if root.name=="scientific-contract-p0-authority" else root/"scientific-contract-p0-authority"
def validate_p0_authority_ledger(row:Mapping[str,Any])->list[str]:
 errs=[];seen=set();cid=_text(row.get("contract_id"));csha=_text(row.get("contract_sha256"))
 if (row.get("authority") or {})!=ZERO_AUTHORITY:errs.append("p0-authority-ledger-execution-authority-leak")
 for i,e in enumerate(row.get("events") or []):
  r=e.get("receipt") or {} if isinstance(e,Mapping) else {}
  if not isinstance(r,Mapping) or not validate_p0_authorization(r):errs.append("p0-authority-receipt-invalid");continue
  if _text(r.get("contract_id"))!=cid or _text(r.get("contract_sha256"))!=csha:errs.append("p0-authority-contract-lineage-mismatch")
  sha=_text(r.get("p0_authorization_sha256"));
  if sha in seen:errs.append("p0-authority-duplicate-receipt")
  if _text(e.get("event_id"))!=_digest([cid,i,sha,_text(e.get("recorded_at"))])[:24]:errs.append("p0-authority-event-id-invalid")
  seen.add(sha)
 return list(dict.fromkeys(errs))
def publish_p0_authorization(root:Path,r:Mapping[str,Any])->dict[str,Any]:
 if not validate_p0_authorization(r):raise RuntimeError("invalid P0 authorization receipt")
 d=_dir(root);d.mkdir(parents=True,exist_ok=True);cid=_text(r.get("contract_id"));path=d/f"{_slug(cid)}.json";lock=d/f".{_slug(cid)}.lock"
 with lock.open("a+") as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX);row=json.loads(path.read_text()) if path.exists() else {"schema_version":SCHEMA_VERSION,"contract_id":cid,"contract_sha256":_text(r.get("contract_sha256")),"events":[],"authority":dict(ZERO_AUTHORITY)};sha=_text(r.get("p0_authorization_sha256"))
  for e in row.get("events") or []:
   p=e.get("receipt") or {} if isinstance(e,Mapping) else {}
   if isinstance(p,Mapping) and _text(p.get("p0_authorization_sha256"))==sha:return row
  at=_text(r.get("authorized_at"));ev={"event_type":"reopen-p0-lifecycle-authorization","receipt":dict(r),"recorded_at":at,"p0_execution_authorized":False,"experiment_authority":False,"gpu_authority":False};ev["event_id"]=_digest([cid,len(row.get("events") or []),sha,at])[:24];row.setdefault("events",[]).append(ev);row["updated_at"]=at
  errs=validate_p0_authority_ledger(row)
  if errs:raise RuntimeError(errs)
  tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path);return row

def public_p0_authorization(root:Path,contract_id:str)->dict[str,Any]:
 empty={"status":"P0_AUTHORIZATION_REVIEW_REQUIRED","p0_authorization_sha256":"","p0_lifecycle_authorized":False,"p0_budget":{},"p0_execution_authorized":False,"authority":dict(ZERO_AUTHORITY)};path=_dir(root)/f"{_slug(contract_id)}.json"
 if not path.exists():return empty
 try:row=json.loads(path.read_text())
 except Exception:return {**empty,"status":"P0_AUTHORITY_LEDGER_INVALID"}
 if validate_p0_authority_ledger(row):return {**empty,"status":"P0_AUTHORITY_LEDGER_INVALID"}
 rs=[e.get("receipt") or {} for e in row.get("events") or [] if isinstance(e,Mapping) and isinstance(e.get("receipt"),Mapping)];r=rs[-1] if rs else {}
 if not r or not validate_p0_authorization(r):return {**empty,"status":"P0_AUTHORITY_LEDGER_INVALID"}
 return {**empty,"status":STATUS,"p0_authorization_sha256":_text(r.get("p0_authorization_sha256")),"p0_lifecycle_authorized":True,"p0_budget":dict(r.get("p0_budget") or {}),"p0_execution_authorized":False,"external_authority_ref_sha256":_text(r.get("external_authority_ref_sha256"))}
