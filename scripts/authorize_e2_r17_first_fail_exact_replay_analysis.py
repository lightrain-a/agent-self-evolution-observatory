#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT='PASS_FIRST_FAIL_EXACT_REPLAY_FULL_INTEGRITY_READY_FOR_ANALYSIS'
STATUS='AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY_ANALYSIS'

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,m:str)->None:
    if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--execution-authorization',type=Path,required=True); ap.add_argument('--completion-audit',type=Path,required=True); ap.add_argument('--run-summary',type=Path,required=True); ap.add_argument('--analyzer',type=Path,required=True); ap.add_argument('--analysis-output',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); req(not a.output.exists() and not a.analysis_output.exists(),'exact-replay analysis auth/output exists')
    c=load(a.contract); e=load(a.execution_authorization); au=load(a.completion_audit); s=load(a.run_summary); csha=sha(a.contract); esha=sha(a.execution_authorization)
    req(c.get('status')=='FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY','contract drift'); req(e.get('status')=='AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY' and e.get('contract_sha256')==csha,'exec auth drift'); req(au.get('status')==AUDIT and au.get('contract_sha256')==csha and au.get('execution_authorization_sha256')==esha,'audit drift'); req(au.get('scientific_scores_read') is False and au.get('partial_effect_read') is False and au.get('analyzer_run') is False and au.get('exact_evidence_identity_pass') is True,'audit boundary drift'); req(au.get('run_summary_sha256')==sha(a.run_summary) and s.get('status')=='COMPLETED_PENDING_SEPARATE_EXACT_REPLAY_ANALYSIS','summary drift')
    d={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-analysis-authorization','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':STATUS,'contract_path':str(a.contract),'contract_sha256':csha,'execution_authorization_path':str(a.execution_authorization),'execution_authorization_sha256':esha,'completion_audit_path':str(a.completion_audit),'completion_audit_sha256':sha(a.completion_audit),'run_summary_path':str(a.run_summary),'run_summary_sha256':sha(a.run_summary),'analyzer_path':str(a.analyzer),'analyzer_sha256':sha(a.analyzer),'analysis_output_path':str(a.analysis_output),'single_use':True,'authority':{'analyzer':True,'read_complete_exact_replay_effect_once':True,'scientific_experiment':False,'provider_io':False,'updater':False,'heldout_evaluation':False,'s2_execution':False,'second_backbone':False,'public_benchmark':False,'e3_confirmation':False,'paper_promotion':False,'submission':False}}; atomic(a.output,d); print(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
