from __future__ import annotations

from typing import Any

from .paper_first_fresh_saturation import REDUCTION_PATTERNS, REDUCTION_FALSIFIABILITY_CONTRACT, reduction_pattern_audit


DISCOVERY_OPERATOR_VERSION = "double-funnel-paperability-evolution-v18-memory-wiki"

# Paperability is broader than principle novelty. These axes are search/triage
# coordinates only: none grants Method, Experiment, P0, GPU, or Paper authority.
PAPERABILITY_AXES: dict[str, str] = {
    "P": "principle_or_problem_formulation",
    "M": "method_or_method_boundary",
    "E": "empirical_phenomenon",
    "B": "benchmark_or_evaluation",
    "T": "theory_or_guarantee",
    "S": "system_or_capability",
}
PAPERABILITY_AXIS_STATUSES: tuple[str, ...] = (
    "SUPPORTED",
    "PLAUSIBLE",
    "OPEN",
    "REDUCED",
    "NOT_CLAIMED",
)

DISCOVERY_LANES: tuple[str, ...] = (
    "CONTRADICTION",
    "CONVERGENT_FAILURE",
    "ASSUMPTION_BREAK",
    "UNEXPLAINED_BOUNDARY",
)

# The canonical double-funnel may explore this broader structural vocabulary
# upstream, but final Problem-Gate candidates must still normalize to one of
# DISCOVERY_LANES. The historical pre-split Search Portfolio publication remains
# a shadow provenance artifact and is never retroactively promoted.
SEARCH_PORTFOLIO_PRIMITIVES: tuple[str, ...] = (
    *DISCOVERY_LANES,
    "IDENTIFIABILITY_GAP",
    "MISSING_DECISION_OBJECT",
    "COMPOSITION_INTERACTION",
    "CROSS_DOMAIN_STRUCTURAL_ANALOGY",
    "NEW_CAPABILITY_QUESTION",
    "LONGITUDINAL_EMERGENCE",
)

FORBIDDEN_DISCOVERY_LANES: tuple[str, ...] = (
    "MISSING_CELL",
    "SHARED_LIMITATION",
    "PURE_TOPIC_BRAINSTORM",
)

SOURCE_EVIDENCE_ROLES: tuple[str, ...] = (
    "EMPIRICAL_FACT",
    "OPERATIONAL_ASSUMPTION",
)

LANE_SOURCE_ROLES: dict[str, tuple[str, str]] = {
    "CONTRADICTION": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "CONVERGENT_FAILURE": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "ASSUMPTION_BREAK": ("OPERATIONAL_ASSUMPTION", "EMPIRICAL_FACT"),
    "UNEXPLAINED_BOUNDARY": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "IDENTIFIABILITY_GAP": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "MISSING_DECISION_OBJECT": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "COMPOSITION_INTERACTION": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "CROSS_DOMAIN_STRUCTURAL_ANALOGY": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "NEW_CAPABILITY_QUESTION": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
    "LONGITUDINAL_EMERGENCE": ("EMPIRICAL_FACT", "EMPIRICAL_FACT"),
}

LANE_DISTINCT_SOURCE_MINIMUM: dict[str, int] = {
    "CONTRADICTION": 2,
    "CONVERGENT_FAILURE": 2,
    "ASSUMPTION_BREAK": 2,
    "UNEXPLAINED_BOUNDARY": 1,
    "IDENTIFIABILITY_GAP": 1,
    "MISSING_DECISION_OBJECT": 2,
    "COMPOSITION_INTERACTION": 1,
    "CROSS_DOMAIN_STRUCTURAL_ANALOGY": 1,
    "NEW_CAPABILITY_QUESTION": 1,
    "LONGITUDINAL_EMERGENCE": 1,
}


LANE_EVIDENCE_REQUIRED: dict[str, tuple[str, ...]] = {
    "CONTRADICTION": (
        "shared_operationalization",
        "shared_intervention_semantics",
        "shared_adaptation_stage",
        "source_a_intervention",
        "source_b_intervention",
        "intervention_surface_match",
        "executor_state_match",
        "comparator_match",
        "endpoint_match",
        "timing_match",
        "treatment_equivalence_argument",
        "incompatibility",
    ),
    "CONVERGENT_FAILURE": (
        "shared_condition",
        "method_a",
        "method_b",
        "failure_a",
        "failure_b",
        "independence_basis",
    ),
    "ASSUMPTION_BREAK": (
        "assumption",
        "violation",
        "scope_link",
    ),
    "UNEXPLAINED_BOUNDARY": (
        "shared_measurement",
        "boundary_observation",
        "adjacent_regime",
        "unexplained_transition",
    ),
    "IDENTIFIABILITY_GAP": (
        "target_question",
        "observational_equivalence",
        "measured_proxy",
        "decision_consequence",
    ),
    "MISSING_DECISION_OBJECT": (
        "surrogate_a",
        "surrogate_b",
        "downstream_decision",
        "mismatch_evidence",
    ),
    "COMPOSITION_INTERACTION": (
        "component_a",
        "component_b",
        "composition_condition",
        "interaction_observation",
        "nonadditivity_basis",
    ),
    "CROSS_DOMAIN_STRUCTURAL_ANALOGY": (
        "source_domain_structure",
        "agent_specific_constraint",
        "agent_evidence_link",
        "why_not_simple_transfer",
    ),
    "NEW_CAPABILITY_QUESTION": (
        "new_capability",
        "newly_observable_signal",
        "previous_measurement_limit",
        "capability_specific_constraint",
    ),
    "LONGITUDINAL_EMERGENCE": (
        "shared_measurement",
        "short_horizon_regime",
        "long_horizon_regime",
        "emergence_signature",
    ),
}

LANE_MACHINE_CONTRACTS: dict[str, str] = {
    "CONTRADICTION": "Two independently grounded empirical facts are incompatible only after a shared operationalization aligns intervention/treatment surface, adaptation stage, executor/parameter state, comparator, endpoint, and intervention timing; inference-time context, retrieval/filtering, parameter updates, and full-parameter training are not interchangeable treatments, and cross-treatment sign differences are REDUCIBLE rather than contradictions.",
    "CONVERGENT_FAILURE": "Two independent method families show quantitative failure under the same bounded operational condition; the candidate names a common failure object rather than a better-method claim.",
    "ASSUMPTION_BREAK": "Source A contains an explicit operational assumption and independent source B contains empirical evidence that violates it in a scope-linked setting.",
    "UNEXPLAINED_BOUNDARY": "Primary evidence quantitatively establishes an anomalous boundary/regime and an adjacent expected regime for the same measured phenomenon; the candidate targets the unexplained transition.",
    "IDENTIFIABILITY_GAP": "Two grounded results show that the field's measured proxy or observational record cannot distinguish scientifically different mechanisms or decisions under the same available information.",
    "MISSING_DECISION_OBJECT": "Two grounded works optimize or report different surrogates while an explicit downstream scientific/deployment decision remains unresolved; the candidate defines the missing decision object rather than another metric.",
    "COMPOSITION_INTERACTION": "Grounded evidence supports individually understood components and a composition regime whose behavior is not explained by simply adding their isolated accounts.",
    "CROSS_DOMAIN_STRUCTURAL_ANALOGY": "Grounded Agent-side evidence instantiates a mature external problem structure, while an explicit Agent-specific structural constraint changes a testable prediction; domain transfer alone is forbidden.",
    "NEW_CAPABILITY_QUESTION": "Grounded recent capabilities expose a measurement/intervention signal that was previously unavailable, creating a falsifiable scientific question rather than a feature request.",
    "LONGITUDINAL_EMERGENCE": "Grounded evidence under a shared measurement separates short- and long-horizon/scaling regimes and identifies an emergence signature that must survive ordinary dynamics as the strongest reduction.",
}

POLICY: dict[str, Any] = {
    "schema_version": "2.2",
    "multi_lane_discovery_required": True,
    "contradiction_first_required": False,
    "contradiction_lane_retained": True,
    "allowed_discovery_lanes": list(DISCOVERY_LANES),
    "search_portfolio_primitives": list(SEARCH_PORTFOLIO_PRIMITIVES),
    "forbidden_discovery_lanes": list(FORBIDDEN_DISCOVERY_LANES),
    "lane_specific_machine_evidence_contract_required": True,
    # Legacy/public Search Portfolio artifacts remain shadow-only. New canonical
    # discovery reuses the same breadth-search engine *inside* one atomic live
    # discovery transaction instead of promoting any historical shadow result.
    "search_portfolio_required": False,
    "search_portfolio_is_shadow_only": True,
    "search_portfolio_cannot_publish_canonical_generator_or_queue": True,
    "canonical_double_funnel_required": True,
    "canonical_double_funnel_reuses_portfolio_engine": True,
    "historical_search_portfolio_remains_shadow_only": True,
    "one_content_addressed_pool_allows_at_most_one_live_generator_call": False,
    "one_content_addressed_pool_allows_at_most_one_live_generator_call_per_discovery_operator": False,
    "one_content_addressed_pool_allows_at_most_one_discovery_transaction": True,
    "bounded_provider_subcalls_inside_discovery_transaction": True,
    "attack_repair_split_before_terminal_review": True,
    # Harness invariants: breadth agents generate search material but cannot acquit
    # themselves scientifically. Deterministic merge/dedup is mechanical only; the
    # independent semantic jury stays BLOCK-only and exact scientific gates remain
    # downstream. v18 additionally injects the compiled zero-authority Research Memory Wiki.
    "fanout_is_generation_only": True,
    "pre_jury_dedup_is_deterministic_mechanical_only": True,
    "fanout_role_cannot_authorize_terminal_scientific_verdict": True,
    "terminal_semantic_jury_requires_resolved_model_independence": True,
    "jury_clear_is_not_scientific_pass": True,
    "portfolio_retains_multiple_survivors_before_scientific_gate": True,
    "effort_profile_cannot_change_assurance_thresholds": True,
    "research_memory_query_pack_required_before_generation": True,
    "research_memory_query_pack_is_zero_authority": True,
    "transient_operational_memory_excluded_from_generation": True,
    "research_memory_query_pack_receipt_required": True,
    "paperability_axes": dict(PAPERABILITY_AXES),
    "principle_reduction_does_not_auto_close_other_paperability_axes": True,
    "cheap_problem_falsifier_may_precede_exact_reduction": True,
    "pre_f0_evidence_acquisition_has_zero_scientific_authority": True,
    "exact_reduction_required_before_final_problem_gate": True,
    "source_coverage_saturation_reopens_once_on_operator_change": True,
    "expansion_reduction_separated": True,
    "mature_theory_veto_delayed_until_formulated_branch": True,
    "diversity_archives_required": True,
    "branch_lineage_required": True,
    "reduction_falsifiability_contract_required": True,
    "generic_theory_label_cannot_veto": True,
    "two_grounded_evidence_items_required": True,
    "same_primary_source_can_supply_multiple_evidence_items_when_lane_minimum_is_one": True,
    "distinct_primary_source_minimum_is_lane_specific": True,
    "single_source_anomaly_first_search_enabled": True,
    "primary_anomaly_can_trigger_controlled_residual_search_without_cross_paper_metric_match": True,
    "support_feasibility_is_search_priority_not_novelty_authority": True,
    "closed_basin_inversion_search_enabled": True,
    "search_closure_inversion_requires_certified_counter_explanation": True,
    "search_closure_inversion_is_search_prior_not_scientific_authority": True,
    "search_closure_inversion_requires_fresh_primary_grounding": True,
    "search_closure_inversion_must_satisfy_recorded_reopen_condition": True,
    # Backward-compatible policy aliases for current research-system consumers.
    # These names are legacy only: they refer to layer-typed search closures, not
    # to scientific dead-end certification except for core_principle rows.
    "principle_dead_end_inversion_search_enabled": True,
    "dead_end_inversion_requires_certified_counter_explanation": True,
    "dead_end_inversion_is_search_prior_not_scientific_authority": True,
    "dead_end_inversion_requires_fresh_primary_grounding": True,
    "dead_end_inversion_must_satisfy_recorded_reopen_condition": True,
    "first_party_inversion_asset_grounding_enabled": True,
    "first_party_inversion_asset_requires_provenance_manifest": True,
    "first_party_inversion_asset_is_zero_authority_search_evidence": True,
    "first_party_inversion_asset_requires_one_direct_seed_per_shard": True,
    "observed_dependency_graph_is_not_an_identifiability_gap": True,
    "reciprocal_coupling_claim_requires_downstream_residual_beyond_distribution_shift": True,
    "feedback_mechanism_requires_causal_write_path_before_experiment": True,
    "positive_residual_search_enabled": True,
    "positive_residual_asset_requires_provenance_manifest": True,
    "positive_residual_asset_is_zero_authority_search_evidence": True,
    "positive_residual_requires_surviving_phenomenon_and_clean_mechanism_stop": True,
    "positive_residual_requires_prospective_pre_outcome_prediction": True,
    "positive_residual_outcome_leakage_forbidden": True,
    "positive_residual_direct_seed_required_in_unexplained_boundary_shard": True,
    "inactive_search_assets_hidden_from_generator": True,
    "inactive_search_assets_remain_provenance_archived": True,
    "no_active_asset_fallback_requires_latest_primary_quantitative_anomaly": True,
    "fresh_phenomenon_seed_must_name_measured_boundary_or_failure": True,
    "fresh_phenomenon_asset_readiness_is_priority_not_novelty_authority": True,
    "fresh_phenomenon_missing_substrate_is_hold_not_scientific_fail": True,
    "fresh_phenomenon_recent_window_source_coverage_required": True,
    "fresh_phenomenon_target_is_evidence_level_not_source_level": True,
    "fresh_phenomenon_principle_closure_is_exact_evidence_sha_only": True,
    "fresh_phenomenon_closure_does_not_blacklist_source": True,
    "fresh_phenomenon_measured_failure_requires_failure_cue": True,
    "fresh_phenomenon_shard_has_deterministic_target_ref": True,
    "fresh_phenomenon_shard_has_deterministic_phenomenon_id": True,
    "fresh_phenomenon_seed1_must_match_target_ref": True,
    "fresh_phenomenon_seed1_must_match_target_phenomenon": True,
    "temporal_exposure_relabeling_after_longitudinal_reduction_forbidden": True,
    "treatment_semantics_seed_requires_executable_version_change": True,
    "treatment_semantics_seed_requires_versioned_treatment_reduction_first": True,
    "contradiction_requires_treatment_surface_alignment": True,
    "contradiction_requires_executor_state_alignment": True,
    "contradiction_requires_comparator_endpoint_timing_alignment": True,
    "cross_treatment_sign_difference_is_reducible_not_contradiction": True,
    "generator_pre_review_allows_pending_exact_reduction": True,
    "generator_pre_review_still_blocks_proven_hard_reduction": True,
    "semantic_reviewer_owns_pending_exact_reduction_adjudication": True,
    "final_problem_gate_still_requires_all_reductions_resolved": True,
    "search_closure_exact_source_reentry_forbidden": True,
    "search_closure_reopen_requires_new_evidence": True,
    "discovery_operator_version": DISCOVERY_OPERATOR_VERSION,
    "shared_limitation_without_empirical_failure_forbidden": True,
    "pure_topic_brainstorm_forbidden": True,
    "open_world_missing_cell_claim_forbidden": True,
    "two_mature_theory_baselines_required": True,
    "same_information_nonreducibility_required": True,
    "domain_transfer_veto_required": True,
    "saturation_map_check_required": True,
    "problem_falsifier_required_before_method_design": True,
    "reduction_pending_is_provisional_not_failed": True,
    "reduction_pending_may_reach_block_only_semantic_review": True,
    "reduction_pending_cannot_pass_problem_gate": True,
    "contradiction_requires_matched_intervention_semantics": True,
    "contradiction_requires_matched_adaptation_stage": True,
    "bounded_first_party_evidence_acquisition_allowed_before_problem_gate_pass": True,
    "support_inventory_is_one_evidence_route_not_global_prerequisite": True,
    "first_party_evidence_cannot_auto_certify_novelty": True,
    "endpoint_headroom_required_before_terminal_interpretation": True,
    "independent_reviewer_must_verify_lane_contract": True,
    "no_lane_specific_downstream_relaxation": True,
    "ai_generation_is_advisory_only": True,
    "zero_survivors_is_valid": True,
    "method_design_authorized_by_problem_gate": False,
    "local_validation_authorized_by_problem_gate": False,
    "p0_authorized_by_problem_gate": False,
    "gpu_authorized_by_problem_gate": False,
}

REQUIRED_FIELDS = (
    "candidate_id",
    "title",
    "discovery_lane",
    "empirical_evidence",
    "lane_evidence",
    "irreducible_object",
    "mature_theory_baselines",
    "reduction_falsifiability_contract",
    "same_information_nonreducibility",
    "exact_prediction",
    "strongest_same_information_baseline",
    "domain_transfer_audit",
    "saturation_scan",
    "cheapest_problem_falsifier",
    "endpoint_headroom_requirement",
    "semantic_reduction_review",
    "authority",
)


def source_schema() -> dict[str, Any]:
    return {
        "required": ["ref", "title", "claim", "evidence_role", "primary_source", "primary_url", "source_sha256"],
        "evidence_roles": list(SOURCE_EVIDENCE_ROLES),
        "primary_source_must_be_true": True,
        "source_sha256_must_match_primary_evidence_registry": True,
        "claim_must_be_primary_evidence_not_future_work": True,
    }


def candidate_schema() -> dict[str, Any]:
    return {
        "schema_version": "2.0",
        "required": list(REQUIRED_FIELDS),
        "discovery_lane": {
            "allowed": list(DISCOVERY_LANES),
            "forbidden": list(FORBIDDEN_DISCOVERY_LANES),
        },
        "empirical_evidence": {
            "required": ["source_a", "source_b", "relation"],
            "source_schema": source_schema(),
        },
        "lane_evidence": {
            "required_by_lane": {key: list(value) for key, value in LANE_EVIDENCE_REQUIRED.items()},
            "machine_contracts": dict(LANE_MACHINE_CONTRACTS),
        },
        "mature_theory_baselines": {
            "minimum": 2,
            "each_required": ["name", "same_information_projection", "ex_ante_prediction", "distinguishing_prediction", "cannot_express", "reduction_class", "exact_reduction_test"],
            "allowed_reduction_classes": ["VALID_HARD_VETO", "SOFT_COLLISION", "NEEDS_EXACT_REDUCTION_TEST", "TOO_GENERIC_TO_VETO"],
        },
        "reduction_falsifiability_contract": dict(REDUCTION_FALSIFIABILITY_CONTRACT),
        "same_information_nonreducibility": {
            "required": ["claim", "why_each_baseline_cannot_express_prediction"],
        },
        "domain_transfer_audit": {
            "required": ["mature_source_domain", "mature_object", "why_not_domain_transfer"],
        },
        "saturation_scan": {
            "required": ["checked", "matched_patterns"],
            "known_patterns": [row["key"] for row in REDUCTION_PATTERNS],
            "matched_patterns_are_proven_hard_reductions_only": True,
            "pending_patterns_require_exact_reduction_test": True,
            "rejected_patterns_are_advisory_and_independently_reviewed": True,
            "pattern_match_alone_is_not_a_veto": True,
            "invalid_entries_must_be_empty": True,
        },
        "semantic_reduction_review": {
            "required": [
                "reviewed",
                "block_only",
                "verdict",
                "reviewer_model",
                "raw_sha256",
                "source_claims_grounded",
                "source_claim_grounding",
                "lane_contract_verified",
            ],
            "verdict_must_be_clear": True,
            "reviewer_can_block_but_never_authorize": True,
            "both_source_claims_require_exact_primary_evidence_grounding": True,
            "lane_contract_must_be_independently_verified": True,
        },
        "authority": {
            "required_false": ["method_design", "experiment_blueprint", "local_validation", "p0", "gpu", "full_experiment"],
        },
    }


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return value is not None


def _normalized_evidence_text(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def _lane_contract_blockers(candidate: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    lane = str(candidate.get("discovery_lane") or "").strip().upper()
    if lane in FORBIDDEN_DISCOVERY_LANES:
        return [f"forbidden-discovery-lane:{lane}"]
    if lane not in DISCOVERY_LANES:
        return [f"unknown-discovery-lane:{lane or 'EMPTY'}"]

    evidence = candidate.get("empirical_evidence") or {}
    source_a = evidence.get("source_a") or {}
    source_b = evidence.get("source_b") or {}
    expected_roles = LANE_SOURCE_ROLES[lane]
    actual_roles = (
        str(source_a.get("evidence_role") or "").strip().upper(),
        str(source_b.get("evidence_role") or "").strip().upper(),
    )
    if actual_roles != expected_roles:
        blockers.append(
            "lane-source-role-mismatch:"
            + lane
            + ":expected="
            + "/".join(expected_roles)
            + ":actual="
            + "/".join(actual_roles)
        )

    lane_evidence = candidate.get("lane_evidence") or {}
    if not isinstance(lane_evidence, dict):
        blockers.append("lane-evidence-must-be-object")
        return blockers
    for key in LANE_EVIDENCE_REQUIRED[lane]:
        if not _nonempty(lane_evidence.get(key)):
            blockers.append(f"lane-evidence-missing:{lane}:{key}")

    # These are structural anti-shortcut checks. Independent semantic review still
    # decides whether the grounded source claims really support the relation.
    if lane == "CONTRADICTION":
        for key in ("intervention_surface_match","executor_state_match","comparator_match","endpoint_match","timing_match"):
            if lane_evidence.get(key) is not True:
                blockers.append(f"contradiction-treatment-alignment-failed:{key}")
        if _normalized_evidence_text(lane_evidence.get("source_a_intervention")) == _normalized_evidence_text(lane_evidence.get("source_b_intervention")) and len(str(lane_evidence.get("treatment_equivalence_argument") or "").split()) < 6:
            blockers.append("contradiction-treatment-equivalence-argument-too-weak")
    if lane == "CONVERGENT_FAILURE":
        if _normalized_evidence_text(lane_evidence.get("method_a")) == _normalized_evidence_text(lane_evidence.get("method_b")):
            blockers.append("convergent-failure-requires-distinct-methods")
    if lane == "ASSUMPTION_BREAK":
        if len(str(lane_evidence.get("assumption") or "").split()) < 4:
            blockers.append("assumption-break-requires-explicit-operational-assumption")
    return blockers


def _shadow_lane_contract_blockers(candidate: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    lane = str(candidate.get("discovery_lane") or "").strip().upper()
    if lane in FORBIDDEN_DISCOVERY_LANES:
        return [f"forbidden-discovery-lane:{lane}"]
    if lane not in SEARCH_PORTFOLIO_PRIMITIVES:
        return [f"unknown-shadow-search-primitive:{lane or 'EMPTY'}"]
    evidence = candidate.get("empirical_evidence") or {}
    source_a = evidence.get("source_a") or {}
    source_b = evidence.get("source_b") or {}
    expected_roles = LANE_SOURCE_ROLES[lane]
    actual_roles = (
        str(source_a.get("evidence_role") or "").strip().upper(),
        str(source_b.get("evidence_role") or "").strip().upper(),
    )
    if actual_roles != expected_roles:
        blockers.append(
            "shadow-primitive-source-role-mismatch:"
            + lane
            + ":expected="
            + "/".join(expected_roles)
            + ":actual="
            + "/".join(actual_roles)
        )
    lane_evidence = candidate.get("lane_evidence") or {}
    if not isinstance(lane_evidence, dict):
        blockers.append("shadow-primitive-evidence-must-be-object")
        return blockers
    for key in LANE_EVIDENCE_REQUIRED[lane]:
        if not _nonempty(lane_evidence.get(key)):
            blockers.append(f"shadow-primitive-evidence-missing:{lane}:{key}")
    if lane == "CONTRADICTION":
        for key in ("intervention_surface_match","executor_state_match","comparator_match","endpoint_match","timing_match"):
            if lane_evidence.get(key) is not True:
                blockers.append(f"contradiction-treatment-alignment-failed:{key}")
    if lane == "CONVERGENT_FAILURE" and _normalized_evidence_text(lane_evidence.get("method_a")) == _normalized_evidence_text(lane_evidence.get("method_b")):
        blockers.append("convergent-failure-requires-distinct-methods")
    if lane == "ASSUMPTION_BREAK" and len(str(lane_evidence.get("assumption") or "").split()) < 4:
        blockers.append("assumption-break-requires-explicit-operational-assumption")
    return blockers


def audit_problem_candidate(
    candidate: dict[str, Any],
    *,
    primary_evidence_by_ref: dict[str, dict[str, Any]] | None = None,
    require_primary_registry: bool = False,
    require_semantic_review: bool = True,
    allow_pending_reduction_for_semantic_review: bool = False,
) -> dict[str, Any]:
    blockers: list[str] = []
    checks: list[dict[str, Any]] = []

    for key in REQUIRED_FIELDS:
        passed = key in candidate and _nonempty(candidate.get(key))
        checks.append({"key": f"field:{key}", "pass": passed})
        if not passed:
            blockers.append(f"missing-or-empty:{key}")

    lane = str(candidate.get("discovery_lane") or "").strip().upper()
    lane_blockers = _lane_contract_blockers(candidate)
    blockers.extend(lane_blockers)
    checks.append({"key": "discovery-lane-contract", "pass": not lane_blockers, "lane": lane})

    evidence = candidate.get("empirical_evidence") or {}
    sources = [evidence.get("source_a") or {}, evidence.get("source_b") or {}]
    source_refs: set[str] = set()
    registry = primary_evidence_by_ref or {}
    for idx, source in enumerate(sources, start=1):
        role = str(source.get("evidence_role") or "").strip().upper()
        passed = (
            all(_nonempty(source.get(key)) for key in ("ref", "title", "claim", "evidence_role", "primary_url", "source_sha256"))
            and role in SOURCE_EVIDENCE_ROLES
            and source.get("primary_source") is True
        )
        checks.append({"key": f"primary-source-{idx}", "pass": passed, "role": role})
        if not passed:
            blockers.append(f"invalid-primary-source:{idx}")
        ref = str(source.get("ref") or "").strip()
        if ref:
            source_refs.add(ref)
        if require_primary_registry:
            record = registry.get(ref)
            if not record:
                blockers.append(f"primary-source-not-in-registry:{idx}")
            else:
                if str(source.get("source_sha256") or "") != str(record.get("source_sha256") or ""):
                    blockers.append(f"primary-source-sha-mismatch:{idx}")
                if str(source.get("primary_url") or "") != str(record.get("primary_url") or ""):
                    blockers.append(f"primary-source-url-mismatch:{idx}")
                if str(source.get("title") or "").strip() != str(record.get("title") or "").strip():
                    blockers.append(f"primary-source-title-mismatch:{idx}")
    minimum_distinct=LANE_DISTINCT_SOURCE_MINIMUM.get(lane,2)
    if len(source_refs) < minimum_distinct:
        blockers.append(f"discovery-lane-requires-{minimum_distinct}-distinct-primary-sources:{lane}")
    if not _nonempty(evidence.get("relation")):
        blockers.append("empirical-evidence-relation-missing")

    baselines = candidate.get("mature_theory_baselines") or []
    allowed_reduction_classes={"VALID_HARD_VETO","SOFT_COLLISION","NEEDS_EXACT_REDUCTION_TEST","TOO_GENERIC_TO_VETO"}
    if not isinstance(baselines, list) or len(baselines) < 2:
        blockers.append("need-at-least-two-mature-theory-baselines")
    else:
        for idx, row in enumerate(baselines, start=1):
            required=("name","same_information_projection","ex_ante_prediction","distinguishing_prediction","cannot_express","reduction_class","exact_reduction_test")
            if not isinstance(row, dict) or not all(_nonempty(row.get(key)) for key in required):
                blockers.append(f"invalid-mature-theory-baseline:{idx}")
                continue
            reduction_class=str(row.get("reduction_class") or "").strip().upper()
            if reduction_class not in allowed_reduction_classes:
                blockers.append(f"invalid-reduction-class:{idx}")
            elif reduction_class == "VALID_HARD_VETO":
                blockers.append(f"mature-theory-valid-hard-veto:{idx}")
            elif reduction_class == "NEEDS_EXACT_REDUCTION_TEST" and not allow_pending_reduction_for_semantic_review:
                blockers.append(f"unresolved-exact-reduction-test:{idx}")

    reduction_contract=candidate.get("reduction_falsifiability_contract") or {}
    required_contract=("same_observable_information_checked","ex_ante_exact_prediction_checked","distinguishing_prediction_checked","scope_boundary_checked")
    contract_ok=isinstance(reduction_contract,dict) and all(reduction_contract.get(key) is True for key in required_contract)
    if allow_pending_reduction_for_semantic_review:
        contract_ok=contract_ok and isinstance(reduction_contract.get("all_exact_reduction_tests_resolved"),bool)
    else:
        contract_ok=contract_ok and reduction_contract.get("all_exact_reduction_tests_resolved") is True
    if not contract_ok:
        blockers.append("reduction-falsifiability-contract-incomplete")

    nonred = candidate.get("same_information_nonreducibility") or {}
    if not isinstance(nonred, dict) or not _nonempty(nonred.get("claim")) or not _nonempty(nonred.get("why_each_baseline_cannot_express_prediction")):
        blockers.append("same-information-nonreducibility-incomplete")

    domain = candidate.get("domain_transfer_audit") or {}
    if not isinstance(domain, dict) or not all(_nonempty(domain.get(key)) for key in ("mature_source_domain", "mature_object", "why_not_domain_transfer")):
        blockers.append("domain-transfer-audit-incomplete")

    closure_reentry = candidate.get("search_closure_reentry_audit") or candidate.get("principle_dead_end_reentry_audit") or {}
    if isinstance(closure_reentry,dict) and closure_reentry.get("blocked") is True:
        matches=[str(x) for x in (closure_reentry.get("matched_source_candidate_ids") or []) if str(x)]
        blockers.append("search-closure-exact-source-reentry:" + ",".join(sorted(matches or ["unknown"])))

    saturation = candidate.get("saturation_scan") or {}
    matched = list(saturation.get("matched_patterns") or []) if isinstance(saturation, dict) else []
    pending = list(saturation.get("pending_patterns") or []) if isinstance(saturation, dict) else []
    rejected = list(saturation.get("rejected_patterns") or []) if isinstance(saturation, dict) else []
    invalid_entries = list(saturation.get("invalid_entries") or []) if isinstance(saturation, dict) else []
    known = {row["key"] for row in REDUCTION_PATTERNS}
    unknown_matches = sorted(set(str(x) for x in matched) - known)
    if not isinstance(saturation, dict) or saturation.get("checked") is not True:
        blockers.append("saturation-scan-not-run")
    # matched_patterns is now reserved for an exact candidate-level hard reduction
    # that already satisfied the falsifiability contract. Mere pattern similarity
    # belongs in rejected_patterns or pending_patterns and cannot auto-veto.
    if matched:
        blockers.append("saturation-proven-hard-reduction:" + ",".join(sorted(str(x) for x in matched)))
    if unknown_matches:
        blockers.append("unknown-saturation-pattern:" + ",".join(unknown_matches))
    for row in pending:
        if not isinstance(row,dict) or str(row.get("key") or "").strip() not in known or not (_nonempty(row.get("exact_reduction_test")) or _nonempty(row.get("reason"))):
            blockers.append("invalid-pending-saturation-pattern")
        elif not allow_pending_reduction_for_semantic_review:
            blockers.append("saturation-exact-reduction-pending:"+str(row.get("key")))
    for row in rejected:
        if not isinstance(row,dict) or str(row.get("key") or "").strip() not in known or not _nonempty(row.get("reason")):
            blockers.append("invalid-rejected-saturation-pattern")
    if invalid_entries:
        blockers.append("invalid-saturation-scan-entry:" + ",".join(sorted(str(x) for x in invalid_entries)))

    if not _nonempty(candidate.get("exact_prediction")):
        blockers.append("exact-prediction-missing")
    if not _nonempty(candidate.get("strongest_same_information_baseline")):
        blockers.append("strongest-same-information-baseline-missing")
    if not _nonempty(candidate.get("cheapest_problem_falsifier")):
        blockers.append("problem-falsifier-missing")
    if not _nonempty(candidate.get("endpoint_headroom_requirement")):
        blockers.append("endpoint-headroom-missing")

    if require_semantic_review:
        semantic_review = candidate.get("semantic_reduction_review") or {}
        if not isinstance(semantic_review, dict) or semantic_review.get("reviewed") is not True or semantic_review.get("block_only") is not True:
            blockers.append("semantic-reduction-review-missing")
        else:
            verdict = str(semantic_review.get("verdict") or "").upper()
            if verdict != "CLEAR":
                blockers.append("semantic-reduction-review-block")
            if semantic_review.get("lane_contract_verified") is not True:
                blockers.append("lane-contract-independent-review-failed")
            if semantic_review.get("source_claims_grounded") is not True:
                blockers.append("source-claim-grounding-failed")
            grounding = semantic_review.get("source_claim_grounding") or {}
            if not isinstance(grounding, dict) or any((grounding.get(key) or {}).get("grounded") is not True for key in ("source_a", "source_b")):
                blockers.append("source-claim-grounding-incomplete")
            if require_primary_registry and isinstance(grounding, dict):
                for source_key in ("source_a", "source_b"):
                    source = evidence.get(source_key) or {}
                    ref = str(source.get("ref") or "").strip()
                    record = registry.get(ref) or {}
                    grounded = grounding.get(source_key) or {}
                    excerpt = str(grounded.get("evidence_excerpt") or "").strip()
                    words = excerpt.split()
                    abstract = _normalized_evidence_text(record.get("abstract") or "")
                    facts = [_normalized_evidence_text(str(fact.get("text") or "")) for fact in (record.get("empirical_facts") or []) if isinstance(fact, dict)]
                    typed = record.get("typed_evidence") or {}
                    assumptions = [_normalized_evidence_text(str(fact.get("text") or "")) for fact in typed.get("operational_assumptions") or [] if isinstance(fact, dict)]
                    failures = [_normalized_evidence_text(str(fact.get("text") or "")) for fact in typed.get("measured_failures") or [] if isinstance(fact, dict)]
                    boundaries = [_normalized_evidence_text(str(fact.get("text") or "")) for fact in typed.get("boundary_observations") or [] if isinstance(fact, dict)]
                    excerpt_norm = _normalized_evidence_text(excerpt)
                    evidence_source = str(grounded.get("evidence_source") or "").strip().lower()
                    role = str(source.get("evidence_role") or "").strip().upper()
                    abstract_match = bool(excerpt_norm and excerpt_norm in abstract)
                    fact_match = bool(excerpt_norm and any(excerpt_norm in fact for fact in facts))
                    assumption_match = bool(excerpt_norm and any(excerpt_norm in fact for fact in assumptions))
                    failure_match = bool(excerpt_norm and any(excerpt_norm in fact for fact in failures))
                    boundary_match = bool(excerpt_norm and any(excerpt_norm in fact for fact in boundaries))
                    fulltext_match = fact_match or assumption_match or failure_match or boundary_match
                    source_match = abstract_match if evidence_source == "abstract" else (fulltext_match if evidence_source == "fulltext" else (abstract_match or fulltext_match))
                    role_match = (role == "OPERATIONAL_ASSUMPTION" and assumption_match) or (role == "EMPIRICAL_FACT" and (abstract_match or fact_match or failure_match or boundary_match))
                    if not (4 <= len(words) <= 30 and source_match and role_match):
                        blockers.append(f"source-claim-evidence-excerpt-mismatch:{source_key}")
            if not _nonempty(semantic_review.get("reviewer_model")) or not _nonempty(semantic_review.get("raw_sha256")):
                blockers.append("semantic-reduction-review-provenance-missing")

    authority = candidate.get("authority") or {}
    for key in ("method_design", "experiment_blueprint", "local_validation", "p0", "gpu", "full_experiment"):
        if authority.get(key) is not False:
            blockers.append(f"authority-must-be-false:{key}")

    blockers = sorted(set(blockers))
    return {
        "schema_version": "2.0",
        "candidate_id": str(candidate.get("candidate_id") or ""),
        "discovery_lane": lane,
        "passed": not blockers,
        "status": "PROBLEM_GATE_PASS_AWAIT_HUMAN_PAPER_DESIGN" if not blockers else "PROBLEM_GATE_BLOCKED",
        "blockers": blockers,
        "checks": checks,
        "policy": POLICY,
        "authority": {
            "paper_design_eligible_for_human_review": not blockers,
            "method_design": False,
            "experiment_blueprint": False,
            "local_validation": False,
            "p0": False,
            "gpu": False,
            "full_experiment": False,
        },
    }


def audit_shadow_problem_candidate(
    candidate: dict[str, Any],
    *,
    primary_evidence_by_ref: dict[str, dict[str, Any]] | None = None,
    require_primary_registry: bool = False,
    require_semantic_review: bool = True,
) -> dict[str, Any]:
    lane = str(candidate.get("discovery_lane") or "").strip().upper()
    base = audit_problem_candidate(
        candidate,
        primary_evidence_by_ref=primary_evidence_by_ref,
        require_primary_registry=require_primary_registry,
        require_semantic_review=require_semantic_review,
    )
    blockers = set(str(value) for value in base.get("blockers") or [])
    if lane in SEARCH_PORTFOLIO_PRIMITIVES:
        blockers.discard(f"unknown-discovery-lane:{lane}")
        if lane not in DISCOVERY_LANES:
            blockers.update(_shadow_lane_contract_blockers(candidate))
    else:
        blockers.add(f"unknown-shadow-search-primitive:{lane or 'EMPTY'}")
    blockers = sorted(blockers)
    checks = [dict(row) for row in base.get("checks") or []]
    for row in checks:
        if row.get("key") == "discovery-lane-contract":
            row["key"] = "shadow-search-primitive-contract"
            row["pass"] = not any(
                blocker.startswith(("unknown-shadow-search-primitive:", "shadow-primitive-", "forbidden-discovery-lane:"))
                for blocker in blockers
            )
            row["lane"] = lane
    return {
        "schema_version": "1.0-shadow",
        "candidate_id": str(candidate.get("candidate_id") or ""),
        "search_primitive": lane,
        "passed": not blockers,
        "status": "SHADOW_MACHINE_REVIEWABLE" if not blockers else "SHADOW_MACHINE_BLOCKED",
        "blockers": blockers,
        "checks": checks,
        "scientific_authority": False,
        "authority": {
            "live_problem_gate": False,
            "paper_design_eligible_for_human_review": False,
            "method_design": False,
            "experiment_blueprint": False,
            "local_validation": False,
            "p0": False,
            "gpu": False,
            "full_experiment": False,
        },
    }


def build_problem_discovery_contract_state() -> dict[str, Any]:
    audit_rows=reduction_pattern_audit()
    classes={name:sum(row["audit_class"]==name for row in audit_rows) for name in ("VALID_HARD_VETO","SOFT_COLLISION","NEEDS_EXACT_REDUCTION_TEST","TOO_GENERIC_TO_VETO")}
    return {
        "schema_version":"2.2",
        "policy":POLICY,
        "candidate_schema":candidate_schema(),
        "reduction_falsifiability_contract":dict(REDUCTION_FALSIFIABILITY_CONTRACT),
        "reduction_pattern_audit":audit_rows,
        "summary":{
            "required_top_level_fields":len(REQUIRED_FIELDS),
            "allowed_discovery_lanes":len(DISCOVERY_LANES),
            "forbidden_discovery_lanes":len(FORBIDDEN_DISCOVERY_LANES),
            "saturation_patterns":len(REDUCTION_PATTERNS),
            "reduction_audit_classes":classes,
            "minimum_distinct_primary_sources":min(LANE_DISTINCT_SOURCE_MINIMUM[lane] for lane in DISCOVERY_LANES),
            "maximum_lane_minimum_distinct_primary_sources":max(LANE_DISTINCT_SOURCE_MINIMUM[lane] for lane in DISCOVERY_LANES),
            "minimum_grounded_evidence_items":2,
            "minimum_mature_theory_baselines":2,
            "automatic_method_authority":0,
            "automatic_experiment_authority":0,
        },
        "lane_contracts":[{"lane":lane,"source_roles":list(LANE_SOURCE_ROLES[lane]),"minimum_distinct_primary_sources":LANE_DISTINCT_SOURCE_MINIMUM[lane],"required_lane_evidence":list(LANE_EVIDENCE_REQUIRED[lane]),"machine_contract":LANE_MACHINE_CONTRACTS[lane]} for lane in DISCOVERY_LANES],
        "generator_order":[
            "INVERT certified closed basins only as zero-authority search priors: extract the opposite principle/search seed, then require fresh primary grounding and the recorded reopen condition before retaining a branch",
            "VERIFY any proposed feedback mechanism has a causal write path into selection, gating, rollback, synthesis, memory admission, artifact promotion, or another state transition; report-only measurements cannot justify feedback-effect experiments",
            "DETECT a grounded anomaly, sign reversal, threshold, nonmonotonic regime, or assumption violation; UNEXPLAINED_BOUNDARY may begin from one primary paper when it contains both required evidence items",
            "ALIGN treatment semantics before CONTRADICTION: intervention surface, executor/parameter state, comparator, endpoint, and timing must match; otherwise record REDUCIBLE cross-treatment contrast",
            "OPERATIONALIZE the smallest shared observable and adjacent/control regime without requiring a second paper to have used the same metric",
            "SEPARATE generator from reviewer: pending exact mature reductions may reach independent semantic review, but proven hard reductions never do",
            "BLOCK exact search-closure re-entry when the same live lane reuses the identical primary source set; reopening requires new evidence that can satisfy the recorded reopen condition",
            "MATERIALIZE a cheapest independent-truth falsifier from released units, first-party code, or an existing provenance-audited substrate whenever possible",
            "REDUCE using closest work + mature theories under the same-information Reduction Falsifiability Contract",
            "retain only a residual with an ex-ante distinguishing prediction over the strongest reduction",
            "require independent lane-contract + exact source grounding review",
            "freeze cheapest problem falsifier and endpoint headroom",
            "audit Problem Gate",
            "human Paper Design only if Problem Gate passes",
        ],
    }
