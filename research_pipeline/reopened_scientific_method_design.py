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
from .reopened_scientific_problem_gate import PASS_STATUS as PROBLEM_GATE_PASS, validate_reopen_problem_gate_receipt

SCHEMA_VERSION = "1.0"
DESIGN_STATUS = "REOPEN_METHOD_DESIGN_FROZEN_AWAITING_INDEPENDENT_REVIEW"
REVIEW_PASS = "REOPEN_METHOD_REVIEW_PASS_BLUEPRINT_DESIGN_ELIGIBLE"
REVIEW_BLOCK = "REOPEN_METHOD_REVIEW_BLOCKED"
REVIEWER_ROLE = "INDEPENDENT_METHOD_REVIEWER"
ZERO_AUTHORITY = {
    "scientific": False,
    "paper_design": False,
    "method": False,
    "experiment_blueprint": False,
    "experiment": False,
    "local_validation": False,
    "p0": False,
    "gpu": False,
    "submission": False,
}

REQUIRED_METHOD_FIELDS = (
    "method_name",
    "method_thesis",
    "formal_objects",
    "mechanism",
    "identifiability_boundary",
    "strongest_same_information_reduction",
    "cheapest_local_falsifier",
    "resource_budget",
    "stop_rules",
    "experiment_blueprint_outline",
)
REQUIRED_REVIEW_CHECKS = (
    "problem_contract_alignment_pass",
    "formal_objects_sufficiently_defined_pass",
    "method_not_generic_relabeling_pass",
    "strongest_same_information_reduction_survives",
    "identifiability_boundary_explicit_pass",
    "cheapest_local_falsifier_pre_outcome_pass",
    "hidden_outcome_search_not_required_pass",
    "same_information_baselines_matched_pass",
    "resource_budget_bounded_pass",
    "stop_rules_decision_complete_pass",
    "experiment_blueprint_separated_from_execution_pass",
    "reviewer_feedback_diagnostic_only_pass",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _text(value: Any) -> str:
    return str(value or "").strip()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown-contract"


def method_design_identity(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract_id": row.get("contract_id"),
        "contract_sha256": row.get("contract_sha256"),
        "problem_gate_receipt_sha256": row.get("problem_gate_receipt_sha256"),
        "method_spec_sha256": row.get("method_spec_sha256"),
        "same_information_baselines_digest": row.get("same_information_baselines_digest"),
        "status": row.get("status"),
    }


def build_reopen_method_design(*, contract: Mapping[str, Any], problem_gate_receipt: Mapping[str, Any], method_spec: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_reopened_scientific_contract(contract):
        raise RuntimeError("valid reopened scientific contract required")
    if not validate_reopen_problem_gate_receipt(problem_gate_receipt) or problem_gate_receipt.get("status") != PROBLEM_GATE_PASS:
        raise RuntimeError("reopen Problem Gate PASS required before method design")
    if _text(problem_gate_receipt.get("contract_sha256")) != _text(contract.get("contract_sha256")):
        raise RuntimeError("method design Problem Gate/contract lineage mismatch")
    spec = dict(method_spec) if isinstance(method_spec, Mapping) else {}
    missing = [field for field in REQUIRED_METHOD_FIELDS if not spec.get(field)]
    if missing:
        raise RuntimeError("method design fields missing: " + ",".join(missing))
    baselines = spec.get("same_information_baselines") or []
    if not isinstance(baselines, list) or len(baselines) < 2:
        raise RuntimeError("method design requires at least two same-information baselines")
    for index, baseline in enumerate(baselines):
        if not isinstance(baseline, Mapping) or not _text(baseline.get("name")) or not _text(baseline.get("same_information_access")) or not _text(baseline.get("reduction_test")):
            raise RuntimeError(f"invalid same-information baseline:{index}")
    stop_rules = spec.get("stop_rules") or []
    if not isinstance(stop_rules, list) or len(stop_rules) < 2 or any(not _text(x) for x in stop_rules):
        raise RuntimeError("method design requires at least two explicit stop rules")
    budget = spec.get("resource_budget") or {}
    if not isinstance(budget, Mapping) or not budget or any(float(budget.get(key) or 0) <= 0 for key in ("max_local_units", "max_provider_calls", "max_gpu_hours")):
        raise RuntimeError("method design resource budget must bound local units, provider calls, and GPU hours")
    normalized_spec = {key: spec[key] for key in REQUIRED_METHOD_FIELDS}
    normalized_spec["same_information_baselines"] = [dict(x) for x in baselines]
    normalized_spec["method_freeze_requirements"] = [str(x) for x in spec.get("method_freeze_requirements") or [] if str(x).strip()]
    method_spec_sha = _digest(normalized_spec)
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "reopen-method-design",
        "contract_id": _text(contract.get("contract_id")),
        "contract_sha256": _text(contract.get("contract_sha256")),
        "parent_contract_sha256": _text(contract.get("parent_contract_sha256")),
        "problem_gate_receipt_sha256": _text(problem_gate_receipt.get("problem_gate_receipt_sha256")),
        "method_spec": normalized_spec,
        "method_spec_sha256": method_spec_sha,
        "same_information_baselines_digest": _digest(normalized_spec["same_information_baselines"]),
        "status": DESIGN_STATUS,
        "method_frozen": True,
        "experiment_blueprint_design_eligible": False,
        "local_validation_eligible": False,
        "problem_gate_pass_is_not_method_execution_authority": True,
        "scientific_authority": False,
        "paper_design_authority": False,
        "method_authority": False,
        "experiment_blueprint_authority": False,
        "experiment_authority": False,
        "local_validation_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    row["method_design_sha256"] = _digest(method_design_identity(row))
    return row


def validate_reopen_method_design(row: Mapping[str, Any]) -> bool:
    if row.get("receipt_type") != "reopen-method-design" or row.get("status") != DESIGN_STATUS or row.get("method_frozen") is not True:
        return False
    spec = row.get("method_spec") or {}
    if not isinstance(spec, Mapping) or any(not spec.get(field) for field in REQUIRED_METHOD_FIELDS):
        return False
    baselines = spec.get("same_information_baselines") or []
    if not isinstance(baselines, list) or len(baselines) < 2 or _text(row.get("same_information_baselines_digest")) != _digest(baselines):
        return False
    if _text(row.get("method_spec_sha256")) != _digest(dict(spec)):
        return False
    if row.get("experiment_blueprint_design_eligible") is not False or row.get("local_validation_eligible") is not False:
        return False
    if row.get("problem_gate_pass_is_not_method_execution_authority") is not True:
        return False
    for key in ("scientific_authority", "paper_design_authority", "method_authority", "experiment_blueprint_authority", "experiment_authority", "local_validation_authority", "p0_authority", "gpu_authority", "submission_authority"):
        if row.get(key) is not False:
            return False
    return _text(row.get("method_design_sha256")) == _digest(method_design_identity(row))


def method_review_identity(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract_id": row.get("contract_id"),
        "contract_sha256": row.get("contract_sha256"),
        "method_design_sha256": row.get("method_design_sha256"),
        "reviewer_ref_sha256": row.get("reviewer_ref_sha256"),
        "reviewed_at": row.get("reviewed_at"),
        "checks": row.get("checks") or {},
        "failed_checks": row.get("failed_checks") or [],
        "status": row.get("status"),
        "experiment_blueprint_design_eligible": row.get("experiment_blueprint_design_eligible"),
    }


def build_reopen_method_review(*, method_design: Mapping[str, Any], review_packet: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_reopen_method_design(method_design):
        raise RuntimeError("valid frozen reopen method design required")
    packet = dict(review_packet) if isinstance(review_packet, Mapping) else {}
    if _text(packet.get("reviewer_role")) != REVIEWER_ROLE:
        raise RuntimeError(f"reviewer_role must be {REVIEWER_ROLE}")
    reviewer_ref = _text(packet.get("reviewer_ref")); reviewed_at = _text(packet.get("reviewed_at"))
    if not reviewer_ref or not reviewed_at:
        raise RuntimeError("independent method reviewer reference and timestamp required")
    checks_source = packet.get("checks") or {}
    if not isinstance(checks_source, Mapping) or set(checks_source.keys()) != set(REQUIRED_REVIEW_CHECKS):
        raise RuntimeError("method review checks must match required set exactly")
    checks = {key: checks_source.get(key) is True for key in REQUIRED_REVIEW_CHECKS}
    reduction_analysis = _text(packet.get("reduction_analysis")); failure_if_blocked = _text(packet.get("failure_if_blocked"))
    if not reduction_analysis or not failure_if_blocked:
        raise RuntimeError("method review reduction_analysis and failure_if_blocked are required")
    failed = [key for key in REQUIRED_REVIEW_CHECKS if checks[key] is not True]
    passed = not failed
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "reopen-method-review",
        "contract_id": _text(method_design.get("contract_id")),
        "contract_sha256": _text(method_design.get("contract_sha256")),
        "method_design_sha256": _text(method_design.get("method_design_sha256")),
        "reviewer_role": REVIEWER_ROLE,
        "reviewer_ref": reviewer_ref,
        "reviewer_ref_sha256": hashlib.sha256(reviewer_ref.encode()).hexdigest(),
        "reviewed_at": reviewed_at,
        "checks": checks,
        "failed_checks": failed,
        "reduction_analysis_sha256": hashlib.sha256(reduction_analysis.encode()).hexdigest(),
        "failure_if_blocked_sha256": hashlib.sha256(failure_if_blocked.encode()).hexdigest(),
        "status": REVIEW_PASS if passed else REVIEW_BLOCK,
        "pass": passed,
        "experiment_blueprint_design_eligible": passed,
        "local_validation_eligible": False,
        "method_frozen": True,
        "review_pass_does_not_authorize_execution": True,
        "scientific_authority": False,
        "paper_design_authority": False,
        "method_authority": False,
        "experiment_blueprint_authority": False,
        "experiment_authority": False,
        "local_validation_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    row["method_review_sha256"] = _digest(method_review_identity(row))
    return row


def validate_reopen_method_review(row: Mapping[str, Any]) -> bool:
    if row.get("receipt_type") != "reopen-method-review" or row.get("status") not in {REVIEW_PASS, REVIEW_BLOCK}:
        return False
    checks = row.get("checks") or {}
    if not isinstance(checks, Mapping) or set(checks.keys()) != set(REQUIRED_REVIEW_CHECKS):
        return False
    failed = [key for key in REQUIRED_REVIEW_CHECKS if checks.get(key) is not True]
    if list(row.get("failed_checks") or []) != failed:
        return False
    passed = not failed
    if row.get("pass") is not passed or row.get("status") != (REVIEW_PASS if passed else REVIEW_BLOCK):
        return False
    if row.get("experiment_blueprint_design_eligible") is not passed or row.get("local_validation_eligible") is not False:
        return False
    reviewer_ref = _text(row.get("reviewer_ref"))
    if not reviewer_ref or hashlib.sha256(reviewer_ref.encode()).hexdigest() != _text(row.get("reviewer_ref_sha256")):
        return False
    if row.get("review_pass_does_not_authorize_execution") is not True or row.get("method_frozen") is not True:
        return False
    for key in ("scientific_authority", "paper_design_authority", "method_authority", "experiment_blueprint_authority", "experiment_authority", "local_validation_authority", "p0_authority", "gpu_authority", "submission_authority"):
        if row.get(key) is not False:
            return False
    return _text(row.get("method_review_sha256")) == _digest(method_review_identity(row))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "scientific-contract-method-design" else root / "scientific-contract-method-design"


def _receipt_sha(row: Mapping[str, Any]) -> str:
    if row.get("receipt_type") == "reopen-method-design": return _text(row.get("method_design_sha256"))
    if row.get("receipt_type") == "reopen-method-review": return _text(row.get("method_review_sha256"))
    return ""


def publish_reopen_method_receipt(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    valid = validate_reopen_method_design(receipt) if receipt.get("receipt_type") == "reopen-method-design" else validate_reopen_method_review(receipt)
    if not valid:
        raise RuntimeError("invalid reopen method receipt")
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    contract_id = _text(receipt.get("contract_id")); path = directory / f"{_slug(contract_id)}.json"; lock = directory / f".{_slug(contract_id)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ledger = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"schema_version": SCHEMA_VERSION, "contract_id": contract_id, "contract_sha256": _text(receipt.get("contract_sha256")), "events": [], "authority": dict(ZERO_AUTHORITY)}
        if _text(ledger.get("contract_sha256")) != _text(receipt.get("contract_sha256")):
            raise RuntimeError("method ledger contract SHA mismatch")
        receipt_sha = _receipt_sha(receipt)
        for event in ledger.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _receipt_sha(prior) == receipt_sha:
                return ledger
        if receipt.get("receipt_type") == "reopen-method-review":
            design_shas = {_text((event.get("receipt") or {}).get("method_design_sha256")) for event in ledger.get("events") or [] if isinstance(event, Mapping) and (event.get("receipt") or {}).get("receipt_type") == "reopen-method-design"}
            if _text(receipt.get("method_design_sha256")) not in design_shas:
                raise RuntimeError("method review requires prior frozen method design")
        recorded_at = _text(receipt.get("reviewed_at")) or _now()
        event = {"event_type": _text(receipt.get("receipt_type")), "receipt": dict(receipt), "recorded_at": recorded_at, "scientific_authority": False, "method_authority": False, "experiment_authority": False, "p0_authority": False, "gpu_authority": False}
        event["event_id"] = _digest([contract_id, len(ledger.get("events") or []), event["event_type"], receipt_sha, recorded_at])[:24]
        ledger.setdefault("events", []).append(event); ledger["updated_at"] = recorded_at
        errors = validate_reopen_method_ledger(ledger)
        if errors: raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); os.replace(tmp, path)
        return ledger


def validate_reopen_method_ledger(ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if (ledger.get("authority") or {}) != ZERO_AUTHORITY: errors.append("reopen-method-ledger-authority-leak")
    design_shas: set[str] = set(); seen: set[str] = set(); contract_id = _text(ledger.get("contract_id")); contract_sha = _text(ledger.get("contract_sha256"))
    for index, event in enumerate(ledger.get("events") or []):
        if not isinstance(event, Mapping): errors.append("reopen-method-event-not-object"); continue
        receipt = event.get("receipt") or {}; rtype = _text(receipt.get("receipt_type")); rsha = _receipt_sha(receipt)
        valid = validate_reopen_method_design(receipt) if rtype == "reopen-method-design" else validate_reopen_method_review(receipt) if rtype == "reopen-method-review" else False
        if not valid: errors.append("reopen-method-receipt-invalid"); continue
        if _text(receipt.get("contract_id")) != contract_id or _text(receipt.get("contract_sha256")) != contract_sha: errors.append("reopen-method-contract-lineage-mismatch")
        if rsha in seen: errors.append("reopen-method-duplicate-receipt")
        if rtype == "reopen-method-design": design_shas.add(rsha)
        elif _text(receipt.get("method_design_sha256")) not in design_shas: errors.append("reopen-method-review-missing-prior-design")
        expected = _digest([contract_id, index, rtype, rsha, _text(event.get("recorded_at"))])[:24]
        if _text(event.get("event_id")) != expected: errors.append("reopen-method-event-id-invalid")
        if any(event.get(key) is True for key in ("scientific_authority", "method_authority", "experiment_authority", "p0_authority", "gpu_authority")): errors.append("reopen-method-event-authority-leak")
        seen.add(rsha)
    return list(dict.fromkeys(errors))


def public_reopen_method_summary(root: Path, contract_id: str) -> dict[str, Any]:
    path = _directory(root) / f"{_slug(contract_id)}.json"
    empty = {"status": "REOPEN_METHOD_DESIGN_REQUIRED", "contract_id": contract_id, "method_design_sha256": "", "method_review_sha256": "", "experiment_blueprint_design_eligible": False, "local_validation_eligible": False, "failed_checks": [], "validation_errors": [], "authority": dict(ZERO_AUTHORITY)}
    if not path.exists(): return empty
    try: ledger = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {**empty, "status": "REOPEN_METHOD_LEDGER_INVALID", "validation_errors": ["reopen-method-ledger-unreadable"]}
    errors = validate_reopen_method_ledger(ledger)
    if errors: return {**empty, "status": "REOPEN_METHOD_LEDGER_INVALID", "validation_errors": errors}
    designs = [event.get("receipt") or {} for event in ledger.get("events") or [] if isinstance(event, Mapping) and (event.get("receipt") or {}).get("receipt_type") == "reopen-method-design"]
    reviews = [event.get("receipt") or {} for event in ledger.get("events") or [] if isinstance(event, Mapping) and (event.get("receipt") or {}).get("receipt_type") == "reopen-method-review"]
    design = designs[-1] if designs else {}; review = reviews[-1] if reviews else {}
    status = _text(review.get("status")) if review else DESIGN_STATUS if design else empty["status"]
    return {**empty, "status": status, "method_design_sha256": _text(design.get("method_design_sha256")), "method_review_sha256": _text(review.get("method_review_sha256")), "experiment_blueprint_design_eligible": review.get("experiment_blueprint_design_eligible") is True, "local_validation_eligible": False, "failed_checks": list(review.get("failed_checks") or []), "reviewer_ref_sha256": _text(review.get("reviewer_ref_sha256"))}
