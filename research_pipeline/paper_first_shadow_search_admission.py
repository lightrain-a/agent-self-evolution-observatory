from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_primary_evidence import load_primary_evidence_state
from .paper_first_problem_generator import load_problem_generator_state
from .paper_first_problem_gate_queue import load_problem_gate_queue_state

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-shadow-search-admission.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-shadow-search-admission.js"
SHADOW_PORTFOLIO_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-search-portfolio-state.json"

GENERATOR_CLOSED_STATUSES = {
    "GENERATED_ZERO_CANDIDATES",
    "GENERATED_AWAIT_PROBLEM_GATE",
    "SKIPPED_SOURCE_COVERAGE_SATURATED",
}


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def source_set_sha256(records: list[dict[str, Any]]) -> str:
    refs = sorted(str(row.get("ref") or "").strip() for row in records if isinstance(row, dict) and str(row.get("ref") or "").strip())
    if not refs or len(refs) != len(set(refs)) or any(not ref.startswith("arXiv:") for ref in refs):
        return ""
    return hashlib.sha256("\n".join(refs).encode()).hexdigest()


def primary_content_sha256(records: list[dict[str, Any]]) -> str:
    rows=[]
    for row in records:
        if not isinstance(row,dict):
            continue
        ref=str(row.get("ref") or "").strip();source_sha=str(row.get("source_sha256") or "").strip().lower();fulltext_sha=str(row.get("fulltext_sha256") or "").strip().lower()
        if not ref.startswith("arXiv:") or not re.fullmatch(r"[0-9a-f]{64}",source_sha) or (fulltext_sha and not re.fullmatch(r"[0-9a-f]{64}",fulltext_sha)):
            return ""
        rows.append({"ref":ref,"source_sha256":source_sha,"fulltext_sha256":fulltext_sha})
    if not rows or len({row["ref"] for row in rows})!=len(rows):
        return ""
    rows.sort(key=lambda row:row["ref"])
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def build_shadow_search_admission(
    *,
    primary_state: dict[str, Any] | None = None,
    generator_state: dict[str, Any] | None = None,
    queue_state: dict[str, Any] | None = None,
    shadow_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    primary = primary_state if primary_state is not None else load_primary_evidence_state()
    generator = generator_state if generator_state is not None else load_problem_generator_state()
    queue = queue_state if queue_state is not None else load_problem_gate_queue_state()
    shadow = shadow_state if shadow_state is not None else _load(SHADOW_PORTFOLIO_JSON)

    ps = primary.get("summary") or {}
    gs = generator.get("summary") or {}
    qs = queue.get("summary") or {}
    primary_tx = str(primary.get("discovery_transaction_id") or "").strip()
    generator_tx = str(generator.get("discovery_transaction_id") or "").strip()
    queue_tx = str(queue.get("discovery_transaction_id") or "").strip()
    current_generated_at = str(primary.get("generated_at") or "").strip()
    primary_records = [row for row in primary.get("records") or [] if isinstance(row, dict)]
    current_set_sha = source_set_sha256(primary_records)
    current_content_sha = primary_content_sha256(primary_records)
    current_records = len(primary_records)

    latest = shadow.get("latest_run") or {}
    latest_run_id = str(latest.get("run_id") or shadow.get("latest_run_id") or "").strip()
    latest_status = str(latest.get("status") or "").strip()
    latest_generated_at = str(latest.get("source_generated_at") or "").strip()
    latest_set_sha = str(latest.get("source_set_sha256") or "").strip().lower()
    latest_content_sha = str(latest.get("source_primary_content_sha256") or "").strip().lower()
    latest_pool_sha = str(latest.get("source_pool_sha256") or "").strip().lower()
    latest_terminal = bool(latest_run_id and latest_status == "SHADOW_TERMINAL_COMPLETE")

    queue_closed = (
        int(qs.get("submitted") or 0) == int(qs.get("audited") or 0)
        and int(qs.get("inbox_errors") or 0) == 0
        and int(gs.get("written_to_auto_inbox") or 0) == int(qs.get("submitted") or 0)
    )
    tx_valid = bool(re.fullmatch(r"[0-9a-f]{64}", primary_tx))
    canonical_closed = (
        primary.get("status") == "READY"
        and ps.get("source_retrieval_complete") is True
        and ps.get("source_coverage_exhausted") is True
        and ps.get("carrier_probe_complete", True) is True
        and generator.get("status") in GENERATOR_CLOSED_STATUSES
        and tx_valid
        and primary_tx == generator_tx == queue_tx
        and queue_closed
        and bool(current_generated_at)
        and bool(re.fullmatch(r"[0-9a-f]{64}", current_set_sha))
        and bool(re.fullmatch(r"[0-9a-f]{64}", current_content_sha))
        and current_records > 0
    )

    same_timestamp = bool(latest_generated_at and latest_generated_at == current_generated_at)
    same_set = bool(latest_set_sha and latest_set_sha == current_set_sha)
    same_content = bool(latest_content_sha and latest_content_sha == current_content_sha)
    source_identity_complete = bool(re.fullmatch(r"[0-9a-f]{64}", latest_set_sha) and re.fullmatch(r"[0-9a-f]{64}", latest_content_sha))
    same_source_transaction = bool(source_identity_complete and same_set and same_content)
    identity_conflict = bool(source_identity_complete and same_timestamp and not (same_set and same_content))

    if not canonical_closed:
        status = "HOLD_CANONICAL_DISCOVERY_TRANSACTION_OPEN"
        reason = "Canonical Primary -> Generator -> Queue is not a closed, internally consistent zero-authority discovery transaction."
    elif latest_run_id and not latest_terminal:
        status = "HOLD_PRIOR_SHADOW_RUN_INCOMPLETE"
        reason = "A prior shadow run is not terminal-complete; finish or stop it before freezing another shadow transaction."
    elif latest_run_id and not source_identity_complete:
        status = "HOLD_PREVIOUS_SHADOW_SOURCE_IDENTITY_UNAVAILABLE"
        reason = "The latest terminal shadow run lacks bounded source-set/content provenance required for deterministic duplicate suppression."
    elif identity_conflict:
        status = "HOLD_SHADOW_SOURCE_IDENTITY_CONFLICT"
        reason = "Latest and current source provenance partially match; treat this as provenance inconsistency rather than evidence for a new run."
    elif same_source_transaction:
        status = "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL"
        reason = "The current canonical source transaction already has a terminal shadow search result; repeating model calls would be redundant."
    else:
        status = "READY_FOR_SHADOW_QUALIFICATION"
        reason = "Canonical discovery is closed and the current source transaction differs from the latest terminal shadow source identity."

    qualification_allowed = status == "READY_FOR_SHADOW_QUALIFICATION"
    checks = [
        {"key": "primary-ready", "pass": primary.get("status") == "READY"},
        {"key": "source-retrieval-complete", "pass": ps.get("source_retrieval_complete") is True},
        {"key": "source-coverage-exhausted", "pass": ps.get("source_coverage_exhausted") is True},
        {"key": "carrier-probe-complete", "pass": ps.get("carrier_probe_complete", True) is True},
        {"key": "canonical-transaction-id-valid", "pass": tx_valid},
        {"key": "primary-generator-queue-transaction-match", "pass": bool(primary_tx) and primary_tx == generator_tx == queue_tx},
        {"key": "canonical-generator-closed", "pass": generator.get("status") in GENERATOR_CLOSED_STATUSES},
        {"key": "canonical-queue-closed", "pass": queue_closed},
        {"key": "current-source-set-digest-valid", "pass": bool(re.fullmatch(r"[0-9a-f]{64}", current_set_sha))},
        {"key": "current-primary-content-digest-valid", "pass": bool(re.fullmatch(r"[0-9a-f]{64}", current_content_sha))},
        {"key": "prior-shadow-terminal-or-absent", "pass": not latest_run_id or latest_terminal},
        {"key": "prior-shadow-source-identity-available-or-absent", "pass": not latest_run_id or source_identity_complete},
        {"key": "source-identity-not-conflicted", "pass": not identity_conflict},
    ]
    return {
        "schema_version": "1.0",
        "status": status,
        "reason": reason,
        "policy": {
            "scientific_authority": False,
            "admission_is_deterministic_search_control_only": True,
            "canonical_generator_and_queue_untouched": True,
            "same_source_transaction_terminal_skips_model_calls": True,
            "prior_shadow_run_must_be_terminal_before_new_qualification": True,
            "admission_can_only_allow_zero_model_qualification_freeze": True,
            "admission_never_authorizes_provider_calls": True,
            "qualification_receipt_is_still_required_before_stage_execution": True,
            "zero_good_ideas_is_valid": True,
        },
        "summary": {
            "primary_records": current_records,
            "canonical_transaction_closed": canonical_closed,
            "latest_shadow_present": bool(latest_run_id),
            "latest_shadow_terminal": latest_terminal,
            "same_source_transaction": same_source_transaction,
            "source_identity_conflict": identity_conflict,
            "qualification_allowed": qualification_allowed,
            "automatic_provider_calls_authorized": 0,
            "checks": len(checks),
            "passed_checks": sum(row["pass"] is True for row in checks),
            "failed_checks": sum(row["pass"] is not True for row in checks),
        },
        "source_identity": {
            "current_source_generated_at": current_generated_at,
            "current_source_set_sha256": current_set_sha,
            "current_primary_content_sha256": current_content_sha,
            "latest_run_id": latest_run_id,
            "latest_status": latest_status,
            "latest_source_generated_at": latest_generated_at,
            "latest_source_set_sha256": latest_set_sha,
            "latest_primary_content_sha256": latest_content_sha,
            "latest_source_pool_sha256": latest_pool_sha,
        },
        "checks": checks,
        "scientific_authority": False,
        "authority": {
            "canonical_generator": False,
            "canonical_queue": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
    }


def validate_shadow_search_admission(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    source = state.get("source_identity") or {}
    authority = state.get("authority") or {}
    allowed = {
        "HOLD_CANONICAL_DISCOVERY_TRANSACTION_OPEN",
        "HOLD_PRIOR_SHADOW_RUN_INCOMPLETE",
        "HOLD_PREVIOUS_SHADOW_SOURCE_IDENTITY_UNAVAILABLE",
        "HOLD_SHADOW_SOURCE_IDENTITY_CONFLICT",
        "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL",
        "READY_FOR_SHADOW_QUALIFICATION",
    }
    if state.get("status") not in allowed:
        errors.append("shadow search admission status invalid")
    if state.get("scientific_authority") is not False or policy.get("scientific_authority") is not False:
        errors.append("shadow search admission cannot carry scientific authority")
    if policy.get("admission_is_deterministic_search_control_only") is not True or policy.get("admission_never_authorizes_provider_calls") is not True or policy.get("qualification_receipt_is_still_required_before_stage_execution") is not True:
        errors.append("shadow search admission policy must remain deterministic zero-provider search control")
    if int(summary.get("automatic_provider_calls_authorized") or 0) != 0 or any(authority.get(key) is not False for key in authority):
        errors.append("shadow search admission cannot authorize provider or downstream work")
    if bool(summary.get("qualification_allowed")) != (state.get("status") == "READY_FOR_SHADOW_QUALIFICATION"):
        errors.append("shadow search qualification allowance does not match admission status")
    if state.get("status") == "SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL" and (summary.get("same_source_transaction") is not True or summary.get("latest_shadow_terminal") is not True):
        errors.append("same-source skip requires one terminal matching shadow source transaction")
    if state.get("status") == "READY_FOR_SHADOW_QUALIFICATION" and summary.get("canonical_transaction_closed") is not True:
        errors.append("shadow qualification cannot open before canonical discovery closes")
    for key in ("current_source_set_sha256", "current_primary_content_sha256", "latest_source_set_sha256", "latest_primary_content_sha256", "latest_source_pool_sha256"):
        value = str(source.get(key) or "")
        if value and not re.fullmatch(r"[0-9a-f]{64}", value):
            errors.append(f"shadow source identity digest invalid:{key}")
    return sorted(set(errors))


def public_shadow_search_admission_summary(state: dict[str, Any]) -> dict[str, Any]:
    summary = state.get("summary") or {}
    source = state.get("source_identity") or {}
    return {
        "schema_version": "1.0",
        "status": str(state.get("status") or "HOLD_CANONICAL_DISCOVERY_TRANSACTION_OPEN"),
        "reason": str(state.get("reason") or "")[:800],
        "policy": {
            "scientific_authority": False,
            "admission_is_deterministic_search_control_only": True,
            "same_source_transaction_terminal_skips_model_calls": True,
            "admission_can_only_allow_zero_model_qualification_freeze": True,
            "admission_never_authorizes_provider_calls": True,
            "qualification_receipt_is_still_required_before_stage_execution": True,
        },
        "summary": {
            key: summary.get(key)
            for key in (
                "primary_records",
                "canonical_transaction_closed",
                "latest_shadow_present",
                "latest_shadow_terminal",
                "same_source_transaction",
                "source_identity_conflict",
                "qualification_allowed",
                "automatic_provider_calls_authorized",
                "checks",
                "passed_checks",
                "failed_checks",
            )
        },
        "source_identity": {
            key: source.get(key)
            for key in (
                "current_source_generated_at",
                "current_source_set_sha256",
                "current_primary_content_sha256",
                "latest_run_id",
                "latest_status",
                "latest_source_generated_at",
                "latest_source_set_sha256",
                "latest_primary_content_sha256",
                "latest_source_pool_sha256",
            )
        },
        "scientific_authority": False,
    }


def write_shadow_search_admission(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state = build_shadow_search_admission()
    errors = validate_shadow_search_admission(state)
    if errors:
        raise ValueError("Invalid shadow search admission:\n- " + "\n- ".join(errors))
    public = public_shadow_search_admission_summary(state)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_SHADOW_SEARCH_ADMISSION = " + json.dumps(public, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    state = write_shadow_search_admission()
    print(json.dumps(public_shadow_search_admission_summary(state), ensure_ascii=False, indent=2))
