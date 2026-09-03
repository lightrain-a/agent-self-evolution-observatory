#!/usr/bin/env python3
"""Pure post-retrieval exact-information adapter for B1's RoMeRL substrate.

This module performs no retrieval, model call, environment action, or outcome
measurement.  It takes an already-frozen retrieval list and constructs the two
minimum identification views frozen by R35:

1. content-only / provenance-hidden;
2. the same content and order plus truthful raw source-outcome provenance.

Later Q utility, role labels, similarity, and retrieval scores never enter the
executor-visible treatment.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Iterable

TREATMENT_FIELD = "source_outcome_success"


class ExactInformationError(ValueError):
    """Raised when a retrieved row cannot support the frozen intervention."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _require_frozen_row(row: dict[str, Any], position: int) -> tuple[str, str, bool]:
    if not isinstance(row, dict):
        raise ExactInformationError(f"retrieved row {position} is not an object")
    memory_id = row.get("memory_id")
    content = row.get("content")
    metadata = row.get("metadata")
    if not isinstance(memory_id, str) or not memory_id:
        raise ExactInformationError(f"retrieved row {position} lacks a stable memory_id")
    if not isinstance(content, str):
        raise ExactInformationError(f"retrieved row {position} lacks string content")
    if not isinstance(metadata, dict):
        raise ExactInformationError(f"retrieved row {position} lacks metadata")
    success = metadata.get("success")
    if type(success) is not bool:  # deliberately reject 0/1 coercion or missing provenance
        raise ExactInformationError(f"retrieved row {position} lacks boolean metadata.success")
    return memory_id, content, success


def build_exact_information_pair(retrieved_rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Build the frozen hidden-vs-raw-provenance pair without altering retrieval.

    The function is intentionally post-retrieval. It preserves every input row
    and its order. The only executor-visible difference is TREATMENT_FIELD.
    Diagnostic digests bind the frozen upstream retrieval using memory ID,
    content, query, similarity, and Q estimate, but those diagnostics are not
    exposed as treatment information.
    """
    source = deepcopy(list(retrieved_rows))
    hidden: list[dict[str, Any]] = []
    raw: list[dict[str, Any]] = []
    frozen_rows: list[dict[str, Any]] = []

    for position, row in enumerate(source):
        memory_id, content, success = _require_frozen_row(row, position)
        visible_base = {"position": position, "content": content}
        hidden.append(dict(visible_base))
        raw.append({**visible_base, TREATMENT_FIELD: success})
        frozen_rows.append(
            {
                "position": position,
                "memory_id": memory_id,
                "content": content,
                "query": row.get("query"),
                "similarity": row.get("similarity"),
                "q_estimate": row.get("q_estimate"),
            }
        )

    frozen_digest = hashlib.sha256(_canonical_json(frozen_rows)).hexdigest()
    hidden_core = [{"position": x["position"], "content": x["content"]} for x in hidden]
    raw_core = [{"position": x["position"], "content": x["content"]} for x in raw]
    if hidden_core != raw_core:
        raise AssertionError("non-provenance executor-visible information drifted across arms")
    if len(hidden) != len(source) or len(raw) != len(source):
        raise AssertionError("adapter changed retrieval cardinality")

    return {
        "content_only_provenance_hidden": hidden,
        "raw_provenance_exact_information": raw,
        "audit": {
            "post_retrieval_only": True,
            "input_row_count": len(source),
            "output_row_count_per_arm": len(source),
            "retrieval_cardinality_preserved": True,
            "retrieval_order_preserved": True,
            "actionable_content_identical": True,
            "only_executor_visible_treatment_field": TREATMENT_FIELD,
            "q_or_role_exposed_to_executor": False,
            "frozen_retrieval_sha256": frozen_digest,
        },
    }
