from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:  # pragma: no cover
    TfidfVectorizer = None  # type: ignore[assignment]
    cosine_similarity = None  # type: ignore[assignment]

from .evidence_graph import bilingual_text, normalize_title


@dataclass(frozen=True, slots=True)
class CollisionThresholds:
    duplicate: float = 0.26
    near_duplicate: float = 0.18
    shared_problem: float = 0.14
    shared_mechanism: float = 0.14
    method_signature_duplicate: float = 0.26


def _field(idea: dict[str, Any], key: str) -> str:
    return bilingual_text(idea.get(key)).strip()


def _assets(idea: dict[str, Any]) -> set[str]:
    values = []
    for key in ("datasets", "domains", "models", "nearest_work"):
        values.extend(str(item).lower() for item in idea.get(key) or [])
    return set(values)


def _jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / max(len(left | right), 1)


def _lexical_similarity(left: str, right: str) -> float:
    a = set(normalize_title(left).split())
    b = set(normalize_title(right).split())
    return _jaccard(a, b)


def _similarity_matrix(documents: list[str]) -> list[list[float]]:
    if not documents:
        return []
    if TfidfVectorizer is None or cosine_similarity is None:
        return [[_lexical_similarity(a, b) for b in documents] for a in documents]
    vectorizer = TfidfVectorizer(
        analyzer="char_wb", ngram_range=(3, 5), min_df=1, sublinear_tf=True,
        max_features=40000,
    )
    matrix = vectorizer.fit_transform(documents)
    return cosine_similarity(matrix).tolist()


def _union_find(size: int, pairs: list[tuple[int, int]]) -> list[list[int]]:
    parent = list(range(size))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[b] = a

    for left, right in pairs:
        union(left, right)
    groups: dict[int, list[int]] = {}
    for index in range(size):
        groups.setdefault(find(index), []).append(index)
    return [members for members in groups.values() if len(members) > 1]


def analyze_collisions(
    idea_bank: dict[str, Any],
    *,
    thresholds: CollisionThresholds = CollisionThresholds(),
) -> dict[str, Any]:
    ideas = list(idea_bank.get("passed_ideas") or []) + list(idea_bank.get("blocked_ideas") or [])
    problem_docs = [_field(idea, "purpose") for idea in ideas]
    mechanism_docs = [_field(idea, "core_idea") + " " + _field(idea, "method_logic") for idea in ideas]
    experiment_docs = [_field(idea, "pilot") + " " + _field(idea, "decisive_metric") + " " + _field(idea, "strongest_baseline") for idea in ideas]
    method_signature_docs = [
        " ".join((
            _field(idea, "core_idea"),
            bilingual_text((idea.get("method_substance") or {}).get("learning_signal")),
            _field(idea, "strongest_baseline"),
        ))
        for idea in ideas
    ]
    full_docs = [" ".join((problem_docs[i], mechanism_docs[i], experiment_docs[i], _field(idea, "title"))) for i, idea in enumerate(ideas)]

    problem_matrix = _similarity_matrix(problem_docs)
    mechanism_matrix = _similarity_matrix(mechanism_docs)
    experiment_matrix = _similarity_matrix(experiment_docs)
    method_signature_matrix = _similarity_matrix(method_signature_docs)
    full_matrix = _similarity_matrix(full_docs)

    records: list[dict[str, Any]] = []
    duplicate_pairs: list[tuple[int, int]] = []
    type_counts: Counter[str] = Counter()
    for left in range(len(ideas)):
        for right in range(left + 1, len(ideas)):
            problem = float(problem_matrix[left][right])
            mechanism = float(mechanism_matrix[left][right])
            experiment = float(experiment_matrix[left][right])
            method_signature = float(method_signature_matrix[left][right])
            full = float(full_matrix[left][right])
            assets = _jaccard(_assets(ideas[left]), _assets(ideas[right]))
            # Problem and mechanism carry most of the weight. Experiment text is deliberately
            # down-weighted because all candidates share a common P0/P1/P2 protocol template.
            hybrid = 0.40 * problem + 0.40 * mechanism + 0.08 * experiment + 0.07 * full + 0.05 * assets
            relation = "distinct"
            action = "keep-separate"
            if method_signature >= thresholds.method_signature_duplicate:
                relation, action = "same-method-signature", "merge-or-rewrite-mechanism"
                duplicate_pairs.append((left, right))
            elif hybrid >= thresholds.duplicate and problem >= 0.55 and mechanism >= 0.55:
                relation, action = "duplicate", "merge-or-stop-lower-priority"
                duplicate_pairs.append((left, right))
            elif hybrid >= thresholds.near_duplicate and problem >= 0.12 and mechanism >= 0.12:
                relation, action = "near-duplicate", "review-exact-difference"
                duplicate_pairs.append((left, right))
            elif problem >= thresholds.shared_problem and mechanism < 0.12:
                relation, action = "same-problem-different-mechanism", "retain-as-controlled-comparison"
            elif mechanism >= thresholds.shared_mechanism and problem < 0.12:
                relation, action = "same-mechanism-different-setting", "consider-cross-domain-merge"
            elif mechanism >= 0.12 and experiment >= 0.75:
                relation, action = "merge-candidate", "review-shared-core"
            if relation == "distinct":
                continue
            type_counts[relation] += 1
            records.append({
                "left_id": ideas[left]["id"],
                "right_id": ideas[right]["id"],
                "left_title": ideas[left].get("title"),
                "right_title": ideas[right].get("title"),
                "relation": relation,
                "recommended_action": action,
                "scores": {
                    "hybrid": round(hybrid, 4),
                    "problem": round(problem, 4),
                    "mechanism": round(mechanism, 4),
                    "experiment": round(experiment, 4),
                    "method_signature": round(method_signature, 4),
                    "full": round(full, 4),
                    "assets": round(assets, 4),
                },
            })
    records.sort(key=lambda item: (-item["scores"]["hybrid"], item["left_id"], item["right_id"]))
    clusters = [
        {
            "cluster_id": f"collision-{index + 1}",
            "idea_ids": [ideas[item]["id"] for item in members],
            "titles": [ideas[item].get("title") for item in members],
        }
        for index, members in enumerate(_union_find(len(ideas), duplicate_pairs))
    ]
    return {
        "schema_version": "1.0",
        "thresholds": {
            "duplicate": thresholds.duplicate,
            "near_duplicate": thresholds.near_duplicate,
            "shared_problem": thresholds.shared_problem,
            "shared_mechanism": thresholds.shared_mechanism,
            "method_signature_duplicate": thresholds.method_signature_duplicate,
        },
        "summary": {
            "ideas": len(ideas),
            "pairwise_comparisons": len(ideas) * (len(ideas) - 1) // 2,
            "flagged_pairs": len(records),
            "clusters": len(clusters),
            "relation_counts": dict(type_counts.most_common()),
        },
        "clusters": clusters,
        "pairs": records,
    }
