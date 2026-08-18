from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_memory_skill_coverage_scope_principle_readjudication import (
    CANDIDATE_ID,
    SEARCH_PRIMITIVE,
    SOURCE_A,
    SOURCE_A_LIMITATION_SHA256,
    SOURCE_A_MONOTONICITY_SHA256,
    SOURCE_B,
    SOURCE_B_TIF_SHA256,
    build_readjudication,
)
from .paper_first_search_portfolio_design_adjudication import _principle_readjudication_rows


class MemorySkillCoverageScopePrincipleReadjudicationTest(unittest.TestCase):
    def test_scope_mismatch_is_certified_from_primary_evidence_not_ai_vote(self) -> None:
        payload = build_readjudication()
        self.assertEqual(payload["candidate_id"], CANDIDATE_ID)
        self.assertEqual(payload["search_primitive"], SEARCH_PRIMITIVE)
        self.assertTrue(payload["principle_dead_end_certified"])
        self.assertFalse(payload["experiment_run_for_this_readjudication"])
        self.assertFalse(payload["source_ai_review_has_scientific_authority"])
        self.assertFalse(payload["broader_skill_harm_or_memory_nonmonotonicity_falsified"])
        counter = payload["principle_diagnosis"]["counter_explanation"]
        self.assertEqual(counter["type"], "SAME_INFORMATION_REDUCTION")
        self.assertTrue(counter["same_information_reduction_verified"])
        self.assertTrue(counter["positive_support"])
        self.assertTrue(payload["principle_diagnosis"]["audit"]["passed"])
        refs = set(counter["evidence_refs"])
        self.assertIn(SOURCE_A, refs)
        self.assertIn(SOURCE_B, refs)
        self.assertIn(f"primary-evidence:{SOURCE_A}#sha256={SOURCE_A_MONOTONICITY_SHA256}", refs)
        self.assertIn(f"primary-evidence:{SOURCE_A}#sha256={SOURCE_A_LIMITATION_SHA256}", refs)
        self.assertIn(f"primary-evidence:{SOURCE_B}#sha256={SOURCE_B_TIF_SHA256}", refs)
        self.assertIn("coverage monotonicity", payload["scientific_interpretation"]["safe_claim"])

    def test_persistent_memory_blocks_pair_scope_without_blacklisting_source_evidence(self) -> None:
        payload = build_readjudication()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "memory-skill-coverage-scope-principle-readjudication.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rows = _principle_readjudication_rows([path])
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["source_candidate_id"], CANDIDATE_ID)
        self.assertEqual(row["search_primitive"], SEARCH_PRIMITIVE)
        self.assertEqual(row["current_source_refs"], sorted([SOURCE_A, SOURCE_B]))
        self.assertTrue(row["dead_end_certified"])
        self.assertEqual(row["memory_class"], "METHOD_FORMULATION_STOP")
        self.assertEqual(row["failure_layer"], "METHOD_FORMULATION")
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertEqual(row["fresh_phenomenon_closure"], {})
        self.assertIn("different scientific quantities", row["strongest_reduction"])
        self.assertIn("Reopen only", row["reopen_only_if"])


if __name__ == "__main__":
    unittest.main()
