#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, re
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

EXPECTED_B10_SHA='e779c19a6a73bdb4b551f0739453a014fe9fc3cafc17cb4fbaa8b70a5137d8e6'
CONDS=['success_memory','failure_memory','no_memory']
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding='utf-8'))
def toks(s:str)->set[str]:return set(re.findall(r"[A-Za-z0-9_'-]+",s.lower()))
def jac(a:str,b:str)->float:
 x,y=toks(a),toks(b);u=x|y;return 0.0 if not u else 1-len(x&y)/len(u)
def mean(v:list[float])->float:return sum(v)/len(v) if v else 0.0
def tv(a:list[str],b:list[str])->float:
 ca,cb=Counter(a),Counter(b);keys=set(ca)|set(cb);return .5*sum(abs(ca[k]/len(a)-cb[k]/len(b)) for k in keys)
def family(sig:str)->str:return sig.split(':',1)[0]
def next_goal(text:str)->str:
 m=re.search(r'"next_goal"\s*:\s*"((?:\\.|[^"\\])*)"',text,re.DOTALL)
 if not m:return ''
 try:return json.loads('"'+m.group(1)+'"')
 except Exception:return m.group(1)
def pair_within(v:list[str])->float:return mean([jac(a,b) for a,b in combinations(v,2)])
def pair_between(a:list[str],b:list[str])->float:return mean([jac(x,y) for x in a for y in b])
def corr(xs:list[float],ys:list[float])->float|None:
 if len(xs)<2:return None
 mx,my=mean(xs),mean(ys);vx=sum((x-mx)**2 for x in xs);vy=sum((y-my)**2 for y in ys)
 if vx<=0 or vy<=0:return None
 return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(vx*vy)

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--b10-result',required=True,type=Path);ap.add_argument('--private-root',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
 if sha(a.b10_result)!=EXPECTED_B10_SHA:raise RuntimeError('B10 result SHA drift')
 b10=load(a.b10_result)
 if b10['status']!='B10_EXECUTION_COMPLETE' or b10['summary']['provider_calls_complete']!=432:raise RuntimeError('B10 incomplete')
 by=defaultdict(lambda:defaultdict(list));raw_by=defaultdict(lambda:defaultdict(list))
 stages=list((a.private_root/'stages').glob('*.json'))
 if len(stages)!=432:raise RuntimeError(f'expected 432 stages, found {len(stages)}')
 for p in stages:
  r=load(p)
  if r.get('status')!='complete':raise RuntimeError('noncomplete stage')
  tid=int(r['future_task']);cond=r['condition'];by[tid][cond].append(str(r['action_signature']))
  raw=a.private_root/'raw'/r['raw_sha256'][:2]/f"{r['raw_sha256']}.txt"
  if not raw.is_file():raise RuntimeError('missing raw')
  raw_by[tid][cond].append(next_goal(raw.read_text(encoding='utf-8')))
 cells=[]
 for c in b10['cell_results']:
  tid=int(c['future_task']);g=by[tid];goals=raw_by[tid]
  if any(len(g[x])!=4 or len(goals[x])!=4 for x in CONDS):raise RuntimeError(f'geometry drift:{tid}')
  sf_fam=tv([family(x) for x in g['success_memory']],[family(x) for x in g['failure_memory']]);sn_fam=tv([family(x) for x in g['success_memory']],[family(x) for x in g['no_memory']]);fn_fam=tv([family(x) for x in g['failure_memory']],[family(x) for x in g['no_memory']])
  sgo,fgo,ngo=goals['success_memory'],goals['failure_memory'],goals['no_memory'];valid=all(x.strip() for x in sgo+fgo+ngo)
  if valid:
   within_sf=.5*(pair_within(sgo)+pair_within(fgo));between_sf=pair_between(sgo,fgo);excess=between_sf-within_sf
   mem_none=.5*(pair_between(sgo,ngo)+pair_between(fgo,ngo));within_all=(pair_within(sgo)+pair_within(fgo)+pair_within(ngo))/3
  else:within_sf=between_sf=excess=mem_none=within_all=None
  cells.append({'future_task':tid,'selected_source_task':c['selected_source_task'],'intent_template_id':c['intent_template_id'],'fine_success_failure_tv':c['success_failure_tv'],'coarse_action_family_success_failure_tv':sf_fam,'coarse_action_family_presence_tv':.5*(sn_fam+fn_fam),'next_goal_all_nonempty':valid,'next_goal_between_success_failure_jaccard_distance':between_sf,'next_goal_within_success_failure_jaccard_distance':within_sf,'next_goal_success_failure_excess_over_within':excess,'next_goal_memory_vs_no_memory_distance':mem_none,'next_goal_mean_within_all_conditions':within_all})
 valid=[x for x in cells if x['next_goal_all_nonempty']]
 ex=[x['next_goal_success_failure_excess_over_within'] for x in valid];fine=[x['fine_success_failure_tv'] for x in cells];coarse=[x['coarse_action_family_success_failure_tv'] for x in cells]
 payload={'schema_version':'1.0','artifact_type':'b10-posthoc-zero-call-process-diagnostic','paper_id':b10['paper_id'],'status':'B10_PROCESS_DIAGNOSTIC_COMPLETE','source_b10_result_sha256':EXPECTED_B10_SHA,'provider_calls':0,'new_rollouts':0,'inferential_authority':False,'summary':{'states':36,'fine_action_mean_success_failure_tv':round(mean(fine),6),'coarse_action_family_mean_success_failure_tv':round(mean(coarse),6),'coarse_action_family_mean_presence_tv':round(mean([x['coarse_action_family_presence_tv'] for x in cells]),6),'states_with_nonzero_coarse_success_failure_tv':sum(x>0 for x in coarse),'next_goal_complete_states':len(valid),'mean_next_goal_between_success_failure_distance':round(mean([x['next_goal_between_success_failure_jaccard_distance'] for x in valid]),6),'mean_next_goal_within_success_failure_distance':round(mean([x['next_goal_within_success_failure_jaccard_distance'] for x in valid]),6),'mean_next_goal_success_failure_excess_over_within':round(mean(ex),6),'states_positive_next_goal_excess':sum(x>0 for x in ex),'states_negative_next_goal_excess':sum(x<0 for x in ex),'mean_next_goal_memory_vs_no_memory_distance':round(mean([x['next_goal_memory_vs_no_memory_distance'] for x in valid]),6),'mean_next_goal_within_all_conditions':round(mean([x['next_goal_mean_within_all_conditions'] for x in valid]),6),'pearson_fine_action_tv_vs_next_goal_excess':corr([x['fine_success_failure_tv'] for x in valid],ex)},'interpretation':'Post-hoc localization only: coarse action-family and next-goal lexical diagnostics reuse the frozen B10 outputs and cannot rescue or replace the preregistered B10 first-action TV gate.','cells':cells,'scientific_authority':False,'experiment_authority':False,'claim_expansion_authority':False}
 a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps({'status':payload['status'],'summary':payload['summary']},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
