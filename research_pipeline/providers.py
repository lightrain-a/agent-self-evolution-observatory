from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence

from .models import BilingualText, IdeaCandidate, PaperEvidence, PilotGate, ReviewRecord


@dataclass(slots=True)
class ResearchScope:
    topic: BilingualText
    target_venue: str
    target_domains: list[str] = field(default_factory=list)
    available_assets: list[str] = field(default_factory=list)
    hard_constraints: list[str] = field(default_factory=list)
    seed_papers: list[str] = field(default_factory=list)
    query_hints: dict[str, list[str]] = field(default_factory=dict)
    year_range: str = ""
    fields_of_study: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SearchQuery:
    query: str
    route: str
    purpose: str
    priority: int = 0
    filters: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievedPaper:
    paper_id: str
    title: str
    year: int | None = None
    venue: str = ""
    abstract: str = ""
    url: str = ""
    citations: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PaperFacet:
    paper_id: str
    problem: BilingualText
    limitation: BilingualText
    core_claim: BilingualText
    intuition: BilingualText
    mechanism: BilingualText
    evidence: BilingualText
    assumptions: BilingualText
    failure_boundary: BilingualText
    reusable_purpose: BilingualText
    reusable_mechanism: BilingualText
    reusable_evaluation: BilingualText


@dataclass(slots=True)
class GapCandidate:
    gap_id: str
    kind: str
    statement: BilingualText
    supporting_papers: list[str]
    contradicting_papers: list[str] = field(default_factory=list)
    required_observation: BilingualText = field(default_factory=dict)
    feasibility_risk: BilingualText = field(default_factory=dict)


@dataclass(slots=True)
class CollisionReport:
    idea_id: str
    same_problem: list[PaperEvidence] = field(default_factory=list)
    same_mechanism: list[PaperEvidence] = field(default_factory=list)
    same_combination: list[PaperEvidence] = field(default_factory=list)
    same_experiment: list[PaperEvidence] = field(default_factory=list)
    verdict: str = "unknown"
    unresolved_difference: BilingualText = field(default_factory=dict)


class QueryPlanner(Protocol):
    """Produce complementary topic, citation, failure, mechanism, and analogy searches."""

    def plan(self, scope: ResearchScope, known_papers: Sequence[RetrievedPaper]) -> list[SearchQuery]: ...


class LiteratureRetriever(Protocol):
    """Search public APIs, citation graphs, or a local full-text index."""

    def search(self, queries: Sequence[SearchQuery], *, limit: int) -> list[RetrievedPaper]: ...

    def expand_citations(self, papers: Sequence[RetrievedPaper], *, depth: int = 1) -> list[RetrievedPaper]: ...


class FacetExtractor(Protocol):
    """Convert papers into the site's evidence-first structured reading schema."""

    def extract(self, papers: Sequence[RetrievedPaper]) -> list[PaperFacet]: ...


class GapMiner(Protocol):
    """Find limitations, contradictions, missing cells, and objective–metric mismatches."""

    def mine(self, scope: ResearchScope, facets: Sequence[PaperFacet]) -> list[GapCandidate]: ...


class IdeaSynthesizer(Protocol):
    """Apply one named idea operator at a time and preserve its evidence lineage."""

    def synthesize(
        self,
        scope: ResearchScope,
        gap: GapCandidate,
        facets: Sequence[PaperFacet],
        *,
        operator_key: str,
        count: int,
    ) -> list[IdeaCandidate]: ...


class NoveltyChecker(Protocol):
    """Run four-way nearest-work search rather than one opaque novelty score."""

    def check(self, idea: IdeaCandidate, corpus: Sequence[RetrievedPaper]) -> CollisionReport: ...


class ReviewerProvider(Protocol):
    """Return an independent verdict and a concrete blocking or revision action."""

    def review(self, idea: IdeaCandidate, collision: CollisionReport) -> ReviewRecord: ...


class PilotPlanner(Protocol):
    """Freeze the smallest experiment most capable of falsifying the idea."""

    def plan(self, idea: IdeaCandidate, reviews: Sequence[ReviewRecord]) -> PilotGate: ...


class DecisionEngine(Protocol):
    """Only this layer may advance, hold, or stop a candidate."""

    def decide(
        self,
        idea: IdeaCandidate,
        collision: CollisionReport,
        reviews: Sequence[ReviewRecord],
        pilot: PilotGate | None,
    ) -> str: ...
