from __future__ import annotations

import argparse, json, os, subprocess
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import evaluate_arm_from_materialized_state, prepare_appworld_runtime_root
from research_pipeline.agent_constraint_externality_capability_execute import capability_gate
from research_pipeline.agent_constraint_externality_codingplan_mcp_harness import MODEL, PROVIDER, PROVIDER_URI, TOOL_CALL_CAP, MAX_ROUNDS, MAX_OUTPUT_TOKENS, CONTEXT_WINDOW, RETRY_MAX_ATTEMPTS, setup_episode, run_atomcode, rows as event_rows, receipts
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, AppendOnlyLedger, EpisodeUnit, RunnerError, sha256_file, sha256_value
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT=Path(__file__).resolve().parents[1]; G=ROOT/'generated'
BUNDLE=G/'agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle'
QUAL=G/'agent-constraint-externality-codingplan-qwen38-mcp-provider-qualification-m1-20260902.json'
VOID=G/'agent-constraint-externality-codingplan-qwen38-c1-use-skill-void-20260902.json'
ADD=G/'agent-constraint-externality-codingplan-qwen38-mcp-capability-addendum-m1-20260902.json'
RESULT=G/'agent-constraint-externality-codingplan-qwen38-mcp-capability-result-m1-20260902.json'
EXEC='CODINGPLAN-QWEN38-MCP-CAPABILITY-M1'; FAMILIES=('ACE-FG-05','ACE-FG-06','ACE-TNF-05','ACE-TNF-06')
PREFIX=("This is a controlled AppWorld benchmark episode. Use only tools whose names start with mcp__ace__. "
        "All other AtomCode tools are outside the scientific harness and are blocked. When several independent AppWorld calls are useful, issue them in parallel in the same model turn to reduce request count. "
        "Do not use skills, shell, coding filesystem tools, web, subagents, or scheduling tools. Stop as soon as the benchmark task is complete.\n\nBenchmark task:\n")

def read(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def jrows(p:Path): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()] if p.exists() else []
def write(p:Path,d:dict[str,Any]): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def units():
    xs=[EpisodeUnit(namespace='capability',key=(MODEL+'@codingplan-mcp-v1',f,r),stage='CODINGPLAN_QWEN38_MCP_CAPABILITY_M1',family_id=f,repeat=r) for f in FAMILIES for r in (1,2)]
    if len(xs)!=8 or len({x.unit_id for x in xs})!=8: raise RunnerError('MCP M1 panel invalid.')
    return xs

def append_measurement(path:Path,d:dict[str,Any]):
    if any(x.get('unit_id')==d['unit_id'] for x in jrows(path)): raise RunnerError('Duplicate MCP measurement.')
    d=dict(d); d['content_sha256']=sha256_value(d)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf-8') as h: h.write(json.dumps(d,ensure_ascii=False,sort_keys=True)+'\n'); h.flush(); os.fsync(h.fileno())

def check_measurements(path:Path):
    xs=jrows(path); seen=set()
    for d in xs:
        c=d.get('content_sha256'); u=dict(d); u.pop('content_sha256',None)
        if c!=sha256_value(u): raise RunnerError('MCP measurement hash mismatch.')
        if d['unit_id'] in seen: raise RunnerError('Duplicate MCP measurement unit.')
        seen.add(d['unit_id'])
    return xs

def execute(appworld_root:Path,runtime:Path,ledger_path:Path,measure_path:Path,auth:Path):
    spec=load_protected_spec(BUNDLE); fams={x['family_id']:x for x in spec['families']}; ledger=AppendOnlyLedger(ledger_path)
    for unit in units():
        if unit.unit_id in ledger.states(): raise RunnerError('Refusing MCP M1 replay: '+unit.unit_id)
        fam=fams[unit.family_id]; arm=next(x for x in fam['arms'] if x['coupling_level']=='LOW')
        ep=runtime/'episodes'/unit.unit_id.replace(':','_').replace('|','_'); app_rt=ep/'appworld'; task='acecpmcp'+unit.family_id.lower().replace('-','')+f'r{unit.repeat}_1'; exp='ace-codingplan-qwen38-mcp-m1'; seed=4100+int(unit.repeat or 0)
        mat=prepare_appworld_runtime_root(appworld_root,app_rt,family=fam,arm=arm,task_id=task)
        home,work,state_path,audit_path=setup_episode(episode_root=ep,prepared_runtime=app_rt,task_id=task,experiment=exp,family_id=unit.family_id,seed=seed,apps=list(fam['fixture']['apps']),snapshot_sha=mat['initial_snapshot_sha256'],instruction_sha=mat['instruction_sha256'],auth_source=auth)
        prompt=PREFIX+arm['task_instruction']
        ledger.dispatch(unit,prompt_sha256=sha256_value(prompt),snapshot_sha256=mat['initial_snapshot_sha256'],repair_sha256=None,requested_model=MODEL,provider=PROVIDER,base_url=PROVIDER_URI)
        try: cp=run_atomcode(config=ep/'atomcode-config.toml',home=home,work=work,prompt=prompt,timeout=900)
        except subprocess.TimeoutExpired as exc:
            ledger.fail(unit,failure_class='ProviderCallError',message='CodingPlan MCP AtomCode timeout; no retry.',receipts=[]); raise RunnerError('CodingPlan MCP timeout; STOP.') from exc
        (ep/'atomcode.jsonl').write_text(cp.stdout,encoding='utf-8'); (ep/'atomcode.stderr.log').write_text(cp.stderr,encoding='utf-8')
        ev=event_rows(cp.stdout)
        try: rec=receipts(unit.unit_id,ev)
        except Exception as exc: ledger.fail(unit,failure_class='ProviderCallError',message=str(exc),receipts=[]); raise
        started=[str(x.get('name','')) for x in ev if x.get('type')=='tool.started']
        if any(not x.startswith('mcp__ace__') for x in started):
            ledger.fail(unit,failure_class='ProviderCallError',message='Non-ACE tool executed despite gate.',receipts=rec); raise RunnerError('Tool isolation failed; STOP.')
        audit=jrows(audit_path); denied=[x for x in audit if not x.get('allowed')]
        if not state_path.exists(): ledger.fail(unit,failure_class='ProviderCallError',message='MCP state absent.',receipts=rec); raise RunnerError('MCP state absent; STOP.')
        state=read(state_path)
        if state.get('status')!='CLOSED': ledger.fail(unit,failure_class='ProviderCallError',message='MCP server not cleanly closed.',receipts=rec); raise RunnerError('MCP close invalid; STOP.')
        evaluation=evaluate_arm_from_materialized_state(arm=arm,source_db_root=Path(state['source_db_root']),changes_db_root=Path(state['changes_db_root']),measurement_db_root=ep/'measurement-final')
        errs=[x for x in ev if x.get('type')=='error']; maxround=any('max rounds' in str(x.get('message','')).lower() for x in errs); other=[x for x in errs if 'max rounds' not in str(x.get('message','')).lower()]
        if other:
            ledger.fail(unit,failure_class='ProviderCallError',message='AtomCode runtime error: '+str(other[-1].get('message',''))[:300],receipts=rec); raise RunnerError('CodingPlan MCP runtime error; STOP.')
        complete=(cp.returncode==0 and not maxround and not bool(state.get('cap_reached')))
        m={'schema_version':'ace-codingplan-qwen38-mcp-measurement-m1-v1','object_id':OBJECT_ID,'execution_id':EXEC,'unit_id':unit.unit_id,'family_id':unit.family_id,'repeat':unit.repeat,'tool_loop_completed':complete,'target_success':bool(evaluation['target_success']),'non_target_preservation':float(evaluation['non_target_preservation']),'malformed_tool_calls':0,'appworld_tool_call_count':int(state.get('tool_call_count',0)),'tool_call_cap':TOOL_CALL_CAP,'cap_reached':bool(state.get('cap_reached')),'codingplan_request_count':len(rec),'denied_non_ace_tool_attempt_count':len(denied),'started_ace_tool_count':len(started),'normal_atomcode_exit':cp.returncode==0,'max_rounds_reached':maxround,'initial_snapshot_sha256':mat['initial_snapshot_sha256'],'instruction_sha256':mat['instruction_sha256']}
        append_measurement(measure_path,m)
        safe={'evaluation':{'target_success':m['target_success'],'non_target_preservation':m['non_target_preservation']},'tool_loop_completed':complete,'appworld_tool_call_count':m['appworld_tool_call_count'],'codingplan_request_count':len(rec),'denied_non_ace_tool_attempt_count':len(denied)}
        if complete: ledger.complete(unit,receipts=rec,result=safe)
        else: ledger.fail(unit,failure_class='RunnerError',message='Capability loop incomplete at frozen AppWorld/request headroom boundary.',receipts=rec)
    ledger.assert_all_terminal(units())

def adjudicate(ledger_path:Path,measure_path:Path):
    ledger=AppendOnlyLedger(ledger_path); ledger.assert_all_terminal(units()); ms=check_measurements(measure_path)
    if len(ms)!=8: raise RunnerError('Need eight MCP measurements.')
    gate=capability_gate([{'tool_loop_completed':bool(x['tool_loop_completed']),'target_success':bool(x['target_success']),'non_target_preservation':float(x['non_target_preservation']),'malformed_tool_calls':0} for x in ms])
    terms=[x for x in ledger.rows() if x['event'] in {'COMPLETION','FAILURE'}]; req=inp=out=cache=0
    for t in terms:
        for r in t.get('provider_receipts',[]):
            if r.get('provider')!=PROVIDER or r.get('resolved_model')!=MODEL: raise RunnerError('Receipt identity drift.')
            u=r.get('usage',{}); req+=int(u.get('codingplan_requests',1)); inp+=int(u.get('input_tokens',0)); out+=int(u.get('output_tokens',0)); cache+=int(u.get('cached_tokens',0))
    d={'schema_version':'ace-codingplan-qwen38-mcp-capability-result-m1-v1','object_id':OBJECT_ID,'execution_id':EXEC,'status':gate['verdict'],'gate':gate,'provider':PROVIDER,'resolved_model':MODEL,'context_window':CONTEXT_WINDOW,'max_output_tokens':MAX_OUTPUT_TOKENS,'retry_max_attempts':RETRY_MAX_ATTEMPTS,'valid_capability_measurements':8,'codingplan_request_total':req,'request_efficiency':{'requests_per_episode':req/8.0,'user_reported_rolling_window_limit':500,'fraction_of_one_window':req/500.0,'max_frozen_requests_per_episode':MAX_ROUNDS},'token_usage':{'input_tokens':inp,'output_tokens':out,'cached_tokens':cache},'runtime_diagnostics':{'total_appworld_tool_calls':sum(int(x['appworld_tool_call_count']) for x in ms),'total_denied_non_ace_tool_attempts':sum(int(x['denied_non_ace_tool_attempt_count']) for x in ms),'completed_agent_loops':sum(bool(x['tool_loop_completed']) for x in ms)},'scientific_outcomes_observed':0,'f0_executed':False,'authority':{'f0':False,'p1':False,'toolsandbox':False,'paper_claim':False},'ledger_sha256':sha256_file(ledger_path),'measurement_ledger_sha256':sha256_file(measure_path),'mcp_provider_qualification_sha256':sha256_file(QUAL),'addendum_sha256':sha256_file(ADD),'json_c1_void_sha256':sha256_file(VOID)}; d['content_sha256']=sha256_value(d); return d

def main():
    p=argparse.ArgumentParser(); p.add_argument('--execute',action='store_true'); p.add_argument('--adjudicate-only',action='store_true'); p.add_argument('--appworld-root',type=Path,default=ROOT/'cache/substrates/appworld-official-20260831'); p.add_argument('--runtime-root',type=Path,default=ROOT/'runtimes/agent-constraint-externality-codingplan-qwen38-mcp-capability-m1-20260902'); p.add_argument('--auth-source',type=Path,default=Path.home()/'.atomcode/auth.toml'); p.add_argument('--result-output',type=Path,default=RESULT); a=p.parse_args(); led=a.runtime_root/'ledger.jsonl'; meas=a.runtime_root/'measurements.jsonl'
    if not ADD.exists() or read(ADD).get('status')!='CODINGPLAN_QWEN38_MCP_NATIVE_CAPABILITY_M1_AUTHORIZED': raise RunnerError('MCP M1 addendum absent/not authorized.')
    if a.execute: execute(a.appworld_root,a.runtime_root,led,meas,a.auth_source)
    d=adjudicate(led,meas); write(a.result_output,d); print(json.dumps({'status':d['status'],'codingplan_requests':d['codingplan_request_total'],'requests_per_episode':d['request_efficiency']['requests_per_episode'],'f0_authorized':False},sort_keys=True))
if __name__=='__main__': main()
