#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARMS=('win_c','first_fail'); REPS=(1,2); EPS=1.0/18.0
AUDIT='PASS_FIRST_FAIL_EXACT_REPLAY_FULL_INTEGRITY_READY_FOR_ANALYSIS'
AUTH='AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY_ANALYSIS'

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,m:str)->None:
    if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)
def rows(path:Path,key:str)->dict[str,dict[str,Any]]:
    out={}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip(): r=json.loads(line); out[str(r[key])]=r
    return out

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--execution-authorization',type=Path,required=True); ap.add_argument('--analysis-authorization',type=Path,required=True); ap.add_argument('--completion-audit',type=Path,required=True); ap.add_argument('--run-summary',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); req(not a.output.exists(),'exact-replay analysis exists')
    c=load(a.contract); e=load(a.execution_authorization); aa=load(a.analysis_authorization); au=load(a.completion_audit); s=load(a.run_summary); csha=sha(a.contract); esha=sha(a.execution_authorization); aush=sha(a.completion_audit); ssha=sha(a.run_summary)
    req(c.get('status')=='FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY','contract drift'); req(e.get('status')=='AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY' and e.get('contract_sha256')==csha,'exec auth drift'); req(au.get('status')==AUDIT and au.get('scientific_scores_read') is False and au.get('partial_effect_read') is False and au.get('analyzer_run') is False and au.get('exact_evidence_identity_pass') is True,'audit not clean'); req(au.get('contract_sha256')==csha and au.get('execution_authorization_sha256')==esha and au.get('run_summary_sha256')==ssha,'audit binding drift'); req(aa.get('status')==AUTH and aa.get('single_use') is True,'analysis auth drift'); req(aa.get('contract_sha256')==csha and aa.get('execution_authorization_sha256')==esha and aa.get('completion_audit_sha256')==aush and aa.get('run_summary_sha256')==ssha,'analysis auth binding drift'); req(aa.get('analyzer_sha256')==sha(Path(__file__)) and Path(aa.get('analysis_output_path',''))==a.output,'analyzer/output authority drift')
    sr={(int(r['replicate']),str(r['arm'])):r for r in s['rows']}; heldout=c['heldout_task_ids']; rates={}; successes={}; task_scores={}; skills={}
    # First heldout outcome access occurs only after complete audit and single-use authority gates above.
    for rep in REPS:
        rates[rep]={}; successes[rep]={}; task_scores[rep]={}; skills[rep]={}
        for arm in ARMS:
            row=sr[(rep,arm)]; skills[rep][arm]=row['skill_post_sha256']; manifest=rows(Path(row['eval_manifest_path']),'task_id'); req(set(manifest)==set(heldout),f'heldout set drift rep{rep}/{arm}'); vals=[]
            for task in heldout:
                ref=load(Path(manifest[task]['trajectory_ref_path'])); value=float(ref['score']); req(value in (0.0,1.0),'score must be binary'); vals.append(value)
            rates[rep][arm]=statistics.fmean(vals); successes[rep][arm]=int(sum(vals)); task_scores[rep][arm]={task:int(v) for task,v in zip(heldout,vals)}
    diffs={rep:rates[rep]['first_fail']-rates[rep]['win_c'] for rep in REPS}; mean_diff=statistics.fmean(diffs.values()); rep_pass={rep:diffs[rep]>=EPS-1e-15 for rep in REPS}; passed=all(rep_pass.values()) and mean_diff>=EPS-1e-15
    status='FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_PASS' if passed else 'FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_FAIL_STATE_GENERATION_VARIANCE'
    parent=load(Path(c['parent_s1']['analysis_path']))
    payload={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-evidence-updater-replication-analysis','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':status,'contract_sha256':csha,'execution_authorization_sha256':esha,'analysis_authorization_sha256':sha(a.analysis_authorization),'completion_audit_sha256':aush,'run_summary_sha256':ssha,'case_stream':'e1-tsr-00','development_only':True,'exact_evidence_identity_pass':True,'measurement_replicates':[1,2],'successes':successes,'success_rates':rates,'skill_post_sha256_by_replicate':skills,'replicate_differences_first_fail_minus_win_c':diffs,'mean_new_replicate_difference':mean_diff,'replication_gate':{'minimum_difference_each_replicate':EPS,'minimum_mean_difference':EPS,'replicate_pass':rep_pass,'pass':passed},'historical_s1_rep0':{'descriptive_only':True,'first_fail_successes':parent['arm_successes']['first_fail'],'win_c_successes':parent['arm_successes']['win_c'],'difference_first_fail_minus_win_c':parent['arm_success_rate']['first_fail']-parent['arm_success_rate']['win_c']},'task_level_scores':task_scores,'interpretation':'Two new contemporaneous updater realizations are generated from byte-identical S1 rendered evidence for both First-Fail and WIN-C. The gate tests whether First-Fail treatment advantage reproduces despite hosted updater stochasticity.','authority':{'s2_execution':False,'new_followup_execution':False,'e3_confirmation':False,'second_backbone':False,'public_benchmark':False,'paper_promotion':False,'submission':False}}; atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if passed else 3
if __name__=='__main__': raise SystemExit(main())
