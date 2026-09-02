#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_diagnostic_witness import build_four_arm_evidence
from research_pipeline.e2_r17_mindmemos_ark_adapter import PLAN_BASE_URL
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import atomic_json, bind_mindmemos, load_json, require, sha_file, validate_updater_runtime
from scripts.run_e2_r17_first_fail_exact_replay import ensure_update
ARMS=('win_c','first_fail')
CONTRACT='FROZEN_E2_R17_FIRST_FAIL_EXACT_REPLAY_UPDATER_RECOVERY_V2'; AUTH='AUTHORIZED_E2_R17_FIRST_FAIL_EXACT_REPLAY_UPDATER_RECOVERY_V2'
def acquire(p:Path,csha:str,asha:str)->None:
 p.parent.mkdir(parents=True,exist_ok=True); d={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-updater-recovery-lease','status':'RUNNING_UPDATER_RECOVERY_V2','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'pid':os.getpid(),'contract_sha256':csha,'authorization_sha256':asha,'partial_effect_read':False}; fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600); os.write(fd,(json.dumps(d,sort_keys=True)+'\n').encode()); os.fsync(fd); os.close(fd)
def seal(p:Path,status:str)->None:
 d=load_json(p); d['status']=status; d['sealed_at_utc']=datetime.now(timezone.utc).isoformat(timespec='seconds'); atomic_json(p,d)
def main_validate(cp:Path,ap:Path)->tuple[dict[str,Any],str,str]:
 c=load_json(cp); a=load_json(ap); csha=sha_file(cp); asha=sha_file(ap); require(c.get('status')==CONTRACT,'recovery contract drift'); require(a.get('status')==AUTH and a.get('contract_sha256')==csha,'recovery auth drift'); au=a.get('authority') or {}; require(au.get('scientific_experiment') is True and au.get('updater') is True and au.get('provider_io') is True,'updater recovery authority absent'); require(au.get('heldout_evaluation') is False and au.get('analyzer') is False,'updater recovery overbroad'); return c,csha,asha
async def go(args:argparse.Namespace)->dict[str,Any]:
 c,csha,asha=main_validate(args.contract,args.authorization); lease=Path(c['lineage_lease_path']); acquire(lease,csha,asha); success=False
 try:
  updater_python,_=validate_updater_runtime({'runtime':c['updater_runtime'],'mindmemos':c['mindmemos']}); require(Path(sys.executable)==updater_python,'recovery must use updater runtime')
  pools=[]
  for row in c['pool_bindings']:
   p=Path(row['path']); require(p.is_file() and sha_file(p)==row['sha256'],f'pool drift {row["task_id"]}'); pools.append(load_frozen_pool(p))
  freeze=load_json(ROOT/c['selector_freeze']['path']); units,_=build_four_arm_evidence(pools,selector_freeze=freeze,final_block_cap_tokens=int(c['renderer']['final_block_cap_tokens']),transcript_max_chars=int(c['updater']['transcript_max_chars']))
  for arm in ARMS: require([u.evidence_sha256 for u in units[arm]]==c['exact_evidence'][arm]['evidence_sha256s'],f'exact evidence drift {arm}')
  mind=Path(c['mindmemos']['root']); head=subprocess.check_output(['git','-C',str(mind),'rev-parse','HEAD'],text=True).strip(); require(head==c['mindmemos']['commit'],'MindMemOS drift'); bind_mindmemos(mind)
  load_env_file(Path(c['env_file'])); raw=ArkSettings.from_env(required=True); require(raw.base_url.rstrip('/')==PLAN_BASE_URL,'non-Ark route'); settings=ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=300,max_retries=0)
  ident=load_json(ROOT/c['model_identity']['path']); m=ident['requested_and_resolved'][c['updater']['requested_model']]; requested=str(m['requested']); resolved=str(m['resolved']); require(resolved==c['updater']['resolved_model'],'model drift')
  init=Path(c['initial_skill']['path']); require(sha_file(init)==c['initial_skill']['sha256'],'initial skill drift'); initial=init.read_text(encoding='utf-8'); initial_sha=sha_file(init)
  run=Path(c['run_root']); require(not run.exists(),'recovery run root must be fresh'); run.mkdir(parents=True); out=[]
  for arm in ARMS:
   state=run/f'states/e1-tsr-00/replicate_2/{arm}'; u=await ensure_update(c=c,csha=csha,asha=asha,rep=2,arm=arm,pools=pools,units=units[arm],initial=initial,initial_sha=initial_sha,mind_head=head,requested=requested,resolved=resolved,settings=settings,state=state); out.append({'replicate':2,'arm':arm,'state_root':str(state),'skill_post_path':u['skill_post_path'],'skill_post_sha256':u['skill_post_sha256'],'update_receipt_path':u['update_receipt_path'],'update_receipt_sha256':u['update_receipt_sha256'],'provider_calls':u['provider_calls']})
  summary={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-updater-recovery-summary','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'COMPLETED_UPDATER_RECOVERY_V2','contract_sha256':csha,'authorization_sha256':asha,'replicate':2,'states':out,'new_learned_states':2,'heldout_rollout_units':0,'scientific_outcomes_read':False,'partial_effect_read':False,'analyzer_run':False}; atomic_json(run/'summary/updater_recovery_summary.json',summary); success=True; return summary
 finally:
  if lease.exists(): seal(lease,'COMPLETED_UPDATER_RECOVERY_V2' if success else 'FAIL_CLOSED_UPDATER_RECOVERY_V2')
def main()->int:
 p=argparse.ArgumentParser(); p.add_argument('--contract',type=Path,required=True); p.add_argument('--authorization',type=Path,required=True); a=p.parse_args(); print(json.dumps(asyncio.run(go(a)),ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
