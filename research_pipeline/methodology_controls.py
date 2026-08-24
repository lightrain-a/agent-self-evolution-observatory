from __future__ import annotations

import json
from pathlib import Path
from typing import Any


C1_PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
C1_GATE_PROFILE = "C1_EXECUTABLE_CLOSURE_V3"
C1_GATE_ID = "C1_EXECUTABLE_CLOSURE_REVIEWER_GATE_V3"
C1_REVISION_PROGRAM = Path(__file__).resolve().parents[1] / "paper_drafts" / "c1-proxy-reward-stanford-r3-20260824" / "mechanism-closure-program-20260824.json"
C1_REQUIRED_BASELINE_IDS = frozenset(
    {
        "neutral-metadata-memory",
        "generic-common-core-residual",
        "semantic-applicability",
        "query-conditioned-reuse",
        "provenance-authorization",
        "success-failure-reflection",
    }
)
C1_ALLOWED_NOVEL_COMPONENT_IDS = frozenset(
    {
        "same-trajectory-counterfactual-branch-residual",
        "evidence-gated-trigger-authority",
    }
)
C1_REQUIRED_VALIDITY_STATES = {"SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"}
C1_EXECUTABLE_CLOSURE_REVIEWER_GATE: dict[str, Any] = {
    "gate": C1_GATE_ID,
    "profile": C1_GATE_PROFILE,
    "paper_id": C1_PAPER_ID,
    "status": "REGISTERED_FAIL_CLOSED_ZERO_AUTHORITY",
    "pass_semantics": "D0_DESIGN_ELIGIBLE_ONLY",
    "baseline_only_component_ids": sorted(C1_REQUIRED_BASELINE_IDS),
    "only_admissible_novel_component_ids": sorted(C1_ALLOWED_NOVEL_COMPONENT_IDS),
    "forbidden_shortcuts": [
        "neutral or metadata memory promoted from baseline to novelty",
        "generic common-core/residual factorization promoted from baseline to novelty",
        "semantic applicability or similarity used as evidence authority by itself",
        "reward/success/failure treatment label used to validate its own branch residual",
        "unbound or non-receipted evidence used to grant branch-specific trigger authority",
        "D0 pass used as provider, GPU, experiment, claim-expansion, or submission authority",
    ],
    "authority": {
        "scientific": False,
        "experiment": False,
        "provider": False,
        "gpu": False,
        "claim_expansion": False,
        "submission": False,
    },
}


def _all_authority_false(authority: Any) -> bool:
    return isinstance(authority, dict) and bool(authority) and not any(bool(value) for value in authority.values())


def adjudicate_c1_executable_closure_gate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Fail-closed pre-D0 reviewer gate for the frozen C1 executable-closure residual.

    The gate is deliberately paper-specific. It can grant D0 *design* eligibility only;
    it never grants scientific execution, provider, GPU, claim-expansion, or submission authority.
    """
    errors: list[str] = []
    if candidate.get("paper_id") != C1_PAPER_ID:
        errors.append("paper_id does not match the frozen C1 paper")
    if candidate.get("gate_profile") != C1_GATE_PROFILE:
        errors.append("gate_profile is not C1_EXECUTABLE_CLOSURE_V3")
    if candidate.get("gate_id") != C1_GATE_ID:
        errors.append("gate_id does not match the registered C1 reviewer gate")

    baseline_ids = set(candidate.get("baseline_only_component_ids") or [])
    novel_ids = set(candidate.get("proposed_novel_component_ids") or [])
    missing_baselines = sorted(C1_REQUIRED_BASELINE_IDS - baseline_ids)
    if missing_baselines:
        errors.append("required baseline-only components missing: " + ", ".join(missing_baselines))
    if novel_ids != C1_ALLOWED_NOVEL_COMPONENT_IDS:
        errors.append(
            "C1 novelty set must be exactly same-trajectory counterfactual branch residual + evidence-gated trigger authority"
        )
    if baseline_ids & novel_ids:
        errors.append("baseline-only components re-enter the novelty set")

    residual = candidate.get("scientific_residual") or {}
    if not str(residual.get("statement") or "").strip():
        errors.append("scientific residual is not explicitly stated")
    required_residual_flags = {
        "same_trajectory_counterfactual_pair_required": "same-trajectory counterfactual identity is not required",
        "byte_identical_trajectory_required": "byte-identical trajectory pairing is not required",
        "incremental_over_baselines_required": "incremental information/effect beyond demoted baselines is not required",
        "fresh_collision_clearance_required": "fresh closest-work clearance is not required before ProblemGate",
        "treatment_label_is_not_validity_evidence": "treatment label may incorrectly self-validate its residual",
        "semantic_applicability_alone_is_insufficient": "semantic applicability may incorrectly grant branch authority",
        "outcome_independent_evidence_required": "outcome-independent evidence is not required",
    }
    for key, message in required_residual_flags.items():
        if residual.get(key) is not True:
            errors.append(message)

    trigger = candidate.get("evidence_trigger_contract") or {}
    required_trigger_flags = {
        "claim_bound_source_or_trajectory_evidence_required": "trigger evidence is not bound to exact source/trajectory facts",
        "outcome_independent": "trigger evidence is not outcome-independent",
        "treatment_label_forbidden_as_validity_evidence": "treatment label is not explicitly forbidden as validity evidence",
        "evidence_receipt_required_before_branch_authority": "branch authority can be granted without an evidence receipt",
        "default_withhold_on_contradicted_or_unverifiable": "contradicted/unverifiable evidence does not fail closed",
    }
    for key, message in required_trigger_flags.items():
        if trigger.get(key) is not True:
            errors.append(message)
    if trigger.get("semantic_applicability_role") != "ELIGIBILITY_BASELINE_ONLY":
        errors.append("semantic applicability must remain eligibility/baseline-only")
    validity_states = {str(value) for value in (trigger.get("validity_states") or [])}
    if validity_states != C1_REQUIRED_VALIDITY_STATES:
        errors.append("evidence validity states must be exactly SUPPORTED/CONTRADICTED/UNVERIFIABLE")
    if trigger.get("trigger_authority_status_now") != "CONTRACT_ONLY_NO_BRANCH_AUTHORITY":
        errors.append("current trigger authority must remain contract-only with no branch authority")
    receipt = trigger.get("evidence_receipt_contract") or {}
    required_receipt_flags = {
        "content_addressed": "evidence receipt is not content-addressed",
        "binds_exact_trajectory_sha256": "evidence receipt does not bind the exact trajectory hash",
        "binds_branch_memory_sha256": "evidence receipt does not bind the branch memory hashes",
        "binds_residual_claim_id": "evidence receipt does not bind the residual claim identity",
        "binds_evidence_refs_and_sha256": "evidence receipt does not bind exact evidence refs and hashes",
        "records_validity_state": "evidence receipt does not record the validity state",
        "records_extractor_and_adjudicator_version": "evidence receipt does not record extractor/adjudicator versions",
        "records_authority_decision": "evidence receipt does not record the branch authority decision",
        "receipt_is_required_before_nonzero_branch_authority": "nonzero branch authority does not require a prior receipt",
        "receipt_cannot_grant_provider_or_scientific_authority": "evidence receipt may incorrectly escalate provider/scientific authority",
    }
    for key, message in required_receipt_flags.items():
        if receipt.get(key) is not True:
            errors.append(message)

    collision = candidate.get("collision_audit_contract") or {}
    if collision.get("status") != "COLLISION_AUDITED_CANDIDATE_FRESH_CLEARANCE_REQUIRED_BEFORE_PROBLEMGATE":
        errors.append("collision audit status does not preserve the fresh-clearance boundary")
    if collision.get("exact_residual_claim_status") != "CANDIDATE_ONLY_NOT_NOVELTY_CLAIM":
        errors.append("exact residual is being overclaimed as established novelty")
    if collision.get("fresh_collision_clearance_required_before_problem_gate") is not True:
        errors.append("fresh collision clearance is not required before ProblemGate")
    if not (collision.get("audit_artifact_refs") or []):
        errors.append("collision audit has no versioned artifact reference")

    d0 = candidate.get("d0_contract") or {}
    if d0.get("zero_or_low_cost") is not True:
        errors.append("D0 is not frozen as zero/low-cost design work")
    if d0.get("outcome_independent_support") is not True:
        errors.append("D0 support is not outcome-independent")
    try:
        provider_budget = int(d0.get("provider_call_budget", -1))
    except (TypeError, ValueError):
        provider_budget = -1
    if provider_budget != 0:
        errors.append("D0 scientific provider-call budget is not frozen at zero")
    if d0.get("provider_execution_authority_after_pass") is not False:
        errors.append("D0 may incorrectly auto-authorize provider execution")
    if d0.get("fresh_experiment_authority_after_pass") is not False:
        errors.append("D0 may incorrectly auto-authorize a fresh experiment")

    authority = candidate.get("authority_after_gate") or {}
    if not _all_authority_false(authority):
        errors.append("C1 residual gate must keep all downstream authority false")

    return {
        "gate": C1_GATE_ID,
        "profile": C1_GATE_PROFILE,
        "paper_id": C1_PAPER_ID,
        "eligible_for_d0_design": not errors,
        "errors": errors,
        "authority": dict(C1_EXECUTABLE_CLOSURE_REVIEWER_GATE["authority"]),
    }


def require_c1_executable_closure_gate(candidate: dict[str, Any]) -> dict[str, Any]:
    result = adjudicate_c1_executable_closure_gate(candidate)
    if result["eligible_for_d0_design"] is not True:
        raise ValueError(C1_GATE_ID + " blocked: " + "; ".join(result["errors"]))
    return result


def load_c1_executable_closure_candidate(path: Path = C1_REVISION_PROGRAM) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        program = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    candidate = program.get("method_novelty_residual_reviewer_gate") or {}
    return candidate if isinstance(candidate, dict) else {}


POLICY: dict[str, Any] = {
    "schema_version": "1.1",
    "cross_cutting_controls_do_not_create_a_seventh_functional_layer": True,
    "controls_inherit_authority_from_their_owner_component": True,
    "unmeasured_controls_must_report_spec_status_not_claim_improvement": True,
    "post_outcome_protocol_changes_require_a_new_registered_contract": True,
    "search_or_tool_access_must_not_leak_hidden_evaluation_answers": True,
    "reproducibility_requires_reexecution_not_only_trace_presence": True,
    "baseline_demoted_components_cannot_reenter_method_novelty_without_new_collision_evidence": True,
    "c1_neutral_metadata_and_generic_core_residual_are_baseline_only": True,
    "c1_only_same_trajectory_counterfactual_residual_plus_evidence_trigger_may_enter_d0": True,
    "semantic_applicability_alone_cannot_grant_evidence_authority": True,
    "treatment_label_cannot_serve_as_its_own_validity_evidence": True,
    "c1_d0_design_gate_cannot_authorize_fresh_execution": True,
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
    c1_candidate = load_c1_executable_closure_candidate()
    c1_adjudication = adjudicate_c1_executable_closure_gate(c1_candidate)
    c1_reviewer_gate = {
        **C1_EXECUTABLE_CLOSURE_REVIEWER_GATE,
        "candidate_loaded": bool(c1_candidate),
        "candidate_adjudication": c1_adjudication,
    }
    return {
        "schema_version": "1.1",
        "policy": POLICY,
        "controls": controls,
        "reviewer_gates": {
            "c1_executable_closure_v3": c1_reviewer_gate,
        },
        "summary": {
            "controls": len(controls),
            "primary_components_added": 0,
            "functional_layers_added": 0,
            "measured_controls": sum(str(row["status"]).startswith("measured") for row in controls),
            "spec_or_contract_ready": sum("ready" in str(row["status"]) for row in controls),
            "registered_reviewer_gates": 1,
            "c1_reviewer_gate_loaded": bool(c1_candidate),
            "c1_reviewer_gate_d0_design_eligible": c1_adjudication["eligible_for_d0_design"],
            "c1_reviewer_gate_downstream_authority": any(bool(value) for value in c1_adjudication["authority"].values()),
        },
        "merge_only_external_designs": [
            {
                "system": "EurekAgent",
                "reason": "permissions/artifact/budget/HITL environment engineering already maps to Runtime & Authority; no duplicate component is required",
            }
        ],
    }
