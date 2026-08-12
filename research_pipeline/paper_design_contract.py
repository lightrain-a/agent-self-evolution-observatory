from __future__ import annotations

from typing import Any


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
        },
        "contract": contract,
        "policy": POLICY,
    }


def build_paper_first_workflow_state(pre_experiment: dict[str, Any]) -> dict[str, Any]:
    cards = list(pre_experiment.get("cards") or [])
    audits = [card.get("paper_design_prerequisite") or {} for card in cards]
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "macro_stages": [
            "paper-problem-and-evidence",
            "paper-novelty-contract",
            "principle-and-method-design",
            "experiment-blueprint",
            "economy-and-pre-experiment-compile",
            "local-validation",
            "method-freeze",
            "full-experiment",
            "paper-evidence-and-writing",
        ],
        "summary": {
            "cards": len(cards),
            "paper_design_passed": sum(audit.get("passed") is True for audit in audits),
            "paper_design_blocked": sum(audit.get("passed") is not True for audit in audits),
            "historical_cards_predating_rule": sum(audit.get("status") == "missing-contract" for audit in audits),
        },
        "rule": "A local pilot tests a frozen paper-motivated method. If the core method changes, return to novelty/method design and invalidate any full-experiment authorization.",
    }
