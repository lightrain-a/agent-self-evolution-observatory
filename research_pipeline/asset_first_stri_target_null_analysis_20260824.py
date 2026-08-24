from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from .asset_first_stri_certificate import optimal_global_package_ratio, optimal_target_package_ratio, support_matrix
from .asset_first_stri_reviewer_extensions import _ratio_from_matrix, load_jsonl

SCHEMA_VERSION = "1.0"
TARGET_ALPHA_GRID = (-1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0)
MAX_SHARE_GRID = (1.0, 0.75, 0.5, 0.4, 1.0 / 3.0, 0.3, 0.25, 0.2, 1.0 / 6.0)
NULL_DRAWS = 200
NULL_SWITCHES_PER_EDGE = 40
NULL_SEED_BASE = 2026082400
TOL = 1e-8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _level1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if int(row.get("level") or -1) == 1 and row.get("accepted_skill_ids")]


def tool_frequency_target(rows: list[dict[str, Any]], alpha: float) -> np.ndarray:
    """Build q_i proportional to count(tool_i)^alpha, normalized to mean one.

    Tool identity and corpus frequency are defined before looking at package IDs or
    the STRI optimum, so this is an exogenous representation-independent target
    family. Global scaling of q leaves R*(A;q) unchanged; mean-one normalization
    is only for readability.
    """
    counts = Counter(str(row.get("tool") or "") for row in rows)
    target = np.asarray([float(counts[str(row.get("tool") or "")]) ** float(alpha) for row in rows], dtype=float)
    if len(target) == 0 or np.any(target <= 0):
        raise ValueError("target family requires nonempty rows and positive tool counts")
    target /= float(target.mean())
    return target


def target_ray_sensitivity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for alpha in TARGET_ALPHA_GRID:
        target = tool_frequency_target(rows, alpha)
        result = optimal_target_package_ratio(rows, target_exposure=target)
        if not result.get("pass") or result.get("ratio") is None:
            raise RuntimeError(f"target-ray LP failed for alpha={alpha}: {result}")
        records.append(
            {
                "alpha": float(alpha),
                "target_definition": "q_i proportional to count(tool_i)^alpha; mean(q)=1",
                "minimum_q": float(target.min()),
                "maximum_q": float(target.max()),
                "R_star": float(result["ratio"]),
                "decision": "RESIDUAL" if float(result["ratio"]) > 1.0 + TOL else "EQUALIZABLE",
            }
        )
    ratios = [float(record["R_star"]) for record in records]
    neutral = next(record for record in records if abs(float(record["alpha"])) <= TOL)
    return {
        "scope": "frozen Skill-SP API-Bank Level-1 support matrix",
        "family": "representation-independent tool-frequency target rays",
        "records": records,
        "summary": {
            "targets": len(records),
            "neutral_R_star": float(neutral["R_star"]),
            "minimum_R_star": min(ratios),
            "maximum_R_star": max(ratios),
            "residual_targets": sum(float(value) > 1.0 + TOL for value in ratios),
            "all_tested_targets_residual": all(float(value) > 1.0 + TOL for value in ratios),
        },
        "claim_boundary": "This deterministic target family tests whether the released residual is an artifact of q=1. It does not claim that tool frequency is the unique deployment priority distribution.",
    }


def max_share_sensitivity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for rho in MAX_SHARE_GRID:
        result = optimal_global_package_ratio(rows, max_share=float(rho))
        records.append(
            {
                "rho": float(rho),
                "pass": bool(result.get("pass")),
                "R_star": float(result["ratio"]) if result.get("ratio") is not None else None,
                "attained_max_share": float(result["attained_max_share"]) if result.get("attained_max_share") is not None else None,
            }
        )
    valid = [record for record in records if record["R_star"] is not None]
    return {
        "scope": "neutral target on frozen Skill-SP API-Bank Level-1 support matrix",
        "records": records,
        "summary": {
            "valid_constraints": len(valid),
            "minimum_R_star": min(float(record["R_star"]) for record in valid),
            "maximum_R_star": max(float(record["R_star"]) for record in valid),
            "all_valid_constraints_residual": all(float(record["R_star"]) > 1.0 + TOL for record in valid),
        },
        "claim_boundary": "This is a feasibility sensitivity test for package-mass concentration, not a claim about which max-share constraint a deployed controller should use.",
    }


def degree_preserving_switch_null(
    matrix: np.ndarray,
    *,
    seed: int,
    successful_switches: int | None = None,
) -> tuple[np.ndarray, int, int]:
    """Bipartite double-edge swaps preserving every row and column degree."""
    A = np.asarray(matrix, dtype=float)
    if A.ndim != 2 or np.any((A != 0.0) & (A != 1.0)):
        raise ValueError("degree-preserving null requires a binary 2-D matrix")
    edges = [(int(i), int(j)) for i, j in zip(*np.where(A > 0.5), strict=True)]
    if len(edges) < 2:
        raise ValueError("degree-preserving null requires at least two edges")
    rng = np.random.default_rng(seed)
    edge_set = set(edges)
    target = successful_switches if successful_switches is not None else NULL_SWITCHES_PER_EDGE * len(edges)
    attempts = 0
    successes = 0
    max_attempts = max(100, int(target) * 50)
    while successes < int(target) and attempts < max_attempts:
        attempts += 1
        a, b = (int(x) for x in rng.integers(0, len(edges), size=2))
        if a == b:
            continue
        r1, c1 = edges[a]
        r2, c2 = edges[b]
        if r1 == r2 or c1 == c2:
            continue
        new_a = (r1, c2)
        new_b = (r2, c1)
        if new_a in edge_set or new_b in edge_set:
            continue
        edge_set.remove((r1, c1))
        edge_set.remove((r2, c2))
        edge_set.add(new_a)
        edge_set.add(new_b)
        edges[a] = new_a
        edges[b] = new_b
        successes += 1
    if successes < int(target):
        raise RuntimeError(f"switch chain mixed only {successes}/{target} requested successful swaps")
    B = np.zeros_like(A)
    for i, j in edges:
        B[i, j] = 1.0
    if not np.array_equal(B.sum(axis=0), A.sum(axis=0)):
        raise RuntimeError("column degrees changed under switch null")
    if not np.array_equal(B.sum(axis=1), A.sum(axis=1)):
        raise RuntimeError("row degrees changed under switch null")
    return B, successes, attempts


def degree_preserving_null_ensemble(rows: list[dict[str, Any]]) -> dict[str, Any]:
    _, skills, A = support_matrix(rows)
    observed = _ratio_from_matrix(A)
    if observed is None:
        raise RuntimeError("observed support matrix is invalid")
    records: list[dict[str, Any]] = []
    switches = NULL_SWITCHES_PER_EDGE * int(A.sum())
    for draw in range(NULL_DRAWS):
        seed = NULL_SEED_BASE + draw
        B, successes, attempts = degree_preserving_switch_null(A, seed=seed, successful_switches=switches)
        ratio = _ratio_from_matrix(B)
        if ratio is None:
            raise RuntimeError(f"null draw {draw} produced an invalid support matrix")
        records.append(
            {
                "draw": draw,
                "seed": seed,
                "successful_switches": successes,
                "attempts": attempts,
                "R_star": float(ratio),
                "decision": "RESIDUAL" if float(ratio) > 1.0 + TOL else "EQUALIZABLE",
            }
        )
    values = np.asarray([float(record["R_star"]) for record in records], dtype=float)
    ge_observed = int(np.sum(values >= float(observed) - TOL))
    return {
        "scope": "frozen Skill-SP API-Bank Level-1 support matrix",
        "null": "bipartite double-edge-switch ensemble preserving every row membership cardinality and every package support count exactly",
        "observed": {
            "rows": int(A.shape[0]),
            "packages": int(A.shape[1]),
            "edges": int(A.sum()),
            "active_skill_ids": skills,
            "R_star": float(observed),
        },
        "mixing": {
            "draws": NULL_DRAWS,
            "successful_switches_per_draw": switches,
            "switches_per_edge": NULL_SWITCHES_PER_EDGE,
            "seed_base": NULL_SEED_BASE,
        },
        "records": records,
        "summary": {
            "minimum_R_star": float(values.min()),
            "q05_R_star": float(np.quantile(values, 0.05)),
            "median_R_star": float(np.median(values)),
            "mean_R_star": float(values.mean()),
            "q95_R_star": float(np.quantile(values, 0.95)),
            "maximum_R_star": float(values.max()),
            "equalizable_draws": int(np.sum(np.abs(values - 1.0) <= TOL)),
            "residual_draws": int(np.sum(values > 1.0 + TOL)),
            "draws_at_least_observed_R_star": ge_observed,
            "empirical_tail_fraction_at_least_observed": ge_observed / NULL_DRAWS,
        },
        "claim_boundary": "The ensemble is a deterministic seeded structural control, not an exact uniform sampler over all bipartite graphs with these degrees and not a formal randomization-test p-value.",
    }


def build(membership: Path) -> dict[str, Any]:
    rows = load_jsonl(membership)
    level1 = _level1(rows)
    covered, skills, A = support_matrix(level1)
    return {
        "schema_version": SCHEMA_VERSION,
        "paper_id": "STRI",
        "analysis_type": "target-ray, package-mass, and same-marginal structural controls",
        "analysis_date": "2026-08-24",
        "input": {
            "membership_sha256": sha256(membership),
            "rows_all_levels": len(rows),
            "level1_covered_rows": len(covered),
            "active_packages": len(skills),
            "support_edges": int(A.sum()),
        },
        "target_ray_sensitivity": target_ray_sensitivity(level1),
        "max_share_sensitivity": max_share_sensitivity(level1),
        "degree_preserving_null_ensemble": degree_preserving_null_ensemble(level1),
        "scientific_boundary": {
            "claim_expansion": False,
            "new_outcome_data": False,
            "new_support_annotations": False,
            "model_calls": 0,
            "gpu_runs": 0,
            "purpose": "reviewer-facing structural controls on the frozen released support matrix",
        },
    }


def write_csv(payload: dict[str, Any], path: Path) -> None:
    rows: list[dict[str, Any]] = []
    for record in payload["target_ray_sensitivity"]["records"]:
        rows.append({"experiment": "target_ray", "setting": f"alpha={record['alpha']}", "R_star": record["R_star"], "decision": record["decision"], "seed": ""})
    for record in payload["max_share_sensitivity"]["records"]:
        rows.append({"experiment": "max_share", "setting": f"rho={record['rho']}", "R_star": record["R_star"], "decision": "RESIDUAL" if record["R_star"] is not None and record["R_star"] > 1.0 + TOL else "INFEASIBLE_OR_EQUALIZABLE", "seed": ""})
    for record in payload["degree_preserving_null_ensemble"]["records"]:
        rows.append({"experiment": "degree_preserving_null", "setting": f"draw={record['draw']}", "R_star": record["R_star"], "decision": record["decision"], "seed": record["seed"]})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["experiment", "setting", "R_star", "decision", "seed"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.membership)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(payload, args.output_csv)
    print(
        json.dumps(
            {
                "target": payload["target_ray_sensitivity"]["summary"],
                "max_share": payload["max_share_sensitivity"]["summary"],
                "null": payload["degree_preserving_null_ensemble"]["summary"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
