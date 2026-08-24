#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path

PAPER_ID='D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPERIMENT_ID='D2-PROXY-B12-REDDIT-CROSSDOMAIN-QUALIFICATION'


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path):
 d=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(d,dict):raise RuntimeError(f'not object:{p}')
 return d
def req(x:bool,msg:str):
 if not x:raise RuntimeError(msg)
def writej(p:Path,d):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');os.replace(t,p)

def main():
 ap=argparse.ArgumentParser()
 for n in ['reddit_parquet','task_config','model_dir','runner','output']:
  ap.add_argument('--'+n.replace('_','-'),required=True,type=Path)
 a=ap.parse_args()
 req(a.reddit_parquet.is_file(),'reddit parquet missing');req(a.task_config.is_file(),'task config missing');req(a.runner.is_file(),'runner missing')
 for n in ['config.json','tokenizer.json','sentence_bert_config.json','model.safetensors']:
  req((a.model_dir/n).exists(),f'model file missing:{n}')
 tasks=json.loads(a.task_config.read_text(encoding='utf-8'));req(isinstance(tasks,list) and len(tasks)==812,'task config geometry drift')
 contract={
  'schema_version':'1.0','paper_id':PAPER_ID,'experiment_id':EXPERIMENT_ID,
  'status':'FROZEN_BEFORE_QUALIFICATION_COMPUTATION','frozen_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
  'scientific_question':'Does a second WebArena domain (Reddit) have enough outcome-independent, released-trajectory, exact-retrieval, deterministic-evaluator support to justify a cross-domain reward-conditioned memory replication?',
  'domain':'reddit','provider_calls':0,'new_rollouts':0,
  'source_selection':{
   'source_description_count':20,'outcome_balance':{'successful':10,'failed':10},
   'reserve_all_string_match_tasks_from_source_selection':True,
   'candidate_requirements':['released AWM shuffle1 trajectory exists','nonempty deterministic action-summary projection','task belongs to reddit','task is not any released string_match evaluator task'],
   'deterministic_rule':'Within each original-outcome stratum, sort candidates by task_id. First take the earliest task from each unseen intent_template_id until the stratum target or templates are exhausted; then fill remaining slots by task_id. No writer output, retrieval score, future outcome, or terminal result may influence source selection.',
  },
  'retrieval_contract':{'model':'all-MiniLM-L6-v2','model_source':'exact model directory already bound by the C1 released-retriever audit','max_seq_length':256,'pooling':'attention-mask mean pooling + L2 normalization','top_k':1,'threshold':0.3,'document':'source task intent only','query':'future task intent only'},
  'future_support':{
   'population':'all released Reddit task configs; source tasks excluded',
   'trajectory_required':True,'evaluator_required':'exact offline string_match with only must_include/exact_match references','future_outcome_not_used_for_selection':True,
  },
  'qualification_gate':{
   'minimum_offline_eligible_retrieval_hits':6,
   'minimum_eligible_intent_templates':2,
   'minimum_distinct_selected_source_tasks':2,
   'maximum_required_source_writer_pairs_for_followup':8,
   'interpretation':'All four support/cost conditions must pass before any B12 writer/provider call is authorized. Failure is a support STOP, not a scientific null.'
  },
  'followup_if_qualified':{
   'stage_1':'freeze paired success/failure writer intervention only for source identities actually selected by eligible future support; same writer family and prompt contracts as C1',
   'stage_2':'if every required source pair completes, freeze matched success/failure native terminal rollouts on every qualified future task; retain the 0.15 practical-effect floor and p<0.05 dual gate',
   'no_positive_cell_selection':True,'no_threshold_relaxation':True,'no_model_fishing':True
  },
  'source_bindings':{
   'reddit_parquet':{'path':str(a.reddit_parquet.resolve()),'sha256':sha(a.reddit_parquet)},
   'task_config':{'path':str(a.task_config.resolve()),'sha256':sha(a.task_config)},
   'model_files':{n:sha(a.model_dir/n) for n in ['config.json','tokenizer.json','sentence_bert_config.json','model.safetensors']},
   'runner':{'path':str(a.runner.resolve()),'sha256':sha(a.runner)},
  },
  'authority':{'scientific_reopen_authority':True,'experiment_authority':True,'provider_call_authority':False,'gpu_authority':False,'claim_expansion_authority':False,'submission_authority':False}
 }
 raw=dict(contract);contract['contract_sha256']=hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()).hexdigest();writej(a.output,contract)
 print(json.dumps({'status':contract['status'],'contract_sha256':contract['contract_sha256'],'qualification_gate':contract['qualification_gate'],'provider_calls':0},indent=2))
if __name__=='__main__':main()
