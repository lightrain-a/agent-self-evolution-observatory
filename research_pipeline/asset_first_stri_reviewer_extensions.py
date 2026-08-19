from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linprog

from .asset_first_stri_certificate import (
    certify,
    dual_global_package_ratio,
    optimal_global_package_ratio,
    semantic_first_construction,
    support_matrix,
)

CALIBRATION_TOOLS = {"AppointmentRegistration", "ModifyRegistration", "QueryHealthData", "RecordHealthData"}
HELDOUT_TOOLS = {"CancelRegistration", "EmergencyKnowledge", "QueryRegistration", "SymptomSearch"}
DEFAULT_MAX_SHARE_GRID = (1.0, 0.75, 0.5, 0.25, 0.125)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _ratio_from_matrix(A: np.ndarray) -> float | None:
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] == 0 or A.shape[1] == 0 or np.any(A.sum(axis=1) <= 0):
        return None
    nr, nc = A.shape
    c = np.zeros(nc + 1)
    c[-1] = 1.0
    A_ub: list[np.ndarray] = []
    b_ub: list[float] = []
    for incidence in A:
        A_ub.append(np.r_[-incidence, 0.0])
        b_ub.append(-1.0)
        A_ub.append(np.r_[incidence, -1.0])
        b_ub.append(0.0)
    result = linprog(
        c,
        A_ub=np.asarray(A_ub),
        b_ub=np.asarray(b_ub),
        bounds=[(0, None)] * (nc + 1),
        method="highs",
    )
    return float(result.x[-1]) if result.success else None


def single_edge_support_stability(rows: list[dict[str, Any]], *, tolerance: float = 1e-8) -> dict[str, Any]:
    covered, skills, A = support_matrix(rows)
    base = _ratio_from_matrix(A)
    if base is None:
        return {"pass": False, "reason": "invalid-base-support", "active_skills": skills}

    base_residual = base > 1.0 + tolerance
    add_ratios: list[float] = []
    delete_ratios: list[float] = []
    deletion_to_uncovered = 0
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            B = A.copy()
            if A[i, j] == 0.0:
                B[i, j] = 1.0
                ratio = _ratio_from_matrix(B)
                if ratio is None:
                    raise RuntimeError("support addition unexpectedly invalidated the LP")
                add_ratios.append(ratio)
            else:
                if A[i].sum() <= 1.0:
                    deletion_to_uncovered += 1
                    continue
                B[i, j] = 0.0
                ratio = _ratio_from_matrix(B)
                if ratio is None:
                    raise RuntimeError("non-uncovering support deletion unexpectedly invalidated the LP")
                delete_ratios.append(ratio)

    def summarize(values: list[float]) -> dict[str, Any]:
        arr = np.asarray(values, dtype=float)
        residual = arr > 1.0 + tolerance
        equalizable = np.abs(arr - 1.0) <= tolerance
        same_class = residual if base_residual else equalizable
        return {
            "perturbations": int(len(arr)),
            "minimum_R_star": float(arr.min()) if len(arr) else None,
            "maximum_R_star": float(arr.max()) if len(arr) else None,
            "residual_count": int(residual.sum()),
            "equalizable_count": int(equalizable.sum()),
            "same_original_class_count": int(same_class.sum()),
            "same_original_class_fraction": float(same_class.mean()) if len(arr) else None,
        }

    return {
        "pass": True,
        "base_R_star": base,
        "covered_rows": len(covered),
        "active_skills": skills,
        "support_additions": summarize(add_ratios),
        "support_deletions_that_keep_row_covered": summarize(delete_ratios),
        "support_deletions_that_would_uncover_row": deletion_to_uncovered,
        "interpretation": "Exact exhaustive one-cell stress test on the frozen binary matrix; this is not a learned-support calibration experiment.",
    }


def analyze_context(rows: list[dict[str, Any]], *, context_id: str) -> dict[str, Any]:
    covered, skills, A = support_matrix(rows)
    primal = optimal_global_package_ratio(rows)
    dual = dual_global_package_ratio(rows)
    if not primal.get("pass") or not dual.get("pass"):
        raise RuntimeError(f"invalid context {context_id}: primal={primal} dual={dual}")
    gap = abs(float(primal["ratio"]) - float(dual["lower_bound"]))

    max_share_scan: dict[str, Any] = {}
    for rho in DEFAULT_MAX_SHARE_GRID:
        result = optimal_global_package_ratio(rows, max_share=rho)
        max_share_scan[f"{rho:.3f}"] = {
            "feasible": bool(result.get("pass")),
            "R_star_rho": result.get("ratio"),
            "attained_max_share": result.get("attained_max_share"),
            "weights": result.get("weights") if result.get("pass") else None,
            "reason": result.get("reason") if not result.get("pass") else None,
        }

    semantic_first = semantic_first_construction(rows)
    if not semantic_first.get("pass"):
        raise RuntimeError(f"semantic-first construction failed for {context_id}: {semantic_first}")

    return {
        "context_id": context_id,
        "covered_rows": len(covered),
        "active_skills": skills,
        "support_shape": [int(A.shape[0]), int(A.shape[1])],
        "R_star": float(primal["ratio"]),
        "dual": {
            "lower_bound": float(dual["lower_bound"]),
            "primal_dual_gap": gap,
            "sum_beta": dual["sum_beta"],
            "minimum_package_slack": dual["minimum_package_slack"],
            "alpha_rows": dual["alpha_rows"],
            "beta_rows": dual["beta_rows"],
        },
        "max_share_scan": max_share_scan,
        "semantic_first_neutral_construction": {
            "maximum_semantic_marginal_error": semantic_first["maximum_semantic_marginal_error"],
            "support_violation_mass": semantic_first["support_violation_mass"],
            "kernel_row_sum_min": semantic_first["kernel_row_sum_min"],
            "kernel_row_sum_max": semantic_first["kernel_row_sum_max"],
        },
        "single_edge_support_stability": single_edge_support_stability(rows),
    }


def per_tool_exact_lp(level1_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_tool: dict[str, list[dict[str, Any]]] = {}
    for row in level1_rows:
        by_tool.setdefault(str(row.get("tool") or ""), []).append(row)
    records: list[dict[str, Any]] = []
    for tool, rows in sorted(by_tool.items()):
        out = certify(rows, context_id=f"tool:{tool}")
        optimum = out.get("optimal_global_package_weighting") or {}
        witness = out.get("structural_witness") or {}
        ratio = optimum.get("ratio")
        records.append(
            {
                "tool": tool,
                "covered_rows": int(out.get("covered_rows") or 0),
                "multi_membership_rows": int(out.get("multi_membership_rows") or 0),
                "witness_count": int(witness.get("witness_count") or 0),
                "R_star": ratio,
                "decision": out.get("decision"),
            }
        )
    no_support = [r for r in records if r["covered_rows"] == 0]
    equalizable = [r for r in records if r["R_star"] is not None and abs(float(r["R_star"]) - 1.0) <= 1e-8]
    residual = [r for r in records if r["R_star"] is not None and float(r["R_star"]) > 1.0 + 1e-8]
    overlap_no_witness = [r for r in records if r["multi_membership_rows"] > 0 and r["witness_count"] == 0]
    return {
        "tool_count": len(records),
        "no_support_tools": len(no_support),
        "equalizable_tools": len(equalizable),
        "residual_tools": len(residual),
        "overlap_without_singleton_witness": {
            "tools": len(overlap_no_witness),
            "equalizable_by_exact_lp": sum(r["R_star"] is not None and abs(float(r["R_star"]) - 1.0) <= 1e-8 for r in overlap_no_witness),
            "residual_by_exact_lp": sum(r["R_star"] is not None and float(r["R_star"]) > 1.0 + 1e-8 for r in overlap_no_witness),
        },
        "records": records,
    }


def evaluate(membership_rows: list[dict[str, Any]], logical_rows: list[dict[str, Any]]) -> dict[str, Any]:
    level1_rows = [r for r in membership_rows if int(r.get("level") or -1) == 1]
    contexts = {
        "api_bank_level1_all": level1_rows,
        "api_bank_level1_calibration_tools": [
            r for r in membership_rows if int(r.get("level") or -1) == 1 and str(r.get("tool") or "") in CALIBRATION_TOOLS
        ],
        "api_bank_level1_heldout_tools": [
            r for r in membership_rows if int(r.get("level") or -1) == 1 and str(r.get("tool") or "") in HELDOUT_TOOLS
        ],
        "api_bank_level3_negative_control": [r for r in membership_rows if int(r.get("level") or -1) == 3],
        "logical_compiler_validation": logical_rows,
    }
    analyses = {name: analyze_context(rows, context_id=name) for name, rows in contexts.items()}
    per_tool = per_tool_exact_lp(level1_rows)

    l1 = analyses["api_bank_level1_all"]["single_edge_support_stability"]
    logical = analyses["logical_compiler_validation"]
    logical_del = logical["single_edge_support_stability"]["support_deletions_that_keep_row_covered"]
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis_type": "reviewer-requested dual/constrained/support-perturbation extensions",
        "contexts": analyses,
        "per_tool_exact_lp": per_tool,
        "headline_checks": {
            "all_primal_dual_gaps_le_1e_8": all(ctx["dual"]["primal_dual_gap"] <= 1e-8 for ctx in analyses.values()),
            "semantic_first_neutral_target_exact_on_all_five_regimes": all(
                ctx["semantic_first_neutral_construction"]["maximum_semantic_marginal_error"] <= 1e-12
                and ctx["semantic_first_neutral_construction"]["support_violation_mass"] <= 1e-12
                and abs(ctx["semantic_first_neutral_construction"]["kernel_row_sum_min"] - 1.0) <= 1e-12
                and abs(ctx["semantic_first_neutral_construction"]["kernel_row_sum_max"] - 1.0) <= 1e-12
                for ctx in analyses.values()
            ),
            "level1_residual_survives_all_single_support_additions": (
                l1["support_additions"]["same_original_class_fraction"] == 1.0
            ),
            "level1_residual_survives_all_nonuncovering_single_support_deletions": (
                l1["support_deletions_that_keep_row_covered"]["same_original_class_fraction"] == 1.0
            ),
            "logical_unrestricted_equalizable": abs(float(logical["R_star"]) - 1.0) <= 1e-8,
            "logical_rho_075_not_equalizable": float(logical["max_share_scan"]["0.750"]["R_star_rho"]) > 1.0 + 1e-8,
            "logical_single_deletions_can_break_equalizability": int(logical_del["residual_count"]) > 0,
            "all_overlap_without_simple_witness_tools_resolve_equalizable": (
                per_tool["overlap_without_singleton_witness"]["tools"]
                == per_tool["overlap_without_singleton_witness"]["equalizable_by_exact_lp"]
            ),
        },
        "claim_boundary": {
            "supported": [
                "the LP dual gives a complete lower-bound certificate and has zero numerical duality gap on all five audited regimes",
                "the Level-1 positive residual is stable to every exhaustive one-cell support addition and every one-cell deletion that keeps the affected row covered",
                "the logical-compiler R*=1 solution is operationally concentrated: imposing a 75% package-mass cap makes the constrained optimum exceed one",
                "the logical-compiler negative boundary is asymmetric under support error: some single support deletions break equalizability",
                "a semantic-first row-stochastic implementation factorization realizes the neutral semantic target exactly on all five covered frozen support regimes despite arbitrary overlap",
            ],
            "not_supported": [
                "learned support estimators are calibrated",
                "arbitrary multi-cell support noise preserves the certificate",
                "static exposure distortion causes downstream utility harm",
                "constrained equalization or semantic-first factorization is a downstream-validated new optimization algorithm",
            ],
        },
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "dynamic_claim": False, "gpu": False},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--logical-support", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = evaluate(load_jsonl(args.membership), load_jsonl(args.logical_support))
    result["inputs"] = {
        "membership_sha256": sha256(args.membership),
        "logical_support_sha256": sha256(args.logical_support),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["headline_checks"], ensure_ascii=False))


if __name__ == "__main__":
    main()
