from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from .config import PROJECT_ROOT
from .models import text
from .providers import ResearchScope, RetrievedPaper, SearchQuery

DEFAULT_SCOPE_PATH = PROJECT_ROOT / "research_pipeline" / "research_scope.json"
ROUTE_PRIORITIES = {
    "seed": 50,
    "topic": 40,
    "failure": 35,
    "mechanism": 30,
    "analogy": 20,
}
ROUTE_PURPOSES = {
    "seed": "Resolve exact seed papers and establish the citation neighborhood.",
    "topic": "Retrieve direct competitors using the same task, setting, or evaluation target.",
    "failure": "Retrieve limitations, negative results, safety failures, and objective-evaluation mismatches.",
    "mechanism": "Retrieve reusable mechanisms without requiring the same target task.",
    "analogy": "Retrieve structurally analogous solutions from adjacent research areas.",
}


def load_scope(path: Path = DEFAULT_SCOPE_PATH) -> ResearchScope:
    payload = json.loads(path.read_text(encoding="utf-8"))
    topic = payload.get("topic") or {}
    return ResearchScope(
        topic=text(str(topic.get("en") or ""), str(topic.get("zh") or "")),
        target_venue=str(payload.get("target_venue") or ""),
        target_domains=[str(value) for value in payload.get("target_domains") or []],
        available_assets=[str(value) for value in payload.get("available_assets") or []],
        hard_constraints=[str(value) for value in payload.get("hard_constraints") or []],
        seed_papers=[str(value) for value in payload.get("seed_papers") or []],
        query_hints={
            str(route): [str(query) for query in queries]
            for route, queries in (payload.get("query_hints") or {}).items()
        },
        year_range=str(payload.get("year_range") or ""),
        fields_of_study=[str(value) for value in payload.get("fields_of_study") or []],
    )


class DefaultQueryPlanner:
    """Deterministic five-route planner with an auditable scope file."""

    @staticmethod
    def _filters(scope: ResearchScope, *, seed: bool = False) -> dict[str, str]:
        filters: dict[str, str] = {}
        if scope.year_range and not seed:
            filters["year"] = scope.year_range
        if scope.fields_of_study:
            filters["fieldsOfStudy"] = ",".join(scope.fields_of_study)
        return filters

    @staticmethod
    def _deduplicate(queries: Sequence[SearchQuery]) -> list[SearchQuery]:
        seen: set[tuple[str, str]] = set()
        result: list[SearchQuery] = []
        for query in queries:
            normalized = " ".join(query.query.lower().replace("-", " ").split())
            key = (query.route, normalized)
            if not normalized or key in seen:
                continue
            seen.add(key)
            result.append(query)
        return result

    def plan(self, scope: ResearchScope, known_papers: Sequence[RetrievedPaper]) -> list[SearchQuery]:
        del known_papers  # The first deterministic pass is scope-driven; later agents may use corpus feedback.
        queries: list[SearchQuery] = []
        for title in scope.seed_papers:
            queries.append(
                SearchQuery(
                    query=title,
                    route="seed",
                    purpose=ROUTE_PURPOSES["seed"],
                    priority=ROUTE_PRIORITIES["seed"],
                    filters=self._filters(scope, seed=True),
                )
            )

        for route in ("topic", "failure", "mechanism", "analogy"):
            for query in scope.query_hints.get(route, []):
                queries.append(
                    SearchQuery(
                        query=query,
                        route=route,
                        purpose=ROUTE_PURPOSES[route],
                        priority=ROUTE_PRIORITIES[route],
                        filters=self._filters(scope),
                    )
                )

        if not scope.query_hints.get("topic") and scope.topic.get("en"):
            queries.append(
                SearchQuery(
                    query=scope.topic["en"],
                    route="topic",
                    purpose=ROUTE_PURPOSES["topic"],
                    priority=ROUTE_PRIORITIES["topic"],
                    filters=self._filters(scope),
                )
            )
        return self._deduplicate(queries)
