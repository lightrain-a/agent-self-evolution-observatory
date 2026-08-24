from __future__ import annotations

import collections
import csv
import json
from pathlib import Path
from typing import Any

from research_pipeline import temporal_skill_g0_analyze as a1stats
from research_pipeline import temporal_skill_g0_execute as core

A1_PLAN = Path("generated/temporal-skill-g0-fresh-factorial-plan-20260824.json")
A1_PREFLIGHT = Path("generated/temporal-skill-g0-reopen-preflight-20260824.json")
A1_RESULTS = core.REPLAY_ROOT / "20260824-g0-stage-a-deepseek-plan-r2" / "results.json"
A2_ANALYSIS = Path("generated/temporal-skill-g0-a2-neutrality-analysis-20260824.json")
OUTPUT = Path("generated/temporal-skill-g0-crossstage-adjudication-20260824.json")
SUMMARY_CSV = core.REPLAY_ROOT / "20260824-g0-stage-a-deepseek-plan-r2" / "operation-specificity-after-a2.csv"


def read_json(path: Path) -> Any: return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    plan=read_json(A1_PLAN); pre=read_json(A1_PREFLIGHT); results=read_json(A1_RESULTS); a2=read_json(A2_ANALYSIS)
    integrity=a1stats.validate_results(plan,results)
    base={"schema_version":"1.0","adjudication_type":"TEMP-O4-independent-neutrality-then-A1-operation-specificity","paper_id":plan["paper_id"],"A1_plan_sha256":plan["plan_body_sha256"],"A2_analysis_status":a2["status"],"A2_neutrality_go":a2["neutrality_go"],"A1_integrity":integrity,"claim_upgrade_authorized":False,"new_positive_cells_authorized":False,"load_bearing_cells_frozen_before_A2":[list(x) for x in a1stats.LOAD_BEARING_CELLS]}
    if not integrity["pass"] or not a2["neutrality_go"]:
        result={**base,"status":"HOLD_NO_OPERATION_SPECIFICITY_AUTHORITY","operation_specificity_evaluated":False}
    else:
        per=collections.defaultdict(lambda:collections.defaultdict(list)); fam={}; phase={}
        for r in results["rows"]:
            eid=r["endpoint_id"]; per[eid][r["arm"]].append(bool(r["family_success"])); fam[eid]=r["failure_family"]; phase[eid]=r["phase"]
        means={eid:{arm:sum(v)/len(v) for arm,v in arms.items()} for eid,arms in per.items()}
        cells={}; downgrades=[]
        for ph,fa in sorted(set(zip(phase.values(),fam.values()))):
            ids=[eid for eid in means if phase[eid]==ph and fam[eid]==fa]
            dg={eid:means[eid]["T_FROZEN"]-means[eid]["G0_NOOP"] for eid in ids}; dn={eid:means[eid]["T_FROZEN"]-means[eid]["N_FRESH"] for eid in ids}
            sg=a1stats.summarize_deltas(dg); sn=a1stats.summarize_deltas(dn); binding=sg["mean"]>0 and sn["mean"]>0; load=(ph,fa) in a1stats.LOAD_BEARING_CELLS; key=f"{ph}|{fa}"
            if load and not binding: downgrades.append(key)
            cells[key]={"n_endpoints":len(ids),"T_minus_G0":sg,"T_minus_N":sn,"binding_direction":binding,"pre_frozen_load_bearing_cell":load}
        result={**base,"status":"STAGE_A_PRIMARY_TRACK_SURVIVES_DIRECTIONAL_GATE" if not downgrades else "DOWNGRADE_LOAD_BEARING_CELLS","operation_specificity_evaluated":True,"operation_specificity":{"cell_summaries":cells,"load_bearing_cell_downgrades":downgrades,"stage_a_primary_track_survives_directional_gate":not downgrades,"Kimi_support_layer_not_adjudicated":True,"TEMP_O5_not_adjudicated":True}}
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    rows=[]
    for key,s in (result.get("operation_specificity",{}).get("cell_summaries") or {}).items():
        rows.append({"cell":key,"n_endpoints":s["n_endpoints"],"T_minus_G0_mean":s["T_minus_G0"]["mean"],"T_minus_N_mean":s["T_minus_N"]["mean"],"binding_direction":s["binding_direction"],"load_bearing":s["pre_frozen_load_bearing_cell"]})
    if rows:
        with SUMMARY_CSV.open("w",encoding="utf-8",newline="") as f: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows); f.flush()
    print(json.dumps({"status":result["status"],"operation_specificity_evaluated":result.get("operation_specificity_evaluated"),"output":str(OUTPUT),"summary_csv":str(SUMMARY_CSV) if rows else ""},indent=2))

if __name__ == "__main__": main()
