from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_codingplan_mcp_harness import (
    CONTEXT_WINDOW, MAX_OUTPUT_TOKENS, MAX_ROUNDS, MODEL, PROFILE, PROVIDER,
    RETRY_MAX_ATTEMPTS, TOOL_CALL_CAP,
)
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, RunnerError, sha256_file, sha256_value

ROOT=Path(__file__).resolve().parents[1]; G=ROOT/'generated'
ACTIVE=G/'agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle'
V4=G/'agent-constraint-externality-capability-substrate-v4-contract-20260902.json'
PLUS=G/'agent-constraint-externality-qwen37plus-capability-result-r5-partial-20260902.json'
QUAL=G/'agent-constraint-externality-codingplan-qwen38-mcp-provider-qualification-m1-20260902.json'
C1_LEDGER=ROOT/'runtimes/agent-constraint-externality-codingplan-qwen38-capability-c1-20260902/ledger.jsonl'
C1_LOG=ROOT/'runtimes/agent-constraint-externality-codingplan-qwen38-capability-c1-20260902/runner.log'
VOID=G/'agent-constraint-externality-codingplan-qwen38-c1-use-skill-void-20260902.json'
ADD=G/'agent-constraint-externality-codingplan-qwen38-mcp-capability-addendum-m1-20260902.json'
EXECUTION='CODINGPLAN-QWEN38-MCP-CAPABILITY-M1'; FAMILIES=['ACE-FG-05','ACE-FG-06','ACE-TNF-05','ACE-TNF-06']

def read(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def write(p:Path,d:dict[str,Any]): p.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def lines(p:Path): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]

def build_void()->dict[str,Any]:
    rs=lines(C1_LEDGER); ds=[x for x in rs if x['event']=='DISPATCH']; fs=[x for x in rs if x['event']=='FAILURE']
    if len(ds)!=1 or len(fs)!=1 or fs[0].get('failure_class')!='ProviderCallError': raise RunnerError('Unexpected JSON C1 ledger for void.')
    log=C1_LOG.read_text(encoding='utf-8',errors='replace')
    if 'use_skill' not in log or 'unknown or unmounted tool' not in log: raise RunnerError('Missing use_skill protocol witness.')
    d={'schema_version':'ace-codingplan-qwen38-json-c1-use-skill-void-v1','object_id':OBJECT_ID,'status':'CODINGPLAN_QWEN38_JSON_C1_VOID_ATOMCODE_USE_SKILL_PROTOCOL_LEAK','execution_id':'CODINGPLAN-QWEN38-27B-CAPABILITY-C1','affected_unit':ds[0]['unit_id'],'valid_capability_measurements':0,'codingplan_requests_spent_as_infrastructure_cost':1,'appworld_actions_executed':0,'retry':False,'replacement':False,'root_cause':{'classification':'ATOMCODE_CODING_PERSONA_NATIVE_TOOL_PROTOCOL_LEAK','observed_native_tool':'use_skill','observed_failure':'unknown or unmounted tool: use_skill','scientific_json_bridge_invalid':True},'disposition':'SUPERSEDED_BY_MCP_NATIVE_HARNESS; DO_NOT_REPLAY_JSON_C1','ledger_sha256':sha256_file(C1_LEDGER),'scientific_outcomes_observed':0,'f0_authorized':False}; d['content_sha256']=sha256_value(d); return d

def build_add()->dict[str,Any]:
    if read(V4).get('status')!='CAPABILITY_SUBSTRATE_V4_TOOL_BUDGET_QUALIFIED': raise RunnerError('V4 not qualified.')
    if read(PLUS).get('status')!='CAPABILITY_CALIBRATION_FAIL_CEILING_STOP': raise RunnerError('Plus ceiling not sealed.')
    if read(QUAL).get('status')!='CODINGPLAN_QWEN38_MCP_NATIVE_PROVIDER_QUALIFICATION_PASS': raise RunnerError('MCP provider not qualified.')
    if read(VOID).get('status')!='CODINGPLAN_QWEN38_JSON_C1_VOID_ATOMCODE_USE_SKILL_PROTOCOL_LEAK': raise RunnerError('JSON C1 not voided.')
    d={'schema_version':'ace-codingplan-qwen38-mcp-capability-addendum-m1-v1','object_id':OBJECT_ID,'execution_id':EXECUTION,'status':'CODINGPLAN_QWEN38_MCP_NATIVE_CAPABILITY_M1_AUTHORIZED','selection_boundary':'POST_QWEN37PLUS_CEILING_AND_POST_JSON_BRIDGE_INTERFACE_VOID','model':{'provider_profile':PROFILE,'resolved_model':MODEL,'provider_id':PROVIDER,'context_window':CONTEXT_WINDOW,'max_output_tokens':MAX_OUTPUT_TOKENS,'retry_max_attempts':RETRY_MAX_ATTEMPTS},'harness':{'surface':'ATOMCODE_NATIVE_MCP_APPWORLD_TOOLS','allowed_model_visible_prefix':'mcp__ace__','all_non_ace_tools_denied_by_pre_tool_hook':True,'direct_gateway_auth_bypass':False,'official_atomcode_binary':True,'max_rounds_per_episode':MAX_ROUNDS,'tool_call_cap':TOOL_CALL_CAP,'parallel_independent_calls_encouraged':True,'provider_qualification_sha256':sha256_file(QUAL),'json_c1_void_sha256':sha256_file(VOID)},'active_substrate':{'bundle_path':str(ACTIVE.relative_to(ROOT)),'bundle_sha256':sha256_file(ACTIVE),'v4_contract_sha256':sha256_file(V4)},'panel':{'family_ids':FAMILIES,'repeats':[1,2],'episodes':8,'reuse_other_model_measurements':False},'gate':{'tool_loop_completion_min':0.75,'target_success_min':0.50,'target_success_max':0.875,'non_target_preservation_min':0.85,'malformed_tool_calls_required':0},'request_budget':{'user_reported_rolling_window_limit':500,'max_requests_per_episode':MAX_ROUNDS,'max_requests_full_panel':MAX_ROUNDS*8,'token_amount_is_not_plan_limit':True},'authority':{'capability_m1':True,'f0':False,'p1':False,'toolsandbox':False,'paper_claim':False},'scientific_outcomes_observed':0}; d['content_sha256']=sha256_value(d); return d

def main():
    if VOID.exists() or ADD.exists(): raise SystemExit('Refusing overwrite of MCP M1 prepare artifacts.')
    v=build_void(); write(VOID,v); a=build_add(); write(ADD,a)
    print(json.dumps({'void':v['status'],'addendum':a['status'],'model':MODEL,'tool_call_cap':TOOL_CALL_CAP,'max_rounds':MAX_ROUNDS,'max_panel_requests':MAX_ROUNDS*8,'f0_authorized':False},sort_keys=True))
if __name__=='__main__': main()
