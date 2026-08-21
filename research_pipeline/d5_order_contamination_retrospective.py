from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HF_BASE = "https://hf-mirror.com/datasets/Salesforce/self-improve-fragility/resolve/main"
METHODS = ("wa_awm", "wa_rbank")
ORDERS = {"ordinal": None, "shuffle1": 42, "shuffle2": 99}
RUNS = ("run1", "run2", "run3")
DOMAINS = ("gitlab", "reddit", "shopping", "shopping_admin")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rate(n: int, d: int) -> float | None:
    return round(n / d, 6) if d else None


def parquet_path(method: str, order: str, domain: str, run: str) -> str:
    subset = f"{method}_{order}"
    return f"{subset}/{domain}_{run}-00000-of-00001.parquet"


def baseline_path(domain: str, run: str) -> str:
    return f"wa_baseline/{domain}_{run}-00000-of-00001.parquet"


def load_column_matrix(remote_path: str, cache_dir: Path) -> dict[int, bool]:
    cache = cache_dir / (remote_path.replace("/", "__") + ".json")
    if cache.exists():
        payload = json.loads(cache.read_text(encoding="utf-8"))
        return {int(k): bool(v) for k, v in payload["rows"].items()}
    import fsspec  # type: ignore
    import pyarrow.parquet as pq  # type: ignore

    url = f"{HF_BASE}/{remote_path}"
    with fsspec.open(url, "rb", block_size=1 << 20, cache_type="readahead") as handle:
        table = pq.read_table(handle, columns=["task_id", "is_successful"])
    ids = table["task_id"].to_pylist()
    success = table["is_successful"].to_pylist()
    rows = {int(task_id): bool(value) for task_id, value in zip(ids, success)}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"source": url, "rows": rows}, sort_keys=True) + "\n", encoding="utf-8")
    return rows


def sequence(task_ids: list[int], seed: int | None) -> list[int]:
    out = sorted(task_ids)
    if seed is not None:
        random.seed(seed)
        random.shuffle(out)
    return out


def overlap(a: list[str], b: list[str]) -> list[str]:
    return sorted(set(a) & set(b))


def analyze_run(
    method: str,
    order: str,
    domain: str,
    run: str,
    matrix: dict[int, bool],
    annotations: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    ids = sorted(task_id for task_id, row in annotations.items() if row.get("domain") == domain and task_id in matrix)
    seq = sequence(ids, ORDERS[order])
    pos = {task_id: idx for idx, task_id in enumerate(seq)}
    reader_rows: list[dict[str, Any]] = []
    mutators = [task_id for task_id in ids if annotations[task_id].get("writes")]
    for reader in ids:
        read_channels = annotations[reader].get("sensitive_reads") or []
        if not read_channels:
            continue
        prior = []
        successful_prior = []
        for writer in mutators:
            if writer == reader or pos[writer] >= pos[reader]:
                continue
            channels = overlap(annotations[writer].get("writes") or [], read_channels)
            if not channels:
                continue
            info = {"task_id": writer, "channels": channels, "scorer_success": bool(matrix.get(writer, False))}
            prior.append(info)
            if info["scorer_success"]:
                successful_prior.append(info)
        reader_rows.append({
            "task_id": reader,
            "success": bool(matrix[reader]),
            "position": pos[reader],
            "static_at_risk": bool(prior),
            "lower_bound_exposed": bool(successful_prior),
            "prior_interfering_writers": prior,
            "successful_prior_interfering_writers": successful_prior,
        })
    total_success = sum(matrix.values())
    exposed = [row for row in reader_rows if row["lower_bound_exposed"]]
    clean = [row for row in reader_rows if not row["lower_bound_exposed"]]
    at_risk = [row for row in reader_rows if row["static_at_risk"]]
    all_fail = sum(not bool(value) for value in matrix.values())
    exposed_fail = sum(not row["success"] for row in exposed)
    reader_fail = sum(not row["success"] for row in reader_rows)
    reader_success = len(reader_rows) - reader_fail
    non_sensitive_tasks = len(matrix) - len(reader_rows)
    non_sensitive_success = total_success - reader_success
    return {
        "method": method,
        "order": order,
        "domain": domain,
        "run": run,
        "tasks": len(matrix),
        "success": total_success,
        "success_rate": rate(total_success, len(matrix)),
        "failures": all_fail,
        "non_sensitive_tasks": non_sensitive_tasks,
        "non_sensitive_success": non_sensitive_success,
        "non_sensitive_success_rate": rate(non_sensitive_success, non_sensitive_tasks),
        "sensitive_readers": len(reader_rows),
        "sensitive_reader_failures": reader_fail,
        "static_at_risk_readers": len(at_risk),
        "lower_bound_exposed_readers": len(exposed),
        "lower_bound_exposed_failures": exposed_fail,
        "exposed_failure_rate": rate(exposed_fail, len(exposed)),
        "clean_readers": len(clean),
        "clean_reader_failures": sum(not row["success"] for row in clean),
        "clean_reader_failure_rate": rate(sum(not row["success"] for row in clean), len(clean)),
        "fraction_all_failures_in_lower_bound_exposed_readers": rate(exposed_fail, all_fail),
        "reader_rows": reader_rows,
    }


def summarize(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in runs:
        groups[(row["method"], row["order"])].append(row)
    out = []
    for (method, order), rows in sorted(groups.items()):
        tasks = sum(r["tasks"] for r in rows)
        success = sum(r["success"] for r in rows)
        failures = sum(r["failures"] for r in rows)
        readers = sum(r["sensitive_readers"] for r in rows)
        reader_fail = sum(r["sensitive_reader_failures"] for r in rows)
        exposed = sum(r["lower_bound_exposed_readers"] for r in rows)
        exposed_fail = sum(r["lower_bound_exposed_failures"] for r in rows)
        clean = sum(r["clean_readers"] for r in rows)
        clean_fail = sum(r["clean_reader_failures"] for r in rows)
        static_risk = sum(r["static_at_risk_readers"] for r in rows)
        non_sensitive_tasks = sum(r["non_sensitive_tasks"] for r in rows)
        non_sensitive_success = sum(r["non_sensitive_success"] for r in rows)
        out.append({
            "method": method,
            "order": order,
            "runs": len(rows),
            "task_units": tasks,
            "success_rate": rate(success, tasks),
            "failures": failures,
            "non_sensitive_task_units": non_sensitive_tasks,
            "non_sensitive_success_rate": rate(non_sensitive_success, non_sensitive_tasks),
            "sensitive_reader_units": readers,
            "sensitive_reader_failure_rate": rate(reader_fail, readers),
            "static_at_risk_reader_units": static_risk,
            "lower_bound_exposed_reader_units": exposed,
            "lower_bound_exposed_reader_failure_rate": rate(exposed_fail, exposed),
            "clean_reader_units": clean,
            "clean_reader_failure_rate": rate(clean_fail, clean),
            "lower_bound_exposed_failures": exposed_fail,
            "fraction_all_failures_in_lower_bound_exposed_readers": rate(exposed_fail, failures),
        })
    return out


def order_contrasts(summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by = {(row["method"], row["order"]): row for row in summary}
    contrasts = []
    for method in METHODS:
        base = by[(method, "ordinal")]
        for order in ("shuffle1", "shuffle2"):
            row = by[(method, order)]
            contrasts.append({
                "method": method,
                "order": order,
                "ordinal_success_rate": base["success_rate"],
                "shuffle_success_rate": row["success_rate"],
                "observed_success_drop": round((base["success_rate"] or 0) - (row["success_rate"] or 0), 6),
                "ordinal_non_sensitive_success_rate": base["non_sensitive_success_rate"],
                "shuffle_non_sensitive_success_rate": row["non_sensitive_success_rate"],
                "non_sensitive_success_drop": round((base["non_sensitive_success_rate"] or 0) - (row["non_sensitive_success_rate"] or 0), 6),
                "gap_reduction_after_excluding_sensitive_readers": round(((base["success_rate"] or 0) - (row["success_rate"] or 0)) - ((base["non_sensitive_success_rate"] or 0) - (row["non_sensitive_success_rate"] or 0)), 6),
                "fraction_observed_gap_removed_by_sensitive_reader_exclusion": round(((((base["success_rate"] or 0) - (row["success_rate"] or 0)) - ((base["non_sensitive_success_rate"] or 0) - (row["non_sensitive_success_rate"] or 0))) / ((base["success_rate"] or 0) - (row["success_rate"] or 0))), 6) if ((base["success_rate"] or 0) - (row["success_rate"] or 0)) > 0 else None,
                "ordinal_sensitive_reader_failure_rate": base["sensitive_reader_failure_rate"],
                "shuffle_sensitive_reader_failure_rate": row["sensitive_reader_failure_rate"],
                "shuffle_lower_bound_exposed_reader_units": row["lower_bound_exposed_reader_units"],
                "shuffle_lower_bound_exposed_reader_failure_rate": row["lower_bound_exposed_reader_failure_rate"],
                "shuffle_clean_reader_failure_rate": row["clean_reader_failure_rate"],
                "fraction_shuffle_failures_in_lower_bound_exposed_readers": row["fraction_all_failures_in_lower_bound_exposed_readers"],
            })
    return contrasts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interference-audit", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--vendor-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if args.vendor_dir:
        sys.path.insert(0, str(args.vendor_dir))
    audit = json.loads(args.interference_audit.read_text(encoding="utf-8"))
    annotations = {int(row["task_id"]): row for row in audit["task_annotations"]}
    specs: list[tuple[str, str, str, str, str]] = []
    for method in METHODS:
        for order in ORDERS:
            for run in RUNS:
                for domain in DOMAINS:
                    specs.append((method, order, domain, run, parquet_path(method, order, domain, run)))
    # Baseline is retained as the ordinal reference; shuffled baseline is the missing decisive control.
    for run in RUNS:
        for domain in DOMAINS:
            specs.append(("wa_baseline", "ordinal", domain, run, baseline_path(domain, run)))

    matrices: dict[tuple[str, str, str, str], dict[int, bool]] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(load_column_matrix, spec[4], args.cache_dir): spec for spec in specs}
        for future in as_completed(futures):
            method, order, domain, run, _ = futures[future]
            matrices[(method, order, domain, run)] = future.result()

    run_rows = []
    for method, order, domain, run, _ in specs:
        run_rows.append(analyze_run(method, order, domain, run, matrices[(method, order, domain, run)], annotations))
    summary = summarize(run_rows)
    contrasts = order_contrasts(summary)
    shuffled_memory_runs = [r for r in run_rows if r["method"] in METHODS and r["order"] != "ordinal"]
    lower_exposed = sum(r["lower_bound_exposed_readers"] for r in shuffled_memory_runs)
    lower_exposed_fail = sum(r["lower_bound_exposed_failures"] for r in shuffled_memory_runs)
    all_shuffle_fail = sum(r["failures"] for r in shuffled_memory_runs)
    report = {
        "schema_version": "1.0",
        "generated_at": now(),
        "status": "RELEASED_TRAJECTORY_RETROSPECTIVE_COMPLETE",
        "scientific_authority": False,
        "policy": {
            "released_author_trajectories_only": True,
            "writer_success_uses_benchmark_is_successful_and_is_therefore_a_lower_bound": True,
            "known_side_effecting_scorer_failures_are_not_counted_in_aggregate_exposure": True,
            "static_interference_classifier_is_conservative_and_not_ground_truth": True,
            "no_memory_shuffle_control_still_required_for_causal_decomposition": True,
        },
        "summary": {
            "run_domain_cells": len(run_rows),
            "memory_shuffle_run_domain_cells": len(shuffled_memory_runs),
            "lower_bound_exposed_reader_units_in_memory_shuffles": lower_exposed,
            "lower_bound_exposed_reader_failures_in_memory_shuffles": lower_exposed_fail,
            "fraction_memory_shuffle_failures_in_lower_bound_exposed_readers": rate(lower_exposed_fail, all_shuffle_fail),
        },
        "order_summary": summary,
        "order_contrasts": contrasts,
        "run_domain_rows": run_rows,
        "claim_boundary": {
            "supported_if_nonzero": "Released trajectories contain outcome failures on state-sensitive tasks after earlier benchmark-successful tasks mutated overlapping persistent environment state; this is a conservative lower bound because scorer-failed tasks can also mutate state.",
            "not_supported": "Removing environment carryover would recover the full reported shuffle gap, because the shuffled no-memory control has not been run.",
        },
        "authority": {"problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "summary": report["summary"], "order_summary": summary, "order_contrasts": contrasts}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
