from __future__ import annotations

from typing import Any


REQUIRED_CHECKS = (
    "hidden_evaluation_sealed",
    "evaluation_artifacts_inaccessible",
    "independent_truth_source",
    "same_information_baselines",
    "claim_metric_alignment",
    "versioned_evaluator",
    "shortcut_audit",
)

PERSISTENT_UPDATE_REQUIRED_CHECKS = (
    "post_update_effect_realization",
)

POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "required_before_experiment_execution": True,
    "is_formal_experiment_gate": False,
    "invalid_protocol_cannot_update_scientific_belief": True,
    "evaluation_shortcut_cannot_count_as_capability": True,
    "protocol_change_invalidates_previous_execution_authority": True,
    "benchmark_or_evaluator_false_negative_must_be_separated_from_method_failure": True,
    "future_persistent_updates_require_post_update_decision_context_support": True,
    "future_persistent_updates_require_intended_effect_realization": True,
    "observation_recurrence_is_insufficient_for_full_policy_context_recurrence": True,
    "effect_realization_failure_updates_protocol_or_operationalization_before_core_principle": True,
    "legacy_contracts_are_not_retroactively_failed_by_new_effect_realization_rule": True,
}

REFERENCES = [
    {"system": "ResearchClawBench", "adopted": "treat experimental-protocol mismatch, evidence mismatch, and missing scientific core as distinct end-to-end research failures"},
    {"system": "HackDetect", "adopted": "audit exposure, agent use of the exposure, and score inflation before treating benchmark performance as intended capability"},
    {"system": "ScienceAgentBench verified split", "adopted": "evaluation artifacts themselves can create false negatives and require versioned verification"},
    {"system": "DAgger", "adopted": "sequential policies must be assessed under the observation distribution they induce rather than only the pre-update data distribution"},
    {"system": "HERO / ReOPD", "adopted": "multi-turn supervision quality depends on alignment with the learner's current decision context and on-policy prefix distribution"},
    {"system": "SkillEvolver", "adopted": "a persistent skill may be content-valid yet silently bypassed at runtime, so deployment-time invocation is a separate validity condition"},
]


def audit_protocol_validity(config: dict[str, Any]) -> dict[str, Any]:
    contract = (config.get("pre_experiment") or {}).get("protocol_validity") or {}
    if not isinstance(contract, dict) or not contract:
        return {
            "required": True,
            "is_formal_gate": False,
            "passed": False,
            "status": "missing-contract",
            "blockers": ["protocol-validity-contract-missing"],
            "policy": POLICY,
        }

    applies_to_persistent_update = contract.get("applies_to_persistent_update") is True
    required_checks = list(REQUIRED_CHECKS)
    if applies_to_persistent_update:
        required_checks.extend(PERSISTENT_UPDATE_REQUIRED_CHECKS)

    blockers: list[str] = []
    checks: list[dict[str, Any]] = []
    for key in required_checks:
        row = contract.get(key)
        if not isinstance(row, dict):
            blockers.append(f"protocol-check-missing:{key}")
            checks.append({"key": key, "pass": False, "evidence": ""})
            continue
        passed = row.get("passed") is True
        evidence = str(row.get("evidence") or "").strip()
        if not passed:
            blockers.append(f"protocol-check-failed:{key}")
        if not evidence:
            blockers.append(f"protocol-evidence-missing:{key}")
        checks.append({"key": key, "pass": passed and bool(evidence), "evidence": evidence})

    passed = not blockers
    return {
        "required": True,
        "is_formal_gate": False,
        "passed": passed,
        "status": "pass" if passed else "repair-required",
        "blockers": sorted(set(blockers)),
        "checks": checks,
        "applies_to_persistent_update": applies_to_persistent_update,
        "required_checks": required_checks,
        "policy": POLICY,
        "references": REFERENCES,
    }
