from __future__ import annotations

import copy
import unittest

from .paper_first_global_relation_scan_admission import build_global_relation_scan_admission, public_global_relation_scan_admission_summary


class GlobalRelationScanAdmissionTest(unittest.TestCase):
    def states(self):
        tx="a"*64
        primary={"status":"READY","discovery_transaction_id":tx,"summary":{"source_retrieval_complete":True,"source_coverage_exhausted":True,"carrier_probe_complete":True}}
        generator={"status":"SKIPPED_SOURCE_COVERAGE_SATURATED","discovery_transaction_id":tx,"summary":{"generated":0,"written_to_auto_inbox":0},"saturation_memory":{"portable_review_receipts":[{"run_id":"r1","source_refs":["arXiv:1","arXiv:2"],"scientific_authority":False},{"run_id":"r2","source_refs":["arXiv:2","arXiv:3"],"scientific_authority":False}]}}
        queue={"discovery_transaction_id":tx,"summary":{"submitted":0,"audited":0,"blocked_problem_gate":0,"passed_problem_gate":0,"paper_design_eligible":0,"inbox_errors":0}}
        # Last scan covers only the first receipt universe.
        from .paper_first_relation_coverage import relation_universe_digest
        relation={"last_completed_scan":{"run_id":"r1","relation_universe_digest":relation_universe_digest([generator["saturation_memory"]["portable_review_receipts"][0]]),"relation_coverage":{"reviewed_receipt_sources":2,"possible_source_pairs":1,"coobserved_source_pairs":1,"pair_coverage_fraction":1.0},"scientific_authority":False},"summary":{"relation_universe_digest":"unused"}}
        delta={"status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE","policy":{"scientific_authority":False},"summary":{"new_reviewed_sources":1,"new_empirical_sources":1,"new_assumption_sources":0,"new_failure_sources":1,"new_boundary_sources":1,"cache_missing_sources":0,"model_scan_authorized":False,"focused_generator_reopen_authorized":False},"pair_slots":{},"interpretation":{},"scientific_authority":False}
        return primary,generator,queue,relation,delta

    def build(self, *, primary=None, generator=None, queue=None, relation=None, delta=None):
        p,g,q,r,d=self.states()
        return build_global_relation_scan_admission(
            primary_state=primary or p,
            generator_state=generator or g,
            queue_state=queue or q,
            relation_state=relation or r,
            delta_state=delta or d,
        )

    def test_all_deterministic_preconditions_only_make_manual_scan_eligible(self) -> None:
        state=self.build()
        self.assertEqual(state["status"],"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN")
        self.assertTrue(state["summary"]["manual_scan_eligible"])
        self.assertFalse(state["summary"]["automatic_model_scan_authorized"])
        self.assertFalse(state["policy"]["automatic_model_scan_authority"])
        self.assertTrue(state["policy"]["manual_execution_requires_explicit_operator_flag"])
        self.assertFalse(state["scientific_authority"])
        self.assertEqual(state["failed_checks"],[])

    def test_public_summary_exposes_gate_counts_without_check_details(self) -> None:
        state=self.build();public=public_global_relation_scan_admission_summary(state);encoded=str(public)
        self.assertEqual(public["status"],"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN")
        self.assertEqual((public["summary"]["checks"],public["summary"]["passed"],public["summary"]["failed"]),(15,15,0))
        self.assertTrue(public["summary"]["manual_scan_eligible"])
        self.assertFalse(public["summary"]["automatic_model_scan_authorized"])
        self.assertNotIn("checks",public)
        self.assertNotIn("live-primary-ready",encoded)
        self.assertFalse(public["scientific_authority"])

    def test_open_live_coverage_blocks_manual_scan(self) -> None:
        primary,_,_,_,_=self.states();primary=copy.deepcopy(primary);primary["summary"]["source_coverage_exhausted"]=False
        state=self.build(primary=primary)
        self.assertEqual(state["status"],"HOLD_MANUAL_RELATION_SCAN")
        self.assertIn("live-source-coverage-exhausted",state["failed_checks"])

    def test_no_new_typed_evidence_blocks_manual_scan(self) -> None:
        *_,delta=self.states();delta=copy.deepcopy(delta)
        for key in ("new_empirical_sources","new_assumption_sources","new_failure_sources","new_boundary_sources"):delta["summary"][key]=0
        state=self.build(delta=delta)
        self.assertIn("new-typed-evidence-delta-nonzero",state["failed_checks"])
        self.assertFalse(state["summary"]["manual_scan_eligible"])

    def test_incomplete_delta_cache_blocks_manual_scan(self) -> None:
        *_,delta=self.states();delta=copy.deepcopy(delta);delta["summary"]["cache_missing_sources"]=1
        state=self.build(delta=delta)
        self.assertIn("relation-delta-cache-complete",state["failed_checks"])

    def test_closed_generated_zero_candidates_is_terminal_for_relation_control(self) -> None:
        _,generator,_,_,_=self.states();generator=copy.deepcopy(generator);generator["status"]="GENERATED_ZERO_CANDIDATES"
        state=self.build(generator=generator)
        self.assertTrue(state["summary"]["manual_scan_eligible"])
        self.assertNotIn("canonical-live-discovery-terminal-no-survivor",state["failed_checks"])

    def test_fully_blocked_problem_gate_candidate_is_terminal_for_relation_control(self) -> None:
        _,generator,queue,_,_=self.states();generator=copy.deepcopy(generator);queue=copy.deepcopy(queue)
        generator["status"]="GENERATED_AWAIT_PROBLEM_GATE";generator["summary"].update({"generated":1,"written_to_auto_inbox":1})
        queue["summary"].update({"submitted":1,"audited":1,"blocked_problem_gate":1,"passed_problem_gate":0,"paper_design_eligible":0})
        state=self.build(generator=generator,queue=queue)
        self.assertEqual(state["status"],"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN")
        self.assertTrue(state["summary"]["manual_scan_eligible"])
        self.assertFalse(state["summary"]["automatic_model_scan_authorized"])

    def test_unreviewed_or_surviving_problem_gate_candidate_blocks_relation_scan(self) -> None:
        _,generator,queue,_,_=self.states();generator=copy.deepcopy(generator);queue=copy.deepcopy(queue)
        generator["status"]="GENERATED_AWAIT_PROBLEM_GATE";generator["summary"].update({"generated":1,"written_to_auto_inbox":1})
        queue["summary"].update({"submitted":1,"audited":0,"blocked_problem_gate":0})
        state=self.build(generator=generator,queue=queue)
        self.assertIn("canonical-live-discovery-terminal-no-survivor",state["failed_checks"])
        queue["summary"].update({"audited":1,"blocked_problem_gate":0,"passed_problem_gate":1,"paper_design_eligible":1})
        state=self.build(generator=generator,queue=queue)
        self.assertIn("canonical-live-discovery-terminal-no-survivor",state["failed_checks"])

    def test_transaction_mismatch_blocks_relation_scan(self) -> None:
        primary,_,queue,_,_=self.states();queue=copy.deepcopy(queue);queue["discovery_transaction_id"]="b"*64
        state=self.build(primary=primary,queue=queue)
        self.assertIn("canonical-live-discovery-terminal-no-survivor",state["failed_checks"])


if __name__=="__main__":unittest.main()
