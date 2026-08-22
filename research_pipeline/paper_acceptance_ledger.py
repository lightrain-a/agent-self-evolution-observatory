from __future__ import annotations

import fcntl, hashlib, json, os, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .paper_acceptance import (
    MockReviewMode, PAPER_ACCEPTANCE_FLOW, PaperContract, PaperState, PrebuttalResolution,
    ReviewerObjection, StoryCandidate, build_claim_audit_receipt, build_mock_review_receipt,
    build_story_search_receipt, build_submission_readiness_receipt, evaluate_manuscript_ci,
    evaluate_paper_transition, evaluate_prebuttal, paper_contract_digest, paper_contract_payload,
)
from .research_memory_wiki import compile_research_memory_query_pack, load_research_memory_wiki


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
        "submission_readiness_receipts": sum(event.get("event_type") == "submission-readiness" for event in events),
        "contract_revisions": sum(event.get("event_type") == "paper-contract-revised" for event in events),
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


def revise_paper_contract(
    root: Path,
    revised_contract: PaperContract,
    *,
    closure_evidence_refs: Sequence[str],
    reason: str,
    actor: str = "scientific-evidence-closure",
) -> dict[str, Any]:
    """Append a scientific contract revision after a PAPER_EVIDENCE hold is closed.

    This is intentionally narrower than arbitrary paper-contract mutation: it is only
    legal before any post-evidence paper transition, must move a held scientific
    status to READY, must preserve every previously supported claim verbatim, and
    must retain all prior evidence references while binding new closure evidence.
    """
    path, lock = _paths(root, revised_contract.paper_id)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        if not path.exists():
            raise RuntimeError(f"paper ledger missing for {revised_contract.paper_id}")
        row = json.loads(path.read_text(encoding="utf-8"))
        if str(row.get("current_state") or "") != PaperState.PAPER_EVIDENCE.value:
            raise RuntimeError("scientific contract revision is only allowed at PAPER_EVIDENCE")
        previous = row.get("contract") or {}
        previous_digest = str(row.get("contract_sha256") or "")
        if _digest(previous) != previous_digest:
            raise RuntimeError("existing paper contract payload/digest mismatch")
        previous_status = str(previous.get("scientific_status") or "")
        if previous_status not in {"CAUSAL_HOLD", "EVIDENCE_GAP"}:
            raise RuntimeError("scientific contract revision requires a closable evidence hold")
        revised_payload = paper_contract_payload(revised_contract)
        revised_digest = paper_contract_digest(revised_contract)
        if revised_contract.scientific_status.value != "READY" or not revised_contract.post_evidence_ready:
            raise RuntimeError("revised scientific contract must be post-evidence READY")
        if str(previous.get("paper_id") or "") != revised_contract.paper_id:
            raise RuntimeError("paper id cannot change during scientific contract revision")
        previous_claims = dict(previous.get("supported_claims") or {})
        revised_claims = dict(revised_payload.get("supported_claims") or {})
        if any(revised_claims.get(key) != value for key, value in previous_claims.items()):
            raise RuntimeError("previously supported claims must be preserved verbatim")
        previous_refs = set(previous.get("evidence_refs") or [])
        revised_refs = set(revised_payload.get("evidence_refs") or [])
        closure_refs = tuple(dict.fromkeys(str(ref) for ref in closure_evidence_refs if str(ref)))
        if not closure_refs:
            raise RuntimeError("scientific contract revision requires closure evidence references")
        if not previous_refs.issubset(revised_refs):
            raise RuntimeError("revised contract must retain all prior evidence references")
        if not set(closure_refs).issubset(revised_refs):
            raise RuntimeError("closure evidence references must be bound into revised contract")
        if not str(reason).strip():
            raise RuntimeError("scientific contract revision requires a reason")
        event = {
            "event_type": "paper-contract-revised",
            "actor": actor,
            "recorded_at": _now(),
            "previous_contract_sha256": previous_digest,
            "previous_contract": previous,
            "new_contract_sha256": revised_digest,
            "new_contract": revised_payload,
            "closure_evidence_refs": list(closure_refs),
            "reason": str(reason).strip(),
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        event["event_id"] = _digest([revised_contract.paper_id, previous_digest, revised_digest, len(row.get("events") or []), event])[:24]
        row.setdefault("events", []).append(event)
        row["contract_sha256"] = revised_digest
        row["contract"] = revised_payload
        row["scientific_status"] = revised_contract.scientific_status.value
        row["updated_at"] = event["recorded_at"]
        _refresh(row)
        _atomic(path, row)
        return row


def _latest(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, dict) and event.get("event_type") == event_type:
            return event
    return {}


def _review_key(value: Any) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return value[:120] or "unknown"


def _public_review_learning_signals(row: Mapping[str, Any]) -> dict[str, Any]:
    """Aggregate Mock-PC structure without exposing reviewer prose or rationale."""
    category_counts: dict[str, int] = {}
    evidence_state_counts: dict[str, int] = {}
    action_class_counts: dict[str, int] = {}
    review_receipts = decision_critical = targeted = preserved = 0
    contract_sha256 = str(row.get("contract_sha256") or "")
    for event in row.get("events") or []:
        if not isinstance(event, dict) or event.get("event_type") != "mock-pc-review":
            continue
        receipt = event.get("receipt") or {}
        if not isinstance(receipt, dict) or str(receipt.get("contract_sha256") or "") != contract_sha256 or not _receipt_hash_valid(receipt):
            continue
        review_receipts += 1
        summary = receipt.get("summary") or {}
        targeted += int(summary.get("targeted_experiment_proposals") or 0)
        preserved += int(summary.get("claim_expansion_requests_preserved_as_limitations") or 0)
        for objection in receipt.get("objections") or []:
            if not isinstance(objection, dict):
                continue
            category = _review_key(objection.get("category"))
            evidence_state = _review_key(objection.get("evidence_state"))
            category_counts[category] = category_counts.get(category, 0) + 1
            evidence_state_counts[evidence_state] = evidence_state_counts.get(evidence_state, 0) + 1
            decision_critical += int(objection.get("decision_critical") is True)
        for action in receipt.get("actions") or []:
            if not isinstance(action, dict):
                continue
            action_class = _review_key(action.get("action_class"))
            action_class_counts[action_class] = action_class_counts.get(action_class, 0) + 1
    return {
        "review_receipts": review_receipts,
        "decision_critical_objections": decision_critical,
        "category_counts": dict(sorted(category_counts.items())),
        "evidence_state_counts": dict(sorted(evidence_state_counts.items())),
        "action_class_counts": dict(sorted(action_class_counts.items())),
        "targeted_experiment_proposals": targeted,
        "claim_expansion_requests_preserved_as_limitations": preserved,
        "reviewer_prose_exposed": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def _primary_internal_next_action(
    row: Mapping[str, Any], *, latest_preparation: Mapping[str, Any], latest_readiness: Mapping[str, Any],
    latest_submission_context: Mapping[str, Any], immediate_submission_hold: bool, gate_clean_submission_ready: bool,
) -> dict[str, Any]:
    scientific_status = str(row.get("scientific_status") or "")
    current_state = str(row.get("current_state") or "")
    support_blocker = str(latest_submission_context.get("support_blocker") or "").strip()
    recommendation = str(latest_submission_context.get("recommended_immediate_submission") or "").strip()
    preparation_recorded = bool(latest_preparation)
    preparation_pass = latest_preparation.get("pass") is True
    readiness_pass = latest_readiness.get("submission_ready") is True

    if scientific_status != "READY":
        action_class = "SCIENTIFIC_EVIDENCE_REQUIRED"
        action = "Resolve the named scientific evidence hold before any further paper optimization."
        action_zh = "先解决已命名的科学证据 HOLD；在此之前不继续论文优化。"
        blocking_on = scientific_status or "SCIENTIFIC_STATUS_NOT_READY"
    elif immediate_submission_hold and support_blocker:
        action_class = "EXTERNAL_EVIDENCE_REQUIRED"
        action = "Wait for or acquire the named external support asset, then rerun the same frozen internal readiness checks."
        action_zh = "等待或取得已命名的外部支持资产，再按同一冻结规则重跑内部就绪检查。"
        blocking_on = support_blocker
    elif preparation_recorded and not preparation_pass:
        action_class = "PAPER_REPAIR_REQUIRED"
        action = "Repair only the failed internal Paper Preparation gates, preserving the frozen scientific claim boundary."
        action_zh = "只修复未通过的内部 Paper Preparation 门，同时保持冻结的科学主张边界不变。"
        blocking_on = "PAPER_PREPARATION_FAILED"
    elif gate_clean_submission_ready:
        action_class = "NO_INTERNAL_ACTION"
        action = "No additional autonomous research, experiment, or paper-repair action is required by the internal Research OS."
        action_zh = "内部 Research OS 已无新增科研、实验或论文修复动作；保持冻结证据与主张边界即可。"
        blocking_on = ""
    elif current_state != PaperState.SUBMISSION_READY.value or not readiness_pass:
        action_class = "PAPER_WORKFLOW_CONTINUE"
        action = "Continue only the next unmet internal Paper Acceptance gate; do not reopen science implicitly."
        action_zh = "只继续下一个尚未完成的内部 Paper Acceptance 门；不得隐式重开科研主张。"
        blocking_on = current_state or "PAPER_WORKFLOW_INCOMPLETE"
    else:
        action_class = "INTERNAL_GATE_REVIEW_REQUIRED"
        action = "Reconcile the latest internal gate receipts before taking any new research action."
        action_zh = "先核对最新内部门禁 receipt，再决定是否存在新的科研动作。"
        blocking_on = recommendation or "READINESS_STATE_INCONSISTENT"
    return {
        "action_class": action_class,
        "action": action,
        "action_zh": action_zh,
        "blocking_on": blocking_on,
        "machine_actionable": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


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
        story_sha = str(receipt.get("story_search_sha256") or "")
        if story_sha != _digest(identity):
            return False
        memory_receipt = receipt.get("paper_design_memory_query_receipt")
        if memory_receipt is None:
            return True
        if not isinstance(memory_receipt, Mapping) or memory_receipt.get("purpose") != "PAPER_DESIGN" or memory_receipt.get("scientific_authority") is not False:
            return False
        if not re.fullmatch(r"[0-9a-f]{64}", str(memory_receipt.get("wiki_sha256") or "")) or not re.fullmatch(r"[0-9a-f]{64}", str(memory_receipt.get("query_pack_sha256") or "")):
            return False
        binding = {"story_search_sha256": story_sha, "paper_design_memory_query_receipt": dict(memory_receipt)}
        return str(receipt.get("paper_design_memory_binding_sha256") or "") == _digest(binding)
    if receipt_type == "mock-pc-review":
        identity = {
            "paper_id": receipt.get("paper_id"),
            "contract_sha256": receipt.get("contract_sha256"),
            "mode": receipt.get("mode"),
            "objections": receipt.get("objections") or [],
            "actions": receipt.get("actions") or [],
        }
        return str(receipt.get("review_sha256") or "") == _digest(identity)
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


def _paper_design_memory_pack(contract: PaperContract) -> dict[str, Any]:
    return compile_research_memory_query_pack(
        load_research_memory_wiki(),
        purpose="PAPER_DESIGN",
        context={
            "paper_id": contract.paper_id,
            "title": contract.title,
            "central_question": contract.central_question,
            "supported_claims": contract.supported_claims,
            "active_unrefuted_claims": getattr(contract, "active_unrefuted_claims", {}),
            "limitations": contract.limitations,
        },
        max_chars=4800,
        max_items=16,
    )


def _paper_design_memory_receipt(pack: Mapping[str, Any]) -> dict[str, Any]:
    if str(pack.get("purpose") or "") != "PAPER_DESIGN" or pack.get("scientific_authority") is not False:
        raise ValueError("Story Search requires a zero-authority PAPER_DESIGN Research Memory query pack")
    query_sha = str(pack.get("query_pack_sha256") or "")
    wiki_sha = str(pack.get("wiki_sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", query_sha) or not re.fullmatch(r"[0-9a-f]{64}", wiki_sha):
        raise ValueError("Story Search Research Memory query pack must be content-addressed")
    selected = [row for row in pack.get("selected") or [] if isinstance(row, Mapping)]
    return {
        "purpose": "PAPER_DESIGN",
        "wiki_sha256": wiki_sha,
        "query_pack_sha256": query_sha,
        "selected_memory_ids": [str(value) for value in (pack.get("selected_memory_ids") or [])],
        "selected": int((pack.get("summary") or {}).get("selected") or 0),
        "review_lessons_selected": sum(str(row.get("kind") or "") == "REVIEW_LESSON" for row in selected),
        "memory_is_context_not_scientific_verdict": True,
        "paper_review_patterns_are_prechecks_not_verdicts": True,
        "scientific_authority": False,
        "method_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def record_story_search(
    root: Path,
    contract: PaperContract,
    candidates: Sequence[StoryCandidate],
    actor: str = "story-search",
    *,
    research_memory_query_pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    pack = dict(research_memory_query_pack) if research_memory_query_pack is not None else _paper_design_memory_pack(contract)
    receipt = build_story_search_receipt(contract, candidates)
    memory_receipt = _paper_design_memory_receipt(pack)
    receipt["paper_design_memory_query_receipt"] = memory_receipt
    receipt["paper_design_memory_binding_sha256"] = _digest({"story_search_sha256": receipt["story_search_sha256"], "paper_design_memory_query_receipt": memory_receipt})
    return _append(root, contract, actor, {"event_type": "story-search", "receipt": receipt})


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


def record_submission_readiness(root: Path, contract: PaperContract, actor: str = "submission-readiness") -> dict[str, Any]:
    row = initialize_paper_ledger(root, contract, actor)
    ci = (_latest(row, "manuscript-ci").get("result") or {"pass": False})
    prebuttal = (_latest(row, "prebuttal").get("result") or {"pass": False})
    receipt = build_submission_readiness_receipt(contract, ci, prebuttal)
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

    final_contract_sha256 = str(row.get("contract_sha256") or "")
    final_contract = row.get("contract") or {}
    if not isinstance(final_contract, dict) or _digest(final_contract) != final_contract_sha256:
        errors.append("current paper contract payload/digest mismatch")
    if str(row.get("scientific_status") or "") != str(final_contract.get("scientific_status") or ""):
        errors.append("paper scientific status diverges from current contract")

    events = list(row.get("events") or [])
    contract_by_digest: dict[str, dict[str, Any]] = {}
    if isinstance(final_contract, dict) and final_contract_sha256:
        contract_by_digest[final_contract_sha256] = dict(final_contract)
    for event in events:
        if not isinstance(event, dict) or event.get("event_type") != "paper-contract-revised":
            continue
        previous = event.get("previous_contract") or {}
        revised = event.get("new_contract") or {}
        previous_digest = str(event.get("previous_contract_sha256") or "")
        revised_digest = str(event.get("new_contract_sha256") or "")
        if not isinstance(previous, dict) or _digest(previous) != previous_digest:
            errors.append("paper contract revision previous payload/digest mismatch")
        else:
            contract_by_digest[previous_digest] = dict(previous)
        if not isinstance(revised, dict) or _digest(revised) != revised_digest:
            errors.append("paper contract revision new payload/digest mismatch")
        else:
            contract_by_digest[revised_digest] = dict(revised)

    registration = next((event for event in events if isinstance(event, dict) and event.get("event_type") == "paper-contract-registered"), {})
    simulated_contract_sha256 = str(registration.get("contract_sha256") or final_contract_sha256)
    simulated_contract = contract_by_digest.get(simulated_contract_sha256)
    if simulated_contract is None:
        errors.append("initial paper contract snapshot unavailable for replay")
        simulated_contract = dict(final_contract) if isinstance(final_contract, dict) else {}
    simulated_state = PaperState.PAPER_EVIDENCE
    simulated_row: dict[str, Any] = {"contract_sha256": simulated_contract_sha256, "events": []}

    for event in events:
        if not isinstance(event, dict):
            errors.append("paper event must be an object")
            continue
        if any(event.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
            errors.append("paper event leaked authority")
        event_type = str(event.get("event_type") or "")

        if event_type == "paper-contract-revised":
            previous = event.get("previous_contract") or {}
            revised = event.get("new_contract") or {}
            previous_digest = str(event.get("previous_contract_sha256") or "")
            revised_digest = str(event.get("new_contract_sha256") or "")
            closure_refs = tuple(str(ref) for ref in (event.get("closure_evidence_refs") or []) if str(ref))
            if simulated_state != PaperState.PAPER_EVIDENCE:
                errors.append("paper contract revision occurred after PAPER_EVIDENCE")
            if previous_digest != simulated_contract_sha256:
                errors.append("paper contract revision previous digest does not match replay contract")
            if not isinstance(previous, dict) or previous != simulated_contract:
                errors.append("paper contract revision previous snapshot does not match replay contract")
            if str(previous.get("scientific_status") or "") not in {"CAUSAL_HOLD", "EVIDENCE_GAP"}:
                errors.append("paper contract revision did not close an evidence hold")
            if not isinstance(revised, dict) or str(revised.get("scientific_status") or "") != "READY":
                errors.append("paper contract revision did not produce READY status")
            if str(previous.get("paper_id") or "") != str(revised.get("paper_id") or ""):
                errors.append("paper contract revision changed paper id")
            previous_claims = dict(previous.get("supported_claims") or {})
            revised_claims = dict(revised.get("supported_claims") or {}) if isinstance(revised, dict) else {}
            if any(revised_claims.get(key) != value for key, value in previous_claims.items()):
                errors.append("paper contract revision changed a previously supported claim")
            previous_refs = set(previous.get("evidence_refs") or [])
            revised_refs = set(revised.get("evidence_refs") or []) if isinstance(revised, dict) else set()
            if not previous_refs.issubset(revised_refs):
                errors.append("paper contract revision dropped prior evidence")
            if not closure_refs or not set(closure_refs).issubset(revised_refs):
                errors.append("paper contract revision closure evidence is missing or unbound")
            if not str(event.get("reason") or "").strip():
                errors.append("paper contract revision reason missing")
            simulated_contract_sha256 = revised_digest
            simulated_contract = dict(revised) if isinstance(revised, dict) else {}
            simulated_row["contract_sha256"] = simulated_contract_sha256

        if event_type in {"story-search", "mock-pc-review", "claim-audit"}:
            receipt = event.get("receipt") or {}
            if not isinstance(receipt, dict) or str(receipt.get("contract_sha256") or "") != simulated_contract_sha256 or not _receipt_hash_valid(receipt):
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
                if str(simulated_contract.get("scientific_status") or "") != "READY":
                    structural_blockers.append("paper-contract-not-ready")
                if not (simulated_contract.get("supported_claims") or {}):
                    structural_blockers.append("no-supported-claim")
                if not (simulated_contract.get("evidence_refs") or []):
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

    if simulated_contract_sha256 != final_contract_sha256:
        errors.append("current paper contract digest does not match replayed contract revisions")
    if simulated_contract != final_contract:
        errors.append("current paper contract does not match replayed contract revisions")
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
    latest_preparation = _latest(row, "paper-preparation").get("receipt") or {}
    latest_readiness = _latest(row, "submission-readiness").get("receipt") or {}
    latest_review = _latest(row, "mock-pc-review").get("receipt") or {}
    latest_claim_audit = _latest(row, "claim-audit").get("receipt") or {}
    latest_submission_context = _latest(row, "submission-readiness-context")
    preparation_recorded = bool(latest_preparation)
    preparation_pass = latest_preparation.get("pass") is True
    immediate_recommendation = str(latest_submission_context.get("recommended_immediate_submission") or "")
    immediate_submission_hold = immediate_recommendation.startswith("HOLD") or (preparation_recorded and not preparation_pass)
    gate_clean_submission_ready = latest_readiness.get("submission_ready") is True and not immediate_submission_hold
    primary_next_action = _primary_internal_next_action(
        row,
        latest_preparation=latest_preparation,
        latest_readiness=latest_readiness,
        latest_submission_context=latest_submission_context,
        immediate_submission_hold=immediate_submission_hold,
        gate_clean_submission_ready=gate_clean_submission_ready,
    )
    review_learning = _public_review_learning_signals(row)
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
        "gate_clean_submission_ready": gate_clean_submission_ready,
        "immediate_submission_hold": immediate_submission_hold,
        "primary_next_action": primary_next_action,
        "review_learning": review_learning,
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
            "paper_design_memory_query_pack_sha256": str((latest_story.get("paper_design_memory_query_receipt") or {}).get("query_pack_sha256") or ""),
            "paper_design_memory_binding_sha256": str(latest_story.get("paper_design_memory_binding_sha256") or ""),
            "paper_design_memory_wiki_sha256": str((latest_story.get("paper_design_memory_query_receipt") or {}).get("wiki_sha256") or ""),
            "paper_design_memory_selected": int((latest_story.get("paper_design_memory_query_receipt") or {}).get("selected") or 0),
            "paper_design_review_lessons_selected": int((latest_story.get("paper_design_memory_query_receipt") or {}).get("review_lessons_selected") or 0),
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
            "pass": latest_preparation.get("pass") is True,
            "protocol_version": str(latest_preparation.get("protocol_version") or ""),
            "receipt_sha256": str(latest_preparation.get("receipt_sha256") or ""),
            "required_gates": int((latest_preparation.get("summary") or {}).get("required_gates") or 0),
            "passed_gates": int((latest_preparation.get("summary") or {}).get("passed_gates") or 0),
            "gate_pass": {str(key): value is True for key, value in (latest_preparation.get("gate_pass") or {}).items()},
            "blockers": [str(item) for item in (latest_preparation.get("blockers") or [])],
        },
        "submission_readiness_context": {
            "artifact_submission_ready": latest_submission_context.get("artifact_submission_ready") is True,
            "recommended_immediate_submission": str(latest_submission_context.get("recommended_immediate_submission") or ""),
            "scientific_status": str(latest_submission_context.get("scientific_status") or ""),
            "support_blocker": str(latest_submission_context.get("support_blocker") or ""),
            "external_human_submission_authority_required_for_SUBMITTED": latest_submission_context.get("external_human_submission_authority_required_for_SUBMITTED") is True,
            "c3_c4_evidence_state": str(latest_submission_context.get("c3_c4_evidence_state") or ""),
            "post_repair_mock_pc_recommendations": [str(item) for item in (latest_submission_context.get("post_repair_mock_pc_recommendations") or [])],
            "post_repair_mock_pc_scores": [int(item) for item in (latest_submission_context.get("post_repair_mock_pc_scores") or [])],
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


def build_portable_paper_ledger_index(registry: Mapping[str, Any]) -> dict[str, Any]:
    """Reconstruct a zero-authority ledger index from a committed PaperRegistry.

    The append-only ledger on the research host remains authoritative whenever it
    is available. This portable projection exists for automation/CI hosts that do
    not mount that host-private directory: an empty local directory must not erase
    a previously published, provenance-bound paper state.
    """
    entries: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    policy = registry.get("policy") or {}
    if policy.get("paper_registry_is_projection_of_append_only_acceptance_ledgers") is not True:
        invalid.append({"paper_id": "paper-registry", "errors": ["portable-registry-provenance-policy-missing"]})
    seen: set[str] = set()
    for raw in registry.get("papers") or []:
        if not isinstance(raw, Mapping):
            invalid.append({"paper_id": "unknown", "errors": ["portable-registry-row-not-object"]})
            continue
        canonical_id = str(raw.get("acceptance_paper_id") or raw.get("paper_id") or "").strip()
        errors: list[str] = []
        if not canonical_id:
            errors.append("portable-registry-paper-id-missing")
        elif canonical_id in seen:
            errors.append("portable-registry-paper-id-duplicate")
        current_state = str(raw.get("current_state") or "")
        if current_state not in {state.value for state in PAPER_ACCEPTANCE_FLOW}:
            errors.append("portable-registry-current-state-invalid")
        authority = raw.get("acceptance_authority") or raw.get("authority") or {}
        if any(bool(authority.get(key)) for key in ("scientific", "experiment", "gpu", "submission")):
            errors.append("portable-registry-authority-leak")
        readiness = raw.get("latest_submission_readiness") or {}
        if not isinstance(readiness, Mapping):
            errors.append("portable-registry-readiness-invalid")
        if errors:
            invalid.append({"paper_id": canonical_id or "unknown", "errors": errors})
            continue
        seen.add(canonical_id)
        row = dict(raw)
        row["paper_id"] = canonical_id
        row["authority"] = {"scientific": False, "experiment": False, "gpu": False, "submission": False}
        entries.append(row)
    by_state: dict[str, int] = {}
    for row in entries:
        state = str(row.get("current_state") or "UNKNOWN")
        by_state[state] = by_state.get(state, 0) + 1
    return {
        "schema_version": "1.0-portable-registry",
        "policy": {
            "source_ledgers_are_append_only": True,
            "public_projection_excludes_raw_reviewer_prose": True,
            "public_projection_excludes_filesystem_paths_and_actors": True,
            "invalid_ledgers_are_visible_and_never_silently_dropped": True,
            "ledger_projection_has_zero_authority": True,
            "portable_registry_fallback_requires_committed_ledger_projection": True,
            "empty_machine_local_ledger_does_not_erase_portable_state": True,
            "submission_ready_is_historical_receipt_count": True,
            "gate_clean_submission_ready_is_latest_effective_internal_readiness": True,
            "primary_next_action_is_internal_only_and_zero_authority": True,
            "review_learning_excludes_reviewer_prose_and_rationale": True,
        },
        "summary": {
            "papers": len(entries),
            "invalid_ledgers": len(invalid),
            "scientific_holds": sum(str(row.get("scientific_status")) != "READY" for row in entries),
            "submission_ready": sum((row.get("latest_submission_readiness") or {}).get("submission_ready") is True for row in entries),
            "gate_clean_submission_ready": sum(row.get("gate_clean_submission_ready") is True for row in entries),
            "paper_preparation_failed": sum((row.get("latest_paper_preparation") or {}).get("required_gates", 0) > 0 and (row.get("latest_paper_preparation") or {}).get("pass") is not True for row in entries),
            "immediate_submission_holds": sum(row.get("immediate_submission_hold") is True for row in entries),
            "internal_action_required": sum((row.get("primary_next_action") or {}).get("action_class") != "NO_INTERNAL_ACTION" for row in entries),
            "no_internal_action": sum((row.get("primary_next_action") or {}).get("action_class") == "NO_INTERNAL_ACTION" for row in entries),
            "by_internal_action": dict(sorted(Counter((row.get("primary_next_action") or {}).get("action_class") or "UNKNOWN" for row in entries).items())),
            "by_state": by_state,
        },
        "entries": entries,
        "invalid": invalid,
        "scientific_authority": False,
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
            "submission_ready_is_historical_receipt_count": True,
            "gate_clean_submission_ready_is_latest_effective_internal_readiness": True,
            "primary_next_action_is_internal_only_and_zero_authority": True,
            "review_learning_excludes_reviewer_prose_and_rationale": True,
        },
        "summary": {
            "papers": len(entries),
            "invalid_ledgers": len(invalid),
            "scientific_holds": sum(str(row.get("scientific_status")) != "READY" for row in entries),
            "submission_ready": sum((row.get("latest_submission_readiness") or {}).get("submission_ready") is True for row in entries),
            "gate_clean_submission_ready": sum(row.get("gate_clean_submission_ready") is True for row in entries),
            "paper_preparation_failed": sum((row.get("latest_paper_preparation") or {}).get("required_gates", 0) > 0 and (row.get("latest_paper_preparation") or {}).get("pass") is not True for row in entries),
            "immediate_submission_holds": sum(row.get("immediate_submission_hold") is True for row in entries),
            "internal_action_required": sum((row.get("primary_next_action") or {}).get("action_class") != "NO_INTERNAL_ACTION" for row in entries),
            "no_internal_action": sum((row.get("primary_next_action") or {}).get("action_class") == "NO_INTERNAL_ACTION" for row in entries),
            "by_internal_action": dict(sorted(Counter((row.get("primary_next_action") or {}).get("action_class") or "UNKNOWN" for row in entries).items())),
            "by_state": by_state,
        },
        "entries": entries,
        "invalid": invalid,
        "scientific_authority": False,
    }
