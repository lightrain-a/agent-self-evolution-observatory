from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated/asset-first-stri-r2-partition-geometry-contract-20260825.json"
OUTPUT = ROOT / "generated/asset-first-stri-r2-partition-geometry-result-20260825.json"
CSV_OUTPUT = ROOT / "generated/asset-first-stri-r2-partition-geometry-result-20260825.csv"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def weak_composition_count_dp(total: int, parts: int, min_each: int = 0) -> int:
    """Exact count of ordered integer compositions using a DP independent of stars-and-bars."""
    if total < 0 or parts <= 0 or min_each < 0:
        return 0
    dp = [0] * (total + 1)
    dp[0] = 1
    for _ in range(parts):
        nxt = [0] * (total + 1)
        prefix = [0] * (total + 2)
        for n, value in enumerate(dp):
            prefix[n + 1] = prefix[n] + value
        for n in range(total + 1):
            hi = n - min_each
            if hi >= 0:
                nxt[n] = prefix[hi + 1]
        dp = nxt
    return dp[total]


def stars_bars(total: int, parts: int, min_each: int = 0) -> int:
    residual = total - parts * min_each
    if residual < 0:
        return 0
    return math.comb(residual + parts - 1, parts - 1)


def build() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    frozen = contract["frozen_parameters"]
    M = int(frozen["threshold_M"])
    ks = tuple(int(x) for x in frozen["k_values"])
    n_min, n_max = int(frozen["N_min"]), int(frozen["N_max"])

    rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    guaranteed_failures: list[dict[str, Any]] = []
    tail_cells: list[dict[str, Any]] = []

    for k in ks:
        for N in range(n_min, n_max + 1):
            total_dp = weak_composition_count_dp(N, k, 0)
            invariant_dp = weak_composition_count_dp(N, k, M)
            fragmented_dp = total_dp - invariant_dp
            total_formula = stars_bars(N, k, 0)
            invariant_formula = stars_bars(N, k, M)
            fragmented_formula = total_formula - invariant_formula
            fraction = fragmented_dp / total_dp if total_dp else 0.0
            predicted_fraction = (
                1.0
                if M <= N < k * M
                else 1.0 - (invariant_formula / total_formula if total_formula else 0.0)
            )
            region = (
                "GUARANTEED_FRAGMENTATION"
                if M <= N < k * M
                else "PARTITION_DEPENDENT_TAIL"
            )
            row = {
                "k": k,
                "N": N,
                "M": M,
                "region": region,
                "total_weak_compositions": total_dp,
                "invariant_compositions": invariant_dp,
                "fragmented_compositions": fragmented_dp,
                "fragmentation_fraction": fraction,
                "closed_form_fragmentation_fraction": predicted_fraction,
                "dp_matches_stars_bars": total_dp == total_formula and invariant_dp == invariant_formula,
                "fraction_matches_closed_form": abs(fraction - predicted_fraction) <= 1e-15,
            }
            rows.append(row)
            if not row["dp_matches_stars_bars"] or not row["fraction_matches_closed_form"]:
                mismatches.append(row)
            if region == "GUARANTEED_FRAGMENTATION" and fraction != 1.0:
                guaranteed_failures.append(row)
            if region == "PARTITION_DEPENDENT_TAIL" and 0.0 < fraction < 1.0:
                tail_cells.append(row)

    by_k: dict[str, Any] = {}
    for k in ks:
        subset = [row for row in rows if row["k"] == k]
        tail = [row for row in subset if row["region"] == "PARTITION_DEPENDENT_TAIL"]
        by_k[str(k)] = {
            "guaranteed_fragmentation_N": [M, k * M - 1],
            "first_partition_dependent_N": k * M,
            "fragmentation_fraction_at_kM": next((row["fragmentation_fraction"] for row in tail if row["N"] == k * M), None),
            "fragmentation_fraction_at_N_max": subset[-1]["fragmentation_fraction"],
            "best_case_balanced_full_retirement_N": k * M,
        }

    pass_gate = not mismatches and not guaranteed_failures and bool(tail_cells)
    result = {
        "schema_version": "1.0",
        "paper_id": "E1.STRI",
        "experiment_id": contract["experiment_id"],
        "stage": "MECHANISM_REDESIGN_DETERMINISTIC_P3_RESULT",
        "decision": "PASS_ARBITRARY_PARTITION_GEOMETRY" if pass_gate else "STOP_PARTITION_GEOMETRY_MISMATCH",
        "pass_gate": pass_gate,
        "contract_sha256": sha_file(CONTRACT),
        "contract_git_commit": "43a4b5951e23e7dc8961c47c20e13fd7f2654fc3",
        "grid": {"k_values": list(ks), "N_min": n_min, "N_max": n_max, "M": M, "cells": len(rows)},
        "headline": {
            "formula_mismatches": len(mismatches),
            "guaranteed_region_failures": len(guaranteed_failures),
            "partition_dependent_tail_cells": len(tail_cells),
            "guaranteed_fragmentation_rule": "For every weak k-way evidence partition, M<=N<kM implies aggregate retirement and native non-retirement; fragmentation fraction is exactly 1.",
            "tail_rule": "For N>=kM, invariance depends on partition balance; fragmentation persists exactly when at least one identity bucket has fewer than M evidence items.",
            "closed_form": "F(N,k,M)=1 for M<=N<kM; otherwise 1-C(N-kM+k-1,k-1)/C(N+k-1,k-1).",
            "by_clone_multiplicity": by_k,
        },
        "rows": rows,
        "mechanism_interpretation": "The original balanced phase boundary is the earliest possible full native retirement, not a fragile equal-split artifact. The entire M<=N<kM region is representation-fragmented for every allocation of the same semantic evidence across k identities; beyond kM, an uneven partition can prolong fragmentation further.",
        "claim_boundary": "Exact combinatorial geometry of the released threshold-gate mechanism under retirement-eligible evidence. It does not establish endogenous partition frequencies, downstream utility, or cross-system phase-law generality.",
        "new_model_calls": 0,
        "new_agent_runs": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    result["result_canonical_sha256"] = canonical_sha(result)
    return result


def write_outputs() -> dict[str, Any]:
    result = build()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = [
        "k", "N", "M", "region", "total_weak_compositions", "invariant_compositions",
        "fragmented_compositions", "fragmentation_fraction", "closed_form_fragmentation_fraction",
        "dp_matches_stars_bars", "fraction_matches_closed_form",
    ]
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row[key] for key in fields} for row in result["rows"])
    return result


if __name__ == "__main__":
    print(json.dumps(write_outputs(), ensure_ascii=False, indent=2))
