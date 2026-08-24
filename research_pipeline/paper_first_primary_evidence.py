from __future__ import annotations

import hashlib
import html
import inspect
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
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
DEFAULT_PORTABLE_REVIEW_STATE = PROJECT_ROOT / "generated" / "paper-first-problem-generator-state.json"
DEFAULT_PORTABLE_SOURCE_REVIEW_STATE = PROJECT_ROOT / "generated" / "paper-first-source-review-receipts.json"
DEFAULT_MAX_PAPERS = 32
DEFAULT_LANE_FLOOR = 1
DEFAULT_SOURCE_COVERAGE_ANCHOR_COUNT = 16
DEFAULT_NO_LANE_CARRIER_PROBE_LIMIT = 3
DEFAULT_CARRIER_PROBE_RECEIPT_MAX_AGE_DAYS = 7.0
CARRIER_PROBE_RECEIPT_LIMIT = 64
PRIMARY_EVIDENCE_OBJECT_LANES: tuple[dict[str, Any], ...] = (
    {"key":"skill_harness","terms":("skill","harness","workflow evolution","agent workflow")},
    {"key":"memory_continual","terms":("agent memory","memory","continual agent","lifelong agent","experience management")},
    {"key":"world_model","terms":("world model","world-model","world modeling","world modelling","world action model")},
    {"key":"parametric_model_state","terms":("model weights","model parameters","lora parameters","policy weights","policy weight","parameter update","weight update","post-train","post-training","on-policy distillation","self-distillation"),"exclude_terms":("without weight updates","does not update model weights","without changing a single model weight","what is updated is not model weights","model weights remain fixed","without parameter updates")},
)
PRIMARY_EVIDENCE_CONTEXT_TAGS: tuple[dict[str, Any], ...] = (
    {"key":"embodied","terms":("embodied","robot","robotic","navigation","physical autonomy")},
    {"key":"collective","terms":("multi-agent","multi agent","collaborative harness","collaborative agent","swarm","group-evolving","group evolving","agent society")},
    {"key":"autonomous_science","terms":("symbolic regression","scientific discovery","scientific agent","research agent","ai scientist","autonomous research","hypothesis generation","experiment planning")},
    {"key":"runtime_deployment","terms":("runtime","deployment","production agent","customer support","long-horizon agent","monitoring","runtime contract")},
)
PRIMARY_EVIDENCE_PROPERTY_TAGS: tuple[dict[str, Any], ...] = (
    {"key":"safety_reliability","terms":("agent safety","safety harness","reliability","robustness","adversarial","security","failure")},
)
PRIMARY_EVIDENCE_LANES = PRIMARY_EVIDENCE_OBJECT_LANES + PRIMARY_EVIDENCE_CONTEXT_TAGS + PRIMARY_EVIDENCE_PROPERTY_TAGS
DEFAULT_MAX_CORPUS_AGE_DAYS = 10.0
DEFAULT_MAX_PUBLICATION_AGE_DAYS = 60.0
DEFAULT_MIN_INTERVAL_SECONDS = 0.75
DEFAULT_RECENT_VERIFIED_CACHE_REUSE_HOURS = 12.0
DEFAULT_RECENT_FULLTEXT_FAILURE_COOLDOWN_HOURS = 2.0
DEFAULT_MAX_PRIMARY_RESPONSE_BYTES = 24 * 1024 * 1024
DEFAULT_ARXIV_QUERY_INTERVAL_SECONDS = 3.1
DEFAULT_ARXIV_PER_QUERY = 48
DEFAULT_ARXIV_MAX_PAGES = 4
DEFAULT_ARXIV_RATE_LIMIT_COOLDOWN_SECONDS = 1800
DEFAULT_ARXIV_RATE_LIMIT_MAX_COOLDOWN_SECONDS = 21600
EMPIRICAL_FACT_EXTRACTION_VERSION = "precision-v2"
TYPED_EVIDENCE_EXTRACTION_VERSION = "typed-v3"
SUPPORTED_TYPED_EVIDENCE_SNAPSHOT_VERSIONS = ("typed-v2", TYPED_EVIDENCE_EXTRACTION_VERSION)
DEFAULT_ARXIV_QUERIES = (
    'all:"self-evolving" AND all:agent',
    'all:"self-improving" AND all:agent',
    'all:"agent evolution" AND all:LLM',
    '(all:"agent skill" OR all:harness) AND all:evolution',
    '(all:"agent memory" OR all:"continual agent") AND (all:evolution OR all:"self-improving")',
    'all:"world model" AND all:agent AND (all:evolution OR all:"self-improving" OR all:"continual")',
    '(all:"post-training" OR all:"post-train" OR all:"weight update" OR all:"parameter update") AND all:agent',
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


_ASSUMPTION_SECTION_TERMS = ("assumption", "method", "setup", "system", "problem", "formulation", "framework", "approach", "algorithm", "protocol")
_MEASURED_SECTION_TERMS = ("result", "experiment", "evaluation", "analysis", "ablation", "discussion", "finding", "failure", "safety", "robust")
_FIRST_PARTY_RESULT_SECTION_TERMS = ("result", "experiment", "evaluation", "analysis", "ablation")
_ASSUMPTION_CUE_RE = re.compile(r"\b(we assume|assume that|assumes that|under the assumption|we require|requires that|we fix|is fixed|we restrict|we consider only|for simplicity,? we (?:assume|consider|restrict)|we hold .{0,40} constant|given a fixed)\b", flags=re.I)
_FAILURE_CUE_RE = re.compile(r"\b(fail(?:s|ed|ure|ures)?|degrad(?:e|es|ed|ation)|drop(?:s|ped)?|harm(?:s|ed|ful)?|worse than|underperform(?:s|ed)?|error rate|attack success rate|cannot|unable to)\b", flags=re.I)
_BOUNDARY_CUE_RE = re.compile(r"\b(only when|only if|threshold|regime|above|below|with increasing|with decreasing|gap between|saturat(?:e|es|ed|ion)|plateau|cross-over|crossover)\b", flags=re.I)
_TYPED_NUMERIC_CUE_RE = re.compile(r"\b\d+(?:\.\d+)?\s*%|\b\d+\.\d+\b|\b\d+\s*/\s*\d+\b")
_FIRST_PARTY_TYPED_EVIDENCE_RE = re.compile(
    r"\b(?:we\s+(?:find|found|observe|observed|show|demonstrate|report|measure|evaluate|test)|"
    r"our\s+(?:results?|experiments?|evaluation|analysis|measurements?|method|approach|system|agent|model|framework)|"
    r"in\s+our\s+(?:experiments?|evaluation|study|setting)|"
    r"results?\s+(?:show|shows|indicate|indicates|demonstrate|demonstrates|reveal|reveals)|"
    r"(?:table|figure)\s+\d+[a-z]?\s+(?:shows|demonstrates|summarizes|establishes))\b",
    flags=re.I,
)
_LITERATURE_ATTRIBUTION_RE = re.compile(
    r"\b(?:prior|previous|earlier|existing|recent)\s+(?:work|studies|research)\b|"
    r"\b(?:prior|previous|existing)\s+(?:benchmarks?|systems?|methods?)\b|"
    r"\b(?:benchmarks?|systems?|methods?)\b[^.!?]{0,180}\b(?:reveal(?:s|ed|ing)?|show(?:s|ed|ing)?|"
    r"demonstrat(?:e|es|ed|ing)|report(?:s|ed|ing)|find(?:s|ings)?|emphasiz(?:e|es|ed|ing)|"
    r"highlight(?:s|ed|ing)|study(?:ies|ied|ing))\b",
    flags=re.I,
)
_CITATION_LED_ATTRIBUTION_RE = re.compile(
    r"^\s*(?:\(\s*\d+(?:\s*[,;]\s*\d+)*\s*\)|\[\s*\d+(?:\s*[,;]\s*\d+)*\s*\])\s*[,;:]?",
    flags=re.I,
)


def extract_typed_evidence_candidates(page: str, *, max_per_type: int = 2) -> dict[str, list[dict[str, str]]]:
    parser = _ArxivFullTextParser()
    try:
        parser.feed(page)
    except Exception:
        return {"operational_assumptions": [], "measured_failures": [], "boundary_observations": []}
    buckets: dict[str, list[tuple[int, int, dict[str, str]]]] = {
        "operational_assumptions": [],
        "measured_failures": [],
        "boundary_observations": [],
    }
    seen: dict[str, set[str]] = {key: set() for key in buckets}
    order = 0
    for section, paragraph in parser.paragraphs:
        section_low = section.lower()
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
            sentence = " ".join(sentence.split()).strip()
            if len(sentence) < 50 or len(sentence) > 600:
                continue
            normalized = re.sub(r"\W+", " ", sentence.lower()).strip()
            if not normalized:
                continue
            item = {"section": section or "unnamed", "text": sentence, "text_sha256": hashlib.sha256(sentence.encode("utf-8")).hexdigest(), "extraction_version": TYPED_EVIDENCE_EXTRACTION_VERSION}
            first_party_typed = bool(_FIRST_PARTY_TYPED_EVIDENCE_RE.search(sentence))
            literature_attributed = bool(_LITERATURE_ATTRIBUTION_RE.search(sentence) or _CITATION_LED_ATTRIBUTION_RE.search(sentence))
            first_party_result_section = any(term in section_low for term in _FIRST_PARTY_RESULT_SECTION_TERMS)
            quantitative_typed = bool(_TYPED_NUMERIC_CUE_RE.search(sentence))
            typed_empirical_eligible = (
                first_party_typed
                or (
                    first_party_result_section
                    and not literature_attributed
                    and quantitative_typed
                )
            )
            if any(term in section_low for term in _ASSUMPTION_SECTION_TERMS) and _ASSUMPTION_CUE_RE.search(sentence) and normalized not in seen["operational_assumptions"]:
                seen["operational_assumptions"].add(normalized)
                score = 3 + (2 if "assumption" in section_low else 0) + (1 if re.search(r"\bwe assume\b|\bunder the assumption\b", sentence, flags=re.I) else 0)
                buckets["operational_assumptions"].append((score, -order, item))
            measured_section = any(term in section_low for term in _MEASURED_SECTION_TERMS)
            if measured_section and typed_empirical_eligible and _FAILURE_CUE_RE.search(sentence) and (_STRONG_EMPIRICAL_CUE_RE.search(sentence) or _DIRECTIONAL_RESULT_RE.search(sentence) or _TYPED_NUMERIC_CUE_RE.search(sentence)) and normalized not in seen["measured_failures"]:
                seen["measured_failures"].add(normalized)
                score = 3 + (2 if _TYPED_NUMERIC_CUE_RE.search(sentence) else 0) + (1 if _STRONG_EMPIRICAL_CUE_RE.search(sentence) else 0)
                buckets["measured_failures"].append((score, -order, item))
            if measured_section and typed_empirical_eligible and _BOUNDARY_CUE_RE.search(sentence) and (_STRONG_EMPIRICAL_CUE_RE.search(sentence) or _DIRECTIONAL_RESULT_RE.search(sentence) or _TYPED_NUMERIC_CUE_RE.search(sentence)) and normalized not in seen["boundary_observations"]:
                seen["boundary_observations"].add(normalized)
                score = 3 + (2 if _TYPED_NUMERIC_CUE_RE.search(sentence) else 0) + (1 if _STRONG_EMPIRICAL_CUE_RE.search(sentence) else 0)
                buckets["boundary_observations"].append((score, -order, item))
            order += 1
    output: dict[str, list[dict[str, str]]] = {}
    for key, rows in buckets.items():
        rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
        output[key] = [row[2] for row in rows[: max(0, max_per_type)]]
    return output


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
    # A preregistered scientific-object match is part of relevance, but never on
    # its own: broad terms such as "post-training" or "world model" also occur
    # outside agent self-evolution.  Require an explicit agent/AI-for-AI context
    # before giving the object lane the minimum two relevance points needed by
    # the selector.  This keeps the source-coverage scheduler inside the same
    # relevance gate while allowing newly discovered lane-grounded agent work to
    # reopen a saturated search transaction as the published policy requires.
    agent_context = any(term in haystack for term in (
        "agent", "agentic", "ai-for-ai", "ai4ai", "self-improv", "self improv", "self-evol", "self evol",
    ))
    if agent_context and _paper_keys_for_registry(paper, PRIMARY_EVIDENCE_OBJECT_LANES):
        score = max(score, 2)
    return score


def _paper_keys_for_registry(paper: dict[str, Any], registry: tuple[dict[str, Any], ...]) -> tuple[str, ...]:
    haystack = f"{paper.get('title','')} {paper.get('abstract','')}".lower()
    keys=[]
    for lane in registry:
        terms=tuple(str(term).lower() for term in lane.get("terms") or ())
        exclude_terms=tuple(str(term).lower() for term in lane.get("exclude_terms") or ())
        if any(term in haystack for term in terms) and not any(term in haystack for term in exclude_terms):
            keys.append(str(lane["key"]))
    return tuple(keys)


def _paper_carrier_rescue_keys(paper: dict[str, Any]) -> tuple[str, ...]:
    allowed={str(lane["key"]) for lane in PRIMARY_EVIDENCE_OBJECT_LANES}
    return tuple(sorted({str(key) for key in paper.get("_paper_first_carrier_rescue_object_lanes") or [] if str(key) in allowed}))


def _paper_object_lane_keys(paper: dict[str, Any]) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*_paper_keys_for_registry(paper,PRIMARY_EVIDENCE_OBJECT_LANES),*_paper_carrier_rescue_keys(paper))))


def _paper_lane_keys(paper: dict[str, Any]) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*_paper_keys_for_registry(paper,PRIMARY_EVIDENCE_LANES),*_paper_carrier_rescue_keys(paper))))


def _lane_counts(papers: list[dict[str, Any]]) -> dict[str, int]:
    counts = {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_LANES}
    for paper in papers:
        for key in _paper_lane_keys(paper):
            counts[key] += 1
    return counts


def _object_lane_counts(papers: list[dict[str, Any]]) -> dict[str, int]:
    counts = {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_OBJECT_LANES}
    for paper in papers:
        for key in _paper_object_lane_keys(paper):
            counts[key] += 1
    return counts


def _source_ref(paper: dict[str, Any]) -> str:
    arxiv_id = _arxiv_id(paper)
    return f"arXiv:{arxiv_id}" if arxiv_id else ""


def _load_json_object(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        payload=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return {}
    return payload if isinstance(payload,dict) else {}


def _portable_review_receipts(generator_state_path: Path | None, primary_state_path: Path | None) -> list[dict[str, Any]]:
    """Read zero-authority source-review receipts that can travel across hosts.

    The generator snapshot carries a bounded receipt history. For repositories
    created before that history existed, the current public Primary + Generator
    pair is enough to bootstrap one receipt when the generator explicitly says
    the run was recorded. Receipts are scheduler metadata only.
    """
    generator=_load_json_object(generator_state_path)
    saturation=generator.get("saturation_memory") or {}
    receipts=[dict(row) for row in saturation.get("portable_review_receipts") or [] if isinstance(row,dict)]
    known={str(row.get("run_id") or "") for row in receipts if row.get("run_id")}
    run_id=str(generator.get("run_id") or "").strip()
    status=str(generator.get("status") or "").strip()
    if (
        run_id and run_id not in known
        and saturation.get("current_run_recorded") is True
        and status in {"GENERATED_ZERO_CANDIDATES","GENERATED_PRE_F0_EVIDENCE_ACQUISITION","GENERATED_AWAIT_PROBLEM_GATE"}
    ):
        primary=_load_json_object(primary_state_path)
        records=[row for row in primary.get("records") or [] if isinstance(row,dict) and row.get("ref")]
        expected=int((generator.get("summary") or {}).get("primary_evidence_records") or 0)
        if primary.get("status")=="READY" and expected==len(records) and expected>=4:
            receipts.append({
                "run_id":run_id,
                "source_refs":sorted({str(row["ref"]) for row in records}),
                "status":status,
                "scientific_authority":False,
                "bootstrap_from_public_transaction":True,
            })
    return receipts[-64:]


def _portable_source_review_receipts(path: Path | None) -> list[dict[str, Any]]:
    """Read explicit zero-authority review receipts outside generator transactions.

    External review exposure changes the source-coverage scheduler, so a receipt is
    accepted only when it is bound to a review artifact with the exact same run id
    and source refs.  The artifact remains zero scientific authority; this check
    prevents a hand-edited receipt from silently marking arbitrary papers reviewed.
    """
    payload=_load_json_object(path)
    valid: list[dict[str, Any]]=[]
    for row in payload.get("receipts") or []:
        if not isinstance(row,dict) or row.get("scientific_authority") is not False:
            continue
        receipt_authority=row.get("authority") or {}
        if any(receipt_authority.get(key) is not False for key in ("candidate_generation","problem","method","experiment","p0","gpu")):
            continue
        run_id=str(row.get("run_id") or "").strip()
        status=str(row.get("status") or "").strip()
        refs=sorted({str(ref).strip() for ref in row.get("source_refs") or [] if str(ref).strip().startswith("arXiv:")})
        if not run_id or status!="EXTERNAL_FRESH_INTAKE_REVIEWED" or len(refs)<4:
            continue
        if row.get("review_complete") is not True or int(row.get("identity_verified_count") or 0)!=len(refs):
            continue
        artifact_ref=str(row.get("review_artifact") or "").strip()
        artifact_rel=Path(artifact_ref)
        if not artifact_ref or artifact_rel.is_absolute() or ".." in artifact_rel.parts:
            continue
        artifact_path=PROJECT_ROOT/artifact_rel
        if not artifact_path.is_file() and path is not None:
            artifact_path=Path(path).parent/artifact_rel
        artifact_sha=str(row.get("review_artifact_sha256") or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}",artifact_sha) or not artifact_path.is_file():
            continue
        if hashlib.sha256(artifact_path.read_bytes()).hexdigest()!=artifact_sha:
            continue
        artifact=_load_json_object(artifact_path)
        artifact_policy=artifact.get("policy") or {}
        artifact_authority=artifact.get("authority") or {}
        artifact_sources=[source for source in artifact.get("sources") or [] if isinstance(source,dict)]
        artifact_refs=sorted({str(source.get("ref") or "").strip() for source in artifact_sources if str(source.get("ref") or "").strip().startswith("arXiv:")})
        artifact_summary=artifact.get("summary") or {}
        if artifact.get("run_id")!=run_id or artifact.get("status")!="EXTERNAL_FRESH_INTAKE_REVIEWED_ZERO_AUTHORITY":
            continue
        if artifact_refs!=refs or len(artifact_sources)!=len(refs) or any(source.get("identity_verified") is not True for source in artifact_sources):
            continue
        if int(artifact_summary.get("identity_verified") or 0)!=len(refs) or int(artifact_summary.get("sources_discovered") or 0)!=len(refs):
            continue
        if int(row.get("provider_model_calls") or 0)!=int(artifact_summary.get("provider_model_calls") or 0):
            continue
        if artifact_policy.get("review_exposure_is_retrieval_metadata_only") is not True or artifact_policy.get("review_exposure_cannot_authorize_or_skip_scientific_gates") is not True:
            continue
        required_authority=("scientific_authority","candidate_generation","problem","method","experiment","p0","gpu")
        if any(artifact_authority.get(key) is not False for key in required_authority):
            continue
        normalized=dict(row);normalized["run_id"]=run_id;normalized["source_refs"]=refs;normalized["scientific_authority"]=False
        valid.append(normalized)
    return valid[-64:]


def _source_exposure_state(
    storage: StorageSettings,
    *,
    portable_generator_state_path: Path | None = None,
    portable_primary_state_path: Path | None = None,
    portable_source_review_state_path: Path | None = None,
) -> tuple[dict[str, int], int, int, list[dict[str, Any]]]:
    """Return deterministic review exposure from private + portable receipts.

    Exposure is retrieval metadata only. It cannot authorize, skip, pass, block,
    or scientifically interpret a paper/problem candidate. Portable receipts
    prevent host switches from forgetting the most recently reviewed tranches.
    """
    path = storage.data_root / "paper-first-problem-discovery" / "discovery-saturation-ledger.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload={}
    private_runs = [row for row in (payload.get("runs") or []) if isinstance(row, dict)] if isinstance(payload, dict) else []
    counts: dict[str, int] = {}
    run_ids:set[str]=set()
    anonymous_private_runs=0
    portable_valid=[]
    for row in private_runs:
        run_id=str(row.get("run_id") or "").strip()
        status=str(row.get("status") or "").strip()
        refs=sorted({str(ref).strip() for ref in row.get("source_refs") or [] if str(ref).strip().startswith("arXiv:")})
        if run_id:
            run_ids.add(run_id)
        else:
            anonymous_private_runs+=1
        for ref in row.get("source_refs") or []:
            ref = str(ref or "").strip()
            if ref:
                counts[ref] = counts.get(ref, 0) + 1
        if run_id and len(refs)>=4 and status in {"GENERATED_ZERO_CANDIDATES","GENERATED_PRE_F0_EVIDENCE_ACQUISITION","GENERATED_AWAIT_PROBLEM_GATE"} and row.get("scientific_authority") is False:
            portable_valid.append({
                "run_id":run_id,
                "pool_sha256":row.get("pool_sha256"),
                "negative_space_sha256":row.get("negative_space_sha256"),
                "discovery_operator_version":row.get("discovery_operator_version"),
                "source_refs":refs,
                "status":status,
                "requested_model":row.get("requested_model"),
                "resolved_model":row.get("resolved_model"),
                "raw_sha256":row.get("raw_sha256"),
                "scientific_authority":False,
                "from_private_saturation_ledger":True,
            })
    portable_added=0
    portable_rows=[
        *_portable_review_receipts(portable_generator_state_path,portable_primary_state_path),
        *_portable_source_review_receipts(portable_source_review_state_path),
    ]
    for row in portable_rows:
        run_id=str(row.get("run_id") or "").strip()
        if not run_id or row.get("scientific_authority") is not False:
            continue
        if str(row.get("status") or "") not in {"GENERATED_ZERO_CANDIDATES","GENERATED_PRE_F0_EVIDENCE_ACQUISITION","GENERATED_AWAIT_PROBLEM_GATE","EXTERNAL_FRESH_INTAKE_REVIEWED"}:
            continue
        refs=sorted({str(ref).strip() for ref in row.get("source_refs") or [] if str(ref).strip().startswith("arXiv:")})
        if len(refs)<4:
            continue
        normalized=dict(row);normalized["run_id"]=run_id;normalized["source_refs"]=refs;normalized["scientific_authority"]=False
        portable_valid.append(normalized)
        if run_id in run_ids:
            continue
        for ref in refs:
            counts[ref]=counts.get(ref,0)+1
        run_ids.add(run_id);portable_added+=1
    by_run:dict[str,dict[str,Any]]={}
    for row in portable_valid:
        run_id=str(row.get("run_id") or "").strip()
        if run_id:
            by_run[run_id]=row
    return counts, len(run_ids)+anonymous_private_runs, portable_added, list(by_run.values())[-64:]


def select_primary_candidates(
    corpus: dict[str, Any],
    *,
    max_papers: int = DEFAULT_MAX_PAPERS,
    now: datetime | None = None,
    max_publication_age_days: float = DEFAULT_MAX_PUBLICATION_AGE_DAYS,
    lane_floor: int = DEFAULT_LANE_FLOOR,
    source_exposure_counts: dict[str, int] | None = None,
    coverage_anchor_count: int = DEFAULT_SOURCE_COVERAGE_ANCHOR_COUNT,
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
    if limit == 0 or not ranked:
        return []

    # No saturation ledger means exactly the legacy global-rank + lane-floor
    # selector. This keeps first-run behavior unchanged.
    scheduler_active = bool(source_exposure_counts)
    if not scheduler_active:
        if lane_floor <= 0:
            return [paper for _, paper in ranked[:limit]]
        selected_ids: set[str] = set()
        selected: list[dict[str, Any]] = []
        lane_counts = {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_LANES}
        for lane in PRIMARY_EVIDENCE_LANES:
            key = str(lane["key"])
            while lane_counts[key] < int(lane_floor) and len(selected) < limit:
                candidate = next(
                    (paper for _, paper in ranked if key in _paper_lane_keys(paper) and _arxiv_id(paper) not in selected_ids),
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

    exposure = {str(key): max(0, int(value or 0)) for key, value in (source_exposure_counts or {}).items()}
    ranked_papers = [paper for _, paper in ranked]
    rank_index = {_arxiv_id(paper): index for index, paper in enumerate(ranked_papers)}
    anchor_count = min(max(0, int(coverage_anchor_count)), limit, len(ranked_papers))
    selected = list(ranked_papers[:anchor_count])
    selected_ids = {_arxiv_id(paper) for paper in selected}

    # The exploration tranche is deterministic: least prior review exposure
    # first, with original global rank as the only tie-break. Exposure does not
    # alter paper relevance/freshness eligibility or scientific authority.
    tail = sorted(
        ranked_papers[anchor_count:],
        key=lambda paper: (
            0 if _paper_object_lane_keys(paper) else (1 if _paper_lane_keys(paper) else 2),
            exposure.get(_source_ref(paper), 0),
            rank_index[_arxiv_id(paper)],
        ),
    )
    for paper in tail:
        if len(selected) >= limit:
            break
        if _arxiv_id(paper) in selected_ids:
            continue
        selected.append(paper)
        selected_ids.add(_arxiv_id(paper))

    if lane_floor > 0:
        eligible_counts = _lane_counts(ranked_papers)
        lane_counts = _lane_counts(selected)
        for lane in PRIMARY_EVIDENCE_LANES:
            key = str(lane["key"])
            needed = min(int(lane_floor), int(eligible_counts.get(key, 0)))
            while lane_counts.get(key, 0) < needed:
                candidate = next(
                    (paper for paper in ranked_papers if key in _paper_lane_keys(paper) and _arxiv_id(paper) not in selected_ids),
                    None,
                )
                if candidate is None:
                    break
                if len(selected) < limit:
                    selected.append(candidate)
                    selected_ids.add(_arxiv_id(candidate))
                    lane_counts = _lane_counts(selected)
                    continue
                candidate_lanes = set(_paper_lane_keys(candidate))
                replaceable: list[tuple[int, dict[str, Any]]] = []
                for index, current_paper in enumerate(selected):
                    if index < anchor_count:
                        continue
                    current_lanes = set(_paper_lane_keys(current_paper))
                    trial = dict(lane_counts)
                    for covered in current_lanes:
                        trial[covered] = max(0, trial.get(covered, 0) - 1)
                    for covered in candidate_lanes:
                        trial[covered] = trial.get(covered, 0) + 1
                    if trial.get(key, 0) < needed:
                        continue
                    preserves_existing = True
                    for other_key, current_count in lane_counts.items():
                        other_needed = min(int(lane_floor), int(eligible_counts.get(other_key, 0)))
                        if current_count >= other_needed and trial.get(other_key, 0) < other_needed:
                            preserves_existing = False
                            break
                    if preserves_existing:
                        replaceable.append((index, current_paper))
                if not replaceable:
                    break
                replace_index, removed = max(
                    replaceable,
                    key=lambda item: (exposure.get(_source_ref(item[1]), 0), rank_index[_arxiv_id(item[1])]),
                )
                selected_ids.remove(_arxiv_id(removed))
                selected[replace_index] = candidate
                selected_ids.add(_arxiv_id(candidate))
                lane_counts = _lane_counts(selected)

    selected.sort(key=lambda paper: rank_index.get(_arxiv_id(paper), 10**9))
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


def _default_arxiv_search_requester(*, query: str, start: int = 0, max_results: int, timeout: float, headers: dict[str, str]):
    return requests.get(
        "https://export.arxiv.org/api/query",
        params={"search_query": query, "start": max(0, int(start)), "max_results": max_results, "sortBy": "submittedDate", "sortOrder": "descending"},
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


def _load_arxiv_rate_limit_state(path: Path | None, *, now: datetime) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        payload=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return {}
    if not isinstance(payload,dict) or payload.get("scientific_authority") is not False:
        return {}
    until=_parse_iso(str(payload.get("blocked_until") or ""))
    if until is None or until <= now:
        return {}
    return payload


def _write_arxiv_rate_limit_state(path: Path | None, *, now: datetime, retry_after_seconds: int) -> dict[str, Any]:
    seconds=max(60,min(int(retry_after_seconds),DEFAULT_ARXIV_RATE_LIMIT_MAX_COOLDOWN_SECONDS))
    payload={
        "schema_version":"1.0",
        "observed_at":now.replace(microsecond=0).isoformat(),
        "blocked_until":(now+timedelta(seconds=seconds)).replace(microsecond=0).isoformat(),
        "retry_after_seconds":seconds,
        "source":"arxiv-export-api",
        "reason":"HTTP 429",
        "scientific_authority":False,
    }
    if path is not None:
        path.parent.mkdir(parents=True,exist_ok=True)
        temp=path.with_name(path.name+".tmp")
        temp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        temp.replace(path)
    return payload


def _arxiv_retry_after_seconds(response: Any, default_seconds: int) -> int:
    headers=getattr(response,"headers",{}) or {}
    try:
        raw=headers.get("Retry-After")
    except AttributeError:
        raw=None
    try:
        return int(str(raw).strip()) if raw is not None and str(raw).strip() else int(default_seconds)
    except ValueError:
        return int(default_seconds)


def discover_arxiv_fallback(
    *,
    queries: tuple[str, ...] = DEFAULT_ARXIV_QUERIES,
    per_query: int = DEFAULT_ARXIV_PER_QUERY,
    max_pages: int = DEFAULT_ARXIV_MAX_PAGES,
    requester: Callable[..., Any] | None = None,
    min_interval_seconds: float = DEFAULT_ARXIV_QUERY_INTERVAL_SECONDS,
    now: datetime | None = None,
    max_publication_age_days: float = DEFAULT_MAX_PUBLICATION_AGE_DAYS,
    rate_limit_state_path: Path | None = None,
    rate_limit_cooldown_seconds: int = DEFAULT_ARXIV_RATE_LIMIT_COOLDOWN_SECONDS,
) -> tuple[list[dict[str, Any]], list[str]]:
    fetch = requester or _default_arxiv_search_requester
    merged: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    last_started: float | None = None
    page_size = max(1, int(per_query))
    page_cap = max(1, int(max_pages))
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    active_rate_limit=_load_arxiv_rate_limit_state(rate_limit_state_path,now=current)
    if active_rate_limit:
        return [], [f"ArxivRateLimitCooldown:until={active_rate_limit.get('blocked_until')}:compute-control-only"]
    cutoff = (current - timedelta(days=max(0.0, float(max_publication_age_days)))).date().isoformat()
    try:
        signature = inspect.signature(fetch)
        supports_start = "start" in signature.parameters or any(param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values())
    except (TypeError, ValueError):
        supports_start = fetch is _default_arxiv_search_requester

    for query in queries:
        query_window_complete = False
        oldest_seen = ""
        for page_index in range(page_cap):
            if page_index > 0 and not supports_start:
                break
            if last_started is not None and min_interval_seconds > 0:
                wait = min_interval_seconds - (time.monotonic() - last_started)
                if wait > 0:
                    time.sleep(wait)
            last_started = time.monotonic()
            try:
                kwargs = {"query": query, "max_results": page_size, "timeout": 30.0, "headers": {"User-Agent": "Agent-Self-Evolution-Observatory/arxiv-fallback"}}
                if supports_start:
                    kwargs["start"] = page_index * page_size
                response = fetch(**kwargs)
                status = int(getattr(response, "status_code", 200))
                if status == 429:
                    rate_state=_write_arxiv_rate_limit_state(rate_limit_state_path,now=current,retry_after_seconds=_arxiv_retry_after_seconds(response,rate_limit_cooldown_seconds))
                    errors.append(f"{query}:RateLimited:HTTP 429:augmentation-circuit-open:until={rate_state.get('blocked_until')}")
                    rows = list(merged.values())
                    rows.sort(key=lambda row: (str((row.get("metadata") or {}).get("publicationDate") or ""), _relevance_score(row), str(row.get("title") or "")), reverse=True)
                    return rows, errors
                if status >= 400:
                    raise RuntimeError(f"HTTP {status}")
                if rate_limit_state_path is not None and rate_limit_state_path.exists():
                    rate_limit_state_path.unlink(missing_ok=True)
                parsed = parse_arxiv_atom(str(getattr(response, "text", "") or ""))
                if not parsed:
                    query_window_complete = True
                    break
                publication_dates = sorted(str((row.get("metadata") or {}).get("publicationDate") or "") for row in parsed if str((row.get("metadata") or {}).get("publicationDate") or ""))
                if publication_dates:
                    oldest_seen = publication_dates[0] if not oldest_seen else min(oldest_seen, publication_dates[0])
                for row in parsed:
                    arxiv_id = _arxiv_id(row)
                    if arxiv_id and _relevance_score(row) >= 2:
                        merged.setdefault(arxiv_id, row)
                if len(parsed) < page_size or (oldest_seen and oldest_seen <= cutoff):
                    query_window_complete = True
                    break
            except Exception as error:
                errors.append(f"{query}:{type(error).__name__}:{str(error)[:160]}")
                query_window_complete = True
                break
        if not query_window_complete:
            errors.append(f"{query}:FreshnessWindowTruncated:oldest={oldest_seen or 'unknown'}:cutoff={cutoff}:pages={page_cap}:page_size={page_size}")
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


def _exact_frozen_fulltext_path(record: dict[str, Any], cache_dir: Path) -> Path:
    ref = str(record.get("ref") or "").strip()
    fulltext_sha = str(record.get("fulltext_sha256") or "").strip().lower()
    if not ref.startswith("arXiv:") or not re.fullmatch(r"[0-9a-f]{64}", fulltext_sha):
        raise ValueError(f"frozen Primary record lacks exact fulltext identity: {ref or 'missing-ref'}")
    arxiv_id = ref.removeprefix("arXiv:")
    safe_id = re.sub(r"[^0-9A-Za-z._-]+", "_", arxiv_id)
    candidates: list[Path] = []
    declared = Path(str(record.get("fulltext_cache_path") or ""))
    if str(declared):
        candidates.append(declared)
    candidates.append(cache_dir / f"arxiv-full-{safe_id}-{fulltext_sha[:12]}.html")
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if not key or key in seen:
            continue
        seen.add(key)
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if not raw or len(raw) > DEFAULT_MAX_PRIMARY_RESPONSE_BYTES:
            continue
        if hashlib.sha256(raw).hexdigest() != fulltext_sha:
            continue
        if b"<section" not in raw.lower():
            continue
        return path
    raise ValueError(f"exact frozen fulltext bytes unavailable for {ref} sha256={fulltext_sha}")


def recompile_frozen_primary_typed_evidence(
    pool: dict[str, Any],
    *,
    cache_dir: Path | None = None,
    storage: StorageSettings | None = None,
) -> dict[str, Any]:
    """Re-derive typed evidence from an exact frozen Primary without retrieval.

    Source refs, primary/fulltext content digests, empirical facts, coverage receipts,
    and selection order are immutable. Only typed evidence and its extractor version
    may change. Every fulltext byte sequence is reverified against the frozen SHA.
    """
    if pool.get("status") != "READY" or not isinstance(pool.get("records"), list) or not pool.get("records"):
        raise ValueError("frozen Primary typed-evidence recompile requires a nonempty READY pool")
    if cache_dir is None:
        storage = storage or StorageSettings.from_env()
        _, cache_dir = _private_paths(storage)
    source = json.loads(json.dumps(pool, ensure_ascii=False))
    prior_version = str(source.get("typed_evidence_extraction_version") or "")
    changed = 0
    for record in source.get("records") or []:
        if not isinstance(record, dict) or record.get("primary_source_verified") is not True:
            raise ValueError("frozen Primary typed-evidence recompile requires verified records only")
        path = _exact_frozen_fulltext_path(record, Path(cache_dir))
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        previous = record.get("typed_evidence") or {}
        typed = extract_typed_evidence_candidates(raw_text, max_per_type=2)
        if previous != typed or str(record.get("typed_evidence_extraction_version") or "") != TYPED_EVIDENCE_EXTRACTION_VERSION:
            changed += 1
        record["typed_evidence"] = typed
        record["typed_evidence_extraction_version"] = TYPED_EVIDENCE_EXTRACTION_VERSION
        record["fulltext_cache_path"] = str(path)
    source["typed_evidence_extraction_version"] = TYPED_EVIDENCE_EXTRACTION_VERSION
    source["derived_evidence_recompile"] = {
        "kind": "typed-evidence-first-party-ownership-recompile",
        "prior_typed_evidence_extraction_version": prior_version,
        "typed_evidence_extraction_version": TYPED_EVIDENCE_EXTRACTION_VERSION,
        "records_recompiled": len(source.get("records") or []),
        "records_changed": changed,
        "source_scheduler_runs_executed": 0,
        "network_fetches_executed": 0,
        "source_manifest_changed": False,
        "scientific_authority": False,
    }
    return source


def project_recompiled_primary_public_state(public_state: dict[str, Any], private_pool: dict[str, Any]) -> dict[str, Any]:
    """Project a frozen typed-evidence recompile into the public Primary receipt."""
    public = json.loads(json.dumps(public_state, ensure_ascii=False))
    private_records = [row for row in private_pool.get("records") or [] if isinstance(row, dict)]
    public_records = [row for row in public.get("records") or [] if isinstance(row, dict)]
    private_manifest = [(str(row.get("ref") or ""), str(row.get("source_sha256") or ""), str(row.get("fulltext_sha256") or "")) for row in private_records]
    public_manifest = [(str(row.get("ref") or ""), str(row.get("source_sha256") or ""), str(row.get("fulltext_sha256") or "")) for row in public_records]
    if not private_manifest or private_manifest != public_manifest:
        raise ValueError("recompiled private Primary manifest does not match public Primary receipt")
    by_ref = {str(row.get("ref") or ""): row for row in private_records}
    total = {key: 0 for key in ("operational_assumptions", "measured_failures", "boundary_observations")}
    for row in public_records:
        private = by_ref[str(row.get("ref") or "")]
        counts = {key: len((private.get("typed_evidence") or {}).get(key) or []) for key in total}
        row["typed_evidence_counts"] = counts
        for key, value in counts.items():
            total[key] += int(value)
    policy = public.setdefault("policy", {})
    policy["typed_evidence_extraction_version"] = TYPED_EVIDENCE_EXTRACTION_VERSION
    policy["typed_evidence_requires_first_party_ownership_or_nonliterature_attribution"] = True
    policy["derived_typed_evidence_reused_only_when_extractor_version_matches"] = True
    public.setdefault("summary", {})["typed_evidence_candidates"] = total
    metadata = private_pool.get("derived_evidence_recompile") or {}
    public["derived_evidence_recompile"] = {
        "kind": str(metadata.get("kind") or "typed-evidence-recompile"),
        "prior_typed_evidence_extraction_version": str(metadata.get("prior_typed_evidence_extraction_version") or ""),
        "typed_evidence_extraction_version": TYPED_EVIDENCE_EXTRACTION_VERSION,
        "records_recompiled": int(metadata.get("records_recompiled") or len(private_records)),
        "records_changed": int(metadata.get("records_changed") or 0),
        "source_scheduler_runs_executed": 0,
        "network_fetches_executed": 0,
        "source_manifest_changed": False,
        "scientific_authority": False,
    }
    return public


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
    if str(record.get("typed_evidence_extraction_version") or "") != TYPED_EVIDENCE_EXTRACTION_VERSION:
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
            "typed_evidence": extract_typed_evidence_candidates(raw_text, max_per_type=2),
            "typed_evidence_extraction_version": TYPED_EVIDENCE_EXTRACTION_VERSION,
        }
    return None


def _portable_carrier_probe_receipts(
    primary_state_path: Path | None,
    *,
    now: datetime,
    max_age_days: float,
) -> list[dict[str, Any]]:
    if primary_state_path is None:
        return []
    payload=_load_json_object(primary_state_path)
    try:
        from .paper_first_no_lane_carrier_probe import CARRIER_CLASSIFIER_VERSION
    except Exception:
        return []
    valid=[]
    for row in (payload.get("carrier_probe") or {}).get("portable_receipts") or []:
        if not isinstance(row,dict) or row.get("scientific_authority") is not False:
            continue
        if str(row.get("classifier_version") or "") != CARRIER_CLASSIFIER_VERSION:
            continue
        age=_age_days(str(row.get("probed_at") or ""),now)
        if age is None or age > max(0.0,float(max_age_days)):
            continue
        ref=str(row.get("ref") or "").strip()
        scope_excluded=str(row.get("probe_outcome") or "")=="SCOPE_EXCLUDED_BY_PRIMARY"
        fulltext_ok=scope_excluded or len(str(row.get("fulltext_sha256") or ""))==64
        if not ref.startswith("arXiv:") or len(str(row.get("primary_sha256") or ""))!=64 or not fulltext_ok:
            continue
        valid.append(dict(row))
    return valid[-CARRIER_PROBE_RECEIPT_LIMIT:]


def _carrier_probe_identity_matches(row: dict[str, Any], paper: dict[str, Any]) -> bool:
    title_fingerprint=hashlib.sha256(_normalize_title(str(paper.get("title") or "")).encode("utf-8")).hexdigest()
    publication_date=str((paper.get("metadata") or {}).get("publicationDate") or "")
    return row.get("title_fingerprint")==title_fingerprint and str(row.get("publication_date") or "")==publication_date


def _carrier_probe_recent_content_matches(row: dict[str, Any], paper: dict[str, Any], cache_dir: Path, *, now: datetime) -> bool:
    if not _carrier_probe_identity_matches(row,paper):
        return False
    arxiv_id=_arxiv_id(paper)
    primary=_cached_primary_page(cache_dir,arxiv_id,paper,now=now,max_age_hours=DEFAULT_RECENT_VERIFIED_CACHE_REUSE_HOURS)
    if not primary or str(primary.get("source_sha256") or "")!=str(row.get("primary_sha256") or ""):
        return False
    if str(row.get("probe_outcome") or "")=="SCOPE_EXCLUDED_BY_PRIMARY":
        return True
    fulltext=_cached_fulltext_page(cache_dir,arxiv_id,now=now,max_age_hours=DEFAULT_RECENT_VERIFIED_CACHE_REUSE_HOURS)
    return bool(fulltext and str(fulltext.get("fulltext_sha256") or "")==str(row.get("fulltext_sha256") or ""))


def _apply_carrier_rescue(paper: dict[str, Any], lanes: list[str] | tuple[str, ...]) -> None:
    allowed={str(row["key"]) for row in PRIMARY_EVIDENCE_OBJECT_LANES}
    rescued=sorted({str(lane) for lane in lanes if str(lane) in allowed})
    if rescued:
        paper["_paper_first_carrier_rescue_object_lanes"]=rescued


def _probe_no_lane_carriers(
    eligible_candidates: list[dict[str, Any]],
    *,
    source_exposure_counts: dict[str, int],
    primary_state_path: Path | None,
    cache_dir: Path,
    requester: Callable[..., Any],
    now: datetime,
    max_probes: int,
    receipt_max_age_days: float,
    min_interval_seconds: float,
) -> dict[str, Any]:
    try:
        from .paper_first_no_lane_carrier_probe import CARRIER_CLASSIFIER_VERSION, build_carrier_probe_receipt, build_primary_scope_exclusion_receipt
    except Exception as error:
        return {"enabled":False,"error":f"classifier-unavailable:{type(error).__name__}","portable_receipts":[],"private_receipts":[],"pending_refs":[],"rescued_refs":[],"attempted":0,"reused":0,"errors":[],"scientific_authority":False}
    no_lane=[paper for paper in eligible_candidates if not _paper_lane_keys(paper) and int(source_exposure_counts.get(_source_ref(paper),0))==0]
    prior=_portable_carrier_probe_receipts(primary_state_path,now=now,max_age_days=receipt_max_age_days)
    by_ref={str(row.get("ref")):row for row in prior if isinstance(row,dict)}
    reusable:dict[str,dict[str,Any]]={}
    for paper in no_lane:
        ref=_source_ref(paper);row=by_ref.get(ref)
        if row and _carrier_probe_recent_content_matches(row,paper,cache_dir,now=now):
            reusable[ref]=row
            _apply_carrier_rescue(paper,row.get("live_rescue_eligible_lanes") or [])
    to_probe=[paper for paper in no_lane if _source_ref(paper) not in reusable][:max(0,int(max_probes))]
    private_receipts=[];new_portable=[];errors=[];last_fetch_started:float|None=None
    cache_dir.mkdir(parents=True,exist_ok=True)
    for paper in to_probe:
        arxiv_id=_arxiv_id(paper);ref=_source_ref(paper)
        try:
            primary=_cached_primary_page(cache_dir,arxiv_id,paper,now=now,max_age_hours=DEFAULT_RECENT_VERIFIED_CACHE_REUSE_HOURS)
            if primary:
                primary_text=str(primary["raw_text"]);primary_sha=str(primary["source_sha256"]);primary_path=str(primary["cache_path"]);parsed=dict(primary["parsed"])
            else:
                if last_fetch_started is not None and min_interval_seconds>0:
                    wait=min_interval_seconds-(time.monotonic()-last_fetch_started)
                    if wait>0: time.sleep(wait)
                last_fetch_started=time.monotonic()
                response=requester(f"https://arxiv.org/abs/{arxiv_id}",timeout=25.0,headers={"User-Agent":"Agent-Self-Evolution-Observatory/carrier-probe-primary"})
                status=int(getattr(response,"status_code",200))
                if status>=400: raise RuntimeError(f"primary-http-{status}")
                primary_text=str(getattr(response,"text","") or "")
                parsed=parse_arxiv_page(primary_text)
                if not parsed["title"] or not parsed["abstract"]: raise RuntimeError("carrier-probe-primary-parse-failed")
                if _title_similarity(str(paper.get("title") or ""),parsed["title"])<0.72: raise RuntimeError("carrier-probe-title-mismatch")
                primary_bytes=primary_text.encode("utf-8");primary_sha=hashlib.sha256(primary_bytes).hexdigest()
                primary_file=cache_dir/f"arxiv-{re.sub(r'[^0-9A-Za-z._-]+','_',arxiv_id)}-{primary_sha[:12]}.html";primary_file.write_bytes(primary_bytes);primary_path=str(primary_file)
            scope_receipt=build_primary_scope_exclusion_receipt(ref=ref,title=parsed["title"],abstract=parsed["abstract"],primary_sha256=primary_sha)
            if scope_receipt:
                scope_receipt.update({"probed_at":now.replace(microsecond=0).isoformat(),"primary_cache_path":primary_path,"fulltext_cache_path":""})
                private_receipts.append(scope_receipt)
                portable={
                    "ref":ref,"probed_at":scope_receipt["probed_at"],
                    "title_fingerprint":hashlib.sha256(_normalize_title(str(paper.get("title") or "")).encode("utf-8")).hexdigest(),
                    "publication_date":str((paper.get("metadata") or {}).get("publicationDate") or ""),
                    "primary_sha256":primary_sha,"fulltext_sha256":"",
                    "classifier_version":CARRIER_CLASSIFIER_VERSION,
                    "probe_outcome":"SCOPE_EXCLUDED_BY_PRIMARY",
                    "scope_exclusion_rule":scope_receipt.get("scope_exclusion_rule"),
                    "matched_existing_object_lanes":[],"live_rescue_eligible_lanes":[],
                    "scientific_authority":False,
                }
                new_portable.append(portable);reusable[ref]=portable
                continue
            cached_full=_cached_fulltext_page(cache_dir,arxiv_id,now=now,max_age_hours=DEFAULT_RECENT_VERIFIED_CACHE_REUSE_HOURS)
            if cached_full:
                fulltext_sha=str(cached_full["fulltext_sha256"]);fulltext_path=str(cached_full["fulltext_cache_path"]);fulltext_text=Path(fulltext_path).read_text(encoding="utf-8",errors="replace")
            else:
                if last_fetch_started is not None and min_interval_seconds>0:
                    wait=min_interval_seconds-(time.monotonic()-last_fetch_started)
                    if wait>0: time.sleep(wait)
                last_fetch_started=time.monotonic()
                response=requester(f"https://arxiv.org/html/{arxiv_id}",timeout=25.0,headers={"User-Agent":"Agent-Self-Evolution-Observatory/carrier-probe-fulltext"})
                status=int(getattr(response,"status_code",200))
                if status>=400: raise RuntimeError(f"fulltext-http-{status}")
                fulltext_text=str(getattr(response,"text","") or "")
                if not fulltext_text or "<section" not in fulltext_text.lower(): raise RuntimeError("carrier-probe-fulltext-parse-failed")
                fulltext_bytes=fulltext_text.encode("utf-8");fulltext_sha=hashlib.sha256(fulltext_bytes).hexdigest()
                fulltext_file=cache_dir/f"arxiv-full-{re.sub(r'[^0-9A-Za-z._-]+','_',arxiv_id)}-{fulltext_sha[:12]}.html";fulltext_file.write_bytes(fulltext_bytes);fulltext_path=str(fulltext_file)
            prior_row=by_ref.get(ref) or {}
            if _carrier_probe_identity_matches(prior_row,paper) and str(prior_row.get("primary_sha256") or "")==primary_sha and str(prior_row.get("fulltext_sha256") or "")==fulltext_sha:
                private_receipt={"ref":ref,"matched_existing_object_lanes":list(prior_row.get("matched_existing_object_lanes") or []),"live_rescue_eligible_lanes":list(prior_row.get("live_rescue_eligible_lanes") or []),"classifier_version":CARRIER_CLASSIFIER_VERSION,"classifier_reused_after_content_reverification":True,"scientific_authority":False}
            else:
                private_receipt=build_carrier_probe_receipt(ref=ref,title=str(paper.get("title") or ""),primary_sha256=primary_sha,fulltext_sha256=fulltext_sha,fulltext_html=fulltext_text)
            private_receipt.update({"probed_at":now.replace(microsecond=0).isoformat(),"primary_cache_path":primary_path,"fulltext_cache_path":fulltext_path})
            private_receipts.append(private_receipt)
            portable={
                "ref":ref,"probed_at":private_receipt["probed_at"],
                "title_fingerprint":hashlib.sha256(_normalize_title(str(paper.get("title") or "")).encode("utf-8")).hexdigest(),
                "publication_date":str((paper.get("metadata") or {}).get("publicationDate") or ""),
                "primary_sha256":primary_sha,"fulltext_sha256":fulltext_sha,
                "classifier_version":CARRIER_CLASSIFIER_VERSION,
                "matched_existing_object_lanes":list(private_receipt.get("matched_existing_object_lanes") or []),
                "live_rescue_eligible_lanes":list(private_receipt.get("live_rescue_eligible_lanes") or []),
                "scientific_authority":False,
            }
            new_portable.append(portable);reusable[ref]=portable
            _apply_carrier_rescue(paper,portable["live_rescue_eligible_lanes"])
        except Exception as error:
            errors.append({"ref":ref,"error":f"{type(error).__name__}:{str(error)[:200]}"})
    all_by_ref={str(row.get("ref")):row for row in prior if isinstance(row,dict)}
    for row in new_portable: all_by_ref[str(row.get("ref"))]=row
    portable=list(all_by_ref.values())[-CARRIER_PROBE_RECEIPT_LIMIT:]
    probed_refs=set(reusable)
    pending=[_source_ref(paper) for paper in no_lane if _source_ref(paper) not in probed_refs]
    rescued=sorted(ref for ref,row in reusable.items() if row.get("live_rescue_eligible_lanes"))
    return {
        "enabled":True,"classifier_version":CARRIER_CLASSIFIER_VERSION,"probe_limit":max(0,int(max_probes)),
        "eligible_no_lane_unreviewed_before_probe":len(no_lane),"attempted":len(to_probe),"reused":len(reusable)-len(new_portable),
        "rescued_refs":rescued,"rescued":len(rescued),"pending_refs":pending,"pending":len(pending),"errors":errors,
        "portable_receipts":portable,"private_receipts":private_receipts,"scientific_authority":False,
    }


def build_primary_evidence_pool(
    *,
    storage: StorageSettings | None = None,
    corpus_path: Path | None = None,
    max_papers: int = DEFAULT_MAX_PAPERS,
    lane_floor: int = DEFAULT_LANE_FLOOR,
    coverage_anchor_count: int = DEFAULT_SOURCE_COVERAGE_ANCHOR_COUNT,
    carrier_probe_limit: int = DEFAULT_NO_LANE_CARRIER_PROBE_LIMIT,
    carrier_probe_receipt_max_age_days: float = DEFAULT_CARRIER_PROBE_RECEIPT_MAX_AGE_DAYS,
    enable_no_lane_carrier_probe: bool = True,
    max_corpus_age_days: float = DEFAULT_MAX_CORPUS_AGE_DAYS,
    max_publication_age_days: float = DEFAULT_MAX_PUBLICATION_AGE_DAYS,
    requester: Callable[..., Any] | None = None,
    arxiv_search_requester: Callable[..., Any] | None = None,
    arxiv_queries: tuple[str, ...] = DEFAULT_ARXIV_QUERIES,
    arxiv_query_interval_seconds: float = DEFAULT_ARXIV_QUERY_INTERVAL_SECONDS,
    arxiv_rate_limit_state_path: Path | None = None,
    arxiv_rate_limit_cooldown_seconds: int = DEFAULT_ARXIV_RATE_LIMIT_COOLDOWN_SECONDS,
    augment_fresh_corpus_with_arxiv: bool = True,
    now: datetime | None = None,
    min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
    recent_verified_cache_reuse_hours: float = DEFAULT_RECENT_VERIFIED_CACHE_REUSE_HOURS,
    recent_fulltext_failure_cooldown_hours: float = DEFAULT_RECENT_FULLTEXT_FAILURE_COOLDOWN_HOURS,
    portable_generator_state_path: Path | None = None,
    portable_primary_state_path: Path | None = None,
    portable_source_review_state_path: Path | None = None,
    cache_dir: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    storage = storage or StorageSettings.from_env()
    corpus_path = corpus_path or storage.corpus_dir / "semantic-scholar-corpus.json"
    corpus = load_live_corpus(corpus_path)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    private_pool_path, default_cache = _private_paths(storage)
    cache_dir = cache_dir or default_cache
    arxiv_rate_limit_state_path = arxiv_rate_limit_state_path or (storage.data_root / "paper-first-problem-discovery" / "arxiv-rate-limit-state.json")
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
        "schema_version": "1.1",
        "generated_at": _now(),
        "policy": {
            "semantic_scholar_is_discovery_metadata_not_primary_evidence": True,
            "verified_primary_page_required": True,
            "arxiv_source_sha_required": True,
            "stale_s2_triggers_primary_arxiv_fallback": True,
            "fresh_s2_is_augmented_by_preregistered_arxiv_lanes": bool(augment_fresh_corpus_with_arxiv),
            "arxiv_augmentation_failure_does_not_invalidate_fresh_corpus": True,
            "arxiv_augmentation_pages_until_freshness_boundary": True,
            "arxiv_augmentation_page_size": int(DEFAULT_ARXIV_PER_QUERY),
            "arxiv_augmentation_max_pages": int(DEFAULT_ARXIV_MAX_PAGES),
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
            "derived_typed_evidence_reused_only_when_extractor_version_matches": True,
            "full_abstracts_remain_private_data_artifacts": True,
            "fulltext_enrichment_is_optional": True,
            "fulltext_snippets_remain_private_data_artifacts": True,
            "empirical_fact_candidates_are_not_ground_truth": True,
            "empirical_fact_precision_gate": True,
            "empirical_fact_extraction_version": EMPIRICAL_FACT_EXTRACTION_VERSION,
            "empirical_fact_evidence_tiers": ["strong-observation", "quantitative-directional", "owned-directional", "result-section-directional"],
            "typed_evidence_candidates_are_not_ground_truth": True,
            "typed_evidence_is_deterministic_and_bounded": True,
            "typed_evidence_requires_first_party_ownership_or_nonliterature_attribution": True,
            "typed_evidence_extraction_version": TYPED_EVIDENCE_EXTRACTION_VERSION,
            "pre_registered_lane_coverage_floor": True,
            "lane_coverage_is_discovery_breadth_not_scientific_authority": True,
            "scientific_object_lanes": [str(lane["key"]) for lane in PRIMARY_EVIDENCE_OBJECT_LANES],
            "context_tags": [str(lane["key"]) for lane in PRIMARY_EVIDENCE_CONTEXT_TAGS],
            "property_tags": [str(lane["key"]) for lane in PRIMARY_EVIDENCE_PROPERTY_TAGS],
            "new_object_lanes_require_shadow_primary_support_and_collision_gate": True,
            "context_and_property_tags_have_zero_scientific_authority": True,
            "lane_floor": int(lane_floor),
            "source_coverage_scheduler_is_discovery_only": True,
            "source_coverage_exploration_prefers_scientific_objects": True,
            "no_lane_carrier_probe_enabled": bool(enable_no_lane_carrier_probe),
            "no_lane_carrier_probe_limit": int(carrier_probe_limit),
            "no_lane_carrier_probe_receipt_max_age_days": float(carrier_probe_receipt_max_age_days),
            "no_lane_carrier_probe_is_existing_object_rescue_only": True,
            "no_lane_carrier_probe_cannot_create_new_object": True,
            "no_lane_carrier_probe_has_zero_scientific_authority": True,
            "no_lane_carrier_probe_failure_prevents_coverage_exhaustion": True,
            "carrier_probe_pending_skips_live_generator_call": True,
            "source_review_exposure_has_zero_scientific_authority": True,
            "portable_source_review_receipts_have_zero_scientific_authority": True,
            "portable_source_review_receipts_require_bound_review_artifact": True,
            "portable_source_review_receipts_require_content_addressed_review_artifact": True,
            "private_saturation_ledger_runs_exported_as_zero_authority_portable_receipts": True,
            "source_exposure_cannot_skip_generation_or_problem_gate": True,
            "source_exposure_does_not_relax_relevance_or_freshness": True,
            "source_coverage_exploration_prefers_preregistered_lanes": True,
            "source_coverage_saturation_is_compute_control_not_scientific_negative": True,
            "source_coverage_exhaustion_requires_complete_retrieval_window": True,
            "new_lane_grounded_source_reopens_generation": True,
            "source_coverage_anchor_count": int(coverage_anchor_count),
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
            "typed_evidence_candidates": {"operational_assumptions": 0, "measured_failures": 0, "boundary_observations": 0},
            "recent_verified_cache_reused": 0,
            "recent_raw_primary_cache_reused": 0,
            "recent_raw_fulltext_cache_reused": 0,
            "recent_fulltext_failure_cooldown_skips": 0,
            "lane_floor": int(lane_floor),
            "source_coverage_scheduler_active": False,
            "saturation_ledger_runs": 0,
            "portable_review_receipts_merged": 0,
            "prior_reviewed_sources": 0,
            "eligible_unreviewed": 0,
            "eligible_lane_unreviewed": 0,
            "eligible_no_lane_unreviewed": 0,
            "selected_previously_reviewed": 0,
            "selected_unreviewed": 0,
            "selected_object_unreviewed": 0,
            "selected_lane_unreviewed": 0,
            "selected_no_lane_unreviewed": 0,
            "carrier_probe_required": False,
            "carrier_probe_attempted": 0,
            "carrier_probe_reused": 0,
            "carrier_probe_rescued": 0,
            "carrier_probe_pending": 0,
            "carrier_probe_errors": 0,
            "carrier_probe_complete": True,
            "eligible_object_linked_sources": 0,
            "reviewed_object_linked_sources": 0,
            "unreviewed_object_linked_sources": 0,
            "eligible_lane_linked_sources": 0,
            "reviewed_lane_linked_sources": 0,
            "unreviewed_lane_linked_sources": 0,
            "unreviewed_no_lane_sources": 0,
            "source_coverage_exhausted": False,
            "source_retrieval_complete": False,
            "coverage_anchor_count": int(coverage_anchor_count),
            "eligible_object_lane_counts": {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_OBJECT_LANES},
            "selected_object_lane_counts": {str(lane["key"]): 0 for lane in PRIMARY_EVIDENCE_OBJECT_LANES},
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
        "schema_version": "1.1",
        "generated_at": public_state["generated_at"],
        "corpus_path": str(corpus_path),
        "empirical_fact_extraction_version": EMPIRICAL_FACT_EXTRACTION_VERSION,
        "typed_evidence_extraction_version": TYPED_EVIDENCE_EXTRACTION_VERSION,
        "records": [],
        "errors": [],
        "fulltext_errors": [],
        "discovery_errors": [],
        "carrier_probe": {"enabled":False,"required":False,"attempted":0,"reused":0,"rescued":0,"pending":0,"errors":[],"portable_receipts":[],"private_receipts":[],"scientific_authority":False},
        "source_coverage": {"scheduler_active": False, "saturation_ledger_runs": 0, "portable_review_receipts_merged": 0, "prior_reviewed_sources": 0, "eligible_unreviewed": 0, "eligible_lane_unreviewed": 0, "eligible_no_lane_unreviewed": 0, "carrier_probe_required":False, "carrier_probe_pending":0, "carrier_probe_complete":True, "eligible_lane_linked_sources": 0, "reviewed_lane_linked_sources": 0, "unreviewed_lane_linked_sources": 0, "unreviewed_no_lane_sources": 0, "coverage_exhausted": False, "coverage_anchor_count": int(coverage_anchor_count), "selected": [], "scientific_authority": False},
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
                now=current,
                max_publication_age_days=max_publication_age_days,
                rate_limit_state_path=arxiv_rate_limit_state_path,
                rate_limit_cooldown_seconds=arxiv_rate_limit_cooldown_seconds,
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
            now=current,
            max_publication_age_days=max_publication_age_days,
            rate_limit_state_path=arxiv_rate_limit_state_path,
            rate_limit_cooldown_seconds=arxiv_rate_limit_cooldown_seconds,
        )
        discovery_corpus = {"papers": fallback_rows}
        public_state["summary"]["discovery_mode"] = "arxiv-primary-fallback"
        private["discovery_mode"] = "arxiv-primary-fallback"
        public_state["discovery_errors"] = discovery_errors
        private["discovery_errors"] = discovery_errors

    source_retrieval_complete = not discovery_errors
    source_exposure_counts, saturation_ledger_runs, portable_review_receipts_merged, portable_review_receipts = _source_exposure_state(
        storage,
        portable_generator_state_path=portable_generator_state_path,
        portable_primary_state_path=portable_primary_state_path,
        portable_source_review_state_path=portable_source_review_state_path,
    )
    source_scheduler_active = bool(source_exposure_counts) and int(max_papers) > max(0, int(coverage_anchor_count))
    eligible_candidates = select_primary_candidates(
        discovery_corpus,
        max_papers=len(discovery_corpus.get("papers") or []),
        now=current,
        max_publication_age_days=max_publication_age_days,
        lane_floor=0,
    )
    fetch = requester or _default_requester
    preprobe_unreviewed_lane_refs={_source_ref(paper) for paper in eligible_candidates if _paper_lane_keys(paper) and int(source_exposure_counts.get(_source_ref(paper),0))==0}
    preprobe_unreviewed_no_lane_refs={_source_ref(paper) for paper in eligible_candidates if not _paper_lane_keys(paper) and int(source_exposure_counts.get(_source_ref(paper),0))==0}
    carrier_probe_required=bool(enable_no_lane_carrier_probe and source_scheduler_active and source_retrieval_complete and not preprobe_unreviewed_lane_refs and preprobe_unreviewed_no_lane_refs)
    prior_carrier_receipts=_portable_carrier_probe_receipts(portable_primary_state_path,now=current,max_age_days=carrier_probe_receipt_max_age_days)
    carrier_probe={"enabled":bool(enable_no_lane_carrier_probe),"required":carrier_probe_required,"attempted":0,"reused":0,"rescued":0,"rescued_refs":[],"pending":0,"pending_refs":[],"errors":[],"portable_receipts":prior_carrier_receipts,"private_receipts":[],"scientific_authority":False}
    if carrier_probe_required:
        carrier_probe=_probe_no_lane_carriers(
            eligible_candidates,
            source_exposure_counts=source_exposure_counts,
            primary_state_path=portable_primary_state_path,
            cache_dir=cache_dir,
            requester=fetch,
            now=current,
            max_probes=carrier_probe_limit,
            receipt_max_age_days=carrier_probe_receipt_max_age_days,
            min_interval_seconds=min_interval_seconds,
        )
        carrier_probe["required"]=True
    carrier_probe_complete=not carrier_probe_required or int(carrier_probe.get("pending") or 0)==0
    candidates = select_primary_candidates(
        discovery_corpus,
        max_papers=max_papers,
        now=current,
        max_publication_age_days=max_publication_age_days,
        lane_floor=lane_floor,
        source_exposure_counts=source_exposure_counts if source_scheduler_active else None,
        coverage_anchor_count=coverage_anchor_count,
    )
    eligible_lane_counts = _lane_counts(eligible_candidates)
    selected_lane_counts = _lane_counts(candidates)
    eligible_object_lane_counts = _object_lane_counts(eligible_candidates)
    selected_object_lane_counts = _object_lane_counts(candidates)
    undercovered_lanes = [
        key for key, eligible_count in eligible_lane_counts.items()
        if eligible_count > 0 and selected_lane_counts.get(key, 0) < min(int(lane_floor), eligible_count)
    ]
    selected_exposures = {_source_ref(paper): int(source_exposure_counts.get(_source_ref(paper), 0)) for paper in candidates}
    selected_previously_reviewed = sum(value > 0 for value in selected_exposures.values())
    eligible_unreviewed_rows=[paper for paper in eligible_candidates if int(source_exposure_counts.get(_source_ref(paper),0))==0]
    selected_unreviewed_rows=[paper for paper in candidates if int(selected_exposures.get(_source_ref(paper),0))==0]
    eligible_object_linked_refs = {_source_ref(paper) for paper in eligible_candidates if _paper_object_lane_keys(paper)}
    reviewed_object_linked_refs = {ref for ref in eligible_object_linked_refs if int(source_exposure_counts.get(ref, 0)) > 0}
    unreviewed_object_linked_refs = eligible_object_linked_refs - reviewed_object_linked_refs
    eligible_lane_linked_refs = {_source_ref(paper) for paper in eligible_candidates if _paper_lane_keys(paper)}
    reviewed_lane_linked_refs = {ref for ref in eligible_lane_linked_refs if int(source_exposure_counts.get(ref, 0)) > 0}
    unreviewed_lane_linked_refs = eligible_lane_linked_refs - reviewed_lane_linked_refs
    unreviewed_no_lane_refs = {_source_ref(paper) for paper in eligible_candidates if not _paper_lane_keys(paper) and int(source_exposure_counts.get(_source_ref(paper), 0)) == 0}
    source_coverage_exhausted = bool(source_scheduler_active and source_retrieval_complete and not unreviewed_lane_linked_refs and carrier_probe_complete)
    public_state["summary"].update({
        "selected": len(candidates),
        "lane_floor": int(lane_floor),
        "source_coverage_scheduler_active": source_scheduler_active,
        "saturation_ledger_runs": int(saturation_ledger_runs),
        "portable_review_receipts_merged": int(portable_review_receipts_merged),
        "prior_reviewed_sources": len(source_exposure_counts),
        "eligible_unreviewed": len(eligible_unreviewed_rows),
        "eligible_lane_unreviewed": sum(bool(_paper_lane_keys(paper)) for paper in eligible_unreviewed_rows),
        "eligible_no_lane_unreviewed": sum(not bool(_paper_lane_keys(paper)) for paper in eligible_unreviewed_rows),
        "selected_previously_reviewed": selected_previously_reviewed,
        "selected_unreviewed": len(selected_unreviewed_rows),
        "selected_object_unreviewed": sum(bool(_paper_object_lane_keys(paper)) for paper in selected_unreviewed_rows),
        "selected_lane_unreviewed": sum(bool(_paper_lane_keys(paper)) for paper in selected_unreviewed_rows),
        "selected_no_lane_unreviewed": sum(not bool(_paper_lane_keys(paper)) for paper in selected_unreviewed_rows),
        "carrier_probe_required": carrier_probe_required,
        "carrier_probe_attempted": int(carrier_probe.get("attempted") or 0),
        "carrier_probe_reused": int(carrier_probe.get("reused") or 0),
        "carrier_probe_rescued": int(carrier_probe.get("rescued") or 0),
        "carrier_probe_pending": int(carrier_probe.get("pending") or 0),
        "carrier_probe_errors": len(carrier_probe.get("errors") or []),
        "carrier_probe_complete": carrier_probe_complete,
        "eligible_object_linked_sources": len(eligible_object_linked_refs),
        "reviewed_object_linked_sources": len(reviewed_object_linked_refs),
        "unreviewed_object_linked_sources": len(unreviewed_object_linked_refs),
        "eligible_lane_linked_sources": len(eligible_lane_linked_refs),
        "reviewed_lane_linked_sources": len(reviewed_lane_linked_refs),
        "unreviewed_lane_linked_sources": len(unreviewed_lane_linked_refs),
        "unreviewed_no_lane_sources": len(unreviewed_no_lane_refs),
        "source_coverage_exhausted": source_coverage_exhausted,
        "source_retrieval_complete": source_retrieval_complete,
        "coverage_anchor_count": min(max(0, int(coverage_anchor_count)), len(candidates)),
        "eligible_object_lane_counts": eligible_object_lane_counts,
        "selected_object_lane_counts": selected_object_lane_counts,
        "eligible_lane_counts": eligible_lane_counts,
        "selected_lane_counts": selected_lane_counts,
        "undercovered_lanes": undercovered_lanes,
    })
    public_state["carrier_probe"]={
        "enabled":bool(carrier_probe.get("enabled")),
        "required":carrier_probe_required,
        "classifier_version":str(carrier_probe.get("classifier_version") or ""),
        "probe_limit":int(carrier_probe.get("probe_limit") or carrier_probe_limit),
        "attempted":int(carrier_probe.get("attempted") or 0),
        "reused":int(carrier_probe.get("reused") or 0),
        "rescued":int(carrier_probe.get("rescued") or 0),
        "pending":int(carrier_probe.get("pending") or 0),
        "complete":carrier_probe_complete,
        "errors":[dict(row) for row in carrier_probe.get("errors") or [] if isinstance(row,dict)],
        "portable_receipts":[dict(row) for row in carrier_probe.get("portable_receipts") or [] if isinstance(row,dict)],
        "scientific_authority":False,
    }
    private["carrier_probe"]=carrier_probe
    private["lane_coverage"] = {
        "lane_floor": int(lane_floor),
        "eligible_object_lane_counts": eligible_object_lane_counts,
        "selected_object_lane_counts": selected_object_lane_counts,
        "eligible_lane_counts": eligible_lane_counts,
        "selected_lane_counts": selected_lane_counts,
        "undercovered_lanes": undercovered_lanes,
    }
    eligible_rank = {_source_ref(paper): index + 1 for index, paper in enumerate(eligible_candidates)}
    private["source_coverage"] = {
        "scheduler_active": source_scheduler_active,
        "saturation_ledger_runs": int(saturation_ledger_runs),
        "portable_review_receipts_merged": int(portable_review_receipts_merged),
        "portable_review_receipts": portable_review_receipts,
        "prior_reviewed_sources": len(source_exposure_counts),
        "eligible_unreviewed": len(eligible_unreviewed_rows),
        "eligible_lane_unreviewed": sum(bool(_paper_lane_keys(paper)) for paper in eligible_unreviewed_rows),
        "eligible_no_lane_unreviewed": sum(not bool(_paper_lane_keys(paper)) for paper in eligible_unreviewed_rows),
        "carrier_probe_required": carrier_probe_required,
        "carrier_probe_pending": int(carrier_probe.get("pending") or 0),
        "carrier_probe_complete": carrier_probe_complete,
        "eligible_object_linked_sources": len(eligible_object_linked_refs),
        "reviewed_object_linked_sources": len(reviewed_object_linked_refs),
        "unreviewed_object_linked_sources": len(unreviewed_object_linked_refs),
        "eligible_lane_linked_sources": len(eligible_lane_linked_refs),
        "reviewed_lane_linked_sources": len(reviewed_lane_linked_refs),
        "unreviewed_lane_linked_sources": len(unreviewed_lane_linked_refs),
        "unreviewed_no_lane_sources": len(unreviewed_no_lane_refs),
        "coverage_exhausted": source_coverage_exhausted,
        "source_retrieval_complete": source_retrieval_complete,
        "coverage_anchor_count": min(max(0, int(coverage_anchor_count)), len(candidates)),
        "selected": [
            {"ref": _source_ref(paper), "prior_review_exposure": selected_exposures.get(_source_ref(paper), 0), "global_rank": eligible_rank.get(_source_ref(paper))}
            for paper in candidates
        ],
        "scientific_authority": False,
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
    typed_evidence_counts = {"operational_assumptions": 0, "measured_failures": 0, "boundary_observations": 0}
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
            for key in typed_evidence_counts:
                typed_evidence_counts[key] += len((record.get("typed_evidence") or {}).get(key) or [])
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
            typed_evidence: dict[str, list[dict[str, str]]] = {"operational_assumptions": [], "measured_failures": [], "boundary_observations": []}
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
                typed_evidence = dict(cached_fulltext.get("typed_evidence") or typed_evidence)
                fulltext_verified += 1
                empirical_fact_count += len(empirical_facts)
                for key in typed_evidence_counts:
                    typed_evidence_counts[key] += len(typed_evidence.get(key) or [])
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
                    typed_evidence = extract_typed_evidence_candidates(full_text, max_per_type=2)
                    fulltext_verified += 1
                    empirical_fact_count += len(empirical_facts)
                    for key in typed_evidence_counts:
                        typed_evidence_counts[key] += len(typed_evidence.get(key) or [])
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
                "typed_evidence": typed_evidence,
                "year": paper.get("year"),
                "publication_date": (paper.get("metadata") or {}).get("publicationDate"),
                "s2_paper_id": paper.get("paper_id"),
                "s2_retrieved_at": (paper.get("metadata") or {}).get("retrievedAt"),
                "fetched_at": _now(),
                "cache_path": str(cache_path),
                "title_similarity": round(similarity, 4),
                "primary_source_verified": True,
                "empirical_fact_extraction_version": EMPIRICAL_FACT_EXTRACTION_VERSION,
                "typed_evidence_extraction_version": TYPED_EVIDENCE_EXTRACTION_VERSION,
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
            "typed_evidence_candidates": dict(typed_evidence_counts),
            "recent_verified_cache_reused": reused_verified,
            "recent_raw_primary_cache_reused": raw_primary_cache_reused,
            "recent_raw_fulltext_cache_reused": raw_fulltext_cache_reused,
            "recent_fulltext_failure_cooldown_skips": fulltext_failure_cooldown_skips,
            "verified_lane_counts": verified_lane_counts,
            "verified_undercovered_lanes": verified_undercovered_lanes,
            "candidate_generation_ready": len(verified) >= 4 and (not carrier_probe_required or bool(unreviewed_lane_linked_refs) or carrier_probe_complete),
        }
    )
    public_state["records"] = [
        {
            **{key: row[key] for key in ("evidence_id", "ref", "title", "primary_url", "source_sha256", "abstract_sha256", "year", "publication_date", "fetched_at")},
            "fulltext_sha256": str(row.get("fulltext_sha256") or ""),
            "empirical_fact_count": len(row.get("empirical_facts") or []),
            "typed_evidence_counts": {key: len((row.get("typed_evidence") or {}).get(key) or []) for key in ("operational_assumptions", "measured_failures", "boundary_observations")},
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
            "summary":{"corpus_available":False,"corpus_fresh":False,"selected":0,"verified":0,"fetch_errors":0,"title_mismatches":0,"fulltext_verified":0,"fulltext_fetch_errors":0,"empirical_fact_candidates":0,"empirical_fact_tier_counts":{},"typed_evidence_candidates":{"operational_assumptions":0,"measured_failures":0,"boundary_observations":0},"candidate_generation_ready":False},"records":[],"errors":[],
        }
    try:
        payload=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return {"schema_version":"1.0","status":"STATE_UNREADABLE","policy":{"candidate_generation_authority":False,"method_authority":False,"experiment_authority":False,"p0_authority":False},"summary":{"corpus_available":False,"corpus_fresh":False,"selected":0,"verified":0,"fetch_errors":1,"title_mismatches":0,"fulltext_verified":0,"fulltext_fetch_errors":0,"empirical_fact_candidates":0,"empirical_fact_tier_counts":{},"typed_evidence_candidates":{"operational_assumptions":0,"measured_failures":0,"boundary_observations":0},"candidate_generation_ready":False},"records":[],"errors":["state-unreadable"]}
    return payload if isinstance(payload,dict) else {"schema_version":"1.0","status":"STATE_INVALID","summary":{},"records":[],"errors":["state-invalid"]}


def write_primary_evidence_pool(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
    *,
    storage: StorageSettings | None = None,
    corpus_path: Path | None = None,
    max_papers: int = DEFAULT_MAX_PAPERS,
    lane_floor: int = DEFAULT_LANE_FLOOR,
    coverage_anchor_count: int = DEFAULT_SOURCE_COVERAGE_ANCHOR_COUNT,
    carrier_probe_limit: int = DEFAULT_NO_LANE_CARRIER_PROBE_LIMIT,
    carrier_probe_receipt_max_age_days: float = DEFAULT_CARRIER_PROBE_RECEIPT_MAX_AGE_DAYS,
    enable_no_lane_carrier_probe: bool = True,
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
    portable_generator_state_path: Path | None = DEFAULT_PORTABLE_REVIEW_STATE,
    portable_primary_state_path: Path | None = None,
    portable_source_review_state_path: Path | None = DEFAULT_PORTABLE_SOURCE_REVIEW_STATE,
    private_pool_output_path: Path | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    state, private = build_primary_evidence_pool(
        storage=storage,
        corpus_path=corpus_path,
        max_papers=max_papers,
        lane_floor=lane_floor,
        coverage_anchor_count=coverage_anchor_count,
        carrier_probe_limit=carrier_probe_limit,
        carrier_probe_receipt_max_age_days=carrier_probe_receipt_max_age_days,
        enable_no_lane_carrier_probe=enable_no_lane_carrier_probe,
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
        portable_generator_state_path=portable_generator_state_path,
        portable_primary_state_path=portable_primary_state_path if portable_primary_state_path is not None else json_path,
        portable_source_review_state_path=portable_source_review_state_path,
    )
    private_pool_path = Path(private_pool_output_path) if private_pool_output_path is not None else private_primary_pool_path(storage)
    private_pool_path.parent.mkdir(parents=True, exist_ok=True)
    private_pool_path.write_text(json.dumps(private, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    public_state = redact_private_paths(state, storage=storage)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(public_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PRIMARY_EVIDENCE = " + json.dumps(public_state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_primary_evidence_pool(), ensure_ascii=False))
