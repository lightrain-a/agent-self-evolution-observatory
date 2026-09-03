#!/usr/bin/env python3
"""Freeze the standalone A/B L2 identification operationalization before validation outcomes.

R35/R39 define A/B as the minimum identification arms. R43 later registers A/B
and C/D as distinct non-pooled estimands. C/D cannot be executed because no
pre-outcome executable PSMG controller was frozen. This contract does not alter
that fact and does not redefine the four-arm program as complete: it freezes the
already-registered A/B identification estimand as a separately reportable L2
scientific object while C/D remains NOT EXECUTED.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
R35 = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r35-fresh-confirmatory-reopen-gate.json"
R39 = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r39-memrl-substrate-audit.json"
R40 = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r40-memrl-g5-preflight.json"
R43 = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r43-memrl-g8-execution-manifest.json"
MIGRATION = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r45m1-host-migration-execution-manifest-v2.json"
AUTH = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r45m1-replacement-execution-authority-v2.json"
ADAPTER = PROJECT_ROOT / "research_pipeline/failure_memory_memrl_exact_information_adapter_r39.py"
R46M2 = PROJECT_ROOT / "research_pipeline/failure_memory_memrl_source_qualification_r46m2.py"
R47M2 = PROJECT_ROOT / "research_pipeline/failure_memory_memrl_utilization_r47m2.py"
R48_RUNNER = PROJECT_ROOT / "research_pipeline/failure_memory_memrl_ab_identification_r48.py"
PRIMARY_AUDIT = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r45m1-primary-preimplementation-audit-20260901.json"
HIST_AUDIT = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r45m1-primary-historical-controller-audit-addendum-20260901.json"
OUT = PROJECT_ROOT / "generated/d2-failure-memory-provenance-r48-ab-identification-operationalization-contract.json"

STATUS = "PREVALIDATION_AB_IDENTIFICATION_FROZEN_C_D_REMAINS_NOT_EXECUTABLE"


def _load(p: Path) -> dict[str, Any]:
    v = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v, dict):
        raise ValueError(f"not-object:{p}")
    return v


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _digest(v: Any) -> str:
    return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _valid_receipt(v: dict[str, Any]) -> bool:
    x = v.get("receipt_sha256")
    return isinstance(x, str) and x == _digest({k: z for k, z in v.items() if k != "receipt_sha256"})


def build() -> dict[str, Any]:
    r35, r39, r40, r43, mig, auth, pa, ha = map(_load, [R35, R39, R40, R43, MIGRATION, AUTH, PRIMARY_AUDIT, HIST_AUDIT])
    if r35.get("paper_id") != PAPER_ID or r43.get("paper_id") != PAPER_ID:
        raise ValueError("paper-id-drift")
    if not _valid_receipt(mig) or not _valid_receipt(auth):
        raise ValueError("replacement-receipt-invalid")
    min_arms = ((r35.get("future_confirmatory_design_boundary") or {}).get("minimum_identification_arms") or [])
    if min_arms != ["content-only provenance-hidden baseline", "raw provenance-tag exact-information arm"]:
        raise ValueError("R35-minimum-identification-arm-drift")
    r39_arms = (((r39.get("G3_exact_information") or {}).get("minimum_identification_arms")) or [])
    if len(r39_arms) != 2 or "content-only provenance-hidden" not in r39_arms[0] or "source_outcome_success" not in r39_arms[1]:
        raise ValueError("R39-identification-arm-drift")
    e = (mig.get("execution_manifest") or {})
    if (e.get("estimands") or {}).get("identification") != "paired terminal success difference B_raw_provenance - A_content_only conditional on identical frozen retrieval":
        raise ValueError("identification-estimand-drift")
    if "distinct estimands; no pooling" not in str(e.get("multiplicity") or ""):
        raise ValueError("distinct-estimand-boundary-drift")
    if ((e.get("analysis") or {}).get("A_vs_B_and_C_vs_D_not_pooled")) is not True:
        raise ValueError("no-pooling-drift")
    if pa.get("status") != "PRIMARY_PREIMPLEMENTATION_HOLD_C_D_CONTROLLER_RULE_UNDERDETERMINED":
        raise ValueError("primary-C-D-audit-drift")
    if ((ha.get("adjudication") or {}).get("preexisting_exact_executable_C_D_controller_is_established")) is not False:
        raise ValueError("historical-controller-audit-drift")

    ids = [str(x) for x in ((e.get("confirmatory_units") or {}).get("representative_ids") or [])]
    if len(ids) != 32 or len(set(ids)) != 32:
        raise ValueError("primary-id-count-drift")
    seed = int(((e.get("randomization") or {}).get("seed") or 0))
    floor = float(((e.get("analysis") or {}).get("effect_relevance_floor") or 0.0))

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-R48-AB-IDENTIFICATION-OPERATIONALIZATION",
        "recorded_date": "2026-09-01",
        "status": STATUS,
        "role": "PREVALIDATION_OPERATIONALIZATION_ADDENDUM_FOR_ALREADY_REGISTERED_MINIMUM_L2_IDENTIFICATION_ARMS",
        "scientific_boundary": {
            "A_B_is_original_minimum_identification_contrast": True,
            "C_D_is_distinct_governance_estimand": True,
            "C_D_not_executed_by_R48": True,
            "four_arm_R43_program_may_not_be_called_complete_from_A_B_alone": True,
            "PSMG_efficacy_claim_forbidden": True,
            "A_B_and_C_D_pooling_forbidden": True,
            "historical_evidence_pooling_forbidden": True,
        },
        "bindings": {
            "R35_sha256": _sha(R35),
            "R39_sha256": _sha(R39),
            "R40_sha256": _sha(R40),
            "R43_sha256": _sha(R43),
            "replacement_manifest_sha256": _sha(MIGRATION),
            "replacement_manifest_receipt_sha256": mig.get("receipt_sha256"),
            "replacement_authority_sha256": _sha(AUTH),
            "replacement_authority_receipt_sha256": auth.get("receipt_sha256"),
            "R39_exact_information_adapter_sha256": _sha(ADAPTER),
            "R46M2_strict_source_qualification_sha256": _sha(R46M2),
            "R47M2_strict_utilization_sha256": _sha(R47M2),
            "R48_AB_runner_sha256": _sha(R48_RUNNER),
            "primary_preimplementation_audit_sha256": _sha(PRIMARY_AUDIT),
            "historical_controller_audit_sha256": _sha(HIST_AUDIT),
        },
        "units": {
            "benchmark": "OSInteraction",
            "statistical_unit": "exact frozen skill_list-signature dependency cluster representative",
            "count": 32,
            "representative_ids": ids,
            "representative_ids_sha256": (e.get("confirmatory_units") or {}).get("representative_ids_sha256"),
        },
        "arms": {
            "A_content_only": "R39 adapter content_only_provenance_hidden executor view",
            "B_raw_provenance": "R39 adapter raw_provenance_exact_information executor view; only added field is truthful boolean source_outcome_success",
        },
        "pre_arm_support_rule": {
            "R46M2_required": True,
            "all_32_primary_clusters_must_have_eligible_frozen_retrieval": True,
            "every_selected_row_used_by_A_B_must_be_eligible": True,
            "missing_or_nonboolean_source_outcome_rejects_before_any_A_B_treatment": True,
            "retrieval_rerun_between_arms": False,
        },
        "renderer": {
            "input": "R46 frozen selected rows in frozen retrieval order, reconstructed into the already-frozen R39 adapter schema",
            "adapter": "build_memrl_exact_information_pair",
            "eligible_rows_only": False,
            "eligibility_policy": "all selected rows must already be eligible; otherwise STOP before A/B execution",
            "serialization": "json.dumps(arm_view, ensure_ascii=False, sort_keys=True, separators=(',', ':'))",
            "memory_context_template": "[Retrieved Memory Context]\\n{canonical_json}",
            "base_system_prompt": "pinned MemRL DEFAULT_SYSTEM_PROMPT",
            "prompt_builder": "build_llb_prompt_with_memory(task='os', base_prompt=DEFAULT_SYSTEM_PROMPT, memory_context=rendered_context)",
            "only_executor_visible_arm_difference": "truthful boolean source_outcome_success field",
            "forbidden_executor_fields": ["memory_id", "task_id", "similarity", "q_estimate", "score", "other metadata"],
        },
        "randomization": {
            "seed": seed,
            "arms": ["A_content_only", "B_raw_provenance"],
            "per_unit_algorithm": "random.Random(int(SHA256('B1-R48-AB-ARM|<seed>|<task_id>')[:16],16)).shuffle(['A_content_only','B_raw_provenance'])",
            "schedule_created_only_after_R46M2_and_R47_PASS": True,
            "schedule_created_before_first_A_B_treatment_outcome": True,
            "outcome_adaptive_randomization": False,
        },
        "execution": {
            "endpoint": "pinned LifelongAgentBench native OSInteraction terminal success",
            "max_steps": int((e.get("source_build") or {}).get("max_steps") or 0),
            "os_timeout_seconds": int((e.get("source_build") or {}).get("os_timeout_seconds") or 0),
            "temperature": float((((e.get("models") or {}).get("llm") or {}).get("temperature") or 0.0)),
            "max_new_tokens": int((((e.get("models") or {}).get("llm") or {}).get("max_new_tokens") or 0)),
            "incremental_jsonl_required": True,
            "per_arm_trace_required": True,
            "mark_STARTED_before_environment_reset": True,
            "STARTED_without_COMPLETE_is_exposed_and_never_retried": True,
            "resume_allowed_only_from_clean_boundary_with_no_incomplete_STARTED_arm": True,
            "no_partial_effect_analysis": True,
        },
        "analysis": {
            "estimand": "mean over 32 clusters of terminal_success(B_raw_provenance) - terminal_success(A_content_only)",
            "effect_relevance_floor_abs": floor,
            "confidence_interval": "95% paired-cluster percentile bootstrap",
            "bootstrap_repetitions": 100000,
            "bootstrap_seed": seed,
            "bootstrap_quantile_method": "sort 100000 paired-resample effects; lower=floor(0.025*(B-1)), upper=ceil(0.975*(B-1))",
            "test": "two-sided exact paired sign-flip test over discordant cluster pairs (equivalent exact binomial/McNemar sign test)",
            "p_value_cannot_upgrade_rung_by_itself": True,
            "complete_case_requirement": "all 32 A/B pairs complete; no imputation",
            "analysis_only_after_64_complete_arm_runs": True,
        },
        "adjudication": {
            "A_B_allowed_claim": "fresh content-controlled executor-visible provenance identification contrast on the frozen MemRL/OSInteraction surface",
            "C_D_status": "NOT_EXECUTED_PSMG_OPERATIONALIZATION_NOT_QUALIFIED",
            "PSMG_efficacy_status": "NOT_IDENTIFIED",
            "if_A_B_null": "qualified content-controlled visible-provenance null on this surface; does not establish hidden-governance null",
            "if_A_B_effect": "visible provenance channel effect on this surface; does not establish PSMG governance value",
        },
        "prevalidation_accounting": {
            "validation_treatment_outcomes_observed": 0,
            "A_B_treatment_outcomes_observed": 0,
            "partial_A_B_effect_inspected": False,
            "source_build_may_be_in_progress": True,
            "source_success_failure_counts_may_have_been_observed_for_execution_health_monitoring": True,
            "source_outcomes_used_to_choose_primary_units": False,
            "source_outcomes_used_to_choose_renderer": False,
            "source_outcomes_used_to_choose_arm_order_algorithm": False,
            "source_outcomes_used_to_choose_effect_floor_or_analysis": False,
            "operationalization_basis": "pre-existing R35 minimum A/B identification boundary, R39 exact-information adapter, R43 distinct-estimand/no-pooling contract, and static code/contract audits",
        },
        "authority": {
            "contract_freeze": True,
            "A_B_execution": False,
            "C_D_execution": False,
            "claim_expansion": False,
        },
    }
    payload["receipt_sha256"] = _digest(payload)
    return payload


def main() -> None:
    p = build()
    OUT.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": p["status"], "receipt_sha256": p["receipt_sha256"], "A_B_execution": False, "C_D_execution": False}, sort_keys=True))


if __name__ == "__main__":
    main()
