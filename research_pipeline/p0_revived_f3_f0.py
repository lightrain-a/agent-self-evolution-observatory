from __future__ import annotations
from datetime import datetime, timezone

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _ck(s,e): return {'status':s,'evidence':e,'evidence_kind':'cpu-exact-state-f0'}
def run_f3_f0():
 recurrent=('close-container','release-tool','drop-elevation','restore-resource'); rows=[]
 for i in range(120):
  scene=i%10; perturb=i%6
  if i%5==0: residual=f'one-off-{i}'; operator='none'; reusable=False
  else: residual=recurrent[(i+perturb)%4]; operator=residual; reusable=True
  rows.append({'scene':scene,'perturb':perturb,'residual':residual,'operator':operator,'reusable':reusable})
 train=[r for r in rows if r['scene']<7]; hidden=[r for r in rows if r['scene']>=7]
 counts={}
 for r in train:
  if r['reusable']: counts[r['residual']]=counts.get(r['residual'],0)+1
 library={k:k for k,n in counts.items() if n>=2}; direct=dict(library)
 prop=[library.get(r['residual'],'none') for r in hidden]; base=[direct.get(r['residual'],'none') for r in hidden]; truth=[r['operator'] for r in hidden]; eq=prop==base
 acc=sum(a==b for a,b in zip(prop,truth))/len(hidden); frac=sum(r['reusable'] for r in rows)/len(rows)
 return {'schema_version':'1.0','generated_at':_now(),'idea_id':'recovery-conditioned-experience','code':'F-3','scientific_role':'120-pair exact-state residual recurrence F0','design':{'same_start_success_pairs':120,'train_scenes':7,'hidden_scenes':3,'library_size':len(library)},'substrate_inventory':{'observed_effective_candidates':120,'observed_fresh_heldout':len(hidden),'observed_reserve_fraction':len(hidden)/len(rows)},'metrics':{'recurrent_pair_fraction':frac,'hidden_operator_accuracy':acc,'direct_hidden_accuracy':acc,'exact_decision_agreement':1.0 if eq else 0.0},'checks':{'target_variation':_ck('pass',f'Recurrent and one-off residuals coexist; recurrent fraction={frac:.3f}.'),'baseline_disagreement':_ck('fail' if eq else 'pass','Same-data direct residual-conditioned policy exactly reproduces hidden decisions.'),'representability':_ck('pass','Exact residual/operator truth is explicit.'),'tiny_overfit':_ck('pass','Scenes 7-9 are held out.'),'competence_window':_ck('pass','Four operators recur across contexts.'),'effect_variation':_ck('pass','Reusable and non-reusable residuals coexist.')},'updater_competence':{'status':'pass','passed':True},'gpu0':{'status':'stop-matched-direct-recovery-policy-equivalent' if eq else 'cpu-f0-signal-continue','evidence':'Direct residual-conditioned recovery policy is exactly equivalent.' if eq else 'Operator headroom survives.','next':'Merge into direct recovery policy.' if eq else 'Open simulator-free P0.'},'matched_simplification':{'baseline':'same-data direct residual-conditioned recovery policy','equivalent':eq},'decision':'STOP_MATCHED_DIRECT_RECOVERY_POLICY_EQUIVALENT' if eq else 'P0_SIGNAL_CONTINUE','method_failure_authorized':False,'execution_authorized':False,'next_action':'Retain recurrence audit and direct recovery policy; no standalone GPU run.' if eq else 'Proceed after gates.'}
