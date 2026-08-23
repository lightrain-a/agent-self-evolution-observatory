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
        self.assertEqual(race["pairwise_matches"], 210)
        self.assertEqual(race["structural_mutation_lineages"], 21)
        self.assertTrue(debate["candidate_identity_lock_required"])
        self.assertTrue(debate["unmapped_candidate_alias_forces_protocol_fail"])
        self.assertTrue(debate["explicit_parent_child_mapping_required_for_material_mutation"])
        self.assertEqual(state["summary"]["active_research_items_after"], 0)
        self.assertEqual(state["summary"]["problem_gate_pass"], 0)
        self.assertEqual(validate_discovery_cycle(state), [])

    def test_identity_lock_cannot_be_silently_removed(self) -> None:
        state = build_discovery_cycle(generated_at="2026-08-23T12:00:00+00:00")
        broken = copy.deepcopy(state)
        broken["debate_contract"]["candidate_identity_lock_required"] = False
        self.assertIn("debate-contract-incomplete", validate_discovery_cycle(broken))


if __name__ == "__main__":
    unittest.main()
