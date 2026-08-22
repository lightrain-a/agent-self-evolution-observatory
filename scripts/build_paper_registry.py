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
DEFAULT_LEDGER_ROOT = Path(os.environ["PAPER_ACCEPTANCE_ROOT"]).expanduser() if os.environ.get("PAPER_ACCEPTANCE_ROOT") else None
DEFAULT_ARTIFACT_ROOT = Path(os.environ["PAPER_ACCEPTANCE_ARTIFACT_ROOT"]).expanduser() if os.environ.get("PAPER_ACCEPTANCE_ARTIFACT_ROOT") else None
DEFAULT_FREEZE_ROOT = Path(os.environ["PAPER_SUBMISSION_FREEZE_ROOT"]).expanduser() if os.environ.get("PAPER_SUBMISSION_FREEZE_ROOT") else None
DEFAULT_HANDOFF_ROOT = Path(os.environ["PAPER_SUBMISSION_HANDOFF_ROOT"]).expanduser() if os.environ.get("PAPER_SUBMISSION_HANDOFF_ROOT") else None
DEFAULT_SIGNOFF_ROOT = Path(os.environ["PAPER_HUMAN_SIGNOFF_ROOT"]).expanduser() if os.environ.get("PAPER_HUMAN_SIGNOFF_ROOT") else None
DEFAULT_ATTEMPT_ROOT = Path(os.environ["PAPER_SUBMISSION_ATTEMPT_ROOT"]).expanduser() if os.environ.get("PAPER_SUBMISSION_ATTEMPT_ROOT") else None
DEFAULT_ATTEMPT_WORKFLOW_ROOT = Path(os.environ["PAPER_SUBMISSION_ATTEMPT_WORKFLOW_ROOT"]).expanduser() if os.environ.get("PAPER_SUBMISSION_ATTEMPT_WORKFLOW_ROOT") else None
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


def project_paper(path: Path, artifact_root: Path | None, freeze_root: Path | None = None, handoff_root: Path | None = None, signoff_root: Path | None = None, attempt_root: Path | None = None, attempt_workflow_root: Path | None = None) -> dict[str, Any]:
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
            "next_attempt": attempt_workflow["status"] if attempt_workflow["status"] != "NOT_ELIGIBLE" else attempt["status"],
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


def source_watermark(ledger_root: Path, freeze_root: Path | None = None, handoff_root: Path | None = None, signoff_root: Path | None = None, attempt_root: Path | None = None, attempt_workflow_root: Path | None = None) -> str:
    timestamps: list[str] = []
    for path in sorted(ledger_root.glob("*.json")):
        try:
            payload = _load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        updated = str(payload.get("updated_at") or "")
        if updated:
            timestamps.append(updated)
    for extra_root in (freeze_root, handoff_root, signoff_root, attempt_root, attempt_workflow_root):
        if extra_root is None or not extra_root.exists():
            continue
        for path in sorted(extra_root.glob("*.json")):
            if path.name in {"current-freeze-index.json", "venue-policy-iclr2027-20260822.json", "index.json"}:
                continue
            try:
                payload = _load_json(path)
            except (OSError, json.JSONDecodeError):
                continue
            updated = str(payload.get("updated_at") or "")
            if updated:
                timestamps.append(updated)
    return max(timestamps) if timestamps else "1970-01-01T00:00:00+00:00"


def build(ledger_root: Path, artifact_root: Path | None = None, freeze_root: Path | None = None, handoff_root: Path | None = None, signoff_root: Path | None = None, attempt_root: Path | None = None, attempt_workflow_root: Path | None = None) -> dict[str, Any]:
    papers = [project_paper(path, artifact_root, freeze_root, handoff_root, signoff_root, attempt_root, attempt_workflow_root) for path in sorted(ledger_root.glob("*.json"))]
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
        "attempt_workflow_stale_or_invalid": sum(int((p["submission_attempt_history"].get("summary") or {}).get("invalid_attempts") or 0) for p in papers),
        "attempt_human_signoff_complete": sum(int((p["submission_attempt_history"].get("summary") or {}).get("human_signoffs") or 0) for p in papers),
        "attempt_venue_submitted": sum(int((p["submission_attempt_history"].get("summary") or {}).get("venue_submissions") or 0) for p in papers),
        "attempt_reviews_recorded": sum(int((p["submission_attempt_history"].get("summary") or {}).get("review_sets") or 0) for p in papers),
        "attempt_rebuttals_prepared": sum(int((p["submission_attempt_history"].get("summary") or {}).get("rebuttals_prepared") or 0) for p in papers),
        "attempt_final_decisions_recorded": sum(int((p["submission_attempt_history"].get("summary") or {}).get("final_decisions") or 0) for p in papers),
        "attempt_post_decision_learning_complete": sum(int((p["submission_attempt_history"].get("summary") or {}).get("post_decision_learn_complete") or 0) for p in papers),
        "attempt_rebuttal_skipped_by_venue": sum(int((p["submission_attempt_history"].get("summary") or {}).get("rebuttals_skipped_by_venue") or 0) for p in papers),
    }
    payload = {
        "schema_version": "1.1",
        "generated_at": source_watermark(ledger_root, freeze_root, handoff_root, signoff_root, attempt_root, attempt_workflow_root),
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
    state = build(args.ledger_root, args.artifact_root, args.freeze_root, handoff_root, signoff_root, attempt_root, attempt_workflow_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.js_output.write_text("window.PAPER_REGISTRY_STATE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "summary": state["summary"], "projection_sha256": state["projection_sha256"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
