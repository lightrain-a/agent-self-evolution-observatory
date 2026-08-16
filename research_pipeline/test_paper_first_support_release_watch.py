from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from . import paper_first_support_release_watch as watch
from .config import StorageSettings
from .paper_first_support_release_watch import (
    build_portable_release_target_manifest,
    explicit_release_targets,
    public_support_release_watch_summary,
    run_support_release_watch,
    validate_portable_release_target_manifest,
    write_portable_release_target_manifest,
)


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

    def test_split_hold_memory_is_watched_and_reused_candidate_ids_join_by_source_ref(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            first = {**self.hold("A", "arXiv:2607.00001"), "source_run_id": "r1", "dead_end_certified": False, "memory_class": "REOPENABLE_HOLD"}
            second = {**self.hold("A", "arXiv:2608.00002"), "source_run_id": "r2", "basin": "near-miss-terminal-support-hold-cafebabe", "dead_end_certified": False, "memory_class": "REOPENABLE_HOLD"}
            dead = {**self.hold("D", "arXiv:2608.00003"), "source_run_id": "r3", "basin": "near-miss-terminal-support-hold-feedface", "dead_end_certified": True, "memory_class": "PRINCIPLE_DEAD_END"}
            design = {"shadow_dead_end_memory": {"blocked_objects": [], "hold_objects": [first, second, dead], "scientific_authority": False}, "scientific_authority": False}
            self.cache(storage, "2607.00001", 'Our code will be made publicly available soon at https://github.com/example/FirstRepo .')
            self.cache(storage, "2608.00002", '<span>Project page: </span><a href="https://lab.github.io/SecondProject/">Project</a>', full=True)
            self.cache(storage, "2608.00003", 'Our code will be made publicly available soon at https://github.com/example/DeadRepo .')
            targets, missing = explicit_release_targets(design, storage=storage)
            manifest = build_portable_release_target_manifest(design, storage=storage)
            joined = watch._portable_targets_for_holds(design, manifest)
        self.assertEqual(len(watch._terminal_support_holds(design)), 2)
        self.assertEqual(len(targets), 2)
        self.assertEqual(missing, [])
        self.assertEqual({row["source_ref"] for row in targets}, {"arXiv:2607.00001", "arXiv:2608.00002"})
        self.assertEqual(manifest["summary"]["support_holds"], 2)
        self.assertEqual(len(joined), 2)
        self.assertEqual({row["source_ref"] for row in joined}, {"arXiv:2607.00001", "arXiv:2608.00002"})
        self.assertNotIn("D", {row["candidate_id"] for row in targets})

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

    def test_portable_manifest_recovers_fulltext_only_endpoint_on_stale_receiver(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);canonical=self.storage(root/"canonical");receiver=self.storage(root/"receiver")
            design=self.design([self.hold("B","arXiv:2608.00002")])
            self.cache(canonical,"2608.00002",'<span>Project page: </span><a href="https://lab.github.io/ProjectX/">Project</a>',full=True)
            manifest_path=root/"portable.json";manifest_js=root/"portable.js"
            manifest=write_portable_release_target_manifest(design_state=design,storage=canonical,json_path=manifest_path,js_path=manifest_js)
            self.assertEqual(validate_portable_release_target_manifest(manifest),[])
            self.assertEqual(set(manifest["targets"][0]),{"candidate_id","source_ref","url","declaration_kind","primary_cache_sha256","scientific_authority"})
            state=run_support_release_watch(storage=receiver,design_state=design,portable_targets_path=manifest_path,max_primary_refreshes=0,fetcher=lambda target:{"status_code":200,"fingerprint":"a"*64,"surface_nonempty":True,"fingerprint_version":"release-surface-v2"},write_ledger=False)
        self.assertEqual(state["summary"]["explicit_release_targets"],1)
        self.assertEqual(state["summary"]["portable_release_targets_used"],1)
        self.assertEqual(state["summary"]["no_explicit_endpoint"],0)
        self.assertEqual(state["rows"][0]["status"],"BASELINE_CAPTURED")
        self.assertTrue(state["rows"][0]["portable_target"])
        self.assertIn("matched released",state["rows"][0]["required_unit"])
        self.assertEqual(state["summary"]["support_qualified"],0)
        self.assertEqual(state["summary"]["generator_reopen_authorized"],0)

    def test_invalid_portable_manifest_is_ignored_fail_closed(self) -> None:
        calls=[]
        def forbidden(target): calls.append(target); raise AssertionError("invalid manifest must not create target")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);receiver=self.storage(root/"receiver");manifest=root/"bad.json"
            manifest.write_text('{"schema_version":"1.0","manifest_sha256":"bad","scientific_authority":false,"targets":[{"candidate_id":"C","source_ref":"arXiv:2608.00003","url":"https://github.com/example/repo","declaration_kind":"PROJECT_PAGE","primary_cache_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","scientific_authority":false}]}',encoding="utf-8")
            state=run_support_release_watch(storage=receiver,design_state=self.design([self.hold("C","arXiv:2608.00003")]),portable_targets_path=manifest,max_primary_refreshes=0,fetcher=forbidden,write_ledger=False)
        self.assertEqual(calls,[])
        self.assertEqual(state["summary"]["portable_release_targets_used"],0)
        self.assertEqual(state["summary"]["no_explicit_endpoint"],1)

    def test_no_explicit_endpoint_does_not_query_release_surfaces_when_primary_refresh_disabled(self) -> None:
        calls = []
        def forbidden(target):
            calls.append(target)
            raise AssertionError("release-surface network forbidden")
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            self.cache(storage, "2608.00003", 'The code may be released after acceptance.')
            state = run_support_release_watch(storage=storage, design_state=self.design([self.hold("C", "arXiv:2608.00003")]), fetcher=forbidden, max_primary_refreshes=0, write_ledger=False)
        self.assertEqual(calls, [])
        self.assertEqual(state["summary"]["no_explicit_endpoint"], 1)
        self.assertEqual(state["summary"]["checked"], 0)
        self.assertEqual(state["summary"]["support_qualified"], 0)

    def test_primary_refresh_can_discover_new_author_release_declaration(self) -> None:
        primary_calls=[];release_calls=[]
        refreshed='<meta name="citation_title" content="Paper C"><blockquote class="abstract">Abstract: Agent evidence.</blockquote> Our code will be released at https://github.com/example/NewRelease .'
        def primary(url, **kwargs):
            primary_calls.append(url)
            return SimpleNamespace(status_code=200,text=refreshed,headers={})
        def release(target):
            release_calls.append(target["url"])
            return {"status_code":200,"fingerprint":"a"*64,"surface_nonempty":True,"artifact_file_count":2,"fingerprint_version":"release-surface-v2"}
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));self.cache(storage,"2608.00003",'<meta name="citation_title" content="Paper C"><blockquote class="abstract">Abstract: Agent evidence.</blockquote> No release link yet.')
            state=run_support_release_watch(storage=storage,design_state=self.design([self.hold("C","arXiv:2608.00003")]),primary_requester=primary,fetcher=release,now=datetime(2026,8,14,tzinfo=timezone.utc),write_ledger=False)
        self.assertEqual(len(primary_calls),1);self.assertEqual(release_calls,["https://github.com/example/NewRelease"])
        self.assertEqual(state["summary"]["primary_declaration_refresh_checked"],1)
        self.assertEqual(state["summary"]["primary_declaration_refresh_changed"],1)
        self.assertEqual(state["summary"]["explicit_release_targets"],1)
        self.assertEqual(state["summary"]["no_explicit_endpoint"],0)
        self.assertEqual(state["rows"][0]["status"],"RECHECK_REQUIRED_NEW_RELEASE_SURFACE")

    def test_primary_refresh_cooldown_prevents_repeat_arxiv_request(self) -> None:
        calls=[]
        refreshed='<meta name="citation_title" content="Paper C"><blockquote class="abstract">Abstract: Agent evidence.</blockquote> No endpoint.'
        def primary(url, **kwargs):
            calls.append(url);return SimpleNamespace(status_code=200,text=refreshed,headers={})
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));self.cache(storage,"2608.00003",refreshed);design=self.design([self.hold("C","arXiv:2608.00003")]);ledger=storage.data_root/"watch.json"
            run_support_release_watch(storage=storage,design_state=design,primary_requester=primary,max_primary_refreshes=1,now=datetime(2026,8,1,tzinfo=timezone.utc),ledger_path=ledger,fetcher=lambda target:(_ for _ in ()).throw(AssertionError("no release target")))
            second=run_support_release_watch(storage=storage,design_state=design,primary_requester=primary,max_primary_refreshes=1,now=datetime(2026,8,2,tzinfo=timezone.utc),ledger_path=ledger,fetcher=lambda target:(_ for _ in ()).throw(AssertionError("no release target")))
        self.assertEqual(len(calls),1);self.assertEqual(second["summary"]["primary_declaration_refresh_skipped_cooldown"],1)

    def test_primary_refresh_429_opens_shared_arxiv_circuit(self) -> None:
        calls=[]
        def limited(url, **kwargs):
            calls.append(url);return SimpleNamespace(status_code=429,text="",headers={"Retry-After":"600"})
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));self.cache(storage,"2608.00003",'<meta name="citation_title" content="Paper C"><blockquote class="abstract">Abstract: Agent evidence.</blockquote> No endpoint.');rate=storage.data_root/"rate.json"
            state=run_support_release_watch(storage=storage,design_state=self.design([self.hold("C","arXiv:2608.00003")]),primary_requester=limited,max_primary_refreshes=1,arxiv_rate_limit_state_path=rate,now=datetime(2026,8,14,tzinfo=timezone.utc),write_ledger=False)
            self.assertTrue(rate.exists())
        self.assertEqual(len(calls),1);self.assertGreaterEqual(state["summary"]["primary_declaration_refresh_rate_limited"],1);self.assertEqual(state["summary"]["checked"],0)

    def test_github_pages_project_fingerprint_uses_head_metadata_not_streaming_get(self) -> None:
        response=SimpleNamespace(status_code=200,url="https://lab.github.io/ProjectX/",headers={"ETag":"\"abc\"","Last-Modified":"Fri, 14 Aug 2026 01:49:29 GMT","Content-Length":"22720"})
        with patch("research_pipeline.paper_first_support_release_watch.requests.head",return_value=response) as head, patch("research_pipeline.paper_first_support_release_watch.requests.get") as get:
            result=watch._default_fetcher({"url":"https://lab.github.io/ProjectX/","declaration_kind":"PROJECT_PAGE"})
        self.assertEqual(result["status_code"],200)
        self.assertTrue(result["surface_nonempty"])
        self.assertEqual(result["fingerprint_version"],watch.FINGERPRINT_VERSION)
        self.assertEqual(len(result["fingerprint"]),64)
        head.assert_called_once();get.assert_not_called()

    def test_future_code_readme_only_surface_stays_waiting_for_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            self.cache(storage, "2607.00001", 'Our code will be made publicly available soon at https://github.com/example/FutureRepo .')
            state = run_support_release_watch(
                storage=storage,
                design_state=self.design([self.hold("A", "arXiv:2607.00001")]),
                fetcher=lambda target: {"status_code": 200, "fingerprint": "a" * 64, "surface_nonempty": False, "artifact_file_count": 0},
                now=datetime(2026, 8, 14, tzinfo=timezone.utc),
                write_ledger=False,
            )
        self.assertEqual(state["rows"][0]["status"], "WAITING_RELEASE_ARTIFACTS")
        self.assertEqual(state["summary"]["recheck_required"], 0)
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

    def test_public_summary_exposes_counts_not_release_urls_or_required_units(self) -> None:
        private={
            "schema_version":"1.0","status":"SUPPORT_RELEASE_WATCH_COMPLETE","scientific_authority":False,
            "summary":{"support_holds":4,"explicit_release_targets":2,"no_explicit_endpoint":2,"checked":2,"skipped_cooldown":0,"provider_errors":0,"recheck_required":0,"support_qualified":0,"generator_reopen_authorized":0,"problem_gate_authorized":0},
            "rows":[{"candidate_id":"SECRET","url":"https://github.com/private/repo","source_refs":["arXiv:secret"],"required_unit":"secret matched units","status":"WAITING_RELEASE_ARTIFACTS","scientific_authority":False}],
        }
        public=public_support_release_watch_summary(private)
        text=str(public)
        self.assertEqual(public["summary"]["support_holds"],4)
        self.assertEqual(public["status_counts"]["WAITING_RELEASE_ARTIFACTS"],1)
        self.assertNotIn("github.com",text);self.assertNotIn("arXiv:secret",text);self.assertNotIn("secret matched units",text);self.assertNotIn("SECRET",text)
        self.assertFalse(public["scientific_authority"])

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
