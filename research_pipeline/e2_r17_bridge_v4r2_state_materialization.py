from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_state_compiler_bridge import (
    CompiledState,
    TypedDiagnosis,
    compile_skill,
    diagnose,
    extract_visible_signals,
    rendered_primitive_count,
    score_only_generic_diagnosis,
    scope_matched_generic_diagnosis,
)

DETERMINISTIC_ARMS = (
    "W_COMP",
    "FF4_COMP",
    "SCORE_ONLY_GENERIC_MAX",
    "SCOPE_MATCHED_GENERIC_MAX",
)


@dataclass(frozen=True)
class SelectedEvidence:
    evidence_text: str
    selected_score: float
    evidence_sha256: str

    def validate(self) -> None:
        if not self.evidence_text.strip():
            raise ValueError("selected evidence text must be non-empty")
        if self.selected_score not in (0.0, 1.0):
            raise ValueError("selected evidence score must be binary")
        actual = hashlib.sha256(self.evidence_text.encode("utf-8")).hexdigest()
        if actual != self.evidence_sha256:
            raise ValueError("selected evidence SHA drift")


def selected_evidence(text: str, score: float) -> SelectedEvidence:
    return SelectedEvidence(
        evidence_text=text,
        selected_score=float(score),
        evidence_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def diagnoses_from_selected_evidence(units: Sequence[SelectedEvidence]) -> tuple[TypedDiagnosis, ...]:
    if len(units) != 8:
        raise ValueError("Bridge deterministic compiler requires exactly eight selected evidence units")
    diagnoses: list[TypedDiagnosis] = []
    for unit in units:
        unit.validate()
        signals = extract_visible_signals(
            evidence_text=unit.evidence_text,
            selected_score=unit.selected_score,
        )
        diagnoses.append(diagnose(signals))
    return tuple(diagnoses)


def compile_comp_state(
    *,
    base_skill_markdown: str,
    units: Sequence[SelectedEvidence],
) -> tuple[CompiledState, tuple[TypedDiagnosis, ...]]:
    diagnoses = diagnoses_from_selected_evidence(units)
    return compile_skill(base_skill_markdown=base_skill_markdown, diagnoses=diagnoses), diagnoses


def compile_score_only_control(
    *,
    base_skill_markdown: str,
    selected_scores: Sequence[float],
) -> CompiledState:
    diagnosis = score_only_generic_diagnosis(selected_scores)
    return compile_skill(base_skill_markdown=base_skill_markdown, diagnoses=[diagnosis])


def compile_scope_matched_control(
    *,
    base_skill_markdown: str,
    selected_scores: Sequence[float],
    rendered_block_count: int,
) -> CompiledState:
    diagnosis = scope_matched_generic_diagnosis(
        selected_scores,
        rendered_block_count=rendered_block_count,
    )
    return compile_skill(base_skill_markdown=base_skill_markdown, diagnoses=[diagnosis])


def compiler_scope(diagnoses: Sequence[TypedDiagnosis]) -> int:
    return rendered_primitive_count(diagnoses)


def canonical_selected_scores(units: Sequence[SelectedEvidence]) -> tuple[float, ...]:
    if len(units) != 8:
        raise ValueError("Bridge score vector requires exactly eight units")
    scores: list[float] = []
    for unit in units:
        unit.validate()
        scores.append(float(unit.selected_score))
    return tuple(scores)


def materialize_actor_visible_state(
    *,
    state_root: Path,
    arm: str,
    compiled: CompiledState,
    source_evidence_sha256s: Sequence[str],
    selected_scores: Sequence[float],
    diagnosis_bundle_sha256: str | None,
    rendered_block_count: int,
) -> dict[str, Any]:
    if arm not in DETERMINISTIC_ARMS:
        raise ValueError(f"not a deterministic Bridge arm: {arm}")
    if state_root.exists():
        raise FileExistsError(state_root)
    if len(source_evidence_sha256s) != 8 or len(selected_scores) != 8:
        raise ValueError("Bridge materialization requires exact eight-unit provenance")
    if any(float(score) not in (0.0, 1.0) for score in selected_scores):
        raise ValueError("Bridge selected scores must be binary")
    if rendered_block_count not in (0, 1, 2):
        raise ValueError("Bridge compiler rendered-block count must be 0/1/2")

    skill_dir = state_root / "skill"
    skill_dir.mkdir(parents=True, exist_ok=False)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(compiled.skill_markdown, encoding="utf-8")
    actual_sha = hashlib.sha256(skill_path.read_bytes()).hexdigest()
    if actual_sha != compiled.skill_sha256:
        raise RuntimeError("materialized SKILL.md differs from CompiledState.skill_sha256")
    if skill_path.read_text(encoding="utf-8") != compiled.skill_markdown:
        raise RuntimeError("materialized SKILL.md bytes/text drift from compiler output")

    # The actor-visible directory must contain only the final treatment bytes.
    actor_visible_entries = sorted(path.name for path in skill_dir.iterdir())
    if actor_visible_entries != ["SKILL.md"]:
        raise RuntimeError("actor-visible deterministic state directory contains non-SKILL metadata")

    receipt = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-bridge-v4r2-deterministic-state-materialization",
        "arm": arm,
        "skill_path": str(skill_path),
        "actor_skill_source": str(skill_dir),
        "skill_sha256": actual_sha,
        "compiled_skill_sha256": compiled.skill_sha256,
        "compiler_diagnosis_bundle_sha256": diagnosis_bundle_sha256,
        "source_evidence_sha256s": list(source_evidence_sha256s),
        "selected_scores": [float(value) for value in selected_scores],
        "rendered_block_count": int(rendered_block_count),
        "primitives": [str(value) for value in compiled.primitives],
        "raw_typed_diagnosis_actor_visible": False,
        "hidden_experiment_metadata_actor_visible": False,
        "post_compile_model_calls": 0,
        "post_compile_renderer": "NONE",
    }
    receipt_path = state_root / "state_receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt


__all__ = [
    "DETERMINISTIC_ARMS",
    "SelectedEvidence",
    "selected_evidence",
    "diagnoses_from_selected_evidence",
    "compile_comp_state",
    "compile_score_only_control",
    "compile_scope_matched_control",
    "compiler_scope",
    "canonical_selected_scores",
    "materialize_actor_visible_state",
]
