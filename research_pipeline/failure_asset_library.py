from __future__ import annotations

from collections import Counter
from typing import Any


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "every_negative_or_blocked_run_yields_reusable_asset": True,
    "assets_are_retrieved_before_new_experiment_design": True,
    "dead_end_registry_is_preserved_across_runs": True,
    "failure_asset_must_name_affected_scientific_layer": True,
    "historical_failure_does_not_auto_block_new_scope": True,
    "institutional_memory_requires_scope_and_effectiveness_tracking": True,
    "stale_or_harmful_memory_can_be_superseded_not_deleted": True,
}

REFERENCES = [
    {"system": "MLEvolve", "adopted": "retrospective memory stores plans, code, metrics, and success/failure outcomes for future retrieval"},
    {"system": "InternAgent-1.5", "adopted": "persistent memory carries experiment outcomes across sessions"},
    {"system": "AutoResearchClaw / MetaClaw", "adopted": "pipeline failures become structured lessons and reusable safeguards across later runs"},
    {"system": "AutoSci / EvoScientist", "adopted": "separate project-active state from long-term reusable memory and track memory evolution rather than treating all historical lessons as timeless"},
]

REUSE_RULES = {
    "infrastructure-error": ("execution", "check runtime/provenance/trace readiness before scientific interpretation"),
    "budget-plan-mismatch": ("execution", "recompute full call graph and measured-throughput budget before launch"),
    "substrate-degenerate": ("experiment", "run competence/effect-variation qualification before method work"),
    "no-label-variation": ("experiment", "measure target entropy/variance before fitting"),
    "underfit": ("optimization", "inspect convergence/tiny-overfit before changing the scientific hypothesis"),
    "representation-signal-mismatch": ("operationalization", "require synthetic realizability and tiny-real fit for the representation"),
    "objective-claim-mismatch": ("operationalization", "freeze claim-objective-primary-metric alignment before training"),
    "matched-simplification-tie": ("method-realization", "run matched simplification/disagreement mining before scale-up"),
    "true-negative": ("method-realization", "route through principle adjudication before any core-principle stop"),
}


def build_failure_asset_library(
    experiment_iteration: dict[str, Any],
    economy_gate: dict[str, Any] | None = None,
    historical_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assets: list[dict[str, Any]] = []
    for node in experiment_iteration.get("nodes") or []:
        diagnosis = str(node.get("diagnosis") or "unknown")
        if diagnosis == "positive-signal":
            continue
        layer, precheck = REUSE_RULES.get(diagnosis, (str(node.get("diagnosis_layer") or "unknown"), "manual review required"))
        assets.append({
            "signature": f"{layer}:{diagnosis}",
            "idea_id": str(node.get("idea_id") or ""),
            "diagnosis": diagnosis,
            "affected_layer": layer,
            "reusable_precheck": precheck,
            "evidence_ref": str(node.get("artifact_dir") or ""),
            "does_not_imply": "core-principle failure" if layer != "core-principle" else "",
            "memory_scope": "institutional-research-memory",
            "reuse_scope": {"diagnosis": diagnosis, "affected_layer": layer},
            "reuse_effectiveness": {"reuse_count": 0, "helped_count": 0, "hurt_count": 0, "status": "not-yet-measured"},
            "superseded_by": "",
            "last_revalidated": "",
        })

    for record in (historical_evidence or {}).get("records") or []:
        diagnosis = str(record.get("diagnosis") or "historical-unknown")
        layer = str(record.get("affected_scientific_layer") or "unknown")
        provenance = record.get("provenance") or {}
        diagnosis_ref = provenance.get("posthoc_diagnosis") or {}
        assets.append({
            "signature": f"{layer}:{diagnosis}",
            "idea_id": "",
            "evidence_id": str(record.get("evidence_id") or ""),
            "diagnosis": diagnosis,
            "affected_layer": layer,
            "reusable_precheck": str(record.get("reusable_precheck") or "manual review required"),
            "evidence_ref": str(diagnosis_ref.get("path") or ""),
            "evidence_timing": str(record.get("evidence_timing") or "historical"),
            "evidence_class": str(record.get("evidence_class") or "historical"),
            "original_decision": str(record.get("original_decision") or ""),
            "original_decision_preserved": bool(record.get("original_decision_preserved")),
            "does_not_imply": "core-principle failure or execution authority",
            "memory_scope": "institutional-research-memory",
            "reuse_scope": {
                "diagnosis": diagnosis,
                "affected_layer": layer,
                "condition": str(record.get("omitted_condition") or ""),
            },
            "reuse_effectiveness": {"reuse_count": 0, "helped_count": 0, "hurt_count": 0, "status": "not-yet-measured"},
            "superseded_by": "",
            "last_revalidated": "",
            "scientific_authority": {
                "active_principle_belief_update_allowed": bool(record.get("active_principle_belief_update_allowed")),
                "principle_falsified": bool(record.get("principle_falsified")),
                "retrospective_principle_certificate_allowed": bool(record.get("retrospective_principle_certificate_allowed")),
                "execution_authorized": bool(record.get("execution_authorized")),
                "scale_up_authorized": bool(record.get("scale_up_authorized")),
            },
            "provenance": provenance,
        })

    signature_counts = Counter(asset["signature"] for asset in assets)
    reusable = []
    seen: set[str] = set()
    for asset in assets:
        signature = asset["signature"]
        if signature in seen:
            continue
        seen.add(signature)
        reusable.append({
            "signature": signature,
            "affected_layer": asset["affected_layer"],
            "reusable_precheck": asset["reusable_precheck"],
            "occurrences": signature_counts[signature],
            "reuse_effectiveness": {"reuse_count": 0, "helped_count": 0, "hurt_count": 0, "status": "not-yet-measured"},
            "revalidation_required_after_scope_change": True,
        })

    econ = (economy_gate or {}).get("summary") or {}
    dead_end_registry = {
        "matched_simplification_stops": int(econ.get("matched_simplification_stops") or 0),
        "substrate_stops": int(econ.get("substrate_stops") or 0),
        "rule": "A dead end is reusable evidence about a formulation/substrate, not a permanent ban on a materially changed principle or scope.",
    }
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "references": REFERENCES,
        "summary": {
            "assets": len(assets),
            "unique_signatures": len(reusable),
            "economy_dead_ends": dead_end_registry["matched_simplification_stops"] + dead_end_registry["substrate_stops"],
            "historical_posthoc_assets": sum(asset.get("evidence_timing") == "post-hoc" for asset in assets),
        },
        "assets": assets,
        "reusable_prechecks": reusable,
        "dead_end_registry": dead_end_registry,
    }
