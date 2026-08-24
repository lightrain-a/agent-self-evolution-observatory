#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID='D2-PROXY-B10-NATIVE-FIRST-ACTION-TRANSPORT'
AUTHORITY_TYPE='human-c1-proxy-reward-stanford-repair-experiment-program'
EXPECTED_B3_SHA='a5e39a817cdadc9b4edae4edba0c9c90068f1cd9d083e4c3a70bdfad32871440'
EXPECTED_B4_CONTRACT_SHA='eb86231b4afe2143e59fa8d322a42a5bb236a09aefcb506fe2d7bb7d8dbaaa11'
EXPECTED_B4_RESULT_SHA='fb3fef89a38806e9a3b13efd8413b920f81b132390818403f4d5be957f42feeb'
EXPECTED_MANIFEST_SHA='2880b83c71745f049039c15edb02f731e4f87a44670977b61627143102bee0d1'
EXPECTED_PARQUET_SHA='fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e'
EXPECTED_AUTH_SHA='ddc5bd50487ed431f5d24ee84cda4e422f36216b4191a02db21db18ae821161f'
EXPECTED_SOURCE_MESSAGE_SHA='7699d234bb5fc874d57ee418a2e0aabf6c49ffc8dcc52685ce5b9bcc86282e62'
MODEL={'requested':'doubao-seed-2.0-mini','expected_resolved':'doubao-seed-2-0-mini-260215','temperature':0.2,'max_output_tokens':900,'thinking':'disabled','provider_retries':0,'store':True,'allow_thinking_compatibility_fallback':False,'substitution_allowed':False}


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def jsha(x:Any)->str:return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(p:Path)->dict[str,Any]:
 d=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(d,dict):raise RuntimeError(f'JSON root not object:{p}')
 return d
def req(x:bool,msg:str):
 if not x:raise RuntimeError(msg)
def writej(p:Path,d:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');os.replace(t,p)


def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument('--b3',required=True,type=Path);ap.add_argument('--b4-contract',required=True,type=Path);ap.add_argument('--b4-result',required=True,type=Path);ap.add_argument('--memory-manifest',required=True,type=Path);ap.add_argument('--parquet',required=True,type=Path);ap.add_argument('--vendor',required=True,type=Path);ap.add_argument('--master-authority',required=True,type=Path);ap.add_argument('--env-file',required=True,type=Path);ap.add_argument('--runner',required=True,type=Path);ap.add_argument('--run-root',required=True,type=Path)
 a=ap.parse_args()
 for p,h,n in [(a.b3,EXPECTED_B3_SHA,'B3'),(a.b4_contract,EXPECTED_B4_CONTRACT_SHA,'B4 contract'),(a.b4_result,EXPECTED_B4_RESULT_SHA,'B4 result'),(a.memory_manifest,EXPECTED_MANIFEST_SHA,'memory manifest'),(a.parquet,EXPECTED_PARQUET_SHA,'parquet'),(a.master_authority,EXPECTED_AUTH_SHA,'human authority')]:req(p.is_file() and sha(p)==h,f'{n} SHA drift')
 req(a.vendor.is_dir(),'vendor missing');req(a.env_file.is_file(),'env missing');req(a.runner.is_file(),'runner missing')
 b3=load(a.b3);b4=load(a.b4_contract);b4r=load(a.b4_result);man=load(a.memory_manifest);master=load(a.master_authority)
 req(b3['status']=='COMPLETE_ZERO_PROVIDER_CALLS' and b3['summary']['offline_eligible_retrieval_matched_tasks']==36,'B3 support drift')
 req(b4['status']=='FROZEN_BEFORE_PROVIDER_CALLS' and len(b4['task_units'])==36 and b4['future_task_count']==36,'B4 support drift')
 req(b4['model']==MODEL,'B4 model drift')
 req(b4r['status']=='B4_EXECUTION_COMPLETE' and b4r['summary']['provider_calls_complete']==288,'B4 result incomplete')
 req(man['status']=='B4_MEMORY_MANIFEST_READY' and man['memory_object_count']==40,'manifest drift')
 req(master.get('authority_type')==AUTHORITY_TYPE and master.get('decision')=='approve' and master.get('paper_id')==PAPER_ID,'human authority invalid')
 req(master.get('source_message_sha256')==EXPECTED_SOURCE_MESSAGE_SHA,'human authority source drift')
 future=master.get('future_repair_experiments') or {};req(future.get('human_program_authorized') is True and future.get('requires_per_experiment_preregistration') is True and future.get('requires_budget_and_stop_rule') is True,'program authority insufficient')
 req(future.get('automatic_execution_without_frozen_subcontract') is False and future.get('outcome_driven_scope_expansion_authorized') is False,'program fail-closed drift')
 req(master.get('provider_credential_use_authorized_if_required_by_a_frozen_subcontract') is True and master.get('claim_expansion_authorized') is False,'authority scope drift')

 sys.path.insert(0,str(a.vendor));import pyarrow.parquet as pq
 rows={str(r['task_id']):r for r in pq.read_table(a.parquet,columns=['task_id','task_prompt','trajectory_json']).to_pylist()}
 units=[]
 for u in b4['task_units']:
  tid=str(u['future_task']);req(tid in rows,f'missing trajectory:{tid}')
  tr=json.loads(str(rows[tid]['trajectory_json']));step=(tr.get('steps') or {}).get('1');req(isinstance(step,dict),f'step1 missing:{tid}')
  contents=((step.get('input_messages') or {}).get('contents') or []);req(len(contents)>=2,f'input contents missing:{tid}')
  system=str(contents[0].get('content') or '');last=str(contents[-1].get('content') or '');marker='[Current state starts here]';req(system.strip() and marker in last,f'system/state missing:{tid}')
  state=last.split(marker,1)[1].strip();req(state,f'empty current state:{tid}')
  req(str(rows[tid]['task_prompt'])==str(u['task_prompt']),f'task prompt drift:{tid}')
  units.append({'future_task':int(tid),'selected_source_task':int(u['selected_source_task']),'future_step':1,'task_prompt_sha256':tsha(str(u['task_prompt'])),'system_instruction_sha256':tsha(system),'current_state_sha256':tsha(state),'retrieval_similarity':u['retrieval_similarity'],'retrieval_margin':u['retrieval_margin'],'intent_template_id':u['intent_template_id'],'memory_wrappers':u['memory_wrappers']})
 req(len(units)==36 and len({x['future_task'] for x in units})==36,'unit geometry drift')

 contract={'schema_version':'1.0','experiment_id':EXPERIMENT_ID,'paper_id':PAPER_ID,'status':'FROZEN_BEFORE_PROVIDER_CALLS','frozen_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),'question':'On the exact 36-task native-retrieval support where terminal branch transport is weak, do success- versus failure-conditioned memories change the first structured browser action before terminal outcome compression?','relationship_to_prior':'Pre-terminal mechanism localization only. B4/B5 terminal non-passes remain unchanged regardless of B10 outcome.','source_bindings':{'b3':{'path':str(a.b3.resolve()),'sha256':EXPECTED_B3_SHA},'b4_contract':{'path':str(a.b4_contract.resolve()),'sha256':EXPECTED_B4_CONTRACT_SHA},'b4_result':{'path':str(a.b4_result.resolve()),'sha256':EXPECTED_B4_RESULT_SHA},'memory_manifest':{'path':str(a.memory_manifest.resolve()),'sha256':EXPECTED_MANIFEST_SHA},'parquet':{'path':str(a.parquet.resolve()),'sha256':EXPECTED_PARQUET_SHA}},'vendor_path':str(a.vendor.resolve()),'provider_env_file':str(a.env_file.resolve()),'human_authority':{'path':str(a.master_authority.resolve()),'sha256':EXPECTED_AUTH_SHA,'source_message_sha256':EXPECTED_SOURCE_MESSAGE_SHA},'code':{'runner':{'path':str(a.runner.resolve()),'sha256':sha(a.runner)}},'state_selection':{'rule':'Use released trajectory step 1 for every frozen future task; retain only the substring after [Current state starts here] in the final input message, thereby excluding pre-existing task-history memory.','future_step':1,'outcome_blind':True,'task_specific_step_selection':False},'task_units':units,'future_task_count':36,'conditions':['success_memory','failure_memory','no_memory'],'rollouts_per_task_per_condition':4,'expected_provider_calls':432,'model':MODEL,'action_signature':'Exact legacy F1D normalization: first structured action name; click_element additionally includes the interactive-element index.','primary_gate':{'statistic':'mean over 36 frozen states of empirical total-variation distance between success-memory and failure-memory first-action signature distributions','min_mean_tv':0.20,'permutation_p_lt':0.05,'permutation_repetitions':100000,'permutation_seed':20260824,'permutation_scheme':'Within each future state, pool the eight success/failure action signatures and randomly assign four to each branch independently across states.'},'secondary_descriptives':['mean 0.5*(TV(success,no-memory)+TV(failure,no-memory)) across states','modal action difference rates','per-state action entropy','correlation of first-action TV with frozen B4 terminal absolute effect'],'missingness_policy':{'provider_retries':0,'stop_after_first_no_text_provider_failure':True,'stop_after_first_unrecoverable_parse_failure':True,'top_up_failed_units':False,'replace_future_tasks':False,'replace_source_tasks':False},'execution_guards':{'single_writer_transaction_lock_required':True,'response_first_archival_required':True,'resumable_stage_cache':True,'fixed_execution_order':True,'batching_may_not_depend_on_intermediate_outcomes':True},'scope_boundary':{'no_terminal_rescue_claim':True,'B4_terminal_negative_boundary_preserved':True,'B5_presence_negative_boundary_preserved':True,'no_live_browser_claim':True,'no_population_causal_effect_claim':True,'no_outcome_driven_state_selection':True},'authority':{'scientific_reopen_authority':True,'experiment_authority':True,'provider_call_authority':True,'gpu_authority':False,'claim_expansion_authority':False,'submission_authority':False}}
 contract['contract_sha256']=jsha(contract);root=a.run_root.resolve();cp=root/'b10-contract.json';writej(cp,contract)
 receipt={'schema_version':'1.0','receipt_type':'scoped-experiment-authorization','paper_id':PAPER_ID,'experiment_id':EXPERIMENT_ID,'status':'B10_NATIVE_FIRST_ACTION_AUTHORIZED','contract_payload_sha256':contract['contract_sha256'],'contract_file_sha256':sha(cp),'runner_sha256':contract['code']['runner']['sha256'],'provider_call_ceiling':432,'future_task_count':36,'primary_gate':contract['primary_gate'],'authority':contract['authority']};writej(root/'b10-authorization-receipt.json',receipt)
 print(json.dumps({'status':receipt['status'],'contract_file_sha256':receipt['contract_file_sha256'],'provider_call_ceiling':432,'future_task_count':36,'primary_gate':receipt['primary_gate']},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
