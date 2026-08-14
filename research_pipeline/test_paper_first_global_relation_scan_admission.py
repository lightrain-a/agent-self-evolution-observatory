from __future__ import annotations

import copy
import unittest

from .paper_first_global_relation_scan_admission import build_global_relation_scan_admission


class GlobalRelationScanAdmissionTest(unittest.TestCase):
    def states(self):
        primary={"status":"READY","summary":{"source_retrieval_complete":True,"source_coverage_exhausted":True,"carrier_probe_complete":True}}
        generator={"status":"SKIPPED_SOURCE_COVERAGE_SATURATED","summary":{"generated":0},"saturation_memory":{"portable_review_receipts":[{"run_id":"r1","source_refs":["arXiv:1","arXiv:2"],"scientific_authority":False},{"run_id":"r2","source_refs":["arXiv:2","arXiv:3"],"scientific_authority":False}]}}
        # Last scan covers only the first receipt universe.
        from .paper_first_relation_coverage import relation_universe_digest
        relation={"last_completed_scan":{"run_id":"r1","relation_universe_digest":relation_universe_digest([generator["saturation_memory"]["portable_review_receipts"][0]]),"relation_coverage":{"reviewed_receipt_sources":2,"possible_source_pairs":1,"coobserved_source_pairs":1,"pair_coverage_fraction":1.0},"scientific_authority":False},"summary":{"relation_universe_digest":"unused"}}
        delta={"status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE","policy":{"scientific_authority":False},"summary":{"new_reviewed_sources":1,"new_empirical_sources":1,"new_assumption_sources":0,"new_failure_sources":1,"new_boundary_sources":1,"cache_missing_sources":0,"model_scan_authorized":False,"focused_generator_reopen_authorized":False},"pair_slots":{},"interpretation":{},"scientific_authority":False}
        return primary,generator,relation,delta

    def test_all_deterministic_preconditions_only_make_manual_scan_eligible(self) -> None:
        primary,generator,relation,delta=self.states()
        state=build_global_relation_scan_admission(primary_state=primary,generator_state=generator,relation_state=relation,delta_state=delta)
        self.assertEqual(state["status"],"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN")
        self.assertTrue(state["summary"]["manual_scan_eligible"])
        self.assertFalse(state["summary"]["automatic_model_scan_authorized"])
        self.assertFalse(state["policy"]["automatic_model_scan_authority"])
        self.assertTrue(state["policy"]["manual_execution_requires_explicit_operator_flag"])
        self.assertFalse(state["scientific_authority"])
        self.assertEqual(state["failed_checks"],[])

    def test_open_live_coverage_blocks_manual_scan(self) -> None:
        primary,generator,relation,delta=self.states();primary=copy.deepcopy(primary);primary["summary"]["source_coverage_exhausted"]=False
        state=build_global_relation_scan_admission(primary_state=primary,generator_state=generator,relation_state=relation,delta_state=delta)
        self.assertEqual(state["status"],"HOLD_MANUAL_RELATION_SCAN")
        self.assertIn("live-source-coverage-exhausted",state["failed_checks"])

    def test_no_new_typed_evidence_blocks_manual_scan(self) -> None:
        primary,generator,relation,delta=self.states();delta=copy.deepcopy(delta)
        for key in ("new_empirical_sources","new_assumption_sources","new_failure_sources","new_boundary_sources"):delta["summary"][key]=0
        state=build_global_relation_scan_admission(primary_state=primary,generator_state=generator,relation_state=relation,delta_state=delta)
        self.assertIn("new-typed-evidence-delta-nonzero",state["failed_checks"])
        self.assertFalse(state["summary"]["manual_scan_eligible"])

    def test_incomplete_delta_cache_blocks_manual_scan(self) -> None:
        primary,generator,relation,delta=self.states();delta=copy.deepcopy(delta);delta["summary"]["cache_missing_sources"]=1
        state=build_global_relation_scan_admission(primary_state=primary,generator_state=generator,relation_state=relation,delta_state=delta)
        self.assertIn("relation-delta-cache-complete",state["failed_checks"])

    def test_nonterminal_generator_blocks_relation_scan_even_if_relation_is_stale(self) -> None:
        primary,generator,relation,delta=self.states();generator=copy.deepcopy(generator);generator["status"]="GENERATED_ZERO_CANDIDATES"
        state=build_global_relation_scan_admission(primary_state=primary,generator_state=generator,relation_state=relation,delta_state=delta)
        self.assertIn("canonical-generator-terminal-zero-call",state["failed_checks"])


if __name__=="__main__":
    unittest.main()
