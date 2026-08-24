#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance/source-native-replay/D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK')
GEN=ROOT/'generated'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p:Path):return list(csv.DictReader(p.open(encoding='utf-8')))
def success(r):return r.get('family_success')=='True'
def combine_triplet(base:Path,repeat:Path):
    by={}
    for p in (base,repeat):
        for r in rows(p):by.setdefault(r['endpoint_id'],{}).setdefault(r['arm'],[]).append(1.0 if success(r) else 0.0)
    means={e:{a:sum(v)/len(v) for a,v in arms.items()} for e,arms in by.items()}
    rates={a:sum(x[a] for x in means.values())/len(means) for a in ('N_FRESH','B_GENERIC','T_FROZEN')}
    contrasts={e:{'T-N':x['T_FROZEN']-x['N_FRESH'],'B-N':x['B_GENERIC']-x['N_FRESH'],'T-B':x['T_FROZEN']-x['B_GENERIC']} for e,x in means.items()}
    cm={k:sum(x[k] for x in contrasts.values())/len(contrasts) for k in ('T-N','B-N','T-B')}
    signs={k:{'positive':sum(x[k]>0 for x in contrasts.values()),'tie':sum(x[k]==0 for x in contrasts.values()),'negative':sum(x[k]<0 for x in contrasts.values())} for k in ('T-N','B-N','T-B')}
    return {'endpoint_arm_means':means,'rates':rates,'contrast_means':cm,'contrast_signs':signs,'run_rows':sum(len(v) for x in by.values() for v in x.values())}
def plan_from_rows(single_files,planning_rows,extra_files):
    s={};p={}
    for f in single_files:
        for r in rows(f):
            if r.get('arm')=='N_FRESH':s.setdefault(r['endpoint_id'],[]).append(1.0 if success(r) else 0.0)
    for r in planning_rows:p.setdefault(r['endpoint_id'],[]).append(1.0 if success(r) else 0.0)
    for f in extra_files:
        for r in rows(f):p.setdefault(r['endpoint_id'],[]).append(1.0 if success(r) else 0.0)
    sm={e:sum(v)/len(v) for e,v in s.items()};pm={e:sum(p[e])/len(p[e]) for e in sm};d={e:pm[e]-sm[e] for e in sm}
    return {'single_endpoint_means':sm,'planning_endpoint_means':pm,'single_mean':sum(sm.values())/len(sm),'planning_mean':sum(pm.values())/len(pm),'mean_delta':sum(d.values())/len(d),'paired_delta':d,'signs':{'positive':sum(x>0 for x in d.values()),'tie':sum(x==0 for x in d.values()),'negative':sum(x<0 for x in d.values())}}
def main():
    hist=DATA/'20260824-extension-benign-generic-deepseek'
    eia=DATA/'20260824-extension-eia-future-nonceiling'
    bls=DATA/'20260824-extension-bls-cpi-crossdomain'
    mt=DATA/'20260824-extension-multiturn-tool-vs-context'
    fed=DATA/'20260824-extension-fed-fomc-planning-prospective'
    historical=[{'endpoint_id':r['endpoint_id'],'arm':r['arm'],'success':success(r)} for r in rows(hist/'results.csv')]
    eia_r=combine_triplet(eia/'results.csv',eia/'repeat-robustness-r1/results.csv')
    bls_r=combine_triplet(bls/'results.csv',bls/'repeat-robustness-r1/results.csv')
    mt_rows=rows(mt/'results.csv'); mt_by={}
    for r in mt_rows:mt_by.setdefault(r['endpoint_id'],{})[r['arm']]={'success':success(r),'tool_called':r.get('tool_called')=='True','tool_call_count':int(r.get('tool_call_count') or 0)}
    mt_summary={'success_rates':{a:sum(x[a]['success'] for x in mt_by.values())/len(mt_by) for a in ('BASE','CONTEXT','TOOL')},'tool_call_rate':sum(x['TOOL']['tool_called'] for x in mt_by.values())/len(mt_by),'tool_vs_context':{e:int(x['TOOL']['success'])-int(x['CONTEXT']['success']) for e,x in mt_by.items()},'endpoints':mt_by}
    base_mt=[r for r in mt_rows if r['arm']=='BASE']
    eia_plan=plan_from_rows([eia/'results.csv',eia/'repeat-robustness-r1/results.csv'],base_mt,[DATA/'20260824-extension-multiturn-base-repeat-r1/results.csv'])
    bls_plan=plan_from_rows([bls/'results.csv',bls/'repeat-robustness-r1/results.csv'],[],[DATA/'20260824-extension-bls-cpi-planning-base/results.csv',DATA/'20260824-extension-bls-cpi-planning-base-repeat-r1/results.csv'])
    fed_plan=plan_from_rows([fed/'results.csv'],[],[fed/'planning-base/results.csv'])
    artifact={
      'schema_version':'1.0','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','status':'EXTENSION_ADJUDICATED','current_canonical_revision':'R15','r15_automatic_mutation':False,
      'experiments':{
        'historical_benign_generic_pilot':{'status':'UNINFORMATIVE_ALL_TIES_NO_SCALE','calls':len(historical),'rows':historical},
        'fresh_eia_benign_generic':{**eia_r,'status':'APPENDIX_HIGH_VALUE','interpretation':'On four new EIA cutoff endpoints, T and the benign evidence organizer both reach 1.0 endpoint-mean success while N is 0.375. Net repair is real relative to N, but targeted-specific credit is fully absorbed by generic evidence organization on this substrate.'},
        'bls_cpi_crossdomain':{**bls_r,'status':'APPENDIX_HIGH_VALUE','interpretation':'Across four BLS CPI endpoints, T=1.0, benign organizer=0.75, N=0.375. Generic organization explains part, but not all, of the targeted residual; one endpoint has stable T>B=N across both repeats.'},
        'multiturn_callable_vs_context':{**mt_summary,'status':'APPENDIX_BOUNDARY_NULL','interpretation':'Actual function calling is supported and endogenous use occurs on 2/4 endpoints, but BASE=CONTEXT=TOOL=1.0 in the exploratory EIA fork. No callable-over-context residual is observed.'},
        'planning_exploratory_eia':{**eia_plan,'status':'EXPLORATORY_POSITIVE_NOT_CONFIRMATORY'},
        'planning_exploratory_bls':{**bls_plan,'status':'EXPLORATORY_POSITIVE_NOT_CONFIRMATORY'},
        'planning_prospective_fed':{**fed_plan,'status':'PROSPECTIVE_FALSIFIER_NO_EFFECT','interpretation':'The single-turn-vs-planning comparison and four Fed endpoints were frozen before any Fed model outcomes. Single-turn N and planning-only both average 0.25; paired changes are one planning-only win, one N-only win, and two ties. The proposed general planning effect does not survive prospective third-substrate testing.'}
      },
      'routing':{
        'current_paper_appendix':['fresh_eia_benign_generic','bls_cpi_crossdomain','multiturn_callable_vs_context'],
        'current_paper_main_claim_change':'NO; add follow-up robustness/claim-boundary evidence only. Preserve T-N as net repair and explicitly show that generic organization can absorb all or part of targeted credit.',
        'next_paper_candidate':{'object':'structured planning/deliberation absorbs apparent temporal-skill gains','decision':'STOP_FOR_NOW','why':'Exploratory EIA/BLS gains do not survive the prospectively frozen Fed FOMC falsifier.','reopen_condition':'A new prospectively frozen independent substrate must show a stable planning-over-single-turn residual under the same-information contract without selecting endpoints after outcomes.'},
        'multiturn_new_paper':'STOP_FOR_NOW_NO_CALLABLE_RESIDUAL'
      },
      'provenance':{
        'eia_source_manifest_sha256':sha(eia/'source_manifest_clean.json'),'eia_plan_sha256':sha(eia/'plan.json'),'bls_source_manifest_sha256':sha(bls/'source_manifest.json'),'bls_plan_sha256':sha(bls/'plan.json'),'multiturn_plan_sha256':sha(mt/'plan.json'),'fed_source_manifest_sha256':sha(fed/'source_manifest.json'),'fed_single_plan_sha256':sha(fed/'plan.json'),'fed_planning_plan_sha256':sha(fed/'planning-base/plan.json')
      },
      'provider':{'route':'Ark Plan /api/plan/v3','requested_model':'deepseek-v4-pro','required_resolved_model':'deepseek-v4-pro-260425'},'scientific_authority':False,'submission_authority':False
    }
    GEN.mkdir(exist_ok=True);out=GEN/'temporal-skill-extension-adjudication-20260824.json';out.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
    csvout=GEN/'temporal-skill-extension-endpoint-summary-20260824.csv'
    with csvout.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['dataset','endpoint_id','N_mean','B_mean','T_mean','T_minus_N','B_minus_N','T_minus_B'])
        for label,res in [('EIA',eia_r),('BLS',bls_r)]:
            for e,x in res['endpoint_arm_means'].items():w.writerow([label,e,x['N_FRESH'],x['B_GENERIC'],x['T_FROZEN'],x['T_FROZEN']-x['N_FRESH'],x['B_GENERIC']-x['N_FRESH'],x['T_FROZEN']-x['B_GENERIC']])
    print(json.dumps({'artifact':str(out),'artifact_sha256':sha(out),'csv':str(csvout),'csv_sha256':sha(csvout),'routing':artifact['routing']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
