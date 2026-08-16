from __future__ import annotations

import unittest

from .asset_first_stri_p0_transition import (
    CANDIDATE_ID,
    P0A_EXPERIMENT_ID,
    P0A_GO,
    P0A_STOP,
    P0B_EXPERIMENT_ID,
    P0B_PASS,
    P0B_STOP,
    P0C_EXPERIMENT_ID,
    compile_transition,
)

RAW = "a" * 64


def p0a(decision: str, *, protocol: bool = True, scientific: bool = True) -> dict:
    return {
        "experiment_id": P0A_EXPERIMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "decision": decision,
        "protocol_valid_for_scientific_update": protocol,
        "scientific_result_available": scientific,
        "raw_sha256": RAW,
        "scientific_authority": False,
    }


def p0b(decision: str, *, raw: str = RAW, scientific: bool = True) -> dict:
    return {
        "experiment_id": P0B_EXPERIMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "decision": decision,
        "scientific_result_available": scientific,
        "input_validation": {"actual_raw_sha256": raw},
        "new_model_calls": 0,
        "new_gpu_hours": 0,
        "scientific_authority": False,
    }


def p0c(decision: str, *, raw: str = RAW, scientific: bool = True, protocol: bool = True) -> dict:
    return {
        "experiment_id": P0C_EXPERIMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "decision": decision,
        "scientific_result_available": scientific,
        "protocol_valid_for_scientific_update": protocol,
        "p0a_raw_sha256": raw,
        "scientific_authority": False,
    }


class STRIP0TransitionTest(unittest.TestCase):
    def assert_zero_authority(self, state: dict) -> None:
        self.assertFalse(state["scientific_authority"])
        self.assertFalse(state["execution_authorized"])
        self.assertTrue(all(value is False for value in state["authority"].values()))

    def test_missing_p0a_waits(self) -> None:
        state = compile_transition(p0a=None)
        self.assertEqual(state["status"], "WAIT_P0A_RESULT")
        self.assertEqual(state["allowed_next_actions"], [])
        self.assert_zero_authority(state)

    def test_p0a_go_opens_only_governed_p0b_and_optional_p0c(self) -> None:
        state = compile_transition(p0a=p0a(P0A_GO))
        self.assertEqual(state["status"], "P0A_GO_P0B_READY_FOR_SEPARATE_GOVERNED_EXECUTION")
        self.assertIn("RUN_FROZEN_P0B_ZERO_NEW_MODEL_CALLS", state["allowed_next_actions"])
        self.assertIn("OPTIONAL_RUN_FROZEN_P0C_SECONDARY", state["allowed_next_actions"])
        self.assertEqual(state["claim_state"]["C4_realized_task_propagation"], "SUPPORTED_REALIZED_TASK_DISTRIBUTION_ONLY_NOT_END_OF_EVOLUTION")
        self.assertEqual(state["claim_state"]["C3_sqc_method_claim"], "LOCKED_UNTIL_FULL_PRIMARY_GATES")
        self.assert_zero_authority(state)

    def test_p0a_stop_disables_p0b_p0c_primary_rescue_and_full(self) -> None:
        state = compile_transition(p0a=p0a(P0A_STOP), p0c=p0c("STRONG_ONE_STEP_SOLVER_CONSEQUENCE"))
        self.assertEqual(state["status"], "STOP_DYNAMIC_PROPAGATION_ON_PREREGISTERED_BACKBONE")
        self.assertEqual(state["p0b_state"], "DISABLED_P0A_STOP")
        self.assertEqual(state["full_experiment_state"], "DISABLED_P0A_STOP")
        self.assertEqual(state["p0c_annotation"], "STRONG_ONE_STEP_SOLVER_CONSEQUENCE")
        self.assertEqual(state["allowed_next_actions"], [])
        self.assert_zero_authority(state)

    def test_p0a_qualification_failure_is_no_belief_update(self) -> None:
        state = compile_transition(p0a=p0a("INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED", protocol=False, scientific=False))
        self.assertEqual(state["status"], "HOLD_P0A_INVALID_OR_BUDGET_NO_BELIEF_UPDATE")
        self.assertEqual(state["claim_state"]["C4_realized_task_propagation"], "LOCKED_PENDING_P0A")
        self.assertEqual(state["allowed_next_actions"], [])
        self.assert_zero_authority(state)

    def test_one_witness_inconclusive_forbids_adaptive_rescue(self) -> None:
        state = compile_transition(p0a=p0a("INCONCLUSIVE_ONE_OF_TWO_WITNESSES_ONLY"))
        self.assertEqual(state["status"], "HOLD_P0A_INCONCLUSIVE_NO_ADAPTIVE_EXTRA_GENERATION")
        self.assertEqual(state["allowed_next_actions"], [])
        self.assertTrue(state["policy"]["p0a_inconclusive_forbids_adaptive_extra_generation_threshold_change_or_second_backbone"])

    def test_p0b_pass_does_not_auto_authorize_full(self) -> None:
        state = compile_transition(p0a=p0a(P0A_GO), p0b=p0b(P0B_PASS))
        self.assertEqual(state["status"], "P0A_P0B_PASS_FULL_REMAINS_GOVERNANCE_LOCKED")
        self.assertEqual(state["p0b_state"], "LOCAL_FEASIBILITY_SUPPORTED")
        self.assertEqual(state["full_experiment_state"], "BLUEPRINT_ELIGIBLE_BUT_NOT_AUTHORIZED")
        self.assertIn("REQUEST_GOVERNED_FULL_EXPERIMENT_AUTHORITY", state["allowed_next_actions"])
        self.assert_zero_authority(state)

    def test_p0b_stop_cannot_be_rescued_by_strong_p0c(self) -> None:
        state = compile_transition(
            p0a=p0a(P0A_GO),
            p0b=p0b(P0B_STOP),
            p0c=p0c("STRONG_ONE_STEP_SOLVER_CONSEQUENCE"),
        )
        self.assertEqual(state["status"], "STOP_CURRENT_SQC_REALIZATION_P0B_FEASIBILITY_FAILED")
        self.assertEqual(state["full_experiment_state"], "DISABLED_P0B_STOP")
        self.assertEqual(state["p0c_annotation"], "STRONG_ONE_STEP_SOLVER_CONSEQUENCE")
        self.assertEqual(state["allowed_next_actions"], [])
        self.assert_zero_authority(state)

    def test_p0b_raw_sha_mismatch_blocks_progression(self) -> None:
        state = compile_transition(p0a=p0a(P0A_GO), p0b=p0b(P0B_PASS, raw="b" * 64))
        self.assertEqual(state["status"], "HOLD_P0B_INVALID_NO_BELIEF_UPDATE")
        self.assertIn("p0b:p0b-raw-sha-not-bound-to-p0a", state["errors"])
        self.assertEqual(state["full_experiment_state"], "LOCKED")
        self.assert_zero_authority(state)

    def test_invalid_p0c_is_secondary_only(self) -> None:
        state = compile_transition(
            p0a=p0a(P0A_GO),
            p0b=p0b(P0B_PASS),
            p0c=p0c("INVALID_P0C_REPARSE_QUALIFICATION_FAILED", scientific=False, protocol=False, raw=""),
        )
        self.assertEqual(state["status"], "P0A_P0B_PASS_FULL_REMAINS_GOVERNANCE_LOCKED")
        self.assertEqual(state["p0c_annotation"], "INVALID_SECONDARY_NO_BELIEF_UPDATE")
        self.assertEqual(state["full_experiment_state"], "BLUEPRINT_ELIGIBLE_BUT_NOT_AUTHORIZED")
        self.assert_zero_authority(state)


if __name__ == "__main__":
    unittest.main()
