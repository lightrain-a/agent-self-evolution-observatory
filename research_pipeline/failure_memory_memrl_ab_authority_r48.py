#!/usr/bin/env python3
"""Freeze conditional A/B sub-estimand authority before any validation outcome.

This narrows, rather than expands, the already human-authorized 32-cluster
primary scope. It does not authorize C/D and cannot be used to call the original
four-arm R43 program complete.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
CONTRACT = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r48-ab-identification-operationalization-contract.json"
PARENT_AUTH = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r45m1-replacement-execution-authority-v2.json"
MIGRATION = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r45m1-host-migration-execution-manifest-v2.json"
OUT = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r48-ab-identification-conditional-authority.json"
STATUS = "CONDITIONAL_AB_SUBESTIMAND_EXECUTION_AUTHORITY_FROZEN_PREVALIDATION"


def load(p: Path) -> dict[str, Any]:
    v = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v, dict): raise ValueError(f"not-object:{p}")
    return v


def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v: Any) -> str: return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def valid(v: dict[str,Any]) -> bool:
    x=v.get("receipt_sha256"); return isinstance(x,str) and x==digest({k:z for k,z in v.items() if k!="receipt_sha256"})


def build() -> dict[str,Any]:
    c,a,m=map(load,[CONTRACT,PARENT_AUTH,MIGRATION])
    if not all(valid(x) for x in [c,a,m]): raise ValueError("receipt-hash-drift")
    if c.get("status")!="PREVALIDATION_AB_IDENTIFICATION_FROZEN_C_D_REMAINS_NOT_EXECUTABLE": raise ValueError("contract-status")
    scope=((a.get("authorized_scope") or {}).get("primary_confirmatory") or {})
    if scope.get("authorized_conditionally_after_source_and_utilization_qualification") is not True or int(scope.get("exact_clusters") or 0)!=32:
        raise ValueError("parent-primary-authority-drift")
    arms=list(scope.get("arms") or [])
    if "A_content_only" not in arms or "B_raw_provenance" not in arms: raise ValueError("parent-A-B-not-authorized")
    if ((a.get("authority") or {}).get("execution")) is not True or ((a.get("authority") or {}).get("local_gpu")) is not True:
        raise ValueError("parent-execution-authority-drift")
    p={
      "schema_version":"1.0","paper_id":PAPER_ID,
      "receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R48-AB-IDENTIFICATION-CONDITIONAL-AUTHORITY",
      "recorded_date":"2026-09-01","status":STATUS,
      "role":"NARROW_SUBESTIMAND_AUTHORITY_WITHIN_EXISTING_HUMAN_BOUNDED_PRIMARY_SCOPE",
      "bindings":{"contract_path":str(CONTRACT.relative_to(PROJECT_ROOT)),"contract_file_sha256":sha(CONTRACT),"contract_receipt_sha256":c.get("receipt_sha256"),"parent_authority_path":str(PARENT_AUTH.relative_to(PROJECT_ROOT)),"parent_authority_file_sha256":sha(PARENT_AUTH),"parent_authority_receipt_sha256":a.get("receipt_sha256"),"migration_manifest_file_sha256":sha(MIGRATION),"migration_manifest_receipt_sha256":m.get("receipt_sha256")},
      "scope":{"benchmark":"OSInteraction","clusters":32,"arms":["A_content_only","B_raw_provenance"],"arm_runs":64,"estimand":"B_raw_provenance - A_content_only","conditional_on":["R46M2 strict source qualification PASS","R47M2 utilization qualification PASS"],"C_D_execution":False,"four_arm_program_completion_claim":False},
      "hard_limits":{"second_A_B_run":False,"unit_replacement":False,"prompt_or_renderer_change_after_first_A_B_exposure":False,"model_or_runtime_change":False,"retrieval_rerun_between_arms":False,"partial_effect_inspection":False,"historical_pooling":False,"C_D_invention_or_execution":False,"optional_stopping":False},
      "prevalidation_accounting":{"A_B_treatment_outcomes_observed":0,"primary_confirmatory_outcomes_observed":0,"partial_A_B_effect_inspected":False},
      "authority":{"A_B_execution_conditionally":True,"C_D_execution":False,"local_gpu":True,"external_provider_spend":False,"scientific_belief":False,"claim_expansion":False},
      "scientific_boundary":"A/B may close only the already-registered minimum L2 identification estimand. C/D remains NOT EXECUTED and PSMG efficacy remains NOT IDENTIFIED."
    }
    p["receipt_sha256"]=digest(p);return p


def main():
    p=build();OUT.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":p["status"],"receipt_sha256":p["receipt_sha256"],"A_B_execution_conditionally":True,"C_D_execution":False},sort_keys=True))
if __name__=="__main__":main()
