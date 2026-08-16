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


def optimal_global_package_ratio(rows: list[dict[str, Any]]) -> dict[str, Any]:
    covered = [row for row in rows if row.get("accepted_skill_ids")]
    skills = sorted({str(skill) for row in covered for skill in row.get("accepted_skill_ids") or []})
    if not covered:
        return {"pass": False, "reason": "no-covered-rows", "ratio": None, "skills": []}
    A = np.asarray([[1.0 if skill in set(map(str, row.get("accepted_skill_ids") or [])) else 0.0 for skill in skills] for row in covered])
    n = len(skills)
    c = np.zeros(n + 1); c[-1] = 1.0
    A_ub = []; b_ub = []
    for incidence in A:
        A_ub.append(np.r_[-incidence, 0.0]); b_ub.append(-1.0)
        A_ub.append(np.r_[incidence, -1.0]); b_ub.append(0.0)
    result = linprog(c, A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub), bounds=[(0, None)] * n + [(0, None)], method="highs")
    if not result.success:
        return {"pass": False, "reason": str(result.message), "ratio": None, "skills": skills}
    weights = result.x[:n]
    exposures = A @ weights
    return {
        "pass": True,
        "ratio": float(result.x[-1]),
        "minimum_exposure": float(exposures.min()),
        "maximum_exposure": float(exposures.max()),
        "weights": {skill: float(weights[i]) for i, skill in enumerate(skills)},
        "skills": skills,
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
