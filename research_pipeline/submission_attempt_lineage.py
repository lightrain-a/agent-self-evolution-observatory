from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .paper_acceptance_ledger import validate_paper_ledger
from .post_decision_learning import validate_learning_receipt, validate_venue_decision_receipt
from .venue_submission_receipt import validate_submission_receipt

SCHEMA_VERSION = "1.0"
ATTEMPT_TYPES = {"RESUBMISSION", "CAMERA_READY"}
RESUBMISSION_PARENT_DECISIONS = {"REJECT", "WITHDRAWN", "VENUE_CLOSED_WITHOUT_DECISION"}
REVISION_CATEGORIES = {
    "WRITING",
    "PAPER_POSITIONING",
    "CITATION",
    "LAYOUT",
    "VISUAL_PRESENTATION",
    "EVIDENCE_PRESENTATION",
    "REPRODUCTION_PACKAGING",
    "VENUE_METADATA",
    "AUTHOR_METADATA",
    "ACKNOWLEDGEMENTS",
    "CAMERA_READY_FORMATTING",
    "SCIENTIFIC_EVIDENCE",
    "EXPERIMENT",
    "CLAIM",
    "SCIENTIFIC_INTERPRETATION",
}
SCIENTIFIC_REVISION_CATEGORIES = {"SCIENTIFIC_EVIDENCE", "EXPERIMENT", "CLAIM", "SCIENTIFIC_INTERPRETATION"}
ZERO_AUTHORITY = {"scientific": False, "experiment": False, "gpu": False, "submission": False}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:140] or "unknown-paper"


def _latest_receipt(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, Mapping) and event.get("event_type") == event_type:
            receipt = event.get("receipt") or {}
            return dict(receipt) if isinstance(receipt, Mapping) else {}
    return {}


def attempt_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "attempt_type": receipt.get("attempt_type"),
        "target_venue": receipt.get("target_venue"),
        "parent_submission_receipt_sha256": receipt.get("parent_submission_receipt_sha256"),
        "parent_venue_decision_sha256": receipt.get("parent_venue_decision_sha256"),
        "parent_learning_receipt_sha256": receipt.get("parent_learning_receipt_sha256"),
        "parent_attempt_sha256": receipt.get("parent_attempt_sha256"),
        "revision_categories": receipt.get("revision_categories") or [],
        "scientific_contract_unchanged": receipt.get("scientific_contract_unchanged"),
        "new_claim_requested": receipt.get("new_claim_requested"),
        "new_experiment_requested": receipt.get("new_experiment_requested"),
        "new_scientific_evidence_requested": receipt.get("new_scientific_evidence_requested"),
        "scientific_interpretation_change_requested": receipt.get("scientific_interpretation_change_requested"),
        "status": receipt.get("status"),
        "machine_preparation_eligible": receipt.get("machine_preparation_eligible"),
        "requires_explicit_scientific_reopen": receipt.get("requires_explicit_scientific_reopen"),
        "parent_submission_bytes_immutable": receipt.get("parent_submission_bytes_immutable"),
        "scientific_claim_status_unchanged": receipt.get("scientific_claim_status_unchanged"),
    }


def _lineage_receipts(paper_ledger: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    submission = _latest_receipt(paper_ledger, "actual-submission")
    decision = _latest_receipt(paper_ledger, "venue-decision")
    learning = _latest_receipt(paper_ledger, "post-decision-learning")
    return submission, decision, learning


def build_attempt_plan(
    *,
    paper_ledger: Mapping[str, Any],
    target_venue: str,
    attempt_type: str,
    revision_categories: Sequence[str],
    scientific_contract_unchanged: bool,
    new_claim_requested: bool = False,
    new_experiment_requested: bool = False,
    new_scientific_evidence_requested: bool = False,
    scientific_interpretation_change_requested: bool = False,
    parent_attempt: Mapping[str, Any] | None = None,
    parent_attempt_workflow: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    paper_id = str(paper_ledger.get("paper_id") or "")
    contract_sha = str(paper_ledger.get("contract_sha256") or "")
    if not paper_id or not contract_sha:
        raise RuntimeError("paper identity missing")
    if str(paper_ledger.get("current_state") or "") != "LEARN":
        raise RuntimeError("new submission attempt may only branch from LEARN")
    ledger_errors = validate_paper_ledger(paper_ledger)
    if ledger_errors:
        raise RuntimeError(f"parent paper ledger invalid: {ledger_errors}")

    attempt_type = str(attempt_type or "").strip().upper()
    if attempt_type not in ATTEMPT_TYPES:
        raise RuntimeError(f"unsupported attempt type: {attempt_type}")
    target_venue = str(target_venue or "").strip()
    if not target_venue:
        raise RuntimeError("target venue required")
    categories = sorted({str(value or "").strip().upper() for value in revision_categories if str(value or "").strip()})
    if not categories:
        raise RuntimeError("at least one revision category required")
    unknown = sorted(set(categories) - REVISION_CATEGORIES)
    if unknown:
        raise RuntimeError("unknown revision categories: " + ",".join(unknown))

    submission, decision, learning = _lineage_receipts(paper_ledger)
    if not submission or not validate_submission_receipt(submission):
        raise RuntimeError("valid parent actual-submission receipt required")
    if not decision or not validate_venue_decision_receipt(decision):
        raise RuntimeError("valid parent venue-decision receipt required")
    if not learning or learning.get("pass") is not True or not validate_learning_receipt(learning):
        raise RuntimeError("valid parent post-decision learning receipt required")
    if str(decision.get("submission_receipt_sha256") or "") != str(submission.get("submission_receipt_sha256") or ""):
        raise RuntimeError("parent decision/submission lineage mismatch")
    if str(learning.get("venue_decision_sha256") or "") != str(decision.get("venue_decision_sha256") or ""):
        raise RuntimeError("parent learning/decision lineage mismatch")

    parent_submission_sha = str(submission.get("submission_receipt_sha256") or "")
    parent_decision_sha = str(decision.get("venue_decision_sha256") or "")
    parent_learning_sha = str(learning.get("learning_receipt_sha256") or "")
    parent_decision = str(decision.get("decision") or "")
    parent_submission_venue = str(submission.get("venue") or "")
    parent_attempt_sha = ""
    if parent_attempt:
        if not validate_attempt_plan(parent_attempt):
            raise RuntimeError("invalid parent submission attempt")
        if str(parent_attempt.get("paper_id") or "") != paper_id or str(parent_attempt.get("contract_sha256") or "") != contract_sha:
            raise RuntimeError("parent attempt paper/contract mismatch")
        parent_attempt_sha = str(parent_attempt.get("attempt_sha256") or "")
    if parent_attempt_workflow is not None:
        if not parent_attempt:
            raise RuntimeError("parent attempt workflow requires a parent attempt plan")
        from .submission_attempt_post_submission import validate_attempt_learning_packet, validate_attempt_venue_decision
        from .submission_attempt_workflow import current_attempt_workflow_summary, validate_attempt_actual_submission, validate_attempt_workflow_ledger
        errors = validate_attempt_workflow_ledger(parent_attempt_workflow)
        if errors:
            raise RuntimeError(f"parent attempt workflow invalid: {errors}")
        summary = current_attempt_workflow_summary(parent_attempt_workflow)
        if summary.get("status") != "ATTEMPT_POST_DECISION_LEARN_COMPLETE":
            raise RuntimeError("parent attempt outcome is not post-decision-learn complete")
        if str(parent_attempt_workflow.get("attempt_sha256") or "") != parent_attempt_sha:
            raise RuntimeError("parent attempt workflow/plan SHA mismatch")
        child_submission = next((e.get("receipt") or {} for e in reversed(parent_attempt_workflow.get("events") or []) if isinstance(e, Mapping) and e.get("event_type") == "attempt-actual-submission"), {})
        child_decision = next((e.get("receipt") or {} for e in reversed(parent_attempt_workflow.get("events") or []) if isinstance(e, Mapping) and e.get("event_type") == "attempt-venue-decision"), {})
        child_learning = next((e.get("receipt") or {} for e in reversed(parent_attempt_workflow.get("events") or []) if isinstance(e, Mapping) and e.get("event_type") == "attempt-post-decision-learning"), {})
        if not isinstance(child_submission, Mapping) or not validate_attempt_actual_submission(child_submission):
            raise RuntimeError("valid parent child-attempt submission receipt required")
        if not isinstance(child_decision, Mapping) or not validate_attempt_venue_decision(child_decision):
            raise RuntimeError("valid parent child-attempt decision receipt required")
        if not isinstance(child_learning, Mapping) or child_learning.get("pass") is not True or not validate_attempt_learning_packet(child_learning):
            raise RuntimeError("valid parent child-attempt learning receipt required")
        if child_decision.get("attempt_submission_receipt_sha256") != child_submission.get("attempt_submission_receipt_sha256"):
            raise RuntimeError("parent child decision/submission lineage mismatch")
        if child_learning.get("attempt_venue_decision_sha256") != child_decision.get("attempt_venue_decision_sha256"):
            raise RuntimeError("parent child learning/decision lineage mismatch")
        parent_submission_sha = str(child_submission.get("attempt_submission_receipt_sha256") or "")
        parent_decision_sha = str(child_decision.get("attempt_venue_decision_sha256") or "")
        parent_learning_sha = str(child_learning.get("attempt_learning_receipt_sha256") or "")
        parent_decision = str(child_decision.get("decision") or "")
        parent_submission_venue = str(child_submission.get("venue") or "")

    if attempt_type == "RESUBMISSION" and parent_decision not in RESUBMISSION_PARENT_DECISIONS:
        raise RuntimeError(f"resubmission requires rejected/withdrawn/closed parent decision, got {parent_decision}")
    if attempt_type == "CAMERA_READY":
        if parent_decision != "ACCEPT":
            raise RuntimeError(f"camera-ready requires ACCEPT parent decision, got {parent_decision}")
        if target_venue != parent_submission_venue:
            raise RuntimeError("camera-ready target venue must match the accepted parent venue")

    science_category = bool(set(categories) & SCIENTIFIC_REVISION_CATEGORIES)
    scientific_change = (
        scientific_contract_unchanged is not True
        or bool(new_claim_requested)
        or bool(new_experiment_requested)
        or bool(new_scientific_evidence_requested)
        or bool(scientific_interpretation_change_requested)
        or science_category
    )
    if attempt_type == "RESUBMISSION":
        status = "RESUBMISSION_REQUIRES_EXPLICIT_SCIENTIFIC_REOPEN" if scientific_change else "RESUBMISSION_PAPER_SIDE_ONLY"
    else:
        status = "CAMERA_READY_REQUIRES_EXPLICIT_SCIENTIFIC_REOPEN" if scientific_change else "CAMERA_READY_PAPER_SIDE_ONLY"

    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "submission-attempt-plan",
        "paper_id": paper_id,
        "contract_sha256": contract_sha,
        "attempt_type": attempt_type,
        "target_venue": target_venue,
        "parent_submission_receipt_sha256": parent_submission_sha,
        "parent_venue_decision_sha256": parent_decision_sha,
        "parent_learning_receipt_sha256": parent_learning_sha,
        "parent_attempt_sha256": parent_attempt_sha,
        "revision_categories": categories,
        "scientific_contract_unchanged": scientific_contract_unchanged is True,
        "new_claim_requested": bool(new_claim_requested),
        "new_experiment_requested": bool(new_experiment_requested),
        "new_scientific_evidence_requested": bool(new_scientific_evidence_requested),
        "scientific_interpretation_change_requested": bool(scientific_interpretation_change_requested),
        "status": status,
        "machine_preparation_eligible": not scientific_change,
        "requires_explicit_scientific_reopen": scientific_change,
        "parent_submission_bytes_immutable": True,
        "parent_attempt_immutable": True,
        "scientific_claim_status_unchanged": True,
        "automatic_reopen_authorized": False,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["attempt_sha256"] = _digest(attempt_identity(receipt))
    receipt["attempt_id"] = f"{attempt_type.lower()}-{receipt['attempt_sha256'][:16]}"
    return receipt


def validate_attempt_plan(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "submission-attempt-plan" or receipt.get("attempt_type") not in ATTEMPT_TYPES:
        return False
    if not receipt.get("paper_id") or not receipt.get("contract_sha256") or not receipt.get("target_venue"):
        return False
    categories = list(receipt.get("revision_categories") or [])
    if not categories or categories != sorted(set(categories)) or any(value not in REVISION_CATEGORIES for value in categories):
        return False
    scientific_change = (
        receipt.get("scientific_contract_unchanged") is not True
        or receipt.get("new_claim_requested") is True
        or receipt.get("new_experiment_requested") is True
        or receipt.get("new_scientific_evidence_requested") is True
        or receipt.get("scientific_interpretation_change_requested") is True
        or bool(set(categories) & SCIENTIFIC_REVISION_CATEGORIES)
    )
    prefix = "RESUBMISSION" if receipt.get("attempt_type") == "RESUBMISSION" else "CAMERA_READY"
    expected_status = f"{prefix}_REQUIRES_EXPLICIT_SCIENTIFIC_REOPEN" if scientific_change else f"{prefix}_PAPER_SIDE_ONLY"
    if receipt.get("status") != expected_status:
        return False
    if receipt.get("machine_preparation_eligible") is not (not scientific_change):
        return False
    if receipt.get("requires_explicit_scientific_reopen") is not scientific_change:
        return False
    if receipt.get("parent_submission_bytes_immutable") is not True or receipt.get("parent_attempt_immutable") is not True:
        return False
    if receipt.get("scientific_claim_status_unchanged") is not True or receipt.get("automatic_reopen_authorized") is not False:
        return False
    if receipt.get("claim_expansion_authorized") is not False or receipt.get("new_experiment_authorized") is not False:
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    if not receipt.get("parent_submission_receipt_sha256") or not receipt.get("parent_venue_decision_sha256") or not receipt.get("parent_learning_receipt_sha256"):
        return False
    expected_sha = _digest(attempt_identity(receipt))
    if str(receipt.get("attempt_sha256") or "") != expected_sha:
        return False
    return str(receipt.get("attempt_id") or "") == f"{str(receipt.get('attempt_type')).lower()}-{expected_sha[:16]}"


def _paths(root: Path, paper_id: str) -> tuple[Path, Path]:
    directory = Path(root) / "paper-submission-attempts"
    directory.mkdir(parents=True, exist_ok=True)
    stem = _slug(paper_id)
    return directory / f"{stem}.json", directory / f".{stem}.lock"


def validate_attempt_ledger(row: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    paper_id = str(row.get("paper_id") or "")
    if not paper_id:
        errors.append("attempt-ledger-paper-id-missing")
    if (row.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("attempt-ledger-authority-leak")
    seen: set[str] = set()
    for index, event in enumerate(row.get("events") or []):
        if not isinstance(event, Mapping):
            errors.append("attempt-event-not-object")
            continue
        if event.get("event_type") != "submission-attempt-plan":
            errors.append("attempt-event-type-invalid")
            continue
        if any(event.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
            errors.append("attempt-event-authority-leak")
        receipt = event.get("receipt") or {}
        if not isinstance(receipt, Mapping) or not validate_attempt_plan(receipt):
            errors.append("attempt-receipt-invalid")
            continue
        if str(receipt.get("paper_id") or "") != paper_id:
            errors.append("attempt-receipt-paper-id-mismatch")
        attempt_sha = str(receipt.get("attempt_sha256") or "")
        if attempt_sha in seen:
            errors.append("duplicate-attempt-sha")
        parent_sha = str(receipt.get("parent_attempt_sha256") or "")
        if parent_sha and parent_sha not in seen:
            errors.append("parent-attempt-must-precede-child")
        expected_event_id = _digest([paper_id, index, attempt_sha, str(event.get("recorded_at") or "")])[:24]
        if str(event.get("event_id") or "") != expected_event_id:
            errors.append("attempt-event-id-invalid")
        seen.add(attempt_sha)
    return list(dict.fromkeys(errors))


def publish_attempt_plan(receipt: Mapping[str, Any], root: Path) -> dict[str, Any]:
    if not validate_attempt_plan(receipt):
        raise RuntimeError("invalid submission attempt plan")
    paper_id = str(receipt.get("paper_id") or "")
    path, lock = _paths(root, paper_id)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "schema_version": SCHEMA_VERSION,
            "paper_id": paper_id,
            "events": [],
            "authority": dict(ZERO_AUTHORITY),
        }
        for event in row.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and prior.get("attempt_sha256") == receipt.get("attempt_sha256"):
                return row
        parent_sha = str(receipt.get("parent_attempt_sha256") or "")
        if parent_sha:
            prior_shas = {
                str((event.get("receipt") or {}).get("attempt_sha256") or "")
                for event in row.get("events") or []
                if isinstance(event, Mapping) and isinstance(event.get("receipt"), Mapping)
            }
            if parent_sha not in prior_shas:
                raise RuntimeError("parent attempt is not present in this append-only ledger")
        recorded_at = _now()
        index = len(row.get("events") or [])
        event = {
            "event_type": "submission-attempt-plan",
            "receipt": dict(receipt),
            "recorded_at": recorded_at,
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        event["event_id"] = _digest([paper_id, index, str(receipt.get("attempt_sha256") or ""), recorded_at])[:24]
        row.setdefault("events", []).append(event)
        row["updated_at"] = recorded_at
        errors = validate_attempt_ledger(row)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return row


def public_attempt_summary(row: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_attempt_ledger(row)
    receipts = [
        dict(event.get("receipt") or {})
        for event in row.get("events") or []
        if isinstance(event, Mapping) and isinstance(event.get("receipt"), Mapping)
    ]
    latest = receipts[-1] if receipts else {}
    return {
        "paper_id": str(row.get("paper_id") or ""),
        "attempts": len(receipts),
        "latest_attempt_id": str(latest.get("attempt_id") or ""),
        "latest_attempt_sha256": str(latest.get("attempt_sha256") or ""),
        "latest_attempt_type": str(latest.get("attempt_type") or ""),
        "latest_status": str(latest.get("status") or ""),
        "target_venue": str(latest.get("target_venue") or ""),
        "machine_preparation_eligible": latest.get("machine_preparation_eligible") is True,
        "requires_explicit_scientific_reopen": latest.get("requires_explicit_scientific_reopen") is True,
        "parent_submission_bytes_immutable": latest.get("parent_submission_bytes_immutable") is True,
        "validation_errors": errors,
        "authority": dict(ZERO_AUTHORITY),
    }
