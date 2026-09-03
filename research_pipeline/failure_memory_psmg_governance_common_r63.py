#!/usr/bin/env python3
"""Deterministic controller math for B1 R63--R65 hidden-governance PSMG.

No benchmark environment is touched by this module.  It defines the frozen
feature schema, ridge/shrinkage controller, policy rules, and complete-only
paired policy analysis used by the prospective governance experiment.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from typing import Any, Iterable

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"

CALIBRATION_IDS = [
    "377","492","316","63","373","57","331","44","185","454","116","357",
    "142","285","338","234","36","474","301","329","112","302","496","274",
]
TEST_IDS = [
    "101","486","412","219","108","216","114","13","494","232","287","189",
    "12","424","490","321","52","409","433","308","343","445","295","444",
    "111","87","298","346","137","359","148","376",
]
RESERVE_IDS = ["33","447","126","464","390","166","255","51","23","299"]
CALIBRATION_IDS_SHA256 = "a4d698d187c5dc82ceeb55086acc7924e24182da70bbf080347b9c16cca1eeb6"
TEST_IDS_SHA256 = "c843abf1823a74eb212370c2af84692e6150d39daf55c7f090461b54ef1e4308"
RESERVE_IDS_SHA256 = "b89602283841c2c9f4f55a423a412046ffce8f560b6f398926794375b0819e24"
REMAINING66_SHA256 = "7c2b84aee347faba6d369abb403eb3a25afb164b8f5c6800ba867c25d1017187"

Z_FEATURE_NAMES = [
    "selected_count",
    "similarity_mean","similarity_max","similarity_min","similarity_std","similarity_top_gap",
    "q_estimate_mean","q_estimate_max","q_estimate_min","q_estimate_std","q_estimate_top_gap",
    "score_mean","score_max","score_min","score_std","score_top_gap",
    "content_chars_mean","content_chars_std","content_lines_mean","content_lines_std",
    "marker_task_reflection_fraction","marker_script_fraction","marker_failed_approach_fraction",
    "marker_what_went_wrong_fraction","marker_trajectory_fraction",
    "skill_count","cluster_member_count","task_instruction_chars",
]
P_FEATURE_NAMES = [
    "success_fraction",
    "similarity_weighted_success_fraction",
    "q_weighted_success_fraction",
    "score_weighted_success_fraction",
    "rank_weighted_success_fraction",
]
RESIDUAL_MODERATOR_Z_NAMES = [
    "similarity_mean",
    "q_estimate_mean",
    "score_mean",
    "marker_task_reflection_fraction",
    "skill_count",
]
MARKERS = [
    ("marker_task_reflection_fraction", "task reflection:"),
    ("marker_script_fraction", "script:"),
    ("marker_failed_approach_fraction", "failed approach:"),
    ("marker_what_went_wrong_fraction", "what went wrong:"),
    ("marker_trajectory_fraction", "trajectory:"),
]

G0_RIDGE_LAMBDA = 1.0
RESIDUAL_RIDGE_LAMBDA = 10.0
DECISION_THRESHOLD = 0.0
SHUFFLE_SEED_STRING = "B1-R65-PSMG-SHUFFLE-20260903"
BOOTSTRAP_SEED = 20260903
BOOTSTRAP_REPETITIONS = 100000
EFFECT_RELEVANCE_FLOOR_ABS = 0.15
CALIBRATION_MIN_BENEFICIAL = 2
CALIBRATION_MIN_HARMFUL = 2


def digest(v: Any) -> str:
    return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",",":"), default=str).encode()).hexdigest()


def ids_hash(ids: Iterable[str]) -> str:
    return hashlib.sha256("\n".join(str(x) for x in ids).encode()).hexdigest()


def _eligible_selected(row: dict[str, Any]) -> list[dict[str, Any]]:
    selected = [x for x in (row.get("selected") or []) if x.get("eligible") is True]
    selected.sort(key=lambda x: int(x.get("rank") or 0))
    if not selected:
        raise ValueError(f"no-eligible-selected:{row.get('representative_id')}")
    for x in selected:
        if type(x.get("source_outcome_success")) is not bool:
            raise ValueError("invalid-provenance")
        if not isinstance(x.get("content"), str) or not x.get("content"):
            raise ValueError("invalid-content")
    return selected


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _pstdev(values: list[float]) -> float:
    if not values:
        return 0.0
    m = _mean(values)
    return float(math.sqrt(sum((float(x) - m) ** 2 for x in values) / len(values)))


def _stats(values: list[float]) -> list[float]:
    vals = [float(x) for x in values]
    top_gap = float(vals[0] - vals[1]) if len(vals) > 1 else 0.0
    return [_mean(vals), max(vals), min(vals), _pstdev(vals), top_gap]


def _weighted_success(selected: list[dict[str, Any]], weights: list[float]) -> float:
    den = float(sum(weights))
    base = float(sum(bool(x["source_outcome_success"]) for x in selected) / len(selected))
    if abs(den) < 1e-12:
        return base
    return float(sum(w * float(bool(x["source_outcome_success"])) for w, x in zip(weights, selected)) / den)


def extract_features(row: dict[str, Any]) -> tuple[list[float], list[float]]:
    """Return (Z, P) using only frozen pre-target-outcome information.

    Z deliberately contains retrieval scores and structural content summaries available
    to the strongest same-information provenance-free governor.  P contains only the
    authentic source-outcome receipt aggregated over the same frozen selected memories.
    """
    selected = _eligible_selected(row)
    z: list[float] = [float(len(selected))]
    for key in ("similarity", "q_estimate", "score"):
        z.extend(_stats([float(x.get(key) or 0.0) for x in selected]))
    chars = [float(len(str(x["content"]))) for x in selected]
    lines = [float(len(str(x["content"]).splitlines())) for x in selected]
    z.extend([_mean(chars), _pstdev(chars), _mean(lines), _pstdev(lines)])
    lower = [str(x["content"]).lower() for x in selected]
    for _, marker in MARKERS:
        z.append(float(sum(marker in text for text in lower) / len(lower)))
    z.extend([
        float(len(row.get("signature") or [])),
        float(row.get("member_count") or 0),
        float(len(str(row.get("task_instruction") or ""))),
    ])
    if len(z) != len(Z_FEATURE_NAMES):
        raise AssertionError((len(z), len(Z_FEATURE_NAMES)))

    success_fraction = float(sum(bool(x["source_outcome_success"]) for x in selected) / len(selected))
    p = [
        success_fraction,
        _weighted_success(selected, [float(x.get("similarity") or 0.0) for x in selected]),
        _weighted_success(selected, [float(x.get("q_estimate") or 0.0) for x in selected]),
        _weighted_success(selected, [float(x.get("score") or 0.0) for x in selected]),
        _weighted_success(selected, [1.0 / (i + 1.0) for i in range(len(selected))]),
    ]
    return z, p


def feature_record(row: dict[str, Any]) -> dict[str, Any]:
    z, p = extract_features(row)
    return {
        "task_id": str(row.get("representative_id")),
        "Z": {k: float(v) for k, v in zip(Z_FEATURE_NAMES, z)},
        "P": {k: float(v) for k, v in zip(P_FEATURE_NAMES, p)},
        "Z_sha256": digest({k: float(v) for k, v in zip(Z_FEATURE_NAMES, z)}),
        "P_sha256": digest({k: float(v) for k, v in zip(P_FEATURE_NAMES, p)}),
    }


def _standardizer(x: list[list[float]]) -> tuple[list[float], list[float]]:
    if not x or not x[0]:
        raise ValueError("empty-design")
    cols = list(zip(*x))
    mean = [_mean([float(v) for v in col]) for col in cols]
    std = [_pstdev([float(v) for v in col]) for col in cols]
    std = [s if s > 1e-12 else 1.0 for s in std]
    return mean, std


def _standardize_row(row: list[float], mean: list[float], std: list[float]) -> list[float]:
    return [(float(v) - float(m)) / float(s) for v, m, s in zip(row, mean, std)]


def _solve_linear(a: list[list[float]], b: list[float]) -> list[float]:
    """Deterministic partial-pivot Gaussian elimination for small ridge systems."""
    n = len(b)
    m = [[float(a[i][j]) for j in range(n)] + [float(b[i])] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: (abs(m[r][col]), -r))
        if abs(m[pivot][col]) < 1e-12:
            raise ValueError(f"singular-ridge-system:{col}")
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
        pv = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            if factor == 0.0:
                continue
            for j in range(col, n + 1):
                m[r][j] -= factor * m[col][j]
    return [float(m[i][n]) for i in range(n)]


def _ridge(x: list[list[float]], y: list[float], lam: float, intercept: bool) -> list[float]:
    design = ([1.0] + list(row) for row in x) if intercept else (list(row) for row in x)
    xx = list(design)
    width = len(xx[0])
    a = [[0.0] * width for _ in range(width)]
    b = [0.0] * width
    for row, target in zip(xx, y):
        for i in range(width):
            b[i] += row[i] * float(target)
            for j in range(width):
                a[i][j] += row[i] * row[j]
    for i in range(width):
        if not (intercept and i == 0):
            a[i][i] += float(lam)
    return _solve_linear(a, b)


def _ridge_with_unpenalized_intercept(x: list[list[float]], y: list[float], lam: float) -> list[float]:
    return _ridge(x, y, lam, intercept=True)


def _ridge_no_intercept(x: list[list[float]], y: list[float], lam: float) -> list[float]:
    return _ridge(x, y, lam, intercept=False)


def residual_feature_names() -> list[str]:
    out = [f"P:{p}" for p in P_FEATURE_NAMES]
    for p in P_FEATURE_NAMES:
        for z in RESIDUAL_MODERATOR_Z_NAMES:
            out.append(f"P:{p}*Z:{z}")
    return out


def _residual_design(p_std: list[list[float]], z_std: list[list[float]]) -> list[list[float]]:
    mod_idx = [Z_FEATURE_NAMES.index(x) for x in RESIDUAL_MODERATOR_Z_NAMES]
    out: list[list[float]] = []
    for p_row, z_row in zip(p_std, z_std):
        mods = [z_row[i] for i in mod_idx]
        row = list(p_row)
        for pv in p_row:
            row.extend(float(pv) * float(mv) for mv in mods)
        if len(row) != len(residual_feature_names()):
            raise AssertionError((len(row), len(residual_feature_names())))
        out.append(row)
    return out


def fit_controller(calibration_feature_rows: list[dict[str, Any]], utility_by_task: dict[str, float]) -> dict[str, Any]:
    if [str(x["task_id"]) for x in calibration_feature_rows] != CALIBRATION_IDS:
        raise ValueError("calibration-order-drift")
    if set(utility_by_task) != set(CALIBRATION_IDS):
        raise ValueError("calibration-utility-support-drift")
    z = [[float(r["Z"][k]) for k in Z_FEATURE_NAMES] for r in calibration_feature_rows]
    p = [[float(r["P"][k]) for k in P_FEATURE_NAMES] for r in calibration_feature_rows]
    y = [float(utility_by_task[t]) for t in CALIBRATION_IDS]
    if any(v not in {-1.0, 0.0, 1.0} for v in y):
        raise ValueError("calibration-utility-not-binary-difference")
    beneficial = sum(v > 0 for v in y); harmful = sum(v < 0 for v in y)
    route_support_pass = beneficial >= CALIBRATION_MIN_BENEFICIAL and harmful >= CALIBRATION_MIN_HARMFUL

    z_mean, z_std = _standardizer(z); z_s = [_standardize_row(row, z_mean, z_std) for row in z]
    g0_coef = _ridge_with_unpenalized_intercept(z_s, y, G0_RIDGE_LAMBDA)
    g0_pred = [float(g0_coef[0] + sum(a*b for a,b in zip(row, g0_coef[1:]))) for row in z_s]
    residual_target = [float(target - pred) for target, pred in zip(y, g0_pred)]
    p_mean, p_std = _standardizer(p); p_s = [_standardize_row(row, p_mean, p_std) for row in p]
    r_design = _residual_design(p_s, z_s)
    r_coef = _ridge_no_intercept(r_design, residual_target, RESIDUAL_RIDGE_LAMBDA)
    residual_pred = [float(sum(a*b for a,b in zip(row, r_coef))) for row in r_design]

    model = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "role": "R64_PSMG_CALIBRATED_CONTROLLER",
        "algorithm": {
            "g0": "standardized Z ridge with unpenalized intercept",
            "g0_lambda": G0_RIDGE_LAMBDA,
            "residual": "standardized P main effects plus P-by-frozen-Z-moderator interactions, no intercept ridge",
            "residual_lambda": RESIDUAL_RIDGE_LAMBDA,
            "decision_rule": "M_content_only iff score > 0; ties and nonpositive scores choose N_no_memory",
            "raw_provenance_executor_visible": False,
        },
        "feature_schema": {
            "Z_feature_names": Z_FEATURE_NAMES,
            "P_feature_names": P_FEATURE_NAMES,
            "residual_moderator_Z_names": RESIDUAL_MODERATOR_Z_NAMES,
            "residual_feature_names": residual_feature_names(),
        },
        "standardization": {
            "Z_mean": [float(x) for x in z_mean], "Z_std": [float(x) for x in z_std],
            "P_mean": [float(x) for x in p_mean], "P_std": [float(x) for x in p_std],
        },
        "weights": {
            "g0_intercept": float(g0_coef[0]),
            "g0_Z": [float(x) for x in g0_coef[1:]],
            "provenance_residual": [float(x) for x in r_coef],
        },
        "calibration_support": {
            "units": len(CALIBRATION_IDS),
            "beneficial_memory_units": beneficial,
            "harmful_memory_units": harmful,
            "neutral_units": int(sum(v == 0 for v in y)),
            "minimum_beneficial_required": CALIBRATION_MIN_BENEFICIAL,
            "minimum_harmful_required": CALIBRATION_MIN_HARMFUL,
            "route_support_pass": bool(route_support_pass),
        },
        "calibration_diagnostics": {
            "g0_predictions": [float(x) for x in g0_pred],
            "residual_targets": [float(x) for x in residual_target],
            "residual_predictions": [float(x) for x in residual_pred],
        },
    }
    model["model_sha256"] = digest(model)
    return model


def score_controller(model: dict[str, Any], feature_row: dict[str, Any], p_override: dict[str, float] | None = None) -> dict[str, float]:
    z = [float(feature_row["Z"][k]) for k in Z_FEATURE_NAMES]
    psrc = p_override if p_override is not None else feature_row["P"]
    p = [float(psrc[k]) for k in P_FEATURE_NAMES]
    s = model["standardization"]; w = model["weights"]
    z_s = _standardize_row(z, list(s["Z_mean"]), list(s["Z_std"]))
    p_s = _standardize_row(p, list(s["P_mean"]), list(s["P_std"]))
    r = _residual_design([p_s], [z_s])[0]
    g0 = float(w["g0_intercept"] + sum(a*b for a,b in zip(z_s, w["g0_Z"])))
    residual = float(sum(a*b for a,b in zip(r, w["provenance_residual"])))
    return {"g0_score": g0, "provenance_residual_score": residual, "psmg_score": g0 + residual}


def decide(score: float) -> str:
    return "M_content_only" if float(score) > DECISION_THRESHOLD else "N_no_memory"


def shuffled_p_donor_map(ids: list[str] | None = None) -> dict[str, str]:
    ids = list(TEST_IDS if ids is None else ids)
    if len(ids) < 2 or len(set(ids)) != len(ids):
        raise ValueError("shuffle-id-support")
    order = sorted(ids, key=lambda t: hashlib.sha256(f"{SHUFFLE_SEED_STRING}|{t}".encode()).hexdigest())
    return {order[i]: order[(i + 1) % len(order)] for i in range(len(order))}


def freeze_test_decisions(model: dict[str, Any], test_feature_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if model.get("model_sha256") != digest({k: v for k, v in model.items() if k != "model_sha256"}):
        raise ValueError("model-hash-drift")
    by = {str(x["task_id"]): x for x in test_feature_rows}
    if list(by) != TEST_IDS or set(by) != set(TEST_IDS):
        raise ValueError("test-feature-order-drift")
    donors = shuffled_p_donor_map(TEST_IDS)
    rows = []
    for tid in TEST_IDS:
        f = by[tid]
        truthful = score_controller(model, f)
        shuffled = score_controller(model, f, p_override=by[donors[tid]]["P"])
        sf = float(f["P"]["success_fraction"])
        rows.append({
            "task_id": tid,
            "g0_score": truthful["g0_score"],
            "psmg_residual_score": truthful["provenance_residual_score"],
            "psmg_score": truthful["psmg_score"],
            "shuffled_P_donor_task_id": donors[tid],
            "shuffled_psmg_score": shuffled["psmg_score"],
            "success_fraction": sf,
            "decisions": {
                "g0": decide(truthful["g0_score"]),
                "psmg": decide(truthful["psmg_score"]),
                "shuffled_psmg": decide(shuffled["psmg_score"]),
                "naive_success_prior": "M_content_only" if sf > 0.5 else "N_no_memory",
                "always_memory": "M_content_only",
                "never_memory": "N_no_memory",
            },
            "Z_sha256": f["Z_sha256"],
            "P_sha256": f["P_sha256"],
        })
    out = {
        "schema_version": "1.0", "paper_id": PAPER_ID,
        "role": "R65_PSMG_TEST_DECISIONS_FROZEN_PRE_TEST_OUTCOME",
        "model_sha256": model["model_sha256"],
        "test_ids": TEST_IDS,
        "test_ids_sha256": TEST_IDS_SHA256,
        "shuffle_seed_string": SHUFFLE_SEED_STRING,
        "rows": rows,
        "test_outcomes_observed_when_frozen": 0,
    }
    out["decision_plan_sha256"] = digest(out)
    return out


def exact_two_sided_signflip(positive: int, negative: int) -> float:
    m = int(positive) + int(negative)
    if m == 0:
        return 1.0
    lo = min(int(positive), int(negative))
    tail = sum(math.comb(m, k) for k in range(lo + 1)) / (2 ** m)
    return min(1.0, 2.0 * tail)


def percentile_ci(effects: list[float], seed: int = BOOTSTRAP_SEED, reps: int = BOOTSTRAP_REPETITIONS) -> list[float]:
    if not effects:
        raise ValueError("empty-effects")
    r = random.Random(int(seed)); n = len(effects); vals = []
    for _ in range(int(reps)):
        vals.append(sum(effects[r.randrange(n)] for _ in range(n)) / n)
    vals.sort()
    return [float(vals[math.floor(0.025 * (reps - 1))]), float(vals[math.ceil(0.975 * (reps - 1))])]


def analyze_test(decision_plan: dict[str, Any], potential_outcomes: dict[str, dict[str, bool]]) -> dict[str, Any]:
    if decision_plan.get("decision_plan_sha256") != digest({k:v for k,v in decision_plan.items() if k != "decision_plan_sha256"}):
        raise ValueError("decision-plan-hash-drift")
    if set(potential_outcomes) != set(TEST_IDS):
        raise ValueError("test-outcome-support-drift")
    policies = ["g0","psmg","shuffled_psmg","naive_success_prior","always_memory","never_memory"]
    value = {p: [] for p in policies}; oracle = []; rows = []
    decision_by = {str(x["task_id"]): x for x in decision_plan["rows"]}
    harmful_reuse = {p: 0 for p in policies}; missed_useful = {p: 0 for p in policies}
    useful = harmful = 0; beneficial_failure_total = beneficial_failure_psmg = 0; harmful_success_total = harmful_success_psmg_reject = 0
    for tid in TEST_IDS:
        o = potential_outcomes[tid]
        n = bool(o["N_no_memory"]); m = bool(o["M_content_only"])
        utility = int(m) - int(n)
        useful += int(utility > 0); harmful += int(utility < 0)
        drow = decision_by[tid]; sf = float(drow["success_fraction"])
        outcomes = {}
        for p in policies:
            action = drow["decisions"][p]
            y = m if action == "M_content_only" else n
            value[p].append(int(y)); outcomes[p] = bool(y)
            harmful_reuse[p] += int(utility < 0 and action == "M_content_only")
            missed_useful[p] += int(utility > 0 and action == "N_no_memory")
        oy = max(int(n), int(m)); oracle.append(oy)
        if utility > 0 and sf < 0.5:
            beneficial_failure_total += 1
            beneficial_failure_psmg += int(drow["decisions"]["psmg"] == "M_content_only")
        if utility < 0 and sf > 0.5:
            harmful_success_total += 1
            harmful_success_psmg_reject += int(drow["decisions"]["psmg"] == "N_no_memory")
        rows.append({"task_id":tid,"N_no_memory":n,"M_content_only":m,"memory_marginal_utility":utility,"policy_outcomes":outcomes,"decisions":drow["decisions"]})

    psmg_vs_g0 = [value["psmg"][i] - value["g0"][i] for i in range(len(TEST_IDS))]
    positive = sum(x > 0 for x in psmg_vs_g0); negative = sum(x < 0 for x in psmg_vs_g0)
    effect = float(sum(psmg_vs_g0) / len(psmg_vs_g0)); p = exact_two_sided_signflip(positive, negative); ci = percentile_ci(psmg_vs_g0)
    if effect >= EFFECT_RELEVANCE_FLOOR_ABS and p < 0.05:
        verdict = "PSMG_INCREMENTAL_GOVERNANCE_VALUE_SUPPORTED"
    elif effect <= -EFFECT_RELEVANCE_FLOOR_ABS and p < 0.05:
        verdict = "PSMG_INCREMENTAL_GOVERNANCE_HARM_SUPPORTED"
    else:
        verdict = "PSMG_EFFICACY_NOT_ESTABLISHED"
    values = {pname: float(sum(v)/len(v)) for pname,v in value.items()}
    oracle_value = float(sum(oracle)/len(oracle))
    out = {
        "schema_version":"1.0","paper_id":PAPER_ID,"role":"R65_PSMG_HIDDEN_GOVERNANCE_COMPLETE_ONLY_ANALYSIS",
        "status":verdict,"units":len(TEST_IDS),"primary_estimand":"policy_value(psmg)-policy_value(g0)",
        "effect_psmg_minus_g0":effect,"ci95_paired_cluster_bootstrap":ci,"bootstrap_repetitions":BOOTSTRAP_REPETITIONS,"bootstrap_seed":BOOTSTRAP_SEED,
        "psmg_only_wins":positive,"g0_only_wins":negative,"discordant_policy_outcomes":positive+negative,"exact_two_sided_signflip_p":p,
        "effect_relevance_floor_abs":EFFECT_RELEVANCE_FLOOR_ABS,"effect_relevance_floor_met":abs(effect)>=EFFECT_RELEVANCE_FLOOR_ABS,
        "policy_values":values,"binary_oracle_value":oracle_value,"policy_regret_to_binary_oracle":{pname:oracle_value-v for pname,v in values.items()},
        "memory_utility_support":{"beneficial_units":useful,"harmful_units":harmful,"neutral_units":len(TEST_IDS)-useful-harmful},
        "harmful_reuse_counts":harmful_reuse,"missed_useful_memory_counts":missed_useful,
        "beneficial_failure_memory":{"eligible_units":beneficial_failure_total,"psmg_admitted":beneficial_failure_psmg},
        "harmful_success_memory":{"eligible_units":harmful_success_total,"psmg_rejected":harmful_success_psmg_reject},
        "raw_provenance_executor_visible":False,"cross_model_pooling":False,"unit_rows":rows,
    }
    out["receipt_sha256"] = digest(out)
    return out
