#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_bridge_v4r2_execution_plan import SCREEN, search_units, stage_stream_ids, update_tasks

STATUS="FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT"
SUITE=Path('/data/wyt/e2-r17-search-projection/state-compiler-bridge-suite-v1-20260903')
MIND=Path('/data/wyt/evidence-substrates/MindMemOS-20260817')
ENV=Path('/home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/.env')
RUN=Path('/data/wyt/e2-r17-search-projection/runs/bridge-v4r2-stage-a-screen-20260907')
LEASE=Path('/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-bridge-v4r2-stage-a-screen-v1.json')
IDENTITY=ROOT/'generated/e2-r17-bridge-v4r2-stage-a-model-identity-20260907.json'
ELIGIBILITY=ROOT/'generated/e2-r17-m3r4-to-bridge-v4r2-eligibility-adjudication-20260907.json'
PROTOCOL=ROOT/'generated/e2-r17-state-compiler-bridge-protocol-v4-r2-20260903.md'
REVIEW=ROOT/'generated/e2-r17-state-compiler-bridge-v4r2-preexecution-rereview-20260904.json'
INITIAL=MIND/'resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md'
RUNTIME_PY=Path('/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python')
RUNTIME_FREEZE=Path('/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt')
RUNTIME_QUAL=ROOT/'generated/e2-r17-runtime-dependency-qualification-r2-20260828.json'


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def item(path:str)->dict[str,str]:
    p=ROOT/path;return {'path':path,'sha256':sha(p)}


def build_contract()->dict[str,Any]:
    identity=load(IDENTITY);elig=load(ELIGIBILITY);review=load(REVIEW)
    if identity.get('status')!='PASS_BRIDGE_V4R2_STAGE_A_MODEL_IDENTITY':raise RuntimeError('Bridge Stage-A identity not PASS')
    if elig.get('status')!='PASS_M3R4_NARROWS_MECHANISM_BUT_DOES_NOT_BLOCK_BRIDGE_V4R2_STAGE_A_ELIGIBILITY':raise RuntimeError('M3R4 eligibility not PASS')
    if review.get('verdict')!='PASS_PREEXECUTION_DESIGN':raise RuntimeError('V4-R2 independent design review not PASS')
    units=search_units(SCREEN);streams=stage_stream_ids(SCREEN);tasks=[t for s in streams for t in update_tasks(s)]
    if len(units)!=384 or len(tasks)!=48 or len(set(tasks))!=48:raise RuntimeError('Bridge Stage-A geometry drift')
    head=subprocess.check_output(['git','-C',str(MIND),'rev-parse','HEAD'],text=True).strip()
    return {
      'schema_version':'1.0','artifact_type':'e2-r17-bridge-v4r2-stage-a-screen-search-support-contract','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':STATUS,'scientific_object':'E2-R17-STATE-COMPILER-BRIDGE-V4R2','stage':'SCREEN_STAGE_A_SEARCH_SUPPORT',
      'protocol':{'path':str(PROTOCOL.relative_to(ROOT)),'sha256':sha(PROTOCOL),'review_path':str(REVIEW.relative_to(ROOT)),'review_sha256':sha(REVIEW),'review_verdict':review['verdict']},
      'm3r4_eligibility':{'path':str(ELIGIBILITY.relative_to(ROOT)),'sha256':sha(ELIGIBILITY),'status':elig['status']},
      'model_identity':{'path':str(IDENTITY.relative_to(ROOT)),'sha256':sha(IDENTITY),'status':identity['status'],'scientific_tranche':'E2-R17-BRIDGE-V4R2-STAGE-A'},
      'env_file':str(ENV),
      'suite':{'root':str(SUITE),'suite_manifest_sha256':sha(SUITE/'suite_manifest.json'),'split_manifest_sha256':sha(SUITE/'bridge_split_manifest.json'),'metadata_sha256':sha(SUITE/'bridge_metadata.json')},
      'mindmemos':{'root':str(MIND),'commit':head},
      'initial_skill':{'path':str(INITIAL),'sha256':sha(INITIAL)},
      'runtime':{'venv_root':str(RUNTIME_PY.parent.parent),'python_executable':str(RUNTIME_PY),'freeze_path':str(RUNTIME_FREEZE),'freeze_sha256':sha(RUNTIME_FREEZE),'qualification_path':str(RUNTIME_QUAL),'qualification_sha256':sha(RUNTIME_QUAL),'qualification_status':'PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2'},
      'actor':{'requested_model':'deepseek-v4-pro','required_resolved_model':'deepseek-v4-pro-ga-260813','temperature':0,'thinking':'disabled','provider_retry_limit':0,'max_turns':10,'max_output_tokens':8192,'search_k':8,'concurrency':1},
      'search':{'stream_ids':list(streams),'tasks_by_stream':{s:list(update_tasks(s)) for s in streams},'task_ids':tasks,'unit_ids':[u.unit_id for u in units],'unit_count':384,'exact_k':8,'order':'frozen execution-plan SHA rank'},
      'support_gate':{'mixed_pools_per_stream_minimum':4,'all_six_streams_must_pass':True,'stream_task_or_k_replacement':False,'inspection_after_all_384_search_units':True},
      'budget':{'search_provider_call_ceiling':3840,'per_search_unit_call_ceiling':10,'updater_call_ceiling':0,'heldout_actor_call_ceiling':0,'removed_or_unused_calls_reallocatable':False},
      'run_root':str(RUN),'lineage_lease_path':str(LEASE),
      'bound_code':{
        'runner':item('scripts/run_e2_r17_bridge_v4r2_stage_a.py'),'runtime':item('research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py'),'support':item('research_pipeline/e2_r17_bridge_v4r2_stage_a_support.py'),'execution_plan':item('research_pipeline/e2_r17_bridge_v4r2_execution_plan.py'),'actor_rollout':item('research_pipeline/e2_r17_actor_pool.py'),'ark_adapter':item('research_pipeline/e2_r17_ark_plan_react.py'),'provider_budget':item('research_pipeline/e2_r17_provider_budget.py')},
      'authority':{'scientific_experiment':False,'provider_io':False,'search_pool_acquisition':False,'support_inspection':False,'free_updater':False,'deterministic_state_materialization':False,'actor_evaluation':False,'screen_outcome_opening':False,'validation_opening':False,'analysis':False,'paper_promotion':False},
      'outcome_boundary':{'method_effect_read':False,'updater_calls':0,'heldout_actor_calls':0,'validation_open':False},
      'next_gate':'ZERO_PROVIDER_STAGE_A_CONTRACT_PREFLIGHT_THEN_INDEPENDENT_EXECUTION_REVIEW'
    }


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise RuntimeError('Stage-A contract output exists')
    p=build_contract();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(p,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(json.dumps(p,ensure_ascii=False,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
