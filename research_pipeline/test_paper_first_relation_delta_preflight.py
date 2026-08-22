from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_relation_coverage import relation_universe_digest
from .paper_first_relation_delta_preflight import build_relation_delta_preflight, public_relation_delta_preflight_summary
from .relation_scan_boundary_manifest import build_relation_scan_boundary_manifest


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

    def test_current_relation_universe_short_circuits_scheduler_boundary_reconstruction(self) -> None:
        old=self.receipt("20260813T100000Z",["arXiv:1","arXiv:2"])
        scheduler_duplicate=self.receipt("20260814T010000Z",["arXiv:1","arXiv:2"])
        relation=self.relation([old],"20260813T235959Z")
        state=build_relation_delta_preflight(generator_state=self.generator([old,scheduler_duplicate]),relation_state=relation,cache_records=[])
        self.assertEqual(state["status"],"RELATION_DELTA_CURRENT_UNIVERSE_NO_NEW_SOURCES")
        self.assertEqual(state["boundary_source"],"CURRENT_RELATION_UNIVERSE_EXACT_DIGEST")
        self.assertEqual(state["summary"]["new_reviewed_sources"],0)
        self.assertEqual(state["summary"]["new_receipt_runs"],0)
        self.assertEqual(state["summary"]["cache_missing_sources"],0)
        self.assertFalse(state["summary"]["model_scan_authorized"])
        self.assertFalse(state["summary"]["focused_generator_reopen_authorized"])

    def test_scan_boundary_must_reconstruct_exact_digest(self) -> None:
        old=[self.receipt("20260813T100000Z",["arXiv:1","arXiv:2"])]
        relation=self.relation(old,"20260813T235959Z")
        relation["last_completed_scan"]["relation_universe_digest"]="x"*64
        rows=[self.row("arXiv:1"),self.row("arXiv:2")]
        state=build_relation_delta_preflight(generator_state=self.generator(old),relation_state=relation,cache_records=rows)
        self.assertEqual(state["status"],"HOLD_SCAN_BOUNDARY_NOT_RECONSTRUCTABLE")
        self.assertFalse(state["summary"]["model_scan_authorized"])

    def test_content_addressed_archive_recovers_replayed_receipt_boundary(self) -> None:
        archived = [
            self.receipt("20260813T100000Z", ["arXiv:1", "arXiv:2"]),
            self.receipt("20260813T110000Z", ["arXiv:2", "arXiv:3"]),
        ]
        relation = {
            "last_completed_scan": {
                "run_id": "20260813T235959Z",
                "relation_universe_digest": relation_universe_digest(archived),
                "relation_coverage": {
                    "reviewed_receipt_sources": 3,
                    "coobserved_source_pairs": 2,
                },
            },
            "raw_artifacts": {"relation": {"sha256": "a" * 64}},
        }
        replayed = [
            self.receipt("20260813T100000Z", ["arXiv:1", "arXiv:2"]),
            self.receipt("20260814T010000Z-replay", ["arXiv:2", "arXiv:3"]),
            self.receipt("20260814T020000Z", ["arXiv:3", "arXiv:4"]),
        ]
        rows = [self.row(f"arXiv:{index}", empirical=True) for index in range(1, 5)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generator_path = root / "generator.json"
            relation_path = root / "relation.json"
            generator_path.write_text(
                json.dumps(self.generator(archived)),
                encoding="utf-8",
            )
            relation_path.write_text(json.dumps(relation), encoding="utf-8")
            manifest = build_relation_scan_boundary_manifest(
                archived_generator_path=generator_path,
                relation_path=relation_path,
            )
        state = build_relation_delta_preflight(
            generator_state=self.generator(replayed),
            relation_state=relation,
            cache_records=rows,
            boundary_manifest=manifest,
        )
        self.assertEqual(state["status"], "RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE")
        self.assertEqual(state["boundary_source"], "CONTENT_ADDRESSED_ARCHIVED_RECEIPTS")
        self.assertEqual(state["summary"]["old_reviewed_sources"], 3)
        self.assertEqual(state["summary"]["new_reviewed_sources"], 1)
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
