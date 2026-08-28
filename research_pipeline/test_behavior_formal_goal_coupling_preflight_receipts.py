from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str) -> dict:
    return json.loads((ROOT / "generated" / name).read_text(encoding="utf-8"))


class BehaviorFormalGoalCouplingPreflightReceiptsTest(unittest.TestCase):
    def test_third_policy_gate_remains_hold(self) -> None:
        row = load("behavior-formal-goal-coupling-third-policy-qualification-20260828.json")
        self.assertFalse(row["scientific_authority"])
        self.assertFalse(row["execution_authority"])
        self.assertFalse(row["gpu_authority"])
        self.assertEqual(row["status"], "HOLD_NO_THIRD_PREOUTCOME_QUALIFIED_POLICY_FAMILY")
        self.assertEqual(row["decision"]["qualified_third_family_count"], 0)

    def test_contract_v2_adjudication_only_allows_preflight(self) -> None:
        row = load("behavior-formal-goal-coupling-official-policy-training-contracts-v2-adjudication-20260828.json")
        self.assertEqual(row["status"], "CONTRACT_V2_PASS_PREFLIGHT_ONLY_THIRD_FAMILY_HOLD")
        self.assertEqual(row["review_consensus"], "2/2 CONTRACT-PASS-PREFLIGHT-ONLY")
        self.assertFalse(row["execution_authority"])
        self.assertFalse(row["gpu_authority"])
        self.assertFalse(row["policy_training_authorized"])
        self.assertFalse(row["policy_rollouts_authorized"])

    def test_phase0_static_receipt_is_exact_revision_and_zero_model(self) -> None:
        row = load("behavior-formal-goal-coupling-phase0-static-data-preflight-20260828.json")
        self.assertEqual(row["status"], "PHASE0_STATIC_PASS_PHASE1_DATA_ONLY_ALLOWED_THIRD_FAMILY_HOLD")
        self.assertEqual(row["authority_source"]["tag"], "v3.0")
        self.assertEqual(row["authority_source"]["revision"], "4f50b44796641a4d526a19d9aeadc8aa51e2f2c2")
        self.assertEqual(row["metadata_tree"]["episode_parquet_files"], 100)
        self.assertEqual(row["dataset_schema"]["total_tasks"], 100)
        self.assertEqual(row["dataset_schema"]["total_episodes"], 20000)
        self.assertEqual(row["dataset_schema"]["state_shape"], [61])
        self.assertEqual(row["dataset_schema"]["action_shape"], [23])
        self.assertTrue(row["gates"]["pass"])
        self.assertFalse(row["model_load_authorized"])
        self.assertFalse(row["policy_outcomes_read"])

    def test_readiness_v2_keeps_phase2_locked_on_third_family_hold(self) -> None:
        row = load("behavior-formal-goal-coupling-local-replication-readiness-v2-20260828.json")
        self.assertEqual(row["status"], "HOLD_THIRD_FAMILY_PREOUTCOME_QUALIFICATION_PHASE1_READY")
        self.assertTrue(row["preflight"]["phase0"]["pass"])
        self.assertTrue(row["preflight"]["phase1"]["pass"])
        self.assertEqual(row["third_policy_gate"]["qualified_third_family_count"], 0)
        self.assertFalse(row["third_policy_gate"]["three_policy_minimum_may_be_lowered"])
        self.assertFalse(row["model_load_authorized"])
        self.assertFalse(row["forward_authorized"])
        self.assertFalse(row["backward_authorized"])
        self.assertFalse(row["optimizer_update_authorized"])
        self.assertFalse(row["policy_training_authorized"])
        self.assertFalse(row["policy_rollouts_authorized"])
        self.assertFalse(row["policy_outcomes_read"])

    def test_current_third_family_tranche_is_conditionally_closed(self) -> None:
        row = load("behavior-formal-goal-coupling-third-policy-current-tranche-closure-20260828.json")
        self.assertEqual(row["status"], "SEARCH_CLOSED_CURRENT_PUBLIC_TRANCHE_THIRD_FAMILY_HOLD")
        self.assertIn("current indexed/public source tranche", row["closure_scope"])
        self.assertEqual(row["current_family_state"]["qualified_family_count"], 2)
        self.assertEqual(row["current_family_state"]["required_independent_families"], 3)
        self.assertFalse(row["current_family_state"]["third_family_gate_pass"])
        self.assertEqual(row["independent_reviews"]["kimi"]["verdict"], "CONFIRM-CURRENT-TRANCHE-CLOSURE")
        self.assertEqual(row["independent_reviews"]["deepseek"]["verdict"], "CONFIRM-CURRENT-TRANCHE-CLOSURE")
        self.assertTrue(row["reopen_conditions"])
        self.assertFalse(row["scientific_authority"])
        self.assertFalse(row["execution_authority"])
        self.assertFalse(row["gpu_authority"])
        self.assertFalse(row["policy_training_authorized"])
        self.assertFalse(row["policy_rollouts_authorized"])
        self.assertFalse(row["policy_outcomes_read"])
        self.assertFalse(row["port010_reopen_authorized"])

    def test_readiness_v3_is_watch_only_and_keeps_phase2_locked(self) -> None:
        row = load("behavior-formal-goal-coupling-local-replication-readiness-v3-20260828.json")
        self.assertEqual(row["status"], "HOLD_THIRD_FAMILY_CURRENT_PUBLIC_TRANCHE_CLOSED_WATCH_ONLY")
        self.assertTrue(row["preflight"]["phase0"]["pass"])
        self.assertTrue(row["preflight"]["phase1"]["pass"])
        self.assertEqual(row["third_family"]["source_watch_status"], "WATCH_STABLE_NO_THIRD_POLICY_SOURCE_CHANGE")
        self.assertEqual(row["third_family"]["search_closure_status"], "SEARCH_CLOSED_CURRENT_PUBLIC_TRANCHE_THIRD_FAMILY_HOLD")
        self.assertEqual(row["third_family"]["qualified_families"], 2)
        self.assertEqual(row["third_family"]["required_families"], 3)
        self.assertFalse(row["third_family"]["phase2_gate_pass"])
        self.assertFalse(row["model_load_authorized"])
        self.assertFalse(row["forward_authorized"])
        self.assertFalse(row["backward_authorized"])
        self.assertFalse(row["optimizer_update_authorized"])
        self.assertFalse(row["policy_training_authorized"])
        self.assertFalse(row["policy_rollouts_authorized"])
        self.assertFalse(row["policy_outcomes_read"])
        self.assertFalse(row["parent_port010_reopen_authorized"])
        self.assertIn("reopen condition", row["reopen_gate"])

    def test_phase1_data_only_receipt_closes_chunk0_without_outcomes(self) -> None:
        row = load("behavior-formal-goal-coupling-phase1-data-only-preflight-20260828.json")
        phase0 = load("behavior-formal-goal-coupling-phase0-static-data-preflight-20260828.json")
        adjudication = load("behavior-formal-goal-coupling-official-policy-training-contracts-v2-adjudication-20260828.json")
        self.assertEqual(row["status"], "PHASE1_DATA_ONLY_PASS_MODEL_LOAD_LOCKED_THIRD_FAMILY_HOLD")
        self.assertEqual(row["phase0_receipt"]["receipt_sha256"], phase0["receipt_sha256"])
        self.assertEqual(row["training_contract_adjudication"]["adjudication_sha256"], adjudication["adjudication_sha256"])
        self.assertEqual(row["episode_metadata"]["rows"], 200)
        self.assertEqual(row["frame_schema_audit"]["rows_total"], 429928)
        self.assertEqual(row["frame_schema_audit"]["action_list_lengths"], [23])
        self.assertEqual(row["frame_schema_audit"]["state_list_lengths"], [61])
        self.assertTrue(row["frame_schema_audit"]["reward_column_present"])
        self.assertFalse(row["frame_schema_audit"]["reward_values_read"])
        self.assertTrue(row["gates"]["pass"])
        self.assertFalse(row["model_load_authorized"])
        self.assertFalse(row["forward_authorized"])
        self.assertFalse(row["backward_authorized"])
        self.assertFalse(row["optimizer_update_authorized"])
        self.assertFalse(row["policy_outcomes_read"])


if __name__ == "__main__":
    unittest.main()
