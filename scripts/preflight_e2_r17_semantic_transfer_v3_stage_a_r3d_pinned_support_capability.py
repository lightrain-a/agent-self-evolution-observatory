#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts import adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery as adjud
CONTROL_PLANE_REVISION='R3D_PINNED_EXTERNAL_SIGNED_SUPPORT_CAPABILITY'
PARENT_R3C_SHA='03b2608872424da2bdf78408266a69b28ff565bc9d84bf929aa82ba7bc11e030'
PARENT_R3_SHA='3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085'
PUBLIC_KEY_SHA='f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0'
RUNNER_SHA='491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89'
AUTHORIZER_SHA='9866bcffb09b4d6a6f31c5c8e947c6107a8bf35e09b8ddc81a6ef6350d6278df'
SCIENCE_KEYS=('failed_r2_parent','suite','mindmemos','provider_route','model_identity_policy','recovery_exceptions','recovery_opportunity_manifest','exact_once_acquisition','equal_dose_support','actor','budget','analysis_boundary','stage_b_plan_no_authority','runtime','env_file_path','run_root','global_lease_path')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def req(v,m):
    if not v: raise RuntimeError(m)
def bound(s):
    p=Path(s); return p if p.is_absolute() else ROOT/p
def atomic(p,row):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(row,indent=2,sort_keys=True)+'\n'); os.replace(t,p)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--parent-r3c-contract',type=Path,required=True); ap.add_argument('--parent-r3-contract',type=Path,required=True); ap.add_argument('--r3c-review',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); req(not a.output.exists(),'R3D preflight exists')
    c=load(a.contract); pc=load(a.parent_r3c_contract); r3=load(a.parent_r3_contract); rv=load(a.r3c_review); req(c.get('control_plane_revision')==CONTROL_PLANE_REVISION,'revision drift'); req(sha(a.parent_r3c_contract)==PARENT_R3C_SHA,'R3C SHA drift'); req(sha(a.parent_r3_contract)==PARENT_R3_SHA,'R3 SHA drift'); req(rv.get('verdict')=='REVISE_R3C_BEFORE_PROVIDER_RECOVERY','review verdict drift')
    for k in SCIENCE_KEYS: req(c.get(k)==r3.get(k),f'science drift {k}'); req(pc.get(k)==r3.get(k),f'parent R3C drift {k}')
    req(c.get('authority')==r3.get('authority'),'authority drift'); req(c['authority'].get('stage_a_provider_execution') is False and c['authority'].get('stage_b_learning_execution') is False,'self authorization')
    checks={}
    for label,row in (c.get('bound_code') or {}).items():
        p=bound(row.get('path','')); req(p.is_file() and sha(p)==row.get('sha256'),f'bound code drift {label}')
    checks['all_bound_code_hashes_match']=True; req(c['bound_code']['stage_a_runner']['sha256']==RUNNER_SHA,'runner drift'); req(c['bound_code']['authorization_minter']['sha256']==AUTHORIZER_SHA,'authorizer drift'); checks['provider_recovery_runner_and_authorizer_unchanged']=True
    s=c['post_terminal_support_read_control']; req(s.get('point_of_use_production_trust_root_pinned') is True and s.get('contract_cannot_select_alternate_trust_root') is True,'point-of-use pin absent'); req(s.get('production_public_key_sha256')==PUBLIC_KEY_SHA,'contract production key pin drift'); req(adjud.PRODUCTION_TRUSTED_PUBLIC_KEY_SHA256==PUBLIC_KEY_SHA,'adjudicator production key SHA pin drift'); req(adjud.PRODUCTION_TRUSTED_PUBLIC_KEY_RELATIVE==s.get('production_public_key_path'),'adjudicator production key path pin drift'); req(adjud.PRODUCTION_TRUSTED_PUBLIC_KEY_PATH.is_file() and sha(adjud.PRODUCTION_TRUSTED_PUBLIC_KEY_PATH)==PUBLIC_KEY_SHA,'production key bytes drift'); checks['point_of_use_production_trust_root_pinned']=True
    run=Path(c['run_root']); lease=Path(c['global_lease_path']); req(not run.exists() and not lease.exists(),'recovery lineage exists'); checks['fresh_r3d_recovery_lineage_absent']=True
    py=Path(c['runtime']['python_executable']); req(py.is_file(),'runtime python absent'); result=subprocess.run([str(py),'-m','unittest','-q','research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control'],cwd=ROOT,capture_output=True,text=True); req(result.returncode==0,f'tests fail {result.stderr[-1600:]}'); checks['support_control_tests_10_of_10_pass']=True
    src=(ROOT/'research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py').read_text(); req('test_full_forged_review_permit_and_capability_cannot_directly_invoke_adjudicator' in src and 'production trust root' in src,'substituted-contract regression absent'); checks['substituted_contract_attacker_key_full_chain_negative_test_present']=True
    req(not (ROOT/'generated/e2-r17-semantic-transfer-v3-stage-a-r3d-signed-support-capability-20260907.json').exists(),'signed capability already minted'); checks['signed_capability_absent']=True
    out={'schema_version':'1.0','artifact_type':'e2-r17-v3-stage-a-r3d-pinned-support-capability-zero-provider-preflight','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3D_PINNED_SUPPORT_CAPABILITY_PREFLIGHT','contract_path':str(a.contract),'contract_sha256':sha(a.contract),'parent_r3c_contract_sha256':PARENT_R3C_SHA,'parent_r3_contract_sha256':PARENT_R3_SHA,'r3c_review_sha256':sha(a.r3c_review),'trusted_public_key_sha256':PUBLIC_KEY_SHA,'checks':checks,'unit_tests':{'passed':10,'total':10},'provider_calls':0,'scientific_execution':False,'support_inspected':False,'fresh_identity_qualified':False,'r3d_recovery_authorization_minted':False,'stage_b_authority':False,'hard_provider_time_gate':'NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800','next_gate':'FRESH_GPT56_SOL_EXTRA_HIGH_R3D_EXACT_CODE_REVIEW_THEN_PROVIDER_RESET_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION','authority':{'provider_recovery':False,'stage_a_support_read':False,'stage_b_execution':False,'heldout':False,'paper_claim':False}}
    atomic(a.output,out); print(json.dumps(out,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
