from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .candidate_identity import validate_candidate_identity
from .config import PROJECT_ROOT

SCHEMA_VERSION = "1.0"
DEFAULT_QUEUE_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-queue.json"
DEFAULT_SUPPORT_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-problem-falsifier-preflight.json"
DEFAULT_TRANSACTION_QUEUE_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-gate-queue.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-falsifier-execution-control.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-pre-f0-falsifier-execution-control.js"
DEFAULT_REQUEST_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-falsifier-execution-authorization-request.json"
DEFAULT_REQUEST_JS = PROJECT_ROOT / "generated" / "paper-first-pre-f0-falsifier-execution-authorization-request.js"
AUTHORITY_ENV = "PAPER_FIRST_PRE_F0_FALSIFIER_HUMAN_AUTHORITY"
AUTHORITY_TYPE = "human-paper-first-pre-f0-falsifier-execution"
_REPO_ROOT = PROJECT_ROOT.resolve()

AUTHORITY = {
    "falsifier_execution": False,
    "live_problem_gate": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}

POLICY = {
    "scientific_authority": False,
    "support_qualified_is_eligibility_not_execution_authority": True,
    "support_qualified_rows_only": True,
    "candidate_id_is_run_local_ordinal_not_execution_identity": True,
    "candidate_snapshot_sha256_is_execution_identity": True,
    "control_binds_current_queue_support_and_discovery_transaction": True,
    "support_scope_is_hard_execution_ceiling": True,
    "explicit_single_use_execution_authority_artifact_required": True,
    "authority_artifact_must_bind_control_snapshot": True,
    "cpu_only_secondary_audit_route": True,
    "provider_calls_default_and_authorized_zero": True,
    "gpu_calls_default_and_authorized_zero": True,
    "positive_f0_requires_exact_same_information_reduction_recheck": True,
    "problem_gate_before_exact_reduction_forbidden": True,
    "public_control_excludes_candidate_id_title_scope_text_and_private_paths": True,
    "current_support_scope_is_not_terminal_hold_resolution_authority": True,
    "historical_execution_cannot_be_retroactively_authorized": True,
    "out_of_scope_fresh_intervention_requires_new_support_control": True,
    "human_execution_authority_must_be_explicit_external_content_addressed_artifact": True,
    "authorization_request_is_zero_authority": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_path(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _sha_text(text: str) -> str:
    return _sha_bytes(text.encode("utf-8"))


def _canonical_sha(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha_bytes(raw)


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object:{path}")
    return payload


def _require_zero_authority(payload: dict[str, Any], keys: tuple[str, ...], label: str) -> None:
    if payload.get("scientific_authority") is not False:
        raise ValueError(f"{label} must have zero scientific authority")
    authority = payload.get("authority") or {}
    if any(authority.get(key) is not False for key in keys):
        raise ValueError(f"{label} leaked downstream authority")


def build_execution_control(
    queue: dict[str, Any],
    support: dict[str, Any],
    transaction_queue: dict[str, Any],
    *,
    queue_sha256: str,
    support_sha256: str,
    transaction_queue_sha256: str,
) -> dict[str, Any]:
    _require_zero_authority(queue, ("problem_gate", "paper_design", "method", "experiment", "p0", "gpu"), "Pre-F0 queue")
    _require_zero_authority(support, ("canonical_generator", "canonical_problem_gate", "paper_design", "method", "experiment", "p0", "gpu"), "Pre-F0 support preflight")

    if str(queue.get("status") or "") != "PRE_F0_QUEUE_READY":
        raise ValueError("Pre-F0 falsifier execution control requires PRE_F0_QUEUE_READY")
    if str(support.get("status") or "") != "PROBLEM_FALSIFIER_PREFLIGHT_COMPLETE":
        raise ValueError("Pre-F0 falsifier execution control requires complete support preflight")
    if int((support.get("summary") or {}).get("falsifier_executed") or 0) != 0:
        raise ValueError("Pre-F0 execution control cannot be compiled after an untracked falsifier execution")

    generator_run_id = str(queue.get("source_generator_run_id") or "").strip()
    if not generator_run_id or str(support.get("run_id") or "").strip() != generator_run_id:
        raise ValueError("Pre-F0 queue/support generator-run binding mismatch")

    transaction_id = str(transaction_queue.get("discovery_transaction_id") or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", transaction_id):
        raise ValueError("sealed discovery transaction id required for Pre-F0 execution control")
    if transaction_queue.get("discovery_transaction_role") != "queue":
        raise ValueError("Pre-F0 execution control requires the sealed transaction queue receipt")
    transaction_summary = transaction_queue.get("summary") or {}
    transaction_policy = transaction_queue.get("policy") or {}
    if int(transaction_summary.get("submitted") or 0) != 0 or int(transaction_summary.get("passed_problem_gate") or 0) != 0:
        raise ValueError("Pre-F0 execution control cannot bind a queue that already entered Problem Gate")
    if transaction_policy.get("all_candidates_require_problem_gate") is not True:
        raise ValueError("sealed transaction queue does not preserve Problem Gate boundary")

    queue_rows = [row for row in queue.get("rows") or [] if isinstance(row, dict)]
    support_rows = [row for row in support.get("rows") or [] if isinstance(row, dict)]
    if int((queue.get("summary") or {}).get("queued") or 0) != len(queue_rows):
        raise ValueError("Pre-F0 queue accounting mismatch")
    if int((support.get("summary") or {}).get("queued") or 0) != len(support_rows):
        raise ValueError("Pre-F0 support accounting mismatch")

    queue_by_snapshot: dict[str, dict[str, Any]] = {}
    for row in queue_rows:
        validate_candidate_identity(row)
        snapshot = str(row.get("candidate_snapshot_sha256") or "").strip().lower()
        if snapshot in queue_by_snapshot:
            raise ValueError("Pre-F0 queue candidate snapshots must be unique")
        queue_by_snapshot[snapshot] = row

    bindings: list[dict[str, Any]] = []
    seen_support_snapshots: set[str] = set()
    for row in support_rows:
        snapshot = str(row.get("candidate_snapshot_sha256") or "").strip().lower()
        if str(row.get("candidate_identity_version") or "") != "candidate-content-v1" or not re.fullmatch(r"[0-9a-f]{64}", snapshot):
            raise ValueError("Pre-F0 support row requires projected candidate-content-v1 snapshot identity")
        if snapshot in seen_support_snapshots:
            raise ValueError("Pre-F0 support candidate snapshots must be unique")
        seen_support_snapshots.add(snapshot)
        queue_row = queue_by_snapshot.get(snapshot)
        if queue_row is None:
            raise ValueError("Pre-F0 support snapshot is stale versus queue")
        if str(row.get("disposition") or "").upper() != "SUPPORT_QUALIFIED":
            continue
        if row.get("falsifier_execution_authorized") is not False:
            raise ValueError("support qualification must not already authorize falsifier execution")
        if str(queue_row.get("next_if_positive") or "") != "RERUN_EXACT_SAME_INFORMATION_REDUCTION":
            raise ValueError("support-qualified Pre-F0 row must preserve post-F0 exact-reduction recheck")
        support_scope = str(row.get("support_scope") or "").strip()
        falsifier = str(queue_row.get("cheapest_problem_falsifier") or "").strip()
        baseline = str(queue_row.get("strongest_same_information_baseline") or "").strip()
        exact_prediction = str(queue_row.get("exact_prediction") or "").strip()
        qualified_units = row.get("qualified_units")
        unit_manifest_sha256 = str(row.get("unit_manifest_sha256") or "").strip().lower()
        if not support_scope or not falsifier or not baseline or not exact_prediction:
            raise ValueError("support-qualified Pre-F0 row lacks frozen execution scope")
        if not isinstance(qualified_units, int) or qualified_units <= 0:
            raise ValueError("support-qualified Pre-F0 row requires positive qualified-unit cap")
        if not re.fullmatch(r"[0-9a-f]{64}", unit_manifest_sha256):
            raise ValueError("support-qualified Pre-F0 row requires unit-manifest digest")
        bindings.append(
            {
                "candidate_snapshot_sha256": snapshot,
                "support_mode": str(row.get("support_mode") or "").strip(),
                "qualified_units_cap": qualified_units,
                "unit_manifest_sha256": unit_manifest_sha256,
                "support_scope_sha256": _sha_text(support_scope),
                "exact_prediction_sha256": _sha_text(exact_prediction),
                "same_information_baseline_sha256": _sha_text(baseline),
                "falsifier_expression_sha256": _sha_text(falsifier),
                "next_if_positive": "RERUN_EXACT_SAME_INFORMATION_REDUCTION",
                "execution_authorized": False,
                "terminal_hold_resolution_authorized": False,
                "retroactive_historical_execution_authorized": False,
                "fresh_out_of_scope_intervention_authorized": False,
                "scientific_authority": False,
            }
        )

    bindings.sort(key=lambda item: item["candidate_snapshot_sha256"])
    expected_qualified = int((support.get("summary") or {}).get("support_qualified") or 0)
    if expected_qualified != len(bindings):
        raise ValueError("support-qualified Pre-F0 execution-control accounting mismatch")

    material = {
        "schema_version": SCHEMA_VERSION,
        "discovery_transaction_id": transaction_id,
        "source_generator_run_id": generator_run_id,
        "queue_sha256": queue_sha256,
        "support_preflight_sha256": support_sha256,
        "support_inventory_sha256": str(support.get("support_inventory_sha256") or "").strip().lower(),
        "transaction_queue_sha256": transaction_queue_sha256,
        "candidate_bindings": bindings,
    }
    control_sha256 = _canonical_sha(material)
    locked = len(bindings) > 0
    summary = {
        "support_qualified_candidates": len(bindings),
        "execution_control_requests": len(bindings),
        "qualified_units_cap_total": sum(int(row["qualified_units_cap"]) for row in bindings),
        "execution_authority_artifacts_present": 0,
        "falsifier_execution_authorized": 0,
        "falsifier_executed": 0,
        "provider_calls_authorized": 0,
        "provider_calls_executed": 0,
        "gpu_authorized": 0,
        "gpu_calls_executed": 0,
        "problem_gate_authorized": 0,
        "paper_design_authorized": 0,
        "method_authorized": 0,
        "experiment_authorized": 0,
        "p0_authorized": 0,
        "terminal_hold_resolution_authorized": 0,
        "retroactive_historical_execution_authorized": 0,
        "fresh_out_of_scope_intervention_authorized": 0,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(),
        "status": "PRE_F0_FALSIFIER_EXECUTION_CONTROL_LOCKED" if locked else "NO_SUPPORT_QUALIFIED_PRE_F0_FALSIFIER",
        "control_snapshot_sha256": control_sha256,
        **material,
        "policy": dict(POLICY),
        "summary": summary,
        "execution_authority_artifact_present": False,
        "execution_authorized": False,
        "terminal_hold_resolution_authorized": False,
        "retroactive_historical_execution_authorized": False,
        "fresh_out_of_scope_intervention_authorized": False,
        "next_action": "REQUIRE_EXPLICIT_SINGLE_USE_EXECUTION_AUTHORITY_FOR_EXACT_SUPPORT_SCOPE" if locked else "NO_EXECUTION_REQUEST",
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }


def build_current_execution_control(
    *,
    queue_path: Path = DEFAULT_QUEUE_JSON,
    support_path: Path = DEFAULT_SUPPORT_JSON,
    transaction_queue_path: Path = DEFAULT_TRANSACTION_QUEUE_JSON,
) -> dict[str, Any]:
    return build_execution_control(
        _load(queue_path),
        _load(support_path),
        _load(transaction_queue_path),
        queue_sha256=_sha_path(queue_path),
        support_sha256=_sha_path(support_path),
        transaction_queue_sha256=_sha_path(transaction_queue_path),
    )


def validate_public_state(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status = str(state.get("status") or "")
    if status not in {"NOT_RUN", "NO_SUPPORT_QUALIFIED_PRE_F0_FALSIFIER", "PRE_F0_FALSIFIER_EXECUTION_CONTROL_LOCKED"}:
        errors.append("Pre-F0 falsifier execution-control status invalid")
    if state.get("scientific_authority") is not False:
        errors.append("Pre-F0 falsifier execution control cannot carry scientific authority")
    if any((state.get("authority") or {}).get(key) is not False for key in AUTHORITY):
        errors.append("Pre-F0 falsifier execution control leaked authority")
    for key, value in POLICY.items():
        if (state.get("policy") or {}).get(key) != value:
            errors.append("Pre-F0 falsifier execution-control policy mismatch:" + key)
    if status == "NOT_RUN":
        return sorted(set(errors))

    for key in ("control_snapshot_sha256", "discovery_transaction_id", "queue_sha256", "support_preflight_sha256", "support_inventory_sha256", "transaction_queue_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(state.get(key) or "")):
            errors.append("Pre-F0 falsifier execution-control digest invalid:" + key)
    if not str(state.get("source_generator_run_id") or "").strip():
        errors.append("Pre-F0 falsifier execution control requires generator-run binding")
    bindings = [row for row in state.get("candidate_bindings") or [] if isinstance(row, dict)]
    summary = state.get("summary") or {}
    if int(summary.get("support_qualified_candidates") or 0) != len(bindings) or int(summary.get("execution_control_requests") or 0) != len(bindings):
        errors.append("Pre-F0 falsifier execution-control candidate accounting mismatch")
    if int(summary.get("qualified_units_cap_total") or 0) != sum(int(row.get("qualified_units_cap") or 0) for row in bindings):
        errors.append("Pre-F0 falsifier execution-control qualified-unit accounting mismatch")
    forbidden_binding_keys = {"candidate_id", "title", "support_scope", "exact_prediction", "strongest_same_information_baseline", "cheapest_problem_falsifier", "source_refs", "path", "url"}
    seen: set[str] = set()
    for row in bindings:
        if any(key in row for key in forbidden_binding_keys):
            errors.append("Pre-F0 falsifier public control exposes candidate text/id/path material")
        snapshot = str(row.get("candidate_snapshot_sha256") or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", snapshot) or snapshot in seen:
            errors.append("Pre-F0 falsifier execution-control candidate snapshot invalid or duplicate")
        seen.add(snapshot)
        for key in ("unit_manifest_sha256", "support_scope_sha256", "exact_prediction_sha256", "same_information_baseline_sha256", "falsifier_expression_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(row.get(key) or "")):
                errors.append("Pre-F0 falsifier execution-control binding digest invalid:" + key)
        if not isinstance(row.get("qualified_units_cap"), int) or int(row.get("qualified_units_cap") or 0) <= 0:
            errors.append("Pre-F0 falsifier execution-control qualified-unit cap invalid")
        if row.get("execution_authorized") is not False or row.get("scientific_authority") is not False:
            errors.append("Pre-F0 falsifier binding cannot authorize execution")
        if any(row.get(key) is not False for key in ("terminal_hold_resolution_authorized", "retroactive_historical_execution_authorized", "fresh_out_of_scope_intervention_authorized")):
            errors.append("Pre-F0 falsifier binding cannot expand exact support scope")
        if row.get("next_if_positive") != "RERUN_EXACT_SAME_INFORMATION_REDUCTION":
            errors.append("Pre-F0 falsifier binding must require exact-reduction recheck after positive F0")

    zero_summary = (
        "execution_authority_artifacts_present",
        "falsifier_execution_authorized",
        "falsifier_executed",
        "provider_calls_authorized",
        "provider_calls_executed",
        "gpu_authorized",
        "gpu_calls_executed",
        "problem_gate_authorized",
        "paper_design_authorized",
        "method_authorized",
        "experiment_authorized",
        "p0_authorized",
        "terminal_hold_resolution_authorized",
        "retroactive_historical_execution_authorized",
        "fresh_out_of_scope_intervention_authorized",
    )
    if any(int(summary.get(key) or 0) != 0 for key in zero_summary):
        errors.append("Pre-F0 falsifier execution control must remain locked and zero-authority")
    if state.get("execution_authority_artifact_present") is not False or state.get("execution_authorized") is not False:
        errors.append("Pre-F0 falsifier execution control requires a separate authority artifact before execution")
    if any(state.get(key) is not False for key in ("terminal_hold_resolution_authorized", "retroactive_historical_execution_authorized", "fresh_out_of_scope_intervention_authorized")):
        errors.append("Pre-F0 falsifier execution control cannot expand current support scope")
    if status == "PRE_F0_FALSIFIER_EXECUTION_CONTROL_LOCKED" and not bindings:
        errors.append("locked Pre-F0 falsifier execution control requires at least one support-qualified binding")
    if status == "NO_SUPPORT_QUALIFIED_PRE_F0_FALSIFIER" and bindings:
        errors.append("empty Pre-F0 falsifier execution control cannot contain bindings")
    return sorted(set(errors))



def build_authorization_request(control: dict[str, Any]) -> dict[str, Any]:
    errors = validate_public_state(control)
    if errors:
        raise ValueError("cannot build authority request from invalid Pre-F0 control: " + ";".join(errors))
    bindings = [dict(row) for row in control.get("candidate_bindings") or [] if isinstance(row, dict)]
    request_entries = [
        {
            "candidate_snapshot_sha256": str(row.get("candidate_snapshot_sha256") or ""),
            "unit_manifest_sha256": str(row.get("unit_manifest_sha256") or ""),
            "support_scope_sha256": str(row.get("support_scope_sha256") or ""),
            "qualified_units_cap": int(row.get("qualified_units_cap") or 0),
            "requested_execution_route": "EXACT_SUPPORT_QUALIFIED_CPU_SECONDARY_AUDIT_ONLY",
            "bounded_falsifier_execution_authorized": False,
            "terminal_hold_resolution_authorized": False,
            "retroactive_historical_execution_authorized": False,
            "fresh_out_of_scope_intervention_authorized": False,
            "scientific_authority": False,
        }
        for row in bindings
    ]
    material = {
        "schema_version": SCHEMA_VERSION,
        "request_type": "paper-first-pre-f0-falsifier-single-use-execution-authority",
        "control_snapshot_sha256": str(control.get("control_snapshot_sha256") or ""),
        "discovery_transaction_id": str(control.get("discovery_transaction_id") or ""),
        "source_generator_run_id": str(control.get("source_generator_run_id") or ""),
        "request_entries": request_entries,
        "required_external_authority_type": AUTHORITY_TYPE,
        "required_external_authority_env": AUTHORITY_ENV,
    }
    request_sha = _canonical_sha(material)
    locked = bool(request_entries)
    return {
        **material,
        "generated_at": _now(),
        "status": "AWAITING_EXPLICIT_EXTERNAL_HUMAN_EXECUTION_AUTHORITY" if locked else "NO_EXECUTION_AUTHORITY_REQUEST",
        "authorization_request_sha256": request_sha,
        "required_authority_contract": {
            "authority_type": AUTHORITY_TYPE,
            "decision": "approve",
            "reviewed_by": "user-or-human-user",
            "reviewed_at_required": True,
            "source_message_ref_required": True,
            "source_message_sha256_required": True,
            "control_snapshot_sha256": str(control.get("control_snapshot_sha256") or ""),
            "discovery_transaction_id": str(control.get("discovery_transaction_id") or ""),
            "source_generator_run_id": str(control.get("source_generator_run_id") or ""),
            "candidate_snapshot_sha256_must_match_one_request_entry": True,
            "unit_manifest_sha256_must_match_selected_request_entry": True,
            "support_scope_sha256_must_match_selected_request_entry": True,
            "bounded_falsifier_execution_authorized": True,
            "cpu_execution_authorized": True,
            "provider_calls_authorized": False,
            "gpu_calls_authorized": False,
            "single_attempt": True,
            "terminal_hold_resolution_authorized": False,
            "retroactive_historical_execution_authorized": False,
            "fresh_out_of_scope_intervention_authorized": False,
            "problem_gate_authorized": False,
            "paper_design_authorized": False,
            "method_authorized": False,
            "experiment_authorized": False,
            "p0_authorized": False,
            "scientific_authority": False,
        },
        "summary": {
            "requests": len(request_entries),
            "execution_authority_artifacts_present": 0,
            "bounded_falsifier_execution_authorized": 0,
            "provider_calls_authorized": 0,
            "gpu_calls_authorized": 0,
            "terminal_hold_resolution_authorized": 0,
            "retroactive_historical_execution_authorized": 0,
            "fresh_out_of_scope_intervention_authorized": 0,
        },
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }


def validate_authorization_request(request: dict[str, Any], *, control: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if request.get("scientific_authority") is not False or any((request.get("authority") or {}).get(key) is not False for key in AUTHORITY):
        errors.append("Pre-F0 authority request leaked authority")
    if request.get("request_type") != "paper-first-pre-f0-falsifier-single-use-execution-authority":
        errors.append("Pre-F0 authority request type invalid")
    if request.get("required_external_authority_type") != AUTHORITY_TYPE or request.get("required_external_authority_env") != AUTHORITY_ENV:
        errors.append("Pre-F0 authority request external-authority binding invalid")
    entries = [row for row in request.get("request_entries") or [] if isinstance(row, dict)]
    status = str(request.get("status") or "")
    if status == "AWAITING_EXPLICIT_EXTERNAL_HUMAN_EXECUTION_AUTHORITY" and not entries:
        errors.append("Pre-F0 authority request awaiting status requires entries")
    if status == "NO_EXECUTION_AUTHORITY_REQUEST" and entries:
        errors.append("Pre-F0 no-authority request cannot contain entries")
    if status not in {"AWAITING_EXPLICIT_EXTERNAL_HUMAN_EXECUTION_AUTHORITY", "NO_EXECUTION_AUTHORITY_REQUEST"}:
        errors.append("Pre-F0 authority request status invalid")
    for row in entries:
        for key in ("candidate_snapshot_sha256", "unit_manifest_sha256", "support_scope_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(row.get(key) or "").lower()):
                errors.append("Pre-F0 authority request binding digest invalid:" + key)
        if row.get("requested_execution_route") != "EXACT_SUPPORT_QUALIFIED_CPU_SECONDARY_AUDIT_ONLY":
            errors.append("Pre-F0 authority request route exceeds support scope")
        if int(row.get("qualified_units_cap") or 0) <= 0:
            errors.append("Pre-F0 authority request qualified-unit cap invalid")
        for key in ("bounded_falsifier_execution_authorized", "terminal_hold_resolution_authorized", "retroactive_historical_execution_authorized", "fresh_out_of_scope_intervention_authorized", "scientific_authority"):
            if row.get(key) is not False:
                errors.append("Pre-F0 authority request must remain zero-authority:" + key)
    summary = request.get("summary") or {}
    if int(summary.get("requests") or 0) != len(entries):
        errors.append("Pre-F0 authority request accounting mismatch")
    for key in ("execution_authority_artifacts_present", "bounded_falsifier_execution_authorized", "provider_calls_authorized", "gpu_calls_authorized", "terminal_hold_resolution_authorized", "retroactive_historical_execution_authorized", "fresh_out_of_scope_intervention_authorized"):
        if int(summary.get(key) or 0) != 0:
            errors.append("Pre-F0 authority request cannot self-authorize:" + key)
    contract = request.get("required_authority_contract") or {}
    required_false = ("provider_calls_authorized", "gpu_calls_authorized", "terminal_hold_resolution_authorized", "retroactive_historical_execution_authorized", "fresh_out_of_scope_intervention_authorized", "problem_gate_authorized", "paper_design_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "scientific_authority")
    if contract.get("bounded_falsifier_execution_authorized") is not True or contract.get("cpu_execution_authorized") is not True or contract.get("single_attempt") is not True:
        errors.append("Pre-F0 authority request must require one bounded CPU attempt")
    if any(contract.get(key) is not False for key in required_false):
        errors.append("Pre-F0 authority request required contract expands authority")
    material = {key: request.get(key) for key in ("schema_version", "request_type", "control_snapshot_sha256", "discovery_transaction_id", "source_generator_run_id", "request_entries", "required_external_authority_type", "required_external_authority_env")}
    if str(request.get("authorization_request_sha256") or "") != _canonical_sha(material):
        errors.append("Pre-F0 authority request content digest mismatch")
    if control is not None:
        if str(request.get("control_snapshot_sha256") or "") != str(control.get("control_snapshot_sha256") or ""):
            errors.append("Pre-F0 authority request/control snapshot mismatch")
        expected = {(str(row.get("candidate_snapshot_sha256") or ""), str(row.get("unit_manifest_sha256") or ""), str(row.get("support_scope_sha256") or ""), int(row.get("qualified_units_cap") or 0)) for row in control.get("candidate_bindings") or [] if isinstance(row, dict)}
        actual = {(str(row.get("candidate_snapshot_sha256") or ""), str(row.get("unit_manifest_sha256") or ""), str(row.get("support_scope_sha256") or ""), int(row.get("qualified_units_cap") or 0)) for row in entries}
        if actual != expected:
            errors.append("Pre-F0 authority request bindings drift from execution control")
    return sorted(set(errors))


def _no_human_authority(control: dict[str, Any], errors: list[str] | None = None) -> dict[str, Any]:
    return {
        "bounded_falsifier_execution_authorized": False,
        "cpu_execution_authorized": False,
        "provider_calls_authorized": False,
        "gpu_calls_authorized": False,
        "single_attempt": False,
        "terminal_hold_resolution_authorized": False,
        "retroactive_historical_execution_authorized": False,
        "fresh_out_of_scope_intervention_authorized": False,
        "problem_gate_authorized": False,
        "paper_design_authorized": False,
        "method_authorized": False,
        "experiment_authorized": False,
        "p0_authorized": False,
        "scientific_authority": False,
        "authority_status": "NO_EXPLICIT_EXTERNAL_PRE_F0_FALSIFIER_EXECUTION_AUTHORITY",
        "control_snapshot_sha256": str(control.get("control_snapshot_sha256") or ""),
        "artifact_path": "",
        "artifact_sha256": "",
        "source_message_ref": "",
        "source_message_sha256": "",
        "errors": list(errors or []),
    }


def load_external_human_authority(control: dict[str, Any], path: str | Path | None = None) -> dict[str, Any]:
    control_errors = validate_public_state(control)
    if control_errors:
        return _no_human_authority(control, ["invalid-control"] + control_errors)
    raw_path = str(path or os.environ.get(AUTHORITY_ENV, "")).strip()
    if not raw_path:
        return _no_human_authority(control, [f"missing-external-authority:{AUTHORITY_ENV}"])
    authority_path = Path(raw_path).expanduser().resolve()
    errors: list[str] = []
    try:
        authority_path.relative_to(_REPO_ROOT)
        errors.append("authority-artifact-must-be-external-to-repository")
    except ValueError:
        pass
    try:
        raw = authority_path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return _no_human_authority(control, errors + [f"authority-artifact-unreadable:{type(error).__name__}"])
    if not isinstance(payload, dict):
        return _no_human_authority(control, errors + ["authority-artifact-root-must-be-object"])
    required = (
        "authority_type", "decision", "reviewed_by", "reviewed_at", "source_message_ref", "source_message_sha256",
        "control_snapshot_sha256", "discovery_transaction_id", "source_generator_run_id", "candidate_snapshot_sha256",
        "unit_manifest_sha256", "support_scope_sha256", "bounded_falsifier_execution_authorized", "cpu_execution_authorized",
        "provider_calls_authorized", "gpu_calls_authorized", "single_attempt", "terminal_hold_resolution_authorized",
        "retroactive_historical_execution_authorized", "fresh_out_of_scope_intervention_authorized", "problem_gate_authorized",
        "paper_design_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "scientific_authority",
    )
    for key in required:
        if key not in payload:
            errors.append("missing:" + key)
    if payload.get("authority_type") != AUTHORITY_TYPE:
        errors.append("invalid-authority-type")
    if payload.get("decision") != "approve":
        errors.append("decision-not-approve")
    if str(payload.get("reviewed_by") or "") not in {"user", "human-user"}:
        errors.append("reviewer-not-human-user")
    if str(payload.get("control_snapshot_sha256") or "") != str(control.get("control_snapshot_sha256") or ""):
        errors.append("binding-mismatch:control_snapshot_sha256")
    if str(payload.get("discovery_transaction_id") or "") != str(control.get("discovery_transaction_id") or ""):
        errors.append("binding-mismatch:discovery_transaction_id")
    if str(payload.get("source_generator_run_id") or "") != str(control.get("source_generator_run_id") or ""):
        errors.append("binding-mismatch:source_generator_run_id")
    source_message_sha = str(payload.get("source_message_sha256") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", source_message_sha):
        errors.append("invalid-source-message-sha256")
    selected = [row for row in control.get("candidate_bindings") or [] if isinstance(row, dict) and str(row.get("candidate_snapshot_sha256") or "") == str(payload.get("candidate_snapshot_sha256") or "")]
    if len(selected) != 1:
        errors.append("candidate-snapshot-not-exactly-one-controlled-binding")
    else:
        binding = selected[0]
        for key in ("unit_manifest_sha256", "support_scope_sha256"):
            if str(payload.get(key) or "") != str(binding.get(key) or ""):
                errors.append("binding-mismatch:" + key)
    for key in ("bounded_falsifier_execution_authorized", "cpu_execution_authorized", "single_attempt"):
        if payload.get(key) is not True:
            errors.append("required-true:" + key)
    for key in ("provider_calls_authorized", "gpu_calls_authorized", "terminal_hold_resolution_authorized", "retroactive_historical_execution_authorized", "fresh_out_of_scope_intervention_authorized", "problem_gate_authorized", "paper_design_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "scientific_authority"):
        if payload.get(key) is not False:
            errors.append("forbidden-authority:" + key)
    artifact_sha = _sha_bytes(raw)
    if errors:
        row = _no_human_authority(control, errors)
        row.update({"artifact_path": str(authority_path), "artifact_sha256": artifact_sha, "source_message_ref": str(payload.get("source_message_ref") or ""), "source_message_sha256": source_message_sha})
        return row
    return {
        "bounded_falsifier_execution_authorized": True,
        "cpu_execution_authorized": True,
        "provider_calls_authorized": False,
        "gpu_calls_authorized": False,
        "single_attempt": True,
        "terminal_hold_resolution_authorized": False,
        "retroactive_historical_execution_authorized": False,
        "fresh_out_of_scope_intervention_authorized": False,
        "problem_gate_authorized": False,
        "paper_design_authorized": False,
        "method_authorized": False,
        "experiment_authorized": False,
        "p0_authorized": False,
        "scientific_authority": False,
        "authority_status": "EXTERNAL_HUMAN_PRE_F0_FALSIFIER_EXECUTION_AUTHORITY_VALID",
        "control_snapshot_sha256": str(control.get("control_snapshot_sha256") or ""),
        "candidate_snapshot_sha256": str(payload["candidate_snapshot_sha256"]),
        "unit_manifest_sha256": str(payload["unit_manifest_sha256"]),
        "support_scope_sha256": str(payload["support_scope_sha256"]),
        "artifact_path": str(authority_path),
        "artifact_sha256": artifact_sha,
        "source_message_ref": str(payload["source_message_ref"]),
        "source_message_sha256": source_message_sha,
        "reviewed_at": str(payload["reviewed_at"]),
        "errors": [],
    }


def require_single_use_execution_authority(control: dict[str, Any], *, authority: dict[str, Any] | None = None) -> dict[str, Any]:
    authority = authority or load_external_human_authority(control)
    for key in ("bounded_falsifier_execution_authorized", "cpu_execution_authorized", "single_attempt"):
        if authority.get(key) is not True:
            raise RuntimeError("Pre-F0 falsifier execution is locked: valid explicit external human authority is required")
    for key in ("provider_calls_authorized", "gpu_calls_authorized", "terminal_hold_resolution_authorized", "retroactive_historical_execution_authorized", "fresh_out_of_scope_intervention_authorized", "problem_gate_authorized", "paper_design_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "scientific_authority"):
        if authority.get(key) is not False:
            raise RuntimeError("Pre-F0 falsifier execution authority illegally expands support or downstream scope: " + key)
    if str(authority.get("control_snapshot_sha256") or "") != str(control.get("control_snapshot_sha256") or ""):
        raise RuntimeError("Pre-F0 falsifier execution authority control binding mismatch")
    return authority


def claim_external_authority_once(control_root: Path, control: dict[str, Any], authority: dict[str, Any], run_id: str) -> Path:
    authority = require_single_use_execution_authority(control, authority=authority)
    artifact_sha = str(authority.get("artifact_sha256") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", artifact_sha):
        raise RuntimeError("Pre-F0 falsifier authority cannot be consumed without content-addressed external artifact")
    run_id = str(run_id or "").strip()
    if not run_id:
        raise RuntimeError("Pre-F0 falsifier authority consumption requires run_id")
    directory = Path(control_root) / "pre-f0-falsifier-permit-consumption"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{artifact_sha}.json"
    row = {
        "schema_version": "1.0-private",
        "status": "claimed-single-attempt",
        "claimed_at": _now(),
        "run_id": run_id,
        "authority_artifact_sha256": artifact_sha,
        "source_message_sha256": authority.get("source_message_sha256"),
        "control_snapshot_sha256": control.get("control_snapshot_sha256"),
        "candidate_snapshot_sha256": authority.get("candidate_snapshot_sha256"),
        "unit_manifest_sha256": authority.get("unit_manifest_sha256"),
        "support_scope_sha256": authority.get("support_scope_sha256"),
        "provider_calls_authorized": False,
        "gpu_calls_authorized": False,
        "terminal_hold_resolution_authorized": False,
        "retroactive_historical_execution_authorized": False,
        "fresh_out_of_scope_intervention_authorized": False,
        "scientific_authority": False,
    }
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(row, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except FileExistsError as error:
        previous = json.loads(path.read_text(encoding="utf-8"))
        raise RuntimeError("Pre-F0 falsifier human permit is single-use and already claimed by " + str(previous.get("run_id") or "unknown-run")) from error
    return path

def write_execution_control(
    *,
    queue_path: Path = DEFAULT_QUEUE_JSON,
    support_path: Path = DEFAULT_SUPPORT_JSON,
    transaction_queue_path: Path = DEFAULT_TRANSACTION_QUEUE_JSON,
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
    request_json_path: Path = DEFAULT_REQUEST_JSON,
    request_js_path: Path = DEFAULT_REQUEST_JS,
) -> dict[str, Any]:
    state = build_current_execution_control(queue_path=queue_path, support_path=support_path, transaction_queue_path=transaction_queue_path)
    errors = validate_public_state(state)
    if errors:
        raise ValueError("invalid Pre-F0 falsifier execution control: " + ";".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PRE_F0_FALSIFIER_EXECUTION_CONTROL = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    request = build_authorization_request(state)
    request_errors = validate_authorization_request(request, control=state)
    if request_errors:
        raise ValueError("invalid Pre-F0 falsifier execution authority request: " + ";".join(request_errors))
    request_json_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    request_js_path.write_text("window.PAPER_FIRST_PRE_F0_FALSIFIER_EXECUTION_AUTHORIZATION_REQUEST = " + json.dumps(request, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


def load_public(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    try:
        return _load(path)
    except (OSError, json.JSONDecodeError, ValueError):
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "NOT_RUN",
            "policy": dict(POLICY),
            "summary": {},
            "scientific_authority": False,
            "authority": dict(AUTHORITY),
        }


def load_authorization_request(path: Path = DEFAULT_REQUEST_JSON) -> dict[str, Any]:
    try:
        return _load(path)
    except (OSError, json.JSONDecodeError, ValueError):
        return {
            "schema_version": SCHEMA_VERSION,
            "request_type": "paper-first-pre-f0-falsifier-single-use-execution-authority",
            "status": "NO_EXECUTION_AUTHORITY_REQUEST",
            "request_entries": [],
            "summary": {"requests": 0},
            "scientific_authority": False,
            "authority": dict(AUTHORITY),
        }


if __name__ == "__main__":
    print(json.dumps(write_execution_control(), ensure_ascii=False, indent=2))
