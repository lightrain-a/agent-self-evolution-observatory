from __future__ import annotations

import unittest

from research_pipeline.e2_r17_bridge_v4r2_execution_plan import (
    SCREEN,
    VALIDATION,
    actor_units,
    canonical_sha256,
    full_plan_payload,
    heldout_for_stream,
    search_units,
    stage_budget,
    stage_heldout,
    stage_stream_ids,
    state_units,
    update_tasks,
    validate_plan,
)


class BridgeV4R2ExecutionPlanTest(unittest.TestCase):
    def test_frozen_stage_partition_and_task_geometry(self) -> None:
        self.assertEqual(len(stage_stream_ids(SCREEN)), 6)
        self.assertEqual(len(stage_stream_ids(VALIDATION)), 6)
        self.assertFalse(set(stage_stream_ids(SCREEN)) & set(stage_stream_ids(VALIDATION)))
        self.assertEqual(len(stage_heldout(SCREEN)), 12)
        self.assertEqual(len(stage_heldout(VALIDATION)), 12)
        self.assertFalse(set(stage_heldout(SCREEN)) & set(stage_heldout(VALIDATION)))
        for stage in (SCREEN, VALIDATION):
            for stream in stage_stream_ids(stage):
                self.assertEqual(len(update_tasks(stream)), 8)
                self.assertEqual(len(heldout_for_stream(stage, stream)), 2)

    def test_search_is_exactly_six_streams_times_eight_tasks_times_k8(self) -> None:
        for stage in (SCREEN, VALIDATION):
            units = search_units(stage)
            self.assertEqual(len(units), 384)
            self.assertEqual(len({u.unit_id for u in units}), 384)
            self.assertTrue(all(u.max_provider_calls == 10 for u in units))

    def test_state_generation_cardinality_and_provider_roles(self) -> None:
        screen = state_units(SCREEN)
        validation = state_units(VALIDATION)
        self.assertEqual(len(screen), 36)
        self.assertEqual(sum(u.provider_required for u in screen), 12)
        self.assertEqual(sum(not u.provider_required for u in screen), 24)
        self.assertEqual(len(validation), 42)
        self.assertEqual(sum(u.provider_required for u in validation), 18)
        self.assertEqual(sum(not u.provider_required for u in validation), 24)
        self.assertTrue(all(u.max_provider_calls == 11 for u in screen if u.provider_required))
        self.assertTrue(all(u.max_provider_calls == 0 for u in screen if not u.provider_required))

    def test_actor_schedule_matches_protocol_and_q3_replication(self) -> None:
        screen = actor_units(SCREEN)
        validation = actor_units(VALIDATION)
        self.assertEqual(len(screen), 72)
        self.assertTrue(all(u.actor_replicate == 1 for u in screen))
        self.assertTrue(all(u.exact_k == 1 for u in screen))
        self.assertEqual(len(validation), 120)
        self.assertTrue(all(u.exact_k == 1 for u in validation))
        rep2 = [u for u in validation if u.actor_replicate == 2]
        self.assertEqual(len(rep2), 36)
        self.assertEqual({u.arm for u in rep2}, {"FF4_FREE_A", "FF4_FREE_B", "FF4_COMP"})

    def test_structural_provider_budgets_are_prefrozen_and_nonreallocatable(self) -> None:
        screen = stage_budget(SCREEN)
        validation = stage_budget(VALIDATION)
        self.assertEqual(screen["search_hard_max_provider_calls"], 3840)
        self.assertEqual(screen["free_updater_hard_max_provider_calls"], 132)
        self.assertEqual(screen["deterministic_compiler_provider_calls"], 0)
        self.assertEqual(screen["heldout_actor_rep1_hard_max_provider_calls_pre_alias"], 720)
        self.assertEqual(screen["heldout_actor_rep2_hard_max_provider_calls_pre_alias"], 0)
        self.assertEqual(screen["heldout_actor_hard_max_provider_calls_pre_alias"], 720)
        self.assertEqual(screen["stage_hard_max_provider_calls_pre_alias"], 4692)
        self.assertEqual(screen["search_k"], 8)
        self.assertEqual(screen["heldout_k"], 1)
        self.assertEqual(validation["search_hard_max_provider_calls"], 3840)
        self.assertEqual(validation["free_updater_hard_max_provider_calls"], 198)
        self.assertEqual(validation["heldout_actor_rep1_hard_max_provider_calls_pre_alias"], 840)
        self.assertEqual(validation["heldout_actor_rep2_hard_max_provider_calls_pre_alias"], 360)
        self.assertEqual(validation["heldout_actor_hard_max_provider_calls_pre_alias"], 1200)
        self.assertEqual(validation["stage_hard_max_provider_calls_pre_alias"], 5238)
        self.assertTrue(screen["all_call_counts_are_structural_pre_alias_ceilings_not_expected_spend"])
        self.assertTrue(screen["aliasing_can_only_reduce_actor_calls"])
        self.assertFalse(screen["removed_alias_calls_reallocatable"])

    def test_validation_order_is_prefrozen_but_authority_is_zero(self) -> None:
        payload = validate_plan()
        self.assertTrue(payload["stage_rule"]["validation_order_prefrozen_before_screen_outcomes"])
        self.assertFalse(payload["stage_rule"]["validation_provider_io_before_raw_screen_pass"])
        self.assertTrue(payload["stages"][VALIDATION]["search_units"])
        self.assertTrue(all(value is False for value in payload["authority"].values()))
        self.assertFalse(payload["scientific_outcomes_read"])

    def test_plan_is_deterministic_and_content_addressable(self) -> None:
        first = full_plan_payload()
        second = full_plan_payload()
        self.assertEqual(first, second)
        self.assertEqual(canonical_sha256(first), canonical_sha256(second))


if __name__ == "__main__":
    unittest.main()
