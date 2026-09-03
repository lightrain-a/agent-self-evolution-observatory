#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json,sha256_file,sha256_text
from research_pipeline.c1_pacta_rb_qwen397_t0_runtime import parse_action
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_q02_budget_20260902 as q02

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q03-precedence-contract-20260903.json'
PARENT=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-source-closeout-20260903.json'
PARENT_SHA='c218f298069cbc9238c7c831bc09cb96808ece0bb0c736f29f2977088942a4d0'
DEFAULT=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q03-precedence-20260903-v1')
BUDGET=32768; DEPTHS=(0,6,18); WITNESS='PACTA_BRIDGE_OK_V1'
BRIDGE=f'''# PACTA Provider-Interface Bridge Q0.3
This is an isolated sealed model-transport qualification workdir, NOT the task repository. Do not inspect this directory or any host filesystem.
PROJECT INSTRUCTION OVERRIDE: native AtomCode tools/function-call syntax MUST NOT be used, including list_directory, read_file, grep, glob, bash, use_skill, list_skills, subagents, web, MCP, or AtomGit tools. This overrides default AtomCode coding-tool preferences for this run. All synthetic task state is already inside EXPERIMENTAL_CONVERSATION_JSON.
Your only action surface is ordinary assistant text. Every response must be exactly:
{WITNESS}
THOUGHT: <brief reasoning about the next synthetic MiniSWEAgent step>
```bash
<exactly one proposed shell command, or commands connected with && / ||>
```
The fenced bash is TEXT ONLY; AtomCode must never execute it. Never emit native tool/function-call protocol. Preserve the fixture marker as a literal shell comment inside the fenced bash.
'''
FIXTURES=(
 ('q03-dir','directory_listing','Q03_DIR_MARKER','Inspect the synthetic project top level before choosing a file. Propose one read-only shell command with literal comment # Q03_DIR_MARKER.'),
 ('q03-find','filename_discovery','Q03_FIND_MARKER','Locate candidate paths named config_synthetic.toml below the synthetic current directory. Propose one read-only shell command with literal comment # Q03_FIND_MARKER.'),
 ('q03-search','content_search','Q03_SEARCH_MARKER','Search synthetic project files for SYNTHETIC_NEEDLE without modifying anything. Propose one shell command with literal comment # Q03_SEARCH_MARKER.'),
 ('q03-read','file_read','Q03_READ_MARKER','README_SYNTHETIC.md is the relevant synthetic file. Propose one read-only shell command to display its first useful section with literal comment # Q03_READ_MARKER.'),
 ('q03-git','git_inspection','Q03_GIT_MARKER','Inspect synthetic repository status plus a short recent log without changing state. Propose one shell command with literal comment # Q03_GIT_MARKER.'),
 ('q03-py','python_source_inventory','Q03_PY_MARKER','Inventory Python source files under synthetic src/ before choosing one to read. Propose one read-only shell command with literal comment # Q03_PY_MARKER.'),
 ('q03-subdir','subdirectory_inspection','Q03_SUBDIR_MARKER','The likely synthetic implementation is under src/widgets/. Propose one read-only shell command to inspect that subtree with literal comment # Q03_SUBDIR_MARKER.'),
 ('q03-multi','multi_signal_read_only_inspection','Q03_MULTI_MARKER','Gather a compact synthetic view of top-level files plus occurrences of SYNTHETIC_API. Propose one shell command or &&/|| chain with literal comment # Q03_MULTI_MARKER.'),
)

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def msgs(row,depth):
 fid,cat,marker,task=row
 out=[{'role':'system','content':'Synthetic offline MiniSWEAgent policy. Return the next assistant message only, as ordinary text with exactly one fenced bash proposal. Do not execute it.'},{'role':'user','content':task}]
 for i in range(1,depth+1):
  out += [{'role':'assistant','content':f"THOUGHT: fixed synthetic history {i}.\n```bash\nprintf 'SYNTHETIC_HISTORY_{i:02d}'\n```"},{'role':'user','content':f'SYNTHETIC_OBSERVATION_{i:02d}: prior proposal recorded; no host action executed.'}]
 if depth: out.append({'role':'user','content':f'Continue with the next read-only shell proposal and preserve literal comment # {marker}.'})
 return out

def stem(index,label): return f"{index:04d}__{re.sub(r'[^A-Za-z0-9_.-]+','_',label)[:120]}"
def raw_path(root,index,label): return root/'q03'/'raw'/f'{stem(index,label)}.stdout.jsonl'
def audit_jsonl(text):
 parts=[]; usage=[]; tools=[]; retries=[]; errors=[]; turns=[]; model=''
 for line in text.splitlines():
  try:r=json.loads(line)
  except: continue
  t=str(r.get('type') or '')
  if t=='run.started': model=str(r.get('model') or '')
  elif t=='message.delta' and isinstance(r.get('text'),str): parts.append(r['text'])
  elif t=='usage': usage.append(r)
  elif t.startswith('tool.') or t.startswith('tool_') or t in {'tool_start','tool_result','permission_request'}: tools.append(r)
  elif t=='retry': retries.append(r)
  elif t=='error': errors.append(str(r.get('message') or ''))
  elif t=='turn.completed': turns.append(r)
 return {'text':''.join(parts).strip(),'model':model,'usage':usage,'tools':tools,'trunc':any(str(x.get('kind') or '')=='output_truncation' for x in retries),'maxrounds':any(str(x.get('stop_reason') or '')=='MaxRounds' or int(x.get('exit_code') or 0)!=0 for x in turns) or any('max rounds' in x.lower() for x in errors),'errors':errors}

def verify_parent():
 if not PARENT.is_file() or sha256_file(PARENT)!=PARENT_SHA: raise RuntimeError('STOP_Q03_PARENT_DRIFT')
 o=json.loads(PARENT.read_text())
 if o.get('status')!='HOLD_FRESH2_ATOMGIT_MSR_SOURCE_POOL_RETIRED_PROVIDER_RUNTIME_INTERCEPTION' or int(o.get('attempted_sources') or 0)!=1 or o.get('pool_retired') is not True or int(o.get('unattempted_sources') or 0)!=9: raise RuntimeError('STOP_Q03_PARENT_VERDICT_DRIFT')

def prepare(root):
 if root.exists(): raise RuntimeError('Q03 root exists; no overwrite')
 verify_parent(); root.mkdir(parents=True); wd=root/'empty-workdir'; wd.mkdir(); bp=wd/'.atomcode.md'; bp.write_text(BRIDGE); os.chmod(bp,0o600)
 cfg=root/'configs'/f'max-{BUDGET}.toml'; q02.write_config(cfg,BUDGET)
 version=subprocess.run([str(q02.ATOMCODE),'--version'],text=True,capture_output=True,check=True).stdout.strip()
 if '5.0.9' not in version: raise RuntimeError('STOP_Q03_ATOMCODE_VERSION_DRIFT')
 manifest=[]
 for row in FIXTURES:
  for d in DEPTHS:
   m=msgs(row,d); manifest.append({'fixture_id':row[0],'category':row[1],'marker':row[2],'history_pairs':d,'messages_sha256':sha256_text(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':'))),'prompt_sha256':sha256_text(q02.serialize_messages(m))})
 out={'schema_version':1,'created_at_utc':now(),'status':'ATOMGIT_QWEN38_Q03_PREPARE_PASS','contract_sha256':sha256_file(CONTRACT),'parent_closeout_sha256':PARENT_SHA,'atomcode_version':version,'atomcode_binary_sha256':sha256_file(q02.ATOMCODE),'provider_config_sha256':sha256_file(cfg),'bridge_sha256':sha256_file(bp),'bridge_witness':WITNESS,'fixture_manifest':manifest,'fixture_count':8,'total_calls':24,'history_depths':list(DEPTHS),'scientific_source_tasks_used':0,'future_task_executions':0,'writer_calls':0,'binder_calls':0,'probe_calls':0,'shadow_calls':0,'final_calls':0}
 atomic_json(root/'prepare.json',out); return out

def run(root):
 prep=json.loads((root/'prepare.json').read_text())
 if prep.get('status')!='ATOMGIT_QWEN38_Q03_PREPARE_PASS' or prep.get('total_calls')!=24: raise RuntimeError('STOP_Q03_PREPARE_INVALID')
 if (root/'q03-result.json').exists() or (root/'q03').exists(): raise RuntimeError('Q03 panel exists; no retry')
 if sha256_file(root/'empty-workdir'/'.atomcode.md')!=prep['bridge_sha256']: raise RuntimeError('STOP_Q03_BRIDGE_DRIFT')
 rows=[]; idx=0
 for fixture in FIXTURES:
  for d in DEPTHS:
   idx+=1; label=f'{fixture[0]}__h{d}'; base=q02.invoke(root,'q03',idx,msgs(fixture,d),BUDGET,label); raw=raw_path(root,idx,label).read_text() if raw_path(root,idx,label).is_file() else ''; a=audit_jsonl(raw); text=a['text'] or str(base.get('assistant_text') or '')
   try: action=parse_action(text); parsed=True
   except Exception as e: action=''; parsed=False; parse_error=f'{type(e).__name__}:{e}'
   witness=text.startswith(WITNESS+'\n'); thought='THOUGHT:' in text; marker=fixture[2] in action; identity=a['model'] in {q02.MODEL,q02.PROFILE}; one_usage=len(a['usage'])==1
   passed=bool(base.get('returncode')==0 and identity and one_usage and len(a['tools'])==0 and not a['trunc'] and not a['maxrounds'] and witness and thought and parsed and marker)
   row={**base,'fixture_id':fixture[0],'category':fixture[1],'marker':fixture[2],'history_pairs':d,'started_model':a['model'],'model_identity_pass':identity,'usage_row_count':len(a['usage']),'codingplan_requests':1 if one_usage else len(a['usage']),'native_tool_event_count':len(a['tools']),'native_tool_event_types':[str(x.get('type') or '') for x in a['tools']],'native_tool_event_sha256s':[sha256_text(json.dumps(x,ensure_ascii=False,sort_keys=True)) for x in a['tools']],'output_truncation_event':a['trunc'],'max_rounds_event':a['maxrounds'],'error_messages':a['errors'],'bridge_witness_pass':witness,'thought_marker_pass':thought,'action_parse_pass':parsed,'action_parse_failure':None if parsed else parse_error,'action_marker_pass':marker,'action_sha256':sha256_text(action) if action else '','pass':passed}
   atomic_json(root/'q03'/'adjudicated'/f'{stem(idx,label)}.json',row); rows.append(row); print(json.dumps({'index':idx,'fixture':fixture[0],'history':d,'pass':passed,'returncode':base.get('returncode'),'tool_events':len(a['tools']),'witness':witness,'action':parsed},sort_keys=True),flush=True)
 qualified=sum(bool(x['pass']) for x in rows); passed=qualified==24
 out={'schema_version':1,'created_at_utc':now(),'status':'ATOMGIT_QWEN38_Q03_PROJECT_INSTRUCTION_PRECEDENCE_PASS' if passed else 'STOP_ATOMGIT_QWEN38_Q03_PROJECT_INSTRUCTION_PRECEDENCE','pass':passed,'qualified':qualified,'total':24,'native_tool_event_count':sum(x['native_tool_event_count'] for x in rows),'nonzero_return_count':sum(int(x.get('returncode') or 0)!=0 for x in rows),'witness_pass_count':sum(x['bridge_witness_pass'] for x in rows),'action_parse_pass_count':sum(x['action_parse_pass'] for x in rows),'action_marker_pass_count':sum(x['action_marker_pass'] for x in rows),'model_identity_pass_count':sum(x['model_identity_pass'] for x in rows),'output_truncation_count':sum(x['output_truncation_event'] for x in rows),'max_rounds_count':sum(x['max_rounds_event'] for x in rows),'rows':rows,'fresh3_authorized':passed,'scientific_source_tasks_used':0,'future_task_executions':0,'writer_calls':0,'binder_calls':0,'probe_calls':0,'shadow_calls':0,'final_calls':0,'claim_authority':'NO_NEW_PACTA_MSR_EFFECT_EVIDENCE'}
 atomic_json(root/'q03-result.json',out); return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=DEFAULT);p.add_argument('--phase',choices=('prepare','run'),required=True);a=p.parse_args();o=prepare(a.root) if a.phase=='prepare' else run(a.root);print(json.dumps(o,ensure_ascii=False,sort_keys=True))
if __name__=='__main__': main()
