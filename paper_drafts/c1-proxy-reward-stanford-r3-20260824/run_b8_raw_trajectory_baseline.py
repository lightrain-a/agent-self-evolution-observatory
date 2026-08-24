#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PAPER_ID='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID='D2-PROXY-B8-RAW-TRAJECTORY-BASELINE'
MODEL='doubao-seed-2.0-mini'; RESOLVED='doubao-seed-2-0-mini-260215'
BASE_URL='https://ark.cn-beijing.volces.com/api/plan/v3'
TOTAL=144; N=4


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode('utf-8')).hexdigest()
def load(p:Path)->dict[str,Any]:
 d=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(d,dict):raise RuntimeError(f'JSON root not object:{p}')
 return d
def writej(p:Path,d:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');os.replace(t,p)
def req(x:bool,msg:str)->None:
 if not x:raise RuntimeError(msg)
def clean(a:str|None)->str:
 a=str(a or '').strip()
 if len(a)>=2 and a[0]==a[-1] and a[0] in "'\"":a=a[1:-1]
 return re.sub(r'(\w+)[\u2010-\u2015\u2212-](\w+)',r'\1-\2',a).lower()
def score(pred:str,refs:dict[str,Any]):
 p=clean(pred);s=1.0;checks={}
 if 'exact_match' in refs:
  ref=str(refs['exact_match']);v=float(p==clean(ref));s*=v;checks['exact_match']={'ref':ref,'score':v}
 if 'must_include' in refs:
  out=[]
  for ref in refs['must_include']:
   v=float(clean(str(ref)) in p);s*=v;out.append({'ref':str(ref),'score':v})
  checks['must_include']=out
 return s,checks
def evidence(traj_json:str):
 tr=json.loads(traj_json);states=[];hashes=[];seen=set()
 for step in (tr.get('steps') or {}).values():
  c=((step.get('input_messages') or {}).get('contents') or [])
  if not c:continue
  text=str(c[-1].get('content') or '')
  if '[Current state starts here]' not in text:continue
  text=text.split('[Current state starts here]',1)[1].strip();h=tsha(text)
  if h in seen:continue
  seen.add(h);states.append(text);hashes.append(h)
 return '\n\n--- RELEASED BROWSER STATE ---\n\n'.join(states),hashes
def prompt(task:str,ev:str,raw_trace:str)->str:
 return f"""The following is a compact action/result trace retrieved from a past task. It is the common trajectory evidence that a memory writer could transform into reusable memory. No counterfactual success/failure label and no rewritten memory item are supplied here.

RETRIEVED PRIOR TRAJECTORY TRACE:
{raw_trace.rstrip()}

You are answering a WebArena read-only benchmark task from a frozen released evidence packet.

RULES:
- Treat the prior trajectory trace only as procedural guidance from a past task, not factual evidence for the current task.
- Use only the RELEASED BROWSER EVIDENCE below as factual evidence for the current task.
- Do not invent names, prices, order values, product facts, ratings, or quotes absent from the released browser evidence.
- Return only the final answer to the benchmark task. Do not return JSON, browser actions, analysis, or commentary.

BENCHMARK TASK:
{task}

RELEASED BROWSER EVIDENCE:
{ev}

FINAL ANSWER:"""
def stage(u:dict[str,Any],i:int)->str:return f"rawtraj-{u['future_task']}-source-{u['selected_source_task']}-r{i}"

def validate(c:dict[str,Any]):
 req(c.get('status')=='FROZEN_BEFORE_PROVIDER_CALLS' and c.get('experiment_id')==EXPERIMENT_ID and c.get('paper_id')==PAPER_ID,'contract identity drift')
 req(c.get('future_task_count')==36 and len(c.get('task_units') or [])==36 and c.get('expected_provider_calls')==TOTAL and c.get('rollouts_per_task')==N,'geometry drift')
 m=c['model'];req(m['requested']==MODEL and m['expected_resolved']==RESOLVED and m['temperature']==0.2 and m['max_output_tokens']==900 and m['thinking']=='disabled' and m['provider_retries']==0 and m['substitution_allowed'] is False,'model drift')
 g=c['primary_gate'];req(g['min_mean_absolute_rewrite_vs_raw_effect']==0.15 and g['omnibus_three_arm_permutation_p_lt']==0.05 and g['permutation_repetitions']==100000 and g['permutation_seed']==20260824,'gate drift')
 a=c['authority'];req(a['experiment_authority'] and a['provider_call_authority'] and not a['claim_expansion_authority'] and not a['submission_authority'],'authority drift')
 for row in list(c['source_artifacts'].values())+[c['b4_contract'],c['b4_result'],c['b5_result'],c['human_authority']]:
  p=Path(row['path']);req(p.is_file() and sha(p)==row['sha256'],f'source drift:{p}')
 rr=c['code']['runner'];req(Path(rr['path']).resolve()==Path(__file__).resolve() and sha(Path(__file__))==rr['sha256'],'runner drift')
 for sid,row in c['source_summaries'].items():
  p=Path(row['path']);req(p.is_file() and sha(p)==row['sha256'] and tsha(p.read_text(encoding='utf-8'))==row['text_sha256'],f'raw trajectory drift:{sid}')
 for u in c['task_units']:
  row=u['raw_trajectory_memory'];req(int(row['source_task'])==int(u['selected_source_task']),'task/source mismatch')

def runtime(c:dict[str,Any]):
 root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root));sys.path.insert(0,str(Path(c['vendor_path'])))
 import pyarrow.parquet as pq
 from research_pipeline.config import load_env_file
 from research_pipeline.ark_provider import ArkResponseStateError,ArkResponsesClient,ArkSettings
 load_env_file(Path(c['provider_env_file']));base=ArkSettings.from_env();req(bool(base.api_key),'credential absent');req(base.base_url==BASE_URL,'base URL drift')
 cfg=ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=180.0,max_retries=0)
 return pq,ArkResponseStateError,ArkResponsesClient(cfg),cfg.safe_summary()
def task_data(c:dict[str,Any],pq):
 rows={int(x['task_id']):x for x in pq.read_table(Path(c['source_artifacts']['parquet']['path']),columns=['task_id','trajectory_json']).to_pylist()};out={}
 for u in c['task_units']:
  tid=int(u['future_task']);ev,hs=evidence(str(rows[tid]['trajectory_json']));req(tsha(ev)==u['evidence_sha256'] and hs==u['released_state_sha256'],f'evidence drift:{tid}')
  raw=Path(u['raw_trajectory_memory']['path']).read_text(encoding='utf-8');out[tid]={'task_prompt':u['task_prompt'],'evidence':ev,'refs':u['reference_answers'],'raw_trace':raw}
 return out
def one(client,error_type,u,i,t,root):
 st=stage(u,i);sp=root/'stages'/f'{st}.json'
 if sp.is_file():return load(sp),False
 pr=prompt(t['task_prompt'],t['evidence'],t['raw_trace']);base={'stage':st,'future_task':u['future_task'],'selected_source_task':u['selected_source_task'],'condition':'raw_trajectory','rollout':i,'prompt_sha256':tsha(pr),'requested_model':MODEL,'raw_trajectory_sha256':u['raw_trajectory_memory']['sha256']}
 try:
  r=client.respond(pr,model=MODEL,max_output_tokens=900,temperature=0.2,thinking='disabled',store=True,allow_thinking_compatibility_fallback=False);ans=str(r.get('text') or '').strip();writej(root/'provider-responses'/f'{st}.json',{**base,'response_id':r.get('response_id'),'provider_status':r.get('status'),'requested_model_returned':r.get('requested_model'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'answer':ans,'answer_sha256':tsha(ans) if ans else '','thinking_compatibility_fallback':r.get('thinking_compatibility_fallback')});req(str(r.get('requested_model'))==MODEL and str(r.get('resolved_model'))==RESOLVED,'model resolution drift');req(r.get('thinking_compatibility_fallback') is False and bool(ans),'empty/fallback response');sc,checks=score(ans,t['refs']);row={**base,'status':'complete','provider_status':r.get('status'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'answer_sha256':tsha(ans),'benchmark_score':sc,'evaluator_checks':checks}
 except error_type as e:row={**base,'status':'provider_state_failure_no_text','error_type':type(e).__name__,'provider_receipt':e.receipt()}
 except Exception as e:row={**base,'status':'provider_or_runtime_failure','error_type':type(e).__name__,'error':str(e)[:1000]}
 writej(sp,row);return row,True
def all_rows(c,root):
 out=[]
 for u in c['task_units']:
  for i in range(1,N+1):
   p=root/'stages'/f'{stage(u,i)}.json'
   if p.is_file():out.append(load(p))
 return out
def combined(c,rawrows):
 b4=load(Path(c['b4_result']['path']));b5=load(Path(c['b5_result']['path']));br=b4['rollouts'];nr=b5['rollouts'];cells=[]
 for u in c['task_units']:
  tid=int(u['future_task']);s=[float(x['benchmark_score']) for x in br if int(x['future_task'])==tid and x['condition']=='success'];f=[float(x['benchmark_score']) for x in br if int(x['future_task'])==tid and x['condition']=='failure'];r=[float(x['benchmark_score']) for x in rawrows if int(x['future_task'])==tid and x.get('status')=='complete'];n=[float(x['benchmark_score']) for x in nr if int(x['future_task'])==tid];req(len(s)==len(f)==len(r)==len(n)==N,f'arm count drift:{tid}');ps,pf,pr,p0=sum(s)/N,sum(f)/N,sum(r)/N,sum(n)/N
  d=(abs(ps-pr)+abs(pf-pr))/2;geom=min([('success_memory',abs(pr-ps)),('failure_memory',abs(pr-pf)),('no_memory',abs(pr-p0))],key=lambda z:(z[1],z[0]))[0]
  cells.append({'future_task':tid,'selected_source_task':u['selected_source_task'],'intent_template_id':u['intent_template_id'],'success_memory_rate':round(ps,6),'failure_memory_rate':round(pf,6),'raw_trajectory_rate':round(pr,6),'no_memory_rate':round(p0,6),'rewrite_vs_raw_effect':round(d,6),'raw_minus_no_memory':round(pr-p0,6),'raw_closest_arm':geom})
 obs=sum(x['rewrite_vs_raw_effect'] for x in cells)/len(cells);return obs,cells
def perm(c,rawrows,obs):
 b4=load(Path(c['b4_result']['path']));br=b4['rollouts'];pools=[]
 for u in c['task_units']:
  tid=int(u['future_task']);s=[float(x['benchmark_score']) for x in br if int(x['future_task'])==tid and x['condition']=='success'];f=[float(x['benchmark_score']) for x in br if int(x['future_task'])==tid and x['condition']=='failure'];r=[float(x['benchmark_score']) for x in rawrows if int(x['future_task'])==tid];pools.append(s+f+r)
 rng=random.Random(20260824);ge=0
 for _ in range(100000):
  vals=[]
  for pool in pools:
   z=list(pool);rng.shuffle(z);ps=sum(z[:4])/4;pf=sum(z[4:8])/4;pr=sum(z[8:12])/4;vals.append((abs(ps-pr)+abs(pf-pr))/2)
  if sum(vals)/len(vals)>=obs-1e-12:ge+=1
 return (ge+1)/100001
def report(c,root,provider,new):
 rows=all_rows(c,root);fail=[x for x in rows if x.get('status')!='complete'];full=len(rows)==TOTAL and not fail;obs=pv=None;cells=[];gate=False;secondary={}
 if full:
  obs,cells=combined(c,rows);pv=perm(c,rows,obs);gate=obs>=0.15 and pv<0.05;secondary={'mean_absolute_raw_vs_no_memory':round(sum(abs(x['raw_trajectory_rate']-x['no_memory_rate']) for x in cells)/len(cells),6),'raw_closest_arm_counts':dict(Counter(x['raw_closest_arm'] for x in cells)),'joint_raw_no_memory_floor_cells':sum(x['raw_trajectory_rate']==0 and x['no_memory_rate']==0 for x in cells),'joint_raw_no_memory_ceiling_cells':sum(x['raw_trajectory_rate']==1 and x['no_memory_rate']==1 for x in cells)}
 decision='SUPPORT_PRACTICALLY_LARGE_REWRITE_VS_RAW_EFFECT' if gate else ('REWRITE_VS_RAW_EFFECT_NOT_ESTABLISHED' if full else 'B8_INCOMPLETE_NO_SCIENTIFIC_VERDICT')
 return {'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'paper_id':PAPER_ID,'status':'B8_EXECUTION_COMPLETE' if full else 'B8_EXECUTION_PARTIAL','contract_sha256':c['contract_sha256'],'provider':provider,'summary':{'provider_calls_expected':TOTAL,'provider_calls_attempted_total':len(rows),'provider_calls_complete':sum(x.get('status')=='complete' for x in rows),'provider_failures':len(fail),'new_provider_calls_this_invocation':new,'future_tasks':36,'observed_mean_absolute_rewrite_vs_raw_effect':None if obs is None else round(obs,6),'three_arm_permutation_p_ge_observed':None if pv is None else round(pv,6),'practical_effect_floor':0.15,'primary_gate_pass':gate},'secondary':secondary,'cell_results':cells,'rollouts':[{k:x.get(k) for k in ('future_task','selected_source_task','condition','rollout','answer_sha256','benchmark_score','provider_status','resolved_model','usage','raw_trajectory_sha256')} for x in rows if x.get('status')=='complete'],'failures':[{k:x.get(k) for k in ('future_task','selected_source_task','condition','rollout','stage','status','error_type','provider_receipt','error')} for x in fail],'decision':decision,'scope_boundary':c['scope_boundary'],'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--private-root',required=True,type=Path);ap.add_argument('--max-new-calls',type=int,default=16);a=ap.parse_args();c=load(a.contract);validate(c);req(1<=a.max_new_calls<=TOTAL,'invalid chunk limit');a.private_root.mkdir(parents=True,exist_ok=True);fh=(a.private_root/'transaction.lock').open('a+')
 try:fcntl.flock(fh.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:print(json.dumps({'status':'TRANSACTION_ALREADY_RUNNING','provider_calls_executed_by_this_process':0}));return 3
 try:
  pq,etype,client,ps=runtime(c);td=task_data(c,pq);new=0;stop=False;chunk=False
  for u in c['task_units']:
   if stop or chunk:break
   t=td[int(u['future_task'])]
   for i in range(1,N+1):
    sp=a.private_root/'stages'/f'{stage(u,i)}.json'
    if not sp.is_file() and new>=a.max_new_calls:chunk=True;break
    r,isnew=one(client,etype,u,i,t,a.private_root);new+=int(isnew);writej(a.output,report(c,a.private_root,ps,new))
    if isnew:print(json.dumps({'stage':r['stage'],'status':r['status'],'new_calls_this_invocation':new,'total_stages':len(all_rows(c,a.private_root))}),flush=True)
    if r.get('status')!='complete':stop=True;break
  out=report(c,a.private_root,ps,new);writej(a.output,out);print(json.dumps({'status':out['status'],'summary':out['summary'],'decision':out['decision']},indent=2),flush=True);return 2 if stop else 0
 finally:fcntl.flock(fh.fileno(),fcntl.LOCK_UN);fh.close()
if __name__=='__main__':raise SystemExit(main())
