"""Stage-2 rootful runtime qualification for calibration/pilot/confirmatory tasks.

This gate is frozen only after retrieval/structural qualification has selected the
final pilot and confirmatory populations.  It therefore materializes only the
8 calibration + 4 pilot + 24 confirmatory task images needed for behavior.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_runtime import (
    EXPERIMENT_ID, ROOTFUL_DOCKER_HOST, SPLIT,
    activate_rootful_runtime, build_runtime_plan, common_contract_fields,
    execute_runtime_plan, load_completed, load_split_d0,
)

STRUCTURAL = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-structural-result-20260901.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-evaluation-runtime-contract-20260901.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-evaluation-runtime-index-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-evaluation-runtime-receipts-20260901"
RESULT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-evaluation-runtime-result-20260901.json"
EXPECTED_CONTRACT_SHA256 = "PENDING"


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    split, d0 = load_split_d0()
    structural = json.loads(STRUCTURAL.read_text(encoding="utf-8"))
    if structural.get("decision") != "RETRIEVAL_STRUCTURAL_QUALIFIED_FINAL_TASKS_FROZEN":
        raise RuntimeError("structural selection gate closed")
    return split, d0, structural


def evaluation_runtime_plan(
    split: dict[str, Any], structural: dict[str, Any],
) -> list[dict[str, Any]]:
    task_ids = (
        list(split["calibration_task_ids"])
        + list(structural["pilot_task_ids"])
        + list(structural["confirmatory_task_ids"])
    )
    if len(task_ids) != 36 or len(set(task_ids)) != 36:
        raise RuntimeError("evaluation runtime requires 36 unique tasks")
    return build_runtime_plan(split, task_ids, prefix="QWEN-EVAL-RUNTIME")


def contract_payload() -> dict[str, Any]:
    split, d0, structural = load_inputs()
    plan = evaluation_runtime_plan(split, structural)
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_ROOTFUL_EVALUATION_RUNTIME_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_ROOTFUL_EVALUATION_RUNTIME_QUALIFICATION_AUTHORIZED",
        **common_contract_fields(split=split, d0=d0, plan=plan),
        "structural_path": str(STRUCTURAL.relative_to(ROOT)),
        "structural_sha256": sha256_file(STRUCTURAL),
        "population": {
            "calibration_count": 8,
            "pilot_count": 4,
            "confirmatory_count": 24,
            "total_unique_tasks": 36,
            "selection_outcome_blind": True,
        },
        "scientific_boundary": {
            "calibration_authorized": False,
            "pilot_authorized": False,
            "confirmatory_execution_authorized": False,
        },
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable evaluation runtime contract")
    payload = contract_payload()
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "planned_task_count": len(payload["plan"]),
    }


def execute() -> dict[str, Any]:
    result = execute_runtime_plan(
        stage="QWEN_ROOTFUL_EVALUATION_RUNTIME_QUALIFICATION",
        contract_path=CONTRACT,
        expected_contract_sha256=EXPECTED_CONTRACT_SHA256,
        index_path=INDEX,
        receipt_dir=RECEIPT_DIR,
    )
    if not result["execution_complete"]:
        return result
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("structural_sha256") != sha256_file(STRUCTURAL):
        raise RuntimeError("evaluation runtime structural binding drift")
    completed = load_completed(contract["plan"], RECEIPT_DIR)
    payload = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_ROOTFUL_EVALUATION_RUNTIME_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_ROOTFUL_EVALUATION_RUNTIME_QUALIFIED_CALIBRATION_GATE_OPEN",
        "contract_sha256": sha256_file(CONTRACT),
        "index_sha256": sha256_file(INDEX),
        "split_sha256": sha256_file(SPLIT),
        "structural_sha256": sha256_file(STRUCTURAL),
        "docker_host": ROOTFUL_DOCKER_HOST,
        "planned_count": len(contract["plan"]),
        "qualified_count": len(completed),
        "all_attempt_count_one": all(row["attempt_count"] == 1 for row in completed),
        "model_calls": 0,
        "provider_calls": 0,
        "evaluator_calls": 0,
        "behavioral_outcomes_observed": False,
        "scientific_boundary": {
            "calibration_authorized": True,
            "pilot_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }
    if RESULT.exists():
        raise RuntimeError("refusing to overwrite evaluation runtime result")
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(RESULT, payload),
        "qualified_count": len(completed),
    }


def require_qualified() -> dict[str, Any]:
    if not RESULT.is_file():
        raise RuntimeError("Qwen evaluation runtime result absent")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if result.get("decision") != "QWEN_ROOTFUL_EVALUATION_RUNTIME_QUALIFIED_CALIBRATION_GATE_OPEN":
        raise RuntimeError("Qwen evaluation rootful runtime gate closed")
    if result.get("docker_host") != ROOTFUL_DOCKER_HOST:
        raise RuntimeError("Qwen evaluation runtime Docker host drift")
    if result.get("split_sha256") != sha256_file(SPLIT):
        raise RuntimeError("Qwen evaluation runtime split binding drift")
    if result.get("structural_sha256") != sha256_file(STRUCTURAL):
        raise RuntimeError("Qwen evaluation runtime structural binding drift")
    # Re-activates the preregistered population-scoped rootful binding.
    activate_rootful_runtime()
    return result


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    value = freeze_contract() if args.freeze_contract else execute()
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
