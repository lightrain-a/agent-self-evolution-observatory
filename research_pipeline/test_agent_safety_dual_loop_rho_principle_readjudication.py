from __future__ import annotations

import json
import unittest
from pathlib import Path

from .config import PROJECT_ROOT
from .principle_adjudication import audit_dead_end_counter_explanation
from .paper_first_search_portfolio_design_adjudication import _principle_readjudication_rows

READJUDICATION = PROJECT_ROOT / "generated" / "agent-safety-dual-loop-rho-treatment-identity-principle-readjudication-20260818.json"


class AgentSafetyDualLoopRhoPrincipleReadjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(READJUDICATION.read_text(encoding="utf-8"))
        cls.counter = cls.payload["principle_diagnosis"]["counter_explanation"]

    def test_counter_explanation_is_principle_valid(self) -> None:
        audit = audit_dead_end_counter_explanation(self.counter)
        self.assertTrue(audit["passed"], audit["blockers"])
        self.assertEqual(audit["type"], "IMPOSSIBILITY_OR_INVARIANCE")

    def test_dead_end_is_scoped_and_not_experiment_authorized(self) -> None:
        self.assertTrue(self.payload["principle_dead_end_certified"])
        self.assertFalse(self.payload["experiment_alone_authorizes_dead_end"])
        self.assertFalse(self.payload["broader_multi_loop_interference_falsified"])
        self.assertIn("rho-critical", self.payload["dead_end_scope"])

    def test_deepseek_review_is_bound_and_no_fallback(self) -> None:
        review = self.payload["independent_review"]
        self.assertIn("deepseek", review["reviewer_model"])
        self.assertEqual(review["verdict"], "PRINCIPLE_DEAD_END_CERTIFIED")
        self.assertFalse(review["transport_fallback_used"])
        self.assertEqual(review["provider_calls_executed"], 1)

    def test_compiler_emits_persistent_principle_dead_end(self) -> None:
        rows = _principle_readjudication_rows([READJUDICATION])
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertTrue(row["dead_end_certified"])
        self.assertEqual(row["memory_class"], "PRINCIPLE_DEAD_END")
        self.assertEqual(row["search_primitive"], "COMPOSITION_INTERACTION")
        self.assertIn("admits an explicit intervention", row["reopen_only_if"])


if __name__ == "__main__":
    unittest.main()
