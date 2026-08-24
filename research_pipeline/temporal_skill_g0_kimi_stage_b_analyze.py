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

PLAN = Path("generated/temporal-skill-g0-kimi-stage-b-plan-20260824.json")
RESULTS = core.REPLAY_ROOT / "20260824-g0-kimi-stage-b" / "results.json"
OUTPUT = Path("generated/temporal-skill-g0-kimi-stage-b-analysis-20260824.json")
SUMMARY_CSV = core.REPLAY_ROOT / "20260824-g0-kimi-stage-b" / "analysis-summary.csv"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def one_sided_sign_p(wins: int, losses: int, positive: bool = True) -> float:
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
        r = observed[k][0]; errs = []
        if not r.get("runtime_valid"): errs.append("runtime-invalid")
        if r.get("resolved_model") != exp["required_resolved_model"]: errs.append("model-drift")
        if r.get("condition_id") != exp["condition_id"]: errs.append("condition-id")
        if r.get("condition_position") != exp["condition_position"]: errs.append("condition-position")
        if not isinstance(r.get("family_success"), bool): errs.append("family-success-type")
        if errs: invalid.append({"key": list(k), "errors": errs})
    integrity = {"pass": not (missing or extra or dup or invalid), "planned": len(expected), "observed": len(results.get("rows") or []), "missing": len(missing), "extra": len(extra), "duplicates": len(dup), "invalid": invalid[:20]}
    base = {"schema_version":"1.0","analysis_type":"TEMP-O4-G0-KIMI-STAGE-B","paper_id":plan["paper_id"],"plan_body_sha256":plan["plan_body_sha256"],"result_payload_sha256":core.canonical_sha(results),"integrity":integrity,"new_positive_target_promotion_forbidden":True}
    if not integrity["pass"]:
        return {**base,"status":"HOLD_INTEGRITY","neutrality_go":False,"operation_specificity_evaluated":False}
    per: dict[str, dict[str, list[int]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    family: dict[str, str] = {}; phase: dict[str, str] = {}
    for r in results["rows"]:
        eid=r["endpoint_id"]; per[eid][r["arm"]].append(int(r["family_success"])); family[eid]=r["failure_family"]; phase[eid]=r["phase"]
    means={eid:{arm:sum(v)/len(v) for arm,v in arms.items()} for eid,arms in per.items()}
    neutral_deltas={eid:arms["G0_NOOP"]-arms["N_FRESH"] for eid,arms in means.items()}
    ci=stats.stratified_bootstrap_ci(neutral_deltas,family,draws=20000,seed=20260824)
    g=stats.summarize_deltas(neutral_deltas); margin=0.10
    fam_s={}; guards=[]
    for fam in sorted(set(family.values())):
        vals={eid:d for eid,d in neutral_deltas.items() if family[eid]==fam}; s=stats.summarize_deltas(vals); positive=s["mean"]>0; p=one_sided_sign_p(s["wins"],s["losses"],positive)
        trigger=abs(s["mean"])>=0.20 and p<=0.05; fam_s[fam]={**s,"directional_sign_p":p,"guardrail_trigger":trigger}
        if trigger: guards.append({"failure_family":fam,"mean":s["mean"],"directional_sign_p":p})
    global_non=abs(g["mean"])>=margin and (ci[0]>0 or ci[1]<0)
    neutrality_go=ci[0]>-margin and ci[1]<margin and not guards
    neutral_status="NEUTRALITY_GO" if neutrality_go else ("G0_NONNEUTRAL_STOP" if global_non or guards else "HOLD_NEUTRALITY_INCONCLUSIVE")
    neutrality={"status":neutral_status,"point":g["mean"],"bootstrap_90_ci":ci,"equivalence_margin":[-margin,margin],"wins":g["wins"],"ties":g["ties"],"losses":g["losses"],"family_summaries":fam_s,"family_guardrails":guards,"global_nonneutral_trigger":global_non,"endpoints":23,"repeats_per_arm":2}
    if not neutrality_go:
        return {**base,"status":neutral_status,"neutrality_go":False,"neutrality":neutrality,"operation_specificity_evaluated":False}
    target_summaries={}; downgrades=[]
    for target, ids in plan["load_bearing_targets"].items():
        tg={eid:means[eid]["T_FROZEN"]-means[eid]["G0_NOOP"] for eid in ids}
        tn={eid:means[eid]["T_FROZEN"]-means[eid]["N_FRESH"] for eid in ids}
        sg=stats.summarize_deltas(tg); sn=stats.summarize_deltas(tn)
        survive=sg["mean"]>0 and sn["mean"]>0
        if not survive: downgrades.append(target)
        target_summaries[target]={"endpoint_ids":ids,"n_endpoints":len(ids),"T_minus_G0":{**sg,"one_sided_positive_sign_p":one_sided_sign_p(sg["wins"],sg["losses"],True)},"T_minus_N":{**sn,"one_sided_positive_sign_p":one_sided_sign_p(sn["wins"],sn["losses"],True)},"survives_directional_gate":survive}
    status="KIMI_SUPPORT_LAYER_SURVIVES" if not downgrades else "KIMI_SUPPORT_LAYER_DOWNGRADE"
    return {**base,"status":status,"neutrality_go":True,"neutrality":neutrality,"operation_specificity_evaluated":True,"operation_specificity":{"load_bearing_targets":target_summaries,"downgrades":downgrades,"all_pre_frozen_targets_survive":not downgrades}}


def write_summary(result: dict[str, Any], path: Path) -> None:
    rows=[{"scope":"neutrality-global","target":"ALL","status":result["status"],"neutrality_go":result.get("neutrality_go"),"mean":result.get("neutrality",{}).get("point"),"ci90_low":(result.get("neutrality",{}).get("bootstrap_90_ci") or [None,None])[0],"ci90_high":(result.get("neutrality",{}).get("bootstrap_90_ci") or [None,None])[1]}]
    for fam,s in (result.get("neutrality",{}).get("family_summaries") or {}).items(): rows.append({"scope":"neutrality-family","target":fam,"n":s["n"],"mean":s["mean"],"wins":s["wins"],"ties":s["ties"],"losses":s["losses"],"guardrail":s["guardrail_trigger"]})
    for target,s in (result.get("operation_specificity",{}).get("load_bearing_targets") or {}).items(): rows.append({"scope":"load-bearing-target","target":target,"n":s["n_endpoints"],"T_minus_G0":s["T_minus_G0"]["mean"],"T_minus_N":s["T_minus_N"]["mean"],"survives":s["survives_directional_gate"]})
    fields=sorted(set().union(*(r.keys() for r in rows))); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows); f.flush()


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--results",type=Path,default=RESULTS); ap.add_argument("--output",type=Path,default=OUTPUT); args=ap.parse_args()
    result=analyze(read_json(PLAN),read_json(args.results)); args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"); write_summary(result,SUMMARY_CSV)
    print(json.dumps({"status":result["status"],"neutrality_go":result.get("neutrality_go"),"integrity":result["integrity"]["pass"],"operation_specificity_evaluated":result.get("operation_specificity_evaluated"),"output":str(args.output),"summary_csv":str(SUMMARY_CSV)},indent=2))

if __name__ == "__main__":
    main()
