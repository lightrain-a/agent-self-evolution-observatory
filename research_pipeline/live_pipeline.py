from __future__ import annotations

import json
import os
import time
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Sequence

from .config import PROJECT_ROOT, SemanticScholarSettings, StorageSettings
from .providers import ResearchScope, RetrievedPaper, SearchQuery
from .query_planner import DEFAULT_SCOPE_PATH, DefaultQueryPlanner, load_scope
from .semantic_scholar import (
    SemanticScholarClient,
    SemanticScholarRetriever,
    paper_to_json,
    paper_to_site_record,
)

STORAGE = StorageSettings.from_env()
DEFAULT_CORPUS_JSON = STORAGE.corpus_dir / "semantic-scholar-corpus.json"
DEFAULT_SITE_JS = STORAGE.site_artifact_dir / "s2-literature.js"
DEFAULT_LOCK = STORAGE.lock_dir / ".semantic-scholar-sync.lock"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


@contextmanager
def exclusive_sync_lock(path: Path = DEFAULT_LOCK, *, stale_after_seconds: float = 7200.0) -> Iterator[None]:
    """Prevent concurrent project syncs from sharing the same 1 req/s key."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and time.time() - path.stat().st_mtime > stale_after_seconds:
        path.unlink(missing_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise RuntimeError(
            f"Another Semantic Scholar sync appears to be running ({path}). "
            "Do not run concurrent syncs with the same 1 request/second key."
        ) from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({"pid": os.getpid(), "started_at": _now_iso()}))
        yield
    finally:
        path.unlink(missing_ok=True)


def _merge_papers(groups: Sequence[Sequence[RetrievedPaper]]) -> list[RetrievedPaper]:
    merged: dict[str, RetrievedPaper] = {}
    title_keys: dict[str, str] = {}
    for group in groups:
        for paper in group:
            normalized_title = " ".join(paper.title.lower().split())
            key = paper.paper_id or title_keys.setdefault(normalized_title, normalized_title)
            if not key or not paper.title:
                continue
            existing = merged.get(key)
            if existing is None:
                merged[key] = paper
                continue
            if not existing.abstract and paper.abstract:
                existing.abstract = paper.abstract
            if not existing.venue and paper.venue:
                existing.venue = paper.venue
            if not existing.url and paper.url:
                existing.url = paper.url
            matches = list(existing.metadata.get("matches") or [])
            for match in paper.metadata.get("matches") or []:
                if match not in matches:
                    matches.append(match)
            if matches:
                existing.metadata["matches"] = matches
            relations = list(existing.metadata.get("relations") or [])
            relation = paper.metadata.get("relation")
            if relation and relation not in relations:
                relations.append(relation)
            if relations:
                existing.metadata["relations"] = relations
            existing.metadata["retrievalScore"] = max(
                float(existing.metadata.get("retrievalScore") or 0.0),
                float(paper.metadata.get("retrievalScore") or 0.0),
            )
    results = list(merged.values())
    results.sort(
        key=lambda paper: (
            -float(paper.metadata.get("retrievalScore") or 0.0),
            -int(paper.metadata.get("citationCount") or 0),
            -(paper.year or 0),
            paper.title.lower(),
        )
    )
    return results


def _select_seed_results(papers: Sequence[RetrievedPaper], *, count: int) -> list[RetrievedPaper]:
    candidates: list[tuple[int, int, RetrievedPaper]] = []
    for paper in papers:
        seed_matches = [match for match in paper.metadata.get("matches") or [] if match.get("route") == "seed"]
        if not seed_matches:
            continue
        best_rank = min(int(match.get("rank") or 999) for match in seed_matches)
        priority = max(int(match.get("priority") or 0) for match in seed_matches)
        candidates.append((-priority, best_rank, paper))
    candidates.sort(key=lambda item: (item[0], item[1], -(item[2].metadata.get("citationCount") or 0)))
    selected: list[RetrievedPaper] = []
    seen: set[str] = set()
    for _, _, paper in candidates:
        if paper.paper_id in seen:
            continue
        seen.add(paper.paper_id)
        selected.append(paper)
        if len(selected) >= count:
            break
    return selected


def _scope_payload(scope: ResearchScope) -> dict[str, Any]:
    return asdict(scope)


def _query_payload(query: SearchQuery) -> dict[str, Any]:
    return asdict(query)


def _statistics(papers: Sequence[RetrievedPaper], queries: Sequence[SearchQuery]) -> dict[str, Any]:
    route_counts: Counter[str] = Counter()
    year_counts: Counter[str] = Counter()
    venue_counts: Counter[str] = Counter()
    open_access = 0
    with_abstract = 0
    for paper in papers:
        routes = {str(match.get("route") or "unknown") for match in paper.metadata.get("matches") or []}
        if not routes and paper.metadata.get("relation"):
            routes = {str(paper.metadata["relation"].get("type") or "citation-graph")}
        route_counts.update(routes)
        year_counts[str(paper.year or "unknown")] += 1
        if paper.venue:
            venue_counts[paper.venue] += 1
        if paper.abstract:
            with_abstract += 1
        if paper.metadata.get("isOpenAccess"):
            open_access += 1
    return {
        "query_count": len(queries),
        "paper_count": len(papers),
        "with_abstract": with_abstract,
        "open_access": open_access,
        "route_counts": dict(route_counts.most_common()),
        "year_counts": dict(sorted(year_counts.items(), reverse=True)),
        "top_venues": dict(venue_counts.most_common(20)),
    }


def build_live_payload(
    *,
    scope_path: Path = DEFAULT_SCOPE_PATH,
    total_limit: int = 120,
    per_query_limit: int = 8,
    citation_seed_count: int = 4,
    citation_limit: int = 6,
    citation_depth: int = 1,
    force_refresh: bool = False,
) -> dict[str, Any]:
    settings = SemanticScholarSettings.from_env(required=True)
    scope = load_scope(scope_path)
    planner = DefaultQueryPlanner()
    queries = planner.plan(scope, [])
    client = SemanticScholarClient(settings)
    retriever = SemanticScholarRetriever(
        client,
        per_query_limit=per_query_limit,
        citation_limit=citation_limit,
        force_refresh=force_refresh,
    )
    search_results = retriever.search(queries, limit=total_limit)
    seed_results = _select_seed_results(search_results, count=citation_seed_count)
    expanded = retriever.expand_citations(seed_results, depth=citation_depth) if citation_depth > 0 else []
    papers = _merge_papers([search_results, expanded])
    retrieved_at = _now_iso()
    provider = settings.safe_summary()
    provider.update(
        {
            "name": "Semantic Scholar Academic Graph API",
            "attribution": "Literature metadata powered by Semantic Scholar",
            "api_key_in_output": False,
        }
    )
    return {
        "schema_version": "1.0",
        "provider": provider,
        "retrieved_at": retrieved_at,
        "scope": _scope_payload(scope),
        "queries": [_query_payload(query) for query in queries],
        "seed_expansion": {
            "requested_seed_count": citation_seed_count,
            "resolved_seeds": [
                {"paper_id": paper.paper_id, "title": paper.title, "year": paper.year}
                for paper in seed_results
            ],
            "depth": citation_depth,
            "per_relation_limit": citation_limit,
            "expanded_count": len(expanded),
        },
        "statistics": {
            **_statistics(papers, queries),
            "provider_error_count": len(retriever.errors),
        },
        "provider_errors": retriever.errors,
        "papers": [paper_to_json(paper) for paper in papers],
        "site_records": [paper_to_site_record(paper) for paper in papers],
    }


def write_live_payload(
    payload: dict[str, Any],
    *,
    json_path: Path = DEFAULT_CORPUS_JSON,
    js_path: Path = DEFAULT_SITE_JS,
) -> None:
    _write_atomic(json_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    meta = {
        "schema_version": payload.get("schema_version"),
        "retrieved_at": payload.get("retrieved_at"),
        "provider": payload.get("provider"),
        "statistics": payload.get("statistics"),
        "seed_expansion": payload.get("seed_expansion"),
    }
    javascript = (
        "window.S2_LITERATURE_META = "
        + json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
        + ";\nwindow.S2_LIVE_PAPERS = "
        + json.dumps(payload.get("site_records") or [], ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    _write_atomic(js_path, javascript)


def sync_semantic_scholar(**kwargs: Any) -> dict[str, Any]:
    json_path = Path(kwargs.pop("json_path", DEFAULT_CORPUS_JSON))
    js_path = Path(kwargs.pop("js_path", DEFAULT_SITE_JS))
    with exclusive_sync_lock():
        payload = build_live_payload(**kwargs)
        write_live_payload(payload, json_path=json_path, js_path=js_path)
    return payload


def load_live_corpus(path: Path = DEFAULT_CORPUS_JSON) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("papers"), list):
        return None
    return payload
