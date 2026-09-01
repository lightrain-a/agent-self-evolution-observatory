"""Shared exactly-once behavioral-unit persistence for calibration, pilot, and main."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from research_pipeline.asset_first_stri_reasoningbank_p1_core import ROOT, sha256_file, utcnow, write_json
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_agent import execute_behavioral_unit
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_d0_qualify import dataset_rows
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_runtime_eval import (
    require_qualified as require_evaluation_runtime,
)


def memory_for_arm(bank_by_task: Mapping[str, Mapping[str, Any]],
                   retrieval: Mapping[str, Any], arm: str) -> str:
    if arm == "N":
        return ""
    selected = bank_by_task[str(retrieval["top1_source_task_id"])]
    items = [str(item) for item in selected["parsed_memory_items"] if str(item).strip()]
    if arm == "A":
        return "\n\n".join(items)
    if arm == "D":
        if len(items) < 2:
            raise RuntimeError("D selected memory is not structurally splittable")
        return items[0]
    raise ValueError(f"unsupported behavioral arm {arm}")


def receipt_path(receipt_dir: Path, unit: Mapping[str, Any]) -> Path:
    safe = str(unit["instance_id"]).replace("__", "-")
    return receipt_dir / f"{int(unit['ordinal']):03d}-{safe}-{unit['arm']}.json"


def load_completed(receipt_dir: Path, plan: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    completed = []
    missing_seen = False
    for unit in plan:
        path = receipt_path(receipt_dir, unit)
        if not path.exists():
            missing_seen = True
            continue
        if missing_seen:
            raise RuntimeError("behavioral receipts are not a frozen-order prefix")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if receipt["run_id"] != unit["run_id"] or receipt["attempt_count"] != 1:
            raise RuntimeError("behavioral receipt identity/attempt drift")
        completed.append(receipt)
    return completed


def index_payload(*, experiment_id: str, stage: str, contract_path: Path,
                  plan: Sequence[dict[str, Any]], completed: Sequence[dict[str, Any]],
                  receipt_dir: Path, inflight: dict[str, Any] | None = None) -> dict[str, Any]:
    complete = len(completed) == len(plan)
    return {
        "schema_version": 1, "experiment_id": experiment_id, "stage": stage,
        "created_at_utc": utcnow(),
        "decision": f"{stage}_COMPLETE" if complete else f"{stage}_IN_PROGRESS",
        "execution_complete": complete, "contract_sha256": sha256_file(contract_path),
        "planned_count": len(plan), "completed_count": len(completed),
        "journal_record_count": len(completed), "inflight": inflight,
        "journal": [{
            "ordinal": row["ordinal"], "run_id": row["run_id"],
            "instance_id": row["instance_id"], "arm": row["arm"],
            "attempt_count": row["attempt_count"], "execution_status": row["execution_status"],
            "persisted": True,
            "receipt_sha256": sha256_file(receipt_path(receipt_dir, row)),
        } for row in completed],
        "checks": {
            "every_attempt_count_one": all(row["attempt_count"] == 1 for row in completed),
            "no_retry": True, "no_replacement": True,
            "frozen_order_prefix": True,
        },
        "credential_material_present": False,
    }


def must_pause_after_result(result: Mapping[str, Any]) -> bool:
    status = str(result.get("execution_status") or "")
    if status in {"TERMINAL_RUNTIME_OR_IMPLEMENTATION_FAILURE", "TERMINAL_TASK_HASH_DRIFT"}:
        return True
    failures = [result.get("failure"), (result.get("trajectory") or {}).get("failure")]
    return any((failure or {}).get("failure_layer") == "provider" for failure in failures)


def run_plan(*, experiment_id: str, stage: str, contract_path: Path,
             expected_contract_sha256: str, index_path: Path, receipt_dir: Path,
             plan: Sequence[dict[str, Any]], sampling: Mapping[str, Any],
             bank_entries: Sequence[dict[str, Any]], retrievals: Mapping[str, Any],
             stop_after_ordinal: int | None = None) -> dict[str, Any]:
    if expected_contract_sha256 == "PENDING":
        raise RuntimeError("behavioral contract SHA not pinned")
    require_evaluation_runtime()
    if sha256_file(contract_path) != expected_contract_sha256:
        raise RuntimeError("behavioral contract SHA drift")
    receipt_dir.mkdir(parents=True, exist_ok=True)
    completed = load_completed(receipt_dir, plan)
    if index_path.exists():
        prior = json.loads(index_path.read_text(encoding="utf-8"))
        inflight = prior.get("inflight")
        if inflight:
            unit = plan[int(inflight["ordinal"]) - 1]
            if not receipt_path(receipt_dir, unit).exists():
                raise RuntimeError(
                    f"{stage}_AMBIGUOUS_INFLIGHT_HOLD: refusing duplicate scientific unit")
    write_json(index_path, index_payload(
        experiment_id=experiment_id, stage=stage, contract_path=contract_path,
        plan=plan, completed=completed, receipt_dir=receipt_dir))
    rows = dataset_rows()
    bank_by_task = {row["source_task_id"]: row for row in bank_entries}
    for unit in plan[len(completed):]:
        if stop_after_ordinal is not None and int(unit["ordinal"]) > stop_after_ordinal:
            break
        write_json(index_path, index_payload(
            experiment_id=experiment_id, stage=stage, contract_path=contract_path,
            plan=plan, completed=completed, receipt_dir=receipt_dir,
            inflight={"ordinal": unit["ordinal"], "run_id": unit["run_id"],
                      "instance_id": unit["instance_id"], "arm": unit["arm"],
                      "attempt_count": 1, "state": "DISPATCHED_BEFORE_ANY_SIDE_EFFECT"}))
        row = rows[unit["instance_id"]]
        qualification_path = ROOT / unit["qualification_receipt"]
        if sha256_file(qualification_path) != unit["qualification_receipt_sha256"]:
            raise RuntimeError("behavioral qualification receipt drift")
        qualification = json.loads(qualification_path.read_text())
        image = qualification["task_receipt"]["image_manifest"]["image_pull_reference"]
        memory = memory_for_arm(bank_by_task, retrievals[unit["instance_id"]], unit["arm"])
        result = execute_behavioral_unit(
            row=row, image_pull_reference=image, selected_memory=memory,
            run_id=unit["run_id"], sampling=sampling,
            expected_R1_sha256=unit["expected_R1_sha256"])
        expected_task_sha = unit.get("task_sha256")
        actual_task_sha = (result.get("trajectory") or {}).get("task_sha256")
        if expected_task_sha is not None and actual_task_sha != expected_task_sha:
            result["behavior_valid"] = False
            result["execution_status"] = "TERMINAL_TASK_HASH_DRIFT"
            result["failure"] = {
                "failure_layer": "artifact_integrity",
                "error_type": "ModelVisibleTaskHashDrift",
                "expected": expected_task_sha, "actual": actual_task_sha,
            }
        receipt = {**unit, **result}
        target = receipt_path(receipt_dir, unit)
        if target.exists():
            raise RuntimeError("refusing to overwrite behavioral receipt")
        write_json(target, receipt)
        completed.append(json.loads(target.read_text(encoding="utf-8")))
        write_json(index_path, index_payload(
            experiment_id=experiment_id, stage=stage, contract_path=contract_path,
            plan=plan, completed=completed, receipt_dir=receipt_dir))
        print(json.dumps({
            "ordinal": unit["ordinal"], "run_id": unit["run_id"],
            "instance_id": unit["instance_id"], "arm": unit["arm"],
            "execution_status": result["execution_status"],
            "completed": len(completed)}, sort_keys=True), flush=True)
        if must_pause_after_result(result):
            break
    final = index_payload(
        experiment_id=experiment_id, stage=stage, contract_path=contract_path,
        plan=plan, completed=completed, receipt_dir=receipt_dir)
    return {"decision": final["decision"], "execution_complete": final["execution_complete"],
            "completed_count": len(completed), "index_sha256": write_json(index_path, final)}
