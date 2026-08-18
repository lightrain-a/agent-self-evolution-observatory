from __future__ import annotations

import json,re,unittest

from .paper_first_problem_discovery_contract import DISCOVERY_LANES,SEARCH_PORTFOLIO_PRIMITIVES,LANE_EVIDENCE_REQUIRED,LANE_SOURCE_ROLES
from .paper_first_problem_search_portfolio import DEFAULT_MAX_PARALLEL_CALLS,_expansion_prompt,_formulation_prompt,_fresh_phenomenon_priors,_fresh_phenomenon_target,_inversion_asset_records,_opposite_search_priors,_valid_seed,run_search_portfolio
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
        if role.startswith("repair-"):
            parents=json.loads(prompt.split("PARENTS=",1)[1].split(". Return JSON only:",1)[0]);repairs=[]
            for p in parents:
                children=[]
                for j in range(2):
                    children.append({"repair_axis":f"measurement-{j}","title":p["title"]+f" repair {j}","problem_seed":p["problem_seed"]+f" repaired {j}","scientific_tension":p["scientific_tension"]+" after reviewer attack","problem_family":p["problem_family"],"structural_signature":p["structural_signature"]+f"|repair-{j}","agent_specific_constraint":p["agent_specific_constraint"],"paperability_axes":{"P":{"status":"OPEN","rationale":"principle unresolved"},"M":{"status":"PLAUSIBLE","rationale":"distinct method boundary"},"E":{"status":"SUPPORTED","rationale":"grounded phenomenon"}},"why_attack_no_longer_applies":"changes the measured object","scores":{"importance":88,"specificity":88,"seed_distance":88,"evidence_grounding":88}})
                repairs.append({"parent_id":p["seed_id"],"attack":"closest-work collision on the original object","attack_class":"CLOSEST_WORK","children":children})
            return {"text":json.dumps({"repairs":repairs}),"resolved_model":"doubao-seed-evolving"}
        if role.startswith("formulate-"):
            branches=json.loads(prompt.split("BRANCHES=",1)[1].split(". SEARCH_CLOSURE_MEMORY=",1)[0]);rows=[{"candidate_id":f"PORT-{i}","source_branch_id":b["seed_id"],"title":b["title"],"discovery_lane":b["discovery_lane"],"paperability_axes":b.get("paperability_axes") or {"E":{"status":"SUPPORTED","rationale":"grounded phenomenon"}}} for i,b in enumerate(branches)]
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
        self.assertGreater(state["summary"]["reviewer_attacks"],0)
        self.assertGreater(state["summary"]["repair_children"],0)
        self.assertTrue(state["policy"]["attack_repair_split_before_formulation"])
        self.assertTrue(state["policy"]["principle_reduction_does_not_auto_close_other_paperability_axes"])
        self.assertGreater(state["summary"]["formulated_candidates"],0)
        self.assertFalse(state["scientific_authority"])

    def test_fresh_phenomenon_prior_uses_evidence_level_closure_without_blacklisting_source(self):
        boundary_sha="a"*64;failure_sha="b"*64;older_sha="c"*64
        records=[
            {"ref":"arXiv:new-boundary","publication_date":"2026-08-13","title":"New boundary","typed_evidence":{"measured_failures":[{"text":"Utility collapses after a restrictive update.","text_sha256":failure_sha}],"boundary_observations":[{"text":"Reward rises from 0.56 at 16 tokens to 0.637 at K=32 and then plateaus.","text_sha256":boundary_sha}]},"empirical_facts":[{"text":"Quantitative sensitivity curve."}]},
            {"ref":"arXiv:new-no-anomaly","publication_date":"2026-08-13","title":"New but smooth","typed_evidence":{"measured_failures":[],"boundary_observations":[]},"empirical_facts":[{"text":"Performance improves."}]},
            {"ref":"arXiv:older-boundary","publication_date":"2026-08-12","title":"Older boundary","typed_evidence":{"measured_failures":[{"text":"The older method fails despite matched support.","text_sha256":older_sha}],"boundary_observations":[]},"empirical_facts":[]},
        ]
        priors=_fresh_phenomenon_priors(records)
        self.assertEqual([row["phenomenon_id"] for row in priors],[failure_sha,boundary_sha,older_sha])
        self.assertEqual(_fresh_phenomenon_target(records,1)["phenomenon_id"],failure_sha)
        memory={"closed_objects":[{"search_closure_certified":True,"dead_end_certified":False,"failure_layer":"method_realization","fresh_phenomenon_closure":{"source_ref":"arXiv:new-boundary","closed_evidence_sha256":[failure_sha],"scientific_authority":False}}],"inversion_asset_evidence":[],"positive_residual_asset_evidence":[]}
        open_priors=_fresh_phenomenon_priors(records,dead_end_memory=memory)
        self.assertEqual([row["phenomenon_id"] for row in open_priors],[boundary_sha,older_sha])
        self.assertEqual(open_priors[0]["ref"],"arXiv:new-boundary")
        target=_fresh_phenomenon_target(records,1,dead_end_memory=memory)
        self.assertEqual(target["phenomenon_id"],boundary_sha)
        prompt=_expansion_prompt("UNEXPLAINED_BOUNDARY",records,2,memory,fresh_target_ref=target["ref"],fresh_target_phenomenon_id=target["phenomenon_id"])
        self.assertIn("FRESH-PHENOMENON BOUNDARY-COVERAGE REQUIREMENT",prompt)
        self.assertIn("FRESH_PHENOMENON_TARGET",prompt)
        self.assertIn(boundary_sha,prompt)
        self.assertIn("Reward rises from 0.56",prompt)
        self.assertNotIn(failure_sha,prompt.split("FRESH_PHENOMENON_PRIORS=",1)[1].split(". LAYER-TYPED CLOSED-BASIN INVERSION PRIORS=",1)[0])
        self.assertIn("strongest mature reduction",prompt)
        self.assertIn("independent truth",prompt)

    def test_fresh_boundary_precision_excludes_protocol_rules_and_example_intros(self):
        records=[
            {"ref":"arXiv:protocol","publication_date":"2026-08-13","title":"Protocol","typed_evidence":{"measured_failures":[],"boundary_observations":[
                {"text":"For batches of at least 20 readable posters, a blinded check may only reduce the score; it is not applied to the mini benchmark.","text_sha256":"a"*64},
                {"text":"All components use temperature 0, and we set the security threshold to 0.5.","text_sha256":"b"*64},
                {"text":"The box below illustrates one representative failure trace from the first evolution round.","text_sha256":"c"*64},
                {"text":"For efficiency regressions, we run the tool on all 182 high-confidence regressions at the primary T=2.0 threshold.","text_sha256":"f"*64},
            ]},"empirical_facts":[]},
            {"ref":"arXiv:empirical","publication_date":"2026-08-13","title":"Empirical","typed_evidence":{"measured_failures":[],"boundary_observations":[
                {"text":"Reward rises from 0.56 at 16 tokens to 0.637 at 32 tokens and then plateaus.","text_sha256":"d"*64},
                {"text":"Full skill evolution further raises success to 34.5%, 6.25 points above the seed.","text_sha256":"e"*64},
            ]},"empirical_facts":[]},
        ]
        priors=_fresh_phenomenon_priors(records)
        self.assertEqual([row["phenomenon_id"] for row in priors],["d"*64])

    def test_measured_failure_requires_directional_degradation_not_domain_noun(self):
        records=[
            {"ref":"arXiv:positive","publication_date":"2026-08-13","title":"Positive restoration","typed_evidence":{"measured_failures":[
                {"text":"Restoration agents consistently outperform model-based methods across most degradation types.","text_sha256":"a"*64},
                {"text":"The collaborative system increases success from 0.82 to 0.88 on mixed degradation types.","text_sha256":"b"*64},
                {"text":"Retrieval robustness is evaluated using Attack Success Rate (ASR), nDCG@5, and malicious-skill count.","text_sha256":"e"*64},
            ],"boundary_observations":[]},"empirical_facts":[]},
            {"ref":"arXiv:negative","publication_date":"2026-08-13","title":"Negative boundary","typed_evidence":{"measured_failures":[
                {"text":"Held-out accuracy degrades from 0.82 to 0.61 after the persistent update.","text_sha256":"c"*64},
                {"text":"The update degrades task success by 12 points under context shift.","text_sha256":"d"*64},
            ],"boundary_observations":[]},"empirical_facts":[]},
        ]
        priors=_fresh_phenomenon_priors(records)
        self.assertEqual({row["phenomenon_id"] for row in priors},{"c"*64,"d"*64})
        self.assertTrue(all(row["ref"]=="arXiv:negative" for row in priors))

    def test_quantitative_anomaly_requires_actual_boundary_not_ordinary_positive_gain(self):
        records=[
            {"ref":"arXiv:positive","publication_date":"2026-08-13","title":"Ordinary gain","typed_evidence":{"measured_failures":[],"boundary_observations":[]},"empirical_facts":[
                {"text":"The method improves over the strongest baseline by 6.5 points.","text_sha256":"a"*64},
                {"text":"Success increases from 0.72 to 0.81 on held-out tasks.","text_sha256":"b"*64},
            ]},
            {"ref":"arXiv:boundary","publication_date":"2026-08-13","title":"Nonmonotonic boundary","typed_evidence":{"measured_failures":[],"boundary_observations":[]},"empirical_facts":[
                {"text":"Reward rises from 0.56 at 16 tokens to 0.637 at 32 tokens and then plateaus at larger budgets.","text_sha256":"c"*64},
                {"text":"Performance improves from 0.60 with one retrieval to 0.64 with three, but additional retrievals yield no consistent gain.","text_sha256":"d"*64},
            ]},
        ]
        priors=_fresh_phenomenon_priors(records)
        self.assertEqual({row["phenomenon_id"] for row in priors},{"c"*64,"d"*64})
        self.assertTrue(all(row["ref"]=="arXiv:boundary" for row in priors))

    def test_exact_support_hold_pauses_only_one_evidence_object(self):
        held_sha="a"*64; open_sha="b"*64
        records=[{"ref":"arXiv:held","publication_date":"2026-08-13","title":"Two boundaries","typed_evidence":{"measured_failures":[
            {"text":"Held-out accuracy drops by 7 points when the unavailable lineage is required.","text_sha256":held_sha},
            {"text":"Task success drops by 4 points under a separate context shift.","text_sha256":open_sha},
        ],"boundary_observations":[]},"empirical_facts":[]}]
        memory={"hold_objects":[{"dead_end_certified":False,"fresh_phenomenon_hold":{"source_ref":"arXiv:held","evidence_sha256":held_sha,"scientific_authority":False}}]}
        priors=_fresh_phenomenon_priors(records,dead_end_memory=memory)
        self.assertEqual({row["phenomenon_id"] for row in priors},{open_sha})
        self.assertEqual(priors[0]["ref"],"arXiv:held")

    def test_provenance_bound_inversion_asset_becomes_primary_search_registry_record(self):
        memory={"inversion_asset_evidence":[{"asset_ref":"first-party-asset:demo@"+"a"*40,"title":"Author implementation","primary_url":"https://github.com/example/repo","source_sha256":"b"*64,"asset_manifest_artifact":"generated/demo.json","asset_manifest_file_sha256":"c"*64,"commit":"a"*40,"empirical_facts":["The released controller reuses the same evaluation signal in every selection round."],"scientific_authority":False}]}
        rows=_inversion_asset_records(memory)
        self.assertEqual(len(rows),1)
        self.assertTrue(rows[0]["primary_source_verified"])
        self.assertEqual(rows[0]["ref"],memory["inversion_asset_evidence"][0]["asset_ref"])
        lane="IDENTIFIABILITY_GAP";roles=LANE_SOURCE_ROLES[lane]
        seed={"discovery_lane":lane,"title":"feedback path","problem_seed":"does feedback matter","structural_signature":"feedback|evaluation|selection|drift","empirical_evidence":{"source_a":{"ref":rows[0]["ref"],"claim":"selection reuses evaluator","evidence_role":roles[0]},"source_b":{"ref":rows[0]["ref"],"claim":"same released path","evidence_role":roles[1]},"relation":"same first-party implementation exposes the causal path"},"lane_evidence":{key:"grounded" for key in LANE_EVIDENCE_REQUIRED[lane]}}
        self.assertTrue(_valid_seed(seed,{rows[0]["ref"]:rows[0]}))
        prompt=_expansion_prompt(lane,self.records(),1,memory)
        self.assertIn(rows[0]["ref"],prompt)
        self.assertIn("Author implementation",prompt)
        self.assertIn("Seed 1 MUST directly execute one certified opposite-search prior",prompt)
        self.assertIn("if the first-party implementation directly exposes whether a causal/update edge exists, do NOT formulate identifiability of that edge",prompt)

    def test_inactive_inversion_asset_is_retained_in_memory_but_excluded_from_search(self):
        active={"asset_ref":"first-party-asset:active@"+"a"*40,"title":"Active asset","primary_url":"https://github.com/example/active","source_sha256":"b"*64,"empirical_facts":["Active first-party fact."],"scientific_authority":False}
        inactive={"asset_ref":"first-party-asset:inactive@"+"c"*40,"title":"Inactive asset","primary_url":"https://github.com/example/inactive","source_sha256":"d"*64,"empirical_facts":["Inactive first-party fact."],"search_active":False,"scientific_authority":False}
        stale_active_copy={**inactive,"search_active":True,"title":"Inactive asset stale receipt"}
        memory={"inversion_asset_evidence":[active,inactive],"blocked_objects":[{"source_candidate_id":"ACTIVE","dead_end_certified":True,"opposite_search_asset_evidence":active,"counter_explanation":{"opposite_principle":"active principle","opposite_search_seed":"active seed","reopen_condition":"fresh evidence","evidence_refs":["asset:active"]}},{"source_candidate_id":"INACTIVE-STALE","dead_end_certified":True,"opposite_search_asset_evidence":stale_active_copy,"counter_explanation":{"opposite_principle":"inactive stale principle","opposite_search_seed":"inactive stale seed","reopen_condition":"fresh evidence","evidence_refs":["asset:inactive"]}},{"source_candidate_id":"INACTIVE","dead_end_certified":True,"opposite_search_asset_evidence":inactive,"counter_explanation":{"opposite_principle":"inactive principle","opposite_search_seed":"inactive seed","reopen_condition":"fresh evidence","evidence_refs":["asset:inactive"]}}]}
        rows=_inversion_asset_records(memory)
        self.assertEqual([row["ref"] for row in rows],[active["asset_ref"]])
        priors=_opposite_search_priors(memory)
        self.assertEqual([row["source_candidate_id"] for row in priors],["ACTIVE"])
        prompt=_expansion_prompt("UNEXPLAINED_BOUNDARY",self.records(),2,memory)
        self.assertIn("Active asset",prompt)
        self.assertNotIn("Inactive asset",prompt)
        certified_slice=prompt.split("LAYER-TYPED CLOSED-BASIN INVERSION PRIORS=",1)[1].split(". CLOSED-BASIN SEARCH MEMORY",1)[0]
        self.assertNotIn("inactive seed",certified_slice)
        self.assertNotIn("inactive stale seed",certified_slice)
        self.assertNotIn("Inactive asset stale receipt",prompt)

    def test_certified_search_closure_emits_opposite_search_prior_without_authority(self):
        memory={"closed_objects":[{"source_candidate_id":"D1","basin":"method-closure-x","search_closure_certified":True,"dead_end_certified":False,"failure_layer":"method_realization","principle_update_allowed":False,"counter_explanation":{"type":"IMPOSSIBILITY_OR_INVARIANCE","opposite_principle":"Evidence sufficiency is relevance-conditioned, not coverage-conditioned.","opposite_search_seed":"Search for relevance-conditioned evidence debt.","reopen_condition":"Fresh evidence must expose a same-information residual.","evidence_refs":["artifact:x"]}}],"hold_objects":[{"source_candidate_id":"H1","dead_end_certified":False,"counter_explanation":{"opposite_principle":"must not appear","opposite_search_seed":"must not appear"}}]}
        priors=_opposite_search_priors(memory)
        self.assertEqual(len(priors),1)
        self.assertEqual(priors[0]["source_candidate_id"],"D1")
        prompt=_expansion_prompt("CONTRADICTION",self.records(),1,memory)
        self.assertIn("CLOSED-BASIN INVERSION is a search prior, never authority",prompt)
        self.assertIn("method_realization",prompt)
        self.assertIn("relevance-conditioned evidence debt",prompt)
        self.assertNotIn("must not appear",prompt.split("LAYER-TYPED CLOSED-BASIN INVERSION PRIORS=",1)[1].split(". CLOSED-BASIN SEARCH MEMORY",1)[0])

    def test_formulation_prompt_never_turns_unresolved_reduction_into_a_fake_clear(self):
        records=self.records();registry={row["ref"]:row for row in records};branch={"seed_id":"B1","parent_id":"","branch_depth":0,"discovery_lane":"UNEXPLAINED_BOUNDARY","title":"Boundary","problem_seed":"Question","scientific_tension":"Tension","problem_family":"boundary","structural_signature":"boundary|signal","agent_specific_constraint":"agent-specific","empirical_evidence":{"source_a":{"ref":records[0]["ref"],"claim":"A","evidence_role":"EMPIRICAL_FACT"},"source_b":{"ref":records[0]["ref"],"claim":"B","evidence_role":"EMPIRICAL_FACT"}},"lane_evidence":{},"cross_domain_origin":""}
        prompt=_formulation_prompt([branch],registry,{})
        self.assertIn("never set all_exact_reduction_tests_resolved=true while any pending pattern",prompt)
        self.assertIn("Do not manufacture a reduction resolution from absence of evidence",prompt)
        self.assertIn("zero-authority pre-F0 evidence-acquisition hold",prompt)
        self.assertIn("P/M/E/B/T/S",prompt)
        self.assertIn("exact same-information reduction must be rerun",prompt)

    def test_every_current_reduction_pattern_has_nonautomatic_audit_class(self):
        rows=reduction_pattern_audit();self.assertEqual(len(rows),34);self.assertTrue(all(row["automatic_veto"] is False for row in rows));self.assertEqual({row["audit_class"] for row in rows},{"VALID_HARD_VETO","SOFT_COLLISION","NEEDS_EXACT_REDUCTION_TEST","TOO_GENERIC_TO_VETO"})

if __name__=="__main__":unittest.main()
