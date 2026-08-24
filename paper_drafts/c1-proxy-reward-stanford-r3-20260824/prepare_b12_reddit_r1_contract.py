#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
PAPER='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE';EXP='D2-PROXY-B12-REDDIT-CROSSDOMAIN-REPLICATION-R1'
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:
 d=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(d,dict):raise RuntimeError(f'not object:{p}')
 return d
def req(x:bool,m:str):
 if not x:raise RuntimeError(m)
def writej(p:Path,d:dict[str,Any]):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');os.replace(t,p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--parent-contract',required=True,type=Path);ap.add_argument('--parent-result',required=True,type=Path);ap.add_argument('--runner',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();p=load(a.parent_contract);r=load(a.parent_result)
 req(p.get('paper_id')==PAPER and p.get('experiment_id')=='D2-PROXY-B12-REDDIT-CROSSDOMAIN-REPLICATION','parent contract identity drift');req(r.get('status')=='B12_REDDIT_WRITER_PARTIAL','parent status drift');req(r['summary']['writer_calls_complete']==7 and r['summary']['writer_failures']==1 and r['summary']['terminal_calls_complete']==0,'parent failure geometry drift');req(len(r.get('failures') or [])==1,'parent failure count drift');f=r['failures'][0];req(int(f.get('source_task'))==610 and f.get('condition')=='failure' and f.get('status')=='provider_state_failure_no_text','parent failure identity drift');rec=f.get('provider_receipt') or {};req(rec.get('incomplete_reason')=='length' and str(rec.get('resolved_model','')).startswith('deepseek-v4-flash'),'parent failure is not length-censored DeepSeek support failure');req(a.runner.is_file(),'r1 runner missing')
 c=json.loads(json.dumps(p));c['experiment_id']=EXP;c['status']='FROZEN_BEFORE_B12_R1_PROVIDER_CALLS';c['frozen_at']=datetime.now(timezone.utc).replace(microsecond=0).isoformat();c['writer_stage']['model']['max_output_tokens']=8192;c['source_bindings']['runner']={'path':str(a.runner.resolve()),'sha256':sha(a.runner)};c['program_budget']={'writer_provider_call_ceiling':8,'terminal_provider_call_ceiling':64,'total_provider_call_ceiling':72,'parent_provider_posts':8,'cumulative_b12_provider_post_ceiling_after_r1':80,'training_runs':0,'gpu_runs':0};c['repair_policy']={'repair_id':'B12-R1-UNIFORM-WRITER-OUTPUT-CAP','trigger':'parent writer source 610 / failure length-censored without assistant text at 4096 tokens','changed_dimension_only':'writer max_output_tokens 4096 -> 8192','all_8_writer_units_regenerated_fresh':True,'parent_successful_writer_outputs_reused_for_science':False,'source_tasks_changed':False,'future_tasks_changed':False,'retrieval_support_changed':False,'writer_model_changed':False,'writer_prompts_changed':False,'terminal_policy_changed':False,'terminal_gate_changed':False,'second_repair_allowed':False};c['parent_execution']={'contract_path':str(a.parent_contract.resolve()),'contract_sha256':sha(a.parent_contract),'result_path':str(a.parent_result.resolve()),'result_sha256':sha(a.parent_result),'provider_posts':8,'scientific_writer_pairs':0,'terminal_calls':0,'disposition':'execution-support parent only; no parent writer output contributes to R1 scientific result'};c['authority']['provider_call_authority']=True
 c.pop('contract_sha256',None);raw=dict(c);c['contract_sha256']=hashlib.sha256(json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();writej(a.output,c);print(json.dumps({'status':c['status'],'experiment_id':EXP,'contract_sha256':c['contract_sha256'],'repair_policy':c['repair_policy'],'r1_call_ceiling':72,'cumulative_b12_ceiling':80},indent=2))
if __name__=='__main__':main()
