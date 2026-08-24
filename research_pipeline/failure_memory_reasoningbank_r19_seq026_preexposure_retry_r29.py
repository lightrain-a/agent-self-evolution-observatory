#!/usr/bin/env python3
"""Adjudicate the single allowed pre-exposure exact retry for R19 sequence 26."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
RECEIPT_ID = "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-SEQ026-PREEXPOSURE-RETRY-R29"
EXPECTED_FAILURE_SHA = "6db0e08ef26006c07f18811833c613832df6196fc647e2e3fe807a6d08d33f2f"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def build(run_root: Path) -> dict:
    failure_path = run_root / "pre-exposure-support-failures" / "seq026-attempt1.json"
    if sha(failure_path) != EXPECTED_FAILURE_SHA:
        raise RuntimeError("seq26 pre-exposure failure SHA drift")
    failure = json.loads(failure_path.read_text(encoding="utf-8"))
    if failure.get("sequence_index") != 26 or failure.get("scientific_exposure") is not False:
        raise RuntimeError("seq26 failure exposure boundary drift")
    attempts = read_jsonl(run_root / "attempts.jsonl")
    progress = read_jsonl(run_root / "progress.jsonl")
    if len(attempts) != len(progress) or len(progress) != 27:
        raise RuntimeError("R29 must be sealed immediately after seq26 completes")
    a = attempts[-1]
    p = progress[-1]
    if int(a.get("sequence_index")) != 26 or int(p.get("sequence_index")) != 26:
        raise RuntimeError("seq26 durable row missing")
    if a.get("task_id") != "530" or a.get("source_task_id") != "529" or a.get("arm") != "STATUS_F":
        raise RuntimeError("seq26 treatment identity drift")
    if p.get("status") != "COMPLETE":
        raise RuntimeError("seq26 retry did not complete")
    if (run_root / "failure.json").exists():
        raise RuntimeError("post-exposure failure exists")
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": RECEIPT_ID,
        "status": "SEQ026_PREEXPOSURE_RESET_FAILURE_EXACT_RETRY_CONSUMED_THEN_COMPLETE",
        "failed_attempt": {
            "receipt_sha256": EXPECTED_FAILURE_SHA,
            "class": failure.get("error_class"),
            "scientific_exposure": False,
            "model_completions": 0,
            "browser_actions": 0,
            "evaluator_calls": 0,
        },
        "retry_adjudication": {
            "frozen_rule": "one exact retry permitted before first model completion/browser action/evaluator call",
            "exact_retry_consumed": True,
            "additional_preexposure_retry_for_sequence26_permitted": False,
            "task_id_unchanged": True,
            "source_task_id_unchanged": True,
            "arm_unchanged": True,
            "memory_unchanged": True,
            "model_unchanged": True,
            "endpoint_unchanged": True,
            "analysis_unchanged": True,
        },
        "durable_result": {
            "attempts_jsonl_sha256": sha(run_root / "attempts.jsonl"),
            "progress_jsonl_sha256": sha(run_root / "progress.jsonl"),
            "sequence26_complete": True,
            "terminal_score_recorded_privately": True,
            "terminal_score_exposed_in_receipt": False,
            "agent_completions": int(p.get("agent_completion_count") or 0),
            "fuzzy_evaluator_completions": int(p.get("fuzzy_evaluator_completion_count") or 0),
        },
        "scientific_verdict": "NO_SEPARATE_VERDICT_SUPPORT_RETRY_ONLY",
        "scientific_claim_authority": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-seq026-preexposure-retry-r29.json"))
    a = ap.parse_args()
    out = build(a.run_root)
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "seq26_complete": True, "retry_consumed": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
