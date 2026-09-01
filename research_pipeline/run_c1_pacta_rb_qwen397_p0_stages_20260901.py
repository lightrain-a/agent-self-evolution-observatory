#!/usr/bin/env python3
"""Prepare, writer, binder, and shadow/gate stages for Qwen397 PACTA P0."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from typing import Any
from research_pipeline.c1_pacta_rb_qwen397 import BRANCHES,PILOT_SALT,RANDOM_SALT,atomic_json,build_shadow_schedule,gate,parse_first_decision,rate_matched_random,sha256_file,sha256_text,writer_twins_valid
from research_pipeline.c1_pacta_rb_qwen397_p0_core import *

def jsonl(path:Path,rows:list[dict[str,Any]])->str:
 raw=''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows).encode();return atomic_bytes(path,raw)

def pilot_units(root:Path)->list[dict[str,Any]]:
 s=load(root/'pilot-split.json');ids=[x['unit_id'] for x in s['pilot']];by={u['unit_id']:u for u in units()}
 if len(ids)!=6 or len(set(ids))!=6 or any(x not in by for x in ids):raise RuntimeError('STOP_PILOT_SPLIT_DRIFT')
 if set(ids)&{x['unit_id'] for x in s['sealed']}:raise RuntimeError('STOP_SEALED_OVERLAP')
 return [by[x] for x in ids]

def prepare(root:Path)->dict[str,Any]:
 if root.exists():raise RuntimeError('P0 root exists; no overwrite')
 hashes=verify_inputs();b=binding();all_units=units();r=ranked(all_units,PILOT_SALT);pilot,sealed=r[:6],r[6:];root.mkdir(parents=True)
 random_ranking=[u['unit_id'] for u in ranked(pilot,RANDOM_SALT)]
 contract={'schema_version':1,'created_at_utc':now(),'experiment':'C1-PACTA-RB-QWEN397-P0-20260901','status':'FROZEN_PRE_WRITER','carrier':'ReasoningBank + SWE-bench Verified + official MiniSWEAgent','official_commit':'ed80611788292ea739f1effd31f16c53823b8a0d','model':MODEL,'enable_thinking':False,'pool_count':9,'pilot_count':6,'sealed_count':3,'pilot_salt':PILOT_SALT,'random_salt':RANDOM_SALT,'pilot':[u['unit_id'] for u in pilot],'sealed':[u['unit_id'] for u in sealed],'random_ranking_pre_shadow':random_ranking,'writer':{'calls':12,'temperature':WRITER_TEMP,'max_completion_tokens':WRITER_MAX,'branches':['SUCCESSFUL_SI','FAILED_SI'],'retries':0},'binder':{'calls':12,'temperature':BINDER_TEMP,'max_completion_tokens':BINDER_MAX,'instruction':BINDER_INSTRUCTION,'current_state':INITIAL_STATE,'retries':0},'shadow':{'calls':144,'temperature':POLICY_TEMP,'max_completion_tokens':FIRST_DECISION_MAX,'gate':'min(B1,B2) > max(WS,WF)','nondegenerate':'2..5/6','retries':0},'final':{'calls':288,'temperature':POLICY_TEMP,'max_completion_tokens':FIRST_DECISION_MAX,'retries':0},'primary':'mean(U_A3_PACTA - U_A2_RATE_MATCHED_RANDOM)','thresholds':{'mean_D_select_ge':0.05,'positive_gt_negative':True,'mean_A3_A0_gt':0.0,'mean_A3_A1_ge':0.0},'token_caps':{'scientific_input':INPUT_CAP,'scientific_output':OUTPUT_CAP},'replacement':False,'top_up':False,'terminal_locked':True,'other_models_locked':True,'R10_locked':True}
 atomic_json(root/'contract.json',contract)
 split_doc={'schema_version':1,'created_at_utc':now(),'status':'FROZEN_OUTCOME_BLIND','pilot':[{'unit_id':u['unit_id'],'pilot_rank':sha256_text(PILOT_SALT+'|'+u['unit_id']),'random_rank':sha256_text(RANDOM_SALT+'|'+u['unit_id'])} for u in pilot],'sealed':[{'unit_id':u['unit_id'],'pilot_rank':sha256_text(PILOT_SALT+'|'+u['unit_id'])} for u in sealed],'sealed_provider_calls':0};atomic_json(root/'pilot-split.json',split_doc)
 shadow=build_shadow_schedule(pilot);jsonl(root/'shadow-schedule.jsonl',shadow)
 audit={'schema_version':1,'created_at_utc':now(),'status':'P0_PREPARE_PASS','static_inputs':hashes,'provider_binding':b,'valid_pool_count':9,'valid_repository_count':9,'pilot':[u['unit_id'] for u in pilot],'sealed':[u['unit_id'] for u in sealed],'random_ranking_pre_shadow':random_ranking,'sealed_provider_calls':0,'contract_sha256':sha256_file(root/'contract.json'),'split_sha256':sha256_file(root/'pilot-split.json'),'shadow_schedule_sha256':sha256_file(root/'shadow-schedule.jsonl'),'writer_calls':0,'binder_calls':0,'shadow_calls':0,'final_calls':0};atomic_json(root/'prepare-audit.json',audit);return audit

def writer_rows(root:Path)->dict[tuple[str,str],dict[str,Any]]:
 rows=[load(p) for p in sorted((root/'writer').glob('*.json'))]
 if len(rows)!=12:raise RuntimeError('writer incomplete')
 return {(r['unit_id'],r['branch']):r for r in rows}
def binder_rows(root:Path)->dict[tuple[str,str],dict[str,Any]]:
 rows=[load(p) for p in sorted((root/'binder').glob('*.json'))]
 if len(rows)!=12:raise RuntimeError('binder incomplete')
 return {(r['unit_id'],r['branch']):r for r in rows}

def writer(root:Path)->dict[str,Any]:
 if (root/'writer-result.json').exists() or (root/'writer').exists():raise RuntimeError('writer phase exists; no retry/overwrite')
 verify_inputs();b=binding();provider=Provider(require_key(),root,b['requested_model'],b['resolved_model']);rows=[]
 for u in pilot_units(root):
  for br in BRANCHES:
   messages,context=writer_messages(u,br);resp=provider.call('writer',u['unit_id']+'__'+br,messages,WRITER_MAX,WRITER_TEMP)
   if resp['provider']['finish_reason']!='stop':raise RuntimeError(f"STOP_WRITER_OUTPUT_INCOMPLETE:{u['unit_id']}:{br}:{resp['provider']['finish_reason']}")
   memory,count=validate_memory(resp['content'])
   row={'schema_version':1,'unit_id':u['unit_id'],'source_task_id':u['source_task_id'],'future_task_id':u['future_task_id'],'branch':br,'trajectory_sha256':u['writer_input_trajectory_sha256'],'source_task_sha256':u['source_task_sha256'],'requested_model':b['requested_model'],'resolved_model':b['resolved_model'],'temperature':WRITER_TEMP,'max_completion_tokens':WRITER_MAX,'context_sha256':sha256_text(context),'memory':memory,'memory_sha256':sha256_text(memory),'memory_item_count':count,'provider':resp['provider']};atomic_json(root/'writer'/f"{sha256_text(u['unit_id'])[:12]}__{br}.json",row);rows.append(row)
 for u in pilot_units(root):
  s=next(x for x in rows if x['unit_id']==u['unit_id'] and x['branch']=='success');f=next(x for x in rows if x['unit_id']==u['unit_id'] and x['branch']=='failure')
  if not writer_twins_valid(s,f):raise RuntimeError('HOLD_WRITER_REALIZATION:'+u['unit_id'])
 result={'schema_version':1,'created_at_utc':now(),'status':'WRITER_TWINS_PASS','calls':12,'units':6,'model_drift':0,**provider.phase_usage(),'sealed_provider_calls':0};atomic_json(root/'writer-result.json',result);return result

def binder_phase(root:Path)->dict[str,Any]:
 if load(root/'writer-result.json').get('status')!='WRITER_TWINS_PASS':raise RuntimeError('writer gate not passed')
 if (root/'binder-result.json').exists() or (root/'binder').exists():raise RuntimeError('binder phase exists; no retry/overwrite')
 b=binding();provider=Provider(require_key(),root,b['requested_model'],b['resolved_model']);mem=writer_rows(root);rows=[]
 for u in pilot_units(root):
  for br in BRANCHES:
   memory=mem[(u['unit_id'],br)]['memory'];messages,prompt=binder_messages(u,memory);resp=provider.call('binder',u['unit_id']+'__'+br,messages,BINDER_MAX,BINDER_TEMP)
   if resp['provider']['finish_reason']!='stop':raise RuntimeError(f"STOP_BINDER_OUTPUT_INCOMPLETE:{u['unit_id']}:{br}:{resp['provider']['finish_reason']}")
   note,words=validate_binding(resp['content']);row={'schema_version':1,'unit_id':u['unit_id'],'branch':br,'memory_sha256':sha256_text(memory),'prompt_sha256':sha256_text(prompt),'binding':note,'binding_sha256':sha256_text(note),'word_count':words,'requested_model':b['requested_model'],'resolved_model':b['resolved_model'],'provider':resp['provider']};atomic_json(root/'binder'/f"{sha256_text(u['unit_id'])[:12]}__{br}.json",row);rows.append(row)
 result={'schema_version':1,'created_at_utc':now(),'status':'BINDER_PASS','calls':12,'model_drift':0,**provider.phase_usage(),'sealed_provider_calls':0};atomic_json(root/'binder-result.json',result);return result

def policy_once(provider:Provider,stage:str,case:dict[str,Any],u:dict[str,Any],memory:str,note:str|None)->dict[str,Any]:
 messages=policy_messages(u,memory,note);resp=provider.call(stage,case['case_id'],messages,FIRST_DECISION_MAX,POLICY_TEMP)
 if resp['provider']['finish_reason']!='stop':raise RuntimeError(f"STOP_FIRST_DECISION_INCOMPLETE:{case['case_id']}:{resp['provider']['finish_reason']}")
 action=parse_first_decision(resp['content']);return {**case,'action_signature':action.strip(),'response_text_sha256':sha256_text(resp['content']),'provider':resp['provider'],'uses_scb':note is not None,'memory_sha256':sha256_text(memory),'binding_sha256':'' if note is None else sha256_text(note)}

def shadow_phase(root:Path)->dict[str,Any]:
 if load(root/'binder-result.json').get('status')!='BINDER_PASS':raise RuntimeError('binder gate not passed')
 if (root/'shadow-result.json').exists() or (root/'shadow'/'outcomes.jsonl').exists():raise RuntimeError('shadow phase exists; no retry/overwrite')
 b=binding();pilot=pilot_units(root);by={u['unit_id']:u for u in pilot};mem=writer_rows(root);notes=binder_rows(root);schedule=[json.loads(x) for x in (root/'shadow-schedule.jsonl').read_text().splitlines() if x.strip()]
 if len(schedule)!=144:raise RuntimeError('shadow geometry drift')
 inputs=[]
 for c in schedule:
  u=by[c['unit_id']];m=mem[(u['unit_id'],c['branch'])]['memory'];n=notes[(u['unit_id'],c['branch'])]['binding'];inputs.append({**c,'prompt_sha256':sha256_text(json.dumps(policy_messages(u,m,n),ensure_ascii=False,sort_keys=True)),'memory_sha256':sha256_text(m),'binding_sha256':sha256_text(n)})
 jsonl(root/'shadow-inputs.jsonl',inputs)
 provider=Provider(require_key(),root,b['requested_model'],b['resolved_model']);out=[]
 for c in schedule:
  u=by[c['unit_id']];m=mem[(u['unit_id'],c['branch'])]['memory'];n=notes[(u['unit_id'],c['branch'])]['binding'];out.append(policy_once(provider,'shadow',c,u,m,n))
 jsonl(root/'shadow'/'outcomes.jsonl',out);per=[];opened=[]
 for u in pilot:
  rows=[x for x in out if x['unit_id']==u['unit_id']];samples={'S1':[x['action_signature'] for x in rows if x['branch']=='success' and x['block']==1],'S2':[x['action_signature'] for x in rows if x['branch']=='success' and x['block']==2],'F1':[x['action_signature'] for x in rows if x['branch']=='failure' and x['block']==1],'F2':[x['action_signature'] for x in rows if x['branch']=='failure' and x['block']==2]};g=gate(samples);per.append({'unit_id':u['unit_id'],**g});opened.extend([u['unit_id']] if g['G'] else [])
 k=len(opened);ranking=load(root/'contract.json')['random_ranking_pre_shadow'];random_open=ranking[:k];geo=2<=k<=5;result={'schema_version':1,'created_at_utc':now(),'status':'SHADOW_GATE_PASS' if geo else 'HOLD_GATE_DEGENERATE_QWEN397','calls':144,**provider.phase_usage(),'per_unit':per,'K':k,'pacta_open':opened,'random_open':random_open,'random_rate_matched':len(random_open)==k,'geometry_pass':geo,'sealed_provider_calls':0};atomic_json(root/'shadow-result.json',result);return result

def main()->None:
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=DEFAULT_RUN);ap.add_argument('--phase',choices=('prepare','writer','binder','shadow'),required=True);a=ap.parse_args()
 result={'prepare':prepare,'writer':writer,'binder':binder_phase,'shadow':shadow_phase}[a.phase](a.root);print(json.dumps(result,ensure_ascii=False,sort_keys=True))
if __name__=='__main__':main()
