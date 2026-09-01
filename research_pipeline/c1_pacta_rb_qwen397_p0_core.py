"""Frozen primitives for the prospective ReasoningBank × Qwen397 PACTA P0."""
from __future__ import annotations
import ast,json,os,re,urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import yaml
from jinja2 import Template
from research_pipeline.c1_pacta_rb_qwen397 import AA_BASE_URL,PILOT_SALT,RANDOM_SALT,atomic_bytes,atomic_json,sha256_file,sha256_text

ROOT=Path(__file__).resolve().parents[1]
OFFICIAL=Path('/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026')
INSTRUCTION=OFFICIAL/'third_party/src/minisweagent/memory/instruction.py'
CONFIG=OFFICIAL/'third_party/src/minisweagent/config/extra/swebench.yaml'
FRESH=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-deepseek-p0-20260831-v1/fresh-pool.json')
CUMULATIVE=ROOT/'paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-rb-qwen397-t0-cumulative-pool-9-20260901.json'
Q0=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-q0-20260831-v2/provider-binding.json')
DEFAULT_RUN=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-p0-20260901-v1')
MODEL='qwen3.5-397b-a17b'
EXPECTED={
 'instruction':'08e11fbeac1ba9e20d1dafb20728be24194b56bdfea33f05f6a1220ae2cc9bae',
 'config':'d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41',
 'fresh':'52ad6ea9308a4d408cbde92ccef5a0b4619e454d12bb165305d44f4195ac402e',
 'cumulative':'6ab3b77146e194de76f20abb238ef106c266ba084b44df3d7e56c4212eb31124'}
WRITER_MAX=2048;BINDER_MAX=512;FIRST_DECISION_MAX=512
WRITER_TEMP=0.0;BINDER_TEMP=0.0;POLICY_TEMP=0.2
INPUT_CAP=5_000_000;OUTPUT_CAP=500_000
MEMORY_PREFIX='\n\nBelow are some memory items that I accumulated from past interaction from the environment that may be helpful to solve the task. You can use it when you feel it\'s relevant. In each step, please first explicitly discuss if you want to use each memory item or not, and then take action.\n'
SCB_PREFIX='\n\nState-conditioned support derived from the retrieved memory for the current decision state. Use it only when relevant:\n'
INITIAL_STATE='This is the initial MiniSWEAgent decision state. The agent is in /testbed. No shell action has been issued and no environment observation has been returned yet.'
BINDER_INSTRUCTION='Given the reusable memory, the ultimate coding task, and the current agent state, produce one concise current-state action implication for a coding agent. Use the memory only when relevant, do not invent repository facts, and state what the agent should prioritize next. Output one sentence, at most 60 words, with no explanation.'
MEMORY_ITEM_RE=re.compile(r'^# Memory Item\s+\S+',re.MULTILINE)

def now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load(path:Path)->dict[str,Any]:return json.loads(path.read_text(encoding='utf-8'))
def verify_inputs()->dict[str,str]:
 actual={'instruction':sha256_file(INSTRUCTION),'config':sha256_file(CONFIG),'fresh':sha256_file(FRESH),'cumulative':sha256_file(CUMULATIVE)}
 if actual!=EXPECTED:raise RuntimeError(f'STOP_P0_INPUT_HASH_DRIFT:{actual}')
 return actual

def binding()->dict[str,str]:
 b=load(Q0);requested=str(b.get('requested_model') or '');resolved=str(b.get('resolved_model') or b.get('resolved_or_returned_model') or '')
 if requested!=MODEL or resolved!=MODEL or not b.get('identity_pass'):raise RuntimeError('STOP_QWEN397_MODEL_BINDING_DRIFT')
 return {'requested_model':requested,'resolved_model':resolved,'binding_sha256':sha256_file(Q0)}
def require_key()->str:
 key=os.environ.get('AA_API_KEY','')
 if not key:raise RuntimeError('STOP_PROVIDER_CREDENTIAL_NOT_CONFIGURED')
 return key

def official_instructions()->dict[str,str]:
 tree=ast.parse(INSTRUCTION.read_text(encoding='utf-8'));out={}
 for node in tree.body:
  if isinstance(node,ast.Assign):
   for target in node.targets:
    if isinstance(target,ast.Name) and target.id in {'SUCCESSFUL_SI','FAILED_SI'}:out[target.id]=ast.literal_eval(node.value)
 if set(out)!={'SUCCESSFUL_SI','FAILED_SI'}:raise RuntimeError('STOP_OFFICIAL_WRITER_INSTRUCTIONS_UNAVAILABLE')
 return out

def units()->list[dict[str,Any]]:
 fresh=load(FRESH);cum=load(CUMULATIVE);by={u['source_task_id']:u for u in fresh['units']};rows=[]
 for valid in cum['valid_units']:
  source=valid['source_task_id'];u=dict(by[source])
  if sha256_text(str(u['source_task']))!=valid['task_sha256']:raise RuntimeError(f'STOP_SOURCE_TASK_HASH_DRIFT:{source}')
  if sha256_file(Path(valid['source_trajectory_path']))!=valid['source_trajectory_sha256']:raise RuntimeError(f'STOP_SOURCE_TRAJECTORY_HASH_DRIFT:{source}')
  if sha256_file(Path(valid['writer_input_trajectory_path']))!=valid['writer_input_trajectory_sha256']:raise RuntimeError(f'STOP_WRITER_INPUT_HASH_DRIFT:{source}')
  u.update(valid);u['unit_id']=str(u['unit_id']);rows.append(u)
 if len(rows)!=9 or len({u['task_family'] for u in rows})!=9:raise RuntimeError('STOP_CUMULATIVE_POOL_GEOMETRY')
 return rows
def ranked(rows:list[dict[str,Any]],salt:str)->list[dict[str,Any]]:return sorted(rows,key=lambda u:(sha256_text(salt+'|'+u['unit_id']),u['unit_id']))
def split()->tuple[list[dict[str,Any]],list[dict[str,Any]]]:
 r=ranked(units(),PILOT_SALT);return r[:6],r[6:]

def writer_messages(unit:dict[str,Any],branch:str)->tuple[list[dict[str,str]],str]:
 ins=official_instructions();trajectory=Path(unit['writer_input_trajectory_path']).read_text(encoding='utf-8');context=f"**Query:** {unit['source_task']}\n\n**Trajectory:**\n{trajectory}"
 system=ins['SUCCESSFUL_SI' if branch=='success' else 'FAILED_SI'].strip();return [{'role':'system','content':system},{'role':'user','content':context}],context
def validate_memory(text:str)->tuple[str,int]:
 memory=text.strip();count=len(MEMORY_ITEM_RE.findall(memory))
 if not memory or count<1 or count>3:raise RuntimeError(f'STOP_WRITER_REALIZATION_FORMAT:item_count={count}')
 if any(memory.count(x)<count for x in ('## Title','## Description','## Content')):raise RuntimeError('STOP_WRITER_REALIZATION_FORMAT:missing_fields')
 return memory,count

def binder_messages(unit:dict[str,Any],memory:str)->tuple[list[dict[str,str]],str]:
 prompt=BINDER_INSTRUCTION+'\n\nREUSABLE MEMORY:\n'+memory+'\n\nULTIMATE CODING TASK:\n'+str(unit['future_task'])+'\n\nCURRENT AGENT STATE:\n'+INITIAL_STATE
 return [{'role':'user','content':prompt}],prompt
def validate_binding(text:str)->tuple[str,int]:
 note=' '.join(text.strip().splitlines()).strip();words=len(note.split())
 if not note or words>60 or '```' in note or note.startswith('#'):raise RuntimeError(f'STOP_BINDER_REALIZATION_FORMAT:words={words}')
 return note,words

def policy_messages(unit:dict[str,Any],memory:str,note:str|None)->list[dict[str,str]]:
 cfg=yaml.safe_load(CONFIG.read_text(encoding='utf-8'));system=Template(cfg['agent']['system_template']).render()+MEMORY_PREFIX+memory.strip()
 if note is not None:system+=SCB_PREFIX+note.strip()
 user=Template(cfg['agent']['instance_template']).render(task=str(unit['future_task']))
 return [{'role':'system','content':system},{'role':'user','content':user}]

class Provider:
 def __init__(self,key:str,root:Path,requested:str,resolved:str):
  self.key,self.root,self.requested,self.resolved=key,root,requested,resolved;self.calls=0
  inp=out=0
  for stage in ('writer','binder','shadow','final'):
   paths=(root/stage/'calls').glob('*.json') if (root/stage/'calls').is_dir() else []
   for p in paths:
    try:
     o=load(p);u=o.get('usage') if isinstance(o.get('usage'),dict) else {};inp+=int(u.get('prompt_tokens') or u.get('input_tokens') or 0);out+=int(u.get('completion_tokens') or u.get('output_tokens') or 0)
    except Exception:pass
  self.input_tokens,self.output_tokens=inp,out;self.start_input,self.start_output=inp,out
 def phase_usage(self)->dict[str,int]:return {'input_tokens':self.input_tokens-self.start_input,'output_tokens':self.output_tokens-self.start_output,'cumulative_input_tokens':self.input_tokens,'cumulative_output_tokens':self.output_tokens}
 def call(self,stage:str,case_id:str,messages:list[dict[str,str]],max_tokens:int,temp:float)->dict[str,Any]:
  if self.input_tokens>=INPUT_CAP or self.output_tokens>=OUTPUT_CAP:raise RuntimeError('STOP_SCIENTIFIC_TOKEN_HARD_CAP')
  self.calls+=1;packet={'model':self.requested,'messages':messages,'stream':False,'n':1,'max_completion_tokens':max_tokens,'temperature':temp,'enable_thinking':False,'enable_search':False}
  safe={'endpoint':AA_BASE_URL+'/chat/completions','method':'POST','body':packet,'authorization_material_persisted':False,'provider_retries':0,'stage':stage,'case_id':case_id}
  stem=f"{self.calls:04d}__{re.sub(r'[^A-Za-z0-9_.-]+','_',case_id)[:140]}";reqp=self.root/stage/'raw'/f'{stem}.request.json';resp=self.root/stage/'raw'/f'{stem}.response.json'
  reqsha=atomic_bytes(reqp,(json.dumps(safe,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode());request=urllib.request.Request(AA_BASE_URL+'/chat/completions',data=json.dumps(packet,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode(),method='POST',headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'})
  status=None
  try:
   with urllib.request.urlopen(request,timeout=240) as x:status=int(x.status);raw=x.read()
  except urllib.error.HTTPError as e:status=int(e.code);raw=e.read()
  ressha=atomic_bytes(resp,raw);base={'schema_version':1,'created_at_utc':now(),'case_id':case_id,'stage':stage,'status_code':status,'request_path':str(reqp),'request_sha256':reqsha,'response_path':str(resp),'response_sha256':ressha,'persisted_before_parse':True,'provider_retries':0,'requested_model':self.requested}
  if status is None or not 200<=status<300:
   atomic_json(self.root/stage/'calls'/f'{stem}.json',{**base,'parse_status':'NOT_PARSED_HTTP_ERROR'});raise RuntimeError(f'STOP_PROVIDER_HTTP_{status};raw={ressha}')
  try:p=json.loads(raw.decode('utf-8'))
  except Exception:
   atomic_json(self.root/stage/'calls'/f'{stem}.json',{**base,'parse_status':'JSON_PARSE_FAILED'});raise
  model=str(p.get('model') or '');usage=p.get('usage') if isinstance(p.get('usage'),dict) else {};inp=int(usage.get('prompt_tokens') or usage.get('input_tokens') or 0);out=int(usage.get('completion_tokens') or usage.get('output_tokens') or 0);self.input_tokens+=inp;self.output_tokens+=out
  content=str(p['choices'][0]['message']['content']);finish=str(p['choices'][0].get('finish_reason') or '')
  call={**base,'parse_status':'JSON_PARSED','resolved_model':model,'model_drift':model!=self.resolved,'response_id':str(p.get('id') or ''),'finish_reason':finish,'usage':usage,'content_sha256':sha256_text(content)};atomic_json(self.root/stage/'calls'/f'{stem}.json',call)
  if model!=self.resolved:raise RuntimeError('STOP_PROVIDER_IDENTITY_DRIFT')
  if self.input_tokens>INPUT_CAP or self.output_tokens>OUTPUT_CAP:raise RuntimeError('STOP_SCIENTIFIC_TOKEN_HARD_CAP')
  return {'content':content,'provider':call}
