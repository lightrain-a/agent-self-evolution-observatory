#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_scientific_experiment_blueprint import build_reopen_blueprint_review,publish_reopen_blueprint_receipt,public_reopen_blueprint_summary,validate_reopen_experiment_blueprint,validate_reopen_blueprint_ledger

def load(p:Path)->dict:
 r=json.loads(p.read_text());
 if not isinstance(r,dict): raise RuntimeError(f'expected JSON object: {p}')
 return r

def latest_blueprint(root:Path,cid:str)->dict:
 p=root/'scientific-contract-experiment-blueprints'/f'{cid}.json'; row=load(p); errs=validate_reopen_blueprint_ledger(row)
 if errs: raise RuntimeError(errs)
 for e in reversed(row.get('events') or []):
  r=e.get('receipt') or {} if isinstance(e,dict) else {}
  if isinstance(r,dict) and validate_reopen_experiment_blueprint(r): return r
 raise RuntimeError('valid frozen experiment blueprint not found')

def main():
 ap=argparse.ArgumentParser(description='Record independent review of a reopened experiment blueprint. PASS only makes local-validation authorization review eligible; it never authorizes execution.')
 ap.add_argument('--root',type=Path,required=True); ap.add_argument('--contract-id',required=True); ap.add_argument('--review-packet',type=Path,required=True); ap.add_argument('--validate-only',action='store_true'); a=ap.parse_args()
 b=latest_blueprint(a.root,a.contract_id); q=build_reopen_blueprint_review(blueprint=b,review_packet=load(a.review_packet)); events=0
 if not a.validate_only:
  row=publish_reopen_blueprint_receipt(a.root,q); errs=validate_reopen_blueprint_ledger(row)
  if errs: raise RuntimeError(errs)
  events=len(row.get('events') or [])
 pub=public_reopen_blueprint_summary(a.root,a.contract_id) if not a.validate_only else {}
 print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_REOPEN_BLUEPRINT_REVIEW_RECORDED','contract_id':a.contract_id,'blueprint_review_sha256':q['blueprint_review_sha256'],'review_status':q['status'],'failed_checks':q['failed_checks'],'local_validation_authorization_review_eligible':q['local_validation_authorization_review_eligible'],'pre_experiment_compiler_input_eligible':q['pre_experiment_compiler_input_eligible'],'execution_authorized':False,'p0_authority':False,'gpu_authority':False,'events':events,'public_status':pub.get('status','')},indent=2))
if __name__=='__main__': main()
