from __future__ import annotations

import fcntl, hashlib, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .experiment_authority import acquire_authority, validate_authority
from .governance_protocol import evaluate_stage_contract
from .reopened_experiment_lease_request import STATUS as REQUEST_READY, validate_experiment_lease_request
from .reopened_local_validation_authorization import validate_local_validation_authorization
from .reopened_pre_experiment_adapter import build_adapter_config, validate_reopened_pre_experiment
from .reopened_scientific_contract import validate_reopened_scientific_contract
from .reopened_scientific_experiment_blueprint import validate_reopen_blueprint_review, validate_reopen_experiment_blueprint

SCHEMA_VERSION="1.0"
ACTIVE_STATUS="EXPERIMENT_LEASE_ACTIVE_RUN_NOT_STARTED"
ZERO_DOWNSTREAM={"scientific":False,"p0":False,"gpu":False,"submission":False}

def _now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _digest(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _text(v:Any)->str:return str(v or "").strip()
def _slug(v:str)->str:return re.sub(r"[^A-Za-z0-9_.-]+","-",v).strip("-")[:180] or "unknown"

def acquisition_identity(r:Mapping[str,Any])->dict[str,Any]:
 return {"contract_id":r.get("contract_id"),"contract_sha256":r.get("contract_sha256"),"lease_request_sha256":r.get("lease_request_sha256"),"plan_hash":r.get("plan_hash"),"run_id":r.get("run_id"),"actor":r.get("actor"),"external_execution_authority_ref_sha256":r.get("external_execution_authority_ref_sha256"),"governance_digest":r.get("governance_digest"),"experiment_authority_id":r.get("experiment_authority_id"),"authority_epoch":r.get("authority_epoch"),"acquired_at":r.get("acquired_at"),"status":r.get("status")}

def acquire_reopened_experiment_lease(*,root:Path,contract:Mapping[str,Any],blueprint:Mapping[str,Any],blueprint_review:Mapping[str,Any],local_authorization:Mapping[str,Any],pre_experiment_receipt:Mapping[str,Any],lease_request:Mapping[str,Any],runtime_supplement:Mapping[str,Any],actor:str,run_id:str,external_execution_authority_ref:str)->dict[str,Any]:
 if not validate_reopened_scientific_contract(contract):raise RuntimeError("valid reopened scientific contract required")
 if not validate_reopen_experiment_blueprint(blueprint) or not validate_reopen_blueprint_review(blueprint_review):raise RuntimeError("valid blueprint lineage required")
 if not validate_local_validation_authorization(local_authorization):raise RuntimeError("valid local-validation human authority required")
 if not validate_reopened_pre_experiment(pre_experiment_receipt) or pre_experiment_receipt.get("status")!="PRE_EXPERIMENT_COMPILER_PASS_EXPERIMENT_LEASE_REQUIRED":raise RuntimeError("Pre-Experiment compiler PASS required before lease acquisition")
 if not validate_experiment_lease_request(lease_request) or lease_request.get("status")!=REQUEST_READY:raise RuntimeError("valid experiment lease request required")
 actor=_text(actor);run_id=_text(run_id);ext=_text(external_execution_authority_ref)
 if not actor or not run_id or not ext:raise RuntimeError("actor, run_id, and external execution-authority reference are required")
 if _text(lease_request.get("contract_id"))!=_text(contract.get("contract_id")) or _text(lease_request.get("pre_experiment_adapter_sha256"))!=_text(pre_experiment_receipt.get("adapter_receipt_sha256")):raise RuntimeError("lease request/pre-experiment lineage mismatch")
 config=build_adapter_config(contract=contract,blueprint=blueprint,blueprint_review=blueprint_review,local_authorization=local_authorization,runtime_supplement=runtime_supplement)
 if _digest(config)!=_text(pre_experiment_receipt.get("config_sha256")):raise RuntimeError("runtime supplement/config drift since Pre-Experiment compilation")
 governance=evaluate_stage_contract(_text(contract.get("contract_id")),config,Path(root))
 if governance.get("execution_authorized") is not True:raise RuntimeError("Research OS governance stage blocks experiment lease acquisition: "+",".join(str(x) for x in governance.get("blockers") or []))
 plan_hash=_text(lease_request.get("plan_hash"))
 authority=acquire_authority(Path(root),_text(contract.get("contract_id")),plan_hash,actor,"reopen-local-f0",run_id)
 row={"schema_version":SCHEMA_VERSION,"receipt_type":"reopen-experiment-lease-acquisition","contract_id":_text(contract.get("contract_id")),"contract_sha256":_text(contract.get("contract_sha256")),"lease_request_sha256":_text(lease_request.get("lease_request_sha256")),"plan_hash":plan_hash,"run_id":run_id,"actor":actor,"external_execution_authority_ref":ext,"external_execution_authority_ref_sha256":hashlib.sha256(ext.encode()).hexdigest(),"governance_digest":_digest(governance),"governance_stage":_text(governance.get("stage")),"experiment_authority_id":_text(authority.get("authority_id")),"authority_epoch":int(authority.get("authority_epoch") or 0),"acquired_at":_text(authority.get("acquired_at")),"status":ACTIVE_STATUS,"experiment_authority_acquired":True,"execution_authorized":True,"execution_started":False,"model_loaded":False,"gpu_allocated":False,"resource_lease_required_if_gpu":True,"explicit_run_start_required":True,"automatic_run_start_forbidden":True,"automatic_gpu_allocation_forbidden":True,"scientific_authority":False,"p0_authority":False,"gpu_authority":False,"submission_authority":False}
 row["lease_acquisition_sha256"]=_digest(acquisition_identity(row));return row

def validate_reopened_experiment_lease(r:Mapping[str,Any])->bool:
 if r.get("receipt_type")!="reopen-experiment-lease-acquisition" or r.get("status")!=ACTIVE_STATUS:return False
 if r.get("experiment_authority_acquired") is not True or r.get("execution_authorized") is not True or r.get("execution_started") is not False:return False
 if r.get("model_loaded") is not False or r.get("gpu_allocated") is not False:return False
 if r.get("resource_lease_required_if_gpu") is not True or r.get("explicit_run_start_required") is not True or r.get("automatic_run_start_forbidden") is not True or r.get("automatic_gpu_allocation_forbidden") is not True:return False
 ref=_text(r.get("external_execution_authority_ref"))
 if not ref or hashlib.sha256(ref.encode()).hexdigest()!=_text(r.get("external_execution_authority_ref_sha256")):return False
 if not _text(r.get("experiment_authority_id")) or not _text(r.get("plan_hash")) or not _text(r.get("run_id")) or not _text(r.get("actor")):return False
 if any(r.get(k) is not False for k in ("scientific_authority","p0_authority","gpu_authority","submission_authority")):return False
 return r.get("lease_acquisition_sha256")==_digest(acquisition_identity(r))

def _directory(root:Path)->Path:
 root=Path(root);return root if root.name=="scientific-contract-experiment-leases" else root/"scientific-contract-experiment-leases"

def validate_reopened_experiment_lease_ledger(ledger:Mapping[str,Any])->list[str]:
 errors:list[str]=[];cid=_text(ledger.get("contract_id"));csha=_text(ledger.get("contract_sha256"));seen:set[str]=set()
 if not cid or not csha:errors.append("experiment-lease-ledger-identity-missing")
 authority=ledger.get("authority") or {}
 if authority!={"experiment":False,"gpu":False,"scientific":False,"p0":False,"submission":False}:errors.append("experiment-lease-ledger-authority-leak")
 for idx,event in enumerate(ledger.get("events") or []):
  if not isinstance(event,Mapping) or event.get("event_type")!="reopen-experiment-lease-acquisition":errors.append("experiment-lease-event-invalid");continue
  receipt=event.get("receipt") or {}
  if not isinstance(receipt,Mapping) or not validate_reopened_experiment_lease(receipt):errors.append("experiment-lease-receipt-invalid");continue
  if _text(receipt.get("contract_id"))!=cid or _text(receipt.get("contract_sha256"))!=csha:errors.append("experiment-lease-contract-lineage-mismatch")
  sha=_text(receipt.get("lease_acquisition_sha256"))
  if sha in seen:errors.append("experiment-lease-duplicate-receipt")
  expected=_digest([cid,idx,sha,_text(event.get("recorded_at"))])[:24]
  if _text(event.get("event_id"))!=expected:errors.append("experiment-lease-event-id-invalid")
  if event.get("execution_started") is not False or event.get("gpu_authority") is not False or event.get("scientific_authority") is not False or event.get("p0_authority") is not False:errors.append("experiment-lease-event-authority-leak")
  seen.add(sha)
 return list(dict.fromkeys(errors))

def publish_reopened_experiment_lease(root:Path,receipt:Mapping[str,Any])->dict[str,Any]:
 if not validate_reopened_experiment_lease(receipt):raise RuntimeError("invalid reopened experiment lease receipt")
 d=_directory(root);d.mkdir(parents=True,exist_ok=True);cid=_text(receipt.get("contract_id"));path=d/f"{_slug(cid)}.json";lock=d/f".{_slug(cid)}.lock"
 with lock.open("a+",encoding="utf-8") as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX);ledger=json.loads(path.read_text()) if path.exists() else {"schema_version":SCHEMA_VERSION,"contract_id":cid,"contract_sha256":_text(receipt.get("contract_sha256")),"events":[],"authority":{"experiment":False,"gpu":False,"scientific":False,"p0":False,"submission":False}}
  sha=_text(receipt.get("lease_acquisition_sha256"))
  for e in ledger.get("events") or []:
   pr=e.get("receipt") or {} if isinstance(e,Mapping) else {}
   if isinstance(pr,Mapping) and _text(pr.get("lease_acquisition_sha256"))==sha:return ledger
  at=_text(receipt.get("acquired_at"));ev={"event_type":"reopen-experiment-lease-acquisition","receipt":dict(receipt),"recorded_at":at,"execution_started":False,"gpu_authority":False,"scientific_authority":False,"p0_authority":False};ev["event_id"]=_digest([cid,len(ledger.get("events") or []),sha,at])[:24];ledger.setdefault("events",[]).append(ev);ledger["updated_at"]=at
  errors=validate_reopened_experiment_lease_ledger(ledger)
  if errors:raise RuntimeError(errors)
  tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path);return ledger

def public_reopened_experiment_lease(root:Path,contract_id:str,*,authority_root:Path|None=None)->dict[str,Any]:
 empty={"status":"EXPERIMENT_LEASE_ACQUIRE_REQUIRED","contract_id":contract_id,"lease_acquisition_sha256":"","experiment_authority_id":"","run_id":"","authority_epoch":0,"experiment_authority_acquired":False,"execution_authorized":False,"execution_started":False,"gpu_allocated":False,"authority":{"experiment":False,"gpu":False,"scientific":False,"p0":False,"submission":False}}
 path=_directory(root)/f"{_slug(contract_id)}.json"
 if not path.exists():return empty
 try:ledger=json.loads(path.read_text())
 except Exception:return {**empty,"status":"EXPERIMENT_LEASE_LEDGER_INVALID"}
 if validate_reopened_experiment_lease_ledger(ledger):return {**empty,"status":"EXPERIMENT_LEASE_LEDGER_INVALID"}
 rs=[e.get("receipt") or {} for e in ledger.get("events") or [] if isinstance(e,Mapping) and isinstance(e.get("receipt"),Mapping)];r=rs[-1] if rs else {}
 if not r or not validate_reopened_experiment_lease(r):return {**empty,"status":"EXPERIMENT_LEASE_LEDGER_INVALID"}
 authority_base=Path(authority_root) if authority_root is not None else (Path(root).parent if Path(root).name=="scientific-contract-experiment-leases" else Path(root))
 current=validate_authority(authority_base,contract_id,_text(r.get("experiment_authority_id")),_text(r.get("plan_hash")))
 if current.get("valid") is not True:return {**empty,"status":"EXPERIMENT_LEASE_STALE_OR_RELEASED","lease_acquisition_sha256":_text(r.get("lease_acquisition_sha256")),"experiment_authority_id":_text(r.get("experiment_authority_id")),"run_id":_text(r.get("run_id")),"authority_epoch":int(r.get("authority_epoch") or 0)}
 return {**empty,"status":ACTIVE_STATUS,"lease_acquisition_sha256":_text(r.get("lease_acquisition_sha256")),"experiment_authority_id":_text(r.get("experiment_authority_id")),"run_id":_text(r.get("run_id")),"authority_epoch":int(r.get("authority_epoch") or 0),"experiment_authority_acquired":True,"execution_authorized":True,"execution_started":False,"gpu_allocated":False,"authority":{"experiment":True,"gpu":False,"scientific":False,"p0":False,"submission":False}}
