from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import StorageSettings
from .paper_first_problem_discovery_contract import DISCOVERY_LANES, DISCOVERY_OPERATOR_VERSION, FORBIDDEN_DISCOVERY_LANES
from .paper_first_problem_gate_queue import build_problem_gate_queue
from .paper_first_problem_generator import _ark, _durable_principle_dead_end_examples, _evidence_excerpt_matches, _normalize_lane_search, _principle_dead_end_reentry_audit, _provider_request_audit, _repair_block_only_reviewer_outer_braces, recover_archived_block_only_reviewer_raw, replay_problem_generator_raw, resume_semantic_reviewer, run_problem_generator, write_problem_generator_state
from .paper_first_problem_generator_prompts import generator_prompt, reviewer_prompt
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
                refs=list(dict.fromkeys([evidence["source_a"]["ref"],evidence["source_b"]["ref"]]))
                lane_search.append({"lane":lane,"status":"CANDIDATE","source_refs":refs,"reason":"A candidate survives the lane-level search audit."})
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

    def test_render_normalized_excerpt_match_ignores_only_numeric_duplication(self) -> None:
        excerpt="EnvScaler reward remains near 0.56 with 8 or 16 tokens per experience, rises sharply to 0.637 with 32"
        rendered="EnvScaler reward remains near 0.560.56 with 88 or 1616 tokens per experience, rises sharply to 0.6370.637 with 3232, and then fluctuates."
        paraphrase="EnvScaler performance is roughly flat at small context sizes before improving near a larger latent capacity."
        self.assertTrue(_evidence_excerpt_matches(excerpt,rendered))
        self.assertFalse(_evidence_excerpt_matches(paraphrase,rendered))

    def test_block_only_reviewer_recovery_inserts_only_missing_outer_braces(self) -> None:
        raw='```json\n{"reviews":[{"candidate_id":"AUTO-1","verdict":"BLOCK","reason":"first"},{"candidate_id":"AUTO-2","verdict":"BLOCK","reason":"second"}]}\n```'
        malformed=raw.replace('"reason":"first"}', '"reason":"first"', 1).replace('"reason":"second"}', '"reason":"second"', 1)
        payload,repaired,offsets=_repair_block_only_reviewer_outer_braces(malformed)
        self.assertEqual([row["candidate_id"] for row in payload["reviews"]],["AUTO-1","AUTO-2"])
        self.assertEqual(len(offsets),2)
        self.assertTrue(all(row["verdict"]=="BLOCK" for row in json.loads(repaired)["reviews"]))
        self.assertIn('"reason":"first"',repaired);self.assertIn('"reason":"second"',repaired)

    def test_block_only_reviewer_recovery_refuses_clear_or_inner_truncation(self) -> None:
        clear='{"reviews":[{"candidate_id":"AUTO-1","verdict":"CLEAR","reason":"clear" ]}'
        truncated='{"reviews":[{"candidate_id":"AUTO-1","verdict":"BLOCK","reason":"cut]}'
        self.assertIsNone(_repair_block_only_reviewer_outer_braces(clear)[0])
        self.assertIsNone(_repair_block_only_reviewer_outer_braces(truncated)[0])

    def test_archived_block_only_reviewer_recovery_writes_zero_authority_receipt(self) -> None:
        malformed='{"reviews":[{"candidate_id":"AUTO-1","verdict":"BLOCK","reason":"first",{"candidate_id":"AUTO-2","verdict":"BLOCK","reason":"second"]}'
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);raw_path=root/"review.txt";raw_path.write_text(malformed);sha=hashlib.sha256(malformed.encode()).hexdigest()
            receipt=recover_archived_block_only_reviewer_raw(storage=self.storage(root),reviewer_raw_path=raw_path,reviewer_raw_sha256=sha,resolved_model="minimax-m3",run_id="recover-test")
            receipts=list((root/"paper-first-problem-discovery"/"reviewer-recoveries").glob("*-receipt.json"))
        self.assertEqual(receipt["status"],"PARSE_REPAIRED_MISSING_REVIEW_OUTER_BRACES_BLOCK_ONLY_ZERO_AUTHORITY")
        self.assertEqual(receipt["inserted_closing_brace_count"],2)
        self.assertEqual(receipt["provider_calls_executed"],0);self.assertFalse(receipt["scientific_authority"])
        self.assertEqual(len(receipts),1)

    def test_durable_principle_dead_end_memory_prioritizes_current_source_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"memory.json"
            rows=[{"source_candidate_id":f"RECENT-{i}","title":f"recent {i}","search_primitive":"CONTRADICTION","current_source_refs":[f"arXiv:other{i}"],"dead_end_certified":True,"counter_explanation":{"reopen_condition":"new evidence"}} for i in range(14)]
            rows.insert(0,{"source_candidate_id":"OLD-DIRECT-MATCH","title":"direct match","search_primitive":"CONVERGENT_FAILURE","current_source_refs":["arXiv:target-a","arXiv:target-b"],"dead_end_certified":True,"counter_explanation":{"reopen_condition":"new matched evidence"}})
            path.write_text(json.dumps({"shadow_dead_end_memory":{"blocked_objects":rows}}),encoding="utf-8")
            selected=_durable_principle_dead_end_examples(path,limit=12,current_refs={"arXiv:target-a","arXiv:target-b"})
        self.assertEqual(len(selected),12)
        self.assertEqual(selected[0]["source_candidate_id"],"OLD-DIRECT-MATCH")
        self.assertIn("OLD-DIRECT-MATCH",[row["source_candidate_id"] for row in selected])

    def test_exact_source_lane_principle_dead_end_reentry_is_machine_blocked(self) -> None:
        candidate=self.raw_candidate("CONVERGENT_FAILURE")
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"memory.json"
            refs=[candidate["empirical_evidence"]["source_a"]["ref"],candidate["empirical_evidence"]["source_b"]["ref"]]
            path.write_text(json.dumps({"shadow_dead_end_memory":{"blocked_objects":[{"source_candidate_id":"OLD-BASIN","search_primitive":"CONVERGENT_FAILURE","current_source_refs":refs,"dead_end_certified":True,"counter_explanation":{"reopen_condition":"reopen only with new evidence"}}]}}),encoding="utf-8")
            audit=_principle_dead_end_reentry_audit(candidate,path)
        self.assertTrue(audit["blocked"])
        self.assertEqual(audit["matched_source_candidate_ids"],["OLD-BASIN"])
        candidate["principle_dead_end_reentry_audit"]=audit
        from .paper_first_problem_discovery_contract import audit_problem_candidate
        result=audit_problem_candidate(candidate,require_semantic_review=False,allow_pending_reduction_for_semantic_review=True)
        self.assertFalse(result["passed"])
        self.assertIn("principle-dead-end-exact-source-reentry:OLD-BASIN",result["blockers"])

    def test_legacy_principle_closure_blocks_only_exact_reverified_evidence(self) -> None:
        candidate=self.raw_candidate("UNEXPLAINED_BOUNDARY");ref=candidate["empirical_evidence"]["source_a"]["ref"]
        candidate["empirical_evidence"]["source_b"]["ref"]=ref
        closed_a="d"*64;closed_b="e"*64
        grounding={
            "source_a":{"ref":ref,"grounded":True,"evidence_sha256":closed_a,"evidence_sha256_verified":True},
            "source_b":{"ref":ref,"grounded":True,"evidence_sha256":closed_b,"evidence_sha256_verified":True},
        }
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"memory.json"
            path.write_text(json.dumps({"shadow_dead_end_memory":{"blocked_objects":[{
                "source_candidate_id":"LEGACY-CLOSURE","search_primitive":"","current_source_refs":[ref],"dead_end_certified":True,
                "fresh_phenomenon_closure":{"source_ref":ref,"closed_evidence_sha256":[closed_a,closed_b]},
                "counter_explanation":{"reopen_condition":"new exact evidence"},
            }]}}),encoding="utf-8")
            exact=_principle_dead_end_reentry_audit(candidate,path,grounding)
            fresh_grounding=json.loads(json.dumps(grounding));fresh_grounding["source_b"]["evidence_sha256"]="f"*64
            fresh=_principle_dead_end_reentry_audit(candidate,path,fresh_grounding)
        self.assertTrue(exact["blocked"])
        self.assertEqual(exact["matches"][0]["match_kind"],"CERTIFIED_EXACT_EVIDENCE_CLOSURE")
        self.assertEqual(set(exact["matches"][0]["grounded_evidence_sha256"]),{closed_a,closed_b})
        self.assertFalse(fresh["blocked"])

    def test_durable_principle_dead_end_memory_preserves_reopen_contract(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"memory.json"
            path.write_text(json.dumps({"shadow_dead_end_memory":{"blocked_objects":[{
                "source_candidate_id":"AUTO-X","title":"cross-treatment false contradiction","search_primitive":"CONTRADICTION","current_source_refs":["arXiv:1","arXiv:2"],"dead_end_certified":True,
                "strongest_reduction":"the interventions use different causal surfaces",
                "counter_explanation":{"opposite_principle":"align treatment semantics before comparing effects","opposite_search_seed":"search same frozen executor treatment","reopen_condition":"reopen only with identical intervention surface"}
            }]}}),encoding="utf-8")
            rows=_durable_principle_dead_end_examples(path)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["source_candidate_id"],"AUTO-X")
        self.assertTrue(rows[0]["dead_end_certified"])
        self.assertIn("identical intervention surface",rows[0]["reopen_condition"])
        self.assertFalse(rows[0]["scientific_authority"])

    def test_generator_prompt_exposes_four_live_and_three_forbidden_lanes(self) -> None:
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
        for field in ("source_a_intervention","source_b_intervention","intervention_surface_match","executor_state_match","comparator_match","endpoint_match","timing_match","treatment_equivalence_argument","shared_intervention_semantics","shared_adaptation_stage"):
            self.assertIn(field,prompt)
        self.assertIn("cross-treatment",prompt.lower())
        self.assertIn("MUST use status=REDUCIBLE",prompt)
        self.assertIn("GENERATOR/REVIEWER REDUCTION SPLIT",prompt)
        self.assertIn("NEEDS_EXACT_REDUCTION_TEST",prompt)
        for field in ("ex_ante_prediction","distinguishing_prediction","cannot_express","reduction_class","exact_reduction_test","reduction_falsifiability_contract","same_observable_information_checked","ex_ante_exact_prediction_checked","distinguishing_prediction_checked","scope_boundary_checked","all_exact_reduction_tests_resolved"):
            self.assertIn(field,prompt)
        self.assertIn("full-parameter SFT are distinct interventions",prompt)


    def test_reviewer_prompt_exposes_numeric_lane_source_minima(self) -> None:
        candidate=self.raw_candidate("UNEXPLAINED_BOUNDARY")
        evidence={
            "arXiv:2608.00001":{"ref":"arXiv:2608.00001","title":"A","source_sha256":"1"*64,"abstract":"Primary abstract fact 1 about self-evolving agents and bounded deployment evidence."},
            "arXiv:2608.00002":{"ref":"arXiv:2608.00002","title":"B","source_sha256":"2"*64,"abstract":"Primary abstract fact 2 about self-evolving agents and bounded deployment evidence."},
        }
        prompt=reviewer_prompt([candidate],evidence)
        self.assertIn('"lane":"UNEXPLAINED_BOUNDARY","source_roles":["EMPIRICAL_FACT","EMPIRICAL_FACT"],"distinct_source_minimum":1,"same_primary_source_allowed":true',prompt)
        self.assertIn('"lane":"CONVERGENT_FAILURE","source_roles":["EMPIRICAL_FACT","EMPIRICAL_FACT"],"distinct_source_minimum":2,"same_primary_source_allowed":false',prompt)

    def test_reviewer_prompt_requires_matched_contradiction_treatment_semantics(self) -> None:
        candidate=self.raw_candidate("CONTRADICTION")
        evidence={
            "arXiv:2608.00001":{"ref":"arXiv:2608.00001","title":"A","source_sha256":"1"*64,"abstract":"Primary abstract fact 1 about self-evolving agents and bounded deployment evidence."},
            "arXiv:2608.00002":{"ref":"arXiv:2608.00002","title":"B","source_sha256":"2"*64,"abstract":"Primary abstract fact 2 about self-evolving agents and bounded deployment evidence."},
        }
        prompt=reviewer_prompt([candidate],evidence)
        self.assertIn("shared intervention semantics and adaptation stage",prompt)
        self.assertIn("full-parameter training are different treatment surfaces",prompt)

    def test_reduction_pending_candidate_reaches_lane_reviewer_before_falsifier(self) -> None:
        candidate=self.raw_candidate("CONTRADICTION")
        candidate["mature_theory_baselines"][0]["reduction_class"]="NEEDS_EXACT_REDUCTION_TEST"
        candidate["reduction_falsifiability_contract"]["all_exact_reduction_tests_resolved"]=False
        calls=[]
        base=self.review("CLEAR",lane_verified=False)
        def reviewer(**kwargs):
            calls.append(kwargs.get("prompt",""))
            result=base(**kwargs)
            payload=json.loads(result["text"]);payload["reviews"][0]["lane_contract_reason"]="treatment-surface mismatch: inference-time context is not full-parameter training"
            result["text"]=json.dumps(payload)
            return result
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json";pool=self.pool(root,now)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=self.gen([candidate]),reviewer_responder=reviewer,now=now)
            queue=build_problem_gate_queue(root/"manual.json",auto_inbox_path=auto,primary_pool_path=pool,storage=self.storage(root))
            inbox=json.loads(auto.read_text())
        self.assertEqual(len(calls),1)
        self.assertEqual(state["summary"]["structurally_reviewable"],1)
        review=inbox["candidates"][0]["semantic_reduction_review"]
        self.assertTrue(review["reviewed"]);self.assertFalse(review["lane_contract_verified"]);self.assertEqual(review["verdict"],"BLOCK")
        self.assertIn("treatment-surface mismatch",review["lane_contract_reason"])
        self.assertEqual(queue["summary"]["passed_problem_gate"],0)
        blockers=queue["blocked"][0]["blockers"]
        self.assertIn("unresolved-exact-reduction-test:1",blockers)
        self.assertIn("reduction-falsifiability-contract-incomplete",blockers)
        self.assertIn("semantic-reduction-review-block",blockers)

    def test_reduction_pending_never_passes_problem_gate_even_if_reviewer_clears(self) -> None:
        candidate=self.raw_candidate("CONTRADICTION")
        candidate["mature_theory_baselines"][0]["reduction_class"]="NEEDS_EXACT_REDUCTION_TEST"
        candidate["reduction_falsifiability_contract"]["all_exact_reduction_tests_resolved"]=False
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json";pool=self.pool(root,now)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=self.gen([candidate]),reviewer_responder=self.review("CLEAR",lane_verified=True),now=now)
            queue=build_problem_gate_queue(root/"manual.json",auto_inbox_path=auto,primary_pool_path=pool,storage=self.storage(root))
        self.assertEqual(state["summary"]["structurally_reviewable"],1)
        self.assertEqual(queue["summary"]["passed_problem_gate"],0)
        self.assertTrue(any(x.startswith("unresolved-exact-reduction-test:") for x in queue["blocked"][0]["blockers"]))

    def test_reviewer_prompt_blocks_cross_treatment_contradictions(self) -> None:
        candidate=valid_candidate("CONTRADICTION")
        evidence={
            "arXiv:2608.00001":{"ref":"arXiv:2608.00001","title":"Primary A","source_sha256":"a"*64,"abstract":"Observed A under frozen setting."},
            "arXiv:2608.00002":{"ref":"arXiv:2608.00002","title":"Primary B","source_sha256":"b"*64,"abstract":"Observed independent outcome B under the relevant setting."},
        }
        prompt=reviewer_prompt([candidate],evidence)
        self.assertIn("same causal treatment surface",prompt)
        self.assertIn("inference-time conditioning versus parameter-updated/SFT training",prompt)
        self.assertIn("cross-treatment contrast",prompt)

    def test_explicit_portfolio_mode_is_not_a_live_generator_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc)
            with self.assertRaises(ValueError):
                run_problem_generator(storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",portfolio_mode=True,now=now)

    def test_unexplained_boundary_lane_search_accepts_one_primary_ref_but_other_lanes_do_not(self) -> None:
        registry={f"arXiv:2608.0000{i}":{} for i in range(1,5)}
        rows=[]
        for lane in DISCOVERY_LANES:
            if lane=="UNEXPLAINED_BOUNDARY":
                rows.append({"lane":lane,"status":"REDUCIBLE","source_refs":["arXiv:2608.00001"],"reason":"One primary paper contains both the anomalous regime and its adjacent control regime."})
            else:
                rows.append({"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No evidence tuple survives."})
        normalized=_normalize_lane_search(rows,registry,list(DISCOVERY_LANES))
        boundary=next(row for row in normalized if row["lane"]=="UNEXPLAINED_BOUNDARY")
        self.assertEqual(boundary["source_refs"],["arXiv:2608.00001"])
        bad=[dict(row) for row in rows]
        bad[0]={"lane":"CONTRADICTION","status":"REDUCIBLE","source_refs":["arXiv:2608.00001"],"reason":"One ref is insufficient for contradiction."}
        with self.assertRaisesRegex(ValueError,"evidence-tuple-invalid"):
            _normalize_lane_search(bad,registry,list(DISCOVERY_LANES))

    def test_complete_lane_audit_is_canonicalized_to_dynamic_priority(self) -> None:
        registry={f"arXiv:2608.0000{i}":{} for i in range(1,5)}
        expected=["CONTRADICTION","CONVERGENT_FAILURE","UNEXPLAINED_BOUNDARY","ASSUMPTION_BREAK"]
        returned=["CONTRADICTION","CONVERGENT_FAILURE","ASSUMPTION_BREAK","UNEXPLAINED_BOUNDARY"]
        rows=[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No evidence tuple survives."} for lane in returned]
        normalized=_normalize_lane_search(rows,registry,expected)
        self.assertEqual([row["lane"] for row in normalized],expected)

    def test_lane_audit_priority_must_itself_cover_exact_live_lanes(self) -> None:
        registry={f"arXiv:2608.0000{i}":{} for i in range(1,5)}
        rows=[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No evidence tuple survives."} for lane in DISCOVERY_LANES]
        with self.assertRaisesRegex(ValueError,"priority-invalid"):
            _normalize_lane_search(rows,registry,["CONTRADICTION","CONVERGENT_FAILURE","ASSUMPTION_BREAK","ASSUMPTION_BREAK"])

    def test_saturated_pool_without_current_operator_receipt_recompiles_once(self) -> None:
        calls=[]
        generator=self.gen([],notes="Anomaly-first recompilation found no surviving residual.")
        def counted(**kwargs):
            calls.append(1); return generator(**kwargs)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);storage=self.storage(root);pool=self.pool(root,now)
            payload=json.loads(pool.read_text());payload["source_coverage"]={"coverage_exhausted":True,"source_retrieval_complete":True,"eligible_lane_linked_sources":4,"reviewed_lane_linked_sources":4,"unreviewed_lane_linked_sources":0,"unreviewed_no_lane_sources":0,"carrier_probe_required":False,"carrier_probe_pending":0,"carrier_probe_complete":True,"scientific_authority":False};pool.write_text(json.dumps(payload),encoding="utf-8")
            first=run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto1.json",generator_responder=counted,now=now)
            second=run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto2.json",generator_responder=counted,now=now+timedelta(minutes=1))
            ledger=json.loads((root/"paper-first-problem-discovery"/"discovery-saturation-ledger.json").read_text())
        self.assertEqual(first["status"],"GENERATED_ZERO_CANDIDATES")
        self.assertIn("operator_recompile_reason",first)
        self.assertEqual(second["status"],"SKIPPED_SOURCE_COVERAGE_SATURATED")
        self.assertEqual(calls,[1])
        self.assertEqual(ledger["runs"][-1]["discovery_operator_version"],DISCOVERY_OPERATOR_VERSION)
        self.assertTrue(second["policy"]["source_coverage_saturation_reopens_once_on_operator_change"])

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
        self.assertFalse(state["policy"]["search_portfolio_enabled"])
        self.assertTrue(state["policy"]["search_portfolio_is_shadow_only"])
        self.assertTrue(state["policy"]["canonical_transaction_forbids_search_portfolio"])
        self.assertTrue(state["policy"]["one_content_addressed_pool_allows_at_most_one_live_generator_call"])
        self.assertTrue(state["policy"]["one_generator_call_max"])
        self.assertTrue(state["policy"]["one_semantic_reviewer_call_max"])

    def test_deferred_reviewer_never_calls_reviewer_and_keeps_candidate_unreviewed(self) -> None:
        reviewer_calls=[]
        def reviewer(**kwargs):
            reviewer_calls.append(1)
            raise AssertionError("reviewer must be deferred")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json"
            state=run_problem_generator(
                storage=self.storage(root),primary_pool_path=self.pool(root,now),auto_inbox_path=auto,
                generator_responder=self.gen([self.raw_candidate()],notes="One structurally reviewable candidate survives."),
                reviewer_responder=reviewer,now=now,defer_reviewer=True,strict_provider=True,
            )
            inbox=json.loads(auto.read_text())
        self.assertEqual(reviewer_calls,[])
        self.assertEqual(state["status"],"GENERATED_AWAIT_SEMANTIC_REVIEW")
        self.assertEqual(state["summary"]["structurally_reviewable"],1)
        self.assertEqual(state["summary"]["semantic_review_unavailable"],1)
        self.assertEqual(state["summary"]["written_to_auto_inbox"],0)
        self.assertEqual(state["candidates"][0]["semantic_verdict"],"UNREVIEWED")
        self.assertEqual(inbox["candidates"],[])
        self.assertTrue(state["policy"]["strict_provider_transport"])
        self.assertTrue(state["policy"]["semantic_reviewer_deferred"])
        self.assertFalse(state["policy"]["thinking_compatibility_repost_allowed"])
        self.assertTrue(state["policy"]["thinking_disabled"])
        self.assertEqual(state["policy"]["generator_thinking_profile"],"disabled")
        self.assertEqual(state["policy"]["generator_max_output_tokens"],6500)
        self.assertFalse(state["policy"]["transport_only_no_output_fallback_allowed"])
        self.assertEqual(state["policy"]["transport_fallback_max_additional_provider_attempts"],0)

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

    def test_no_output_provider_failure_allows_one_transport_fallback(self) -> None:
        from .ark_provider import ArkResponseStateError,ArkSettings
        settings=ArkSettings(api_key="test-key",base_url="https://example.invalid",default_model="glm-5.3",timeout_seconds=120,max_retries=0)
        incomplete=ArkResponseStateError(
            "Ark response incomplete before assistant output; response_id=resp_glm; reason=length; requested_model=glm-5.3",
            {"id":"resp_glm","status":"incomplete","model":"glm-5.3-260817","incomplete_details":{"reason":"length"}},
            "glm-5.3",
        )
        with patch("research_pipeline.paper_first_problem_generator.ArkSettings.from_env",return_value=settings), patch(
            "research_pipeline.paper_first_problem_generator.ArkResponsesClient.respond",
            side_effect=[
                incomplete,
                {"text":"OK","resolved_model":"kimi-k3"},
            ],
        ) as respond:
            result=_ark(prompt="test",model="glm-5.3",max_output_tokens=64,temperature=0.0,stage="problem_generation")
        self.assertEqual(respond.call_count,2)
        self.assertTrue(all(call.kwargs.get("store") is True for call in respond.call_args_list))
        self.assertIsNone(respond.call_args_list[0].kwargs.get("thinking"))
        self.assertEqual(respond.call_args_list[1].kwargs.get("thinking"),"disabled")
        self.assertTrue(result["transport_fallback_used"])
        self.assertEqual([row["requested_model"] for row in result["transport_attempts"]],["glm-5.3","kimi-k3"])
        self.assertEqual([row["assistant_output_present"] for row in result["transport_attempts"]],[False,True])
        self.assertEqual(result["transport_attempts"][0]["provider_receipt"]["response_id"],"resp_glm")
        self.assertEqual(result["transport_attempts"][0]["provider_receipt"]["status"],"incomplete")
        self.assertEqual(result["resolved_model"],"kimi-k3")

    def test_strict_provider_disables_transport_fallback_after_incomplete(self) -> None:
        from .ark_provider import ArkResponseStateError,ArkSettings
        settings=ArkSettings(api_key="test-key",base_url="https://example.invalid",default_model="glm-5.3",timeout_seconds=120,max_retries=0)
        incomplete=ArkResponseStateError(
            "Ark response incomplete before assistant output; response_id=resp_glm_strict; reason=length; requested_model=glm-5.3",
            {"id":"resp_glm_strict","status":"incomplete","model":"glm-5.3-260817","incomplete_details":{"reason":"length"}},
            "glm-5.3",
        )
        with patch("research_pipeline.paper_first_problem_generator.ArkSettings.from_env",return_value=settings), patch(
            "research_pipeline.paper_first_problem_generator.ArkResponsesClient.respond",
            side_effect=incomplete,
        ) as respond:
            with self.assertRaisesRegex(RuntimeError,"failed before an auditable assistant output") as caught:
                _ark(prompt="test",model="glm-5.3",max_output_tokens=64,temperature=0.0,stage="problem_generation",allow_transport_fallback=False)
        self.assertEqual(respond.call_count,1)
        self.assertIsNone(respond.call_args.kwargs.get("thinking"))
        self.assertFalse(respond.call_args.kwargs.get("allow_thinking_compatibility_fallback"))
        self.assertEqual(len(caught.exception.transport_attempts),1)
        self.assertEqual(caught.exception.transport_attempts[0]["provider_receipt"]["response_id"],"resp_glm_strict")

    def test_no_receipt_timeout_is_archived_and_blocks_automatic_replay(self) -> None:
        calls=[]
        def timeout_responder(**kwargs):
            calls.append(1)
            audit=_provider_request_audit(stage="problem_generation",prompt=kwargs["prompt"],model=kwargs["model"],max_output_tokens=kwargs["max_output_tokens"],temperature=0.0)
            error=RuntimeError("provider connection timed out after POST")
            error.transport_attempts=[{**audit,"requested_model":kwargs["model"],"status":"error-no-output","error_kind":"transport-timeout-or-connection","assistant_output_present":False,"provider_error_audit":{"exception_type":"Timeout","http_status":None,"detail_sha256":"d"*64,"scientific_authority":False}}]
            raise error
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,17,tzinfo=timezone.utc);storage=self.storage(root);pool=self.pool(root,now)
            first=run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto1.json",generator_model="glm-5.3",generator_responder=timeout_responder,now=now,strict_provider=True,defer_reviewer=True)
            orphan_files=list((root/"paper-first-problem-discovery"/"provider-orphans").glob("*.json"))
            with patch("research_pipeline.paper_first_problem_generator._ark",side_effect=AssertionError("automatic replay must be blocked")) as ark:
                second=run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto2.json",generator_model="glm-5.3",now=now+timedelta(minutes=1),strict_provider=True,defer_reviewer=True)
            orphan=json.loads(orphan_files[0].read_text())
        self.assertEqual(calls,[1])
        self.assertEqual(first["status"],"GENERATOR_ERROR_ZERO_AUTHORITY")
        self.assertEqual(len(orphan_files),1)
        self.assertEqual(orphan["status"],"ORPHANED_POST_NO_RECEIPT")
        self.assertEqual(orphan["replay_policy"],"BLOCK_AUTOMATIC_REPLAY_UNTIL_EXPLICIT_OPERATOR_OVERRIDE")
        self.assertFalse(orphan["scientific_authority"])
        self.assertEqual(second["status"],"SKIPPED_ORPHANED_PROVIDER_REQUEST")
        self.assertEqual(ark.call_count,0)
        self.assertIn("provider acceptance is ambiguous",second["coverage_skip_reason"])
        self.assertTrue(second["policy"]["provider_orphan_replay_forbidden"])

    def test_pending_provider_receipt_does_not_fallback_or_repost(self) -> None:
        from .ark_provider import ArkResponseStateError,ArkSettings
        settings=ArkSettings(api_key="test-key",base_url="https://example.invalid",default_model="glm-5.3",timeout_seconds=120,max_retries=0)
        pending=ArkResponseStateError(
            "Ark response contained neither assistant output_text nor function_call; response_id=resp_pending; status=in_progress; requested_model=glm-5.3; resolved_model=glm-5.3-260817",
            {"id":"resp_pending","status":"in_progress","model":"glm-5.3-260817","output":[]},
            "glm-5.3",
        )
        with patch("research_pipeline.paper_first_problem_generator.ArkSettings.from_env",return_value=settings), patch(
            "research_pipeline.paper_first_problem_generator.ArkResponsesClient.respond",
            side_effect=pending,
        ) as respond:
            with self.assertRaisesRegex(RuntimeError,"re-POST forbidden") as caught:
                _ark(prompt="test",model="glm-5.3",max_output_tokens=64,temperature=0.0,stage="problem_generation")
        self.assertEqual(respond.call_count,1)
        self.assertTrue(respond.call_args.kwargs.get("store") is True)
        self.assertEqual(caught.exception.provider_receipt["response_id"],"resp_pending")
        self.assertEqual(caught.exception.provider_receipt["status"],"in_progress")
        self.assertEqual(len(caught.exception.transport_attempts),1)

    def test_nontransport_provider_error_does_not_fallback(self) -> None:
        from .ark_provider import ArkSettings
        settings=ArkSettings(api_key="test-key",base_url="https://example.invalid",default_model="glm-5.3",timeout_seconds=120,max_retries=0)
        with patch("research_pipeline.paper_first_problem_generator.ArkSettings.from_env",return_value=settings), patch(
            "research_pipeline.paper_first_problem_generator.ArkResponsesClient.respond",
            side_effect=RuntimeError("schema-invalid-after-output"),
        ) as respond:
            with self.assertRaisesRegex(RuntimeError,"Ark provider failed before an auditable assistant output"):
                _ark(prompt="test",model="glm-5.3",max_output_tokens=64,temperature=0.0,stage="problem_generation")
        self.assertEqual(respond.call_count,1)

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

    def test_provider_response_id_is_private_and_public_state_keeps_only_audit_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,17,tzinfo=timezone.utc);storage=self.storage(root);json_path=root/"public.json";js_path=root/"public.js";base=self.gen([],resolved="kimi-k3",notes="All four lanes were audited; none survives.")
            def responder(**kwargs):
                result=base(**kwargs);result["transport_fallback_used"]=True;result["transport_attempts"]=[
                    {"requested_model":"glm-5.3","status":"error-no-output","error_kind":"provider-incomplete-before-output","assistant_output_present":False,"provider_receipt":{"response_id":"resp_secret_glm","status":"incomplete","requested_model":"glm-5.3","resolved_model":"glm-5.3-260817","incomplete_reason":"length"}},
                    {"requested_model":"kimi-k3","status":"success","resolved_model":"kimi-k3","assistant_output_present":True},
                ];return result
            internal=write_problem_generator_state(json_path=json_path,js_path=js_path,storage=storage,primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=responder,now=now)
            public_text=json_path.read_text();private_files=list((root/"paper-first-problem-discovery"/"provider-receipts").glob("*.json"));private_payload=json.loads(private_files[0].read_text())
        self.assertEqual(len(private_files),1)
        self.assertEqual(private_payload["provider_receipt"]["response_id"],"resp_secret_glm")
        self.assertNotIn("resp_secret_glm",public_text)
        self.assertNotIn("provider_receipt",internal["raw_artifacts"]["generator"]["transport_attempts"][0])
        audit=internal["raw_artifacts"]["generator"]["transport_attempts"][0]["provider_receipt_audit"]
        self.assertEqual(audit["status"],"incomplete")
        self.assertEqual(len(audit["provider_receipt_sha256"]),64)

    def test_pending_provider_response_id_is_archived_before_generator_error_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,17,tzinfo=timezone.utc);storage=self.storage(root);json_path=root/"public.json";js_path=root/"public.js"
            def pending(**kwargs):
                error=RuntimeError("Ark provider response is pending; re-POST forbidden; requested_model=glm-5.3; status=in_progress")
                receipt={"response_id":"resp_pending_secret","status":"in_progress","requested_model":"glm-5.3","resolved_model":"glm-5.3-260817","incomplete_reason":""}
                error.provider_receipt=receipt;error.transport_attempts=[{"requested_model":"glm-5.3","status":"error-no-output","error_kind":"provider-empty-output","assistant_output_present":False,"provider_receipt":receipt}]
                raise error
            state=write_problem_generator_state(json_path=json_path,js_path=js_path,storage=storage,primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=pending,now=now)
            public_text=json_path.read_text();private_files=list((root/"paper-first-problem-discovery"/"provider-receipts").glob("*.json"));private_payload=json.loads(private_files[0].read_text())
        self.assertEqual(state["status"],"GENERATOR_ERROR_ZERO_AUTHORITY")
        self.assertEqual(len(private_files),1)
        self.assertEqual(private_payload["provider_receipt"]["response_id"],"resp_pending_secret")
        self.assertNotIn("resp_pending_secret",public_text)
        self.assertEqual(state["provider_receipt_audits"][0]["status"],"in_progress")
        self.assertEqual(state["provider_transport_attempts"][0]["provider_receipt_audit"]["status"],"in_progress")

    def test_pending_reviewer_receipt_is_not_converted_into_scientific_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,17,tzinfo=timezone.utc);storage=self.storage(root);json_path=root/"public.json";js_path=root/"public.js";auto=root/"auto.json"
            def pending_reviewer(**kwargs):
                error=RuntimeError("Ark provider response is pending; re-POST forbidden; requested_model=deepseek-v4-pro; status=in_progress")
                receipt={"response_id":"resp_reviewer_secret","status":"in_progress","requested_model":"deepseek-v4-pro","resolved_model":"deepseek-v4-pro-260817","incomplete_reason":""}
                error.provider_receipt=receipt;error.transport_attempts=[{"requested_model":"deepseek-v4-pro","status":"error-no-output","error_kind":"provider-empty-output","assistant_output_present":False,"provider_receipt":receipt}]
                raise error
            state=write_problem_generator_state(json_path=json_path,js_path=js_path,storage=storage,primary_pool_path=self.pool(root,now),auto_inbox_path=auto,generator_responder=self.gen([self.raw_candidate()]),reviewer_responder=pending_reviewer,now=now)
            public_text=json_path.read_text();public=json.loads(public_text);inbox=json.loads(auto.read_text());private_files=list((root/"paper-first-problem-discovery"/"provider-receipts").glob("*.json"))
        self.assertEqual(state["status"],"REVIEWER_ERROR_ZERO_AUTHORITY")
        self.assertEqual(state["summary"]["semantic_review_unavailable"],1)
        self.assertEqual(state["summary"]["semantic_blocked"],0)
        self.assertEqual(state["summary"]["written_to_auto_inbox"],0)
        self.assertEqual(inbox["candidates"],[])
        self.assertEqual(public["candidates"][0]["semantic_verdict"],"UNREVIEWED")
        self.assertNotIn("resp_reviewer_secret",public_text)
        self.assertEqual(len(private_files),1)

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
            run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=root/"seed-auto.json",generator_responder=self.gen([],notes="Seed current anomaly-first operator receipt."),now=now)
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

    def test_incomplete_retrieval_without_new_lane_source_makes_zero_model_calls(self) -> None:
        calls=[]
        def responder(**kwargs):
            calls.append(1);raise AssertionError("incomplete retrieval without source delta must not call a model")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,14,tzinfo=timezone.utc);pool=self.pool(root,now);payload=json.loads(pool.read_text())
            payload["source_coverage"]={"coverage_exhausted":False,"source_retrieval_complete":False,"eligible_lane_linked_sources":4,"reviewed_lane_linked_sources":4,"unreviewed_lane_linked_sources":0,"unreviewed_no_lane_sources":2,"carrier_probe_required":False,"carrier_probe_pending":0,"carrier_probe_complete":True,"scientific_authority":False}
            pool.write_text(json.dumps(payload),encoding="utf-8")
            auto=root/"auto.json";state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=responder,reviewer_responder=responder,now=now);inbox=json.loads(auto.read_text())
            ledger=root/"paper-first-problem-discovery"/"discovery-saturation-ledger.json"
        self.assertEqual(state["status"],"SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE")
        self.assertEqual(calls,[])
        self.assertEqual(inbox["candidates"],[])
        self.assertFalse(state["source_coverage"]["source_retrieval_complete"])
        self.assertFalse(state["source_coverage"]["coverage_exhausted"])
        self.assertTrue(state["policy"]["incomplete_retrieval_without_new_lane_source_skips_model_call"])
        self.assertTrue(state["policy"]["retrieval_incomplete_is_compute_control_not_scientific_negative"])
        self.assertFalse(state["saturation_memory"]["current_run_recorded"])
        self.assertFalse(ledger.exists())

    def test_carrier_probe_pending_makes_zero_model_calls_without_saturation_receipt(self) -> None:
        calls=[]
        def responder(**kwargs):
            calls.append(1);raise AssertionError("carrier-probe backlog must not call a model")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);pool=self.pool(root,now);payload=json.loads(pool.read_text())
            payload["source_coverage"]={"coverage_exhausted":False,"eligible_lane_linked_sources":4,"reviewed_lane_linked_sources":4,"unreviewed_lane_linked_sources":0,"unreviewed_no_lane_sources":2,"carrier_probe_required":True,"carrier_probe_pending":2,"carrier_probe_complete":False,"scientific_authority":False}
            pool.write_text(json.dumps(payload),encoding="utf-8")
            auto=root/"auto.json";state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=responder,reviewer_responder=responder,now=now);inbox=json.loads(auto.read_text())
            ledger=root/"paper-first-problem-discovery"/"discovery-saturation-ledger.json"
        self.assertEqual(state["status"],"SKIPPED_SOURCE_CARRIER_PROBE_PENDING")
        self.assertEqual(calls,[])
        self.assertEqual(inbox["candidates"],[])
        self.assertEqual(state["source_coverage"]["carrier_probe_pending"],2)
        self.assertFalse(state["source_coverage"]["carrier_probe_complete"])
        self.assertTrue(state["policy"]["carrier_probe_pending_skips_model_call"])
        self.assertTrue(state["policy"]["carrier_probe_pending_is_compute_control_not_scientific_negative"])
        self.assertFalse(state["saturation_memory"]["current_run_recorded"])
        self.assertFalse(ledger.exists())

    def test_lane_grounded_source_coverage_saturation_makes_zero_model_calls(self) -> None:
        calls=[]
        def responder(**kwargs):
            calls.append(1); raise AssertionError("coverage-saturated primary pool must not call a model")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);storage=self.storage(root);pool=self.pool(root,now)
            run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=root/"seed-auto.json",generator_responder=self.gen([],notes="Seed current anomaly-first operator receipt."),now=now)
            payload=json.loads(pool.read_text());payload["source_coverage"]={"coverage_exhausted":True,"eligible_lane_linked_sources":4,"reviewed_lane_linked_sources":4,"unreviewed_lane_linked_sources":0,"unreviewed_no_lane_sources":1,"scientific_authority":False};pool.write_text(json.dumps(payload),encoding="utf-8")
            auto=root/"auto.json";state=run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=auto,generator_responder=responder,reviewer_responder=responder,now=now);inbox=json.loads(auto.read_text())
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

    def test_legacy_pair_audit_receipt_keeps_legacy_provenance_after_operator_upgrade(self) -> None:
        priority=list(DISCOVERY_LANES)
        legacy={"run_id":"legacy-run","generator_status":"GENERATED_ZERO_CANDIDATES","generated_at":"2026-08-14T11:43:57+00:00","mode":"legacy_pair_audit","lane_search_priority":priority,"lane_search":[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"Historical pair audit found no pair."} for lane in priority],"generation_notes":"Historical receipt.","scientific_authority":False}
        from .paper_first_problem_generator import _normalize_last_completed_lane_search_receipt
        normalized=_normalize_last_completed_lane_search_receipt(legacy)
        self.assertEqual(normalized["mode"],"legacy_pair_audit")
        self.assertEqual(normalized["discovery_operator_version"],"")

    def test_completed_lane_search_becomes_portable_zero_authority_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);storage=self.storage(root);j=root/"generator.json";js=root/"generator.js"
            state=write_problem_generator_state(json_path=j,js_path=js,storage=storage,primary_pool_path=self.pool(root,now),auto_inbox_path=root/"auto.json",generator_responder=self.gen([],notes="All four lanes were audited; none survives."),now=now)
            public=json.loads(j.read_text())
        receipt=public["search_diagnostics"]["last_completed_lane_search"]
        self.assertEqual(receipt["run_id"],state["run_id"]);self.assertEqual(receipt["generator_status"],"GENERATED_ZERO_CANDIDATES")
        self.assertEqual([row["lane"] for row in receipt["lane_search"]],receipt["lane_search_priority"])
        self.assertEqual(len(receipt["lane_search"]),len(DISCOVERY_LANES));self.assertFalse(receipt["scientific_authority"])
        self.assertTrue(public["policy"]["last_completed_lane_search_is_portable_zero_authority_receipt"])

    def test_saturated_zero_call_preserves_previous_completed_lane_search(self) -> None:
        calls=[]
        def forbidden(**kwargs):calls.append(1);raise AssertionError("saturated follow-up must not call a model")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);storage=self.storage(root);j=root/"generator.json";js=root/"generator.js";pool=self.pool(root,now)
            first=write_problem_generator_state(json_path=j,js_path=js,storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto1.json",generator_responder=self.gen([],notes="Initial complete lane audit."),now=now)
            payload=json.loads(pool.read_text());payload["source_coverage"]={"coverage_exhausted":True,"eligible_lane_linked_sources":4,"reviewed_lane_linked_sources":4,"unreviewed_lane_linked_sources":0,"unreviewed_no_lane_sources":0,"scientific_authority":False};pool.write_text(json.dumps(payload),encoding="utf-8")
            second=write_problem_generator_state(json_path=j,js_path=js,storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto2.json",generator_responder=forbidden,reviewer_responder=forbidden,now=now+timedelta(minutes=1))
            public=json.loads(j.read_text())
        self.assertEqual(calls,[]);self.assertEqual(second["status"],"SKIPPED_SOURCE_COVERAGE_SATURATED");self.assertFalse(public["search_diagnostics"]["lane_search_complete"])
        receipt=public["search_diagnostics"]["last_completed_lane_search"]
        self.assertEqual(receipt["run_id"],first["run_id"]);self.assertEqual(len(receipt["lane_search"]),len(DISCOVERY_LANES));self.assertFalse(receipt["scientific_authority"])

    def test_saturated_migration_seed_backfills_last_completed_lane_search(self) -> None:
        priority=list(DISCOVERY_LANES)
        seed={"run_id":"historic-real-call","generator_status":"GENERATED_ZERO_CANDIDATES","generated_at":"2026-08-13T14:12:22+00:00","lane_search_priority":priority,"lane_search":[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No pair survived this historical lane audit."} for lane in priority],"generation_notes":"Historic completed lane audit.","scientific_authority":False}
        calls=[]
        def forbidden(**kwargs):calls.append(1);raise AssertionError
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);storage=self.storage(root);pool=self.pool(root,now)
            run_problem_generator(storage=storage,primary_pool_path=pool,auto_inbox_path=root/"seed-auto.json",generator_responder=self.gen([],notes="Seed current anomaly-first operator receipt."),now=now)
            payload=json.loads(pool.read_text());payload["source_coverage"]={"coverage_exhausted":True,"eligible_lane_linked_sources":4,"reviewed_lane_linked_sources":4,"unreviewed_lane_linked_sources":0,"unreviewed_no_lane_sources":0,"scientific_authority":False};pool.write_text(json.dumps(payload),encoding="utf-8")
            j=root/"generator.json";js=root/"generator.js";write_problem_generator_state(json_path=j,js_path=js,storage=storage,primary_pool_path=pool,auto_inbox_path=root/"auto.json",generator_responder=forbidden,reviewer_responder=forbidden,last_completed_lane_search_seed=seed,now=now)
            public=json.loads(j.read_text())
        self.assertEqual(calls,[]);self.assertFalse(public["search_diagnostics"]["lane_search_complete"]);self.assertEqual(public["search_diagnostics"]["last_completed_lane_search"]["run_id"],"historic-real-call")
        self.assertFalse(public["search_diagnostics"]["last_completed_lane_search"]["scientific_authority"])

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

    def test_pending_exact_reduction_reaches_reviewer_but_clear_cannot_close_falsifier(self) -> None:
        candidate=self.raw_candidate("ASSUMPTION_BREAK")
        candidate["mature_theory_baselines"][1]["reduction_class"]="NEEDS_EXACT_REDUCTION_TEST"
        candidate["reduction_falsifiability_contract"]["all_exact_reduction_tests_resolved"]=False
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);auto=root/"auto.json";pool=self.pool(root,now)
            state=run_problem_generator(storage=self.storage(root),primary_pool_path=pool,auto_inbox_path=auto,generator_responder=self.gen([candidate]),reviewer_responder=self.review("CLEAR",lane="ASSUMPTION_BREAK"),now=now)
            inbox=json.loads(auto.read_text());queue=build_problem_gate_queue(root/"manual.json",auto_inbox_path=auto,primary_pool_path=pool,storage=self.storage(root))
        self.assertEqual(state["summary"]["structurally_reviewable"],1)
        self.assertEqual(state["summary"]["semantic_clear"],1)
        self.assertFalse(inbox["candidates"][0]["reduction_falsifiability_contract"]["all_exact_reduction_tests_resolved"])
        self.assertEqual(queue["summary"]["passed_problem_gate"],0)
        self.assertIn("unresolved-exact-reduction-test:2",queue["blocked"][0]["blockers"])

    def test_reviewer_only_resume_never_reruns_generator_and_preserves_pending_falsifier(self) -> None:
        candidate=self.raw_candidate("ASSUMPTION_BREAK")
        candidate["mature_theory_baselines"][1]["reduction_class"]="NEEDS_EXACT_REDUCTION_TEST"
        candidate["reduction_falsifiability_contract"]["all_exact_reduction_tests_resolved"]=False
        generator=self.gen([candidate],resolved="kimi-k3",notes="One reviewable candidate survives.")
        reviewer_calls=[];reviewer=self.review("CLEAR",resolved="deepseek-v4-pro",lane="ASSUMPTION_BREAK")
        def counted_reviewer(**kwargs): reviewer_calls.append(1); return reviewer(**kwargs)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);storage=self.storage(root);pool=self.pool(root,now);raw_path=root/"generator.txt";raw=generator(prompt="unused",model="kimi-k3",max_output_tokens=10)["text"];raw_path.write_text(raw,encoding="utf-8");raw_sha=hashlib.sha256(raw.encode()).hexdigest();auto=root/"review-auto.json"
            state=resume_semantic_reviewer(storage=storage,primary_pool_path=pool,generator_raw_path=raw_path,generator_raw_sha256=raw_sha,generator_requested_model="kimi-k3",generator_resolved_model="kimi-k3",source_generator_run_id="GEN-1",reviewer_model="deepseek-v4-pro",auto_inbox_path=auto,reviewer_responder=counted_reviewer,expected_pool_sha256="",now=now)
            queue=build_problem_gate_queue(root/"manual.json",auto_inbox_path=auto,primary_pool_path=pool,storage=storage)
            review_inbox=json.loads(auto.read_text())
        self.assertEqual(reviewer_calls,[1])
        self.assertTrue(state["policy"]["reviewer_only_resume"])
        self.assertEqual(state["policy"]["generator_calls_authorized"],0)
        self.assertEqual(state["status"],"GENERATED_AWAIT_PROBLEM_GATE")
        self.assertEqual(state["summary"]["semantic_clear"],1)
        self.assertFalse(review_inbox["candidates"][0]["reduction_falsifiability_contract"]["all_exact_reduction_tests_resolved"])
        self.assertEqual(queue["summary"]["passed_problem_gate"],0)
        self.assertIn("unresolved-exact-reduction-test:2",queue["blocked"][0]["blockers"])

    def test_reviewer_only_resume_reverifies_prior_grounding_without_reusing_prior_verdict(self) -> None:
        candidate=self.raw_candidate("CONTRADICTION");generator=self.gen([candidate],resolved="kimi-k3",notes="One reviewable candidate survives.")
        old_reviewer=self.review("BLOCK",resolved="old-reviewer",use_fulltext=True);new_reviewer=self.review("CLEAR",resolved="deepseek-v4-pro",use_fulltext=True)
        calls=[]
        def counted_reviewer(**kwargs):calls.append(1);return new_reviewer(**kwargs)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);storage=self.storage(root);pool=self.pool(root,now)
            generator_raw=generator(prompt="unused",model="kimi-k3",max_output_tokens=10)["text"];generator_path=root/"generator.txt";generator_path.write_text(generator_raw);generator_sha=hashlib.sha256(generator_raw.encode()).hexdigest()
            prior_raw=old_reviewer(prompt="unused",model="old-reviewer",max_output_tokens=10)["text"];prior_path=root/"prior-reviewer.txt";prior_path.write_text(prior_raw);prior_sha=hashlib.sha256(prior_raw.encode()).hexdigest()
            state=resume_semantic_reviewer(storage=storage,primary_pool_path=pool,generator_raw_path=generator_path,generator_raw_sha256=generator_sha,generator_requested_model="kimi-k3",generator_resolved_model="kimi-k3",source_generator_run_id="GEN-1",reviewer_model="deepseek-v4-pro",auto_inbox_path=root/"auto.json",reviewer_responder=counted_reviewer,prior_reviewer_raw_path=prior_path,prior_reviewer_raw_sha256=prior_sha,now=now)
        self.assertEqual(calls,[1])
        self.assertEqual(state["status"],"GENERATED_AWAIT_PROBLEM_GATE")
        self.assertEqual(state["summary"]["semantic_clear"],1)
        self.assertEqual(state["prior_reviewer_grounding_audit"]["candidate_exact_evidence_grounding_verified"],1)
        self.assertFalse(state["prior_reviewer_grounding_audit"]["prior_verdict_reused"])
        self.assertTrue(state["policy"]["prior_reviewer_verdict_reuse_forbidden"])

    def test_reviewer_only_resume_bad_generator_sha_makes_zero_reviewer_calls(self) -> None:
        reviewer_calls=[]
        def reviewer(**kwargs): reviewer_calls.append(1); raise AssertionError
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);storage=self.storage(root);pool=self.pool(root,now);raw=root/"generator.txt";raw.write_text(self.gen([],notes="zero")(prompt="x",model="kimi-k3",max_output_tokens=10)["text"],encoding="utf-8")
            state=resume_semantic_reviewer(storage=storage,primary_pool_path=pool,generator_raw_path=raw,generator_raw_sha256="0"*64,generator_requested_model="kimi-k3",generator_resolved_model="kimi-k3",source_generator_run_id="GEN-1",reviewer_responder=reviewer,now=now)
        self.assertEqual(reviewer_calls,[])
        self.assertEqual(state["status"],"REVIEWER_RESUME_INPUT_INVALID")
        self.assertEqual(state["error"],"generator-raw-sha-mismatch")

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
        self.assertEqual(review["source_claim_grounding"]["source_a"]["evidence_sha256"], "6"*64)
        self.assertTrue(review["source_claim_grounding"]["source_a"]["evidence_sha256_verified"])
        self.assertEqual(review["source_claim_grounding"]["source_b"]["evidence_sha256"], "7"*64)
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

    def test_generator_raw_replay_is_zero_provider_and_recompiles_lane_search_against_current_pool(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);pool=self.pool(root,now);raw_path=root/"generator-raw.json"
            payload={"lane_search":[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No current pair survives this lane search."} for lane in DISCOVERY_LANES],"candidates":[],"generation_notes":"Archived generator found no surviving candidate."}
            raw=json.dumps(payload);raw_path.write_text(raw);sha=hashlib.sha256(raw.encode()).hexdigest();auto=root/"auto.json"
            state=replay_problem_generator_raw(storage=self.storage(root),primary_pool_path=pool,generator_raw_path=raw_path,generator_raw_sha256=sha,generator_requested_model="kimi-k3",generator_resolved_model="kimi-k3",source_generator_run_id="old-run",source_discovery_operator_version="old-op",auto_inbox_path=auto,now=now)
            inbox=json.loads(auto.read_text())
        self.assertEqual(state["status"],"GENERATED_ZERO_CANDIDATES")
        self.assertEqual(state["provider_calls_executed"],0);self.assertEqual(state["semantic_reviewer_calls_executed"],0)
        self.assertTrue(state["policy"]["generator_replayed_without_provider"]);self.assertEqual(state["policy"]["automatic_provider_calls_authorized"],0)
        self.assertTrue(state["search_diagnostics"]["lane_search_complete"]);self.assertEqual(len(state["search_diagnostics"]["lane_search"]),len(DISCOVERY_LANES))
        self.assertTrue(state["raw_artifacts"]["generator"]["raw_replayed_without_provider"]);self.assertEqual(state["raw_artifacts"]["generator"]["sha256"],sha)
        self.assertEqual(inbox["candidates"],[])

    def test_generator_raw_replay_fails_closed_if_current_contract_still_requires_semantic_review(self) -> None:
        candidate=self.raw_candidate("CONTRADICTION")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);now=datetime(2026,8,13,tzinfo=timezone.utc);pool=self.pool(root,now);raw_path=root/"generator-raw.json"
            lane_search=[]
            for lane in DISCOVERY_LANES:
                if lane=="CONTRADICTION": lane_search.append({"lane":lane,"status":"CANDIDATE","source_refs":["arXiv:2608.00001","arXiv:2608.00002"],"reason":"A grounded candidate survives."})
                else: lane_search.append({"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No current pair survives."})
            raw=json.dumps({"lane_search":lane_search,"candidates":[candidate],"generation_notes":"one candidate"});raw_path.write_text(raw);sha=hashlib.sha256(raw.encode()).hexdigest()
            state=replay_problem_generator_raw(storage=self.storage(root),primary_pool_path=pool,generator_raw_path=raw_path,generator_raw_sha256=sha,generator_requested_model="kimi-k3",generator_resolved_model="kimi-k3",source_generator_run_id="old-run",source_discovery_operator_version="old-op",auto_inbox_path=root/"auto.json",now=now)
        self.assertEqual(state["status"],"REPLAY_REQUIRES_SEMANTIC_REVIEW")
        self.assertGreater(state["summary"]["structurally_reviewable"],0)
        self.assertEqual(state["provider_calls_executed"],0);self.assertEqual(state["semantic_reviewer_calls_executed"],0)

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
