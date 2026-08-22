from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .reopened_p0_result_adjudication import METHOD_PASS, validate_p0_adjudication, validate_p0_result_packet
from .reopened_scientific_contract import validate_reopened_scientific_contract
from .submission_attempt_lineage import validate_attempt_plan

SCHEMA_VERSION = "1.0"
STATUS = "SCIENTIFIC_REOPEN_EVIDENCE_READY_CHILD_CLAIM_AUDIT_REQUIRED"
ALLOWED_EVIDENCE_ROLES = {"PRIMARY", "MECHANISM", "SUPPORTING", "BOUNDARY"}
ALLOWED_CLAIM_RELATIONS = {"EXISTING_PARENT_CLAIM", "BOUNDARY_CLARIFICATION", "NEW_CHILD_CLAIM"}
ZERO_AUTHORITY = {"scientific": False, "claim_update": False, "paper_preparation": False, "submission": False, "experiment": False, "gpu": False}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown"


def _candidate_claims(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise RuntimeError("child paper revision handoff requires at least one candidate claim")
    rows: list[dict[str, str]] = []
    ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise RuntimeError(f"candidate claim must be object: {index}")
        claim_id = _text(item.get("claim_id")); claim_text = _text(item.get("claim_text")); role = _text(item.get("evidence_role")).upper(); relation = _text(item.get("claim_relation")).upper()
        if not claim_id or not claim_text or role not in ALLOWED_EVIDENCE_ROLES or relation not in ALLOWED_CLAIM_RELATIONS:
            raise RuntimeError(f"candidate claim incomplete: {index}")
        if claim_id in ids:
            raise RuntimeError("candidate claim ids must be unique")
        ids.add(claim_id)
        rows.append({"claim_id": claim_id, "claim_text": claim_text, "evidence_role": role, "claim_relation": relation})
    return rows


def handoff_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "paper_id", "parent_paper_contract_sha256", "attempt_sha256", "reopened_contract_id",
        "reopened_contract_sha256", "p0_plan_sha256", "p0_result_packet_sha256",
        "p0_adjudication_sha256", "evidence_bundle_sha256", "candidate_claims_sha256",
        "status",
    )}


def build_scientific_evidence_paper_handoff(
    *,
    attempt_plan: Mapping[str, Any],
    reopened_contract: Mapping[str, Any],
    p0_result_packet: Mapping[str, Any],
    p0_adjudication: Mapping[str, Any],
    revision_spec: Mapping[str, Any],
) -> dict[str, Any]:
    if not validate_attempt_plan(attempt_plan):
        raise RuntimeError("valid submission attempt plan required")
    if attempt_plan.get("requires_explicit_scientific_reopen") is not True or attempt_plan.get("machine_preparation_eligible") is not False:
        raise RuntimeError("paper evidence handoff requires a scientific-reopen submission attempt")
    if not validate_reopened_scientific_contract(reopened_contract):
        raise RuntimeError("valid reopened scientific contract required")
    if _text(reopened_contract.get("source_attempt_sha256")) != _text(attempt_plan.get("attempt_sha256")):
        raise RuntimeError("reopened scientific contract does not belong to this submission attempt")
    if _text(reopened_contract.get("parent_paper_id")) != _text(attempt_plan.get("paper_id")) or _text(reopened_contract.get("parent_contract_sha256")) != _text(attempt_plan.get("contract_sha256")):
        raise RuntimeError("reopened scientific contract parent paper lineage mismatch")
    if not validate_p0_result_packet(p0_result_packet) or not validate_p0_adjudication(p0_adjudication):
        raise RuntimeError("valid confirmatory P0 result/adjudication required")
    if p0_adjudication.get("status") != METHOD_PASS or p0_adjudication.get("method_verdict") != "METHOD-PASS" or p0_adjudication.get("method_verdict_authorized") is not True:
        raise RuntimeError("child paper evidence promotion requires independently adjudicated P0 METHOD-PASS")
    if _text(p0_result_packet.get("contract_id")) != _text(reopened_contract.get("contract_id")) or _text(p0_result_packet.get("contract_sha256")) != _text(reopened_contract.get("contract_sha256")):
        raise RuntimeError("P0 result/reopened scientific contract lineage mismatch")
    if _text(p0_adjudication.get("p0_result_packet_sha256")) != _text(p0_result_packet.get("p0_result_packet_sha256")) or _text(p0_adjudication.get("p0_plan_sha256")) != _text(p0_result_packet.get("p0_plan_sha256")):
        raise RuntimeError("P0 adjudication/result lineage mismatch")

    spec = dict(revision_spec or {})
    claims = _candidate_claims(spec.get("candidate_claims"))
    revision_summary = _text(spec.get("revision_summary"))
    if not revision_summary:
        raise RuntimeError("child paper revision summary required")
    if spec.get("parent_submitted_bytes_will_be_modified") is not False:
        raise RuntimeError("parent submitted bytes must remain immutable")
    if spec.get("automatic_claim_upgrade_requested") is not False:
        raise RuntimeError("automatic claim upgrade is forbidden")
    if spec.get("outcome_driven_claim_selection_used") is not False:
        raise RuntimeError("outcome-driven claim selection is forbidden")

    evidence_bundle = {
        "p0_result_packet_sha256": _text(p0_result_packet.get("p0_result_packet_sha256")),
        "p0_adjudication_sha256": _text(p0_adjudication.get("p0_adjudication_sha256")),
        "p0_plan_sha256": _text(p0_result_packet.get("p0_plan_sha256")),
        "artifact_manifest_sha256": _text(p0_result_packet.get("artifact_manifest_sha256")),
        "analysis_receipt_sha256": _text(p0_result_packet.get("analysis_receipt_sha256")),
        "recompute_receipt_sha256": _text(p0_result_packet.get("recompute_receipt_sha256")),
        "primary_metric_name": _text(p0_result_packet.get("primary_metric_name")),
        "primary_metric_value": p0_result_packet.get("primary_metric_value"),
        "primary_test_p_value": p0_result_packet.get("primary_test_p_value"),
        "same_information_baseline_summary_sha256": _text(p0_result_packet.get("same_information_baseline_summary_sha256")),
        "method_verdict": "METHOD-PASS",
        "method_realization_scope_only": True,
        "principle_proven": False,
    }
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "scientific-reopen-paper-revision-handoff",
        "paper_id": _text(attempt_plan.get("paper_id")),
        "parent_paper_contract_sha256": _text(attempt_plan.get("contract_sha256")),
        "attempt_id": _text(attempt_plan.get("attempt_id")),
        "attempt_sha256": _text(attempt_plan.get("attempt_sha256")),
        "reopened_contract_id": _text(reopened_contract.get("contract_id")),
        "reopened_contract_sha256": _text(reopened_contract.get("contract_sha256")),
        "p0_plan_sha256": _text(p0_result_packet.get("p0_plan_sha256")),
        "p0_result_packet_sha256": _text(p0_result_packet.get("p0_result_packet_sha256")),
        "p0_adjudication_sha256": _text(p0_adjudication.get("p0_adjudication_sha256")),
        "evidence_bundle": evidence_bundle,
        "evidence_bundle_sha256": _digest(evidence_bundle),
        "candidate_claims": claims,
        "candidate_claims_sha256": _digest(claims),
        "revision_summary": revision_summary,
        "status": STATUS,
        "child_manuscript_revision_eligible": True,
        "child_claim_audit_required": True,
        "child_claim_audit_passed": False,
        "claim_upgrade_authorized": False,
        "claim_expansion_authorized": False,
        "paper_preparation_eligible": False,
        "submission_eligible": False,
        "parent_submitted_bytes_immutable": True,
        "parent_paper_claim_status_unchanged": True,
        "child_claim_status_unchanged_pending_audit": True,
        "outcome_driven_claim_selection_used": False,
        "principle_status_not_used_as_claim_proof": True,
        "scientific_authority": False,
        "claim_update_authority": False,
        "submission_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }
    receipt["paper_revision_handoff_sha256"] = _digest(handoff_identity(receipt))
    if not validate_scientific_evidence_paper_handoff(receipt):
        raise RuntimeError("generated scientific-evidence paper handoff invalid")
    return receipt


def validate_scientific_evidence_paper_handoff(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "scientific-reopen-paper-revision-handoff" or receipt.get("status") != STATUS:
        return False
    if not _text(receipt.get("paper_id")) or not _text(receipt.get("attempt_sha256")) or not _text(receipt.get("reopened_contract_sha256")):
        return False
    if _digest(receipt.get("evidence_bundle") or {}) != _text(receipt.get("evidence_bundle_sha256")):
        return False
    claims = receipt.get("candidate_claims") or []
    if not isinstance(claims, list) or not claims or _digest(claims) != _text(receipt.get("candidate_claims_sha256")):
        return False
    if any(receipt.get(key) is not True for key in (
        "child_manuscript_revision_eligible", "child_claim_audit_required", "parent_submitted_bytes_immutable",
        "parent_paper_claim_status_unchanged", "child_claim_status_unchanged_pending_audit",
        "principle_status_not_used_as_claim_proof",
    )):
        return False
    if receipt.get("outcome_driven_claim_selection_used") is not False:
        return False
    if any(receipt.get(key) is not False for key in (
        "child_claim_audit_passed", "claim_upgrade_authorized", "claim_expansion_authorized",
        "paper_preparation_eligible", "submission_eligible", "scientific_authority",
        "claim_update_authority", "submission_authority", "experiment_authority", "gpu_authority",
    )):
        return False
    bundle = receipt.get("evidence_bundle") or {}
    if bundle.get("method_verdict") != "METHOD-PASS" or bundle.get("method_realization_scope_only") is not True or bundle.get("principle_proven") is not False:
        return False
    return _text(receipt.get("paper_revision_handoff_sha256")) == _digest(handoff_identity(receipt))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "paper-scientific-revision-handoffs" else root / "paper-scientific-revision-handoffs"


def validate_paper_revision_handoff_ledger(ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []; seen: set[str] = set(); attempt_sha = _text(ledger.get("attempt_sha256"))
    if (ledger.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("paper-revision-handoff-ledger-authority-leak")
    for index, event in enumerate(ledger.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if not isinstance(receipt, Mapping) or not validate_scientific_evidence_paper_handoff(receipt):
            errors.append("paper-revision-handoff-receipt-invalid"); continue
        if _text(receipt.get("attempt_sha256")) != attempt_sha:
            errors.append("paper-revision-handoff-attempt-lineage-mismatch")
        sha = _text(receipt.get("paper_revision_handoff_sha256"))
        if sha in seen:
            errors.append("paper-revision-handoff-duplicate")
        recorded = _text(event.get("recorded_at"))
        if _text(event.get("event_id")) != _digest([attempt_sha, index, sha, recorded])[:24]:
            errors.append("paper-revision-handoff-event-id-invalid")
        seen.add(sha)
    return list(dict.fromkeys(errors))


def publish_scientific_evidence_paper_handoff(root: Path, receipt: Mapping[str, Any], *, recorded_at: str) -> dict[str, Any]:
    if not validate_scientific_evidence_paper_handoff(receipt):
        raise RuntimeError("invalid scientific-evidence paper handoff")
    at = _text(recorded_at)
    if not at:
        raise RuntimeError("paper revision handoff recorded_at required")
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    attempt_sha = _text(receipt.get("attempt_sha256")); path = directory / f"{_slug(attempt_sha)}.json"; lock = directory / f".{_slug(attempt_sha)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ledger = json.loads(path.read_text()) if path.exists() else {"schema_version": SCHEMA_VERSION, "paper_id": _text(receipt.get("paper_id")), "attempt_sha256": attempt_sha, "events": [], "authority": dict(ZERO_AUTHORITY)}
        sha = _text(receipt.get("paper_revision_handoff_sha256"))
        for event in ledger.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _text(prior.get("paper_revision_handoff_sha256")) == sha:
                return ledger
        event = {"event_type": "scientific-reopen-paper-revision-handoff", "receipt": dict(receipt), "recorded_at": at, "claim_update_authority": False, "submission_authority": False}
        event["event_id"] = _digest([attempt_sha, len(ledger.get("events") or []), sha, at])[:24]
        ledger.setdefault("events", []).append(event); ledger["updated_at"] = at
        errors = validate_paper_revision_handoff_ledger(ledger)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"); os.replace(tmp, path)
        return ledger


def public_scientific_evidence_paper_handoff(root: Path, attempt_sha256: str) -> dict[str, Any]:
    empty = {"status": "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_REQUIRED", "attempt_sha256": attempt_sha256, "paper_revision_handoff_sha256": "", "reopened_contract_id": "", "candidate_claims": 0, "child_manuscript_revision_eligible": False, "child_claim_audit_required": True, "claim_upgrade_authorized": False, "paper_preparation_eligible": False, "submission_eligible": False, "authority": dict(ZERO_AUTHORITY)}
    path = _directory(root) / f"{_slug(attempt_sha256)}.json"
    if not path.exists():
        return empty
    try:
        ledger = json.loads(path.read_text())
    except Exception:
        return {**empty, "status": "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_LEDGER_INVALID"}
    if validate_paper_revision_handoff_ledger(ledger):
        return {**empty, "status": "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_LEDGER_INVALID"}
    receipts = [event.get("receipt") or {} for event in ledger.get("events") or [] if isinstance(event, Mapping) and isinstance(event.get("receipt"), Mapping)]
    receipt = receipts[-1] if receipts else {}
    if not receipt or not validate_scientific_evidence_paper_handoff(receipt):
        return {**empty, "status": "SCIENTIFIC_EVIDENCE_PAPER_HANDOFF_LEDGER_INVALID"}
    return {**empty, "status": STATUS, "paper_revision_handoff_sha256": _text(receipt.get("paper_revision_handoff_sha256")), "reopened_contract_id": _text(receipt.get("reopened_contract_id")), "candidate_claims": len(receipt.get("candidate_claims") or []), "child_manuscript_revision_eligible": True, "child_claim_audit_required": True, "claim_upgrade_authorized": False, "paper_preparation_eligible": False, "submission_eligible": False}
