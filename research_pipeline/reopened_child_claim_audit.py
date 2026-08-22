from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .reopened_scientific_evidence_paper_handoff import STATUS as HANDOFF_STATUS, validate_scientific_evidence_paper_handoff

SCHEMA_VERSION = "1.0"
AUDITOR_ROLE = "INDEPENDENT_CHILD_PAPER_CLAIM_AUDITOR"
PASS_STATUS = "CHILD_CLAIM_AUDIT_PASS_PAPER_CONTRACT_REVISION_REQUIRED"
HOLD_STATUS = "CHILD_CLAIM_AUDIT_HOLD_NEW_CLAIM_AUTHORITY_REQUIRED"
BLOCK_STATUS = "CHILD_CLAIM_AUDIT_BLOCKED"
CHECKS = (
    "evidence_trace_pass",
    "scope_within_reopened_contract_pass",
    "method_principle_boundary_pass",
    "wording_evidence_compatible_pass",
)
ZERO_AUTHORITY = {"scientific": False, "claim_update": False, "paper_preparation": False, "submission": False, "experiment": False, "gpu": False}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown"


def audit_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "paper_id", "attempt_sha256", "paper_revision_handoff_sha256", "auditor_ref_sha256",
        "audited_at", "claim_decisions_sha256", "supported_claim_ids", "held_new_claim_ids",
        "failed_claim_ids", "status", "paper_contract_revision_eligible",
    )}


def build_child_claim_audit(*, handoff: Mapping[str, Any], audit_packet: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_scientific_evidence_paper_handoff(handoff) or handoff.get("status") != HANDOFF_STATUS:
        raise RuntimeError("valid scientific-evidence child paper handoff required")
    packet = dict(audit_packet or {})
    if _text(packet.get("auditor_role")) != AUDITOR_ROLE:
        raise RuntimeError("independent child-paper claim auditor role required")
    ref = _text(packet.get("auditor_ref")); at = _text(packet.get("audited_at"))
    if not ref or not at:
        raise RuntimeError("child claim auditor identity and timestamp required")
    input_rows = packet.get("claim_checks") or []
    if not isinstance(input_rows, list):
        raise RuntimeError("child claim audit claim_checks must be a list")
    by_id: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(input_rows):
        if not isinstance(row, Mapping):
            raise RuntimeError(f"claim check must be object: {index}")
        claim_id = _text(row.get("claim_id"))
        if not claim_id or claim_id in by_id:
            raise RuntimeError("claim checks require unique claim ids")
        if set(row.get("checks") or {}) != set(CHECKS):
            raise RuntimeError(f"claim checks must match required set exactly: {claim_id}")
        by_id[claim_id] = row
    candidates = list(handoff.get("candidate_claims") or [])
    candidate_ids = [_text(row.get("claim_id")) for row in candidates]
    if set(by_id) != set(candidate_ids):
        raise RuntimeError("claim audit must cover every candidate claim exactly once")

    decisions: list[dict[str, Any]] = []
    supported: list[str] = []; held_new: list[str] = []; failed: list[str] = []
    for claim in candidates:
        claim_id = _text(claim.get("claim_id")); relation = _text(claim.get("claim_relation")); source = by_id[claim_id]
        checks = {key: (source.get("checks") or {}).get(key) is True for key in CHECKS}
        failed_checks = [key for key in CHECKS if not checks[key]]
        if failed_checks:
            disposition = "NOT_PROMOTED_AUDIT_CHECK_FAILED"; failed.append(claim_id)
        elif relation == "NEW_CHILD_CLAIM":
            disposition = "HELD_NEW_CLAIM_HUMAN_EXPANSION_AUTHORITY_REQUIRED"; held_new.append(claim_id)
        else:
            disposition = "SUPPORTED_BY_REOPENED_EVIDENCE_PENDING_CHILD_PAPER_CONTRACT_REVISION"; supported.append(claim_id)
        decisions.append({
            "claim_id": claim_id,
            "claim_relation": relation,
            "evidence_role": _text(claim.get("evidence_role")),
            "checks": checks,
            "failed_checks": failed_checks,
            "disposition": disposition,
        })
    if failed:
        status = BLOCK_STATUS
    elif supported:
        status = PASS_STATUS
    else:
        status = HOLD_STATUS
    revision_eligible = status == PASS_STATUS
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "scientific-reopen-child-claim-audit",
        "paper_id": _text(handoff.get("paper_id")),
        "attempt_sha256": _text(handoff.get("attempt_sha256")),
        "reopened_contract_id": _text(handoff.get("reopened_contract_id")),
        "reopened_contract_sha256": _text(handoff.get("reopened_contract_sha256")),
        "paper_revision_handoff_sha256": _text(handoff.get("paper_revision_handoff_sha256")),
        "auditor_role": AUDITOR_ROLE,
        "auditor_ref": ref,
        "auditor_ref_sha256": hashlib.sha256(ref.encode()).hexdigest(),
        "audited_at": at,
        "claim_decisions": decisions,
        "claim_decisions_sha256": _digest(decisions),
        "supported_claim_ids": supported,
        "held_new_claim_ids": held_new,
        "failed_claim_ids": failed,
        "status": status,
        "claim_audit_passed": status == PASS_STATUS,
        "paper_contract_revision_eligible": revision_eligible,
        "human_claim_expansion_authority_required": bool(held_new),
        "new_claim_expansion_authorized": False,
        "claim_update_authorized": False,
        "paper_preparation_eligible": False,
        "submission_eligible": False,
        "parent_submitted_bytes_immutable": True,
        "parent_paper_claim_status_unchanged": True,
        "principle_proof_from_method_pass_forbidden": True,
        "scientific_authority": False,
        "paper_preparation_authority": False,
        "submission_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }
    receipt["child_claim_audit_sha256"] = _digest(audit_identity(receipt))
    if not validate_child_claim_audit(receipt):
        raise RuntimeError("generated child claim audit invalid")
    return receipt


def validate_child_claim_audit(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "scientific-reopen-child-claim-audit" or receipt.get("status") not in {PASS_STATUS, HOLD_STATUS, BLOCK_STATUS}:
        return False
    ref = _text(receipt.get("auditor_ref"))
    if not ref or hashlib.sha256(ref.encode()).hexdigest() != _text(receipt.get("auditor_ref_sha256")):
        return False
    decisions = receipt.get("claim_decisions") or []
    if not isinstance(decisions, list) or not decisions or _digest(decisions) != _text(receipt.get("claim_decisions_sha256")):
        return False
    supported = [row.get("claim_id") for row in decisions if row.get("disposition") == "SUPPORTED_BY_REOPENED_EVIDENCE_PENDING_CHILD_PAPER_CONTRACT_REVISION"]
    held = [row.get("claim_id") for row in decisions if row.get("disposition") == "HELD_NEW_CLAIM_HUMAN_EXPANSION_AUTHORITY_REQUIRED"]
    failed = [row.get("claim_id") for row in decisions if row.get("disposition") == "NOT_PROMOTED_AUDIT_CHECK_FAILED"]
    if supported != list(receipt.get("supported_claim_ids") or []) or held != list(receipt.get("held_new_claim_ids") or []) or failed != list(receipt.get("failed_claim_ids") or []):
        return False
    expected_status = BLOCK_STATUS if failed else PASS_STATUS if supported else HOLD_STATUS
    if receipt.get("status") != expected_status:
        return False
    if receipt.get("claim_audit_passed") is not (expected_status == PASS_STATUS) or receipt.get("paper_contract_revision_eligible") is not (expected_status == PASS_STATUS):
        return False
    if receipt.get("human_claim_expansion_authority_required") is not bool(held):
        return False
    if any(receipt.get(key) is not True for key in ("parent_submitted_bytes_immutable", "parent_paper_claim_status_unchanged", "principle_proof_from_method_pass_forbidden")):
        return False
    if any(receipt.get(key) is not False for key in (
        "new_claim_expansion_authorized", "claim_update_authorized", "paper_preparation_eligible", "submission_eligible",
        "scientific_authority", "paper_preparation_authority", "submission_authority", "experiment_authority", "gpu_authority",
    )):
        return False
    return _text(receipt.get("child_claim_audit_sha256")) == _digest(audit_identity(receipt))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "paper-scientific-claim-audits" else root / "paper-scientific-claim-audits"


def validate_child_claim_audit_ledger(ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []; seen: set[str] = set(); attempt_sha = _text(ledger.get("attempt_sha256"))
    if (ledger.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("child-claim-audit-ledger-authority-leak")
    for index, event in enumerate(ledger.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if not isinstance(receipt, Mapping) or not validate_child_claim_audit(receipt):
            errors.append("child-claim-audit-receipt-invalid"); continue
        if _text(receipt.get("attempt_sha256")) != attempt_sha:
            errors.append("child-claim-audit-attempt-lineage-mismatch")
        sha = _text(receipt.get("child_claim_audit_sha256"))
        if sha in seen:
            errors.append("child-claim-audit-duplicate")
        recorded = _text(event.get("recorded_at"))
        if _text(event.get("event_id")) != _digest([attempt_sha, index, sha, recorded])[:24]:
            errors.append("child-claim-audit-event-id-invalid")
        seen.add(sha)
    return list(dict.fromkeys(errors))


def publish_child_claim_audit(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_child_claim_audit(receipt):
        raise RuntimeError("invalid child claim audit")
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    attempt_sha = _text(receipt.get("attempt_sha256")); path = directory / f"{_slug(attempt_sha)}.json"; lock = directory / f".{_slug(attempt_sha)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ledger = json.loads(path.read_text()) if path.exists() else {"schema_version": SCHEMA_VERSION, "paper_id": _text(receipt.get("paper_id")), "attempt_sha256": attempt_sha, "events": [], "authority": dict(ZERO_AUTHORITY)}
        sha = _text(receipt.get("child_claim_audit_sha256"))
        for event in ledger.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _text(prior.get("child_claim_audit_sha256")) == sha:
                return ledger
        at = _text(receipt.get("audited_at")); event = {"event_type": "scientific-reopen-child-claim-audit", "receipt": dict(receipt), "recorded_at": at, "claim_update_authority": False, "submission_authority": False}
        event["event_id"] = _digest([attempt_sha, len(ledger.get("events") or []), sha, at])[:24]
        ledger.setdefault("events", []).append(event); ledger["updated_at"] = at
        errors = validate_child_claim_audit_ledger(ledger)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"); os.replace(tmp, path)
        return ledger


def public_child_claim_audit(root: Path, attempt_sha256: str) -> dict[str, Any]:
    empty = {"status": "CHILD_CLAIM_AUDIT_REQUIRED", "attempt_sha256": attempt_sha256, "child_claim_audit_sha256": "", "supported_claims": 0, "held_new_claims": 0, "failed_claims": 0, "paper_contract_revision_eligible": False, "claim_update_authorized": False, "paper_preparation_eligible": False, "submission_eligible": False, "authority": dict(ZERO_AUTHORITY)}
    path = _directory(root) / f"{_slug(attempt_sha256)}.json"
    if not path.exists():
        return empty
    try:
        ledger = json.loads(path.read_text())
    except Exception:
        return {**empty, "status": "CHILD_CLAIM_AUDIT_LEDGER_INVALID"}
    if validate_child_claim_audit_ledger(ledger):
        return {**empty, "status": "CHILD_CLAIM_AUDIT_LEDGER_INVALID"}
    receipts = [event.get("receipt") or {} for event in ledger.get("events") or [] if isinstance(event, Mapping) and isinstance(event.get("receipt"), Mapping)]
    receipt = receipts[-1] if receipts else {}
    if not receipt or not validate_child_claim_audit(receipt):
        return {**empty, "status": "CHILD_CLAIM_AUDIT_LEDGER_INVALID"}
    return {**empty, "status": _text(receipt.get("status")), "child_claim_audit_sha256": _text(receipt.get("child_claim_audit_sha256")), "supported_claims": len(receipt.get("supported_claim_ids") or []), "held_new_claims": len(receipt.get("held_new_claim_ids") or []), "failed_claims": len(receipt.get("failed_claim_ids") or []), "paper_contract_revision_eligible": receipt.get("paper_contract_revision_eligible") is True, "claim_update_authorized": False, "paper_preparation_eligible": False, "submission_eligible": False}
