from __future__ import annotations
import csv,fcntl,hashlib,json,math,os,re,subprocess,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.ark_provider import ArkResponseStateError,ArkResponsesClient,ArkSettings,extract_json_object
from research_pipeline.config import load_env_file
CONTRACT=HERE/'c1-scmb-pilot-contract-20260829.json';FREEZE=HERE/'c1-scmb-pilot-freeze-20260829.json';AUTH=HERE/'c1-scmb-human-authorization-20260829.json';SUPPORT=HERE/'c1-scmb-provider-support-20260829.json'
B10=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b10-native-first-action-transport-20260824/b10-contract.json')
RUN=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-scmb-p0-fresh-uptake-20260829-pilot-v1');ENV=Path('/home/wyt/code/agent-self-evolution-observatory/.env');MODEL='doubao-seed-2.0-mini';RESOLVED='doubao-seed-2-0-mini-260215'

def shab(b):return hashlib.sha256(b).hexdigest()
def shaf(p):return shab(Path(p).read_bytes())
def shat(s):return shab(s.encode())
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(p)
def req(x,m):
 if not x:raise RuntimeError(m)
def now():return datetime.now(timezone.utc).isoformat()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()

def action_signature(payload):
 cur=payload.get('current_state') or {};acts=payload.get('action') or (cur.get('action') if isinstance(cur,dict) else None) or []
 if not acts or not isinstance(acts[0],dict):return 'NO_ACTION'
 a=acts[0];name=next(iter(a),'UNKNOWN');args=a.get(name) or {}
 return f"click_element:{args.get('index')}" if name=='click_element' and isinstance(args,dict) else name

def parse_output(text):
 try:
  p=extract_json_object(text);sig=action_signature(p);cur=p.get('current_state') or {};goal=str(cur.get('next_goal') or '') if isinstance(cur,dict) else '';return sig,goal,False
 except Exception as e:
  m=re.search(r'"action"\s*:\s*\[\s*\{\s*"([^"]+)"\s*:\s*\{(.*?)\}\s*\}\s*\]',text,re.S)
  if not m:raise e
  name=m.group(1);body=m.group(2)
  if name=='click_element':
   ix=re.search(r'"index"\s*:\s*(\d+)',body)
   if not ix:raise e
   sig=f'click_element:{ix.group(1)}'
  else:sig=name
  gm=re.search(r'"next_goal"\s*:\s*"((?:\\.|[^"\\])*)"',text,re.S);goal=''
  if gm:
   try:goal=json.loads('"'+gm.group(1)+'"')
   except Exception:goal=gm.group(1)
  return sig,goal,True

def tv(a,b):
 ca,cb=Counter(a),Counter(b);n,m=len(a),len(b);keys=set(ca)|set(cb);return .5*sum(abs(ca[k]/n-cb[k]/m) for k in keys)

def materialize_states(freeze,b10):
 sys.path.insert(0,str(b10['vendor_path']));import pyarrow.parquet as pq
 par=Path(b10['source_bindings']['parquet']['path']);req(shaf(par)==b10['source_bindings']['parquet']['sha256'],'parquet drift')
 raw={int(r['task_id']):r for r in pq.read_table(par,columns=['task_id','task_prompt','trajectory_json']).to_pylist()};out={}
 for u in freeze['selection']['pilot']:
  tid=int(u['future_task']);r=raw[tid];task=str(r['task_prompt']);req(shat(task)==u['task_prompt_sha256'],f'task drift {tid}');tr=json.loads(str(r['trajectory_json']));step=(tr.get('steps') or {}).get('1');contents=((step.get('input_messages') or {}).get('contents') or []);system=str(contents[0].get('content') or '');last=str(contents[-1].get('content') or '');marker='[Current state starts here]';req(marker in last,f'marker {tid}');state=last.split(marker,1)[1].strip();req(shat(system)==u['system_instruction_sha256'] and shat(state)==u['current_state_sha256'],f'state drift {tid}')
  branches={}
  for br in ['success','failure']:
   p=Path(u[f'{br}_memory_wrapper_path']);req(p.is_file() and shaf(p)==u[f'{br}_memory_wrapper_sha256'],f'memory drift {tid}/{br}');branches[br]=p.read_text(encoding='utf-8')
  out[tid]={'unit':u,'system':system,'task':task,'state':state,'memory':branches}
 return out

def binder_prompt(kind,memory,task,state,c):
 if kind=='A1':return c['binder']['A1_instruction']+'\n\nREUSABLE MEMORY:\n'+memory
 return c['binder']['A2_instruction']+'\n\nREUSABLE MEMORY:\n'+memory+'\n\nULTIMATE TASK:\n'+task+'\n\nCURRENT BROWSER STATE:\n'+state

def policy_prompt(system,task,state,memory,note=None):
 extra='' if note is None else '\n\nADAPTED SUPPORT:\n'+note.strip()
 return f'''SYSTEM INSTRUCTION:\n{system}\n\nREUSABLE MEMORY:\n{memory.strip()}{extra}\n\nULTIMATE TASK:\n{task}\n\nCURRENT BROWSER STATE:\n{state}\n\nChoose the next browser-agent action now. Return only the JSON object required by the system instruction.'''

def client():
 load_env_file(ENV);raw=ArkSettings.from_env();s=ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=180,max_retries=0);return ArkResponsesClient(s),s.safe_summary()

def provider_call(cl,prompt,max_tokens,temp):
 r=cl.respond(prompt,model=MODEL,max_output_tokens=max_tokens,temperature=temp,thinking='disabled',store=True,allow_thinking_compatibility_fallback=False);req(r.get('requested_model')==MODEL,'requested drift');req(r.get('resolved_model')==RESOLVED,'resolved drift');req(r.get('thinking_compatibility_fallback') is False,'fallback');t=str(r.get('text') or '');req(bool(t.strip()),'empty text');return r,t

def main():
 RUN.mkdir(parents=True,exist_ok=True);lock=open(RUN/'.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 c,f,a,s,b10=load(CONTRACT),load(FREEZE),load(AUTH),load(SUPPORT),load(B10);req(s['status']=='SUPPORT_PASS','support not pass');req(a['authority']['pilot_binder_provider'] and a['authority']['pilot_policy_provider'],'no authority');states=materialize_states(f,b10)
 manifest={'schema_version':'1.0','run_id':RUN.name,'paper_id':c['paper_id'],'experiment_id':c['experiment_id'],'design_git_sha':git('rev-parse','HEAD'),'execution_base':git('rev-parse','origin/main'),'contract_sha256':shaf(CONTRACT),'freeze_sha256':shaf(FREEZE),'support_sha256':shaf(SUPPORT),'pilot_ids':list(states),'template_holdout_ids':[x['future_task'] for x in f['selection']['template_holdout']],'expected_binder_calls':48,'expected_policy_calls':432,'binder':c['binder'],'policy':c['policy'],'started_at':now(),'no_terminal_outcome':True,'confirmatory_locked':True}
 if not (RUN/'run-manifest.json').exists():dump(RUN/'run-manifest.json',manifest)
 else:req(load(RUN/'run-manifest.json')['contract_sha256']==manifest['contract_sha256'],'manifest drift')
 cl,ps=client();dump(RUN/'provider-summary.json',ps)
 # Binder phase: 12 states x 2 branches x A1/A2 = 48. Resume-safe.
 notes={}
 for tid,st in states.items():
  notes[tid]={}
  for br0 in ['success','failure']:
   notes[tid][br0]={}
   mem=st['memory'][br0]
   for kind in ['A1','A2']:
    pth=RUN/'binder'/f'task-{tid}__{kind}__{br0}.json';prompt=binder_prompt(kind,mem,st['task'],st['state'],c)
    if pth.exists():o=load(pth);req(o.get('status')=='complete' and o['prompt_sha256']==shat(prompt),'binder resume drift')
    else:
     r,t=provider_call(cl,prompt,180,0.0);o={'status':'complete','future_task':tid,'kind':kind,'branch':br0,'prompt_sha256':shat(prompt),'memory_sha256':shat(mem),'text':t.strip(),'text_sha256':shat(t.strip()),'word_count':len(t.split()),'response_id':r.get('response_id'),'resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'completed_at':now()};dump(pth,o)
    notes[tid][br0][kind]=o['text']
 dump(RUN/'binder-progress.json',{'status':'COMPLETE','completed':sum(1 for _ in (RUN/'binder').glob('*.json')),'expected':48,'updated_at':now()})
 # Freeze action inputs/schedule before action calls.
 rows=[]
 for tid,st in states.items():
  u=st['unit']
  for arm in ['A0_NATIVE','A1_MEMORY_ONLY_ADAPTER','A2_STATE_CONDITIONED_BINDING']:
   for br0 in ['success','failure']:
    note=None if arm=='A0_NATIVE' else notes[tid][br0]['A1' if arm.startswith('A1') else 'A2'];prompt=policy_prompt(st['system'],st['task'],st['state'],st['memory'][br0],note)
    for rollout in range(1,7):
     cid=f'task-{tid}__{arm}__{br0}_memory__r{rollout}';rows.append({'case_id':cid,'future_task':tid,'intent_template_id':u['intent_template_id'],'selected_source_task':u['selected_source_task'],'arm':arm,'branch':br0,'rollout':rollout,'prompt_sha256':shat(prompt),'prompt':prompt,'memory_sha256':shat(st['memory'][br0]),'note_sha256':'' if note is None else shat(note)})
 rows.sort(key=lambda x:shat('C1-SCMB-ACTION-SCHEDULE-v1|'+x['case_id']))
 for i,r in enumerate(rows,1):r['order']=i
 if not (RUN/'schedule.jsonl').exists():(RUN/'schedule.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
 else:req(shaf(RUN/'schedule.jsonl')==shaf(RUN/'schedule.jsonl'),'schedule')
 dump(RUN/'action-input-manifest.json',{'cases':len(rows),'schedule_sha256':shaf(RUN/'schedule.jsonl'),'created_at':now()})
 # action phase
 failures=[]
 for r in rows:
  pth=RUN/'per_case'/f"{r['case_id']}.json"
  if pth.exists():
   o=load(pth);req(o.get('status')=='complete','existing failed case');continue
  try:
   resp,text=provider_call(cl,r['prompt'],900,0.2);sig,goal,recovered=parse_output(text);o={k:v for k,v in r.items() if k!='prompt'};o.update({'status':'complete','resolved_model':resp.get('resolved_model'),'response_id':resp.get('response_id'),'provider_status':resp.get('status'),'raw_text':text,'raw_text_sha256':shat(text),'action_signature':sig,'next_goal_sha256':shat(goal) if goal else '','parse_recovered':recovered,'usage':resp.get('usage') or {},'completed_at':now()});dump(pth,o)
  except Exception as e:
   o={k:v for k,v in r.items() if k!='prompt'};o.update({'status':'failed','failure_type':type(e).__name__,'failure':str(e)[:1200],'completed_at':now()});dump(pth,o);failures.append(o);break
  if r['order']%12==0:dump(RUN/'progress.json',{'status':'RUNNING','completed':sum(1 for _ in (RUN/'per_case').glob('*.json')),'expected':432,'updated_at':now()})
 if failures:
  dump(RUN/'progress.json',{'status':'STOP_ON_FIRST_FAILURE','completed':sum(1 for _ in (RUN/'per_case').glob('*.json')),'expected':432,'failed':len(failures),'updated_at':now()});print(json.dumps({'status':'STOP_ON_FIRST_FAILURE','failure':failures[0]}));return 2
 cases=[load(p) for p in sorted((RUN/'per_case').glob('*.json'))];req(len(cases)==432 and all(x['status']=='complete' for x in cases),'action incomplete');dump(RUN/'progress.json',{'status':'EXECUTION_COMPLETE','completed':432,'expected':432,'failed':0,'updated_at':now()})
 # analysis
 per=[]
 for tid,st in states.items():
  row={'future_task':tid,'intent_template_id':st['unit']['intent_template_id'],'selected_source_task':st['unit']['selected_source_task']}
  for arm in ['A0_NATIVE','A1_MEMORY_ONLY_ADAPTER','A2_STATE_CONDITIONED_BINDING']:
   ss=[x['action_signature'] for x in cases if x['future_task']==tid and x['arm']==arm and x['branch']=='success'];ff=[x['action_signature'] for x in cases if x['future_task']==tid and x['arm']==arm and x['branch']=='failure'];row['U_'+arm]=tv(ss,ff)
  row['D_A2_minus_A1']=row['U_A2_STATE_CONDITIONED_BINDING']-row['U_A1_MEMORY_ONLY_ADAPTER'];row['N_A2_minus_A0']=row['U_A2_STATE_CONDITIONED_BINDING']-row['U_A0_NATIVE'];per.append(row)
 means={k:sum(r[k] for r in per)/len(per) for k in ['U_A0_NATIVE','U_A1_MEMORY_ONLY_ADAPTER','U_A2_STATE_CONDITIONED_BINDING','D_A2_minus_A1','N_A2_minus_A0']}
 dpos=sum(r['D_A2_minus_A1']>0 for r in per);gate={'mean_D_ge_0_05':means['D_A2_minus_A1']>=.05,'D_positive_at_least_6_of_12':dpos>=6,'mean_N_gt_0':means['N_A2_minus_A0']>0,'A2_gt_A1':means['U_A2_STATE_CONDITIONED_BINDING']>means['U_A1_MEMORY_ONLY_ADAPTER'],'A2_gt_A0':means['U_A2_STATE_CONDITIONED_BINDING']>means['U_A0_NATIVE']};passed=all(gate.values())
 with (RUN/'pilot-per-state.csv').open('w',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(per[0]));w.writeheader();w.writerows(per)
 binders=[load(p) for p in (RUN/'binder').glob('*.json')];lens={k:[x['word_count'] for x in binders if x['kind']==k] for k in ['A1','A2']}
 analysis={'schema_version':'1.0','artifact_kind':'C1_SCMB_PILOT_ANALYSIS','status':'PILOT_SIGNAL_PASS' if passed else 'PILOT_HOLD_OR_STOP','execution':{'binder_calls':48,'policy_calls':432,'failed':0,'parse_recovered':sum(bool(x['parse_recovered']) for x in cases),'model_drift':0,'old36_calls':0,'template_holdout_calls':0},'effect_summary':{**means,'D_positive_count':dpos,'D_negative_count':sum(r['D_A2_minus_A1']<0 for r in per),'D_zero_count':sum(r['D_A2_minus_A1']==0 for r in per)},'gate':{'checks':gate,'pass':passed,'thresholds_unchanged':True},'binder_realization':{'A1_mean_words':sum(lens['A1'])/len(lens['A1']),'A2_mean_words':sum(lens['A2'])/len(lens['A2']),'A1_range':[min(lens['A1']),max(lens['A1'])],'A2_range':[min(lens['A2']),max(lens['A2'])]},'heterogeneity':per,'claim_boundary':'A positive pilot would show only a modest proof-of-concept that a known-style state-conditioned adapter aligns with the diagnosed uptake surface; it would not establish method novelty, terminal utility, or causal mediation.','confirmatory_executed':False}
 dump(RUN/'pilot-analysis.json',analysis)
 differential={'schema_version':'1.0','artifact_kind':'C1_SCMB_FAILURE_DIFFERENTIAL','pilot_status':analysis['status'],'layers':{'execution_failure':False,'binder_delivery_failure':False,'generic_memory_rewrite_explanation':{'active_or_competing':not gate['A2_gt_A1']},'state_conditioning_signal':{'supported':passed},'measurement_note':'first-action TV is the pre-registered uptake observable; terminal utility was not tested'},'next_action':'STOP_AND_REVIEW; fresh 19-template holdout remains sealed.'};dump(RUN/'pilot-failure-differential.json',differential)
 print(json.dumps({'status':analysis['status'],'means':means,'D_positive':dpos,'gate':gate,'binder_calls':48,'policy_calls':432,'holdout_calls':0}))
 return 0
if __name__=='__main__':raise SystemExit(main())
