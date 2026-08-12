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
    "decision-context-support-mismatch": ("operationalization", "for persistent updates, verify post-update full decision-context recurrence and intended intervention realization before interpreting downstream task failure"),
    "matched-simplification-tie": ("method-realization", "run matched simplification/disagreement mining before scale-up"),
    "true-negative": ("method-realization", "route through principle adjudication before any core-principle stop"),
}


def build_failure_asset_library(
    experiment_iteration: dict[str, Any],
    economy_gate: dict[str, Any] | None = None,
    post_c2_adjudication: dict[str, Any] | None = None,
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

    scienceworld = (post_c2_adjudication or {}).get("scienceworld_scope_evidence") or {}
    if scienceworld.get("f0_decision") == "SYMMETRIC_F0_HOLD" and scienceworld.get("scope_refinement_candidate"):
        diagnosis = "decision-context-support-mismatch"
        layer, precheck = REUSE_RULES[diagnosis]
        assets.append({
            "signature": f"{layer}:{diagnosis}",
            "idea_id": "scienceworld-persistent-correction-closure",
            "diagnosis": diagnosis,
            "affected_layer": layer,
            "reusable_precheck": precheck,
            "evidence_ref": f"scienceworld:f0={scienceworld.get('f0_sha256','')};diagnosis={scienceworld.get('diagnosis_sha256','')}",
            "does_not_imply": "method failure, core-principle failure, or rescue of the current ALFWorld memory paper",
            "memory_scope": "institutional-research-memory",
            "reuse_scope": {
                "environment": "ScienceWorld",
                "update_family": "persistent correction",
                "diagnosis": diagnosis,
                "affected_layer": layer,
            },
            "reuse_effectiveness": {"reuse_count": 1, "helped_count": 1, "hurt_count": 0, "status": "helped-protocol-audit"},
            "superseded_by": "",
            "last_revalidated": "2026-08-12",
            "source_decision": scienceworld.get("f0_decision"),
            "source_scope_refinement": scienceworld.get("scope_refinement_candidate"),
            "parent_evidence_for_current_paper": False,
            "can_authorize_current_paper": False,
            "authority_note": scienceworld.get("principle_authority"),
            "cross_surface_rule": scienceworld.get("relationship_to_current_paper"),
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
        },
        "assets": assets,
        "reusable_prechecks": reusable,
        "dead_end_registry": dead_end_registry,
    }
