#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_scientific_contract import validate_reopened_scientific_contract
from research_pipeline.reopened_scientific_problem_gate import (
    build_reopen_problem_gate_receipt,
    public_reopen_problem_gate_summary,
    publish_reopen_problem_gate_receipt,
    validate_reopen_problem_gate_ledger,
    validate_reopen_problem_gate_receipt,
)


def load_json(path: Path) -> dict:
    row=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(row,dict):
        raise RuntimeError(f'expected JSON object: {path}')
    return row


def main() -> None:
    parser=argparse.ArgumentParser(description='Audit a reopened child scientific contract at the dedicated Problem Gate. PASS grants process eligibility only; no method, experiment, P0, GPU, claim, or submission authority is granted.')
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--contract-id',required=True)
    parser.add_argument('--packet',type=Path,required=True)
    args=parser.parse_args()

    contract_path=args.root/'scientific-contracts'/f'{args.contract_id}.json'
    contract=load_json(contract_path)
    if not validate_reopened_scientific_contract(contract):
        raise RuntimeError('reopened scientific contract invalid')
    packet=load_json(args.packet)
    receipt=build_reopen_problem_gate_receipt(contract=contract,packet=packet)
    if not validate_reopen_problem_gate_receipt(receipt):
        raise RuntimeError('reopen Problem Gate receipt failed validation')
    row=publish_reopen_problem_gate_receipt(args.root,receipt)
    errors=validate_reopen_problem_gate_ledger(row)
    if errors:
        raise RuntimeError(errors)
    public=public_reopen_problem_gate_summary(receipt)
    print(json.dumps({
        'status':'PASS_REOPEN_PROBLEM_GATE_RECORDED' if public['pass'] else 'BLOCKED_REOPEN_PROBLEM_GATE_RECORDED',
        'contract_id':args.contract_id,
        'contract_sha256':contract['contract_sha256'],
        'problem_gate_status':public['status'],
        'problem_gate_receipt_sha256':public['problem_gate_receipt_sha256'],
        'failed_checks':public['failed_checks'],
        'paper_design_eligible':public['paper_design_eligible'],
        'method_design_review_eligible':public['method_design_review_eligible'],
        'parent_claim_status_unchanged':True,
        'scientific_authority':False,
        'paper_design_authority':False,
        'method_design_authority':False,
        'experiment_authority':False,
        'p0_authority':False,
        'gpu_authority':False,
        'submission_authority':False,
    },ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
