from __future__ import annotations
import hashlib, json, os, re
from pathlib import Path
from typing import Any
from .p0_alfworld_adapter import HFAdmissiblePolicy

def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(tmp,path)

def append_jsonl(path: Path, payload: dict[str,Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a',encoding='utf-8') as h:
        h.write(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n'); h.flush()

def trace_summary(trace: dict[str,Any], limit:int=10)->str:
    all_actions=list(trace.get('actions') or []); actions=all_actions[-limit:]
    observations=list(trace.get('observations') or []); start=max(0,len(all_actions)-len(actions))
    rows=[f"goal={trace.get('task_goal') or ''}",f"family={trace.get('task_family') or ''}"]
    for off,action in enumerate(actions):
        idx=start+off; obs=observations[idx+1] if idx+1<len(observations) else ''
        rows.append(f"{off+1}. {action} -> {str(obs)[:160]}")
    return '\n'.join(rows)

def replan_patch(trace:dict[str,Any])->str:
    goal=str(trace.get('task_goal') or 'the task goal')
    return "If a previous attempt has not completed the task, explicitly identify the earliest unmet goal predicate for '"+goal[:160]+"' and prioritize an admissible action that advances it before repeating prior search or navigation."

def ordered_pair(first:str,second:str)->str:
    return first+'\nAfter applying that rule, also apply this later rule: '+second

def hidden_assignment(candidate_id:str,hidden:list[str],count:int,seed:int)->list[str]:
    return sorted(hidden,key=lambda x:hashlib.sha256(f'{seed}|{candidate_id}|{x}'.encode()).hexdigest())[:count]

def check_gpu_free(min_free_gib:float=20.0)->dict[str,float]:
    import torch
    if not torch.cuda.is_available(): raise RuntimeError('CUDA is unavailable')
    free,total=torch.cuda.mem_get_info(); info={'free_gib':free/2**30,'total_gib':total/2**30}
    if info['free_gib']<min_free_gib: raise RuntimeError(f"GPU free memory {info['free_gib']:.2f} GiB < required {min_free_gib:.2f} GiB")
    return info

def generate_label(policy:HFAdmissiblePolicy,system:str,user:str,seed:int)->dict[str,Any]:
    torch=policy.torch; torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    messages=[{'role':'system','content':system},{'role':'user','content':user}]
    prompt=policy.tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
    inputs=policy.tokenizer(prompt,return_tensors='pt').to(policy.device)
    with torch.no_grad():
        generated=policy.model.generate(**inputs,max_new_tokens=48,do_sample=True,temperature=0.65,top_p=0.9,pad_token_id=policy.tokenizer.eos_token_id)
    suffix=generated[0,inputs['input_ids'].shape[1]:]; policy._record_usage(inputs,suffix)
    raw=policy.tokenizer.decode(suffix,skip_special_tokens=True).strip()
    decision='ACCEPT' if re.search(r'\bACCEPT\b',raw,re.I) and not re.search(r'\bQUARANTINE\b',raw,re.I) else 'QUARANTINE'
    m=re.search(r'(?:confidence|conf)\D{0,8}(0(?:\.\d+)?|1(?:\.0+)?)',raw,re.I)
    confidence=float(m.group(1)) if m else 0.5
    return {'decision':decision,'confidence':max(0.0,min(1.0,confidence)),'raw':raw[:500]}

def self_label_lineages(policy:HFAdmissiblePolicy,candidate:dict[str,Any],source_trace:dict[str,Any],source_after:dict[str,Any],seed:int)->list[dict[str,Any]]:
    lenses=['scope transfer','regression risk','goal fidelity','tool/state consistency','over-generalization']
    base=(f"Failure trace:\n{trace_summary(source_trace)}\n\nCandidate correction:\n{candidate['patch']}\n\n"
          f"Current-task intervention: before_success={source_trace.get('success',0)}, after_success={source_after.get('success',0)}, "
          f"before_steps={source_trace.get('steps',0)}, after_steps={source_after.get('steps',0)}. Hidden future outcomes are unavailable.")
    rows=[]
    for root in range(2):
        parent=None
        for round_idx,lens in enumerate(lenses):
            lineage_id=f"{candidate['candidate_id']}:root{root}"
            root_note='transfer-first independent root' if root==0 else 'safety-first independent root'
            parent_note='' if parent is None else f"Parent self-label: {parent['decision']} confidence={parent['confidence']:.3f}; treat it as evidence, not truth."
            out=generate_label(policy,'Decide whether one correction should be persistently committed. Output ACCEPT or QUARANTINE plus confidence in [0,1].',f"{base}\nReview lens={lens}; style={root_note}.\n{parent_note}\nDecision:",seed+root*1000+round_idx)
            row={'label_id':f'{lineage_id}:r{round_idx}','lineage_id':lineage_id,'candidate_id':candidate['candidate_id'],'root':root,'round':round_idx,'parent_label_id':parent.get('label_id') if parent else None,'lens':lens,**out}
            rows.append(row); parent=row
    return rows
