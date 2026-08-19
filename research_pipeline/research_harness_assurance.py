from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "1.0"

ARIS_REFERENCE = {
    "name": "ARIS / Auto-Research-In-Sleep",
    "paper": "arXiv:2605.03042",
    "repository": "https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep",
    "adopted_boundary": "Harness invariants only: breadth generation is separated from adjudication, execution completeness cannot self-acquit scientific quality, artifacts persist across stages, and effort is orthogonal to assurance. Local scientific gates remain authoritative.",
}

EFFORT_PROFILES: dict[str, dict[str, Any]] = {
    "lite": {"purpose": "cheap exploratory breadth", "relative_fanout": 1},
    "standard": {"purpose": "default bounded multi-lane breadth", "relative_fanout": 2},
    "max": {"purpose": "high-recall candidate expansion", "relative_fanout": 4},
    "swarm": {"purpose": "maximum bounded breadth when search, not review, is the bottleneck", "relative_fanout": 8},
}

ASSURANCE_PROFILES: dict[str, dict[str, Any]] = {
    "exploratory": {"requires": ["machine schema/provenance", "zero-authority labeling"]},
    "qualified": {"requires": ["independent resolved-model review", "exact primary grounding", "typed reduction status"]},
    "experiment-ready": {"requires": ["problem/paper design authority", "frozen protocol", "Pre-Experiment gates"]},
    "paper-ready": {"requires": ["completed claim ledger", "content-addressed evidence", "independent final review"]},
}

POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "fanout_and_jury_are_distinct_roles": True,
    "executor_can_establish_execution_facts_but_cannot_self_acquit_scientific_status": True,
    "jury_clear_is_not_scientific_pass": True,
    "resolved_model_identity_not_requested_alias_controls_independence": True,
    "mechanical_merge_before_jury_has_zero_scientific_authority": True,
    "effort_and_assurance_are_orthogonal": True,
    "increasing_firepower_cannot_relax_assurance": True,
    "harness_assurance_cannot_override_local_scientific_gates": True,
}


def _check(key: str, passed: bool, evidence: Any) -> dict[str, Any]:
    return {"key": key, "pass": bool(passed), "evidence": evidence}


def build_research_harness_assurance(
    *,
    discovery_contract_state: dict[str, Any],
    generator_state: dict[str, Any],
    installed_generator_policy: dict[str, Any],
    premium_model_policy: dict[str, Any],
    governance_state: dict[str, Any],
    paper_quality_policy: dict[str, Any],
    candidate_portfolio_state: dict[str, Any],
    search_telemetry_state: dict[str, Any],
) -> dict[str, Any]:
    dp = discovery_contract_state.get("policy") or {}
    gp = installed_generator_policy or {}
    gov = governance_state.get("policy") or {}
    pp = candidate_portfolio_state.get("policy") or {}
    tp = search_telemetry_state.get("policy") or {}
    stages = premium_model_policy.get("stages") or {}

    generation_models = tuple(stages.get("portfolio_expand") or stages.get("problem_generation") or [])
    review_models = tuple(stages.get("semantic_review") or [])
    different_default_families = bool(generation_models and review_models and generation_models[0] != review_models[0])

    reviewed_candidates = []
    independence_violations = []
    for row in generator_state.get("candidates") or []:
        if not isinstance(row, dict):
            continue
        review = row.get("semantic_reduction_review") if isinstance(row.get("semantic_reduction_review"), dict) else {}
        if not review:
            continue
        reviewed_candidates.append(str(row.get("candidate_id") or ""))
        if review.get("independent_resolved_model") is False:
            independence_violations.append(str(row.get("candidate_id") or ""))

    checks = [
        _check(
            "fanout-generation-only",
            dp.get("fanout_is_generation_only") is True and gp.get("fanout_is_generation_only") is True,
            {"discovery_contract": dp.get("fanout_is_generation_only"), "generator": gp.get("fanout_is_generation_only")},
        ),
        _check(
            "mechanical-pre-jury-merge-zero-authority",
            dp.get("pre_jury_dedup_is_deterministic_mechanical_only") is True and gp.get("pre_jury_dedup_is_deterministic_mechanical_only") is True,
            {"discovery_contract": dp.get("pre_jury_dedup_is_deterministic_mechanical_only"), "generator": gp.get("pre_jury_dedup_is_deterministic_mechanical_only")},
        ),
        _check(
            "resolved-model-independent-jury",
            gp.get("same_resolved_model_cannot_count_as_independent_review") is True
            and premium_model_policy.get("designer_reviewer_resolved_model_independence_required") is True
            and different_default_families
            and not independence_violations,
            {"generation_default": generation_models[0] if generation_models else "", "review_default": review_models[0] if review_models else "", "reviewed_candidates": reviewed_candidates, "violations": independence_violations},
        ),
        _check(
            "jury-cannot-acquit",
            gp.get("semantic_reviewer_is_block_only") is True
            and gp.get("jury_clear_is_not_scientific_pass") is True
            and dp.get("jury_clear_is_not_scientific_pass") is True,
            {"semantic_reviewer_is_block_only": gp.get("semantic_reviewer_is_block_only"), "jury_clear_is_not_scientific_pass": gp.get("jury_clear_is_not_scientific_pass")},
        ),
        _check(
            "execution-completeness-cannot-self-acquit",
            gov.get("execution_completeness_cannot_set_scientific_pass") is True
            and gov.get("scientific_status_requires_independent_stage_authority") is True,
            {"execution_completeness_cannot_set_scientific_pass": gov.get("execution_completeness_cannot_set_scientific_pass"), "scientific_status_requires_independent_stage_authority": gov.get("scientific_status_requires_independent_stage_authority")},
        ),
        _check(
            "persistent-multi-candidate-portfolio",
            pp.get("multiple_candidates_may_remain_visible_while_one_line_is_blocked") is True
            and pp.get("portfolio_cannot_promote_candidate_stage") is True,
            candidate_portfolio_state.get("summary") or {},
        ),
        _check(
            "claim-ledger-before-paper-ready",
            paper_quality_policy.get("manuscript_claims_must_read_from_claim_ledger") is True
            and paper_quality_policy.get("claim_ledger_preserves_refuted_and_inconclusive_rows") is True
            and paper_quality_policy.get("claim_ledger_has_zero_scientific_authority") is True,
            {"paper_quality_schema": paper_quality_policy.get("schema_version")},
        ),
        _check(
            "effort-assurance-orthogonal",
            dp.get("effort_profile_cannot_change_assurance_thresholds") is True
            and gp.get("effort_profile_cannot_change_assurance_thresholds") is True
            and len(EFFORT_PROFILES) >= 4
            and len(ASSURANCE_PROFILES) >= 4,
            {"effort_profiles": sorted(EFFORT_PROFILES), "assurance_profiles": sorted(ASSURANCE_PROFILES)},
        ),
        _check(
            "meta-telemetry-zero-authority",
            search_telemetry_state.get("scientific_authority") is False
            and tp.get("telemetry_is_observability_not_scientific_authority") is True
            and tp.get("portfolio_capacity_pressure_cannot_relax_gates") is True,
            {"bottleneck": (search_telemetry_state.get("bottleneck") or {}).get("key")},
        ),
    ]
    passed = sum(item["pass"] for item in checks)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_HARNESS_ASSURANCE" if passed == len(checks) else "HOLD_HARNESS_ASSURANCE",
        "policy": dict(POLICY),
        "reference": dict(ARIS_REFERENCE),
        "effort_profiles": EFFORT_PROFILES,
        "assurance_profiles": ASSURANCE_PROFILES,
        "checks": checks,
        "summary": {
            "checks": len(checks),
            "passed": passed,
            "failed": len(checks) - passed,
            "reviewed_candidate_receipts": len(reviewed_candidates),
            "resolved_model_independence_violations": len(independence_violations),
        },
        "scientific_authority": False,
        "authority": {
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
    }
