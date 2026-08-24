#!/usr/bin/env python3
"""Run exactly two authorized nonbenchmark transport completions for B1/R19."""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.failure_memory_reasoningbank_r19_execution_authority_r21 import require_authority

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
EXPECTED_CONTRACT_SHA = "ed803f0958002ab2095563a56cff6328a054ff4c4d7bd9fc18fc97bb3bdc3282"
ALIASES = ["gpt-4", "gpt-4-1106-preview"]
PROMPT = "Nonbenchmark transport check. Reply with one short acknowledgement."


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def complete(base: str, model: str, *, timeout_seconds: int) -> dict[str, Any]:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "temperature": 0,
        "max_tokens": 16,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        base.rstrip("/") + "/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer ollama"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as r:
        raw = r.read()
        status = int(r.status)
    obj = json.loads(raw)
    content = str(obj["choices"][0]["message"].get("content") or "")
    if status != 200 or not content.strip():
        raise RuntimeError(f"synthetic smoke failed for {model}: HTTP {status}, empty={not bool(content.strip())}")
    return {
        "alias": model,
        "http_status": status,
        "assistant_nonempty": True,
        "assistant_chars": len(content),
        "assistant_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "semantic_content_retained": False,
    }


def execute(a: argparse.Namespace) -> dict[str, Any]:
    authority = require_authority(a.authority)
    if sha(a.contract) != EXPECTED_CONTRACT_SHA:
        raise RuntimeError("R19 contract SHA drift")
    support = json.loads(a.support_receipt.read_text(encoding="utf-8"))
    if support.get("status") != "R19_PREBENCHMARK_ZERO_COMPLETION_SUPPORT_GATE_PASS":
        raise RuntimeError("R19 zero-completion support gate not passed")
    if support["bindings"]["authority_artifact_sha256"] != authority["artifact_sha256"]:
        raise RuntimeError("support/authority mismatch")
    timeout_receipt = json.loads(a.timeout_receipt.read_text(encoding="utf-8"))
    if timeout_receipt.get("status") != "PREBENCHMARK_SYNTHETIC_TRANSPORT_TIMEOUT_ZERO_COMPLETION_EXACT_RETRY_ALLOWED":
        raise RuntimeError("synthetic timeout adjudication missing")
    if timeout_receipt["bindings"]["authority_artifact_sha256"] != authority["artifact_sha256"]:
        raise RuntimeError("timeout receipt/authority mismatch")
    rows = [complete(a.ollama_base, alias, timeout_seconds=a.timeout_seconds) for alias in ALIASES]
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-SYNTHETIC-SMOKES-R21",
        "recorded_at": now(),
        "status": "R19_TWO_FIXED_NONBENCHMARK_SYNTHETIC_COMPLETION_SMOKES_PASS",
        "bindings": {
            "r19_contract_sha256": EXPECTED_CONTRACT_SHA,
            "prebenchmark_support_receipt_sha256": sha(a.support_receipt),
            "authority_artifact_sha256": authority["artifact_sha256"],
            "first_transport_timeout_receipt_sha256": sha(a.timeout_receipt),
        },
        "prompt": {
            "benchmark_content_present": False,
            "prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
            "semantic_response_used_for_selection": False,
        },
        "smokes": rows,
        "transport_request_attempts": 3,
        "first_alias_exact_retry_used": True,
        "completion_count": 2,
        "budget": {"authorized_successful_completions": 2, "consumed_successful_completions": 2, "remaining_successful_completions": 0, "precompletion_transport_retry_used": 1},
        "gate": {
            "both_transport_paths_pass": True,
            "benchmark_execution_support_gate_pass": True,
            "scientific_claim_prejudged": False,
        },
        "scientific_verdict": "NO_VERDICT_TRANSPORT_SUPPORT_ONLY",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--authority", type=Path, required=True)
    p.add_argument("--contract", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-contract.json"))
    p.add_argument("--support-receipt", type=Path, required=True)
    p.add_argument("--ollama-base", default="http://127.0.0.1:11444")
    p.add_argument("--timeout-receipt", type=Path, required=True)
    p.add_argument("--timeout-seconds", type=int, default=300)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-synthetic-smokes-r21.json"))
    a = p.parse_args()
    out = execute(a)
    a.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "completion_count": 2, "benchmark_gate": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
