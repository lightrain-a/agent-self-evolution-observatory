from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .principle_adjudication import FAILURE_LAYER_SPECS


PROBLEM_NOVELTY = "problem_novelty"
EXECUTION = "execution"
EXPERIMENT_IDENTIFIABILITY = "experiment_identifiability"
OPTIMIZATION = "optimization"
OPERATIONALIZATION = "operationalization"
METHOD_REALIZATION = "method_realization"
ASSUMPTION_SCOPE = "assumption_scope"
CORE_PRINCIPLE = "core_principle"

SCIENTIFIC_FAILURE_LAYERS = tuple(FAILURE_LAYER_SPECS)
CLOSURE_LAYERS = (PROBLEM_NOVELTY, *SCIENTIFIC_FAILURE_LAYERS)

MEMORY_CLASS_BY_CLOSURE_LAYER = {
    PROBLEM_NOVELTY: "PROBLEM_NOVELTY_STOP",
    EXECUTION: "EXECUTION_STOP",
    EXPERIMENT_IDENTIFIABILITY: "EXPERIMENT_IDENTIFIABILITY_STOP",
    OPTIMIZATION: "OPTIMIZATION_STOP",
    OPERATIONALIZATION: "OPERATIONALIZATION_STOP",
    METHOD_REALIZATION: "METHOD_REALIZATION_STOP",
    ASSUMPTION_SCOPE: "ASSUMPTION_SCOPE_STOP",
    CORE_PRINCIPLE: "CORE_PRINCIPLE_STOP",
}

# Re-audited 2026-08-18. These two exact formulations fail because the
# experiment/intervention cannot identify the proposed scientific object.
EXPERIMENT_IDENTIFIABILITY_READJUDICATION_ARTIFACTS = {
    "autodesign-posterbench-causal-nopath-principle-readjudication-20260817.json",
    "shadow-p01-locked-set-causal-nopath-principle-readjudication-20260816.json",
}

# Re-audited 2026-08-18. These three exact formulations use the wrong
# measurement/comparator/representation bridge for the claimed object.
OPERATIONALIZATION_READJUDICATION_ARTIFACTS = {
    "p06-coverage-starvation-principle-readjudication-20260816.json",
    "shadow-v4-reciprocal-coupling-principle-readjudication-20260816.json",
    "shaper-scaling-comparator-principle-readjudication-20260817.json",
}

# Re-audited 2026-08-18. These two formulations lose a necessary treatment or
# feasibility/scope assumption; the broader phenomenon is not falsified.
ASSUMPTION_SCOPE_READJUDICATION_ARTIFACTS = {
    "evodrc-block7-stall-principle-readjudication-20260817.json",
    "static-procedural-prior-cross-regime-contradiction-principle-readjudication-20260817.json",
}


def _broader_core_principle_falsified(payload: dict[str, Any]) -> bool:
    if payload.get("broader_core_principle_falsified") is True or payload.get("core_principle_falsified") is True:
        return True
    for key, value in payload.items():
        if key.startswith("broader_") and key.endswith("_falsified") and value is True:
            return True
    return bool(payload.get("benchmark_level_dead_end_certified") is True)


def classify_readjudication(payload: dict[str, Any], artifact_ref: str | Path) -> dict[str, Any]:
    """Classify a persistent scoped closure using the canonical failure-layer schema.

    Historical ``principle_dead_end_certified`` means the exact search basin was
    certified for persistent blocking; it does not imply ``core_principle``. A
    canonical core-principle layer requires the current artifact to explicitly type
    the scoped stop as ``PRINCIPLE_STOP`` (or to explicitly record broader/core
    falsification). Problem/novelty stops are handled separately upstream.
    """
    artifact_name = Path(str(artifact_ref)).name
    diagnosis = payload.get("principle_diagnosis") or {}
    counter = diagnosis.get("counter_explanation") or {}
    counter_type = str(counter.get("type") or diagnosis.get("counter_explanation_type") or "").strip().upper()
    stop_class = str(payload.get("stop_class") or "").strip().upper()
    broader_falsified = _broader_core_principle_falsified(payload)

    if stop_class == "PRINCIPLE_STOP" or broader_falsified:
        layer = CORE_PRINCIPLE
        reason = "The current artifact explicitly types this scoped scientific closure as PRINCIPLE_STOP after a scope-matched positive counter-explanation or exact same-information reduction."
    elif artifact_name in EXPERIMENT_IDENTIFIABILITY_READJUDICATION_ARTIFACTS:
        layer = EXPERIMENT_IDENTIFIABILITY
        reason = "The proposed experiment/intervention cannot identify the claimed scientific object under the recorded causal path or comparison design."
    elif artifact_name in OPERATIONALIZATION_READJUDICATION_ARTIFACTS:
        layer = OPERATIONALIZATION
        reason = "The measured quantity, representation, comparator, or observable does not operationalize the scientific object claimed by the formulation."
    elif artifact_name in ASSUMPTION_SCOPE_READJUDICATION_ARTIFACTS or counter_type == "NECESSARY_ASSUMPTION_REFUTED":
        layer = ASSUMPTION_SCOPE
        reason = "A necessary treatment, feasibility, or scope assumption for the scoped formulation does not hold; the broader phenomenon remains unresolved."
    else:
        layer = METHOD_REALIZATION
        reason = "The phenomenon may remain real, but the proposed standalone mechanism/method formulation leaves no residual beyond the recorded same-information reduction or supported counter-mechanism."

    experiment_run = payload.get("experiment_run_for_this_readjudication") is True
    authority = payload.get("authority") or {}
    experiment_alone = authority.get("experiment_alone_authorizes_dead_end") is True or payload.get("old_outcome_may_directly_authorize_dead_end") is True
    return {
        "closure_layer": layer,
        "failure_layer": layer,
        "memory_class": MEMORY_CLASS_BY_CLOSURE_LAYER[layer],
        "principle_update_allowed": layer == CORE_PRINCIPLE,
        "broader_core_principle_falsified": broader_falsified,
        "source_stop_class": stop_class,
        "failure_layer_reason": reason,
        "failure_layer_review_basis": "durable-readjudication-re-review-2026-08-18",
        "experiment_run_for_this_readjudication": experiment_run,
        "experiment_alone_authorizes_closure": experiment_alone,
    }


def problem_novelty_classification(*, basis: str) -> dict[str, Any]:
    """Type an upstream literature/theory collision without pretending it is an experiment failure."""
    return {
        "closure_layer": PROBLEM_NOVELTY,
        "failure_layer": None,
        "memory_class": MEMORY_CLASS_BY_CLOSURE_LAYER[PROBLEM_NOVELTY],
        "principle_update_allowed": False,
        "broader_core_principle_falsified": False,
        "source_stop_class": "PROBLEM_NOVELTY_STOP",
        "failure_layer_reason": "The exact paper-problem formulation stops before method/experiment scale-up because current primary work or mature theory already expresses the claimed object under matched information/scope.",
        "failure_layer_review_basis": basis,
        "experiment_run_for_this_readjudication": False,
        "experiment_alone_authorizes_closure": False,
    }


def normalize_closed_row(row: dict[str, Any]) -> dict[str, Any]:
    """Migrate legacy persistent rows without silently promoting them to core principle."""
    item = dict(row)
    closure_layer = str(item.get("closure_layer") or "").strip().lower()
    failure_layer = str(item.get("failure_layer") or "").strip().lower()
    if closure_layer in CLOSURE_LAYERS:
        item["closure_layer"] = closure_layer
        item["failure_layer"] = None if closure_layer == PROBLEM_NOVELTY else closure_layer
        item["memory_class"] = MEMORY_CLASS_BY_CLOSURE_LAYER[closure_layer]
        item["principle_update_allowed"] = closure_layer == CORE_PRINCIPLE
        item.setdefault("broader_core_principle_falsified", False)
        return item
    if failure_layer in SCIENTIFIC_FAILURE_LAYERS:
        item["closure_layer"] = failure_layer
        item["failure_layer"] = failure_layer
        item["memory_class"] = MEMORY_CLASS_BY_CLOSURE_LAYER[failure_layer]
        item["principle_update_allowed"] = failure_layer == CORE_PRINCIPLE
        item.setdefault("broader_core_principle_falsified", False)
        return item

    basin = str(item.get("basin") or "")
    disposition = str(item.get("disposition") or "")
    if basin.startswith("current-source-hard-veto-") or basin in {
        "skill-deployment-governance-contextual-acceptance",
        "near-miss-current-primary-collision",
        "near-miss-mature-theory-reduction",
    } or disposition in {"STOP_CURRENT_PRIMARY_COLLISION", "STOP_MATURE_THEORY_REDUCTION"}:
        item.update(problem_novelty_classification(basis="legacy-problem-reduction-migration-2026-08-18"))
        return item

    item.update({
        "closure_layer": METHOD_REALIZATION,
        "failure_layer": METHOD_REALIZATION,
        "memory_class": MEMORY_CLASS_BY_CLOSURE_LAYER[METHOD_REALIZATION],
        "principle_update_allowed": False,
        "broader_core_principle_falsified": False,
        "source_stop_class": "LEGACY_SCOPED_STOP",
        "failure_layer_reason": "Legacy scoped closure retained for search control; no explicit evidence promotes it beyond method realization.",
        "failure_layer_review_basis": "legacy-conservative-migration-2026-08-18",
        "experiment_run_for_this_readjudication": False,
        "experiment_alone_authorizes_closure": False,
    })
    return item


def audit_closed_row_layer(row: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    closure_layer = str(row.get("closure_layer") or "").strip().lower()
    failure_layer = str(row.get("failure_layer") or "").strip().lower()
    if closure_layer not in CLOSURE_LAYERS:
        blockers.append("closure-layer-missing-or-invalid")
    elif closure_layer == PROBLEM_NOVELTY:
        if failure_layer:
            blockers.append("problem-novelty-cannot-pretend-to-be-experimental-failure-layer")
        if row.get("memory_class") != MEMORY_CLASS_BY_CLOSURE_LAYER[PROBLEM_NOVELTY]:
            blockers.append("problem-novelty-memory-class-mismatch")
        if row.get("principle_update_allowed") is not False:
            blockers.append("problem-novelty-cannot-update-principle")
    else:
        if failure_layer not in SCIENTIFIC_FAILURE_LAYERS or failure_layer != closure_layer:
            blockers.append("scientific-failure-layer-missing-or-not-canonical")
        if row.get("memory_class") != MEMORY_CLASS_BY_CLOSURE_LAYER.get(closure_layer):
            blockers.append("scientific-memory-class-mismatch")
        if row.get("principle_update_allowed") is not (failure_layer == CORE_PRINCIPLE):
            blockers.append("principle-update-authority-does-not-match-failure-layer")
    if row.get("broader_core_principle_falsified") not in {True, False}:
        blockers.append("broader-core-falsification-flag-missing")
    if row.get("broader_core_principle_falsified") is True and failure_layer != CORE_PRINCIPLE:
        blockers.append("broader-core-falsification-requires-core-principle-layer")
    return {"passed": not blockers, "blockers": blockers, "closure_layer": closure_layer, "failure_layer": failure_layer or None}


def summarize_closure_layers(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(row.get("closure_layer") or "") for row in rows if isinstance(row, dict))
    return {layer: int(counts.get(layer, 0)) for layer in CLOSURE_LAYERS}


def summarize_scientific_failure_layers(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(row.get("failure_layer") or "") for row in rows if isinstance(row, dict))
    return {layer: int(counts.get(layer, 0)) for layer in SCIENTIFIC_FAILURE_LAYERS}
