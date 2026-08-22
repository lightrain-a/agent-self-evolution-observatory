from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from .post_decision_learning import FINAL_DECISIONS, LESSON_CATEGORIES, REUSE_SCOPES
from .rebuttal_protocol import EVIDENCE_STATES, RESOLUTION_ACTIONS
from .submission_attempt_workflow import validate_attempt_actual_submission

SCHEMA_VERSION = "1.0"
DECISION_PHASES = {"POST_REBUTTAL", "PRE_REBUTTAL_TERMINAL"}
ZERO_AUTHORITY = {"scientific": False, "experiment": False, "gpu": False, "submission": False}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def latest_receipt(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, Mapping) and event.get("event_type") == event_type:
            receipt = event.get("receipt") or {}
            return dict(receipt) if isinstance(receipt, Mapping) else {}
    return {}


def review_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"), "attempt_sha256": receipt.get("attempt_sha256"),
        "attempt_submission_receipt_sha256": receipt.get("attempt_submission_receipt_sha256"),
        "venue_submission_id": receipt.get("venue_submission_id"), "reviews": receipt.get("reviews") or [],
    }


def build_attempt_review_set(workflow_ledger: Mapping[str, Any], reviews: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    submission = latest_receipt(workflow_ledger, "attempt-actual-submission")
    if not submission or not validate_attempt_actual_submission(submission):
        raise RuntimeError("valid child-attempt actual submission receipt required before review intake")
    if str(submission.get("attempt_sha256") or "") != str(workflow_ledger.get("attempt_sha256") or ""):
        raise RuntimeError("child submission/workflow attempt mismatch")
    records: list[dict[str, Any]] = []
    public: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in reviews:
        rid = str(source.get("review_id") or "").strip(); text = str(source.get("text") or "").strip()
        source_ref = str(source.get("source_ref") or "").strip(); received_at = str(source.get("received_at") or "").strip()
        if not rid or rid in seen: raise RuntimeError("review ids must be nonempty and unique")
        if not text or not source_ref or not received_at: raise RuntimeError(f"review {rid} missing text/source/timestamp")
        seen.add(rid)
        row = {"review_id": rid, "source_ref": source_ref, "received_at": received_at, "text": text,
               "text_sha256": hashlib.sha256(text.encode()).hexdigest(), "rating": source.get("rating"),
               "confidence": source.get("confidence"), "supersedes_review_id": str(source.get("supersedes_review_id") or "")}
        records.append(row)
        public.append({key: row[key] for key in ("review_id", "source_ref", "received_at", "text_sha256", "rating", "confidence", "supersedes_review_id")})
    if not records: raise RuntimeError("review set is empty")
    ids = {row["review_id"] for row in records}
    for row in records:
        if row["supersedes_review_id"] and row["supersedes_review_id"] not in ids:
            raise RuntimeError(f"review {row['review_id']} supersedes unknown review {row['supersedes_review_id']}")
    receipt: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "receipt_type": "attempt-review-set",
        "paper_id": str(workflow_ledger.get("paper_id") or ""), "attempt_id": str(workflow_ledger.get("attempt_id") or ""),
        "attempt_sha256": str(workflow_ledger.get("attempt_sha256") or ""),
        "attempt_submission_receipt_sha256": str(submission.get("attempt_submission_receipt_sha256") or ""),
        "venue_submission_id": str(submission.get("venue_submission_id") or ""), "reviews": public,
        "review_records": records, "review_count": len(records), "status": "ATTEMPT_VENUE_REVIEWS_RECORDED", **ZERO_AUTHORITY}
    receipt["attempt_review_set_sha256"] = digest(review_identity(receipt)); return receipt


def validate_attempt_review_set(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "attempt-review-set" or receipt.get("status") != "ATTEMPT_VENUE_REVIEWS_RECORDED": return False
    records = receipt.get("review_records") or []; public = receipt.get("reviews") or []
    if not isinstance(records, list) or not records or len(records) != len(public) or int(receipt.get("review_count") or 0) != len(records): return False
    for record, public_row in zip(records, public):
        if not isinstance(record, Mapping) or not isinstance(public_row, Mapping): return False
        text = str(record.get("text") or "")
        if not text or hashlib.sha256(text.encode()).hexdigest() != str(record.get("text_sha256") or ""): return False
        expected = {key: record.get(key) for key in ("review_id", "source_ref", "received_at", "text_sha256", "rating", "confidence", "supersedes_review_id")}
        if dict(public_row) != expected: return False
    return not any(receipt.get(key) is True for key in ZERO_AUTHORITY) and str(receipt.get("attempt_review_set_sha256") or "") == digest(review_identity(receipt))


def rebuttal_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in ("paper_id", "contract_sha256", "attempt_sha256", "attempt_submission_receipt_sha256",
        "attempt_review_set_sha256", "objection_digest", "resolution_digest", "response_sha256", "response_limit_words", "response_words", "pass")} | {"blockers": receipt.get("blockers") or []}


def build_attempt_rebuttal_preparation(*, paper_ledger: Mapping[str, Any], workflow_ledger: Mapping[str, Any], review_set: Mapping[str, Any],
        objections: Sequence[Mapping[str, Any]], resolutions: Sequence[Mapping[str, Any]], response_text: str, response_limit_words: int) -> dict[str, Any]:
    contract = paper_ledger.get("contract") or {}; contract_sha = str(paper_ledger.get("contract_sha256") or ""); paper_id = str(paper_ledger.get("paper_id") or "")
    submission = latest_receipt(workflow_ledger, "attempt-actual-submission"); blockers: list[str] = []
    if str(workflow_ledger.get("paper_id") or "") != paper_id or not contract_sha: blockers.append("attempt-rebuttal-paper-contract-mismatch")
    if not submission or not validate_attempt_actual_submission(submission): blockers.append("attempt-rebuttal-valid-submission-required")
    if not validate_attempt_review_set(review_set): blockers.append("attempt-rebuttal-review-set-invalid")
    if review_set.get("attempt_sha256") != workflow_ledger.get("attempt_sha256"): blockers.append("attempt-rebuttal-review-set-attempt-mismatch")
    if submission and review_set.get("attempt_submission_receipt_sha256") != submission.get("attempt_submission_receipt_sha256"): blockers.append("attempt-rebuttal-review-submission-mismatch")
    review_ids = {str(row.get("review_id") or "") for row in review_set.get("reviews") or []}
    allowed_claims = set((contract.get("supported_claims") or {}).keys()) | set((contract.get("active_unrefuted_claims") or {}).keys())
    allowed_evidence = set(str(x) for x in contract.get("evidence_refs") or [])
    obs: list[dict[str, Any]] = []; obs_ids: set[str] = set()
    for source in objections:
        oid = str(source.get("objection_id") or "").strip(); state = str(source.get("evidence_state") or "").strip()
        refs = [str(x) for x in source.get("review_ids") or []]; claim_ids = [str(x) for x in source.get("claim_ids") or []]
        if not oid or oid in obs_ids: blockers.append("attempt-rebuttal-objection-id-invalid-or-duplicate"); continue
        obs_ids.add(oid)
        if state not in EVIDENCE_STATES: blockers.append(f"attempt-rebuttal-objection-evidence-state-invalid:{oid}")
        if not refs or any(ref not in review_ids for ref in refs): blockers.append(f"attempt-rebuttal-objection-review-lineage-invalid:{oid}")
        if set(claim_ids) - allowed_claims: blockers.append(f"attempt-rebuttal-objection-unknown-claims:{oid}")
        obs.append({"objection_id": oid, "review_ids": refs, "category": str(source.get("category") or "other"),
                    "summary": str(source.get("summary") or "").strip(), "decision_critical": source.get("decision_critical") is True,
                    "evidence_state": state, "claim_ids": claim_ids})
    if not obs: blockers.append("attempt-rebuttal-no-objections")
    res_by: dict[str, dict[str, Any]] = {}; res: list[dict[str, Any]] = []
    for source in resolutions:
        oid = str(source.get("objection_id") or "").strip(); action = str(source.get("action") or "").strip(); segment = str(source.get("response_segment") or "").strip()
        refs = [str(x) for x in source.get("evidence_refs") or []]
        if not oid or oid in res_by or oid not in obs_ids: blockers.append("attempt-rebuttal-resolution-objection-invalid-or-duplicate"); continue
        if action not in RESOLUTION_ACTIONS: blockers.append(f"attempt-rebuttal-resolution-action-invalid:{oid}")
        if not segment: blockers.append(f"attempt-rebuttal-resolution-response-empty:{oid}")
        row = {"objection_id": oid, "action": action, "response_segment": segment, "evidence_refs": refs}; res_by[oid] = row; res.append(row)
    for objection in obs:
        oid = objection["objection_id"]; state = objection["evidence_state"]; resolution = res_by.get(oid)
        if objection["decision_critical"] and resolution is None: blockers.append(f"attempt-rebuttal-critical-objection-unresolved:{oid}"); continue
        if resolution is None: continue
        action = resolution["action"]; refs = set(resolution["evidence_refs"])
        if action in {"ANSWER_WITH_EXISTING_EVIDENCE", "CORRECT_FALSE_PREMISE"}:
            if not refs: blockers.append(f"attempt-rebuttal-existing-evidence-response-missing-refs:{oid}")
            if refs - allowed_evidence: blockers.append(f"attempt-rebuttal-response-uses-unfrozen-evidence:{oid}")
        if state == "EXISTING_EVIDENCE" and action not in {"ANSWER_WITH_EXISTING_EVIDENCE", "CLARIFY_SCOPE"}: blockers.append(f"attempt-rebuttal-existing-evidence-action-mismatch:{oid}")
        if state == "CLARIFICATION_ONLY" and action != "CLARIFY_SCOPE": blockers.append(f"attempt-rebuttal-clarification-action-mismatch:{oid}")
        if state == "FALSE_PREMISE_WITH_EVIDENCE" and action != "CORRECT_FALSE_PREMISE": blockers.append(f"attempt-rebuttal-false-premise-action-mismatch:{oid}")
        if state == "MISSING_DECISIVE_EVIDENCE" and action not in {"PRESERVE_LIMITATION", "REQUEST_HUMAN_ADJUDICATION"}: blockers.append(f"attempt-rebuttal-missing-evidence-cannot-be-papered-over:{oid}")
        if state == "REQUIRES_NEW_CLAIM" and action != "PRESERVE_LIMITATION": blockers.append(f"attempt-rebuttal-new-claim-request-must-preserve-scope:{oid}")
        if state == "UNCERTAIN" and action != "REQUEST_HUMAN_ADJUDICATION": blockers.append(f"attempt-rebuttal-uncertain-objection-requires-human:{oid}")
        if resolution["response_segment"] not in response_text: blockers.append(f"attempt-rebuttal-response-segment-not-in-final-response:{oid}")
    words = len(response_text.split())
    if response_limit_words <= 0: blockers.append("attempt-rebuttal-response-limit-invalid")
    if not response_text.strip(): blockers.append("attempt-rebuttal-response-empty")
    if response_limit_words > 0 and words > response_limit_words: blockers.append("attempt-rebuttal-response-over-budget")
    blockers = list(dict.fromkeys(blockers))
    obs_public = [{k: row[k] for k in ("objection_id", "review_ids", "category", "decision_critical", "evidence_state", "claim_ids")} for row in obs]
    res_public = [{"objection_id": row["objection_id"], "action": row["action"], "evidence_refs": row["evidence_refs"], "response_segment_sha256": hashlib.sha256(row["response_segment"].encode()).hexdigest()} for row in res]
    receipt: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "receipt_type": "attempt-rebuttal-preparation", "paper_id": paper_id, "contract_sha256": contract_sha,
        "attempt_id": str(workflow_ledger.get("attempt_id") or ""), "attempt_sha256": str(workflow_ledger.get("attempt_sha256") or ""),
        "attempt_submission_receipt_sha256": str(submission.get("attempt_submission_receipt_sha256") or ""), "attempt_review_set_sha256": str(review_set.get("attempt_review_set_sha256") or ""),
        "objection_digest": digest(obs_public), "resolution_digest": digest(res_public), "response_sha256": hashlib.sha256(response_text.encode()).hexdigest(),
        "response_limit_words": int(response_limit_words), "response_words": words, "pass": not blockers, "blockers": blockers,
        "summary": {"reviews": int(review_set.get("review_count") or 0), "objections": len(obs), "decision_critical": sum(row["decision_critical"] for row in obs),
                    "resolved": len(res), "missing_decisive_evidence": sum(row["evidence_state"] == "MISSING_DECISIVE_EVIDENCE" for row in obs),
                    "new_claim_requests": sum(row["evidence_state"] == "REQUIRES_NEW_CLAIM" for row in obs)},
        "claim_expansion_authorized": False, "new_experiment_authorized": False, **ZERO_AUTHORITY}
    receipt["attempt_rebuttal_receipt_sha256"] = digest(rebuttal_identity(receipt)); return receipt


def validate_attempt_rebuttal_preparation(receipt: Mapping[str, Any]) -> bool:
    return receipt.get("receipt_type") == "attempt-rebuttal-preparation" and receipt.get("claim_expansion_authorized") is False and receipt.get("new_experiment_authorized") is False and not any(receipt.get(k) is True for k in ZERO_AUTHORITY) and str(receipt.get("attempt_rebuttal_receipt_sha256") or "") == digest(rebuttal_identity(receipt))

def decision_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in ("paper_id", "contract_sha256", "attempt_sha256", "attempt_submission_receipt_sha256",
        "attempt_rebuttal_receipt_sha256", "decision_phase", "rebuttal_available", "decision_id", "source_ref", "received_at", "decision",
        "decision_text_sha256", "scientific_claim_status_unchanged")}


def build_attempt_venue_decision(*, paper_ledger: Mapping[str, Any], workflow_ledger: Mapping[str, Any], decision_id: str,
        source_ref: str, received_at: str, decision: str, decision_text: str, decision_phase: str = "POST_REBUTTAL", rebuttal_available: bool = True) -> dict[str, Any]:
    submission = latest_receipt(workflow_ledger, "attempt-actual-submission"); rebuttal = latest_receipt(workflow_ledger, "attempt-rebuttal-preparation")
    phase = str(decision_phase or "").strip().upper(); decision = str(decision or "").strip().upper()
    if not submission or not validate_attempt_actual_submission(submission): raise RuntimeError("valid child-attempt submission required")
    if phase not in DECISION_PHASES: raise RuntimeError(f"unsupported decision phase: {phase}")
    if decision not in FINAL_DECISIONS: raise RuntimeError(f"unsupported final decision: {decision}")
    if phase == "POST_REBUTTAL":
        if rebuttal_available is not True: raise RuntimeError("post-rebuttal decision must declare rebuttal_available=true")
        if not rebuttal or rebuttal.get("pass") is not True or not validate_attempt_rebuttal_preparation(rebuttal): raise RuntimeError("valid child rebuttal preparation receipt required")
        if rebuttal.get("attempt_submission_receipt_sha256") != submission.get("attempt_submission_receipt_sha256"): raise RuntimeError("child rebuttal/submission lineage mismatch")
    else:
        if rebuttal_available is not False: raise RuntimeError("pre-rebuttal terminal decision must declare rebuttal_available=false")
        rebuttal = {}
    if not str(decision_id or "").strip() or not str(source_ref or "").strip() or not str(received_at or "").strip() or not str(decision_text or "").strip():
        raise RuntimeError("decision id, source, timestamp, and decision text are required")
    receipt: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "receipt_type": "attempt-venue-final-decision",
        "paper_id": str(paper_ledger.get("paper_id") or ""), "contract_sha256": str(paper_ledger.get("contract_sha256") or ""),
        "attempt_id": str(workflow_ledger.get("attempt_id") or ""), "attempt_sha256": str(workflow_ledger.get("attempt_sha256") or ""),
        "attempt_submission_receipt_sha256": str(submission.get("attempt_submission_receipt_sha256") or ""),
        "attempt_rebuttal_receipt_sha256": str(rebuttal.get("attempt_rebuttal_receipt_sha256") or ""), "decision_phase": phase,
        "rebuttal_available": bool(rebuttal_available), "decision_id": str(decision_id).strip(), "source_ref": str(source_ref).strip(),
        "received_at": str(received_at).strip(), "decision": decision, "decision_text_sha256": hashlib.sha256(str(decision_text).encode()).hexdigest(),
        "scientific_claim_status_unchanged": True, "acceptance_does_not_prove_scientific_truth": True,
        "rejection_does_not_refute_scientific_claims": True, **ZERO_AUTHORITY}
    receipt["attempt_venue_decision_sha256"] = digest(decision_identity(receipt)); return receipt


def validate_attempt_venue_decision(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "attempt-venue-final-decision" or receipt.get("decision") not in FINAL_DECISIONS: return False
    phase = str(receipt.get("decision_phase") or "")
    if phase not in DECISION_PHASES: return False
    if phase == "POST_REBUTTAL":
        if receipt.get("rebuttal_available") is not True or not receipt.get("attempt_rebuttal_receipt_sha256"): return False
    elif receipt.get("rebuttal_available") is not False or receipt.get("attempt_rebuttal_receipt_sha256"): return False
    if receipt.get("scientific_claim_status_unchanged") is not True or receipt.get("acceptance_does_not_prove_scientific_truth") is not True or receipt.get("rejection_does_not_refute_scientific_claims") is not True: return False
    return not any(receipt.get(k) is True for k in ZERO_AUTHORITY) and str(receipt.get("attempt_venue_decision_sha256") or "") == digest(decision_identity(receipt))


def skip_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in ("paper_id", "attempt_sha256", "attempt_submission_receipt_sha256", "attempt_venue_decision_sha256", "status", "pass", "scientific_claim_status_unchanged")}


def build_attempt_rebuttal_skipped_by_venue(*, workflow_ledger: Mapping[str, Any], venue_decision: Mapping[str, Any]) -> dict[str, Any]:
    submission = latest_receipt(workflow_ledger, "attempt-actual-submission")
    if not submission or not validate_attempt_actual_submission(submission): raise RuntimeError("valid child submission required")
    if not validate_attempt_venue_decision(venue_decision) or venue_decision.get("decision_phase") != "PRE_REBUTTAL_TERMINAL" or venue_decision.get("rebuttal_available") is not False:
        raise RuntimeError("valid pre-rebuttal child terminal decision required")
    if venue_decision.get("attempt_submission_receipt_sha256") != submission.get("attempt_submission_receipt_sha256"): raise RuntimeError("child skip decision/submission lineage mismatch")
    receipt: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "receipt_type": "attempt-rebuttal-skipped-by-venue",
        "paper_id": str(workflow_ledger.get("paper_id") or ""), "attempt_id": str(workflow_ledger.get("attempt_id") or ""),
        "attempt_sha256": str(workflow_ledger.get("attempt_sha256") or ""), "attempt_submission_receipt_sha256": str(submission.get("attempt_submission_receipt_sha256") or ""),
        "attempt_venue_decision_sha256": str(venue_decision.get("attempt_venue_decision_sha256") or ""), "status": "ATTEMPT_REBUTTAL_SKIPPED_BY_VENUE", "pass": True,
        "scientific_claim_status_unchanged": True, "review_fabrication_forbidden": True, "claim_expansion_authorized": False, "new_experiment_authorized": False, **ZERO_AUTHORITY}
    receipt["attempt_rebuttal_skip_sha256"] = digest(skip_identity(receipt)); return receipt


def validate_attempt_rebuttal_skipped(receipt: Mapping[str, Any]) -> bool:
    return receipt.get("receipt_type") == "attempt-rebuttal-skipped-by-venue" and receipt.get("status") == "ATTEMPT_REBUTTAL_SKIPPED_BY_VENUE" and receipt.get("pass") is True and receipt.get("scientific_claim_status_unchanged") is True and receipt.get("review_fabrication_forbidden") is True and receipt.get("claim_expansion_authorized") is False and receipt.get("new_experiment_authorized") is False and not any(receipt.get(k) is True for k in ZERO_AUTHORITY) and str(receipt.get("attempt_rebuttal_skip_sha256") or "") == digest(skip_identity(receipt))


def learning_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in ("paper_id", "contract_sha256", "attempt_sha256", "attempt_venue_decision_sha256", "lessons_digest", "pass", "scientific_claim_status_unchanged")} | {"blockers": receipt.get("blockers") or []}


def build_attempt_learning_packet(*, paper_ledger: Mapping[str, Any], workflow_ledger: Mapping[str, Any], venue_decision: Mapping[str, Any], lessons: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    contract = paper_ledger.get("contract") or {}; allowed_claims = set((contract.get("supported_claims") or {}).keys()) | set((contract.get("active_unrefuted_claims") or {}).keys()) | set((contract.get("unsupported_claims") or {}).keys())
    blockers: list[str] = []
    if not validate_attempt_venue_decision(venue_decision): blockers.append("attempt-learning-venue-decision-invalid")
    if venue_decision.get("attempt_sha256") != workflow_ledger.get("attempt_sha256"): blockers.append("attempt-learning-decision-attempt-mismatch")
    rows: list[dict[str, Any]] = []; seen: set[str] = set()
    for source in lessons:
        lid = str(source.get("lesson_id") or "").strip(); category = str(source.get("category") or "").strip(); scope = str(source.get("reuse_scope") or "").strip(); statement = str(source.get("statement") or "").strip()
        basis = [str(x) for x in source.get("basis_refs") or [] if str(x)]; claims = [str(x) for x in source.get("claim_ids") or [] if str(x)]
        if not lid or lid in seen: blockers.append("attempt-learning-lesson-id-invalid-or-duplicate"); continue
        seen.add(lid)
        if category not in LESSON_CATEGORIES: blockers.append(f"attempt-learning-category-invalid:{lid}")
        if scope not in REUSE_SCOPES: blockers.append(f"attempt-learning-reuse-scope-invalid:{lid}")
        if not statement: blockers.append(f"attempt-learning-statement-empty:{lid}")
        if not basis: blockers.append(f"attempt-learning-basis-missing:{lid}")
        if set(claims) - allowed_claims: blockers.append(f"attempt-learning-unknown-claim:{lid}")
        if (category == "SCIENTIFIC_DIAGNOSTIC" or claims) and scope != "SCIENTIFIC_DIAGNOSTIC_ONLY": blockers.append(f"attempt-learning-scientific-lesson-must-remain-diagnostic:{lid}")
        rows.append({"lesson_id": lid, "category": category, "reuse_scope": scope, "statement_sha256": hashlib.sha256(statement.encode()).hexdigest(), "basis_refs": basis, "claim_ids": claims, "scientific_authority": False})
    if not rows: blockers.append("attempt-learning-packet-empty")
    blockers = list(dict.fromkeys(blockers))
    receipt: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "receipt_type": "attempt-post-decision-learning",
        "paper_id": str(paper_ledger.get("paper_id") or ""), "contract_sha256": str(paper_ledger.get("contract_sha256") or ""),
        "attempt_id": str(workflow_ledger.get("attempt_id") or ""), "attempt_sha256": str(workflow_ledger.get("attempt_sha256") or ""),
        "attempt_venue_decision_sha256": str(venue_decision.get("attempt_venue_decision_sha256") or ""), "decision": str(venue_decision.get("decision") or ""),
        "lessons_digest": digest(rows), "lessons": rows, "pass": not blockers, "blockers": blockers,
        "summary": {"lessons": len(rows), "scientific_diagnostic_only": sum(row["reuse_scope"] == "SCIENTIFIC_DIAGNOSTIC_ONLY" for row in rows), "paper_process_lessons": sum(row["reuse_scope"] != "SCIENTIFIC_DIAGNOSTIC_ONLY" for row in rows)},
        "scientific_claim_status_unchanged": True, "claim_expansion_authorized": False, "new_experiment_authorized": False, "automatic_reopen_authorized": False, **ZERO_AUTHORITY}
    receipt["attempt_learning_receipt_sha256"] = digest(learning_identity(receipt)); return receipt


def validate_attempt_learning_packet(receipt: Mapping[str, Any]) -> bool:
    lessons = receipt.get("lessons") or []
    return receipt.get("receipt_type") == "attempt-post-decision-learning" and isinstance(lessons, list) and bool(lessons) and str(receipt.get("lessons_digest") or "") == digest(lessons) and receipt.get("scientific_claim_status_unchanged") is True and receipt.get("claim_expansion_authorized") is False and receipt.get("new_experiment_authorized") is False and receipt.get("automatic_reopen_authorized") is False and not any(receipt.get(k) is True for k in ZERO_AUTHORITY) and str(receipt.get("attempt_learning_receipt_sha256") or "") == digest(learning_identity(receipt))
