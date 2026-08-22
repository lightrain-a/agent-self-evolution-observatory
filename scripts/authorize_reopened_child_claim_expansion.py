#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from research_pipeline.reopened_child_claim_audit import validate_child_claim_audit,validate_child_claim_audit_ledger
from research_pipeline.reopened_child_claim_expansion_authorization import build_child_claim_expansion_authorization,publish_child_claim_expansion_authorization,public_child_claim_expansion_authorization,validate_claim_expansion_authority_ledger


def load(path:Path)->dict:
 row=json.loads(path.read_text(encoding='utf-8'))
 if not isinstance(row,dict): raise RuntimeError(f'expected JSON object: {path}')
 return row

def latest_audit(root:Path,attempt_sha:str)->dict:
 row=load(root/'paper-scientific-claim-audits'/f'{attempt_sha}.json');errs=validate_child_claim_audit_ledger(row)
 if errs: raise RuntimeError(errs)
 for event in reversed(row.get('events') or []):
  receipt=event.get('receipt') or {} if isinstance(event,dict) else {}
  if isinstance(receipt,dict) and validate_child_claim_audit(receipt): return receipt
 raise RuntimeError('valid child Claim Audit not found')
def main():
 p=argparse.ArgumentParser(description='Record explicit human authority for selected Claim-Audit-held NEW_CHILD_CLAIM ids. Authority applies only to listed claims and does not update parent claims or unlock preparation by itself.')
 p.add_argument('--root',type=Path,required=True);p.add_argument('--attempt-sha256',required=True);p.add_argument('--approve-claim-id',action='append',required=True);p.add_argument('--external-authority-ref',required=True);p.add_argument('--authorized-at',required=True);p.add_argument('--scope',required=True);a=p.parse_args()
 audit=latest_audit(a.root,a.attempt_sha256);receipt=build_child_claim_expansion_authorization(claim_audit=audit,approved_new_claim_ids=a.approve_claim_id,external_authority_ref=a.external_authority_ref,authorized_at=a.authorized_at,scope=a.scope);ledger=publish_child_claim_expansion_authorization(a.root,receipt);errs=validate_claim_expansion_authority_ledger(ledger)
 if errs: raise RuntimeError(errs)
 public=public_child_claim_expansion_authorization(a.root,a.attempt_sha256)
 print(json.dumps({'status':'PASS_CHILD_NEW_CLAIM_EXPANSION_AUTHORIZATION_RECORDED','paper_id':receipt['paper_id'],'attempt_sha256':receipt['attempt_sha256'],'authorization_sha256':receipt['child_claim_expansion_authorization_sha256'],'approved_new_claim_ids':receipt['approved_new_claim_ids'],'approved_new_claims':len(receipt['approved_new_claim_ids']),'future_claim_expansion_authorized':False,'parent_claim_update_authorized':False,'paper_preparation_authorized':False,'public_status':public['status']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
