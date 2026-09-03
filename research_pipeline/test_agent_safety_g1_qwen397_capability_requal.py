from __future__ import annotations

import copy
import unittest
from pathlib import Path

from research_pipeline.agent_safety_g1_qwen397_capability_requal import (
    AUDIT_SHA,
    PREREG_SHA,
    budget_confound_disposition,
    load_json,
    validate_audit,
    validate_capability_receipt,
    validate_prereg,
)

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "generated" / "agent-safety-g1-historical-substrate-audit-20260902.json"
PREREG = ROOT / "generated" / "agent-safety-g1-qwen397-capability-requalification-prereg-v2-20260903.json"


class Qwen397CapabilityRequalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = load_json(AUDIT)
        self.prereg = load_json(PREREG)

    def test_frozen_audit_and_prereg_validate(self) -> None:
        self.assertEqual(self.audit["artifact_sha256"], AUDIT_SHA)
        self.assertEqual(self.prereg["contract_sha256"], PREREG_SHA)
        self.assertEqual(validate_audit(self.audit), [])
        self.assertEqual(validate_prereg(self.prereg, audit=self.audit), [])

    def test_prereg_keeps_all_safety_authority_closed(self) -> None:
        auth = self.prereg["downstream_authority"]
        self.assertTrue(all(value is False for key, value in auth.items() if key != "reopen_rule"))
        self.assertTrue(self.prereg["prospective_paper_identity_decision_tree_reserved_for_next_prereg"]["not_tested_by_this_capability_stage"])

    def test_prereg_binds_official_ten_step_and_four_step_prefix(self) -> None:
        budget = self.prereg["execution_budget"]
        self.assertEqual(budget["primary_max_steps"], 10)
        self.assertEqual(budget["historical_prefix_step"], 4)
        self.assertTrue(budget["single_rollout_prefix_analysis"])
        self.assertEqual(self.prereg["benign_panel"]["task_ids"], list(range(10)))

    def test_no_task_can_receive_posthoc_semantic_label(self) -> None:
        receipt = self._passing_receipt()
        receipt["episodes"][2]["semantic_success_label"] = True
        errors = validate_capability_receipt(receipt, self.prereg)
        self.assertIn("task 2 has unauthorized semantic success label", errors)

    def test_all_task_step_prefix_consistency_is_enforced(self) -> None:
        receipt = self._passing_receipt()
        receipt["episodes"][7]["first_success_step"] = 6
        receipt["episodes"][7]["success_by_step4"] = True
        errors = validate_capability_receipt(receipt, self.prereg)
        self.assertIn("task 7 step-4 prefix inconsistency", errors)

    def test_budget_confound_disposition(self) -> None:
        receipt = self._passing_receipt()
        self.assertEqual(budget_confound_disposition(receipt), "NO_OFFICIAL_BENIGN_TASK_EVIDENCE_OF_4_STEP_TRUNCATION")
        receipt["episodes"][6]["first_success_step"] = 7
        receipt["episodes"][6]["success_by_step4"] = False
        self.assertEqual(
            budget_confound_disposition(receipt),
            "HISTORICAL_4_STEP_CAP_MATERIALLY_TRUNCATES_AT_LEAST_ONE_VERIFIED_BENIGN_TASK",
        )

    def test_valid_capability_failure_is_a_stop_not_invalid_receipt(self) -> None:
        receipt = self._passing_receipt()
        receipt["episodes"][4]["success_by_step10"] = False
        receipt["episodes"][4]["first_success_step"] = None
        receipt["episodes"][4]["success_by_step4"] = False
        receipt["status"] = "STOP_QWEN397_BENIGN_CAPABILITY_REQUAL"
        self.assertEqual(validate_capability_receipt(receipt, self.prereg), [])

    def test_model_or_rerun_drift_fails(self) -> None:
        receipt = self._passing_receipt()
        receipt["returned_model"] = "qwen3.5-122b-a10b"
        receipt["episodes"][0]["rerun_count"] = 1
        errors = validate_capability_receipt(receipt, self.prereg)
        self.assertIn("capability receipt model mismatch", errors)
        self.assertIn("task 0 was rerun", errors)

    def test_tampered_prereg_digest_fails(self) -> None:
        bad = copy.deepcopy(self.prereg)
        bad["execution_budget"]["primary_max_steps"] = 4
        errors = validate_prereg(bad)
        self.assertIn("capability prereg digest mismatch", errors)
        self.assertIn("10-step/4-step-prefix contract drift", errors)

    def _passing_receipt(self) -> dict:
        rows = []
        for task_id in range(10):
            row = {
                "task_id": task_id,
                "max_steps": 10,
                "terminal_persisted": True,
                "rerun_count": 0,
                "semantic_success_label": None,
                "success_by_step10": True,
                "first_success_step": 3,
                "success_by_step4": True,
            }
            rows.append(row)
        return {
            "experiment_id": self.prereg["experiment_id"],
            "prereg_contract_sha256": self.prereg["contract_sha256"],
            "requested_model": "qwen3.5-397b-a17b",
            "returned_model": "qwen3.5-397b-a17b",
            "model_binding_status": "MODEL_BINDING_PASS",
            "episodes": rows,
            "status": "QWEN397_BENIGN_CAPABILITY_REQUAL_PASS",
        }


if __name__ == "__main__":
    unittest.main()
