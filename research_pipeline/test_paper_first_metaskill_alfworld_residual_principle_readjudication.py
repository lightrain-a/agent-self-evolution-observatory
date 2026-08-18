from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_metaskill_alfworld_residual_principle_readjudication import (
    APPENDIX_COMPONENT_ABLATION_SHA256,
    SOURCE_FULLTEXT_SHA256,
    SOURCE_REF,
    TARGET_EVIDENCE_SHA256,
    build_readjudication,
)
from .paper_first_problem_search_portfolio import _fresh_phenomenon_closed_keys
from .paper_first_search_portfolio_design_adjudication import _principle_readjudication_rows


class MetaSkillAlfworldResidualPrincipleReadjudicationTest(unittest.TestCase):
    def test_source_internal_component_ablation_certifies_only_exact_p4_residual(self) -> None:
        payload = build_readjudication()
        self.assertTrue(payload["principle_dead_end_certified"])
        self.assertEqual(payload["search_primitive"], "UNEXPLAINED_BOUNDARY")
        counter = payload["principle_diagnosis"]["counter_explanation"]
        self.assertEqual(counter["type"], "COUNTER_MECHANISM_SUPPORTED")
        self.assertTrue(counter["counter_prediction_observed"])
        self.assertTrue(counter["positive_support"])
        self.assertTrue(payload["principle_diagnosis"]["audit"]["passed"])
        self.assertIn(f"primary-fulltext:{SOURCE_REF}#sha256={SOURCE_FULLTEXT_SHA256}", counter["evidence_refs"])
        self.assertIn(f"primary-fulltext-evidence:{SOURCE_REF}#sha256={APPENDIX_COMPONENT_ABLATION_SHA256}", counter["evidence_refs"])
        closure = payload["fresh_phenomenon_closure"]
        self.assertEqual(closure["source_ref"], SOURCE_REF)
        self.assertEqual(closure["closed_evidence_sha256"], [TARGET_EVIDENCE_SHA256])
        self.assertFalse(closure["scientific_authority"])
        self.assertFalse(payload["broader_two_timescale_meta_skill_value_falsified"])

    def test_persistent_memory_projection_closes_target_not_source(self) -> None:
        payload = build_readjudication()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "metaskill-residual-principle-readjudication.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rows = _principle_readjudication_rows([path])
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertTrue(row["search_closure_certified"])
        self.assertFalse(row["dead_end_certified"])
        self.assertEqual(row["memory_class"], "METHOD_REALIZATION_STOP")
        self.assertEqual(row["failure_layer"], "method_realization")
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertEqual(row["fresh_phenomenon_closure"]["source_ref"], SOURCE_REF)
        memory = {"blocked_objects": rows}
        closed = _fresh_phenomenon_closed_keys(memory)
        self.assertIn((SOURCE_REF, TARGET_EVIDENCE_SHA256), closed)
        self.assertNotIn((SOURCE_REF, "0" * 64), closed)
        self.assertEqual({sha for ref, sha in closed if ref == SOURCE_REF}, {TARGET_EVIDENCE_SHA256})


if __name__ == "__main__":
    unittest.main()
