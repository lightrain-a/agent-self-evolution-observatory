#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil
from collections import Counter
from pathlib import Path

EXPECTED_PROGRAM_STATUS = "FROZEN_BEFORE_NEW_EXPERIMENTS"
SOURCE_TASKS = [21, 22, 23, 25]
FUTURES = [164, 385, 387, 388]
TASK_CONFIG_SHA = "d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6"
MEMORY_PY_SHA = "d4f499fe3321571db7f631132b939cf5b9ab121f24d81fa80637df221aad6386"
RETRIEVER_PY_SHA = "bab30513553a0133ea463f45a0716627bcf099ab34a1ce969581442d42278f13"
CONFIG_SHA = "953f9c0d463486b10a6871cc2fd59f223b2c70184f49815e7efbcab5d8908b41"
TOKENIZER_SHA = "be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037"
POOL_SHA = "4be450dde3b0273bb9787637cfbd28fe04a7ba6ab9d36ac48e92b11e350ffc23"
MODULES_SHA = "84e40c8e006c9b1d6c122e02cba9b02458120b5fb0c87b746c41e0207cf642cf"
WEIGHTS_SHA = "53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db"
MAX_LEN = 256
THRESHOLD = 0.3


def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p: Path): return json.loads(p.read_text(encoding="utf-8"))
def require(x: bool, msg: str):
    if not x: raise RuntimeError(msg)
def writej(p: Path, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); os.replace(t,p)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--program',required=True,type=Path)
    ap.add_argument('--task-config',required=True,type=Path)
    ap.add_argument('--memory-py',required=True,type=Path)
    ap.add_argument('--retriever-py',required=True,type=Path)
    ap.add_argument('--snapshot',required=True,type=Path)
    ap.add_argument('--weights',required=True,type=Path)
    ap.add_argument('--run-root',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args()
    prog=load(a.program); require(prog.get('status')==EXPECTED_PROGRAM_STATUS,'program not frozen')
    b1=prog['experiments']['B1_exact_retrieval_exposure']; require(b1['provider_call_ceiling']==0,'B1 provider budget drift')
    require(b1['top_k']==1 and abs(float(b1['threshold'])-THRESHOLD)<1e-12 and b1['max_seq_length']==MAX_LEN,'retrieval contract drift')
    for p,h,label in [(a.task_config,TASK_CONFIG_SHA,'task config'),(a.memory_py,MEMORY_PY_SHA,'memory.py'),(a.retriever_py,RETRIEVER_PY_SHA,'retriever.py'),(a.snapshot/'config.json',CONFIG_SHA,'model config'),(a.snapshot/'tokenizer.json',TOKENIZER_SHA,'tokenizer'),(a.snapshot/'1_Pooling/config.json',POOL_SHA,'pool config'),(a.snapshot/'modules.json',MODULES_SHA,'modules'),(a.weights,WEIGHTS_SHA,'weights')]:
        require(p.is_file() and sha(p)==h,f'{label} SHA drift')
    modules=load(a.snapshot/'modules.json'); pool=load(a.snapshot/'1_Pooling/config.json'); sb=load(a.snapshot/'sentence_bert_config.json')
    require([x['type'].split('.')[-1] for x in modules]==['Transformer','Pooling','Normalize'],'SentenceTransformer module drift')
    require(pool['pooling_mode_mean_tokens'] is True and not pool['pooling_mode_cls_token'] and not pool['pooling_mode_max_tokens'],'pooling drift')
    require(int(sb['max_seq_length'])==MAX_LEN,'max sequence drift')
    mt=a.memory_py.read_text(encoding='utf-8'); rt=a.retriever_py.read_text(encoding='utf-8')
    require('task_pools = [v["task_description"] for v in self.reasoningbank_memory.values()]' in mt,'retrieval key drift')
    require('new_embeddings = self.embedder.encode(new_docs_to_add, convert_to_numpy=True)' in rt,'embedder source drift')
    require('if sim >= threshold:' in rt,'threshold source drift')

    # Build a run-local model directory from the exact cached snapshot plus exact safetensors blob.
    model_dir=a.run_root/'exact-minilm-l6-v2'; model_dir.mkdir(parents=True,exist_ok=True)
    for name in ['config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.txt','sentence_bert_config.json']:
        src=a.snapshot/name
        if src.exists(): shutil.copy2(src,model_dir/name)
    target=model_dir/'model.safetensors'
    if target.exists() or target.is_symlink(): target.unlink()
    target.symlink_to(a.weights)
    os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'; os.environ['TOKENIZERS_PARALLELISM']='false'
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer
    tok=AutoTokenizer.from_pretrained(model_dir,local_files_only=True)
    model=AutoModel.from_pretrained(model_dir,local_files_only=True); model.eval()

    tasks=load(a.task_config); require(isinstance(tasks,list) and len(tasks)==812,'task corpus drift')
    by={int(r['task_id']):r for r in tasks}; require(all(t in by for t in SOURCE_TASKS+FUTURES),'frozen task missing')
    src_text=[str(by[t]['intent']) for t in SOURCE_TASKS]
    all_text=[str(r['intent']) for r in tasks]
    def encode(texts:list[str],bs:int=64):
        chunks=[]
        with torch.no_grad():
            for i in range(0,len(texts),bs):
                batch=tok(texts[i:i+bs],padding=True,truncation=True,max_length=MAX_LEN,return_tensors='pt')
                out=model(**batch).last_hidden_state
                mask=batch['attention_mask'].unsqueeze(-1).expand(out.size()).float()
                emb=(out*mask).sum(1)/mask.sum(1).clamp(min=1e-9)
                chunks.append(F.normalize(emb,p=2,dim=1).cpu())
        return torch.cat(chunks,0)
    se=encode(src_text,4); qe=encode(all_text,64); sims=(qe@se.T).numpy()
    rows=[]
    for idx,r in enumerate(tasks):
        vals=[float(x) for x in sims[idx]]; order=sorted(range(4),key=lambda j:vals[j],reverse=True)
        best,second=order[0],order[1]; sim=vals[best]; second_sim=vals[second]
        rows.append({'task_id':int(r['task_id']),'sites':list(r.get('sites') or []),'intent':str(r['intent']),'intent_template_id':r.get('intent_template_id'),'top1_source_task':SOURCE_TASKS[best],'top1_similarity':round(sim,8),'threshold_hit':bool(sim>=THRESHOLD),'runner_up_source_task':SOURCE_TASKS[second],'runner_up_similarity':round(second_sim,8),'top1_margin':round(sim-second_sim,8),'is_source_task':int(r['task_id']) in SOURCE_TASKS,'is_frozen_future':int(r['task_id']) in FUTURES})
    shopping=[x for x in rows if 'shopping' in x['sites']]
    held=[x for x in shopping if not x['is_source_task']]
    hits=[x for x in held if x['threshold_hit']]
    per=Counter(str(x['top1_source_task']) for x in hits)
    future=[next(x for x in rows if x['task_id']==f) for f in FUTURES]
    top_examples={str(s):sorted([x for x in held if x['top1_source_task']==s],key=lambda x:x['top1_similarity'],reverse=True)[:10] for s in SOURCE_TASKS}
    payload={'schema_version':'1.0','experiment_id':'D2-PROXY-B1-EXACT-RETRIEVAL-EXPOSURE','paper_id':'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE','status':'COMPLETE_ZERO_PROVIDER_CALLS','contract_sha256':sha(a.program),'source_bindings':{'task_config_sha256':TASK_CONFIG_SHA,'memory_py_sha256':MEMORY_PY_SHA,'retriever_py_sha256':RETRIEVER_PY_SHA,'model_config_sha256':CONFIG_SHA,'tokenizer_sha256':TOKENIZER_SHA,'pooling_sha256':POOL_SHA,'modules_sha256':MODULES_SHA,'weights_sha256':WEIGHTS_SHA},'retrieval_contract':{'source_tasks':SOURCE_TASKS,'document_texts':src_text,'model':'all-MiniLM-L6-v2','max_seq_length':MAX_LEN,'pooling':'mean+normalize','top_k':1,'threshold':THRESHOLD},'summary':{'all_webarena_tasks':len(rows),'shopping_tasks':len(shopping),'shopping_heldout_tasks':len(held),'shopping_threshold_hits':len(hits),'shopping_hit_rate':round(len(hits)/len(held),8) if held else None,'hit_count_by_selected_source':dict(sorted(per.items())),'frozen_future_hits':sum(x['threshold_hit'] for x in future),'frozen_future_count':len(future)},'frozen_future_results':future,'top10_heldout_by_selected_source':top_examples,'all_rows':rows,'scientific_interpretation':'Exact source-faithful retrieval exposure only. This does not execute the native ReasoningBank prompt wrapper or browser environment and therefore does not by itself establish source-faithful terminal transport.','provider_calls':0,'new_rollouts':0,'scientific_authority':False,'experiment_authority':True,'claim_expansion_authority':False}
    writej(a.output,payload)
    print(json.dumps({'status':payload['status'],'summary':payload['summary'],'frozen_future_results':future},ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
