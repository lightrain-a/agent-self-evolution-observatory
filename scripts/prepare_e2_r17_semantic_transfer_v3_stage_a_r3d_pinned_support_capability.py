#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
CONTROL_PLANE_REVISION="R3D_PINNED_EXTERNAL_SIGNED_SUPPORT_CAPABILITY"
PARENT_R3C_SHA="03b2608872424da2bdf78408266a69b28ff565bc9d84bf929aa82ba7bc11e030"
PARENT_R3_SHA="3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085"
R3C_REVIEW_VERDICT="REVISE_R3C_BEFORE_PROVIDER_RECOVERY"
PUBLIC_KEY_REL="generated/e2-r17-r3c-support-signing-public-key-20260906.pem"
PUBLIC_KEY_SHA="f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def req(v:bool,m:str):
    if not v: raise RuntimeError(m)
def rel(p:Path)->str:
    p=p.resolve(); return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
def atomic(p:Path,row:dict[str,Any]):
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(row,indent=2,sort_keys=True)+'\n'); os.replace(t,p)
def bc(p:Path):return {'path':rel(p),'sha256':sha(p)}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--parent-r3c-contract',type=Path,required=True); ap.add_argument('--parent-r3-contract',type=Path,required=True); ap.add_argument('--r3c-review',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    req(not a.output.exists(),'R3D contract exists'); p=load(a.parent_r3c_contract); r3=load(a.parent_r3_contract); rv=load(a.r3c_review)
    req(sha(a.parent_r3c_contract)==PARENT_R3C_SHA,'R3C parent SHA drift'); req(sha(a.parent_r3_contract)==PARENT_R3_SHA,'R3 parent SHA drift'); req(rv.get('verdict')==R3C_REVIEW_VERDICT,'R3C review verdict drift'); req(rv.get('scientific_equivalence_to_parent_r3')=='PASS','R3C review science drift'); req(rv.get('provider_recovery_authority_affected') is False,'provider geometry invalidated'); req(rv.get('r3_contract_redesign_required') is False and rv.get('new_scientific_experiment_required') is False,'scientific redesign requested')
    out=copy.deepcopy(p); out['created_at_utc']=datetime.now(timezone.utc).isoformat(timespec='seconds'); out['control_plane_revision']=CONTROL_PLANE_REVISION; out['parent_r3c_contract']={'path':rel(a.parent_r3c_contract),'sha256':PARENT_R3C_SHA,'relationship':'control-plane-only successor hard-pinning production Ed25519 trust root at adjudicator point of use'}
    for key in list(out.get('bound_code') or {}):
        if key.startswith('r3c_'):
            del out['bound_code'][key]
    files={'equal_dose_adjudicator':ROOT/'scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py','post_terminal_support_minter':ROOT/'scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py','post_terminal_support_gate':ROOT/'scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py','post_terminal_support_tests':ROOT/'research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py','r3d_signed_capability_verifier':ROOT/'research_pipeline/e2_r17_r3c_signed_support_capability.py','r3d_external_capability_signer':ROOT/'scripts/sign_e2_r17_semantic_transfer_v3_stage_a_r3c_support_capability.py','r3d_contract_builder':Path(__file__).resolve(),'r3d_preflight':ROOT/'scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3d_pinned_support_capability.py'}
    for k,v in files.items(): req(v.is_file(),f'missing {k}'); out['bound_code'][k]=bc(v)
    reviews=copy.deepcopy(out.get('recovery_reviews') or {}); reviews['r3c_point_of_use_review']={'path':rel(a.r3c_review),'sha256':sha(a.r3c_review),'verdict':R3C_REVIEW_VERDICT}; out['recovery_reviews']=reviews
    c=copy.deepcopy(out.get('post_terminal_support_read_control') or {}); c.update({'control_plane_revision':CONTROL_PLANE_REVISION,'point_of_use_production_trust_root_pinned':True,'production_public_key_path':PUBLIC_KEY_REL,'production_public_key_sha256':PUBLIC_KEY_SHA,'contract_cannot_select_alternate_trust_root':True,'actual_support_read_authorization_minted':False,'actual_signed_capability_minted':False}); c['trusted_external_signer']={'algorithm':'Ed25519','signature_context':'E2-R17-R3D-POST-TERMINAL-SUPPORT-CAPABILITY-V1','public_key_path':PUBLIC_KEY_REL,'public_key_sha256':PUBLIC_KEY_SHA,'private_key_in_repository':False,'private_key_location_class':'external controller only; root-owned on host52'}; out['post_terminal_support_read_control']=c
    out['authority']=copy.deepcopy(r3['authority']); out['scientific_role']='R3D control-plane-only successor; parent R3 scientific geometry and provider execution universe unchanged'; out['next_gate']={'before_provider_reset':'FRESH_GPT56_SOL_EXTRA_HIGH_R3D_EXACT_CODE_REVIEW_ONLY_NO_PROVIDER_CALL','after_reset_and_r3d_pass':'EXACTLY_ONE_FRESH_DEEPSEEK_IDENTITY_THEN_LOCAL_ADJUDICATION_THEN_SEPARATE_R3D_RECOVERY_AUTHORIZATION','provider_recovery':'EXECUTE_ONLY_158_ORIGINAL_PROVIDER_TASKS_UNDER_R3D_CONTRACT','post_terminal':'MINT_STRUCTURAL_REQUEST_THEN_EXTERNAL_SIGNED_CAPABILITY_THEN_POINT_OF_USE_PIN_VERIFY_AND_CONSUME','stage_b':'SEPARATE_CONTRACT_REVIEW_AND_AUTHORITY_REQUIRED'}
    atomic(a.output,out); print(json.dumps({'control_plane_revision':CONTROL_PLANE_REVISION,'output':str(a.output),'output_sha256':sha(a.output),'provider_calls':0,'scientific_execution':False,'stage_b_authority':False},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
