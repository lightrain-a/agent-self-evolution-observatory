#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'; EXP='D2-PROXY-B4-RETRIEVAL-MATCHED-FIXED-EVIDENCE'
MASTER_SHA='ddc5bd50487ed431f5d24ee84cda4e422f36216b4191a02db21db18ae821161f'; B3_SHA='a5e39a817cdadc9b4edae4edba0c9c90068f1cd9d083e4c3a70bdfad32871440'; MANIFEST_SHA='2880b83c71745f049039c15edb02f731e4f87a44670977b61627143102bee0d1'
TASK_SHA='d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6'; PARQUET_SHA='fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e'; EVAL_SHA='f78eb61554c811f9411e7d72e0bdf2b5baa27379cbf632ade7fe49ce51a3f30d'; MEMORY_PY_SHA='d4f499fe3321571db7f631132b939cf5b9ab121f24d81fa80637df221aad6386'
MODEL={'requested':'doubao-seed-2.0-mini','expected_resolved':'doubao-seed-2-0-mini-260215','temperature':0.2,'max_output_tokens':900,'thinking':'disabled','provider_retries':0,'store':True,'allow_thinking_compatibility_fallback':False,'substitution_allowed':False}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def load(p:Path):return json.loads(p.read_text())
def req(x,msg):
 if not x:raise RuntimeError(msg)
def writej(p:Path,d):p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');os.replace(t,p)
def evidence(traj_json:str):
 tr=json.loads(traj_json);states=[];hashes=[];seen=set()
 for step in (tr.get('steps') or {}).values():
  c=((step.get('input_messages') or {}).get('contents') or [])
  if not c:continue
  text=str(c[-1].get('content') or '')
  if '[Current state starts here]' not in text:continue
  text=text.split('[Current state starts here]',1)[1].strip();h=tsha(text)
  if h in seen:continue
  seen.add(h);states.append(text);hashes.append(h)
 return '\n\n--- RELEASED BROWSER STATE ---\n\n'.join(states),hashes

def main():
 ap=argparse.ArgumentParser();
 for n in ['master_authority','b3_result','memory_manifest','runner','input_root','env_file','run_root']:ap.add_argument('--'+n.replace('_','-'),required=True,type=Path)
 a=ap.parse_args();req(sha(a.master_authority)==MASTER_SHA,'master SHA drift');req(sha(a.b3_result)==B3_SHA,'B3 SHA drift');req(sha(a.memory_manifest)==MANIFEST_SHA,'manifest SHA drift');master=load(a.master_authority);b3=load(a.b3_result);manifest=load(a.memory_manifest)
 req(master.get('paper_id')==PAPER and master.get('decision')=='approve' and master.get('provider_credential_use_authorized_if_required_by_a_frozen_subcontract') is True,'master authority invalid');f=master.get('future_repair_experiments') or {};req(f.get('human_program_authorized') is True and f.get('requires_per_experiment_preregistration') is True and f.get('automatic_execution_without_frozen_subcontract') is False,'program authority invalid');req(master.get('claim_expansion_authorized') is False,'claim expansion authorized unexpectedly')
 req(b3['status']=='COMPLETE_ZERO_PROVIDER_CALLS' and b3['summary']['offline_eligible_retrieval_matched_tasks']==36,'B3 support drift');req(manifest['status']=='B4_MEMORY_MANIFEST_READY' and manifest['memory_object_count']==40,'memory manifest drift')
 task_config=a.input_root/'generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/benchmarks/wa/test_configs/test.raw.json';parquet=a.input_root/'generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet';evaluator=a.input_root/'generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/evaluators/wa/wa_evaluators.py';memory_py=a.input_root/'generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/benchmarks/wa/memory.py';vendor=a.input_root/'generated/research-data/paper-yield-d5-c01/vendor'
 for p,h,n in [(task_config,TASK_SHA,'task'),(parquet,PARQUET_SHA,'parquet'),(evaluator,EVAL_SHA,'evaluator'),(memory_py,MEMORY_PY_SHA,'memory.py')]:req(p.is_file() and sha(p)==h,f'{n} drift')
 req(a.runner.is_file() and a.env_file.is_file() and vendor.is_dir(),'runner/env/vendor missing')
 import sys;sys.path.insert(0,str(vendor));import pyarrow.parquet as pq
 cfg=load(task_config);by={int(x['task_id']):x for x in cfg};rows={int(x['task_id']):x for x in pq.read_table(parquet,columns=['task_id','trajectory_json']).to_pylist()};mobj={(int(x['source_task']),x['condition']):x for x in manifest['objects']}
 units=[]
 for x in b3['offline_eligible_support']:
  tid=int(x['task_id']);src=int(x['top1_source_task']);req(tid in rows and tid in by,'eligible task missing');refs=(by[tid].get('eval') or {}).get('reference_answers') or {};req(set(refs).issubset({'must_include','exact_match'}) and bool(refs),'non-deterministic evaluator leaked');ev,hs=evidence(str(rows[tid]['trajectory_json']));req(bool(ev),'empty fixed evidence')
  wrappers={}
  for cond in ['success','failure']:
   o=mobj[(src,cond)];p=Path(o['native_wrapper_path']);req(p.is_file() and sha(p)==o['native_wrapper_sha256'],'wrapper drift');wrappers[cond]={'path':str(p.resolve()),'sha256':o['native_wrapper_sha256'],'raw_sha256':o['raw_sha256']}
  units.append({'future_task':tid,'task_prompt':str(by[tid]['intent']),'intent_template_id':by[tid].get('intent_template_id'),'selected_source_task':src,'retrieval_similarity':x['top1_similarity'],'retrieval_margin':x['top1_margin'],'evidence_sha256':tsha(ev),'released_state_sha256':hs,'reference_answers':refs,'memory_wrappers':wrappers})
 req(len(units)==36 and len({x['future_task'] for x in units})==36,'unit support drift')
 contract={'schema_version':'1.0','experiment_id':EXP,'paper_id':PAPER,'status':'FROZEN_BEFORE_PROVIDER_CALLS','frozen_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),'question':'Under the released top-1/.3 retrieval identity and native ReasoningBank memory wrapper, do success- versus failure-conditioned memories alter terminal success under frozen released future evidence?','relationship_to_primary_claim':'retrieval-matched fixed-evidence transport replication; stronger ecological interface than F2R1 but still not live-browser end-to-end execution','human_authority':{'path':str(a.master_authority.resolve()),'sha256':MASTER_SHA},'b3':{'path':str(a.b3_result.resolve()),'sha256':B3_SHA},'memory_manifest':{'path':str(a.memory_manifest.resolve()),'sha256':MANIFEST_SHA},'source_artifacts':{'task_config':{'path':str(task_config.resolve()),'sha256':TASK_SHA},'parquet':{'path':str(parquet.resolve()),'sha256':PARQUET_SHA},'evaluator':{'path':str(evaluator.resolve()),'sha256':EVAL_SHA},'memory_py':{'path':str(memory_py.resolve()),'sha256':MEMORY_PY_SHA}},'vendor_path':str(vendor.resolve()),'provider_env_file':str(a.env_file.resolve()),'code':{'runner':{'path':str(a.runner.resolve()),'sha256':sha(a.runner)}},'task_units':units,'future_task_count':36,'conditions':['success','failure'],'rollouts_per_task_per_condition':4,'expected_provider_calls':288,'model':MODEL,'prompt_contract':{'retrieval_identity':'exact B3 all-MiniLM-L6-v2 top-1 threshold .3','memory_wrapper_text':'exact ReasoningBankMemory.agent_messages text with rm_meta_instruct=true','memory_wrapper_role_transport':'single-provider prompt serialization of the native human-memory text; not claimed byte-equivalent to the released BrowserUse message stack','future_evidence':'released fixed browser-state packet extracted from AWM trajectories','evaluator':'deterministic released string-match subset only'},'primary_gate':{'statistic':'mean over 36 frozen future tasks of absolute difference in terminal success rate between success- and failure-conditioned retrieved-memory states','min_mean_absolute_success_rate_difference':0.15,'permutation_p_lt':0.05,'permutation_repetitions':100000,'permutation_seed':20260824},'secondary_descriptives':['mean signed failure-minus-success','zero/nonzero task count','sign counts','effect by retrieved source','effect by intent template','retrieval-similarity versus absolute-effect descriptive correlation'],'missingness_policy':{'provider_retries':0,'stop_after_first_no_text_provider_failure':True,'top_up_failed_units':False,'replace_future_tasks':False,'replace_source_tasks':False,'text_bearing_provider_status_incomplete_is_scorable':True},'execution_guards':{'single_writer_transaction_lock_required':True,'response_first_archival_required':True,'resumable_stage_cache':True,'fixed_order_chunking_allowed':True,'chunking_cannot_depend_on_outcomes':True},'scope_boundary':{'no_live_browser_claim':True,'no_population_causal_effect_claim':True,'no_threshold_relaxation':True,'no_outcome_driven_task_selection':True,'original_F2R1_gate_unchanged':True},'authority':{'scientific_reopen_authority':True,'experiment_authority':True,'provider_call_authority':True,'gpu_authority':False,'claim_expansion_authority':False,'submission_authority':False}}
 raw=dict(contract);contract['contract_sha256']=hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()).hexdigest();cp=a.run_root/'b4-contract.json';writej(cp,contract);receipt={'schema_version':'1.0','receipt_type':'scoped-experiment-authorization','paper_id':PAPER,'experiment_id':EXP,'status':'B4_RETRIEVAL_MATCHED_FIXED_EVIDENCE_AUTHORIZED','master_authority_sha256':MASTER_SHA,'b3_sha256':B3_SHA,'memory_manifest_sha256':MANIFEST_SHA,'contract_file_sha256':sha(cp),'runner_sha256':contract['code']['runner']['sha256'],'future_task_count':36,'provider_call_ceiling':288,'primary_gate':contract['primary_gate'],'authority':contract['authority']};writej(a.run_root/'b4-authorization-receipt.json',receipt);print(json.dumps({'status':receipt['status'],'contract_file_sha256':receipt['contract_file_sha256'],'future_task_count':36,'provider_call_ceiling':288,'primary_gate':receipt['primary_gate']},indent=2))
if __name__=='__main__':main()
