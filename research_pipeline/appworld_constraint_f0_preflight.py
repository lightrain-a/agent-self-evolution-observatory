from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research_pipeline.ark_provider import ARK_MODELS, ArkSettings

OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
GENERATED_AT = "2026-08-31T19:45:00+08:00"
ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
FAMILY_MANIFEST = (
    GENERATED / "agent-constraint-externality-matched-family-manifest-20260831.json"
)
COMPILER_QUALIFICATION = (
    GENERATED / "agent-constraint-externality-appworld-compiler-qualification-20260831.json"
)
COMPILER_MANIFEST = (
    GENERATED / "agent-constraint-externality-appworld-compiler-manifest-20260831.json"
)
CAPABILITY_FAMILIES = (
    "ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06"
)
F0_FAMILIES = (
    "ACE-FG-01", "ACE-FG-02", "ACE-FG-03", "ACE-FG-04",
    "ACE-TNF-01", "ACE-TNF-02", "ACE-TNF-03", "ACE-TNF-04",
)
MODEL_SELECTION_ORDER = (
    "doubao-seed-2.0-lite", "deepseek-v4-flash", "deepseek-v4-pro"
)
SEEDS = (1201, 1202, 1203)
ARMS = ("INDEPENDENT", "LOW", "HIGH")
BRANCHES = ("NO_UPDATE", "UPDATE")


class PreflightError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    families = read_json(FAMILY_MANIFEST)
    qualification = read_json(COMPILER_QUALIFICATION)
    if families["object_id"] != OBJECT_ID or qualification["object_id"] != OBJECT_ID:
        raise PreflightError("Scientific object identity mismatch.")
    if qualification["verdict"] != "PRE_F0_5_PASS":
        raise PreflightError("F0 preflight requires PRE_F0_5_PASS.")
    if not all(qualification["pass_conditions"].values()):
        raise PreflightError("A compiler pass condition is false.")
    available = {row["family_id"]: row for row in families["families"]}
    selected = set(CAPABILITY_FAMILIES) | set(F0_FAMILIES)
    if set(CAPABILITY_FAMILIES) & set(F0_FAMILIES):
        raise PreflightError("Capability and decisive splits overlap.")
    if selected != set(available):
        raise PreflightError("Outcome-blind split must partition all compiled families.")
    if not all(model in ARK_MODELS for model in MODEL_SELECTION_ORDER):
        raise PreflightError("A preregistered model is absent from the provider catalog.")
    return families, qualification


def build_artifacts() -> dict[str, dict[str, Any]]:
    families, qualification = validate_inputs()
    settings = ArkSettings.from_env(required=False)
    safe_provider = settings.safe_summary()
    provider_ready = bool(safe_provider["configured"])

    capability = {
        "schema_version": "agent-constraint-externality-capability-calibration-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "stage": "DISJOINT_CAPABILITY_CALIBRATION",
        "outcome_status": "NOT_EXECUTED",
        "family_split_rule": "FIXED_BEFORE_ANY_PROVIDER_CALL",
        "family_ids": list(CAPABILITY_FAMILIES),
        "family_count": len(CAPABILITY_FAMILIES),
        "repeats_per_family": 2,
        "episodes_per_candidate": len(CAPABILITY_FAMILIES) * 2,
        "maximum_candidate_count": len(MODEL_SELECTION_ORDER),
        "maximum_episode_envelope": (
            len(CAPABILITY_FAMILIES) * 2 * len(MODEL_SELECTION_ORDER)
        ),
        "model_selection_order": list(MODEL_SELECTION_ORDER),
        "selection_rule": "FIRST_CANDIDATE_MEETING_ALL_FLOOR_AND_CEILING_RULES",
        "candidate_isolation": (
            "Each rejected candidate uses only this disjoint split; no F0 family "
            "outcome is readable before backbone freeze."
        ),
        "qualification_rules": {
            "tool_loop_completion_rate_min": 0.75,
            "target_success_rate_min": 0.50,
            "target_success_rate_max": 0.875,
            "baseline_non_target_preservation_rate_min": 0.85,
            "zero_malformed_function_calls_required": True,
        },
        "floor_disposition": "TRY_NEXT_PREDECLARED_CANDIDATE_OR_STOP",
        "ceiling_disposition": "TRY_NEXT_PREDECLARED_CANDIDATE_OR_HARDER_PREDECLARED_STRATUM",
        "all_candidates_fail_disposition": "CAPABILITY_CALIBRATION_FAIL_STOP",
        "execution": {
            "provider": "ARK_RESPONSES_API",
            "provider_max_retries": 0,
            "application_retry": False,
            "tool_interaction_cap": 12,
            "temperature": 0,
            "append_only_ledger": True,
            "no_episode_replacement": True,
        },
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
        "gpu_runs": 0,
    }

    f0 = {
        "schema_version": "agent-constraint-externality-f0-protocol-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "stage": "F0_FROZEN_NOT_EXECUTED",
        "family_ids": list(F0_FAMILIES),
        "family_count": len(F0_FAMILIES),
        "split_is_disjoint_from_capability": True,
        "backbone": "FROZEN_FROM_CAPABILITY_CALIBRATION_BEFORE_F0",
        "harness": "APPWORLD_FUNCTION_CALLING_V1",
        "update_surface": "PERSISTENT_PROCEDURAL_REPAIR_NOTE",
        "source_phase": {
            "episodes": len(F0_FAMILIES),
            "one_target_isolated_episode_per_family": True,
            "updater_input": [
                "TARGET_CONSTRAINT_SPEC",
                "TARGET_TASK_INSTRUCTION",
                "TARGET_FAILURE_SLICE",
                "TARGET_TOOL_TRAJECTORY",
            ],
            "forbidden_updater_input": [
                "NON_TARGET_OUTCOMES",
                "TOPOLOGY_LABEL",
                "COUPLING_LEVEL",
                "ARM_ASSIGNMENT",
                "F0_EFFECT",
            ],
            "candidate_generation": (
                "Same frozen backbone generates one procedural repair note "
                "automatically from target failure only."
            ),
            "human_edit_after_generation": False,
            "freeze_fields": [
                "sha256", "exact_bytes", "byte_length",
                "fixed_tokenizer_token_count", "procedural_clause_count",
                "injection_position", "exposure_rule",
            ],
            "minimum_eligible_repair_families": 6,
            "maximum_eligible_repair_families": 8,
            "failure_or_success_retention": (
                "Retain every source result; never replace a family. Only a "
                "preregistered target failure can yield a repair artifact."
            ),
        },
        "probe_phase": {
            "arms": list(ARMS),
            "branches": list(BRANCHES),
            "seeds": list(SEEDS),
            "repeats": len(SEEDS),
            "planned_episode_envelope": (
                len(F0_FAMILIES) * len(ARMS) * len(BRANCHES) * len(SEEDS)
            ),
            "actual_episode_formula": (
                "eligible_repair_family_count * 3 arms * 2 branches * 3 seeds"
            ),
            "same_update_bytes_across_all_arms_and_update_replays": True,
            "reset_snapshot_before_every_replay": True,
            "partial_effects_readable_during_execution": False,
            "branch_order": {
                "method": "SHA256_PARITY",
                "salt": "ACE-F0-BRANCH-ORDER-20260831-V1",
                "key_fields": ["family_id", "arm", "seed"],
                "balanced_pair_rule": (
                    "Parity zero runs NO_UPDATE first; parity one runs UPDATE first."
                ),
            },
        },
        "exactly_once": {
            "provider_max_retries": 0,
            "application_retry": False,
            "append_only_ledger": True,
            "unique_episode_key_fields": ["family_id", "arm", "branch", "seed"],
            "dispatch_recorded_before_provider_call": True,
            "completion_appended_after_provider_call": True,
            "duplicate_key_is_fatal": True,
            "failed_or_partial_episode_retained": True,
            "retry_or_replacement_forbidden": True,
        },
        "metrics": {
            "target_repair_gain": "TARGET_UPDATE_MINUS_NO_UPDATE",
            "collateral_regression_rate": (
                "NEWLY_FAILED_BASELINE_SATISFIED_NON_TARGETS_DIVIDED_BY_ELIGIBLE_NON_TARGETS"
            ),
            "update_attributable_externality": "CRR_UPDATE_MINUS_CRR_NO_UPDATE",
            "primary_contrast": "UE_HIGH_MINUS_UE_INDEPENDENT_WITHIN_REPAIR_FAMILY",
            "secondary_ordered_contrast": "UE_INDEPENDENT_LE_UE_LOW_LE_UE_HIGH",
            "negative_values_retained": True,
            "per_constraint_rows_required": True,
        },
        "adjudication": {
            "uptake_fail": (
                "Fewer than 6 eligible repair families or mean target repair gain "
                "is not positive."
            ),
            "mechanism_support": (
                "At least 6 eligible families, positive mean target repair gain, "
                "mean within-family UE_HIGH-UE_INDEPENDENT >= 0.05, and the "
                "ordered exposure direction holds in at least two thirds of "
                "eligible families."
            ),
            "mechanism_fail": (
                "Uptake passes but mean UE_HIGH-UE_INDEPENDENT <= 0 and no ordered "
                "exposure direction remains."
            ),
            "otherwise": "F0_INCONCLUSIVE_STOP_OR_REVISE_WITHOUT_P1",
            "no_significance_claim_from_f0": True,
        },
        "post_f0_authority": {
            "toolsandbox_only_after": "F0_MECHANISM_SUPPORT",
            "appworld_ul_only_after": "F0_AND_TOOLSANDBOX_MECHANISM_SUPPORT",
            "full_p1": False,
            "workarena": False,
            "multi_backbone": False,
            "method_claim": False,
            "paper_claim": False,
        },
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
        "gpu_runs": 0,
    }

    readiness_status = (
        "CAPABILITY_CALIBRATION_READY_NOT_EXECUTED"
        if provider_ready
        else "CAPABILITY_CALIBRATION_BLOCKED_PROVIDER_NOT_CONFIGURED"
    )
    readiness = {
        "schema_version": "agent-constraint-externality-f0-readiness-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "status": readiness_status,
        "compiler_verdict": qualification["verdict"],
        "compiler_pass_conditions_all_true": all(
            qualification["pass_conditions"].values()
        ),
        "capability_contract_frozen": True,
        "f0_contract_frozen": True,
        "provider": safe_provider,
        "execution_override": {
            "max_retries": 0,
            "note": "Frozen protocol overrides provider default for scientific calls.",
        },
        "blocker": (
            None
            if provider_ready
            else "ARK_API_KEY is absent from the configured ignored server environment."
        ),
        "next_authorized_action": (
            "RUN_DISJOINT_CAPABILITY_CALIBRATION"
            if provider_ready
            else "CONFIGURE_PROVIDER_CREDENTIAL_THEN_RERUN_READINESS"
        ),
        "f0_executed": False,
        "f0_outcomes_observed": 0,
        "tool_sandbox_authorized": False,
        "appworld_ul_authorized": False,
        "p1_authorized": False,
    }
    return {
        "agent-constraint-externality-capability-contract-20260831.json": capability,
        "agent-constraint-externality-f0-frozen-protocol-20260831.json": f0,
        "agent-constraint-externality-f0-readiness-20260831.json": readiness,
    }


def main() -> None:
    artifacts = build_artifacts()
    for name, payload in artifacts.items():
        write_json(GENERATED / name, payload)
    manifest_files = {
        str((GENERATED / name).relative_to(ROOT)): {
            "sha256": file_sha256(GENERATED / name),
            "bytes": (GENERATED / name).stat().st_size,
        }
        for name in artifacts
    }
    for path in (FAMILY_MANIFEST, COMPILER_QUALIFICATION, COMPILER_MANIFEST):
        manifest_files[str(path.relative_to(ROOT))] = {
            "sha256": file_sha256(path),
            "bytes": path.stat().st_size,
        }
    readiness = artifacts[
        "agent-constraint-externality-f0-readiness-20260831.json"
    ]
    manifest = {
        "schema_version": "agent-constraint-externality-f0-preflight-manifest-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "status": readiness["status"],
        "files": manifest_files,
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
        "gpu_runs": 0,
        "authority": {
            "capability_calibration": (
                readiness["status"] == "CAPABILITY_CALIBRATION_READY_NOT_EXECUTED"
            ),
            "f0": False,
            "toolsandbox": False,
            "appworld_ul": False,
            "p1": False,
            "method": False,
            "paper_claim": False,
        },
    }
    write_json(
        GENERATED / "agent-constraint-externality-f0-preflight-manifest-20260831.json",
        manifest,
    )
    print(json.dumps({
        "status": readiness["status"],
        "capability_family_count": len(CAPABILITY_FAMILIES),
        "f0_family_count": len(F0_FAMILIES),
        "f0_episode_envelope": (
            len(F0_FAMILIES) * len(ARMS) * len(BRANCHES) * len(SEEDS)
        ),
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
