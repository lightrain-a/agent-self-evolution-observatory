from __future__ import annotations

import argparse, json, os, shutil, tempfile, time
from pathlib import Path
from typing import Any

import research_pipeline.agent_constraint_externality_sq0_v5_live as base
from research_pipeline.agent_constraint_externality_direct_sfq_a0_build import CONTRACT_OUTPUT as STATIC_CONTRACT, QUAL_OUTPUT as STATIC_QUAL, OUTPUT_BUNDLE, TOOL_CALL_CAP, load_cases
from research_pipeline.agent_constraint_externality_direct_sfq_a0_cases import evaluate_case_from_state
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT=Path(__file__).resolve().parents[1]; GENERATED=ROOT/'generated'
SELECTION=GENERATED/'agent-constraint-externality-capability-backbone-selection-final-20260903.json'
TRANSPORT=GENERATED/'agent-constraint-externality-sq0-v2r1-transport-result-20260903.json'
V5_CLOSEOUT=GENERATED/'agent-constraint-externality-sq0-v5-final-closeout-20260903.json'
APPWORLD_PYTHON=Path('/data/wyt/agent-self-evolution-observatory/worktrees/agent-constraint-externality-20260831/runtimes/appworld-constraint-externality-py312/bin/python')
MODEL_PROFILE='AtomGit-mimo-v2.5-pro'; MODEL_ID='mimo-v2.5-pro'; PROVIDER='ATOMGIT_CODINGPLAN_SIGNED_GATEWAY'; BASE_URL='https://llm-api.atomgit.com/v1'
MODEL_ROUND_CAP=56; CASE_COUNT=12; SHARED_RESERVE=100; MARGIN=5; MIN_REMAINING=MODEL_ROUND_CAP+SHARED_RESERVE+MARGIN
EXECUTION_ID='DIRECT-SFQ-A0-ATOMGIT-MIMO25PRO-20260906'
AUTH_OUTPUT=GENERATED/'agent-constraint-externality-direct-sfq-a0-atomgit-mimo25pro-human-authorization-20260906.json'
Q1_OUTPUT=GENERATED/'agent-constraint-externality-direct-sfq-a0-atomgit-mimo25pro-q1-predispatch-20260906.json'
EXEC_CONTRACT=GENERATED/'agent-constraint-externality-direct-sfq-a0-atomgit-mimo25pro-execution-contract-20260906.json'
RESULT_OUTPUT=GENERATED/'agent-constraint-externality-direct-sfq-a0-atomgit-mimo25pro-result-20260906.json'
OP_OUTPUT=GENERATED/'agent-constraint-externality-direct-sfq-a0-atomgit-mimo25pro-operational-state-20260906.json'
BRIDGE=ROOT/'research_pipeline/agent_constraint_externality_direct_sfq_atomgit_mcp_bridge.py'

class Stop(RuntimeError): pass
class QuotaHold(RuntimeError):
    def __init__(self,usage:dict[str,Any]): super().__init__('shared quota hold'); self.usage=usage

def readj(p:Path)->dict[str,Any]: return json.loads(p.read_text(encoding='utf-8'))
def writej(p:Path,x:dict[str,Any])->None: p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def verified(p:Path,status:str)->dict[str,Any]:
    x=readj(p)
    if x.get('object_id')!=OBJECT_ID or x.get('status')!=status: raise Stop(f'identity/status mismatch: {p}')
    c=x.get('content_sha256')
    if c:
        u=dict(x);u.pop('content_sha256',None)
        if c!=sha256_value(u): raise Stop(f'content hash mismatch: {p}')
    return x

def config()->str:
    return f'''default_provider = "{MODEL_PROFILE}"\ndefault_model = "{MODEL_PROFILE}"\nauto_update = false\nauto_commit = false\n[provider_accounts.AtomGit]\nprovider = "openai"\nbase_url = "{BASE_URL}"\n[models."{MODEL_PROFILE}"]\naccount = "AtomGit"\nmodel = "{MODEL_ID}"\ncontext_window = 1000000\nretry_max_attempts = 1\nsystem_prompt = "Complete the target-local Direct-SFQ-A0 AppWorld task using only mcp__appworld__ tools. Any ~/ path is virtual AppWorld state. Never use native host tools. Preserve unrelated state. Batch independent tool calls when safe."\n[loop_config]\nmax_rounds = {MODEL_ROUND_CAP}\n[coding]\nmax_rounds = {MODEL_ROUND_CAP}\nshell_guard_policy = "prompt"\n[tools.todo]\nenabled = false\n[ui]\nai_session_naming = false\n'''
def agents()->str: return '# Direct-SFQ-A0 AppWorld run\nUse only mcp__appworld__* tools. Any ~/ path is AppWorld virtual state. Never use native host tools. Preserve unrelated state.\n'
def mcp(case_id:str,root:Path,progress:Path,task_id:str)->dict[str,Any]:
    a=['-m','research_pipeline.agent_constraint_externality_direct_sfq_atomgit_mcp_bridge','--bundle',str(OUTPUT_BUNDLE),'--case-id',case_id,'--runtime-root',str(root/'appworld'),'--task-id',task_id,'--experiment-name','ace-direct-sfq-a0-atomgit-mimo25pro','--progress',str(progress),'--tool-call-cap',str(TOOL_CALL_CAP)]
    return {'mcpServers':{'appworld':{'command':str(APPWORLD_PYTHON),'args':a,'env':{'PYTHONPATH':str(ROOT)},'timeout_ms':30000,'trust':True}}}
def uid(case_id:str)->str: return f'directsfqa0:{MODEL_ID}|{case_id}|1'

def patch()->None:
    base.MODEL_PROFILE=MODEL_PROFILE; base.MODEL_ID=MODEL_ID; base.MODEL_ROUND_CAP=MODEL_ROUND_CAP; base.TOOL_CALL_CAP=TOOL_CALL_CAP; base.EXECUTION_ID=EXECUTION_ID
    base.OUTPUT_BUNDLE=OUTPUT_BUNDLE; base.load_cases=load_cases; base.evaluate_case_from_state=evaluate_case_from_state; base._config=config; base._agents=agents; base._mcp=mcp; base._unit_id=uid
    base._patch_live(); base.live.MODEL_PROFILE=MODEL_PROFILE; base.live.MODEL_ROUND_CAP=MODEL_ROUND_CAP; base.live.TOOL_CALL_CAP=TOOL_CALL_CAP

def inputs()->tuple[dict[str,Any],dict[str,Any],dict[str,Any],dict[str,Any],dict[str,Any]]:
    s=verified(STATIC_CONTRACT,'DIRECT_SFQ_A0_STATIC_DESIGN_READY_PROVIDER_CREDIT_BLOCKED'); q=verified(STATIC_QUAL,'DIRECT_SFQ_A0_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS_EXECUTION_BLOCKED')
    sel=verified(SELECTION,'CAPABILITY_BACKBONE_SELECTED_MIMO25PRO_PASS'); tr=verified(TRANSPORT,'SQ0_V2R1_TRANSPORT_QUALIFICATION_PASS'); v5=verified(V5_CLOSEOUT,'SQ0_V5_FINAL_CALIBRATION_INVALID_STOP_NO_V6')
    if sel.get('selected_backbone',{}).get('model_id')!=MODEL_ID: raise Stop('selected backbone drift')
    if s.get('case_count')!=12 or s.get('acceptable_final_failure_counts')!=[9,10] or s.get('protected_bundle',{}).get('sha256')!=sha256_file(OUTPUT_BUNDLE): raise Stop('Direct-SFQ static geometry drift')
    if q.get('contract_content_sha256')!=s.get('content_sha256') or q.get('private_fixture_ids_used') is not False: raise Stop('Direct-SFQ static qualification drift')
    if any((s.get('freshness_audit') or {}).get(k)!=0 for k in ('case_id_overlap_count','instruction_hash_overlap_count','fixture_hash_overlap_count','target_local_resource_hash_overlap_count')): raise Stop('Direct-SFQ freshness drift')
    if (s.get('development_lineage') or {}).get('sq0_v5_final_invalid_status_preserved') is not True or (v5.get('authority') or {}).get('sq0_v6') is not False: raise Stop('SQ0-V5 terminal lineage not preserved')
    if tr.get('native_tool_attempts')!=[] or tr.get('prohibited_tool') is not None: raise Stop('inherited MCP transport not clean')
    if not APPWORLD_PYTHON.is_file(): raise Stop('AppWorld Python missing')
    return s,q,sel,tr,v5

def usage()->dict[str,Any]:
    patch()
    with tempfile.TemporaryDirectory(prefix='ace-dsfq-usage-') as d:
        r=Path(d); ah=r/'atom';wd=r/'work';ah.mkdir();wd.mkdir(); auth=Path.home()/'.atomcode/auth.toml'
        if not auth.is_file(): raise Stop('AtomCode auth missing')
        shutil.copy2(auth,ah/'auth.toml');os.chmod(ah/'auth.toml',0o600);(ah/'config.toml').write_text(config(),encoding='utf-8');proc=None
        try:
            proc,b,t=base.live.start_daemon(atom_home=ah,workdir=wd,log_path=r/'daemon.log'); return dict(base.live.codingplan_usage(b,t))
        finally:
            if proc is not None: base.live.terminate_process(proc)

def freeze()->dict[str,Any]:
    patch();s,q,sel,tr,v5=inputs()
    if any(p.exists() for p in (AUTH_OUTPUT,Q1_OUTPUT,EXEC_CONTRACT)): raise Stop('freeze artifacts already exist')
    legacy=base.qualify_q1()
    if legacy.get('codingplan_model_requests')!=0 or legacy.get('session_mcp_progress_status')!='TOOLS_LISTED': raise Stop('Q1 crossed zero-request boundary')
    u=usage(); q1={'schema_version':'ace-direct-sfq-a0-atomgit-q1-v1','object_id':OBJECT_ID,'status':'DIRECT_SFQ_A0_ATOMGIT_MIMO25PRO_MCP_PREDISPATCH_PASS','legacy_q1_sha256':sha256_value(legacy),'codingplan_model_requests':0,'codingplan_usage':u,'bundle_sha256':sha256_file(OUTPUT_BUNDLE),'bridge_sha256':sha256_file(BRIDGE),'scientific_dispatch_sent':False,'scientific_outcomes_observed':0};q1['content_sha256']=sha256_value(q1);writej(Q1_OUTPUT,q1)
    auth={'schema_version':'ace-direct-sfq-a0-atomgit-human-authorization-v1','object_id':OBJECT_ID,'status':'USER_AUTHORIZED_DIRECT_SFQ_A0_ATOMGIT_MIMO25PRO_DEVELOPMENT_ONLY','authorization_basis':'User instructed continuation after AtomGit login/configuration and approved using the shared AtomGit plan for experiments on 2026-09-06.','scope':'Exactly the never-executed 12 Direct-SFQ-A0 cases under selected MiMo-V2.5-Pro; does not replace or satisfy qwen3.7-flash mainline Gate1.','static_contract_content_sha256':s['content_sha256'],'static_qualification_content_sha256':q['content_sha256'],'selected_backbone_content_sha256':sel['content_sha256'],'authority':{'direct_sfq_atomgit_mimo25pro_execution':True,'direct_qwen37flash_gate1':False,'f0_r1':False,'rq1_rq2':False,'rq3':False,'rq4':False,'paper_claim':False},'scientific_outcomes_observed':0};auth['content_sha256']=sha256_value(auth);writej(AUTH_OUTPUT,auth)
    c={'schema_version':'ace-direct-sfq-a0-atomgit-mimo25pro-contract-v1','object_id':OBJECT_ID,'execution_id':EXECUTION_ID,'status':'DIRECT_SFQ_A0_ATOMGIT_MIMO25PRO_EXECUTION_AUTHORIZED','purpose':'DEVELOPMENT_ONLY_SOURCE_FAILURE_QUALIFICATION_ON_FROZEN_DIRECT_SFQ_CASE_GEOMETRY','interpretation_boundary':'AtomGit/MiMo-Pro development evidence only; not interchangeable with qwen3.7-flash mainline Gate1.','human_authorization_content_sha256':auth['content_sha256'],'q1_content_sha256':q1['content_sha256'],'static_contract_content_sha256':s['content_sha256'],'static_qualification_content_sha256':q['content_sha256'],'selected_backbone_content_sha256':sel['content_sha256'],'inherited_transport_result_content_sha256':tr['content_sha256'],'v5_final_closeout_content_sha256':v5['content_sha256'],'model':{'provider':PROVIDER,'profile':MODEL_PROFILE,'id':MODEL_ID},'harness':{'id':'ATOMCODE_CODINGPLAN_MCP_V1','tool_call_cap':80,'model_round_cap_per_case':56,'retry_allowed':False,'replacement_allowed':False,'appworld_python':str(APPWORLD_PYTHON),'atomcode_binary_sha256':sha256_file(base.live.ATOMCODE_BIN)},'panel':{'case_count':12,'case_ids':[x['case_id'] for x in load_cases()],'one_episode_per_case':True,'confirmatory_reuse':False},'gate':{'acceptable_final_failure_counts':[9,10],'non_semantic_failure_invalidates_qualification':True},'quota':{'rolling_window_limit':500,'shared_reserve_for_g1':100,'operational_margin':5,'minimum_remaining_before_each_case':MIN_REMAINING,'pre_dispatch_hold_is_resumable':True,'post_dispatch_retry_allowed':False},'execution_policy':{'durable_dispatch_before_model_request':True,'unknown_after_dispatch_replay':False,'partial_outcome_redesign':False,'futility_early_stop':{'stop_too_easy_if_target_success_count_exceeds':3,'stop_too_hard_if_usable_failure_count_exceeds':10}},'authority':auth['authority'],'scientific_outcomes_observed':0};c['content_sha256']=sha256_value(c);writej(EXEC_CONTRACT,c)
    return {'authorization':auth,'q1':q1,'contract':c}

def futility(rows:list[dict[str,Any]])->str|None:
    if any(bool(x.get('non_semantic_failure')) for x in rows): return 'DIRECT_SFQ_A0_ATOMGIT_INVALID_NON_SEMANTIC_FAILURE_STOP'
    if sum(bool(x.get('target_success')) for x in rows)>3: return 'DIRECT_SFQ_A0_ATOMGIT_FUTILITY_TOO_EASY_STOP'
    if sum(bool(x.get('usable_target_failure')) for x in rows)>10: return 'DIRECT_SFQ_A0_ATOMGIT_FUTILITY_TOO_HARD_STOP'
    return None

def operational(ledger:Path,status:str,u:dict[str,Any]|None,next_case:str|None)->dict[str,Any]:
    rows=[x for x in base.live.ledger_rows(ledger) if x.get('event')=='COMPLETION']; x={'schema_version':'ace-direct-sfq-a0-atomgit-operational-v1','object_id':OBJECT_ID,'execution_id':EXECUTION_ID,'status':status,'completed_case_count':len(rows),'usable_target_failure_count':sum(bool(r.get('usable_target_failure')) for r in rows),'target_success_count':sum(bool(r.get('target_success')) for r in rows),'next_undispatched_case':next_case,'codingplan_usage':u,'minimum_remaining_before_case':MIN_REMAINING,'shared_reserve_for_g1':SHARED_RESERVE,'downstream_authority_opened':False,'scientific_effects_observed':0};x['content_sha256']=sha256_value(x);writej(OP_OUTPUT,x);return x

def execute(runtime_root:Path,ledger:Path)->dict[str,Any]:
    patch();verified(EXEC_CONTRACT,'DIRECT_SFQ_A0_ATOMGIT_MIMO25PRO_EXECUTION_AUTHORIZED'); runtime_root=runtime_root.resolve();ledger=ledger.resolve();runtime_root.mkdir(parents=True,exist_ok=True);states=base.live.ledger_states(ledger)
    for case in load_cases():
        k=uid(case['case_id']); st=states.get(k)
        if st=='COMPLETION': continue
        if st is not None: raise Stop(f'refusing replay: {k}:{st}')
        u0=usage()
        if int(u0['remaining'])<MIN_REMAINING: return operational(ledger,'DIRECT_SFQ_A0_ATOMGIT_OPERATIONAL_HOLD_SHARED_QUOTA',u0,case['case_id'])
        root=runtime_root/case['case_id'].lower()
        if root.exists(): raise Stop(f'refusing overwrite: {root}')
        root.mkdir(); atom,work,progress,mcp_payload=base._prepare(case['case_id'],root);proc=None;result=None;before={};after={}
        try:
            proc,b,t=base.live.start_daemon(atom_home=atom,workdir=work,log_path=root/'atomcode-daemon.log');(atom/'mcp.json').write_text(json.dumps(mcp_payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');base.live.http_json(b,t,'/live/mode',method='POST',body={'mode':'build'})
            def before_submit()->dict[str,Any]:
                ps=readj(progress)
                if ps.get('status')!='TOOLS_LISTED': raise Stop('MCP tools not listed')
                uu=dict(base.live.codingplan_usage(b,t))
                if int(uu['remaining'])<MIN_REMAINING: raise QuotaHold(uu)
                row={'schema_version':'ace-direct-sfq-a0-atomgit-ledger-v1','object_id':OBJECT_ID,'execution_id':EXECUTION_ID,'event':'DISPATCH','unit_id':k,'case_id':case['case_id'],'kind':case['kind'],'provider':PROVIDER,'model_profile':MODEL_PROFILE,'model_id':MODEL_ID,'harness':'ATOMCODE_CODINGPLAN_MCP_V1','prompt_sha256':sha256_value(case['task_instruction']),'initial_snapshot_sha256':ps['initial_snapshot_sha256'],'tool_call_cap':80,'model_round_cap':56,'codingplan_window_before':uu,'dispatch_time_ns':time.time_ns(),'attempt':1,'retry_allowed':False,'replacement_allowed':False};base.live.append_jsonl(ledger,row);return {'usage_before':uu}
            try: result=base.live.run_live_turn(base=b,token=t,instruction=case['task_instruction'],progress_path=progress,before_submit=before_submit,timeout_seconds=480)
            except QuotaHold as h:
                if base.live.ledger_states(ledger).get(k) is None:
                    base.live.terminate_process(proc);proc=None;shutil.rmtree(root);return operational(ledger,'DIRECT_SFQ_A0_ATOMGIT_OPERATIONAL_HOLD_SHARED_QUOTA',h.usage,case['case_id'])
                raise
            before=dict(result['pre_submit']['usage_before']);time.sleep(.3);after=dict(base.live.codingplan_usage(b,t))
            if result['prohibited_tool'] or result['error_message']:
                base.live.append_jsonl(ledger,{'schema_version':'ace-direct-sfq-a0-atomgit-ledger-v1','object_id':OBJECT_ID,'execution_id':EXECUTION_ID,'event':'FAILURE','unit_id':k,'case_id':case['case_id'],'failure_class':'HARNESS_OR_PROVIDER_INTERFACE_STOP','message':str(result['prohibited_tool'] or result['error_message'])[:400],'codingplan_window_after':after,'time_ns':time.time_ns(),'retry_attempted':False}); raise Stop('interface/harness failure after dispatch')
        finally:
            if proc is not None: base.live.terminate_process(proc)
        ps=readj(progress);tc=int(ps.get('tool_call_count',0));normal=result is not None and result['stop_reason']=='stopped' and tc<=80;target=evaluate_case_from_state(case,source_db_root=Path(ps['source_db_root']),changes_db_root=Path(ps['changes_db_root']),measurement_root=root/'measurement-full-dbs')
        base.live.append_jsonl(ledger,{'schema_version':'ace-direct-sfq-a0-atomgit-ledger-v1','object_id':OBJECT_ID,'execution_id':EXECUTION_ID,'event':'COMPLETION','unit_id':k,'case_id':case['case_id'],'kind':case['kind'],'tool_loop_completed':normal,'target_success':bool(target),'usable_target_failure':normal and not target,'non_semantic_failure':not normal,'atomcode_stop_reason':result['stop_reason'],'appworld_tool_call_count':tc,'model_round_count':int(result['model_round_count']),'prompt_tokens_total':int(result['prompt_tokens_total']),'completion_tokens_total':int(result['completion_tokens_total']),'codingplan_window_before':before,'codingplan_window_after':after,'bridge_progress_sha256':sha256_file(progress),'time_ns':time.time_ns()});states=base.live.ledger_states(ledger);rows=[x for x in base.live.ledger_rows(ledger) if x.get('event')=='COMPLETION'];f=futility(rows)
        if f: return operational(ledger,f,after,None)
    return operational(ledger,'DIRECT_SFQ_A0_ATOMGIT_PANEL_TERMINAL_READY_FOR_ADJUDICATION',usage(),None)

def adjudicate(ledger:Path)->dict[str,Any]:
    rows=base.live.ledger_rows(ledger);states=base.live.ledger_states(ledger); comp=[x for x in rows if x.get('event')=='COMPLETION'];fail=[x for x in rows if x.get('event')=='FAILURE'];expected={uid(c['case_id']) for c in load_cases()};f=futility(comp)
    if fail: status='DIRECT_SFQ_A0_ATOMGIT_INVALID_NON_SEMANTIC_FAILURE_STOP'
    elif set(states)==expected and len(comp)==12:
        n=sum(bool(x['usable_target_failure']) for x in comp); status='DIRECT_SFQ_A0_ATOMGIT_TARGET_FAILURE_QUALIFICATION_PASS' if n in {9,10} else ('DIRECT_SFQ_A0_ATOMGIT_TARGET_CHALLENGE_TOO_EASY_STOP' if n<9 else 'DIRECT_SFQ_A0_ATOMGIT_TARGET_CHALLENGE_TOO_HARD_STOP')
    elif f: status=f
    else: raise Stop('incomplete panel without terminal/futility proof')
    n=sum(bool(x.get('usable_target_failure')) for x in comp);s=sum(bool(x.get('target_success')) for x in comp);rem=12-len(comp);x={'schema_version':'ace-direct-sfq-a0-atomgit-mimo25pro-result-v1','object_id':OBJECT_ID,'execution_id':EXECUTION_ID,'status':status,'provider':PROVIDER,'model_profile':MODEL_PROFILE,'model_id':MODEL_ID,'harness':'ATOMCODE_CODINGPLAN_MCP_V1','planned_case_count':12,'completed_case_count':len(comp),'remaining_undispatched_case_count':rem,'usable_target_failure_count':n,'observed_usable_target_failure_rate':n/len(comp) if comp else None,'target_success_count':s,'possible_final_failure_count_interval':[n,n+rem],'acceptable_final_failure_counts':[9,10],'non_semantic_failure_units':[r['unit_id'] for r in comp if r.get('non_semantic_failure')]+[r['unit_id'] for r in fail],'scientific_model_round_count':sum(int(r.get('model_round_count',0)) for r in comp),'appworld_tool_call_total':sum(int(r.get('appworld_tool_call_count',0)) for r in comp),'ledger_sha256':sha256_file(ledger),'development_only':True,'confirmatory_reuse':False,'mainline_gate1_satisfied':False,'scientific_effects_observed':0,'authority':{'direct_sfq_atomgit_mimo25pro_closed':True,'direct_qwen37flash_gate1':False,'f0_r1':False,'rq1_rq2':False,'rq3':False,'rq4':False,'paper_claim':False}};x['content_sha256']=sha256_value(x);return x

def main()->None:
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--usage-only',action='store_true');p.add_argument('--runtime-root',type=Path);p.add_argument('--ledger',type=Path);p.add_argument('--result-output',type=Path,default=RESULT_OUTPUT);a=p.parse_args()
    if a.usage_only: print(json.dumps({'status':'ZERO_REQUEST_USAGE_PROBE','usage':usage(),'model_requests':0},sort_keys=True));return
    if a.freeze:
        z=freeze();print(json.dumps({'authorization':z['authorization']['status'],'q1':z['q1']['status'],'q1_model_requests':0,'usage':z['q1']['codingplan_usage'],'contract':z['contract']['status'],'mainline_gate1_authorized':False},sort_keys=True));return
    if a.runtime_root is None or a.ledger is None: raise SystemExit('--runtime-root and --ledger required')
    op=execute(a.runtime_root,a.ledger)
    if op['status']=='DIRECT_SFQ_A0_ATOMGIT_PANEL_TERMINAL_READY_FOR_ADJUDICATION' or op['status'].startswith('DIRECT_SFQ_A0_ATOMGIT_FUTILITY_') or op['status']=='DIRECT_SFQ_A0_ATOMGIT_INVALID_NON_SEMANTIC_FAILURE_STOP':
        r=adjudicate(a.ledger.resolve());writej(a.result_output.resolve(),r);print(json.dumps({'status':r['status'],'usable_target_failure_count':r['usable_target_failure_count'],'completed_case_count':r['completed_case_count'],'scientific_model_round_count':r['scientific_model_round_count'],'mainline_gate1_satisfied':False},sort_keys=True))
    else: print(json.dumps({'status':op['status'],'completed_case_count':op['completed_case_count'],'next_undispatched_case':op['next_undispatched_case'],'codingplan_usage':op['codingplan_usage'],'mainline_gate1_satisfied':False},sort_keys=True))
if __name__=='__main__': main()
