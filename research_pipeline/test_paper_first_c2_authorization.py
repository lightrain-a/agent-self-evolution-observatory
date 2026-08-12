from __future__ import annotations

import copy
import unittest

from .paper_first_c2_authorization import (
    EXPECTED_DEEPSEEK_RAW_SHA256,
    EXPECTED_GLM_RAW_SHA256,
    EXPECTED_PROVENANCE_SHA256,
    EXPECTED_STRUCTURAL_SHA256,
    build_c2_authorization,
    evaluate_c2_authorization,
)
from .paper_first_c2_contract import build_c2_contract
from .paper_first_collision_review import build_fresh_collision_review
from .paper_first_stop_triage import build_paper_first_stop_triage


class PaperFirstC2AuthorizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_c2_authorization()

    def _valid_inputs(self):
        contract = build_c2_contract()
        replay = {
            "decision": "ENVIRONMENT_REPLAY_FEASIBILITY_PASS",
            "summary": {"selected_tasks": 20, "failed_units": 0},
        }
        support = {
            "reviewers": {
                "deepseek_v4_pro": {"raw_sha256": EXPECTED_DEEPSEEK_RAW_SHA256},
                "glm_5_2": {"raw_sha256": EXPECTED_GLM_RAW_SHA256},
            },
            "synthesis": {
                "decision": "FREEZE_EXACT_10_UNIT_C2_RULE_PENDING_STRUCTURAL_PRECHECK",
                "valid_units_required": 10,
                "minimum_nonzero_tau_units": 9,
                "minimum_parent_sign_concordant_units": 9,
                "same_memory_three_context_sign_pattern_required": True,
            },
        }
        structural = {
            "decision": "C2_STRUCTURAL_PRECHECK_PASS",
            "valid_units": 10,
            "required_valid_units": 10,
            "outcome_opened": False,
            "tau_A_computed": False,
            "units": [{"unit_id": unit_id, "valid": True} for unit_id in contract["strict_units"]],
        }
        provenance = {
            "decision": "PROVENANCE_INCONCLUSIVE",
            "paper_level_scientific_authority": False,
            "formal_method_experiment_authorized": False,
            "deterministic_nonzero_regeneration": {
                "nonzero_units": 11,
                "controlled_effect_sign_matches": 10,
                "controlled_effect_sign_mismatches": 1,
                "gpu_uuid": contract["runtime"]["gpu_uuid"],
                "model_path": contract["runtime"]["model_path"],
            },
        }
        return contract, replay, support, structural, provenance

    def _evaluate(self, *, contract=None, replay=None, support=None, structural=None, provenance=None):
        base_contract, base_replay, base_support, base_structural, base_provenance = self._valid_inputs()
        return evaluate_c2_authorization(
            collision=build_fresh_collision_review(),
            triage=build_paper_first_stop_triage(),
            replay=replay or base_replay,
            support=support or base_support,
            structural=structural or base_structural,
            provenance=provenance or base_provenance,
            contract=contract or base_contract,
            structural_sha256=EXPECTED_STRUCTURAL_SHA256,
            provenance_sha256=EXPECTED_PROVENANCE_SHA256,
        )

    def test_completed_c2_is_terminal_locked_against_rerun(self) -> None:
        self.assertEqual(self.state["decision"], "C2_LOCAL_VALIDATION_TERMINAL_LOCKED")
        self.assertFalse(self.state["local_validation_authorized"])
        self.assertTrue(self.state["historical_machine_authorization_recheck_skipped"])
        self.assertEqual(self.state["terminal_post_c2_decision"], "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM")
        self.assertTrue(self.state["C3_locked"])
        self.assertFalse(self.state["full_experiment_authorized"])
        self.assertFalse(self.state["old_b9_formal_method_reopened"])

    def test_synthetic_nominal_fixture_authorizes_only_historical_c2_scope(self) -> None:
        result = self._evaluate()
        self.assertEqual(result["decision"], "C2_LOCAL_VALIDATION_AUTHORIZED")
        self.assertTrue(result["local_validation_authorized"])
        self.assertTrue(result["C3_locked"])
        self.assertFalse(result["full_experiment_authorized"])

    def test_structural_artifact_failure_locks_c2(self) -> None:
        _, _, _, structural, _ = self._valid_inputs()
        structural = copy.deepcopy(structural)
        structural["valid_units"] = 9
        result = self._evaluate(structural=structural)
        self.assertEqual(result["decision"], "C2_LOCAL_VALIDATION_LOCKED")
        self.assertFalse(result["local_validation_authorized"])

    def test_parent_provenance_must_remain_inconclusive(self) -> None:
        _, _, _, _, provenance = self._valid_inputs()
        provenance = copy.deepcopy(provenance)
        provenance["decision"] = "PROVENANCE_PASS"
        result = self._evaluate(provenance=provenance)
        self.assertEqual(result["decision"], "C2_LOCAL_VALIDATION_LOCKED")
        self.assertFalse(result["old_b9_formal_method_reopened"])

    def test_threshold_relaxation_is_not_authorized(self) -> None:
        contract, _, _, _, _ = self._valid_inputs()
        contract = copy.deepcopy(contract)
        contract["frozen_gate"]["go"]["minimum_nonzero_tau_units"] = 8
        result = self._evaluate(contract=contract)
        self.assertEqual(result["decision"], "C2_LOCAL_VALIDATION_LOCKED")


if __name__ == "__main__":
    unittest.main()
