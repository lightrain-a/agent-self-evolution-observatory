#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

def sha(p:Path|str)->str: return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p:Path|str): return json.loads(Path(p).read_text(encoding='utf-8'))
def req(x:bool,msg:str):
    if not x: raise RuntimeError(msg)
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--candidate',type=Path,required=True); ap.add_argument('--runner-entry-preflight',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 req(not a.output.exists(),'repair1 execution authorization exists')
 c=load(a.candidate); p=load(a.runner_entry_preflight)
 req(c['status']=='CANDIDATE_E2_R18_DIAGNOSTIC_VALUE_STAGE_A_REPAIR1','candidate status'); req(p['status']=='PASS_R18_STAGE_A_REPAIR1_RUNNER_ENTRY_BEFORE_GLOBAL_LEASE','runner-entry preflight status'); req(p['candidate_authorization_sha256']==sha(a.candidate),'candidate/preflight drift'); req(p['provider_calls']==0 and p['provider_claims']==0,'preflight crossed provider boundary')
 out=dict(c); out['artifact_type']='e2-r18-stage-a-repair1-execution-authorization'; out['created_at_utc']=datetime.now(timezone.utc).isoformat(timespec='seconds'); out['status']='AUTHORIZED_E2_R18_DIAGNOSTIC_VALUE_STAGE_A'; out['runner_entry_preflight_path']=str(a.runner_entry_preflight); out['runner_entry_preflight_sha256']=sha(a.runner_entry_preflight); out['single_use']=True; out['authorized_runs']=1; out['repair_scope']='authorization schema only: add exact runtime python/freeze/qualification bindings; no scientific variable changed'
 a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
