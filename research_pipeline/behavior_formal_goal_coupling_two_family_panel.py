from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import statistics
from pathlib import Path

SCHEMA_VERSION = "behavior-formal-goal-coupling-two-family-panel-result-v1"
OBJECT_ID = "SUCC-C-BEHAVIOR2026-TWO-FAMILY-STRICT-MATCHED-PANEL"
FAMILIES = ("pi0.5", "GR00T N1.7")
PUBLIC_EVAL_INSTANCES = tuple(range(10))
EXPECTED_PAIR_COUNT = 13
EXPECTED_TASK_COUNT = EXPECTED_PAIR_COUNT * 2
EXPECTED_RESULT_ROWS = EXPECTED_TASK_COUNT * len(FAMILIES) * len(PUBLIC_EVAL_INSTANCES)


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
        raise ValueError(f"expected 100 challenge tasks, got {len(rows)}")
    return rows


def strict_matched_pairs(structure_rows: list[dict]) -> list[dict]:
    candidates: list[tuple] = []
    for i, a in enumerate(structure_rows):
        for j in range(i + 1, len(structure_rows)):
            b = structure_rows[j]
            if int(a["atomic_goal_count"]) != int(b["atomic_goal_count"]):
                continue
            if int(a["branch_operator_count"]) != int(b["branch_operator_count"]):
                continue
            if int(a["goal_logic_depth"]) != int(b["goal_logic_depth"]):
                continue
            if int(a["quantifier_count"]) != int(b["quantifier_count"]):
                continue
            edge_a = int(a["shared_argument_edge_count"])
            edge_b = int(b["shared_argument_edge_count"])
            gap = abs(edge_a - edge_b)
            if gap == 0:
                continue
            if edge_a < edge_b:
                lo_idx, lo, hi_idx, hi = i, a, j, b
            else:
                lo_idx, lo, hi_idx, hi = j, b, i, a
            candidates.append(
                (
                    gap,
                    str(lo["activity"]),
                    str(hi["activity"]),
                    lo_idx,
                    hi_idx,
                    lo,
                    hi,
                )
            )
    ordered = sorted(
        candidates,
        key=lambda row: (row[0], row[1], row[2], row[3], row[4]),
        reverse=True,
    )
    used: set[int] = set()
    selected: list[dict] = []
    for gap, _, _, lo_idx, hi_idx, lo, hi in ordered:
        if lo_idx in used or hi_idx in used:
            continue
        selected.append(
            {
                "pair_id": len(selected) + 1,
                "low_task_index": lo_idx,
                "high_task_index": hi_idx,
                "low_activity": str(lo["activity"]),
                "high_activity": str(hi["activity"]),
                "low_edge": int(lo["shared_argument_edge_count"]),
                "high_edge": int(hi["shared_argument_edge_count"]),
                "edge_gap": int(gap),
                "atomic_goal_count": int(lo["atomic_goal_count"]),
                "branch_operator_count": int(lo["branch_operator_count"]),
                "goal_logic_depth": int(lo["goal_logic_depth"]),
                "quantifier_count": int(lo["quantifier_count"]),
            }
        )
        used.update((lo_idx, hi_idx))
    if len(selected) != EXPECTED_PAIR_COUNT:
        raise ValueError(f"strict pairing drift: expected {EXPECTED_PAIR_COUNT}, got {len(selected)}")
    return selected


def validate_result_rows(rows: list[dict], pairs: list[dict]) -> None:
    task_ids = sorted(
        {int(p["low_task_index"]) for p in pairs}
        | {int(p["high_task_index"]) for p in pairs}
    )
    if len(task_ids) != EXPECTED_TASK_COUNT:
        raise ValueError("pair panel is not task-disjoint")
    if len(rows) != EXPECTED_RESULT_ROWS:
        raise ValueError(f"expected {EXPECTED_RESULT_ROWS} evaluator rows, got {len(rows)}")
    expected = {
        (task_id, family, instance)
        for task_id in task_ids
        for family in FAMILIES
        for instance in PUBLIC_EVAL_INSTANCES
    }
    observed = set()
    for row in rows:
        key = (int(row["task_index"]), str(row["family"]), int(row["instance_index"]))
        if key in observed:
            raise ValueError(f"duplicate evaluator unit {key}")
        observed.add(key)
        q = float(row["q_score"])
        if not (0.0 <= q <= 1.0):
            raise ValueError(f"q_score out of range for {key}: {q}")
    if observed != expected:
        missing = sorted(expected - observed)[:20]
        extra = sorted(observed - expected)[:20]
        raise ValueError(f"evaluator matrix mismatch; missing={missing}, extra={extra}")


def task_means(rows: list[dict]) -> dict[tuple[int, str], float]:
    buckets: dict[tuple[int, str], list[float]] = {}
    for row in rows:
        key = (int(row["task_index"]), str(row["family"]))
        buckets.setdefault(key, []).append(float(row["q_score"]))
    means = {}
    for key, values in buckets.items():
        if len(values) != len(PUBLIC_EVAL_INSTANCES):
            raise ValueError(f"task-family unit {key} has {len(values)} instances")
        means[key] = statistics.fmean(values)
    return means


def exact_sign_flip_mean_pvalue(values: list[float]) -> dict:
    if len(values) != EXPECTED_PAIR_COUNT:
        raise ValueError(f"expected {EXPECTED_PAIR_COUNT} pair contrasts")
    observed = statistics.fmean(values)
    extreme = 0
    total = 1 << len(values)
    for mask in range(total):
        flipped = [(-v if (mask >> i) & 1 else v) for i, v in enumerate(values)]
        stat = statistics.fmean(flipped)
        if abs(stat) >= abs(observed) - 1e-15:
            extreme += 1
    return {
        "observed_mean": observed,
        "two_sided_p": extreme / total,
        "assignments": total,
        "reference_test": "exact sign-flip reference distribution over 13 task-pair contrasts",
    }


def analyze(rows: list[dict], pairs: list[dict]) -> dict:
    validate_result_rows(rows, pairs)
    means = task_means(rows)
    per_pair = []
    for pair in pairs:
        family_deltas = {}
        for family in FAMILIES:
            low = means[(int(pair["low_task_index"]), family)]
            high = means[(int(pair["high_task_index"]), family)]
            family_deltas[family] = high - low
        pair_delta = statistics.fmean(family_deltas.values())
        per_pair.append({**pair, "family_high_minus_low": family_deltas, "two_family_mean_high_minus_low": pair_delta})
    pooled = [r["two_family_mean_high_minus_low"] for r in per_pair]
    primary = exact_sign_flip_mean_pvalue(pooled)
    family_medians = {
        family: statistics.median([r["family_high_minus_low"][family] for r in per_pair])
        for family in FAMILIES
    }
    negative_pairs = sum(1 for x in pooled if x < 0)
    positive_pairs = sum(1 for x in pooled if x > 0)
    zero_pairs = len(pooled) - negative_pairs - positive_pairs
    support = bool(
        primary["observed_mean"] < 0.0
        and primary["two_sided_p"] < 0.05
        and all(v < 0.0 for v in family_medians.values())
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "object_id": OBJECT_ID,
        "status": "TWO_FAMILY_STRICT_PANEL_SUPPORT" if support else "TWO_FAMILY_STRICT_PANEL_NOT_SUPPORTED",
        "claim_scope": "direct policy-performance association restricted to the two official BEHAVIOR 2026 baseline families; not broad cross-family generalization",
        "primary": {
            **primary,
            "direction_required": "mean high-coupling minus low-coupling Q < 0",
            "family_median_coherence_required": "both pi0.5 and GR00T N1.7 family medians < 0",
            "family_medians": family_medians,
            "negative_pair_count": negative_pairs,
            "positive_pair_count": positive_pairs,
            "zero_pair_count": zero_pairs,
            "pass": support,
        },
        "pairs": per_pair,
        "does_not_imply": [
            "generalization to a third independent policy family",
            "authorization to lower the frozen three-family requirement of SUCC-C-BEHAVIOR2026-LOCAL-REPLICATION",
            "PORT-010 reopen",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--rows", type=Path)
    parser.add_argument("--pairs-out", type=Path)
    parser.add_argument("--result-out", type=Path)
    args = parser.parse_args()
    pairs = strict_matched_pairs(load_structure(args.structure))
    if args.pairs_out:
        args.pairs_out.parent.mkdir(parents=True, exist_ok=True)
        args.pairs_out.write_text(json.dumps(pairs, indent=2, sort_keys=True) + "\n")
    if args.rows:
        if not args.result_out:
            raise SystemExit("--result-out is required with --rows")
        rows = json.loads(args.rows.read_text(encoding="utf-8"))
        if isinstance(rows, dict):
            rows = rows.get("rows") or []
        result = analyze(rows, pairs)
        args.result_out.parent.mkdir(parents=True, exist_ok=True)
        args.result_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": result["status"], "primary": result["primary"]}, sort_keys=True))
    else:
        print(json.dumps({"pair_count": len(pairs), "task_count": 2 * len(pairs)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
