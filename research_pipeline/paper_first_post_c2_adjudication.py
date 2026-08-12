from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_c2_contract import build_c2_contract

SOURCE = Path(__file__).with_name("paper_first_post_c2_evidence_20260812.json")
DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-post-c2-adjudication.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-post-c2-adjudication.js"

POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "executed_frozen_contract_is_historical_authority": True,
    "later_stricter_gate_cannot_rewrite_executed_contract": True,
    "posthoc_validity_can_invalidate_but_never_rescue_a_negative": True,
    "c2_stop_keeps_c3_locked": True,
    "c2_stop_keeps_full_experiment_locked": True,
    "local_falsifier_cannot_discover_or_redefine_method": True,
    "broad_phenomenon_may_survive_a_method_falsifier": True,
    "new_paper_problem_requires_fresh_novelty_method_blueprint_cycle": True,
    "retrospective_principle_certificate_forbidden": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_source() -> dict[str, Any]:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def _gate_stops(metrics: dict[str, Any], gate: dict[str, Any]) -> bool:
    valid = int(metrics.get("valid_units") or 0)
    nonzero = int(metrics.get("nonzero_tau_units") or 0)
    concordant = int(metrics.get("parent_sign_concordant_units") or 0)
    reversal = metrics.get("same_memory_cross_context_sign_reversal") is True
    if valid < int(gate.get("valid_units") or 0):
        return True
    if nonzero < int(gate.get("minimum_nonzero_tau_units") or 0):
        return True
    minimum_concordant = gate.get("minimum_parent_sign_concordant_units")
    if minimum_concordant is not None and concordant < int(minimum_concordant):
        return True
    if gate.get("same_memory_cross_context_sign_reversal_required") is True and not reversal:
        return True
    return False


def evaluate_post_c2_adjudication(
    authority: dict[str, Any],
    latest_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    latest_contract = deepcopy(latest_contract or build_c2_contract())
    c2 = authority.get("c2") or {}
    metrics = c2.get("metrics") or {}
    historical = authority.get("historical_frozen_contract") or {}
    historical_gate = historical.get("go") or {}
    latest_gate = ((latest_contract.get("frozen_gate") or {}).get("go") or {})
    validity = authority.get("decision_context_validity") or {}
    scienceworld = authority.get("scienceworld_parent_evidence") or {}
    rules = authority.get("authority_rules") or {}

    historical_stop = _gate_stops(metrics, historical_gate)
    latest_stop = _gate_stops(metrics, latest_gate)
    validity_pass = bool(
        validity.get("decision") == "POSTHOC_DECISION_CONTEXT_VALIDITY_PASS"
        and int(validity.get("valid_units") or 0) == int(validity.get("required_units") or -1) == 10
    )
    c2_stop = c2.get("decision") == "C2_STOP_CONTROLLED_ACTION_MECHANISM_NOT_SUPPORTED"
    authority_rules_pass = bool(
        rules.get("historical_c2_contract_must_not_be_rewritten") is True
        and rules.get("posthoc_validity_cannot_relax_c2_gate") is True
        and rules.get("scienceworld_evidence_cannot_rescue_c2") is True
        and rules.get("c3_locked_after_c2_stop") is True
        and rules.get("full_experiment_locked_after_c2_stop") is True
        and rules.get("new_method_auto_authorized") is False
        and rules.get("new_paper_problem_auto_authorized") is False
        and rules.get("new_paper_problem_requires_fresh_novelty_method_blueprint_cycle") is True
    )

    if not c2_stop:
        decision = "POST_C2_ADJUDICATION_NOT_APPLICABLE"
        mechanism_status = "not-terminalized-by-this-adjudicator"
        reason = "The imported C2 artifact is not a C2 mechanism STOP."
    elif not validity_pass:
        decision = "C2_NEGATIVE_VALIDITY_INCONCLUSIVE_REDESIGN_REQUIRED"
        mechanism_status = "unresolved-because-posthoc-validity-failed"
        reason = (
            "The C2 outcome is negative, but the post-hoc full decision-context validity check did not pass; "
            "the negative cannot be used as a clean mechanism falsifier."
        )
    elif not historical_stop:
        decision = "C2_PROVENANCE_INCONSISTENT_HOLD"
        mechanism_status = "unresolved-because-recorded-result-does-not-trigger-executed-gate"
        reason = "The recorded C2 STOP does not satisfy the STOP logic of the contract actually frozen for the run."
    else:
        decision = "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM"
        mechanism_status = "local-falsifier-triggered"
        reason = (
            "All ten strict C2 units are execution-valid and the full pre-divergence policy decision context is reproducible, "
            "yet only 2/10 controlled action contrasts are nonzero and the preregistered same-memory cross-context sign reversal is absent. "
            "The earliest-divergent-action controlled-mediator mechanism is therefore unsupported by its local falsifier."
        )

    clean_mechanism_stop = bool(
        decision == "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM"
        and historical_stop
        and validity_pass
        and authority_rules_pass
    )

    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "paper_id": authority.get("paper_id"),
        "decision": decision,
        "reason": reason,
        "current_paper_formulation_status": "STOP" if clean_mechanism_stop else "HOLD",
        "current_method_status": mechanism_status,
        "broad_parent_phenomenon_status": (
            "SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE" if clean_mechanism_stop else "UNRESOLVED"
        ),
        "broad_parent_phenomenon": (
            "Persistent memory effects can be context-dependent and early branch divergence is reproducible in parent evidence; "
            "C2 does not erase that phenomenon, but it rejects the paper's proposed earliest-divergent-action mediator explanation."
        ),
        "c2_result": {
            "decision": c2.get("decision"),
            "decision_sha256": c2.get("decision_sha256"),
            "metrics": metrics,
        },
        "gate_provenance": {
            "executed_contract_sha256": historical.get("sha256"),
            "executed_gate": historical_gate,
            "executed_gate_stops_observed_result": historical_stop,
            "latest_source_gate": latest_gate,
            "latest_source_gate_stops_observed_result": latest_stop,
            "decision_invariant_to_later_gate_tightening": bool(historical_stop and latest_stop),
            "rule": "The executed frozen contract is historical authority; the later stricter source gate is reported only as a robustness/provenance check.",
        },
        "decision_context_validity": {
            "decision": validity.get("decision"),
            "sha256": validity.get("sha256"),
            "valid_units": validity.get("valid_units"),
            "required_units": validity.get("required_units"),
            "pass": validity_pass,
            "interpretation": (
                "The ScienceWorld-discovered environment-state versus policy-context concern was explicitly checked on C2 and does not invalidate this negative."
                if validity_pass
                else "The C2 negative is not mechanism-authoritative until full policy decision-context equality is established."
            ),
        },
        "scienceworld_scope_evidence": {
            "f0_decision": scienceworld.get("f0_decision"),
            "f0_sha256": scienceworld.get("f0_sha256"),
            "diagnosis_sha256": scienceworld.get("diagnosis_sha256"),
            "scope_refinement_candidate": scienceworld.get("scope_refinement_candidate"),
            "principle_authority": scienceworld.get("principle_authority"),
            "relationship_to_current_paper": scienceworld.get("cross_surface_rule"),
            "auto_rescues_current_paper": False,
        },
        "scientific_interpretation": {
            "supported": [
                "The executed C2 environment/replay instrument is valid at the full pre-divergence policy decision-context level for all 10 strict units.",
                "The current earliest-divergent-action controlled mediator has insufficient support: 2/10 nonzero tau_A and no required three-context sign reversal.",
                "A broader context-dependent persistent-memory-effect phenomenon remains parent evidence, not a successful method claim."
            ],
            "not_supported": [
                "That the earliest divergent action generally mediates the parent memory effect.",
                "That C2 authorizes C3 certificate training, a full experiment, a second backbone, or a new updater.",
                "That the ScienceWorld post-hoc scope lesson can be used to retrofit or rescue the current memory-paper mechanism.",
                "That the ScienceWorld HOLD retrospectively falsifies a principle without a prospective principle certificate."
            ],
        },
        "authority": {
            "clean_mechanism_stop": clean_mechanism_stop,
            "authority_rules_pass": authority_rules_pass,
            "C3_locked": True,
            "full_experiment_authorized": False,
            "second_backbone_authorized": False,
            "new_method_auto_authorized": False,
            "new_paper_problem_auto_authorized": False,
            "threshold_relaxation_authorized": False,
            "unit_replacement_authorized": False,
            "retrospective_principle_certificate_authorized": False,
        },
        "next_action": (
            "Archive the current controlled-mediator paper formulation. If a genuinely new paper problem is proposed from the surviving phenomenon or the ScienceWorld decision-context lesson, restart at fresh novelty/collision review, method design, and experiment blueprint; do not treat it as C2 repair."
            if clean_mechanism_stop
            else "Resolve the adjudication/validity inconsistency before any new paper claim; C3 and full experiments remain locked."
        ),
        "policy": POLICY,
    }


def build_post_c2_adjudication() -> dict[str, Any]:
    return evaluate_post_c2_adjudication(_load_source(), build_c2_contract())


def write_post_c2_adjudication(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
) -> dict[str, Any]:
    row = build_post_c2_adjudication()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.PAPER_FIRST_POST_C2_ADJUDICATION = "
        + json.dumps(row, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    return row


if __name__ == "__main__":
    print(json.dumps(write_post_c2_adjudication(), ensure_ascii=False))
