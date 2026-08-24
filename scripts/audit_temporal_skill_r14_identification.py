#!/usr/bin/env python3
from __future__ import annotations
import csv, collections, hashlib, json, math, random, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance/source-native-replay/D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK')
A1=BASE/'20260824-g0-stage-a-deepseek-plan-r2/results.csv'; O5=BASE/'20260824-temp-o5-deepseek-t-vs-r/results.csv'; OUT=ROOT/'generated/temporal-skill-r14-identification-audit-20260824.json'; CSV=ROOT/'generated/temporal-skill-r14-contrast-decomposition-20260824.csv'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def b(x):return str(x).lower()=='true'
def betacf(a,b,x):
 eps=3e-14;fmin=1e-300;qab=a+b;qap=a+1;qam=a-1;c=1.;d=1-qab*x/qap;d=fmin if abs(d)<fmin else d;d=1/d;h=d
 for m in range(1,201):
  m2=2*m;aa=m*(b-m)*x/((qam+m2)*(a+m2));d=1+aa*d;d=fmin if abs(d)<fmin else d;c=1+aa/c;c=fmin if abs(c)<fmin else c;d=1/d;h*=d*c
  aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2));d=1+aa*d;d=fmin if abs(d)<fmin else d;c=1+aa/c;c=fmin if abs(c)<fmin else c;d=1/d;de=d*c;h*=de
  if abs(de-1)<eps:break
 return h
def betai(a,b,x):
 if x<=0:return 0.;
 if x>=1:return 1.
 bt=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
 return bt*betacf(a,b,x)/a if x<(a+1)/(a+b+2) else 1-bt*betacf(b,a,1-x)/b
def tcdf(t,nu):
 x=nu/(nu+t*t);q=betai(nu/2,.5,x);return 1-.5*q if t>=0 else .5*q
def tppf(p,nu):
 lo,hi=-20.,20.
 for _ in range(100):
  mid=(lo+hi)/2
  if tcdf(mid,nu)<p:lo=mid
  else:hi=mid
 return (lo+hi)/2
def means(path):
 by=collections.defaultdict(lambda:collections.defaultdict(list));meta={}
 for r in csv.DictReader(open(path)):by[r['endpoint_id']][r['arm']].append(int(b(r['family_success'])));meta[r['endpoint_id']]={'phase':r['phase'],'family':r['failure_family']}
 return {e:{a:sum(v)/len(v) for a,v in x.items()} for e,x in by.items()},meta
m1,meta1=means(A1);mr,metar=means(O5);strata=[('C3_grounding','C3-R','exogenous_grounding'),('C4_grounding','C4-R','exogenous_grounding'),('EIA_mechanism_replication','C4-R4','temporal_cutoff')];decomp=[]
for label,phase,fam in strata:
 ids=[e for e,x in meta1.items() if x['phase']==phase and x['family']==fam];tn=statistics.mean(m1[e]['T_FROZEN']-m1[e]['N_FRESH'] for e in ids);tg=statistics.mean(m1[e]['T_FROZEN']-m1[e]['G0_NOOP'] for e in ids);gn=statistics.mean(m1[e]['G0_NOOP']-m1[e]['N_FRESH'] for e in ids);assert abs(tn-(tg+gn))<1e-12;decomp.append({'stratum':label,'endpoint_count':len(ids),'T_minus_N':tn,'T_minus_G0':tg,'G0_minus_N':gn,'identity_error':tn-(tg+gn),'classification':'net_repair_with_zero_observed_placebo_shift' if gn==0 and tn>0 else ('net_repair_with_surface_interaction' if tn>0 else 'no_net_repair')})
# portfolio TOST
d=[x['T_CALLABLE']-x['R_RETRIEVAL'] for x in mr.values()];n=len(d);mu=statistics.mean(d);sd=statistics.stdev(d);se=sd/math.sqrt(n);df=n-1;margin=.10;tlo=(mu+margin)/se;thi=(mu-margin)/se;p_lo=1-tcdf(tlo,df);p_hi=tcdf(thi,df);t90=tppf(.95,df);t95=tppf(.975,df)
# deterministic parametric sensitivity power under true zero and observed SD
rng=random.Random(20260824);reps=100000;passed=0
for _ in range(reps):
 xs=[rng.gauss(0,sd) for __ in range(n)];mm=sum(xs)/n;ss=statistics.stdev(xs);q=ss/math.sqrt(n);passed+=max(1-tcdf((mm+margin)/q,df),tcdf((mm-margin)/q,df))<.05
out={'schema_version':'1.0','receipt_type':'temporal-r14-identification-statistical-audit','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','data_bindings':{'A1_csv_sha256':sha(A1),'O5_csv_sha256':sha(O5)},'contrast_decomposition':decomp,'interpretation':{'T_minus_N':'net targeted-intervention repair relative to the original agent','T_minus_G0':'same-surface operation-output contrast conditional on the G0 exposure surface; not a pure operation effect when G0-N is nonzero','G0_minus_N':'surface/placebo perturbation diagnostic','rule':'Do not collapse the three contrasts into a pure operation attribution unless the placebo shift is itself negligible at the relevant resolution.'},'surface_equivalence':{'endpoint_count':n,'mean_T_minus_Rsurf':mu,'endpoint_sd':sd,'standard_error':se,'df':df,'frozen_material_margin':[-margin,margin],'TOST_alpha':.05,'TOST_lower_t':tlo,'TOST_lower_p':p_lo,'TOST_upper_t':thi,'TOST_upper_p':p_hi,'TOST_equivalence_pass':max(p_lo,p_hi)<.05,'paired_t_90_ci':[mu-t90*se,mu+t90*se],'paired_t_95_ci':[mu-t95*se,mu+t95*se],'smallest_symmetric_margin_supported_by_90_t_ci':abs(mu)+t90*se,'smallest_symmetric_margin_supported_by_95_t_ci':abs(mu)+t95*se,'parametric_equivalence_power_if_true_mean_zero_observed_sd':passed/reps,'power_simulation_draws':reps,'boundary':'The TOST supports portfolio-average equivalence at the prospectively frozen +/-10pp margin. It does not establish +/-10pp equivalence on the four strictly non-ceiling endpoints, whose bootstrap interval remains wide.'},'EIA_classification':{'label':'compatibility-selected mechanism replication','not':'prospective cross-domain confirmation','reason':'The 12 endpoint construction and 4/8 time split were frozen before EIA outcomes, but EIA was selected post-review for structural compatibility with the already frozen cutoff mechanism.'},'new_model_calls':0,'new_provider_calls':0,'scientific_authority':False,'submission_authority':False};out['receipt_sha256']=hashlib.sha256(json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');f=open(CSV,'w',newline='');w=csv.DictWriter(f,fieldnames=['stratum','endpoint_count','T_minus_N','T_minus_G0','G0_minus_N','identity_error','classification'],lineterminator='\n');w.writeheader();w.writerows(decomp);f.close();print(json.dumps({'receipt':str(OUT.relative_to(ROOT)),'receipt_sha256':out['receipt_sha256'],'csv':str(CSV.relative_to(ROOT)),'csv_sha256':sha(CSV),'TOST_max_p':max(p_lo,p_hi),'power':passed/reps},indent=2))
