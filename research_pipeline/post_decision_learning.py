from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

LEARN_SCHEMA_VERSION = "1.0"
FINAL_DECISIONS = {"ACCEPT", "REJECT", "WITHDRAWN", "VENUE_CLOSED_WITHOUT_DECISION"}
LESSON_CATEGORIES = {
    "PAPER_POSITIONING",
    "EVIDENCE_DESIGN",
    "EXPERIMENT_DESIGN",
    "STATISTICS",
    "WRITING_CLARITY",
    "VISUAL_COMMUNICATION",
    "REPRODUCIBILITY",
    "VENUE_FIT",
    "REVIEW_PROCESS",
    "SCIENTIFIC_DIAGNOSTIC",
}
REUSE_SCOPES = {
    "PAPER_PREPARATION_HEURISTIC",
    "EXPERIMENT_DESIGN_PRIOR",
    "VENUE_SELECTION_PRIOR",
    "WRITING_HEURISTIC",
    "REVIEW_HEURISTIC",
    "SCIENTIFIC_DIAGNOSTIC_ONLY",
}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _latest(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, Mapping) and event.get("event_type") == event_type:
            return dict(event)
    return {}


def _receipt(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    event = _latest(row, event_type)
    receipt = event.get("receipt") or {}
    return dict(receipt) if isinstance(receipt, Mapping) else {}


def venue_decision_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "submission_receipt_sha256": receipt.get("submission_receipt_sha256"),
        "rebuttal_receipt_sha256": receipt.get("rebuttal_receipt_sha256"),
        "decision_id": receipt.get("decision_id"),
        "source_ref": receipt.get("source_ref"),
        "received_at": receipt.get("received_at"),
        "decision": receipt.get("decision"),
        "decision_text_sha256": receipt.get("decision_text_sha256"),
        "scientific_claim_status_unchanged": receipt.get("scientific_claim_status_unchanged"),
    }


def build_venue_decision_receipt(
    *,
    paper_ledger: Mapping[str, Any],
    decision_id: str,
    source_ref: str,
    received_at: str,
    decision: str,
    decision_text: str,
) -> dict[str, Any]:
    from .rebuttal_protocol import validate_rebuttal_receipt
    from .venue_submission_receipt import validate_submission_receipt

    paper_id = str(paper_ledger.get("paper_id") or "")
    contract_sha = str(paper_ledger.get("contract_sha256") or "")
    if str(paper_ledger.get("current_state") or "") != "REBUTTAL":
        raise RuntimeError("final venue decision requires paper state REBUTTAL")
    submission = _receipt(paper_ledger, "actual-submission")
    rebuttal = _receipt(paper_ledger, "rebuttal-preparation")
    if not submission or not validate_submission_receipt(submission):
        raise RuntimeError("valid actual submission receipt required")
    if not rebuttal or rebuttal.get("pass") is not True or not validate_rebuttal_receipt(rebuttal):
        raise RuntimeError("valid rebuttal preparation receipt required")
    if rebuttal.get("submission_receipt_sha256") != submission.get("submission_receipt_sha256"):
        raise RuntimeError("rebuttal/submission lineage mismatch")
    decision = str(decision or "").strip().upper()
    if decision not in FINAL_DECISIONS:
        raise RuntimeError(f"unsupported final decision: {decision}")
    if not str(decision_id or "").strip() or not str(source_ref or "").strip() or not str(received_at or "").strip() or not str(decision_text or "").strip():
        raise RuntimeError("decision id, source, timestamp, and decision text are required")
    receipt: dict[str, Any] = {
        "schema_version": LEARN_SCHEMA_VERSION,
        "receipt_type": "venue-final-decision",
        "paper_id": paper_id,
        "contract_sha256": contract_sha,
        "submission_receipt_sha256": str(submission.get("submission_receipt_sha256") or ""),
        "rebuttal_receipt_sha256": str(rebuttal.get("rebuttal_receipt_sha256") or ""),
        "decision_id": str(decision_id).strip(),
        "source_ref": str(source_ref).strip(),
        "received_at": str(received_at).strip(),
        "decision": decision,
        "decision_text_sha256": hashlib.sha256(str(decision_text).encode()).hexdigest(),
        "scientific_claim_status_unchanged": True,
        "acceptance_does_not_prove_scientific_truth": True,
        "rejection_does_not_refute_scientific_claims": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["venue_decision_sha256"] = _digest(venue_decision_identity(receipt))
    return receipt


def validate_venue_decision_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "venue-final-decision" or receipt.get("decision") not in FINAL_DECISIONS:
        return False
    if receipt.get("scientific_claim_status_unchanged") is not True:
        return False
    if receipt.get("acceptance_does_not_prove_scientific_truth") is not True or receipt.get("rejection_does_not_refute_scientific_claims") is not True:
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("venue_decision_sha256") or "") == _digest(venue_decision_identity(receipt))


def learning_receipt_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "venue_decision_sha256": receipt.get("venue_decision_sha256"),
        "lessons_digest": receipt.get("lessons_digest"),
        "pass": receipt.get("pass"),
        "blockers": receipt.get("blockers") or [],
        "scientific_claim_status_unchanged": receipt.get("scientific_claim_status_unchanged"),
    }


def build_learning_packet(
    *,
    paper_ledger: Mapping[str, Any],
    venue_decision: Mapping[str, Any],
    lessons: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    blockers: list[str] = []
    paper_id = str(paper_ledger.get("paper_id") or "")
    contract_sha = str(paper_ledger.get("contract_sha256") or "")
    contract = paper_ledger.get("contract") or {}
    allowed_claims = set((contract.get("supported_claims") or {}).keys()) | set((contract.get("active_unrefuted_claims") or {}).keys()) | set((contract.get("unsupported_claims") or {}).keys())
    if str(paper_ledger.get("current_state") or "") != "REBUTTAL":
        blockers.append("learning-paper-not-in-rebuttal")
    if not validate_venue_decision_receipt(venue_decision):
        blockers.append("learning-venue-decision-invalid")
    if str(venue_decision.get("paper_id") or "") != paper_id or str(venue_decision.get("contract_sha256") or "") != contract_sha:
        blockers.append("learning-decision-paper-contract-mismatch")

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in lessons:
        lesson_id = str(source.get("lesson_id") or "").strip()
        category = str(source.get("category") or "").strip()
        scope = str(source.get("reuse_scope") or "").strip()
        statement = str(source.get("statement") or "").strip()
        basis_refs = [str(x) for x in source.get("basis_refs") or [] if str(x)]
        claim_ids = [str(x) for x in source.get("claim_ids") or [] if str(x)]
        if not lesson_id or lesson_id in seen:
            blockers.append("learning-lesson-id-invalid-or-duplicate")
            continue
        seen.add(lesson_id)
        if category not in LESSON_CATEGORIES:
            blockers.append(f"learning-category-invalid:{lesson_id}")
        if scope not in REUSE_SCOPES:
            blockers.append(f"learning-reuse-scope-invalid:{lesson_id}")
        if not statement:
            blockers.append(f"learning-statement-empty:{lesson_id}")
        if not basis_refs:
            blockers.append(f"learning-basis-missing:{lesson_id}")
        unknown_claims = sorted(set(claim_ids) - allowed_claims)
        if unknown_claims:
            blockers.append(f"learning-unknown-claim:{lesson_id}:" + ",".join(unknown_claims))
        if (category == "SCIENTIFIC_DIAGNOSTIC" or claim_ids) and scope != "SCIENTIFIC_DIAGNOSTIC_ONLY":
            blockers.append(f"learning-scientific-lesson-must-remain-diagnostic:{lesson_id}")
        rows.append({
            "lesson_id": lesson_id,
            "category": category,
            "reuse_scope": scope,
            "statement_sha256": hashlib.sha256(statement.encode()).hexdigest(),
            "basis_refs": basis_refs,
            "claim_ids": claim_ids,
            "scientific_authority": False,
        })
    if not rows:
        blockers.append("learning-packet-empty")
    blockers = list(dict.fromkeys(blockers))
    receipt: dict[str, Any] = {
        "schema_version": LEARN_SCHEMA_VERSION,
        "receipt_type": "post-decision-learning",
        "paper_id": paper_id,
        "contract_sha256": contract_sha,
        "venue_decision_sha256": str(venue_decision.get("venue_decision_sha256") or ""),
        "decision": str(venue_decision.get("decision") or ""),
        "lessons_digest": _digest(rows),
        "lessons": rows,
        "pass": not blockers,
        "blockers": blockers,
        "summary": {
            "lessons": len(rows),
            "scientific_diagnostic_only": sum(row["reuse_scope"] == "SCIENTIFIC_DIAGNOSTIC_ONLY" for row in rows),
            "paper_process_lessons": sum(row["reuse_scope"] != "SCIENTIFIC_DIAGNOSTIC_ONLY" for row in rows),
        },
        "scientific_claim_status_unchanged": True,
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "automatic_reopen_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["learning_receipt_sha256"] = _digest(learning_receipt_identity(receipt))
    return receipt


def validate_learning_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "post-decision-learning":
        return False
    lessons = receipt.get("lessons") or []
    if not isinstance(lessons, list) or not lessons or str(receipt.get("lessons_digest") or "") != _digest(lessons):
        return False
    if receipt.get("scientific_claim_status_unchanged") is not True:
        return False
    if receipt.get("claim_expansion_authorized") is not False or receipt.get("new_experiment_authorized") is not False or receipt.get("automatic_reopen_authorized") is not False:
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("learning_receipt_sha256") or "") == _digest(learning_receipt_identity(receipt))
