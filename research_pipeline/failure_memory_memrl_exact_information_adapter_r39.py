#!/usr/bin/env python3
"""Post-retrieval exact-information adapter for B1 on pinned MemRL.

The pinned MemRL retriever returns selected rows containing `memory_id`,
`content`, `metadata`, `similarity`, and `q_estimate`.  B1's provenance-only
identification must not rerun retrieval differently across arms.  This adapter
therefore acts strictly *after* selected rows are frozen and exposes only:

- hidden arm: actionable content;
- raw arm: identical actionable content + truthful source `metadata.success`.

Retrieval IDs/order, similarity, Q, task IDs, source benchmark, update strategy,
and all other metadata remain audit-only and are not executor-visible.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Iterable

TREATMENT_FIELD = "source_outcome_success"


class MemRLExactInformationError(ValueError):
    pass


def _meta_to_dict(metadata: Any) -> dict[str, Any]:
    if isinstance(metadata, dict):
        return dict(metadata)
    if metadata is None:
        return {}
    if hasattr(metadata, "model_dump"):
        try:
            data = metadata.model_dump()
            extra = getattr(metadata, "model_extra", None)
            if isinstance(extra, dict):
                data.update(extra)
            return dict(data)
        except Exception:
            return {}
    extra = getattr(metadata, "model_extra", None)
    if isinstance(extra, dict):
        return dict(extra)
    return {}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def build_memrl_exact_information_pair(selected_rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = deepcopy(list(selected_rows))
    hidden: list[dict[str, Any]] = []
    raw: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []

    for position, row in enumerate(rows):
        if not isinstance(row, dict):
            raise MemRLExactInformationError(f"selected row {position} is not an object")
        memory_id = row.get("memory_id")
        content = row.get("content")
        metadata = _meta_to_dict(row.get("metadata"))
        success = metadata.get("success")

        if not isinstance(memory_id, str) or not memory_id:
            raise MemRLExactInformationError(f"selected row {position} lacks stable memory_id")
        if not isinstance(content, str) or not content:
            raise MemRLExactInformationError(f"selected row {position} lacks actionable content")
        if type(success) is not bool:
            raise MemRLExactInformationError(f"selected row {position} lacks boolean source metadata.success")

        visible = {"position": position, "content": content}
        hidden.append(dict(visible))
        raw.append({**visible, TREATMENT_FIELD: success})
        audit_rows.append(
            {
                "position": position,
                "memory_id": memory_id,
                "content": content,
                "similarity": row.get("similarity"),
                "q_estimate": row.get("q_estimate"),
                "score": row.get("score"),
                "task_id": row.get("task_id"),
                "metadata_success": success,
            }
        )

    hidden_core = [{"position": x["position"], "content": x["content"]} for x in hidden]
    raw_core = [{"position": x["position"], "content": x["content"]} for x in raw]
    if hidden_core != raw_core:
        raise AssertionError("non-provenance executor-visible information differs across arms")

    return {
        "content_only_provenance_hidden": hidden,
        "raw_provenance_exact_information": raw,
        "audit": {
            "post_retrieval_only": True,
            "input_selected_rows": len(rows),
            "rows_per_arm": len(rows),
            "retrieval_membership_preserved": True,
            "retrieval_order_preserved": True,
            "actionable_content_identical": True,
            "only_executor_visible_difference": TREATMENT_FIELD,
            "similarity_q_score_role_and_ids_hidden_from_executor": True,
            "frozen_selected_sha256": hashlib.sha256(_canonical(audit_rows)).hexdigest(),
        },
    }
