from __future__ import annotations

import hashlib,json,os,re
from pathlib import Path
from typing import Any,Mapping

from .reopened_p0_authorization import STATUS as P0_AUTH_STATUS,validate_p0_authorization
from .reopened_local_f0_completion import SIGNAL,validate_adjudication

SCHEMA_VERSION='1.0'
STATUS='P0_CONFIRMATORY_PLAN_FROZEN_PRE_EXPERIMENT_REQUIRED'
ZERO_AUTHORITY={'scientific':False,'experiment':False,'gpu':False,'submission':False}
REQ=('plan_id','confirmatory_prediction','unit_definition','qualification_rule','truth_source','primary_metric','analysis_plan','evaluation_split','exclusion_rules','stop_rules')

def _text(v:Any)->str:return str(v or '').strip()
def _digest(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def _slug(v:str)->str:return re.sub(r'[^A-Za-z0-9_.-]+','-',v).strip('-')[:180] or 'unknown'
def identity(r:Mapping[str,Any])->dict[str,Any]:
 return {k:r.get(k) for k in ('contract_id','contract_sha256','p0_authorization_sha256','evidence_adjudication_sha256','plan_spec_sha256','status')}

def build_p0_plan(*,p0_authorization:Mapping[str,Any],adjudication:Mapping[str,Any],spec:Mapping[str,Any])->dict[str,Any]:
 if not validate_p0_authorization(p0_authorization) or p0_authorization.get('status')!=P0_AUTH_STATUS:raise RuntimeError('valid P0 lifecycle authorization required')
 if not validate_adjudication(adjudication) or adjudication.get('status')!=SIGNAL:raise RuntimeError('valid local-F0 screening signal adjudication required')
 if _text(p0_authorization.get('evidence_adjudication_sha256'))!=_text(adjudication.get('evidence_adjudication_sha256')):raise RuntimeError('P0 plan evidence lineage mismatch')
 s=dict(spec or {})
 for k in REQ:
  if not s.get(k):raise RuntimeError(f'P0 plan field required: {k}')
 if not isinstance(s.get('arms'),list) or len(s['arms'])<2:raise RuntimeError('P0 plan requires at least two arms')
 if not isinstance(s.get('same_information_baselines'),list) or len(s['same_information_baselines'])<2:raise RuntimeError('P0 plan requires at least two same-information baselines')
 if not isinstance(s.get('seeds'),list) or len(s['seeds'])<2:raise RuntimeError('P0 confirmatory plan requires at least two frozen seeds/replicates')
 alpha=float(s.get('alpha') or 0); units=int(s.get('requested_units') or 0); calls=int(s.get('expected_provider_calls') or 0); gpu=float(s.get('estimated_gpu_hours') or 0)
 if not (0<alpha<=0.1) or units<=0 or calls<=0 or gpu<0:raise RuntimeError('P0 plan alpha/budget fields invalid')
 cap=p0_authorization.get('p0_budget') or {}
 if units>int(cap.get('max_units') or 0) or calls>int(cap.get('max_provider_calls') or 0) or gpu>float(cap.get('max_gpu_hours') or 0)+1e-12:raise RuntimeError('P0 plan exceeds authorized P0 budget')
 if _text(s.get('evaluation_split')).lower() in {'local-f0','screening','same-as-local-f0'}:raise RuntimeError('P0 confirmatory evaluation split must be fresh and held out from local F0')
 if s.get('frozen_before_p0_outcomes') is not True or s.get('local_f0_data_excluded_from_confirmatory_statistic') is not True or s.get('outcome_driven_selection_forbidden') is not True:raise RuntimeError('P0 confirmatory preregistration safeguards required')
 r={'schema_version':SCHEMA_VERSION,'receipt_type':'reopen-p0-confirmatory-plan','contract_id':_text(adjudication.get('contract_id')),'contract_sha256':_text(adjudication.get('contract_sha256')),'p0_authorization_sha256':_text(p0_authorization.get('p0_authorization_sha256')),'evidence_adjudication_sha256':_text(adjudication.get('evidence_adjudication_sha256')),'plan_spec':s,'plan_spec_sha256':_digest(s),'status':STATUS,'confirmatory_plan_frozen':True,'fresh_pre_experiment_compiler_required':True,'fresh_experiment_lease_required':True,'fresh_run_lineage_required':True,'local_f0_data_excluded_from_confirmatory_statistic':True,'execution_authorized':False,'p0_result_authorized':False,'claim_update_authorized':False,'method_verdict_authorized':False,'full_experiment_authorized':False,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False}
 r['p0_plan_sha256']=_digest(identity(r))
 if not validate_p0_plan(r):raise RuntimeError('generated P0 plan invalid')
 return r

def validate_p0_plan(r:Mapping[str,Any])->bool:
 if r.get('receipt_type')!='reopen-p0-confirmatory-plan' or r.get('status')!=STATUS:return False
 if r.get('confirmatory_plan_frozen') is not True or r.get('fresh_pre_experiment_compiler_required') is not True or r.get('fresh_experiment_lease_required') is not True or r.get('fresh_run_lineage_required') is not True:return False
 if r.get('local_f0_data_excluded_from_confirmatory_statistic') is not True:return False
 if any(r.get(k) is not False for k in ('execution_authorized','p0_result_authorized','claim_update_authorized','method_verdict_authorized','full_experiment_authorized','scientific_authority','experiment_authority','gpu_authority','submission_authority')):return False
 if _digest(r.get('plan_spec') or {})!=_text(r.get('plan_spec_sha256')):return False
 return _text(r.get('p0_plan_sha256'))==_digest(identity(r))

def _dir(root:Path)->Path:
 root=Path(root);return root if root.name=='scientific-contract-p0-plans' else root/'scientific-contract-p0-plans'
def publish_p0_plan(root:Path,r:Mapping[str,Any])->dict[str,Any]:
 if not validate_p0_plan(r):raise RuntimeError('invalid P0 confirmatory plan')
 d=_dir(root);d.mkdir(parents=True,exist_ok=True);cid=_text(r.get('contract_id'));path=d/f'{_slug(cid)}.json'
 row=json.loads(path.read_text()) if path.exists() else {'schema_version':SCHEMA_VERSION,'contract_id':cid,'contract_sha256':_text(r.get('contract_sha256')),'events':[],'authority':dict(ZERO_AUTHORITY)}
 sha=_text(r.get('p0_plan_sha256'))
 for e in row.get('events') or []:
  p=e.get('receipt') or {} if isinstance(e,Mapping) else {}
  if isinstance(p,Mapping) and _text(p.get('p0_plan_sha256'))==sha:return row
 ev={'event_type':'reopen-p0-confirmatory-plan','receipt':dict(r),'recorded_at':_text((r.get('plan_spec') or {}).get('frozen_at')),'scientific_authority':False,'experiment_authority':False,'gpu_authority':False};ev['event_id']=_digest([cid,len(row.get('events') or []),sha,ev['recorded_at']])[:24];row.setdefault('events',[]).append(ev);row['updated_at']=ev['recorded_at'];tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,path);return row

def public_p0_plan(root:Path,contract_id:str)->dict[str,Any]:
 empty={'status':'P0_CONFIRMATORY_PLAN_REQUIRED','p0_plan_sha256':'','plan_id':'','requested_units':0,'execution_authorized':False,'authority':dict(ZERO_AUTHORITY)};path=_dir(root)/f'{_slug(contract_id)}.json'
 if not path.exists():return empty
 try:row=json.loads(path.read_text())
 except Exception:return {**empty,'status':'P0_PLAN_LEDGER_INVALID'}
 rs=[e.get('receipt') or {} for e in row.get('events') or [] if isinstance(e,Mapping) and isinstance(e.get('receipt'),Mapping)];r=rs[-1] if rs else {}
 if not r or not validate_p0_plan(r):return {**empty,'status':'P0_PLAN_LEDGER_INVALID'}
 s=r.get('plan_spec') or {};return {**empty,'status':STATUS,'p0_plan_sha256':_text(r.get('p0_plan_sha256')),'plan_id':_text(s.get('plan_id')),'requested_units':int(s.get('requested_units') or 0),'alpha':float(s.get('alpha') or 0),'evaluation_split':_text(s.get('evaluation_split')),'execution_authorized':False}
