from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .reopened_child_claim_audit import PASS_STATUS, validate_child_claim_audit
from .reopened_scientific_evidence_paper_handoff import validate_scientific_evidence_paper_handoff

SCHEMA_VERSION = "1.0"
STATUS = "CHILD_PAPER_CONTRACT_REVISION_FROZEN_PREPARATION_REVIEW_REQUIRED"
ZERO_AUTHORITY = {"scientific": False, "parent_claim_update": False, "paper_preparation": False, "submission": False, "experiment": False, "gpu": False}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown"


def contract_identity(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {key: contract.get(key) for key in (
        "paper_id", "attempt_sha256", "parent_paper_contract_sha256", "reopened_contract_sha256",
        "paper_revision_handoff_sha256", "child_claim_audit_sha256", "supported_claims",
        "held_new_claim_ids", "manuscript_scope", "limitations_boundary", "status",
    )}


def build_child_paper_contract(*, handoff: Mapping[str, Any], claim_audit: Mapping[str, Any], revision_spec: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_scientific_evidence_paper_handoff(handoff):
        raise RuntimeError("valid scientific-evidence child paper handoff required")
    if not validate_child_claim_audit(claim_audit) or claim_audit.get("status") != PASS_STATUS or claim_audit.get("paper_contract_revision_eligible") is not True:
        raise RuntimeError("passing child Claim Audit required before paper-contract revision")
    if _text(claim_audit.get("paper_revision_handoff_sha256")) != _text(handoff.get("paper_revision_handoff_sha256")) or _text(claim_audit.get("attempt_sha256")) != _text(handoff.get("attempt_sha256")):
        raise RuntimeError("child Claim Audit/handoff lineage mismatch")
    spec = dict(revision_spec or {})
    manuscript_scope = _text(spec.get("manuscript_scope")); limitations = _text(spec.get("limitations_boundary"))
    if not manuscript_scope or not limitations:
        raise RuntimeError("child paper contract requires manuscript scope and limitations boundary")
    if spec.get("parent_submitted_bytes_immutable") is not True or spec.get("preserve_parent_claims_not_listed") is not True:
        raise RuntimeError("child paper contract must preserve parent submission and untouched parent claims")
    wording = spec.get("claim_wording") or {}
    if not isinstance(wording, Mapping):
        raise RuntimeError("child paper claim_wording must be an object")
    supported_ids = list(claim_audit.get("supported_claim_ids") or [])
    if set(wording.keys()) != set(supported_ids):
        raise RuntimeError("child paper claim wording must cover exactly the audit-supported claims")
    candidate_by_id = {_text(row.get("claim_id")): row for row in handoff.get("candidate_claims") or []}
    supported_claims: list[dict[str, str]] = []
    for claim_id in supported_ids:
        candidate = candidate_by_id.get(claim_id) or {}
        text = _text(wording.get(claim_id))
        if not text:
            raise RuntimeError(f"child paper claim wording empty: {claim_id}")
        if candidate.get("claim_relation") == "NEW_CHILD_CLAIM":
            raise RuntimeError("new child claim cannot enter contract without separate expansion authority")
        supported_claims.append({
            "claim_id": claim_id,
            "claim_text": text,
            "claim_relation": _text(candidate.get("claim_relation")),
            "evidence_role": _text(candidate.get("evidence_role")),
            "evidence_bundle_sha256": _text(handoff.get("evidence_bundle_sha256")),
        })
    held_new = list(claim_audit.get("held_new_claim_ids") or [])
    contract: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "contract_type": "SCIENTIFIC_REOPEN_CHILD_PAPER_REVISION",
        "paper_id": _text(handoff.get("paper_id")),
        "attempt_sha256": _text(handoff.get("attempt_sha256")),
        "parent_paper_contract_sha256": _text(handoff.get("parent_paper_contract_sha256")),
        "reopened_contract_id": _text(handoff.get("reopened_contract_id")),
        "reopened_contract_sha256": _text(handoff.get("reopened_contract_sha256")),
        "paper_revision_handoff_sha256": _text(handoff.get("paper_revision_handoff_sha256")),
        "child_claim_audit_sha256": _text(claim_audit.get("child_claim_audit_sha256")),
        "supported_claims": supported_claims,
        "held_new_claim_ids": held_new,
        "manuscript_scope": manuscript_scope,
        "limitations_boundary": limitations,
        "status": STATUS,
        "child_claim_revision_frozen": True,
        "paper_preparation_review_eligible": True,
        "paper_preparation_authorized": False,
        "submission_eligible": False,
        "parent_submitted_bytes_immutable": True,
        "parent_claim_update_authorized": False,
        "new_claim_expansion_authorized": False,
        "held_new_claims_excluded_from_contract": True,
        "method_pass_not_principle_proof": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    contract["child_paper_contract_sha256"] = _digest(contract_identity(contract))
    contract["child_paper_contract_id"] = "child-paper-contract-" + contract["child_paper_contract_sha256"][:20]
    if not validate_child_paper_contract(contract):
        raise RuntimeError("generated child paper contract invalid")
    return contract


def validate_child_paper_contract(contract: Mapping[str, Any]) -> bool:
    if contract.get("contract_type") != "SCIENTIFIC_REOPEN_CHILD_PAPER_REVISION" or contract.get("status") != STATUS:
        return False
    if not _text(contract.get("paper_id")) or not _text(contract.get("attempt_sha256")) or not _text(contract.get("child_claim_audit_sha256")):
        return False
    claims = contract.get("supported_claims") or []
    if not isinstance(claims, list) or not claims:
        return False
    if len({row.get("claim_id") for row in claims if isinstance(row, Mapping)}) != len(claims):
        return False
    if any(not isinstance(row, Mapping) or not _text(row.get("claim_id")) or not _text(row.get("claim_text")) or row.get("claim_relation") == "NEW_CHILD_CLAIM" for row in claims):
        return False
    if any(contract.get(key) is not True for key in (
        "child_claim_revision_frozen", "paper_preparation_review_eligible", "parent_submitted_bytes_immutable",
        "held_new_claims_excluded_from_contract", "method_pass_not_principle_proof",
    )):
        return False
    if any(contract.get(key) is not False for key in (
        "paper_preparation_authorized", "submission_eligible", "parent_claim_update_authorized",
        "new_claim_expansion_authorized", "scientific_authority", "experiment_authority", "gpu_authority", "submission_authority",
    )):
        return False
    expected_sha = _digest(contract_identity(contract))
    return _text(contract.get("child_paper_contract_sha256")) == expected_sha and _text(contract.get("child_paper_contract_id")) == "child-paper-contract-" + expected_sha[:20]


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "paper-scientific-child-contracts" else root / "paper-scientific-child-contracts"


def publish_child_paper_contract(root: Path, contract: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_child_paper_contract(contract):
        raise RuntimeError("invalid child paper contract")
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{_slug(_text(contract.get('attempt_sha256')))}.json"
    if path.exists():
        existing = json.loads(path.read_text())
        if _text(existing.get("child_paper_contract_sha256")) == _text(contract.get("child_paper_contract_sha256")) and validate_child_paper_contract(existing):
            return existing
        raise RuntimeError("a different immutable child paper contract already exists for this attempt")
    tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(dict(contract), ensure_ascii=False, indent=2) + "\n"); os.replace(tmp, path)
    return dict(contract)


def load_child_paper_contract(root: Path, attempt_sha256: str) -> dict[str, Any]:
    path = _directory(root) / f"{_slug(attempt_sha256)}.json"
    if not path.exists():
        return {}
    try:
        contract = json.loads(path.read_text())
    except Exception:
        return {}
    return contract if validate_child_paper_contract(contract) else {}


def public_child_paper_contract(root: Path, attempt_sha256: str) -> dict[str, Any]:
    empty = {"status": "CHILD_PAPER_CONTRACT_REVISION_REQUIRED", "attempt_sha256": attempt_sha256, "child_paper_contract_id": "", "child_paper_contract_sha256": "", "supported_claims": 0, "held_new_claims": 0, "paper_preparation_review_eligible": False, "paper_preparation_authorized": False, "submission_eligible": False, "authority": dict(ZERO_AUTHORITY)}
    contract = load_child_paper_contract(root, attempt_sha256)
    if not contract:
        return empty
    return {**empty, "status": STATUS, "child_paper_contract_id": _text(contract.get("child_paper_contract_id")), "child_paper_contract_sha256": _text(contract.get("child_paper_contract_sha256")), "supported_claims": len(contract.get("supported_claims") or []), "held_new_claims": len(contract.get("held_new_claim_ids") or []), "paper_preparation_review_eligible": True, "paper_preparation_authorized": False, "submission_eligible": False}
