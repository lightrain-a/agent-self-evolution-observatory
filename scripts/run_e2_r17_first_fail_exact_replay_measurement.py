#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json,require,sha_file
ORDER='E2-R17-FIRST-FAIL-EXACT-REPLAY-MEASUREMENT-ORDER-v1'
def atomic(p:Path,d:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); os.replace(t,p)
def append(p:Path,d:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('a',encoding='utf-8') as h: h.write(json.dumps(d,ensure_ascii=False,sort_keys=True)+'\n'); h.flush(); os.fsync(h.fileno())
def rows(p:Path,key:str)->dict[str,dict[str,Any]]:
 out={}
 if not p.exists(): return out
 for line in p.read_text(encoding='utf-8').splitlines():
  if line.strip(): r=json.loads(line); v=str(r[key]); require(v not in out,f'duplicate {key}: {v}'); out[v]=r
 return out
def order(rep:int,task:str)->list[str]: return sorted(('win_c','first_fail'),key=lambda a:hashlib.sha256(f'{ORDER}|rep{rep}|{task}|{a}'.encode()).hexdigest())
def acquire(p:Path,csha:str,a1:str,a2:str)->None:
 p.parent.mkdir(parents=True,exist_ok=True); d={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-measurement-lease','status':'RUNNING_EXACT_REPLAY_MEASUREMENT','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'pid':os.getpid(),'contract_sha256':csha,'authorization_sha256s':[a1,a2],'exactly_once':True,'partial_effect_read':False}; fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600); os.write(fd,(json.dumps(d,sort_keys=True)+'\n').encode()); os.fsync(fd); os.close(fd)
def seal(p:Path,status:str)->None:
 d=load_json(p); d['status']=status; d['sealed_at_utc']=datetime.now(timezone.utc).isoformat(timespec='seconds'); atomic(p,d)
def verify_eval(row:dict[str,Any],state:dict[str,Any])->None:
 sp=Path(row['summary_path']); rp=Path(row['trajectory_ref_path']); require(sp.is_file() and sha_file(sp)==row['summary_sha256'],'eval summary drift'); require(rp.is_file() and sha_file(rp)==row['trajectory_ref_sha256'],'eval ref drift'); sd=load_json(sp); require(sd.get('status')=='COMPLETED' and int(sd.get('k'))==1 and sd.get('skill_pre_sha256')==state['skill_post_sha256'] and sd.get('updater_receipt_sha256')==state['update_receipt_sha256'],'state binding drift'); ref=load_json(rp); traj=Path(ref['trajectory_path']); require(traj.is_file() and sha_file(traj)==ref['trajectory_sha256'],'trajectory drift')
def ensure_eval(*,c:dict[str,Any],auth:Path,identity:Path,actor_python:Path,actor_env:dict[str,str],rep:int,arm:str,task:str,state:dict[str,Any],root:Path)->dict[str,Any]:
 mroot=root/f'replicate_{rep}/{arm}'; manifest=mroot/'completed_eval_tasks.jsonl'; existing=rows(manifest,'task_id')
 if task in existing: verify_eval(existing[task],state); return existing[task]
 eroot=mroot/'evaluation'/task
 if eroot.exists() and any(eroot.rglob('*')): raise RuntimeError(f'partial measurement eval rep{rep}/{arm}/{task}')
 ledger=mroot/'provider_budget.sqlite3'; summary=eroot/'evaluation_summary.json'; cmd=[str(actor_python),str(ROOT/'scripts/run_e2_r17_actor_pool_first_fail_exact_replay_measurement.py'),'--env-file',c['env_file'],'--suite-root',c['suite']['root'],'--mindmemos-root',c['mindmemos']['root'],'--run-root',str(eroot),'--identity',str(identity),'--authorization',str(auth.resolve()),'--skill-source',str(Path(state['skill_post_path']).parent),'--updater-receipt',state['update_receipt_path'],'--mode','e1','--model',c['actor']['requested_model'],'--task-id',task,'--k','1','--prefix-ks','1','--max-turns',str(c['actor']['max_turns']),'--max-output-tokens',str(c['actor']['max_output_tokens']),'--concurrency','1','--provider-budget-ledger',str(ledger),'--provider-total-call-limit','191','--provider-per-unit-call-limit','11','--output',str(summary)]
 r=subprocess.run(cmd,cwd=ROOT,env=actor_env,capture_output=True,text=True)
 if r.returncode!=0: atomic(mroot/f'eval_failure_{task}.json',{'status':'TECHNICAL_FAILURE','replicate':rep,'arm':arm,'task_id':task,'returncode':r.returncode,'stdout_tail':r.stdout[-3000:],'stderr_tail':r.stderr[-3000:],'provider_relaunch_authorized':False}); raise RuntimeError(f'measurement eval failed rep{rep}/{arm}/{task}')
 ref=eroot/'cases'/task/'rollout_0/r17_trajectory_ref.json'; require(summary.is_file() and ref.is_file(),'actor missing output'); row={'task_id':task,'summary_path':str(summary),'summary_sha256':sha_file(summary),'trajectory_ref_path':str(ref),'trajectory_ref_sha256':sha_file(ref),'completed_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds')}; verify_eval(row,state); append(manifest,row); return row
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--rep1-authorization',type=Path,required=True); ap.add_argument('--rep2-authorization',type=Path,required=True); a=ap.parse_args(); c=load_json(a.contract); require(c.get('status')=='FROZEN_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT','contract drift'); csha=sha_file(a.contract); auths={1:a.rep1_authorization,2:a.rep2_authorization}; ash={r:sha_file(p) for r,p in auths.items()}
 for rep,p in auths.items(): d=load_json(p); require(d.get('status')=='AUTHORIZED_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_ONLY' and d.get('contract_sha256')==csha and int(next(g['replicate'] for g in c['state_groups'] if g['group']==d['group']))==rep,'measurement auth drift')
 lease=Path(c['lineage_lease_path']); acquire(lease,csha,ash[1],ash[2]); success=False
 try:
  run=Path(c['run_root']); require(not run.exists(),'measurement root must be fresh'); run.mkdir(parents=True); actor_python,actor_env=validate_actor_runtime({'runtime':c['actor_runtime']}); actor_env['LITELLM_LOCAL_MODEL_COST_MAP']='True'; identity=ROOT/c['model_identity']['path']; require(sha_file(identity)==c['model_identity']['sha256'],'identity drift'); groups={int(g['replicate']):g for g in c['state_groups']}
  for rep in (1,2):
   states={x['arm']:x for x in groups[rep]['learned_states']}
   for task in c['heldout_task_ids']:
    for arm in order(rep,task): ensure_eval(c=c,auth=auths[rep],identity=identity,actor_python=actor_python,actor_env=actor_env,rep=rep,arm=arm,task=task,state=states[arm],root=run)
  out=[]
  for rep in (1,2):
   states={x['arm']:x for x in groups[rep]['learned_states']}
   for arm in ('win_c','first_fail'):
    mroot=run/f'replicate_{rep}/{arm}'; em=mroot/'completed_eval_tasks.jsonl'; er=rows(em,'task_id'); require(list(er)==c['heldout_task_ids'],f'completion drift rep{rep}/{arm}'); ledger=ProviderBudgetLedger(path=mroot/'provider_budget.sqlite3',contract_sha256=csha,authorization_sha256=ash[rep],total_limit=191,per_unit_limit=11,allow_create=False); st=states[arm]; out.append({'replicate':rep,'arm':arm,'skill_post_path':st['skill_post_path'],'skill_post_sha256':st['skill_post_sha256'],'update_receipt_path':st['update_receipt_path'],'update_receipt_sha256':st['update_receipt_sha256'],'parent_updater_contract_sha256':groups[rep]['parent_contract_sha256'],'parent_updater_authorization_sha256':groups[rep]['parent_authorization_sha256'],'measurement_authorization_sha256':ash[rep],'eval_manifest_path':str(em),'eval_manifest_sha256':sha_file(em),'completed_heldout_tasks':18,'provider_budget':ledger.snapshot().to_dict()})
  s={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-measurement-summary','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'COMPLETED_PENDING_SEPARATE_EXACT_REPLAY_MEASUREMENT_ANALYSIS','contract_sha256':csha,'authorization_sha256s':[ash[1],ash[2]],'case_stream':'e1-tsr-00','rows':out,'new_learned_states':0,'measurement_states':4,'heldout_rollout_units':72,'inference_performed':False,'partial_effect_read':False,'analyzer_run':False}; atomic(run/'summary/measurement_summary.json',s); success=True; print(json.dumps(s,ensure_ascii=False,indent=2,sort_keys=True)); return 0
 finally:
  if lease.exists(): seal(lease,'COMPLETED_EXACT_REPLAY_MEASUREMENT' if success else 'FAIL_CLOSED_EXACT_REPLAY_MEASUREMENT')
if __name__=='__main__': raise SystemExit(main())
