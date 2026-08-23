from __future__ import annotations

import copy, tempfile, unittest
from pathlib import Path

from .research_memory_wiki import build_research_memory_wiki, compile_research_memory_query_pack, lint_research_memory_wiki, load_research_memory_wiki


def base_inputs():
    search={"shadow_search_memory":{"closed_objects":[{"source_candidate_id":"CLOSED","title":"closed method","search_closure_certified":True,"dead_end_certified":False,"closure_layer":"method_realization","failure_layer":"method_realization","principle_update_allowed":False,"strongest_reduction":"matched simplification","current_source_refs":["arXiv:1"],"counter_explanation":{"reopen_condition":"new observable defeats reduction"}}],"hold_objects":[{"source_candidate_id":"HOLD","title":"missing support","closure_layer":"experiment_identifiability","failure_layer":"experiment_identifiability","principle_update_allowed":False,"current_source_refs":["arXiv:2"],"counter_explanation":{"reopen_condition":"new matched unit appears"}}]}}
    failures={"summary":{"assets":2},"assets":[{"signature":"execution:ssh-timeout","idea_id":"I1","affected_layer":"execution","reusable_precheck":"check runtime first","reuse_effectiveness":{"reuse_count":0},"does_not_imply":"science failure"}],"reusable_prechecks":[{"signature":"execution:ssh-timeout","affected_layer":"execution","reusable_precheck":"check runtime first","occurrences":1}]}
    meta={"summary":{"unresolved_principles":1},"unresolved_questions":[{"principle_id":"P1","idea_id":"I1","uncertainty":"which context transports"}]}
    portfolio={"summary":{"visible_candidates":1}}
    iteration={"nodes":[]}
    generator={"saturation_memory":{"blocked_problem_memory":{"blocked_candidate_attempts":0}}}
    claims=[{"claim_id":"N1","claim_type":"mechanism","claim_text":"narrow supported effect","adjudication_status":"SUPPORTED_NARROWLY","trace_complete":True,"evidence_ids":["E1"]}]
    return search,failures,meta,portfolio,iteration,generator,claims


class ResearchMemoryWikiTest(unittest.TestCase):
    def build(self):
        s,f,m,p,i,g,c=base_inputs();return build_research_memory_wiki(search_design_state=s,failure_asset_library=f,scientific_meta_trace=m,candidate_portfolio=p,experiment_iteration=i,generator_state=g,claim_ledger=c,generated_at="2026-08-19T00:00:00+00:00")

    def test_transient_operational_noise_is_archived_but_not_prompt_eligible(self):
        wiki=self.build();row=next(r for r in wiki["entries"] if r["kind"]=="FAILURE_ASSET")
        self.assertEqual(row["durability_class"],"transient");self.assertFalse(row["prompt_eligible"]);self.assertEqual(wiki["lint"]["summary"]["errors"],0)
        pack=compile_research_memory_query_pack(wiki,purpose="EXPERIMENT_DESIGN",context="ssh runtime")
        self.assertNotIn(row["memory_id"],pack["selected_memory_ids"])

    def test_repeated_execution_failure_becomes_systemic_precheck(self):
        s,f,m,p,i,g,c=base_inputs();f["assets"].append(copy.deepcopy(f["assets"][0]));f["reusable_prechecks"][0]["occurrences"]=2
        wiki=build_research_memory_wiki(search_design_state=s,failure_asset_library=f,scientific_meta_trace=m,candidate_portfolio=p,experiment_iteration=i,generator_state=g,claim_ledger=c)
        row=next(r for r in wiki["entries"] if r["kind"]=="FAILURE_ASSET")
        self.assertEqual(row["durability_class"],"recurring-systemic");self.assertTrue(row["prompt_eligible"])
        pack=compile_research_memory_query_pack(wiki,purpose="EXPERIMENT_DESIGN",context="ssh runtime")
        self.assertIn(row["memory_id"],pack["selected_memory_ids"]);self.assertIn("check runtime first",pack["text"])

    def test_non_core_closure_cannot_update_principle(self):
        wiki=self.build();bad=copy.deepcopy(wiki);row=next(r for r in bad["entries"] if r["kind"]=="SEARCH_CLOSURE");row["principle_update_allowed"]=True
        lint=lint_research_memory_wiki(bad);self.assertEqual(lint["status"],"FAIL");self.assertIn("non-core-memory-cannot-update-principle",{x["code"] for x in lint["errors"]})

    def test_scientific_dead_end_requires_core_principle_certificate(self):
        s,f,m,p,i,g,c=base_inputs();dead=copy.deepcopy(s["shadow_search_memory"]["closed_objects"][0]);dead.update({"source_candidate_id":"PSTOP","dead_end_certified":True,"closure_layer":"core_principle","failure_layer":"core_principle","principle_update_allowed":True});s["shadow_search_memory"]["closed_objects"].append(dead)
        wiki=build_research_memory_wiki(search_design_state=s,failure_asset_library=f,scientific_meta_trace=m,candidate_portfolio=p,experiment_iteration=i,generator_state=g,claim_ledger=c)
        row=next(r for r in wiki["entries"] if r["kind"]=="SCIENTIFIC_CLOSURE");self.assertTrue(row["scientific_dead_end_certified"]);self.assertEqual(row["affected_layer"],"core_principle")

    def test_missing_or_invalid_durable_wiki_fails_before_provider_use(self):
        with tempfile.TemporaryDirectory() as td:
            missing=Path(td)/"missing.json"
            with self.assertRaises(FileNotFoundError):load_research_memory_wiki(missing)
            bad=Path(td)/"bad.json";bad.write_text("{bad",encoding="utf-8")
            with self.assertRaises(ValueError):load_research_memory_wiki(bad)

    def test_query_packs_are_bounded_and_purpose_specific(self):
        wiki=self.build();idea=compile_research_memory_query_pack(wiki,purpose="IDEA_SEARCH",context="closed method",max_chars=1800);exp=compile_research_memory_query_pack(wiki,purpose="EXPERIMENT_DESIGN",context="supported effect",max_chars=1800)
        self.assertLessEqual(idea["summary"]["characters"],1800);self.assertLessEqual(exp["summary"]["characters"],1800);self.assertNotEqual(idea["query_pack_sha256"],exp["query_pack_sha256"]);self.assertFalse(idea["scientific_authority"])

    def test_discovery_failure_lessons_guide_idea_search_without_authority(self):
        s,f,m,p,i,g,c=base_inputs();cycle={"lessons":[{"lesson_id":"LS-X","candidate_id":"OLD-X","lesson_type":"SCIENTIFIC_REDUCTION","affected_layer":"problem_novelty","title":"failure-guided mutation","summary":"same-information reduction absorbs the old formulation","source_refs":["receipt:x"],"reopen_condition":"new structural observable forces opposite prediction","reusable_precheck":"run the matched simplification first","opposite_search_seed":"search outside the old reduction basin","scientific_authority":False}]}
        wiki=build_research_memory_wiki(search_design_state=s,failure_asset_library=f,scientific_meta_trace=m,candidate_portfolio=p,experiment_iteration=i,generator_state=g,claim_ledger=c,discovery_cycle=cycle)
        lesson=next(r for r in wiki["entries"] if r["kind"]=="DISCOVERY_LESSON")
        self.assertTrue(lesson["prompt_eligible"]);self.assertFalse(lesson["scientific_authority"]);self.assertFalse(lesson["principle_update_allowed"]);self.assertEqual(wiki["summary"]["discovery_lessons"],1)
        pack=compile_research_memory_query_pack(wiki,purpose="IDEA_SEARCH",context="failure guided mutation same information reduction")
        self.assertIn(lesson["memory_id"],pack["selected_memory_ids"]);self.assertIn("run the matched simplification first",pack["text"]);self.assertTrue(pack["policy"]["downstream_scientific_gates_unchanged"])

    def test_structured_mock_pc_patterns_become_zero_authority_paper_design_prechecks(self):
        s,f,m,p,i,g,c=base_inputs()
        paper_index={"summary":{"papers":1},"entries":[{"paper_id":"PAPER-X","review_learning":{"review_receipts":2,"decision_critical_objections":4,"category_counts":{"artifact-provenance":2,"empirical-sufficiency":2},"evidence_state_counts":{"existing-evidence":2,"missing-decisive-evidence":2},"action_class_counts":{"narrative-repair":2,"targeted-experiment":2},"targeted_experiment_proposals":2,"claim_expansion_requests_preserved_as_limitations":1}}]}
        wiki=build_research_memory_wiki(search_design_state=s,failure_asset_library=f,scientific_meta_trace=m,candidate_portfolio=p,experiment_iteration=i,generator_state=g,claim_ledger=c,paper_ledger_index=paper_index)
        lesson=next(r for r in wiki["entries"] if r["kind"]=="REVIEW_LESSON")
        self.assertEqual(lesson["durability_class"],"recurring-systemic");self.assertTrue(lesson["prompt_eligible"]);self.assertFalse(lesson["scientific_authority"]);self.assertFalse(lesson["principle_update_allowed"])
        pack=compile_research_memory_query_pack(wiki,purpose="PAPER_DESIGN",context="artifact provenance empirical sufficiency")
        self.assertIn(lesson["memory_id"],pack["selected_memory_ids"]);self.assertIn("artifact-provenance",pack["text"]);self.assertTrue(pack["policy"]["paper_review_pattern_cannot_authorize_experiments"]);self.assertGreaterEqual(pack["summary"]["review_lessons_selected"],1)
        serialized=str(lesson)
        self.assertNotIn("reviewer_text",serialized);self.assertNotIn("action_reason",serialized)

    def test_paper_design_budget_reserves_review_lesson_before_high_overlap_science_memory(self):
        s,f,m,p,i,g,c=base_inputs()
        for index in range(8):
            row=copy.deepcopy(s["shadow_search_memory"]["closed_objects"][0]);row["source_candidate_id"]=f"CLOSED-{index}";row["title"]="closed method matched simplification taxonomy representation skill invariance "*5;s["shadow_search_memory"]["closed_objects"].append(row)
        paper_index={"summary":{"papers":1},"entries":[{"paper_id":"PAPER-X","review_learning":{"review_receipts":2,"decision_critical_objections":3,"category_counts":{"novelty":1,"empirical-sufficiency":2},"evidence_state_counts":{"existing-evidence":1,"missing-decisive-evidence":2},"action_class_counts":{"narrative-repair":1,"preserve-limitation":2}}}]}
        wiki=build_research_memory_wiki(search_design_state=s,failure_asset_library=f,scientific_meta_trace=m,candidate_portfolio=p,experiment_iteration=i,generator_state=g,claim_ledger=c,paper_ledger_index=paper_index)
        pack=compile_research_memory_query_pack(wiki,purpose="PAPER_DESIGN",context="closed method matched simplification taxonomy representation skill invariance",max_chars=1200,max_items=16)
        self.assertGreaterEqual(pack["summary"]["review_lessons_selected"],1);self.assertEqual(pack["selected"][0]["kind"],"PAPER_DEVELOPMENT_GUIDANCE");self.assertEqual(pack["selected"][1]["kind"],"REVIEW_LESSON");self.assertTrue(pack["policy"]["paper_design_reserves_review_lesson_when_available"]);self.assertTrue(pack["policy"]["paper_design_reserves_development_guidance_when_available"])

    def test_senior_paper_development_guidance_is_always_zero_authority_and_reserved_for_paper_design(self):
        wiki=self.build();rows=[r for r in wiki["entries"] if r["kind"]=="PAPER_DEVELOPMENT_GUIDANCE"]
        self.assertEqual(len(rows),1);row=rows[0]
        self.assertTrue(row["prompt_eligible"]);self.assertEqual(row["durability_class"],"recurring-systemic");self.assertFalse(row["scientific_authority"]);self.assertFalse(row["principle_update_allowed"])
        self.assertEqual(len((row.get("guidance") or {}).get("dimensions") or []),4)
        backlog=(row.get("guidance") or {}).get("paper_development_backlog") or [];self.assertEqual(len(backlog),5);self.assertTrue(all(x.get("maturity")=="INITIAL_DRAFT_NEEDS_DEEPENING" and x.get("paper_only_work_allowed") is True and x.get("may_execute_new_experiments") is False for x in backlog))
        pack=compile_research_memory_query_pack(wiki,purpose="PAPER_DESIGN",context="method related work experiment clarity",max_chars=1800,max_items=8)
        self.assertEqual(pack["selected"][0]["kind"],"PAPER_DEVELOPMENT_GUIDANCE");self.assertIn(row["memory_id"],pack["selected_memory_ids"]);self.assertTrue(pack["policy"]["paper_development_guidance_cannot_authorize_experiments"])
        self.assertIn("initial drafts",pack["text"].lower())


if __name__=="__main__":unittest.main()
