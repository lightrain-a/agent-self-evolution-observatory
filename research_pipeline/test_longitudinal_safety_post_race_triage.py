from __future__ import annotations

import copy
import unittest

from .longitudinal_safety_post_race_triage import (
    build_post_race_triage,
    validate_post_race_triage,
)


class LongitudinalSafetyPostRaceTriageTest(unittest.TestCase):
    def test_top_nine_all_fail_closed_after_cross_lineage_reduction(self) -> None:
        state = build_post_race_triage(generated_at="2026-08-24T02:00:00+08:00")
        summary = state["summary"]
        self.assertEqual(summary["ranked_failure_leaves"], 9)
        self.assertEqual(summary["triaged"], 9)
        self.assertEqual(summary["current_post_race_survivors"], 0)
        self.assertEqual(summary["material_child_required"], 3)
        self.assertEqual(summary["deferred_to_existing_object"], 3)
        self.assertEqual(summary["stopped_by_mature_reduction"], 3)
        self.assertEqual(summary["untriaged_fail_closed"], 0)
        self.assertEqual(summary["provider_calls_authorized"], 0)
        self.assertEqual(summary["gpu_authorized"], 0)
        self.assertEqual(validate_post_race_triage(state), [])

    def test_existing_support_hold_is_deferred_not_relabelled_method_fail(self) -> None:
        state = build_post_race_triage(generated_at="2026-08-24T02:00:00+08:00")
        rows = {row["candidate_id"]: row for row in state["rows"]}
        memory = rows["randomized-memory-action-policy"]
        self.assertEqual(memory["disposition"], "DEFER_TO_EXISTING_OBJECT")
        self.assertEqual(memory["canonical_reducers"][0]["idea_id"], "retrieval-interference-auditor")
        self.assertIn(
            "STOP_CURRENT_SUBSTRATE_FRESH_CINTERACTION_SUPPORT_INSUFFICIENT",
            str(memory["canonical_reducers"][0]["current_fact"]),
        )
        self.assertFalse(memory["problem_gate_eligible"])

    def test_operator_reachability_pattern_is_concrete_nonautomatic_reduction(self) -> None:
        state = build_post_race_triage(generated_at="2026-08-24T02:00:00+08:00")
        rows = {row["candidate_id"]: row for row in state["rows"]}
        router = rows["budget-split-contract-router-transpiler"]
        self.assertEqual(router["disposition"], "STOP_MATURE_REDUCTION")
        self.assertEqual(router["mature_reduction_patterns"][0]["key"], "operator-closure-reachability")
        self.assertEqual(router["mature_reduction_patterns"][0]["audit_class"], "VALID_HARD_VETO")
        self.assertFalse(router["mature_reduction_patterns"][0]["automatic_veto"])
        self.assertIn("same transition/action graph", router["reason"])

    def test_material_child_rows_do_not_count_as_survivors(self) -> None:
        state = build_post_race_triage(generated_at="2026-08-24T02:00:00+08:00")
        rows = {row["candidate_id"]: row for row in state["rows"]}
        for candidate_id in (
            "verified-risk-predicate-grammar",
            "version-differential-active-diagnosis",
            "counterfactual-correction-production-grammar",
        ):
            self.assertEqual(rows[candidate_id]["disposition"], "MATERIAL_CHILD_REQUIRED")
            self.assertFalse(rows[candidate_id]["problem_gate_eligible"])
            self.assertFalse(rows[candidate_id]["research_item_eligible"])

    def test_any_manual_promotion_is_rejected(self) -> None:
        state = build_post_race_triage(generated_at="2026-08-24T02:00:00+08:00")
        broken = copy.deepcopy(state)
        broken["rows"][0]["problem_gate_eligible"] = True
        self.assertTrue(
            any(error.startswith("row-promotion:") for error in validate_post_race_triage(broken))
        )


if __name__ == "__main__":
    unittest.main()
