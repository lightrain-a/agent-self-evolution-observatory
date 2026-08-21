from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class ScientificPaperStatus(str, Enum):
    READY = "READY"
    EVIDENCE_GAP = "EVIDENCE_GAP"
    CAUSAL_HOLD = "CAUSAL_HOLD"
    TERMINAL_NEGATIVE = "TERMINAL_NEGATIVE"


class PaperState(str, Enum):
    PAPER_EVIDENCE = "PAPER_EVIDENCE"
    PAPER_DESIGN = "PAPER_DESIGN"
    MANUSCRIPT = "MANUSCRIPT"
    MOCK_PC = "MOCK_PC"
    TARGETED_REPAIR = "TARGETED_REPAIR"
    CLAIM_AUDIT = "CLAIM_AUDIT"
    PDF_QA = "PDF_QA"
    PREBUTTAL = "PREBUTTAL"
    SUBMISSION_READY = "SUBMISSION_READY"
    SUBMITTED = "SUBMITTED"
    REBUTTAL = "REBUTTAL"
    LEARN = "LEARN"


PAPER_ACCEPTANCE_FLOW: tuple[PaperState, ...] = tuple(PaperState)
PAPER_ACCEPTANCE_TEMPORAL_KEYS: tuple[str, ...] = (
    "paper-evidence", "paper-design", "manuscript", "mock-pc", "targeted-repair", "claim-audit",
    "pdf-qa", "prebuttal", "submission-ready", "submitted", "rebuttal", "learn",
)


class MockReviewMode(str, Enum):
    BLIND_MANUSCRIPT = "BLIND_MANUSCRIPT"
    ARTIFACT_AWARE = "ARTIFACT_AWARE"


class ObjectionEvidenceState(str, Enum):
    EXISTING_EVIDENCE = "EXISTING_EVIDENCE"
    MISSING_DECISIVE_EVIDENCE = "MISSING_DECISIVE_EVIDENCE"
    REQUIRES_NEW_CLAIM = "REQUIRES_NEW_CLAIM"
    FALSE_PREMISE_WITH_EVIDENCE = "FALSE_PREMISE_WITH_EVIDENCE"
    UNCERTAIN = "UNCERTAIN"


class ReviewActionClass(str, Enum):
    NARRATIVE_REPAIR = "NARRATIVE_REPAIR"
    TARGETED_EXPERIMENT = "TARGETED_EXPERIMENT"
    PREBUTTAL = "PREBUTTAL"
    PRESERVE_LIMITATION = "PRESERVE_LIMITATION"
    HUMAN_ADJUDICATION = "HUMAN_ADJUDICATION"


MANDATORY_MANUSCRIPT_CI_CHECKS: tuple[str, ...] = (
    "citation-reference-consistency",
    "numeric-consistency",
    "figure-table-consistency",
    "forbidden-claim-detection",
    "anonymity",
    "page-constraint",
    "rendered-pdf-visual-qa",
    "artifact-hashes",
    "statement-evidence-binding",
)


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "scientific_truth_precedes_paper_optimization": True,
    "paper_workflow_never_grants_scientific_authority": True,
    "paper_workflow_never_grants_experiment_or_gpu_authority": True,
    "evidence_gap_blocks_post_evidence_advancement": True,
    "causal_hold_blocks_post_evidence_advancement": True,
    "story_search_may_reframe_but_not_expand_supported_claims": True,
    "story_search_winner_required_for_manuscript": True,
    "blind_and_artifact_aware_review_are_distinct": True,
    "both_mock_pc_modes_required_for_targeted_repair": True,
    "review_to_action_is_advisory_only": True,
    "claim_audit_pass_required_for_pdf_qa": True,
    "missing_evidence_does_not_auto_authorize_an_experiment": True,
    "new_claim_request_preserves_limitation_instead_of_claim_expansion": True,
    "decision_critical_prebuttal_objections_must_be_resolved": True,
    "manuscript_ci_fails_closed": True,
    "submission_ready_requires_prebuttal_and_manuscript_ci": True,
    "paper_ledger_is_append_only_event_projection": True,
    "blocked_transitions_are_recorded": True,
    "ledger_contract_digest_is_immutable": True,
    "submitted_state_requires_external_human_submission_authority": True,
}


@dataclass(frozen=True)
class PaperContract:
    paper_id: str
    title: str
    central_question: str
    supported_claims: Mapping[str, str]
    active_unrefuted_claims: Mapping[str, str] = field(default_factory=dict)
    active_claim_experiment_debt: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    unsupported_claims: Mapping[str, str] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    reopen_conditions: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    scientific_status: ScientificPaperStatus = ScientificPaperStatus.READY
    scientific_authority: bool = field(default=False, init=False)
    experiment_authority: bool = field(default=False, init=False)
    gpu_authority: bool = field(default=False, init=False)

    def blockers(self) -> tuple[str, ...]:
        blockers: list[str] = []
        if self.scientific_status == ScientificPaperStatus.EVIDENCE_GAP:
            blockers.append("scientific-evidence-gap")
        elif self.scientific_status == ScientificPaperStatus.CAUSAL_HOLD:
            blockers.append("causal-hold")
        elif self.scientific_status == ScientificPaperStatus.TERMINAL_NEGATIVE:
            blockers.append("terminal-negative-no-active-paper-claim")
        if not self.supported_claims:
            blockers.append("no-supported-claim")
        if not self.evidence_refs:
            blockers.append("no-evidence-reference")
        return tuple(blockers)

    @property
    def post_evidence_ready(self) -> bool:
        return self.scientific_status == ScientificPaperStatus.READY and not self.blockers()


def paper_contract_payload(contract: PaperContract) -> dict[str, Any]:
    return {
        "paper_id": contract.paper_id,
        "title": contract.title,
        "central_question": contract.central_question,
        "supported_claims": dict(contract.supported_claims),
        "active_unrefuted_claims": dict(contract.active_unrefuted_claims),
        "active_claim_experiment_debt": {key: list(value) for key, value in contract.active_claim_experiment_debt.items()},
        "unsupported_claims": dict(contract.unsupported_claims),
        "limitations": list(contract.limitations),
        "reopen_conditions": list(contract.reopen_conditions),
        "evidence_refs": list(contract.evidence_refs),
        "scientific_status": contract.scientific_status.value,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def paper_contract_digest(contract: PaperContract) -> str:
    payload = json.dumps(paper_contract_payload(contract), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class StoryCandidate:
    story_id: str
    title: str
    framing: str
    contribution_order: tuple[str, ...]
    emphasized_claim_ids: tuple[str, ...]
    figure_order: tuple[str, ...] = ()

    def validate(self, contract: PaperContract) -> tuple[str, ...]:
        manuscript_claims = set(contract.supported_claims) | set(contract.active_unrefuted_claims)
        referenced = set(self.contribution_order) | set(self.emphasized_claim_ids)
        unknown = sorted(referenced - manuscript_claims)
        errors: list[str] = []
        if unknown:
            errors.append("story-references-unsupported-claims:" + ",".join(unknown))
        if len(self.contribution_order) != len(set(self.contribution_order)):
            errors.append("duplicate-contribution-claim")
        if not self.emphasized_claim_ids:
            errors.append("story-has-no-supported-claim-emphasis")
        return tuple(errors)


def evaluate_story_search(contract: PaperContract, candidates: Sequence[StoryCandidate]) -> dict[str, Any]:
    supported = set(contract.supported_claims)
    active = set(contract.active_unrefuted_claims)
    manuscript_claims = supported | active
    denom = max(1, len(manuscript_claims))
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        errors = candidate.validate(contract)
        emphasized = set(candidate.emphasized_claim_ids) & manuscript_claims
        contributions = set(candidate.contribution_order) & manuscript_claims
        score = 0.6 * len(emphasized) / denom + 0.4 * len(contributions) / denom
        rows.append({
            "story_id": candidate.story_id,
            "title": candidate.title,
            "framing": candidate.framing,
            "valid": not errors,
            "errors": list(errors),
            "manuscript_claim_coverage": round(len(emphasized) / denom, 4),
            "supported_claim_coverage": round(len(set(candidate.emphasized_claim_ids) & supported) / max(1, len(supported)), 4),
            "active_unrefuted_claim_coverage": round(len(set(candidate.emphasized_claim_ids) & active) / max(1, len(active)), 4) if active else 0.0,
            "rank_score": round(score, 4) if not errors else 0.0,
            "scientific_authority": False,
        })
    rows.sort(key=lambda row: (not row["valid"], -float(row["rank_score"]), str(row["story_id"])))
    return {
        "paper_id": contract.paper_id,
        "candidates": rows,
        "valid_candidates": sum(bool(row["valid"]) for row in rows),
        "selected_story_id": next((str(row["story_id"]) for row in rows if row["valid"]), ""),
        "claim_expansion_authorized": False,
        "scientific_authority": False,
    }


def build_story_search_receipt(contract: PaperContract, candidates: Sequence[StoryCandidate]) -> dict[str, Any]:
    result = evaluate_story_search(contract, candidates)
    selected_id = str(result.get("selected_story_id") or "")
    selected = next((row for row in result["candidates"] if row.get("story_id") == selected_id), {})
    candidate_identity = [
        {
            "story_id": row.story_id,
            "title": row.title,
            "framing": row.framing,
            "contribution_order": list(row.contribution_order),
            "emphasized_claim_ids": list(row.emphasized_claim_ids),
            "figure_order": list(row.figure_order),
        }
        for row in candidates
    ]
    identity = {
        "paper_id": contract.paper_id,
        "contract_sha256": paper_contract_digest(contract),
        "candidate_set_sha256": hashlib.sha256(json.dumps(candidate_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "selected_story_id": selected_id,
        "selected_story_title": str(selected.get("title") or ""),
        "valid_candidates": int(result.get("valid_candidates") or 0),
        "winner_valid": bool(selected and selected.get("valid") is True),
        "claim_expansion_authorized": False,
    }
    raw = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": "1.0",
        "receipt_type": "story-search",
        **identity,
        "pass": bool(selected_id and identity["winner_valid"]),
        "story_search_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


@dataclass(frozen=True)
class ReviewerObjection:
    objection_id: str
    category: str
    text: str
    decision_critical: bool
    evidence_state: ObjectionEvidenceState
    claim_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewAction:
    objection_id: str
    action_class: ReviewActionClass
    reason: str
    claim_expansion_authorized: bool = False
    execution_authorized: bool = False
    scientific_authority: bool = False


@dataclass(frozen=True)
class PrebuttalResolution:
    objection_id: str
    resolved: bool
    evidence_refs: tuple[str, ...] = ()


def evaluate_paper_transition(contract: PaperContract, current: PaperState, target: PaperState) -> dict[str, Any]:
    current_index = PAPER_ACCEPTANCE_FLOW.index(current)
    target_index = PAPER_ACCEPTANCE_FLOW.index(target)
    blockers: list[str] = []
    if target_index != current_index + 1:
        blockers.append("transition-must-advance-exactly-one-paper-state")
    if target != PaperState.PAPER_EVIDENCE and not contract.post_evidence_ready:
        blockers.extend(contract.blockers())
    return {
        "paper_id": contract.paper_id,
        "from": current.value,
        "to": target.value,
        "allowed": not blockers,
        "blockers": tuple(dict.fromkeys(blockers)),
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def compile_review_action(objection: ReviewerObjection, contract: PaperContract) -> ReviewAction:
    manuscript_claims = set(contract.supported_claims) | set(contract.active_unrefuted_claims)
    unknown_claims = sorted(set(objection.claim_ids) - manuscript_claims)
    if objection.evidence_state == ObjectionEvidenceState.REQUIRES_NEW_CLAIM or unknown_claims:
        action = ReviewActionClass.PRESERVE_LIMITATION
        reason = "Answering this objection would expand the frozen scientific contract; preserve the limitation unless science is formally reopened."
    elif objection.evidence_state == ObjectionEvidenceState.EXISTING_EVIDENCE:
        action = ReviewActionClass.NARRATIVE_REPAIR
        reason = "Existing admissible evidence should be made legible in the manuscript."
    elif objection.evidence_state == ObjectionEvidenceState.FALSE_PREMISE_WITH_EVIDENCE:
        action = ReviewActionClass.PREBUTTAL
        reason = "The objection can be answered from already-admissible evidence without changing the claim."
    elif objection.evidence_state == ObjectionEvidenceState.MISSING_DECISIVE_EVIDENCE:
        action = ReviewActionClass.TARGETED_EXPERIMENT
        reason = "A decision-critical evidence gap is present; experiment design may be proposed but is not authorized."
    else:
        action = ReviewActionClass.HUMAN_ADJUDICATION
        reason = "The objection cannot be safely compiled into a paper-only repair from current evidence."
    return ReviewAction(objection_id=objection.objection_id, action_class=action, reason=reason)


def build_mock_review_receipt(contract: PaperContract, mode: MockReviewMode, objections: Sequence[ReviewerObjection]) -> dict[str, Any]:
    actions = [compile_review_action(objection, contract) for objection in objections]
    action_rows = [{
        "objection_id": row.objection_id,
        "action_class": row.action_class.value,
        "reason": row.reason,
        "claim_expansion_authorized": False,
        "execution_authorized": False,
        "scientific_authority": False,
    } for row in actions]
    objection_rows = [{
        "objection_id": row.objection_id,
        "category": row.category,
        "text": row.text,
        "decision_critical": row.decision_critical,
        "evidence_state": row.evidence_state.value,
        "claim_ids": list(row.claim_ids),
    } for row in objections]
    identity = {"paper_id": contract.paper_id, "contract_sha256": paper_contract_digest(contract), "mode": mode.value, "objections": objection_rows, "actions": action_rows}
    raw = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": "1.0",
        "receipt_type": "mock-pc-review",
        **identity,
        "review_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "summary": {
            "objections": len(objection_rows),
            "decision_critical": sum(bool(row["decision_critical"]) for row in objection_rows),
            "targeted_experiment_proposals": sum(row["action_class"] == ReviewActionClass.TARGETED_EXPERIMENT.value for row in action_rows),
            "claim_expansion_requests_preserved_as_limitations": sum(row["action_class"] == ReviewActionClass.PRESERVE_LIMITATION.value for row in action_rows),
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def evaluate_claim_audit(
    contract: PaperContract,
    *,
    manuscript_ref: str,
    claimed_ids: Sequence[str],
    evidence_bound_claim_ids: Sequence[str],
    unsupported_claim_ids_present: Sequence[str] = (),
    limitations_preserved: bool,
) -> dict[str, Any]:
    supported = set(contract.supported_claims)
    active = set(contract.active_unrefuted_claims)
    manuscript_claims = supported | active
    claimed = set(claimed_ids)
    evidence_bound = set(evidence_bound_claim_ids)
    unsupported_present = set(unsupported_claim_ids_present)
    blockers: list[str] = []
    if not manuscript_ref:
        blockers.append("claim-audit-missing-manuscript-ref")
    if not claimed:
        blockers.append("claim-audit-no-claims")
    unknown = sorted(claimed - manuscript_claims)
    if unknown:
        blockers.append("claim-audit-unknown-or-unsupported-claims:" + ",".join(unknown))
    contract_unsupported = sorted(unsupported_present & set(contract.unsupported_claims))
    extra_unsupported = sorted(unsupported_present - set(contract.unsupported_claims))
    if contract_unsupported:
        blockers.append("claim-audit-frozen-unsupported-claims-present:" + ",".join(contract_unsupported))
    if extra_unsupported:
        blockers.append("claim-audit-unregistered-claims-present:" + ",".join(extra_unsupported))
    unbound = sorted((claimed & manuscript_claims) - evidence_bound)
    if unbound:
        blockers.append("claim-audit-evidence-binding-missing:" + ",".join(unbound))
    if contract.limitations and not limitations_preserved:
        blockers.append("claim-audit-limitations-not-preserved")
    return {
        "paper_id": contract.paper_id,
        "pass": not blockers,
        "manuscript_ref": manuscript_ref,
        "claimed_ids": sorted(claimed),
        "evidence_bound_claim_ids": sorted(evidence_bound),
        "unsupported_claim_ids_present": sorted(unsupported_present),
        "limitations_preserved": limitations_preserved,
        "blockers": tuple(blockers),
        "scientific_authority": False,
    }


def build_claim_audit_receipt(
    contract: PaperContract,
    *,
    manuscript_ref: str,
    claimed_ids: Sequence[str],
    evidence_bound_claim_ids: Sequence[str],
    unsupported_claim_ids_present: Sequence[str] = (),
    limitations_preserved: bool,
) -> dict[str, Any]:
    result = evaluate_claim_audit(
        contract,
        manuscript_ref=manuscript_ref,
        claimed_ids=claimed_ids,
        evidence_bound_claim_ids=evidence_bound_claim_ids,
        unsupported_claim_ids_present=unsupported_claim_ids_present,
        limitations_preserved=limitations_preserved,
    )
    identity = {
        "paper_id": contract.paper_id,
        "contract_sha256": paper_contract_digest(contract),
        "manuscript_ref": manuscript_ref,
        "claimed_ids": list(result["claimed_ids"]),
        "evidence_bound_claim_ids": list(result["evidence_bound_claim_ids"]),
        "unsupported_claim_ids_present": list(result["unsupported_claim_ids_present"]),
        "limitations_preserved": result["limitations_preserved"],
        "pass": result["pass"],
        "blockers": list(result["blockers"]),
    }
    raw = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": "1.0",
        "receipt_type": "claim-audit",
        **identity,
        "claim_audit_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def evaluate_prebuttal(objections: Sequence[ReviewerObjection], resolutions: Sequence[PrebuttalResolution]) -> dict[str, Any]:
    resolution_by_id = {row.objection_id: row for row in resolutions}
    blockers: list[str] = []
    for objection in objections:
        if not objection.decision_critical:
            continue
        resolution = resolution_by_id.get(objection.objection_id)
        if resolution is None or not resolution.resolved:
            blockers.append(f"unresolved-decision-critical:{objection.objection_id}")
            continue
        if not resolution.evidence_refs:
            blockers.append(f"decision-critical-resolution-missing-evidence:{objection.objection_id}")
    return {
        "pass": not blockers,
        "decision_critical": sum(row.decision_critical for row in objections),
        "blockers": tuple(blockers),
        "scientific_authority": False,
    }


def evaluate_manuscript_ci(checks: Mapping[str, bool]) -> dict[str, Any]:
    missing = tuple(name for name in MANDATORY_MANUSCRIPT_CI_CHECKS if name not in checks)
    failed = tuple(name for name in MANDATORY_MANUSCRIPT_CI_CHECKS if checks.get(name) is False)
    return {
        "pass": not missing and not failed,
        "required": len(MANDATORY_MANUSCRIPT_CI_CHECKS),
        "passed": sum(checks.get(name) is True for name in MANDATORY_MANUSCRIPT_CI_CHECKS),
        "missing": missing,
        "failed": failed,
        "scientific_authority": False,
    }


def evaluate_submission_ready(
    contract: PaperContract,
    manuscript_ci: Mapping[str, Any],
    prebuttal: Mapping[str, Any],
) -> dict[str, Any]:
    blockers = list(contract.blockers())
    if not manuscript_ci.get("pass"):
        blockers.append("manuscript-ci-not-pass")
    if not prebuttal.get("pass"):
        blockers.append("prebuttal-not-pass")
    return {
        "paper_id": contract.paper_id,
        "submission_ready": not blockers,
        "blockers": tuple(dict.fromkeys(blockers)),
        "scientific_authority": False,
        "submission_authority": False,
    }


def build_submission_readiness_receipt(contract: PaperContract, manuscript_ci: Mapping[str, Any], prebuttal: Mapping[str, Any]) -> dict[str, Any]:
    gate = evaluate_submission_ready(contract, manuscript_ci, prebuttal)
    identity = {
        "paper_id": contract.paper_id,
        "contract_sha256": paper_contract_digest(contract),
        "manuscript_ci_pass": manuscript_ci.get("pass") is True,
        "prebuttal_pass": prebuttal.get("pass") is True,
        "submission_ready": gate["submission_ready"],
        "blockers": list(gate["blockers"]),
    }
    raw = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": "1.0",
        "receipt_type": "submission-readiness",
        **identity,
        "receipt_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def paper_phase_experiment_value(
    *,
    information_gain: float,
    scientific_decision_value: float,
    reviewer_risk_reduction: float,
    central_claim_leverage: float,
    cost: float,
) -> float:
    values = (information_gain, scientific_decision_value, reviewer_risk_reduction, central_claim_leverage)
    if cost <= 0:
        raise ValueError("cost must be > 0")
    if any(value < 0 for value in values):
        raise ValueError("paper-phase experiment value inputs must be non-negative")
    return (information_gain * scientific_decision_value * reviewer_risk_reduction * central_claim_leverage) / cost


def build_paper_acceptance_system_state() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "policy": dict(POLICY),
        "paper_states": [state.value for state in PAPER_ACCEPTANCE_FLOW],
        "temporal_keys": list(PAPER_ACCEPTANCE_TEMPORAL_KEYS),
        "mock_review_modes": [mode.value for mode in MockReviewMode],
        "mandatory_manuscript_ci_checks": list(MANDATORY_MANUSCRIPT_CI_CHECKS),
        "review_action_classes": [action.value for action in ReviewActionClass],
        "summary": {
            "paper_states": len(PAPER_ACCEPTANCE_FLOW),
            "mock_review_modes": len(MockReviewMode),
            "mandatory_manuscript_ci_checks": len(MANDATORY_MANUSCRIPT_CI_CHECKS),
            "append_only_ledger": True,
            "automatic_scientific_authority": 0,
            "automatic_experiment_authority": 0,
            "automatic_gpu_authority": 0,
            "automatic_submission_authority": 0,
        },
        "scientific_authority": False,
    }
