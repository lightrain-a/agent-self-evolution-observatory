from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .human_submission_signoff import verify_current_signoff
from .presubmission_freeze import validate_freeze, verify_current_frozen_artifacts
from .submission_handoff import validate_handoff_ledger
from .venue_form_consistency import verify_current_venue_form_audit

RECEIPT_SCHEMA_VERSION = "1.1"
RECEIPT_STATUS = "VENUE_SUBMISSION_CONFIRMED"


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _latest(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, Mapping) and event.get("event_type") == event_type:
            return dict(event)
    return {}


def _receipt(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    event = _latest(row, event_type)
    receipt = event.get("receipt") or {}
    return dict(receipt) if isinstance(receipt, Mapping) else {}


def submission_receipt_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    identity = {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "human_signoff_sha256": receipt.get("human_signoff_sha256"),
        "handoff_sha256": receipt.get("handoff_sha256"),
        "freeze_sha256": receipt.get("freeze_sha256"),
        "venue": receipt.get("venue"),
        "venue_submission_id": receipt.get("venue_submission_id"),
        "venue_forum_ref": receipt.get("venue_forum_ref"),
        "uploaded_artifact_sha256": receipt.get("uploaded_artifact_sha256") or {},
        "submitted_at": receipt.get("submitted_at"),
        "external_human_submission_authority_ref": receipt.get("external_human_submission_authority_ref"),
        "status": receipt.get("status"),
        "actual_submission_status": receipt.get("actual_submission_status"),
    }
    if str(receipt.get("schema_version") or "1.0") != "1.0":
        identity["venue_form_audit_sha256"] = receipt.get("venue_form_audit_sha256")
    return identity


def build_submission_receipt(
    *,
    paper_ledger: Mapping[str, Any],
    freeze_ledger: Mapping[str, Any],
    handoff_ledger: Mapping[str, Any],
    signoff_ledger: Mapping[str, Any],
    venue_form_audit_ledger: Mapping[str, Any],
    venue_submission_id: str,
    venue_forum_ref: str,
    uploaded_artifact_sha256: Mapping[str, str],
    submitted_at: str,
    external_human_submission_authority_ref: str,
) -> dict[str, Any]:
    paper_id = str(paper_ledger.get("paper_id") or "")
    if not paper_id:
        raise RuntimeError("paper id missing")
    if paper_ledger.get("current_state") != "SUBMISSION_READY":
        raise RuntimeError("paper must still be SUBMISSION_READY before recording actual submission")
    freeze_errors = validate_freeze(freeze_ledger)
    if freeze_errors:
        raise RuntimeError(f"freeze ledger invalid: {freeze_errors}")
    drift = verify_current_frozen_artifacts(freeze_ledger)
    if drift:
        raise RuntimeError(f"frozen artifacts are stale: {drift}")
    handoff_errors = validate_handoff_ledger(handoff_ledger)
    if handoff_errors:
        raise RuntimeError(f"handoff ledger invalid: {handoff_errors}")
    venue_form_errors = verify_current_venue_form_audit(venue_form_audit_ledger, handoff_ledger, freeze_ledger)
    if venue_form_errors:
        raise RuntimeError(f"venue form audit is missing, failed, or stale: {venue_form_errors}")
    signoff_errors = verify_current_signoff(signoff_ledger, handoff_ledger, freeze_ledger, venue_form_audit_ledger)
    if signoff_errors:
        raise RuntimeError(f"human signoff is missing or stale: {signoff_errors}")
    freeze = _receipt(freeze_ledger, "pre-submission-freeze")
    handoff = _receipt(handoff_ledger, "machine-submission-handoff")
    signoff = _receipt(signoff_ledger, "human-submission-signoff")
    venue_form = _receipt(venue_form_audit_ledger, "venue-form-consistency-audit")
    if str(signoff.get("schema_version") or "1.0") == "1.0":
        raise RuntimeError("actual submission requires v1.1 human signoff bound to a PASS venue-form audit")
    if str(freeze_ledger.get("paper_id") or "") != paper_id or str(handoff_ledger.get("paper_id") or "") != paper_id or str(signoff_ledger.get("paper_id") or "") != paper_id or str(venue_form_audit_ledger.get("paper_id") or "") != paper_id:
        raise RuntimeError("submission lineage paper id mismatch")
    expected = {str(item.get("label") or ""): str(item.get("sha256") or "") for item in freeze.get("frozen_artifacts") or [] if isinstance(item, Mapping)}
    uploaded = {str(k): str(v) for k, v in uploaded_artifact_sha256.items()}
    if not expected or uploaded != expected:
        raise RuntimeError(f"uploaded artifact hashes do not exactly match current freeze: expected={expected}, uploaded={uploaded}")
    if not str(venue_submission_id or "").strip():
        raise RuntimeError("venue submission id required")
    if not str(venue_forum_ref or "").strip():
        raise RuntimeError("venue forum/reference required")
    if not str(submitted_at or "").strip():
        raise RuntimeError("submission time required")
    if not str(external_human_submission_authority_ref or "").strip():
        raise RuntimeError("external human submission authority reference required")
    receipt: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "receipt_type": "actual-venue-submission",
        "paper_id": paper_id,
        "contract_sha256": str(paper_ledger.get("contract_sha256") or ""),
        "human_signoff_sha256": str(signoff.get("signoff_sha256") or ""),
        "handoff_sha256": str(handoff.get("handoff_sha256") or ""),
        "freeze_sha256": str(freeze.get("freeze_sha256") or ""),
        "venue_form_audit_sha256": str(venue_form.get("venue_form_audit_sha256") or ""),
        "venue": str(handoff.get("venue") or ""),
        "venue_submission_id": str(venue_submission_id).strip(),
        "venue_forum_ref": str(venue_forum_ref).strip(),
        "uploaded_artifact_sha256": uploaded,
        "submitted_at": str(submitted_at).strip(),
        "external_human_submission_authority_ref": str(external_human_submission_authority_ref).strip(),
        "status": RECEIPT_STATUS,
        "actual_submission_status": "SUBMITTED",
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["submission_receipt_sha256"] = _digest(submission_receipt_identity(receipt))
    return receipt


def validate_submission_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "actual-venue-submission" or receipt.get("status") != RECEIPT_STATUS:
        return False
    if str(receipt.get("schema_version") or "1.0") not in {"1.0", RECEIPT_SCHEMA_VERSION}:
        return False
    if str(receipt.get("schema_version") or "1.0") != "1.0" and not str(receipt.get("venue_form_audit_sha256") or ""):
        return False
    if receipt.get("actual_submission_status") != "SUBMITTED":
        return False
    if not receipt.get("external_human_submission_authority_ref") or not receipt.get("venue_submission_id") or not receipt.get("venue_forum_ref"):
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("submission_receipt_sha256") or "") == _digest(submission_receipt_identity(receipt))


def external_transition_authority_ref(receipt: Mapping[str, Any]) -> str:
    if not validate_submission_receipt(receipt):
        raise RuntimeError("invalid actual submission receipt")
    return "submission-receipt:" + str(receipt.get("submission_receipt_sha256") or "")
