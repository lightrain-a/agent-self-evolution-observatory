from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path


SCHEMA_VERSION = "behavior-formal-goal-coupling-demo-horizon-result-v1"
OBJECT_ID = "SUCC-C-BEHAVIOR2026-DEMO-HORIZON"
EXPOSED_TASK_INDICES = {0}
EXPECTED_EPISODES_PER_TASK = 200
DEFAULT_PERMUTATIONS = 100_000
DEFAULT_PERMUTATION_SEED = 20260831


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_structure(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows") or []
    if len(rows) != 100:
        raise ValueError(f"expected 100 challenge structure rows, got {len(rows)}")
    required = {
        "activity",
        "atomic_goal_count",
        "shared_argument_edge_count",
        "goal_logic_depth",
        "branch_operator_count",
        "quantifier_count",
    }
    for i, row in enumerate(rows):
        missing = sorted(required - set(row))
        if missing:
            raise ValueError(f"structure row {i} missing {missing}")
    return rows


def frozen_matched_pairs(structure_rows: list[dict], n_pairs: int = 16) -> list[dict]:
    candidates: list[tuple] = []
    for i, a in enumerate(structure_rows):
        if i in EXPOSED_TASK_INDICES:
            continue
        for j in range(i + 1, len(structure_rows)):
            if j in EXPOSED_TASK_INDICES:
                continue
            b = structure_rows[j]
            if a["atomic_goal_count"] != b["atomic_goal_count"]:
                continue
            if a["branch_operator_count"] != b["branch_operator_count"]:
                continue
            depth_diff = abs(int(a["goal_logic_depth"]) - int(b["goal_logic_depth"]))
            if depth_diff > 1:
                continue
            edge_a = int(a["shared_argument_edge_count"])
            edge_b = int(b["shared_argument_edge_count"])
            gap = abs(edge_a - edge_b)
            if gap <= 0:
                continue
            qdiff = abs(int(a["quantifier_count"]) - int(b["quantifier_count"]))
            score = 10 * gap - qdiff - 2 * depth_diff
            if edge_a < edge_b:
                lo_idx, lo, hi_idx, hi = i, a, j, b
            else:
                lo_idx, lo, hi_idx, hi = j, b, i, a
            candidates.append(
                (
                    score,
                    gap,
                    -qdiff,
                    str(lo["activity"]),
                    str(hi["activity"]),
                    lo_idx,
                    hi_idx,
                    lo,
                    hi,
                )
            )

    used: set[int] = set()
    selected: list[dict] = []
    ordered = sorted(
        candidates,
        key=lambda row: (row[0], row[1], row[2], row[3], row[4], row[5], row[6]),
        reverse=True,
    )
    for score, gap, neg_qdiff, _, _, lo_idx, hi_idx, lo, hi in ordered:
        if lo_idx in used or hi_idx in used:
            continue
        selected.append(
            {
                "pair_id": len(selected) + 1,
                "low_task_index": lo_idx,
                "high_task_index": hi_idx,
                "atomic_goal_count": int(lo["atomic_goal_count"]),
                "branch_operator_count": int(lo["branch_operator_count"]),
                "low_activity": str(lo["activity"]),
                "high_activity": str(hi["activity"]),
                "low_edge": int(lo["shared_argument_edge_count"]),
                "high_edge": int(hi["shared_argument_edge_count"]),
                "edge_gap": int(gap),
                "low_goal_logic_depth": int(lo["goal_logic_depth"]),
                "high_goal_logic_depth": int(hi["goal_logic_depth"]),
                "low_quantifier_count": int(lo["quantifier_count"]),
                "high_quantifier_count": int(hi["quantifier_count"]),
                "selection_score": int(score),
                "quantifier_difference": int(-neg_qdiff),
            }
        )
        used.update((lo_idx, hi_idx))
        if len(selected) == n_pairs:
            break
    if len(selected) != n_pairs:
        raise ValueError(f"could only construct {len(selected)} frozen matched pairs")
    return selected


def _read_episode_lengths(path: Path, expected_task_index: int) -> list[int]:
    try:
        import pyarrow.parquet as pq
    except Exception as exc:  # pragma: no cover - dependency is an execution preflight
        raise RuntimeError("pyarrow is required to read frozen episode metadata") from exc

    table = pq.read_table(path, columns=["episode_index", "task_index", "length"])
    data = table.to_pydict()
    episode_indices = [int(x) for x in data["episode_index"]]
    task_indices = [int(x) for x in data["task_index"]]
    lengths = [int(x) for x in data["length"]]
    if len(lengths) != EXPECTED_EPISODES_PER_TASK:
        raise ValueError(f"{path}: expected {EXPECTED_EPISODES_PER_TASK} episodes, got {len(lengths)}")
    if sorted(episode_indices) != list(range(EXPECTED_EPISODES_PER_TASK)):
        raise ValueError(f"{path}: episode_index is not exactly 0..199")
    if set(task_indices) != {expected_task_index}:
        raise ValueError(f"{path}: task_index set {sorted(set(task_indices))} != {{{expected_task_index}}}")
    if any(x <= 0 for x in lengths):
        raise ValueError(f"{path}: non-positive episode length")
    return lengths


def load_task_outcomes(metadata_root: Path, structure_rows: list[dict]) -> list[dict]:
    outcomes: list[dict] = []
    for task_index, structure in enumerate(structure_rows):
        if task_index in EXPOSED_TASK_INDICES:
            continue
        path = metadata_root / f"chunk-{task_index:03d}" / "file-000.parquet"
        if not path.is_file():
            raise FileNotFoundError(path)
        lengths = _read_episode_lengths(path, task_index)
        median_frames = float(statistics.median(lengths))
        outcomes.append(
            {
                "task_index": task_index,
                "activity": structure["activity"],
                "atomic_goal_count": int(structure["atomic_goal_count"]),
                "shared_argument_edge_count": int(structure["shared_argument_edge_count"]),
                "branch_operator_count": int(structure["branch_operator_count"]),
                "median_episode_length_frames": median_frames,
                "log_median_episode_length_frames": math.log(median_frames),
                "episode_count": len(lengths),
                "metadata_path": str(path),
                "metadata_sha256": sha256_file(path),
            }
        )
    if len(outcomes) != 99:
        raise ValueError(f"expected 99 fresh task outcomes, got {len(outcomes)}")
    return outcomes


def _strata(outcomes: list[dict]) -> dict[int, list[dict]]:
    groups: dict[int, list[dict]] = defaultdict(list)
    for row in outcomes:
        groups[int(row["atomic_goal_count"])].append(row)
    return dict(sorted(groups.items()))


def _within_stratum_beta(outcomes: list[dict], y_values: list[float] | None = None) -> float:
    if y_values is not None and len(y_values) != len(outcomes):
        raise ValueError("y override length mismatch")
    enriched = []
    for i, row in enumerate(outcomes):
        enriched.append(
            {
                "group": int(row["atomic_goal_count"]),
                "x": float(row["shared_argument_edge_count"]),
                "y": float(row["log_median_episode_length_frames"] if y_values is None else y_values[i]),
            }
        )
    groups: dict[int, list[dict]] = defaultdict(list)
    for row in enriched:
        groups[row["group"]].append(row)
    numerator = 0.0
    denominator = 0.0
    for rows in groups.values():
        xbar = sum(r["x"] for r in rows) / len(rows)
        ybar = sum(r["y"] for r in rows) / len(rows)
        for row in rows:
            xw = row["x"] - xbar
            yw = row["y"] - ybar
            numerator += xw * yw
            denominator += xw * xw
    if denominator <= 0.0:
        raise ValueError("no within-atomic-goal-count edge variation")
    return numerator / denominator


def fixed_effect_edge_fit(outcomes: list[dict]) -> dict:
    groups = _strata(outcomes)
    return {
        "beta_edge": float(_within_stratum_beta(outcomes)),
        "estimator": "Frisch-Waugh-Lovell within-stratum slope with exact atomic_goal_count fixed effects",
        "atomic_goal_count_fixed_effect_levels": sorted(groups),
        "stratum_sizes": {str(k): len(v) for k, v in groups.items()},
        "n_tasks": len(outcomes),
    }


def stratified_permutation_pvalue(
    outcomes: list[dict],
    *,
    permutations: int = DEFAULT_PERMUTATIONS,
    seed: int = DEFAULT_PERMUTATION_SEED,
) -> dict:
    observed = float(_within_stratum_beta(outcomes))
    groups: dict[int, list[int]] = defaultdict(list)
    for i, row in enumerate(outcomes):
        groups[int(row["atomic_goal_count"])].append(i)
    base_y = [float(r["log_median_episode_length_frames"]) for r in outcomes]
    rng = random.Random(seed)
    extreme = 0
    for _ in range(permutations):
        permuted = list(base_y)
        for indices in groups.values():
            values = [base_y[i] for i in indices]
            rng.shuffle(values)
            for i, value in zip(indices, values):
                permuted[i] = value
        beta = float(_within_stratum_beta(outcomes, permuted))
        if abs(beta) >= abs(observed) - 1e-15:
            extreme += 1
    return {
        "observed_beta_edge": observed,
        "permutations": permutations,
        "seed": seed,
        "two_sided_p": (extreme + 1.0) / (permutations + 1.0),
        "permutation_scope": "shuffle log task-median episode length only within exact atomic_goal_count strata",
    }


def matched_pair_corroboration(outcomes: list[dict], pairs: list[dict]) -> dict:
    by_index = {int(r["task_index"]): r for r in outcomes}
    rows = []
    for pair in pairs:
        low = by_index[int(pair["low_task_index"])]
        high = by_index[int(pair["high_task_index"])]
        delta = float(high["log_median_episode_length_frames"] - low["log_median_episode_length_frames"])
        rows.append({**pair, "high_minus_low_log_median_frames": delta})
    deltas = [float(r["high_minus_low_log_median_frames"]) for r in rows]
    return {
        "pair_count": len(rows),
        "mean_high_minus_low_log_median_frames": float(statistics.fmean(deltas)),
        "median_high_minus_low_log_median_frames": float(statistics.median(deltas)),
        "positive_pair_count": sum(1 for x in deltas if x > 0),
        "negative_pair_count": sum(1 for x in deltas if x < 0),
        "zero_pair_count": sum(1 for x in deltas if x == 0),
        "pairs": rows,
    }


def analyze(
    structure_path: Path,
    metadata_root: Path,
    prereg_path: Path,
    *,
    permutations: int = DEFAULT_PERMUTATIONS,
    seed: int = DEFAULT_PERMUTATION_SEED,
) -> dict:
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    if prereg.get("object_id") != OBJECT_ID:
        raise ValueError("preregistration object identity mismatch")
    if prereg.get("status") != "PREREGISTERED_BEFORE_FRESH_TASK_METADATA_ACCESS":
        raise ValueError("preregistration status mismatch")
    structure_rows = load_structure(structure_path)
    pairs = frozen_matched_pairs(structure_rows, int(prereg["matched_pair_corroboration"]["pair_count"]))
    expected_pairs = prereg["matched_pair_corroboration"]["pairs"]
    if pairs != expected_pairs:
        raise ValueError("frozen matched pair panel drift")
    outcomes = load_task_outcomes(metadata_root, structure_rows)
    fit = fixed_effect_edge_fit(outcomes)
    perm = stratified_permutation_pvalue(outcomes, permutations=permutations, seed=seed)
    pair_result = matched_pair_corroboration(outcomes, pairs)
    pass_primary = bool(fit["beta_edge"] > 0.0 and perm["two_sided_p"] < 0.05)
    return {
        "schema_version": SCHEMA_VERSION,
        "object_id": OBJECT_ID,
        "status": "DEMO_HORIZON_PRIMARY_SUPPORT" if pass_primary else "DEMO_HORIZON_PRIMARY_NOT_SUPPORTED",
        "scientific_scope": "fresh 99-task human-demonstration-horizon construct/mechanism lane only; never a rescue of BEHAVIOR policy-Q confirmatory objects",
        "parent_port010_reopen_authorized": False,
        "policy_outcomes_read": False,
        "model_loaded": False,
        "gpu_used": False,
        "excluded_exposed_task_indices": sorted(EXPOSED_TASK_INDICES),
        "structure_source": {"path": str(structure_path), "sha256": sha256_file(structure_path)},
        "preregistration": {"path": str(prereg_path), "sha256": sha256_file(prereg_path)},
        "primary": {**fit, **perm, "direction_required": "beta_edge > 0", "pass": pass_primary},
        "matched_pair_corroboration": pair_result,
        "task_rows": outcomes,
        "does_not_imply": [
            "that formal goal coupling causes longer demonstrations",
            "that BEHAVIOR policy Q is lower for more coupled tasks",
            "that the frozen 2026 public-outcome preregistration may use human demo duration",
            "that the frozen three-policy local replication gate may be lowered",
            "that PORT-010 may reopen",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="One-shot fresh-task human-demo horizon analysis for formal goal coupling")
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--metadata-root", type=Path, required=True)
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--permutations", type=int, default=DEFAULT_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=DEFAULT_PERMUTATION_SEED)
    args = parser.parse_args()
    result = analyze(args.structure, args.metadata_root, args.prereg, permutations=args.permutations, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "primary": result["primary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
