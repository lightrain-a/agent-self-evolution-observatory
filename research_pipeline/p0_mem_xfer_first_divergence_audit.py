from __future__ import annotations
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import mannwhitneyu
from sklearn.metrics import average_precision_score,brier_score_loss,mutual_info_score,roc_auc_score
from .p0_alfworld_adapter import ALFWorldGameRunner,load_config

def J(p): return json.loads(Path(p).read_text())
def JL(p): return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def af(a):
 if a is None:return 'terminal'
 v=a.strip().split(' ',1)[0].lower() if a.strip() else ''
 return {'go':'navigate','examine':'inspect','open':'container','close':'container','take':'take','move':'place','put':'place','clean':'transform','cool':'transform','heat':'transform','slice':'transform','toggle':'toggle'}.get(v,v or 'other')
def req(f):
 for x in ('clean','cool','heat'):
  if x in f:return x
 return None
def phase(prefix,f):
 vs=[a.split(' ',1)[0].lower() for a in prefix]; ac='take' in vs; tr=req(f); td=bool(tr and tr in vs); pl=any(v in {'move','put'} for v in vs)
 if pl:p='post_place_or_recovery'
 elif not ac:p='pre_acquire'
 elif tr and not td:p='post_acquire_pre_transform'
 elif tr and td:p='post_transform_pre_place'
 else:p='post_acquire_pre_place'
 return p,ac,td,pl
def lcp(a,b):
 for i,(x,y) in enumerate(zip(a,b)):
  if x!=y:return i
 return min(len(a),len(b))
def gp(train,test,keys):
 g=float(np.mean([r['nonzero'] for r in train])); d=defaultdict(list)
 for r in train:d[tuple(r[k] for k in keys)].append(r['nonzero'])
 m={k:float(np.mean(v)) for k,v in d.items()}
 return [m.get(tuple(r[k] for k in keys),g) for r in test]
def met(y,p):
 return {'brier':float(brier_score_loss(y,p)),'average_precision':float(average_precision_score(y,p)) if sum(y) else None,'roc_auc':float(roc_auc_score(y,p)) if len(set(y))==2 else None}
def mip(rows,key,n=10000):
 y=np.array([r['nonzero'] for r in rows]); s=[r[key] for r in rows]; roles=np.array([r['evaluation_role'] for r in rows]); obs=float(mutual_info_score(s,y)); rng=np.random.default_rng(20260811); null=[]
 for _ in range(n):
  z=y.copy()
  for role in set(roles):
   ix=np.where(roles==role)[0]; z[ix]=rng.permutation(z[ix])
  null.append(mutual_info_score(s,z))
 null=np.array(null); return {'observed_mi':obs,'permutation_p':float((1+(null>=obs).sum())/(n+1)),'permutations':n,'null_mean':float(null.mean()),'null_p90':float(np.quantile(null,.9))}
def run(run_dir,out,config,contract_path):
 c=J(contract_path); full=run_dir/'full-support-table'; raw=JL(full/'raw-traces.jsonl'); main={r['unit_id']:r for r in csv.DictReader(open(full/'main_table.csv'))}
 if len(raw)!=216 or len(main)!=72: raise RuntimeError('frozen table shape mismatch')
 by=defaultdict(dict)
 for r in raw:by[r['unit_id']][r['arm']]=r
 runner=ALFWorldGameRunner(load_config(config)); data=Path(str(Path(run_dir).parents[1]/'alfworld')); rows=[]; bad=0
 for uid in sorted(main):
  a=by[uid]; ra=list(a['retrieved']['actions']); pa=list(a['placebo']['actions']); i=lcp(ra,pa); pre=ra[:i]; tf=main[uid]['target_family']; ph,ac,td,pl=phase(pre,tf); rf=af(ra[i] if i<len(ra) else None); pf=af(pa[i] if i<len(pa) else None)
  game=str(main[uid]['target_task_id']).replace('\\','/'); game=str(data/game.split('/alfworld/',1)[1]) if '/alfworld/' in game else game
  env=runner.build_env('eval_out_of_distribution',[game]); obs_text=''; adm=0; done=False
  try:
   obs,info=env.reset(); obs_text=str(obs[0])
   for act in pre:
    cmds=list((info.get('admissible_commands') or [[]])[0]); bad+=int(act not in cmds); obs,scores,dones,info=env.step([act]); obs_text=str(obs[0]); done=bool(dones[0])
    if done:break
   adm=0 if done else len(list((info.get('admissible_commands') or [[]])[0]))
  finally:
   close=getattr(env,'close',None)
   if callable(close):close()
  delta=int(main[uid]['controlled_delta']); sig=f'{ph}|{rf}>{pf}'
  rows.append({'unit_id':uid,'memory_id':main[uid]['memory_id'],'source_family':main[uid]['source_family'],'target_family':tf,'evaluation_role':main[uid]['evaluation_role'],'controlled_delta':delta,'nonzero':int(delta!=0),'first_divergence_index':i,'first_divergence_fraction':i/max(1,max(len(ra),len(pa))),'phase':ph,'object_acquired':int(ac),'required_transform_completed':int(td),'placement_seen':int(pl),'retrieved_action':ra[i] if i<len(ra) else '<TERMINAL>','placebo_action':pa[i] if i<len(pa) else '<TERMINAL>','retrieved_action_family':rf,'placebo_action_family':pf,'same_action_family':int(rf==pf),'state_signature':sig,'target_state_signature':f'{tf}|{sig}','prediv_admissible_count':adm,'prediv_observation':obs_text[:600]})
 train=[r for r in rows if r['evaluation_role']=='probe_development']; test=[r for r in rows if r['evaluation_role']=='future_eval']; y=[r['nonzero'] for r in test]; prev=float(np.mean(y))
 specs={'zero':None,'source_family':('source_family',),'target_family':('target_family',),'source_target_relation':('source_family','target_family'),'phase':('phase',),'state_signature':('state_signature',),'target_state_signature':('target_state_signature',)}; preds={}; metrics={}
 for n,k in specs.items():
  p=[0.0]*len(test) if k is None else gp(train,test,k); preds[n]=p; metrics[n]=met(y,p)
 task=min(['zero','source_family','target_family','source_target_relation'],key=lambda n:metrics[n]['brier']); state=min(['phase','state_signature','target_state_signature'],key=lambda n:metrics[n]['brier']); tb=metrics[task]['brier']; sb=metrics[state]['brier']; imp=(tb-sb)/tb if tb else 0; apm=(metrics[state]['average_precision'] or 0)/prev if prev else 0; mi=mip(rows,'state_signature')
 h=c['diagnostic_signal_heuristic']; checks={'state_brier_improvement':{'actual':imp,'required_min':h['state_brier_relative_improvement_over_best_task_baseline_min'],'pass':imp>=h['state_brier_relative_improvement_over_best_task_baseline_min']},'state_ap_multiple':{'actual':apm,'required_min':h['state_average_precision_vs_prevalence_multiple_min'],'pass':apm>=h['state_average_precision_vs_prevalence_multiple_min']},'state_signature_mi':{'actual_p':mi['permutation_p'],'required_p_max':h['state_signature_mi_permutation_p_max'],'pass':mi['permutation_p']<=h['state_signature_mi_permutation_p_max']}}
 signal=all(v['pass'] for v in checks.values())
 counts=defaultdict(lambda:{'n':0,'nonzero':0,'harm':0,'benefit':0})
 for r in rows:
  z=counts[r['state_signature']]; z['n']+=1; z['nonzero']+=r['nonzero']; z['harm']+=int(r['controlled_delta']<0); z['benefit']+=int(r['controlled_delta']>0)
 conc=sorted(({'signature':k,**v,'nonzero_rate':v['nonzero']/v['n']} for k,v in counts.items()),key=lambda x:(-x['nonzero'],-x['nonzero_rate'],-x['n'],x['signature']))
 nt=[r['first_divergence_fraction'] for r in rows if r['nonzero']]; zt=[r['first_divergence_fraction'] for r in rows if not r['nonzero']]; mw=mannwhitneyu(nt,zt,alternative='two-sided')
 out.mkdir(parents=True,exist_ok=True)
 with open(out/'state-table.csv','w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 with open(out/'future-predictions.csv','w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['unit_id','nonzero',*preds]); w.writeheader()
  for i,r in enumerate(test):w.writerow({'unit_id':r['unit_id'],'nonzero':r['nonzero'],**{n:preds[n][i] for n in preds}})
 d={'schema_version':'1.0','audit_id':c['audit_id'],'contract_sha256':c['contract_sha256'],'decision':'STATE_LOCALIZATION_SIGNAL' if signal else 'WEAK_OR_NO_STATE_LOCALIZATION','diagnostic_only':True,'method_pass_authorized':False,'method_failure_authorized':False,'r1_authorized':False,'formal_method_authorized':False,'second_model_authorized':False,'table_shape':{'units':len(rows),'probe_units':len(train),'future_units':len(test),'future_nonzero':sum(y)},'replay':{'bad_prefix_actions':bad,'pass':bad==0},'best_task_baseline':task,'best_state_model':state,'metrics':metrics,'future_prevalence':prev,'state_brier_relative_improvement':imp,'state_average_precision_multiple':apm,'state_signature_mi':mi,'checks':checks,'signature_concentration':conc,'divergence_timing':{'nonzero_mean':float(np.mean(nt)),'zero_mean':float(np.mean(zt)),'mann_whitney_u':float(mw.statistic),'p_value':float(mw.pvalue)},'interpretation':'The old candidate-global formulation may have aggregated away a state-localized causal signal; design a separate state-level hypothesis before any new experiment.' if signal else 'Current traces do not support the claim that task-level aggregation alone explains the failure; state-localization rescue is weak on this substrate. Do not revive B-8/B-9 from this diagnostic.'}
 (out/'decision.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 (out/'manifest.json').write_text(json.dumps({'audit_id':c['audit_id'],'contract_sha256':c['contract_sha256'],'source_raw_sha256':hashlib.sha256((full/'raw-traces.jsonl').read_bytes()).hexdigest(),'source_main_table_sha256':hashlib.sha256((full/'main_table.csv').read_bytes()).hexdigest(),'cpu_only':True,'model_calls':0,'gpu_calls':0},indent=2)+'\n')
 return d

def main():
 p=argparse.ArgumentParser(); p.add_argument('--run-dir',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True); p.add_argument('--config',type=Path,required=True); p.add_argument('--contract',type=Path,required=True); a=p.parse_args(); d=run(a.run_dir,a.output_dir,a.config,a.contract); print(json.dumps({'decision':d['decision'],'best_task_baseline':d['best_task_baseline'],'best_state_model':d['best_state_model'],'state_brier_relative_improvement':d['state_brier_relative_improvement'],'state_average_precision_multiple':d['state_average_precision_multiple'],'state_signature_mi_p':d['state_signature_mi']['permutation_p'],'checks':d['checks']}))
if __name__=='__main__':main()
