from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-a6-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-a6-cpu.js"


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _cases()->list[dict[str,Any]]:
    rows=[]
    for i in range(24):
        n=4+(i%5); atoms=tuple(f"u{j}" for j in range(n))
        if i%3==0: fault=(atoms[(2*i+1)%n],)
        else:
            a=(2*i+1)%n; b=(3*i+2)%n
            if b==a:b=(b+1)%n
            fault=tuple(sorted((atoms[a],atoms[b])))
        # Structural prior is frozen independently of the injected fault: a rotation
        # of update order. Every baseline receives the same ordering, so no method gets
        # privileged access to the ground-truth fault set.
        shift=(2*i+1)%n; prior=atoms[shift:]+atoms[:shift]
        rows.append({"case_id":f"c{i:02d}","atoms":atoms,"fault":fault,"prior":prior})
    return rows

def _oracle(fault:set[str])->tuple[Callable[[set[str]],bool],dict[str,int]]:
    cost={"tests":0}
    def fails(active:set[str])->bool:
        cost["tests"]+=1
        return fault.issubset(active)
    return fails,cost

def _ddmin(atoms:tuple[str,...],fails:Callable[[set[str]],bool])->set[str]:
    current=list(atoms); n=2
    if not fails(set(current)): return set()
    while len(current)>=2:
        size=(len(current)+n-1)//n; subsets=[current[i:i+size] for i in range(0,len(current),size)]; reduced=False
        for subset in subsets:
            if fails(set(subset)):
                current=list(subset); n=max(n-1,2); reduced=True; break
        if reduced: continue
        for subset in subsets:
            comp=[x for x in current if x not in subset]
            if comp and fails(set(comp)):
                current=comp; n=max(n-1,2); reduced=True; break
        if reduced: continue
        if n>=len(current): break
        n=min(len(current),2*n)
    return set(current)

def _one_at_a_time(atoms:tuple[str,...],fails:Callable[[set[str]],bool])->set[str]:
    full=set(atoms); needed=set()
    if not fails(full): return set()
    for atom in atoms:
        if not fails(full-{atom}): needed.add(atom)
    return needed

def _active_group(atoms:tuple[str,...],fails:Callable[[set[str]],bool])->set[str]:
    # Monotone sparse-fault group testing for fault sets of size <=2. Every query is
    # an enable/disable intervention over the same atom universe used by ddmin.
    full=set(atoms)
    if not fails(full): return set()
    candidates=list(atoms)
    while len(candidates)>1:
        half=candidates[:max(1,len(candidates)//2)]
        # If disabling half repairs failure, at least one causal atom is in half.
        if not fails(full-set(half)): candidates=half
        else: candidates=[x for x in candidates if x not in half]
    first=candidates[0]
    if fails({first}): return {first}
    remaining=[x for x in atoms if x!=first]
    # For a pair fault, {first}+subset fails iff the second causal atom is in subset.
    while len(remaining)>1:
        half=remaining[:max(1,len(remaining)//2)]
        if fails({first,*half}): remaining=half
        else: remaining=[x for x in remaining if x not in half]
    return {first,remaining[0]} if remaining else {first}

def _binary_group_testing(atoms:tuple[str,...],fails:Callable[[set[str]],bool])->set[str]:
    # Non-learning matched simplification. It knows only the preregistered sparse
    # fault-size ceiling (<=2) and uses deterministic binary group tests.
    full=set(atoms)
    if not fails(full): return set()
    cand=list(atoms)
    while len(cand)>1:
        half=cand[:max(1,len(cand)//2)]
        cand=half if not fails(full-set(half)) else [x for x in cand if x not in half]
    first=cand[0]
    if fails({first}): return {first}
    rem=[x for x in atoms if x!=first]
    while len(rem)>1:
        half=rem[:max(1,len(rem)//2)]
        rem=half if fails({first,*half}) else [x for x in rem if x not in half]
    return {first,rem[0]} if rem else {first}

def _last_update(atoms:tuple[str,...],fails:Callable[[set[str]],bool])->set[str]:
    # Zero-search heuristic: rollback only the most recent atom under the shared order.
    full=set(atoms); fails(full)
    return {atoms[-1]}

def _exact_shapley(atoms:tuple[str,...],fails:Callable[[set[str]],bool])->set[str]:
    import itertools, math
    cache={}
    def value(s:set[str])->int:
        key=tuple(sorted(s))
        if key not in cache: cache[key]=int(fails(set(s)))
        return cache[key]
    n=len(atoms); score={a:0.0 for a in atoms}
    for atom in atoms:
        others=[x for x in atoms if x!=atom]
        for k in range(len(others)+1):
            weight=math.factorial(k)*math.factorial(n-k-1)/math.factorial(n)
            for subset in itertools.combinations(others,k):
                s=set(subset); score[atom]+=weight*(value(s|{atom})-value(s))
    return {a for a,v in score.items() if v>1e-10}


def _run_method(case:dict[str,Any],method:Callable[[tuple[str,...],Callable[[set[str]],bool]],set[str]])->dict[str,Any]:
    fault=set(case["fault"]); fails,cost=_oracle(fault); pred=method(tuple(case["prior"]),fails)
    return {"rollback":sorted(pred),"tests":cost["tests"],"exact":pred==fault,"rollback_size":len(pred),"benign_removed":len(pred-fault)}

def _sign_p(active:list[int],baseline:list[int])->float:
    import math
    wins=sum(a<b for a,b in zip(active,baseline)); losses=sum(a>b for a,b in zip(active,baseline)); n=wins+losses
    if n==0:return 1.0
    k=min(wins,losses); tail=sum(math.comb(n,i) for i in range(k+1))/(2**n)
    return min(1.0,2*tail)


def run_a6_cpu_p0()->dict[str,Any]:
    methods={"active-causal":_active_group,"binary-group-testing":_binary_group_testing,"delta-debugging":_ddmin,"one-at-a-time":_one_at_a_time,"last-update":_last_update,"exact-shapley":_exact_shapley}
    rows=[]
    for case in _cases():
        results={name:_run_method(case,fn) for name,fn in methods.items()}
        rows.append({"case_id":case["case_id"],"n_updates":len(case["atoms"]),"fault_size":len(case["fault"]),"fault":list(case["fault"]),"shared_order":list(case["prior"]),"methods":results})
    summary={}
    for name in methods:
        vals=[r["methods"][name] for r in rows]
        summary[name]={"exact_recovery":sum(v["exact"] for v in vals)/len(vals),"mean_tests":sum(v["tests"] for v in vals)/len(vals),"max_tests":max(v["tests"] for v in vals),"mean_rollback_size":sum(v["rollback_size"] for v in vals)/len(vals),"benign_removed":sum(v["benign_removed"] for v in vals)}
    active=[r["methods"]["active-causal"]["tests"] for r in rows]; dd=[r["methods"]["delta-debugging"]["tests"] for r in rows]; simple=[r["methods"]["binary-group-testing"]["tests"] for r in rows]
    active_exact=summary["active-causal"]["exact_recovery"]==1.0; dd_exact=summary["delta-debugging"]["exact_recovery"]==1.0; simple_exact=summary["binary-group-testing"]["exact_recovery"]==1.0
    saving=(summary["delta-debugging"]["mean_tests"]-summary["active-causal"]["mean_tests"])/summary["delta-debugging"]["mean_tests"]
    simple_saving=(summary["binary-group-testing"]["mean_tests"]-summary["active-causal"]["mean_tests"])/summary["binary-group-testing"]["mean_tests"]
    paired_p=_sign_p(active,dd); simple_p=_sign_p(active,simple)
    matched_simple= simple_exact and abs(simple_saving)<1e-12 and all(a==b for a,b in zip(active,simple))
    pass_gate=active_exact and dd_exact and saving>=0.15 and paired_p<0.05 and not matched_simple
    decision="STOP_MATCHED_GROUP_TESTING_EQUIVALENT" if matched_simple else ("P0_SIGNAL_CONTINUE_REAL_SEQUENCE_GATE" if pass_gate else "STOP_NO_ADVANTAGE_OVER_DELTA_DEBUGGING")
    return {"schema_version":"1.0","experiment_id":"P0-A6-ACTIVE-CAUSAL-MINIMAL-ROLLBACK","created_at":_now(),"design":{"cases":24,"update_range":[4,8],"fault_sizes":[1,2],"shared_structural_order":True,"fault_independent_prior":True,"independent_truth":"programmatic minimal fault set","strongest_baselines":["binary-group-testing","delta-debugging","one-at-a-time","exact-shapley"]},"summary":summary,"paired_active_vs_ddmin":{"relative_mean_test_saving":saving,"paired_sign_p":paired_p,"minimum_saving_required":0.15,"p_required":0.05},"matched_simplification":{"baseline":"binary-group-testing","relative_mean_test_saving":simple_saving,"paired_sign_p":simple_p,"per_case_test_counts_identical":all(a==b for a,b in zip(active,simple)),"equivalent":matched_simple},"decision":decision,"standalone_claim_stop_authorized":decision=="STOP_MATCHED_GROUP_TESTING_EQUIVALENT","synthetic_gate_pass":pass_gate,"real_sequence_gate_required":pass_gate,"next_action":"Stop standalone A-6; the current active query policy is exactly reproduced by non-learning binary group testing under the same sparse-fault prior." if matched_simple else "Open the real-sequence gate only after human review.","scientific_authority":"CPU synthetic matched-simplification falsifier; cannot establish real-sequence benefit","rows":rows}


def write_a6_cpu_p0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_a6_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_A6_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state

if __name__=="__main__": print(json.dumps(write_a6_cpu_p0(),ensure_ascii=False))
