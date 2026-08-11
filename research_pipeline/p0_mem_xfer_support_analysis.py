from __future__ import annotations
import argparse,csv,hashlib,json,re
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ID='P0-MEM-XFER-SUPPORT-ENRICHED'
PLAN_HASH='47dbaebf7c0f26079ccc0d6116e8e66305331ba64a40e793e6abd8726daffc6b'

def _now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _json(p:Path): return json.loads(p.read_text(encoding='utf-8'))
def _sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def _mean(xs): return sum(xs)/len(xs) if xs else 0.0
def _sign(x): return 1 if x>1e-12 else (-1 if x < -1e-12 else 0)

def _select_completed_full_dir(run:Path)->Path:
    # The first authoritative 216-execution stream used the historical
    # ``full-support-table`` stage name. A later same-plan duplicate used
    # ``full-qwen-support-table`` and was explicitly stopped at 117/216.
    # Select by terminal evidence, never by directory name alone.
    candidates=(run/'full-support-table',run/'full-qwen-support-table')
    complete=[]
    for full in candidates:
        required=(full/'progress.json',full/'decision.json',full/'manifest.json',full/'main_table.csv',full/'raw-traces.jsonl')
        if not all(p.exists() for p in required):
            continue
        prog=_json(full/'progress.json'); dec=_json(full/'decision.json')
        executions=int(prog.get('completed_executions') or prog.get('completed_episodes') or 0)
        units=int(prog.get('completed_units') or 0)
        if dec.get('decision')=='FULL_SUPPORT_TABLE_COLLECTED' and executions==216 and units==72:
            complete.append(full)
    if len(complete)!=1:
        raise RuntimeError(f'expected exactly one completed frozen full-support table, got {[str(p) for p in complete]}')
    return complete[0]

def _rows(run:Path):
    plan=_json(run/'plan.json'); full=_select_completed_full_dir(run)
    prog=_json(full/'progress.json'); dec=_json(full/'decision.json'); man=_json(full/'manifest.json')
    if plan.get('plan_hash')!=PLAN_HASH or man.get('plan_hash')!=PLAN_HASH: raise RuntimeError('frozen plan hash mismatch')
    if dec.get('decision')!='FULL_SUPPORT_TABLE_COLLECTED': raise RuntimeError('full support table incomplete')
    executions=int(prog.get('completed_executions') or prog.get('completed_episodes') or 0)
    if executions!=216 or int(prog.get('completed_units',0))!=72: raise RuntimeError('full support progress integrity failed')
    rows=[]
    with (full/'main_table.csv').open(encoding='utf-8',newline='') as h:
        for r in csv.DictReader(h):
            for k in ('candidate_index','retrieved_success','no_memory_success','placebo_success','retrieved_delta','placebo_delta','controlled_delta'): r[k]=int(r[k])
            rows.append(r)
    if len(rows)!=72 or len({r['unit_id'] for r in rows})!=72: raise RuntimeError('expected 72 unique units')
    frozen={x['unit_id']:x for x in plan['units']}
    if set(frozen)!={r['unit_id'] for r in rows}: raise RuntimeError('table/plan unit mismatch')
    for r in rows:
        f=frozen[r['unit_id']]; r['relation']=f['relation']
        for k in ('memory_id','source_family','target_family','candidate_role','evaluation_role'):
            if str(r[k])!=str(f[k]): raise RuntimeError(f'frozen metadata mismatch:{r["unit_id"]}:{k}')
    ev={'plan_hash':PLAN_HASH,'full_table_dir':str(full),'full_table_stage':man.get('stage'),'progress_sha256':_sha(full/'progress.json'),'decision_sha256':_sha(full/'decision.json'),'main_table_sha256':_sha(full/'main_table.csv'),'raw_sha256':_sha(full/'raw-traces.jsonl')}
    return rows,ev

def _support3(rows):
    by=defaultdict(list)
    for r in rows: by[r['memory_id']].append(r)
    cand=[]
    for mid,items in sorted(by.items()):
        probe=[r for r in items if r['evaluation_role']=='probe_development']
        future=[r for r in items if r['evaluation_role']=='future_eval']
        if len(probe)!=3 or len(future)!=3:
            raise RuntimeError(f'candidate split integrity failed:{mid}:probe={len(probe)}:future={len(future)}')
        pe=[r['controlled_delta'] for r in probe]; fe=[r['controlled_delta'] for r in future]
        probe_harm=sum(v<0 for v in pe); future_harm=sum(v<0 for v in fe)
        probe_benefit=sum(v>0 for v in pe); future_benefit=sum(v>0 for v in fe)
        cand.append({
            'memory_id':mid,'source_family':items[0]['source_family'],'candidate_role':items[0]['candidate_role'],
            'probe_nonzero':sum(v!=0 for v in pe),'future_nonzero':sum(v!=0 for v in fe),
            'probe_harm':probe_harm,'future_harm':future_harm,'probe_benefit':probe_benefit,'future_benefit':future_benefit,
            'controlled_nonzero':sum(v!=0 for v in pe+fe),'mean_controlled_effect':_mean(pe+fe),
            'replicated_harm':probe_harm>0 and future_harm>0,
            'replicated_benefit':probe_benefit>0 and future_benefit>0,
        })
    held=[r for r in rows if r['candidate_role']=='heldout_candidate' and r['evaluation_role']=='future_eval']
    nh=sum(x['replicated_harm'] for x in cand); nb=sum(x['replicated_benefit'] for x in cand)
    checks={'candidate_count':{'required':8,'actual':len(cand),'pass':len(cand)>=8},'replicated_controlled_harm_candidates':{'required':2,'actual':nh,'pass':nh>=2},'replicated_controlled_benefit_candidates':{'required':2,'actual':nb,'pass':nb>=2},'candidate_level_independent_heldout_future_evaluation':{'required':True,'actual':len(held)==12,'pass':len(held)==12}}
    return {'replication_contract':'same candidate must exhibit the same controlled-effect sign in both probe_development and future_eval; require >=2 harm candidates and >=2 benefit candidates','candidates':cand,'heldout_future_units':len(held),'gate_checks':checks,'support_gate_pass':all(x['pass'] for x in checks.values())}

def _policy(eval_rows,scores,name,all_on=False):
    accepted=[]
    for r in eval_rows:
        s=1.0 if all_on else float(scores.get(r['unit_id'],0.0))
        if all_on or s>0: accepted.append(r)
    nz=[r for r in eval_rows if r['controlled_delta']!=0 and _sign(float(scores.get(r['unit_id'],0)))!=0]
    correct=sum(_sign(float(scores.get(r['unit_id'],0)))==_sign(r['controlled_delta']) for r in nz)
    return {'policy':name,'eval_units':len(eval_rows),'accepted_units':len(accepted),'coverage':len(accepted)/len(eval_rows) if eval_rows else 0.0,'future_harm_events':sum(r['retrieved_delta']<0 for r in accepted),'future_benefit_events':sum(r['retrieved_delta']>0 for r in accepted),'net_utility_vs_no_memory':sum(r['retrieved_delta'] for r in accepted),'effect_sign_accuracy':correct/len(nz) if nz else None}

def _gate3(rows):
    train=[r for r in rows if r['candidate_role']=='development' and r['evaluation_role']=='probe_development']
    dev=[r for r in rows if r['candidate_role']=='development' and r['evaluation_role']=='future_eval']
    held=[r for r in rows if r['candidate_role']=='heldout_candidate' and r['evaluation_role']=='future_eval']
    byc=defaultdict(list); byf=defaultdict(list)
    for r in train: byc[r['memory_id']].append(r); byf[r['source_family']].append(r)
    def scores(es,key,mode):
        out={}
        for r in es:
            src=byc[r['memory_id']] if mode=='candidate' else byf[r['source_family']]
            out[r['unit_id']]=_mean([x[key] for x in src])
        return out
    devpol=[_policy(dev,{},'no-memory'),_policy(dev,{},'write-all',True),_policy(dev,scores(dev,'retrieved_delta','candidate'),'two-arm-candidate-mean'),_policy(dev,scores(dev,'controlled_delta','candidate'),'placebo-controlled-candidate-mean')]
    heldpol=[_policy(held,{},'no-memory'),_policy(held,{},'write-all',True),_policy(held,scores(held,'retrieved_delta','family'),'two-arm-source-family-shrinkage'),_policy(held,scores(held,'controlled_delta','family'),'placebo-controlled-source-family-shrinkage')]
    disagreement=sum(_sign(r['retrieved_delta'])!=_sign(r['controlled_delta']) for r in rows)
    return {'train_contract':'development candidates x probe_development only','development_future':{'units':len(dev),'policies':devpol},'heldout_candidate_future':{'units':len(held),'policies':heldpol},'two_arm_vs_controlled_attribution_disagreement_units':disagreement,'method_pass_authorized':False,'method_pass_note':'No numeric minimum-coverage threshold was frozen for the qualitative method-PASS condition; report evidence without inventing a post-hoc threshold.'}

def _tok(s): return {x for x in re.split(r'[^a-z0-9]+',s.lower()) if len(x)>1 and x not in {'home','hdd','yutong','agent','evolution','data','alfworld','valid','unseen','game','trial','none','recep'}}
def _jac(a,b):
    x,y=_tok(a),_tok(b); return len(x&y)/len(x|y) if x|y else 0.0

def _transport(rows):
    train=[r for r in rows if r['candidate_role']=='development' and r['evaluation_role']=='probe_development']
    ev=[r for r in rows if r['candidate_role']=='heldout_candidate' and r['evaluation_role']=='future_eval']
    pred=[]
    for r in ev:
        allowed=[x for x in train if x['target_family']!=r['target_family']]
        same=[x for x in allowed if x['source_family']==r['source_family']]
        sf=_mean([x['controlled_delta'] for x in same])
        nearest=max(allowed,key=lambda x:_jac(x['target_task_id'],r['target_task_id']),default=None)
        sem=float(nearest['controlled_delta']) if nearest else 0.0
        rel=[x for x in same if x['relation']==r['relation']]
        sig=_mean([x['controlled_delta'] for x in rel]) if rel else sf
        pred.append({'unit_id':r['unit_id'],'source_family':r['source_family'],'target_family':r['target_family'],'actual_controlled_delta':r['controlled_delta'],'actual_retrieved_delta':r['retrieved_delta'],'source_family_mean_loto':sf,'semantic_similarity_loto':sem,'nearest_family_task_signature_loto':sig})
    def met(key):
        covered=[r for r in pred if _sign(r[key])!=0]; nz=[r for r in covered if r['actual_controlled_delta']!=0]
        correct=sum(_sign(r[key])==_sign(r['actual_controlled_delta']) for r in nz); accepted=[r for r in pred if r[key]>0]
        return {'baseline':key,'eval_units':len(pred),'selective_coverage':len(covered)/len(pred) if pred else 0.0,'nonzero_effects_covered':len(nz),'effect_sign_error':1-correct/len(nz) if nz else None,'negative_transfer_events':sum(r['actual_retrieved_delta']<0 for r in accepted),'net_utility_vs_no_memory':sum(r['actual_retrieved_delta'] for r in accepted)}
    fam=Counter(r['target_family'] for r in rows if r['controlled_delta']!=0); eligible=sum(v>=2 for v in fam.values()); nn=sum(r['controlled_delta']!=0 for r in rows)
    checks={'controlled_nonzero':{'required':12,'actual':nn,'pass':nn>=12},'eligible_target_family_folds':{'required':3,'actual':eligible,'pass':eligible>=3}}
    return {'strict_loto_contract':'Hold out target family; train only development-candidate probe rows from other target families; evaluate candidate-3 future_eval.','support_gate_checks':checks,'support_gate_pass':all(x['pass'] for x in checks.values()),'target_family_nonzero':dict(fam),'baselines':[met('source_family_mean_loto'),met('semantic_similarity_loto'),met('nearest_family_task_signature_loto')],'r_learner_status':'BASELINE_ESTIMATION_UNDERPOWERED','r_learner_note':'A distinct R-learner is not estimated from only 24 development-probe paired-effect units; this is baseline underpower, not method failure.','proposed_transport_status':'MECHANISM_NOT_YET_IMPLEMENTED_AS_DISTINCT_FROM_MATCHED_SIMPLIFICATIONS','method_failure_authorized':False,'predictions':pred}

def analyze(run_dir:Path):
    rows,ev=_rows(run_dir); s3=_support3(rows); g3=_gate3(rows); t5=_transport(rows)
    second=bool(s3['support_gate_pass'] and t5['support_gate_pass'])
    return {'schema_version':'1.0','analysis_id':'p0-mem-xfer-support-enriched-offline-v1','created_at':_now(),'experiment_id':EXPERIMENT_ID,'source_evidence':ev,'idea_3':{'idea_id':'replicated-effect-memory-gate','support':s3,'analysis':g3,'verdict':'SUPPORT_GATE_PASS_METHOD_EVALUATION_INCONCLUSIVE' if s3['support_gate_pass'] else 'SUPPORT_INSUFFICIENT_METHOD_INCONCLUSIVE'},'idea_5':{'idea_id':'cross-task-effect-transport-certificate','analysis':t5,'verdict':'TRANSPORT_SUPPORT_GATE_PASS_MECHANISM_INCONCLUSIVE' if t5['support_gate_pass'] else 'TRANSPORT_SUPPORT_INSUFFICIENT'},'second_model_authorized':second,'second_model_rule':'Authorization requires both frozen full-table mechanism/support gates; it does not imply #3/#5 method PASS.','method_failure_authorized':False}

def write_analysis(run_dir:Path,out:Path,overwrite:bool=False):
    if out.exists() and any(out.iterdir()) and not overwrite: raise RuntimeError(f'refusing to overwrite non-empty analysis directory:{out}')
    out.mkdir(parents=True,exist_ok=True); result=analyze(run_dir)
    files={'replicated_effect_memory_gate.json':result['idea_3'],'cross_task_effect_transport.json':result['idea_5'],'offline_decision.json':result}
    for name,payload in files.items(): (out/name).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    pred=result['idea_5']['analysis']['predictions']
    if pred:
        with (out/'strict_loto_predictions.csv').open('w',encoding='utf-8',newline='') as h:
            w=csv.DictWriter(h,fieldnames=list(pred[0])); w.writeheader(); w.writerows(pred)
    manifest={'schema_version':'1.0','cpu_only':True,'source_files_modified':False,'created_at':_now(),'plan_hash':PLAN_HASH,'outputs':sorted([*files,'strict_loto_predictions.csv'])}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

def _analysis_matches_run(result:dict,run_dir:Path)->bool:
    try:
        full=_select_completed_full_dir(run_dir); ev=result.get('source_evidence') or {}
        return (
            ev.get('plan_hash')==PLAN_HASH
            and ev.get('progress_sha256')==_sha(full/'progress.json')
            and ev.get('decision_sha256')==_sha(full/'decision.json')
            and ev.get('main_table_sha256')==_sha(full/'main_table.csv')
            and ev.get('raw_sha256')==_sha(full/'raw-traces.jsonl')
        )
    except Exception:
        return False

def ensure_analysis(run_dir:Path,out:Path):
    p=out/'offline_decision.json'
    if p.exists():
        existing=_json(p)
        if _analysis_matches_run(existing,run_dir): return existing
        return write_analysis(run_dir,out,overwrite=True)
    return write_analysis(run_dir,out)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--run-dir',type=Path,required=True); p.add_argument('--output-dir',type=Path); p.add_argument('--overwrite',action='store_true'); a=p.parse_args()
    out=a.output_dir or a.run_dir/'support-enriched-analysis'; print(json.dumps(write_analysis(a.run_dir,out,a.overwrite),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
