from __future__ import annotations

import unittest

from .paper_first_relation_coverage import relation_recall_freshness, relation_universe_digest


class PaperFirstRelationCoverageTest(unittest.TestCase):
    def generator(self, receipts: list[dict]) -> dict:
        return {"saturation_memory": {"portable_review_receipts": receipts}}

    def receipt(self, run_id: str, refs: list[str]) -> dict:
        return {"run_id": run_id, "source_refs": refs, "scientific_authority": False}

    def relation(self, receipts: list[dict], *, not_reduced: int = 0, reopen: bool = False) -> dict:
        refs = {ref for row in receipts for ref in row["source_refs"]}
        possible = len(refs) * (len(refs) - 1) // 2
        return {
            "status": "GLOBAL_RELATION_RECALL_COMPLETE",
            "summary": {
                "reviewed_receipt_sources": len(refs),
                "not_reduced": not_reduced,
                "focused_problem_generator_reopen_required": reopen,
            },
            "last_completed_scan": {
                "run_id": max((str(row.get("run_id") or "") for row in receipts), default=""),
                "relation_universe_digest": relation_universe_digest(receipts),
                "relation_coverage": {
                    "reviewed_receipt_sources": len(refs),
                    "possible_source_pairs": possible,
                    "coobserved_source_pairs": 1,
                    "pair_coverage_fraction": 1 / possible if possible else 1.0,
                },
                "summary": {
                    "reviewed_receipt_sources": len(refs),
                    "not_reduced": not_reduced,
                    "focused_problem_generator_reopen_required": reopen,
                },
                "scientific_authority": False,
            },
        }

    def test_changed_relation_universe_marks_old_zero_as_unknown_and_deferred(self) -> None:
        old = [self.receipt("r1", ["arXiv:A", "arXiv:B"])]
        current = [*old, self.receipt("r2", ["arXiv:B", "arXiv:C"])]
        state = relation_recall_freshness(self.generator(current), self.relation(old, not_reduced=0))
        self.assertEqual(state["status"], "STALE_RELATION_UNIVERSE")
        self.assertTrue(state["summary"]["universe_stale"])
        self.assertTrue(state["summary"]["current_not_reduced_unknown"])
        self.assertTrue(state["summary"]["model_scan_deferred"])
        self.assertFalse(state["summary"]["focused_problem_generator_reopen_allowed"])
        self.assertEqual((state["summary"]["last_scanned_sources"], state["summary"]["current_reviewed_sources"]), (2, 3))
        self.assertNotEqual(state["last_scanned_relation_universe_digest"], state["current_relation_universe_digest"])
        self.assertFalse(state["scientific_authority"])

    def test_scheduler_only_coobservation_drift_does_not_trigger_model_rescan(self) -> None:
        old=[self.receipt("r1",["arXiv:A","arXiv:B"]),self.receipt("r2",["arXiv:A","arXiv:C"])]
        current=[*old,self.receipt("r3",["arXiv:B","arXiv:C"])]
        state=relation_recall_freshness(self.generator(current),self.relation(old,not_reduced=0))
        self.assertEqual(state["status"],"CURRENT_RELATION_UNIVERSE")
        self.assertTrue(state["summary"]["raw_topology_digest_changed"])
        self.assertTrue(state["summary"]["source_boundary_reconstructable"])
        self.assertTrue(state["summary"]["scheduler_topology_only_drift"])
        self.assertFalse(state["summary"]["universe_stale"])
        self.assertFalse(state["summary"]["current_not_reduced_unknown"])
        self.assertFalse(state["summary"]["model_scan_deferred"])
        self.assertEqual(state["current_source_universe_digest"],state["last_scanned_source_universe_digest"])
        self.assertNotEqual(state["current_relation_universe_digest"],state["last_scanned_relation_universe_digest"])
        self.assertTrue(state["policy"]["portable_review_receipts_are_scheduler_metadata_only"])
        self.assertTrue(state["policy"]["scheduler_topology_only_drift_does_not_require_model_rescan"])

    def test_same_relation_universe_keeps_completed_scan_current(self) -> None:
        receipts = [self.receipt("r1", ["arXiv:A", "arXiv:B", "arXiv:C"])]
        state = relation_recall_freshness(self.generator(receipts), self.relation(receipts, not_reduced=1, reopen=True))
        self.assertEqual(state["status"], "CURRENT_RELATION_UNIVERSE")
        self.assertFalse(state["summary"]["universe_stale"])
        self.assertFalse(state["summary"]["current_not_reduced_unknown"])
        self.assertFalse(state["summary"]["model_scan_deferred"])
        self.assertTrue(state["summary"]["focused_problem_generator_reopen_allowed"])
        self.assertEqual(state["last_scanned_relation_universe_digest"], state["current_relation_universe_digest"])

    def test_no_completed_scan_is_unknown_without_automatic_reopen(self) -> None:
        receipts = [self.receipt("r1", ["arXiv:A", "arXiv:B"])]
        state = relation_recall_freshness(self.generator(receipts), {"status": "NOT_RUN", "summary": {}})
        self.assertEqual(state["status"], "NO_COMPLETED_RELATION_SCAN")
        self.assertTrue(state["summary"]["current_not_reduced_unknown"])
        self.assertFalse(state["summary"]["focused_problem_generator_reopen_allowed"])
        self.assertFalse(state["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
