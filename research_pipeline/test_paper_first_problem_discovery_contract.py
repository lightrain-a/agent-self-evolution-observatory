from __future__ import annotations

import unittest

from .paper_first_fresh_saturation import REDUCTION_PATTERNS
from .paper_first_problem_discovery_contract import (
    DISCOVERY_LANES,
    FORBIDDEN_DISCOVERY_LANES,
    audit_problem_candidate,
    build_problem_discovery_contract_state,
)


def _lane_evidence(lane: str) -> dict:
    if lane == "CONTRADICTION":
        return {
            "shared_operationalization": "Both sources evaluate the same measured behavior under the same bounded setting.",
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
        return {
            "shared_measurement": "Both sources use the same success metric for the same phenomenon.",
            "boundary_observation": "Source A measures a robust sign or regime change near boundary B.",
            "adjacent_regime": "Source B establishes the expected behavior in the adjacent regime.",
            "unexplained_transition": "Neither grounded source explains the transition location or shape.",
        }
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
            {
                "name": "Theory A",
                "same_information_projection": "Uses all observed variables and metadata.",
                "reduction_test": "Cannot express prediction P under these observations.",
            },
            {
                "name": "Theory B",
                "same_information_projection": "Uses the same observations and interventions.",
                "reduction_test": "Cannot express prediction P without an extra object.",
            },
        ],
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
    def test_contract_is_multilane_empirical_and_theory_first(self) -> None:
        state = build_problem_discovery_contract_state()
        policy = state["policy"]
        self.assertTrue(policy["multi_lane_discovery_required"])
        self.assertFalse(policy["contradiction_first_required"])
        self.assertTrue(policy["contradiction_lane_retained"])
        self.assertEqual(tuple(policy["allowed_discovery_lanes"]), DISCOVERY_LANES)
        self.assertEqual(tuple(policy["forbidden_discovery_lanes"]), FORBIDDEN_DISCOVERY_LANES)
        self.assertTrue(policy["lane_specific_machine_evidence_contract_required"])
        self.assertTrue(policy["no_lane_specific_downstream_relaxation"])
        self.assertTrue(policy["two_mature_theory_baselines_required"])
        self.assertTrue(policy["same_information_nonreducibility_required"])
        self.assertTrue(policy["domain_transfer_veto_required"])
        self.assertTrue(policy["saturation_map_check_required"])
        self.assertTrue(state["candidate_schema"]["semantic_reduction_review"]["both_source_claims_require_exact_primary_evidence_grounding"])
        self.assertTrue(state["candidate_schema"]["semantic_reduction_review"]["lane_contract_must_be_independently_verified"])
        self.assertEqual(state["summary"]["allowed_discovery_lanes"], 4)
        self.assertEqual(state["summary"]["forbidden_discovery_lanes"], 3)
        self.assertEqual(state["summary"]["saturation_patterns"], len(REDUCTION_PATTERNS))
        self.assertEqual((state["summary"]["automatic_method_authority"], state["summary"]["automatic_experiment_authority"]), (0, 0))

    def test_all_four_allowed_lanes_can_reach_only_human_paper_design(self) -> None:
        for lane in DISCOVERY_LANES:
            with self.subTest(lane=lane):
                audit = audit_problem_candidate(valid_candidate(lane))
                self.assertTrue(audit["passed"], audit["blockers"])
                self.assertEqual(audit["discovery_lane"], lane)
                self.assertEqual(audit["status"], "PROBLEM_GATE_PASS_AWAIT_HUMAN_PAPER_DESIGN")
                self.assertTrue(audit["authority"]["paper_design_eligible_for_human_review"])
                for key in ("method_design", "experiment_blueprint", "local_validation", "p0", "gpu", "full_experiment"):
                    self.assertFalse(audit["authority"][key])

    def test_three_speculative_lanes_are_forbidden(self) -> None:
        for lane in FORBIDDEN_DISCOVERY_LANES:
            with self.subTest(lane=lane):
                candidate = valid_candidate()
                candidate["discovery_lane"] = lane
                audit = audit_problem_candidate(candidate)
                self.assertFalse(audit["passed"])
                self.assertIn(f"forbidden-discovery-lane:{lane}", audit["blockers"])

    def test_two_distinct_primary_sources_are_required_in_every_lane(self) -> None:
        candidate = valid_candidate("CONVERGENT_FAILURE")
        candidate["empirical_evidence"]["source_b"] = {}
        audit = audit_problem_candidate(candidate)
        self.assertFalse(audit["passed"])
        self.assertIn("invalid-primary-source:2", audit["blockers"])
        self.assertIn("discovery-lane-requires-two-distinct-primary-sources", audit["blockers"])

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
        self.assertTrue(any(value.startswith("saturation-pattern-match:") for value in audit["blockers"]))

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
