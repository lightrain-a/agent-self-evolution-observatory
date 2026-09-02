#!/usr/bin/env python3
"""Compile byte-frozen deterministic read-only MSR probe specs before any PACTA-MSR outcome."""
from __future__ import annotations
import hashlib,json,re,shlex
from pathlib import Path
from typing import Any
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json,sha256_file

ROOT=Path(__file__).resolve().parents[1]
POOL=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-fresh-pool-20260902.json'
POOL_SHA='2391967a3da363bcbbe87403599970854d7cf7ed82b249078b0469b36a8de59e'
ADDENDUM=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-probe-compiler-addendum-20260902.json'
RUNTIME=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-runtime-20260902-v1/normalization-qualification.json')
RUNTIME_SHA='7b876c9dc31e964868fa1c5cff3cd5ab3510e57162e65368023102822d933a01'
OUT=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-probe-specs-20260902.json'
TOKEN_SALT='C1-PACTA-MSR-PROBE-TOKEN-v1'
STOP={
 'about','after','again','also','another','because','before','being','between','both','bug','case','change','changes','code','could','current','describe','does','error','expected','feature','file','files','fix','from','have','into','issue','like','method','more','need','only','other','plus','problem','python','same','should','test','tests','that','their','then','there','these','this','using','value','values','want','when','where','which','with','would','your'}
LEX=re.compile(r'\b[A-Za-z_][A-Za-z0-9_.-]{3,}\b')
BACKTICK=re.compile(r'`([^`\n]{2,120})`')

def sha(x:str)->str:return hashlib.sha256(x.encode()).hexdigest()
def normalize_token(x:str)->str:
 x=x.strip().strip('()[]{}:,;')
 if x.endswith('()'):x=x[:-2]
 return x[:100]
def candidates(task:str)->list[tuple[int,str]]:
 out=[];seen=set()
 for raw in BACKTICK.findall(task):
  for tok in LEX.findall(raw):
   tok=normalize_token(tok);low=tok.lower()
   if len(tok)>=4 and low not in STOP and low not in seen:seen.add(low);out.append((0,tok))
 for tok in LEX.findall(task):
  tok=normalize_token(tok);low=tok.lower()
  if len(tok)>=4 and low not in STOP and low not in seen:seen.add(low);out.append((1,tok))
 return out
def compile_tokens(task:str,task_sha:str)->list[str]:
 c=candidates(task)
 ranked=sorted(c,key=lambda x:(x[0],sha(TOKEN_SALT+'|'+task_sha+'|'+x[1].lower()),x[1].lower(),x[1]))
 if len(ranked)<3:raise RuntimeError('STOP_MSR_PROBE_TOKEN_SUPPORT_INSUFFICIENT')
 return [x[1] for x in ranked[:3]]
def compile_command(tokens:list[str])->str:
 if len(tokens)!=3:raise ValueError('exactly three tokens required')
 expr=' '.join('-e '+shlex.quote(x) for x in tokens)
 return f"git status --short; git grep -n -I {expr} -- . | head -n 80; git ls-files | head -n 40"
def prepare()->dict[str,Any]:
 if sha256_file(POOL)!=POOL_SHA:raise RuntimeError('fresh pool drift')
 if sha256_file(RUNTIME)!=RUNTIME_SHA:raise RuntimeError('runtime drift')
 add=json.loads(ADDENDUM.read_text())
 if add.get('status')!='FROZEN_PRE_PROVIDER_DESIGN_ADDENDUM' or add.get('provider_calls_for_probe')!=0:raise RuntimeError('probe addendum invalid')
 pool=json.loads(POOL.read_text());runtime=json.loads(RUNTIME.read_text());future={x['instance_id']:x for x in runtime['rows'] if x['role']=='future' and x['exact_base_normalization_pass']}
 rows=[]
 for u in pool['units']:
  rr=future.get(u['future_task_id'])
  if not rr:raise RuntimeError('future runtime absent '+u['future_task_id'])
  toks=compile_tokens(u['future_task'],u['future_task_sha256']);cmd=compile_command(toks)
  rows.append({'unit_id':u['unit_id'],'future_task_id':u['future_task_id'],'future_task_sha256':u['future_task_sha256'],'future_base_commit':u['future_base_commit'],'future_digest_ref':rr['digest_ref'],'tokens':toks,'command':cmd,'command_sha256':sha(cmd),'probe_timeout_seconds':60,'provider_calls':0,'branch_blind':True,'memory_blind':True,'read_only':True})
 if len(rows)!=10 or len({x['command_sha256'] for x in rows})<1:raise RuntimeError('probe geometry')
 return {'schema_version':1,'experiment':'C1-PACTA-MSR-QWEN397-PROBE-SPECS-20260902','status':'MSR_10_PROBE_SPECS_FROZEN_PRE_SOURCE_OUTCOME','fresh_pool_sha256':POOL_SHA,'runtime_sha256':RUNTIME_SHA,'addendum_sha256':sha256_file(ADDENDUM),'token_salt':TOKEN_SALT,'rows':rows,'provider_calls':0,'future_task_executions':0,'writer_calls':0,'shadow_calls':0,'final_calls':0}
def main()->None:
 if OUT.exists():raise RuntimeError('probe specs already exist; no overwrite')
 o=prepare();atomic_json(OUT,o);print(json.dumps({'status':o['status'],'specs':len(o['rows']),'sha256':sha256_file(OUT)},sort_keys=True))
if __name__=='__main__':main()
