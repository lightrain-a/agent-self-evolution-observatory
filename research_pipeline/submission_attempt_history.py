from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .submission_attempt_lineage import validate_attempt_ledger
from .submission_attempt_workflow import current_attempt_workflow_summary, validate_attempt_workflow_ledger


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def empty_history(paper_id: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "attempts": [],
        "summary": {
            "attempts": 0,
            "resubmissions": 0,
            "camera_ready": 0,
            "machine_preparation_eligible": 0,
            "requires_explicit_scientific_reopen": 0,
            "human_signoffs": 0,
            "submission_conflict_blocks": 0,
            "venue_submissions": 0,
            "review_sets": 0,
            "rebuttals_prepared": 0,
            "rebuttals_skipped_by_venue": 0,
            "final_decisions": 0,
            "post_decision_learn_complete": 0,
            "active_or_pending": 0,
            "invalid_attempts": 0,
        },
        "latest_attempt_id": "",
        "latest_attempt_sha256": "",
        "validation_errors": [],
        "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
    }
    payload["history_sha256"] = _digest(payload)
    return payload


def build_attempt_history(paper_id: str, attempt_root: Path | None, workflow_root: Path | None) -> dict[str, Any]:
    if attempt_root is None:
        return empty_history(paper_id)
    ledger_path = attempt_root / f"{paper_id}.json"
    if not ledger_path.exists():
        return empty_history(paper_id)
    try:
        ledger = _load(ledger_path)
    except (OSError, json.JSONDecodeError):
        payload = empty_history(paper_id)
        payload["validation_errors"] = ["attempt-ledger-unreadable"]
        payload["history_sha256"] = _digest({key: value for key, value in payload.items() if key != "history_sha256"})
        return payload
    ledger_errors = validate_attempt_ledger(ledger)
    rows: list[dict[str, Any]] = []
    sha_to_id: dict[str, str] = {}
    for event in ledger.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if not isinstance(receipt, Mapping):
            continue
        attempt_id = str(receipt.get("attempt_id") or "")
        attempt_sha = str(receipt.get("attempt_sha256") or "")
        workflow_summary: dict[str, Any] = {
            "status": "ATTEMPT_WORKFLOW_NOT_STARTED" if receipt.get("machine_preparation_eligible") is True else "NOT_ELIGIBLE",
            "attempt_sha256": attempt_sha,
            "signoff_sha256": "",
            "submission_conflict_guard_status": "",
            "submission_conflict_count": 0,
            "actual_submission_status": "NOT_SUBMITTED",
            "venue_submission_id": "",
            "review_count": 0,
            "rebuttal_receipt_sha256": "",
            "rebuttal_skip_sha256": "",
            "venue_decision_sha256": "",
            "venue_decision": "",
            "learning_receipt_sha256": "",
            "validation_errors": [],
        }
        if workflow_root is not None and attempt_id:
            path = workflow_root / f"{attempt_id}.json"
            if path.exists():
                try:
                    workflow = _load(path)
                    workflow_errors = validate_attempt_workflow_ledger(workflow)
                    workflow_summary = {**workflow_summary, **current_attempt_workflow_summary(workflow)}
                    if workflow_errors:
                        workflow_summary["status"] = "ATTEMPT_WORKFLOW_INVALID"
                        workflow_summary["validation_errors"] = workflow_errors
                    if str(workflow_summary.get("attempt_sha256") or "") != attempt_sha:
                        workflow_summary["status"] = "ATTEMPT_WORKFLOW_INVALID"
                        workflow_summary["validation_errors"] = list(dict.fromkeys(list(workflow_summary.get("validation_errors") or []) + ["attempt-history-workflow-plan-sha-mismatch"]))
                except (OSError, json.JSONDecodeError, TypeError, ValueError):
                    workflow_summary["status"] = "ATTEMPT_WORKFLOW_INVALID"
                    workflow_summary["validation_errors"] = ["attempt-workflow-ledger-unreadable"]
        row = {
            "attempt_id": attempt_id,
            "attempt_sha256": attempt_sha,
            "parent_attempt_sha256": str(receipt.get("parent_attempt_sha256") or ""),
            "parent_attempt_id": "",
            "attempt_type": str(receipt.get("attempt_type") or ""),
            "target_venue": str(receipt.get("target_venue") or ""),
            "plan_status": str(receipt.get("status") or ""),
            "machine_preparation_eligible": receipt.get("machine_preparation_eligible") is True,
            "requires_explicit_scientific_reopen": receipt.get("requires_explicit_scientific_reopen") is True,
            "parent_submission_bytes_immutable": receipt.get("parent_submission_bytes_immutable") is True,
            "workflow_status": str(workflow_summary.get("status") or ""),
            "human_signoff_recorded": bool(workflow_summary.get("signoff_sha256")),
            "submission_conflict_blocked": str(workflow_summary.get("submission_conflict_guard_status") or "") == "ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING",
            "submission_conflict_count": int(workflow_summary.get("submission_conflict_count") or 0),
            "venue_submitted": workflow_summary.get("actual_submission_status") == "SUBMITTED",
            "venue_submission_id": str(workflow_summary.get("venue_submission_id") or ""),
            "review_count": int(workflow_summary.get("review_count") or 0),
            "rebuttal_prepared": bool(workflow_summary.get("rebuttal_receipt_sha256")),
            "rebuttal_skipped_by_venue": bool(workflow_summary.get("rebuttal_skip_sha256")),
            "final_decision": str(workflow_summary.get("venue_decision") or ""),
            "final_decision_recorded": bool(workflow_summary.get("venue_decision_sha256")),
            "post_decision_learn_complete": str(workflow_summary.get("status") or "") == "ATTEMPT_POST_DECISION_LEARN_COMPLETE",
            "workflow_validation_errors": list(workflow_summary.get("validation_errors") or []),
        }
        rows.append(row)
        if attempt_sha:
            sha_to_id[attempt_sha] = attempt_id
    for row in rows:
        parent_sha = row["parent_attempt_sha256"]
        row["parent_attempt_id"] = sha_to_id.get(parent_sha, "") if parent_sha else ""
    invalid_statuses = {"ATTEMPT_WORKFLOW_INVALID", "ATTEMPT_HANDOFF_STALE", "ATTEMPT_FREEZE_STALE", "ATTEMPT_HUMAN_SIGNOFF_STALE"}
    summary = {
        "attempts": len(rows),
        "resubmissions": sum(row["attempt_type"] == "RESUBMISSION" for row in rows),
        "camera_ready": sum(row["attempt_type"] == "CAMERA_READY" for row in rows),
        "machine_preparation_eligible": sum(row["machine_preparation_eligible"] for row in rows),
        "requires_explicit_scientific_reopen": sum(row["requires_explicit_scientific_reopen"] for row in rows),
        "human_signoffs": sum(row["human_signoff_recorded"] for row in rows),
        "submission_conflict_blocks": sum(row["submission_conflict_blocked"] for row in rows),
        "venue_submissions": sum(row["venue_submitted"] for row in rows),
        "review_sets": sum(row["review_count"] > 0 for row in rows),
        "rebuttals_prepared": sum(row["rebuttal_prepared"] for row in rows),
        "rebuttals_skipped_by_venue": sum(row["rebuttal_skipped_by_venue"] for row in rows),
        "final_decisions": sum(row["final_decision_recorded"] for row in rows),
        "post_decision_learn_complete": sum(row["post_decision_learn_complete"] for row in rows),
        "active_or_pending": sum(not row["post_decision_learn_complete"] and not row["requires_explicit_scientific_reopen"] for row in rows),
        "invalid_attempts": sum(bool(row["workflow_validation_errors"]) or row["workflow_status"] in invalid_statuses for row in rows),
    }
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "attempts": rows,
        "summary": summary,
        "latest_attempt_id": rows[-1]["attempt_id"] if rows else "",
        "latest_attempt_sha256": rows[-1]["attempt_sha256"] if rows else "",
        "validation_errors": list(ledger_errors),
        "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
    }
    payload["history_sha256"] = _digest(payload)
    return payload
