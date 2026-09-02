"""Prospective provider-resume qualification after a terminal source rate limit.

A consumed source unit is never retried or replaced.  This gate only proves that
provider transport is live again before the next untouched source unit is allowed
to run.  Each trigger gets one immutable contract and one exactly-once synthetic
non-benchmark liveness probe.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_agent import (
    MODEL, make_client, safe_response,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_provider import QwenProviderError

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
SOURCE_CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-contract-20260901.json"
SOURCE_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-index-20260901.json"
SOURCE_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-trajectories-20260901"
RESUME_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-provider-resume-20260902"
QUALIFIED_DECISION = "QWEN_SOURCE_PROVIDER_RESUME_QUALIFIED_NEXT_UNTOUCHED_GATE_OPEN"
HOLD_DECISION = "QWEN_SOURCE_PROVIDER_RESUME_HOLD_REMAINING_UNTOUCHED"
EXPECTED_CONTRACT_SHA256_BY_TRIGGER: dict[int, str] = {
    3: "51420cc0397a0bbd438b4d18dea2a660468d94e25e2387c3d9996ee976fc30f4",
}


def contract_path(trigger_ordinal: int) -> Path:
    return RESUME_DIR / f"{trigger_ordinal:02d}-contract.json"


def index_path(trigger_ordinal: int) -> Path:
    return RESUME_DIR / f"{trigger_ordinal:02d}-index.json"


def result_path(trigger_ordinal: int) -> Path:
    return RESUME_DIR / f"{trigger_ordinal:02d}-result.json"


def source_receipt_path(trigger_ordinal: int) -> Path:
    matches = sorted(SOURCE_DIR.glob(f"{trigger_ordinal:02d}-*.json"))
    if len(matches) != 1:
        raise RuntimeError("source resume trigger receipt is not unique")
    return matches[0]


def _rate_limit_code(receipt: dict[str, Any]) -> str:
    trajectory = receipt.get("trajectory") or {}
    failure = trajectory.get("failure") or {}
    safe = failure.get("safe_receipt") or {}
    detail = safe.get("detail") or {}
    error = detail.get("error") or {}
    return str(error.get("code") or "")


def validate_trigger(trigger_ordinal: int) -> tuple[dict[str, Any], dict[str, Any], Path, dict[str, Any]]:
    source_contract = json.loads(SOURCE_CONTRACT.read_text(encoding="utf-8"))
    source_index = json.loads(SOURCE_INDEX.read_text(encoding="utf-8"))
    if source_index.get("execution_complete") is True:
        raise RuntimeError("source execution already complete")
    if source_index.get("inflight") is not None:
        raise RuntimeError("source resume requires a clean no-inflight boundary")
    if int(source_index.get("completed_count") or 0) != trigger_ordinal:
        raise RuntimeError("source resume trigger must be the last completed ordinal")
    journal = list(source_index.get("journal") or [])
    if not journal or int(journal[-1]["ordinal"]) != trigger_ordinal:
        raise RuntimeError("source resume journal trigger drift")
    path = source_receipt_path(trigger_ordinal)
    if sha256_file(path) != journal[-1]["receipt_sha256"]:
        raise RuntimeError("source resume trigger receipt SHA drift")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if receipt.get("execution_status") != "TERMINAL_PROVIDER_OR_POLICY_FAILURE":
        raise RuntimeError("source resume is only authorized for terminal provider/policy failure")
    trajectory = receipt.get("trajectory") or {}
    failure = trajectory.get("failure") or {}
    if failure.get("failure_layer") != "provider":
        raise RuntimeError("source resume trigger is not a provider failure")
    if _rate_limit_code(receipt) != "rate_limit_exceeded":
        raise RuntimeError("source resume trigger is not rate_limit_exceeded")
    if failure.get("ambiguous_generation_reissued") is not False:
        raise RuntimeError("source resume trigger is ambiguous or was reissued")
    cleanup = receipt.get("container_cleanup_receipt") or {}
    if cleanup.get("accepted") is not True:
        raise RuntimeError("source resume trigger cleanup is not accepted")
    plan = list(source_contract.get("source_plan") or [])
    if trigger_ordinal >= len(plan):
        raise RuntimeError("source resume has no remaining untouched unit")
    if int(plan[trigger_ordinal - 1]["ordinal"]) != trigger_ordinal:
        raise RuntimeError("source contract trigger ordinal drift")
    return source_contract, source_index, path, receipt


def probe_request() -> dict[str, Any]:
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Synthetic provider liveness check only. Follow the user exactly."},
            {"role": "user", "content": "Return exactly SOURCE_RESUME_OK and nothing else."},
        ],
        "temperature": 0.0,
        "top_p": 1.0,
        "max_completion_tokens": 16,
        "n": 1,
        "stream": False,
    }


def contract_payload(trigger_ordinal: int) -> dict[str, Any]:
    source_contract, source_index, path, receipt = validate_trigger(trigger_ordinal)
    request = probe_request()
    remaining = list(source_contract["source_plan"])[trigger_ordinal:]
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_PROVIDER_RESUME_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_SOURCE_PROVIDER_RESUME_SINGLE_PROBE_AUTHORIZED",
        "trigger_ordinal": trigger_ordinal,
        "trigger_instance_id": receipt["instance_id"],
        "trigger_execution_status": receipt["execution_status"],
        "trigger_failure_code": _rate_limit_code(receipt),
        "trigger_source_receipt": str(path.relative_to(ROOT)),
        "trigger_source_receipt_sha256": sha256_file(path),
        "source_contract_sha256": sha256_file(SOURCE_CONTRACT),
        "source_index_hold_sha256": sha256_file(SOURCE_INDEX),
        "source_index_completed_count": source_index["completed_count"],
        "next_untouched_ordinal": trigger_ordinal + 1,
        "remaining_untouched_ordinals": [int(row["ordinal"]) for row in remaining],
        "probe_request": request,
        "probe_request_sha256": sha256_text(canonical_json(request)),
        "execution_policy": {
            "synthetic_nonbenchmark_probe_count": 1,
            "attempt_count": 1,
            "automatic_retry": False,
            "source_trigger_retry": False,
            "source_task_replacement": False,
            "probe_failure_leaves_remaining_source_units_untouched": True,
        },
        "scientific_boundary": {
            "trigger_source_receipt_permanently_retained": True,
            "trigger_source_reexecution_authorized": False,
            "next_untouched_source_execution_authorized": False,
            "remaining_source_outcomes_observed": False,
            "memory_extraction_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze_contract(trigger_ordinal: int) -> dict[str, Any]:
    path = contract_path(trigger_ordinal)
    if path.exists():
        raise RuntimeError("refusing to overwrite immutable source resume contract")
    payload = contract_payload(trigger_ordinal)
    return {
        "decision": payload["decision"],
        "trigger_ordinal": trigger_ordinal,
        "file_sha256": write_json(path, payload),
    }


def _write_index(trigger_ordinal: int, *, contract_sha256: str,
                 inflight: bool, result_sha256: str | None = None) -> str:
    payload = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_PROVIDER_RESUME_QUALIFICATION",
        "created_at_utc": utcnow(),
        "trigger_ordinal": trigger_ordinal,
        "contract_sha256": contract_sha256,
        "inflight": ({
            "probe_id": f"SOURCE-RESUME-{trigger_ordinal:02d}",
            "attempt_count": 1,
            "state": "DISPATCHED_BEFORE_PROVIDER_CALL",
        } if inflight else None),
        "execution_complete": result_sha256 is not None,
        "result_sha256": result_sha256,
        "credential_material_present": False,
    }
    return write_json(index_path(trigger_ordinal), payload)


def execute(trigger_ordinal: int) -> dict[str, Any]:
    contract_file = contract_path(trigger_ordinal)
    result_file = result_path(trigger_ordinal)
    expected = EXPECTED_CONTRACT_SHA256_BY_TRIGGER.get(trigger_ordinal)
    if not expected or expected == "PENDING":
        raise RuntimeError("source resume contract SHA not pinned for trigger")
    if not contract_file.is_file() or sha256_file(contract_file) != expected:
        raise RuntimeError("source resume contract SHA drift")
    if result_file.exists():
        raise RuntimeError("refusing duplicate source resume qualification")
    idx = index_path(trigger_ordinal)
    if idx.exists():
        prior = json.loads(idx.read_text(encoding="utf-8"))
        if prior.get("inflight") and not result_file.exists():
            raise RuntimeError("SOURCE_RESUME_AMBIGUOUS_INFLIGHT_HOLD: refusing duplicate probe")
    contract = json.loads(contract_file.read_text(encoding="utf-8"))
    # Revalidate the exact hold before the liveness probe. No source unit may have
    # been added since the repair contract was frozen.
    _, _, trigger_path, _ = validate_trigger(trigger_ordinal)
    if sha256_file(trigger_path) != contract["trigger_source_receipt_sha256"]:
        raise RuntimeError("source resume trigger receipt changed after freeze")
    if sha256_file(SOURCE_INDEX) != contract["source_index_hold_sha256"]:
        raise RuntimeError("source resume hold index changed after freeze")
    _write_index(trigger_ordinal, contract_sha256=expected, inflight=True)
    request = dict(contract["probe_request"])
    safe: dict[str, Any] | None = None
    failure: dict[str, Any] | None = None
    try:
        client = make_client(timeout_seconds=120.0)
        response = client.create_response(
            input_items=request["messages"], model=request["model"],
            temperature=request["temperature"], top_p=request["top_p"],
            max_output_tokens=request["max_completion_tokens"],
        )
        if response.get("actual_request_sha256") != contract["probe_request_sha256"]:
            raise RuntimeError("source resume actual request hash drift")
        safe = safe_response(response)
        checks = {
            "provider_response_received": True,
            "resolved_model_exact": safe.get("resolved_model") == MODEL,
            "transport_attempt_exactly_one": int(safe.get("transport_attempts") or 0) == 1,
            "exact_liveness_text": str(safe.get("text") or "").strip() == "SOURCE_RESUME_OK",
            "credential_material_absent": safe.get("credential_material_present") is False,
        }
    except QwenProviderError as error:
        failure = error.safe_receipt()
        checks = {
            "provider_response_received": False,
            "resolved_model_exact": False,
            "transport_attempt_exactly_one": True,
            "exact_liveness_text": False,
            "credential_material_absent": True,
        }
    qualified = all(checks.values())
    payload = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_PROVIDER_RESUME_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": QUALIFIED_DECISION if qualified else HOLD_DECISION,
        "trigger_ordinal": trigger_ordinal,
        "trigger_source_receipt_sha256": contract["trigger_source_receipt_sha256"],
        "source_contract_sha256": contract["source_contract_sha256"],
        "source_index_hold_sha256": contract["source_index_hold_sha256"],
        "next_untouched_ordinal": contract["next_untouched_ordinal"],
        "contract_sha256": expected,
        "probe_request_sha256": contract["probe_request_sha256"],
        "probe_response": safe,
        "failure": failure,
        "checks": checks,
        "source_trigger_retry_count": 0,
        "source_replacement_count": 0,
        "scientific_boundary": {
            "trigger_source_receipt_permanently_retained": True,
            "trigger_source_reexecution_authorized": False,
            "next_untouched_source_execution_authorized": qualified,
            "remaining_source_outcomes_observed": False,
            "memory_extraction_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }
    result_sha = write_json(result_file, payload)
    _write_index(trigger_ordinal, contract_sha256=expected, inflight=False,
                 result_sha256=result_sha)
    return {
        "decision": payload["decision"],
        "trigger_ordinal": trigger_ordinal,
        "file_sha256": result_sha,
    }


def require_resume_gate(trigger_ordinal: int, terminal_receipt_path: Path) -> dict[str, Any]:
    result_file = result_path(trigger_ordinal)
    if not result_file.is_file():
        raise RuntimeError("SOURCE_PROVIDER_RESUME_QUALIFICATION_REQUIRED")
    result = json.loads(result_file.read_text(encoding="utf-8"))
    if result.get("decision") != QUALIFIED_DECISION:
        raise RuntimeError("source provider resume gate closed")
    if result.get("trigger_ordinal") != trigger_ordinal:
        raise RuntimeError("source provider resume trigger ordinal drift")
    if result.get("trigger_source_receipt_sha256") != sha256_file(terminal_receipt_path):
        raise RuntimeError("source provider resume trigger receipt binding drift")
    if result.get("source_contract_sha256") != sha256_file(SOURCE_CONTRACT):
        raise RuntimeError("source provider resume contract binding drift")
    if result.get("next_untouched_ordinal") != trigger_ordinal + 1:
        raise RuntimeError("source provider resume next ordinal drift")
    if result.get("source_trigger_retry_count") != 0 or result.get("source_replacement_count") != 0:
        raise RuntimeError("source provider resume retry/replacement drift")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trigger-ordinal", type=int, required=True)
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    value = freeze_contract(args.trigger_ordinal) if args.freeze_contract else execute(args.trigger_ordinal)
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
