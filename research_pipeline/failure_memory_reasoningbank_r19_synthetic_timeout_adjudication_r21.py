#!/usr/bin/env python3
"""Adjudicate the first R19 synthetic transport timeout before any completion."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from research_pipeline.failure_memory_reasoningbank_r19_execution_authority_r21 import require_authority

EXPECTED_SUPPORT_SHA = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--authority", type=Path, required=True)
    p.add_argument("--support-receipt", type=Path, required=True)
    p.add_argument("--ollama-log", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-synthetic-timeout-r21.json"))
    a = p.parse_args()
    auth = require_authority(a.authority)
    support = json.loads(a.support_receipt.read_text(encoding="utf-8"))
    if support.get("status") != "R19_PREBENCHMARK_ZERO_COMPLETION_SUPPORT_GATE_PASS":
        raise RuntimeError("prebenchmark support receipt drift")
    text = a.ollama_log.read_text(encoding="utf-8", errors="replace")
    required = [
        "client connection closed before server finished loading, aborting load",
        'error="timed out waiting for llama runner to start: context canceled"',
        'POST     "/v1/chat/completions"',
        "| 499 |",
    ]
    if not all(x in text for x in required):
        raise RuntimeError("Ollama zero-completion timeout evidence missing")
    out = {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-SYNTHETIC-TIMEOUT-R21",
        "recorded_at": now(),
        "status": "PREBENCHMARK_SYNTHETIC_TRANSPORT_TIMEOUT_ZERO_COMPLETION_EXACT_RETRY_ALLOWED",
        "bindings": {
            "prebenchmark_support_receipt_sha256": sha(a.support_receipt),
            "authority_artifact_sha256": auth["artifact_sha256"],
            "ollama_log_sha256": sha(a.ollama_log),
        },
        "failed_attempt": {
            "alias": "gpt-4",
            "request_semantics_changed": False,
            "client_timeout_seconds": 120,
            "server_http_status_after_client_close": 499,
            "failure_stage": "initial model load before server became available",
            "server_aborted_load_after_client_close": True,
            "assistant_completion_observed": False,
            "successful_completion_budget_consumed": 0,
            "benchmark_content_present": False,
            "browser_action": False,
            "evaluator_call": False,
            "benchmark_outcome": False,
        },
        "frozen_retry_rule_application": {
            "failure_before_first_model_completion_browser_action_or_evaluator_call": True,
            "one_exact_retry_allowed": True,
            "exact_retry_remaining": 1,
            "same_model_alias_required": True,
            "same_prompt_and_generation_parameters_required": True,
            "only_client_wait_window_may_be_extended_for_model_load": True,
            "model_provider_or_manifest_change": False,
            "benchmark_execution_still_blocked_until_both_synthetic_smokes_pass": True,
        },
        "scientific_verdict": "NO_VERDICT_PREBENCHMARK_SUPPORT_FAILURE_RETRYABLE_ONCE",
    }
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "completed_model_calls": 0, "exact_retry_remaining": 1}, ensure_ascii=False))


if __name__ == "__main__":
    main()
