from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .reopened_scientific_contract import validate_reopened_scientific_contract

SCHEMA_VERSION = "1.0"
PASS_STATUS = "REOPEN_PROBLEM_GATE_PASS_METHOD_DESIGN_REVIEW_ELIGIBLE"
BLOCK_STATUS = "REOPEN_PROBLEM_GATE_BLOCKED"
REVIEWER_ROLE = "INDEPENDENT_PROBLEM_REVIEWER"
ZERO_AUTHORITY = {
    "scientific": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
    "submission": False,
}

REQUIRED_CHECKS = (
    "requested_delta_traceability_pass",
    "parent_contract_nonrewrite_pass",
    "scientific_question_nonredundant_pass",
    "reopen_needed_for_requested_delta_pass",
    "strongest_parent_reduction_checked",
    "falsifiable_prediction_testable_pass",
    "cheapest_falsifier_pre_outcome_pass",
    "evidence_plan_adjudicates_prediction_pass",
    "scope_bounded_pass",
    "stop_condition_decision_rule_pass",
    "outcome_independent_design_pass",
    "reviewer_feedback_diagnostic_only_pass",
    "existing_evidence_readjudication_pass",
    "support_failure_semantics_pass",
    "no_parent_claim_inheritance_pass",
)
REQUIRED_TEXT_FIELDS = (
    "decision_critical_question",
    "strongest_parent_reduction",
    "why_reopen_survives_parent_reduction",
    "failure_if_false",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown-contract"


def _text(value: Any) -> str:
    return str(value or "").strip()


def audit_packet_identity(packet: Mapping[str, Any]) -> dict[str, Any]:
    checks = packet.get("checks") or {}
    return {
        "audit_id": packet.get("audit_id"),
        "reviewer_role": packet.get("reviewer_role"),
        "reviewer_ref_sha256": packet.get("reviewer_ref_sha256"),
        "reviewed_at": packet.get("reviewed_at"),
        "contract_sha256": packet.get("contract_sha256"),
        "checks": checks,
        "decision_critical_question_sha256": packet.get("decision_critical_question_sha256"),
        "strongest_parent_reduction_sha256": packet.get("strongest_parent_reduction_sha256"),
        "why_reopen_survives_parent_reduction_sha256": packet.get("why_reopen_survives_parent_reduction_sha256"),
        "failure_if_false_sha256": packet.get("failure_if_false_sha256"),
    }


def normalize_problem_gate_packet(contract: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_reopened_scientific_contract(contract):
        raise RuntimeError("valid reopened scientific contract required")
    source = dict(packet) if isinstance(packet, Mapping) else {}
    reviewer_ref = _text(source.get("reviewer_ref"))
    if not reviewer_ref:
        raise RuntimeError("independent problem reviewer reference required")
    audit_id = _text(source.get("audit_id"))
    if not audit_id:
        raise RuntimeError("problem gate audit id required")
    reviewed_at = _text(source.get("reviewed_at"))
    if not reviewed_at:
        raise RuntimeError("problem gate review timestamp required")
    if _text(source.get("reviewer_role")) != REVIEWER_ROLE:
        raise RuntimeError(f"reviewer_role must be {REVIEWER_ROLE}")
    checks_source = source.get("checks") or {}
    if not isinstance(checks_source, Mapping):
        raise RuntimeError("problem gate checks must be an object")
    checks = {key: checks_source.get(key) is True for key in REQUIRED_CHECKS}
    if set(checks_source.keys()) != set(REQUIRED_CHECKS):
        raise RuntimeError("problem gate checks must match required check set exactly")
    texts: dict[str, str] = {}
    for field in REQUIRED_TEXT_FIELDS:
        value = _text(source.get(field))
        if not value:
            raise RuntimeError(f"problem gate field required: {field}")
        texts[field] = value
    contract_sha = _text(source.get("contract_sha256"))
    if contract_sha != _text(contract.get("contract_sha256")):
        raise RuntimeError("problem gate packet contract SHA mismatch")
    for key in (
        "scientific_authority",
        "paper_design_authority",
        "method_design_authority",
        "experiment_authority",
        "p0_authority",
        "gpu_authority",
        "claim_expansion_authority",
    ):
        if source.get(key) is True:
            raise RuntimeError(f"problem gate packet may not grant authority: {key}")
    normalized: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": audit_id,
        "reviewer_role": REVIEWER_ROLE,
        "reviewer_ref": reviewer_ref,
        "reviewer_ref_sha256": hashlib.sha256(reviewer_ref.encode()).hexdigest(),
        "reviewed_at": reviewed_at,
        "contract_sha256": contract_sha,
        "checks": checks,
        **texts,
    }
    for field in REQUIRED_TEXT_FIELDS:
        normalized[field + "_sha256"] = hashlib.sha256(texts[field].encode()).hexdigest()
    normalized["audit_packet_sha256"] = _digest(audit_packet_identity(normalized))
    return normalized


def validate_problem_gate_packet(packet: Mapping[str, Any]) -> bool:
    if packet.get("reviewer_role") != REVIEWER_ROLE:
        return False
    reviewer_ref = _text(packet.get("reviewer_ref"))
    if not reviewer_ref or hashlib.sha256(reviewer_ref.encode()).hexdigest() != _text(packet.get("reviewer_ref_sha256")):
        return False
    checks = packet.get("checks") or {}
    if not isinstance(checks, Mapping) or set(checks.keys()) != set(REQUIRED_CHECKS):
        return False
    if any(not isinstance(checks.get(key), bool) for key in REQUIRED_CHECKS):
        return False
    for field in REQUIRED_TEXT_FIELDS:
        value = _text(packet.get(field))
        if not value or hashlib.sha256(value.encode()).hexdigest() != _text(packet.get(field + "_sha256")):
            return False
    if not _text(packet.get("audit_id")) or not _text(packet.get("reviewed_at")) or not _text(packet.get("contract_sha256")):
        return False
    return _text(packet.get("audit_packet_sha256")) == _digest(audit_packet_identity(packet))


def receipt_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract_id": receipt.get("contract_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "parent_contract_sha256": receipt.get("parent_contract_sha256"),
        "research_os_handoff_sha256": receipt.get("research_os_handoff_sha256"),
        "audit_packet_sha256": receipt.get("audit_packet_sha256"),
        "failed_checks": receipt.get("failed_checks") or [],
        "status": receipt.get("status"),
        "pass": receipt.get("pass"),
        "paper_design_eligible": receipt.get("paper_design_eligible"),
        "method_design_review_eligible": receipt.get("method_design_review_eligible"),
    }


def build_reopen_problem_gate_receipt(*, contract: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_reopened_scientific_contract(contract):
        raise RuntimeError("valid reopened scientific contract required")
    normalized = normalize_problem_gate_packet(contract, packet)
    if not validate_problem_gate_packet(normalized):
        raise RuntimeError("normalized problem gate packet failed validation")
    failed = [key for key in REQUIRED_CHECKS if normalized["checks"].get(key) is not True]
    passed = not failed
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "reopen-scientific-problem-gate",
        "contract_id": str(contract.get("contract_id") or ""),
        "contract_sha256": str(contract.get("contract_sha256") or ""),
        "parent_contract_sha256": str(contract.get("parent_contract_sha256") or ""),
        "research_os_handoff_sha256": str(contract.get("research_os_handoff_sha256") or ""),
        "audit_id": normalized["audit_id"],
        "reviewer_role": normalized["reviewer_role"],
        "reviewer_ref": normalized["reviewer_ref"],
        "reviewer_ref_sha256": normalized["reviewer_ref_sha256"],
        "reviewed_at": normalized["reviewed_at"],
        "audit_packet_sha256": normalized["audit_packet_sha256"],
        "checks": dict(normalized["checks"]),
        "failed_checks": failed,
        "decision_critical_question_sha256": normalized["decision_critical_question_sha256"],
        "strongest_parent_reduction_sha256": normalized["strongest_parent_reduction_sha256"],
        "why_reopen_survives_parent_reduction_sha256": normalized["why_reopen_survives_parent_reduction_sha256"],
        "failure_if_false_sha256": normalized["failure_if_false_sha256"],
        "status": PASS_STATUS if passed else BLOCK_STATUS,
        "pass": passed,
        "paper_design_eligible": passed,
        "method_design_review_eligible": passed,
        "parent_claim_status_unchanged": True,
        "reviewer_feedback_is_diagnostic_context_not_evidence": True,
        "existing_evidence_still_requires_child_contract_readjudication": True,
        "problem_gate_authority": False,
        "paper_design_authority": False,
        "method_design_authority": False,
        "experiment_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
        "claim_expansion_authority": False,
        "submission_authority": False,
    }
    receipt["problem_gate_receipt_sha256"] = _digest(receipt_identity(receipt))
    return receipt


def validate_reopen_problem_gate_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "reopen-scientific-problem-gate" or receipt.get("status") not in {PASS_STATUS, BLOCK_STATUS}:
        return False
    failed = list(receipt.get("failed_checks") or [])
    checks = receipt.get("checks") or {}
    if not isinstance(checks, Mapping) or set(checks.keys()) != set(REQUIRED_CHECKS):
        return False
    expected_failed = [key for key in REQUIRED_CHECKS if checks.get(key) is not True]
    if failed != expected_failed:
        return False
    passed = not failed
    if receipt.get("pass") is not passed or receipt.get("status") != (PASS_STATUS if passed else BLOCK_STATUS):
        return False
    if receipt.get("paper_design_eligible") is not passed or receipt.get("method_design_review_eligible") is not passed:
        return False
    if receipt.get("parent_claim_status_unchanged") is not True:
        return False
    if receipt.get("reviewer_feedback_is_diagnostic_context_not_evidence") is not True:
        return False
    if receipt.get("existing_evidence_still_requires_child_contract_readjudication") is not True:
        return False
    for key in (
        "problem_gate_authority",
        "paper_design_authority",
        "method_design_authority",
        "experiment_authority",
        "p0_authority",
        "gpu_authority",
        "claim_expansion_authority",
        "submission_authority",
    ):
        if receipt.get(key) is not False:
            return False
    reviewer_ref = _text(receipt.get("reviewer_ref"))
    if not reviewer_ref or hashlib.sha256(reviewer_ref.encode()).hexdigest() != _text(receipt.get("reviewer_ref_sha256")):
        return False
    return _text(receipt.get("problem_gate_receipt_sha256")) == _digest(receipt_identity(receipt))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "scientific-contract-problem-gates" else root / "scientific-contract-problem-gates"


def publish_reopen_problem_gate_receipt(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_reopen_problem_gate_receipt(receipt):
        raise RuntimeError("invalid reopen problem gate receipt")
    directory = _directory(root)
    directory.mkdir(parents=True, exist_ok=True)
    contract_id = _text(receipt.get("contract_id"))
    path = directory / f"{_slug(contract_id)}.json"
    lock = directory / f".{_slug(contract_id)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "schema_version": SCHEMA_VERSION,
            "contract_id": contract_id,
            "contract_sha256": _text(receipt.get("contract_sha256")),
            "events": [],
            "authority": dict(ZERO_AUTHORITY),
        }
        if _text(row.get("contract_sha256")) != _text(receipt.get("contract_sha256")):
            raise RuntimeError("problem gate ledger contract SHA mismatch")
        for event in row.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _text(prior.get("problem_gate_receipt_sha256")) == _text(receipt.get("problem_gate_receipt_sha256")):
                return row
        event = {
            "event_type": "reopen-scientific-problem-gate",
            "receipt": dict(receipt),
            "recorded_at": _text(receipt.get("reviewed_at")) or _now(),
            "scientific_authority": False,
            "paper_design_authority": False,
            "method_design_authority": False,
            "experiment_authority": False,
            "p0_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        event["event_id"] = _digest([contract_id, len(row.get("events") or []), receipt.get("problem_gate_receipt_sha256"), event["recorded_at"]])[:24]
        row.setdefault("events", []).append(event)
        row["updated_at"] = event["recorded_at"]
        errors = validate_reopen_problem_gate_ledger(row)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return row


def validate_reopen_problem_gate_ledger(row: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if (row.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("reopen-problem-gate-ledger-authority-leak")
    contract_id = _text(row.get("contract_id"))
    contract_sha = _text(row.get("contract_sha256"))
    seen: set[str] = set()
    for index, event in enumerate(row.get("events") or []):
        if not isinstance(event, Mapping) or event.get("event_type") != "reopen-scientific-problem-gate":
            errors.append("reopen-problem-gate-event-invalid")
            continue
        receipt = event.get("receipt") or {}
        if not isinstance(receipt, Mapping) or not validate_reopen_problem_gate_receipt(receipt):
            errors.append("reopen-problem-gate-receipt-invalid")
            continue
        if _text(receipt.get("contract_id")) != contract_id or _text(receipt.get("contract_sha256")) != contract_sha:
            errors.append("reopen-problem-gate-contract-lineage-mismatch")
        receipt_sha = _text(receipt.get("problem_gate_receipt_sha256"))
        if receipt_sha in seen:
            errors.append("reopen-problem-gate-duplicate-receipt")
        expected_event_id = _digest([contract_id, index, receipt_sha, _text(event.get("recorded_at"))])[:24]
        if _text(event.get("event_id")) != expected_event_id:
            errors.append("reopen-problem-gate-event-id-invalid")
        if any(event.get(key) is True for key in (
            "scientific_authority", "paper_design_authority", "method_design_authority", "experiment_authority", "p0_authority", "gpu_authority", "submission_authority"
        )):
            errors.append("reopen-problem-gate-event-authority-leak")
        seen.add(receipt_sha)
    return list(dict.fromkeys(errors))


def load_latest_reopen_problem_gate(root: Path, contract_id: str) -> dict[str, Any]:
    path = _directory(root) / f"{_slug(contract_id)}.json"
    if not path.exists():
        return {}
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"_invalid": True, "_errors": ["reopen-problem-gate-ledger-unreadable"]}
    errors = validate_reopen_problem_gate_ledger(row)
    if errors:
        return {"_invalid": True, "_errors": errors}
    for event in reversed(row.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if isinstance(receipt, Mapping) and validate_reopen_problem_gate_receipt(receipt):
            return dict(receipt)
    return {}


def public_reopen_problem_gate_summary(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if receipt.get("_invalid") is True:
        return {
            "status": "REOPEN_PROBLEM_GATE_LEDGER_INVALID",
            "pass": False,
            "failed_checks": [],
            "problem_gate_receipt_sha256": "",
            "paper_design_eligible": False,
            "method_design_review_eligible": False,
            "validation_errors": list(receipt.get("_errors") or []),
            "authority": dict(ZERO_AUTHORITY),
        }
    if not receipt:
        return {
            "status": "REOPEN_PROBLEM_GATE_REQUIRED",
            "pass": False,
            "failed_checks": [],
            "problem_gate_receipt_sha256": "",
            "paper_design_eligible": False,
            "method_design_review_eligible": False,
            "validation_errors": [],
            "authority": dict(ZERO_AUTHORITY),
        }
    if not validate_reopen_problem_gate_receipt(receipt):
        return {
            "status": "REOPEN_PROBLEM_GATE_LEDGER_INVALID",
            "pass": False,
            "failed_checks": [],
            "problem_gate_receipt_sha256": "",
            "paper_design_eligible": False,
            "method_design_review_eligible": False,
            "validation_errors": ["reopen-problem-gate-receipt-invalid"],
            "authority": dict(ZERO_AUTHORITY),
        }
    return {
        "status": str(receipt.get("status") or ""),
        "pass": receipt.get("pass") is True,
        "failed_checks": list(receipt.get("failed_checks") or []),
        "problem_gate_receipt_sha256": str(receipt.get("problem_gate_receipt_sha256") or ""),
        "audit_id": str(receipt.get("audit_id") or ""),
        "reviewer_role": str(receipt.get("reviewer_role") or ""),
        "reviewer_ref_sha256": str(receipt.get("reviewer_ref_sha256") or ""),
        "paper_design_eligible": receipt.get("paper_design_eligible") is True,
        "method_design_review_eligible": receipt.get("method_design_review_eligible") is True,
        "parent_claim_status_unchanged": True,
        "reviewer_feedback_is_diagnostic_context_not_evidence": True,
        "validation_errors": [],
        "authority": dict(ZERO_AUTHORITY),
    }
