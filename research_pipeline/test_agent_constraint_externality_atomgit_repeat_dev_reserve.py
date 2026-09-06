from __future__ import annotations

import json
import unittest

from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_reserve_build import (
    CONTRACT_OUTPUT,
    ORDER_SALT,
    OUTPUT_BUNDLE,
    QUAL_OUTPUT,
    load_reserve_spec,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_file, sha256_value


class RepeatDevReserveStaticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_OUTPUT.read_text(encoding="utf-8"))
        cls.qual = json.loads(QUAL_OUTPUT.read_text(encoding="utf-8"))
        cls.spec = load_reserve_spec()

    def test_frozen_bundle_and_content_hashes(self) -> None:
        self.assertEqual(self.contract["protected_bundle"]["sha256"], sha256_file(OUTPUT_BUNDLE))
        unsigned = dict(self.contract); claimed = unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))
        unsigned_q = dict(self.qual); claimed_q = unsigned_q.pop("content_sha256")
        self.assertEqual(claimed_q, sha256_value(unsigned_q))
        self.assertEqual(self.qual["protected_bundle_sha256"], sha256_file(OUTPUT_BUNDLE))

    def test_reserve_is_8_plus_8_and_fresh(self) -> None:
        self.assertEqual(self.contract["reserve"]["family_count"], 16)
        self.assertEqual(self.contract["reserve"]["per_category"], 8)
        self.assertEqual(self.contract["reserve"]["needed_per_category"], 3)
        self.assertEqual(self.qual["category_counts"], {"FILE_GMAIL": 8, "TODO_NOTE_FILE": 8})
        fresh = self.contract["freshness"]
        self.assertTrue(fresh["source_case_ids_unique"])
        self.assertTrue(fresh["source_instruction_hashes_unique"])
        self.assertTrue(fresh["source_fixture_hashes_unique"])
        for key in ("case_id_overlap_count", "instruction_hash_overlap_count", "fixture_hash_overlap_count", "target_local_resource_hash_overlap_count"):
            self.assertEqual(fresh[key], 0)

    def test_pre_topology_selection_rule_is_frozen(self) -> None:
        reserve = self.contract["reserve"]
        self.assertEqual(reserve["order_salt"], ORDER_SALT)
        self.assertEqual(reserve["maximum_source_dispatches"], 16)
        self.assertFalse(reserve["retry"])
        self.assertFalse(reserve["replacement_outside_frozen_reserve"])
        self.assertFalse(reserve["challenge_recipe_change_after_first_dispatch"])
        self.assertEqual(reserve["technical_invalidity_after_dispatch"], "HARD_STOP_NO_REPLAY_NO_SKIP")
        self.assertIn("first three", reserve["selection_rule"].lower())
        self.assertIn("target success", reserve["selection_rule"].lower())

    def test_ranked_order_is_complete_unique_and_category_local(self) -> None:
        ranked = self.contract["reserve"]["ranked_source_order_by_category"]
        self.assertEqual(set(ranked), {"FG", "TNF"})
        seen = set()
        for category, rows in ranked.items():
            self.assertEqual(len(rows), 8)
            self.assertEqual([row["rank_sha256"] for row in rows], sorted(row["rank_sha256"] for row in rows))
            for row in rows:
                self.assertNotIn(row["family_id"], seen)
                seen.add(row["family_id"])
                self.assertIn(f"-{category}-", row["family_id"])
        self.assertEqual(len(seen), 16)

    def test_public_oracle_and_topology_static_pass(self) -> None:
        self.assertTrue(self.qual["public_oracle_pass"])
        self.assertTrue(self.qual["matched_topology_pass"])
        self.assertTrue(self.qual["initial_non_target_satisfaction_pass"])
        self.assertEqual(len(self.contract["public_source_oracles"]), 16)
        self.assertTrue(all(row["target_success"] for row in self.contract["public_source_oracles"]))
        self.assertGreaterEqual(self.contract["minimum_public_tool_headroom"], 1)
        for summary in self.contract["family_summaries"]:
            self.assertEqual(summary["shared_resource_exposure"], {"INDEPENDENT": 0, "LOW": 1, "HIGH": 2})
            self.assertTrue(summary["initial_non_target_constraints_satisfied"])

    def test_old_fixed_six_is_not_salvaged(self) -> None:
        self.assertFalse(self.contract["parent_fixed_six_reuse"])
        self.assertFalse(self.contract["parent_fixed_six_completed_failures_carried_forward"])
        self.assertTrue(self.contract["selected_development_panel_after_source"]["permanently_excluded_from_confirmatory"])

    def test_all_execution_authority_remains_closed(self) -> None:
        self.assertTrue(all(value is False for value in self.contract["authority"].values()))
        self.assertTrue(all(value is False for value in self.qual["authority"].values()))
        self.assertEqual(self.contract["provider_requests_created"], 0)
        self.assertEqual(self.contract["scientific_topology_outcomes_observed"], 0)
        self.assertEqual(self.spec["provider_calls_created_by_build"], 0)


if __name__ == "__main__":
    unittest.main()
