"""Prospective transport-only pacing repair for untouched Qwen source units.

The repair is motivated solely by persisted provider rate-limit receipts and usage
metadata.  It never changes model identity, sampling, prompt/messages, tool/action
semantics, task order, task eligibility, retries, or replacements.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
SOURCE_CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-contract-20260901.json"
SOURCE_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-index-20260901.json"
SOURCE_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-trajectories-20260901"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-provider-pacing-contract-20260902.json"
EXPECTED_CONTRACT_SHA256 = "b88dbaf8717117fb92e465d7a998b3c43eb131994898396e1ab3ef94e6dfc255"
ACTIVE_FROM_ORDINAL = 8
TARGET_INPUT_TOKENS_PER_MINUTE = 400_000
TRIGGER_ORDINALS = (3, 6, 7)


def source_receipt_path(ordinal: int) -> Path:
    matches = sorted(SOURCE_DIR.glob(f"{ordinal:02d}-*.json"))
    if len(matches) != 1:
        raise RuntimeError(f"pacing trigger/source receipt is not unique at ordinal {ordinal}")
    return matches[0]


def rate_limit_failure(receipt: dict[str, Any]) -> dict[str, Any]:
    trajectory = receipt.get("trajectory") or {}
    failure = trajectory.get("failure") or {}
    safe = failure.get("safe_receipt") or {}
    detail = safe.get("detail") or {}
    error = detail.get("error") or {}
    if receipt.get("execution_status") != "TERMINAL_PROVIDER_OR_POLICY_FAILURE":
        raise RuntimeError("pacing trigger is not a terminal provider/policy failure")
    if failure.get("failure_layer") != "provider" or error.get("code") != "rate_limit_exceeded":
        raise RuntimeError("pacing trigger is not rate_limit_exceeded")
    if failure.get("ambiguous_generation_reissued") is not False:
        raise RuntimeError("pacing trigger has ambiguous or reissued generation")
    if (receipt.get("container_cleanup_receipt") or {}).get("accepted") is not True:
        raise RuntimeError("pacing trigger cleanup is not accepted")
    return {
        "error_code": "rate_limit_exceeded",
        "status_code": safe.get("status_code"),
        "model_call_count": trajectory.get("model_call_count"),
        "accepted_response_count": trajectory.get("accepted_response_count"),
    }


def usage_summary_through_hold() -> dict[str, Any]:
    source_index = json.loads(SOURCE_INDEX.read_text(encoding="utf-8"))
    if source_index.get("completed_count") != ACTIVE_FROM_ORDINAL - 1:
        raise RuntimeError("pacing repair must freeze at the ordinal-7 clean hold")
    if source_index.get("inflight") is not None or source_index.get("execution_complete") is True:
        raise RuntimeError("pacing repair requires clean incomplete source boundary")
    rows = []
    total_input = total_output = total_calls = total_accepted = 0
    for ordinal in range(1, ACTIVE_FROM_ORDINAL):
        path = source_receipt_path(ordinal)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        trajectory = receipt.get("trajectory") or {}
        responses = trajectory.get("responses") or []
        input_tokens = sum(int((row.get("usage") or {}).get("input_tokens") or 0) for row in responses)
        output_tokens = sum(int((row.get("usage") or {}).get("output_tokens") or 0) for row in responses)
        calls = int(trajectory.get("model_call_count") or 0)
        accepted = int(trajectory.get("accepted_response_count") or 0)
        total_input += input_tokens
        total_output += output_tokens
        total_calls += calls
        total_accepted += accepted
        rows.append({
            "ordinal": ordinal,
            "instance_id": receipt.get("instance_id"),
            "execution_status": receipt.get("execution_status"),
            "receipt_sha256": sha256_file(path),
            "model_call_count": calls,
            "accepted_response_count": accepted,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        })
    return {
        "completed_source_count": len(rows),
        "total_model_call_count": total_calls,
        "total_accepted_response_count": total_accepted,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "per_source_non_outcome_usage": rows,
    }


def contract_payload() -> dict[str, Any]:
    source_contract = json.loads(SOURCE_CONTRACT.read_text(encoding="utf-8"))
    source_index = json.loads(SOURCE_INDEX.read_text(encoding="utf-8"))
    usage = usage_summary_through_hold()
    triggers = []
    for ordinal in TRIGGER_ORDINALS:
        path = source_receipt_path(ordinal)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        triggers.append({
            "ordinal": ordinal,
            "instance_id": receipt["instance_id"],
            "receipt_sha256": sha256_file(path),
            **rate_limit_failure(receipt),
        })
    plan = list(source_contract.get("source_plan") or [])
    if len(plan) != 32 or int(plan[ACTIVE_FROM_ORDINAL - 1]["ordinal"]) != ACTIVE_FROM_ORDINAL:
        raise RuntimeError("source plan drift for pacing repair")
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_PROVIDER_TRANSPORT_PACING_REPAIR",
        "created_at_utc": utcnow(),
        "decision": "QWEN_SOURCE_PROVIDER_PACING_REPAIR_AUTHORIZED",
        "source_contract_sha256": sha256_file(SOURCE_CONTRACT),
        "source_index_hold_sha256": sha256_file(SOURCE_INDEX),
        "source_index_completed_count": source_index["completed_count"],
        "trigger_rate_limit_receipts": triggers,
        "non_outcome_usage_evidence": usage,
        "repair": {
            "active_from_source_ordinal": ACTIVE_FROM_ORDINAL,
            "target_input_tokens_per_minute": TARGET_INPUT_TOKENS_PER_MINUTE,
            "algorithm": (
                "before each provider call after the first accepted response in a trajectory, "
                "let min_interval = previous_response_input_tokens * 60 / target_input_tokens_per_minute; "
                "sleep max(0, min_interval - elapsed_since_previous_provider_call_start)"
            ),
            "previous_usage_source": "provider-reported input_tokens from immediately preceding accepted response",
            "missing_previous_input_tokens_policy": "fail closed before the next provider call",
            "request_payload_changed": False,
            "messages_changed": False,
            "model_changed": False,
            "sampling_changed": False,
            "max_output_tokens_changed": False,
            "task_order_changed": False,
            "task_eligibility_changed": False,
            "retry_enabled": False,
            "replacement_enabled": False,
        },
        "scientific_boundary": {
            "completed_source_receipts_1_through_7_immutable": True,
            "source_ordinals_8_through_32_outcomes_unobserved_at_freeze": True,
            "provider_failure_and_usage_metadata_only": True,
            "evaluator_outcomes_used_to_design_repair": False,
            "source_retry_authorized": False,
            "source_replacement_authorized": False,
            "memory_extraction_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable source pacing contract")
    payload = contract_payload()
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "active_from_source_ordinal": payload["repair"]["active_from_source_ordinal"],
        "target_input_tokens_per_minute": payload["repair"]["target_input_tokens_per_minute"],
    }


def require_pacing(next_source_ordinal: int) -> dict[str, Any] | None:
    if next_source_ordinal < ACTIVE_FROM_ORDINAL:
        return None
    if not CONTRACT.is_file():
        raise RuntimeError("SOURCE_PROVIDER_PACING_REPAIR_REQUIRED")
    if EXPECTED_CONTRACT_SHA256 == "PENDING":
        raise RuntimeError("source pacing contract SHA not pinned")
    if sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("source pacing contract SHA drift")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("decision") != "QWEN_SOURCE_PROVIDER_PACING_REPAIR_AUTHORIZED":
        raise RuntimeError("source pacing repair gate closed")
    if contract.get("source_contract_sha256") != sha256_file(SOURCE_CONTRACT):
        raise RuntimeError("source pacing/source contract binding drift")
    repair = contract.get("repair") or {}
    if int(repair.get("active_from_source_ordinal") or 0) != ACTIVE_FROM_ORDINAL:
        raise RuntimeError("source pacing active ordinal drift")
    if int(repair.get("target_input_tokens_per_minute") or 0) != TARGET_INPUT_TOKENS_PER_MINUTE:
        raise RuntimeError("source pacing target drift")
    if repair.get("request_payload_changed") is not False or repair.get("sampling_changed") is not False:
        raise RuntimeError("source pacing repair is not transport-only")
    return {
        "active_from_source_ordinal": ACTIVE_FROM_ORDINAL,
        "target_input_tokens_per_minute": TARGET_INPUT_TOKENS_PER_MINUTE,
        "contract_sha256": EXPECTED_CONTRACT_SHA256,
        "algorithm": repair["algorithm"],
    }


def main() -> None:
    print(json.dumps(freeze_contract(), sort_keys=True))


if __name__ == "__main__":
    main()
