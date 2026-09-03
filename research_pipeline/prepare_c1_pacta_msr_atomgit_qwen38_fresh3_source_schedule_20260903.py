#!/usr/bin/env python3
"""Freeze the fresh3 source acquisition schedule before any source outcome."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research_pipeline.c1_pacta_rb_qwen397 import atomic_json, sha256_file

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-pool-20260903.json"
POOL_SHA = "3780fa80ee0bbfce01e3fd4f6bcabe6aaaa21111c0aa910ea7ce1bde302a9257"
SPLIT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-split-20260903.json"
SPLIT_SHA = "d71f48910e531e62de2d056342c0c17ce17872503f089a29b16182fca3c1b2d9"
PROBES = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-probe-specs-20260903.json"
PROBES_SHA = "19f119fdb80e58427809a565d515900a14455394e79c31126645521702940c97"
Q02 = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-q02-budget-20260902-v1/q02-result.json")
Q02_SHA = "c4c7c05f4e14d82fa8ef7d0d0ea2c31a8888295f96eb810b649150da1577b7ce"
Q03 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q03-text-bridge-closure-20260903.json"
Q03_SHA = "077383ca894abc1c3986e01ef90b16628d2580a3058d66c2838a63796208fdac"
OUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-source-schedule-20260903.json"
ORDER_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-SOURCE-v1"


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def prepare() -> dict[str, Any]:
    for path, expected, label in (
        (POOL, POOL_SHA, "pool"),
        (SPLIT, SPLIT_SHA, "split"),
        (PROBES, PROBES_SHA, "probes"),
        (Q02, Q02_SHA, "q02"),
        (Q03, Q03_SHA, "q03"),
    ):
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"STOP_FRESH3_SOURCE_SCHEDULE_INPUT_DRIFT:{label}")
    pool = json.loads(POOL.read_text())
    q02 = json.loads(Q02.read_text())
    q03 = json.loads(Q03.read_text())
    if q02.get("status") != "ATOMGIT_QWEN38_Q02_SOURCE_BUDGET_PASS" or q02.get("pass") is not True:
        raise RuntimeError("STOP_FRESH3_SOURCE_Q02_NOT_QUALIFIED")
    if q02.get("selected_source_budget") != 32768 or q02.get("invocation_timeout_seconds") != 900:
        raise RuntimeError("STOP_FRESH3_SOURCE_Q02_PARAMETER_DRIFT")
    if q03.get("status") != "ATOMGIT_QWEN38_Q03_TEXT_BRIDGE_PASS" or q03.get("fresh3_authorized") is not True:
        raise RuntimeError("STOP_FRESH3_SOURCE_Q03_NOT_QUALIFIED")
    units = sorted(
        pool["units"],
        key=lambda unit: (sha(ORDER_SALT + "|" + unit["unit_id"]), unit["unit_id"]),
    )
    rows = []
    for sequence, unit in enumerate(units, 1):
        rows.append({
            "sequence": sequence,
            "unit_id": unit["unit_id"],
            "repository": unit["task_family"],
            "source_task_id": unit["source_task_id"],
            "source_task_sha256": unit["source_task_sha256"],
            "source_base_commit": unit["source_base_commit"],
            "future_task_id": unit["future_task_id"],
            "logical_attempts": 1,
            "replacement": False,
            "future_task_executed": False,
            "order_key": sha(ORDER_SALT + "|" + unit["unit_id"]),
            "runtime_binding": "DEFERRED_UNTIL_FRESH3_20_RUNTIME_READY",
        })
    if len(rows) != 10 or len({row["source_task_id"] for row in rows}) != 10:
        raise RuntimeError("STOP_FRESH3_SOURCE_SCHEDULE_GEOMETRY")
    return {
        "schema_version": 1,
        "experiment": "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-SOURCE-T0-20260903",
        "status": "FRESH3_SOURCE_SCHEDULE_FROZEN_PRE_SOURCE_OUTCOME",
        "fresh_pool_sha256": POOL_SHA,
        "pilot_split_sha256": SPLIT_SHA,
        "probe_specs_sha256": PROBES_SHA,
        "q02_result_sha256": Q02_SHA,
        "q03_text_bridge_sha256": Q03_SHA,
        "bridge_schema": "c1-minisweagent-ordinary-json-text-bridge-v1",
        "order_salt": ORDER_SALT,
        "source_max_completion_tokens": 32768,
        "atomcode_subprocess_timeout_seconds": 900,
        "first_decision_budget": 2048,
        "sampling_control": "PROVIDER_MANAGED_NOT_EXPOSED_BY_ATOMCODE_5_0_9",
        "source_gate": "all 10 provenance-valid via frozen Q0.3 text bridge; any consumed-invalid source retires the entire fresh3 pool; no replacement or top-up",
        "rows": rows,
        "provider_calls": 0,
        "scientific_source_tasks_used": 0,
        "future_task_executions": 0,
        "writer_calls": 0,
        "binder_calls": 0,
        "probe_calls": 0,
        "shadow_calls": 0,
        "final_calls": 0,
    }


def main() -> None:
    if OUT.exists():
        raise RuntimeError("fresh3 source schedule exists; no overwrite")
    result = prepare()
    atomic_json(OUT, result)
    print(json.dumps({"status": result["status"], "scheduled": len(result["rows"]), "sha256": sha256_file(OUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
