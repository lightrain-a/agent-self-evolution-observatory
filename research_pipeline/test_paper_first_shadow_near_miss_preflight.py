from __future__ import annotations

import copy
import unittest

from .paper_first_shadow_near_miss_preflight import (
    build_shadow_near_miss_preflight,
    compile_shadow_dead_end_rows,
    validate_shadow_near_miss_preflight,
)


class ShadowNearMissPreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_shadow_near_miss_preflight()

    def test_r2_near_misses_have_distinct_hold_and_stop_dispositions(self) -> None:
        self.assertEqual(validate_shadow_near_miss_preflight(self.state), [])
        rows={row["source_candidate_id"]:row for row in self.state["receipts"]}
        self.assertEqual(rows["SHADOW-P03-C01"]["disposition"],"HOLD_SUPPORT_UNAVAILABLE")
        self.assertEqual(rows["SHADOW-P09-C01"]["disposition"],"STOP_CURRENT_PRIMARY_COLLISION")
        self.assertEqual(self.state["summary"]["support_holds"],1)
        self.assertEqual(self.state["summary"]["current_primary_stops"],1)

    def test_preflight_never_authorizes_live_or_experiment_state(self) -> None:
        self.assertFalse(self.state["scientific_authority"])
        self.assertTrue(self.state["policy"]["shadow_search_control_only"])
        self.assertTrue(self.state["policy"]["cannot_mutate_canonical_generator_or_queue"])
        for row in self.state["receipts"]:
            self.assertFalse(row["scientific_authority"])
            for key in ("automatic_problem_gate_authority","automatic_method_authority","automatic_experiment_authority","automatic_p0_authority","automatic_gpu_authority"):
                self.assertFalse(row[key])

    def test_compiler_preserves_reopen_conditions_and_primary_refs(self) -> None:
        rows={row["source_candidate_id"]:row for row in compile_shadow_dead_end_rows(self.state)}
        self.assertEqual(rows["SHADOW-P03-C01"]["basin"],"near-miss-support-hold")
        self.assertEqual(rows["SHADOW-P09-C01"]["basin"],"near-miss-current-primary-collision")
        self.assertEqual(rows["SHADOW-P03-C01"]["current_source_refs"],["arXiv:2608.11888"])
        self.assertEqual(rows["SHADOW-P09-C01"]["current_source_refs"],["arXiv:2605.13716"])
        self.assertIn("released",rows["SHADOW-P03-C01"]["reopen_only_if"].lower())
        self.assertIn("same-information",rows["SHADOW-P09-C01"]["reopen_only_if"].lower())

    def test_missing_reopen_condition_fails_closed(self) -> None:
        broken=copy.deepcopy(self.state)
        broken["receipts"][0]["reopen_only_if"]=""
        self.assertTrue(any("incomplete" in error for error in validate_shadow_near_miss_preflight(broken)))


if __name__ == "__main__":
    unittest.main()
