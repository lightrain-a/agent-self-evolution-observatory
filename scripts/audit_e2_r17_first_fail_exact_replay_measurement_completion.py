#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
STATUS='PASS_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_FULL_INTEGRITY_READY_FOR_ANALYSIS'
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
def ledger(p:Path,csha:str,asha:str)->int:
 con=sqlite3.connect(f'file:{p}?mode=ro',uri=True)
 try: meta={str(k):str(v) for k,v in con.execute('select key,value from metadata')}; n=con.execute('select count(*) from claims').fetchone()[0]
 finally: con.close()
 req(meta.get('contract_sha256')==csha and meta.get('authorization_sha256')==asha and int(meta.get('total_limit',-1))==191 and int(meta.get('per_unit_limit',-1))==11,'measurement ledger drift'); return int(n)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--rep1-authorization',type=Path,required=True); ap.add_argument('--rep2-authorization',type=Path,required=True); ap.add_argument('--run-summary',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--analysis-output',type=Path); a=ap.parse_args(); req(not a.output.exists(),'measurement audit exists');
 if a.analysis_output: req(not a.analysis_output.exists(),'analysis exists before audit')
 c=load(a.contract); s=load(a.run_summary); csha=sha(a.contract); auths={1:a.rep1_authorization,2:a.rep2_authorization}; ash={r:sha(p) for r,p in auths.items()}; req(c.get('status')=='FROZEN_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT','contract drift'); req(s.get('status')=='COMPLETED_PENDING_SEPARATE_EXACT_REPLAY_MEASUREMENT_ANALYSIS' and s.get('contract_sha256')==csha and s.get('authorization_sha256s')==[ash[1],ash[2]],'summary drift'); req(s.get('inference_performed') is False and s.get('partial_effect_read') is False and s.get('analyzer_run') is False and int(s.get('heldout_rollout_units',-1))==72,'summary boundary/cardinality drift')
 for rep,p in auths.items(): d=load(p); req(d.get('status')=='AUTHORIZED_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_ONLY' and d.get('contract_sha256')==csha,'measurement auth drift')
 run=Path(c['run_root']); req(run.is_dir() and not list(run.rglob('*failure*.json')),'measurement run/failure drift'); lease=Path(c['lineage_lease_path']); ld=load(lease); req(ld.get('status')=='COMPLETED_EXACT_REPLAY_MEASUREMENT' and ld.get('contract_sha256')==csha,'terminal lease drift'); groups={int(g['replicate']):g for g in c['state_groups']}; sr={(int(r['replicate']),str(r['arm'])):r for r in s['rows']}; req(set(sr)=={(r,a) for r in (1,2) for a in ('win_c','first_fail')},'summary row set drift'); heldout=set(c['heldout_task_ids']); claims={}
 for rep in (1,2):
  states={x['arm']:x for x in groups[rep]['learned_states']}
  for arm in ('win_c','first_fail'):
   r=sr[(rep,arm)]; st=states[arm]; req(r['skill_post_sha256']==st['skill_post_sha256'] and r['update_receipt_sha256']==st['update_receipt_sha256'] and r['parent_updater_authorization_sha256']==groups[rep]['parent_authorization_sha256'],'state provenance drift'); em=Path(r['eval_manifest_path']); req(em.is_file() and sha(em)==r['eval_manifest_sha256'],'eval manifest drift'); er=rows(em,'task_id'); req(set(er)==heldout and len(er)==18,'heldout drift')
   for task,row in er.items():
    sp=Path(row['summary_path']); rp=Path(row['trajectory_ref_path']); req(sp.is_file() and sha(sp)==row['summary_sha256'],'eval summary drift'); req(rp.is_file() and sha(rp)==row['trajectory_ref_sha256'],'eval ref drift'); sd=load(sp); req(sd.get('status')=='COMPLETED' and int(sd.get('k'))==1 and sd.get('skill_pre_sha256')==st['skill_post_sha256'] and sd.get('updater_receipt_sha256')==st['update_receipt_sha256'] and sd.get('contract_sha256')==csha and sd.get('authorization_sha256')==ash[rep],'measurement binding drift'); ref=load(rp); traj=Path(ref['trajectory_path']); req(traj.is_file() and sha(traj)==ref['trajectory_sha256'],'trajectory drift')
   claims[f'rep{rep}/{arm}']=ledger(run/f'replicate_{rep}/{arm}/provider_budget.sqlite3',csha,ash[rep])
 p={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-measurement-completion-audit','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':STATUS,'contract_path':str(a.contract),'contract_sha256':csha,'authorization_sha256s':[ash[1],ash[2]],'run_summary_path':str(a.run_summary),'run_summary_sha256':sha(a.run_summary),'lineage_lease_path':str(lease),'lineage_lease_sha256':sha(lease),'new_learned_states':0,'measurement_states':4,'heldout_rollout_units':72,'provider_claims_by_state':claims,'provider_budget_binding_pass':True,'scientific_scores_read':False,'partial_effect_read':False,'analyzer_run':False,'authority':{'mint_single_use_analysis_authorization':True,'provider_io':False,'scientific_execution':False,'updater':False,'paper_promotion':False,'submission':False}}; atomic(a.output,p); print(json.dumps(p,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
