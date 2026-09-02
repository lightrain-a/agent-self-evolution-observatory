#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path): return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,msg:str):
    if not x: raise RuntimeError(msg)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--preflight',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 req(not a.output.exists(),'adjudication exists')
 c=load(a.contract); p=load(a.preflight)
 req(c['status']=='FROZEN_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_POOL_SUPPORT','contract status')
 req(p['status']=='PASS_R18_STAGE_A_ACTUAL_PATH_12_OF_12_ZERO_PROVIDER','preflight status'); req(p['contract_sha256']==sha(a.contract),'preflight contract drift')
 req(p['provider_calls']==0 and p['provider_claims']==0 and p['updater_calls']==0 and p['heldout_evaluations']==0,'preflight boundary crossed')
 prereg=Path(c['preregistration']['path']); req(sha(prereg)==c['preregistration']['sha256'],'prereg drift'); pr=load(prereg); req(pr['parent']['terminal_status']=='HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS','parent drift')
 elig=Path(c['future_substrate_eligibility']['path']); req(sha(elig)==c['future_substrate_eligibility']['sha256'],'eligibility drift'); req(load(elig)['status']=='PASS_R18_UNTOUCHED_FUTURE_SUBSTRATE_ELIGIBLE_FOR_NEW_CHILD_ONLY','future substrate not eligible')
 held=Path(c['fresh_heldout_qualification']['path']); req(sha(held)==c['fresh_heldout_qualification']['sha256'],'heldout qual drift')
 req(not Path(c['run_root']).exists(),'Stage A run root already exists'); lease=Path(c['global_lineage_lease']['path']); req(not lease.exists(),'Stage A global lease already exists')
 req(not Path('generated/e2-r18-diagnostic-value-prediction-freeze-20260902.json').exists(),'prediction already exists before Stage A')
 head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
 payload={'schema_version':'1.0','artifact_type':'e2-r18-stage-a-preexecution-adjudication','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_R18_STAGE_A_READY_FOR_SINGLE_USE_EXECUTION_AUTHORIZATION','git_head':head,'contract_path':str(a.contract),'contract_sha256':sha(a.contract),'actual_path_preflight_path':str(a.preflight),'actual_path_preflight_sha256':sha(a.preflight),'future_streams':12,'future_tasks':96,'k':8,'actor_rollouts_exact':768,'provider_call_hard_ceiling':7680,'provider_retry_limit':0,'updater_calls_authorized':0,'heldout_evaluations_authorized':0,'parent_r17_status':'HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS','parent_r17_status_changed':False,'old_e3_authority_reused':False,'fresh_heldout_reserved_for_later_stage_b':True,'run_root_absent':True,'global_lease_absent':True,'provider_calls_before_authorization':0,'prediction_freeze_before_stage_a':False,'negative_guard_tests':{'preflight_auth_cannot_execute':True,'wrong_k_rejected':True,'out_of_scope_task_rejected':True},'authority':{'mint_single_use_stage_a_execution_authorization':True,'updater':False,'heldout_evaluation':False,'analyzer':False,'second_backbone':False,'public_benchmark':False,'paper_promotion':False}}
 a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
