from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .submission_attempt_lineage import validate_attempt_plan

SCHEMA_VERSION = "1.0"
ZERO_AUTHORITY = {"scientific": False, "experiment": False, "gpu": False, "submission": False}
PROPOSAL_STATUS = "SCIENTIFIC_REOPEN_PROPOSED_EXTERNAL_AUTHORITY_REQUIRED"
AUTHORIZED_STATUS = "EXTERNAL_SCIENTIFIC_REOPEN_CONFIRMED_NEW_CONTRACT_REQUIRED"
AUTHORIZATION_SCOPE = "CREATE_NEW_SCIENTIFIC_CONTRACT_ONLY"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:160] or "unknown-paper"


def proposal_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "attempt_id": receipt.get("attempt_id"),
        "attempt_sha256": receipt.get("attempt_sha256"),
        "attempt_type": receipt.get("attempt_type"),
        "target_venue": receipt.get("target_venue"),
        "revision_categories": receipt.get("revision_categories") or [],
        "new_claim_requested": receipt.get("new_claim_requested"),
        "new_experiment_requested": receipt.get("new_experiment_requested"),
        "new_scientific_evidence_requested": receipt.get("new_scientific_evidence_requested"),
        "scientific_interpretation_change_requested": receipt.get("scientific_interpretation_change_requested"),
        "parent_submission_receipt_sha256": receipt.get("parent_submission_receipt_sha256"),
        "parent_venue_decision_sha256": receipt.get("parent_venue_decision_sha256"),
        "parent_learning_receipt_sha256": receipt.get("parent_learning_receipt_sha256"),
        "status": receipt.get("status"),
        "new_scientific_contract_required": receipt.get("new_scientific_contract_required"),
        "existing_scientific_contract_immutable": receipt.get("existing_scientific_contract_immutable"),
    }


def build_scientific_reopen_proposal(attempt_plan: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_attempt_plan(attempt_plan):
        raise RuntimeError("invalid submission attempt plan")
    if attempt_plan.get("requires_explicit_scientific_reopen") is not True or attempt_plan.get("machine_preparation_eligible") is not False:
        raise RuntimeError("paper-side-only attempt must not create a scientific reopen proposal")
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "scientific-reopen-proposal",
        "paper_id": str(attempt_plan.get("paper_id") or ""),
        "contract_sha256": str(attempt_plan.get("contract_sha256") or ""),
        "attempt_id": str(attempt_plan.get("attempt_id") or ""),
        "attempt_sha256": str(attempt_plan.get("attempt_sha256") or ""),
        "attempt_type": str(attempt_plan.get("attempt_type") or ""),
        "target_venue": str(attempt_plan.get("target_venue") or ""),
        "revision_categories": list(attempt_plan.get("revision_categories") or []),
        "new_claim_requested": attempt_plan.get("new_claim_requested") is True,
        "new_experiment_requested": attempt_plan.get("new_experiment_requested") is True,
        "new_scientific_evidence_requested": attempt_plan.get("new_scientific_evidence_requested") is True,
        "scientific_interpretation_change_requested": attempt_plan.get("scientific_interpretation_change_requested") is True,
        "parent_submission_receipt_sha256": str(attempt_plan.get("parent_submission_receipt_sha256") or ""),
        "parent_venue_decision_sha256": str(attempt_plan.get("parent_venue_decision_sha256") or ""),
        "parent_learning_receipt_sha256": str(attempt_plan.get("parent_learning_receipt_sha256") or ""),
        "status": PROPOSAL_STATUS,
        "new_scientific_contract_required": True,
        "existing_scientific_contract_immutable": True,
        "automatic_reopen_authorized": False,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "new_scientific_evidence_authorized": False,
        "scientific_interpretation_change_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["scientific_reopen_proposal_sha256"] = _digest(proposal_identity(receipt))
    return receipt


def validate_scientific_reopen_proposal(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "scientific-reopen-proposal" or receipt.get("status") != PROPOSAL_STATUS:
        return False
    if receipt.get("new_scientific_contract_required") is not True or receipt.get("existing_scientific_contract_immutable") is not True:
        return False
    if receipt.get("automatic_reopen_authorized") is not False:
        return False
    if receipt.get("claim_expansion_authorized") is not False or receipt.get("new_experiment_authorized") is not False:
        return False
    if receipt.get("new_scientific_evidence_authorized") is not False or receipt.get("scientific_interpretation_change_authorized") is not False:
        return False
    if not receipt.get("attempt_sha256") or not receipt.get("contract_sha256"):
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("scientific_reopen_proposal_sha256") or "") == _digest(proposal_identity(receipt))


def authorization_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "attempt_sha256": receipt.get("attempt_sha256"),
        "scientific_reopen_proposal_sha256": receipt.get("scientific_reopen_proposal_sha256"),
        "authorization_scope": receipt.get("authorization_scope"),
        "external_scientific_authority_ref_sha256": receipt.get("external_scientific_authority_ref_sha256"),
        "authorized_at": receipt.get("authorized_at"),
        "status": receipt.get("status"),
        "new_scientific_contract_required": receipt.get("new_scientific_contract_required"),
        "existing_scientific_contract_immutable": receipt.get("existing_scientific_contract_immutable"),
    }


def build_scientific_reopen_authorization(
    *,
    proposal: Mapping[str, Any],
    external_scientific_authority_ref: str,
    authorized_at: str,
) -> dict[str, Any]:
    if not validate_scientific_reopen_proposal(proposal):
        raise RuntimeError("valid scientific reopen proposal required")
    authority_ref = str(external_scientific_authority_ref or "").strip()
    if not authority_ref:
        raise RuntimeError("external scientific authority reference required")
    authorized_at = str(authorized_at or "").strip()
    if not authorized_at:
        raise RuntimeError("scientific reopen authorization timestamp required")
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "scientific-reopen-authorization",
        "paper_id": str(proposal.get("paper_id") or ""),
        "contract_sha256": str(proposal.get("contract_sha256") or ""),
        "attempt_id": str(proposal.get("attempt_id") or ""),
        "attempt_sha256": str(proposal.get("attempt_sha256") or ""),
        "scientific_reopen_proposal_sha256": str(proposal.get("scientific_reopen_proposal_sha256") or ""),
        "authorization_scope": AUTHORIZATION_SCOPE,
        "external_scientific_authority_ref": authority_ref,
        "external_scientific_authority_ref_sha256": hashlib.sha256(authority_ref.encode()).hexdigest(),
        "authorized_at": authorized_at,
        "status": AUTHORIZED_STATUS,
        "external_scientific_authority_confirmed": True,
        "new_scientific_contract_required": True,
        "existing_scientific_contract_immutable": True,
        "old_contract_claim_status_unchanged": True,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "new_scientific_evidence_authorized": False,
        "scientific_interpretation_change_authorized": False,
        "gpu_execution_authorized": False,
        "automatic_contract_creation_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["scientific_reopen_authorization_sha256"] = _digest(authorization_identity(receipt))
    return receipt


def validate_scientific_reopen_authorization(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "scientific-reopen-authorization" or receipt.get("status") != AUTHORIZED_STATUS:
        return False
    if receipt.get("authorization_scope") != AUTHORIZATION_SCOPE or receipt.get("external_scientific_authority_confirmed") is not True:
        return False
    authority_ref = str(receipt.get("external_scientific_authority_ref") or "")
    if not authority_ref or hashlib.sha256(authority_ref.encode()).hexdigest() != str(receipt.get("external_scientific_authority_ref_sha256") or ""):
        return False
    if receipt.get("new_scientific_contract_required") is not True or receipt.get("existing_scientific_contract_immutable") is not True:
        return False
    if receipt.get("old_contract_claim_status_unchanged") is not True or receipt.get("automatic_contract_creation_authorized") is not False:
        return False
    if receipt.get("claim_expansion_authorized") is not False or receipt.get("new_experiment_authorized") is not False:
        return False
    if receipt.get("new_scientific_evidence_authorized") is not False or receipt.get("scientific_interpretation_change_authorized") is not False:
        return False
    if receipt.get("gpu_execution_authorized") is not False:
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("scientific_reopen_authorization_sha256") or "") == _digest(authorization_identity(receipt))


def _paths(root: Path, paper_id: str) -> tuple[Path, Path]:
    directory = Path(root) / "paper-scientific-reopen"
    directory.mkdir(parents=True, exist_ok=True)
    stem = _slug(paper_id)
    return directory / f"{stem}.json", directory / f".{stem}.lock"


def validate_scientific_reopen_ledger(row: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    paper_id = str(row.get("paper_id") or "")
    if not paper_id:
        errors.append("scientific-reopen-paper-id-missing")
    if (row.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("scientific-reopen-ledger-authority-leak")
    proposals: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()
    for index, event in enumerate(row.get("events") or []):
        if not isinstance(event, Mapping):
            errors.append("scientific-reopen-event-not-object")
            continue
        receipt = event.get("receipt") or {}
        if not isinstance(receipt, Mapping):
            errors.append("scientific-reopen-receipt-not-object")
            continue
        receipt_type = str(receipt.get("receipt_type") or "")
        if receipt_type == "scientific-reopen-proposal":
            valid = validate_scientific_reopen_proposal(receipt)
            receipt_sha = str(receipt.get("scientific_reopen_proposal_sha256") or "")
            expected_type = "scientific-reopen-proposal"
            if valid:
                proposals[receipt_sha] = dict(receipt)
        elif receipt_type == "scientific-reopen-authorization":
            valid = validate_scientific_reopen_authorization(receipt)
            receipt_sha = str(receipt.get("scientific_reopen_authorization_sha256") or "")
            expected_type = "scientific-reopen-authorization"
            proposal_sha = str(receipt.get("scientific_reopen_proposal_sha256") or "")
            proposal = proposals.get(proposal_sha)
            if proposal is None:
                errors.append("scientific-reopen-authorization-missing-prior-proposal")
            elif str(proposal.get("attempt_sha256") or "") != str(receipt.get("attempt_sha256") or ""):
                errors.append("scientific-reopen-authorization-attempt-mismatch")
        else:
            errors.append("scientific-reopen-event-type-invalid")
            continue
        if not valid:
            errors.append("scientific-reopen-receipt-invalid")
        if event.get("event_type") != expected_type:
            errors.append("scientific-reopen-event-type-mismatch")
        if str(receipt.get("paper_id") or "") != paper_id:
            errors.append("scientific-reopen-paper-id-mismatch")
        if receipt_sha in seen:
            errors.append("scientific-reopen-duplicate-receipt")
        expected_event_id = _digest([paper_id, index, expected_type, receipt_sha, str(event.get("recorded_at") or "")])[:24]
        if str(event.get("event_id") or "") != expected_event_id:
            errors.append("scientific-reopen-event-id-invalid")
        if any(event.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
            errors.append("scientific-reopen-event-authority-leak")
        seen.add(receipt_sha)
    return list(dict.fromkeys(errors))


def publish_scientific_reopen_receipt(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    receipt_type = str(receipt.get("receipt_type") or "")
    if receipt_type == "scientific-reopen-proposal":
        valid = validate_scientific_reopen_proposal(receipt)
        receipt_sha = str(receipt.get("scientific_reopen_proposal_sha256") or "")
    elif receipt_type == "scientific-reopen-authorization":
        valid = validate_scientific_reopen_authorization(receipt)
        receipt_sha = str(receipt.get("scientific_reopen_authorization_sha256") or "")
    else:
        raise RuntimeError("unsupported scientific reopen receipt type")
    if not valid:
        raise RuntimeError("invalid scientific reopen receipt")
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
            if not isinstance(prior, Mapping):
                continue
            prior_sha = str(prior.get("scientific_reopen_proposal_sha256") or prior.get("scientific_reopen_authorization_sha256") or "")
            if prior_sha == receipt_sha:
                return row
        if receipt_type == "scientific-reopen-authorization":
            proposal_sha = str(receipt.get("scientific_reopen_proposal_sha256") or "")
            prior_proposals = {
                str((event.get("receipt") or {}).get("scientific_reopen_proposal_sha256") or "")
                for event in row.get("events") or []
                if isinstance(event, Mapping) and isinstance(event.get("receipt"), Mapping) and (event.get("receipt") or {}).get("receipt_type") == "scientific-reopen-proposal"
            }
            if proposal_sha not in prior_proposals:
                raise RuntimeError("scientific reopen authorization requires a previously published proposal")
        recorded_at = str(receipt.get("authorized_at") or _now())
        event = {
            "event_type": receipt_type,
            "receipt": dict(receipt),
            "recorded_at": recorded_at,
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        event["event_id"] = _digest([paper_id, len(row.get("events") or []), receipt_type, receipt_sha, recorded_at])[:24]
        row.setdefault("events", []).append(event)
        row["updated_at"] = recorded_at
        errors = validate_scientific_reopen_ledger(row)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return row


def public_scientific_reopen_summary(row: Mapping[str, Any], attempt_sha256: str = "") -> dict[str, Any]:
    errors = validate_scientific_reopen_ledger(row)
    proposals = [
        event.get("receipt") or {}
        for event in row.get("events") or []
        if isinstance(event, Mapping) and event.get("event_type") == "scientific-reopen-proposal" and isinstance(event.get("receipt"), Mapping)
    ]
    if attempt_sha256:
        proposals = [receipt for receipt in proposals if str(receipt.get("attempt_sha256") or "") == attempt_sha256]
    proposal = proposals[-1] if proposals else {}
    authorizations = [
        event.get("receipt") or {}
        for event in row.get("events") or []
        if isinstance(event, Mapping) and event.get("event_type") == "scientific-reopen-authorization" and isinstance(event.get("receipt"), Mapping)
        and (not proposal or str((event.get("receipt") or {}).get("scientific_reopen_proposal_sha256") or "") == str(proposal.get("scientific_reopen_proposal_sha256") or ""))
    ]
    authorization = authorizations[-1] if authorizations else {}
    if errors:
        status = "SCIENTIFIC_REOPEN_LEDGER_INVALID"
    elif authorization:
        status = AUTHORIZED_STATUS
    elif proposal:
        status = PROPOSAL_STATUS
    else:
        status = "SCIENTIFIC_REOPEN_PROPOSAL_REQUIRED"
    return {
        "status": status,
        "paper_id": str(row.get("paper_id") or ""),
        "attempt_sha256": str(proposal.get("attempt_sha256") or attempt_sha256 or ""),
        "proposal_sha256": str(proposal.get("scientific_reopen_proposal_sha256") or ""),
        "authorization_sha256": str(authorization.get("scientific_reopen_authorization_sha256") or ""),
        "authorization_scope": str(authorization.get("authorization_scope") or ""),
        "external_scientific_authority_confirmed": authorization.get("external_scientific_authority_confirmed") is True,
        "new_scientific_contract_required": bool(proposal) or bool(authorization),
        "existing_scientific_contract_immutable": True,
        "automatic_contract_creation_authorized": False,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "gpu_execution_authorized": False,
        "validation_errors": errors,
        "authority": dict(ZERO_AUTHORITY),
    }
