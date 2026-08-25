from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from research_pipeline.config import PROJECT_ROOT
from research_pipeline.paper_first_evidence_acquisition import _plan_status, _sha, _summary, validate_evidence_plan
from research_pipeline.paper_first_pre_f0_evidence_control import _public_state, _write_public, control_snapshot
from research_pipeline.paper_first_discovery_frontier import build_paper_first_discovery_frontier

BASELINE_COMMIT = "4d35da10a24c93dfa94eabf65f6c84dc99ae0ac4"
CANDIDATE_ID = "PORT-010"
EXPECTED_DATASET_REVISION = "2e152f9f0d082066bb6bc1f8d72809581e664709"
EXPECTED_OLD_REOPEN_RECEIPT = "1a28718e1931e08828326e19d290e1b98df4bd4271dd22ad2ad98c3e1701901e"
PLAN = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"
PUBLIC_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-state.json"
PUBLIC_JS = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-state.js"
QUEUE = PROJECT_ROOT / "generated" / "paper-first-pre-f0-queue.json"
SUPPORT = PROJECT_ROOT / "generated" / "paper-first-pre-f0-problem-falsifier-preflight.json"
RESEARCH_SYSTEM_JSON = PROJECT_ROOT / "generated" / "research-system-state.json"
RESEARCH_SYSTEM_JS = PROJECT_ROOT / "generated" / "research-system-state.js"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def historical_row() -> dict:
    raw = subprocess.check_output([
        "git", "show", f"{BASELINE_COMMIT}:generated/paper-first-pre-f0-evidence-acquisition-plan.json"
    ], cwd=PROJECT_ROOT)
    payload = json.loads(raw)
    return deepcopy(next(row for row in payload["entries"] if row.get("candidate_id") == CANDIDATE_ID))



def project_into_research_system(public: dict) -> None:
    """Update only Pre-F0-derived fields in the persisted composite snapshot."""
    state = json.loads(RESEARCH_SYSTEM_JSON.read_text(encoding="utf-8"))
    state["paper_first_pre_f0_evidence_acquisition"] = deepcopy(public)

    summary = state.get("summary") or {}
    ps = public.get("summary") or {}
    summary.update({
        "paper_first_pre_f0_evidence_status": public.get("status", "NOT_RUN"),
        "paper_first_pre_f0_evidence_candidates": int(ps.get("provisional_problem_candidates") or 0),
        "paper_first_pre_f0_evidence_execution_ready": int(ps.get("execution_ready") or 0),
        "paper_first_pre_f0_evidence_execution_completed": int(ps.get("execution_completed") or 0),
        "paper_first_pre_f0_evidence_reduction_supported": int(ps.get("reduction_supported") or 0),
        "paper_first_pre_f0_evidence_residual_survives": int(ps.get("residual_survives") or 0),
        "paper_first_pre_f0_evidence_inconclusive": int(ps.get("inconclusive") or 0),
    })
    state["summary"] = summary

    old_frontier = state.get("paper_first_discovery_frontier") or {}
    frontier_time = datetime.fromisoformat(str(old_frontier.get("generated_at"))) if old_frontier.get("generated_at") else None
    frontier = build_paper_first_discovery_frontier(
        primary_state=state.get("paper_first_primary_evidence") or {},
        generator_state=state.get("paper_first_problem_generator") or {},
        queue_state=state.get("paper_first_problem_gate_queue") or {},
        relation_freshness_state=state.get("paper_first_global_relation_freshness") or {},
        relation_admission_state=state.get("paper_first_global_relation_scan_admission") or {},
        shadow_admission_state=state.get("paper_first_shadow_search_admission") or {},
        object_candidate_state=state.get("paper_first_scientific_object_candidate_evidence") or {},
        support_release_watch_state=state.get("paper_first_support_release_watch") or {},
        support_asset_recheck_state=state.get("paper_first_support_asset_recheck") or {},
        shadow_portfolio_state=state.get("paper_first_problem_search_portfolio") or {},
        evidence_migration_state=state.get("paper_first_evidence_migration") or {},
        pre_f0_evidence_state=public,
        now=frontier_time,
    )
    state["paper_first_discovery_frontier"] = frontier
    fs = frontier.get("summary") or {}
    summary.update({
        "paper_first_discovery_frontier_status": frontier.get("status", "WAIT_EXTERNAL_EVIDENCE_TRIGGERS"),
        "paper_first_discovery_frontier_open_internal": int(fs.get("open_internal_frontiers") or 0),
        "paper_first_discovery_frontier_external_triggers": int(fs.get("external_triggers") or 0),
        "paper_first_discovery_frontier_model_calls": int(fs.get("automatic_model_calls_authorized") or 0),
        "paper_first_discovery_frontier_evidence_open": int(fs.get("evidence_internal_open") or 0),
    })

    for check in state.get("health_checks") or []:
        if isinstance(check, dict) and check.get("key") == "paper-first-discovery-frontier":
            check["pass"] = True
            check["detail"] = {"status": frontier.get("status"), "summary": fs, "blockers": frontier.get("blockers") or []}

    RESEARCH_SYSTEM_JSON.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RESEARCH_SYSTEM_JS.write_text("window.RESEARCH_SYSTEM_STATE = " + json.dumps(state, ensure_ascii=False, separators=(",",":")) + ";\n", encoding="utf-8")

def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    idx = next(i for i, row in enumerate(plan["entries"]) if row.get("candidate_id") == CANDIDATE_ID)
    current = deepcopy(plan["entries"][idx])
    current_receipt = deepcopy(current.get("primary_asset_release_receipt") or {})
    if current.get("status") == "HOLD_EVIDENCE_REVIEW_BLOCKED" and current_receipt.get("reopen_scope") == "RELEASE_CHANGE_AUDIT_ONLY":
        public = json.loads(PUBLIC_JSON.read_text(encoding="utf-8"))
        project_into_research_system(public)
        print("PORT-010 release-change HOLD reconciliation already applied; composite projection refreshed")
        return
    if current.get("status") != "NEEDS_BOUNDED_EVIDENCE_DESIGN":
        raise SystemExit(f"unexpected current PORT-010 status: {current.get('status')}")
    if current_receipt.get("authoritative_revision") != EXPECTED_DATASET_REVISION:
        raise SystemExit("unexpected VWE-Bench revision in current release receipt")
    if current_receipt.get("receipt_sha256") != EXPECTED_OLD_REOPEN_RECEIPT:
        raise SystemExit("unexpected historical reopen receipt digest")
    missing = " ".join(current_receipt.get("remaining_missing_requirements") or []).lower()
    if "outcome" not in missing and "pass@1" not in missing:
        raise SystemExit("current receipt no longer declares the missing outcome blocker")

    restored = historical_row()
    if restored.get("status") != "HOLD_EVIDENCE_REVIEW_BLOCKED":
        raise SystemExit("baseline PORT-010 is not the expected HOLD state")
    if (restored.get("evidence_review") or {}).get("verdict") != "BLOCK_BAKE_IN":
        raise SystemExit("baseline PORT-010 is not bound to BLOCK_BAKE_IN")

    # Preserve the historical erroneous reopen as provenance; do not erase it.
    restored["primary_asset_release_reopen_history"] = deepcopy(current.get("primary_asset_release_reopen_history") or [])
    restored["primary_asset_release_reopen_count"] = int(current.get("primary_asset_release_reopen_count") or 0)
    restored["primary_asset_release_effective_reopen_count"] = 0

    audit_receipt = deepcopy(current_receipt)
    audit_receipt.pop("receipt_sha256", None)
    audit_receipt["release_change_detected"] = True
    audit_receipt["qualifying_outcome_artifact"] = False
    audit_receipt["required_reopen_components"] = ["query_units", "per_case_outcomes"]
    audit_receipt["materialized_reopen_components"] = ["query_units"]
    audit_receipt["remaining_reopen_blockers"] = ["per_case_outcomes"]
    audit_receipt["reopen_scope"] = "RELEASE_CHANGE_AUDIT_ONLY"
    audit_receipt["scientific_authority"] = False
    audit_receipt["execution_authority"] = False
    audit_receipt["transport_is_authority"] = False
    audit_receipt["receipt_sha256"] = _sha(audit_receipt)
    restored["primary_asset_release_receipt"] = audit_receipt
    restored["primary_asset_release_audit_count"] = 1
    restored["primary_asset_release_audit_history"] = [{
        "audited_at": now(),
        "release_receipt": deepcopy(audit_receipt),
        "invalidated_reopen_receipt_sha256": EXPECTED_OLD_REOPEN_RECEIPT,
        "preserved_status": "HOLD_EVIDENCE_REVIEW_BLOCKED",
        "preserved_contract_sha256": restored.get("contract_sha256"),
        "reason": "VWE-Bench released query metadata are materialized, but no author-released per-case target-model Pass@1/outcome artifact or sufficient original trajectory is present. The frozen reopen_only_if condition therefore remains unsatisfied.",
        "scientific_authority": False,
    }]
    restored["release_change_feedback"] = "Metadata release is provenance-bearing support, not a qualifying outcome release. PORT-010 remains HOLD; self-generated main.py/eval.py outcomes cannot be represented as author-released evidence."
    restored["release_change_adjudication"] = {
        "release_change_detected": True,
        "qualifying_author_outcome_artifact": False,
        "reopen_condition_satisfied": False,
        "required_reopen_components": ["query_units", "per_case_outcomes"],
        "materialized_reopen_components": ["query_units"],
        "remaining_reopen_components": ["per_case_outcomes"],
        "effective_status": "HOLD_EVIDENCE_REVIEW_BLOCKED",
        "offline_replay_tier_authorized": False,
        "provider_authority": False,
        "gpu_authority": False,
        "scientific_execution_authority": False,
        "local_rollout_as_author_outcome": "PROHIBITED",
        "authority_class": "ZERO_AUTHORITY",
        "scientific_authority": False,
    }

    plan["entries"][idx] = restored
    plan.setdefault("policy", {})["release_change_without_reopen_condition_stays_hold"] = True
    plan["generated_at"] = now()
    plan["summary"] = _summary(plan["entries"])
    plan["status"] = _plan_status(plan["entries"])
    errors = validate_evidence_plan(plan)
    if errors:
        raise SystemExit("reconciled plan invalid: " + ";".join(errors))
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    previous_public = json.loads(PUBLIC_JSON.read_text(encoding="utf-8"))
    control = control_snapshot(queue_path=QUEUE, support_path=SUPPORT, plan_path=PLAN)
    stage = {
        "stage": "release-change-adjudication",
        "candidate_ids": [CANDIDATE_ID],
        "provider_calls_executed": 0,
        "scientific_authority": False,
    }
    public = _public_state(plan=plan, control=control, last_stage=stage)
    public["parent_control_snapshot_sha256"] = str(previous_public.get("control_snapshot_sha256") or "")
    _write_public(public, PUBLIC_JSON, PUBLIC_JS)
    project_into_research_system(public)
    print(json.dumps({
        "candidate_id": CANDIDATE_ID,
        "status": restored["status"],
        "plan_status": plan["status"],
        "release_scope": audit_receipt["reopen_scope"],
        "qualifying_outcome_artifact": audit_receipt["qualifying_outcome_artifact"],
        "receipt_sha256": audit_receipt["receipt_sha256"],
        "control_snapshot_sha256": public["control_snapshot_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
