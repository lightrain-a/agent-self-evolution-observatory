from __future__ import annotations

import argparse,json,os,signal,sys
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld,prepare_appworld_runtime_root
from research_pipeline.agent_constraint_externality_runner_core import sha256_value

MCP_PROTOCOL_VERSION='2025-11-25'

def _send(x): sys.stdout.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n'); sys.stdout.flush()
def _text(t,e=False): return {'content':[{'type':'text','text':t}],'isError':e}
def _write(path,p):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(p,ensure_ascii=False,indent=2,sort_keys=True)+'\n'); os.replace(tmp,path)

def main():
 p=argparse.ArgumentParser(); p.add_argument('--case-json',type=Path,required=True); p.add_argument('--appworld-root',type=Path,required=True); p.add_argument('--runtime-root',type=Path,required=True); p.add_argument('--task-id',required=True); p.add_argument('--progress',type=Path,required=True); p.add_argument('--tool-call-cap',type=int,required=True); a=p.parse_args()
 case=json.loads(a.case_json.read_text()); family={'family_id':case['case_id'],'fixture':case['fixture']}; arm={'task_instruction':case['task_instruction']}; mat=prepare_appworld_runtime_root(a.appworld_root,a.runtime_root,family=family,arm=arm,task_id=a.task_id)
 w=AppWorldToolWorld(runtime_root=a.runtime_root,task_id=a.task_id,experiment_name='ace-sq0-v2r1-transport',seed=1,allowed_apps=set(case['fixture']['apps']),max_interactions=a.tool_call_cap); tools={r['name']:r for r in w.tools}; calls=0; closed=False
 def persist(status,**extra):
  x={'schema_version':'ace-sq0-v2r1-transport-progress-v1','case_id':case['case_id'],'status':status,'tool_call_count':calls,'tool_call_cap':a.tool_call_cap,'initial_snapshot_sha256':mat['initial_snapshot_sha256'],'instruction_sha256':mat['instruction_sha256'],**extra}; x['content_sha256']=sha256_value(x); _write(a.progress,x)
 def close(*_):
  nonlocal closed
  if closed:return
  closed=True
  try:w.save_state();persist('CLOSED_STATE_SAVED')
  except:pass
  try:w.close()
  except:pass
 signal.signal(signal.SIGTERM,lambda *_:(close(),sys.exit(0))); signal.signal(signal.SIGINT,lambda *_:(close(),sys.exit(0))); persist('PROCESS_READY',tool_count=len(tools))
 try:
  for line in sys.stdin:
   try:m=json.loads(line)
   except:continue
   method,rid=m.get('method'),m.get('id')
   if method=='initialize': persist('MCP_INITIALIZED',tool_count=len(tools)); _send({'jsonrpc':'2.0','id':rid,'result':{'protocolVersion':MCP_PROTOCOL_VERSION,'capabilities':{'tools':{}},'serverInfo':{'name':'ace-v2r1-transport','version':'1.0'},'instructions':'Use only AppWorld MCP tools. Any ~/ path is virtual AppWorld state, never host filesystem.'}})
   elif method=='notifications/initialized':continue
   elif method=='tools/list':
    rows=[{'name':r['name'],'description':r.get('description',''),'inputSchema':r['parameters']} for r in w.tools];persist('TOOLS_LISTED',tool_count=len(rows));_send({'jsonrpc':'2.0','id':rid,'result':{'tools':rows}})
   elif method=='tools/call':
    q=m.get('params') or {};name=str(q.get('name',''));args=q.get('arguments') or {}
    if name not in tools:_send({'jsonrpc':'2.0','id':rid,'result':_text('Unknown AppWorld tool',True)});continue
    calls+=1
    if calls>a.tool_call_cap:persist('TOOL_CALL_CAP_EXCEEDED',attempted_tool=name);_send({'jsonrpc':'2.0','id':rid,'result':_text('AppWorld tool-call cap exceeded',True)});continue
    try:o=w.execute(name,dict(args));w.save_state();err=str(o).lstrip().startswith('Execution failed');persist('STATE_SAVED_AFTER_TOOL',last_tool=name,last_tool_result_error=err);_send({'jsonrpc':'2.0','id':rid,'result':_text(str(o),err)})
    except Exception as exc:persist('TOOL_EXECUTION_FAILED',last_tool=name,failure_class=type(exc).__name__,message=str(exc)[:200]);_send({'jsonrpc':'2.0','id':rid,'result':_text(f'{type(exc).__name__}: {exc}',True)})
 finally:close()
if __name__=='__main__':main()
