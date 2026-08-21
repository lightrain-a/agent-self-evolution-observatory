from __future__ import annotations

import copy
import unittest

from .paper_first_parallel_search_admission import build_parallel_search_admission
from .paper_first_problem_generator import _pool_sha


def _record(ref: str, lane: str = "runtime_deployment") -> dict:
    return {
        "ref": ref,
        "title": ref,
        "source_sha256": "a" * 64,
        "fulltext_sha256": "b" * 64,
        "primary_source_verified": True,
        "lane_keys": [lane] if lane else [],
        "parallel_delta_provenance": {"scientific_authority": False},
    }


class ParallelSearchAdmissionTest(unittest.TestCase):
    def inputs(self) -> dict:
        tx = "c" * 64
        pool = {"status": "READY", "generated_at": "2026-08-20T00:00:00+00:00", "records": [_record("arXiv:2608.00001")]}
        snapshots = ["1" * 64, "2" * 64, "3" * 64]
        rows = [{"candidate_id": f"C{i}", "candidate_snapshot_sha256": value} for i, value in enumerate(snapshots, 1)]
        return {
            "primary_state": {"status": "READY", "discovery_transaction_id": tx},
            "generator_state": {
                "discovery_transaction_id": tx,
                "saturation_memory": {"current_review_receipt": {"pool_sha256": _pool_sha(pool)}},
            },
            "queue_state": {
                "discovery_transaction_id": tx,
                "summary": {"passed_problem_gate": 0, "paper_design_eligible": 0},
            },
            "pre_f0_state": {"rows": rows},
            "support_preflight": {
                "summary": {
                    "queued": 3,
                    "support_qualified": 0,
                    "hold_support_unavailable": 3,
                    "falsifier_executed": 0,
                }
            },
            "round3_manifest": {},
            "canonical_private_pool": pool,
            "delta_records": [_record("arXiv:2608.15591")],
        }

    def test_fresh_lane_grounded_delta_can_open_zero_authority_parallel_qualification(self) -> None:
        state = build_parallel_search_admission(**self.inputs())
        self.assertEqual(state["status"], "READY_FOR_PARALLEL_SEARCH_QUALIFICATION")
        self.assertEqual(state["summary"]["search_hold_shortfall"], 2)
        self.assertEqual(state["summary"]["delta_sources"], 1)
        self.assertEqual(state["summary"]["automatic_provider_calls_authorized"], 0)
        self.assertEqual(len(state["canonical_binding"]["current_candidate_snapshot_sha256"]), 3)
        self.assertFalse(state["scientific_authority"])
        self.assertTrue(all(value is False for value in state["authority"].values()))

    def test_round3_recovery_lineage_can_bind_missing_generator_stamp(self) -> None:
        values = self.inputs()
        tx = values["primary_state"]["discovery_transaction_id"]
        pool_sha = _pool_sha(values["canonical_private_pool"])
        values["generator_state"].pop("discovery_transaction_id")
        values["generator_state"]["raw_artifacts"] = {"generator": {"sha256": "d" * 64}}
        values["generator_state"]["portfolio_ingestion_recovery"] = {
            "source_transaction_id": tx,
            "source_portfolio_sha256": "e" * 64,
            "recovery_sha256": "d" * 64,
        }
        values["round3_manifest"] = {
            "status": "ROUND3_PROVENANCE_COMPLETE",
            "manifest_content_sha256": "f" * 64,
            "transaction": {"transaction_id": tx, "source_pool_sha256": pool_sha},
            "source_artifacts": {"portfolio_sha256": "e" * 64, "ingestion_recovery_sha256": "d" * 64},
            "coverage": {"record_level_lineage_complete": True},
        }
        state = build_parallel_search_admission(**values)
        self.assertEqual(state["status"], "READY_FOR_PARALLEL_SEARCH_QUALIFICATION")
        self.assertEqual(state["canonical_binding"]["mode"], "ROUND3_RECOVERY_LINEAGE")

    def test_support_qualified_candidate_blocks_parallel_capacity_recovery(self) -> None:
        values = self.inputs()
        values["support_preflight"] = copy.deepcopy(values["support_preflight"])
        values["support_preflight"]["summary"].update({"support_qualified": 1, "hold_support_unavailable": 2})
        state = build_parallel_search_admission(**values)
        self.assertEqual(state["status"], "HOLD_PARALLEL_SEARCH_ADMISSION")
        failed = {row["key"] for row in state["checks"] if row["pass"] is not True}
        self.assertIn("support-preflight-covers-current-holds", failed)

    def test_reused_or_unverified_delta_cannot_reopen_search(self) -> None:
        values = self.inputs()
        values["delta_records"] = [copy.deepcopy(values["canonical_private_pool"]["records"][0])]
        values["delta_records"][0]["parallel_delta_provenance"] = {"scientific_authority": False}
        state = build_parallel_search_admission(**values)
        self.assertEqual(state["status"], "HOLD_PARALLEL_SEARCH_ADMISSION")
        failed = {row["key"] for row in state["checks"] if row["pass"] is not True}
        self.assertIn("delta-source-not-canonical", failed)


if __name__ == "__main__":
    unittest.main()
