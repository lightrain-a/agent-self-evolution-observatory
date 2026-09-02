#!/usr/bin/env python3
"""Prepare the zero-provider fresh substrate for C1 PACTA-MSR / Qwen397."""
from __future__ import annotations
import hashlib,json,os,tempfile
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[1]
DATASET=Path('/data/wyt/agent-self-evolution-observatory/external/stri-swebench-verified-78f471bf655a3137b2e8a75af1501690ec009ec3/data/test-00000-of-00001.parquet')
OLD_POOL=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1/fresh-pool.json')
FIXTURES=(
 ROOT/'generated/asset-first-stri-reasoningbank-p1-task-fixtures-20260829.json',
 ROOT/'generated/asset-first-stri-reasoningbank-p1-q2-task-fixtures-20260830.json',
 ROOT/'generated/asset-first-stri-reasoningbank-p1-q3-task-fixtures-20260830.json',
)
DESIGN=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-design-20260902.json'
OUT=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-fresh-pool-20260902.json'
RUN=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-preflight-20260902-v1')
SOURCE_SALT='C1-PACTA-MSR-QWEN397-SOURCE-v1'
FUTURE_SALT='C1-PACTA-MSR-QWEN397-FUTURE-v1'
PILOT_SALT='C1-PACTA-MSR-QWEN397-PILOT-v1'
RANDOM_SALT='C1-PACTA-MSR-QWEN397-RANDOM-v1'


def now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def sha_text(x:str)->str:return hashlib.sha256(x.encode()).hexdigest()
def sha_file(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x:Any)->str:return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def atomic_json(path:Path,obj:dict[str,Any])->str:
 path.parent.mkdir(parents=True,exist_ok=True);body=dict(obj);body['payload_sha256']=sha_text(canon(obj));raw=(json.dumps(body,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
 fd,tmp=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as h:h.write(raw);h.flush();os.fsync(h.fileno())
  os.replace(tmp,path)
 finally:
  try:os.unlink(tmp)
  except FileNotFoundError:pass
 return hashlib.sha256(raw).hexdigest()

def collect_instance_ids(x:Any,out:set[str])->None:
 if isinstance(x,dict):
  if isinstance(x.get('instance_id'),str):out.add(x['instance_id'])
  for v in x.values():collect_instance_ids(v,out)
 elif isinstance(x,list):
  for v in x:collect_instance_ids(v,out)

def prior_ids()->tuple[set[str],dict[str,Any]]:
 old=json.loads(OLD_POOL.read_text());ids=set();old_ids=[]
 for u in old['units']:
  for k in ('source_task_id','future_task_id'):
   ids.add(u[k]);old_ids.append(u[k])
 fixture_ids=set();fixture_hashes={}
 for p in FIXTURES:
  if not p.is_file():raise RuntimeError(f'missing fixture: {p}')
  fixture_hashes[str(p)]=sha_file(p);o=json.loads(p.read_text());collect_instance_ids(o,fixture_ids)
 ids|=fixture_ids
 return ids,{'old_pool_sha256':sha_file(OLD_POOL),'old_pool_ids':sorted(set(old_ids)),'fixture_ids':sorted(fixture_ids),'fixture_sha256':fixture_hashes}

def select_pool()->dict[str,Any]:
 if not DATASET.is_file() or not DESIGN.is_file():raise RuntimeError('missing dataset/design')
 prior,prov=prior_ids();rows=pq.read_table(DATASET,columns=['instance_id','repo','problem_statement','base_commit']).to_pylist();by=defaultdict(list)
 for r in rows:
  if r['instance_id'] not in prior:by[str(r['repo'])].append(r)
 eligible={repo:rs for repo,rs in by.items() if len(rs)>=2}
 if len(eligible)!=10:raise RuntimeError(f'expected exactly ten eligible repositories after exclusions, got {len(eligible)}')
 out=[]
 for repo,rs in sorted(eligible.items()):
  s=min(rs,key=lambda r:(sha_text(SOURCE_SALT+'|'+r['instance_id']),r['instance_id']))
  f=min((r for r in rs if r['instance_id']!=s['instance_id']),key=lambda r:(sha_text(FUTURE_SALT+'|'+s['instance_id']+'|'+r['instance_id']),r['instance_id']))
  uid=s['instance_id']+'=>'+f['instance_id']
  out.append({
   'unit_id':uid,'task_family':repo,
   'source_task_id':s['instance_id'],'source_task':s['problem_statement'],'source_task_sha256':sha_text(s['problem_statement']),'source_base_commit':s['base_commit'],
   'future_task_id':f['instance_id'],'future_task':f['problem_statement'],'future_task_sha256':sha_text(f['problem_statement']),'future_base_commit':f['base_commit'],
   'source_rank':sha_text(SOURCE_SALT+'|'+s['instance_id']),'future_rank':sha_text(FUTURE_SALT+'|'+s['instance_id']+'|'+f['instance_id']),
   'pilot_rank':sha_text(PILOT_SALT+'|'+uid),'random_gate_rank':sha_text(RANDOM_SALT+'|'+uid),
   'prior_id_overlap':False,'prior_reasoningbank_scientific_output':False})
 ids=[x for u in out for x in (u['source_task_id'],u['future_task_id'])]
 if len(ids)!=20 or len(set(ids))!=20 or set(ids)&prior:raise RuntimeError('fresh pair disjointness failure')
 return {'schema_version':1,'created_at_utc':now(),'experiment':'C1-PACTA-MSR-QWEN397-P0-20260902','status':'FRESH_PAIR_POOL_FROZEN_PRE_PROVIDER','dataset':{'path':str(DATASET),'sha256':sha_file(DATASET),'rows':len(rows)},'design_sha256':sha_file(DESIGN),'prior_exclusion_count':len(prior),'prior_provenance':prov,'selection':{'source_salt':SOURCE_SALT,'future_salt':FUTURE_SALT,'pilot_salt':PILOT_SALT,'random_salt':RANDOM_SALT,'one_pair_per_repository':True,'outcome_fields_read':False},'candidate_count':len(out),'repository_count':len({u['task_family'] for u in out}),'units':out,'provider_calls':0,'writer_calls':0,'probe_calls':0,'shadow_calls':0,'final_calls':0}

def main()->None:
 if OUT.exists() or RUN.exists():raise RuntimeError('fresh-pool preparation target exists; no overwrite')
 pool=select_pool();outsha=atomic_json(OUT,pool);RUN.mkdir(parents=True);atomic_json(RUN/'fresh-pool.json',pool);atomic_json(RUN/'manifest.json',{'schema_version':1,'created_at_utc':now(),'status':'ZERO_PROVIDER_FRESH_POOL_READY','fresh_pool_path':str(OUT),'fresh_pool_sha256':outsha,'provider_calls':0})
 print(json.dumps({'status':pool['status'],'candidate_count':pool['candidate_count'],'repository_count':pool['repository_count'],'prior_exclusion_count':pool['prior_exclusion_count'],'fresh_pool_sha256':outsha},sort_keys=True))

if __name__=='__main__':main()
