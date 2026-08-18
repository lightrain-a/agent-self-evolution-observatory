from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_problem_search_portfolio import _fresh_phenomenon_closed_keys
from .paper_first_search_portfolio_design_adjudication import _principle_readjudication_rows
from .paper_first_skillcoach_distractor_boundary_principle_readjudication import (
    DEGRADATION_EVIDENCE_SHA256,
    NONCOLLAPSE_EVIDENCE_SHA256,
    SOURCE_REF,
    build_readjudication,
)


class SkillCoachDistractorBoundaryPrincipleReadjudicationTest(unittest.TestCase):
    def test_boundary_is_scoped_counter_mechanism_not_source_blacklist(self) -> None:
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
        self.assertEqual(set(closure["closed_evidence_sha256"]), {DEGRADATION_EVIDENCE_SHA256, NONCOLLAPSE_EVIDENCE_SHA256})
        self.assertFalse(closure["scientific_authority"])
        self.assertFalse(payload["skillcoach_training_or_process_supervision_falsified"])

    def test_persistent_memory_closes_only_two_boundary_items(self) -> None:
        payload = build_readjudication()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "skillcoach-boundary-principle-readjudication.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rows = _principle_readjudication_rows([path])
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertTrue(row["dead_end_certified"])
        self.assertEqual(row["memory_class"], "METHOD_FORMULATION_STOP")
        self.assertEqual(row["failure_layer"], "METHOD_FORMULATION")
        self.assertFalse(row["broader_core_principle_falsified"])
        closed = _fresh_phenomenon_closed_keys({"blocked_objects": rows})
        self.assertEqual(
            {sha for ref, sha in closed if ref == SOURCE_REF},
            {DEGRADATION_EVIDENCE_SHA256, NONCOLLAPSE_EVIDENCE_SHA256},
        )
        self.assertNotIn((SOURCE_REF, "2ee2b898434ba010bc34a43297de53ced0ab7c1ae1139855c432080674a6b351"), closed)


if __name__ == "__main__":
    unittest.main()
