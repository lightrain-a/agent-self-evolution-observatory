from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_qwen_model_prereg import (
    ALLOWED_ALIAS,
    MANIFEST as MODEL_ADDENDUM_MANIFEST,
    OUTPUT as MODEL_ADDENDUM,
    PROVIDER_ID,
    REQUESTED_MODEL,
    safe_provider_summary,
)

OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
GENERATED_AT = "2026-09-01T15:35:00+08:00"
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
M1_QUALIFICATION = (
    GENERATED / "agent-constraint-externality-m1-runner-qualification-v1-20260901.json"
)
M1_MANIFEST = (
    GENERATED / "agent-constraint-externality-m1-runner-qualification-v1-manifest-20260901.json"
)
CAPABILITY_FAMILIES = (
    "ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06"
)
F0_FAMILIES = (
    "ACE-FG-01", "ACE-FG-02", "ACE-FG-03", "ACE-FG-04",
    "ACE-TNF-01", "ACE-TNF-02", "ACE-TNF-03", "ACE-TNF-04",
)
MODEL_SELECTION_ORDER = (REQUESTED_MODEL,)
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
    if MODEL_SELECTION_ORDER != (REQUESTED_MODEL,):
        raise PreflightError("Exactly one Qwen candidate must remain preregistered.")
    addendum = read_json(MODEL_ADDENDUM)
    if addendum["status"] != "QWEN_MODEL_PREREG_ADDENDUM_A0_PASS":
        raise PreflightError("Qwen model prereg addendum is not qualified.")
    return families, qualification


def build_artifacts() -> dict[str, dict[str, Any]]:
    families, qualification = validate_inputs()
    safe_provider = safe_provider_summary()
    provider_ready = bool(safe_provider["configured"])
    m1 = read_json(M1_QUALIFICATION) if M1_QUALIFICATION.is_file() else {}
    m1_pass = m1.get("status") == "M1_RUNNER_QUALIFICATION_PASS"

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
        "selection_rule": "ONLY_QWEN_CANDIDATE_MUST_QUALIFY_OR_STOP",
        "requested_model": REQUESTED_MODEL,
        "allowed_alias": ALLOWED_ALIAS,
        "candidate_isolation": (
            "The single candidate uses only this disjoint split; no F0 family "
            "outcome is readable before backbone freeze."
        ),
        "qualification_rules": {
            "tool_loop_completion_rate_min": 0.75,
            "target_success_rate_min": 0.50,
            "target_success_rate_max": 0.875,
            "baseline_non_target_preservation_rate_min": 0.85,
            "zero_malformed_function_calls_required": True,
        },
        "floor_disposition": "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP",
        "ceiling_disposition": "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP",
        "interface_disposition": "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
        "automatic_fallback": False,
        "execution": {
            "provider": PROVIDER_ID,
            "provider_max_retries": 0,
            "application_retry": False,
            "capability_episode_cap": 8,
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
        "budgets": {
            "capability_agent_episodes": 8,
            "f0_source_agent_episodes": 8,
            "f0_probe_agent_episode_min": 108,
            "f0_probe_agent_episode_max": 144,
            "agent_episode_total_max": 160,
            "repair_generation_provider_request_cap": 8,
            "count_separately": [
                "agent_episode_count", "agent_model_request_count",
                "updater_model_request_count", "provider_request_total",
            ],
        },
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
                "sha256", "raw_bytes", "normalized_bytes", "byte_length",
                "word_count", "fixed_tokenizer_token_count",
                "procedural_clause_count", "injection_position", "exposure_rule",
                "generation_model_id", "generation_request_sha256",
                "source_trajectory_sha256",
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

    if not m1_pass:
        readiness_status = "M1_RUNNER_QUALIFICATION_REQUIRED"
        blocker = "M1 scientific runner qualification has not passed."
        next_action = "RUN_M1_MOCK_QUALIFICATION"
    elif not provider_ready:
        readiness_status = "QWEN_PROVIDER_CONFIGURATION_REQUIRED"
        blocker = "AA_API_KEY is not configured in the approved environment."
        next_action = "CONFIGURE_QWEN_PROVIDER_CREDENTIAL"
    else:
        readiness_status = "CAPABILITY_CALIBRATION_READY"
        blocker = None
        next_action = "RUN_QWEN_CAPABILITY_CALIBRATION"
    readiness = {
        "schema_version": "agent-constraint-externality-f0-readiness-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "status": readiness_status,
        "compiler_verdict": qualification["verdict"],
        "compiler_pass_conditions_all_true": all(
            qualification["pass_conditions"].values()
        ),
        "model_prereg_addendum_a0_pass": True,
        "m1_runner_qualification_pass": m1_pass,
        "capability_contract_frozen": True,
        "f0_contract_frozen": True,
        "provider": safe_provider,
        "execution_override": {
            "max_retries": 0,
            "note": "Frozen protocol overrides provider default for scientific calls.",
        },
        "provider_credential_present": provider_ready,
        "blocker": blocker,
        "next_authorized_action": next_action,
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
    for path in (
        FAMILY_MANIFEST, COMPILER_QUALIFICATION, COMPILER_MANIFEST,
        MODEL_ADDENDUM, MODEL_ADDENDUM_MANIFEST, M1_QUALIFICATION, M1_MANIFEST,
    ):
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
            "m1_mock_qualification": not readiness["m1_runner_qualification_pass"],
            "capability_calibration": readiness["m1_runner_qualification_pass"],
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
        "capability_episode_cap": 8,
        "f0_source_episode_cap": 8,
        "f0_probe_episode_envelope": (
            len(F0_FAMILIES) * len(ARMS) * len(BRANCHES) * len(SEEDS)
        ),
        "agent_episode_total_max": 160,
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
