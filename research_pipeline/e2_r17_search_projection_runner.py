from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Sequence


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class ProjectionName(StrEnum):
    WINNER_ONLY = "winner_only"
    PRECOMMITTED_ALWAYS = "precommitted_always"
    REJECTED_WITNESS = "rejected_witness"
    MIXED_REJECTED_WITNESS = "mixed_rejected_witness"
    DUPLICATED_WINNER = "duplicated_winner"
    WINNER_RANDOM_NONWINNER = "winner_random_nonwinner"
    SKILLCAT_STYLE_CONTRAST = "skillcat_style_contrast"


@dataclass(frozen=True)
class TrajectoryRef:
    task_id: str
    rollout_index: int
    score: float
    trajectory_path: str
    trajectory_sha256: str
    input_sha256: str
    prompt_sha256: str
    skill_pre_sha256: str
    verifier_sha256: str
    requested_model: str
    resolved_model: str
    provider_call_id_sha256: str
    evidence_tokens: int
    technical_status: str = "COMPLETED"
    failure_code: str | None = None
    provider_budget_unit_id: str | None = None
    provider_budget_claim_count: int = 0
    provider_budget_claim_bundle_sha256: str | None = None
    provider_budget_unit_claimed_after: int | None = None
    provider_budget_total_claimed_after: int | None = None

    def validate(self) -> None:
        if self.rollout_index < 0:
            raise ValueError("rollout_index must be non-negative")
        if self.score not in (0.0, 1.0):
            raise ValueError("R4 primary verifier score must be binary")
        if self.evidence_tokens < 0:
            raise ValueError("evidence_tokens must be non-negative")
        if self.technical_status != "COMPLETED":
            raise ValueError("technical-incomplete trajectories cannot enter a frozen pool")
        if self.provider_budget_claim_count < 0:
            raise ValueError("provider_budget_claim_count must be non-negative")
        if self.provider_budget_claim_count:
            if not self.provider_budget_unit_id:
                raise ValueError("provider_budget_unit_id is required when budget claims are present")
            if self.provider_budget_unit_claimed_after is None or self.provider_budget_unit_claimed_after < self.provider_budget_claim_count:
                raise ValueError("provider_budget_unit_claimed_after must cover this rollout's claims")
            if self.provider_budget_total_claimed_after is None or self.provider_budget_total_claimed_after < self.provider_budget_unit_claimed_after:
                raise ValueError("provider_budget_total_claimed_after must cover the unit claim count")
            digest = self.provider_budget_claim_bundle_sha256 or ""
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                raise ValueError("provider_budget_claim_bundle_sha256 must be a lowercase SHA-256 hex digest")
        for name in (
            "trajectory_sha256",
            "input_sha256",
            "prompt_sha256",
            "skill_pre_sha256",
            "verifier_sha256",
            "provider_call_id_sha256",
        ):
            value = getattr(self, name)
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise ValueError(f"{name} must be a lowercase SHA-256 hex digest")
        if not self.resolved_model:
            raise ValueError("resolved_model is required")


@dataclass(frozen=True)
class SearchPool:
    pool_id: str
    task_id: str
    k: int
    trajectories: tuple[TrajectoryRef, ...]
    search_topology: str = "parallel_best_of_k"

    def validate(self) -> None:
        if self.k < 1 or len(self.trajectories) != self.k:
            raise ValueError("pool cardinality must equal k")
        if self.search_topology != "parallel_best_of_k":
            raise ValueError("R4 primary pool topology is frozen to parallel_best_of_k")
        for trajectory in self.trajectories:
            trajectory.validate()
        indices = [trajectory.rollout_index for trajectory in self.trajectories]
        if indices != list(range(self.k)):
            raise ValueError("trajectory indices must be ordered and equal 0..k-1")
        invariant_fields = (
            "task_id",
            "input_sha256",
            "prompt_sha256",
            "skill_pre_sha256",
            "verifier_sha256",
            "requested_model",
            "resolved_model",
        )
        for field in invariant_fields:
            values = {getattr(trajectory, field) for trajectory in self.trajectories}
            if len(values) != 1:
                raise ValueError(f"pool invariant violated: {field}")
        if self.trajectories[0].task_id != self.task_id:
            raise ValueError("pool task_id does not match trajectories")
        expected_id = canonical_sha256(
            {
                "task_id": self.task_id,
                "k": self.k,
                "topology": self.search_topology,
                "trajectory_sha256": [trajectory.trajectory_sha256 for trajectory in self.trajectories],
            }
        )
        if self.pool_id != expected_id:
            raise ValueError("pool_id is not content-addressed to the exact pool")

    @classmethod
    def freeze(cls, trajectories: Sequence[TrajectoryRef]) -> "SearchPool":
        if not trajectories:
            raise ValueError("cannot freeze an empty pool")
        ordered = tuple(sorted(trajectories, key=lambda row: row.rollout_index))
        task_id = ordered[0].task_id
        k = len(ordered)
        pool_id = canonical_sha256(
            {
                "task_id": task_id,
                "k": k,
                "topology": "parallel_best_of_k",
                "trajectory_sha256": [trajectory.trajectory_sha256 for trajectory in ordered],
            }
        )
        pool = cls(pool_id=pool_id, task_id=task_id, k=k, trajectories=ordered)
        pool.validate()
        return pool

    @property
    def precommitted(self) -> TrajectoryRef:
        return self.trajectories[0]

    @property
    def winner(self) -> TrajectoryRef:
        # Frozen selector: maximum binary verifier score, then lowest rollout index.
        return min(self.trajectories, key=lambda row: (-row.score, row.rollout_index))

    @property
    def acting_success(self) -> float:
        return self.winner.score

    @property
    def precommitted_success(self) -> float:
        return self.precommitted.score

    @property
    def rescue_event(self) -> bool:
        return self.precommitted.score == 0.0 and self.winner.score == 1.0

    @property
    def rescue_censoring_mass(self) -> float:
        return float(self.rescue_event)

    @property
    def mixed_pool(self) -> bool:
        scores = {trajectory.score for trajectory in self.trajectories}
        return scores == {0.0, 1.0}

    @property
    def first_failed_nonwinner(self) -> TrajectoryRef:
        if not self.mixed_pool:
            raise ValueError("a failed non-winner exists only on mixed pools")
        failures = [
            trajectory
            for trajectory in self.trajectories
            if trajectory.score == 0.0 and trajectory.rollout_index != self.winner.rollout_index
        ]
        if not failures:
            raise ValueError("mixed pool does not contain a failed non-winner")
        return min(failures, key=lambda row: row.rollout_index)


@dataclass(frozen=True)
class EvidenceSlot:
    role: str
    rollout_index: int
    trajectory_sha256: str
    score: float
    trajectory_path: str
    evidence_tokens: int


@dataclass(frozen=True)
class ProjectionPacket:
    projection: ProjectionName
    pool_id: str
    task_id: str
    acting_winner_index: int
    acting_winner_sha256: str
    rescue_event: bool
    slots: tuple[EvidenceSlot, ...]
    rule_version: str
    randomization_salt: str | None = None

    @property
    def packet_sha256(self) -> str:
        return canonical_sha256(asdict(self))

    @property
    def selected_indices(self) -> tuple[int, ...]:
        return tuple(slot.rollout_index for slot in self.slots)

    @property
    def total_evidence_tokens(self) -> int:
        return sum(slot.evidence_tokens for slot in self.slots)


def _slot(role: str, trajectory: TrajectoryRef) -> EvidenceSlot:
    return EvidenceSlot(
        role=role,
        rollout_index=trajectory.rollout_index,
        trajectory_sha256=trajectory.trajectory_sha256,
        score=trajectory.score,
        trajectory_path=trajectory.trajectory_path,
        evidence_tokens=trajectory.evidence_tokens,
    )


def _random_nonwinner(pool: SearchPool, salt: str) -> TrajectoryRef:
    candidates = [trajectory for trajectory in pool.trajectories if trajectory.rollout_index != pool.winner.rollout_index]
    if not candidates:
        return pool.winner
    digest = hashlib.sha256(f"{salt}|{pool.pool_id}".encode("utf-8")).hexdigest()
    return candidates[int(digest[:16], 16) % len(candidates)]


def project(
    pool: SearchPool,
    projection: ProjectionName,
    *,
    randomization_salt: str = "e2-r17-r4-random-nonwinner-v1",
) -> ProjectionPacket:
    pool.validate()
    winner = pool.winner
    precommitted = pool.precommitted
    if projection is ProjectionName.WINNER_ONLY:
        slots = (_slot("served_winner", winner),)
        salt = None
    elif projection is ProjectionName.PRECOMMITTED_ALWAYS:
        slots = (_slot("precommitted_rollout_0", precommitted),)
        salt = None
    elif projection is ProjectionName.REJECTED_WITNESS:
        selected = precommitted if pool.rescue_event else winner
        role = "precommitted_rejected_failure" if pool.rescue_event else "served_winner_outside_rescue"
        slots = (_slot(role, selected),)
        salt = None
    elif projection is ProjectionName.MIXED_REJECTED_WITNESS:
        selected = pool.first_failed_nonwinner if pool.mixed_pool else winner
        role = "first_failed_nonwinner" if pool.mixed_pool else "served_winner_outside_mixed_pool"
        slots = (_slot(role, selected),)
        salt = None
    elif projection is ProjectionName.DUPLICATED_WINNER:
        slots = (_slot("served_winner_slot_1", winner), _slot("served_winner_slot_2", winner))
        salt = None
    elif projection is ProjectionName.WINNER_RANDOM_NONWINNER:
        random_nonwinner = _random_nonwinner(pool, randomization_salt)
        slots = (_slot("served_winner", winner), _slot("hash_selected_nonwinner", random_nonwinner))
        salt = randomization_salt
    elif projection is ProjectionName.SKILLCAT_STYLE_CONTRAST:
        # This freezes only the source trajectory pair. Any generated contrastive
        # summary is a downstream updater artifact and must retain both source SHAs.
        contrast = precommitted if pool.rescue_event else winner
        second_role = "precommitted_rejected_failure" if pool.rescue_event else "duplicated_winner_outside_rescue"
        slots = (_slot("served_winner", winner), _slot(second_role, contrast))
        salt = None
    else:  # pragma: no cover - StrEnum exhaustiveness guard
        raise ValueError(f"unsupported projection: {projection}")
    packet = ProjectionPacket(
        projection=projection,
        pool_id=pool.pool_id,
        task_id=pool.task_id,
        acting_winner_index=winner.rollout_index,
        acting_winner_sha256=winner.trajectory_sha256,
        rescue_event=pool.rescue_event,
        slots=slots,
        rule_version="E2-R17-R4-PROJECTION-V1",
        randomization_salt=salt,
    )
    validate_packet(pool, packet)
    return packet


def validate_packet(pool: SearchPool, packet: ProjectionPacket) -> None:
    pool.validate()
    if packet.pool_id != pool.pool_id or packet.task_id != pool.task_id:
        raise ValueError("projection packet is not bound to the exact pool")
    if packet.acting_winner_index != pool.winner.rollout_index:
        raise ValueError("acting winner changed across learning projections")
    if packet.acting_winner_sha256 != pool.winner.trajectory_sha256:
        raise ValueError("acting winner SHA changed across learning projections")
    if packet.rescue_event != pool.rescue_event:
        raise ValueError("rescue-event flag mismatch")
    by_index = {trajectory.rollout_index: trajectory for trajectory in pool.trajectories}
    for slot in packet.slots:
        source = by_index.get(slot.rollout_index)
        if source is None or source.trajectory_sha256 != slot.trajectory_sha256:
            raise ValueError("projection introduced evidence outside the frozen pool")
        if source.score != slot.score or source.trajectory_path != slot.trajectory_path:
            raise ValueError("projection slot altered source trajectory metadata")
    if packet.projection is ProjectionName.REJECTED_WITNESS:
        expected = pool.precommitted if pool.rescue_event else pool.winner
        if packet.selected_indices != (expected.rollout_index,):
            raise ValueError("Rejected-Witness violates its event-gated precommitment")
        if pool.rescue_event and not (packet.slots[0].score == 0.0 and pool.winner.score == 1.0):
            raise ValueError("Rejected-Witness must expose a rejected failure only on rescue events")
    if packet.projection is ProjectionName.MIXED_REJECTED_WITNESS:
        expected = pool.first_failed_nonwinner if pool.mixed_pool else pool.winner
        if packet.selected_indices != (expected.rollout_index,):
            raise ValueError("Mixed-Rejected-Witness violates its deterministic mixed-pool rule")
        if pool.mixed_pool and packet.slots[0].score != 0.0:
            raise ValueError("Mixed-Rejected-Witness must expose a failed non-winner on mixed pools")
    if packet.projection is ProjectionName.DUPLICATED_WINNER:
        expected = (pool.winner.rollout_index, pool.winner.rollout_index)
        if packet.selected_indices != expected:
            raise ValueError("duplicated-winner packet is not an exact duplicate")


def validate_primary_cloned_pair(pool: SearchPool, winner_packet: ProjectionPacket, witness_packet: ProjectionPacket) -> None:
    validate_packet(pool, winner_packet)
    validate_packet(pool, witness_packet)
    if winner_packet.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("first packet must be winner-only")
    if witness_packet.projection is not ProjectionName.REJECTED_WITNESS:
        raise ValueError("second packet must be Rejected-Witness")
    if winner_packet.pool_id != witness_packet.pool_id:
        raise ValueError("cloned pair does not use the exact same pool")
    if winner_packet.acting_winner_sha256 != witness_packet.acting_winner_sha256:
        raise ValueError("acting winner differs between cloned arms")
    if not pool.rescue_event and winner_packet.selected_indices != witness_packet.selected_indices:
        raise ValueError("g_RW must equal g_WIN outside the rescue event")
    if pool.rescue_event and winner_packet.selected_indices == witness_packet.selected_indices:
        raise ValueError("g_RW must differ from g_WIN on the rescue event")


@dataclass(frozen=True)
class StreamProjection:
    stream_id: str
    initial_skill_sha256: str
    pools: tuple[SearchPool, ...]
    packets: tuple[ProjectionPacket, ...]
    projection: ProjectionName

    @property
    def stream_sha256(self) -> str:
        return canonical_sha256(
            {
                "stream_id": self.stream_id,
                "initial_skill_sha256": self.initial_skill_sha256,
                "pool_ids": [pool.pool_id for pool in self.pools],
                "packet_sha256": [packet.packet_sha256 for packet in self.packets],
                "projection": self.projection,
            }
        )


def project_stream(
    *,
    stream_id: str,
    initial_skill_sha256: str,
    pools: Sequence[SearchPool],
    projection: ProjectionName,
) -> StreamProjection:
    if len(initial_skill_sha256) != 64:
        raise ValueError("initial skill SHA-256 is required")
    if len(pools) != 8:
        raise ValueError("MindMemOS R4 updater batch is frozen to exactly 8 task pools")
    if len({pool.task_id for pool in pools}) != 8:
        raise ValueError("one evolution stream must contain eight distinct tasks")
    if any(pool.trajectories[0].skill_pre_sha256 != initial_skill_sha256 for pool in pools):
        raise ValueError("all pools must be generated from the exact initial skill state")
    packets = tuple(project(pool, projection) for pool in pools)
    return StreamProjection(
        stream_id=stream_id,
        initial_skill_sha256=initial_skill_sha256,
        pools=tuple(pools),
        packets=packets,
        projection=projection,
    )


def validate_mixed_cloned_pair(pool: SearchPool, winner_packet: ProjectionPacket, witness_packet: ProjectionPacket) -> None:
    validate_packet(pool, winner_packet)
    validate_packet(pool, witness_packet)
    if winner_packet.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("first packet must be winner-only")
    if witness_packet.projection is not ProjectionName.MIXED_REJECTED_WITNESS:
        raise ValueError("second packet must be Mixed-Rejected-Witness")
    if winner_packet.pool_id != witness_packet.pool_id:
        raise ValueError("cloned pair does not use the exact same pool")
    if winner_packet.acting_winner_sha256 != witness_packet.acting_winner_sha256:
        raise ValueError("acting winner differs between cloned arms")
    if not pool.mixed_pool and winner_packet.selected_indices != witness_packet.selected_indices:
        raise ValueError("g_MRW must equal g_WIN outside the mixed-pool event")
    if pool.mixed_pool and winner_packet.selected_indices == witness_packet.selected_indices:
        raise ValueError("g_MRW must differ from g_WIN on the mixed-pool event")


def validate_cloned_streams(winner: StreamProjection, witness: StreamProjection) -> None:
    if winner.stream_id != witness.stream_id or winner.initial_skill_sha256 != witness.initial_skill_sha256:
        raise ValueError("cloned streams are not cloned from the same unit")
    if winner.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("winner stream projection mismatch")
    if witness.projection is not ProjectionName.REJECTED_WITNESS:
        raise ValueError("witness stream projection mismatch")
    if [pool.pool_id for pool in winner.pools] != [pool.pool_id for pool in witness.pools]:
        raise ValueError("cloned streams do not share exact pool IDs")
    for pool, win_packet, rw_packet in zip(winner.pools, winner.packets, witness.packets):
        validate_primary_cloned_pair(pool, win_packet, rw_packet)


def validate_mixed_cloned_streams(winner: StreamProjection, witness: StreamProjection) -> None:
    if winner.stream_id != witness.stream_id or winner.initial_skill_sha256 != witness.initial_skill_sha256:
        raise ValueError("cloned streams are not cloned from the same unit")
    if winner.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("winner stream projection mismatch")
    if witness.projection is not ProjectionName.MIXED_REJECTED_WITNESS:
        raise ValueError("mixed-witness stream projection mismatch")
    if [pool.pool_id for pool in winner.pools] != [pool.pool_id for pool in witness.pools]:
        raise ValueError("cloned streams do not share exact pool IDs")
    for pool, win_packet, rw_packet in zip(winner.pools, winner.packets, witness.packets):
        validate_mixed_cloned_pair(pool, win_packet, rw_packet)


def write_stream_receipt(path: Path, stream: StreamProjection) -> None:
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-search-projection-stream-receipt",
        "stream_id": stream.stream_id,
        "stream_sha256": stream.stream_sha256,
        "initial_skill_sha256": stream.initial_skill_sha256,
        "projection": stream.projection,
        "pool_ids": [pool.pool_id for pool in stream.pools],
        "packets": [asdict(packet) | {"packet_sha256": packet.packet_sha256} for packet in stream.packets],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def pools_from_jsonl(path: Path) -> tuple[SearchPool, ...]:
    pools: list[SearchPool] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        trajectories = tuple(TrajectoryRef(**row) for row in payload["trajectories"])
        pool = SearchPool(
            pool_id=payload["pool_id"],
            task_id=payload["task_id"],
            k=payload["k"],
            trajectories=trajectories,
            search_topology=payload.get("search_topology", "parallel_best_of_k"),
        )
        pool.validate()
        pools.append(pool)
    return tuple(pools)


def append_pool_jsonl(path: Path, pool: SearchPool) -> None:
    pool.validate()
    payload = {
        "pool_id": pool.pool_id,
        "task_id": pool.task_id,
        "k": pool.k,
        "search_topology": pool.search_topology,
        "trajectories": [asdict(row) for row in pool.trajectories],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
