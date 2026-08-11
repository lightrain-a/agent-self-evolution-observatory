from __future__ import annotations
from typing import Any

MATCH_DIMENSIONS=("candidate_pool","labels_or_truth","model_calls","environment_calls","tokens","hidden_access","tuning_split")

def compile_matched_simplifications(idea_id:str,mechanism:str,declared_baseline:str)->dict[str,Any]:
 text=(mechanism+' '+declared_baseline).lower(); rows=[]
 def add(key,title,why):
  if key not in {r['key'] for r in rows}: rows.append({'key':key,'title':title,'why':why})
 add('declared-strongest','Declared strongest baseline','Preserve the author-declared closest baseline under identical evidence and budget.')
 add('same-representation-shallow','Same-representation shallow rule','Test whether the same features/labels are already sufficient with CART, sparse linear, lookup, or monotone rules.')
 if any(k in text for k in ('memory','retrieval','experience')):
  add('memory-policy-simple','Simple memory policy','Compare family/mean/nearest-neighbor plus recency/frequency or no-memory/placebo controls at matched audit cost.')
 if any(k in text for k in ('causal','counterfactual','intervention')):
  add('noncausal-same-input','Non-causal same-input control','Use the identical representation and observations without intervention-specific machinery.')
 if any(k in text for k in ('active','search','rollback','minimal','localiz')):
  add('standard-algorithm','Standard algorithmic baseline','Compare ddmin/group testing/greedy/beam/checkpoint algorithms at equal query or candidate-check budget.')
 if any(k in text for k in ('symbolic','constraint','rule','logic','typed','grammar')):
  add('complexity-matched-rule','Complexity-matched rule learner','Compare ILP/DNF/n-ary factor/direct typed lookup at matched rule capacity.')
 if any(k in text for k in ('workflow','edit','rewrite')):
  add('direct-edit-reuse','Direct edit-effect reuse','Compare nearest/direct paired edit-effect lookup with zero hidden search and matched source calls.')
 if any(k in text for k in ('controller','predict','regression','classifier','gate')):
  add('mean-or-threshold','Mean / threshold control','Compare calibrated means, fixed thresholds, family shrinkage, and nearest-neighbor decisions.')
 return {'schema_version':'1.0','idea_id':idea_id,'minimum_required_baselines':3,'compiled_baselines':rows,'baseline_count':len(rows),'matched_dimensions':list(MATCH_DIMENSIONS),'hidden_outcome_retuning_forbidden':True,'posthoc_baseline_deletion_forbidden':True}
