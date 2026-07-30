from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:  # pragma: no cover - deterministic lexical fallback remains available
    TfidfVectorizer = None  # type: ignore[assignment]
    cosine_similarity = None  # type: ignore[assignment]


_WORDS = re.compile(r"[a-z0-9][a-z0-9+_.-]+", re.I)
_STOPWORDS = {
    "agent", "agents", "model", "models", "method", "methods", "paper", "task", "tasks",
    "using", "with", "without", "from", "into", "that", "this", "these", "those", "the",
    "and", "for", "are", "was", "were", "has", "have", "via", "towards", "toward",
}


def normalize_title(value: str) -> str:
    return " ".join(token for token in _WORDS.findall(value.lower().replace("–", "-")) if token not in _STOPWORDS)


def node_id(kind: str, value: str) -> str:
    digest = hashlib.sha1(f"{kind}:{value}".encode("utf-8")).hexdigest()[:14]
    return f"{kind}:{digest}"


def bilingual_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(str(value.get(key) or "") for key in ("en", "zh"))
    return str(value or "")


def idea_document(idea: dict[str, Any]) -> str:
    fields = (
        "title", "purpose", "core_idea", "rationale", "method_logic", "hypothesis",
        "collision_boundary", "comparative_advantage", "decisive_metric", "pilot",
    )
    parts = [bilingual_text(idea.get(field)) for field in fields]
    parts.extend(str(item) for item in idea.get("nearest_work") or [])
    parts.extend(str(item) for item in idea.get("datasets") or [])
    parts.extend(str(item) for item in idea.get("domains") or [])
    return " ".join(parts)


def paper_document(paper: dict[str, Any]) -> str:
    return " ".join(
        str(paper.get(key) or "")
        for key in ("title", "abstract", "venue")
    )


@dataclass(slots=True)
class GraphBuilder:
    corpus: dict[str, Any]
    idea_bank: dict[str, Any]
    evidence_per_idea: int = 6

    def build(self) -> dict[str, Any]:
        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, Any]] = []
        edge_keys: set[tuple[str, str, str]] = set()

        def add_node(kind: str, key: str, **attrs: Any) -> str:
            identifier = node_id(kind, key)
            if identifier not in nodes:
                nodes[identifier] = {"id": identifier, "kind": kind, "key": key, **attrs}
            else:
                for attr, value in attrs.items():
                    if value not in (None, "", [], {}) and not nodes[identifier].get(attr):
                        nodes[identifier][attr] = value
            return identifier

        def add_edge(source: str, target: str, relation: str, **attrs: Any) -> None:
            key = (source, target, relation)
            if key in edge_keys:
                return
            edge_keys.add(key)
            edges.append({"source": source, "target": target, "relation": relation, **attrs})

        query_nodes: dict[str, str] = {}
        for query in self.corpus.get("queries") or []:
            query_text = str(query.get("query") or "").strip()
            if not query_text:
                continue
            qid = add_node(
                "query", query_text, route=query.get("route"), purpose=query.get("purpose"),
                priority=query.get("priority"),
            )
            query_nodes[query_text] = qid

        paper_by_id: dict[str, str] = {}
        paper_by_title: dict[str, str] = {}
        papers = self.corpus.get("papers") or []
        for paper in papers:
            title = str(paper.get("title") or "").strip()
            if not title:
                continue
            key = str(paper.get("paper_id") or normalize_title(title))
            pid = add_node(
                "paper", key, title=title, year=paper.get("year"), venue=paper.get("venue"),
                url=paper.get("url"), citation_count=(paper.get("metadata") or {}).get("citationCount"),
            )
            paper_by_id[key] = pid
            paper_by_title[normalize_title(title)] = pid
            metadata = paper.get("metadata") or {}
            for match in metadata.get("matches") or []:
                query_text = str(match.get("query") or "").strip()
                qid = query_nodes.get(query_text)
                if qid:
                    add_edge(qid, pid, "retrieved", route=match.get("route"), rank=match.get("rank"))
            relation = metadata.get("relation") or {}
            source_id = str(relation.get("sourcePaperId") or relation.get("source_paper_id") or "")
            if source_id and source_id in paper_by_id:
                add_edge(paper_by_id[source_id], pid, str(relation.get("type") or "citation-neighbor"))

        ideas = list(self.idea_bank.get("passed_ideas") or []) + list(self.idea_bank.get("blocked_ideas") or [])
        idea_ids: dict[str, str] = {}
        for idea in ideas:
            iid = add_node(
                "idea", str(idea["id"]), title=idea.get("title"), status=idea.get("status"),
                rank=idea.get("rank"), priority=idea.get("priority"), track_id=idea.get("track_id"),
                operator=idea.get("operator"),
            )
            idea_ids[str(idea["id"])] = iid
            track_key = str(idea.get("track_id") or "unknown")
            tid = add_node("track", track_key, title=idea.get("track"))
            add_edge(iid, tid, "belongs-to")
            for field, relation in (("purpose", "states-problem"), ("core_idea", "uses-mechanism"), ("hypothesis", "tests-hypothesis")):
                value = bilingual_text(idea.get(field)).strip()
                if value:
                    cid = add_node("claim", f"{idea['id']}:{field}", field=field, text=idea.get(field))
                    add_edge(iid, cid, relation)
            for dataset in idea.get("datasets") or []:
                did = add_node("dataset", str(dataset), title=str(dataset))
                add_edge(iid, did, "evaluates-on")
            for domain in idea.get("domains") or []:
                did = add_node("domain", str(domain), title=str(domain))
                add_edge(iid, did, "covers-domain")
            for model in idea.get("models") or []:
                mid = add_node("model", str(model), title=str(model))
                add_edge(iid, mid, "uses-model")
            for work in idea.get("nearest_work") or []:
                normalized = normalize_title(str(work))
                target = paper_by_title.get(normalized) or add_node("paper-alias", normalized, title=str(work))
                add_edge(iid, target, "nearest-work", provenance="curated")

        self._add_semantic_evidence(ideas, papers, idea_ids, paper_by_id, add_edge)

        kind_counts = Counter(node["kind"] for node in nodes.values())
        relation_counts = Counter(edge["relation"] for edge in edges)
        isolated = self._isolated_nodes(nodes, edges)
        return {
            "schema_version": "1.0",
            "summary": {
                "nodes": len(nodes),
                "edges": len(edges),
                "node_kinds": dict(kind_counts.most_common()),
                "relations": dict(relation_counts.most_common()),
                "isolated_nodes": len(isolated),
                "ideas_with_semantic_evidence": len({edge["source"] for edge in edges if edge["relation"] == "semantic-evidence"}),
            },
            "nodes": sorted(nodes.values(), key=lambda item: (item["kind"], item["key"])),
            "edges": edges,
            "isolated_node_ids": isolated[:200],
        }

    def _add_semantic_evidence(
        self,
        ideas: list[dict[str, Any]],
        papers: list[dict[str, Any]],
        idea_ids: dict[str, str],
        paper_by_id: dict[str, str],
        add_edge: Any,
    ) -> None:
        if not ideas or not papers:
            return
        idea_docs = [idea_document(idea) for idea in ideas]
        paper_docs = [paper_document(paper) for paper in papers]
        if TfidfVectorizer is None or cosine_similarity is None:
            for idea, document in zip(ideas, idea_docs):
                terms = set(normalize_title(document).split())
                scored: list[tuple[float, dict[str, Any]]] = []
                for paper, pdoc in zip(papers, paper_docs):
                    pterms = set(normalize_title(pdoc).split())
                    score = len(terms & pterms) / max(len(terms | pterms), 1)
                    if score:
                        scored.append((score, paper))
                scored.sort(key=lambda item: item[0], reverse=True)
                self._emit_evidence(idea, scored[: self.evidence_per_idea], idea_ids, paper_by_id, add_edge)
            return
        vectorizer = TfidfVectorizer(
            analyzer="word", ngram_range=(1, 2), min_df=1, max_df=0.95,
            sublinear_tf=True, stop_words="english", max_features=30000,
        )
        matrix = vectorizer.fit_transform(idea_docs + paper_docs)
        similarities = cosine_similarity(matrix[: len(ideas)], matrix[len(ideas) :])
        for row, idea in enumerate(ideas):
            order = similarities[row].argsort()[::-1]
            scored = [(float(similarities[row, index]), papers[int(index)]) for index in order[: self.evidence_per_idea] if similarities[row, index] > 0]
            self._emit_evidence(idea, scored, idea_ids, paper_by_id, add_edge)

    @staticmethod
    def _emit_evidence(
        idea: dict[str, Any],
        scored: Iterable[tuple[float, dict[str, Any]]],
        idea_ids: dict[str, str],
        paper_by_id: dict[str, str],
        add_edge: Any,
    ) -> None:
        source = idea_ids[str(idea["id"])]
        for rank, (score, paper) in enumerate(scored, start=1):
            key = str(paper.get("paper_id") or normalize_title(str(paper.get("title") or "")))
            target = paper_by_id.get(key)
            if target:
                add_edge(source, target, "semantic-evidence", score=round(score, 4), rank=rank)

    @staticmethod
    def _isolated_nodes(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]) -> list[str]:
        degree: defaultdict[str, int] = defaultdict(int)
        for edge in edges:
            degree[edge["source"]] += 1
            degree[edge["target"]] += 1
        return [identifier for identifier in nodes if degree[identifier] == 0]


def build_evidence_graph(corpus: dict[str, Any], idea_bank: dict[str, Any]) -> dict[str, Any]:
    return GraphBuilder(corpus=corpus, idea_bank=idea_bank).build()
