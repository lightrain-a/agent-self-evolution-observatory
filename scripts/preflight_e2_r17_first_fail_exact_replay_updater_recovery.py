#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_diagnostic_witness import build_four_arm_evidence
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json,require,sha_file
from scripts.run_e2_r17_v31_provider_runtime_pilot import validate_updater_runtime
def atomic(p:Path,d:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); require(not a.output.exists(),'recovery preflight exists')
 c=load_json(a.contract); require(c.get('status')=='FROZEN_E2_R17_FIRST_FAIL_EXACT_REPLAY_UPDATER_RECOVERY_V2','contract drift'); require(not any((c.get('authority') or {}).values()),'contract grants authority'); require(not Path(c['run_root']).exists() and not Path(c['lineage_lease_path']).exists(),'recovery root/lease exists')
 for label,item in c['bound_code'].items(): p=ROOT/item['path']; require(p.is_file() and sha_file(p)==item['sha256'],f'bound code drift {label}')
 updater,_=validate_updater_runtime({'runtime':c['updater_runtime'],'mindmemos':c['mindmemos']}); require(updater.is_file(),'updater runtime absent'); mind=Path(c['mindmemos']['root']); require(subprocess.check_output(['git','-C',str(mind),'rev-parse','HEAD'],text=True).strip()==c['mindmemos']['commit'],'MindMemOS drift')
 pools=[]
 for row in c['pool_bindings']:
  p=Path(row['path']); require(p.is_file() and sha_file(p)==row['sha256'],f'pool drift {row["task_id"]}'); pools.append(load_frozen_pool(p))
 freeze=load_json(ROOT/c['selector_freeze']['path']); units,_=build_four_arm_evidence(pools,selector_freeze=freeze,final_block_cap_tokens=int(c['renderer']['final_block_cap_tokens']),transcript_max_chars=int(c['updater']['transcript_max_chars']))
 for arm in ('win_c','first_fail'): require([u.evidence_sha256 for u in units[arm]]==c['exact_evidence'][arm]['evidence_sha256s'],f'exact evidence drift {arm}')
 payload={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-updater-recovery-preflight','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_FIRST_FAIL_EXACT_REPLAY_UPDATER_RECOVERY_ZERO_PROVIDER_PREFLIGHT','contract_path':str(a.contract),'contract_sha256':sha_file(a.contract),'provider_calls':0,'scientific_outcomes_read':False,'exact_evidence_identity_pass':True,'rep1_preserved':True,'rep2_updaters_never_started':True,'next_gate':'MINT_UPDATER_RECOVERY_V2_AUTHORIZATION'}; atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
