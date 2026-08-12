from __future__ import annotations

import unittest

from .paper_first_fresh_saturation import REDUCTION_PATTERNS
from .paper_first_problem_discovery_contract import audit_problem_candidate, build_problem_discovery_contract_state


def valid_candidate() -> dict:
    return {
        "candidate_id":"N1",
        "title":"A contradiction-first research problem",
        "empirical_contradiction":{
            "source_a":{"ref":"arXiv:2608.00001","title":"Primary A","claim":"Observed A under frozen setting.","primary_source":True,"primary_url":"https://arxiv.org/abs/2608.00001","source_sha256":"a"*64},
            "source_b":{"ref":"arXiv:2608.00002","title":"Primary B","claim":"Observed not-A under a related frozen setting.","primary_source":True,"primary_url":"https://arxiv.org/abs/2608.00002","source_sha256":"b"*64},
            "tension":"The two observations cannot both be explained by the same current mechanism account.",
        },
        "irreducible_object":"A formally named object that is not one of the saturated reductions.",
        "mature_theory_baselines":[
            {"name":"Theory A","same_information_projection":"Uses all observed variables and metadata.","reduction_test":"Cannot express prediction P under these observations."},
            {"name":"Theory B","same_information_projection":"Uses the same observations and interventions.","reduction_test":"Cannot express prediction P without an extra object."},
        ],
        "same_information_nonreducibility":{"claim":"Prediction P differs from both mature theories.","why_each_baseline_cannot_express_prediction":"Theory A lacks X; Theory B lacks Y under identical information."},
        "exact_prediction":"Under condition C, outcome Y must change sign while mature baselines predict invariance.",
        "strongest_same_information_baseline":"Theory A plus Theory B with identical observations.",
        "domain_transfer_audit":{"mature_source_domain":"generic mature domain","mature_object":"known object Z","why_not_domain_transfer":"Prediction P depends on an additional structure not representable by Z."},
        "saturation_scan":{"checked":True,"matched_patterns":[]},
        "cheapest_problem_falsifier":"Check whether condition C ever produces the required sign change before designing a method.",
        "endpoint_headroom_requirement":"At least two valid outcome states and non-censored terminal variation must exist.",
        "semantic_reduction_review":{"reviewed":True,"block_only":True,"verdict":"CLEAR","reviewer_model":"independent-test-reviewer","raw_sha256":"c"*64,"matched_patterns":[],"strongest_reduction":"none"},
        "authority":{"method_design":False,"experiment_blueprint":False,"local_validation":False,"p0":False,"gpu":False,"full_experiment":False},
    }


class PaperFirstProblemDiscoveryContractTest(unittest.TestCase):
    def test_contract_is_contradiction_and_theory_first(self) -> None:
        state=build_problem_discovery_contract_state(); p=state["policy"]
        self.assertTrue(p["contradiction_first_required"])
        self.assertTrue(p["two_primary_source_facts_required"])
        self.assertTrue(p["two_mature_theory_baselines_required"])
        self.assertTrue(p["same_information_nonreducibility_required"])
        self.assertTrue(p["domain_transfer_veto_required"])
        self.assertTrue(p["saturation_map_check_required"])
        self.assertEqual(state["summary"]["saturation_patterns"],len(REDUCTION_PATTERNS))
        self.assertEqual((state["summary"]["automatic_method_authority"],state["summary"]["automatic_experiment_authority"]),(0,0))

    def test_valid_problem_can_only_reach_human_paper_design_review(self) -> None:
        audit=audit_problem_candidate(valid_candidate())
        self.assertTrue(audit["passed"],audit["blockers"])
        self.assertEqual(audit["status"],"PROBLEM_GATE_PASS_AWAIT_HUMAN_PAPER_DESIGN")
        self.assertTrue(audit["authority"]["paper_design_eligible_for_human_review"])
        for key in ("method_design","experiment_blueprint","local_validation","p0","gpu","full_experiment"):
            self.assertFalse(audit["authority"][key])

    def test_one_primary_source_is_not_a_contradiction(self) -> None:
        c=valid_candidate(); c["empirical_contradiction"]["source_b"]={}
        audit=audit_problem_candidate(c)
        self.assertFalse(audit["passed"])
        self.assertIn("invalid-primary-source:2",audit["blockers"])
        self.assertIn("contradiction-requires-two-distinct-primary-sources",audit["blockers"])

    def test_saturation_match_hard_blocks_candidate(self) -> None:
        c=valid_candidate(); c["saturation_scan"]={"checked":True,"matched_patterns":["typed-epistemic-authority"]}
        audit=audit_problem_candidate(c)
        self.assertFalse(audit["passed"])
        self.assertTrue(any(x.startswith("saturation-pattern-match:") for x in audit["blockers"]))

    def test_semantic_reduction_review_is_block_only_and_required(self) -> None:
        c=valid_candidate(); c["semantic_reduction_review"]["verdict"]="BLOCK"
        audit=audit_problem_candidate(c)
        self.assertFalse(audit["passed"])
        self.assertIn("semantic-reduction-review-block",audit["blockers"])

    def test_candidate_cannot_self_authorize_execution(self) -> None:
        c=valid_candidate(); c["authority"]["local_validation"]=True
        audit=audit_problem_candidate(c)
        self.assertFalse(audit["passed"])
        self.assertIn("authority-must-be-false:local_validation",audit["blockers"])


if __name__=="__main__": unittest.main()
