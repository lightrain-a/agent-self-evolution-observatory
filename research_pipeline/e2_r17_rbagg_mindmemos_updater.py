from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_mindmemos_updater import sha_file, sha_text
from research_pipeline.e2_r17_rbagg_posthold import (
    RBAggregatedSessionEvidence,
    build_rb_precomputed_summary_payload,
    build_rb_search_session_add_payload,
    validate_rb_add_summary_pair,
)
from research_pipeline.e2_r17_search_projection_runner import SearchPool

_ID_NAMESPACE = uuid.UUID("24631de6-d366-445b-815d-f931786abb17")


@dataclass(frozen=True)
class RBAggUpdateResult:
    stream_id: str
    update_receipt_path: str
    update_receipt_sha256: str
    skill_post_path: str
    skill_post_sha256: str
    evolved: bool
    new_version_ids: tuple[str, ...]
    mindmemos_provider_calls: int
    mindmemos_provider_total_tokens: int


def rb_trace_uuid(stream_id: str, task_id: str, pool_id: str) -> str:
    return str(uuid.uuid5(_ID_NAMESPACE, f"{stream_id}|{task_id}|{pool_id}|rbagg"))


async def run_rbagg_update(
    *,
    stream_id: str,
    pools: Sequence[SearchPool],
    aggregates: Sequence[RBAggregatedSessionEvidence],
    initial_skill_md: str,
    initial_skill_sha256: str,
    run_dir: Path,
    llm_adapter: Any,
    mindmemos_commit: str,
    contract_sha256: str,
    authorization_sha256: str,
    transcript_max_chars: int = 100000,
) -> RBAggUpdateResult:
    """Run the first-party MindMemOS patch stage on eight precomputed RB summaries.

    ReasoningBank's PARALLEL_SI call replaces MindMemOS's per-trajectory summary
    stage; it does not add a second evolution stage. Each aggregate is represented
    by a 1:1 explicit search-session add record plus a precomputed
    ``SkillTraceSummary``. The standard first-party scored patch proposer and
    deterministic patch applier remain unchanged.

    The synthetic search-session record is never summarized by MindMemOS. Before
    ``SkillEvolver.evolve`` is entered this function proves all eight matching
    summaries already exist, so ``_injected_candidates`` must skip all eight add
    records. Any mismatch is fail-closed.
    """

    if len(pools) != 8 or len(aggregates) != 8:
        raise ValueError("RB-AGG requires exactly eight frozen task pools and eight aggregates")
    if [pool.task_id for pool in pools] != [unit.task_id for unit in aggregates]:
        raise ValueError("RB-AGG pool/aggregate task order mismatch")
    for pool, unit in zip(pools, aggregates):
        pool.validate()
        unit.validate()
        if unit.pool_id != pool.pool_id:
            raise ValueError("RB-AGG pool identity mismatch")
        if float(unit.acting_score) != float(pool.acting_success):
            raise ValueError("RB-AGG session score differs from frozen acting outcome")

    run_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = run_dir / "update_receipt.json"
    skill_path = run_dir / "skill_post" / "SKILL.md"
    if receipt_path.exists() and skill_path.exists():
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        if sha_file(skill_path) != payload.get("skill_post_sha256"):
            raise RuntimeError("existing RB-AGG updater receipt failed skill content-address check")
        return RBAggUpdateResult(
            stream_id=stream_id,
            update_receipt_path=str(receipt_path.resolve()),
            update_receipt_sha256=sha_file(receipt_path),
            skill_post_path=str(skill_path.resolve()),
            skill_post_sha256=sha_file(skill_path),
            evolved=bool(payload.get("evolved")),
            new_version_ids=tuple(payload.get("new_version_ids") or []),
            mindmemos_provider_calls=len(payload.get("adapter_receipts") or []),
            mindmemos_provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in payload.get("adapter_receipts") or []),
        )

    from mindmemos.components.skill import deserialize_bundle, serialize_bundle
    from mindmemos.config import QdrantConfig, SkillEvolutionConfig
    from mindmemos.infra.db import SkillVersionRepository
    from mindmemos.infra.db.models import AddRecordPoint
    from mindmemos.infra.db.qdrant import QdrantStore
    from mindmemos.mappers import to_skill_trace_summary_point
    from mindmemos.pipelines.skill import SkillVersionStore
    from mindmemos.pipelines.skill import evolution as evolution_module
    from mindmemos.pipelines.skill.evolution import SkillEvolver
    from mindmemos.typing import SkillTraceSummary
    from qdrant_client import AsyncQdrantClient

    client = AsyncQdrantClient(":memory:")
    qdrant_cfg = QdrantConfig(
        url="http://unused",
        add_record_collection="r17_rbagg_add_record",
        skill_version_collection="r17_rbagg_skill_version",
        skill_blob_collection="r17_rbagg_skill_blob",
        skill_trace_pending_collection="r17_rbagg_skill_trace_pending",
        skill_trace_summary_collection="r17_rbagg_skill_trace_summary",
        vector_size=2,
    )
    qdrant = QdrantStore(qdrant_cfg, client=client)
    await qdrant.ensure_schema()
    skill_repo = SkillVersionRepository(qdrant_cfg, engine=qdrant.engine)
    await skill_repo.ensure_schema()
    store = SkillVersionStore(skill_repo=skill_repo, add_record_repo=qdrant.add_record)
    evolver = SkillEvolver(
        store=store,
        skill_repo=skill_repo,
        add_record_repo=qdrant.add_record,
        llm_client=llm_adapter,
    )

    project_id = f"e2-r17-rbagg-{stream_id}"
    root = await store.register(
        project_id=project_id,
        name="xlsx",
        content=serialize_bundle({"SKILL.md": initial_skill_md}),
    )
    base_time = datetime(2026, 9, 2, tzinfo=UTC)
    provenance_rows: list[dict[str, Any]] = []

    for index, (pool, unit) in enumerate(zip(pools, aggregates)):
        add_id = rb_trace_uuid(stream_id, pool.task_id, pool.pool_id)
        created_at = base_time + timedelta(minutes=index)
        add_payload = build_rb_search_session_add_payload(
            unit=unit,
            project_id=project_id,
            task_completed_at=created_at.isoformat(),
            initial_skill_sha256=initial_skill_sha256,
            root_version_id=root.version_id,
            deterministic_add_record_id=add_id,
        )
        summary_payload = build_rb_precomputed_summary_payload(
            unit=unit,
            project_id=project_id,
            cloud_skill_id=root.cloud_skill_id,
            skill_name="xlsx",
            deterministic_add_record_id=add_id,
            created_at=created_at,
        )
        validate_rb_add_summary_pair(add_payload, summary_payload)
        await qdrant.upsert_add_record(AddRecordPoint(add_record_id=add_id, payload=add_payload))
        summary = SkillTraceSummary(
            summary_id=summary_payload["summary_id"],
            project_id=summary_payload["project_id"],
            cloud_skill_id=summary_payload["cloud_skill_id"],
            add_record_id=summary_payload["add_record_id"],
            skill_name=summary_payload["skill_name"],
            summary=summary_payload["summary"],
            created_at=summary_payload["created_at"],
            consumed_version_id=None,
            score=float(summary_payload["score"]),
            task_id=summary_payload["task_id"],
        )
        await skill_repo.upsert_summary(to_skill_trace_summary_point(summary))
        provenance_rows.append(
            {
                "task_id": pool.task_id,
                "pool_id": pool.pool_id,
                "add_record_id": add_id,
                "aggregate_memory_items_sha256": unit.memory_items_sha256,
                "aggregate_memory_item_count": unit.memory_item_count,
                "session_score": float(unit.acting_score),
                "source_trajectory_count": 8,
                "direct_mindmemos_trajectory_summary_call": False,
            }
        )

    # Fail closed if any search-session source record is not already represented
    # by exactly one precomputed summary before the first-party evolver is entered.
    existing = await evolver._existing_summaries(project_id, root.cloud_skill_id)
    expected_ids = {rb_trace_uuid(stream_id, pool.task_id, pool.pool_id) for pool in pools}
    if set(existing) != expected_ids or len(existing) != 8:
        raise RuntimeError("RB-AGG precomputed summary set is incomplete or contains extras")
    for summary_id, item in existing.items():
        if item.add_record_id != summary_id or item.score is None:
            raise RuntimeError("RB-AGG precomputed summary provenance/score drift")

    frozen_cfg = SkillEvolutionConfig(
        min_aggregate=8,
        max_aggregate=8,
        summary_concurrency=4,
        rewrite_skill=False,
        use_trajectory_score=True,
        evolved_status="draft",
        transcript_max_chars=transcript_max_chars,
        max_trace_scan=100,
    )

    class _Algo:
        skill_evolution = frozen_cfg

    class _Config:
        algo_config = _Algo()

    original_get_config = evolution_module.get_config
    evolution_module.get_config = lambda: _Config()
    try:
        update = await evolver.evolve(project_id=project_id, cloud_skill_id=root.cloud_skill_id)
        post_existing = await evolver._existing_summaries(project_id, root.cloud_skill_id)
    finally:
        evolution_module.get_config = original_get_config

    try:
        if not update.evolved or not update.new_version_id:
            raise RuntimeError(
                f"RB-AGG first-party SkillEvolver did not mint a version: pending={update.pending_count}; summarized={update.summarized_count}"
            )
        if update.summarized_count != 0:
            raise RuntimeError("RB-AGG unexpectedly invoked first-party trajectory summarization")
        if len(update.new_version_ids) != 1 or update.consumed_count != 8:
            raise RuntimeError("RB-AGG must mint exactly one version from eight precomputed summaries")
        post = await store.get_content(
            project_id=project_id,
            cloud_skill_id=root.cloud_skill_id,
            version_id=update.new_version_id,
        )
        skill_post_md = deserialize_bundle(post.content)["SKILL.md"]
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        temp_skill = skill_path.with_suffix(".md.tmp")
        temp_skill.write_text(skill_post_md, encoding="utf-8")
        os.replace(temp_skill, skill_path)
        adapter_receipts = llm_adapter.public_receipts()
        summary_rows = [
            {
                "summary_id": item.summary_id,
                "add_record_id": item.add_record_id,
                "task_id": item.task_id,
                "score": item.score,
                "summary_sha256": sha_text(item.summary),
                "consumed_version_id": item.consumed_version_id,
            }
            for item in sorted(post_existing.values(), key=lambda row: (str(row.task_id), row.summary_id))
        ]
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-rbagg-cloned-state-mindmemos-update",
            "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "status": "COMPLETED",
            "stream_id": stream_id,
            "semantic_role": "reasoningbank_style_precomputed_search_session_summaries_to_first_party_scored_patch",
            "mindmemos_commit": mindmemos_commit,
            "contract_sha256": contract_sha256,
            "authorization_sha256": authorization_sha256,
            "initial_skill_sha256": initial_skill_sha256,
            "summary_count": len(summary_rows),
            "new_first_party_trajectory_summaries": int(update.summarized_count),
            "precomputed_summary_consumed_count": int(update.consumed_count),
            "score_semantics": "search_session_best_of_k_acting_success_equal_to_win_winner_score",
            "provenance_rows": provenance_rows,
            "summaries": summary_rows,
            "evolved": bool(update.evolved),
            "new_version_ids": list(update.new_version_ids),
            "skill_post_path": str(skill_path.resolve()),
            "skill_post_sha256": sha_file(skill_path),
            "adapter_receipts": adapter_receipts,
            "mindmemos_provider_calls": len(adapter_receipts),
            "mindmemos_provider_total_tokens": sum(int(row.get("total_tokens") or 0) for row in adapter_receipts),
            "heldout_evaluations": 0,
            "scientific_effectiveness_evaluated": False,
        }
        temp_receipt = receipt_path.with_suffix(".json.tmp")
        temp_receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temp_receipt, receipt_path)
        return RBAggUpdateResult(
            stream_id=stream_id,
            update_receipt_path=str(receipt_path.resolve()),
            update_receipt_sha256=sha_file(receipt_path),
            skill_post_path=str(skill_path.resolve()),
            skill_post_sha256=sha_file(skill_path),
            evolved=bool(update.evolved),
            new_version_ids=tuple(update.new_version_ids),
            mindmemos_provider_calls=len(adapter_receipts),
            mindmemos_provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in adapter_receipts),
        )
    finally:
        await client.close()
