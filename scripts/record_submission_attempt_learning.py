#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.submission_attempt_post_submission import build_attempt_learning_packet,validate_attempt_learning_packet,validate_attempt_venue_decision
from research_pipeline.submission_attempt_workflow import append_attempt_workflow_receipt,current_attempt_workflow_summary,validate_attempt_workflow_ledger

def load(path:Path):
 p=json.loads(path.read_text(encoding='utf-8')); return p if isinstance(p,dict) else {}
def latest(row,kind):
 for e in reversed(row.get('events') or []):
  if isinstance(e,dict) and e.get('event_type')==kind and isinstance(e.get('receipt'),dict): return e['receipt']
 return {}
def main():
 ap=argparse.ArgumentParser(description='Record scoped post-decision learning for a child attempt. Acceptance/rejection never changes scientific claim truth or authorizes automatic reopen.')
 ap.add_argument('--root',type=Path,required=True);ap.add_argument('--attempt-id',required=True);ap.add_argument('--lessons',type=Path,required=True);a=ap.parse_args()
 row=load(a.root/'paper-submission-attempt-workflows'/f'{a.attempt_id}.json'); err=validate_attempt_workflow_ledger(row)
 if err: raise RuntimeError(err)
 paper=load(a.root/'paper-acceptance'/f"{row['paper_id']}.json"); decision=latest(row,'attempt-venue-decision')
 if not validate_attempt_venue_decision(decision): raise RuntimeError('valid child attempt venue decision not found')
 src=json.loads(a.lessons.read_text(encoding='utf-8')); lessons=src.get('lessons') if isinstance(src,dict) else src
 if not isinstance(lessons,list): raise RuntimeError('lessons JSON must be a list or {lessons:[...]}')
 receipt=build_attempt_learning_packet(paper_ledger=paper,workflow_ledger=row,venue_decision=decision,lessons=lessons)
 if not validate_attempt_learning_packet(receipt): raise RuntimeError('attempt learning receipt validation failed')
 row=append_attempt_workflow_receipt(a.root,receipt); summary=current_attempt_workflow_summary(row)
 print(json.dumps({'status':'PASS_ATTEMPT_POST_DECISION_LEARNING_RECORDED' if receipt['pass'] else 'ATTEMPT_POST_DECISION_LEARNING_BLOCKED','paper_id':row['paper_id'],'attempt_id':row['attempt_id'],'decision':receipt['decision'],'attempt_learning_receipt_sha256':receipt['attempt_learning_receipt_sha256'],'pass':receipt['pass'],'blockers':receipt['blockers'],'summary':receipt['summary'],'workflow_status':summary['status'],'scientific_claim_status_unchanged':True,'automatic_reopen_authorized':False,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
