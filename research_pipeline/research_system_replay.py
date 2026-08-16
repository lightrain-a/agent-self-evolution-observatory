from __future__ import annotations

from typing import Any

from .principle_adjudication import adjudicate_experiment_evidence


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "research_system_changes_require_replay": True,
    "benchmark_contains_false_stop_and_false_go_cases": True,
    "component_addition_should_improve_replay_not_only_complexity": True,
    "historical_replay_is_diagnostic_not_new_scientific_evidence": True,
}

REFERENCES = [
    {"system": "ResearchClawBench", "adopted": "evaluate end-to-end research artifacts and explicitly score protocol/evidence/scientific-core failures"},
    {"system": "ResearchGym", "adopted": "evaluate autonomous research under fixed time/API budgets against objective baselines"},
    {"system": "ScienceAgentBench", "adopted": "use reproducible scientific tasks and verified evaluation artifacts"},
    {"system": "AutoLabs", "adopted": "ablate research-system components instead of assuming more agent machinery is better"},
    {"system": "ReplicationBench", "adopted": "paper-scale author-validated reproduction tasks that score experimental setup, derivations, analysis, code fidelity, and final correctness"},
]


def _first_certificate(pre_experiment: dict[str, Any]) -> dict[str, Any]:
    for card in pre_experiment.get("cards") or []:
        cert = card.get("principle_certificate_prerequisite") or {}
        if cert.get("passed") is True:
            return cert
    return {}


def build_research_system_replay(pre_experiment: dict[str, Any]) -> dict[str, Any]:
    cert = _first_certificate(pre_experiment)
    contract = cert.get("contract") or {}
    prediction_ids = list((contract.get("falsification") or {}).get("prediction_ids") or [])
    prediction_id = str(prediction_ids[0]) if prediction_ids else ""
    full_falsifier = {
        "registered_prediction_id": prediction_id,
        "assumptions_hold": True,
        "scope_conditions_hold": True,
        "operationalization_valid": True,
        "experiment_identifiable": True,
        "optimization_adequate": True,
        "independent_truth": True,
        "matched_baseline": True,
        "protocol_validity": True,
        "falsifier_triggered": True,
    }
    certified_counter = {
        "type": "COUNTER_MECHANISM_SUPPORTED",
        "statement": "A simpler matched mechanism predicts the observed outcome while the proposed mechanism does not.",
        "opposite_prediction": "Under matched information and scope, the simpler mechanism preserves the observed sign and the proposed residual disappears.",
        "opposite_principle": "The simpler matched mechanism, not the proposed standalone mechanism, governs the observed effect.",
        "opposite_search_seed": "Search for a setting with the same information where the simpler mechanism makes the wrong prediction and a residual is identifiable.",
        "scope": "replay fixture",
        "same_information_or_scope_matched": True,
        "evidence_refs": ["replay:counter-mechanism"],
        "alternative_explanations_ruled_out": ["execution", "substrate", "operationalization"],
        "counter_prediction_observed": True,
        "positive_support": True,
        "reopen_condition": "Reopen only if a new scoped prediction survives the same-information counter-mechanism.",
    }
    scenarios = [
        ("runtime-error", "infrastructure-error", {}, "NO_PRINCIPLE_UPDATE"),
        ("no-target-variation", "no-label-variation", {}, "EXPERIMENT_DESIGN_REPAIR"),
        ("bad-measurement-bridge", "representation-signal-mismatch", {}, "OPERATIONALIZATION_REPAIR"),
        ("simple-baseline-tie", "matched-simplification-tie", {}, "METHOD_OR_NOVELTY_WEAKENED"),
        ("omitted-moderator", "true-negative", {"omitted_condition_discovered": True}, "ASSUMPTION_OR_SCOPE_REFINEMENT"),
        ("protocol-invalid-negative", "true-negative", {**full_falsifier, "protocol_validity": False}, "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED"),
        ("registered-contradiction", "true-negative", full_falsifier, "REGISTERED_PREDICTION_REJECTED_COUNTEREXPLANATION_REQUIRED"),
        ("counter-explained-dead-end", "true-negative", {**full_falsifier, "counter_explanation": certified_counter}, "PRINCIPLE_DEAD_END_CERTIFIED"),
    ]
    rows: list[dict[str, Any]] = []
    for case_id, diagnosis, evidence, expected in scenarios:
        actual = adjudicate_experiment_evidence(diagnosis, cert, evidence)
        rows.append({
            "case_id": case_id,
            "diagnosis": diagnosis,
            "expected": expected,
            "actual": str(actual.get("verdict") or ""),
            "pass": str(actual.get("verdict") or "") == expected,
        })
    passed = sum(row["pass"] for row in rows)
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "references": REFERENCES,
        "summary": {
            "cases": len(rows),
            "passed": passed,
            "failed": len(rows) - passed,
            "false_stop_guard_cases": 7,
            "true_falsification_cases": 1,
        },
        "cases": rows,
        "paper_scale_reproduction": {
            "status": "spec-ready-not-yet-run",
            "required_facets": ["experimental-setup", "derivation-or-method", "data-analysis", "code-or-workflow", "result-correctness", "faithfulness-to-source"],
            "authority": "benchmark-only; reproduction score cannot authorize a scientific claim by itself",
        },
        "metrics": [
            "false_stop_rate",
            "false_go_rate",
            "duplicate_experiment_rate",
            "time_to_correct_failure_layer",
            "protocol_mismatch_rate",
            "evidence_mismatch_rate",
            "principle_attribution_accuracy",
            "gpu_hours_wasted_before_decisive_evidence",
        ],
    }
