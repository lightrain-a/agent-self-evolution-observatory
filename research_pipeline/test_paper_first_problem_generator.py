from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, FORBIDDEN_DISCOVERY_LANES
from .paper_first_problem_gate_queue import build_problem_gate_queue
from .paper_first_problem_generator import run_problem_generator, write_problem_generator_state
from .paper_first_problem_generator_prompts import generator_prompt
from .test_paper_first_problem_discovery_contract import valid_candidate


class PaperFirstProblemGeneratorTest(unittest.TestCase):
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

    def pool(self, root: Path, now: datetime) -> Path:
        records = []
        for i in range(1, 5):
            records.append(
                {
                    "ref": f"arXiv:2608.0000{i}",
                    "title": f"Primary {i}",
                    "primary_url": f"https://arxiv.org/abs/2608.0000{i}",
                    "source_sha256": str(i) * 64,
                    "abstract_sha256": str(i + 4) * 64,
                    "abstract": f"Primary abstract fact {i} about self-evolving agents and bounded deployment evidence.",
                    "empirical_facts": [
                        {
                            "section": "Results",
                            "text": f"We find fulltext empirical fact {i} improves verified agent success by {10+i}.0 percent across held-out tasks.",
                            "text_sha256": str(i + 5) * 64,
                        }
                    ],
                    "typed_evidence": {
                        "operational_assumptions": [{"section":"Method Assumptions","text":"The method assumes stationary tool availability during deployment.","text_sha256":"a"*64}] if i==1 else [],
                        "measured_failures": [{"section":"Results","text":f"We find method {i} fails on 4/10 held-out tasks under the bounded condition.","text_sha256":"b"*64}],
                        "boundary_observations": [{"section":"Analysis","text":f"Results show a threshold regime for method {i}: success drops below 40.0 percent only when evidence is scarce.","text_sha256":"c"*64}],
                    },
                    "primary_source_verified": True,
                }
            )
        path = root / "primary.json"
        path.write_text(json.dumps({"status": "READY", "generated_at": now.isoformat(), "records": records}), encoding="utf-8")
        return path

    def raw_candidate(self, lane: str = "CONTRADICTION") -> dict:
        source = valid_candidate(lane)
        evidence = source["empirical_evidence"]
        return {
            "candidate_id": "AUTO-1",
            "title": source["title"],
            "discovery_lane": lane,
            "empirical_evidence": {
                "source_a": {key: evidence["source_a"][key] for key in ("ref", "claim", "evidence_role")},
                "source_b": {key: evidence["source_b"][key] for key in ("ref", "claim", "evidence_role")},
                "relation": evidence["relation"],
            },
            "lane_evidence": source["lane_evidence"],
            "irreducible_object": source["irreducible_object"],
            "mature_theory_baselines": source["mature_theory_baselines"],
            "reduction_falsifiability_contract": source["reduction_falsifiability_contract"],
            "same_information_nonreducibility": source["same_information_nonreducibility"],
            "exact_prediction": source["exact_prediction"],
            "strongest_same_information_baseline": source["strongest_same_information_baseline"],
            "domain_transfer_audit": source["domain_transfer_audit"],
            "saturation_scan": source["saturation_scan"],
            "cheapest_problem_falsifier": source["cheapest_problem_falsifier"],
            "endpoint_headroom_requirement": source["endpoint_headroom_requirement"],
        }

    def gen(self, candidates: list[dict], resolved: str = "doubao-seed-evolving", notes: str = ""):
        lane_search=[]
        for lane in DISCOVERY_LANES:
            matching=[candidate for candidate in candidates if candidate.get("discovery_lane")==lane]
            if matching:
                evidence=matching[0]["empirical_evidence"]
                lane_search.append({"lane":lane,"status":"CANDIDATE","source_refs":[evidence["source_a"]["ref"],evidence["source_b"]["ref"]],"reason":"A candidate survives the lane-level search audit."})
            else:
                lane_search.append({"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No current pair survives this lane search."})
        def responder(**kwargs):
            return {"text": json.dumps({"lane_search":lane_search,"candidates": candidates, "generation_notes": notes}), "resolved_model": resolved}
        return responder

    def review(
        self,
        verdict: str = "CLEAR",
        resolved: str = "glm-5-2-260617",
        matched: list[str] | None = None,
        grounded: bool = True,
        use_fulltext: bool = False,
        lane_verified: bool = True,
        lane: str = "CONTRADICTION",
    ):
        assumption_lane = lane == "ASSUMPTION_BREAK"
        support = {
            "source_a": {
                "supported": grounded,
                "evidence_source": "fulltext" if (use_fulltext or assumption_lane) else "abstract",
                "evidence_excerpt": "The method assumes stationary tool availability during deployment" if assumption_lane and grounded else ("fulltext empirical fact 1 improves verified agent success" if use_fulltext and grounded else ("Primary abstract fact 1 about self-evolving agents" if grounded else "unsupported excerpt")),
            },
            "source_b": {
                "supported": grounded,
                "evidence_source": "fulltext" if use_fulltext else "abstract",
                "evidence_excerpt": "fulltext empirical fact 2 improves verified agent success" if use_fulltext and grounded else ("Primary abstract fact 2 about self-evolving agents" if grounded else "unsupported excerpt"),
            },
        }
        def responder(**kwargs):
            return {
                "text": json.dumps(
                    {
                        "reviews": [
                            {
                                "candidate_id": "AUTO-1",
                                "verdict": verdict,
                                "lane_contract_verified": lane_verified,
                                "lane_contract_reason": "grounded relation satisfies lane" if lane_verified else "lane relation unsupported",
                                "source_claim_support": support,
                                "matched_patterns": matched or [],
                                "reduction_class": "VALID_HARD_VETO" if verdict == "BLOCK" and matched else "NONE",
                                "exact_reduction_test": "matched exact reduction" if verdict == "BLOCK" and matched else "none",
                                "strongest_reduction": "none" if verdict == "CLEAR" else "mature reduction",
                                "reason": "review",
                            }
                        ]
                    }
                ),
                "resolved_model": resolved,
            }
        return responder

    def test_generator_prompt_exposes_ten_allowed_and_three_forbidden_lanes(self) -> None:
        records = []
        for i in range(32):
            records.append(
                {
                    "ref": f"arXiv:2608.{10000+i:05d}",
                    "title": f"Primary {i}",
                    "primary_url": f"https://arxiv.org/abs/2608.{10000+i:05d}",
                    "source_sha256": str(i % 10) * 64,
                    "abstract": f"Verified abstract {i} about self-evolving agents.",
                    "empirical_facts": [{"section": "Results", "text": f"We find empirical result {i} improves held-out success by 12.0 percent across tasks."}],
                }
            )
        prompt = generator_prompt(records)
        self.assertIn(records[31]["ref"], prompt)
        self.assertEqual(sum(1 for row in records if row["ref"] in prompt), 32)
        for lane in DISCOVERY_LANES + FORBIDDEN_DISCOVERY_LANES:
            self.assertIn(lane, prompt)
        self.assertIn("lane_evidence", prompt)
        self.assertIn("OPERATIONAL_ASSUMPTION", prompt)

    def test_zero_candidates_is_valid_and_skips_reviewer(self) -> None:
        calls = []
        def reviewer(**kwargs):
            calls.append(1)
            raise AssertionError
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); auto = root / "auto.json"
            state = run_problem_generator(storage=self.storage(root), primary_pool_path=self.pool(root, now), auto_inbox_path=auto, generator_responder=self.gen([],notes="No empirical discovery lane survives the shared non-reduction gates."), reviewer_responder=reviewer, now=now)
            inbox = json.loads(auto.read_text())
            ledger = json.loads((root/"paper-first-problem-discovery"/"discovery-saturation-ledger.json").read_text())
        self.assertEqual(state["status"], "GENERATED_ZERO_CANDIDATES")
        self.assertEqual(calls, [])
        self.assertEqual(inbox["schema_version"], "2.0")
        self.assertEqual(inbox["candidates"], [])
        self.assertIn("No empirical discovery lane",state["generation_notes"])
        self.assertTrue(state["saturation_memory"]["current_run_recorded"])
        self.assertFalse(state["saturation_memory"]["scientific_authority"])
        self.assertEqual(len(ledger["runs"]),1)
        self.assertFalse(ledger["runs"][0]["scientific_authority"])
        self.assertTrue(state["policy"]["multi_lane_discovery_enabled"])
        self.assertEqual(tuple(state["policy"]["allowed_discovery_lanes"]), DISCOVERY_LANES)

    def test_identical_zero_candidate_pool_is_remembered_but_not_auto_authorized(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);storage=self.storage(root);pool=self.pool(root,now)
            first=run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto1.json",generator_responder=self.gen([],notes="zero-1"),now=now)
            second=run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto2.json",generator_responder=self.gen([],notes="zero-2"),now=now)
        self.assertEqual(first["saturation_memory"]["prior_identical_zero_runs"],0)
        self.assertEqual(second["saturation_memory"]["prior_identical_zero_runs"],1)
        self.assertFalse(second["saturation_memory"]["scientific_authority"])
        self.assertFalse(second["policy"]["automatic_method_authority"])
        self.assertFalse(second["policy"]["automatic_p0_authority"])

    def test_zero_candidates_without_rationale_is_generator_error_not_scientific_saturation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=self.gen([]),now=now)
            ledger_path=root/"paper-first-problem-discovery"/"discovery-saturation-ledger.json"
        self.assertEqual(state["status"],"GENERATOR_ERROR_ZERO_AUTHORITY")
        self.assertIn("zero-candidate-generation-notes-required",state["error"])
        self.assertFalse(state["saturation_memory"]["current_run_recorded"])
        self.assertFalse(ledger_path.exists())

    def test_public_writer_redacts_private_paths_but_keeps_raw_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); json_path = root / "public.json"; js_path = root / "public.js"
            internal = write_problem_generator_state(json_path=json_path, js_path=js_path, storage=self.storage(root), primary_pool_path=self.pool(root, now), auto_inbox_path=root / "auto.json", generator_responder=self.gen([],notes="No empirical discovery lane survives."), now=now)
            public = json.loads(json_path.read_text())
        self.assertIn("primary_pool_path", internal)
        self.assertNotIn("primary_pool_path", public)
        self.assertNotIn("auto_inbox_path", public)
        self.assertNotIn("archived_previous_auto_inbox", public)
        self.assertNotIn("path", public["raw_artifacts"]["generator"])
        self.assertEqual(public["raw_artifacts"]["generator"]["sha256"], internal["raw_artifacts"]["generator"]["sha256"])

    def test_public_writer_carries_zero_authority_review_receipts_across_hosts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);json_path=root/"public.json";js_path=root/"public.js"
            old_refs=[f"arXiv:old-{i}" for i in range(4)]
            json_path.write_text(json.dumps({"schema_version":"2.1","run_id":"remote-old","status":"GENERATED_ZERO_CANDIDATES","summary":{"primary_evidence_records":4},"policy":{},"saturation_memory":{"current_run_recorded":True,"portable_review_receipts":[{"run_id":"remote-old","source_refs":old_refs,"status":"GENERATED_ZERO_CANDIDATES","scientific_authority":False}]}}),encoding="utf-8")
            state=write_problem_generator_state(json_path=json_path,js_path=js_path,storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=self.gen([],notes="No empirical discovery lane survives current evidence."),now=now)
            public=json.loads(json_path.read_text())
        receipts=public["saturation_memory"]["portable_review_receipts"]
        self.assertEqual(len(receipts),2)
        self.assertEqual(receipts[0]["run_id"],"remote-old")
        self.assertEqual(receipts[-1]["run_id"],state["run_id"])
        self.assertEqual(len(receipts[-1]["source_refs"]),4)
        self.assertTrue(all(row["scientific_authority"] is False for row in receipts))
        self.assertTrue(public["policy"]["portable_review_receipts_are_scheduler_metadata_only"])

    def test_saturation_skip_inherits_primary_transaction_review_receipts_without_model_calls(self) -> None:
        calls=[]
        def responder(**kwargs):
            calls.append(1); raise AssertionError("coverage-saturated writer must not call a model")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); now=datetime(2026,8,13,tzinfo=timezone.utc); storage=self.storage(root); pool=self.pool(root,now)
            receipts=[]
            for idx in (1,2):
                receipts.append({"run_id":f"private-{idx}","pool_sha256":str(idx)*64,"negative_space_sha256":"f"*64,"source_refs":[f"arXiv:{idx}-{j}" for j in range(4)],"status":"GENERATED_ZERO_CANDIDATES","requested_model":"ark-code-latest","resolved_model":"doubao-seed-evolving","raw_sha256":"e"*64,"scientific_authority":False,"from_private_saturation_ledger":True})
            payload=json.loads(pool.read_text()); payload["source_coverage"]={"coverage_exhausted":True,"eligible_lane_linked_sources":8,"reviewed_lane_linked_sources":8,"unreviewed_lane_linked_sources":0,"unreviewed_no_lane_sources":0,"portable_review_receipts":receipts,"scientific_authority":False}; pool.write_text(json.dumps(payload),encoding="utf-8")
            public_json=root/"generator-public.json"; public_js=root/"generator-public.js"
            state=write_problem_generator_state(json_path=public_json,js_path=public_js,storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto.json",generator_responder=responder,reviewer_responder=responder,now=now)
            public=json.loads(public_json.read_text())
        self.assertEqual(state["status"],"SKIPPED_SOURCE_COVERAGE_SATURATED")
        self.assertEqual(calls,[])
        inherited=public["saturation_memory"]["portable_review_receipts"]
        self.assertEqual([row["run_id"] for row in inherited],["private-1","private-2"])
        self.assertTrue(all(row["scientific_authority"] is False for row in inherited))
        self.assertTrue(public["policy"]["primary_source_coverage_receipts_are_inherited_transactionally"])

    def test_lane_grounded_source_coverage_saturation_makes_zero_model_calls(self) -> None:
        calls=[]
        def responder(**kwargs):
            calls.append(1); raise AssertionError("coverage-saturated primary pool must not call a model")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);pool=self.pool(root,now);payload=json.loads(pool.read_text());payload["source_coverage"]={"coverage_exhausted":True,"eligible_lane_linked_sources":4,"reviewed_lane_linked_sources":4,"unreviewed_lane_linked_sources":0,"unreviewed_no_lane_sources":1,"scientific_authority":False};pool.write_text(json.dumps(payload),encoding="utf-8")
            auto=root/"auto.json";state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=responder,reviewer_responder=responder,now=now);inbox=json.loads(auto.read_text())
        self.assertEqual(state["status"],"SKIPPED_SOURCE_COVERAGE_SATURATED")
        self.assertEqual(calls,[])
        self.assertEqual(inbox["candidates"],[])
        self.assertTrue(state["policy"]["source_coverage_saturation_skips_model_call"])
        self.assertTrue(state["policy"]["source_coverage_saturation_is_compute_control_not_scientific_negative"])
        self.assertTrue(state["policy"]["new_lane_grounded_primary_source_reopens_generation"])
        self.assertTrue(state["source_coverage"]["coverage_exhausted"])
        self.assertFalse(state["source_coverage"]["scientific_authority"])
        self.assertFalse(state["policy"]["automatic_method_authority"]);self.assertFalse(state["policy"]["automatic_p0_authority"])

    def test_reviewer_blocked_memory_detects_repeated_reduction_basin(self) -> None:
        captured = {}
        def generator(**kwargs):
            captured["prompt"] = kwargs["prompt"]
            priority=["CONTRADICTION","CONVERGENT_FAILURE","UNEXPLAINED_BOUNDARY","ASSUMPTION_BREAK"]
            lane_search=[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No pair survives this lane after prior reductions."} for lane in priority]
            return {"text": json.dumps({"lane_search":lane_search,"candidates": [], "generation_notes": "No new problem survives prior reviewer reductions."}), "resolved_model": "doubao-seed-evolving"}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); now=datetime(2026,8,13,tzinfo=timezone.utc)
            archive=root/"paper-first-problem-discovery"/"archive"; archive.mkdir(parents=True)
            for idx in range(5):
                candidate={"candidate_id":f"AUTO-{idx+1}","title":f"Memory monotonicity variant {idx+1}","discovery_lane":"ASSUMPTION_BREAK","empirical_evidence":{"source_a":{"ref":"arXiv:2608.00001"},"source_b":{"ref":"arXiv:2608.00002"}},"semantic_reduction_review":{"verdict":"BLOCK","lane_contract_verified":True,"source_claims_grounded":True,"matched_patterns":["procedural-memory-nonmonotonicity"],"strongest_reduction":"procedural-memory-nonmonotonicity","reason":"Captured by nonmonotonic belief revision."}}
                (archive/f"auto-inbox-{idx}.json").write_text(json.dumps({"generator_run_id":f"old-{idx}","candidates":[candidate]}),encoding="utf-8")
            state=run_problem_generator(storage=storage,primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=generator,now=now)
        memory=state["saturation_memory"]["blocked_problem_memory"]
        self.assertEqual(memory["blocked_candidate_attempts"],5)
        self.assertEqual(memory["top_reduction_basin"]["pattern"],"procedural-memory-nonmonotonicity")
        self.assertEqual(memory["top_reduction_basin"]["count"],5)
        self.assertTrue(memory["repeated_reduction_basin"]); self.assertTrue(memory["search_escape_required"])
        self.assertIn("REVIEWER-PROVEN DEAD-END MEMORY",captured["prompt"])
        self.assertIn("procedural-memory-nonmonotonicity",captured["prompt"])

    def test_portable_blocked_problem_memory_survives_host_switch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); now=datetime(2026,8,13,tzinfo=timezone.utc); j=root/"generator.json"; js=root/"generator.js"
            row={"signature_id":"deadbeef","title":"Prior blocked object","discovery_lane":"CONVERGENT_FAILURE","matched_patterns":["artifact-uptake-after-retrieval"],"strongest_reduction":"artifact-uptake-after-retrieval","lane_contract_verified":True,"source_claims_grounded":True,"scientific_authority":False}
            j.write_text(json.dumps({"status":"GENERATED_ZERO_CANDIDATES","summary":{"primary_evidence_records":4},"saturation_memory":{"blocked_problem_memory":{"portable_blocked_problem_memory":[row],"scientific_authority":False}}}),encoding="utf-8")
            def generator(**kwargs):
                priority=["CONTRADICTION","ASSUMPTION_BREAK","UNEXPLAINED_BOUNDARY","CONVERGENT_FAILURE"]
                lane_search=[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No pair."} for lane in priority]
                return {"text":json.dumps({"lane_search":lane_search,"candidates":[],"generation_notes":"No new problem survives."}),"resolved_model":"doubao-seed-evolving"}
            write_problem_generator_state(json_path=j,js_path=js,storage=storage,primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=generator,now=now)
            public=json.loads(j.read_text())
        memory=public["saturation_memory"]["blocked_problem_memory"]
        self.assertEqual(memory["blocked_candidate_attempts"],1); self.assertEqual(memory["portable_blocked_problem_memory"][0]["signature_id"],"deadbeef")

    def test_exact_excerpt_machine_location_survives_declared_source_mismatch(self) -> None:
        base=self.review("CLEAR")
        def reviewer(**kwargs):
            response=base(**kwargs); payload=json.loads(response["text"])
            for source in payload["reviews"][0]["source_claim_support"].values(): source["evidence_source"]="fulltext"
            response["text"]=json.dumps(payload); return response
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); now=datetime(2026,8,13,tzinfo=timezone.utc); auto=root/"auto.json"
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=auto,generator_responder=self.gen([self.raw_candidate()]),reviewer_responder=reviewer,now=now)
            review=json.loads(auto.read_text())["candidates"][0]["semantic_reduction_review"]
        grounding=review["source_claim_grounding"]["source_a"]
        self.assertTrue(review["source_claims_grounded"]); self.assertEqual(review["verdict"],"CLEAR")
        self.assertEqual(grounding["evidence_source"],"abstract"); self.assertEqual(grounding["declared_evidence_source"],"fulltext"); self.assertFalse(grounding["declared_source_matches"])
        self.assertTrue(state["policy"]["exact_excerpt_location_is_machine_inferred"])

    def test_zero_candidates_with_complete_lane_audit_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); now=datetime(2026,8,13,tzinfo=timezone.utc)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=self.gen([],notes="All four lanes were audited; none survives."),now=now)
        self.assertEqual(state["status"],"GENERATED_ZERO_CANDIDATES")
        self.assertTrue(state["search_diagnostics"]["lane_search_complete"])
        self.assertEqual({row["lane"] for row in state["search_diagnostics"]["lane_search"]},set(DISCOVERY_LANES))
        self.assertTrue(all(row["status"]=="NO_PAIR" for row in state["search_diagnostics"]["lane_search"]))
        self.assertFalse(state["search_diagnostics"]["scientific_authority"])

    def test_missing_lane_audit_is_generator_error_without_retry(self) -> None:
        calls=[]
        def responder(**kwargs):
            calls.append(1)
            lane_search=[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No pair."} for lane in DISCOVERY_LANES[:-1]]
            return {"text":json.dumps({"lane_search":lane_search,"candidates":[],"generation_notes":"Incomplete audit."}),"resolved_model":"doubao-seed-evolving"}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); now=datetime(2026,8,13,tzinfo=timezone.utc)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=responder,now=now)
        self.assertEqual(state["status"],"GENERATOR_ERROR_ZERO_AUTHORITY")
        self.assertIn("generator-lane-search-must-cover-all-lanes",state["error"])
        self.assertEqual(calls,[1])
        self.assertFalse(state["search_diagnostics"]["lane_search_complete"])

    def test_lane_audit_candidate_pair_must_match_candidate(self) -> None:
        candidate=self.raw_candidate("CONTRADICTION")
        def responder(**kwargs):
            lane_search=[]
            for lane in DISCOVERY_LANES:
                if lane=="CONTRADICTION": lane_search.append({"lane":lane,"status":"CANDIDATE","source_refs":["arXiv:2608.00003","arXiv:2608.00004"],"reason":"Wrong pair."})
                else: lane_search.append({"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No pair."})
            return {"text":json.dumps({"lane_search":lane_search,"candidates":[candidate],"generation_notes":"candidate"}),"resolved_model":"doubao-seed-evolving"}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); now=datetime(2026,8,13,tzinfo=timezone.utc)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=responder,now=now)
        self.assertEqual(state["status"],"GENERATOR_ERROR_ZERO_AUTHORITY")
        self.assertIn("generator-lane-search-candidate-pair-mismatch",state["error"])

    def test_blocked_lane_history_prioritizes_underexplored_lanes(self) -> None:
        captured={}
        def generator(**kwargs):
            captured["prompt"]=kwargs["prompt"]
            priority=[lane for lane in DISCOVERY_LANES if lane!="ASSUMPTION_BREAK"]+["ASSUMPTION_BREAK"]
            lane_search=[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No pair."} for lane in priority]
            return {"text":json.dumps({"lane_search":lane_search,"candidates":[],"generation_notes":"No lane survives."}),"resolved_model":"doubao-seed-evolving"}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); storage=self.storage(root); now=datetime(2026,8,13,tzinfo=timezone.utc)
            archive=root/"paper-first-problem-discovery"/"archive"; archive.mkdir(parents=True)
            for idx in range(4):
                c={"candidate_id":f"A{idx}","title":"Old assumption","discovery_lane":"ASSUMPTION_BREAK","empirical_evidence":{"source_a":{"ref":"arXiv:2608.00001"},"source_b":{"ref":"arXiv:2608.00002"}},"semantic_reduction_review":{"verdict":"BLOCK","lane_contract_verified":True,"source_claims_grounded":True,"matched_patterns":["procedural-memory-nonmonotonicity"],"strongest_reduction":"procedural-memory-nonmonotonicity"}}
                (archive/f"auto-inbox-{idx}.json").write_text(json.dumps({"generator_run_id":f"old-{idx}","candidates":[c]}),encoding="utf-8")
            state=run_problem_generator(storage=storage,primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=generator,now=now)
        expected=[lane for lane in DISCOVERY_LANES if lane!="ASSUMPTION_BREAK"]+["ASSUMPTION_BREAK"]
        self.assertEqual(state["search_diagnostics"]["lane_search_priority"],expected)
        self.assertIn('"lane_search_priority":'+json.dumps(expected,separators=(",",":")),captured["prompt"])

    def test_stale_pool_makes_zero_api_calls(self) -> None:
        calls = []
        def responder(**kwargs):
            calls.append(1)
            raise AssertionError
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); old = now - timedelta(hours=72)
            state = run_problem_generator(storage=self.storage(root), primary_pool_path=self.pool(root, old), auto_inbox_path=root / "auto.json", generator_responder=responder, reviewer_responder=responder, now=now)
        self.assertEqual(state["status"], "SKIPPED_STALE_PRIMARY_EVIDENCE")
        self.assertEqual(calls, [])

    def test_malformed_generator_archives_raw_and_clears_auto_inbox(self) -> None:
        def bad(**kwargs):
            return {"text": "{bad json", "resolved_model": "doubao-seed-evolving"}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); auto = root / "auto.json"; auto.write_text(json.dumps({"candidates": [{"candidate_id": "OLD"}]}))
            state = run_problem_generator(storage=self.storage(root), primary_pool_path=self.pool(root, now), auto_inbox_path=auto, generator_responder=bad, now=now)
            inbox = json.loads(auto.read_text())
            raw_exists = Path(state["raw_artifacts"]["generator"]["path"]).exists()
        self.assertEqual(state["status"], "GENERATOR_ERROR_ZERO_AUTHORITY")
        self.assertTrue(raw_exists)
        self.assertEqual(inbox["candidates"], [])
        self.assertTrue(state["archived_previous_auto_inbox"])

    def test_each_allowed_lane_can_be_structurally_reviewed_and_only_reach_human_design(self) -> None:
        for lane in DISCOVERY_LANES:
            with self.subTest(lane=lane), tempfile.TemporaryDirectory() as td:
                root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); auto = root / "auto.json"; pool = self.pool(root, now)
                state = run_problem_generator(storage=self.storage(root), primary_pool_path=pool, auto_inbox_path=auto, generator_responder=self.gen([self.raw_candidate(lane)]), reviewer_responder=self.review(lane=lane), now=now)
                queue = build_problem_gate_queue(root / "manual.json", auto_inbox_path=auto, primary_pool_path=pool, storage=self.storage(root))
            self.assertEqual(state["summary"]["generated_by_lane"][lane], 1)
            self.assertEqual(state["summary"]["structurally_reviewable_by_lane"][lane], 1)
            self.assertEqual(state["summary"]["semantic_clear_by_lane"][lane], 1)
            self.assertEqual((queue["summary"]["passed_problem_gate"], queue["summary"]["paper_design_eligible"]), (1, 1))
            self.assertEqual(queue["passed"][0]["discovery_lane"], lane)
            self.assertEqual((queue["summary"]["method_authorized"], queue["summary"]["p0_authorized"]), (0, 0))

    def test_reviewer_clear_without_lane_verification_is_forced_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); auto = root / "auto.json"; pool = self.pool(root, now)
            state = run_problem_generator(storage=self.storage(root), primary_pool_path=pool, auto_inbox_path=auto, generator_responder=self.gen([self.raw_candidate("CONVERGENT_FAILURE")]), reviewer_responder=self.review("CLEAR", lane_verified=False), now=now)
            inbox = json.loads(auto.read_text())
        review = inbox["candidates"][0]["semantic_reduction_review"]
        self.assertFalse(review["lane_contract_verified"])
        self.assertEqual(review["verdict"], "BLOCK")
        self.assertEqual(state["summary"]["semantic_clear"], 0)

    def test_rejected_saturation_pattern_is_normalized_and_sent_to_independent_reviewer(self) -> None:
        candidate=self.raw_candidate("ASSUMPTION_BREAK")
        candidate["saturation_scan"]={"checked":True,"matched_patterns":["procedural-memory-nonmonotonicity considered and rejected because the supplied evidence lacks same-information conflict"]}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json";pool=self.pool(root,now)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=self.gen([candidate]),reviewer_responder=self.review("CLEAR",lane="ASSUMPTION_BREAK"),now=now)
            inbox=json.loads(auto.read_text())
        scan=inbox["candidates"][0]["saturation_scan"]
        self.assertEqual(scan["matched_patterns"],[])
        self.assertEqual(scan["rejected_patterns"][0]["key"],"procedural-memory-nonmonotonicity")
        self.assertEqual(scan["invalid_entries"],[])
        self.assertEqual(state["summary"]["structurally_reviewable"],1)
        self.assertEqual(state["summary"]["semantic_clear"],1)

    def test_freeform_unknown_saturation_entry_blocks_before_reviewer(self) -> None:
        candidate=self.raw_candidate("CONTRADICTION")
        candidate["saturation_scan"]={"checked":True,"matched_patterns":["some unknown collision explanation"]}
        calls=[]
        def reviewer(**kwargs):calls.append(1);raise AssertionError
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=self.gen([candidate]),reviewer_responder=reviewer,now=now)
        self.assertEqual(state["summary"]["structurally_reviewable"],0)
        self.assertEqual(calls,[])

    def test_lane_role_mismatch_blocks_before_reviewer(self) -> None:
        candidate = self.raw_candidate("ASSUMPTION_BREAK")
        candidate["empirical_evidence"]["source_a"]["evidence_role"] = "EMPIRICAL_FACT"
        calls = []
        def reviewer(**kwargs):
            calls.append(1)
            raise AssertionError
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc)
            state = run_problem_generator(storage=self.storage(root), primary_pool_path=self.pool(root, now), auto_inbox_path=root / "auto.json", generator_responder=self.gen([candidate]), reviewer_responder=reviewer, now=now)
        self.assertEqual(state["summary"]["generated"], 1)
        self.assertEqual(state["summary"]["structurally_reviewable"], 0)
        self.assertEqual(calls, [])
        self.assertEqual(state["summary"]["semantic_blocked_by_lane"]["ASSUMPTION_BREAK"], 1)

    def test_fulltext_fact_excerpt_can_ground_independent_reviewer_claims(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); auto = root / "auto.json"; pool = self.pool(root, now)
            state = run_problem_generator(storage=self.storage(root), primary_pool_path=pool, auto_inbox_path=auto, generator_responder=self.gen([self.raw_candidate()]), reviewer_responder=self.review("CLEAR", use_fulltext=True), now=now)
            inbox = json.loads(auto.read_text())
        review = inbox["candidates"][0]["semantic_reduction_review"]
        self.assertTrue(review["source_claims_grounded"])
        self.assertEqual(review["source_claim_grounding"]["source_a"]["evidence_source"], "fulltext")
        self.assertEqual(review["verdict"], "CLEAR")
        self.assertEqual(state["summary"]["semantic_clear"], 1)

    def test_semantic_blocker_prevents_problem_gate_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); auto = root / "auto.json"; pool = self.pool(root, now)
            state = run_problem_generator(storage=self.storage(root), primary_pool_path=pool, auto_inbox_path=auto, generator_responder=self.gen([self.raw_candidate()]), reviewer_responder=self.review("BLOCK", matched=["update-order-path-dependence"]), now=now)
            queue = build_problem_gate_queue(root / "manual.json", auto_inbox_path=auto, primary_pool_path=pool, storage=self.storage(root))
        self.assertEqual(state["summary"]["semantic_blocked"], 1)
        self.assertEqual(queue["summary"]["passed_problem_gate"], 0)
        self.assertTrue(any(value == "semantic-reduction-review-block" or value.startswith("saturation-proven-hard-reduction:") for value in queue["blocked"][0]["blockers"]))

    def test_same_resolved_model_is_not_independent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); auto = root / "auto.json"; pool = self.pool(root, now)
            state = run_problem_generator(storage=self.storage(root), primary_pool_path=pool, auto_inbox_path=auto, generator_responder=self.gen([self.raw_candidate()], resolved="glm-5-2-260617"), reviewer_responder=self.review("CLEAR", resolved="glm-5-2-260617"), now=now)
            inbox = json.loads(auto.read_text())
        review = inbox["candidates"][0]["semantic_reduction_review"]
        self.assertFalse(review["independent_resolved_model"])
        self.assertEqual(review["verdict"], "BLOCK")
        self.assertEqual(state["summary"]["semantic_clear"], 0)

    def test_reviewer_clear_cannot_pass_if_source_excerpt_is_not_primary_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); now = datetime(2026, 8, 13, tzinfo=timezone.utc); auto = root / "auto.json"; pool = self.pool(root, now)
            state = run_problem_generator(storage=self.storage(root), primary_pool_path=pool, auto_inbox_path=auto, generator_responder=self.gen([self.raw_candidate()]), reviewer_responder=self.review("CLEAR", grounded=False), now=now)
            inbox = json.loads(auto.read_text())
            queue = build_problem_gate_queue(root / "manual.json", auto_inbox_path=auto, primary_pool_path=pool, storage=self.storage(root))
        review = inbox["candidates"][0]["semantic_reduction_review"]
        self.assertFalse(review["source_claims_grounded"])
        self.assertEqual(review["verdict"], "BLOCK")
        self.assertEqual(state["summary"]["semantic_clear"], 0)
        self.assertEqual(queue["summary"]["passed_problem_gate"], 0)
        self.assertTrue(any(value in {"semantic-reduction-review-block", "source-claim-grounding-failed"} for value in queue["blocked"][0]["blockers"]))


if __name__ == "__main__":
    unittest.main()
