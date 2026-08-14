from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from .config import StorageSettings
from .paper_first_carrier_preview import run_carrier_preview


class PaperFirstCarrierPreviewTest(unittest.TestCase):
    def storage(self, root: Path) -> StorageSettings:
        return StorageSettings(
            data_root=root / "data",
            corpus_dir=root / "data" / "corpora",
            dataset_dir=root / "data" / "datasets",
            paper_dir=root / "data" / "papers",
            index_dir=root / "data" / "indexes",
            run_dir=root / "data" / "runs",
            cache_dir=root / "data" / "cache",
            lock_dir=root / "data" / "locks",
            site_artifact_dir=root / "site",
        )

    def test_private_preview_persists_pending_result_without_mutating_canonical_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);storage.ensure();now=datetime(2026,8,14,1,0,tzinfo=timezone.utc)
            primary_state=root/"primary.json";generator_state=root/"generator.json";queue_state=root/"queue.json"
            primary_state.write_text('{"sentinel":"primary"}\n',encoding="utf-8")
            generator_state.write_text('{"sentinel":"generator"}\n',encoding="utf-8")
            queue_state.write_text('{"sentinel":"queue"}\n',encoding="utf-8")
            before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (primary_state,generator_state,queue_state)}

            titles={1:"Self-Evolving Agent Skill One",2:"Harness Evolution Agent Two",3:"Persistent Agent Memory Three",4:"Self-Evolving World Model Four",5:"Self-Evolving Autonomous Agent Strategy Alpha",6:"Self-Evolving Autonomous Agent Strategy Beta"}
            abstracts={idx:("A self-evolving agent skill harness improves adaptation." if idx<3 else ("Persistent agent memory improves a continual agent." if idx==3 else ("A self-evolving world model improves planning." if idx==4 else "A self-evolving autonomous agent iterates strategy from feedback."))) for idx in titles}
            papers=[{"paper_id":f"s2-{idx}","title":titles[idx],"year":2026,"abstract":abstracts[idx],"metadata":{"externalIds":{"ArXiv":f"2608.72{idx:03d}"},"publicationDate":f"2026-08-{14-idx:02d}","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]}} for idx in range(1,7)]
            corpus=storage.corpus_dir/"semantic-scholar-corpus.json";corpus.parent.mkdir(parents=True,exist_ok=True);corpus.write_text(json.dumps({"schema_version":"1.0","retrieved_at":now.isoformat(),"papers":papers}),encoding="utf-8")
            discovery=storage.data_root/"paper-first-problem-discovery";discovery.mkdir(parents=True,exist_ok=True)
            refs=[f"arXiv:2608.72{i:03d}" for i in range(1,5)]
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"schema_version":"1.0","runs":[{"run_id":"reviewed","source_refs":refs,"scientific_authority":False}]}),encoding="utf-8")

            def requester(url:str,*,timeout:float,headers:dict[str,str]):
                aid=url.rsplit('/',1)[-1];idx=int(aid[-1])
                if '/html/' in url:
                    return SimpleNamespace(status_code=200,text='<html><body><section><h2>Experimental Results</h2><p>We find verified performance improves by 11.0 percent on held-out tasks.</p></section></body></html>')
                return SimpleNamespace(status_code=200,text=f'<meta name="citation_title" content="{titles[idx]}"><blockquote class="abstract mathjax">Abstract: {abstracts[idx]}</blockquote>')

            result=run_carrier_preview(
                storage=storage,
                primary_state_path=primary_state,
                generator_state_path=generator_state,
                queue_state_path=queue_state,
                now=now,
                primary_kwargs={"corpus_path":corpus,"requester":requester,"augment_fresh_corpus_with_arxiv":False,"max_papers":5,"lane_floor":0,"coverage_anchor_count":2,"carrier_probe_limit":1,"min_interval_seconds":0},
            )
            after={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (primary_state,generator_state,queue_state)}
            artifact=Path(result["artifact_path"]);payload=json.loads(artifact.read_text())

        self.assertEqual(before,after)
        self.assertTrue(result["canonical_public_state_unchanged"])
        self.assertEqual(result["status"],"PRIVATE_CARRIER_PREVIEW_COMPLETE")
        self.assertEqual(result["preview_action"],"CARRIER_PROBE_PENDING_ZERO_CALL")
        self.assertFalse(result["generator_called"]);self.assertFalse(result["reviewer_called"]);self.assertFalse(result["scientific_authority"])
        self.assertEqual(payload["primary_summary"]["carrier_probe_pending"],1)
        self.assertEqual(payload["primary_summary"]["carrier_probe_rescued"],0)
        self.assertFalse(payload["scientific_authority"])
        self.assertTrue(payload["policy"]["canonical_public_state_mutation_forbidden"])
        self.assertTrue(payload["policy"]["preview_cannot_authorize_live_transaction"])


if __name__ == "__main__":
    unittest.main()
