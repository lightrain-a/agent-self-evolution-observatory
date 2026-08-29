from __future__ import annotations
import glob,json,math,random,re
from collections import Counter
from pathlib import Path
R=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-scmb-p0-fresh-uptake-20260829-pilot-v1'); OUT=Path(__file__).resolve().parent/'c1-scmb-independent-verification-20260829.json'
def tv(a,b):
 ca,cb=Counter(a),Counter(b);n,m=len(a),len(b);ks=set(ca)|set(cb);return .5*sum(abs(ca[k]/n-cb[k]/m) for k in ks)
def toks(s):return set(re.findall(r'[a-z0-9]+',s.lower()))
def jac(a,b):
 a,b=toks(a),toks(b);return len(a&b)/len(a|b) if a|b else 1
def main():
 cases=[json.load(open(p)) for p in glob.glob(str(R/'per_case/*.json'))]; assert len(cases)==432 and all(x['status']=='complete' for x in cases)
 tids=sorted({x['future_task'] for x in cases}); per=[]
 for tid in tids:
  x={'future_task':tid}
  for arm in ['A0_NATIVE','A1_MEMORY_ONLY_ADAPTER','A2_STATE_CONDITIONED_BINDING']:
   s=[z['action_signature'] for z in cases if z['future_task']==tid and z['arm']==arm and z['branch']=='success'];f=[z['action_signature'] for z in cases if z['future_task']==tid and z['arm']==arm and z['branch']=='failure'];assert len(s)==len(f)==6;x['U_'+arm]=tv(s,f)
  x['D']=x['U_A2_STATE_CONDITIONED_BINDING']-x['U_A1_MEMORY_ONLY_ADAPTER'];x['N']=x['U_A2_STATE_CONDITIONED_BINDING']-x['U_A0_NATIVE'];per.append(x)
 means={k:sum(x[k] for x in per)/12 for k in ['U_A0_NATIVE','U_A1_MEMORY_ONLY_ADAPTER','U_A2_STATE_CONDITIONED_BINDING','D','N']}
 analysis=json.load(open(R/'pilot-analysis.json'));assert abs(means['D']-analysis['effect_summary']['D_A2_minus_A1'])<1e-12 and abs(means['N']-analysis['effect_summary']['N_A2_minus_A0'])<1e-12
 bind=[json.load(open(p)) for p in glob.glob(str(R/'binder/*.json'))];idx={(x['future_task'],x['branch'],x['kind']):x for x in bind}
 div=[]
 for x in per:
  t=x['future_task'];j=jac(idx[(t,'success','A2')]['text'],idx[(t,'failure','A2')]['text']);div.append((x['D'],1-j))
 def corr(xs,ys):
  mx=sum(xs)/len(xs);my=sum(ys)/len(ys);vx=sum((x-mx)**2 for x in xs);vy=sum((y-my)**2 for y in ys);return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(vx*vy) if vx and vy else None
 D=[x['D'] for x in per];random.seed(20260829);boot=[]
 for _ in range(100000):boot.append(sum(random.choice(D) for _ in D)/12)
 boot.sort();sq=sorted([d*d for d in D],reverse=True); noncomp=[x for x in bind if x['kind']=='A2' and x['word_count']>60]
 out={'schema_version':'1.0','artifact_kind':'C1_SCMB_INDEPENDENT_VERIFICATION','status':'REPRODUCED_HETEROGENEOUS_AGGREGATE_SIGNAL_GATE_FAILS','cases':432,'binder_calls':48,'means':means,'D_signs':{'positive':sum(d>0 for d in D),'negative':sum(d<0 for d in D),'zero':sum(d==0 for d in D)},'D_bootstrap_95_ci':[boot[2500],boot[97499]],'top3_squared_D_mass_fraction':sum(sq[:3])/sum(sq),'posthoc_A2_branch_note_divergence_correlation_with_D':corr([x[0] for x in div],[x[1] for x in div]),'binder_format_noncompliance':[{'future_task':x['future_task'],'branch':x['branch'],'word_count':x['word_count']} for x in noncomp],'binder_noncompliance_drives_positive_cell':any(x['future_task'] in {z['future_task'] for z in per if z['D']>0} for x in noncomp),'old36_calls':0,'fresh_holdout_calls':0,'claim_boundary':'Aggregate uptake is higher under state-conditioned binding, but the pre-registered cross-state consistency gate fails. Treat as heterogeneous proof-of-concept signal, not validated general repair. The note-divergence correlation is post-hoc hypothesis generation only.'}
 OUT.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
