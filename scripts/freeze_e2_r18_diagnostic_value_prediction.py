#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path): return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,msg:str):
    if not x: raise RuntimeError(msg)
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--prereg',type=Path,required=True); ap.add_argument('--pool-support',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    req(not a.output.exists(),'prediction already frozen')
    pr=load(a.prereg); support=load(a.pool_support)
    req(support.get('provider_pool_stage_complete') is True,'pool stage incomplete')
    req(support.get('updater_calls')==0 and support.get('heldout_evaluations')==0,'prediction must freeze before updater/evaluation')
    req(support.get('scientific_effect_read') is False,'effect already read')
    split=Path(pr['future_update_substrate']['split_manifest']); req(sha(split)==pr['future_update_substrate']['split_manifest_sha256'],'split drift')
    sp=load(split); streams=sp['e3_future_streams']
    counts={str(k):int(v) for k,v in support.get('mixed_pool_count_by_stream',{}).items()}
    req(set(counts)==set(streams),'pool support stream set drift')
    suite=Path(pr['future_update_substrate']['suite_root']); meta=load(suite/'r17_controlled_metadata.json'); byid={r['id']:r for r in meta}
    fam_streams=defaultdict(list)
    for s,ids in streams.items():
        fams={byid[t]['primary_failure_family'] for t in ids}; req(len(fams)==1,f'family drift {s}')
        c=counts[s]; req(0<=c<=8,f'mixed count invalid {s}')
        fam_streams[next(iter(fams))].append((s,c/8.0,c))
    delta={k:float(v) for k,v in pr['calibration_lock']['family_effects_delta_hat'].items()}
    req(set(fam_streams)==set(delta),'family set drift')
    preds={}; values=[]
    for fam in sorted(delta):
        rows=sorted(fam_streams[fam]); req(len(rows)==2,f'expected 2 streams {fam}')
        m=sum(r[1] for r in rows)/2.0; rhat=m*delta[fam]; values.append(round(rhat,15))
        preds[fam]={'delta_hat_r17':delta[fam],'future_mixed_fraction_mean':m,'Rhat':rhat,'streams':[{'stream_id':s,'mixed_count':c,'mixed_fraction':f} for s,f,c in rows]}
    distinct=len(set(values)); gate=distinct>=4
    payload={'schema_version':'1.0','artifact_type':'e2-r18-diagnostic-value-prediction-freeze','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_R18_PREDICTION_FROZEN_BEFORE_UPDATER' if gate else 'HOLD_R18_PREDICTOR_SUPPORT_DEGENERATE_BEFORE_UPDATER','prereg_path':str(a.prereg),'prereg_sha256':sha(a.prereg),'pool_support_path':str(a.pool_support),'pool_support_sha256':sha(a.pool_support),'split_manifest_sha256':sha(split),'family_predictions':preds,'distinct_Rhat_values':distinct,'support_gate_pass':gate,'prediction_formula':'Rhat_z=M_z_future*delta_hat_z_R17','updater_calls_before_freeze':0,'heldout_evaluations_before_freeze':0,'scientific_effect_read_before_freeze':False,'authority':{'updater':False,'heldout_evaluation':False,'analyzer':False,'provider_io':False,'scientific_execution':False}}
    a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if gate else 3
if __name__=='__main__': raise SystemExit(main())
