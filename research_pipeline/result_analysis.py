from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT


SCHEMA_VERSION = "1.0"
DEFAULT_LEDGER = PROJECT_ROOT / "research_pipeline" / "result_analysis_ledger_20260825.json"
REQUIRED_FAILURE_LAYERS = {
    "execution",
    "experiment_identifiability",
    "optimization",
    "operationalization",
    "method_realization",
    "assumption_scope",
    "core_principle",
}
POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "raw_result_artifact_is_not_result_analysis": True,
    "terminal_result_requires_interpretation_before_distillation": True,
    "analysis_must_separate_observed_from_inferred": True,
    "analysis_must_name_estimand_and_strongest_alternative_explanation": True,
    "analysis_must_state_positive_implication_and_negative_boundary": True,
    "analysis_must_type_failure_layer_before_terminal_routing": True,
    "support_or_qualification_failure_is_not_method_effect_failure": True,
    "method_extension_stop_does_not_invalidate_independent_measurement_evidence": True,
    "post_outcome_validator_invention_cannot_rescue_a_failed_gate": True,
    "distilled_memory_has_zero_scientific_or_execution_authority": True,
}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _authority_zero(value: Any) -> bool:
    return isinstance(value, dict) and bool(value) and not any(bool(v) for v in value.values())


def load_result_analysis_ledger(path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def validate_result_analysis_ledger(ledger: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if ledger.get("schema_version") != SCHEMA_VERSION:
        errors.append("result-analysis schema version drift")
    policy = ledger.get("policy") or {}
    for key, expected in POLICY.items():
        if key == "schema_version":
            continue
        if policy.get(key) is not expected:
            errors.append(f"result-analysis policy missing: {key}")
    if ledger.get("scientific_authority") is not False:
        errors.append("result-analysis ledger must have zero scientific authority")

    seen: set[str] = set()
    for index, row in enumerate(ledger.get("analyses") or []):
        prefix = f"analysis[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} is not an object")
            continue
        analysis_id = _text(row.get("analysis_id"))
        if not analysis_id:
            errors.append(f"{prefix} missing analysis_id")
        elif analysis_id in seen:
            errors.append(f"duplicate analysis_id: {analysis_id}")
        seen.add(analysis_id)
        for field in ("paper_id", "candidate_id", "result_scope", "terminal_decision"):
            if not _text(row.get(field)):
                errors.append(f"{prefix} missing {field}")
        if not (row.get("source_refs") or []):
            errors.append(f"{prefix} has no source refs")
        if not (row.get("estimands") or []):
            errors.append(f"{prefix} has no estimand")
        observed = row.get("observed") or []
        if not observed:
            errors.append(f"{prefix} has no observed findings")
        for obs_index, obs in enumerate(observed):
            if not isinstance(obs, dict) or not _text(obs.get("statement")) or not _text(obs.get("evidence")):
                errors.append(f"{prefix}.observed[{obs_index}] must bind statement and evidence")

        analysis = row.get("analysis") or {}
        for field in (
            "positive_implications",
            "negative_boundaries",
            "strongest_alternative_explanations",
        ):
            if not (analysis.get(field) or []):
                errors.append(f"{prefix} missing analysis.{field}")
        for field in (
            "mechanism_interpretation",
            "failure_layer",
            "failure_type",
            "failure_diagnosis",
            "does_not_imply",
            "paper_implication",
            "next_scientific_action",
        ):
            if not _text(analysis.get(field)):
                errors.append(f"{prefix} missing analysis.{field}")
        if _text(analysis.get("failure_layer")) not in REQUIRED_FAILURE_LAYERS:
            errors.append(f"{prefix} failure layer is not canonical")
        for alt_index, alt in enumerate(analysis.get("strongest_alternative_explanations") or []):
            if not isinstance(alt, dict) or not _text(alt.get("alternative")) or not _text(alt.get("disposition")):
                errors.append(f"{prefix}.alternative[{alt_index}] must bind alternative and disposition")

        failure = row.get("failure_asset") or {}
        for field in ("signature", "diagnosis", "affected_layer", "reusable_precheck", "evidence_ref", "does_not_imply"):
            if not _text(failure.get(field)):
                errors.append(f"{prefix} missing failure_asset.{field}")
        if _text(failure.get("affected_layer")) != _text(analysis.get("failure_layer")):
            errors.append(f"{prefix} failure asset layer does not match analysis failure layer")
        if failure.get("scientific_authority") is not False:
            errors.append(f"{prefix} failure asset authority leak")

        lessons = row.get("discovery_lessons") or []
        if not lessons:
            errors.append(f"{prefix} has no discovery lessons")
        for lesson_index, lesson in enumerate(lessons):
            if not isinstance(lesson, dict):
                errors.append(f"{prefix}.lesson[{lesson_index}] is not an object")
                continue
            for field in ("lesson_id", "lesson_type", "affected_layer", "title", "summary", "reopen_condition", "reusable_precheck"):
                if not _text(lesson.get(field)):
                    errors.append(f"{prefix}.lesson[{lesson_index}] missing {field}")

        guidance = row.get("paper_guidance") or {}
        for field in ("paper_id", "guidance_id", "active_archetype", "active_story", "load_bearing_message"):
            if not _text(guidance.get(field)):
                errors.append(f"{prefix} missing paper_guidance.{field}")
        if not (guidance.get("required_paper_only_actions") or []):
            errors.append(f"{prefix} has no paper-only actions")
        if not (guidance.get("forbidden_rescue_moves") or []):
            errors.append(f"{prefix} has no forbidden rescue moves")
        if guidance.get("scientific_authority") is not False or guidance.get("experiment_authority") is not False:
            errors.append(f"{prefix} paper guidance authority leak")

        if not _authority_zero(row.get("authority")):
            errors.append(f"{prefix} analysis authority must remain all false")
    return errors


def build_result_analysis_state(ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    source = ledger if ledger is not None else load_result_analysis_ledger()
    errors = validate_result_analysis_ledger(source)
    analyses = [dict(row) for row in source.get("analyses") or [] if isinstance(row, dict)]
    layers = Counter(_text((row.get("analysis") or {}).get("failure_layer")) for row in analyses)
    terminal = sum(bool(_text(row.get("terminal_decision"))) for row in analyses)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "RESULT_ANALYSIS_DISTILLED" if not errors else "RESULT_ANALYSIS_INVALID",
        "policy": dict(POLICY),
        "summary": {
            "analyses": len(analyses),
            "terminal_results_analyzed": terminal,
            "failure_layers": dict(sorted((key, value) for key, value in layers.items() if key)),
            "discovery_lessons": sum(len(row.get("discovery_lessons") or []) for row in analyses),
            "failure_assets": sum(1 for row in analyses if isinstance(row.get("failure_asset"), dict) and row.get("failure_asset")),
            "paper_guidance_records": sum(1 for row in analyses if isinstance(row.get("paper_guidance"), dict) and row.get("paper_guidance")),
            "errors": len(errors),
        },
        "analyses": analyses,
        "errors": errors,
        "scientific_authority": False,
        "authority": {
            "problem_gate": False,
            "method": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
            "claim_expansion": False,
            "submission": False,
        },
    }


def result_analysis_failure_assets(state: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in state.get("analyses") or []:
        if not isinstance(row, dict):
            continue
        asset = row.get("failure_asset") or {}
        if not isinstance(asset, dict) or not asset:
            continue
        out.append({**asset, "external_memory_input": True, "scientific_authority": False})
    return out


def result_analysis_discovery_lessons(state: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in state.get("analyses") or []:
        if not isinstance(row, dict):
            continue
        for lesson in row.get("discovery_lessons") or []:
            if isinstance(lesson, dict):
                out.append({**lesson, "source_analysis_id": _text(row.get("analysis_id"))})
    return out


def result_analysis_paper_guidance(state: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in state.get("analyses") or []:
        if not isinstance(row, dict):
            continue
        guidance = row.get("paper_guidance") or {}
        if isinstance(guidance, dict) and guidance:
            out.append({**guidance, "source_analysis_id": _text(row.get("analysis_id"))})
    return out
