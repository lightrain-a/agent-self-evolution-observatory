#!/usr/bin/env python3
"""Adjudicate exhausted pre-exposure support retry at R19 sequence 29.

This receipt is support/control evidence only. It does not inspect or summarize
terminal scores and it forbids further execution of the current R19
confirmatory attempt once the single exact pre-exposure retry is exhausted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
RECEIPT_ID = "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-SEQ029-PREEXPOSURE-RETRY-EXHAUSTION-R31"
STATUS = "SEQ029_PREEXPOSURE_SUPPORT_FAILURE_EXACT_RETRY_EXHAUSTED_R19_STOPPED"
VERDICT = "NO_VERDICT_PREOUTCOME_SUPPORT_FAILURE_RETRY_EXHAUSTED"
EXPECTED_ATTEMPT1_SHA = "6ed109898606969797019806dd84d31e23b01e94c501c626e3f1b7386e8c8f21"
EXPECTED_ATTEMPT2_SHA = "c605c7e7eb1563ce7d951cd8eb9e6c0e38491175bf88b133f84527b1b3a734bf"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def build(run_root: Path) -> dict[str, Any]:
    attempt1_path = run_root / "pre-exposure-support-failures" / "seq029-attempt1.json"
    attempt2_path = run_root / "pre-exposure-support-failures" / "seq029-attempt2.json"
    if sha(attempt1_path) != EXPECTED_ATTEMPT1_SHA:
        raise RuntimeError("seq29 attempt1 receipt SHA drift")
    if sha(attempt2_path) != EXPECTED_ATTEMPT2_SHA:
        raise RuntimeError("seq29 attempt2 receipt SHA drift")
    a1, a2 = read_json(attempt1_path), read_json(attempt2_path)
    for idx, obj in enumerate((a1, a2), start=1):
        if int(obj.get("sequence_index", -1)) != 29:
            raise RuntimeError(f"seq29 attempt{idx} sequence drift")
        if str(obj.get("task_id")) != "147" or str(obj.get("source_task_id")) != "148":
            raise RuntimeError(f"seq29 attempt{idx} task/source drift")
        if obj.get("status") != "R19_PRE_EXPOSURE_RESET_SUPPORT_FAILURE":
            raise RuntimeError(f"seq29 attempt{idx} status drift")
        if obj.get("scientific_exposure") is not False:
            raise RuntimeError(f"seq29 attempt{idx} opened scientific exposure")

    attempts = read_jsonl(run_root / "attempts.jsonl")
    progress = read_jsonl(run_root / "progress.jsonl")
    if len(attempts) != 29 or len(progress) != 29:
        raise RuntimeError("R19 prefix must remain exactly 29/29 at retry exhaustion")
    if [int(x["sequence_index"]) for x in attempts] != list(range(29)):
        raise RuntimeError("attempt ledger is not exact 0..28 prefix")
    if [int(x["sequence_index"]) for x in progress] != list(range(29)):
        raise RuntimeError("progress ledger is not exact 0..28 prefix")
    if (run_root / "failure.json").exists():
        raise RuntimeError("post-STARTED failure receipt unexpectedly exists")

    complete_tasks: dict[str, int] = {}
    for row in progress:
        complete_tasks[str(row["task_id"])] = complete_tasks.get(str(row["task_id"]), 0) + 1
    complete_task_count = sum(v == 4 for v in complete_tasks.values())
    if complete_task_count != 7:
        raise RuntimeError("expected seven complete independent tasks in 29-episode prefix")
    if complete_tasks.get("147") != 1:
        raise RuntimeError("task147 must have exactly one completed episode before seq29 support exhaustion")

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": RECEIPT_ID,
        "recorded_at": now(),
        "status": STATUS,
        "support_failure_chain": {
            "sequence_index": 29,
            "task_id": "147",
            "source_task_id": "148",
            "first_attempt": {
                "receipt_sha256": EXPECTED_ATTEMPT1_SHA,
                "scientific_exposure": False,
                "model_completions": 0,
                "browser_actions": 0,
                "evaluator_calls": 0,
            },
            "exact_retry_attempt": {
                "receipt_sha256": EXPECTED_ATTEMPT2_SHA,
                "scientific_exposure": False,
                "model_completions": 0,
                "browser_actions": 0,
                "evaluator_calls": 0,
            },
            "exact_retry_consumed": True,
            "additional_retry_permitted": False,
        },
        "durable_prefix": {
            "episodes_complete": 29,
            "episodes_expected": 140,
            "complete_independent_tasks": 7,
            "current_incomplete_task_id": "147",
            "current_incomplete_task_completed_episodes": 1,
            "last_complete_sequence_index": 28,
            "attempts_jsonl_sha256": sha(run_root / "attempts.jsonl"),
            "progress_jsonl_sha256": sha(run_root / "progress.jsonl"),
            "run_contract_sha256": sha(run_root / "run-contract.json"),
            "summary_sha256": sha(run_root / "summary.json"),
            "agent_completions": sum(int(x.get("agent_completion_count") or 0) for x in progress),
            "fuzzy_evaluator_completions": sum(int(x.get("fuzzy_evaluator_completion_count") or 0) for x in progress),
            "terminal_scores_exposed_in_receipt": False,
        },
        "adjudication": {
            "current_R19_confirmatory_execution_stopped": True,
            "resume_sequence29_under_current_R19": False,
            "execute_sequence30_or_later_under_current_R19": False,
            "partial_29_episode_prefix_may_enter_confirmatory_analysis": False,
            "task_deltas_may_be_computed": False,
            "effect_mean_may_be_computed": False,
            "p_value_may_be_computed": False,
            "confidence_interval_may_be_computed": False,
            "support_failure_is_scientific_negative": False,
            "no_effect_claim_authorized": False,
            "R19_current_attempt_retriable": False,
        },
        "reopen_condition": {
            "current_R19_may_not_resume": True,
            "future_work_requires_new_experiment_contract": True,
            "future_work_requires_new_explicit_scientific_and_execution_authority": True,
            "support_must_be_restored_before_new_benchmark_exposure": True,
            "partial_R19_outcomes_must_not_select_new_tasks_thresholds_endpoints_or_models": True,
            "R18_or_R19_partial_outcomes_must_not_be_pooled_into_new_confirmatory_sample": True,
        },
        "scientific_verdict": VERDICT,
        "scientific_negative": False,
        "scientific_claim_authority": False,
        "submission_authority": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-seq029-preexposure-retry-exhaustion-r31.json"))
    ap.add_argument("--stop-marker", type=Path, required=True)
    a = ap.parse_args()
    out = build(a.run_root)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    marker = {
        "schema_version": "1.0",
        "status": "R19_CONFIRMATORY_EXECUTION_PERMANENTLY_STOPPED",
        "reason": STATUS,
        "adjudication_receipt_sha256": sha(a.output),
        "episodes_complete": 29,
        "last_complete_sequence_index": 28,
        "resume_under_current_contract": False,
    }
    a.stop_marker.parent.mkdir(parents=True, exist_ok=True)
    a.stop_marker.write_text(json.dumps(marker, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "verdict": out["scientific_verdict"], "episodes_complete": 29, "retry_exhausted": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
