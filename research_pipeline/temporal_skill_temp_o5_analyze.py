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

PLAN = Path("generated/temporal-skill-temp-o5-deepseek-plan-20260824.json")
RESULTS = core.REPLAY_ROOT / "20260824-temp-o5-deepseek-t-vs-r" / "results.json"
OUTPUT = Path("generated/temporal-skill-temp-o5-deepseek-analysis-20260824.json")
SUMMARY_CSV = core.REPLAY_ROOT / "20260824-temp-o5-deepseek-t-vs-r" / "analysis-summary.csv"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def one_sided_positive_sign_p(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    return sum(math.comb(n, j) for j in range(wins, n + 1)) / (2 ** n)


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
        errors = []
        if not r.get("runtime_valid"): errors.append("runtime-invalid")
        if r.get("resolved_model") != exp["required_resolved_model"]: errors.append("model-drift")
        if r.get("condition_position") != exp["condition_position"]: errors.append("condition-position")
        if not isinstance(r.get("family_success"), bool): errors.append("family-success-type")
        if r.get("arm") == "R_RETRIEVAL":
            parity = r.get("retrieval_parity") or {}
            if not (parity.get("candidate_evidence_preserved") and parity.get("operation_output_content_equal") and parity.get("only_added_field")):
                errors.append("retrieval-parity")
        if errors:
            invalid.append({"key": list(k), "errors": errors})
    integrity = {
        "pass": not (missing or extra or dup or invalid), "planned": len(expected), "observed": len(results.get("rows") or []),
        "missing": len(missing), "extra": len(extra), "duplicates": len(dup), "invalid": invalid[:20],
    }
    base = {
        "schema_version": "1.0", "analysis_type": "TEMP-O5-DEEPSEEK-T-VS-R", "paper_id": plan["paper_id"],
        "plan_body_sha256": plan["plan_body_sha256"], "result_payload_sha256": core.canonical_sha(results),
        "integrity": integrity, "claim_expansion_default": False,
    }
    if not integrity["pass"]:
        return {**base, "status": "HOLD_INTEGRITY", "container_residual_survives": False}

    per: dict[str, dict[str, list[int]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    cell: dict[str, str] = {}
    for r in results["rows"]:
        eid = r["endpoint_id"]
        per[eid][r["arm"]].append(int(r["family_success"]))
        cell[eid] = f"{r['phase']}|{r['failure_family']}"
    means = {eid: {arm: sum(vals) / len(vals) for arm, vals in arms.items()} for eid, arms in per.items()}
    deltas = {eid: arms["T_CALLABLE"] - arms["R_RETRIEVAL"] for eid, arms in means.items()}
    ci = stats.stratified_bootstrap_ci(deltas, cell, draws=20000, seed=20260824)
    global_summary = stats.summarize_deltas(deltas)
    sign_p = one_sided_positive_sign_p(global_summary["wins"], global_summary["losses"])

    cell_summaries = {}
    cell_guardrails = []
    for label in sorted(set(cell.values())):
        vals = {eid: d for eid, d in deltas.items() if cell[eid] == label}
        summary = stats.summarize_deltas(vals)
        p = one_sided_positive_sign_p(summary["wins"], summary["losses"])
        guard = summary["mean"] >= 0.25 and p <= 0.05
        cell_summaries[label] = {**summary, "one_sided_positive_sign_p": p, "positive_container_guardrail": guard}
        if guard:
            cell_guardrails.append({"cell": label, "mean": summary["mean"], "one_sided_positive_sign_p": p})

    threshold = float(plan["decision_contract"]["material_container_advantage_threshold"])
    container_residual = global_summary["mean"] >= threshold and ci[0] > 0 and sign_p <= 0.05
    r_outperforms = ci[1] < 0
    no_material_advantage = ci[1] <= threshold and not cell_guardrails and not container_residual
    if container_residual:
        status = "CONTAINER_RESIDUAL_SURVIVES"
    elif r_outperforms:
        status = "R_OUTPERFORMS_T"
    elif no_material_advantage:
        status = "NO_MATERIAL_CONTAINER_ADVANTAGE"
    else:
        status = "HOLD_CONTAINER_VALUE_INCONCLUSIVE"

    return {
        **base,
        "status": status,
        "container_residual_survives": container_residual,
        "no_material_container_advantage": no_material_advantage,
        "R_outperforms_T": r_outperforms,
        "primary": {
            "independent_endpoints": len(deltas), "repeats_per_arm": 2,
            "T_minus_R_point": global_summary["mean"], "bootstrap_90_ci": ci,
            "wins": global_summary["wins"], "ties": global_summary["ties"], "losses": global_summary["losses"],
            "one_sided_positive_sign_p": sign_p, "material_advantage_threshold": threshold,
            "cell_summaries": cell_summaries, "positive_cell_guardrails": cell_guardrails,
        },
        "interpretation": {
            "CONTAINER_RESIDUAL_SURVIVES": "Callable skill state retains a prospectively resolved material residual over same-information retrieval/context materialization in the tested DeepSeek primary regime.",
            "R_OUTPERFORMS_T": "The retrieval/context surface outperforms callable skill state; callable-container superiority is refuted in the tested regime.",
            "NO_MATERIAL_CONTAINER_ADVANTAGE": "The experiment rules out a >10pp callable-container advantage at the frozen 90% resolution, with no load-bearing cell-specific positive residual guardrail. The supported story remains operation value, not container superiority.",
            "HOLD_CONTAINER_VALUE_INCONCLUSIVE": "The frozen experiment cannot resolve a material container residual; do not claim container superiority or equivalence.",
        }[status],
        "claim_policy": {
            "new_container_value_claim_authorized": bool(container_residual),
            "operation_level_claim_remains_valid_if_no_container_advantage": True,
            "retrieval_side_baseline_must_be_reported": True,
        },
    }


def write_summary(result: dict[str, Any], path: Path) -> None:
    rows = [{
        "scope": "global", "status": result["status"],
        "T_minus_R": (result.get("primary") or {}).get("T_minus_R_point"),
        "ci90_low": ((result.get("primary") or {}).get("bootstrap_90_ci") or [None, None])[0],
        "ci90_high": ((result.get("primary") or {}).get("bootstrap_90_ci") or [None, None])[1],
        "wins": (result.get("primary") or {}).get("wins"), "ties": (result.get("primary") or {}).get("ties"),
        "losses": (result.get("primary") or {}).get("losses"),
    }]
    for label, s in ((result.get("primary") or {}).get("cell_summaries") or {}).items():
        rows.append({"scope": "cell", "cell": label, "T_minus_R": s["mean"], "wins": s["wins"], "ties": s["ties"], "losses": s["losses"], "guardrail": s["positive_container_guardrail"]})
    fields = sorted(set().union(*(row.keys() for row in rows)))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(rows); fh.flush()


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--results", type=Path, default=RESULTS); ap.add_argument("--output", type=Path, default=OUTPUT); args = ap.parse_args()
    result = analyze(read_json(PLAN), read_json(args.results))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(result, SUMMARY_CSV)
    print(json.dumps({"status": result["status"], "integrity": result["integrity"]["pass"], "container_residual_survives": result.get("container_residual_survives"), "output": str(args.output), "summary_csv": str(SUMMARY_CSV)}, indent=2))

if __name__ == "__main__":
    main()
