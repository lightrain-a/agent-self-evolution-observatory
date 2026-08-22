#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_p0_authorization import validate_p0_authorization,validate_p0_authority_ledger
from research_pipeline.reopened_p0_plan import validate_p0_plan
from research_pipeline.reopened_p0_pre_experiment_adapter import compile_p0_pre_experiment,publish_p0_pre_experiment,public_p0_pre_experiment

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
 p=argparse.ArgumentParser(description='Compile a fresh confirmatory P0 plan through the native Pre-Experiment Compiler. This never reuses local-F0 cards/leases and never authorizes execution by itself.')
 p.add_argument('--root',type=Path,required=True);p.add_argument('--contract-id',required=True);p.add_argument('--runtime-supplement',type=Path,required=True);a=p.parse_args();cid=a.contract_id
 ar=load(a.root/'scientific-contract-p0-authority'/f'{cid}.json');errs=validate_p0_authority_ledger(ar)
 if errs:raise RuntimeError(errs)
 auth=latest(ar,validate_p0_authorization);pr=load(a.root/'scientific-contract-p0-plans'/f'{cid}.json');plan=latest(pr,validate_p0_plan)
 if not auth or not plan:raise RuntimeError('valid P0 authority/plan lineage incomplete')
 runtime=load(a.runtime_supplement);r=compile_p0_pre_experiment(p0_plan=plan,p0_authorization=auth,runtime_supplement=runtime,data_root=a.root);events=len((publish_p0_pre_experiment(a.root,r).get('events') or []));pub=public_p0_pre_experiment(a.root,cid)
 print(json.dumps({'status':'PASS_P0_PRE_EXPERIMENT_ADAPTER_RECORDED','contract_id':cid,'p0_adapter_sha256':r['p0_adapter_sha256'],'adapter_status':r['status'],'passed_gates':r['passed_gates'],'gate_count':r['gate_count'],'compiler_blocker_count':len(r['compiler_blockers']),'compiler_execution_ready':r['compiler_execution_ready'],'effective_execution_authorized':False,'fresh_experiment_lease_required':True,'fresh_run_lineage_required':True,'events':events,'public_status':pub['status']},ensure_ascii=False,indent=2))
 if r['status'].endswith('BLOCKED'):raise SystemExit(3)
if __name__=='__main__':main()
