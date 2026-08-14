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
from .paper_first_primary_evidence import DEFAULT_ARXIV_QUERIES, EMPIRICAL_FACT_EXTRACTION_VERSION, TYPED_EVIDENCE_EXTRACTION_VERSION, _default_requester, _paper_lane_keys, _paper_object_lane_keys, _source_exposure_state, build_primary_evidence_pool, discover_arxiv_fallback, extract_empirical_fact_candidates, extract_typed_evidence_candidates, parse_arxiv_atom, parse_arxiv_page, select_primary_candidates


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
            page = f'''<html><body><section><h2>Method Assumptions</h2><p>We assume that tool availability remains stationary throughout bounded deployment for primary source {arxiv_id}.</p></section><section><h2>Experimental Results</h2><p>We find that verified persistent adaptation improves held-out success by 12.5% for primary source {arxiv_id}, while an ablation without verification fails more often.</p><p>Results show a threshold regime: performance drops below 40.0% only when the retained evidence budget falls below 2.0 units.</p></section></body></html>'''
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

    def test_world_model_and_parametric_state_are_scientific_object_lanes(self) -> None:
        world={"title":"Self-Evolving World Models for Agent Planning","abstract":"A world model is continually optimized from interaction evidence."}
        param={"title":"Recursive Agent Improvement","abstract":"We post-train the agent and update LoRA parameters from execution-grounded feedback."}
        frozen={"title":"Harness Evolution","abstract":"Model weights remain fixed; adaptation changes only the external harness."}
        self.assertIn("world_model",_paper_object_lane_keys(world))
        self.assertIn("parametric_model_state",_paper_object_lane_keys(param))
        self.assertNotIn("parametric_model_state",_paper_object_lane_keys(frozen))

    def test_source_scheduler_prefers_object_grounded_exploration_over_context_only(self) -> None:
        papers=[
            {"paper_id":"anchor","title":"Agent Skill Harness Anchor","abstract":"A self-evolving agent skill harness.","year":2026,"metadata":{"externalIds":{"ArXiv":"2608.41001"},"publicationDate":"2026-08-13","citationCount":0,"retrievalScore":0,"matches":[{"route":"topic"}]}},
            {"paper_id":"context","title":"Autonomous Agent Runtime Deployment","abstract":"A self-evolving autonomous agent is studied in runtime deployment.","year":2026,"metadata":{"externalIds":{"ArXiv":"2608.41002"},"publicationDate":"2026-08-12","citationCount":0,"retrievalScore":0,"matches":[{"route":"topic"}]}},
            {"paper_id":"world","title":"Adaptive World Model for Self-Evolving Agents","abstract":"A world model evolves from interaction evidence.","year":2026,"metadata":{"externalIds":{"ArXiv":"2608.41003"},"publicationDate":"2026-08-11","citationCount":0,"retrievalScore":0,"matches":[{"route":"topic"}]}},
        ]
        exposure={"arXiv:2608.41001":1,"arXiv:2608.41002":0,"arXiv:2608.41003":0}
        selected=select_primary_candidates({"papers":papers},max_papers=2,lane_floor=0,source_exposure_counts=exposure,coverage_anchor_count=1,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual([row["paper_id"] for row in selected],["anchor","world"])

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

    def test_typed_evidence_extraction_separates_assumption_failure_and_boundary(self) -> None:
        page='''<html><body><section><h2>Method Assumptions</h2><p>We assume that tool availability remains stationary throughout bounded deployment.</p></section><section><h2>Experimental Results</h2><p>We find that the unverified agent fails on 4/10 held-out tasks under the bounded condition.</p><p>Results show a threshold regime: success drops below 40.0% only when the evidence budget falls below 2.0 units.</p></section><section><h2>Related Work</h2><p>We assume many prior systems are interesting, but this sentence is not an operational assumption.</p></section></body></html>'''
        typed=extract_typed_evidence_candidates(page,max_per_type=2)
        self.assertEqual(len(typed["operational_assumptions"]),1)
        self.assertGreaterEqual(len(typed["measured_failures"]),1)
        self.assertEqual(len(typed["boundary_observations"]),1)
        self.assertIn("stationary",typed["operational_assumptions"][0]["text"])
        self.assertTrue(any("4/10" in row["text"] for row in typed["measured_failures"]))
        self.assertIn("threshold regime",typed["boundary_observations"][0]["text"])
        self.assertTrue(all(row["extraction_version"]==TYPED_EVIDENCE_EXTRACTION_VERSION for rows in typed.values() for row in rows))
        self.assertTrue(all(len(row["text_sha256"])==64 for rows in typed.values() for row in rows))

    def test_empirical_fact_extraction_rejects_metric_protocol_and_related_work_sentences(self) -> None:
        page='''<html><body><section><h2>Evaluation</h2><p>We report three metrics: attack success rate, clean utility, and false positive rate for every run.</p><p>Three gates: validity gate, activation gate, and significance gate are applied before scoring failures.</p><p>Recent work has highlighted the difficulty of evaluating self-improving agents and attribution failures.</p><p>Our method improves held-out success from 41.0% to 58.5% across 120 tasks under the same budget.</p></section></body></html>'''
        facts=extract_empirical_fact_candidates(page,max_facts=8)
        self.assertEqual(len(facts),1)
        self.assertIn("58.5%",facts[0]["text"])
        self.assertIn(facts[0]["evidence_tier"],{"quantitative-directional","owned-directional"})

    def test_parse_arxiv_atom_extracts_primary_metadata(self) -> None:
        rows=parse_arxiv_atom('<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>https://arxiv.org/abs/2608.12345v2</id><title> Self-Evolving Agent </title><summary> primary abstract </summary><published>2026-08-12T00:00:00Z</published></entry></feed>')
        self.assertEqual(len(rows),1); self.assertEqual(rows[0]["metadata"]["externalIds"]["ArXiv"],"2608.12345"); self.assertEqual(rows[0]["title"],"Self-Evolving Agent")

    def test_arxiv_fallback_pages_until_freshness_boundary(self) -> None:
        calls=[]
        pages={
            0:[("2608.30001","2026-08-12"),("2608.30002","2026-08-10")],
            2:[("2607.30003","2026-07-01"),("2606.30004","2026-06-10")],
        }
        def paged_search(*,query:str,start:int,max_results:int,timeout:float,headers:dict[str,str]):
            calls.append(start);entries=[]
            for aid,date in pages.get(start,[]):
                entries.append(f'<entry><id>https://arxiv.org/abs/{aid}v1</id><title>Self-Evolving Agent {aid}</title><summary>A self-evolving agent improves persistent adaptation.</summary><published>{date}T00:00:00Z</published></entry>')
            return SimpleNamespace(status_code=200,text='<feed xmlns="http://www.w3.org/2005/Atom">'+''.join(entries)+'</feed>')
        rows,errors=discover_arxiv_fallback(queries=('q',),per_query=2,max_pages=4,requester=paged_search,min_interval_seconds=0,now=datetime(2026,8,13,tzinfo=timezone.utc),max_publication_age_days=60)
        self.assertEqual(calls,[0,2])
        self.assertEqual(len(rows),4)
        self.assertEqual(errors,[])

    def test_arxiv_fallback_marks_bounded_truncation_before_freshness_boundary(self) -> None:
        calls=[]
        def paged_search(*,query:str,start:int,max_results:int,timeout:float,headers:dict[str,str]):
            calls.append(start);entries=[]
            for offset in range(max_results):
                aid=f"2608.{start+offset+40000:05d}"
                entries.append(f'<entry><id>https://arxiv.org/abs/{aid}v1</id><title>Self-Evolving Agent {aid}</title><summary>A self-evolving agent improves persistent adaptation.</summary><published>2026-08-01T00:00:00Z</published></entry>')
            return SimpleNamespace(status_code=200,text='<feed xmlns="http://www.w3.org/2005/Atom">'+''.join(entries)+'</feed>')
        rows,errors=discover_arxiv_fallback(queries=('q',),per_query=2,max_pages=2,requester=paged_search,min_interval_seconds=0,now=datetime(2026,8,13,tzinfo=timezone.utc),max_publication_age_days=60)
        self.assertEqual(calls,[0,2])
        self.assertEqual(len(rows),4)
        self.assertEqual(len(errors),1)
        self.assertIn('FreshnessWindowTruncated',errors[0])

    def test_arxiv_rate_limit_opens_one_request_circuit_breaker(self) -> None:
        calls=[]
        def limited(*,query:str,start:int,max_results:int,timeout:float,headers:dict[str,str]):
            calls.append((query,start));return SimpleNamespace(status_code=429,text='')
        rows,errors=discover_arxiv_fallback(queries=('q1','q2','q3'),per_query=2,max_pages=4,requester=limited,min_interval_seconds=0,now=datetime(2026,8,14,tzinfo=timezone.utc),max_publication_age_days=60)
        self.assertEqual(rows,[])
        self.assertEqual(calls,[('q1',0)])
        self.assertEqual(len(errors),1)
        self.assertIn('RateLimited:HTTP 429:augmentation-circuit-open',errors[0])

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

    def test_portable_review_receipt_merges_missing_host_run_without_double_count(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);discovery=root/"paper-first-problem-discovery";discovery.mkdir(parents=True)
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"runs":[{"run_id":"private-run","source_refs":["arXiv:A","arXiv:B","arXiv:C","arXiv:D"]}]}),encoding="utf-8")
            generator=root/"generator.json";generator.write_text(json.dumps({"saturation_memory":{"portable_review_receipts":[
                {"run_id":"private-run","source_refs":["arXiv:A","arXiv:B","arXiv:C","arXiv:D"],"status":"GENERATED_ZERO_CANDIDATES","scientific_authority":False},
                {"run_id":"remote-run","source_refs":["arXiv:C","arXiv:D","arXiv:E","arXiv:F"],"status":"GENERATED_AWAIT_PROBLEM_GATE","scientific_authority":False},
            ]}}),encoding="utf-8")
            counts,runs,portable,receipts=_source_exposure_state(storage,portable_generator_state_path=generator,portable_primary_state_path=root/"unused.json")
        self.assertEqual((runs,portable),(2,1));self.assertEqual({row["run_id"] for row in receipts},{"private-run","remote-run"})
        self.assertEqual({k:counts[k] for k in sorted(counts)},{"arXiv:A":1,"arXiv:B":1,"arXiv:C":2,"arXiv:D":2,"arXiv:E":1,"arXiv:F":1})

    def test_private_saturation_runs_are_exported_as_zero_authority_portable_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);discovery=root/"paper-first-problem-discovery";discovery.mkdir(parents=True)
            runs=[]
            for idx in (1,2):
                runs.append({"run_id":f"private-{idx}","pool_sha256":str(idx)*64,"negative_space_sha256":"f"*64,"source_refs":[f"arXiv:{idx}-{j}" for j in range(4)],"status":"GENERATED_ZERO_CANDIDATES","requested_model":"ark-code-latest","resolved_model":"doubao-seed-evolving","raw_sha256":"e"*64,"scientific_authority":False})
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"schema_version":"1.0","runs":runs}),encoding="utf-8")
            counts,run_count,portable_added,receipts=_source_exposure_state(storage,portable_generator_state_path=root/"missing-generator.json",portable_primary_state_path=root/"missing-primary.json")
        self.assertEqual(run_count,2);self.assertEqual(portable_added,0);self.assertEqual(len(counts),8)
        self.assertEqual([row["run_id"] for row in receipts],["private-1","private-2"])
        self.assertTrue(all(row.get("from_private_saturation_ledger") is True and row.get("scientific_authority") is False for row in receipts))

    def test_pre_receipt_public_transaction_bootstraps_cross_host_exposure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);generator=root/"generator.json";primary=root/"primary.json"
            generator.write_text(json.dumps({"run_id":"legacy-public-run","status":"GENERATED_ZERO_CANDIDATES","summary":{"primary_evidence_records":4},"saturation_memory":{"current_run_recorded":True,"scientific_authority":False}}),encoding="utf-8")
            primary.write_text(json.dumps({"status":"READY","records":[{"ref":f"arXiv:{i}"} for i in range(4)]}),encoding="utf-8")
            counts,runs,portable,receipts=_source_exposure_state(storage,portable_generator_state_path=generator,portable_primary_state_path=primary)
        self.assertEqual((runs,portable),(1,1));self.assertEqual(len(counts),4);self.assertTrue(all(value==1 for value in counts.values()));self.assertEqual(receipts[0]["run_id"],"legacy-public-run")

    def test_source_coverage_scheduler_preserves_anchors_and_adds_unreviewed_tail(self) -> None:
        papers=[]
        for idx in range(1,7):
            papers.append({
                "paper_id":f"p{idx}","title":f"Self-Evolving Agent Skill Harness Study {idx}","year":2026,"venue":"arXiv",
                "abstract":"A self-evolving agent skill harness improves persistent workflow adaptation.",
                "metadata":{"externalIds":{"ArXiv":f"2608.30{idx:03d}"},"publicationDate":f"2026-08-{14-idx:02d}","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]},
            })
        exposure={f"arXiv:2608.30{idx:03d}":1 for idx in range(1,6)}
        selected=select_primary_candidates({"papers":papers},max_papers=4,lane_floor=0,source_exposure_counts=exposure,coverage_anchor_count=2,now=datetime(2026,8,13,tzinfo=timezone.utc))
        ids=[row["paper_id"] for row in selected]
        self.assertEqual(ids[:2],["p1","p2"])
        self.assertIn("p6",ids)
        self.assertEqual(len(ids),4)

    def test_source_coverage_scheduler_preserves_lane_floor_after_exposure_reranking(self) -> None:
        papers=[]
        specs=[
            ("skill-1","Self-Evolving Agent Skill Harness One","A self-evolving agent skill harness improves persistent workflow adaptation."),
            ("skill-2","Self-Evolving Agent Skill Harness Two","A self-evolving agent skill harness improves persistent workflow adaptation."),
            ("collective","Collaborative Multi-Agent Evolution","A self-evolving multi-agent collaborative system studies agent evolution."),
            ("skill-4","Self-Evolving Agent Skill Harness Four","A self-evolving agent skill harness improves persistent workflow adaptation."),
            ("skill-5","Self-Evolving Agent Skill Harness Five","A self-evolving agent skill harness improves persistent workflow adaptation."),
        ]
        for idx,(pid,title,abstract) in enumerate(specs,1):
            papers.append({"paper_id":pid,"title":title,"year":2026,"venue":"arXiv","abstract":abstract,"metadata":{"externalIds":{"ArXiv":f"2608.31{idx:03d}"},"publicationDate":f"2026-08-{14-idx:02d}","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]}})
        exposure={"arXiv:2608.31001":1,"arXiv:2608.31002":1,"arXiv:2608.31003":9}
        selected=select_primary_candidates({"papers":papers},max_papers=4,lane_floor=1,source_exposure_counts=exposure,coverage_anchor_count=2,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertIn("collective",[row["paper_id"] for row in selected])
        self.assertGreaterEqual(sum("collective" in _paper_lane_keys(row) for row in selected),1)

    def test_source_coverage_exploration_prefers_preregistered_lane_sources_before_no_lane_fillers(self) -> None:
        papers=[
            {"paper_id":"anchor","title":"Self-Evolving Agent Skill Harness Anchor","year":2026,"venue":"arXiv","abstract":"A self-evolving agent skill harness study.","metadata":{"externalIds":{"ArXiv":"2608.32001"},"publicationDate":"2026-08-13","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]}},
            {"paper_id":"broad","title":"Autonomous Agent Governance Study","year":2026,"venue":"arXiv","abstract":"We study an autonomous agent governance framework without a self-evolution mechanism.","metadata":{"externalIds":{"ArXiv":"2608.32002"},"publicationDate":"2026-08-12","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]}},
            {"paper_id":"lane","title":"HarnessSafe for Persistent Agent Harnesses","year":2026,"venue":"arXiv","abstract":"A self-evolving agent harness safety and reliability study.","metadata":{"externalIds":{"ArXiv":"2608.32003"},"publicationDate":"2026-08-11","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]}},
        ]
        selected=select_primary_candidates({"papers":papers},max_papers=2,lane_floor=0,source_exposure_counts={"arXiv:2608.32001":1,"arXiv:2608.32002":0,"arXiv:2608.32003":0},coverage_anchor_count=1,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertEqual([row["paper_id"] for row in selected],["anchor","lane"])

    def test_source_coverage_scheduler_never_relaxes_relevance_or_publication_age(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            corpus=json.loads(self.corpus(Path(td)).read_text())
            corpus["papers"][0]["metadata"]["publicationDate"]="2026-05-01"
            exposure={f"arXiv:2608.0000{i}":5 for i in range(1,5)}
            exposure["arXiv:2608.00005"]=0
            selected=select_primary_candidates(corpus,max_papers=10,lane_floor=1,source_exposure_counts=exposure,coverage_anchor_count=1,now=datetime(2026,8,13,tzinfo=timezone.utc))
        self.assertFalse(any(row["metadata"]["externalIds"]["ArXiv"]=="2608.00001" for row in selected))
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

    def test_build_uses_private_saturation_ledger_only_for_zero_authority_source_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); corpus=self.corpus(root)
            discovery=root/"paper-first-problem-discovery"; discovery.mkdir(parents=True)
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"schema_version":"1.0","runs":[{"source_refs":["arXiv:2608.00004","arXiv:2608.00003","arXiv:2608.00002"],"scientific_authority":False}]}),encoding="utf-8")
            public,private=build_primary_evidence_pool(
                storage=storage,corpus_path=corpus,requester=self.fake_requester,
                augment_fresh_corpus_with_arxiv=False,coverage_anchor_count=1,
                now=datetime(2026,8,13,tzinfo=timezone.utc),min_interval_seconds=0,max_papers=3,
                cache_dir=root/"primary-cache",
            )
        self.assertTrue(public["summary"]["source_coverage_scheduler_active"])
        self.assertEqual(public["summary"]["saturation_ledger_runs"],1)
        self.assertEqual(public["summary"]["prior_reviewed_sources"],3)
        self.assertEqual(public["summary"]["portable_review_receipts_merged"],0)
        self.assertEqual(public["summary"]["eligible_unreviewed"],1)
        self.assertEqual(public["summary"]["eligible_lane_unreviewed"],1)
        self.assertEqual(public["summary"]["eligible_no_lane_unreviewed"],0)
        self.assertEqual(public["summary"]["selected_previously_reviewed"]+public["summary"]["selected_unreviewed"],public["summary"]["selected"])
        self.assertGreaterEqual(public["summary"]["selected_unreviewed"],1)
        self.assertEqual(public["summary"]["selected_lane_unreviewed"],public["summary"]["selected_unreviewed"])
        self.assertEqual(public["summary"]["coverage_anchor_count"],1)
        self.assertTrue(public["policy"]["source_coverage_scheduler_is_discovery_only"])
        self.assertTrue(public["policy"]["source_review_exposure_has_zero_scientific_authority"])
        self.assertTrue(public["policy"]["source_exposure_cannot_skip_generation_or_problem_gate"])
        self.assertTrue(public["policy"]["source_exposure_does_not_relax_relevance_or_freshness"])
        self.assertFalse(private["source_coverage"]["scientific_authority"])
        self.assertEqual(len(private["source_coverage"]["selected"]),3)

    def test_source_coverage_exhaustion_is_lane_grounded_compute_state_not_scientific_negative(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);corpus=self.corpus(root);discovery=root/"paper-first-problem-discovery";discovery.mkdir(parents=True)
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"schema_version":"1.0","runs":[{"source_refs":[f"arXiv:2608.0000{i}" for i in range(1,5)],"scientific_authority":False}]}),encoding="utf-8")
            public,private=build_primary_evidence_pool(storage=storage,corpus_path=corpus,requester=self.fake_requester,augment_fresh_corpus_with_arxiv=False,coverage_anchor_count=1,now=datetime(2026,8,13,tzinfo=timezone.utc),min_interval_seconds=0,max_papers=3,cache_dir=root/"primary-cache")
        self.assertTrue(public["summary"]["source_coverage_scheduler_active"])
        self.assertTrue(public["summary"]["source_coverage_exhausted"])
        self.assertTrue(public["summary"]["source_retrieval_complete"])
        self.assertEqual(public["summary"]["unreviewed_lane_linked_sources"],0)
        self.assertEqual(public["summary"]["reviewed_lane_linked_sources"],public["summary"]["eligible_lane_linked_sources"])
        self.assertTrue(public["policy"]["source_coverage_saturation_is_compute_control_not_scientific_negative"])
        self.assertTrue(public["policy"]["new_lane_grounded_source_reopens_generation"])
        self.assertTrue(private["source_coverage"]["coverage_exhausted"])
        self.assertFalse(private["source_coverage"]["scientific_authority"])

    def test_no_lane_carrier_probe_rescues_existing_parametric_object_before_selection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);now=datetime(2026,8,13,tzinfo=timezone.utc)
            titles={
                1:"Self-Evolving Agent Skill Harness One",2:"Harness Evolution for Autonomous Agents Two",
                3:"Persistent Agent Memory Evolution Three",4:"Adaptive World Model for Self-Evolving Agents Four",
                5:"Self-Evolving Autonomous Agent Strategy Alpha",6:"Self-Evolving Autonomous Agent Strategy Beta",
            }
            abstracts={
                1:"A self-evolving agent skill improves persistent adaptation.",2:"A harness evolves for autonomous agents.",
                3:"Agent memory supports a self-improving continual agent.",4:"A world model evolves for self-evolving agents.",
                5:"A self-evolving autonomous agent iterates decision strategy from feedback.",6:"A self-evolving autonomous agent iterates decision strategy from feedback.",
            }
            papers=[]
            for idx in range(1,7):
                papers.append({"paper_id":f"s2-{idx}","title":titles[idx],"year":2026,"abstract":abstracts[idx],"metadata":{"externalIds":{"ArXiv":f"2608.51{idx:03d}"},"publicationDate":f"2026-08-{14-idx:02d}","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]}})
            corpus=root/"carrier-corpus.json";corpus.write_text(json.dumps({"schema_version":"1.0","retrieved_at":"2026-08-13T00:00:00+00:00","papers":papers}),encoding="utf-8")
            discovery=root/"paper-first-problem-discovery";discovery.mkdir(parents=True)
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"schema_version":"1.0","runs":[{"run_id":"reviewed","source_refs":[f"arXiv:2608.51{i:03d}" for i in range(1,5)],"scientific_authority":False}]}),encoding="utf-8")
            def requester(url:str,*,timeout:float,headers:dict[str,str]):
                aid=url.rsplit('/',1)[-1];idx=int(aid[-1])
                if '/html/' in url:
                    if idx==5:
                        text='<html><body><section><h2>Experiment Setup</h2><p>For self-evolution, we perform LoRA-based fine-tuning on the proactive agent model using interaction trajectories and measured rewards.</p></section></body></html>'
                    else:
                        text='<html><body><section><h2>Experimental Results</h2><p>We find verified agent performance improves by 12.0 percent on held-out tasks.</p></section></body></html>'
                    return SimpleNamespace(status_code=200,text=text)
                return SimpleNamespace(status_code=200,text=f'<meta name="citation_title" content="{titles[idx]}"><blockquote class="abstract mathjax">Abstract: {abstracts[idx]}</blockquote>')
            public,private=build_primary_evidence_pool(storage=storage,corpus_path=corpus,requester=requester,augment_fresh_corpus_with_arxiv=False,coverage_anchor_count=2,carrier_probe_limit=1,now=now,min_interval_seconds=0,max_papers=5,cache_dir=root/"primary-cache")
        self.assertEqual(public["schema_version"],"1.1")
        self.assertTrue(public["summary"]["carrier_probe_required"])
        self.assertEqual((public["summary"]["carrier_probe_attempted"],public["summary"]["carrier_probe_rescued"],public["summary"]["carrier_probe_pending"]),(1,1,1))
        self.assertFalse(public["summary"]["source_coverage_exhausted"])
        self.assertEqual(public["summary"]["unreviewed_lane_linked_sources"],1)
        self.assertTrue(public["summary"]["candidate_generation_ready"])
        receipt=public["carrier_probe"]["portable_receipts"][0]
        self.assertEqual(receipt["live_rescue_eligible_lanes"],["parametric_model_state"])
        self.assertFalse(receipt["scientific_authority"])
        rescued=next(row for row in private["records"] if row["ref"]=="arXiv:2608.51005")
        self.assertIn("parametric_model_state",rescued["lane_keys"])

    def test_no_lane_carrier_probe_pending_blocks_exhaustion_without_rescue(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);now=datetime(2026,8,13,tzinfo=timezone.utc)
            titles={1:"Self-Evolving Agent Skill One",2:"Harness Evolution Agent Two",3:"Persistent Agent Memory Three",4:"Self-Evolving World Model Four",5:"Self-Evolving Autonomous Agent Strategy Alpha",6:"Self-Evolving Autonomous Agent Strategy Beta"}
            abstracts={idx:("A self-evolving agent skill harness improves adaptation." if idx<3 else ("Persistent agent memory improves a continual agent." if idx==3 else ("A self-evolving world model improves planning." if idx==4 else "A self-evolving autonomous agent iterates strategy from feedback."))) for idx in titles}
            papers=[{"paper_id":f"s2-{idx}","title":titles[idx],"year":2026,"abstract":abstracts[idx],"metadata":{"externalIds":{"ArXiv":f"2608.52{idx:03d}"},"publicationDate":f"2026-08-{14-idx:02d}","citationCount":0,"retrievalScore":0.0,"matches":[{"route":"topic"}]}} for idx in range(1,7)]
            corpus=root/"carrier-pending-corpus.json";corpus.write_text(json.dumps({"schema_version":"1.0","retrieved_at":"2026-08-13T00:00:00+00:00","papers":papers}),encoding="utf-8")
            discovery=root/"paper-first-problem-discovery";discovery.mkdir(parents=True)
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"schema_version":"1.0","runs":[{"run_id":"reviewed","source_refs":[f"arXiv:2608.52{i:03d}" for i in range(1,5)],"scientific_authority":False}]}),encoding="utf-8")
            def requester(url:str,*,timeout:float,headers:dict[str,str]):
                aid=url.rsplit('/',1)[-1];idx=int(aid[-1])
                if '/html/' in url:
                    return SimpleNamespace(status_code=200,text='<html><body><section><h2>Experimental Results</h2><p>We find verified performance improves by 11.0 percent on held-out tasks.</p></section></body></html>')
                return SimpleNamespace(status_code=200,text=f'<meta name="citation_title" content="{titles[idx]}"><blockquote class="abstract mathjax">Abstract: {abstracts[idx]}</blockquote>')
            public,_=build_primary_evidence_pool(storage=storage,corpus_path=corpus,requester=requester,augment_fresh_corpus_with_arxiv=False,coverage_anchor_count=2,carrier_probe_limit=1,now=now,min_interval_seconds=0,max_papers=5,cache_dir=root/"primary-cache")
        self.assertTrue(public["summary"]["carrier_probe_required"])
        self.assertEqual((public["summary"]["carrier_probe_rescued"],public["summary"]["carrier_probe_pending"]),(0,1))
        self.assertEqual(public["summary"]["unreviewed_lane_linked_sources"],0)
        self.assertFalse(public["summary"]["carrier_probe_complete"])
        self.assertFalse(public["summary"]["source_coverage_exhausted"])
        self.assertFalse(public["summary"]["candidate_generation_ready"])
        self.assertFalse(public["carrier_probe"]["scientific_authority"])

    def test_incomplete_arxiv_freshness_window_cannot_claim_source_coverage_exhausted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);storage=self.storage(root);corpus=self.corpus(root);discovery=root/"paper-first-problem-discovery";discovery.mkdir(parents=True)
            (discovery/"discovery-saturation-ledger.json").write_text(json.dumps({"schema_version":"1.0","runs":[{"source_refs":[f"arXiv:2608.0000{i}" for i in range(1,5)],"scientific_authority":False}]}),encoding="utf-8")
            def truncated_search(*,query:str,start:int,max_results:int,timeout:float,headers:dict[str,str]):
                entries=[]
                for offset in range(max_results):
                    idx=(offset%4)+1;aid=f"2608.0000{idx}"
                    entries.append(f'<entry><id>https://arxiv.org/abs/{aid}v1</id><title>Self-Evolving Agent Skills {idx}</title><summary>A self-evolving agent skill harness improves persistent adaptation.</summary><published>2026-08-0{idx}T00:00:00Z</published></entry>')
                return SimpleNamespace(status_code=200,text='<feed xmlns="http://www.w3.org/2005/Atom">'+''.join(entries)+'</feed>')
            public,private=build_primary_evidence_pool(storage=storage,corpus_path=corpus,requester=self.fake_requester,arxiv_search_requester=truncated_search,arxiv_queries=('q',),arxiv_query_interval_seconds=0,coverage_anchor_count=1,now=datetime(2026,8,13,tzinfo=timezone.utc),min_interval_seconds=0,max_papers=3,cache_dir=root/"primary-cache")
        self.assertTrue(public["summary"]["source_coverage_scheduler_active"])
        self.assertEqual(public["summary"]["unreviewed_lane_linked_sources"],0)
        self.assertFalse(public["summary"]["source_retrieval_complete"])
        self.assertFalse(public["summary"]["source_coverage_exhausted"])
        self.assertFalse(private["source_coverage"]["source_retrieval_complete"])
        self.assertTrue(any('FreshnessWindowTruncated' in row for row in public["discovery_errors"]))

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
        self.assertGreaterEqual(public["summary"]["typed_evidence_candidates"]["operational_assumptions"],4)
        self.assertGreaterEqual(public["summary"]["typed_evidence_candidates"]["measured_failures"],4)
        self.assertGreaterEqual(public["summary"]["typed_evidence_candidates"]["boundary_observations"],4)
        self.assertEqual(public["policy"]["typed_evidence_extraction_version"],TYPED_EVIDENCE_EXTRACTION_VERSION)
        self.assertTrue(public["policy"]["typed_evidence_candidates_are_not_ground_truth"])
        self.assertTrue(public["policy"]["typed_evidence_is_deterministic_and_bounded"])
        self.assertTrue(all("abstract" not in row and "empirical_facts" not in row and "typed_evidence" not in row for row in public["records"]))
        self.assertTrue(all(set(row["typed_evidence_counts"])=={"operational_assumptions","measured_failures","boundary_observations"} for row in public["records"]))
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
                    "typed_evidence":{"operational_assumptions":[{"section":"Method Assumptions","text":"We assume tool availability remains stationary during deployment.","text_sha256":"e"*64,"extraction_version":TYPED_EVIDENCE_EXTRACTION_VERSION}],"measured_failures":[{"section":"Results","text":f"We find method {idx} fails on 4/10 held-out tasks.","text_sha256":"f"*64,"extraction_version":TYPED_EVIDENCE_EXTRACTION_VERSION}],"boundary_observations":[{"section":"Analysis","text":"Results show a threshold regime below 40.0 percent success.","text_sha256":"9"*64,"extraction_version":TYPED_EVIDENCE_EXTRACTION_VERSION}]},
                    "fetched_at":"2026-08-13T05:00:00+00:00","primary_source_verified":True,
                    "empirical_fact_extraction_version":EMPIRICAL_FACT_EXTRACTION_VERSION,
                    "typed_evidence_extraction_version":TYPED_EVIDENCE_EXTRACTION_VERSION,
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
                    "typed_evidence":{"operational_assumptions":[],"measured_failures":[],"boundary_observations":[]},
                    "fetched_at":"2026-08-13T05:00:00+00:00","primary_source_verified":True,
                    "empirical_fact_extraction_version":"legacy-v0",
                    "typed_evidence_extraction_version":TYPED_EVIDENCE_EXTRACTION_VERSION,
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
