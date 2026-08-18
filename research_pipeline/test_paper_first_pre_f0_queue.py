from __future__ import annotations

import unittest

from .paper_first_pre_f0_queue import build_pre_f0_queue


class PaperFirstPreF0QueueTest(unittest.TestCase):
    def candidate(self) -> dict:
        return {
            "candidate_id": "PORT-001",
            "title": "A surviving empirical boundary",
            "discovery_lane": "UNEXPLAINED_BOUNDARY",
            "source_branch_id": "B-R1",
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
        self.assertTrue(all(value is False for value in state["rows"][0]["authority"].values()))

    def test_queue_rejects_authority_leak(self) -> None:
        row=self.candidate();row["authority"]["method"]=True
        generator={"policy":{"search_portfolio_enabled":True,"exact_reduction_required_before_final_problem_gate":True},"pre_f0_candidates":[row]}
        with self.assertRaisesRegex(ValueError,"authority"):
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


if __name__ == "__main__":
    unittest.main()
