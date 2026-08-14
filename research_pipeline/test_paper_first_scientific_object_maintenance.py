from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_scientific_object_maintenance import run_shadow_scientific_object_maintenance


class ScientificObjectMaintenanceTest(unittest.TestCase):
    NOW = datetime(2026, 8, 14, 4, 50, tzinfo=timezone.utc)

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

    def primary(self, *, exhausted: bool = True, retrieval_complete: bool = True, carrier_complete: bool = True) -> dict:
        return {
            "status": "READY",
            "summary": {
                "source_retrieval_complete": retrieval_complete,
                "source_coverage_exhausted": exhausted,
                "carrier_probe_complete": carrier_complete,
            },
        }

    def writer(self, calls: dict[str, int], key: str, result: dict):
        def run(*, storage: StorageSettings):
            calls[key] = calls.get(key, 0) + 1
            return result
        return run

    def loader(self, state: dict):
        def load(*, storage: StorageSettings):
            return state
        return load

    def test_open_live_coverage_skips_every_shadow_writer(self) -> None:
        calls: dict[str, int] = {}
        with tempfile.TemporaryDirectory() as td:
            state = run_shadow_scientific_object_maintenance(
                storage=self.storage(Path(td)),
                primary_state=self.primary(exhausted=False),
                now=self.NOW,
                retrieval_writer=self.writer(calls, "retrieval", {}),
                candidate_writer=self.writer(calls, "candidate", {}),
                ontology_writer=self.writer(calls, "ontology", {}),
                retrieval_state_loader=self.loader({}),
                canonical_sha_provider=lambda: {"primary": "a", "generator": "b", "queue": "c"},
            )
        self.assertEqual(state["status"], "SKIPPED_LIVE_SOURCE_COVERAGE_NOT_CLOSED")
        self.assertEqual(calls, {})
        self.assertTrue(state["canonical_public_state_unchanged"])
        self.assertFalse(state["scientific_authority"])

    def test_recent_complete_retrieval_skips_network_but_recomputes_offline_layers(self) -> None:
        calls: dict[str, int] = {}
        previous = {
            "status": "SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE",
            "generated_at": (self.NOW - timedelta(days=1)).isoformat(),
            "scientific_authority": False,
        }
        candidate = {"status": "SHADOW_CANDIDATE_EVIDENCE_COMPLETE", "summary": {"primary_verified": 2}}
        ontology = {"status": "SHADOW_AUDIT_ONLY", "summary": {"activation_authorized": 0}}
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            state = run_shadow_scientific_object_maintenance(
                storage=storage,
                primary_state=self.primary(),
                now=self.NOW,
                retrieval_writer=self.writer(calls, "retrieval", {}),
                candidate_writer=self.writer(calls, "candidate", candidate),
                ontology_writer=self.writer(calls, "ontology", ontology),
                retrieval_state_loader=self.loader(previous),
                canonical_sha_provider=lambda: {"primary": "a", "generator": "b", "queue": "c"},
            )
            artifacts = list((storage.run_dir / "paper-first-object-maintenance").glob("*.json"))
        self.assertEqual(calls, {"candidate": 1, "ontology": 1})
        self.assertEqual(state["status"], "SHADOW_OBJECT_MAINTENANCE_COMPLETE")
        self.assertEqual(state["steps"][0]["status"], "SKIPPED_RECENT_COMPLETE_AUDIT")
        self.assertEqual(len(artifacts), 1)
        self.assertTrue(state["canonical_public_state_unchanged"])

    def test_stale_or_missing_audit_runs_one_retrieval_then_offline_layers(self) -> None:
        calls: dict[str, int] = {}
        previous = {
            "status": "SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE",
            "generated_at": (self.NOW - timedelta(days=8)).isoformat(),
            "scientific_authority": False,
        }
        retrieval = {"status": "SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE", "scientific_authority": False}
        candidate = {"status": "SHADOW_CANDIDATE_EVIDENCE_COMPLETE", "summary": {"primary_verified": 0}}
        ontology = {"status": "SHADOW_AUDIT_ONLY", "summary": {"activation_authorized": 0}}
        with tempfile.TemporaryDirectory() as td:
            state = run_shadow_scientific_object_maintenance(
                storage=self.storage(Path(td)),
                primary_state=self.primary(),
                now=self.NOW,
                retrieval_writer=self.writer(calls, "retrieval", retrieval),
                candidate_writer=self.writer(calls, "candidate", candidate),
                ontology_writer=self.writer(calls, "ontology", ontology),
                retrieval_state_loader=self.loader(previous),
                canonical_sha_provider=lambda: {"primary": "a", "generator": "b", "queue": "c"},
            )
        self.assertEqual(calls, {"retrieval": 1, "candidate": 1, "ontology": 1})
        self.assertEqual(state["status"], "SHADOW_OBJECT_MAINTENANCE_COMPLETE")
        self.assertEqual(state["steps"][0]["status"], "SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE")

    def test_incomplete_retrieval_stays_shadow_and_does_not_become_negative(self) -> None:
        calls: dict[str, int] = {}
        retrieval = {"status": "SHADOW_OBJECT_RETRIEVAL_AUDIT_INCOMPLETE", "scientific_authority": False}
        candidate = {"status": "SHADOW_CANDIDATE_EVIDENCE_BLOCKED_RETRIEVAL_INCOMPLETE", "summary": {"primary_verified": 0}}
        ontology = {"status": "SHADOW_AUDIT_ONLY", "summary": {"activation_authorized": 0}}
        with tempfile.TemporaryDirectory() as td:
            state = run_shadow_scientific_object_maintenance(
                storage=self.storage(Path(td)),
                primary_state=self.primary(),
                now=self.NOW,
                retrieval_writer=self.writer(calls, "retrieval", retrieval),
                candidate_writer=self.writer(calls, "candidate", candidate),
                ontology_writer=self.writer(calls, "ontology", ontology),
                retrieval_state_loader=self.loader({"status": "NOT_RUN"}),
                canonical_sha_provider=lambda: {"primary": "a", "generator": "b", "queue": "c"},
            )
        self.assertEqual(state["status"], "SHADOW_OBJECT_MAINTENANCE_RETRIEVAL_INCOMPLETE")
        self.assertEqual(calls, {"retrieval": 1, "candidate": 1, "ontology": 1})
        self.assertFalse(state["scientific_authority"])
        self.assertFalse(state["generator_called"])
        self.assertFalse(state["reviewer_called"])

    def test_canonical_sha_change_aborts_shadow_maintenance(self) -> None:
        calls: dict[str, int] = {}
        shas = iter([
            {"primary": "a", "generator": "b", "queue": "c"},
            {"primary": "changed", "generator": "b", "queue": "c"},
        ])
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(RuntimeError, "mutated canonical Primary/Generator/Queue"):
                run_shadow_scientific_object_maintenance(
                    storage=self.storage(Path(td)),
                    primary_state=self.primary(),
                    now=self.NOW,
                    retrieval_writer=self.writer(calls, "retrieval", {"status": "SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE"}),
                    candidate_writer=self.writer(calls, "candidate", {"status": "SHADOW_CANDIDATE_EVIDENCE_COMPLETE", "summary": {}}),
                    ontology_writer=self.writer(calls, "ontology", {"status": "SHADOW_AUDIT_ONLY", "summary": {}}),
                    retrieval_state_loader=self.loader({"status": "NOT_RUN"}),
                    canonical_sha_provider=lambda: next(shas),
                )
        self.assertEqual(calls, {"retrieval": 1, "candidate": 1, "ontology": 1})


if __name__ == "__main__":
    unittest.main()
