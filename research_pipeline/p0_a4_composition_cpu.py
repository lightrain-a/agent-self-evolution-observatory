from __future__ import annotations

import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"p0-a4-composition-cpu.json"
DEFAULT_JS=PROJECT_ROOT/"generated"/"p0-a4-composition-cpu.js"
TYPES=("prompt:schema","memory:ordering","workflow:retry","prompt:verify","memory:retry","workflow:schema")
NO_GO={frozenset(("workflow:retry","prompt:verify"))}
PRECEDENCE={("prompt:schema","memory:ordering"),("memory:retry","workflow:schema")}


def _now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _safe(sequence:tuple[str,...])->bool:
    present=set(sequence)
    if any(pair.issubset(present) for pair in NO_GO): return False
    pos={x:i for i,x in enumerate(sequence)}
    return all(a not in pos or b not in pos or pos[a]<pos[b] for a,b in PRECEDENCE)


def _pair_table()->list[dict[str,Any]]:
    rows=[]
    for a,b in itertools.combinations(TYPES,2):
        rows.append({"a":a,"b":b,"safe_ab":_safe((a,b)),"safe_ba":_safe((b,a))})
    return rows


def _registry(rows:list[dict[str,Any]])->dict[str,Any]:
    no_good=[]; precedence=[]; compatible=[]
    for r in rows:
        if not r["safe_ab"] and not r["safe_ba"]: no_good.append([r["a"],r["b"]])
        elif r["safe_ab"] and not r["safe_ba"]: precedence.append([r["a"],r["b"]])
        elif r["safe_ba"] and not r["safe_ab"]: precedence.append([r["b"],r["a"]])
        else: compatible.append([r["a"],r["b"]])
    return {"no_good":no_good,"precedence":precedence,"compatible":compatible}


def _direct(rows:list[dict[str,Any]])->dict[tuple[str,str],bool]:
    model={}
    for r in rows:
        model[(r["a"],r["b"])]=r["safe_ab"]; model[(r["b"],r["a"])]=r["safe_ba"]
    return model


def _registry_safe(sequence:tuple[str,...],reg:dict[str,Any])->bool:
    present=set(sequence); pos={x:i for i,x in enumerate(sequence)}
    if any(set(pair).issubset(present) for pair in reg["no_good"]): return False
    return all(a not in pos or b not in pos or pos[a]<pos[b] for a,b in reg["precedence"])


def _direct_safe(sequence:tuple[str,...],model:dict[tuple[str,str],bool])->bool:
    return all(model[(sequence[i],sequence[j])] for i in range(len(sequence)) for j in range(i+1,len(sequence)))


def _repair(sequence:tuple[str,...],safe_fn)->tuple[tuple[str,...],int,int]:
    # Prefer reorder-only; if impossible because of a no-good pair, drop one update.
    checks=0
    for p in itertools.permutations(sequence):
        checks+=1
        if safe_fn(p): return tuple(p),0,checks
    for drop in range(len(sequence)):
        rest=sequence[:drop]+sequence[drop+1:]
        for p in itertools.permutations(rest):
            checks+=1
            if safe_fn(p): return tuple(p),1,checks
    return tuple(),len(sequence),checks


def _hidden_cases()->list[dict[str,Any]]:
    rows=[]; index=0
    # Held-out identities instantiate frozen types; triples were never present in pair training.
    triples=list(itertools.combinations(TYPES,3))
    for triple in triples:
        order=tuple(triple[(index+j)%3] for j in range(3)); identities=tuple(f"hidden-{t.replace(':','-')}-{index}-{j}" for j,t in enumerate(order))
        rows.append({"case_id":f"h{index:02d}","types":order,"identities":identities}); index+=1
    return rows


def run_a4_cpu_p0()->dict[str,Any]:
    table=_pair_table(); reg=_registry(table); model=_direct(table); hidden=_hidden_cases()
    rows=[]; pred_match=repair_match=0; reg_success=direct_success=0; reg_checks=direct_checks=0
    for case in hidden:
        seq=case["types"]; truth=_safe(seq); rp=_registry_safe(seq,reg); dp=_direct_safe(seq,model)
        rr,rd,rc=_repair(seq,lambda x:_registry_safe(x,reg)); dr,dd,dc=_repair(seq,lambda x:_direct_safe(x,model))
        r_ok=_safe(rr) and rd==min(1,rd); d_ok=_safe(dr) and dd==min(1,dd)
        pred_match+=int(rp==dp); repair_match+=int(rr==dr and rd==dd); reg_success+=int(r_ok); direct_success+=int(d_ok); reg_checks+=rc; direct_checks+=dc
        rows.append({"case_id":case["case_id"],"hidden_identities":list(case["identities"]),"types":list(seq),"truth_safe":truth,"registry_prediction":rp,"direct_prediction":dp,"registry_repair":list(rr),"direct_repair":list(dr),"registry_drop_count":rd,"direct_drop_count":dd,"registry_candidate_checks":rc,"direct_candidate_checks":dc})
    n=len(hidden); equivalent=(pred_match==repair_match==reg_success==direct_success==n and reg_checks==direct_checks)
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"compositional-update-compatibility","code":"A-4",
      "scientific_role":"CPU held-out-identity and held-out-triple composition P0 with independent programmatic execution truth",
      "design":{"typed_update_descriptors":len(TYPES),"pair_intervention_rows":len(table),"hidden_triples":n,"hidden_update_identities_disjoint":True,"triples_absent_from_training":True,"independent_truth":"programmatic ordered-composition verifier"},
      "registry":reg,"direct_ordered_pair_model":{"cells":len(model)},"rows":rows,
      "metrics":{"registry_prediction_accuracy":sum(r["registry_prediction"]==r["truth_safe"] for r in rows)/n,"direct_prediction_accuracy":sum(r["direct_prediction"]==r["truth_safe"] for r in rows)/n,"prediction_agreement":pred_match/n,"registry_repair_success":reg_success/n,"direct_repair_success":direct_success/n,"repair_exact_agreement":repair_match/n,"registry_candidate_checks":reg_checks,"direct_candidate_checks":direct_checks},
      "matched_simplification":{"baseline":"direct ordered-descriptor pair risk table + equal-budget local constrained repair search","same_pair_intervention_table":True,"same_descriptor_language":True,"same_hidden_cases":True,"same_candidate_check_budget":reg_checks==direct_checks,"equivalent":equivalent},
      "decision":"STOP_DIRECT_ORDER_AWARE_RISK_EQUIVALENT" if equivalent else "P0_SIGNAL_CONTINUE","standalone_claim_stop_authorized":equivalent,"p1_authorized":False,
      "next_action":"Merge A-4 into a direct ordered-composition risk/repair baseline; the typed registry adds no held-out prediction or repair value." if equivalent else "Validate the surviving registry advantage on a real composition table after human review."}


def write_a4_cpu_p0(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    state=run_a4_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_A4_COMPOSITION_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__=="__main__": print(json.dumps(write_a4_cpu_p0(),ensure_ascii=False,indent=2))
