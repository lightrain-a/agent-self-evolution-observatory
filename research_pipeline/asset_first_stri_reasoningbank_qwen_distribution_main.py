"""Execute the frozen confirmatory schedule in resource-qualified contiguous chunks."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from research_pipeline.asset_first_stri_reasoningbank_p1_core import ROOT, sha256_file
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_behavioral_runner import (
    load_completed, receipt_path, run_plan,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_resource import (
    AUTHORITY, HEADROOM_MULTIPLIER,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
STAGE = "QWEN_CONFIRMATORY_BEHAVIORAL_EXECUTION"
MANIFEST = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-manifest-20260901.json"
SCHEDULE = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-schedule-20260901.json"
STRUCTURAL = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-structural-result-20260901.json"
BANK = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-bank-20260901.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-index-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-runs-20260901"
EXPECTED_AUTHORITY_SHA256 = "PENDING"


def next_chunk(chunks: Sequence[Mapping[str, int]], completed_count: int) -> Mapping[str, int] | None:
    next_ordinal = completed_count + 1
    for chunk in chunks:
        if int(chunk["start_ordinal"]) <= next_ordinal <= int(chunk["end_ordinal"]):
            return chunk
    return None


def consumed_resources(receipts: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    calls, tokens = 0, 0
    for receipt in receipts:
        trajectory = receipt.get("trajectory") or {}
        calls += int(trajectory.get("model_call_count") or 0)
        for response in trajectory.get("responses") or []:
            usage = response.get("usage") or {}
            tokens += int(usage.get("input_tokens") or 0) + int(usage.get("output_tokens") or 0)
    return {"model_calls": calls, "total_tokens": tokens}


def chunk_headroom(authority: Mapping[str, Any], chunk: Mapping[str, int],
                   completed_count: int, consumed: Mapping[str, int]) -> dict[str, Any]:
    remaining_units = int(chunk["end_ordinal"]) - completed_count
    quota = authority["quota_evidence"]
    summary = authority["resource_summary"]
    required_calls = math.ceil(
        float(summary["model_calls"]["p95"]) * remaining_units * HEADROOM_MULTIPLIER)
    required_tokens = math.ceil(
        float(summary["total_tokens"]["p95"]) * remaining_units * HEADROOM_MULTIPLIER)
    request_budget = quota.get("effective_request_budget")
    token_budget = quota.get("effective_token_budget")
    remaining_requests = (None if request_budget is None else
                          int(request_budget) - int(consumed["model_calls"]))
    remaining_tokens = (None if token_budget is None else
                        int(token_budget) - int(consumed["total_tokens"]))
    request_check = (bool(quota["request_budget_proven"])
                     and remaining_requests is not None
                     and remaining_requests >= required_calls)
    token_check = (bool(quota["token_budget_proven"])
                   and remaining_tokens is not None
                   and remaining_tokens >= required_tokens)
    passed = request_check or token_check
    return {
        "chunk_id": int(chunk["chunk_id"]), "remaining_chunk_units": remaining_units,
        "main_consumed_model_calls": int(consumed["model_calls"]),
        "main_consumed_total_tokens": int(consumed["total_tokens"]),
        "remaining_proven_requests": remaining_requests,
        "remaining_proven_tokens": remaining_tokens,
        "required_chunk_p95_headroom_requests": required_calls,
        "required_chunk_p95_headroom_tokens": required_tokens,
        "request_headroom_pass": request_check, "token_headroom_pass": token_check,
        "decision": ("CHUNK_RESOURCE_HEADROOM_PASS" if passed
                     else "CHUNK_RESOURCE_HEADROOM_HOLD"),
    }


def run_next_chunk() -> dict[str, Any]:
    if EXPECTED_AUTHORITY_SHA256 == "PENDING":
        raise RuntimeError("resource authority SHA not pinned")
    if sha256_file(AUTHORITY) != EXPECTED_AUTHORITY_SHA256:
        raise RuntimeError("resource authority SHA drift")
    authority = json.loads(AUTHORITY.read_text())
    if not authority["execution_authorized"]:
        raise RuntimeError("confirmatory execution authority is not open")
    manifest = json.loads(MANIFEST.read_text())
    schedule = json.loads(SCHEDULE.read_text())
    structural = json.loads(STRUCTURAL.read_text())
    bank = json.loads(BANK.read_text())
    if authority["input_hashes"]["schedule"] != sha256_file(SCHEDULE):
        raise RuntimeError("resource authority schedule binding drift")
    if authority["schedule_sha256"] != schedule["schedule_sha256"]:
        raise RuntimeError("scientific schedule semantic hash drift")
    plan = schedule["units"]
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    completed = load_completed(RECEIPT_DIR, plan)
    chunk = next_chunk(authority["operational_chunks"], len(completed))
    if chunk is None:
        if len(completed) != len(plan):
            raise RuntimeError("resource chunk plan does not cover next ordinal")
        return {"decision": f"{STAGE}_COMPLETE", "execution_complete": True,
                "completed_count": len(completed)}
    headroom = chunk_headroom(
        authority, chunk, len(completed), consumed_resources(completed))
    if headroom["decision"] != "CHUNK_RESOURCE_HEADROOM_PASS":
        return {"decision": headroom["decision"], "execution_complete": False,
                "completed_count": len(completed), "headroom": headroom}
    result = run_plan(
        experiment_id=EXPERIMENT_ID, stage=STAGE, contract_path=SCHEDULE,
        expected_contract_sha256=authority["input_hashes"]["schedule"],
        index_path=INDEX, receipt_dir=RECEIPT_DIR, plan=plan,
        sampling=manifest["provider_model"]["sampling"], bank_entries=bank["entries"],
        retrievals=structural["retrievals"],
        stop_after_ordinal=int(chunk["end_ordinal"]))
    result["operational_chunk_id"] = int(chunk["chunk_id"])
    result["chunk_end_ordinal"] = int(chunk["end_ordinal"])
    result["headroom_at_chunk_start"] = headroom
    return result


def main() -> None:
    print(json.dumps(run_next_chunk(), sort_keys=True))


if __name__ == "__main__":
    main()
