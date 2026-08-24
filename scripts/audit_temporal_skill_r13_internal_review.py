#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, math, random
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance/source-native-replay/D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK')
A1=BASE/'20260824-g0-stage-a-deepseek-plan-r2/results.csv'; A2=BASE/'20260824-g0-a2-neutrality-deepseek/results.csv'; O5=BASE/'20260824-temp-o5-deepseek-t-vs-r/results.csv'
OUT=ROOT/'generated/temporal-skill-r13-internal-review-adjudication-20260824.json'; CSV=ROOT/'generated/temporal-skill-r13-internal-review-falsifiers-20260824.csv'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def b(x):return str(x).lower()=='true'
def pct(xs,p):
 xs=sorted(xs);z=(len(xs)-1)*p;lo=int(z);hi=min(lo+1,len(xs)-1);f=z-lo;return xs[lo]*(1-f)+xs[hi]*f
def boot(v,seed=20260824,n=50000):
 r=random.Random(seed);m=len(v);s=[sum(v[r.randrange(m)] for _ in range(m))/m for __ in range(n)];return [pct(s,.05),pct(s,.95)],[pct(s,.025),pct(s,.975)]
def sign(v):
 w=sum(x>0 for x in v);t=sum(x==0 for x in v);l=sum(x<0 for x in v);n=w+l
 p=sum(math.comb(n,j) for j in range(w,n+1))/(2**n) if n else 1.0
 return {'wins':w,'ties':t,'losses':l,'one_sided_p_positive':p}
def means(path):
 rows=list(csv.DictReader(open(path)));by=defaultdict(lambda:defaultdict(list));meta={}
 for r in rows:by[r['endpoint_id']][r['arm']].append(int(b(r['family_success'])));meta[r['endpoint_id']]={'phase':r['phase'],'family':r['failure_family']}
 return {e:{a:sum(v)/len(v) for a,v in x.items()} for e,x in by.items()},meta
m1,meta1=means(A1);m2,meta2=means(A2);mr,metar=means(O5)
strata=[('C3_grounding','C3-R','exogenous_grounding'),('C4_grounding','C4-R','exogenous_grounding'),('EIA_heldout_cutoff','C4-R4','temporal_cutoff')]
rows=[];stratum={}
for label,phase,fam in strata:
 ids=[e for e,x in meta1.items() if x['phase']==phase and x['family']==fam]
 item={'endpoint_count':len(ids),'endpoint_ids':ids,'A1':{},'A2_G0_minus_N':{}}
 for name,a,c in [('T_minus_N','T_FROZEN','N_FRESH'),('T_minus_G0','T_FROZEN','G0_NOOP'),('G0_minus_N','G0_NOOP','N_FRESH')]:
  v=[m1[e][a]-m1[e][c] for e in ids];c90,c95=boot(v);item['A1'][name]={'point':sum(v)/len(v),'bootstrap_90_ci':c90,'bootstrap_95_ci':c95,**sign(v),'endpoint_deltas':dict(zip(ids,v))}
 ids2=[e for e in ids if e in m2];v=[m2[e]['G0_NOOP']-m2[e]['N_FRESH'] for e in ids2];c90,c95=boot(v,20260825);item['A2_G0_minus_N']={'point':sum(v)/len(v),'bootstrap_90_ci':c90,'bootstrap_95_ci':c95,**sign(v),'equivalence_10pp':c90[0]>-.1 and c90[1]<.1,'endpoint_deltas':dict(zip(ids2,v))}
 stratum[label]=item
 for contrast,x in item['A1'].items():rows.append({'audit':'A1_exact_stratum','stratum':label,'contrast':contrast,'n':len(ids),'point':x['point'],'ci90_lo':x['bootstrap_90_ci'][0],'ci90_hi':x['bootstrap_90_ci'][1],'ci95_lo':x['bootstrap_95_ci'][0],'ci95_hi':x['bootstrap_95_ci'][1],'wins':x['wins'],'ties':x['ties'],'losses':x['losses']})
 x=item['A2_G0_minus_N'];rows.append({'audit':'A2_exact_stratum','stratum':label,'contrast':'G0_minus_N','n':len(ids2),'point':x['point'],'ci90_lo':x['bootstrap_90_ci'][0],'ci90_hi':x['bootstrap_90_ci'][1],'ci95_lo':x['bootstrap_95_ci'][0],'ci95_hi':x['bootstrap_95_ci'][1],'wins':x['wins'],'ties':x['ties'],'losses':x['losses']})
# T/R surface audit
surface={};all_ids=list(mr)
for label,ids in [('all_prefrozen',all_ids),('T_non_ceiling',[e for e in mr if mr[e]['T_CALLABLE']<1]),('C3_grounding',[e for e,x in metar.items() if x['phase']=='C3-R']),('C4_grounding',[e for e,x in metar.items() if x['phase']=='C4-R']),('EIA_heldout_cutoff',[e for e,x in metar.items() if x['phase']=='C4-R4'])]:
 v=[mr[e]['T_CALLABLE']-mr[e]['R_RETRIEVAL'] for e in ids];c90,c95=boot(v,20260826);x={'endpoint_count':len(ids),'T_mean':sum(mr[e]['T_CALLABLE'] for e in ids)/len(ids),'R_mean':sum(mr[e]['R_RETRIEVAL'] for e in ids)/len(ids),'T_minus_R':sum(v)/len(v),'bootstrap_90_ci':c90,'bootstrap_95_ci':c95,**sign(v),'endpoint_ids':ids,'endpoint_deltas':dict(zip(ids,v))};surface[label]=x;rows.append({'audit':'O5_surface','stratum':label,'contrast':'T_minus_R','n':len(ids),'point':x['T_minus_R'],'ci90_lo':c90[0],'ci90_hi':c90[1],'ci95_lo':c95[0],'ci95_hi':c95[1],'wins':x['wins'],'ties':x['ties'],'losses':x['losses']})
# R semantics/parity from raw formal results
raw=json.load(open(BASE/'20260824-temp-o5-deepseek-t-vs-r/results.json'))['rows'];rr=[r for r in raw if r['arm']=='R_RETRIEVAL']
parity={'R_rows':len(rr),'candidate_evidence_preserved':sum((r.get('retrieval_parity') or {}).get('candidate_evidence_preserved') is True for r in rr),'operation_output_content_equal':sum((r.get('retrieval_parity') or {}).get('operation_output_content_equal') is True for r in rr),'only_added_field':sum((r.get('retrieval_parity') or {}).get('only_added_field') is True for r in rr),'interpretation':'R is a controlled integration-surface/context-materialization intervention using the exact frozen operation output. It is intentionally not an independently learned or heuristic temporal retriever and must not support a broad temporal-retrieval equivalence claim.'}
# EIA design audit
r4=BASE/'20260822-r4-postreview-eia'; eia={'source_manifest_sha256':sha(r4/'source_manifest.json'),'endpoints_sha256':sha(r4/'endpoints.json'),'execution_plan_sha256':sha(r4/'execution_plan.json'),'harness_sha256':sha(r4/'harness.py'),'scorer_sha256':sha(r4/'scorer.py'),'selection':'16 fixed EIA weekly releases; targets are deterministic source indices 3..14; phase is release-date split before 2026-04-01 vs >=2026-04-01; 12 endpoints and the condition order were frozen before R4 model outcomes.','boundary':'The EIA institution/domain was selected post-review because its recurring dated releases are structurally compatible with the cutoff mechanism. Therefore it is a compatibility-selected validation, not an independently sampled cross-domain generalization test.'}
adjudication={
 'G0_stratum_neutrality':{'verdict':'PAPER_ONLY_REFRAME','reason':'Pooled A2 G0 equivalence does not imply +/-10pp equivalence within all load-bearing strata. Remove stratum-level behavior-neutral language. Treat G0 as a same-surface no-operation placebo. Net repair is T-N; within-surface operation contribution is T-G0. G0-N remains a perturbation diagnostic, not a causal admission gate.'},
 'A1_A2_sequential_selection':{'verdict':'RESOLVED_BY_IDENTIFICATION_REFRAME','reason':'R14 no longer conditions T-G0 admissibility on A2 equivalence. A1 and A2 remain unpooled robustness studies; their only role is to characterize wrapper/no-op perturbation.'},
 'R_ceiling_attack':{'verdict':'RESOLVED_EXISTING_ANALYSIS_WITH_BOUNDARY','reason':'Parity is not confined to ceiling: C3 grounding has T=R=0.60 across five endpoints and C4 grounding T=R=0.70 across five. The T<1 non-ceiling subset has mean T-R=0 but only four endpoints and wide CI; report this low-resolution boundary.'},
 'R_is_independent_temporal_retriever':{'verdict':'VALID_CRITIQUE_PAPER_ONLY_REFRAME','reason':'R intentionally reuses the exact operation output to isolate integration surface. Rename it context-materialization/surface control; delete any wording that implies an independent temporal-RAG algorithm or broad retrieval equivalence. A new independent retriever is required only for such a broader claim, which R14 will not make.'},
 'T_R_material_advantage':{'verdict':'SUPPORTED_AT_PREFROZEN_PORTFOLIO_MARGIN','reason':'Across 18 pre-frozen endpoints T-R=0; 90% CI [-5.56,+5.56] and post-hoc 95% sensitivity CI [-8.33,+8.33], both within the predeclared +/-10pp material margin. Scope is the forced one-answer integration surface, not persistent multi-turn container value in general.'},
 'EIA_postreview_selection':{'verdict':'PERMANENT_BOUNDARY','reason':'Endpoint construction/order were outcome-independent and frozen, but EIA was chosen post-review for cutoff-compatible release structure. Keep it as compatibility-selected held-out validation; do not use it for generic cross-domain transfer.'},
 'need_new_experiment_now':{'verdict':'NO_FOR_R14_NARROW_CLAIM','reason':'Existing data can support the narrower operation-repair and integration-surface claims after the above reframe. New independent temporal retriever or new domain would be required only to broaden claims, not to retain the bounded R14 thesis.'}
}
out={'schema_version':'1.0','receipt_type':'temporal-r13-internal-review-existing-evidence-adjudication','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','source_review_kind':'INTERNAL_ICLR_PANEL_ZERO_AUTHORITY','source_review_dir':'generated/temporal-skill-r13-internal-review-20260824','data_bindings':{'A1_csv_sha256':sha(A1),'A2_csv_sha256':sha(A2),'O5_csv_sha256':sha(O5)},'exact_stratum_audit':stratum,'surface_control_audit':surface,'surface_control_semantics':parity,'EIA_design_audit':eia,'adjudication':adjudication,'new_model_calls':0,'new_provider_calls':0,'scientific_authority':False,'submission_authority':False}
out['receipt_sha256']=hashlib.sha256(json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
CSV.parent.mkdir(parents=True,exist_ok=True);cols=['audit','stratum','contrast','n','point','ci90_lo','ci90_hi','ci95_lo','ci95_hi','wins','ties','losses'];f=open(CSV,'w',newline='');w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows);f.close();print(json.dumps({'receipt':str(OUT.relative_to(ROOT)),'receipt_sha256':out['receipt_sha256'],'csv':str(CSV.relative_to(ROOT)),'csv_sha256':sha(CSV),'new_model_calls':0},indent=2))
