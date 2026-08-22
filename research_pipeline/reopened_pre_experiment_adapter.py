from __future__ import annotations

import fcntl, hashlib, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .pre_experiment_compiler import compile_pre_experiment_card
from .reopened_local_validation_authorization import STATUS as LOCAL_AUTH_STATUS, validate_local_validation_authorization
from .reopened_scientific_contract import validate_reopened_scientific_contract
from .reopened_scientific_experiment_blueprint import validate_reopen_blueprint_review, validate_reopen_experiment_blueprint

SCHEMA_VERSION="1.0"
PASS_STATUS="PRE_EXPERIMENT_COMPILER_PASS_EXPERIMENT_LEASE_REQUIRED"
BLOCK_STATUS="PRE_EXPERIMENT_COMPILER_BLOCKED"
ZERO_AUTHORITY={"scientific":False,"method":False,"local_validation":False,"experiment":False,"p0":False,"gpu":False,"submission":False}
REQUIRED_RUNTIME_TOP=("models","datasets","seeds","scope","analysis","governance","pre_experiment")
REQUIRED_RUNTIME_PRE=("paper_design","principle_certificate","protocol_validity","updater_competence","parameter_provenance","competence","identifiability","statistics","throughput","recovery","outcomes")

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _digest(v:Any)->str: return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _text(v:Any)->str: return str(v or "").strip()
def _slug(v:str)->str: return re.sub(r"[^A-Za-z0-9_.-]+","-",v).strip("-")[:180] or "unknown"

def latest_receipt(root:Path,contract_id:str,event_type:str)->dict[str,Any]:
 mapping={"blueprint":("scientific-contract-experiment-blueprints","reopen-experiment-blueprint"),"blueprint-review":("scientific-contract-experiment-blueprints","reopen-blueprint-review"),"local-auth":("scientific-contract-local-validation-authority","reopen-local-validation-authorization")}
 d,typ=mapping[event_type]; path=Path(root)/d/f"{_slug(contract_id)}.json"
 if not path.exists(): return {}
 row=json.loads(path.read_text())
 for e in reversed(row.get("events") or []):
  r=e.get("receipt") or {} if isinstance(e,Mapping) else {}
  if isinstance(r,Mapping) and r.get("receipt_type")==typ:return dict(r)
 return {}

def build_adapter_config(*,contract:Mapping[str,Any],blueprint:Mapping[str,Any],blueprint_review:Mapping[str,Any],local_authorization:Mapping[str,Any],runtime_supplement:Mapping[str,Any])->dict[str,Any]:
 if not validate_reopened_scientific_contract(contract): raise RuntimeError("valid reopened scientific contract required")
 if not validate_reopen_experiment_blueprint(blueprint) or not validate_reopen_blueprint_review(blueprint_review): raise RuntimeError("valid frozen blueprint and independent review required")
 if not validate_local_validation_authorization(local_authorization) or local_authorization.get("status")!=LOCAL_AUTH_STATUS: raise RuntimeError("valid local-validation human authorization required")
 if _text(blueprint.get("contract_sha256"))!=_text(contract.get("contract_sha256")) or _text(local_authorization.get("blueprint_sha256"))!=_text(blueprint.get("blueprint_sha256")) or _text(local_authorization.get("blueprint_review_sha256"))!=_text(blueprint_review.get("blueprint_review_sha256")): raise RuntimeError("pre-experiment adapter lineage mismatch")
 runtime=dict(runtime_supplement) if isinstance(runtime_supplement,Mapping) else {}
 missing=[k for k in REQUIRED_RUNTIME_TOP if not runtime.get(k)]
 pre=runtime.get("pre_experiment") or {}; missing.extend(f"pre_experiment.{k}" for k in REQUIRED_RUNTIME_PRE if not pre.get(k))
 if missing: raise RuntimeError("runtime supplement missing: "+",".join(missing))
 if not isinstance(runtime.get("models"),list) or not runtime["models"] or not isinstance(runtime.get("datasets"),list) or not runtime["datasets"] or not isinstance(runtime.get("seeds"),list) or not runtime["seeds"]: raise RuntimeError("runtime models/datasets/seeds must be nonempty lists")
 scope=dict(runtime["scope"]); analysis=dict(runtime["analysis"]); governance=dict(runtime["governance"]); pre=dict(pre)
 spec=blueprint.get("blueprint_spec") or {}; auth_budget=local_authorization.get("authorized_budget") or {}; sample=spec.get("sample_plan") or {}; arms=spec.get("arms") or []
 max_units=int(auth_budget.get("max_units") or 0); reps=int(sample.get("replicates_per_arm") or 0); episode_cap=max_units*reps*len(arms)
 if episode_cap<=0: raise RuntimeError("cannot derive bounded local episode cap")
 declared_worst=int(scope.get("worst_case_environment_episodes") or scope.get("expected_environment_episodes") or 0)
 if declared_worst and declared_worst>episode_cap: raise RuntimeError("runtime supplement worst-case episodes exceed local authorization cap")
 scope.setdefault("expected_environment_episodes",episode_cap); scope.setdefault("worst_case_environment_episodes",episode_cap)
 if not int(scope.get("max_steps") or 0): raise RuntimeError("runtime supplement scope.max_steps required")
 governance={**governance,"scientific_stage":str(governance.get("scientific_stage") or "f0-identifiability")}
 config={
  "schema_version":"2.3",
  "idea_id":_text(contract.get("contract_id")),
  "phase":"P0-screening",
  "governance":governance,
  "models":list(runtime["models"]),"datasets":list(runtime["datasets"]),"seeds":list(runtime["seeds"]),"scope":scope,"analysis":analysis,
  "resource_cap":{"max_gpus":1,"gpu_hours":float(auth_budget["max_gpu_hours"]),"wall_hours":float(runtime.get("wall_hours") or max(1.0,float(auth_budget["max_gpu_hours"])*1.5)),"episodes":episode_cap},
  "pre_experiment":pre,
  "reopen_lineage":{"contract_sha256":_text(contract.get("contract_sha256")),"blueprint_sha256":_text(blueprint.get("blueprint_sha256")),"blueprint_review_sha256":_text(blueprint_review.get("blueprint_review_sha256")),"local_validation_authorization_sha256":_text(local_authorization.get("local_validation_authorization_sha256")),"authorized_max_provider_calls":int(auth_budget["max_provider_calls"]),"selection_before_outcome":True,"core_method_frozen":True,"adapter_cannot_authorize_execution":True},
 }
 return config

def adapter_identity(r:Mapping[str,Any])->dict[str,Any]:
 return {"contract_id":r.get("contract_id"),"contract_sha256":r.get("contract_sha256"),"blueprint_sha256":r.get("blueprint_sha256"),"local_validation_authorization_sha256":r.get("local_validation_authorization_sha256"),"runtime_supplement_sha256":r.get("runtime_supplement_sha256"),"config_sha256":r.get("config_sha256"),"pre_experiment_card_sha256":r.get("pre_experiment_card_sha256"),"compiler_status":r.get("compiler_status"),"passed_gates":r.get("passed_gates"),"gate_count":r.get("gate_count"),"status":r.get("status")}

def compile_reopened_pre_experiment(*,contract:Mapping[str,Any],blueprint:Mapping[str,Any],blueprint_review:Mapping[str,Any],local_authorization:Mapping[str,Any],runtime_supplement:Mapping[str,Any],data_root:Path)->dict[str,Any]:
 config=build_adapter_config(contract=contract,blueprint=blueprint,blueprint_review=blueprint_review,local_authorization=local_authorization,runtime_supplement=runtime_supplement)
 card=compile_pre_experiment_card(_text(contract.get("contract_id")),config,Path(data_root))
 compiler_pass=card.get("execution_authorized") is True
 row={"schema_version":SCHEMA_VERSION,"receipt_type":"reopen-pre-experiment-adapter","contract_id":_text(contract.get("contract_id")),"contract_sha256":_text(contract.get("contract_sha256")),"blueprint_sha256":_text(blueprint.get("blueprint_sha256")),"blueprint_review_sha256":_text(blueprint_review.get("blueprint_review_sha256")),"local_validation_authorization_sha256":_text(local_authorization.get("local_validation_authorization_sha256")),"runtime_supplement_sha256":_digest(dict(runtime_supplement)),"config_sha256":_digest(config),"pre_experiment_card_sha256":_digest(card),"compiler_status":str(card.get("status") or ""),"passed_gates":int(card.get("passed_gates") or 0),"gate_count":int(card.get("gate_count") or 0),"compiler_execution_ready":compiler_pass,"compiler_blockers":[str(x) for x in card.get("blockers") or []],"status":PASS_STATUS if compiler_pass else BLOCK_STATUS,"pre_experiment_card":card,"effective_execution_authorized":False,"experiment_lease_required":True,"governance_stage_recheck_required":True,"automatic_lease_acquisition_forbidden":True,**{f"{k}_authority":False for k in ("scientific","method","local_validation","experiment","p0","gpu","submission")}}
 row["adapter_receipt_sha256"]=_digest(adapter_identity(row));return row

def validate_reopened_pre_experiment(r:Mapping[str,Any])->bool:
 if r.get("receipt_type")!="reopen-pre-experiment-adapter" or r.get("status") not in {PASS_STATUS,BLOCK_STATUS}:return False
 passed=r.get("compiler_execution_ready") is True
 if r.get("status")!=(PASS_STATUS if passed else BLOCK_STATUS):return False
 if int(r.get("gate_count") or 0)!=8 or int(r.get("passed_gates") or 0)<0 or int(r.get("passed_gates") or 0)>8:return False
 if r.get("effective_execution_authorized") is not False or r.get("experiment_lease_required") is not True or r.get("governance_stage_recheck_required") is not True or r.get("automatic_lease_acquisition_forbidden") is not True:return False
 if any(r.get(f"{k}_authority") is not False for k in ("scientific","method","local_validation","experiment","p0","gpu","submission")):return False
 if _text(r.get("pre_experiment_card_sha256"))!=_digest(r.get("pre_experiment_card") or {}):return False
 return r.get("adapter_receipt_sha256")==_digest(adapter_identity(r))

def _directory(root:Path)->Path:
 root=Path(root); return root if root.name=="scientific-contract-pre-experiment" else root/"scientific-contract-pre-experiment"
def publish_reopened_pre_experiment(root:Path,receipt:Mapping[str,Any])->dict[str,Any]:
 if not validate_reopened_pre_experiment(receipt):raise RuntimeError("invalid reopened pre-experiment receipt")
 d=_directory(root);d.mkdir(parents=True,exist_ok=True);cid=_text(receipt.get("contract_id"));path=d/f"{_slug(cid)}.json";lock=d/f".{_slug(cid)}.lock"
 with lock.open("a+",encoding="utf-8") as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX);ledger=json.loads(path.read_text()) if path.exists() else {"schema_version":SCHEMA_VERSION,"contract_id":cid,"contract_sha256":_text(receipt.get("contract_sha256")),"events":[],"authority":dict(ZERO_AUTHORITY)}
  sha=_text(receipt.get("adapter_receipt_sha256"))
  for e in ledger.get("events") or []:
   pr=e.get("receipt") or {} if isinstance(e,Mapping) else {}
   if isinstance(pr,Mapping) and _text(pr.get("adapter_receipt_sha256"))==sha:return ledger
  at=_now();ev={"event_type":"reopen-pre-experiment-adapter","receipt":dict(receipt),"recorded_at":at,"execution_authorized":False,"experiment_authority":False,"gpu_authority":False};ev["event_id"]=_digest([cid,len(ledger.get("events") or []),sha,at])[:24];ledger.setdefault("events",[]).append(ev);ledger["updated_at"]=at
  tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path);return ledger

def public_reopened_pre_experiment(root:Path,contract_id:str)->dict[str,Any]:
 empty={"status":"PRE_EXPERIMENT_COMPILER_REQUIRED","contract_id":contract_id,"adapter_receipt_sha256":"","passed_gates":0,"gate_count":8,"compiler_blocker_count":0,"compiler_execution_ready":False,"effective_execution_authorized":False,"experiment_lease_required":True,"authority":dict(ZERO_AUTHORITY)}
 path=_directory(root)/f"{_slug(contract_id)}.json"
 if not path.exists():return empty
 try:ledger=json.loads(path.read_text())
 except Exception:return {**empty,"status":"PRE_EXPERIMENT_ADAPTER_LEDGER_INVALID"}
 rs=[e.get("receipt") or {} for e in ledger.get("events") or [] if isinstance(e,Mapping) and isinstance(e.get("receipt"),Mapping)];r=rs[-1] if rs else {}
 if not r or not validate_reopened_pre_experiment(r):return {**empty,"status":"PRE_EXPERIMENT_ADAPTER_LEDGER_INVALID"}
 return {**empty,"status":_text(r.get("status")),"adapter_receipt_sha256":_text(r.get("adapter_receipt_sha256")),"passed_gates":int(r.get("passed_gates") or 0),"compiler_blocker_count":len(r.get("compiler_blockers") or []),"compiler_execution_ready":r.get("compiler_execution_ready") is True,"effective_execution_authorized":False,"experiment_lease_required":True}
