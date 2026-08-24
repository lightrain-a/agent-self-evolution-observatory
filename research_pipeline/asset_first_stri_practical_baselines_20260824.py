from __future__ import annotations

import argparse
import csv
import io
import json
import math
import zipfile
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp, nnls

from .asset_first_stri_certificate import optimal_target_package_ratio, semantic_first_construction, support_matrix

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUPPLEMENT = ROOT / "downloads" / "STRI-ICLR2027-supplement.zip"
DEFAULT_SPLIT = ROOT / "generated" / "asset-first-stri-tool-disjoint-split-20260816.json"
DEFAULT_JSON = ROOT / "generated" / "asset-first-stri-practical-baselines-20260824.json"
DEFAULT_CSV = ROOT / "generated" / "asset-first-stri-practical-baselines-20260824.csv"


def _jsonl_from_zip(path: Path, member: str) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as zf:
        return [json.loads(line) for line in zf.read(member).decode("utf-8").splitlines() if line.strip()]


def regimes_from_rows(tool_rows: list[dict[str, Any]], logical: list[dict[str, Any]], split: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_id = {f"L{row['level']}:{row['index']}:{row['tool']}": row for row in tool_rows}
    return {
        "skillsp_l1_full": [row for row in tool_rows if int(row.get("level") or -1) == 1],
        "skillsp_l1_calibration": [by_id[row_id] for row_id in split["partitions"]["calibration"]["row_ids"]],
        "skillsp_l1_heldout": [by_id[row_id] for row_id in split["partitions"]["heldout"]["row_ids"]],
        "skillsp_l3": [row for row in tool_rows if int(row.get("level") or -1) == 3],
        "logical_compiler": logical,
    }


def load_regimes(supplement: Path = DEFAULT_SUPPLEMENT, split_path: Path = DEFAULT_SPLIT) -> dict[str, list[dict[str, Any]]]:
    tool_rows = _jsonl_from_zip(supplement, "data/skillsp-toolcall-membership.jsonl")
    logical = _jsonl_from_zip(supplement, "data/skillsp-logical-support-matrix.jsonl")
    split = json.loads(split_path.read_text(encoding="utf-8"))
    return regimes_from_rows(tool_rows, logical, split)


def _scale_invariant_metrics(A: np.ndarray, w: np.ndarray, q: np.ndarray | None = None) -> dict[str, Any]:
    q = np.ones(A.shape[0], dtype=float) if q is None else np.asarray(q, dtype=float)
    w = np.asarray(w, dtype=float)
    exposure = A @ w
    relative = exposure / q
    minimum = float(relative.min()) if len(relative) else 0.0
    maximum = float(relative.max()) if len(relative) else 0.0
    ratio = float("inf") if minimum <= 1e-12 else maximum / minimum
    mean = float(relative.mean()) if len(relative) else 0.0
    cv = float(relative.std() / mean) if mean > 1e-12 else float("inf")
    if float(np.dot(relative, relative)) > 1e-15:
        scale = float(np.dot(relative, np.ones_like(relative)) / np.dot(relative, relative))
        fitted = scale * relative
        rmse = float(np.sqrt(np.mean((fitted - 1.0) ** 2)))
        max_abs = float(np.max(np.abs(fitted - 1.0)))
    else:
        scale, rmse, max_abs = 0.0, float("inf"), float("inf")
    total = float(w.sum())
    if total > 1e-12:
        p = w / total
        max_share = float(p.max())
        effective = float(1.0 / np.dot(p, p))
    else:
        max_share, effective = None, 0.0
    return {
        "distortion_ratio": ratio,
        "minimum_relative_exposure": minimum,
        "maximum_relative_exposure": maximum,
        "coefficient_of_variation": cv,
        "best_scale_rmse": rmse,
        "best_scale_max_abs_error": max_abs,
        "active_packages": int(np.sum(w > 1e-9)),
        "max_package_share": max_share,
        "effective_package_count": effective,
        "zero_exposure_rows": int(np.sum(relative <= 1e-12)),
    }


def _uniform(A: np.ndarray) -> np.ndarray:
    return np.ones(A.shape[1], dtype=float)


def _inverse_support(A: np.ndarray, power: float) -> np.ndarray:
    coverage = A.sum(axis=0)
    return np.where(coverage > 0, coverage ** (-power), 0.0)


def _fractional_load_inverse(A: np.ndarray) -> np.ndarray:
    degree = A.sum(axis=1)
    fractional_load = (A / degree[:, None]).sum(axis=0)
    return np.where(fractional_load > 0, 1.0 / fractional_load, 0.0)


def _nnls(A: np.ndarray) -> np.ndarray:
    return nnls(A, np.ones(A.shape[0], dtype=float))[0]


def _chebyshev(A: np.ndarray) -> np.ndarray:
    m = A.shape[1]
    c = np.r_[np.zeros(m), 1.0]
    aub, bub = [], []
    for row in A:
        aub.append(np.r_[row, -1.0]); bub.append(1.0)
        aub.append(np.r_[-row, -1.0]); bub.append(-1.0)
    result = linprog(c, A_ub=np.asarray(aub), b_ub=np.asarray(bub), bounds=[(0, None)] * m + [(0, None)], method="highs")
    if not result.success:
        raise RuntimeError(result.message)
    return result.x[:m]


def _maxmin_fair(A: np.ndarray) -> np.ndarray:
    m = A.shape[1]
    c = np.r_[np.zeros(m), -1.0]
    aub = np.asarray([np.r_[-row, 1.0] for row in A])
    beq = np.asarray([1.0])
    aeq = np.asarray([np.r_[np.ones(m), 0.0]])
    result = linprog(c, A_ub=aub, b_ub=np.zeros(A.shape[0]), A_eq=aeq, b_eq=beq, bounds=[(0, None)] * m + [(None, None)], method="highs")
    if not result.success:
        raise RuntimeError(result.message)
    return result.x[:m]


def _greedy_cover(A: np.ndarray) -> np.ndarray:
    uncovered = set(range(A.shape[0])); selected: list[int] = []
    while uncovered:
        scores = [(sum(A[i, j] > 0 for i in uncovered), -j, j) for j in range(A.shape[1])]
        count, _, best = max(scores)
        if count <= 0:
            raise RuntimeError("greedy cover encountered uncovered row")
        selected.append(best)
        uncovered -= {i for i in uncovered if A[i, best] > 0}
    w = np.zeros(A.shape[1], dtype=float); w[selected] = 1.0
    return w


def _exact_min_cover(A: np.ndarray) -> np.ndarray:
    m = A.shape[1]
    result = milp(
        np.ones(m), integrality=np.ones(m), bounds=Bounds(np.zeros(m), np.ones(m)),
        constraints=LinearConstraint(A, lb=np.ones(A.shape[0]), ub=np.full(A.shape[0], np.inf)),
        options={"disp": False},
    )
    if not result.success:
        raise RuntimeError(str(result.message))
    return (result.x > 0.5).astype(float)


def _exact_rstar(rows: list[dict[str, Any]], skills: list[str]) -> np.ndarray:
    result = optimal_target_package_ratio(rows)
    if not result.get("pass"):
        raise RuntimeError(str(result.get("reason")))
    return np.asarray([float((result.get("weights") or {}).get(skill, 0.0)) for skill in skills], dtype=float)


def evaluate_regime(rows: list[dict[str, Any]]) -> dict[str, Any]:
    covered, skills, A = support_matrix(rows)
    if not covered:
        raise ValueError("regime has no covered rows")
    methods: list[tuple[str, Callable[[], np.ndarray], str]] = [
        ("released_uniform", lambda: _uniform(A), "released-style package-uniform routing"),
        ("inverse_support_size", lambda: _inverse_support(A, 1.0), "inverse column coverage heuristic"),
        ("inverse_sqrt_support", lambda: _inverse_support(A, 0.5), "tempered inverse column coverage heuristic"),
        ("fractional_load_inverse", lambda: _fractional_load_inverse(A), "inverse fractional responsibility heuristic"),
        ("nnls_l2", lambda: _nnls(A), "nonnegative least-squares fit to neutral target"),
        ("chebyshev_linf", lambda: _chebyshev(A), "minimum absolute L-infinity target fit"),
        ("greedy_cover_uniform", lambda: _greedy_cover(A), "greedy set-cover then uniform routing"),
        ("exact_min_cover_uniform", lambda: _exact_min_cover(A), "exact minimum set-cover then uniform routing"),
        ("maxmin_fair", lambda: _maxmin_fair(A), "max-min exposure under unit package mass"),
        ("exact_rstar", lambda: _exact_rstar(rows, skills), "STRI exact worst-case multiplicative optimum"),
    ]
    out = []
    for name, build, description in methods:
        w = build()
        metrics = _scale_invariant_metrics(A, w)
        out.append({
            "baseline": name,
            "description": description,
            "metrics": metrics,
            "weights": {skill: float(w[i]) for i, skill in enumerate(skills)},
        })
    semantic = semantic_first_construction(rows)
    out.append({
        "baseline": "semantic_first_upper_bound",
        "description": "interface-changing semantic-first construction; not a package-only baseline",
        "metrics": {
            "distortion_ratio": 1.0,
            "maximum_semantic_marginal_error": float(semantic.get("maximum_semantic_marginal_error") or 0.0),
            "support_violation_mass": float(semantic.get("support_violation_mass") or 0.0),
        },
        "weights": {},
    })
    exact = next(row for row in out if row["baseline"] == "exact_rstar")
    return {
        "covered_rows": len(covered),
        "packages": len(skills),
        "skills": skills,
        "multi_membership_rows": int(np.sum(A.sum(axis=1) > 1)),
        "exact_R_star": exact["metrics"]["distortion_ratio"],
        "baselines": out,
    }


def _align_weights(train_skills: list[str], weights: dict[str, float], test_skills: list[str]) -> np.ndarray:
    return np.asarray([float(weights.get(skill, 0.0)) for skill in test_skills], dtype=float)


def calibration_to_heldout(calibration: list[dict[str, Any]], heldout: list[dict[str, Any]]) -> dict[str, Any]:
    train = evaluate_regime(calibration)
    covered_test, test_skills, Atest = support_matrix(heldout)
    rows = []
    for method in train["baselines"]:
        if method["baseline"] == "semantic_first_upper_bound":
            rows.append({"baseline": method["baseline"], "heldout_metrics": {"distortion_ratio": 1.0}, "note": "interface-changing upper bound"})
            continue
        w = _align_weights(train["skills"], method["weights"], test_skills)
        rows.append({
            "baseline": method["baseline"],
            "calibration_metrics": method["metrics"],
            "heldout_metrics": _scale_invariant_metrics(Atest, w),
            "weights_frozen_from_calibration": {skill: float(w[i]) for i, skill in enumerate(test_skills)},
        })
    return {
        "train_regime": "skillsp_l1_calibration",
        "test_regime": "skillsp_l1_heldout",
        "train_rows": train["covered_rows"],
        "test_rows": len(covered_test),
        "train_skills": train["skills"],
        "test_skills": test_skills,
        "no_heldout_refit": True,
        "results": rows,
    }


def build_from_regimes(regimes: dict[str, list[dict[str, Any]]], *, input_supplement: str, input_split: str) -> dict[str, Any]:
    evaluated = {name: evaluate_regime(rows) for name, rows in regimes.items()}
    transfer = calibration_to_heldout(regimes["skillsp_l1_calibration"], regimes["skillsp_l1_heldout"])
    l1 = evaluated["skillsp_l1_full"]
    by_name = {row["baseline"]: row for row in l1["baselines"]}
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis": "practical-baseline-suite",
        "input_supplement": input_supplement,
        "input_split": input_split,
        "new_model_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "regimes": evaluated,
        "calibration_to_heldout": transfer,
        "headline": {
            "level1_exact_R_star": l1["exact_R_star"],
            "level1_uniform_ratio": by_name["released_uniform"]["metrics"]["distortion_ratio"],
            "level1_inverse_support_ratio": by_name["inverse_support_size"]["metrics"]["distortion_ratio"],
            "level1_inverse_sqrt_ratio": by_name["inverse_sqrt_support"]["metrics"]["distortion_ratio"],
            "level1_nnls_ratio": by_name["nnls_l2"]["metrics"]["distortion_ratio"],
            "level1_nnls_cv": by_name["nnls_l2"]["metrics"]["coefficient_of_variation"],
            "level1_uniform_cv": by_name["released_uniform"]["metrics"]["coefficient_of_variation"],
            "interpretation": "Uniform routing already attains the exact Level-1 worst-case optimum R*=2, so the residual is not poor tuning. Mean-error and inverse-coverage heuristics can improve a different objective or intuitively debias broad packages while substantially worsening worst-case representation distortion.",
        },
        "scientific_boundary": "All rows are frozen released/programmatic support data. Semantic-first is an interface-changing upper bound, not a validated repair. Calibration-to-heldout freezes weights before opening heldout evaluation and does not claim downstream task utility.",
    }


def build_from_rows(tool_rows: list[dict[str, Any]], logical_rows: list[dict[str, Any]], split: dict[str, Any], *, input_label: str = "packaged-data") -> dict[str, Any]:
    return build_from_regimes(regimes_from_rows(tool_rows, logical_rows, split), input_supplement=input_label, input_split=input_label)


def build(supplement: Path = DEFAULT_SUPPLEMENT, split_path: Path = DEFAULT_SPLIT) -> dict[str, Any]:
    return build_from_regimes(load_regimes(supplement, split_path), input_supplement=str(supplement), input_split=str(split_path))


def write_outputs(payload: dict[str, Any], json_path: Path = DEFAULT_JSON, csv_path: Path = DEFAULT_CSV) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["experiment", "regime", "baseline", "covered_rows", "packages", "distortion_ratio", "coefficient_of_variation", "best_scale_rmse", "max_package_share", "effective_package_count", "active_packages", "zero_exposure_rows"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for regime, block in payload["regimes"].items():
            for row in block["baselines"]:
                m = row["metrics"]
                writer.writerow({
                    "experiment": "within_regime", "regime": regime, "baseline": row["baseline"],
                    "covered_rows": block["covered_rows"], "packages": block["packages"],
                    "distortion_ratio": m.get("distortion_ratio"), "coefficient_of_variation": m.get("coefficient_of_variation"),
                    "best_scale_rmse": m.get("best_scale_rmse"), "max_package_share": m.get("max_package_share"),
                    "effective_package_count": m.get("effective_package_count"), "active_packages": m.get("active_packages"),
                    "zero_exposure_rows": m.get("zero_exposure_rows"),
                })
        for row in payload["calibration_to_heldout"]["results"]:
            m = row["heldout_metrics"]
            writer.writerow({
                "experiment": "calibration_to_heldout", "regime": "skillsp_l1_heldout", "baseline": row["baseline"],
                "covered_rows": payload["calibration_to_heldout"]["test_rows"], "packages": len(payload["calibration_to_heldout"]["test_skills"]),
                "distortion_ratio": m.get("distortion_ratio"), "coefficient_of_variation": m.get("coefficient_of_variation"),
                "best_scale_rmse": m.get("best_scale_rmse"), "max_package_share": m.get("max_package_share"),
                "effective_package_count": m.get("effective_package_count"), "active_packages": m.get("active_packages"),
                "zero_exposure_rows": m.get("zero_exposure_rows"),
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
