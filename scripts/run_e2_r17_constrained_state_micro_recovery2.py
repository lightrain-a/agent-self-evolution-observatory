#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime

ARMS=("g0_base","g1_verify","g2_complete","g3_complete_recover")
CONTRACT_STATUS="FROZEN_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO"
AUTH_STATUS="AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_MEASUREMENT"

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def req(c:bool,m:str)->None:
    if not c: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)
def append(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as h: h.write(json.dumps(d,sort_keys=True)+'\n'); h.flush(); os.fsync(h.fileno())
def rows(p:Path,key:str)->dict[str,dict[str,Any]]:
    out={}
    if not p.exists(): return out
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip():
            r=json.loads(line); v=str(r[key]); req(v not in out,f'duplicate {key}: {v}'); out[v]=r
    return out

def validate(cp:Path,ap:Path)->tuple[dict[str,Any],dict[str,Any],str,str]:
    c,a=load(cp),load(ap); cs,aus=sha(cp),sha(ap)
    req(c.get('status')==CONTRACT_STATUS,'recovery2 contract drift'); req(a.get('status')==AUTH_STATUS and a.get('contract_sha256')==cs,'recovery2 auth drift')
    au=a.get('authority') or {}; req(au.get('scientific_experiment') is True and au.get('measurement_only') is True and au.get('updater') is False and au.get('analyzer') is False,'authority drift')
    rec=c['recovery2']; req(rec['inherited_completed_measurements']==45 and rec['new_measurements']==27 and rec['completed_unit_replay'] is False,'recovery2 cardinality drift')
    parent=Path(rec['parent_run_root']); lease=Path(rec['parent_lease_path']); req(parent.is_dir() and lease.is_file(),'parent recovery missing'); ld=load(lease); req(ld.get('status')=='FAIL_CLOSED_CONSTRAINED_STATE_MICRO','parent recovery not fail-closed')
    fp=parent/rec['parent_failure_relpath']; req(fp.is_file() and sha(fp)==rec['parent_failure_sha256'],'parent failure drift'); fd=load(fp); req(fd.get('task_id')=='r17-b4-msp-p8' and fd.get('arm')=='g2_complete','parent failure identity drift'); req('weekly usage quota' in str(fd.get('stderr_tail','')),'parent failure is not explicit weekly quota 429')
    req(int(a['execution_scope']['provider_budget']['total_limit'])==int(rec['child_provider_total_limit'])==123,'child budget drift')
    return c,a,cs,aus

def verify_parent_row(row:dict[str,Any],skill_sha:str,parent_cs:str,parent_as:str)->None:
    sp=Path(row['summary_path']); rp=Path(row['trajectory_ref_path']); req(sp.is_file() and sha(sp)==row['summary_sha256'],'parent summary drift'); req(rp.is_file() and sha(rp)==row['trajectory_ref_sha256'],'parent ref drift'); sd=load(sp); req(sd.get('status')=='COMPLETED' and int(sd.get('k'))==1,'parent eval status drift'); req(sd.get('skill_pre_sha256')==skill_sha,'parent skill drift'); req(sd.get('contract_sha256')==parent_cs and sd.get('authorization_sha256')==parent_as,'parent provenance drift'); ref=load(rp); tp=Path(ref['trajectory_path']); req(tp.is_file() and sha(tp)==ref['trajectory_sha256'],'parent trajectory drift')

def create_state_receipt(run:Path,arm:str,state:dict[str,Any],cs:str,aus:str)->Path:
    p=run/'state_receipts'/arm/'update_receipt.json'; payload={'schema_version':'1.0','artifact_type':'e2-r17-deterministic-constrained-state-receipt','status':'COMPLETED','arm':arm,'contract_sha256':cs,'authorization_sha256':aus,'skill_post_path':str(Path(state['skill_path']).resolve()),'skill_post_sha256':state['skill_sha256'],'deterministic_state':True,'updater_calls':0}; atomic(p,payload); return p

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--authorization',type=Path,required=True); args=ap.parse_args(); c,a,cs,aus=validate(args.contract,args.authorization)
    run=Path(c['run_root']); lease=Path(c['lineage_lease_path']); req(not run.exists() and not lease.exists(),'recovery2 run root/lease not fresh'); run.mkdir(parents=True)
    lease.parent.mkdir(parents=True,exist_ok=True); atomic(lease,{'schema_version':'1.0','artifact_type':'e2-r17-constrained-state-micro-recovery2-lineage-lease','status':'RUNNING_CONSTRAINED_STATE_MICRO_RECOVERY2','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'pid':os.getpid(),'pgid':os.getpgrp(),'contract_sha256':cs,'authorization_sha256':aus,'exactly_once':True,'partial_effect_read':False})
    success=False
    try:
        actor_py,env=validate_actor_runtime({'runtime':c['actor_runtime']}); env['LITELLM_LOCAL_MODEL_COST_MAP']='True'; states={x['arm']:x for x in c['states']}; receipts={arm:create_state_receipt(run,arm,states[arm],cs,aus) for arm in ARMS}; identity=ROOT/c['model_identity']['path']; held=list(c['heldout_task_ids']); parent_cs=c['recovery2']['parent_contract_sha256']; parent_as=c['recovery2']['parent_authorization_sha256']
        parent_rows={}; allowed=[]
        for arm in ARMS:
            pm=Path(c['recovery2']['parent_manifests'][arm]['path']); req(pm.is_file() and sha(pm)==c['recovery2']['parent_manifests'][arm]['sha256'],f'parent manifest drift {arm}'); pr=rows(pm,'task_id'); parent_rows[arm]=pr
            for row in pr.values(): verify_parent_row(row,states[arm]['skill_sha256'],parent_cs,parent_as)
            for task in held:
                if task not in pr: allowed.append((arm,task))
        req(len(allowed)==27 and ('g2_complete','r17-b4-msp-p8') in allowed,'remaining set drift')
        completed_child={arm:{} for arm in ARMS}; ledgers={}
        for arm,task in allowed:
            state_root=run/'measurement'/arm; manifest=state_root/'completed_eval_tasks.jsonl'; eroot=state_root/'evaluation'/task
            if eroot.exists() and any(eroot.rglob('*')): raise RuntimeError(f'ambiguous recovery2 partial unit {arm}/{task}')
            if arm not in ledgers:
                lp=state_root/'provider_budget.sqlite3'; ledgers[arm]=(lp,ProviderBudgetLedger(path=lp,contract_sha256=cs,authorization_sha256=aus,total_limit=123,per_unit_limit=11,allow_create=True))
            lp,ledger=ledgers[arm]; before=ledger.snapshot().total_claimed; out=eroot/'evaluation_summary.json'; skill_dir=str(Path(states[arm]['skill_path']).parent)
            cmd=[str(actor_py),str(ROOT/'scripts/run_e2_r17_actor_pool_constrained_state_micro.py'),'--env-file',c['env_file'],'--suite-root',c['suite']['root'],'--mindmemos-root',c['mindmemos']['root'],'--run-root',str(eroot),'--identity',str(identity),'--authorization',str(args.authorization.resolve()),'--skill-source',skill_dir,'--updater-receipt',str(receipts[arm]),'--mode','e1','--model',c['actor']['requested_model'],'--task-id',task,'--k','1','--prefix-ks','1','--max-turns',str(c['actor']['max_turns']),'--max-output-tokens',str(c['actor']['max_output_tokens']),'--concurrency','1','--provider-budget-ledger',str(lp),'--provider-total-call-limit','123','--provider-per-unit-call-limit','11','--output',str(out)]
            z=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True); after=ledger.snapshot().total_claimed
            if z.returncode!=0:
                atomic(state_root/f'eval_failure_{task}.json',{'status':'TECHNICAL_FAILURE','arm':arm,'task_id':task,'returncode':z.returncode,'provider_claims_before':before,'provider_claims_after':after,'stdout_tail':z.stdout[-3000:],'stderr_tail':z.stderr[-3000:],'provider_relaunch_authorized':False}); raise RuntimeError(f'recovery2 eval failed {arm}/{task}')
            ref=eroot/'cases'/task/'rollout_0/r17_trajectory_ref.json'; req(out.is_file() and ref.is_file(),'child actor output missing'); sd=load(out); req(sd.get('status')=='COMPLETED' and sd.get('skill_pre_sha256')==states[arm]['skill_sha256'],'child eval binding drift'); row={'task_id':task,'summary_path':str(out),'summary_sha256':sha(out),'trajectory_ref_path':str(ref),'trajectory_ref_sha256':sha(ref),'completed_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'source':'recovery2_child'}; append(manifest,row); completed_child[arm][task]=row
        combined_rows=[]
        for arm in ARMS:
            cm=run/'combined'/arm/'completed_eval_tasks.jsonl'
            for task in held:
                row=parent_rows[arm].get(task) or completed_child[arm].get(task); req(row is not None,f'missing combined {arm}/{task}'); append(cm,row)
            req(len(rows(cm,'task_id'))==18,f'combined count drift {arm}'); combined_rows.append({'arm':arm,'eval_manifest_path':str(cm),'eval_manifest_sha256':sha(cm),'completed_heldout_tasks':18})
        summary={'schema_version':'1.0','artifact_type':'e2-r17-single-case-constrained-state-micro-recovery2-summary','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'COMPLETED_PENDING_SEPARATE_CONSTRAINED_STATE_ANALYSIS','contract_sha256':cs,'authorization_sha256':aus,'case_stream':'e1-tsr-00','rows':combined_rows,'heldout_rollout_units':72,'inherited_completed_measurements':45,'new_measurements':27,'explicit_429_recovery_units':1,'new_updater_calls':0,'inference_performed':False,'partial_effect_read':False,'analyzer_run':False}; atomic(run/'summary/recovery2_summary.json',summary); success=True; print(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)); return 0
    finally:
        if lease.exists():
            ld=load(lease); ld['status']='COMPLETED_CONSTRAINED_STATE_MICRO' if success else 'FAIL_CLOSED_CONSTRAINED_STATE_MICRO_RECOVERY2'; ld['sealed_at_utc']=datetime.now(timezone.utc).isoformat(timespec='seconds'); atomic(lease,ld)
if __name__=='__main__': raise SystemExit(main())
