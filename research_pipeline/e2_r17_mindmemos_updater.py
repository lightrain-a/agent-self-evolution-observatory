from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_search_projection_runner import ProjectionPacket, SearchPool, StreamProjection

_ID_NAMESPACE = uuid.UUID("8a1cab2c-aef8-4eb6-bcdf-21a88b4e2f17")


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha(payload: Any) -> str:
    return sha_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _truncate_middle(text: str, limit: int) -> str:
    if limit <= 0 or len(text) <= limit:
        return text
    marker = f"\n...[{len(text) - limit} chars deterministically elided]...\n"
    usable = max(0, limit - len(marker))
    head = usable // 2
    tail = usable - head
    return text[:head] + marker + text[-tail:]


def render_trajectory_evidence(path: Path, expected_sha256: str, *, char_budget: int = 6000) -> str:
    if sha_file(path) != expected_sha256:
        raise RuntimeError(f"trajectory SHA mismatch: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    lines = [
        f"TASK_ID: {payload['case_id']}",
        f"ROLLOUT_INDEX: {payload['rollout_index']}",
        f"VERIFIER_SCORE: {payload['score']}",
        f"VERIFIER_MESSAGE: {payload.get('score_message', '')}",
        "TRAJECTORY:",
    ]
    for message in payload.get("messages") or []:
        role = str(message.get("role") or "unknown").upper()
        content = message.get("content")
        if content:
            lines.append(f"[{role}] {content}")
        for call in message.get("tool_calls") or []:
            function = call.get("function") or {}
            lines.append(
                f"[ASSISTANT_TOOL_CALL name={function.get('name', '')}] {function.get('arguments', '{}')}"
            )
        if role == "TOOL":
            lines.append(
                f"[TOOL_BINDING id={message.get('tool_call_id', '')} name={message.get('name', '')}]"
            )
    return _truncate_middle("\n".join(lines), char_budget)


def render_projection_packet(
    pool: SearchPool,
    packet: ProjectionPacket,
    *,
    slot_char_budget: int = 6000,
) -> tuple[str, dict[str, Any]]:
    pool.validate()
    sections = [
        "E2-R17 LEARNING PROJECTION PACKET",
        f"PROJECTION: {packet.projection}",
        f"TASK_ID: {packet.task_id}",
        f"POOL_ID: {packet.pool_id}",
        f"ACTING_WINNER_INDEX: {packet.acting_winner_index}",
        f"ACTING_WINNER_SHA256: {packet.acting_winner_sha256}",
        f"RESCUE_EVENT: {str(packet.rescue_event).lower()}",
        "The user-facing acting outcome is fixed by the acting winner above. The following slots are the only evidence exposed to the persistent updater.",
    ]
    slot_rows: list[dict[str, Any]] = []
    for slot_index, slot in enumerate(packet.slots):
        evidence = render_trajectory_evidence(
            Path(slot.trajectory_path), slot.trajectory_sha256, char_budget=slot_char_budget
        )
        sections.extend(
            [
                f"\n--- EVIDENCE SLOT {slot_index} ---",
                f"ROLE: {slot.role}",
                f"SOURCE_ROLLOUT_INDEX: {slot.rollout_index}",
                f"SOURCE_TRAJECTORY_SHA256: {slot.trajectory_sha256}",
                f"SOURCE_VERIFIER_SCORE: {slot.score}",
                evidence,
            ]
        )
        slot_rows.append(
            {
                "slot_index": slot_index,
                "role": slot.role,
                "rollout_index": slot.rollout_index,
                "trajectory_sha256": slot.trajectory_sha256,
                "score": slot.score,
                "rendered_chars": len(evidence),
                "rendered_sha256": sha_text(evidence),
            }
        )
    text = "\n".join(sections)
    metadata = {
        "packet_sha256": packet.packet_sha256,
        "projection": str(packet.projection),
        "pool_id": packet.pool_id,
        "task_id": packet.task_id,
        "acting_score": pool.acting_success,
        "rescue_event": packet.rescue_event,
        "rendered_packet_sha256": sha_text(text),
        "rendered_packet_chars": len(text),
        "slots": slot_rows,
    }
    return text, metadata


@dataclass(frozen=True)
class BlindedEvidenceUnit:
    """One pre-rendered learner-visible evidence unit for the V3.1 causal path.

    Projection/arm identity and source provenance remain available to the experiment
    receipt, but ``evidence_text`` is the only trajectory text placed in the
    first-party MindMemOS add-record ``messages`` field. ``source_score`` is the
    verifier score of that selected evidence trajectory, not the served acting
    winner score.
    """

    task_id: str
    pool_id: str
    acting_winner_sha256: str
    source_rollout_index: int
    source_trajectory_sha256: str
    source_score: float
    evidence_text: str
    evidence_sha256: str
    evidence_tokens: int

    def validate(self) -> None:
        if not self.task_id or not self.pool_id:
            raise ValueError("blinded evidence must bind task_id and pool_id")
        if self.source_rollout_index < 0:
            raise ValueError("source_rollout_index must be nonnegative")
        if sha_text(self.evidence_text) != self.evidence_sha256:
            raise ValueError("blinded evidence SHA mismatch")
        if self.evidence_tokens <= 0:
            raise ValueError("blinded evidence token count must be positive")


def build_blinded_add_record_payload(
    *,
    unit: BlindedEvidenceUnit,
    pool: SearchPool,
    project_id: str,
    task_completed_at: str,
    initial_skill_sha256: str,
    root_version_id: str,
    projection_label: str,
) -> dict[str, Any]:
    """Build the first-party add-record payload for V3.1 without treatment-label leakage.

    At pinned MindMemOS commit 9049182..., ``SkillEvolver`` constructs the LLM
    transcript from ``payload['messages']`` and obtains the scored-patch label from
    ``payload['score']``. The ``r17_*`` fields below are provenance-only and are
    intentionally absent from model-visible messages.
    """
    unit.validate()
    pool.validate()
    if unit.task_id != pool.task_id or unit.pool_id != pool.pool_id:
        raise ValueError("blinded evidence task/pool binding mismatch")
    if unit.acting_winner_sha256 != pool.winner.trajectory_sha256:
        raise ValueError("blinded evidence acting-winner provenance mismatch")
    return {
        "project_id": project_id,
        "task_completed_at": task_completed_at,
        "messages": [{"role": "user", "content": unit.evidence_text}],
        "score": float(unit.source_score),
        "task_id": pool.task_id,
        "skill_bindings": [
            {
                "name": "xlsx",
                "content_hash": initial_skill_sha256,
                "version_id": root_version_id,
                "usage": "injected",
            }
        ],
        "r17_projection": projection_label,
        "r17_rendered_packet_sha256": unit.evidence_sha256,
        "r17_pool_id": pool.pool_id,
        "r17_rescue_event": pool.rescue_event,
        "r17_acting_score": pool.acting_success,
        "r17_acting_winner_sha256": unit.acting_winner_sha256,
        "r17_source_rollout_index": unit.source_rollout_index,
        "r17_source_trajectory_sha256": unit.source_trajectory_sha256,
        "r17_selected_evidence_score": float(unit.source_score),
        "r17_evidence_tokens": int(unit.evidence_tokens),
    }


@dataclass(frozen=True)
class ProjectionUpdateResult:
    stream_id: str
    projection: str
    update_receipt_path: str
    update_receipt_sha256: str
    skill_post_path: str
    skill_post_sha256: str
    evolved: bool
    new_version_ids: tuple[str, ...]
    provider_calls: int
    provider_total_tokens: int


def _trace_uuid(stream_id: str, projection: str, task_id: str) -> str:
    return str(uuid.uuid5(_ID_NAMESPACE, f"{stream_id}|{projection}|{task_id}"))


async def run_projection_update(
    *,
    stream: StreamProjection,
    pools: Sequence[SearchPool],
    initial_skill_md: str,
    run_dir: Path,
    llm_adapter: Any,
    mindmemos_commit: str,
    contract_sha256: str,
    authorization_sha256: str,
    slot_char_budget: int = 6000,
    transcript_max_chars: int = 16000,
    blinded_evidence_units: Sequence[BlindedEvidenceUnit] | None = None,
) -> ProjectionUpdateResult:
    """Run one cloned MindMemOS SkillEvolver update from eight projected task packets.

    ``blinded_evidence_units`` activates the V3.1 causal-purity path. In that mode
    the first-party updater receives only the pre-rendered arm-blinded evidence
    text plus the selected evidence trajectory's verifier score. Acting winner,
    projection label, rollout index and SHA provenance remain database/receipt
    metadata and are not placed in the model-visible transcript.
    """

    if len(stream.packets) != 8 or len(pools) != 8:
        raise ValueError("one E2-R17 update unit must contain exactly eight task pools")
    if [pool.pool_id for pool in pools] != [pool.pool_id for pool in stream.pools]:
        raise ValueError("stream pools differ from supplied exact pools")
    run_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = run_dir / "update_receipt.json"
    skill_path = run_dir / "skill_post" / "SKILL.md"
    if receipt_path.exists() and skill_path.exists():
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        if sha_file(skill_path) != payload.get("skill_post_sha256"):
            raise RuntimeError("existing updater receipt failed skill content-address check")
        return ProjectionUpdateResult(
            stream_id=stream.stream_id,
            projection=str(stream.projection),
            update_receipt_path=str(receipt_path.resolve()),
            update_receipt_sha256=sha_file(receipt_path),
            skill_post_path=str(skill_path.resolve()),
            skill_post_sha256=sha_file(skill_path),
            evolved=bool(payload.get("evolved")),
            new_version_ids=tuple(payload.get("new_version_ids") or []),
            provider_calls=len(payload.get("adapter_receipts") or []),
            provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in payload.get("adapter_receipts") or []),
        )

    # Imports remain inside the function so the caller can bind the exact
    # MindMemOS source tree before loading this module.
    from mindmemos.components.skill import deserialize_bundle, serialize_bundle
    from mindmemos.config import QdrantConfig, SkillEvolutionConfig
    from mindmemos.infra.db import SkillVersionRepository
    from mindmemos.infra.db.models import AddRecordPoint
    from mindmemos.infra.db.qdrant import QdrantStore
    from mindmemos.pipelines.skill import SkillVersionStore
    from mindmemos.pipelines.skill import evolution as evolution_module
    from mindmemos.pipelines.skill.evolution import SkillEvolver
    from qdrant_client import AsyncQdrantClient

    packet_rows: list[dict[str, Any]] = []
    rendered_packets: list[tuple[str, dict[str, Any]]] = []
    blinded_rows: list[BlindedEvidenceUnit] | None = None
    if blinded_evidence_units is not None:
        blinded_rows = list(blinded_evidence_units)
        if len(blinded_rows) != len(pools):
            raise ValueError("blinded evidence cardinality must match the eight exact pools")
        for pool, unit in zip(pools, blinded_rows):
            unit.validate()
            if unit.task_id != pool.task_id or unit.pool_id != pool.pool_id:
                raise ValueError("blinded evidence task/pool binding mismatch")
            if unit.acting_winner_sha256 != pool.winner.trajectory_sha256:
                raise ValueError("blinded evidence acting-winner provenance mismatch")
            if len(f"[user] {unit.evidence_text}") > transcript_max_chars:
                raise ValueError("blinded evidence would be silently truncated by first-party transcript renderer")
            metadata = {
                "packet_sha256": sha_text(unit.evidence_text),
                "projection": str(stream.projection),
                "pool_id": unit.pool_id,
                "task_id": unit.task_id,
                "acting_score": pool.acting_success,
                "acting_winner_sha256": unit.acting_winner_sha256,
                "source_rollout_index": unit.source_rollout_index,
                "source_trajectory_sha256": unit.source_trajectory_sha256,
                "source_score": unit.source_score,
                "rendered_packet_sha256": unit.evidence_sha256,
                "rendered_packet_chars": len(unit.evidence_text),
                "rendered_packet_tokens": unit.evidence_tokens,
                "arm_metadata_visible": False,
                "score_semantics": "selected_evidence_trajectory",
            }
            rendered_packets.append((unit.evidence_text, metadata))
            packet_rows.append(metadata)
    else:
        for pool, packet in zip(pools, stream.packets):
            text, metadata = render_projection_packet(pool, packet, slot_char_budget=slot_char_budget)
            rendered_packets.append((text, metadata))
            packet_rows.append(metadata)

    client = AsyncQdrantClient(":memory:")
    qdrant_cfg = QdrantConfig(
        url="http://unused",
        add_record_collection="r17_add_record",
        skill_version_collection="r17_skill_version",
        skill_blob_collection="r17_skill_blob",
        skill_trace_pending_collection="r17_skill_trace_pending",
        skill_trace_summary_collection="r17_skill_trace_summary",
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
    project_id = f"e2-r17-{stream.stream_id}-{stream.projection}"
    root = await store.register(
        project_id=project_id,
        name="xlsx",
        content=serialize_bundle({"SKILL.md": initial_skill_md}),
    )
    base_time = datetime(2026, 8, 28, tzinfo=UTC)
    for index, ((packet_text, packet_meta), pool) in enumerate(zip(rendered_packets, pools)):
        selected_score = (
            float(blinded_rows[index].source_score)
            if blinded_rows is not None
            else float(pool.acting_success)
        )
        if blinded_rows is not None:
            payload = build_blinded_add_record_payload(
                unit=blinded_rows[index],
                pool=pool,
                project_id=project_id,
                task_completed_at=(base_time + timedelta(minutes=index)).isoformat(),
                initial_skill_sha256=stream.initial_skill_sha256,
                root_version_id=root.version_id,
                projection_label=str(stream.projection),
            )
            if float(payload["score"]) != selected_score:
                raise AssertionError("V3.1 selected-evidence score serialization drift")
        else:
            payload = {
                "project_id": project_id,
                "task_completed_at": (base_time + timedelta(minutes=index)).isoformat(),
                "messages": [{"role": "user", "content": packet_text}],
                "score": selected_score,
                "task_id": pool.task_id,
                "skill_bindings": [
                    {
                        "name": "xlsx",
                        "content_hash": stream.initial_skill_sha256,
                        "version_id": root.version_id,
                        "usage": "injected",
                    }
                ],
                "r17_projection": str(stream.projection),
                "r17_projection_packet_sha256": packet_meta["packet_sha256"],
                "r17_rendered_packet_sha256": packet_meta["rendered_packet_sha256"],
                "r17_pool_id": pool.pool_id,
                "r17_rescue_event": pool.rescue_event,
            }
        await qdrant.upsert_add_record(
            AddRecordPoint(
                add_record_id=_trace_uuid(stream.stream_id, str(stream.projection), pool.task_id),
                payload=payload,
            )
        )

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
        summaries = await evolver._existing_summaries(project_id, root.cloud_skill_id)
    finally:
        evolution_module.get_config = original_get_config

    try:
        if not update.evolved or not update.new_version_id:
            raise RuntimeError(
                f"first-party SkillEvolver did not mint a version: pending={update.pending_count}; "
                f"summarized={update.summarized_count}"
            )
        if len(update.new_version_ids) != 1 or update.consumed_count != 8:
            raise RuntimeError("R17 frozen updater must mint exactly one version from eight task packets")
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
                "summary": item.summary,
                "summary_sha256": sha_text(item.summary),
                "consumed_version_id": item.consumed_version_id,
            }
            for item in sorted(summaries.values(), key=lambda row: (str(row.task_id), row.summary_id))
        ]
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-cloned-state-mindmemos-update",
            "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "status": "COMPLETED",
            "stream_id": stream.stream_id,
            "stream_sha256": stream.stream_sha256,
            "projection": str(stream.projection),
            "initial_skill_sha256": stream.initial_skill_sha256,
            "skill_post_path": str(skill_path.resolve()),
            "skill_post_sha256": sha_file(skill_path),
            "mindmemos_commit": mindmemos_commit,
            "first_party_updater": "mindmemos.pipelines.skill.evolution.SkillEvolver",
            "updater_config": asdict(frozen_cfg),
            "project_id": project_id,
            "root_version_id": root.version_id,
            "cloud_skill_id": root.cloud_skill_id,
            "evolved": update.evolved,
            "new_version_id": update.new_version_id,
            "new_version_ids": update.new_version_ids,
            "summarized_count": update.summarized_count,
            "consumed_count": update.consumed_count,
            "pending_count": update.pending_count,
            "packets": packet_rows,
            "summaries": summary_rows,
            "adapter_receipts": adapter_receipts,
            "adapter_receipt_bundle_sha256": llm_adapter.receipt_bundle_sha256,
            "contract_sha256": contract_sha256,
            "authorization_sha256": authorization_sha256,
            "provider_retry_limit": 0,
            "hidden_provider_retry_used": False,
            "causal_purity_mode": "arm_blinded_selected_evidence" if blinded_rows is not None else "legacy_projection_packet",
            "updater_visible_score_semantics": "selected_evidence_trajectory" if blinded_rows is not None else "served_acting_outcome_legacy",
            "arm_metadata_visible_in_transcript": False if blinded_rows is not None else True,
            "private_credentials_included": False,
            "raw_response_ids_included": False,
        }
        atomic_json(receipt_path, payload)
    finally:
        await client.close()

    return ProjectionUpdateResult(
        stream_id=stream.stream_id,
        projection=str(stream.projection),
        update_receipt_path=str(receipt_path.resolve()),
        update_receipt_sha256=sha_file(receipt_path),
        skill_post_path=str(skill_path.resolve()),
        skill_post_sha256=sha_file(skill_path),
        evolved=True,
        new_version_ids=tuple(update.new_version_ids),
        provider_calls=len(adapter_receipts),
        provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in adapter_receipts),
    )


__all__ = [
    "BlindedEvidenceUnit",
    "build_blinded_add_record_payload",
    "ProjectionUpdateResult",
    "render_projection_packet",
    "render_trajectory_evidence",
    "run_projection_update",
]
