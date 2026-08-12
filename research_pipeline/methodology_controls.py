from __future__ import annotations

from typing import Any


POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "cross_cutting_controls_do_not_create_a_seventh_functional_layer": True,
    "controls_inherit_authority_from_their_owner_component": True,
    "unmeasured_controls_must_report_spec_status_not_claim_improvement": True,
    "post_outcome_protocol_changes_require_a_new_registered_contract": True,
    "search_or_tool_access_must_not_leak_hidden_evaluation_answers": True,
    "reproducibility_requires_reexecution_not_only_trace_presence": True,
}


def build_methodology_controls_state() -> dict[str, Any]:
    controls = [
        {
            "key": "exploration-frontier",
            "owner_component": "wide-search-ideation",
            "primary_layer": "paper-design",
            "status": "spec-ready-not-yet-scored",
            "purpose": {
                "en": "Detect portfolio collapse toward a small neighborhood of seed literature even when individual ideas appear novel.",
                "zh": "检测 Idea 组合是否虽然单项看似新颖，却整体塌缩在 seed 文献附近的同一小片区域。",
            },
            "measures": [
                "quality-thresholded diversity yield",
                "distance from seed literature",
                "pairwise semantic dispersion",
                "novelty-axis coverage",
                "lineage/branch entropy",
            ],
            "rules": {
                "novelty_prompt_alone_is_not_evidence_of_search_breadth": True,
                "quality_and_diversity_are_joint_objectives": True,
                "portfolio_level_collapse_is_distinct_from_pairwise_collision": True,
                "low_breadth_triggers_search_reallocation_not_paper_rejection": True,
            },
            "design_sources": [
                "AI Research Agents Narrow Scientific Exploration",
                "IDEAgent",
                "Heuresis",
                "SwarmResearch",
            ],
        },
        {
            "key": "experimental-design-integrity",
            "owner_component": "protocol-and-replay",
            "primary_layer": "experiment-design",
            "status": "contract-ready-not-yet-retrospectively-scored",
            "purpose": {
                "en": "Freeze researcher degrees of freedom before outcomes are visible and prevent web/tool access from contaminating hidden evaluation.",
                "zh": "在看到结果前冻结实验者自由度，并防止联网检索或工具访问污染 hidden evaluation。",
            },
            "preregistration_fields": [
                "model/checkpoint and inference settings",
                "prompt/scaffold and tool policy",
                "task/sample split",
                "metric and outcome semantics",
                "analysis plan and statistical test",
                "randomness/replication and stochastic-agent variance plan",
                "stopping/exclusion rules",
                "allowed adaptations and fallback path",
                "for persistent updates: post-update decision-context support and intended-effect realization check",
            ],
            "contamination_classes": [
                "benchmark-metadata leakage",
                "question-context leakage",
                "explicit-answer leakage",
            ],
            "rules": {
                "outcome_contingent_redesign_requires_new_contract": True,
                "search_trajectory_is_part_of_protocol_provenance": True,
                "hidden_evaluation_access_requires_explicit_allowlist": True,
                "contaminated_runs_cannot_support_method_or_principle_claims": True,
                "persistent_update_support_must_be_checked_under_post_update_policy": True,
                "observation_recurrence_is_not_equivalent_to_full_decision_context_recurrence": True,
                "local_supervision_is_not_behaviorally_realized_until_the_updated_policy_revisits_the_full_context_and_executes_the_intended_intervention": True,
                "failed_effect_realization_is_protocol_or_operationalization_evidence_before_it_is_method_failure": True,
                "historical_runs_predating_this_rule_are_not_retroactively_reclassified": True,
            },
            "design_sources": [
                "Preregistration for Experiments with AI Agents",
                "Search-Time Contamination in Deep Research Agents",
                "AstaBench",
                "An Experimental Design Approach to Evaluating Agentic AI's Autonomous Model Discovery",
                "DAgger / induced observation-distribution consistency",
                "HERO / current-decision-context aligned agentic self-distillation",
                "ReOPD / reliability-aware on-policy prefix distribution",
                "SkillEvolver / deployed-skill silent-bypass audit",
            ],
        },
        {
            "key": "reproducibility-readiness",
            "owner_component": "literature-evidence-integrity",
            "primary_layer": "evidence-knowledge",
            "status": "spec-ready-not-yet-independent-reexecuted",
            "purpose": {
                "en": "Require a third party to reconstruct and rerun the result-generating workflow instead of treating logs or citations as sufficient reproducibility evidence.",
                "zh": "要求第三方能够重建并重跑结果生成流程，而不是把“有日志/有引用”误当成已经可复现。",
            },
            "required_graph": [
                "source/data dependencies",
                "preprocessing/transformation steps",
                "method/configuration",
                "execution commands and environment",
                "metrics/analysis",
                "figure/table/claim outputs",
            ],
            "required_artifacts": [
                "dependency-aware workflow graph",
                "versioned environment manifest",
                "re-execution entry point",
                "seed/data split record",
                "failure/recovery notes",
                "independent reproduction report",
            ],
            "rules": {
                "claim_traceability_is_not_equivalent_to_reproducibility": True,
                "reproduction_must_execute_without_copying_checked_in_results": True,
                "environment_or_dependency_failure_is_reported_separately_from_scientific_failure": True,
                "paper_ready_status_requires_independent_reexecution_for_load_bearing_results": True,
            },
            "design_sources": [
                "ARA: Agentic Reproducibility Assessment",
                "Artisan",
                "ArtifactCopilot",
                "Scaling Reproducibility",
            ],
        },
    ]
    return {
        "schema_version": "1.0",
        "policy": POLICY,
        "controls": controls,
        "summary": {
            "controls": len(controls),
            "primary_components_added": 0,
            "functional_layers_added": 0,
            "measured_controls": sum(str(row["status"]).startswith("measured") for row in controls),
            "spec_or_contract_ready": sum("ready" in str(row["status"]) for row in controls),
        },
        "merge_only_external_designs": [
            {
                "system": "EurekAgent",
                "reason": "permissions/artifact/budget/HITL environment engineering already maps to Runtime & Authority; no duplicate component is required",
            }
        ],
    }
