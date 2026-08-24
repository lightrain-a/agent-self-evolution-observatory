from __future__ import annotations

import argparse
import collections
import csv
import json
from pathlib import Path
from typing import Any

from research_pipeline import temporal_skill_g0_analyze as stats
from research_pipeline import temporal_skill_g0_execute as core

PLAN = Path("generated/temporal-skill-temp-o5-kimi-plan-20260824.json")
RESULTS = core.REPLAY_ROOT / "20260824-temp-o5-kimi-alignment-t-vs-r" / "results.json"
OUTPUT = Path("generated/temporal-skill-temp-o5-kimi-analysis-20260824.json")
SUMMARY_CSV = core.REPLAY_ROOT / "20260824-temp-o5-kimi-alignment-t-vs-r" / "analysis-summary.csv"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(plan: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    expected = {(r["endpoint_id"], int(r["repeat_id"]), r["arm"]): r for r in plan["rows"]}
    observed: dict[tuple[str, int, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for r in results.get("rows") or []:
        observed[(r.get("endpoint_id"), int(r.get("repeat_id", -1)), r.get("arm"))].append(r)
    missing = [k for k in expected if k not in observed]
    extra = [k for k in observed if k not in expected]
    dup = [k for k, vals in observed.items() if len(vals) != 1]
    invalid = []
    for k, exp in expected.items():
        if k not in observed or len(observed[k]) != 1:
            continue
        r = observed[k][0]
        errs = []
        if not r.get("runtime_valid"): errs.append("runtime-invalid")
        if r.get("resolved_model") != exp["required_resolved_model"]: errs.append("model-drift")
        if r.get("condition_position") != exp["condition_position"]: errs.append("condition-position")
        if not isinstance(r.get("family_success"), bool): errs.append("family-success-type")
        if r.get("arm") == "R_RETRIEVAL":
            p = r.get("retrieval_parity") or {}
            if not (p.get("candidate_evidence_preserved") and p.get("operation_output_content_equal") and p.get("only_added_field")):
                errs.append("retrieval-parity")
        if errs:
            invalid.append({"key": list(k), "errors": errs})
    integrity = {"pass": not (missing or extra or dup or invalid), "planned": len(expected), "observed": len(results.get("rows") or []), "missing": len(missing), "extra": len(extra), "duplicates": len(dup), "invalid": invalid[:20]}
    base = {
        "schema_version": "1.0", "analysis_type": "TEMP-O5-KIMI-ALIGNMENT-SECONDARY", "paper_id": plan["paper_id"],
        "plan_body_sha256": plan["plan_body_sha256"], "result_payload_sha256": core.canonical_sha(results), "integrity": integrity,
        "primary_authority": False, "cannot_authorize_container_claim": True,
        "cannot_override_deepseek_primary_TEMP_O5_adjudication": True,
    }
    if not integrity["pass"]:
        return {**base, "status": "HOLD_INTEGRITY"}
    per: dict[str, dict[str, list[int]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in results["rows"]:
        per[r["endpoint_id"]][r["arm"]].append(int(r["family_success"]))
    means = {eid: {arm: sum(vals) / len(vals) for arm, vals in arms.items()} for eid, arms in per.items()}
    deltas = {eid: arms["T_CALLABLE"] - arms["R_RETRIEVAL"] for eid, arms in means.items()}
    labels = {eid: "KIMI_C4_RELEASE_ALIGNMENT" for eid in deltas}
    ci = stats.stratified_bootstrap_ci(deltas, labels, draws=20000, seed=20260824)
    summary = stats.summarize_deltas(deltas)
    threshold = float(plan["analysis_contract"]["material_threshold"])
    if ci[1] <= threshold:
        descriptive = "NO_MATERIAL_CONTAINER_ADVANTAGE_AT_SECONDARY_RESOLUTION"
    elif ci[0] > 0 and summary["mean"] >= threshold:
        descriptive = "DIRECTIONAL_T_OVER_R_LOW_RESOLUTION"
    elif ci[1] < 0:
        descriptive = "DIRECTIONAL_R_OVER_T_LOW_RESOLUTION"
    else:
        descriptive = "SECONDARY_INCONCLUSIVE"
    endpoint_rows = {eid: {"T_rate": means[eid]["T_CALLABLE"], "R_rate": means[eid]["R_RETRIEVAL"], "T_minus_R": deltas[eid]} for eid in sorted(deltas)}
    return {
        **base,
        "status": descriptive,
        "secondary": {
            "independent_endpoints": 3, "repeats_per_arm": 5, "T_minus_R_point": summary["mean"], "bootstrap_90_ci": ci,
            "wins": summary["wins"], "ties": summary["ties"], "losses": summary["losses"], "material_threshold": threshold,
            "endpoint_summaries": endpoint_rows,
        },
        "interpretation": "This is a low-resolution Kimi alignment robustness check only. It is reported descriptively and cannot create or erase the DeepSeek-primary TEMP-O5 conclusion.",
    }


def write_summary(result: dict[str, Any], path: Path) -> None:
    s = result.get("secondary") or {}
    rows = [{"scope": "global-secondary", "status": result["status"], "T_minus_R": s.get("T_minus_R_point"), "ci90_low": (s.get("bootstrap_90_ci") or [None, None])[0], "ci90_high": (s.get("bootstrap_90_ci") or [None, None])[1]}]
    for eid, e in (s.get("endpoint_summaries") or {}).items():
        rows.append({"scope": "endpoint", "endpoint_id": eid, **e})
    fields = sorted(set().union(*(r.keys() for r in rows)))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(rows); fh.flush()


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--results", type=Path, default=RESULTS); ap.add_argument("--output", type=Path, default=OUTPUT); args = ap.parse_args()
    result = analyze(read_json(PLAN), read_json(args.results))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(result, SUMMARY_CSV)
    print(json.dumps({"status": result["status"], "integrity": result["integrity"]["pass"], "output": str(args.output), "summary_csv": str(SUMMARY_CSV)}, indent=2))

if __name__ == "__main__":
    main()
