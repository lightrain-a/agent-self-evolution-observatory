from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .reopened_p0_principle_memory_authorization import HANDOFF_STATUS, validate_principle_memory_handoff

SCHEMA_VERSION = "1.0"
STATUS = "SCOPED_PRINCIPLE_SCIENTIFIC_CLOSURE_PERSISTED"
ZERO_AUTHORITY = {"scientific": False, "problem_gate": False, "method": False, "experiment": False, "p0": False, "gpu": False, "submission": False}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown"


def closure_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "closure_id", "memory_id", "contract_id", "contract_sha256", "principle_id",
        "principle_memory_handoff_sha256", "principle_evidence_sha256", "scope",
        "reopen_condition", "opposite_search_seed", "source_refs", "persisted_at", "status",
    )}


def build_principle_scientific_closure(*, memory_handoff: Mapping[str, Any], persisted_at: str) -> dict[str, Any]:
    if not validate_principle_memory_handoff(memory_handoff) or memory_handoff.get("status") != HANDOFF_STATUS:
        raise RuntimeError("valid Research Memory principle handoff required")
    at = _text(persisted_at)
    if not at:
        raise RuntimeError("principle scientific closure persisted_at required")
    spec = memory_handoff.get("memory_spec") or {}
    principle_id = _text(memory_handoff.get("principle_id")); contract_id = _text(memory_handoff.get("contract_id"))
    seed = _digest([principle_id, contract_id, memory_handoff.get("principle_memory_handoff_sha256"), spec.get("scope"), spec.get("reopen_condition")])
    closure_id = f"P0-PRINCIPLE-CLOSURE-{seed[:20]}"
    memory_id = f"MEM-SCIP0-{seed[:18]}"
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "reopen-p0-principle-scientific-closure",
        "closure_id": closure_id,
        "memory_id": memory_id,
        "status": STATUS,
        "contract_id": contract_id,
        "contract_sha256": _text(memory_handoff.get("contract_sha256")),
        "principle_id": principle_id,
        "principle_memory_handoff_sha256": _text(memory_handoff.get("principle_memory_handoff_sha256")),
        "principle_evidence_sha256": _text(memory_handoff.get("principle_evidence_sha256")),
        "source_candidate_id": closure_id,
        "title": _text(spec.get("title")),
        "reason": _text(spec.get("summary")),
        "scope": _text(spec.get("scope")),
        "failure_layer": "core_principle",
        "closure_layer": "core_principle",
        "dead_end_certified": True,
        "principle_update_allowed": True,
        "memory_class": "PRINCIPLE_DEAD_END",
        "search_closure_certified": False,
        "counter_explanation": {
            "scope": _text(spec.get("scope")),
            "reopen_condition": _text(spec.get("reopen_condition")),
            "opposite_search_seed": _text(spec.get("opposite_search_seed")),
        },
        "source_refs": [_text(item) for item in spec.get("source_refs") or []],
        "persisted_at": at,
        "scope_match_required_for_reuse": True,
        "reopen_condition_required_for_reentry": True,
        "automatic_global_blacklist_forbidden": True,
        "adjacent_scientific_objects_remain_open": True,
        "downstream_scientific_gates_unchanged": True,
        "parent_paper_claim_update_authorized": False,
        "scientific_authority": False,
    }
    receipt["principle_closure_sha256"] = _digest(closure_identity(receipt))
    if not validate_principle_scientific_closure(receipt):
        raise RuntimeError("generated principle scientific closure invalid")
    return receipt


def validate_principle_scientific_closure(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "reopen-p0-principle-scientific-closure" or receipt.get("status") != STATUS:
        return False
    if receipt.get("failure_layer") != "core_principle" or receipt.get("closure_layer") != "core_principle" or receipt.get("memory_class") != "PRINCIPLE_DEAD_END":
        return False
    if receipt.get("dead_end_certified") is not True or receipt.get("principle_update_allowed") is not True:
        return False
    counter = receipt.get("counter_explanation") or {}
    if not isinstance(counter, Mapping) or not _text(counter.get("scope")) or not _text(counter.get("reopen_condition")) or not _text(counter.get("opposite_search_seed")):
        return False
    if not list(receipt.get("source_refs") or []) or not _text(receipt.get("principle_evidence_sha256")):
        return False
    if any(receipt.get(key) is not True for key in ("scope_match_required_for_reuse", "reopen_condition_required_for_reentry", "automatic_global_blacklist_forbidden", "adjacent_scientific_objects_remain_open", "downstream_scientific_gates_unchanged")):
        return False
    if receipt.get("parent_paper_claim_update_authorized") is not False or receipt.get("scientific_authority") is not False:
        return False
    return _text(receipt.get("principle_closure_sha256")) == _digest(closure_identity(receipt))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "research-memory-principle-closures" else root / "research-memory-principle-closures"


def validate_principle_closure_ledger(ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []; seen: set[str] = set(); principle_id = _text(ledger.get("principle_id"))
    if (ledger.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("principle-closure-ledger-authority-leak")
    for index, event in enumerate(ledger.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if not isinstance(receipt, Mapping) or not validate_principle_scientific_closure(receipt):
            errors.append("principle-closure-receipt-invalid"); continue
        if _text(receipt.get("principle_id")) != principle_id:
            errors.append("principle-closure-principle-lineage-mismatch")
        sha = _text(receipt.get("principle_closure_sha256"))
        if sha in seen:
            errors.append("principle-closure-duplicate")
        recorded = _text(event.get("recorded_at"))
        if _text(event.get("event_id")) != _digest([principle_id, index, sha, recorded])[:24]:
            errors.append("principle-closure-event-id-invalid")
        seen.add(sha)
    return list(dict.fromkeys(errors))


def publish_principle_scientific_closure(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_principle_scientific_closure(receipt):
        raise RuntimeError("invalid principle scientific closure")
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    principle_id = _text(receipt.get("principle_id")); path = directory / f"{_slug(principle_id)}.json"; lock = directory / f".{_slug(principle_id)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ledger = json.loads(path.read_text()) if path.exists() else {"schema_version": SCHEMA_VERSION, "principle_id": principle_id, "events": [], "authority": dict(ZERO_AUTHORITY)}
        sha = _text(receipt.get("principle_closure_sha256"))
        for event in ledger.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _text(prior.get("principle_closure_sha256")) == sha:
                return ledger
        at = _text(receipt.get("persisted_at"))
        event = {"event_type": "reopen-p0-principle-scientific-closure", "receipt": dict(receipt), "recorded_at": at, "scientific_authority": False, "global_blacklist_authority": False}
        event["event_id"] = _digest([principle_id, len(ledger.get("events") or []), sha, at])[:24]
        ledger.setdefault("events", []).append(event); ledger["updated_at"] = at
        errors = validate_principle_closure_ledger(ledger)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"); os.replace(tmp, path)
        return ledger


def load_principle_closures(root: Path) -> list[dict[str, Any]]:
    directory = _directory(root)
    rows: list[dict[str, Any]] = []
    if not directory.exists():
        return rows
    for path in sorted(directory.glob("*.json")):
        try:
            ledger = json.loads(path.read_text())
        except Exception:
            continue
        if validate_principle_closure_ledger(ledger):
            continue
        for event in ledger.get("events") or []:
            receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(receipt, Mapping) and validate_principle_scientific_closure(receipt):
                rows.append(dict(receipt))
    return rows


def public_principle_closure_summary(root: Path) -> dict[str, Any]:
    rows = load_principle_closures(root)
    return {
        "status": "PRINCIPLE_CLOSURE_REGISTRY_READY",
        "scientific_closures": len(rows),
        "principles": len({row.get("principle_id") for row in rows}),
        "all_scope_bound": all(row.get("scope_match_required_for_reuse") is True for row in rows),
        "all_reopenable": all(bool(_text((row.get("counter_explanation") or {}).get("reopen_condition"))) for row in rows),
        "automatic_global_blacklist_authorized": False,
        "scientific_authority": False,
    }
