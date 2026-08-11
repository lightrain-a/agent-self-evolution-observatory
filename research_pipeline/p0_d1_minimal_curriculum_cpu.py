from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-d1-minimal-curriculum-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-d1-minimal-curriculum-cpu.js"
NUISANCE=tuple(f"n{i}" for i in range(12))


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _rules()->list[dict[str,Any]]:
    return [{"rule_id":f"r{i:02d}","causal":f"boundary-{i:02d}"} for i in range(20)]


def _source_candidates(rule:dict[str,Any])->list[set[str]]:
    rows=[]; idx=int(rule["rule_id"][1:])
    for j in range(4):
        nuis={NUISANCE[(idx+2*j)%12],NUISANCE[(idx+3*j+1)%12],NUISANCE[(idx+5*j+2)%12]}
        rows.append({rule["causal"],*nuis})
    return rows


def _verifier(rule:dict[str,Any],constraints:set[str])->bool:
    # A legal task is a counterexample iff the true boundary atom remains.
    return rule["causal"] in constraints


def _minimize(rule:dict[str,Any],candidate:set[str])->tuple[set[str],int]:
    cur=set(candidate); calls=0
    for atom in sorted(candidate):
        trial=cur-{atom}; calls+=1
        if _verifier(rule,trial): cur=trial
    return cur,calls


def _intersection(candidates:list[set[str]])->set[str]:
    out=set(candidates[0])
    for c in candidates[1:]: out&=c
    return out


def _hidden(rule:dict[str,Any])->list[set[str]]:
    idx=int(rule["rule_id"][1:]); rows=[]
    for j in range(3):
        rows.append({rule["causal"],NUISANCE[(idx+7*j+4)%12],f"hidden-{idx}-{j}"})
    return rows


def _evaluate(updates:dict[str,set[str]])->dict[str,Any]:
    correct=0; total=0; false_boundaries=0
    for rule in _rules():
        learned=updates[rule["rule_id"]]
        false_boundaries+=max(0,len(learned)-1)
        for case in _hidden(rule):
            prediction=bool(learned & case); truth=_verifier(rule,case)
            correct+=int(prediction==truth); total+=1
    return {"hidden_cases":total,"hidden_boundary_accuracy":correct/total,"extra_noncausal_atoms_in_updates":false_boundaries}


def run_d1_cpu_p0()->dict[str,Any]:
    minimal_updates={}; intersection_updates={}; raw_updates={}; min_calls=base_calls=0; one_minimal=0
    for rule in _rules():
        candidates=_source_candidates(rule); base_calls+=len(candidates)
        minimized=[]
        for candidate in candidates:
            # Candidate validity call is shared with all arms; minimization adds deletion calls only.
            m,calls=_minimize(rule,candidate); min_calls+=calls; minimized.append(m); one_minimal+=int(len(m)==1 and rule["causal"] in m)
        minimal_updates[rule["rule_id"]]=set.intersection(*minimized)
        intersection_updates[rule["rule_id"]]=_intersection(candidates)
        raw_updates[rule["rule_id"]]=set(candidates[0])
    me=_evaluate(minimal_updates); ie=_evaluate(intersection_updates); re=_evaluate(raw_updates)
    # Compiled update strings are fixed-length padded; final training-token budget is therefore identical.
    token_budget=20*16
    equivalent=(me["hidden_boundary_accuracy"]==ie["hidden_boundary_accuracy"]==1.0 and me["extra_noncausal_atoms_in_updates"]==ie["extra_noncausal_atoms_in_updates"]==0 and intersection_updates==minimal_updates)
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"counterexample-generating-curriculum","code":"D-1",
      "scientific_role":"CPU verifier-grounded curriculum P0; proposer is frozen and independent hidden boundaries are never used in minimization/selection",
      "design":{"rules":20,"verified_candidates_per_rule":4,"verified_candidates":80,"hidden_boundary_cases":60,"final_training_tokens_per_arm":token_budget,"same_final_training_tokens":True,"independent_truth":"programmatic boundary verifier"},
      "one_minimal":{"verified_1minimal_examples":one_minimal,"extra_verifier_calls_for_minimization":min_calls,"compiled_updates":{k:sorted(v) for k,v in minimal_updates.items()},"evaluation":me},
      "matched_intersection":{"extra_verifier_calls_after_validation":0,"compiled_updates":{k:sorted(v) for k,v in intersection_updates.items()},"evaluation":ie},
      "nonminimal_first":{"compiled_updates":{k:sorted(v) for k,v in raw_updates.items()},"evaluation":re},
      "matched_simplification":{"baseline":"intersection of multiple verifier-confirmed non-minimal counterexamples per rule","same_verified_candidates":True,"same_final_training_tokens":True,"same_hidden_boundary_set":True,"compiled_updates_identical":intersection_updates==minimal_updates,"equivalent":equivalent,"avoided_extra_verifier_calls":min_calls},
      "decision":"STOP_MATCHED_INTERSECTION_FILTER_EQUIVALENT" if equivalent else "P0_SIGNAL_CONTINUE","standalone_claim_stop_authorized":equivalent,"p1_authorized":False,
      "next_action":"Keep verifier counterexamples but drop per-example 1-minimality as a standalone curriculum variable; merge into generic counterexample learning." if equivalent else "Validate 1-minimality on a real boundary task family after human review."}


def write_d1_cpu_p0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_d1_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_D1_MINIMAL_CURRICULUM_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__=="__main__": print(json.dumps(write_d1_cpu_p0(),ensure_ascii=False,indent=2))
