from __future__ import annotations

import unittest

from .paper_first_relation_coverage import relation_universe_digest
from .paper_first_relation_delta_preflight import build_relation_delta_preflight, public_relation_delta_preflight_summary


class RelationDeltaPreflightTest(unittest.TestCase):
    def receipt(self, run_id: str, refs: list[str]) -> dict:
        return {"run_id":run_id,"source_refs":refs,"scientific_authority":False}

    def generator(self, receipts: list[dict]) -> dict:
        return {"saturation_memory":{"portable_review_receipts":receipts}}

    def row(self, ref: str, *, empirical: bool=False, assumption: bool=False, failure: bool=False, boundary: bool=False) -> dict:
        return {
            "ref":ref,"title":ref,"abstract":"evidence","primary_source_verified":True,"lane_keys":[],
            "empirical_facts":[{"text":"fact"}] if empirical else [],
            "typed_evidence":{
                "operational_assumptions":[{"text":"assumption"}] if assumption else [],
                "measured_failures":[{"text":"failure"}] if failure else [],
                "boundary_observations":[{"text":"boundary"}] if boundary else [],
            },
        }

    def relation(self, old_receipts: list[dict], cutoff: str) -> dict:
        return {"last_completed_scan":{"run_id":cutoff,"relation_universe_digest":relation_universe_digest(old_receipts),"scientific_authority":False}}

    def test_delta_counts_typed_opportunities_without_authorizing_lane_or_model(self) -> None:
        old=[self.receipt("20260813T100000Z",["arXiv:1","arXiv:2"])]
        new=self.receipt("20260814T010000Z",["arXiv:2","arXiv:3","arXiv:4"])
        rows=[
            self.row("arXiv:1",empirical=True,assumption=True),
            self.row("arXiv:2",empirical=True,failure=True),
            self.row("arXiv:3",empirical=True,failure=True,boundary=True),
            self.row("arXiv:4",empirical=True,failure=True),
        ]
        state=build_relation_delta_preflight(generator_state=self.generator(old+[new]),relation_state=self.relation(old,"20260813T235959Z"),cache_records=rows)
        self.assertEqual(state["status"],"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE")
        self.assertEqual(state["summary"]["new_reviewed_sources"],2)
        self.assertEqual(state["summary"]["new_assumption_sources"],0)
        self.assertEqual(state["summary"]["new_failure_sources"],2)
        self.assertEqual(state["summary"]["new_boundary_sources"],1)
        self.assertEqual(state["interpretation"]["assumption_break"],"NO_NEW_ASSUMPTION_ENDPOINT")
        self.assertIn("LANE_VALIDITY_UNKNOWN",state["interpretation"]["convergent_failure"])
        self.assertGreater(state["pair_slots"]["failure_failure_slots_touching_new"],0)
        self.assertFalse(state["summary"]["model_scan_authorized"])
        self.assertFalse(state["summary"]["focused_generator_reopen_authorized"])
        self.assertFalse(state["scientific_authority"])
        self.assertTrue(state["policy"]["pair_slots_are_not_lane_valid_pairs"])

    def test_scan_boundary_must_reconstruct_exact_digest(self) -> None:
        old=[self.receipt("20260813T100000Z",["arXiv:1","arXiv:2"])]
        relation=self.relation(old,"20260813T235959Z")
        relation["last_completed_scan"]["relation_universe_digest"]="x"*64
        rows=[self.row("arXiv:1"),self.row("arXiv:2")]
        state=build_relation_delta_preflight(generator_state=self.generator(old),relation_state=relation,cache_records=rows)
        self.assertEqual(state["status"],"HOLD_SCAN_BOUNDARY_NOT_RECONSTRUCTABLE")
        self.assertFalse(state["summary"]["model_scan_authorized"])

    def test_missing_current_cache_holds_preflight_instead_of_treating_missing_as_no_evidence(self) -> None:
        old=[self.receipt("20260813T100000Z",["arXiv:1","arXiv:2"])]
        new=self.receipt("20260814T010000Z",["arXiv:2","arXiv:3"])
        rows=[self.row("arXiv:1"),self.row("arXiv:2")]
        state=build_relation_delta_preflight(generator_state=self.generator(old+[new]),relation_state=self.relation(old,"20260813T235959Z"),cache_records=rows)
        self.assertEqual(state["status"],"HOLD_RELATION_DELTA_CACHE_INCOMPLETE")
        self.assertEqual(state["summary"]["cache_missing_sources"],1)
        self.assertFalse(state["summary"]["model_scan_authorized"])

    def test_public_summary_exposes_counts_not_refs_or_private_material(self) -> None:
        state={"status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE","summary":{"old_reviewed_sources":214,"current_reviewed_sources":226,"new_reviewed_sources":12,"new_failure_sources":11,"model_scan_authorized":False,"focused_generator_reopen_authorized":False},"pair_slots":{"failure_failure_slots_touching_new":1782},"interpretation":{"convergent_failure":"NEW_FAILURE_EVIDENCE_PRESENT_LANE_VALIDITY_UNKNOWN"},"secret_refs":["arXiv:secret"],"private_path":"/home/wyt/private","scientific_authority":False}
        public=public_relation_delta_preflight_summary(state)
        encoded=str(public)
        self.assertEqual(public["summary"]["new_reviewed_sources"],12)
        self.assertEqual(public["pair_slots"]["failure_failure_slots_touching_new"],1782)
        self.assertNotIn("arXiv:secret",encoded)
        self.assertNotIn("/home/wyt",encoded)
        self.assertFalse(public["policy"]["pair_slots_are_not_lane_valid_pairs"] is False)
        self.assertFalse(public["scientific_authority"])

    def test_no_completed_scan_is_unknown_not_a_negative(self) -> None:
        rows=[self.row("arXiv:1",empirical=True)]
        state=build_relation_delta_preflight(generator_state=self.generator([self.receipt("20260814T010000Z",["arXiv:1"])]),relation_state={},cache_records=rows)
        self.assertEqual(state["status"],"NO_COMPLETED_RELATION_SCAN")
        self.assertFalse(state["summary"]["model_scan_authorized"])
        self.assertFalse(state["summary"]["focused_generator_reopen_authorized"])


if __name__=="__main__":
    unittest.main()
