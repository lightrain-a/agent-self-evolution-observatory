from __future__ import annotations

from typing import Any

from .paper_quality_gate import audit_paper_evidence_plan
from .system_architecture import TEMPORAL_FLOW


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "paper_novelty_precedes_method_design": True,
    "method_design_precedes_experiment_blueprint": True,
    "experiment_blueprint_precedes_local_validation": True,
    "local_validation_is_for_falsification_not_method_discovery": True,
    "full_experiment_requires_frozen_method_and_blueprint": True,
    "method_change_after_local_validation_invalidates_full_experiment_authority": True,
    "pilot_score_cannot_redefine_paper_contribution": True,
    "novelty_requires_closest_work_and_irreducible_difference": True,
    "paper_quality_v2_requires_typed_baselines_ablations_and_analyses": True,
    "paper_quality_v2_requires_why_better_and_ruling_out_evidence": True,
    "paper_quality_v2_1_requires_visual_evidence_contract": True,
    "visual_evidence_is_claim_mapped_not_decorative": True,
    "paper_quality_v2_is_required_for_schema_2_3_plus_or_explicit_v2_contract": True,
    "legacy_contracts_are_not_retroactively_rewritten": True,
}

REQUIRED_NOVELTY_FIELDS = {
    "paper_problem",
    "closest_work",
    "novelty_axis",
    "contribution_claim",
    "irreducible_difference",
    "collision_status",
}

REQUIRED_METHOD_FIELDS = {
    "method_name",
    "core_mechanism",
    "novelty_to_method_mapping",
    "components",
    "strongest_simplification",
    "method_change_rule",
}

REQUIRED_BLUEPRINT_FIELDS = {
    "claim_experiment_matrix",
    "local_validation_scope",
    "full_experiment_scope",
    "baseline_matrix",
    "ablation_matrix",
    "freeze_rule",
    "experimental_integrity",
}

REQUIRED_EXPERIMENTAL_INTEGRITY_FIELDS = {
    "model_and_inference",
    "prompt_tool_policy",
    "task_sample_split",
    "metric_analysis_plan",
    "randomness_replication_plan",
    "stopping_exclusion_rules",
    "allowed_adaptations",
    "hidden_evaluation_access_policy",
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple)):
        return bool(value)
    return value is not None


def audit_paper_design_contract(config: dict[str, Any]) -> dict[str, Any]:
    contract = (config.get("pre_experiment") or {}).get("paper_design") or {}
    if not isinstance(contract, dict) or not contract:
        return {
            "required": True,
            "is_formal_gate": False,
            "passed": False,
            "status": "missing-contract",
            "blockers": ["paper-design-contract-missing"],
            "policy": POLICY,
        }

    blockers: list[str] = []
    novelty = contract.get("novelty") or {}
    method = contract.get("method") or {}
    blueprint = contract.get("experiment_blueprint") or {}
    evidence_quality = contract.get("evidence_quality") or {}

    for field in sorted(REQUIRED_NOVELTY_FIELDS):
        if not _nonempty(novelty.get(field)):
            blockers.append(f"paper-novelty-field-missing:{field}")
    closest = novelty.get("closest_work") or []
    if not isinstance(closest, list) or not closest:
        blockers.append("paper-novelty-closest-work-missing")
    else:
        for index, row in enumerate(closest):
            if not isinstance(row, dict) or not _text(row.get("identity")) or not _text(row.get("difference")) or not _text(row.get("source_ref")):
                blockers.append(f"paper-novelty-closest-work-incomplete:{index}")

    for field in sorted(REQUIRED_METHOD_FIELDS):
        if not _nonempty(method.get(field)):
            blockers.append(f"method-design-field-missing:{field}")
    mapping = method.get("novelty_to_method_mapping") or []
    if not isinstance(mapping, list) or not mapping:
        blockers.append("novelty-to-method-mapping-missing")

    for field in sorted(REQUIRED_BLUEPRINT_FIELDS):
        if not _nonempty(blueprint.get(field)):
            blockers.append(f"experiment-blueprint-field-missing:{field}")
    integrity = blueprint.get("experimental_integrity") or {}
    if not isinstance(integrity, dict):
        blockers.append("experimental-integrity-invalid")
        integrity = {}
    for field in sorted(REQUIRED_EXPERIMENTAL_INTEGRITY_FIELDS):
        if not _nonempty(integrity.get(field)):
            blockers.append(f"experimental-integrity-field-missing:{field}")
    claim_matrix = blueprint.get("claim_experiment_matrix") or []
    if not isinstance(claim_matrix, list) or not claim_matrix:
        blockers.append("claim-experiment-matrix-missing")
    else:
        for index, row in enumerate(claim_matrix):
            if not isinstance(row, dict):
                blockers.append(f"claim-experiment-row-invalid:{index}")
                continue
            for field in ("claim_id", "claim", "local_test", "full_test", "metric", "strongest_baseline"):
                if not _text(row.get(field)):
                    blockers.append(f"claim-experiment-field-missing:{index}:{field}")

    schema_parts = _text(config.get("schema_version")).split(".")
    try:
        schema_major = int(schema_parts[0]) if schema_parts else 0
        schema_minor = int(schema_parts[1]) if len(schema_parts) > 1 else 0
    except ValueError:
        schema_major, schema_minor = 0, 0
    quality_required = bool(evidence_quality) or (schema_major, schema_minor) >= (2, 3)
    if quality_required:
        quality_audit = audit_paper_evidence_plan(evidence_quality, method_components=len(method.get("components") or []))
        if not quality_audit.get("passed"):
            blockers.extend(str(item) for item in quality_audit.get("blockers") or [])
    else:
        quality_audit = {
            "schema_version": "legacy",
            "required": False,
            "is_formal_gate": False,
            "passed": True,
            "status": "LEGACY_PREDATES_PAPER_QUALITY_V2",
            "blockers": [],
            "warnings": ["paper-quality-v2-not-retroactively-invented"],
            "summary": {"baselines": 0, "ablations": 0, "analyses": 0, "visualizations": 0, "main_visualizations": 0, "main_visual_roles": []},
            "scientific_authority": False,
        }

    passed = not blockers
    return {
        "required": True,
        "is_formal_gate": False,
        "passed": passed,
        "status": "pass" if passed else "repair-required",
        "blockers": sorted(set(blockers)),
        "summary": {
            "closest_work": len(closest) if isinstance(closest, list) else 0,
            "method_components": len(method.get("components") or []),
            "paper_claims": len(claim_matrix) if isinstance(claim_matrix, list) else 0,
            "experimental_integrity_fields": sum(_nonempty(integrity.get(field)) for field in REQUIRED_EXPERIMENTAL_INTEGRITY_FIELDS),
            "paper_quality_v2_passed": quality_audit.get("passed") is True,
            "typed_baselines": int((quality_audit.get("summary") or {}).get("baselines") or 0),
            "typed_ablations": int((quality_audit.get("summary") or {}).get("ablations") or 0),
            "typed_analyses": int((quality_audit.get("summary") or {}).get("analyses") or 0),
            "visualizations": int((quality_audit.get("summary") or {}).get("visualizations") or 0),
            "main_visualizations": int((quality_audit.get("summary") or {}).get("main_visualizations") or 0),
            "main_visual_roles": list((quality_audit.get("summary") or {}).get("main_visual_roles") or []),
        },
        "paper_quality": quality_audit,
        "contract": contract,
        "policy": POLICY,
    }


def build_paper_first_workflow_state(pre_experiment: dict[str, Any]) -> dict[str, Any]:
    cards = list(pre_experiment.get("cards") or [])
    audits = [card.get("paper_design_prerequisite") or {} for card in cards]
    quality_audits = [audit.get("paper_quality") or {} for audit in audits]
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "macro_stages": [str(row["key"]) for row in TEMPORAL_FLOW],
        "summary": {
            "cards": len(cards),
            "paper_design_passed": sum(audit.get("passed") is True for audit in audits),
            "paper_design_blocked": sum(audit.get("passed") is not True for audit in audits),
            "historical_cards_predating_rule": sum(audit.get("status") == "missing-contract" for audit in audits),
            "paper_quality_v2_applied": sum(quality.get("required") is True for quality in quality_audits),
            "paper_quality_v2_passed": sum(quality.get("required") is True and quality.get("passed") is True for quality in quality_audits),
            "typed_baselines": sum(int((audit.get("summary") or {}).get("typed_baselines") or 0) for audit in audits),
            "typed_ablations": sum(int((audit.get("summary") or {}).get("typed_ablations") or 0) for audit in audits),
            "typed_analyses": sum(int((audit.get("summary") or {}).get("typed_analyses") or 0) for audit in audits),
            "visualizations": sum(int((audit.get("summary") or {}).get("visualizations") or 0) for audit in audits),
            "main_visualizations": sum(int((audit.get("summary") or {}).get("main_visualizations") or 0) for audit in audits),
        },
        "rule": "A local pilot tests a frozen paper-motivated method. If the core method changes, return to novelty/method design and invalidate any full-experiment authorization.",
    }
