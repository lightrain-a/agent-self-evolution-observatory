from __future__ import annotations

import itertools
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

TYPES=("exception","observation","policy","recovery","safety","tool")
WORLDS=(
    {"base":(("safety","policy"),),"conditional":(("exception","policy","safety"),("observation","tool","recovery"))},
    {"base":(("policy","observation"),),"conditional":(("recovery","observation","policy"),("safety","exception","tool"))},
    {"base":(("recovery","exception"),),"conditional":(("tool","exception","recovery"),("policy","observation","safety"))},
    {"base":(("tool","safety"),),"conditional":(("observation","safety","tool"),("exception","policy","recovery"))},
)
DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-b10-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-b10-cpu.js"


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def _before(order:tuple[str,...],a:str,b:str)->bool:return order.index(a)<order.index(b)

def _constraints(world:dict[str,Any],combo:tuple[str,...])->list[tuple[str,str]]:
    edges=[]
    conditional_pairs={(a,b) for c,a,b in world["conditional"] if c in combo}
    for a,b in world["base"]:
        if a in combo and b in combo and (a,b) not in conditional_pairs and (b,a) not in conditional_pairs: edges.append((a,b))
    for c,a,b in world["conditional"]:
        if c in combo and a in combo and b in combo: edges.append((a,b))
    return edges

def _legal(world:dict[str,Any],combo:tuple[str,...],order:tuple[str,...])->bool:
    return all(_before(order,a,b) for a,b in _constraints(world,combo))

def _combos(world:dict[str,Any])->list[tuple[str,...]]:
    out=[]
    for n in (3,4,5):
        for c in itertools.combinations(TYPES,n):
            if any(_legal(world,c,p) for p in itertools.permutations(c)): out.append(c)
    return out

def _split(world_index:int,world:dict[str,Any])->tuple[list[tuple[str,...]],list[tuple[str,...]]]:
    combos=_combos(world)
    # Held-out cells must actually exercise the ordering mechanism. Exclude
    # unconstrained combinations and force the unique multi-constraint hard case.
    candidates=[c for c in combos if len(c)>=4 and len(_constraints(world,c))>=1]
    candidates=sorted(candidates,key=lambda c:(-len(_constraints(world,c)),sum((i+1)*(TYPES.index(x)+3) for i,x in enumerate(c))+17*world_index))
    hard=[c for c in candidates if len(_constraints(world,c))>=2]
    rest=[c for c in candidates if c not in hard]
    offset=world_index % max(1,len(rest))
    rotated=rest[offset:]+rest[:offset]
    test=(hard[:1]+rotated)[:8]
    if len(test)!=8 or any(len(_constraints(world,c))<1 for c in test):
        raise RuntimeError("B10 held-out split must contain 8 binding-constraint combinations per world")
    return [c for c in combos if c not in test],test


def _training_records(world:dict[str,Any],train:list[tuple[str,...]])->list[tuple[tuple[str,...],tuple[str,...],int]]:
    rows=[]
    for combo in train:
        for order in itertools.permutations(combo): rows.append((combo,order,int(_legal(world,combo,order))))
    return rows

def _symbolic_learn(rows:list[tuple[tuple[str,...],tuple[str,...],int]])->dict[tuple[str,str,str|None],int]:
    # MDL-style clause selection. For each typed pair, derive whether each training
    # type-combination constrains its orientation (+1/-1) or leaves it free (0), then
    # choose the smallest base+context program that reproduces those targets.
    legal=defaultdict(list)
    for combo,order,y in rows:
        if y: legal[combo].append(order)
    rules={}
    for a,b in itertools.combinations(TYPES,2):
        contexts=[x for x in TYPES if x not in {a,b}]
        targets=[]
        for combo,orders in legal.items():
            if a not in combo or b not in combo: continue
            vals={1 if _before(o,a,b) else -1 for o in orders}
            targets.append((combo,next(iter(vals)) if len(vals)==1 else 0))
        if not targets: continue
        best=None
        # A real MDL search over all 3^(1+4)=243 tiny programs.
        for base in (-1,0,1):
            for ctx_values in itertools.product((-1,0,1),repeat=len(contexts)):
                model={c:v for c,v in zip(contexts,ctx_values) if v}
                errors=0
                for combo,target in targets:
                    active={model[c] for c in contexts if c in combo and c in model}
                    pred=next(iter(active)) if len(active)==1 else (0 if len(active)>1 else base)
                    errors+=pred!=target
                complexity=int(base!=0)+len(model)
                score=(errors,complexity,tuple(ctx_values),base)
                if best is None or score<best[0]: best=(score,base,model)
        _,base,model=best
        if base: rules[(a,b,None)]=base
        for c,v in model.items(): rules[(a,b,c)]=v
    return rules

def _factor_features(combo:tuple[str,...],order:tuple[str,...])->dict[tuple[str,str,str|None],float]:
    out={}
    for a,b in itertools.combinations(TYPES,2):
        if a not in combo or b not in combo: continue
        sign=1.0 if _before(order,a,b) else -1.0
        out[(a,b,None)]=sign
        for ctx in combo:
            if ctx not in {a,b}: out[(a,b,ctx)]=sign
    return out

def _sigmoid(z:float)->float:
    if z>=0:
        e=math.exp(-min(z,60)); return 1/(1+e)
    e=math.exp(max(z,-60)); return e/(1+e)

def _factor_learn(rows:list[tuple[tuple[str,...],tuple[str,...],int]])->dict[str,Any]:
    # Strong capacity-matched typed n-ary factor baseline: balanced logistic energy
    # over exactly the same typed pair/context variables available to the symbolic
    # clause learner. Pure-Python SGD avoids adding an ML-library dependency.
    weights=defaultdict(float); bias=0.0
    pos=sum(y for _,_,y in rows); neg=len(rows)-pos
    pw=len(rows)/(2*pos) if pos else 1.0; nw=len(rows)/(2*neg) if neg else 1.0
    lr=0.06; l2=1e-4
    cached=[(_factor_features(c,o),y) for c,o,y in rows]
    for epoch in range(45):
        step=lr/(1+0.04*epoch)
        for feats,y in cached:
            z=bias+sum(weights[k]*v for k,v in feats.items()); p=_sigmoid(z); sw=pw if y else nw; err=(p-y)*sw
            bias-=step*err*0.15
            for k,v in feats.items(): weights[k]-=step*(err*v+l2*weights[k])
    correct=0
    for feats,y in cached:
        pred=int(bias+sum(weights[k]*v for k,v in feats.items())>=0); correct+=pred==y
    return {"weights":dict(weights),"bias":bias,"train_accuracy":correct/len(cached) if cached else 0.0,"positive_weight":pw,"negative_weight":nw}

def _active_symbolic_edges(rules:dict[tuple[str,str,str|None],int],combo:tuple[str,...])->list[tuple[str,str]]:
    edges=[]
    for a,b in itertools.combinations(TYPES,2):
        if a not in combo or b not in combo: continue
        contextual=[(ctx,rules[(a,b,ctx)]) for ctx in combo if ctx not in {a,b} and (a,b,ctx) in rules]
        sign=contextual[0][1] if contextual and all(v==contextual[0][1] for _,v in contextual) else rules.get((a,b,None))
        if sign==1: edges.append((a,b))
        elif sign==-1: edges.append((b,a))
    return edges

def _symbolic_ok(order:tuple[str,...],edges:list[tuple[str,str]])->bool:
    return all(_before(order,a,b) for a,b in edges)

def _factor_score(order:tuple[str,...],combo:tuple[str,...],model:dict[str,Any])->float:
    feats=_factor_features(combo,order); weights=model["weights"]
    return float(model["bias"])+sum(weights.get(k,0.0)*v for k,v in feats.items())


def _symbolic_exact(combo:tuple[str,...],rules:dict[tuple[str,str,str|None],int])->tuple[tuple[str,...],int]:
    edges=_active_symbolic_edges(rules,combo); candidates=list(itertools.permutations(combo))
    valid=[p for p in candidates if _symbolic_ok(p,edges)]
    return (min(valid) if valid else min(candidates,key=lambda p:sum(not _before(p,a,b) for a,b in edges)),len(candidates))

def _factor_exact(combo:tuple[str,...],factors:dict[str,Any])->tuple[tuple[str,...],int]:
    candidates=list(itertools.permutations(combo)); best=max(candidates,key=lambda p:(_factor_score(p,combo,factors),tuple(reversed(p))))
    return best,len(candidates)

def _has_path(edges:set[tuple[str,str]],src:str,dst:str)->bool:
    stack=[src]; seen=set()
    while stack:
        x=stack.pop()
        if x==dst:return True
        if x in seen:continue
        seen.add(x); stack.extend(b for a,b in edges if a==x)
    return False

def _toposort(combo:tuple[str,...],weighted_edges:list[tuple[float,str,str]])->tuple[tuple[str,...],int]:
    # Compile pair preferences into an acyclic precedence graph by descending confidence.
    edges:set[tuple[str,str]]=set(); checks=0
    for weight,a,b in sorted(weighted_edges,key=lambda x:(-x[0],x[1],x[2])):
        checks+=1
        if not _has_path(edges,b,a): edges.add((a,b))
    incoming={x:0 for x in combo}
    for a,b in edges: incoming[b]+=1
    ready=sorted(x for x,v in incoming.items() if v==0); out=[]
    while ready:
        x=ready.pop(0); out.append(x)
        for a,b in sorted(edges):
            if a==x:
                incoming[b]-=1
                if incoming[b]==0 and b not in out and b not in ready: ready.append(b); ready.sort()
    if len(out)<len(combo): out.extend(sorted(set(combo)-set(out)))
    return tuple(out),checks

def _symbolic_compiled(combo:tuple[str,...],rules:dict[tuple[str,str,str|None],int])->tuple[tuple[str,...],int]:
    weighted=[]
    for a,b in _active_symbolic_edges(rules,combo):
        # contextual clauses are treated as more specific than base clauses.
        confidence=2.0 if any((min(a,b),max(a,b),c) in rules for c in combo if c not in {a,b}) else 1.0
        weighted.append((confidence,a,b))
    return _toposort(combo,weighted)

def _factor_weighted_edges(combo:tuple[str,...],factors:dict[str,Any])->list[tuple[float,str,str]]:
    weighted=[]; weights=factors["weights"]
    for a,b in itertools.combinations(TYPES,2):
        if a not in combo or b not in combo:continue
        score=weights.get((a,b,None),0.0)+sum(weights.get((a,b,c),0.0) for c in combo if c not in {a,b})
        if abs(score)>1e-9: weighted.append((abs(score),a,b) if score>0 else (abs(score),b,a))
    return sorted(weighted,key=lambda x:(-x[0],x[1],x[2]))

def _factor_compiled(combo:tuple[str,...],factors:dict[str,Any])->tuple[tuple[str,...],int]:
    return _toposort(combo,_factor_weighted_edges(combo,factors))

def _factor_compiled_budgeted(combo:tuple[str,...],factors:dict[str,Any],edge_budget:int)->tuple[tuple[str,...],int]:
    # Strong matched decoder control: keep exactly the top-k typed factor edges,
    # where k equals the number of active symbolic precedence edges for this input.
    # This prevents a sparse symbolic registry from winning merely by using fewer edges.
    edges=_factor_weighted_edges(combo,factors)[:max(0,edge_budget)]
    return _toposort(combo,edges)

def _binom_two_sided(wins:int,losses:int)->float:
    n=wins+losses
    if n==0:return 1.0
    k=min(wins,losses); tail=sum(math.comb(n,i) for i in range(k+1))/(2**n)
    return min(1.0,2*tail)


def run_b10_cpu_p0() -> dict[str, Any]:
    rows=[]; train_records=0
    for wi,world in enumerate(WORLDS):
        train,test=_split(wi,world); records=_training_records(world,train); train_records+=len(records)
        symbolic=_symbolic_learn(records); factors=_factor_learn(records)
        for combo in test:
            truth={p for p in itertools.permutations(combo) if _legal(world,combo,p)}
            se,se_cost=_symbolic_exact(combo,symbolic); fe,fe_cost=_factor_exact(combo,factors)
            sc,sc_cost=_symbolic_compiled(combo,symbolic); fc,fc_cost=_factor_compiled(combo,factors)
            symbolic_edges=len(_active_symbolic_edges(symbolic,combo))
            fb,fb_cost=_factor_compiled_budgeted(combo,factors,symbolic_edges)
            rows.append({"world":wi,"combo":list(combo),"active_truth_constraints":len(_constraints(world,combo)),"legal_orders":len(truth),
                "symbolic_exact_success":int(se in truth),"factor_exact_success":int(fe in truth),
                "symbolic_compiled_success":int(sc in truth),"factor_compiled_success":int(fc in truth),
                "factor_budgeted_compiled_success":int(fb in truth),"matched_edge_budget":symbolic_edges,
                "symbolic_exact_candidates":se_cost,"factor_exact_candidates":fe_cost,
                "symbolic_compiled_edge_checks":sc_cost,"factor_compiled_edge_checks":fc_cost,"factor_budgeted_edge_checks":fb_cost})
    n=len(rows)
    sx=sum(r["symbolic_exact_success"] for r in rows); fx=sum(r["factor_exact_success"] for r in rows)
    sc=sum(r["symbolic_compiled_success"] for r in rows); fc=sum(r["factor_compiled_success"] for r in rows)
    fbc=sum(r["factor_budgeted_compiled_success"] for r in rows)
    sw=sum(r["symbolic_exact_success"]>r["factor_exact_success"] for r in rows)
    fw=sum(r["factor_exact_success"]>r["symbolic_exact_success"] for r in rows)
    p=_binom_two_sided(sw,fw); rep_adv=(sx-fx)/n if n else 0.0
    sym_cost=sum(r["symbolic_exact_candidates"] for r in rows)/n
    sym_comp=sum(r["symbolic_compiled_edge_checks"] for r in rows)/n
    factor_cost=sum(r["factor_exact_candidates"] for r in rows)/n
    factor_comp=sum(r["factor_compiled_edge_checks"] for r in rows)/n
    factor_budgeted_comp=sum(r["factor_budgeted_edge_checks"] for r in rows)/n
    rep_survives=rep_adv>=0.10 and p<0.05
    compile_noninferior=(sc/n if n else 0)>=(sx/n if n else 0)-0.02 and sym_comp<sym_cost
    factor_compile_matches=(fc/n if n else 0)>=(sc/n if n else 0)-0.02 and factor_comp<=sym_comp*1.10
    factor_budgeted_matches=(fbc/n if n else 0)>=(sc/n if n else 0)-0.02 and factor_budgeted_comp<=sym_comp*1.10
    if not rep_survives and factor_budgeted_matches: decision="STOP_MATCHED_NARY_EQUIVALENT"
    elif not rep_survives: decision="PIVOT_COMPILED_DECODER_ONLY"
    elif not compile_noninferior: decision="STOP_COMPILED_DECODER_CLAIM"
    else: decision="P0_SIGNAL_CONTINUE"
    return {
        "schema_version":"1.0","experiment_id":"P0-B10-TYPED-MEMORY-ORDER","created_at":_now(),
        "design":{"worlds":len(WORLDS),"held_out_combinations":n,"train_records":train_records,"types":list(TYPES),
            "representation_cells":["symbolic-clauses","typed-nary-factor"],"decoder_cells":["exact","compiled"],
            "independent_truth":"exhaustive legal-order enumeration"},
        "metrics":{"symbolic_exact_accuracy":sx/n,"factor_exact_accuracy":fx/n,
            "symbolic_compiled_accuracy":sc/n,"factor_compiled_accuracy":fc/n,"factor_budgeted_compiled_accuracy":fbc/n,
            "symbolic_only_wins":sw,"factor_only_wins":fw,"paired_sign_p":p,
            "symbolic_representation_advantage":rep_adv,"symbolic_exact_candidates_mean":sym_cost,
            "symbolic_compiled_edge_checks_mean":sym_comp,"factor_exact_candidates_mean":factor_cost,
            "factor_compiled_edge_checks_mean":factor_comp,"factor_budgeted_edge_checks_mean":factor_budgeted_comp},
        "gates":{"representation_advantage_required":0.10,"paired_p_required":0.05,
            "representation_claim_pass":rep_survives,"compiled_noninferior_and_cheaper":compile_noninferior,
            "matched_factor_compiled_matches":factor_compile_matches,"matched_edge_budget_factor_matches":factor_budgeted_matches},
        "baseline_fairness":{"same_typed_variables":True,"same_training_records":True,"same_held_out_combinations":True,"same_exact_candidate_enumeration":True,"compiled_edge_budget_matched":True,"test_outcomes_used_for_decoding":False},
        "decision":decision,
        "standalone_claim_stop_authorized":decision=="STOP_MATCHED_NARY_EQUIVALENT",
        "real_agent_generalization_not_tested":True,
        "next_action":"Stop standalone B-10 and do not spend GPU; retain this P0 as the matched-simplification falsifier and return the drop/merge decision to human review." if decision=="STOP_MATCHED_NARY_EQUIVALENT" else "Return the surviving subclaim to human review before any further experiment.",
        "scientific_authority":"CPU P0 mechanism falsifier for the typed-ordering claim; no real-agent performance claim","rows":rows}


def write_b10_cpu_p0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_b10_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_B10_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state

if __name__=="__main__": print(json.dumps(write_b10_cpu_p0(),ensure_ascii=False))
