"""Freeze the confirmatory manifest and its deterministic 432-unit schedule."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_schedule import (
    build_schedule,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
STRUCTURAL = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-structural-result-20260901.json"
PILOT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-pilot-result-20260901.json"
SPLIT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-task-split-20260901.json"
BANK = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-bank-20260901.json"
Q0 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-result-20260901.json"
Q1 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q1-result-20260901.json"
MANIFEST = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-manifest-20260901.json"
SCHEDULE = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-schedule-20260901.json"


def manifest_payload() -> dict[str, Any]:
    structural = json.loads(STRUCTURAL.read_text())
    pilot = json.loads(PILOT.read_text())
    split = json.loads(SPLIT.read_text())
    q0 = json.loads(Q0.read_text())
    q1 = json.loads(Q1.read_text())
    if pilot["decision"] != "QWEN_PILOT_METRIC_AND_RELIABILITY_QUALIFIED":
        raise RuntimeError("pilot gate closed")
    tasks = list(structural["confirmatory_task_ids"])
    if len(tasks) != 24:
        raise RuntimeError("confirmatory population count drift")
    per_task = {}
    for task_id in tasks:
        receipt = structural["structural_receipts"][task_id]
        retrieval = structural["retrievals"][task_id]
        per_task[task_id] = {
            "task_sha256": receipt["task_sha256"],
            "qualification_receipt": split["task_receipts"][task_id]["qualification_receipt"],
            "qualification_receipt_sha256": split["task_receipts"][task_id]["qualification_receipt_sha256"],
            "underlying_semantic_evidence_sha256": receipt["underlying_semantic_evidence_sha256"],
            "retrieved_source_task_id": retrieval["top1_source_task_id"],
            "retrieval": {
                "top1_relevance": retrieval["top1_relevance"],
                "top2_relevance": retrieval["top2_relevance"],
                "top1_top2_margin": retrieval["top1_top2_margin"],
                "source_repository": retrieval["source_repository"],
                "same_repository_indicator": retrieval["same_repository_indicator"],
            },
            "complete_R1_sha256": {
                arm: receipt["complete_R1_sha256"][arm] for arm in ("A", "D", "N")},
        }
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_CONFIRMATORY_PREREGISTRATION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_CONFIRMATORY_MANIFEST_FROZEN_EXECUTION_UNAUTHORIZED",
        "input_hashes": {
            "structural": sha256_file(STRUCTURAL), "pilot": sha256_file(PILOT),
            "split": sha256_file(SPLIT), "source_bank": sha256_file(BANK),
            "q0": sha256_file(Q0), "q1": sha256_file(Q1),
        },
        "evaluation_population": {
            "dataset_design": split["dataset_design"], "task_count": 24,
            "task_ids": tasks, "deterministic_selection": (
                "repository SHA256 order; task SHA256 order; zero-model evaluator "
                "qualification; zero-provider structural qualification; no behavior outcome"
            ),
        },
        "treatments": {
            "A": "official task-specific top-1 memory, canonical one-case visible state",
            "D": "same evidence partitioned across cases; frozen top-1 exposes first partition",
            "N": "no ReasoningBank memory",
            "B": "structural control only; complete R1 byte-identical to A",
            "E": "case-ID placebo structural control only; complete R1 byte-identical to A",
            "C": "historical order-sensitivity boundary probe; not a main behavioral arm",
        },
        "per_task_frozen_state": per_task,
        "provider_model": {
            "provider": "domestic OpenAI-compatible Ark Responses route",
            "base_url": "https://ark.cn-beijing.volces.com/api/plan/v3",
            "requested_resolved_model_required": "qwen3-coder-next",
            "sampling": q0["recommended_sampling_resolution"],
            "backend_classification": q1["backend_classification"],
            "max_retries": 0, "streaming": False, "seed": "omitted",
        },
        "sample": {
            "N_confirmatory_tasks": 24, "K_per_arm": 6, "arms": ["A", "D", "N"],
            "planned_trajectories": 432, "repeat_policy": "six planned samples per task-arm",
            "stopping_rule": "execute every planned unit exactly once unless resource headroom prevents starting the next untouched unit",
            "no_replacement": True, "no_run_level_retry": True,
        },
        "claim_ladder": {
            "R0": "representation/retrieval state",
            "R1": "exact complete model-visible request",
            "R2": "first behavior/action signature",
            "R3": "complete trajectory and EditTargetSet distribution",
            "R4": "terminal official SWE-bench outcome",
        },
        "primary": {
            "contrast": "A versus D", "unit": "task",
            "endpoint": "EditTargetSet Jaccard cross-minus-within distribution separation",
            "T_i": "2*mean[d(A,D)]-mean[d(A,A')]-mean[d(D,D')]",
            "T_global": "mean task T_i across analyzable tasks",
            "inference": "100000 Monte Carlo within-task A/D label permutations; preserve actual group sizes",
            "p_value": "one-sided (1+null>=observed)/(100000+1)",
            "confidence_interval": "95% task bootstrap, 100000 task resamples",
            "formal_energy_distance_claim": False,
        },
        "secondary": {
            "A_vs_N": "same cross-minus-within statistic as memory uptake diagnostic",
            "R2": ["action class LIST/SEARCH/READ/TEST/EDIT/SUBMIT/OTHER",
                   "first referenced path", "first referenced Python symbol/module", "parse validity"],
            "R3": ["modified-file set", "exact patch hash/equality", "EditTargetSet",
                   "modified-file count", "hunk count", "model calls", "shell actions",
                   "tests run", "trajectory length", "submission state"],
            "R4": (
                "per-task resolution proportions; a paired task enters a contrast with >=4 "
                "behavior-valid and evaluator-valid trials in both arms; 100000 two-sided task sign-flip "
                "permutations of arm-proportion differences plus task bootstrap CI"
            ),
            "relevance_sensitivity": structural["high_relevance_sensitivity_task_ids"],
        },
        "missingness": {
            "primary_task_rule": "valid_A>=4 and valid_D>=4; use all valid trials",
            "secondary_task_rule": "valid_A>=4 and valid_N>=4; use all valid trials",
            "minimum_analyzable_AD_tasks": 20,
            "arm_imbalance_hold": "Fisher two-sided p<0.05 AND absolute A/D failure-rate difference>0.10",
            "failed_units_terminal": True, "replacement": False,
        },
        "power": {
            "MDE80": pilot["MDE80"], "POWER_LIMITED": pilot["POWER_LIMITED"],
            "N_or_K_changed_from_pilot_effect": False,
        },
        "predictions": {
            "P1": "R1_A == R1_B == R1_E for every task",
            "P2": "R1_D != R1_A for every task",
            "P3": "repeated A may differ behaviorally under identical R1",
            "P4": "if representation propagates, T_global(A,D)>0 beyond same-state dispersion",
            "P5": "A-v-N may establish memory uptake",
            "P6": "relevance moderation is secondary/exploratory",
            "P7": "R3 may differ while R4 remains similar",
        },
        "artifact_schema": {
            "run": ["run_id", "ordinal", "round", "instance_id", "arm", "attempt_count",
                    "complete R1 hash", "requests", "responses", "actions", "final patch",
                    "EditTargetSet", "R2/R3 observables", "R4", "failure", "cleanup"],
            "index": ["frozen order", "inflight", "journal", "attempt counts", "persisted receipts"],
        },
        "failure_handling": {
            "ambiguous accepted generation": "terminal missing/failed unit; never reissue run ID",
            "provider_runtime_evaluator_parser": "persist terminal layer; no replacement",
            "resource exhaustion": "do not start next untouched unit; resume later in same global order",
        },
        "claim_boundary": {
            "R3_does_not_require_R4_difference": True,
            "POWER_LIMITED_null_wording": (
                "no detectable behavioral distribution shift larger than the qualified precision range"
            ),
            "prohibited": ["no effect", "behavioral equivalence", "STRI disproven",
                           "model-independent", "all self-evolving agents", "population-wide SWE-bench effect"],
        },
        "execution_order_rule": (
            "derive seed from SHA256(experiment_id||this frozen manifest file SHA); "
            "six rounds; deterministic task and within-task arm shuffle; exact early/middle/late balance"
        ),
        "execution_authority": "UNAUTHORIZED_PENDING_SEPARATE_RESOURCE_AUTHORITY",
        "credential_material_present": False,
    }


def freeze_manifest(output: Path = MANIFEST) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite confirmatory manifest")
    payload = manifest_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload)}


def schedule_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text())
    structural = json.loads(STRUCTURAL.read_text())
    split = json.loads(SPLIT.read_text())
    schedule = build_schedule(
        manifest["evaluation_population"]["task_ids"],
        experiment_id=EXPERIMENT_ID, frozen_manifest_sha256=sha256_file(MANIFEST))
    enriched = []
    per_task = manifest["per_task_frozen_state"]
    for row in schedule["units"]:
        task = per_task[row["instance_id"]]
        enriched.append({
            **row, "task_sha256": task["task_sha256"],
            "expected_R1_sha256": task["complete_R1_sha256"][row["arm"]],
            "qualification_receipt": task["qualification_receipt"],
            "qualification_receipt_sha256": task["qualification_receipt_sha256"],
        })
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_CONFIRMATORY_EXECUTION_SCHEDULE",
        "created_at_utc": utcnow(),
        "decision": "QWEN_432_UNIT_GLOBAL_SCHEDULE_FROZEN_EXECUTION_UNAUTHORIZED",
        "manifest_sha256": sha256_file(MANIFEST), "rng_seed": schedule["rng_seed"],
        "unit_count": len(enriched), "units": enriched,
        "schedule_sha256": sha256_text(canonical_json(enriched)),
        "execution_policy": schedule["execution_policy"],
        "operational_chunking": "contiguous only; boundaries frozen by resource authority",
        "credential_material_present": False,
    }


def freeze_schedule(output: Path = SCHEDULE) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite confirmatory schedule")
    payload = schedule_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "unit_count": payload["unit_count"], "schedule_sha256": payload["schedule_sha256"]}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-manifest", action="store_true")
    parser.add_argument("--freeze-schedule", action="store_true")
    args = parser.parse_args()
    if args.freeze_manifest == args.freeze_schedule:
        raise SystemExit("choose exactly one freeze action")
    print(json.dumps(freeze_manifest() if args.freeze_manifest else freeze_schedule(), sort_keys=True))


if __name__ == "__main__":
    main()
