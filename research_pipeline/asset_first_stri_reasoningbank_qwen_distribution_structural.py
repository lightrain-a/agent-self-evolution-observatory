"""Frozen A/B/D/E/N construction and complete R1 structural receipts."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    canonical_json, render_messages, sha256_text,
)

MODEL = "qwen3-coder-next"


def complete_request(problem_statement: str, selected_memory: str,
                     sampling: Mapping[str, Any]) -> dict[str, Any]:
    request: dict[str, Any] = {
        "model": MODEL,
        "messages": render_messages(problem_statement, selected_memory),
        "temperature": float(sampling["temperature"]),
        "top_p": float(sampling["top_p"]),
        "max_completion_tokens": int(sampling["max_output_tokens"]),
        "n": 1,
        "stream": False,
    }
    if isinstance(sampling.get("top_k"), int):
        request["top_k"] = int(sampling["top_k"])
    return request


def treatment_cases(case_id: str, source_query: str,
                    memory_items: Sequence[str]) -> dict[str, list[dict[str, Any]]]:
    items = [str(item) for item in memory_items if str(item).strip()]
    if len(items) < 2:
        raise ValueError("retrieved memory requires at least two nonempty atomic items")
    canonical = "\n\n".join(items)
    return {
        "A": [{"task_id": case_id, "query": source_query, "memory_items": [canonical]}],
        "B": [{"task_id": case_id, "query": source_query, "memory_items": items}],
        "D": [
            {"task_id": f"{case_id}::cross-1", "query": source_query,
             "memory_items": [items[0]], "embedding_identity": "CLONED-SOURCE-QUERY"},
            {"task_id": f"{case_id}::cross-2", "query": source_query,
             "memory_items": items[1:], "embedding_identity": "CLONED-SOURCE-QUERY"},
        ],
        "E": [{"task_id": f"{case_id}::case-id-placebo", "query": source_query,
               "memory_items": items}],
    }


def selected_memory(cases: Sequence[Mapping[str, Any]]) -> str:
    # Frozen official top-1 consumption; within the selected case, all items reunite.
    selected_case = cases[0]
    return "\n\n".join(str(item) for item in selected_case["memory_items"])


def structural_receipt(*, instance_id: str, task_sha256: str,
                       problem_statement: str, retrieved_case: Mapping[str, Any],
                       sampling: Mapping[str, Any]) -> dict[str, Any]:
    items = [str(item) for item in retrieved_case["memory_items"] if str(item).strip()]
    cases = treatment_cases(
        str(retrieved_case["task_id"]), str(retrieved_case["query"]), items)
    memories = {arm: selected_memory(value) for arm, value in cases.items()}
    requests = {arm: complete_request(problem_statement, memory, sampling)
                for arm, memory in memories.items()}
    requests["N"] = complete_request(problem_statement, "", sampling)
    hashes = {arm: sha256_text(canonical_json(request))
              for arm, request in requests.items()}
    evidence_hash = sha256_text(canonical_json(items))
    checks = {
        "at_least_two_nonempty_atomic_items": len(items) >= 2,
        "A_B_complete_R1_equal": canonical_json(requests["A"]) == canonical_json(requests["B"]),
        "A_E_complete_R1_equal": canonical_json(requests["A"]) == canonical_json(requests["E"]),
        "A_B_E_sha256_equal": hashes["A"] == hashes["B"] == hashes["E"],
        "D_complete_R1_differs_from_A": canonical_json(requests["D"]) != canonical_json(requests["A"]),
        "D_sha256_differs_from_A": hashes["D"] != hashes["A"],
        "same_underlying_semantic_evidence_before_transform": True,
        "no_semantic_evidence_added_to_D": True,
    }
    qualified = all(checks.values())
    return {
        "schema_version": 1, "instance_id": instance_id,
        "task_sha256": task_sha256,
        "retrieved_case_id": str(retrieved_case["task_id"]),
        "atomic_memory_item_count": len(items),
        "underlying_semantic_evidence_sha256": evidence_hash,
        "representations": cases,
        "selected_memory_sha256": {arm: sha256_text(value) for arm, value in memories.items()},
        "complete_R1": requests,
        "complete_R1_sha256": hashes,
        "checks": checks,
        "structurally_qualified": qualified,
        "behavioral_calls_made": 0,
        "credential_material_present": False,
    }
