from __future__ import annotations

import unittest
from collections import Counter

from research_pipeline.e2_r17_m3r4_execution_plan import (
    MAX_PROVIDER_CALLS_PER_LOGICAL_UNIT,
    ORDER_SALT,
    REQUIRED_RESOLVED_MODEL,
    STATE_BINDINGS,
    TASK_IDS,
    logical_units,
    order_manifest,
    structural_provider_budget,
    validate_state_bindings,
)


class M3R4ExecutionPlanTest(unittest.TestCase):
    def test_exact_scientific_cardinality(self) -> None:
        rows = logical_units()
        self.assertEqual(len(rows), 72)
        self.assertEqual(len(TASK_IDS), 18)
        self.assertEqual({row.state_id for row in rows}, {"ff_r1", "ff_r2"})
        self.assertEqual({row.actor_replicate for row in rows}, {1, 2})
        self.assertEqual(Counter(row.state_id for row in rows), Counter({"ff_r1": 36, "ff_r2": 36}))
        self.assertEqual(Counter(row.actor_replicate for row in rows), Counter({1: 36, 2: 36}))

    def test_every_task_gets_exact_four_postfreeze_observations(self) -> None:
        rows = logical_units()
        for task_id in TASK_IDS:
            task_rows = [row for row in rows if row.task_id == task_id]
            self.assertEqual(len(task_rows), 4)
            self.assertEqual(
                {(row.state_id, row.actor_replicate) for row in task_rows},
                {("ff_r1", 1), ("ff_r1", 2), ("ff_r2", 1), ("ff_r2", 2)},
            )
            self.assertEqual({row.round_index for row in task_rows}, {0, 1, 2, 3})

    def test_each_round_is_task_complete_and_treatment_balanced(self) -> None:
        rows = logical_units()
        for round_index in range(4):
            rr = [row for row in rows if row.round_index == round_index]
            self.assertEqual(len(rr), 18)
            self.assertEqual({row.task_id for row in rr}, set(TASK_IDS))
            counts = Counter((row.state_id, row.actor_replicate) for row in rr)
            self.assertEqual(sorted(counts.values()), [4, 4, 5, 5])

    def test_order_is_content_addressed_and_outcome_blind(self) -> None:
        a = order_manifest()
        b = order_manifest()
        self.assertEqual(a, b)
        self.assertEqual(a["order_salt"], ORDER_SALT)
        self.assertEqual(a["unit_count"], 72)
        self.assertFalse(a["outcome_conditioned"])
        self.assertEqual(len(a["logical_units_sha256"]), 64)
        # The manifest contains identities/order only, never scores/effects.
        serialized = str(a).lower()
        for forbidden in ("score", "success_rate", "effect", "p_value", "e_real"):
            self.assertNotIn(forbidden, serialized)

    def test_state_bindings_are_exact_existing_content_addressed_artifacts(self) -> None:
        validate_state_bindings()
        self.assertEqual(len(STATE_BINDINGS), 2)
        self.assertEqual(
            {row.skill_sha256 for row in STATE_BINDINGS},
            {
                "596bd30b49935d16f35d51e9eed36e19567332cd8a9104ae50d832f91ffdf04f",
                "fb5454a27faf8182ba1b0d722273c4377d4762815cd1898c3780cc8ff336615e",
            },
        )

    def test_structural_provider_ceiling_is_actor_only(self) -> None:
        budget = structural_provider_budget()
        self.assertEqual(MAX_PROVIDER_CALLS_PER_LOGICAL_UNIT, 10)
        self.assertEqual(budget["logical_units"], 72)
        self.assertEqual(budget["hard_max_provider_calls_structural"], 720)
        self.assertEqual(budget["provider_retry_limit"], 0)
        self.assertFalse(budget["automatic_retry"])
        self.assertFalse(budget["unused_budget_reallocation"])

    def test_model_identity_requirement_does_not_silently_change_target_model(self) -> None:
        self.assertEqual(REQUIRED_RESOLVED_MODEL, "deepseek-v4-pro-ga-260813")


if __name__ == "__main__":
    unittest.main()
