#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_scientific_contract import validate_reopened_scientific_contract
from research_pipeline.reopened_scientific_experiment_blueprint import validate_reopen_experiment_blueprint,validate_reopen_blueprint_review,validate_reopen_blueprint_ledger
from research_pipeline.reopened_local_validation_authorization import validate_local_validation_authorization,validate_local_validation_authority_ledger
from research_pipeline.reopened_pre_experiment_adapter import compile_reopened_pre_experiment,publish_reopened_pre_experiment,public_reopened_pre_experiment,validate_reopened_pre_experiment

def load(p:Path)->dict:
 r=json.loads(p.read_text());
 if not isinstance(r,dict): raise RuntimeError(f'expected JSON object: {p}')
 return r

def latest(root:Path,cid:str):
 brow=load(root/'scientific-contract-experiment-blueprints'/f'{cid}.json');
 if (errs:=validate_reopen_blueprint_ledger(brow)): raise RuntimeError(errs)
 b=q={}
 for e in brow.get('events') or []:
  r=e.get('receipt') or {} if isinstance(e,dict) else {}
  if validate_reopen_experiment_blueprint(r): b=r
  if validate_reopen_blueprint_review(r): q=r
 arow=load(root/'scientific-contract-local-validation-authority'/f'{cid}.json')
 if (errs:=validate_local_validation_authority_ledger(arow)): raise RuntimeError(errs)
 a={}
 for e in reversed(arow.get('events') or []):
  r=e.get('receipt') or {} if isinstance(e,dict) else {}
  if validate_local_validation_authorization(r): a=r; break
 if not b or not q or not a: raise RuntimeError('blueprint/review/local-authority lineage incomplete')
 return b,q,a

def main():
 ap=argparse.ArgumentParser(description='Compile a human-authorized reopened local-F0 blueprint through the existing Pre-Experiment 8-gate compiler. This command never acquires an experiment lease or runs the experiment.')
 ap.add_argument('--root',type=Path,required=True); ap.add_argument('--contract-id',required=True); ap.add_argument('--runtime-supplement',type=Path,required=True); ap.add_argument('--data-root',type=Path,required=True); ap.add_argument('--validate-only',action='store_true'); a=ap.parse_args()
 contract=load(a.root/'scientific-contracts'/f'{a.contract_id}.json')
 if not validate_reopened_scientific_contract(contract): raise RuntimeError('invalid reopened scientific contract')
 b,q,auth=latest(a.root,a.contract_id); receipt=compile_reopened_pre_experiment(contract=contract,blueprint=b,blueprint_review=q,local_authorization=auth,runtime_supplement=load(a.runtime_supplement),data_root=a.data_root)
 if not validate_reopened_pre_experiment(receipt): raise RuntimeError('pre-experiment adapter receipt validation failed')
 events=0
 if not a.validate_only:
  row=publish_reopened_pre_experiment(a.root,receipt); events=len(row.get('events') or [])
 pub=public_reopened_pre_experiment(a.root,a.contract_id) if not a.validate_only else {}
 print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_PRE_EXPERIMENT_ADAPTER_RECORDED','contract_id':a.contract_id,'adapter_receipt_sha256':receipt['adapter_receipt_sha256'],'adapter_status':receipt['status'],'passed_gates':receipt['passed_gates'],'gate_count':receipt['gate_count'],'compiler_blocker_count':len(receipt['compiler_blockers']),'compiler_execution_ready':receipt['compiler_execution_ready'],'effective_execution_authorized':False,'experiment_lease_required':True,'automatic_lease_acquisition_forbidden':True,'events':events,'public_status':pub.get('status','')},ensure_ascii=False,indent=2))
 if receipt['status']=='PRE_EXPERIMENT_COMPILER_BLOCKED': raise SystemExit(3)
if __name__=='__main__': main()
