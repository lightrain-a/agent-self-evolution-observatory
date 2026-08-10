from __future__ import annotations

from collections import Counter
from typing import Any


CHECKS: tuple[dict[str, str], ...] = (
    {"key":"claim_alignment", "group":"claim", "question":"Does the training objective directly optimize the quantity required by the paper claim?"},
    {"key":"target_variation", "group":"identifiability", "question":"Does the target have enough entropy/variance to expose the claimed decision boundary?"},
    {"key":"baseline_disagreement", "group":"identifiability", "question":"Can the proposed method and strongest simplification make different decisions on the frozen discovery pool?"},
    {"key":"representability", "group":"model", "question":"Can the chosen representation/model express the hypothesized mechanism on a synthetic realizability test?"},
    {"key":"tiny_overfit", "group":"optimization", "question":"Can the learner fit a tiny real discovery subset before a scientific run is allowed?"},
    {"key":"competence_window", "group":"substrate", "question":"Is the base agent neither degenerate-easy nor degenerate-hard, with both successes and failures?"},
    {"key":"effect_variation", "group":"substrate", "question":"Do candidate interventions produce both useful and harmful/non-useful effects?"},
    {"key":"cost_plan", "group":"execution", "question":"Are unique inference count, measured throughput, expected wall time, and hard cap frozen before execution?"},
    {"key":"provenance_plan", "group":"execution", "question":"Are streaming traces, checkpoints, output locking, commit/source hashes, and resume rules specified?"},
    {"key":"interpretation_matrix", "group":"scientific", "question":"Is every important observable outcome mapped in advance to scientific/experimental diagnosis and allowed next action?"},
)


POLICY: dict[str, Any] = {
    "schema_version":"1.0",
    "all_checks_required":True,
    "p0_execution_requires_pre_p0_pass":True,
    "missing_contract_blocks_execution":True,
    "underfit_is_not_scientific_failure":True,
    "zero_disagreement_blocks_gpu_p0":True,
    "zero_target_variation_blocks_training":True,
    "failed_realizability_blocks_training":True,
    "outcome_interpretation_must_be_preregistered":True,
    "automatic_override_forbidden":True,
}


# Current contracts intentionally encode what the retrospective Round-1 audit taught us.
# They are not positive scientific results. A repaired child must replace the failed
# preflight evidence before it can become executable.
CURRENT_CONTRACTS: dict[str, dict[str, Any]] = {
    "update-trust-region": {
        "code":"A-1",
        "claim":"A cross-surface behavioral trust-region signal should reject harmful persistent updates while preserving useful updates.",
        "objective":"Predict harmful-update admission from gain plus behavioral divergence.",
        "primary_metric":"Harmful accepted updates at matched useful-update acceptance.",
        "checks":{
            "claim_alignment":True,
            "target_variation":True,
            "baseline_disagreement":True,
            "representability":False,
            "tiny_overfit":False,
            "competence_window":True,
            "effect_variation":True,
            "cost_plan":True,
            "provenance_plan":True,
            "interpretation_matrix":True,
        },
        "evidence":{
            "representability":"Retrospective canonical Round-1 converged at chance validation AUC; current global divergence representation is not sufficient.",
            "tiny_overfit":"No pre-GPU tiny-real-set overfit gate existed before the run.",
        },
        "required_next":"A1-R1 must pass retrospective/synthetic contextual-divergence realizability and tiny-overfit before another GPU P0.",
    },
    "budgeted-evolution-controller": {
        "code":"A-2",
        "claim":"A persistent update controller can save update calls by learning when to continue, stop, or rollback.",
        "objective":"Predict whether one more persistent update is worth applying.",
        "primary_metric":"Calls saved at matched final task utility and regression.",
        "checks":{
            "claim_alignment":True,
            "target_variation":False,
            "baseline_disagreement":False,
            "representability":True,
            "tiny_overfit":False,
            "competence_window":True,
            "effect_variation":True,
            "cost_plan":True,
            "provenance_plan":True,
            "interpretation_matrix":True,
        },
        "evidence":{
            "target_variation":"Canonical Round-1 produced no optimal-stop label variation.",
            "baseline_disagreement":"Without early/late/rollback-optimal sequence archetypes, controller policies cannot expose a meaningful decision disagreement.",
        },
        "required_next":"A2-R1 must prove sequence-archetype target entropy and controller/baseline disagreement offline before training.",
    },
    "outcome-equivalent-trajectory-contrast": {
        "code":"B-1",
        "claim":"Process-robust intervention utility should improve lesson admission beyond ordinary utility-only selection.",
        "objective":"Rank lessons by cross-process memory-on/off effect stability.",
        "primary_metric":"Hidden future-task effect and negative transfer at matched replay/memory budget.",
        "checks":{
            "claim_alignment":True,
            "target_variation":True,
            "baseline_disagreement":False,
            "representability":True,
            "tiny_overfit":True,
            "competence_window":True,
            "effect_variation":True,
            "cost_plan":True,
            "provenance_plan":True,
            "interpretation_matrix":True,
        },
        "evidence":{
            "baseline_disagreement":"Canonical Round-1 single-source, consensus, utility-only, and cross-process-robust selected the same lessons.",
        },
        "required_next":"Mine a frozen offline pool for utility-only vs process-robust decision disagreements; merge if none exist.",
    },
    "workflow-generalization-certificate": {
        "code":"E-1",
        "claim":"A frozen paired edit-effect policy should choose the best local workflow edit on unseen workflow contexts without target-time search.",
        "objective":"Canonical Round-1 optimized positive-edit classification rather than conditional best-edit ranking.",
        "primary_metric":"Top-1 best-edit selection and edit regret versus global-best/simple editors.",
        "checks":{
            "claim_alignment":False,
            "target_variation":True,
            "baseline_disagreement":False,
            "representability":True,
            "tiny_overfit":True,
            "competence_window":True,
            "effect_variation":True,
            "cost_plan":True,
            "provenance_plan":True,
            "interpretation_matrix":True,
        },
        "evidence":{
            "claim_alignment":"Binary effect AUC reached 1.0 while calibration top-1 edit accuracy remained 0; objective and paper claim were misaligned.",
            "baseline_disagreement":"The learned editor did not beat global-best edit selection on calibration.",
        },
        "required_next":"E1-R1 must use pairwise/listwise edit ranking and beat global-best on calibration before hidden workflows or GPU P0 are opened.",
    },
}


def audit_contract(idea_id: str, contract: dict[str, Any] | None) -> dict[str, Any]:
    if not contract:
        return {
            "idea_id":idea_id,
            "code":"--",
            "status":"missing-contract",
            "execution_ready":False,
            "passed":0,
            "total":len(CHECKS),
            "blockers":["missing-pre-p0-contract"],
            "checks":[],
            "required_next":"Create and validate a Pre-P0 identifiability contract before execution.",
            "estimated_voi":"unknown",
        }
    values = contract.get("checks") or {}
    rows=[]; blockers=[]
    for spec in CHECKS:
        passed = bool(values.get(spec["key"], False))
        rows.append({**spec,"pass":passed,"evidence":str((contract.get("evidence") or {}).get(spec["key"]) or "")})
        if not passed: blockers.append(spec["key"])
    execution_ready = not blockers
    # If identifiability gates fail, a new GPU pilot has near-zero decision value until repaired.
    critical = {"claim_alignment","target_variation","baseline_disagreement","representability","competence_window","effect_variation"}
    estimated_voi = "eligible" if execution_ready else ("near-zero-before-repair" if critical.intersection(blockers) else "blocked-by-execution-readiness")
    return {
        "idea_id":idea_id,
        "code":contract.get("code") or "--",
        "status":"pass" if execution_ready else "repair-required",
        "execution_ready":execution_ready,
        "passed":sum(row["pass"] for row in rows),
        "total":len(rows),
        "blockers":blockers,
        "checks":rows,
        "claim":contract.get("claim"),
        "objective":contract.get("objective"),
        "primary_metric":contract.get("primary_metric"),
        "required_next":contract.get("required_next"),
        "estimated_voi":estimated_voi,
    }


def build_pre_p0_identifiability_audit(idea_bank: dict[str, Any] | None = None) -> dict[str, Any]:
    known_ids = {str(idea.get("id")) for idea in (idea_bank or {}).get("passed_ideas") or []}
    ids = [idea_id for idea_id in CURRENT_CONTRACTS if not known_ids or idea_id in known_ids]
    nodes = [audit_contract(idea_id, CURRENT_CONTRACTS.get(idea_id)) for idea_id in ids]
    statuses=Counter(node["status"] for node in nodes)
    blockers=Counter(blocker for node in nodes for blocker in node["blockers"])
    return {
        "schema_version":"1.0",
        "policy":POLICY,
        "checks":list(CHECKS),
        "summary":{
            "audited":len(nodes),
            "execution_ready":sum(node["execution_ready"] for node in nodes),
            "blocked":sum(not node["execution_ready"] for node in nodes),
            "status_counts":dict(statuses),
            "blocker_counts":dict(blockers.most_common()),
        },
        "nodes":nodes,
    }


def execution_status(idea_id: str) -> str:
    return str(audit_contract(idea_id, CURRENT_CONTRACTS.get(idea_id))["status"])


def execution_ready(idea_id: str) -> bool:
    return execution_status(idea_id) == "pass"
