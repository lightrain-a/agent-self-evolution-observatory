from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

R38 = Path("generated/d2-failure-memory-provenance-r38-romerl-exact-information-gate.json")


class TestFailureMemoryRoMeRLExactInformationGateR38(unittest.TestCase):
    def setUp(self) -> None:
        self.d = json.loads(R38.read_text(encoding="utf-8"))

    def test_g3_passes_but_global_gate_remains_closed(self) -> None:
        gate = self.d["gate_adjudication"]
        self.assertTrue(gate["G1_RELEASE"])
        self.assertTrue(gate["G2_PROVENANCE_SCHEMA"])
        self.assertTrue(gate["G3_EXACT_INFORMATION"])
        self.assertFalse(gate["G4_FRESH_CAPACITY"])
        self.assertFalse(gate["G5_SUPPORT_AND_PREREGISTRATION"])
        self.assertFalse(gate["G6_AUTHORITY"])
        self.assertFalse(gate["gate_pass_now"])
        self.assertEqual(gate["blocking_stage"], "G4_FRESH_CAPACITY")
        self.assertEqual(gate["passed_stages_now"], ["G1_RELEASE", "G2_PROVENANCE_SCHEMA", "G3_EXACT_INFORMATION"])
        self.assertIsNone(gate["qualified_substrate_now"])
        self.assertTrue(all(v is False for v in self.d["authority"].values()))

    def test_exact_information_adapter_preserves_all_non_provenance_executor_information(self) -> None:
        g3 = self.d["G3_exact_information"]
        self.assertTrue(g3["passed_now"])
        self.assertEqual(g3["treatment_field"], "source_outcome_success")
        self.assertEqual(g3["unit_tests"], {"passed": 6, "total": 6})
        for row in g3["pinned_checkpoint_integration"].values():
            if not isinstance(row, dict) or "rows_checked" not in row:
                continue
            self.assertEqual(row["rows_checked"], 32)
            self.assertTrue(row["actionable_content_identical"])
            self.assertTrue(row["retrieval_order_preserved"])
            self.assertTrue(row["retrieval_cardinality_preserved"])
            self.assertFalse(row["q_or_role_exposed_to_executor"])
            self.assertEqual(len(row["frozen_retrieval_sha256"]), 64)
        self.assertEqual(g3["pinned_checkpoint_integration"]["model_calls"], 0)
        self.assertEqual(g3["pinned_checkpoint_integration"]["environment_actions"], 0)
        self.assertEqual(g3["pinned_checkpoint_integration"]["outcome_measurements"], 0)

    def test_bundled_checkpoint_cannot_supply_32_task_level_unexposed_units(self) -> None:
        g4 = self.d["G4_fresh_capacity"]
        self.assertFalse(g4["passed_now"])
        self.assertEqual(g4["frozen_reference_independent_units"], 32)
        os = g4["source_memory_task_coverage"]["OSInteraction"]
        db = g4["source_memory_task_coverage"]["DBBench"]
        self.assertEqual((os["benchmark_task_universe"], os["unique_task_ids_with_active_source_memory"]), (500, 498))
        self.assertEqual((db["benchmark_task_universe"], db["unique_task_ids_with_active_source_memory"]), (500, 500))
        self.assertLess(os["task_ids_without_active_source_memory_upper_bound"], 32)
        self.assertLess(db["task_ids_without_active_source_memory_upper_bound"], 32)
        self.assertFalse(os["can_supply_32_task_level_unexposed_units"])
        self.assertFalse(db["can_supply_32_task_level_unexposed_units"])
        self.assertFalse(g4["current_bundled_checkpoint_confirmatory_eligible"])

    def test_no_shortcut_relabels_full_checkpoint_or_validation_as_fresh(self) -> None:
        shortcuts = "\n".join(self.d["G4_fresh_capacity"]["forbidden_shortcuts"])
        self.assertIn("500 checkpoint tasks", shortcuts)
        self.assertIn("30% validation set", shortcuts)
        self.assertIn("32-unit reference", shortcuts)
        disp = self.d["candidate_disposition"]
        self.assertEqual(disp["RoMeRL_bundled_checkpoint"], "STOP_AS_FRESH_CONFIRMATORY_SUBSTRATE_AT_G4")
        self.assertEqual(disp["RoMeRL_schema_construct_witness"], "KEEP")
        self.assertEqual(disp["R19"], "REMAINS_STOPPED")
        self.assertEqual(disp["same_asset_27"], "REMAINS_NON_CONFIRMATORY_INVENTORY")

    def test_parent_and_adapter_are_content_addressed(self) -> None:
        for bind in self.d["parent_bindings"].values():
            p = Path(bind["path"])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), bind["sha256"])

    def test_claim_policy_does_not_change_scientific_result(self) -> None:
        self.assertTrue(all(v is False for v in self.d["claim_policy"].values()))
        self.assertEqual(
            self.d["scientific_verdict"],
            "NO_VERDICT_ROMERL_BUNDLED_CHECKPOINT_FAILS_FRESH_CAPACITY_WITHOUT_RELAXING_GATE",
        )

    def test_public_receipt_has_no_private_paths(self) -> None:
        text = R38.read_text(encoding="utf-8")
        for needle in ["/tmp/", "/data/", "/home/", "wyt@", "192.168.", "source_message_ref", "source_message_sha256"]:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
