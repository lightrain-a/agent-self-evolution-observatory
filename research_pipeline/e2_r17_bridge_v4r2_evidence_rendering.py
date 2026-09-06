from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_bridge_v4r2_evidence_package import (
    LearnerEvidencePackage,
    validate_paired_packages,
)
from research_pipeline.e2_r17_bridge_v4r2_state_materialization import SelectedEvidence, selected_evidence
from research_pipeline.e2_r17_evidence_window_v2 import (
    ExactMatchedEvidenceBlockRenderer,
    canonical_trajectory_text,
    sha256_text,
)
from research_pipeline.e2_r17_mindmemos_updater import BlindedEvidenceUnit, sha_file
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef

FORBIDDEN_MODEL_VISIBLE_MARKERS = (
    "WINNER",
    "FIRST_FAIL_4",
    "FF4",
    "W_COMP",
    "FF4_COMP",
    "W_FREE",
    "FF4_FREE",
    "PROJECTION:",
    "ACTING_WINNER",
    "POOL_ID:",
    "SOURCE_ROLLOUT_INDEX:",
    "SOURCE_TRAJECTORY_SHA256:",
)


@dataclass(frozen=True)
class RenderedPairReceipt:
    pool_ordinal: int
    pool_id: str
    task_id: str
    ff4_replaced: bool
    acting_winner_sha256: str
    winner_source_sha256: str
    ff4_source_sha256: str
    winner_selected_score: float
    ff4_selected_score: float
    winner_rendered_sha256: str
    ff4_rendered_sha256: str
    matched_final_block_tokens: int
    unchanged_pool_byte_identical: bool
    parity_receipt: dict[str, Any]


@dataclass(frozen=True)
class RenderedBridgeEvidence:
    stream_id: str
    winner_package_sha256: str
    ff4_package_sha256: str
    winner_free_units: tuple[BlindedEvidenceUnit, ...]
    ff4_free_units: tuple[BlindedEvidenceUnit, ...]
    winner_compiler_units: tuple[SelectedEvidence, ...]
    ff4_compiler_units: tuple[SelectedEvidence, ...]
    pair_receipts: tuple[RenderedPairReceipt, ...]

    @property
    def receipt_sha256(self) -> str:
        payload = {
            "stream_id": self.stream_id,
            "winner_package_sha256": self.winner_package_sha256,
            "ff4_package_sha256": self.ff4_package_sha256,
            "winner_free": [
                {
                    "task_id": u.task_id,
                    "pool_id": u.pool_id,
                    "acting_winner_sha256": u.acting_winner_sha256,
                    "source_rollout_index": u.source_rollout_index,
                    "source_trajectory_sha256": u.source_trajectory_sha256,
                    "source_score": u.source_score,
                    "evidence_sha256": u.evidence_sha256,
                    "evidence_tokens": u.evidence_tokens,
                }
                for u in self.winner_free_units
            ],
            "ff4_free": [
                {
                    "task_id": u.task_id,
                    "pool_id": u.pool_id,
                    "acting_winner_sha256": u.acting_winner_sha256,
                    "source_rollout_index": u.source_rollout_index,
                    "source_trajectory_sha256": u.source_trajectory_sha256,
                    "source_score": u.source_score,
                    "evidence_sha256": u.evidence_sha256,
                    "evidence_tokens": u.evidence_tokens,
                }
                for u in self.ff4_free_units
            ],
            "pair_receipts": [asdict(row) for row in self.pair_receipts],
        }
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


def _trajectory_ref(pool: SearchPool, *, rollout_index: int, trajectory_sha256: str) -> TrajectoryRef:
    matches = [
        row
        for row in pool.trajectories
        if row.rollout_index == rollout_index and row.trajectory_sha256 == trajectory_sha256
    ]
    if len(matches) != 1:
        raise RuntimeError("selected learner trajectory is not uniquely bound to sealed pool")
    return matches[0]


def _canonical_source(ref: TrajectoryRef) -> str:
    path = Path(ref.trajectory_path)
    if not path.is_file() or sha_file(path) != ref.trajectory_sha256:
        raise RuntimeError(f"Bridge trajectory file/SHA drift: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if str(payload.get("case_id")) != ref.task_id:
        raise RuntimeError("Bridge trajectory case_id/task_id drift")
    if int(payload.get("rollout_index")) != ref.rollout_index:
        raise RuntimeError("Bridge trajectory rollout_index drift")
    if float(payload.get("score")) != ref.score:
        raise RuntimeError("Bridge trajectory verifier score drift")
    return canonical_trajectory_text(payload)


def _blinded_unit(
    *,
    pool: SearchPool,
    ref: TrajectoryRef,
    rendered: str,
    evidence_tokens: int,
) -> BlindedEvidenceUnit:
    unit = BlindedEvidenceUnit(
        task_id=pool.task_id,
        pool_id=pool.pool_id,
        acting_winner_sha256=pool.winner.trajectory_sha256,
        source_rollout_index=ref.rollout_index,
        source_trajectory_sha256=ref.trajectory_sha256,
        source_score=float(ref.score),
        evidence_text=rendered,
        evidence_sha256=sha256_text(rendered),
        evidence_tokens=int(evidence_tokens),
    )
    unit.validate()
    return unit


def render_paired_packages(
    *,
    pools: Sequence[SearchPool],
    winner_package: LearnerEvidencePackage,
    ff4_package: LearnerEvidencePackage,
    final_block_cap_tokens: int = 3072,
) -> RenderedBridgeEvidence:
    validate_paired_packages(winner_package, ff4_package)
    if len(pools) != 8:
        raise ValueError("Bridge rendering requires exactly eight sealed pools")
    if tuple(pool.pool_id for pool in pools) != tuple(unit.pool_id for unit in winner_package.units):
        raise ValueError("Bridge rendered pool order differs from frozen learner package order")

    renderer = ExactMatchedEvidenceBlockRenderer(final_block_cap_tokens=final_block_cap_tokens)
    winner_free: list[BlindedEvidenceUnit] = []
    ff4_free: list[BlindedEvidenceUnit] = []
    winner_compiler: list[SelectedEvidence] = []
    ff4_compiler: list[SelectedEvidence] = []
    receipts: list[RenderedPairReceipt] = []

    for index, (pool, w_unit, f_unit) in enumerate(
        zip(pools, winner_package.units, ff4_package.units, strict=True)
    ):
        pool.validate()
        if index != w_unit.pool_ordinal or index != f_unit.pool_ordinal:
            raise ValueError("Bridge pool ordinal drift")
        w_ref = _trajectory_ref(
            pool,
            rollout_index=w_unit.learner_rollout_index,
            trajectory_sha256=w_unit.learner_trajectory_sha256,
        )
        f_ref = _trajectory_ref(
            pool,
            rollout_index=f_unit.learner_rollout_index,
            trajectory_sha256=f_unit.learner_trajectory_sha256,
        )
        w_source = _canonical_source(w_ref)
        f_source = _canonical_source(f_ref)
        w_block, f_block, parity = renderer.render_pair(w_source, f_source)
        w_tokens = len(renderer.encoding.encode(w_block))
        f_tokens = len(renderer.encoding.encode(f_block))
        if w_tokens != f_tokens or w_tokens != parity.matched_final_block_tokens:
            raise RuntimeError("Bridge W/FF4 provider-visible token parity drift")
        if not f_unit.ff4_replaced and w_block != f_block:
            raise RuntimeError("unchanged Bridge W/FF4 pool is not byte-identical after rendering")
        for visible in (w_block, f_block):
            if any(marker in visible for marker in FORBIDDEN_MODEL_VISIBLE_MARKERS):
                raise RuntimeError("Bridge treatment/provenance marker leaked into model-visible evidence")

        w_blind = _blinded_unit(pool=pool, ref=w_ref, rendered=w_block, evidence_tokens=w_tokens)
        f_blind = _blinded_unit(pool=pool, ref=f_ref, rendered=f_block, evidence_tokens=f_tokens)
        w_comp = selected_evidence(w_block, w_ref.score)
        f_comp = selected_evidence(f_block, f_ref.score)

        # Information parity is load-bearing: both generator mechanisms consume
        # the same bytes and selected-evidence score within an evidence-source cell.
        if w_blind.evidence_text != w_comp.evidence_text or w_blind.source_score != w_comp.selected_score:
            raise RuntimeError("Winner FREE/COMP information parity drift")
        if f_blind.evidence_text != f_comp.evidence_text or f_blind.source_score != f_comp.selected_score:
            raise RuntimeError("FF4 FREE/COMP information parity drift")
        if w_blind.acting_winner_sha256 != f_blind.acting_winner_sha256:
            raise RuntimeError("Bridge evidence rendering changed served acting winner")

        winner_free.append(w_blind)
        ff4_free.append(f_blind)
        winner_compiler.append(w_comp)
        ff4_compiler.append(f_comp)
        receipts.append(
            RenderedPairReceipt(
                pool_ordinal=index,
                pool_id=pool.pool_id,
                task_id=pool.task_id,
                ff4_replaced=f_unit.ff4_replaced,
                acting_winner_sha256=pool.winner.trajectory_sha256,
                winner_source_sha256=w_ref.trajectory_sha256,
                ff4_source_sha256=f_ref.trajectory_sha256,
                winner_selected_score=float(w_ref.score),
                ff4_selected_score=float(f_ref.score),
                winner_rendered_sha256=sha256_text(w_block),
                ff4_rendered_sha256=sha256_text(f_block),
                matched_final_block_tokens=w_tokens,
                unchanged_pool_byte_identical=(w_block == f_block),
                parity_receipt=parity.to_dict(),
            )
        )

    rendered = RenderedBridgeEvidence(
        stream_id=winner_package.stream_id,
        winner_package_sha256=winner_package.package_sha256,
        ff4_package_sha256=ff4_package.package_sha256,
        winner_free_units=tuple(winner_free),
        ff4_free_units=tuple(ff4_free),
        winner_compiler_units=tuple(winner_compiler),
        ff4_compiler_units=tuple(ff4_compiler),
        pair_receipts=tuple(receipts),
    )
    if sum(row.ff4_replaced for row in rendered.pair_receipts) != 4:
        raise RuntimeError("Bridge rendered FF4 replacement dose drift")
    return rendered


__all__ = [
    "FORBIDDEN_MODEL_VISIBLE_MARKERS",
    "RenderedPairReceipt",
    "RenderedBridgeEvidence",
    "render_paired_packages",
]
