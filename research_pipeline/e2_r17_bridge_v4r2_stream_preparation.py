from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Sequence

from research_pipeline.e2_r17_bridge_v4r2_evidence_package import (
    LearnerEvidencePackage,
    build_ff4_package,
    build_winner_package,
    validate_paired_packages,
)
from research_pipeline.e2_r17_bridge_v4r2_evidence_rendering import (
    RenderedBridgeEvidence,
    render_paired_packages,
)
from research_pipeline.e2_r17_bridge_v4r2_state_materialization import (
    canonical_selected_scores,
    compile_comp_state,
    compile_scope_matched_control,
    compile_score_only_control,
    compiler_scope,
)
from research_pipeline.e2_r17_bridge_v4r2_updater_binding import (
    BridgeUpdaterStream,
    build_bridge_updater_stream,
    validate_blinded_bridge_units,
)
from research_pipeline.e2_r17_search_projection_runner import SearchPool
from research_pipeline.e2_r17_state_compiler_bridge import CompiledState

STREAM_ARMS = (
    "W_FREE",
    "W_COMP",
    "FF4_FREE",
    "FF4_COMP",
    "SCORE_ONLY_GENERIC_MAX",
    "SCOPE_MATCHED_GENERIC_MAX",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class BridgeV4R2StreamPreparation:
    stream_id: str
    initial_skill_sha256: str
    winner_package: LearnerEvidencePackage
    ff4_package: LearnerEvidencePackage
    rendered: RenderedBridgeEvidence
    winner_updater_stream: BridgeUpdaterStream
    ff4_updater_stream: BridgeUpdaterStream
    w_comp: CompiledState
    ff4_comp: CompiledState
    score_only_generic: CompiledState
    scope_matched_generic: CompiledState
    ff4_compiler_scope: int

    @property
    def state_sha256_by_deterministic_arm(self) -> dict[str, str]:
        return {
            "W_COMP": self.w_comp.skill_sha256,
            "FF4_COMP": self.ff4_comp.skill_sha256,
            "SCORE_ONLY_GENERIC_MAX": self.score_only_generic.skill_sha256,
            "SCOPE_MATCHED_GENERIC_MAX": self.scope_matched_generic.skill_sha256,
        }

    @property
    def preparation_sha256(self) -> str:
        return canonical_sha256(
            {
                "schema": "E2-R17-BRIDGE-V4R2-STREAM-PREPARATION-v1",
                "stream_id": self.stream_id,
                "initial_skill_sha256": self.initial_skill_sha256,
                "winner_package_sha256": self.winner_package.package_sha256,
                "ff4_package_sha256": self.ff4_package.package_sha256,
                "rendered_receipt_sha256": self.rendered.receipt_sha256,
                "winner_updater_stream_sha256": self.winner_updater_stream.stream_sha256,
                "ff4_updater_stream_sha256": self.ff4_updater_stream.stream_sha256,
                "deterministic_state_sha256": self.state_sha256_by_deterministic_arm,
                "ff4_compiler_scope": self.ff4_compiler_scope,
                "winner_selected_scores": list(canonical_selected_scores(self.rendered.winner_compiler_units)),
                "ff4_selected_scores": list(canonical_selected_scores(self.rendered.ff4_compiler_units)),
            }
        )


def prepare_stream_from_sealed_pools(
    *,
    stream_id: str,
    pools: Sequence[SearchPool],
    initial_skill_markdown: str,
    initial_skill_sha256: str,
    final_block_cap_tokens: int = 3072,
) -> BridgeV4R2StreamPreparation:
    if sha256_text(initial_skill_markdown) != initial_skill_sha256:
        raise ValueError("Bridge initial skill bytes/SHA drift")
    frozen = tuple(pools)
    if len(frozen) != 8:
        raise ValueError("Bridge integrated stream preparation requires exactly eight sealed pools")

    winner = build_winner_package(stream_id, frozen)
    ff4 = build_ff4_package(stream_id, frozen)
    validate_paired_packages(winner, ff4)
    rendered = render_paired_packages(
        pools=frozen,
        winner_package=winner,
        ff4_package=ff4,
        final_block_cap_tokens=final_block_cap_tokens,
    )

    winner_stream = build_bridge_updater_stream(
        stream_id=stream_id,
        initial_skill_sha256=initial_skill_sha256,
        pools=frozen,
        scientific_projection="WINNER",
    )
    ff4_stream = build_bridge_updater_stream(
        stream_id=stream_id,
        initial_skill_sha256=initial_skill_sha256,
        pools=frozen,
        scientific_projection="FIRST_FAIL_4",
    )
    validate_blinded_bridge_units(stream=winner_stream, units=rendered.winner_free_units)
    validate_blinded_bridge_units(stream=ff4_stream, units=rendered.ff4_free_units)

    w_comp, w_diag = compile_comp_state(
        base_skill_markdown=initial_skill_markdown,
        units=rendered.winner_compiler_units,
    )
    ff4_comp, ff4_diag = compile_comp_state(
        base_skill_markdown=initial_skill_markdown,
        units=rendered.ff4_compiler_units,
    )
    del w_diag
    ff4_scope = compiler_scope(ff4_diag)
    ff4_scores = canonical_selected_scores(rendered.ff4_compiler_units)
    score_only = compile_score_only_control(
        base_skill_markdown=initial_skill_markdown,
        selected_scores=ff4_scores,
    )
    scope_matched = compile_scope_matched_control(
        base_skill_markdown=initial_skill_markdown,
        selected_scores=ff4_scores,
        rendered_block_count=ff4_scope,
    )

    # Load-bearing information parity: FREE and COMP use the exact same rendered
    # bytes and selected-evidence score inside each source cell.
    for free, comp in zip(rendered.winner_free_units, rendered.winner_compiler_units, strict=True):
        if free.evidence_text != comp.evidence_text or free.source_score != comp.selected_score:
            raise RuntimeError("Bridge integrated Winner FREE/COMP information parity drift")
    for free, comp in zip(rendered.ff4_free_units, rendered.ff4_compiler_units, strict=True):
        if free.evidence_text != comp.evidence_text or free.source_score != comp.selected_score:
            raise RuntimeError("Bridge integrated FF4 FREE/COMP information parity drift")

    prepared = BridgeV4R2StreamPreparation(
        stream_id=stream_id,
        initial_skill_sha256=initial_skill_sha256,
        winner_package=winner,
        ff4_package=ff4,
        rendered=rendered,
        winner_updater_stream=winner_stream,
        ff4_updater_stream=ff4_stream,
        w_comp=w_comp,
        ff4_comp=ff4_comp,
        score_only_generic=score_only,
        scope_matched_generic=scope_matched,
        ff4_compiler_scope=ff4_scope,
    )
    if set(prepared.state_sha256_by_deterministic_arm) != {
        "W_COMP",
        "FF4_COMP",
        "SCORE_ONLY_GENERIC_MAX",
        "SCOPE_MATCHED_GENERIC_MAX",
    }:
        raise RuntimeError("Bridge deterministic arm set drift")
    return prepared


__all__ = [
    "STREAM_ARMS",
    "BridgeV4R2StreamPreparation",
    "prepare_stream_from_sealed_pools",
]
