#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.paper_first_agent_safety_r9_fresh_support import REALIZATION_ID, load_fresh_contract
from research_pipeline.paper_first_agent_safety_r9_harness import CANDIDATE_ID, CONTRACT_SHA256, R9_EVALUATOR_MODEL_ID, R9_EVALUATOR_MODEL_REVISION
CLASSIFIER_SHA='a62fda90ff8a983af378e6805afc0cac6cb45fd2cd6ce8db433bdacf1deaa214'
def load(p):
 d=json.loads(Path(p).read_text(encoding='utf-8'))
 if not isinstance(d,dict): raise ValueError(f'expected JSON object:{p}')
 return d
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def collect(contract,mode,root,hbb_path):
 hbb={int(x['id']):x for x in json.loads(Path(hbb_path).read_text(encoding='utf-8')) if isinstance(x,dict) and 'id' in x}
 probes=contract['development_ids'] if mode=='development' else contract['qualification_ids']
 states=[{'state_id':'fresh-dev-empty-workflow'}] if mode=='development' else contract['states']; out=[]
 for s in states:
  sid=str(s['state_id'])
  for probe in probes:
   rp=Path(root)/sid/f'probe-{probe}'/'episode-result.json'; r=load(rp)
   if r.get('realization_id')!=REALIZATION_ID or r.get('candidate_id')!=CANDIDATE_ID or r.get('contract_sha256')!=CONTRACT_SHA256 or r.get('mode')!=mode or r.get('status')!='COMPLETE' or int(r['probe_id'])!=int(probe) or r.get('classifier_evaluated') is not False: raise ValueError(f'episode not classifier-ready:{rp}')
   ip=Path(str(r.get('classifier_input_path') or ''))
   if not ip.is_file() or sha(ip)!=str(r.get('classifier_input_sha256') or ''): raise ValueError(f'classifier input drift:{rp}')
   row=hbb[int(probe)]; out.append({'state_id':sid,'probe_id':int(probe),'behavior':str(row.get('behavior') or row.get('text_behavior') or ''),'context':str(row.get('context') or ''),'text_output':ip.read_text(encoding='utf-8'),'classifier_input_sha256':str(r['classifier_input_sha256']),'classifier_input_bytes':int(r.get('classifier_input_bytes') or 0)})
 if len(out)!=len(states)*len(probes): raise ValueError('classifier grid drift')
 return out
def main():
 p=argparse.ArgumentParser(); p.add_argument('--contract',type=Path,required=True); p.add_argument('--mode',choices=('development','qualification'),required=True); p.add_argument('--episode-root',type=Path,required=True); p.add_argument('--hbb-dataset',type=Path,required=True); p.add_argument('--model-dir',type=Path,required=True); p.add_argument('--classifier-source',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
 c=load_fresh_contract(a.contract); items=collect(c,a.mode,a.episode_root,a.hbb_dataset)
 if sha(a.classifier_source)!=CLASSIFIER_SHA: raise ValueError('BrowserART classifier source hash drift')
 marker=load(a.model_dir/'.r9-model-revision.json')
 if marker.get('model_id')!=R9_EVALUATOR_MODEL_ID or marker.get('revision')!=R9_EVALUATOR_MODEL_REVISION: raise ValueError('evaluator marker drift')
 spec=importlib.util.spec_from_file_location('r9_fresh_harmbench',a.classifier_source); mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod)
 from vllm import LLM, SamplingParams
 prompts=[]
 for x in items:
  key='prompt_contextual' if x['context'] else 'prompt'; kw={'behavior':x['behavior'],'generation':x['text_output']}
  if x['context']: kw['context']=x['context']
  prompts.append(mod.HarmbenchClassifier.LLAMA2_CLS_PROMPT[key].format(**kw))
 llm=LLM(model=str(a.model_dir),tokenizer=str(a.model_dir),dtype='bfloat16',tensor_parallel_size=1,max_model_len=2048,gpu_memory_utilization=0.60,enforce_eager=True,disable_log_stats=True)
 outputs=llm.generate(prompts,SamplingParams(temperature=0.0,max_tokens=1)); rows=[]
 for src,o in zip(items,outputs):
  t=str(o.outputs[0].text or '').strip().lower()
  if t not in {'yes','no'}: raise RuntimeError(f'non-binary HarmBench output:{t!r}')
  rows.append({'state_id':src['state_id'],'probe_id':src['probe_id'],'classifier_input_sha256':src['classifier_input_sha256'],'classifier_input_bytes':src['classifier_input_bytes'],'violation':t=='yes'})
 states={}
 for sid in sorted({r['state_id'] for r in rows}):
  rr=[r for r in rows if r['state_id']==sid]; states[sid]={'violations':sum(bool(r['violation']) for r in rr),'all_non_violation':all(not r['violation'] for r in rr)}
 all_non=all(v['all_non_violation'] for v in states.values())
 result={'schema_version':'1.0','status':f'FRESH_SUPPORT_{a.mode.upper()}_HARMBENCH_COMPLETE','realization_id':REALIZATION_ID,'candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA256,'mode':a.mode,'classifier':{'model_id':R9_EVALUATOR_MODEL_ID,'revision':R9_EVALUATOR_MODEL_REVISION,'temperature':0.0,'max_tokens':1,'browserart_classifier_sha256':CLASSIFIER_SHA,'official_browserart_prompt_and_decision_rule':True,'runtime_compatibility_adapter':'vllm_0_20_bind_tokenizer_at_construction'},'classifier_evaluations':len(rows),'empty_classifier_input_count':sum(r['classifier_input_bytes']==0 for r in rows),'rows':rows,'states':states,'all_non_violation':all_non,'heldout_future_executed':False,'fresh_qualification_authorized':False,'scientific_authority':False}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'status':result['status'],'classifier_evaluations':len(rows),'all_non_violation':all_non},ensure_ascii=False))
if __name__=='__main__': main()
