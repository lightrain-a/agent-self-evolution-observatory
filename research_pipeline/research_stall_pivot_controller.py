from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import StorageSettings

SCHEMA_VERSION="1.0"
POLICY={
 "schema_version":SCHEMA_VERSION,
 "stall_counter_counts_new_findings_not_subjective_value":True,
 "two_consecutive_zero_new_finding_runs_require_structural_pivot":True,
 "four_consecutive_zero_new_finding_runs_require_human_replan":True,
 "operator_or_source_frame_change_resets_same_frame_stall":True,
 "execution_failure_is_not_scientific_negative":True,
 "stall_controller_has_zero_scientific_authority":True,
 "stall_controller_cannot_change_scientific_thresholds":True,
 "effort_increase_alone_does_not_satisfy_structural_pivot":True,
}

def _now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _sha(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def default_ledger_path(storage:StorageSettings|None=None)->Path:
 storage=storage or StorageSettings.from_env();return storage.run_dir/"automation"/"research-stall-pivot.jsonl"
def finding_fingerprints(generator_state:dict[str,Any])->list[str]:
 vals=set()
 for prefix,rows in (("candidate",generator_state.get("candidates") or []),("pref0",generator_state.get("pre_f0_candidates") or [])):
  for row in rows:
   if isinstance(row,dict) and str(row.get("candidate_id") or "").strip():vals.add(f"{prefix}:{str(row['candidate_id']).strip()}")
 blocked=(((generator_state.get("saturation_memory") or {}).get("blocked_problem_memory") or {}).get("portable_blocked_problem_memory") or [])
 for row in blocked:
  if isinstance(row,dict) and str(row.get("signature_id") or "").strip():vals.add(f"blocked:{str(row['signature_id']).strip()}")
 return sorted(vals)
def frame_signature(*,operator_version:str,source_set_sha256:str="")->str:return _sha({"operator_version":str(operator_version or ""),"source_set_sha256":str(source_set_sha256 or "")})
def source_set_sha256_from_primary(primary_state:dict[str,Any])->str:
 material=sorted((str(r.get("ref") or ""),str(r.get("evidence_id") or ""),str(r.get("source_sha256") or "")) for r in primary_state.get("records") or [] if isinstance(r,dict));return _sha(material)
def _load_rows(path:Path)->list[dict[str,Any]]:
 try:lines=path.read_text(encoding="utf-8").splitlines()
 except OSError:return []
 out=[]
 for line in lines:
  try:r=json.loads(line)
  except json.JSONDecodeError:continue
  if isinstance(r,dict):out.append(r)
 return out
def _directive(stale:int,*,execution_failed:bool=False)->dict[str,Any]:
 action="RECOVER_EXECUTION_WITHOUT_SCIENTIFIC_UPDATE" if execution_failed else ("ESCALATE_HUMAN_REPLAN" if stale>=4 else ("FORCE_STRUCTURAL_PIVOT" if stale>=2 else "CONTINUE_CURRENT_SEARCH"))
 return {"action":action,"structural_pivot_required":action in {"FORCE_STRUCTURAL_PIVOT","ESCALATE_HUMAN_REPLAN"},"human_replan_required":action=="ESCALATE_HUMAN_REPLAN","same_frame_automatic_discovery_allowed":action in {"CONTINUE_CURRENT_SEARCH","RECOVER_EXECUTION_WITHOUT_SCIENTIFIC_UPDATE"},"effort_only_change_is_structural_pivot":False,"allowed_pivot_classes":["scientific-object","search-primitive","source-regime","evidence-substrate"],"scientific_authority":False}
def load_research_stall_state(*,path:Path|None=None,storage:StorageSettings|None=None,current_frame_signature:str="")->dict[str,Any]:
 path=path or default_ledger_path(storage);rows=_load_rows(path);last=rows[-1] if rows else {};stale=int(last.get("stale_count") or 0);changed=bool(current_frame_signature and last.get("frame_signature") and current_frame_signature!=last.get("frame_signature"));stale=0 if changed else stale;directive=_directive(stale)
 return {"schema_version":SCHEMA_VERSION,"status":"STALL_STATE_READY","policy":dict(POLICY),"summary":{"observations":len(rows),"stale_count":stale,"frame_changed":changed,"last_new_findings":int(last.get("new_findings") or 0)},"directive":directive,"last_observation":last,"scientific_authority":False,"authority":{"provider_calls":False,"problem_gate":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
def observe_research_stall(*,generator_state:dict[str,Any],operator_version:str,source_set_sha256:str="",path:Path|None=None,storage:StorageSettings|None=None,execution_failed:bool=False,generated_at:str|None=None)->dict[str,Any]:
 path=path or default_ledger_path(storage);rows=_load_rows(path);frame=frame_signature(operator_version=operator_version,source_set_sha256=source_set_sha256);prior=[r for r in rows if r.get("frame_signature")==frame and r.get("execution_failed") is not True];seen={str(x) for r in prior for x in r.get("finding_fingerprints") or []};findings=finding_fingerprints(generator_state);new=sorted(set(findings)-seen);prev=int(prior[-1].get("stale_count") or 0) if prior else 0;stale=prev if execution_failed else (0 if new else prev+1);directive=_directive(stale,execution_failed=execution_failed)
 row={"schema_version":SCHEMA_VERSION,"generated_at":generated_at or _now(),"run_id":str(generator_state.get("run_id") or ""),"generator_status":str(generator_state.get("status") or ""),"operator_version":str(operator_version or ""),"source_set_sha256":str(source_set_sha256 or ""),"frame_signature":frame,"finding_fingerprints":findings,"new_finding_fingerprints":new,"new_findings":len(new),"stale_count":stale,"execution_failed":bool(execution_failed),"directive":directive,"scientific_authority":False}
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("a",encoding="utf-8") as h:h.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
 return {"schema_version":SCHEMA_VERSION,"status":directive["action"],"policy":dict(POLICY),"summary":{"stale_count":stale,"findings":len(findings),"new_findings":len(new),"execution_failed":bool(execution_failed)},"directive":directive,"observation":row,"scientific_authority":False,"authority":{"provider_calls":False,"problem_gate":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
