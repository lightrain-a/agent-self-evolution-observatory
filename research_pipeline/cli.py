from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import SemanticScholarSettings, StorageSettings
from .cvpr_idea_factory import DEFAULT_JS as DEFAULT_CVPR_JS
from .cvpr_idea_factory import DEFAULT_JSON as DEFAULT_CVPR_JSON
from .cvpr_idea_factory import build_cvpr_idea_bank, validate_bank, write_cvpr_idea_bank
from .iclr_idea_factory import DEFAULT_JS as DEFAULT_ICLR_JS
from .iclr_idea_factory import DEFAULT_JSON as DEFAULT_ICLR_JSON
from .iclr_idea_factory import build_iclr_idea_bank, validate_bank as validate_iclr_bank, write_iclr_idea_bank
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
