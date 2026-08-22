from __future__ import annotations

import fcntl,hashlib,json,os,re
from pathlib import Path
from typing import Any,Mapping

from .reopened_local_f0_run import validate_reopened_local_f0_run_start
from .reopened_p0_authorization import validate_p0_authorization
from .reopened_p0_plan import validate_p0_plan
from .reopened_p0_pre_experiment_adapter import PASS as P0_PRE_PASS,validate_p0_pre_experiment

SCHEMA_VERSION='1.0'
STATUS='P0_EXPERIMENT_LEASE_REQUEST_READY_EXPLICIT_ACQUIRE_REQUIRED'
ZERO={'scientific':False,'experiment':False,'gpu':False,'submission':False}

def _text(v:Any)->str:return str(v or '').strip()
def _digest(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def _slug(v:str)->str:return re.sub(r'[^A-Za-z0-9_.-]+','-',v).strip('-')[:180] or 'unknown'
def identity(r:Mapping[str,Any])->dict[str,Any]:
 return {k:r.get(k) for k in ('contract_id','contract_sha256','p0_adapter_sha256','p0_plan_sha256','p0_authorization_sha256','p0_plan_hash','local_f0_plan_hash','local_f0_lease_request_sha256','status')}

def build_p0_lease_request(*,p0_pre_experiment:Mapping[str,Any],p0_plan:Mapping[str,Any],p0_authorization:Mapping[str,Any],local_f0_run_start:Mapping[str,Any])->dict[str,Any]:
 if not validate_p0_pre_experiment(p0_pre_experiment) or p0_pre_experiment.get('status')!=P0_PRE_PASS or p0_pre_experiment.get('compiler_execution_ready') is not True:raise RuntimeError('P0 Pre-Experiment compiler PASS required before fresh P0 lease request')
 if not validate_p0_plan(p0_plan) or not validate_p0_authorization(p0_authorization):raise RuntimeError('valid P0 plan/authorization required')
 if not validate_reopened_local_f0_run_start(local_f0_run_start):raise RuntimeError('valid historical local-F0 run-start lineage required')
 cid=_text(p0_plan.get('contract_id'))
 if any(_text(x.get('contract_id'))!=cid for x in (p0_pre_experiment,p0_authorization,local_f0_run_start)):raise RuntimeError('P0 lease request contract lineage mismatch')
 if _text(p0_pre_experiment.get('p0_plan_sha256'))!=_text(p0_plan.get('p0_plan_sha256')) or _text(p0_pre_experiment.get('p0_authorization_sha256'))!=_text(p0_authorization.get('p0_authorization_sha256')):raise RuntimeError('P0 lease request P0 lineage mismatch')
 card=p0_pre_experiment.get('pre_experiment_card') or {};p0_hash=_text((card.get('research_execution_plan') or {}).get('plan_hash'));local_hash=_text(local_f0_run_start.get('plan_hash'));local_req=_text(local_f0_run_start.get('lease_request_sha256'))
 if not p0_hash or not local_hash or not local_req:raise RuntimeError('P0/local-F0 plan and lease-request identity required')
 if p0_hash==local_hash:raise RuntimeError('confirmatory P0 plan hash must be fresh and must not reuse local-F0 research-execution plan')
 r={'schema_version':SCHEMA_VERSION,'receipt_type':'reopen-p0-experiment-lease-request','contract_id':cid,'contract_sha256':_text(p0_plan.get('contract_sha256')),'p0_adapter_sha256':_text(p0_pre_experiment.get('p0_adapter_sha256')),'p0_plan_sha256':_text(p0_plan.get('p0_plan_sha256')),'p0_authorization_sha256':_text(p0_authorization.get('p0_authorization_sha256')),'p0_plan_hash':p0_hash,'local_f0_plan_hash':local_hash,'local_f0_lease_request_sha256':local_req,'status':STATUS,'fresh_from_local_f0':True,'local_f0_plan_reuse_forbidden':True,'local_f0_lease_request_reuse_forbidden':True,'fresh_p0_experiment_lease_required':True,'run_id_assignment_required':True,'actor_identity_required':True,'governance_stage_recheck_required':True,'experiment_authority_acquired':False,'execution_authorized':False,'gpu_allocated':False,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False};r['p0_lease_request_sha256']=_digest(identity(r))
 if not validate_p0_lease_request(r):raise RuntimeError('generated P0 lease request invalid')
 return r

def validate_p0_lease_request(r:Mapping[str,Any])->bool:
 if r.get('receipt_type')!='reopen-p0-experiment-lease-request' or r.get('status')!=STATUS:return False
 if not all(_text(r.get(k)) for k in ('p0_adapter_sha256','p0_plan_sha256','p0_authorization_sha256','p0_plan_hash','local_f0_plan_hash','local_f0_lease_request_sha256')):return False
 if _text(r.get('p0_plan_hash'))==_text(r.get('local_f0_plan_hash')):return False
 if any(r.get(k) is not True for k in ('fresh_from_local_f0','local_f0_plan_reuse_forbidden','local_f0_lease_request_reuse_forbidden','fresh_p0_experiment_lease_required','run_id_assignment_required','actor_identity_required','governance_stage_recheck_required')):return False
 if r.get('experiment_authority_acquired') is not False or r.get('execution_authorized') is not False or r.get('gpu_allocated') is not False:return False
 if any(r.get(k) is not False for k in ('scientific_authority','experiment_authority','gpu_authority','submission_authority')):return False
 return _text(r.get('p0_lease_request_sha256'))==_digest(identity(r))
def _dir(root:Path)->Path:
 root=Path(root);return root if root.name=='scientific-contract-p0-lease-requests' else root/'scientific-contract-p0-lease-requests'
def publish_p0_lease_request(root:Path,r:Mapping[str,Any])->dict[str,Any]:
 if not validate_p0_lease_request(r):raise RuntimeError('invalid P0 experiment lease request')
 d=_dir(root);d.mkdir(parents=True,exist_ok=True);cid=_text(r.get('contract_id'));path=d/f'{_slug(cid)}.json';lock=d/f'.{_slug(cid)}.lock'
 with lock.open('a+') as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX);row=json.loads(path.read_text()) if path.exists() else {'schema_version':SCHEMA_VERSION,'contract_id':cid,'contract_sha256':_text(r.get('contract_sha256')),'events':[],'authority':dict(ZERO)};sha=_text(r.get('p0_lease_request_sha256'))
  for e in row.get('events') or []:
   p=e.get('receipt') or {} if isinstance(e,Mapping) else {}
   if isinstance(p,Mapping) and _text(p.get('p0_lease_request_sha256'))==sha:return row
  at=str((r.get('pre_experiment_card') or {}).get('compiled_at') or '');ev={'event_type':'reopen-p0-experiment-lease-request','receipt':dict(r),'recorded_at':at,'execution_authorized':False};ev['event_id']=_digest([cid,len(row.get('events') or []),sha,at])[:24];row.setdefault('events',[]).append(ev);row['updated_at']=at;tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path);return row
def public_p0_lease_request(root:Path,contract_id:str)->dict[str,Any]:
 empty={'status':'P0_EXPERIMENT_LEASE_REQUEST_REQUIRED','p0_lease_request_sha256':'','p0_plan_hash':'','fresh_from_local_f0':False,'experiment_authority_acquired':False,'execution_authorized':False,'authority':dict(ZERO)};path=_dir(root)/f'{_slug(contract_id)}.json'
 if not path.exists():return empty
 try:row=json.loads(path.read_text())
 except Exception:return {**empty,'status':'P0_EXPERIMENT_LEASE_REQUEST_LEDGER_INVALID'}
 rs=[e.get('receipt') or {} for e in row.get('events') or [] if isinstance(e,Mapping) and isinstance(e.get('receipt'),Mapping)];r=rs[-1] if rs else {}
 if not r or not validate_p0_lease_request(r):return {**empty,'status':'P0_EXPERIMENT_LEASE_REQUEST_LEDGER_INVALID'}
 return {**empty,'status':STATUS,'p0_lease_request_sha256':_text(r.get('p0_lease_request_sha256')),'p0_plan_hash':_text(r.get('p0_plan_hash')),'fresh_from_local_f0':True,'experiment_authority_acquired':False,'execution_authorized':False}
