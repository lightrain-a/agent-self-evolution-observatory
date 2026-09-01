"""Preregistered pilot metric-degeneracy checks for EditTargetSet."""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Mapping, Sequence

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_edit_targets import (
    atoms_from_signature, jaccard_distance,
)


def pilot_metric_gate(
    tasks: Mapping[str, Mapping[str, Sequence[Mapping[str, Any]]]]
) -> dict[str, Any]:
    distances = []
    python_hunks = 0
    fallback_hunks = 0
    for _, arms in sorted(tasks.items()):
        pooled = list(arms.get("A", [])) + list(arms.get("D", []))
        for left, right in combinations(pooled, 2):
            distances.append(jaccard_distance(
                atoms_from_signature(left), atoms_from_signature(right)))
        for signature in pooled:
            python_hunks += int(signature.get("nonempty_python_diff_hunk_count", 0))
            fallback_hunks += int(signature.get("python_fallback_hunk_count", 0))
    if not distances:
        raise ValueError("pilot has no preregistered A/D pairwise distances")
    counts = Counter(distances)
    modal_value, modal_count = sorted(
        counts.items(), key=lambda row: (-row[1], row[0]))[0]
    constant_rate = modal_count / len(distances)
    fallback_rate = fallback_hunks / python_hunks if python_hunks else 0.0
    constant_fail = constant_rate >= .90
    fallback_fail = python_hunks > 0 and fallback_rate >= .90
    qualified = not constant_fail and not fallback_fail
    return {
        "distance_count": len(distances),
        "unique_distance_count": len(counts),
        "modal_distance": modal_value,
        "modal_distance_count": modal_count,
        "modal_distance_rate": constant_rate,
        "nonempty_python_diff_hunk_count": python_hunks,
        "python_fallback_hunk_count": fallback_hunks,
        "python_fallback_rate": fallback_rate,
        "constant_distance_degeneracy": constant_fail,
        "python_symbol_fallback_degeneracy": fallback_fail,
        "decision": "EDIT_TARGET_METRIC_QUALIFIED" if qualified else "EDIT_TARGET_METRIC_UNQUALIFIED",
        "confirmatory_execution_authorized": False,
    }
