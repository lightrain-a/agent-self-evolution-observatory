from __future__ import annotations

import hashlib
import html
import json
import re
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable

import requests

from .config import PROJECT_ROOT, StorageSettings
from .live_pipeline import DEFAULT_CORPUS_JSON, load_live_corpus

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.js"
DEFAULT_MAX_PAPERS = 16
DEFAULT_MAX_CORPUS_AGE_DAYS = 10.0
DEFAULT_MIN_INTERVAL_SECONDS = 0.75

_RELEVANCE_TERMS = (
    "self-evol",
    "self evol",
    "self-improv",
    "self improv",
    "agent skill",
    "agent memory",
    "agentic workflow",
    "harness",
    "continual agent",
    "autonomous agent",
    "evolving agent",
    "agent evolution",
    "world model",
    "embodied agent",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_iso(value: str) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _age_days(value: str, now: datetime) -> float | None:
    parsed = _parse_iso(value)
    if parsed is None:
        return None
    return max(0.0, (now - parsed).total_seconds() / 86400.0)


def _normalize_title(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).split())


def _title_similarity(a: str, b: str) -> float:
    x, y = _normalize_title(a), _normalize_title(b)
    if not x or not y:
        return 0.0
    if x == y:
        return 1.0
    return SequenceMatcher(a=x, b=y).ratio()


def _strip_html(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment, flags=re.S)
    return " ".join(html.unescape(text).split())


def _meta_content(page: str, name: str) -> str:
    patterns = (
        rf'<meta\s+[^>]*name=["\']{re.escape(name)}["\'][^>]*content=["\']([^"\']*)["\'][^>]*>',
        rf'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']{re.escape(name)}["\'][^>]*>',
    )
    for pattern in patterns:
        match = re.search(pattern, page, flags=re.I | re.S)
        if match:
            return html.unescape(match.group(1)).strip()
    return ""


def parse_arxiv_page(page: str) -> dict[str, str]:
    title = _meta_content(page, "citation_title")
    abstract_match = re.search(
        r'<blockquote\s+[^>]*class=["\'][^"\']*abstract[^"\']*["\'][^>]*>(.*?)</blockquote>',
        page,
        flags=re.I | re.S,
    )
    abstract = _strip_html(abstract_match.group(1)) if abstract_match else ""
    abstract = re.sub(r"^Abstract:\s*", "", abstract, flags=re.I).strip()
    return {"title": title, "abstract": abstract}


def _arxiv_id(paper: dict[str, Any]) -> str:
    metadata = paper.get("metadata") or {}
    external = metadata.get("externalIds") or {}
    if not isinstance(external, dict):
        return ""
    for key in ("ArXiv", "arXiv", "ARXIV", "arxiv"):
        value = str(external.get(key) or "").strip()
        if value:
            return value.removeprefix("arXiv:")
    return ""


def _relevance_score(paper: dict[str, Any]) -> int:
    haystack = f"{paper.get('title','')} {paper.get('abstract','')}".lower()
    score = sum(2 if term in str(paper.get("title") or "").lower() else 1 for term in _RELEVANCE_TERMS if term in haystack)
    matches = (paper.get("metadata") or {}).get("matches") or []
    if any(str(row.get("route") or "") in {"seed", "mechanism", "failure", "topic"} for row in matches if isinstance(row, dict)):
        score += 1
    return score


def select_primary_candidates(corpus: dict[str, Any], *, max_papers: int = DEFAULT_MAX_PAPERS) -> list[dict[str, Any]]:
    selected: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    seen: set[str] = set()
    for paper in corpus.get("papers") or []:
        if not isinstance(paper, dict):
            continue
        arxiv_id = _arxiv_id(paper)
        abstract = str(paper.get("abstract") or "").strip()
        score = _relevance_score(paper)
        if not arxiv_id or not abstract or score < 2 or arxiv_id in seen:
            continue
        seen.add(arxiv_id)
        metadata = paper.get("metadata") or {}
        publication_date = str(metadata.get("publicationDate") or "")
        year = int(paper.get("year") or 0)
        citation_count = int(metadata.get("citationCount") or 0)
        retrieval_score = float(metadata.get("retrievalScore") or 0.0)
        rank_key = (publication_date, year, score, retrieval_score, citation_count, str(paper.get("title") or ""))
        selected.append((rank_key, paper))
    selected.sort(key=lambda item: item[0], reverse=True)
    return [paper for _, paper in selected[: max(0, max_papers)]]


def _default_requester(url: str, *, timeout: float, headers: dict[str, str]):
    return requests.get(url, timeout=timeout, headers=headers)


def private_primary_pool_path(storage: StorageSettings | None = None) -> Path:
    storage = storage or StorageSettings.from_env()
    return storage.data_root / "paper-first-problem-discovery" / "primary-evidence-pool.json"


def _private_paths(storage: StorageSettings) -> tuple[Path, Path]:
    root = storage.data_root / "paper-first-problem-discovery"
    return private_primary_pool_path(storage), root / "primary-sources"


def load_private_primary_pool(path: Path | None = None, *, storage: StorageSettings | None = None) -> dict[str, Any] | None:
    source = path or private_primary_pool_path(storage)
    if not source.exists():
        return None
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        return None
    return payload


def build_primary_evidence_pool(
    *,
    storage: StorageSettings | None = None,
    corpus_path: Path | None = None,
    max_papers: int = DEFAULT_MAX_PAPERS,
    max_corpus_age_days: float = DEFAULT_MAX_CORPUS_AGE_DAYS,
    requester: Callable[..., Any] | None = None,
    now: datetime | None = None,
    min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
    cache_dir: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    storage = storage or StorageSettings.from_env()
    corpus_path = corpus_path or storage.corpus_dir / "semantic-scholar-corpus.json"
    corpus = load_live_corpus(corpus_path)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    private_pool_path, default_cache = _private_paths(storage)
    cache_dir = cache_dir or default_cache
    public_state: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": _now(),
        "corpus_path": str(corpus_path),
        "private_pool_path": str(private_pool_path),
        "policy": {
            "semantic_scholar_is_discovery_metadata_not_primary_evidence": True,
            "verified_primary_page_required": True,
            "arxiv_source_sha_required": True,
            "stale_corpus_blocks_generation": True,
            "no_parallel_primary_fetch": True,
            "full_abstracts_remain_private_data_artifacts": True,
            "candidate_generation_authority": False,
            "method_authority": False,
            "experiment_authority": False,
            "p0_authority": False,
        },
        "summary": {
            "corpus_available": bool(corpus),
            "corpus_fresh": False,
            "selected": 0,
            "verified": 0,
            "fetch_errors": 0,
            "title_mismatches": 0,
            "candidate_generation_ready": False,
        },
        "records": [],
        "errors": [],
    }
    private: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": public_state["generated_at"],
        "corpus_path": str(corpus_path),
        "records": [],
        "errors": [],
    }
    if not corpus:
        public_state["status"] = "NO_CORPUS"
        private["status"] = "NO_CORPUS"
        return public_state, private
    retrieved_at = str(corpus.get("retrieved_at") or "")
    corpus_age = _age_days(retrieved_at, current)
    fresh = corpus_age is not None and corpus_age <= max_corpus_age_days
    public_state["corpus_retrieved_at"] = retrieved_at
    public_state["corpus_age_days"] = corpus_age
    public_state["summary"]["corpus_fresh"] = fresh
    private["corpus_retrieved_at"] = retrieved_at
    if not fresh:
        public_state["status"] = "STALE_CORPUS_BLOCKED"
        private["status"] = "STALE_CORPUS_BLOCKED"
        return public_state, private

    candidates = select_primary_candidates(corpus, max_papers=max_papers)
    public_state["summary"]["selected"] = len(candidates)
    fetch = requester or _default_requester
    cache_dir.mkdir(parents=True, exist_ok=True)
    last_fetch_started: float | None = None
    verified: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    title_mismatches = 0
    for paper in candidates:
        arxiv_id = _arxiv_id(paper)
        url = f"https://arxiv.org/abs/{arxiv_id}"
        if last_fetch_started is not None and min_interval_seconds > 0:
            wait = min_interval_seconds - (time.monotonic() - last_fetch_started)
            if wait > 0:
                time.sleep(wait)
        last_fetch_started = time.monotonic()
        try:
            response = fetch(url, timeout=25.0, headers={"User-Agent": "Agent-Self-Evolution-Observatory/primary-evidence"})
            status = int(getattr(response, "status_code", 200))
            if status >= 400:
                raise RuntimeError(f"HTTP {status}")
            raw_text = str(getattr(response, "text", "") or "")
            if not raw_text:
                raise RuntimeError("empty-primary-page")
            parsed = parse_arxiv_page(raw_text)
            if not parsed["title"] or not parsed["abstract"]:
                raise RuntimeError("primary-page-missing-title-or-abstract")
            similarity = _title_similarity(str(paper.get("title") or ""), parsed["title"])
            if similarity < 0.72:
                title_mismatches += 1
                errors.append({"ref": f"arXiv:{arxiv_id}", "error": "title-mismatch", "similarity": round(similarity, 4)})
                continue
            raw_bytes = raw_text.encode("utf-8")
            source_sha = hashlib.sha256(raw_bytes).hexdigest()
            abstract_sha = hashlib.sha256(parsed["abstract"].encode("utf-8")).hexdigest()
            cache_path = cache_dir / f"arxiv-{re.sub(r'[^0-9A-Za-z._-]+','_',arxiv_id)}-{source_sha[:12]}.html"
            cache_path.write_bytes(raw_bytes)
            record = {
                "evidence_id": hashlib.sha256(f"arXiv:{arxiv_id}:{source_sha}".encode("utf-8")).hexdigest(),
                "ref": f"arXiv:{arxiv_id}",
                "title": parsed["title"],
                "primary_url": url,
                "source_sha256": source_sha,
                "abstract_sha256": abstract_sha,
                "abstract": parsed["abstract"],
                "year": paper.get("year"),
                "publication_date": (paper.get("metadata") or {}).get("publicationDate"),
                "s2_paper_id": paper.get("paper_id"),
                "s2_retrieved_at": (paper.get("metadata") or {}).get("retrievedAt"),
                "fetched_at": _now(),
                "cache_path": str(cache_path),
                "title_similarity": round(similarity, 4),
                "primary_source_verified": True,
            }
            verified.append(record)
        except Exception as error:  # network/provider failures are evidence absence, not scientific negatives
            errors.append({"ref": f"arXiv:{arxiv_id}", "error": f"{type(error).__name__}:{str(error)[:240]}"})

    private["records"] = verified
    private["errors"] = errors
    private["status"] = "READY" if len(verified) >= 4 else "INSUFFICIENT_PRIMARY_EVIDENCE"
    public_state["summary"].update(
        {
            "verified": len(verified),
            "fetch_errors": sum(1 for row in errors if row.get("error") != "title-mismatch"),
            "title_mismatches": title_mismatches,
            "candidate_generation_ready": len(verified) >= 4,
        }
    )
    public_state["records"] = [
        {key: row[key] for key in ("evidence_id", "ref", "title", "primary_url", "source_sha256", "abstract_sha256", "year", "publication_date", "fetched_at")}
        for row in verified
    ]
    public_state["errors"] = errors
    public_state["status"] = private["status"]
    return public_state, private


def load_primary_evidence_state(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version":"1.0","status":"NOT_RUN","policy":{"candidate_generation_authority":False,"method_authority":False,"experiment_authority":False,"p0_authority":False},
            "summary":{"corpus_available":False,"corpus_fresh":False,"selected":0,"verified":0,"fetch_errors":0,"title_mismatches":0,"candidate_generation_ready":False},"records":[],"errors":[],
        }
    try:
        payload=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return {"schema_version":"1.0","status":"STATE_UNREADABLE","policy":{"candidate_generation_authority":False,"method_authority":False,"experiment_authority":False,"p0_authority":False},"summary":{"corpus_available":False,"corpus_fresh":False,"selected":0,"verified":0,"fetch_errors":1,"title_mismatches":0,"candidate_generation_ready":False},"records":[],"errors":["state-unreadable"]}
    return payload if isinstance(payload,dict) else {"schema_version":"1.0","status":"STATE_INVALID","summary":{},"records":[],"errors":["state-invalid"]}


def write_primary_evidence_pool(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
    *,
    storage: StorageSettings | None = None,
    corpus_path: Path | None = None,
    max_papers: int = DEFAULT_MAX_PAPERS,
    max_corpus_age_days: float = DEFAULT_MAX_CORPUS_AGE_DAYS,
    requester: Callable[..., Any] | None = None,
    now: datetime | None = None,
    min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    state, private = build_primary_evidence_pool(
        storage=storage,
        corpus_path=corpus_path,
        max_papers=max_papers,
        max_corpus_age_days=max_corpus_age_days,
        requester=requester,
        now=now,
        min_interval_seconds=min_interval_seconds,
    )
    private_pool_path, _ = _private_paths(storage)
    private_pool_path.parent.mkdir(parents=True, exist_ok=True)
    private_pool_path.write_text(json.dumps(private, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PRIMARY_EVIDENCE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_primary_evidence_pool(), ensure_ascii=False))
