from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Sequence

from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef

FF4_ALLOCATION_SALT = "E2-R17-BRIDGE-FF4-v1"
REQUIRED_POOLS = 8
REQUIRED_FF4_REPLACEMENTS = 4


class InsufficientMixedSupport(RuntimeError):
    pass


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class LearnerEvidenceUnit:
    stream_id: str
    pool_ordinal: int
    pool_id: str
    task_id: str
    served_winner_index: int
    served_winner_sha256: str
    served_winner_score: float
    learner_rollout_index: int
    learner_trajectory_sha256: str
    learner_score: float
    learner_role: str
    ff4_eligible_mixed_pool: bool
    ff4_allocation_sha256: str | None
    ff4_replaced: bool


@dataclass(frozen=True)
class LearnerEvidencePackage:
    stream_id: str
    projection: str
    allocation_salt: str
    pool_count: int
    mixed_pool_count: int
    ff4_replacement_count: int
    units: tuple[LearnerEvidenceUnit, ...]

    @property
    def package_sha256(self) -> str:
        return canonical_sha256(asdict(self))

    @property
    def learner_trajectory_sha256s(self) -> tuple[str, ...]:
        return tuple(unit.learner_trajectory_sha256 for unit in self.units)

    @property
    def served_winner_sha256s(self) -> tuple[str, ...]:
        return tuple(unit.served_winner_sha256 for unit in self.units)


def _validate_stream_pools(stream_id: str, pools: Sequence[SearchPool]) -> tuple[SearchPool, ...]:
    if not stream_id.strip():
        raise ValueError("stream_id must be non-empty")
    if len(pools) != REQUIRED_POOLS:
        raise ValueError("Bridge learner package requires exactly eight sealed pools")
    frozen = tuple(pools)
    seen_pool_ids: set[str] = set()
    seen_task_ids: set[str] = set()
    for pool in frozen:
        pool.validate()
        if pool.k != 8:
            raise ValueError("Bridge pool K must equal 8")
        if pool.pool_id in seen_pool_ids:
            raise ValueError("duplicate pool_id in Bridge stream")
        if pool.task_id in seen_task_ids:
            raise ValueError("duplicate task_id in Bridge stream")
        seen_pool_ids.add(pool.pool_id)
        seen_task_ids.add(pool.task_id)
    return frozen


def ff4_allocation_sha256(stream_id: str, pool_id: str) -> str:
    return hashlib.sha256(f"{FF4_ALLOCATION_SALT}|{stream_id}|{pool_id}".encode("utf-8")).hexdigest()


def ff4_selected_pool_ids(stream_id: str, pools: Sequence[SearchPool]) -> tuple[str, ...]:
    frozen = _validate_stream_pools(stream_id, pools)
    eligible = [pool for pool in frozen if pool.mixed_pool]
    if len(eligible) < REQUIRED_FF4_REPLACEMENTS:
        raise InsufficientMixedSupport(
            f"HOLD_INSUFFICIENT_MIXED_SUPPORT: {stream_id} has {len(eligible)} mixed pools; requires >=4"
        )
    ranked = sorted(
        eligible,
        key=lambda pool: (ff4_allocation_sha256(stream_id, pool.pool_id), pool.pool_id),
    )
    return tuple(pool.pool_id for pool in ranked[:REQUIRED_FF4_REPLACEMENTS])


def _unit(
    *,
    stream_id: str,
    pool_ordinal: int,
    pool: SearchPool,
    learner: TrajectoryRef,
    learner_role: str,
    replaced: bool,
) -> LearnerEvidenceUnit:
    winner = pool.winner
    return LearnerEvidenceUnit(
        stream_id=stream_id,
        pool_ordinal=pool_ordinal,
        pool_id=pool.pool_id,
        task_id=pool.task_id,
        served_winner_index=winner.rollout_index,
        served_winner_sha256=winner.trajectory_sha256,
        served_winner_score=winner.score,
        learner_rollout_index=learner.rollout_index,
        learner_trajectory_sha256=learner.trajectory_sha256,
        learner_score=learner.score,
        learner_role=learner_role,
        ff4_eligible_mixed_pool=pool.mixed_pool,
        ff4_allocation_sha256=ff4_allocation_sha256(stream_id, pool.pool_id) if pool.mixed_pool else None,
        ff4_replaced=replaced,
    )


def build_winner_package(stream_id: str, pools: Sequence[SearchPool]) -> LearnerEvidencePackage:
    frozen = _validate_stream_pools(stream_id, pools)
    units = tuple(
        _unit(
            stream_id=stream_id,
            pool_ordinal=index,
            pool=pool,
            learner=pool.winner,
            learner_role="served_winner",
            replaced=False,
        )
        for index, pool in enumerate(frozen)
    )
    return LearnerEvidencePackage(
        stream_id=stream_id,
        projection="WINNER",
        allocation_salt=FF4_ALLOCATION_SALT,
        pool_count=REQUIRED_POOLS,
        mixed_pool_count=sum(pool.mixed_pool for pool in frozen),
        ff4_replacement_count=0,
        units=units,
    )


def build_ff4_package(stream_id: str, pools: Sequence[SearchPool]) -> LearnerEvidencePackage:
    frozen = _validate_stream_pools(stream_id, pools)
    selected = set(ff4_selected_pool_ids(stream_id, frozen))
    units: list[LearnerEvidenceUnit] = []
    for index, pool in enumerate(frozen):
        if pool.pool_id in selected:
            learner = pool.first_failed_nonwinner
            role = "first_failed_nonwinner"
            replaced = True
        else:
            learner = pool.winner
            role = "served_winner_unchanged"
            replaced = False
        units.append(
            _unit(
                stream_id=stream_id,
                pool_ordinal=index,
                pool=pool,
                learner=learner,
                learner_role=role,
                replaced=replaced,
            )
        )
    package = LearnerEvidencePackage(
        stream_id=stream_id,
        projection="FIRST_FAIL_4",
        allocation_salt=FF4_ALLOCATION_SALT,
        pool_count=REQUIRED_POOLS,
        mixed_pool_count=sum(pool.mixed_pool for pool in frozen),
        ff4_replacement_count=sum(unit.ff4_replaced for unit in units),
        units=tuple(units),
    )
    if package.ff4_replacement_count != REQUIRED_FF4_REPLACEMENTS:
        raise RuntimeError("FF4 package must contain exactly four replacements")
    return package


def validate_paired_packages(
    winner: LearnerEvidencePackage,
    ff4: LearnerEvidencePackage,
) -> None:
    if winner.stream_id != ff4.stream_id:
        raise ValueError("paired Bridge packages must share stream_id")
    if winner.pool_count != REQUIRED_POOLS or ff4.pool_count != REQUIRED_POOLS:
        raise ValueError("paired Bridge packages must each contain exactly eight pools")
    if len(winner.units) != REQUIRED_POOLS or len(ff4.units) != REQUIRED_POOLS:
        raise ValueError("paired Bridge unit cardinality drift")
    if ff4.ff4_replacement_count != REQUIRED_FF4_REPLACEMENTS:
        raise ValueError("FF4 treatment dose drift")
    for w, f in zip(winner.units, ff4.units, strict=True):
        if (w.pool_ordinal, w.pool_id, w.task_id) != (f.pool_ordinal, f.pool_id, f.task_id):
            raise ValueError("paired Bridge pool order/identity drift")
        if (w.served_winner_index, w.served_winner_sha256, w.served_winner_score) != (
            f.served_winner_index,
            f.served_winner_sha256,
            f.served_winner_score,
        ):
            raise ValueError("FF4 learner projection changed served acting winner")
        if f.ff4_replaced:
            if not f.ff4_eligible_mixed_pool or f.learner_score != 0.0:
                raise ValueError("FF4 replacement is not a failed trajectory from a mixed pool")
        else:
            if f.learner_trajectory_sha256 != w.learner_trajectory_sha256:
                raise ValueError("unchanged FF4 pool does not retain Winner evidence")


__all__ = [
    "FF4_ALLOCATION_SALT",
    "REQUIRED_POOLS",
    "REQUIRED_FF4_REPLACEMENTS",
    "InsufficientMixedSupport",
    "LearnerEvidenceUnit",
    "LearnerEvidencePackage",
    "ff4_allocation_sha256",
    "ff4_selected_pool_ids",
    "build_winner_package",
    "build_ff4_package",
    "validate_paired_packages",
]
