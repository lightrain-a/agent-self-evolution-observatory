from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_support_release_watch import explicit_release_targets, run_support_release_watch


class SupportReleaseWatchTest(unittest.TestCase):
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

    def hold(self, candidate: str, ref: str) -> dict:
        return {
            "source_candidate_id": candidate,
            "basin": "near-miss-terminal-support-hold-deadbeef",
            "disposition": "HOLD_SUPPORT_UNAVAILABLE",
            "support_status": "SUPPORT_UNAVAILABLE_FOR_FROZEN_PROBLEM_FALSIFIER",
            "required_unit": "matched released unit-level traces",
            "evidence_basis": [ref],
            "reopen_only_if": "The authors release the required matched unit-level traces.",
            "scientific_authority": False,
        }

    def design(self, rows: list[dict]) -> dict:
        return {"shadow_dead_end_memory": {"blocked_objects": rows, "scientific_authority": False}, "scientific_authority": False}

    def cache(self, storage: StorageSettings, arxiv_id: str, text: str, *, full: bool = False) -> None:
        root = storage.data_root / "paper-first-problem-discovery" / "primary-sources"
        root.mkdir(parents=True, exist_ok=True)
        prefix = "arxiv-full" if full else "arxiv"
        (root / f"{prefix}-{arxiv_id}-test.html").write_text(text, encoding="utf-8")

    def test_extracts_future_code_and_project_page_but_not_bibliography_repo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            self.cache(storage, "2607.00001", 'Our code will be made publicly available soon at https://github.com/example/FutureRepo .')
            self.cache(storage, "2608.00002", '<span>Project page: </span><a href="https://lab.github.io/ProjectX/">Project</a>', full=True)
            self.cache(storage, "2608.00003", 'References. Note: https://github.com/other/baseline repository.', full=True)
            targets, missing = explicit_release_targets(self.design([
                self.hold("A", "arXiv:2607.00001"),
                self.hold("B", "arXiv:2608.00002"),
                self.hold("C", "arXiv:2608.00003"),
            ]), storage=storage)
        by_id = {row["candidate_id"]: row for row in targets}
        self.assertEqual(by_id["A"]["declaration_kind"], "FUTURE_CODE_RELEASE")
        self.assertEqual(by_id["B"]["declaration_kind"], "PROJECT_PAGE")
        self.assertNotIn("C", by_id)
        self.assertEqual([row["candidate_id"] for row in missing], ["C"])

    def test_no_explicit_endpoint_never_calls_network(self) -> None:
        calls = []
        def forbidden(target):
            calls.append(target)
            raise AssertionError("network forbidden")
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            self.cache(storage, "2608.00003", 'The code may be released after acceptance.')
            state = run_support_release_watch(storage=storage, design_state=self.design([self.hold("C", "arXiv:2608.00003")]), fetcher=forbidden, write_ledger=False)
        self.assertEqual(calls, [])
        self.assertEqual(state["summary"]["no_explicit_endpoint"], 1)
        self.assertEqual(state["summary"]["checked"], 0)
        self.assertEqual(state["summary"]["support_qualified"], 0)

    def test_future_code_first_success_only_requests_recheck(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            self.cache(storage, "2607.00001", 'Our code will be made publicly available soon at https://github.com/example/FutureRepo .')
            state = run_support_release_watch(
                storage=storage,
                design_state=self.design([self.hold("A", "arXiv:2607.00001")]),
                fetcher=lambda target: {"status_code": 200, "fingerprint": "a" * 64, "surface_nonempty": True},
                now=datetime(2026, 8, 14, tzinfo=timezone.utc),
                write_ledger=False,
            )
        self.assertEqual(state["rows"][0]["status"], "RECHECK_REQUIRED_NEW_RELEASE_SURFACE")
        self.assertEqual(state["summary"]["recheck_required"], 1)
        self.assertEqual(state["summary"]["support_qualified"], 0)
        self.assertEqual(state["summary"]["generator_reopen_authorized"], 0)

    def test_project_page_baselines_then_only_change_requests_recheck(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            self.cache(storage, "2608.00002", '<span>Project page: </span><a href="https://lab.github.io/ProjectX/">Project</a>', full=True)
            design = self.design([self.hold("B", "arXiv:2608.00002")])
            ledger = storage.data_root / "watch.json"
            first = run_support_release_watch(storage=storage, design_state=design, fetcher=lambda target: {"status_code": 200, "fingerprint": "a" * 64, "surface_nonempty": True}, now=datetime(2026, 8, 1, tzinfo=timezone.utc), cooldown_days=7, ledger_path=ledger)
            same = run_support_release_watch(storage=storage, design_state=design, fetcher=lambda target: {"status_code": 200, "fingerprint": "a" * 64, "surface_nonempty": True}, now=datetime(2026, 8, 9, tzinfo=timezone.utc), cooldown_days=7, ledger_path=ledger)
            changed = run_support_release_watch(storage=storage, design_state=design, fetcher=lambda target: {"status_code": 200, "fingerprint": "b" * 64, "surface_nonempty": True}, now=datetime(2026, 8, 17, tzinfo=timezone.utc), cooldown_days=7, ledger_path=ledger)
        self.assertEqual(first["rows"][0]["status"], "BASELINE_CAPTURED")
        self.assertEqual(same["rows"][0]["status"], "NO_RELEASE_CHANGE")
        self.assertEqual(changed["rows"][0]["status"], "RECHECK_REQUIRED_RELEASE_CHANGED")
        self.assertEqual(changed["summary"]["support_qualified"], 0)

    def test_cooldown_reuses_observation_without_network(self) -> None:
        calls = []
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            self.cache(storage, "2607.00001", 'Our code will be made publicly available soon at https://github.com/example/FutureRepo .')
            design = self.design([self.hold("A", "arXiv:2607.00001")])
            ledger = storage.data_root / "watch.json"
            run_support_release_watch(storage=storage, design_state=design, fetcher=lambda target: {"status_code": 200, "fingerprint": "a" * 64, "surface_nonempty": True}, now=datetime(2026, 8, 1, tzinfo=timezone.utc), cooldown_days=7, ledger_path=ledger)
            def forbidden(target):
                calls.append(target)
                raise AssertionError("cooldown must prevent network")
            second = run_support_release_watch(storage=storage, design_state=design, fetcher=forbidden, now=datetime(2026, 8, 2, tzinfo=timezone.utc), cooldown_days=7, ledger_path=ledger)
        self.assertEqual(calls, [])
        self.assertEqual(second["summary"]["skipped_cooldown"], 1)
        self.assertEqual(second["rows"][0]["status"], "SKIPPED_COOLDOWN")


if __name__ == "__main__":
    unittest.main()
