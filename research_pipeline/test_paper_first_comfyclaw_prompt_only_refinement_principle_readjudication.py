from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_comfyclaw_prompt_only_refinement_principle_readjudication import (
    SOURCE_REF,
    TARGET_EVIDENCE_SHA256,
    build_readjudication,
)
from .paper_first_problem_search_portfolio import _fresh_phenomenon_closed_keys
from .paper_first_search_portfolio_design_adjudication import _principle_readjudication_rows


class ComfyClawPromptOnlyRefinementPrincipleReadjudicationTest(unittest.TestCase):
    def test_action_space_and_feedback_counter_explanation_closes_only_prompt_only_boundary(self) -> None:
        payload = build_readjudication()
        self.assertTrue(payload["principle_dead_end_certified"])
        self.assertEqual(payload["search_primitive"], "UNEXPLAINED_BOUNDARY")
        counter = payload["principle_diagnosis"]["counter_explanation"]
        self.assertEqual(counter["type"], "COUNTER_MECHANISM_SUPPORTED")
        self.assertTrue(counter["counter_prediction_observed"])
        self.assertTrue(counter["positive_support"])
        self.assertTrue(payload["principle_diagnosis"]["audit"]["passed"])
        closure = payload["fresh_phenomenon_closure"]
        self.assertEqual(closure["source_ref"], SOURCE_REF)
        self.assertEqual(closure["closed_evidence_sha256"], [TARGET_EVIDENCE_SHA256])
        self.assertFalse(closure["scientific_authority"])
        self.assertFalse(payload["comfyclaw_skill_evolution_falsified"])

    def test_persistent_memory_keeps_adjacent_comfyclaw_evidence_open(self) -> None:
        payload = build_readjudication()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "comfyclaw-prompt-only-principle-readjudication.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rows = _principle_readjudication_rows([path])
        self.assertEqual(len(rows), 1)
        closed = _fresh_phenomenon_closed_keys({"blocked_objects": rows})
        self.assertEqual({sha for ref, sha in closed if ref == SOURCE_REF}, {TARGET_EVIDENCE_SHA256})
        self.assertNotIn((SOURCE_REF, "265a7f1100492358e7de5ce6d2c7de05738cc79c1db2f4bb296d8969cc2c166c"), closed)


if __name__ == "__main__":
    unittest.main()
