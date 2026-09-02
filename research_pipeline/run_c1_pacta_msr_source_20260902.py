#!/usr/bin/env python3
"""Acquire exactly-once native ReasoningBank source trajectories for the 10 fresh PACTA-MSR pairs."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import yaml
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json,sha256_file
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime_v7 import Container,SOURCE_MAX_COMPLETION_TOKENS,PACTA_FIRST_DECISION_BUDGET,execute_trajectory

ROOT=Path(__file__).resolve().parents[1]
POOL=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-fresh-pool-20260902.json'
POOL_SHA='2391967a3da363bcbbe87403599970854d7cf7ed82b249078b0469b36a8de59e'
RUNTIME=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-runtime-20260902-v1/normalization-qualification.json')
RUNTIME_SHA='7b876c9dc31e964868fa1c5cff3cd5ab3510e57162e65368023102822d933a01'
SOURCE_BUDGET_Q0=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-source-budget-q0-20260901-v2/qualification-result.json')
SOURCE_BUDGET_Q0_SHA='668848d930db9087617fbe839c11d77ca3d57e75a2787a32605ce13ddb530e25'
OFFICIAL=Path('/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026')
OFFICIAL_COMMIT='ed80611788292ea739f1effd31f16c53823b8a0d'
CONFIG=OFFICIAL/'third_party/src/minisweagent/config/extra/swebench.yaml'
CONFIG_SHA='d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41'
MODEL='qwen3.5-397b-a17b'
DEFAULT=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-source-20260902-v1')
ORDER_SALT='C1-PACTA-MSR-QWEN397-SOURCE-ACQUIRE-v1'

def now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def sha_text(x:str)->str:return hashlib.sha256(x.encode()).hexdigest()
def append(path:Path,row:dict[str,Any])->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('a',encoding='utf-8') as h:h.write(json.dumps(row,sort_keys=True)+'\n');h.flush();os.fsync(h.fileno())
def require_key()->str:
 k=os.environ.get('AA_API_KEY','')
 if not k:raise RuntimeError('STOP_PROVIDER_CREDENTIAL_NOT_CONFIGURED')
 return k

def verify()->tuple[list[dict[str,Any]],dict[str,Any]]:
 if sha256_file(POOL)!=POOL_SHA:raise RuntimeError('fresh pool drift')
 if sha256_file(RUNTIME)!=RUNTIME_SHA:raise RuntimeError('runtime qualification drift')
 if sha256_file(SOURCE_BUDGET_Q0)!=SOURCE_BUDGET_Q0_SHA:raise RuntimeError('source budget qualification drift')
 if sha256_file(CONFIG)!=CONFIG_SHA:raise RuntimeError('official config drift')
 head=subprocess.run(['git','-C',str(OFFICIAL),'rev-parse','HEAD'],text=True,capture_output=True,check=True).stdout.strip()
 if head!=OFFICIAL_COMMIT:raise RuntimeError('carrier commit drift')
 q=load(SOURCE_BUDGET_Q0)
 if q.get('decision')!='SOURCE_TRAJECTORY_BUDGET_16384_QUALIFIED' or q.get('qualified')!=6 or q.get('source_trajectory_output_budget')!=SOURCE_MAX_COMPLETION_TOKENS or q.get('pacta_first_decision_budget')!=PACTA_FIRST_DECISION_BUDGET:raise RuntimeError('source budget qualification invalid')
 p=load(POOL);runtime=load(RUNTIME)
 if p.get('candidate_count')!=10 or runtime.get('status')!='MSR_20_RUNTIME_READY' or runtime.get('source_qualified')!=10 or runtime.get('future_qualified')!=10:raise RuntimeError('fresh runtime support incomplete')
 by_runtime={x['instance_id']:x for x in runtime['rows']}
 rows=[]
 for u in p['units']:
  rr=by_runtime.get(u['source_task_id'])
  if not rr or rr.get('role')!='source' or not rr.get('exact_base_normalization_pass'):raise RuntimeError('source runtime missing '+u['source_task_id'])
  rows.append({**u,'digest_ref':rr['digest_ref']})
 if len(rows)!=10 or len({x['source_task_id'] for x in rows})!=10:raise RuntimeError('source geometry drift')
 return rows,q

def schedule(rows:list[dict[str,Any]])->list[dict[str,Any]]:
 out=[]
 for u in sorted(rows,key=lambda x:(sha_text(ORDER_SALT+'|'+x['unit_id']),x['unit_id'])):
  out.append({'sequence':len(out)+1,'unit_id':u['unit_id'],'source_task_id':u['source_task_id'],'future_task_id':u['future_task_id'],'repository':u['task_family'],'task_sha256':u['source_task_sha256'],'base_commit':u['source_base_commit'],'digest_ref':u['digest_ref'],'order_key':sha_text(ORDER_SALT+'|'+u['unit_id']),'logical_attempts':1,'selected_memory':'','future_task_executed':False})
 return out

def prepare(root:Path)->dict[str,Any]:
 if root.exists():raise RuntimeError('source root exists; no overwrite')
 rows,_=verify();sched=schedule(rows);root.mkdir(parents=True)
 contract={'schema_version':1,'created_at_utc':now(),'experiment':'C1-PACTA-MSR-QWEN397-SOURCE-20260902','status':'FROZEN_BEFORE_SOURCE_POLICY','model':MODEL,'source_max_completion_tokens':SOURCE_MAX_COMPLETION_TOKENS,'pacta_first_decision_budget_unchanged':PACTA_FIRST_DECISION_BUDGET,'fresh_pool_sha256':POOL_SHA,'runtime_qualification_sha256':RUNTIME_SHA,'source_budget_q0_sha256':SOURCE_BUDGET_Q0_SHA,'scheduled_source_units':10,'logical_attempts_per_source':1,'replacement':False,'top_up':False,'rate_limit_transport_recovery':{'max_retries':2,'backoff_seconds':[60,120],'only_when_no_model_content':True},'environment_command_timeout_seconds':60,'step_limit':250,'source_input_token_hard_cap':30000000,'source_output_token_hard_cap':1000000,'future_task_executions':0,'writer_calls':0,'binder_calls':0,'probe_calls':0,'shadow_calls':0,'final_calls':0,'forbidden':['replacement source','future task execution','writer','binder','MSR probe','shadow','gate','final','model switch']}
 atomic_json(root/'contract.json',contract);atomic_json(root/'acquisition-schedule.json',{'schema_version':1,'created_at_utc':now(),'status':'FROZEN','order_salt':ORDER_SALT,'schedule':sched,'scheduled_count':10,'replacement':False,'top_up':False,'future_task_executions':0})
 return {'status':'MSR_SOURCE_SCHEDULE_FROZEN','scheduled':10,'contract_sha256':sha256_file(root/'contract.json'),'schedule_sha256':sha256_file(root/'acquisition-schedule.json')}

def prelaunch(root:Path)->dict[str,Any]:
 if (root/'prelaunch-qualification.json').exists():raise RuntimeError('prelaunch exists; no overwrite')
 rows=[]
 for item in load(root/'acquisition-schedule.json')['schedule']:
  p=root/'prelaunch'/item['source_task_id'];c=None;ok=False;err=None
  try:c=Container(item['digest_ref'],item['base_commit'],p);ok=True
  except Exception as e:err=f'{type(e).__name__}: {e}'
  finally:
   if c is not None:c.cleanup()
  rows.append({'source_task_id':item['source_task_id'],'pass':ok,'error':err,'normalization_path':str(p/'exact-base-normalization.json') if ok else None,'normalization_sha256':sha256_file(p/'exact-base-normalization.json') if ok else None})
 out={'schema_version':1,'created_at_utc':now(),'status':'MSR_SOURCE_PRELAUNCH_PASS' if all(x['pass'] for x in rows) else 'HOLD_MSR_SOURCE_PRELAUNCH','qualified':sum(x['pass'] for x in rows),'total':10,'rows':rows,'provider_calls':0,'future_task_executions':0}
 atomic_json(root/'prelaunch-qualification.json',out);return out

def acquire(root:Path)->dict[str,Any]:
 key=require_key();rows,_=verify();by={x['source_task_id']:x for x in rows};pre=load(root/'prelaunch-qualification.json')
 if pre.get('status')!='MSR_SOURCE_PRELAUNCH_PASS' or pre.get('qualified')!=10:raise RuntimeError('source prelaunch not passed')
 config=yaml.safe_load(CONFIG.read_text());out=[];stop=None
 for item in load(root/'acquisition-schedule.json')['schedule']:
  u=by[item['source_task_id']];r=execute_trajectory(u['source_task_id'],u['source_task'],item['digest_ref'],root/f"source-{u['source_task_id']}",config,key,MODEL,MODEL,item['base_commit']);out.append(r);append(root/'acquisition-journal.jsonl',r);print(json.dumps({'source':u['source_task_id'],'validity':r['validity_status'],'terminal':r['terminal_status'],'logical_calls':r['provider_logical_calls'],'transport_attempts':r['provider_transport_attempts']}),flush=True)
  if r.get('failure_layer') is not None:stop=f"{u['source_task_id']}:{r['failure_layer']}";break
  if sum(int(x.get('input_tokens') or 0) for x in out)>30000000 or sum(int(x.get('output_tokens') or 0) for x in out)>1000000:stop='SOURCE_TOKEN_HARD_CAP';break
 valid=[x for x in out if x['validity_status']=='TRAJECTORY_BACKED_VALID'];decision='MSR_SOURCE_POOL_10_QUALIFIED' if len(out)==10 and len(valid)==10 else ('MSR_SOURCE_POOL_PARTIAL_STOP' if len(valid)>=8 else 'HOLD_MSR_SOURCE_SUPPORT_INSUFFICIENT')
 audit={'schema_version':1,'created_at_utc':now(),'decision':decision,'rows':out,'attempted':len(out),'valid':len(valid),'valid_repositories':len({by[x['source_task_id']]['task_family'] for x in valid}),'stop_reason':stop,'input_tokens':sum(int(x.get('input_tokens') or 0) for x in out),'output_tokens':sum(int(x.get('output_tokens') or 0) for x in out),'future_task_executions':0,'writer_calls':0,'binder_calls':0,'probe_calls':0,'shadow_calls':0,'final_calls':0,'claim_authority':'NO_MSR_METHOD_EFFECT_EVIDENCE'}
 atomic_json(root/'support-audit.json',audit);return audit

def main()->None:
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=DEFAULT);a.add_argument('--phase',choices=('prepare','prelaunch','acquire'),required=True);x=a.parse_args();result={'prepare':prepare,'prelaunch':prelaunch,'acquire':acquire}[x.phase](x.root);print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
