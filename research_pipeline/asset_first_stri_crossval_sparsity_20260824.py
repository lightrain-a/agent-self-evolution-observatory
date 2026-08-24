from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linprog

from .asset_first_stri_certificate import support_matrix
from .asset_first_stri_practical_baselines_20260824 import (
    DEFAULT_SPLIT,
    DEFAULT_SUPPLEMENT,
    _align_weights,
    _scale_invariant_metrics,
    evaluate_regime,
    load_regimes,
    regimes_from_rows,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "generated" / "asset-first-stri-crossval-sparsity-20260824.json"
DEFAULT_CSV = ROOT / "generated" / "asset-first-stri-crossval-sparsity-20260824.csv"


def _jsonl_from_zip(path: Path, member: str) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as zf:
        return [json.loads(line) for line in zf.read(member).decode("utf-8").splitlines() if line.strip()]


def _row_id(row: dict[str, Any]) -> str:
    return f"L{row['level']}:{row['index']}:{row['tool']}"


def _finite_or_none(value: float | None) -> float | None:
    if value is None or not math.isfinite(float(value)):
        return None
    return float(value)


def leave_one_tool_out_transfer(
    tool_rows: list[dict[str, Any]],
    split: dict[str, Any],
) -> dict[str, Any]:
    by_id = {_row_id(row): row for row in tool_rows}
    selected_ids = [
        *split["partitions"]["calibration"]["row_ids"],
        *split["partitions"]["heldout"]["row_ids"],
    ]
    selected = [by_id[row_id] for row_id in selected_ids]
    tools = sorted({str(row["tool"]) for row in selected})
    folds: list[dict[str, Any]] = []

    for heldout_tool in tools:
        train_rows = [row for row in selected if str(row["tool"]) != heldout_tool]
        test_rows = [row for row in selected if str(row["tool"]) == heldout_tool]
        train = evaluate_regime(train_rows)
        covered_test, test_skills, atest = support_matrix(test_rows)
        method_rows: list[dict[str, Any]] = []
        for method in train["baselines"]:
            name = str(method["baseline"])
            if name == "semantic_first_upper_bound":
                method_rows.append({
                    "baseline": name,
                    "train_distortion_ratio": 1.0,
                    "heldout_distortion_ratio": 1.0,
                    "heldout_coefficient_of_variation": None,
                    "zero_exposure_rows": 0,
                    "interface_changing": True,
                })
                continue
            weights = _align_weights(train["skills"], method["weights"], test_skills)
            metrics = _scale_invariant_metrics(atest, weights)
            method_rows.append({
                "baseline": name,
                "train_distortion_ratio": _finite_or_none(method["metrics"].get("distortion_ratio")),
                "heldout_distortion_ratio": _finite_or_none(metrics.get("distortion_ratio")),
                "heldout_coefficient_of_variation": _finite_or_none(metrics.get("coefficient_of_variation")),
                "zero_exposure_rows": int(metrics.get("zero_exposure_rows") or 0),
                "weights_frozen_from_train": {skill: float(weights[i]) for i, skill in enumerate(test_skills)},
                "interface_changing": False,
            })
        folds.append({
            "heldout_tool": heldout_tool,
            "train_tools": [tool for tool in tools if tool != heldout_tool],
            "train_rows": len(train_rows),
            "heldout_rows": len(covered_test),
            "train_packages": len(train["skills"]),
            "heldout_packages": len(test_skills),
            "no_heldout_refit": True,
            "results": method_rows,
        })

    baselines = sorted({row["baseline"] for fold in folds for row in fold["results"]})
    aggregate: list[dict[str, Any]] = []
    for baseline in baselines:
        rows = [next(row for row in fold["results"] if row["baseline"] == baseline) for fold in folds]
        finite = [float(row["heldout_distortion_ratio"]) for row in rows if row["heldout_distortion_ratio"] is not None]
        aggregate.append({
            "baseline": baseline,
            "folds": len(rows),
            "finite_folds": len(finite),
            "zero_exposure_folds": sum(int(row["zero_exposure_rows"] > 0) for row in rows),
            "heldout_ratio_median": float(np.median(finite)) if finite else None,
            "heldout_ratio_mean": float(np.mean(finite)) if finite else None,
            "heldout_ratio_max": float(np.max(finite)) if finite else None,
            "heldout_ratio_min": float(np.min(finite)) if finite else None,
        })
    return {
        "split_id": split.get("split_id"),
        "selected_tools": tools,
        "selected_rows": len(selected),
        "folds": folds,
        "aggregate": aggregate,
        "selection_reads_outcomes": False,
        "no_heldout_refit": True,
    }


def _rstar_for_subset(A: np.ndarray, subset: tuple[int, ...]) -> tuple[float | None, np.ndarray | None]:
    if not subset:
        return None, None
    sub = A[:, subset]
    if np.any(sub.sum(axis=1) <= 0):
        return None, None
    m = len(subset)
    c = np.r_[np.zeros(m), 1.0]
    aub: list[np.ndarray] = []
    bub: list[float] = []
    for row in sub:
        aub.append(np.r_[-row, 0.0]); bub.append(-1.0)
        aub.append(np.r_[row, -1.0]); bub.append(0.0)
    result = linprog(
        c,
        A_ub=np.asarray(aub),
        b_ub=np.asarray(bub),
        bounds=[(0, None)] * m + [(0, None)],
        method="highs",
    )
    if not result.success:
        return None, None
    return float(result.x[-1]), np.asarray(result.x[:m], dtype=float)


def exact_sparsity_frontier(rows: list[dict[str, Any]]) -> dict[str, Any]:
    covered, skills, A = support_matrix(rows)
    if not covered:
        raise ValueError("regime has no covered rows")
    frontier: list[dict[str, Any]] = []
    for budget in range(1, len(skills) + 1):
        best_ratio: float | None = None
        best_subset: tuple[int, ...] | None = None
        best_weights: np.ndarray | None = None
        feasible_subsets = 0
        enumerated_subsets = 0
        for size in range(1, budget + 1):
            for subset in itertools.combinations(range(len(skills)), size):
                enumerated_subsets += 1
                ratio, weights = _rstar_for_subset(A, subset)
                if ratio is None or weights is None:
                    continue
                feasible_subsets += 1
                candidate_key = (ratio, len(subset), tuple(skills[i] for i in subset))
                best_key = (
                    best_ratio if best_ratio is not None else float("inf"),
                    len(best_subset) if best_subset is not None else 10**9,
                    tuple(skills[i] for i in best_subset) if best_subset is not None else tuple(),
                )
                if best_subset is None or candidate_key < best_key:
                    best_ratio, best_subset, best_weights = ratio, subset, weights
        if best_subset is None or best_weights is None:
            frontier.append({
                "active_package_budget": budget,
                "feasible": False,
                "best_R_star": None,
                "best_subset": [],
                "active_packages": 0,
                "enumerated_subsets": enumerated_subsets,
                "feasible_subsets": feasible_subsets,
            })
            continue
        full_weights = np.zeros(len(skills), dtype=float)
        for local, global_idx in enumerate(best_subset):
            full_weights[global_idx] = best_weights[local]
        frontier.append({
            "active_package_budget": budget,
            "feasible": True,
            "best_R_star": float(best_ratio),
            "best_subset": [skills[i] for i in best_subset],
            "active_packages": len(best_subset),
            "enumerated_subsets": enumerated_subsets,
            "feasible_subsets": feasible_subsets,
            "metrics": _scale_invariant_metrics(A, full_weights),
            "weights": {skills[i]: float(full_weights[i]) for i in range(len(skills)) if full_weights[i] > 1e-12},
        })
    first_feasible = next((row for row in frontier if row["feasible"]), None)
    unrestricted = frontier[-1]
    first_optimal = next(
        (
            row
            for row in frontier
            if row["feasible"]
            and unrestricted["best_R_star"] is not None
            and abs(float(row["best_R_star"]) - float(unrestricted["best_R_star"])) <= 1e-9
        ),
        None,
    )
    return {
        "covered_rows": len(covered),
        "packages": len(skills),
        "skills": skills,
        "frontier": frontier,
        "minimum_feasible_active_packages": int(first_feasible["active_packages"]) if first_feasible else None,
        "unrestricted_R_star": unrestricted.get("best_R_star"),
        "minimum_active_packages_attaining_unrestricted_R_star": int(first_optimal["active_packages"]) if first_optimal else None,
    }


def build_from_rows(
    tool_rows: list[dict[str, Any]],
    logical_rows: list[dict[str, Any]],
    split: dict[str, Any],
    *,
    input_label: str = "packaged-data",
) -> dict[str, Any]:
    regimes = regimes_from_rows(tool_rows, logical_rows, split)
    loo = leave_one_tool_out_transfer(tool_rows, split)
    sparsity = {name: exact_sparsity_frontier(rows) for name, rows in regimes.items()}
    by_name = {row["baseline"]: row for row in loo["aggregate"]}
    l1 = sparsity["skillsp_l1_full"]
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis": "cross-validation-and-exact-controller-sparsity-frontier",
        "input_supplement": input_label,
        "input_split": input_label,
        "new_model_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "leave_one_tool_out": loo,
        "sparsity_frontiers": sparsity,
        "headline": {
            "leave_one_tool_out_folds": len(loo["folds"]),
            "exact_rstar_heldout_ratio_median": by_name["exact_rstar"]["heldout_ratio_median"],
            "exact_rstar_heldout_ratio_max": by_name["exact_rstar"]["heldout_ratio_max"],
            "uniform_heldout_ratio_median": by_name["released_uniform"]["heldout_ratio_median"],
            "uniform_heldout_ratio_max": by_name["released_uniform"]["heldout_ratio_max"],
            "nnls_heldout_ratio_median": by_name["nnls_l2"]["heldout_ratio_median"],
            "nnls_heldout_ratio_max": by_name["nnls_l2"]["heldout_ratio_max"],
            "l1_minimum_feasible_active_packages": l1["minimum_feasible_active_packages"],
            "l1_minimum_active_packages_attaining_unrestricted_R_star": l1["minimum_active_packages_attaining_unrestricted_R_star"],
            "l1_unrestricted_R_star": l1["unrestricted_R_star"],
        },
        "scientific_boundary": "All folds and sparsity subsets are determined from frozen released support before evaluating heldout distortion. Leave-one-tool-out freezes weights without heldout refitting. Sparsity frontiers enumerate exact package subsets and optimize only the neutral support objective; neither experiment claims task utility or a learned deployment policy.",
    }


def build(
    supplement: Path = DEFAULT_SUPPLEMENT,
    split_path: Path = DEFAULT_SPLIT,
) -> dict[str, Any]:
    tool_rows = _jsonl_from_zip(supplement, "data/skillsp-toolcall-membership.jsonl")
    logical_rows = _jsonl_from_zip(supplement, "data/skillsp-logical-support-matrix.jsonl")
    split = json.loads(split_path.read_text(encoding="utf-8"))
    return build_from_rows(tool_rows, logical_rows, split, input_label=f"{supplement} | {split_path}")


def write_outputs(payload: dict[str, Any], json_path: Path = DEFAULT_JSON, csv_path: Path = DEFAULT_CSV) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = [
        "experiment", "regime", "fold_or_budget", "baseline", "train_rows", "heldout_rows",
        "distortion_ratio", "ratio_median", "ratio_max", "feasible", "active_packages",
        "best_subset", "zero_exposure_rows",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for fold in payload["leave_one_tool_out"]["folds"]:
            for row in fold["results"]:
                writer.writerow({
                    "experiment": "leave_one_tool_out",
                    "regime": "skillsp_l1_selected_tools",
                    "fold_or_budget": fold["heldout_tool"],
                    "baseline": row["baseline"],
                    "train_rows": fold["train_rows"],
                    "heldout_rows": fold["heldout_rows"],
                    "distortion_ratio": row["heldout_distortion_ratio"],
                    "zero_exposure_rows": row["zero_exposure_rows"],
                })
        for row in payload["leave_one_tool_out"]["aggregate"]:
            writer.writerow({
                "experiment": "leave_one_tool_out_aggregate",
                "regime": "skillsp_l1_selected_tools",
                "baseline": row["baseline"],
                "ratio_median": row["heldout_ratio_median"],
                "ratio_max": row["heldout_ratio_max"],
                "zero_exposure_rows": row["zero_exposure_folds"],
            })
        for regime, block in payload["sparsity_frontiers"].items():
            for row in block["frontier"]:
                writer.writerow({
                    "experiment": "exact_sparsity_frontier",
                    "regime": regime,
                    "fold_or_budget": row["active_package_budget"],
                    "distortion_ratio": row["best_R_star"],
                    "feasible": row["feasible"],
                    "active_packages": row["active_packages"],
                    "best_subset": ";".join(row["best_subset"]),
                    "zero_exposure_rows": (row.get("metrics") or {}).get("zero_exposure_rows"),
                })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--supplement", type=Path, default=DEFAULT_SUPPLEMENT)
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    payload = build(args.supplement, args.split)
    write_outputs(payload, args.json, args.csv)
    print(json.dumps({"headline": payload["headline"], "json": str(args.json), "csv": str(args.csv)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
