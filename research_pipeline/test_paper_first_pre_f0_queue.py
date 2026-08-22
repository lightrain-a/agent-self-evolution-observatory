from __future__ import annotations

import copy
import unittest

from .paper_first_pre_f0_queue import build_pre_f0_queue, carry_forward_unresolved_support_debt


class PaperFirstPreF0QueueTest(unittest.TestCase):
    def candidate(self) -> dict:
        return {
            "candidate_id": "PORT-001",
            "title": "A surviving empirical boundary",
            "discovery_lane": "UNEXPLAINED_BOUNDARY",
            "source_branch_id": "B-R1",
            "primary_refs": ["arXiv:2608.00001", "arXiv:2608.00002"],
            "paperability_axes": {"P": {"status": "REDUCED"}, "E": {"status": "SUPPORTED"}},
            "surviving_paperability_axes": ["E"],
            "non_principle_surviving_axes": ["E"],
            "route_reason": "P_REDUCED_NON_P_AXIS_SURVIVES",
            "reduction_blockers": ["mature-theory-valid-hard-veto:0"],
            "exact_prediction": "The boundary reverses the held-out decision under the frozen information set.",
            "strongest_same_information_baseline": "Distribution-shift baseline with the same pre-outcome fields.",
            "cheapest_problem_falsifier": "Replay 12 matched released units and preregister a sign test.",
            "endpoint_headroom_requirement": "At least four matched reversals.",
            "post_f0_requirement": "RERUN_EXACT_SAME_INFORMATION_REDUCTION_BEFORE_PROBLEM_GATE",
            "scientific_authority": False,
            "authority": {"paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
        }

    def test_queue_is_zero_authority_and_requires_exact_reduction_after_positive_f0(self) -> None:
        generator={"run_id":"r1","status":"GENERATED_PRE_F0_EVIDENCE_ACQUISITION","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[self.candidate()]}
        state=build_pre_f0_queue(generator)
        self.assertEqual(state["status"],"PRE_F0_QUEUE_READY")
        self.assertEqual(state["summary"]["queued"],1)
        self.assertFalse(state["scientific_authority"])
        self.assertTrue(state["policy"]["positive_f0_requires_exact_same_information_reduction_recheck"])
        self.assertEqual(state["rows"][0]["next_if_positive"],"RERUN_EXACT_SAME_INFORMATION_REDUCTION")
        self.assertEqual(state["rows"][0]["primary_refs"],["arXiv:2608.00001","arXiv:2608.00002"])
        self.assertEqual(state["rows"][0]["candidate_identity_version"],"candidate-content-v1")
        self.assertEqual(len(state["rows"][0]["candidate_snapshot_sha256"]),64)
        self.assertTrue(state["policy"]["candidate_id_is_run_local_ordinal"])
        self.assertTrue(state["policy"]["candidate_snapshot_sha256_required"])
        self.assertTrue(all(value is False for value in state["rows"][0]["authority"].values()))

    def test_candidate_snapshot_is_independent_of_run_local_port_ordinal_but_changes_with_scientific_object(self) -> None:
        first=self.candidate();second=copy.deepcopy(first);second["candidate_id"]="PORT-099"
        first_state=build_pre_f0_queue({"run_id":"r1","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[first]})
        second_state=build_pre_f0_queue({"run_id":"r2","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[second]})
        self.assertEqual(first_state["rows"][0]["candidate_snapshot_sha256"],second_state["rows"][0]["candidate_snapshot_sha256"])
        changed=copy.deepcopy(second);changed["title"]="A different scientific candidate reusing the same local ordinal"
        changed_state=build_pre_f0_queue({"run_id":"r3","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[changed]})
        self.assertNotEqual(first_state["rows"][0]["candidate_snapshot_sha256"],changed_state["rows"][0]["candidate_snapshot_sha256"])

    def test_queue_rejects_authority_leak(self) -> None:
        row=self.candidate();row["authority"]["method"]=True
        generator={"policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[row]}
        with self.assertRaisesRegex(ValueError,"authority"):
            build_pre_f0_queue(generator)

    def test_queue_rejects_missing_primary_provenance(self) -> None:
        row=self.candidate();row["primary_refs"]=[]
        generator={"policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[row]}
        with self.assertRaisesRegex(ValueError,"incomplete"):
            build_pre_f0_queue(generator)

    def test_queue_rejects_missing_post_f0_reduction_obligation(self) -> None:
        row=self.candidate();row["post_f0_requirement"]=""
        generator={"policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[row]}
        with self.assertRaisesRegex(ValueError,"exact-reduction"):
            build_pre_f0_queue(generator)

    def test_empty_queue_remains_zero_authority(self) -> None:
        state=build_pre_f0_queue({"policy":{},"pre_f0_candidates":[]})
        self.assertEqual(state["status"],"PRE_F0_QUEUE_EMPTY")
        self.assertEqual(state["summary"]["queued"],0)
        self.assertFalse(state["scientific_authority"])

    def test_zero_candidate_generator_carries_forward_exact_unresolved_support_debt(self) -> None:
        previous=build_pre_f0_queue({"run_id":"old-run","status":"GENERATED_PRE_F0_EVIDENCE_ACQUISITION","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[self.candidate()]})
        row=previous["rows"][0]
        support={
            "run_id":"old-run","status":"PROBLEM_FALSIFIER_PREFLIGHT_COMPLETE","scientific_authority":False,
            "authority":{"canonical_generator":False,"canonical_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
            "summary":{"queued":1,"support_qualified":0,"hold_support_unavailable":1,"falsifier_executed":0},
            "rows":[{"candidate_id":row["candidate_id"],"candidate_identity_version":row["candidate_identity_version"],"candidate_snapshot_sha256":row["candidate_snapshot_sha256"],"disposition":"HOLD_SUPPORT_UNAVAILABLE"}],
        }
        current={"run_id":"new-zero-run","status":"GENERATED_ZERO_CANDIDATES","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[]}
        state=carry_forward_unresolved_support_debt(current,previous,support)
        self.assertEqual(state["status"],"PRE_F0_QUEUE_CARRIED_FORWARD_SUPPORT_DEBT")
        self.assertEqual(state["source_generator_run_id"],"old-run")
        self.assertEqual(state["current_generator_run_id"],"new-zero-run")
        self.assertEqual(state["summary"]["carried_forward_support_debt"],1)
        self.assertEqual(state["summary"]["current_generator_pre_f0_candidates"],0)
        self.assertEqual(state["rows"],[row])
        self.assertFalse(state["scientific_authority"])
        self.assertTrue(state["policy"]["carried_forward_rows_are_not_current_generator_output"])

    def test_support_debt_carry_forward_fails_closed_on_snapshot_mismatch(self) -> None:
        previous=build_pre_f0_queue({"run_id":"old-run","status":"GENERATED_PRE_F0_EVIDENCE_ACQUISITION","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[self.candidate()]})
        row=previous["rows"][0]
        support={
            "run_id":"old-run","status":"PROBLEM_FALSIFIER_PREFLIGHT_COMPLETE","scientific_authority":False,
            "authority":{"canonical_generator":False,"canonical_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
            "summary":{"queued":1,"support_qualified":0,"hold_support_unavailable":1,"falsifier_executed":0},
            "rows":[{"candidate_id":row["candidate_id"],"candidate_identity_version":row["candidate_identity_version"],"candidate_snapshot_sha256":"0"*64,"disposition":"HOLD_SUPPORT_UNAVAILABLE"}],
        }
        current={"run_id":"new-zero-run","status":"GENERATED_ZERO_CANDIDATES","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[]}
        state=carry_forward_unresolved_support_debt(current,previous,support)
        self.assertEqual(state["status"],"PRE_F0_QUEUE_EMPTY")
        self.assertEqual(state["summary"]["queued"],0)

    def test_new_pre_f0_candidates_replace_older_support_debt(self) -> None:
        previous=build_pre_f0_queue({"run_id":"old-run","status":"GENERATED_PRE_F0_EVIDENCE_ACQUISITION","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[self.candidate()]})
        current_candidate=copy.deepcopy(self.candidate());current_candidate["candidate_id"]="PORT-002";current_candidate["title"]="A new current candidate"
        current={"run_id":"new-run","status":"GENERATED_PRE_F0_EVIDENCE_ACQUISITION","policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[current_candidate]}
        state=carry_forward_unresolved_support_debt(current,previous,{})
        self.assertEqual(state["status"],"PRE_F0_QUEUE_READY")
        self.assertEqual(state["source_generator_run_id"],"new-run")
        self.assertEqual([row["candidate_id"] for row in state["rows"]],["PORT-002"])


if __name__ == "__main__":
    unittest.main()
