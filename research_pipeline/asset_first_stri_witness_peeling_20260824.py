from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from .asset_first_stri_certificate import dual_global_package_ratio, optimal_global_package_ratio
from .asset_first_stri_reviewer_extensions import load_jsonl

TOL = 1e-8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def level1_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if int(row.get("level") or -1) == 1 and row.get("accepted_skill_ids")]


def row_key(row: dict[str, Any]) -> tuple[int, str]:
    return int(row.get("index")), str(row.get("tool") or "")


def witness_peeling(rows: list[dict[str, Any]]) -> dict[str, Any]:
    remaining = list(rows)
    original_count = len(remaining)
    rounds: list[dict[str, Any]] = []
    removed_keys: set[tuple[int, str]] = set()

    while True:
        primal = optimal_global_package_ratio(remaining)
        ratio = primal.get("ratio")
        if ratio is None:
            raise RuntimeError("witness peeling encountered an invalid primal support matrix")
        if float(ratio) <= 1.0 + TOL:
            final_ratio = float(ratio)
            break

        dual = dual_global_package_ratio(remaining)
        lower = dual.get("lower_bound")
        if not dual.get("pass") or lower is None or abs(float(lower) - float(ratio)) > TOL:
            raise RuntimeError("witness peeling requires a tight primal-dual optimum")

        witness_rows = dual.get("alpha_rows", []) + dual.get("beta_rows", [])
        keys = {row_key(row) for row in witness_rows}
        if not keys:
            raise RuntimeError("residual optimum returned an empty dual witness")
        if keys & removed_keys:
            raise RuntimeError("witness peeling produced a previously removed row")

        rounds.append(
            {
                "round": len(rounds),
                "rows_before": len(remaining),
                "R_star_before": float(ratio),
                "dual_lower_bound": float(lower),
                "witness_rows": sorted(
                    [
                        {
                            "index": int(row.get("index")),
                            "tool": str(row.get("tool") or ""),
                            "accepted_skill_ids": sorted(str(x) for x in row.get("accepted_skill_ids") or []),
                            "dual_role": "alpha" if row in dual.get("alpha_rows", []) else "beta",
                            "dual_value": float(row.get("value")),
                        }
                        for row in witness_rows
                    ],
                    key=lambda item: (item["index"], item["tool"], item["dual_role"]),
                ),
                "witness_row_count": len(keys),
            }
        )
        removed_keys.update(keys)
        next_remaining = [row for row in remaining if row_key(row) not in keys]
        if len(next_remaining) >= len(remaining):
            raise RuntimeError("witness peeling failed to remove the selected witness")
        remaining = next_remaining

    three_row_rounds = sum(int(record["witness_row_count"]) == 3 for record in rounds)
    witness_tools = {str(row["tool"]) for record in rounds for row in record["witness_rows"]}
    witness_skill_ids = {str(skill_id) for record in rounds for row in record["witness_rows"] for skill_id in row["accepted_skill_ids"]}
    witness_support_patterns = {tuple(row["accepted_skill_ids"]) for record in rounds for row in record["witness_rows"]}
    return {
        "scope": "frozen Skill-SP API-Bank Level-1 support matrix",
        "procedure": "solve neutral R*, extract one tight HiGHS dual optimum, remove every row with positive alpha/beta mass, and repeat until equalizable",
        "summary": {
            "initial_rows": original_count,
            "initial_R_star": float(rounds[0]["R_star_before"]) if rounds else final_ratio,
            "peeling_rounds_before_equalizable": len(rounds),
            "pairwise_disjoint_witness_rows_removed": len(removed_keys),
            "fraction_rows_removed": len(removed_keys) / original_count if original_count else 0.0,
            "three_row_sparse_rounds": three_row_rounds,
            "unique_tools_spanned": len(witness_tools),
            "active_skill_ids_spanned": len(witness_skill_ids),
            "unique_support_patterns_spanned": len(witness_support_patterns),
            "remaining_rows": len(remaining),
            "final_R_star": final_ratio,
        },
        "rounds": rounds,
        "claim_boundary": "This deterministic solver-path stress test establishes repeated disjoint sparse certificates under successive row removal. It is not a minimum-deletion computation, does not prove that 66 rows are necessary, and does not claim uniqueness of the dual witness sequence.",
    }


def build(membership: Path) -> dict[str, Any]:
    rows = load_jsonl(membership)
    level1 = level1_rows(rows)
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis_type": "iterative sparse dual-witness peeling stress",
        "analysis_date": "2026-08-24",
        "input": {
            "membership_sha256": sha256(membership),
            "rows_all_levels": len(rows),
            "level1_covered_rows": len(level1),
        },
        "witness_peeling": witness_peeling(level1),
        "scientific_boundary": {
            "claim_expansion": False,
            "new_outcome_data": False,
            "new_support_annotations": False,
            "model_calls": 0,
            "gpu_runs": 0,
        },
    }


def write_csv(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["round", "rows_before", "R_star_before", "witness_row_count", "witness_rows"])
        writer.writeheader()
        for record in payload["witness_peeling"]["rounds"]:
            writer.writerow(
                {
                    "round": record["round"],
                    "rows_before": record["rows_before"],
                    "R_star_before": record["R_star_before"],
                    "witness_row_count": record["witness_row_count"],
                    "witness_rows": json.dumps(record["witness_rows"], ensure_ascii=False, sort_keys=True),
                }
            )


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
    print(json.dumps(payload["witness_peeling"]["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
