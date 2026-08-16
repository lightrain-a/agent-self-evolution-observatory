from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SCHEMA_VERSION = "1.0"

FINAL_REVIEW = "generated/asset-first-stri-narrow-final-review-20260816.json"
COHERENCE = "generated/asset-first-stri-narrow-paper-coherence-20260816.json"
SUBMISSION_QA = "generated/asset-first-stri-submission-qa-20260816.json"
REDUCTION = "generated/asset-first-skill-taxonomy-representation-invariance-reduction-20260816.json"
PAPER_DESIGN = "generated/asset-first-stri-narrow-paper-design-20260816.json"
CURRENT_SOURCE = "generated/asset-first-stri-current-source-review-20260816.json"

SOURCE_ARTIFACTS = {
    "final_review": FINAL_REVIEW,
    "coherence": COHERENCE,
    "submission_qa": SUBMISSION_QA,
    "reduction": REDUCTION,
    "paper_design": PAPER_DESIGN,
    "current_source_review": CURRENT_SOURCE,
}

POLICY = {
    "asset_first_track_is_separate_from_canonical_problem_gate": True,
    "asset_first_ready_cannot_mutate_canonical_generator_or_queue": True,
    "asset_first_ready_is_not_canonical_problem_gate_pass": True,
    "paper_ready_requires_final_review": True,
    "paper_ready_requires_claim_coherence": True,
    "paper_ready_requires_submission_qa": True,
    "paper_ready_requires_current_source_survival": True,
    "paper_ready_requires_superseding_reduction_state": True,
    "dynamic_p0_is_not_required_for_the_narrow_claim_scope": True,
    "dynamic_qualification_failure_is_not_positive_or_negative_narrow_evidence": True,
    "paper_ready_does_not_authorize_method_p0_or_gpu": True,
}

AUTHORITY = {
    "canonical_problem_gate": False,
    "canonical_generator": False,
    "canonical_queue": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sha(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def build_asset_first_stri_public_status(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    values = {key: _load(project_root / rel) for key, rel in SOURCE_ARTIFACTS.items()}
    final = values["final_review"]
    coherence = values["coherence"]
    qa = values["submission_qa"]
    reduction = values["reduction"]
    design = values["paper_design"]
    current = values["current_source_review"]

    claims = coherence.get("claims") if isinstance(coherence.get("claims"), dict) else {}
    claim_ids = ("N1", "N2", "N3")
    supported = [claim_id for claim_id in claim_ids if (claims.get(claim_id) or {}).get("status") == "SUPPORTED"]
    qa_passed = int(qa.get("checks_passed") or 0)
    qa_total = int(qa.get("checks_total") or 0)

    gates = {
        "final_review": final.get("verdict") == "READY_NARROW_ICLR",
        "claim_coherence": coherence.get("status") == "READY_NARROW_ICLR_CLAIMS_COHERENT" and len(supported) == len(claim_ids),
        "submission_qa": qa.get("status") == "PASS" and qa_total > 0 and qa_passed == qa_total,
        "current_source": current.get("verdict") == "SURVIVES_NARROWLY",
        "superseding_reduction": reduction.get("status") == "NARROW_PAPER_READY_AFTER_DYNAMIC_QUALIFICATION_HOLD",
        "paper_design": str(design.get("submission_readiness") or "").startswith("READY_NARROW_ICLR"),
    }
    ready = all(gates.values())
    artifacts = {
        key: {"path": rel, "sha256": _sha(project_root / rel), "present": bool(values[key])}
        for key, rel in SOURCE_ARTIFACTS.items()
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "paper_id": "STRI",
        "candidate_id": "skill-taxonomy-representation-invariance",
        "title": str(coherence.get("title") or design.get("recommended_title") or "Skill-Taxonomy Representation Invariance"),
        "status": "READY_NARROW_ICLR" if ready else "HOLD_ASSET_FIRST_PAPER_NOT_READY",
        "track": "ASSET_FIRST_PAPER_READY",
        "gates": gates,
        "claims": {
            claim_id: {
                "status": str((claims.get(claim_id) or {}).get("status") or "UNKNOWN"),
                "object": str((claims.get(claim_id) or {}).get("object") or ""),
                "forbidden": str((claims.get(claim_id) or {}).get("forbidden") or ""),
            }
            for claim_id in claim_ids
        },
        "summary": {
            "paper_ready": 1 if ready else 0,
            "claims_supported": len(supported),
            "claims_total": len(claim_ids),
            "qa_checks_passed": qa_passed,
            "qa_checks_total": qa_total,
            "final_review_confidence": float(final.get("confidence") or 0.0),
            "canonical_problem_gate_pass_added": 0,
            "canonical_generator_candidates_added": 0,
            "canonical_queue_candidates_added": 0,
            "method_authorized": 0,
            "experiment_authorized": 0,
            "p0_authorized": 0,
            "gpu_authorized": 0,
        },
        "claim_boundary": {
            "dynamic_p0": "qualification failure is disclosed and excluded from narrow scientific evidence",
            "downstream_utility": "not claimed or required for the frozen narrow submission scope",
            "solver_novelty": "STRI-Cert is not claimed as a computationally novel LP solver",
            "repair_method": "no claim that Support-Quotient Control has been empirically validated",
        },
        "source_artifacts": artifacts,
        "policy": dict(POLICY),
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }


def validate_asset_first_stri_public_status(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    authority = state.get("authority") or {}
    gates = state.get("gates") or {}

    if state.get("scientific_authority") is not False:
        errors.append("asset-first paper-ready projection must have zero scientific authority")
    for key, expected in POLICY.items():
        if policy.get(key) is not expected:
            errors.append(f"asset-first policy mismatch:{key}")
    if any(authority.get(key) is not False for key in AUTHORITY):
        errors.append("asset-first paper-ready projection cannot authorize canonical or execution state")
    if any(int(summary.get(key) or 0) != 0 for key in (
        "canonical_problem_gate_pass_added",
        "canonical_generator_candidates_added",
        "canonical_queue_candidates_added",
        "method_authorized",
        "experiment_authorized",
        "p0_authorized",
        "gpu_authorized",
    )):
        errors.append("asset-first paper-ready projection leaked canonical/execution authority")

    ready = state.get("status") == "READY_NARROW_ICLR"
    if ready:
        if not all(gates.get(key) is True for key in (
            "final_review", "claim_coherence", "submission_qa", "current_source", "superseding_reduction", "paper_design"
        )):
            errors.append("READY_NARROW_ICLR requires every cross-validated paper-ready gate")
        if int(summary.get("paper_ready") or 0) != 1:
            errors.append("READY_NARROW_ICLR must expose paper_ready=1")
        if (int(summary.get("claims_supported") or 0), int(summary.get("claims_total") or 0)) != (3, 3):
            errors.append("READY_NARROW_ICLR requires N1/N2/N3 supported")
        if int(summary.get("qa_checks_total") or 0) <= 0 or int(summary.get("qa_checks_passed") or 0) != int(summary.get("qa_checks_total") or 0):
            errors.append("READY_NARROW_ICLR requires complete submission QA")
        for key, row in (state.get("source_artifacts") or {}).items():
            if row.get("present") is not True or len(str(row.get("sha256") or "")) != 64:
                errors.append(f"READY_NARROW_ICLR source artifact missing/digest invalid:{key}")
    elif int(summary.get("paper_ready") or 0) != 0:
        errors.append("non-ready asset-first state must expose paper_ready=0")
    return sorted(set(errors))
