from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from .reopened_child_claim_audit import PASS_STATUS, HOLD_STATUS, validate_child_claim_audit

SCHEMA_VERSION = "1.0"
STATUS = "CHILD_NEW_CLAIM_HUMAN_EXPANSION_AUTHORIZED_CONTRACT_REVISION_REQUIRED"
ZERO_AUTHORITY = {"scientific": False, "parent_claim_update": False, "paper_preparation": False, "submission": False, "experiment": False, "gpu": False}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown"


def authorization_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "paper_id", "attempt_sha256", "child_claim_audit_sha256", "approved_new_claim_ids",
        "external_authority_ref_sha256", "authorized_at", "scope", "status",
    )}


def build_child_claim_expansion_authorization(
    *,
    claim_audit: Mapping[str, Any],
    approved_new_claim_ids: Sequence[str],
    external_authority_ref: str,
    authorized_at: str,
    scope: str,
) -> dict[str, Any]:
    if not validate_child_claim_audit(claim_audit) or claim_audit.get("status") not in {PASS_STATUS, HOLD_STATUS}:
        raise RuntimeError("valid child Claim Audit with held new claims required")
    held = list(claim_audit.get("held_new_claim_ids") or [])
    if not held:
        raise RuntimeError("child Claim Audit has no held new claims requiring expansion authority")
    approved = sorted({_text(value) for value in approved_new_claim_ids if _text(value)})
    if not approved:
        raise RuntimeError("at least one held new claim must be explicitly approved")
    unknown = sorted(set(approved) - set(held))
    if unknown:
        raise RuntimeError("claim expansion authority may approve only audit-held new claims: " + ",".join(unknown))
    ref = _text(external_authority_ref); at = _text(authorized_at); scope_text = _text(scope)
    if not ref or not at or not scope_text:
        raise RuntimeError("human claim-expansion authority ref, timestamp, and scope are required")
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "scientific-reopen-child-claim-expansion-authorization",
        "paper_id": _text(claim_audit.get("paper_id")),
        "attempt_sha256": _text(claim_audit.get("attempt_sha256")),
        "child_claim_audit_sha256": _text(claim_audit.get("child_claim_audit_sha256")),
        "held_new_claim_ids_at_audit": held,
        "approved_new_claim_ids": approved,
        "external_authority_ref": ref,
        "external_authority_ref_sha256": hashlib.sha256(ref.encode()).hexdigest(),
        "authorized_at": at,
        "scope": scope_text,
        "status": STATUS,
        "child_claim_expansion_authorized": True,
        "authorization_applies_only_to_listed_claim_ids": True,
        "future_claim_expansion_authorized": False,
        "parent_claim_update_authorized": False,
        "paper_preparation_authorized": False,
        "submission_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }
    receipt["child_claim_expansion_authorization_sha256"] = _digest(authorization_identity(receipt))
    if not validate_child_claim_expansion_authorization(receipt):
        raise RuntimeError("generated child claim-expansion authorization invalid")
    return receipt


def validate_child_claim_expansion_authorization(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "scientific-reopen-child-claim-expansion-authorization" or receipt.get("status") != STATUS:
        return False
    held = list(receipt.get("held_new_claim_ids_at_audit") or []); approved = list(receipt.get("approved_new_claim_ids") or [])
    if not held or not approved or approved != sorted(set(approved)) or not set(approved).issubset(set(held)):
        return False
    ref = _text(receipt.get("external_authority_ref"))
    if not ref or hashlib.sha256(ref.encode()).hexdigest() != _text(receipt.get("external_authority_ref_sha256")):
        return False
    if not _text(receipt.get("scope")) or not _text(receipt.get("authorized_at")):
        return False
    if receipt.get("child_claim_expansion_authorized") is not True or receipt.get("authorization_applies_only_to_listed_claim_ids") is not True:
        return False
    if any(receipt.get(key) is not False for key in (
        "future_claim_expansion_authorized", "parent_claim_update_authorized", "paper_preparation_authorized",
        "submission_authorized", "scientific_authority", "experiment_authority", "gpu_authority",
    )):
        return False
    return _text(receipt.get("child_claim_expansion_authorization_sha256")) == _digest(authorization_identity(receipt))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "paper-scientific-claim-expansion-authority" else root / "paper-scientific-claim-expansion-authority"


def validate_claim_expansion_authority_ledger(ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []; seen: set[str] = set(); attempt_sha = _text(ledger.get("attempt_sha256"))
    if (ledger.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("claim-expansion-authority-ledger-global-authority-leak")
    for index, event in enumerate(ledger.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if not isinstance(receipt, Mapping) or not validate_child_claim_expansion_authorization(receipt):
            errors.append("claim-expansion-authority-receipt-invalid"); continue
        if _text(receipt.get("attempt_sha256")) != attempt_sha:
            errors.append("claim-expansion-authority-attempt-lineage-mismatch")
        sha = _text(receipt.get("child_claim_expansion_authorization_sha256"))
        if sha in seen:
            errors.append("claim-expansion-authority-duplicate")
        recorded = _text(event.get("recorded_at"))
        if _text(event.get("event_id")) != _digest([attempt_sha, index, sha, recorded])[:24]:
            errors.append("claim-expansion-authority-event-id-invalid")
        seen.add(sha)
    return list(dict.fromkeys(errors))


def publish_child_claim_expansion_authorization(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_child_claim_expansion_authorization(receipt):
        raise RuntimeError("invalid child claim-expansion authorization")
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    attempt_sha = _text(receipt.get("attempt_sha256")); path = directory / f"{_slug(attempt_sha)}.json"; lock = directory / f".{_slug(attempt_sha)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ledger = json.loads(path.read_text()) if path.exists() else {"schema_version": SCHEMA_VERSION, "paper_id": _text(receipt.get("paper_id")), "attempt_sha256": attempt_sha, "events": [], "authority": dict(ZERO_AUTHORITY)}
        sha = _text(receipt.get("child_claim_expansion_authorization_sha256"))
        for event in ledger.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _text(prior.get("child_claim_expansion_authorization_sha256")) == sha:
                return ledger
        at = _text(receipt.get("authorized_at")); event = {"event_type": "scientific-reopen-child-claim-expansion-authorization", "receipt": dict(receipt), "recorded_at": at, "parent_claim_update_authority": False, "paper_preparation_authority": False}
        event["event_id"] = _digest([attempt_sha, len(ledger.get("events") or []), sha, at])[:24]
        ledger.setdefault("events", []).append(event); ledger["updated_at"] = at
        errors = validate_claim_expansion_authority_ledger(ledger)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"); os.replace(tmp, path)
        return ledger


def public_child_claim_expansion_authorization(root: Path, attempt_sha256: str) -> dict[str, Any]:
    empty = {"status": "CHILD_NEW_CLAIM_EXPANSION_AUTHORITY_REQUIRED", "attempt_sha256": attempt_sha256, "authorization_sha256": "", "approved_new_claims": 0, "future_claim_expansion_authorized": False, "parent_claim_update_authorized": False, "paper_preparation_authorized": False, "authority": dict(ZERO_AUTHORITY)}
    path = _directory(root) / f"{_slug(attempt_sha256)}.json"
    if not path.exists():
        return empty
    try:
        ledger = json.loads(path.read_text())
    except Exception:
        return {**empty, "status": "CHILD_CLAIM_EXPANSION_AUTHORITY_LEDGER_INVALID"}
    if validate_claim_expansion_authority_ledger(ledger):
        return {**empty, "status": "CHILD_CLAIM_EXPANSION_AUTHORITY_LEDGER_INVALID"}
    receipts = [event.get("receipt") or {} for event in ledger.get("events") or [] if isinstance(event, Mapping) and isinstance(event.get("receipt"), Mapping)]
    receipt = receipts[-1] if receipts else {}
    if not receipt or not validate_child_claim_expansion_authorization(receipt):
        return {**empty, "status": "CHILD_CLAIM_EXPANSION_AUTHORITY_LEDGER_INVALID"}
    return {**empty, "status": STATUS, "authorization_sha256": _text(receipt.get("child_claim_expansion_authorization_sha256")), "approved_new_claims": len(receipt.get("approved_new_claim_ids") or []), "future_claim_expansion_authorized": False, "parent_claim_update_authorized": False, "paper_preparation_authorized": False}
