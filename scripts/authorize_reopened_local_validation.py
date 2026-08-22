#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_scientific_experiment_blueprint import validate_reopen_experiment_blueprint,validate_reopen_blueprint_review,validate_reopen_blueprint_ledger
from research_pipeline.reopened_local_validation_authorization import build_local_validation_authorization,publish_local_validation_authorization,public_local_validation_authorization,validate_local_validation_authority_ledger

def load(p:Path)->dict:
 r=json.loads(p.read_text());
 if not isinstance(r,dict): raise RuntimeError(f'expected JSON object: {p}')
 return r

def latest(root:Path,cid:str):
 p=root/'scientific-contract-experiment-blueprints'/f'{cid}.json'; row=load(p); errs=validate_reopen_blueprint_ledger(row)
 if errs: raise RuntimeError(errs)
 b=q={}
 for e in row.get('events') or []:
  r=e.get('receipt') or {} if isinstance(e,dict) else {}
  if validate_reopen_experiment_blueprint(r): b=r
  if validate_reopen_blueprint_review(r): q=r
 if not b or not q: raise RuntimeError('blueprint/review lineage incomplete')
 return b,q

def main():
 ap=argparse.ArgumentParser(description='Record explicit human/PI authority for the bounded reopened local-F0 blueprint. This never authorizes execution; Pre-Experiment Compiler and experiment lease remain required.')
 ap.add_argument('--root',type=Path,required=True); ap.add_argument('--contract-id',required=True); ap.add_argument('--external-authority-ref',required=True); ap.add_argument('--authorized-at',required=True); ap.add_argument('--max-units',type=int,required=True); ap.add_argument('--max-provider-calls',type=int,required=True); ap.add_argument('--max-gpu-hours',type=float,required=True); ap.add_argument('--validate-only',action='store_true'); a=ap.parse_args()
 b,q=latest(a.root,a.contract_id); receipt=build_local_validation_authorization(blueprint=b,blueprint_review=q,external_authority_ref=a.external_authority_ref,authorized_at=a.authorized_at,authorized_budget={'max_units':a.max_units,'max_provider_calls':a.max_provider_calls,'max_gpu_hours':a.max_gpu_hours}); events=0
 if not a.validate_only:
  row=publish_local_validation_authorization(a.root,receipt); errs=validate_local_validation_authority_ledger(row)
  if errs: raise RuntimeError(errs)
  events=len(row.get('events') or [])
 pub=public_local_validation_authorization(a.root,a.contract_id) if not a.validate_only else {}
 print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_LOCAL_VALIDATION_AUTHORIZATION_RECORDED','contract_id':a.contract_id,'authorization_sha256':receipt['local_validation_authorization_sha256'],'authorization_status':receipt['status'],'authorized_budget':receipt['authorized_budget'],'local_validation_authorized':True,'pre_experiment_compiler_required':True,'pre_experiment_compiler_input_eligible':True,'execution_authorized':False,'experiment_authority':False,'p0_authority':False,'gpu_authority':False,'events':events,'public_status':pub.get('status','')},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
