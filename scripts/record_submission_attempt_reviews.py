#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.submission_attempt_post_submission import build_attempt_review_set,validate_attempt_review_set
from research_pipeline.submission_attempt_workflow import append_attempt_workflow_receipt,current_attempt_workflow_summary,validate_attempt_workflow_ledger

def load(path:Path):
 p=json.loads(path.read_text(encoding='utf-8')); return p if isinstance(p,dict) else {}
def workflow(root:Path,attempt_id:str):
 p=load(root/'paper-submission-attempt-workflows'/f'{attempt_id}.json'); e=validate_attempt_workflow_ledger(p)
 if e: raise RuntimeError(e)
 return p
def main():
 ap=argparse.ArgumentParser(description='Record real venue reviews for one already-submitted child attempt. Raw review text remains private in the attempt workflow ledger.')
 ap.add_argument('--root',type=Path,required=True);ap.add_argument('--attempt-id',required=True);ap.add_argument('--reviews',type=Path,required=True);a=ap.parse_args()
 row=workflow(a.root,a.attempt_id); src=json.loads(a.reviews.read_text(encoding='utf-8')); reviews=src.get('reviews') if isinstance(src,dict) else src
 if not isinstance(reviews,list): raise RuntimeError('reviews JSON must be a list or {reviews:[...]}')
 receipt=build_attempt_review_set(row,reviews)
 if not validate_attempt_review_set(receipt): raise RuntimeError('attempt review set validation failed')
 row=append_attempt_workflow_receipt(a.root,receipt); summary=current_attempt_workflow_summary(row)
 print(json.dumps({'status':'PASS_ATTEMPT_REVIEWS_RECORDED','paper_id':row['paper_id'],'attempt_id':row['attempt_id'],'attempt_review_set_sha256':receipt['attempt_review_set_sha256'],'review_count':receipt['review_count'],'workflow_status':summary['status'],'raw_review_text_public':False,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
