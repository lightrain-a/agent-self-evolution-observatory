from __future__ import annotations

import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "generated" / "relational-constraint-capacity-construct-v2-20260830.json"
PORT_PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"
EXPECTED_SHA256 = "48a86fa4bb83cdb9308a1cd6a005cf8ea34033f8649cd579c15fbe3e8347317f"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RelationalConstraintCapacityConstructV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.qualification = self.artifact["construct_qualification_v2"]

    def test_is_content_addressed_pre_f0_and_construct_passes(self) -> None:
        self.assertEqual(sha256_file(ARTIFACT), EXPECTED_SHA256)
        self.assertEqual(
            self.artifact["object_id"], "RELATIONAL-CONSTRAINT-CAPACITY-20260830"
        )
        self.assertIsNone(self.artifact["canonical_candidate_id"])
        self.assertEqual(
            self.artifact["status"],
            "PRE_F0_HOLD_ASSET_AND_CONSTRUCT_QUALIFICATION",
        )
        self.assertEqual(self.qualification["verdict"], "PASS")
        self.assertEqual(self.qualification["scientific_outcomes_observed"], 0)

    def test_relation_types_are_balanced_at_every_nested_dose(self) -> None:
        contract = self.qualification[
            "relation_type_balanced_nested_permutations"
        ]
        self.assertEqual(contract["relation_count_levels"], [1, 2, 3, 4, 5])
        self.assertEqual(contract["permutation_count"], 10)
        self.assertTrue(contract["nested_prefix_check"])
        self.assertTrue(contract["balance_audit"]["pass"])
        for dose in contract["balance_audit"]["by_relation_count"].values():
            self.assertEqual(dose["family_max_minus_min"], 0)
            self.assertEqual(set(dose["direction_pair_abs_differences"].values()), {0})
            self.assertTrue(dose["pass"])

        for permutation in contract["permutations"]:
            relation_ids = [
                relation["relation_slot_id"] for relation in permutation["relations"]
            ]
            self.assertEqual(len(relation_ids), 5)
            self.assertEqual(len(set(relation_ids)), 5)
            for count in range(1, 6):
                self.assertEqual(len(set(relation_ids[:count])), count)

    def test_relation_count_and_token_length_are_crossed_not_collinear(self) -> None:
        length = self.qualification["length_disentanglement"]
        self.assertEqual(length["target_clip_tokens_including_special"], [52, 68])
        self.assertEqual(length["encoder_max_length"], 77)
        self.assertEqual(length["headroom_tokens"], 9)
        factorial = length["factorial_audit"]
        self.assertTrue(factorial["complete_factorial"])
        self.assertTrue(factorial["equal_replication"])
        self.assertEqual(
            factorial["pearson_relation_count_vs_target_tokens"], 0.0
        )
        self.assertTrue(factorial["pass"])

        rows = length["design_cells"]
        self.assertEqual(len(rows), 100)
        cells = Counter(
            (
                row["relation_count"],
                row["target_clip_tokens_including_special"],
            )
            for row in rows
        )
        self.assertEqual(set(cells.values()), {10})
        by_semantic_cell = {}
        for row in rows:
            key = (row["permutation_id"], row["relation_count"])
            by_semantic_cell.setdefault(key, []).append(row)
        self.assertEqual(set(map(len, by_semantic_cell.values())), {2})
        for pair in by_semantic_cell.values():
            self.assertEqual(pair[0]["relation_slot_ids"], pair[1]["relation_slot_ids"])
            self.assertNotEqual(
                pair[0]["target_clip_tokens_including_special"],
                pair[1]["target_clip_tokens_including_special"],
            )

    def test_endpoint_hierarchy_and_joint_mixed_effects_are_frozen(self) -> None:
        endpoints = self.qualification["endpoint_freeze"]
        self.assertEqual(endpoints["primary"]["name"], "relation_level_iRecall")
        self.assertEqual(endpoints["primary"]["record"], "satisfied in {0,1}")
        self.assertEqual(endpoints["secondary"]["name"], "exact_all_success")
        self.assertTrue(endpoints["hierarchy_change_after_outcomes_forbidden"])
        self.assertIn("easy iRecall", endpoints["diagnostic_only"])

        prereg = self.qualification["analysis_preregistration"]
        primary = prereg["primary_model"]
        secondary = prereg["secondary_model"]
        self.assertEqual(primary["family"], "binomial logistic mixed-effects model")
        self.assertIn(
            "relation_count_c * clip_token_count_c", primary["formula"]
        )
        self.assertIn("(1 + relation_count_c | base_scene_id)", primary["formula"])
        self.assertIn("(1 | base_scene_id:relation_triplet_id)", primary["formula"])
        self.assertEqual(secondary["outcome"], "exact_all_success")
        self.assertIn(
            "relation_count_c * clip_token_count_c", secondary["formula"]
        )
        self.assertIn(
            "remain in the same fitted model",
            primary["simultaneous_effect_requirement"],
        )

    def test_unofficial_checkpoint_is_smoke_only_and_cannot_enter_p1(self) -> None:
        policy = self.artifact["unofficial_checkpoint_policy"]
        self.assertEqual(policy["allowed_scope"], "NON_SCIENTIFIC_EXECUTION_SMOKE")
        self.assertEqual(policy["case_count_min"], 3)
        self.assertEqual(policy["case_count_max"], 10)
        self.assertFalse(policy["scientific_evidence_eligible"])
        self.assertTrue(policy["p1_projection_forbidden"])
        self.assertFalse(policy["may_qualify_official_reproduction"])

        progression = self.artifact["dual_key_progression"]
        self.assertEqual(progression["construct_qualification_v2"], "PASS")
        self.assertEqual(progression["non_scientific_execution_smoke"], "NOT_RUN")
        self.assertEqual(
            progression["proposal_gate"], "CLOSED_REQUIRES_BOTH_PASS"
        )
        self.assertTrue(progression["proposal_is_not_authority"])
        self.assertFalse(any(self.artifact["authority"].values()))
        self.assertFalse(self.artifact["scientific_authority"])
        self.assertFalse(self.artifact["execution_authority"])

    def test_port010_is_unchanged_in_source_and_snapshot(self) -> None:
        plan = json.loads(PORT_PLAN.read_text(encoding="utf-8"))
        rows = [
            row
            for row in plan.get("entries") or []
            if row.get("candidate_id") == "PORT-010"
            and row.get("title")
            == "Complex-description boundary in end-to-end 3D world construction"
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        snapshot = self.artifact["relation_to_port010"]
        self.assertEqual(row["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual(row["evidence_review"]["verdict"], "BLOCK_BAKE_IN")
        self.assertEqual(snapshot["status"], row["status"])
        self.assertEqual(snapshot["evidence_review"], "BLOCK_BAKE_IN")
        self.assertEqual(snapshot["remaining_reopen_components"], ["per_case_outcomes"])
        for key in (
            "offline_replay_tier_authorized",
            "provider_authority",
            "gpu_authority",
            "scientific_execution_authority",
        ):
            self.assertFalse(snapshot[key])
        self.assertFalse(snapshot["changed_by_this_object"])


if __name__ == "__main__":
    unittest.main()
