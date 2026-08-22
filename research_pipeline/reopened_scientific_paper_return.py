from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .reopened_child_claim_audit import public_child_claim_audit
from .reopened_child_claim_expansion_authorization import public_child_claim_expansion_authorization
from .reopened_child_paper_contract import public_child_paper_contract
from .reopened_scientific_evidence_paper_handoff import public_scientific_evidence_paper_handoff
from .submission_attempt_lineage import validate_attempt_plan
from .submission_attempt_workflow import current_attempt_workflow_summary, validate_attempt_workflow_ledger


def _find_attempt(root: Path, attempt_sha256: str) -> dict[str, Any]:
    directory = Path(root) / "paper-submission-attempts"
    if not directory.exists():
        return {}
    for path in sorted(directory.glob("*.json")):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for event in row.get("events") or []:
            receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(receipt, Mapping) and receipt.get("attempt_sha256") == attempt_sha256 and validate_attempt_plan(receipt):
                return dict(receipt)
    return {}


def _workflow(root: Path, attempt: Mapping[str, Any]) -> dict[str, Any]:
    attempt_id = str(attempt.get("attempt_id") or "")
    if not attempt_id:
        return {"status": "ATTEMPT_WORKFLOW_NOT_STARTED", "validation_errors": []}
    path = Path(root) / "paper-submission-attempt-workflows" / f"{attempt_id}.json"
    if not path.exists():
        return {"status": "ATTEMPT_WORKFLOW_NOT_STARTED", "validation_errors": []}
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "ATTEMPT_WORKFLOW_INVALID", "validation_errors": ["workflow-unreadable"]}
    errors = validate_attempt_workflow_ledger(row)
    if errors:
        return {"status": "ATTEMPT_WORKFLOW_INVALID", "validation_errors": errors}
    return current_attempt_workflow_summary(row)


def public_scientific_paper_return_state(root: Path, attempt_sha256: str) -> dict[str, Any]:
    root = Path(root)
    attempt = _find_attempt(root, attempt_sha256)
    handoff = public_scientific_evidence_paper_handoff(root, attempt_sha256)
    audit = public_child_claim_audit(root, attempt_sha256)
    expansion = public_child_claim_expansion_authorization(root, attempt_sha256)
    child_contract = public_child_paper_contract(root, attempt_sha256)
    workflow = _workflow(root, attempt)
    if not attempt:
        status = "SCIENTIFIC_PAPER_RETURN_ATTEMPT_NOT_FOUND"
    elif workflow.get("status") == "ATTEMPT_WORKFLOW_INVALID":
        status = "SCIENTIFIC_PAPER_RETURN_ATTEMPT_WORKFLOW_INVALID"
    elif workflow.get("status") not in {"ATTEMPT_WORKFLOW_NOT_STARTED", "NOT_ELIGIBLE", ""} and child_contract.get("status") == "CHILD_PAPER_CONTRACT_REVISION_FROZEN_PREPARATION_REVIEW_REQUIRED":
        status = "SCIENTIFIC_REOPEN_RESOLVED_RETURNED_TO_ATTEMPT_WORKFLOW"
    elif child_contract.get("status") == "CHILD_PAPER_CONTRACT_REVISION_FROZEN_PREPARATION_REVIEW_REQUIRED":
        status = "SCIENTIFIC_REOPEN_CHILD_PAPER_CONTRACT_FROZEN_PREPARATION_REQUIRED"
    elif expansion.get("status") == "CHILD_NEW_CLAIM_HUMAN_EXPANSION_AUTHORIZED_CONTRACT_REVISION_REQUIRED":
        status = "CHILD_NEW_CLAIM_HUMAN_EXPANSION_AUTHORIZED_CONTRACT_REVISION_REQUIRED"
    elif expansion.get("status") == "CHILD_CLAIM_EXPANSION_AUTHORITY_LEDGER_INVALID":
        status = "CHILD_CLAIM_EXPANSION_AUTHORITY_LEDGER_INVALID"
    elif audit.get("status") == "CHILD_CLAIM_AUDIT_PASS_PAPER_CONTRACT_REVISION_REQUIRED":
        status = "SCIENTIFIC_REOPEN_CHILD_CLAIM_AUDIT_PASS_CONTRACT_REVISION_REQUIRED"
    elif audit.get("status") in {"CHILD_CLAIM_AUDIT_HOLD_NEW_CLAIM_AUTHORITY_REQUIRED", "CHILD_CLAIM_AUDIT_BLOCKED", "CHILD_CLAIM_AUDIT_LEDGER_INVALID"}:
        status = str(audit.get("status"))
    elif handoff.get("status") == "SCIENTIFIC_REOPEN_EVIDENCE_READY_CHILD_CLAIM_AUDIT_REQUIRED":
        status = "SCIENTIFIC_REOPEN_EVIDENCE_READY_CHILD_CLAIM_AUDIT_REQUIRED"
    elif handoff.get("status") == "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_LEDGER_INVALID":
        status = "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_LEDGER_INVALID"
    else:
        status = "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_REQUIRED"
    return {
        "status": status,
        "paper_id": str(attempt.get("paper_id") or ""),
        "attempt_id": str(attempt.get("attempt_id") or ""),
        "attempt_sha256": attempt_sha256,
        "requires_explicit_scientific_reopen": attempt.get("requires_explicit_scientific_reopen") is True,
        "paper_revision_handoff_sha256": str(handoff.get("paper_revision_handoff_sha256") or ""),
        "child_claim_audit_sha256": str(audit.get("child_claim_audit_sha256") or ""),
        "child_paper_contract_sha256": str(child_contract.get("child_paper_contract_sha256") or ""),
        "candidate_claims": int(handoff.get("candidate_claims") or 0),
        "supported_claims": int(audit.get("supported_claims") or 0),
        "held_new_claims": int(audit.get("held_new_claims") or 0),
        "approved_new_claims": int(expansion.get("approved_new_claims") or 0),
        "claim_expansion_authorization_sha256": str(expansion.get("authorization_sha256") or ""),
        "failed_claims": int(audit.get("failed_claims") or 0),
        "attempt_workflow_status": str(workflow.get("status") or "ATTEMPT_WORKFLOW_NOT_STARTED"),
        "parent_submission_bytes_immutable": True,
        "parent_claim_update_authorized": False,
        "new_claim_expansion_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
        "validation_errors": list(workflow.get("validation_errors") or []),
    }
