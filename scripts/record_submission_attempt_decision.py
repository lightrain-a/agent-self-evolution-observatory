#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.post_decision_learning import FINAL_DECISIONS
from research_pipeline.submission_attempt_post_submission import build_attempt_rebuttal_skipped_by_venue,build_attempt_venue_decision,validate_attempt_rebuttal_skipped,validate_attempt_venue_decision
from research_pipeline.submission_attempt_workflow import append_attempt_workflow_receipt,current_attempt_workflow_summary,validate_attempt_workflow_ledger

def load(path:Path):
 p=json.loads(path.read_text(encoding='utf-8')); return p if isinstance(p,dict) else {}
def main():
 ap=argparse.ArgumentParser(description='Record the real final venue decision for a child attempt. --pre-rebuttal-terminal records an explicit venue-skip receipt and never fabricates reviews.')
 ap.add_argument('--root',type=Path,required=True);ap.add_argument('--attempt-id',required=True);ap.add_argument('--decision',choices=sorted(FINAL_DECISIONS),required=True);ap.add_argument('--decision-id',required=True);ap.add_argument('--source-ref',required=True);ap.add_argument('--received-at',required=True);ap.add_argument('--decision-text',type=Path,required=True);ap.add_argument('--pre-rebuttal-terminal',action='store_true');a=ap.parse_args()
 row=load(a.root/'paper-submission-attempt-workflows'/f'{a.attempt_id}.json'); err=validate_attempt_workflow_ledger(row)
 if err: raise RuntimeError(err)
 paper=load(a.root/'paper-acceptance'/f"{row['paper_id']}.json")
 receipt=build_attempt_venue_decision(paper_ledger=paper,workflow_ledger=row,decision_id=a.decision_id,source_ref=a.source_ref,received_at=a.received_at,decision=a.decision,decision_text=a.decision_text.read_text(encoding='utf-8'),decision_phase='PRE_REBUTTAL_TERMINAL' if a.pre_rebuttal_terminal else 'POST_REBUTTAL',rebuttal_available=not a.pre_rebuttal_terminal)
 if not validate_attempt_venue_decision(receipt): raise RuntimeError('attempt venue decision validation failed')
 row=append_attempt_workflow_receipt(a.root,receipt); skip={}
 if a.pre_rebuttal_terminal:
  skip=build_attempt_rebuttal_skipped_by_venue(workflow_ledger=row,venue_decision=receipt)
  if not validate_attempt_rebuttal_skipped(skip): raise RuntimeError('attempt venue-skip validation failed')
  row=append_attempt_workflow_receipt(a.root,skip)
 summary=current_attempt_workflow_summary(row)
 print(json.dumps({'status':'PASS_ATTEMPT_VENUE_DECISION_RECORDED','paper_id':row['paper_id'],'attempt_id':row['attempt_id'],'decision':receipt['decision'],'decision_phase':receipt['decision_phase'],'rebuttal_available':receipt['rebuttal_available'],'attempt_venue_decision_sha256':receipt['attempt_venue_decision_sha256'],'attempt_rebuttal_skip_sha256':str(skip.get('attempt_rebuttal_skip_sha256') or ''),'workflow_status':summary['status'],'scientific_claim_status_unchanged':True,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
