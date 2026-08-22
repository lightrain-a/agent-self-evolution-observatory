#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_scientific_contract import validate_reopened_scientific_contract
from research_pipeline.reopened_scientific_method_design import public_reopen_method_summary,validate_reopen_method_design,validate_reopen_method_review
from research_pipeline.reopened_scientific_experiment_blueprint import build_reopen_experiment_blueprint,publish_reopen_blueprint_receipt,validate_reopen_experiment_blueprint,validate_reopen_blueprint_ledger

def load(p:Path)->dict:
 r=json.loads(p.read_text());
 if not isinstance(r,dict): raise RuntimeError(f'expected JSON object: {p}')
 return r

def latest_method(root:Path,cid:str):
 p=root/'scientific-contract-method-design'/f'{cid}.json'; row=load(p); design=review={}
 for e in row.get('events') or []:
  r=e.get('receipt') or {} if isinstance(e,dict) else {}
  if validate_reopen_method_design(r): design=r
  if validate_reopen_method_review(r): review=r
 if not design or not review: raise RuntimeError('method design/review lineage incomplete')
 return design,review

def main():
 ap=argparse.ArgumentParser(description='Freeze a reopened local-F0 experiment blueprint. This does not authorize execution.')
 ap.add_argument('--root',type=Path,required=True); ap.add_argument('--contract-id',required=True); ap.add_argument('--blueprint-spec',type=Path,required=True); ap.add_argument('--validate-only',action='store_true'); a=ap.parse_args()
 c=load(a.root/'scientific-contracts'/f'{a.contract_id}.json')
 if not validate_reopened_scientific_contract(c): raise RuntimeError('invalid reopened scientific contract')
 d,r=latest_method(a.root,a.contract_id); b=build_reopen_experiment_blueprint(contract=c,method_design=d,method_review=r,blueprint_spec=load(a.blueprint_spec))
 if not validate_reopen_experiment_blueprint(b): raise RuntimeError('blueprint validation failed')
 events=0
 if not a.validate_only:
  row=publish_reopen_blueprint_receipt(a.root,b); errs=validate_reopen_blueprint_ledger(row)
  if errs: raise RuntimeError(errs)
  events=len(row.get('events') or [])
 print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_REOPEN_BLUEPRINT_RECORDED','contract_id':a.contract_id,'blueprint_sha256':b['blueprint_sha256'],'blueprint_status':b['status'],'execution_authorized':False,'local_validation_authority':False,'p0_authority':False,'gpu_authority':False,'events':events},indent=2))
if __name__=='__main__': main()
