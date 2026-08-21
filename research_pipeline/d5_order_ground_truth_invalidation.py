from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

HF_MIRROR = "https://hf-mirror.com/datasets/Salesforce/self-improve-fragility/resolve/main/metadata"
METHODS = ("wa_awm", "wa_rbank")
ORDERS = {"ordinal": None, "shuffle1": 42, "shuffle2": 99}
RUNS = ("run1", "run2", "run3")
TASK96_GOLD = "The last order was canceled. It will never arrive."


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fetch(path: str, cache_dir: Path) -> tuple[str, dict[str, Any]]:
    target = cache_dir / path
    target.parent.mkdir(parents=True, exist_ok=True)
    url = f"{HF_MIRROR}/{path}"
    if target.exists():
        raw = target.read_bytes()
        mode = "cache"
    else:
        response = requests.get(url, timeout=45)
        response.raise_for_status()
        raw = response.content
        target.write_bytes(raw)
        mode = "network"
    return raw.decode("utf-8", errors="replace"), {
        "path": path,
        "url": url,
        "sha256": sha256(raw),
        "bytes": len(raw),
        "acquisition": mode,
        "scientific_authority": False,
    }


def result_verdict(text: str, task_id: int) -> str:
    matches = re.findall(rf"\[task_{task_id}\]\s+\[Result\]\s+\((PASS|FAIL)\)", text)
    return matches[-1] if matches else "MISSING"


def score_value(text: str, task_id: int) -> float | None:
    matches = re.findall(rf"\[task_{task_id}\].*?score=([0-9.]+)", text)
    return float(matches[-1]) if matches else None


def task96_state(text: str) -> dict[str, Any]:
    orders = re.findall(r"Order\s*#?[: ]+([0-9]{6,9})", text, re.I)
    statuses = re.findall(r"Status:\s*([A-Za-z]+)", text)
    totals = re.findall(r"(?:Grand Total|Order Total):\s*\$([0-9,.]+)", text, re.I)
    item = ""
    for line in text.splitlines():
        if "Item:" in line and "Order" not in line:
            item = line.split("Item:", 1)[-1].strip()
    return {
        "order_number": orders[-1] if orders else "",
        "status": statuses[-1] if statuses else "",
        "grand_total": totals[-1] if totals else "",
        "item_excerpt": item[:260],
    }


def purchase_state(text: str, task_id: int) -> dict[str, Any]:
    checkout_success = bool(re.search(r"checkout.*success|success page.*load|order (?:placement )?succeeded|purchase completed", text, re.I))
    totals = re.findall(r"(?:Grand Total|Order Total):\s*\$([0-9,.]+)", text, re.I)
    item = ""
    for line in text.splitlines():
        if "Product:" in line:
            item = line.split("Product:", 1)[-1].strip()
    if not item:
        m = re.search(r"Purchased\s+(.+?)\s+for\s+\$", text, re.I)
        if m:
            item = m.group(1).strip()
    return {
        "task_id": task_id,
        "benchmark_verdict": result_verdict(text, task_id),
        "benchmark_score": score_value(text, task_id),
        "checkout_success_observed": checkout_success,
        "order_total": totals[-1] if totals else "",
        "item_excerpt": item[:260],
    }


def domain_sequence(raw_tasks: list[dict[str, Any]], domain: str, seed: int | None) -> list[int]:
    ids = sorted(int(row["task_id"]) for row in raw_tasks if row.get("sites") == [domain])
    if seed is not None:
        random.seed(seed)
        random.shuffle(ids)
    return ids


def task96_panel(cache_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    for method in METHODS:
        for order in ORDERS:
            for run in RUNS:
                path = f"{method}_{order}/shopping_{run}/logs/96.log"
                text, receipt = fetch(path, cache_dir)
                state = task96_state(text)
                rows.append({
                    "method": method,
                    "order": order,
                    "run": run,
                    "task_id": 96,
                    "verdict": result_verdict(text, 96),
                    "score": score_value(text, 96),
                    **state,
                    "source_sha256": receipt["sha256"],
                })
                sources.append(receipt)
    for run in RUNS:
        path = f"wa_baseline/shopping_{run}/logs/96.log"
        text, receipt = fetch(path, cache_dir)
        state = task96_state(text)
        rows.append({
            "method": "wa_baseline",
            "order": "ordinal",
            "run": run,
            "task_id": 96,
            "verdict": result_verdict(text, 96),
            "score": score_value(text, 96),
            **state,
            "source_sha256": receipt["sha256"],
        })
        sources.append(receipt)
    return rows, sources


def build_report(raw_tasks: list[dict[str, Any]], cache_dir: Path) -> dict[str, Any]:
    panel, sources = task96_panel(cache_dir)
    # Direct causal chain: AWM shuffle1 run1 task 509 writes the exact order later read by task 96.
    writer_path = "wa_awm_shuffle1/shopping_run1/logs/509.log"
    writer_text, writer_receipt = fetch(writer_path, cache_dir)
    sources.append(writer_receipt)
    writer = purchase_state(writer_text, 509)
    reader = next(row for row in panel if row["method"] == "wa_awm" and row["order"] == "shuffle1" and row["run"] == "run1")

    sequences = {name: domain_sequence(raw_tasks, "shopping", seed) for name, seed in ORDERS.items()}
    positions = {name: {tid: idx for idx, tid in enumerate(seq)} for name, seq in sequences.items()}
    ordering = {
        name: {
            "task509_position": positions[name][509],
            "task96_position": positions[name][96],
            "task509_precedes_task96": positions[name][509] < positions[name][96],
        }
        for name in ORDERS
    }

    ordinal_memory = [r for r in panel if r["method"] in METHODS and r["order"] == "ordinal"]
    shuffled_memory = [r for r in panel if r["method"] in METHODS and r["order"] != "ordinal"]
    baseline = [r for r in panel if r["method"] == "wa_baseline"]
    order_total_match = bool(writer["order_total"] and reader["grand_total"] and writer["order_total"] == reader["grand_total"])
    item_match = bool(writer["item_excerpt"] and reader["item_excerpt"] and "cole haan" in writer["item_excerpt"].lower() and "cole haan" in reader["item_excerpt"].lower())
    observed_chain = (
        writer["checkout_success_observed"]
        and ordering["shuffle1"]["task509_precedes_task96"]
        and writer["benchmark_verdict"] == "FAIL"
        and reader["verdict"] == "FAIL"
        and reader["status"].lower() == "pending"
        and order_total_match
        and item_match
    )
    # Cross-run certification uses the benchmark verdict, which is present in every released log.
    # Parsed status text is an auxiliary consistency check only because some PASS logs omit the
    # final status string even though the evaluator verdict is retained.
    ordinal_clean = all(r["verdict"] == "PASS" for r in ordinal_memory) and all(
        not r["status"] or r["status"].lower() in {"canceled", "cancelled"} for r in ordinal_memory
    )
    shuffled_stale = all(r["verdict"] == "FAIL" for r in shuffled_memory) and all(
        not r["status"] or r["status"].lower() == "pending" for r in shuffled_memory
    )
    baseline_clean = all(r["verdict"] == "PASS" for r in baseline) and all(
        not r["status"] or r["status"].lower() in {"canceled", "cancelled"} for r in baseline
    )

    status = "OBSERVED_GROUND_TRUTH_INVALIDATION_CERTIFIED" if observed_chain and ordinal_clean and shuffled_stale and baseline_clean else "INCOMPLETE"
    return {
        "schema_version": "1.0",
        "generated_at": now(),
        "status": status,
        "scientific_authority": False,
        "candidate_lineage": {
            "parent_candidate": "D5-C01",
            "derivation_type": "child_of_falsifier_observation",
            "child_candidate": "D5-C01-ENV-ORDER-CONTAMINATION",
        },
        "claim_boundary": {
            "supported": "At least one released shuffled WebArena run contains a successful persistent environment write that changes the object denoted by a later task's fixed ground-truth answer, causing a correct read of current environment state to be scored as failure.",
            "not_yet_supported": "Environment carryover explains the full aggregate task-order degradation reported for AWM or ReasoningBank.",
            "decisive_missing_control": "No-memory baseline under the identical shuffle seeds 42 and 99 with the same stateful WebArena execution protocol.",
        },
        "task96_gold": TASK96_GOLD,
        "task96_panel": panel,
        "summary": {
            "ordinal_memory_task96_pass": sum(r["verdict"] == "PASS" for r in ordinal_memory),
            "ordinal_memory_task96_total": len(ordinal_memory),
            "shuffled_memory_task96_pass": sum(r["verdict"] == "PASS" for r in shuffled_memory),
            "shuffled_memory_task96_total": len(shuffled_memory),
            "baseline_ordinal_task96_pass": sum(r["verdict"] == "PASS" for r in baseline),
            "baseline_ordinal_task96_total": len(baseline),
            "direct_writer_reader_chain_certified": observed_chain,
        },
        "direct_chain": {
            "writer": {"source_path": writer_path, **writer},
            "reader": {
                "source_path": "wa_awm_shuffle1/shopping_run1/logs/96.log",
                "task_id": 96,
                "benchmark_verdict": reader["verdict"],
                "benchmark_score": reader["score"],
                "observed_latest_order": reader["order_number"],
                "observed_status": reader["status"],
                "observed_total": reader["grand_total"],
                "observed_item_excerpt": reader["item_excerpt"],
            },
            "ordering": ordering,
            "same_order_total": order_total_match,
            "same_item_identity": item_match,
            "interpretation": "Task 509 reaches checkout success and mutates the shopping backend even though its benchmark verdict is FAIL. Task 96 later queries the latest order and reads the matching newly-created Cole Haan order as Pending, while its static gold remains the pre-run canceled order.",
        },
        "source_receipts": sources,
        "authority": {"problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-config", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_tasks = json.loads(args.raw_config.read_text(encoding="utf-8"))
    report = build_report(raw_tasks, args.cache_dir)
    report["raw_config_receipt"] = {"path": str(args.raw_config), "sha256": sha256(args.raw_config.read_bytes())}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "summary": report["summary"], "direct_chain": report["direct_chain"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
