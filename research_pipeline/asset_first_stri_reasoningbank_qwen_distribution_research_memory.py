"""Deposit the E1/STRI Qwen experiment as reusable scientific memory."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, sha256_file, utcnow, write_json,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
ADJUDICATION = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-adjudication-20260901.json"
SOURCE_BANK = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-bank-20260901.json"
STRUCTURAL = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-structural-result-20260901.json"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-scientific-memory-20260901.json"


def lesson_catalog() -> list[str]:
    return [
        "implementation/operationalization failure -> no scientific belief update -> prospective repaired qualification",
        "return code 0 does not guarantee evaluator observability",
        "SSH/client acknowledgement failure does not imply remote side effect failure",
        "same exact model-visible request does not guarantee identical sampled trajectory",
        "single-rollout inequality is not behavioral causal evidence under a stochastic backend",
        "fixed irrelevant memory across unrelated tasks is insufficient for a decision-relevance behavioral test",
        "behavioral representation effects must be measured relative to same-state stochastic dispersion",
        "source-memory relevance must be generated/retrieved prospectively, not hand-selected from favorable outcomes",
    ]


def memory_payload() -> dict[str, Any]:
    adjudication = json.loads(ADJUDICATION.read_text())
    source_bank = json.loads(SOURCE_BANK.read_text())
    structural = json.loads(STRUCTURAL.read_text())
    primary = adjudication["primary_A_vs_D"]["permutation"]
    uptake = adjudication["secondary_A_vs_N"]["permutation"]
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "SCIENTIFIC_MEMORY_DEPOSITION", "created_at_utc": utcnow(),
        "decision": "QWEN_BEHAVIORAL_DISTRIBUTION_EXPERIMENT_DEPOSITED",
        "input_hashes": {
            "adjudication": sha256_file(ADJUDICATION),
            "source_bank": sha256_file(SOURCE_BANK),
            "structural": sha256_file(STRUCTURAL),
        },
        "historical_sequence": {
            "Q2": "evidence preserved",
            "Q3": (
                "stopped before model outcome because the runtime base-state rule was "
                "overly strict; not a mechanism negative"),
            "Q4": (
                "independently preregistered outcome-blind implementation repair; "
                "implementation qualification only"),
            "DeepSeek_Full_P1": (
                "immutable FULL_P1_BEHAVIORAL_PROPAGATION_ADJUDICATION_HOLD; "
                "same-R1 stochastic divergence motivated distributional measurement; "
                "fixed cross-task memory was structurally useful but weakly decision-relevant"),
        },
        "three_carrier_theory": {
            "Skill-Pro": {
                "role": "PREDICTED FAILURE",
                "boundary": "identity-local readiness/evolution gate",
            },
            "ACE": {
                "role": "PREDICTED REPAIR/TIMING CONDITION",
                "boundary": "reunion must precede the consuming operator",
            },
            "ReasoningBank": {
                "role": "CONDITIONAL NATIVE POSITIVE CONTROL",
                "boundary": (
                    "within-case fragments reunite before consumption; cross-case top-1 "
                    "partition can prevent reunion"),
            },
        },
        "qwen_experiment": {
            "source_task_count": len(source_bank["entries"]),
            "confirmatory_task_count": len(
                structural["confirmatory_task_ids"]),
            "structural_A_B_E_equal_count": adjudication["structural"][
                "A_B_E_exact_R1_equal_count"],
            "structural_D_differs_count": adjudication["structural"][
                "D_R1_differs_A_count"],
            "N_analyzable_AD": adjudication["N_analyzable_AD"],
            "primary_global_T": None if primary is None else primary["observed_global_T"],
            "primary_p": None if primary is None else primary["monte_carlo_p_value"],
            "uptake_global_T": None if uptake is None else uptake["observed_global_T"],
            "uptake_p": None if uptake is None else uptake["monte_carlo_p_value"],
            "scientific_decision": adjudication["decision"],
            "strongest_supported_claim": adjudication["scientific_adjudication"][
                "strongest_supported_claim"],
            "POWER_LIMITED": adjudication["POWER_LIMITED"],
            "MDE80": adjudication["MDE80"],
        },
        "reusable_lessons": lesson_catalog(),
        "claim_boundary": adjudication["claim_boundary"],
        "failed_units_retained": True, "selective_memory_deletion": False,
        "retry_or_replacement": False, "credential_material_present": False,
    }


def deposit(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing duplicate scientific-memory deposition")
    payload = memory_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload)}


def main() -> None:
    print(json.dumps(deposit(), sort_keys=True))


if __name__ == "__main__":
    main()
