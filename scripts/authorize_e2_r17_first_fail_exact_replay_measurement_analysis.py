#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
AUDIT='PASS_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_FULL_INTEGRITY_READY_FOR_ANALYSIS'; STATUS='AUTHORIZED_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_ANALYSIS'
def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,m:str)->None:
 if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--rep1-authorization',type=Path,required=True); ap.add_argument('--rep2-authorization',type=Path,required=True); ap.add_argument('--completion-audit',type=Path,required=True); ap.add_argument('--run-summary',type=Path,required=True); ap.add_argument('--analyzer',type=Path,required=True); ap.add_argument('--analysis-output',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); req(not a.output.exists() and not a.analysis_output.exists(),'analysis auth/output exists')
 c=load(a.contract); au=load(a.completion_audit); s=load(a.run_summary); csha=sha(a.contract); ash=[sha(a.rep1_authorization),sha(a.rep2_authorization)]; req(c.get('status')=='FROZEN_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT','contract drift'); req(au.get('status')==AUDIT and au.get('contract_sha256')==csha and au.get('authorization_sha256s')==ash and au.get('run_summary_sha256')==sha(a.run_summary),'audit drift'); req(au.get('scientific_scores_read') is False and au.get('partial_effect_read') is False and au.get('analyzer_run') is False,'audit crossed outcome boundary'); req(s.get('status')=='COMPLETED_PENDING_SEPARATE_EXACT_REPLAY_MEASUREMENT_ANALYSIS','summary incomplete')
 p={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-measurement-analysis-authorization','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':STATUS,'contract_path':str(a.contract),'contract_sha256':csha,'measurement_authorization_sha256s':ash,'completion_audit_path':str(a.completion_audit),'completion_audit_sha256':sha(a.completion_audit),'run_summary_path':str(a.run_summary),'run_summary_sha256':sha(a.run_summary),'analyzer_path':str(a.analyzer),'analyzer_sha256':sha(a.analyzer),'analysis_output_path':str(a.analysis_output),'single_use':True,'authority':{'analyzer':True,'read_complete_measurement_effect_once':True,'scientific_experiment':False,'provider_io':False,'updater':False,'heldout_evaluation':False,'new_followup_execution':False,'s2_execution':False,'e3_confirmation':False,'second_backbone':False,'public_benchmark':False,'paper_promotion':False,'submission':False}}; atomic(a.output,p); print(json.dumps(p,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
