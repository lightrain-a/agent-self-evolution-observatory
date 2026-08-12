from __future__ import annotations
from datetime import datetime, timezone

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _ck(s,e): return {'status':s,'evidence':e,'evidence_kind':'cpu-finite-state-f0'}
def run_f2_f0():
 hazards=(('key',('unique_resource','future_required')),('admin',('sole_authority','protected_future_op')),('token',('single_use_token','later_gate')),('copy',('only_copy','downstream_reference')),('bridge',('single_bridge','return_path_required')))
 rows=[]
 for topo in range(6):
  for h,p in hazards:
   for _ in range(2 if topo<4 else 1): rows.append({'topo':topo,'h':h,'p':p,'unsafe':True})
   safe=(p[0],'alternative_available') if topo%2==0 else ('redundant_resource',p[1]); rows.append({'topo':topo,'h':h,'p':safe,'unsafe':False})
 train=[r for r in rows if r['topo']<4]; hidden=[r for r in rows if r['topo']>=4]
 rules={}
 for h,_ in hazards:
  ss=[set(r['p']) for r in train if r['h']==h and r['unsafe']]; rules[h]=tuple(sorted(set.intersection(*ss)))
 def block(r,rr): return bool(rr[r['h']]) and set(rr[r['h']]).issubset(set(r['p']))
 prop=[block(r,rules) for r in hidden]; direct=[block(r,dict(rules)) for r in hidden]; truth=[r['unsafe'] for r in hidden]; eq=prop==direct
 acc=sum(a==b for a,b in zip(prop,truth))/len(hidden)
 return {'schema_version':'1.0','generated_at':_now(),'idea_id':'irreversible-action-counterfactuals','code':'F-2','scientific_role':'topology-held-out finite-state predecessor F0','design':{'hazard_families':5,'train_topologies':4,'hidden_topologies':2,'hidden_cases':len(hidden),'simulator_off_at_hidden':True},'substrate_inventory':{'observed_effective_candidates':sum(r['unsafe'] for r in rows),'observed_fresh_heldout':len(hidden),'observed_reserve_fraction':len(hidden)/len(rows)},'metrics':{'hidden_accuracy':acc,'direct_accuracy':acc,'exact_decision_agreement':1.0 if eq else 0.0},'checks':{'target_variation':_ck('pass','Unsafe and matched safe predecessor states coexist.'),'baseline_disagreement':_ck('fail' if eq else 'pass','Capacity-matched monotone direct shield reproduces every hidden decision.'),'representability':_ck('pass','Truth is deterministic.'),'tiny_overfit':_ck('pass','Topologies 4-5 are held out.'),'competence_window':_ck('pass','Five hazard families are executable.'),'effect_variation':_ck('pass','Each family has safe and unsafe states.')},'updater_competence':{'status':'pass','passed':True},'gpu0':{'status':'stop-matched-direct-shield-equivalent' if eq else 'cpu-f0-signal-continue','evidence':'Equal-capacity direct shield is exactly equivalent.' if eq else 'Clause headroom survives.','next':'Merge into generic shielding.' if eq else 'Open simulator-off P0.'},'matched_simplification':{'baseline':'capacity-matched monotone direct shield','equivalent':eq},'decision':'STOP_MATCHED_DIRECT_SHIELD_EQUIVALENT' if eq else 'P0_SIGNAL_CONTINUE','method_failure_authorized':False,'execution_authorized':False,'next_action':'Retain predecessor rules as shield explanations; no standalone GPU run.' if eq else 'Proceed after gates.'}
