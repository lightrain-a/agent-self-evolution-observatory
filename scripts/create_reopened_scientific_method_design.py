#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.reopened_scientific_contract import validate_reopened_scientific_contract
from research_pipeline.reopened_scientific_problem_gate import load_latest_reopen_problem_gate
from research_pipeline.reopened_scientific_method_design import build_reopen_method_design, publish_reopen_method_receipt, validate_reopen_method_design, validate_reopen_method_ledger

def load(path:Path)->dict:
    row=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(row,dict): raise RuntimeError(f'expected JSON object: {path}')
    return row

def main():
    ap=argparse.ArgumentParser(description='Freeze a method design for a reopened scientific contract after Problem Gate PASS. This never authorizes execution.')
    ap.add_argument('--root',type=Path,required=True); ap.add_argument('--contract-id',required=True); ap.add_argument('--method-spec',type=Path,required=True); ap.add_argument('--validate-only',action='store_true'); a=ap.parse_args()
    contract_path=a.root/'scientific-contracts'/f'{a.contract_id}.json'
    if not contract_path.exists(): raise RuntimeError('reopened scientific contract not found')
    contract=load(contract_path)
    if not validate_reopened_scientific_contract(contract): raise RuntimeError('reopened scientific contract is invalid')
    gate=load_latest_reopen_problem_gate(a.root,a.contract_id)
    if not gate or gate.get('_invalid'): raise RuntimeError('valid reopen Problem Gate receipt not found')
    receipt=build_reopen_method_design(contract=contract,problem_gate_receipt=gate,method_spec=load(a.method_spec))
    if not validate_reopen_method_design(receipt): raise RuntimeError('method design failed validation')
    events=0
    if not a.validate_only:
        row=publish_reopen_method_receipt(a.root,receipt); errors=validate_reopen_method_ledger(row)
        if errors: raise RuntimeError(errors)
        events=len(row.get('events') or [])
    print(json.dumps({'status':'PASS_VALIDATE_ONLY' if a.validate_only else 'PASS_REOPEN_METHOD_DESIGN_RECORDED','contract_id':receipt['contract_id'],'method_design_sha256':receipt['method_design_sha256'],'method_name':receipt['method_spec']['method_name'],'method_status':receipt['status'],'events':events,'experiment_blueprint_design_eligible':False,'experiment_authority':False,'p0_authority':False,'gpu_authority':False},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
