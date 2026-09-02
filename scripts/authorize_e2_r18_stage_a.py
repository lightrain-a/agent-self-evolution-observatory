#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path): return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,msg:str):
    if not x: raise RuntimeError(msg)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--preflight',type=Path,required=True); ap.add_argument('--adjudication',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 req(not a.output.exists(),'execution authorization already exists')
 c=load(a.contract); p=load(a.preflight); j=load(a.adjudication); csha=sha(a.contract)
 req(c['status']=='FROZEN_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_POOL_SUPPORT','contract status drift')
 req(p['status']=='PASS_R18_STAGE_A_ACTUAL_PATH_12_OF_12_ZERO_PROVIDER' and p['contract_sha256']==csha,'preflight not bound/pass')
 req(j['status']=='PASS_R18_STAGE_A_READY_FOR_SINGLE_USE_EXECUTION_AUTHORIZATION' and j['contract_sha256']==csha,'adjudication not bound/pass')
 req(j['actual_path_preflight_sha256']==sha(a.preflight),'adjudication preflight drift')
 req(not Path(c['run_root']).exists(),'run root exists'); req(not Path(c['global_lineage_lease']['path']).exists(),'global lease exists')
 split=load(Path(c['suite']['root'])/'r17_split_manifest.json'); tasks=[t for s in c['streams'] for t in split['e3_future_streams'][s]]; req(len(tasks)==96 and len(set(tasks))==96,'task scope drift')
 payload={'schema_version':'1.0','artifact_type':'e2-r18-stage-a-execution-authorization','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'AUTHORIZED_E2_R18_DIAGNOSTIC_VALUE_STAGE_A','single_use':True,'authorized_runs':1,'contract_path':str(a.contract),'contract_sha256':csha,'actual_path_preflight_path':str(a.preflight),'actual_path_preflight_sha256':sha(a.preflight),'preexecution_adjudication_path':str(a.adjudication),'preexecution_adjudication_sha256':sha(a.adjudication),'mindmemos_commit':c['mindmemos']['commit'],'global_lineage_lease_path':c['global_lineage_lease']['path'],'authority':{'scientific_experiment':True,'r18_stage_a_preflight':False,'r18_stage_a_pool_support':True,'provider_io':True,'updater':False,'heldout_evaluation':False,'analyzer':False,'paper_promotion':False,'second_backbone':False,'public_benchmark':False},'execution_scope':{'allowed_modes':['e1'],'allowed_task_ids':tasks,'exact_k':8,'allow_noninitial_skill':False,'required_skill_pre_sha256':c['mindmemos']['initial_skill_sha256'],'required_resolved_model':c['actor']['resolved_model'],'identity_artifact_sha256':c['model_identity']['sha256'],'suite_manifest_sha256':c['suite']['suite_manifest_sha256'],'split_manifest_sha256':c['suite']['split_manifest_sha256'],'max_turns':c['actor']['max_turns'],'max_output_tokens':c['actor']['max_output_tokens'],'provider_budget':{'required':True,'total_limit':c['budget']['max_provider_calls'],'per_unit_limit':c['actor']['max_turns']},'updater_calls':0,'heldout_evaluations':0},'post_execution_boundary':'After 96 pools complete, freeze Rhat predictions mechanically before any updater; this authorization grants no Stage B authority.'}
 a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
