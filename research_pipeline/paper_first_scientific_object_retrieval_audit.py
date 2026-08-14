from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .config import StorageSettings
from .paper_first_primary_evidence import (
    DEFAULT_MAX_PUBLICATION_AGE_DAYS,
    _source_exposure_state,
    _source_ref,
    discover_arxiv_fallback,
    select_primary_candidates,
)
from .paper_first_scientific_object_ontology import (
    _matches_candidate,
    _matches_object_purity,
    audit_candidate_object,
    load_scientific_object_config,
    reviewed_primary_cache_records,
)

SHADOW_OBJECT_QUERIES: dict[str, tuple[str, ...]] = {
    "knowledge_retrieval_state": (
        '(all:"self-evolving" OR all:"self-improving") AND all:agent AND (all:retrieval OR all:"knowledge graph" OR all:GraphRAG)',
        'all:"co-evolving knowledge graph"',
        'all:"self-evolving knowledge graph"',
        'all:"self-evolving retrieval"',
    ),
    "evaluator_reward_verifier": (
        'all:"evolving evaluator"',
        'all:"evaluator evolution"',
        'all:"evaluator adaptation" AND all:agent',
        'all:"verifier evolution" AND all:agent',
        'all:"reward model update" AND (all:agent OR all:"self-improving")',
    ),
    "tool_action_interface": (
        'all:agent AND (all:"tool acquisition" OR all:"tool creation" OR all:"tool synthesis" OR all:"tool evolution")',
    ),
}

SearchFn = Callable[..., tuple[list[dict[str, Any]], list[str]]]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def audit_candidate_retrieval(
    *,
    candidate_key: str,
    queries: tuple[str, ...],
    reviewed_records: list[dict[str, Any]],
    reviewed_refs: set[str],
    config: dict[str, Any],
    searcher: SearchFn = discover_arxiv_fallback,
    now: datetime | None = None,
    rate_limit_state_path: Path | None = None,
    per_query: int = 48,
    max_pages: int = 2,
    max_publication_age_days: float = DEFAULT_MAX_PUBLICATION_AGE_DAYS,
) -> dict[str, Any]:
    current = (now or _now()).astimezone(timezone.utc)
    spec = config["candidates"][candidate_key]
    support_gate = config["support_gate"]
    current_audit = audit_candidate_object(reviewed_records, candidate_key, config=config)
    rows_by_ref: dict[str, dict[str, Any]] = {}
    query_receipts: list[dict[str, Any]] = []
    all_errors: list[str] = []

    for query in queries:
        rows, errors = searcher(
            queries=(query,),
            per_query=per_query,
            max_pages=max_pages,
            min_interval_seconds=3.1,
            now=current,
            max_publication_age_days=max_publication_age_days,
            rate_limit_state_path=rate_limit_state_path,
        )
        # discover_arxiv_fallback intentionally keeps the cutoff-crossing page.
        # Re-apply the exact production eligibility gate before interpreting
        # any row as fresh candidate-object support.
        fresh_rows = select_primary_candidates(
            {"papers": rows},
            max_papers=max(1, len(rows)),
            now=current,
            max_publication_age_days=max_publication_age_days,
            lane_floor=0,
        )
        matched_refs: list[str] = []
        for paper in fresh_rows:
            if not _matches_candidate(paper, spec):
                continue
            ref = _source_ref(paper)
            if not ref:
                continue
            rows_by_ref.setdefault(
                ref,
                {
                    "ref": ref,
                    "title": str(paper.get("title") or ""),
                    "publication_date": str((paper.get("metadata") or {}).get("publicationDate") or ""),
                    "already_reviewed": ref in reviewed_refs,
                    "direct_object_match": _matches_object_purity(paper, spec),
                },
            )
            matched_refs.append(ref)
        query_receipts.append(
            {
                "query": query,
                "raw_rows": len(rows),
                "fresh_live_eligible_rows": len(fresh_rows),
                "candidate_support_refs": sorted(set(matched_refs)),
                "errors": list(errors),
                "scientific_authority": False,
            }
        )
        all_errors.extend(str(error) for error in errors)
        if any("RateLimit" in str(error) for error in errors):
            break

    support_rows = [rows_by_ref[key] for key in sorted(rows_by_ref)]
    new_support = [row for row in support_rows if not row["already_reviewed"]]
    new_direct = [row for row in new_support if row["direct_object_match"]]
    verified_support = int(current_audit["observed"]["reviewed_primary_refs"])
    potential_support_after_primary_verification = verified_support + len(new_support)
    minimum_verified_support = int(support_gate["minimum_reviewed_primary_refs"])

    if all_errors:
        status = "SHADOW_RETRIEVAL_INCOMPLETE"
    elif not new_support:
        status = "NO_NEW_SUPPORT_FOUND"
    elif potential_support_after_primary_verification >= minimum_verified_support:
        status = "PRIMARY_VERIFICATION_THRESHOLD_CANDIDATE"
    else:
        status = "RECALL_GAP_FOUND_SUPPORT_STILL_INSUFFICIENT"

    return {
        "candidate_key": candidate_key,
        "scientific_object": spec["scientific_object"],
        "status": status,
        "current_verified_support": verified_support,
        "minimum_verified_support": minimum_verified_support,
        "potential_support_after_primary_verification": potential_support_after_primary_verification,
        "fresh_candidate_support_refs": len(support_rows),
        "fresh_direct_object_refs": sum(bool(row["direct_object_match"]) for row in support_rows),
        "new_candidate_support_refs": len(new_support),
        "new_direct_object_refs": len(new_direct),
        "rows": support_rows,
        "queries": query_receipts,
        "errors": sorted(set(all_errors)),
        "primary_verification_required_before_support_count_changes": True,
        "live_query_set_change_authorized": False,
        "lane_preregistration_authorized": False,
        "scientific_authority": False,
    }


def build_shadow_scientific_object_retrieval_audit(
    *,
    storage: StorageSettings | None = None,
    searcher: SearchFn = discover_arxiv_fallback,
    now: datetime | None = None,
    query_map: dict[str, tuple[str, ...]] | None = None,
    rate_limit_state_path: Path | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    current = (now or _now()).astimezone(timezone.utc)
    config = load_scientific_object_config()
    reviewed_records = reviewed_primary_cache_records(storage)
    exposure, _, _, _ = _source_exposure_state(storage)
    queries = query_map or SHADOW_OBJECT_QUERIES
    cooldown_path = rate_limit_state_path or storage.data_root / "paper-first-problem-discovery" / "arxiv-rate-limit-cooldown.json"
    results: dict[str, Any] = {}
    for candidate_key, candidate_queries in queries.items():
        results[candidate_key] = audit_candidate_retrieval(
            candidate_key=candidate_key,
            queries=candidate_queries,
            reviewed_records=reviewed_records,
            reviewed_refs=set(exposure),
            config=config,
            searcher=searcher,
            now=current,
            rate_limit_state_path=cooldown_path,
        )
        if results[candidate_key]["status"] == "SHADOW_RETRIEVAL_INCOMPLETE" and any(
            "RateLimit" in error for error in results[candidate_key]["errors"]
        ):
            break

    statuses = {row["status"] for row in results.values()}
    status = "SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE"
    if "SHADOW_RETRIEVAL_INCOMPLETE" in statuses:
        status = "SHADOW_OBJECT_RETRIEVAL_AUDIT_INCOMPLETE"
    return {
        "schema_version": "1.0",
        "generated_at": current.replace(microsecond=0).isoformat(),
        "status": status,
        "policy": {
            "scientific_authority": False,
            "shadow_only": True,
            "live_query_set_changed": False,
            "selector_changed": False,
            "generator_called": False,
            "reviewer_called": False,
            "candidate_metadata_does_not_count_as_verified_primary_support": True,
            "production_freshness_and_relevance_gate_reapplied": True,
            "incomplete_or_rate_limited_query_is_not_negative_evidence": True,
            "primary_verification_required_before_lane_preregistration": True,
            "automatic_lane_activation": False,
        },
        "reviewed_primary_records": len(reviewed_records),
        "reviewed_source_refs": len(exposure),
        "results": results,
        "scientific_authority": False,
    }


def write_private_shadow_scientific_object_retrieval_audit(
    *,
    storage: StorageSettings | None = None,
    output_path: Path | None = None,
    searcher: SearchFn = discover_arxiv_fallback,
    now: datetime | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    state = build_shadow_scientific_object_retrieval_audit(storage=storage, searcher=searcher, now=now)
    target = output_path or storage.data_root / "paper-first-problem-discovery" / "scientific-object-retrieval-blindspot-audit-v2.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    state = write_private_shadow_scientific_object_retrieval_audit()
    print(json.dumps({key: value["status"] for key, value in state["results"].items()}, ensure_ascii=False))
