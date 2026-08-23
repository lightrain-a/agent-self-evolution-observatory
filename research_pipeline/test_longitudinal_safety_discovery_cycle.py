from __future__ import annotations

import copy
import unittest

from .longitudinal_safety_discovery_cycle import build_discovery_cycle, validate_discovery_cycle


class LongitudinalSafetyDiscoveryCycleTest(unittest.TestCase):
    def test_historical_pool_tournament_and_debate_contract_are_fail_closed(self) -> None:
        state = build_discovery_cycle(generated_at="2026-08-23T12:00:00+00:00")
        audit = state["historical_pool_audit"]
        race = audit["horse_race"]
        debate = state["debate_contract"]
        self.assertEqual((audit["generation_records"], audit["unique_candidate_ids"]), (119, 119))
        self.assertEqual(race["preclosure_eligible_failure_lineages"], 53)
        self.assertEqual(race["eligible_failure_lineages"], 16)
        self.assertEqual(race["pairwise_matches"], 36)
        self.assertEqual(race["structural_mutation_lineages"], 9)
        self.assertTrue(race["reviewed_descendants_supersede_stale_parent_vectors"])
        self.assertTrue(race["terminal_or_absorbed_lineages_cannot_reenter_via_ancestor"])
        self.assertTrue(debate["candidate_identity_lock_required"])
        self.assertTrue(debate["unmapped_candidate_alias_forces_protocol_fail"])
        self.assertTrue(debate["explicit_parent_child_mapping_required_for_material_mutation"])
        self.assertEqual(state["summary"]["active_research_items_after"], 0)
        self.assertEqual(state["summary"]["problem_gate_pass"], 0)
        self.assertEqual(validate_discovery_cycle(state), [])

    def test_descendant_closure_blocks_stale_parent_reentry(self) -> None:
        state = build_discovery_cycle(generated_at="2026-08-23T12:00:00+00:00")
        audit = state["historical_pool_audit"]
        closure = {
            row["candidate_id"]: row
            for row in audit["lineage_closure"]["records"]
        }
        ranked = {
            row["candidate_id"]
            for row in audit["horse_race"]["top_mutation_parents"]
        }

        self.assertEqual(
            closure["typed-correction-skill-grammar-v5"]["status"],
            "SUPERSEDED_BY_REVIEWED_DESCENDANT",
        )
        self.assertEqual(
            closure["typed-correction-skill-grammar-v5"]["replacement_failure_leaves"],
            ["counterfactual-correction-production-grammar"],
        )
        self.assertEqual(
            closure["counterfactual-correction-production-grammar"]["status"],
            "CURRENT_HISTORICAL_LEAF",
        )
        self.assertIn("counterfactual-correction-production-grammar", ranked)
        self.assertNotIn("typed-correction-skill-grammar-v5", ranked)

        self.assertEqual(
            closure["restoration-clause-learning"]["status"],
            "DESCENDANT_TERMINALIZED_OR_ABSORBED",
        )
        self.assertIn(
            "restoration-clause-induction-v5",
            closure["restoration-clause-learning"]["terminal_or_absorbed_descendants"],
        )
        self.assertNotIn("restoration-clause-learning", ranked)

        self.assertEqual(
            closure["rollback-conditioned-update-inverter"]["status"],
            "DESCENDANT_TERMINALIZED_OR_ABSORBED",
        )
        self.assertIn(
            "certified-out-of-span-interaction-inverter-v53",
            closure["rollback-conditioned-update-inverter"]["terminal_or_absorbed_descendants"],
        )
        self.assertNotIn("rollback-conditioned-update-inverter", ranked)

    def test_stale_ranked_parent_is_rejected_by_validation(self) -> None:
        state = build_discovery_cycle(generated_at="2026-08-23T12:00:00+00:00")
        broken = copy.deepcopy(state)
        broken["historical_pool_audit"]["horse_race"]["top_mutation_parents"].append(
            {"candidate_id": "typed-correction-skill-grammar-v5"}
        )
        self.assertIn(
            "stale-mutation-parent:typed-correction-skill-grammar-v5",
            validate_discovery_cycle(broken),
        )

    def test_identity_lock_cannot_be_silently_removed(self) -> None:
        state = build_discovery_cycle(generated_at="2026-08-23T12:00:00+00:00")
        broken = copy.deepcopy(state)
        broken["debate_contract"]["candidate_identity_lock_required"] = False
        self.assertIn("debate-contract-incomplete", validate_discovery_cycle(broken))


if __name__ == "__main__":
    unittest.main()
