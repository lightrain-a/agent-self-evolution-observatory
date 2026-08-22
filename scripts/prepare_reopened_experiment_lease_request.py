#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_pre_experiment_adapter import validate_reopened_pre_experiment
from research_pipeline.reopened_local_validation_authorization import validate_local_validation_authorization,validate_local_validation_authority_ledger
from research_pipeline.reopened_experiment_lease_request import build_experiment_lease_request,publish_experiment_lease_request,public_experiment_lease_request

def load(p:Path)->dict:
 r=json.loads(p.read_text());
 if not isinstance(r,dict):raise RuntimeError(f'expected JSON object: {p}')
 return r

def latest_pre(root:Path,cid:str)->dict:
 row=load(root/'scientific-contract-pre-experiment'/f'{cid}.json')
 for e in reversed(row.get('events') or []):
  r=e.get('receipt') or {} if isinstance(e,dict) else {}
  if isinstance(r,dict) and validate_reopened_pre_experiment(r):return r
 raise RuntimeError('valid Pre-Experiment adapter receipt not found')
def latest_auth(root:Path,cid:str)->dict:
 row=load(root/'scientific-contract-local-validation-authority'/f'{cid}.json');errs=validate_local_validation_authority_ledger(row)
 if errs:raise RuntimeError(errs)
 for e in reversed(row.get('events') or []):
  r=e.get('receipt') or {} if isinstance(e,dict) else {}
  if isinstance(r,dict) and validate_local_validation_authorization(r):return r
 raise RuntimeError('valid local-validation authorization not found')
def main():
 ap=argparse.ArgumentParser(description='Prepare a single-writer experiment lease request after Pre-Experiment PASS. This does not acquire the lease, assign a GPU, or execute the run.')
 ap.add_argument('--root',type=Path,required=True);ap.add_argument('--contract-id',required=True);ap.add_argument('--validate-only',action='store_true');a=ap.parse_args()
 r=build_experiment_lease_request(pre_experiment_receipt=latest_pre(a.root,a.contract_id),local_authorization=latest_auth(a.root,a.contract_id));events=0
 if not a.validate_only:events=len((publish_experiment_lease_request(a.root,r).get('events') or []))
 pub=public_experiment_lease_request(a.root,a.contract_id) if not a.validate_only else {}
 print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_EXPERIMENT_LEASE_REQUEST_RECORDED','contract_id':a.contract_id,'lease_request_sha256':r['lease_request_sha256'],'plan_hash':r['plan_hash'],'request_status':r['status'],'experiment_authority_acquired':False,'execution_authorized':False,'external_executor_action_required':True,'run_id_assignment_required':True,'single_writer_lease_required':True,'events':events,'public_status':pub.get('status','')},indent=2))
if __name__=='__main__':main()
