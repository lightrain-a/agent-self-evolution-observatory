#!/usr/bin/env python3
"""Build the small public status ledger shared by every frontend page."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.asset_first_stri_public_status import build_asset_first_stri_public_status, validate_asset_first_stri_public_status
from research_pipeline.paper_first_problem_discovery_contract import build_problem_discovery_contract_state
from research_pipeline.paper_first_pre_f0_queue import load_pre_f0_queue
from research_pipeline.paper_first_problem_falsifier_preflight import load_pre_f0_problem_falsifier_preflight

GEN = ROOT / "generated"


def load(name: str) -> dict:
    return json.loads((GEN / name).read_text(encoding="utf-8"))


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


system = load("research-system-state.json")
problem_generator = load("paper-first-problem-generator-state.json")
problem_queue = load("paper-first-problem-gate-queue.json")
pre_f0_queue = load_pre_f0_queue()
pre_f0_support = load_pre_f0_problem_falsifier_preflight()
discovery_contract = build_problem_discovery_contract_state()
paper_backlog = load("paper-first-paper-design-backlog.json")
p0_ledger = load("p0-decision-ledger.json")
program_final = load("persistent-updater-program-final.json")
shadow = load("paper-first-search-portfolio-design-adjudication.json")
sp15 = load("paper-first-sp15-identifiability-support.json")
pf1 = load("paper-first-pf1-problem-adjudication.json")
pf2 = load("paper-first-pf2-method-adjudication.json")
pf357 = load("paper-first-pf357-problem-adjudication.json")
stri = load("asset-first-stri-iclr2027-final-state-20260816.json")
paper_quality = load("asset-first-stri-paper-quality-v2-20260816.json")
stri_p0a = load("asset-first-stri-p0a-host52-execution-state-20260816.json")
stri_p0d_review = load("asset-first-stri-skillrl-fixed-task-p0d-review-20260816.json")
stri_p0d_dead_end = load("asset-first-stri-skillrl-p0d-dead-end-diagnosis-20260816.json")
stri_p0e_principle = load("asset-first-stri-skillrl-final-policy-p0e-principle-disposition-20260817.json")
stri_p0e_diagnosis = load("asset-first-stri-skillrl-final-policy-p0e-qualified-stop-diagnosis-20260817.json")
support_release = load("paper-first-support-release-targets.json")
fresh_phenomenon = load("paper-first-fresh-phenomenon-portfolio-20260817.json")
shadow_admission = load("paper-first-shadow-search-admission.json")
positive_local = load("positive-residual-memory-local-mechanism-readjudication-20260816.json")
positive_temporal = load("positive-residual-memory-temporal-exposure-principle-readjudication-20260816.json")
positive_treatment = load("positive-residual-memory-treatment-semantics-principle-readjudication-20260816.json")

# STRI is a selected-paper/publication projection with its own content-addressed
# source chain. Do not source it from the broader research-system snapshot: that
# snapshot can intentionally lag unrelated live discovery-control changes.
sys_stri = build_asset_first_stri_public_status()
stri_errors = validate_asset_first_stri_public_status(sys_stri)
if stri_errors:
    raise RuntimeError("invalid STRI public status:\n- " + "\n- ".join(stri_errors))
stri_summary = sys_stri.get("summary", {})
queue_summary = problem_queue.get("summary", {})
backlog_summary = paper_backlog.get("summary", {})
p0_summary = p0_ledger.get("summary", {})
shadow_summary = shadow.get("summary", {})
sp15_summary = sp15.get("summary", {})
quality_debt = paper_quality.get("evidence_debt", {})
shadow_admission_summary = shadow_admission.get("summary", {})
fresh_phenomenon_summary = fresh_phenomenon.get("summary", {})
generator_summary = problem_generator.get("summary", {})
generator_policy = problem_generator.get("policy", {})
pre_f0_summary = pre_f0_queue.get("summary", {})
pre_f0_support_summary = pre_f0_support.get("summary", {})
discovery_policy = discovery_contract.get("policy", {})

shadow_rows = []
for row in shadow.get("rows", []):
    shadow_rows.append({
        "id": row.get("id"),
        "title": row.get("shadow_candidate_title") or row.get("original_problem"),
        "status": row.get("paper_problem_status"),
        "verdict": row.get("verdict"),
        "next_action": row.get("next_action"),
        "live_paper_design_eligible": bool(row.get("live_paper_design_eligible", False)),
        "method_design_authorized": bool(row.get("method_design_authorized", False)),
    })

shadow_closed_rows = []
shadow_memory = shadow.get("shadow_search_memory") or shadow.get("shadow_dead_end_memory") or {}
for row in (shadow_memory.get("closed_objects") or shadow_memory.get("blocked_objects") or []):
    if not isinstance(row, dict):
        continue
    shadow_closed_rows.append({
        "candidate_id": row.get("source_candidate_id"),
        "title": row.get("title") or row.get("problem_text") or row.get("source_candidate_id"),
        "closure_layer": row.get("closure_layer"),
        "failure_layer": row.get("failure_layer"),
        "memory_class": row.get("memory_class"),
        "source_stop_class": row.get("source_stop_class"),
        "reason": row.get("reason"),
        "strongest_reduction": row.get("strongest_reduction"),
        "reopen_only_if": row.get("reopen_only_if"),
        "experiment_run_for_this_readjudication": bool(row.get("experiment_run_for_this_readjudication", False)),
        "experiment_alone_authorizes_closure": bool(row.get("experiment_alone_authorizes_closure", False)),
        "principle_update_allowed": bool(row.get("principle_update_allowed", False)),
        "broader_core_principle_falsified": bool(row.get("broader_core_principle_falsified", False)),
        "source_readjudication_artifact": row.get("source_readjudication_artifact"),
    })

paper_first_terminal = [
    {
        "id": "PF-1",
        "status": pf1.get("paper_problem_status"),
        "decision": pf1.get("decision"),
        "next_action": pf1.get("next_action"),
        "survives_as": (pf1.get("what_survives") or {}).get("scientific_lesson"),
    },
    {
        "id": "PF-2",
        "status": pf2.get("method_status") or pf2.get("paper_problem_status"),
        "decision": pf2.get("decision"),
        "next_action": pf2.get("next_action"),
        "survives_as": (pf2.get("what_survives") or {}).get("problem"),
    },
]
for row in pf357.get("rows", []):
    paper_first_terminal.append({
        "id": row.get("id"),
        "status": row.get("paper_problem_status"),
        "decision": row.get("decision"),
        "next_action": None,
        "survives_as": row.get("surviving_system_role"),
    })

state = {
    "schema_version": "1.0",
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source_revision": git_head(),
    "as_of_date": datetime.now(timezone.utc).date().isoformat(),
    "headline": {
        "paper_ready": int(bool(stri_summary.get("paper_ready"))),
        "paper_quality_hold": int(bool(sys_stri) and not bool(stri_summary.get("paper_quality_v2_passed", False))),
        "paper_quality_evidence_debt": int(stri_summary.get("paper_quality_evidence_debt", 0)),
        "canonical_live_ideas": int(queue_summary.get("paper_design_eligible", 0)),
        "canonical_problem_gate_pass": int(queue_summary.get("passed_problem_gate", 0)),
        "canonical_paper_design_backlog": int(backlog_summary.get("pending_human_paper_design", 0)),
        "idea_search_raw_seeds": int(generator_summary.get("raw_seeds", 0)),
        "idea_search_semantic_unique": int(generator_summary.get("semantic_unique_seeds", 0)),
        "idea_search_evolved_branches": int(generator_summary.get("evolved_branches", 0)),
        "idea_search_reviewer_attacks": int(generator_summary.get("reviewer_attacks", 0)),
        "idea_search_repair_children": int(generator_summary.get("repair_children", 0)),
        "idea_search_pre_f0": int(pre_f0_summary.get("queued", 0)),
        "idea_search_pre_f0_support_ready": int(pre_f0_support_summary.get("support_qualified", 0)),
        "idea_search_pre_f0_support_holds": int(pre_f0_support_summary.get("hold_support_unavailable", 0)),
        "legacy_p0_lifecycle": int(p0_summary.get("active_p0", 0)),
        "legacy_p0_experiment_stopped": int(p0_summary.get("experiment_stopped", 0)),
        "legacy_p0_merged": int(p0_summary.get("experiment_merged", 0)),
        "legacy_p0_upstream_hold": int(p0_summary.get("upstream_hold", 0)),
        "legacy_p0_method_stop": int(p0_summary.get("method_development_stop", 0)),
        "launchable_formal_experiments": int(p0_summary.get("launchable", 0)),
        "shadow_dead_ends": int(shadow_summary.get("shadow_dead_end_objects", 0)),
        "shadow_closed_basins": int(shadow_summary.get("shadow_closed_basins", shadow_summary.get("shadow_dead_end_objects", 0))),
        "shadow_problem_novelty_stops": int(shadow_summary.get("problem_novelty_stops", 0)),
        "shadow_execution_stops": int(shadow_summary.get("execution_stops", 0)),
        "shadow_experiment_identifiability_stops": int(shadow_summary.get("experiment_identifiability_stops", 0)),
        "shadow_optimization_stops": int(shadow_summary.get("optimization_stops", 0)),
        "shadow_operationalization_stops": int(shadow_summary.get("operationalization_stops", 0)),
        "shadow_method_realization_stops": int(shadow_summary.get("method_realization_stops", 0)),
        "shadow_assumption_scope_stops": int(shadow_summary.get("assumption_scope_stops", 0)),
        "shadow_core_principle_stops": int(shadow_summary.get("core_principle_stops", 0)),
        "shadow_broader_core_principle_falsifications": int(shadow_summary.get("broader_core_principle_falsifications", 0)),
        "shadow_core_principle_dead_ends": int(shadow_summary.get("core_principle_dead_ends", 0)),
        "shadow_holds": int(shadow_summary.get("shadow_hold_objects", 0)),
        "shadow_method_ready": int(shadow_summary.get("advance_to_method_design", 0)),
        "shadow_qualification_ready": int(bool(shadow_admission_summary.get("qualification_allowed", False))),
        "fresh_active_f0": int(fresh_phenomenon_summary.get("active_f0", 0)),
        "fresh_design_ready_f0": int(fresh_phenomenon_summary.get("design_ready_f0", 0)),
        "fresh_support_holds": int(fresh_phenomenon_summary.get("hold_support", 0)),
        "fresh_execution_holds": int(fresh_phenomenon_summary.get("hold_execution", 0)),
        "fresh_ready_problem_review": int(fresh_phenomenon_summary.get("ready_for_problem_review", 0)),
        "method_authorized": 0,
        "gpu_authorized": 0,
    },
    "leading_paper_track": {
        "paper_id": sys_stri.get("paper_id", "STRI"),
        "candidate_id": sys_stri.get("candidate_id", "skill-taxonomy-representation-invariance"),
        "title": sys_stri.get("title"),
        "status": sys_stri.get("status"),
        "submission_status": sys_stri.get("submission_status"),
        "stage": paper_quality.get("status"),
        "track": sys_stri.get("track", "ASSET_FIRST_PAPER_QUALITY_REPAIR"),
        "claims_supported": int(stri_summary.get("claims_supported", 0)),
        "claims_total": int(stri_summary.get("claims_total", 0)),
        "qa_passed": int(stri_summary.get("qa_checks_passed", 0)),
        "qa_total": int(stri_summary.get("qa_checks_total", 0)),
        "official_qa_passed": int(stri_summary.get("official_qa_checks_passed", 0)),
        "official_qa_total": int(stri_summary.get("official_qa_checks_total", 0)),
        "main_text_pages": int(stri_summary.get("main_text_pages", 0)),
        "main_text_page_limit": int(stri_summary.get("main_text_page_limit", 0)),
        "supplement_ready": bool(stri_summary.get("supplement_ready", False)),
        "supplement_unit_tests": stri_summary.get("supplement_unit_tests"),
        "human_signoff_pending": bool(stri_summary.get("human_signoff_pending", True)),
        "new_gpu_evidence_required": bool(stri_summary.get("new_gpu_evidence_required", False)),
        "paper_quality_v2_passed": bool(stri_summary.get("paper_quality_v2_passed", False)),
        "paper_quality_content_addressed_completion": bool(stri_summary.get("paper_quality_content_addressed_completion", False)),
        "paper_quality_content_addressed_files": int(stri_summary.get("paper_quality_content_addressed_files", 0)),
        "paper_quality_evidence_debt": int(stri_summary.get("paper_quality_evidence_debt", 0)),
        "paper_quality_missing_ids": list(stri_summary.get("paper_quality_missing_ids", [])),
        "paper_quality_schema_version": (paper_quality.get("quality_contract") or {}).get("schema_version"),
        "paper_quality_visualizations": int(stri_summary.get("paper_quality_visualizations", 0)),
        "paper_quality_main_visualizations": int(stri_summary.get("paper_quality_main_visualizations", 0)),
        "paper_quality_main_visual_roles": list(stri_summary.get("paper_quality_main_visual_roles", [])),
        "paper_visual_figure_qa": (stri.get("visual_evidence") or {}).get("figure_qa"),
        "paper_visual_new_result_figure": (stri.get("visual_evidence") or {}).get("new_result_figure"),
        "paper_quality_interpretation": quality_debt.get("interpretation"),
        "cheap_first": quality_debt.get("cheap_first"),
        "scientific_authority": False,
        "canonical_problem_gate_added": int(stri_summary.get("canonical_problem_gate_pass_added", 0)),
        "downloads": (sys_stri.get("submission_handoff") or {}).get("downloads", {}),
        "deadline_status": (sys_stri.get("submission_handoff") or {}).get("official_source_conflict_status"),
        "official_source_conflict": bool((sys_stri.get("submission_handoff") or {}).get("official_source_conflict", False)),
        "operational_safe_abstract_deadline_aoe": (sys_stri.get("submission_handoff") or {}).get("operational_safe_abstract_deadline_aoe"),
        "operational_safe_full_paper_deadline_aoe": (sys_stri.get("submission_handoff") or {}).get("operational_safe_full_paper_deadline_aoe"),
        "recorded_author_guide_abstract_deadline_aoe": (sys_stri.get("submission_handoff") or {}).get("recorded_author_guide_abstract_deadline_aoe"),
        "recorded_author_guide_full_paper_deadline_aoe": (sys_stri.get("submission_handoff") or {}).get("recorded_author_guide_full_paper_deadline_aoe"),
        "author_membership_freezes_at_abstract_deadline": bool((sys_stri.get("submission_handoff") or {}).get("author_membership_freezes_at_abstract_deadline", False)),
        "title_freezes_at_full_paper_deadline": bool((sys_stri.get("submission_handoff") or {}).get("title_freezes_at_full_paper_deadline", False)),
        "prior_mechanical_submission_state": stri.get("status"),
        "next_action": (
            "Human authors must verify the live ICLR/OpenReview deadline because official ICLR pages currently conflict. Until resolved, operate against the earlier published dates: genuine abstract and frozen author membership by 2026-09-11 AoE; full paper and anonymous supplement by 2026-09-16 AoE. Complete profile/quota/reviewer/dual-submission/ethics/AI-use signoff; do not reopen dynamic P0 or broaden N1-N3."
            if bool((sys_stri.get("submission_handoff") or {}).get("official_source_conflict", False))
            else (stri.get("next_action") or quality_debt.get("cheap_first"))
        ),
        "claim_boundary": sys_stri.get("claim_boundary", {}),
    },
    "idea_search_funnel": {
        "installed_operator_version": discovery_policy.get("discovery_operator_version"),
        "installed_mode": "CANONICAL_DOUBLE_FUNNEL" if bool(discovery_policy.get("canonical_double_funnel_required")) else "LEGACY",
        "next_canonical_transaction_uses_double_funnel": bool(discovery_policy.get("canonical_double_funnel_required")),
        "historical_shadow_portfolio_remains_shadow_only": bool(discovery_policy.get("historical_search_portfolio_remains_shadow_only")),
        "search_primitives": list(discovery_policy.get("search_portfolio_primitives") or []),
        "paperability_axes": dict(discovery_policy.get("paperability_axes") or {}),
        "last_completed_generator_operator_version": generator_policy.get("discovery_operator_version"),
        "last_completed_generator_mode": "CANONICAL_DOUBLE_FUNNEL" if bool(generator_policy.get("search_portfolio_enabled")) else "LEGACY_SINGLE_PASS",
        "last_completed_generator_status": problem_generator.get("status"),
        "last_completed_raw_seeds": int(generator_summary.get("raw_seeds", 0)),
        "last_completed_semantic_unique": int(generator_summary.get("semantic_unique_seeds", 0)),
        "last_completed_evolved_branches": int(generator_summary.get("evolved_branches", 0)),
        "last_completed_reviewer_attacks": int(generator_summary.get("reviewer_attacks", 0)),
        "last_completed_repair_children": int(generator_summary.get("repair_children", 0)),
        "pre_f0_status": pre_f0_queue.get("status"),
        "pre_f0_queued": int(pre_f0_summary.get("queued", 0)),
        "pre_f0_support_status": pre_f0_support.get("status"),
        "pre_f0_support_ready": int(pre_f0_support_summary.get("support_qualified", 0)),
        "pre_f0_support_holds": int(pre_f0_support_summary.get("hold_support_unavailable", 0)),
        "pre_f0_scientific_authority": bool(pre_f0_queue.get("scientific_authority", False)),
        "final_problem_gate_pass": int(queue_summary.get("passed_problem_gate", 0)),
        "exact_reduction_required_before_final_problem_gate": bool(discovery_policy.get("exact_reduction_required_before_final_problem_gate")),
        "principle_reduction_does_not_auto_close_other_axes": bool(discovery_policy.get("principle_reduction_does_not_auto_close_other_paperability_axes")),
        "reviewer_attack_repair_split_enabled": bool(discovery_policy.get("attack_repair_split_before_terminal_review")),
        "scientific_authority": False,
    },
    "canonical_live": {
        "generator_status": problem_generator.get("status"),
        "generator_operator_version": generator_policy.get("discovery_operator_version"),
        "installed_operator_version": discovery_policy.get("discovery_operator_version"),
        "installed_double_funnel": bool(discovery_policy.get("canonical_double_funnel_required")),
        "generated": int(generator_summary.get("generated", 0)),
        "raw_seeds": int(generator_summary.get("raw_seeds", 0)),
        "semantic_unique_seeds": int(generator_summary.get("semantic_unique_seeds", 0)),
        "evolved_branches": int(generator_summary.get("evolved_branches", 0)),
        "reviewer_attacks": int(generator_summary.get("reviewer_attacks", 0)),
        "repair_children": int(generator_summary.get("repair_children", 0)),
        "pre_f0_eligible": int(pre_f0_summary.get("queued", 0)),
        "queue_submitted": int(queue_summary.get("submitted", 0)),
        "problem_gate_pass": int(queue_summary.get("passed_problem_gate", 0)),
        "paper_design_eligible": int(queue_summary.get("paper_design_eligible", 0)),
        "paper_design_backlog": int(backlog_summary.get("pending_human_paper_design", 0)),
        "method_authorized": int(queue_summary.get("method_authorized", 0)),
        "experiment_authorized": int(queue_summary.get("experiment_authorized", 0)),
        "p0_authorized": int(queue_summary.get("p0_authorized", 0)),
        "gpu_authorized": int(backlog_summary.get("gpu_authorized", 0)),
        "note": "The latest completed canonical generator receipt is a v17 double-funnel receipt. Historical Search Portfolio results remain shadow-only and are not retroactively promoted; current Pre-F0 support readiness is reported separately from queue size and from formal Problem-Gate passes.",
    },
    "fresh_phenomenon_portfolio": {
        "status": fresh_phenomenon.get("status"),
        "active_f0": int(fresh_phenomenon_summary.get("active_f0", 0)),
        "design_ready_f0": int(fresh_phenomenon_summary.get("design_ready_f0", 0)),
        "support_holds": int(fresh_phenomenon_summary.get("hold_support", 0)),
        "execution_holds": int(fresh_phenomenon_summary.get("hold_execution", 0)),
        "ready_for_problem_review": int(fresh_phenomenon_summary.get("ready_for_problem_review", 0)),
        "canonical_problem_gate_added": int(fresh_phenomenon_summary.get("canonical_problem_gate_added", 0)),
        "scientific_authority": False,
        "rows": [
            {
                "candidate_id": row.get("candidate_id"),
                "title": row.get("title"),
                "status": row.get("status"),
                "support_status": row.get("support_status"),
                "phenomenon": row.get("phenomenon"),
                "strongest_reduction": row.get("strongest_reduction"),
                "cheapest_falsifier": row.get("cheapest_falsifier"),
                "why_now": row.get("why_now"),
                "stop_class": (row.get("evidence") or {}).get("stop_class"),
                "benchmark_level_dead_end_certified": (row.get("evidence") or {}).get("benchmark_level_dead_end_certified"),
                "historical_child": (row.get("evidence") or {}).get("historical_child") or {},
                "revised_f0_authorized": (row.get("evidence") or {}).get("revised_f0_authorized"),
                "provider_formulation_review_required": (row.get("evidence") or {}).get("provider_formulation_review_required"),
                "f0_design_ready": bool(row.get("f0_design_ready", False)),
                "execution_readiness": row.get("execution_readiness") or {},
                "paper_problem_claimed": bool(row.get("paper_problem_claimed", False)),
            }
            for row in fresh_phenomenon.get("candidates", [])
        ],
    },
    "stri_dynamic_evidence": {
        "p0a": {
            "status": stri_p0a.get("status"),
            "role": "qualification failure asset; neither positive nor negative evidence for the narrow STRI claims",
            "next_action": stri_p0a.get("next_action"),
        },
        "skillrl_p0d": {
            "status": str(stri_p0d_dead_end.get("disposition") or "SUBSTRATE_SUPPORT_FAILURE"),
            "outcome": str((stri_p0d_dead_end.get("evidence") or {}).get("outcome") or "INCONCLUSIVE"),
            "pristine_success": int((stri_p0d_dead_end.get("evidence") or {}).get("pristine_success_count") or 0),
            "role": "historical endpoint-support failure on the SFT warm-start; does not update STRI mechanism belief",
            "scientific_authority": False,
        },
        "skillrl_p0e": {
            "status": str(stri_p0e_principle.get("experimental_realization_disposition") or "UNKNOWN"),
            "experimental_stop_valid": bool(stri_p0e_principle.get("experimental_stop_valid", False)),
            "persistent_principle_dead_end_certified": bool(stri_p0e_principle.get("persistent_principle_dead_end_certified", False)),
            "principle_disposition": str(stri_p0e_principle.get("principle_disposition") or "UNKNOWN"),
            "stage2_locked": bool(stri_p0e_principle.get("stage2_confirmation_locked", True)),
            "new_gpu_authorized": bool(stri_p0e_principle.get("new_gpu_authorized", False)),
            "calibration": dict(stri_p0e_diagnosis.get("qualification") or {}),
            "endpoint_result": dict(stri_p0e_diagnosis.get("endpoint_result") or {}),
            "role": "qualified optional C4 realization negative; does not expand or invalidate N1-N3",
            "scientific_authority": False,
        },
    },
    "shadow_search": {
        "reviewed": int(shadow_summary.get("reviewed", 0)),
        "method_ready": int(shadow_summary.get("advance_to_method_design", 0)),
        "revise_hold": int(shadow_summary.get("revise_paper_problem", 0)),
        "stop_standalone": int(shadow_summary.get("stop_standalone", 0)),
        "dead_end_objects": int(shadow_summary.get("shadow_dead_end_objects", 0)),
        "closed_basins": int(shadow_summary.get("shadow_closed_basins", shadow_summary.get("shadow_dead_end_objects", 0))),
        "problem_novelty_stops": int(shadow_summary.get("problem_novelty_stops", 0)),
        "execution_stops": int(shadow_summary.get("execution_stops", 0)),
        "experiment_identifiability_stops": int(shadow_summary.get("experiment_identifiability_stops", 0)),
        "optimization_stops": int(shadow_summary.get("optimization_stops", 0)),
        "operationalization_stops": int(shadow_summary.get("operationalization_stops", 0)),
        "method_realization_stops": int(shadow_summary.get("method_realization_stops", 0)),
        "assumption_scope_stops": int(shadow_summary.get("assumption_scope_stops", 0)),
        "core_principle_stops": int(shadow_summary.get("core_principle_stops", 0)),
        "broader_core_principle_falsifications": int(shadow_summary.get("broader_core_principle_falsifications", 0)),
        "core_principle_dead_ends": int(shadow_summary.get("core_principle_dead_ends", 0)),
        "principle_readjudication_dead_ends": int(shadow_summary.get("principle_readjudication_dead_ends", 0)),
        "principle_readjudication_closed_basins": int(shadow_summary.get("principle_readjudication_closed_basins", shadow_summary.get("principle_readjudication_dead_ends", 0))),
        "hold_objects": int(shadow_summary.get("shadow_hold_objects", 0)),
        "semantic_holds": int(shadow_summary.get("semantic_hold_objects", 0)),
        "near_miss_holds": int(shadow_summary.get("near_miss_holds", 0)),
        "support_release_holds": int((support_release.get("summary") or {}).get("support_holds", 0)),
        "explicit_release_targets": int((support_release.get("summary") or {}).get("explicit_release_targets", 0)),
        "scientific_authority": False,
        "rows": shadow_rows,
        "closed_rows": shadow_closed_rows,
        "sp15_support": {
            "decision": sp15.get("decision"),
            "support_status": sp15_summary.get("support_status"),
            "stop_class": (sp15.get("support_diagnosis") or {}).get("stop_class"),
            "failure_layer": (sp15.get("support_diagnosis") or {}).get("failure_layer"),
            "failure_subtype": (sp15.get("support_diagnosis") or {}).get("failure_subtype"),
            "principle_dead_end_certified": bool((sp15.get("support_diagnosis") or {}).get("principle_dead_end_certified", False)),
            "principle_update_allowed": bool((sp15.get("support_diagnosis") or {}).get("principle_update_allowed", False)),
            "audited_sources": int(sp15_summary.get("primary_or_author_releases_audited", 0)),
            "query_level_identifiability_units": int(sp15_summary.get("query_level_identifiability_units", 0)),
            "method_design_authorized": int(sp15_summary.get("method_design_authorized", 0)),
        },
        "qualification": {
            "status": shadow_admission.get("status"),
            "operator_version": shadow_admission_summary.get("current_discovery_operator_version"),
            "operator_upgrade_recompile": bool(shadow_admission_summary.get("operator_upgrade_recompile", False)),
            "qualification_allowed": bool(shadow_admission_summary.get("qualification_allowed", False)),
            "automatic_provider_calls_authorized": int(shadow_admission_summary.get("automatic_provider_calls_authorized", 0)),
            "reason": shadow_admission.get("reason"),
            "scope": "global-v13-shadow-control; does not reactivate archived positive-residual assets",
        },
    },
    "positive_residual": {
        "parent_phenomenon_status": (positive_local.get("surviving_parent_phenomenon") and "SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE") or "UNKNOWN",
        "parent_phenomenon": positive_local.get("surviving_parent_phenomenon"),
        "local_mechanism_decision": positive_local.get("decision"),
        "local_admissibility_result": next((row.get("result") for row in positive_local.get("failed_or_insufficient_explanations", []) if row.get("name") == "pre-divergence symbolic memory-consistent admissible-option collapse"), None),
        "temporal_exposure_dead_end": bool(positive_temporal.get("principle_dead_end_certified", False)),
        "temporal_exposure_status": (positive_temporal.get("principle_diagnosis") or {}).get("status"),
        "treatment_semantics_dead_end": bool(positive_treatment.get("principle_dead_end_certified", False)),
        "treatment_semantics_status": "PRINCIPLE_DEAD_END_CERTIFIED" if positive_treatment.get("principle_dead_end_certified", False) else "OPEN",
        "active_mechanism_seed": bool((positive_treatment.get("scientific_interpretation") or {}).get("active_mechanism_seed", False)),
        "next_search_basin": (positive_treatment.get("scientific_interpretation") or {}).get("next_search_basin") or (positive_temporal.get("scientific_interpretation") or {}).get("next_search_basin"),
        "next_search_is_zero_authority": True,
        "shadow_qualification_status": "TERMINAL_NO_ACTIVE_MECHANISM_SEED" if not bool((positive_treatment.get("scientific_interpretation") or {}).get("active_mechanism_seed", False)) else shadow_admission.get("status"),
        "shadow_qualification_allowed": bool(shadow_admission_summary.get("qualification_allowed", False)) and bool((positive_treatment.get("scientific_interpretation") or {}).get("active_mechanism_seed", False)),
        "problem_gate_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
    },
    "legacy_p0": {
        "status": "TERMINAL_LEGACY_PORTFOLIO_NOT_ACTIVE_EXECUTION_QUEUE",
        "program_verdict": program_final.get("verdict"),
        "lifecycle_contracts": int(p0_summary.get("active_p0", 0)),
        "experiment_stopped": int(p0_summary.get("experiment_stopped", 0)),
        "experiment_merged": int(p0_summary.get("experiment_merged", 0)),
        "upstream_hold": int(p0_summary.get("upstream_hold", 0)),
        "method_development_stop": int(p0_summary.get("method_development_stop", 0)),
        "launchable": int(p0_summary.get("launchable", 0)),
        "execution_authorized": int(p0_summary.get("execution_authorized", 0)),
        "note": "P0 lifecycle records are historical frozen contracts. Current decisions are STOP/MERGE/HOLD; none is a launchable formal experiment.",
    },
    "paper_first_terminal": paper_first_terminal,
    "interpretation": {
        "paper_ready_is_not_canonical_problem_gate_pass": True,
        "mechanical_and_format_qa_cannot_substitute_for_paper_quality_v2": True,
        "paper_quality_v2_required_for_submission_ready": True,
        "positive_residual_parent_is_not_new_problem_gate_pass": True,
        "archived_positive_residual_without_active_mechanism_seed_is_not_shadow_qualification": True,
        "global_shadow_operator_upgrade_qualification_is_independent_of_archived_positive_residual_seed": True,
        "p0_lifecycle_is_not_active_execution": True,
        "shadow_hold_is_not_dead_end": True,
        "qualification_failure_is_not_scientific_negative": True,
        "diagnostic_only_artifacts_cannot_create_authority": True,
        "installed_discovery_operator_can_differ_from_last_completed_receipt": True,
        "historical_shadow_portfolio_is_not_retroactively_canonical": True,
        "pre_f0_is_evidence_acquisition_not_problem_gate": True,
        "positive_pre_f0_requires_exact_reduction_recheck": True,
        "principle_reduction_does_not_auto_close_method_empirical_benchmark_theory_system_axes": True,
    },
}

json_path = GEN / "current-research-status.json"
js_path = GEN / "current-research-status.js"
json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
js_path.write_text("window.CURRENT_RESEARCH_STATUS = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print(json_path.relative_to(ROOT))
print(js_path.relative_to(ROOT))
