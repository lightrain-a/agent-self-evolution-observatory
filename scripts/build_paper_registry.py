#!/usr/bin/env python3
"""Project canonical Paper Acceptance ledgers into a frontend PaperRegistry snapshot.

The projection has zero scientific/submission authority. Canonical truth remains in
the append-only Paper Acceptance ledger. Preparation receipts are displayed independently
from the legacy SUBMISSION_READY state so older ledgers are not silently rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from research_pipeline.presubmission_freeze import verify_frozen_artifacts
from research_pipeline.submission_handoff import validate_handoff_ledger, validate_handoff_receipt
from research_pipeline.human_submission_signoff import validate_signoff_ledger, verify_current_signoff
from research_pipeline.venue_submission_receipt import validate_submission_receipt
from research_pipeline.revision_impact_audit import audit_freeze_receipt
from research_pipeline.rebuttal_protocol import validate_rebuttal_receipt
from research_pipeline.post_decision_learning import validate_learning_receipt, validate_rebuttal_skipped_by_venue_receipt, validate_venue_decision_receipt
from research_pipeline.submission_attempt_history import build_attempt_history
from research_pipeline.submission_attempt_lineage import public_attempt_summary, validate_attempt_ledger
from research_pipeline.submission_attempt_workflow import current_attempt_workflow_summary, validate_attempt_workflow_ledger
from research_pipeline.scientific_reopen_protocol import public_scientific_reopen_summary, validate_scientific_reopen_ledger
from research_pipeline.reopened_scientific_contract import find_contract_by_handoff, public_reopened_contract_summary
from research_pipeline.reopened_scientific_problem_gate import load_latest_reopen_problem_gate, public_reopen_problem_gate_summary
from research_pipeline.reopened_scientific_method_design import public_reopen_method_summary
from research_pipeline.reopened_scientific_experiment_blueprint import public_reopen_blueprint_summary
from research_pipeline.reopened_local_validation_authorization import public_local_validation_authorization
from research_pipeline.reopened_pre_experiment_adapter import public_reopened_pre_experiment
from research_pipeline.reopened_experiment_lease_request import public_experiment_lease_request
from research_pipeline.reopened_experiment_lease import public_reopened_experiment_lease
from research_pipeline.reopened_local_f0_run import public_reopened_local_f0_run
from research_pipeline.reopened_local_f0_completion import public_completion, SIGNAL as LOCAL_F0_SIGNAL
from research_pipeline.reopened_p0_authorization import public_p0_authorization
DEFAULT_LEDGER_ROOT = Path(os.environ["PAPER_ACCEPTANCE_ROOT"]).expanduser() if os.environ.get("PAPER_ACCEPTANCE_ROOT") else None
DEFAULT_ARTIFACT_ROOT = Path(os.environ["PAPER_ACCEPTANCE_ARTIFACT_ROOT"]).expanduser() if os.environ.get("PAPER_ACCEPTANCE_ARTIFACT_ROOT") else None
DEFAULT_FREEZE_ROOT = Path(os.environ["PAPER_SUBMISSION_FREEZE_ROOT"]).expanduser() if os.environ.get("PAPER_SUBMISSION_FREEZE_ROOT") else None
DEFAULT_HANDOFF_ROOT = Path(os.environ["PAPER_SUBMISSION_HANDOFF_ROOT"]).expanduser() if os.environ.get("PAPER_SUBMISSION_HANDOFF_ROOT") else None
DEFAULT_SIGNOFF_ROOT = Path(os.environ["PAPER_HUMAN_SIGNOFF_ROOT"]).expanduser() if os.environ.get("PAPER_HUMAN_SIGNOFF_ROOT") else None
DEFAULT_ATTEMPT_ROOT = Path(os.environ["PAPER_SUBMISSION_ATTEMPT_ROOT"]).expanduser() if os.environ.get("PAPER_SUBMISSION_ATTEMPT_ROOT") else None
DEFAULT_ATTEMPT_WORKFLOW_ROOT = Path(os.environ["PAPER_SUBMISSION_ATTEMPT_WORKFLOW_ROOT"]).expanduser() if os.environ.get("PAPER_SUBMISSION_ATTEMPT_WORKFLOW_ROOT") else None
DEFAULT_SCIENTIFIC_REOPEN_ROOT = Path(os.environ["PAPER_SCIENTIFIC_REOPEN_ROOT"]).expanduser() if os.environ.get("PAPER_SCIENTIFIC_REOPEN_ROOT") else None
DEFAULT_SCIENTIFIC_CONTRACT_ROOT = Path(os.environ["RESEARCH_SCIENTIFIC_CONTRACT_ROOT"]).expanduser() if os.environ.get("RESEARCH_SCIENTIFIC_CONTRACT_ROOT") else None
DEFAULT_SCIENTIFIC_PROBLEM_GATE_ROOT = Path(os.environ["RESEARCH_SCIENTIFIC_PROBLEM_GATE_ROOT"]).expanduser() if os.environ.get("RESEARCH_SCIENTIFIC_PROBLEM_GATE_ROOT") else None
DEFAULT_SCIENTIFIC_METHOD_ROOT = Path(os.environ["RESEARCH_SCIENTIFIC_METHOD_ROOT"]).expanduser() if os.environ.get("RESEARCH_SCIENTIFIC_METHOD_ROOT") else None
DEFAULT_SCIENTIFIC_BLUEPRINT_ROOT = Path(os.environ["RESEARCH_SCIENTIFIC_BLUEPRINT_ROOT"]).expanduser() if os.environ.get("RESEARCH_SCIENTIFIC_BLUEPRINT_ROOT") else None
DEFAULT_LOCAL_VALIDATION_AUTH_ROOT = Path(os.environ["RESEARCH_LOCAL_VALIDATION_AUTH_ROOT"]).expanduser() if os.environ.get("RESEARCH_LOCAL_VALIDATION_AUTH_ROOT") else None
DEFAULT_PRE_EXPERIMENT_ADAPTER_ROOT = Path(os.environ["RESEARCH_PRE_EXPERIMENT_ADAPTER_ROOT"]).expanduser() if os.environ.get("RESEARCH_PRE_EXPERIMENT_ADAPTER_ROOT") else None
DEFAULT_EXPERIMENT_LEASE_REQUEST_ROOT = Path(os.environ["RESEARCH_EXPERIMENT_LEASE_REQUEST_ROOT"]).expanduser() if os.environ.get("RESEARCH_EXPERIMENT_LEASE_REQUEST_ROOT") else None
DEFAULT_EXPERIMENT_LEASE_ROOT = Path(os.environ["RESEARCH_EXPERIMENT_LEASE_ROOT"]).expanduser() if os.environ.get("RESEARCH_EXPERIMENT_LEASE_ROOT") else None
DEFAULT_EXPERIMENT_AUTHORITY_ROOT = Path(os.environ["RESEARCH_EXPERIMENT_AUTHORITY_ROOT"]).expanduser() if os.environ.get("RESEARCH_EXPERIMENT_AUTHORITY_ROOT") else None
DEFAULT_RUN_START_ROOT = Path(os.environ["RESEARCH_RUN_START_ROOT"]).expanduser() if os.environ.get("RESEARCH_RUN_START_ROOT") else None
DEFAULT_RESOURCE_LEASE_ROOT = Path(os.environ["RESEARCH_RESOURCE_LEASE_ROOT"]).expanduser() if os.environ.get("RESEARCH_RESOURCE_LEASE_ROOT") else None
DEFAULT_RUN_COMPLETION_ROOT = Path(os.environ["RESEARCH_RUN_COMPLETION_ROOT"]).expanduser() if os.environ.get("RESEARCH_RUN_COMPLETION_ROOT") else None
DEFAULT_P0_AUTH_ROOT = Path(os.environ["RESEARCH_P0_AUTH_ROOT"]).expanduser() if os.environ.get("RESEARCH_P0_AUTH_ROOT") else None
DEFAULT_JSON = ROOT / "generated/paper-registry-state.json"
DEFAULT_JS = ROOT / "generated/paper-registry-state.js"
C01_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
C01_ADJUDICATION = ROOT / "generated/d2-failure-memory-provenance-targeted-repair-adjudication-20260822.json"
D2_SCHEDULER = ROOT / "generated/d2-active-paper-reopen-scheduler.json"


def digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def latest_event(row: dict[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(row.get("events") or []):
        if event.get("event_type") == event_type:
            return event
    return {}


def event_payload(row: dict[str, Any], event_type: str) -> dict[str, Any]:
    event = latest_event(row, event_type)
    payload = event.get("receipt") or event.get("result") or {}
    return payload if isinstance(payload, dict) else {}


def targeted_repair_boundary(paper_id: str) -> dict[str, Any]:
    """Return public-safe decision boundaries for a paper still in targeted repair.

    This projection intentionally carries only scientific decision summaries. It omits
    execution hosts, filesystem locations, provider response identifiers, and raw prompts.
    """
    if paper_id != C01_ID or not C01_ADJUDICATION.exists():
        return {}
    try:
        adjudication = _load_json(C01_ADJUDICATION)
    except (OSError, json.JSONDecodeError):
        return {}
    scheduler_state = "HOLD_SUPPORT_AND_IDENTIFICATION"
    if D2_SCHEDULER.exists():
        try:
            scheduler = _load_json(D2_SCHEDULER)
            match = next((entry for entry in scheduler.get("entries") or [] if entry.get("paper_id") == paper_id), {})
            scheduler_state = str(match.get("scheduler_state") or scheduler_state)
        except (OSError, json.JSONDecodeError):
            pass
    r4 = adjudication.get("r4_primary_result") or {}
    power = adjudication.get("power_audit") or {}
    ident = adjudication.get("identification_audit") or {}
    confirm = adjudication.get("independent_confirmation_support") or {}
    decision = adjudication.get("scientific_decision") or {}
    return {
        "scheduler_state": scheduler_state,
        "scientific_decision": str(decision.get("C4") or ""),
        "primary_result": {
            "success_minus_failure": r4.get("mean_success_minus_failure_terminal_rate"),
            "effect_floor": r4.get("support_effect_floor"),
            "permutation_p_success_greater": r4.get("permutation_p_success_greater"),
            "p_threshold": r4.get("p_threshold"),
            "support_gate_pass": r4.get("support_gate_pass") is True,
            "counterevidence_gate_pass": r4.get("counterevidence_gate_pass") is True,
            "verdict": str(r4.get("verdict") or ""),
        },
        "power": {
            "four_pair_power_range": list(power.get("approx_power_at_four_pairs_range") or []),
            "independent_pairs_for_80pct_power_range": list(power.get("approx_independent_pairs_for_80pct_power_range") or []),
        },
        "identification": {
            "primary_pairs": int(ident.get("primary_pairs") or 0),
            "original_verifier_strict_pass": int(ident.get("original_verifier_strict_pass") or 0),
            "deepseek_strict_pass": int(ident.get("deepseek_strict_pass") or 0),
            "kimi_strict_pass": int(ident.get("kimi_strict_pass") or 0),
            "three_reviewer_unanimous_strict_pass": int(ident.get("three_reviewer_unanimous_strict_pass") or 0),
            "minimum_embedding_cosine": ident.get("minimum_primary_embedding_cosine"),
        },
        "independent_confirmation": {
            "fresh_same_release_qualified_tasks": int(confirm.get("fresh_qualified_task_count") or 0),
            "same_release_confirmation_available": confirm.get("same_release_confirmation_available") is True,
        },
        "reopen_conditions": list(adjudication.get("reopen_conditions") or []),
        "forbidden_repairs": list(adjudication.get("forbidden_repairs") or []),
    }


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def paper_preparation(row: dict[str, Any], artifact_root: Path | None) -> dict[str, Any]:
    receipt = event_payload(row, "paper-preparation")
    if not receipt and artifact_root is not None:
        p = artifact_root / str(row.get("paper_id") or "") / "paper-preparation-receipt.json"
        if p.exists():
            try:
                loaded = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    receipt = loaded
            except Exception:
                pass
    state = str(row.get("current_state") or "")
    if receipt:
        status = "PASS" if receipt.get("pass") is True else "BLOCKED"
    elif state == "SUBMISSION_READY":
        status = "LEGACY_READY_NEEDS_PREPARATION_MIGRATION"
    else:
        status = "NOT_YET_ELIGIBLE"
    return {
        "status": status,
        "pass": receipt.get("pass") is True,
        "protocol_version": str(receipt.get("protocol_version") or ""),
        "receipt_sha256": str(receipt.get("receipt_sha256") or ""),
        "gate_pass": dict(receipt.get("gate_pass") or {}),
        "blockers": list(receipt.get("blockers") or []),
        "human_submission_signoff_pending": state == "SUBMISSION_READY" and receipt.get("pass") is True,
    }


def submission_freeze(paper_id: str, preparation: dict[str, Any], freeze_root: Path | None) -> dict[str, Any]:
    receipt: dict[str, Any] = {}
    drift_errors: list[str] = []
    if freeze_root is not None:
        path = freeze_root / f"{paper_id}.json"
        if path.exists():
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
                event = latest_event(row, "pre-submission-freeze")
                candidate = event.get("receipt") or {}
                identity = {key: candidate.get(key) for key in (
                    "paper_id", "contract_sha256", "paper_preparation_receipt_sha256",
                    "venue_policy_snapshot_sha256", "frozen_artifacts", "status", "human_signoff_status"
                )}
                if candidate.get("freeze_sha256") == digest(identity):
                    receipt = candidate
                else:
                    drift_errors.append("freeze-receipt-hash-invalid")
            except Exception:
                drift_errors.append("freeze-ledger-unreadable")
    if receipt:
        drift_errors.extend(verify_frozen_artifacts(receipt))
        if preparation.get("receipt_sha256") and receipt.get("paper_preparation_receipt_sha256") != preparation.get("receipt_sha256"):
            drift_errors.append("freeze-preparation-receipt-stale")
        if freeze_root is not None:
            index = freeze_root / "current-freeze-index.json"
            if index.exists():
                try:
                    current_policy = str(json.loads(index.read_text(encoding="utf-8")).get("venue_policy_snapshot_sha256") or "")
                    if current_policy and receipt.get("venue_policy_snapshot_sha256") != current_policy:
                        drift_errors.append("freeze-venue-policy-stale")
                except Exception:
                    drift_errors.append("freeze-policy-index-unreadable")
        drift_errors = list(dict.fromkeys(drift_errors))
        status = "MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING" if not drift_errors else "MACHINE_FREEZE_STALE"
    elif preparation.get("status") == "PASS":
        status = "MACHINE_FREEZE_PENDING"
    elif preparation.get("status") == "BLOCKED":
        status = "PREPARATION_BLOCKED"
    else:
        status = "NOT_READY_FOR_HUMAN_SUBMISSION"
    impact = audit_freeze_receipt(receipt) if receipt else {
        "status": "NOT_AVAILABLE",
        "impact_classes": [],
        "minimum_rerun_paper_preparation_gates": [],
        "minimum_rerun_paper_acceptance_checks": [],
        "requires_full_preparation_reaudit": False,
    }
    if status == "MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING" and impact.get("status") != "NO_CHANGE":
        impact = dict(impact)
        impact["status"] = "INCONSISTENT_FREEZE_AUDIT"
    return {
        "status": status,
        "freeze_sha256": str(receipt.get("freeze_sha256") or ""),
        "venue_policy_snapshot_sha256": str(receipt.get("venue_policy_snapshot_sha256") or ""),
        "human_signoff_status": str(receipt.get("human_signoff_status") or ""),
        "frozen_artifacts": len(receipt.get("frozen_artifacts") or []),
        "integrity_pass": bool(receipt) and not drift_errors,
        "drift_errors": drift_errors,
        "revision_impact": {
            "status": str(impact.get("status") or ""),
            "impact_classes": list(impact.get("impact_classes") or []),
            "minimum_rerun_paper_preparation_gates": list(impact.get("minimum_rerun_paper_preparation_gates") or []),
            "minimum_rerun_paper_acceptance_checks": list(impact.get("minimum_rerun_paper_acceptance_checks") or []),
            "requires_full_preparation_reaudit": impact.get("requires_full_preparation_reaudit") is True,
        },
        "external_human_submission_authority_required": True,
    }


def submission_handoff(paper_id: str, freeze: dict[str, Any], handoff_root: Path | None) -> dict[str, Any]:
    receipt: dict[str, Any] = {}
    errors: list[str] = []
    if handoff_root is not None:
        path = handoff_root / f"{paper_id}.json"
        if path.exists():
            try:
                row = _load_json(path)
                errors.extend(validate_handoff_ledger(row))
                event = latest_event(row, "machine-submission-handoff")
                candidate = event.get("receipt") or {}
                if isinstance(candidate, dict) and validate_handoff_receipt(candidate):
                    receipt = candidate
                else:
                    errors.append("handoff-receipt-invalid")
            except Exception:
                errors.append("handoff-ledger-unreadable")
    if receipt and freeze.get("freeze_sha256") and receipt.get("freeze_sha256") != freeze.get("freeze_sha256"):
        errors.append("handoff-freeze-stale")
    errors = list(dict.fromkeys(errors))
    if receipt:
        status = "MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED" if not errors and freeze.get("integrity_pass") is True else "MACHINE_HANDOFF_STALE"
    elif freeze.get("status") == "MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING":
        status = "MACHINE_HANDOFF_PENDING"
    elif freeze.get("status") == "PREPARATION_BLOCKED":
        status = "PREPARATION_BLOCKED"
    else:
        status = "NOT_READY_FOR_HUMAN_SUBMISSION"
    return {
        "status": status,
        "handoff_sha256": str(receipt.get("handoff_sha256") or ""),
        "freeze_sha256": str(receipt.get("freeze_sha256") or ""),
        "venue": str(receipt.get("venue") or ""),
        "deadlines_aoe": dict(receipt.get("deadlines_aoe") or {}),
        "human_confirmation_status": str(receipt.get("human_confirmation_status") or ""),
        "frozen_artifacts": len(receipt.get("frozen_artifacts") or []),
        "artifacts": [dict(item) for item in receipt.get("frozen_artifacts") or [] if isinstance(item, dict)],
        "human_checklist": [str(item) for item in receipt.get("human_checklist") or [] if str(item)],
        "must_not_submit_if_hash_mismatch": receipt.get("must_not_submit_if_hash_mismatch") is True,
        "must_not_submit_if_freeze_stale": receipt.get("must_not_submit_if_freeze_stale") is True,
        "integrity_pass": bool(receipt) and not errors and freeze.get("integrity_pass") is True,
        "errors": errors,
        "external_human_submission_authority_required": True,
    }


def human_signoff(paper_id: str, handoff: dict[str, Any], freeze_root: Path | None, handoff_root: Path | None, signoff_root: Path | None) -> dict[str, Any]:
    if handoff.get("status") != "MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED":
        return {"status": "NOT_ELIGIBLE", "signoff_sha256": "", "integrity_pass": False, "errors": [], "actual_submission_status": "NOT_SUBMITTED"}
    if signoff_root is None:
        return {"status": "PENDING_HUMAN_CONFIRMATION", "signoff_sha256": "", "integrity_pass": False, "errors": [], "actual_submission_status": "NOT_SUBMITTED"}
    path = signoff_root / f"{paper_id}.json"
    if not path.exists():
        return {"status": "PENDING_HUMAN_CONFIRMATION", "signoff_sha256": "", "integrity_pass": False, "errors": [], "actual_submission_status": "NOT_SUBMITTED"}
    try:
        row = _load_json(path)
        errors = list(validate_signoff_ledger(row))
        event = latest_event(row, "human-submission-signoff")
        receipt = event.get("receipt") or {}
        if freeze_root is None or handoff_root is None:
            errors.append("human-signoff-currentness-roots-missing")
        else:
            freeze_ledger = _load_json(freeze_root / f"{paper_id}.json")
            handoff_ledger = _load_json(handoff_root / f"{paper_id}.json")
            errors.extend(verify_current_signoff(row, handoff_ledger, freeze_ledger))
        errors = list(dict.fromkeys(errors))
    except Exception:
        return {"status": "HUMAN_SIGNOFF_STALE", "signoff_sha256": "", "integrity_pass": False, "errors": ["human-signoff-ledger-unreadable"], "actual_submission_status": "NOT_SUBMITTED"}
    return {
        "status": "HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING" if not errors else "HUMAN_SIGNOFF_STALE",
        "signoff_sha256": str(receipt.get("signoff_sha256") or ""),
        "integrity_pass": not errors,
        "errors": errors,
        "confirmed_at": str(receipt.get("confirmed_at") or ""),
        "actual_submission_status": str(receipt.get("actual_submission_status") or "NOT_SUBMITTED"),
    }


def actual_submission(row: dict[str, Any]) -> dict[str, Any]:
    receipt = event_payload(row, "actual-submission")
    valid = bool(receipt) and str(receipt.get("contract_sha256") or "") == str(row.get("contract_sha256") or "") and validate_submission_receipt(receipt)
    state = str(row.get("current_state") or "")
    if state in {"SUBMITTED", "REBUTTAL", "LEARN"}:
        status = "VENUE_SUBMISSION_CONFIRMED" if valid else "SUBMITTED_RECEIPT_INVALID"
    elif valid:
        status = "VENUE_SUBMISSION_RECEIPT_RECORDED_TRANSITION_PENDING"
    else:
        status = "NOT_SUBMITTED"
    return {
        "status": status,
        "valid": valid,
        "venue": str(receipt.get("venue") or ""),
        "venue_submission_id": str(receipt.get("venue_submission_id") or ""),
        "venue_forum_ref": str(receipt.get("venue_forum_ref") or ""),
        "submitted_at": str(receipt.get("submitted_at") or ""),
        "submission_receipt_sha256": str(receipt.get("submission_receipt_sha256") or ""),
    }


def rebuttal_state(row: dict[str, Any]) -> dict[str, Any]:
    receipt = event_payload(row, "rebuttal-preparation")
    skip = event_payload(row, "rebuttal-skipped-by-venue")
    decision = event_payload(row, "venue-decision")
    valid = bool(receipt) and str(receipt.get("contract_sha256") or "") == str(row.get("contract_sha256") or "") and validate_rebuttal_receipt(receipt)
    skip_valid = bool(skip) and str(skip.get("contract_sha256") or "") == str(row.get("contract_sha256") or "") and validate_rebuttal_skipped_by_venue_receipt(skip)
    decision_valid = bool(decision) and str(decision.get("contract_sha256") or "") == str(row.get("contract_sha256") or "") and validate_venue_decision_receipt(decision)
    skip_lineage_ok = skip_valid and decision_valid and decision.get("decision_phase") == "PRE_REBUTTAL_TERMINAL" and decision.get("rebuttal_available") is False and skip.get("venue_decision_sha256") == decision.get("venue_decision_sha256")
    state = str(row.get("current_state") or "")
    if state == "REBUTTAL":
        status = "REBUTTAL_ACTIVE" if valid and receipt.get("pass") is True else ("REBUTTAL_SKIPPED_BY_VENUE" if skip_lineage_ok else "REBUTTAL_RECEIPT_INVALID")
    elif state == "SUBMITTED":
        status = "REBUTTAL_PREPARED_TRANSITION_PENDING" if valid and receipt.get("pass") is True else ("REBUTTAL_SKIPPED_TRANSITION_PENDING" if skip_lineage_ok else "AWAITING_REVIEW_OR_REBUTTAL_PREPARATION")
    elif state == "LEARN" and skip_lineage_ok:
        status = "REBUTTAL_SKIPPED_BY_VENUE"
    else:
        status = "NOT_ELIGIBLE"
    summary = receipt.get("summary") if isinstance(receipt.get("summary"), dict) else {}
    return {
        "status": status,
        "valid": (valid and receipt.get("pass") is True) or skip_lineage_ok,
        "pass": receipt.get("pass") is True or skip_lineage_ok,
        "review_set_sha256": str(receipt.get("review_set_sha256") or ""),
        "rebuttal_receipt_sha256": str(receipt.get("rebuttal_receipt_sha256") or ""),
        "rebuttal_skip_sha256": str(skip.get("rebuttal_skip_sha256") or ""),
        "venue_decision_sha256": str(decision.get("venue_decision_sha256") or "") if skip_lineage_ok else "",
        "review_fabrication_forbidden": skip.get("review_fabrication_forbidden") is True if skip_lineage_ok else False,
        "reviews": int(summary.get("reviews") or 0),
        "objections": int(summary.get("objections") or 0),
        "decision_critical": int(summary.get("decision_critical") or 0),
        "missing_decisive_evidence": int(summary.get("missing_decisive_evidence") or 0),
        "new_claim_requests": int(summary.get("new_claim_requests") or 0),
        "response_words": int(receipt.get("response_words") or 0),
        "response_limit_words": int(receipt.get("response_limit_words") or 0),
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
    }


def learning_state(row: dict[str, Any]) -> dict[str, Any]:
    decision = event_payload(row, "venue-decision")
    learning = event_payload(row, "post-decision-learning")
    decision_valid = bool(decision) and str(decision.get("contract_sha256") or "") == str(row.get("contract_sha256") or "") and validate_venue_decision_receipt(decision)
    learning_valid = bool(learning) and str(learning.get("contract_sha256") or "") == str(row.get("contract_sha256") or "") and validate_learning_receipt(learning)
    lineage_ok = decision_valid and learning_valid and learning.get("venue_decision_sha256") == decision.get("venue_decision_sha256")
    state = str(row.get("current_state") or "")
    if state == "LEARN":
        status = "LEARN_COMPLETE" if lineage_ok and learning.get("pass") is True else "LEARN_RECEIPT_INVALID"
    elif state == "REBUTTAL":
        if not decision_valid:
            status = "AWAITING_FINAL_VENUE_DECISION"
        elif lineage_ok and learning.get("pass") is True:
            status = "LEARNING_PREPARED_TRANSITION_PENDING"
        else:
            status = "POST_DECISION_LEARNING_PENDING"
    else:
        status = "NOT_ELIGIBLE"
    summary = learning.get("summary") if isinstance(learning.get("summary"), dict) else {}
    return {
        "status": status,
        "decision": str(decision.get("decision") or ""),
        "venue_decision_sha256": str(decision.get("venue_decision_sha256") or ""),
        "learning_receipt_sha256": str(learning.get("learning_receipt_sha256") or ""),
        "decision_valid": decision_valid,
        "learning_valid": lineage_ok,
        "lessons": int(summary.get("lessons") or 0),
        "scientific_diagnostic_only": int(summary.get("scientific_diagnostic_only") or 0),
        "paper_process_lessons": int(summary.get("paper_process_lessons") or 0),
        "scientific_claim_status_unchanged": True,
        "automatic_reopen_authorized": False,
        "new_experiment_authorized": False,
        "claim_expansion_authorized": False,
    }


def submission_attempt_state(paper_id: str, paper_state: str, attempt_root: Path | None) -> dict[str, Any]:
    empty = {
        "status": "ATTEMPT_NOT_PLANNED" if paper_state == "LEARN" else "NOT_ELIGIBLE",
        "attempts": 0,
        "latest_attempt_id": "",
        "latest_attempt_sha256": "",
        "latest_attempt_type": "",
        "target_venue": "",
        "machine_preparation_eligible": False,
        "requires_explicit_scientific_reopen": False,
        "parent_submission_bytes_immutable": True,
        "validation_errors": [],
    }
    if attempt_root is None:
        return empty
    path = attempt_root / f"{paper_id}.json"
    if not path.exists():
        return empty
    try:
        row = _load_json(path)
        errors = validate_attempt_ledger(row)
        summary = public_attempt_summary(row)
    except Exception:
        return {**empty, "status": "ATTEMPT_LEDGER_INVALID", "validation_errors": ["attempt-ledger-unreadable"]}
    if errors:
        return {**empty, **summary, "status": "ATTEMPT_LEDGER_INVALID", "validation_errors": errors}
    return {**empty, **summary, "status": str(summary.get("latest_status") or empty["status"])}


def submission_attempt_workflow_state(attempt: dict[str, Any], workflow_root: Path | None) -> dict[str, Any]:
    empty = {
        "status": "ATTEMPT_WORKFLOW_NOT_STARTED" if int(attempt.get("attempts") or 0) > 0 and attempt.get("machine_preparation_eligible") is True else "NOT_ELIGIBLE",
        "attempt_id": str(attempt.get("latest_attempt_id") or ""),
        "attempt_sha256": str(attempt.get("latest_attempt_sha256") or ""),
        "preparation_sha256": "",
        "freeze_sha256": "",
        "handoff_sha256": "",
        "signoff_sha256": "",
        "submission_conflict_guard_sha256": "",
        "submission_conflict_guard_status": "",
        "submission_conflict_count": 0,
        "submission_receipt_sha256": "",
        "venue_submission_id": "",
        "submitted_at": "",
        "actual_submission_status": "NOT_SUBMITTED",
        "review_set_sha256": "",
        "review_count": 0,
        "rebuttal_receipt_sha256": "",
        "rebuttal_missing_decisive_evidence": 0,
        "rebuttal_new_claim_requests": 0,
        "venue_decision_sha256": "",
        "venue_decision": "",
        "decision_phase": "",
        "rebuttal_skip_sha256": "",
        "learning_receipt_sha256": "",
        "learning_lessons": 0,
        "learning_scientific_diagnostic_only": 0,
        "frozen_artifacts": 0,
        "freeze_drift_errors": [],
        "validation_errors": [],
        "human_confirmation_status": "",
        "parent_submission_bytes_immutable": True,
    }
    attempt_id = str(attempt.get("latest_attempt_id") or "")
    if not attempt_id or workflow_root is None:
        return empty
    path = workflow_root / f"{attempt_id}.json"
    if not path.exists():
        return empty
    try:
        row = _load_json(path)
        errors = validate_attempt_workflow_ledger(row)
        summary = current_attempt_workflow_summary(row)
    except Exception:
        return {**empty, "status": "ATTEMPT_WORKFLOW_INVALID", "validation_errors": ["attempt-workflow-ledger-unreadable"]}
    if errors:
        return {**empty, **summary, "status": "ATTEMPT_WORKFLOW_INVALID", "validation_errors": errors}
    if str(summary.get("attempt_sha256") or "") != str(attempt.get("latest_attempt_sha256") or ""):
        return {**empty, **summary, "status": "ATTEMPT_WORKFLOW_INVALID", "validation_errors": ["attempt-workflow-plan-lineage-mismatch"]}
    return {**empty, **summary}


def scientific_reopen_state(paper_id: str, attempt: dict[str, Any], reopen_root: Path | None, scientific_contract_root: Path | None = None, scientific_problem_gate_root: Path | None = None, scientific_method_root: Path | None = None, scientific_blueprint_root: Path | None = None, local_validation_auth_root: Path | None = None, pre_experiment_adapter_root: Path | None = None, experiment_lease_request_root: Path | None = None, experiment_lease_root: Path | None = None, experiment_authority_root: Path | None = None, run_start_root: Path | None = None, resource_lease_root: Path | None = None, run_completion_root: Path | None = None, p0_auth_root: Path | None = None) -> dict[str, Any]:
    empty = {
        "status": "SCIENTIFIC_REOPEN_PROPOSAL_REQUIRED" if attempt.get("requires_explicit_scientific_reopen") is True else "NOT_ELIGIBLE",
        "attempt_sha256": str(attempt.get("latest_attempt_sha256") or ""),
        "proposal_sha256": "",
        "authorization_sha256": "",
        "authorization_scope": "",
        "external_scientific_authority_confirmed": False,
        "research_os_handoff_sha256": "",
        "new_contract_seed_id": "",
        "destination_gate": "",
        "new_contract_creation_eligible": False,
        "new_scientific_contract_required": attempt.get("requires_explicit_scientific_reopen") is True,
        "existing_scientific_contract_immutable": True,
        "automatic_contract_creation_authorized": False,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "gpu_execution_authorized": False,
        "validation_errors": [],
        "new_contract": {**public_reopened_contract_summary({}), "problem_gate": public_reopen_problem_gate_summary({}), "method_design": public_reopen_method_summary(Path('/nonexistent'), ''), "experiment_blueprint": public_reopen_blueprint_summary(Path('/nonexistent'), ''), "local_validation_authorization": public_local_validation_authorization(Path('/nonexistent'), ''), "pre_experiment": public_reopened_pre_experiment(Path('/nonexistent'), ''), "experiment_lease_request": public_experiment_lease_request(Path('/nonexistent'), ''), "experiment_lease": public_reopened_experiment_lease(Path('/nonexistent'), ''), "local_f0_run": public_reopened_local_f0_run(Path('/nonexistent'), ''), "local_f0_completion": public_completion(Path('/nonexistent'), '')},
    }
    if attempt.get("requires_explicit_scientific_reopen") is not True or reopen_root is None:
        return empty
    path = reopen_root / f"{paper_id}.json"
    if not path.exists():
        return empty
    try:
        row = _load_json(path)
        errors = validate_scientific_reopen_ledger(row)
        summary = public_scientific_reopen_summary(row, str(attempt.get("latest_attempt_sha256") or ""))
    except Exception:
        return {**empty, "status": "SCIENTIFIC_REOPEN_LEDGER_INVALID", "validation_errors": ["scientific-reopen-ledger-unreadable"]}
    if errors:
        return {**empty, **summary, "status": "SCIENTIFIC_REOPEN_LEDGER_INVALID", "validation_errors": errors}
    projected = {**empty, **summary}
    handoff_sha = str(projected.get("research_os_handoff_sha256") or "")
    if handoff_sha and scientific_contract_root is not None:
        try:
            contract = find_contract_by_handoff(scientific_contract_root, handoff_sha)
            contract_summary = public_reopened_contract_summary(contract)
        except Exception:
            contract_summary = {**public_reopened_contract_summary({}), "status": "NEW_SCIENTIFIC_CONTRACT_INVALID"}
        if contract_summary.get("status") == "NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED":
            gate_root = scientific_problem_gate_root or (scientific_contract_root.parent / "scientific-contract-problem-gates")
            gate_receipt = load_latest_reopen_problem_gate(gate_root, str(contract_summary.get("contract_id") or ""))
            gate_summary = public_reopen_problem_gate_summary(gate_receipt)
            method_root = scientific_method_root or (scientific_contract_root.parent / "scientific-contract-method-design")
            method_summary = public_reopen_method_summary(method_root, str(contract_summary.get("contract_id") or "")) if gate_summary.get("status") == "REOPEN_PROBLEM_GATE_PASS_METHOD_DESIGN_REVIEW_ELIGIBLE" else public_reopen_method_summary(Path('/nonexistent'), '')
            blueprint_root = scientific_blueprint_root or (scientific_contract_root.parent / "scientific-contract-experiment-blueprints")
            blueprint_summary = public_reopen_blueprint_summary(blueprint_root, str(contract_summary.get("contract_id") or "")) if method_summary.get("status") == "REOPEN_METHOD_REVIEW_PASS_BLUEPRINT_DESIGN_ELIGIBLE" else public_reopen_blueprint_summary(Path('/nonexistent'), '')
            local_auth_root = local_validation_auth_root or (scientific_contract_root.parent / "scientific-contract-local-validation-authority")
            local_auth_summary = public_local_validation_authorization(local_auth_root, str(contract_summary.get("contract_id") or "")) if blueprint_summary.get("status") == "REOPEN_BLUEPRINT_REVIEW_PASS_LOCAL_VALIDATION_AUTHORIZATION_ELIGIBLE" else public_local_validation_authorization(Path('/nonexistent'), '')
            adapter_root = pre_experiment_adapter_root or (scientific_contract_root.parent / "scientific-contract-pre-experiment")
            pre_experiment_summary = public_reopened_pre_experiment(adapter_root, str(contract_summary.get("contract_id") or "")) if local_auth_summary.get("status") == "LOCAL_VALIDATION_AUTHORIZED_PRE_EXPERIMENT_COMPILER_REQUIRED" else public_reopened_pre_experiment(Path('/nonexistent'), '')
            lease_request_root = experiment_lease_request_root or (scientific_contract_root.parent / "scientific-contract-experiment-lease-requests")
            lease_request_summary = public_experiment_lease_request(lease_request_root, str(contract_summary.get("contract_id") or "")) if pre_experiment_summary.get("status") == "PRE_EXPERIMENT_COMPILER_PASS_EXPERIMENT_LEASE_REQUIRED" else public_experiment_lease_request(Path('/nonexistent'), '')
            lease_root = experiment_lease_root or (scientific_contract_root.parent / "scientific-contract-experiment-leases")
            authority_root = experiment_authority_root or scientific_contract_root.parent
            lease_summary = public_reopened_experiment_lease(lease_root, str(contract_summary.get("contract_id") or ""), authority_root=authority_root) if lease_request_summary.get("status") == "EXPERIMENT_LEASE_REQUEST_READY_EXPLICIT_ACQUIRE_REQUIRED" else public_reopened_experiment_lease(Path('/nonexistent'), '')
            run_root = run_start_root or (scientific_contract_root.parent / "scientific-contract-run-starts")
            resource_root = resource_lease_root or scientific_contract_root.parent
            run_summary = public_reopened_local_f0_run(run_root, str(contract_summary.get("contract_id") or ""), resource_root=resource_root, authority_root=authority_root) if lease_summary.get("status") == "EXPERIMENT_LEASE_ACTIVE_RUN_NOT_STARTED" else public_reopened_local_f0_run(Path('/nonexistent'), '')
            completion_root = run_completion_root or (scientific_contract_root.parent / "scientific-contract-run-completions")
            completion_summary = public_completion(completion_root, str(contract_summary.get("contract_id") or ""))
            p0_root = p0_auth_root or (scientific_contract_root.parent / "scientific-contract-p0-authority")
            p0_summary = public_p0_authorization(p0_root, str(contract_summary.get("contract_id") or "")) if completion_summary.get("status") == LOCAL_F0_SIGNAL else public_p0_authorization(Path('/nonexistent'), '')
            contract_summary = {**contract_summary, "problem_gate": gate_summary, "method_design": method_summary, "experiment_blueprint": blueprint_summary, "local_validation_authorization": local_auth_summary, "pre_experiment": pre_experiment_summary, "experiment_lease_request": lease_request_summary, "experiment_lease": lease_summary, "local_f0_run": run_summary, "local_f0_completion": completion_summary, "p0_authorization": p0_summary}
            if gate_summary["status"] == "REOPEN_PROBLEM_GATE_REQUIRED":
                projected["status"] = "NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED"
            elif gate_summary["status"] == "REOPEN_PROBLEM_GATE_PASS_METHOD_DESIGN_REVIEW_ELIGIBLE":
                if method_summary.get("status") == "REOPEN_METHOD_REVIEW_PASS_BLUEPRINT_DESIGN_ELIGIBLE":
                    if completion_summary.get("status") != "LOCAL_F0_COMPLETION_REQUIRED":
                        projected["status"] = p0_summary.get("status") if completion_summary.get("status") == LOCAL_F0_SIGNAL and p0_summary.get("status") == "P0_LIFECYCLE_AUTHORIZED_CONFIRMATORY_PLAN_REQUIRED" else completion_summary.get("status")
                    elif pre_experiment_summary.get("status") == "PRE_EXPERIMENT_COMPILER_PASS_EXPERIMENT_LEASE_REQUIRED":
                        if lease_summary.get("status") == "EXPERIMENT_LEASE_ACTIVE_RUN_NOT_STARTED":
                            projected["status"] = run_summary.get("status") if run_summary.get("status") != "REOPEN_LOCAL_F0_RUN_START_REQUIRED" else lease_summary.get("status")
                        else:
                            projected["status"] = lease_summary.get("status") if lease_summary.get("status") != "EXPERIMENT_LEASE_ACQUIRE_REQUIRED" else lease_request_summary.get("status")
                    else:
                        projected["status"] = pre_experiment_summary.get("status") if local_auth_summary.get("status") == "LOCAL_VALIDATION_AUTHORIZED_PRE_EXPERIMENT_COMPILER_REQUIRED" else (local_auth_summary.get("status") if blueprint_summary.get("status") == "REOPEN_BLUEPRINT_REVIEW_PASS_LOCAL_VALIDATION_AUTHORIZATION_ELIGIBLE" else blueprint_summary.get("status"))
                else:
                    projected["status"] = method_summary.get("status") or "REOPEN_METHOD_DESIGN_REQUIRED"
            else:
                projected["status"] = gate_summary["status"]
        projected["new_contract"] = contract_summary
    return projected


def project_paper(path: Path, artifact_root: Path | None, freeze_root: Path | None = None, handoff_root: Path | None = None, signoff_root: Path | None = None, attempt_root: Path | None = None, attempt_workflow_root: Path | None = None, scientific_reopen_root: Path | None = None, scientific_contract_root: Path | None = None, scientific_problem_gate_root: Path | None = None, scientific_method_root: Path | None = None, scientific_blueprint_root: Path | None = None, local_validation_auth_root: Path | None = None, pre_experiment_adapter_root: Path | None = None, experiment_lease_request_root: Path | None = None, experiment_lease_root: Path | None = None, experiment_authority_root: Path | None = None, run_start_root: Path | None = None, resource_lease_root: Path | None = None, run_completion_root: Path | None = None, p0_auth_root: Path | None = None) -> dict[str, Any]:
    row = json.loads(path.read_text(encoding="utf-8"))
    contract = row.get("contract") or {}
    summary = row.get("summary") or {}
    claim_audit = event_payload(row, "claim-audit")
    manuscript_ci = event_payload(row, "manuscript-ci")
    prebuttal = event_payload(row, "prebuttal")
    readiness = event_payload(row, "submission-readiness")
    preparation = paper_preparation(row, artifact_root)
    supported = contract.get("supported_claims") or {}
    unsupported = contract.get("unsupported_claims") or {}
    active = contract.get("active_unrefuted_claims") or {}
    if not isinstance(supported, dict):
        supported = {}
    if not isinstance(unsupported, dict):
        unsupported = {}
    if not isinstance(active, dict):
        active = {}
    paper_id = str(row.get("paper_id") or contract.get("paper_id") or path.stem)
    freeze = submission_freeze(paper_id, preparation, freeze_root)
    handoff = submission_handoff(paper_id, freeze, handoff_root)
    signoff = human_signoff(paper_id, handoff, freeze_root, handoff_root, signoff_root)
    submission = actual_submission(row)
    rebuttal = rebuttal_state(row)
    learning = learning_state(row)
    state = str(row.get("current_state") or "")
    attempt = submission_attempt_state(paper_id, state, attempt_root)
    attempt_workflow = submission_attempt_workflow_state(attempt, attempt_workflow_root)
    attempt_history = build_attempt_history(paper_id, attempt_root, attempt_workflow_root)
    scientific_reopen = scientific_reopen_state(paper_id, attempt, scientific_reopen_root, scientific_contract_root, scientific_problem_gate_root, scientific_method_root, scientific_blueprint_root, local_validation_auth_root, pre_experiment_adapter_root, experiment_lease_request_root, experiment_lease_root, experiment_authority_root, run_start_root, resource_lease_root, run_completion_root, p0_auth_root)
    scientific_layer = "SUPPORTED_AND_AUDITED" if claim_audit.get("pass") is True else ("ACTIVE_REPAIR" if state == "TARGETED_REPAIR" else "PRE_AUDIT")
    paper_quality_layer = "PASS" if manuscript_ci.get("pass") is True and prebuttal.get("pass") is True else ("IN_PROGRESS" if state not in {"PAPER_EVIDENCE", "PAPER_DESIGN"} else "NOT_STARTED")
    return {
        "paper_id": paper_id,
        "title": str(contract.get("title") or paper_id),
        "central_question": str(contract.get("central_question") or ""),
        "current_state": state,
        "contract_sha256": str(row.get("contract_sha256") or ""),
        "ledger_events": len(row.get("events") or []),
        "supported_claims": len(supported),
        "active_unrefuted_claims": len(active),
        "unsupported_claims": len(unsupported),
        "limitations": len(contract.get("limitations") or []),
        "layers": {
            "scientific": scientific_layer,
            "paper_quality": paper_quality_layer,
            "paper_preparation": preparation["status"],
            "submission": submission["status"] if submission["status"] != "NOT_SUBMITTED" else (signoff["status"] if signoff["status"] != "PENDING_HUMAN_CONFIRMATION" and signoff["status"] != "NOT_ELIGIBLE" else handoff["status"]),
            "post_submission": learning["status"] if learning["status"] != "NOT_ELIGIBLE" else rebuttal["status"],
            "next_attempt": scientific_reopen["status"] if attempt.get("requires_explicit_scientific_reopen") is True else (attempt_workflow["status"] if attempt_workflow["status"] != "NOT_ELIGIBLE" else attempt["status"]),
        },
        "gates": {
            "claim_audit": claim_audit.get("pass") is True,
            "manuscript_ci": manuscript_ci.get("pass") is True,
            "prebuttal": prebuttal.get("pass") is True,
            "submission_readiness": readiness.get("submission_ready") is True,
        },
        "paper_preparation": preparation,
        "submission_freeze": freeze,
        "submission_handoff": handoff,
        "human_signoff": signoff,
        "actual_submission": submission,
        "rebuttal": rebuttal,
        "learning": learning,
        "submission_attempt": attempt,
        "submission_attempt_workflow": attempt_workflow,
        "submission_attempt_history": attempt_history,
        "scientific_reopen": scientific_reopen,
        "targeted_repair_boundary": targeted_repair_boundary(paper_id) if state == "TARGETED_REPAIR" else {},
        "ledger_summary": {
            "mock_reviews": int(summary.get("mock_reviews") or 0),
            "claim_audit_receipts": int(summary.get("claim_audit_receipts") or 0),
            "manuscript_ci_receipts": int(summary.get("manuscript_ci_receipts") or 0),
            "prebuttal_receipts": int(summary.get("prebuttal_receipts") or 0),
            "paper_preparation_receipts": int(summary.get("paper_preparation_receipts") or 0),
            "actual_submission_receipts": int(summary.get("actual_submission_receipts") or 0),
            "rebuttal_preparation_receipts": int(summary.get("rebuttal_preparation_receipts") or 0),
            "rebuttal_skipped_receipts": int(summary.get("rebuttal_skipped_receipts") or 0),
            "venue_decision_receipts": int(summary.get("venue_decision_receipts") or 0),
            "post_decision_learning_receipts": int(summary.get("post_decision_learning_receipts") or 0),
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def source_watermark(ledger_root: Path, freeze_root: Path | None = None, handoff_root: Path | None = None, signoff_root: Path | None = None, attempt_root: Path | None = None, attempt_workflow_root: Path | None = None, scientific_reopen_root: Path | None = None, scientific_contract_root: Path | None = None, scientific_problem_gate_root: Path | None = None, scientific_method_root: Path | None = None, scientific_blueprint_root: Path | None = None, local_validation_auth_root: Path | None = None, pre_experiment_adapter_root: Path | None = None, experiment_lease_request_root: Path | None = None, experiment_lease_root: Path | None = None, experiment_authority_root: Path | None = None, run_start_root: Path | None = None, resource_lease_root: Path | None = None, run_completion_root: Path | None = None, p0_auth_root: Path | None = None) -> str:
    timestamps: list[str] = []
    for path in sorted(ledger_root.glob("*.json")):
        try:
            payload = _load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        updated = str(payload.get("updated_at") or "")
        if updated:
            timestamps.append(updated)
    authority_dir = (experiment_authority_root / "experiment-authority") if experiment_authority_root is not None else None
    resource_dir = (resource_lease_root / "resource-leases") if resource_lease_root is not None else None
    for extra_root in (freeze_root, handoff_root, signoff_root, attempt_root, attempt_workflow_root, scientific_reopen_root, scientific_contract_root, scientific_problem_gate_root, scientific_method_root, scientific_blueprint_root, local_validation_auth_root, pre_experiment_adapter_root, experiment_lease_request_root, experiment_lease_root, run_start_root, run_completion_root, p0_auth_root, authority_dir, resource_dir):
        if extra_root is None or not extra_root.exists():
            continue
        for path in sorted(extra_root.glob("*.json")):
            if path.name in {"current-freeze-index.json", "venue-policy-iclr2027-20260822.json", "index.json"}:
                continue
            try:
                payload = _load_json(path)
            except (OSError, json.JSONDecodeError):
                continue
            updated = str(payload.get("updated_at") or payload.get("released_at") or payload.get("acquired_at") or payload.get("created_at") or "")
            if updated:
                timestamps.append(updated)
    return max(timestamps) if timestamps else "1970-01-01T00:00:00+00:00"


def build(ledger_root: Path, artifact_root: Path | None = None, freeze_root: Path | None = None, handoff_root: Path | None = None, signoff_root: Path | None = None, attempt_root: Path | None = None, attempt_workflow_root: Path | None = None, scientific_reopen_root: Path | None = None, scientific_contract_root: Path | None = None, scientific_problem_gate_root: Path | None = None, scientific_method_root: Path | None = None, scientific_blueprint_root: Path | None = None, local_validation_auth_root: Path | None = None, pre_experiment_adapter_root: Path | None = None, experiment_lease_request_root: Path | None = None, experiment_lease_root: Path | None = None, experiment_authority_root: Path | None = None, run_start_root: Path | None = None, resource_lease_root: Path | None = None, run_completion_root: Path | None = None, p0_auth_root: Path | None = None) -> dict[str, Any]:
    papers = [project_paper(path, artifact_root, freeze_root, handoff_root, signoff_root, attempt_root, attempt_workflow_root, scientific_reopen_root, scientific_contract_root, scientific_problem_gate_root, scientific_method_root, scientific_blueprint_root, local_validation_auth_root, pre_experiment_adapter_root, experiment_lease_request_root, experiment_lease_root, experiment_authority_root, run_start_root, resource_lease_root, run_completion_root, p0_auth_root) for path in sorted(ledger_root.glob("*.json"))]
    order = {"LEARN": -3, "REBUTTAL": -2, "SUBMITTED": -1, "SUBMISSION_READY": 0, "PREBUTTAL": 1, "PDF_QA": 2, "CLAIM_AUDIT": 3, "TARGETED_REPAIR": 4, "MOCK_PC": 5, "MANUSCRIPT": 6, "PAPER_DESIGN": 7, "PAPER_EVIDENCE": 8}
    papers.sort(key=lambda p: (order.get(p["current_state"], 99), p["paper_id"]))
    summary = {
        "papers": len(papers),
        "submission_ready": sum(p["current_state"] == "SUBMISSION_READY" for p in papers),
        "targeted_repair": sum(p["current_state"] == "TARGETED_REPAIR" for p in papers),
        "preparation_pass": sum(p["paper_preparation"]["pass"] for p in papers),
        "preparation_blocked": sum(p["paper_preparation"]["status"] == "BLOCKED" for p in papers),
        "legacy_ready_needs_preparation_migration": sum(p["paper_preparation"]["status"] == "LEGACY_READY_NEEDS_PREPARATION_MIGRATION" for p in papers),
        "machine_frozen_candidates": sum(p["submission_freeze"]["status"] == "MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING" for p in papers),
        "machine_freeze_stale": sum(p["submission_freeze"]["status"] == "MACHINE_FREEZE_STALE" for p in papers),
        "machine_handoff_ready": sum(p["submission_handoff"]["status"] == "MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED" for p in papers),
        "machine_handoff_stale": sum(p["submission_handoff"]["status"] == "MACHINE_HANDOFF_STALE" for p in papers),
        "human_submission_signoff_pending": sum(p["submission_handoff"]["status"] == "MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED" and p["human_signoff"]["status"] == "PENDING_HUMAN_CONFIRMATION" for p in papers),
        "human_signoff_complete": sum(p["human_signoff"]["status"] == "HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING" for p in papers),
        "human_signoff_stale": sum(p["human_signoff"]["status"] == "HUMAN_SIGNOFF_STALE" for p in papers),
        "submitted": sum(p["current_state"] == "SUBMITTED" for p in papers),
        "submitted_receipt_bound": sum(p["actual_submission"]["status"] == "VENUE_SUBMISSION_CONFIRMED" for p in papers),
        "rebuttal_active": sum(p["rebuttal"]["status"] == "REBUTTAL_ACTIVE" for p in papers),
        "rebuttal_prepared": sum(p["rebuttal"]["status"] == "REBUTTAL_PREPARED_TRANSITION_PENDING" for p in papers),
        "rebuttal_skipped_by_venue": sum(p["rebuttal"]["status"] in {"REBUTTAL_SKIPPED_TRANSITION_PENDING", "REBUTTAL_SKIPPED_BY_VENUE"} for p in papers),
        "final_decisions_recorded": sum(p["learning"]["decision_valid"] for p in papers),
        "learning_prepared": sum(p["learning"]["status"] == "LEARNING_PREPARED_TRANSITION_PENDING" for p in papers),
        "learn_complete": sum(p["learning"]["status"] == "LEARN_COMPLETE" for p in papers),
        "submission_attempt_plans": sum(int((p["submission_attempt_history"].get("summary") or {}).get("attempts") or 0) for p in papers),
        "attempt_machine_preparation_eligible": sum(int((p["submission_attempt_history"].get("summary") or {}).get("machine_preparation_eligible") or 0) for p in papers),
        "attempts_requiring_scientific_reopen": sum(int((p["submission_attempt_history"].get("summary") or {}).get("requires_explicit_scientific_reopen") or 0) for p in papers),
        "resubmission_plans": sum(int((p["submission_attempt_history"].get("summary") or {}).get("resubmissions") or 0) for p in papers),
        "camera_ready_plans": sum(int((p["submission_attempt_history"].get("summary") or {}).get("camera_ready") or 0) for p in papers),
        "attempt_preparation_pass": sum(p["submission_attempt_workflow"].get("status") == "ATTEMPT_PREPARATION_PASS_FREEZE_PENDING" for p in papers),
        "attempt_machine_frozen": sum(p["submission_attempt_workflow"].get("status") == "ATTEMPT_MACHINE_FROZEN_HANDOFF_PENDING" for p in papers),
        "attempt_machine_handoff_ready": sum(p["submission_attempt_workflow"].get("status") == "ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED" for p in papers),
        "attempt_submission_blocked_active_sibling": sum(p["submission_attempt_workflow"].get("status") == "ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING" for p in papers),
        "attempt_workflow_stale_or_invalid": sum(int((p["submission_attempt_history"].get("summary") or {}).get("invalid_attempts") or 0) for p in papers),
        "attempt_human_signoff_complete": sum(int((p["submission_attempt_history"].get("summary") or {}).get("human_signoffs") or 0) for p in papers),
        "attempt_venue_submitted": sum(int((p["submission_attempt_history"].get("summary") or {}).get("venue_submissions") or 0) for p in papers),
        "attempt_reviews_recorded": sum(int((p["submission_attempt_history"].get("summary") or {}).get("review_sets") or 0) for p in papers),
        "attempt_rebuttals_prepared": sum(int((p["submission_attempt_history"].get("summary") or {}).get("rebuttals_prepared") or 0) for p in papers),
        "attempt_final_decisions_recorded": sum(int((p["submission_attempt_history"].get("summary") or {}).get("final_decisions") or 0) for p in papers),
        "attempt_post_decision_learning_complete": sum(int((p["submission_attempt_history"].get("summary") or {}).get("post_decision_learn_complete") or 0) for p in papers),
        "attempt_rebuttal_skipped_by_venue": sum(int((p["submission_attempt_history"].get("summary") or {}).get("rebuttals_skipped_by_venue") or 0) for p in papers),
        "scientific_reopen_proposed": sum(p["scientific_reopen"].get("status") == "SCIENTIFIC_REOPEN_PROPOSED_EXTERNAL_AUTHORITY_REQUIRED" for p in papers),
        "scientific_reopen_authorized_new_contract_required": sum(p["scientific_reopen"].get("status") == "EXTERNAL_SCIENTIFIC_REOPEN_CONFIRMED_NEW_CONTRACT_REQUIRED" for p in papers),
        "scientific_reopen_research_os_handoff_ready": sum(p["scientific_reopen"].get("status") == "RESEARCH_OS_NEW_CONTRACT_HANDOFF_READY" for p in papers),
        "reopened_scientific_contract_problem_gate_required": sum(p["scientific_reopen"].get("status") == "NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED" for p in papers),
        "reopen_problem_gate_pass": sum(p["scientific_reopen"].get("status") == "REOPEN_PROBLEM_GATE_PASS_METHOD_DESIGN_REVIEW_ELIGIBLE" for p in papers),
        "reopen_problem_gate_blocked": sum(p["scientific_reopen"].get("status") == "REOPEN_PROBLEM_GATE_BLOCKED" for p in papers),
        "reopen_problem_gate_invalid": sum(p["scientific_reopen"].get("status") == "REOPEN_PROBLEM_GATE_LEDGER_INVALID" for p in papers),
        "reopen_method_design_required": sum(p["scientific_reopen"].get("status") == "REOPEN_METHOD_DESIGN_REQUIRED" for p in papers),
        "reopen_method_design_awaiting_review": sum(p["scientific_reopen"].get("status") == "REOPEN_METHOD_DESIGN_FROZEN_AWAITING_INDEPENDENT_REVIEW" for p in papers),
        "reopen_method_review_pass": sum(p["scientific_reopen"].get("status") == "REOPEN_METHOD_REVIEW_PASS_BLUEPRINT_DESIGN_ELIGIBLE" for p in papers),
        "reopen_method_review_blocked": sum(p["scientific_reopen"].get("status") == "REOPEN_METHOD_REVIEW_BLOCKED" for p in papers),
        "reopen_method_invalid": sum(p["scientific_reopen"].get("status") == "REOPEN_METHOD_LEDGER_INVALID" for p in papers),
        "reopen_blueprint_required": sum(p["scientific_reopen"].get("status") == "REOPEN_EXPERIMENT_BLUEPRINT_REQUIRED" for p in papers),
        "reopen_blueprint_awaiting_review": sum(p["scientific_reopen"].get("status") == "REOPEN_EXPERIMENT_BLUEPRINT_FROZEN_AWAITING_INDEPENDENT_REVIEW" for p in papers),
        "reopen_blueprint_review_pass": sum(p["scientific_reopen"].get("status") == "REOPEN_BLUEPRINT_REVIEW_PASS_LOCAL_VALIDATION_AUTHORIZATION_ELIGIBLE" for p in papers),
        "reopen_blueprint_review_blocked": sum(p["scientific_reopen"].get("status") == "REOPEN_BLUEPRINT_REVIEW_BLOCKED" for p in papers),
        "reopen_blueprint_invalid": sum(p["scientific_reopen"].get("status") == "REOPEN_BLUEPRINT_LEDGER_INVALID" for p in papers),
        "reopen_local_validation_authorized": sum(p["scientific_reopen"].get("status") == "LOCAL_VALIDATION_AUTHORIZED_PRE_EXPERIMENT_COMPILER_REQUIRED" for p in papers),
        "reopen_local_validation_authority_invalid": sum(p["scientific_reopen"].get("status") == "LOCAL_VALIDATION_AUTHORITY_LEDGER_INVALID" for p in papers),
        "reopen_pre_experiment_required": sum(p["scientific_reopen"].get("status") == "PRE_EXPERIMENT_COMPILER_REQUIRED" for p in papers),
        "reopen_pre_experiment_blocked": sum(p["scientific_reopen"].get("status") == "PRE_EXPERIMENT_COMPILER_BLOCKED" for p in papers),
        "reopen_pre_experiment_pass_lease_required": sum(p["scientific_reopen"].get("status") == "PRE_EXPERIMENT_COMPILER_PASS_EXPERIMENT_LEASE_REQUIRED" for p in papers),
        "reopen_pre_experiment_invalid": sum(p["scientific_reopen"].get("status") == "PRE_EXPERIMENT_ADAPTER_LEDGER_INVALID" for p in papers),
        "reopen_experiment_lease_request_required": sum(p["scientific_reopen"].get("status") == "EXPERIMENT_LEASE_REQUEST_REQUIRED" for p in papers),
        "reopen_experiment_lease_request_ready": sum(p["scientific_reopen"].get("status") == "EXPERIMENT_LEASE_REQUEST_READY_EXPLICIT_ACQUIRE_REQUIRED" for p in papers),
        "reopen_experiment_lease_request_invalid": sum(p["scientific_reopen"].get("status") == "EXPERIMENT_LEASE_REQUEST_LEDGER_INVALID" for p in papers),
        "reopen_experiment_lease_active_run_not_started": sum(p["scientific_reopen"].get("status") == "EXPERIMENT_LEASE_ACTIVE_RUN_NOT_STARTED" for p in papers),
        "reopen_experiment_lease_stale_or_released": sum(p["scientific_reopen"].get("status") == "EXPERIMENT_LEASE_STALE_OR_RELEASED" for p in papers),
        "reopen_experiment_lease_invalid": sum(p["scientific_reopen"].get("status") == "EXPERIMENT_LEASE_LEDGER_INVALID" for p in papers),
        "reopen_local_f0_run_start_required": sum(p["scientific_reopen"].get("status") == "REOPEN_LOCAL_F0_RUN_START_REQUIRED" for p in papers),
        "reopen_local_f0_run_active": sum(p["scientific_reopen"].get("status") == "REOPEN_LOCAL_F0_RUN_STARTED_RESOURCE_LEASE_ACTIVE" for p in papers),
        "reopen_local_f0_run_stale_or_released": sum(p["scientific_reopen"].get("status") == "REOPEN_LOCAL_F0_RUN_RESOURCE_LEASE_STALE_OR_RELEASED" for p in papers),
        "reopen_local_f0_run_invalid": sum(p["scientific_reopen"].get("status") == "REOPEN_LOCAL_F0_RUN_LEDGER_INVALID" for p in papers),
        "reopen_local_f0_completion_pending_adjudication": sum(p["scientific_reopen"].get("status") == "REOPEN_LOCAL_F0_RUN_COMPLETED_AWAIT_EVIDENCE_ADJUDICATION" for p in papers),
        "reopen_local_f0_completion_protocol_hold": sum(p["scientific_reopen"].get("status") == "REOPEN_LOCAL_F0_RUN_COMPLETED_PROTOCOL_HOLD" for p in papers),
        "reopen_local_f0_signal_p0_review": sum(p["scientific_reopen"].get("status") == "LOCAL_F0_VALID_SCREENING_SIGNAL_P0_AUTHORIZATION_REVIEW_ELIGIBLE" for p in papers),
        "reopen_local_f0_valid_no_signal": sum(p["scientific_reopen"].get("status") == "LOCAL_F0_VALID_SCREENING_NO_SIGNAL_NO_NEGATIVE_SCIENTIFIC_AUTHORITY" for p in papers),
        "reopen_local_f0_typed_stop_or_inconclusive": sum(p["scientific_reopen"].get("status") in {"LOCAL_F0_SUPPORT_STOP_NO_SCIENTIFIC_NEGATIVE","LOCAL_F0_PROTOCOL_STOP_NO_SCIENTIFIC_INTERPRETATION","LOCAL_F0_RUNTIME_STOP_NO_SCIENTIFIC_NEGATIVE","LOCAL_F0_IMPLEMENTATION_STOP_NO_SCIENTIFIC_NEGATIVE","LOCAL_F0_BUDGET_STOP_NO_SCIENTIFIC_RESULT","LOCAL_F0_BASELINE_BOUNDARY_NO_METHOD_NEGATIVE","LOCAL_F0_INCONCLUSIVE_NO_SCIENTIFIC_NEGATIVE"} for p in papers),
        "reopen_local_f0_completion_invalid": sum(p["scientific_reopen"].get("status") == "LOCAL_F0_COMPLETION_LEDGER_INVALID" for p in papers),
        "reopen_p0_lifecycle_authorized": sum(p["scientific_reopen"].get("status") == "P0_LIFECYCLE_AUTHORIZED_CONFIRMATORY_PLAN_REQUIRED" for p in papers),
        "reopen_p0_authority_invalid": sum(p["scientific_reopen"].get("status") == "P0_AUTHORITY_LEDGER_INVALID" for p in papers),
        "scientific_reopen_invalid": sum(p["scientific_reopen"].get("status") == "SCIENTIFIC_REOPEN_LEDGER_INVALID" for p in papers),
    }
    payload = {
        "schema_version": "1.1",
        "generated_at": source_watermark(ledger_root, freeze_root, handoff_root, signoff_root, attempt_root, attempt_workflow_root, scientific_reopen_root, scientific_contract_root, scientific_problem_gate_root, scientific_method_root, scientific_blueprint_root, local_validation_auth_root, pre_experiment_adapter_root, experiment_lease_request_root, experiment_lease_root, experiment_authority_root, run_start_root, resource_lease_root, run_completion_root, p0_auth_root),
        "source": "canonical_paper_acceptance_ledger",
        "summary": summary,
        "papers": papers,
        "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
    }
    payload["projection_sha256"] = digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger-root", type=Path, default=DEFAULT_LEDGER_ROOT, help="Canonical Paper Acceptance ledger root; may also be supplied via PAPER_ACCEPTANCE_ROOT.")
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT, help="Optional paper-preparation artifact root; may also be supplied via PAPER_ACCEPTANCE_ARTIFACT_ROOT.")
    parser.add_argument("--freeze-root", type=Path, default=DEFAULT_FREEZE_ROOT, help="Optional pre-submission freeze ledger root; may also be supplied via PAPER_SUBMISSION_FREEZE_ROOT.")
    parser.add_argument("--handoff-root", type=Path, default=DEFAULT_HANDOFF_ROOT, help="Optional machine submission handoff ledger root; may also be supplied via PAPER_SUBMISSION_HANDOFF_ROOT.")
    parser.add_argument("--signoff-root", type=Path, default=DEFAULT_SIGNOFF_ROOT, help="Optional human signoff ledger root; may also be supplied via PAPER_HUMAN_SIGNOFF_ROOT.")
    parser.add_argument("--attempt-root", type=Path, default=DEFAULT_ATTEMPT_ROOT, help="Optional resubmission/camera-ready attempt ledger root; may also be supplied via PAPER_SUBMISSION_ATTEMPT_ROOT.")
    parser.add_argument("--attempt-workflow-root", type=Path, default=DEFAULT_ATTEMPT_WORKFLOW_ROOT, help="Optional attempt-scoped Preparation/Freeze/Handoff workflow root; may also be supplied via PAPER_SUBMISSION_ATTEMPT_WORKFLOW_ROOT.")
    parser.add_argument("--scientific-reopen-root", type=Path, default=DEFAULT_SCIENTIFIC_REOPEN_ROOT, help="Optional scientific-reopen proposal/authorization ledger root; may also be supplied via PAPER_SCIENTIFIC_REOPEN_ROOT.")
    parser.add_argument("--scientific-contract-root", type=Path, default=DEFAULT_SCIENTIFIC_CONTRACT_ROOT, help="Optional reopened scientific-contract directory; may also be supplied via RESEARCH_SCIENTIFIC_CONTRACT_ROOT.")
    parser.add_argument("--scientific-problem-gate-root", type=Path, default=DEFAULT_SCIENTIFIC_PROBLEM_GATE_ROOT, help="Optional reopened scientific-contract Problem Gate ledger root; may also be supplied via RESEARCH_SCIENTIFIC_PROBLEM_GATE_ROOT.")
    parser.add_argument("--scientific-method-root", type=Path, default=DEFAULT_SCIENTIFIC_METHOD_ROOT, help="Optional reopened scientific-contract method-design ledger root; may also be supplied via RESEARCH_SCIENTIFIC_METHOD_ROOT.")
    parser.add_argument("--scientific-blueprint-root", type=Path, default=DEFAULT_SCIENTIFIC_BLUEPRINT_ROOT, help="Optional reopened experiment-blueprint ledger root; may also be supplied via RESEARCH_SCIENTIFIC_BLUEPRINT_ROOT.")
    parser.add_argument("--local-validation-auth-root", type=Path, default=DEFAULT_LOCAL_VALIDATION_AUTH_ROOT, help="Optional reopened local-validation human authority ledger root; may also be supplied via RESEARCH_LOCAL_VALIDATION_AUTH_ROOT.")
    parser.add_argument("--pre-experiment-adapter-root", type=Path, default=DEFAULT_PRE_EXPERIMENT_ADAPTER_ROOT, help="Optional reopened Pre-Experiment adapter ledger root; may also be supplied via RESEARCH_PRE_EXPERIMENT_ADAPTER_ROOT.")
    parser.add_argument("--experiment-lease-request-root", type=Path, default=DEFAULT_EXPERIMENT_LEASE_REQUEST_ROOT, help="Optional reopened experiment lease-request ledger root; may also be supplied via RESEARCH_EXPERIMENT_LEASE_REQUEST_ROOT.")
    parser.add_argument("--experiment-lease-root", type=Path, default=DEFAULT_EXPERIMENT_LEASE_ROOT, help="Optional reopened experiment-lease receipt root; may also be supplied via RESEARCH_EXPERIMENT_LEASE_ROOT.")
    parser.add_argument("--experiment-authority-root", type=Path, default=DEFAULT_EXPERIMENT_AUTHORITY_ROOT, help="Root containing the canonical experiment-authority single-writer leases; may also be supplied via RESEARCH_EXPERIMENT_AUTHORITY_ROOT.")
    parser.add_argument("--run-start-root", type=Path, default=DEFAULT_RUN_START_ROOT, help="Optional reopened local-F0 run-start ledger root; may also be supplied via RESEARCH_RUN_START_ROOT.")
    parser.add_argument("--resource-lease-root", type=Path, default=DEFAULT_RESOURCE_LEASE_ROOT, help="Root containing GPU/resource leases; may also be supplied via RESEARCH_RESOURCE_LEASE_ROOT.")
    parser.add_argument("--run-completion-root", type=Path, default=DEFAULT_RUN_COMPLETION_ROOT, help="Optional reopened local-F0 completion/adjudication ledger root; may also be supplied via RESEARCH_RUN_COMPLETION_ROOT.")
    parser.add_argument("--p0-auth-root", type=Path, default=DEFAULT_P0_AUTH_ROOT, help="Optional reopened P0 lifecycle human-authority ledger root; may also be supplied via RESEARCH_P0_AUTH_ROOT.")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--js-output", type=Path, default=DEFAULT_JS)
    args = parser.parse_args()
    if args.ledger_root is None:
        parser.error("canonical ledger root is required via --ledger-root or PAPER_ACCEPTANCE_ROOT")
    handoff_root = args.handoff_root
    if handoff_root is None:
        candidate = args.ledger_root.parent / "paper-submission-handoffs"
        handoff_root = candidate if candidate.is_dir() else None
    signoff_root = args.signoff_root
    if signoff_root is None:
        candidate = args.ledger_root.parent / "paper-human-signoffs"
        signoff_root = candidate if candidate.is_dir() else None
    attempt_root = args.attempt_root
    if attempt_root is None:
        candidate = args.ledger_root.parent / "paper-submission-attempts"
        attempt_root = candidate if candidate.is_dir() else None
    attempt_workflow_root = args.attempt_workflow_root
    if attempt_workflow_root is None:
        candidate = args.ledger_root.parent / "paper-submission-attempt-workflows"
        attempt_workflow_root = candidate if candidate.is_dir() else None
    scientific_reopen_root = args.scientific_reopen_root
    if scientific_reopen_root is None:
        candidate = args.ledger_root.parent / "paper-scientific-reopen"
        scientific_reopen_root = candidate if candidate.is_dir() else None
    scientific_contract_root = args.scientific_contract_root
    if scientific_contract_root is None:
        candidate = args.ledger_root.parent / "scientific-contracts"
        scientific_contract_root = candidate if candidate.is_dir() else None
    scientific_problem_gate_root = args.scientific_problem_gate_root
    if scientific_problem_gate_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-problem-gates"
        scientific_problem_gate_root = candidate if candidate.is_dir() else None
    scientific_method_root = args.scientific_method_root
    if scientific_method_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-method-design"
        scientific_method_root = candidate if candidate.is_dir() else None
    scientific_blueprint_root = args.scientific_blueprint_root
    if scientific_blueprint_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-experiment-blueprints"
        scientific_blueprint_root = candidate if candidate.is_dir() else None
    local_validation_auth_root = args.local_validation_auth_root
    if local_validation_auth_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-local-validation-authority"
        local_validation_auth_root = candidate if candidate.is_dir() else None
    pre_experiment_adapter_root = args.pre_experiment_adapter_root
    if pre_experiment_adapter_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-pre-experiment"
        pre_experiment_adapter_root = candidate if candidate.is_dir() else None
    experiment_lease_request_root = args.experiment_lease_request_root
    if experiment_lease_request_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-experiment-lease-requests"
        experiment_lease_request_root = candidate if candidate.is_dir() else None
    experiment_lease_root = args.experiment_lease_root
    if experiment_lease_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-experiment-leases"
        experiment_lease_root = candidate if candidate.is_dir() else None
    experiment_authority_root = args.experiment_authority_root or args.ledger_root.parent
    run_start_root = args.run_start_root
    if run_start_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-run-starts"
        run_start_root = candidate if candidate.is_dir() else None
    resource_lease_root = args.resource_lease_root or args.ledger_root.parent
    run_completion_root = args.run_completion_root
    if run_completion_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-run-completions"
        run_completion_root = candidate if candidate.is_dir() else None
    p0_auth_root = args.p0_auth_root
    if p0_auth_root is None:
        candidate = args.ledger_root.parent / "scientific-contract-p0-authority"
        p0_auth_root = candidate if candidate.is_dir() else None
    state = build(args.ledger_root, args.artifact_root, args.freeze_root, handoff_root, signoff_root, attempt_root, attempt_workflow_root, scientific_reopen_root, scientific_contract_root, scientific_problem_gate_root, scientific_method_root, scientific_blueprint_root, local_validation_auth_root, pre_experiment_adapter_root, experiment_lease_request_root, experiment_lease_root, experiment_authority_root, run_start_root, resource_lease_root, run_completion_root, p0_auth_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.js_output.write_text("window.PAPER_REGISTRY_STATE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "summary": state["summary"], "projection_sha256": state["projection_sha256"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
