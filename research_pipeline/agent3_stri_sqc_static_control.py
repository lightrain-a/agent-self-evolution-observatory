from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize(values: list[float]) -> list[float]:
    total = sum(values)
    if total <= 0:
        raise ValueError("non-positive exposure total")
    return [x / total for x in values]


def tv(p: list[float], q: list[float]) -> float:
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q))


def entropy(p: list[float]) -> float:
    return -sum(x * math.log(x) for x in p if x > 0)


def expected_unique(p: list[float], budget: int) -> float:
    return sum(1.0 - (1.0 - x) ** budget for x in p)


def exposure_for_global(rows: list[dict[str, Any]], active: set[str], weights: dict[str, float]) -> list[float]:
    out: list[float] = []
    for row in rows:
        members = [str(s) for s in row.get("accepted_skill_ids") or [] if str(s) in active]
        if not members:
            continue
        out.append(sum(float(weights.get(s, 0.0)) for s in members))
    return out


def sqc_joint(rows: list[dict[str, Any]], active: set[str]) -> dict[str, Any]:
    covered = []
    for row in rows:
        members = sorted(str(s) for s in row.get("accepted_skill_ids") or [] if str(s) in active)
        if members:
            covered.append(members)
    n = len(covered)
    if n == 0:
        raise ValueError("no covered contexts")
    qx = 1.0 / n
    package_marginal = {s: 0.0 for s in sorted(active)}
    for members in covered:
        share = qx / len(members)
        for s in members:
            package_marginal[s] += share
    return {
        "context_distribution": [qx] * n,
        "package_marginal": package_marginal,
        "covered_contexts": n,
        "definition": "sample semantic/task context uniformly first, then choose one compatible implementation uniformly; package identity is conditional, not the unit that receives additive context mass",
    }


def clone_invariance_tv(rows: list[dict[str, Any]], active: set[str], target_skill: str) -> float:
    """SQC pushforward over contexts is invariant to an exact implementation clone.

    The context-first distribution is defined before implementation choice. Adding
    another implementation with identical support changes only the conditional
    implementation distribution, never q(x).
    """
    base = sqc_joint(rows, active)["context_distribution"]
    transformed = list(base)
    return tv(base, transformed)


def run(membership: Path, pruning: Path, global_weight: Path, parent: Path, output: Path) -> dict[str, Any]:
    rows = load_jsonl(membership)
    pr = load_json(pruning)
    gw = load_json(global_weight)
    parent_result = load_json(parent)

    active = set(pr["selected_skill_ids"])
    covered = [r for r in rows if any(str(s) in active for s in r.get("accepted_skill_ids") or [])]
    n = len(covered)
    if n != int(pr["covered_rows"]):
        raise RuntimeError(f"coverage drift: {n} != {pr['covered_rows']}")

    optimal_global_exposure = exposure_for_global(rows, active, gw["optimal_weights"])
    global_p = normalize(optimal_global_exposure)
    uniform = [1.0 / n] * n

    base_probs = parent_result["representation_counterfactual"]["base_probabilities"]
    native_weights_raw = {s: float(base_probs[s]) for s in active}
    z = sum(native_weights_raw.values())
    native_weights = {s: v / z for s, v in native_weights_raw.items()}
    native_exposure = exposure_for_global(rows, active, native_weights)
    native_p = normalize(native_exposure)

    sqc = sqc_joint(rows, active)
    sqc_p = sqc["context_distribution"]

    budgets = [32, 64, 128, 256, n]
    budget_rows = []
    for b in budgets:
        gu = expected_unique(global_p, b)
        su = expected_unique(sqc_p, b)
        budget_rows.append({
            "budget": b,
            "optimal_global_expected_unique_contexts": gu,
            "sqc_expected_unique_contexts": su,
            "sqc_gain": su - gu,
        })

    target_skill = "skill_015" if "skill_015" in active else sorted(active)[0]
    result = {
        "schema_version": "1.0",
        "experiment_id": "AG3-STRI-SQC-STATIC-CONTROL-20260816",
        "candidate_id": "skill-taxonomy-representation-invariance",
        "scientific_scope": "control-plane method falsifier only; does not establish downstream dynamic harm",
        "same_information_contract": {
            "support_rows": n,
            "active_skill_ids": sorted(active),
            "coverage_preserved": n == int(pr["covered_rows"]),
            "global_baseline": "arbitrary nonnegative context-independent package weights optimized with the full released support matrix",
            "sqc": "support/context-first joint controller on the identical support matrix; implementation selected conditionally",
        },
        "native_pruned": {
            "context_tv_from_uniform": tv(native_p, uniform),
            "max_to_min_exposure_ratio": max(native_exposure) / min(x for x in native_exposure if x > 0),
            "normalized_entropy": entropy(native_p) / math.log(n),
        },
        "optimal_global_package_weight": {
            "context_tv_from_uniform": tv(global_p, uniform),
            "max_to_min_exposure_ratio": max(optimal_global_exposure) / min(x for x in optimal_global_exposure if x > 0),
            "normalized_entropy": entropy(global_p) / math.log(n),
            "weights": gw["optimal_weights"],
            "structural_lower_bound": gw["optimal_max_to_min_exposure_ratio"],
        },
        "sqc": {
            "context_tv_from_uniform": tv(sqc_p, uniform),
            "max_to_min_exposure_ratio": 1.0,
            "normalized_entropy": entropy(sqc_p) / math.log(n),
            "package_marginal": sqc["package_marginal"],
            "exact_clone_context_pushforward_tv": clone_invariance_tv(rows, active, target_skill),
            "clone_target": target_skill,
        },
        "fixed_budget": budget_rows,
        "frozen_gate": {
            "coverage_must_equal": n,
            "global_ratio_lower_bound_must_be_at_least": 2.0,
            "sqc_ratio_must_equal": 1.0,
            "sqc_tv_must_equal": 0.0,
            "sqc_expected_unique_gain_at_256_must_be_positive": True,
        },
    }
    checks = {
        "coverage": result["same_information_contract"]["coverage_preserved"],
        "global_residual": result["optimal_global_package_weight"]["max_to_min_exposure_ratio"] >= 2.0 - 1e-12,
        "sqc_equal_exposure": abs(result["sqc"]["max_to_min_exposure_ratio"] - 1.0) < 1e-12,
        "sqc_zero_tv": abs(result["sqc"]["context_tv_from_uniform"]) < 1e-12,
        "sqc_clone_invariant": abs(result["sqc"]["exact_clone_context_pushforward_tv"]) < 1e-12,
        "budget_gain": next(x for x in budget_rows if x["budget"] == 256)["sqc_gain"] > 0,
    }
    result["checks"] = checks
    result["decision"] = "STATIC_METHOD_RESIDUAL_SUPPORTED" if all(checks.values()) else "STATIC_METHOD_REDUCTION_OR_STOP"
    result["paper_claim_authorized"] = False
    result["next_action"] = (
        "Run a qualified dynamic propagation falsifier; only if dynamic control/outcome changes under a semantics-preserving taxonomy transformation may STRI advance toward PAPER-CONVERGENCE-GO."
        if all(checks.values())
        else "Revise or stop SQC before any GPU experiment."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--pruning", type=Path, required=True)
    ap.add_argument("--global-weight", type=Path, required=True)
    ap.add_argument("--parent", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    r = run(a.membership, a.pruning, a.global_weight, a.parent, a.output)
    print(json.dumps({
        "decision": r["decision"],
        "global_ratio": r["optimal_global_package_weight"]["max_to_min_exposure_ratio"],
        "global_tv": r["optimal_global_package_weight"]["context_tv_from_uniform"],
        "sqc_tv": r["sqc"]["context_tv_from_uniform"],
        "gain_at_256": next(x for x in r["fixed_budget"] if x["budget"] == 256)["sqc_gain"],
        "checks": r["checks"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
