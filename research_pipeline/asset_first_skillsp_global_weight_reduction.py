from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog


def rows(path: Path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--membership',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    rs=rows(a.membership)
    skills=sorted({s for r in rs for s in r['accepted_skill_ids']})
    covered=[r for r in rs if r['accepted_skill_ids']]
    A=np.array([[1.0 if s in r['accepted_skill_ids'] else 0.0 for s in skills] for r in covered])
    n=len(skills)
    # Variables: nonnegative skill weights w_1..w_n and max exposure t.
    # Normalize the minimum exposure of every covered task to at least 1.
    # Minimize t subject to 1 <= A_i w <= t for every task.
    c=np.zeros(n+1); c[-1]=1.0
    Aub=[]; bub=[]
    for row in A:
        Aub.append(np.r_[-row,0.0]); bub.append(-1.0)
        Aub.append(np.r_[row,-1.0]); bub.append(0.0)
    res=linprog(c,A_ub=np.asarray(Aub),b_ub=np.asarray(bub),bounds=[(0,None)]*n+[(0,None)],method='highs')
    if not res.success: raise RuntimeError(res.message)
    w=res.x[:n]; exposure=A@w; t=float(res.x[-1])
    unique={}
    for j,s in enumerate(skills):
        only=np.where((A[:,j]==1)&(A.sum(axis=1)==1))[0]
        unique[s]=int(len(only))
    witnesses=[]
    for i,r in enumerate(covered):
        acc=r['accepted_skill_ids']
        if len(acc)>1 and exposure[i] >= t-1e-8:
            witnesses.append({'accepted_skill_ids':acc,'tool':r.get('tool'),'exposure':float(exposure[i])})
    out={
      'schema_version':'1.0','analysis_type':'strongest-global-package-reweighting reduction audit',
      'candidate_id':'skill-taxonomy-representation-invariance',
      'baseline':'arbitrary nonnegative global per-package weights with every released covered task constrained to exposure >= 1; minimize maximum task exposure',
      'skills':skills,'covered_rows':len(covered),'optimal_max_to_min_exposure_ratio':t,
      'minimum_exposure':float(exposure.min()),'maximum_exposure':float(exposure.max()),
      'optimal_weights':{s:float(w[j]) for j,s in enumerate(skills)},
      'single_membership_unique_row_counts':unique,
      'max_exposure_witnesses':witnesses[:20],
      'all_task_exposure_equalizable':bool(t <= 1.0+1e-8),
      'reduction_verdict':'GLOBAL_PACKAGE_REWEIGHTING_CANNOT_REMOVE_PARTIAL_OVERLAP_RESIDUAL' if t>1.0+1e-8 else 'GLOBAL_REWEIGHTING_ABSORBS',
      'interpretation':'This baseline is stronger than uniform sampling, text dedup, and fixed scalar retuning: it may set redundant package weights to zero and freely reweight every remaining package. A ratio >1 proves that no context-independent scalar weight per package can equalize exposure over all released supported tasks while keeping each supported task at the same positive exposure floor.',
      'paper_design_authorized':False,'method_authorized':False,'gpu_authorized':False
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'verdict':out['reduction_verdict'],'ratio':t,'min':out['minimum_exposure'],'max':out['maximum_exposure'],'weights':out['optimal_weights']},ensure_ascii=False))
if __name__=='__main__': main()
