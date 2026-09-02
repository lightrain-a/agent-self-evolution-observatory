#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, itertools, json, math, statistics, subprocess
from pathlib import Path
from typing import Any

PROCEDURAL=("aggregation_join","formula_materialization","multi_step_pipeline")
BINDING=("input_output_contract","schema_key_alignment","target_sheet_range")
FAMILY_CODE={"aggregation_join":"agj","formula_materialization":"fmv","input_output_contract":"ioc","multi_step_pipeline":"msp","schema_key_alignment":"ska","target_sheet_range":"tsr"}


def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def req(c:bool,m:str)->None:
    if not c: raise RuntimeError(m)
def rankdata(xs:list[float])->list[float]:
    order=sorted(range(len(xs)),key=lambda i:xs[i]); out=[0.0]*len(xs); j=0
    while j<len(order):
        k=j+1
        while k<len(order) and xs[order[k]]==xs[order[j]]: k+=1
        r=(j+1+k)/2.0
        for q in range(j,k): out[order[q]]=r
        j=k
    return out
def corr(a:list[float],b:list[float])->float:
    ma=statistics.fmean(a); mb=statistics.fmean(b)
    da=[x-ma for x in a]; db=[x-mb for x in b]
    den=math.sqrt(sum(x*x for x in da)*sum(x*x for x in db))
    return sum(x*y for x,y in zip(da,db))/den if den else 0.0
def spearman(a:list[float],b:list[float])->float: return corr(rankdata(a),rankdata(b))

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--e2-root',type=Path,required=True); a=ap.parse_args()
    root=Path.cwd()
    analysis_path=root/'generated/e2-r17-deepseek-v2-repair2-continuation-v2-analysis-20260902.json'
    closeout_path=root/'generated/e2-r17-deepseek-v2-final-scientific-closeout-20260902.json'
    support_path=root/'generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json'
    split_path=Path('/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/r17_split_manifest.json')
    ph_root=Path('/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-ph-v2')
    ph_split=ph_root/'r17_prospective_split_manifest.json'; ph_meta=ph_root/'r17_controlled_metadata.json'; ph_manifest=ph_root/'suite_manifest.json'
    qwen_close=root/'generated/e2-r17-qwen25-32b-q4-local-route-closeout-20260902.json'
    for p in [analysis_path,closeout_path,support_path,split_path,ph_split,ph_meta,ph_manifest,qwen_close]: req(p.is_file(),f'missing {p}')
    req(sha(ph_manifest)=='2e04956e72dbc56fe029fa99eded91953c9775f10a3425f10a085d7d52497868','ph suite drift')
    req(sha(ph_split)=='bbc24277c717f7499d9f9e30ccb254ad98229bcd61bd17e484310a8397fb2d46','ph split drift')
    req(sha(ph_meta)=='40cb56082903ed5ad2fb7ed6cf55b813c8fb80f3ec43e8535cb02af2d0953853','ph metadata drift')
    analysis=json.loads(analysis_path.read_text()); req(analysis['status']=='HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS','closed status drift')
    closeout=json.loads(closeout_path.read_text()); req(closeout['status']=='HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS','closeout status drift')
    support=json.loads(support_path.read_text()); split=json.loads(split_path.read_text()); phs=json.loads(ph_split.read_text()); meta={x['id']:x for x in json.loads(ph_meta.read_text())}
    stream_effect={x['stream_id']:(0.0 if abs(float(x['mean_difference_mrw_minus_win_c']))<1e-12 else float(x['mean_difference_mrw_minus_win_c'])) for x in analysis['per_stream']}
    family_effect={}
    for fam,code in FAMILY_CODE.items():
        vals=[stream_effect[f'e1-{code}-00'],stream_effect[f'e1-{code}-01']]; family_effect[fam]=statistics.fmean(vals)
    proc=[family_effect[x] for x in PROCEDURAL]; bind=[family_effect[x] for x in BINDING]
    observed=statistics.fmean(proc)-statistics.fmean(bind)
    allvals=proc+bind; perm=[]
    for idx in itertools.combinations(range(6),3):
        s=set(idx); p=[allvals[i] for i in range(6) if i in s]; b=[allvals[i] for i in range(6) if i not in s]; perm.append(statistics.fmean(p)-statistics.fmean(b))
    p_perm=sum(v>=observed-1e-15 for v in perm)/len(perm)
    req(abs(p_perm-.05)<1e-12,'CAL separation no longer 1/20')
    mixed=support['primary_support']['per_stream_mixed_recomputed']
    loo_pred=[]; loo_true=[]; direction=0
    for fam,code in FAMILY_CODE.items():
        s0=f'e1-{code}-00'; s1=f'e1-{code}-01'
        for target,sibling in [(s0,s1),(s1,s0)]:
            mt=float(mixed[target])/8.0; ms=float(mixed[sibling])/8.0; pred=mt*(stream_effect[sibling]/ms if ms else 0.0); true=stream_effect[target]
            loo_pred.append(pred); loo_true.append(true); direction += int((pred>0)==(true>0) if pred!=0 and true!=0 else pred==true)
    loo_rho=spearman(loo_pred,loo_true)
    e3={str(k):list(map(str,v)) for k,v in split['e3_future_streams'].items()}; req(len(e3)==12,'e3 stream count')
    e3_ids=[x for v in e3.values() for x in v]; req(len(e3_ids)==96 and len(set(e3_ids))==96,'e3 task uniqueness'); req(all('-b5-' in x or '-b6-' in x for x in e3_ids),'e3 blocks drift')
    runs=a.e2_root/'runs'; rg=subprocess.run(['rg','-l','r17-b[56]-',str(runs)],capture_output=True,text=True); refs=[] if rg.returncode==1 else [x for x in rg.stdout.splitlines() if x.strip()]
    req(rg.returncode in (0,1),'rg scan failed'); req(len(refs)==0,f'b5/b6 already referenced in runs: {len(refs)}')
    trajectory_refs=[p for p in a.e2_root.rglob('r17_trajectory_ref.json') if 'r17-b5-' in str(p) or 'r17-b6-' in str(p)]; req(not trajectory_refs,'b5/b6 trajectory refs exist')
    held=list(map(str,phs['common_heldout_probe'])); req(len(held)==18 and len(set(held))==18,'heldout count'); req(set(held).isdisjoint(e3_ids),'heldout/update overlap')
    req(all(int(meta[x]['block'])==13 for x in held),'heldout not b13')
    htraj=[p for p in a.e2_root.rglob('r17_trajectory_ref.json') if any(x in str(p) for x in held)]; req(not htraj,'b13 heldout already executed')
    fam_counts={f:sum(meta[x]['primary_failure_family']==f for x in held) for f in FAMILY_CODE}; req(all(v==3 for v in fam_counts.values()),'heldout family balance')
    payload={
      'schema_version':'1.0','artifact_type':'e2-r17-selective-mrw-v3-static-audit','status':'PASS_SELECTIVE_MRW_V3_ZERO_PROVIDER_STATIC_AUDIT','provider_calls':0,'scientific_execution':False,'new_test_outcomes_accessed':False,
      'closed_calibration':{'analysis_path':str(analysis_path),'analysis_sha256':sha(analysis_path),'status':analysis['status'],'family_effects':family_effect,'procedural_mean':statistics.fmean(proc),'binding_mean':statistics.fmean(bind),'contrast':observed,'exact_3v3_permutation_p_calibration_only':p_perm,'sibling_loo_spearman':loo_rho,'sibling_loo_direction_agreement':f'{direction}/12','role':'calibration_only_no_confirmatory_reuse'},
      'taxonomy':{'procedural_transformation':list(PROCEDURAL),'instance_binding_localization':list(BINDING),'frozen_before_e3_execution':True},
      'sealed_e3_test':{'streams':e3,'stream_count':12,'update_task_count':96,'historical_run_files_referencing_b5_b6':0,'historical_b5_b6_trajectory_refs':0,'untouched_pass':True},
      'new_heldout':{'suite_manifest_sha256':sha(ph_manifest),'split_manifest_sha256':sha(ph_split),'metadata_sha256':sha(ph_meta),'task_ids':held,'task_count':18,'per_family_count':fam_counts,'historical_trajectory_refs':0,'untouched_pass':True},
      'cost_shape':{'stage_a_k8_pools':96,'stage_a_actor_rollouts':768,'stage_b_replicates_per_stream':8,'stage_b_paired_units':96,'stage_b_learned_states':192,'stage_b_heldout_evaluations':3456,'selective_mrw_extra_updater_calls':0,'selective_mrw_extra_heldout_evaluations':0},
      'qwen_route':{'closeout_path':str(qwen_close),'closeout_sha256':sha(qwen_close),'status':json.loads(qwen_close.read_text())['status']},
      'authority':{'stage_a_provider_execution':False,'stage_b_learning_execution':False,'analyzer':False,'second_backbone':False,'paper_promotion':False,'next':'CURRENT_DEEPSEEK_IDENTITY_QUALIFICATION_AND_ZERO_PROVIDER_STAGE_A_PREFLIGHT'}
    }
    req(not a.output.exists(),'audit output exists'); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':payload['status'],'calibration':payload['closed_calibration'],'sealed_e3':{'streams':12,'tasks':96,'refs':0},'heldout':{'tasks':18,'refs':0},'cost_shape':payload['cost_shape']},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
