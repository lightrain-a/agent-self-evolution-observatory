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
    build_portable_release_observation_manifest,
    build_portable_release_observation_receipt,
    build_portable_release_target_manifest,
    explicit_release_targets,
    public_support_release_watch_summary,
    release_watch_contract_sha,
    run_support_release_watch,
    validate_portable_release_observation_manifest,
    validate_portable_release_observation_receipt,
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

    def test_effective_pre_f0_evidence_hold_is_watched_after_bounded_design_blocks(self) -> None:
        baseline="1"*40
        changed="2"*40
        snapshot="3"*64
        target={
            "source_ref":"arXiv:2608.15265",
            "url":"https://github.com/usail-hkust/VibeWorlding-Gym",
            "declaration_kind":"FIRST_PARTY_REPOSITORY",
            "baseline_revision":baseline,
            "scientific_authority":False,
        }
        contract_sha=release_watch_contract_sha(
            candidate_id="PORT-010",candidate_snapshot_sha256=snapshot,targets=[target],
            required_reopen_components=["query_units","per_case_outcomes"],
        )
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td));storage.site_artifact_dir.mkdir(parents=True,exist_ok=True)
            preflight={
                "schema_version":"1.0-shadow","run_id":"pre-f0-vwe","scientific_authority":False,
                "support_inventory_sha256":"a"*64,
                "authority":{"canonical_generator":False,"canonical_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
                "rows":[{
                    "candidate_id":"PORT-010","candidate_snapshot_sha256":snapshot,
                    "disposition":"HOLD_SUPPORT_UNAVAILABLE","scientific_authority":False,
                    "primary_refs":["arXiv:2608.15265"],
                    "required_unit":"VWE query units plus per-case target-model outcomes.",
                    "reopen_only_if":"Query units and per-case outcomes are both author-released.",
                    "bounded_first_party_evidence_design_allowed":True,
                    "next_route":"BOUNDED_EVIDENCE_DESIGN_OR_WAIT_PRIMARY_ASSET",
                }],
            }
            evidence={
                "scientific_authority":False,
                "entries":[{
                    "candidate_id":"PORT-010","candidate_snapshot_sha256":snapshot,
                    "status":"HOLD_EVIDENCE_REVIEW_BLOCKED","execution_authorized":False,"scientific_authority":False,
                    "release_watch_contract":{
                        "candidate_id":"PORT-010","candidate_snapshot_sha256":snapshot,
                        "targets":[target],"required_reopen_components":["query_units","per_case_outcomes"],
                        "contract_sha256":contract_sha,"scientific_authority":False,
                    },
                }],
            }
            (storage.site_artifact_dir/"paper-first-pre-f0-problem-falsifier-preflight.json").write_text(__import__("json").dumps(preflight),encoding="utf-8")
            (storage.site_artifact_dir/"paper-first-pre-f0-evidence-acquisition-plan.json").write_text(__import__("json").dumps(evidence),encoding="utf-8")
            targets,missing=explicit_release_targets(self.design([]),storage=storage)
            self.assertEqual(missing,[]);self.assertEqual(len(targets),1)
            self.assertEqual(targets[0]["baseline_revision"],baseline)
            self.assertEqual(targets[0]["endpoint_provenance_sha256"],contract_sha)
            self.assertEqual(targets[0]["declaration_context"],"durable-support-audit-first-party-repository")
            drift=run_support_release_watch(
                storage=storage,design_state=self.design([]),portable_targets_path=Path(td)/"missing-portable.json",
                fetcher=lambda target:{"status_code":200,"fingerprint":"4"*64,"surface_nonempty":True,"artifact_file_count":20,"resolved_revision":changed},
                now=datetime(2026,8,27,tzinfo=timezone.utc),write_ledger=False,
            )
            evidence["entries"][0]["release_watch_contract"]["contract_sha256"]="f"*64
            (storage.site_artifact_dir/"paper-first-pre-f0-evidence-acquisition-plan.json").write_text(__import__("json").dumps(evidence),encoding="utf-8")
            rejected,_=explicit_release_targets(self.design([]),storage=storage)
            self.assertEqual([row for row in rejected if row.get("candidate_id")=="PORT-010"],[])
        self.assertEqual(drift["rows"][0]["status"],"RECHECK_REQUIRED_RELEASE_CHANGED")
        self.assertEqual(drift["summary"]["support_holds"],1)
        self.assertEqual(drift["summary"]["recheck_required"],1)
        self.assertEqual(drift["summary"]["support_qualified"],0)
        self.assertFalse(drift["scientific_authority"])

    def test_pre_f0_release_change_only_repo_uses_audited_revision_without_portable_leak(self) -> None:
        baseline="6129934d53ea00ac306c14723874321dc3667246"
        changed="7"*40
        with tempfile.TemporaryDirectory() as td:
            storage=self.storage(Path(td))
            storage.site_artifact_dir.mkdir(parents=True,exist_ok=True)
            preflight={
                "schema_version":"1.0-shadow","run_id":"pre-f0-z1","scientific_authority":False,
                "support_inventory_sha256":"a"*64,
                "authority":{"canonical_generator":False,"canonical_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},
                "rows":[{
                    "candidate_id":"PORT-003","disposition":"HOLD_SUPPORT_UNAVAILABLE","scientific_authority":False,
                    "primary_refs":["arXiv:2608.09096","arXiv:2608.16590"],
                    "required_unit":"Frozen Zetta state with independent intermediate timescale arms.",
                    "reopen_only_if":"A first-party revision exposes native contract-valid intermediate arms.",
                    "support_audit_sha256":"b"*64,
                    "release_watch_targets":[{
                        "source_ref":"arXiv:2608.16590","url":"https://github.com/air-embodied-brain/Zetta-Embodiment",
                        "declaration_kind":"FIRST_PARTY_REPOSITORY","baseline_revision":baseline,"scientific_authority":False,
                    }],
                    "bounded_first_party_evidence_design_allowed":False,
                    "next_route":"WAIT_FIRST_PARTY_RELEASE_CHANGE",
                    "support_recheck_mode":"FIRST_PARTY_RELEASE_CHANGE_ONLY",
                }],
            }
            (storage.site_artifact_dir/"paper-first-pre-f0-problem-falsifier-preflight.json").write_text(__import__("json").dumps(preflight),encoding="utf-8")
            design=self.design([])
            targets,missing=explicit_release_targets(design,storage=storage)
            self.assertEqual(missing,[])
            self.assertEqual(len(targets),1)
            self.assertTrue(targets[0]["support_audited_target"])
            self.assertEqual(targets[0]["baseline_revision"],baseline)
            portable=build_portable_release_target_manifest(design,storage=storage)
            self.assertEqual(portable["targets"],[])
            self.assertEqual(portable["summary"]["explicit_release_targets"],0)

            same=run_support_release_watch(
                storage=storage,design_state=design,portable_targets_path=Path(td)/"missing-portable.json",
                fetcher=lambda target:{"status_code":200,"fingerprint":"c"*64,"surface_nonempty":True,"artifact_file_count":250,"resolved_revision":baseline},
                now=datetime(2026,8,19,tzinfo=timezone.utc),write_ledger=False,
            )
            drift=run_support_release_watch(
                storage=storage,design_state=design,portable_targets_path=Path(td)/"missing-portable.json",
                fetcher=lambda target:{"status_code":200,"fingerprint":"d"*64,"surface_nonempty":True,"artifact_file_count":251,"resolved_revision":changed},
                now=datetime(2026,8,20,tzinfo=timezone.utc),write_ledger=False,
            )
        self.assertEqual(same["rows"][0]["status"],"NO_RELEASE_CHANGE")
        self.assertEqual(same["summary"]["recheck_required"],0)
        self.assertEqual(drift["rows"][0]["status"],"RECHECK_REQUIRED_RELEASE_CHANGED")
        self.assertEqual(drift["summary"]["recheck_required"],1)
        for state in (same,drift):
            self.assertEqual(state["summary"]["support_holds"],1)
            self.assertEqual(state["summary"]["support_qualified"],0)
            self.assertEqual(state["summary"]["generator_reopen_authorized"],0)
            self.assertEqual(state["summary"]["problem_gate_authorized"],0)
            self.assertFalse(state["scientific_authority"])


    def test_huggingface_dataset_fetcher_uses_official_revision_and_file_manifest(self) -> None:
        revision = "1" * 40
        response = SimpleNamespace(
            status_code=200,
            json=lambda: {
                "sha": revision,
                "siblings": [
                    {"rfilename": "README.md"},
                    {"rfilename": "data/rl/train.parquet"},
                    {"rfilename": "data/test/001/query.json"},
                ],
            },
        )
        target = {
            "url": "https://huggingface.co/datasets/usail-hkust/VWE-Bench",
            "declaration_kind": "FIRST_PARTY_DATASET",
        }
        with patch.object(watch.requests, "get", return_value=response) as get:
            result = watch._default_fetcher(target)
        self.assertEqual(result["resolved_revision"], revision)
        self.assertEqual(result["artifact_file_count"], 3)
        self.assertTrue(result["surface_nonempty"])
        self.assertEqual(result["fingerprint_version"], watch.FINGERPRINT_VERSION)
        self.assertEqual(len(result["artifact_path_digest"]), 64)
        args, kwargs = get.call_args
        self.assertEqual(args[0], "https://huggingface.co/api/datasets/usail-hkust/VWE-Bench")
        self.assertEqual(kwargs["params"], {"full": "full"})
        self.assertTrue(watch._acceptable_release_url(target["url"]))
        self.assertFalse(watch._acceptable_release_url("https://huggingface.co/usail-hkust/VibeWorlder-8B"))

    def test_effective_pre_f0_hold_watches_huggingface_dataset_revision_without_authority(self) -> None:
        baseline = "1" * 40
        changed = "2" * 40
        snapshot = "3" * 64
        target = {
            "source_ref": "arXiv:2608.15265",
            "url": "https://huggingface.co/datasets/usail-hkust/VWE-Bench",
            "declaration_kind": "FIRST_PARTY_DATASET",
            "baseline_revision": baseline,
            "scientific_authority": False,
        }
        contract_sha = release_watch_contract_sha(
            candidate_id="PORT-010",
            candidate_snapshot_sha256=snapshot,
            targets=[target],
            required_reopen_components=["query_units", "per_case_outcomes"],
        )
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            storage.site_artifact_dir.mkdir(parents=True, exist_ok=True)
            preflight = {
                "schema_version": "1.0-shadow",
                "run_id": "pre-f0-vwe-hf",
                "scientific_authority": False,
                "support_inventory_sha256": "a" * 64,
                "authority": {"canonical_generator": False, "canonical_problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
                "rows": [{
                    "candidate_id": "PORT-010",
                    "candidate_snapshot_sha256": snapshot,
                    "disposition": "HOLD_SUPPORT_UNAVAILABLE",
                    "scientific_authority": False,
                    "primary_refs": ["arXiv:2608.15265"],
                    "required_unit": "VWE query units plus per-case target-model outcomes.",
                    "reopen_only_if": "Query units and per-case outcomes are both author-released.",
                    "bounded_first_party_evidence_design_allowed": True,
                    "next_route": "BOUNDED_EVIDENCE_DESIGN_OR_WAIT_PRIMARY_ASSET",
                }],
            }
            evidence = {
                "scientific_authority": False,
                "entries": [{
                    "candidate_id": "PORT-010",
                    "candidate_snapshot_sha256": snapshot,
                    "status": "HOLD_EVIDENCE_REVIEW_BLOCKED",
                    "execution_authorized": False,
                    "scientific_authority": False,
                    "release_watch_contract": {
                        "candidate_id": "PORT-010",
                        "candidate_snapshot_sha256": snapshot,
                        "targets": [target],
                        "required_reopen_components": ["query_units", "per_case_outcomes"],
                        "contract_sha256": contract_sha,
                        "scientific_authority": False,
                    },
                }],
            }
            (storage.site_artifact_dir / "paper-first-pre-f0-problem-falsifier-preflight.json").write_text(__import__("json").dumps(preflight), encoding="utf-8")
            (storage.site_artifact_dir / "paper-first-pre-f0-evidence-acquisition-plan.json").write_text(__import__("json").dumps(evidence), encoding="utf-8")
            targets, missing = explicit_release_targets(self.design([]), storage=storage)
            self.assertEqual(missing, [])
            self.assertEqual(len(targets), 1)
            self.assertEqual(targets[0]["declaration_kind"], "FIRST_PARTY_DATASET")
            self.assertEqual(targets[0]["declaration_context"], "durable-support-audit-first-party-dataset")
            self.assertEqual(targets[0]["baseline_revision"], baseline)
            same = run_support_release_watch(
                storage=storage,
                design_state=self.design([]),
                portable_targets_path=Path(td) / "missing-portable.json",
                fetcher=lambda _: {"status_code": 200, "fingerprint": "c" * 64, "surface_nonempty": True, "artifact_file_count": 300, "resolved_revision": baseline},
                now=datetime(2026, 8, 28, tzinfo=timezone.utc),
                write_ledger=False,
            )
            drift = run_support_release_watch(
                storage=storage,
                design_state=self.design([]),
                portable_targets_path=Path(td) / "missing-portable.json",
                fetcher=lambda _: {"status_code": 200, "fingerprint": "d" * 64, "surface_nonempty": True, "artifact_file_count": 301, "resolved_revision": changed},
                now=datetime(2026, 8, 29, tzinfo=timezone.utc),
                write_ledger=False,
            )
        self.assertEqual(same["rows"][0]["status"], "NO_RELEASE_CHANGE")
        self.assertEqual(drift["rows"][0]["status"], "RECHECK_REQUIRED_RELEASE_CHANGED")
        self.assertEqual(same["summary"]["support_qualified"], 0)
        self.assertEqual(drift["summary"]["support_qualified"], 0)
        self.assertEqual(drift["summary"]["generator_reopen_authorized"], 0)
        self.assertEqual(drift["summary"]["problem_gate_authorized"], 0)
        self.assertFalse(same["scientific_authority"])
        self.assertFalse(drift["scientific_authority"])

    def test_support_audited_target_kind_must_match_endpoint_type(self) -> None:
        baseline = "1" * 40
        snapshot = "3" * 64
        bad_targets = [
            {"source_ref": "arXiv:2608.15265", "url": "https://github.com/usail-hkust/VibeWorlding-Gym", "declaration_kind": "FIRST_PARTY_DATASET", "baseline_revision": baseline, "scientific_authority": False},
            {"source_ref": "arXiv:2608.15265", "url": "https://huggingface.co/datasets/usail-hkust/VWE-Bench", "declaration_kind": "FIRST_PARTY_REPOSITORY", "baseline_revision": baseline, "scientific_authority": False},
        ]
        contract_sha = release_watch_contract_sha(
            candidate_id="PORT-010",
            candidate_snapshot_sha256=snapshot,
            targets=bad_targets,
            required_reopen_components=["query_units", "per_case_outcomes"],
        )
        with tempfile.TemporaryDirectory() as td:
            storage = self.storage(Path(td))
            storage.site_artifact_dir.mkdir(parents=True, exist_ok=True)
            preflight = {
                "schema_version": "1.0-shadow", "run_id": "pre-f0-kind-mismatch", "scientific_authority": False,
                "support_inventory_sha256": "a" * 64,
                "authority": {"canonical_generator": False, "canonical_problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
                "rows": [{"candidate_id": "PORT-010", "candidate_snapshot_sha256": snapshot, "disposition": "HOLD_SUPPORT_UNAVAILABLE", "scientific_authority": False, "primary_refs": ["arXiv:2608.15265"], "required_unit": "outcomes", "reopen_only_if": "author release", "bounded_first_party_evidence_design_allowed": True, "next_route": "BOUNDED_EVIDENCE_DESIGN_OR_WAIT_PRIMARY_ASSET"}],
            }
            evidence = {"scientific_authority": False, "entries": [{"candidate_id": "PORT-010", "candidate_snapshot_sha256": snapshot, "status": "HOLD_EVIDENCE_REVIEW_BLOCKED", "execution_authorized": False, "scientific_authority": False, "release_watch_contract": {"candidate_id": "PORT-010", "candidate_snapshot_sha256": snapshot, "targets": bad_targets, "required_reopen_components": ["query_units", "per_case_outcomes"], "contract_sha256": contract_sha, "scientific_authority": False}}]}
            (storage.site_artifact_dir / "paper-first-pre-f0-problem-falsifier-preflight.json").write_text(__import__("json").dumps(preflight), encoding="utf-8")
            (storage.site_artifact_dir / "paper-first-pre-f0-evidence-acquisition-plan.json").write_text(__import__("json").dumps(evidence), encoding="utf-8")
            targets, _ = explicit_release_targets(self.design([]), storage=storage)
        self.assertEqual(targets, [])


    def _portable_observation_fixture(self, root: Path, *, baseline: str = "1" * 40, contract_salt: str = ""):
        storage = self.storage(root)
        storage.site_artifact_dir.mkdir(parents=True, exist_ok=True)
        snapshot = "3" * 64
        target = {
            "source_ref": "arXiv:2608.15265",
            "url": "https://huggingface.co/datasets/usail-hkust/VWE-Bench",
            "declaration_kind": "FIRST_PARTY_DATASET",
            "baseline_revision": baseline,
            "scientific_authority": False,
        }
        contract_sha = release_watch_contract_sha(
            candidate_id="PORT-010",
            candidate_snapshot_sha256=snapshot,
            targets=[target],
            required_reopen_components=["query_units", "per_case_outcomes"],
        )
        preflight = {
            "schema_version": "1.0-shadow",
            "run_id": "pre-f0-portable-observation" + contract_salt,
            "scientific_authority": False,
            "support_inventory_sha256": "a" * 64,
            "authority": {"canonical_generator": False, "canonical_problem_gate": False, "paper_design": False, "method": False, "experiment": False, "p0": False, "gpu": False},
            "rows": [{
                "candidate_id": "PORT-010",
                "candidate_snapshot_sha256": snapshot,
                "disposition": "HOLD_SUPPORT_UNAVAILABLE",
                "scientific_authority": False,
                "primary_refs": ["arXiv:2608.15265"],
                "required_unit": "VWE query units plus per-case outcomes.",
                "reopen_only_if": "Both are author-released and content-addressed.",
                "bounded_first_party_evidence_design_allowed": True,
                "next_route": "BOUNDED_EVIDENCE_DESIGN_OR_WAIT_PRIMARY_ASSET",
            }],
        }
        evidence = {
            "scientific_authority": False,
            "entries": [{
                "candidate_id": "PORT-010",
                "candidate_snapshot_sha256": snapshot,
                "status": "HOLD_EVIDENCE_REVIEW_BLOCKED",
                "execution_authorized": False,
                "scientific_authority": False,
                "release_watch_contract": {
                    "candidate_id": "PORT-010",
                    "candidate_snapshot_sha256": snapshot,
                    "targets": [target],
                    "required_reopen_components": ["query_units", "per_case_outcomes"],
                    "contract_sha256": contract_sha,
                    "scientific_authority": False,
                },
            }],
        }
        (storage.site_artifact_dir / "paper-first-pre-f0-problem-falsifier-preflight.json").write_text(__import__("json").dumps(preflight), encoding="utf-8")
        (storage.site_artifact_dir / "paper-first-pre-f0-evidence-acquisition-plan.json").write_text(__import__("json").dumps(evidence), encoding="utf-8")
        targets, missing = explicit_release_targets(self.design([]), storage=storage)
        self.assertEqual(missing, [])
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]["candidate_snapshot_sha256"], snapshot)
        self.assertEqual(targets[0]["endpoint_provenance_sha256"], contract_sha)
        return storage, targets[0]

    def test_portable_release_observation_same_revision_uses_same_watch_logic_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            storage, target = self._portable_observation_fixture(root)
            observed_at = datetime(2026, 8, 28, 2, 0, tzinfo=timezone.utc)
            receipt = build_portable_release_observation_receipt(
                target=target,
                result={
                    "status_code": 200,
                    "fingerprint": "b" * 64,
                    "surface_nonempty": True,
                    "artifact_file_count": 300,
                    "artifact_path_digest": "c" * 64,
                    "resolved_revision": target["baseline_revision"],
                    "fingerprint_version": watch.FINGERPRINT_VERSION,
                },
                checked_at=observed_at,
            )
            manifest = build_portable_release_observation_manifest([receipt])
            manifest_path = root / "portable-observations.json"
            manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")
            calls = []
            def forbidden_fetcher(_):
                calls.append(True)
                raise AssertionError("receiver must not refetch a matched portable observation")
            state = run_support_release_watch(
                storage=storage,
                design_state=self.design([]),
                portable_targets_path=root / "missing-targets.json",
                portable_observations_path=manifest_path,
                fetcher=forbidden_fetcher,
                now=datetime(2026, 8, 28, 3, 0, tzinfo=timezone.utc),
                write_ledger=False,
            )
        self.assertEqual(calls, [])
        self.assertEqual(state["rows"][0]["status"], "NO_RELEASE_CHANGE")
        self.assertEqual(state["rows"][0]["observation_source"], "PORTABLE_ZERO_AUTHORITY_RELEASE_OBSERVATION")
        self.assertEqual(state["rows"][0]["checked_at"], observed_at.isoformat())
        self.assertEqual(state["summary"]["portable_release_observations_used"], 1)
        self.assertEqual(state["summary"]["recheck_required"], 0)
        self.assertEqual(state["summary"]["support_qualified"], 0)
        self.assertEqual(state["summary"]["problem_gate_authorized"], 0)
        self.assertFalse(state["scientific_authority"])

    def test_portable_release_observation_revision_drift_requests_recheck_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            storage, target = self._portable_observation_fixture(root)
            receipt = build_portable_release_observation_receipt(
                target=target,
                result={
                    "status_code": 200,
                    "fingerprint": "d" * 64,
                    "surface_nonempty": True,
                    "artifact_file_count": 301,
                    "artifact_path_digest": "e" * 64,
                    "resolved_revision": "2" * 40,
                    "fingerprint_version": watch.FINGERPRINT_VERSION,
                },
                checked_at=datetime(2026, 8, 29, tzinfo=timezone.utc),
            )
            manifest = build_portable_release_observation_manifest([receipt])
            manifest_path = root / "portable-observations.json"
            manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")
            state = run_support_release_watch(
                storage=storage,
                design_state=self.design([]),
                portable_targets_path=root / "missing-targets.json",
                portable_observations_path=manifest_path,
                fetcher=lambda _: (_ for _ in ()).throw(AssertionError("portable observation should be consumed")),
                now=datetime(2026, 8, 29, 1, 0, tzinfo=timezone.utc),
                write_ledger=False,
            )
        self.assertEqual(state["rows"][0]["status"], "RECHECK_REQUIRED_RELEASE_CHANGED")
        self.assertEqual(state["summary"]["portable_release_observations_used"], 1)
        self.assertEqual(state["summary"]["recheck_required"], 1)
        self.assertEqual(state["summary"]["support_qualified"], 0)
        self.assertEqual(state["summary"]["generator_reopen_authorized"], 0)
        self.assertEqual(state["summary"]["problem_gate_authorized"], 0)
        self.assertFalse(state["scientific_authority"])

    def test_stale_contract_portable_observation_is_rejected_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            storage, target = self._portable_observation_fixture(root)
            stale_target = dict(target)
            stale_target["endpoint_provenance_sha256"] = "f" * 64
            receipt = build_portable_release_observation_receipt(
                target=stale_target,
                result={
                    "status_code": 200,
                    "fingerprint": "d" * 64,
                    "surface_nonempty": True,
                    "artifact_file_count": 301,
                    "artifact_path_digest": "e" * 64,
                    "resolved_revision": "2" * 40,
                    "fingerprint_version": watch.FINGERPRINT_VERSION,
                },
                checked_at=datetime(2026, 8, 29, tzinfo=timezone.utc),
            )
            manifest = build_portable_release_observation_manifest([receipt])
            manifest_path = root / "portable-observations.json"
            manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")
            state = run_support_release_watch(
                storage=storage,
                design_state=self.design([]),
                portable_targets_path=root / "missing-targets.json",
                portable_observations_path=manifest_path,
                fetcher=lambda _: (_ for _ in ()).throw(RuntimeError("network unavailable")),
                now=datetime(2026, 8, 29, 1, 0, tzinfo=timezone.utc),
                write_ledger=False,
            )
        self.assertEqual(state["summary"]["portable_release_observations_used"], 0)
        self.assertEqual(state["summary"]["portable_release_observations_rejected"], 1)
        self.assertEqual(state["summary"]["provider_errors"], 1)
        self.assertEqual(state["summary"]["recheck_required"], 0)
        self.assertEqual(state["summary"]["support_qualified"], 0)
        self.assertEqual(state["rows"][0]["status"], "RELEASE_WATCH_PROVIDER_ERROR")
        self.assertFalse(state["scientific_authority"])

    def test_portable_release_observation_cannot_self_authorize_or_assert_science(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, target = self._portable_observation_fixture(root)
            receipt = build_portable_release_observation_receipt(
                target=target,
                result={
                    "status_code": 200,
                    "fingerprint": "b" * 64,
                    "surface_nonempty": True,
                    "artifact_file_count": 300,
                    "resolved_revision": target["baseline_revision"],
                    "fingerprint_version": watch.FINGERPRINT_VERSION,
                },
                checked_at=datetime(2026, 8, 28, tzinfo=timezone.utc),
            )
            receipt["authority"]["scientific"] = True
            receipt["scientific_release"] = "RELEASED"
            errors = validate_portable_release_observation_receipt(receipt)
        self.assertTrue(any("non-zero authority" in error for error in errors))
        self.assertTrue(any("scientific decision fields" in error for error in errors))
        self.assertTrue(any("receipt digest mismatch" in error for error in errors))
        manifest_errors = validate_portable_release_observation_manifest({
            "schema_version": watch.PORTABLE_OBSERVATIONS_SCHEMA,
            "scientific_authority": False,
            "policy": {"scientific_authority": False},
            "receipts": [receipt],
            "manifest_sha256": "0" * 64,
        })
        self.assertTrue(manifest_errors)


if __name__ == "__main__":
    unittest.main()
