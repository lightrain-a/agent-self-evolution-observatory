from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

def _rows(path:Path)->list[dict[str,Any]]:
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def load_shared(root:Path)->dict[str,list[dict[str,Any]]]:
    out={k:[] for k in ('candidates','labels','future','modes')}
    for shard in sorted(root.glob('shard-*')):
        out['candidates']+=_rows(shard/'correction-candidates.jsonl')
        out['labels']+=_rows(shard/'self-labels.jsonl')
        out['future']+=_rows(shard/'future-runs.jsonl')
        for extra in sorted(shard.glob('future-extra-part-*.jsonl')):
            out['future']+=_rows(extra)
        out['modes']+=_rows(shard/'mode-runs.jsonl')
    out['future']+=_rows(root/'c1-future-runs.jsonl')
    return out

def candidate_effects(data:dict[str,list[dict[str,Any]]])->dict[str,dict[str,Any]]:
    by={c['candidate_id']:{**c,'probe_delta':[],'hidden_delta':[]} for c in data['candidates']}
    for row in data['future']:
        cid=row.get('candidate_id')
        if cid not in by: continue
        role=row.get('role'); delta=int((row.get('trace') or {}).get('success',0))-int(row.get('baseline_success',0))
        if role=='candidate-probe': by[cid]['probe_delta'].append(delta)
        elif role=='candidate-hidden': by[cid]['hidden_delta'].append(delta)
    for c in by.values():
        c['probe_sum']=sum(c['probe_delta']); c['probe_mean']=float(np.mean(c['probe_delta'])) if c['probe_delta'] else 0.0
        c['probe_harm']=sum(x<0 for x in c['probe_delta']); c['hidden_sum']=sum(c['hidden_delta']); c['hidden_mean']=float(np.mean(c['hidden_delta'])) if c['hidden_delta'] else 0.0
        c['future_truth']='benefit' if c['hidden_sum']>0 else ('harm' if c['hidden_sum']<0 else 'neutral')
    return by

def candidate_effects_reanchored(data:dict[str,list[dict[str,Any]]],baseline_success_by_task:dict[str,int])->dict[str,dict[str,Any]]:
    by={c['candidate_id']:{**c,'probe_delta':[],'hidden_delta':[]} for c in data['candidates']}
    covered=0
    for row in data['future']:
        cid=row.get('candidate_id')
        if cid not in by: continue
        role=row.get('role')
        if role not in {'candidate-probe','candidate-hidden'} or row.get('truth_completion')=='C-1': continue
        task=str(row.get('task') or '')
        if task not in baseline_success_by_task: continue
        covered+=1
        delta=int((row.get('trace') or {}).get('success',0))-int(baseline_success_by_task[task])
        if role=='candidate-probe': by[cid]['probe_delta'].append(delta)
        else: by[cid]['hidden_delta'].append(delta)
    for c in by.values():
        c['probe_sum']=sum(c['probe_delta']); c['probe_mean']=float(np.mean(c['probe_delta'])) if c['probe_delta'] else 0.0
        c['probe_harm']=sum(x<0 for x in c['probe_delta']); c['hidden_sum']=sum(c['hidden_delta']); c['hidden_mean']=float(np.mean(c['hidden_delta'])) if c['hidden_delta'] else 0.0
        c['future_truth']='benefit' if c['hidden_sum']>0 else ('harm' if c['hidden_sum']<0 else 'neutral')
    by['_reanchor_meta']={'covered_candidate_rows':covered,'baseline_tasks':len(baseline_success_by_task)}
    return by

def _label_confidence(row:dict[str,Any])->float:
    import re
    raw=str(row.get('raw') or '')
    m=re.search(r'\[(0(?:\.\d+)?|1(?:\.0+)?)\]',raw)
    if m: return float(m.group(1))
    return float(row.get('confidence',0.5))

def analyze_c1(data:dict[str,list[dict[str,Any]]],effects:dict[str,dict[str,Any]])->dict[str,Any]:
    labels=[r for r in data['labels'] if r.get('candidate_id') in effects and effects[r['candidate_id']].get('hidden_delta')]
    truth={cid:('ACCEPT' if c['hidden_sum']>0 else 'QUARANTINE') for cid,c in effects.items() if c.get('hidden_delta')}
    lineages=defaultdict(list)
    for r in labels: lineages[r['lineage_id']].append(r)
    wrong_desc=[]; correct_desc=[]
    for rows in lineages.values():
        rows=sorted(rows,key=lambda r:r['round']); root=rows[0]; t=truth.get(root['candidate_id'])
        if not t: continue
        errs=[int(r['decision']!=t) for r in rows[1:]]
        (wrong_desc if root['decision']!=t else correct_desc).extend(errs)
    wrong_rate=float(np.mean(wrong_desc)) if wrong_desc else None; correct_rate=float(np.mean(correct_desc)) if correct_desc else None
    decisions={}
    for cid in truth:
        rs=[r for r in labels if r['candidate_id']==cid]
        if not rs: continue
        direct=np.mean([(1 if r['decision']=='ACCEPT' else 0)*_label_confidence(r) for r in rs])
        root_votes=[]
        for root in (0,1):
            rr=[r for r in rs if int(r['root'])==root]
            accept_weight=sum(_label_confidence(r) for r in rr if r['decision']=='ACCEPT')
            total_weight=sum(_label_confidence(r) for r in rr) or 1.0
            root_votes.append(int(accept_weight/total_weight>=0.5))
        # One ancestry/root contributes at most one effective vote.  This is
        # intentionally not the mean-of-root-means statistic: with equal
        # lineage lengths that statistic is algebraically identical to the
        # naive all-descendants average and can never establish disagreement.
        lineage_collapsed=bool(sum(root_votes)==len(root_votes))
        decisions[cid]={'direct':direct>=0.5,'decorrelated':lineage_collapsed}
    disagreement=float(np.mean([v['direct']!=v['decorrelated'] for v in decisions.values()])) if decisions else 0.0
    truth_counts={k:sum(v==k for v in truth.values()) for k in ('ACCEPT','QUARANTINE')}
    enrichment=(wrong_rate-correct_rate) if wrong_rate is not None and correct_rate is not None else None
    enough=len(labels)>=200 and min(truth_counts.values())>0
    signal=bool(enough and enrichment is not None and enrichment>=0.15 and disagreement>=0.20)
    decision='F0_LINEAGE_SIGNAL_CONTINUE' if signal else ('HOLD_C1_TARGET_OR_LINEAGE_SUPPORT_INSUFFICIENT' if not enough else 'STOP_SIMPLE_LINEAGE_WEIGHTING_NO_HEADROOM')
    hidden_evals=sum(len(effects[cid].get('hidden_delta') or []) for cid in truth)
    return {'idea_id':'self-label-confidence-flow','code':'C-1','decision':decision,'labels_with_future_truth':len(labels),'candidates_with_future_truth':len(truth),'hidden_candidate_task_evaluations':hidden_evals,'truth_counts':truth_counts,'wrong_root_descendant_error_rate':wrong_rate,'correct_root_descendant_error_rate':correct_rate,'lineage_error_enrichment':enrichment,'decorrelated_vs_direct_decision_disagreement':disagreement,'decision_statistic':'one discrete confidence-majority vote per ancestry/root; both independent roots required for ACCEPT','decision_statistic_repair':'frozen before final hidden truth completion because equal-length mean-of-root-means is algebraically identical to naive descendant averaging','f0_signal_continue':signal}

def _loo_mode_predictions(rows:list[dict[str,Any]])->tuple[list[str],list[str],list[str]]:
    truth=[]; logistic=[]; tree=[]
    df=pd.DataFrame(rows); families=sorted(df.task_family.unique())
    for family in families:
        train=df[df.task_family!=family]; test=df[df.task_family==family]
        if train.empty or test.empty: continue
        y=train.target_mode.astype(str)
        if y.nunique()==1:
            lp=[y.iloc[0]]*len(test); tp=list(lp)
        else:
            prep=ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore'),['task_family']),('num',StandardScaler(),['source_steps','source_invalid_rate','patch_words'])])
            lpipe=Pipeline([('prep',prep),('clf',LogisticRegression(max_iter=500,multi_class='auto',random_state=0))])
            tpipe=Pipeline([('prep',prep),('clf',DecisionTreeClassifier(max_depth=3,min_samples_leaf=2,random_state=0))])
            lpipe.fit(train[['task_family','source_steps','source_invalid_rate','patch_words']],y); tpipe.fit(train[['task_family','source_steps','source_invalid_rate','patch_words']],y)
            lp=list(lpipe.predict(test[['task_family','source_steps','source_invalid_rate','patch_words']])); tp=list(tpipe.predict(test[['task_family','source_steps','source_invalid_rate','patch_words']]))
        truth+=list(test.target_mode.astype(str)); logistic+=lp; tree+=tp
    return truth,logistic,tree

def analyze_c4(data:dict[str,list[dict[str,Any]]],effects:dict[str,dict[str,Any]])->dict[str,Any]:
    mode_out={}
    for r in data['modes']:
        cid=r.get('candidate_id'); mode=r.get('mode')
        if mode not in {'rewrite','replan','retrieve'}: continue
        tr=r.get('trace') or {}; mode_out.setdefault(cid,{})[mode]=(int(tr.get('success',0)),int(tr.get('steps',999)))
    rows=[]; order_pairs=0; order_diff=0
    for cid,c in effects.items():
        opts=mode_out.get(cid,{})
        successful=[(mode,val[1]) for mode,val in opts.items() if val[0]>0]
        target=min(successful,key=lambda x:(x[1],x[0]))[0] if successful else 'stop'
        rows.append({'candidate_id':cid,'task_family':c.get('task_family','unknown'),'source_steps':int(c.get('source_steps',0)),'source_invalid_rate':float(c.get('source_invalid_rate',0.0)),'patch_words':int(c.get('patch_words',0)),'target_mode':target})
        a=c.get('rewrite_replan_success'); b=c.get('replan_rewrite_success')
        if a is not None and b is not None:
            order_pairs+=1; order_diff+=int(a!=b)
    truth,logit,tree=_loo_mode_predictions(rows)
    lacc=accuracy_score(truth,logit) if truth else 0.0; tacc=accuracy_score(truth,tree) if truth else 0.0
    disagreement=float(np.mean([a!=b for a,b in zip(logit,tree)])) if truth else 0.0
    mode_counts={m:sum(r['target_mode']==m for r in rows) for m in sorted({r['target_mode'] for r in rows})}
    variation=len([v for v in mode_counts.values() if v>0])>=2
    order_rate=order_diff/max(1,order_pairs)
    signal=bool(len(rows)>=30 and variation and order_rate>=0.15 and disagreement>=0.20 and lacc>tacc+0.05)
    if len(rows)<30 or not variation: decision='HOLD_C4_MODE_TARGET_SUPPORT_INSUFFICIENT'
    elif order_rate<0.15: decision='STOP_C4_NO_NONTRIVIAL_ORDER_EFFECT'
    elif not signal: decision='STOP_C4_SHALLOW_RULE_NO_HEADROOM'
    else: decision='F0_C4_TRANSITION_SIGNAL_CONTINUE'
    return {'idea_id':'self-correction-collapse-detector','code':'C-4','decision':decision,'failures':len(rows),'target_mode_counts':mode_counts,'order_pairs':order_pairs,'order_effect_pairs':order_diff,'order_effect_rate':order_rate,'loo_logistic_accuracy':lacc,'loo_depth3_cart_accuracy':tacc,'logistic_cart_disagreement':disagreement,'f0_signal_continue':signal}

def _loo_binary(rows:list[dict[str,Any]])->tuple[list[str],list[int],list[int]]:
    ids=[]; truth=[]; pred=[]; df=pd.DataFrame(rows)
    for family in sorted(df.task_family.unique()):
        train=df[df.task_family!=family]; test=df[df.task_family==family]
        if train.empty or test.empty: continue
        y=train.truth_accept.astype(int)
        if y.nunique()==1:
            pp=[int(y.iloc[0])]*len(test)
        else:
            prep=ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore'),['task_family']),('num',StandardScaler(),['source_gain','probe_mean','probe_harm','patch_words'])])
            pipe=Pipeline([('prep',prep),('clf',LogisticRegression(max_iter=500,class_weight='balanced',random_state=0))])
            pipe.fit(train[['task_family','source_gain','probe_mean','probe_harm','patch_words']],y)
            pp=list(pipe.predict(test[['task_family','source_gain','probe_mean','probe_harm','patch_words']]).astype(int))
        ids+=list(test.candidate_id.astype(str)); truth+=list(test.truth_accept.astype(int)); pred+=pp
    return ids,truth,pred

def analyze_c5(data:dict[str,list[dict[str,Any]]],effects:dict[str,dict[str,Any]])->dict[str,Any]:
    rows=[]
    for cid,c in effects.items():
        if not c.get('hidden_delta') or len(c.get('probe_delta') or [])<8: continue
        rows.append({'candidate_id':cid,'task_family':c.get('task_family','unknown'),'source_gain':int(c.get('rewrite_success',0)),'probe_mean':float(c.get('probe_mean',0.0)),'probe_harm':int(c.get('probe_harm',0)),'patch_words':int(c.get('patch_words',0)),'truth_accept':int(c.get('hidden_sum',0)>0)})
    ids,truth,learned=_loo_binary(rows)
    learned_acc=accuracy_score(truth,learned) if truth else 0.0
    simple_by={r['candidate_id']:int(r['source_gain']>0 and r['probe_harm']==0 and r['probe_mean']>=0) for r in rows}
    truth_by={r['candidate_id']:r['truth_accept'] for r in rows}
    simple=[simple_by[i] for i in ids]; simple_truth=[truth_by[i] for i in ids]
    simple_acc=accuracy_score(simple_truth,simple) if simple else 0.0
    disagreement=float(np.mean([a!=b for a,b in zip(learned,simple)])) if simple else 0.0
    positives=sum(r['truth_accept'] for r in rows); negatives=len(rows)-positives; variation=positives>0 and negatives>0
    signal=bool(len(rows)>=24 and variation and disagreement>=0.20 and learned_acc>simple_acc+0.05)
    if len(rows)<24 or not variation: decision='HOLD_C5_FUTURE_UTILITY_SUPPORT_INSUFFICIENT'
    elif not signal: decision='STOP_C5_A3_SIMPLE_THRESHOLD_NO_HEADROOM'
    else: decision='F0_C5_INTERVENTION_SIGNAL_CONTINUE'
    return {'idea_id':'intervention-validated-self-correction','code':'C-5','decision':decision,'candidates':len(rows),'future_accept':positives,'future_quarantine':negatives,'loo_intervention_logistic_accuracy':learned_acc,'a3_simple_threshold_accuracy':simple_acc,'learned_simple_decision_disagreement':disagreement,'f0_signal_continue':signal}

def analyze_shared(root:Path)->dict[str,Any]:
    data=load_shared(root); effects=candidate_effects(data)
    complete=[]
    for shard in sorted(root.glob('shard-*')):
        p=shard/'complete.json'
        if p.exists(): complete.append(json.loads(p.read_text(encoding='utf-8')))
    c4_frozen=root/'c4-f0-at-30.json'
    try: c4=json.loads(c4_frozen.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError): c4=analyze_c4(data,effects)
    c1_data={**data,'future':[row for row in data['future'] if row.get('truth_completion')=='C-1']}
    c1_effects=candidate_effects(c1_data)
    c1=analyze_c1(c1_data,c1_effects)
    c1_contract=(c1.get('candidates_with_future_truth')==40 and c1.get('hidden_candidate_task_evaluations')==80)
    c1['truth_contract_pass']=bool(c1_contract)
    c1['truth_contract_expected']={'candidates':40,'hidden_pairs':80,'hidden_per_candidate':2}
    if not c1_contract:
        c1['decision']='HOLD_C1_TRUTH_CONTRACT_INCOMPLETE'; c1['f0_signal_continue']=False
    portability_path=root/'runtime-portability-audit.json'
    reanchor_path=root/'runtime-reanchor-60.json'
    try: portability=json.loads(portability_path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError): portability={}
    try: reanchor=json.loads(reanchor_path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError): reanchor={}
    if reanchor.get('decision')=='RUNTIME_REANCHOR_COMPLETE' and int(reanchor.get('tasks') or 0)==32:
        c5_effects=candidate_effects_reanchored(data,{str(k):int(v) for k,v in (reanchor.get('baseline_success_by_task') or {}).items()})
        reanchor_meta=c5_effects.pop('_reanchor_meta',{})
        c5=analyze_c5(data,c5_effects)
        c5['runtime_reanchor']={**{k:v for k,v in reanchor.items() if k!='baseline_success_by_task'},**reanchor_meta}
        c5['runtime_portability']=portability
        if reanchor_meta.get('covered_candidate_rows')!=288:
            c5['pre_reanchor_decision']=c5.get('decision')
            c5['decision']='HOLD_C5_RUNTIME_REANCHOR_INCOMPLETE'; c5['f0_signal_continue']=False
    else:
        c5=analyze_c5(data,effects)
        c5['runtime_portability']=portability
        if portability.get('decision')!='PORTABILITY_PASS':
            c5['pre_portability_decision']=c5.get('decision')
            c5['decision']='HOLD_C5_RUNTIME_PORTABILITY_PENDING' if not portability else 'HOLD_C5_RUNTIME_REANCHOR_REQUIRED'
            c5['f0_signal_continue']=False
    out={'schema_version':'1.0','scientific_role':'shared upstream substrate qualification only; no automatic METHOD-PASS/FAIL','shards_complete':len(complete),'candidates_total':len(data['candidates']),'self_label_decisions':len(data['labels']),'C-1':c1,'C-4':c4,'C-5':c5}
    (root/'analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); return out

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); a=p.parse_args()
    print(json.dumps(analyze_shared(a.root),ensure_ascii=False,indent=2))
