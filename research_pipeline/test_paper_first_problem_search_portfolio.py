from __future__ import annotations

import json,re,unittest

from .paper_first_problem_discovery_contract import DISCOVERY_LANES,SEARCH_PORTFOLIO_PRIMITIVES,LANE_EVIDENCE_REQUIRED,LANE_SOURCE_ROLES
from .paper_first_problem_search_portfolio import DEFAULT_MAX_PARALLEL_CALLS,_expansion_prompt,_formulation_prompt,_opposite_search_priors,run_search_portfolio
from .paper_first_fresh_saturation import reduction_pattern_audit


class SearchPortfolioTest(unittest.TestCase):
    def records(self):
        return [{"ref":f"arXiv:2608.30{i:03d}","title":f"Primary {i}","abstract":f"Primary result {i} for self-evolving agents.","empirical_facts":[{"text":f"Results show condition {i} changes held-out success."}],"primary_url":f"https://arxiv.org/abs/2608.30{i:03d}","source_sha256":str(i)*64,"primary_source_verified":True} for i in range(1,7)]

    def caller(self,**kwargs):
        role=kwargs["role"];prompt=kwargs["prompt"]
        if role.startswith("expand-"):
            lane=next(x for x in SEARCH_PORTFOLIO_PRIMITIVES if x.lower() in role)
            count=int(re.search(r"Generate exactly (\d+)",prompt).group(1));seeds=[]
            for i in range(count):
                roles=LANE_SOURCE_ROLES[lane];refs=[f"arXiv:2608.30{(i%3)+1:03d}",f"arXiv:2608.30{((i+1)%3)+4:03d}"]
                seeds.append({"seed_id":f"{lane}-{i}","title":f"{lane} seed {i}","problem_seed":f"Question {lane} {i}","scientific_tension":f"Tension {lane} {i}","problem_family":f"family-{i%3}","structural_signature":f"{lane}|object-{i}|regime-{i%2}|effect-{i}","agent_specific_constraint":f"self-authored persistent constraint {i}","empirical_evidence":{"source_a":{"ref":refs[0],"claim":"grounded A","evidence_role":roles[0]},"source_b":{"ref":refs[1],"claim":"grounded B","evidence_role":roles[1]},"relation":"typed relation"},"lane_evidence":{key:f"{key}-{i}" for key in LANE_EVIDENCE_REQUIRED[lane]},"cross_domain_origin":"control theory" if lane=="CROSS_DOMAIN_STRUCTURAL_ANALOGY" else "","scores":{"importance":75+i,"specificity":75,"seed_distance":80-i,"evidence_grounding":85}})
            return {"text":json.dumps({"seeds":seeds}),"resolved_model":"doubao-seed-evolving"}
        if role.startswith("evolve-"):
            parents=json.loads(prompt.split("PARENTS=",1)[1].split(". Return JSON only:",1)[0]);children=[]
            for p in parents:children.append({"parent_id":p["seed_id"],"title":p["title"]+" child","problem_seed":p["problem_seed"]+" with changed regime","scientific_tension":p["scientific_tension"]+" sharpened","problem_family":p["problem_family"],"structural_signature":p["structural_signature"]+"|child","agent_specific_constraint":p["agent_specific_constraint"],"changed_assumption":"one assumption","why_deeper":"more precise","scores":{"importance":85,"specificity":85,"seed_distance":85,"evidence_grounding":85}})
            return {"text":json.dumps({"children":children}),"resolved_model":"doubao-seed-evolving"}
        if role.startswith("formulate-"):
            branches=json.loads(prompt.split("BRANCHES=",1)[1].split(". DEAD_END_MEMORY=",1)[0]);rows=[{"candidate_id":f"PORT-{i}","source_branch_id":b["seed_id"],"title":b["title"],"discovery_lane":b["discovery_lane"]} for i,b in enumerate(branches)]
            return {"text":json.dumps({"candidates":rows,"rejected":[]}),"resolved_model":"doubao-seed-evolving"}
        raise AssertionError(role)

    def test_default_parallelism_is_provider_burst_safe(self):
        self.assertEqual(DEFAULT_MAX_PARALLEL_CALLS,2)

    def test_search_portfolio_expands_diversifies_and_evolves_before_reduction(self):
        state=run_search_portfolio(records=self.records(),call=self.caller,model="ark-code-latest",target_raw_seeds=20,archive_capacity=16,evolution_parents=8,second_generation=4,formulation_budget=8,max_parallel_calls=3)
        self.assertTrue(state["policy"]["expansion_precedes_reduction"])
        self.assertTrue(state["policy"]["mature_theory_veto_delayed_until_formulation"])
        self.assertEqual(len(state["lane_counts"]),len(SEARCH_PORTFOLIO_PRIMITIVES))
        self.assertGreaterEqual(state["summary"]["raw_seeds"],20)
        self.assertGreaterEqual(state["summary"]["semantic_unique"],len(SEARCH_PORTFOLIO_PRIMITIVES))
        self.assertEqual(state["summary"]["archive_lane_coverage"],len(SEARCH_PORTFOLIO_PRIMITIVES))
        self.assertGreater(state["summary"]["evolved_branches"],0)
        self.assertGreaterEqual(state["summary"]["max_branch_depth"],1)
        self.assertGreater(state["summary"]["formulated_candidates"],0)
        self.assertFalse(state["scientific_authority"])

    def test_certified_dead_end_emits_opposite_search_prior_without_authority(self):
        memory={"blocked_objects":[{"source_candidate_id":"D1","basin":"principle-dead-end-x","dead_end_certified":True,"counter_explanation":{"type":"IMPOSSIBILITY_OR_INVARIANCE","opposite_principle":"Evidence sufficiency is relevance-conditioned, not coverage-conditioned.","opposite_search_seed":"Search for relevance-conditioned evidence debt.","reopen_condition":"Fresh evidence must expose a same-information residual.","evidence_refs":["artifact:x"]}}],"hold_objects":[{"source_candidate_id":"H1","dead_end_certified":False,"counter_explanation":{"opposite_principle":"must not appear","opposite_search_seed":"must not appear"}}]}
        priors=_opposite_search_priors(memory)
        self.assertEqual(len(priors),1)
        self.assertEqual(priors[0]["source_candidate_id"],"D1")
        prompt=_expansion_prompt("CONTRADICTION",self.records(),1,memory)
        self.assertIn("DEAD-END INVERSION is a search prior, never authority",prompt)
        self.assertIn("relevance-conditioned evidence debt",prompt)
        self.assertNotIn("must not appear",prompt.split("CERTIFIED DEAD-END INVERSION PRIORS=",1)[1].split(". DEAD-END SEARCH MEMORY",1)[0])

    def test_formulation_prompt_never_turns_unresolved_reduction_into_a_fake_clear(self):
        records=self.records();registry={row["ref"]:row for row in records};branch={"seed_id":"B1","parent_id":"","branch_depth":0,"discovery_lane":"UNEXPLAINED_BOUNDARY","title":"Boundary","problem_seed":"Question","scientific_tension":"Tension","problem_family":"boundary","structural_signature":"boundary|signal","agent_specific_constraint":"agent-specific","empirical_evidence":{"source_a":{"ref":records[0]["ref"],"claim":"A","evidence_role":"EMPIRICAL_FACT"},"source_b":{"ref":records[0]["ref"],"claim":"B","evidence_role":"EMPIRICAL_FACT"}},"lane_evidence":{},"cross_domain_origin":""}
        prompt=_formulation_prompt([branch],registry,{})
        self.assertIn("never set all_exact_reduction_tests_resolved=true while any pending pattern",prompt)
        self.assertIn("Do not manufacture a reduction resolution from absence of evidence",prompt)
        self.assertIn("zero-authority reduction-pending hold",prompt)

    def test_every_current_reduction_pattern_has_nonautomatic_audit_class(self):
        rows=reduction_pattern_audit();self.assertEqual(len(rows),34);self.assertTrue(all(row["automatic_veto"] is False for row in rows));self.assertEqual({row["audit_class"] for row in rows},{"VALID_HARD_VETO","SOFT_COLLISION","NEEDS_EXACT_REDUCTION_TEST","TOO_GENERIC_TO_VETO"})

if __name__=="__main__":unittest.main()
