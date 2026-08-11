from __future__ import annotations
import argparse,csv,hashlib,json,random
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor
AID='mem-xfer-applicability-falsifier-v1'
CONTRACT='dd985ce145471a4fa6aa27f9a2c2b19d06736fc000fc0e977f38b6210a56a308'
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p): return json.loads(Path(p).read_text())
def mean(x): return sum(x)/len(x) if x else 0.0
def sign(x): return 1 if x>1e-12 else (-1 if x<-1e-12 else 0)
def sig(task):
 p=Path(task).parts[-3].split('-')
 if len(p)<4: raise RuntimeError('bad task signature')
 return p[0],p[1],p[3]
def sim(a,b): return sum(x==y for x,y in zip(a,b))
def mse(pred,rows): return sum((p-int(r['controlled_delta']))**2 for p,r in zip(pred,rows))/len(rows)
def metric(name,pred,rows):
 nz=[(p,int(r['controlled_delta'])) for p,r in zip(pred,rows) if int(r['controlled_delta'])!=0]
 cov=[(p,y) for p,y in nz if sign(p)!=0]; cor=sum(sign(p)==sign(y) for p,y in cov)
 zr=[p for p,r in zip(pred,rows) if int(r['controlled_delta'])==0]
 return {'predictor':name,'mse':mse(pred,rows),'future_nonzero':len(nz),'future_nonzero_covered':len(cov),'future_nonzero_coverage':len(cov)/len(nz) if nz else None,'covered_nonzero_sign_accuracy':cor/len(cov) if cov else None,'predicted_nonzero_units':sum(sign(p)!=0 for p in pred),'false_positive_zero_units':sum(sign(p)!=0 for p in zr),'false_positive_zero_rate':sum(sign(p)!=0 for p in zr)/len(zr) if zr else None}
def group(probe,key):
 d=defaultdict(list)
 for r in probe:d[key(r)].append(int(r['controlled_delta']))
 return lambda r:mean(d.get(key(r),[]))
def feat(r,cand=False):
 f,o,q=sig(r['target_task_id']); d={'source':r['source_family'],'target':f,'object':o,'recep':q,'relation':'same' if r['source_family']==f else 'cross'}
 if cand:d['candidate']=r['memory_id']
 return d
def tree(probe,future,cand,depth):
 keys=list(feat(probe[0],cand)); X=[[feat(r,cand)[k] for k in keys] for r in probe]; Z=[[feat(r,cand)[k] for k in keys] for r in future]; y=np.array([int(r['controlled_delta']) for r in probe],float)
 m=make_pipeline(OneHotEncoder(handle_unknown='ignore'),DecisionTreeRegressor(max_depth=depth,min_samples_leaf=2,random_state=20260811)); m.fit(X,y); return [float(x) for x in m.predict(Z)]
def analyze(run,out):
 cp=out/'contract.json'
 if sha(cp)!=CONTRACT: raise RuntimeError('contract hash mismatch')
 c=js(cp); full=run/'full-support-table'; rec=js(full/'provenance-recovery/final-decision.json')
 if rec.get('decision')!='PROVENANCE_INCONCLUSIVE' or rec.get('evidence_role')!='diagnostic-only': raise RuntimeError('source must be diagnostic-only')
 rows=[]
 with (full/'main_table.csv').open(newline='') as h:
  for r in csv.DictReader(h): r['controlled_delta']=int(r['controlled_delta']); rows.append(r)
 probe=[r for r in rows if r['evaluation_role']=='probe_development']; future=[r for r in rows if r['evaluation_role']=='future_eval']
 if (len(rows),len(probe),len(future))!=(72,36,36): raise RuntimeError('split integrity')
 by=defaultdict(list)
 for r in probe: by[r['memory_id']].append(r)
 if len(by)!=12 or any(len(v)!=3 for v in by.values()): raise RuntimeError('candidate profile integrity')
 def local(r,mapping=None):
  mid=(mapping or {}).get(r['memory_id'],r['memory_id']); src=by[mid]; s=sig(r['target_task_id']); best=max(sim(s,sig(x['target_task_id'])) for x in src); return mean([x['controlled_delta'] for x in src if sim(s,sig(x['target_task_id']))==best])
 def cmean(r): return mean([x['controlled_delta'] for x in by[r['memory_id']]])
 def nearest(r):
  s=sig(r['target_task_id']); best=max(sim(s,sig(x['target_task_id'])) for x in probe); return mean([x['controlled_delta'] for x in probe if sim(s,sig(x['target_task_id']))==best])
 sf=group(probe,lambda r:r['source_family']); tf=group(probe,lambda r:r['target_family']); rel=group(probe,lambda r:r['source_family']==r['target_family'])
 preds={'candidate-local-scope':[local(r) for r in future],'zero':[0.0]*len(future),'candidate-probe-mean':[cmean(r) for r in future],'source-family-probe-mean':[sf(r) for r in future],'target-family-probe-mean':[tf(r) for r in future],'same-vs-cross-relation-probe-mean':[rel(r) for r in future],'candidate-free-global-nearest-signature':[nearest(r) for r in future]}
 for d in (1,2,3): preds[f'structural-cart-depth-{d}']=tree(probe,future,False,d); preds[f'candidate-structural-cart-depth-{d}']=tree(probe,future,True,d)
 met={k:metric(k,v,future) for k,v in preds.items()}; localm=met['candidate-local-scope']; zero=met['zero']; cm=met['candidate-probe-mean']
 cf=['source-family-probe-mean','target-family-probe-mean','same-vs-cross-relation-probe-mean','candidate-free-global-nearest-signature','structural-cart-depth-1','structural-cart-depth-2','structural-cart-depth-3']
 bestcf=min(cf,key=lambda k:met[k]['mse']); bestany=min([k for k in met if k!='candidate-local-scope'],key=lambda k:met[k]['mse'])
 ids=sorted(by); rng=random.Random(20260811); pm=[]
 for _ in range(10000):
  s=ids[:]; rng.shuffle(s); mp=dict(zip(ids,s)); pm.append(mse([local(r,mp) for r in future],future))
 p=(1+sum(x<=localm['mse']+1e-12 for x in pm))/(1+len(pm)); t=c['screen_pass_requires_all']
 ratio=localm['mse']/cm['mse'] if cm['mse'] else None
 checks={'candidate_shuffle_signal':{'actual':p,'required_p_max':t['candidate_shuffle_p_max'],'pass':p<=t['candidate_shuffle_p_max']},'scope_beats_candidate_mean_by_10pct':{'actual_ratio':ratio,'required_ratio_max':t['scope_mse_vs_candidate_mean_ratio_max'],'pass':bool(ratio is not None and ratio<=t['scope_mse_vs_candidate_mean_ratio_max'])},'scope_beats_zero':{'scope_mse':localm['mse'],'zero_mse':zero['mse'],'pass':localm['mse']<zero['mse']},'scope_beats_best_candidate_free':{'scope_mse':localm['mse'],'baseline':bestcf,'baseline_mse':met[bestcf]['mse'],'pass':localm['mse']<met[bestcf]['mse']},'future_nonzero_coverage':{'actual':localm['future_nonzero_coverage'],'required_min':t['future_nonzero_coverage_min'],'pass':(localm['future_nonzero_coverage'] or 0)>=t['future_nonzero_coverage_min']},'covered_nonzero_sign_accuracy':{'actual':localm['covered_nonzero_sign_accuracy'],'required_min':t['covered_nonzero_sign_accuracy_min'],'pass':(localm['covered_nonzero_sign_accuracy'] or 0)>=t['covered_nonzero_sign_accuracy_min']}}
 passed=all(v['pass'] for v in checks.values())
 result={'schema_version':'1.0','analysis_id':AID,'created_at':now(),'decision':'APPLICABILITY_STRUCTURE_SCREEN_PASS_R1_ELIGIBLE' if passed else 'NO_R1_VOI_STOP_STANDALONE','screen_pass':passed,'clean_r1_authorized':False,'clean_r1_eligible_for_human_authorization':passed,'method_failure_authorized':False,'second_model_authorized':False,'scientific_role':c['scientific_role'],'source_evidence':{'contract_sha256':sha(cp),'main_table_sha256':sha(full/'main_table.csv'),'provenance_final_sha256':sha(full/'provenance-recovery/final-decision.json'),'provenance_decision':rec['decision'],'evidence_role':rec['evidence_role']},'split_summary':{'probe_units':36,'future_units':36,'probe_nonzero':sum(r['controlled_delta']!=0 for r in probe),'future_nonzero':sum(r['controlled_delta']!=0 for r in future)},'metrics':met,'candidate_shuffle':{'permutations':10000,'seed':20260811,'observed_mse':localm['mse'],'permutation_mean_mse':mean(pm),'p_value':p},'best_candidate_free_baseline':bestcf,'best_any_baseline':bestany,'checks':checks,'next_action':'Freeze a fresh source-locked same-backbone R1 design for human authorization; #5 remains merged as a secondary scope-conditioned transport analysis.' if passed else 'Do not launch clean R1 or a second backbone. Stop standalone #3/#5 escalation; retain #5 only as archived secondary transport analysis and preserve all old evidence as diagnostic-only.'}
 pr=[]
 for i,r in enumerate(future):
  x={'unit_id':r['unit_id'],'memory_id':r['memory_id'],'candidate_role':r['candidate_role'],'source_family':r['source_family'],'target_family':r['target_family'],'target_task_id':r['target_task_id'],'actual_controlled_delta':r['controlled_delta']}
  for k,v in preds.items(): x[k]=v[i]
  pr.append(x)
 result['predictions']=pr
 return result
def main():
 a=argparse.ArgumentParser(); a.add_argument('--run-dir',type=Path,required=True); a.add_argument('--output-dir',type=Path,required=True); z=a.parse_args(); r=analyze(z.run_dir,z.output_dir)
 (z.output_dir/'decision.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 with (z.output_dir/'predictions.csv').open('w',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(r['predictions'][0])); w.writeheader(); w.writerows(r['predictions'])
 m={'schema_version':'1.0','analysis_id':AID,'cpu_only':True,'outputs':['contract.json','decision.json','predictions.csv'],'source_table_modified':False,'method_failure_authorized':False,'second_model_authorized':False,'created_at':now()}; (z.output_dir/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps({'decision':r['decision'],'screen_pass':r['screen_pass'],'candidate_shuffle_p':r['candidate_shuffle']['p_value'],'local_scope_mse':r['metrics']['candidate-local-scope']['mse'],'candidate_mean_mse':r['metrics']['candidate-probe-mean']['mse'],'best_candidate_free':r['best_candidate_free_baseline'],'best_candidate_free_mse':r['metrics'][r['best_candidate_free_baseline']]['mse'],'future_nonzero_coverage':r['metrics']['candidate-local-scope']['future_nonzero_coverage'],'sign_accuracy':r['metrics']['candidate-local-scope']['covered_nonzero_sign_accuracy'],'checks':r['checks']},ensure_ascii=False))
if __name__=='__main__': main()
