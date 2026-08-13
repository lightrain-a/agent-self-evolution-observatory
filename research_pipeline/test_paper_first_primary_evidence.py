from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import requests

from .config import StorageSettings
from .paper_first_primary_evidence import DEFAULT_ARXIV_QUERIES, EMPIRICAL_FACT_EXTRACTION_VERSION, _default_requester, build_primary_evidence_pool, extract_empirical_fact_candidates, parse_arxiv_atom, parse_arxiv_page, select_primary_candidates


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
        if "/html/" in url:
            page = f'''<html><body><section><h2>Experimental Results</h2><p>We find that verified persistent adaptation improves held-out success by 12.5% for primary source {arxiv_id}, while an ablation without verification fails more often.</p></section></body></html>'''
        else:
            page = f'''<html><head><meta name="citation_title" content="{titles.get(suffix,'Unknown')}"></head>
            <body><blockquote class="abstract mathjax">Abstract: Primary abstract for {arxiv_id} about self-evolving agents and persistent adaptation.</blockquote></body></html>'''
        return SimpleNamespace(status_code=200, text=page)

    def fake_arxiv_search(self, *, query: str, max_results: int, timeout: float, headers: dict[str,str]):
        entries=[]
        for idx,title in enumerate(("Self-Evolving Agent Skills Under Feedback","Harness Evolution for Autonomous Agents","Persistent Memory for Self-Improving Agents","Continual Agent Workflow Evolution"),start=1):
            entries.append(f'''<entry><id>https://arxiv.org/abs/2608.0000{idx}v1</id><title>{title}</title><summary>We study self-evolving autonomous agents, persistent skills, harnesses, and feedback.</summary><published>2026-08-0{idx}T00:00:00Z</published></entry>''')
        return SimpleNamespace(status_code=200,text='<feed xmlns="http://www.w3.org/2005/Atom">'+''.join(entries)+'</feed>')

    def test_fallback_queries_cover_sparse_preregistered_scientific_objects(self) -> None:
        joined=" ".join(DEFAULT_ARXIV_QUERIES).lower()
        self.assertIn('multi-agent',joined)
        self.assertIn('scientific agent',joined)
        self.assertIn('embodied agent',joined)
        self.assertIn('agent memory',joined)
        self.assertIn('safety',joined)

    def test_parse_arxiv_page_extracts_title_and_abstract(self) -> None:
        parsed = parse_arxiv_page('<meta name="citation_title" content="Paper A"><blockquote class="abstract mathjax">Abstract: hello <b>world</b></blockquote>')
        self.assertEqual(parsed, {"title":"Paper A","abstract":"hello world"})

    def test_fulltext_empirical_fact_extraction_is_section_and_cue_bounded(self) -> None:
        page='''<html><body><section><h2>Experimental Results</h2><p>We find that the verified skill improves held-out success by 17.5% across five tasks, while the unverified ablation fails on two tasks.</p></section><section><h2>Related Work</h2><p>We find many papers interesting but this is not an experimental result.</p></section></body></html>'''
        facts=extract_empirical_fact_candidates(page,max_facts=4)
        self.assertEqual(len(facts),1)
        self.assertEqual(facts[0]["section"],"Experimental Results")
        self.assertIn("17.5%",facts[0]["text"])
        self.assertEqual(facts[0]["evidence_tier"],"strong-observation")
        self.assertEqual(len(facts[0]["text_sha256"]),64)

    def test_empirical_fact_extraction_rejects_metric_protocol_and_related_work_sentences(self) -> None:
        page='''<html><body><section><h2>Evaluation</h2><p>We report three metrics: attack success rate, clean utility, and false positive rate for every run.</p><p>Three gates: validity gate, activation gate, and significance gate are applied before scoring failures.</p><p>Recent work has highlighted the difficulty of evaluating self-improving agents and attribution failures.</p><p>Our method improves held-out success from 41.0% to 58.5% across 120 tasks under the same budget.</p></section></body></html>'''
        facts=extract_empirical_fact_candidates(page,max_facts=8)
        self.assertEqual(len(facts),1)
        self.assertIn("58.5%",facts[0]["text"])
        self.assertIn(facts[0]["evidence_tier"],{"quantitative-directional","owned-directional"})

    def test_parse_arxiv_atom_extracts_primary_metadata(self) -> None:
        rows=parse_arxiv_atom('<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>https://arxiv.org/abs/2608.12345v2</id><title> Self-Evolving Agent </title><summary> primary abstract </summary><published>2026-08-12T00:00:00Z</published></entry></feed>')
        self.assertEqual(len(rows),1); self.assertEqual(rows[0]["metadata"]["externalIds"]["ArXiv"],"2608.12345"); self.assertEqual(rows[0]["title"],"Self-Evolving Agent")

    def test_lane_floor_adds_only_highest_ranked_sparse_lane_representative(self) -> None:
        papers=[]
        for idx in range(1,6):
            papers.append({
                "paper_id":f"skill-{idx}","title":f"Self-Evolving Agent Skill Harness {idx}","year":2026,"venue":"arXiv",
                "abstract":"A self-evolving agent skill harness improves persistent workflow adaptation.",
                "metadata":{"externalIds":{"ArXiv":f"2608.20{idx:03d}"},"publicationDate":f"2026-08-{13-idx:02d}","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]},
            })
        papers.append({
            "paper_id":"collective-1","title":"Collaborative Multi-Agent Evolution Across Isolated Workloads","year":2026,"venue":"arXiv",
            "abstract":"A self-evolving multi-agent system coordinates collaborative agents across isolated workloads.",
            "metadata":{"externalIds":{"ArXiv":"2608.19001"},"publicationDate":"2026-08-01","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]},
        })
        corpus={"papers":papers}
        no_floor=select_primary_candidates(corpus,max_papers=3,lane_floor=0,now=datetime(2026,8,13,tzinfo=timezone.utc))
        with_floor=select_primary_candidates(corpus,max_papers=3,lane_floor=1,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertFalse(any(row["paper_id"]=="collective-1" for row in no_floor))
        self.assertTrue(any(row["paper_id"]=="collective-1" for row in with_floor))
        self.assertEqual(len(with_floor),3)
        self.assertEqual(with_floor[0]["paper_id"],"skill-1")
        self.assertEqual(with_floor[-1]["paper_id"],"collective-1")

    def test_lane_floor_does_not_synthesize_missing_lane_or_relax_relevance(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            corpus=json.loads(self.corpus(Path(td)).read_text())
            selected=select_primary_candidates(corpus,max_papers=10,lane_floor=1,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(len(selected),4)
        self.assertFalse(any("Ads Recommendation" in row["title"] for row in selected))

    def test_selection_requires_relevance_abstract_arxiv_id_and_recent_publication(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            corpus = json.loads(self.corpus(Path(td)).read_text())
            selected = select_primary_candidates(corpus, max_papers=10, now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(len(selected), 4)
        self.assertTrue(all((row["metadata"]["externalIds"]["ArXiv"]) for row in selected))
        self.assertFalse(any("Ads Recommendation" in row["title"] for row in selected))

    def test_publications_older_than_sixty_days_are_excluded_even_if_corpus_is_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            corpus = json.loads(self.corpus(Path(td)).read_text())
            corpus["papers"][0]["metadata"]["publicationDate"] = "2026-05-01"
            selected = select_primary_candidates(corpus, max_papers=10, now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual(len(selected), 3)
        self.assertFalse(any(row["metadata"]["externalIds"]["ArXiv"] == "2608.00001" for row in selected))

    def test_fresh_corpus_fetches_primary_pages_and_keeps_full_abstract_private(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            public, private = build_primary_evidence_pool(
                storage=storage,
                corpus_path=corpus,
                requester=self.fake_requester,
                augment_fresh_corpus_with_arxiv=False,
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
        self.assertTrue(all(row["empirical_facts"] for row in private["records"]))
        self.assertEqual(public["summary"]["fulltext_verified"],4)
        self.assertEqual(public["summary"]["fulltext_fetch_errors"],0)
        self.assertEqual(public["summary"]["lane_floor"],1)
        self.assertEqual(public["summary"]["undercovered_lanes"],[])
        self.assertEqual(public["summary"]["verified_undercovered_lanes"],[])
        self.assertTrue(public["policy"]["pre_registered_lane_coverage_floor"])
        self.assertTrue(public["policy"]["lane_coverage_is_discovery_breadth_not_scientific_authority"])
        self.assertTrue(public["policy"]["empirical_fact_precision_gate"])
        self.assertEqual(public["policy"]["empirical_fact_extraction_version"],"precision-v2")
        self.assertGreaterEqual(public["summary"]["empirical_fact_candidates"],4)
        self.assertEqual(sum(public["summary"]["empirical_fact_tier_counts"].values()),public["summary"]["empirical_fact_candidates"])
        self.assertTrue(all("abstract" not in row and "empirical_facts" not in row for row in public["records"]))
        self.assertTrue(all(row["empirical_fact_count"] >= 1 for row in public["records"]))
        self.assertTrue(all(len(row["fulltext_sha256"]) == 64 for row in public["records"]))
        self.assertNotIn("corpus_path",public); self.assertNotIn("private_pool_path",public)
        self.assertTrue(all(len(row["source_sha256"]) == 64 for row in public["records"]))

    def test_fresh_corpus_is_augmented_by_missing_arxiv_lane_evidence(self) -> None:
        science_title="A-SR: Self-Evolving Agentic LLMs for Symbolic Regression via Hierarchical Coordination"
        def search(**kwargs):
            return SimpleNamespace(status_code=200,text=f'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>https://arxiv.org/abs/2608.99999v1</id><title>{science_title}</title><summary>We present a self-evolving scientific discovery agent for symbolic regression and experiment planning.</summary><published>2026-08-06T00:00:00Z</published></entry></feed>''')
        def primary(url: str, *, timeout: float, headers: dict[str,str]):
            arxiv_id=url.rsplit('/',1)[-1]
            if arxiv_id=='2608.99999':
                if '/html/' in url:
                    return SimpleNamespace(status_code=200,text='<html><body><section><h2>Results</h2><p>We find that the self-evolving scientific agent improves held-out symbolic regression accuracy by 12.0 percent across scientific domains.</p></section></body></html>')
                return SimpleNamespace(status_code=200,text=f'<meta name="citation_title" content="{science_title}"><blockquote class="abstract mathjax">Abstract: We present a self-evolving scientific discovery agent for symbolic regression and experiment planning.</blockquote>')
            return self.fake_requester(url,timeout=timeout,headers=headers)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            public,private=build_primary_evidence_pool(
                storage=storage,corpus_path=corpus,requester=primary,arxiv_search_requester=search,
                arxiv_queries=('science-lane',),arxiv_query_interval_seconds=0,now=datetime(2026,8,13,tzinfo=timezone.utc),
                min_interval_seconds=0,max_papers=4,cache_dir=root/'primary-cache')
        refs={row['ref'] for row in public['records']}
        self.assertEqual(public['summary']['discovery_mode'],'semantic-scholar-plus-arxiv-augmentation')
        self.assertEqual(public['summary']['augmentation_discovered'],1)
        self.assertEqual(public['summary']['augmentation_added'],1)
        self.assertIn('arXiv:2608.99999',refs)
        self.assertEqual(public['summary']['selected_lane_counts']['autonomous_science'],1)
        self.assertEqual(public['summary']['undercovered_lanes'],[])
        self.assertEqual(len(private['records']),4)

    def test_fresh_augmentation_failure_is_metadata_error_not_primary_failure(self) -> None:
        def failed_search(**kwargs): return SimpleNamespace(status_code=503,text='')
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            public,_=build_primary_evidence_pool(
                storage=storage,corpus_path=corpus,requester=self.fake_requester,arxiv_search_requester=failed_search,
                arxiv_queries=('science-lane',),arxiv_query_interval_seconds=0,now=datetime(2026,8,13,tzinfo=timezone.utc),min_interval_seconds=0)
        self.assertEqual(public['status'],'READY')
        self.assertEqual(public['summary']['verified'],4)
        self.assertEqual(public['summary']['augmentation_added'],0)
        self.assertTrue(public['discovery_errors'])
        self.assertTrue(public['policy']['arxiv_augmentation_failure_does_not_invalidate_fresh_corpus'])
    def test_default_requester_has_whole_response_wall_clock_timeout(self) -> None:
        class SlowResponse:
            status_code=200
            encoding="utf-8"
            def __enter__(self): return self
            def __exit__(self,*args): return False
            def iter_content(self,chunk_size=65536):
                yield b"partial"
                yield b"still-trickling"
        with patch("research_pipeline.paper_first_primary_evidence.requests.get",return_value=SlowResponse()), patch("research_pipeline.paper_first_primary_evidence.time.monotonic",side_effect=[0.0,30.0]):
            with self.assertRaises(requests.Timeout):
                _default_requester("https://arxiv.org/html/test",timeout=25.0,headers={})

    def test_interrupted_raw_content_addressed_cache_resumes_without_network(self) -> None:
        calls=[]
        def fail_requester(*args,**kwargs):
            calls.append((args,kwargs)); raise AssertionError("fresh raw cache should avoid repeat network")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            cache_dir=root/"paper-first-problem-discovery"/"primary-sources"; cache_dir.mkdir(parents=True)
            import hashlib
            for idx,title in enumerate((
                "Self-Evolving Agent Skills Under Feedback",
                "Harness Evolution for Autonomous Agents",
                "Persistent Memory for Self-Improving Agents",
                "Continual Agent Workflow Evolution",
            ),start=1):
                arxiv_id=f"2608.0000{idx}"
                primary=f'''<html><head><meta name="citation_title" content="{title}"></head><body><blockquote class="abstract mathjax">Abstract: Cached primary abstract {idx} about self-evolving agents.</blockquote></body></html>'''.encode()
                primary_sha=hashlib.sha256(primary).hexdigest(); (cache_dir/f"arxiv-{arxiv_id}-{primary_sha[:12]}.html").write_bytes(primary)
                full=f'''<html><body><section><h2>Experimental Results</h2><p>We find cached result {idx} improves held-out success by 12.0 percent across tasks.</p></section></body></html>'''.encode()
                full_sha=hashlib.sha256(full).hexdigest(); (cache_dir/f"arxiv-full-{arxiv_id}-{full_sha[:12]}.html").write_bytes(full)
            public,private=build_primary_evidence_pool(
                storage=storage,corpus_path=corpus,requester=fail_requester,
                augment_fresh_corpus_with_arxiv=False,
                now=datetime(2026,8,13,8,0,tzinfo=timezone.utc),min_interval_seconds=0,max_papers=8,
            )
        self.assertEqual(calls,[])
        self.assertEqual(public["summary"]["verified"],4)
        self.assertEqual(public["summary"]["recent_verified_cache_reused"],0)
        self.assertEqual(public["summary"]["recent_raw_primary_cache_reused"],4)
        self.assertEqual(public["summary"]["recent_raw_fulltext_cache_reused"],4)
        self.assertEqual(public["summary"]["fulltext_verified"],4)
        self.assertGreaterEqual(public["summary"]["empirical_fact_candidates"],4)
        self.assertEqual(len(private["records"]),4)

    def test_recent_optional_fulltext_failures_use_short_retry_cooldown(self) -> None:
        calls=[]
        def fail_requester(*args,**kwargs):
            calls.append((args,kwargs)); raise AssertionError("recent optional fulltext failures should cool down")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            cache_dir=root/"paper-first-problem-discovery"/"primary-sources"; cache_dir.mkdir(parents=True)
            private_dir=root/"paper-first-problem-discovery"; records=[]; fulltext_errors=[]
            import hashlib
            for idx,title in enumerate((
                "Self-Evolving Agent Skills Under Feedback",
                "Harness Evolution for Autonomous Agents",
                "Persistent Memory for Self-Improving Agents",
                "Continual Agent Workflow Evolution",
            ),start=1):
                arxiv_id=f"2608.0000{idx}"; ref=f"arXiv:{arxiv_id}"
                primary=f'''<html><head><meta name="citation_title" content="{title}"></head><body><blockquote class="abstract mathjax">Abstract: Cached primary abstract {idx} about self-evolving agents.</blockquote></body></html>'''.encode()
                primary_sha=hashlib.sha256(primary).hexdigest(); source_path=cache_dir/f"arxiv-{arxiv_id}-{primary_sha[:12]}.html"; source_path.write_bytes(primary)
                records.append({
                    "evidence_id":str(idx)*64,"ref":ref,"title":title,"primary_url":f"https://arxiv.org/abs/{arxiv_id}",
                    "source_sha256":primary_sha,"abstract_sha256":"b"*64,"abstract":f"Cached primary abstract {idx} about self-evolving agents.",
                    "fulltext_url":f"https://arxiv.org/html/{arxiv_id}","fulltext_sha256":"","fulltext_cache_path":"","empirical_facts":[],
                    "cache_path":str(source_path),"fetched_at":"2026-08-13T05:30:00+00:00","primary_source_verified":True,
                })
                fulltext_errors.append({"ref":ref,"error":"ReadTimeout:prior optional fulltext failure"})
            (private_dir/"primary-evidence-pool.json").write_text(json.dumps({
                "status":"READY","generated_at":"2026-08-13T05:30:00+00:00","records":records,"fulltext_errors":fulltext_errors,
            }),encoding="utf-8")
            public,private=build_primary_evidence_pool(
                storage=storage,corpus_path=corpus,requester=fail_requester,augment_fresh_corpus_with_arxiv=False,
                now=datetime(2026,8,13,6,0,tzinfo=timezone.utc),min_interval_seconds=0,max_papers=8,
            )
        self.assertEqual(calls,[])
        self.assertEqual(public["status"],"READY")
        self.assertEqual(public["summary"]["verified"],4)
        self.assertEqual(public["summary"]["fulltext_verified"],0)
        self.assertEqual(public["summary"]["recent_raw_primary_cache_reused"],4)
        self.assertEqual(public["summary"]["recent_fulltext_failure_cooldown_skips"],4)
        self.assertEqual(public["summary"]["fulltext_fetch_errors"],4)
        self.assertTrue(all(row["error"]=="recent-fulltext-failure-cooldown" for row in private["fulltext_errors"]))
        self.assertTrue(public["policy"]["fulltext_failure_cooldown_applies_only_to_optional_enrichment"])

    def test_recent_complete_private_pool_is_reused_without_repeat_network_fetch(self) -> None:
        calls=[]
        def fail_requester(*args,**kwargs):
            calls.append((args,kwargs)); raise AssertionError("recent verified cache should avoid network")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            private_dir=root/"paper-first-problem-discovery"; private_dir.mkdir(parents=True)
            records=[]
            for idx,title in enumerate((
                "Self-Evolving Agent Skills Under Feedback",
                "Harness Evolution for Autonomous Agents",
                "Persistent Memory for Self-Improving Agents",
                "Continual Agent Workflow Evolution",
            ),start=1):
                source_cache=private_dir/f"source-{idx}.html"; source_cache.write_text("cached primary",encoding="utf-8")
                full_cache=private_dir/f"full-{idx}.html"; full_cache.write_text("<section>cached fulltext</section>",encoding="utf-8")
                records.append({
                    "evidence_id":str(idx)*64,"ref":f"arXiv:2608.0000{idx}","title":title,
                    "primary_url":f"https://arxiv.org/abs/2608.0000{idx}","source_sha256":"a"*64,"abstract_sha256":"b"*64,
                    "abstract":f"Primary abstract fact {idx} about self-evolving agents.","fulltext_url":f"https://arxiv.org/html/2608.0000{idx}",
                    "fulltext_sha256":"c"*64,"cache_path":str(source_cache),"fulltext_cache_path":str(full_cache),
                    "empirical_facts":[{"section":"Results","text":f"Cached empirical fact {idx} improves held-out success by 12.0 percent.","text_sha256":"d"*64}],
                    "fetched_at":"2026-08-13T05:00:00+00:00","primary_source_verified":True,
                    "empirical_fact_extraction_version":EMPIRICAL_FACT_EXTRACTION_VERSION,
                })
            (private_dir/"primary-evidence-pool.json").write_text(json.dumps({"status":"READY","generated_at":"2026-08-13T05:00:00+00:00","records":records}),encoding="utf-8")
            public,private=build_primary_evidence_pool(
                storage=storage,corpus_path=corpus,requester=fail_requester,
                augment_fresh_corpus_with_arxiv=False,
                now=datetime(2026,8,13,6,0,tzinfo=timezone.utc),min_interval_seconds=0,max_papers=8,
            )
        self.assertEqual(calls,[])
        self.assertEqual(public["status"],"READY")
        self.assertEqual(public["summary"]["verified"],4)
        self.assertEqual(public["summary"]["fulltext_verified"],4)
        self.assertEqual(public["summary"]["recent_verified_cache_reused"],4)
        self.assertEqual(len(private["records"]),4)
        self.assertTrue(public["policy"]["recent_cache_reuse_is_retry_optimization_not_weekly_freshness_relaxation"])

    def test_extractor_version_mismatch_reuses_raw_cache_but_rederives_empirical_facts(self) -> None:
        calls=[]
        def fail_requester(*args,**kwargs):
            calls.append((args,kwargs)); raise AssertionError("content-addressed raw cache should avoid network during extractor upgrade")
        with tempfile.TemporaryDirectory() as td:
            import hashlib
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            private_dir=root/"paper-first-problem-discovery"; private_dir.mkdir(parents=True)
            cache_dir=private_dir/"primary-sources"; cache_dir.mkdir(parents=True)
            records=[]
            titles=(
                "Self-Evolving Agent Skills Under Feedback",
                "Harness Evolution for Autonomous Agents",
                "Persistent Memory for Self-Improving Agents",
                "Continual Agent Workflow Evolution",
            )
            for idx,title in enumerate(titles,start=1):
                arxiv_id=f"2608.0000{idx}"
                primary=f'''<html><head><meta name="citation_title" content="{title}"></head><body><blockquote class="abstract mathjax">Abstract: Cached primary abstract {idx} about self-evolving agents.</blockquote></body></html>'''.encode()
                source_sha=hashlib.sha256(primary).hexdigest(); source_cache=cache_dir/f"arxiv-{arxiv_id}-{source_sha[:12]}.html"; source_cache.write_bytes(primary)
                full=f'''<html><body><section><h2>Experimental Results</h2><p>We report three metrics: success, failure, and latency.</p><p>Our method improves held-out success from 41.0% to 58.5% across 120 tasks under the same budget.</p></section></body></html>'''.encode()
                full_sha=hashlib.sha256(full).hexdigest(); full_cache=cache_dir/f"arxiv-full-{arxiv_id}-{full_sha[:12]}.html"; full_cache.write_bytes(full)
                records.append({
                    "evidence_id":str(idx)*64,"ref":f"arXiv:{arxiv_id}","title":title,
                    "primary_url":f"https://arxiv.org/abs/{arxiv_id}","source_sha256":source_sha,"abstract_sha256":"b"*64,
                    "abstract":f"Cached primary abstract {idx} about self-evolving agents.","fulltext_url":f"https://arxiv.org/html/{arxiv_id}",
                    "fulltext_sha256":full_sha,"cache_path":str(source_cache),"fulltext_cache_path":str(full_cache),
                    "empirical_facts":[{"section":"Evaluation","text":"We report three metrics: success, failure, and latency.","text_sha256":"d"*64}],
                    "fetched_at":"2026-08-13T05:00:00+00:00","primary_source_verified":True,
                    "empirical_fact_extraction_version":"legacy-v0",
                })
            (private_dir/"primary-evidence-pool.json").write_text(json.dumps({"status":"READY","generated_at":"2026-08-13T05:00:00+00:00","records":records}),encoding="utf-8")
            public,private=build_primary_evidence_pool(
                storage=storage,corpus_path=corpus,requester=fail_requester,
                augment_fresh_corpus_with_arxiv=False,
                now=datetime(2026,8,13,6,0,tzinfo=timezone.utc),min_interval_seconds=0,max_papers=8,
            )
        self.assertEqual(calls,[])
        self.assertEqual(public["summary"]["recent_verified_cache_reused"],0)
        self.assertEqual(public["summary"]["recent_raw_primary_cache_reused"],4)
        self.assertEqual(public["summary"]["recent_raw_fulltext_cache_reused"],4)
        self.assertEqual(public["policy"]["empirical_fact_extraction_version"],EMPIRICAL_FACT_EXTRACTION_VERSION)
        self.assertTrue(public["policy"]["derived_empirical_facts_reused_only_when_extractor_version_matches"])
        self.assertTrue(all(row["empirical_fact_extraction_version"]==EMPIRICAL_FACT_EXTRACTION_VERSION for row in private["records"]))
        self.assertTrue(all(row["empirical_facts"] and "58.5%" in row["empirical_facts"][0]["text"] for row in private["records"]))
        self.assertFalse(any("We report three metrics" in fact["text"] for row in private["records"] for fact in row["empirical_facts"]))

    def test_stale_corpus_uses_arxiv_primary_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root,retrieved_at="2026-07-01T00:00:00+00:00")
            public, private = build_primary_evidence_pool(
                storage=storage,
                corpus_path=corpus,
                requester=self.fake_requester,
                arxiv_search_requester=self.fake_arxiv_search,
                arxiv_queries=('all:"self-evolving" AND all:agent',),
                arxiv_query_interval_seconds=0,
                now=datetime(2026,8,13,tzinfo=timezone.utc),
                min_interval_seconds=0,
            )
        self.assertEqual(public["status"], "READY")
        self.assertFalse(public["summary"]["corpus_fresh"])
        self.assertEqual(public["summary"]["discovery_mode"],"arxiv-primary-fallback")
        self.assertEqual(public["summary"]["verified"],4)
        self.assertEqual(len(private["records"]),4)

    def test_missing_corpus_and_failed_fallback_yields_insufficient_evidence(self) -> None:
        def failed_search(**kwargs): return SimpleNamespace(status_code=429,text='')
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root)
            public,private=build_primary_evidence_pool(storage=storage,corpus_path=root/"missing.json",arxiv_search_requester=failed_search,arxiv_queries=('q',),arxiv_query_interval_seconds=0,now=datetime(2026,8,13,tzinfo=timezone.utc),min_interval_seconds=0)
        self.assertEqual(public["status"],"INSUFFICIENT_PRIMARY_EVIDENCE")
        self.assertEqual(public["summary"]["verified"],0)
        self.assertFalse(public["summary"]["candidate_generation_ready"])
        self.assertTrue(public["discovery_errors"])
        self.assertEqual(private["records"],[])

    def test_title_mismatch_is_evidence_absence_not_scientific_negative(self) -> None:
        def wrong(url: str, *, timeout: float, headers: dict[str,str]):
            return SimpleNamespace(status_code=200,text='<meta name="citation_title" content="Completely Different"><blockquote class="abstract mathjax">Abstract: evidence</blockquote>')
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            public, _ = build_primary_evidence_pool(storage=storage,corpus_path=corpus,requester=wrong,augment_fresh_corpus_with_arxiv=False,now=datetime(2026,8,13,tzinfo=timezone.utc),min_interval_seconds=0)
        self.assertEqual(public["summary"]["verified"],0)
        self.assertEqual(public["summary"]["title_mismatches"],4)
        self.assertEqual(public["status"],"INSUFFICIENT_PRIMARY_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
