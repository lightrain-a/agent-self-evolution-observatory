from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .config import PROJECT_ROOT, SemanticScholarSettings, StorageSettings
from .ai_consultation_automation import run_ai_consultation_automation
from .cvpr_idea_factory import write_cvpr_idea_bank
from .discussion_portfolio import write_discussion_portfolio
from .emerging_niche import write_emerging_niche_policy
from .human_terminal_state import write_human_terminal_state
from .p0_admission import write_p0_admission_state
from .p0_b10_cpu import write_b10_cpu_p0
from .p0_a12_soft_audit_f0 import write as write_a12_soft_audit_f0
from .p0_a3_substrate_stop import write_state as write_a3_substrate_stop
from .p0_a4_composition_cpu import write_a4_cpu_p0
from .p0_a5_history_cpu import write_a5_cpu_p0
from .p0_a6_cpu import write_a6_cpu_p0
from .p0_a7_counterfactual_cpu import write_a7_cpu_p0
from .p0_b2_support_stop import write_state as write_b2_support_stop
from .p0_b3_interference_cpu import write_b3_cpu_screen
from .p0_b3_fresh_support_stop import write_state as write_b3_fresh_support_stop
from .p0_b3_real_state import write_state as write_b3_real_state
from .p0_b5_applicability_cpu import write_b5_cpu_p0
from .p0_b6_memory_utility_cpu import write_b6_cpu_p0
from .p0_c2_evaluator_cpu import write_c2_cpu_p0
from .p0_d1_minimal_curriculum_cpu import write_d1_cpu_p0
from .p0_e1_edit_table_stop import write_state as write_e1_table_stop
from .p0_e2_workflow_cpu import write_e2_cpu_p0
from .p0_e3_real_api import write as write_e3_real_api_p0
from .p0_e3_stateful import write_stateful as write_e3_stateful_p0
from .p0_e4_permission_cpu import write_state as write_e4_permission_p0
from .p0_offline_qualification import write_p0_offline_qualification_state
from .p0_realizability_suite import write_p0_realizability_suite
from .p0_revived_batch_f0 import write_revived_batch_f0
from .iclr_experiment_audit import write_audit as write_iclr_audit
from .iclr_idea_factory import write_iclr_idea_bank
from .idea_discovery_v3 import write_idea_discovery_v3
from .idea_discovery_v31 import write_idea_discovery_v31
from .idea_discovery_v5 import write_idea_discovery_v5
from .idea_discovery_v51 import write_idea_discovery_v51
from .idea_discovery_v52 import write_idea_discovery_v52
from .idea_discovery_v53 import write_idea_discovery_v53
from .idea_discovery_v4 import write_idea_discovery_v4
from .machine_school_idea_factory import write_machine_school_bank
from .live_pipeline import sync_semantic_scholar
from .published_experiment_audit import write_audit as write_published_audit
from .paper_first_idea_incubation import write_paper_first_idea_incubation
from .paper_first_fresh_saturation import write_fresh_saturation_state
from .paper_first_discovery_transaction import write_problem_discovery_transaction
from .paper_first_discovery_frontier import build_paper_first_discovery_frontier
from .paper_first_global_relation_recall import load_global_relation_recall_state, write_global_relation_recall_state
from .paper_first_global_relation_scan_admission import build_global_relation_scan_admission, public_global_relation_scan_admission_summary
from .paper_first_primary_evidence import load_primary_evidence_state
from .paper_first_problem_generator import load_problem_generator_state
from .paper_first_problem_gate_queue import load_problem_gate_queue_state
from .paper_first_shadow_search_admission import build_shadow_search_admission, public_shadow_search_admission_summary
from .paper_first_shadow_continuation_frontier import build_shadow_continuation_frontier
from .paper_first_relation_coverage import relation_recall_freshness
from .paper_first_relation_delta_preflight import load_private_relation_delta_preflight, public_relation_delta_preflight_summary, write_private_relation_delta_preflight
from .paper_first_relation_cache_backfill import backfill_relation_cache
from .paper_first_paper_design_backlog import write_paper_design_backlog
from .paper_first_p0_f0 import write_paper_first_p0_f0_state
from .paper_first_scientific_object_candidate_evidence import load_scientific_object_candidate_evidence_ledger, public_scientific_object_candidate_evidence_summary
from .paper_first_scientific_object_maintenance import run_shadow_scientific_object_maintenance
from .paper_first_support_release_watch import load_private_support_release_watch, public_support_release_watch_summary, run_support_release_watch
from .paper_first_support_asset_recheck import load_private_support_asset_recheck_queue, public_support_asset_recheck_summary, write_private_support_asset_recheck_queue
from .paper_first_support_asset_recheck_handoff import load_private_support_asset_recheck_handoff, public_support_asset_recheck_handoff_summary, write_private_support_asset_recheck_handoff
from .research_system import write_research_system_state
from .publication import PUBLICATION_OK_STATES, publish_generated_state


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@contextmanager
def cycle_lock(path: Path, *, stale_after_seconds: float = 21600) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        lock_pid = 0
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            lock_pid = int(payload.get("pid") or 0) if isinstance(payload, dict) else 0
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            lock_pid = 0
        if lock_pid and not _pid_is_alive(lock_pid):
            path.unlink(missing_ok=True)
        elif not lock_pid and time.time() - path.stat().st_mtime > stale_after_seconds:
            path.unlink(missing_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise RuntimeError(f"Another automation cycle is active: {path}") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({"pid": os.getpid(), "started_at": _now()}))
        yield
    finally:
        path.unlink(missing_ok=True)


def _run_global_relation_control(
    *,
    storage: StorageSettings,
    mode: str,
    allow_model_scan: bool,
    relation_writer: Any = write_global_relation_recall_state,
    delta_writer: Any = write_private_relation_delta_preflight,
    admission_builder: Any = build_global_relation_scan_admission,
) -> dict[str, Any]:
    primary_state = load_primary_evidence_state()
    generator_state = load_problem_generator_state()
    relation_state = load_global_relation_recall_state()
    freshness = relation_recall_freshness(generator_state, relation_state)
    delta_private = delta_writer(storage=storage)
    delta = public_relation_delta_preflight_summary(delta_private)
    admission = admission_builder(primary_state=primary_state,generator_state=generator_state,relation_state=relation_state,delta_state=delta_private)
    if not allow_model_scan:
        return {
            "schema_version": "1.0",
            "status": "DEFERRED_RELATION_MODEL_SCAN",
            "freshness": freshness,
            "delta_preflight": delta,
            "manual_scan_admission": admission,
            "model_calls_authorized": False,
            "scientific_authority": False,
        }
    if mode != "manual":
        raise RuntimeError("global relation model scan is manual-only")
    if (admission.get("summary") or {}).get("manual_scan_eligible") is not True:
        raise RuntimeError("global relation manual-scan admission blocked: "+",".join(str(x) for x in admission.get("failed_checks") or []))
    result=dict(relation_writer(storage=storage,explicit_manual_scan_intent=True))
    result["delta_preflight"]=delta
    result["manual_scan_admission"]=admission
    return result


def _run_shadow_search_admission_control() -> dict[str, Any]:
    """Evaluate next shadow-run admission and emit a zero-provider cross-host handoff contract."""
    state = build_shadow_search_admission()
    public = public_shadow_search_admission_summary(state)
    ready = public.get("status") == "READY_FOR_SHADOW_QUALIFICATION" and (public.get("summary") or {}).get("qualification_allowed") is True
    handoff = {
        "required": bool(ready),
        "role": "canonical-private-pool-shadow-qualifier" if ready else "none",
        "launcher_entrypoint": "research_pipeline.problem_search_shadow_launcher" if ready else "",
        "provider_calls_authorized": False,
        "automatic_remote_execution_authorized": False,
        "scientific_authority": False,
    }
    public["handoff"] = handoff
    public.setdefault("summary", {}).update({
        "handoff_required": handoff["required"],
        "handoff_role": handoff["role"],
        "handoff_launcher_entrypoint": handoff["launcher_entrypoint"],
        "handoff_provider_calls_authorized": 0,
        "handoff_automatic_remote_execution_authorized": False,
    })
    public["model_calls_authorized"] = False
    public["qualification_created"] = False
    public["scientific_authority"] = False
    return public


def _run_shadow_continuation_frontier_control(storage: StorageSettings) -> dict[str, Any]:
    """Project the current shadow continuation frontier without creating or executing work."""
    admission = public_shadow_search_admission_summary(build_shadow_search_admission())
    support_watch = public_support_release_watch_summary(load_private_support_release_watch(storage=storage))
    asset_queue = public_support_asset_recheck_summary(load_private_support_asset_recheck_queue(storage=storage))
    support_handoff = public_support_asset_recheck_handoff_summary(load_private_support_asset_recheck_handoff(storage=storage))
    frontier = build_shadow_continuation_frontier(
        admission=admission,
        support_watch=support_watch,
        asset_queue=asset_queue,
        support_handoff=support_handoff,
    )
    frontier.setdefault("summary", {}).update({
        "frontier_status": frontier.get("status", "HOLD_SHADOW_CONTINUATION_STATE_INCOMPLETE"),
        "next_control_action": frontier.get("next_control_action", "repair-shadow-continuation-state"),
    })
    frontier["scientific_authority"] = False
    return frontier


def _run_discovery_frontier_control(storage: StorageSettings) -> dict[str, Any]:
    """Project the final paper-first discovery frontier for the cycle report only."""
    primary = load_primary_evidence_state()
    generator = load_problem_generator_state()
    queue = load_problem_gate_queue_state()
    relation = load_global_relation_recall_state()
    freshness = relation_recall_freshness(generator, relation)
    delta_private = load_private_relation_delta_preflight(storage=storage)
    relation_admission = public_global_relation_scan_admission_summary(
        build_global_relation_scan_admission(
            primary_state=primary,
            generator_state=generator,
            relation_state=relation,
            delta_state=delta_private,
        )
    )
    shadow_admission = public_shadow_search_admission_summary(build_shadow_search_admission())
    object_candidate = public_scientific_object_candidate_evidence_summary(
        load_scientific_object_candidate_evidence_ledger(storage=storage)
    )
    support_watch = public_support_release_watch_summary(load_private_support_release_watch(storage=storage))
    asset_queue = public_support_asset_recheck_summary(load_private_support_asset_recheck_queue(storage=storage))
    frontier = build_paper_first_discovery_frontier(
        primary_state=primary,
        generator_state=generator,
        queue_state=queue,
        relation_freshness_state=freshness,
        relation_admission_state=relation_admission,
        shadow_admission_state=shadow_admission,
        object_candidate_state=object_candidate,
        support_release_watch_state=support_watch,
        support_asset_recheck_state=asset_queue,
    )
    frontier.setdefault("summary", {}).update({
        "frontier_status": frontier.get("status", "WAIT_EXTERNAL_EVIDENCE_TRIGGERS"),
        "frontier_blockers": list(frontier.get("blockers") or []),
        "trigger_names": [str(row.get("trigger") or "") for row in frontier.get("triggers") or []],
    })
    frontier["scientific_authority"] = False
    return frontier


def run_cycle(
    *,
    mode: str = "daily",
    sync_literature: bool = False,
    web_review_limit: int = 0,
    ai_consultation_limit: int = 1,
    ai_consultations: bool = True,
    global_relation_model_scan: bool = False,
    publish: bool = False,
) -> dict[str, Any]:
    if global_relation_model_scan and mode != "manual":
        raise ValueError("global_relation_model_scan is allowed only in manual mode")
    storage = StorageSettings.from_env()
    storage.ensure()
    run_dir = storage.run_dir / "automation"
    run_dir.mkdir(parents=True, exist_ok=True)
    lock = storage.lock_dir / ".research-automation-cycle.lock"
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "started_at": _now(),
        "mode": mode,
        "sync_literature": sync_literature,
        "web_review_limit": web_review_limit,
        "ai_consultation_limit": ai_consultation_limit,
        "ai_consultations": ai_consultations,
        "global_relation_model_scan": bool(global_relation_model_scan),
        "publish": publish,
        "steps": [],
        "status": "running",
    }
    with cycle_lock(lock):
        if sync_literature:
            report["steps"].append(_step("literature-sync", _sync_literature))
        if mode in {"weekly", "manual"}:
            # Preserve already-passed Problem-Gate candidates before the volatile discovery queue can refresh.
            # Canonical live discovery remains the four-lane atomic transaction; the ten-primitive Search Portfolio is shadow-only.
            # Global Relation Recall supplements cross-tranche live-lane pair recall without gaining canonical Problem-Gate authority.
            report["steps"].append(_step("paper-design-backlog-pre-discovery", write_paper_design_backlog))
            report["steps"].append(_step("paper-first-fresh-saturation", write_fresh_saturation_state))
            report["steps"].append(_step("paper-first-discovery-transaction", write_problem_discovery_transaction))
            report["steps"].append(_step("paper-first-shadow-search-admission", _run_shadow_search_admission_control))
            # Shadow scientific-object recall is strictly downstream of the live atomic transaction.
            # It only runs when live source coverage is fully closed and cannot mutate canonical Primary/Generator/Queue.
            report["steps"].append(_step("paper-first-scientific-object-shadow-maintenance", run_shadow_scientific_object_maintenance))
            report["steps"].append(_step("paper-first-support-release-watch", lambda: run_support_release_watch(storage=storage)))
            report["steps"].append(_step("paper-first-support-asset-recheck-queue", lambda: write_private_support_asset_recheck_queue(storage=storage)))
            report["steps"].append(_step("paper-first-support-asset-recheck-handoff", lambda: write_private_support_asset_recheck_handoff(storage=storage)))
            report["steps"].append(_step("paper-first-shadow-continuation-frontier", lambda: _run_shadow_continuation_frontier_control(storage)))
            report["steps"].append(_step("paper-first-relation-cache-backfill", backfill_relation_cache))
            report["steps"].append(_step("paper-first-global-relation-recall", lambda: _run_global_relation_control(storage=storage,mode=mode,allow_model_scan=global_relation_model_scan)))
            report["steps"].append(_step("paper-first-discovery-frontier", lambda: _run_discovery_frontier_control(storage)))
            report["steps"].append(_step("iclr-bank", write_iclr_idea_bank))
            report["steps"].append(_step("machine-school-inspired-bank", write_machine_school_bank))
            report["steps"].append(_step("archival-solution-first-idea-discovery-v3", write_idea_discovery_v3))
            report["steps"].append(_step("archival-reviewer-repaired-idea-discovery-v31", write_idea_discovery_v31))
            report["steps"].append(_step("archival-expanded-idea-discovery-v5", write_idea_discovery_v5))
            report["steps"].append(_step("archival-reviewer-targeted-idea-discovery-v51", write_idea_discovery_v51))
            report["steps"].append(_step("archival-second-order-idea-discovery-v52", write_idea_discovery_v52))
            report["steps"].append(_step("archival-final-boundary-idea-discovery-v53", write_idea_discovery_v53))
            report["steps"].append(_step("archival-discussion-ready-portfolio", write_discussion_portfolio))
            report["steps"].append(_step("historical-paper-first-idea-incubation", write_paper_first_idea_incubation))
            report["steps"].append(_step("archival-constrained-combination-idea-discovery-v4", write_idea_discovery_v4))
            report["steps"].append(_step("iclr-audit", write_iclr_audit))
            report["steps"].append(_step("cvpr-followup-bank", write_cvpr_idea_bank))
            report["steps"].append(_step("published-visual-audit", write_published_audit))
        report["steps"].append(_step("emerging-niche-policy", write_emerging_niche_policy))
        if mode not in {"weekly", "manual"}:
            report["steps"].append(_step("paper-first-fresh-saturation", write_fresh_saturation_state))
            # Daily maintenance may refill verified public primary abstracts, but it never runs Global Relation Recall.
            report["steps"].append(_step("paper-first-relation-cache-maintenance", lambda: backfill_relation_cache(max_primary_per_run=16,max_fulltext_per_run=0)))
            # Queue provenance is transaction-bound to Primary -> Generator -> Queue.
            # A daily cycle does not run Primary/Generator, so it preserves the versioned queue snapshot.
        report["steps"].append(_step("paper-design-backlog", write_paper_design_backlog))
        report["steps"].append(_step("human-terminal-idea-state", write_human_terminal_state))
        report["steps"].append(_step("paper-first-p0-f0-state", write_paper_first_p0_f0_state))
        report["steps"].append(_step("p0-realizability-suite", write_p0_realizability_suite))
        report["steps"].append(_step("p0-revived-batch-f0", write_revived_batch_f0))
        report["steps"].append(_step("p0-b10-cpu", write_b10_cpu_p0))
        report["steps"].append(_step("p0-a12-soft-audit-f0", lambda: _preserve_on_missing_historical_source(write_a12_soft_audit_f0)))
        report["steps"].append(_step("p0-a3-substrate-stop", lambda: _preserve_on_missing_historical_source(write_a3_substrate_stop)))
        report["steps"].append(_step("p0-a4-composition-cpu", write_a4_cpu_p0))
        report["steps"].append(_step("p0-a5-history-cpu", write_a5_cpu_p0))
        report["steps"].append(_step("p0-a6-cpu", write_a6_cpu_p0))
        report["steps"].append(_step("p0-a7-counterfactual-cpu", write_a7_cpu_p0))
        report["steps"].append(_step("p0-b2-support-stop", write_b2_support_stop))
        report["steps"].append(_step("p0-b3-interference-cpu", write_b3_cpu_screen))
        report["steps"].append(_step("p0-b3-fresh-support-stop", lambda: _preserve_on_missing_historical_source(write_b3_fresh_support_stop)))
        report["steps"].append(_step("p0-b3-real-state", write_b3_real_state))
        report["steps"].append(_step("p0-b5-applicability-cpu", write_b5_cpu_p0))
        report["steps"].append(_step("p0-b6-memory-utility-cpu", write_b6_cpu_p0))
        report["steps"].append(_step("p0-c2-evaluator-cpu", write_c2_cpu_p0))
        report["steps"].append(_step("p0-d1-minimal-curriculum-cpu", write_d1_cpu_p0))
        report["steps"].append(_step("p0-e1-edit-table-stop", write_e1_table_stop))
        report["steps"].append(_step("p0-e2-workflow-cpu", write_e2_cpu_p0))
        report["steps"].append(_step("p0-e3-real-api", write_e3_real_api_p0))
        report["steps"].append(_step("p0-e3-stateful", write_e3_stateful_p0))
        report["steps"].append(_step("p0-e4-permission", write_e4_permission_p0))
        report["steps"].append(_step("p0-offline-qualification", write_p0_offline_qualification_state))
        report["steps"].append(_step("p0-admission-state", write_p0_admission_state))
        report["steps"].append(_step("research-system-pre-ai", write_research_system_state))
        report["steps"].append(_step(
            "ai-consultation-automation",
            lambda: run_ai_consultation_automation(
                storage,
                execute=ai_consultations,
                max_cases=max(0, ai_consultation_limit),
            ),
        ))
        report["steps"].append(_step("research-system-state", write_research_system_state))
        if web_review_limit > 0:
            if mode in {"weekly", "manual"}:
                report["steps"].append(_advisory_step("external-research-system-learning-review", lambda: _run_external_system_learning_review(storage)))
            report["steps"].append(_advisory_step("project-web-gpt-repair-review", lambda: _run_web_reviews(web_review_limit, storage)))
        hard_failures = [step for step in report["steps"] if step["status"] == "fail"]
        advisory_warnings = [step for step in report["steps"] if step["status"] == "warning"]
        report["status"] = "degraded" if hard_failures else ("pass_with_warnings" if advisory_warnings else "pass")
    report["completed_at"] = _now()
    stamp = report["completed_at"].replace(":", "-")
    report_path = run_dir / f"cycle-{stamp}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest = run_dir / "latest.json"
    latest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if publish:
        # Rebuild once so the public state can include the latest cycle report, then publish
        # only if normalized content has changed.
        write_emerging_niche_policy()
        write_human_terminal_state()
        write_p0_realizability_suite()
        write_revived_batch_f0()
        write_b10_cpu_p0()
        _preserve_on_missing_historical_source(write_a12_soft_audit_f0)
        _preserve_on_missing_historical_source(write_a3_substrate_stop)
        write_a4_cpu_p0()
        write_a5_cpu_p0()
        write_a6_cpu_p0()
        write_a7_cpu_p0()
        write_b2_support_stop()
        write_b3_cpu_screen()
        _preserve_on_missing_historical_source(write_b3_fresh_support_stop)
        write_b3_real_state()
        write_b5_cpu_p0()
        write_b6_cpu_p0()
        write_c2_cpu_p0()
        write_d1_cpu_p0()
        write_e1_table_stop()
        write_e2_cpu_p0()
        write_e3_real_api_p0()
        write_e3_stateful_p0()
        write_e4_permission_p0()
        write_p0_offline_qualification_state()
        write_p0_admission_state()
        write_research_system_state()
        publication_started = time.time()
        try:
            publication_result = publish_generated_state(mode=mode)
            publication_status = "pass" if publication_result.get("status") in PUBLICATION_OK_STATES else "fail"
            publication = {
                "name": "publish-generated-state",
                "status": publication_status,
                "duration_seconds": round(time.time() - publication_started, 3),
                "summary": publication_result,
            }
        except Exception as error:
            publication = {
                "name": "publish-generated-state",
                "status": "fail",
                "duration_seconds": round(time.time() - publication_started, 3),
                "error": f"{type(error).__name__}: {error}",
            }
        report["steps"].append(publication)
        if publication["status"] != "pass":
            report["status"] = "degraded"
        report["completed_at"] = _now()
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        latest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def _preserve_on_missing_historical_source(function: Any) -> Any:
    """Keep the last frozen scientific artifact when a compute host lacks its source run tree."""
    try:
        return function()
    except FileNotFoundError as error:
        return {"status":"preserved-missing-historical-source","missing_source":str(error)}


def _step(name: str, function: Any) -> dict[str, Any]:
    started = time.time()
    try:
        result = function()
        return {
            "name": name,
            "status": "pass",
            "duration_seconds": round(time.time() - started, 3),
            "summary": _safe_summary(result),
        }
    except Exception as error:  # keep the cycle alive and preserve prior valid artifacts
        return {
            "name": name,
            "status": "fail",
            "duration_seconds": round(time.time() - started, 3),
            "error": f"{type(error).__name__}: {error}",
        }


def _advisory_step(name: str, function: Any) -> dict[str, Any]:
    """Record optional external consultations truthfully without blocking core publication."""
    started = time.time()
    try:
        result = function()
        ok = not isinstance(result, dict) or result.get("ok") is not False
        return {
            "name": name,
            "status": "pass" if ok else "warning",
            "advisory": True,
            "duration_seconds": round(time.time() - started, 3),
            "summary": _safe_summary(result),
        }
    except Exception as error:
        return {
            "name": name,
            "status": "warning",
            "advisory": True,
            "duration_seconds": round(time.time() - started, 3),
            "error": f"{type(error).__name__}: {error}",
        }


def _safe_summary(result: Any) -> Any:
    if not isinstance(result, dict):
        return str(result)[:500]
    for key in ("summary", "statistics", "health"):
        if key in result:
            return result[key]
    return {key: result[key] for key in list(result)[:8]}


def _sync_literature() -> dict[str, Any]:
    s2 = SemanticScholarSettings.from_env(required=False)
    if not s2.api_key:
        return {
            "status":"SKIPPED_PROVIDER_UNCONFIGURED",
            "provider":"semantic-scholar",
            "configured":False,
            "fallback":"paper-first-primary-evidence will use low-rate arXiv primary discovery",
            "scientific_authority":False,
        }
    old_retries = os.environ.get("S2_MAX_RETRIES")
    old_timeout = os.environ.get("S2_TIMEOUT_SECONDS")
    os.environ["S2_MAX_RETRIES"] = os.getenv("AUTOMATION_S2_MAX_RETRIES", "2")
    os.environ["S2_TIMEOUT_SECONDS"] = os.getenv("AUTOMATION_S2_TIMEOUT_SECONDS", "20")
    try:
        return sync_semantic_scholar(
            total_limit=int(os.getenv("AUTOMATION_S2_LIMIT", "300")),
            per_query_limit=int(os.getenv("AUTOMATION_S2_PER_QUERY", "10")),
            citation_seed_count=int(os.getenv("AUTOMATION_S2_CITATION_SEEDS", "8")),
            citation_limit=int(os.getenv("AUTOMATION_S2_CITATION_LIMIT", "6")),
            citation_depth=1,
            force_refresh=False,
        )
    finally:
        if old_retries is None:
            os.environ.pop("S2_MAX_RETRIES", None)
        else:
            os.environ["S2_MAX_RETRIES"] = old_retries
        if old_timeout is None:
            os.environ.pop("S2_TIMEOUT_SECONDS", None)
        else:
            os.environ["S2_TIMEOUT_SECONDS"] = old_timeout


def _run_external_system_learning_review(storage: StorageSettings) -> dict[str, Any]:
    output_dir = storage.run_dir / "reviews" / "research-system-learning"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "latest.md"
    prompt = (
        "Run a bounded weekly delta scan, not an exhaustive survey. Search official project pages, primary papers, and author repositories for at most FOUR materially new or updated autonomous scientific-research systems. "
        "Prefer developments from the last 90 days and omit systems with no meaningful control-plane change. Extract at most ONE workflow/control mechanism per system and reject superficial agent-role renamings. "
        "Compare each surviving mechanism against our current stack: Principle Certificate, Protocol Validity, P0 Economy, eight-gate compiler, Scientific Meta-Trace, Failure Asset Library, information-gain scheduler, AI consultation, research-system replay, and single-writer scientific authority. "
        "For each survivor return: primary/official source, mechanism, failure mode solved, local collision, adopt/merge/watch verdict, cheapest local replay or falsifier, and safety/authority implications. "
        "Do not recommend automatic code adoption without a local gap test. Keep the whole answer under 900 words. If nothing materially new survives, return a concise zero-update result."
    )
    review_timeout = max(120, int(os.getenv("AUTOMATION_SYSTEM_LEARNING_TIMEOUT", "300")))
    command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "project_web_gpt.py"),
        "--json", "--timeout", str(review_timeout),
        "--slug", "external-research-system-learning",
        "--output", str(output),
        prompt,
    ]
    completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=review_timeout + 60, check=False)
    exists = output.exists()
    return {
        "ok": completed.returncode == 0 and exists,
        "returncode": completed.returncode,
        "output": str(output),
        "exists": exists,
        "stderr": completed.stderr[-1000:],
    }


def _run_web_reviews(limit: int, storage: StorageSettings) -> dict[str, Any]:
    state_path = PROJECT_ROOT / "generated" / "research-system-state.json"
    if not state_path.exists():
        raise RuntimeError("research system state must be generated before web review")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    queue = (state.get("repair_queue") or {}).get("queue") or []
    idea_path = PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json"
    ideas_payload = json.loads(idea_path.read_text(encoding="utf-8"))
    ideas = {str(item["id"]): item for item in list(ideas_payload.get("passed_ideas") or []) + list(ideas_payload.get("blocked_ideas") or [])}
    output_dir = storage.run_dir / "reviews" / "automatic-repairs"
    output_dir.mkdir(parents=True, exist_ok=True)
    completed: list[dict[str, Any]] = []
    from .review_repair import build_web_review_prompt
    for item in queue[:limit]:
        idea = ideas.get(str(item["idea_id"]))
        if not idea:
            continue
        output = output_dir / f"{item['idea_id']}.md"
        command = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "project_web_gpt.py"),
            "--json", "--timeout", os.getenv("AUTOMATION_WEB_GPT_TIMEOUT", "240"),
            "--slug", f"auto-repair-{item['idea_id'][:35]}",
            "--output", str(output),
            build_web_review_prompt(item, idea),
        ]
        completed_process = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=300, check=False)
        completed.append({
            "idea_id": item["idea_id"],
            "returncode": completed_process.returncode,
            "output": str(output),
            "exists": output.exists(),
            "stderr": completed_process.stderr[-1000:],
        })
    ok = all(row.get("returncode") == 0 and row.get("exists") is True for row in completed)
    return {"ok": ok, "requested": limit, "completed": completed}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fail-safe continuous research cycle.")
    parser.add_argument("--mode", choices=("daily", "weekly", "manual"), default="manual")
    parser.add_argument("--sync-literature", action="store_true")
    parser.add_argument("--web-review-limit", type=int, default=0)
    parser.add_argument("--ai-consultation-limit", type=int, default=1, help="Maximum new AI-clinic cases executed per cycle.")
    parser.add_argument("--no-ai-consultations", action="store_true", help="Keep AI-clinic trigger/hash sync active but skip external reviewer calls for this cycle.")
    parser.add_argument("--global-relation-model-scan", action="store_true", help="Manual mode only: explicitly authorize the zero-authority relation/lane/reduction model scan. Weekly cycles defer it by default.")
    parser.add_argument("--publish", action="store_true", help="Publish substantive generated-artifact changes to origin/main.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_cycle(
        mode=args.mode,
        sync_literature=args.sync_literature,
        web_review_limit=max(args.web_review_limit, 0),
        ai_consultation_limit=max(args.ai_consultation_limit, 0),
        ai_consultations=not args.no_ai_consultations,
        global_relation_model_scan=args.global_relation_model_scan,
        publish=args.publish,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in {"pass", "pass_with_warnings"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
