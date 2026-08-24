from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

DEFAULT_PLAN = Path("generated/temporal-skill-g0-fresh-factorial-plan-20260824.json")
DEFAULT_PREFLIGHT = Path("generated/temporal-skill-g0-reopen-preflight-20260824.json")
DEFAULT_OUTPUT = Path("generated/temporal-skill-g0-stage-a-analysis.json")

# These are the DeepSeek-primary positive cells currently carrying the paper story.
# They are frozen before Stage-A outcomes and are downgrade-only: Stage A cannot add
# a new universal claim by finding another positive cell.
LOAD_BEARING_CELLS = (
    ("C3-R", "exogenous_grounding"),
    ("C4-R", "exogenous_grounding"),
    ("C4-R4", "temporal_cutoff"),
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values: list[float], p: float) -> float:
    xs = sorted(values)
    idx = (len(xs) - 1) * p
    lo = int(idx)
    hi = min(lo + 1, len(xs) - 1)
    frac = idx - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def one_sided_sign_p(wins: int, losses: int, direction: str) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    if direction == "positive":
        k = wins
    elif direction == "negative":
        k = losses
    else:
        raise ValueError(direction)
    return sum(math.comb(n, j) for j in range(k, n + 1)) / (2**n)


def summarize_deltas(values: dict[str, float]) -> dict[str, Any]:
    xs = list(values.values())
    wins = sum(x > 0 for x in xs)
    ties = sum(x == 0 for x in xs)
    losses = sum(x < 0 for x in xs)
    mean = sum(xs) / len(xs) if xs else 0.0
    return {
        "n": len(xs),
        "mean": mean,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "one_sided_sign_p_positive": one_sided_sign_p(wins, losses, "positive"),
        "one_sided_sign_p_negative": one_sided_sign_p(wins, losses, "negative"),
    }


def stratified_bootstrap_ci(
    endpoint_delta: dict[str, float],
    endpoint_family: dict[str, str],
    *,
    draws: int,
    seed: int,
) -> list[float]:
    rng = random.Random(seed)
    by_family: dict[str, list[str]] = collections.defaultdict(list)
    for eid in sorted(endpoint_delta):
        by_family[endpoint_family[eid]].append(eid)
    samples: list[float] = []
    for _ in range(draws):
        chosen: list[float] = []
        for family in sorted(by_family):
            ids = by_family[family]
            chosen.extend(endpoint_delta[rng.choice(ids)] for _ in range(len(ids)))
        samples.append(sum(chosen) / len(chosen))
    return [percentile(samples, 0.05), percentile(samples, 0.95)]


def validate_results(plan: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    expected_hash = str(plan["plan_body_sha256"])
    supplied_hash = str(results.get("plan_body_sha256") or "")
    errors: list[str] = []
    if supplied_hash != expected_hash:
        errors.append(f"plan-hash-mismatch:{supplied_hash or 'missing'}")

    expected: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in plan["rows"]:
        key = (str(row["endpoint_id"]), int(row["repeat_id"]), str(row["arm"]))
        expected[key] = row

    observed: dict[tuple[str, int, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for row in results.get("rows") or []:
        key = (str(row.get("endpoint_id") or ""), int(row.get("repeat_id", -1)), str(row.get("arm") or ""))
        observed[key].append(row)

    missing = sorted(key for key in expected if key not in observed)
    extra = sorted(key for key in observed if key not in expected)
    duplicates = sorted(key for key, rows in observed.items() if len(rows) != 1)
    if missing:
        errors.append(f"missing-planned-units:{len(missing)}")
    if extra:
        errors.append(f"extra-unplanned-units:{len(extra)}")
    if duplicates:
        errors.append(f"duplicate-units:{len(duplicates)}")

    invalid_rows: list[dict[str, Any]] = []
    required_resolved = str(plan["model_identity"]["required_resolved_model"])
    for key in expected:
        if key not in observed or len(observed[key]) != 1:
            continue
        got = observed[key][0]
        exp = expected[key]
        row_errors: list[str] = []
        if not bool(got.get("runtime_valid")):
            row_errors.append("runtime_invalid")
        if str(got.get("resolved_model") or "") != required_resolved:
            row_errors.append("resolved_model_drift")
        if str(got.get("condition_id") or "") != str(exp["condition_id"]):
            row_errors.append("condition_id_mismatch")
        if int(got.get("condition_position", -1)) != int(exp["condition_position"]):
            row_errors.append("condition_position_mismatch")
        if str(got.get("failure_family") or "") != str(exp["failure_family"]):
            row_errors.append("family_mismatch")
        if not isinstance(got.get("family_success"), bool):
            row_errors.append("family_success_not_bool")
        if row_errors:
            invalid_rows.append({"key": list(key), "errors": row_errors})
    if invalid_rows:
        errors.append(f"invalid-planned-rows:{len(invalid_rows)}")

    return {
        "pass": not errors,
        "errors": errors,
        "planned_units": len(expected),
        "observed_rows": len(results.get("rows") or []),
        "missing_units": [list(x) for x in missing[:50]],
        "extra_units": [list(x) for x in extra[:50]],
        "duplicate_units": [list(x) for x in duplicates[:50]],
        "invalid_rows": invalid_rows[:50],
    }


def analyze(
    plan: dict[str, Any],
    preflight: dict[str, Any],
    results: dict[str, Any],
    *,
    bootstrap_draws: int | None = None,
) -> dict[str, Any]:
    integrity = validate_results(plan, results)
    frozen_code = preflight.get("frozen_execution_code") or {}
    expected_runner = str(frozen_code.get("runner_sha256") or "")
    expected_analyzer = str(frozen_code.get("analyzer_sha256") or "")
    current_analyzer = sha_file(Path(__file__))
    if str(results.get("runner_sha256") or "") != expected_runner:
        integrity["errors"].append("runner-hash-mismatch")
        integrity["pass"] = False
    if current_analyzer != expected_analyzer:
        integrity["errors"].append("analyzer-hash-mismatch")
        integrity["pass"] = False
    base = {
        "schema_version": "1.0",
        "analysis_type": "TEMP-O4-stage-a-deepseek-primary-g0-analysis",
        "paper_id": plan["paper_id"],
        "plan_body_sha256": plan["plan_body_sha256"],
        "preflight_receipt_body_sha256": preflight["receipt_body_sha256"],
        "result_payload_sha256": canonical_sha(results),
        "integrity": integrity,
        "load_bearing_cells_frozen_before_outcomes": [list(x) for x in LOAD_BEARING_CELLS],
    }
    if not integrity["pass"]:
        return {
            **base,
            "status": "HOLD_INCOMPLETE_OR_MODEL_DRIFT",
            "neutrality_go": False,
            "operation_specificity_evaluated": False,
            "claim_upgrade_authorized": False,
        }

    rows = results["rows"]
    per_endpoint_arm: dict[str, dict[str, list[bool]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    endpoint_family: dict[str, str] = {}
    endpoint_phase: dict[str, str] = {}
    for row in rows:
        eid = str(row["endpoint_id"])
        arm = str(row["arm"])
        per_endpoint_arm[eid][arm].append(bool(row["family_success"]))
        endpoint_family[eid] = str(row["failure_family"])
        endpoint_phase[eid] = str(row["phase"])

    means: dict[str, dict[str, float]] = {}
    for eid, arms in per_endpoint_arm.items():
        means[eid] = {}
        for arm in plan["summary"]["arms"]:
            values = arms[arm]
            if len(values) != int(plan["summary"]["repeats"]):
                raise RuntimeError(f"validated result has wrong repeat count for {eid}/{arm}")
            means[eid][arm] = sum(values) / len(values)

    g0_minus_n = {eid: x["G0_NOOP"] - x["N_FRESH"] for eid, x in means.items()}
    t_minus_g0 = {eid: x["T_FROZEN"] - x["G0_NOOP"] for eid, x in means.items()}
    t_minus_n = {eid: x["T_FROZEN"] - x["N_FRESH"] for eid, x in means.items()}

    neutrality = preflight["neutrality_contract"]
    margin = float(neutrality["equivalence_margin_absolute_risk_difference"][1])
    draws = int(bootstrap_draws or neutrality["bootstrap_draws"])
    seed = int(neutrality["bootstrap_seed"])
    ci90 = stratified_bootstrap_ci(g0_minus_n, endpoint_family, draws=draws, seed=seed)
    global_summary = summarize_deltas(g0_minus_n)

    family_summary: dict[str, Any] = {}
    family_guardrails: list[dict[str, Any]] = []
    for family in sorted(set(endpoint_family.values())):
        vals = {eid: g0_minus_n[eid] for eid in g0_minus_n if endpoint_family[eid] == family}
        s = summarize_deltas(vals)
        direction = "positive" if s["mean"] > 0 else "negative"
        p_dir = s["one_sided_sign_p_positive"] if direction == "positive" else s["one_sided_sign_p_negative"]
        trigger = abs(float(s["mean"])) >= 0.20 and p_dir <= 0.05
        family_summary[family] = {**s, "guardrail_trigger": trigger, "guardrail_direction": direction if trigger else None}
        if trigger:
            family_guardrails.append({"failure_family": family, "mean": s["mean"], "direction": direction, "one_sided_sign_p": p_dir})

    global_nonneutral = (
        abs(float(global_summary["mean"])) >= margin
        and (ci90[0] > 0.0 or ci90[1] < 0.0)
    )
    neutrality_go = ci90[0] > -margin and ci90[1] < margin and not family_guardrails
    if neutrality_go:
        status = "NEUTRALITY_GO"
    elif global_nonneutral or family_guardrails:
        status = "G0_NONNEUTRAL_STOP"
    else:
        status = "HOLD_NEUTRALITY_INCONCLUSIVE"

    result: dict[str, Any] = {
        **base,
        "status": status,
        "neutrality_go": neutrality_go,
        "neutrality": {
            "estimand": "G0_NOOP_minus_N_FRESH endpoint-repeat-mean risk difference",
            "point": global_summary["mean"],
            "bootstrap_90_ci": ci90,
            "bootstrap_draws": draws,
            "bootstrap_seed": seed,
            "equivalence_margin": [-margin, margin],
            "global_wins_ties_losses": {k: global_summary[k] for k in ("wins", "ties", "losses")},
            "global_nonneutral_trigger": global_nonneutral,
            "family_summaries": family_summary,
            "family_guardrails": family_guardrails,
        },
        "operation_specificity_evaluated": neutrality_go,
        "claim_upgrade_authorized": False,
    }

    if neutrality_go:
        cell_summaries: dict[str, Any] = {}
        frozen_load_bearing_downgrades: list[str] = []
        all_cells = sorted(set((endpoint_phase[eid], endpoint_family[eid]) for eid in means))
        for phase, family in all_cells:
            ids = [eid for eid in means if endpoint_phase[eid] == phase and endpoint_family[eid] == family]
            dg = {eid: t_minus_g0[eid] for eid in ids}
            dn = {eid: t_minus_n[eid] for eid in ids}
            sg = summarize_deltas(dg)
            sn = summarize_deltas(dn)
            binding_direction = float(sg["mean"]) > 0.0 and float(sn["mean"]) > 0.0
            key = f"{phase}|{family}"
            is_load_bearing = (phase, family) in LOAD_BEARING_CELLS
            if is_load_bearing and not binding_direction:
                frozen_load_bearing_downgrades.append(key)
            cell_summaries[key] = {
                "n_endpoints": len(ids),
                "T_minus_G0": sg,
                "T_minus_N": sn,
                "binding_direction": binding_direction,
                "pre_frozen_load_bearing_cell": is_load_bearing,
            }
        result["operation_specificity"] = {
            "global_T_minus_G0": summarize_deltas(t_minus_g0),
            "global_T_minus_N": summarize_deltas(t_minus_n),
            "cell_summaries": cell_summaries,
            "load_bearing_cell_downgrades": frozen_load_bearing_downgrades,
            "stage_a_primary_track_survives_directional_gate": not frozen_load_bearing_downgrades,
            "Kimi_support_layer_not_adjudicated": True,
            "TEMP_O5_not_adjudicated": True,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = analyze(read_json(args.plan), read_json(args.preflight), read_json(args.results))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "neutrality_go": result["neutrality_go"],
        "integrity_pass": result["integrity"]["pass"],
        "output": str(args.output),
        "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
