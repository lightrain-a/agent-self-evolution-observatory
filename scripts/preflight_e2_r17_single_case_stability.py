#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json, require, sha_file
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime

def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); t.replace(p)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); require(not a.output.exists(),'stability preflight exists')
    c=load_json(a.contract); require(c.get('status')=='FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY','stability contract drift'); require(not any((c.get('authority') or {}).values()),'contract unexpectedly grants authority')
    for label,item in c['bound_code'].items(): p=ROOT/item['path']; require(p.is_file() and sha_file(p)==item['sha256'],f'bound code drift {label}')
    for state in c['learned_states']:
        skill=Path(state['skill_post_path']); receipt=Path(state['update_receipt_path']); require(skill.is_file() and sha_file(skill)==state['skill_post_sha256'],f'skill drift {state["arm"]}'); require(receipt.is_file() and sha_file(receipt)==state['update_receipt_sha256'],f'receipt drift {state["arm"]}')
    run=Path(c['run_root']); lease=Path(c['lineage_lease_path']); require(not run.exists(),'stability run root exists'); require(not lease.exists(),'stability lease exists')
    suite=Path(c['suite']['root']); require(sha_file(suite/'suite_manifest.json')==c['suite']['suite_manifest_sha256'],'suite drift'); require(sha_file(suite/'r17_split_manifest.json')==c['suite']['split_manifest_sha256'],'split drift')
    actor_python,_=validate_actor_runtime({'runtime':c['actor_runtime']}); require(actor_python.is_file(),'actor runtime missing'); identity=ROOT/c['model_identity']['path']; require(identity.is_file() and sha_file(identity)==c['model_identity']['sha256'],'identity drift'); require(load_json(identity).get('status')=='PASS_CURRENT_REVIEW_TRANCHE','identity not passing')
    mind=Path(c['mindmemos']['root']); head=subprocess.check_output(['git','-C',str(mind),'rev-parse','HEAD'],text=True).strip(); require(head==c['mindmemos']['commit'],'MindMemOS commit drift'); require(not subprocess.check_output(['git','-C',str(mind),'status','--short'],text=True).strip(),'MindMemOS dirty')
    payload={'schema_version':'1.0','artifact_type':'e2-r17-single-case-first-fail-stability-zero-provider-preflight','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_FIRST_FAIL_STABILITY_ZERO_PROVIDER_PREFLIGHT','contract_path':str(a.contract),'contract_sha256':sha_file(a.contract),'provider_calls':0,'provider_claims':0,'scientific_outcomes_read':False,'partial_effect_read':False,'analyzer_run':False,'run_root_absent':True,'lineage_lease_absent':True,'learned_states_bound':2,'measurement_replicates':[1,2],'heldout_units':72,'next_gate':'MINT_SINGLE_USE_FIRST_FAIL_STABILITY_MEASUREMENT_AUTHORIZATION'}; atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
