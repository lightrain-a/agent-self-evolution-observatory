#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_p0_pre_experiment_adapter import validate_p0_pre_experiment
from research_pipeline.reopened_p0_plan import validate_p0_plan
from research_pipeline.reopened_p0_authorization import validate_p0_authorization,validate_p0_authority_ledger
from research_pipeline.reopened_local_f0_run import validate_reopened_local_f0_run_start,validate_run_start_ledger
from research_pipeline.reopened_p0_experiment_lease_request import build_p0_lease_request,publish_p0_lease_request,public_p0_lease_request

def load(p:Path):
 r=json.loads(p.read_text());
 if not isinstance(r,dict):raise RuntimeError(f'expected JSON object: {p}')
 return r
def latest(row,validator):
 for e in reversed(row.get('events') or []):
  r=e.get('receipt') or {} if isinstance(e,dict) else {}
  if isinstance(r,dict) and validator(r):return r
 return None
def main():
 p=argparse.ArgumentParser(description='Prepare a fresh confirmatory-P0 experiment lease request after P0 Pre-Experiment PASS. This never acquires authority, allocates GPU, or reuses the local-F0 plan/lease.')
 p.add_argument('--root',type=Path,required=True);p.add_argument('--contract-id',required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args();cid=a.contract_id
 pre=latest(load(a.root/'scientific-contract-p0-pre-experiment'/f'{cid}.json'),validate_p0_pre_experiment);plan=latest(load(a.root/'scientific-contract-p0-plans'/f'{cid}.json'),validate_p0_plan);ar=load(a.root/'scientific-contract-p0-authority'/f'{cid}.json');errs=validate_p0_authority_ledger(ar)
 if errs:raise RuntimeError(errs)
 auth=latest(ar,validate_p0_authorization);rr=load(a.root/'scientific-contract-run-starts'/f'{cid}.json');errs=validate_run_start_ledger(rr)
 if errs:raise RuntimeError(errs)
 local=latest(rr,validate_reopened_local_f0_run_start)
 if not pre or not plan or not auth or not local:raise RuntimeError('fresh P0 lease-request lineage incomplete')
 r=build_p0_lease_request(p0_pre_experiment=pre,p0_plan=plan,p0_authorization=auth,local_f0_run_start=local);events=0
 if not a.validate_only:events=len((publish_p0_lease_request(a.root,r).get('events') or []))
 pub=public_p0_lease_request(a.root,cid) if not a.validate_only else {}
 print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_P0_EXPERIMENT_LEASE_REQUEST_RECORDED','contract_id':cid,'p0_lease_request_sha256':r['p0_lease_request_sha256'],'p0_plan_hash':r['p0_plan_hash'],'request_status':r['status'],'fresh_from_local_f0':True,'experiment_authority_acquired':False,'execution_authorized':False,'gpu_allocated':False,'events':events,'public_status':pub.get('status','')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
