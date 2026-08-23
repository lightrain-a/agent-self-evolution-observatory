from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from .presubmission_freeze import validate_freeze, verify_current_frozen_artifacts
from .submission_handoff import validate_handoff_ledger, validate_handoff_receipt
from .venue_form_consistency import validate_venue_form_audit_ledger, verify_current_venue_form_audit

SIGNOFF_SCHEMA_VERSION = "1.1"
SIGNOFF_STATUS = "HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING"
AUTHORITY = {"scientific": False, "experiment": False, "gpu": False, "submission": False}

KNOWN_CHECK_IDS = {
    "confirm complete author list and OpenReview profiles": "AUTHOR_LIST_AND_OPENREVIEW_PROFILES",
    "confirm author quota and reciprocal-reviewing obligations": "AUTHOR_QUOTA_AND_RECIPROCAL_REVIEWING",
    "confirm dual-submission compliance": "DUAL_SUBMISSION_COMPLIANCE",
    "acknowledge ICLR Code of Ethics": "ETHICS_ACKNOWLEDGEMENT",
    "review and approve mandatory AI-use disclosure": "AI_USE_DISCLOSURE_APPROVAL",
    "verify final PDF/source/supplement hashes immediately before upload": "FINAL_UPLOAD_HASH_CHECK",
    "confirm title and abstract used for reviewer bidding are the intended final submission metadata": "TITLE_ABSTRACT_METADATA_APPROVAL",
    "confirm every author accepts responsibility for the final manuscript and AI-assisted artifacts": "AUTHOR_RESPONSIBILITY_ACKNOWLEDGEMENT",
    "capture final OpenReview form snapshot and pass venue-form consistency audit": "VENUE_FORM_CONSISTENCY_AUDIT",
    "recompute and compare every frozen artifact SHA256 immediately before upload": "FINAL_HASH_RECOMPUTE",
}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _latest(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, Mapping) and event.get("event_type") == event_type:
            return dict(event)
    return {}


def _handoff_receipt(handoff_ledger: Mapping[str, Any]) -> dict[str, Any]:
    event = _latest(handoff_ledger, "machine-submission-handoff")
    receipt = event.get("receipt") or {}
    return dict(receipt) if isinstance(receipt, Mapping) else {}


def _freeze_receipt(freeze_ledger: Mapping[str, Any]) -> dict[str, Any]:
    event = _latest(freeze_ledger, "pre-submission-freeze")
    receipt = event.get("receipt") or {}
    return dict(receipt) if isinstance(receipt, Mapping) else {}


def checklist_items(handoff_receipt: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    used: set[str] = set()
    for raw in handoff_receipt.get("human_checklist") or []:
        text = str(raw).strip()
        if not text:
            continue
        check_id = KNOWN_CHECK_IDS.get(text) or f"CHECK_{_digest(text)[:12].upper()}"
        if check_id in used:
            continue
        used.add(check_id)
        rows.append({"check_id": check_id, "text": text})
    return rows


def build_signoff_template(handoff_ledger: Mapping[str, Any], venue_form_audit_ledger: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = validate_handoff_ledger(handoff_ledger)
    if errors:
        raise RuntimeError(f"handoff ledger invalid: {errors}")
    handoff = _handoff_receipt(handoff_ledger)
    if not handoff or not validate_handoff_receipt(handoff):
        raise RuntimeError("current handoff receipt invalid")
    venue_form_status = "PENDING_FORM_SNAPSHOT_AND_AUDIT"
    if venue_form_audit_ledger is not None:
        audit_errors = validate_venue_form_audit_ledger(venue_form_audit_ledger)
        audit_event = _latest(venue_form_audit_ledger, "venue-form-consistency-audit")
        audit_receipt = audit_event.get("receipt") if isinstance(audit_event.get("receipt"), Mapping) else {}
        if (
            not audit_errors
            and audit_receipt.get("pass") is True
            and audit_receipt.get("handoff_sha256") == handoff.get("handoff_sha256")
            and audit_receipt.get("freeze_sha256") == handoff.get("freeze_sha256")
        ):
            venue_form_status = "PASS_BOUND_TO_CURRENT_HANDOFF"
        else:
            venue_form_status = "AUDIT_PRESENT_NOT_CURRENT_OR_NOT_PASS"
    template = {
        "schema_version": SIGNOFF_SCHEMA_VERSION,
        "paper_id": str(handoff.get("paper_id") or ""),
        "handoff_sha256": str(handoff.get("handoff_sha256") or ""),
        "freeze_sha256": str(handoff.get("freeze_sha256") or ""),
        "status": "PENDING_HUMAN_CONFIRMATION",
        "required_confirmations": checklist_items(handoff),
        "required_explicit_inputs": [
            "external_human_confirmation_ref",
            "confirmed_at",
            "venue_form_audit_sha256 from a current PASS venue-form audit",
            "all required confirmation IDs",
            "acknowledge_current_artifact_hashes=true",
            "acknowledge_actual_submission_not_performed=true",
        ],
        "venue_form_audit_status": venue_form_status,
        "submission_authority": False,
    }
    template["template_sha256"] = _digest(template)
    return template


def signoff_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    identity = {
        "paper_id": receipt.get("paper_id"),
        "handoff_sha256": receipt.get("handoff_sha256"),
        "freeze_sha256": receipt.get("freeze_sha256"),
        "confirmed_check_ids": receipt.get("confirmed_check_ids") or [],
        "external_human_confirmation_ref": receipt.get("external_human_confirmation_ref"),
        "confirmed_at": receipt.get("confirmed_at"),
        "acknowledge_current_artifact_hashes": receipt.get("acknowledge_current_artifact_hashes"),
        "acknowledge_actual_submission_not_performed": receipt.get("acknowledge_actual_submission_not_performed"),
        "status": receipt.get("status"),
    }
    if str(receipt.get("schema_version") or "1.0") != "1.0":
        identity["venue_form_audit_sha256"] = receipt.get("venue_form_audit_sha256")
    return identity


def build_signoff_receipt(
    *,
    handoff_ledger: Mapping[str, Any],
    freeze_ledger: Mapping[str, Any],
    venue_form_audit_ledger: Mapping[str, Any],
    confirmed_check_ids: Sequence[str],
    external_human_confirmation_ref: str,
    confirmed_at: str,
    acknowledge_current_artifact_hashes: bool,
    acknowledge_actual_submission_not_performed: bool,
) -> dict[str, Any]:
    handoff_errors = validate_handoff_ledger(handoff_ledger)
    if handoff_errors:
        raise RuntimeError(f"handoff ledger invalid: {handoff_errors}")
    freeze_errors = validate_freeze(freeze_ledger)
    if freeze_errors:
        raise RuntimeError(f"freeze ledger invalid: {freeze_errors}")
    artifact_errors = verify_current_frozen_artifacts(freeze_ledger)
    if artifact_errors:
        raise RuntimeError(f"frozen artifacts are stale: {artifact_errors}")
    venue_form_errors = verify_current_venue_form_audit(venue_form_audit_ledger, handoff_ledger, freeze_ledger)
    if venue_form_errors:
        raise RuntimeError(f"venue form audit is missing, failed, or stale: {venue_form_errors}")
    handoff = _handoff_receipt(handoff_ledger)
    freeze = _freeze_receipt(freeze_ledger)
    if not handoff or not validate_handoff_receipt(handoff):
        raise RuntimeError("current handoff receipt invalid")
    if str(handoff.get("freeze_sha256") or "") != str(freeze.get("freeze_sha256") or ""):
        raise RuntimeError("handoff is stale relative to current freeze")
    required = [row["check_id"] for row in checklist_items(handoff)]
    confirmed = list(dict.fromkeys(str(item).strip() for item in confirmed_check_ids if str(item).strip()))
    missing = [item for item in required if item not in confirmed]
    extra = [item for item in confirmed if item not in required]
    if missing:
        raise RuntimeError("missing human confirmations: " + ",".join(missing))
    if extra:
        raise RuntimeError("unknown human confirmations: " + ",".join(extra))
    if not str(external_human_confirmation_ref or "").strip():
        raise RuntimeError("external human confirmation reference required")
    if not str(confirmed_at or "").strip():
        raise RuntimeError("human confirmation timestamp required")
    if acknowledge_current_artifact_hashes is not True:
        raise RuntimeError("human must acknowledge current frozen artifact hashes")
    if acknowledge_actual_submission_not_performed is not True:
        raise RuntimeError("human must acknowledge that actual submission is a separate action")
    venue_form_event = _latest(venue_form_audit_ledger, "venue-form-consistency-audit")
    venue_form_receipt = venue_form_event.get("receipt") if isinstance(venue_form_event.get("receipt"), Mapping) else {}
    receipt: dict[str, Any] = {
        "schema_version": SIGNOFF_SCHEMA_VERSION,
        "receipt_type": "human-submission-signoff",
        "paper_id": str(handoff.get("paper_id") or ""),
        "handoff_sha256": str(handoff.get("handoff_sha256") or ""),
        "freeze_sha256": str(handoff.get("freeze_sha256") or ""),
        "venue_form_audit_sha256": str(venue_form_receipt.get("venue_form_audit_sha256") or ""),
        "confirmed_check_ids": required,
        "external_human_confirmation_ref": str(external_human_confirmation_ref).strip(),
        "confirmed_at": str(confirmed_at).strip(),
        "acknowledge_current_artifact_hashes": True,
        "acknowledge_actual_submission_not_performed": True,
        "status": SIGNOFF_STATUS,
        "actual_submission_status": "NOT_SUBMITTED",
        "external_human_submission_authority_required_for_actual_submit": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["signoff_sha256"] = _digest(signoff_identity(receipt))
    return receipt


def validate_signoff_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "human-submission-signoff" or receipt.get("status") != SIGNOFF_STATUS:
        return False
    if str(receipt.get("schema_version") or "1.0") not in {"1.0", SIGNOFF_SCHEMA_VERSION}:
        return False
    if str(receipt.get("schema_version") or "1.0") != "1.0" and not str(receipt.get("venue_form_audit_sha256") or ""):
        return False
    if receipt.get("actual_submission_status") != "NOT_SUBMITTED":
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("signoff_sha256") or "") == _digest(signoff_identity(receipt))


def append_signoff(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_signoff_receipt(receipt):
        raise RuntimeError("invalid human signoff receipt")
    paper_id = str(receipt.get("paper_id") or "")
    directory = Path(root) / "paper-human-signoffs"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{paper_id}.json"
    lock = directory / f".{paper_id}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "schema_version": SIGNOFF_SCHEMA_VERSION,
            "paper_id": paper_id,
            "events": [],
            "authority": dict(AUTHORITY),
        }
        prior = _latest(row, "human-submission-signoff")
        prior_receipt = prior.get("receipt") if isinstance(prior.get("receipt"), Mapping) else {}
        if prior_receipt.get("signoff_sha256") == receipt.get("signoff_sha256"):
            return row
        event = {
            "event_type": "human-submission-signoff",
            "receipt": dict(receipt),
            "recorded_at": str(receipt.get("confirmed_at") or ""),
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        event["event_id"] = _digest([paper_id, len(row.get("events") or []), event])[:24]
        row.setdefault("events", []).append(event)
        row["updated_at"] = event["recorded_at"]
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return row


def validate_signoff_ledger(row: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if (row.get("authority") or {}) != AUTHORITY:
        errors.append("human signoff ledger must not grant submission authority")
    for event in row.get("events") or []:
        if not isinstance(event, Mapping) or event.get("event_type") != "human-submission-signoff":
            errors.append("unknown human signoff event")
            continue
        receipt = event.get("receipt") or {}
        if not isinstance(receipt, Mapping) or not validate_signoff_receipt(receipt):
            errors.append("invalid human signoff receipt")
    return list(dict.fromkeys(errors))


def verify_current_signoff(signoff_ledger: Mapping[str, Any], handoff_ledger: Mapping[str, Any], freeze_ledger: Mapping[str, Any], venue_form_audit_ledger: Mapping[str, Any] | None = None) -> list[str]:
    errors = list(validate_signoff_ledger(signoff_ledger))
    latest_signoff = _latest(signoff_ledger, "human-submission-signoff")
    signoff = latest_signoff.get("receipt") if isinstance(latest_signoff.get("receipt"), Mapping) else {}
    handoff = _handoff_receipt(handoff_ledger)
    freeze = _freeze_receipt(freeze_ledger)
    if not signoff:
        errors.append("human-signoff-receipt-missing")
        return list(dict.fromkeys(errors))
    if signoff.get("handoff_sha256") != handoff.get("handoff_sha256"):
        errors.append("human-signoff-handoff-stale")
    if signoff.get("freeze_sha256") != freeze.get("freeze_sha256"):
        errors.append("human-signoff-freeze-stale")
    if str(signoff.get("schema_version") or "1.0") != "1.0":
        if venue_form_audit_ledger is None:
            errors.append("human-signoff-venue-form-audit-ledger-missing")
        else:
            venue_errors = verify_current_venue_form_audit(venue_form_audit_ledger, handoff_ledger, freeze_ledger)
            errors.extend(venue_errors)
            venue_event = _latest(venue_form_audit_ledger, "venue-form-consistency-audit")
            venue_receipt = venue_event.get("receipt") if isinstance(venue_event.get("receipt"), Mapping) else {}
            if signoff.get("venue_form_audit_sha256") != venue_receipt.get("venue_form_audit_sha256"):
                errors.append("human-signoff-venue-form-audit-stale")
    errors.extend(verify_current_frozen_artifacts(freeze_ledger))
    return list(dict.fromkeys(errors))
