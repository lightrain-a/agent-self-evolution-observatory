#!/usr/bin/env python3
from __future__ import annotations
import csv, glob, hashlib, json, math, random, statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PID='D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK'
PDF_SHA='0fef51f15bb188fc669411be8d6dedaeae7d83389cec3f5d917f9a120fe2906e'
PRIVATE=Path('/data/wyt/agent-self-evolution-observatory/external-reviews')
O5=Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance/source-native-replay')/PID/'20260824-temp-o5-deepseek-t-vs-r'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def b(x):return str(x).lower()=='true'
def betacf(a,bv,x):
 eps=3e-14;fmin=1e-300;qab=a+bv;qap=a+1;qam=a-1;c=1.;d=1-qab*x/qap;d=fmin if abs(d)<fmin else d;d=1/d;h=d
 for m in range(1,201):
  m2=2*m;aa=m*(bv-m)*x/((qam+m2)*(a+m2));d=1+aa*d;d=fmin if abs(d)<fmin else d;c=1+aa/c;c=fmin if abs(c)<fmin else c;d=1/d;h*=d*c
  aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2));d=1+aa*d;d=fmin if abs(d)<fmin else d;c=1+aa/c;c=fmin if abs(c)<fmin else c;d=1/d;de=d*c;h*=de
  if abs(de-1)<eps:break
 return h
def betai(a,bv,x):
 if x<=0:return 0.
 if x>=1:return 1.
 bt=math.exp(math.lgamma(a+bv)-math.lgamma(a)-math.lgamma(bv)+a*math.log(x)+bv*math.log1p(-x))
 return bt*betacf(a,bv,x)/a if x<(a+1)/(a+bv+2) else 1-bt*betacf(bv,a,1-x)/bv
def tcdf(t,nu):
 x=nu/(nu+t*t);q=betai(nu/2,.5,x);return 1-.5*q if t>=0 else .5*q
def tost_power(n,sd,margin=.10,reps=30000,seed=20260824):
 if sd<=0:return None
 rng=random.Random(seed+n);df=n-1;ok=0
 for _ in range(reps):
  xs=[rng.gauss(0,sd) for __ in range(n)];m=sum(xs)/n;s=statistics.stdev(xs);se=s/math.sqrt(n)
  ok+=max(1-tcdf((m+margin)/se,df),tcdf((m-margin)/se,df))<.05
 return ok/reps

def latest_private():
 files=sorted(PRIVATE.glob('stanford-agentic-reviewer-20260824T*-e2-r14-result.json'))
 if not files: raise SystemExit('missing private R14 Stanford result')
 return files[-1]

def main():
 priv=latest_private(); obj=json.loads(priv.read_text()); resp=obj['response']; sec=resp.get('sections') or {}
 public={
  'schema_version':'1.0','paper_id':PID,'revision':'R14','service':'Stanford Agentic Reviewer · paperreview.ai','venue':resp.get('venue'),'pdf_sha256':PDF_SHA,
  'submission_date':resp.get('submission_date'),'review_date':resp.get('review_date'),'fetched_at_utc':obj.get('fetched_at_utc'),'numerical_score':resp.get('numerical_score'),
  'numeric_score_is_official_iclr_score':False,'textual_verdict':'Accept','assessment':sec.get('assessment',''),'summary':sec.get('summary',''),
  'strengths':sec.get('strengths',''),'weaknesses':sec.get('weaknesses',''),'questions':sec.get('questions',''),'binary_scores':sec.get('binary_scores',''),
  'token_included':False,'email_included':False,'scientific_authority':False,'experiment_authority':False,'submission_authority':False,
 }
 pubp=ROOT/'generated/temporal-skill-r14-stanford-review-result-20260824.json';pubp.write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
 # O5 endpoint means/residuals.
 by=defaultdict(lambda:defaultdict(list));meta={}
 for r in csv.DictReader(open(O5/'results.csv')):
  by[r['endpoint_id']][r['arm']].append(int(b(r['family_success'])));meta[r['endpoint_id']]={'phase':r['phase'],'family':r['failure_family']}
 rows=[]
 for e in sorted(by):
  t=sum(by[e]['T_CALLABLE'])/len(by[e]['T_CALLABLE']); rr=sum(by[e]['R_RETRIEVAL'])/len(by[e]['R_RETRIEVAL']);d=t-rr
  rows.append({'endpoint_id':e,**meta[e],'T_mean':t,'Rsurf_mean':rr,'T_minus_Rsurf':d,'non_tie':bool(d),'T_ceiling':t==1.0})
 csvp=ROOT/'generated/temporal-skill-r14-rsurf-endpoint-residuals-20260824.csv'
 with csvp.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 # Raw error diagnosis: exactly two non-tie endpoint means and opposite signs.
 raw=json.loads((O5/'results.json').read_text())['rows']; diagnoses=[]
 for e in [x['endpoint_id'] for x in rows if x['non_tie']]:
  er=[x for x in raw if x.get('endpoint_id')==e and x.get('arm') in ('T_CALLABLE','R_RETRIEVAL')]
  op_objects=[x.get('operation_output') for x in er]; parity_hashes=sorted({(x.get('retrieval_parity') or {}).get('operation_output_sha256') for x in er if (x.get('retrieval_parity') or {}).get('operation_output_sha256')})
  diagnoses.append({'endpoint_id':e,'mean_residual':next(x['T_minus_Rsurf'] for x in rows if x['endpoint_id']==e),'operation_output_content_equal_across_T_and_R':all(x==op_objects[0] for x in op_objects),'registered_operation_output_sha256':parity_hashes[0] if len(parity_hashes)==1 else None,'repeat_outcomes':[{'repeat':x.get('repeat_id'),'arm':x.get('arm'),'success':x.get('family_success'),'selected_span_ids':json.loads(x.get('raw_text') or '{}').get('selected_span_ids',[])} for x in sorted(er,key=lambda z:(z.get('repeat_id'),z.get('arm')))]})
 # Variance/power planning. Zero observed SD in tiny tie/ceiling cells is not treated as evidence of zero population variance.
 groups={'portfolio':rows,'C3_grounding':[x for x in rows if x['phase']=='C3-R'],'C4_grounding':[x for x in rows if x['phase']=='C4-R'],'EIA_cutoff':[x for x in rows if x['phase']=='C4-R4']}
 planning={}
 for name,rs in groups.items():
  ds=[x['T_minus_Rsurf'] for x in rs];sd=statistics.stdev(ds) if len(ds)>1 else 0.; planning[name]={'n':len(ds),'mean':statistics.mean(ds),'observed_sd':sd,'power_at_current_n_if_true_mean_zero':tost_power(len(ds),sd) if sd>0 else None,'zero_variance_caveat':sd==0}
 pooled_sd=planning['portfolio']['observed_sd']; planning['portfolio']['estimated_n_for_80pct_power_same_sd']=27; planning['portfolio']['simulated_power_n27']=tost_power(27,pooled_sd,reps=50000)
 planning['C4_grounding']['illustrative_power_n100_same_observed_sd']=tost_power(100,planning['C4_grounding']['observed_sd'],reps=20000)
 planning['C4_grounding']['estimated_n_for_80pct_power_same_sd']=110
 planning['C4_grounding']['simulated_power_n110']=tost_power(110,planning['C4_grounding']['observed_sd'],reps=30000)
 power={'schema_version':'1.0','analysis':'Rsurf post-review power/MDE planning sensitivity','margin':[-.10,.10],'margin_provenance':'The +/-10pp materiality threshold was frozen before Rsurf outcomes and was not selected from Rsurf variance or optimized to pass equivalence. The pre-outcome contract does not record a variance-based power rationale. A later scale note observes that already-known targeted contrasts were 20--60pp, but that note is contextual and is not retroactively treated as preregistered justification.','planning':planning,'interpretation':'At the pooled observed SD, n=18 has about 53% equivalence-detection sensitivity if the true mean is zero; about 27 independent endpoints would reach roughly 80% under the same variance. Family-specific observed SDs are unstable: C3/EIA are all ties/ceiling and cannot justify optimistic zero-variance planning; C4 has only five endpoints and large observed SD, with roughly 110 independent endpoints needed for about 80% sensitivity if that observed variance persisted. This is post-review future-design planning, not retroactive validation.','new_model_calls':0,'new_provider_calls':0}
 powerp=ROOT/'generated/temporal-skill-r14-rsurf-power-planning-20260824.json';powerp.write_text(json.dumps(power,ensure_ascii=False,indent=2)+'\n')
 adjud={
  'schema_version':'1.0','paper_id':PID,'revision':'R14','external_review':{'numeric':resp.get('numerical_score'),'textual':'Accept','round1':{'numeric':5.8,'textual':'Borderline Reject'},'round2':{'numeric':5.4,'textual':'Weak Accept'}},
  'decision':'ACCEPT_NO_SCIENTIFIC_REOPEN_FOR_CURRENT_NARROW_CLAIM','reason':'The fresh external reviewer accepts the R14 attribution-audit thesis. Remaining decision-critical improvements are clarification or existing-data analysis; requested benign-generic/non-ceiling expansion would be new evidence for broader confidence, not a prerequisite for the current narrow claim.',
  'questions':[
   {'id':'R14-S1','topic':'a priori +/-10pp margin and power','disposition':'ANALYSIS_AND_PAPER_ONLY','action':'State honestly that the margin was prospectively frozen as materiality, not power-derived; add post-review future-power planning and do not retrofit an a priori power claim.'},
   {'id':'R14-S2','topic':'benign mechanism-agnostic generic helper','disposition':'FUTURE_SCIENTIFIC_REOPEN_ONLY','action':'Do not run now. G is a stress comparator and G0 a same-surface placebo; a new benign generic is a distinct treatment for broader typical-practice triangulation.'},
   {'id':'R14-S3','topic':'multi-turn adaptive surface isolation','disposition':'PAPER_ONLY_FUTURE_DESIGN','action':'Add a prospective design sketch with episode as unit, synchronized evidence/output, and separate availability/use estimands; no current multi-turn claim.'},
   {'id':'R14-S4','topic':'per-endpoint Rsurf residuals/non-tie errors','disposition':'EXISTING_DATA_ANALYSIS','action':'Publish all 18 endpoint residuals and the two opposite-signed non-tie repeat patterns; no new calls.'},
   {'id':'R14-S5','topic':'alternative family/conjunctive scorers','disposition':'EXISTING_EVIDENCE_PAPER_ONLY','action':'Surface the already frozen auxiliary conjunctive-score sensitivity and explain the estimand mismatch; do not redefine the primary scorer post outcome.'},
   {'id':'R14-S6','topic':'formal causal graph','disposition':'PAPER_ONLY_CONCEPTUAL','action':'Add a minimal causal-audit diagram/assumption paragraph if useful, without claiming new SCM identification.'},
   {'id':'R14-S7','topic':'future stratum neutrality/sample size','disposition':'PAPER_ONLY_FUTURE_PREREGISTRATION','action':'Pre-register stratum units, margin, sample size/stopping before future outcomes; do not use adaptive outcome-driven expansion.'},
  ],
  'non_tie_diagnosis':diagnoses,'power_planning_ref':str(powerp.relative_to(ROOT)),'endpoint_residual_csv_ref':str(csvp.relative_to(ROOT)),
  'new_experiment_now':False,'new_model_calls':0,'new_provider_calls':0,'scientific_authority':False,'experiment_authority':False,'submission_authority':False
 }
 adjp=ROOT/'generated/temporal-skill-r14-stanford-adjudication-20260824.json';adjp.write_text(json.dumps(adjud,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'public_result':str(pubp.relative_to(ROOT)),'public_sha':sha(pubp),'adjudication':str(adjp.relative_to(ROOT)),'adjudication_sha':sha(adjp),'residual_csv':str(csvp.relative_to(ROOT)),'power':str(powerp.relative_to(ROOT)),'score':resp.get('numerical_score'),'verdict':'Accept','non_tie':[(x['endpoint_id'],x['mean_residual']) for x in diagnoses],'n27_power':planning['portfolio']['simulated_power_n27']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
