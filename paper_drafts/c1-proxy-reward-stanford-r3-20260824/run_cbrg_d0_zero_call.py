#!/usr/bin/env python3
from __future__ import annotations
import json,re,hashlib,os
from pathlib import Path
from collections import defaultdict

HERE=Path(__file__).resolve().parent
SHOP_MAN=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b4-retrieval-matched-fixed-evidence-20260824/b4-memory-manifest.json')
NEUTRAL_MAN=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b11-outcome-blind-procedural-20260824/b11-neutral-memory-manifest.json')
B3=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/b3-expanded-retrieval-exposure.json')
REDDIT_ROOT=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b12-crossdomain-qualification-20260824')
MODEL=Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/exact-minilm-l6-v2')
CONTRACT=HERE/'cbrg-d0-contract-20260824.json'; OUT=HERE/'cbrg-d0-result-20260824.json'

def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fields(text):
    # Deterministic memory schema units; ignore preambles and item markers.
    out=[]
    for line in text.splitlines():
        m=re.match(r'^##\s+(Title|Description|Content):\s*(.+?)\s*$',line.strip())
        if m and m.group(2): out.append({'field':m.group(1).lower(),'text':m.group(2).strip()})
    if not out:
        # Reddit/provider text uses the same schema; this fallback is only for compact single-line artifacts.
        for m in re.finditer(r'(?:Title|Description|Content):\s*([^\n#]+)',text): out.append({'field':'unknown','text':m.group(1).strip()})
    if not out: raise RuntimeError('no schema fields parsed')
    return out

def main():
    c=load(CONTRACT); assert c['status']=='FROZEN_ZERO_CALL_DIAGNOSTIC_ONLY' and c['provider_calls']==0
    sm=load(SHOP_MAN); nm=load(NEUTRAL_MAN); b3=load(B3); rq=load(REDDIT_ROOT/'b12-reddit-qualification-result.json')
    pairs={}; neutral={}
    for o in sm['objects']:
        sid=int(o['source_task']);pairs.setdefault(('shopping',sid),{})[o['condition']]=Path(o['raw_path']).read_text()
    for o in nm['objects']: neutral[int(o['source_task'])]=Path(o['raw_path']).read_text()
    for sid in [404,405,595,610]:
        for cond in ['success','failure']:
            p=REDDIT_ROOT/f'private/execution-r1/writer/provider-responses/reddit-r1-writer-{sid}-{cond}.json'
            pairs.setdefault(('reddit',sid),{})[cond]=load(p)['text']
    assert len([k for k,v in pairs.items() if set(v)=={'success','failure'}])==24
    targets=[]
    for x in b3['offline_eligible_support']:
        targets.append({'domain':'shopping','task':int(x['task_id']),'source':int(x['top1_source_task']),'intent':x['intent']})
    for x in rq['eligible_future_support']:
        targets.append({'domain':'reddit','task':int(x['task_id']),'source':int(x['top1_source_task']),'intent':x['intent']})
    assert sum(x['domain']=='shopping' for x in targets)==36 and sum(x['domain']=='reddit' for x in targets)==8
    atoms=[]
    for key,v in pairs.items():
        for cond,t in v.items():
            for u in fields(t): atoms.append((key,cond,u))
    neutral_atoms={sid:fields(t) for sid,t in neutral.items()}
    texts=[u['text'] for _,_,u in atoms]+[u['text'] for us in neutral_atoms.values() for u in us]+[x['intent'] for x in targets]
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
    import torch, torch.nn.functional as F
    from transformers import AutoTokenizer,AutoModel
    tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True);model=AutoModel.from_pretrained(MODEL,local_files_only=True);model.eval()
    def enc(ts):
        out=[]
        with torch.no_grad():
            for i in range(0,len(ts),64):
                b=tok(ts[i:i+64],padding=True,truncation=True,max_length=256,return_tensors='pt');h=model(**b).last_hidden_state;m=b['attention_mask'].unsqueeze(-1).expand(h.size()).float();e=(h*m).sum(1)/m.sum(1).clamp(min=1e-9);out.append(F.normalize(e,p=2,dim=1).cpu())
        return torch.cat(out)
    E=enc(texts); idx=0; emb={}
    for key,cond,u in atoms: emb[(key,cond,u['text'])]=E[idx];idx+=1
    nemb={}
    for sid,us in neutral_atoms.items():
        for u in us:nemb[(sid,u['text'])]=E[idx];idx+=1
    temb={}
    for x in targets:temb[(x['domain'],x['task'])]=E[idx];idx+=1
    rows=[]; residual_atoms={}
    for key,v in sorted(pairs.items()):
        units={cond:fields(t) for cond,t in v.items()}; vals=[]; by={}
        for cond,opp in [('success','failure'),('failure','success')]:
            oppE=torch.stack([emb[(key,opp,u['text'])] for u in units[opp]])
            br=[]
            for u in units[cond]:
                e=emb[(key,cond,u['text'])]; mx=float((oppE@e).max()); w=max(0.0,min(2.0,1-mx)); br.append({'field':u['field'],'text_sha256':hashlib.sha256(u['text'].encode()).hexdigest(),'opposite_explainability':mx,'residual_weight':w,'embedding':e})
                vals.append(mx)
            by[cond]=br
        neutral_align=None
        if key[0]=='shopping' and key[1] in neutral_atoms:
            nE=torch.stack([nemb[(key[1],u['text'])] for u in neutral_atoms[key[1]]])
            sfE=torch.stack([emb[(key,c,u['text'])] for c in ['success','failure'] for u in units[c]])
            neutral_align=sum(float((sfE@e).max()) for e in nE)/len(nE)
        rows.append({'domain':key[0],'source':key[1],'success_units':len(units['success']),'failure_units':len(units['failure']),'common_core_strength':sum(vals)/len(vals),'residual_energy':sum(1-x for x in vals)/len(vals),'neutral_to_sf_max_alignment':neutral_align})
        residual_atoms[key]=by
    app=[]
    for t in targets:
        key=(t['domain'],t['source']); q=temb[(t['domain'],t['task'])]
        r={'domain':t['domain'],'task':t['task'],'source':t['source']}
        for cond in ['success','failure']:
            scores=[a['residual_weight']*max(0.0,float(a['embedding']@q)) for a in residual_atoms[key][cond]]
            r[cond+'_residual_applicability']=max(scores) if scores else 0.0
        r['branch_applicability_gap']=abs(r['success_residual_applicability']-r['failure_residual_applicability']);app.append(r)
    import statistics as st
    def summary(xs):
        xs=sorted(xs);n=len(xs)
        return {'n':n,'mean':sum(xs)/n,'median':st.median(xs),'min':xs[0],'max':xs[-1],'stdev':st.pstdev(xs),'q25':xs[n//4],'q75':xs[(3*n)//4]}
    per_source=defaultdict(list)
    for x in app:per_source[(x['domain'],x['source'])].append(max(x['success_residual_applicability'],x['failure_residual_applicability']))
    variable_sources=sum(len(v)>=2 and max(v)>min(v) for v in per_source.values())
    payload={'schema_version':'1.0','experiment_id':c['experiment_id'],'status':'D0_ZERO_CALL_CONTINUOUS_DIAGNOSTIC_COMPLETE','contract_sha256':sha(CONTRACT),'provider_calls':0,'gpu_runs':0,
      'support':{'paired_sources':len(rows),'shopping_pairs':20,'reddit_pairs':4,'targets':len(app),'shopping_targets':36,'reddit_targets':8},
      'summary':{'common_core_strength':summary([x['common_core_strength'] for x in rows]),'residual_energy':summary([x['residual_energy'] for x in rows]),'shopping_neutral_alignment':summary([x['neutral_to_sf_max_alignment'] for x in rows if x['neutral_to_sf_max_alignment'] is not None]),'target_max_residual_applicability':summary([max(x['success_residual_applicability'],x['failure_residual_applicability']) for x in app]),'target_branch_applicability_gap':summary([x['branch_applicability_gap'] for x in app]),'sources_with_multiple_targets_and_nonzero_applicability_range':variable_sources,'sources_with_multiple_targets':sum(len(v)>=2 for v in per_source.values())},
      'pair_results':rows,'target_results':app,'interpretation_boundary':'Threshold-free representation-feasibility diagnostic only. No terminal outcomes enter any metric; no method effect or novelty claim is authorized.','scientific_authority':False,'experiment_authority':False,'provider_call_authority':False,'claim_expansion_authority':False}
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print(json.dumps(payload['summary'],indent=2))
if __name__=='__main__':main()
