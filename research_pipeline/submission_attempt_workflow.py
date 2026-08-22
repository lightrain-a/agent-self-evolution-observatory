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


def submission_conflict_guard_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "attempt_id": receipt.get("attempt_id"),
        "attempt_sha256": receipt.get("attempt_sha256"),
        "attempt_signoff_sha256": receipt.get("attempt_signoff_sha256"),
        "attempt_type": receipt.get("attempt_type"),
        "target_venue": receipt.get("target_venue"),
        "parent_attempt_sha256": receipt.get("parent_attempt_sha256"),
        "sibling_snapshot": receipt.get("sibling_snapshot") or [],
        "sibling_snapshot_sha256": receipt.get("sibling_snapshot_sha256"),
        "active_conflicts": receipt.get("active_conflicts") or [],
        "status": receipt.get("status"),
        "pass": receipt.get("pass"),
    }


def _attempt_plan_for_workflow(root: Path, workflow_ledger: Mapping[str, Any]) -> dict[str, Any]:
    paper_id = str(workflow_ledger.get("paper_id") or "")
    attempt_sha = str(workflow_ledger.get("attempt_sha256") or "")
    path = Path(root) / "paper-submission-attempts" / f"{_slug(paper_id)}.json"
    if not path.exists():
        raise RuntimeError("submission-attempt plan ledger missing")
    row = json.loads(path.read_text(encoding="utf-8"))
    for event in row.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if isinstance(receipt, Mapping) and str(receipt.get("attempt_sha256") or "") == attempt_sha:
            if not validate_attempt_plan(receipt):
                raise RuntimeError("submission-attempt plan receipt invalid")
            return dict(receipt)
    raise RuntimeError("submission-attempt plan for workflow not found")


def _sibling_submission_snapshot(root: Path, workflow_ledger: Mapping[str, Any], current_plan: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    directory = Path(root) / "paper-submission-attempt-workflows"
    paper_id = str(workflow_ledger.get("paper_id") or "")
    attempt_sha = str(workflow_ledger.get("attempt_sha256") or "")
    rows: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    if not directory.exists():
        return rows, conflicts
    for path in sorted(directory.glob("*.json")):
        try:
            sibling = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            rows.append({"attempt_sha256": "", "workflow_status": "ATTEMPT_WORKFLOW_UNREADABLE", "validation_errors": ["unreadable-workflow"]})
            conflicts.append({"attempt_sha256": "", "reason": "SIBLING_WORKFLOW_UNREADABLE"})
            continue
        if str(sibling.get("paper_id") or "") != paper_id or str(sibling.get("attempt_sha256") or "") == attempt_sha:
            continue
        sibling_sha = str(sibling.get("attempt_sha256") or "")
        errors = validate_attempt_workflow_ledger(sibling)
        if errors:
            rows.append({"attempt_sha256": sibling_sha, "workflow_status": "ATTEMPT_WORKFLOW_INVALID", "validation_errors": list(errors)})
            conflicts.append({"attempt_sha256": sibling_sha, "reason": "SIBLING_WORKFLOW_INVALID"})
            continue
        summary = current_attempt_workflow_summary(sibling)
        submission = _latest_receipt(sibling, "attempt-actual-submission")
        decision = _latest_receipt(sibling, "attempt-venue-decision")
        decision_value = str(decision.get("decision") or "")
        snapshot = {
            "attempt_sha256": sibling_sha,
            "workflow_status": str(summary.get("status") or ""),
            "submission_receipt_sha256": str(submission.get("attempt_submission_receipt_sha256") or ""),
            "venue": str(submission.get("venue") or ""),
            "venue_decision": decision_value,
            "venue_decision_sha256": str(decision.get("attempt_venue_decision_sha256") or ""),
            "validation_errors": [],
        }
        rows.append(snapshot)
        if not snapshot["submission_receipt_sha256"]:
            continue
        closed = decision_value in {"REJECT", "WITHDRAWN", "VENUE_CLOSED_WITHOUT_DECISION"}
        accepted_camera_ready_parent = (
            decision_value == "ACCEPT"
            and str(current_plan.get("attempt_type") or "") == "CAMERA_READY"
            and str(current_plan.get("parent_attempt_sha256") or "") == sibling_sha
            and str(current_plan.get("target_venue") or "") == snapshot["venue"]
        )
        if not closed and not accepted_camera_ready_parent:
            conflicts.append({
                "attempt_sha256": sibling_sha,
                "submission_receipt_sha256": snapshot["submission_receipt_sha256"],
                "venue": snapshot["venue"],
                "venue_decision": decision_value,
                "reason": "ACCEPTED_PARENT_REQUIRES_CAMERA_READY" if decision_value == "ACCEPT" else "ACTIVE_SIBLING_SUBMISSION",
            })
    rows.sort(key=lambda item: (str(item.get("attempt_sha256") or ""), str(item.get("workflow_status") or "")))
    conflicts.sort(key=lambda item: (str(item.get("attempt_sha256") or ""), str(item.get("reason") or "")))
    return rows, conflicts


def build_attempt_submission_conflict_guard(*, root: Path, workflow_ledger: Mapping[str, Any], signoff_receipt: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_attempt_workflow_ledger(workflow_ledger)
    if errors:
        raise RuntimeError(f"attempt workflow ledger invalid: {errors}")
    if not validate_attempt_human_signoff(signoff_receipt):
        raise RuntimeError("valid attempt human signoff required before submission conflict check")
    if str(signoff_receipt.get("attempt_sha256") or "") != str(workflow_ledger.get("attempt_sha256") or ""):
        raise RuntimeError("submission conflict guard signoff belongs to another attempt")
    plan = _attempt_plan_for_workflow(root, workflow_ledger)
    siblings, conflicts = _sibling_submission_snapshot(root, workflow_ledger, plan)
    snapshot_sha = _digest(siblings)
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "attempt-submission-conflict-guard",
        "paper_id": str(workflow_ledger.get("paper_id") or ""),
        "attempt_id": str(workflow_ledger.get("attempt_id") or ""),
        "attempt_sha256": str(workflow_ledger.get("attempt_sha256") or ""),
        "attempt_signoff_sha256": str(signoff_receipt.get("attempt_signoff_sha256") or ""),
        "attempt_type": str(plan.get("attempt_type") or ""),
        "target_venue": str(plan.get("target_venue") or ""),
        "parent_attempt_sha256": str(plan.get("parent_attempt_sha256") or ""),
        "sibling_snapshot": siblings,
        "sibling_snapshot_sha256": snapshot_sha,
        "active_conflicts": conflicts,
        "status": "ATTEMPT_SUBMISSION_CONFLICT_GUARD_PASS" if not conflicts else "ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING",
        "pass": not conflicts,
        "dual_submission_machine_guard": True,
        "parent_submission_bytes_immutable": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["attempt_submission_conflict_guard_sha256"] = _digest(submission_conflict_guard_identity(receipt))
    return receipt


def validate_attempt_submission_conflict_guard(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "attempt-submission-conflict-guard":
        return False
    if receipt.get("status") not in {"ATTEMPT_SUBMISSION_CONFLICT_GUARD_PASS", "ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING"}:
        return False
    conflicts = list(receipt.get("active_conflicts") or [])
    if receipt.get("pass") is not (not conflicts):
        return False
    if str(receipt.get("sibling_snapshot_sha256") or "") != _digest(receipt.get("sibling_snapshot") or []):
        return False
    if receipt.get("dual_submission_machine_guard") is not True or receipt.get("parent_submission_bytes_immutable") is not True:
        return False
    if not receipt.get("attempt_signoff_sha256"):
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("attempt_submission_conflict_guard_sha256") or "") == _digest(submission_conflict_guard_identity(receipt))


def verify_attempt_submission_conflict_guard_current(*, root: Path, workflow_ledger: Mapping[str, Any], guard_receipt: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not validate_attempt_submission_conflict_guard(guard_receipt):
        return ["attempt-submission-conflict-guard-invalid"]
    signoff = _latest_receipt(workflow_ledger, "attempt-human-signoff")
    if not signoff or guard_receipt.get("attempt_signoff_sha256") != signoff.get("attempt_signoff_sha256"):
        errors.append("attempt-submission-conflict-guard-signoff-stale")
        return errors
    fresh = build_attempt_submission_conflict_guard(root=root, workflow_ledger=workflow_ledger, signoff_receipt=signoff)
    if fresh.get("attempt_submission_conflict_guard_sha256") != guard_receipt.get("attempt_submission_conflict_guard_sha256"):
        errors.append("attempt-submission-conflict-guard-sibling-snapshot-stale")
    if fresh.get("pass") is not True:
        errors.append("attempt-submission-conflict-active-sibling")
    return list(dict.fromkeys(errors))


def attempt_submission_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "attempt_sha256": receipt.get("attempt_sha256"),
        "attempt_signoff_sha256": receipt.get("attempt_signoff_sha256"),
        "attempt_handoff_sha256": receipt.get("attempt_handoff_sha256"),
        "attempt_freeze_sha256": receipt.get("attempt_freeze_sha256"),
        "attempt_submission_conflict_guard_sha256": receipt.get("attempt_submission_conflict_guard_sha256"),
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
    conflict_guard_receipt: Mapping[str, Any],
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
    if not validate_attempt_submission_conflict_guard(conflict_guard_receipt) or conflict_guard_receipt.get("pass") is not True:
        raise RuntimeError("passing attempt submission conflict guard required")
    handoff = _latest_receipt(workflow_ledger, "attempt-handoff")
    freeze = _latest_receipt(workflow_ledger, "attempt-freeze")
    if str(signoff_receipt.get("attempt_sha256") or "") != str(workflow_ledger.get("attempt_sha256") or ""):
        raise RuntimeError("attempt signoff belongs to a different attempt")
    if str(conflict_guard_receipt.get("attempt_sha256") or "") != str(workflow_ledger.get("attempt_sha256") or "") or conflict_guard_receipt.get("attempt_signoff_sha256") != signoff_receipt.get("attempt_signoff_sha256"):
        raise RuntimeError("attempt submission conflict guard belongs to a different attempt/signoff")
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
        "attempt_submission_conflict_guard_sha256": str(conflict_guard_receipt.get("attempt_submission_conflict_guard_sha256") or ""),
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
    if not receipt.get("attempt_signoff_sha256") or not receipt.get("attempt_submission_conflict_guard_sha256") or not receipt.get("venue_submission_id") or not receipt.get("venue_forum_ref") or not receipt.get("external_human_submission_authority_ref"):
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
    if receipt.get("receipt_type") == "attempt-submission-conflict-guard":
        return "attempt-submission-conflict-guard", str(receipt.get("attempt_submission_conflict_guard_sha256") or "")
    if receipt.get("receipt_type") == "attempt-actual-submission":
        return "attempt-actual-submission", str(receipt.get("attempt_submission_receipt_sha256") or "")
    if receipt.get("receipt_type") == "attempt-review-set":
        return "attempt-review-set", str(receipt.get("attempt_review_set_sha256") or "")
    if receipt.get("receipt_type") == "attempt-rebuttal-preparation":
        return "attempt-rebuttal-preparation", str(receipt.get("attempt_rebuttal_receipt_sha256") or "")
    if receipt.get("receipt_type") == "attempt-venue-final-decision":
        return "attempt-venue-decision", str(receipt.get("attempt_venue_decision_sha256") or "")
    if receipt.get("receipt_type") == "attempt-rebuttal-skipped-by-venue":
        return "attempt-rebuttal-skipped-by-venue", str(receipt.get("attempt_rebuttal_skip_sha256") or "")
    if receipt.get("receipt_type") == "attempt-post-decision-learning":
        return "attempt-post-decision-learning", str(receipt.get("attempt_learning_receipt_sha256") or "")
    raise RuntimeError("unknown attempt workflow receipt type")


def _validator(receipt: Mapping[str, Any]) -> bool:
    receipt_type = str(receipt.get("receipt_type") or "")
    if receipt_type == "attempt-preparation": return validate_attempt_preparation(receipt)
    if receipt_type == "attempt-freeze": return validate_attempt_freeze(receipt)
    if receipt_type == "attempt-handoff": return validate_attempt_handoff(receipt)
    if receipt_type == "attempt-human-signoff": return validate_attempt_human_signoff(receipt)
    if receipt_type == "attempt-submission-conflict-guard": return validate_attempt_submission_conflict_guard(receipt)
    if receipt_type == "attempt-actual-submission": return validate_attempt_actual_submission(receipt)
    from .submission_attempt_post_submission import (
        validate_attempt_learning_packet, validate_attempt_rebuttal_preparation,
        validate_attempt_rebuttal_skipped, validate_attempt_review_set, validate_attempt_venue_decision,
    )
    if receipt_type == "attempt-review-set": return validate_attempt_review_set(receipt)
    if receipt_type == "attempt-rebuttal-preparation": return validate_attempt_rebuttal_preparation(receipt)
    if receipt_type == "attempt-venue-final-decision": return validate_attempt_venue_decision(receipt)
    if receipt_type == "attempt-rebuttal-skipped-by-venue": return validate_attempt_rebuttal_skipped(receipt)
    if receipt_type == "attempt-post-decision-learning": return validate_attempt_learning_packet(receipt)
    return False


def validate_attempt_workflow_ledger(row: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if (row.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("attempt-workflow-ledger-authority-leak")
    attempt_sha = str(row.get("attempt_sha256") or "")
    seen_preparations: set[str] = set()
    seen_freezes: set[str] = set()
    seen_handoffs: set[str] = set()
    seen_signoffs: set[str] = set()
    seen_guards: dict[str, bool] = {}
    seen_submissions: set[str] = set()
    seen_reviews: set[str] = set()
    seen_rebuttals: set[str] = set()
    seen_decisions: dict[str, str] = {}
    seen_skip_decisions: set[str] = set()
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
        elif kind == "attempt-submission-conflict-guard":
            if str(receipt.get("attempt_signoff_sha256") or "") not in seen_signoffs:
                errors.append("attempt-conflict-guard-missing-prior-signoff")
            seen_guards[receipt_sha] = receipt.get("pass") is True
        elif kind == "attempt-actual-submission":
            if str(receipt.get("attempt_signoff_sha256") or "") not in seen_signoffs:
                errors.append("attempt-submission-missing-prior-signoff")
            guard_sha = str(receipt.get("attempt_submission_conflict_guard_sha256") or "")
            if guard_sha not in seen_guards or seen_guards.get(guard_sha) is not True:
                errors.append("attempt-submission-missing-prior-passing-conflict-guard")
            seen_submissions.add(receipt_sha)
        elif kind == "attempt-review-set":
            if str(receipt.get("attempt_submission_receipt_sha256") or "") not in seen_submissions:
                errors.append("attempt-review-missing-prior-submission")
            seen_reviews.add(receipt_sha)
        elif kind == "attempt-rebuttal-preparation":
            if str(receipt.get("attempt_submission_receipt_sha256") or "") not in seen_submissions:
                errors.append("attempt-rebuttal-missing-prior-submission")
            if str(receipt.get("attempt_review_set_sha256") or "") not in seen_reviews:
                errors.append("attempt-rebuttal-missing-prior-review-set")
            seen_rebuttals.add(receipt_sha)
        elif kind == "attempt-venue-decision":
            if str(receipt.get("attempt_submission_receipt_sha256") or "") not in seen_submissions:
                errors.append("attempt-decision-missing-prior-submission")
            phase = str(receipt.get("decision_phase") or "")
            rebuttal_sha = str(receipt.get("attempt_rebuttal_receipt_sha256") or "")
            if phase == "POST_REBUTTAL" and rebuttal_sha not in seen_rebuttals:
                errors.append("attempt-decision-missing-prior-rebuttal")
            if phase == "PRE_REBUTTAL_TERMINAL" and rebuttal_sha:
                errors.append("attempt-terminal-decision-must-not-bind-rebuttal")
            seen_decisions[receipt_sha] = phase
        elif kind == "attempt-rebuttal-skipped-by-venue":
            decision_sha = str(receipt.get("attempt_venue_decision_sha256") or "")
            if str(receipt.get("attempt_submission_receipt_sha256") or "") not in seen_submissions:
                errors.append("attempt-skip-missing-prior-submission")
            if seen_decisions.get(decision_sha) != "PRE_REBUTTAL_TERMINAL":
                errors.append("attempt-skip-missing-prior-terminal-decision")
            seen_skip_decisions.add(decision_sha)
        elif kind == "attempt-post-decision-learning":
            decision_sha = str(receipt.get("attempt_venue_decision_sha256") or "")
            if decision_sha not in seen_decisions:
                errors.append("attempt-learning-missing-prior-decision")
            if seen_decisions.get(decision_sha) == "PRE_REBUTTAL_TERMINAL" and decision_sha not in seen_skip_decisions:
                errors.append("attempt-learning-terminal-decision-missing-skip-receipt")
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


def _paper_submission_lock_path(root: Path, paper_id: str) -> Path:
    directory = Path(root) / "paper-submission-attempt-workflows" / ".paper-submission-locks"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{_slug(paper_id)}.lock"


def _append_attempt_workflow_receipt_unlocked(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
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


def append_attempt_workflow_receipt(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not _validator(receipt):
        raise RuntimeError("invalid attempt workflow receipt")
    if receipt.get("receipt_type") != "attempt-actual-submission":
        return _append_attempt_workflow_receipt_unlocked(root, receipt)

    paper_id = str(receipt.get("paper_id") or "")
    attempt_id = str(receipt.get("attempt_id") or "")
    path, _ = _path(root, attempt_id)
    paper_lock = _paper_submission_lock_path(root, paper_id)
    with paper_lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        if not path.exists():
            raise RuntimeError("attempt workflow ledger missing before actual submission")
        row = json.loads(path.read_text(encoding="utf-8"))
        guard_sha = str(receipt.get("attempt_submission_conflict_guard_sha256") or "")
        guard = next((
            event.get("receipt") or {}
            for event in reversed(row.get("events") or [])
            if isinstance(event, Mapping)
            and event.get("event_type") == "attempt-submission-conflict-guard"
            and isinstance(event.get("receipt"), Mapping)
            and str((event.get("receipt") or {}).get("attempt_submission_conflict_guard_sha256") or "") == guard_sha
        ), {})
        if not guard:
            raise RuntimeError("actual child submission missing prior conflict guard receipt")
        guard_errors = verify_attempt_submission_conflict_guard_current(root=root, workflow_ledger=row, guard_receipt=guard)
        if guard_errors:
            raise RuntimeError("attempt submission conflict guard stale or blocked: " + ",".join(guard_errors))
        return _append_attempt_workflow_receipt_unlocked(root, receipt)


def current_attempt_workflow_summary(row: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_attempt_workflow_ledger(row)
    preparations = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-preparation"]
    freezes = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-freeze"]
    handoffs = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-handoff"]
    signoffs = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-human-signoff"]
    guards = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-submission-conflict-guard"]
    submissions = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-actual-submission"]
    reviews = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-review-set"]
    rebuttals = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-rebuttal-preparation"]
    decisions = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-venue-decision"]
    skips = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-rebuttal-skipped-by-venue"]
    learnings = [event.get("receipt") or {} for event in row.get("events") or [] if isinstance(event, Mapping) and event.get("event_type") == "attempt-post-decision-learning"]
    preparation = preparations[-1] if preparations else {}; freeze = freezes[-1] if freezes else {}; handoff = handoffs[-1] if handoffs else {}
    signoff = signoffs[-1] if signoffs else {}; guard = guards[-1] if guards else {}; submission = submissions[-1] if submissions else {}; review = reviews[-1] if reviews else {}
    rebuttal = rebuttals[-1] if rebuttals else {}; decision = decisions[-1] if decisions else {}; skip = skips[-1] if skips else {}; learning = learnings[-1] if learnings else {}
    drift = verify_frozen_artifacts(freeze) if freeze else []
    freeze_current = bool(freeze) and not drift
    handoff_current = bool(handoff) and freeze_current and handoff.get("attempt_freeze_sha256") == freeze.get("attempt_freeze_sha256")
    signoff_current = bool(signoff) and handoff_current and signoff.get("attempt_handoff_sha256") == handoff.get("attempt_handoff_sha256") and signoff.get("attempt_freeze_sha256") == freeze.get("attempt_freeze_sha256")
    submission_valid = bool(submission) and validate_attempt_actual_submission(submission) and bool(signoff) and submission.get("attempt_signoff_sha256") == signoff.get("attempt_signoff_sha256")
    from .submission_attempt_post_submission import (
        validate_attempt_learning_packet, validate_attempt_rebuttal_preparation, validate_attempt_rebuttal_skipped,
        validate_attempt_review_set, validate_attempt_venue_decision,
    )
    review_valid = bool(review) and validate_attempt_review_set(review) and submission_valid and review.get("attempt_submission_receipt_sha256") == submission.get("attempt_submission_receipt_sha256")
    rebuttal_valid = bool(rebuttal) and rebuttal.get("pass") is True and validate_attempt_rebuttal_preparation(rebuttal) and review_valid and rebuttal.get("attempt_review_set_sha256") == review.get("attempt_review_set_sha256")
    decision_valid = bool(decision) and validate_attempt_venue_decision(decision) and submission_valid and decision.get("attempt_submission_receipt_sha256") == submission.get("attempt_submission_receipt_sha256")
    skip_valid = bool(skip) and validate_attempt_rebuttal_skipped(skip) and decision_valid and skip.get("attempt_venue_decision_sha256") == decision.get("attempt_venue_decision_sha256")
    learning_valid = bool(learning) and learning.get("pass") is True and validate_attempt_learning_packet(learning) and decision_valid and learning.get("attempt_venue_decision_sha256") == decision.get("attempt_venue_decision_sha256")
    if errors:
        status = "ATTEMPT_WORKFLOW_INVALID"
    elif learning_valid:
        status = "ATTEMPT_POST_DECISION_LEARN_COMPLETE"
    elif decision_valid:
        status = "ATTEMPT_TERMINAL_DECISION_SKIP_PENDING" if decision.get("decision_phase") == "PRE_REBUTTAL_TERMINAL" and not skip_valid else "ATTEMPT_FINAL_DECISION_LEARNING_PENDING"
    elif rebuttal_valid:
        status = "ATTEMPT_REBUTTAL_PREPARED_DECISION_PENDING"
    elif review_valid:
        status = "ATTEMPT_VENUE_REVIEWS_RECORDED"
    elif submission_valid:
        status = "ATTEMPT_VENUE_SUBMISSION_CONFIRMED"
    elif signoff_current and guard and guard.get("pass") is False:
        status = "ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING"
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
        "submission_conflict_guard_sha256": str(guard.get("attempt_submission_conflict_guard_sha256") or ""),
        "submission_conflict_guard_status": str(guard.get("status") or ""),
        "submission_conflict_count": len(guard.get("active_conflicts") or []),
        "submission_receipt_sha256": str(submission.get("attempt_submission_receipt_sha256") or ""),
        "venue_submission_id": str(submission.get("venue_submission_id") or ""),
        "submitted_at": str(submission.get("submitted_at") or ""),
        "frozen_artifacts": len(freeze.get("frozen_artifacts") or []),
        "freeze_drift_errors": drift,
        "validation_errors": errors,
        "parent_submission_bytes_immutable": True,
        "human_confirmation_status": str(signoff.get("status") or handoff.get("human_confirmation_status") or ""),
        "actual_submission_status": str(submission.get("actual_submission_status") or "NOT_SUBMITTED"),
        "review_set_sha256": str(review.get("attempt_review_set_sha256") or ""),
        "review_count": int(review.get("review_count") or 0),
        "rebuttal_receipt_sha256": str(rebuttal.get("attempt_rebuttal_receipt_sha256") or ""),
        "rebuttal_missing_decisive_evidence": int((rebuttal.get("summary") or {}).get("missing_decisive_evidence") or 0) if isinstance(rebuttal.get("summary"), Mapping) else 0,
        "rebuttal_new_claim_requests": int((rebuttal.get("summary") or {}).get("new_claim_requests") or 0) if isinstance(rebuttal.get("summary"), Mapping) else 0,
        "venue_decision_sha256": str(decision.get("attempt_venue_decision_sha256") or ""),
        "venue_decision": str(decision.get("decision") or ""),
        "decision_phase": str(decision.get("decision_phase") or ""),
        "rebuttal_skip_sha256": str(skip.get("attempt_rebuttal_skip_sha256") or ""),
        "learning_receipt_sha256": str(learning.get("attempt_learning_receipt_sha256") or ""),
        "learning_lessons": int((learning.get("summary") or {}).get("lessons") or 0) if isinstance(learning.get("summary"), Mapping) else 0,
        "learning_scientific_diagnostic_only": int((learning.get("summary") or {}).get("scientific_diagnostic_only") or 0) if isinstance(learning.get("summary"), Mapping) else 0,
        "authority": dict(ZERO_AUTHORITY),
    }
