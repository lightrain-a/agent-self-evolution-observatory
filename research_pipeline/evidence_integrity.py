from __future__ import annotations

from typing import Any


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "every_publishable_claim_requires_evidence_chain": True,
    "claim_type_determines_required_artifact": True,
    "numeric_claim_requires_evaluator_artifact": True,
    "citation_claim_requires_primary_source_anchor": True,
    "method_claim_requires_code_or_spec_alignment": True,
    "protocol_claim_requires_frozen_config_or_plan": True,
    "status_claim_requires_decision_ledger_or_authority_artifact": True,
    "verifier_identity_and_version_must_be_recorded": True,
    "uncalibrated_verifier_cannot_be_treated_as_ground_truth": True,
    "publication_authority_requires_zero_unresolved_high_risk_chain_gaps": True,
}

CLAIM_TYPES: dict[str, dict[str, Any]] = {
    "numeric-result": {
        "required_artifacts": ["evaluator-log", "metric-table", "run-provenance"],
        "audit": "recompute or match the reported value against the frozen evaluator artifact",
    },
    "citation": {
        "required_artifacts": ["primary-source", "passage-anchor", "bibliographic-identity"],
        "audit": "verify that the cited passage supports the exact claim and that the paper identity is correct",
    },
    "method-description": {
        "required_artifacts": ["implementation", "method-spec", "config"],
        "audit": "check method-code/spec alignment rather than prose similarity",
    },
    "protocol": {
        "required_artifacts": ["frozen-config", "plan-hash", "split-definition"],
        "audit": "verify that reported protocol matches the executed protocol",
    },
    "scientific-status": {
        "required_artifacts": ["decision-ledger", "authority-artifact", "evidence-summary"],
        "audit": "verify that PASS/HOLD/STOP wording matches current scientific authority",
    },
}

VERIFIER_CONTRACT: dict[str, Any] = {
    "required_fields": [
        "verifier_id",
        "verifier_version",
        "task",
        "gold_anchor_id",
        "calibration_split",
        "decision_threshold",
        "measured_recall_supported",
        "measured_recall_unsupported",
    ],
    "status": "spec-ready-not-yet-calibrated",
    "rule": "A model/judge verdict is an instrument reading, not ground truth. Calibrate the instrument against human or deterministic gold before using its flags as a publication gate.",
}

REFERENCES = [
    {"system": "ScientistOne", "adopted": "Chain-of-Evidence and CoE Audit: score verification, specification violation, reference verification, and method-code alignment"},
    {"system": "PaperQA2", "adopted": "retrieval + evidence gathering + cited synthesis with literature-specific evaluation"},
    {"system": "Citation-faithfulness verifier calibration", "adopted": "name and calibrate the verifier; do not compare unsupported-citation rates across unnamed verifier protocols"},
]


def audit_claim_chain(claim: dict[str, Any]) -> dict[str, Any]:
    claim_type = str(claim.get("claim_type") or "")
    spec = CLAIM_TYPES.get(claim_type)
    if not spec:
        return {"passed": False, "status": "unknown-claim-type", "blockers": ["claim-type-unregistered"]}
    artifacts = {str(item) for item in claim.get("artifact_kinds") or []}
    required = set(spec["required_artifacts"])
    missing = sorted(required - artifacts)
    blockers = [f"missing-artifact:{item}" for item in missing]
    if not str(claim.get("claim_text") or "").strip():
        blockers.append("claim-text-missing")
    return {
        "passed": not blockers,
        "status": "pass" if not blockers else "repair-required",
        "claim_type": claim_type,
        "required_artifacts": sorted(required),
        "blockers": blockers,
        "audit_rule": spec["audit"],
    }


def build_evidence_integrity_state() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "claim_types": CLAIM_TYPES,
        "verifier_contract": VERIFIER_CONTRACT,
        "references": REFERENCES,
        "summary": {
            "claim_types": len(CLAIM_TYPES),
            "verifier_calibration_status": VERIFIER_CONTRACT["status"],
            "publication_gate_active": True,
            "claims_scored": 0,
        },
    }
