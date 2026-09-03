from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_live import EXEC_CONTRACT, RESULT_OUTPUT

ROOT=Path(__file__).resolve().parents[1]
GENERATED=ROOT/'generated'
OUTPUT=GENERATED/'agent-constraint-externality-sq0-v1-closeout-20260903.json'
LEDGER=ROOT/'runtimes/agent-constraint-externality-sq0-mimo25pro-v1-20260903/ledger.jsonl'

def read(path:Path)->dict[str,Any]: return json.loads(path.read_text())
def verified(path:Path,status:str)->dict[str,Any]:
 x=read(path)
 if x.get('object_id')!=OBJECT_ID or x.get('status')!=status: raise RuntimeError(f'identity/status mismatch: {path}')
 c=x.get('content_sha256'); u=dict(x); u.pop('content_sha256',None)
 if c!=sha256_value(u): raise RuntimeError(f'content hash mismatch: {path}')
 return x

def build()->dict[str,Any]:
 r=verified(RESULT_OUTPUT,'SQ0_TARGET_CHALLENGE_TOO_EASY_STOP'); c=verified(EXEC_CONTRACT,'SQ0_MIMO25PRO_V1_EXECUTION_AUTHORIZED')
 if r['case_count']!=12 or r['target_success_count']!=12 or r['usable_target_failure_count']!=0 or r['non_semantic_failure_units']!=[]: raise RuntimeError('SQ0 V1 aggregate drifted.')
 if r['ledger_sha256']!=sha256_file(LEDGER): raise RuntimeError('SQ0 V1 ledger hash drifted.')
 x={'schema_version':'ace-sq0-v1-closeout-v1','object_id':OBJECT_ID,'status':'SQ0_V1_TOO_EASY_CLOSEOUT','verdict':r['status'],'result_artifact':str(RESULT_OUTPUT.relative_to(ROOT)),'result_content_sha256':r['content_sha256'],'result_file_sha256':sha256_file(RESULT_OUTPUT),'execution_contract_content_sha256':c['content_sha256'],'ledger_sha256':r['ledger_sha256'],'case_count':12,'target_success_count':12,'usable_target_failure_count':0,'usable_target_failure_rate':0.0,'non_semantic_failure_count':0,'scientific_model_round_count':r['scientific_model_round_count'],'appworld_tool_call_total':r['appworld_tool_call_total'],'prompt_tokens_total':r['prompt_tokens_total'],'completion_tokens_total':r['completion_tokens_total'],'interpretation':'V1 is a valid development qualification result: the single-layer routing challenge is too easy for MiMo 2.5 Pro. It provides no F0 mechanism evidence.','reuse_rule':'V1 cases are permanently excluded from SQ0-V2 and confirmatory F0-R1.','scientific_effects_observed':0,'authority':{'current_sq0':False,'sq0_v2_design':True,'sq0_v2_execution':False,'f0_r1':False,'probe':False,'p1':False,'paper_claim':False}}
 x['content_sha256']=sha256_value(x); return x

def main()->None:
 x=build(); OUTPUT.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':x['status'],'usable_target_failure_rate':0.0,'scientific_model_round_count':x['scientific_model_round_count'],'sq0_v2_execution_authorized':False},sort_keys=True))
if __name__=='__main__': main()
