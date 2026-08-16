from __future__ import annotations
import argparse,hashlib,json,math,os,pathlib
from collections import Counter

def sha(path:pathlib.Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(32<<20),b''):h.update(b)
 return h.hexdigest()

def validate(model:pathlib.Path,actor:pathlib.Path,source_revision:str,smoke:bool)->dict:
 import torch
 from safetensors import safe_open
 from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer
 expected_actor={
 'model_world_size_4_rank_0.pt':(7615805455,'82336e369faec11529d7b6b2f1570531be302c546a2fcc3a20f6bc2bf0d6a1bd'),
 'model_world_size_4_rank_1.pt':(7615805455,'e0bfd396384c412a20c5ba942f105fea3ea3c5039ff8f0c5bae7d89b6ebb8366'),
 'model_world_size_4_rank_2.pt':(7615805455,'839b26609fdb601119b1dbd7a963ca97d2150bcfdd304cc9de53868ecbeea0be'),
 'model_world_size_4_rank_3.pt':(7615805455,'69931c4d203a86d7cbf6eea6e8248d82b76ae0b189e5cabd5bdeb5043cd70b3e')}
 actor_rows=[]
 for name,(size,expected) in expected_actor.items():
  p=actor/name
  if not p.is_file() or p.stat().st_size!=size:raise RuntimeError(f'actor-size:{name}')
  got=sha(p)
  if got!=expected:raise RuntimeError(f'actor-sha:{name}:{got}')
  actor_rows.append({'file':name,'bytes':size,'sha256':got})
 config=AutoConfig.from_pretrained(model,trust_remote_code=True);tokenizer=AutoTokenizer.from_pretrained(model,trust_remote_code=True)
 arch=(config.architectures or [None])[0]
 if arch!='Qwen2ForCausalLM':raise RuntimeError(f'architecture:{arch}')
 with torch.device('meta'): skeleton=AutoModelForCausalLM.from_config(config,dtype=torch.bfloat16,trust_remote_code=True)
 expected_state=skeleton.state_dict();expected_keys=set(expected_state);param_numel=sum(p.numel() for p in skeleton.parameters())
 tensor_files=sorted(model.glob('*.safetensors'))
 if not tensor_files:raise RuntimeError('no-safetensors')
 actual_keys=set();tensor_numel=0;dtypes=Counter()
 for f in tensor_files:
  with safe_open(f,framework='pt',device='cpu') as sf:
   for k in sf.keys():
    if k in actual_keys:raise RuntimeError(f'duplicate-key:{k}')
    sl=sf.get_slice(k);shape=tuple(sl.get_shape());dtype=str(sl.get_dtype());actual_keys.add(k);tensor_numel+=math.prod(shape);dtypes[dtype]+=1
 missing=sorted(expected_keys-actual_keys);unexpected=sorted(actual_keys-expected_keys)
 if missing or unexpected:raise RuntimeError(f'state-key-mismatch missing={missing[:20]} unexpected={unexpected[:20]}')
 if set(dtypes)-{'BF16'}:raise RuntimeError(f'non-bf16-tensors:{dict(dtypes)}')
 files=[]
 for p in sorted(x for x in model.iterdir() if x.is_file()):files.append({'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
 smoke_result={'requested':smoke,'passed':False}
 if smoke:
  from vllm import LLM,SamplingParams
  llm=LLM(model=str(model),tokenizer=str(model),tensor_parallel_size=1,gpu_memory_utilization=.90,max_model_len=1024,trust_remote_code=True,enable_prefix_caching=False,enforce_eager=True)
  prompt='Reply with exactly: OK'
  rendered=tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
  out=llm.generate([rendered],SamplingParams(temperature=0,max_tokens=8),use_tqdm=False)[0].outputs[0].text.strip()
  if not out:raise RuntimeError('vllm-smoke-empty')
  smoke_result={'requested':True,'passed':True,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'response_sha256':hashlib.sha256(out.encode()).hexdigest(),'response_nonempty':True}
 payload={'schema_version':'1.0','artifact_kind':'pre-outcome-merged-policy-manifest','status':'VALIDATED_PRE_OUTCOME_HF_MODEL' if smoke_result['passed'] else 'STATIC_VALIDATED_PRE_OUTCOME_HF_MODEL','source_repo':'Jianwen/Alfworld-7B-RL','source_revision':source_revision,'source_actor_dir':str(actor),'source_actor_files':actor_rows,'model_dir':str(model),'architecture':arch,'parameters':param_numel,'state_tensor_numel':tensor_numel,'tensor_bytes':tensor_numel*2,'tensor_dtype_counts':dict(dtypes),'state_key_count':len(actual_keys),'tokenizer_class':type(tokenizer).__name__,'vocab_size':len(tokenizer),'files':files,'smoke':smoke_result,'environment_outcomes_read':False,'scientific_authority':False}
 return payload

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--model',type=pathlib.Path,required=True);ap.add_argument('--actor',type=pathlib.Path,required=True);ap.add_argument('--source-revision',default='2ce16cb90e6357892dde201928279d4513d35c59');ap.add_argument('--smoke',action='store_true');ap.add_argument('--output',type=pathlib.Path,required=True);a=ap.parse_args();p=validate(a.model,a.actor,a.source_revision,a.smoke);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');print(json.dumps(p,ensure_ascii=False))
if __name__=='__main__':main()
