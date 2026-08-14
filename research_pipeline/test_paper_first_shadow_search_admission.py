from __future__ import annotations

import copy
import unittest

from .paper_first_shadow_search_admission import (
    build_shadow_search_admission,
    public_shadow_search_admission_summary,
    source_set_sha256,
    validate_shadow_search_admission,
)


class ShadowSearchAdmissionTest(unittest.TestCase):
    def states(self):
        refs=["arXiv:2608.00001","arXiv:2608.00002"]
        tx="a"*64
        generated_at="2026-08-14T03:47:25+00:00"
        set_sha=source_set_sha256([{"ref":ref} for ref in refs])
        primary={"status":"READY","generated_at":generated_at,"discovery_transaction_id":tx,"records":[{"ref":ref} for ref in refs],"summary":{"source_retrieval_complete":True,"source_coverage_exhausted":True,"carrier_probe_complete":True}}
        generator={"status":"SKIPPED_SOURCE_COVERAGE_SATURATED","discovery_transaction_id":tx,"summary":{"generated":0,"written_to_auto_inbox":0}}
        queue={"discovery_transaction_id":tx,"summary":{"submitted":0,"audited":0,"inbox_errors":0}}
        shadow={"scientific_authority":False,"policy":{"shadow_only":True},"latest_run_id":"shadow-r5","latest_run":{"run_id":"shadow-r5","status":"SHADOW_TERMINAL_COMPLETE","source_generated_at":generated_at,"source_set_sha256":set_sha,"source_pool_sha256":"b"*64,"scientific_authority":False}}
        return primary,generator,queue,shadow

    def test_source_set_digest_matches_frozen_pool_convention(self):
        records=[{"ref":"arXiv:2"},{"ref":"arXiv:1"}]
        import hashlib
        expected=hashlib.sha256("arXiv:1\narXiv:2".encode()).hexdigest()
        self.assertEqual(source_set_sha256(records),expected)
        self.assertEqual(source_set_sha256([{"ref":"not-arxiv"}]),"")

    def test_same_terminal_source_transaction_is_zero_call_skip(self):
        primary,generator,queue,shadow=self.states()
        state=build_shadow_search_admission(primary_state=primary,generator_state=generator,queue_state=queue,shadow_state=shadow)
        self.assertEqual(validate_shadow_search_admission(state),[])
        self.assertEqual(state["status"],"SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL")
        self.assertTrue(state["summary"]["same_source_transaction"])
        self.assertFalse(state["summary"]["qualification_allowed"])
        self.assertEqual(state["summary"]["automatic_provider_calls_authorized"],0)
        self.assertFalse(state["scientific_authority"])

    def test_new_closed_source_transaction_opens_qualification_only(self):
        primary,generator,queue,shadow=self.states()
        primary=copy.deepcopy(primary);generator=copy.deepcopy(generator);queue=copy.deepcopy(queue)
        primary["generated_at"]="2026-08-15T03:47:25+00:00";primary["records"].append({"ref":"arXiv:2608.00003"})
        tx="c"*64;primary["discovery_transaction_id"]=tx;generator["discovery_transaction_id"]=tx;queue["discovery_transaction_id"]=tx
        state=build_shadow_search_admission(primary_state=primary,generator_state=generator,queue_state=queue,shadow_state=shadow)
        self.assertEqual(validate_shadow_search_admission(state),[])
        self.assertEqual(state["status"],"READY_FOR_SHADOW_QUALIFICATION")
        self.assertTrue(state["summary"]["qualification_allowed"])
        self.assertFalse(state["summary"]["same_source_transaction"])
        self.assertEqual(state["summary"]["automatic_provider_calls_authorized"],0)
        self.assertTrue(state["policy"]["admission_can_only_allow_zero_model_qualification_freeze"])

    def test_open_canonical_transaction_holds_even_with_new_sources(self):
        primary,generator,queue,shadow=self.states();queue=copy.deepcopy(queue);queue["summary"].update({"submitted":1,"audited":0})
        state=build_shadow_search_admission(primary_state=primary,generator_state=generator,queue_state=queue,shadow_state=shadow)
        self.assertEqual(state["status"],"HOLD_CANONICAL_DISCOVERY_TRANSACTION_OPEN")
        self.assertFalse(state["summary"]["canonical_transaction_closed"])
        self.assertFalse(state["summary"]["qualification_allowed"])

    def test_incomplete_prior_shadow_blocks_new_qualification(self):
        primary,generator,queue,shadow=self.states();shadow=copy.deepcopy(shadow);shadow["latest_run"]["status"]="SHADOW_TERMINAL_INCOMPLETE_PROBLEM_FALSIFIER_PREFLIGHT"
        state=build_shadow_search_admission(primary_state=primary,generator_state=generator,queue_state=queue,shadow_state=shadow)
        self.assertEqual(state["status"],"HOLD_PRIOR_SHADOW_RUN_INCOMPLETE")
        self.assertFalse(state["summary"]["qualification_allowed"])

    def test_legacy_terminal_without_source_identity_fails_closed(self):
        primary,generator,queue,shadow=self.states();shadow=copy.deepcopy(shadow);shadow["latest_run"].pop("source_generated_at");shadow["latest_run"].pop("source_set_sha256")
        state=build_shadow_search_admission(primary_state=primary,generator_state=generator,queue_state=queue,shadow_state=shadow)
        self.assertEqual(state["status"],"HOLD_PREVIOUS_SHADOW_SOURCE_IDENTITY_UNAVAILABLE")
        self.assertFalse(state["summary"]["qualification_allowed"])

    def test_partial_source_identity_match_is_conflict_not_reopen(self):
        primary,generator,queue,shadow=self.states();shadow=copy.deepcopy(shadow);shadow["latest_run"]["source_set_sha256"]="d"*64
        state=build_shadow_search_admission(primary_state=primary,generator_state=generator,queue_state=queue,shadow_state=shadow)
        self.assertEqual(state["status"],"HOLD_SHADOW_SOURCE_IDENTITY_CONFLICT")
        self.assertTrue(state["summary"]["source_identity_conflict"])
        self.assertFalse(state["summary"]["qualification_allowed"])

    def test_public_summary_is_bounded_and_zero_authority(self):
        primary,generator,queue,shadow=self.states()
        state=build_shadow_search_admission(primary_state=primary,generator_state=generator,queue_state=queue,shadow_state=shadow)
        public=public_shadow_search_admission_summary(state)
        self.assertEqual(public["status"],"SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL")
        self.assertNotIn("checks",public)
        self.assertNotIn("discovery_transaction_id",str(public))
        self.assertEqual(len(public["source_identity"]["current_source_set_sha256"]),64)
        self.assertFalse(public["scientific_authority"])
        self.assertFalse(public["summary"]["qualification_allowed"])


if __name__=="__main__":
    unittest.main()
