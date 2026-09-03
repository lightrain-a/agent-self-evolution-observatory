from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Iterable, Sequence


class RepairPrimitive(StrEnum):
    """Frozen minimal repair vocabulary for the E2-R17 development bridge.

    The vocabulary is intentionally small.  It is a proposal/development object,
    not an E3-confirmatory vocabulary, and must be frozen before any prospective
    bridge outcome is inspected.
    """

    VERIFY_OUTPUT = "VERIFY_OUTPUT"
    COMPLETE_WORKFLOW = "COMPLETE_WORKFLOW"
    RECOVER_TOOL_ERROR = "RECOVER_TOOL_ERROR"


@dataclass(frozen=True)
class TrajectorySignals:
    """Signals derivable only from learner-visible trajectory content.

    No arm, projection, stream family, task family, source rollout identity, or
    hidden experiment provenance is permitted here.
    """

    selected_score: float
    saw_workbook_read: bool
    saw_write_or_materialization: bool
    saw_output_save: bool
    saw_output_reload: bool
    saw_target_verification: bool
    saw_tool_error: bool
    saw_clean_recovery_after_error: bool

    def validate(self) -> None:
        if self.selected_score not in (0.0, 1.0):
            raise ValueError("selected_score must be binary")


@dataclass(frozen=True)
class TypedDiagnosis:
    schema_version: str
    failure_stage: str
    failed_invariants: tuple[str, ...]
    observed_evidence: tuple[str, ...]
    required_repairs: tuple[RepairPrimitive, ...]
    source_signal_sha256: str

    @property
    def diagnosis_sha256(self) -> str:
        payload = asdict(self)
        payload["required_repairs"] = [str(x) for x in self.required_repairs]
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CompiledState:
    skill_markdown: str
    primitives: tuple[RepairPrimitive, ...]
    diagnosis_sha256: str
    skill_sha256: str


_ERROR_PATTERNS = (
    r"traceback",
    r"syntaxerror",
    r"exception",
    r"command not found",
    r"no such file or directory",
    r"permission denied",
    r"returned non-zero",
    r"exit code [1-9]",
    r"tool error",
    r"malformed",
)

_WRITE_PATTERNS = (
    r"\.cell\s*\(",
    r"\[[\"'][A-Z]{1,3}[0-9]+[\"']\]\s*=",
    r"to_excel\s*\(",
    r"write_only",
)

_SAVE_PATTERNS = (
    r"\.save\s*\(\s*[\"']output\.xlsx[\"']",
    r"to_excel\s*\(\s*[\"']output\.xlsx[\"']",
)

_RELOAD_PATTERNS = (
    r"load_workbook\s*\(\s*[\"']output\.xlsx[\"']",
    r"read_excel\s*\(\s*[\"']output\.xlsx[\"']",
)

_VERIFY_PATTERNS = (
    r"assert\s+.*(?:cell|value|output)",
    r"verify|verified|verification",
    r"expected.*(?:==|equals|match)",
    r"(?:==|equals|match).*expected",
)

_READ_PATTERNS = (
    r"load_workbook\s*\(",
    r"read_excel\s*\(",
    r"sheetnames",
    r"max_row",
    r"max_column",
)

_RECOVERY_PATTERNS = (
    r"retry",
    r"corrected",
    r"fix(?:ed|ing)?",
    r"second attempt",
    r"re-run",
    r"rerun",
)


def _has_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) for pattern in patterns)


def extract_visible_signals(*, evidence_text: str, selected_score: float) -> TrajectorySignals:
    """Deterministically extract signals from the exact learner-visible evidence.

    This function is deliberately text-only so the constrained arm cannot use
    privileged structured metadata that the free-form updater did not receive.
    """

    if not evidence_text.strip():
        raise ValueError("evidence_text must be non-empty")
    lower = evidence_text.lower()
    saw_error = _has_any(lower, _ERROR_PATTERNS)
    signals = TrajectorySignals(
        selected_score=float(selected_score),
        saw_workbook_read=_has_any(lower, _READ_PATTERNS),
        saw_write_or_materialization=_has_any(lower, _WRITE_PATTERNS),
        saw_output_save=_has_any(lower, _SAVE_PATTERNS),
        saw_output_reload=_has_any(lower, _RELOAD_PATTERNS),
        saw_target_verification=_has_any(lower, _VERIFY_PATTERNS),
        saw_tool_error=saw_error,
        saw_clean_recovery_after_error=saw_error and _has_any(lower, _RECOVERY_PATTERNS),
    )
    signals.validate()
    return signals


def diagnose(signals: TrajectorySignals) -> TypedDiagnosis:
    """Map visible trajectory signals to a typed diagnosis without model calls."""

    signals.validate()
    failures: list[str] = []
    observed: list[str] = []
    repairs: list[RepairPrimitive] = []

    if signals.saw_workbook_read:
        observed.append("workbook_read")
    if signals.saw_write_or_materialization:
        observed.append("write_or_materialization")
    if signals.saw_output_save:
        observed.append("output_saved")
    if signals.saw_output_reload:
        observed.append("output_reloaded")
    if signals.saw_target_verification:
        observed.append("target_verified")
    if signals.saw_tool_error:
        observed.append("tool_error")
    if signals.saw_clean_recovery_after_error:
        observed.append("clean_recovery_after_error")

    # A successful selected trajectory is not force-labelled as needing repair.
    # This prevents the compiler from injecting generic workflow advice into every
    # winner merely because the vocabulary contains useful instructions.
    if signals.selected_score == 0.0:
        if not signals.saw_write_or_materialization or not signals.saw_output_save:
            failures.append("incomplete_execution_before_materialized_output")
            repairs.append(RepairPrimitive.COMPLETE_WORKFLOW)
        elif not signals.saw_output_reload or not signals.saw_target_verification:
            failures.append("output_not_closed_by_reload_and_verification")
            repairs.append(RepairPrimitive.VERIFY_OUTPUT)
        if signals.saw_tool_error and not signals.saw_clean_recovery_after_error:
            failures.append("unrecovered_tool_error")
            repairs.append(RepairPrimitive.RECOVER_TOOL_ERROR)

    # Canonical order is scientific state, not Python set iteration order.
    order = (
        RepairPrimitive.COMPLETE_WORKFLOW,
        RepairPrimitive.VERIFY_OUTPUT,
        RepairPrimitive.RECOVER_TOOL_ERROR,
    )
    repair_set = set(repairs)
    canonical_repairs = tuple(x for x in order if x in repair_set)

    if not failures:
        stage = "NO_TYPED_REPAIR"
    elif RepairPrimitive.COMPLETE_WORKFLOW in canonical_repairs:
        stage = "EXECUTION_COMPLETION"
    elif RepairPrimitive.VERIFY_OUTPUT in canonical_repairs:
        stage = "OUTPUT_CLOSURE"
    else:
        stage = "TOOL_RECOVERY"

    signal_payload = json.dumps(asdict(signals), sort_keys=True, separators=(",", ":"))
    signal_sha = hashlib.sha256(signal_payload.encode("utf-8")).hexdigest()
    return TypedDiagnosis(
        schema_version="E2-R17-TYPED-DIAGNOSIS-v1",
        failure_stage=stage,
        failed_invariants=tuple(failures),
        observed_evidence=tuple(observed),
        required_repairs=canonical_repairs,
        source_signal_sha256=signal_sha,
    )


_PRIMITIVE_BLOCKS: dict[RepairPrimitive, str] = {
    RepairPrimitive.VERIFY_OUTPUT: """## Output Verification Guard\n\nAfter saving `output.xlsx`, reload it with `load_workbook(\"output.xlsx\", data_only=True)` and verify the exact target cells contain the intended final values before stopping. If verification fails, fix the output and save it again before completion.""",
    RepairPrimitive.COMPLETE_WORKFLOW: """## Completion Loop\n\nFor every spreadsheet task, complete this full sequence before stopping:\n\n1. Inspect the workbook structure and identify the exact source and target cells.\n2. Read the source data required by the request.\n3. Compute the requested transformation or final values.\n4. Write or materialize the requested values into the exact target cells.\n5. Save the result to `output.xlsx` without modifying `input.xlsx`.\n6. Reload `output.xlsx` with `load_workbook(\"output.xlsx\", data_only=True)` and verify the target cells contain the intended values.\n\nInspection alone is never task completion. Do not stop until the requested output has been written, saved, reloaded, and verified.""",
    RepairPrimitive.RECOVER_TOOL_ERROR: """## Tool-Error Recovery Guard\n\nIf a shell, Python, or tool invocation fails or is malformed, do not stop and do not repeat the same broken call unchanged. Issue a clean minimal corrected command, then continue the completion loop through write, save, reload, and verification.""",
}


def compile_skill(*, base_skill_markdown: str, diagnoses: Sequence[TypedDiagnosis]) -> CompiledState:
    """Compile a canonical persistent skill from typed diagnoses.

    Composition is union-of-required-primitives with fixed canonical ordering.
    Duplicate diagnoses cannot increase state length.  No free-form generation is
    used here, so identical diagnoses compile byte-identically.
    """

    if not base_skill_markdown.strip():
        raise ValueError("base_skill_markdown must be non-empty")
    order = (
        RepairPrimitive.COMPLETE_WORKFLOW,
        RepairPrimitive.VERIFY_OUTPUT,
        RepairPrimitive.RECOVER_TOOL_ERROR,
    )
    requested = {primitive for diagnosis in diagnoses for primitive in diagnosis.required_repairs}
    primitives = tuple(p for p in order if p in requested)

    # COMPLETE_WORKFLOW already contains reload+verification semantics, so a
    # separate VERIFY_OUTPUT block would be redundant.  Canonicalization removes
    # that duplicate surface while retaining the typed diagnosis receipt.
    rendered_primitives = list(primitives)
    if RepairPrimitive.COMPLETE_WORKFLOW in rendered_primitives and RepairPrimitive.VERIFY_OUTPUT in rendered_primitives:
        rendered_primitives.remove(RepairPrimitive.VERIFY_OUTPUT)

    parts = [base_skill_markdown.rstrip()]
    for primitive in rendered_primitives:
        parts.append(_PRIMITIVE_BLOCKS[primitive])
    skill = "\n\n".join(parts).rstrip() + "\n"
    diag_bundle = [d.diagnosis_sha256 for d in diagnoses]
    diag_sha = hashlib.sha256(
        json.dumps(diag_bundle, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    skill_sha = hashlib.sha256(skill.encode("utf-8")).hexdigest()
    return CompiledState(
        skill_markdown=skill,
        primitives=primitives,
        diagnosis_sha256=diag_sha,
        skill_sha256=skill_sha,
    )


__all__ = [
    "RepairPrimitive",
    "TrajectorySignals",
    "TypedDiagnosis",
    "CompiledState",
    "extract_visible_signals",
    "diagnose",
    "compile_skill",
]
