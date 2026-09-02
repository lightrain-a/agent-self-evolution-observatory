#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_diagnostic_witness import build_four_arm_evidence
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json, require, sha_file
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_v31_provider_runtime_pilot import validate_updater_runtime

STATUS="PASS_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY_ZERO_PROVIDER_PREFLIGHT"


def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); t.replace(p)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); require(not a.output.exists(),'exact-replay preflight exists')
    c=load_json(a.contract); require(c.get('status')=='FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY','contract drift'); require(not any((c.get('authority') or {}).values()),'contract grants authority')
    for label,item in c['bound_code'].items():
        p=ROOT/item['path']; require(p.is_file() and sha_file(p)==item['sha256'],f'bound code drift {label}')
    for key in ('design','selector_freeze'):
        item=c[key]; p=ROOT/item['path']; require(p.is_file() and sha_file(p)==item['sha256'],f'{key} drift')
    run=Path(c['run_root']); lease=Path(c['lineage_lease_path']); require(not run.exists(),'exact-replay run root exists'); require(not lease.exists(),'exact-replay lease exists')
    suite=Path(c['suite']['root']); require(sha_file(suite/'suite_manifest.json')==c['suite']['suite_manifest_sha256'],'suite drift'); require(sha_file(suite/'r17_split_manifest.json')==c['suite']['split_manifest_sha256'],'split drift')
    updater_python,_=validate_updater_runtime({'runtime':c['updater_runtime'],'mindmemos':c['mindmemos']}); actor_python,_=validate_actor_runtime({'runtime':c['actor_runtime']}); require(updater_python.is_file() and actor_python.is_file(),'runtime missing')
    identity=ROOT/c['model_identity']['path']; require(identity.is_file() and sha_file(identity)==c['model_identity']['sha256'],'identity drift'); require(load_json(identity).get('status')=='PASS_CURRENT_REVIEW_TRANCHE','identity not passing')
    mind=Path(c['mindmemos']['root']); head=subprocess.check_output(['git','-C',str(mind),'rev-parse','HEAD'],text=True).strip(); require(head==c['mindmemos']['commit'],'MindMemOS drift'); require(not subprocess.check_output(['git','-C',str(mind),'status','--short'],text=True).strip(),'MindMemOS dirty')
    pools=[]
    for row in c['pool_bindings']:
        p=Path(row['path']); require(p.is_file() and sha_file(p)==row['sha256'],f'pool drift {row["task_id"]}'); pool=load_frozen_pool(p); require(pool.pool_id==row['pool_id'] and pool.task_id==row['task_id'],'pool identity drift'); pools.append(pool)
    freeze=load_json(ROOT/c['selector_freeze']['path']); units,_=build_four_arm_evidence(pools,selector_freeze=freeze,final_block_cap_tokens=int(c['renderer']['final_block_cap_tokens']),transcript_max_chars=int(c['updater']['transcript_max_chars']))
    evidence_checks={}
    for arm in ('win_c','first_fail'):
        actual=[str(u.evidence_sha256) for u in units[arm]]; expected=c['exact_evidence'][arm]['evidence_sha256s']; require(actual==expected,f'exact rendered evidence drift {arm}'); evidence_checks[arm]={'count':len(actual),'sha_match':True,'evidence_sha256s':actual}
    payload={'schema_version':'1.0','artifact_type':'e2-r17-single-case-first-fail-exact-replay-preflight','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':STATUS,'contract_path':str(a.contract),'contract_sha256':sha_file(a.contract),'provider_calls':0,'provider_claims':0,'scientific_outcomes_read':False,'partial_effect_read':False,'analyzer_run':False,'run_root_absent':True,'lineage_lease_absent':True,'exact_evidence_identity_pass':True,'evidence_checks':evidence_checks,'new_learned_states':4,'heldout_units':72,'next_gate':'MINT_SINGLE_USE_FIRST_FAIL_EXACT_REPLAY_AUTHORIZATION'}; atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
