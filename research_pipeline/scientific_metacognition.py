from __future__ import annotations

from typing import Any

from .research_execution_kernel import SCHEMA_VERSION, canonical_sha256

FAILURE_FAMILIES: dict[str, dict[str, Any]] = {
    "INFRASTRUCTURE": {"scientific_belief_update_allowed": False, "core_stop_allowed": False},
    "PROTOCOL": {"scientific_belief_update_allowed": False, "core_stop_allowed": False},
    "IDENTIFIABILITY": {"scientific_belief_update_allowed": False, "core_stop_allowed": False},
    "OPTIMIZATION": {"scientific_belief_update_allowed": False, "core_stop_allowed": False},
    "METHOD_REALIZATION": {"scientific_belief_update_allowed": True, "core_stop_allowed": False},
    "SCIENTIFIC_NEGATIVE": {"scientific_belief_update_allowed": True, "core_stop_allowed": False},
    "SCIENTIFIC_POSITIVE": {"scientific_belief_update_allowed": True, "core_stop_allowed": False},
    "MANUAL_REVIEW": {"scientific_belief_update_allowed": False, "core_stop_allowed": False},
}

DIAGNOSIS_TO_FAILURE_FAMILY = {
    "infrastructure-error": "INFRASTRUCTURE", "budget-plan-mismatch": "PROTOCOL",
    "substrate-degenerate": "IDENTIFIABILITY", "no-label-variation": "IDENTIFIABILITY",
    "underfit": "OPTIMIZATION", "representation-signal-mismatch": "METHOD_REALIZATION",
    "objective-claim-mismatch": "PROTOCOL", "decision-context-support-mismatch": "PROTOCOL",
    "authority-provenance-mismatch": "PROTOCOL", "matched-simplification-tie": "SCIENTIFIC_NEGATIVE",
    "true-negative": "SCIENTIFIC_NEGATIVE", "positive-signal": "SCIENTIFIC_POSITIVE",
}


def evaluate_metacognition(expected: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    mismatches: list[str] = []
    for key in ("scientific_object", "hypothesis", "primary_metric", "protocol_sha256"):
        value = expected.get(key)
        if value not in (None, "") and observed.get(key) != value: mismatches.append(f"intent-output-mismatch:{key}")
    validated = {str(v) for v in observed.get("validated_evidence_refs") or []}
    claim_refs = {str(v) for v in observed.get("claim_evidence_refs") or []}
    unsupported_refs = sorted(claim_refs - validated)
    if unsupported_refs: mismatches.append("claim-cites-unvalidated-evidence:" + ",".join(unsupported_refs))
    unsupported = [str(v) for v in observed.get("unsupported_inferences") or [] if str(v)]
    deviations = [str(v) for v in observed.get("protocol_deviations") or [] if str(v)]
    if unsupported: mismatches.append("unsupported-inference-present")
    if deviations: mismatches.append("protocol-deviation-present")
    receipt = {
        "schema_version": SCHEMA_VERSION, "status": "PASS" if not mismatches else "REVISE", "mismatches": mismatches,
        "unsupported_evidence_refs": unsupported_refs, "unsupported_inferences": unsupported,
        "protocol_deviations": deviations,
        "alternative_explanations_considered": [str(v) for v in observed.get("alternative_explanations") or [] if str(v)],
        "transition_allowed": not mismatches, "scientific_authority": False, "experiment_authority": False,
    }
    receipt["receipt_sha256"] = canonical_sha256(receipt); return receipt


def classify_failure(diagnosis: str) -> dict[str, Any]:
    family = DIAGNOSIS_TO_FAILURE_FAMILY.get(str(diagnosis), "MANUAL_REVIEW")
    return {"diagnosis": str(diagnosis), "family": family, **FAILURE_FAMILIES[family],
            "persistent_dead_end_authority": False, "scientific_authority": False}


def validate_failure_interpretation(diagnosis: str, proposed_family: str, *, proposed_core_stop: bool = False) -> dict[str, Any]:
    canonical = classify_failure(diagnosis); blockers: list[str] = []
    if str(proposed_family) != canonical["family"]: blockers.append(f"failure-family-mismatch:{canonical['family']}")
    if proposed_core_stop: blockers.append("execution-kernel-never-authorizes-core-principle-stop")
    return {"status": "PASS" if not blockers else "BLOCK", "passed": not blockers,
            "blockers": blockers, "canonical": canonical, "scientific_authority": False}


def build_failure_taxonomy_state() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "families": FAILURE_FAMILIES,
            "diagnosis_mapping": DIAGNOSIS_TO_FAILURE_FAMILY,
            "policy": {"support_or_infrastructure_failure_is_not_scientific_negative": True,
                       "execution_kernel_never_certifies_persistent_dead_end": True,
                       "core_principle_stop_requires_existing_principle_adjudicator": True},
            "summary": {"families": len(FAILURE_FAMILIES), "typed_diagnoses": len(DIAGNOSIS_TO_FAILURE_FAMILY)},
            "scientific_authority": False}
