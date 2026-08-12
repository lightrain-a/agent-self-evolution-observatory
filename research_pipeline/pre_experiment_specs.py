from __future__ import annotations

from typing import Any

ALLOWED_PROVENANCE_TYPES = {
    "literature",
    "statistical-calculation",
    "measured-throughput",
    "explicit-protocol-choice",
}

GATES: tuple[dict[str, str], ...] = (
    {"key": "parameter_provenance", "tag": "PROVENANCE", "title": "Literature-to-Protocol"},
    {"key": "baseline_competence", "tag": "COMPETENCE", "title": "Baseline Competence"},
    {"key": "mechanism_identifiability", "tag": "IDENTIFY", "title": "Mechanism Identifiability"},
    {"key": "statistical_resolution", "tag": "STATS", "title": "Statistical Resolution"},
    {"key": "compute_graph", "tag": "COMPUTE", "title": "Compute Graph"},
    {"key": "measured_throughput", "tag": "THROUGHPUT", "title": "Measured Throughput"},
    {"key": "observability_recovery", "tag": "RECOVERY", "title": "Observability & Recovery"},
    {"key": "outcome_semantics", "tag": "SEMANTICS", "title": "Outcome Semantics"},
)

TYPED_OUTCOMES = {
    "METHOD-PASS",
    "METHOD-FAIL",
    "SCREENING-SIGNAL",
    "SCREENING-NO-SIGNAL",
    "INCONCLUSIVE",
    "BASELINE-FLOOR",
    "BASELINE-CEILING",
    "RUNTIME-ERROR",
    "IMPLEMENTATION-ERROR",
    "BUDGET-STOP",
    "HORIZON-CENSORED",
}

POLICY: dict[str, Any] = {
    "schema_version": "2.3",
    "paper_design_contract_required_before_principle_and_implementation": True,
    "paper_design_contract_is_not_a_formal_gate": True,
    "local_validation_cannot_discover_or_redefine_core_method": True,
    "core_method_change_requires_return_to_paper_design": True,
    "full_experiment_requires_frozen_method_and_experiment_blueprint": True,
    "principle_certificate_required_before_updater_competence": True,
    "principle_certificate_is_not_a_formal_gate": True,
    "protocol_validity_required_before_updater_competence": True,
    "protocol_validity_is_not_a_formal_gate": True,
    "research_execution_plan_required_before_launch": True,
    "research_execution_plan_is_derived_not_a_formal_gate": True,
    "research_execution_plan_cannot_authorize_execution": True,
    "experiment_is_evidence_about_principle_not_a_vote_on_idea": True,
    "updater_competence_required_before_gate_1": True,
    "updater_competence_is_not_a_ninth_gate": True,
    "all_eight_gates_required": True,
    "launch_requires_execution_authorized": True,
    "automatic_override_forbidden": True,
    "screening_cannot_emit_method_fail": True,
    "baseline_floor_or_ceiling_is_not_method_failure": True,
    "inconclusive_does_not_update_negative_scientific_belief": True,
    "budget_stop_does_not_register_scientific_result": True,
    "method_fail_does_not_automatically_falsify_principle": True,
    "principle_falsification_requires_registered_prediction_and_valid_bridge": True,
    "invalid_evaluation_protocol_cannot_emit_method_or_principle_result": True,
    "future_persistent_update_contracts_require_post_update_effect_realization_check": True,
    "post_update_effect_realization_is_cross_cutting_protocol_validity_not_a_ninth_gate": True,
    "observation_level_recurrence_alone_cannot_establish_effect_realization": True,
    "legacy_contracts_predating_effect_realization_rule_are_not_retroactively_reclassified": True,
    "terminal_outcome_requires_endpoint_headroom_audit": True,
    "execution_cap_censoring_must_be_typed_separately": True,
    "cap_censored_branch_cannot_count_as_natural_terminal_failure": True,
    "parameters_require_provenance": True,
    "gpu_hours_must_derive_from_measured_throughput": True,
}
