from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

R37 = Path("generated/d2-failure-memory-provenance-r37-romerl-substrate-audit.json")


class TestFailureMemoryRoMeRLSubstrateAuditR37(unittest.TestCase):
    def setUp(self) -> None:
        self.d = json.loads(R37.read_text(encoding="utf-8"))

    def test_r37_is_substrate_discovery_not_execution_authority(self) -> None:
        self.assertEqual(
            self.d["status"],
            "ROMERL_PUBLIC_SUBSTRATE_FOUND_SOURCE_LEVEL_AUDIT_ONLY_NO_CONFIRMATORY_EXECUTION_AUTHORITY",
        )
        gate = self.d["gate_adjudication"]
        self.assertFalse(gate["gate_pass_now"])
        self.assertIsNone(gate["qualified_substrate_now"])
        self.assertTrue(gate["G1_RELEASE"]["passed_now"])
        self.assertTrue(gate["G2_PROVENANCE_SCHEMA"]["passed_now"])
        self.assertTrue(all(gate[g]["passed_now"] is False for g in [
            "G3_EXACT_INFORMATION", "G4_FRESH_CAPACITY", "G5_SUPPORT_AND_PREREGISTRATION", "G6_AUTHORITY",
        ]))
        self.assertEqual(gate["passed_stages_now"], ["G1_RELEASE", "G2_PROVENANCE_SCHEMA"])
        self.assertEqual(gate["next_blocking_stage"], "G3_EXACT_INFORMATION")
        self.assertTrue(all(v is False for v in self.d["authority"].values()))

    def test_public_release_has_real_provenance_schema_signals_but_write_side_is_missing(self) -> None:
        c = self.d["candidate"]
        signal = c["construct_signal"]
        boundary = c["release_boundary"]
        self.assertTrue(signal["public_memory_metadata_includes_success"])
        self.assertTrue(signal["public_runtime_categorizes_by_metadata_success"])
        self.assertEqual(signal["public_runtime_roles"], ["best_success", "latest_failure", "best_failure", "recovery"])
        self.assertTrue(signal["retrieval_returns_content_and_metadata_as_separate_fields"])
        self.assertTrue(boundary["evaluation_only"])
        self.assertFalse(boundary["memory_construction_released"])
        self.assertFalse(boundary["q_learning_or_reward_propagation_released"])
        self.assertTrue(self.d["gate_adjudication"]["G2_PROVENANCE_SCHEMA"]["passed_now"])
        audit = c["provenance_schema_audit"]
        self.assertEqual(audit["OSInteraction"]["role_vs_success_mismatches"], 0)
        self.assertEqual(audit["DBBench"]["role_vs_success_mismatches"], 0)
        self.assertEqual(audit["OSInteraction"]["missing_pointer_targets"], 0)
        self.assertEqual(audit["DBBench"]["missing_pointer_targets"], 0)

    def test_checkpoint_inventory_is_content_addressed_but_not_miscounted_as_confirmatory_units(self) -> None:
        inv = self.d["candidate"]["public_checkpoint_inventory"]
        self.assertEqual(inv["raw_task_count_total"], 1000)
        self.assertEqual(inv["raw_active_memory_count_total"], 1730)
        self.assertTrue(inv["raw_inventory_is_not_confirmatory_unit_count"])
        self.assertEqual(inv["OSInteraction"]["task_count"], 500)
        self.assertEqual(inv["DBBench"]["task_count"], 500)
        self.assertEqual(len(inv["OSInteraction"]["public_file_sha256"]), 5)
        self.assertEqual(len(inv["DBBench"]["public_file_sha256"]), 5)
        for row in (inv["OSInteraction"], inv["DBBench"]):
            self.assertIn("success", row["metadata_fields_include"])
            for digest in row["public_file_sha256"].values():
                self.assertEqual(len(digest), 64)
                int(digest, 16)
        self.assertFalse(self.d["gate_adjudication"]["G4_FRESH_CAPACITY"]["passed_now"])
        self.assertEqual(self.d["gate_adjudication"]["G4_FRESH_CAPACITY"]["minimum_reference_independent_units"], 32)

    def test_g1_is_pinned_and_payload_hashes_are_verified(self) -> None:
        pin = self.d["candidate"]["content_addressing"]
        self.assertTrue(pin["checkpoint_payload_hashes_published_by_first_party"])
        self.assertTrue(pin["repository_commit_sha_pinned_in_this_audit"])
        self.assertEqual(pin["repository_commit_sha"], "d3311e28abf9328ec5377c640763f79b9df5b9c9")
        self.assertTrue(pin["pinned_checkout_clean"])
        self.assertTrue(pin["all_ten_checkpoint_payload_hashes_verified_against_first_party_manifests"])
        self.assertTrue(self.d["gate_adjudication"]["G1_RELEASE"]["passed_now"])

    def test_r19_and_same_asset_27_remain_closed(self) -> None:
        watch = self.d["candidate_watch_update"]
        self.assertEqual(watch["best_available_immediate_source_level_audit_target"], "RoMeRL")
        self.assertEqual(watch["cleanest_native_construct_candidate_waiting_release"], "Spatial Memory Agent (SMA)")
        self.assertFalse(watch["R19_reopen"])
        self.assertFalse(watch["same_asset_27_promoted_to_confirmatory"])
        claim = self.d["claim_policy"]
        self.assertTrue(all(v is False for v in claim.values()))

    def test_parent_receipts_are_content_addressed(self) -> None:
        for bind in self.d["parent_bindings"].values():
            p = Path(bind["path"])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), bind["sha256"])

    def test_public_receipt_has_no_private_paths(self) -> None:
        text = R37.read_text(encoding="utf-8")
        for needle in ["/data/", "/home/", "wyt@", "192.168.", "source_message_ref", "source_message_sha256"]:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
