#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_local_f0_completion import complete_run,publish_receipt,public_completion,validate_completion_ledger
from research_pipeline.reopened_local_f0_run import validate_reopened_local_f0_run_start,validate_run_start_ledger
from research_pipeline.reopened_local_validation_authorization import validate_local_validation_authorization

def load(path):
 row=json.loads(Path(path).read_text());
 if not isinstance(row,dict):raise RuntimeError(f'expected JSON object: {path}')
 return row
def latest(path,validator,ledger_validator=None):
 row=load(path)
 if ledger_validator:
  errors=ledger_validator(row)
  if errors:raise RuntimeError(errors)
 for event in reversed(row.get('events') or []):
  r=event.get('receipt') or {} if isinstance(event,dict) else {}
  if isinstance(r,dict) and validator(r):return r
 raise RuntimeError(f'valid receipt not found: {path}')
def main():
 p=argparse.ArgumentParser(description='Close a reopened local-F0 run, release resource + experiment authority, and record typed execution completion without scientific interpretation.')
 p.add_argument('--root',type=Path,required=True);p.add_argument('--contract-id',required=True);p.add_argument('--typed-outcome',required=True);p.add_argument('--completed-units',type=int,required=True);p.add_argument('--provider-calls',type=int,required=True);p.add_argument('--gpu-hours-used',type=float,required=True);p.add_argument('--artifact-manifest',type=Path,required=True);p.add_argument('--completed-at',default='');a=p.parse_args();cid=a.contract_id
 run=latest(a.root/'scientific-contract-run-starts'/f'{cid}.json',validate_reopened_local_f0_run_start,validate_run_start_ledger); auth=latest(a.root/'scientific-contract-local-validation-authority'/f'{cid}.json',validate_local_validation_authorization); manifest=load(a.artifact_manifest).get('artifacts') or []
 r=complete_run(root=a.root,run_start=run,local_authorization=auth,typed_execution_outcome=a.typed_outcome,completed_units=a.completed_units,provider_calls=a.provider_calls,gpu_hours_used=a.gpu_hours_used,artifact_manifest=manifest,completed_at=a.completed_at); ledger=publish_receipt(a.root,r);errs=validate_completion_ledger(ledger)
 if errs:raise RuntimeError(errs)
 pub=public_completion(a.root,cid)
 print(json.dumps({'status':'PASS_LOCAL_F0_EXECUTION_COMPLETED_RESOURCES_RELEASED','contract_id':cid,'completion_sha256':r['completion_sha256'],'completion_status':r['status'],'typed_execution_outcome':r['typed_execution_outcome'],'artifact_count':len(r['artifact_manifest']),'budget_compliant':r['budget_compliant'],'resource_lease_released':True,'experiment_authority_released':True,'scientific_interpretation_authorized':False,'p0_authorized':False,'public_status':pub['status']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
