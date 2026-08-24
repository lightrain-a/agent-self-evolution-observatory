#!/usr/bin/env python3
from __future__ import annotations
import argparse, fcntl, hashlib, json, math, os, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

MODEL='doubao-seed-2.0-mini'; RESOLVED='doubao-seed-2-0-mini-260215'; BASE_URL='https://ark.cn-beijing.volces.com/api/plan/v3'; TOTAL=288; N=4

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def load(p:Path):
 d=json.loads(p.read_text());
 if not isinstance(d,dict):raise RuntimeError(f'JSON root not object:{p}')
 return d
def writej(p:Path,d):p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,ensure_ascii=False,sort_keys=True)+'\n');os.replace(t,p)
def req(x,msg):
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
  vals=list(refs['must_include']);out=[]
  for ref in vals:
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
def prompt(task:str,ev:str,wrapper:str)->str:
 return f"""{wrapper.rstrip()}

You are answering a WebArena read-only benchmark task from a frozen released evidence packet.

RULES:
- Treat the memory above as procedural guidance from a past task, not task-specific ground truth.
- Use only the RELEASED BROWSER EVIDENCE below as factual evidence for the current task.
- Do not invent names, prices, order values, product facts, ratings, or quotes absent from the evidence.
- Return only the final answer to the benchmark task. Do not return JSON, browser actions, analysis, or commentary.

BENCHMARK TASK:
{task}

RELEASED BROWSER EVIDENCE:
{ev}

FINAL ANSWER:"""
def stage(u:dict[str,Any],cond:str,i:int)->str:return f"terminal-{u['future_task']}-source-{u['selected_source_task']}-{cond}-r{i}"

def validate(cp:Path,c:dict[str,Any]):
 req(c.get('status')=='FROZEN_BEFORE_PROVIDER_CALLS' and c.get('experiment_id')=='D2-PROXY-B4-RETRIEVAL-MATCHED-FIXED-EVIDENCE','contract identity drift');req(c.get('future_task_count')==36 and len(c.get('task_units') or [])==36,'future support drift');req(c.get('expected_provider_calls')==TOTAL and c.get('rollouts_per_task_per_condition')==N and c.get('conditions')==['success','failure'],'geometry drift')
 m=c['model'];req(m['requested']==MODEL and m['expected_resolved']==RESOLVED and m['temperature']==0.2 and m['max_output_tokens']==900 and m['thinking']=='disabled' and m['provider_retries']==0 and m['substitution_allowed'] is False,'model drift');g=c['primary_gate'];req(g['min_mean_absolute_success_rate_difference']==0.15 and g['permutation_p_lt']==0.05 and g['permutation_repetitions']==100000 and g['permutation_seed']==20260824,'gate drift');miss=c['missingness_policy'];req(miss['provider_retries']==0 and miss['stop_after_first_no_text_provider_failure'] is True and miss['top_up_failed_units'] is False and miss['replace_future_tasks'] is False,'missingness drift');a=c['authority'];req(a['experiment_authority'] is True and a['provider_call_authority'] is True and a['claim_expansion_authority'] is False and a['submission_authority'] is False,'authority drift')
 for row in list(c['source_artifacts'].values())+[c['b3'],c['memory_manifest'],c['human_authority']]:
  p=Path(row['path']);req(p.is_file() and sha(p)==row['sha256'],f'source drift:{p}')
 r=c['code']['runner'];req(Path(r['path']).resolve()==Path(__file__).resolve() and sha(Path(__file__))==r['sha256'],'runner SHA drift')
 for u in c['task_units']:
  for cond in c['conditions']:
   w=u['memory_wrappers'][cond];p=Path(w['path']);req(p.is_file() and sha(p)==w['sha256'],f'wrapper drift:{u["future_task"]}/{cond}')

def runtime(c):
 root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root));sys.path.insert(0,str(Path(c['vendor_path'])))
 import pyarrow.parquet as pq
 from research_pipeline.config import load_env_file
 from research_pipeline.ark_provider import ArkResponseStateError,ArkResponsesClient,ArkSettings
 load_env_file(Path(c['provider_env_file']));base=ArkSettings.from_env();req(bool(base.api_key),'credential absent');req(base.base_url==BASE_URL,'base URL drift');cfg=ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=180.0,max_retries=0);return pq,ArkResponseStateError,ArkResponsesClient(cfg),cfg.safe_summary()
def task_data(c,pq):
 par=Path(c['source_artifacts']['parquet']['path']);rows={int(x['task_id']):x for x in pq.read_table(par,columns=['task_id','trajectory_json']).to_pylist()};out={}
 for u in c['task_units']:
  tid=int(u['future_task']);req(tid in rows,f'trajectory missing:{tid}');ev,hs=evidence(str(rows[tid]['trajectory_json']));req(tsha(ev)==u['evidence_sha256'] and hs==u['released_state_sha256'],f'evidence drift:{tid}');out[tid]={'task_prompt':u['task_prompt'],'evidence':ev,'refs':u['reference_answers']}
 return out
def one(client,error_type,u,cond,i,t,root):
 st=stage(u,cond,i);sp=root/'stages'/f'{st}.json'
 if sp.is_file():return load(sp),False
 wrapper=Path(u['memory_wrappers'][cond]['path']).read_text();pr=prompt(t['task_prompt'],t['evidence'],wrapper);base={'stage':st,'future_task':u['future_task'],'selected_source_task':u['selected_source_task'],'condition':cond,'rollout':i,'prompt_sha256':tsha(pr),'requested_model':MODEL}
 try:
  r=client.respond(pr,model=MODEL,max_output_tokens=900,temperature=0.2,thinking='disabled',store=True,allow_thinking_compatibility_fallback=False);ans=str(r.get('text') or '').strip();writej(root/'provider-responses'/f'{st}.json',{**base,'response_id':r.get('response_id'),'provider_status':r.get('status'),'requested_model_returned':r.get('requested_model'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'answer':ans,'answer_sha256':tsha(ans) if ans else '','thinking_compatibility_fallback':r.get('thinking_compatibility_fallback')});req(str(r.get('requested_model'))==MODEL and str(r.get('resolved_model'))==RESOLVED,'model resolution drift');req(r.get('thinking_compatibility_fallback') is False,'thinking fallback');req(bool(ans),'no assistant text');sc,checks=score(ans,t['refs']);row={**base,'status':'complete','provider_status':r.get('status'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'answer_sha256':tsha(ans),'benchmark_score':sc,'evaluator_checks':checks}
 except error_type as e:row={**base,'status':'provider_state_failure_no_text','error_type':type(e).__name__,'provider_receipt':e.receipt()}
 except Exception as e:row={**base,'status':'provider_or_runtime_failure','error_type':type(e).__name__,'error':str(e)[:1000]}
 writej(sp,row);return row,True
def all_rows(c,root):
 out=[]
 for u in c['task_units']:
  for cond in c['conditions']:
   for i in range(1,N+1):
    p=root/'stages'/f'{stage(u,cond,i)}.json'
    if p.is_file():out.append(load(p))
 return out
def pearson(xs,ys):
 n=len(xs)
 if n<2:return None
 mx=sum(xs)/n;my=sum(ys)/n;dx=[x-mx for x in xs];dy=[y-my for y in ys];den=math.sqrt(sum(x*x for x in dx)*sum(y*y for y in dy));return None if den==0 else sum(x*y for x,y in zip(dx,dy))/den
def stats(c,rows):
 cells=[]
 umap={int(u['future_task']):u for u in c['task_units']}
 for u in c['task_units']:
  tid=int(u['future_task']);a=[float(r['benchmark_score']) for r in rows if int(r['future_task'])==tid and r['condition']=='success' and r['status']=='complete'];b=[float(r['benchmark_score']) for r in rows if int(r['future_task'])==tid and r['condition']=='failure' and r['status']=='complete'];req(len(a)==N and len(b)==N,f'incomplete cell:{tid}');pa=sum(a)/N;pb=sum(b)/N;cells.append({'future_task':tid,'selected_source_task':int(u['selected_source_task']),'intent_template_id':u['intent_template_id'],'retrieval_similarity':u['retrieval_similarity'],'retrieval_margin':u['retrieval_margin'],'success_memory_rate':round(pa,6),'failure_memory_rate':round(pb,6),'absolute_rate_difference':round(abs(pb-pa),6),'signed_failure_minus_success':round(pb-pa,6)})
 obs=sum(x['absolute_rate_difference'] for x in cells)/len(cells);signed=sum(x['signed_failure_minus_success'] for x in cells)/len(cells);return obs,signed,cells
def perm(c,rows,observed):
 rng=random.Random(20260824);pools=[]
 for u in c['task_units']:
  tid=int(u['future_task']);a=[float(r['benchmark_score']) for r in rows if int(r['future_task'])==tid and r['condition']=='success'];b=[float(r['benchmark_score']) for r in rows if int(r['future_task'])==tid and r['condition']=='failure'];pools.append(a+b)
 ge=0
 for _ in range(100000):
  vals=[]
  for pool in pools:
   z=list(pool);rng.shuffle(z);vals.append(abs(sum(z[:N])/N-sum(z[N:])/N))
  if sum(vals)/len(vals)>=observed-1e-12:ge+=1
 return (ge+1)/100001
def report(c,root,provider,new_calls):
 rows=all_rows(c,root);fail=[r for r in rows if r.get('status')!='complete'];full=len(rows)==TOTAL and not fail;obs=pv=signed=None;cells=[];gate=False;secondary={}
 if full:
  obs,signed,cells=stats(c,rows);pv=perm(c,rows,obs);gate=obs>=0.15 and pv<0.05;by_source=defaultdict(list);by_template=defaultdict(list)
  for x in cells:by_source[str(x['selected_source_task'])].append(x['absolute_rate_difference']);by_template[str(x['intent_template_id'])].append(x['absolute_rate_difference'])
  secondary={'zero_cells':sum(x['absolute_rate_difference']==0 for x in cells),'positive_signed_cells':sum(x['signed_failure_minus_success']>0 for x in cells),'negative_signed_cells':sum(x['signed_failure_minus_success']<0 for x in cells),'by_source_mean_absolute_effect':{k:round(sum(v)/len(v),6) for k,v in sorted(by_source.items())},'by_template_mean_absolute_effect':{k:round(sum(v)/len(v),6) for k,v in sorted(by_template.items())},'pearson_retrieval_similarity_vs_absolute_effect':pearson([float(x['retrieval_similarity']) for x in cells],[float(x['absolute_rate_difference']) for x in cells])}
 decision='SUPPORT_RETRIEVAL_MATCHED_FIXED_EVIDENCE_TRANSPORT' if gate else ('RETRIEVAL_MATCHED_TRANSPORT_NOT_ESTABLISHED' if full else 'B4_INCOMPLETE_NO_SCIENTIFIC_VERDICT')
 return {'schema_version':'1.0','experiment_id':c['experiment_id'],'paper_id':c['paper_id'],'status':'B4_EXECUTION_COMPLETE' if full else 'B4_EXECUTION_PARTIAL','contract_sha256':c['contract_sha256'],'provider':provider,'summary':{'provider_calls_expected':TOTAL,'provider_calls_attempted_total':len(rows),'provider_calls_complete':sum(r.get('status')=='complete' for r in rows),'provider_failures':len(fail),'new_provider_calls_this_invocation':new_calls,'future_tasks':36,'rollouts_per_task_per_condition':N,'observed_mean_absolute_success_rate_difference':None if obs is None else round(obs,6),'mean_signed_failure_minus_success':None if signed is None else round(signed,6),'permutation_p_ge_observed':None if pv is None else round(pv,6),'practical_effect_floor':0.15,'breadth_gate_pass':gate},'secondary':secondary,'cell_results':cells,'rollouts':[{k:r.get(k) for k in ('future_task','selected_source_task','condition','rollout','answer_sha256','benchmark_score','provider_status','resolved_model','usage')} for r in rows if r.get('status')=='complete'],'failures':[{k:r.get(k) for k in ('future_task','selected_source_task','condition','rollout','stage','status','error_type','provider_receipt','error')} for r in fail],'decision':decision,'scope_boundary':c['scope_boundary'],'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--private-root',required=True,type=Path);ap.add_argument('--max-new-calls',type=int,default=72);a=ap.parse_args();c=load(a.contract);validate(a.contract,c);req(1<=a.max_new_calls<=TOTAL,'invalid chunk limit');a.private_root.mkdir(parents=True,exist_ok=True);fh=(a.private_root/'transaction.lock').open('a+')
 try:fcntl.flock(fh.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:print(json.dumps({'status':'TRANSACTION_ALREADY_RUNNING','provider_calls_executed_by_this_process':0}));return 3
 try:
  pq,etype,client,ps=runtime(c);td=task_data(c,pq);new=0;stop=False;chunk=False
  for u in c['task_units']:
   if stop or chunk:break
   t=td[int(u['future_task'])]
   for cond in c['conditions']:
    if stop or chunk:break
    for i in range(1,N+1):
     sp=a.private_root/'stages'/f'{stage(u,cond,i)}.json'
     if not sp.is_file() and new>=a.max_new_calls:chunk=True;break
     r,isnew=one(client,etype,u,cond,i,t,a.private_root);new+=int(isnew);writej(a.output,report(c,a.private_root,ps,new))
     if isnew and (new%16==0 or r.get('status')!='complete'):print(json.dumps({'stage':r['stage'],'status':r['status'],'new_calls_this_invocation':new,'total_stages':len(all_rows(c,a.private_root))}),flush=True)
     if r.get('status')!='complete':stop=True;break
  out=report(c,a.private_root,ps,new);writej(a.output,out);print(json.dumps({'status':out['status'],'summary':out['summary'],'decision':out['decision']},indent=2),flush=True);return 2 if stop else 0
 finally:fcntl.flock(fh.fileno(),fcntl.LOCK_UN);fh.close()
if __name__=='__main__':raise SystemExit(main())
