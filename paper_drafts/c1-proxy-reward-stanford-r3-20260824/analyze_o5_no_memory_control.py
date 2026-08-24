#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

FUTURE_TASKS = ["164", "385", "387", "388"]
SOURCE_TASKS = ["21", "22", "23", "25"]
N_PER_FUTURE = 8
Z_95 = 1.959963984540054


def load(path: Path):
    return json.loads(path.read_text())


def wilson(successes: int, n: int, z: float = Z_95) -> tuple[float, float]:
    if n <= 0:
        raise ValueError("Wilson interval requires n > 0")
    p = successes / n
    z2 = z * z
    den = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / den
    half = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n)) / den
    return max(0.0, center - half), min(1.0, center + half)


def newcombe_difference(
    successes_a: int,
    n_a: int,
    successes_b: int,
    n_b: int,
) -> tuple[float, float, float]:
    """Newcombe hybrid-score interval for p_a - p_b using Wilson component intervals."""
    p_a = successes_a / n_a
    p_b = successes_b / n_b
    la, ua = wilson(successes_a, n_a)
    lb, ub = wilson(successes_b, n_b)
    d = p_a - p_b
    lower = d - math.sqrt((p_a - la) ** 2 + (ub - p_b) ** 2)
    upper = d + math.sqrt((ua - p_a) ** 2 + (p_b - lb) ** 2)
    return d, max(-1.0, lower), min(1.0, upper)


def geometry(p_success: float, p_failure: float, p0: float) -> str:
    lo = min(p_success, p_failure)
    hi = max(p_success, p_failure)
    if lo < p0 < hi:
        return "BASELINE_BETWEEN_ARMS"
    ds = abs(p_success - p0)
    df = abs(p_failure - p0)
    if math.isclose(ds, df, rel_tol=0.0, abs_tol=1e-12):
        return "EQUIDISTANT"
    return "BASELINE_CLOSER_TO_SUCCESS" if ds < df else "BASELINE_CLOSER_TO_FAILURE"


def validate_new_result(result: dict) -> dict[str, list[int]]:
    if result.get("condition") not in (None, "no_memory"):
        raise ValueError("Result-level condition, if present, must be no_memory")
    rows = result.get("rollouts")
    if not isinstance(rows, list):
        raise ValueError("Result must contain a rollouts list")
    if len(rows) != len(FUTURE_TASKS) * N_PER_FUTURE:
        raise ValueError(f"Expected exactly 32 rollouts, got {len(rows)}")

    grouped: dict[str, list[int]] = defaultdict(list)
    seen: set[tuple[str, int]] = set()
    for row in rows:
        task = str(row.get("future_task"))
        if task not in FUTURE_TASKS:
            raise ValueError(f"Unexpected future task: {task}")
        if "source_memory_task" in row and row.get("source_memory_task") not in (None, ""):
            raise ValueError("No-memory rollouts must not carry a source-memory dimension")
        if row.get("condition", "no_memory") != "no_memory":
            raise ValueError("Every rollout condition must be no_memory")
        idx = int(row.get("rollout"))
        key = (task, idx)
        if key in seen:
            raise ValueError(f"Duplicate rollout index: {key}")
        seen.add(key)
        score = float(row.get("benchmark_score"))
        if score not in (0.0, 1.0):
            raise ValueError("benchmark_score must be binary 0/1")
        grouped[task].append(int(score))

    for task in FUTURE_TASKS:
        if len(grouped[task]) != N_PER_FUTURE:
            raise ValueError(f"Expected {N_PER_FUTURE} fresh rollouts for task {task}, got {len(grouped[task])}")
    return grouped


def main() -> int:
    ap = argparse.ArgumentParser(description="Frozen offline analysis for the PROXY-O5 no-memory terminal control.")
    ap.add_argument("--result", required=True, type=Path, help="Fresh O5 result JSON; exactly 32 no-memory rollouts.")
    ap.add_argument(
        "--f2r1",
        type=Path,
        default=Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE/f2r1-confirmatory.json"),
    )
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    new_result = load(args.result)
    grouped = validate_new_result(new_result)
    f2r1 = load(args.f2r1)

    cell_map = {
        (str(row["source_memory_task"]), str(row["future_task"])): row
        for row in f2r1["cell_results"]
    }
    expected_cells = {(s, f) for s in SOURCE_TASKS for f in FUTURE_TASKS}
    if set(cell_map) != expected_cells:
        raise ValueError("F2R1 cell support no longer matches the frozen 4x4 support")

    baseline_rows = []
    baseline_counts = {}
    for future in FUTURE_TASKS:
        successes = sum(grouped[future])
        lo, hi = wilson(successes, N_PER_FUTURE)
        baseline_counts[future] = successes
        baseline_rows.append({
            "future_task": future,
            "successes": successes,
            "n": N_PER_FUTURE,
            "no_memory_rate": successes / N_PER_FUTURE,
            "wilson_95": [lo, hi],
        })

    comparisons = []
    geometry_counts: dict[str, int] = defaultdict(int)
    for source in SOURCE_TASKS:
        for future in FUTURE_TASKS:
            cell = cell_map[(source, future)]
            p_s = float(cell["success_memory_rate"])
            p_f = float(cell["failure_memory_rate"])
            s_s = int(round(p_s * N_PER_FUTURE))
            s_f = int(round(p_f * N_PER_FUTURE))
            s_0 = baseline_counts[future]
            d_s, l_s, u_s = newcombe_difference(s_s, N_PER_FUTURE, s_0, N_PER_FUTURE)
            d_f, l_f, u_f = newcombe_difference(s_f, N_PER_FUTURE, s_0, N_PER_FUTURE)
            p0 = s_0 / N_PER_FUTURE
            g = geometry(p_s, p_f, p0)
            geometry_counts[g] += 1
            comparisons.append({
                "source_memory_task": source,
                "future_task": future,
                "success_memory_rate_f2r1": p_s,
                "failure_memory_rate_f2r1": p_f,
                "no_memory_rate_fresh": p0,
                "success_minus_no_memory": d_s,
                "success_minus_no_memory_newcombe_95": [l_s, u_s],
                "failure_minus_no_memory": d_f,
                "failure_minus_no_memory_newcombe_95": [l_f, u_f],
                "point_estimate_geometry": g,
                "shared_baseline_note": "The same future-task no-memory estimate is shared by four source comparisons and is not an independent observation in each cell.",
            })

    out = {
        "schema_version": "1.0",
        "analysis_id": "D2-PROXY-O5-NO-MEMORY-BRANCH-LOCATION",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "objection_id": "PROXY-O5",
        "analysis_scope": "Secondary branch-location control only; the original F2R1 two-arm primary statistic and gate remain unchanged.",
        "fresh_no_memory_calls": 32,
        "old_exploratory_no_memory_calls_in_estimator": 0,
        "global_p_value": None,
        "global_gate": None,
        "no_memory_by_future_task": baseline_rows,
        "cell_relative_comparisons": comparisons,
        "point_estimate_geometry_counts": dict(sorted(geometry_counts.items())),
        "inference_boundary": [
            "No-memory is source-independent; do not count the shared future-task baseline four times as independent evidence.",
            "Geometry labels are descriptive point-estimate summaries, not new significance claims.",
            "This control does not expand claims to new models, live WebArena, new future tasks, or a three-arm randomized factorial design."
        ],
    }
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
