from __future__ import annotations

import json
from pathlib import Path
import unittest

from research_pipeline.e2_r17_m3r4_execution_plan import logical_units, sha256_file


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated/e2-r17-m3r4-execution-draft-contract-20260904.json"
ORDER = ROOT / "generated/e2-r17-m3r4-logical-unit-order-20260904.json"
OLD_IDENTITY = ROOT / "generated/e2-r17-deepseek-v2-repair2-model-identity-adjudication-20260831.json"


class M3R4ExecutionDraftContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.order = json.loads(ORDER.read_text(encoding="utf-8"))

    def test_draft_is_hard_hold_with_zero_scientific_authority(self) -> None:
        self.assertEqual(
            self.contract["status"],
            "HOLD_FRESH_MODEL_IDENTITY_REQUALIFICATION_REQUIRED_ZERO_PROVIDER_PREP_ONLY",
        )
        authority = self.contract["authority"]
        self.assertTrue(authority)
        self.assertTrue(all(value is False for value in authority.values()))
        self.assertFalse(self.contract["fresh_model_identity_gate"]["historical_identity_reusable_for_m3r4"])
        self.assertIsNone(self.contract["fresh_model_identity_gate"]["fresh_identity_artifact"])
        self.assertIsNone(self.contract["fresh_model_identity_gate"]["fresh_identity_sha256"])

    def test_old_identity_itself_demands_requalification(self) -> None:
        old = json.loads(OLD_IDENTITY.read_text(encoding="utf-8"))
        self.assertIn("must be requalified before any later scientific tranche", old["adjudication"])
        self.assertEqual(self.contract["fresh_model_identity_gate"]["historical_identity_sha256"], sha256_file(OLD_IDENTITY))

    def test_order_manifest_is_exactly_bound_and_matches_code(self) -> None:
        self.assertEqual(self.contract["logical_unit_order"]["sha256"], sha256_file(ORDER))
        self.assertEqual(self.order["unit_count"], 72)
        self.assertEqual(
            [row["unit_id"] for row in self.order["logical_units"]],
            [row.unit_id for row in logical_units()],
        )
        self.assertEqual(
            self.contract["logical_unit_order"]["logical_units_sha256"],
            self.order["logical_units_sha256"],
        )

    def test_provider_budget_is_structural_actor_only(self) -> None:
        budget = self.contract["provider_budget"]
        self.assertEqual(budget["logical_units"], 72)
        self.assertEqual(budget["max_provider_calls_per_logical_unit"], 10)
        self.assertEqual(budget["hard_max_provider_calls_structural"], 720)
        self.assertEqual(budget["provider_retry_limit"], 0)
        self.assertFalse(budget["automatic_retry"])
        self.assertFalse(budget["unused_budget_reallocation"])

    def test_state_and_scientific_scope_are_exact(self) -> None:
        self.assertEqual(self.contract["scientific_scope"]["states"], ["ff_r1", "ff_r2"])
        self.assertEqual(self.contract["scientific_scope"]["task_count"], 18)
        self.assertEqual(self.contract["scientific_scope"]["logical_units"], 72)
        self.assertEqual(self.contract["scientific_scope"]["updater_calls"], 0)
        self.assertFalse(self.contract["scientific_scope"]["historical_actor_outcomes_in_gate"])
        self.assertEqual(len(self.contract["states"]), 2)

    def test_inference_assumption_failure_cannot_trigger_rerun(self) -> None:
        q = self.contract["inference_qualification"]
        self.assertTrue(q["within_task_iid_stationarity_required_for_propensity_and_exact_test"])
        self.assertTrue(q["cross_task_conditional_factorization_required_for_binomial_tail"])
        self.assertTrue(q["detected_coupling_blocks_inference"])
        self.assertFalse(q["assumption_failure_automatic_rerun"])

    def test_recovery_v3_is_resource_priority_not_outcome_design_switch(self) -> None:
        r = self.contract["resource_priority"]
        self.assertIn("Recovery V3 scheduled continuation has priority", r["rule"])
        self.assertFalse(r["m2_outcome_may_change_m3r4_design"])

    def test_run_root_and_lease_are_not_created_by_draft_freeze(self) -> None:
        self.assertFalse(Path(self.contract["run_root"]).exists())
        self.assertFalse(Path(self.contract["lineage_lease_path"]).exists())


if __name__ == "__main__":
    unittest.main()
