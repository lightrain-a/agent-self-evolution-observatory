from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import run_c1_pacta_20260830 as legacy
RUN=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v2-p0-shadow-policy-20260830-v1')
MODEL='doubao-seed-2.0-mini'; RESOLVED='doubao-seed-2-0-mini-260215'
def now(): return datetime.now(timezone.utc).isoformat()
def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); tmp.replace(path)
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def main():
 if git('status','--porcelain'): raise RuntimeError('support probe worktree must be clean and committed')
 prompt='NON-SCIENTIFIC PROVIDER SUPPORT PROBE. Return exactly this JSON object and no prose:\n{"current_state":{"next_goal":"Wait for the synthetic page."},"action":[{"wait":{"seconds":1}}]}'
 client,summary=legacy.client(); response,text=legacy.provider_call(client,prompt,120,0.2); signature,goal,recovered=legacy.parse_policy_output(text)
 passed=(response.get('requested_model')==MODEL and response.get('resolved_model')==RESOLVED and response.get('thinking_compatibility_fallback') is False and signature=='wait')
 result={'schema_version':'1.0','artifact_kind':'C1_PACTA_V2_NON_SCIENTIFIC_MODEL_SUPPORT','status':'SUPPORT_PASS' if passed else 'STOP_SUPPORT','scientific_state_used':False,'requested_model':response.get('requested_model'),'resolved_model':response.get('resolved_model'),'thinking':'disabled','thinking_compatibility_fallback':response.get('thinking_compatibility_fallback'),'temperature':0.2,'max_output_tokens':120,'provider_retries':0,'substitution':False,'schema_parse_pass':signature=='wait','action_signature':signature,'parse_recovered':recovered,'response_id':response.get('response_id'),'provider_status':response.get('status'),'raw_output':text,'usage':response.get('usage') or {},'provider_summary':summary,'execution_git_sha':git('rev-parse','HEAD'),'completed_at':now()}
 dump(RUN/'model-support.json',result); manifest=json.loads((RUN/'manifest.json').read_text(encoding='utf-8')); manifest.update({'status':result['status'],'support_probe_completed_at':result['completed_at']}); dump(RUN/'manifest.json',manifest)
 print(json.dumps({'status':result['status'],'requested':result['requested_model'],'resolved':result['resolved_model'],'schema_parse_pass':result['schema_parse_pass']})); return 0 if passed else 2
if __name__=='__main__': raise SystemExit(main())
