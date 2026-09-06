from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_mindmemos_updater import (
    BlindedEvidenceUnit,
    ProjectionUpdateResult,
    run_projection_update,
)
from research_pipeline.e2_r17_search_projection_runner import (
    ProjectionName,
    ProjectionPacket,
    SearchPool,
    project,
)

BRIDGE_FREE_PROJECTIONS = ("WINNER", "FIRST_FAIL_4")


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class BridgeUpdaterStream:
    """Bridge-specific carrier for the first-party blinded-evidence updater path.

    The packet tuple exists only to satisfy the already-qualified eight-pool
    topology interface of ``run_projection_update``.  In blinded mode the model
    receives only ``BlindedEvidenceUnit.evidence_text`` and selected score.  The
    scientific projection label is therefore kept separate from the historical
    ProjectionName enum so FIRST_FAIL_4 cannot be confused with the older
    all-mixed-pools MIXED_REJECTED_WITNESS treatment.
    """

    stream_id: str
    initial_skill_sha256: str
    pools: tuple[SearchPool, ...]
    packets: tuple[ProjectionPacket, ...]
    projection: str

    @property
    def stream_sha256(self) -> str:
        return canonical_sha256(
            {
                "schema": "E2-R17-BRIDGE-V4R2-UPDATER-STREAM-v1",
                "stream_id": self.stream_id,
                "initial_skill_sha256": self.initial_skill_sha256,
                "pool_ids": [pool.pool_id for pool in self.pools],
                "carrier_packet_sha256": [packet.packet_sha256 for packet in self.packets],
                "scientific_projection": self.projection,
                "model_visible_treatment_source": "BLINDED_EVIDENCE_UNITS_ONLY",
            }
        )


def build_bridge_updater_stream(
    *,
    stream_id: str,
    initial_skill_sha256: str,
    pools: Sequence[SearchPool],
    scientific_projection: str,
) -> BridgeUpdaterStream:
    if scientific_projection not in BRIDGE_FREE_PROJECTIONS:
        raise ValueError(f"unsupported Bridge FREE projection: {scientific_projection}")
    if len(initial_skill_sha256) != 64:
        raise ValueError("Bridge updater stream requires initial skill SHA-256")
    frozen = tuple(pools)
    if len(frozen) != 8 or len({pool.task_id for pool in frozen}) != 8:
        raise ValueError("Bridge updater stream requires eight distinct sealed task pools")
    for pool in frozen:
        pool.validate()
        if pool.k != 8:
            raise ValueError("Bridge updater stream pool K must equal 8")
        if pool.trajectories[0].skill_pre_sha256 != initial_skill_sha256:
            raise ValueError("Bridge updater pool was not generated from exact initial skill")
    carrier_packets = tuple(project(pool, ProjectionName.WINNER_ONLY) for pool in frozen)
    return BridgeUpdaterStream(
        stream_id=stream_id,
        initial_skill_sha256=initial_skill_sha256,
        pools=frozen,
        packets=carrier_packets,
        projection=scientific_projection,
    )


def validate_blinded_bridge_units(
    *,
    stream: BridgeUpdaterStream,
    units: Sequence[BlindedEvidenceUnit],
) -> None:
    if len(units) != 8:
        raise ValueError("Bridge FREE updater requires exactly eight blinded evidence units")
    for pool, unit in zip(stream.pools, units, strict=True):
        unit.validate()
        if (unit.task_id, unit.pool_id) != (pool.task_id, pool.pool_id):
            raise ValueError("Bridge updater evidence task/pool binding drift")
        if unit.acting_winner_sha256 != pool.winner.trajectory_sha256:
            raise ValueError("Bridge updater evidence changed served winner provenance")
        by_index = {row.rollout_index: row for row in pool.trajectories}
        source = by_index.get(unit.source_rollout_index)
        if source is None or source.trajectory_sha256 != unit.source_trajectory_sha256:
            raise ValueError("Bridge updater evidence source is outside sealed pool")
        if float(source.score) != float(unit.source_score):
            raise ValueError("Bridge updater selected-evidence score drift")


async def run_bridge_free_update(
    *,
    stream: BridgeUpdaterStream,
    pools: Sequence[SearchPool],
    blinded_evidence_units: Sequence[BlindedEvidenceUnit],
    initial_skill_md: str,
    run_dir: Path,
    llm_adapter: Any,
    mindmemos_commit: str,
    contract_sha256: str,
    authorization_sha256: str,
    transcript_max_chars: int,
) -> ProjectionUpdateResult:
    validate_blinded_bridge_units(stream=stream, units=blinded_evidence_units)
    if tuple(pool.pool_id for pool in pools) != tuple(pool.pool_id for pool in stream.pools):
        raise ValueError("Bridge updater supplied pools differ from stream carrier pools")
    result = await run_projection_update(
        stream=stream,  # type: ignore[arg-type] -- structural Bridge carrier, intentionally outside historical enum.
        pools=pools,
        initial_skill_md=initial_skill_md,
        run_dir=run_dir,
        llm_adapter=llm_adapter,
        mindmemos_commit=mindmemos_commit,
        contract_sha256=contract_sha256,
        authorization_sha256=authorization_sha256,
        transcript_max_chars=transcript_max_chars,
        blinded_evidence_units=blinded_evidence_units,
    )
    if result.projection != stream.projection:
        raise RuntimeError("Bridge updater receipt projection label drift")
    return result


__all__ = [
    "BRIDGE_FREE_PROJECTIONS",
    "BridgeUpdaterStream",
    "build_bridge_updater_stream",
    "validate_blinded_bridge_units",
    "run_bridge_free_update",
]
