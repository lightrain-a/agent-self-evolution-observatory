"""Core primitives for fresh PACTA-MSR/Qwen397 P0. No execution occurs on import."""
from __future__ import annotations
import ast,hashlib,json,os,re,tempfile,time,urllib.error,urllib.request
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from jinja2 import Template
from research_pipeline.c1_pacta_rb_qwen397 import AA_BASE_URL,atomic_bytes,atomic_json,canonical,sha256_file,sha256_text

ROOT=Path(__file__).resolve().parents[1]
POOL=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-fresh-pool-20260902.json'
POOL_SHA='2391967a3da363bcbbe87403599970854d7cf7ed82b249078b0469b36a8de59e'
SPLIT=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-pilot-split-20260902.json'
PROBE_SPECS=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-probe-specs-v2-20260902.json'
PROBE_SPECS_SHA='8b687006bf5308c53a95e48e9ab48a0c79957c015b2d32d17dafba9c584c76a0'
EXECUTION_CONTRACT=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-p0-execution-contract-20260902.json'
SOURCE_ROOT=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-source-20260902-v1')
OFFICIAL=Path('/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026')
CONFIG=OFFICIAL/'third_party/src/minisweagent/config/extra/swebench.yaml'
INSTRUCTION=OFFICIAL/'third_party/src/minisweagent/memory/instruction.py'
MODEL='qwen3.5-397b-a17b';MEMORY_PREFIX='\n\nBelow are some memory items that I accumulated from past interaction from the environment that may be helpful to solve the task. You can use it when you feel it\'s relevant. In each step, please first explicitly discuss if you want to use each memory item or not, and then take action.\n'
ACTION_RE=re.compile(r'```bash\n(.*?)\n```',re.S)
INPUT_CAP=10_000_000;OUTPUT_CAP=1_000_000
RATE_LIMIT_BACKOFF=(60,120)

def now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def sha(x:str)->str:return hashlib.sha256(x.encode()).hexdigest()
def safe_id(x:str)->str:return sha(x)[:12]
def parse_action(text:str)->str:
 found=ACTION_RE.findall(text)
 if len(found)!=1:raise ValueError(f'expected exactly one fenced bash action, found {len(found)}')
 action=found[0].strip()
 if not action:raise ValueError('empty action')
 return action
def tv(a:list[str],b:list[str])->float:
 if not a or not b:raise ValueError('empty distribution')
 ca,cb=Counter(a),Counter(b);keys=set(ca)|set(cb);return .5*sum(abs(ca[k]/len(a)-cb[k]/len(b)) for k in keys)
def gate(samples:dict[str,list[str]])->dict[str,Any]:
 for k in ('S1','S2','F1','F2'):
  if len(samples.get(k,[]))!=6:raise ValueError('HOLD_MSR_SHADOW_CALIBRATION')
 b1=tv(samples['S1'],samples['F1']);b2=tv(samples['S2'],samples['F2']);ws=tv(samples['S1'],samples['S2']);wf=tv(samples['F1'],samples['F2']);margin=min(b1,b2)-max(ws,wf)
 return {'B1':b1,'B2':b2,'WS':ws,'WF':wf,'margin':margin,'G':margin>0}
def load_instructions()->dict[str,str]:
 tree=ast.parse(INSTRUCTION.read_text());out={}
 for node in tree.body:
  if isinstance(node,ast.Assign):
   for t in node.targets:
    if isinstance(t,ast.Name) and t.id in {'SUCCESSFUL_SI','FAILED_SI'}:out[t.id]=ast.literal_eval(node.value)
 if set(out)!={'SUCCESSFUL_SI','FAILED_SI'}:raise RuntimeError('official writer instruction drift')
 return out
def memory_valid(text:str)->bool:
 return bool(text.strip()) and 1<=len(re.findall(r'^# Memory Item\s+\d+',text,re.M))<=3
def source_support()->dict[str,dict[str,Any]]:
 audit=load(SOURCE_ROOT/'support-audit.json')
 if audit.get('decision')!='MSR_SOURCE_POOL_10_QUALIFIED' or audit.get('valid')!=10 or audit.get('attempted')!=10:raise RuntimeError('MSR source pool not fully qualified')
 pool=load(POOL);by={u['source_task_id']:u for u in pool['units']};out={}
 for row in audit['rows']:
  if row.get('validity_status')!='TRAJECTORY_BACKED_VALID':raise RuntimeError('invalid source in support audit')
  u=by[row['source_task_id']];tp=Path(row['source_trajectory_path']);wp=Path(row['writer_input_trajectory_path'])
  if not tp.is_file() or sha256_file(tp)!=row['source_trajectory_sha256'] or not wp.is_file() or sha256_file(wp)!=row['writer_input_trajectory_sha256']:raise RuntimeError('source content address drift')
  out[u['unit_id']]={**u,'source_run':row}
 if len(out)!=10:raise RuntimeError('source support geometry')
 return out
def pilot_units()->tuple[list[dict[str,Any]],list[str],list[str]]:
 if sha256_file(POOL)!=POOL_SHA or sha256_file(PROBE_SPECS)!=PROBE_SPECS_SHA:raise RuntimeError('frozen PACTA-MSR input drift')
 allu=source_support();split=load(SPLIT);pilot=list(split['pilot']);sealed=list(split['sealed'])
 if len(pilot)!=8 or len(sealed)!=2 or set(pilot)|set(sealed)!=set(allu):raise RuntimeError('pilot split drift')
 return [allu[x] for x in pilot],sealed,list(split['random_gate_ranking_pre_shadow'])
def probe_specs()->dict[str,dict[str,Any]]:
 o=load(PROBE_SPECS)
 if o.get('status')!='MSR_10_PROBE_SPECS_V2_FROZEN_PRE_SOURCE_OUTCOME':raise RuntimeError('probe specs status drift')
 return {x['unit_id']:x for x in o['rows']}
def writer_prompt(u:dict[str,Any])->str:
 run=u['source_run'];return '**Query:** '+u['source_task']+'\n\n**Trajectory:**\n'+Path(run['writer_input_trajectory_path']).read_text()
def binding_state(selector:str,probe:dict[str,Any]|None)->str:
 if selector=='G0_STEP0':return 'Initial MiniSWEAgent decision state at /testbed. No shell action has executed and no repository observation has been returned yet.'
 if selector!='GPLUS_MATCHED_REVEAL' or probe is None:raise ValueError('invalid selector/probe')
 return 'Matched State Reveal command:\n'+probe['command']+'\n\nMatched State Reveal observation:\n'+probe['observation']['output']
def binding_prompt(memory:str,task:str,state:str)->str:
 return ('Given the reusable memory, the ultimate coding task, and the current agent state, produce one concise current-state action implication. Use the memory only when relevant, do not invent facts, and state what the agent should prioritize next. Output one sentence, at most 60 words, with no explanation.\n\nREUSABLE MEMORY:\n'+memory+'\n\nULTIMATE TASK:\n'+task+'\n\nCURRENT AGENT STATE:\n'+state)
def base_system(config:dict[str,Any])->str:return Template(config['agent']['system_template']).render()
def observation_text(config:dict[str,Any],obs:dict[str,Any])->str:return Template(config['agent']['action_observation_template']).render(output=obs)
def policy_messages(config:dict[str,Any],task:str,memory:str,binding:str|None,selector:str,probe:dict[str,Any]|None)->list[dict[str,str]]:
 system=base_system(config)+MEMORY_PREFIX+memory.strip()
 if binding is not None:system+='\n\nADAPTED SUPPORT:\n'+binding.strip()
 user=Template(config['agent']['instance_template']).render(task=task);messages=[{'role':'system','content':system},{'role':'user','content':user}]
 if selector=='GPLUS_MATCHED_REVEAL':
  if probe is None:raise ValueError('matched probe missing')
  assistant='THOUGHT: Execute the frozen branch-blind Matched State Reveal probe before branch-specific policy selection.\n\n```bash\n'+probe['command']+'\n```';messages.append({'role':'assistant','content':assistant});messages.append({'role':'user','content':observation_text(config,probe['observation'])})
 elif selector!='G0_STEP0':raise ValueError('unknown selector')
 return messages
def rate_limit_error(status:int|None,raw:bytes)->bool:
 if status not in (400,429):return False
 try:o=json.loads(raw.decode())
 except Exception:return False
 e=o.get('error') if isinstance(o,dict) else None;return isinstance(e,dict) and str(e.get('code') or e.get('type') or '')=='rate_limit_exceeded'

def scan_usage(root:Path)->tuple[int,int]:
 I=O=0
 for stage in ('writer','binder','shadow','final'):
  d=root/stage/'calls'
  if not d.is_dir():continue
  for p in d.glob('*.json'):
   try:
    x=load(p)
    if x.get('logical_success_receipt') is not True:continue
    u=x.get('usage') if isinstance(x.get('usage'),dict) else {};I+=int(u.get('prompt_tokens') or u.get('input_tokens') or 0);O+=int(u.get('completion_tokens') or u.get('output_tokens') or 0)
   except Exception:pass
 return I,O
class Provider:
 def __init__(self,key:str,root:Path,stage:str):
  if not key:raise RuntimeError('AA_API_KEY is not configured')
  self.key,self.root,self.stage=key,root,stage;self.stage_root=root/stage;self.calls=0
  self.base_input,self.base_output=scan_usage(root);self.input_tokens=self.base_input;self.output_tokens=self.base_output
 def call(self,messages:list[dict[str,str]],label:str,*,max_tokens:int,temperature:float)->dict[str,Any]:
  self.calls+=1;logical=self.calls
  for attempt in (1,2,3):
   packet={'model':MODEL,'messages':messages,'stream':False,'n':1,'max_completion_tokens':max_tokens,'temperature':temperature,'enable_thinking':False,'enable_search':False};safe={'endpoint':AA_BASE_URL+'/chat/completions','method':'POST','body':packet,'authorization_material_persisted':False,'logical_call':logical,'transport_attempt':attempt,'rate_limit_only_recovery':True}
   reqp=self.stage_root/'raw'/f'{logical:04d}-{safe_id(label)}-request-a{attempt}.json';resp=self.stage_root/'raw'/f'{logical:04d}-{safe_id(label)}-response-a{attempt}.json';reqsha=atomic_bytes(reqp,(canonical(safe)+'\n').encode());request=urllib.request.Request(AA_BASE_URL+'/chat/completions',data=canonical(packet).encode(),method='POST',headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'});status=None
   try:
    with urllib.request.urlopen(request,timeout=300) as x:status=int(x.status);raw=x.read()
   except urllib.error.HTTPError as e:status=int(e.code);raw=e.read()
   ressha=atomic_bytes(resp,raw);base={'schema_version':1,'timestamp_utc':now(),'stage':self.stage,'label':label,'logical_call':logical,'transport_attempt':attempt,'status_code':status,'request_path':str(reqp),'request_sha256':reqsha,'response_path':str(resp),'response_sha256':ressha,'persisted_before_parse':True,'requested_model':MODEL,'max_completion_tokens':max_tokens,'temperature':temperature}
   if status is None or not 200<=status<300:
    retry=rate_limit_error(status,raw) and attempt<3;receipt={**base,'parse_status':'NOT_PARSED_HTTP_ERROR','rate_limit':rate_limit_error(status,raw),'retryable':retry,'model_content_observed':False,'logical_success_receipt':False};atomic_json(self.stage_root/'calls'/f'{logical:04d}-{safe_id(label)}-a{attempt}.json',receipt)
    if retry:time.sleep(RATE_LIMIT_BACKOFF[attempt-1]);continue
    raise RuntimeError(f'provider HTTP {status}; raw preserved {ressha}')
   payload=json.loads(raw.decode());model=str(payload.get('model') or '');choice=payload['choices'][0];content=str(choice['message']['content']);finish=str(choice.get('finish_reason') or '');u=payload.get('usage') if isinstance(payload.get('usage'),dict) else {};self.input_tokens+=int(u.get('prompt_tokens') or u.get('input_tokens') or 0);self.output_tokens+=int(u.get('completion_tokens') or u.get('output_tokens') or 0);receipt={**base,'parse_status':'JSON_PARSED','response_id':str(payload.get('id') or ''),'resolved_model':model,'model_drift':model!=MODEL,'finish_reason':finish,'usage':u,'content_sha256':sha(content),'logical_success_receipt':True};atomic_json(self.stage_root/'calls'/f'{logical:04d}-{safe_id(label)}.json',receipt)
   if model!=MODEL:raise RuntimeError('STOP_PROVIDER_IDENTITY_DRIFT')
   if finish!='stop':raise RuntimeError('STOP_PROVIDER_OUTPUT_INCOMPLETE')
   if self.input_tokens>INPUT_CAP or self.output_tokens>OUTPUT_CAP:raise RuntimeError('STOP_P0_TOKEN_HARD_CAP')
   return {'content':content,'receipt':receipt}
  raise AssertionError('unreachable')
def phase_usage(p:Provider)->dict[str,int]:return {'phase_input_tokens':p.input_tokens-p.base_input,'phase_output_tokens':p.output_tokens-p.base_output,'cumulative_input_tokens':p.input_tokens,'cumulative_output_tokens':p.output_tokens}
