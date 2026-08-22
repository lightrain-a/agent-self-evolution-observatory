from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .paper_preparation_protocol import build_paper_preparation_receipt, validate_paper_preparation_receipt
from .presubmission_freeze import verify_frozen_artifacts
from .submission_attempt_lineage import validate_attempt_plan

SCHEMA_VERSION = "1.0"
ZERO_AUTHORITY = {"scientific": False, "experiment": False, "gpu": False, "submission": False}
HUMAN_CHECKLIST = (
    "confirm complete author list and venue profiles",
    "confirm dual-submission compliance for this child attempt",
    "review and approve venue-specific AI-use disclosure",
    "verify child-attempt PDF/source/supplement hashes immediately before upload",
    "confirm the parent submitted bytes remain archived and unmodified",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:160] or "unknown-attempt"


def _policy_valid(policy: Mapping[str, Any]) -> bool:
    sha = str(policy.get("snapshot_sha256") or "")
    material = {key: value for key, value in policy.items() if key != "snapshot_sha256"}
    return bool(sha) and sha == _digest(material)


def preparation_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "attempt_sha256": receipt.get("attempt_sha256"),
        "parent_submission_receipt_sha256": receipt.get("parent_submission_receipt_sha256"),
        "paper_preparation_receipt_sha256": receipt.get("paper_preparation_receipt_sha256"),
        "status": receipt.get("status"),
    }


def build_attempt_preparation(*, attempt_plan: Mapping[str, Any], preparation_packet: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_attempt_plan(attempt_plan):
        raise RuntimeError("invalid submission attempt plan")
    if attempt_plan.get("machine_preparation_eligible") is not True or attempt_plan.get("requires_explicit_scientific_reopen") is True:
        raise RuntimeError("attempt requires explicit scientific reopen before machine preparation")
    paper_receipt = build_paper_preparation_receipt(
        paper_id=str(attempt_plan.get("paper_id") or ""),
        contract_sha256=str(attempt_plan.get("contract_sha256") or ""),
        packet=preparation_packet,
    )
    if paper_receipt.get("pass") is not True or not validate_paper_preparation_receipt(paper_receipt):
        raise RuntimeError(f"child attempt paper preparation did not pass: {paper_receipt.get('blockers')}")
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "attempt-preparation",
        "paper_id": str(attempt_plan.get("paper_id") or ""),
        "contract_sha256": str(attempt_plan.get("contract_sha256") or ""),
        "attempt_id": str(attempt_plan.get("attempt_id") or ""),
        "attempt_sha256": str(attempt_plan.get("attempt_sha256") or ""),
        "attempt_type": str(attempt_plan.get("attempt_type") or ""),
        "target_venue": str(attempt_plan.get("target_venue") or ""),
        "parent_submission_receipt_sha256": str(attempt_plan.get("parent_submission_receipt_sha256") or ""),
        "paper_preparation_receipt_sha256": str(paper_receipt.get("receipt_sha256") or ""),
        "paper_preparation_receipt": paper_receipt,
        "status": "ATTEMPT_PREPARATION_PASS",
        "parent_submission_bytes_immutable": True,
        "scientific_contract_unchanged": True,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["attempt_preparation_sha256"] = _digest(preparation_identity(receipt))
    return receipt


def validate_attempt_preparation(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "attempt-preparation" or receipt.get("status") != "ATTEMPT_PREPARATION_PASS":
        return False
    paper_receipt = receipt.get("paper_preparation_receipt") or {}
    if not isinstance(paper_receipt, Mapping) or paper_receipt.get("pass") is not True or not validate_paper_preparation_receipt(paper_receipt):
        return False
    if str(receipt.get("paper_preparation_receipt_sha256") or "") != str(paper_receipt.get("receipt_sha256") or ""):
        return False
    if receipt.get("parent_submission_bytes_immutable") is not True or receipt.get("scientific_contract_unchanged") is not True:
        return False
    if receipt.get("claim_expansion_authorized") is not False or receipt.get("new_experiment_authorized") is not False:
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("attempt_preparation_sha256") or "") == _digest(preparation_identity(receipt))


def freeze_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "attempt_sha256": receipt.get("attempt_sha256"),
        "parent_submission_receipt_sha256": receipt.get("parent_submission_receipt_sha256"),
        "attempt_preparation_sha256": receipt.get("attempt_preparation_sha256"),
        "venue_policy_snapshot_sha256": receipt.get("venue_policy_snapshot_sha256"),
        "frozen_artifacts": receipt.get("frozen_artifacts") or [],
        "status": receipt.get("status"),
    }


def build_attempt_freeze(
    *,
    attempt_plan: Mapping[str, Any],
    preparation_receipt: Mapping[str, Any],
    artifacts: Sequence[Mapping[str, Any]],
    venue_policy: Mapping[str, Any],
) -> dict[str, Any]:
    if not validate_attempt_plan(attempt_plan) or not validate_attempt_preparation(preparation_receipt):
        raise RuntimeError("attempt plan/preparation invalid")
    if str(preparation_receipt.get("attempt_sha256") or "") != str(attempt_plan.get("attempt_sha256") or ""):
        raise RuntimeError("attempt preparation/plan lineage mismatch")
    if not _policy_valid(venue_policy):
        raise RuntimeError("venue policy snapshot integrity failed")
    if str(venue_policy.get("venue") or "") != str(attempt_plan.get("target_venue") or ""):
        raise RuntimeError("attempt target venue does not match venue policy")
    frozen = [dict(item) for item in artifacts if isinstance(item, Mapping)]
    if not frozen or any(not item.get("label") or not item.get("path") or not item.get("sha256") for item in frozen):
        raise RuntimeError("attempt freeze requires content-addressed artifact specs")
    probe = {"frozen_artifacts": frozen}
    drift = verify_frozen_artifacts(probe)
    if drift:
        raise RuntimeError(f"attempt artifacts are already stale: {drift}")
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "attempt-freeze",
        "paper_id": str(attempt_plan.get("paper_id") or ""),
        "contract_sha256": str(attempt_plan.get("contract_sha256") or ""),
        "attempt_id": str(attempt_plan.get("attempt_id") or ""),
        "attempt_sha256": str(attempt_plan.get("attempt_sha256") or ""),
        "attempt_type": str(attempt_plan.get("attempt_type") or ""),
        "target_venue": str(attempt_plan.get("target_venue") or ""),
        "parent_submission_receipt_sha256": str(attempt_plan.get("parent_submission_receipt_sha256") or ""),
        "attempt_preparation_sha256": str(preparation_receipt.get("attempt_preparation_sha256") or ""),
        "venue_policy_snapshot_sha256": str(venue_policy.get("snapshot_sha256") or ""),
        "frozen_artifacts": frozen,
        "status": "ATTEMPT_MACHINE_FROZEN",
        "frozen_at": _now(),
        "parent_submission_bytes_immutable": True,
        "human_submission_authority_required": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["attempt_freeze_sha256"] = _digest(freeze_identity(receipt))
    return receipt


def validate_attempt_freeze(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "attempt-freeze" or receipt.get("status") != "ATTEMPT_MACHINE_FROZEN":
        return False
    if not receipt.get("attempt_sha256") or not receipt.get("attempt_preparation_sha256") or not receipt.get("venue_policy_snapshot_sha256"):
        return False
    if receipt.get("parent_submission_bytes_immutable") is not True or receipt.get("human_submission_authority_required") is not True:
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    if not receipt.get("frozen_artifacts"):
        return False
    return str(receipt.get("attempt_freeze_sha256") or "") == _digest(freeze_identity(receipt))


def handoff_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "attempt_sha256": receipt.get("attempt_sha256"),
        "parent_submission_receipt_sha256": receipt.get("parent_submission_receipt_sha256"),
        "attempt_freeze_sha256": receipt.get("attempt_freeze_sha256"),
        "venue_policy_snapshot_sha256": receipt.get("venue_policy_snapshot_sha256"),
        "artifacts": receipt.get("artifacts") or [],
        "human_checklist": receipt.get("human_checklist") or [],
        "status": receipt.get("status"),
    }


def build_attempt_handoff(
    *,
    attempt_plan: Mapping[str, Any],
    preparation_receipt: Mapping[str, Any],
    freeze_receipt: Mapping[str, Any],
    venue_policy: Mapping[str, Any],
) -> dict[str, Any]:
    if not validate_attempt_plan(attempt_plan) or not validate_attempt_preparation(preparation_receipt) or not validate_attempt_freeze(freeze_receipt):
        raise RuntimeError("attempt workflow lineage invalid")
    if str(freeze_receipt.get("attempt_sha256") or "") != str(attempt_plan.get("attempt_sha256") or ""):
        raise RuntimeError("attempt freeze/plan lineage mismatch")
    if str(freeze_receipt.get("attempt_preparation_sha256") or "") != str(preparation_receipt.get("attempt_preparation_sha256") or ""):
        raise RuntimeError("attempt freeze/preparation lineage mismatch")
    if not _policy_valid(venue_policy) or str(venue_policy.get("snapshot_sha256") or "") != str(freeze_receipt.get("venue_policy_snapshot_sha256") or ""):
        raise RuntimeError("attempt freeze/policy lineage mismatch")
    drift = verify_frozen_artifacts(freeze_receipt)
    if drift:
        raise RuntimeError(f"attempt frozen artifacts are stale: {drift}")
    public_artifacts = [
        {
            "label": str(item.get("label") or "artifact"),
            "filename": Path(str(item.get("path") or "artifact")).name,
            "sha256": str(item.get("sha256") or ""),
            "bytes": int(item.get("bytes") or 0),
        }
        for item in freeze_receipt.get("frozen_artifacts") or []
        if isinstance(item, Mapping)
    ]
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "attempt-handoff",
        "paper_id": str(attempt_plan.get("paper_id") or ""),
        "contract_sha256": str(attempt_plan.get("contract_sha256") or ""),
        "attempt_id": str(attempt_plan.get("attempt_id") or ""),
        "attempt_sha256": str(attempt_plan.get("attempt_sha256") or ""),
        "attempt_type": str(attempt_plan.get("attempt_type") or ""),
        "target_venue": str(attempt_plan.get("target_venue") or ""),
        "parent_submission_receipt_sha256": str(attempt_plan.get("parent_submission_receipt_sha256") or ""),
        "attempt_freeze_sha256": str(freeze_receipt.get("attempt_freeze_sha256") or ""),
        "venue_policy_snapshot_sha256": str(venue_policy.get("snapshot_sha256") or ""),
        "artifacts": public_artifacts,
        "human_checklist": list(HUMAN_CHECKLIST),
        "human_confirmation_status": "PENDING_HUMAN",
        "status": "ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED",
        "parent_submission_bytes_immutable": True,
        "must_not_upload_if_hash_mismatch": True,
        "external_human_submission_authority_required": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["attempt_handoff_sha256"] = _digest(handoff_identity(receipt))
    return receipt


def validate_attempt_handoff(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "attempt-handoff" or receipt.get("status") != "ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED":
        return False
    if receipt.get("human_confirmation_status") != "PENDING_HUMAN":
        return False
    if receipt.get("parent_submission_bytes_immutable") is not True or receipt.get("must_not_upload_if_hash_mismatch") is not True:
        return False
    if receipt.get("external_human_submission_authority_required") is not True:
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("attempt_handoff_sha256") or "") == _digest(handoff_identity(receipt))


def _latest_receipt(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, Mapping) and event.get("event_type") == event_type:
            receipt = event.get("receipt") or {}
            return dict(receipt) if isinstance(receipt, Mapping) else {}
    return {}


def attempt_checklist_items(handoff_receipt: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    used: set[str] = set()
    for raw in handoff_receipt.get("human_checklist") or []:
        text = str(raw).strip()
        if not text:
            continue
        check_id = "ATTEMPT_CHECK_" + _digest(text)[:12].upper()
        if check_id in used:
            continue
        used.add(check_id)
        rows.append({"check_id": check_id, "text": text})
    return rows


def attempt_signoff_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "attempt_sha256": receipt.get("attempt_sha256"),
        "attempt_handoff_sha256": receipt.get("attempt_handoff_sha256"),
        "attempt_freeze_sha256": receipt.get("attempt_freeze_sha256"),
        "confirmed_check_ids": receipt.get("confirmed_check_ids") or [],
        "external_human_confirmation_ref": receipt.get("external_human_confirmation_ref"),
        "confirmed_at": receipt.get("confirmed_at"),
        "acknowledge_current_artifact_hashes": receipt.get("acknowledge_current_artifact_hashes"),
        "acknowledge_actual_submission_not_performed": receipt.get("acknowledge_actual_submission_not_performed"),
        "status": receipt.get("status"),
    }


def build_attempt_signoff_template(workflow_ledger: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_attempt_workflow_ledger(workflow_ledger)
    if errors:
        raise RuntimeError(f"attempt workflow ledger invalid: {errors}")
    summary = current_attempt_workflow_summary(workflow_ledger)
    if summary.get("status") != "ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED":
        raise RuntimeError("attempt handoff is not current and human-signoff eligible")
    handoff = _latest_receipt(workflow_ledger, "attempt-handoff")
    template = {
        "schema_version": SCHEMA_VERSION,
        "paper_id": str(workflow_ledger.get("paper_id") or ""),
        "attempt_id": str(workflow_ledger.get("attempt_id") or ""),
        "attempt_sha256": str(workflow_ledger.get("attempt_sha256") or ""),
        "attempt_handoff_sha256": str(handoff.get("attempt_handoff_sha256") or ""),
        "status": "ATTEMPT_PENDING_HUMAN_CONFIRMATION",
        "required_confirmations": attempt_checklist_items(handoff),
        "required_explicit_inputs": [
            "external_human_confirmation_ref",
            "confirmed_at",
            "all required confirmation IDs",
            "acknowledge_current_artifact_hashes=true",
            "acknowledge_actual_submission_not_performed=true",
        ],
        "submission_authority": False,
    }
    template["template_sha256"] = _digest(template)
    return template


def build_attempt_human_signoff(
    *,
    workflow_ledger: Mapping[str, Any],
    confirmed_check_ids: Sequence[str],
    external_human_confirmation_ref: str,
    confirmed_at: str,
    acknowledge_current_artifact_hashes: bool,
    acknowledge_actual_submission_not_performed: bool,
) -> dict[str, Any]:
    errors = validate_attempt_workflow_ledger(workflow_ledger)
    if errors:
        raise RuntimeError(f"attempt workflow ledger invalid: {errors}")
    summary = current_attempt_workflow_summary(workflow_ledger)
    if summary.get("status") != "ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED":
        raise RuntimeError("attempt handoff is not current and human-signoff eligible")
    handoff = _latest_receipt(workflow_ledger, "attempt-handoff")
    freeze = _latest_receipt(workflow_ledger, "attempt-freeze")
    required = [row["check_id"] for row in attempt_checklist_items(handoff)]
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
        raise RuntimeError("human must acknowledge current child-attempt artifact hashes")
    if acknowledge_actual_submission_not_performed is not True:
        raise RuntimeError("human must acknowledge actual child submission is a separate action")
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "attempt-human-signoff",
        "paper_id": str(workflow_ledger.get("paper_id") or ""),
        "attempt_id": str(workflow_ledger.get("attempt_id") or ""),
        "attempt_sha256": str(workflow_ledger.get("attempt_sha256") or ""),
        "attempt_handoff_sha256": str(handoff.get("attempt_handoff_sha256") or ""),
        "attempt_freeze_sha256": str(freeze.get("attempt_freeze_sha256") or ""),
        "confirmed_check_ids": required,
        "external_human_confirmation_ref": str(external_human_confirmation_ref).strip(),
        "confirmed_at": str(confirmed_at).strip(),
        "acknowledge_current_artifact_hashes": True,
        "acknowledge_actual_submission_not_performed": True,
        "status": "ATTEMPT_HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING",
        "actual_submission_status": "NOT_SUBMITTED",
        "parent_signoff_reuse_forbidden": True,
        "external_human_submission_authority_required_for_actual_submit": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["attempt_signoff_sha256"] = _digest(attempt_signoff_identity(receipt))
    return receipt


def validate_attempt_human_signoff(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "attempt-human-signoff" or receipt.get("status") != "ATTEMPT_HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING":
        return False
    if receipt.get("actual_submission_status") != "NOT_SUBMITTED" or receipt.get("parent_signoff_reuse_forbidden") is not True:
        return False
    if receipt.get("external_human_submission_authority_required_for_actual_submit") is not True:
        return False
    if not receipt.get("attempt_handoff_sha256") or not receipt.get("attempt_freeze_sha256") or not receipt.get("confirmed_check_ids"):
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("attempt_signoff_sha256") or "") == _digest(attempt_signoff_identity(receipt))


def attempt_submission_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "attempt_sha256": receipt.get("attempt_sha256"),
        "attempt_signoff_sha256": receipt.get("attempt_signoff_sha256"),
        "attempt_handoff_sha256": receipt.get("attempt_handoff_sha256"),
        "attempt_freeze_sha256": receipt.get("attempt_freeze_sha256"),
        "venue": receipt.get("venue"),
        "venue_submission_id": receipt.get("venue_submission_id"),
        "venue_forum_ref": receipt.get("venue_forum_ref"),
        "uploaded_artifact_sha256": receipt.get("uploaded_artifact_sha256") or {},
        "submitted_at": receipt.get("submitted_at"),
        "external_human_submission_authority_ref": receipt.get("external_human_submission_authority_ref"),
        "status": receipt.get("status"),
        "actual_submission_status": receipt.get("actual_submission_status"),
    }


def build_attempt_actual_submission(
    *,
    workflow_ledger: Mapping[str, Any],
    signoff_receipt: Mapping[str, Any],
    venue_submission_id: str,
    venue_forum_ref: str,
    uploaded_artifact_sha256: Mapping[str, str],
    submitted_at: str,
    external_human_submission_authority_ref: str,
) -> dict[str, Any]:
    errors = validate_attempt_workflow_ledger(workflow_ledger)
    if errors:
        raise RuntimeError(f"attempt workflow ledger invalid: {errors}")
    if not validate_attempt_human_signoff(signoff_receipt):
        raise RuntimeError("valid attempt human signoff required")
    handoff = _latest_receipt(workflow_ledger, "attempt-handoff")
    freeze = _latest_receipt(workflow_ledger, "attempt-freeze")
    if str(signoff_receipt.get("attempt_sha256") or "") != str(workflow_ledger.get("attempt_sha256") or ""):
        raise RuntimeError("attempt signoff belongs to a different attempt")
    if signoff_receipt.get("attempt_handoff_sha256") != handoff.get("attempt_handoff_sha256") or signoff_receipt.get("attempt_freeze_sha256") != freeze.get("attempt_freeze_sha256"):
        raise RuntimeError("attempt signoff is stale relative to current handoff/freeze")
    drift = verify_frozen_artifacts(freeze)
    if drift:
        raise RuntimeError(f"attempt frozen artifacts are stale: {drift}")
    expected = {str(item.get("label") or ""): str(item.get("sha256") or "") for item in freeze.get("frozen_artifacts") or [] if isinstance(item, Mapping)}
    uploaded = {str(key): str(value) for key, value in uploaded_artifact_sha256.items()}
    if not expected or uploaded != expected:
        raise RuntimeError(f"uploaded child-attempt hashes do not match current freeze: expected={expected}, uploaded={uploaded}")
    if not str(venue_submission_id or "").strip() or not str(venue_forum_ref or "").strip():
        raise RuntimeError("venue submission id and forum/reference are required")
    if not str(submitted_at or "").strip() or not str(external_human_submission_authority_ref or "").strip():
        raise RuntimeError("submission timestamp and external human submission authority reference are required")
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "attempt-actual-submission",
        "paper_id": str(workflow_ledger.get("paper_id") or ""),
        "attempt_id": str(workflow_ledger.get("attempt_id") or ""),
        "attempt_sha256": str(workflow_ledger.get("attempt_sha256") or ""),
        "attempt_signoff_sha256": str(signoff_receipt.get("attempt_signoff_sha256") or ""),
        "attempt_handoff_sha256": str(handoff.get("attempt_handoff_sha256") or ""),
        "attempt_freeze_sha256": str(freeze.get("attempt_freeze_sha256") or ""),
        "venue": str(handoff.get("target_venue") or ""),
        "venue_submission_id": str(venue_submission_id).strip(),
        "venue_forum_ref": str(venue_forum_ref).strip(),
        "uploaded_artifact_sha256": uploaded,
        "submitted_at": str(submitted_at).strip(),
        "external_human_submission_authority_ref": str(external_human_submission_authority_ref).strip(),
        "status": "ATTEMPT_VENUE_SUBMISSION_CONFIRMED",
        "actual_submission_status": "SUBMITTED",
        "parent_submission_receipt_reuse_forbidden": True,
        "parent_submission_bytes_immutable": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["attempt_submission_receipt_sha256"] = _digest(attempt_submission_identity(receipt))
    return receipt


def validate_attempt_actual_submission(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "attempt-actual-submission" or receipt.get("status") != "ATTEMPT_VENUE_SUBMISSION_CONFIRMED":
        return False
    if receipt.get("actual_submission_status") != "SUBMITTED" or receipt.get("parent_submission_receipt_reuse_forbidden") is not True:
        return False
    if receipt.get("parent_submission_bytes_immutable") is not True:
        return False
    if not receipt.get("attempt_signoff_sha256") or not receipt.get("venue_submission_id") or not receipt.get("venue_forum_ref") or not receipt.get("external_human_submission_authority_ref"):
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("attempt_submission_receipt_sha256") or "") == _digest(attempt_submission_identity(receipt))


def _event_sha(receipt: Mapping[str, Any]) -> tuple[str, str]:
    if receipt.get("receipt_type") == "attempt-preparation":
        return "attempt-preparation", str(receipt.get("attempt_preparation_sha256") or "")
    if receipt.get("receipt_type") == "attempt-freeze":
        return "attempt-freeze", str(receipt.get("attempt_freeze_sha256") or "")
    if receipt.get("receipt_type") == "attempt-handoff":
        return "attempt-handoff", str(receipt.get("attempt_handoff_sha256") or "")
    if receipt.get("receipt_type") == "attempt-human-signoff":
        return "attempt-human-signoff", str(receipt.get("attempt_signoff_sha256") or "")
    if receipt.get("receipt_type") == "attempt-actual-submission":
        return "attempt-actual-submission", str(receipt.get("attempt_submission_receipt_sha256") or "")
    raise RuntimeError("unknown attempt workflow receipt type")


def _validator(receipt: Mapping[str, Any]) -> bool:
    return (
        validate_attempt_preparation(receipt)
        if receipt.get("receipt_type") == "attempt-preparation"
        else validate_attempt_freeze(receipt)
        if receipt.get("receipt_type") == "attempt-freeze"
        else validate_attempt_handoff(receipt)
        if receipt.get("receipt_type") == "attempt-handoff"
        else validate_attempt_human_signoff(receipt)
        if receipt.get("receipt_type") == "attempt-human-signoff"
        else validate_attempt_actual_submission(receipt)
        if receipt.get("receipt_type") == "attempt-actual-submission"
        else False
    )


def validate_attempt_workflow_ledger(row: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if (row.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("attempt-workflow-ledger-authority-leak")
    attempt_sha = str(row.get("attempt_sha256") or "")
    seen_preparations: set[str] = set()
    seen_freezes: set[str] = set()
    seen_handoffs: set[str] = set()
    seen_signoffs: set[str] = set()
    seen_receipts: set[str] = set()
    for index, event in enumerate(row.get("events") or []):
        if not isinstance(event, Mapping):
            errors.append("attempt-workflow-event-not-object")
            continue
        receipt = event.get("receipt") or {}
        if not isinstance(receipt, Mapping) or not _validator(receipt):
            errors.append("attempt-workflow-receipt-invalid")
            continue
        kind, receipt_sha = _event_sha(receipt)
        if event.get("event_type") != kind:
            errors.append("attempt-workflow-event-type-mismatch")
        if str(receipt.get("attempt_sha256") or "") != attempt_sha:
            errors.append("attempt-workflow-attempt-sha-mismatch")
        if receipt_sha in seen_receipts:
            errors.append("attempt-workflow-duplicate-receipt")
        if kind == "attempt-preparation":
            seen_preparations.add(receipt_sha)
        elif kind == "attempt-freeze":
            if str(receipt.get("attempt_preparation_sha256") or "") not in seen_preparations:
                errors.append("attempt-freeze-missing-prior-preparation")
            seen_freezes.add(receipt_sha)
        elif kind == "attempt-handoff":
            if str(receipt.get("attempt_freeze_sha256") or "") not in seen_freezes:
                errors.append("attempt-handoff-missing-prior-freeze")
            seen_handoffs.add(receipt_sha)
        elif kind == "attempt-human-signoff":
            if str(receipt.get("attempt_handoff_sha256") or "") not in seen_handoffs:
                errors.append("attempt-signoff-missing-prior-handoff")
            seen_signoffs.add(receipt_sha)
        elif kind == "attempt-actual-submission" and str(receipt.get("attempt_signoff_sha256") or "") not in seen_signoffs:
            errors.append("attempt-submission-missing-prior-signoff")
        expected_event_id = _digest([attempt_sha, index, kind, receipt_sha, str(event.get("recorded_at") or "")])[:24]
        if str(event.get("event_id") or "") != expected_event_id:
            errors.append("attempt-workflow-event-id-invalid")
        if any(event.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
            errors.append("attempt-workflow-event-authority-leak")
        seen_receipts.add(receipt_sha)
    return list(dict.fromkeys(errors))


def _path(root: Path, attempt_id: str) -> tuple[Path, Path]:
    directory = Path(root) / "paper-submission-attempt-workflows"
    directory.mkdir(parents=True, exist_ok=True)
    stem = _slug(attempt_id)
    return directory / f"{stem}.json", directory / f".{stem}.lock"


def append_attempt_workflow_receipt(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not _validator(receipt):
        raise RuntimeError("invalid attempt workflow receipt")
    attempt_id = str(receipt.get("attempt_id") or "")
    attempt_sha = str(receipt.get("attempt_sha256") or "")
    path, lock = _path(root, attempt_id)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "schema_version": SCHEMA_VERSION,
            "paper_id": str(receipt.get("paper_id") or ""),
            "attempt_id": attempt_id,
            "attempt_sha256": attempt_sha,
            "events": [],
            "authority": dict(ZERO_AUTHORITY),
        }
        if str(row.get("attempt_sha256") or "") != attempt_sha:
            raise RuntimeError("attempt workflow ledger SHA mismatch")
        kind, receipt_sha = _event_sha(receipt)
        for event in row.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _event_sha(prior)[1] == receipt_sha:
                return row
        recorded_at = str(receipt.get("frozen_at") or _now())
        index = len(row.get("events") or [])
        event = {
            "event_type": kind,
            "receipt": dict(receipt),
            "recorded_at": recorded_at,
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        event["event_id"] = _digest([attempt_sha, index, kind, receipt_sha, recorded_at])[:24]
        row.setdefault("events", []).append(event)
        row["updated_at"] = recorded_at
        errors = validate_attempt_workflow_ledger(row)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return row


def current_attempt_workflow_summary(row: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_attempt_workflow_ledger(row)
    preparations = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-preparation"]
    freezes = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-freeze"]
    handoffs = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-handoff"]
    signoffs = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-human-signoff"]
    submissions = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-actual-submission"]
    preparation = preparations[-1] if preparations else {}
    freeze = freezes[-1] if freezes else {}
    handoff = handoffs[-1] if handoffs else {}
    signoff = signoffs[-1] if signoffs else {}
    submission = submissions[-1] if submissions else {}
    drift = verify_frozen_artifacts(freeze) if freeze else []
    freeze_current = bool(freeze) and not drift
    handoff_current = bool(handoff) and freeze_current and handoff.get("attempt_freeze_sha256") == freeze.get("attempt_freeze_sha256")
    signoff_current = bool(signoff) and handoff_current and signoff.get("attempt_handoff_sha256") == handoff.get("attempt_handoff_sha256") and signoff.get("attempt_freeze_sha256") == freeze.get("attempt_freeze_sha256")
    submission_valid = bool(submission) and validate_attempt_actual_submission(submission) and bool(signoff) and submission.get("attempt_signoff_sha256") == signoff.get("attempt_signoff_sha256")
    if errors:
        status = "ATTEMPT_WORKFLOW_INVALID"
    elif submission_valid:
        status = "ATTEMPT_VENUE_SUBMISSION_CONFIRMED"
    elif signoff_current:
        status = "ATTEMPT_HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING"
    elif signoff:
        status = "ATTEMPT_HUMAN_SIGNOFF_STALE"
    elif handoff_current:
        status = "ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED"
    elif handoff:
        status = "ATTEMPT_HANDOFF_STALE"
    elif freeze_current:
        status = "ATTEMPT_MACHINE_FROZEN_HANDOFF_PENDING"
    elif freeze:
        status = "ATTEMPT_FREEZE_STALE"
    elif preparation:
        status = "ATTEMPT_PREPARATION_PASS_FREEZE_PENDING"
    else:
        status = "ATTEMPT_WORKFLOW_NOT_STARTED"
    return {
        "paper_id": str(row.get("paper_id") or ""),
        "attempt_id": str(row.get("attempt_id") or ""),
        "attempt_sha256": str(row.get("attempt_sha256") or ""),
        "status": status,
        "preparation_sha256": str(preparation.get("attempt_preparation_sha256") or ""),
        "freeze_sha256": str(freeze.get("attempt_freeze_sha256") or ""),
        "handoff_sha256": str(handoff.get("attempt_handoff_sha256") or ""),
        "signoff_sha256": str(signoff.get("attempt_signoff_sha256") or ""),
        "submission_receipt_sha256": str(submission.get("attempt_submission_receipt_sha256") or ""),
        "venue_submission_id": str(submission.get("venue_submission_id") or ""),
        "submitted_at": str(submission.get("submitted_at") or ""),
        "frozen_artifacts": len(freeze.get("frozen_artifacts") or []),
        "freeze_drift_errors": drift,
        "validation_errors": errors,
        "parent_submission_bytes_immutable": True,
        "human_confirmation_status": str(signoff.get("status") or handoff.get("human_confirmation_status") or ""),
        "actual_submission_status": str(submission.get("actual_submission_status") or "NOT_SUBMITTED"),
        "authority": dict(ZERO_AUTHORITY),
    }
