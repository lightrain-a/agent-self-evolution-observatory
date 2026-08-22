from __future__ import annotations

import fcntl, hashlib, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .experiment_authority import release_authority, validate_authority
from .pre_experiment_specs import TYPED_OUTCOMES
from .resource_lease import list_gpu_leases, release_gpu_lease
from .reopened_local_f0_run import validate_reopened_local_f0_run_start
from .reopened_local_validation_authorization import validate_local_validation_authorization
from .reopened_scientific_experiment_blueprint import validate_reopen_blueprint_review, validate_reopen_experiment_blueprint

SCHEMA_VERSION="1.0"
COMPLETION_READY="REOPEN_LOCAL_F0_RUN_COMPLETED_AWAIT_EVIDENCE_ADJUDICATION"
COMPLETION_HOLD="REOPEN_LOCAL_F0_RUN_COMPLETED_PROTOCOL_HOLD"
SIGNAL="LOCAL_F0_VALID_SCREENING_SIGNAL_P0_AUTHORIZATION_REVIEW_ELIGIBLE"
NO_SIGNAL="LOCAL_F0_VALID_SCREENING_NO_SIGNAL_NO_NEGATIVE_SCIENTIFIC_AUTHORITY"
SUPPORT_STOP="LOCAL_F0_SUPPORT_STOP_NO_SCIENTIFIC_NEGATIVE"
PROTOCOL_STOP="LOCAL_F0_PROTOCOL_STOP_NO_SCIENTIFIC_INTERPRETATION"
RUNTIME_STOP="LOCAL_F0_RUNTIME_STOP_NO_SCIENTIFIC_NEGATIVE"
IMPLEMENTATION_STOP="LOCAL_F0_IMPLEMENTATION_STOP_NO_SCIENTIFIC_NEGATIVE"
BUDGET_STOP="LOCAL_F0_BUDGET_STOP_NO_SCIENTIFIC_RESULT"
BASELINE_BOUNDARY="LOCAL_F0_BASELINE_BOUNDARY_NO_METHOD_NEGATIVE"
INCONCLUSIVE="LOCAL_F0_INCONCLUSIVE_NO_SCIENTIFIC_NEGATIVE"
REQUIRED_ROLES={"raw-trace","progress","execution-summary"}
ADJUDICATOR_ROLE="INDEPENDENT_LOCAL_F0_EVIDENCE_ADJUDICATOR"
CHECKS=("artifact_manifest_integrity_pass","protocol_validity_pass","support_qualification_pass","truth_source_valid_pass","outcome_semantics_valid_pass","budget_compliant_pass","no_outcome_selection_pass","baseline_parity_pass","statistical_plan_followed_pass")
ZERO_AUTHORITY={"scientific":False,"p0":False,"full_experiment":False,"submission":False}

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _text(v): return str(v or "").strip()
def _digest(v): return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _slug(v): return re.sub(r"[^A-Za-z0-9_.-]+","-",str(v)).strip("-")[:180] or "unknown"
def _sha(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_manifest(run_root:Path, rows:list[Mapping[str,Any]]):
 root=run_root.resolve(); verified=[]; errors=[]; roles=set()
 for i,row in enumerate(rows):
  if not isinstance(row,Mapping): errors.append(f"artifact-{i}-not-object"); continue
  rel=_text(row.get("relative_path")); role=_text(row.get("role")); expected=_text(row.get("sha256")); size=int(row.get("bytes") or -1)
  if not rel or not role or not expected: errors.append(f"artifact-{i}-identity-incomplete"); continue
  path=(root/rel).resolve()
  try: path.relative_to(root)
  except ValueError: errors.append(f"artifact-{i}-path-escape"); continue
  if not path.is_file(): errors.append(f"artifact-{i}-missing"); continue
  actual=_sha(path); actual_size=path.stat().st_size; roles.add(role)
  if actual!=expected: errors.append(f"artifact-{i}-sha-mismatch")
  if actual_size!=size: errors.append(f"artifact-{i}-bytes-mismatch")
  verified.append({"relative_path":rel,"role":role,"sha256":actual,"bytes":actual_size})
 errors.extend(f"required-artifact-role-missing:{x}" for x in sorted(REQUIRED_ROLES-roles))
 return verified,errors

def completion_identity(r):
 return {k:r.get(k) for k in ("contract_id","contract_sha256","run_start_sha256","run_id","typed_execution_outcome","completed_units","provider_calls","gpu_hours_used","artifact_manifest_sha256","artifact_manifest_errors","budget_compliant","resource_release_sha256","experiment_authority_release_sha256","completed_at","status")}

def validate_completion(r:Mapping[str,Any])->bool:
 if r.get("receipt_type")!="reopen-local-f0-run-completion" or r.get("status") not in {COMPLETION_READY,COMPLETION_HOLD}: return False
 if r.get("execution_completed") is not True or r.get("evidence_adjudication_required") is not True or r.get("scientific_interpretation_authorized") is not False: return False
 if r.get("resource_lease_released") is not True or r.get("experiment_authority_released") is not True: return False
 if any(r.get(k) is not False for k in ("p0_authorization_review_eligible","scientific_authority","p0_authority","full_experiment_authority","submission_authority")): return False
 if _text(r.get("typed_execution_outcome")) not in {x for x in TYPED_OUTCOMES if x not in {"METHOD-PASS","METHOD-FAIL"}}: return False
 if _digest(r.get("artifact_manifest") or [])!=_text(r.get("artifact_manifest_sha256")): return False
 expected=COMPLETION_READY if not list(r.get("artifact_manifest_errors") or []) and r.get("budget_compliant") is True else COMPLETION_HOLD
 return r.get("status")==expected and _text(r.get("completion_sha256"))==_digest(completion_identity(r))

def complete_run(*,root:Path,run_start:Mapping[str,Any],local_authorization:Mapping[str,Any],typed_execution_outcome:str,completed_units:int,provider_calls:int,gpu_hours_used:float,artifact_manifest:list[Mapping[str,Any]],completed_at:str=""):
 root=Path(root)
 if not validate_reopened_local_f0_run_start(run_start): raise RuntimeError("valid run-start receipt required")
 if not validate_local_validation_authorization(local_authorization): raise RuntimeError("valid local-validation authorization required")
 if _text(run_start.get("local_validation_authorization_sha256"))!=_text(local_authorization.get("local_validation_authorization_sha256")): raise RuntimeError("completion local-validation authority mismatch")
 outcome=_text(typed_execution_outcome); allowed={x for x in TYPED_OUTCOMES if x not in {"METHOD-PASS","METHOD-FAIL"}}
 if outcome not in allowed: raise RuntimeError("local-F0 completion requires screening/non-method typed outcome")
 completed_units=int(completed_units); provider_calls=int(provider_calls); gpu_hours_used=float(gpu_hours_used)
 if completed_units<0 or provider_calls<0 or gpu_hours_used<0: raise RuntimeError("completion usage counters must be nonnegative")
 run_root=Path(_text(run_start.get("run_root"))).resolve(); marker=run_root/"run-start.json"
 if not marker.is_file(): raise RuntimeError("run-start marker missing")
 verified,errors=verify_manifest(run_root,list(artifact_manifest or [])); budget=local_authorization.get("authorized_budget") or {}
 budget_ok=completed_units<=int(budget.get("max_units") or 0) and provider_calls<=int(budget.get("max_provider_calls") or 0) and gpu_hours_used<=float(budget.get("max_gpu_hours") or 0)+1e-12
 cid=_text(run_start.get("contract_id")); aid=_text(run_start.get("experiment_authority_id")); plan=_text(run_start.get("plan_hash")); lease_id=_text(run_start.get("gpu_lease_id"))
 resource=next((x for x in list_gpu_leases(root,False) if _text(x.get("lease_id"))==lease_id),{})
 if resource.get("status")=="active": resource_release=release_gpu_lease(root,_text(resource.get("server_id")),_text(resource.get("gpu_uuid")),lease_id,idea_id=cid,authority_id=aid,plan_hash=plan,outcome="local-f0-run-completed")
 else: resource_release={"status":_text(resource.get("status")) or "missing","lease_id":lease_id,"release_outcome":"already-inactive"}
 authority=validate_authority(root,cid,aid,plan)
 authority_release=release_authority(root,cid,aid,"local-f0-run-completed") if authority.get("valid") is True else {"status":_text((authority.get("authority") or {}).get("status")) or "missing","authority_id":aid,"release_outcome":"already-inactive"}
 if validate_authority(root,cid,aid,plan).get("valid") is True: raise RuntimeError("experiment authority remained active after completion")
 if any(_text(x.get("lease_id"))==lease_id for x in list_gpu_leases(root,True)): raise RuntimeError("GPU resource lease remained active after completion")
 r={"schema_version":SCHEMA_VERSION,"receipt_type":"reopen-local-f0-run-completion","contract_id":cid,"contract_sha256":_text(run_start.get("contract_sha256")),"run_start_sha256":_text(run_start.get("run_start_sha256")),"run_id":_text(run_start.get("run_id")),"typed_execution_outcome":outcome,"completed_units":completed_units,"provider_calls":provider_calls,"gpu_hours_used":gpu_hours_used,"artifact_manifest":verified,"artifact_manifest_sha256":_digest(verified),"artifact_manifest_errors":errors,"budget_compliant":budget_ok,"resource_release_sha256":_digest(resource_release),"experiment_authority_release_sha256":_digest(authority_release),"resource_lease_released":True,"experiment_authority_released":True,"completed_at":_text(completed_at) or _now(),"status":COMPLETION_READY if not errors and budget_ok else COMPLETION_HOLD,"execution_completed":True,"evidence_adjudication_required":True,"scientific_interpretation_authorized":False,"p0_authorization_review_eligible":False,"scientific_authority":False,"p0_authority":False,"full_experiment_authority":False,"submission_authority":False}
 r["completion_sha256"]=_digest(completion_identity(r))
 if not validate_completion(r): raise RuntimeError("generated completion receipt invalid")
 return r

def adjudication_identity(r):
 return {k:r.get(k) for k in ("contract_id","contract_sha256","completion_sha256","blueprint_sha256","blueprint_review_sha256","adjudicator_ref_sha256","adjudicated_at","checks","failed_checks","status","p0_authorization_review_eligible")}

def validate_adjudication(r:Mapping[str,Any])->bool:
 statuses={SIGNAL,NO_SIGNAL,SUPPORT_STOP,PROTOCOL_STOP,RUNTIME_STOP,IMPLEMENTATION_STOP,BUDGET_STOP,BASELINE_BOUNDARY,INCONCLUSIVE}
 if r.get("receipt_type")!="reopen-local-f0-evidence-adjudication" or r.get("status") not in statuses: return False
 ref=_text(r.get("adjudicator_ref")); checks=r.get("checks") or {}
 if not ref or hashlib.sha256(ref.encode()).hexdigest()!=_text(r.get("adjudicator_ref_sha256")): return False
 if not isinstance(checks,Mapping) or set(checks.keys())!=set(CHECKS): return False
 failed=[k for k in CHECKS if checks.get(k) is not True]
 if failed!=list(r.get("failed_checks") or []): return False
 if r.get("p0_authorization_review_eligible") is not (r.get("status")==SIGNAL): return False
 if any(r.get(k) is not False for k in ("p0_authorized","claim_update_authorized","method_verdict_authorized","scientific_authority","p0_authority","full_experiment_authority","submission_authority")): return False
 if r.get("parent_claim_status_unchanged") is not True or r.get("support_failure_is_not_scientific_negative") is not True or r.get("runtime_or_budget_stop_is_not_scientific_negative") is not True: return False
 return _text(r.get("evidence_adjudication_sha256"))==_digest(adjudication_identity(r))

def adjudicate_evidence(*,completion:Mapping[str,Any],blueprint:Mapping[str,Any],blueprint_review:Mapping[str,Any],packet:Mapping[str,Any]):
 if not validate_completion(completion): raise RuntimeError("valid completion receipt required")
 if not validate_reopen_experiment_blueprint(blueprint) or not validate_reopen_blueprint_review(blueprint_review): raise RuntimeError("valid blueprint/review required")
 if _text(completion.get("contract_id"))!=_text(blueprint.get("contract_id")) or _text(blueprint_review.get("blueprint_sha256"))!=_text(blueprint.get("blueprint_sha256")): raise RuntimeError("adjudication lineage mismatch")
 packet=dict(packet or {}); ref=_text(packet.get("adjudicator_ref")); at=_text(packet.get("adjudicated_at")); src=packet.get("checks") or {}
 if _text(packet.get("adjudicator_role"))!=ADJUDICATOR_ROLE or not ref or not at: raise RuntimeError("independent evidence adjudicator identity required")
 if not isinstance(src,Mapping) or set(src.keys())!=set(CHECKS): raise RuntimeError("evidence checks must match required set exactly")
 checks={k:src.get(k) is True for k in CHECKS}; failed=[k for k in CHECKS if not checks[k]]; outcome=_text(completion.get("typed_execution_outcome"))
 if completion.get("status")==COMPLETION_HOLD or any(not checks[k] for k in ("artifact_manifest_integrity_pass","protocol_validity_pass","truth_source_valid_pass","outcome_semantics_valid_pass","no_outcome_selection_pass")): status=PROTOCOL_STOP
 elif not checks["support_qualification_pass"]: status=SUPPORT_STOP
 elif outcome=="RUNTIME-ERROR": status=RUNTIME_STOP
 elif outcome=="IMPLEMENTATION-ERROR": status=IMPLEMENTATION_STOP
 elif outcome=="BUDGET-STOP" or not checks["budget_compliant_pass"]: status=BUDGET_STOP
 elif outcome in {"BASELINE-FLOOR","BASELINE-CEILING"}: status=BASELINE_BOUNDARY
 elif outcome=="SCREENING-SIGNAL" and not failed: status=SIGNAL
 elif outcome=="SCREENING-NO-SIGNAL" and not failed: status=NO_SIGNAL
 else: status=INCONCLUSIVE
 r={"schema_version":SCHEMA_VERSION,"receipt_type":"reopen-local-f0-evidence-adjudication","contract_id":_text(completion.get("contract_id")),"contract_sha256":_text(completion.get("contract_sha256")),"completion_sha256":_text(completion.get("completion_sha256")),"blueprint_sha256":_text(blueprint.get("blueprint_sha256")),"blueprint_review_sha256":_text(blueprint_review.get("blueprint_review_sha256")),"adjudicator_role":ADJUDICATOR_ROLE,"adjudicator_ref":ref,"adjudicator_ref_sha256":hashlib.sha256(ref.encode()).hexdigest(),"adjudicated_at":at,"checks":checks,"failed_checks":failed,"typed_execution_outcome":outcome,"status":status,"p0_authorization_review_eligible":status==SIGNAL,"p0_authorized":False,"claim_update_authorized":False,"method_verdict_authorized":False,"parent_claim_status_unchanged":True,"support_failure_is_not_scientific_negative":True,"runtime_or_budget_stop_is_not_scientific_negative":True,"scientific_authority":False,"p0_authority":False,"full_experiment_authority":False,"submission_authority":False}
 r["evidence_adjudication_sha256"]=_digest(adjudication_identity(r))
 if not validate_adjudication(r): raise RuntimeError("generated evidence adjudication invalid")
 return r

def _directory(root:Path):
 root=Path(root); return root if root.name=="scientific-contract-run-completions" else root/"scientific-contract-run-completions"
def _receipt_sha(r):
 typ=_text(r.get("receipt_type"))
 return _text(r.get("evidence_adjudication_sha256")) if typ=="reopen-local-f0-evidence-adjudication" else _text(r.get("completion_sha256"))
def validate_completion_ledger(ledger:Mapping[str,Any]):
 errors=[]; seen=set(); completions=set(); cid=_text(ledger.get("contract_id")); csha=_text(ledger.get("contract_sha256"))
 if (ledger.get("authority") or {})!=ZERO_AUTHORITY: errors.append("completion-ledger-authority-leak")
 for i,event in enumerate(ledger.get("events") or []):
  r=event.get("receipt") or {} if isinstance(event,Mapping) else {}; typ=_text(r.get("receipt_type")) if isinstance(r,Mapping) else ""
  valid=validate_completion(r) if typ=="reopen-local-f0-run-completion" else validate_adjudication(r) if typ=="reopen-local-f0-evidence-adjudication" else False
  if not valid: errors.append("completion-receipt-invalid"); continue
  if _text(r.get("contract_id"))!=cid or _text(r.get("contract_sha256"))!=csha: errors.append("completion-contract-lineage-mismatch")
  sha=_receipt_sha(r)
  if sha in seen: errors.append("completion-duplicate-receipt")
  if typ=="reopen-local-f0-run-completion": completions.add(_text(r.get("completion_sha256")))
  elif _text(r.get("completion_sha256")) not in completions: errors.append("adjudication-missing-prior-completion")
  if _text(event.get("event_id"))!=_digest([cid,i,typ,sha,_text(event.get("recorded_at"))])[:24]: errors.append("completion-event-id-invalid")
  seen.add(sha)
 return list(dict.fromkeys(errors))

def publish_receipt(root:Path,r:Mapping[str,Any]):
 typ=_text(r.get("receipt_type")); valid=validate_completion(r) if typ=="reopen-local-f0-run-completion" else validate_adjudication(r) if typ=="reopen-local-f0-evidence-adjudication" else False
 if not valid: raise RuntimeError("invalid completion/adjudication receipt")
 d=_directory(root); d.mkdir(parents=True,exist_ok=True); cid=_text(r.get("contract_id")); path=d/f"{_slug(cid)}.json"; lock=d/f".{_slug(cid)}.lock"
 with lock.open("a+") as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX); ledger=json.loads(path.read_text()) if path.exists() else {"schema_version":SCHEMA_VERSION,"contract_id":cid,"contract_sha256":_text(r.get("contract_sha256")),"events":[],"authority":dict(ZERO_AUTHORITY)}; sha=_receipt_sha(r)
  for event in ledger.get("events") or []:
   prior=event.get("receipt") or {} if isinstance(event,Mapping) else {}
   if isinstance(prior,Mapping) and _receipt_sha(prior)==sha: return ledger
  if typ=="reopen-local-f0-evidence-adjudication" and _text(r.get("completion_sha256")) not in {_text((e.get("receipt") or {}).get("completion_sha256")) for e in ledger.get("events") or [] if isinstance(e,Mapping) and (e.get("receipt") or {}).get("receipt_type")=="reopen-local-f0-run-completion"}: raise RuntimeError("adjudication requires published completion")
  at=_text(r.get("completed_at") or r.get("adjudicated_at")) or _now(); event={"event_type":typ,"receipt":dict(r),"recorded_at":at,"scientific_authority":False,"p0_authority":False}; event["event_id"]=_digest([cid,len(ledger.get("events") or []),typ,sha,at])[:24]; ledger.setdefault("events",[]).append(event); ledger["updated_at"]=at
  errs=validate_completion_ledger(ledger)
  if errs: raise RuntimeError(errs)
  tmp=path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n"); os.replace(tmp,path); return ledger

def public_completion(root:Path,contract_id:str):
 empty={"status":"LOCAL_F0_COMPLETION_REQUIRED","completion_sha256":"","evidence_adjudication_sha256":"","typed_execution_outcome":"","p0_authorization_review_eligible":False,"artifact_count":0,"failed_checks":[],"authority":dict(ZERO_AUTHORITY)}; path=_directory(root)/f"{_slug(contract_id)}.json"
 if not path.exists(): return empty
 try: ledger=json.loads(path.read_text())
 except Exception: return {**empty,"status":"LOCAL_F0_COMPLETION_LEDGER_INVALID"}
 if validate_completion_ledger(ledger): return {**empty,"status":"LOCAL_F0_COMPLETION_LEDGER_INVALID"}
 completion={}; adjudication={}
 for event in ledger.get("events") or []:
  r=event.get("receipt") or {} if isinstance(event,Mapping) else {}
  if r.get("receipt_type")=="reopen-local-f0-run-completion": completion=r
  elif r.get("receipt_type")=="reopen-local-f0-evidence-adjudication": adjudication=r
 if adjudication: return {**empty,"status":_text(adjudication.get("status")),"completion_sha256":_text(completion.get("completion_sha256")),"evidence_adjudication_sha256":_text(adjudication.get("evidence_adjudication_sha256")),"typed_execution_outcome":_text(completion.get("typed_execution_outcome")),"p0_authorization_review_eligible":adjudication.get("p0_authorization_review_eligible") is True,"artifact_count":len(completion.get("artifact_manifest") or []),"failed_checks":list(adjudication.get("failed_checks") or [])}
 if completion: return {**empty,"status":_text(completion.get("status")),"completion_sha256":_text(completion.get("completion_sha256")),"typed_execution_outcome":_text(completion.get("typed_execution_outcome")),"artifact_count":len(completion.get("artifact_manifest") or [])}
 return empty
