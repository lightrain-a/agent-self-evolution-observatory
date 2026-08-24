from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings
from .paper_first_primary_evidence import load_private_primary_pool, private_primary_pool_path
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, audit_problem_candidate
from .feynman_socratic_gate import build_feynman_socratic_certificate, audit_feynman_socratic_certificate
from .reproduction_gate import reproduction_from_candidate
from .research_reasoning_layer import attribute_simplification, build_contribution_attribution
from .public_state_redaction import redact_private_paths

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-gate-queue.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-problem-gate-queue.js"
INBOX_ENV = "PAPER_FIRST_PROBLEM_CANDIDATE_INBOX"
AUTO_INBOX_ENV = "PAPER_FIRST_PROBLEM_AUTO_CANDIDATE_INBOX"
PRIMARY_POOL_ENV = "PAPER_FIRST_PRIMARY_EVIDENCE_POOL"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _discovery_root(storage: StorageSettings | None = None) -> Path:
    storage = storage or StorageSettings.from_env()
    return storage.data_root / "paper-first-problem-discovery"


def default_inbox_path(storage: StorageSettings | None = None) -> Path:
    explicit = os.getenv(INBOX_ENV, "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    return _discovery_root(storage) / "candidate-inbox.json"


def default_auto_inbox_path(storage: StorageSettings | None = None) -> Path:
    explicit = os.getenv(AUTO_INBOX_ENV, "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    return _discovery_root(storage) / "auto-candidate-inbox.json"


def default_primary_pool_path(storage: StorageSettings | None = None) -> Path:
    explicit = os.getenv(PRIMARY_POOL_ENV, "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    return private_primary_pool_path(storage)


def load_candidate_inbox(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [], [f"inbox-unreadable:{path.name}:{type(error).__name__}"]
    if not isinstance(payload, dict):
        return [], [f"inbox-root-must-be-object:{path.name}"]
    rows = payload.get("candidates") or []
    if not isinstance(rows, list):
        return [], [f"inbox-candidates-must-be-array:{path.name}"]
    candidates: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"candidate-{index}-must-be-object:{path.name}")
            continue
        copied = dict(row)
        copied["_source_inbox"] = str(path)
        candidates.append(copied)
    return candidates, errors


def _primary_registry(path: Path) -> dict[str, dict[str, Any]]:
    pool = load_private_primary_pool(path)
    if not pool:
        return {}
    registry: dict[str, dict[str, Any]] = {}
    for row in pool.get("records") or []:
        if not isinstance(row, dict) or row.get("primary_source_verified") is not True:
            continue
        ref = str(row.get("ref") or "").strip()
        if ref:
            registry[ref] = row
    return registry


def _candidate_snapshot(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        key: candidate.get(key)
        for key in (
            "candidate_id",
            "title",
            "discovery_lane",
            "source_branch_id",
            "branch_depth",
            "empirical_evidence",
            "lane_evidence",
            "irreducible_object",
            "novelty_category",
            "paperability_axes",
            "paperability_claim",
            "reviewer_attack",
            "reviewer_attack_class",
            "repair_axis",
            "why_attack_no_longer_applies",
            "closest_work",
            "closest_work_distance",
            "closest_work_reproduction",
            "mature_theory_baselines",
            "reduction_falsifiability_contract",
            "same_information_nonreducibility",
            "exact_prediction",
            "strongest_same_information_baseline",
            "domain_transfer_audit",
            "saturation_scan",
            "semantic_reduction_review",
            "cheapest_problem_falsifier",
            "endpoint_headroom_requirement",
            "importance",
            "likely_iclr_story",
            "primary_contribution_type",
            "problem_importance",
            "under_explained_observation",
            "missing_insight",
            "minimal_decisive_test",
            "minimal_sufficient_intervention",
            "insight_predictions",
            "contribution_attribution",
            "simplification_attribution_evidence",
        )
    }


def _count_by_lane(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {lane: 0 for lane in DISCOVERY_LANES}
    counts["OTHER"] = 0
    for row in rows:
        lane = str(row.get("discovery_lane") or "").strip().upper()
        counts[lane if lane in counts else "OTHER"] += 1
    return counts


def build_problem_gate_queue(
    inbox_path: Path | None = None,
    *,
    auto_inbox_path: Path | None = None,
    primary_pool_path: Path | None = None,
    storage: StorageSettings | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    manual_source = inbox_path or default_inbox_path(storage)
    auto_source = auto_inbox_path or default_auto_inbox_path(storage)
    primary_source = primary_pool_path or default_primary_pool_path(storage)
    sources: list[Path] = []
    for source in (manual_source, auto_source):
        if source not in sources:
            sources.append(source)

    candidates: list[dict[str, Any]] = []
    inbox_errors: list[str] = []
    for source in sources:
        rows, errors = load_candidate_inbox(source)
        candidates.extend(rows)
        inbox_errors.extend(errors)
    registry = _primary_registry(primary_source)

    audited: list[dict[str, Any]] = []
    passed: list[dict[str, Any]] = []
    seen: set[str] = set()
    duplicate_ids: list[str] = []

    for index, candidate in enumerate(candidates):
        cid = str(candidate.get("candidate_id") or f"candidate-{index}")
        if cid in seen:
            duplicate_ids.append(cid)
        seen.add(cid)
        feynman_certificate = build_feynman_socratic_certificate(candidate)
        feynman_audit = audit_feynman_socratic_certificate(feynman_certificate)
        reproduction_contract, reproduction_audit = reproduction_from_candidate(candidate)
        contribution_attribution = build_contribution_attribution(candidate)
        simplification_spec = candidate.get("simplification_attribution_evidence") if isinstance(candidate.get("simplification_attribution_evidence"), dict) else {}
        if contribution_attribution.get("status") == "ATTRIBUTION_COMPLETE" and simplification_spec.get("reproduced_layers"):
            simplification_attribution = attribute_simplification(
                primary_contribution_type=str(contribution_attribution.get("primary_contribution_type") or ""),
                claimed_layers=contribution_attribution.get("claimed_layers") or [],
                reproduced_layers=simplification_spec.get("reproduced_layers") or [],
                baseline_ref=str(simplification_spec.get("baseline_ref") or ""),
                same_information=simplification_spec.get("same_information") is True,
            )
        else:
            simplification_attribution = {
                "schema_version": "1.0",
                "status": "SIMPLIFICATION_ATTRIBUTION_NOT_YET_EVALUABLE",
                "whole_paper_stop_authorized": False,
                "scientific_authority": False,
                "paper_authority": False,
            }
        audit = audit_problem_candidate(
            candidate,
            primary_evidence_by_ref=registry,
            require_primary_registry=True,
        )
        pre_problem_blockers: list[str] = []
        if feynman_audit.get("status") != "CLEAR_FOR_PROBLEM_GATE_REVIEW":
            pre_problem_blockers.append(
                "feynman-socratic-mature-reduction-alert"
                if feynman_audit.get("status") == "MATURE_REDUCTION_ALERT"
                else "feynman-socratic-certificate-incomplete"
            )
        if reproduction_audit.get("required_for_problem_qualification") is True and reproduction_audit.get("qualification_satisfied") is not True:
            pre_problem_blockers.append(
                "closest-work-reproduction-support-hold"
                if reproduction_audit.get("support_hold") is True
                else "closest-work-reproduction-required"
            )
        if pre_problem_blockers:
            audit = dict(audit)
            audit["passed"] = False
            audit["status"] = "PROBLEM_GATE_BLOCKED"
            audit["blockers"] = sorted(set(list(audit.get("blockers") or []) + pre_problem_blockers))
        contribution_shadow = {
            "schema_version": "1.0",
            "current_problem_gate_status": str(audit.get("status") or ""),
            "current_problem_gate_passed": audit.get("passed") is True,
            "contribution_attribution": contribution_attribution,
            "simplification_attribution": simplification_attribution,
            "eventual_problem_gate": "PENDING_OR_CURRENT_ONLY",
            "eventual_closest_work": "PENDING",
            "eventual_paper_survival": "PENDING",
            "live_problem_gate_mutated": False,
            "scientific_authority": False,
            "paper_authority": False,
        }
        snapshot = _candidate_snapshot(candidate)
        row = {
            "candidate_id": cid,
            "title": str(candidate.get("title") or ""),
            "discovery_lane": str(candidate.get("discovery_lane") or "").strip().upper(),
            "source_inbox": str(candidate.get("_source_inbox") or ""),
            "candidate": snapshot,
            "feynman_socratic": {"certificate": feynman_certificate, "audit": feynman_audit},
            "closest_work_reproduction": {"contract": reproduction_contract, "audit": reproduction_audit},
            "contribution_shadow": contribution_shadow,
            "audit": audit,
            "paper_design_eligible": bool(audit.get("passed")),
            "authority": {
                "method_design": False,
                "experiment_blueprint": False,
                "local_validation": False,
                "p0": False,
                "gpu": False,
                "full_experiment": False,
            },
        }
        audited.append(row)
        if audit.get("passed"):
            passed.append({
                "candidate_id": cid,
                "title": row["title"],
                "discovery_lane": row["discovery_lane"],
                "status": "AWAIT_HUMAN_PAPER_DESIGN_REVIEW",
                "paper_design_eligible": True,
                "source_inbox": row["source_inbox"],
                "candidate": snapshot,
                "feynman_socratic": {"certificate": feynman_certificate, "audit": feynman_audit},
                "closest_work_reproduction": {"contract": reproduction_contract, "audit": reproduction_audit},
                "contribution_shadow": contribution_shadow,
            })

    if duplicate_ids:
        duplicates = set(duplicate_ids)
        inbox_errors.append("duplicate-candidate-ids:" + ",".join(sorted(duplicates)))
        passed = [row for row in passed if row["candidate_id"] not in duplicates]
        for row in audited:
            if row["candidate_id"] in duplicates:
                row["paper_design_eligible"] = False
                row["audit"]["passed"] = False
                row["audit"]["status"] = "PROBLEM_GATE_BLOCKED"
                row["audit"]["blockers"] = sorted(set(list(row["audit"].get("blockers") or []) + ["duplicate-candidate-id"]))

    passed_ids = {row["candidate_id"] for row in passed}
    blocked = [
        {
            "candidate_id": row["candidate_id"],
            "title": row["title"],
            "discovery_lane": row["discovery_lane"],
            "status": "PROBLEM_GATE_BLOCKED",
            "source_inbox": row["source_inbox"],
            "blockers": list(row["audit"].get("blockers") or []),
        }
        for row in audited
        if row["candidate_id"] not in passed_ids
    ]

    return {
        "schema_version": "2.0",
        "generated_at": _now(),
        "source_inbox": str(manual_source),
        "source_inboxes": [str(path) for path in sources],
        "primary_evidence_pool": str(primary_source),
        "primary_evidence_records": len(registry),
        "source_exists": any(path.exists() for path in sources),
        "policy": {
            "candidate_inbox_is_not_authority": True,
            "manual_and_auto_inboxes_are_merged": True,
            "verified_primary_evidence_registry_required_for_submitted_candidates": True,
            "multi_lane_candidate_schema_required": True,
            "lane_contract_independent_review_required": True,
            "independent_semantic_reduction_review_required": True,
            "semantic_reviewer_is_block_only": True,
            "feynman_socratic_certificate_required_before_problem_gate": True,
            "feynman_socratic_gate_is_zero_authority": True,
            "feynman_socratic_mature_reduction_alert_only_uses_typed_existing_review": True,
            "problem_insight_certificate_runs_in_shadow_and_does_not_change_live_problem_gate_authority_yet": True,
            "contribution_attribution_shadow_is_recorded_before_any_future_live-gate migration": True,
            "prospective_shadow_records_current_verdict_and_waits_for_eventual_closest_work_and_paper_survival": True,
            "shadow_simplification_attribution_cannot_mutate_live_problem_gate": True,
            "closest_work_reproduction_required_only_when_implementation_is_decisive": True,
            "missing_source_faithful_reproduction_assets_is_support_hold_not_scientific_negative": True,
            "all_candidates_require_problem_gate": True,
            "problem_gate_pass_only_grants_human_paper_design_eligibility": True,
            "old_solution_first_discovery_is_archival_input_only": True,
            "zero_candidates_or_zero_passes_is_valid": True,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
        },
        "summary": {
            "submitted": len(candidates),
            "audited": len(audited),
            "passed_problem_gate": len(passed),
            "blocked_problem_gate": len(blocked),
            "paper_design_eligible": len(passed),
            "inbox_errors": len(inbox_errors),
            "primary_evidence_records": len(registry),
            "feynman_socratic_clear": sum((row.get("feynman_socratic") or {}).get("audit", {}).get("status") == "CLEAR_FOR_PROBLEM_GATE_REVIEW" for row in audited),
            "feynman_socratic_revise": sum((row.get("feynman_socratic") or {}).get("audit", {}).get("status") == "REVISE_CERTIFICATE" for row in audited),
            "feynman_socratic_reduction_alert": sum((row.get("feynman_socratic") or {}).get("audit", {}).get("status") == "MATURE_REDUCTION_ALERT" for row in audited),
            "reproduction_required": sum((row.get("closest_work_reproduction") or {}).get("audit", {}).get("required_for_problem_qualification") is True for row in audited),
            "reproduction_qualified": sum((row.get("closest_work_reproduction") or {}).get("audit", {}).get("required_for_problem_qualification") is True and (row.get("closest_work_reproduction") or {}).get("audit", {}).get("qualification_satisfied") is True for row in audited),
            "reproduction_support_holds": sum((row.get("closest_work_reproduction") or {}).get("audit", {}).get("support_hold") is True for row in audited),
            "contribution_shadow_complete": sum((row.get("contribution_shadow") or {}).get("contribution_attribution", {}).get("status") == "ATTRIBUTION_COMPLETE" for row in audited),
            "simplification_attribution_shadow_evaluable": sum((row.get("contribution_shadow") or {}).get("simplification_attribution", {}).get("status") != "SIMPLIFICATION_ATTRIBUTION_NOT_YET_EVALUABLE" for row in audited),
            "shadow_live_problem_gate_mutations": sum((row.get("contribution_shadow") or {}).get("live_problem_gate_mutated") is True for row in audited),
            "submitted_by_lane": _count_by_lane(candidates),
            "passed_by_lane": _count_by_lane(passed),
            "blocked_by_lane": _count_by_lane(blocked),
            "method_authorized": 0,
            "experiment_authorized": 0,
            "p0_authorized": 0,
        },
        "inbox_errors": inbox_errors,
        "passed": passed,
        "blocked": blocked,
        "audited": audited,
        "next_action": "Human Paper Design review may inspect passed candidates. Blocked, stale, malformed, or missing candidates do not create a paper, method, experiment, or P0 lifecycle entry.",
    }


def load_problem_gate_queue_state(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    """Load the frozen public queue snapshot without re-reading host-private inboxes."""
    if not path.exists():
        return {
            "schema_version": "2.0",
            "status": "NOT_RUN",
            "policy": {
                "candidate_inbox_is_not_authority": True,
                "all_candidates_require_problem_gate": True,
                "problem_gate_pass_only_grants_human_paper_design_eligibility": True,
                "automatic_method_authority": False,
                "automatic_experiment_authority": False,
                "automatic_p0_authority": False,
            },
            "summary": {
                "submitted": 0, "audited": 0, "passed_problem_gate": 0, "blocked_problem_gate": 0,
                "paper_design_eligible": 0, "inbox_errors": 0, "primary_evidence_records": 0,
                "submitted_by_lane": _count_by_lane([]), "passed_by_lane": _count_by_lane([]), "blocked_by_lane": _count_by_lane([]),
                "method_authorized": 0, "experiment_authorized": 0, "p0_authorized": 0,
            },
            "inbox_errors": [], "passed": [], "blocked": [], "audited": [],
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "schema_version": "2.0", "status": "STATE_UNREADABLE", "policy": {},
            "summary": {"submitted": 0, "audited": 0, "passed_problem_gate": 0, "blocked_problem_gate": 0, "paper_design_eligible": 0, "inbox_errors": 1, "primary_evidence_records": 0, "method_authorized": 0, "experiment_authorized": 0, "p0_authorized": 0},
            "inbox_errors": ["state-unreadable"], "passed": [], "blocked": [], "audited": [],
        }
    return payload if isinstance(payload, dict) else {"schema_version": "2.0", "status": "STATE_INVALID", "policy": {}, "summary": {}, "passed": [], "blocked": [], "audited": []}


def write_problem_gate_queue(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
    *,
    inbox_path: Path | None = None,
    auto_inbox_path: Path | None = None,
    primary_pool_path: Path | None = None,
    storage: StorageSettings | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    state = build_problem_gate_queue(
        inbox_path,
        auto_inbox_path=auto_inbox_path,
        primary_pool_path=primary_pool_path,
        storage=storage,
    )
    public_state = redact_private_paths(state, storage=storage)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(public_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PROBLEM_GATE_QUEUE = " + json.dumps(public_state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_problem_gate_queue(), ensure_ascii=False))
