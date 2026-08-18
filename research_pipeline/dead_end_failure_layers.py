from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


PROBLEM_NOVELTY = "PROBLEM_NOVELTY"
OPERATIONALIZATION_IDENTIFIABILITY = "OPERATIONALIZATION_IDENTIFIABILITY"
METHOD_FORMULATION = "METHOD_FORMULATION"
ASSUMPTION_SCOPE = "ASSUMPTION_SCOPE"
PRINCIPLE = "PRINCIPLE"

FAILURE_LAYERS = (
    PROBLEM_NOVELTY,
    OPERATIONALIZATION_IDENTIFIABILITY,
    METHOD_FORMULATION,
    ASSUMPTION_SCOPE,
    PRINCIPLE,
)

MEMORY_CLASS_BY_LAYER = {
    PROBLEM_NOVELTY: "PROBLEM_NOVELTY_STOP",
    OPERATIONALIZATION_IDENTIFIABILITY: "OPERATIONALIZATION_IDENTIFIABILITY_STOP",
    METHOD_FORMULATION: "METHOD_FORMULATION_STOP",
    ASSUMPTION_SCOPE: "ASSUMPTION_SCOPE_STOP",
    PRINCIPLE: "PRINCIPLE_STOP",
}

LAYER_BY_MEMORY_CLASS = {value: key for key, value in MEMORY_CLASS_BY_LAYER.items()}

# These five readjudications close a measurement/contrast/causal-path realization,
# not the broader scientific principle.  They were re-audited against the current
# failure-layer policy on 2026-08-18.
OPERATIONALIZATION_READJUDICATION_ARTIFACTS = {
    "autodesign-posterbench-causal-nopath-principle-readjudication-20260817.json",
    "p06-coverage-starvation-principle-readjudication-20260816.json",
    "shadow-p01-locked-set-causal-nopath-principle-readjudication-20260816.json",
    "shadow-v4-reciprocal-coupling-principle-readjudication-20260816.json",
    "shaper-scaling-comparator-principle-readjudication-20260817.json",
}

# These two readjudications show that a necessary feasibility/treatment-alignment
# condition for the scoped formulation does not hold.  They narrow/reframe scope;
# they do not establish a broader core-principle falsification.
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
    return False


def classify_readjudication(payload: dict[str, Any], artifact_ref: str | Path) -> dict[str, Any]:
    """Classify a certified scoped closure by the scientific layer that actually failed.

    ``principle_dead_end_certified`` in historical artifacts means that the exact
    formulation earned persistent search-blocking status. It must not be read as
    proof that the broader benchmark/phenomenon was falsified. A PRINCIPLE layer is
    used only when the artifact itself explicitly types the scoped scientific stop
    as PRINCIPLE_STOP (or explicitly records a broader/core falsification).
    """
    artifact_name = Path(str(artifact_ref)).name
    diagnosis = payload.get("principle_diagnosis") or {}
    counter = diagnosis.get("counter_explanation") or {}
    counter_type = str(counter.get("type") or diagnosis.get("counter_explanation_type") or "").strip().upper()

    stop_class = str(payload.get("stop_class") or "").strip().upper()
    broader_falsified = _broader_core_principle_falsified(payload)
    if stop_class == "PRINCIPLE_STOP" or broader_falsified:
        layer = PRINCIPLE
        reason = "The readjudication explicitly types the scoped scientific closure as PRINCIPLE_STOP (or records a broader/core falsification), after a scope-matched positive counter-explanation or exact same-information reduction."
    elif artifact_name in OPERATIONALIZATION_READJUDICATION_ARTIFACTS:
        layer = OPERATIONALIZATION_IDENTIFIABILITY
        reason = "The scoped claim fails because its measurement, comparison, identifiability, or causal-path bridge cannot support the claimed mechanism."
    elif artifact_name in ASSUMPTION_SCOPE_READJUDICATION_ARTIFACTS or counter_type == "NECESSARY_ASSUMPTION_REFUTED":
        layer = ASSUMPTION_SCOPE
        reason = "A necessary feasibility, treatment-alignment, or scope assumption for the scoped formulation does not hold; the broader phenomenon is not thereby falsified."
    elif counter_type == "IMPOSSIBILITY_OR_INVARIANCE":
        layer = OPERATIONALIZATION_IDENTIFIABILITY
        reason = "A structural witness shows that the proposed intervention/observable cannot affect or identify the claimed object under the recorded implementation."
    else:
        layer = METHOD_FORMULATION
        reason = "The phenomenon may remain real, but the proposed standalone mechanism/formulation leaves no residual beyond the recorded same-information reduction or supported counter-mechanism."

    experiment_run = payload.get("experiment_run_for_this_readjudication") is True
    authority = payload.get("authority") or {}
    experiment_alone = authority.get("experiment_alone_authorizes_dead_end") is True or payload.get("old_outcome_may_directly_authorize_dead_end") is True
    return {
        "failure_layer": layer,
        "memory_class": MEMORY_CLASS_BY_LAYER[layer],
        "principle_layer_closed": layer == PRINCIPLE,
        "broader_core_principle_falsified": broader_falsified,
        "source_stop_class": stop_class,
        "failure_layer_reason": reason,
        "failure_layer_review_basis": "durable-readjudication-re-review-2026-08-18",
        "experiment_run_for_this_readjudication": experiment_run,
        "experiment_alone_authorizes_closure": experiment_alone,
    }


def problem_novelty_classification(*, basis: str) -> dict[str, Any]:
    return {
        "failure_layer": PROBLEM_NOVELTY,
        "memory_class": MEMORY_CLASS_BY_LAYER[PROBLEM_NOVELTY],
        "principle_layer_closed": False,
        "broader_core_principle_falsified": False,
        "source_stop_class": "PROBLEM_STOP",
        "failure_layer_reason": "The exact paper-problem formulation is stopped before method/experiment scale-up because current primary work or mature theory already expresses the claimed object under matched information/scope.",
        "failure_layer_review_basis": basis,
        "experiment_run_for_this_readjudication": False,
        "experiment_alone_authorizes_closure": False,
    }


def normalize_closed_row(row: dict[str, Any]) -> dict[str, Any]:
    """Migrate legacy blocked rows without erasing a newer explicit layer label."""
    item = dict(row)
    layer = str(item.get("failure_layer") or "").strip().upper()
    if layer in FAILURE_LAYERS:
        item["failure_layer"] = layer
        item["memory_class"] = MEMORY_CLASS_BY_LAYER[layer]
        item["principle_layer_closed"] = layer == PRINCIPLE
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

    # A legacy principle-readjudication row should normally be replaced by the
    # current provenance-bound compiler output before reaching this fallback.
    # Preserve search blocking but classify conservatively as a method/formulation
    # stop rather than overclaiming core-principle falsification.
    item.update({
        "failure_layer": METHOD_FORMULATION,
        "memory_class": MEMORY_CLASS_BY_LAYER[METHOD_FORMULATION],
        "principle_layer_closed": False,
        "broader_core_principle_falsified": False,
        "source_stop_class": "LEGACY_SCOPED_STOP",
        "failure_layer_reason": "Legacy scoped closure retained for search control; no explicit principle-layer STOP or broader/core falsification evidence is present in this row.",
        "failure_layer_review_basis": "legacy-conservative-migration-2026-08-18",
        "experiment_run_for_this_readjudication": False,
        "experiment_alone_authorizes_closure": False,
    })
    return item


def summarize_failure_layers(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(row.get("failure_layer") or "") for row in rows if isinstance(row, dict))
    return {layer: int(counts.get(layer, 0)) for layer in FAILURE_LAYERS}
