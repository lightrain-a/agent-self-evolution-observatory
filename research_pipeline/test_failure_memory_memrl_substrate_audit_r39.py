from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

R39 = Path("generated/d2-failure-memory-provenance-r39-memrl-substrate-audit.json")


class TestFailureMemoryMemRLSubstrateAuditR39(unittest.TestCase):
    def setUp(self) -> None:
        self.d = json.loads(R39.read_text(encoding="utf-8"))

    def test_only_g1_to_g4_pass_and_execution_remains_closed(self) -> None:
        g = self.d["gate_adjudication"]
        self.assertTrue(all(g[x] is True for x in ["G1_RELEASE", "G2_PROVENANCE_SCHEMA", "G3_EXACT_INFORMATION", "G4_FRESH_CAPACITY"]))
        self.assertFalse(g["G5_SUPPORT_AND_PREREGISTRATION"])
        self.assertFalse(g["G6_AUTHORITY"])
        self.assertFalse(g["gate_pass_now"])
        self.assertEqual(g["next_blocking_stage"], "G5_SUPPORT_AND_PREREGISTRATION")
        self.assertEqual(g["qualified_for_G5_now"], "MemRL")
        self.assertIsNone(g["qualified_for_confirmatory_execution_now"])
        self.assertTrue(all(v is False for v in self.d["authority"].values()))

    def test_g2_keeps_source_provenance_separate_from_later_q_utility(self) -> None:
        g2 = self.d["G2_provenance_schema"]
        self.assertTrue(g2["passed_now"])
        joined = "\n".join(g2["source_chain"])
        self.assertIn("trajectory success", joined)
        self.assertIn("metadata.success", joined)
        later = "\n".join(g2["post_use_utility_separation"])
        self.assertIn("q_value", later)
        self.assertIn("later target episode success", later)
        self.assertIn("after retrieval is frozen", g2["important_boundary"])

    def test_g3_adapter_is_post_retrieval_and_zero_outcome(self) -> None:
        g3 = self.d["G3_exact_information"]
        self.assertTrue(g3["passed_now"])
        self.assertEqual(g3["adapter_unit_tests"], {"passed": 5, "total": 5})
        self.assertIn("content-only provenance-hidden", g3["minimum_identification_arms"])
        self.assertTrue(any("metadata.success" in x for x in g3["minimum_identification_arms"]))
        self.assertEqual(g3["model_calls"], 0)
        self.assertEqual(g3["environment_actions"], 0)
        self.assertEqual(g3["treatment_outcomes_observed"], 0)

    def test_g4_has_disjoint_future_capacity_above_frozen_reference(self) -> None:
        g4 = self.d["G4_fresh_capacity"]
        self.assertTrue(g4["passed_now"])
        self.assertEqual(g4["frozen_reference_independent_units"], 32)
        self.assertTrue(g4["validation_is_read_only"])
        self.assertEqual(g4["validation_write_operations_found"], 0)
        os = g4["OSInteraction"]
        db = g4["DBBench"]
        self.assertEqual((os["source_train_tasks"], os["future_validation_tasks"]), (350, 150))
        self.assertEqual((db["source_train_tasks"], db["future_validation_tasks"]), (361, 139))
        self.assertEqual(os["train_validation_key_overlap"], 0)
        self.assertEqual(db["train_validation_key_overlap"], 0)
        self.assertEqual(os["train_validation_normalized_instruction_overlap"], 0)
        self.assertEqual(db["train_validation_normalized_instruction_overlap"], 0)
        self.assertGreaterEqual(os["validation_skill_signature_clusters"], 32)
        self.assertGreaterEqual(db["validation_skill_signature_clusters"], 32)
        self.assertTrue(os["cluster_capacity_exceeds_reference"])
        self.assertTrue(db["cluster_capacity_exceeds_reference"])

    def test_g4_does_not_confuse_semantic_transfer_with_source_episode_leakage(self) -> None:
        policy = self.d["G4_fresh_capacity"]["unit_policy"]
        self.assertTrue(policy["raw_task_count_is_not_automatically_independence"])
        self.assertEqual(policy["conservative_dependency_cluster"], "exact sorted skill_list signature within benchmark")
        self.assertIn("shared skill-family dependence", policy["semantic_transfer_overlap_is_not_called_provenance_leakage"])

    def test_memrl_advances_only_to_g5(self) -> None:
        d = self.d["candidate_disposition"]
        self.assertEqual(d["MemRL"], "ADVANCE_TO_G5_SUPPORT_AND_PREREGISTRATION_AUDIT_ONLY")
        self.assertEqual(d["preferred_primary_capacity_surface"], "OSInteraction")
        self.assertEqual(d["secondary_replication_capacity_surface"], "DBBench")
        self.assertEqual(d["RoMeRL_bundled_checkpoint"], "KEEP_STOPPED_AT_G4")
        self.assertEqual(d["R19"], "REMAINS_STOPPED")
        self.assertEqual(d["same_asset_27"], "REMAINS_NON_CONFIRMATORY_INVENTORY")
        self.assertTrue(all(v is False for v in self.d["claim_policy"].values()))

    def test_parent_and_adapter_are_content_addressed(self) -> None:
        for bind in self.d["parent_bindings"].values():
            p = Path(bind["path"])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), bind["sha256"])

    def test_pinned_source_and_data_have_hex_sha256(self) -> None:
        for digest in self.d["candidate"]["pinned_source_sha256"].values():
            self.assertEqual(len(digest), 64)
            int(digest, 16)
        for row in self.d["candidate"]["pinned_data_sha256"].values():
            for digest in row.values():
                self.assertEqual(len(digest), 64)
                int(digest, 16)

    def test_public_receipt_has_no_private_paths(self) -> None:
        text = R39.read_text(encoding="utf-8")
        for needle in ["/tmp/", "/data/", "/home/", "wyt@", "192.168.", "source_message_ref", "source_message_sha256"]:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
