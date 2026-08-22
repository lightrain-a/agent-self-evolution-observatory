from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

REBUTTAL_SCHEMA_VERSION = "1.0"
AUTHORITY = {"scientific": False, "experiment": False, "gpu": False, "submission": False}

EVIDENCE_STATES = {
    "EXISTING_EVIDENCE",
    "CLARIFICATION_ONLY",
    "FALSE_PREMISE_WITH_EVIDENCE",
    "MISSING_DECISIVE_EVIDENCE",
    "REQUIRES_NEW_CLAIM",
    "UNCERTAIN",
}
RESOLUTION_ACTIONS = {
    "ANSWER_WITH_EXISTING_EVIDENCE",
    "CLARIFY_SCOPE",
    "CORRECT_FALSE_PREMISE",
    "PRESERVE_LIMITATION",
    "REQUEST_HUMAN_ADJUDICATION",
}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _latest(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, Mapping) and event.get("event_type") == event_type:
            return dict(event)
    return {}


def _actual_submission_receipt(paper_ledger: Mapping[str, Any]) -> dict[str, Any]:
    event = _latest(paper_ledger, "actual-submission")
    receipt = event.get("receipt") or {}
    return dict(receipt) if isinstance(receipt, Mapping) else {}


def build_review_set(paper_ledger: Mapping[str, Any], reviews: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    from .venue_submission_receipt import validate_submission_receipt

    paper_id = str(paper_ledger.get("paper_id") or "")
    if str(paper_ledger.get("current_state") or "") != "SUBMITTED":
        raise RuntimeError("review intake requires a receipt-bound SUBMITTED paper")
    submission = _actual_submission_receipt(paper_ledger)
    if not submission or not validate_submission_receipt(submission):
        raise RuntimeError("valid actual venue submission receipt required before review intake")
    if str(submission.get("paper_id") or "") != paper_id:
        raise RuntimeError("submission/paper identity mismatch")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in reviews:
        review_id = str(source.get("review_id") or "").strip()
        text = str(source.get("text") or "").strip()
        source_ref = str(source.get("source_ref") or "").strip()
        received_at = str(source.get("received_at") or "").strip()
        if not review_id or review_id in seen:
            raise RuntimeError("review ids must be nonempty and unique")
        if not text or not source_ref or not received_at:
            raise RuntimeError(f"review {review_id} missing text/source/timestamp")
        seen.add(review_id)
        rows.append({
            "review_id": review_id,
            "source_ref": source_ref,
            "received_at": received_at,
            "text": text,
            "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "rating": source.get("rating"),
            "confidence": source.get("confidence"),
            "supersedes_review_id": str(source.get("supersedes_review_id") or ""),
        })
    if not rows:
        raise RuntimeError("review set is empty")
    ids = {row["review_id"] for row in rows}
    for row in rows:
        supersedes = row["supersedes_review_id"]
        if supersedes and supersedes not in ids:
            raise RuntimeError(f"review {row['review_id']} supersedes unknown review {supersedes}")
    identity = {
        "paper_id": paper_id,
        "contract_sha256": str(paper_ledger.get("contract_sha256") or ""),
        "submission_receipt_sha256": str(submission.get("submission_receipt_sha256") or ""),
        "venue_submission_id": str(submission.get("venue_submission_id") or ""),
        "reviews": [{k: row[k] for k in ("review_id", "source_ref", "received_at", "text_sha256", "rating", "confidence", "supersedes_review_id")} for row in rows],
    }
    return {
        "schema_version": REBUTTAL_SCHEMA_VERSION,
        "artifact_type": "venue-review-set",
        **identity,
        "review_set_sha256": _digest(identity),
        "review_count": len(rows),
        "review_records": rows,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def validate_review_set(review_set: Mapping[str, Any]) -> bool:
    if review_set.get("artifact_type") != "venue-review-set":
        return False
    rows = review_set.get("review_records") or []
    public_rows = review_set.get("reviews") or []
    if len(rows) != len(public_rows) or int(review_set.get("review_count") or 0) != len(rows) or not rows:
        return False
    identity = {
        "paper_id": review_set.get("paper_id"),
        "contract_sha256": review_set.get("contract_sha256"),
        "submission_receipt_sha256": review_set.get("submission_receipt_sha256"),
        "venue_submission_id": review_set.get("venue_submission_id"),
        "reviews": public_rows,
    }
    return str(review_set.get("review_set_sha256") or "") == _digest(identity)


def append_review_set(root: Path, review_set: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_review_set(review_set):
        raise RuntimeError("invalid review set")
    paper_id = str(review_set.get("paper_id") or "")
    directory = Path(root) / "paper-review-intake"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{paper_id}.json"
    lock = directory / f".{paper_id}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "schema_version": REBUTTAL_SCHEMA_VERSION,
            "paper_id": paper_id,
            "events": [],
            "authority": dict(AUTHORITY),
        }
        prior = _latest(row, "review-set")
        prior_set = prior.get("review_set") if isinstance(prior.get("review_set"), Mapping) else {}
        if prior_set.get("review_set_sha256") == review_set.get("review_set_sha256"):
            return row
        event = {
            "event_type": "review-set",
            "review_set": dict(review_set),
            "recorded_at": max((str(r.get("received_at") or "") for r in review_set.get("review_records") or []), default=""),
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        event["event_id"] = _digest([paper_id, len(row.get("events") or []), review_set.get("review_set_sha256")])[:24]
        row.setdefault("events", []).append(event)
        row["updated_at"] = event["recorded_at"]
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return row


def rebuttal_receipt_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "submission_receipt_sha256": receipt.get("submission_receipt_sha256"),
        "review_set_sha256": receipt.get("review_set_sha256"),
        "objection_digest": receipt.get("objection_digest"),
        "resolution_digest": receipt.get("resolution_digest"),
        "response_sha256": receipt.get("response_sha256"),
        "response_limit_words": receipt.get("response_limit_words"),
        "response_words": receipt.get("response_words"),
        "pass": receipt.get("pass"),
        "blockers": receipt.get("blockers") or [],
    }


def build_rebuttal_preparation(
    *,
    paper_ledger: Mapping[str, Any],
    review_set: Mapping[str, Any],
    objections: Sequence[Mapping[str, Any]],
    resolutions: Sequence[Mapping[str, Any]],
    response_text: str,
    response_limit_words: int,
) -> dict[str, Any]:
    from .venue_submission_receipt import validate_submission_receipt

    paper_id = str(paper_ledger.get("paper_id") or "")
    contract = paper_ledger.get("contract") or {}
    contract_sha = str(paper_ledger.get("contract_sha256") or "")
    submission = _actual_submission_receipt(paper_ledger)
    blockers: list[str] = []
    if str(paper_ledger.get("current_state") or "") != "SUBMITTED":
        blockers.append("rebuttal-paper-not-submitted")
    if not submission or not validate_submission_receipt(submission):
        blockers.append("rebuttal-valid-submission-receipt-required")
    if not validate_review_set(review_set):
        blockers.append("rebuttal-review-set-invalid")
    if str(review_set.get("paper_id") or "") != paper_id or str(review_set.get("contract_sha256") or "") != contract_sha:
        blockers.append("rebuttal-review-set-paper-contract-mismatch")
    if submission and review_set.get("submission_receipt_sha256") != submission.get("submission_receipt_sha256"):
        blockers.append("rebuttal-review-set-submission-mismatch")

    review_ids = {str(row.get("review_id") or "") for row in review_set.get("reviews") or []}
    allowed_claims = set((contract.get("supported_claims") or {}).keys()) | set((contract.get("active_unrefuted_claims") or {}).keys())
    allowed_evidence = set(str(x) for x in contract.get("evidence_refs") or [])
    objection_rows: list[dict[str, Any]] = []
    objection_ids: set[str] = set()
    for source in objections:
        oid = str(source.get("objection_id") or "").strip()
        state = str(source.get("evidence_state") or "").strip()
        refs = [str(x) for x in source.get("review_ids") or []]
        claim_ids = [str(x) for x in source.get("claim_ids") or []]
        if not oid or oid in objection_ids:
            blockers.append("rebuttal-objection-id-invalid-or-duplicate")
            continue
        objection_ids.add(oid)
        if state not in EVIDENCE_STATES:
            blockers.append(f"rebuttal-objection-evidence-state-invalid:{oid}")
        if not refs or any(ref not in review_ids for ref in refs):
            blockers.append(f"rebuttal-objection-review-lineage-invalid:{oid}")
        unknown_claims = sorted(set(claim_ids) - allowed_claims)
        if unknown_claims:
            blockers.append(f"rebuttal-objection-unknown-claims:{oid}:" + ",".join(unknown_claims))
        objection_rows.append({
            "objection_id": oid,
            "review_ids": refs,
            "category": str(source.get("category") or "other"),
            "summary": str(source.get("summary") or "").strip(),
            "decision_critical": source.get("decision_critical") is True,
            "evidence_state": state,
            "claim_ids": claim_ids,
        })
    if not objection_rows:
        blockers.append("rebuttal-no-objections")

    resolutions_by_id: dict[str, dict[str, Any]] = {}
    resolution_rows: list[dict[str, Any]] = []
    for source in resolutions:
        oid = str(source.get("objection_id") or "").strip()
        action = str(source.get("action") or "").strip()
        segment = str(source.get("response_segment") or "").strip()
        evidence_refs = [str(x) for x in source.get("evidence_refs") or []]
        if not oid or oid in resolutions_by_id or oid not in objection_ids:
            blockers.append("rebuttal-resolution-objection-invalid-or-duplicate")
            continue
        if action not in RESOLUTION_ACTIONS:
            blockers.append(f"rebuttal-resolution-action-invalid:{oid}")
        if not segment:
            blockers.append(f"rebuttal-resolution-response-empty:{oid}")
        row = {"objection_id": oid, "action": action, "response_segment": segment, "evidence_refs": evidence_refs}
        resolutions_by_id[oid] = row
        resolution_rows.append(row)

    for objection in objection_rows:
        oid = objection["objection_id"]
        state = objection["evidence_state"]
        resolution = resolutions_by_id.get(oid)
        if objection["decision_critical"] and resolution is None:
            blockers.append(f"rebuttal-critical-objection-unresolved:{oid}")
            continue
        if resolution is None:
            continue
        action = resolution["action"]
        refs = set(resolution["evidence_refs"])
        if action in {"ANSWER_WITH_EXISTING_EVIDENCE", "CORRECT_FALSE_PREMISE"}:
            if not refs:
                blockers.append(f"rebuttal-existing-evidence-response-missing-refs:{oid}")
            unknown_refs = sorted(refs - allowed_evidence)
            if unknown_refs:
                blockers.append(f"rebuttal-response-uses-unfrozen-evidence:{oid}")
        if state == "EXISTING_EVIDENCE" and action not in {"ANSWER_WITH_EXISTING_EVIDENCE", "CLARIFY_SCOPE"}:
            blockers.append(f"rebuttal-existing-evidence-action-mismatch:{oid}")
        if state == "CLARIFICATION_ONLY" and action != "CLARIFY_SCOPE":
            blockers.append(f"rebuttal-clarification-action-mismatch:{oid}")
        if state == "FALSE_PREMISE_WITH_EVIDENCE" and action != "CORRECT_FALSE_PREMISE":
            blockers.append(f"rebuttal-false-premise-action-mismatch:{oid}")
        if state == "MISSING_DECISIVE_EVIDENCE" and action not in {"PRESERVE_LIMITATION", "REQUEST_HUMAN_ADJUDICATION"}:
            blockers.append(f"rebuttal-missing-evidence-cannot-be-papered-over:{oid}")
        if state == "REQUIRES_NEW_CLAIM" and action != "PRESERVE_LIMITATION":
            blockers.append(f"rebuttal-new-claim-request-must-preserve-scope:{oid}")
        if state == "UNCERTAIN" and action != "REQUEST_HUMAN_ADJUDICATION":
            blockers.append(f"rebuttal-uncertain-objection-requires-human:{oid}")
        if resolution["response_segment"] not in response_text:
            blockers.append(f"rebuttal-response-segment-not-in-final-response:{oid}")

    if response_limit_words <= 0:
        blockers.append("rebuttal-response-limit-invalid")
    words = len(response_text.split())
    if not response_text.strip():
        blockers.append("rebuttal-response-empty")
    if response_limit_words > 0 and words > response_limit_words:
        blockers.append("rebuttal-response-over-budget")

    blockers = list(dict.fromkeys(blockers))
    objection_public = [{k: row[k] for k in ("objection_id", "review_ids", "category", "decision_critical", "evidence_state", "claim_ids")} for row in objection_rows]
    resolution_public = [{"objection_id": row["objection_id"], "action": row["action"], "evidence_refs": row["evidence_refs"], "response_segment_sha256": hashlib.sha256(row["response_segment"].encode()).hexdigest()} for row in resolution_rows]
    receipt: dict[str, Any] = {
        "schema_version": REBUTTAL_SCHEMA_VERSION,
        "receipt_type": "rebuttal-preparation",
        "paper_id": paper_id,
        "contract_sha256": contract_sha,
        "submission_receipt_sha256": str(submission.get("submission_receipt_sha256") or ""),
        "review_set_sha256": str(review_set.get("review_set_sha256") or ""),
        "objection_digest": _digest(objection_public),
        "resolution_digest": _digest(resolution_public),
        "response_sha256": hashlib.sha256(response_text.encode()).hexdigest(),
        "response_limit_words": int(response_limit_words),
        "response_words": words,
        "pass": not blockers,
        "blockers": blockers,
        "summary": {
            "reviews": int(review_set.get("review_count") or 0),
            "objections": len(objection_rows),
            "decision_critical": sum(row["decision_critical"] for row in objection_rows),
            "resolved": len(resolution_rows),
            "missing_decisive_evidence": sum(row["evidence_state"] == "MISSING_DECISIVE_EVIDENCE" for row in objection_rows),
            "new_claim_requests": sum(row["evidence_state"] == "REQUIRES_NEW_CLAIM" for row in objection_rows),
        },
        "claim_expansion_authorized": False,
        "new_experiment_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["rebuttal_receipt_sha256"] = _digest(rebuttal_receipt_identity(receipt))
    return receipt


def validate_rebuttal_receipt(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("receipt_type") != "rebuttal-preparation":
        return False
    if receipt.get("claim_expansion_authorized") is not False or receipt.get("new_experiment_authorized") is not False:
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("rebuttal_receipt_sha256") or "") == _digest(rebuttal_receipt_identity(receipt))
