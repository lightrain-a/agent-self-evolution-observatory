#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,statistics
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
EPS=1.0/18.0; AUDIT='PASS_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_FULL_INTEGRITY_READY_FOR_ANALYSIS'; AUTH='AUTHORIZED_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_ANALYSIS'
def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,m:str)->None:
 if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)
def rows(p:Path,key:str)->dict[str,dict[str,Any]]:
 out={}
 for line in p.read_text(encoding='utf-8').splitlines():
  if line.strip(): r=json.loads(line); out[str(r[key])]=r
 return out
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--rep1-authorization',type=Path,required=True); ap.add_argument('--rep2-authorization',type=Path,required=True); ap.add_argument('--analysis-authorization',type=Path,required=True); ap.add_argument('--completion-audit',type=Path,required=True); ap.add_argument('--run-summary',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); req(not a.output.exists(),'measurement analysis exists')
 c=load(a.contract); au=load(a.completion_audit); aa=load(a.analysis_authorization); s=load(a.run_summary); csha=sha(a.contract); ash=[sha(a.rep1_authorization),sha(a.rep2_authorization)]; aush=sha(a.completion_audit); ssha=sha(a.run_summary)
 req(c.get('status')=='FROZEN_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT','contract drift'); req(au.get('status')==AUDIT and au.get('scientific_scores_read') is False and au.get('partial_effect_read') is False and au.get('analyzer_run') is False,'audit not clean'); req(au.get('contract_sha256')==csha and au.get('authorization_sha256s')==ash and au.get('run_summary_sha256')==ssha,'audit binding drift'); req(aa.get('status')==AUTH and aa.get('single_use') is True and aa.get('contract_sha256')==csha and aa.get('measurement_authorization_sha256s')==ash and aa.get('completion_audit_sha256')==aush and aa.get('run_summary_sha256')==ssha,'analysis auth drift'); req(aa.get('analyzer_sha256')==sha(Path(__file__)) and Path(aa.get('analysis_output_path',''))==a.output,'analyzer/output drift')
 sr={(int(r['replicate']),str(r['arm'])):r for r in s['rows']}; heldout=c['heldout_task_ids']; rates={}; successes={}; task_scores={}; diffs={}
 # First heldout score access only after complete integrity and single-use authorization validation above.
 for rep in (1,2):
  rates[rep]={}; successes[rep]={}; task_scores[rep]={}
  for arm in ('win_c','first_fail'):
   manifest=rows(Path(sr[(rep,arm)]['eval_manifest_path']),'task_id'); req(set(manifest)==set(heldout),'heldout set drift'); vals=[]
   for task in heldout:
    ref=load(Path(manifest[task]['trajectory_ref_path'])); v=float(ref['score']); req(v in (0.0,1.0),'score must be binary'); vals.append(v)
   rates[rep][arm]=statistics.fmean(vals); successes[rep][arm]=int(sum(vals)); task_scores[rep][arm]={t:int(v) for t,v in zip(heldout,vals)}
  diffs[rep]=rates[rep]['first_fail']-rates[rep]['win_c']
 mean=statistics.fmean(diffs.values()); rep_pass={r:diffs[r]>=EPS-1e-15 for r in (1,2)}; passed=all(rep_pass.values()) and mean>=EPS-1e-15; status='FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_PASS' if passed else 'FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_FAIL_STATE_GENERATION_VARIANCE'
 p={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-evidence-updater-replication-final-analysis','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':status,'contract_sha256':csha,'measurement_authorization_sha256s':ash,'analysis_authorization_sha256':sha(a.analysis_authorization),'completion_audit_sha256':aush,'run_summary_sha256':ssha,'case_stream':'e1-tsr-00','development_only':True,'successes':successes,'success_rates':rates,'replicate_differences_first_fail_minus_win_c':diffs,'mean_difference_first_fail_minus_win_c':mean,'replication_gate':{'minimum_difference_each_replicate':EPS,'minimum_mean_difference':EPS,'replicate_pass':rep_pass,'pass':passed},'task_level_scores':task_scores,'interpretation':'Rep1 and rep2 use the exact S1 rendered evidence for both arms but independently generated updater states. This adjudicates whether First-Fail advantage itself reproduces across hosted updater realizations.','authority':{'new_followup_execution':False,'s2_execution':False,'e3_confirmation':False,'second_backbone':False,'public_benchmark':False,'paper_promotion':False,'submission':False}}; atomic(a.output,p); print(json.dumps(p,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if passed else 3
if __name__=='__main__': raise SystemExit(main())
