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
}

POLICY: dict[str, Any] = {
    "schema_version": "2.0",
    "all_eight_gates_required": True,
    "launch_requires_execution_authorized": True,
    "automatic_override_forbidden": True,
    "screening_cannot_emit_method_fail": True,
    "baseline_floor_or_ceiling_is_not_method_failure": True,
    "inconclusive_does_not_update_negative_scientific_belief": True,
    "budget_stop_does_not_register_scientific_result": True,
    "parameters_require_provenance": True,
    "gpu_hours_must_derive_from_measured_throughput": True,
}
