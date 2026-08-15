from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_support_asset_recheck_handoff import (
    build_support_asset_recheck_handoff,
    load_private_support_asset_recheck_handoff,
    public_support_asset_recheck_handoff_summary,
    write_private_support_asset_recheck_handoff,
)


class SupportAssetRecheckHandoffTest(unittest.TestCase):
    def storage(self, root: Path) -> StorageSettings:
        return StorageSettings(
            data_root=root,
            corpus_dir=root / "corpora",
            dataset_dir=root / "datasets",
            paper_dir=root / "papers",
            index_dir=root / "indexes",
            run_dir=root / "runs",
            cache_dir=root / "cache",
            lock_dir=root / "locks",
            site_artifact_dir=root / "site",
        )

    def queue(self, *, complete: bool = True) -> dict:
        return {
            "schema_version": "1.0",
            "status": "SUPPORT_ASSET_RECHECK_QUEUE_READY",
            "entries": [{
                "queue_id": "a" * 64,
                "candidate_id": "C1",
                "queue_status": "AWAIT_ASSET_RECHECK",
                "latest_trigger_digest": "b" * 64,
                "source_run_id": "shadow-r1" if complete else "",
                "source_stage_manifest_sha256": "c" * 64 if complete else "",
                "source_refs": ["arXiv:2608.00001"],
                "required_unit": "matched released trajectory units",
                "reopen_only_if": "The release contains those units.",
                "scientific_authority": False,
            }],
            "scientific_authority": False,
        }

    def test_empty_queue_produces_zero_authority_empty_handoff(self) -> None:
        state = build_support_asset_recheck_handoff(
            storage=self.storage(Path('/tmp/unused-handoff-test')),
            queue_state={"entries": [], "scientific_authority": False},
            now=datetime(2026, 8, 14, tzinfo=timezone.utc),
        )
        self.assertEqual(state["status"], "SUPPORT_ASSET_RECHECK_HANDOFF_EMPTY")
        self.assertEqual(state["summary"]["support_inventory_recheck_ready"], 0)
        self.assertEqual(state["entries"], [])
        self.assertFalse(state["scientific_authority"])

    def test_ready_queue_hands_off_to_existing_support_inventory_without_authority(self) -> None:
        state = build_support_asset_recheck_handoff(
            storage=self.storage(Path('/tmp/unused-handoff-test')),
            queue_state=self.queue(),
            now=datetime(2026, 8, 14, tzinfo=timezone.utc),
        )
        self.assertEqual(state["status"], "SUPPORT_ASSET_RECHECK_HANDOFF_READY")
        self.assertEqual((state["summary"]["queued_asset_rechecks"], state["summary"]["support_inventory_recheck_ready"]), (1, 1))
        row = state["entries"][0]
        self.assertEqual(row["next_entrypoint"], "research_pipeline.paper_first_problem_falsifier_preflight")
        self.assertIn("materialized independent truth", row["support_inventory_scope"])
        self.assertTrue(row["support_inventory_request_required"])
        self.assertTrue(state["policy"]["support_inventory_must_consider_direct_or_reconstructed_truth"])
        self.assertTrue(state["policy"]["reconstructed_truth_requires_materialized_units_and_provenance_before_qualification"])
        for key in ("automatic_execution_authorized","provider_calls_authorized","support_qualified","falsifier_execution_authorized","generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized","scientific_authority"):
            self.assertFalse(row[key])

    def test_missing_run_provenance_holds_before_support_inventory(self) -> None:
        state = build_support_asset_recheck_handoff(
            storage=self.storage(Path('/tmp/unused-handoff-test')),
            queue_state=self.queue(complete=False),
            now=datetime(2026, 8, 14, tzinfo=timezone.utc),
        )
        self.assertEqual(state["status"], "SUPPORT_ASSET_RECHECK_HANDOFF_HOLD_PROVENANCE")
        self.assertEqual(state["summary"]["support_inventory_recheck_ready"], 0)
        self.assertEqual(state["summary"]["provenance_incomplete"], 1)
        self.assertEqual(state["entries"][0]["handoff_status"], "HOLD_RECHECK_HANDOFF_PROVENANCE_INCOMPLETE")

    def test_public_summary_exposes_health_counts_not_private_handoff_rows(self) -> None:
        private=build_support_asset_recheck_handoff(storage=self.storage(Path('/tmp/unused-handoff-public')),queue_state=self.queue(),now=datetime(2026,8,14,tzinfo=timezone.utc))
        public=public_support_asset_recheck_handoff_summary(private);text=str(public)
        self.assertEqual((public["summary"]["queued_asset_rechecks"],public["summary"]["support_inventory_recheck_ready"],public["summary"]["provenance_incomplete"]),(1,1,0))
        self.assertFalse(public["scientific_authority"])
        self.assertNotIn("entries",public)
        for marker in ("C1","arXiv:2608.00001","matched released trajectory units","shadow-r1"):
            self.assertNotIn(marker,text)
        self.assertTrue(public["policy"]["problem_falsifier_preflight_remains_support_authority_boundary"])

    def test_private_writer_persists_handoff_only_in_private_data_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            state = write_private_support_asset_recheck_handoff(storage=storage, queue_state=self.queue(), now=datetime(2026, 8, 14, tzinfo=timezone.utc))
            path = storage.data_root / "paper-first-problem-discovery" / "support-release-watch" / "asset-recheck-handoff.json"
            self.assertTrue(path.exists())
            self.assertEqual(state["status"], "SUPPORT_ASSET_RECHECK_HANDOFF_READY")
            loaded=load_private_support_asset_recheck_handoff(storage=storage)
            self.assertEqual(loaded["summary"]["support_inventory_recheck_ready"],1)
            self.assertFalse(state["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
