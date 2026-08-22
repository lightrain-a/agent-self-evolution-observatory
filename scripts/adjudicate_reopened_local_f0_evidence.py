#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_local_f0_completion import adjudicate_evidence,publish_receipt,public_completion,validate_completion,validate_completion_ledger
from research_pipeline.reopened_scientific_experiment_blueprint import validate_reopen_blueprint_review,validate_reopen_experiment_blueprint

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
 p=argparse.ArgumentParser(description='Independently adjudicate a completed reopened local-F0 run. This never authorizes P0 automatically and never updates parent claims.')
 p.add_argument('--root',type=Path,required=True);p.add_argument('--contract-id',required=True);p.add_argument('--adjudication-packet',type=Path,required=True);a=p.parse_args();cid=a.contract_id
 completion=latest(a.root/'scientific-contract-run-completions'/f'{cid}.json',validate_completion,validate_completion_ledger)
 row=load(a.root/'scientific-contract-experiment-blueprints'/f'{cid}.json');blueprint=next((e['receipt'] for e in row['events'] if validate_reopen_experiment_blueprint(e.get('receipt') or {})),None);review=next((e['receipt'] for e in row['events'] if validate_reopen_blueprint_review(e.get('receipt') or {})),None)
 if not blueprint or not review:raise RuntimeError('valid blueprint/review not found')
 receipt=adjudicate_evidence(completion=completion,blueprint=blueprint,blueprint_review=review,packet=load(a.adjudication_packet));ledger=publish_receipt(a.root,receipt);errors=validate_completion_ledger(ledger)
 if errors:raise RuntimeError(errors)
 pub=public_completion(a.root,cid)
 print(json.dumps({'status':'PASS_LOCAL_F0_EVIDENCE_ADJUDICATED','contract_id':cid,'evidence_adjudication_sha256':receipt['evidence_adjudication_sha256'],'evidence_status':receipt['status'],'typed_execution_outcome':receipt['typed_execution_outcome'],'p0_authorization_review_eligible':receipt['p0_authorization_review_eligible'],'p0_authorized':False,'claim_update_authorized':False,'method_verdict_authorized':False,'public_status':pub['status']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
