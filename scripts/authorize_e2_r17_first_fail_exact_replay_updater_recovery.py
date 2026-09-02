#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json,require,sha_file
def atomic(p:Path,d:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(p)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--preflight',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); require(not a.output.exists(),'recovery auth exists')
 c=load_json(a.contract); p=load_json(a.preflight); csha=sha_file(a.contract); require(c.get('status')=='FROZEN_E2_R17_FIRST_FAIL_EXACT_REPLAY_UPDATER_RECOVERY_V2','contract drift'); require(p.get('status')=='PASS_FIRST_FAIL_EXACT_REPLAY_UPDATER_RECOVERY_ZERO_PROVIDER_PREFLIGHT' and p.get('contract_sha256')==csha and p.get('provider_calls')==0 and p.get('scientific_outcomes_read') is False,'preflight drift'); require(not Path(c['run_root']).exists() and not Path(c['lineage_lease_path']).exists(),'root/lease no longer fresh')
 d={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-updater-recovery-authorization','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'AUTHORIZED_E2_R17_FIRST_FAIL_EXACT_REPLAY_UPDATER_RECOVERY_V2','contract_path':str(a.contract),'contract_sha256':csha,'preflight_path':str(a.preflight),'preflight_sha256':sha_file(a.preflight),'mindmemos_commit':c['mindmemos']['commit'],'single_use':True,'authority':{'scientific_experiment':True,'provider_io':True,'updater':True,'heldout_evaluation':False,'analyzer':False,'second_backbone':False,'public_benchmark':False,'e3_confirmation':False,'paper_promotion':False,'submission':False},'execution_scope':{'phase':'updater_recovery_v2','replicate':2,'arms':['win_c','first_fail'],'new_learned_states':2,'heldout_units':0,'exact_evidence':c['exact_evidence'],'provider_budget':{'required':True,'total_limit':191,'per_unit_limit':11},'rep1_replay':False,'exactly_once':True,'automatic_retry':False,'lineage_lease_path':c['lineage_lease_path']},'interpretation_boundary':'Updater-only recovery for two never-started rep2 states after deterministic actor authorization-schema failure. No heldout, analyzer, S2/E3, paper, or submission authority.'}; atomic(a.output,d); print(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
