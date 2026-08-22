from __future__ import annotations

import fcntl, hashlib, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .reopened_local_validation_authorization import validate_local_validation_authorization
from .reopened_pre_experiment_adapter import PASS_STATUS as PREEXP_PASS, validate_reopened_pre_experiment

SCHEMA_VERSION="1.0"
STATUS="EXPERIMENT_LEASE_REQUEST_READY_EXPLICIT_ACQUIRE_REQUIRED"
ZERO_AUTHORITY={"scientific":False,"method":False,"local_validation":False,"experiment":False,"p0":False,"gpu":False,"submission":False}

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _digest(v:Any)->str: return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _text(v:Any)->str: return str(v or "").strip()
def _slug(v:str)->str: return re.sub(r"[^A-Za-z0-9_.-]+","-",v).strip("-")[:180] or "unknown"

def request_identity(r:Mapping[str,Any])->dict[str,Any]:
 return {"contract_id":r.get("contract_id"),"contract_sha256":r.get("contract_sha256"),"pre_experiment_adapter_sha256":r.get("pre_experiment_adapter_sha256"),"local_validation_authorization_sha256":r.get("local_validation_authorization_sha256"),"plan_hash":r.get("plan_hash"),"phase":r.get("phase"),"authorized_budget":r.get("authorized_budget") or {},"status":r.get("status")}

def build_experiment_lease_request(*,pre_experiment_receipt:Mapping[str,Any],local_authorization:Mapping[str,Any])->dict[str,Any]:
 if not validate_reopened_pre_experiment(pre_experiment_receipt) or pre_experiment_receipt.get("status")!=PREEXP_PASS or pre_experiment_receipt.get("compiler_execution_ready") is not True: raise RuntimeError("Pre-Experiment compiler PASS required before experiment lease request")
 if not validate_local_validation_authorization(local_authorization): raise RuntimeError("valid local-validation human authorization required")
 if _text(pre_experiment_receipt.get("contract_id"))!=_text(local_authorization.get("contract_id")) or _text(pre_experiment_receipt.get("local_validation_authorization_sha256"))!=_text(local_authorization.get("local_validation_authorization_sha256")): raise RuntimeError("lease request local-authorization lineage mismatch")
 card=pre_experiment_receipt.get("pre_experiment_card") or {}; plan=card.get("research_execution_plan") or {}; plan_hash=_text(plan.get("plan_hash"))
 if not plan_hash: raise RuntimeError("Pre-Experiment compiler did not produce a research execution plan hash")
 budget=dict(local_authorization.get("authorized_budget") or {})
 row={"schema_version":SCHEMA_VERSION,"receipt_type":"reopen-experiment-lease-request","contract_id":_text(pre_experiment_receipt.get("contract_id")),"contract_sha256":_text(pre_experiment_receipt.get("contract_sha256")),"pre_experiment_adapter_sha256":_text(pre_experiment_receipt.get("adapter_receipt_sha256")),"local_validation_authorization_sha256":_text(local_authorization.get("local_validation_authorization_sha256")),"plan_hash":plan_hash,"phase":"reopen-local-f0","authorized_budget":budget,"status":STATUS,"experiment_authority_acquired":False,"execution_authorized":False,"external_executor_action_required":True,"run_id_assignment_required":True,"actor_identity_required":True,"single_writer_lease_required":True,"governance_stage_recheck_required":True,"lease_must_use_exact_plan_hash":True,"automatic_gpu_allocation_forbidden":True,"automatic_execution_forbidden":True,**{f"{k}_authority":False for k in ("scientific","method","local_validation","experiment","p0","gpu","submission")}}
 row["lease_request_sha256"]=_digest(request_identity(row)); return row

def validate_experiment_lease_request(r:Mapping[str,Any])->bool:
 if r.get("receipt_type")!="reopen-experiment-lease-request" or r.get("status")!=STATUS:return False
 if not _text(r.get("plan_hash")) or not _text(r.get("pre_experiment_adapter_sha256")) or not _text(r.get("local_validation_authorization_sha256")):return False
 if r.get("experiment_authority_acquired") is not False or r.get("execution_authorized") is not False:return False
 for key in ("external_executor_action_required","run_id_assignment_required","actor_identity_required","single_writer_lease_required","governance_stage_recheck_required","lease_must_use_exact_plan_hash","automatic_gpu_allocation_forbidden","automatic_execution_forbidden"):
  if r.get(key) is not True:return False
 if any(r.get(f"{k}_authority") is not False for k in ("scientific","method","local_validation","experiment","p0","gpu","submission")):return False
 return r.get("lease_request_sha256")==_digest(request_identity(r))

def _directory(root:Path)->Path:
 root=Path(root);return root if root.name=="scientific-contract-experiment-lease-requests" else root/"scientific-contract-experiment-lease-requests"
def publish_experiment_lease_request(root:Path,receipt:Mapping[str,Any])->dict[str,Any]:
 if not validate_experiment_lease_request(receipt):raise RuntimeError("invalid experiment lease request")
 d=_directory(root);d.mkdir(parents=True,exist_ok=True);cid=_text(receipt.get("contract_id"));path=d/f"{_slug(cid)}.json";lock=d/f".{_slug(cid)}.lock"
 with lock.open("a+",encoding="utf-8") as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX);ledger=json.loads(path.read_text()) if path.exists() else {"schema_version":SCHEMA_VERSION,"contract_id":cid,"contract_sha256":_text(receipt.get("contract_sha256")),"events":[],"authority":dict(ZERO_AUTHORITY)}
  sha=_text(receipt.get("lease_request_sha256"))
  for e in ledger.get("events") or []:
   pr=e.get("receipt") or {} if isinstance(e,Mapping) else {}
   if isinstance(pr,Mapping) and _text(pr.get("lease_request_sha256"))==sha:return ledger
  at=_now();ev={"event_type":"reopen-experiment-lease-request","receipt":dict(receipt),"recorded_at":at,"execution_authorized":False,"experiment_authority":False,"gpu_authority":False};ev["event_id"]=_digest([cid,len(ledger.get("events") or []),sha,at])[:24];ledger.setdefault("events",[]).append(ev);ledger["updated_at"]=at
  tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path);return ledger

def public_experiment_lease_request(root:Path,contract_id:str)->dict[str,Any]:
 empty={"status":"EXPERIMENT_LEASE_REQUEST_REQUIRED","contract_id":contract_id,"lease_request_sha256":"","plan_hash":"","authorized_budget":{},"experiment_authority_acquired":False,"execution_authorized":False,"single_writer_lease_required":True,"authority":dict(ZERO_AUTHORITY)}
 path=_directory(root)/f"{_slug(contract_id)}.json"
 if not path.exists():return empty
 try:ledger=json.loads(path.read_text())
 except Exception:return {**empty,"status":"EXPERIMENT_LEASE_REQUEST_LEDGER_INVALID"}
 rs=[e.get("receipt") or {} for e in ledger.get("events") or [] if isinstance(e,Mapping) and isinstance(e.get("receipt"),Mapping)];r=rs[-1] if rs else {}
 if not r or not validate_experiment_lease_request(r):return {**empty,"status":"EXPERIMENT_LEASE_REQUEST_LEDGER_INVALID"}
 return {**empty,"status":STATUS,"lease_request_sha256":_text(r.get("lease_request_sha256")),"plan_hash":_text(r.get("plan_hash")),"authorized_budget":dict(r.get("authorized_budget") or {}),"experiment_authority_acquired":False,"execution_authorized":False,"single_writer_lease_required":True}
