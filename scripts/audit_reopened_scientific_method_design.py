#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_scientific_method_design import build_reopen_method_review, publish_reopen_method_receipt, public_reopen_method_summary, validate_reopen_method_design, validate_reopen_method_ledger

def load(path:Path)->dict:
    row=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(row,dict): raise RuntimeError(f'expected JSON object: {path}')
    return row

def latest_design(root:Path,contract_id:str)->dict:
    path=root/'scientific-contract-method-design'/f'{contract_id}.json'
    if not path.exists(): raise RuntimeError('method design ledger not found')
    row=load(path); errors=validate_reopen_method_ledger(row)
    if errors: raise RuntimeError(errors)
    for event in reversed(row.get('events') or []):
        receipt=event.get('receipt') or {} if isinstance(event,dict) else {}
        if isinstance(receipt,dict) and validate_reopen_method_design(receipt): return receipt
    raise RuntimeError('valid frozen method design not found')

def main():
    ap=argparse.ArgumentParser(description='Record independent review of a reopened scientific method design. PASS grants blueprint-design eligibility only, never execution authority.')
    ap.add_argument('--root',type=Path,required=True); ap.add_argument('--contract-id',required=True); ap.add_argument('--review-packet',type=Path,required=True); ap.add_argument('--validate-only',action='store_true'); a=ap.parse_args()
    design=latest_design(a.root,a.contract_id); receipt=build_reopen_method_review(method_design=design,review_packet=load(a.review_packet))
    events=0
    if not a.validate_only:
        row=publish_reopen_method_receipt(a.root,receipt); errors=validate_reopen_method_ledger(row)
        if errors: raise RuntimeError(errors)
        events=len(row.get('events') or [])
    summary=public_reopen_method_summary(a.root,a.contract_id) if not a.validate_only else {}
    print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_REOPEN_METHOD_REVIEW_RECORDED','contract_id':receipt['contract_id'],'method_review_sha256':receipt['method_review_sha256'],'review_status':receipt['status'],'failed_checks':receipt['failed_checks'],'experiment_blueprint_design_eligible':receipt['experiment_blueprint_design_eligible'],'local_validation_eligible':False,'experiment_authority':False,'p0_authority':False,'gpu_authority':False,'events':events,'public_status':summary.get('status','')},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
