from __future__ import annotations

import copy
import unittest

from research_pipeline.paper_first_schedule_conditional_evolution_scout import (
    build_schedule_conditional_evolution_scout,
    validate_schedule_conditional_evolution_scout,
)


class ScheduleConditionalEvolutionScoutTest(unittest.TestCase):
    def test_scout_is_evidence_bound_but_downstream_blocked(self) -> None:
        state = build_schedule_conditional_evolution_scout()
        self.assertEqual([], validate_schedule_conditional_evolution_scout(state))
        self.assertEqual("HOLD_SUBSTRATE_AUDIT", state["status"])
        self.assertEqual("INCUBATION_EVIDENCE_BOUND", state["paper_state"])
        self.assertEqual("arXiv:2606.02461", state["novelty_review"]["nearest_collision"])
        self.assertEqual("REDUCED", state["paperability_axes"]["P"])
        self.assertEqual("PLAUSIBLE", state["paperability_axes"]["B"])
        self.assertTrue(all(value is False for value in state["authority"].values()))
        claims = {row["claim_id"]: row for row in state["claim_ledger"]}
        self.assertEqual("UNSUPPORTED_AWAIT_F0", claims["PA-07-C3"]["status"])

    def test_execution_acquisition_failure_has_no_belief_authority(self) -> None:
        failure = build_schedule_conditional_evolution_scout()["substrate_audit"]["acquisition_failure"]
        self.assertEqual("RUNTIME_ERROR", failure["failure_code"])
        self.assertFalse(failure["belief_authority"])
        self.assertEqual("none", failure["scientific_effect"])
        self.assertEqual(["require_repair"], failure["allowed_effect"])

    def test_validator_rejects_scientific_authority_leak(self) -> None:
        state = build_schedule_conditional_evolution_scout()
        state["authority"]["experiment"] = True
        self.assertIn(
            "scout illegally carries downstream authority",
            validate_schedule_conditional_evolution_scout(state),
        )

    def test_validator_rejects_unsupported_claim_promotion(self) -> None:
        state = build_schedule_conditional_evolution_scout()
        state["claim_ledger"][2]["status"] = "SUPPORTED"
        self.assertIn(
            "unobserved causal effect became supported",
            validate_schedule_conditional_evolution_scout(state),
        )

    def test_validator_rejects_paper_stage_bypass(self) -> None:
        state = copy.deepcopy(build_schedule_conditional_evolution_scout())
        next(row for row in state["paper_progression"] if row["stage"] == "paper")["status"] = "READY"
        self.assertIn(
            "paper progression bypassed substrate hold",
            validate_schedule_conditional_evolution_scout(state),
        )


if __name__ == "__main__":
    unittest.main()
