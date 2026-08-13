from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from .config import StorageSettings
from .paper_first_discovery_transaction import _validate, write_problem_discovery_transaction
from .paper_first_problem_discovery_contract import DISCOVERY_LANES


class PaperFirstDiscoveryTransactionTest(unittest.TestCase):
    def storage(self, root: Path) -> StorageSettings:
        return StorageSettings(
            data_root=root/"data", corpus_dir=root/"data"/"corpora", dataset_dir=root/"data"/"datasets",
            paper_dir=root/"data"/"papers", index_dir=root/"data"/"indexes", run_dir=root/"data"/"runs",
            cache_dir=root/"data"/"cache", lock_dir=root/"data"/"locks", site_artifact_dir=root/"site",
        )

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
        self.assertEqual(result["status"],"COMMITTED")
        ids={row["discovery_transaction_id"] for row in payloads};self.assertEqual(ids,{result["transaction_id"]})
        self.assertEqual([row["discovery_transaction_role"] for row in payloads],["primary","generator","queue"])
        self.assertEqual(payloads[0]["status"],"READY");self.assertEqual(payloads[0]["summary"]["verified"],4)
        self.assertEqual(payloads[1]["status"],"GENERATED_ZERO_CANDIDATES");self.assertEqual(payloads[1]["summary"]["generated"],0)
        self.assertEqual(payloads[2]["summary"]["submitted"],0)
        self.assertEqual(result["authority"],{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False})

    def test_generator_error_aborts_without_changing_any_public_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            for key,path in targets.items(): path.write_text(f"OLD-{key}\n",encoding="utf-8")
            before={key:path.read_bytes() for key,path in targets.items()}
            def bad_generator(**kwargs): raise RuntimeError("provider-down")
            with self.assertRaisesRegex(RuntimeError,"generator-did-not-complete-discovery-transaction"):
                write_problem_discovery_transaction(
                    storage=storage,**targets,
                    primary_kwargs={"corpus_path":self.corpus(root,now),"requester":self.requester,"augment_fresh_corpus_with_arxiv":False,"max_papers":4,"lane_floor":0,"coverage_anchor_count":0,"now":now,"min_interval_seconds":0},
                    generator_kwargs={"generator_responder":bad_generator,"now":now},
                )
            after={key:path.read_bytes() for key,path in targets.items()}
        self.assertEqual(after,before)

    def test_source_coverage_saturation_commits_zero_call_transaction_atomically(self) -> None:
        calls=[]
        def forbidden_generator(**kwargs):
            calls.append(1); raise AssertionError("coverage-saturated transaction must make zero model calls")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            corpus=self.corpus(root,now)
            refs=[f"arXiv:2608.40{idx:03d}" for idx in range(1,5)]
            discovery=storage.data_root/"paper-first-problem-discovery";discovery.mkdir(parents=True,exist_ok=True)
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"schema_version":"1.0","runs":[{"run_id":"prior-reviewed-pool","pool_sha256":"a"*64,"negative_space_sha256":"b"*64,"source_refs":refs,"status":"GENERATED_ZERO_CANDIDATES","requested_model":"ark-code-latest","resolved_model":"doubao-seed-evolving","raw_sha256":"c"*64,"scientific_authority":False}]}),encoding="utf-8")
            result=write_problem_discovery_transaction(
                storage=storage,**targets,
                primary_kwargs={"corpus_path":corpus,"requester":self.requester,"augment_fresh_corpus_with_arxiv":False,"max_papers":4,"lane_floor":0,"coverage_anchor_count":1,"now":now,"min_interval_seconds":0},
                generator_kwargs={"generator_responder":forbidden_generator,"reviewer_responder":forbidden_generator,"now":now},
            )
            primary=json.loads(targets["primary_json"].read_text());generator=json.loads(targets["generator_json"].read_text());queue=json.loads(targets["queue_json"].read_text())
        self.assertEqual(calls,[])
        self.assertEqual(result["status"],"COMMITTED")
        self.assertEqual(generator["status"],"SKIPPED_SOURCE_COVERAGE_SATURATED")
        self.assertTrue(primary["summary"]["source_coverage_exhausted"])
        self.assertEqual(primary["summary"]["unreviewed_lane_linked_sources"],0)
        self.assertEqual(generator["summary"]["generated"],0)
        self.assertEqual((queue["summary"]["submitted"],queue["summary"]["audited"],queue["summary"]["passed_problem_gate"],queue["summary"]["blocked_problem_gate"]),(0,0,0,0))
        self.assertEqual({primary["discovery_transaction_id"],generator["discovery_transaction_id"],queue["discovery_transaction_id"]},{result["transaction_id"]})
        receipts=generator["saturation_memory"]["portable_review_receipts"]
        self.assertEqual(len(receipts),1);self.assertEqual(receipts[0]["run_id"],"prior-reviewed-pool");self.assertFalse(receipts[0]["scientific_authority"])
        self.assertEqual(result["summary"]["source_coverage_exhausted"],True)
        self.assertEqual(result["summary"]["unreviewed_lane_linked_sources"],0)
        self.assertEqual(result["authority"],{"paper":False,"method":False,"experiment":False,"p0":False,"gpu":False})

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
