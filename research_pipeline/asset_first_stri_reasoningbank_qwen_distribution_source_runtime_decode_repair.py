"""Prospective repair for the ordinal-9 zero-model runtime decode failure.

The invalid source receipt is preserved byte-for-byte, excluded from the scientific
completed prefix, and the same frozen source case may be executed once only after a
zero-model exact-runtime smoke passes under the scoped control-plane decode repair.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_runtime import (
    load_split_d0, qualify_unit, source_runtime_plan,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
TARGET_ORDINAL = 9
TARGET_INSTANCE_ID = "sympy__sympy-13031"
SOURCE_CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-contract-20260901.json"
SOURCE_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-index-20260901.json"
SOURCE_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-trajectories-20260901"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-runtime-decode-repair-contract-20260902.json"
SMOKE = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-runtime-decode-repair-smoke-20260902.json"
RESULT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-runtime-decode-repair-result-20260902.json"
REGISTRY = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-invalid-attempt-registry-20260902.json"
INVALID_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-invalid-attempts-20260902"
EXPECTED_CONTRACT_SHA256 = "52764f8d6c3bb502ab5444e7d41f85ff6c0276db04a73a95d5ca522ae88de11c"
REPAIR_CODE_PATHS = (
    ROOT / "research_pipeline/asset_first_stri_reasoningbank_p1_core.py",
    ROOT / "research_pipeline/asset_first_stri_reasoningbank_p1_q10_runtime.py",
    ROOT / "research_pipeline/asset_first_stri_reasoningbank_qwen_distribution_source.py",
    ROOT / "research_pipeline/test_asset_first_stri_reasoningbank_p1_q10_runtime.py",
)


def canonical_source_receipt() -> Path:
    matches = sorted(SOURCE_DIR.glob(f"{TARGET_ORDINAL:02d}-*.json"))
    if len(matches) != 1:
        raise RuntimeError("ordinal-9 invalid source receipt is not uniquely present")
    return matches[0]


def validate_invalid_hold() -> tuple[dict[str, Any], Path, dict[str, Any]]:
    index = json.loads(SOURCE_INDEX.read_text(encoding="utf-8"))
    if index.get("execution_complete") is True or index.get("inflight") is not None:
        raise RuntimeError("runtime-decode repair requires clean incomplete source boundary")
    if int(index.get("completed_count") or 0) != TARGET_ORDINAL:
        raise RuntimeError("runtime-decode repair requires ordinal-9 completed hold")
    journal = list(index.get("journal") or [])
    if len(journal) != TARGET_ORDINAL or int(journal[-1]["ordinal"]) != TARGET_ORDINAL:
        raise RuntimeError("runtime-decode repair source journal drift")
    path = canonical_source_receipt()
    if sha256_file(path) != journal[-1]["receipt_sha256"]:
        raise RuntimeError("runtime-decode repair source receipt SHA drift")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    trajectory = receipt.get("trajectory") or {}
    failure = trajectory.get("failure") or {}
    if receipt.get("instance_id") != TARGET_INSTANCE_ID:
        raise RuntimeError("runtime-decode repair source identity drift")
    if receipt.get("execution_status") != "TERMINAL_FAILURE":
        raise RuntimeError("runtime-decode repair trigger is not terminal failure")
    if trajectory.get("execution_status") != "TERMINAL_IMPLEMENTATION_OR_RUNTIME_FAILURE":
        raise RuntimeError("runtime-decode repair trigger layer drift")
    if failure.get("failure_layer") != "runtime_or_implementation" or failure.get("error_type") != "UnicodeDecodeError":
        raise RuntimeError("runtime-decode repair trigger is not UnicodeDecodeError")
    if int(trajectory.get("model_call_count") or 0) != 0:
        raise RuntimeError("runtime-decode invalid attempt exposed model calls")
    if trajectory.get("responses") or trajectory.get("requests"):
        raise RuntimeError("runtime-decode invalid attempt contains provider interaction")
    if "R4_terminal_outcome" in trajectory:
        raise RuntimeError("runtime-decode invalid attempt observed evaluator outcome")
    if (receipt.get("container_cleanup_receipt") or {}).get("accepted") is not True:
        raise RuntimeError("runtime-decode invalid attempt cleanup not accepted")
    return index, path, receipt


def contract_payload() -> dict[str, Any]:
    index, path, receipt = validate_invalid_hold()
    split, _ = load_split_d0()
    runtime_plan = source_runtime_plan(split)
    unit = runtime_plan[TARGET_ORDINAL - 1]
    if unit["instance_id"] != TARGET_INSTANCE_ID:
        raise RuntimeError("runtime-decode smoke source plan identity drift")
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_RUNTIME_DECODE_INVALID_ATTEMPT_REPAIR",
        "created_at_utc": utcnow(),
        "decision": "QWEN_SOURCE_RUNTIME_DECODE_REPAIR_AUTHORIZED",
        "trigger": {
            "ordinal": TARGET_ORDINAL,
            "instance_id": TARGET_INSTANCE_ID,
            "source_receipt": str(path.relative_to(ROOT)),
            "source_receipt_sha256": sha256_file(path),
            "source_index_hold_sha256": sha256_file(SOURCE_INDEX),
            "failure_layer": "runtime_or_implementation",
            "error_type": "UnicodeDecodeError",
            "model_call_count": 0,
            "provider_interaction_count": 0,
            "evaluator_outcome_observed": False,
            "cleanup_accepted": True,
        },
        "source_contract_sha256": sha256_file(SOURCE_CONTRACT),
        "runtime_smoke_unit": unit,
        "repair_code_sha256": {
            str(path.relative_to(ROOT)): sha256_file(path)
            for path in REPAIR_CODE_PATHS
        },
        "repair": {
            "scope": "Docker/runtime control-plane output decoding only",
            "control_plane_utf8_errors": "replace",
            "agent_action_output_utf8_errors": "strict",
            "model_visible_request_changed": False,
            "model_visible_messages_changed": False,
            "sampling_changed": False,
            "provider_changed": False,
            "task_changed": False,
            "task_order_changed": False,
            "source_replacement": False,
            "scientific_attempt_consumed_by_invalid_attempt": False,
        },
        "execution_policy": {
            "zero_model_runtime_smoke_required_before_replay": True,
            "smoke_model_calls": 0,
            "smoke_provider_calls": 0,
            "smoke_evaluator_calls": 0,
            "same_source_case_only": TARGET_INSTANCE_ID,
            "authorized_scientific_replay_count": 1,
            "invalid_attempt_must_be_archived_byte_exact": True,
            "canonical_slot_reopened_only_after_smoke_pass": True,
        },
        "scientific_boundary": {
            "invalid_attempt_scientifically_valid": False,
            "invalid_attempt_model_outcome_observed": False,
            "invalid_attempt_evaluator_outcome_observed": False,
            "treatment_selection_from_invalid_attempt_forbidden": True,
            "ordinals_10_through_32_outcomes_unobserved": True,
            "memory_extraction_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable runtime-decode repair contract")
    payload = contract_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload)}


def require_contract() -> dict[str, Any]:
    if EXPECTED_CONTRACT_SHA256 == "PENDING":
        raise RuntimeError("runtime-decode repair contract SHA not pinned")
    if not CONTRACT.is_file() or sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("runtime-decode repair contract SHA drift")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("decision") != "QWEN_SOURCE_RUNTIME_DECODE_REPAIR_AUTHORIZED":
        raise RuntimeError("runtime-decode repair contract gate closed")
    return contract


def run_smoke() -> dict[str, Any]:
    if SMOKE.exists():
        raise RuntimeError("refusing duplicate runtime-decode repair smoke")
    contract = require_contract()
    index, path, _ = validate_invalid_hold()
    if sha256_file(SOURCE_INDEX) != contract["trigger"]["source_index_hold_sha256"]:
        raise RuntimeError("runtime-decode repair hold index changed after freeze")
    if sha256_file(path) != contract["trigger"]["source_receipt_sha256"]:
        raise RuntimeError("runtime-decode repair invalid receipt changed after freeze")
    unit = dict(contract["runtime_smoke_unit"])
    try:
        receipt = qualify_unit(unit)
        checks = {
            "runtime_qualified": receipt.get("qualified") is True,
            "model_calls_zero": int(receipt.get("model_calls") or 0) == 0,
            "provider_calls_zero": int(receipt.get("provider_calls") or 0) == 0,
            "evaluator_calls_zero": int(receipt.get("evaluator_calls") or 0) == 0,
            "behavioral_outcomes_not_observed": receipt.get("behavioral_outcomes_observed") is False,
            "cleanup_accepted": (receipt.get("cleanup_receipt") or {}).get("accepted") is True,
        }
        failure = None
    except Exception as error:
        receipt = None
        checks = {
            "runtime_qualified": False,
            "model_calls_zero": True,
            "provider_calls_zero": True,
            "evaluator_calls_zero": True,
            "behavioral_outcomes_not_observed": True,
            "cleanup_accepted": False,
        }
        failure = {"error_type": type(error).__name__, "message": str(error)}
    passed = all(checks.values())
    payload = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_RUNTIME_DECODE_REPAIR_SMOKE",
        "created_at_utc": utcnow(),
        "decision": (
            "QWEN_SOURCE_RUNTIME_DECODE_REPAIR_SMOKE_PASS"
            if passed else "QWEN_SOURCE_RUNTIME_DECODE_REPAIR_SMOKE_HOLD"
        ),
        "contract_sha256": EXPECTED_CONTRACT_SHA256,
        "source_index_hold_sha256": sha256_file(SOURCE_INDEX),
        "invalid_attempt_receipt_sha256": sha256_file(path),
        "checks": checks,
        "runtime_receipt": receipt,
        "failure": failure,
        "scientific_boundary": {
            "model_calls": 0,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "behavioral_outcomes_observed": False,
            "scientific_replay_authorized": passed,
        },
        "credential_material_present": False,
    }
    return {"decision": payload["decision"], "file_sha256": write_json(SMOKE, payload)}


def archive_invalid_and_open_replay() -> dict[str, Any]:
    if RESULT.exists() or REGISTRY.exists():
        raise RuntimeError("refusing duplicate runtime-decode invalid-attempt adjudication")
    contract = require_contract()
    smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
    if smoke.get("decision") != "QWEN_SOURCE_RUNTIME_DECODE_REPAIR_SMOKE_PASS":
        raise RuntimeError("runtime-decode smoke did not authorize replay")
    index, path, receipt = validate_invalid_hold()
    if sha256_file(SOURCE_INDEX) != contract["trigger"]["source_index_hold_sha256"]:
        raise RuntimeError("runtime-decode archive hold index drift")
    invalid_sha = sha256_file(path)
    if invalid_sha != contract["trigger"]["source_receipt_sha256"]:
        raise RuntimeError("runtime-decode archive invalid receipt drift")
    INVALID_DIR.mkdir(parents=True, exist_ok=True)
    archive = INVALID_DIR / (
        "09-sympy-sympy-13031-runtime-decode-invalid-attempt1.json"
    )
    if archive.exists():
        raise RuntimeError("invalid-attempt archive already exists")
    archive.write_bytes(path.read_bytes())
    if sha256_file(archive) != invalid_sha:
        raise RuntimeError("invalid-attempt byte-exact archive failed")
    entry = {
        "ordinal": TARGET_ORDINAL,
        "instance_id": TARGET_INSTANCE_ID,
        "original_canonical_path": str(path.relative_to(ROOT)),
        "archive_path": str(archive.relative_to(ROOT)),
        "invalid_attempt_receipt_sha256": invalid_sha,
        "invalid_reason": "runtime-control UnicodeDecodeError before any model/provider call",
        "model_call_count": 0,
        "provider_interaction_count": 0,
        "evaluator_outcome_observed": False,
        "scientific_attempt_count_consumed": 0,
        "authorized_replay_ordinal": TARGET_ORDINAL,
        "same_source_case_only": TARGET_INSTANCE_ID,
        "replacement": False,
    }
    registry_payload = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_INVALID_ATTEMPT_REGISTRY",
        "created_at_utc": utcnow(),
        "decision": "QWEN_SOURCE_INVALID_ATTEMPT_REGISTRY_ACTIVE",
        "invalid_attempts": [entry],
        "selective_scientific_outcome_deletion": False,
        "invalid_operational_artifact_archived": True,
        "credential_material_present": False,
    }
    registry_sha = write_json(REGISTRY, registry_payload)
    path.unlink()

    # Import only after canonical slot 9 is empty; source.py will retain the
    # invalid-attempt registry in every future moving index.
    from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_source as source
    source_contract = json.loads(source.CONTRACT.read_text(encoding="utf-8"))
    completed = source.load_completed(source_contract["source_plan"])
    if sorted(completed) != list(range(1, TARGET_ORDINAL)):
        raise RuntimeError("runtime-decode replay did not reopen exactly ordinal 9")
    rewound_sha = write_json(source.INDEX, source.index_payload(source_contract, completed))
    payload = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_RUNTIME_DECODE_INVALID_ATTEMPT_ADJUDICATION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_SOURCE_RUNTIME_INVALID_ATTEMPT_ARCHIVED_REPLAY_GATE_OPEN",
        "contract_sha256": EXPECTED_CONTRACT_SHA256,
        "smoke_sha256": sha256_file(SMOKE),
        "invalid_attempt_receipt_sha256": invalid_sha,
        "invalid_attempt_archive_sha256": sha256_file(archive),
        "invalid_attempt_registry_sha256": registry_sha,
        "source_index_pre_repair_sha256": contract["trigger"]["source_index_hold_sha256"],
        "source_index_reopened_sha256": rewound_sha,
        "authorized_replay_ordinal": TARGET_ORDINAL,
        "authorized_replay_instance_id": TARGET_INSTANCE_ID,
        "scientific_attempt_count_consumed": 0,
        "scientific_replay_count_authorized": 1,
        "source_replacement": False,
        "repair_scope": contract["repair"]["scope"],
        "scientific_boundary": {
            "invalid_attempt_retained_byte_exact": True,
            "invalid_attempt_scientifically_valid": False,
            "model_or_evaluator_outcome_used_for_repair": False,
            "same_source_only": True,
            "ordinals_10_through_32_remain_untouched": True,
            "memory_extraction_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }
    return {"decision": payload["decision"], "file_sha256": write_json(RESULT, payload)}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    parser.add_argument("--run-smoke", action="store_true")
    parser.add_argument("--archive-open-replay", action="store_true")
    args = parser.parse_args()
    selected = sum(bool(x) for x in (args.freeze_contract, args.run_smoke, args.archive_open_replay))
    if selected != 1:
        raise RuntimeError("choose exactly one runtime-decode repair action")
    if args.freeze_contract:
        value = freeze_contract()
    elif args.run_smoke:
        value = run_smoke()
    else:
        value = archive_invalid_and_open_replay()
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
