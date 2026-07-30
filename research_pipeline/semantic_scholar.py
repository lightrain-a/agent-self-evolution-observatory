from __future__ import annotations

import hashlib
import json
import math
import os
import random
import threading
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence
from urllib.parse import quote, urlencode

import requests

from .config import SemanticScholarSettings
from .providers import RetrievedPaper, SearchQuery

PAPER_FIELDS = (
    "paperId",
    "corpusId",
    "title",
    "abstract",
    "year",
    "venue",
    "url",
    "authors",
    "externalIds",
    "citationCount",
    "influentialCitationCount",
    "referenceCount",
    "publicationDate",
    "publicationTypes",
    "fieldsOfStudy",
    "s2FieldsOfStudy",
    "isOpenAccess",
    "openAccessPdf",
)
PAPER_FIELDS_CSV = ",".join(PAPER_FIELDS)


class SemanticScholarError(RuntimeError):
    """Base error for Semantic Scholar provider failures."""


class SemanticScholarHTTPError(SemanticScholarError):
    def __init__(self, status: int, message: str, *, url: str = "") -> None:
        super().__init__(f"Semantic Scholar HTTP {status}: {message}")
        self.status = status
        self.url = url


class SharedRateLimiter:
    """One limiter shared by every endpoint used by a client instance."""

    def __init__(
        self,
        min_interval_seconds: float,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.min_interval_seconds = min_interval_seconds
        self._clock = clock
        self._sleep = sleeper
        self._lock = threading.Lock()
        self._last_request_started: float | None = None

    def wait(self) -> None:
        with self._lock:
            now = self._clock()
            if self._last_request_started is not None:
                wait_for = self.min_interval_seconds - (now - self._last_request_started)
                if wait_for > 0:
                    self._sleep(wait_for)
                    now = self._clock()
            self._last_request_started = now


class DiskResponseCache:
    def __init__(self, directory: Path, ttl_hours: float) -> None:
        self.directory = directory
        self.ttl_seconds = ttl_hours * 3600.0

    @staticmethod
    def key(url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def _path(self, url: str) -> Path:
        return self.directory / f"{self.key(url)}.json"

    def get(self, url: str) -> Any | None:
        path = self._path(url)
        if not path.exists():
            return None
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            stored_at = float(envelope.get("stored_at", 0.0))
            if self.ttl_seconds == 0 or time.time() - stored_at > self.ttl_seconds:
                return None
            return envelope.get("payload")
        except (OSError, ValueError, TypeError):
            return None

    def put(self, url: str, payload: Any) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        envelope = {
            "stored_at": time.time(),
            "url": url,
            "payload": payload,
        }
        target = self._path(url)
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(envelope, ensure_ascii=False), encoding="utf-8")
        os.replace(temporary, target)


class SemanticScholarClient:
    """Small dependency-free client for the Semantic Scholar Academic Graph API."""

    def __init__(
        self,
        settings: SemanticScholarSettings,
        *,
        limiter: SharedRateLimiter | None = None,
        requester: Callable[..., Any] | None = None,
        session: requests.Session | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if not settings.api_key:
            raise RuntimeError("Semantic Scholar API key is empty")
        self.settings = settings
        self.limiter = limiter or SharedRateLimiter(settings.min_interval_seconds, sleeper=sleeper)
        self.cache = DiskResponseCache(settings.cache_dir, settings.cache_ttl_hours)
        self._session = session or requests.Session()
        self._request = requester or self._session.request
        self._sleep = sleeper

    def _build_url(self, path: str, params: dict[str, Any] | None = None) -> str:
        clean_params = {
            key: value
            for key, value in (params or {}).items()
            if value is not None and value != "" and value != []
        }
        query = urlencode(clean_params, doseq=True)
        return f"{self.settings.base_url}/{path.lstrip('/')}" + (f"?{query}" if query else "")

    @staticmethod
    def _error_message(response: Any) -> str:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                return str(payload.get("message") or payload.get("error") or payload)
            return str(payload)
        except Exception:
            return str(getattr(response, "text", "") or f"HTTP {getattr(response, 'status_code', 'error')}")[:500]

    def get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        force_refresh: bool = False,
        use_cache: bool = True,
    ) -> Any:
        url = self._build_url(path, params)
        if use_cache and not force_refresh:
            cached = self.cache.get(url)
            if cached is not None:
                return cached

        attempts = self.settings.max_retries + 1
        for attempt in range(attempts):
            self.limiter.wait()
            headers = {
                "x-api-key": self.settings.api_key,
                "Accept": "application/json",
                "User-Agent": "Agent-Self-Evolution-Observatory/2.1",
            }
            try:
                response = self._request(
                    "GET",
                    url,
                    headers=headers,
                    timeout=self.settings.timeout_seconds,
                )
                status = int(getattr(response, "status_code", 200))
                if status >= 400:
                    message = self._error_message(response)
                    retryable = status == 429 or 500 <= status < 600
                    if not retryable or attempt + 1 >= attempts:
                        raise SemanticScholarHTTPError(status, message, url=url)
                    response_headers = getattr(response, "headers", {}) or {}
                    retry_after = response_headers.get("Retry-After")
                    try:
                        delay = float(retry_after) if retry_after else 0.0
                    except (TypeError, ValueError):
                        delay = 0.0
                    if delay <= 0:
                        delay = min(30.0, (2**attempt) * self.settings.min_interval_seconds)
                    delay += random.uniform(0.0, 0.2)
                    self._sleep(delay)
                    continue
                payload = response.json()
                if use_cache:
                    self.cache.put(url, payload)
                return payload
            except SemanticScholarHTTPError:
                raise
            except (requests.RequestException, TimeoutError, OSError, ValueError, json.JSONDecodeError) as error:
                if attempt + 1 >= attempts:
                    raise SemanticScholarError(f"Semantic Scholar request failed: {error}") from error
                self._sleep(min(30.0, (2**attempt) * self.settings.min_interval_seconds))
        raise AssertionError("unreachable")

    def search_papers(
        self,
        query: str,
        *,
        limit: int = 10,
        offset: int = 0,
        filters: dict[str, str] | None = None,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        params: dict[str, Any] = {
            "query": query.strip().replace("-", " "),
            "offset": offset,
            "limit": max(1, min(100, limit)),
            "fields": PAPER_FIELDS_CSV,
        }
        params.update(filters or {})
        payload = self.get_json("paper/search", params, force_refresh=force_refresh)
        return list(payload.get("data") or [])

    def get_paper(self, paper_id: str, *, force_refresh: bool = False) -> dict[str, Any]:
        encoded = quote(paper_id, safe=":")
        return dict(
            self.get_json(
                f"paper/{encoded}",
                {"fields": PAPER_FIELDS_CSV},
                force_refresh=force_refresh,
            )
        )

    def get_citations(
        self,
        paper_id: str,
        *,
        limit: int = 10,
        offset: int = 0,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        encoded = quote(paper_id, safe=":")
        nested_fields = ",".join(["contexts", "intents", "isInfluential"] + [f"citingPaper.{field}" for field in PAPER_FIELDS])
        payload = self.get_json(
            f"paper/{encoded}/citations",
            {"offset": offset, "limit": max(1, min(1000, limit)), "fields": nested_fields},
            force_refresh=force_refresh,
        )
        return list(payload.get("data") or [])

    def get_references(
        self,
        paper_id: str,
        *,
        limit: int = 10,
        offset: int = 0,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        encoded = quote(paper_id, safe=":")
        nested_fields = ",".join(["contexts", "intents", "isInfluential"] + [f"citedPaper.{field}" for field in PAPER_FIELDS])
        payload = self.get_json(
            f"paper/{encoded}/references",
            {"offset": offset, "limit": max(1, min(1000, limit)), "fields": nested_fields},
            force_refresh=force_refresh,
        )
        return list(payload.get("data") or [])


def _authors(raw: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"authorId": str(author.get("authorId") or ""), "name": str(author.get("name") or "")}
        for author in raw.get("authors") or []
        if author.get("name")
    ]


def retrieved_paper_from_api(raw: dict[str, Any], *, relation: dict[str, Any] | None = None) -> RetrievedPaper:
    metadata = {
        "source": "semantic-scholar",
        "corpusId": raw.get("corpusId"),
        "externalIds": raw.get("externalIds") or {},
        "authors": _authors(raw),
        "citationCount": raw.get("citationCount"),
        "influentialCitationCount": raw.get("influentialCitationCount"),
        "referenceCount": raw.get("referenceCount"),
        "publicationDate": raw.get("publicationDate"),
        "publicationTypes": raw.get("publicationTypes") or [],
        "fieldsOfStudy": raw.get("fieldsOfStudy") or [],
        "s2FieldsOfStudy": raw.get("s2FieldsOfStudy") or [],
        "isOpenAccess": raw.get("isOpenAccess"),
        "openAccessPdf": raw.get("openAccessPdf") or {},
        "retrievedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    if relation:
        metadata["relation"] = relation
    return RetrievedPaper(
        paper_id=str(raw.get("paperId") or ""),
        title=str(raw.get("title") or "").strip(),
        year=raw.get("year"),
        venue=str(raw.get("venue") or ""),
        abstract=str(raw.get("abstract") or ""),
        url=str(raw.get("url") or ""),
        metadata=metadata,
    )


class SemanticScholarRetriever:
    """Search and citation expansion implementation for LiteratureRetriever."""

    def __init__(
        self,
        client: SemanticScholarClient,
        *,
        per_query_limit: int = 10,
        citation_limit: int = 8,
        force_refresh: bool = False,
    ) -> None:
        self.client = client
        self.per_query_limit = max(1, min(100, per_query_limit))
        self.citation_limit = max(1, min(1000, citation_limit))
        self.force_refresh = force_refresh
        self.errors: list[dict[str, Any]] = []

    @staticmethod
    def _merge(existing: RetrievedPaper, incoming: RetrievedPaper, query: SearchQuery, rank: int) -> RetrievedPaper:
        metadata = dict(existing.metadata)
        matches = list(metadata.get("matches") or [])
        match = {
            "query": query.query,
            "route": query.route,
            "purpose": query.purpose,
            "priority": query.priority,
            "rank": rank,
        }
        if match not in matches:
            matches.append(match)
        metadata["matches"] = matches
        metadata["retrievalScore"] = max(
            float(metadata.get("retrievalScore") or 0.0),
            float(query.priority) + 1.0 / max(rank, 1),
        )
        existing.metadata = metadata
        if not existing.abstract and incoming.abstract:
            existing.abstract = incoming.abstract
        if not existing.url and incoming.url:
            existing.url = incoming.url
        if not existing.venue and incoming.venue:
            existing.venue = incoming.venue
        return existing

    def search(self, queries: Sequence[SearchQuery], *, limit: int) -> list[RetrievedPaper]:
        if limit <= 0:
            return []
        papers: dict[str, RetrievedPaper] = {}
        title_fallback: dict[str, str] = {}
        ordered_queries = sorted(queries, key=lambda item: (-item.priority, item.route, item.query))
        adaptive_limit = max(self.per_query_limit, math.ceil(limit / max(len(ordered_queries), 1)))
        request_limit = min(100, adaptive_limit)
        for query in ordered_queries:
            try:
                raw_results = self.client.search_papers(
                    query.query,
                    limit=request_limit,
                    filters=query.filters,
                    force_refresh=self.force_refresh,
                )
            except SemanticScholarError as error:
                self.errors.append({
                    "stage": "search",
                    "route": query.route,
                    "query": query.query,
                    "error": str(error),
                })
                continue
            for rank, raw in enumerate(raw_results, start=1):
                paper = retrieved_paper_from_api(raw)
                if not paper.title:
                    continue
                key = paper.paper_id or hashlib.sha1(paper.title.lower().encode("utf-8")).hexdigest()
                if not paper.paper_id:
                    normalized = " ".join(paper.title.lower().split())
                    key = title_fallback.setdefault(normalized, key)
                if key in papers:
                    papers[key] = self._merge(papers[key], paper, query, rank)
                else:
                    paper.metadata["matches"] = [
                        {
                            "query": query.query,
                            "route": query.route,
                            "purpose": query.purpose,
                            "priority": query.priority,
                            "rank": rank,
                        }
                    ]
                    paper.metadata["retrievalScore"] = float(query.priority) + 1.0 / rank
                    papers[key] = paper
        results = list(papers.values())
        results.sort(
            key=lambda paper: (
                -float(paper.metadata.get("retrievalScore") or 0.0),
                -int(paper.metadata.get("citationCount") or 0),
                -(paper.year or 0),
                paper.title.lower(),
            )
        )
        return results[:limit]

    def expand_citations(self, papers: Sequence[RetrievedPaper], *, depth: int = 1) -> list[RetrievedPaper]:
        seen = {paper.paper_id for paper in papers if paper.paper_id}
        expanded: list[RetrievedPaper] = []
        frontier = [paper for paper in papers if paper.paper_id]
        for current_depth in range(1, max(depth, 0) + 1):
            next_frontier: list[RetrievedPaper] = []
            for paper in frontier:
                relations: list[tuple[str, str, list[dict[str, Any]]]] = []
                for relation_name, payload_key, fetcher in (
                    ("citation", "citingPaper", self.client.get_citations),
                    ("reference", "citedPaper", self.client.get_references),
                ):
                    try:
                        records = fetcher(
                            paper.paper_id,
                            limit=self.citation_limit,
                            force_refresh=self.force_refresh,
                        )
                    except SemanticScholarError as error:
                        self.errors.append({
                            "stage": "citation-expand",
                            "relation": relation_name,
                            "paper_id": paper.paper_id,
                            "paper_title": paper.title,
                            "error": str(error),
                        })
                        continue
                    relations.append((relation_name, payload_key, records))
                for relation_name, payload_key, records in relations:
                    for record in records:
                        raw = record.get(payload_key) or {}
                        related = retrieved_paper_from_api(
                            raw,
                            relation={
                                "type": relation_name,
                                "sourcePaperId": paper.paper_id,
                                "sourceTitle": paper.title,
                                "depth": current_depth,
                                "isInfluential": bool(record.get("isInfluential")),
                                "intents": record.get("intents") or [],
                                "contexts": record.get("contexts") or [],
                            },
                        )
                        if not related.paper_id or related.paper_id in seen or not related.title:
                            continue
                        seen.add(related.paper_id)
                        expanded.append(related)
                        next_frontier.append(related)
            frontier = next_frontier
            if not frontier:
                break
        return expanded


def paper_to_json(paper: RetrievedPaper) -> dict[str, Any]:
    return asdict(paper)


def paper_to_site_record(paper: RetrievedPaper) -> dict[str, Any]:
    matches = list(paper.metadata.get("matches") or [])
    routes = sorted({str(match.get("route") or "topic") for match in matches})
    fields = [str(field) for field in paper.metadata.get("fieldsOfStudy") or []]
    visual_terms = (
        "vision",
        "visual",
        "image",
        "video",
        "multimodal",
        "embodied",
        "robot",
        "navigation",
        "gui",
        "web agent",
    )
    haystack = f"{paper.title} {paper.abstract} {' '.join(fields)}".lower()
    vision = any(term in haystack for term in visual_terms)
    abstract = " ".join(paper.abstract.split())
    summary = abstract[:420] + ("…" if len(abstract) > 420 else "")
    route_label = ", ".join(routes) if routes else "topic"
    return {
        "year": paper.year,
        "title": paper.title,
        "venue": paper.venue or "Semantic Scholar record",
        "url": paper.url or f"https://www.semanticscholar.org/paper/{paper.paper_id}",
        "category": "Live literature",
        "subcategory": route_label,
        "updateTarget": "agent component",
        "signal": "Semantic Scholar retrieval",
        "vision": vision,
        "source": "semantic-scholar",
        "summary": summary,
        "summaryZh": "",
        "citationCount": paper.metadata.get("citationCount"),
        "s2PaperId": paper.paper_id,
        "s2CorpusId": paper.metadata.get("corpusId"),
        "s2RetrievedAt": paper.metadata.get("retrievedAt"),
        "s2Routes": routes,
        "s2Matches": matches,
    }
