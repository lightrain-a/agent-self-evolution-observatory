#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS="PASS_FIRST_FAIL_STABILITY_FULL_INTEGRITY_READY_FOR_ANALYSIS"
ARMS=("win_c","first_fail")
REPS=(1,2)

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding="utf-8"))
def req(x:bool,m:str)->None:
    if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); t.replace(p)
def rows(path:Path,key:str)->dict[str,dict[str,Any]]:
    out={}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip(): r=json.loads(line); v=str(r[key]); req(v not in out,f"duplicate {key}: {v}"); out[v]=r
    return out
def audit_ledger(path:Path,csha:str,asha:str)->int:
    req(path.is_file(),f"missing ledger {path}"); con=sqlite3.connect(f"file:{path}?mode=ro",uri=True)
    try: meta={str(k):str(v) for k,v in con.execute('SELECT key,value FROM metadata')}; claims=[(str(u),int(i)) for u,i in con.execute('SELECT unit_id,unit_call_index FROM claims')]
    finally: con.close()
    req(meta.get('contract_sha256')==csha and meta.get('authorization_sha256')==asha,'stability ledger authority drift'); req(int(meta.get('total_limit',-1))==191 and int(meta.get('per_unit_limit',-1))==11,'stability ledger budget drift'); req(len(claims)==len(set(claims)) and len(claims)<=191,'stability ledger duplicate/budget drift'); counts=Counter(u for u,_ in claims)
    for u,n in counts.items(): req(n<=11 and sorted(i for uu,i in claims if uu==u)==list(range(1,n+1)),f'ledger sequence drift {u}')
    return len(claims)
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--execution-authorization',type=Path,required=True); ap.add_argument('--run-summary',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--analysis-output',type=Path); a=ap.parse_args(); req(not a.output.exists(),'stability audit exists');
    if a.analysis_output: req(not a.analysis_output.exists(),'stability analysis exists before audit')
    c=load(a.contract); ea=load(a.execution_authorization); s=load(a.run_summary); csha=sha(a.contract); easha=sha(a.execution_authorization)
    req(c.get('status')=='FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY','stability contract drift'); req(ea.get('status')=='AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY_MEASUREMENT' and ea.get('contract_sha256')==csha,'stability exec auth drift'); req(s.get('status')=='COMPLETED_PENDING_SEPARATE_STABILITY_ANALYSIS' and s.get('contract_sha256')==csha and s.get('authorization_sha256')==easha,'stability summary drift'); req(s.get('inference_performed') is False and s.get('partial_effect_read') is False and s.get('analyzer_run') is False,'stability runner crossed outcome boundary'); req(int(s.get('new_learned_states',-1))==0 and int(s.get('measurement_states',-1))==4 and int(s.get('heldout_rollout_units',-1))==72,'stability cardinality drift')
    run=Path(c['run_root']); req(run.is_dir(),'stability run root missing'); req(not list(run.rglob('*failure*.json')),'stability technical failures present'); lease=Path(c['lineage_lease_path']); ld=load(lease); req(ld.get('status')=='COMPLETED_FIRST_FAIL_STABILITY' and ld.get('contract_sha256')==csha and ld.get('authorization_sha256')==easha,'stability terminal lease drift')
    state_bind={x['arm']:x for x in c['learned_states']}; req(set(state_bind)==set(ARMS),'stability parent state set drift'); summary_rows={(int(r['replicate']),str(r['arm'])):r for r in s['rows']}; req(set(summary_rows)=={(r,a) for r in REPS for a in ARMS},'stability summary row set drift'); claims={}
    heldout=set(c['heldout_task_ids'])
    for rep in REPS:
        for arm in ARMS:
            r=summary_rows[(rep,arm)]; em=Path(r['eval_manifest_path']); req(em.is_file() and sha(em)==r['eval_manifest_sha256'],f'eval manifest drift rep{rep}/{arm}'); er=rows(em,'task_id'); req(set(er)==heldout and len(er)==18,f'heldout set drift rep{rep}/{arm}'); parent=state_bind[arm]
            for task,row in er.items():
                sp=Path(row['summary_path']); rp=Path(row['trajectory_ref_path']); req(sp.is_file() and sha(sp)==row['summary_sha256'],f'eval summary drift {rep}/{arm}/{task}'); req(rp.is_file() and sha(rp)==row['trajectory_ref_sha256'],f'eval ref drift {rep}/{arm}/{task}'); sd=load(sp); req(sd.get('status')=='COMPLETED' and int(sd.get('k'))==1 and sd.get('skill_pre_sha256')==parent['skill_post_sha256'] and sd.get('updater_receipt_sha256')==parent['update_receipt_sha256'],f'learned-state binding drift {rep}/{arm}/{task}'); ref=load(rp); traj=Path(ref['trajectory_path']); req(traj.is_file() and sha(traj)==ref['trajectory_sha256'],f'trajectory drift {rep}/{arm}/{task}')
                # Outcome-blind: heldout score is intentionally not accessed here.
            state_root=Path(em).parent; claims[f'rep{rep}/{arm}']=audit_ledger(state_root/'provider_budget.sqlite3',csha,easha)
    payload={'schema_version':'1.0','artifact_type':'e2-r17-single-case-first-fail-stability-completion-audit','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':STATUS,'contract_path':str(a.contract),'contract_sha256':csha,'execution_authorization_path':str(a.execution_authorization),'execution_authorization_sha256':easha,'run_summary_path':str(a.run_summary),'run_summary_sha256':sha(a.run_summary),'lineage_lease_path':str(lease),'lineage_lease_sha256':sha(lease),'new_learned_states':0,'measurement_states':4,'heldout_rollout_units':72,'provider_claims_by_measurement_state':claims,'provider_budget_binding_pass':True,'provider_claim_uniqueness_pass':True,'scientific_scores_read':False,'partial_effect_read':False,'analyzer_run':False,'authority':{'mint_single_use_stability_analysis_authorization':True,'provider_io':False,'scientific_execution':False,'updater':False,'paper_promotion':False,'submission':False}}; atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
