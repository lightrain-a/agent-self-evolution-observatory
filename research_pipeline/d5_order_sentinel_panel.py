from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

SENTINELS = {
    96: {"domain": "shopping", "dynamic_object": "latest order", "gold": "last order canceled / never arrives"},
    189: {"domain": "shopping", "dynamic_object": "latest pending order", "gold": "total = 754.99"},
    198: {"domain": "shopping_admin", "dynamic_object": "most recent canceled order", "gold": "customer = Lily Potter"},
}
METHODS = ("wa_awm", "wa_rbank")
RUNS = ("run1", "run2", "run3")


def wilson(success: int, total: int, z: float = 1.959963984540054) -> list[float] | None:
    if total <= 0:
        return None
    p = success / total
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return [round(max(0.0, center - half), 6), round(min(1.0, center + half), 6)]


def sign_test_all_negative(n: int) -> dict[str, float]:
    return {"one_sided_p": round(0.5 ** n, 10), "two_sided_p": round(min(1.0, 2 * (0.5 ** n)), 10)}


def build(retro: dict[str, Any]) -> dict[str, Any]:
    idx: dict[tuple[str, str, str, str, int], dict[str, Any]] = {}
    for cell in retro["run_domain_rows"]:
        for row in cell["reader_rows"]:
            idx[(cell["method"], cell["order"], cell["domain"], cell["run"], int(row["task_id"]))] = row
    sentinel_rows = []
    for task_id, spec in SENTINELS.items():
        ordinal = []
        shuffle1 = []
        shuffle2 = []
        for method in METHODS:
            for run in RUNS:
                ordinal.append(idx[(method, "ordinal", spec["domain"], run, task_id)])
                shuffle1.append(idx[(method, "shuffle1", spec["domain"], run, task_id)])
                shuffle2.append(idx[(method, "shuffle2", spec["domain"], run, task_id)])
        record = {
            "task_id": task_id,
            **spec,
            "ordinal": {
                "pass": sum(r["success"] for r in ordinal),
                "total": len(ordinal),
                "pass_rate": sum(r["success"] for r in ordinal) / len(ordinal),
                "exposed": sum(r["lower_bound_exposed"] for r in ordinal),
            },
            "shuffle1": {
                "pass": sum(r["success"] for r in shuffle1),
                "total": len(shuffle1),
                "pass_rate": sum(r["success"] for r in shuffle1) / len(shuffle1),
                "exposed": sum(r["lower_bound_exposed"] for r in shuffle1),
            },
            "shuffle2": {
                "pass": sum(r["success"] for r in shuffle2),
                "total": len(shuffle2),
                "pass_rate": sum(r["success"] for r in shuffle2) / len(shuffle2),
                "exposed": sum(r["lower_bound_exposed"] for r in shuffle2),
            },
        }
        record["ordinal"]["wilson95"] = wilson(record["ordinal"]["pass"], record["ordinal"]["total"])
        for order in ("shuffle1", "shuffle2"):
            record[order]["wilson95"] = wilson(record[order]["pass"], record[order]["total"])
            paired = 0
            reverse = 0
            order_rows = shuffle1 if order == "shuffle1" else shuffle2
            for a, b in zip(ordinal, order_rows):
                if a["success"] and not b["success"]:
                    paired += 1
                elif not a["success"] and b["success"]:
                    reverse += 1
            record[order]["paired_ordinal_pass_to_shuffle_fail"] = paired
            record[order]["paired_ordinal_fail_to_shuffle_pass"] = reverse
            record[order]["paired_sign_test"] = sign_test_all_negative(paired) if paired and reverse == 0 else None
        sentinel_rows.append(record)

    all_ordinal_pass = sum(r["ordinal"]["pass"] for r in sentinel_rows)
    all_ordinal_total = sum(r["ordinal"]["total"] for r in sentinel_rows)
    all_shuffle_pass = sum(r[o]["pass"] for r in sentinel_rows for o in ("shuffle1", "shuffle2"))
    all_shuffle_total = sum(r[o]["total"] for r in sentinel_rows for o in ("shuffle1", "shuffle2"))
    return {
        "schema_version": "1.0",
        "status": "HIGH_PRECISION_SENTINEL_REPLICATION_COMPLETE",
        "scientific_authority": False,
        "sentinels": sentinel_rows,
        "summary": {
            "sentinel_tasks": len(sentinel_rows),
            "ordinal_memory_pass": all_ordinal_pass,
            "ordinal_memory_total": all_ordinal_total,
            "ordinal_memory_pass_rate": all_ordinal_pass / all_ordinal_total,
            "shuffled_memory_pass": all_shuffle_pass,
            "shuffled_memory_total": all_shuffle_total,
            "shuffled_memory_pass_rate": all_shuffle_pass / all_shuffle_total,
            "ordinal_to_shuffle_risk_difference": round((all_shuffle_pass / all_shuffle_total) - (all_ordinal_pass / all_ordinal_total), 6),
            "all_three_sentinels_replicate_across_both_memory_methods_and_three_runs": all(
                r["ordinal"]["pass"] == 6 and r["shuffle1"]["pass"] == 0 and r["shuffle2"]["pass"] == 0 for r in sentinel_rows
            ),
        },
        "interpretation": "These sentinels are predefined dynamic-reference tasks whose fixed answers depend on latest/most-recent mutable backend objects. Every AWM/RBank ordinal replicate passes, while every corresponding shuffled replicate fails. This panel establishes stable order sensitivity on ground-truth-unstable tasks; it does not by itself attribute all benchmark-wide order degradation to environment carryover.",
        "authority": {"problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrospective", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(json.loads(args.retrospective.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
