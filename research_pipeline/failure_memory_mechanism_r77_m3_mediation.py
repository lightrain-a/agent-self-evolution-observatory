#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, os, pathlib, socket, subprocess, sys, urllib.request
from datetime import datetime, timezone
from typing import Any

ROOT=pathlib.Path('/data/wyt/b1-memrl-r77-mechanism')
CODE=pathlib.Path('/data/wyt/b1-r72-validate-20260904/research_pipeline')
if str(CODE) not in sys.path:sys.path.insert(0,str(CODE))
import failure_memory_memrl_ab_identification_r48 as r48

MANIFEST=pathlib.Path('/data/wyt/b1-memrl-r59-overlay-44960f8c/generated/d2-failure-memory-provenance-r59-llama-executor-replication-manifest.json')
SELECTION=pathlib.Path('/data/wyt/b1-memrl-r53-full350-execution/fresh-support-r54v2/fresh-validation-selection.json')
HIST_COMPLETED=pathlib.Path('/data/wyt/b1-memrl-r59-llama-execution/ab-r61/completed-ab-arms.jsonl')
M1=ROOT/'R77_M1_DIVERGENCE_LOCALIZATION.json'
M2A=ROOT/'R77_M2A_EXACT_GREEDY_REPLAY.json'
M2B=ROOT/'R77_M2B_EXACT_SAME_STATE_LOGIT_PROBE.json'
CLEAN_SOURCE=pathlib.Path('/data/wyt/b1-r77-clean-memrl')
TASKS=['125','136','193','327']
ARMS=['A_content_only','B_raw_provenance']
HIST_OUTCOME={('125','A_content_only'):True,('125','B_raw_provenance'):False,('136','A_content_only'):False,('136','B_raw_provenance'):True,('193','A_content_only'):False,('193','B_raw_provenance'):True,('327','A_content_only'):True,('327','B_raw_provenance'):False}
EXPECTED_SHA={MANIFEST:'2add9259f78d5d8a63aad10fc15c9d7cfaf7a14f58b670e61279930b79c81340',SELECTION:'39957119208258bd0bbd7a9a613cfa3403e9693229cb9452714c655774ad071c',HIST_COMPLETED:'34747ca158bf33a354516b3480975483b6214e3c00fc97e78325ae663f04af38'}

def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
def rows(p):return [json.loads(x) for x in pathlib.Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def append(p,row):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def normobs(x):return '\n'.join(z.rstrip() for z in str(x or '').strip().splitlines())

def preflight():
 for p,h in EXPECTED_SHA.items():
  if sha(p)!=h:raise RuntimeError(f'file-sha-drift:{p}')
 m1,m2a,m2b=map(load,[M1,M2A,M2B])
 if m1.get('status')!='R77_M1_DIVERGENCE_LOCALIZATION_COMPLETE_ZERO_MODEL' or m2a.get('status')!='R77_M2A_EXACT_GREEDY_REPLAY_PASS' or m2b.get('status')!='R77_M2B_EXACT_SAME_STATE_LOGIT_PROBE_COMPLETE':raise RuntimeError('mechanism-parent-status-drift')
 if any(not x.get('normalized_action_matches_historical') for x in m2a['rows']):raise RuntimeError('M2A-fidelity-not-pass')
 for p,h in [(M1,m1['receipt_sha256']),(M2A,m2a['receipt_sha256']),(M2B,m2b['receipt_sha256'])]:
  if h!=digest({k:v for k,v in load(p).items() if k!='receipt_sha256'}):raise RuntimeError(f'parent-receipt-invalid:{p}')
 m0=load(MANIFEST);m=copy.deepcopy(m0);e=m['execution_manifest']
 if e['models']['llm']['temperature']!=0.0:raise RuntimeError('temperature-drift')
 head=subprocess.check_output(['git','-C',str(CLEAN_SOURCE),'rev-parse','HEAD'],text=True).strip();dirty=subprocess.check_output(['git','-C',str(CLEAN_SOURCE),'status','--porcelain'],text=True).strip()
 if head!=e['source']['revision'] or dirty:raise RuntimeError('clean-source-drift')
 for rel,h in e['source']['pinned_source_file_sha256'].items():
  if sha(CLEAN_SOURCE/rel)!=h:raise RuntimeError(f'pinned-source-drift:{rel}')
 split=CLEAN_SOURCE/e['confirmatory_units']['split']
 if sha(split)!=e['confirmatory_units']['split_sha256']:raise RuntimeError('split-drift')
 image=subprocess.check_output(['docker','image','inspect',e['runtime_image']['execution_tag'],'--format','{{.Id}}'],text=True).strip()
 if image!=e['runtime_image']['id']:raise RuntimeError('image-drift')
 with urllib.request.urlopen(e['external_runtime_adapter']['loopback_base_url'].rstrip('/')+'/models',timeout=5) as rr:ids={str(x.get('id')) for x in json.loads(rr.read().decode()).get('data') or []}
 need={e['external_runtime_adapter']['llm_model_id'],e['external_runtime_adapter']['embedding_model_id']}
 if need-ids:raise RuntimeError('loopback-model-route-drift')
 m['execution_manifest']['source']['checkout']=str(CLEAN_SOURCE)
 sel=load(SELECTION);selby={str(x['validation_task_id']):x for x in sel['primary_records']};make_prompt=r48.prompt_builder(m);prompts={}
 for tid in TASKS:
  pair=r48.render_pair(list(selby[tid]['selected']),tid)
  for arm in ARMS:prompts[(tid,arm)]=make_prompt(pair[arm])
 histrows=rows(HIST_COMPLETED);hledger={(str(x['task_id']),str(x['arm'])):x for x in histrows};htraces={(tid,arm):load(hledger[(tid,arm)]['trace_file']) for tid in TASKS for arm in ARMS}
 m1by={str(x['task_id']):x for x in m1['rows']};m2aby={(str(x['task_id']),str(x['arm'])):x for x in m2a['rows']}
 plan=[];ordn=0
 for tid in TASKS:
  target=int(m1by[tid]['first_normalized_action_divergence_action_index'])
  for native,forced in [('A_content_only','B_raw_provenance'),('B_raw_provenance','A_content_only')]:
   replay_arm='B' if forced=='B_raw_provenance' else 'A';forced_text=str(m2aby[(tid,replay_arm)]['generated_text']);
   plan.append({'ordinal':ordn,'task_id':tid,'native_arm':native,'forced_branch_arm':forced,'target_action_index':target,'native_prompt_sha256':hashlib.sha256(prompts[(tid,native)].encode()).hexdigest(),'forced_response_sha256':hashlib.sha256(forced_text.encode()).hexdigest(),'historical_native_terminal':HIST_OUTCOME[(tid,native)],'historical_forced_branch_terminal':HIST_OUTCOME[(tid,forced)]});ordn+=1
 pf={'schema_version':'1.0','paper_id':'D2-PAPER-FAILURE-MEMORY-PROVENANCE','receipt_id':'D2-FAILURE-MEMORY-PROVENANCE-R77-M3-BRANCH-RESPONSE-MEDIATION-PLAN','status':'R77_M3_BRANCH_RESPONSE_MEDIATION_FROZEN_PRE_EXECUTION','role':'POST_HOC_BRANCH_RESPONSE_MEDIATION_NOT_PRIMARY_INFERENCE','bindings':{'M1_file_sha256':sha(M1),'M1_receipt_sha256':m1['receipt_sha256'],'M2A_file_sha256':sha(M2A),'M2A_receipt_sha256':m2a['receipt_sha256'],'M2B_file_sha256':sha(M2B),'M2B_receipt_sha256':m2b['receipt_sha256'],'manifest_file_sha256':sha(MANIFEST),'historical_completed_file_sha256':sha(HIST_COMPLETED)},'clean_source_commit':head,'runtime_image_id':image,'temperature':0.0,'do_sample':False,'intervention':'Replay the native historical pre-divergence assistant responses on a fresh environment, require actual OS observations to match the historical native prefix, then inject the opposite arm exact-greedy natural branch response at the first normalized-action divergence and resume freely under the original native system prompt. This swaps branch response (reasoning+action), not action alone.','planned_runs':8,'plan':plan,'changes_R72_R73_primary_inference':False}
 pf['receipt_sha256']=digest(pf);(ROOT/'R77_M3_BRANCH_RESPONSE_MEDIATION_PLAN.json').write_text(json.dumps(pf,ensure_ascii=False,indent=2)+'\n')
 return m,prompts,htraces,m1by,m2aby,pf

def run_one(m,adapter,prompts,htraces,m1by,m2aby,item,out):
 tid=item['task_id'];native=item['native_arm'];forced=item['forced_branch_arm'];target=item['target_action_index'];native_trace=htraces[(tid,native)];forced_key='B' if forced=='B_raw_provenance' else 'A';forced_response=m2aby[(tid,forced_key)]['generated_text']
 e=m['execution_manifest'];root=pathlib.Path(e['source']['checkout']);llb=root/'3rdparty'/'LifelongAgentBench'
 for p in [root,llb]:
  if str(p) not in sys.path:sys.path.insert(0,str(p))
 from memrl.lifelongbench_eval.task_wrappers import build_task
 from src.agents.instance.language_model_agent import LanguageModelAgent
 from src.typings import Session,SampleStatus,SessionEvaluationOutcome,ChatHistoryItem,Role
 task,tname=build_task(task='os',data_file_path=str(root/e['confirmatory_units']['split']),max_round=int(e['source_build']['max_steps']),os_timeout=int(e['source_build']['os_timeout_seconds']))
 session=Session(task_name=tname,sample_index=tid);agent=LanguageModelAgent(language_model=adapter,system_prompt=prompts[(tid,native)]);events=[];free_actions=[]
 try:
  task.reset(session)
  # Initial chat history must match historical native trace exactly.
  for i in range(3):
   got=session.chat_history.get_item_deep_copy(i);exp=native_trace['chat_messages'][i]
   role='user' if str(got.role)=='user' else 'agent'
   if role!=exp['role'] or str(got.content)!=str(exp['content']):raise RuntimeError(f'initial-history-drift:{tid}:{native}:{i}')
  # Replay native pre-divergence branch responses and verify resulting observations.
  for j in range(target):
   resp=str(native_trace['actions'][j]['response']);session.chat_history.inject(ChatHistoryItem(role=Role.AGENT,content=resp));task.interact(session)
   if session.sample_status!=SampleStatus.RUNNING:raise RuntimeError(f'prefix-terminated-early:{tid}:{native}:{j}:{session.sample_status}')
   got=session.chat_history.get_item_deep_copy(-1);exp_idx=4+2*j;exp=native_trace['chat_messages'][exp_idx]
   if str(got.role)!='user' or normobs(got.content)!=normobs(exp['content']):raise RuntimeError(f'prefix-observation-drift:{tid}:{native}:{j}')
   events.append({'phase':'native_prefix','action_index':j,'response_sha256':hashlib.sha256(resp.encode()).hexdigest(),'observation_sha256':hashlib.sha256(normobs(got.content).encode()).hexdigest()})
  # Cross-force the opposite natural branch response.
  session.chat_history.inject(ChatHistoryItem(role=Role.AGENT,content=forced_response));task.interact(session)
  events.append({'phase':'forced_branch','action_index':target,'forced_branch_arm':forced,'response_sha256':hashlib.sha256(forced_response.encode()).hexdigest(),'sample_status_after':str(session.sample_status)})
  # Resume the original prompt freely from the intervened closed-loop state.
  while session.sample_status==SampleStatus.RUNNING:
   agent.inference(session);resp=str(session.chat_history.get_item_deep_copy(-1).content or '');free_actions.append(resp);task.interact(session)
   if len(free_actions)>int(e['source_build']['max_steps'])*2:raise RuntimeError('free-continuation-step-ceiling')
  task.complete(session);outcome=getattr(getattr(session,'evaluation_record',None),'outcome',None);success=(outcome==SessionEvaluationOutcome.CORRECT)
  chat=[]
  for i in range(session.chat_history.get_value_length()):
   x=session.chat_history.get_item_deep_copy(i);chat.append({'role':str(x.role),'content':str(x.content or '')})
  result={'task_id':tid,'native_arm':native,'forced_branch_arm':forced,'target_action_index':target,'terminal_success':success,'evaluation_outcome':str(outcome),'historical_native_terminal':HIST_OUTCOME[(tid,native)],'historical_forced_branch_terminal':HIST_OUTCOME[(tid,forced)],'terminal_matches_opposite_historical_branch':success is HIST_OUTCOME[(tid,forced)],'terminal_differs_from_native_historical':success is not HIST_OUTCOME[(tid,native)],'native_prefix_actions_replayed':target,'free_continuation_inferences':len(free_actions),'events':events,'chat_messages':chat}
  tp=out/'trace.json';tp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');result['trace_file']=str(tp);result['trace_file_sha256']=sha(tp);result.pop('chat_messages');return result
 finally:
  try:task.release()
  except Exception:pass

def main():
 ROOT.mkdir(parents=True,exist_ok=True);m,prompts,htraces,m1by,m2aby,plan=preflight();outroot=ROOT/'m3-branch-response-mediation';outroot.mkdir(parents=True,exist_ok=True);started=outroot/'started.jsonl';completed=outroot/'completed.jsonl'
 if started.exists() or completed.exists():raise RuntimeError('R77-M3-existing-exposure-no-implicit-rerun')
 adapter=r48.r47base.build_adapter(m)
 for item in plan['plan']:
  ad=outroot/f"{item['ordinal']:02d}-{item['task_id']}-{item['native_arm']}-force-{item['forced_branch_arm']}";ad.mkdir(parents=True,exist_ok=False);append(started,{**item,'status':'STARTED','at':now(),'no_retry_if_exposed':True})
  try:
   r=run_one(m,adapter,prompts,htraces,m1by,m2aby,item,ad);r['ordinal']=item['ordinal'];r['status']='COMPLETE';r['completed_at']=now();append(completed,r);print(json.dumps({k:r[k] for k in ['task_id','native_arm','forced_branch_arm','terminal_success','historical_native_terminal','historical_forced_branch_terminal','terminal_matches_opposite_historical_branch','free_continuation_inferences']},sort_keys=True),flush=True)
  except Exception as ex:
   f={'status':'EXPOSED_FAILURE_NO_RETRY','task_id':item['task_id'],'native_arm':item['native_arm'],'forced_branch_arm':item['forced_branch_arm'],'error_type':type(ex).__name__,'error':str(ex),'at':now()};(ad/'failure.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n');raise
 rr=rows(completed)
 if len(rr)!=8:raise RuntimeError(f'M3-incomplete:{len(rr)}')
 taskrows=[]
 for tid in TASKS:
  a=next(x for x in rr if x['task_id']==tid and x['native_arm']=='A_content_only');b=next(x for x in rr if x['task_id']==tid and x['native_arm']=='B_raw_provenance')
  taskrows.append({'task_id':tid,'A_prompt_force_B_terminal':a['terminal_success'],'B_prompt_force_A_terminal':b['terminal_success'],'historical_A_B':[HIST_OUTCOME[(tid,'A_content_only')],HIST_OUTCOME[(tid,'B_raw_provenance')]],'both_cross_forced_terminals_match_opposite_historical_branches':bool(a['terminal_matches_opposite_historical_branch'] and b['terminal_matches_opposite_historical_branch']),'cross_forcing_changes_terminal_both_directions':bool(a['terminal_differs_from_native_historical'] and b['terminal_differs_from_native_historical'])})
 result={'schema_version':'1.0','paper_id':plan['paper_id'],'receipt_id':'D2-FAILURE-MEMORY-PROVENANCE-R77-M3-BRANCH-RESPONSE-MEDIATION-RESULT','status':'R77_M3_BRANCH_RESPONSE_MEDIATION_COMPLETE','role':'POST_HOC_BRANCH_RESPONSE_MEDIATION_NOT_PRIMARY_INFERENCE','plan_receipt_sha256':plan['receipt_sha256'],'arm_runs':8,'task_rows':taskrows,'full_bidirectional_terminal_swap_count':sum(int(x['both_cross_forced_terminals_match_opposite_historical_branches']) for x in taskrows),'interpretation_boundary':'A successful swap shows the first divergent full assistant branch response is sufficient, conditional on the replayed native prefix and original system prompt, to redirect the subsequent closed-loop outcome. It does not isolate action from contemporaneous reasoning text and is post-hoc selected.','changes_R72_R73_primary_inference':False,'new_model_trajectories':8}
 result['receipt_sha256']=digest(result);(ROOT/'R77_M3_BRANCH_RESPONSE_MEDIATION_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
