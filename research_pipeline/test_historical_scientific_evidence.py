from __future__ import annotations

import unittest

from .failure_asset_library import build_failure_asset_library
from .historical_scientific_evidence import (
    EXPECTED_DIAGNOSIS_SHA256,
    EXPECTED_F0_SHA256,
    build_historical_scientific_evidence_registry,
)
from .paper_first_post_c2_adjudication import build_post_c2_adjudication
from .scientific_meta_trace import build_scientific_meta_trace


class HistoricalScientificEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = build_historical_scientific_evidence_registry()
        self.record = self.registry["records"][0]

    def test_scienceworld_frozen_hold_and_provenance_are_preserved(self) -> None:
        self.assertEqual(self.record["original_decision"], "SYMMETRIC_F0_HOLD")
        self.assertTrue(self.record["original_decision_preserved"])
        self.assertEqual(self.record["evidence_timing"], "post-hoc")
        self.assertEqual(self.record["evidence_class"], "method-level-negative")
        self.assertEqual(self.record["diagnosis"], "post-hoc-omitted-condition")
        self.assertEqual(self.record["provenance"]["f0"]["sha256"], EXPECTED_F0_SHA256)
        self.assertEqual(self.record["provenance"]["posthoc_diagnosis"]["sha256"], EXPECTED_DIAGNOSIS_SHA256)

    def test_posthoc_scope_evidence_has_no_principle_or_execution_authority(self) -> None:
        self.assertFalse(self.record["active_principle_belief_update_allowed"])
        self.assertFalse(self.record["principle_falsified"])
        self.assertFalse(self.record["retrospective_principle_certificate_allowed"])
        self.assertFalse(self.record["execution_authorized"])
        self.assertFalse(self.record["scale_up_authorized"])
        self.assertTrue(self.registry["policy"]["posthoc_evidence_cannot_be_relabelled_preregistered"])
        self.assertTrue(self.registry["policy"]["method_level_negative_does_not_auto_falsify_principle"])

    def test_failure_library_retrieves_scienceworld_as_institutional_memory(self) -> None:
        library = build_failure_asset_library({"nodes": []}, historical_evidence=self.registry)
        self.assertEqual(library["summary"]["assets"], 1)
        self.assertEqual(library["summary"]["historical_posthoc_assets"], 1)
        asset = library["assets"][0]
        self.assertEqual(asset["signature"], "method-realization:post-hoc-omitted-condition")
        self.assertEqual(asset["memory_scope"], "institutional-research-memory")
        self.assertEqual(asset["original_decision"], "SYMMETRIC_F0_HOLD")
        self.assertFalse(asset["scientific_authority"]["principle_falsified"])
        self.assertFalse(asset["scientific_authority"]["execution_authorized"])

    def test_meta_trace_records_boundary_without_mutating_active_principle(self) -> None:
        cert = {"passed": True, "principle_id": "p1", "contract": {"mechanism": "m", "predictions": [{"id": "P"}]}}
        pre = {"cards": [{"idea_id": "a", "principle_certificate_prerequisite": cert}]}
        principle = {"adjudications": []}
        iteration = {"nodes": [{"idea_id": "a", "diagnosis": "true-negative", "repair_children": []}]}
        meta = build_scientific_meta_trace(pre, principle, iteration, historical_evidence=self.registry)
        self.assertEqual(meta["principles"][0]["belief_state"], "unresolved")
        self.assertEqual(meta["summary"]["historical_boundary_evidence"], 1)
        self.assertEqual(meta["summary"]["historical_active_principle_belief_updates"], 0)
        self.assertEqual(meta["summary"]["historical_execution_authorized"], 0)
        boundary = meta["historical_boundary_evidence"][0]
        self.assertEqual(boundary["original_decision"], "SYMMETRIC_F0_HOLD")
        self.assertFalse(boundary["active_principle_belief_update_allowed"])
        self.assertFalse(boundary["execution_authorized"])

    def test_closed_c2_paper_is_not_reopened(self) -> None:
        post_c2 = build_post_c2_adjudication()
        relationship = self.record["paper_relationship"]
        self.assertEqual(post_c2["decision"], "STOP_CURRENT_CONTROLLED_MEDIATOR_PAPER_MECHANISM")
        self.assertFalse(relationship["can_rescue_closed_formulation"])
        self.assertFalse(relationship["can_reopen_closed_method"])
        self.assertFalse(relationship["can_authorize_new_paper_problem"])
        self.assertFalse(post_c2["authority"]["full_experiment_authorized"])


if __name__ == "__main__":
    unittest.main()
