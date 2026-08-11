from __future__ import annotations

import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-b5-applicability-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-b5-applicability-cpu.js"
PREDICATES=tuple(f"p{i}" for i in range(6))


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _skill(index:int)->dict[str,Any]:
    base=PREDICATES[index%6]
    extra1=PREDICATES[(index+2)%6]
    extra2=PREDICATES[(index+4)%6] if index%3==0 else None
    true={base,extra1}|({extra2} if extra2 else set())
    return {"skill_id":f"s{index:02d}","base":{base},"true":true,"complexity_budget":len(true)}


def _all_assignments()->list[dict[str,int]]:
    return [{p:int((mask>>i)&1) for i,p in enumerate(PREDICATES)} for mask in range(1<<len(PREDICATES))]


def _applies(gate:set[str],x:dict[str,int])->bool:
    return all(x[p]==1 for p in gate)


def _dataset(skill:dict[str,Any])->dict[str,list[dict[str,int]]]:
    xs=_all_assignments(); base=skill["base"]; truth=skill["true"]
    positives=[x for x in xs if _applies(truth,x)]
    counter=[x for x in xs if _applies(base,x) and not _applies(truth,x)]
    old=positives[:min(8,len(positives))]
    cex=counter[:min(12,len(counter))]
    hidden_pos=positives[len(old):] or positives[-2:]
    hidden_neg=counter[len(cex):] or counter[-2:]
    return {"old_positive":old,"counterexamples":cex,"hidden_positive":hidden_pos,"hidden_negative":hidden_neg}


def _monotone(skill:dict[str,Any],data:dict[str,list[dict[str,int]]])->set[str]:
    gate=set(skill["base"]); remaining=list(data["counterexamples"])
    while remaining and len(gate)<skill["complexity_budget"]:
        candidates=[]
        for p in PREDICATES:
            if p in gate: continue
            if any(x[p]==0 for x in data["old_positive"]): continue
            rejected=sum(x[p]==0 for x in remaining)
            if rejected>0:candidates.append((rejected,p))
        if not candidates: break
        _,best=max(candidates,key=lambda t:(t[0],-PREDICATES.index(t[1]))); gate.add(best); remaining=[x for x in remaining if _applies(gate,x)]
    return gate


def _ilp_exhaustive(skill:dict[str,Any],data:dict[str,list[dict[str,int]]])->set[str]:
    base=set(skill["base"]); rest=[p for p in PREDICATES if p not in base]; feasible=[]
    for k in range(skill["complexity_budget"]-len(base)+1):
        for add in itertools.combinations(rest,k):
            gate=base|set(add)
            if all(_applies(gate,x) for x in data["old_positive"]) and all(not _applies(gate,x) for x in data["counterexamples"]):
                feasible.append(gate)
        if feasible: break
    return min(feasible,key=lambda g:tuple(PREDICATES.index(p) for p in sorted(g))) if feasible else base


def _eval(gate:set[str],data:dict[str,list[dict[str,int]]])->dict[str,Any]:
    old=sum(_applies(gate,x) for x in data["old_positive"]); hp=sum(_applies(gate,x) for x in data["hidden_positive"]); hn=sum(not _applies(gate,x) for x in data["hidden_negative"])
    return {"old_positive_preserved":old/len(data["old_positive"]),"hidden_positive_accuracy":hp/len(data["hidden_positive"]),"hidden_negative_accuracy":hn/len(data["hidden_negative"]),"gate_size":len(gate)}


def run_b5_cpu_p0()->dict[str,Any]:
    rows=[]; equal=0; mono_correct=ilp_correct=0
    for i in range(12):
        skill=_skill(i); data=_dataset(skill); mono=_monotone(skill,data); ilp=_ilp_exhaustive(skill,data); me=_eval(mono,data); ie=_eval(ilp,data)
        equal+=int(mono==ilp); mono_correct+=int(mono==skill["true"]); ilp_correct+=int(ilp==skill["true"])
        rows.append({"skill_id":skill["skill_id"],"true_gate":sorted(skill["true"]),"monotone_gate":sorted(mono),"ilp_gate":sorted(ilp),"same_gate":mono==ilp,"monotone_eval":me,"ilp_eval":ie})
    n=len(rows); equivalent=(equal==n and all(r["monotone_eval"]==r["ilp_eval"] for r in rows))
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"local-counterexample-memory-repair","code":"B-5",
      "scientific_role":"CPU applicability-gate P0 with frozen predicate vocabulary, old-positive protection, hidden boundaries, and independent programmatic truth",
      "design":{"skills":n,"predicate_vocabulary":len(PREDICATES),"old_positive_protection":True,"complexity_matched":True,"independent_truth":"programmatic applicability predicate"},
      "rows":rows,"metrics":{"monotone_true_gate_recovery":mono_correct/n,"ilp_true_gate_recovery":ilp_correct/n,"exact_gate_agreement":equal/n},
      "matched_simplification":{"baseline":"complexity-matched exhaustive ILP/precondition learner","same_predicate_vocabulary":True,"same_counterexamples":True,"same_old_positive_set":True,"same_complexity_budget":True,"equivalent":equivalent},
      "decision":"STOP_COMPLEXITY_MATCHED_ILP_EQUIVALENT" if equivalent else "P0_SIGNAL_CONTINUE","standalone_claim_stop_authorized":equivalent,"p1_authorized":False,
      "next_action":"Merge B-5 into a standard compact precondition/ILP learner; monotone counterexample specialization adds no independent boundary-generalization value." if equivalent else "Validate the surviving monotone constraint on a real skill boundary dataset after human review."}


def write_b5_cpu_p0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_b5_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_B5_APPLICABILITY_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__=="__main__": print(json.dumps(write_b5_cpu_p0(),ensure_ascii=False,indent=2))
