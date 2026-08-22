#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_p0_authorization import validate_p0_authorization,validate_p0_authority_ledger
from research_pipeline.reopened_local_f0_completion import validate_adjudication,validate_completion_ledger,SIGNAL
from research_pipeline.reopened_p0_plan import build_p0_plan,publish_p0_plan,public_p0_plan

def load(p:Path):
 r=json.loads(p.read_text());
 if not isinstance(r,dict):raise RuntimeError(f'expected JSON object: {p}')
 return r
def latest(row,validator,extra=None):
 for e in reversed(row.get('events') or []):
  r=e.get('receipt') or {} if isinstance(e,dict) else {}
  if isinstance(r,dict) and validator(r) and (extra is None or extra(r)):return r
 return None
def main():
 p=argparse.ArgumentParser(description='Freeze a fresh confirmatory P0 plan after explicit P0 lifecycle authorization. This never authorizes execution and cannot reuse local-F0 data in the confirmatory statistic.')
 p.add_argument('--root',type=Path,required=True);p.add_argument('--contract-id',required=True);p.add_argument('--plan-spec',type=Path,required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args();cid=a.contract_id
 ar=load(a.root/'scientific-contract-p0-authority'/f'{cid}.json');errs=validate_p0_authority_ledger(ar)
 if errs:raise RuntimeError(errs)
 auth=latest(ar,validate_p0_authorization)
 cr=load(a.root/'scientific-contract-run-completions'/f'{cid}.json');errs=validate_completion_ledger(cr)
 if errs:raise RuntimeError(errs)
 adj=latest(cr,validate_adjudication,lambda r:r.get('status')==SIGNAL)
 if not auth or not adj:raise RuntimeError('P0 authorization / valid signal adjudication lineage incomplete')
 spec=load(a.plan_spec);r=build_p0_plan(p0_authorization=auth,adjudication=adj,spec=spec);events=0
 if not a.validate_only:events=len((publish_p0_plan(a.root,r).get('events') or []))
 pub=public_p0_plan(a.root,cid) if not a.validate_only else {}
 print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_P0_CONFIRMATORY_PLAN_FROZEN','contract_id':cid,'p0_plan_sha256':r['p0_plan_sha256'],'plan_id':spec['plan_id'],'requested_units':spec['requested_units'],'alpha':spec['alpha'],'evaluation_split':spec['evaluation_split'],'fresh_pre_experiment_compiler_required':True,'fresh_experiment_lease_required':True,'execution_authorized':False,'p0_result_authorized':False,'events':events,'public_status':pub.get('status','')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
