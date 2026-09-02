#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

def sha(p:Path|str)->str: return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--preflight-authorization',type=Path,required=True); a=ap.parse_args()
 if a.contract.exists() or a.preflight_authorization.exists(): raise RuntimeError('R18 Stage A freeze artifacts already exist')
 suite=Path('/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2'); sp=json.loads((suite/'r17_split_manifest.json').read_text()); streams=list(sp['e3_future_streams'])
 c={
  'schema_version':'1.0','artifact_type':'e2-r18-diagnostic-value-stage-a-contract','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'FROZEN_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_POOL_SUPPORT',
  'preregistration':{'path':'generated/e2-r18-diagnostic-value-transport-preregistration-20260902.json','sha256':sha('generated/e2-r18-diagnostic-value-transport-preregistration-20260902.json')},
  'future_substrate_eligibility':{'path':'generated/e2-r18-future-substrate-eligibility-audit-20260902.json','sha256':sha('generated/e2-r18-future-substrate-eligibility-audit-20260902.json'),'required_status':'PASS_R18_UNTOUCHED_FUTURE_SUBSTRATE_ELIGIBLE_FOR_NEW_CHILD_ONLY'},
  'fresh_heldout_qualification':{'path':'generated/e2-r18-heldout-probe-runtime-qualification-20260902.json','sha256':sha('generated/e2-r18-heldout-probe-runtime-qualification-20260902.json'),'required_status':'PASS_ZERO_PROVIDER_R18_FRESH_HELDOUT_RUNTIME_QUALIFIED'},
  'parent_calibration':{'analysis_path':'generated/e2-r17-deepseek-v2-repair2-continuation-v2-analysis-20260902.json','analysis_sha256':sha('generated/e2-r17-deepseek-v2-repair2-continuation-v2-analysis-20260902.json'),'required_status':'HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS','role':'calibration_only'},
  'suite':{'root':str(suite),'suite_manifest_sha256':sha(suite/'suite_manifest.json'),'split_manifest_sha256':sha(suite/'r17_split_manifest.json'),'metadata_sha256':sha(suite/'r17_controlled_metadata.json'),'future_field':'e3_future_streams','old_e3_authority_reused':False},
  'streams':streams,
  'actor':{'requested_model':'deepseek-v4-pro','resolved_model':'deepseek-v4-pro-ga-260813','k':8,'prefix_ks':[1,2,4,8],'max_turns':10,'max_output_tokens':4096,'concurrency':4,'provider_retry_limit':0,'temperature':0,'thinking':'disabled','search_topology':'parallel_best_of_k'},
  'budget':{'actor_rollouts_exact':768,'max_provider_calls':7680,'max_output_tokens_per_provider_call':4096,'provider_retry_limit':0,'updater_calls':0,'heldout_evaluations':0,'claim_before_provider_io':True,'claims_never_released':True},
  'support_gate':{'role':'diagnostic_only_before_mechanical_prediction_freeze','mixed_pool_total':96,'mixed_pool_count_minimum':24,'exposed_stream_minimum':8,'mixed_pools_per_exposed_stream_minimum':2,'supported_families_minimum':4,'r18_binding_gate':'prediction freeze requires >=4 distinct family Rhat values; no updater before freeze'},
  'prediction_freeze':{'script':'scripts/freeze_e2_r18_diagnostic_value_prediction.py','sha256':sha('scripts/freeze_e2_r18_diagnostic_value_prediction.py'),'formula':'Rhat_z=M_z_future*delta_hat_z_R17','must_run_after_stage_a_before_any_updater':True},
  'model_identity':{'path':'generated/e2-r17-e1-a-v2-1-model-identity-adjudication-20260828.json','sha256':sha('generated/e2-r17-e1-a-v2-1-model-identity-adjudication-20260828.json'),'required_status':'PASS_CURRENT_REVIEW_TRANCHE'},
  'runtime':{'venv_root':'/data/wyt/e2-r17-search-projection/mindmemos-eval-venv','python_executable':'/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python','freeze_path':'/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt','freeze_sha256':'ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e','qualification_path':'generated/e2-r17-runtime-dependency-qualification-r2-20260828.json','qualification_sha256':'38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b'},
  'mindmemos':{'root':'/data/wyt/evidence-substrates/MindMemOS-20260817','commit':'90491828726e1540442b17cd445d0308d0b8093c','initial_skill_sha256':'bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb','skill_mutation_allowed':False},
  'bound_code':{
    'actor_stage_a':{'path':'scripts/run_e2_r18_actor_pool_stage_a.py','sha256':sha('scripts/run_e2_r18_actor_pool_stage_a.py')},
    'runner_stage_a':{'path':'scripts/run_e2_r18_pool_support_stage_a.py','sha256':sha('scripts/run_e2_r18_pool_support_stage_a.py')},
    'preflight_stage_a':{'path':'scripts/preflight_e2_r18_stage_a.py','sha256':sha('scripts/preflight_e2_r18_stage_a.py')},
    'prediction_freeze':{'path':'scripts/freeze_e2_r18_diagnostic_value_prediction.py','sha256':sha('scripts/freeze_e2_r18_diagnostic_value_prediction.py')},
    'freeze_contract':{'path':'scripts/freeze_e2_r18_stage_a_contract.py','sha256':sha('scripts/freeze_e2_r18_stage_a_contract.py')}
  },
  'run_root':'/data/wyt/e2-r18-diagnostic-value-transport/runs/stage-a-pool-support-20260902',
  'global_lineage_lease':{'path':'/data/wyt/e2-r18-diagnostic-value-transport/lineage-leases/stage-a-v1.json','acquire':'O_EXCL_BEFORE_RUN_ROOT_AND_PROVIDER_IO','persistent_terminal_seal':True},
  'forbidden':['updater','heldout evaluation','prediction refit','old E3 authorization reuse','second backbone','public benchmark','paper promotion','parent R17 status change','partial R18 effect'],
  'authority':{'provider_io':False,'scientific_experiment':False,'updater':False,'heldout_evaluation':False,'analyzer':False,'paper_promotion':False,'second_backbone':False,'public_benchmark':False}
 }
 a.contract.parent.mkdir(parents=True,exist_ok=True); a.contract.write_text(json.dumps(c,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); csha=sha(a.contract)
 tasks=[t for s in streams for t in sp['e3_future_streams'][s]]
 au={'schema_version':'1.0','artifact_type':'e2-r18-stage-a-preflight-authorization','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'AUTHORIZED_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_PREFLIGHT','contract_path':str(a.contract),'contract_sha256':csha,'mindmemos_commit':c['mindmemos']['commit'],'authority':{'scientific_experiment':False,'r18_stage_a_preflight':True,'r18_stage_a_pool_support':False,'provider_io':False,'updater':False,'heldout_evaluation':False,'analyzer':False,'paper_promotion':False,'second_backbone':False,'public_benchmark':False},'execution_scope':{'allowed_modes':['e1'],'allowed_task_ids':tasks,'exact_k':8,'allow_noninitial_skill':False,'required_skill_pre_sha256':c['mindmemos']['initial_skill_sha256'],'required_resolved_model':c['actor']['resolved_model'],'identity_artifact_sha256':c['model_identity']['sha256'],'suite_manifest_sha256':c['suite']['suite_manifest_sha256'],'split_manifest_sha256':c['suite']['split_manifest_sha256'],'max_turns':10,'max_output_tokens':4096,'provider_budget':{'required':True,'total_limit':7680,'per_unit_limit':10}}}
 a.preflight_authorization.write_text(json.dumps(au,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); print(json.dumps({'contract_sha256':csha,'preflight_authorization_sha256':sha(a.preflight_authorization)},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
