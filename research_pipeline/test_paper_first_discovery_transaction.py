from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from .config import StorageSettings
from .paper_first_discovery_transaction import close_existing_problem_discovery_transaction, recompile_existing_problem_discovery_transaction, recompile_primary_typed_evidence_with_generator_replay_transaction, _transaction_id, _transaction_lock, _transaction_lock_path, _validate, write_problem_discovery_transaction
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, DISCOVERY_OPERATOR_VERSION
from .paper_first_problem_generator import _pool_sha


class PaperFirstDiscoveryTransactionTest(unittest.TestCase):
    def storage(self, root: Path) -> StorageSettings:
        return StorageSettings(
            data_root=root/"data", corpus_dir=root/"data"/"corpora", dataset_dir=root/"data"/"datasets",
            paper_dir=root/"data"/"papers", index_dir=root/"data"/"indexes", run_dir=root/"data"/"runs",
            cache_dir=root/"data"/"cache", lock_dir=root/"data"/"locks", site_artifact_dir=root/"site",
        )

    def test_transaction_lock_is_host_shared_across_worktree_storage_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);left=self.storage(root/"left");right=self.storage(root/"right");shared=root/"host-paper-first.lock"
            with patch.dict(os.environ,{"PAPER_FIRST_DISCOVERY_TRANSACTION_LOCK":str(shared)}):
                self.assertEqual(_transaction_lock_path(left),_transaction_lock_path(right))
                with _transaction_lock(left):
                    with self.assertRaisesRegex(RuntimeError,"active on this host"):
                        with _transaction_lock(right):
                            self.fail("second worktree must not acquire the same transaction lock")

    def corpus(self, root: Path, now: datetime) -> Path:
        root.mkdir(parents=True,exist_ok=True);path=root/"corpus.json";papers=[]
        titles=(
            "Self-Evolving Agent Skill Harness Alpha",
            "Persistent Agent Memory Evolution Beta",
            "Embodied Self-Improving Agent Gamma",
            "Multi-Agent Harness Evolution Delta",
        )
        for idx,title in enumerate(titles,1):
            papers.append({
                "paper_id":f"s2-{idx}","title":title,"year":2026,"venue":"arXiv",
                "abstract":"We study self-evolving autonomous agents, persistent memory, skills, harnesses, and verified adaptation.",
                "metadata":{"externalIds":{"ArXiv":f"2608.40{idx:03d}"},"publicationDate":"2026-08-13","citationCount":0,"retrievalScore":1.0,"retrievedAt":now.isoformat(),"matches":[{"route":"test"}]},
            })
        path.write_text(json.dumps({"schema_version":"1.0","retrieved_at":now.isoformat(),"papers":papers}),encoding="utf-8")
        return path

    def requester(self, url: str, *, timeout: float, headers: dict[str,str]):
        arxiv_id=url.rsplit('/',1)[-1];idx=int(arxiv_id[-1]);titles=(
            "Self-Evolving Agent Skill Harness Alpha",
            "Persistent Agent Memory Evolution Beta",
            "Embodied Self-Improving Agent Gamma",
            "Multi-Agent Harness Evolution Delta",
        )
        if "/html/" in url:
            return SimpleNamespace(status_code=200,text=f'<html><body><section><h2>Results</h2><p>We find verified self-evolution improves held-out success by {10+idx}.0 percent across tasks.</p></section></body></html>')
        return SimpleNamespace(status_code=200,text=f'<meta name="citation_title" content="{titles[idx-1]}"><blockquote class="abstract mathjax">Abstract: Verified primary evidence for self-evolving agents and persistent adaptation {idx}.</blockquote>')

    def generator(self, *, prompt: str, model: str, max_output_tokens: int):
        lane_search=[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No current pair survives this lane search."} for lane in DISCOVERY_LANES]
        return {"text":json.dumps({"lane_search":lane_search,"candidates":[],"generation_notes":"No evidence-first discovery lane survives the current same-information and mature-theory vetoes."}),"resolved_model":"doubao-seed-evolving"}

    def targets(self, root: Path):
        public=root/"public";public.mkdir(parents=True,exist_ok=True)
        return {
            "primary_json":public/"primary.json","primary_js":public/"primary.js",
            "generator_json":public/"generator.json","generator_js":public/"generator.js",
            "queue_json":public/"queue.json","queue_js":public/"queue.js",
        }

    def run_txn(self, root: Path, storage: StorageSettings, targets: dict[str,Path], now: datetime):
        return write_problem_discovery_transaction(
            storage=storage,**targets,
            primary_kwargs={"corpus_path":self.corpus(root,now),"requester":self.requester,"augment_fresh_corpus_with_arxiv":False,"max_papers":4,"lane_floor":0,"coverage_anchor_count":0,"now":now,"min_interval_seconds":0},
            generator_kwargs={"generator_responder":self.generator,"now":now},
        )

    def test_success_commits_all_public_roles_with_one_transaction_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            result=self.run_txn(root,storage,targets,now)
            payloads=[json.loads(targets[key].read_text()) for key in ("primary_json","generator_json","queue_json")]
            discovery=storage.data_root/"paper-first-problem-discovery"
            private_pool=json.loads((discovery/"primary-evidence-pool.json").read_text())
            auto_inbox=json.loads((discovery/"auto-candidate-inbox.json").read_text())
            saturation=json.loads((discovery/"discovery-saturation-ledger.json").read_text())
        self.assertEqual(result["status"],"COMMITTED")
        ids={row["discovery_transaction_id"] for row in payloads};self.assertEqual(ids,{result["transaction_id"]})
        self.assertEqual([row["discovery_transaction_role"] for row in payloads],["primary","generator","queue"])
        self.assertEqual(payloads[0]["status"],"READY");self.assertEqual(payloads[0]["summary"]["verified"],4)
        self.assertEqual(payloads[1]["status"],"GENERATED_ZERO_CANDIDATES");self.assertEqual(payloads[1]["summary"]["generated"],0)
        self.assertEqual(payloads[2]["summary"]["submitted"],0)
        self.assertEqual([row["ref"] for row in private_pool["records"]],[row["ref"] for row in payloads[0]["records"]])
        self.assertEqual(auto_inbox["generator_run_id"],payloads[1]["run_id"])
        self.assertEqual(auto_inbox["status"],payloads[1]["status"])
        self.assertEqual(saturation["runs"][-1]["run_id"],payloads[1]["run_id"])
        self.assertEqual(saturation["runs"][-1]["status"],payloads[1]["status"])
        self.assertEqual(result["discovery_operator_version"],DISCOVERY_OPERATOR_VERSION)
        self.assertEqual(result["generator_receipt_run_id"],payloads[1]["run_id"])
        self.assertEqual(len(result["generator_receipt_sha256"]),64)
        self.assertEqual(result["generator_receipt_raw_sha256"],payloads[1]["raw_artifacts"]["generator"]["sha256"])
        self.assertEqual((result["generator_provider_calls_executed"],result["semantic_reviewer_calls_executed"]),(1,0))
        self.assertEqual(result["provider_calls_executed"],1)
        self.assertEqual(result["authority"],{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False})

    def test_close_existing_transaction_replays_exact_private_pool_without_rerunning_scheduler(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            first=self.run_txn(root,storage,targets,now)
            current_private=storage.data_root/"paper-first-problem-discovery"/"primary-evidence-pool.json"
            replay_source=root/"frozen-primary-replay.json";replay_source.write_bytes(current_private.read_bytes())
            source=json.loads(replay_source.read_text());source["generated_at"]="2026-08-12T00:00:00+00:00";replay_source.write_text(json.dumps(source),encoding="utf-8")
            for key in ("primary_json","generator_json","queue_json"):
                payload=json.loads(targets[key].read_text());payload.pop("discovery_transaction_id",None);payload.pop("discovery_transaction_role",None);targets[key].write_text(json.dumps(payload),encoding="utf-8")
            drift=json.loads(current_private.read_text());drift["records"][0]["ref"]="arXiv:drifted";current_private.write_text(json.dumps(drift),encoding="utf-8")
            result=close_existing_problem_discovery_transaction(storage=storage,**targets,private_pool_source=replay_source)
            payloads=[json.loads(targets[key].read_text()) for key in ("primary_json","generator_json","queue_json")]
            rebound=json.loads(current_private.read_text())
        self.assertEqual(first["status"],"COMMITTED")
        self.assertEqual(result["status"],"COMMITTED_EXISTING_CLOSED_STATE")
        self.assertEqual(result["provider_calls_executed"],0)
        self.assertEqual(result["source_scheduler_runs_executed"],0)
        self.assertEqual({row["discovery_transaction_id"] for row in payloads},{result["transaction_id"]})
        self.assertEqual([row["discovery_transaction_role"] for row in payloads],["primary","generator","queue"])
        self.assertEqual([row["ref"] for row in rebound["records"]],[row["ref"] for row in payloads[0]["records"]])
        self.assertEqual(rebound["generated_at"],payloads[0]["generated_at"])
        self.assertEqual((rebound.get("transaction_replay") or {}).get("mode"),"existing-closed-state-envelope")

    def test_close_existing_transaction_preserves_historical_operator_receipt_after_runtime_upgrade(self) -> None:
        historical_operator="fresh-phenomenon-treatment-aligned-v14"
        self.assertNotEqual(historical_operator,DISCOVERY_OPERATOR_VERSION)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            first=self.run_txn(root,storage,targets,now)
            generator=json.loads(targets["generator_json"].read_text());generator["policy"]["discovery_operator_version"]=historical_operator
            receipt=generator["saturation_memory"]["current_review_receipt"];receipt["discovery_operator_version"]=historical_operator
            targets["generator_json"].write_text(json.dumps(generator),encoding="utf-8")
            targets["generator_js"].write_text("window.PAPER_FIRST_PROBLEM_GENERATOR = "+json.dumps(generator,separators=(",",":"))+";\n",encoding="utf-8")
            ledger_path=storage.data_root/"paper-first-problem-discovery"/"discovery-saturation-ledger.json"
            ledger=json.loads(ledger_path.read_text())
            for row in ledger.get("runs") or []:
                if row.get("run_id")==generator["run_id"]:row["discovery_operator_version"]=historical_operator
            ledger_path.write_text(json.dumps(ledger),encoding="utf-8")
            for key in ("primary_json","generator_json","queue_json"):
                payload=json.loads(targets[key].read_text());payload.pop("discovery_transaction_id",None);payload.pop("discovery_transaction_role",None);targets[key].write_text(json.dumps(payload),encoding="utf-8")
            source=storage.data_root/"paper-first-problem-discovery"/"primary-evidence-pool.json"
            result=close_existing_problem_discovery_transaction(storage=storage,**targets,private_pool_source=source)
            rebound=json.loads(source.read_text());closed_generator=json.loads(targets["generator_json"].read_text())
        self.assertEqual(first["status"],"COMMITTED")
        self.assertEqual(result["status"],"COMMITTED_EXISTING_CLOSED_STATE")
        self.assertEqual(result["provider_calls_executed"],0)
        self.assertEqual(result["source_scheduler_runs_executed"],0)
        self.assertEqual(result["discovery_operator_version"],historical_operator)
        self.assertEqual(result["runtime_discovery_operator_version"],DISCOVERY_OPERATOR_VERSION)
        self.assertTrue(result["operator_version_replayed_without_provider"])
        self.assertEqual(result["generator_receipt_run_id"],closed_generator["run_id"])
        self.assertEqual(len(result["generator_receipt_sha256"]),64)
        replay=rebound["transaction_replay"]
        self.assertEqual(replay["discovery_operator_version"],historical_operator)
        self.assertEqual(replay["runtime_discovery_operator_version"],DISCOVERY_OPERATOR_VERSION)
        self.assertTrue(replay["operator_version_replayed_without_provider"])

    def test_transaction_id_binds_generator_operator_and_review_receipt(self) -> None:
        primary={"status":"READY","records":[{"ref":"arXiv:1","source_sha256":"a"*64,"fulltext_sha256":"b"*64}],"carrier_probe":{"pending":0,"portable_receipts":[]}}
        receipt={"run_id":"run-a","pool_sha256":"c"*64,"negative_space_sha256":"d"*64,"discovery_operator_version":"operator-v1","source_refs":["arXiv:1"],"status":"GENERATED_ZERO_CANDIDATES","requested_model":"model-a","resolved_model":"model-a","raw_sha256":"e"*64,"scientific_authority":False}
        generator={"run_id":"run-a","status":"GENERATED_ZERO_CANDIDATES","policy":{"discovery_operator_version":"operator-v1"},"saturation_memory":{"current_review_receipt":receipt},"raw_artifacts":{"generator":{"sha256":"e"*64}}}
        queue={"audited":[]}
        original=_transaction_id(primary,generator,queue)
        changed_operator=json.loads(json.dumps(generator));changed_operator["policy"]["discovery_operator_version"]="operator-v2"
        changed_receipt=json.loads(json.dumps(generator));changed_receipt["saturation_memory"]["current_review_receipt"]["raw_sha256"]="f"*64
        self.assertNotEqual(original,_transaction_id(primary,changed_operator,queue))
        self.assertNotEqual(original,_transaction_id(primary,changed_receipt,queue))

    def _downgrade_typed_evidence_fixture(self, storage: StorageSettings, targets: dict[str,Path]) -> tuple[Path,Path,int]:
        private=storage.data_root/"paper-first-problem-discovery"/"primary-evidence-pool.json"
        pool=json.loads(private.read_text());before_count=sum(len(((row.get("typed_evidence") or {}).get("measured_failures") or [])) for row in pool.get("records") or [])
        false_text="Long-horizon benchmarks reveal quality degradation and hidden-test failures across prior systems (17; 3; 10)."
        false_item={"section":"Long-horizon coding-agent evaluation","text":false_text,"text_sha256":__import__('hashlib').sha256(false_text.encode()).hexdigest(),"extraction_version":"typed-v1"}
        pool["typed_evidence_extraction_version"]="typed-v1"
        for row in pool.get("records") or []:row["typed_evidence_extraction_version"]="typed-v1"
        pool["records"][0].setdefault("typed_evidence",{}).setdefault("measured_failures",[]).append(false_item)
        private.write_text(json.dumps(pool),encoding="utf-8");old_pool_sha=_pool_sha(pool)
        primary=json.loads(targets["primary_json"].read_text());primary["policy"]["typed_evidence_extraction_version"]="typed-v1";primary["policy"].pop("typed_evidence_requires_first_party_ownership_or_nonliterature_attribution",None);primary["summary"]["typed_evidence_candidates"]["measured_failures"]+=1;primary["records"][0]["typed_evidence_counts"]["measured_failures"]+=1
        targets["primary_json"].write_text(json.dumps(primary),encoding="utf-8")
        generator=json.loads(targets["generator_json"].read_text());receipt=generator["saturation_memory"]["current_review_receipt"];receipt["pool_sha256"]=old_pool_sha
        for row in generator["saturation_memory"].get("portable_review_receipts") or []:
            if isinstance(row,dict) and row.get("run_id")==generator.get("run_id"):row["pool_sha256"]=old_pool_sha
        targets["generator_json"].write_text(json.dumps(generator),encoding="utf-8")
        ledger=storage.data_root/"paper-first-problem-discovery"/"discovery-saturation-ledger.json"
        if ledger.exists():
            payload=json.loads(ledger.read_text())
            for row in payload.get("runs") or []:
                if isinstance(row,dict) and row.get("run_id")==generator.get("run_id"):row["pool_sha256"]=old_pool_sha
            ledger.write_text(json.dumps(payload),encoding="utf-8")
        for key in ("primary_json","generator_json","queue_json"):
            payload=json.loads(targets[key].read_text());payload.pop("discovery_transaction_id",None);payload.pop("discovery_transaction_role",None);targets[key].write_text(json.dumps(payload),encoding="utf-8")
        close_existing_problem_discovery_transaction(storage=storage,**targets,private_pool_source=private)
        raw_sha=generator["raw_artifacts"]["generator"]["sha256"];raw_files=list((storage.data_root/"paper-first-problem-discovery"/"raw-generations").glob(f"*{raw_sha[:12]}*.txt"))
        if len(raw_files)!=1:raise AssertionError(f"expected one archived generator raw, found {raw_files}")
        return private,raw_files[0],before_count

    def test_typed_evidence_recompile_replays_archived_generator_with_zero_provider_calls(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            first=self.run_txn(root,storage,targets,now);private,raw_path,before_count=self._downgrade_typed_evidence_fixture(storage,targets);old_tx=json.loads(targets["primary_json"].read_text())["discovery_transaction_id"]
            result=recompile_primary_typed_evidence_with_generator_replay_transaction(storage=storage,**targets,private_pool_source=private,private_pool_target=private,fulltext_cache_dir=storage.data_root/"paper-first-problem-discovery"/"primary-sources",generator_raw_path=raw_path)
            primary=json.loads(targets["primary_json"].read_text());generator=json.loads(targets["generator_json"].read_text());queue=json.loads(targets["queue_json"].read_text());recompiled=json.loads(private.read_text())
        self.assertEqual(first["status"],"COMMITTED")
        self.assertEqual(result["status"],"COMMITTED_TYPED_EVIDENCE_RECOMPILE_ZERO_PROVIDER_REPLAY")
        self.assertEqual(result["provider_calls_executed"],0);self.assertEqual(result["generator_provider_calls_executed"],0);self.assertEqual(result["semantic_reviewer_calls_executed"],0)
        self.assertNotEqual(result["transaction_id"],old_tx)
        self.assertEqual(primary["policy"]["typed_evidence_extraction_version"],"typed-v2");self.assertTrue(primary["policy"]["typed_evidence_requires_first_party_ownership_or_nonliterature_attribution"])
        self.assertEqual(primary["summary"]["typed_evidence_candidates"]["measured_failures"],before_count)
        self.assertEqual(recompiled["typed_evidence_extraction_version"],"typed-v2");self.assertEqual((recompiled.get("derived_evidence_recompile") or {}).get("network_fetches_executed"),0)
        self.assertTrue(generator["policy"]["generator_replayed_without_provider"]);self.assertEqual(generator["status"],"GENERATED_ZERO_CANDIDATES")
        self.assertEqual(queue["summary"]["submitted"],0);self.assertEqual(queue["summary"]["passed_problem_gate"],0)
        self.assertEqual({primary["discovery_transaction_id"],generator["discovery_transaction_id"],queue["discovery_transaction_id"]},{result["transaction_id"]})

    def test_typed_evidence_recompile_replay_failure_preserves_previous_public_and_private_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            self.run_txn(root,storage,targets,now);private,raw_path,_=self._downgrade_typed_evidence_fixture(storage,targets);discovery=storage.data_root/"paper-first-problem-discovery";tracked={**targets,"private":private,"auto":discovery/"auto-candidate-inbox.json","ledger":discovery/"discovery-saturation-ledger.json"};before={key:path.read_bytes() for key,path in tracked.items() if path.exists()}
            with patch("research_pipeline.paper_first_discovery_transaction.write_replayed_problem_generator_state",side_effect=RuntimeError("replay-broken")):
                with self.assertRaisesRegex(RuntimeError,"replay-broken"):
                    recompile_primary_typed_evidence_with_generator_replay_transaction(storage=storage,**targets,private_pool_source=private,private_pool_target=private,fulltext_cache_dir=discovery/"primary-sources",generator_raw_path=raw_path)
            after={key:path.read_bytes() for key,path in tracked.items() if path.exists()};aborted=list((storage.run_dir/"paper-first-discovery-transactions").glob("aborted-typed-recompile-*.json"))
        self.assertEqual(after,before);self.assertTrue(aborted)

    def _downgrade_committed_operator_fixture(self, storage: StorageSettings, targets: dict[str,Path], *, old_operator: str = "fresh-phenomenon-anomaly-precision-v13") -> Path:
        generator=json.loads(targets["generator_json"].read_text());generator["policy"]["discovery_operator_version"]=old_operator
        saturation=generator.get("saturation_memory") or {}
        if isinstance(saturation.get("current_review_receipt"),dict):saturation["current_review_receipt"]["discovery_operator_version"]=old_operator
        for row in saturation.get("portable_review_receipts") or []:
            if isinstance(row,dict):row["discovery_operator_version"]=old_operator
        targets["generator_json"].write_text(json.dumps(generator),encoding="utf-8")
        targets["generator_js"].write_text("window.PAPER_FIRST_PROBLEM_GENERATOR = "+json.dumps(generator,separators=(",",":"))+";\n",encoding="utf-8")
        private=storage.data_root/"paper-first-problem-discovery"/"primary-evidence-pool.json"
        pool=json.loads(private.read_text())
        for row in (pool.get("source_coverage") or {}).get("portable_review_receipts") or []:
            if isinstance(row,dict):row["discovery_operator_version"]=old_operator
        private.write_text(json.dumps(pool),encoding="utf-8")
        ledger=storage.data_root/"paper-first-problem-discovery"/"discovery-saturation-ledger.json"
        if ledger.exists():
            payload=json.loads(ledger.read_text())
            for row in payload.get("runs") or []:
                if isinstance(row,dict):row["discovery_operator_version"]=old_operator
            ledger.write_text(json.dumps(payload),encoding="utf-8")
        return private

    def test_operator_recompile_reuses_exact_primary_without_source_scheduler(self) -> None:
        calls=[]
        def generator(**kwargs):
            calls.append("generator")
            return self.generator(**kwargs)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            first=self.run_txn(root,storage,targets,now)
            source=self._downgrade_committed_operator_fixture(storage,targets)
            before_primary=json.loads(targets["primary_json"].read_text())
            result=recompile_existing_problem_discovery_transaction(storage=storage,**targets,private_pool_source=source,generator_kwargs={"generator_responder":generator,"now":now+timedelta(hours=1)})
            primary=json.loads(targets["primary_json"].read_text());new_generator=json.loads(targets["generator_json"].read_text());queue=json.loads(targets["queue_json"].read_text());private=json.loads(source.read_text())
        self.assertEqual(first["status"],"COMMITTED")
        self.assertEqual(result["status"],"COMMITTED_OPERATOR_RECOMPILE")
        self.assertEqual(result["source_scheduler_runs_executed"],0)
        self.assertEqual(result["generator_provider_calls_executed"],1)
        self.assertEqual(result["semantic_reviewer_calls_executed"],0)
        self.assertEqual(calls,["generator"])
        self.assertNotEqual(result["transaction_id"],first["transaction_id"])
        self.assertEqual([row["ref"] for row in primary["records"]],[row["ref"] for row in before_primary["records"]])
        self.assertEqual([row["source_sha256"] for row in primary["records"]],[row["source_sha256"] for row in before_primary["records"]])
        self.assertEqual((new_generator.get("policy") or {}).get("discovery_operator_version"),DISCOVERY_OPERATOR_VERSION)
        self.assertEqual(new_generator["status"],"GENERATED_ZERO_CANDIDATES")
        self.assertEqual(queue["summary"]["submitted"],0)
        self.assertEqual({primary["discovery_transaction_id"],new_generator["discovery_transaction_id"],queue["discovery_transaction_id"]},{result["transaction_id"]})
        self.assertEqual((private.get("operator_recompile") or {}).get("source_scheduler_runs_executed"),0)
        self.assertEqual((private.get("operator_recompile") or {}).get("discovery_operator_version"),DISCOVERY_OPERATOR_VERSION)
        self.assertEqual(result["discovery_operator_version"],DISCOVERY_OPERATOR_VERSION)
        self.assertEqual(result["generator_receipt_run_id"],new_generator["run_id"])
        self.assertEqual(len(result["generator_receipt_sha256"]),64)
        self.assertEqual(result["generator_receipt_raw_sha256"],new_generator["raw_artifacts"]["generator"]["sha256"])

    def test_operator_recompile_refuses_same_operator_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            self.run_txn(root,storage,targets,now)
            source=storage.data_root/"paper-first-problem-discovery"/"primary-evidence-pool.json"
            with self.assertRaisesRegex(RuntimeError,"older discovery operator"):
                recompile_existing_problem_discovery_transaction(storage=storage,**targets,private_pool_source=source,generator_kwargs={"generator_responder":self.generator,"now":now+timedelta(hours=1)})

    def test_operator_recompile_failure_preserves_previous_public_and_private_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            self.run_txn(root,storage,targets,now);source=self._downgrade_committed_operator_fixture(storage,targets)
            discovery=storage.data_root/"paper-first-problem-discovery"
            tracked={**targets,"private":source,"auto":discovery/"auto-candidate-inbox.json","ledger":discovery/"discovery-saturation-ledger.json"}
            before={key:path.read_bytes() for key,path in tracked.items() if path.exists()}
            def broken(**kwargs):raise RuntimeError("operator-provider-down")
            with self.assertRaisesRegex(RuntimeError,"operator recompile transaction invalid"):
                recompile_existing_problem_discovery_transaction(storage=storage,**targets,private_pool_source=source,generator_kwargs={"generator_responder":broken,"now":now+timedelta(hours=1)})
            after={key:path.read_bytes() for key,path in tracked.items() if path.exists()}
            aborted=list((storage.run_dir/"paper-first-discovery-transactions").glob("aborted-recompile-*.json"))
        self.assertEqual(after,before)
        self.assertTrue(aborted)

    def test_generator_error_aborts_without_changing_public_or_private_control_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            for key,path in targets.items(): path.write_text(f"OLD-{key}\n",encoding="utf-8")
            discovery=storage.data_root/"paper-first-problem-discovery";discovery.mkdir(parents=True,exist_ok=True)
            private_paths={
                "private_pool":discovery/"primary-evidence-pool.json",
                "auto_inbox":discovery/"auto-candidate-inbox.json",
                "saturation_ledger":discovery/"discovery-saturation-ledger.json",
            }
            private_paths["private_pool"].write_text(json.dumps({"schema_version":"1.1","generated_at":"2026-08-12T00:00:00+00:00","status":"READY","records":[],"source_coverage":{"portable_review_receipts":[]}}),encoding="utf-8")
            private_paths["auto_inbox"].write_text(json.dumps({"schema_version":"2.0","generator_run_id":"committed-old-run","status":"GENERATED_ZERO_CANDIDATES","candidates":[]}),encoding="utf-8")
            private_paths["saturation_ledger"].write_text(json.dumps({"schema_version":"1.0","runs":[]}),encoding="utf-8")
            before={key:path.read_bytes() for key,path in {**targets,**private_paths}.items()}
            def bad_generator(**kwargs): raise RuntimeError("provider-down")
            with self.assertRaisesRegex(RuntimeError,"generator-did-not-complete-discovery-transaction"):
                write_problem_discovery_transaction(
                    storage=storage,**targets,
                    primary_kwargs={"corpus_path":self.corpus(root,now),"requester":self.requester,"augment_fresh_corpus_with_arxiv":False,"max_papers":4,"lane_floor":0,"coverage_anchor_count":0,"now":now,"min_interval_seconds":0},
                    generator_kwargs={"generator_responder":bad_generator,"now":now},
                )
            after={key:path.read_bytes() for key,path in {**targets,**private_paths}.items()}
            aborted=sorted((storage.run_dir/"paper-first-discovery-transactions").glob("aborted-*.json"),key=lambda path:path.stat().st_mtime,reverse=True)
            self.assertTrue(aborted)
            receipt=json.loads(aborted[0].read_text())
        self.assertEqual(after,before)
        diagnostics=receipt["stage_diagnostics"]
        self.assertEqual(diagnostics["primary_status"],"READY")
        self.assertEqual(diagnostics["primary_verified"],4)
        self.assertEqual(diagnostics["generator_status"],"GENERATOR_ERROR_ZERO_AUTHORITY")
        self.assertIn("provider-down",diagnostics["generator_error"])
        self.assertFalse(diagnostics["generator_raw_output_present"])
        self.assertEqual(diagnostics["generator_transport_attempts"],[])
        self.assertTrue(diagnostics["queue_reached"])
        self.assertEqual(diagnostics["queue_audited"],0)
        self.assertFalse(diagnostics["scientific_authority"])

    def test_source_coverage_saturation_commits_zero_call_transaction_atomically(self) -> None:
        calls=[]
        def forbidden_generator(**kwargs):
            calls.append(1); raise AssertionError("coverage-saturated transaction with a current-operator receipt must make zero model calls")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            corpus=self.corpus(root,now)
            first=write_problem_discovery_transaction(
                storage=storage,**targets,
                primary_kwargs={"corpus_path":corpus,"requester":self.requester,"augment_fresh_corpus_with_arxiv":False,"max_papers":4,"lane_floor":0,"coverage_anchor_count":1,"now":now,"min_interval_seconds":0},
                generator_kwargs={"generator_responder":self.generator,"now":now},
            )
            first_generator=json.loads(targets["generator_json"].read_text());first_run_id=first_generator["run_id"]
            result=write_problem_discovery_transaction(
                storage=storage,**targets,
                primary_kwargs={"corpus_path":corpus,"requester":self.requester,"augment_fresh_corpus_with_arxiv":False,"max_papers":4,"lane_floor":0,"coverage_anchor_count":1,"now":now+timedelta(minutes=1),"min_interval_seconds":0},
                generator_kwargs={"generator_responder":forbidden_generator,"reviewer_responder":forbidden_generator,"now":now+timedelta(minutes=1)},
            )
            primary=json.loads(targets["primary_json"].read_text());generator=json.loads(targets["generator_json"].read_text());queue=json.loads(targets["queue_json"].read_text())
        self.assertEqual(first["status"],"COMMITTED")
        self.assertEqual(calls,[])
        self.assertEqual(result["status"],"COMMITTED")
        self.assertEqual(generator["status"],"SKIPPED_SOURCE_COVERAGE_SATURATED")
        self.assertTrue(primary["summary"]["source_coverage_exhausted"])
        self.assertEqual(primary["summary"]["unreviewed_lane_linked_sources"],0)
        self.assertEqual(generator["summary"]["generated"],0)
        self.assertEqual((queue["summary"]["submitted"],queue["summary"]["audited"],queue["summary"]["passed_problem_gate"],queue["summary"]["blocked_problem_gate"]),(0,0,0,0))
        self.assertEqual({primary["discovery_transaction_id"],generator["discovery_transaction_id"],queue["discovery_transaction_id"]},{result["transaction_id"]})
        receipts=generator["saturation_memory"]["portable_review_receipts"]
        self.assertEqual(len(receipts),1);self.assertEqual(receipts[0]["run_id"],first_run_id);self.assertFalse(receipts[0]["scientific_authority"])
        self.assertEqual(result["summary"]["source_coverage_exhausted"],True)
        self.assertEqual(result["summary"]["unreviewed_lane_linked_sources"],0)
        self.assertEqual(result["authority"],{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False})

    def test_carrier_probe_pending_commits_atomic_zero_model_transaction(self) -> None:
        model_calls=[]
        def forbidden(**kwargs):model_calls.append(1);raise AssertionError("carrier pending transaction must not call generator/reviewer")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            titles={1:"Self-Evolving Agent Skill One",2:"Harness Evolution Agent Two",3:"Persistent Agent Memory Three",4:"Self-Evolving World Model Four",5:"Self-Evolving Autonomous Agent Strategy Alpha",6:"Self-Evolving Autonomous Agent Strategy Beta"}
            abstracts={idx:("A self-evolving agent skill harness improves adaptation." if idx<3 else ("Persistent agent memory improves a continual agent." if idx==3 else ("A self-evolving world model improves planning." if idx==4 else "A self-evolving autonomous agent iterates strategy from feedback."))) for idx in titles}
            papers=[{"paper_id":f"s2-{idx}","title":titles[idx],"year":2026,"abstract":abstracts[idx],"metadata":{"externalIds":{"ArXiv":f"2608.62{idx:03d}"},"publicationDate":f"2026-08-{14-idx:02d}","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]}} for idx in range(1,7)]
            corpus=root/"carrier-transaction-corpus.json";corpus.write_text(json.dumps({"schema_version":"1.0","retrieved_at":now.isoformat(),"papers":papers}),encoding="utf-8")
            discovery=storage.data_root/"paper-first-problem-discovery";discovery.mkdir(parents=True,exist_ok=True)
            refs=[f"arXiv:2608.62{i:03d}" for i in range(1,5)]
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"schema_version":"1.0","runs":[{"run_id":"prior-reviewed","pool_sha256":"a"*64,"negative_space_sha256":"b"*64,"source_refs":refs,"status":"GENERATED_ZERO_CANDIDATES","requested_model":"ark-code-latest","resolved_model":"doubao-seed-evolving","raw_sha256":"c"*64,"scientific_authority":False}]}),encoding="utf-8")
            def requester(url:str,*,timeout:float,headers:dict[str,str]):
                aid=url.rsplit('/',1)[-1];idx=int(aid[-1])
                if '/html/' in url:return SimpleNamespace(status_code=200,text='<html><body><section><h2>Experimental Results</h2><p>We find verified performance improves by 10.0 percent on held-out tasks.</p></section></body></html>')
                return SimpleNamespace(status_code=200,text=f'<meta name="citation_title" content="{titles[idx]}"><blockquote class="abstract mathjax">Abstract: {abstracts[idx]}</blockquote>')
            result=write_problem_discovery_transaction(storage=storage,**targets,primary_kwargs={"corpus_path":corpus,"requester":requester,"augment_fresh_corpus_with_arxiv":False,"max_papers":5,"lane_floor":0,"coverage_anchor_count":2,"carrier_probe_limit":1,"now":now,"min_interval_seconds":0},generator_kwargs={"generator_responder":forbidden,"reviewer_responder":forbidden,"now":now})
            primary=json.loads(targets["primary_json"].read_text());generator=json.loads(targets["generator_json"].read_text());queue=json.loads(targets["queue_json"].read_text())
        self.assertEqual(model_calls,[])
        self.assertEqual(result["status"],"COMMITTED")
        self.assertEqual(primary["schema_version"],"1.1")
        self.assertEqual((primary["summary"]["carrier_probe_rescued"],primary["summary"]["carrier_probe_pending"]),(0,1))
        self.assertFalse(primary["summary"]["source_coverage_exhausted"])
        self.assertEqual(generator["status"],"SKIPPED_SOURCE_CARRIER_PROBE_PENDING")
        self.assertEqual((queue["summary"]["submitted"],queue["summary"]["passed_problem_gate"]),(0,0))
        self.assertEqual({primary["discovery_transaction_id"],generator["discovery_transaction_id"],queue["discovery_transaction_id"]},{result["transaction_id"]})

    def test_validator_accepts_zero_call_retrieval_incomplete_transaction(self) -> None:
        refs=[f"arXiv:{idx}" for idx in range(1,5)]
        primary={"schema_version":"1.1","status":"READY","policy":{"scientific_object_lanes":["skill_harness","memory_continual","world_model","parametric_model_state"]},"summary":{"verified":4,"prior_reviewed_sources":4,"source_retrieval_complete":False,"unreviewed_lane_linked_sources":0,"carrier_probe_pending":0,"carrier_probe_complete":True},"carrier_probe":{"pending":0,"complete":True,"portable_receipts":[],"scientific_authority":False}}
        generator={"status":"SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE","summary":{"primary_evidence_records":4,"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0},"source_coverage":{"coverage_exhausted":False,"source_retrieval_complete":False,"unreviewed_lane_linked_sources":0,"carrier_probe_required":False,"carrier_probe_pending":0,"carrier_probe_complete":True},"saturation_memory":{"portable_review_receipts":[{"run_id":"prior","source_refs":refs,"scientific_authority":False}]},"policy":{"search_portfolio_enabled":False,"one_generator_call_max":True,"one_semantic_reviewer_call_max":True,"one_content_addressed_pool_allows_at_most_one_live_generator_call":True,"incomplete_retrieval_without_new_lane_source_skips_model_call":True,"retrieval_incomplete_is_compute_control_not_scientific_negative":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"candidates":[]}
        queue={"summary":{"primary_evidence_records":4,"submitted":0,"audited":0,"passed_problem_gate":0,"blocked_problem_gate":0,"inbox_errors":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0},"audited":[]}
        self.assertEqual(_validate(primary,generator,queue),[])

    def test_validator_accepts_primary_scope_exclusion_receipt_without_fulltext(self) -> None:
        refs=[f"arXiv:{idx}" for idx in range(1,5)]
        scope={"ref":"arXiv:scope","primary_sha256":"a"*64,"fulltext_sha256":"","classifier_version":"existing-object-carrier-v1","probe_outcome":"SCOPE_EXCLUDED_BY_PRIMARY","scope_exclusion_rule":"genetic-network-programming-non-llm-v1","live_rescue_eligible_lanes":[],"scientific_authority":False}
        primary={"schema_version":"1.1","status":"READY","policy":{"scientific_object_lanes":["skill_harness","memory_continual","world_model","parametric_model_state"]},"summary":{"verified":4,"prior_reviewed_sources":4,"source_retrieval_complete":False,"unreviewed_lane_linked_sources":0,"carrier_probe_pending":0,"carrier_probe_complete":True},"carrier_probe":{"pending":0,"complete":True,"portable_receipts":[scope],"scientific_authority":False}}
        generator={"status":"SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE","summary":{"primary_evidence_records":4,"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0},"source_coverage":{"coverage_exhausted":False,"source_retrieval_complete":False,"unreviewed_lane_linked_sources":0,"carrier_probe_required":False,"carrier_probe_pending":0,"carrier_probe_complete":True},"saturation_memory":{"portable_review_receipts":[{"run_id":"prior","source_refs":refs,"scientific_authority":False}]},"policy":{"search_portfolio_enabled":False,"one_generator_call_max":True,"one_semantic_reviewer_call_max":True,"one_content_addressed_pool_allows_at_most_one_live_generator_call":True,"incomplete_retrieval_without_new_lane_source_skips_model_call":True,"retrieval_incomplete_is_compute_control_not_scientific_negative":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"candidates":[]}
        queue={"summary":{"primary_evidence_records":4,"submitted":0,"audited":0,"passed_problem_gate":0,"blocked_problem_gate":0,"inbox_errors":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0},"audited":[]}
        self.assertEqual(_validate(primary,generator,queue),[])
        bad=json.loads(json.dumps(primary));bad["carrier_probe"]["portable_receipts"][0]["live_rescue_eligible_lanes"]=["memory_continual"]
        self.assertIn("primary-carrier-scope-exclusion-cannot-rescue",_validate(bad,generator,queue))

    def test_validator_accepts_zero_call_carrier_probe_pending_transaction(self) -> None:
        refs=[f"arXiv:{idx}" for idx in range(1,5)]
        primary={"schema_version":"1.1","status":"READY","policy":{"scientific_object_lanes":["skill_harness","memory_continual","world_model","parametric_model_state"]},"summary":{"verified":4,"prior_reviewed_sources":4,"source_retrieval_complete":True,"carrier_probe_pending":2,"carrier_probe_complete":False},"carrier_probe":{"pending":2,"complete":False,"portable_receipts":[],"scientific_authority":False}}
        generator={"status":"SKIPPED_SOURCE_CARRIER_PROBE_PENDING","summary":{"primary_evidence_records":4,"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0},"source_coverage":{"coverage_exhausted":False,"unreviewed_lane_linked_sources":0,"carrier_probe_required":True,"carrier_probe_pending":2,"carrier_probe_complete":False},"saturation_memory":{"portable_review_receipts":[{"run_id":"prior","source_refs":refs,"scientific_authority":False}]},"policy":{"search_portfolio_enabled":False,"one_generator_call_max":True,"one_semantic_reviewer_call_max":True,"one_content_addressed_pool_allows_at_most_one_live_generator_call":True,"carrier_probe_pending_skips_model_call":True,"carrier_probe_pending_is_compute_control_not_scientific_negative":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"candidates":[]}
        queue={"summary":{"primary_evidence_records":4,"submitted":0,"audited":0,"passed_problem_gate":0,"blocked_problem_gate":0,"inbox_errors":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0},"audited":[]}
        self.assertEqual(_validate(primary,generator,queue),[])

    def test_carrier_probe_receipt_changes_atomic_transaction_id_without_record_churn(self) -> None:
        base={"status":"READY","records":[{"ref":"arXiv:1","source_sha256":"a"*64,"fulltext_sha256":"b"*64}],"carrier_probe":{"pending":1,"portable_receipts":[]}}
        advanced=json.loads(json.dumps(base));advanced["carrier_probe"]={"pending":0,"portable_receipts":[{"ref":"arXiv:9","primary_sha256":"c"*64,"fulltext_sha256":"d"*64,"classifier_version":"existing-object-carrier-v1","live_rescue_eligible_lanes":[]}]}
        generator={"run_id":"same","status":"SKIPPED_SOURCE_CARRIER_PROBE_PENDING","raw_artifacts":{}}
        queue={"audited":[]}
        self.assertNotEqual(_transaction_id(base,generator,queue),_transaction_id(advanced,generator,queue))

    def test_validator_rejects_portfolio_as_canonical_transaction_generator(self) -> None:
        primary={"status":"READY","summary":{"verified":4}}
        generator={"schema_version":"3.2","status":"GENERATED_ZERO_CANDIDATES","summary":{"primary_evidence_records":4,"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0},"policy":{"search_portfolio_enabled":True,"one_generator_call_max":False,"one_semantic_reviewer_call_max":False,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"candidates":[]}
        queue={"summary":{"primary_evidence_records":4,"submitted":0,"audited":0,"passed_problem_gate":0,"blocked_problem_gate":0,"inbox_errors":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0},"audited":[]}
        errors=_validate(primary,generator,queue)
        self.assertIn("canonical-transaction-forbids-search-portfolio",errors)
        self.assertIn("canonical-transaction-requires-single-call-budget",errors)

    def test_validator_rejects_saturation_skip_when_unreviewed_lane_source_remains(self) -> None:
        primary={"status":"READY","summary":{"verified":4}}
        generator={"status":"SKIPPED_SOURCE_COVERAGE_SATURATED","summary":{"primary_evidence_records":4,"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0},"source_coverage":{"coverage_exhausted":True,"unreviewed_lane_linked_sources":1},"policy":{"source_coverage_saturation_skips_model_call":True,"source_coverage_saturation_is_compute_control_not_scientific_negative":True,"new_lane_grounded_primary_source_reopens_generation":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"candidates":[]}
        queue={"summary":{"primary_evidence_records":4,"submitted":0,"audited":0,"passed_problem_gate":0,"blocked_problem_gate":0,"inbox_errors":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0},"audited":[]}
        errors=_validate(primary,generator,queue)
        self.assertIn("coverage-skip-not-exhausted",errors)

    def test_validator_rejects_saturation_skip_when_retrieval_window_is_incomplete(self) -> None:
        primary={"status":"READY","summary":{"verified":4,"source_retrieval_complete":False}}
        generator={"status":"SKIPPED_SOURCE_COVERAGE_SATURATED","summary":{"primary_evidence_records":4,"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0},"source_coverage":{"coverage_exhausted":True,"unreviewed_lane_linked_sources":0},"policy":{"source_coverage_saturation_skips_model_call":True,"source_coverage_saturation_is_compute_control_not_scientific_negative":True,"new_lane_grounded_primary_source_reopens_generation":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"candidates":[]}
        queue={"summary":{"primary_evidence_records":4,"submitted":0,"audited":0,"passed_problem_gate":0,"blocked_problem_gate":0,"inbox_errors":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0},"audited":[]}
        errors=_validate(primary,generator,queue)
        self.assertIn("coverage-skip-retrieval-window-incomplete",errors)

    def test_validator_rejects_exhausted_transaction_with_incomplete_portable_receipts(self) -> None:
        primary={"status":"READY","summary":{"verified":4,"prior_reviewed_sources":4,"source_coverage_exhausted":True}}
        generator={"status":"SKIPPED_SOURCE_COVERAGE_SATURATED","summary":{"primary_evidence_records":4,"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0},"source_coverage":{"coverage_exhausted":True,"unreviewed_lane_linked_sources":0},"saturation_memory":{"portable_review_receipts":[{"run_id":"partial","source_refs":["arXiv:1","arXiv:2"],"scientific_authority":False}]},"policy":{"source_coverage_saturation_skips_model_call":True,"source_coverage_saturation_is_compute_control_not_scientific_negative":True,"new_lane_grounded_primary_source_reopens_generation":True,"primary_source_coverage_receipts_are_inherited_transactionally":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"candidates":[]}
        queue={"summary":{"primary_evidence_records":4,"submitted":0,"audited":0,"passed_problem_gate":0,"blocked_problem_gate":0,"inbox_errors":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0},"audited":[]}
        errors=_validate(primary,generator,queue)
        self.assertIn("coverage-skip-portable-receipts-incomplete",errors)

    def test_validator_rejects_v24_generated_state_without_complete_lane_search(self) -> None:
        primary={"status":"READY","summary":{"verified":4}}
        generator={"schema_version":"2.4","status":"GENERATED_ZERO_CANDIDATES","summary":{"primary_evidence_records":4,"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0},"search_diagnostics":{"lane_search_complete":False,"lane_search":[],"scientific_authority":False},"policy":{"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},"candidates":[]}
        queue={"summary":{"primary_evidence_records":4,"submitted":0,"audited":0,"passed_problem_gate":0,"blocked_problem_gate":0,"inbox_errors":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0},"audited":[]}
        self.assertIn("generator-lane-search-audit-incomplete",_validate(primary,generator,queue))

    def test_second_host_inherits_first_transaction_review_exposure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            first_storage=self.storage(root/"host-a");first=self.run_txn(root/"host-a",first_storage,targets,now)
            first_generator=json.loads(targets["generator_json"].read_text());first_run_id=first_generator["run_id"]
            second_storage=self.storage(root/"host-b");second=self.run_txn(root/"host-b",second_storage,targets,now+timedelta(minutes=1))
            primary=json.loads(targets["primary_json"].read_text());generator=json.loads(targets["generator_json"].read_text())
        self.assertNotEqual(first["transaction_id"],second["transaction_id"])
        self.assertEqual(primary["summary"]["portable_review_receipts_merged"],1)
        self.assertEqual(primary["summary"]["prior_reviewed_sources"],4)
        self.assertEqual(primary["summary"]["eligible_unreviewed"],0)
        self.assertTrue(primary["summary"]["source_coverage_exhausted"])
        self.assertEqual(generator["status"],"SKIPPED_SOURCE_COVERAGE_SATURATED")
        receipts=generator["saturation_memory"]["portable_review_receipts"]
        self.assertEqual(len(receipts),1);self.assertEqual(receipts[0]["run_id"],first_run_id)
        self.assertTrue(all(row["scientific_authority"] is False for row in receipts))
        self.assertEqual(second["summary"]["generated"],0)
        self.assertEqual(second["summary"]["queue_submitted"],0)


if __name__=="__main__":unittest.main()
