#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil
from collections import Counter
from pathlib import Path

ORIGINAL_SOURCES=[21,22,23,25]
ORIGINAL_FUTURES=[164,385,387,388]
THRESHOLD=0.3; MAX_LEN=256
EXPECTED={'task_config':'d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6','memory_py':'d4f499fe3321571db7f631132b939cf5b9ab121f24d81fa80637df221aad6386','retriever_py':'bab30513553a0133ea463f45a0716627bcf099ab34a1ce969581442d42278f13','config':'953f9c0d463486b10a6871cc2fd59f223b2c70184f49815e7efbcab5d8908b41','tokenizer':'be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037','pool':'4be450dde3b0273bb9787637cfbd28fe04a7ba6ab9d36ac48e92b11e350ffc23','modules':'84e40c8e006c9b1d6c122e02cba9b02458120b5fb0c87b746c41e0207cf642cf','weights':'53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db','b2':'PLACEHOLDER_B2','b1':'88ba6ee7e3fae02f4c461d8fa421b67f4211a9259f597cdcc36e927fe9cdde45'}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path):return json.loads(p.read_text())
def req(x,msg):
 if not x:raise RuntimeError(msg)
def writej(p:Path,d):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');os.replace(t,p)

def deterministic_string_match(task:dict)->bool:
 ev=task.get('eval') or {}; types=list(ev.get('eval_types') or []); refs=ev.get('reference_answers') or {}
 return types==['string_match'] and bool(refs) and set(refs).issubset({'must_include','exact_match'})

def eval_class(task:dict)->str:
 if deterministic_string_match(task): return 'OFFLINE_DETERMINISTIC_STRING_MATCH'
 ev=task.get('eval') or {}; types=list(ev.get('eval_types') or []); refs=ev.get('reference_answers') or {}
 if types==['string_match'] and 'fuzzy_match' in refs:return 'LLM_FUZZY_OR_UA_REQUIRED'
 if any(x in types for x in ['url_match','program_html']):return 'LIVE_ENVIRONMENT_REQUIRED'
 return 'OTHER_OR_MIXED_EVALUATOR'

def main():
 ap=argparse.ArgumentParser();
 for n in ['task_config','memory_py','retriever_py','snapshot','weights','b2_evidence','b1_result','parquet','run_root','output']: ap.add_argument('--'+n.replace('_','-'),required=True,type=Path)
 a=ap.parse_args()
 # b2 is intentionally bound at runtime because it is generated after B2-R1 completion.
 for p,h,label in [(a.task_config,EXPECTED['task_config'],'task config'),(a.memory_py,EXPECTED['memory_py'],'memory.py'),(a.retriever_py,EXPECTED['retriever_py'],'retriever.py'),(a.snapshot/'config.json',EXPECTED['config'],'model config'),(a.snapshot/'tokenizer.json',EXPECTED['tokenizer'],'tokenizer'),(a.snapshot/'1_Pooling/config.json',EXPECTED['pool'],'pool'),(a.snapshot/'modules.json',EXPECTED['modules'],'modules'),(a.weights,EXPECTED['weights'],'weights'),(a.b1_result,EXPECTED['b1'],'B1 result')]:req(p.is_file() and sha(p)==h,f'{label} SHA drift')
 b2=load(a.b2_evidence);req(b2['status']=='B2_BROAD_WRITE_CHANNEL_SUPPORTED' and b2['combined_complete_pairs']==20,'B2 breadth evidence not ready')
 b1=load(a.b1_result);req(b1['status']=='COMPLETE_ZERO_PROVIDER_CALLS','B1 drift')
 modules=load(a.snapshot/'modules.json');pool=load(a.snapshot/'1_Pooling/config.json');sb=load(a.snapshot/'sentence_bert_config.json')
 req([x['type'].split('.')[-1] for x in modules]==['Transformer','Pooling','Normalize'],'module drift');req(pool['pooling_mode_mean_tokens'] is True and not pool['pooling_mode_cls_token'] and not pool['pooling_mode_max_tokens'],'pool drift');req(int(sb['max_seq_length'])==MAX_LEN,'max len drift')
 mt=a.memory_py.read_text();rt=a.retriever_py.read_text();req('task_pools = [v["task_description"] for v in self.reasoningbank_memory.values()]' in mt,'key drift');req('if sim >= threshold:' in rt,'threshold drift')
 tasks=load(a.task_config);req(isinstance(tasks,list) and len(tasks)==812,'task corpus drift');by={int(x['task_id']):x for x in tasks}
 new_sources=[int(x['task_id']) for x in b2['new_pair_results']];source_tasks=ORIGINAL_SOURCES+new_sources;req(len(source_tasks)==20 and len(set(source_tasks))==20,'20-source bank drift');req(all(t in by for t in source_tasks),'source task missing')
 source_text=[str(by[t]['intent']) for t in source_tasks]
 model_dir=a.run_root/'exact-minilm-l6-v2';model_dir.mkdir(parents=True,exist_ok=True)
 for name in ['config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.txt','sentence_bert_config.json']:
  src=a.snapshot/name
  if src.exists():shutil.copy2(src,model_dir/name)
 target=model_dir/'model.safetensors'
 if target.exists() or target.is_symlink():target.unlink()
 target.symlink_to(a.weights)
 os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
 import torch,torch.nn.functional as F
 from transformers import AutoModel,AutoTokenizer
 tok=AutoTokenizer.from_pretrained(model_dir,local_files_only=True);model=AutoModel.from_pretrained(model_dir,local_files_only=True);model.eval()
 def encode(texts,bs=64):
  out=[]
  with torch.no_grad():
   for i in range(0,len(texts),bs):
    b=tok(texts[i:i+bs],padding=True,truncation=True,max_length=MAX_LEN,return_tensors='pt');h=model(**b).last_hidden_state;m=b['attention_mask'].unsqueeze(-1).expand(h.size()).float();e=(h*m).sum(1)/m.sum(1).clamp(min=1e-9);out.append(F.normalize(e,p=2,dim=1).cpu())
  return torch.cat(out,0)
 se=encode(source_text,20);qe=encode([str(x['intent']) for x in tasks],64);sims=(qe@se.T).numpy()
 # trajectory availability from released AWM parquet
 import pyarrow.parquet as pq
 prow=pq.read_table(a.parquet,columns=['task_id','trajectory_json']).to_pylist();traj={int(x['task_id']):bool(str(x.get('trajectory_json') or '').strip()) for x in prow}
 rows=[]
 for i,t in enumerate(tasks):
  vals=[float(v) for v in sims[i]];order=sorted(range(len(source_tasks)),key=lambda j:vals[j],reverse=True);b,s=order[:2];tid=int(t['task_id']);site=list(t.get('sites') or []);shopping='shopping' in site;held=tid not in source_tasks;hit=vals[b]>=THRESHOLD
  rows.append({'task_id':tid,'sites':site,'intent':str(t['intent']),'intent_template_id':t.get('intent_template_id'),'top1_source_task':source_tasks[b],'top1_similarity':round(vals[b],8),'threshold_hit':hit,'runner_up_source_task':source_tasks[s],'runner_up_similarity':round(vals[s],8),'top1_margin':round(vals[b]-vals[s],8),'is_source_task':not held,'is_shopping':shopping,'trajectory_available':traj.get(tid,False),'evaluator_class':eval_class(t),'retrieval_matched_offline_eligible':bool(shopping and held and hit and traj.get(tid,False) and deterministic_string_match(t))})
 shopping=[x for x in rows if x['is_shopping']];held=[x for x in shopping if not x['is_source_task']];hits=[x for x in held if x['threshold_hit']];eligible=[x for x in hits if x['retrieval_matched_offline_eligible']]
 old_hit_ids={int(x['task_id']) for x in b1['all_rows'] if x.get('threshold_hit') and 'shopping' in (x.get('sites') or []) and not x.get('is_source_task')};old_reserved=sorted(old_hit_ids)
 orig_future=[next(x for x in rows if x['task_id']==t) for t in ORIGINAL_FUTURES]
 payload={'schema_version':'1.0','experiment_id':'D2-PROXY-B3-EXPANDED-BANK-EXACT-RETRIEVAL-EXPOSURE','paper_id':'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE','status':'COMPLETE_ZERO_PROVIDER_CALLS','source_bindings':{'b2_breadth_evidence_sha256':sha(a.b2_evidence),'b1_result_sha256':EXPECTED['b1'],'task_config_sha256':EXPECTED['task_config'],'memory_py_sha256':EXPECTED['memory_py'],'retriever_py_sha256':EXPECTED['retriever_py'],'weights_sha256':EXPECTED['weights']},'retrieval_contract':{'source_tasks':source_tasks,'source_task_count':20,'document_texts':source_text,'model':'all-MiniLM-L6-v2','max_seq_length':MAX_LEN,'pooling':'mean+normalize','top_k':1,'threshold':THRESHOLD},'summary':{'shopping_tasks':len(shopping),'shopping_heldout_tasks':len(held),'shopping_threshold_hits':len(hits),'shopping_hit_rate':round(len(hits)/len(held),8),'offline_eligible_retrieval_matched_tasks':len(eligible),'hit_count_by_selected_source':dict(sorted(Counter(str(x['top1_source_task']) for x in hits).items())),'hit_intent_template_count':len({x['intent_template_id'] for x in hits}),'eligible_intent_template_count':len({x['intent_template_id'] for x in eligible}),'original_B1_reserved_hit_count':len(old_reserved),'original_B1_reserved_hits_still_hit':sum(next(x for x in rows if x['task_id']==tid)['threshold_hit'] for tid in old_reserved),'original_future_hits':sum(x['threshold_hit'] for x in orig_future)},'offline_eligible_support':eligible,'all_threshold_hits':hits,'original_B1_reserved_hit_ids':old_reserved,'original_future_results':orig_future,'all_rows':rows,'scientific_interpretation':'Exact released-retriever exposure after expanding the memory-bank source support from 4 to 20 paired sources. Eligible downstream support is selected only by pre-outcome retrieval, trajectory-availability, and evaluator-executability criteria.','provider_calls':0,'new_rollouts':0,'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False}
 writej(a.output,payload);print(json.dumps({'status':payload['status'],'summary':payload['summary'],'offline_eligible_support':eligible,'original_future_results':orig_future},indent=2))
if __name__=='__main__':main()
