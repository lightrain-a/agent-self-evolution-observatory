#!/usr/bin/env python3
from __future__ import annotations
import argparse, fcntl, hashlib, json, os, random, re, sys
from collections import Counter
from pathlib import Path
from typing import Any
MODEL='doubao-seed-2.0-mini';RESOLVED='doubao-seed-2-0-mini-260215';BASE_URL='https://ark.cn-beijing.volces.com/api/plan/v3';TOTAL=144;N=4

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def load(p:Path):
 d=json.loads(p.read_text());
 if not isinstance(d,dict):raise RuntimeError('JSON root not object')
 return d
def writej(p:Path,d):p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,ensure_ascii=False,sort_keys=True)+'\n');os.replace(t,p)
def req(x,msg):
 if not x:raise RuntimeError(msg)
def clean(a:str|None)->str:
 a=str(a or '').strip()
 if len(a)>=2 and a[0]==a[-1] and a[0] in "'\"":a=a[1:-1]
 return re.sub(r'(\w+)[\u2010-\u2015\u2212-](\w+)',r'\1-\2',a).lower()
def score(pred,refs):
 p=clean(pred);s=1.0;checks={}
 if 'exact_match' in refs:
  ref=str(refs['exact_match']);v=float(p==clean(ref));s*=v;checks['exact_match']={'ref':ref,'score':v}
 if 'must_include' in refs:
  out=[]
  for ref in refs['must_include']:
   v=float(clean(str(ref)) in p);s*=v;out.append({'ref':str(ref),'score':v})
  checks['must_include']=out
 return s,checks
def evidence(traj_json):
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
def prompt(task,ev):
 return f"""You are answering a WebArena read-only benchmark task from a frozen released evidence packet.

RULES:
- No reusable memory is supplied.
- Use only the RELEASED BROWSER EVIDENCE below as factual evidence for the current task.
- Do not invent names, prices, order values, product facts, ratings, or quotes absent from the evidence.
- Return only the final answer to the benchmark task. Do not return JSON, browser actions, analysis, or commentary.

BENCHMARK TASK:
{task}

RELEASED BROWSER EVIDENCE:
{ev}

FINAL ANSWER:"""
def stage(tid,i):return f'nomem-{tid}-r{i}'
def validate(c):
 req(c['status']=='FROZEN_BEFORE_PROVIDER_CALLS' and c['future_task_count']==36 and c['expected_provider_calls']==TOTAL,'contract identity/geometry drift');m=c['model'];req(m['requested']==MODEL and m['expected_resolved']==RESOLVED and m['temperature']==0.2 and m['max_output_tokens']==900 and m['thinking']=='disabled' and m['provider_retries']==0,'model drift');g=c['primary_gate'];req(g['min_mean_absolute_memory_presence_effect']==0.15 and g['omnibus_permutation_p_lt']==0.05 and g['permutation_repetitions']==100000,'gate drift');req(load(Path(c['b4_result']['path']))['decision']=='RETRIEVAL_MATCHED_TRANSPORT_NOT_ESTABLISHED','B4 negative boundary missing');a=c['authority'];req(a['provider_call_authority'] and a['experiment_authority'] and not a['claim_expansion_authority'],'authority drift');
 for r in list(c['source_artifacts'].values())+[c['b4_contract'],c['b4_result'],c['human_authority']]:
  p=Path(r['path']);req(p.is_file() and sha(p)==r['sha256'],f'source drift:{p}')
 rr=c['code']['runner'];req(Path(rr['path']).resolve()==Path(__file__).resolve() and sha(Path(__file__))==rr['sha256'],'runner drift')
def runtime(c):
 root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root));sys.path.insert(0,str(Path(c['vendor_path'])));import pyarrow.parquet as pq
 from research_pipeline.config import load_env_file
 from research_pipeline.ark_provider import ArkResponseStateError,ArkResponsesClient,ArkSettings
 load_env_file(Path(c['provider_env_file']));base=ArkSettings.from_env();req(bool(base.api_key) and base.base_url==BASE_URL,'provider config drift');cfg=ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=180.0,max_retries=0);return pq,ArkResponseStateError,ArkResponsesClient(cfg),cfg.safe_summary()
def data(c,pq):
 rows={int(x['task_id']):x for x in pq.read_table(Path(c['source_artifacts']['parquet']['path']),columns=['task_id','trajectory_json']).to_pylist()};out={}
 for u in c['task_units']:
  tid=int(u['future_task']);ev,hs=evidence(str(rows[tid]['trajectory_json']));req(tsha(ev)==u['evidence_sha256'] and hs==u['released_state_sha256'],f'evidence drift:{tid}');out[tid]={'task_prompt':u['task_prompt'],'evidence':ev,'refs':u['reference_answers']}
 return out
def one(client,error_type,u,i,t,root):
 st=stage(u['future_task'],i);sp=root/'stages'/f'{st}.json'
 if sp.is_file():return load(sp),False
 pr=prompt(t['task_prompt'],t['evidence']);base={'stage':st,'future_task':u['future_task'],'selected_source_task':u['selected_source_task'],'condition':'no_memory','rollout':i,'prompt_sha256':tsha(pr),'requested_model':MODEL}
 try:
  r=client.respond(pr,model=MODEL,max_output_tokens=900,temperature=0.2,thinking='disabled',store=True,allow_thinking_compatibility_fallback=False);ans=str(r.get('text') or '').strip();writej(root/'provider-responses'/f'{st}.json',{**base,'response_id':r.get('response_id'),'provider_status':r.get('status'),'requested_model_returned':r.get('requested_model'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'answer':ans,'answer_sha256':tsha(ans) if ans else '','thinking_compatibility_fallback':r.get('thinking_compatibility_fallback')});req(str(r.get('requested_model'))==MODEL and str(r.get('resolved_model'))==RESOLVED,'model resolution drift');req(r.get('thinking_compatibility_fallback') is False and bool(ans),'empty/fallback response');sc,checks=score(ans,t['refs']);row={**base,'status':'complete','provider_status':r.get('status'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'answer_sha256':tsha(ans),'benchmark_score':sc,'evaluator_checks':checks}
 except error_type as e:row={**base,'status':'provider_state_failure_no_text','error_type':type(e).__name__,'provider_receipt':e.receipt()}
 except Exception as e:row={**base,'status':'provider_or_runtime_failure','error_type':type(e).__name__,'error':str(e)[:1000]}
 writej(sp,row);return row,True
def all_rows(c,root):
 out=[]
 for u in c['task_units']:
  for i in range(1,N+1):
   p=root/'stages'/f'{stage(u["future_task"],i)}.json'
   if p.is_file():out.append(load(p))
 return out
def combined(c,nrows):
 b4=load(Path(c['b4_result']['path']));br=b4['rollouts'];cells=[]
 for u in c['task_units']:
  tid=int(u['future_task']);s=[float(x['benchmark_score']) for x in br if int(x['future_task'])==tid and x['condition']=='success'];f=[float(x['benchmark_score']) for x in br if int(x['future_task'])==tid and x['condition']=='failure'];n=[float(x['benchmark_score']) for x in nrows if int(x['future_task'])==tid];req(len(s)==len(f)==len(n)==N,f'arm count drift:{tid}');ps,pf,p0=sum(s)/N,sum(f)/N,sum(n)/N;ds=ps-p0;df=pf-p0
  geom='EQUIDISTANT' if abs(ds)==abs(df) else ('CLOSER_TO_SUCCESS' if abs(ds)<abs(df) else 'CLOSER_TO_FAILURE')
  cells.append({'future_task':tid,'selected_source_task':u['selected_source_task'],'intent_template_id':u['intent_template_id'],'success_memory_rate':round(ps,6),'failure_memory_rate':round(pf,6),'no_memory_rate':round(p0,6),'success_minus_no_memory':round(ds,6),'failure_minus_no_memory':round(df,6),'mean_absolute_memory_presence_effect':round((abs(ds)+abs(df))/2,6),'no_memory_geometry':geom})
 obs=sum(x['mean_absolute_memory_presence_effect'] for x in cells)/len(cells);return obs,cells
def perm(c,nrows,obs):
 b4=load(Path(c['b4_result']['path']));br=b4['rollouts'];pools=[]
 for u in c['task_units']:
  tid=int(u['future_task']);s=[float(x['benchmark_score']) for x in br if int(x['future_task'])==tid and x['condition']=='success'];f=[float(x['benchmark_score']) for x in br if int(x['future_task'])==tid and x['condition']=='failure'];n=[float(x['benchmark_score']) for x in nrows if int(x['future_task'])==tid];pools.append(s+f+n)
 rng=random.Random(20260824);ge=0
 for _ in range(100000):
  vals=[]
  for pool in pools:
   z=list(pool);rng.shuffle(z);ps=sum(z[:4])/4;pf=sum(z[4:8])/4;p0=sum(z[8:])/4;vals.append((abs(ps-p0)+abs(pf-p0))/2)
  if sum(vals)/len(vals)>=obs-1e-12:ge+=1
 return (ge+1)/100001
def report(c,root,provider,new):
 rows=all_rows(c,root);fail=[x for x in rows if x.get('status')!='complete'];full=len(rows)==TOTAL and not fail;obs=pv=None;cells=[];gate=False;geo={}
 if full:
  obs,cells=combined(c,rows);pv=perm(c,rows,obs);gate=obs>=0.15 and pv<0.05;geo=dict(Counter(x['no_memory_geometry'] for x in cells))
 decision='SUPPORT_NATIVE_MEMORY_PRESENCE_EFFECT' if gate else ('NATIVE_MEMORY_PRESENCE_EFFECT_NOT_ESTABLISHED' if full else 'B5_INCOMPLETE_NO_SCIENTIFIC_VERDICT')
 return {'schema_version':'1.0','experiment_id':c['experiment_id'],'paper_id':c['paper_id'],'status':'B5_EXECUTION_COMPLETE' if full else 'B5_EXECUTION_PARTIAL','contract_sha256':c['contract_sha256'],'provider':provider,'summary':{'provider_calls_expected':TOTAL,'provider_calls_attempted_total':len(rows),'provider_calls_complete':sum(x.get('status')=='complete' for x in rows),'provider_failures':len(fail),'new_provider_calls_this_invocation':new,'future_tasks':36,'observed_mean_absolute_memory_presence_effect':None if obs is None else round(obs,6),'omnibus_permutation_p_ge_observed':None if pv is None else round(pv,6),'practical_effect_floor':0.15,'memory_presence_gate_pass':gate,'geometry_counts':geo},'cell_results':cells,'rollouts':[{k:x.get(k) for k in ('future_task','selected_source_task','condition','rollout','answer_sha256','benchmark_score','provider_status','resolved_model','usage')} for x in rows if x.get('status')=='complete'],'failures':[{k:x.get(k) for k in ('future_task','selected_source_task','condition','rollout','stage','status','error_type','provider_receipt','error')} for x in fail],'decision':decision,'scope_boundary':c['scope_boundary'],'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--private-root',required=True,type=Path);ap.add_argument('--max-new-calls',type=int,default=72);a=ap.parse_args();c=load(a.contract);validate(c);a.private_root.mkdir(parents=True,exist_ok=True);fh=(a.private_root/'transaction.lock').open('a+')
 try:fcntl.flock(fh.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:print(json.dumps({'status':'TRANSACTION_ALREADY_RUNNING','provider_calls_executed_by_this_process':0}));return 3
 try:
  pq,etype,client,ps=runtime(c);td=data(c,pq);new=0;stop=False;chunk=False
  for u in c['task_units']:
   if stop or chunk:break
   t=td[int(u['future_task'])]
   for i in range(1,N+1):
    sp=a.private_root/'stages'/f'{stage(u["future_task"],i)}.json'
    if not sp.is_file() and new>=a.max_new_calls:chunk=True;break
    r,isnew=one(client,etype,u,i,t,a.private_root);new+=int(isnew);writej(a.output,report(c,a.private_root,ps,new))
    if isnew and (new%16==0 or r.get('status')!='complete'):print(json.dumps({'stage':r['stage'],'status':r['status'],'new_calls_this_invocation':new,'total_stages':len(all_rows(c,a.private_root))}),flush=True)
    if r.get('status')!='complete':stop=True;break
  out=report(c,a.private_root,ps,new);writej(a.output,out);print(json.dumps({'status':out['status'],'summary':out['summary'],'decision':out['decision']},indent=2));return 2 if stop else 0
 finally:fcntl.flock(fh.fileno(),fcntl.LOCK_UN);fh.close()
if __name__=='__main__':raise SystemExit(main())
