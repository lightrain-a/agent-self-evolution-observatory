#!/usr/bin/env python3
"""Static integrity checks for the consolidated Agent Self-Evolution Observatory."""
from __future__ import annotations

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from research_pipeline.public_projection_invariants import validate_public_control_plane

ROOT = Path(__file__).resolve().parent
CANONICAL_PAGES = {
    "index.html": "home",
    "foundations.html": "foundations",
    "mechanisms.html": "mechanisms",
    "system-overview.html": "system-overview",
    "research-map.html": "research-map",
    "research-timeline.html": "research-timeline",
    "research-map.html": "research-map",
    "research-directions.html": "research-directions",
    "paper-ideas.html": "paper-ideas",
    "experiments.html": "experiments",
    "selected-paper.html": "selected-paper",
    "bibliography.html": "bibliography",
}
REDIRECT_PAGES = {
    "taxonomy.html": "foundations.html#group-taxonomy",
    "model-improvement.html": "mechanisms.html#field-model-parameters",
    "prompt-evolution.html": "mechanisms.html#field-prompt-policy",
    "memory-evolution.html": "mechanisms.html#field-memory",
    "tool-evolution.html": "mechanisms.html#field-skill-tool",
    "workflow-evolution.html": "mechanisms.html#field-workflow",
    "domains.html": "mechanisms.html#chapter-domain-axis",
    "visual-multimodal.html": "mechanisms.html#field-multimodal",
    "gui-web.html": "mechanisms.html#field-gui-web",
    "embodied-world.html": "mechanisms.html#field-embodied",
    "evaluation.html": "mechanisms.html#chapter-evidence-axis",
    "evaluation-safety.html": "mechanisms.html#field-evaluation-safety",
    "datasets-benchmarks.html": "mechanisms.html#field-datasets-benchmarks",
    "repositories.html": "mechanisms.html#field-repositories",
    "coverage-method.html": "bibliography.html#group-coverage-method",
    "research-agenda.html": "research-directions.html#group-research-agenda",
    "direction-board.html": "paper-ideas.html#discussed-ideas",
    "paper-problem.html": "selected-paper.html#group-paper-problem",
    "paper-experiments.html": "selected-paper.html#group-paper-experiments",
    "paper-roadmap.html": "selected-paper.html#group-paper-roadmap",
    "review-log.html": "selected-paper.html#group-review-log",
}
REQUIRED_STATIC = [
    "CNAME", "_config.yml", ".gitignore", "style.css", "app.js", "data.js",
    "content-consolidated.js", "redirect.js", "favicon.svg", "robots.txt",
    "sitemap.xml", "site.webmanifest", "404.html", "knowledge-map.svg",
    "agent-self-evolution-directions-en.svg", "agent-self-evolution-directions-zh.svg",
    "agent-self-evolution-history-en.svg", "agent-self-evolution-history-zh.svg",
    "portfolio-data.js", "direction-guide-data.js", "direction-literature-data.js", "page-architecture-data.js", "idea-explanations.js", "idea-comparisons.js",
    "paper-analysis-data.js", "top-paper-analysis-data.js", "published-literature-data.js", "citation-ranking-data.js", "paper-novelty-audit-data.js", "paper-external-review-data.js",
    "literature-idea-mining-data-1.js", "literature-idea-mining-data-2.js", "literature-idea-mining-data-3.js", "literature-idea-mining-data.json",
    "history-figure-data.js", "catalog_audit.py", "build_citation_cache.py", "scripts/build_literature_idea_mining_input.py",
    "browser_smoke_test.py", "hierarchy_smoke_test.py", "CHANGELOG.md",
    "content-review-external.js", "generated/iclr-external-reviews.json",
    "machine-school-ideas-view.js", "generated/machine-school-inspired-ideas.json",
    "generated/machine-school-inspired-ideas.js", "generated/machine-school-external-reviews.json",
    "review-localizations.js", "discussion-ready-view.js", "idea-discovery-v5-view.js", "idea-discovery-v4-view.js", "solution-first-ideas-view.js",
    "generated/discussion-ready-ideas.json", "generated/discussion-ready-ideas.js",
    "generated/idea-discovery-v5.json", "generated/idea-discovery-v5.js", "generated/idea-discovery-v5-external-reviews.json",
    "generated/idea-discovery-v51.json", "generated/idea-discovery-v51.js", "generated/idea-discovery-v51-external-reviews.json",
    "generated/idea-discovery-v52.json", "generated/idea-discovery-v52.js", "generated/idea-discovery-v52-external-reviews.json",
    "generated/idea-discovery-v53.json", "generated/idea-discovery-v53.js", "generated/idea-discovery-v53-external-reviews.json",
    "generated/idea-discovery-v4.json", "generated/idea-discovery-v4.js", "generated/idea-discovery-v4-external-reviews.json",
    "generated/idea-discovery-v3.json", "generated/idea-discovery-v3.js", "generated/idea-discovery-v3-external-reviews.json",
    "generated/idea-discovery-v31.json", "generated/idea-discovery-v31.js", "generated/idea-discovery-v31-external-reviews.json",
    "content-system-overview.js", "system-overview-core.js", "system-overview-map.js", "system-overview-layers.js", "system-overview-intake.js", "system-overview-lifecycle.js", "system-overview-reader.js", "system-overview-preflight.js", "system-overview-operations.js", "system-overview-closure.js", "system-overview-view.js", "system-overview.css", "system-overview-v2.css",
    "research-timeline.html", "research-timeline-view.js", "research-timeline.css", "generated/research-timeline.js", "generated/research-timeline.json", "generated/research-dashboard.js", "generated/research-dashboard.json",
    "research-map.html", "research-map-view.js", "research-map.css", "research-landscape-data.js",
    "idea-lab.css",
    "current-research-status-view.js", "generated/current-research-status.json", "generated/current-research-status.js",
    "generated/pre-researchitem-candidates.json", "generated/pre-researchitem-candidates.js",
    "generated/research-items.json", "generated/research-items.js", "generated/paper-registry.json", "generated/paper-registry.js",
    "research_pipeline/research_item_state.py", "research_pipeline/test_research_item_state.py", "scripts/build_research_items.py",
    "generated/research-memory-wiki.json", "generated/research-memory-wiki.js",
    "generated/p0-experiment-plan.js", "generated/p0-collision-recheck.js", "generated/p0-runtime-readiness.js",
]
PLACEHOLDERS = ["PAGE_CHUNKS", "<!--NEXT", "<!--PAPERS", "<!--SCRIPT"]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    for name in REQUIRED_STATIC:
        if not (ROOT / name).exists():
            fail(f"missing required file {name}")

    current_status = json.loads((ROOT / "generated" / "current-research-status.json").read_text(encoding="utf-8"))
    pre_researchitem = json.loads((ROOT / "generated" / "pre-researchitem-candidates.json").read_text(encoding="utf-8"))
    research_system = json.loads((ROOT / "generated" / "research-system-state.json").read_text(encoding="utf-8"))
    research_memory = json.loads((ROOT / "generated" / "research-memory-wiki.json").read_text(encoding="utf-8"))
    research_timeline = json.loads((ROOT / "generated" / "research-timeline.json").read_text(encoding="utf-8"))
    research_items = json.loads((ROOT / "generated" / "research-items.json").read_text(encoding="utf-8"))
    paper_registry = json.loads((ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
    research_dashboard = json.loads((ROOT / "generated" / "research-dashboard.json").read_text(encoding="utf-8"))
    projection_errors = validate_public_control_plane(research_state=research_items, paper_registry=paper_registry, research_system=research_system, research_dashboard=research_dashboard, research_memory=research_memory)
    if projection_errors:
        fail("public control-plane projection invariants failed: " + "; ".join(projection_errors))
    ri_summary = research_items.get("summary") or {}
    if (int(ri_summary.get("research_items") or 0), int(ri_summary.get("experiment_records") or 0), int(ri_summary.get("portfolio_experiment_contexts") or 0), int(ri_summary.get("evidence_contexts") or 0), int(ri_summary.get("portfolio_objects") or 0)) != (88, 30, 3, 2, 93):
        fail(f"canonical ResearchItem projection counts drifted: {ri_summary}")
    if ri_summary.get("parent_scientific_states") != {"HOLD": 4, "MERGED": 6, "STOPPED": 16}:
        fail(f"canonical parent scientific states must be HOLD=4/MERGED=6/STOPPED=16: {ri_summary.get('parent_scientific_states')}")
    if int(ri_summary.get("active_research_items") or 0) != 0 or research_items.get("policy", {}).get("zero_active_research_items_is_valid") is not True or research_items.get("policy", {}).get("visibility_tracking_does_not_create_active_slot") is not True:
        fail(f"canonical ResearchItem registry must explicitly permit and currently expose zero active rows: {ri_summary}")
    expected_category_totals = {"A": 13, "B": 21, "C": 10, "D": 3, "E": 27, "F": 6, "G": 13}
    actual_category_totals = {key: int(((ri_summary.get("by_category") or {}).get(key) or {}).get("portfolio_total") or 0) for key in expected_category_totals}
    if actual_category_totals != expected_category_totals:
        fail(f"canonical A-G portfolio totals drifted: {actual_category_totals}")
    ri_by_code = {row.get("code"): row for row in research_items.get("research_items") or []}
    if any((ri_by_code.get(code) or {}).get("scientific_state") != "HOLD" for code in ("A-3", "B-2", "B-3", "E-1")):
        fail("support/current-substrate stops must remain HOLD in canonical ResearchItem state")
    if (ri_by_code.get("F-4") or {}).get("scientific_state") != "STOPPED" or (ri_by_code.get("F-4") or {}).get("portfolio_disposition") == "ACTIVE_RESEARCH":
        fail("F-4 must remain a stopped historical ResearchItem and never backfill an active slot")
    if (ri_by_code.get("E-7") or {}).get("scientific_state") != "PAPER_READY" or ((ri_by_code.get("E-7") or {}).get("paper_transition") or {}).get("paper_id") != "STRI":
        fail("E-7 must hand off to STRI PaperState")
    pre_rows = pre_researchitem.get("candidates") or []
    pre_by_id = {row.get("candidate_id"): row for row in pre_rows}
    memento_pre = pre_by_id.get("MEMENTO-JOINT-BOUNDARY-CONTROL") or {}
    pre_summary = pre_researchitem.get("summary") or {}
    current_pre = current_status.get("pre_researchitem_candidates") or {}
    current_pre_rows = {row.get("candidate_id"): row for row in current_pre.get("rows") or []}
    if pre_researchitem.get("policy", {}).get("read_only_projection") is not True or any(pre_researchitem.get("policy", {}).get(key) is not False for key in ("scientific_authority", "experiment_authority", "promotion_authority")):
        fail(f"pre-ResearchItem registry must remain read-only and zero-authority: {pre_researchitem.get('policy')}")
    if int(pre_summary.get("pre_researchitem_candidates") or 0) != 1 or int(pre_summary.get("canonical_consumer_surface_live") or 0) != 1 or int(pre_summary.get("experiment_holds") or 0) != 1:
        fail(f"pre-ResearchItem registry must enumerate the one live held MEMENTO candidate: {pre_summary}")
    if not memento_pre or (memento_pre.get("canonical_consumer_surface") or {}).get("live") is not True or (memento_pre.get("promotion") or {}).get("research_item") is not False or (memento_pre.get("promotion") or {}).get("paper_state") is not False or (memento_pre.get("experiment_gate") or {}).get("episodes") != 36 or (memento_pre.get("experiment_gate") or {}).get("status") != "HOLD_EXACT_MEMENTO_RUNTIME_ASSETS_MISSING":
        fail(f"MEMENTO must remain canonical/live but pre-ResearchItem/PaperState and exact-runtime F0-held: {memento_pre}")
    if "MEMENTO-JOINT-BOUNDARY-CONTROL" not in current_pre_rows or int((current_status.get("headline") or {}).get("canonical_live_pre_researchitem_candidates") or 0) != 1:
        fail(f"current research status must consume the pre-ResearchItem registry: {current_pre}")
    papers = paper_registry.get("papers") or []
    papers_by_id = {row.get("paper_id"): row for row in papers}
    stri_registry = papers_by_id.get("STRI") or {}
    safety_registry = papers_by_id.get("AGENT-SAFETY-R9") or {}
    if len(papers) != 5 or stri_registry.get("source_research_item") != "E-7" or stri_registry.get("paper_stage") != "SUBMISSION_READY" or stri_registry.get("submission_ready") is not True:
        fail(f"PaperRegistry must project all five canonical ledgers while binding STRI to E-7 at SUBMISSION_READY: {papers}")
    safety_action = safety_registry.get("primary_next_action") or {}
    safety_prep = safety_registry.get("latest_paper_preparation") or {}
    if safety_registry.get("source_research_item") != "G-1" or safety_registry.get("paper_stage") != "PREBUTTAL" or safety_registry.get("scientific_status") != "READY" or safety_registry.get("submission_ready") is not False or safety_registry.get("gate_clean_submission_ready") is not False or safety_registry.get("immediate_submission_hold") is not True or safety_action.get("action_class") != "EXTERNAL_EVIDENCE_REQUIRED" or safety_action.get("blocking_on") != "HUMAN_SEMANTIC_LABEL_EVIDENCE_REQUIRED" or (int(safety_prep.get("passed_gates") or 0), int(safety_prep.get("required_gates") or 0), safety_prep.get("pass")) != (7, 8, False):
        fail(f"PaperRegistry must bind the scientifically reopened Agent Safety r8 paper to G-1 at READY / PREBUTTAL with the human-label evidence hold visible: {safety_registry}")
    if (ri_by_code.get("G-1") or {}).get("scientific_state") != "HOLD" or (ri_by_code.get("G-1") or {}).get("principle_dead_end_certified") is not False:
        fail("the broader G-1 replication/support ResearchItem must remain reopenable HOLD while the bounded r8 PaperState follows its current scientific-reopen epoch")
    d2_temporal = papers_by_id.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK") or {}
    d2_proxy = papers_by_id.get("D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE") or {}
    d2_failure = papers_by_id.get("D2-PAPER-FAILURE-MEMORY-PROVENANCE") or {}
    temporal_prep = d2_temporal.get("latest_paper_preparation") or {}
    temporal_context = d2_temporal.get("submission_readiness_context") or {}
    temporal_evidence = d2_temporal.get("source_native_evidence") or {}
    temporal_review = (d2_temporal.get("latest_mock_review") or {}).get("summary") or {}
    temporal_clean = temporal_prep.get("pass") is True
    temporal_expected_action = "NO_INTERNAL_ACTION" if temporal_clean else "PAPER_REPAIR_REQUIRED"
    if d2_temporal.get("paper_stage") != "SUBMISSION_READY" or d2_temporal.get("submission_ready") is not True or d2_temporal.get("gate_clean_submission_ready") is not temporal_clean or d2_temporal.get("immediate_submission_hold") is temporal_clean or d2_temporal.get("source_kind") != "paper-first-discovery-candidate" or d2_temporal.get("source_research_item") is not None or d2_temporal.get("source_candidates") != ["D2-C06"] or int(temporal_prep.get("required_gates") or 0) != 8 or int(temporal_prep.get("passed_gates") or 0) > 8 or ((d2_temporal.get("primary_next_action") or {}).get("action_class") != temporal_expected_action) or (not temporal_clean and not (temporal_prep.get("blockers") or [])) or temporal_context.get("support_blocker") != "" or int(temporal_evidence.get("runtime_valid_rows") or 0) <= 0 or (int(temporal_evidence.get("distinct_endpoints") or 0), int(temporal_evidence.get("institutional_systems") or 0)) != (35, 3) or not bool((d2_temporal.get("latest_mock_review") or {}).get("review_sha256")):
        fail(f"Temporal Skill D2 PaperState must preserve source-native evidence while latest Paper Preparation controls effective readiness: {d2_temporal}")
    if d2_proxy.get("paper_stage") != "SUBMISSION_READY" or d2_proxy.get("submission_ready") is not True or d2_proxy.get("gate_clean_submission_ready") is not True or (d2_proxy.get("latest_paper_preparation") or {}).get("pass") is not True or d2_proxy.get("source_kind") != "paper-first-discovery-candidate":
        fail(f"Proxy Reward D2 PaperState must remain ledger-ready and latest-gate-clean with paper-first provenance: {d2_proxy}")
    if d2_failure.get("paper_stage") != "SUBMISSION_READY" or d2_failure.get("submission_ready") is not True or d2_failure.get("gate_clean_submission_ready") is not True or (d2_failure.get("latest_paper_preparation") or {}).get("pass") is not True or d2_failure.get("active_unrefuted_claims") != 2 or d2_failure.get("source_kind") != "paper-first-discovery-candidate" or (d2_failure.get("acceptance_authority") or {}).get("submission") is not False:
        fail(f"Failure-Memory D2 PaperState must match its canonical SUBMISSION_READY ledger while retaining active-unrefuted claims and zero submission authority: {d2_failure}")
    registry_summary = paper_registry.get("summary") or {}
    expected_stage_counts = dict(sorted(__import__("collections").Counter(row.get("paper_stage") for row in papers).items()))
    expected_gate_clean = sum(row.get("gate_clean_submission_ready") is True for row in papers)
    expected_prep_failed = sum(int(((row.get("latest_paper_preparation") or {}).get("required_gates") or 0)) > 0 and (row.get("latest_paper_preparation") or {}).get("pass") is not True for row in papers)
    expected_holds = sum(row.get("immediate_submission_hold") is True for row in papers)
    expected_internal_actions = sum((row.get("primary_next_action") or {}).get("action_class") != "NO_INTERNAL_ACTION" for row in papers)
    if registry_summary.get("papers") != len(papers) or registry_summary.get("submission_ready") != sum(row.get("submission_ready") is True for row in papers) or registry_summary.get("gate_clean_submission_ready") != expected_gate_clean or registry_summary.get("paper_preparation_failed") != expected_prep_failed or registry_summary.get("immediate_submission_holds") != expected_holds or registry_summary.get("internal_action_required") != expected_internal_actions or registry_summary.get("no_internal_action") != len(papers) - expected_internal_actions or registry_summary.get("by_stage") != expected_stage_counts or registry_summary.get("scientific_holds") != 0:
        fail(f"PaperRegistry summary must be derived from the latest effective per-paper receipts: {registry_summary}")
    timeline_summary = research_timeline.get("summary") or {}
    timeline_policy = research_timeline.get("projection_policy") or {}
    timeline_events = research_timeline.get("events") or []
    if int(timeline_summary.get("events") or 0) != len(timeline_events) or len(timeline_events) < 756 or int(timeline_summary.get("days") or 0) < 20:
        fail("research timeline must preserve the full generated history rather than a truncated recent subset")
    if timeline_policy.get("read_only") is not True or timeline_policy.get("display_timezone") != "Asia/Shanghai" or timeline_policy.get("canonical_entity_bindings_are_read_only") is not True:
        fail("research timeline must remain a read-only China-time projection with read-only canonical entity bindings")
    if research_timeline.get("schema_version") != "1.1" or int(timeline_summary.get("canonical_research_bound_events") or 0) <= 0 or int(timeline_summary.get("canonical_experiment_bound_events") or 0) <= 0 or int(timeline_summary.get("canonical_paper_bound_events") or 0) <= 0 or int(timeline_summary.get("canonical_research_items_with_events") or 0) <= 0 or int(timeline_summary.get("canonical_papers_with_events") or 0) < 2:
        fail(f"research timeline canonical provenance binding summary is incomplete: {timeline_summary}")
    valid_ri_codes = set(ri_by_code)
    valid_experiment_ids = {row.get("experiment_id") for row in research_items.get("experiment_records") or []}
    valid_paper_ids = set(papers_by_id)
    bound_codes, bound_papers = set(), set()
    for event in timeline_events:
        refs = event.get("canonical_refs") or {}
        for ref in refs.get("research_items") or []:
            if ref.get("code") not in valid_ri_codes:
                fail(f"timeline event references missing ResearchItem: {ref}")
            bound_codes.add(ref.get("code"))
        for ref in refs.get("experiments") or []:
            if ref.get("experiment_id") not in valid_experiment_ids:
                fail(f"timeline event references missing ExperimentRecord: {ref}")
        for ref in refs.get("papers") or []:
            if ref.get("paper_id") not in valid_paper_ids:
                fail(f"timeline event references missing PaperState: {ref}")
            bound_papers.add(ref.get("paper_id"))
    if not {"A-3", "E-7", "G-1"}.issubset(bound_codes) or not {"STRI", "AGENT-SAFETY-R9"}.issubset(bound_papers):
        fail(f"timeline must bind representative ResearchItems and the canonical paper spine: research={sorted(bound_codes)} papers={sorted(bound_papers)}")
    dashboard_policy = research_dashboard.get("projection_policy") or {}
    dashboard_summary = research_dashboard.get("summary") or {}
    dashboard_attention = research_dashboard.get("attention") or []
    dashboard_by_code = {row.get("code"): row for row in dashboard_attention}
    if research_dashboard.get("schema_version") != "1.0" or dashboard_policy.get("read_only") is not True or any(dashboard_policy.get(key) is not False for key in ("scientific_authority", "experiment_authority", "submission_authority")) or dashboard_policy.get("dashboard_never_overrides_source_ledgers") is not True or dashboard_policy.get("next_action_class_is_canonical_control_semantics") is not True or dashboard_policy.get("next_step_text_is_human_explanation_only") is not True or dashboard_policy.get("zero_active_research_items_is_valid") is not True or dashboard_policy.get("attention_is_visibility_not_activity") is not True:
        fail(f"research dashboard must remain read-only, allow zero active rows, and separate attention visibility from activity: {dashboard_policy}")
    expected_dashboard_summary = {"portfolio_objects":int(ri_summary.get("portfolio_objects") or 0),"research_items":int(ri_summary.get("research_items") or 0),"active_research_items":0,"current_attention":6,"research_handoffs":1,"research_waiting_reopen":5,"machine_actionable_attention":0,"paper_ready":1,"holds":5,"launchable_formal_experiments":0,"papers":int(registry_summary.get("papers") or 0),"submission_ready":int(registry_summary.get("gate_clean_submission_ready") or 0),"ledger_submission_ready":int(registry_summary.get("submission_ready") or 0),"immediate_submission_holds":int(registry_summary.get("immediate_submission_holds") or 0)}
    if any(int(dashboard_summary.get(key) or 0) != value for key, value in expected_dashboard_summary.items()):
        fail(f"research dashboard canonical summary drifted: {dashboard_summary}")
    expected_attention = {"E-7","G-1","A-3","B-2","B-3","E-1"}
    if set(dashboard_by_code) != expected_attention or dashboard_by_code.get("E-7",{}).get("scientific_state") != "PAPER_READY" or any(dashboard_by_code.get(code,{}).get("scientific_state") != "HOLD" for code in expected_attention-{"E-7"}):
        fail(f"research dashboard current-attention set is incomplete or misclassified: {dashboard_by_code}")
    dashboard_g1 = dashboard_by_code.get("G-1") or {}
    if (dashboard_by_code.get("E-7") or {}).get("paper_id") != "STRI" or (dashboard_by_code.get("E-7") or {}).get("paper_stage") != "SUBMISSION_READY" or (dashboard_by_code.get("E-7") or {}).get("submission_ready") is not True or dashboard_g1.get("paper_id") != "AGENT-SAFETY-R9" or dashboard_g1.get("paper_stage") != "PREBUTTAL" or dashboard_g1.get("submission_ready") is not False or dashboard_g1.get("paper_next_action_class") != "EXTERNAL_EVIDENCE_REQUIRED":
        fail(f"research dashboard must preserve current ResearchItem→PaperState handoffs, including the G1 r8 scientific-reopen hold: {dashboard_by_code}")
    if any(not row.get("portfolio_href") or not row.get("timeline_href") or not row.get("briefing_zh") or not row.get("next_step_zh") for row in dashboard_attention):
        fail("every dashboard attention row needs a human briefing, explanatory action text, ResearchItem link, and timeline link")
    dashboard_week = research_dashboard.get("week") or {}
    if not dashboard_week.get("start_date") or not dashboard_week.get("end_date") or int(dashboard_week.get("research_days") or 0) < 1 or int(dashboard_week.get("substantive_events") or 0) < 1 or len(dashboard_week.get("highlights") or []) < 3:
        fail(f"research dashboard weekly summary is incomplete: {dashboard_week}")
    embedded_memory = research_system.get("research_memory_wiki") or {}
    if research_memory.get("wiki_sha256") != embedded_memory.get("wiki_sha256") or (research_memory.get("summary") or {}) != (embedded_memory.get("summary") or {}) or (research_memory.get("lint") or {}) != (embedded_memory.get("lint") or {}):
        fail("research memory wiki is stale versus embedded research-system state")
    if int((research_system.get("summary") or {}).get("research_memory_entries") or 0) != int((research_memory.get("summary") or {}).get("entries") or 0):
        fail(f"research-system summary memory count is stale: system={(research_system.get('summary') or {}).get('research_memory_entries')} memory={(research_memory.get('summary') or {}).get('entries')}")
    if research_memory.get("scientific_authority") is not False or int(((research_memory.get("lint") or {}).get("summary") or {}).get("errors") or 0) != 0:
        fail("research memory wiki must remain zero-authority with zero hard lint errors")
    if any(row.get("durability_class") == "transient" and row.get("prompt_eligible") is True for row in research_memory.get("entries") or [] if isinstance(row, dict)):
        fail("transient operational memory cannot enter research query packs")
    discovery_lessons = [row for row in research_memory.get("entries") or [] if isinstance(row, dict) and row.get("kind") == "DISCOVERY_LESSON"]
    discovery_cycle = json.loads((ROOT / "generated" / "longitudinal-safety-discovery-cycle-20260823.json").read_text(encoding="utf-8"))
    expected_discovery_lessons = int((discovery_cycle.get("summary") or {}).get("failure_lessons") or 0)
    if expected_discovery_lessons < 19 or int((research_memory.get("summary") or {}).get("discovery_lessons") or 0) != expected_discovery_lessons or len(discovery_lessons) != expected_discovery_lessons:
        fail(f"Research Memory must expose all canonical longitudinal discovery lessons: expected={expected_discovery_lessons} summary={(research_memory.get('summary') or {}).get('discovery_lessons')} rows={len(discovery_lessons)}")
    if any(row.get("scientific_authority") is not False or row.get("principle_update_allowed") is not False for row in discovery_lessons):
        fail("Discovery Lessons must remain retrieval/precheck memory with zero scientific or principle-update authority")
    system_reader_source = (ROOT / "system-overview-reader.js").read_text(encoding="utf-8")
    if "data-discovery-lesson-section" not in system_reader_source or "data-discovery-lesson" not in system_reader_source:
        fail("System Overview must visibly render Discovery Lessons from the embedded Research Memory projection")
    durable_shadow_admission = json.loads((ROOT / "generated" / "paper-first-shadow-search-admission.json").read_text(encoding="utf-8"))
    embedded_shadow_admission = research_system.get("paper_first_shadow_search_admission") or {}
    durable_summary = durable_shadow_admission.get("summary") or {}
    embedded_summary = embedded_shadow_admission.get("summary") or {}
    for key in ("status", "reason", "policy", "summary", "source_identity", "scientific_authority"):
        if embedded_shadow_admission.get(key) != durable_shadow_admission.get(key):
            fail(f"research-system Shadow Search admission is stale at {key}")
    qualification_ready = int(bool(durable_summary.get("qualification_allowed")))
    if int((current_status.get("headline") or {}).get("shadow_qualification_ready") or 0) != qualification_ready:
        fail("current-research-status global shadow qualification does not match durable admission")
    global_qualification = ((current_status.get("shadow_search") or {}).get("qualification") or {})
    if bool(global_qualification.get("qualification_allowed")) != bool(durable_summary.get("qualification_allowed")):
        fail("current-research-status global qualification is stale versus durable admission")
    if int(global_qualification.get("automatic_provider_calls_authorized") or 0) != 0 or int(durable_summary.get("automatic_provider_calls_authorized") or 0) != 0:
        fail("shadow qualification cannot authorize provider calls")
    residual = current_status.get("positive_residual") or {}
    if residual.get("active_mechanism_seed") is False and residual.get("shadow_qualification_allowed") is not False:
        fail("archived positive residual cannot be reactivated by global operator-upgrade qualification")
    if qualification_ready and residual.get("active_mechanism_seed") is False and global_qualification.get("scope") != "global-v13-shadow-control; does not reactivate archived positive-residual assets":
        fail("global v13 shadow qualification must explicitly remain separate from the archived positive residual")

    if (ROOT / ".nojekyll").exists():
        fail(".nojekyll must stay absent so the branch-mode Pages fallback honors _config.yml exclusions")
    pages_config = (ROOT / "_config.yml").read_text(encoding="utf-8")
    for marker in (
        "research_pipeline", "scripts", "deploy", "deliveries", "downloads",
        "advisor-priority-view.js", "generated/advisor-priority-ideas.json",
        "browser_smoke_test.py", "site_smoke_test.py",
    ):
        if marker not in pages_config:
            fail(f"Pages exclusion config is missing {marker}")

    html_files = {path.name for path in ROOT.glob("*.html") if path.name != "404.html"}
    expected = set(CANONICAL_PAGES) | set(REDIRECT_PAGES)
    if html_files != expected:
        fail(f"HTML set mismatch; missing={sorted(expected-html_files)}, extra={sorted(html_files-expected)}")

    referenced_scripts: set[str] = set()
    canonical_scripts: dict[str, list[str]] = {}
    for filename, page_id in CANONICAL_PAGES.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        match = re.search(r'<body\s+data-page="([^"]+)"', text)
        if not match or match.group(1) != page_id:
            fail(f"{filename} must use data-page={page_id}")
        if 'class="sidebar"' not in text or 'id="site-search"' not in text or 'id="dynamic-page"' not in text:
            fail(f"{filename} is missing canonical page UI")
        scripts = re.findall(r'<script\s+src="([^"]+)"', text)
        canonical_scripts[filename] = scripts
        title = re.search(r'<title>(.*?)</title>', text)
        description = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', text)
        if not title or not title.group(1).strip() or not description or not description.group(1).strip():
            fail(f"{filename} must have a non-empty title and meta description")
        if "data.js" not in scripts or "app.js" not in scripts:
            fail(f"{filename} must load data.js and app.js")
        if filename == "research-timeline.html":
            if "generated/research-timeline.js" not in scripts or "research-timeline-view.js" not in scripts:
                fail("research-timeline.html must load its generated projection and dedicated renderer")
            if scripts.index("generated/research-timeline.js") > scripts.index("app.js") or scripts.index("research-timeline-view.js") > scripts.index("app.js"):
                fail("research timeline data/view must load before app.js")
        else:
            if "page-architecture-data.js" not in scripts:
                fail(f"{filename} must load page-architecture-data.js")
            if "generated/current-research-status.js" not in scripts or "current-research-status-view.js" not in scripts:
                fail(f"{filename} must load the unified public current-research status before app.js")
            if scripts.index("generated/current-research-status.js") > scripts.index("app.js") or scripts.index("current-research-status-view.js") > scripts.index("app.js"):
                fail(f"{filename} must load current-research status/view before app.js")
        for script in scripts:
            referenced_scripts.add(script)
            if not (ROOT / script).exists():
                fail(f"{filename} references missing script {script}")

    current_state_pages = {"index.html", "system-overview.html", "research-map.html", "research-directions.html", "paper-ideas.html", "experiments.html", "selected-paper.html"}
    for filename in current_state_pages:
        if "generated/research-system-state.js" not in canonical_scripts.get(filename, []):
            fail(f"{filename} must load the unified current research-system state")
    stable_reference_pages = {"foundations.html", "mechanisms.html", "bibliography.html"}
    for filename in stable_reference_pages:
        if "generated/research-system-state.js" in canonical_scripts.get(filename, []):
            fail(f"{filename} is a stable reference page and must not mix in current P0 state")
    idea_scripts = canonical_scripts.get("paper-ideas.html", [])
    if not all(name in idea_scripts for name in ("generated/research-items.js", "generated/paper-registry.js")) or idea_scripts.index("generated/research-items.js") > idea_scripts.index("app.js") or idea_scripts.index("generated/paper-registry.js") > idea_scripts.index("app.js"):
        fail("paper-ideas must load canonical ResearchItem/PaperRegistry state before app.js")
    home_scripts = canonical_scripts.get("index.html", [])
    if "generated/research-dashboard.js" not in home_scripts or home_scripts.index("generated/research-dashboard.js") > home_scripts.index("app.js"):
        fail("home must load the lightweight read-only research dashboard before app.js")
    map_scripts = canonical_scripts.get("research-map.html", [])
    if not all(name in map_scripts for name in ("generated/research-items.js", "generated/paper-registry.js", "generated/research-dashboard.js", "research-map-view.js")) or map_scripts.index("generated/research-items.js") > map_scripts.index("app.js") or map_scripts.index("generated/paper-registry.js") > map_scripts.index("app.js") or map_scripts.index("generated/research-dashboard.js") > map_scripts.index("research-map-view.js") or map_scripts.index("research-map-view.js") > map_scripts.index("app.js"):
        fail("research-map must load canonical ResearchItem/PaperRegistry/dashboard state and its renderer before app.js")
    map_view_source = (ROOT / "research-map-view.js").read_text(encoding="utf-8")
    if "RESEARCH_ITEM_STATE" not in map_view_source or "[\"A\",\"B\",\"C\",\"D\",\"E\",\"F\",\"G\"]" not in map_view_source:
        fail("research-map must render the complete A-G map from canonical ResearchItem state with an explicit completeness guard")
    landscape_source = (ROOT / "research-landscape-data.js").read_text(encoding="utf-8")
    if "formal_papers:" not in landscape_source or "formalPublicationTimeline" not in map_view_source or "formalPublishedPapers" not in map_view_source or "frontierPapersForGroup" not in map_view_source:
        fail("research-map must prioritize formally published conference/journal literature and keep preprints as a separate frontier supplement")
    boundary_block = landscape_source.split("frontier_boundaries:", 1)[1].split("formal_papers:", 1)[0] if "frontier_boundaries:" in landscape_source else ""
    if len(re.findall(r'^    [A-G]:\{zh:"[^"]+",en:"[^"]+"\}', boundary_block, re.MULTILINE)) != 7 or not all(title in boundary_block for title in ("HarnessBank", "RoMeRL", "Who Grades the Grader?", "EmbodiSkill", "Robo-Cortex", "SpaceMind")):
        fail("research-map must carry seven bilingual latest-literature boundary notes grounded in the authenticated S2 refresh")
    if "frontierBoundary" not in map_view_source or "ResearchItem scientific state" not in map_view_source:
        fail("latest-literature boundary notes must remain a read-only nearest-work overlay and explicitly preserve ResearchItem authority")
    if "rpm-external-density" not in map_view_source or "EXTERNAL LITERATURE DENSITY" not in map_view_source or "novelty verdicts" not in map_view_source:
        fail("research-map coverage chapter must separate internal ResearchItem accumulation from external literature density without treating density as novelty")
    if "row.source_kind!==\"shadow_closed\"" not in map_view_source or "primaryLedger" not in map_view_source or "attentionCard" not in map_view_source or "formalCategoryList" not in map_view_source:
        fail("research-map must list every reader-facing internal research line, expand active/hold evidence, and give the wider literature column a year-grouped formal-paper view")
    directions_scripts = canonical_scripts.get("research-directions.html", [])
    if "generated/research-items.js" not in directions_scripts or directions_scripts.index("generated/research-items.js") > directions_scripts.index("app.js"):
        fail("research-directions must load canonical ResearchItem state before app.js for the D1-D10 ↔ A-G crosswalk")
    selected_scripts_list = canonical_scripts.get("selected-paper.html", [])
    if not all(name in selected_scripts_list for name in ("generated/research-items.js", "generated/paper-registry.js")) or selected_scripts_list.index("generated/research-items.js") > selected_scripts_list.index("app.js") or selected_scripts_list.index("generated/paper-registry.js") > selected_scripts_list.index("app.js"):
        fail("selected-paper must load canonical ResearchItem/PaperRegistry state before app.js")
    selected_scripts = set(selected_scripts_list)
    if {"content-review.js", "content-review-external.js"} & selected_scripts:
        fail("selected-paper must not load stale review overrides")
    selected_html = (ROOT / "selected-paper.html").read_text(encoding="utf-8")
    if "Papers · PaperRegistry" not in selected_html:
        fail("selected-paper must be explicitly labeled as the canonical PaperRegistry workspace")
    if "current-research-status-view.js" not in selected_html:
        fail("selected-paper must load the unified current-paper renderer")
    if "paper-novelty-audit-data.js" not in selected_html or selected_scripts_list.index("paper-novelty-audit-data.js") > selected_scripts_list.index("current-research-status-view.js"):
        fail("selected-paper must load the advisor-facing novelty audit before the current-paper renderer")
    if "paper-external-review-data.js" not in selected_html or selected_scripts_list.index("paper-external-review-data.js") > selected_scripts_list.index("current-research-status-view.js"):
        fail("selected-paper must load the external-review repair overlay before the current-paper renderer")
    if "generated/stanford-r2-objection-matrix.js" not in selected_html or selected_scripts_list.index("generated/stanford-r2-objection-matrix.js") > selected_scripts_list.index("current-research-status-view.js"):
        fail("selected-paper must load the Stanford Round-2 objection matrix before the current-paper renderer")
    paper_story_data_scripts = tuple(sorted(path.name for path in ROOT.glob("paper-story-*.js") if path.name not in {"paper-story-blueprint.js", "paper-story-view.js"}))
    paper_story_scripts = ("paper-story-blueprint.js",) + paper_story_data_scripts + ("paper-story-view.js",)
    if not all(name in selected_scripts_list for name in paper_story_scripts):
        fail("selected-paper must load the complete Paper Story V3 blueprint, every discovered paper story, and renderer")
    if paper_story_data_scripts and (selected_scripts_list.index("paper-story-blueprint.js") > min(selected_scripts_list.index(name) for name in paper_story_data_scripts) or max(selected_scripts_list.index(name) for name in paper_story_data_scripts) > selected_scripts_list.index("paper-story-view.js")) or selected_scripts_list.index("paper-story-view.js") > selected_scripts_list.index("current-research-status-view.js"):
        fail("Paper Story V3 data must load after its blueprint and before the PaperRegistry renderer")
    novelty_source = (ROOT / "paper-novelty-audit-data.js").read_text(encoding="utf-8")
    novelty_ids = ("STRI", "AGENT-SAFETY-R9", "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE", "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK", "D2-PAPER-FAILURE-MEMORY-PROVENANCE")
    if not all(f'\"{paper_id}\"' in novelty_source for paper_id in novelty_ids) or "scientific_authority:false" not in novelty_source or "cannot_change_paper_state:true" not in novelty_source:
        fail("paper novelty audit must cover all five PaperStates and remain a zero-authority read-only literature overlay")
    for marker in ("Demystifying Agent Skills", "Remembering More, Risking More", "Memory Reward Inflation", "Not All Skills Help", "Memory Provenance Laundering"):
        if marker not in novelty_source:
            fail(f"paper novelty audit is missing nearest-work evidence: {marker}")
    external_review_source = (ROOT / "paper-external-review-data.js").read_text(encoding="utf-8")
    if not all(f'\"{paper_id}\"' in external_review_source for paper_id in novelty_ids) or "read_only_external_review_overlay:true" not in external_review_source or "cannot_change_paper_state:true" not in external_review_source or "score_is_not_official_iclr_score:true" not in external_review_source:
        fail("external paper review overlay must cover all five PaperStates and remain read-only / non-official")
    for marker in ("review_round:2", "6.1", "6.3", "5.4", "Accept", "Weak Accept", "Weak Reject", "Borderline-leaning Reject", "Borderline Reject"):
        if marker not in external_review_source:
            fail(f"external paper review overlay is missing Round-2 score/recommendation evidence: {marker}")
    objection_matrix_path = ROOT / "generated" / "stanford-r2-objection-matrix.json"
    objection_matrix = json.loads(objection_matrix_path.read_text(encoding="utf-8"))
    objection_matrix_js = (ROOT / "generated" / "stanford-r2-objection-matrix.js").read_text(encoding="utf-8")
    expected_objection_js = "window.STANFORD_R2_OBJECTION_MATRIX = " + json.dumps(objection_matrix, ensure_ascii=False, separators=(",", ":")) + ";\n"
    if objection_matrix_js != expected_objection_js:
        fail("Stanford Round-2 objection matrix JSON/JS projections are not byte-consistent")
    objection_rows = [row for paper in objection_matrix.get("papers", {}).values() for row in paper.get("objections", [])]
    disposition_counts = Counter(row.get("d") for row in objection_rows)
    matrix_summary = objection_matrix.get("summary", {})
    expected_dispositions = {"RESOLVED":int(matrix_summary.get("resolved") or 0),"EXISTING_EVIDENCE_ACTIONABLE":int(matrix_summary.get("existing_evidence_actionable") or 0),"REQUIRES_SCIENTIFIC_REOPEN":int(matrix_summary.get("requires_scientific_reopen") or 0),"PERMANENT_CLAIM_BOUNDARY":int(matrix_summary.get("permanent_claim_boundary") or 0)}
    if len(objection_matrix.get("papers", {})) != 5 or len(objection_rows) != 33 or disposition_counts != Counter(expected_dispositions) or int(matrix_summary.get("objections") or 0) != len(objection_rows):
        fail(f"Stanford objection matrix summary/projection drifted: papers={len(objection_matrix.get('papers', {}))} objections={len(objection_rows)} summary={matrix_summary} counts={dict(disposition_counts)}")
    if any(objection_matrix.get("policy", {}).get(key) is not False for key in ("scientific_authority","experiment_authority","gpu_authority","submission_authority")):
        fail("Stanford Round-2 objection matrix must grant zero automatic scientific/experiment/GPU/submission authority")
    if any(not row.get("e") or row.get("action") != "NONE" for row in objection_rows if row.get("d") == "RESOLVED"):
        fail("Every RESOLVED Stanford objection must bind traceable evidence and require no action")
    safety_objections = {row.get("id"): row for row in (objection_matrix.get("papers", {}).get("AGENT-SAFETY-R9", {}).get("objections") or [])}
    if any((safety_objections.get(oid) or {}).get("d") != "RESOLVED" for oid in ("SAFETY-O3", "SAFETY-O4")) or any((safety_objections.get(oid) or {}).get("d") != "REQUIRES_SCIENTIFIC_REOPEN" for oid in ("SAFETY-O5", "SAFETY-O6", "SAFETY-O7")):
        fail(f"G1 Stanford R2 objection dispositions must reflect r7 paper-only closure without auto-authorizing new evidence: {safety_objections}")
    temporal_objections = {row.get("id"): row for row in (objection_matrix.get("papers", {}).get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK", {}).get("objections") or [])}
    if (temporal_objections.get("TEMP-O3") or {}).get("d") != "RESOLVED" or "88/88" not in json.dumps(temporal_objections.get("TEMP-O3"), ensure_ascii=False) or (temporal_objections.get("TEMP-O4") or {}).get("d") != "RESOLVED" or (temporal_objections.get("TEMP-O5") or {}).get("d") != "PERMANENT_CLAIM_BOUNDARY" or "G0" not in json.dumps(temporal_objections.get("TEMP-O4"), ensure_ascii=False) or "Rsurf" not in json.dumps(temporal_objections.get("TEMP-O5"), ensure_ascii=False):
        fail(f"E2 Stanford R2 objection dispositions must reconcile historical objections to canonical R14 without reopening the current narrow claim: {temporal_objections}")
    failure_objections = {row.get("id"): row for row in (objection_matrix.get("papers", {}).get("D2-PAPER-FAILURE-MEMORY-PROVENANCE", {}).get("objections") or [])}
    if any((failure_objections.get(oid) or {}).get("d") != "RESOLVED" for oid in ("FAILURE-O3", "FAILURE-O4")) or any((failure_objections.get(oid) or {}).get("d") != "REQUIRES_SCIENTIFIC_REOPEN" for oid in ("FAILURE-O5", "FAILURE-O6")):
        fail(f"B1 Stanford R2 objection dispositions must reflect r7 power/equivalence closure while preserving L2/L3 scientific reopen debt: {failure_objections}")
    if any(row.get("action") != "OFFLINE_ANALYSIS_ONLY" for row in objection_rows if row.get("d") == "EXISTING_EVIDENCE_ACTIONABLE"):
        fail("Existing-evidence Stanford objections must be limited to offline analysis/manuscript absorption")
    if any(row.get("action") != "SCIENTIFIC_REOPEN_REQUIRED" or not row.get("reopen") for row in objection_rows if row.get("d") == "REQUIRES_SCIENTIFIC_REOPEN"):
        fail("Scientific-reopen Stanford objections must carry an explicit reopen condition and cannot auto-execute")
    if any(row.get("action") != "NONE" for row in objection_rows if row.get("d") == "PERMANENT_CLAIM_BOUNDARY"):
        fail("Permanent Stanford claim boundaries must not create an execution action")
    for secret_marker in ("598666122", "rrPkIBax5D", "QUnnU4wFKS", "DqW1VNWgFx", "_Q3_zdvJNr", "e2EhqrGLn2"):
        if secret_marker in external_review_source or secret_marker in selected_html:
            fail("public external-review overlay leaked a private email or review token")
    current_view_source = (ROOT / "current-research-status-view.js").read_text(encoding="utf-8")
    if "paper-novelty-portfolio" not in current_view_source or "paper-novelty-detail" not in current_view_source or "Decision needed" not in current_view_source:
        fail("selected-paper must render both portfolio-level and per-paper novelty decisions")
    if "paper-external-review-portfolio" not in current_view_source or "paper-external-review-detail" not in current_view_source or "targeted repair plan" not in current_view_source.lower():
        fail("selected-paper must render portfolio-level and per-paper external review / repair plans")
    if "stanford-r2-objection-matrix" not in current_view_source or "reviewer-objection-detail" not in current_view_source or "REQUIRES_SCIENTIFIC_REOPEN" not in current_view_source:
        fail("selected-paper must render the portfolio and per-paper Stanford Round-2 objection disposition matrix")

    stale_markers = (
        "Selected ICLR Paper Workspace", "选中 ICLR 论文工作区",
        "No executed pilot results yet", "尚无真实 Pilot",
        "minimum pilot evidence remains missing", "仍缺最小 Pilot",
    )
    for filename in CANONICAL_PAGES:
        html = (ROOT / filename).read_text(encoding="utf-8")
        loaded = [html]
        for script in canonical_scripts.get(filename, []):
            path = ROOT / script
            if path.exists() and not script.startswith("generated/"):
                loaded.append(path.read_text(encoding="utf-8", errors="ignore"))
        rendered_source = "\n".join(loaded)
        for marker in stale_markers:
            if marker in rendered_source:
                fail(f"{filename} still exposes stale current-state marker: {marker}")

    for filename, target in REDIRECT_PAGES.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        match = re.search(r'<body\s+data-redirect="([^"]+)"', text)
        if not match or match.group(1) != target:
            fail(f"{filename} must redirect to {target}")
        if 'name="robots" content="noindex"' not in text or 'redirect.js' not in text:
            fail(f"{filename} is not a noindex compatibility redirect")
        target_file = target.split("#", 1)[0]
        if target_file not in CANONICAL_PAGES:
            fail(f"{filename} redirects to non-canonical target {target_file}")

    js_files = sorted(ROOT.glob("*.js"))
    for path in js_files:
        subprocess.run(["node", "--check", str(path)], check=True)
    subprocess.run(["node", str(ROOT / "scripts" / "validate_paper_story_contract.js")], cwd=ROOT, check=True)

    combined = "\n".join(path.read_text(encoding="utf-8") for path in js_files if path.name != "app.js")
    architecture_text = (ROOT / "page-architecture-data.js").read_text(encoding="utf-8")
    expected_chapter_ids = {
        "home": ["understand-field", "select-research", "execute-audit"],
        "foundations": ["boundary", "taxonomy-evidence"],
        "mechanisms": ["mechanism-axis", "domain-axis", "evidence-axis"],
        "research-directions": ["orientation", "direction-atlas", "current-bridge"],
        "research-map": ["layering", "coverage-gaps", "integrated-map", "handoff"],
        "paper-ideas": ["discussed-ideas", "new-ideas"],
        "selected-paper": ["problem-scope", "evidence-experiments", "narrative-execution", "review-gates"],
        "bibliography": ["published-spine", "published-comparison", "idea-mining", "field-maps", "search-corpus", "coverage-protocol"],
    }
    for page_id, chapter_ids in expected_chapter_ids.items():
        for chapter_id in chapter_ids:
            if architecture_text.count(f'id:"{chapter_id}"') != 1:
                fail(f"page architecture {page_id} is missing unique chapter {chapter_id}")
    app_text = (ROOT / "app.js").read_text(encoding="utf-8")
    for marker in ["renderArchitectureOverview", "renderCustomChapter", 'const tocSelector = "#dynamic-page h2, #dynamic-page h3"', "toc-level-${node.level}"]:
        if marker not in app_text:
            fail(f"hierarchical renderer is missing {marker}")
    if 'const tocSelector = "#dynamic-page h2, #dynamic-page h3, #dynamic-page h4"' in app_text:
        fail("canonical sidebar TOCs must stop at H3")
    display_localization_pairs = (
        ("Use frozen existing P0 evidence; do not rerun identical compute.", "使用已冻结的现有 P0 证据；不要重复运行相同计算。"),
        ("Merge branch soft-audit into research-system scheduling; stop standalone A-1 repair and do not spend GPU unless a materially new observable/substrate is proposed.", "把分支 soft-audit 并入科研系统调度"),
        ("Merge evidence-depth scheduling into A-1/system soft audit; stop standalone A-2 repair and do not launch controller GPU training.", "把 evidence-depth 调度并入 A-1/系统 soft audit"),
        ("Human authors must verify the live ICLR/OpenReview deadline because official ICLR pages currently conflict.", "作者必须在提交前人工核验实时 ICLR/OpenReview 截止日期"),
        ("DECISION → LEARN → PUBLISH", "裁决 → 沉淀 → 发布"),
        ("SELF-EVOLVING RESEARCH OS", "自进化科研操作系统"),
        ("PRE-EXPERIMENT COMPILER · GATE 1–8", "实验前编译器 · Gate 1–8"),
    )
    for source, localized in display_localization_pairs:
        if source not in app_text or localized not in app_text:
            fail(f"display localization mapping is incomplete: {source}")

    # Reader-facing clarity contract: canonical entry copy must explain concrete
    # user questions/actions before exposing internal machine terminology.
    clarity_markers = {
        "data.js": ("集中回答四个具体问题", "统一科研工作区", "每个 ResearchItem"),
        "content-system-overview.js": ("一个研究方向，怎样才能变成实验，再变成论文", "AI 评审负责找文献撞车", "只有人工负责人可以改变核心科学主张"),
        "system-overview-reader.js": ("先确认异常现象真实存在", "这个最小实验无论成功或失败，都会改变下一步吗", "什么时候才允许说“这个原理走不通”", "终止结论、搜索记忆和历史 snapshot 必须分层读取", "关闭一个 Idea 不会让下一个 Idea 自动晋级"),
        "system-overview-operations.js": ("长实验怎样安全启动、断线后怎样继续", "哪些文件必须留下，才能以后证明当时到底发生了什么"),
        "content-idea-portfolio.js": ("这页不是“看起来不错的 Idea 清单”", "最近一轮问题发现又审查了 41 条草案", "先从 ResearchItem 理解问题和当前结论"),
        "current-research-status-view.js": ("先看控制面", "PAPERSTATE_HANDOFF", "REOPEN_CONDITION_REQUIRED", "machine-actionable ResearchItem"),
        "content-selected-iclr.js": ("这个旧项目现在没有任何实验允许启动", "不能只靠追加样本或换第二个模型重开"),
        "content-research-directions.js": ("领域图谱总入口", "历史项目只是过去尝试过的方案", "当前 A–G 才是今天 ResearchItem、实验与论文统一使用的权威坐标"),
    }
    for filename, markers in clarity_markers.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            fail(f"reader-facing clarity contract is incomplete in {filename}: {missing}")
    opaque_entry_phrases = (
        "zero-authority positive-residual search",
        "canonical/shadow discovery state",
        "Six-layer research architecture from evidence and AI consultation through P0 Economy",
        "Current idea status: current paper, archived residual, canonical, shadow, and legacy P0 are separate layers",
    )
    entry_sources = "\n".join((ROOT / name).read_text(encoding="utf-8", errors="ignore") for name in (
        "data.js", "content-consolidated.js", "content-system-overview.js", "content-idea-portfolio.js"
    ))
    for phrase in opaque_entry_phrases:
        if phrase in entry_sources:
            fail(f"opaque internal terminology leaked back into canonical entry copy: {phrase}")

    for page_id in CANONICAL_PAGES.values():
        if page_id != "home" and f'"{page_id}"' not in combined and f'.{page_id}' not in combined:
            fail(f"no content configuration found for canonical page {page_id}")

    portfolio_text = (ROOT / "portfolio-data.js").read_text(encoding="utf-8")
    direction_ids = re.findall(r'^\s*id:"([a-z0-9-]+)",\s*code:"D\d+"', portfolio_text, re.MULTILINE)
    idea_rows = re.findall(r'^  \{name:"([^"]+)",directionId:"([a-z0-9-]+)",rank:(\d+)', portfolio_text, re.MULTILINE)
    if len(direction_ids) != 10 or len(set(direction_ids)) != 10:
        fail("portfolio must contain 10 unique research directions")
    if len(idea_rows) != 34:
        fail("portfolio must contain 34 paper ideas")
    names = [name for name, _, _ in idea_rows]
    ranks = sorted(int(rank) for _, _, rank in idea_rows)
    if len(set(names)) != 34 or ranks != list(range(1, 35)):
        fail("paper ideas must have unique names and ranks 1-34")
    mapped_names: list[str] = []
    for block in re.findall(r'ideaIds:\[([^\]]*)\]', portfolio_text):
        mapped_names.extend(re.findall(r'"([^"]+)"', block))
    if sorted(mapped_names) != sorted(names) or len(mapped_names) != len(set(mapped_names)):
        fail("each paper idea must appear exactly once in the direction mapping")

    direction_guide_text = (ROOT / "direction-guide-data.js").read_text(encoding="utf-8")
    if len(re.findall(r'id:"(?:learn|commit|adapt|govern)"', direction_guide_text)) != 4:
        fail("direction guide must contain four macro questions")
    for direction_id in direction_ids:
        marker = f'"{direction_id}":{{'
        if marker not in direction_guide_text:
            fail(f"direction guide is missing {direction_id}")
        block = direction_guide_text.split(marker, 1)[1].split("\n    }", 1)[0]
        for field in ("plain", "object", "example", "distinction"):
            match = re.search(rf'{field}:\{{en:"([^"]+)",zh:"([^"]+)"\}}', block)
            if not match or not match.group(1).strip() or not match.group(2).strip():
                fail(f"direction {direction_id} is missing bilingual {field}")

    direction_literature_text = (ROOT / "direction-literature-data.js").read_text(encoding="utf-8")
    literature_direction_ids = re.findall(r'^  "([a-z0-9-]+)": \[', direction_literature_text, re.MULTILINE)
    if sorted(literature_direction_ids) != sorted(direction_ids) or len(literature_direction_ids) != 10:
        fail("direction literature must cover all ten research directions exactly once")
    literature_titles = re.findall(r'^      title:"([^"]+)"', direction_literature_text, re.MULTILINE)
    if len(literature_titles) < 30:
        fail("direction literature must keep at least three representative papers per research direction")
    direction_blocks = re.findall(r'^  "([a-z0-9-]+)": \[(.*?)(?=^  "[a-z0-9-]+": \[|^};)', direction_literature_text, re.MULTILINE | re.DOTALL)
    sparse_directions = [direction_id for direction_id, block in direction_blocks if len(re.findall(r'^      title:"([^"]+)"', block, re.MULTILINE)) < 3]
    if sparse_directions:
        fail(f"direction literature has fewer than three representative papers: {sparse_directions}")
    method_count = len(re.findall(r'method:\{en:"[^"]+",zh:"[^"]+"\}', direction_literature_text))
    fit_count = len(re.findall(r'fit:\{en:"[^"]+",zh:"[^"]+"\}', direction_literature_text))
    if method_count != len(literature_titles):
        fail("every representative paper must have a bilingual one-line method")
    if fit_count != len(literature_titles):
        fail("every representative paper must explain its bilingual direction fit")
    curated_text = (ROOT / "data.js").read_text(encoding="utf-8")
    missing_direction_papers = [title for title in literature_titles if title not in curated_text]
    if missing_direction_papers:
        fail(f"direction literature papers missing from curated bibliography: {missing_direction_papers}")
    direction_page = (ROOT / "research-directions.html").read_text(encoding="utf-8")
    script_order = [direction_page.find('src="direction-guide-data.js"'), direction_page.find('src="direction-literature-data.js"'), direction_page.find('src="app.js"')]
    if any(position < 0 for position in script_order) or script_order != sorted(script_order):
        fail("research directions page must load direction literature before app.js")

    idea_page = (ROOT / "paper-ideas.html").read_text(encoding="utf-8")
    system_script_order = [
        idea_page.find('src="generated/iclr-low-resource-ideas.js"'),
        idea_page.find('src="generated/machine-school-inspired-ideas.js"'),
        idea_page.find('src="idea-human-review-data.js"'),
        idea_page.find('src="generated/current-final-ideas.js"'),
        idea_page.find('src="generated/paper-first-idea-incubation.js"'),
        idea_page.find('src="content-idea-portfolio.js"'),
        idea_page.find('src="page-architecture-data.js"'),
        idea_page.find('src="paper-first-incubation-view.js"'),
        idea_page.find('src="app.js"'),
    ]
    if any(position < 0 for position in system_script_order) or system_script_order != sorted(system_script_order):
        fail("paper ideas page must load the human-review idea data and current supplemental candidates before app.js")
    idea_app_text = (ROOT / "app.js").read_text(encoding="utf-8")
    pf_view_text = (ROOT / "paper-first-incubation-view.js").read_text(encoding="utf-8")
    idea_css_text = (ROOT / "idea-lab.css").read_text(encoding="utf-8")
    concrete_markers = (
        "PARENT_SIMPLE_COMPARISONS_ZH", "SUPPLEMENTAL_SIMPLE_COMPARISONS_ZH",
        "PARENT_SIMPLE_METHOD_GUIDES_ZH", "SUPPLEMENTAL_SIMPLE_METHOD_GUIDES_ZH",
        "我们的方法怎么做", "简单方法一句话", "简单方法具体怎么做到", "输入看什么", "具体怎么跑", "最后输出什么", "相比复杂方法少了什么", "怎么保证比较公平", "效果差多少",
        "简单方法 +20 个百分点", "少 35 个（47.9%）", "简单规则少 16", "二元稀疏组测试",
        "简单方法 +66.67 个百分点", "简单规则少 24 次（45.3%）",
    )
    if not all(marker in idea_app_text for marker in concrete_markers):
        fail("paper ideas must retain concrete method/baseline designs, matched comparison, and exact deltas")
    if not all(marker in pf_view_text for marker in ("pfSimpleComparisonsZh", "pfSimpleGuidesZh", "简单方法具体怎么做到", "无数值差值；方法预演阶段已停止", "数学上相同", "renderPFComparison")):
        fail("PF design-equivalence closures must explain the simple comparator mechanics and distinguish unrun experiments from numeric ties")
    if not all(marker in idea_css_text for marker in (".concrete-method-comparison", ".comparison-table-wrap", ".simple-method-guide")):
        fail("concrete method comparison / simple-baseline explanation UI styles are missing")
    for filename in ("paper-ideas.html", "system-overview.html"):
        page = (ROOT / filename).read_text(encoding="utf-8")
        if "emerging-niche-policy" in page or "emerging-niche-view" in page or "Emerging-Niche Score" in page:
            fail(f"{filename} must not load the retired Emerging-Niche Score surface")
    for retired in (ROOT / "emerging-niche-view.js", ROOT / "generated" / "emerging-niche-policy.json", ROOT / "generated" / "emerging-niche-policy.js"):
        if retired.exists():
            fail(f"retired Emerging-Niche artifact still exists: {retired.relative_to(ROOT)}")
    incubation = json.loads((ROOT / "generated" / "paper-first-idea-incubation.json").read_text(encoding="utf-8"))
    incubation_summary = incubation.get("summary") or {}
    if (incubation_summary.get("candidates"),incubation_summary.get("advance_to_paper_design"),incubation_summary.get("revise_novelty_boundary"),incubation_summary.get("blocked_collision"),incubation_summary.get("p0_authorized"),incubation_summary.get("gpu_authorized")) != (9,4,3,2,0,0):
        fail(f"paper-first incubation summary is invalid: {incubation_summary}")
    if len({str(row.get("theme") or "") for row in incubation.get("candidates") or []}) < 6:
        fail("paper-first incubation queue collapsed into too few themes")
    state_path = ROOT / "generated" / "research-system-state.json"
    if not state_path.exists():
        fail("research-system-state.json is missing")
    research_state = json.loads(state_path.read_text(encoding="utf-8"))
    if research_state.get("health", {}).get("status") not in {"healthy", "pass"}:
        fail("continuous research system is not healthy/pass")
    summary = research_state.get("summary") or {}
    premature_method_path = ROOT / "generated" / "paper-first-premature-method-diagnostics.json"
    if not premature_method_path.exists():
        fail("paper-first-premature-method-diagnostics.json is missing")
    premature_method = json.loads(premature_method_path.read_text(encoding="utf-8"))
    pmd_summary = premature_method.get("summary") or {}
    if (pmd_summary.get("directions"),pmd_summary.get("completed_diagnostics"),pmd_summary.get("design_holds"),pmd_summary.get("same_information_reducibility_findings"),pmd_summary.get("hidden_executions"),pmd_summary.get("scientifically_authorized"),pmd_summary.get("p0_lifecycle_mutations")) != (2,2,1,2,0,0,0):
        fail(f"premature Paper-first Method diagnostic archive is missing or authoritative: {pmd_summary}")
    if (premature_method.get("authority") or {}).get("cannot_retroactively_authorize") is not True:
        fail("premature Paper-first Method diagnostics must never retroactively create P0 authority")
    if summary.get("papers", 0) < 200 or summary.get("evidence_nodes", 0) <= summary.get("papers", 0):
        fail("continuous research evidence graph is incomplete")
    primary = research_state.get("paper_first_primary_evidence") or {}
    primary_summary = primary.get("summary") or {}
    primary_policy = primary.get("policy") or {}
    if primary.get("status") != "READY" or primary_summary.get("verified") != 32 or primary_policy.get("empirical_fact_precision_gate") is not True or primary_policy.get("empirical_fact_extraction_version") != "precision-v2" or primary_policy.get("derived_empirical_facts_reused_only_when_extractor_version_matches") is not True:
        fail(f"primary-evidence precision state is stale: status={primary.get('status')} summary={primary_summary} policy_version={primary_policy.get('empirical_fact_extraction_version')}")
    if sum(int(value or 0) for value in (primary_summary.get("empirical_fact_tier_counts") or {}).values()) != int(primary_summary.get("empirical_fact_candidates") or 0):
        fail("primary-evidence fact-tier accounting does not match fact-candidate count")
    if str(primary.get("schema_version") or "0") >= "1.1":
        carrier = primary.get("carrier_probe") or {}
        allowed_objects = set(primary_policy.get("scientific_object_lanes") or [])
        if primary_policy.get("no_lane_carrier_probe_enabled") is not True or primary_policy.get("no_lane_carrier_probe_is_existing_object_rescue_only") is not True or primary_policy.get("no_lane_carrier_probe_cannot_create_new_object") is not True or primary_policy.get("no_lane_carrier_probe_has_zero_scientific_authority") is not True or primary_policy.get("no_lane_carrier_probe_failure_prevents_coverage_exhaustion") is not True or primary_policy.get("carrier_probe_pending_skips_live_generator_call") is not True:
            fail("Primary 1.1 no-lane carrier probe policy is incomplete")
        if carrier.get("scientific_authority") is not False or int(carrier.get("pending") or 0) != int(primary_summary.get("carrier_probe_pending") or 0) or bool(carrier.get("complete")) != bool(primary_summary.get("carrier_probe_complete")):
            fail("Primary 1.1 carrier-probe accounting is inconsistent")
        if primary_summary.get("source_coverage_exhausted") is True and int(primary_summary.get("carrier_probe_pending") or 0) > 0:
            fail("Primary 1.1 cannot claim exhausted source coverage with carrier backlog")
        for receipt in carrier.get("portable_receipts") or []:
            scope_excluded = str(receipt.get("probe_outcome") or "") == "SCOPE_EXCLUDED_BY_PRIMARY"
            fulltext_ok = (scope_excluded and not str(receipt.get("fulltext_sha256") or "") and not (receipt.get("live_rescue_eligible_lanes") or [])) or len(str(receipt.get("fulltext_sha256") or "")) == 64
            if receipt.get("scientific_authority") is not False or len(str(receipt.get("primary_sha256") or "")) != 64 or not fulltext_ok or not str(receipt.get("classifier_version") or "") or any(str(value) not in allowed_objects for value in receipt.get("live_rescue_eligible_lanes") or []):
                fail("Primary 1.1 carrier receipt is not zero-authority/content-addressed/existing-object-only")
    generator = research_state.get("paper_first_problem_generator") or {}
    generator_policy = generator.get("policy") or {}
    saturation = generator.get("saturation_memory") or {}
    if generator.get("status") == "GENERATED_ZERO_CANDIDATES" and not str(generator.get("generation_notes") or "").strip():
        fail("zero-candidate problem discovery must expose an auditable rationale")
    if generator_policy.get("zero_candidate_rationale_required") is not True or generator_policy.get("generation_notes_are_advisory_not_scientific_authority") is not True or generator_policy.get("discovery_saturation_memory_has_zero_scientific_authority") is not True or saturation.get("scientific_authority") is not False:
        fail("problem-discovery rationale/saturation memory authority policy is stale")
    if generator.get("status") == "SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE":
        coverage = generator.get("source_coverage") or {}
        if generator_policy.get("incomplete_retrieval_without_new_lane_source_skips_model_call") is not True or generator_policy.get("retrieval_incomplete_is_compute_control_not_scientific_negative") is not True or coverage.get("source_retrieval_complete") is not False or coverage.get("coverage_exhausted") is True or int(coverage.get("unreviewed_lane_linked_sources") or 0) != 0:
            fail("retrieval-incomplete Generator state is not a valid zero-call compute-control terminal")
        if any(int((generator.get("summary") or {}).get(key) or 0) != 0 for key in ("generated","written_to_auto_inbox","semantic_clear","semantic_blocked")):
            fail("retrieval-incomplete Generator cannot expose generated/reviewed candidates")
    if generator.get("status") == "SKIPPED_SOURCE_CARRIER_PROBE_PENDING":
        coverage = generator.get("source_coverage") or {}
        if generator_policy.get("carrier_probe_pending_skips_model_call") is not True or generator_policy.get("carrier_probe_pending_is_compute_control_not_scientific_negative") is not True or coverage.get("coverage_exhausted") is True or coverage.get("carrier_probe_required") is not True or int(coverage.get("carrier_probe_pending") or 0) <= 0 or coverage.get("carrier_probe_complete") is True or int(coverage.get("unreviewed_lane_linked_sources") or 0) != 0:
            fail("carrier-pending Generator state is not a valid zero-call compute-control terminal")
        if any(int((generator.get("summary") or {}).get(key) or 0) != 0 for key in ("generated","written_to_auto_inbox","semantic_clear","semantic_blocked")):
            fail("carrier-pending Generator cannot expose generated/reviewed candidates")
    if research_state.get("collision_engine", {}).get("summary", {}).get("pairwise_comparisons") != 406:
        fail("collision engine did not compare all 29 structured ICLR candidates")
    if research_state.get("pilot_registry", {}).get("summary", {}).get("phases") != 78:
        fail("pilot registry must contain P0/P1/P2 for all 26 passed ICLR ideas")
    if (summary.get("solution_children"), summary.get("solution_shortlist"), summary.get("reviewer_repair_children"), summary.get("reviewer_repair_pass")) != (14,10,6,0):
        fail("research-system state must expose both v3 and v3.1 solution-first rounds")
    if (summary.get("v4_candidates"), summary.get("v4_finalists"), summary.get("v4_revivals")) != (28,16,8):
        fail("research-system state must expose the v4 composition and revival round")
    if (summary.get("v5_candidates"), summary.get("v5_finalists"), summary.get("v5_revivals")) != (36,32,8):
        fail("research-system state must expose the v5 wide-search round")
    components = research_state.get("components", [])
    required_component_sources = {"ResearchAgent", "Human terminal ledger", "P0 retrospective economy review", "Unified P0 decision ledger", "Web GPT + domestic-model independent consultation", "Content-addressed AI consultation automation", "FirstResearch / Popper / Co-Scientist / RD-Agent", "Qiushi / Kosmos / MLEvolve", "MLEvolve / InternAgent / AutoResearchClaw", "ResearchClawBench / HackDetect / ScienceAgentBench / AutoLabs", "External-system intake registry", "Biomni / BioMedAgent / PaperQA2", "AutoResearchBench / PaperQA2 / SciNetBench / ScientistOne / verifier calibration", "Advisor paper-first research contract", "ARIS + local double-funnel", "ARIS portfolio persistence + local scientific gates", "ARIS meta-optimization pattern + local typed failure semantics", "ARIS research wiki pattern + local typed closure"}
    component_sources = {str(item.get("source") or "") for item in components}
    if len(components) < 31 or not required_component_sources.issubset(component_sources):
        fail(f"research-system state is missing current backend responsibilities: count={len(components)}, missing={sorted(required_component_sources-component_sources)}")
    architecture = research_state.get("system_architecture", {})
    architecture_summary = architecture.get("summary", {})
    if (architecture_summary.get("temporal_stages"), architecture_summary.get("reader_chapters"), architecture_summary.get("reader_stage_coverage"), architecture_summary.get("functional_layers"), architecture_summary.get("assigned_components"), architecture_summary.get("unassigned_components"), architecture_summary.get("duplicate_component_keys"), architecture_summary.get("cross_cutting_controls"), architecture_summary.get("orphan_cross_cutting_controls")) != (21,10,21,6,32,0,0,3,0):
        fail(f"backend architecture manifest is incomplete or stale: {architecture_summary}")
    if len({str(item.get("key") or "") for item in components}) != len(components) or any(not item.get("primary_layer") for item in components):
        fail("backend components must expose unique architecture keys and one primary layer each")
    pre_p0 = research_state.get("pre_p0_identifiability", {})
    if pre_p0.get("summary", {}).get("audited") != 4 or pre_p0.get("summary", {}).get("execution_ready") != 0:
        fail(f"Pre-P0 identifiability state is inconsistent: {pre_p0.get('summary')}")
    if research_state.get("pilot_registry", {}).get("summary", {}).get("p0_authorized") != 0:
        fail("P0 authorization must be zero while all current Pre-P0 contracts are blocked")
    graph_component = next((item for item in components if item.get("source") == "ResearchAgent"), {})
    if graph_component.get("component", {}).get("zh") != "引文与证据图谱":
        fail("citation/evidence component must be bilingual in the backend state")
    external_review_store = json.loads((ROOT / "generated" / "iclr-external-reviews.json").read_text(encoding="utf-8"))
    external_status = external_review_store.get("status", {})
    if external_review_store.get("total_passed_ideas") != 26:
        fail("external review store must track all 26 first-round-passed ICLR ideas")
    if int(external_status.get("reviewed", 0)) != 26 or int(external_status.get("pending", 0)) != 0 or not external_status.get("complete"):
        fail("external review store must report 26 reviewed, zero pending, and complete")
    expected_external_verdicts = {"pass": 4, "revise": 10, "block": 12, "unknown": 0}
    if external_status.get("verdict_counts") != expected_external_verdicts:
        fail(f"unexpected external verdict distribution: {external_status.get('verdict_counts')}")
    iclr_bank = json.loads((ROOT / "generated" / "iclr-low-resource-ideas.json").read_text(encoding="utf-8"))
    iclr_summary = iclr_bank.get("summary", {})
    if (iclr_summary.get("project_web_gpt_reviewed"), iclr_summary.get("project_web_gpt_pending"), iclr_summary.get("project_web_gpt_complete")) != (26, 0, True):
        fail("ICLR bank external-review completion summary is inconsistent")
    if (iclr_summary.get("external_pass"), iclr_summary.get("external_revise"), iclr_summary.get("external_block")) != (4, 10, 12):
        fail("ICLR bank external verdict counts are inconsistent")
    ideas = iclr_bank.get("passed_ideas", [])
    if [idea.get("external_verdict") for idea in ideas[:4]] != ["pass"] * 4:
        fail("R2 ranking must place all four PASS ideas first")
    if sorted(idea.get("programmatic_rank") for idea in ideas) != list(range(1, 27)):
        fail("ICLR bank must preserve all original R1 ranks")

    inspired_bank = json.loads((ROOT / "generated" / "machine-school-inspired-ideas.json").read_text(encoding="utf-8"))
    inspired_summary = inspired_bank.get("summary", {})
    expected_inspired = {
        "raw": 24,
        "internal_pass": 11,
        "internal_revise": 7,
        "internal_reject": 6,
        "external_reviewed": 11,
        "external_pass": 1,
        "external_revise": 7,
        "external_block": 3,
    }
    if any(inspired_summary.get(key) != value for key, value in expected_inspired.items()):
        fail(f"unexpected inspired-bank summary: {inspired_summary}")
    inspired_passed = inspired_bank.get("passed_ideas", [])
    if len(inspired_passed) != 11 or [item.get("external_rank") for item in inspired_passed] != list(range(1, 12)):
        fail("inspired-bank external ranking is incomplete")
    if inspired_passed[0].get("id") != "regression-probe-half-life" or inspired_passed[0].get("final_status") != "pilot-now":
        fail("Regression-Probe Half-Life must be the sole pilot-now inspired idea")
    if len(inspired_bank.get("teacher_shortlist", [])) != 8:
        fail("inspired-bank teacher shortlist must contain eight decision candidates")
    discovery_v4 = json.loads((ROOT / "generated" / "idea-discovery-v4.json").read_text(encoding="utf-8"))
    v4_summary = discovery_v4.get("summary", {})
    if (v4_summary.get("raw_candidates"), v4_summary.get("discussion"), v4_summary.get("revival"), v4_summary.get("repair"), v4_summary.get("component"), v4_summary.get("tournament_finalists")) != (28, 14, 8, 4, 2, 16):
        fail(f"unexpected Idea Discovery v4 structure: {v4_summary}")
    if len(discovery_v4.get("repository_patterns", [])) != 11 or len(discovery_v4.get("workflow_stages", [])) != 9:
        fail("Idea Discovery v4 must expose eleven repository patterns and nine workflow stages")
    if len(discovery_v4.get("all_candidates", [])) != 28 or len(discovery_v4.get("tournament_finalists", [])) != 16:
        fail("Idea Discovery v4 candidate or finalist list is incomplete")
    if any(not item.get("composition_logic", {}).get("zh") or not item.get("mechanism_atoms") for item in discovery_v4.get("all_candidates", [])):
        fail("Idea Discovery v4 contains an unstructured composition")
    if any(not item.get("revival_condition", {}).get("zh") for item in discovery_v4.get("revival", [])):
        fail("Idea Discovery v4 revival branches lack material revival conditions")
    v4_external = json.loads((ROOT / "generated" / "idea-discovery-v4-external-reviews.json").read_text(encoding="utf-8"))
    v4_status = v4_external.get("status", {})
    if (v4_status.get("reviewed"), v4_status.get("pending")) != (v4_summary.get("external_reviewed"), v4_summary.get("external_pending")):
        fail("Idea Discovery v4 review store and public summary disagree")
    expected_v4_verdicts = {"pass": v4_summary.get("external_pass", 0), "revise": v4_summary.get("external_revise", 0), "block": v4_summary.get("external_block", 0), "unknown": v4_summary.get("external_pending", 0)}
    if v4_status.get("verdict_counts") != expected_v4_verdicts:
        fail(f"Idea Discovery v4 external verdict counts are inconsistent: {v4_status.get('verdict_counts')}")

    discovery_v5 = json.loads((ROOT / "generated" / "idea-discovery-v5.json").read_text(encoding="utf-8"))
    v5_summary = discovery_v5.get("summary", {})
    if (v5_summary.get("raw_candidates"), v5_summary.get("finalist"), v5_summary.get("revival"), v5_summary.get("repair"), v5_summary.get("component")) != (36,24,8,2,2):
        fail(f"unexpected Idea Discovery v5 structure: {v5_summary}")
    if len(discovery_v5.get("finalists", [])) != 32 or len(discovery_v5.get("repository_patterns", [])) < 13:
        fail("Idea Discovery v5 finalist pool or repository patterns are incomplete")
    if any(not item.get("necessity_logic", {}).get("zh") or not item.get("strongest_baseline", {}).get("zh") for item in discovery_v5.get("all_candidates", [])):
        fail("Idea Discovery v5 contains a candidate without a simplification/necessity contract")
    v5_external_path = ROOT / "generated" / "idea-discovery-v5-external-reviews.json"
    if v5_external_path.exists():
        v5_external = json.loads(v5_external_path.read_text(encoding="utf-8")); v5_status = v5_external.get("status", {})
        if (v5_status.get("reviewed"), v5_status.get("pending")) != (v5_summary.get("external_reviewed"), v5_summary.get("external_pending")):
            fail("Idea Discovery v5 review store and public summary disagree")
    expected_repair_rounds = {
        "idea-discovery-v51.json": (19, 19, 3),
        "idea-discovery-v52.json": (12, 12, 1),
        "idea-discovery-v53.json": (4, 4, 3),
    }
    for filename, expected in expected_repair_rounds.items():
        payload = json.loads((ROOT / "generated" / filename).read_text(encoding="utf-8"))
        summary = payload.get("summary", {})
        if (summary.get("children"), summary.get("reviewed"), summary.get("pass")) != expected:
            fail(f"unexpected repair-round summary for {filename}: {summary}")
    discussion = json.loads((ROOT / "generated" / "discussion-ready-ideas.json").read_text(encoding="utf-8"))
    if int(discussion.get("count") or 0) < int(discussion.get("target") or 0) or discussion.get("remaining") != 0 or discussion.get("ready") is not True:
        fail(f"strict discussion-ready portfolio has not reached minimum target: {discussion}")

    discovery_v3 = json.loads((ROOT / "generated" / "idea-discovery-v3.json").read_text(encoding="utf-8"))
    v3_summary = discovery_v3.get("summary", {})
    if (v3_summary.get("raw_children"), v3_summary.get("internal_shortlist"), v3_summary.get("repair"), v3_summary.get("external_reviewed"), v3_summary.get("external_revise"), v3_summary.get("external_block"), v3_summary.get("external_pass")) != (14, 10, 4, 10, 6, 4, 0):
        fail(f"unexpected solution-first v3 summary: {v3_summary}")
    if len(discovery_v3.get("repository_patterns", [])) != 7 or len(discovery_v3.get("workflow_stages", [])) != 9 or len(discovery_v3.get("solution_gates", [])) != 5:
        fail("solution-first v3 must preserve seven GitHub patterns, nine workflow stages, and five mechanism gates")
    for item in discovery_v3.get("shortlist", []):
        if not item.get("exact_mechanism", {}).get("zh") or not item.get("independent_ground_truth", {}).get("zh"):
            fail(f"solution-first child is not concretized: {item.get('id')}")

    discovery_v31 = json.loads((ROOT / "generated" / "idea-discovery-v31.json").read_text(encoding="utf-8"))
    v31_summary = discovery_v31.get("summary", {})
    if (v31_summary.get("children"), v31_summary.get("external_reviewed"), v31_summary.get("external_pass"), v31_summary.get("external_revise"), v31_summary.get("external_block")) != (6,6,0,2,4):
        fail(f"unexpected reviewer-repair v3.1 summary: {v31_summary}")
    if any(not item.get("exact_mechanism", {}).get("zh") for item in discovery_v31.get("children", [])):
        fail("v3.1 reviewer-repaired children are not algorithmically specified")

    inspired_external = json.loads((ROOT / "generated" / "machine-school-external-reviews.json").read_text(encoding="utf-8"))
    inspired_status = inspired_external.get("status", {})
    if (inspired_status.get("reviewed"), inspired_status.get("pending"), inspired_status.get("complete")) != (11, 0, True):
        fail("inspired external review must report 11 reviewed and zero pending")
    if inspired_status.get("verdict_counts") != {"pass": 1, "revise": 7, "block": 3, "unknown": 0}:
        fail("inspired external verdict distribution is inconsistent")

    system_page = (ROOT / "system-overview.html").read_text(encoding="utf-8")
    required_system_scripts = [
        "generated/s2-literature.js",
        "generated/research-system-state.js",
        "generated/research-memory-wiki.js",
        "generated/iclr-agent-paper-template.js",
        "content-system-overview.js",
        "page-architecture-data.js",
        "system-overview-core.js",
        "system-overview-methodology.js",
        "system-overview-lifecycle.js",
        "system-overview-reader.js",
        "system-overview-preflight.js",
        "system-overview-operations.js",
        "system-overview-view.js",
        "app.js",
    ]
    system_positions = [system_page.find(f'src="{name}"') for name in required_system_scripts]
    if any(position < 0 for position in system_positions) or system_positions != sorted(system_positions):
        fail("system overview must load research-system state and modular renderers before app.js")
    forbidden_system_scripts = ("generated/iclr-low-resource-ideas.js", "generated/machine-school-inspired-ideas.js", "generated/discussion-ready-ideas.js", "generated/idea-discovery-v5.js")
    if any(f'src="{name}"' in system_page for name in forbidden_system_scripts):
        fail("system overview must not load current idea-bank or discussion-pool artifacts")
    research_memory = json.loads((ROOT / "generated" / "research-memory-wiki.json").read_text(encoding="utf-8"))
    guidance_rows = [row for row in research_memory.get("entries", []) if row.get("kind") == "PAPER_DEVELOPMENT_GUIDANCE"]
    if len(guidance_rows) != 1 or (research_memory.get("summary") or {}).get("paper_development_guidance") != 1 or (research_memory.get("lint") or {}).get("status") != "PASS":
        fail("Research Memory must expose exactly one lint-clean paper-development guidance entry")
    guidance = guidance_rows[0].get("guidance") or {}; backlog = guidance.get("paper_development_backlog") or []
    if len(guidance.get("dimensions") or []) != 4 or len(backlog) != 5 or any(row.get("maturity") != "INITIAL_DRAFT_NEEDS_DEEPENING" or row.get("paper_only_work_allowed") is not True or row.get("may_execute_new_experiments") is not False for row in backlog):
        fail("Senior paper-development guidance must bind four dimensions and five paper-only initial-draft backlog rows")
    if any((guidance.get("authority") or {}).get(key) is not False for key in ("scientific","method","experiment","gpu","submission")):
        fail("Paper-development guidance must remain zero authority")
    template_path = ROOT / "generated" / "iclr-agent-paper-template.json"
    template = json.loads(template_path.read_text(encoding="utf-8"))
    template_js = (ROOT / "generated" / "iclr-agent-paper-template.js").read_text(encoding="utf-8")
    expected_template_js = "window.ICLR_AGENT_PAPER_TEMPLATE = " + json.dumps(template, ensure_ascii=False, separators=(",", ":")) + ";\n"
    if template_js != expected_template_js:
        fail("ICLR Agent Paper Template JSON/JS projections are not byte-consistent")
    if len(template.get("derived_from") or []) != 8 or len(template.get("experiment_lanes") or []) != 7 or sum(row.get("required") is True for row in template.get("experiment_lanes") or []) != 6 or abs(sum(float(row.get("pages") or 0) for row in template.get("page_budget_main_body") or []) - 9.0) > 1e-9:
        fail("ICLR Agent Paper Template must bind 8 exemplars, 7 lanes / 6 required, and a 9-page main-body budget")
    if any((template.get("authority") or {}).get(key) is not False for key in ("scientific","method","experiment","gpu","submission")):
        fail("ICLR Agent Paper Template must remain zero authority")
    if (guidance.get("manuscript_template") or {}).get("template_id") != template.get("template_id") or any((row.get("manuscript_template_id") != template.get("template_id") or row.get("template_binding_required_on_next_material_revision") is not True) for row in backlog):
        fail("Senior paper-development backlog must bind the current ICLR manuscript template on the next material revision")
    system_files = ["system-overview-core.js", "system-overview-map.js", "system-overview-layers.js", "system-overview-methodology.js", "system-overview-intake.js", "system-overview-lifecycle.js", "system-overview-reader.js", "system-overview-governance-v2.js", "system-overview-preflight.js", "system-overview-operations.js", "system-overview-closure.js", "system-overview-view.js"]
    system_text = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in system_files)
    for marker in ("READ THIS PAGE IN 10 CHAPTERS", "ONE AUTHORITY MODEL", "DECIDE WHETHER A NEW PROBLEM EXISTS", "DESIGN THE SCIENTIFIC CONTRIBUTION BEFORE CODING", "CHECK THE SMALLEST TEST BEFORE GPU", "RUN SMALL, DIAGNOSE, THEN DECIDE WHETHER TO SCALE", "CHECK THAT EVERY CLAIM HAS EVIDENCE", "SEARCH THE STORY, THEN BUILD THE MANUSCRIPT", "SIMULATE REJECTION RISK AND REPAIR WITHIN THE EVIDENCE BOUNDARY", "CLOSE PREBUTTAL, SUBMISSION AUTHORITY, AND REAL REVIEW IN THE SAME LEDGER", "REMEMBER WHY WE CONTINUED, STOPPED, ACCEPTED, OR WERE REJECTED", "TERMINATION & MEMORY AUTHORITY", "WHO OWNS EACH BACKEND JOB", "CROSS-CUTTING METHODOLOGY CONTROLS", "Are candidate problems too similar?", "Search-Time Contamination", "Can another person rerun the key result from scratch?",  "21 BACKEND STEPS FROM LITERATURE TO SUBMISSION LEARNING", "system-layer-list", "P0 ECONOMY", "PRE-EXPERIMENT COMPILER", "8 / 8", "CAN THE EXPERIMENT DISTINGUISH THE MECHANISM?", "10 / 10", "SHADOW SEARCH LAB", "v2.9 · MACHINE-ENFORCED", "LOCAL VALIDATION SUB-MACHINE · P0-SYSTEM v2", "system-failure-layer", "How long experiments are launched safely and resumed after disconnects", "CURRENT DECISION → CAUSE → NEXT-RUN RULE", "PAPER DEVELOPMENT QUALITY V1", "Scientific closure is not the same as manuscript maturity", "Writing requirement: make the paper easy to understand", "ICLR PAPER TEMPLATE V1", "E1–E6 are planning slots"):
        if marker not in system_text:
            fail(f"system overview implementation is missing {marker}")
    shadow_portfolio = json.loads((ROOT / "generated" / "paper-first-problem-search-portfolio-state.json").read_text(encoding="utf-8"))
    shadow_queue = json.loads((ROOT / "generated" / "paper-first-problem-search-portfolio-queue-shadow.json").read_text(encoding="utf-8"))
    if shadow_portfolio.get("scientific_authority") is not False or (shadow_portfolio.get("policy") or {}).get("shadow_only") is not True or (shadow_portfolio.get("summary") or {}).get("live_paper_design_eligible") != 0:
        fail("Search Portfolio history must remain shadow-only with zero live Paper Design eligibility")
    shadow_summary = shadow_portfolio.get("summary") or {}
    if int(shadow_summary.get("generator_model_calls") or 0) < 0 or int(shadow_summary.get("reviewer_model_calls") or 0) < 0 or int(shadow_summary.get("counterfactual_problem_gate_passed") or 0) < 0:
        fail("Search Portfolio shadow provenance counts must be nonnegative")
    if (shadow_queue.get("policy") or {}).get("shadow_only") is not True or (shadow_queue.get("summary") or {}).get("live_paper_design_eligible") != 0:
        fail("Search Portfolio shadow queue must never expose live eligibility")
    latest_shadow = shadow_portfolio.get("latest_run") or {}
    latest_summary = latest_shadow.get("summary") or {}
    latest_run_id = str(shadow_portfolio.get("latest_run_id") or "")
    if not latest_run_id or latest_shadow.get("run_id") != latest_run_id:
        fail(f"latest Search Portfolio run identity is inconsistent: {latest_run_id}/{latest_shadow.get('run_id')}")
    nonnegative_fields = (
        "requested_raw_seeds","expansion_requested_shards","expansion_successful_shards","expansion_execution_failures",
        "raw_seeds","semantic_unique","evolved_branches","evolution_g1_requested","evolution_g1_valid","evolution_g2_requested","evolution_g2_valid",
        "formulation_requested_shards","formulation_successful_shards","formulation_provider_failures","formulation_parse_failures",
        "formulation_requested_branches","formulation_successful_branches","formulation_execution_censored_branches","formulated_candidates",
        "formulation_reduction_pending","formulation_rejected","machine_reviewable","machine_reduction_pending","machine_reduction_blocked",
        "problem_falsifier_eligible","problem_falsifier_inventory_requested","problem_falsifier_support_qualified",
        "problem_falsifier_hold_support_unavailable","problem_falsifier_executed","semantic_clear","terminal_shadow_survivors",
    )
    if any(int(latest_summary.get(key) or 0) < 0 for key in nonnegative_fields):
        fail(f"latest Search Portfolio funnel contains negative counters: {latest_summary}")
    if int(latest_summary.get("expansion_successful_shards") or 0) + int(latest_summary.get("expansion_execution_failures") or 0) != int(latest_summary.get("expansion_requested_shards") or 0):
        fail(f"latest Search Portfolio expansion accounting is inconsistent: {latest_summary}")
    if int(latest_summary.get("formulation_successful_shards") or 0) + int(latest_summary.get("formulation_provider_failures") or 0) + int(latest_summary.get("formulation_parse_failures") or 0) != int(latest_summary.get("formulation_requested_shards") or 0):
        fail(f"latest Search Portfolio formulation-shard accounting is inconsistent: {latest_summary}")
    if int(latest_summary.get("formulation_successful_branches") or 0) + int(latest_summary.get("formulation_execution_censored_branches") or 0) != int(latest_summary.get("formulation_requested_branches") or 0):
        fail(f"latest Search Portfolio formulation-branch accounting is inconsistent: {latest_summary}")
    if int(latest_summary.get("formulated_candidates") or 0) + int(latest_summary.get("formulation_reduction_pending") or 0) + int(latest_summary.get("formulation_rejected") or 0) != int(latest_summary.get("formulation_successful_branches") or 0):
        fail(f"latest Search Portfolio formulation disposition accounting is inconsistent: {latest_summary}")
    if int(latest_summary.get("problem_falsifier_eligible") or 0) != int(latest_summary.get("machine_reduction_pending") or 0):
        fail(f"latest Search Portfolio falsifier eligibility must track machine reduction-pending objects: {latest_summary}")
    latest_policy = latest_shadow.get("policy") or {}; latest_authority = latest_shadow.get("authority") or {}
    inventory_requested = int(latest_summary.get("problem_falsifier_inventory_requested") or 0)
    inventory_policy_ok = latest_policy.get("problem_falsifier_support_inventory_hash_verified") is True if inventory_requested else latest_policy.get("support_inventory_is_one_evidence_route_not_global_prerequisite") is True
    if latest_shadow.get("status") != "SHADOW_TERMINAL_COMPLETE" or latest_shadow.get("scientific_authority") is not False or latest_policy.get("current_source_web_receipt_required_after_semantic_clear") is not True or latest_policy.get("missing_or_failed_current_source_reviewer_is_not_pass") is not True or latest_policy.get("execution_loss_is_not_scientific_negative") is not True or latest_policy.get("problem_falsifier_hold_is_not_scientific_fail") is not True or not inventory_policy_ok or int(latest_summary.get("current_source_missing") or 0) != 0 or int(latest_summary.get("live_paper_design_eligible") or 0) != 0 or any(latest_authority.get(key) is not False for key in ("live_problem_gate","paper_design","method","experiment","p0","gpu")):
        fail("latest Search Portfolio terminal must be complete, fail-closed on current-source review, and zero-authority")
    latest_queue = shadow_queue.get("latest_run") or {}; latest_queue_summary = latest_queue.get("summary") or {}
    if shadow_queue.get("latest_run_id") != latest_run_id or latest_queue.get("run_id") != latest_run_id or int(latest_queue_summary.get("terminal_shadow_survivors") or 0) != 0 or int(latest_queue_summary.get("live_paper_design_eligible") or 0) != 0:
        fail("shadow queue latest-run projection must match the current portfolio run and remain zero-survivor/zero-live-authority")
    system_content = (ROOT / "content-system-overview.js").read_text(encoding="utf-8")
    forbidden_idea_markers = ("主 ICLR Idea Bank", "最终师兄讨论门槛", "Main ICLR idea bank", "Final advisor gate", "paper-ideas.html#discussed-ideas")
    if any(marker in system_text or marker in system_content for marker in forbidden_idea_markers):
        fail("system overview must contain only the research system, not current idea decisions")
    for marker in ("自动执行", "条件自动", "人工控制", "8/8 Pre-Experiment", "10/10 identifiability", "整体流程与权限：从研究问题到实验，再到论文", "确认是否真的存在新的科学问题", "写代码前先把科学贡献设计完整", "找到最便宜、但足以改变结论的实验", "先小规模验证，弄清失败原因，再决定是否扩量", "冻结论文科学证据", "先选出最佳故事线，再形成成稿", "模拟审稿、定向修稿与主张审计", "投稿准备、人工授权与真实审稿", "记住为什么继续、停止、被接收或被拒绝", "当前科学结论记录"):
        if marker not in system_text and marker not in system_content and marker not in (ROOT / "page-architecture-data.js").read_text(encoding="utf-8"):
            fail(f"Chinese research-system documentation is missing {marker}")

    for figure_name in ("agent-self-evolution-directions-en.svg", "agent-self-evolution-directions-zh.svg"):
        try:
            figure_root = ET.parse(ROOT / figure_name).getroot()
        except ET.ParseError as error:
            fail(f"invalid SVG {figure_name}: {error}")
        if len(figure_root.findall('.//*[@data-paper]')) != 20:
            fail(f"{figure_name} must cite two representative papers for each of ten directions")

    explanations_text = (ROOT / "idea-explanations.js").read_text(encoding="utf-8")
    explanation_blocks = re.findall(r'^  "([^"]+)": \{\n(.*?)(?=^  "[^"]+": \{|^\};)', explanations_text, re.MULTILINE | re.DOTALL)
    explanation_names = [name for name, _ in explanation_blocks]
    if sorted(explanation_names) != sorted(names) or len(explanation_names) != len(set(explanation_names)):
        fail("each paper idea must have exactly one explanation block")
    required_fields = ("purpose", "core", "rationale", "logic")
    for name, block in explanation_blocks:
        for field in required_fields:
            match = re.search(rf'{field}:\{{en:"([^"]+)",zh:"([^"]+)"\}}', block)
            if not match or not match.group(1).strip() or not match.group(2).strip():
                fail(f"idea {name} is missing bilingual {field}")

    comparisons_text = (ROOT / "idea-comparisons.js").read_text(encoding="utf-8")
    comparison_blocks = re.findall(r'^  "([^"]+)": \{\n(.*?)(?=^  "[^"]+": \{|^\};)', comparisons_text, re.MULTILINE | re.DOTALL)
    comparison_names = [name for name, _ in comparison_blocks]
    if sorted(comparison_names) != sorted(names) or len(comparison_names) != len(set(comparison_names)):
        fail("each paper idea must have exactly one importance/advantage block")
    for name, block in comparison_blocks:
        for field in ("importance", "advantage"):
            match = re.search(rf'{field}:\{{en:"([^"]+)",zh:"([^"]+)"\}}', block)
            if not match or not match.group(1).strip() or not match.group(2).strip():
                fail(f"idea {name} is missing bilingual {field}")

    history_text = (ROOT / "history-figure-data.js").read_text(encoding="utf-8")
    if len(re.findall(r'^\s*\{?\s*code:"P\d"', history_text, re.MULTILINE)) != 6:
        fail("history figure must contain six stages")
    if len(re.findall(r'^\s*\{name:\{en:', history_text, re.MULTILINE)) != 5:
        fail("history figure must contain five capability rows")
    if len(re.findall(r'^\s*\{code:"D\d+"', history_text, re.MULTILINE)) != 10:
        fail("history figure must contain ten research directions")
    milestones = re.findall(r'\{year:\d{4},short:"[^"]+",title:"([^"]+)"', history_text)
    if len(milestones) != 23 or len(set(milestones)) != 23:
        fail("history figure must contain 23 unique published milestones")
    data_text = (ROOT / "data.js").read_text(encoding="utf-8")
    missing_milestones = [title for title in milestones if title not in data_text]
    if missing_milestones:
        fail(f"history milestones missing from curated bibliography: {missing_milestones}")
    for figure_name, method_label in [("agent-self-evolution-history-en.svg", "Update:"), ("agent-self-evolution-history-zh.svg", "更新：")]:
        figure_path = ROOT / figure_name
        try:
            root = ET.parse(figure_path).getroot()
        except ET.ParseError as error:
            fail(f"invalid SVG {figure_name}: {error}")
        milestone_nodes = root.findall(".//*[@data-milestone]")
        figure_text = figure_path.read_text(encoding="utf-8")
        if len(milestone_nodes) != 23:
            fail(f"{figure_name} must contain 23 milestone method cards")
        if figure_text.count(method_label) < 23:
            fail(f"{figure_name} must describe the update target for every milestone")

    paper_analysis_text = (ROOT / "paper-analysis-data.js").read_text(encoding="utf-8")
    method_note_titles = re.findall(r'^  "([^"]+)": \{', paper_analysis_text, re.MULTILINE)
    if len(method_note_titles) < 23 or len(method_note_titles) != len(set(method_note_titles)):
        fail("paper analysis data must contain at least 23 unique paper-specific method notes")
    missing_method_notes = [title for title in method_note_titles if title not in data_text]
    if missing_method_notes:
        fail(f"paper-specific method notes missing from curated bibliography: {missing_method_notes}")

    top_analysis_text = (ROOT / "top-paper-analysis-data.js").read_text(encoding="utf-8")
    top_blocks = re.findall(r'^  "([^"]+)": \{\n(.*?)(?=^  "[^"]+": \{|^\};)', top_analysis_text, re.MULTILINE | re.DOTALL)
    if len(top_blocks) != 24 or len({title for title, _ in top_blocks}) != 24:
        fail("top-paper analysis must contain exactly 24 unique paper analyses")
    for title, block in top_blocks:
        if title not in data_text:
            fail(f"top-paper analysis missing from curated bibliography: {title}")
        for field in ("problem", "advantage", "intuition", "rationale", "flow", "validation"):
            match = re.search(rf'{field}:\{{en:"([^"]+)",zh:"([^"]+)"\}}', block)
            if not match or not match.group(1).strip() or not match.group(2).strip():
                fail(f"top paper {title} is missing bilingual {field}")

    ranking_text = (ROOT / "citation-ranking-data.js").read_text(encoding="utf-8")
    for sort_id in ("priority", "citations", "venue", "recent"):
        if f'id:"{sort_id}"' not in ranking_text:
            fail(f"citation ranking config is missing sort mode {sort_id}")
    if len(re.findall(r'label:"[^"]+",pattern:', ranking_text)) < 15:
        fail("citation ranking config must define at least 15 top-venue patterns")
    role_ids = re.findall(r'\{id:"([a-z-]+)",rank:\d+,title:', ranking_text)
    expected_roles = ["must-read", "field-overview", "core-evolution", "evaluation-governance", "enabling-mechanism", "agent-foundation", "model-foundation", "adjacent"]
    if role_ids != expected_roles:
        fail(f"reading-role order is incomplete or unstable: {role_ids}")
    if ranking_text.count("mustReadAnchors") != 1 or len(re.findall(r'\{title:"[^"]+",rank:\d+,reason:', ranking_text)) < 10:
        fail("bibliography must keep a small explicit must-read anchor set ahead of general surveys")
    if ranking_text.count("citationCount:") < 20 or "snapshotUpdatedAt:" not in ranking_text:
        fail("citation ranking config must contain a dated deployment snapshot for at least 20 core papers")
    bibliography_html = (ROOT / "bibliography.html").read_text(encoding="utf-8")
    required_bibliography_scripts = ["citation-ranking-data.js", "paper-analysis-data.js", "top-paper-analysis-data.js", "published-literature-data.js", "published-paper-evidence-core1.js", "published-paper-evidence-core2.js", "published-paper-evidence-core3.js", "published-paper-evidence-core4.js", "literature-idea-mining-data-1.js", "literature-idea-mining-data-2.js", "literature-idea-mining-data-3.js", "generated/literature-idea-mining-collision.js", "app.js"]
    script_positions = [bibliography_html.find(f'src="{name}"') for name in required_bibliography_scripts]
    if any(position < 0 for position in script_positions) or script_positions != sorted(script_positions):
        fail("bibliography must load ranking and analysis scripts before app.js")
    if "window.LITERATURE_REFRESH_META" not in data_text or not all(marker in data_text for marker in ("verified_at:\"2026-08-22\"", "added:27", "added:6", "updated:1", "Authenticated Semantic Scholar Academic Graph", "API key 不进入网页产物")):
        fail("bibliography must publish the 2026-08-22 incremental literature-refresh provenance without exposing the Semantic Scholar API key")
    for filename in CANONICAL_PAGES:
        if filename == "research-timeline.html":
            continue
        html = (ROOT / filename).read_text(encoding="utf-8")
        if html.find('src="citation-ranking-data.js"') < 0 or html.find('src="citation-ranking-data.js"') > html.find('src="app.js"'):
            fail(f"{filename} must load citation-ranking-data.js before app.js for stable reference numbering")

    app_text = (ROOT / "app.js").read_text(encoding="utf-8")
    if "bibliography-refresh-log" not in app_text or "LATEST VERIFIED DELTA" not in app_text or "Semantic Scholar + arXiv" not in app_text:
        fail("bibliography must render the latest incremental literature-refresh provenance before the bulk Semantic Scholar snapshot")
    for marker in ["Problem motivation", "Comparative advantage", "Core intuition", "Why it should work", "Method flow", "Experimental validation"]:
        if marker not in app_text:
            fail(f"paper-card analysis renderer is missing {marker}")
    for marker in ["paperConcreteDesign", "paperSpecificFlow", "Concrete design: how the paper actually works", "designComponents", "designInputs", "designLoop", "designArtifact", "designAcceptance"]:
        if marker not in app_text:
            fail(f"paper-card concrete implementation breakdown is missing {marker}")
    published_text = (ROOT / "published-literature-data.js").read_text(encoding="utf-8")
    for marker in ["Agent 到底应该学什么？", "经验应该变成什么？", "D1", "D10", "全部追加 + Top-K 相似度检索", "固定工具/API", "固定训练集 + 固定 reward"]:
        if marker not in published_text:
            fail(f"published-literature reading spine is missing concrete baseline marker: {marker}")
    for marker in ["renderPublishedSpine", "renderPublishedComparisons", "renderPublishedQuickRead", "publishedLiteratureAudit", "publishedEvidenceOverride", "missingMustReadEvidence", "30 秒读懂这篇正式论文", "实验实际看到了什么"]:
        if marker not in app_text:
            fail(f"published-literature renderer is missing {marker}")
    for marker in ["renderLiteratureIdeaMining", "literatureIdeaMiningAudit", "高碰撞排除项", "还值得继续挖的断层", "后续 API 碰撞优先问", "再撞我们自己当前 ResearchItem", "一个文献空白什么时候才值得升级成候选研究问题"]:
        if marker not in app_text:
            fail(f"literature idea-mining renderer is missing {marker}")
    idea_mining_text = "\n".join((ROOT / f"literature-idea-mining-data-{i}.js").read_text(encoding="utf-8") for i in range(1,4))
    for marker in ["D1:{opportunity", "D10:{opportunity", "X8", "persistent experience admission causal effect transport", "agent self evolution governance evidence allocation", "只有这 7 项"]:
        if marker not in idea_mining_text and marker not in app_text:
            fail(f"literature idea-mining data is missing: {marker}")
    if sum(idea_mining_text.count(f"{code}:{{opportunity") for code in [f"D{i}" for i in range(1,11)]) != 10:
        fail("literature idea-mining registry must contain exactly one D1-D10 opportunity record each")
    idea_mining_json = json.loads((ROOT / "literature-idea-mining-data.json").read_text(encoding="utf-8"))
    if idea_mining_json.get("schemaVersion") != "1.0" or list((idea_mining_json.get("directions") or {}).keys()) != [f"D{i}" for i in range(1,11)] or len(idea_mining_json.get("intersections") or []) != 8 or len(idea_mining_json.get("candidateContract") or []) != 7:
        fail("machine-readable literature idea-mining registry is incomplete or out of sync")
    expected_gap_category_map = {"D1":["A","B","D"],"D2":["B"],"D3":["E","G"],"D4":["A","E"],"D5":["F"],"D6":["C","G"],"D7":["A","G"],"D8":["A","D","G"],"D9":["B","C","D"],"D10":["A","B"]}
    if idea_mining_json.get("currentCategoryMap") != expected_gap_category_map:
        fail(f"literature gap registry current A-G collision map drifted: {idea_mining_json.get('currentCategoryMap')}")
    idea_input = json.loads((ROOT / "generated/literature-idea-mining-input.json").read_text(encoding="utf-8"))
    idea_policy = idea_input.get("projection_policy") or {}
    if idea_input.get("schema_version") != "1.0" or len(idea_input.get("directions") or {}) != 10 or len(idea_input.get("intersections") or []) != 8 or len(idea_input.get("candidate_contract") or []) != 7:
        fail("generated literature idea-mining input bundle is incomplete")
    if idea_policy.get("read_only") is not True or any(idea_policy.get(key) is not False for key in ("scientific_authority","experiment_authority","promotion_authority")) or idea_policy.get("gap_is_not_an_idea") is not True:
        fail(f"literature idea-mining input must remain a read-only zero-authority projection: {idea_policy}")
    if (idea_input.get("directions") or {}).get("D7",{}).get("current_categories") != ["A","G"]:
        fail("D7 idea-mining bundle must collide persistent-state security gaps against current A/G ResearchItems")
    collision_text = (ROOT / "generated/literature-idea-mining-collision.js").read_text(encoding="utf-8")
    if not collision_text.startswith("window.LITERATURE_IDEA_COLLISIONS = "):
        fail("compact literature idea collision projection is missing")
    collision_payload = json.loads(collision_text.split("=",1)[1].strip().rstrip(";"))
    if int(collision_payload.get("research_items") or 0) < 80 or len(collision_payload.get("directions") or {}) != 10 or len(((collision_payload.get("directions") or {}).get("D7") or {}).get("active") or []) < 1:
        fail(f"compact literature idea collision projection is incomplete: {collision_payload}")
    evidence_text = "\n".join((ROOT / f"published-paper-evidence-core{i}.js").read_text(encoding="utf-8") for i in range(1,5))
    if evidence_text.count("source:{zh:") != 22:
        fail("all 22 A-tier must-read publications need paper-specific source-grounded evidence")
    for marker in ["HumanEval pass@1 = 91%", "4.8% 提到 42.4%", "平均比当时 SOTA 自动工作流方法高 5.7%", "general benchmark 平均 +2.4%", "57.8%", "正式摘要没有给一个可安全概括的统一平均百分点"]:
        if marker not in evidence_text:
            fail(f"paper-specific published evidence is missing concrete result marker: {marker}")
    if "Semantic Scholar retrieval" not in (ROOT / "generated/s2-literature.js").read_text(encoding="utf-8") or "semantic scholar retrieval" not in app_text.lower():
        fail("Semantic Scholar retrieval provenance must remain present in the raw snapshot and explicitly handled by the analysis layer")
    for marker in ["sortBibliographyRecords", "publicationTier", "readingRoleInfo", "renderRecommendedPaperGroups", "bibliography-sort", "citation-ranking-status", "citationCount"]:
        if marker not in app_text:
            fail(f"literature ranking implementation is missing {marker}")

    literature_nav = re.search(r'\{ title:\{en:"Literature",zh:"文献"\}, open:true, pages:\[(.*?)\]\}', data_text, re.DOTALL)
    if not literature_nav or '"bibliography.html",{en:"Literature Library · Spine & Research Gaps",zh:"文献库 · 主线与研究空白"}' not in literature_nav.group(1):
        fail("Literature navigation must be default-open and use the canonical bibliography label")
    if '"selected-paper.html",{en:"Papers · PaperRegistry",zh:"论文 · PaperRegistry"}' not in data_text:
        fail("PaperRegistry navigation label must be canonical in both languages")
    if 'const LANGUAGE_STORAGE_KEY = "agent-evolution-language";' not in app_text or 'localStorage.setItem(LANGUAGE_STORAGE_KEY, language);' not in app_text or "scopedLanguageKey" in app_text:
        fail("all canonical pages must share one sidebar language state instead of page-scoped navigation language")

    public_role_assets = [
        *(ROOT / name for name in CANONICAL_PAGES),
        *ROOT.glob("*.js"),
        *(ROOT / "generated").glob("*.js"),
        *(ROOT / "generated").glob("*.json"),
    ]
    role_term_leaks = [str(path.relative_to(ROOT)) for path in public_role_assets if path.is_file() and "师兄" in path.read_text(encoding="utf-8", errors="ignore")]
    if role_term_leaks:
        fail(f"public pages/assets must use role-neutral decision language; residual role term found in: {role_term_leaks[:12]}")

    nav_targets = sorted(set(re.findall(r'\["([a-z0-9-]+\.html)"', data_text.split("window.SUPPLEMENTAL_PAPERS", 1)[0])))
    expected_nav = set(CANONICAL_PAGES) - {"experiments.html"}
    if set(nav_targets) != expected_nav:
        fail(f"primary navigation must contain canonical reader pages while keeping experiments as a deep-audit route: {nav_targets}")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for filename in CANONICAL_PAGES:
        url = "https://agent-evolution.lightrain.asia/" if filename == "index.html" else f"https://agent-evolution.lightrain.asia/{filename}"
        if url not in sitemap:
            fail(f"sitemap missing canonical page {filename}")
    for filename in REDIRECT_PAGES:
        if f"https://agent-evolution.lightrain.asia/{filename}" in sitemap:
            fail(f"sitemap must not index redirect page {filename}")

    all_checked = [*(ROOT / name for name in CANONICAL_PAGES), ROOT / "404.html", *js_files, ROOT / "style.css"]
    for path in all_checked:
        text = path.read_text(encoding="utf-8")
        for placeholder in PLACEHOLDERS:
            if placeholder in text:
                fail(f"placeholder {placeholder!r} remains in {path.name}")

    cname = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
    if cname != "agent-evolution.lightrain.asia":
        fail(f"unexpected CNAME: {cname}")

    print("PASS")
    print(f"Canonical pages: {len(CANONICAL_PAGES)}")
    print(f"Compatibility redirects: {len(REDIRECT_PAGES)}")
    print(f"JavaScript files checked: {len(js_files)}")
    print(f"Navigation targets: {len(nav_targets)}")


if __name__ == "__main__":
    main()
