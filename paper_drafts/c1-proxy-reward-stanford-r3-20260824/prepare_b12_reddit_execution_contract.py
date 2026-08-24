#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

PAPER='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE';EXP='D2-PROXY-B12-REDDIT-CROSSDOMAIN-REPLICATION'
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode('utf-8')).hexdigest()
def load(p:Path)->dict[str,Any]:
 d=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(d,dict):raise RuntimeError(f'not object:{p}')
 return d
def req(x:bool,m:str):
 if not x:raise RuntimeError(m)
def writej(p:Path,d:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');os.replace(t,p)
def norm(t:Any)->str:return ' '.join(str(t or '').split())
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

def main():
 ap=argparse.ArgumentParser()
 for n in ['qualification','reddit_parquet','success_prompt','failure_prompt','memory_py','human_authority','env_file','runner','output']:
  ap.add_argument('--'+n.replace('_','-'),required=True,type=Path)
 ap.add_argument('--vendor-path',required=True,type=Path);a=ap.parse_args()
 q=load(a.qualification);req(q.get('status')=='B12_REDDIT_QUALIFIED_FOR_FROZEN_FOLLOWUP' and q['summary']['qualification_pass'] is True,'qualification not pass');req(q.get('provider_calls')==0,'qualification provider-call drift')
 for p in [a.reddit_parquet,a.success_prompt,a.failure_prompt,a.memory_py,a.human_authority,a.env_file,a.runner]:req(p.is_file(),f'missing:{p}')
 auth=load(a.human_authority);req(auth.get('paper_id')==PAPER and auth.get('decision')=='approve','human authority invalid');req((auth.get('future_repair_experiments') or {}).get('human_program_authorized') is True,'future program authority missing');req(auth.get('provider_credential_use_authorized_if_required_by_a_frozen_subcontract') is True,'provider credential authority missing');req(auth.get('claim_expansion_authorized') is False,'claim expansion drift')
 import pyarrow.parquet as pq
 rows={int(x['task_id']):x for x in pq.read_table(a.reddit_parquet,columns=['task_id','task_prompt','trajectory_json']).to_pylist()}
 source_index={int(x['task_id']):x for x in q['source_selection']};required=[int(x) for x in q['summary']['required_source_writer_tasks']];req(len(required)==4,'required source geometry drift')
 units=[]
 for tid in required:
  req(tid in rows and tid in source_index,f'required source missing:{tid}');summary=action_summary(str(rows[tid]['trajectory_json']));req(tsha(summary)==source_index[tid]['action_summary_sha256'],f'action summary drift:{tid}');units.append({'source_task':tid,'task_prompt':str(rows[tid]['task_prompt']),'action_summary_sha256':tsha(summary),'action_summary_chars':len(summary),'retrieved_by_future_tasks':sorted(int(x['task_id']) for x in q['eligible_future_support'] if int(x['top1_source_task'])==tid)})
 futures=[]
 for x in q['eligible_future_support']:
  futures.append({'future_task':int(x['task_id']),'task_prompt':str(x['intent']),'intent_template_id':int(x['intent_template_id']),'selected_source_task':int(x['top1_source_task']),'retrieval_similarity':float(x['top1_similarity']),'retrieval_margin':float(x['top1_margin']),'reference_answers':x['deterministic_reference_answers'],'evidence_sha256':x['released_evidence_sha256'],'released_state_sha256':x['released_state_sha256']})
 req(len(futures)==8 and len({x['intent_template_id'] for x in futures})==2,'future support drift')
 c={'schema_version':'1.0','paper_id':PAPER,'experiment_id':EXP,'status':'FROZEN_BEFORE_ANY_B12_PROVIDER_CALLS','frozen_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),'changed_assumption':'Replicate the label-only write and native transport test on a second WebArena domain (Reddit) using outcome-independent exact-retrieval support qualified before any B12 writer call.','qualification_binding':{'path':str(a.qualification.resolve()),'sha256':sha(a.qualification),'qualification_contract_sha256':q['contract_sha256']},'writer_stage':{'source_tasks':required,'source_units':units,'conditions':['success','failure'],'expected_provider_calls':8,'model':{'requested':'deepseek-v4-flash','temperature':0.0,'max_output_tokens':4096,'thinking':None,'provider_retries':0,'substitution_allowed':False},'success_prompt':{'path':str(a.success_prompt.resolve()),'sha256':sha(a.success_prompt)},'failure_prompt':{'path':str(a.failure_prompt.resolve()),'sha256':sha(a.failure_prompt)},'activation_rule':'Terminal stage activates only after all 8 paired writer units complete and parse into 1-3 memory items.'},'terminal_stage':{'task_units':futures,'future_task_count':8,'conditions':['success','failure'],'rollouts_per_task_per_condition':4,'expected_provider_calls':64,'model':{'requested':'doubao-seed-2.0-mini','expected_resolved':'doubao-seed-2-0-mini-260215','temperature':0.2,'max_output_tokens':900,'thinking':'disabled','provider_retries':0,'substitution_allowed':False},'primary_gate':{'statistic':'mean over 8 frozen Reddit future tasks of absolute success-rate difference between success-memory and failure-memory branches','min_mean_absolute_success_rate_difference':0.15,'permutation_p_lt':0.05,'permutation_repetitions':100000,'permutation_seed':20260824,'interpretation':'Both the practical floor and within-task permutation criterion must pass; sample size does not relax the Shopping gate.'},'missingness_policy':{'provider_retries':0,'stop_after_first_no_text_provider_failure':True,'top_up_failed_units':False,'replace_future_tasks':False,'replace_source_tasks':False}},'program_budget':{'writer_provider_call_ceiling':8,'terminal_provider_call_ceiling':64,'total_provider_call_ceiling':72,'training_runs':0,'gpu_runs':0},'execution_guards':{'single_writer_transaction_lock':True,'response_first_archival':True,'per_provider_post_stage_json':True,'aggregate_json_refreshed_after_each_provider_post':True,'csv_projection_refreshed_after_each_provider_post':True,'resumable_stage_cache':True,'fixed_order_chunking':True,'chunking_cannot_depend_on_outcomes':True},'source_bindings':{'reddit_parquet':{'path':str(a.reddit_parquet.resolve()),'sha256':sha(a.reddit_parquet)},'memory_py':{'path':str(a.memory_py.resolve()),'sha256':sha(a.memory_py)},'human_authority':{'path':str(a.human_authority.resolve()),'sha256':sha(a.human_authority)},'runner':{'path':str(a.runner.resolve()),'sha256':sha(a.runner)}},'provider_env_file':str(a.env_file.resolve()),'vendor_path':str(a.vendor_path.resolve()),'scope_boundary':{'second_domain':'reddit','source_support_selected_before_writer_outputs':True,'future_support_selected_before_writer_outputs':True,'future_outcomes_not_used_for_support':True,'no_retrieval_threshold_change':True,'no_live_browser_claim':True,'no_population_effect_claim':True,'no_writer_or_policy_invariance_claim':True,'no_claim_expansion':True},'authority':{'scientific_reopen_authority':True,'experiment_authority':True,'provider_call_authority':True,'gpu_authority':False,'claim_expansion_authority':False,'submission_authority':False}}
 raw=dict(c);c['contract_sha256']=hashlib.sha256(json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();writej(a.output,c);print(json.dumps({'status':c['status'],'contract_sha256':c['contract_sha256'],'writer_sources':required,'future_tasks':[x['future_task'] for x in futures],'call_ceiling':72,'primary_gate':c['terminal_stage']['primary_gate']},indent=2))
if __name__=='__main__':main()
