"""Official ReasoningBank memory parsing and deterministic source-bank audit rules."""
from __future__ import annotations

import hashlib
from typing import Any, Iterable, Sequence

from research_pipeline.asset_first_stri_reasoningbank_p1_core import canonical_json, sha256_text


def parse_official_memory_items(raw_response: str) -> list[str]:
    # Exact pinned official induce_memory.py semantics at commit ed806117...
    return [item for item in raw_response.split("\n\n") if item.strip()]


def memory_record(*, source_task_id: str, source_repository: str,
                  source_query: str, task_sha256: str, trajectory_sha256: str,
                  source_resolved: bool, raw_response: str,
                  policy_model: str, extractor_model: str,
                  provider_config_sha256: str, evaluator_result: dict[str, Any]) -> dict[str, Any]:
    items = parse_official_memory_items(raw_response)
    return {
        "source_task_id": source_task_id, "source_repository": source_repository,
        "source_query": source_query, "source_query_sha256": sha256_text(source_query),
        "task_sha256": task_sha256, "source_trajectory_sha256": trajectory_sha256,
        "source_resolved": source_resolved, "raw_extractor_response": raw_response,
        "raw_extractor_response_sha256": sha256_text(raw_response),
        "parsed_memory_items": items, "memory_item_count": len(items),
        "memory_item_hashes": [sha256_text(item) for item in items],
        "policy_model": policy_model, "extractor_model": extractor_model,
        "provider_config_sha256": provider_config_sha256,
        "source_evaluator_result": evaluator_result,
        "removed_for_quality": False, "credential_material_present": False,
    }


def audit_sample(task_ids: Sequence[str], *, experiment_id: str) -> list[str]:
    if len(task_ids) % 4:
        raise ValueError("source task count must be divisible by four")
    ranked = sorted(task_ids, key=lambda task_id: (
        hashlib.sha256(f"{experiment_id}||{task_id}".encode()).hexdigest(), task_id))
    return ranked[:len(task_ids) // 4]


def adjudicate_fidelity(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    receipts = list(rows)
    if not receipts:
        raise ValueError("empty fidelity audit")
    severe = sum(bool(row["SEVERE_FIDELITY_FAILURE"]) for row in receipts)
    rate = severe / len(receipts)
    passed = rate <= .25
    return {
        "audited_source_task_count": len(receipts),
        "severe_fidelity_failure_count": severe,
        "severe_fidelity_failure_rate": rate,
        "threshold_rule": "source bank fails only when severe failures > 25% of audited tasks",
        "decision": "SOURCE_BANK_FIDELITY_QUALIFIED" if passed else "SOURCE_BANK_FIDELITY_UNQUALIFIED",
        "all_frozen_memories_retained": passed,
        "selective_memory_deletion_performed": False,
    }
