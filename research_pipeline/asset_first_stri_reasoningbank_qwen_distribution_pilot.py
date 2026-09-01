"""Freeze, execute, and qualify the 4-task, A/D/N, K=4 pilot."""
from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_behavioral_runner import (
    receipt_path, run_plan,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_edit_targets import (
    atoms_from_signature,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_pilot_gate import (
    pilot_metric_gate,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_power import (
    precision_simulation,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_schedule import schedule_seed

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
STAGE = "QWEN_BEHAVIORAL_PILOT"
STRUCTURAL = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-structural-result-20260901.json"
CALIBRATION = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-calibration-result-20260901.json"
SPLIT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-task-split-20260901.json"
BANK = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-bank-20260901.json"
Q0 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-result-20260901.json"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-pilot-contract-20260901.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-pilot-index-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-pilot-runs-20260901"
RESULT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-pilot-result-20260901.json"
EXPECTED_CONTRACT_SHA256 = "PENDING"
ARMS = ("A", "D", "N")
K_PILOT = 4


def pilot_plan(tasks: list[str], *, manifest_sha256: str,
               structural: dict[str, Any], split: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
    if len(tasks) != 4 or len(set(tasks)) != 4:
        raise RuntimeError("pilot requires four unique tasks")
    seed = schedule_seed(EXPERIMENT_ID + "||PILOT", manifest_sha256)
    rng = random.Random(seed)
    plan, ordinal = [], 0
    for trial_round in range(1, K_PILOT + 1):
        task_order = list(tasks)
        rng.shuffle(task_order)
        for task_position, task_id in enumerate(task_order, start=1):
            arm_order = list(ARMS)
            rng.shuffle(arm_order)
            for arm_position, arm in enumerate(arm_order, start=1):
                ordinal += 1
                meta = split["task_receipts"][task_id]
                plan.append({
                    "ordinal": ordinal, "run_id": f"QWEN-PILOT-{ordinal:02d}",
                    "round": trial_round, "task_position_within_round": task_position,
                    "arm_position_within_task": arm_position,
                    "instance_id": task_id, "arm": arm,
                    "expected_R1_sha256": structural["structural_receipts"][task_id]["complete_R1_sha256"][arm],
                    "qualification_receipt": meta["qualification_receipt"],
                    "qualification_receipt_sha256": meta["qualification_receipt_sha256"],
                    "attempt_count": 1, "automatic_retry": False, "replacement": False,
                })
    if len(plan) != 48 or Counter((row["instance_id"], row["arm"]) for row in plan) != Counter(
            {(task, arm): 4 for task in tasks for arm in ARMS}):
        raise RuntimeError("pilot schedule drift")
    return seed, plan


def contract_payload() -> dict[str, Any]:
    structural = json.loads(STRUCTURAL.read_text())
    calibration = json.loads(CALIBRATION.read_text())
    split = json.loads(SPLIT.read_text())
    q0 = json.loads(Q0.read_text())
    if calibration["decision"] != "QWEN_CAPABILITY_CALIBRATION_QUALIFIED":
        raise RuntimeError("calibration gate closed")
    tasks = list(structural["pilot_task_ids"])
    binding = sha256_text(canonical_json({
        "structural_sha256": sha256_file(STRUCTURAL),
        "calibration_sha256": sha256_file(CALIBRATION),
        "tasks": tasks,
    }))
    seed, plan = pilot_plan(tasks, manifest_sha256=binding,
                            structural=structural, split=split)
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID, "stage": STAGE,
        "created_at_utc": utcnow(), "decision": "QWEN_K4_ADN_PILOT_AUTHORIZED",
        "structural_sha256": sha256_file(STRUCTURAL),
        "calibration_sha256": sha256_file(CALIBRATION),
        "source_bank_sha256": sha256_file(BANK), "q0_sha256": sha256_file(Q0),
        "sampling": q0["recommended_sampling_resolution"],
        "task_ids": tasks, "N_pilot": 4, "K_pilot": 4, "arms": list(ARMS),
        "planned_trajectory_count": 48, "rng_seed": seed,
        "plan": plan, "plan_sha256": sha256_text(canonical_json(plan)),
        "purposes_only": [
            "repeated-trial machinery", "provider reliability", "runtime and quota",
            "EditTargetSet extraction", "behavior signature replay",
            "metric degeneracy", "R1 invariants", "cost",
        ],
        "forbidden": [
            "use pilot in confirmatory inference", "tune N/K from A-v-D effect",
            "select confirmatory hypotheses from pilot effect",
        ],
        "pilot_reliability_gate": {
            "all_four_A_valid_per_task_for_precision": True,
            "minimum_valid_D_per_task": 3, "minimum_valid_N_per_task": 3,
        },
        "metric_gate": {
            "constant_distance_threshold": .90,
            "python_fallback_threshold": .90,
        },
        "precision": {
            "pilot_A_only": True, "synthetic_T_grid": [.05, .10, .15, .20, .25],
            "simulation_replicates": 20_000, "N_fixed": 24, "K_fixed": 6,
        },
        "confirmatory_execution_authorized": False,
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite pilot contract")
    payload = contract_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "planned_trajectory_count": 48}


def adjudicate() -> dict[str, Any]:
    if RESULT.exists():
        raise RuntimeError("refusing duplicate pilot adjudication")
    contract = json.loads(CONTRACT.read_text())
    index = json.loads(INDEX.read_text())
    if not index["execution_complete"] or index["completed_count"] != 48:
        raise RuntimeError("pilot incomplete")
    receipts = [json.loads(receipt_path(RECEIPT_DIR, unit).read_text())
                for unit in contract["plan"]]
    valid_counts = Counter(
        (row["instance_id"], row["arm"]) for row in receipts if row["behavior_valid"])
    signature_rows: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list))
    pilot_a_atoms = defaultdict(list)
    for row in receipts:
        if not row["behavior_valid"]:
            continue
        signature = row["behavior_observables"]["edit_target_set"]
        signature_rows[row["instance_id"]][row["arm"]].append(signature)
        if row["arm"] == "A":
            pilot_a_atoms[row["instance_id"]].append(atoms_from_signature(signature))
    reliability = {
        "every_task_four_valid_A": all(valid_counts[(task, "A")] == 4
                                       for task in contract["task_ids"]),
        "every_task_at_least_three_valid_D": all(valid_counts[(task, "D")] >= 3
                                                 for task in contract["task_ids"]),
        "every_task_at_least_three_valid_N": all(valid_counts[(task, "N")] >= 3
                                                 for task in contract["task_ids"]),
        "every_attempt_count_one": all(row["attempt_count"] == 1 for row in receipts),
        "every_valid_R1_exact": all(row["complete_R1_exact"]
                                    for row in receipts if row["behavior_valid"]),
    }
    reliability_pass = all(reliability.values())
    metric = pilot_metric_gate(signature_rows) if reliability_pass else {
        "decision": "EDIT_TARGET_METRIC_UNQUALIFIED_INSUFFICIENT_PILOT_COMPLETENESS"}
    power = precision_simulation(
        pilot_a_atoms, seed=int(contract["rng_seed"]) ^ 0xE1,
        replicates=int(contract["precision"]["simulation_replicates"])) if reliability_pass else None
    passed = reliability_pass and metric["decision"] == "EDIT_TARGET_METRIC_QUALIFIED"
    payload = {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID, "stage": STAGE,
        "created_at_utc": utcnow(),
        "decision": "QWEN_PILOT_METRIC_AND_RELIABILITY_QUALIFIED" if passed
                    else ("EDIT_TARGET_METRIC_UNQUALIFIED"
                          if metric["decision"].startswith("EDIT_TARGET_METRIC_UNQUALIFIED")
                          else "QWEN_PILOT_RELIABILITY_HOLD"),
        "contract_sha256": sha256_file(CONTRACT), "index_sha256": sha256_file(INDEX),
        "valid_counts_by_task_arm": {
            task: {arm: valid_counts[(task, arm)] for arm in ARMS}
            for task in contract["task_ids"]
        },
        "reliability_checks": reliability, "metric_gate": metric,
        "precision_appendix": power,
        "MDE80": power["MDE80"] if power else None,
        "POWER_LIMITED": power["POWER_LIMITED"] if power else True,
        "pilot_treatment_effect_used_for_design": False,
        "pilot_outcomes_enter_confirmatory_inference": False,
        "scientific_boundary": {
            "confirmatory_preregistration_authorized": passed,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }
    return {"decision": payload["decision"], "file_sha256": write_json(RESULT, payload),
            "MDE80": payload["MDE80"], "POWER_LIMITED": payload["POWER_LIMITED"]}


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
