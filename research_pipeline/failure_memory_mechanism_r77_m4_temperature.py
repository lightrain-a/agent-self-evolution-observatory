#!/usr/bin/env python3
from __future__ import annotations
import json, math, hashlib
from pathlib import Path
from typing import Any
ROOT=Path('/data/wyt/b1-memrl-r77-mechanism')
SRC=ROOT/'R77_M2B_EXACT_SAME_STATE_LOGIT_PROBE.json'
TEMPS=[0.05,0.1,0.2,0.5,1.0]
def digest(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def valid(v):
 r=v.get('receipt_sha256');return isinstance(r,str) and r==digest({k:x for k,x in v.items() if k!='receipt_sha256'})
def sig(x):
 if x>=0:
  z=math.exp(-x);return 1/(1+z)
 z=math.exp(x);return z/(1+z)
def main():
 x=json.loads(SRC.read_text())
 if not valid(x) or x.get('status')!='R77_M2B_EXACT_SAME_STATE_LOGIT_PROBE_COMPLETE':raise RuntimeError('M2B-invalid')
 rows=[]
 for r in x['rows']:
  entry={'task_id':r['task_id'],'anchor':r['anchor'],'A_prompt_logodds_B_minus_A':r['conditions']['A']['branchpoint_logodds_B_minus_A'],'B_prompt_logodds_B_minus_A':r['conditions']['B']['branchpoint_logodds_B_minus_A'],'prompt_swap_flips_candidate_preference':r['prompt_swap_flips_A_vs_B_candidate_token_preference'],'temperatures':[]}
  la=entry['A_prompt_logodds_B_minus_A'];lb=entry['B_prompt_logodds_B_minus_A']
  for t in TEMPS:
   pa=sig(la/t);pb=sig(lb/t)
   entry['temperatures'].append({'temperature':t,'pairwise_P_B_branch_given_A_or_B_candidate_under_A_prompt':pa,'pairwise_P_B_branch_given_A_or_B_candidate_under_B_prompt':pb,'provenance_probability_shift_BminusA_prompt':pb-pa})
  rows.append(entry)
 summary=[]
 for tid in sorted({r['task_id'] for r in rows},key=int):
  rr=[r for r in rows if r['task_id']==tid]
  signs=[(a['A_prompt_logodds_B_minus_A']>0,a['B_prompt_logodds_B_minus_A']>0) for a in rr]
  if all(a!=b for a,b in signs): typ='DIRECT_PROMPT_BOUNDARY_FLIP_ALL_ANCHORS'
  elif len(set(signs))>1 and all(a==b for a,b in signs): typ='HISTORY_ANCHOR_DOMINANT_SIGN_WITHIN_ANCHOR'
  elif any(a!=b for a,b in signs): typ='MIXED_PROMPT_AND_HISTORY_SENSITIVITY'
  else: typ='NO_SIGN_FLIP_AT_CANDIDATE_BOUNDARY'
  summary.append({'task_id':tid,'mechanism_temperature_type':typ,'anchors':len(rr),'max_abs_prompt_logodds_shift':max(abs(a['B_prompt_logodds_B_minus_A']-a['A_prompt_logodds_B_minus_A']) for a in rr),'temperature_0p2_probability_shifts':[next(z['provenance_probability_shift_BminusA_prompt'] for z in a['temperatures'] if z['temperature']==0.2) for a in rr]})
 out={'schema_version':'1.0','paper_id':x['paper_id'],'receipt_id':'D2-FAILURE-MEMORY-PROVENANCE-R77-M4-ANALYTIC-TEMPERATURE-SENSITIVITY','status':'R77_M4_ANALYTIC_TEMPERATURE_SENSITIVITY_COMPLETE_ZERO_MODEL','role':'POST_HOC_BRANCHPOINT_TEMPERATURE_DIAGNOSTIC_NOT_PRIMARY_INFERENCE','bindings':{'M2B_receipt_sha256':x['receipt_sha256']},'definition':'For each frozen branchpoint, treat only the two faithfully replayed A/B candidate next tokens as the choice set. Given raw log-odds d=z_B-z_A, pairwise P(B|{A,B},temperature T)=sigmoid(d/T). This is analytic branchpoint sensitivity, not full-vocabulary or full-response sampling.','temperatures':TEMPS,'rows':rows,'task_summary':summary,'new_model_calls':0,'new_environment_trajectories':0,'changes_R72_R73_primary_inference':False}
 out['receipt_sha256']=digest(out);(ROOT/'R77_M4_TEMPERATURE_SENSITIVITY_ANALYTIC.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'receipt_sha256':out['receipt_sha256'],'task_summary':summary},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
