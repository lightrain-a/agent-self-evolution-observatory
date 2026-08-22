from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .principle_adjudication import adjudicate_experiment_evidence
from .reopened_p0_result_adjudication import METHOD_FAIL, METHOD_PASS, validate_p0_adjudication

SCHEMA_VERSION = "1.0"
SUPPORT_STATUS = "P0_PRINCIPLE_SUPPORTED_NOT_PROVEN_HUMAN_REVIEW_OPTIONAL"
UNRESOLVED_STATUS = "P0_METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED"
PREDICTION_REJECTED_STATUS = "P0_REGISTERED_PREDICTION_REJECTED_COUNTEREXPLANATION_REQUIRED"
DEAD_END_CANDIDATE_STATUS = "P0_PRINCIPLE_DEAD_END_CANDIDATE_HUMAN_REVIEW_REQUIRED"
ZERO_AUTHORITY = {"principle": False, "scientific": False, "claim_update": False, "experiment": False, "gpu": False, "submission": False}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown"


def handoff_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "contract_id", "contract_sha256", "p0_adjudication_sha256", "principle_id",
        "principle_certificate_sha256", "principle_evidence_sha256", "underlying_verdict",
        "status", "registered_prediction_rejected", "dead_end_candidate",
        "automatic_principle_update_authorized",
    )}


def build_p0_principle_handoff(*, p0_adjudication: Mapping[str, Any], principle_certificate: Mapping[str, Any], principle_evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not validate_p0_adjudication(p0_adjudication):
        raise RuntimeError("valid independent P0 adjudication required")
    if p0_adjudication.get("status") not in {METHOD_PASS, METHOD_FAIL}:
        raise RuntimeError("principle handoff requires an authorized P0 method verdict")
    certificate = dict(principle_certificate or {})
    if certificate.get("passed") is not True or not isinstance(certificate.get("contract"), Mapping):
        raise RuntimeError("valid passed principle certificate required")
    evidence = dict(principle_evidence or {})
    diagnosis = "positive-signal" if p0_adjudication.get("status") == METHOD_PASS else "true-negative"
    underlying = adjudicate_experiment_evidence(diagnosis, certificate, evidence)
    verdict = _text(underlying.get("verdict"))
    if verdict == "PRINCIPLE_SUPPORTED_NOT_PROVEN":
        status = SUPPORT_STATUS
    elif verdict == "REGISTERED_PREDICTION_REJECTED_COUNTEREXPLANATION_REQUIRED":
        status = PREDICTION_REJECTED_STATUS
    elif verdict == "PRINCIPLE_DEAD_END_CERTIFIED":
        status = DEAD_END_CANDIDATE_STATUS
    else:
        status = UNRESOLVED_STATUS
    dead_end_candidate = verdict == "PRINCIPLE_DEAD_END_CERTIFIED"
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "reopen-p0-principle-handoff",
        "contract_id": _text(p0_adjudication.get("contract_id")),
        "contract_sha256": _text(p0_adjudication.get("contract_sha256")),
        "p0_adjudication_sha256": _text(p0_adjudication.get("p0_adjudication_sha256")),
        "principle_id": _text((certificate.get("contract") or {}).get("principle_id")),
        "principle_certificate_sha256": _digest(certificate),
        "principle_evidence_sha256": _digest(evidence),
        "underlying_verdict": verdict,
        "underlying_failure_layer": underlying.get("failure_layer"),
        "registered_prediction_rejected": underlying.get("registered_prediction_rejected") is True,
        "registered_prediction_id": _text(underlying.get("registered_prediction_id")),
        "preconditions": dict(underlying.get("preconditions") or {}),
        "missing_preconditions": list(underlying.get("missing_preconditions") or []),
        "scientific_belief_target": _text(underlying.get("scientific_belief_target")),
        "status": status,
        "dead_end_candidate": dead_end_candidate,
        "external_human_principle_review_required": dead_end_candidate,
        "automatic_principle_update_authorized": False,
        "persistent_dead_end_memory_write_authorized": False,
        "claim_update_authorized": False,
        "parent_paper_claim_status_unchanged": True,
        "method_fail_alone_cannot_falsify_principle": True,
        "positive_method_evidence_does_not_prove_principle": True,
        "scientific_authority": False,
        "principle_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["principle_handoff_sha256"] = _digest(handoff_identity(receipt))
    if not validate_p0_principle_handoff(receipt):
        raise RuntimeError("generated P0 principle handoff invalid")
    return receipt


def validate_p0_principle_handoff(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "reopen-p0-principle-handoff":
        return False
    allowed = {SUPPORT_STATUS, UNRESOLVED_STATUS, PREDICTION_REJECTED_STATUS, DEAD_END_CANDIDATE_STATUS}
    if receipt.get("status") not in allowed:
        return False
    if not _text(receipt.get("principle_id")) or not _text(receipt.get("principle_certificate_sha256")):
        return False
    dead_end = receipt.get("status") == DEAD_END_CANDIDATE_STATUS
    if receipt.get("dead_end_candidate") is not dead_end:
        return False
    if receipt.get("external_human_principle_review_required") is not dead_end:
        return False
    if any(receipt.get(key) is not False for key in (
        "automatic_principle_update_authorized", "persistent_dead_end_memory_write_authorized",
        "claim_update_authorized", "scientific_authority", "principle_authority",
        "experiment_authority", "gpu_authority", "submission_authority",
    )):
        return False
    if receipt.get("parent_paper_claim_status_unchanged") is not True or receipt.get("method_fail_alone_cannot_falsify_principle") is not True or receipt.get("positive_method_evidence_does_not_prove_principle") is not True:
        return False
    return _text(receipt.get("principle_handoff_sha256")) == _digest(handoff_identity(receipt))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "scientific-contract-p0-principle-handoffs" else root / "scientific-contract-p0-principle-handoffs"


def validate_p0_principle_handoff_ledger(ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []; seen: set[str] = set(); cid = _text(ledger.get("contract_id")); csha = _text(ledger.get("contract_sha256"))
    if (ledger.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("p0-principle-handoff-ledger-authority-leak")
    for index, event in enumerate(ledger.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if not isinstance(receipt, Mapping) or not validate_p0_principle_handoff(receipt):
            errors.append("p0-principle-handoff-receipt-invalid"); continue
        if _text(receipt.get("contract_id")) != cid or _text(receipt.get("contract_sha256")) != csha:
            errors.append("p0-principle-handoff-contract-lineage-mismatch")
        sha = _text(receipt.get("principle_handoff_sha256"))
        if sha in seen:
            errors.append("p0-principle-handoff-duplicate")
        recorded = _text(event.get("recorded_at"))
        if _text(event.get("event_id")) != _digest([cid, index, sha, recorded])[:24]:
            errors.append("p0-principle-handoff-event-id-invalid")
        seen.add(sha)
    return list(dict.fromkeys(errors))


def publish_p0_principle_handoff(root: Path, receipt: Mapping[str, Any], *, recorded_at: str) -> dict[str, Any]:
    if not validate_p0_principle_handoff(receipt):
        raise RuntimeError("invalid P0 principle handoff receipt")
    at = _text(recorded_at)
    if not at:
        raise RuntimeError("P0 principle handoff recorded_at required")
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    cid = _text(receipt.get("contract_id")); path = directory / f"{_slug(cid)}.json"; lock = directory / f".{_slug(cid)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ledger = json.loads(path.read_text()) if path.exists() else {"schema_version": SCHEMA_VERSION, "contract_id": cid, "contract_sha256": _text(receipt.get("contract_sha256")), "events": [], "authority": dict(ZERO_AUTHORITY)}
        sha = _text(receipt.get("principle_handoff_sha256"))
        for event in ledger.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _text(prior.get("principle_handoff_sha256")) == sha:
                return ledger
        event = {"event_type": "reopen-p0-principle-handoff", "receipt": dict(receipt), "recorded_at": at, "principle_authority": False, "claim_update_authority": False}
        event["event_id"] = _digest([cid, len(ledger.get("events") or []), sha, at])[:24]
        ledger.setdefault("events", []).append(event); ledger["updated_at"] = at
        errors = validate_p0_principle_handoff_ledger(ledger)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"); os.replace(tmp, path)
        return ledger


def public_p0_principle_handoff(root: Path, contract_id: str) -> dict[str, Any]:
    empty = {"status": "P0_PRINCIPLE_HANDOFF_REQUIRED", "principle_handoff_sha256": "", "principle_id": "", "underlying_verdict": "", "registered_prediction_rejected": False, "dead_end_candidate": False, "automatic_principle_update_authorized": False, "authority": dict(ZERO_AUTHORITY)}
    path = _directory(root) / f"{_slug(contract_id)}.json"
    if not path.exists():
        return empty
    try:
        ledger = json.loads(path.read_text())
    except Exception:
        return {**empty, "status": "P0_PRINCIPLE_HANDOFF_LEDGER_INVALID"}
    if validate_p0_principle_handoff_ledger(ledger):
        return {**empty, "status": "P0_PRINCIPLE_HANDOFF_LEDGER_INVALID"}
    receipts = [event.get("receipt") or {} for event in ledger.get("events") or [] if isinstance(event, Mapping) and isinstance(event.get("receipt"), Mapping)]
    receipt = receipts[-1] if receipts else {}
    if not receipt or not validate_p0_principle_handoff(receipt):
        return {**empty, "status": "P0_PRINCIPLE_HANDOFF_LEDGER_INVALID"}
    return {**empty, "status": _text(receipt.get("status")), "principle_handoff_sha256": _text(receipt.get("principle_handoff_sha256")), "principle_id": _text(receipt.get("principle_id")), "underlying_verdict": _text(receipt.get("underlying_verdict")), "registered_prediction_rejected": receipt.get("registered_prediction_rejected") is True, "dead_end_candidate": receipt.get("dead_end_candidate") is True, "automatic_principle_update_authorized": False}
