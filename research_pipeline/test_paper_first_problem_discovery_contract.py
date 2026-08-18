from __future__ import annotations

import unittest

from .paper_first_fresh_saturation import REDUCTION_PATTERNS
from .paper_first_problem_discovery_contract import (
    DISCOVERY_LANES,
    SEARCH_PORTFOLIO_PRIMITIVES,
    LANE_DISTINCT_SOURCE_MINIMUM,
    FORBIDDEN_DISCOVERY_LANES,
    audit_problem_candidate,
    audit_shadow_problem_candidate,
    build_problem_discovery_contract_state,
)


def _lane_evidence(lane: str) -> dict:
    if lane == "CONTRADICTION":
        return {
            "shared_operationalization": "Both sources evaluate the same causal treatment under the same bounded setting.",
            "shared_intervention_semantics": "Both sources apply the same frozen inference-time context treatment to an unchanged policy.",
            "shared_adaptation_stage": "Both treatments occur at inference time with no parameter update or training-data selection stage.",
            "source_a_intervention": "Apply the same inference-time procedural artifact to a frozen executor.",
            "source_b_intervention": "Apply the same inference-time procedural artifact to a frozen executor.",
            "intervention_surface_match": True,
            "executor_state_match": True,
            "comparator_match": True,
            "endpoint_match": True,
            "timing_match": True,
            "treatment_equivalence_argument": "Both sources intervene on the identical inference-time artifact while keeping executor parameters, comparator construction, endpoint, and timing fixed.",
            "incompatibility": "The two grounded facts require opposite outcomes under that shared operationalization.",
        }
    if lane == "CONVERGENT_FAILURE":
        return {
            "shared_condition": "Both methods are evaluated under the same bounded condition C.",
            "method_a": "Method family A",
            "method_b": "Method family B",
            "failure_a": "Method A exhibits quantitative failure under C.",
            "failure_b": "Method B exhibits quantitative failure under C.",
            "independence_basis": "The two method families use distinct mechanisms and implementations.",
        }
    if lane == "ASSUMPTION_BREAK":
        return {
            "assumption": "The method assumes stationary tool availability during deployment.",
            "violation": "Independent evidence measures non-stationary tool availability and a corresponding failure.",
            "scope_link": "The deployment setting falls within the method's stated operational scope.",
        }
    if lane == "UNEXPLAINED_BOUNDARY":
        return {"shared_measurement":"Both sources use the same success metric for the same phenomenon.","boundary_observation":"Source A measures a robust sign or regime change near boundary B.","adjacent_regime":"Source B establishes the expected behavior in the adjacent regime.","unexplained_transition":"Neither grounded source explains the transition location or shape."}
    if lane == "IDENTIFIABILITY_GAP":
        return {"target_question":"Which causal mechanism produced the same observed endpoint?","observational_equivalence":"Both mechanisms generate the same available observation.","measured_proxy":"Current work measures only endpoint success.","decision_consequence":"The repair decision differs across the observationally equivalent mechanisms."}
    if lane == "MISSING_DECISION_OBJECT":
        return {"surrogate_a":"Source A optimizes immediate success.","surrogate_b":"Source B optimizes retention.","downstream_decision":"A persistent update must be accepted, rejected, or probed further.","mismatch_evidence":"The two surrogates can recommend different actions under the same update."}
    if lane == "COMPOSITION_INTERACTION":
        return {"component_a":"Component A has an isolated account.","component_b":"Component B has an isolated account.","composition_condition":"Both components are active in the same persistent agent.","interaction_observation":"The composed outcome differs from isolated behavior.","nonadditivity_basis":"The deviation is not reproduced by adding isolated effects."}
    if lane == "CROSS_DOMAIN_STRUCTURAL_ANALOGY":
        return {"source_domain_structure":"Partial-failure consistency in distributed systems.","agent_specific_constraint":"The agent rewrites the persistent artifact that later conditions its own policy.","agent_evidence_link":"The grounded Agent results exhibit self-authored persistent state plus downstream reuse.","why_not_simple_transfer":"The feedback from self-authored state changes the observable intervention structure."}
    if lane == "NEW_CAPABILITY_QUESTION":
        return {"new_capability":"Recent agents can persist and revise executable skills across episodes.","newly_observable_signal":"The same skill can now be intervened on and re-used downstream.","previous_measurement_limit":"Earlier stateless settings could not expose persistent cross-episode consequences.","capability_specific_constraint":"The persistent artifact becomes part of future decision context."}
    if lane == "LONGITUDINAL_EMERGENCE":
        return {"shared_measurement":"Both sources measure task success over repeated adaptation.","short_horizon_regime":"Short runs remain stable.","long_horizon_regime":"Longer runs exhibit a different regime.","emergence_signature":"The transition survives matched per-step improvement controls."}
    return {}


def valid_candidate(lane: str = "CONTRADICTION") -> dict:
    lane = lane.upper()
    role_a = "OPERATIONAL_ASSUMPTION" if lane == "ASSUMPTION_BREAK" else "EMPIRICAL_FACT"
    claim_a = (
        "The method assumes stationary tool availability during deployment."
        if lane == "ASSUMPTION_BREAK"
        else "Observed A under frozen setting."
    )
    return {
        "candidate_id": "N1",
        "title": f"A {lane.lower()} research problem",
        "discovery_lane": lane,
        "empirical_evidence": {
            "source_a": {
                "ref": "arXiv:2608.00001",
                "title": "Primary A",
                "claim": claim_a,
                "evidence_role": role_a,
                "primary_source": True,
                "primary_url": "https://arxiv.org/abs/2608.00001",
                "source_sha256": "a" * 64,
            },
            "source_b": {
                "ref": "arXiv:2608.00002",
                "title": "Primary B",
                "claim": "Observed independent outcome B under the relevant setting.",
                "evidence_role": "EMPIRICAL_FACT",
                "primary_source": True,
                "primary_url": "https://arxiv.org/abs/2608.00002",
                "source_sha256": "b" * 64,
            },
            "relation": "The two grounded source items instantiate the selected discovery-lane relation.",
        },
        "lane_evidence": _lane_evidence(lane),
        "irreducible_object": "A formally named object that is not one of the saturated reductions.",
        "mature_theory_baselines": [
            {"name":"Theory A","same_information_projection":"Uses all observed variables and metadata.","ex_ante_prediction":"Predicts invariance under condition C.","distinguishing_prediction":"Candidate predicts a sign change under C.","cannot_express":"Cannot express the sign change without the candidate structure.","reduction_class":"SOFT_COLLISION","exact_reduction_test":"Fit Theory A on identical observables and test the preregistered sign contrast."},
            {"name":"Theory B","same_information_projection":"Uses the same observations and interventions.","ex_ante_prediction":"Predicts the same outcome in both regimes.","distinguishing_prediction":"Candidate predicts regime-specific divergence.","cannot_express":"Cannot express the regime-specific divergence under identical information.","reduction_class":"TOO_GENERIC_TO_VETO","exact_reduction_test":"Fit Theory B with the identical information set and test the regime contrast."},
        ],
        "reduction_falsifiability_contract":{"same_observable_information_checked":True,"ex_ante_exact_prediction_checked":True,"distinguishing_prediction_checked":True,"scope_boundary_checked":True,"all_exact_reduction_tests_resolved":True},
        "same_information_nonreducibility": {
            "claim": "Prediction P differs from both mature theories.",
            "why_each_baseline_cannot_express_prediction": "Theory A lacks X; Theory B lacks Y under identical information.",
        },
        "exact_prediction": "Under condition C, outcome Y must change sign while mature baselines predict invariance.",
        "strongest_same_information_baseline": "Theory A plus Theory B with identical observations.",
        "domain_transfer_audit": {
            "mature_source_domain": "generic mature domain",
            "mature_object": "known object Z",
            "why_not_domain_transfer": "Prediction P depends on an additional structure not representable by Z.",
        },
        "saturation_scan": {"checked": True, "matched_patterns": []},
        "cheapest_problem_falsifier": "Check whether condition C produces the required prediction before designing a method.",
        "endpoint_headroom_requirement": "At least two valid outcome states and non-censored terminal variation must exist.",
        "semantic_reduction_review": {
            "reviewed": True,
            "block_only": True,
            "verdict": "CLEAR",
            "reviewer_model": "independent-test-reviewer",
            "raw_sha256": "c" * 64,
            "source_claims_grounded": True,
            "source_claim_grounding": {
                "source_a": {"grounded": True, "evidence_source": "abstract", "evidence_excerpt": claim_a.rstrip(".")},
                "source_b": {"grounded": True, "evidence_source": "abstract", "evidence_excerpt": "Observed independent outcome B under the relevant setting"},
            },
            "lane_contract_verified": True,
            "lane_contract_reason": "The two grounded source items satisfy the selected lane contract.",
            "matched_patterns": [],
            "strongest_reduction": "none",
        },
        "authority": {
            "method_design": False,
            "experiment_blueprint": False,
            "local_validation": False,
            "p0": False,
            "gpu": False,
            "full_experiment": False,
        },
    }


class PaperFirstProblemDiscoveryContractTest(unittest.TestCase):
    def test_contract_keeps_four_final_lanes_but_enables_canonical_double_funnel(self) -> None:
        state = build_problem_discovery_contract_state()
        policy = state["policy"]
        self.assertTrue(policy["multi_lane_discovery_required"])
        self.assertFalse(policy["contradiction_first_required"])
        self.assertTrue(policy["contradiction_lane_retained"])
        self.assertEqual(tuple(policy["allowed_discovery_lanes"]), DISCOVERY_LANES)
        self.assertEqual(tuple(policy["forbidden_discovery_lanes"]), FORBIDDEN_DISCOVERY_LANES)
        self.assertTrue(policy["lane_specific_machine_evidence_contract_required"])
        # These three search_portfolio flags describe the historical published
        # pre-split artifact only; canonical discovery reuses the engine inside
        # one new atomic double-funnel transaction without promoting history.
        self.assertFalse(policy["search_portfolio_required"]); self.assertTrue(policy["search_portfolio_is_shadow_only"]); self.assertTrue(policy["search_portfolio_cannot_publish_canonical_generator_or_queue"])
        self.assertTrue(policy["canonical_double_funnel_required"]);self.assertTrue(policy["canonical_double_funnel_reuses_portfolio_engine"]);self.assertTrue(policy["historical_search_portfolio_remains_shadow_only"])
        self.assertFalse(policy["one_content_addressed_pool_allows_at_most_one_live_generator_call"]);self.assertTrue(policy["one_content_addressed_pool_allows_at_most_one_discovery_transaction"]);self.assertTrue(policy["bounded_provider_subcalls_inside_discovery_transaction"])
        self.assertTrue(policy["attack_repair_split_before_terminal_review"]);self.assertTrue(policy["principle_reduction_does_not_auto_close_other_paperability_axes"]);self.assertTrue(policy["cheap_problem_falsifier_may_precede_exact_reduction"]);self.assertTrue(policy["exact_reduction_required_before_final_problem_gate"])
        self.assertEqual(set(policy["paperability_axes"]),{"P","M","E","B","T","S"})
        self.assertEqual(tuple(policy["search_portfolio_primitives"]), SEARCH_PORTFOLIO_PRIMITIVES)
        self.assertTrue(policy["expansion_reduction_separated"]); self.assertTrue(policy["mature_theory_veto_delayed_until_formulated_branch"]); self.assertTrue(policy["reduction_falsifiability_contract_required"]); self.assertTrue(policy["generic_theory_label_cannot_veto"])
        self.assertTrue(policy["no_lane_specific_downstream_relaxation"])
        self.assertTrue(policy["two_mature_theory_baselines_required"])
        self.assertTrue(policy["same_information_nonreducibility_required"])
        self.assertTrue(policy["domain_transfer_veto_required"])
        self.assertTrue(policy["reduction_pending_may_reach_block_only_semantic_review"])
        self.assertTrue(policy["reduction_pending_cannot_pass_problem_gate"])
        self.assertTrue(policy["contradiction_requires_matched_intervention_semantics"])
        self.assertTrue(policy["contradiction_requires_matched_adaptation_stage"])
        self.assertTrue(policy["positive_residual_search_enabled"])
        self.assertTrue(policy["positive_residual_asset_requires_provenance_manifest"])
        self.assertTrue(policy["positive_residual_asset_is_zero_authority_search_evidence"])
        self.assertTrue(policy["positive_residual_requires_surviving_phenomenon_and_clean_mechanism_stop"])
        self.assertTrue(policy["positive_residual_requires_prospective_pre_outcome_prediction"])
        self.assertTrue(policy["positive_residual_outcome_leakage_forbidden"])
        self.assertTrue(policy["positive_residual_direct_seed_required_in_unexplained_boundary_shard"])
        self.assertTrue(policy["inactive_search_assets_hidden_from_generator"])
        self.assertTrue(policy["inactive_search_assets_remain_provenance_archived"])
        self.assertTrue(policy["no_active_asset_fallback_requires_latest_primary_quantitative_anomaly"])
        self.assertTrue(policy["fresh_phenomenon_seed_must_name_measured_boundary_or_failure"])
        self.assertTrue(policy["fresh_phenomenon_asset_readiness_is_priority_not_novelty_authority"])
        self.assertTrue(policy["fresh_phenomenon_missing_substrate_is_hold_not_scientific_fail"])
        self.assertTrue(policy["fresh_phenomenon_recent_window_source_coverage_required"])
        self.assertTrue(policy["fresh_phenomenon_target_is_evidence_level_not_source_level"])
        self.assertTrue(policy["fresh_phenomenon_principle_closure_is_exact_evidence_sha_only"])
        self.assertTrue(policy["fresh_phenomenon_closure_does_not_blacklist_source"])
        self.assertTrue(policy["fresh_phenomenon_measured_failure_requires_failure_cue"])
        self.assertTrue(policy["fresh_phenomenon_shard_has_deterministic_target_ref"])
        self.assertTrue(policy["fresh_phenomenon_shard_has_deterministic_phenomenon_id"])
        self.assertTrue(policy["fresh_phenomenon_seed1_must_match_target_ref"])
        self.assertTrue(policy["fresh_phenomenon_seed1_must_match_target_phenomenon"])
        self.assertTrue(policy["temporal_exposure_relabeling_after_longitudinal_reduction_forbidden"])
        self.assertTrue(policy["treatment_semantics_seed_requires_executable_version_change"])
        self.assertTrue(policy["treatment_semantics_seed_requires_versioned_treatment_reduction_first"])
        self.assertTrue(policy["contradiction_requires_treatment_surface_alignment"])
        self.assertTrue(policy["contradiction_requires_executor_state_alignment"])
        self.assertTrue(policy["contradiction_requires_comparator_endpoint_timing_alignment"])
        self.assertTrue(policy["cross_treatment_sign_difference_is_reducible_not_contradiction"])
        self.assertTrue(policy["generator_pre_review_allows_pending_exact_reduction"])
        self.assertTrue(policy["generator_pre_review_still_blocks_proven_hard_reduction"])
        self.assertTrue(policy["semantic_reviewer_owns_pending_exact_reduction_adjudication"])
        self.assertTrue(policy["final_problem_gate_still_requires_all_reductions_resolved"])
        self.assertTrue(policy["principle_dead_end_exact_source_reentry_forbidden"])
        self.assertTrue(policy["principle_dead_end_reopen_requires_new_evidence"])
        self.assertTrue(policy["saturation_map_check_required"])
        self.assertTrue(state["candidate_schema"]["semantic_reduction_review"]["both_source_claims_require_exact_primary_evidence_grounding"])
        self.assertTrue(state["candidate_schema"]["semantic_reduction_review"]["lane_contract_must_be_independently_verified"])
        self.assertEqual(state["summary"]["allowed_discovery_lanes"], 4)
        self.assertEqual(state["summary"]["forbidden_discovery_lanes"], 3)
        self.assertEqual(state["summary"]["saturation_patterns"], len(REDUCTION_PATTERNS))
        self.assertEqual((state["summary"]["automatic_method_authority"], state["summary"]["automatic_experiment_authority"]), (0, 0))

    def test_all_four_live_lanes_can_reach_only_human_paper_design(self) -> None:
        for lane in DISCOVERY_LANES:
            with self.subTest(lane=lane):
                audit = audit_problem_candidate(valid_candidate(lane))
                self.assertTrue(audit["passed"], audit["blockers"])
                self.assertEqual(audit["discovery_lane"], lane)
                self.assertEqual(audit["status"], "PROBLEM_GATE_PASS_AWAIT_HUMAN_PAPER_DESIGN")
                self.assertTrue(audit["authority"]["paper_design_eligible_for_human_review"])
                for key in ("method_design", "experiment_blueprint", "local_validation", "p0", "gpu", "full_experiment"):
                    self.assertFalse(audit["authority"][key])

    def test_pending_exact_reduction_can_reach_semantic_review_but_not_final_problem_gate(self) -> None:
        candidate = valid_candidate("ASSUMPTION_BREAK")
        candidate["mature_theory_baselines"][1]["reduction_class"]="NEEDS_EXACT_REDUCTION_TEST"
        candidate["reduction_falsifiability_contract"]["all_exact_reduction_tests_resolved"]=False
        strict=audit_problem_candidate(candidate,require_semantic_review=False)
        pre_review=audit_problem_candidate(candidate,require_semantic_review=False,allow_pending_reduction_for_semantic_review=True)
        self.assertFalse(strict["passed"])
        self.assertIn("unresolved-exact-reduction-test:2",strict["blockers"])
        self.assertTrue(pre_review["passed"],pre_review["blockers"])

    def test_proven_hard_reduction_still_blocks_semantic_review_pre_gate(self) -> None:
        candidate = valid_candidate("ASSUMPTION_BREAK")
        candidate["saturation_scan"]["matched_patterns"]=[REDUCTION_PATTERNS[0]["key"]]
        pre_review=audit_problem_candidate(candidate,require_semantic_review=False,allow_pending_reduction_for_semantic_review=True)
        self.assertFalse(pre_review["passed"])
        self.assertTrue(any(x.startswith("saturation-proven-hard-reduction:") for x in pre_review["blockers"]))

    def test_contradiction_blocks_cross_treatment_sign_contrast_before_semantic_review(self) -> None:
        candidate = valid_candidate("CONTRADICTION")
        candidate["lane_evidence"].update({
            "source_a_intervention": "Inference-time static skill on a frozen executor.",
            "source_b_intervention": "SFT parameter update followed by prompt-history ablation.",
            "intervention_surface_match": False,
            "executor_state_match": False,
            "treatment_equivalence_argument": "Both use text, but the causal update surfaces differ.",
        })
        audit = audit_problem_candidate(candidate, require_semantic_review=False)
        self.assertFalse(audit["passed"])
        self.assertIn("contradiction-treatment-alignment-failed:intervention_surface_match", audit["blockers"])
        self.assertIn("contradiction-treatment-alignment-failed:executor_state_match", audit["blockers"])

    def test_shadow_search_primitives_can_be_machine_audited(self) -> None:
        for primitive in SEARCH_PORTFOLIO_PRIMITIVES:
            if primitive in DISCOVERY_LANES:
                continue
            candidate = valid_candidate(primitive)
            live = audit_problem_candidate(candidate)
            shadow = audit_shadow_problem_candidate(candidate)
            self.assertFalse(live["passed"])
            self.assertTrue(shadow["passed"], shadow["blockers"])
            self.assertEqual(shadow["status"], "SHADOW_MACHINE_REVIEWABLE")
            self.assertFalse(shadow["scientific_authority"])
            self.assertFalse(shadow["authority"]["live_problem_gate"])
            self.assertFalse(shadow["authority"]["paper_design_eligible_for_human_review"])

    def test_shadow_search_primitives_cannot_enter_live_problem_gate(self) -> None:
        for primitive in SEARCH_PORTFOLIO_PRIMITIVES:
            if primitive in DISCOVERY_LANES:
                continue
            with self.subTest(primitive=primitive):
                candidate = valid_candidate()
                candidate["discovery_lane"] = primitive
                candidate["lane_evidence"] = _lane_evidence(primitive)
                audit = audit_problem_candidate(candidate)
                self.assertFalse(audit["passed"])
                self.assertTrue(any(value.startswith("unknown-discovery-lane:") for value in audit["blockers"]), audit["blockers"])

    def test_three_speculative_lanes_are_forbidden(self) -> None:
        for lane in FORBIDDEN_DISCOVERY_LANES:
            with self.subTest(lane=lane):
                candidate = valid_candidate()
                candidate["discovery_lane"] = lane
                audit = audit_problem_candidate(candidate)
                self.assertFalse(audit["passed"])
                self.assertIn(f"forbidden-discovery-lane:{lane}", audit["blockers"])

    def test_distinct_primary_source_minimum_is_lane_specific(self) -> None:
        for lane in DISCOVERY_LANES:
            with self.subTest(lane=lane):
                candidate=valid_candidate(lane)
                candidate["empirical_evidence"]["source_b"]=dict(candidate["empirical_evidence"]["source_a"])
                audit=audit_problem_candidate(candidate)
                if LANE_DISTINCT_SOURCE_MINIMUM[lane]==2:
                    self.assertFalse(audit["passed"]);self.assertTrue(any(x.startswith("discovery-lane-requires-2-distinct-primary-sources") for x in audit["blockers"]))
                else:
                    # Only the duplicate-source condition is under test; role must still match.
                    candidate["empirical_evidence"]["source_b"]["evidence_role"]="EMPIRICAL_FACT"
                    audit=audit_problem_candidate(candidate)
                    self.assertTrue(audit["passed"],audit["blockers"])

    def test_assumption_break_requires_explicit_assumption_role(self) -> None:
        candidate = valid_candidate("ASSUMPTION_BREAK")
        candidate["empirical_evidence"]["source_a"]["evidence_role"] = "EMPIRICAL_FACT"
        audit = audit_problem_candidate(candidate)
        self.assertFalse(audit["passed"])
        self.assertTrue(any(value.startswith("lane-source-role-mismatch:ASSUMPTION_BREAK") for value in audit["blockers"]))

    def test_convergent_failure_requires_distinct_methods_and_all_lane_fields(self) -> None:
        candidate = valid_candidate("CONVERGENT_FAILURE")
        candidate["lane_evidence"]["method_b"] = candidate["lane_evidence"]["method_a"]
        candidate["lane_evidence"].pop("independence_basis")
        audit = audit_problem_candidate(candidate)
        self.assertFalse(audit["passed"])
        self.assertIn("convergent-failure-requires-distinct-methods", audit["blockers"])
        self.assertIn("lane-evidence-missing:CONVERGENT_FAILURE:independence_basis", audit["blockers"])

    def test_saturation_match_hard_blocks_every_lane(self) -> None:
        candidate = valid_candidate("UNEXPLAINED_BOUNDARY")
        candidate["saturation_scan"] = {"checked": True, "matched_patterns": ["typed-epistemic-authority"]}
        audit = audit_problem_candidate(candidate)
        self.assertFalse(audit["passed"])
        self.assertTrue(any(value.startswith("saturation-proven-hard-reduction:") for value in audit["blockers"]))


    def test_generic_pattern_similarity_does_not_hard_veto(self) -> None:
        candidate=valid_candidate("UNEXPLAINED_BOUNDARY")
        candidate["saturation_scan"]={"checked":True,"matched_patterns":[],"pending_patterns":[],"rejected_patterns":[{"key":"stream-instability","reason":"Generic dynamics does not give the candidate-level intervention prediction."}]}
        audit=audit_problem_candidate(candidate)
        self.assertTrue(audit["passed"],audit["blockers"])

    def test_pending_exact_reduction_blocks_problem_gate(self) -> None:
        candidate=valid_candidate("IDENTIFIABILITY_GAP")
        candidate["saturation_scan"]={"checked":True,"matched_patterns":[],"pending_patterns":[{"key":"horizon-censored-attribution","exact_reduction_test":"Fit the exact partial-identification baseline on the same observables."}],"rejected_patterns":[]}
        audit=audit_problem_candidate(candidate)
        self.assertFalse(audit["passed"]); self.assertIn("saturation-exact-reduction-pending:horizon-censored-attribution",audit["blockers"])

    def test_semantic_review_must_verify_lane_contract(self) -> None:
        candidate = valid_candidate("CONTRADICTION")
        candidate["semantic_reduction_review"]["lane_contract_verified"] = False
        audit = audit_problem_candidate(candidate)
        self.assertFalse(audit["passed"])
        self.assertIn("lane-contract-independent-review-failed", audit["blockers"])

    def test_candidate_cannot_self_authorize_execution(self) -> None:
        candidate = valid_candidate("ASSUMPTION_BREAK")
        candidate["authority"]["local_validation"] = True
        audit = audit_problem_candidate(candidate)
        self.assertFalse(audit["passed"])
        self.assertIn("authority-must-be-false:local_validation", audit["blockers"])


if __name__ == "__main__":
    unittest.main()
