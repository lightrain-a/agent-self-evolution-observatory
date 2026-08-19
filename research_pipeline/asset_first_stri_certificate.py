from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import linprog

from .asset_first_stri_structural_witness import structural_lower_bound


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def support_matrix(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str], np.ndarray]:
    """Return covered rows, active package IDs, and the binary support matrix."""
    covered = [row for row in rows if row.get("accepted_skill_ids")]
    skills = sorted({str(skill) for row in covered for skill in row.get("accepted_skill_ids") or []})
    A = np.asarray(
        [
            [1.0 if skill in set(map(str, row.get("accepted_skill_ids") or [])) else 0.0 for skill in skills]
            for row in covered
        ],
        dtype=float,
    )
    return covered, skills, A


def _target_vector(row_count: int, target_exposure: np.ndarray | list[float] | tuple[float, ...] | None) -> np.ndarray:
    """Normalize a strictly positive representation-independent semantic target."""
    if target_exposure is None:
        return np.ones(row_count, dtype=float)
    target = np.asarray(target_exposure, dtype=float)
    if target.ndim != 1 or len(target) != row_count:
        raise ValueError("target_exposure must have one positive value per covered support row")
    if np.any(~np.isfinite(target)) or np.any(target <= 0):
        raise ValueError("target_exposure must be finite and strictly positive")
    return target


def semantic_first_construction(
    rows: list[dict[str, Any]],
    *,
    target_exposure: np.ndarray | list[float] | tuple[float, ...] | None = None,
) -> dict[str, Any]:
    """Construct a semantic-first joint controller on the frozen support relation.

    The target ray q is normalized to a semantic-unit distribution pi. The
    controller first selects semantic unit i ~ pi, then selects an implementation
    package j from any row-stochastic kernel K supported by A. We use the
    deterministic uniform-within-row kernel as one witness. By construction the
    semantic marginal is exactly pi for arbitrary overlap. This changes the
    action basis relative to package-first control and is therefore a design
    construction, not a package-only baseline.
    """
    covered, skills, A = support_matrix(rows)
    if not covered:
        return {"pass": False, "reason": "no-covered-rows", "skills": []}
    target = _target_vector(len(covered), target_exposure)
    pi = target / float(target.sum())
    degree = A.sum(axis=1)
    if np.any(degree <= 0):
        return {"pass": False, "reason": "positive-target-row-without-support", "skills": skills}
    kernel = A / degree[:, None]
    joint = pi[:, None] * kernel
    semantic_marginal = joint.sum(axis=1)
    package_marginal = joint.sum(axis=0)
    support_violation_mass = float(np.sum(joint[A <= 0]))
    return {
        "pass": True,
        "skills": skills,
        "semantic_units": len(covered),
        "target_distribution": [float(value) for value in pi],
        "semantic_marginal": [float(value) for value in semantic_marginal],
        "package_marginal": {skill: float(package_marginal[j]) for j, skill in enumerate(skills)},
        "maximum_semantic_marginal_error": float(np.max(np.abs(semantic_marginal - pi))),
        "support_violation_mass": support_violation_mass,
        "kernel_row_sum_min": float(kernel.sum(axis=1).min()),
        "kernel_row_sum_max": float(kernel.sum(axis=1).max()),
        "interpretation": "Semantic-first selection realizes the target marginal exactly; package overlap only changes implementation responsibility inside each selected semantic unit.",
    }


def optimal_target_package_ratio(
    rows: list[dict[str, Any]],
    *,
    target_exposure: np.ndarray | list[float] | tuple[float, ...] | None = None,
    max_share: float | None = None,
) -> dict[str, Any]:
    """Solve target-conditioned R*(A;q), optionally with w_j <= rho * sum_k w_k.

    The default q=1 is the neutral audit used by the paper when no external
    pre-context semantic priority is specified. A nonuniform q lets a caller
    audit whether a representation-independent target ray is realizable by the
    package action cone without redefining STRI as uniformity itself.
    """
    covered, skills, A = support_matrix(rows)
    if not covered:
        return {"pass": False, "reason": "no-covered-rows", "ratio": None, "skills": []}
    if max_share is not None and not (0.0 < float(max_share) <= 1.0):
        raise ValueError("max_share must lie in (0, 1]")

    target = _target_vector(len(covered), target_exposure)
    n = len(skills)
    c = np.zeros(n + 1)
    c[-1] = 1.0
    A_ub: list[np.ndarray] = []
    b_ub: list[float] = []
    for incidence, desired in zip(A, target, strict=True):
        A_ub.append(np.r_[-incidence, 0.0])
        b_ub.append(-float(desired))
        A_ub.append(np.r_[incidence, -float(desired)])
        b_ub.append(0.0)
    if max_share is not None:
        rho = float(max_share)
        for j in range(n):
            cap = np.zeros(n + 1)
            cap[j] = 1.0
            cap[:n] -= rho
            A_ub.append(cap)
            b_ub.append(0.0)

    result = linprog(
        c,
        A_ub=np.asarray(A_ub),
        b_ub=np.asarray(b_ub),
        bounds=[(0, None)] * n + [(0, None)],
        method="highs",
    )
    if not result.success:
        return {
            "pass": False,
            "reason": str(result.message),
            "ratio": None,
            "skills": skills,
            "max_share": max_share,
        }
    weights = result.x[:n]
    exposures = A @ weights
    relative_exposure = exposures / target
    total_mass = float(weights.sum())
    return {
        "pass": True,
        "ratio": float(result.x[-1]),
        "minimum_relative_exposure": float(relative_exposure.min()),
        "maximum_relative_exposure": float(relative_exposure.max()),
        "minimum_exposure": float(exposures.min()),
        "maximum_exposure": float(exposures.max()),
        "weights": {skill: float(weights[i]) for i, skill in enumerate(skills)},
        "skills": skills,
        "target_exposure": [float(value) for value in target],
        "neutral_target": bool(np.allclose(target, 1.0)),
        "max_share": max_share,
        "attained_max_share": float(weights.max() / total_mass) if total_mass > 0 else None,
    }


def optimal_global_package_ratio(rows: list[dict[str, Any]], *, max_share: float | None = None) -> dict[str, Any]:
    """Backward-compatible neutral-target wrapper for R*(A;1)."""
    return optimal_target_package_ratio(rows, target_exposure=None, max_share=max_share)


def dual_target_package_ratio(
    rows: list[dict[str, Any]],
    *,
    target_exposure: np.ndarray | list[float] | tuple[float, ...] | None = None,
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Solve the dual of target-conditioned R*(A;q).

    The dual is max q^T alpha subject to A^T(beta-alpha)>=0,
    q^T beta<=1, alpha,beta>=0. Any feasible pair is a lower-bound
    certificate; strong duality makes the optimum equal R*(A;q).
    """
    covered, skills, A = support_matrix(rows)
    if not covered:
        return {"pass": False, "reason": "no-covered-rows", "lower_bound": None, "skills": []}
    target = _target_vector(len(covered), target_exposure)
    nr, nc = A.shape
    objective = np.r_[-target, np.zeros(nr)]
    A_ub: list[np.ndarray] = []
    b_ub: list[float] = []
    for j in range(nc):
        A_ub.append(np.r_[A[:, j], -A[:, j]])
        b_ub.append(0.0)
    A_ub.append(np.r_[np.zeros(nr), target])
    b_ub.append(1.0)
    result = linprog(
        objective,
        A_ub=np.asarray(A_ub),
        b_ub=np.asarray(b_ub),
        bounds=[(0, None)] * (2 * nr),
        method="highs",
    )
    if not result.success:
        return {"pass": False, "reason": str(result.message), "lower_bound": None, "skills": skills}

    alpha = result.x[:nr]
    beta = result.x[nr:]
    package_slack = A.T @ (beta - alpha)

    def nonzero_rows(values: np.ndarray) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for i in np.where(values > tolerance)[0]:
            row = covered[int(i)]
            out.append(
                {
                    "matrix_row": int(i),
                    "value": float(values[i]),
                    "target": float(target[i]),
                    "level": row.get("level"),
                    "index": row.get("index"),
                    "tool": row.get("tool"),
                    "source_skill_id": row.get("source_skill_id"),
                    "accepted_skill_ids": list(row.get("accepted_skill_ids") or []),
                }
            )
        return out

    return {
        "pass": True,
        "lower_bound": float(-result.fun),
        "target_weighted_beta": float(target @ beta),
        "sum_beta": float(beta.sum()),
        "minimum_package_slack": float(package_slack.min()) if len(package_slack) else None,
        "alpha_rows": nonzero_rows(alpha),
        "beta_rows": nonzero_rows(beta),
        "skills": skills,
        "target_exposure": [float(value) for value in target],
        "neutral_target": bool(np.allclose(target, 1.0)),
    }


def dual_global_package_ratio(rows: list[dict[str, Any]], *, tolerance: float = 1e-9) -> dict[str, Any]:
    """Backward-compatible neutral-target wrapper for the dual of R*(A;1)."""
    return dual_target_package_ratio(rows, target_exposure=None, tolerance=tolerance)


def robust_interval_package_ratio(
    lower_support: np.ndarray,
    upper_support: np.ndarray,
    *,
    skills: list[str] | None = None,
    target_exposure: np.ndarray | list[float] | tuple[float, ...] | None = None,
) -> dict[str, Any]:
    """Exact box-robust extension for target-conditioned additive support.

    With nonnegative w and elementwise L <= A <= U, the worst lower exposure is
    Lw and the worst upper exposure is Uw, so robust STRI is the LP
    min t s.t. Lw >= q and Uw <= tq. The default q=1 recovers the neutral audit.
    """
    lower = np.asarray(lower_support, dtype=float)
    upper = np.asarray(upper_support, dtype=float)
    if lower.ndim != 2 or lower.shape != upper.shape:
        raise ValueError("lower_support and upper_support must be same-shape matrices")
    if np.any(lower < 0) or np.any(upper < lower):
        raise ValueError("support interval must satisfy 0 <= lower <= upper")
    nr, nc = lower.shape
    names = list(skills) if skills is not None else [f"package_{j}" for j in range(nc)]
    if len(names) != nc:
        raise ValueError("skills length must match support columns")
    if nr == 0 or nc == 0:
        return {"pass": False, "reason": "empty-support-interval", "ratio": None, "skills": names}
    target = _target_vector(nr, target_exposure)

    c = np.zeros(nc + 1)
    c[-1] = 1.0
    A_ub: list[np.ndarray] = []
    b_ub: list[float] = []
    for lo, hi, desired in zip(lower, upper, target, strict=True):
        A_ub.append(np.r_[-lo, 0.0])
        b_ub.append(-float(desired))
        A_ub.append(np.r_[hi, -float(desired)])
        b_ub.append(0.0)
    result = linprog(
        c,
        A_ub=np.asarray(A_ub),
        b_ub=np.asarray(b_ub),
        bounds=[(0, None)] * nc + [(0, None)],
        method="highs",
    )
    if not result.success:
        return {"pass": False, "reason": str(result.message), "ratio": None, "skills": names}
    weights = result.x[:nc]
    return {
        "pass": True,
        "ratio": float(result.x[-1]),
        "weights": {name: float(weights[i]) for i, name in enumerate(names)},
        "skills": names,
        "target_exposure": [float(value) for value in target],
        "neutral_target": bool(np.allclose(target, 1.0)),
    }


def certify(rows: list[dict[str, Any]], *, context_id: str) -> dict[str, Any]:
    covered = [row for row in rows if row.get("accepted_skill_ids")]
    active_skills = {str(skill) for row in covered for skill in row.get("accepted_skill_ids") or []}
    witness = structural_lower_bound(rows, active_skills)
    optimum = optimal_global_package_ratio(rows)
    multi = sum(len(row.get("accepted_skill_ids") or []) > 1 for row in covered)
    singleton = sum(len(row.get("accepted_skill_ids") or []) == 1 for row in covered)
    max_membership = max((len(row.get("accepted_skill_ids") or []) for row in covered), default=0)

    theorem_lb = witness.get("global_nonnegative_package_weight_exposure_ratio_lower_bound")
    ratio = optimum.get("ratio")
    if ratio is not None and float(ratio) > 1.0 + 1e-8:
        decision = (
            "CERTIFIED_IRREDUCIBLE_PACKAGE_ONLY_REPRESENTATION_RESIDUAL_WITH_CLOSED_FORM_WITNESS"
            if theorem_lb is not None
            else "CERTIFIED_IRREDUCIBLE_PACKAGE_ONLY_REPRESENTATION_RESIDUAL_BY_EXACT_LP"
        )
    elif covered and ratio is not None and abs(float(ratio) - 1.0) <= 1e-8:
        decision = "CERTIFIED_PACKAGE_ONLY_EQUALIZABLE_NEGATIVE_CONTROL"
    else:
        decision = "UNRESOLVED_SUPPORT_OPTIMIZATION_OR_EMPTY_CONTEXT"

    return {
        "context_id": context_id,
        "rows": len(rows),
        "covered_rows": len(covered),
        "active_skills": sorted(active_skills),
        "single_membership_rows": singleton,
        "multi_membership_rows": multi,
        "maximum_membership_cardinality": max_membership,
        "decision": decision,
        "negative_control_subtype": (
            "DISJOINT_SUPPORT" if decision == "CERTIFIED_PACKAGE_ONLY_EQUALIZABLE_NEGATIVE_CONTROL" and multi == 0
            else "OVERLAP_BUT_GLOBALLY_EQUALIZABLE" if decision == "CERTIFIED_PACKAGE_ONLY_EQUALIZABLE_NEGATIVE_CONTROL"
            else ""
        ),
        "structural_witness": witness,
        "optimal_global_package_weighting": optimum,
        "tight_lower_bound": bool(theorem_lb is not None and ratio is not None and abs(float(theorem_lb) - float(ratio)) <= 1e-8),
        "scientific_authority": False,
    }


def filter_rows(rows: Iterable[dict[str, Any]], *, level: int | None = None, tools: set[str] | None = None) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if level is not None and int(row.get("level") or -1) != level:
            continue
        if tools is not None and str(row.get("tool") or "") not in tools:
            continue
        out.append(row)
    return out


def evaluate_frozen_contexts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    calibration_tools = {"AppointmentRegistration", "ModifyRegistration", "QueryHealthData", "RecordHealthData"}
    heldout_tools = {"CancelRegistration", "EmergencyKnowledge", "QueryRegistration", "SymptomSearch"}
    contexts = {
        "api_bank_level1_all": filter_rows(rows, level=1),
        "api_bank_level1_calibration_tools": filter_rows(rows, level=1, tools=calibration_tools),
        "api_bank_level1_heldout_tools": filter_rows(rows, level=1, tools=heldout_tools),
        "api_bank_level3_negative_control": filter_rows(rows, level=3),
    }
    results = {name: certify(part, context_id=name) for name, part in contexts.items()}
    expected = {
        "api_bank_level1_all": "CERTIFIED_IRREDUCIBLE_PACKAGE_ONLY_REPRESENTATION_RESIDUAL_WITH_CLOSED_FORM_WITNESS",
        "api_bank_level1_calibration_tools": "CERTIFIED_IRREDUCIBLE_PACKAGE_ONLY_REPRESENTATION_RESIDUAL_WITH_CLOSED_FORM_WITNESS",
        "api_bank_level1_heldout_tools": "CERTIFIED_IRREDUCIBLE_PACKAGE_ONLY_REPRESENTATION_RESIDUAL_WITH_CLOSED_FORM_WITNESS",
        "api_bank_level3_negative_control": "CERTIFIED_PACKAGE_ONLY_EQUALIZABLE_NEGATIVE_CONTROL",
    }
    checks = {name: results[name]["decision"] == target for name, target in expected.items()}
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "candidate_id": "skill-taxonomy-representation-invariance",
        "method": "STRI-Cert",
        "role": "mechanism-derived representation-invariance diagnostic certificate; not a downstream utility method",
        "contexts": results,
        "expected_mechanism_boundary": expected,
        "checks": checks,
        "all_expected_contexts_pass": all(checks.values()),
        "interpretation": "The certificate fires on the full Level-1 support graph and independently on the preregistered tool-disjoint calibration and heldout subsets, while the released Level-3 disjoint-support regime is a real negative control where package weighting is exactly equalizable (ratio=1). This tests the mechanism boundary without new model generation.",
        "prohibited_claims": [
            "STRI-Cert improves task success",
            "support overlap always causes downstream harm",
            "absence of the simple singleton-overlap witness proves representation invariance in arbitrary overlap graphs",
            "SQC has been validated dynamically",
        ],
        "scientific_authority": False,
        "authority": {"paper_claim_C3": False, "paper_claim_C4": False, "p0": False, "gpu": False},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = evaluate_frozen_contexts(load_jsonl(args.membership))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_expected_contexts_pass": result["all_expected_contexts_pass"], "checks": result["checks"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
