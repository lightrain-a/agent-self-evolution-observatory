from __future__ import annotations
import csv,json,random,itertools
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT
DATA_ROOT=Path('/data/wyt/agent-self-evolution-observatory/runs/p0-mem-xfer-support-enriched-qwen-v1')
A1_JSON=PROJECT_ROOT/'generated/p0-a1-soft-audit-f0.json'; A1_JS=PROJECT_ROOT/'generated/p0-a1-soft-audit-f0.js'
A2_JSON=PROJECT_ROOT/'generated/p0-a2-evidence-depth-f0.json'; A2_JS=PROJECT_ROOT/'generated/p0-a2-evidence-depth-f0.js'
HORIZONS=(1,2,3,5,8)
def _now(): return datetime.now(timezone.utc).isoformat()
def _load():
 with (DATA_ROOT/'first-divergence-audit-v1/state-table.csv').open(encoding='utf-8') as fh: rows=list(csv.DictReader(fh))
 traces=defaultdict(dict)
 with (DATA_ROOT/'full-support-table/raw-traces.jsonl').open(encoding='utf-8') as fh:
  for line in fh:
   r=json.loads(line)
   if r.get('arm') in {'retrieved','placebo'}: traces[r['unit_id']][r['arm']]=r
 if len(rows)!=72 or any(set(traces[r['unit_id']])!={'retrieved','placebo'} for r in rows): raise RuntimeError('frozen paired table incomplete')
 return rows,traces
def _full(r,t): return sum(int(t[r['unit_id']][a]['steps']) for a in ('retrieved','placebo'))
def _screen(r,h,t): return sum(min(h,int(t[r['unit_id']][a]['steps'])) for a in ('retrieved','placebo'))
def _fixed(rows,t,h):
 pos=[r for r in rows if int(r['controlled_delta'])!=0]; harms=[r for r in rows if int(r['controlled_delta'])<0]; flagged=[]; cost=0
 for r in rows:
  if int(r['first_divergence_index'])<h: flagged.append(r); cost+=_full(r,t)
  else: cost+=_screen(r,h,t)
 total=sum(_full(r,t) for r in rows); found=sum(int(r['controlled_delta'])!=0 for r in flagged); hf=sum(int(r['controlled_delta'])<0 for r in flagged)
 return {'h':h,'flagged_units':len(flagged),'found_nonzero':found,'nonzero_recall':found/len(pos),'harm_recall':hf/len(harms) if harms else None,'precision':found/len(flagged) if flagged else 0.0,'action_step_cost':cost,'full_action_step_cost':total,'cost_fraction':cost/total}
def _rates(dev,key):
 n=Counter(r[key] for r in dev); p=Counter(r[key] for r in dev if int(r['controlled_delta'])!=0); return {k:p[k]/n[k] for k in n}
def _audit(rows,t,order,budget):
 used=0; chosen=[]
 for r in order:
  c=_full(r,t)
  if used+c<=budget: used+=c; chosen.append(r)
 pos=sum(int(r['controlled_delta'])!=0 for r in rows); harms=sum(int(r['controlled_delta'])<0 for r in rows); found=sum(int(r['controlled_delta'])!=0 for r in chosen); hf=sum(int(r['controlled_delta'])<0 for r in chosen)
 return {'audited_units':len(chosen),'action_step_cost':used,'found_nonzero':found,'nonzero_recall':found/pos,'harm_recall':hf/harms if harms else None}
def _random(rows,t,budget,repeats=20000):
 rng=random.Random(42); vals=[]; ns=[]
 for _ in range(repeats):
  order=list(rows); rng.shuffle(order); z=_audit(rows,t,order,budget); vals.append(z['nonzero_recall']); ns.append(z['audited_units'])
 vals.sort(); return {'seed':42,'repeats':repeats,'mean_nonzero_recall':sum(vals)/len(vals),'p025_nonzero_recall':vals[int(.025*len(vals))],'p975_nonzero_recall':vals[int(.975*len(vals))-1],'mean_audited_units':sum(ns)/len(ns)}
def _signature_rank_rescue(future,t,budget):
 pred_path=DATA_ROOT/'first-divergence-audit-v1/future-predictions.csv'
 with pred_path.open(encoding='utf-8') as fh: preds=list(csv.DictReader(fh))
 by_id={r['unit_id']:r for r in future}; base=0
 def acquire(r):
  row=by_id[r['unit_id']]; h=int(row['first_divergence_index'])+1
  return _screen(row,h,t)
 base=sum(acquire(r) for r in preds); out={}
 for score in ('state_signature','target_state_signature'):
  used=base; chosen=[]
  for p in sorted(preds,key=lambda x:(-float(x[score]),x['unit_id'])):
   row=by_id[p['unit_id']]; extra=_full(row,t)-acquire(p)
   if used+extra<=budget: used+=extra; chosen.append(p)
  out[score]={'signature_acquisition_steps':base,'action_step_cost':used,'audited_units':len(chosen),'found_nonzero':sum(int(x['nonzero']) for x in chosen),'nonzero_recall':sum(int(x['nonzero']) for x in chosen)/sum(int(x['nonzero']) for x in preds)}
 return out

def _a1(rows,t):
 dev=[r for r in rows if r['evaluation_role']=='probe_development']; future=[r for r in rows if r['evaluation_role']=='future_eval']
 curve=[_fixed(dev,t,h) for h in HORIZONS]; eligible=[z for z in curve if z['cost_fraction']<=.35]
 chosen=min(eligible,key=lambda z:(-z['nonzero_recall'],z['cost_fraction'],z['h'])); test=_fixed(future,t,chosen['h']); budget=test['action_step_cost']
 tr=_rates(dev,'target_family'); sr=_rates(dev,'source_family')
 target=_audit(future,t,sorted(future,key=lambda r:(-tr.get(r['target_family'],0),r['target_family'],r['unit_id'])),budget)
 source=_audit(future,t,sorted(future,key=lambda r:(-sr.get(r['source_family'],0),r['source_family'],r['unit_id'])),budget)
 trig=[]; tc=0
 for r in future:
  yes=int(r['first_divergence_index'])<1 and r['retrieved_action_family']=='navigate' and r['placebo_action_family']=='navigate'
  if yes: trig.append(r); tc+=_full(r,t)
  else: tc+=_screen(r,1,t)
 pos=sum(int(r['controlled_delta'])!=0 for r in future); harms=sum(int(r['controlled_delta'])<0 for r in future)
 trigger={'rule':'h=1 AND navigate>navigate','audited_units':len(trig),'action_step_cost':tc,'cost_fraction':tc/sum(_full(r,t) for r in future),'nonzero_recall':sum(int(r['controlled_delta'])!=0 for r in trig)/pos,'harm_recall':sum(int(r['controlled_delta'])<0 for r in trig)/harms if harms else None}
 dominated=(target['nonzero_recall']>=test['nonzero_recall'] and target['action_step_cost']<=test['action_step_cost']) or (trigger['nonzero_recall']>=test['nonzero_recall'] and trigger['action_step_cost']<=test['action_step_cost'])
 return {'schema_version':'1.0','generated_at':_now(),'idea_id':'update-trust-region','code':'A-1','repair':'soft audit allocation from early branch divergence','scientific_role':'retrospective repair F0 only; no method PASS/FAIL authority for the original governance claim','split':{'development':len(dev),'future_eval':len(future),'development_nonzero':sum(int(r['controlled_delta'])!=0 for r in dev),'future_nonzero':pos,'future_harm':harms},'selection_rule':'choose h maximizing development nonzero recall subject to <=35% paired-action cost; tie lower cost then h','development_curve':curve,'selected_h':chosen['h'],'future_branch_policy':test,'matched_baselines':{'target_family_prior':target,'source_family_prior':source,'random_full_audit':_random(future,t,budget),'simple_h1_navigate_trigger':trigger},'context_signature_rescue':_signature_rank_rescue(future,t,budget),'decision':'STOP_REPAIR_SOFT_AUDIT_SIMPLE_TRIAGE_DOMINATES' if dominated else 'REPAIR_F0_SIGNAL_NEEDS_FRESH_VALIDATION','standalone_method_authorized':False,'hard_gate_authorized':False,'formal_p0_authorized':False,'harm_claim_authorized':harms>=3,'interpretation':'Early branch divergence remains an operational audit-priority signal, but a simpler target-family prior has higher held-out impact recall at lower cost and an h=1 navigate trigger matches recall at lower cost. Only one future harmful unit exists, so harm prioritization is not identifiable.','next_action':'Merge branch soft-audit into research-system scheduling; stop standalone A-1 repair and do not spend GPU unless a materially new observable/substrate is proposed.'}
def _family_policy(rows,t,policy,feature='target_family'):
 pos=[r for r in rows if int(r['controlled_delta'])!=0]; flagged=[]; cost=0
 for r in rows:
  key=('same' if r['source_family']==r['target_family'] else 'cross') if feature=='source_target_relation' else r[feature]
  h=policy[key]
  if int(r['first_divergence_index'])<h: flagged.append(r); cost+=_full(r,t)
  else: cost+=_screen(r,h,t)
 total=sum(_full(r,t) for r in rows); found=sum(int(r['controlled_delta'])!=0 for r in flagged)
 return {'policy':policy,'flagged_units':len(flagged),'found_nonzero':found,'nonzero_recall':found/len(pos),'action_step_cost':cost,'cost_fraction':cost/total}
def _adaptive_feature(dev,future,t,feature):
 keys=sorted({('same' if r['source_family']==r['target_family'] else 'cross') if feature=='source_target_relation' else r[feature] for r in dev}); cand=[]
 for hs in itertools.product(HORIZONS,repeat=len(keys)):
  z=_family_policy(dev,t,dict(zip(keys,hs)),feature)
  if z['nonzero_recall']>=.8: cand.append(z)
 selected=min(cand,key=lambda z:(z['cost_fraction'],-z['nonzero_recall'],sum(z['policy'].values())))
 return {'feature':feature,'development':selected,'future':_family_policy(future,t,selected['policy'],feature)}

def _a2(rows,t):
 dev=[r for r in rows if r['evaluation_role']=='probe_development']; future=[r for r in rows if r['evaluation_role']=='future_eval']
 sweep=[_adaptive_feature(dev,future,t,f) for f in ('target_family','source_family','source_target_relation')]; selected=sweep[0]['development']; test=sweep[0]['future']
 fixed=[_fixed(dev,t,h) for h in HORIZONS]; sf=min([z for z in fixed if z['nonzero_recall']>=.8],key=lambda z:(z['cost_fraction'],z['h'])); test_sf=_fixed(future,t,sf['h']); h1=_fixed(future,t,1)
 dominated=all(h1['nonzero_recall']>=x['future']['nonzero_recall'] and h1['cost_fraction']<=x['future']['cost_fraction'] for x in sweep)
 return {'schema_version':'1.0','generated_at':_now(),'idea_id':'budgeted-evolution-controller','code':'A-2','repair':'adaptive evidence-acquisition depth after no early divergence','scientific_role':'retrospective repair F0 only; does not validate the original update-round controller','selection_rule':'development-only per-target-family horizons from {1,2,3,5,8}, minimum cost subject to >=80% nonzero recall','development_adaptive':selected,'future_adaptive':test,'categorical_adaptive_sweep':sweep,'development_best_fixed_at_same_recall':sf,'future_best_fixed_at_dev_target':test_sf,'future_fixed_h1':h1,'decision':'STOP_REPAIR_FIXED_HORIZON_DOMINATES' if dominated else 'REPAIR_F0_SIGNAL_NEEDS_FRESH_VALIDATION','standalone_controller_authorized':False,'formal_p0_authorized':False,'interpretation':'The development-selected family-adaptive depth policy does not transfer: on future_eval it reaches the same nonzero recall as fixed h=1 while spending more paired-action cost. A learned evidence-depth controller is not justified on this substrate.','next_action':'Merge evidence-depth scheduling into A-1/system soft audit; stop standalone A-2 repair and do not launch controller GPU training.'}
def build():
 rows,t=_load(); return _a1(rows,t),_a2(rows,t)
def write():
 a1,a2=build()
 for obj,jp,jsp,var in [(a1,A1_JSON,A1_JS,'P0_A1_SOFT_AUDIT_F0'),(a2,A2_JSON,A2_JS,'P0_A2_EVIDENCE_DEPTH_F0')]:
  jp.parent.mkdir(parents=True,exist_ok=True); jp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); jsp.write_text(f'window.{var} = '+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
 return a1,a2
if __name__=='__main__':
 a1,a2=write(); print(json.dumps({'a1':a1,'a2':a2},ensure_ascii=False,indent=2))
