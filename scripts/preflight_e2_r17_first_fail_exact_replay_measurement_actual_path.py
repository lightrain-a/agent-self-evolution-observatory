#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.run_e2_r17_deepseek_v2_repair2_continuation_v2 import load_json,require,sha_file
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
def atomic(p:Path,d:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); os.replace(t,p)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--contract',type=Path,required=True); ap.add_argument('--rep1-authorization',type=Path,required=True); ap.add_argument('--rep2-authorization',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); require(not a.output.exists(),'measurement actual-path preflight exists')
 c=load_json(a.contract); require(c.get('status')=='FROZEN_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT','contract drift'); root=Path(c['preflight_root']); require(not root.exists(),'measurement preflight root must be fresh'); root.mkdir(parents=True)
 actor_python,actor_env=validate_actor_runtime({'runtime':c['actor_runtime']}); actor_env['LITELLM_LOCAL_MODEL_COST_MAP']='True'; identity=ROOT/c['model_identity']['path']; require(identity.is_file() and sha_file(identity)==c['model_identity']['sha256'],'identity drift'); task=c['heldout_task_ids'][0]; results=[]
 for auth_path in (a.rep1_authorization,a.rep2_authorization):
  auth=load_json(auth_path); require(auth.get('status')=='PREFLIGHT_ONLY_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT','preflight auth drift'); group=auth['group']; states=auth['execution_scope']['learned_states']
  for state in states:
   arm=state['arm']; unit=root/group/arm; ledger=unit/'provider_budget.sqlite3'; out=unit/'preflight.json'; unit.mkdir(parents=True,exist_ok=True)
   cmd=[str(actor_python),str(ROOT/'scripts/run_e2_r17_actor_pool_first_fail_exact_replay_measurement.py'),'--env-file',c['env_file'],'--suite-root',c['suite']['root'],'--mindmemos-root',c['mindmemos']['root'],'--run-root',str(unit/'actor'),'--identity',str(identity),'--authorization',str(auth_path.resolve()),'--skill-source',str(Path(state['skill_post_path']).parent),'--updater-receipt',state['update_receipt_path'],'--mode','e1','--model',c['actor']['requested_model'],'--task-id',task,'--k','1','--prefix-ks','1','--max-turns',str(c['actor']['max_turns']),'--max-output-tokens',str(c['actor']['max_output_tokens']),'--concurrency','1','--provider-budget-ledger',str(ledger),'--provider-total-call-limit','191','--provider-per-unit-call-limit','11','--stop-before-provider-io','--output',str(out)]
   r=subprocess.run(cmd,cwd=ROOT,env=actor_env,capture_output=True,text=True); require(r.returncode==0,f'actual-path preflight failed {group}/{arm}: {r.stderr[-2000:]}'); require(out.is_file(),'preflight output missing'); d=load_json(out); require(d.get('status')=='STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO' and d.get('provider_calls')==0 and d.get('provider_claims')==0,'preflight crossed provider boundary'); results.append({'group':group,'arm':arm,'output_path':str(out),'output_sha256':sha_file(out),'provider_calls':0})
 payload={'schema_version':'1.0','artifact_type':'e2-r17-first-fail-exact-replay-measurement-actual-path-preflight','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_ACTUAL_PATH_ZERO_PROVIDER','contract_path':str(a.contract),'contract_sha256':sha_file(a.contract),'rep1_preflight_authorization_sha256':sha_file(a.rep1_authorization),'rep2_preflight_authorization_sha256':sha_file(a.rep2_authorization),'results':results,'provider_calls':0,'scientific_outcomes_read':False,'next_gate':'MINT_TWO_MEASUREMENT_ONLY_AUTHORIZATIONS'}; atomic(a.output,payload); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
