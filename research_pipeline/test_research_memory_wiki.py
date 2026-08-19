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


if __name__=="__main__":unittest.main()
