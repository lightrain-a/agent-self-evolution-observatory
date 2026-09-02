"""Preregister and run 32 disjoint Qwen source trajectories exactly once."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_agent import (
    QualificationDockerRun, evaluate, execute_trajectory,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_runtime import (
    SOURCE_RESULT, require_source_qualified,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_d0_qualify import (
    dataset_rows,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_source_resume import (
    require_resume_gate,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
SPLIT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-task-split-20260901.json"
Q0 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-result-20260901.json"
Q1 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q1-result-20260901.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-contract-20260901.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-index-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-trajectories-20260901"
EXPECTED_CONTRACT_SHA256 = "072980a4e71a3e31de2e59ef77b52cd090073d645b665af0adc25c24a99b8daa"


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    q0 = json.loads(Q0.read_text(encoding="utf-8"))
    q1 = json.loads(Q1.read_text(encoding="utf-8"))
    if split["decision"] != "QWEN_OUTCOME_BLIND_TASK_SPLITS_FROZEN":
        raise RuntimeError("task split gate closed")
    if q0["decision"] != "Q0_QWEN3_CODER_NEXT_PROVIDER_QUALIFIED":
        raise RuntimeError("Q0 gate closed")
    if q1["backend_classification"] not in {"DETERMINISTIC", "STOCHASTIC"}:
        raise RuntimeError("Q1 gate closed")
    return split, q0, q1


def source_plan(split: dict[str, Any]) -> list[dict[str, Any]]:
    plan = []
    for ordinal, task_id in enumerate(split["source_task_ids"], start=1):
        meta = split["task_receipts"][task_id]
        plan.append({
            "ordinal": ordinal, "run_id": f"QWEN-SOURCE-{ordinal:02d}",
            "instance_id": task_id, "task_sha256": meta["task_sha256"],
            "qualification_receipt": meta["qualification_receipt"],
            "qualification_receipt_sha256": meta["qualification_receipt_sha256"],
            "attempt_count": 1, "automatic_retry": False, "replacement": False,
        })
    if len(plan) not in {24, 32}:
        raise RuntimeError("source plan count drift")
    return plan


def contract_payload() -> dict[str, Any]:
    split, q0, q1 = load_inputs()
    plan = source_plan(split)
    sampling = dict(q0["recommended_sampling_resolution"])
    if sampling["max_retries"] != 0:
        raise RuntimeError("Q0 retries drift")
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_TRAJECTORY_EXECUTION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_SOURCE_TRAJECTORIES_EXACTLY_ONCE_AUTHORIZED",
        "split_sha256": sha256_file(SPLIT), "q0_sha256": sha256_file(Q0),
        "q1_sha256": sha256_file(Q1),
        "source_runtime_result_sha256": sha256_file(SOURCE_RESULT),
        "source_plan": plan,
        "source_plan_sha256": sha256_text(canonical_json(plan)),
        "source_task_count": len(plan), "sampling": sampling,
        "execution_policy": {
            "exactly_once_per_source_task": True, "attempt_count": 1,
            "automatic_retry": False, "replacement": False,
            "failed_timeout_and_unsuccessful_trajectories_preserved": True,
        },
        "scientific_boundary": {
            "source_tasks_disjoint": True,
            "rootful_source_runtime_qualified": True,
            "memory_extraction_authorized": False,
            "calibration_authorized": False, "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite source contract")
    payload = contract_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "source_task_count": payload["source_task_count"]}


def receipt_path(unit: dict[str, Any]) -> Path:
    safe = unit["instance_id"].replace("__", "-")
    return RECEIPT_DIR / f"{unit['ordinal']:02d}-{safe}.json"


def load_completed(plan: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    completed = {}
    for unit in plan:
        path = receipt_path(unit)
        if not path.exists():
            continue
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if receipt["run_id"] != unit["run_id"] or receipt["attempt_count"] != 1:
            raise RuntimeError("source receipt identity/attempt drift")
        completed[unit["ordinal"]] = receipt
    prefix = list(range(1, len(completed) + 1))
    if sorted(completed) != prefix:
        raise RuntimeError("source receipts are not a frozen-order prefix")
    return completed


def require_resume_if_last_terminal(
    contract: dict[str, Any], completed: dict[int, dict[str, Any]],
) -> dict[str, Any] | None:
    """Fail closed at a consumed terminal source until its resume gate passes."""
    if not completed:
        return None
    last_ordinal = max(completed)
    last = completed[last_ordinal]
    if last.get("execution_status") == "COMPLETED":
        return None
    if last.get("execution_status") != "TERMINAL_PROVIDER_OR_POLICY_FAILURE":
        raise RuntimeError("SOURCE_TERMINAL_HOLD_REQUIRES_EXPLICIT_PROSPECTIVE_REPAIR")
    trajectory = last.get("trajectory") or {}
    failure = trajectory.get("failure") or {}
    safe = failure.get("safe_receipt") or {}
    detail = safe.get("detail") or {}
    error = detail.get("error") or {}
    if failure.get("failure_layer") != "provider" or error.get("code") != "rate_limit_exceeded":
        raise RuntimeError("SOURCE_TERMINAL_HOLD_NOT_RATE_LIMIT_RESUMABLE")
    if failure.get("ambiguous_generation_reissued") is not False:
        raise RuntimeError("SOURCE_TERMINAL_HOLD_AMBIGUOUS_PROVIDER_GENERATION")
    cleanup = last.get("container_cleanup_receipt") or {}
    if cleanup.get("accepted") is not True:
        raise RuntimeError("SOURCE_TERMINAL_HOLD_CLEANUP_NOT_ACCEPTED")
    unit = contract["source_plan"][last_ordinal - 1]
    terminal_path = receipt_path(unit)
    return require_resume_gate(last_ordinal, terminal_path)


def index_payload(contract: dict[str, Any], completed: dict[int, dict[str, Any]],
                  inflight: dict[str, Any] | None = None) -> dict[str, Any]:
    journal = [{
        "ordinal": ordinal, "run_id": row["run_id"],
        "instance_id": row["instance_id"], "attempt_count": row["attempt_count"],
        "execution_status": row["execution_status"], "persisted": True,
        "receipt_sha256": sha256_file(receipt_path(contract["source_plan"][ordinal - 1])),
    } for ordinal, row in sorted(completed.items())]
    complete = len(completed) == len(contract["source_plan"])
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_SOURCE_TRAJECTORY_EXECUTION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_SOURCE_TRAJECTORIES_COMPLETE" if complete else "QWEN_SOURCE_TRAJECTORIES_IN_PROGRESS",
        "execution_complete": complete, "contract_sha256": sha256_file(CONTRACT),
        "planned_count": len(contract["source_plan"]), "completed_count": len(completed),
        "journal_record_count": len(journal), "journal": journal,
        "inflight": inflight,
        "checks": {
            "frozen_order_prefix": True,
            "every_attempt_count_one": all(row["attempt_count"] == 1 for row in journal),
            "no_retry": True, "no_replacement": True,
            "all_receipts_persisted": all(row["persisted"] for row in journal),
        },
        "credential_material_present": False,
    }


def run() -> dict[str, Any]:
    if EXPECTED_CONTRACT_SHA256 == "PENDING":
        raise RuntimeError("source contract SHA not pinned")
    if sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("source contract SHA drift")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["split_sha256"] != sha256_file(SPLIT):
        raise RuntimeError("source split binding drift")
    runtime = require_source_qualified()
    if contract["source_runtime_result_sha256"] != sha256_file(SOURCE_RESULT):
        raise RuntimeError("source runtime binding drift")
    if runtime["decision"] != "QWEN_ROOTFUL_SOURCE_RUNTIME_QUALIFIED_SOURCE_GATE_OPEN":
        raise RuntimeError("source runtime gate closed")
    rows = dataset_rows()
    completed = load_completed(contract["source_plan"])
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    if INDEX.exists():
        prior = json.loads(INDEX.read_text(encoding="utf-8"))
        inflight = prior.get("inflight")
        if inflight and not receipt_path(inflight).exists():
            raise RuntimeError(
                "SOURCE_AMBIGUOUS_INFLIGHT_HOLD: refusing to reissue an unreceipted source unit"
            )
    require_resume_if_last_terminal(contract, completed)
    write_json(INDEX, index_payload(contract, completed))
    for unit in contract["source_plan"][len(completed):]:
        write_json(INDEX, index_payload(contract, completed, inflight={
            "ordinal": unit["ordinal"], "run_id": unit["run_id"],
            "instance_id": unit["instance_id"], "attempt_count": 1,
            "state": "DISPATCHED_BEFORE_ANY_SIDE_EFFECT",
        }))
        row = rows[unit["instance_id"]]
        qpath = ROOT / unit["qualification_receipt"]
        if sha256_file(qpath) != unit["qualification_receipt_sha256"]:
            raise RuntimeError("qualification receipt drift")
        qualification = json.loads(qpath.read_text(encoding="utf-8"))
        image = qualification["task_receipt"]["image_manifest"]["image_pull_reference"]
        container = QualificationDockerRun(
            image=image, base_commit=str(row["base_commit"]), run_id=unit["run_id"])
        trajectory: dict[str, Any] | None = None
        try:
            trajectory, _ = execute_trajectory(
                row=row, image_pull_reference=image, selected_memory="",
                run_id=unit["run_id"], sampling=contract["sampling"],
                container=container)
            status = "COMPLETED"
            if trajectory.get("failure") is not None:
                status = "TERMINAL_PROVIDER_OR_POLICY_FAILURE"
            if trajectory["task_sha256"] != unit["task_sha256"]:
                trajectory["failure"] = {
                    "failure_layer": "artifact_integrity",
                    "error_type": "ModelVisibleTaskHashDrift",
                    "expected": unit["task_sha256"], "actual": trajectory["task_sha256"],
                }
                status = "TERMINAL_TASK_HASH_DRIFT"
            try:
                trajectory["R4_terminal_outcome"] = evaluate(container, row)
                # Preserve any earlier terminal provider/artifact status.
            except Exception as error:
                trajectory["R4_terminal_outcome"] = {
                    "valid": False, "resolved": False,
                    "failure": {"failure_layer": "evaluator",
                                "error_type": type(error).__name__, "message": str(error)},
                }
                if status == "COMPLETED":
                    status = "TERMINAL_EVALUATOR_FAILURE"
        except Exception as error:
            trajectory = {
                "schema_version": 1, "run_id": unit["run_id"],
                "created_at_utc": utcnow(), "instance_id": unit["instance_id"],
                "task_sha256": unit["task_sha256"], "attempt_count": 1,
                "execution_status": "TERMINAL_IMPLEMENTATION_OR_RUNTIME_FAILURE",
                "failure": {"failure_layer": "runtime_or_implementation",
                            "error_type": type(error).__name__, "message": str(error)},
                "model_call_count": 0, "automatic_retry": False, "replacement": False,
                "gold_patch_model_visible": False, "test_patch_model_visible": False,
                "credential_material_present": False,
            }
            status = "TERMINAL_FAILURE"
        cleanup = container.close()
        receipt = {
            **unit, "created_at_utc": utcnow(), "execution_status": status,
            "trajectory": trajectory, "container_cleanup_receipt": cleanup,
            "credential_material_present": False,
        }
        target = receipt_path(unit)
        if target.exists():
            raise RuntimeError("refusing to overwrite source task receipt")
        write_json(target, receipt)
        completed[unit["ordinal"]] = json.loads(target.read_text(encoding="utf-8"))
        write_json(INDEX, index_payload(contract, completed))
        print(json.dumps({
            "ordinal": unit["ordinal"], "instance_id": unit["instance_id"],
            "execution_status": status, "completed": len(completed)}, sort_keys=True), flush=True)
        if status != "COMPLETED":
            break
    final = index_payload(contract, completed)
    return {"decision": final["decision"], "completed_count": len(completed),
            "index_sha256": write_json(INDEX, final)}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    print(json.dumps(freeze_contract() if args.freeze_contract else run(), sort_keys=True))


if __name__ == "__main__":
    main()
