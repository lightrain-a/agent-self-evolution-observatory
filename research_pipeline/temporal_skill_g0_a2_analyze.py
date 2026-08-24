from __future__ import annotations

import argparse
import collections
import csv
import json
import math
from pathlib import Path
from typing import Any

from research_pipeline import temporal_skill_g0_analyze as stats
from research_pipeline import temporal_skill_g0_execute as core

PLAN = Path("generated/temporal-skill-g0-a2-neutrality-plan-20260824.json")
RESULTS = core.REPLAY_ROOT / "20260824-g0-a2-neutrality-deepseek" / "results.json"
OUTPUT = Path("generated/temporal-skill-g0-a2-neutrality-analysis-20260824.json")
SUMMARY_CSV = core.REPLAY_ROOT / "20260824-g0-a2-neutrality-deepseek" / "analysis-summary.csv"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sign_p(wins: int, losses: int, positive: bool) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    k = wins if positive else losses
    return sum(math.comb(n, j) for j in range(k, n + 1)) / (2 ** n)


def analyze(plan: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    expected = {(r["endpoint_id"], int(r["repeat_id"]), r["arm"]): r for r in plan["rows"]}
    observed: dict[tuple[str, int, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for r in results.get("rows") or []:
        observed[(r.get("endpoint_id"), int(r.get("repeat_id", -1)), r.get("arm"))].append(r)
    missing = [k for k in expected if k not in observed]
    extra = [k for k in observed if k not in expected]
    dup = [k for k, v in observed.items() if len(v) != 1]
    invalid = []
    for k, exp in expected.items():
        if k not in observed or len(observed[k]) != 1:
            continue
        r = observed[k][0]
        errs = []
        if not r.get("runtime_valid"): errs.append("runtime-invalid")
        if r.get("resolved_model") != exp["required_resolved_model"]: errs.append("model-drift")
        if r.get("condition_id") != exp["condition_id"]: errs.append("condition-id")
        if r.get("condition_position") != exp["condition_position"]: errs.append("condition-position")
        if not isinstance(r.get("family_success"), bool): errs.append("family-success-type")
        if errs: invalid.append({"key": list(k), "errors": errs})
    integrity = {"pass": not (missing or extra or dup or invalid), "planned": len(expected), "observed": len(results.get("rows") or []), "missing": len(missing), "extra": len(extra), "duplicates": len(dup), "invalid": invalid[:20]}
    base = {"schema_version":"1.0","analysis_type":"TEMP-O4-G0-A2-independent-neutrality","paper_id":plan["paper_id"],"plan_body_sha256":plan["plan_body_sha256"],"result_payload_sha256":core.canonical_sha(results),"integrity":integrity,"A1_A2_pooling_for_primary":False}
    if not integrity["pass"]:
        return {**base,"status":"HOLD_INTEGRITY","neutrality_go":False}
    per: dict[str, dict[str, list[int]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    family: dict[str, str] = {}
    for r in results["rows"]:
        eid=r["endpoint_id"]; per[eid][r["arm"]].append(int(r["family_success"])); family[eid]=r["failure_family"]
    deltas={eid: sum(arms["G0_NOOP"])/len(arms["G0_NOOP"]) - sum(arms["N_FRESH"])/len(arms["N_FRESH"]) for eid,arms in per.items()}
    ci=stats.stratified_bootstrap_ci(deltas,family,draws=20000,seed=20260825)
    global_s=stats.summarize_deltas(deltas)
    fam_s={}; guards=[]
    for fam in sorted(set(family.values())):
        vals={eid:d for eid,d in deltas.items() if family[eid]==fam}; s=stats.summarize_deltas(vals)
        positive=s["mean"]>0; p=sign_p(s["wins"],s["losses"],positive); trigger=abs(s["mean"])>=0.20 and p<=0.05
        fam_s[fam]={**s,"directional_sign_p":p,"guardrail_trigger":trigger}
        if trigger: guards.append({"failure_family":fam,"mean":s["mean"],"directional_sign_p":p})
    margin=0.10
    global_non=abs(global_s["mean"])>=margin and (ci[0]>0 or ci[1]<0)
    go=ci[0]>-margin and ci[1]<margin and not guards
    status="NEUTRALITY_GO" if go else ("G0_NONNEUTRAL_STOP" if global_non or guards else "HOLD_NEUTRALITY_INCONCLUSIVE")
    return {**base,"status":status,"neutrality_go":go,"neutrality":{"point":global_s["mean"],"bootstrap_90_ci":ci,"equivalence_margin":[-margin,margin],"wins":global_s["wins"],"ties":global_s["ties"],"losses":global_s["losses"],"global_nonneutral_trigger":global_non,"family_summaries":fam_s,"family_guardrails":guards,"repeats_per_arm":4,"independent_endpoints":35},"cross_stage_operation_specificity_authorized":go}


def write_summary(result: dict[str, Any], path: Path) -> None:
    rows=[{"scope":"global","failure_family":"ALL","status":result["status"],"neutrality_go":result["neutrality_go"],"mean_G0_minus_N":result.get("neutrality",{}).get("point"),"ci90_low":(result.get("neutrality",{}).get("bootstrap_90_ci") or [None,None])[0],"ci90_high":(result.get("neutrality",{}).get("bootstrap_90_ci") or [None,None])[1]}]
    for fam,s in (result.get("neutrality",{}).get("family_summaries") or {}).items(): rows.append({"scope":"family","failure_family":fam,"n":s["n"],"mean_G0_minus_N":s["mean"],"wins":s["wins"],"ties":s["ties"],"losses":s["losses"],"guardrail_trigger":s["guardrail_trigger"]})
    fields=sorted(set().union(*(r.keys() for r in rows))); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows); f.flush()


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--results",type=Path,default=RESULTS); ap.add_argument("--output",type=Path,default=OUTPUT); args=ap.parse_args()
    result=analyze(read_json(PLAN),read_json(args.results)); args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"); write_summary(result,SUMMARY_CSV)
    print(json.dumps({"status":result["status"],"neutrality_go":result["neutrality_go"],"integrity":result["integrity"]["pass"],"output":str(args.output),"summary_csv":str(SUMMARY_CSV)},indent=2))

if __name__ == "__main__": main()
