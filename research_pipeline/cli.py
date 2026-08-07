from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import SemanticScholarSettings, StorageSettings
from .advisor_selection import build_advisor_selection, write_advisor_selection
from .cvpr_idea_factory import DEFAULT_JS as DEFAULT_CVPR_JS
from .cvpr_idea_factory import DEFAULT_JSON as DEFAULT_CVPR_JSON
from .cvpr_idea_factory import build_cvpr_idea_bank, validate_bank, write_cvpr_idea_bank
from .discussion_portfolio import build_discussion_portfolio, write_discussion_portfolio
from .iclr_idea_factory import DEFAULT_JS as DEFAULT_ICLR_JS
from .iclr_idea_factory import DEFAULT_JSON as DEFAULT_ICLR_JSON
from .iclr_idea_factory import build_iclr_idea_bank, validate_bank as validate_iclr_bank, write_iclr_idea_bank
from .idea_discovery_v3 import DEFAULT_JS as DEFAULT_DISCOVERY_V3_JS
from .idea_discovery_v3 import DEFAULT_JSON as DEFAULT_DISCOVERY_V3_JSON
from .idea_discovery_v3 import build_idea_discovery_v3, validate as validate_discovery_v3, write_idea_discovery_v3
from .idea_discovery_v31 import DEFAULT_JS as DEFAULT_DISCOVERY_V31_JS
from .idea_discovery_v31 import DEFAULT_JSON as DEFAULT_DISCOVERY_V31_JSON
from .idea_discovery_v31 import build_idea_discovery_v31, validate as validate_discovery_v31, write_idea_discovery_v31
from .idea_discovery_v5 import DEFAULT_JS as DEFAULT_DISCOVERY_V5_JS, DEFAULT_JSON as DEFAULT_DISCOVERY_V5_JSON, build_idea_discovery_v5, validate as validate_discovery_v5, write_idea_discovery_v5
from .idea_discovery_v51 import build_idea_discovery_v51, write_idea_discovery_v51
from .idea_discovery_v52 import build_idea_discovery_v52, write_idea_discovery_v52
from .idea_discovery_v53 import build_idea_discovery_v53, write_idea_discovery_v53
from .idea_discovery_v4 import DEFAULT_JS as DEFAULT_DISCOVERY_V4_JS
from .idea_discovery_v4 import DEFAULT_JSON as DEFAULT_DISCOVERY_V4_JSON
from .idea_discovery_v4 import build_idea_discovery_v4, validate as validate_discovery_v4, write_idea_discovery_v4
from .iclr_experiment_audit import DEFAULT_JS as DEFAULT_ICLR_AUDIT_JS
from .iclr_experiment_audit import DEFAULT_JSON as DEFAULT_ICLR_AUDIT_JSON
from .iclr_experiment_audit import build_payload as build_iclr_audit
from .iclr_experiment_audit import validate as validate_iclr_audit
from .iclr_experiment_audit import write_audit as write_iclr_audit
from .published_experiment_audit import DEFAULT_JS as DEFAULT_AUDIT_JS
from .published_experiment_audit import DEFAULT_JSON as DEFAULT_AUDIT_JSON
from .published_experiment_audit import build_payload as build_published_audit
from .published_experiment_audit import validate as validate_published_audit
from .published_experiment_audit import write_audit
from .machine_school_idea_factory import DEFAULT_JS as DEFAULT_MACHINE_SCHOOL_JS
from .machine_school_idea_factory import DEFAULT_JSON as DEFAULT_MACHINE_SCHOOL_JSON
from .machine_school_idea_factory import build_machine_school_bank, validate_bank as validate_machine_school_bank, write_machine_school_bank
from .live_pipeline import (
    DEFAULT_CORPUS_JSON,
    DEFAULT_SITE_JS,
    load_live_corpus,
    sync_semantic_scholar,
)
from .pipeline import ROOT, build_snapshot, write_snapshot
from .query_planner import DEFAULT_SCOPE_PATH
from .research_system import DEFAULT_JS as DEFAULT_SYSTEM_JS
from .research_system import DEFAULT_JSON as DEFAULT_SYSTEM_JSON
from .research_system import build_research_system_state, validate_state, write_research_system_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the evidence-gated paper-idea decision snapshot.")
    parser.add_argument("--json", type=Path, default=ROOT / "generated" / "idea-pipeline.json")
    parser.add_argument("--js", type=Path, default=ROOT / "generated" / "idea-pipeline-snapshot.js")
    parser.add_argument("--check", action="store_true", help="Validate the snapshot without writing idea files.")

    storage = parser.add_argument_group("Research storage")
    storage.add_argument("--storage-status", action="store_true", help="Show code/data paths and disk capacity without exposing secrets.")
    storage.add_argument("--init-storage", action="store_true", help="Create the configured corpus, dataset, paper, index, run, cache, lock, and site-artifact directories.")

    system = parser.add_argument_group("Continuous research system")
    system.add_argument("--build-research-system", action="store_true", help="Build evidence graph, collision analysis, lineage, pilot registry, and repair queue.")
    system.add_argument("--research-system-status", action="store_true", help="Show safe automation-component and health summaries.")
    system.add_argument("--research-system-json", type=Path, default=DEFAULT_SYSTEM_JSON)
    system.add_argument("--research-system-js", type=Path, default=DEFAULT_SYSTEM_JS)

    iclr = parser.add_argument_group("ICLR-first low-resource idea bank")
    iclr.add_argument("--build-iclr-bank", action="store_true", help="Validate and export the ICLR-first self-evolution idea bank.")
    iclr.add_argument("--iclr-status", action="store_true", help="Show ICLR candidate counts, review gates, and top priorities.")
    iclr.add_argument("--iclr-json", type=Path, default=DEFAULT_ICLR_JSON)
    iclr.add_argument("--iclr-js", type=Path, default=DEFAULT_ICLR_JS)
    iclr.add_argument("--build-iclr-audit", action="store_true", help="Export the ICLR experiment-substrate audit.")
    iclr.add_argument("--iclr-audit-status", action="store_true", help="Show validation status for the ICLR experiment audit.")
    iclr.add_argument("--iclr-audit-json", type=Path, default=DEFAULT_ICLR_AUDIT_JSON)
    iclr.add_argument("--iclr-audit-js", type=Path, default=DEFAULT_ICLR_AUDIT_JS)

    inspired = parser.add_argument_group("Internet-inspired self-evolution idea bank")
    inspired.add_argument("--build-machine-school-bank", action="store_true", help="Validate and export the machine-school-inspired candidate bank.")
    inspired.add_argument("--machine-school-status", action="store_true", help="Show internal and external screening counts for the inspired bank.")
    inspired.add_argument("--machine-school-json", type=Path, default=DEFAULT_MACHINE_SCHOOL_JSON)
    inspired.add_argument("--machine-school-js", type=Path, default=DEFAULT_MACHINE_SCHOOL_JS)

    discovery = parser.add_argument_group("Solution-first Idea Discovery v3")
    discovery.add_argument("--build-idea-discovery-v3", action="store_true", help="Build the solution-first method-child bank.")
    discovery.add_argument("--idea-discovery-v3-status", action="store_true", help="Show solution-child, Pareto-front, and external-review counts.")
    discovery.add_argument("--idea-discovery-v3-json", type=Path, default=DEFAULT_DISCOVERY_V3_JSON)
    discovery.add_argument("--idea-discovery-v3-js", type=Path, default=DEFAULT_DISCOVERY_V3_JS)
    discovery.add_argument("--build-idea-discovery-v31", action="store_true", help="Build the Reviewer-vector repair round.")
    discovery.add_argument("--idea-discovery-v31-status", action="store_true", help="Show v3.1 repair and external-review counts.")
    discovery.add_argument("--idea-discovery-v31-json", type=Path, default=DEFAULT_DISCOVERY_V31_JSON)
    discovery.add_argument("--idea-discovery-v31-js", type=Path, default=DEFAULT_DISCOVERY_V31_JS)
    discovery.add_argument("--build-idea-discovery-v5", action="store_true", help="Build the wide-search v5 idea bank.")
    discovery.add_argument("--idea-discovery-v5-status", action="store_true", help="Show v5 candidate and R2 counts.")
    discovery.add_argument("--idea-discovery-v5-json", type=Path, default=DEFAULT_DISCOVERY_V5_JSON)
    discovery.add_argument("--idea-discovery-v5-js", type=Path, default=DEFAULT_DISCOVERY_V5_JS)
    discovery.add_argument("--discussion-ready-status", action="store_true", help="Show strict R2-PASS progress toward the 20-idea discussion target.")
    discovery.add_argument("--build-discussion-ready", action="store_true", help="Rebuild the strict discussion-ready portfolio.")
    discovery.add_argument("--idea-discovery-v51-status", action="store_true", help="Show targeted v5.1 reviewer-vector repair children.")
    discovery.add_argument("--advisor-priority-status", action="store_true", help="Show the comparative 22-to-8 advisor shortlist.")
    discovery.add_argument("--build-advisor-priority", action="store_true", help="Rebuild the comparative advisor shortlist and meta-review view.")
    discovery.add_argument("--idea-discovery-v52-status", action="store_true", help="Show second-order v5.2 repair children.")
    discovery.add_argument("--idea-discovery-v53-status", action="store_true", help="Show final-boundary v5.3 repair children.")
    discovery.add_argument("--build-idea-discovery-v4", action="store_true", help="Build constrained-combination and conditional-revival candidates.")
    discovery.add_argument("--idea-discovery-v4-status", action="store_true", help="Show v4 candidate groups, finalists, and external-review counts.")
    discovery.add_argument("--idea-discovery-v4-json", type=Path, default=DEFAULT_DISCOVERY_V4_JSON)
    discovery.add_argument("--idea-discovery-v4-js", type=Path, default=DEFAULT_DISCOVERY_V4_JS)

    cvpr = parser.add_argument_group("Secondary CVPR visual-specialization bank")
    cvpr.add_argument("--build-cvpr-bank", action="store_true", help="Validate and export the self-reviewed low-resource CVPR idea bank.")
    cvpr.add_argument("--cvpr-status", action="store_true", help="Show safe counts and budget limits for the CVPR idea bank.")
    cvpr.add_argument("--cvpr-json", type=Path, default=DEFAULT_CVPR_JSON)
    cvpr.add_argument("--cvpr-js", type=Path, default=DEFAULT_CVPR_JS)

    audit = parser.add_argument_group("Published experiment substrate audit")
    audit.add_argument("--build-published-audit", action="store_true", help="Export the verified API/open-weight/training audit for published visual-agent papers.")
    audit.add_argument("--published-audit-status", action="store_true", help="Show safe counts and validation status for the published-paper experiment audit.")
    audit.add_argument("--published-audit-json", type=Path, default=DEFAULT_AUDIT_JSON)
    audit.add_argument("--published-audit-js", type=Path, default=DEFAULT_AUDIT_JS)

    semantic = parser.add_argument_group("Semantic Scholar live literature")
    semantic.add_argument("--sync-s2", action="store_true", help="Run the five-route Semantic Scholar retrieval and citation expansion.")
    semantic.add_argument("--s2-status", action="store_true", help="Show safe provider configuration and local corpus status without exposing the key.")
    semantic.add_argument("--s2-scope", type=Path, default=DEFAULT_SCOPE_PATH)
    semantic.add_argument("--s2-json", type=Path, default=DEFAULT_CORPUS_JSON)
    semantic.add_argument("--s2-js", type=Path, default=DEFAULT_SITE_JS)
    semantic.add_argument("--s2-limit", type=int, default=120, help="Maximum direct-search papers retained after deduplication.")
    semantic.add_argument("--s2-per-query", type=int, default=8, help="Minimum results requested for each planned query.")
    semantic.add_argument("--s2-citation-seeds", type=int, default=4, help="Number of resolved seed papers expanded through the citation graph.")
    semantic.add_argument("--s2-citation-limit", type=int, default=6, help="Citations and references retained per expanded seed.")
    semantic.add_argument("--s2-depth", type=int, default=1, help="Citation graph expansion depth; use 0 to disable expansion.")
    semantic.add_argument("--s2-force-refresh", action="store_true", help="Ignore response cache and make fresh API requests.")
    return parser.parse_args()


def _print_storage_status() -> None:
    settings = StorageSettings.from_env()
    print(json.dumps(settings.safe_summary(), ensure_ascii=False, indent=2))


def _print_research_system_status() -> None:
    state = build_research_system_state()
    print(json.dumps({
        "summary": state["summary"],
        "health": state["health"],
        "components": state["components"],
        "validation_errors": validate_state(state),
    }, ensure_ascii=False, indent=2))


def _print_iclr_status() -> None:
    payload = build_iclr_idea_bank()
    print(json.dumps({
        "summary": payload["summary"],
        "policy": payload["policy"],
        "validation_errors": validate_iclr_bank(payload),
        "top_candidates": [
            {"rank": idea["rank"], "title": idea["title"], "track": idea["track"], "gpu_hours": idea["budget"]["gpu_hours"], "priority": idea["priority"]}
            for idea in payload["passed_ideas"][:10]
        ],
    }, ensure_ascii=False, indent=2))


def _print_machine_school_status() -> None:
    payload = build_machine_school_bank()
    print(json.dumps({
        "summary": payload["summary"],
        "validation_errors": validate_machine_school_bank(payload),
        "teacher_shortlist": [
            {
                "rank": idea.get("external_rank"),
                "title": idea["title"],
                "external_verdict": idea.get("external_verdict"),
                "final_status": idea.get("final_status"),
                "gpu_hours": idea["budget"]["gpu_hours"],
            }
            for idea in payload["teacher_shortlist"]
        ],
    }, ensure_ascii=False, indent=2))


def _print_idea_discovery_v3_status() -> None:
    payload = build_idea_discovery_v3()
    print(json.dumps({
        "summary": payload["summary"],
        "policy": payload["policy"],
        "validation_errors": validate_discovery_v3(payload),
        "pareto_front_ids": payload["pareto_front_ids"],
        "shortlist": [
            {"rank": idea["internal_rank"], "title": idea["title"], "parent_id": idea["parent_id"], "external_verdict": idea.get("external_verdict"), "mean_score": idea["mean_score"]}
            for idea in payload["shortlist"]
        ],
    }, ensure_ascii=False, indent=2))


def _print_idea_discovery_v31_status() -> None:
    payload = build_idea_discovery_v31()
    print(json.dumps({
        "summary": payload["summary"],
        "policy": payload["policy"],
        "validation_errors": validate_discovery_v31(payload),
        "children": [
            {
                "rank": idea["internal_rank"],
                "title": idea["title"],
                "parent_id": idea["parent_id"],
                "external_verdict": idea.get("external_verdict"),
                "mean_score": idea["mean_score"],
            }
            for idea in payload["children"]
        ],
    }, ensure_ascii=False, indent=2))


def _print_idea_discovery_v4_status() -> None:
    payload = build_idea_discovery_v4()
    print(json.dumps({
        "summary": payload["summary"],
        "policy": payload["policy"],
        "validation_errors": validate_discovery_v4(payload),
        "pareto_front_ids": payload["pareto_front_ids"],
        "tournament_finalists": [
            {
                "rank": idea["internal_rank"],
                "title": idea["title"],
                "lineage_type": idea["lineage_type"],
                "internal_status": idea["internal_status"],
                "external_verdict": idea.get("external_verdict"),
                "mean_score": idea["mean_score"],
            }
            for idea in payload["tournament_finalists"]
        ],
    }, ensure_ascii=False, indent=2))


def _print_idea_discovery_v5_status() -> None:
    payload = build_idea_discovery_v5()
    print(json.dumps({"summary": payload["summary"], "validation_errors": validate_discovery_v5(payload), "discussion_ready": [{"rank":x.get("external_rank"),"title":x["title"],"verdict":x.get("external_verdict")} for x in payload.get("discussion_ready", [])]}, ensure_ascii=False, indent=2))


def _print_discussion_ready_status() -> None:
    payload = build_discussion_portfolio()
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _print_idea_discovery_v51_status() -> None:
    payload = build_idea_discovery_v51()
    print(json.dumps({"summary": payload["summary"], "children": [{"rank":x.get("rank"),"id":x.get("id"),"parent_id":x.get("parent_id"),"verdict":x.get("external_verdict")} for x in payload.get("children",[])]}, ensure_ascii=False, indent=2))


def _print_idea_discovery_v52_status() -> None:
    payload = build_idea_discovery_v52()
    print(json.dumps({"summary": payload["summary"], "children": [{"rank":x.get("rank"),"id":x.get("id"),"parent_id":x.get("parent_id"),"verdict":x.get("external_verdict")} for x in payload.get("children",[])]}, ensure_ascii=False, indent=2))


def _print_idea_discovery_v53_status() -> None:
    payload = build_idea_discovery_v53()
    print(json.dumps({"summary": payload["summary"], "children": [{"rank":x.get("rank"),"id":x.get("id"),"parent_id":x.get("parent_id"),"verdict":x.get("external_verdict")} for x in payload.get("children",[])]}, ensure_ascii=False, indent=2))


def _print_advisor_priority_status() -> None:
    payload = build_advisor_selection()
    print(json.dumps({"source_count":payload["source_count"],"shortlist":[{"rank":x["advisor_rank"],"id":x["id"],"title":x["title"],"tier":x["relative_tier"],"p0":x["first_pilot_priority"]} for x in payload["primary_shortlist"]]}, ensure_ascii=False, indent=2))


def _print_iclr_audit_status() -> None:
    payload = build_iclr_audit()
    print(json.dumps({
        "summary": payload["summary"],
        "validation_errors": validate_iclr_audit(payload),
        "papers": [{"id": paper["id"], "venue": paper["venue"], "substrate": paper["substrate"], "verification": paper["verification"]} for paper in payload["papers"]],
    }, ensure_ascii=False, indent=2))


def _print_cvpr_status() -> None:
    payload = build_cvpr_idea_bank()
    status = {
        "summary": payload["summary"],
        "policy": payload["policy"],
        "validation_errors": validate_bank(payload),
        "top_candidates": [
            {
                "rank": idea["rank"],
                "title": idea["title"],
                "track": idea["track"],
                "gpu_hours": idea["budget"]["gpu_hours"],
                "priority": idea["priority"],
            }
            for idea in payload["passed_ideas"][:10]
        ],
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))


def _print_published_audit_status() -> None:
    payload = build_published_audit()
    print(json.dumps({
        "summary": payload["summary"],
        "validation_errors": validate_published_audit(payload),
        "papers": [
            {"id": paper["id"], "venue": paper["venue"], "substrate": paper["substrate"], "verification": paper["verification"]}
            for paper in payload["papers"]
        ],
    }, ensure_ascii=False, indent=2))


def _print_s2_status() -> None:
    settings = SemanticScholarSettings.from_env(required=False)
    corpus = load_live_corpus()
    status = {
        "provider": settings.safe_summary(),
        "corpus": {
            "exists": corpus is not None,
            "retrieved_at": corpus.get("retrieved_at") if corpus else None,
            "paper_count": (corpus.get("statistics") or {}).get("paper_count") if corpus else 0,
            "query_count": (corpus.get("statistics") or {}).get("query_count") if corpus else 0,
        },
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    if args.init_storage:
        storage = StorageSettings.from_env()
        storage.ensure()
        print(f"Initialized research storage at {storage.data_root}")
    if args.storage_status:
        _print_storage_status()
    if args.research_system_status:
        _print_research_system_status()
    if args.build_research_system:
        state = write_research_system_state(args.research_system_json, args.research_system_js)
        print(
            "Research system complete: "
            f"{state['summary']['evidence_nodes']} evidence nodes, "
            f"{state['summary']['collision_flags']} collision flags, "
            f"{state['summary']['repair_queue']} queued repairs."
        )
        print(f"Wrote {args.research_system_json}")
        print(f"Wrote {args.research_system_js}")
    if args.iclr_status:
        _print_iclr_status()
    if args.build_iclr_bank:
        payload = write_iclr_idea_bank(args.iclr_json, args.iclr_js)
        print(f"ICLR idea bank complete: {payload['summary']['passed']} passed, {payload['summary']['blocked_after_structured_review']} structured blocked, {payload['summary']['early_rejected']} early rejected.")
        print(f"Wrote {args.iclr_json}")
        print(f"Wrote {args.iclr_js}")
    if args.machine_school_status:
        _print_machine_school_status()
    if args.build_machine_school_bank:
        payload = write_machine_school_bank(args.machine_school_json, args.machine_school_js)
        print(f"Inspired idea bank complete: {payload['summary']['internal_pass']} pass, {payload['summary']['internal_revise']} revise, {payload['summary']['internal_reject']} reject.")
        print(f"Wrote {args.machine_school_json}")
        print(f"Wrote {args.machine_school_js}")
    if args.idea_discovery_v3_status:
        _print_idea_discovery_v3_status()
    if args.build_idea_discovery_v3:
        payload = write_idea_discovery_v3(args.idea_discovery_v3_json, args.idea_discovery_v3_js)
        print(f"Idea Discovery v3 complete: {payload['summary']['raw_children']} children, {payload['summary']['internal_shortlist']} shortlisted, {payload['summary']['external_pass']} external PASS.")
        print(f"Wrote {args.idea_discovery_v3_json}")
        print(f"Wrote {args.idea_discovery_v3_js}")
    if args.idea_discovery_v31_status:
        _print_idea_discovery_v31_status()
    if args.build_idea_discovery_v31:
        payload = write_idea_discovery_v31(args.idea_discovery_v31_json, args.idea_discovery_v31_js)
        print(f"Idea Discovery v3.1 complete: {payload['summary']['children']} children, {payload['summary']['external_revise']} external REVISE, {payload['summary']['external_block']} external BLOCK.")
        print(f"Wrote {args.idea_discovery_v31_json}")
        print(f"Wrote {args.idea_discovery_v31_js}")
    if args.idea_discovery_v4_status:
        _print_idea_discovery_v4_status()
    if args.build_idea_discovery_v4:
        payload = write_idea_discovery_v4(args.idea_discovery_v4_json, args.idea_discovery_v4_js)
        print(f"Idea Discovery v4 complete: {payload['summary']['raw_candidates']} candidates, {payload['summary']['discussion']} discussion, {payload['summary']['revival']} revival, {payload['summary']['external_pass']} external PASS.")
        print(f"Wrote {args.idea_discovery_v4_json}")
        print(f"Wrote {args.idea_discovery_v4_js}")
    if args.idea_discovery_v5_status:
        _print_idea_discovery_v5_status()
    if args.build_idea_discovery_v5:
        payload = write_idea_discovery_v5(args.idea_discovery_v5_json, args.idea_discovery_v5_js)
        print(f"Idea Discovery v5 complete: {payload['summary']['raw_candidates']} candidates, {len(payload['finalists'])} finalists/revivals, {payload['summary']['external_pass']} external PASS.")
        print(f"Wrote {args.idea_discovery_v5_json}")
        print(f"Wrote {args.idea_discovery_v5_js}")
    if args.discussion_ready_status:
        _print_discussion_ready_status()
    if args.build_discussion_ready:
        payload = write_discussion_portfolio()
        print(f"Discussion-ready portfolio: {payload['count']}/{payload['target']} strict R2 PASS.")
    if args.idea_discovery_v51_status:
        _print_idea_discovery_v51_status()
    if args.advisor_priority_status:
        _print_advisor_priority_status()
    if args.build_advisor_priority:
        payload = write_advisor_selection()
        print(f"Advisor priority shortlist: {len(payload['primary_shortlist'])}/{payload['source_count']} strict PASS ideas.")
    if args.idea_discovery_v52_status:
        _print_idea_discovery_v52_status()
    if args.idea_discovery_v53_status:
        _print_idea_discovery_v53_status()
    if args.iclr_audit_status:
        _print_iclr_audit_status()
    if args.build_iclr_audit:
        payload = write_iclr_audit(args.iclr_audit_json, args.iclr_audit_js)
        print(f"ICLR experiment audit complete: {payload['summary']['papers']} papers.")
        print(f"Wrote {args.iclr_audit_json}")
        print(f"Wrote {args.iclr_audit_js}")
    if args.cvpr_status:
        _print_cvpr_status()
    if args.build_cvpr_bank:
        payload = write_cvpr_idea_bank(args.cvpr_json, args.cvpr_js)
        print(
            "CVPR idea bank complete: "
            f"{payload['summary']['passed']} passed, "
            f"{payload['summary']['early_rejected']} early rejected, "
            f"{payload['summary']['tracks']} tracks."
        )
        print(f"Wrote {args.cvpr_json}")
        print(f"Wrote {args.cvpr_js}")
    if args.published_audit_status:
        _print_published_audit_status()
    if args.build_published_audit:
        payload = write_audit(args.published_audit_json, args.published_audit_js)
        print(f"Published experiment audit complete: {payload['summary']['papers']} papers.")
        print(f"Wrote {args.published_audit_json}")
        print(f"Wrote {args.published_audit_js}")
    if args.s2_status:
        _print_s2_status()

    if args.sync_s2:
        payload = sync_semantic_scholar(
            scope_path=args.s2_scope,
            total_limit=args.s2_limit,
            per_query_limit=args.s2_per_query,
            citation_seed_count=args.s2_citation_seeds,
            citation_limit=args.s2_citation_limit,
            citation_depth=args.s2_depth,
            force_refresh=args.s2_force_refresh,
            json_path=args.s2_json,
            js_path=args.s2_js,
        )
        statistics = payload.get("statistics") or {}
        seed = payload.get("seed_expansion") or {}
        print(
            "Semantic Scholar sync complete: "
            f"{statistics.get('paper_count', 0)} papers, "
            f"{statistics.get('query_count', 0)} queries, "
            f"{seed.get('expanded_count', 0)} citation-graph additions."
        )
        print(f"Wrote {args.s2_json}")
        print(f"Wrote {args.s2_js}")

    utility_only = (
        (
            args.init_storage or args.storage_status or args.research_system_status or args.build_research_system
            or args.iclr_status or args.build_iclr_bank or args.iclr_audit_status or args.build_iclr_audit
            or args.machine_school_status or args.build_machine_school_bank
            or args.idea_discovery_v3_status or args.build_idea_discovery_v3
            or args.idea_discovery_v31_status or args.build_idea_discovery_v31
            or args.idea_discovery_v5_status or args.build_idea_discovery_v5
            or args.discussion_ready_status or args.build_discussion_ready or args.idea_discovery_v51_status
            or args.advisor_priority_status or args.build_advisor_priority
            or args.idea_discovery_v52_status or args.idea_discovery_v53_status
            or args.idea_discovery_v4_status or args.build_idea_discovery_v4
            or args.cvpr_status or args.build_cvpr_bank
            or args.published_audit_status or args.build_published_audit or args.s2_status
        )
        and not args.sync_s2
        and not args.check
    )
    if utility_only:
        return

    snapshot = build_snapshot()
    if args.check:
        print(
            f"OK: {len(snapshot.ideas)} ideas, {len(snapshot.funnel)} funnel stages, "
            f"architecture={snapshot.architecture_version}"
        )
        return
    write_snapshot(snapshot, args.json, args.js)
    print(f"Wrote {args.json}")
    print(f"Wrote {args.js}")


if __name__ == "__main__":
    main()
