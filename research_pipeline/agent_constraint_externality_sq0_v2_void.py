from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT=Path(__file__).resolve().parents[1]
GENERATED=ROOT/'generated'
LEDGER=ROOT/'runtimes/agent-constraint-externality-sq0-v2-mimo25pro-20260903/ledger.jsonl'
CONTRACT=GENERATED/'agent-constraint-externality-sq0-v2-mimo25pro-execution-contract-20260903.json'
OUTPUT=GENERATED/'agent-constraint-externality-sq0-v2-harness-contamination-void-20260903.json'

def build()->dict[str,Any]:
    rows=[json.loads(x) for x in LEDGER.read_text().splitlines() if x.strip()]
    if len(rows)!=2 or [r['event'] for r in rows]!=['DISPATCH','FAILURE']:
        raise RuntimeError('SQ0-V2 failed-at-first-dispatch ledger shape drifted.')
    d,f=rows
    if d['unit_id']!='sq0v2:mimo-v2.5-pro|SQ0V2-FG-01|1' or f['unit_id']!=d['unit_id']:
        raise RuntimeError('SQ0-V2 affected unit drifted.')
    if f.get('failure_class')!='HARNESS_OR_PROVIDER_INTERFACE_STOP' or f.get('message')!='read_file':
        raise RuntimeError('SQ0-V2 contamination signature drifted.')
    if int(d['codingplan_window_before']['used'])!=167 or int(f['codingplan_window_after']['used'])!=168:
        raise RuntimeError('SQ0-V2 interface-cost accounting drifted.')
    contract=json.loads(CONTRACT.read_text()); claimed=contract['content_sha256']; u=dict(contract); u.pop('content_sha256')
    if claimed!=sha256_value(u) or contract.get('status')!='SQ0_V2_MIMO25PRO_EXECUTION_AUTHORIZED':
        raise RuntimeError('SQ0-V2 contract is not frozen/valid.')
    x={'schema_version':'ace-sq0-v2-harness-contamination-void-v1','object_id':OBJECT_ID,'status':'SQ0_V2_VOID_NATIVE_READ_FILE_SCHEMA_CONTAMINATION','execution_id':'CODINGPLAN-MIMO25PRO-SQ0-TARGET-FAILURE-V2','affected_unit':d['unit_id'],'affected_case_id':'SQ0V2-FG-01','ledger_sha256':sha256_file(LEDGER),'execution_contract_content_sha256':claimed,'failure_class':f['failure_class'],'observed_native_tool':'read_file','appworld_tool_calls_executed':0,'codingplan_account_window_requests_spent':1,'valid_sq0_v2_measurements':0,'scientific_difficulty_outcomes_observed':0,'retry':False,'replacement':False,'root_cause':{'classification':'ATOMCODE_NATIVE_TOOL_SCHEMA_CONTAMINATION','daemon_live_prepare_tools_hardcoded_true':True,'official_signed_binary_required':True,'public_source_rebuild_cannot_preserve_codingplan_signing':True,'direct_custom_tool_chat_surface_available':False},'disposition':'VOID_V2_ATTEMPT; DO_NOT REPLAY AFFECTED UNIT; REPLACE WITH FRESH V2-R1 CASE SET AND TRANSPORT-DISAMBIGUATED TASK SURFACE','authority':{'current_sq0_v2':False,'sq0_v2_r1_design':True,'sq0_v2_r1_execution':False,'f0_r1':False,'probe':False,'p1':False,'paper_claim':False}}
    x['content_sha256']=sha256_value(x); return x

def main()->None:
    x=build(); OUTPUT.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':x['status'],'valid_sq0_v2_measurements':0,'codingplan_requests_spent':1,'sq0_v2_r1_execution_authorized':False},sort_keys=True))
if __name__=='__main__': main()
