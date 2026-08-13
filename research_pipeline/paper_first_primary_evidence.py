from __future__ import annotations

import hashlib
import html
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import requests

from .config import PROJECT_ROOT, StorageSettings
from .live_pipeline import DEFAULT_CORPUS_JSON, load_live_corpus
from .public_state_redaction import redact_private_paths

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.js"
DEFAULT_MAX_PAPERS = 32
DEFAULT_LANE_FLOOR = 1
PRIMARY_EVIDENCE_LANES: tuple[dict[str, Any], ...] = (
    {"key":"skill_harness","terms":("skill","harness","workflow evolution","agent workflow")},
    {"key":"memory_continual","terms":("agent memory","memory","continual agent","lifelong agent","experience management")},
    {"key":"embodied","terms":("embodied","robot","robotic","navigation","physical autonomy")},
    {"key":"collective","terms":("multi-agent","multi agent","collaborative harness","collaborative agent","swarm","group-evolving","group evolving","agent society")},
    {"key":"autonomous_science","terms":("symbolic regression","scientific discovery","scientific agent","research agent","ai scientist","autonomous research","hypothesis generation","experiment planning")},
    {"key":"runtime_deployment","terms":("runtime","deployment","production agent","customer support","long-horizon agent","monitoring","runtime contract")},
    {"key":"safety_reliability","terms":("agent safety","safety harness","reliability","robustness","adversarial","security","failure")},
)
DEFAULT_MAX_CORPUS_AGE_DAYS = 10.0
DEFAULT_MAX_PUBLICATION_AGE_DAYS = 60.0
DEFAULT_MIN_INTERVAL_SECONDS = 0.75
DEFAULT_RECENT_VERIFIED_CACHE_REUSE_HOURS = 12.0
DEFAULT_RECENT_FULLTEXT_FAILURE_COOLDOWN_HOURS = 2.0
DEFAULT_MAX_PRIMARY_RESPONSE_BYTES = 24 * 1024 * 1024
DEFAULT_ARXIV_QUERY_INTERVAL_SECONDS = 3.1
DEFAULT_ARXIV_PER_QUERY = 12
EMPIRICAL_FACT_EXTRACTION_VERSION = "precision-v2"
DEFAULT_ARXIV_QUERIES = (
    'all:"self-evolving" AND all:agent',
    'all:"self-improving" AND all:agent',
    'all:"agent evolution" AND all:LLM',
    '(all:"agent skill" OR all:harness) AND all:evolution',
    '(all:"agent memory" OR all:"continual agent") AND (all:evolution OR all:"self-improving")',
    'all:"embodied agent" AND (all:evolution OR all:"self-improving")',
    '(all:"multi-agent" OR all:"collaborative agent") AND (all:evolution OR all:"self-improving")',
    '(all:"scientific agent" OR all:"research agent" OR all:"symbolic regression") AND (all:evolution OR all:"self-evolving")',
    '(all:runtime OR all:deployment) AND all:agent AND (all:evolution OR all:"self-improving")',
    '(all:safety OR all:reliability) AND all:agent AND (all:evolution OR all:"self-improving")',
)

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


def _age_hours(value: str, now: datetime) -> float | None:
    parsed = _parse_iso(value)
    if parsed is None:
        return None
    return max(0.0, (now - parsed).total_seconds() / 3600.0)


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


_FULLTEXT_SECTION_TERMS = (
    "result", "experiment", "evaluation", "analysis", "ablation", "discussion",
    "limitation", "conclusion", "finding", "failure", "safety", "robust",
)
_STRONG_EMPIRICAL_CUE_RE = re.compile(
    r"\b(we\s+(?:find|found|observe|observed|show|demonstrate)|"
    r"results?\s+(?:show|shows|indicate|indicates|demonstrate|demonstrates|reveal|reveals)|"
    r"(?:table|figure)\s+\d+[a-z]?\s+(?:shows|demonstrates|summarizes|establishes))\b",
    flags=re.I,
)
_DIRECTIONAL_RESULT_RE = re.compile(
    r"\b(outperform(?:s|ed|ing)?|improv(?:e|es|ed|ing|ement)|decreas(?:e|es|ed|ing)|"
    r"increas(?:e|es|ed|ing)|drop(?:s|ped|ping)?|gain(?:s|ed|ing)?|boost(?:s|ed|ing)?|"
    r"reduc(?:e|es|ed|ing|tion)|surpass(?:es|ed|ing)?|better|worse|higher|lower|"
    r"harm(?:s|ed|ful)?|degrad(?:e|es|ed|ing|ation)|fail(?:s|ed|ure|ures)?)\b",
    flags=re.I,
)
_NUMERIC_RESULT_RE = re.compile(r"(?:\b\d+(?:\.\d+)?\s*%|\b\d+\.\d+\b|\b\d+\s*/\s*\d+\b|\b\d+\s+(?:points?|tasks?|cases?|runs?|trials?)\b)", flags=re.I)
_NUMERIC_COMPARISON_RE = re.compile(r"\b(reach(?:es|ed)?|achiev(?:e|es|ed)?|rise(?:s|rose)?|yield(?:s|ed)?|attain(?:s|ed)?|score(?:s|d)?|versus|vs\.?|from)\b", flags=re.I)
_OWN_RESULT_SUBJECT_RE = re.compile(r"\b(our\s+(?:method|approach|system|agent|model|framework)|the\s+(?:proposed|evolved|learned)\s+(?:method|approach|system|agent|model|harness|policy))\b", flags=re.I)
_NAMED_RESULT_SUBJECT_RE = re.compile(r"\b[A-Z][A-Z0-9_.-]{2,}\b[^.!?]{0,90}\b(outperform(?:s|ed|ing)?|improv(?:e|es|ed|ing)?|reduc(?:e|es|ed|ing)?|achiev(?:e|es|ed)?|reach(?:es|ed)?)\b")
_NON_RESULT_SENTENCE_RE = re.compile(
    r"\b(we\s+report\s+(?:the\s+)?(?:following\s+)?(?:\w+\s+){0,4}metrics?|"
    r"metrics?\s+(?:are|include|consist|measure)|we\s+(?:log|define|use|introduce|propose|present|describe)\b|"
    r"(?:is|are)\s+defined\s+as|selection\s+criterion|evaluation\s+protocol|"
    r"(?:is|are)\s+considered\s+(?:successful|failed)|used\s+to\s+evaluate\s+whether|"
    r"\bin\s+each\s+trial\b|\bevaluate\s+whether\b|\bdesigned\s+to\s+test\b|\bwe\s+adopt\s+the\s+official\s+evaluation\b|"
    r"(?:three|four|five|six|seven|eight)\s+gates?|recent\s+work|prior\s+work|previous\s+work)\b",
    flags=re.I,
)


class _ArxivFullTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.current_section = ""
        self._capture: str | None = None
        self._buffer: list[str] = []
        self.paragraphs: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        low = tag.lower()
        if self._capture is None and low in {"h1", "h2", "h3", "h4", "p"}:
            self._capture = low
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        low = tag.lower()
        if self._capture != low:
            return
        text = " ".join("".join(self._buffer).split())
        if low in {"h1", "h2", "h3", "h4"}:
            if text:
                self.current_section = text
        elif low == "p" and text:
            self.paragraphs.append((self.current_section, text))
        self._capture = None
        self._buffer = []


def extract_empirical_fact_candidates(page: str, *, max_facts: int = 4) -> list[dict[str, str]]:
    parser = _ArxivFullTextParser()
    try:
        parser.feed(page)
    except Exception:
        return []
    ranked: list[tuple[int, int, dict[str, str]]] = []
    seen: set[str] = set()
    order = 0
    for section, paragraph in parser.paragraphs:
        section_low = section.lower()
        if not any(term in section_low for term in _FULLTEXT_SECTION_TERMS):
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
            sentence = " ".join(sentence.split()).strip()
            if len(sentence) < 60 or len(sentence) > 520 or _NON_RESULT_SENTENCE_RE.search(sentence):
                continue
            strong_observation = bool(_STRONG_EMPIRICAL_CUE_RE.search(sentence))
            directional = bool(_DIRECTIONAL_RESULT_RE.search(sentence))
            numeric = bool(_NUMERIC_RESULT_RE.search(sentence))
            quantitative_directional = directional and numeric
            quantitative_comparison = numeric and bool(_NUMERIC_COMPARISON_RE.search(sentence))
            owned_directional = directional and bool(_OWN_RESULT_SUBJECT_RE.search(sentence))
            named_directional = directional and bool(_NAMED_RESULT_SUBJECT_RE.search(sentence))
            result_section_directional = directional and any(term in section_low for term in ("result", "experiment", "evaluation", "ablation", "analysis"))
            if not (strong_observation or quantitative_directional or quantitative_comparison or owned_directional or named_directional or result_section_directional):
                continue
            normalized = re.sub(r"\W+", " ", sentence.lower()).strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            if strong_observation:
                evidence_tier = "strong-observation"
            elif quantitative_directional or quantitative_comparison:
                evidence_tier = "quantitative-directional"
            elif owned_directional or named_directional:
                evidence_tier = "owned-directional"
            else:
                evidence_tier = "result-section-directional"
            score = 5 if strong_observation else (4 if quantitative_directional or quantitative_comparison else 3)
            if owned_directional or named_directional:
                score += 1
            if any(term in section_low for term in ("result", "experiment", "evaluation", "ablation")):
                score += 1
            ranked.append((score, -order, {
                "section": section or "unnamed",
                "text": sentence,
                "text_sha256": hashlib.sha256(sentence.encode("utf-8")).hexdigest(),
                "evidence_tier": evidence_tier,
            }))
            order += 1
    ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return [row[2] for row in ranked[: max(0, max_facts)]]


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


def _paper_lane_keys(paper: dict[str, Any]) -> tuple[str, ...]:
    haystack = f"{paper.get('title','')} {paper.get('abstract','')}".lower()
    return tuple(
        str(lane["key"])
        for lane in PRIMARY_EVIDENCE_LANES
        if any(str(term).lower() in haystack for term in lane["terms"])
    )


def _lane_counts(papers: list[dict[str, Any]]) -> dict[str, int]:
    counts = {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_LANES}
    for paper in papers:
        for key in _paper_lane_keys(paper):
            counts[key] += 1
    return counts


def select_primary_candidates(
    corpus: dict[str, Any],
    *,
    max_papers: int = DEFAULT_MAX_PAPERS,
    now: datetime | None = None,
    max_publication_age_days: float = DEFAULT_MAX_PUBLICATION_AGE_DAYS,
    lane_floor: int = DEFAULT_LANE_FLOOR,
) -> list[dict[str, Any]]:
    ranked: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    seen: set[str] = set()
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
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
        publication_age = _age_days(publication_date, current)
        if publication_age is None or publication_age > max_publication_age_days:
            continue
        year = int(paper.get("year") or 0)
        citation_count = int(metadata.get("citationCount") or 0)
        retrieval_score = float(metadata.get("retrievalScore") or 0.0)
        rank_key = (publication_date, year, score, retrieval_score, citation_count, str(paper.get("title") or ""))
        ranked.append((rank_key, paper))
    ranked.sort(key=lambda item: item[0], reverse=True)
    limit = max(0, int(max_papers))
    if limit == 0:
        return []
    if lane_floor <= 0 or not ranked:
        return [paper for _, paper in ranked[:limit]]

    # Coverage is a deterministic membership floor only. Each lane receives the
    # highest globally-ranked eligible paper when one exists; the remaining
    # budget is filled in the original global order. One paper may satisfy more
    # than one lane, and lanes with no eligible papers are never synthesized.
    selected_ids: set[str] = set()
    selected: list[dict[str, Any]] = []
    lane_counts = {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_LANES}
    for lane in PRIMARY_EVIDENCE_LANES:
        key = str(lane["key"])
        while lane_counts[key] < int(lane_floor) and len(selected) < limit:
            candidate = next(
                (
                    paper
                    for _, paper in ranked
                    if key in _paper_lane_keys(paper) and _arxiv_id(paper) not in selected_ids
                ),
                None,
            )
            if candidate is None:
                break
            selected.append(candidate)
            selected_ids.add(_arxiv_id(candidate))
            for covered in _paper_lane_keys(candidate):
                lane_counts[covered] += 1
    for _, paper in ranked:
        if len(selected) >= limit:
            break
        arxiv_id = _arxiv_id(paper)
        if arxiv_id in selected_ids:
            continue
        selected.append(paper)
        selected_ids.add(arxiv_id)
    selected_rank = {_arxiv_id(paper): index for index, (_, paper) in enumerate(ranked)}
    selected.sort(key=lambda paper: selected_rank.get(_arxiv_id(paper), 10**9))
    return selected


def _default_requester(url: str, *, timeout: float, headers: dict[str, str]):
    """Fetch a primary page with both socket and whole-response bounds.

    `requests` scalar timeouts are inactivity bounds, not wall-clock bounds: a
    server that trickles bytes can keep a response alive indefinitely. Primary
    evidence refresh is a scheduled control path, so bound total wall time and
    response size while still returning the small response interface used by
    the pipeline and test fakes.
    """
    total_timeout = max(float(timeout), 1.0)
    connect_timeout = min(5.0, total_timeout)
    read_timeout = min(8.0, total_timeout)
    deadline = time.monotonic() + total_timeout
    response = requests.get(
        url,
        timeout=(connect_timeout, read_timeout),
        headers=headers,
        stream=True,
    )
    with response:
        status_code = int(response.status_code)
        if status_code >= 400:
            return SimpleNamespace(status_code=status_code, text="")
        chunks: list[bytes] = []
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            total_bytes += len(chunk)
            if total_bytes > DEFAULT_MAX_PRIMARY_RESPONSE_BYTES:
                raise RuntimeError(f"primary-response-too-large:{total_bytes}")
            chunks.append(chunk)
            if time.monotonic() > deadline:
                raise requests.Timeout(f"primary-response-wall-clock-timeout:{total_timeout:.1f}s")
        body = b"".join(chunks)
        encoding = response.encoding or "utf-8"
        return SimpleNamespace(status_code=status_code, text=body.decode(encoding, errors="replace"))


def _default_arxiv_search_requester(*, query: str, max_results: int, timeout: float, headers: dict[str, str]):
    return requests.get(
        "https://export.arxiv.org/api/query",
        params={"search_query": query, "start": 0, "max_results": max_results, "sortBy": "submittedDate", "sortOrder": "descending"},
        timeout=timeout,
        headers=headers,
    )


def parse_arxiv_atom(text: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    rows: list[dict[str, Any]] = []
    for entry in root.findall("a:entry", ns):
        raw_id = str(entry.findtext("a:id", default="", namespaces=ns) or "")
        arxiv_id = raw_id.rsplit("/", 1)[-1].split("v", 1)[0].strip()
        title = " ".join(str(entry.findtext("a:title", default="", namespaces=ns) or "").split())
        abstract = " ".join(str(entry.findtext("a:summary", default="", namespaces=ns) or "").split())
        published = str(entry.findtext("a:published", default="", namespaces=ns) or "")
        if not arxiv_id or not title or not abstract:
            continue
        year = None
        try:
            year = int(published[:4]) if len(published) >= 4 else None
        except ValueError:
            year = None
        rows.append({
            "paper_id": f"arxiv:{arxiv_id}", "title": title, "year": year, "venue": "arXiv",
            "abstract": abstract, "url": f"https://arxiv.org/abs/{arxiv_id}",
            "metadata": {"externalIds": {"ArXiv": arxiv_id}, "publicationDate": published[:10], "citationCount": 0, "retrievalScore": 0.0, "retrievedAt": _now(), "matches": [{"route": "arxiv-fallback"}]},
        })
    return rows


def discover_arxiv_fallback(
    *,
    queries: tuple[str, ...] = DEFAULT_ARXIV_QUERIES,
    per_query: int = DEFAULT_ARXIV_PER_QUERY,
    requester: Callable[..., Any] | None = None,
    min_interval_seconds: float = DEFAULT_ARXIV_QUERY_INTERVAL_SECONDS,
) -> tuple[list[dict[str, Any]], list[str]]:
    fetch = requester or _default_arxiv_search_requester
    merged: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    last_started: float | None = None
    for query in queries:
        if last_started is not None and min_interval_seconds > 0:
            wait = min_interval_seconds - (time.monotonic() - last_started)
            if wait > 0:
                time.sleep(wait)
        last_started = time.monotonic()
        try:
            response = fetch(query=query, max_results=per_query, timeout=30.0, headers={"User-Agent": "Agent-Self-Evolution-Observatory/arxiv-fallback"})
            status = int(getattr(response, "status_code", 200))
            if status >= 400:
                raise RuntimeError(f"HTTP {status}")
            for row in parse_arxiv_atom(str(getattr(response, "text", "") or "")):
                arxiv_id = _arxiv_id(row)
                if arxiv_id and _relevance_score(row) >= 2:
                    merged.setdefault(arxiv_id, row)
        except Exception as error:
            errors.append(f"{query}:{type(error).__name__}:{str(error)[:160]}")
    rows = list(merged.values())
    rows.sort(key=lambda row: (str((row.get("metadata") or {}).get("publicationDate") or ""), _relevance_score(row), str(row.get("title") or "")), reverse=True)
    return rows, errors


def _augment_discovery_corpus(corpus: dict[str, Any], augmentation: list[dict[str, Any]]) -> tuple[dict[str, Any], int]:
    merged: dict[str, dict[str, Any]] = {}
    passthrough: list[dict[str, Any]] = []
    for paper in corpus.get("papers") or []:
        if not isinstance(paper, dict):
            continue
        arxiv_id = _arxiv_id(paper)
        if arxiv_id:
            merged.setdefault(arxiv_id, paper)
        else:
            passthrough.append(paper)
    added = 0
    for paper in augmentation:
        if not isinstance(paper, dict):
            continue
        arxiv_id = _arxiv_id(paper)
        if not arxiv_id or arxiv_id in merged:
            continue
        merged[arxiv_id] = paper
        added += 1
    return {"papers": [*merged.values(), *passthrough]}, added


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


def _reusable_verified_record(
    record: dict[str, Any],
    paper: dict[str, Any],
    *,
    now: datetime,
    max_age_hours: float,
) -> bool:
    if record.get("primary_source_verified") is not True or max_age_hours <= 0:
        return False
    # Raw primary/fulltext bytes may be reused across extractor upgrades, but
    # derived empirical facts may not. A version mismatch deliberately falls
    # through to the content-addressed caches so facts are re-derived by the
    # current extractor without an unnecessary network fetch.
    if str(record.get("empirical_fact_extraction_version") or "") != EMPIRICAL_FACT_EXTRACTION_VERSION:
        return False
    age = _age_hours(str(record.get("fetched_at") or ""), now)
    if age is None or age > max_age_hours:
        return False
    if _title_similarity(str(record.get("title") or ""), str(paper.get("title") or "")) < 0.72:
        return False
    if not str(record.get("abstract") or "").strip() or len(str(record.get("source_sha256") or "")) != 64:
        return False
    source_cache = Path(str(record.get("cache_path") or ""))
    fulltext_cache = Path(str(record.get("fulltext_cache_path") or ""))
    if not source_cache.exists():
        return False
    # Reuse only complete primary+fulltext evidence. A record whose optional
    # fulltext failed is retried so a transient provider error can still heal.
    if len(str(record.get("fulltext_sha256") or "")) != 64 or not fulltext_cache.exists():
        return False
    return True


def _recent_cache_file(path: Path, *, now: datetime, max_age_hours: float) -> bool:
    if max_age_hours <= 0 or not path.is_file():
        return False
    try:
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return False
    return max(0.0, (now - modified).total_seconds() / 3600.0) <= max_age_hours


def _cached_primary_page(
    cache_dir: Path,
    arxiv_id: str,
    paper: dict[str, Any],
    *,
    now: datetime,
    max_age_hours: float,
) -> dict[str, Any] | None:
    safe_id = re.sub(r"[^0-9A-Za-z._-]+", "_", arxiv_id)
    candidates = sorted(cache_dir.glob(f"arxiv-{safe_id}-*.html"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in candidates:
        if not _recent_cache_file(path, now=now, max_age_hours=max_age_hours):
            continue
        try:
            raw_bytes = path.read_bytes()
        except OSError:
            continue
        if not raw_bytes or len(raw_bytes) > DEFAULT_MAX_PRIMARY_RESPONSE_BYTES:
            continue
        source_sha = hashlib.sha256(raw_bytes).hexdigest()
        if not path.stem.endswith(source_sha[:12]):
            continue
        raw_text = raw_bytes.decode("utf-8", errors="replace")
        parsed = parse_arxiv_page(raw_text)
        if not parsed["title"] or not parsed["abstract"]:
            continue
        similarity = _title_similarity(str(paper.get("title") or ""), parsed["title"])
        if similarity < 0.72:
            continue
        return {
            "raw_text": raw_text,
            "parsed": parsed,
            "source_sha256": source_sha,
            "abstract_sha256": hashlib.sha256(parsed["abstract"].encode("utf-8")).hexdigest(),
            "cache_path": str(path),
            "title_similarity": round(similarity, 4),
        }
    return None


def _cached_fulltext_page(
    cache_dir: Path,
    arxiv_id: str,
    *,
    now: datetime,
    max_age_hours: float,
) -> dict[str, Any] | None:
    safe_id = re.sub(r"[^0-9A-Za-z._-]+", "_", arxiv_id)
    candidates = sorted(cache_dir.glob(f"arxiv-full-{safe_id}-*.html"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in candidates:
        if not _recent_cache_file(path, now=now, max_age_hours=max_age_hours):
            continue
        try:
            raw_bytes = path.read_bytes()
        except OSError:
            continue
        if not raw_bytes or len(raw_bytes) > DEFAULT_MAX_PRIMARY_RESPONSE_BYTES:
            continue
        source_sha = hashlib.sha256(raw_bytes).hexdigest()
        if not path.stem.endswith(source_sha[:12]):
            continue
        raw_text = raw_bytes.decode("utf-8", errors="replace")
        if "<section" not in raw_text.lower():
            continue
        return {
            "fulltext_sha256": source_sha,
            "fulltext_cache_path": str(path),
            "empirical_facts": extract_empirical_fact_candidates(raw_text, max_facts=4),
        }
    return None


def build_primary_evidence_pool(
    *,
    storage: StorageSettings | None = None,
    corpus_path: Path | None = None,
    max_papers: int = DEFAULT_MAX_PAPERS,
    lane_floor: int = DEFAULT_LANE_FLOOR,
    max_corpus_age_days: float = DEFAULT_MAX_CORPUS_AGE_DAYS,
    max_publication_age_days: float = DEFAULT_MAX_PUBLICATION_AGE_DAYS,
    requester: Callable[..., Any] | None = None,
    arxiv_search_requester: Callable[..., Any] | None = None,
    arxiv_queries: tuple[str, ...] = DEFAULT_ARXIV_QUERIES,
    arxiv_query_interval_seconds: float = DEFAULT_ARXIV_QUERY_INTERVAL_SECONDS,
    augment_fresh_corpus_with_arxiv: bool = True,
    now: datetime | None = None,
    min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
    recent_verified_cache_reuse_hours: float = DEFAULT_RECENT_VERIFIED_CACHE_REUSE_HOURS,
    recent_fulltext_failure_cooldown_hours: float = DEFAULT_RECENT_FULLTEXT_FAILURE_COOLDOWN_HOURS,
    cache_dir: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    storage = storage or StorageSettings.from_env()
    corpus_path = corpus_path or storage.corpus_dir / "semantic-scholar-corpus.json"
    corpus = load_live_corpus(corpus_path)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    private_pool_path, default_cache = _private_paths(storage)
    cache_dir = cache_dir or default_cache
    prior_pool = load_private_primary_pool(private_pool_path) or {}
    prior_records_by_ref = {
        str(row.get("ref")): row
        for row in prior_pool.get("records") or []
        if isinstance(row, dict) and row.get("ref")
    }
    prior_pool_age_hours = _age_hours(str(prior_pool.get("generated_at") or ""), current) if prior_pool else None
    prior_fulltext_failure_refs = {
        str(row.get("ref"))
        for row in prior_pool.get("fulltext_errors") or []
        if isinstance(row, dict) and row.get("ref")
    } if prior_pool_age_hours is not None and prior_pool_age_hours <= recent_fulltext_failure_cooldown_hours else set()
    public_state: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": _now(),
        "policy": {
            "semantic_scholar_is_discovery_metadata_not_primary_evidence": True,
            "verified_primary_page_required": True,
            "arxiv_source_sha_required": True,
            "stale_s2_triggers_primary_arxiv_fallback": True,
            "fresh_s2_is_augmented_by_preregistered_arxiv_lanes": bool(augment_fresh_corpus_with_arxiv),
            "arxiv_augmentation_failure_does_not_invalidate_fresh_corpus": True,
            "arxiv_fallback_is_primary_metadata_not_a_scientific_claim": True,
            "primary_publication_age_is_bounded": True,
            "maximum_publication_age_days": max_publication_age_days,
            "no_parallel_primary_fetch": True,
            "recent_verified_cache_reuse_hours": float(recent_verified_cache_reuse_hours),
            "recent_fulltext_failure_cooldown_hours": float(recent_fulltext_failure_cooldown_hours),
            "recent_cache_reuse_is_retry_optimization_not_weekly_freshness_relaxation": True,
            "fulltext_failure_cooldown_applies_only_to_optional_enrichment": True,
            "content_addressed_raw_cache_must_reverify_sha_and_parseability": True,
            "derived_empirical_facts_reused_only_when_extractor_version_matches": True,
            "full_abstracts_remain_private_data_artifacts": True,
            "fulltext_enrichment_is_optional": True,
            "fulltext_snippets_remain_private_data_artifacts": True,
            "empirical_fact_candidates_are_not_ground_truth": True,
            "empirical_fact_precision_gate": True,
            "empirical_fact_extraction_version": EMPIRICAL_FACT_EXTRACTION_VERSION,
            "empirical_fact_evidence_tiers": ["strong-observation", "quantitative-directional", "owned-directional", "result-section-directional"],
            "pre_registered_lane_coverage_floor": True,
            "lane_coverage_is_discovery_breadth_not_scientific_authority": True,
            "lane_floor": int(lane_floor),
            "candidate_generation_authority": False,
            "method_authority": False,
            "experiment_authority": False,
            "p0_authority": False,
        },
        "summary": {
            "corpus_available": bool(corpus),
            "corpus_fresh": False,
            "discovery_mode": "none",
            "augmentation_discovered": 0,
            "augmentation_added": 0,
            "selected": 0,
            "verified": 0,
            "fetch_errors": 0,
            "title_mismatches": 0,
            "fulltext_verified": 0,
            "fulltext_fetch_errors": 0,
            "empirical_fact_candidates": 0,
            "empirical_fact_tier_counts": {},
            "recent_verified_cache_reused": 0,
            "recent_raw_primary_cache_reused": 0,
            "recent_raw_fulltext_cache_reused": 0,
            "recent_fulltext_failure_cooldown_skips": 0,
            "lane_floor": int(lane_floor),
            "eligible_lane_counts": {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_LANES},
            "selected_lane_counts": {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_LANES},
            "verified_lane_counts": {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_LANES},
            "undercovered_lanes": [],
            "verified_undercovered_lanes": [],
            "candidate_generation_ready": False,
        },
        "records": [],
        "errors": [],
        "discovery_errors": [],
    }
    private: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": public_state["generated_at"],
        "corpus_path": str(corpus_path),
        "empirical_fact_extraction_version": EMPIRICAL_FACT_EXTRACTION_VERSION,
        "records": [],
        "errors": [],
        "fulltext_errors": [],
        "discovery_errors": [],
    }
    retrieved_at = str((corpus or {}).get("retrieved_at") or "")
    corpus_age = _age_days(retrieved_at, current) if corpus else None
    fresh = bool(corpus) and corpus_age is not None and corpus_age <= max_corpus_age_days
    public_state["corpus_retrieved_at"] = retrieved_at
    public_state["corpus_age_days"] = corpus_age
    public_state["summary"]["corpus_fresh"] = fresh
    private["corpus_retrieved_at"] = retrieved_at
    discovery_errors: list[str] = []
    if fresh:
        discovery_corpus = corpus or {"papers": []}
        if augment_fresh_corpus_with_arxiv:
            augmentation_rows, discovery_errors = discover_arxiv_fallback(
                queries=arxiv_queries,
                requester=arxiv_search_requester,
                min_interval_seconds=arxiv_query_interval_seconds,
            )
            discovery_corpus, augmentation_added = _augment_discovery_corpus(discovery_corpus, augmentation_rows)
            public_state["summary"].update({
                "discovery_mode": "semantic-scholar-plus-arxiv-augmentation",
                "augmentation_discovered": len(augmentation_rows),
                "augmentation_added": augmentation_added,
            })
            private["discovery_mode"] = "semantic-scholar-plus-arxiv-augmentation"
            private["augmentation"] = {"discovered": len(augmentation_rows), "added": augmentation_added}
            public_state["discovery_errors"] = discovery_errors
            private["discovery_errors"] = discovery_errors
        else:
            public_state["summary"]["discovery_mode"] = "semantic-scholar-corpus"
            private["discovery_mode"] = "semantic-scholar-corpus"
    else:
        fallback_rows, discovery_errors = discover_arxiv_fallback(
            queries=arxiv_queries,
            requester=arxiv_search_requester,
            min_interval_seconds=arxiv_query_interval_seconds,
        )
        discovery_corpus = {"papers": fallback_rows}
        public_state["summary"]["discovery_mode"] = "arxiv-primary-fallback"
        private["discovery_mode"] = "arxiv-primary-fallback"
        public_state["discovery_errors"] = discovery_errors
        private["discovery_errors"] = discovery_errors

    eligible_candidates = select_primary_candidates(
        discovery_corpus,
        max_papers=len(discovery_corpus.get("papers") or []),
        now=current,
        max_publication_age_days=max_publication_age_days,
        lane_floor=0,
    )
    candidates = select_primary_candidates(
        discovery_corpus,
        max_papers=max_papers,
        now=current,
        max_publication_age_days=max_publication_age_days,
        lane_floor=lane_floor,
    )
    eligible_lane_counts = _lane_counts(eligible_candidates)
    selected_lane_counts = _lane_counts(candidates)
    undercovered_lanes = [
        key for key, eligible_count in eligible_lane_counts.items()
        if eligible_count > 0 and selected_lane_counts.get(key, 0) < min(int(lane_floor), eligible_count)
    ]
    public_state["summary"].update({
        "selected": len(candidates),
        "lane_floor": int(lane_floor),
        "eligible_lane_counts": eligible_lane_counts,
        "selected_lane_counts": selected_lane_counts,
        "undercovered_lanes": undercovered_lanes,
    })
    private["lane_coverage"] = {
        "lane_floor": int(lane_floor),
        "eligible_lane_counts": eligible_lane_counts,
        "selected_lane_counts": selected_lane_counts,
        "undercovered_lanes": undercovered_lanes,
    }
    candidate_lane_by_ref = {f"arXiv:{_arxiv_id(paper)}": _paper_lane_keys(paper) for paper in candidates}
    fetch = requester or _default_requester
    cache_dir.mkdir(parents=True, exist_ok=True)
    last_fetch_started: float | None = None
    verified: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    fulltext_errors: list[dict[str, Any]] = []
    title_mismatches = 0
    fulltext_verified = 0
    empirical_fact_count = 0
    reused_verified = 0
    raw_primary_cache_reused = 0
    raw_fulltext_cache_reused = 0
    fulltext_failure_cooldown_skips = 0
    for paper in candidates:
        arxiv_id = _arxiv_id(paper)
        ref = f"arXiv:{arxiv_id}"
        url = f"https://arxiv.org/abs/{arxiv_id}"
        cached = prior_records_by_ref.get(ref) or {}
        if _reusable_verified_record(
            cached,
            paper,
            now=current,
            max_age_hours=recent_verified_cache_reuse_hours,
        ):
            record = dict(cached)
            record.update({
                "year": paper.get("year"),
                "publication_date": (paper.get("metadata") or {}).get("publicationDate"),
                "s2_paper_id": paper.get("paper_id"),
                "s2_retrieved_at": (paper.get("metadata") or {}).get("retrievedAt"),
                "lane_keys": list(candidate_lane_by_ref.get(ref, ())),
            })
            verified.append(record)
            fulltext_verified += 1
            empirical_fact_count += len(record.get("empirical_facts") or [])
            reused_verified += 1
            continue
        try:
            cached_primary = _cached_primary_page(
                cache_dir,
                arxiv_id,
                paper,
                now=current,
                max_age_hours=recent_verified_cache_reuse_hours,
            )
            if cached_primary:
                parsed = cached_primary["parsed"]
                source_sha = str(cached_primary["source_sha256"])
                abstract_sha = str(cached_primary["abstract_sha256"])
                cache_path = Path(str(cached_primary["cache_path"]))
                similarity = float(cached_primary["title_similarity"])
                raw_primary_cache_reused += 1
            else:
                if last_fetch_started is not None and min_interval_seconds > 0:
                    wait = min_interval_seconds - (time.monotonic() - last_fetch_started)
                    if wait > 0:
                        time.sleep(wait)
                last_fetch_started = time.monotonic()
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
                    errors.append({"ref": ref, "error": "title-mismatch", "similarity": round(similarity, 4)})
                    continue
                raw_bytes = raw_text.encode("utf-8")
                source_sha = hashlib.sha256(raw_bytes).hexdigest()
                abstract_sha = hashlib.sha256(parsed["abstract"].encode("utf-8")).hexdigest()
                cache_path = cache_dir / f"arxiv-{re.sub(r'[^0-9A-Za-z._-]+','_',arxiv_id)}-{source_sha[:12]}.html"
                cache_path.write_bytes(raw_bytes)

            fulltext_url = f"https://arxiv.org/html/{arxiv_id}"
            fulltext_sha = ""
            fulltext_cache_path = ""
            empirical_facts: list[dict[str, str]] = []
            cached_fulltext = _cached_fulltext_page(
                cache_dir,
                arxiv_id,
                now=current,
                max_age_hours=recent_verified_cache_reuse_hours,
            )
            if cached_fulltext:
                fulltext_sha = str(cached_fulltext["fulltext_sha256"])
                fulltext_cache_path = str(cached_fulltext["fulltext_cache_path"])
                empirical_facts = list(cached_fulltext.get("empirical_facts") or [])
                fulltext_verified += 1
                empirical_fact_count += len(empirical_facts)
                raw_fulltext_cache_reused += 1
            elif ref in prior_fulltext_failure_refs:
                fulltext_errors.append({"ref": ref, "error": "recent-fulltext-failure-cooldown"})
                fulltext_failure_cooldown_skips += 1
            else:
                try:
                    if last_fetch_started is not None and min_interval_seconds > 0:
                        wait = min_interval_seconds - (time.monotonic() - last_fetch_started)
                        if wait > 0:
                            time.sleep(wait)
                    last_fetch_started = time.monotonic()
                    full_response = fetch(
                        fulltext_url,
                        timeout=25.0,
                        headers={"User-Agent": "Agent-Self-Evolution-Observatory/fulltext-evidence"},
                    )
                    full_status = int(getattr(full_response, "status_code", 200))
                    if full_status >= 400:
                        raise RuntimeError(f"HTTP {full_status}")
                    full_text = str(getattr(full_response, "text", "") or "")
                    if not full_text or "<section" not in full_text.lower():
                        raise RuntimeError("fulltext-page-missing-sections")
                    full_bytes = full_text.encode("utf-8")
                    fulltext_sha = hashlib.sha256(full_bytes).hexdigest()
                    full_path = cache_dir / f"arxiv-full-{re.sub(r'[^0-9A-Za-z._-]+','_',arxiv_id)}-{fulltext_sha[:12]}.html"
                    full_path.write_bytes(full_bytes)
                    fulltext_cache_path = str(full_path)
                    empirical_facts = extract_empirical_fact_candidates(full_text, max_facts=4)
                    fulltext_verified += 1
                    empirical_fact_count += len(empirical_facts)
                except Exception as full_error:
                    fulltext_errors.append({
                        "ref": ref,
                        "error": f"{type(full_error).__name__}:{str(full_error)[:240]}",
                    })

            record = {
                "evidence_id": hashlib.sha256(f"arXiv:{arxiv_id}:{source_sha}".encode("utf-8")).hexdigest(),
                "ref": f"arXiv:{arxiv_id}",
                "title": parsed["title"],
                "primary_url": url,
                "source_sha256": source_sha,
                "abstract_sha256": abstract_sha,
                "abstract": parsed["abstract"],
                "fulltext_url": fulltext_url,
                "fulltext_sha256": fulltext_sha,
                "fulltext_cache_path": fulltext_cache_path,
                "empirical_facts": empirical_facts,
                "year": paper.get("year"),
                "publication_date": (paper.get("metadata") or {}).get("publicationDate"),
                "s2_paper_id": paper.get("paper_id"),
                "s2_retrieved_at": (paper.get("metadata") or {}).get("retrievedAt"),
                "fetched_at": _now(),
                "cache_path": str(cache_path),
                "title_similarity": round(similarity, 4),
                "primary_source_verified": True,
                "empirical_fact_extraction_version": EMPIRICAL_FACT_EXTRACTION_VERSION,
                "lane_keys": list(candidate_lane_by_ref.get(f"arXiv:{arxiv_id}", ())),
            }
            verified.append(record)
        except Exception as error:  # network/provider failures are evidence absence, not scientific negatives
            errors.append({"ref": f"arXiv:{arxiv_id}", "error": f"{type(error).__name__}:{str(error)[:240]}"})

    verified_lane_counts = {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_LANES}
    empirical_fact_tier_counts: dict[str, int] = {}
    for record in verified:
        for key in record.get("lane_keys") or []:
            if key in verified_lane_counts:
                verified_lane_counts[key] += 1
        for fact in record.get("empirical_facts") or []:
            if not isinstance(fact, dict):
                continue
            tier = str(fact.get("evidence_tier") or "untyped")
            empirical_fact_tier_counts[tier] = empirical_fact_tier_counts.get(tier, 0) + 1
    verified_undercovered_lanes = [
        key for key, eligible_count in eligible_lane_counts.items()
        if eligible_count > 0 and verified_lane_counts.get(key, 0) < min(int(lane_floor), eligible_count)
    ]
    private["records"] = verified
    private["errors"] = errors
    private["fulltext_errors"] = fulltext_errors
    private["lane_coverage"]["verified_lane_counts"] = verified_lane_counts
    private["lane_coverage"]["verified_undercovered_lanes"] = verified_undercovered_lanes
    private["status"] = "READY" if len(verified) >= 4 else "INSUFFICIENT_PRIMARY_EVIDENCE"
    public_state["summary"].update(
        {
            "verified": len(verified),
            "fetch_errors": sum(1 for row in errors if row.get("error") != "title-mismatch"),
            "title_mismatches": title_mismatches,
            "fulltext_verified": fulltext_verified,
            "fulltext_fetch_errors": len(fulltext_errors),
            "empirical_fact_candidates": empirical_fact_count,
            "empirical_fact_tier_counts": empirical_fact_tier_counts,
            "recent_verified_cache_reused": reused_verified,
            "recent_raw_primary_cache_reused": raw_primary_cache_reused,
            "recent_raw_fulltext_cache_reused": raw_fulltext_cache_reused,
            "recent_fulltext_failure_cooldown_skips": fulltext_failure_cooldown_skips,
            "verified_lane_counts": verified_lane_counts,
            "verified_undercovered_lanes": verified_undercovered_lanes,
            "candidate_generation_ready": len(verified) >= 4,
        }
    )
    public_state["records"] = [
        {
            **{key: row[key] for key in ("evidence_id", "ref", "title", "primary_url", "source_sha256", "abstract_sha256", "year", "publication_date", "fetched_at")},
            "fulltext_sha256": str(row.get("fulltext_sha256") or ""),
            "empirical_fact_count": len(row.get("empirical_facts") or []),
        }
        for row in verified
    ]
    public_state["errors"] = errors
    public_state["fulltext_errors"] = fulltext_errors
    public_state["status"] = private["status"]
    return public_state, private


def load_primary_evidence_state(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version":"1.0","status":"NOT_RUN","policy":{"candidate_generation_authority":False,"method_authority":False,"experiment_authority":False,"p0_authority":False},
            "summary":{"corpus_available":False,"corpus_fresh":False,"selected":0,"verified":0,"fetch_errors":0,"title_mismatches":0,"fulltext_verified":0,"fulltext_fetch_errors":0,"empirical_fact_candidates":0,"empirical_fact_tier_counts":{},"candidate_generation_ready":False},"records":[],"errors":[],
        }
    try:
        payload=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return {"schema_version":"1.0","status":"STATE_UNREADABLE","policy":{"candidate_generation_authority":False,"method_authority":False,"experiment_authority":False,"p0_authority":False},"summary":{"corpus_available":False,"corpus_fresh":False,"selected":0,"verified":0,"fetch_errors":1,"title_mismatches":0,"fulltext_verified":0,"fulltext_fetch_errors":0,"empirical_fact_candidates":0,"empirical_fact_tier_counts":{},"candidate_generation_ready":False},"records":[],"errors":["state-unreadable"]}
    return payload if isinstance(payload,dict) else {"schema_version":"1.0","status":"STATE_INVALID","summary":{},"records":[],"errors":["state-invalid"]}


def write_primary_evidence_pool(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
    *,
    storage: StorageSettings | None = None,
    corpus_path: Path | None = None,
    max_papers: int = DEFAULT_MAX_PAPERS,
    lane_floor: int = DEFAULT_LANE_FLOOR,
    max_corpus_age_days: float = DEFAULT_MAX_CORPUS_AGE_DAYS,
    max_publication_age_days: float = DEFAULT_MAX_PUBLICATION_AGE_DAYS,
    requester: Callable[..., Any] | None = None,
    arxiv_search_requester: Callable[..., Any] | None = None,
    arxiv_queries: tuple[str, ...] = DEFAULT_ARXIV_QUERIES,
    arxiv_query_interval_seconds: float = DEFAULT_ARXIV_QUERY_INTERVAL_SECONDS,
    augment_fresh_corpus_with_arxiv: bool = True,
    now: datetime | None = None,
    min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
    recent_verified_cache_reuse_hours: float = DEFAULT_RECENT_VERIFIED_CACHE_REUSE_HOURS,
    recent_fulltext_failure_cooldown_hours: float = DEFAULT_RECENT_FULLTEXT_FAILURE_COOLDOWN_HOURS,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    state, private = build_primary_evidence_pool(
        storage=storage,
        corpus_path=corpus_path,
        max_papers=max_papers,
        lane_floor=lane_floor,
        max_corpus_age_days=max_corpus_age_days,
        max_publication_age_days=max_publication_age_days,
        requester=requester,
        arxiv_search_requester=arxiv_search_requester,
        arxiv_queries=arxiv_queries,
        arxiv_query_interval_seconds=arxiv_query_interval_seconds,
        augment_fresh_corpus_with_arxiv=augment_fresh_corpus_with_arxiv,
        now=now,
        min_interval_seconds=min_interval_seconds,
        recent_verified_cache_reuse_hours=recent_verified_cache_reuse_hours,
        recent_fulltext_failure_cooldown_hours=recent_fulltext_failure_cooldown_hours,
    )
    private_pool_path, _ = _private_paths(storage)
    private_pool_path.parent.mkdir(parents=True, exist_ok=True)
    private_pool_path.write_text(json.dumps(private, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    public_state = redact_private_paths(state, storage=storage)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(public_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PRIMARY_EVIDENCE = " + json.dumps(public_state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_primary_evidence_pool(), ensure_ascii=False))
