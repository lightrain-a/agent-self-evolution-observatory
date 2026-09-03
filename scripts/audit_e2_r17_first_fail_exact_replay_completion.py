#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS='PASS_FIRST_FAIL_EXACT_REPLAY_FULL_INTEGRITY_READY_FOR_ANALYSIS'
ARMS=('win_c','first_fail'); REPS=(1,2)

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,m:str)->None:
    if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)
def rows(path:Path,key:str)->dict[str,dict[str,Any]]:
    out={}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip(): r=json.loads(line); v=str(r[key]); req(v not in out,f'duplicate {key}: {v}'); out[v]=r
    return out
def audit_ledger(path:Path,csha:str,asha:str)->int:
    req(path.is_file(),f'missing ledger {path}'); con=sqlite3.connect(f'file:{path}?mode=ro',uri=True)
    try: meta={str(k):str(v) for k,v in con.execute('SELECT key,value FROM metadata')}; claims=[(str(u),int(i)) for u,i in con.execute('SELECT unit_id,unit_call_index FROM claims')]
    finally: con.close()
    req(meta.get('contract_sha256')==csha and meta.get('authorization_sha256')==asha,'ledger authority drift'); req(int(meta.get('total_limit',-1))==191 and int(meta.get('per_unit_limit',-1))==11,'ledger budget drift'); req(len(claims)==len(set(claims)) and len(claims)<=191,'ledger duplicate/budget drift'); counts=Counter(u for u,_ in claims)
    for u,n in counts.items(): req(n<=11 and sorted(i for uu,i in claims if uu==u)==list(range(1,n+1)),f'ledger sequence drift {u}')
    return len(claims)
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--execution-authorization',type=Path,required=True); ap.add_argument('--run-summary',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--analysis-output',type=Path); a=ap.parse_args(); req(not a.output.exists(),'exact-replay audit exists');
    if a.analysis_output: req(not a.analysis_output.exists(),'exact-replay analysis exists before audit')
    c=load(a.contract); ea=load(a.execution_authorization); s=load(a.run_summary); csha=sha(a.contract); easha=sha(a.execution_authorization)
    req(c.get('status')=='FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY','contract drift'); req(ea.get('status')=='AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY' and ea.get('contract_sha256')==csha,'exec auth drift'); req(s.get('status')=='COMPLETED_PENDING_SEPARATE_EXACT_REPLAY_ANALYSIS' and s.get('contract_sha256')==csha and s.get('authorization_sha256')==easha,'summary drift'); req(s.get('inference_performed') is False and s.get('partial_effect_read') is False and s.get('analyzer_run') is False,'runner crossed outcome boundary'); req(int(s.get('new_learned_states',-1))==4 and int(s.get('heldout_rollout_units',-1))==72,'cardinality drift')
    run=Path(c['run_root']); req(run.is_dir(),'run root missing'); req(not list(run.rglob('*failure*.json')),'technical failures present'); lease=Path(c['lineage_lease_path']); ld=load(lease); req(ld.get('status')=='COMPLETED_FIRST_FAIL_EXACT_REPLAY' and ld.get('contract_sha256')==csha and ld.get('authorization_sha256')==easha,'terminal lease drift')
    evidence=run/'exact_evidence_receipt.json'; ed=load(evidence); req(ed.get('contract_sha256')==csha and ed.get('authorization_sha256')==easha and ed.get('source_parent_s1_packet_identity_pass') is True and ed.get('partial_effect_read') is False,'exact evidence receipt drift')
    sr={(int(r['replicate']),str(r['arm'])):r for r in s['rows']}; req(set(sr)=={(r,a) for r in REPS for a in ARMS},'summary row set drift'); heldout=set(c['heldout_task_ids']); claims={}
    for rep in REPS:
        for arm in ARMS:
            r=sr[(rep,arm)]; state=Path(r['state_root']); skill=state/'update/skill_post/SKILL.md'; receipt=Path(r['update_receipt_path']); req(skill.is_file() and sha(skill)==r['skill_post_sha256'],f'skill drift rep{rep}/{arm}'); req(receipt.is_file() and sha(receipt)==r['update_receipt_sha256'],f'update receipt drift rep{rep}/{arm}'); ur=load(receipt); req(ur.get('contract_sha256')==csha and ur.get('authorization_sha256')==easha and ur.get('causal_purity_mode')=='arm_blinded_selected_evidence','update provenance drift')
            expected=c['exact_evidence'][arm]['evidence_sha256s']; actual=[str(x['rendered_packet_sha256']) for x in ur.get('packets') or []]; req(actual==expected,f'update evidence identity drift rep{rep}/{arm}')
            em=Path(r['eval_manifest_path']); req(em.is_file() and sha(em)==r['eval_manifest_sha256'],f'eval manifest drift rep{rep}/{arm}'); er=rows(em,'task_id'); req(set(er)==heldout and len(er)==18,f'heldout set drift rep{rep}/{arm}')
            for task,row in er.items():
                sp=Path(row['summary_path']); rp=Path(row['trajectory_ref_path']); req(sp.is_file() and sha(sp)==row['summary_sha256'],f'eval summary drift {rep}/{arm}/{task}'); req(rp.is_file() and sha(rp)==row['trajectory_ref_sha256'],f'eval ref drift {rep}/{arm}/{task}'); sd=load(sp); req(sd.get('status')=='COMPLETED' and int(sd.get('k'))==1 and sd.get('skill_pre_sha256')==r['skill_post_sha256'] and sd.get('updater_receipt_sha256')==r['update_receipt_sha256'],f'eval state binding drift {rep}/{arm}/{task}'); ref=load(rp); traj=Path(ref['trajectory_path']); req(traj.is_file() and sha(traj)==ref['trajectory_sha256'],f'trajectory drift {rep}/{arm}/{task}')
                # Outcome-blind: heldout score intentionally not accessed.
            claims[f'rep{rep}/{arm}']=audit_ledger(state/'checkpoints/provider_budget.sqlite3',csha,easha)
    payload={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-completion-audit','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':STATUS,'contract_path':str(a.contract),'contract_sha256':csha,'execution_authorization_path':str(a.execution_authorization),'execution_authorization_sha256':easha,'run_summary_path':str(a.run_summary),'run_summary_sha256':sha(a.run_summary),'lineage_lease_path':str(lease),'lineage_lease_sha256':sha(lease),'exact_evidence_receipt_path':str(evidence),'exact_evidence_receipt_sha256':sha(evidence),'new_learned_states':4,'heldout_rollout_units':72,'exact_evidence_identity_pass':True,'provider_claims_by_state':claims,'provider_budget_binding_pass':True,'provider_claim_uniqueness_pass':True,'scientific_scores_read':False,'partial_effect_read':False,'analyzer_run':False,'authority':{'mint_single_use_exact_replay_analysis_authorization':True,'provider_io':False,'scientific_execution':False,'updater':False,'paper_promotion':False,'submission':False}}; atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
