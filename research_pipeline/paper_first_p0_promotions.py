from __future__ import annotations

from typing import Any

PROMOTIONS: dict[str, dict[str, Any]] = {
    "future-learnability-preserving-self-evolution": {
        "incubation_id": "PF-1", "code": "A-8", "group": "A",
        "title": {"zh": "面向未来可学习性的自进化", "en": "Future-Learnability-Preserving Self-Evolution"},
        "paper_problem": "A persistent update may preserve current reward and old-task retention yet reduce the agent's capacity to learn the next task efficiently.",
        "novelty_boundary": "Retention/capability preservation protects current or old behavior; this paper treats future adaptation capacity as a separate update-admission quantity.",
        "principle": "Current capability is state value; future learnability is option value. An update can preserve the former while changing the latter.",
        "mechanism": "Probe candidate updates with an identical sealed second-stage adaptation budget and gate commits using future-adaptation AUC after matching current gain and retention.",
        "baseline": "Current-gain + retention gate with the same candidate updates, tasks, model calls, and second-stage adaptation budget.",
        "truth": "ALFWorld environment success on sealed future task families under identical second-stage adaptation budget.",
        "minimum_p0": "Find matched candidate-update pairs with similar current/retention performance, then compare future-adaptation AUC and improvement-per-example on sealed task families.",
        "stop": "Stop the standalone method if future-learnability deltas vanish after matching current gain/retention or are fully predicted by those quantities.",
        "setup": ("gpu-two-stage-adaptation-first", "Qwen2.5-7B-Instruct + ALFWorld sealed two-stage adaptation", 48),
        "economy": {
            "substrate_inventory": {"effective_candidates_min": 3, "fresh_heldout_min": 4, "reserve_fraction_min": 0.25, "target_variation_rule": "at least two matched update pairs with nonzero future-adaptation delta"},
            "causal_unit": "candidate-update x sealed-future-adaptation episode", "prediction_unit": "candidate-update x sealed-future-adaptation episode",
            "effect_observable": "future adaptation AUC / improvement-per-example after matching current gain and retention",
            "effect_moderators": "task family; initial update; baseline current success; retention delta", "effect_stability_scope": "Qwen2.5-7B local P0 only; second model locked",
            "aggregation_risk": "family-level cancellation can hide update-specific plasticity debt; report per-update and per-family before macro averaging",
            "cheapest_falsifier": "four initial updates, matched current/retention probes, one identical bounded second-stage adaptation, sealed future probes",
            "decision_changing_outcomes": "nonzero future-learnability separation at matched current/retention vs no separation",
            "abandonment_condition": "no matched pairs or future-adaptation effect collapses to current/retention predictors",
        },
    },
    "cross-surface-repair-routing": {
        "incubation_id": "PF-2", "code": "E-5", "group": "E",
        "title": {"zh": "跨 Agent 更新表面的因果修复路由", "en": "Causal Routing Across Agent Update Surfaces"},
        "paper_problem": "The same observed failure may be repaired at prompt/memory, workflow, tool/code, or weights, but most systems choose the update surface before causal evidence is collected.",
        "novelty_boundary": "Existing localization work searches edits inside a chosen workflow/source surface; this problem is upstream ownership selection across persistent update surfaces.",
        "principle": "The preferred repair is the lowest-scope intervention that is causally sufficient, transfers to held-out cases, and minimizes collateral change.",
        "mechanism": "Run same-information minimal interventions on declared repair surfaces, estimate causal repair benefit/collateral regression/cost, and route to the smallest sufficient surface.",
        "baseline": "Best fixed surface and same-evidence LLM surface selector, both under identical intervention and evaluation budgets.",
        "truth": "ALFWorld environment outcome plus controlled hidden fault ownership in the local falsifier; later paper evidence must use natural failures too.",
        "minimum_p0": "Controlled prompt/workflow/tool fault table with matched repairs; require heterogeneous repair ownership and held-out advantage over fixed-surface routing.",
        "stop": "Stop if one surface dominates all faults, ownership is recoverable from trivial metadata, or a same-evidence simple selector matches the router.",
        "setup": ("gpu-shared-surface-intervention-first", "Qwen2.5-7B-Instruct + ALFWorld controlled fault x repair-surface table", 36),
        "economy": {
            "substrate_inventory": {"effective_candidates_min": 18, "fresh_heldout_min": 9, "reserve_fraction_min": 0.25, "target_variation_rule": "at least two fault families require different minimal sufficient repair surfaces"},
            "causal_unit": "fault-instance x repair-surface intervention", "prediction_unit": "fault-instance x repair-surface intervention",
            "effect_observable": "paired success recovery, held-out transfer, collateral regression, and intervention cost",
            "effect_moderators": "fault family; task family; repair surface", "effect_stability_scope": "controlled ALFWorld local P0; natural-failure validation required before paper claim",
            "aggregation_risk": "oracle injected ownership can make routing trivial; metadata is hidden and outcome-only identification is required",
            "cheapest_falsifier": "three fault families x three repair surfaces on a small held-out ALFWorld task set",
            "decision_changing_outcomes": "heterogeneous minimal-surface ownership plus outcome-based routing headroom vs fixed/simple baselines",
            "abandonment_condition": "single-surface dominance or no outcome-identifiable ownership",
        },
    },
    "diagnosability-preserving-self-evolution": {
        "incubation_id": "PF-4", "code": "C-7", "group": "C",
        "title": {"zh": "保持可诊断性的自进化", "en": "Diagnosability-Preserving Self-Evolution"},
        "paper_problem": "An update can improve task success while making later failures harder to localize by erasing trace distinctions or provenance signals.",
        "novelty_boundary": "Observability is commonly used to improve the harness; this work treats diagnosability itself as a post-update invariant that can veto a commit.",
        "principle": "An agent should not purchase current capability by consuming the evidence needed to diagnose its next failure.",
        "mechanism": "Use sealed failure probes and a frozen external cause observer; commit only if task utility improves without degrading failure-cause separability/provenance coverage.",
        "baseline": "Task regression + trace completeness and observability-only optimization under the same probes.",
        "truth": "Controlled hidden fault labels plus environment success in F0; later natural-failure repair cost is the stronger external validation.",
        "minimum_p0": "Use the shared controlled-fault table to freeze a simple diagnostic observer on development tasks and test post-update cause localization on held-out tasks.",
        "stop": "Stop if diagnosability changes are fully explained by trace length/completeness or do not predict downstream repair cost/accuracy.",
        "setup": ("shared-surface-diagnostic-analysis", "Shared PF-2 ALFWorld controlled fault x repair-surface table", 36),
        "economy": {
            "substrate_inventory": {"effective_candidates_min": 3, "fresh_heldout_min": 9, "reserve_fraction_min": 0.25, "target_variation_rule": "at least three fault causes with nontrivial diagnostic separability"},
            "causal_unit": "candidate-update x sealed diagnostic fault probe", "prediction_unit": "candidate-update x sealed diagnostic fault probe",
            "effect_observable": "frozen-observer cause localization accuracy/AUROC and provenance coverage at matched task utility",
            "effect_moderators": "fault cause; update surface; task family", "effect_stability_scope": "shared ALFWorld local P0 only",
            "aggregation_risk": "successful repair can remove the original fault signature; diagnosability is measured on independent sealed fault probes after the update",
            "cheapest_falsifier": "reuse PF-2 collection and evaluate a frozen simple observer before/after candidate updates",
            "decision_changing_outcomes": "utility-matched updates with reproducibly different diagnostic separability vs trace-completeness baseline",
            "abandonment_condition": "no diagnostic variation beyond trace completeness or no relation to future repair difficulty",
        },
    },
    "failure-mode-transport-under-self-evolution": {
        "incubation_id": "PF-6", "code": "A-9", "group": "A",
        "title": {"zh": "自进化中的失败模式迁移", "en": "Failure-Mode Transport Under Self-Evolution"},
        "paper_problem": "Aggregate success can improve while residual failure probability moves toward more silent, severe, or unrecoverable modes.",
        "novelty_boundary": "Static failure taxonomies and aggregate regression do not measure paired longitudinal movement of failure probability mass under a persistent update.",
        "principle": "Update quality depends on where failure mass moves, not only on total failure probability.",
        "mechanism": "Estimate a paired before/after Failure Transport Matrix over preregistered failure classes and gate updates that substitute ordinary failures with higher-risk modes.",
        "baseline": "Aggregate success/regression and static failure-weighted risk using the same paired tasks.",
        "truth": "ALFWorld environment outcome plus deterministic trace-derived failure classes with independent classification rules frozen before analysis.",
        "minimum_p0": "Reuse the shared PF-2 collection; classify paired pre/post traces into preregistered failure modes and test whether equal/similar success deltas can hide different transport risk.",
        "stop": "Stop if paired transport adds no decision-relevant information beyond aggregate success/static risk or failure classes are not stable/reproducible.",
        "setup": ("shared-failure-transport-analysis", "Shared PF-2 ALFWorld controlled fault x repair-surface table", 36),
        "economy": {
            "substrate_inventory": {"effective_candidates_min": 18, "fresh_heldout_min": 9, "reserve_fraction_min": 0.25, "target_variation_rule": "at least three preregistered failure classes and non-diagonal before/after transitions"},
            "causal_unit": "paired task before/after persistent update", "prediction_unit": "paired task before/after persistent update",
            "effect_observable": "failure-class transport matrix and risk-weighted transport delta",
            "effect_moderators": "task family; fault class; update surface", "effect_stability_scope": "shared ALFWorld local P0 only",
            "aggregation_risk": "macro success can cancel harmful substitutions; report full transition matrix and per-class mass",
            "cheapest_falsifier": "reuse PF-2 paired traces and deterministic preregistered failure taxonomy",
            "decision_changing_outcomes": "same/similar aggregate success with materially different transport risk vs transport fully determined by aggregate success",
            "abandonment_condition": "no stable non-diagonal transport or transport never changes an update decision",
        },
    },
}

AUTHORITY: dict[str, Any] = {
    "promotion_authorized": False,
    "local_validation_authorized": False,
    "full_experiment_authorized": False,
    "authority_status": "NO_EXPLICIT_USER_P0_PROMOTION_AUTHORITY",
    "basis": "The paper-first authority preceding these executions explicitly kept local validation locked; no external user-authorization artifact is referenced by the promotion code.",
    "executed_f0_disposition": "PREMATURE_UNAUTHORIZED_LOCAL_VALIDATION_DIAGNOSTIC_ONLY",
    "rule": "Executed traces are preserved as historical diagnostics but cannot create P0 lifecycle, method-admission, principle, or scale-up authority.",
}

# Keep the four paper/method specifications as design candidates and historical
# execution provenance, but expose no live P0 promotion until an external human
# authority artifact explicitly authorizes that transition.
AUTHORIZED_PROMOTIONS: dict[str, dict[str, Any]] = {}
PROMOTION_BY_INCUBATION = {
    str(row["incubation_id"]): idea_id for idea_id, row in AUTHORIZED_PROMOTIONS.items()
}


def independent_row(idea_id: str) -> dict[str, Any]:
    if idea_id not in AUTHORIZED_PROMOTIONS:
        raise RuntimeError(f"paper-first P0 promotion is not authorized: {idea_id}")
    spec = AUTHORIZED_PROMOTIONS[idea_id]
    return {
        "terminal_state": "p0",
        "title": spec["title"],
        "code": spec["code"],
        "group": spec["group"],
        "source_incubation_id": spec["incubation_id"],
        "paper_first_contract_version": "2026-08-12-v1",
        "current_fact": {
            "zh": "经 Paper-first novelty premortem 与用户明确授权进入 P0 lifecycle。当前只授权局部 F0/P0-Support 资格验证；方法结论、扩预算、第二 backbone 与 full experiment 均保持锁定，必须经过 Economy、Updater/Support、Pre-Experiment 8/8 与 Method Freeze。",
            "en": "Promoted into the P0 lifecycle after the paper-first novelty premortem and explicit user authorization. Only local F0/P0-Support qualification is currently authorized; method conclusions, budget expansion, a second backbone, and full experiments remain locked behind Economy, updater/support qualification, Pre-Experiment 8/8, and Method Freeze."
        },
        "p0_entry": {"date": "2026-08-12", "basis": "explicit-user-paper-first-p0-promotion", "execution_authorized": False},
        "paper_problem": spec["paper_problem"],
        "novelty_boundary": spec["novelty_boundary"],
        "final_parent_mechanism": {"en": spec["mechanism"], "zh": spec["mechanism"]},
        "strongest_baseline": {"en": spec["baseline"], "zh": spec["baseline"]},
        "minimum_p0": {"en": spec["minimum_p0"], "zh": spec["minimum_p0"]},
        "exact_stop": {"en": spec["stop"], "zh": spec["stop"]},
        "economy_contract": spec["economy"],
    }


def promotion_summary() -> dict[str, Any]:
    return {"promoted": len(PROMOTIONS), "codes": [row["code"] for row in PROMOTIONS.values()], "incubation_ids": [row["incubation_id"] for row in PROMOTIONS.values()]}
