from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-b3-interference-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-b3-interference-cpu.js"
PATHWAYS=("item","content","rank","co-retrieval")


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _cases()->list[dict[str,Any]]:
    rows=[]
    for i in range(24):
        pathway=PATHWAYS[i%4]
        rows.append({
          "case_id":f"b3-{i:02d}","pathway":pathway,
          "memory_a":f"lesson-a-{i:02d}","memory_b":f"lesson-b-{i:02d}",
          "base_future_benefit":2+(i%3),"audit_seed":100+i,
        })
    return rows


def _audit_harm(case:dict[str,Any],arm:str)->int:
    p=case["pathway"]
    if arm=="full": return 1
    if arm=="content-correct": return int(p!="content")
    if arm=="rank-low": return int(p!="rank")
    if arm=="a-only": return int(p!="co-retrieval")
    if arm=="b-only": return 0
    if arm=="none": return 0
    raise KeyError(arm)


def _pathway_policy(case:dict[str,Any])->tuple[str,int,list[dict[str,Any]]]:
    calls=[]
    for arm in ("full","content-correct","rank-low","a-only"):
        calls.append({"arm":arm,"harm":_audit_harm(case,arm)})
    by={x["arm"]:x["harm"] for x in calls}
    if by["content-correct"]==0: action="rewrite"
    elif by["rank-low"]==0: action="rank-cap"
    elif by["a-only"]==0: action="mutex"
    else: action="quarantine-a"
    return action,len(calls),calls


def _simple_policy(case:dict[str,Any])->tuple[str,int,list[dict[str,Any]]]:
    # Frozen strongest simplification: per-item causal selector + simple co-occurrence exclusion.
    calls=[]
    for arm in ("full","a-only","b-only","none"):
        calls.append({"arm":arm,"harm":_audit_harm(case,arm)})
    by={x["arm"]:x["harm"] for x in calls}
    if by["a-only"]==0 and by["b-only"]==0: action="mutex"
    elif by["a-only"]==1: action="quarantine-a"
    else: action="quarantine-b"
    return action,len(calls),calls


def _future(case:dict[str,Any],action:str)->dict[str,Any]:
    p=case["pathway"]; benefit=int(case["base_future_benefit"])
    if p=="item":
        harm=0 if action=="quarantine-a" else 1
        retained=0 if action=="quarantine-a" else benefit
    elif p=="content":
        harm=0 if action in {"rewrite","quarantine-a"} else 1
        retained=benefit if action=="rewrite" else 0 if action=="quarantine-a" else benefit
    elif p=="rank":
        harm=0 if action in {"rank-cap","quarantine-a"} else 1
        retained=benefit if action=="rank-cap" else 0 if action=="quarantine-a" else benefit
    else:
        harm=0 if action in {"mutex","quarantine-a","quarantine-b"} else 1
        retained=benefit if action=="mutex" else max(0,benefit-1)
    return {"future_harm":harm,"retained_benefit":retained,"net_utility":retained-4*harm}


def run_b3_cpu_screen() -> dict[str,Any]:
    rows=[]; pcalls=scalls=0; pharm=sharm=0; putil=sutil=0; pbenef=sbenef=0
    by_path={p:{"n":0,"pathway_utility":0,"simple_utility":0,"pathway_harm":0,"simple_harm":0} for p in PATHWAYS}
    for case in _cases():
        pa,pc,parms=_pathway_policy(case); sa,sc,sarms=_simple_policy(case)
        pf=_future(case,pa); sf=_future(case,sa)
        pcalls+=pc; scalls+=sc; pharm+=pf["future_harm"]; sharm+=sf["future_harm"]
        putil+=pf["net_utility"]; sutil+=sf["net_utility"]; pbenef+=pf["retained_benefit"]; sbenef+=sf["retained_benefit"]
        b=by_path[case["pathway"]]; b["n"]+=1; b["pathway_utility"]+=pf["net_utility"]; b["simple_utility"]+=sf["net_utility"]; b["pathway_harm"]+=pf["future_harm"]; b["simple_harm"]+=sf["future_harm"]
        rows.append({"case_id":case["case_id"],"truth_pathway":case["pathway"],"pathway_action":pa,"simple_action":sa,"pathway_audit":parms,"simple_audit":sarms,"pathway_future":pf,"simple_future":sf})
    n=len(rows); same_cost=pcalls==scalls; safe=pharm==0 and sharm==0
    utility_gain=(putil-sutil)/max(1,abs(sutil)); benefit_gain=pbenef-sbenef
    signal=same_cost and safe and utility_gain>=0.15 and benefit_gain>0
    equivalent=same_cost and pharm==sharm and putil==sutil
    decision="STOP_MATCHED_PER_ITEM_COOCCURRENCE_EQUIVALENT" if equivalent else "SCREENING_SIGNAL_REAL_COINTERACTION_REQUIRED" if signal else "SCREENING_NO_SIGNAL"
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"retrieval-interference-auditor","code":"B-3",
      "scientific_role":"synthetic mechanism screening only; cannot establish that real memory co-retrieval interference exists",
      "design":{"cases":n,"pathways":list(PATHWAYS),"cases_per_pathway":n//len(PATHWAYS),"audit_calls_per_candidate":4,"independent_truth":"programmatic interference oracle","matched_audit_cost":same_cost},
      "metrics":{"pathway_audit_calls":pcalls,"simple_audit_calls":scalls,"pathway_future_harm":pharm,"simple_future_harm":sharm,"pathway_retained_benefit":pbenef,"simple_retained_benefit":sbenef,"pathway_net_utility":putil,"simple_net_utility":sutil,"relative_net_utility_gain":utility_gain,"retained_benefit_gain":benefit_gain},
      "by_pathway":by_path,"rows":rows,
      "matched_simplification":{"baseline":"per-item causal selector + simple co-occurrence exclusion","same_audit_calls":same_cost,"equivalent":equivalent},
      "runtime_preflight_snapshot":{"measured_on":"2026-08-11","server":"60","gpu_state":"3x RTX3090-class idle","registered_profile_runtime":"FAIL: adapter importable but ALFWorld package missing","legacy_runtime_overlay":"FAIL: Python 3.8 interpreter mixed with Python>=3.9/3.12 TextWorld/Numpy packages","python313_base":"FAIL: Torch present but Transformers stack absent","installation_or_environment_mutation_attempted":False,"decision":"HOLD_RUNTIME_ENVIRONMENT_DRIFT"},
      "decision":decision,"p1_authorized":False,
      "next_action":"Collect a small real ALFWorld co-retrieval factorial block; freeze retrieval/content/rank/co-retrieval arms and compare the same matched baseline before any learned repair." if signal else "Return B-3 to human DROP/merge review."}


def write_b3_cpu_screen(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_b3_cpu_screen(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_B3_INTERFERENCE_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__=="__main__": print(json.dumps(write_b3_cpu_screen(),ensure_ascii=False,indent=2))
