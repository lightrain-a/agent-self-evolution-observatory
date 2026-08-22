from __future__ import annotations

import fcntl,hashlib,json,os,re
from pathlib import Path
from typing import Any,Mapping

from .pre_experiment_compiler import compile_pre_experiment_card
from .reopened_p0_authorization import validate_p0_authorization
from .reopened_p0_plan import validate_p0_plan

SCHEMA_VERSION='1.0'
PASS='P0_PRE_EXPERIMENT_COMPILER_PASS_FRESH_LEASE_REQUIRED'
BLOCK='P0_PRE_EXPERIMENT_COMPILER_BLOCKED'
ZERO={'scientific':False,'experiment':False,'gpu':False,'submission':False}
REQ_TOP=('models','datasets','seeds','scope','analysis','governance','pre_experiment')
REQ_PRE=('paper_design','principle_certificate','protocol_validity','updater_competence','parameter_provenance','competence','identifiability','statistics','throughput','recovery','outcomes')

def _text(v:Any)->str:return str(v or '').strip()
def _digest(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def _slug(v:str)->str:return re.sub(r'[^A-Za-z0-9_.-]+','-',v).strip('-')[:180] or 'unknown'
def build_p0_config(*,p0_plan:Mapping[str,Any],p0_authorization:Mapping[str,Any],runtime_supplement:Mapping[str,Any])->dict[str,Any]:
 if not validate_p0_plan(p0_plan):raise RuntimeError('valid frozen confirmatory P0 plan required')
 if not validate_p0_authorization(p0_authorization):raise RuntimeError('valid P0 lifecycle authorization required')
 if _text(p0_plan.get('p0_authorization_sha256'))!=_text(p0_authorization.get('p0_authorization_sha256')):raise RuntimeError('P0 adapter authority/plan lineage mismatch')
 runtime=dict(runtime_supplement or {});missing=[k for k in REQ_TOP if not runtime.get(k)];pre=runtime.get('pre_experiment') or {};missing.extend(f'pre_experiment.{k}' for k in REQ_PRE if not pre.get(k))
 if missing:raise RuntimeError('P0 runtime supplement missing: '+','.join(missing))
 spec=p0_plan.get('plan_spec') or {};scope=dict(runtime.get('scope') or {});analysis=dict(runtime.get('analysis') or {});gov=dict(runtime.get('governance') or {});pre=dict(pre)
 if _text(scope.get('confirmatory_split_id'))!=_text(spec.get('evaluation_split')):raise RuntimeError('P0 runtime confirmatory split must exactly match frozen P0 plan')
 if scope.get('uses_local_f0_data_in_confirmatory_statistic') is not False:raise RuntimeError('P0 runtime must explicitly exclude local-F0 data from confirmatory statistic')
 arms=spec.get('arms') or [];units=int(spec.get('requested_units') or 0);episodes=units*max(1,len(arms));cap=p0_authorization.get('p0_budget') or {}
 declared=int(scope.get('worst_case_environment_episodes') or scope.get('expected_environment_episodes') or 0)
 if declared and declared>episodes:raise RuntimeError('P0 runtime episode claim exceeds frozen confirmatory plan')
 scope.setdefault('expected_environment_episodes',episodes);scope.setdefault('worst_case_environment_episodes',episodes)
 if not int(scope.get('max_steps') or 0):raise RuntimeError('P0 runtime scope.max_steps required')
 gov={**gov,'scientific_stage':str(gov.get('scientific_stage') or 'p0-method')}
 return {'schema_version':'2.3','idea_id':_text(p0_plan.get('contract_id')),'phase':'P0','governance':gov,'models':list(runtime['models']),'datasets':list(runtime['datasets']),'seeds':list(runtime['seeds']),'scope':scope,'analysis':analysis,'resource_cap':{'max_gpus':1,'gpu_hours':float(cap.get('max_gpu_hours') or 0),'wall_hours':float(runtime.get('wall_hours') or max(1,float(cap.get('max_gpu_hours') or 0)*1.5)),'episodes':episodes},'pre_experiment':pre,'reopen_p0_lineage':{'p0_plan_sha256':_text(p0_plan.get('p0_plan_sha256')),'p0_authorization_sha256':_text(p0_authorization.get('p0_authorization_sha256')),'evidence_adjudication_sha256':_text(p0_plan.get('evidence_adjudication_sha256')),'fresh_confirmatory_split':_text(spec.get('evaluation_split')),'local_f0_data_excluded':True,'local_f0_pre_experiment_reuse_forbidden':True,'local_f0_lease_reuse_forbidden':True,'adapter_cannot_authorize_execution':True}}
def identity(r:Mapping[str,Any])->dict[str,Any]:return {k:r.get(k) for k in ('contract_id','contract_sha256','p0_plan_sha256','p0_authorization_sha256','runtime_supplement_sha256','config_sha256','pre_experiment_card_sha256','passed_gates','gate_count','status')}
def compile_p0_pre_experiment(*,p0_plan:Mapping[str,Any],p0_authorization:Mapping[str,Any],runtime_supplement:Mapping[str,Any],data_root:Path)->dict[str,Any]:
 cfg=build_p0_config(p0_plan=p0_plan,p0_authorization=p0_authorization,runtime_supplement=runtime_supplement);card=compile_pre_experiment_card(_text(p0_plan.get('contract_id')),cfg,Path(data_root));passed=card.get('execution_authorized') is True
 r={'schema_version':SCHEMA_VERSION,'receipt_type':'reopen-p0-pre-experiment-adapter','contract_id':_text(p0_plan.get('contract_id')),'contract_sha256':_text(p0_plan.get('contract_sha256')),'p0_plan_sha256':_text(p0_plan.get('p0_plan_sha256')),'p0_authorization_sha256':_text(p0_authorization.get('p0_authorization_sha256')),'runtime_supplement_sha256':_digest(dict(runtime_supplement)),'config_sha256':_digest(cfg),'pre_experiment_card_sha256':_digest(card),'pre_experiment_card':card,'passed_gates':int(card.get('passed_gates') or 0),'gate_count':int(card.get('gate_count') or 0),'compiler_blockers':[str(x) for x in card.get('blockers') or []],'status':PASS if passed else BLOCK,'compiler_execution_ready':passed,'effective_execution_authorized':False,'fresh_experiment_lease_required':True,'fresh_run_lineage_required':True,'local_f0_card_reuse_forbidden':True,'local_f0_lease_reuse_forbidden':True,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False};r['p0_adapter_sha256']=_digest(identity(r));return r
def validate_p0_pre_experiment(r:Mapping[str,Any])->bool:
 if r.get('receipt_type')!='reopen-p0-pre-experiment-adapter' or r.get('status') not in {PASS,BLOCK}:return False
 passed=r.get('compiler_execution_ready') is True
 if r.get('status')!=(PASS if passed else BLOCK) or int(r.get('gate_count') or 0)!=8:return False
 if r.get('effective_execution_authorized') is not False or r.get('fresh_experiment_lease_required') is not True or r.get('fresh_run_lineage_required') is not True or r.get('local_f0_card_reuse_forbidden') is not True or r.get('local_f0_lease_reuse_forbidden') is not True:return False
 if any(r.get(k) is not False for k in ('scientific_authority','experiment_authority','gpu_authority','submission_authority')):return False
 if _digest(r.get('pre_experiment_card') or {})!=_text(r.get('pre_experiment_card_sha256')):return False
 return _text(r.get('p0_adapter_sha256'))==_digest(identity(r))
def _dir(root:Path)->Path:
 root=Path(root);return root if root.name=='scientific-contract-p0-pre-experiment' else root/'scientific-contract-p0-pre-experiment'
def publish_p0_pre_experiment(root:Path,r:Mapping[str,Any])->dict[str,Any]:
 if not validate_p0_pre_experiment(r):raise RuntimeError('invalid P0 Pre-Experiment receipt')
 d=_dir(root);d.mkdir(parents=True,exist_ok=True);cid=_text(r.get('contract_id'));path=d/f'{_slug(cid)}.json';lock=d/f'.{_slug(cid)}.lock'
 with lock.open('a+') as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX);row=json.loads(path.read_text()) if path.exists() else {'schema_version':SCHEMA_VERSION,'contract_id':cid,'contract_sha256':_text(r.get('contract_sha256')),'events':[],'authority':dict(ZERO)};sha=_text(r.get('p0_adapter_sha256'))
  for e in row.get('events') or []:
   p=e.get('receipt') or {} if isinstance(e,Mapping) else {}
   if isinstance(p,Mapping) and _text(p.get('p0_adapter_sha256'))==sha:return row
  at=str((r.get('pre_experiment_card') or {}).get('compiled_at') or '');ev={'event_type':'reopen-p0-pre-experiment-adapter','receipt':dict(r),'recorded_at':at,'execution_authorized':False};ev['event_id']=_digest([cid,len(row.get('events') or []),sha,at])[:24];row.setdefault('events',[]).append(ev);row['updated_at']=at;tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path);return row
def public_p0_pre_experiment(root:Path,contract_id:str)->dict[str,Any]:
 empty={'status':'P0_PRE_EXPERIMENT_COMPILER_REQUIRED','p0_adapter_sha256':'','passed_gates':0,'gate_count':8,'compiler_blocker_count':0,'compiler_execution_ready':False,'effective_execution_authorized':False,'authority':dict(ZERO)};path=_dir(root)/f'{_slug(contract_id)}.json'
 if not path.exists():return empty
 try:row=json.loads(path.read_text())
 except Exception:return {**empty,'status':'P0_PRE_EXPERIMENT_LEDGER_INVALID'}
 rs=[e.get('receipt') or {} for e in row.get('events') or [] if isinstance(e,Mapping) and isinstance(e.get('receipt'),Mapping)];r=rs[-1] if rs else {}
 if not r or not validate_p0_pre_experiment(r):return {**empty,'status':'P0_PRE_EXPERIMENT_LEDGER_INVALID'}
 return {**empty,'status':_text(r.get('status')),'p0_adapter_sha256':_text(r.get('p0_adapter_sha256')),'passed_gates':int(r.get('passed_gates') or 0),'gate_count':int(r.get('gate_count') or 0),'compiler_blocker_count':len(r.get('compiler_blockers') or []),'compiler_execution_ready':r.get('compiler_execution_ready') is True,'effective_execution_authorized':False}
