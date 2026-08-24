#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,fcntl,hashlib,json,os,random,re,sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PAPER='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE';EXP='D2-PROXY-B12-REDDIT-CROSSDOMAIN-REPLICATION';BASE='https://ark.cn-beijing.volces.com/api/plan/v3'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode('utf-8')).hexdigest()
def jsha(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(p:Path)->dict[str,Any]:
 d=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(d,dict):raise RuntimeError(f'not object:{p}')
 return d
def writej(p:Path,d:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');os.replace(t,p)
def req(x:bool,m:str):
 if not x:raise RuntimeError(m)
def norm(t:Any)->str:return ' '.join(str(t or '').split())
def clean(a:str|None)->str:
 a=str(a or '').strip()
 if len(a)>=2 and a[0]==a[-1] and a[0] in "'\"":a=a[1:-1]
 return re.sub(r'(\w+)[\u2010-\u2015\u2212-](\w+)',r'\1-\2',a).lower()
def tokens(s:str)->set[str]:return set(re.findall(r'[a-z0-9]+',str(s).lower()))
def jaccard_distance(a:str,b:str)->float:
 x,y=tokens(a),tokens(b)
 return 0.0 if not x and not y else 1.0-len(x&y)/len(x|y)
def action_summary(s:str)->str:
 d=json.loads(s);lines=[]
 for sid,step in sorted((d.get('steps') or {}).items(),key=lambda kv:int(kv[0])):
  out=(step or {}).get('output_messages') or {};calls=(out.get('tool_call_message') or {}).get('tool_calls') or []
  if calls:
   args=calls[0].get('args') or {};cur=args.get('current_state') or {}
   if cur.get('evaluation_previous_goal'):lines.append(f"Step {sid} evaluation: {norm(cur['evaluation_previous_goal'])[:500]}")
   if cur.get('next_goal'):lines.append(f"Step {sid} next goal: {norm(cur['next_goal'])[:500]}")
   for a in args.get('action') or []:lines.append(f"Step {sid} action: {json.dumps(a,ensure_ascii=False,sort_keys=True)[:900]}")
  ctr=(step or {}).get('controller_messages') or {}
  for r in ctr.get('action_result') or []:
   content=r.get('content') if isinstance(r,dict) else str(r)
   if content:lines.append(f"Step {sid} result: {norm(content)[:900]}")
  if len(lines)>=36:break
 return '\n'.join(lines)
def evidence(s:str)->tuple[str,list[str]]:
 d=json.loads(s);states=[];hs=[];seen=set()
 for sid,step in sorted((d.get('steps') or {}).items(),key=lambda kv:int(kv[0])):
  c=((step or {}).get('input_messages') or {}).get('contents') or []
  if not c:continue
  text=str(c[-1].get('content') or '')
  if '[Current state starts here]' not in text:continue
  cur=text.split('[Current state starts here]',1)[1].strip();h=tsha(cur)
  if h in seen:continue
  seen.add(h);states.append(cur);hs.append(h)
 return '\n\n--- RELEASED BROWSER STATE ---\n\n'.join(states),hs
def writer_prompt(system_prompt:str,task:str,trajectory:str)->str:return f"""{system_prompt.strip()}\n\nTask: {task}\n\nTrajectory:\n{trajectory}\n\nCreate memory items for the task above. Return only the requested Markdown memory-item format."""
def parse_items(text:str)->list[dict[str,str]]:
 blocks=re.split(r'(?m)^# Memory Item \d+\s*$',str(text or ''));out=[]
 for b in blocks:
  if not b.strip():continue
  a=re.search(r'(?m)^## Title:\s*(.+?)\s*$',b);d=re.search(r'(?m)^## Description:\s*(.+?)\s*$',b);c=re.search(r'(?ms)^## Content:\s*(.+?)\s*$',b)
  if a and d and c:out.append({'title':a.group(1).strip(),'description':d.group(1).strip(),'content':c.group(1).strip()})
 return out
def wrapper(task:str,items:list[dict[str,str]])->str:
 text='\nBelow are some memory items that I accumulated from past interaction from the environment that may be helpful to solve the task. You can use it when you feel it\'s relevant.\n\n'
 text+=f'[Retrieved from past task: "{task}"]\n'
 for x in items:text+=f"Title: {x['title']}\nDescription: {x['description']}\nContent: {x['content']}\n\n"
 return text
def terminal_prompt(task:str,ev:str,mem:str)->str:return f"""{mem.rstrip()}

You are answering a WebArena read-only benchmark task from a frozen released evidence packet.

RULES:
- Treat the memory above as procedural guidance from a past task, not task-specific ground truth.
- Use only the RELEASED BROWSER EVIDENCE below as factual evidence for the current task.
- Do not invent names, URLs, counts, quotes, or facts absent from the released browser evidence.
- Return only the final answer to the benchmark task. Do not return JSON, browser actions, analysis, or commentary.

BENCHMARK TASK:
{task}

RELEASED BROWSER EVIDENCE:
{ev}

FINAL ANSWER:"""
def score(pred:str,refs:dict[str,Any])->tuple[float,dict[str,Any]]:
 p=clean(pred);s=1.0;checks={}
 if 'exact_match' in refs:
  ref=str(refs['exact_match']);v=float(p==clean(ref));s*=v;checks['exact_match']={'ref':ref,'score':v}
 if 'must_include' in refs:
  out=[]
  for ref in refs['must_include']:
   v=float(clean(str(ref)) in p);s*=v;out.append({'ref':str(ref),'score':v})
  checks['must_include']=out
 return s,checks
def normalized_model(s:str)->str:return re.sub(r'[^a-z0-9]','',str(s or '').lower())

def validate(c:dict[str,Any]):
 req(c.get('paper_id')==PAPER and c.get('experiment_id')==EXP and c.get('status')=='FROZEN_BEFORE_ANY_B12_PROVIDER_CALLS','contract identity drift');req(c['program_budget']['total_provider_call_ceiling']==72,'budget drift');req(c['writer_stage']['expected_provider_calls']==8 and c['terminal_stage']['expected_provider_calls']==64,'geometry drift');req(len(c['writer_stage']['source_units'])==4 and len(c['terminal_stage']['task_units'])==8,'support drift');g=c['terminal_stage']['primary_gate'];req(g['min_mean_absolute_success_rate_difference']==0.15 and g['permutation_p_lt']==0.05 and g['permutation_repetitions']==100000 and g['permutation_seed']==20260824,'gate drift');a=c['authority'];req(a['provider_call_authority'] is True and a['experiment_authority'] is True and a['claim_expansion_authority'] is False and a['submission_authority'] is False,'authority drift')
 for key,row in c['source_bindings'].items():
  p=Path(row['path']);req(p.is_file() and sha(p)==row['sha256'],f'source drift:{key}')
 req(Path(c['source_bindings']['runner']['path']).resolve()==Path(__file__).resolve(),'runner path drift');req(sha(Path(__file__))==c['source_bindings']['runner']['sha256'],'runner SHA drift');q=Path(c['qualification_binding']['path']);req(q.is_file() and sha(q)==c['qualification_binding']['sha256'],'qualification drift')
 for cond in ['success','failure']:
  row=c['writer_stage'][f'{cond}_prompt'];p=Path(row['path']);req(p.is_file() and sha(p)==row['sha256'],f'{cond} prompt drift')

def runtime(c):
 root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root));sys.path.insert(0,str(Path(c['vendor_path'])))
 import pyarrow.parquet as pq
 from research_pipeline.config import load_env_file
 from research_pipeline.ark_provider import ArkResponseStateError,ArkResponsesClient,ArkSettings
 load_env_file(Path(c['provider_env_file']));base=ArkSettings.from_env();req(bool(base.api_key),'credential absent');req(base.base_url==BASE,'base URL drift');cfg=ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=180.0,max_retries=0);return pq,ArkResponseStateError,ArkResponsesClient(cfg),cfg.safe_summary()
def load_data(c,pq):
 rows={int(x['task_id']):x for x in pq.read_table(Path(c['source_bindings']['reddit_parquet']['path']),columns=['task_id','task_prompt','trajectory_json']).to_pylist()};src={};future={}
 for u in c['writer_stage']['source_units']:
  tid=int(u['source_task']);req(tid in rows,f'source missing:{tid}');summary=action_summary(str(rows[tid]['trajectory_json']));req(tsha(summary)==u['action_summary_sha256'],f'source summary drift:{tid}');src[tid]={'task_prompt':str(rows[tid]['task_prompt']),'summary':summary}
 for u in c['terminal_stage']['task_units']:
  tid=int(u['future_task']);req(tid in rows,f'future missing:{tid}');ev,hs=evidence(str(rows[tid]['trajectory_json']));req(tsha(ev)==u['evidence_sha256'] and hs==u['released_state_sha256'],f'future evidence drift:{tid}');future[tid]={'task_prompt':u['task_prompt'],'evidence':ev,'refs':u['reference_answers']}
 return src,future
def writer_stage_name(tid:int,cond:str)->str:return f'reddit-writer-{tid}-{cond}'
def terminal_stage_name(tid:int,src:int,cond:str,r:int)->str:return f'reddit-terminal-{tid}-source-{src}-{cond}-r{r}'
def archive_text(root:Path,text:str)->str:
 h=tsha(text);p=root/'raw'/h[:2]/f'{h}.txt';p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():req(p.read_text(encoding='utf-8')==text,'content-address collision')
 else:p.write_text(text,encoding='utf-8')
 return h

def write_csvs(c,root:Path,wcsv:Path,tcsv:Path):
 wr=[]
 for u in c['writer_stage']['source_units']:
  for cond in ['success','failure']:
   p=root/'writer'/'stages'/f'{writer_stage_name(int(u["source_task"]),cond)}.json'
   if p.is_file():
    r=load(p);wr.append({k:r.get(k) for k in ['source_task','condition','status','memory_item_count','raw_sha256','resolved_model']})
 wcsv.parent.mkdir(parents=True,exist_ok=True)
 with wcsv.open('w',newline='',encoding='utf-8') as f:
  fields=['source_task','condition','status','memory_item_count','raw_sha256','resolved_model'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(wr)
 tr=[]
 for u in c['terminal_stage']['task_units']:
  for cond in ['success','failure']:
   for i in range(1,5):
    p=root/'terminal'/'stages'/f'{terminal_stage_name(int(u["future_task"]),int(u["selected_source_task"]),cond,i)}.json'
    if p.is_file():
     r=load(p);tr.append({k:r.get(k) for k in ['future_task','selected_source_task','condition','rollout','status','benchmark_score','answer_sha256','resolved_model']})
 with tcsv.open('w',newline='',encoding='utf-8') as f:
  fields=['future_task','selected_source_task','condition','rollout','status','benchmark_score','answer_sha256','resolved_model'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(tr)
def writer_rows(c,root):
 out=[]
 for u in c['writer_stage']['source_units']:
  for cond in ['success','failure']:
   p=root/'writer'/'stages'/f'{writer_stage_name(int(u["source_task"]),cond)}.json'
   if p.is_file():out.append(load(p))
 return out
def terminal_rows(c,root):
 out=[]
 for u in c['terminal_stage']['task_units']:
  for cond in ['success','failure']:
   for i in range(1,5):
    p=root/'terminal'/'stages'/f'{terminal_stage_name(int(u["future_task"]),int(u["selected_source_task"]),cond,i)}.json'
    if p.is_file():out.append(load(p))
 return out
def wrappers_ready(c,root)->bool:return len(writer_rows(c,root))==8 and all(r.get('status')=='complete' for r in writer_rows(c,root))
def run_writer(client,etype,u,cond,data,c,root):
 tid=int(u['source_task']);st=writer_stage_name(tid,cond);sp=root/'writer'/'stages'/f'{st}.json'
 if sp.is_file():return load(sp),False
 sysp=Path(c['writer_stage'][f'{cond}_prompt']['path']).read_text(encoding='utf-8');pr=writer_prompt(sysp,data['task_prompt'],data['summary']);base={'stage':st,'source_task':tid,'condition':cond,'prompt_sha256':tsha(pr),'action_summary_sha256':u['action_summary_sha256'],'requested_model':'deepseek-v4-flash'}
 try:
  r=client.respond(pr,model='deepseek-v4-flash',max_output_tokens=4096,temperature=0.0,thinking=None,store=True,allow_thinking_compatibility_fallback=False);text=str(r.get('text') or '').strip();writej(root/'writer'/'provider-responses'/f'{st}.json',{**base,'response_id':r.get('response_id'),'provider_status':r.get('status'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'text':text,'text_sha256':tsha(text) if text else ''});req(str(r.get('requested_model'))=='deepseek-v4-flash','writer requested model drift');req(normalized_model(str(r.get('resolved_model'))).startswith('deepseekv4flash'),'writer resolved family drift');req(bool(text),'writer empty text');items=parse_items(text);req(1<=len(items)<=3,f'writer schema failure:{len(items)}');raw=archive_text(root/'writer',text);wrap=wrapper(data['task_prompt'],items);wp=root/'wrappers'/f'{tid}-{cond}-native-wrapper.txt';wp.parent.mkdir(parents=True,exist_ok=True);wp.write_text(wrap,encoding='utf-8');row={**base,'status':'complete','provider_status':r.get('status'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'raw_sha256':raw,'memory_item_count':len(items),'titles':[x['title'] for x in items],'wrapper_path':str(wp.resolve()),'wrapper_sha256':sha(wp)}
 except etype as e:row={**base,'status':'provider_state_failure_no_text','error_type':type(e).__name__,'provider_receipt':e.receipt()}
 except Exception as e:row={**base,'status':'provider_or_runtime_failure','error_type':type(e).__name__,'error':str(e)[:1200]}
 writej(sp,row);return row,True
def run_terminal(client,etype,u,cond,i,data,root):
 tid=int(u['future_task']);src=int(u['selected_source_task']);st=terminal_stage_name(tid,src,cond,i);sp=root/'terminal'/'stages'/f'{st}.json'
 if sp.is_file():return load(sp),False
 wp=root/'wrappers'/f'{src}-{cond}-native-wrapper.txt';req(wp.is_file(),f'wrapper missing:{src}/{cond}');mem=wp.read_text(encoding='utf-8');pr=terminal_prompt(data['task_prompt'],data['evidence'],mem);base={'stage':st,'future_task':tid,'selected_source_task':src,'condition':cond,'rollout':i,'prompt_sha256':tsha(pr),'memory_wrapper_sha256':sha(wp),'requested_model':'doubao-seed-2.0-mini'}
 try:
  r=client.respond(pr,model='doubao-seed-2.0-mini',max_output_tokens=900,temperature=0.2,thinking='disabled',store=True,allow_thinking_compatibility_fallback=False);ans=str(r.get('text') or '').strip();writej(root/'terminal'/'provider-responses'/f'{st}.json',{**base,'response_id':r.get('response_id'),'provider_status':r.get('status'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'answer':ans,'answer_sha256':tsha(ans) if ans else '','thinking_compatibility_fallback':r.get('thinking_compatibility_fallback')});req(str(r.get('requested_model'))=='doubao-seed-2.0-mini' and str(r.get('resolved_model'))=='doubao-seed-2-0-mini-260215','terminal model drift');req(r.get('thinking_compatibility_fallback') is False,'terminal thinking fallback');req(bool(ans),'terminal empty text');sc,checks=score(ans,data['refs']);row={**base,'status':'complete','provider_status':r.get('status'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'answer_sha256':tsha(ans),'benchmark_score':sc,'evaluator_checks':checks}
 except etype as e:row={**base,'status':'provider_state_failure_no_text','error_type':type(e).__name__,'provider_receipt':e.receipt()}
 except Exception as e:row={**base,'status':'provider_or_runtime_failure','error_type':type(e).__name__,'error':str(e)[:1200]}
 writej(sp,row);return row,True
def permutation(c,rows,obs):
 rng=random.Random(20260824);pools=[]
 for u in c['terminal_stage']['task_units']:
  tid=int(u['future_task']);p=[float(r['benchmark_score']) for r in rows if int(r['future_task'])==tid];req(len(p)==8,f'perm pool drift:{tid}');pools.append(p)
 ge=0
 for _ in range(100000):
  vals=[]
  for p in pools:
   z=list(p);rng.shuffle(z);vals.append(abs(sum(z[:4])/4-sum(z[4:])/4))
  if sum(vals)/len(vals)>=obs-1e-12:ge+=1
 return (ge+1)/100001
def aggregate(c,root,provider,new_calls):
 wr=writer_rows(c,root);tr=terminal_rows(c,root);wf=[x for x in wr if x.get('status')!='complete'];tf=[x for x in tr if x.get('status')!='complete'];writer_complete=len(wr)==8 and not wf;writer_pairs=[]
 if writer_complete:
  for u in c['writer_stage']['source_units']:
   tid=int(u['source_task']);s=next(x for x in wr if int(x['source_task'])==tid and x['condition']=='success');f=next(x for x in wr if int(x['source_task'])==tid and x['condition']=='failure');st=(root/'writer'/'raw'/s['raw_sha256'][:2]/f"{s['raw_sha256']}.txt").read_text(encoding='utf-8');ft=(root/'writer'/'raw'/f['raw_sha256'][:2]/f"{f['raw_sha256']}.txt").read_text(encoding='utf-8');writer_pairs.append({'source_task':tid,'exact_content_change':s['raw_sha256']!=f['raw_sha256'],'title_set_change':set(s['titles'])!=set(f['titles']),'token_jaccard_distance':round(jaccard_distance(st,ft),6)})
 terminal_complete=len(tr)==64 and not tf;cells=[];obs=pv=signed=None;gate=False
 if terminal_complete:
  for u in c['terminal_stage']['task_units']:
   tid=int(u['future_task']);s=[float(x['benchmark_score']) for x in tr if int(x['future_task'])==tid and x['condition']=='success'];f=[float(x['benchmark_score']) for x in tr if int(x['future_task'])==tid and x['condition']=='failure'];req(len(s)==len(f)==4,f'terminal cell drift:{tid}');ps=sum(s)/4;pf=sum(f)/4;cells.append({'future_task':tid,'selected_source_task':int(u['selected_source_task']),'intent_template_id':int(u['intent_template_id']),'retrieval_similarity':u['retrieval_similarity'],'success_memory_rate':round(ps,6),'failure_memory_rate':round(pf,6),'absolute_rate_difference':round(abs(ps-pf),6),'signed_failure_minus_success':round(pf-ps,6)})
  obs=sum(x['absolute_rate_difference'] for x in cells)/8;signed=sum(x['signed_failure_minus_success'] for x in cells)/8;pv=permutation(c,tr,obs);gate=obs>=0.15 and pv<0.05
 if terminal_complete:status='B12_REDDIT_EXECUTION_COMPLETE'
 elif writer_complete:status='B12_REDDIT_WRITER_COMPLETE_TERMINAL_PARTIAL'
 else:status='B12_REDDIT_WRITER_PARTIAL'
 bysrc=defaultdict(list)
 for x in cells:bysrc[str(x['selected_source_task'])].append(x['absolute_rate_difference'])
 return {'schema_version':'1.0','paper_id':PAPER,'experiment_id':EXP,'status':status,'contract_sha256':c['contract_sha256'],'provider':provider,'summary':{'provider_calls_ceiling':72,'provider_calls_attempted_total':len(wr)+len(tr),'new_provider_calls_this_invocation':new_calls,'writer_calls_complete':sum(x.get('status')=='complete' for x in wr),'writer_failures':len(wf),'terminal_calls_complete':sum(x.get('status')=='complete' for x in tr),'terminal_failures':len(tf),'writer_pairs_complete':len(writer_pairs),'writer_exact_content_change_pairs':sum(x['exact_content_change'] for x in writer_pairs),'writer_title_set_change_pairs':sum(x['title_set_change'] for x in writer_pairs),'writer_mean_token_jaccard_distance':None if not writer_pairs else round(sum(x['token_jaccard_distance'] for x in writer_pairs)/len(writer_pairs),6),'observed_mean_absolute_success_rate_difference':None if obs is None else round(obs,6),'mean_signed_failure_minus_success':None if signed is None else round(signed,6),'permutation_p_ge_observed':None if pv is None else round(pv,6),'practical_effect_floor':0.15,'primary_gate_pass':gate if terminal_complete else None,'zero_effect_tasks':None if not cells else sum(x['absolute_rate_difference']==0 for x in cells),'nonzero_effect_tasks':None if not cells else sum(x['absolute_rate_difference']>0 for x in cells)},'writer_pair_results':writer_pairs,'cell_results':cells,'by_source_mean_absolute_effect':{k:round(sum(v)/len(v),6) for k,v in sorted(bysrc.items())},'decision':('SUPPORT_CROSSDOMAIN_REDDIT_NATIVE_BRANCH_TRANSPORT' if gate else 'CROSSDOMAIN_REDDIT_NATIVE_BRANCH_TRANSPORT_NOT_ESTABLISHED') if terminal_complete else 'INCOMPLETE_NO_SCIENTIFIC_VERDICT','failures':wf+tf,'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False,'submission_authority':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--private-root',required=True,type=Path);ap.add_argument('--writer-csv',required=True,type=Path);ap.add_argument('--terminal-csv',required=True,type=Path);ap.add_argument('--max-new-calls',type=int,default=8);a=ap.parse_args();c=load(a.contract);validate(c);req(1<=a.max_new_calls<=72,'invalid chunk');a.private_root.mkdir(parents=True,exist_ok=True);fh=(a.private_root/'transaction.lock').open('a+')
 try:fcntl.flock(fh.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:print(json.dumps({'status':'TRANSACTION_ALREADY_RUNNING','new_calls':0}));return 3
 try:
  pq,etype,client,provider=runtime(c);src,future=load_data(c,pq);new=0;stop=False;chunk=False
  for u in c['writer_stage']['source_units']:
   if stop or chunk:break
   for cond in ['success','failure']:
    p=a.private_root/'writer'/'stages'/f'{writer_stage_name(int(u["source_task"]),cond)}.json'
    if not p.is_file() and new>=a.max_new_calls:chunk=True;break
    r,isnew=run_writer(client,etype,u,cond,src[int(u['source_task'])],c,a.private_root);new+=int(isnew);write_csvs(c,a.private_root,a.writer_csv,a.terminal_csv);writej(a.output,aggregate(c,a.private_root,provider,new))
    if isnew:print(json.dumps({'stage':r['stage'],'status':r['status'],'new_calls':new,'writer_complete':len(writer_rows(c,a.private_root))}),flush=True)
    if r.get('status')!='complete':stop=True;break
  if not stop and not chunk and wrappers_ready(c,a.private_root):
   for u in c['terminal_stage']['task_units']:
    if stop or chunk:break
    for cond in ['success','failure']:
     if stop or chunk:break
     for i in range(1,5):
      p=a.private_root/'terminal'/'stages'/f'{terminal_stage_name(int(u["future_task"]),int(u["selected_source_task"]),cond,i)}.json'
      if not p.is_file() and new>=a.max_new_calls:chunk=True;break
      r,isnew=run_terminal(client,etype,u,cond,i,future[int(u['future_task'])],a.private_root);new+=int(isnew);write_csvs(c,a.private_root,a.writer_csv,a.terminal_csv);writej(a.output,aggregate(c,a.private_root,provider,new))
      if isnew and (new<=12 or new%16==0 or r.get('status')!='complete'):print(json.dumps({'stage':r['stage'],'status':r['status'],'new_calls':new,'terminal_complete':len(terminal_rows(c,a.private_root))}),flush=True)
      if r.get('status')!='complete':stop=True;break
  out=aggregate(c,a.private_root,provider,new);write_csvs(c,a.private_root,a.writer_csv,a.terminal_csv);writej(a.output,out);print(json.dumps({'status':out['status'],'summary':out['summary'],'decision':out['decision']},indent=2));return 2 if stop else 0
 finally:fcntl.flock(fh.fileno(),fcntl.LOCK_UN);fh.close()
if __name__=='__main__':raise SystemExit(main())
