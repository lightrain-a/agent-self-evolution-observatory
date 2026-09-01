from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    MeasurementInterfaceError,
    evaluate_arm_from_materialized_state,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    ALLOWED_ALIAS,
    OBJECT_ID,
    PROVIDER_ID,
    RunnerError,
    sha256_file,
    sha256_value,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec

RECOVERY_ID = "APPWORLD-INTERFACE-RECOVERY-R1"
HISTORICAL_UNIT_ID = "capability:qwen3.7-flash|ACE-FG-05|1"
HISTORICAL_FAMILY_ID = "ACE-FG-05"
HISTORICAL_REPEAT = 1
HISTORICAL_TASK_ID = "acecapacefg05r1_1"
HISTORICAL_EXPERIMENT_NAME = "ace-capability"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def recompute_snapshot_sha256(source_db_root: Path) -> str:
    dbs = sorted(source_db_root.glob("*.db"))
    if not dbs:
        raise RunnerError("Historical task input has no full SQLite databases.")
    return sha256_value({path.name: sha256_file(path) for path in dbs})


def validate_historical_lineage(
    *,
    ledger_path: Path,
    protected_bundle: Path,
    unit_root: Path,
) -> dict[str, Any]:
    rows = [row for row in _read_jsonl(ledger_path) if row.get("unit_id") == HISTORICAL_UNIT_ID]
    if [row.get("event") for row in rows] != ["DISPATCH", "FAILURE"]:
        raise RunnerError("Historical unit must retain exactly DISPATCH then FAILURE.")
    dispatch, failure = rows
    if dispatch.get("object_id") != OBJECT_ID or failure.get("object_id") != OBJECT_ID:
        raise RunnerError("Historical object lineage mismatch.")
    if dispatch.get("stage") != "CAPABILITY_CALIBRATION":
        raise RunnerError("Historical unit stage drifted.")
    if dispatch.get("family_id") != HISTORICAL_FAMILY_ID:
        raise RunnerError("Historical family lineage mismatch.")
    unit = dispatch.get("unit", {})
    if unit.get("repeat") != HISTORICAL_REPEAT:
        raise RunnerError("Historical repeat lineage mismatch.")
    if dispatch.get("model_id") != ALLOWED_ALIAS:
        raise RunnerError("Historical model identity drifted from frozen allowed alias.")
    if dispatch.get("provider") != PROVIDER_ID:
        raise RunnerError("Historical provider identity drifted.")
    if dispatch.get("max_retries") != 0 or dispatch.get("attempt") != 1:
        raise RunnerError("Historical exactly-once/retry contract mismatch.")
    if failure.get("failure_class") != "OperationalError":
        raise RunnerError("Historical failure class is not the frozen evaluator failure.")
    if "no such table: emails" not in str(failure.get("message", "")):
        raise RunnerError("Historical evaluator failure message drifted.")
    if failure.get("retry_attempted") is not False:
        raise RunnerError("Historical failure unexpectedly retried.")
    receipts = failure.get("provider_receipts", [])
    if len(receipts) != 5:
        raise RunnerError("Historical provider receipt count drifted from five requests.")
    if any(receipt.get("resolved_model") != ALLOWED_ALIAS for receipt in receipts):
        raise RunnerError("Historical provider resolved-model identity drifted.")
    if any(receipt.get("status") != "completed" for receipt in receipts):
        raise RunnerError("Historical provider execution was not terminal before measurement failure.")

    source_db_root = unit_root / "data" / "tasks" / HISTORICAL_TASK_ID / "dbs"
    task_specs_path = unit_root / "data" / "tasks" / HISTORICAL_TASK_ID / "specs.json"
    if not task_specs_path.is_file():
        raise RunnerError("Historical task specs are missing.")
    spec = load_protected_spec(protected_bundle)
    family = next(
        (item for item in spec["families"] if item["family_id"] == HISTORICAL_FAMILY_ID),
        None,
    )
    if family is None:
        raise RunnerError("Frozen protected family specification is missing.")
    arm = next((item for item in family["arms"] if item["coupling_level"] == "LOW"), None)
    if arm is None:
        raise RunnerError("Frozen LOW capability arm is missing.")
    task_specs = json.loads(task_specs_path.read_text(encoding="utf-8"))
    if task_specs.get("instruction") != arm["task_instruction"]:
        raise RunnerError("Historical task instruction differs from frozen LOW arm.")
    if sha256_value(arm["task_instruction"]) != dispatch.get("prompt_sha256"):
        raise RunnerError("Historical prompt SHA does not match frozen task instruction.")
    snapshot_sha = recompute_snapshot_sha256(source_db_root)
    if snapshot_sha != dispatch.get("initial_snapshot_sha256"):
        raise RunnerError("Historical initial snapshot SHA drifted.")

    changes_db_root = (
        unit_root
        / "experiments"
        / "outputs"
        / HISTORICAL_EXPERIMENT_NAME
        / "tasks"
        / HISTORICAL_TASK_ID
        / "dbs"
    )
    required_apps = sorted(
        {constraint["evaluator_binding"]["app"] for constraint in arm["constraints"]}
    )
    missing_changes = [
        str(changes_db_root / f"{app}.jsonl")
        for app in required_apps
        if not (changes_db_root / f"{app}.jsonl").is_file()
    ]
    if missing_changes:
        raise RunnerError(f"Historical output changes are missing: {missing_changes}")
    return {
        "dispatch": dispatch,
        "failure": failure,
        "provider_receipts": receipts,
        "family": family,
        "arm": arm,
        "source_db_root": source_db_root,
        "changes_db_root": changes_db_root,
        "task_specs_path": task_specs_path,
        "snapshot_sha256": snapshot_sha,
        "required_apps": required_apps,
    }


def recover_historical_measurement(
    *,
    ledger_path: Path,
    protected_bundle: Path,
    unit_root: Path,
    measurement_db_root: Path,
) -> dict[str, Any]:
    lineage = validate_historical_lineage(
        ledger_path=ledger_path,
        protected_bundle=protected_bundle,
        unit_root=unit_root,
    )
    evaluation = evaluate_arm_from_materialized_state(
        arm=lineage["arm"],
        source_db_root=lineage["source_db_root"],
        changes_db_root=lineage["changes_db_root"],
        measurement_db_root=measurement_db_root,
    )
    tool_call_count = sum(
        1
        for receipt in lineage["provider_receipts"]
        for item in receipt.get("output", [])
        if item.get("type") == "function_call"
    )
    result: dict[str, Any] = {
        "schema_version": "ace-capability-measurement-recovery-r1-v1",
        "object_id": OBJECT_ID,
        "recovery_id": RECOVERY_ID,
        "unit_id": HISTORICAL_UNIT_ID,
        "status": "HISTORICAL_MEASUREMENT_RECOVERY_PASS",
        "recovery_mode": "MEASUREMENT_ONLY_RECOVERY",
        "historical_failure_preserved": True,
        "historical_failure_class": lineage["failure"]["failure_class"],
        "historical_ledger_sha256": sha256_file(ledger_path),
        "historical_provider_request_count": len(lineage["provider_receipts"]),
        "historical_tool_call_count": tool_call_count,
        "tool_loop_completed": tool_call_count > 0,
        "provider_requests_added_by_recovery": 0,
        "agent_reexecution": False,
        "tool_reexecution": False,
        "model_switch": False,
        "retry": False,
        "replacement": False,
        "resolved_model": ALLOWED_ALIAS,
        "family_id": HISTORICAL_FAMILY_ID,
        "repeat": HISTORICAL_REPEAT,
        "task_id": HISTORICAL_TASK_ID,
        "initial_snapshot_sha256": lineage["snapshot_sha256"],
        "task_specs_sha256": sha256_file(lineage["task_specs_path"]),
        "required_apps": lineage["required_apps"],
        "evaluation": evaluation,
        "valid_capability_measurements": 1,
        "scheduled_capability_measurements": 8,
        "scientific_outcomes_observed": 1,
        "partial_f0_effects_reported": False,
        "authority": {
            "capability_continuation": False,
            "provider_reexecution": False,
            "f0": False,
            "p1": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "second_model": False,
            "method": False,
            "paper_claim": False,
        },
    }
    result["content_sha256"] = sha256_value(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--protected-bundle", type=Path, required=True)
    parser.add_argument("--unit-root", type=Path, required=True)
    parser.add_argument("--measurement-db-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = recover_historical_measurement(
        ledger_path=args.ledger,
        protected_bundle=args.protected_bundle,
        unit_root=args.unit_root,
        measurement_db_root=args.measurement_db_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
