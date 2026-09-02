#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json, require, sha_file

def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); t.replace(p)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--preflight',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); require(not a.output.exists(),'stability authorization exists')
    c=load_json(a.contract); p=load_json(a.preflight); csha=sha_file(a.contract); require(c.get('status')=='FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY','contract drift'); require(p.get('status')=='PASS_FIRST_FAIL_STABILITY_ZERO_PROVIDER_PREFLIGHT' and p.get('contract_sha256')==csha,'preflight drift'); require(int(p.get('provider_calls',-1))==0 and p.get('scientific_outcomes_read') is False,'preflight crossed boundary'); require(not Path(c['run_root']).exists() and not Path(c['lineage_lease_path']).exists(),'stability root/lease no longer fresh')
    parent=c['parent_s1']; payload={'schema_version':'1.0','artifact_type':'e2-r17-single-case-first-fail-stability-measurement-authorization','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'AUTHORIZED_E2_R17_SINGLE_CASE_FIRST_FAIL_STABILITY_MEASUREMENT','contract_path':str(a.contract),'contract_sha256':csha,'preflight_path':str(a.preflight),'preflight_sha256':sha_file(a.preflight),'mindmemos_commit':c['mindmemos']['commit'],'single_use':True,'authority':{'scientific_experiment':True,'measurement_only':True,'provider_io':True,'updater':False,'analyzer':False,'second_backbone':False,'public_benchmark':False,'e3_confirmation':False,'paper_promotion':False,'submission':False},'parent_repair2_provenance':{'contract_path':str((ROOT/parent['contract_path']).resolve()),'contract_sha256':parent['contract_sha256'],'authorization_path':str((ROOT/parent['authorization_path']).resolve()),'authorization_sha256':parent['authorization_sha256']},'execution_scope':{'measurement_child':'E2-R17-SINGLE-CASE-FIRST-FAIL-STABILITY','allowed_modes':['e1'],'allowed_task_ids':c['heldout_task_ids'],'exact_k':1,'allow_noninitial_skill':True,'learned_states':c['learned_states'],'measurement_replicates':[1,2],'required_resolved_model':c['actor']['resolved_model'],'identity_artifact_sha256':c['model_identity']['sha256'],'suite_manifest_sha256':c['suite']['suite_manifest_sha256'],'split_manifest_sha256':c['suite']['split_manifest_sha256'],'max_turns':c['actor']['max_turns'],'max_output_tokens':c['actor']['max_output_tokens'],'provider_budget':{'required':True,'total_limit':191,'per_unit_limit':11},'exactly_once':True,'automatic_retry':False,'completed_unit_replay':False,'partial_effect_read':False,'lineage_lease_path':c['lineage_lease_path']},'interpretation_boundary':'Measurement-only development follow-up on two frozen S1 learned states. No updater calls, no S2/E3, no second backbone, no paper or submission authority.'}; atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
