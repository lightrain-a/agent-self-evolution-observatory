#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.submission_attempt_post_submission import build_attempt_rebuttal_preparation,validate_attempt_rebuttal_preparation
from research_pipeline.submission_attempt_workflow import append_attempt_workflow_receipt,current_attempt_workflow_summary,validate_attempt_workflow_ledger

def load(path:Path):
 p=json.loads(path.read_text(encoding='utf-8')); return p if isinstance(p,dict) else {}
def latest(row,kind):
 for e in reversed(row.get('events') or []):
  if isinstance(e,dict) and e.get('event_type')==kind and isinstance(e.get('receipt'),dict): return e['receipt']
 return {}
def main():
 ap=argparse.ArgumentParser(description='Prepare and validate a rebuttal for a submitted child attempt. Reviewer requests never authorize experiments or claim expansion.')
 ap.add_argument('--root',type=Path,required=True);ap.add_argument('--attempt-id',required=True);ap.add_argument('--objections',type=Path,required=True);ap.add_argument('--resolutions',type=Path,required=True);ap.add_argument('--response-text',type=Path,required=True);ap.add_argument('--response-limit-words',type=int,required=True);a=ap.parse_args()
 row=load(a.root/'paper-submission-attempt-workflows'/f'{a.attempt_id}.json'); err=validate_attempt_workflow_ledger(row)
 if err: raise RuntimeError(err)
 paper=load(a.root/'paper-acceptance'/f"{row['paper_id']}.json"); review=latest(row,'attempt-review-set')
 obs=json.loads(a.objections.read_text(encoding='utf-8')); obs=obs.get('objections') if isinstance(obs,dict) else obs
 res=json.loads(a.resolutions.read_text(encoding='utf-8')); res=res.get('resolutions') if isinstance(res,dict) else res
 if not isinstance(obs,list) or not isinstance(res,list): raise RuntimeError('objections/resolutions must be JSON lists or keyed list objects')
 receipt=build_attempt_rebuttal_preparation(paper_ledger=paper,workflow_ledger=row,review_set=review,objections=obs,resolutions=res,response_text=a.response_text.read_text(encoding='utf-8'),response_limit_words=a.response_limit_words)
 if not validate_attempt_rebuttal_preparation(receipt): raise RuntimeError('attempt rebuttal receipt validation failed')
 row=append_attempt_workflow_receipt(a.root,receipt); summary=current_attempt_workflow_summary(row)
 print(json.dumps({'status':'PASS_ATTEMPT_REBUTTAL_RECORDED' if receipt['pass'] else 'ATTEMPT_REBUTTAL_BLOCKED','paper_id':row['paper_id'],'attempt_id':row['attempt_id'],'attempt_rebuttal_receipt_sha256':receipt['attempt_rebuttal_receipt_sha256'],'pass':receipt['pass'],'blockers':receipt['blockers'],'summary':receipt['summary'],'workflow_status':summary['status'],'claim_expansion_authorized':False,'new_experiment_authorized':False,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
