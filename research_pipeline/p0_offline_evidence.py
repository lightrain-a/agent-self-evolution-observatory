from __future__ import annotations
import json, math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

def rel(root:Path,path:Path)->str:
    try:return str(path.relative_to(root))
    except ValueError:return path.name

def j(path: Path)->dict[str,Any]:
    try:return json.loads(path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError):return {}

def jl(path: Path)->list[dict[str,Any]]:
    try:return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
    except (OSError,json.JSONDecodeError):return []

def alfworld(root:Path)->dict[str,Any]:
    p=root/'pre-experiment-qualification-qwen25-react-family-ood134.json'; d=j(p); g=d.get('gate') or {}
    return {'source':rel(root,p),'passed':bool(g.get('passed')),'successes':int(d.get('successes') or 0),'total':int(d.get('num_envs') or 0),'success_rate':float(d.get('success_rate') or 0),'task_types_with_success':int(d.get('task_types_with_success') or 0)}

def a1(root:Path)->dict[str,Any]:
    p=root/'pre-experiment-a1-screening-review-20260810.json'; d=j(p); e=d.get('directional_effect') or {}; f=d.get('probe_fidelity') or {}
    return {'source':rel(root,p),'harmful_candidates':int(e.get('harmful_candidate_count') or 0),'harmful_reduction':float(e.get('harmful_update_reduction') or 0),'target_gain_loss':float(e.get('target_gain_loss') or 0),'panel_auc':float(f.get('aggregate_panel_leave_one_candidate_out_auc') or 0),'best_probe_auc':float(f.get('best_single_probe_action_auc') or 0),'min_auc':float(f.get('minimum_fidelity_auc') or .65),'fidelity_pass':bool(f.get('fidelity_pass'))}

def a2(root:Path)->dict[str,Any]:
    p=root/'qualification'/'a2-updater-support-v1'/'fixed-sequences.jsonl'; rows=jl(p); best=[]; harm=0; pos=0
    for s in rows:
        rs=s.get('rounds') or []
        if not rs:continue
        score=[(float(r.get('success') or 0),-float(r.get('regression') or 0),-float(r.get('cumulative_calls') or 0)) for r in rs]; bi=max(range(len(rs)),key=lambda i:score[i]); best.append(bi+1); b=rs[bi]
        harm+=any(float(r.get('success') or 0)<float(b.get('success') or 0) or float(r.get('regression') or 0)>float(b.get('regression') or 0) for r in rs[bi+1:])
        pos+=any(float(r.get('marginal_gain') or 0)>0 for r in rs)
    c=Counter(best); n=len(best); H=-sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0
    return {'source':rel(root,p),'sequences':n,'optimal_round_counts':dict(c),'entropy_bits':H,'non_early':sum(x>1 for x in best),'harm_after_best':harm,'positive_gain_sequences':pos}

def memory(root:Path)->dict[str,Any]:
    p=root/'runs'/'p0-mem-xfer-support-enriched-qwen-v1'/'support-qualification'/'analysis.json'; d=j(p)
    return {'source':rel(root,p),'decision':d.get('decision'),'units':int(d.get('complete_units') or 0),'nonzero':int(d.get('controlled_nonzero') or 0),'harm':int(d.get('controlled_harm') or 0),'benefit':int(d.get('controlled_benefit') or 0),'families':len(d.get('target_families_with_nonzero') or [])}

def a3_panel(root:Path)->dict[str,Any]:
    p=root/'pre-gpu'/'a3-mastered-probe-panel-v1.json'; d=j(p)
    return {'source':rel(root,p),'passed':bool(d.get('pass')),'panel_size':int(d.get('panel_size') or 0),'mastered_candidates':int(d.get('mastered_candidates') or 0),'family_coverage':int(d.get('task_family_coverage') or 0),'next_gate':d.get('next_gate')}

def a67_dataset(root:Path)->dict[str,Any]:
    p=root/'qualification'/'a2-updater-support-v1'/'fixed-sequences.jsonl'; rows=jl(p)
    return {'source':rel(root,p),'sequences':len(rows),'prefix_states':sum(len(r.get('rounds') or []) for r in rows),'a6_nonprefix_interventions':0,'a6_minimal_fault_oracle':False,'a7_same_state_four_action_rows':0,'ready_a6':False,'ready_a7':False}

def e1(root:Path)->dict[str,Any]:
    p=root/'runs'/'round1-20260810'/'e1-r5'/'evaluations.jsonl'; rows=[r for r in jl(p) if r.get('stage')=='workflow-edit-matrix']; a=defaultdict(list)
    for r in rows:
        c=str(r.get('context_id') or '')
        if '|' in c:
            w,e=c.split('|',1); a[(w,e)].append(float(r.get('reward') or 0))
    m={k:sum(v)/len(v) for k,v in a.items() if v}; ws=sorted({w for w,_ in m}); edits=sorted({e for _,e in m if e!='base'}); eff=uniq=0; split=Counter(); seff=Counter()
    for w in ws:
        if (w,'base') not in m:continue
        s='confirm' if 'wf-confirm' in w else 'calibration' if 'wf-calibration' in w else 'discovery'; split[s]+=1; b=m[(w,'base')]; ds=[m.get((w,e),b)-b for e in edits]
        if max(ds,default=0)>0:eff+=1;seff[s]+=1
        if len({round(x,8) for x in ds})>1:uniq+=1
    total=sum(split.values())
    return {'source':rel(root,p),'workflows':total,'edits':len(edits),'effective_workflows':eff,'uniquely_ranked_workflows':uniq,'effective_fraction':eff/total if total else 0,'split_total':dict(split),'split_effective':dict(seff),'identifiable':eff>=6 and uniq>=6}
