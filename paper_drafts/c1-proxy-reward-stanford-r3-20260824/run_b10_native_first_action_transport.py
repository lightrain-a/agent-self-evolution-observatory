#!/usr/bin/env python3
from __future__ import annotations
import argparse, fcntl, hashlib, json, math, os, random, re, sys
from collections import Counter
from pathlib import Path
from typing import Any

EXPERIMENT_ID='D2-PROXY-B10-NATIVE-FIRST-ACTION-TRANSPORT'
MODEL='doubao-seed-2.0-mini'; RESOLVED='doubao-seed-2-0-mini-260215'; BASE_URL='https://ark.cn-beijing.volces.com/api/plan/v3'
TOTAL=432; N=4; CONDITIONS=['success_memory','failure_memory','no_memory']
EXPECTED_B3_SHA='a5e39a817cdadc9b4edae4edba0c9c90068f1cd9d083e4c3a70bdfad32871440'
EXPECTED_B4_CONTRACT_SHA='eb86231b4afe2143e59fa8d322a42a5bb236a09aefcb506fe2d7bb7d8dbaaa11'
EXPECTED_B4_RESULT_SHA='fb3fef89a38806e9a3b13efd8413b920f81b132390818403f4d5be957f42feeb'
EXPECTED_MANIFEST_SHA='2880b83c71745f049039c15edb02f731e4f87a44670977b61627143102bee0d1'
EXPECTED_PARQUET_SHA='fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e'
EXPECTED_AUTH_SHA='ddc5bd50487ed431f5d24ee84cda4e422f36216b4191a02db21db18ae821161f'


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def load(p:Path)->dict[str,Any]:
 d=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(d,dict):raise RuntimeError(f'JSON root not object:{p}')
 return d
def req(x:bool,msg:str):
 if not x:raise RuntimeError(msg)
def writej(p:Path,d:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');os.replace(t,p)
def archive(root:Path,text:str)->str:
 h=tsha(text);p=root/'raw'/h[:2]/f'{h}.txt';p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():req(p.read_text(encoding='utf-8')==text,'raw archive collision')
 else:p.write_text(text,encoding='utf-8')
 return h

def action_signature(payload:dict[str,Any])->str:
 current=payload.get('current_state') or {};actions=payload.get('action') or (current.get('action') if isinstance(current,dict) else None) or []
 if not actions or not isinstance(actions[0],dict):return 'NO_ACTION'
 action=actions[0];name=next(iter(action),'UNKNOWN');args=action.get(name) or {}
 if name=='click_element' and isinstance(args,dict):return f"click_element:{args.get('index')}"
 return name

def parse_output(text:str,extract_json_object)->tuple[str,str,bool]:
 try:
  payload=extract_json_object(text);sig=action_signature(payload);cur=payload.get('current_state') or {};goal=str(cur.get('next_goal') or '') if isinstance(cur,dict) else '';return sig,goal,False
 except Exception as strict_error:
  m=re.search(r'"action"\s*:\s*\[\s*\{\s*"([^"]+)"\s*:\s*\{(.*?)\}\s*\}\s*\]',text,re.DOTALL)
  if not m:raise strict_error
  name=m.group(1);body=m.group(2)
  if name=='click_element':
   ix=re.search(r'"index"\s*:\s*(\d+)',body)
   if not ix:raise strict_error
   sig=f'click_element:{ix.group(1)}'
  else:sig=name
  gm=re.search(r'"next_goal"\s*:\s*"((?:\\.|[^"\\])*)"',text,re.DOTALL);goal=''
  if gm:
   try:goal=json.loads('"'+gm.group(1)+'"')
   except Exception:goal=gm.group(1)
  return sig,goal,True

def tv(a:list[str],b:list[str])->float:
 ca,cb=Counter(a),Counter(b);keys=set(ca)|set(cb);na=max(1,len(a));nb=max(1,len(b));return .5*sum(abs(ca[k]/na-cb[k]/nb) for k in keys)
def entropy(v:list[str])->float:
 if not v:return 0.0
 c=Counter(v);n=len(v);return -sum((x/n)*math.log2(x/n) for x in c.values())
def mode(v:list[str])->str:
 if not v:return ''
 c=Counter(v);m=max(c.values());return sorted(k for k,x in c.items() if x==m)[0]
def corr(xs:list[float],ys:list[float])->float|None:
 if len(xs)<2:return None
 mx=sum(xs)/len(xs);my=sum(ys)/len(ys);vx=sum((x-mx)**2 for x in xs);vy=sum((y-my)**2 for y in ys)
 if vx<=0 or vy<=0:return None
 return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(vx*vy)

def decision_prompt(system:str,task:str,state:str,memory:str)->str:
 mem=memory.strip() if memory.strip() else 'No reusable memory is available for this decision.'
 return f'''SYSTEM INSTRUCTION:\n{system}\n\nREUSABLE MEMORY:\n{mem}\n\nULTIMATE TASK:\n{task}\n\nCURRENT BROWSER STATE:\n{state}\n\nChoose the next browser-agent action now. Return only the JSON object required by the system instruction.'''

def validate(c:dict[str,Any]):
 req(c.get('status')=='FROZEN_BEFORE_PROVIDER_CALLS' and c.get('experiment_id')==EXPERIMENT_ID,'contract identity drift');req(c.get('future_task_count')==36 and len(c.get('task_units') or [])==36,'support drift');req(c.get('conditions')==CONDITIONS and c.get('rollouts_per_task_per_condition')==N and c.get('expected_provider_calls')==TOTAL,'geometry drift')
 m=c['model'];req(m['requested']==MODEL and m['expected_resolved']==RESOLVED and m['temperature']==0.2 and m['max_output_tokens']==900 and m['thinking']=='disabled' and m['provider_retries']==0 and m['allow_thinking_compatibility_fallback'] is False and m['substitution_allowed'] is False,'model drift')
 g=c['primary_gate'];req(g['min_mean_tv']==0.20 and g['permutation_p_lt']==0.05 and g['permutation_repetitions']==100000 and g['permutation_seed']==20260824,'gate drift')
 req(c['state_selection']['future_step']==1 and c['state_selection']['outcome_blind'] is True and c['state_selection']['task_specific_step_selection'] is False,'state-selection drift')
 miss=c['missingness_policy'];req(miss['provider_retries']==0 and miss['stop_after_first_no_text_provider_failure'] is True and miss['stop_after_first_unrecoverable_parse_failure'] is True and miss['top_up_failed_units'] is False,'missingness drift')
 a=c['authority'];req(a['experiment_authority'] is True and a['provider_call_authority'] is True and a['claim_expansion_authority'] is False and a['submission_authority'] is False,'authority drift')
 expected={'b3':EXPECTED_B3_SHA,'b4_contract':EXPECTED_B4_CONTRACT_SHA,'b4_result':EXPECTED_B4_RESULT_SHA,'memory_manifest':EXPECTED_MANIFEST_SHA,'parquet':EXPECTED_PARQUET_SHA}
 for k,h in expected.items():p=Path(c['source_bindings'][k]['path']);req(p.is_file() and sha(p)==h,f'{k} binding drift')
 hp=Path(c['human_authority']['path']);req(hp.is_file() and sha(hp)==EXPECTED_AUTH_SHA,'human authority drift')
 rp=Path(c['code']['runner']['path']);req(rp.resolve()==Path(__file__).resolve() and sha(rp)==c['code']['runner']['sha256'],'runner drift')

def runtime(c:dict[str,Any]):
 sys.path.insert(0,str(c['vendor_path']));import pyarrow.parquet as pq
 repo=Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo))
 from research_pipeline.config import load_env_file
 from research_pipeline.ark_provider import ArkResponseStateError,ArkResponsesClient,ArkSettings,extract_json_object
 load_env_file(Path(c['provider_env_file']));base=ArkSettings.from_env();req(bool(base.api_key),'credential unavailable');req(base.base_url==BASE_URL,'base URL drift');settings=ArkSettings(api_key=base.api_key,base_url=base.base_url,default_model=base.default_model,timeout_seconds=180.0,max_retries=0);return pq,ArkResponseStateError,ArkResponsesClient(settings),extract_json_object,settings.safe_summary()

def source_rows(c:dict[str,Any],pq)->dict[int,dict[str,Any]]:
 par=Path(c['source_bindings']['parquet']['path']);raw={int(r['task_id']):r for r in pq.read_table(par,columns=['task_id','task_prompt','trajectory_json']).to_pylist()};out={}
 for u in c['task_units']:
  tid=int(u['future_task']);r=raw[tid];req(tsha(str(r['task_prompt']))==u['task_prompt_sha256'],f'task prompt drift:{tid}');tr=json.loads(str(r['trajectory_json']));step=(tr.get('steps') or {}).get('1');contents=((step.get('input_messages') or {}).get('contents') or []);system=str(contents[0].get('content') or '');last=str(contents[-1].get('content') or '');marker='[Current state starts here]';req(marker in last,f'state marker drift:{tid}');state=last.split(marker,1)[1].strip();req(tsha(system)==u['system_instruction_sha256'] and tsha(state)==u['current_state_sha256'],f'system/state SHA drift:{tid}');out[tid]={'task_prompt':str(r['task_prompt']),'system':system,'state':state,'source':int(u['selected_source_task']),'unit':u}
 return out

def one(client,error_type,extract_json_object,c:dict[str,Any],root:Path,td:dict[str,Any],condition:str,rollout:int)->dict[str,Any]:
 tid=td['unit']['future_task'];src=td['source'];st=f'first-action-{tid}-source-{src}-{condition}-r{rollout}';sp=root/'stages'/f'{st}.json'
 if sp.is_file():return load(sp)
 memory=''
 if condition!='no_memory':
  key='success' if condition=='success_memory' else 'failure';mp=Path(td['unit']['memory_wrappers'][key]['path']);req(mp.is_file() and sha(mp)==td['unit']['memory_wrappers'][key]['sha256'],f'memory wrapper drift:{tid}/{key}');memory=mp.read_text(encoding='utf-8')
 pr=decision_prompt(td['system'],td['task_prompt'],td['state'],memory);base={'stage':st,'future_task':tid,'selected_source_task':src,'condition':condition,'rollout':rollout,'prompt_sha256':tsha(pr),'requested_model':MODEL}
 try:
  r=client.respond(pr,model=MODEL,max_output_tokens=900,temperature=0.2,thinking='disabled',store=True,allow_thinking_compatibility_fallback=False);text=str(r.get('text') or '');writej(root/'provider-responses'/f'{st}.json',{**base,'response_id':r.get('response_id'),'provider_status':r.get('status'),'requested_model_returned':r.get('requested_model'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'text':text,'text_sha256':tsha(text) if text else '','thinking_compatibility_fallback':r.get('thinking_compatibility_fallback')});req(str(r.get('requested_model'))==MODEL and str(r.get('resolved_model'))==RESOLVED,'model resolution drift');req(r.get('thinking_compatibility_fallback') is False,'thinking fallback');req(bool(text.strip()),'no assistant text');raw=archive(root,text)
  try:sig,goal,recovered=parse_output(text,extract_json_object)
  except Exception as e:row={**base,'status':'parse_failure','error_type':type(e).__name__,'raw_sha256':raw,'provider_status':r.get('status'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {}}
  else:row={**base,'status':'complete','provider_status':r.get('status'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'raw_sha256':raw,'action_signature':sig,'next_goal_sha256':tsha(goal) if goal else '','parse_recovered':recovered}
 except error_type as e:row={**base,'status':'provider_state_failure_no_text','error_type':type(e).__name__,'provider_receipt':e.receipt()}
 except Exception as e:row={**base,'status':'provider_or_runtime_failure','error_type':type(e).__name__,'error':str(e)[:1000]}
 writej(sp,row);return row

def perm_p(cells:list[dict[str,Any]],obs:float)->float:
 pools=[x['success']+x['failure'] for x in cells];rng=random.Random(20260824);ge=0;R=100000
 for _ in range(R):
  vals=[]
  for pool in pools:
   z=list(pool);rng.shuffle(z);vals.append(tv(z[:N],z[N:]))
  if sum(vals)/len(vals)>=obs-1e-12:ge+=1
 return (ge+1)/(R+1)

def report(c:dict[str,Any],rows:list[dict[str,Any]],provider:dict[str,Any],new_calls:int)->dict[str,Any]:
 complete=[r for r in rows if r.get('status')=='complete'];fail=[r for r in rows if r.get('status')!='complete'];full=len(complete)==TOTAL and not fail;cells=[];obs=pv=presence=None;gate=False
 if full:
  for u in c['task_units']:
   tid=u['future_task'];groups={cond:[r['action_signature'] for r in complete if r['future_task']==tid and r['condition']==cond] for cond in CONDITIONS};req(all(len(v)==N for v in groups.values()),f'incomplete state:{tid}');sf=tv(groups['success_memory'],groups['failure_memory']);sn=tv(groups['success_memory'],groups['no_memory']);fn=tv(groups['failure_memory'],groups['no_memory']);cells.append({'future_task':tid,'selected_source_task':u['selected_source_task'],'retrieval_similarity':u['retrieval_similarity'],'retrieval_margin':u['retrieval_margin'],'intent_template_id':u['intent_template_id'],'success':groups['success_memory'],'failure':groups['failure_memory'],'no_memory':groups['no_memory'],'success_failure_tv':sf,'success_no_memory_tv':sn,'failure_no_memory_tv':fn,'presence_tv':.5*(sn+fn),'modal_success':mode(groups['success_memory']),'modal_failure':mode(groups['failure_memory']),'modal_no_memory':mode(groups['no_memory']),'entropy_success':entropy(groups['success_memory']),'entropy_failure':entropy(groups['failure_memory']),'entropy_no_memory':entropy(groups['no_memory'])})
  obs=sum(x['success_failure_tv'] for x in cells)/len(cells);presence=sum(x['presence_tv'] for x in cells)/len(cells);pv=perm_p(cells,obs);gate=obs>=.20 and pv<.05
 b4=load(Path(c['source_bindings']['b4_result']['path']));b4map={int(x['future_task']):float(x['absolute_rate_difference']) for x in b4['cell_results']};cor=None
 if cells:cor=corr([float(x['success_failure_tv']) for x in cells],[b4map[int(x['future_task'])] for x in cells])
 secondary={}
 if cells:
  secondary={'mean_memory_presence_tv':round(presence,6),'states_with_nonzero_success_failure_tv':sum(x['success_failure_tv']>0 for x in cells),'states_with_modal_success_failure_difference':sum(x['modal_success']!=x['modal_failure'] for x in cells),'states_where_either_memory_modal_differs_from_no_memory':sum((x['modal_success']!=x['modal_no_memory']) or (x['modal_failure']!=x['modal_no_memory']) for x in cells),'pearson_first_action_tv_vs_B4_terminal_abs_effect':cor,'mean_entropy_bits':{'success':round(sum(x['entropy_success'] for x in cells)/36,6),'failure':round(sum(x['entropy_failure'] for x in cells)/36,6),'no_memory':round(sum(x['entropy_no_memory'] for x in cells)/36,6)}}
 decision='SUPPORT_NATIVE_FIRST_ACTION_BRANCH_TRANSPORT' if gate else ('NATIVE_FIRST_ACTION_BRANCH_TRANSPORT_NOT_ESTABLISHED' if full else 'B10_INCOMPLETE_NO_SCIENTIFIC_VERDICT')
 return {'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'paper_id':c['paper_id'],'status':'B10_EXECUTION_COMPLETE' if full else 'B10_EXECUTION_PARTIAL','contract_sha256':c['contract_sha256'],'provider':provider,'summary':{'provider_calls_expected':TOTAL,'provider_calls_attempted_total':len(rows),'provider_calls_complete':len(complete),'provider_failures_or_parse_failures':len(fail),'new_provider_calls_this_invocation':new_calls,'future_tasks':36,'rollouts_per_task_per_condition':N,'observed_mean_success_failure_tv':None if obs is None else round(obs,6),'permutation_p_ge_observed':None if pv is None else round(pv,6),'practical_tv_floor':.20,'primary_gate_pass':gate},'secondary':secondary,'cell_results':cells,'rollouts':[{k:r.get(k) for k in ('future_task','selected_source_task','condition','rollout','action_signature','next_goal_sha256','parse_recovered','provider_status','resolved_model','usage')} for r in complete],'failures':[{k:r.get(k) for k in ('future_task','selected_source_task','condition','rollout','stage','status','error_type','provider_receipt','error')} for r in fail],'decision':decision,'scope_boundary':c['scope_boundary'],'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False}

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--contract',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--private-root',required=True,type=Path);ap.add_argument('--max-new-calls',type=int,default=72);a=ap.parse_args();c=load(a.contract);validate(c);a.private_root.mkdir(parents=True,exist_ok=True);lock=(a.private_root/'transaction.lock').open('a+')
 try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:print(json.dumps({'status':'TRANSACTION_ALREADY_RUNNING','provider_calls_executed_by_this_process':0}));return 3
 try:
  pq,etype,client,extract,ps=runtime(c);td=source_rows(c,pq);existing=[]
  for p in sorted((a.private_root/'stages').glob('*.json')) if (a.private_root/'stages').exists() else []:existing.append(load(p))
  rows=list(existing);new=0;stop=any(r.get('status')!='complete' for r in rows)
  seen={r['stage'] for r in rows}
  if not stop:
   for u in c['task_units']:
    if new>=a.max_new_calls:break
    t=td[int(u['future_task'])]
    for cond in CONDITIONS:
     if new>=a.max_new_calls or stop:break
     for i in range(1,N+1):
      st=f"first-action-{u['future_task']}-source-{u['selected_source_task']}-{cond}-r{i}"
      if st in seen:continue
      r=one(client,etype,extract,c,a.private_root,t,cond,i);rows.append(r);seen.add(st);new+=1;writej(a.output,report(c,rows,ps,new))
      if new%12==0 or r.get('status')!='complete':print(json.dumps({'stage':st,'status':r.get('status'),'new_calls_this_invocation':new,'total_stages':len(rows)}),flush=True)
      if r.get('status')!='complete':stop=True;break
  out=report(c,rows,ps,new);writej(a.output,out);print(json.dumps({'status':out['status'],'summary':out['summary'],'secondary':out['secondary'],'decision':out['decision']},indent=2),flush=True);return 0 if out['status']=='B10_EXECUTION_COMPLETE' else (2 if stop else 4)
 finally:fcntl.flock(lock.fileno(),fcntl.LOCK_UN);lock.close()
if __name__=='__main__':raise SystemExit(main())
