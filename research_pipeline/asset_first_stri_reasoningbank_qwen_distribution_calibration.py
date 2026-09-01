"""Freeze, execute, and adjudicate eight A-only capability calibration tasks."""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any, Sequence

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_behavioral_runner import (
    receipt_path, run_plan,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_runtime_eval import (
    RESULT as EVALUATION_RUNTIME,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
STAGE = "QWEN_CAPABILITY_CALIBRATION"
STRUCTURAL = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-structural-result-20260901.json"
SPLIT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-task-split-20260901.json"
BANK = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-bank-20260901.json"
Q0 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-result-20260901.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-calibration-contract-20260901.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-calibration-index-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-calibration-runs-20260901"
RESULT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-calibration-result-20260901.json"
EXPECTED_CONTRACT_SHA256 = "PENDING"


def plan() -> list[dict[str, Any]]:
    structural = json.loads(STRUCTURAL.read_text())
    split = json.loads(SPLIT.read_text())
    tasks = list(split["calibration_task_ids"])
    if len(tasks) != 8:
        raise RuntimeError("calibration requires exactly eight tasks")
    rows = []
    for ordinal, task_id in enumerate(tasks, start=1):
        meta = split["task_receipts"][task_id]
        rows.append({
            "ordinal": ordinal, "run_id": f"QWEN-CAL-A-{ordinal:02d}",
            "instance_id": task_id, "arm": "A",
            "expected_R1_sha256": structural["calibration_requests"][task_id]["complete_R1_sha256"],
            "qualification_receipt": meta["qualification_receipt"],
            "qualification_receipt_sha256": meta["qualification_receipt_sha256"],
            "attempt_count": 1, "automatic_retry": False, "replacement": False,
        })
    return rows


def contract_payload() -> dict[str, Any]:
    structural = json.loads(STRUCTURAL.read_text())
    q0 = json.loads(Q0.read_text())
    if structural["decision"] != "RETRIEVAL_STRUCTURAL_QUALIFIED_FINAL_TASKS_FROZEN":
        raise RuntimeError("structural gate closed")
    rows = plan()
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID, "stage": STAGE,
        "created_at_utc": utcnow(), "decision": "QWEN_A_ONLY_CALIBRATION_AUTHORIZED",
        "structural_sha256": sha256_file(STRUCTURAL), "split_sha256": sha256_file(SPLIT),
        "source_bank_sha256": sha256_file(BANK), "q0_sha256": sha256_file(Q0),
        "evaluation_runtime_result_sha256": sha256_file(EVALUATION_RUNTIME),
        "sampling": q0["recommended_sampling_resolution"],
        "plan": rows, "plan_sha256": sha256_text(canonical_json(rows)),
        "task_count": 8, "arms": ["A"],
        "purpose": [
            "catastrophic policy/runtime floor detection", "ceiling description",
            "harness sanity", "token/call/runtime/resource estimation",
        ],
        "forbidden": ["execute D", "inspect A-v-D", "alter model from treatment outcome"],
        "capability_gate": {
            "all_eight_planned_receipts_required": True,
            "minimum_behavior_valid": 6,
            "every_complete_R1_exact": True,
            "every_attempt_count_one": True,
            "R4_zero_of_eight_alone_is_not_a_provider_capability_failure": True,
        },
        "confirmatory_execution_authorized": False,
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite calibration contract")
    payload = contract_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload)}


def quantile(values: Sequence[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower, upper = int(position), min(int(position) + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def adjudicate() -> dict[str, Any]:
    if RESULT.exists():
        raise RuntimeError("refusing duplicate calibration adjudication")
    contract = json.loads(CONTRACT.read_text())
    index = json.loads(INDEX.read_text())
    if not index["execution_complete"] or index["completed_count"] != 8:
        raise RuntimeError("calibration execution incomplete")
    receipts = [
        json.loads(receipt_path(RECEIPT_DIR, unit).read_text())
        for unit in contract["plan"]
    ]
    valid = sum(bool(row["behavior_valid"]) for row in receipts)
    r4_valid = sum(bool((row.get("R4_terminal_outcome") or {}).get("valid")) for row in receipts)
    resolved = sum(bool((row.get("R4_terminal_outcome") or {}).get("resolved")) for row in receipts)
    resource_rows = []
    for row in receipts:
        trajectory = row.get("trajectory") or {}
        responses = trajectory.get("responses") or []
        usage = [response.get("usage") or {} for response in responses]
        resource_rows.append({
            "run_id": row["run_id"],
            "model_calls": int(trajectory.get("model_call_count") or 0),
            "input_tokens": sum(int(item.get("input_tokens") or 0) for item in usage),
            "output_tokens": sum(int(item.get("output_tokens") or 0) for item in usage),
            "provider_latency_seconds": sum(float(response.get("latency_seconds") or 0)
                                            for response in responses),
        })
    checks = {
        "eight_receipts": len(receipts) == 8,
        "minimum_six_behavior_valid": valid >= 6,
        "every_R1_exact": all(row["complete_R1_exact"] for row in receipts),
        "every_attempt_count_one": all(row["attempt_count"] == 1 for row in receipts),
        "no_D_executed": all(row["arm"] == "A" for row in receipts),
        "credential_material_absent": all(not row["credential_material_present"] for row in receipts),
    }
    passed = all(checks.values())
    payload = {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID, "stage": STAGE,
        "created_at_utc": utcnow(),
        "decision": "QWEN_CAPABILITY_CALIBRATION_QUALIFIED" if passed
                    else "QWEN_CAPABILITY_CATASTROPHIC_HOLD_SUCCESSOR_PREREGISTRATION_REQUIRED",
        "contract_sha256": sha256_file(CONTRACT), "index_sha256": sha256_file(INDEX),
        "behavior_valid_count": valid, "R4_evaluator_valid_count": r4_valid,
        "R4_resolved_count": resolved,
        "catastrophic_floor": not passed,
        "catastrophic_ceiling_descriptive": resolved == 8,
        "checks": checks, "resource_rows": resource_rows,
        "resource_summary": {
            metric: {
                "mean": mean([row[metric] for row in resource_rows]),
                "p50": quantile([row[metric] for row in resource_rows], .50),
                "p90": quantile([row[metric] for row in resource_rows], .90),
                "p95": quantile([row[metric] for row in resource_rows], .95),
            } for metric in ("model_calls", "input_tokens", "output_tokens",
                             "provider_latency_seconds")
        },
        "treatment_effect_inspected": False, "D_calls": 0,
        "scientific_boundary": {
            "pilot_authorized": passed, "confirmatory_execution_authorized": False,
            "R4_is_descriptive_not_the_sole_capability_gate": True,
        },
        "credential_material_present": False,
    }
    return {"decision": payload["decision"], "file_sha256": write_json(RESULT, payload),
            "behavior_valid_count": valid, "R4_resolved_count": resolved}


def run() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text())
    structural = json.loads(STRUCTURAL.read_text())
    bank = json.loads(BANK.read_text())
    result = run_plan(
        experiment_id=EXPERIMENT_ID, stage=STAGE, contract_path=CONTRACT,
        expected_contract_sha256=EXPECTED_CONTRACT_SHA256,
        index_path=INDEX, receipt_dir=RECEIPT_DIR, plan=contract["plan"],
        sampling=contract["sampling"], bank_entries=bank["entries"],
        retrievals=structural["retrievals"])
    if result["execution_complete"]:
        result["adjudication"] = adjudicate()
    return result


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    parser.add_argument("--adjudicate-only", action="store_true")
    args = parser.parse_args()
    value = freeze_contract() if args.freeze_contract else (
        adjudicate() if args.adjudicate_only else run())
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
