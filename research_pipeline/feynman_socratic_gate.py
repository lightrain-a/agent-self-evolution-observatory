from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.1"

POLICY: dict[str, Any] = {
    "certificate_is_zero_authority": True,
    "gate_runs_before_problem_gate": True,
    "plain_language_compression_is_not_novelty_evidence": True,
    "socratic_attack_must_name_counterexample_boundary_simplification_and_falsifier": True,
    "mature_reduction_alert_must_be_derived_from_typed_existing_review_not_freeform_judge_opinion": True,
    "gate_cannot_grant_problem_method_experiment_p0_or_gpu_authority": True,
    "retrospective_replay_is_regression_evidence_not_scientific_evidence": True,
    "problem_insight_certificate_is_shadow_until_contribution_replay_and_prospective_validation_pass": True,
    "method_complexity_is_not_paper_contribution": True,
    "minimal_sufficient_intervention_is_preferred_over_unnecessary_complexity": True,
    "under_explained_observation_may_be_primary_contribution_evidence_but_not_novelty_authority": True,
}

CORE_FIELDS = (
    "problem_plain",
    "why_existing_baseline_fails",
    "decisive_observable",
    "counterexample",
    "boundary_condition",
    "strongest_simplification",
    "falsifier",
)

PROBLEM_INSIGHT_SHADOW_FIELDS = (
    "primary_contribution_type",
    "problem_importance",
    "under_explained_observation",
    "missing_insight",
    "minimal_decisive_test",
    "minimal_sufficient_intervention",
    "insight_predictions",
)


def _text(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("en", "zh", "statement", "reason", "claim", "summary"):
            if str(value.get(key) or "").strip():
                return str(value[key]).strip()
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, list):
        return "; ".join(_text(v) for v in value if _text(v))
    return str(value or "").strip()


def _first(*values: Any) -> str:
    for value in values:
        text = _text(value)
        if text:
            return text
    return ""


def _semantic_review(candidate: dict[str, Any]) -> dict[str, Any]:
    review = candidate.get("semantic_reduction_review")
    return review if isinstance(review, dict) else {}


def _typed_mature_reduction(candidate: dict[str, Any]) -> dict[str, Any]:
    """Return an existing typed reduction witness; never infer a closure from prose alone."""
    review = _semantic_review(candidate)
    review_verdict = str(review.get("verdict") or "").upper()
    reduction_class = str(review.get("reduction_class") or "").upper()
    hard_classes = {
        "VALID_HARD_VETO", "EXACT_REDUCTION", "MATURE_THEORY_REDUCTION",
        "MATCHED_SIMPLIFICATION", "SOURCE_INTERNAL_REDUCTION",
    }
    if review_verdict == "BLOCK" and (
        reduction_class in hard_classes
        or review.get("matched_simplification_stop_certified") is True
        or review.get("exact_reduction_certified") is True
    ):
        return {
            "source": "semantic_reduction_review",
            "reduction_class": reduction_class or "TYPED_BLOCK",
            "strongest_reduction": _first(review.get("strongest_reduction"), candidate.get("strongest_same_information_baseline")),
        }

    # A scoped problem-novelty closure is enough for a pre-ProblemGate warning, but
    # it is deliberately not treated as a persistent scientific dead-end. Later
    # method/support/operationalization failures are excluded from this pre-gate alert.
    if (
        candidate.get("search_closure_certified") is True
        and str(candidate.get("closure_layer") or "") == "problem_novelty"
        and _text(candidate.get("strongest_reduction"))
    ):
        return {
            "source": "certified_problem_novelty_closure",
            "reduction_class": str(candidate.get("source_stop_class") or "SCOPED_PROBLEM_NOVELTY_CLOSURE"),
            "strongest_reduction": _text(candidate.get("strongest_reduction")),
            "persistent_dead_end_certified": candidate.get("dead_end_certified") is True,
        }
    return {}


def build_feynman_socratic_certificate(candidate: dict[str, Any]) -> dict[str, Any]:
    review = _semantic_review(candidate)
    counter = candidate.get("counter_explanation") if isinstance(candidate.get("counter_explanation"), dict) else {}
    contract = candidate.get("reduction_falsifiability_contract")
    domain = candidate.get("domain_transfer_audit")
    saturation = candidate.get("saturation_scan")
    certificate = {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": _first(candidate.get("candidate_id"), candidate.get("source_candidate_id"), candidate.get("id")),
        "problem_plain": _first(candidate.get("problem_plain"), candidate.get("problem_text"), candidate.get("irreducible_object"), candidate.get("paper_problem"), candidate.get("title")),
        "why_existing_baseline_fails": _first(candidate.get("same_information_nonreducibility"), candidate.get("closest_work_distance"), review.get("reason"), candidate.get("reason")),
        "changed_assumption_or_intervention": _first(candidate.get("changed_assumption"), candidate.get("repair_axis"), candidate.get("novelty_category"), candidate.get("intervention")),
        "decisive_observable": _first(candidate.get("exact_prediction"), counter.get("opposite_prediction"), candidate.get("required_observation"), candidate.get("paperability_claim")),
        "counterexample": _first(candidate.get("reviewer_attack"), counter.get("statement"), contract, candidate.get("avoid")),
        "boundary_condition": _first(candidate.get("endpoint_headroom_requirement"), saturation, domain, candidate.get("reopen_only_if"), candidate.get("irreducible_object")),
        "strongest_simplification": _first(candidate.get("strongest_same_information_baseline"), review.get("strongest_reduction"), candidate.get("strongest_reduction")),
        "falsifier": _first(candidate.get("cheapest_problem_falsifier"), review.get("exact_reduction_test"), contract, candidate.get("reopen_only_if")),
        "primary_contribution_type": _first(candidate.get("primary_contribution_type"), candidate.get("contribution_type")),
        "problem_importance": _first(candidate.get("problem_importance")),
        "under_explained_observation": _first(candidate.get("under_explained_observation")),
        "missing_insight": _first(candidate.get("missing_insight")),
        "minimal_decisive_test": _first(candidate.get("minimal_decisive_test")),
        "minimal_sufficient_intervention": _first(candidate.get("minimal_sufficient_intervention")),
        "insight_predictions": _first(candidate.get("insight_predictions")),
        "typed_reduction_witness": _typed_mature_reduction(candidate),
        "scientific_authority": False,
        "problem_gate_authority": False,
        "method_authority": False,
        "experiment_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
    }
    return certificate


def audit_feynman_socratic_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in CORE_FIELDS if not _text(certificate.get(field))]
    problem_insight_missing = [field for field in PROBLEM_INSIGHT_SHADOW_FIELDS if not _text(certificate.get(field))]
    primary = str(certificate.get("primary_contribution_type") or "").strip().lower().replace("-", "_").replace(" ", "_")
    problem_insight_shadow_status = "PROBLEM_INSIGHT_SHADOW_COMPLETE" if not problem_insight_missing else "PROBLEM_INSIGHT_SHADOW_INCOMPLETE"
    witness = certificate.get("typed_reduction_witness") if isinstance(certificate.get("typed_reduction_witness"), dict) else {}
    if witness:
        status = "MATURE_REDUCTION_ALERT"
    elif missing:
        status = "REVISE_CERTIFICATE"
    else:
        status = "CLEAR_FOR_PROBLEM_GATE_REVIEW"
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": certificate.get("candidate_id"),
        "status": status,
        "missing_fields": missing,
        "typed_reduction_witness": witness,
        "problem_insight_shadow": {
            "status": problem_insight_shadow_status,
            "missing_fields": problem_insight_missing,
            "primary_contribution_type": primary,
            "insight_dominant_candidate": primary == "insight" and not problem_insight_missing,
            "live_problem_gate_authority": False,
            "scientific_authority": False,
        },
        "problem_gate_review_may_continue": status == "CLEAR_FOR_PROBLEM_GATE_REVIEW",
        "machine_actionable": False,
        "scientific_authority": False,
        "problem_gate_authority": False,
        "method_authority": False,
        "experiment_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
    }


def run_historical_replay(project_root: Path, sample_size: int = 20) -> dict[str, Any]:
    """Regression-only replay. Expected labels come from canonical typed state, never from gate prose."""
    search_path = project_root / "generated" / "paper-first-search-portfolio-design-adjudication.json"
    discovery_path = project_root / "generated" / "asset-first-discovery-ledger-20260816.json"
    incubation_path = project_root / "generated" / "paper-first-idea-incubation.json"
    search = json.loads(search_path.read_text(encoding="utf-8"))
    memory = search.get("shadow_search_memory") or {}

    positives: list[dict[str, Any]] = []
    for row in memory.get("closed_objects") or []:
        if not isinstance(row, dict):
            continue
        if (
            row.get("search_closure_certified") is True
            and str(row.get("closure_layer") or "") == "problem_novelty"
            and _text(row.get("strongest_reduction"))
        ):
            positives.append(row)

    negatives: list[dict[str, Any]] = []
    for row in memory.get("hold_objects") or []:
        if isinstance(row, dict) and row.get("dead_end_certified") is not True:
            negatives.append(row)

    if incubation_path.exists():
        incubation = json.loads(incubation_path.read_text(encoding="utf-8"))
        for row in incubation.get("candidates") or []:
            if not isinstance(row, dict) or str(row.get("verdict") or "") != "ADVANCE_TO_PAPER_DESIGN":
                continue
            safe = dict(row)
            safe.setdefault("problem_plain", row.get("problem") or row.get("title") or row.get("id"))
            safe.setdefault("why_existing_baseline_fails", row.get("novelty_boundary") or row.get("reason") or "historically advanced to Paper Design")
            safe.setdefault("exact_prediction", row.get("minimum_p0") or row.get("reason") or "registered candidate prediction")
            safe.setdefault("reviewer_attack", row.get("reviewer_risk") or "attempt strongest same-information reduction")
            safe.setdefault("reopen_only_if", row.get("stop_rule") or "historical candidate was not closed at this stage")
            safe.setdefault("strongest_same_information_baseline", row.get("strongest_baseline") or "registered strongest simplification")
            safe.setdefault("cheapest_problem_falsifier", row.get("minimum_p0") or row.get("stop_rule") or "registered historical falsifier")
            negatives.append(safe)

    if discovery_path.exists():
        discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
        for row in discovery.get("candidates") or discovery.get("ledger") or []:
            if isinstance(row, dict) and str(row.get("decision") or "").upper() == "SELECT_FOR_PAPER_DESIGN":
                safe = dict(row)
                safe.setdefault("problem_plain", row.get("candidate") or row.get("title") or "selected paper-design candidate")
                safe.setdefault("why_existing_baseline_fails", row.get("reason") or "survived registered reductions")
                safe.setdefault("exact_prediction", row.get("reason") or "registered residual survives")
                safe.setdefault("reviewer_attack", "attempt strongest same-information reduction")
                safe.setdefault("reopen_only_if", "not applicable: candidate survived the historical gate")
                safe.setdefault("strongest_same_information_baseline", "registered strongest simplification")
                safe.setdefault("cheapest_problem_falsifier", "registered historical falsifier")
                negatives.append(safe)

    # Use all available problem-novelty closures first, then fill with typed HOLD / historical
    # advance controls. The expected label is never passed into certificate construction.
    n_positive = min(len(positives), sample_size)
    n_negative = min(len(negatives), sample_size - n_positive)
    rows = [(row, True) for row in positives[:n_positive]] + [(row, False) for row in negatives[:n_negative]]
    alerts = true_alerts = false_alerts = 0
    results: list[dict[str, Any]] = []
    for row, expected_alert in rows:
        certificate = build_feynman_socratic_certificate(row)
        audit = audit_feynman_socratic_certificate(certificate)
        alerted = audit["status"] == "MATURE_REDUCTION_ALERT"
        alerts += int(alerted)
        true_alerts += int(alerted and expected_alert)
        false_alerts += int(alerted and not expected_alert)
        results.append({
            "candidate_id": certificate.get("candidate_id") or _first(row.get("basin"), row.get("title")),
            "expected_typed_mature_reduction": expected_alert,
            "status": audit["status"],
            "source_scope": "canonical-retrospective-regression",
            "scientific_authority": False,
        })
    expected_positive = sum(int(flag) for _, flag in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if len(rows) == sample_size and true_alerts == expected_positive and false_alerts == 0 else "FAIL",
        "sample_size": len(rows),
        "expected_mature_reductions": expected_positive,
        "detected_mature_reductions": true_alerts,
        "false_mature_reduction_alerts": false_alerts,
        "alerts": alerts,
        "results": results,
        "retrospective_only": True,
        "scientific_authority": False,
    }


def build_feynman_socratic_gate_state(project_root: Path) -> dict[str, Any]:
    replay = run_historical_replay(project_root, 20)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "Feynman_Socratic_GATE_INSTALLED" if replay.get("status") == "PASS" else "Feynman_Socratic_GATE_REPLAY_FAILED",
        "policy": dict(POLICY),
        "historical_replay": replay,
        "summary": {
            "replay_cases": int(replay.get("sample_size") or 0),
            "problem_novelty_reductions": int(replay.get("expected_mature_reductions") or 0),
            "problem_novelty_reductions_detected": int(replay.get("detected_mature_reductions") or 0),
            "false_reduction_alerts": int(replay.get("false_mature_reduction_alerts") or 0),
            "automatic_scientific_authority": 0,
        },
        "scientific_authority": False,
    }
