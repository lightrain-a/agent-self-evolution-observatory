from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

from .asset_first_stri_certificate import support_matrix
from .asset_first_stri_reviewer_extensions import _ratio_from_matrix, load_jsonl

TOL = 1e-8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def level1_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if int(row.get("level") or -1) == 1 and row.get("accepted_skill_ids")]


def _equalizing_edit_milp(matrix: np.ndarray, *, mode: str) -> dict[str, Any]:
    """Solve the exact neutral-target support-cell edit radius.

    For q=1, R*(A;1)=1 iff A w = 1 for some w>=0. Every active column
    appears in at least one original row, so any feasible equalizing solution has
    0<=w_j<=1. This makes M=1 an exact bound for linearizing y=z*w.

    mode='addition' allows only 0->1 support edits and minimizes their count.
    mode='deletion' allows only 1->0 edits and equivalently maximizes retained
    support cells. The output is independently rechecked with the exact R* LP.
    """
    A = np.asarray(matrix, dtype=float)
    if A.ndim != 2 or np.any((A != 0.0) & (A != 1.0)):
        raise ValueError("support-edit MILP requires a binary 2-D matrix")
    n, m = A.shape
    if np.any(A.sum(axis=0) <= 0):
        raise ValueError("every active package must appear in at least one original row")
    if mode == "addition":
        cells = [(i, j) for i in range(n) for j in range(m) if A[i, j] < 0.5]
        maximize_retained = False
    elif mode == "deletion":
        cells = [(i, j) for i in range(n) for j in range(m) if A[i, j] > 0.5]
        maximize_retained = True
    else:
        raise ValueError(f"unknown edit mode: {mode}")

    k = len(cells)
    # Variable layout: package weights w[m], binary selectors z[k], products y[k].
    total_vars = m + 2 * k
    objective = np.zeros(total_vars, dtype=float)
    objective[m : m + k] = -1.0 if maximize_retained else 1.0
    integrality = np.zeros(total_vars, dtype=int)
    integrality[m : m + k] = 1
    bounds = Bounds(np.zeros(total_vars), np.ones(total_vars))
    cell_index = {cell: idx for idx, cell in enumerate(cells)}

    exposure = lil_matrix((n, total_vars), dtype=float)
    for i in range(n):
        for j in range(m):
            if mode == "addition":
                if A[i, j] > 0.5:
                    exposure[i, j] += 1.0
                else:
                    exposure[i, m + k + cell_index[(i, j)]] += 1.0
            elif A[i, j] > 0.5:
                exposure[i, m + k + cell_index[(i, j)]] += 1.0
    exposure_constraint = LinearConstraint(exposure.tocsr(), np.ones(n), np.ones(n))

    # Exact McCormick linearization for binary z and w in [0,1]: y=z*w.
    product = lil_matrix((3 * k, total_vars), dtype=float)
    lo = np.full(3 * k, -np.inf, dtype=float)
    hi = np.zeros(3 * k, dtype=float)
    for idx, (_, j) in enumerate(cells):
        z = m + idx
        y = m + k + idx
        # y <= z
        product[3 * idx, y] = 1.0
        product[3 * idx, z] = -1.0
        # y <= w_j
        product[3 * idx + 1, y] = 1.0
        product[3 * idx + 1, j] = -1.0
        # y >= w_j + z - 1  <=>  w_j + z - y <= 1.
        product[3 * idx + 2, j] = 1.0
        product[3 * idx + 2, z] = 1.0
        product[3 * idx + 2, y] = -1.0
        hi[3 * idx + 2] = 1.0
    product_constraint = LinearConstraint(product.tocsr(), lo, hi)

    result = milp(
        objective,
        integrality=integrality,
        bounds=bounds,
        constraints=[exposure_constraint, product_constraint],
        options={"mip_rel_gap": 0.0},
    )
    if result.x is None or int(result.status) != 0:
        raise RuntimeError(f"{mode} edit-radius MILP failed: status={result.status} message={result.message}")

    z_values = np.asarray(result.x[m : m + k], dtype=float)
    weights = np.asarray(result.x[:m], dtype=float)
    selected = [cells[idx] for idx, value in enumerate(z_values) if value > 0.5]
    if mode == "addition":
        edits = selected
        modified = A.copy()
        for cell in edits:
            modified[cell] = 1.0
        edit_count = len(edits)
    else:
        retained = set(selected)
        edits = [cell for cell in cells if cell not in retained]
        modified = A.copy()
        for cell in edits:
            modified[cell] = 0.0
        edit_count = len(edits)

    verified_ratio = _ratio_from_matrix(modified)
    if verified_ratio is None or abs(float(verified_ratio) - 1.0) > TOL:
        raise RuntimeError(f"{mode} MILP solution failed independent R* verification: {verified_ratio}")
    if np.any(modified.sum(axis=1) <= 0):
        raise RuntimeError(f"{mode} MILP produced an uncovered row")

    return {
        "mode": mode,
        "solver_status": int(result.status),
        "solver_message": str(result.message),
        "mip_gap": float(getattr(result, "mip_gap", 0.0) or 0.0),
        "mip_node_count": int(getattr(result, "mip_node_count", 0) or 0),
        "edit_count": edit_count,
        "package_weights": [float(value) for value in weights],
        "edited_cells": [{"row": int(i), "column": int(j)} for i, j in edits],
        "verified_R_star": float(verified_ratio),
        "verified_all_rows_covered": bool(np.all(modified.sum(axis=1) > 0)),
    }


def support_edit_radius(matrix: np.ndarray) -> dict[str, Any]:
    observed = _ratio_from_matrix(matrix)
    if observed is None:
        raise RuntimeError("invalid observed support matrix")
    additions = _equalizing_edit_milp(matrix, mode="addition")
    deletions = _equalizing_edit_milp(matrix, mode="deletion")
    return {
        "observed_R_star": float(observed),
        "minimum_additions_to_equalizable": additions["edit_count"],
        "minimum_deletions_to_equalizable": deletions["edit_count"],
        "addition_solution": additions,
        "deletion_solution": deletions,
        "claim_boundary": "These are exact cell-edit radii for the frozen binary support matrix, neutral q=1, and addition-only/deletion-only interventions. They do not cover mixed edits, learned support, or downstream utility.",
    }


def build(membership: Path) -> dict[str, Any]:
    rows = load_jsonl(membership)
    level1 = level1_rows(rows)
    covered, skills, A = support_matrix(level1)
    radius = support_edit_radius(A)
    for solution_name in ("addition_solution", "deletion_solution"):
        for cell in radius[solution_name]["edited_cells"]:
            i = int(cell["row"])
            j = int(cell["column"])
            cell["skill_id"] = str(skills[j])
            cell["source_index"] = int(covered[i].get("index"))
            cell["tool"] = str(covered[i].get("tool") or "")
    addition_ids = {cell["skill_id"] for cell in radius["addition_solution"]["edited_cells"]}
    radius["addition_solution"]["edited_skill_ids"] = sorted(addition_ids)
    radius["addition_solution"]["all_additions_same_skill"] = len(addition_ids) == 1
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis_type": "exact neutral-target support-cell edit radius",
        "analysis_date": "2026-08-24",
        "input": {
            "membership_sha256": sha256(membership),
            "level1_covered_rows": int(A.shape[0]),
            "active_packages": int(A.shape[1]),
            "support_edges": int(A.sum()),
            "active_skill_ids": [str(skill) for skill in skills],
        },
        "support_edit_radius": radius,
        "scientific_boundary": {
            "claim_expansion": False,
            "new_outcome_data": False,
            "new_support_annotations": False,
            "model_calls": 0,
            "gpu_runs": 0,
            "purpose": "reviewer-facing exact robustness radius on the frozen released support matrix",
        },
    }


def write_csv(payload: dict[str, Any], path: Path) -> None:
    radius = payload["support_edit_radius"]
    rows: list[dict[str, Any]] = []
    for mode, key in (("addition", "addition_solution"), ("deletion", "deletion_solution")):
        solution = radius[key]
        for cell in solution["edited_cells"]:
            rows.append(
                {
                    "mode": mode,
                    "minimum_edit_count": solution["edit_count"],
                    "source_index": cell["source_index"],
                    "matrix_row": cell["row"],
                    "skill_id": cell["skill_id"],
                    "tool": cell["tool"],
                    "verified_R_star": solution["verified_R_star"],
                    "mip_gap": solution["mip_gap"],
                }
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["mode", "minimum_edit_count", "source_index", "matrix_row", "skill_id", "tool", "verified_R_star", "mip_gap"],
        )
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
    radius = payload["support_edit_radius"]
    print(
        json.dumps(
            {
                "observed_R_star": radius["observed_R_star"],
                "minimum_additions_to_equalizable": radius["minimum_additions_to_equalizable"],
                "minimum_deletions_to_equalizable": radius["minimum_deletions_to_equalizable"],
                "addition_skill_ids": radius["addition_solution"]["edited_skill_ids"],
                "addition_gap": radius["addition_solution"]["mip_gap"],
                "deletion_gap": radius["deletion_solution"]["mip_gap"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
