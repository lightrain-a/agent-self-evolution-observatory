#!/usr/bin/env python3
"""Bind private CSV durability mirrors to the R25 no-interim R19 checkpoint."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
RECEIPT_ID = "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-CSV-DURABILITY-R25"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts-csv", type=Path, required=True)
    ap.add_argument("--progress-csv", type=Path, required=True)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-csv-durability-r25.json"))
    a = ap.parse_args()
    ck = json.loads(a.checkpoint.read_text(encoding="utf-8"))
    if ck.get("receipt_id") != "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-PARTIAL-CHECKPOINT-R25":
        raise RuntimeError("checkpoint receipt identity drift")
    n = int(ck["execution"]["episodes_complete"])
    ar, pr = rows(a.attempts_csv), rows(a.progress_csv)
    if ar != n or pr != n:
        raise RuntimeError(f"CSV row-count drift: attempts={ar}, progress={pr}, checkpoint={n}")
    if ck["interim_policy"]["task_deltas_computed"] is not False or ck["interim_policy"]["effect_mean_computed"] is not False:
        raise RuntimeError("checkpoint is not no-interim-inference")
    out = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": RECEIPT_ID,
        "status": "R19_PRIVATE_CSV_DURABILITY_CHECKPOINT_BOUND_NO_INTERIM_INFERENCE",
        "checkpoint_sha256": sha(a.checkpoint),
        "episodes_complete": n,
        "complete_independent_tasks": int(ck["execution"]["complete_independent_tasks"]),
        "next_sequence_index": int(ck["execution"]["next_sequence_index"]),
        "private_csv": {
            "attempts_rows": ar,
            "attempts_csv_sha256": sha(a.attempts_csv),
            "progress_rows": pr,
            "progress_csv_sha256": sha(a.progress_csv),
            "contents_embedded_publicly": False,
            "private_paths_embedded_publicly": False,
        },
        "interim_policy": {
            "terminal_scores_exposed": False,
            "task_deltas_computed": False,
            "effect_mean_computed": False,
            "p_value_computed": False,
            "confidence_interval_computed": False,
        },
        "scientific_verdict": "NO_VERDICT_DURABILITY_CHECKPOINT_ONLY",
    }
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "rows": n, "next": out["next_sequence_index"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
