from __future__ import annotations

import itertools
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-b6-memory-utility-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-b6-memory-utility-cpu.js"


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _rows()->list[dict[str,Any]]:
    rows=[]
    for m in range(12):
        for t in range(25):
            recency=1+((2*t+m)%6); frequency=1+((t+2*m)%5)
            # Independent replay truth: old/rare memories become harmful; all others remain beneficial.
            utility=-1 if recency>=4 and frequency<=2 else 1
            rows.append({"memory_id":f"m{m:02d}","activation":t,"recency":recency,"frequency":frequency,"utility_on_minus_off":utility,"audited":t%5==0})
    return rows


def _features(row:dict[str,Any])->list[float]:
    return [1.0,row["recency"]/6,row["frequency"]/5,(row["recency"]*row["frequency"])/30]


def _fit_logistic(train:list[dict[str,Any]],epochs:int=700,lr:float=0.2)->list[float]:
    w=[0.0]*len(_features(train[0]))
    for _ in range(epochs):
        g=[0.0]*len(w)
        for row in train:
            x=_features(row); y=float(row["utility_on_minus_off"]<0); z=sum(a*b for a,b in zip(w,x)); p=1/(1+math.exp(-max(-30,min(30,z)))); err=p-y
            for j,v in enumerate(x):g[j]+=err*v
        for j in range(len(w)):w[j]-=lr*g[j]/len(train)
    return w


def _score(w:list[float],row:dict[str,Any])->float:
    z=sum(a*b for a,b in zip(w,_features(row))); return 1/(1+math.exp(-max(-30,min(30,z))))


def _fit_threshold(train:list[dict[str,Any]])->tuple[int,int]:
    best=None
    for rcut,fcut in itertools.product(range(2,7),range(1,6)):
        correct=sum(((row["recency"]>=rcut and row["frequency"]<=fcut)==(row["utility_on_minus_off"]<0)) for row in train)
        score=(correct,-rcut,fcut)
        if best is None or score>best[0]:best=(score,(rcut,fcut))
    return best[1]


def _eval(rows:list[dict[str,Any]],policy)->dict[str,Any]:
    retained_harm=0; quarantined_benefit=0; retained_benefit=0; decisions=[]
    for row in rows:
        quarantine=bool(policy(row)); harmful=row["utility_on_minus_off"]<0
        retained_harm+=int(harmful and not quarantine); quarantined_benefit+=int((not harmful) and quarantine); retained_benefit+=int((not harmful) and not quarantine)
        decisions.append({"memory_id":row["memory_id"],"activation":row["activation"],"quarantine":quarantine,"harmful":harmful})
    return {"n":len(rows),"retained_harm":retained_harm,"quarantined_benefit":quarantined_benefit,"retained_benefit":retained_benefit,"decisions":decisions}


def run_b6_cpu_p0()->dict[str,Any]:
    rows=_rows(); audited=[r for r in rows if r["audited"]]; future=[r for r in rows if not r["audited"]]
    w=_fit_logistic(audited); threshold=0.5; cuts=_fit_threshold(audited)
    learned=_eval(future,lambda r:_score(w,r)>=threshold)
    simple=_eval(future,lambda r:r["recency"]>=cuts[0] and r["frequency"]<=cuts[1])
    ttl=_eval(future,lambda r:r["recency"]>=4)
    equivalent=(learned["retained_harm"]==simple["retained_harm"] and learned["quarantined_benefit"]==simple["quarantined_benefit"] and all(a["quarantine"]==b["quarantine"] for a,b in zip(learned["decisions"],simple["decisions"])))
    simple_dominates=(simple["retained_harm"]<=learned["retained_harm"] and simple["quarantined_benefit"]<=learned["quarantined_benefit"] and simple["retained_benefit"]>=learned["retained_benefit"])
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"memory-half-life","code":"B-6",
      "scientific_role":"CPU longitudinal reuse P0 with frozen 20% activation audit and independent ON/OFF utility truth",
      "design":{"memories":12,"reuse_opportunities":len(rows),"audit_fraction":len(audited)/len(rows),"audited_activations":len(audited),"future_activations":len(future),"independent_truth":"programmatic matched memory ON/OFF utility","same_audit_labels":True},
      "utility_hazard":{"weights":w,"future":learned},"recency_frequency":{"cuts":{"recency":cuts[0],"frequency":cuts[1]},"future":simple},"ttl":{"future":ttl},
      "matched_simplification":{"baseline":"recency+frequency threshold tuned on the identical 20% audited ON/OFF labels","same_audit_budget":True,"same_future_reuse_stream":True,"decision_equivalent":equivalent,"simple_dominates":simple_dominates},
      "decision":"STOP_RECENCY_FREQUENCY_POLICY_DOMINATES" if simple_dominates else "P0_SIGNAL_CONTINUE","standalone_claim_stop_authorized":simple_dominates,"p1_authorized":False,
      "next_action":"Retain only a simple cache/revalidation policy; the learned utility-hazard model adds no future-reuse decision value." if simple_dominates else "Validate the surviving hazard advantage on a real longitudinal reuse stream after human review."}


def write_b6_cpu_p0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_b6_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_B6_MEMORY_UTILITY_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__=="__main__": print(json.dumps(write_b6_cpu_p0(),ensure_ascii=False,indent=2))
