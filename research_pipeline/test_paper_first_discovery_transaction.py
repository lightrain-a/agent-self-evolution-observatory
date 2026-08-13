from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from .config import StorageSettings
from .paper_first_discovery_transaction import write_problem_discovery_transaction


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
        return {"text":json.dumps({"candidates":[],"generation_notes":"No evidence-first discovery lane survives the current same-information and mature-theory vetoes."}),"resolved_model":"doubao-seed-evolving"}

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
            with self.assertRaisesRegex(RuntimeError,"generator-did-not-complete-scientific-run"):
                write_problem_discovery_transaction(
                    storage=storage,**targets,
                    primary_kwargs={"corpus_path":self.corpus(root,now),"requester":self.requester,"augment_fresh_corpus_with_arxiv":False,"max_papers":4,"lane_floor":0,"coverage_anchor_count":0,"now":now,"min_interval_seconds":0},
                    generator_kwargs={"generator_responder":bad_generator,"now":now},
                )
            after={key:path.read_bytes() for key,path in targets.items()}
        self.assertEqual(after,before)

    def test_second_host_inherits_first_transaction_review_exposure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);targets=self.targets(root);now=datetime(2026,8,13,12,0,tzinfo=timezone.utc)
            first_storage=self.storage(root/"host-a");first=self.run_txn(root/"host-a",first_storage,targets,now)
            second_storage=self.storage(root/"host-b");second=self.run_txn(root/"host-b",second_storage,targets,now+timedelta(minutes=1))
            primary=json.loads(targets["primary_json"].read_text());generator=json.loads(targets["generator_json"].read_text())
        self.assertNotEqual(first["transaction_id"],second["transaction_id"])
        self.assertEqual(primary["summary"]["portable_review_receipts_merged"],1)
        self.assertEqual(primary["summary"]["prior_reviewed_sources"],4)
        self.assertEqual(primary["summary"]["eligible_unreviewed"],0)
        receipts=generator["saturation_memory"]["portable_review_receipts"]
        self.assertEqual(len(receipts),2);self.assertEqual(len({row["run_id"] for row in receipts}),2)
        self.assertTrue(all(row["scientific_authority"] is False for row in receipts))


if __name__=="__main__":unittest.main()
