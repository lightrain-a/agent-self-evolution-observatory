from __future__ import annotations

import argparse, hashlib, inspect, json, math, time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import numpy as np

CANDIDATE_ID='SHADOW-P05-C01'
CONTRACT_SHA='834e3415836389161daa063e9908fd70a90cd87ece1112fbdeb42e91e8598615'
PLAN_SHA='d8b5b8d62d0bd26a73ed1425c7d090f2f2c8816d1d487d2fa49037adcfd23ff8'
D=10; PATTERNS=64; METRIC_DIM=1+PATTERNS+4

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:
 o=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(o,dict):raise ValueError('expected-object')
 return o
def seed(ns:str,i:int,suffix:str)->int:return int.from_bytes(hashlib.sha256(f'{ns}|{i}|{suffix}'.encode()).digest()[:8],'big')&0x7fffffff

def validate_plan(path:Path)->dict[str,Any]:
 if sha(path)!=PLAN_SHA:raise ValueError('plan-sha-mismatch')
 p=load(path)
 if p.get('candidate_id')!=CANDIDATE_ID or p.get('contract_sha256')!=CONTRACT_SHA:raise ValueError('contract-mismatch')
 u=p.get('units') or {}; b=p.get('budget') or {}
 if (int(u.get('equivalence_pairs',0)),int(u.get('main_pairs',0)))!=(8,16):raise ValueError('pair-budget-mismatch')
 if int(b.get('planned_pairs',0))!=24 or float(b.get('max_gpu_hours',-1))!=0 or int(b.get('max_model_calls',-1))!=0:raise ValueError('cpu-budget-mismatch')
 return p

def hidden_truth(x:np.ndarray)->np.ndarray:
 x=np.asarray(x,dtype=np.int8)
 a=np.bitwise_xor(np.bitwise_xor(x[...,0],x[...,1]),x[...,2])
 b=(x[...,3]+x[...,4]+x[...,5]>=2).astype(np.int8)
 return np.bitwise_xor(a,b).astype(np.int8)
def pidx(x:np.ndarray)->np.ndarray:
 x=np.asarray(x,dtype=np.int8); powers=(1<<np.arange(6,dtype=np.int64)); return (x[...,:6].astype(np.int64)*powers).sum(axis=-1)
def phi(x:np.ndarray)->np.ndarray:
 x=np.asarray(x,dtype=float); idx=pidx(x); one=np.zeros((len(x),PATTERNS));one[np.arange(len(x)),idx]=1
 return np.concatenate([np.ones((len(x),1)),one,x[:,6:10]],axis=1)
def sig(z):z=np.clip(z,-30,30);return 1/(1+np.exp(-z))
def mprob(w,x):return sig(phi(x)@w)
def task_score(x):
 x=np.asarray(x,dtype=float);return .55+.15*x[...,6]+.15*x[...,7]+.075*x[...,8]+.075*x[...,9]
def diversity(pop):
 if len(pop)<2:return 0.
 d=(pop[:,None,:]!=pop[None,:,:]).mean(-1);ii=np.triu_indices(len(pop),1);return float(d[ii].mean())
def ancestry(pop,warm):
 if not len(pop):return 0.
 d=(pop[:,None,:]!=warm[None,:,:]).mean(-1);return float((1-d.min(1)).mean())
def det_summary(w):
 q=w[1:65];return {'bias':float(w[0]),'pattern_mean':float(q.mean()),'pattern_std':float(q.std()),'task_weight_l1':float(np.abs(w[-4:]).sum())}

def balanced_set(rng,repeats):
 rows=[]
 for pat in range(64):
  bits=np.array([(pat>>i)&1 for i in range(6)],dtype=np.int8)
  for _ in range(repeats):rows.append(np.concatenate([bits,rng.integers(0,2,size=4,dtype=np.int8)]))
 a=np.stack(rows);rng.shuffle(a);return a
def initial_pop(rng,n):
 pool=rng.integers(0,2,size=(n*32,D),dtype=np.int8);good=pool[task_score(pool)>=.70];sel=[]
 for r in good:
  if not sel or float(np.mean(np.stack(sel)!=r,axis=1).min())>=.20:sel.append(r.copy())
  if len(sel)>=n:break
 if len(sel)<n:
  for r in good:
   sel.append(r.copy())
   if len(sel)>=n:break
 if len(sel)<n:raise RuntimeError('initial-pop-insufficient')
 return np.stack(sel[:n])

def metric_update(w,x,y,lr=.8,steps=8,l2=.002):
 w=w.copy();X=phi(x);y=np.asarray(y,dtype=float)
 for _ in range(steps):w-=lr*(X.T@(sig(X@w)-y)/len(X)+l2*w)
 return w
def post_update(w,pop):return metric_update(w,pop,(task_score(pop)>=.80).astype(float),lr=.35,steps=4,l2=.004)

def evolve(pop,w,turnover,rng,proposal_pool,mutation_p):
 n=len(pop);rep=max(1,min(n-1,int(round(n*turnover))))
 parents=rng.integers(0,n,size=proposal_pool);props=pop[parents].copy();props=np.bitwise_xor(props,(rng.random(props.shape)<mutation_p).astype(np.int8))
 ts=task_score(props);ms=mprob(w,props);fit=.60*ts+.40*ms;cur=.60*task_score(pop)+.40*mprob(w,pop)
 keep=np.argsort(-cur,kind='mergesort')[:n-rep];sel=[pop[i].copy() for i in keep]
 for j in np.argsort(-fit,kind='mergesort'):
  c=props[j]
  if ts[j]<.70:continue
  md=float(np.mean(np.stack(sel)!=c,axis=1).min()) if sel else 1.
  if md<.10:continue
  sel.append(c.copy())
  if len(sel)==n:break
 if len(sel)<n:
  for j in np.argsort(-fit,kind='mergesort'):
   if ts[j]<.70:continue
   sel.append(props[j].copy())
   if len(sel)==n:break
 if len(sel)!=n:raise RuntimeError('replacement-pool-insufficient')
 return np.stack(sel),{'replace_n':rep,'proposal_pool':proposal_pool}

@dataclass
class State:
 w:np.ndarray;pop:np.ndarray;warm:np.ndarray;locked_x:np.ndarray;locked_y:np.ndarray;anchor_x:np.ndarray;anchor_y:np.ndarray;warm_rows:list[dict[str,Any]]

def eval_cycle(s:State,pair,arm,cycle,removed,updates,turn):
 pred=(mprob(s.w,s.locked_x)>=.5).astype(np.int8)
 return {'pair_id':pair,'arm':arm,'cycle':cycle,'elapsed_cycle':cycle,'checkpoint_age':max(0,cycle-4),'anchor_removed':int(removed),'metric_update_count':updates,'turnover_fraction':float(turn),'locked_validity':float((pred==s.locked_y).mean()),'always_pass_rate':float(pred.mean()),'task_score':float(task_score(s.pop).mean()),'output_diversity':diversity(s.pop),'ancestry_overlap':ancestry(s.pop,s.warm),'composition_drift':1-ancestry(s.pop,s.warm),'detector':det_summary(s.w)}

def common_warmup(p,seed_id):
 ns=p['units']['seed_namespace'];rt=np.random.default_rng(seed(ns,seed_id,'truth'));ra=np.random.default_rng(seed(ns,seed_id,'anchor'));rp=np.random.default_rng(seed(ns,seed_id,'population'))
 lx=balanced_set(rt,8);ax=balanced_set(ra,4);pop=initial_pop(rp,int(p['generator']['population_size']));s=State(np.zeros(METRIC_DIM),pop,pop.copy(),lx,hidden_truth(lx),ax,hidden_truth(ax),[]);updates=0
 for c in range(int(p['dynamics']['warmup_cycles'])):
  s.w=metric_update(s.w,s.anchor_x,s.anchor_y);updates+=1;rc=np.random.default_rng(seed(ns,seed_id,f'warmup-{c}'))
  s.pop,_=evolve(s.pop,s.w,.20,rc,int(p['generator']['proposal_pool_per_cycle']),float(p['generator']['mutation_bit_probability']));s.warm=s.pop.copy()
  s.warm_rows.append(eval_cycle(s,f'seed-{seed_id}','common',c+1,False,updates,.20))
 return s

def clone(s):return State(s.w.copy(),s.pop.copy(),s.warm.copy(),s.locked_x.copy(),s.locked_y.copy(),s.anchor_x.copy(),s.anchor_y.copy(),[dict(r) for r in s.warm_rows])
def run_arm(p,base,seed_id,arm,turn,anchors_retained):
 s=clone(base);ns=p['units']['seed_namespace'];rows=[];updates=int(p['dynamics']['warmup_cycles'])
 for k in range(int(p['dynamics']['post_anchor_cycles'])):
  cyc=int(p['dynamics']['warmup_cycles'])+k+1;rc=np.random.default_rng(seed(ns,seed_id,f'post-{k}'))
  s.pop,meta=evolve(s.pop,s.w,turn,rc,int(p['generator']['proposal_pool_per_cycle']),float(p['generator']['mutation_bit_probability']))
  s.w=metric_update(s.w,s.anchor_x,s.anchor_y) if anchors_retained else post_update(s.w,s.pop);updates+=1
  r=eval_cycle(s,f'seed-{seed_id}',arm,cyc,not anchors_retained,updates,turn);r['replacement_count']=meta['replace_n'];r['proposal_pool']=meta['proposal_pool'];rows.append(r)
 return rows

def matching(p,hi,lo):
 m=p['matching'];td=abs(np.mean([r['task_score'] for r in hi])-np.mean([r['task_score'] for r in lo]));dd=abs(np.mean([r['output_diversity'] for r in hi])-np.mean([r['output_diversity'] for r in lo]));ad=abs(np.mean([r['ancestry_overlap'] for r in hi])-np.mean([r['ancestry_overlap'] for r in lo]));ue=[r['metric_update_count'] for r in hi]==[r['metric_update_count'] for r in lo]
 sufficient=min(np.mean([r['task_score'] for r in hi]),np.mean([r['task_score'] for r in lo]))>=float(p['decision_gates']['task_score_sufficient_min'])
 ok=td<=m['max_abs_mean_task_score_difference'] and dd<=m['max_abs_output_diversity_difference'] and ad<=m['max_abs_ancestry_overlap_difference'] and ue and sufficient
 return {'passed':bool(ok),'task_diff':float(td),'diversity_diff':float(dd),'ancestry_diff':float(ad),'metric_updates_exact':bool(ue),'task_sufficient':bool(sufficient)}

def sign_p(vals):
 pos=sum(v>1e-12 for v in vals);neg=sum(v<-1e-12 for v in vals);n=pos+neg
 return 1. if n==0 else float(sum(math.comb(n,k) for k in range(pos,n+1))/(2**n))
def baseline_matrix(rows):
 by={(r['pair_id'],r['arm'],r['cycle']):r for r in rows};X=[];y=[]
 for r in rows:
  prev=by.get((r['pair_id'],r['arm'],r['cycle']-1));pv=float(prev['locked_validity']) if prev else float(r['locked_validity'])
  X.append([r['elapsed_cycle'],r['checkpoint_age'],r['anchor_removed'],pv,r['metric_update_count'],r['task_score'],r['output_diversity'],r['ancestry_overlap']]);y.append(r['locked_validity'])
 return np.asarray(X,float),np.asarray(y,float)
def ridge(train_x,train_y,test_x,lam):
 mu=train_x.mean(0);sd=train_x.std(0);sd[sd<1e-9]=1;x=(train_x-mu)/sd;xt=(test_x-mu)/sd;x=np.c_[np.ones(len(x)),x];xt=np.c_[np.ones(len(xt)),xt];R=np.eye(x.shape[1])*lam;R[0,0]=0
 return xt@np.linalg.solve(x.T@x+R,x.T@train_y)

def protocol_probe(plan_path):
 p=validate_plan(plan_path);ep=set(inspect.signature(evolve).parameters);up=set(inspect.signature(post_update).parameters)
 x=np.zeros((16,D),dtype=np.int8);x[:,6:]=np.tile(np.array([[0,0,0,0],[1,1,1,1]],dtype=np.int8),(8,1))
 checks={'plan_hash':sha(plan_path)==PLAN_SHA,'cpu_only':p['budget']['max_gpu_hours']==0 and p['budget']['max_model_calls']==0,'hidden_truth_not_evolution_input':not any('truth' in z or 'locked' in z for z in ep),'hidden_truth_not_post_update_input':not any('truth' in z or 'locked' in z for z in up),'truth_independent_of_task_bits':len(set(hidden_truth(x).tolist()))==1,'pair_budget':p['units']['equivalence_pairs']+p['units']['main_pairs']<=p['budget']['max_units'],'baseline_excludes_turnover':all(all(q not in z for q in ('turnover','replacement','drift')) for z in p['baseline']['features'])}
 return {'candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA,'plan_sha256':sha(plan_path),'checks':checks,'passed':all(checks.values()),'scientific_authority':False}
def manifest(plan_path,out):
 pr=protocol_probe(plan_path);o={'schema_version':'1.0-private','candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA,'plan_sha256':sha(plan_path),'runtime_code_sha256':sha(Path(__file__).resolve()),'numpy_version':np.__version__,'probe':pr,'sandboxed':True,'budget_feasible':pr['checks']['cpu_only'] and pr['checks']['pair_budget'],'scientific_authority':False};out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');return {**o,'harness_manifest_sha256':sha(out)}

def execute(plan_path,out):
 p=validate_plan(plan_path);start=time.monotonic();hi_t=float(p['dynamics']['high_turnover_fraction']);lo_t=float(p['dynamics']['low_turnover_fraction']);eq=[];eqrows=[]
 for sid in range(int(p['units']['equivalence_pairs'])):
  base=common_warmup(p,sid);hi=run_arm(p,base,sid,'high',hi_t,True);lo=run_arm(p,base,sid,'low',lo_t,True);m=matching(p,hi,lo);wp=max(r['locked_validity'] for r in base.warm_rows);eq.append({'pair_id':f'seed-{sid}','matching':m,'terminal_validity_difference':abs(hi[-1]['locked_validity']-lo[-1]['locked_validity']),'high_validity_drop_from_warmup_peak':wp-hi[-1]['locked_validity'],'low_validity_drop_from_warmup_peak':wp-lo[-1]['locked_validity'],'terminal_always_pass_max':max(hi[-1]['always_pass_rate'],lo[-1]['always_pass_rate'])});eqrows+=hi+lo
 e=p['equivalence_probe'];valid=[x for x in eq if x['matching']['passed']];eqpass=len(valid)>=e['minimum_valid_pairs'] and all(x['terminal_validity_difference']<=e['max_abs_terminal_validity_difference'] and x['high_validity_drop_from_warmup_peak']<=e['max_allowed_validity_drop_from_warmup_peak'] and x['low_validity_drop_from_warmup_peak']<=e['max_allowed_validity_drop_from_warmup_peak'] and x['terminal_always_pass_max']<=e['max_terminal_always_pass_rate'] for x in valid)
 main=[];meta=[]
 if eqpass:
  off=int(p['units']['equivalence_pairs'])
  for j in range(int(p['units']['main_pairs'])):
   sid=off+j;base=common_warmup(p,sid);hi=run_arm(p,base,sid,'high',hi_t,False);lo=run_arm(p,base,sid,'low',lo_t,False);meta.append({'pair_id':f'seed-{sid}','matching':matching(p,hi,lo),'warmup_start_validity':base.warm_rows[0]['locked_validity'],'warmup_terminal_validity':base.warm_rows[-1]['locked_validity']});main+=hi+lo
 raw=out.with_suffix('.jsonl');raw.parent.mkdir(parents=True,exist_ok=True)
 with raw.open('w',encoding='utf-8') as f:
  for r in [{**x,'phase':'equivalence'} for x in eqrows]+[{**x,'phase':'main'} for x in main]:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 o={'candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA,'plan_sha256':sha(plan_path),'equivalence_probe_passed':bool(eqpass),'equivalence_pairs':eq,'main_pair_metadata':meta,'main_executed':bool(eqpass),'raw_rows_path':str(raw),'wall_seconds':round(time.monotonic()-start,6),'gpu_hours':0.0,'model_calls':0,'scientific_authority':False};out.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');return o

def analyze(plan_path,run_path,out):
 p=validate_plan(plan_path);run=load(run_path);raw=Path(run['raw_rows_path']);rows=[json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines() if x.strip()];main=[r for r in rows if r.get('phase')=='main'];meta={x['pair_id']:x for x in run.get('main_pair_metadata') or []}
 if not run.get('equivalence_probe_passed'):
  metrics={'equivalence_probe_passed':False,'valid_main_pairs':0};outcome='INCONCLUSIVE'
 else:
  ids=sorted({r['pair_id'] for r in main});valid=[i for i in ids if meta.get(i,{}).get('matching',{}).get('passed')];term={}
  for i in ids:
   for arm in ('high','low'):
    rr=sorted([r for r in main if r['pair_id']==i and r['arm']==arm],key=lambda z:z['cycle'])
    if rr:term[(i,arm)]=rr[-1]
  vg=[term[(i,'low')]['locked_validity']-term[(i,'high')]['locked_validity'] for i in valid];pg=[term[(i,'high')]['always_pass_rate']-term[(i,'low')]['always_pass_rate'] for i in valid];res=[];lam=float(p['baseline']['ridge_lambda'])
  for held in valid:
   tr=[r for r in main if r['pair_id']!=held];te=[r for r in main if r['pair_id']==held]
   if not tr or not te:continue
   tx,ty=baseline_matrix(tr);hx,_=baseline_matrix(te);pred=ridge(tx,ty,hx,lam);pb={(r['arm'],r['cycle']):float(y) for r,y in zip(te,pred)};mc=max(r['cycle'] for r in te);actual=term[(held,'low')]['locked_validity']-term[(held,'high')]['locked_validity'];predgap=pb[('low',mc)]-pb[('high',mc)];res.append(actual-predgap)
  g=p['decision_gates'];n=len(valid);mv=float(np.mean(vg)) if vg else float('nan');mp=float(np.mean(pg)) if pg else float('nan');mr=float(np.mean(res)) if res else float('nan');sp=sign_p(res);wg=float(np.mean([meta[i]['warmup_terminal_validity']-meta[i]['warmup_start_validity'] for i in valid])) if valid else float('nan');adequate=n>=g['minimum_valid_main_pairs'] and len(res)==n;practical=(mv>=g['practical_terminal_validity_gap_low_minus_high_min'] or mp>=g['practical_terminal_always_pass_gap_high_minus_low_min']) if adequate else False;survive=bool(adequate and practical and mr>=g['baseline_residual_validity_gap_min'] and sp<=g['paired_direction_sign_test_p_max']);outcome='INCONCLUSIVE' if not adequate else ('RESIDUAL_SURVIVES' if survive else 'REDUCTION_SUPPORTED');metrics={'equivalence_probe_passed':True,'valid_main_pairs':n,'main_pairs_total':len(ids),'mean_terminal_validity_gap_low_minus_high':mv,'mean_terminal_always_pass_gap_high_minus_low':mp,'mean_baseline_residual_validity_gap':mr,'paired_direction_sign_test_p':sp,'mean_warmup_validity_gain':wg,'practical_headroom_met':bool(practical),'residual_gate_met':bool(survive),'matching':{i:meta[i]['matching'] for i in ids}}
 material={'contract':CONTRACT_SHA,'plan':sha(plan_path),'run':sha(run_path),'raw':sha(raw),'outcome':outcome,'metrics':metrics};msha=hashlib.sha256(json.dumps(material,sort_keys=True,separators=(',',':')).encode()).hexdigest();o={'candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA,'outcome':outcome,'qualified_units':int(metrics.get('valid_main_pairs',0)),'protocol_valid':bool(run.get('equivalence_probe_passed')),'metric_summary':json.dumps(metrics,ensure_ascii=False,sort_keys=True),'metrics':metrics,'evidence_manifest_sha256':msha,'gpu_hours':0.0,'model_calls':0,'decision_rule_frozen_before_execution':True,'scientific_authority':False};out.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');return o

def main():
 a=argparse.ArgumentParser();a.add_argument('command',choices=('probe','manifest','run','analyze'));a.add_argument('--plan',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--run-json',type=Path);x=a.parse_args()
 if x.command=='probe':r=protocol_probe(x.plan);x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 elif x.command=='manifest':r=manifest(x.plan,x.output)
 elif x.command=='run':r=execute(x.plan,x.output)
 else:
  if not x.run_json:raise SystemExit('--run-json required')
  r=analyze(x.plan,x.run_json,x.output)
 print(json.dumps(r,ensure_ascii=False))
if __name__=='__main__':main()
