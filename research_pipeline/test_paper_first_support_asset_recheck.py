from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_support_asset_recheck import build_support_asset_recheck_queue, public_support_asset_recheck_summary, write_private_support_asset_recheck_queue


class SupportAssetRecheckQueueTest(unittest.TestCase):
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

    def design(self, candidate_id: str = "C1") -> dict:
        return {
            "shadow_dead_end_memory": {
                "scientific_authority": False,
                "blocked_objects": [{
                    "source_candidate_id": candidate_id,
                    "basin": "near-miss-terminal-support-hold-deadbeef",
                    "disposition": "HOLD_SUPPORT_UNAVAILABLE",
                    "support_status": "SUPPORT_UNAVAILABLE_FOR_FROZEN_PROBLEM_FALSIFIER",
                    "required_unit": "matched released trajectory units",
                    "reopen_only_if": "The authors release the matched units.",
                    "strongest_reduction": "generic partial identification",
                    "evidence_basis": ["arXiv:2608.00001"],
                    "source_run_id": "shadow-r1",
                    "source_stage_manifest_sha256": "a" * 64,
                    "scientific_authority": False,
                }],
            },
            "scientific_authority": False,
        }

    def watch(self, status: str = "RECHECK_REQUIRED_RELEASE_CHANGED") -> dict:
        return {
            "schema_version": "1.0",
            "status": "SUPPORT_RELEASE_WATCH_COMPLETE",
            "rows": [{
                "candidate_id": "C1",
                "status": status,
                "declaration_kind": "PROJECT_PAGE",
                "url": "https://lab.github.io/project/",
                "fingerprint": "b" * 64,
                "scientific_authority": False,
            }],
            "scientific_authority": False,
        }

    def test_release_change_creates_zero_authority_asset_recheck_task(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state = build_support_asset_recheck_queue(
                storage=self.storage(Path(td)), watch_state=self.watch(), design_state=self.design(), previous_state={},
                now=datetime(2026, 8, 14, tzinfo=timezone.utc),
            )
        self.assertEqual(state["status"], "SUPPORT_ASSET_RECHECK_QUEUE_READY")
        self.assertEqual((state["summary"]["queued"], state["summary"]["new_triggers"]), (1, 1))
        row = state["entries"][0]
        self.assertEqual(row["queue_status"], "AWAIT_ASSET_RECHECK")
        self.assertEqual(row["source_refs"], ["arXiv:2608.00001"])
        self.assertEqual(row["required_unit"], "matched released trajectory units")
        for key in ("support_qualified", "generator_reopen_authorized", "problem_gate_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized", "scientific_authority"):
            self.assertFalse(row[key])

    def test_unresolved_task_survives_watcher_cooldown(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td)); now = datetime(2026, 8, 14, tzinfo=timezone.utc)
            first = build_support_asset_recheck_queue(storage=storage, watch_state=self.watch(), design_state=self.design(), previous_state={}, now=now)
            cooldown = self.watch("SKIPPED_COOLDOWN")
            cooldown["rows"][0]["previous_status"] = "RECHECK_REQUIRED_RELEASE_CHANGED"
            second = build_support_asset_recheck_queue(storage=storage, watch_state=cooldown, design_state=self.design(), previous_state=first, now=now)
        self.assertEqual(second["summary"]["queued"], 1)
        self.assertEqual(second["summary"]["new_triggers"], 0)
        self.assertEqual(second["summary"]["carried_forward"], 1)
        self.assertEqual(second["entries"][0]["queue_id"], first["entries"][0]["queue_id"])
        self.assertEqual(second["entries"][0]["latest_trigger_digest"], first["entries"][0]["latest_trigger_digest"])

    def test_non_recheck_watch_state_does_not_create_task(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state = build_support_asset_recheck_queue(
                storage=self.storage(Path(td)), watch_state=self.watch("BASELINE_CAPTURED"), design_state=self.design(), previous_state={},
                now=datetime(2026, 8, 14, tzinfo=timezone.utc),
            )
        self.assertEqual(state["status"], "SUPPORT_ASSET_RECHECK_QUEUE_EMPTY")
        self.assertEqual(state["entries"], [])
        self.assertEqual(state["summary"]["queued"], 0)

    def test_task_is_not_carried_when_candidate_is_no_longer_current_support_hold(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td)); now = datetime(2026, 8, 14, tzinfo=timezone.utc)
            first = build_support_asset_recheck_queue(storage=storage, watch_state=self.watch(), design_state=self.design(), previous_state={}, now=now)
            resolved_design = {"shadow_dead_end_memory": {"blocked_objects": [], "scientific_authority": False}, "scientific_authority": False}
            second = build_support_asset_recheck_queue(storage=storage, watch_state={"rows": [], "scientific_authority": False}, design_state=resolved_design, previous_state=first, now=now)
        self.assertEqual(second["entries"], [])
        self.assertEqual(second["summary"]["support_holds"], 0)

    def test_public_summary_exposes_counts_not_private_queue_entries(self) -> None:
        private = build_support_asset_recheck_queue(
            storage=self.storage(Path('/tmp/unused-support-recheck-test')),
            watch_state=self.watch(), design_state=self.design(), previous_state={}, now=datetime(2026, 8, 14, tzinfo=timezone.utc),
        )
        public = public_support_asset_recheck_summary(private)
        text = str(public)
        self.assertEqual(public["summary"]["queued"], 1)
        self.assertFalse(public["scientific_authority"])
        self.assertNotIn("entries", public)
        for marker in ("arXiv:2608.00001", "github.io", "matched released trajectory units", "C1"):
            self.assertNotIn(marker, text)

    def test_private_writer_persists_empty_or_ready_queue_only_under_private_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            state = write_private_support_asset_recheck_queue(storage=storage, watch_state=self.watch(), design_state=self.design(), now=datetime(2026, 8, 14, tzinfo=timezone.utc))
            path = storage.data_root / "paper-first-problem-discovery" / "support-release-watch" / "asset-recheck-queue.json"
            self.assertTrue(path.exists())
            self.assertEqual(state["summary"]["queued"], 1)
            self.assertFalse(state["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
