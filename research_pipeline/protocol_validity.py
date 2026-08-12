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

POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "required_before_experiment_execution": True,
    "is_formal_experiment_gate": False,
    "invalid_protocol_cannot_update_scientific_belief": True,
    "evaluation_shortcut_cannot_count_as_capability": True,
    "protocol_change_invalidates_previous_execution_authority": True,
    "benchmark_or_evaluator_false_negative_must_be_separated_from_method_failure": True,
}

REFERENCES = [
    {"system": "ResearchClawBench", "adopted": "treat experimental-protocol mismatch, evidence mismatch, and missing scientific core as distinct end-to-end research failures"},
    {"system": "HackDetect", "adopted": "audit exposure, agent use of the exposure, and score inflation before treating benchmark performance as intended capability"},
    {"system": "ScienceAgentBench verified split", "adopted": "evaluation artifacts themselves can create false negatives and require versioned verification"},
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

    blockers: list[str] = []
    checks: list[dict[str, Any]] = []
    for key in REQUIRED_CHECKS:
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
        "policy": POLICY,
        "references": REFERENCES,
    }
