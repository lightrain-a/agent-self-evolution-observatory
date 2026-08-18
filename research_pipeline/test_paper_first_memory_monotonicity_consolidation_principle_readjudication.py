from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_memory_monotonicity_consolidation_principle_readjudication import (
    CANDIDATE_ID,
    SEARCH_PRIMITIVE,
    SOURCE_A,
    SOURCE_B,
    build_readjudication,
)
from .paper_first_search_portfolio_design_adjudication import _principle_readjudication_rows
from .principle_adjudication import audit_dead_end_counter_explanation


class MemoryMonotonicityConsolidationPrincipleReadjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_readjudication()

    def test_primary_only_counter_explanation_certifies_scoped_dead_end(self) -> None:
        state = self.state
        self.assertEqual(state["candidate_id"], CANDIDATE_ID)
        self.assertEqual(state["search_primitive"], SEARCH_PRIMITIVE)
        self.assertTrue(state["principle_dead_end_certified"])
        self.assertFalse(state["experiment_run_for_this_readjudication"])
        self.assertFalse(state["source_ai_review_has_scientific_authority"])
        self.assertFalse(state["broader_memory_nonmonotonicity_falsified"])
        counter = state["principle_diagnosis"]["counter_explanation"]
        self.assertEqual(counter["type"], "SAME_INFORMATION_REDUCTION")
        self.assertTrue(counter["same_information_reduction_verified"])
        self.assertTrue(counter["positive_support"])
        self.assertEqual(audit_dead_end_counter_explanation(counter)["blockers"], [])
        self.assertIn(SOURCE_A, counter["evidence_refs"])
        self.assertIn(SOURCE_B, counter["evidence_refs"])
        self.assertIn("conflict-aware selective forgetting", counter["opposite_principle"])
        self.assertIn("retention/compression quantity", counter["reopen_condition"])

    def test_compiler_places_scope_only_in_principle_dead_end_memory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "memory-monotonicity-consolidation-principle-readjudication-test.json"
            path.write_text(json.dumps(self.state, ensure_ascii=False), encoding="utf-8")
            rows = _principle_readjudication_rows([path])
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["source_candidate_id"], CANDIDATE_ID)
        self.assertEqual(row["search_primitive"], SEARCH_PRIMITIVE)
        self.assertEqual(row["current_source_refs"], sorted([SOURCE_A, SOURCE_B]))
        self.assertTrue(row["search_closure_certified"])
        self.assertFalse(row["dead_end_certified"])
        self.assertEqual(row["memory_class"], "METHOD_REALIZATION_STOP")
        self.assertEqual(row["failure_layer"], "method_realization")
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertFalse(row["scientific_authority"])
        self.assertIn("retention/compression quantity", row["reopen_only_if"])


if __name__ == "__main__":
    unittest.main()
