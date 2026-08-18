from __future__ import annotations

import unittest

from .pace_bench_mechanism_redesign_principle_readjudication import build_readjudication, validate_readjudication
from .paper_first_search_portfolio_design_adjudication import _principle_readjudication_rows


class PaceBenchMechanismRedesignPrincipleReadjudicationTest(unittest.TestCase):
    def test_old_child_is_invalid_operationalization_not_scientific_negative(self) -> None:
        state = build_readjudication()
        self.assertEqual([], validate_readjudication(state))
        child = state["old_rank_reversal_child"]
        self.assertEqual("ARCHIVED_INVALID_OPERATIONALIZATION", child["status"])
        self.assertEqual("PROTOCOL_STOP", child["stop_class"])
        self.assertEqual("REALIZATION_STOP", child["secondary_failure_class"])
        self.assertFalse(child["principle_dead_end_certified"])

    def test_current_residual_is_scoped_same_information_principle_stop(self) -> None:
        state = build_readjudication()
        self.assertEqual("PRINCIPLE_STOP", state["stop_class"])
        self.assertTrue(state["principle_dead_end_certified"])
        self.assertFalse(state["benchmark_level_dead_end_certified"])
        self.assertEqual("SAME_INFORMATION_REDUCTION_VERIFIED", state["exact_reduction"]["status"])
        self.assertFalse(state["scientific_interpretation"]["revised_f0_authorized"])
        self.assertFalse(state["scientific_interpretation"]["provider_formulation_review_required"])

    def test_closure_compiles_into_durable_principle_memory(self) -> None:
        rows = [
            row
            for row in _principle_readjudication_rows()
            if row.get("source_candidate_id") == "PA-06-PACE-MECHANISM-REDESIGN-IDENTIFIABILITY"
        ]
        self.assertEqual(1, len(rows))
        self.assertTrue(rows[0]["dead_end_certified"])
        self.assertEqual("CORE_PRINCIPLE_STOP", rows[0]["memory_class"])
        self.assertEqual("core_principle", rows[0]["failure_layer"])
        self.assertTrue(rows[0]["principle_update_allowed"])
        self.assertFalse(rows[0]["broader_core_principle_falsified"])
        self.assertIn("generic feedback-guided program synthesis/repair", rows[0]["strongest_reduction"])
        self.assertIn("same known repair surface", rows[0]["reopen_only_if"])


if __name__ == "__main__":
    unittest.main()
