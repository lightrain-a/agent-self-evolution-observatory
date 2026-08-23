"""Freeze the pre-outcome runtime policy addendum for B1 L2B.

This addendum converts the R10 support audit into a prospective runtime policy.
It changes no scientific value and does not authorize browser/model execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
ADDENDUM_ID = "D2-C45-L2B-RUNTIME-ADDENDUM-R10"
EXPECTED_PARENT_STATUS = "IDENTIFICATION_COHORT_AND_STATISTICAL_DIRECTION_FROZEN_RUNTIME_EXECUTOR_BUDGET_UNBOUND"
EXPECTED_AUDIT_STATUS = "DECLARED_PY313_RUNTIME_NOT_DIRECTLY_MATERIALIZABLE_PY312_WEBARENA_COMPATIBILITY_PATH_VERIFIED"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_addendum(parent: dict[str, Any], audit: dict[str, Any], *, parent_sha: str, audit_sha: str) -> dict[str, Any]:
    if parent.get("status") != EXPECTED_PARENT_STATUS:
        raise ValueError("parent R9 adapter contract drift")
    if audit.get("status") != EXPECTED_AUDIT_STATUS:
        raise ValueError("R10 runtime audit drift")
    if int(parent["cohort"]["independent_units"]) != 36:
        raise ValueError("parent cohort drift")
    adj = audit["adjudication"]
    compat = audit["python312_compatibility_runtime"]
    if adj["exact_declared_python313_runtime_materialized"] is not False:
        raise ValueError("unexpected exact runtime state")
    if adj["python312_browsergym0141_component_path_materialized"] is not True:
        raise ValueError("compatibility runtime missing")
    if adj["python312_webarena_import_verified"] is not True:
        raise ValueError("compatibility WebArena import missing")
    if compat["webarena_registered_task_ids"] != 812:
        raise ValueError("WebArena registry drift")

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "addendum_id": ADDENDUM_ID,
        "recorded_date": "2026-08-24",
        "status": "PY312_BG0141_COMPATIBILITY_RUNTIME_SELECTED_PREOUTCOME_LIVE_DEPLOYMENT_BLOCKED",
        "role": "PROSPECTIVE_RUNTIME_POLICY_ADDENDUM_NO_SCIENTIFIC_AUTHORITY",
        "bindings": {
            "parent_r9_adapter_contract_sha256": parent_sha,
            "r10_runtime_audit_sha256": audit_sha,
            "reasoningbank_commit": audit["first_party_runtime"]["commit"],
            "cohort_units": parent["cohort"]["independent_units"],
            "downstream_task_ids": parent["cohort"]["downstream_task_ids"],
        },
        "runtime_policy": {
            "exact_declared_python313_path": "SUPPORT_FAILED_STANDARD_BUILD",
            "selected_l2b_runtime_label": "PY312_BG0141_EXPLICIT_COMPATIBILITY_DEVIATION",
            "python": compat["python"],
            "browsergym_core": compat["versions"]["browsergym-core"],
            "browsergym_experiments": compat["versions"]["browsergym-experiments"],
            "browsergym_webarena": compat["versions"]["browsergym-webarena"],
            "playwright": compat["versions"]["playwright"],
            "greenlet": compat["versions"]["greenlet"],
            "libwebarena": compat["versions"]["libwebarena"],
            "reasoningbank_source_commit_unchanged": True,
            "intervention_renderer_unchanged": True,
            "cohort_unchanged": True,
            "primary_analysis_unchanged": True,
            "runtime_deviation": "Python 3.12.13 replaces the first-party declared Python>=3.13 because the locked greenlet 3.0.3 standard build fails on Python 3.13; benchmark component versions remain at the first-party locked WebArena path.",
        },
        "identification_scope": {
            "why_l2_definition_survives_runtime_deviation": "Both metadata arms use the same compatibility runtime; selected memory ID/order, memory_items bytes, query/state, retrieval result, and all non-status prompt bytes remain paired and identical. The interpreter deviation changes evaluated-substrate/runtime transport, not which variable is manipulated within the L2 pair.",
            "strongest_allowed_positive_claim": "A provenance-status metadata effect on the frozen ReasoningBank/WebArena compatibility substrate.",
            "forbidden_claims": [
                "exact-as-declared ReasoningBank runtime replication",
                "source-faithful financial AgentDojo transport",
                "general provenance effect across runtimes",
                "R5 rescue or pooling with historical bridge units",
            ],
            "o6_l3_unblocked": False,
        },
        "live_runtime_support": {
            "webarena_import_verified": compat["webarena_import_completed"],
            "registered_webarena_task_ids": compat["webarena_registered_task_ids"],
            "expected_chromium_revision": compat["playwright_chromium_revision"],
            "matching_chromium_cache_found": compat["matching_default_chromium_cache_found"],
            "required_site_envs": list(compat["webarena_site_env_configured"].keys()),
            "all_required_site_envs_present": compat["webarena_all_required_site_envs_present"],
            "live_webarena_deployment_detected": compat["live_webarena_deployment_detected"],
        },
        "execution_gate": {
            "native_status_field_pinned": True,
            "36_unit_cohort_frozen": True,
            "two_sided_primary_and_effect_floor_frozen": True,
            "compatibility_package_runtime_materialized": True,
            "webarena_import_verified": True,
            "exact_chromium_revision_available": bool(compat["matching_default_chromium_cache_found"]),
            "webarena_sites_configured_and_deployed": bool(compat["live_webarena_deployment_detected"]),
            "source_native_reset_evaluator_smoke_pass": False,
            "source_memory_generation_bound": False,
            "executor_model_version_budget_bound": False,
            "l2_variance_noise_and_paired_rollouts_bound": False,
            "scientific_authority": False,
            "experiment_model_call_authority": False,
            "execution_permitted": False,
        },
        "next_support_actions": [
            "Recover or deploy the seven WebArena site endpoints and bind their URLs without opening model outcomes.",
            "Acquire Playwright Chromium revision 1117 in the isolated compatibility runtime.",
            "Run one no-model source-native environment reset/evaluator smoke before any L2 outcome execution.",
            "Freeze source-memory generation/fixed-selection and executor/model/request-budget bindings.",
            "Freeze L2-specific variance/noise and paired-rollout assumptions plus final randomization implementation.",
            "Obtain separate scientific and experiment/model-call authority before executing the 36-unit cohort.",
        ],
        "scientific_verdict": "NO_VERDICT_RUNTIME_POLICY_ONLY",
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_calls": False,
            "browser_tasks": False,
            "gpu": False,
            "submission": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--parent-contract", type=Path, required=True)
    p.add_argument("--runtime-audit", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-runtime-addendum-r10.json"))
    args = p.parse_args()
    parent = json.loads(args.parent_contract.read_text(encoding="utf-8"))
    audit = json.loads(args.runtime_audit.read_text(encoding="utf-8"))
    payload = build_addendum(parent, audit, parent_sha=sha256(args.parent_contract), audit_sha=sha256(args.runtime_audit))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "runtime": payload["runtime_policy"]["selected_l2b_runtime_label"],
        "live_deployment": payload["live_runtime_support"]["live_webarena_deployment_detected"],
        "execution_permitted": payload["execution_gate"]["execution_permitted"],
        "scientific_verdict": payload["scientific_verdict"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
