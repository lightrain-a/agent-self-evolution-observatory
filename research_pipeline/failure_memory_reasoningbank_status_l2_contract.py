"""Build the zero-call R9 L2B power sensitivity and adapter contract.

The outputs bind the already-frozen 36-unit ReasoningBank-status preflight.
They do not materialize a runtime, generate memories, execute a browser, or call
a model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
POWER_ID = "D2-C45-L2B-STATUS-POWER-SENSITIVITY-R9"
CONTRACT_ID = "D2-C45-L2B-REASONINGBANK-STATUS-ADAPTER-R9"
ALPHA = 0.05
EFFECT = 0.15
TARGET_POWER = 0.80
EXPECTED_UNITS = 36


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def build_power(preflight: dict[str, Any], *, preflight_sha: str, census_sha: str) -> dict[str, Any]:
    n = int(preflight["cohort_summary"]["template_independent_units"])
    if n != EXPECTED_UNITS:
        raise ValueError(f"unit drift: {n}")
    z_one = 1.6448536269514722
    z_two = 1.959963984540054
    scenarios = []
    for sd in (0.20, 0.30, 0.40):
        noncentral = EFFECT * math.sqrt(n) / sd
        one = phi(noncentral - z_one)
        two = 1.0 - phi(z_two - noncentral) + phi(-z_two - noncentral)
        scenarios.append(
            {
                "task_level_sd": sd,
                "independent_tasks": n,
                "approx_one_sided_power": round(one, 6),
                "approx_two_sided_power": round(two, 6),
                "two_sided_target_0_80_met": two >= TARGET_POWER,
            }
        )
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "plan_id": POWER_ID,
        "recorded_date": "2026-08-24",
        "status": "FULL_36_COHORT_SENSITIVITY_FROZEN_NO_POWER_GUARANTEE_NO_EXECUTION_AUTHORITY",
        "analysis_type": "prospective-L2B-design-sensitivity-not-retrospective-power",
        "preflight_sha256": preflight_sha,
        "candidate_census_sha256": census_sha,
        "independent_unit": "one downstream task per intent_template_id",
        "maximum_frozen_independent_tasks": n,
        "primary_hypothesis": "two-sided metadata effect; no justified a-priori sign for success versus failure provenance metadata",
        "target_absolute_effect": EFFECT,
        "alpha": ALPHA,
        "target_power": TARGET_POWER,
        "approximation": "normal approximation for a paired task-level mean used only as a pre-outcome sensitivity envelope; confirmatory inference remains the frozen task-level randomization test",
        "planning_scenarios": scenarios,
        "planning_decision": {
            "use_full_36_unit_cohort_if_executed": True,
            "outcome_adaptive_early_stop": False,
            "post_outcome_task_replacement": False,
            "post_outcome_sample_extension": False,
            "claim_80_percent_power_unconditionally": False,
            "reason": "36 exceeds the two-sided n=32 reference under SD=.30 but not n=56 under SD=.40; L2-specific variance and rollout/noise assumptions must be frozen before any claim of adequate power.",
        },
        "execution_bindings_still_required": [
            "paired rollout/seed count per arm",
            "executor/model/version and decoding randomness",
            "pre-outcome L2-specific variance/noise source or exact simulation assumptions",
            "missingness/provider/browser retry policy",
            "final randomization enumeration/simulation implementation",
        ],
        "primary_decision_rule_draft": {
            "estimand": "mean across 36 task units of terminal WebArena score(status=S) - terminal WebArena score(status=F)",
            "support_if": "abs(mean_delta) >= 0.15 AND two-sided task-level randomization p < 0.05",
            "otherwise": "INCONCLUSIVE_NO_NO_EFFECT_AUTHORITY",
            "directional_p_values": "secondary descriptive only",
        },
        "scientific_verdict": "NO_VERDICT_PLANNING_ONLY",
        "scientific_authority": False,
        "experiment_authority": False,
        "model_calls": False,
        "gpu_authority": False,
    }


def build_contract(preflight: dict[str, Any], power: dict[str, Any], *, preflight_sha: str, power_path: Path) -> dict[str, Any]:
    n = int(preflight["cohort_summary"]["template_independent_units"])
    if n != EXPECTED_UNITS:
        raise ValueError(f"unit drift: {n}")
    rb = preflight["first_party_reasoningbank_binding"]
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "contract_id": CONTRACT_ID,
        "recorded_date": "2026-08-24",
        "status": "IDENTIFICATION_COHORT_AND_STATISTICAL_DIRECTION_FROZEN_RUNTIME_EXECUTOR_BUDGET_UNBOUND",
        "role": "PROSPECTIVE_PRE_OUTCOME_ADAPTER_CONTRACT_NO_EXECUTION_AUTHORITY",
        "separate_from_historical_objects": {
            "R5": "remains frozen 5/10 support failure with zero calls",
            "historical_explicit_cue_bridge": "remains six prior units / 144 calls / delta 0 / p=1 / inconclusive",
            "pooling_with_R5_or_bridge": False,
            "L3_financial_transport": False,
        },
        "source_bindings": {
            "reasoningbank_commit": rb["commit"],
            "reasoningbank_file_sha256": rb["file_sha256"],
            "downstream_asset_sha256": preflight["frozen_downstream_asset"]["sha256"],
            "task_config_sha256": preflight["frozen_downstream_asset"]["config_sha256"],
            "preflight_sha256": preflight_sha,
            "power_sensitivity_path": str(power_path),
            "power_sensitivity_sha256": "BOUND_AFTER_WRITE",
        },
        "native_field": {
            "name": "status",
            "native_values": ["success", "fail"],
            "semantics": "source trajectory terminal outcome used by the first-party ReasoningBank writer",
            "stored_separately_from_memory_items": True,
            "default_executor_hidden": True,
        },
        "intervention": {
            "arms": ["STATUS_S", "STATUS_F"],
            "constant_semantic_legend": "ReasoningBank status code: S means source trajectory success; F means source trajectory fail.",
            "STATUS_S_serialization": "status: S",
            "STATUS_F_serialization": "status: F",
            "single_character_treatment_difference": True,
            "memory_items_bytes_identical_across_arms": True,
            "selected_source_record_id_identical_across_arms": True,
            "retrieval_or_forced_disclosure_selection_run_once_before_arm_rendering": True,
            "status_must_not_affect_retrieval_admission_rank_or_order": True,
        },
        "cohort": {
            "independent_units": n,
            "downstream_task_ids": preflight["cohort_summary"]["downstream_task_ids"],
            "source_task_ids": preflight["cohort_summary"]["source_task_ids"],
            "one_downstream_unit_per_intent_template": True,
            "selection_uses_downstream_outcome": False,
            "selection_uses_source_outcome": False,
            "source_status_read_after_assignment_only": True,
            "full_cohort_required_if_executed": True,
            "outcome_adaptive_subset_forbidden": True,
            "post_outcome_replacement_forbidden": True,
        },
        "source_memory_generation": {
            "status": "UNBOUND_EXECUTION_COMPONENT",
            "required": "For each frozen source task, create one ReasoningBank memory record once using the pinned first-party success/fail writer contract corresponding to its native source status; freeze task_id/status/memory_items/content hash before downstream arm execution.",
            "writer_model_unbound": True,
            "writer_temperature_unbound": True,
            "generation_calls_authorized": False,
            "no_arm_specific_regeneration": True,
            "memory_content_selected_or_edited_after_downstream_outcomes": False,
        },
        "downstream_runtime": {
            "required_python": ">=3.13",
            "required_browsergym": "0.14.1",
            "required_webarena": "0.14.1",
            "exact_runtime_currently_materialized_on_69": bool(preflight["runtime_materialization"]["current_69_exact_runtime_found"]),
            "installed_0_4_0_runtime_may_substitute": False,
            "environment_reset_between_task_arm_runs_required": True,
            "official_task_evaluator_required": True,
        },
        "executor": {
            "model_unbound": True,
            "version_unbound": True,
            "decoding_unbound": True,
            "paired_seed_count_unbound": True,
            "maximum_request_budget_unbound": True,
            "execution_calls_authorized": False,
        },
        "primary_analysis": {
            "estimand": "task-level terminal WebArena score difference STATUS_S minus STATUS_F averaged over the 36 frozen template-independent tasks",
            "primary_test": "two-sided task-level paired randomization/sign-flip test",
            "alpha": ALPHA,
            "practical_effect_floor_abs_delta": EFFECT,
            "support_if": "abs(mean_delta) >= 0.15 and p_two_sided < 0.05",
            "otherwise": "INCONCLUSIVE_NO_NO_EFFECT_AUTHORITY",
            "directional_sign_claim_predeclared": False,
            "two_sided_sensitivity_and_paired_interval_required": True,
        },
        "fail_closed_rules": [
            "no threshold rescue",
            "no task replacement after any downstream outcome",
            "no reuse of prior-D2 downstream units",
            "no arm-specific retrieval",
            "no arm-specific memory regeneration",
            "no switch from terminal endpoint to early-action endpoint after outcomes",
            "no substitution of BrowserGym 0.4.0 for 0.14.1",
            "no scientific claim from support/runtime failures",
        ],
        "execution_gate": {
            "support_capacity_pass": True,
            "cohort_frozen": True,
            "native_field_pinned": True,
            "power_sensitivity_frozen": True,
            "exact_runtime_materialized": bool(preflight["runtime_materialization"]["current_69_exact_runtime_found"]),
            "source_memory_generation_bound": False,
            "executor_budget_bound": False,
            "scientific_authority": False,
            "experiment_authority": False,
            "execution_permitted": False,
        },
        "scientific_verdict": "NO_VERDICT_CONTRACT_ONLY",
        "scientific_authority": False,
        "experiment_authority": False,
        "model_calls": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def dump(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--preflight", type=Path, required=True)
    p.add_argument("--census", type=Path, required=True)
    p.add_argument("--power-output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-power-sensitivity-r9.json"))
    p.add_argument("--contract-output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-adapter-contract-r9.json"))
    args = p.parse_args()

    preflight = json.loads(args.preflight.read_text(encoding="utf-8"))
    preflight_sha = sha256(args.preflight)
    census_sha = sha256(args.census)
    power = build_power(preflight, preflight_sha=preflight_sha, census_sha=census_sha)
    dump(args.power_output, power)
    contract = build_contract(preflight, power, preflight_sha=preflight_sha, power_path=args.power_output)
    contract["source_bindings"]["power_sensitivity_sha256"] = sha256(args.power_output)
    dump(args.contract_output, contract)
    print(json.dumps({
        "power_status": power["status"],
        "contract_status": contract["status"],
        "units": power["maximum_frozen_independent_tasks"],
        "execution_permitted": contract["execution_gate"]["execution_permitted"],
        "scientific_authority": False,
        "model_calls": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
