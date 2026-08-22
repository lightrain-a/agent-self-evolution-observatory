from __future__ import annotations

import fcntl, hashlib, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .paper_acceptance import (
    MockReviewMode, PAPER_ACCEPTANCE_FLOW, PaperContract, PaperState, PrebuttalResolution,
    ReviewerObjection, StoryCandidate, build_claim_audit_receipt, build_mock_review_receipt,
    build_story_search_receipt, build_submission_readiness_receipt, evaluate_manuscript_ci,
    evaluate_paper_transition, evaluate_prebuttal, paper_contract_digest, paper_contract_payload,
)
from .paper_preparation_protocol import (
    build_paper_preparation_receipt,
    validate_paper_preparation_receipt,
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:140] or "unknown-paper"


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _paths(root: Path, paper_id: str) -> tuple[Path, Path]:
    directory = Path(root) / "paper-acceptance"
    directory.mkdir(parents=True, exist_ok=True)
    stem = _slug(paper_id)
    return directory / f"{stem}.json", directory / f".{stem}.lock"


def _atomic(path: Path, row: Mapping[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _refresh(row: dict[str, Any]) -> None:
    events = [event for event in row.get("events") or [] if isinstance(event, dict)]
    row["summary"] = {
        "events": len(events),
        "allowed_transitions": sum(event.get("event_type") == "paper-transition" and event.get("allowed") is True for event in events),
        "blocked_transitions": sum(event.get("event_type") == "paper-transition" and event.get("allowed") is False for event in events),
        "story_search_receipts": sum(event.get("event_type") == "story-search" for event in events),
        "mock_reviews": sum(event.get("event_type") == "mock-pc-review" for event in events),
        "claim_audit_receipts": sum(event.get("event_type") == "claim-audit" for event in events),
        "manuscript_ci_receipts": sum(event.get("event_type") == "manuscript-ci" for event in events),
        "prebuttal_receipts": sum(event.get("event_type") == "prebuttal" for event in events),
        "paper_preparation_receipts": sum(event.get("event_type") == "paper-preparation" for event in events),
        "submission_readiness_receipts": sum(event.get("event_type") == "submission-readiness" for event in events),
    }


def _new(contract: PaperContract, actor: str) -> dict[str, Any]:
    timestamp = _now()
    digest = paper_contract_digest(contract)
    row = {
        "schema_version": "1.0", "paper_id": contract.paper_id, "contract_sha256": digest,
        "contract": paper_contract_payload(contract), "current_state": PaperState.PAPER_EVIDENCE.value,
        "scientific_status": contract.scientific_status.value, "created_at": timestamp, "updated_at": timestamp,
        "events": [{"event_type": "paper-contract-registered", "event_id": _digest([contract.paper_id, digest, timestamp])[:24],
                    "actor": actor, "recorded_at": timestamp, "contract_sha256": digest, "scientific_authority": False}],
        "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
    }
    _refresh(row)
    return row


def load_paper_ledger(root: Path, paper_id: str) -> dict[str, Any]:
    path, _ = _paths(root, paper_id)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def initialize_paper_ledger(root: Path, contract: PaperContract, actor: str = "system") -> dict[str, Any]:
    path, lock = _paths(root, contract.paper_id)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        if path.exists():
            row = json.loads(path.read_text(encoding="utf-8"))
            if row.get("contract_sha256") != paper_contract_digest(contract):
                raise RuntimeError(f"paper contract digest mismatch for {contract.paper_id}")
            return row
        row = _new(contract, actor)
        _atomic(path, row)
        return row


def _latest(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, dict) and event.get("event_type") == event_type:
            return event
    return {}


def _stage_events(row: Mapping[str, Any], state: PaperState) -> list[dict[str, Any]]:
    events = [event for event in row.get("events") or [] if isinstance(event, dict)]
    start = -1
    for index, event in enumerate(events):
        if event.get("event_type") == "paper-transition" and event.get("allowed") is True and event.get("to") == state.value:
            start = index
    return events[start + 1:] if start >= 0 else []


def _receipt_hash_valid(receipt: Mapping[str, Any]) -> bool:
    receipt_type = str(receipt.get("receipt_type") or "")
    if receipt_type == "story-search":
        identity = {
            "paper_id": receipt.get("paper_id"),
            "contract_sha256": receipt.get("contract_sha256"),
            "candidate_set_sha256": receipt.get("candidate_set_sha256"),
            "selected_story_id": receipt.get("selected_story_id"),
            "selected_story_title": receipt.get("selected_story_title"),
            "valid_candidates": receipt.get("valid_candidates"),
            "winner_valid": receipt.get("winner_valid"),
            "claim_expansion_authorized": receipt.get("claim_expansion_authorized"),
        }
        return str(receipt.get("story_search_sha256") or "") == _digest(identity)
    if receipt_type == "mock-pc-review":
        identity = {
            "paper_id": receipt.get("paper_id"),
            "contract_sha256": receipt.get("contract_sha256"),
            "mode": receipt.get("mode"),
            "objections": receipt.get("objections") or [],
            "actions": receipt.get("actions") or [],
        }
        return str(receipt.get("review_sha256") or "") == _digest(identity)
    if receipt_type == "paper-preparation":
        return validate_paper_preparation_receipt(receipt)
    if receipt_type == "claim-audit":
        identity = {
            "paper_id": receipt.get("paper_id"),
            "contract_sha256": receipt.get("contract_sha256"),
            "manuscript_ref": receipt.get("manuscript_ref"),
            "claimed_ids": receipt.get("claimed_ids") or [],
            "evidence_bound_claim_ids": receipt.get("evidence_bound_claim_ids") or [],
            "unsupported_claim_ids_present": receipt.get("unsupported_claim_ids_present") or [],
            "limitations_preserved": receipt.get("limitations_preserved"),
            "pass": receipt.get("pass"),
            "blockers": receipt.get("blockers") or [],
        }
        return str(receipt.get("claim_audit_sha256") or "") == _digest(identity)
    return False


def _valid_stage_receipt(event: Mapping[str, Any], receipt_type: str, contract_sha256: str) -> dict[str, Any]:
    if event.get("event_type") != receipt_type:
        return {}
    receipt = event.get("receipt") or {}
    if not isinstance(receipt, dict):
        return {}
    if str(receipt.get("contract_sha256") or "") != contract_sha256:
        return {}
    if not _receipt_hash_valid(receipt):
        return {}
    return receipt


def _transition_gate(row: Mapping[str, Any], current: PaperState, target: PaperState) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    gate_receipts: dict[str, Any] = {}
    stage_events = _stage_events(row, current)
    contract_sha256 = str(row.get("contract_sha256") or "")
    if target == PaperState.MANUSCRIPT:
        receipt = next((_valid_stage_receipt(event, "story-search", contract_sha256) for event in reversed(stage_events) if event.get("event_type") == "story-search"), {})
        receipt_sha = str(receipt.get("story_search_sha256") or "")
        if receipt.get("pass") is not True or receipt.get("winner_valid") is not True or not receipt.get("selected_story_id") or not receipt_sha:
            blockers.append("story-search-winner-receipt-required")
        else:
            gate_receipts["story_search_sha256"] = receipt_sha
            gate_receipts["selected_story_id"] = str(receipt.get("selected_story_id") or "")
    if target == PaperState.TARGETED_REPAIR:
        reviews: dict[str, str] = {}
        for event in stage_events:
            receipt = _valid_stage_receipt(event, "mock-pc-review", contract_sha256)
            if not receipt:
                continue
            mode = str(receipt.get("mode") or "")
            review_sha = str(receipt.get("review_sha256") or "")
            if mode in {item.value for item in MockReviewMode} and review_sha:
                reviews[mode] = review_sha
        missing = [mode.value for mode in MockReviewMode if mode.value not in reviews]
        if missing:
            blockers.append("mock-pc-modes-incomplete:" + ",".join(missing))
        else:
            gate_receipts["mock_pc_review_sha256"] = {mode.value: reviews[mode.value] for mode in MockReviewMode}
    if target == PaperState.PDF_QA:
        receipt = next((_valid_stage_receipt(event, "claim-audit", contract_sha256) for event in reversed(stage_events) if event.get("event_type") == "claim-audit"), {})
        receipt_sha = str(receipt.get("claim_audit_sha256") or "")
        if receipt.get("pass") is not True or not receipt_sha:
            blockers.append("claim-audit-pass-receipt-required")
        else:
            gate_receipts["claim_audit_sha256"] = receipt_sha
    if target == PaperState.SUBMISSION_READY and str((row.get("contract") or {}).get("paper_preparation_protocol_version") or "").strip():
        receipt = next((_valid_stage_receipt(event, "paper-preparation", contract_sha256) for event in reversed(stage_events) if event.get("event_type") == "paper-preparation"), {})
        receipt_sha = str(receipt.get("receipt_sha256") or "")
        if receipt.get("pass") is not True or not receipt_sha:
            blockers.append("paper-preparation-pass-receipt-required")
        else:
            gate_receipts["paper_preparation_receipt_sha256"] = receipt_sha
    return blockers, gate_receipts


def _append(root: Path, contract: PaperContract, actor: str, event: Mapping[str, Any]) -> dict[str, Any]:
    path, lock = _paths(root, contract.paper_id)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = json.loads(path.read_text(encoding="utf-8")) if path.exists() else _new(contract, actor)
        digest = paper_contract_digest(contract)
        if row.get("contract_sha256") != digest:
            raise RuntimeError(f"paper contract digest mismatch for {contract.paper_id}")
        payload = dict(event); payload.setdefault("actor", actor); payload.setdefault("recorded_at", _now())
        for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority"):
            payload.setdefault(key, False)
        payload["event_id"] = _digest([contract.paper_id, digest, len(row.get("events") or []), payload])[:24]
        row.setdefault("events", []).append(payload); row["updated_at"] = payload["recorded_at"]
        _refresh(row); _atomic(path, row); return row


def record_story_search(root: Path, contract: PaperContract, candidates: Sequence[StoryCandidate], actor: str = "story-search") -> dict[str, Any]:
    return _append(root, contract, actor, {"event_type": "story-search", "receipt": build_story_search_receipt(contract, candidates)})


def record_mock_review(root: Path, contract: PaperContract, mode: MockReviewMode,
                       objections: Sequence[ReviewerObjection], actor: str = "mock-pc") -> dict[str, Any]:
    return _append(root, contract, actor, {"event_type": "mock-pc-review", "receipt": build_mock_review_receipt(contract, mode, objections)})


def record_claim_audit(
    root: Path,
    contract: PaperContract,
    *,
    manuscript_ref: str,
    claimed_ids: Sequence[str],
    evidence_bound_claim_ids: Sequence[str],
    unsupported_claim_ids_present: Sequence[str] = (),
    limitations_preserved: bool,
    actor: str = "claim-audit",
) -> dict[str, Any]:
    receipt = build_claim_audit_receipt(
        contract,
        manuscript_ref=manuscript_ref,
        claimed_ids=claimed_ids,
        evidence_bound_claim_ids=evidence_bound_claim_ids,
        unsupported_claim_ids_present=unsupported_claim_ids_present,
        limitations_preserved=limitations_preserved,
    )
    return _append(root, contract, actor, {"event_type": "claim-audit", "receipt": receipt})


def record_manuscript_ci(root: Path, contract: PaperContract, checks: Mapping[str, bool], actor: str = "manuscript-ci") -> dict[str, Any]:
    result = evaluate_manuscript_ci(checks)
    return _append(root, contract, actor, {"event_type": "manuscript-ci", "checks": dict(checks),
        "result": {**result, "missing": list(result["missing"]), "failed": list(result["failed"])}})


def record_prebuttal(root: Path, contract: PaperContract, objections: Sequence[ReviewerObjection],
                     resolutions: Sequence[PrebuttalResolution], actor: str = "prebuttal") -> dict[str, Any]:
    result = evaluate_prebuttal(objections, resolutions)
    return _append(root, contract, actor, {"event_type": "prebuttal", "result": {**result, "blockers": list(result["blockers"])}})


def record_paper_preparation(
    root: Path,
    contract: PaperContract,
    packet: Mapping[str, Any],
    actor: str = "paper-preparation",
) -> dict[str, Any]:
    receipt = build_paper_preparation_receipt(
        paper_id=contract.paper_id,
        contract_sha256=paper_contract_digest(contract),
        packet=packet,
    )
    return _append(root, contract, actor, {"event_type": "paper-preparation", "receipt": receipt})


def record_frozen_contract_paper_preparation(
    root: Path,
    paper_id: str,
    packet: Mapping[str, Any],
    actor: str = "legacy-paper-preparation-migration",
) -> dict[str, Any]:
    """Append preparation evidence to a legacy ledger without reserializing its contract.

    Older ledgers may predate optional contract fields that current dataclasses emit even
    when empty. Their byte-level contract identity remains authoritative. This helper
    verifies that the stored canonical payload still hashes to the recorded digest, then
    binds the new preparation receipt to that frozen digest. It never changes contract,
    scientific state, or any authority bit.
    """
    path, lock = _paths(root, paper_id)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        if not path.exists():
            raise FileNotFoundError(path)
        row = json.loads(path.read_text(encoding="utf-8"))
        digest = str(row.get("contract_sha256") or "")
        frozen_contract = row.get("contract") or {}
        if not digest or _digest(frozen_contract) != digest:
            raise RuntimeError(f"frozen paper contract payload digest mismatch for {paper_id}")
        if str(row.get("paper_id") or "") != paper_id:
            raise RuntimeError(f"paper id mismatch for frozen ledger {paper_id}")
        receipt = build_paper_preparation_receipt(
            paper_id=paper_id,
            contract_sha256=digest,
            packet=packet,
        )
        payload = {
            "event_type": "paper-preparation",
            "receipt": receipt,
            "actor": actor,
            "recorded_at": _now(),
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        payload["event_id"] = _digest([paper_id, digest, len(row.get("events") or []), payload])[:24]
        row.setdefault("events", []).append(payload)
        row["updated_at"] = payload["recorded_at"]
        _refresh(row)
        _atomic(path, row)
        return row


def record_submission_readiness(root: Path, contract: PaperContract, actor: str = "submission-readiness") -> dict[str, Any]:
    row = initialize_paper_ledger(root, contract, actor)
    ci = (_latest(row, "manuscript-ci").get("result") or {"pass": False})
    prebuttal = (_latest(row, "prebuttal").get("result") or {"pass": False})
    prep_event = _latest(row, "paper-preparation")
    prep = prep_event.get("receipt") if isinstance(prep_event.get("receipt"), dict) else {}
    if prep and (str(prep.get("contract_sha256") or "") != paper_contract_digest(contract) or not validate_paper_preparation_receipt(prep)):
        prep = {}
    receipt = build_submission_readiness_receipt(contract, ci, prebuttal, prep)
    return _append(root, contract, actor, {"event_type": "submission-readiness", "receipt": receipt})


def advance_paper_ledger(root: Path, contract: PaperContract, target: PaperState, *, actor: str = "paper-workflow",
                         artifact_refs: Sequence[str] = (), external_submission_authority_ref: str = "") -> dict[str, Any]:
    path, lock = _paths(root, contract.paper_id)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = json.loads(path.read_text(encoding="utf-8")) if path.exists() else _new(contract, actor)
        digest = paper_contract_digest(contract)
        if row.get("contract_sha256") != digest:
            raise RuntimeError(f"paper contract digest mismatch for {contract.paper_id}")
        current = PaperState(str(row.get("current_state") or PaperState.PAPER_EVIDENCE.value))
        gate = evaluate_paper_transition(contract, current, target); blockers = list(gate["blockers"])
        hard_gate_blockers, gate_receipts = _transition_gate(row, current, target)
        blockers.extend(hard_gate_blockers)
        if target == PaperState.PREBUTTAL and (_latest(row, "manuscript-ci").get("result") or {}).get("pass") is not True:
            blockers.append("manuscript-ci-not-pass")
        if target == PaperState.SUBMISSION_READY and (_latest(row, "submission-readiness").get("receipt") or {}).get("submission_ready") is not True:
            blockers.append("submission-readiness-receipt-not-pass")
        if target == PaperState.SUBMITTED and not external_submission_authority_ref:
            blockers.append("external-human-submission-authority-required")
        event = {"event_type": "paper-transition", "actor": actor, "recorded_at": _now(), "from": current.value, "to": target.value,
                 "allowed": not blockers, "blockers": list(dict.fromkeys(blockers)), "artifact_refs": list(artifact_refs),
                 "gate_receipts": gate_receipts,
                 "external_submission_authority_ref": external_submission_authority_ref if target == PaperState.SUBMITTED else "",
                 "scientific_authority": False, "experiment_authority": False, "gpu_authority": False, "submission_authority": False}
        event["event_id"] = _digest([contract.paper_id, digest, len(row.get("events") or []), event])[:24]
        row.setdefault("events", []).append(event)
        if event["allowed"]: row["current_state"] = target.value
        row["updated_at"] = event["recorded_at"]; _refresh(row); _atomic(path, row)
        return {"ledger": row, "receipt": event}


def validate_paper_ledger(row: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if (row.get("authority") or {}) != {"scientific": False, "experiment": False, "gpu": False, "submission": False}:
        errors.append("paper ledger must not grant authority")
    try:
        current_state = PaperState(str(row.get("current_state") or ""))
    except ValueError:
        errors.append("unknown current paper state")
        current_state = PaperState.PAPER_EVIDENCE
    contract_sha256 = str(row.get("contract_sha256") or "")
    contract = row.get("contract") or {}
    if str(row.get("scientific_status") or "") != str(contract.get("scientific_status") or ""):
        errors.append("paper scientific status diverges from frozen contract")
    simulated_state = PaperState.PAPER_EVIDENCE
    simulated_row: dict[str, Any] = {"contract_sha256": contract_sha256, "contract": dict(contract), "events": []}
    for event in row.get("events") or []:
        if not isinstance(event, dict):
            errors.append("paper event must be an object")
            continue
        if any(event.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
            errors.append("paper event leaked authority")
        event_type = str(event.get("event_type") or "")
        if event_type in {"story-search", "mock-pc-review", "claim-audit", "paper-preparation"}:
            receipt = event.get("receipt") or {}
            if not isinstance(receipt, dict) or str(receipt.get("contract_sha256") or "") != contract_sha256 or not _receipt_hash_valid(receipt):
                errors.append(f"invalid-content-addressed-receipt:{event_type}")
        if event_type == "paper-transition":
            try:
                target = PaperState(str(event.get("to") or ""))
            except ValueError:
                errors.append("transition has unknown target state")
                simulated_row["events"].append(event)
                continue
            if str(event.get("from") or "") != simulated_state.value:
                errors.append("transition from-state does not match replay state")
            current_index = PAPER_ACCEPTANCE_FLOW.index(simulated_state)
            target_index = PAPER_ACCEPTANCE_FLOW.index(target)
            structural_blockers: list[str] = []
            if target_index != current_index + 1:
                structural_blockers.append("transition-must-advance-exactly-one-paper-state")
            if target != PaperState.PAPER_EVIDENCE:
                if str(contract.get("scientific_status") or "") != "READY":
                    structural_blockers.append("paper-contract-not-ready")
                if not (contract.get("supported_claims") or {}):
                    structural_blockers.append("no-supported-claim")
                if not (contract.get("evidence_refs") or []):
                    structural_blockers.append("no-evidence-reference")
            gate_blockers, expected_gate_receipts = _transition_gate(simulated_row, simulated_state, target)
            structural_blockers.extend(gate_blockers)
            if target == PaperState.PREBUTTAL:
                latest_ci = _latest(simulated_row, "manuscript-ci").get("result") or {}
                if latest_ci.get("pass") is not True:
                    structural_blockers.append("manuscript-ci-not-pass")
            if target == PaperState.SUBMISSION_READY:
                latest_readiness = _latest(simulated_row, "submission-readiness").get("receipt") or {}
                if latest_readiness.get("submission_ready") is not True:
                    structural_blockers.append("submission-readiness-receipt-not-pass")
            if target == PaperState.SUBMITTED and not event.get("external_submission_authority_ref"):
                structural_blockers.append("external-human-submission-authority-required")
            should_allow = not structural_blockers
            if event.get("allowed") is True and not should_allow:
                errors.append("allowed transition bypassed a fail-closed gate")
            if event.get("allowed") is True and (event.get("gate_receipts") or {}) != expected_gate_receipts:
                errors.append("allowed transition gate receipt binding mismatch")
            if event.get("allowed") is True:
                simulated_state = target
        simulated_row["events"].append(event)
    if simulated_state != current_state:
        errors.append("current paper state does not match replayed allowed transitions")
    if len(PAPER_ACCEPTANCE_FLOW) != 12:
        errors.append("paper acceptance flow size mismatch")
    return list(dict.fromkeys(errors))


def public_paper_ledger_summary(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return the frontend-safe projection of one append-only paper ledger.

    Reviewer prose, filesystem locations, actors, and raw event payloads stay private.
    The public state exposes only the paper contract boundary, current workflow state,
    typed gate summaries, and zero-authority invariants.
    """
    contract = row.get("contract") or {}
    latest_story = _latest(row, "story-search").get("receipt") or {}
    latest_ci = _latest(row, "manuscript-ci").get("result") or {}
    latest_prebuttal = _latest(row, "prebuttal").get("result") or {}
    latest_readiness = _latest(row, "submission-readiness").get("receipt") or {}
    latest_prep = _latest(row, "paper-preparation").get("receipt") or {}
    latest_review = _latest(row, "mock-pc-review").get("receipt") or {}
    latest_claim_audit = _latest(row, "claim-audit").get("receipt") or {}
    mock_modes = {}
    for event in row.get("events") or []:
        receipt = (event.get("receipt") or {}) if isinstance(event, dict) and event.get("event_type") == "mock-pc-review" else {}
        mode = str(receipt.get("mode") or "")
        if mode in {item.value for item in MockReviewMode} and _receipt_hash_valid(receipt):
            mock_modes[mode] = str(receipt.get("review_sha256") or "")
    latest_transition = _latest(row, "paper-transition")
    return {
        "paper_id": str(row.get("paper_id") or ""),
        "title": str(contract.get("title") or ""),
        "central_question": str(contract.get("central_question") or ""),
        "contract_sha256": str(row.get("contract_sha256") or ""),
        "scientific_status": str(row.get("scientific_status") or ""),
        "current_state": str(row.get("current_state") or ""),
        "supported_claims": len(contract.get("supported_claims") or {}),
        "active_unrefuted_claims": len(contract.get("active_unrefuted_claims") or {}),
        "unsupported_claims": len(contract.get("unsupported_claims") or {}),
        "limitations": list(contract.get("limitations") or []),
        "reopen_conditions": list(contract.get("reopen_conditions") or []),
        "summary": dict(row.get("summary") or {}),
        "latest_story_search": {
            "pass": latest_story.get("pass") is True,
            "selected_story_id": str(latest_story.get("selected_story_id") or ""),
            "selected_story_title": str(latest_story.get("selected_story_title") or ""),
            "story_search_sha256": str(latest_story.get("story_search_sha256") or ""),
            "valid_candidates": int(latest_story.get("valid_candidates") or 0),
        },
        "mock_pc_modes": {mode.value: mock_modes.get(mode.value, "") for mode in MockReviewMode},
        "latest_mock_review": {
            "mode": str(latest_review.get("mode") or ""),
            "review_sha256": str(latest_review.get("review_sha256") or ""),
            "summary": dict(latest_review.get("summary") or {}),
        },
        "latest_claim_audit": {
            "pass": latest_claim_audit.get("pass") is True,
            "claim_audit_sha256": str(latest_claim_audit.get("claim_audit_sha256") or ""),
            "blockers": list(latest_claim_audit.get("blockers") or []),
        },
        "latest_manuscript_ci": {
            "pass": latest_ci.get("pass") is True,
            "required": int(latest_ci.get("required") or 0),
            "passed": int(latest_ci.get("passed") or 0),
            "missing": list(latest_ci.get("missing") or []),
            "failed": list(latest_ci.get("failed") or []),
        },
        "latest_prebuttal": {
            "pass": latest_prebuttal.get("pass") is True,
            "decision_critical": int(latest_prebuttal.get("decision_critical") or 0),
            "blockers": list(latest_prebuttal.get("blockers") or []),
        },
        "latest_paper_preparation": {
            "required": bool(str(contract.get("paper_preparation_protocol_version") or "").strip()),
            "pass": latest_prep.get("pass") is True,
            "protocol_version": str(latest_prep.get("protocol_version") or ""),
            "receipt_sha256": str(latest_prep.get("receipt_sha256") or ""),
            "gate_pass": dict(latest_prep.get("gate_pass") or {}),
            "blockers": list(latest_prep.get("blockers") or []),
        },
        "latest_submission_readiness": {
            "submission_ready": latest_readiness.get("submission_ready") is True,
            "receipt_sha256": str(latest_readiness.get("receipt_sha256") or ""),
            "blockers": list(latest_readiness.get("blockers") or []),
        },
        "latest_transition": {
            "from": str(latest_transition.get("from") or ""),
            "to": str(latest_transition.get("to") or ""),
            "allowed": latest_transition.get("allowed") is True,
            "blockers": list(latest_transition.get("blockers") or []),
        },
        "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
    }


def build_paper_ledger_index(root: Path) -> dict[str, Any]:
    directory = Path(root) / "paper-acceptance"
    entries: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    if directory.exists():
        for path in sorted(directory.glob("*.json")):
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                invalid.append({"paper_id": path.stem, "errors": ["state-unreadable"]})
                continue
            if not isinstance(row, dict):
                invalid.append({"paper_id": path.stem, "errors": ["state-not-object"]})
                continue
            errors = validate_paper_ledger(row)
            if errors:
                invalid.append({"paper_id": str(row.get("paper_id") or path.stem), "errors": errors})
                continue
            entries.append(public_paper_ledger_summary(row))
    by_state: dict[str, int] = {}
    for row in entries:
        state = str(row.get("current_state") or "UNKNOWN")
        by_state[state] = by_state.get(state, 0) + 1
    return {
        "schema_version": "1.0",
        "policy": {
            "source_ledgers_are_append_only": True,
            "public_projection_excludes_raw_reviewer_prose": True,
            "public_projection_excludes_filesystem_paths_and_actors": True,
            "invalid_ledgers_are_visible_and_never_silently_dropped": True,
            "ledger_projection_has_zero_authority": True,
        },
        "summary": {
            "papers": len(entries),
            "invalid_ledgers": len(invalid),
            "scientific_holds": sum(str(row.get("scientific_status")) != "READY" for row in entries),
            "submission_ready": sum((row.get("latest_submission_readiness") or {}).get("submission_ready") is True for row in entries),
            "by_state": by_state,
        },
        "entries": entries,
        "invalid": invalid,
        "scientific_authority": False,
    }
