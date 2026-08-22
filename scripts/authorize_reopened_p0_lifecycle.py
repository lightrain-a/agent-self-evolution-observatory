#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_local_f0_completion import validate_adjudication,validate_completion_ledger,SIGNAL
from research_pipeline.reopened_scientific_experiment_blueprint import validate_reopen_experiment_blueprint,validate_reopen_blueprint_review,validate_reopen_blueprint_ledger
from research_pipeline.reopened_p0_authorization import build_p0_authorization,publish_p0_authorization,public_p0_authorization,validate_p0_authority_ledger

def load(p:Path):
 r=json.loads(p.read_text());
 if not isinstance(r,dict):raise RuntimeError(f'expected JSON object: {p}')
 return r
def main():
 p=argparse.ArgumentParser(description='Record explicit human/PI authorization for confirmatory P0 lifecycle after a valid reopened local-F0 screening signal. This does not authorize P0 execution, GPU, or claim updates.')
 p.add_argument('--root',type=Path,required=True);p.add_argument('--contract-id',required=True);p.add_argument('--external-authority-ref',required=True);p.add_argument('--authorized-at',required=True);p.add_argument('--max-units',type=int,required=True);p.add_argument('--max-provider-calls',type=int,required=True);p.add_argument('--max-gpu-hours',type=float,required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args();cid=a.contract_id
 crow=load(a.root/'scientific-contract-run-completions'/f'{cid}.json');errs=validate_completion_ledger(crow)
 if errs:raise RuntimeError(errs)
 adj=next((e.get('receipt') for e in reversed(crow.get('events') or []) if isinstance(e,dict) and isinstance(e.get('receipt'),dict) and validate_adjudication(e['receipt']) and e['receipt'].get('status')==SIGNAL),None)
 if not adj:raise RuntimeError('valid local-F0 screening signal adjudication not found')
 brow=load(a.root/'scientific-contract-experiment-blueprints'/f'{cid}.json');errs=validate_reopen_blueprint_ledger(brow)
 if errs:raise RuntimeError(errs)
 b=next((e.get('receipt') for e in brow.get('events') or [] if isinstance(e,dict) and validate_reopen_experiment_blueprint(e.get('receipt') or {})),None);br=next((e.get('receipt') for e in brow.get('events') or [] if isinstance(e,dict) and validate_reopen_blueprint_review(e.get('receipt') or {})),None)
 if not b or not br:raise RuntimeError('valid blueprint/review not found')
 r=build_p0_authorization(adjudication=adj,blueprint=b,blueprint_review=br,external_authority_ref=a.external_authority_ref,authorized_at=a.authorized_at,p0_budget={'max_units':a.max_units,'max_provider_calls':a.max_provider_calls,'max_gpu_hours':a.max_gpu_hours});events=0
 if not a.validate_only:
  row=publish_p0_authorization(a.root,r);errs=validate_p0_authority_ledger(row)
  if errs:raise RuntimeError(errs)
  events=len(row.get('events') or [])
 pub=public_p0_authorization(a.root,cid) if not a.validate_only else {}
 print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_P0_LIFECYCLE_AUTHORIZATION_RECORDED','contract_id':cid,'p0_authorization_sha256':r['p0_authorization_sha256'],'p0_status':r['status'],'p0_budget':r['p0_budget'],'p0_lifecycle_authorized':True,'p0_execution_authorized':False,'fresh_pre_experiment_compiler_required':True,'fresh_experiment_lease_required':True,'local_f0_lease_reuse_forbidden':True,'local_f0_run_reuse_forbidden':True,'claim_update_authorized':False,'gpu_authority':False,'events':events,'public_status':pub.get('status','')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
