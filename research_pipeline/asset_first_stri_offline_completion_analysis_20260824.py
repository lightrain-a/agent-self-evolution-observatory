from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import scipy

from .asset_first_stri_certificate import support_matrix
from .asset_first_stri_reviewer_extensions import _ratio_from_matrix, load_jsonl

SCHEMA_VERSION = "1.0"
TOL = 1e-8
SCALE_GRID = (
    (128, 8),
    (512, 16),
    (2048, 32),
    (8192, 64),
    (16384, 96),
)
SCALE_REPEATS = 3
SCALE_SEED = 20260824


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_ratio(value: float | None) -> str:
    if value is None:
        return "FAIL_CLOSED_INVALID_SUPPORT"
    if abs(float(value) - 1.0) <= TOL:
        return "EQUALIZABLE"
    if float(value) > 1.0 + TOL:
        return "RESIDUAL"
    return "NUMERICAL_ANOMALY"


def _matrix_signature(row: np.ndarray) -> tuple[int, ...]:
    return tuple(int(v > 0.5) for v in row.tolist())


def _changed_cells(A: np.ndarray, B: np.ndarray) -> int:
    return int(np.count_nonzero(A != B))


def _summarize_perturbations(records: list[dict[str, Any]], *, base_class: str) -> dict[str, Any]:
    valid = [r for r in records if r["decision"] != "FAIL_CLOSED_INVALID_SUPPORT"]
    invalid = [r for r in records if r["decision"] == "FAIL_CLOSED_INVALID_SUPPORT"]
    same = [r for r in valid if r["decision"] == base_class]
    flipped = [r for r in valid if r["decision"] != base_class]
    ratios = [float(r["R_star"]) for r in valid if r.get("R_star") is not None]
    flip_cells = [int(r["changed_cells"]) for r in flipped]
    by_decision = Counter(r["decision"] for r in records)
    return {
        "perturbations": len(records),
        "valid_covered_perturbations": len(valid),
        "fail_closed_uncovered_or_invalid": len(invalid),
        "same_original_class": len(same),
        "same_original_class_fraction_among_valid": (len(same) / len(valid)) if valid else None,
        "class_flips_among_valid": len(flipped),
        "minimum_changed_cells_for_class_flip": min(flip_cells) if flip_cells else None,
        "minimum_R_star_among_valid": min(ratios) if ratios else None,
        "maximum_R_star_among_valid": max(ratios) if ratios else None,
        "decision_counts": dict(sorted(by_decision.items())),
    }


def signature_block_relabels(A: np.ndarray) -> list[dict[str, Any]]:
    groups: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for i, row in enumerate(A):
        groups[_matrix_signature(row)].append(i)
    signatures = sorted(groups)
    records: list[dict[str, Any]] = []
    for source_sig, target_sig in itertools.permutations(signatures, 2):
        B = A.copy()
        idx = groups[source_sig]
        B[idx, :] = np.asarray(target_sig, dtype=float)
        ratio = _ratio_from_matrix(B)
        records.append(
            {
                "source_signature": list(source_sig),
                "target_signature": list(target_sig),
                "affected_rows": len(idx),
                "changed_cells": _changed_cells(A, B),
                "R_star": ratio,
                "decision": classify_ratio(ratio),
            }
        )
    return records


def package_wide_biases(A: np.ndarray, skills: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for j, skill in enumerate(skills):
        for mode, value in (("systematic_false_positive", 1.0), ("systematic_false_negative", 0.0)):
            B = A.copy()
            B[:, j] = value
            changed = _changed_cells(A, B)
            if changed == 0:
                continue
            ratio = _ratio_from_matrix(B)
            records.append(
                {
                    "skill": skill,
                    "mode": mode,
                    "changed_cells": changed,
                    "R_star": ratio,
                    "decision": classify_ratio(ratio),
                }
            )
    return records


def tool_block_package_biases(covered: list[dict[str, Any]], A: np.ndarray, skills: list[str]) -> list[dict[str, Any]]:
    by_tool: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(covered):
        by_tool[str(row.get("tool") or "")].append(i)
    records: list[dict[str, Any]] = []
    for tool in sorted(by_tool):
        idx = by_tool[tool]
        for j, skill in enumerate(skills):
            for mode, value in (("tool_block_false_positive", 1.0), ("tool_block_false_negative", 0.0)):
                B = A.copy()
                before = B[idx, j].copy()
                B[idx, j] = value
                changed = int(np.count_nonzero(before != value))
                if changed == 0:
                    continue
                ratio = _ratio_from_matrix(B)
                records.append(
                    {
                        "tool": tool,
                        "skill": skill,
                        "mode": mode,
                        "affected_tool_rows": len(idx),
                        "changed_cells": changed,
                        "R_star": ratio,
                        "decision": classify_ratio(ratio),
                    }
                )
    return records


def support_misspecification(rows: list[dict[str, Any]]) -> dict[str, Any]:
    level1 = [r for r in rows if int(r.get("level") or -1) == 1]
    covered, skills, A = support_matrix(level1)
    base_ratio = _ratio_from_matrix(A)
    base_class = classify_ratio(base_ratio)
    if base_class != "RESIDUAL":
        raise RuntimeError(f"expected frozen Level-1 residual, got R*={base_ratio} class={base_class}")

    signature_records = signature_block_relabels(A)
    package_records = package_wide_biases(A, skills)
    tool_records = tool_block_package_biases(covered, A, skills)
    families = {
        "support_signature_block_relabel": {
            "definition": "For every ordered pair of distinct support signatures already observed in the frozen Level-1 matrix, relabel every row with the source signature to the target signature.",
            "summary": _summarize_perturbations(signature_records, base_class=base_class),
            "records": signature_records,
        },
        "package_wide_systematic_bias": {
            "definition": "For each active package, force its support bit to one for every covered row (systematic false positive) or to zero for every covered row (systematic false negative).",
            "summary": _summarize_perturbations(package_records, base_class=base_class),
            "records": package_records,
        },
        "tool_block_package_systematic_bias": {
            "definition": "For every observed tool × active-package block, force that package support bit to one or zero on every covered row of the tool; unchanged blocks are omitted.",
            "summary": _summarize_perturbations(tool_records, base_class=base_class),
            "records": tool_records,
        },
    }

    all_records = signature_records + package_records + tool_records
    valid_flips = [r for r in all_records if r["decision"] not in {base_class, "FAIL_CLOSED_INVALID_SUPPORT"}]
    return {
        "scope": "frozen released Skill-SP API-Bank Level-1 support matrix only",
        "base": {
            "covered_rows": len(covered),
            "active_packages": len(skills),
            "active_skill_ids": skills,
            "observed_support_signatures": len({_matrix_signature(row) for row in A}),
            "R_star": base_ratio,
            "decision": base_class,
        },
        "families": families,
        "aggregate": {
            "structured_perturbations": len(all_records),
            "valid_class_flips": len(valid_flips),
            "minimum_changed_cells_for_valid_class_flip": min((int(r["changed_cells"]) for r in valid_flips), default=None),
            "minimum_class_flip_examples": sorted(valid_flips, key=lambda r: (int(r["changed_cells"]), json.dumps(r, sort_keys=True)))[:8],
        },
        "interpretation_boundary": {
            "supports": "Deterministic sensitivity of the frozen STRI certificate to three structured families of support-label misspecification.",
            "does_not_support": [
                "a calibrated probability model for support-label error",
                "robustness to arbitrary adversarial multi-cell corruption",
                "accuracy of any learned support estimator",
                "retrospective replacement of the frozen support truth used by the main result",
            ],
        },
    }


def synthetic_support_matrix(rows: int, packages: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    A = np.zeros((rows, packages), dtype=float)
    # Predeclared heterogeneous degree distribution. Coverage is guaranteed and
    # every package appears at least once; no outcome from the paper is used.
    probs = np.asarray([0.48, 0.34, 0.18])
    degrees = rng.choice(np.asarray([1, 2, 3]), size=rows, p=probs)
    for i, degree in enumerate(degrees):
        cols = rng.choice(packages, size=min(int(degree), packages), replace=False)
        A[i, cols] = 1.0
    for j in range(packages):
        A[j % rows, j] = 1.0
    if np.any(A.sum(axis=1) <= 0):
        raise RuntimeError("synthetic generator produced an uncovered row")
    return A


def percentile(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    return float(np.quantile(np.asarray(values, dtype=float), q, method="linear"))


def scalability_profile() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for grid_index, (rows, packages) in enumerate(SCALE_GRID):
        for rep in range(SCALE_REPEATS):
            seed = SCALE_SEED + 1000 * grid_index + rep
            A = synthetic_support_matrix(rows, packages, seed)
            start = time.perf_counter()
            ratio = _ratio_from_matrix(A)
            seconds = time.perf_counter() - start
            if ratio is None:
                raise RuntimeError(f"synthetic R* LP failed at {(rows, packages, rep)}")
            constraints = 2 * rows
            variables = packages + 1
            dense_coefficients = constraints * variables
            records.append(
                {
                    "rows": rows,
                    "packages": packages,
                    "repeat": rep,
                    "seed": seed,
                    "variables": variables,
                    "inequality_constraints": constraints,
                    "dense_lp_coefficients": dense_coefficients,
                    "dense_lp_matrix_MiB": dense_coefficients * 8 / (1024 * 1024),
                    "support_density": float(A.mean()),
                    "R_star": ratio,
                    "wall_seconds": seconds,
                }
            )

    by_grid: list[dict[str, Any]] = []
    for rows, packages in SCALE_GRID:
        subset = [r for r in records if r["rows"] == rows and r["packages"] == packages]
        times = [float(r["wall_seconds"]) for r in subset]
        by_grid.append(
            {
                "rows": rows,
                "packages": packages,
                "variables": packages + 1,
                "inequality_constraints": 2 * rows,
                "median_wall_seconds": statistics.median(times),
                "p95_wall_seconds": percentile(times, 0.95),
                "max_wall_seconds": max(times),
                "dense_lp_matrix_MiB": subset[0]["dense_lp_matrix_MiB"],
                "mean_support_density": statistics.mean(float(r["support_density"]) for r in subset),
                "R_star_values": [float(r["R_star"]) for r in subset],
            }
        )
    return {
        "scope": "CPU solver profiling of the existing SciPy/HiGHS neutral-target R* LP after a support matrix is already materialized; this does not profile support annotation or signature enumeration.",
        "runtime_environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "logical_cpu_count": os.cpu_count(),
        },
        "grid": [list(x) for x in SCALE_GRID],
        "repeats_per_grid": SCALE_REPEATS,
        "seed_base": SCALE_SEED,
        "generator": "binary covered support matrix with deterministic seeded row degrees in {1,2,3}; every package is forced to appear at least once",
        "records": records,
        "summary": by_grid,
        "claim_boundary": [
            "The reported wall times characterize this reference dense-LP implementation on the recorded current CPU environment and host load only; repeat batches may differ materially in wall time.",
            "They do not establish asymptotic solver novelty, population-scale support acquisition cost, or end-to-end skill-system scalability.",
        ],
    }


def build(membership: Path) -> dict[str, Any]:
    rows = load_jsonl(membership)
    result = {
        "schema_version": SCHEMA_VERSION,
        "paper_id": "STRI",
        "analysis_type": "offline manuscript-completion analysis for structured support sensitivity and conditional R* scaling",
        "analysis_date": "2026-08-24",
        "input": {
            "membership_sha256": sha256(membership),
            "rows": len(rows),
        },
        "support_misspecification_sensitivity": support_misspecification(rows),
        "rstar_solver_scalability": scalability_profile(),
        "paper_use": {
            "E4_artifact_diagnostic_quality": "structured support-misspecification sensitivity",
            "E6_efficiency_cost_scale": "reference R* LP CPU scaling after support materialization",
        },
        "scientific_boundary": {
            "claim_expansion": False,
            "new_outcome_data": False,
            "new_support_annotations": False,
            "model_calls": 0,
            "gpu_runs": 0,
            "preserve_same_run_causal_scope": True,
            "preserve_skillrl_as_adjacent_not_independent_support": True,
            "preserve_autoskill_as_closest_work_not_prevalence": True,
        },
        "scientific_authority": False,
        "authority": {"method": False, "experiment": False, "gpu": False, "paper_claim_expansion": False},
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.membership)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "support": result["support_misspecification_sensitivity"]["aggregate"],
                "scale": result["rstar_solver_scalability"]["summary"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
