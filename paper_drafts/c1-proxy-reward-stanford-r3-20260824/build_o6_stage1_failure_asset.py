#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_PARENT_DESIGN_SHA = "e33996f4e4f00da7b162bf7e9c26ca004aaf7e5d04f2547aacbc04f47ad05c1e"
EXPECTED_PARENT_CONTRACT_SHA = "7103efdbf1739638d815f9b0960462d7302821c91c063f42c5a6fcd331b46bfa"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True, type=Path)
    ap.add_argument("--design", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    if sha(args.design) != EXPECTED_PARENT_DESIGN_SHA:
        raise RuntimeError("parent O6 design SHA drift")
    contract_path = args.run_root / "o6-stage1-contract.json"
    if sha(contract_path) != EXPECTED_PARENT_CONTRACT_SHA:
        raise RuntimeError("parent Stage-1 contract SHA drift")

    stages = [load(p) for p in sorted((args.run_root / "private/stages").glob("*.json"))]
    if not stages:
        raise RuntimeError("no Stage-1 stage receipts found")
    statuses = Counter(str(r.get("status")) for r in stages)
    incomplete = [r for r in stages if r.get("status") == "provider_state_failure"]
    incomplete_ids = sorted({str((r.get("provider_receipt") or {}).get("response_id") or "") for r in incomplete if (r.get("provider_receipt") or {}).get("response_id")})
    incomplete_reasons = Counter(str((r.get("provider_receipt") or {}).get("incomplete_reason") or "") for r in incomplete)
    raw_files = sorted((args.run_root / "private/raw").rglob("*.txt"))
    response_archives = sorted((args.run_root / "private/provider-responses").glob("*.json"))

    if len(incomplete) < 2 or incomplete_reasons.get("length", 0) < 2:
        raise RuntimeError("expected repeated length-censoring evidence was not found")
    for row in incomplete:
        receipt = row.get("provider_receipt") or {}
        if receipt.get("requested_model") != "glm-5.3" or receipt.get("resolved_model") != "glm-5.3":
            raise RuntimeError("incomplete response model binding drift")

    # Because two runner processes overlapped after the transport 502 and the parent harness lacked a transaction lock,
    # exact POST count is not reconstructible from overwritten per-stage response receipts. Distinct content archives plus
    # distinct incomplete response IDs form a conservative observable lower bound.
    provider_calls_lower_bound = len(raw_files) + len(incomplete_ids)

    payload = {
        "schema_version": "1.0",
        "artifact_type": "execution-and-operationalization-failure-asset",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "objection_id": "PROXY-O6",
        "parent_design_sha256": EXPECTED_PARENT_DESIGN_SHA,
        "parent_contract_sha256": EXPECTED_PARENT_CONTRACT_SHA,
        "status": "STAGE1_STOP_OUTPUT_CAP_CENSORING_PLUS_CONCURRENCY_RACE",
        "scientific_decision": "STOP_PARENT_STAGE1_NO_STAGE2_AUTHORITY",
        "observed_stage_receipts": len(stages),
        "stage_status_counts": dict(sorted(statuses.items())),
        "provider_incomplete": {
            "count": len(incomplete),
            "response_ids_archived": len(incomplete_ids),
            "reason_counts": dict(sorted(incomplete_reasons.items())),
            "tasks_and_labels": [{"task_id": r.get("task_id"), "label": r.get("label"), "reason": (r.get("provider_receipt") or {}).get("incomplete_reason")} for r in incomplete],
            "get_only_diagnosis": "Both inspected incomplete responses are final status=incomplete with output_tokens=2200, reasoning_tokens=0, no assistant text, and resolved_model=glm-5.3.",
        },
        "execution_concurrency_failure": {
            "transport_event": "MCP/SSH invocation returned HTTP 502 while the remote runner continued executing.",
            "overlapping_runner_processes_observed": 2,
            "parent_harness_transaction_lock_present": False,
            "distinct_raw_content_archives": len(raw_files),
            "per_stage_provider_response_archives": len(response_archives),
            "exact_provider_post_count_reconstructible": False,
            "provider_post_count_observable_lower_bound": provider_calls_lower_bound,
            "why_lower_bound_only": "Concurrent processes could POST the same stage before either wrote its stage receipt. Response archives are keyed by stage and can be overwritten, while identical duplicate outputs can also collapse to the same content hash."
        },
        "failure_layer": "operationalization-plus-execution",
        "scientific_interpretation": "The parent Stage-1 gate cannot pass because repeated failure-label requests are censored exactly at the frozen 2200-output-token cap. This is not evidence that GLM-5.3 lacks reward-conditioned write divergence; the paired scientific outcome is missing for those units.",
        "single_repair_child_allowed": {
            "changed_scientific_variable": "writer max_output_tokens only: 2200 -> 4096 for all eight fresh GLM-5.3 writes",
            "execution_only_repairs": ["add nonblocking single-writer transaction lock", "stop immediately after any scientifically incomplete provider response", "archive provider response before local validation"],
            "unchanged": ["four source trajectories", "task prompts", "historical action-summary algorithm", "ReasoningBank success/failure prompts", "GLM-5.3 writer", "temperature=0", "thinking omitted", "Stage-1 content/title gates", "Stage-2 0.15 and p<0.05 gate"],
            "if_4096_still_length_incomplete": "STOP_CROSS_WRITER_NO_FURTHER_TOKEN_CAP_RESCUE"
        },
        "scientific_authority": False,
        "principle_update_authority": False,
        "stage2_experiment_authority": False
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
