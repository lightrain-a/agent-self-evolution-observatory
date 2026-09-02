#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def req(x:bool,m:str)->None:
    if not x: raise RuntimeError(m)
def atomic(p:Path,d:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)

def packet_bindings(receipt_path:Path,expected_sha:str)->dict[str,Any]:
    req(receipt_path.is_file() and sha(receipt_path)==expected_sha,f'parent update receipt drift: {receipt_path}')
    d=load(receipt_path); packets=d.get('packets') or []; req(len(packets)==8,'parent packet cardinality drift')
    return {'receipt_path':str(receipt_path),'receipt_sha256':expected_sha,'task_ids':[str(x['task_id']) for x in packets],'evidence_sha256s':[str(x['rendered_packet_sha256']) for x in packets],'evidence_tokens':[int(x['rendered_packet_tokens']) for x in packets],'source_trajectory_sha256s':[str(x['source_trajectory_sha256']) for x in packets]}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--design',type=Path,required=True); ap.add_argument('--s1-contract',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); req(not a.output.exists(),'exact-replay contract exists')
    d=load(a.design); s1=load(a.s1_contract); req(d.get('status')=='DESIGN_ONLY_ZERO_AUTHORITY' and not any((d.get('authority') or {}).values()),'design not zero-authority'); req(s1.get('status')=='FROZEN_E2_R17_SINGLE_CASE_DIAGNOSTIC_WITNESS_S1','S1 contract drift')
    parent=d['parent_s1']; req(sha(a.s1_contract)==parent['contract_sha256'],'S1 contract binding drift'); stab=ROOT/d['parent_stability_analysis']['path']; req(stab.is_file() and sha(stab)==d['parent_stability_analysis']['sha256'] and load(stab).get('status')==d['parent_stability_analysis']['required_status'],'stability parent drift')
    ff_info=d['exact_evidence_rule']; ff=packet_bindings(Path(ff_info['s1_first_fail_update_receipt_path']),ff_info['s1_first_fail_update_receipt_sha256'])
    win_path=Path('/data/wyt/e2-r17-search-projection/runs/single-case-diagnostic-witness-s1-20260902/states/e1-tsr-00/replicate_0/win_c/update/update_receipt.json'); win=packet_bindings(win_path,'eb1dfc4d2849205b7ddca2cc6f006031501770eb146a70076799e46266fbe08d')
    req(ff['task_ids']==win['task_ids']==[x['task_id'] for x in s1['pool_bindings']],'packet task order drift')
    code={
      'actor_wrapper':'scripts/run_e2_r17_actor_pool_first_fail_exact_replay.py',
      'runner':'scripts/run_e2_r17_first_fail_exact_replay.py',
      'preflight':'scripts/preflight_e2_r17_first_fail_exact_replay.py',
      'authorizer':'scripts/authorize_e2_r17_first_fail_exact_replay.py',
      'diagnostic_witness':'research_pipeline/e2_r17_diagnostic_witness.py',
      'provider_budget':'research_pipeline/e2_r17_provider_budget.py',
      'audit':'scripts/audit_e2_r17_first_fail_exact_replay_completion.py',
      'analysis_authorizer':'scripts/authorize_e2_r17_first_fail_exact_replay_analysis.py',
      'analyzer':'scripts/analyze_e2_r17_first_fail_exact_replay.py',
    }
    bound={k:{'path':v,'sha256':sha(ROOT/v)} for k,v in code.items()}
    payload={'schema_version':'1.0','artifact_type':'e2-r17-single-case-first-fail-exact-evidence-updater-replication-contract','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'FROZEN_E2_R17_SINGLE_CASE_FIRST_FAIL_EXACT_REPLAY','scientific_object':d['scientific_object'],'case_stream':'e1-tsr-00','arms':['win_c','first_fail'],'replicates':[1,2],'scientific_scope':{'new_learned_states':4,'heldout_units':72,'replicates':2},'authority':{'scientific_experiment':False,'exact_replay':False,'provider_io':False,'updater':False,'heldout_evaluation':False,'analyzer':False,'second_backbone':False,'public_benchmark':False,'e3_confirmation':False,'paper_promotion':False,'submission':False},'design':{'path':str(a.design.resolve().relative_to(ROOT)),'sha256':sha(a.design)},'parent_s1':parent,'parent_stability_analysis':d['parent_stability_analysis'],'pool_bindings':s1['pool_bindings'],'selector_freeze':s1['selector_freeze'],'exact_evidence':{'win_c':win,'first_fail':ff},'heldout_task_ids':s1['heldout_task_ids'],'initial_skill':s1['initial_skill'],'suite':s1['suite'],'mindmemos':s1['mindmemos'],'model_identity':s1['model_identity'],'updater_runtime':s1['updater_runtime'],'actor_runtime':s1['actor_runtime'],'updater':s1['updater'],'actor':s1['actor'],'renderer':s1['renderer'],'budget':s1['budget'],'env_file':s1['env_file'],'bound_code':bound,'run_root':'/data/wyt/e2-r17-search-projection/runs/single-case-first-fail-exact-replay-20260902','lineage_lease_path':'/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-single-case-first-fail-exact-replay-v1.json','outcome_embargo':{'before_72_heldout':True,'partial_effect_read':False,'analyzer_authorized':False},'replication_gate':d['replication_gate'],'git_commit_at_freeze':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}; atomic(a.output,payload); print(json.dumps({'status':payload['status'],'sha256':sha(a.output),'new_learned_states':4,'heldout':72},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
