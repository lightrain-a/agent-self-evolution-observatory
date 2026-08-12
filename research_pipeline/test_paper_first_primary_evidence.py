from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from .config import StorageSettings
from .paper_first_primary_evidence import build_primary_evidence_pool, parse_arxiv_page, select_primary_candidates


class PaperFirstPrimaryEvidenceTest(unittest.TestCase):
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

    def corpus(self, root: Path, *, retrieved_at: str = "2026-08-12T00:00:00+00:00") -> Path:
        path = root / "corpus.json"
        papers = []
        for idx, title in enumerate((
            "Self-Evolving Agent Skills Under Feedback",
            "Harness Evolution for Autonomous Agents",
            "Persistent Memory for Self-Improving Agents",
            "Continual Agent Workflow Evolution",
            "Unrelated Ads Recommendation System",
        ), start=1):
            relevant = idx < 5
            papers.append({
                "paper_id": f"s2-{idx}",
                "title": title,
                "year": 2026,
                "venue": "arXiv",
                "abstract": ("We study self-evolving autonomous agents, persistent skills, harnesses, and feedback." if relevant else "We study advertising recommendation."),
                "url": f"https://www.semanticscholar.org/paper/s2-{idx}",
                "metadata": {
                    "externalIds": {"ArXiv": f"2608.0000{idx}"},
                    "publicationDate": f"2026-08-0{idx}",
                    "citationCount": idx,
                    "retrievalScore": float(idx),
                    "retrievedAt": retrieved_at,
                    "matches": [{"route": "topic"}],
                },
            })
        path.write_text(json.dumps({"schema_version":"1.0","retrieved_at":retrieved_at,"papers":papers}), encoding="utf-8")
        return path

    def fake_requester(self, url: str, *, timeout: float, headers: dict[str, str]):
        arxiv_id = url.rsplit("/", 1)[-1]
        suffix = arxiv_id[-1]
        titles = {
            "1": "Self-Evolving Agent Skills Under Feedback",
            "2": "Harness Evolution for Autonomous Agents",
            "3": "Persistent Memory for Self-Improving Agents",
            "4": "Continual Agent Workflow Evolution",
        }
        page = f'''<html><head><meta name="citation_title" content="{titles.get(suffix,'Unknown')}"></head>
        <body><blockquote class="abstract mathjax">Abstract: Primary abstract for {arxiv_id} about self-evolving agents and persistent adaptation.</blockquote></body></html>'''
        return SimpleNamespace(status_code=200, text=page)

    def test_parse_arxiv_page_extracts_title_and_abstract(self) -> None:
        parsed = parse_arxiv_page('<meta name="citation_title" content="Paper A"><blockquote class="abstract mathjax">Abstract: hello <b>world</b></blockquote>')
        self.assertEqual(parsed, {"title":"Paper A","abstract":"hello world"})

    def test_selection_requires_relevance_abstract_and_arxiv_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            corpus = json.loads(self.corpus(Path(td)).read_text())
            selected = select_primary_candidates(corpus, max_papers=10)
        self.assertEqual(len(selected), 4)
        self.assertTrue(all((row["metadata"]["externalIds"]["ArXiv"]) for row in selected))
        self.assertFalse(any("Ads Recommendation" in row["title"] for row in selected))

    def test_fresh_corpus_fetches_primary_pages_and_keeps_full_abstract_private(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            public, private = build_primary_evidence_pool(
                storage=storage,
                corpus_path=corpus,
                requester=self.fake_requester,
                now=datetime(2026,8,13,tzinfo=timezone.utc),
                min_interval_seconds=0,
                max_papers=8,
                cache_dir=root/"primary-cache",
            )
        self.assertEqual(public["status"], "READY")
        self.assertEqual(public["summary"]["verified"], 4)
        self.assertTrue(public["summary"]["candidate_generation_ready"])
        self.assertEqual(len(private["records"]), 4)
        self.assertTrue(all(row["abstract"] for row in private["records"]))
        self.assertTrue(all("abstract" not in row for row in public["records"]))
        self.assertTrue(all(len(row["source_sha256"]) == 64 for row in public["records"]))

    def test_stale_corpus_blocks_without_network_fetch(self) -> None:
        calls=[]
        def requester(*args,**kwargs):
            calls.append(args); raise AssertionError("network should not be called")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root,retrieved_at="2026-07-01T00:00:00+00:00")
            public, private = build_primary_evidence_pool(
                storage=storage,
                corpus_path=corpus,
                requester=requester,
                now=datetime(2026,8,13,tzinfo=timezone.utc),
                min_interval_seconds=0,
            )
        self.assertEqual(public["status"], "STALE_CORPUS_BLOCKED")
        self.assertFalse(public["summary"]["candidate_generation_ready"])
        self.assertEqual(calls,[])
        self.assertEqual(private["records"],[])

    def test_title_mismatch_is_evidence_absence_not_scientific_negative(self) -> None:
        def wrong(url: str, *, timeout: float, headers: dict[str,str]):
            return SimpleNamespace(status_code=200,text='<meta name="citation_title" content="Completely Different"><blockquote class="abstract mathjax">Abstract: evidence</blockquote>')
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            public, _ = build_primary_evidence_pool(storage=storage,corpus_path=corpus,requester=wrong,now=datetime(2026,8,13,tzinfo=timezone.utc),min_interval_seconds=0)
        self.assertEqual(public["summary"]["verified"],0)
        self.assertEqual(public["summary"]["title_mismatches"],4)
        self.assertEqual(public["status"],"INSUFFICIENT_PRIMARY_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
