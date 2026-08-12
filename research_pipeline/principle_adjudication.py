from __future__ import annotations

from collections import Counter
from typing import Any


REQUIRED_FALSIFICATION_PRECONDITIONS = {
    "registered_prediction",
    "assumptions_hold",
    "scope_conditions_hold",
    "operationalization_valid",
    "experiment_identifiable",
    "optimization_adequate",
    "independent_truth",
    "matched_baseline",
}

REQUIRED_FAILURE_UPDATE_RULES = {
    "execution-invalid",
    "design-nonidentifiable",
    "operationalization-failure",
    "assumption-violation",
    "matched-simplification",
    "registered-prediction-contradicted",
}

POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "principle_certificate_required_before_experiment_compile": True,
    "principle_certificate_is_not_a_formal_experiment_gate": True,
    "experiment_is_evidence_about_a_principle_not_a_vote_on_an_idea": True,
    "negative_result_requires_layer_adjudication": True,
    "design_failure_cannot_falsify_principle": True,
    "operationalization_failure_cannot_falsify_principle": True,
    "substrate_failure_cannot_falsify_broader_problem": True,
    "true_negative_does_not_automatically_falsify_principle": True,
    "principle_falsification_requires_registered_prediction": True,
    "principle_falsification_requires_all_preconditions": True,
    "omitted_condition_updates_assumption_or_scope_before_core_mechanism": True,
    "positive_evidence_supports_but_does_not_prove_principle": True,
}

REFERENCES = [
    {"system": "FirstResearch", "adopted": "Research Question Certificate: primitives, assumptions, mechanism, falsifiable hypothesis, minimal decisive test, and explicit failure-update rule"},
    {"system": "Popper", "adopted": "decompose high-level hypotheses into measurable falsifiable implications and test them sequentially"},
    {"system": "Google Co-Scientist", "adopted": "separate generation, reflection, ranking, evolution, and meta-review around hypotheses rather than a single proposal chain"},
    {"system": "AI Scientist-v2", "adopted": "progressive experiment trees preserve alternative branches instead of committing every observation to a single hill-climb"},
    {"system": "RD-Agent", "adopted": "separate research-hypothesis feedback from development/implementation feedback"},
]

CONSULTATION_POLICY = {
    "principle_formation": ["hypothesis-generator", "mechanism-critic", "novelty-collision-reviewer", "meta-reviewer"],
    "pre_experiment": ["experimentalist", "statistics-reviewer", "systems-cost-reviewer", "falsification-reviewer"],
    "negative_result": ["design-critic", "operationalization-critic", "principle-advocate", "principle-falsifier", "meta-adjudicator"],
    "scale_up": ["replication-reviewer", "baseline-fairness-reviewer", "human-approval"],
    "rule": "No single reviewer may convert a negative run directly into a core-principle STOP; the meta-adjudicator must name the exact belief layer updated.",
}

COMMON_FALSIFICATION_REQUIRES = sorted(REQUIRED_FALSIFICATION_PRECONDITIONS)
COMMON_FAILURE_UPDATE_RULES = {
    "execution-invalid": "repair execution only; preserve the scientific contract and do not update principle belief",
    "design-nonidentifiable": "repair substrate/task/variation so the principle becomes testable; do not register a principle negative",
    "operationalization-failure": "repair the measurement, representation, or objective bridge before retesting the same principle",
    "assumption-violation": "revise the omitted assumption or scope condition, derive a new prediction, and keep the core mechanism unresolved",
    "matched-simplification": "weaken or merge the current method realization/novelty claim; do not automatically reject the broader principle",
    "registered-prediction-contradicted": "only after all falsification preconditions hold may the registered principle prediction be rejected",
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _nonempty_text_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(bool(_text(item)) for item in value)


def audit_principle_certificate(config: dict[str, Any]) -> dict[str, Any]:
    contract = (config.get("pre_experiment") or {}).get("principle_certificate") or {}
    if not isinstance(contract, dict) or not contract:
        return {
            "required": True,
            "is_formal_gate": False,
            "passed": False,
            "status": "missing-contract",
            "blockers": ["principle-certificate-missing"],
            "policy": POLICY,
        }

    blockers: list[str] = []
    principle_id = _text(contract.get("principle_id"))
    if not principle_id:
        blockers.append("principle-id-missing")
    if not _nonempty_text_list(contract.get("primitives")):
        blockers.append("principle-primitives-missing")
    if not _text(contract.get("mechanism")):
        blockers.append("principle-mechanism-missing")
    if not _nonempty_text_list(contract.get("scope_conditions")):
        blockers.append("principle-scope-conditions-missing")

    assumptions = contract.get("assumptions") or []
    assumption_ids: set[str] = set()
    if not isinstance(assumptions, list) or not assumptions:
        blockers.append("principle-assumptions-missing")
    else:
        for index, row in enumerate(assumptions):
            if not isinstance(row, dict):
                blockers.append(f"assumption-invalid:{index}")
                continue
            aid = _text(row.get("id"))
            if not aid:
                blockers.append(f"assumption-id-missing:{index}")
            elif aid in assumption_ids:
                blockers.append(f"assumption-id-duplicate:{aid}")
            else:
                assumption_ids.add(aid)
            if not _text(row.get("statement")):
                blockers.append(f"assumption-statement-missing:{aid or index}")
            if not _text(row.get("observable_check")):
                blockers.append(f"assumption-check-missing:{aid or index}")

    predictions = contract.get("predictions") or []
    prediction_ids: set[str] = set()
    if not isinstance(predictions, list) or not predictions:
        blockers.append("principle-predictions-missing")
    else:
        for index, row in enumerate(predictions):
            if not isinstance(row, dict):
                blockers.append(f"prediction-invalid:{index}")
                continue
            pid = _text(row.get("id"))
            if not pid:
                blockers.append(f"prediction-id-missing:{index}")
            elif pid in prediction_ids:
                blockers.append(f"prediction-id-duplicate:{pid}")
            else:
                prediction_ids.add(pid)
            if not _text(row.get("statement")):
                blockers.append(f"prediction-statement-missing:{pid or index}")
            if not _text(row.get("observable")):
                blockers.append(f"prediction-observable-missing:{pid or index}")
            if _text(row.get("role")) not in {"phenomenon-prerequisite", "mechanism-test", "boundary-test"}:
                blockers.append(f"prediction-role-invalid:{pid or index}")

    operationalization = contract.get("operationalization") or []
    if not isinstance(operationalization, list) or not operationalization:
        blockers.append("principle-operationalization-missing")
    else:
        for index, row in enumerate(operationalization):
            if not isinstance(row, dict) or not _text(row.get("concept")) or not _text(row.get("measure")) or not _text(row.get("validity_check")):
                blockers.append(f"operationalization-incomplete:{index}")

    falsification = contract.get("falsification") or {}
    registered_predictions = set(str(item) for item in falsification.get("prediction_ids") or [])
    if not registered_predictions:
        blockers.append("principle-falsifier-predictions-missing")
    elif not registered_predictions.issubset(prediction_ids):
        blockers.append("principle-falsifier-prediction-unknown")
    preconditions = set(str(item) for item in falsification.get("requires") or [])
    for missing in sorted(REQUIRED_FALSIFICATION_PRECONDITIONS - preconditions):
        blockers.append(f"principle-falsifier-precondition-missing:{missing}")
    if not _text(falsification.get("contradiction_rule")):
        blockers.append("principle-contradiction-rule-missing")

    failure_rules = contract.get("failure_update_rules") or {}
    if not isinstance(failure_rules, dict):
        blockers.append("principle-failure-update-rules-invalid")
        failure_rules = {}
    for missing in sorted(REQUIRED_FAILURE_UPDATE_RULES - set(failure_rules)):
        blockers.append(f"principle-failure-update-rule-missing:{missing}")
    for key, value in failure_rules.items():
        if not _text(value):
            blockers.append(f"principle-failure-update-rule-empty:{key}")

    passed = not blockers
    return {
        "required": True,
        "is_formal_gate": False,
        "passed": passed,
        "status": "pass" if passed else "repair-required",
        "principle_id": principle_id,
        "blockers": sorted(set(blockers)),
        "summary": {
            "primitives": len(contract.get("primitives") or []),
            "assumptions": len(assumptions),
            "predictions": len(predictions),
            "registered_falsifiers": len(registered_predictions),
            "operationalizations": len(operationalization),
        },
        "contract": contract,
        "policy": POLICY,
    }


def adjudicate_experiment_evidence(
    diagnosis: str,
    certificate: dict[str, Any],
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Decide which scientific layer an experiment is allowed to update."""
    evidence = evidence or {}
    cert = certificate if "passed" in certificate and "contract" in certificate else {"passed": True, "contract": certificate}
    contract = cert.get("contract") or {}
    prediction_ids = set(str(item) for item in (contract.get("falsification") or {}).get("prediction_ids") or [])
    base = {
        "diagnosis": diagnosis,
        "principle_id": _text(contract.get("principle_id")),
        "principle_falsified": False,
        "core_mechanism_rejected": False,
        "scientific_belief_target": "none",
        "requires_human_review": False,
    }
    if cert.get("passed") is not True:
        return {**base, "verdict": "PRINCIPLE_CONTRACT_REPAIR", "reason": "The principle certificate is incomplete, so evidence cannot be interpreted at principle level."}
    if diagnosis in {"infrastructure-error", "budget-plan-mismatch"}:
        return {**base, "verdict": "NO_PRINCIPLE_UPDATE", "repair_layer": "execution", "reason": "The run did not validly test the mechanism."}
    if diagnosis in {"substrate-degenerate", "no-label-variation"}:
        return {**base, "verdict": "EXPERIMENT_DESIGN_REPAIR", "repair_layer": "experiment", "reason": "The design failed to instantiate an identifiable test of the principle."}
    if diagnosis == "underfit":
        return {**base, "verdict": "OPTIMIZATION_REPAIR", "repair_layer": "optimization", "reason": "Optimization was insufficient to interpret the scientific prediction."}
    if diagnosis in {"representation-signal-mismatch", "objective-claim-mismatch"}:
        return {
            **base,
            "verdict": "OPERATIONALIZATION_REPAIR",
            "repair_layer": "operationalization",
            "scientific_belief_target": "measurement-bridge",
            "reason": "The current measurement/representation bridge is weakened; the underlying principle is not rejected by itself.",
        }
    if diagnosis == "matched-simplification-tie":
        return {
            **base,
            "verdict": "METHOD_OR_NOVELTY_WEAKENED",
            "scientific_belief_target": "method-realization",
            "requires_human_review": True,
            "reason": "The realization adds no identifiable value over the strongest matched simplification; the broader mechanism may still hold.",
        }
    if diagnosis == "positive-signal":
        return {
            **base,
            "verdict": "PRINCIPLE_SUPPORTED_NOT_PROVEN",
            "scientific_belief_target": "principle-support",
            "requires_human_review": True,
            "reason": "Observed evidence is compatible with the preregistered mechanism prediction but does not prove the principle.",
        }
    if diagnosis != "true-negative":
        return {**base, "verdict": "INCONCLUSIVE_PRINCIPLE_STATUS", "reason": "No principle-level mapping is registered for this diagnosis."}

    if evidence.get("omitted_condition_discovered") is True or evidence.get("assumption_violation_discovered") is True:
        return {
            **base,
            "verdict": "ASSUMPTION_OR_SCOPE_REFINEMENT",
            "scientific_belief_target": "assumption-or-scope",
            "requires_human_review": True,
            "reason": "The negative result exposed an omitted condition; refine scope/assumptions and derive a new prediction before rejecting the core mechanism.",
        }

    registered_prediction_id = _text(evidence.get("registered_prediction_id"))
    checks = {
        "registered_prediction": registered_prediction_id in prediction_ids,
        "assumptions_hold": evidence.get("assumptions_hold") is True,
        "scope_conditions_hold": evidence.get("scope_conditions_hold") is True,
        "operationalization_valid": evidence.get("operationalization_valid") is True,
        "experiment_identifiable": evidence.get("experiment_identifiable") is True,
        "optimization_adequate": evidence.get("optimization_adequate") is True,
        "independent_truth": evidence.get("independent_truth") is True,
        "matched_baseline": evidence.get("matched_baseline") is True,
    }
    missing = [key for key, passed in checks.items() if not passed]
    if missing or evidence.get("falsifier_triggered") is not True:
        return {
            **base,
            "verdict": "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED",
            "scientific_belief_target": "method-realization",
            "requires_human_review": True,
            "preconditions": checks,
            "missing_preconditions": missing,
            "reason": "A method-level negative exists, but the registered principle falsifier has not been established under every required condition.",
        }

    return {
        **base,
        "verdict": "PRINCIPLE_FALSIFIED",
        "principle_falsified": True,
        "core_mechanism_rejected": True,
        "scientific_belief_target": "core-principle",
        "requires_human_review": True,
        "preconditions": checks,
        "registered_prediction_id": registered_prediction_id,
        "reason": "A preregistered principle prediction was contradicted with assumptions, scope, measurement validity, identifiability, optimization, independent truth, and matched baselines all verified.",
    }


def build_principle_layer_state(cards: list[dict[str, Any]], experiment_nodes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    audits = [card.get("principle_certificate_prerequisite") or {} for card in cards]
    by_idea = {str(card.get("idea_id")): card for card in cards if card.get("idea_id")}
    verdicts: list[dict[str, Any]] = []
    for node in experiment_nodes or []:
        card = by_idea.get(str(node.get("idea_id")))
        if card:
            verdicts.append(adjudicate_experiment_evidence(
                str(node.get("diagnosis") or ""),
                card.get("principle_certificate_prerequisite") or {},
                node.get("principle_evidence") or {},
            ))
    counts = Counter(str(row.get("verdict")) for row in verdicts)
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "references": REFERENCES,
        "consultation_policy": CONSULTATION_POLICY,
        "summary": {
            "cards": len(cards),
            "certificates_passed": sum(audit.get("passed") is True for audit in audits),
            "certificates_blocked": sum(audit.get("passed") is not True for audit in audits),
            "postrun_adjudications": len(verdicts),
            "principle_falsifications": counts.get("PRINCIPLE_FALSIFIED", 0),
            "principle_repairs_or_refinements": sum(
                value for key, value in counts.items()
                if key in {"PRINCIPLE_CONTRACT_REPAIR", "EXPERIMENT_DESIGN_REPAIR", "OPERATIONALIZATION_REPAIR", "ASSUMPTION_OR_SCOPE_REFINEMENT"}
            ),
        },
        "adjudications": verdicts,
    }
