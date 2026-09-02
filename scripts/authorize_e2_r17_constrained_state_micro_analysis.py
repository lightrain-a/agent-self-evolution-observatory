#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]: return json.loads(path.read_text(encoding="utf-8"))
def require(c:bool,m:str)->None:
    if not c: raise RuntimeError(m)
def atomic(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); tmp.replace(path)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",type=Path,required=True); ap.add_argument("--execution-authorization",type=Path,required=True); ap.add_argument("--completion-audit",type=Path,required=True); ap.add_argument("--run-summary",type=Path,required=True); ap.add_argument("--analyzer",type=Path,required=True); ap.add_argument("--analysis-output",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    require(not args.output.exists(),"analysis authorization exists"); require(not args.analysis_output.exists(),"analysis output exists")
    c=load(args.contract); a=load(args.execution_authorization); audit=load(args.completion_audit); summary=load(args.run_summary); csha=sha(args.contract); asha=sha(args.execution_authorization)
    require(c.get("status")=="FROZEN_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO","contract drift")
    require(a.get("status")=="AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_MEASUREMENT" and a.get("contract_sha256")==csha,"execution auth drift")
    require(audit.get("status")=="PASS_CONSTRAINED_STATE_MICRO_FULL_INTEGRITY_READY_FOR_ANALYSIS","audit not passing")
    require(audit.get("contract_sha256")==csha and audit.get("execution_authorization_sha256")==asha,"audit binding drift")
    require(audit.get("scientific_scores_read") is False and audit.get("partial_effect_read") is False,"audit crossed score boundary")
    require(summary.get("status")=="COMPLETED_PENDING_SEPARATE_CONSTRAINED_STATE_ANALYSIS","summary incomplete")
    payload={"schema_version":"1.0","artifact_type":"e2-r17-single-case-constrained-state-micro-analysis-authorization","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_ANALYSIS","contract_path":str(args.contract.resolve()),"contract_sha256":csha,"execution_authorization_sha256":asha,"completion_audit_path":str(args.completion_audit.resolve()),"completion_audit_sha256":sha(args.completion_audit),"run_summary_path":str(args.run_summary.resolve()),"run_summary_sha256":sha(args.run_summary),"analyzer_path":str(args.analyzer.resolve()),"analyzer_sha256":sha(args.analyzer),"analysis_output_path":str(args.analysis_output.resolve()),"single_use":True,"authority":{"analyzer":True,"read_complete_micro_effect_once":True,"scientific_experiment":False,"provider_io":False,"updater":False,"heldout_evaluation":False,"second_backbone":False,"public_benchmark":False,"e3_confirmation":False,"paper_promotion":False,"submission":False}}
    atomic(args.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
