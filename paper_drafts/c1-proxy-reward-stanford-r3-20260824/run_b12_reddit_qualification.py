#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, hashlib, json, os, re
from collections import Counter
from pathlib import Path
from typing import Any

PAPER_ID='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID='D2-PROXY-B12-REDDIT-CROSSDOMAIN-QUALIFICATION'


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode('utf-8')).hexdigest()
def load(p:Path)->dict[str,Any]:
 d=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(d,dict):raise RuntimeError(f'not object:{p}')
 return d
def req(x:bool,msg:str):
 if not x:raise RuntimeError(msg)
def writej(p:Path,d:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');os.replace(t,p)
def norm(t:Any)->str:return ' '.join(str(t or '').split())

def action_summary(trajectory_json:str)->str:
 d=json.loads(trajectory_json);lines=[]
 for step_id,step in sorted((d.get('steps') or {}).items(),key=lambda kv:int(kv[0])):
  output=(step or {}).get('output_messages') or {}; tc=output.get('tool_call_message') or {}; calls=tc.get('tool_calls') or []
  if calls:
   args=calls[0].get('args') or {};cur=args.get('current_state') or {}
   if cur.get('evaluation_previous_goal'):lines.append(f"Step {step_id} evaluation: {norm(cur['evaluation_previous_goal'])[:500]}")
   if cur.get('next_goal'):lines.append(f"Step {step_id} next goal: {norm(cur['next_goal'])[:500]}")
   for a in args.get('action') or []:lines.append(f"Step {step_id} action: {json.dumps(a,ensure_ascii=False,sort_keys=True)[:900]}")
  controller=(step or {}).get('controller_messages') or {}
  for r in controller.get('action_result') or []:
   content=r.get('content') if isinstance(r,dict) else str(r)
   if content:lines.append(f"Step {step_id} result: {norm(content)[:900]}")
  if len(lines)>=36:break
 return '\n'.join(lines)

def released_evidence(trajectory_json:str)->tuple[str,list[str]]:
 d=json.loads(trajectory_json);states=[];hashes=[];seen=set()
 for step_id,step in sorted((d.get('steps') or {}).items(),key=lambda kv:int(kv[0])):
  contents=((step or {}).get('input_messages') or {}).get('contents') or []
  if not contents:continue
  text=str(contents[-1].get('content') or '')
  if '[Current state starts here]' not in text:continue
  cur=text.split('[Current state starts here]',1)[1].strip();h=tsha(cur)
  if h in seen:continue
  seen.add(h);states.append(cur);hashes.append(h)
 return '\n\n--- RELEASED BROWSER STATE ---\n\n'.join(states),hashes

def deterministic_refs(task:dict[str,Any])->dict[str,Any]|None:
 ev=task.get('eval') or {};types=list(ev.get('eval_types') or []);refs=ev.get('reference_answers') or {}
 if types!=['string_match'] or not refs or not set(refs).issubset({'must_include','exact_match'}):return None
 return refs

def select_sources(rows:list[dict[str,Any]], tasks:dict[int,dict[str,Any]], reserved:set[int])->list[dict[str,Any]]:
 selected=[]
 for outcome in (True,False):
  candidates=[]
  for r in rows:
   tid=int(r['task_id'])
   if bool(r['is_successful'])!=outcome or tid in reserved:continue
   task=tasks.get(tid)
   if not task or 'reddit' not in (task.get('sites') or []):continue
   summary=action_summary(str(r.get('trajectory_json') or ''))
   if not summary.strip():continue
   candidates.append({'task_id':tid,'task_prompt':str(r['task_prompt']),'original_outcome':outcome,'intent_template_id':int(task.get('intent_template_id')),'action_summary':summary,'action_summary_sha256':tsha(summary),'action_summary_chars':len(summary)})
  candidates.sort(key=lambda x:x['task_id'])
  chosen=[];seen=set()
  for x in candidates:
   if x['intent_template_id'] in seen:continue
   chosen.append(x);seen.add(x['intent_template_id'])
   if len(chosen)==10:break
  if len(chosen)<10:
   used={x['task_id'] for x in chosen}
   for x in candidates:
    if x['task_id'] in used:continue
    chosen.append(x)
    if len(chosen)==10:break
  req(len(chosen)==10,f'insufficient source candidates for outcome={outcome}')
  selected.extend(chosen)
 return selected

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--csv',required=True,type=Path);a=ap.parse_args();c=load(a.contract)
 req(c.get('paper_id')==PAPER_ID and c.get('experiment_id')==EXPERIMENT_ID and c.get('status')=='FROZEN_BEFORE_QUALIFICATION_COMPUTATION','contract identity drift');req(c.get('provider_calls')==0,'provider-call drift')
 for key in ['reddit_parquet','task_config','runner']:
  row=c['source_bindings'][key];p=Path(row['path']);req(p.is_file() and sha(p)==row['sha256'],f'binding drift:{key}')
 req(Path(c['source_bindings']['runner']['path']).resolve()==Path(__file__).resolve(),'runner path drift');req(sha(Path(__file__))==c['source_bindings']['runner']['sha256'],'runner SHA drift')
 model_dir=Path(c['source_bindings']['reddit_parquet']['path']).parent # overwritten below from exact known model binding lookup
 # Contract stores hashes but not path separately; use the exact B3 materialized model directory as fixed local implementation.
 model_dir=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/exact-minilm-l6-v2')
 for n,h in c['source_bindings']['model_files'].items():req((model_dir/n).exists() and sha(model_dir/n)==h,f'model binding drift:{n}')

 import pyarrow.parquet as pq
 rows=pq.read_table(Path(c['source_bindings']['reddit_parquet']['path'])).to_pylist();req(len(rows)==106,'reddit trajectory geometry drift')
 tasks_all=json.loads(Path(c['source_bindings']['task_config']['path']).read_text(encoding='utf-8'));req(isinstance(tasks_all,list) and len(tasks_all)==812,'task config geometry drift');tasks={int(x['task_id']):x for x in tasks_all}
 reddit_cfg=[x for x in tasks_all if 'reddit' in (x.get('sites') or [])];req(len(reddit_cfg)==129,'reddit task-config geometry drift')
 row_by={int(r['task_id']):r for r in rows}
 reserve={int(x['task_id']) for x in reddit_cfg if list((x.get('eval') or {}).get('eval_types') or [])==['string_match']}
 source=select_sources(rows,tasks,reserve);source_ids=[x['task_id'] for x in source];req(len(source_ids)==20 and len(set(source_ids))==20,'source geometry drift');req(sum(x['original_outcome'] for x in source)==10,'source balance drift')

 os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
 import torch,torch.nn.functional as F
 from transformers import AutoModel,AutoTokenizer
 tok=AutoTokenizer.from_pretrained(model_dir,local_files_only=True);model=AutoModel.from_pretrained(model_dir,local_files_only=True);model.eval()
 def encode(texts:list[str],bs:int=64):
  out=[]
  with torch.no_grad():
   for i in range(0,len(texts),bs):
    b=tok(texts[i:i+bs],padding=True,truncation=True,max_length=256,return_tensors='pt');h=model(**b).last_hidden_state;m=b['attention_mask'].unsqueeze(-1).expand(h.size()).float();e=(h*m).sum(1)/m.sum(1).clamp(min=1e-9);out.append(F.normalize(e,p=2,dim=1).cpu())
  return torch.cat(out,0)
 se=encode([tasks[t]['intent'] for t in source_ids],20);qe=encode([x['intent'] for x in reddit_cfg],64);sims=(qe@se.T).numpy()
 all_rows=[]
 for i,t in enumerate(reddit_cfg):
  tid=int(t['task_id']);vals=[float(v) for v in sims[i]];order=sorted(range(len(source_ids)),key=lambda j:(-vals[j],source_ids[j]));b,s=order[:2];hit=vals[b]>=0.3;traj=row_by.get(tid);refs=deterministic_refs(t);ev='';hashes=[]
  if traj:
   ev,hashes=released_evidence(str(traj['trajectory_json']))
  eligible=bool(tid not in source_ids and hit and traj and ev.strip() and refs)
  all_rows.append({'task_id':tid,'intent':str(t['intent']),'intent_template_id':int(t.get('intent_template_id')),'is_source_task':tid in source_ids,'trajectory_available':bool(traj),'original_outcome':None if not traj else bool(traj['is_successful']),'deterministic_reference_answers':refs,'released_evidence_available':bool(ev.strip()),'released_evidence_sha256':tsha(ev) if ev else None,'released_state_sha256':hashes,'top1_source_task':source_ids[b],'top1_similarity':round(vals[b],8),'runner_up_source_task':source_ids[s],'runner_up_similarity':round(vals[s],8),'top1_margin':round(vals[b]-vals[s],8),'threshold_hit':hit,'offline_eligible_retrieval_hit':eligible})
 eligible=[x for x in all_rows if x['offline_eligible_retrieval_hit']];hit=[x for x in all_rows if not x['is_source_task'] and x['threshold_hit']]
 required=sorted({x['top1_source_task'] for x in eligible});templates=sorted({x['intent_template_id'] for x in eligible});g=c['qualification_gate'];passes={'offline_eligible_retrieval_hits':len(eligible)>=g['minimum_offline_eligible_retrieval_hits'],'eligible_intent_templates':len(templates)>=g['minimum_eligible_intent_templates'],'distinct_selected_source_tasks':len(required)>=g['minimum_distinct_selected_source_tasks'],'required_source_writer_pairs_cost':len(required)<=g['maximum_required_source_writer_pairs_for_followup']};qualified=all(passes.values())
 result={'schema_version':'1.0','paper_id':PAPER_ID,'experiment_id':EXPERIMENT_ID,'status':'B12_REDDIT_QUALIFIED_FOR_FROZEN_FOLLOWUP' if qualified else 'B12_REDDIT_SUPPORT_STOP','contract_sha256':c['contract_sha256'],'contract_file_sha256':sha(a.contract),'provider_calls':0,'new_rollouts':0,'source_selection':[{k:v for k,v in x.items() if k!='action_summary'} for x in source],'summary':{'reddit_config_tasks':len(reddit_cfg),'reddit_trajectory_tasks':len(rows),'source_descriptions':20,'source_outcome_balance':{'successful':10,'failed':10},'source_intent_templates':len({x['intent_template_id'] for x in source}),'heldout_threshold_hits':len(hit),'offline_deterministic_string_match_tasks':sum(deterministic_refs(x) is not None for x in reddit_cfg),'offline_eligible_retrieval_hits':len(eligible),'eligible_intent_templates':len(templates),'distinct_selected_source_tasks':len(required),'required_source_writer_tasks':required,'qualification_checks':passes,'qualification_pass':qualified,'projected_followup_writer_calls':2*len(required),'projected_followup_terminal_calls':8*len(eligible),'projected_followup_provider_calls_total':2*len(required)+8*len(eligible)},'eligible_future_support':eligible,'all_reddit_retrieval_rows':all_rows,'decision':'AUTHORIZE_PER_EXPERIMENT_FROZEN_B12_WRITER_CONTRACT' if qualified else 'STOP_NO_PROVIDER_CALLS','interpretation':'Support qualification only. Passing permits a separately frozen paired-writer/native-terminal subcontract; it is not evidence for cross-domain write or transport effects. A support STOP is not a scientific null.','authority':{'scientific_authority':False,'experiment_authority':True,'provider_call_authority':False,'claim_expansion_authority':False,'submission_authority':False}}
 writej(a.output,result)
 a.csv.parent.mkdir(parents=True,exist_ok=True)
 with a.csv.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['task_id','intent_template_id','trajectory_available','original_outcome','top1_source_task','top1_similarity','runner_up_source_task','runner_up_similarity','top1_margin','threshold_hit','offline_eligible_retrieval_hit']);w.writeheader();w.writerows([{k:x.get(k) for k in w.fieldnames} for x in all_rows])
 print(json.dumps({'status':result['status'],'summary':result['summary'],'eligible_future_support':eligible,'provider_calls':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
