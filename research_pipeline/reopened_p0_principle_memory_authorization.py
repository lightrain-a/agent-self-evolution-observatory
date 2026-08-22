from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .reopened_p0_principle_handoff import DEAD_END_CANDIDATE_STATUS, validate_p0_principle_handoff

SCHEMA_VERSION = "1.0"
AUTH_STATUS = "P0_PRINCIPLE_DEAD_END_HUMAN_AUTHORIZED_MEMORY_HANDOFF_REQUIRED"
HANDOFF_STATUS = "RESEARCH_MEMORY_PRINCIPLE_DEAD_END_HANDOFF_READY"
MEMORY_DESTINATION = "RESEARCH_MEMORY_SCIENTIFIC_CLOSURE_GATE"
ZERO_LEDGER_AUTHORITY = {"principle": False, "memory_write": False, "claim_update": False, "experiment": False, "gpu": False, "submission": False}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown"


def authorization_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "contract_id", "contract_sha256", "principle_id", "principle_handoff_sha256",
        "external_authority_ref_sha256", "authorized_at", "authorization_scope", "status",
    )}


def build_principle_memory_authorization(*, principle_handoff: Mapping[str, Any], external_authority_ref: str, authorized_at: str) -> dict[str, Any]:
    if not validate_p0_principle_handoff(principle_handoff) or principle_handoff.get("status") != DEAD_END_CANDIDATE_STATUS:
        raise RuntimeError("human principle-memory authorization requires a valid dead-end candidate")
    ref = _text(external_authority_ref); at = _text(authorized_at)
    if not ref:
        raise RuntimeError("external human principle authority reference required")
    if not at:
        raise RuntimeError("principle-memory authorization timestamp required")
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "reopen-p0-principle-memory-authorization",
        "contract_id": _text(principle_handoff.get("contract_id")),
        "contract_sha256": _text(principle_handoff.get("contract_sha256")),
        "principle_id": _text(principle_handoff.get("principle_id")),
        "principle_handoff_sha256": _text(principle_handoff.get("principle_handoff_sha256")),
        "principle_evidence_sha256": _text(principle_handoff.get("principle_evidence_sha256")),
        "external_authority_ref": ref,
        "external_authority_ref_sha256": hashlib.sha256(ref.encode()).hexdigest(),
        "authorized_at": at,
        "authorization_scope": "CREATE_SCOPED_PRINCIPLE_DEAD_END_MEMORY_HANDOFF_ONLY",
        "status": AUTH_STATUS,
        "principle_memory_update_authorized": True,
        "automatic_memory_write_authorized": False,
        "persistent_memory_write_completed": False,
        "claim_update_authorized": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["principle_memory_authorization_sha256"] = _digest(authorization_identity(receipt))
    if not validate_principle_memory_authorization(receipt):
        raise RuntimeError("generated principle-memory authorization invalid")
    return receipt


def validate_principle_memory_authorization(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "reopen-p0-principle-memory-authorization" or receipt.get("status") != AUTH_STATUS:
        return False
    ref = _text(receipt.get("external_authority_ref"))
    if not ref or hashlib.sha256(ref.encode()).hexdigest() != _text(receipt.get("external_authority_ref_sha256")):
        return False
    if receipt.get("authorization_scope") != "CREATE_SCOPED_PRINCIPLE_DEAD_END_MEMORY_HANDOFF_ONLY":
        return False
    if receipt.get("principle_memory_update_authorized") is not True:
        return False
    if receipt.get("automatic_memory_write_authorized") is not False or receipt.get("persistent_memory_write_completed") is not False:
        return False
    if any(receipt.get(key) is not False for key in ("claim_update_authorized", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return _text(receipt.get("principle_memory_authorization_sha256")) == _digest(authorization_identity(receipt))


def memory_handoff_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "contract_id", "contract_sha256", "principle_id", "principle_handoff_sha256",
        "principle_memory_authorization_sha256", "principle_evidence_sha256", "memory_spec_sha256",
        "destination_gate", "status",
    )}


def build_principle_memory_handoff(*, principle_handoff: Mapping[str, Any], authorization: Mapping[str, Any], memory_spec: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_p0_principle_handoff(principle_handoff) or principle_handoff.get("status") != DEAD_END_CANDIDATE_STATUS:
        raise RuntimeError("valid dead-end candidate required for Research Memory handoff")
    if not validate_principle_memory_authorization(authorization):
        raise RuntimeError("valid human principle-memory authorization required")
    if _text(authorization.get("principle_handoff_sha256")) != _text(principle_handoff.get("principle_handoff_sha256")):
        raise RuntimeError("principle-memory authorization/handoff lineage mismatch")
    spec = dict(memory_spec or {})
    for key in ("title", "summary", "scope", "reopen_condition", "opposite_search_seed"):
        if not _text(spec.get(key)):
            raise RuntimeError(f"principle memory handoff field required: {key}")
    refs = spec.get("source_refs") or []
    if not isinstance(refs, list) or not refs or any(not _text(item) for item in refs):
        raise RuntimeError("principle memory handoff requires source refs")
    if _text(spec.get("source_principle_evidence_sha256")) != _text(principle_handoff.get("principle_evidence_sha256")):
        raise RuntimeError("principle memory handoff must bind exact principle evidence SHA")
    canonical_spec = {
        "title": _text(spec.get("title")),
        "summary": _text(spec.get("summary")),
        "scope": _text(spec.get("scope")),
        "reopen_condition": _text(spec.get("reopen_condition")),
        "opposite_search_seed": _text(spec.get("opposite_search_seed")),
        "source_refs": [_text(item) for item in refs],
        "source_principle_evidence_sha256": _text(spec.get("source_principle_evidence_sha256")),
    }
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "reopen-p0-principle-memory-handoff",
        "contract_id": _text(principle_handoff.get("contract_id")),
        "contract_sha256": _text(principle_handoff.get("contract_sha256")),
        "principle_id": _text(principle_handoff.get("principle_id")),
        "principle_handoff_sha256": _text(principle_handoff.get("principle_handoff_sha256")),
        "principle_memory_authorization_sha256": _text(authorization.get("principle_memory_authorization_sha256")),
        "principle_evidence_sha256": _text(principle_handoff.get("principle_evidence_sha256")),
        "memory_spec": canonical_spec,
        "memory_spec_sha256": _digest(canonical_spec),
        "destination_gate": MEMORY_DESTINATION,
        "status": HANDOFF_STATUS,
        "memory_class": "PRINCIPLE_DEAD_END",
        "failure_layer": "core_principle",
        "scientific_dead_end_certified": True,
        "principle_update_allowed": True,
        "human_principle_authority_confirmed": True,
        "automatic_memory_write_authorized": False,
        "persistent_memory_write_completed": False,
        "claim_update_authorized": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["principle_memory_handoff_sha256"] = _digest(memory_handoff_identity(receipt))
    if not validate_principle_memory_handoff(receipt):
        raise RuntimeError("generated Research Memory principle handoff invalid")
    return receipt


def validate_principle_memory_handoff(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "reopen-p0-principle-memory-handoff" or receipt.get("status") != HANDOFF_STATUS:
        return False
    if receipt.get("destination_gate") != MEMORY_DESTINATION or receipt.get("memory_class") != "PRINCIPLE_DEAD_END" or receipt.get("failure_layer") != "core_principle":
        return False
    if receipt.get("scientific_dead_end_certified") is not True or receipt.get("principle_update_allowed") is not True or receipt.get("human_principle_authority_confirmed") is not True:
        return False
    if receipt.get("automatic_memory_write_authorized") is not False or receipt.get("persistent_memory_write_completed") is not False:
        return False
    if any(receipt.get(key) is not False for key in ("claim_update_authorized", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    spec = receipt.get("memory_spec") or {}
    if not isinstance(spec, Mapping) or _digest(spec) != _text(receipt.get("memory_spec_sha256")):
        return False
    if not _text(spec.get("reopen_condition")) or not _text(spec.get("scope")) or not list(spec.get("source_refs") or []):
        return False
    if _text(spec.get("source_principle_evidence_sha256")) != _text(receipt.get("principle_evidence_sha256")):
        return False
    return _text(receipt.get("principle_memory_handoff_sha256")) == _digest(memory_handoff_identity(receipt))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "scientific-contract-p0-principle-memory" else root / "scientific-contract-p0-principle-memory"


def _receipt_sha(receipt: Mapping[str, Any]) -> str:
    if receipt.get("receipt_type") == "reopen-p0-principle-memory-handoff":
        return _text(receipt.get("principle_memory_handoff_sha256"))
    return _text(receipt.get("principle_memory_authorization_sha256"))


def validate_principle_memory_ledger(ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []; seen: set[str] = set(); authorizations: set[str] = set()
    cid = _text(ledger.get("contract_id")); csha = _text(ledger.get("contract_sha256"))
    if (ledger.get("authority") or {}) != ZERO_LEDGER_AUTHORITY:
        errors.append("principle-memory-ledger-global-authority-leak")
    for index, event in enumerate(ledger.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        typ = _text(receipt.get("receipt_type")) if isinstance(receipt, Mapping) else ""
        valid = validate_principle_memory_authorization(receipt) if typ == "reopen-p0-principle-memory-authorization" else validate_principle_memory_handoff(receipt) if typ == "reopen-p0-principle-memory-handoff" else False
        if not valid:
            errors.append("principle-memory-receipt-invalid"); continue
        if _text(receipt.get("contract_id")) != cid or _text(receipt.get("contract_sha256")) != csha:
            errors.append("principle-memory-contract-lineage-mismatch")
        sha = _receipt_sha(receipt)
        if sha in seen:
            errors.append("principle-memory-duplicate-receipt")
        if typ == "reopen-p0-principle-memory-authorization":
            authorizations.add(sha)
        elif _text(receipt.get("principle_memory_authorization_sha256")) not in authorizations:
            errors.append("principle-memory-handoff-missing-prior-authorization")
        recorded = _text(event.get("recorded_at"))
        if _text(event.get("event_id")) != _digest([cid, index, typ, sha, recorded])[:24]:
            errors.append("principle-memory-event-id-invalid")
        seen.add(sha)
    return list(dict.fromkeys(errors))


def publish_principle_memory_receipt(root: Path, receipt: Mapping[str, Any], *, recorded_at: str) -> dict[str, Any]:
    typ = _text(receipt.get("receipt_type"))
    valid = validate_principle_memory_authorization(receipt) if typ == "reopen-p0-principle-memory-authorization" else validate_principle_memory_handoff(receipt) if typ == "reopen-p0-principle-memory-handoff" else False
    if not valid:
        raise RuntimeError("invalid principle-memory receipt")
    at = _text(recorded_at)
    if not at:
        raise RuntimeError("principle-memory receipt recorded_at required")
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    cid = _text(receipt.get("contract_id")); path = directory / f"{_slug(cid)}.json"; lock = directory / f".{_slug(cid)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ledger = json.loads(path.read_text()) if path.exists() else {"schema_version": SCHEMA_VERSION, "contract_id": cid, "contract_sha256": _text(receipt.get("contract_sha256")), "events": [], "authority": dict(ZERO_LEDGER_AUTHORITY)}
        sha = _receipt_sha(receipt)
        for event in ledger.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _receipt_sha(prior) == sha:
                return ledger
        if typ == "reopen-p0-principle-memory-handoff":
            auths = {_text((event.get("receipt") or {}).get("principle_memory_authorization_sha256")) for event in ledger.get("events") or [] if isinstance(event, Mapping) and (event.get("receipt") or {}).get("receipt_type") == "reopen-p0-principle-memory-authorization"}
            if _text(receipt.get("principle_memory_authorization_sha256")) not in auths:
                raise RuntimeError("Research Memory handoff requires published human principle authorization")
        event = {"event_type": typ, "receipt": dict(receipt), "recorded_at": at, "global_principle_authority": False, "automatic_memory_write": False}
        event["event_id"] = _digest([cid, len(ledger.get("events") or []), typ, sha, at])[:24]
        ledger.setdefault("events", []).append(event); ledger["updated_at"] = at
        errors = validate_principle_memory_ledger(ledger)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"); os.replace(tmp, path)
        return ledger


def public_principle_memory_state(root: Path, contract_id: str) -> dict[str, Any]:
    empty = {"status": "P0_PRINCIPLE_MEMORY_AUTHORIZATION_REQUIRED", "authorization_sha256": "", "memory_handoff_sha256": "", "principle_id": "", "destination_gate": "", "principle_update_allowed": False, "automatic_memory_write_authorized": False, "persistent_memory_write_completed": False, "authority": dict(ZERO_LEDGER_AUTHORITY)}
    path = _directory(root) / f"{_slug(contract_id)}.json"
    if not path.exists():
        return empty
    try:
        ledger = json.loads(path.read_text())
    except Exception:
        return {**empty, "status": "P0_PRINCIPLE_MEMORY_LEDGER_INVALID"}
    if validate_principle_memory_ledger(ledger):
        return {**empty, "status": "P0_PRINCIPLE_MEMORY_LEDGER_INVALID"}
    authorization: Mapping[str, Any] = {}; handoff: Mapping[str, Any] = {}
    for event in ledger.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if receipt.get("receipt_type") == "reopen-p0-principle-memory-authorization": authorization = receipt
        elif receipt.get("receipt_type") == "reopen-p0-principle-memory-handoff": handoff = receipt
    if handoff:
        return {**empty, "status": HANDOFF_STATUS, "authorization_sha256": _text(authorization.get("principle_memory_authorization_sha256")), "memory_handoff_sha256": _text(handoff.get("principle_memory_handoff_sha256")), "principle_id": _text(handoff.get("principle_id")), "destination_gate": MEMORY_DESTINATION, "principle_update_allowed": True, "automatic_memory_write_authorized": False, "persistent_memory_write_completed": False}
    if authorization:
        return {**empty, "status": AUTH_STATUS, "authorization_sha256": _text(authorization.get("principle_memory_authorization_sha256")), "principle_id": _text(authorization.get("principle_id")), "principle_update_allowed": True, "automatic_memory_write_authorized": False, "persistent_memory_write_completed": False}
    return empty
