#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_bridge_v4r2_execution_plan import SCREEN, VALIDATION, search_units, stage_heldout, stage_stream_ids, update_tasks
from research_pipeline.e2_r17_bridge_v4r2_stage_a_runtime import CONTRACT_STATUS

STATUS='PASS_ZERO_PROVIDER_BRIDGE_V4R2_STAGE_A_CONTRACT_PREFLIGHT'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def req(v:bool,m:str)->None:
    if not v:raise RuntimeError(m)

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();req(not a.output.exists(),'Stage-A preflight output exists')
    c=load(a.contract);cs=sha(a.contract);req(c.get('status')==CONTRACT_STATUS,'contract status drift');req(not any((c.get('authority') or {}).values()),'contract grants authority')
    for label,item in c['bound_code'].items():
        p=ROOT/item['path'];req(p.is_file() and sha(p)==item['sha256'],f'bound code drift:{label}')
    for label,item in (('protocol',c['protocol']),('eligibility',c['m3r4_eligibility']),('identity',c['model_identity'])):
        p=ROOT/item['path'];req(p.is_file() and sha(p)==item['sha256'],f'{label} drift')
    review=ROOT/c['protocol']['review_path'];req(review.is_file() and sha(review)==c['protocol']['review_sha256'],'protocol review drift');req(load(review).get('verdict')=='PASS_PREEXECUTION_DESIGN','protocol review not PASS')
    req(load(ROOT/c['m3r4_eligibility']['path']).get('adjudication',{}).get('bridge_q1_stage_a_design_eligibility') is True,'M3R4->Bridge eligibility false')
    ident=load(ROOT/c['model_identity']['path']);req(ident.get('status')=='PASS_BRIDGE_V4R2_STAGE_A_MODEL_IDENTITY','identity not PASS');req(ident.get('provider_retry_limit')==0,'identity retry drift')
    suite=Path(c['suite']['root'])
    for n,key in (('suite_manifest.json','suite_manifest_sha256'),('bridge_split_manifest.json','split_manifest_sha256'),('bridge_metadata.json','metadata_sha256')):req((suite/n).is_file() and sha(suite/n)==c['suite'][key],f'suite drift:{n}')
    mind=Path(c['mindmemos']['root']);head=subprocess.check_output(['git','-C',str(mind),'rev-parse','HEAD'],text=True).strip();req(head==c['mindmemos']['commit'],'MindMemOS drift');skill=Path(c['initial_skill']['path']);req(skill.is_file() and sha(skill)==c['initial_skill']['sha256'],'initial skill drift')
    runtime=c['runtime'];py=Path(runtime['python_executable']);freeze=Path(runtime['freeze_path']);qual=Path(runtime['qualification_path']);req(py.is_file(),'runtime python missing');req(freeze.is_file() and sha(freeze)==runtime['freeze_sha256'],'runtime freeze drift');req(qual.is_file() and sha(qual)==runtime['qualification_sha256'],'runtime qualification drift');req(load(qual).get('status')=='PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2','runtime qualification not PASS')
    smoke=subprocess.run([str(py),'-c','import openpyxl,pydantic; from mindmemos_eval.skills.agents import ReactAgentFactory; from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv'],capture_output=True,text=True);req(smoke.returncode==0,'runtime import smoke failed')
    units=search_units(SCREEN);ids=[u.unit_id for u in units];streams=stage_stream_ids(SCREEN);tasks=[t for s in streams for t in update_tasks(s)];req(c['search']['unit_ids']==ids and len(ids)==384 and len(set(ids))==384,'search unit drift');req(c['search']['task_ids']==tasks and len(tasks)==48 and len(set(tasks))==48,'search task drift');req(c['search']['stream_ids']==list(streams) and len(streams)==6,'stream drift');req(c['support_gate']=={'mixed_pools_per_stream_minimum':4,'all_six_streams_must_pass':True,'stream_task_or_k_replacement':False,'inspection_after_all_384_search_units':True},'support gate drift');req(c['budget']['search_provider_call_ceiling']==3840 and c['budget']['per_search_unit_call_ceiling']==10,'budget drift');req(c['budget']['updater_call_ceiling']==0 and c['budget']['heldout_actor_call_ceiling']==0,'Stage-A budget overreach')
    held=set(stage_heldout(SCREEN))|set(stage_heldout(VALIDATION));req(not (set(tasks)&held),'Stage-A search leaks heldout');req(not Path(c['run_root']).exists() and not Path(c['lineage_lease_path']).exists(),'Stage-A run root/lease not fresh')
    out={'schema_version':'1.0','artifact_type':'e2-r17-bridge-v4r2-stage-a-contract-preflight','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':STATUS,'contract_path':str(a.contract.resolve()),'contract_sha256':cs,'search_units':384,'streams':6,'tasks':48,'search_k':8,'support_mixed_minimum_per_stream':4,'heldout_overlap':0,'provider_calls':0,'provider_claims':0,'scientific_outcomes_read':False,'method_effect_read':False,'updater_calls':0,'heldout_actor_calls':0,'validation_open':False,'run_root_fresh':True,'lease_fresh':True,'next_gate':'FRESH_INDEPENDENT_STAGE_A_EXECUTION_REVIEW_BEFORE_AUTHORIZATION'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
