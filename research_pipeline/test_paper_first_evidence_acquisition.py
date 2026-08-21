from __future__ import annotations

import unittest

from .paper_first_evidence_acquisition import (
    adjudicate_evidence_receipts,
    build_provisional_evidence_plan,
    compile_evidence_designs,
    compile_evidence_reviews,
    compile_harness_implementation_receipts,
    compile_harness_runtime_invalidations,
    compile_operationalization_recompiles,
    compile_substrate_preflight,
    evidence_design_prompt,
    operationalization_recompile_prompt,
    validate_evidence_plan,
)


def machine(rows=2):
    q=[]
    for i in range(rows):
        q.append({
            "candidate_id":f"C{i+1}","title":f"candidate {i+1}","discovery_lane":"UNEXPLAINED_BOUNDARY",
            "source_branch_id":f"B{i+1}","blockers":["reduction-falsifiability-contract-incomplete","unresolved-exact-reduction-test:1"],
            "irreducible_object":f"scientific object {i+1}","endpoint_headroom_requirement":"nondegenerate endpoint",
            "exact_prediction":f"prediction {i+1}","strongest_same_information_baseline":f"baseline {i+1}","cheapest_problem_falsifier":f"falsifier {i+1}",
            "scientific_authority":False,
        })
    return {"scientific_authority":False,"authority":{"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False},"problem_falsifier_queue":q}


def design_for(entry, *, source="REPRODUCIBLE_FIRST_PARTY", mode="FIRST_PARTY_REPLAY", adapter="EXISTING_REPLAY_HARNESS"):
    return {
        "candidate_id":entry["candidate_id"],
        "frozen_exact_prediction":entry["frozen_exact_prediction"],
        "frozen_same_information_baseline":entry["frozen_same_information_baseline"],
        "frozen_falsifier_expression":entry["frozen_falsifier_expression"],
        "changed_variable":"","source_specificity":source,"acquisition_mode":mode,
        "reproduction_target":"reproduce the measured boundary with a neutral harness",
        "independent_truth":"environment or program truth frozen before candidate evaluation",
        "causal_unit":"matched decision state","observable":"paired outcome difference",
        "intervention":"replay both arms from one frozen state without fitting the candidate mechanism",
        "same_information_lock":"both arms and the mature baseline consume the same state, actions, and budget",
        "matched_baseline_execution":"execute the strongest baseline on exactly the same units and observations",
        "anti_bake_in_controls":["truth is external","units are sampled before labels","candidate rule never generates outcomes"],
        "decision_criteria":{"baseline_reduction_supported":"baseline reproduces the prediction","candidate_residual_survives":"residual prediction remains after matched baseline","inconclusive":"protocol-valid data do not separate them"},
        "single_variable_repair_if_inconclusive":"increase paired repeats only",
        "execution_adapter":adapter,
        "budget":{"max_units":24,"max_wall_minutes":30,"max_gpu_hours":0.0,"max_model_calls":0},
    }


def clear_review(plan):
    rows=[r for r in plan.get("entries") or [] if r.get("status")=="NEEDS_INDEPENDENT_EVIDENCE_REVIEW"]
    checks={"independent_truth_valid":True,"scientific_object_preserved":True,"no_mechanism_bake_in":True,"same_information_baseline_valid":True,"falsifier_not_method_evaluation":True,"outcome_semantics_valid":True,"bounded_budget_valid":True,"prior_support_constraint_respected":True,"operationalization_equivalence_valid":True}
    payload={"reviews":[{"candidate_id":r["candidate_id"],"verdict":"CLEAR_FOR_SUBSTRATE_PREFLIGHT","checks":checks,"reason":"all bounded evidence-contract checks pass","required_revision":""} for r in rows]}
    return compile_evidence_reviews(plan,payload,reviewer_model="independent-reviewer")


def preflight_ready(plan):
    rows=[r for r in plan.get("entries") or [] if r.get("status")=="READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT"]
    receipts={"receipts":[{"candidate_id":r["candidate_id"],"contract_sha256":r["contract_sha256"],"disposition":"EXISTING_HARNESS_READY","reason":"existing local harness is available","inventory_summary":"frozen harness and matched units passed local inventory probe","asset_manifest_sha256":"d"*64,"probe_passed":True,"budget_feasible":True} for r in rows]}
    return compile_substrate_preflight(plan,receipts)


class EvidenceAcquisitionTest(unittest.TestCase):
    def test_reduction_pending_becomes_bounded_provisional_portfolio(self):
        state=build_provisional_evidence_plan(machine(6),run_id="shadow-new")
        self.assertEqual(state["summary"]["provisional_problem_candidates"],6)
        self.assertEqual(state["summary"]["design_selected"],4)
        self.assertEqual(state["summary"]["deferred_by_portfolio_budget"],2)
        self.assertEqual(validate_evidence_plan(state),[])
        self.assertEqual(state["summary"]["paper_design_authorized"],0)

    def test_provisional_plan_preserves_primary_source_refs_for_terminal_holds(self):
        m=machine(1);m["problem_falsifier_queue"][0]["candidate"]={"empirical_evidence":{"source_a":{"ref":"arXiv:2608.13040"},"source_b":{"ref":"arXiv:2608.13040"}}}
        state=build_provisional_evidence_plan(m)
        self.assertEqual(state["entries"][0]["source_refs"],["arXiv:2608.13040"])

    def test_memory_query_pack_is_mandatory_prompt_context_not_authority(self):
        plan=build_provisional_evidence_plan(machine(1));pack={"purpose":"EXPERIMENT_DESIGN","query_pack_sha256":"a"*64,"selected_memory_ids":["MEM-X"],"text":"MEM-X precheck=check prior runtime integrity","scientific_authority":False}
        prompt,ids=evidence_design_prompt(plan,research_memory_query_pack=pack)
        self.assertEqual(ids,["C1"]);self.assertIn("HISTORICAL_RESEARCH_MEMORY",prompt);self.assertIn("MEM-X",prompt);self.assertIn("never a scientific veto",prompt)
        source=design_for(plan["entries"][0],source="SOURCE_SPECIFIC_REQUIRED",mode="PRIMARY_ASSET_REUSE",adapter="PRIMARY_ASSET_ONLY");pending=compile_evidence_designs(plan,{"designs":[source]})
        reprompt,rids=operationalization_recompile_prompt(pending,research_memory_query_pack=pack)
        self.assertEqual(rids,["C1"]);self.assertIn("MEM-X",reprompt);self.assertIn("historical success cannot authorize transport",reprompt)

    def test_first_party_design_gets_execution_not_scientific_authority(self):
        plan=build_provisional_evidence_plan(machine(1))
        state=compile_evidence_designs(plan,{"designs":[design_for(plan["entries"][0])]},part=1,design_model="designer")
        self.assertEqual(state["entries"][0]["status"],"NEEDS_INDEPENDENT_EVIDENCE_REVIEW")
        self.assertFalse(state["entries"][0]["execution_authorized"])
        state=clear_review(state);row=state["entries"][0]
        self.assertEqual(row["status"],"READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT")
        self.assertFalse(row["execution_authorized"])
        state=preflight_ready(state);row=state["entries"][0]
        self.assertEqual(row["status"],"READY_FOR_BOUNDED_EVIDENCE_ACQUISITION")
        self.assertTrue(row["execution_authorized"])
        self.assertTrue(row["authority"]["bounded_evidence_acquisition"])
        self.assertFalse(row["authority"]["paper_design"])
        self.assertEqual(validate_evidence_plan(state),[])

    def test_compiler_owns_frozen_fields_and_empty_repair_is_valid_stop_policy(self):
        plan=build_provisional_evidence_plan(machine(1));entry=plan["entries"][0];d=design_for(entry)
        d["frozen_exact_prediction"]="model attempted drift";d["frozen_same_information_baseline"]="drift";d["frozen_falsifier_expression"]="drift";d["single_variable_repair_if_inconclusive"]=""
        state=compile_evidence_designs(plan,{"designs":[d]});row=state["entries"][0]
        self.assertEqual(row["status"],"NEEDS_INDEPENDENT_EVIDENCE_REVIEW")
        self.assertEqual(row["design"]["frozen_exact_prediction"],entry["frozen_exact_prediction"])
        self.assertEqual(row["design"]["frozen_same_information_baseline"],entry["frozen_same_information_baseline"])
        self.assertEqual(row["design"]["frozen_falsifier_expression"],entry["frozen_falsifier_expression"])
        self.assertEqual(row["design"]["decision_rule"]["REDUCTION_SUPPORTED"],d["decision_criteria"]["baseline_reduction_supported"])
        self.assertEqual(row["design"]["decision_rule"]["RESIDUAL_SURVIVES"],d["decision_criteria"]["candidate_residual_survives"])

    def test_independent_review_blocks_bake_in_and_same_model_self_review(self):
        plan=build_provisional_evidence_plan(machine(1));state=compile_evidence_designs(plan,{"designs":[design_for(plan["entries"][0])]},design_model="designer")
        checks={"independent_truth_valid":True,"scientific_object_preserved":True,"no_mechanism_bake_in":False,"same_information_baseline_valid":True,"falsifier_not_method_evaluation":True,"outcome_semantics_valid":True,"bounded_budget_valid":True,"prior_support_constraint_respected":True,"operationalization_equivalence_valid":True}
        payload={"reviews":[{"candidate_id":"C1","verdict":"BLOCK_BAKE_IN","checks":checks,"reason":"synthetic truth encodes the target mechanism","required_revision":""}]}
        with self.assertRaisesRegex(ValueError,"reviewer must be independent"):
            compile_evidence_reviews(state,payload,reviewer_model="designer")
        held=compile_evidence_reviews(state,payload,reviewer_model="independent")
        self.assertEqual(held["entries"][0]["status"],"HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertFalse(held["entries"][0]["execution_authorized"])

    def test_execution_ready_harness_can_be_invalidated_by_later_runtime_support_evidence(self):
        plan=build_provisional_evidence_plan(machine(1));entry=plan["entries"][0]
        state=clear_review(compile_evidence_designs(plan,{"designs":[design_for(entry)]}));row=state["entries"][0]
        preflight={"receipts":[{"candidate_id":row["candidate_id"],"contract_sha256":row["contract_sha256"],"disposition":"MINIMAL_HARNESS_IMPLEMENTATION_READY","reason":"bounded adapter is implementable","inventory_summary":"pinned substrate is available","harness_plan_sha256":"e"*64,"implementation_scope":"implement frozen adapter only","budget_feasible":True}]}
        pending=compile_substrate_preflight(state,preflight);row=pending["entries"][0]
        passed=compile_harness_implementation_receipts(pending,{"receipts":[{"candidate_id":row["candidate_id"],"contract_sha256":row["contract_sha256"],"harness_manifest_sha256":"a"*64,"implementation_summary":"outcome-free runtime probe initially passed","sandboxed":True,"probe_passed":True,"budget_feasible":True}]});row=passed["entries"][0]
        self.assertTrue(row["execution_authorized"])
        invalid=compile_harness_runtime_invalidations(passed,{"receipts":[{"candidate_id":row["candidate_id"],"contract_sha256":row["contract_sha256"],"harness_manifest_sha256":"a"*64,"failure_manifest_sha256":"b"*64,"failure_class":"support/runtime","reason":"later workload probe invalidated the transport implementation","reopen_condition":"restore the original transport or pass a provider-neutral workload probe","provider_calls_charged":0,"remaining_model_call_budget":256}]});row=invalid["entries"][0]
        self.assertEqual(row["status"],"HOLD_HARNESS_RUNTIME_SUPPORT")
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["harness_runtime_invalidation"]["remaining_model_call_budget"],256)
        self.assertEqual(validate_evidence_plan(invalid),[])

    def test_harness_runtime_support_failure_is_reopenable_zero_authority_hold(self):
        plan=build_provisional_evidence_plan(machine(1));entry=plan["entries"][0]
        state=clear_review(compile_evidence_designs(plan,{"designs":[design_for(entry)]}))
        row=state["entries"][0]
        preflight={"receipts":[{"candidate_id":row["candidate_id"],"contract_sha256":row["contract_sha256"],"disposition":"MINIMAL_HARNESS_IMPLEMENTATION_READY","reason":"public substrate exists but needs a bounded adapter","inventory_summary":"pinned public code and benchmark are available","harness_plan_sha256":"e"*64,"implementation_scope":"implement only the frozen runtime adapter","budget_feasible":True}]}
        pending=compile_substrate_preflight(state,preflight);row=pending["entries"][0]
        receipt={"receipts":[{"candidate_id":row["candidate_id"],"contract_sha256":row["contract_sha256"],"implementation_status":"SUPPORT_BLOCKED","failure_manifest_sha256":"f"*64,"failure_class":"support/runtime","reason":"required web transport is unavailable in the current environment","reopen_condition":"original transport credentials or a provider-neutral adapter passes the frozen workload admissibility probe"}]}
        held=compile_harness_implementation_receipts(pending,receipt);row=held["entries"][0]
        self.assertEqual(row["status"],"HOLD_HARNESS_RUNTIME_SUPPORT")
        self.assertFalse(row["execution_authorized"])
        self.assertFalse(row["harness_implementation_failure"]["belief_authority"])
        self.assertEqual(held["summary"]["harness_runtime_hold"],1)
        self.assertEqual(validate_evidence_plan(held),[])

    def test_substrate_protocol_defect_routes_back_to_one_bounded_design_repair(self):
        plan=build_provisional_evidence_plan(machine(1));state=clear_review(compile_evidence_designs(plan,{"designs":[design_for(plan["entries"][0])]},design_model="designer"));row=state["entries"][0]
        receipt={"receipts":[{"candidate_id":row["candidate_id"],"contract_sha256":row["contract_sha256"],"disposition":"PROTOCOL_REPAIR_REQUIRED","reason":"asset audit exposed an executable-protocol contradiction without changing the frozen scientific object","inventory_summary":"public substrate exists, but the current baseline training/evaluation contract is internally inconsistent","required_revision":"freeze a disjoint calibration/evaluation split and register baseline predictions before evaluation outcomes are opened"}]}
        repaired=compile_substrate_preflight(state,receipt);entry=repaired["entries"][0]
        self.assertEqual(entry["status"],"NEEDS_BOUNDED_EVIDENCE_DESIGN");self.assertEqual(entry["design_revision_count"],1);self.assertFalse(entry["execution_authorized"]);self.assertEqual(entry["frozen_exact_prediction"],row["frozen_exact_prediction"]);self.assertEqual(entry["frozen_same_information_baseline"],row["frozen_same_information_baseline"]);self.assertEqual(validate_evidence_plan(repaired),[])

    def test_source_specific_claim_waits_for_primary_asset(self):
        plan=build_provisional_evidence_plan(machine(1))
        d=design_for(plan["entries"][0],source="SOURCE_SPECIFIC_REQUIRED",mode="PRIMARY_ASSET_REUSE",adapter="PRIMARY_ASSET_ONLY")
        state=compile_evidence_designs(plan,{"designs":[d]})
        self.assertEqual(state["entries"][0]["status"],"NEEDS_OPERATIONALIZATION_RECOMPILE")
        self.assertFalse(state["entries"][0]["execution_authorized"])

    def test_source_asset_dependency_gets_one_operationalization_recompile(self):
        plan=build_provisional_evidence_plan(machine(1));entry=plan["entries"][0]
        source=design_for(entry,source="SOURCE_SPECIFIC_REQUIRED",mode="PRIMARY_ASSET_REUSE",adapter="PRIMARY_ASSET_ONLY")
        state=compile_evidence_designs(plan,{"designs":[source]},design_model="designer")
        self.assertEqual(state["entries"][0]["status"],"NEEDS_OPERATIONALIZATION_RECOMPILE")
        recompiled=design_for(state["entries"][0]);recompiled["acquisition_mode"]="FIRST_PARTY_SANDBOX";recompiled["execution_adapter"]="EXISTING_SANDBOX_HARNESS"
        payload={"recompiles":[{"candidate_id":"C1","verdict":"RECOMPILED_FIRST_PARTY","reason":"the unavailable file identity is acquisition provenance rather than the frozen causal contrast","scientific_object_invariants":["same causal unit","same observable","same intervention contrast","same baseline information"],"source_specific_dependencies_removed":["original file identity"],"why_dependencies_are_not_scientific_object":"the frozen prediction concerns the contrast rather than the original file identity","transport_scope":"same-domain controlled first-party instantiation","equivalence_probe":"verify observables, intervention arms, and baseline inputs before the main contrast","equivalence_failure_action":"return to source-specific wait","design":recompiled}]}
        out=compile_operationalization_recompiles(state,payload,part=1,recompiler_model="recompiler")
        row=out["entries"][0]
        self.assertEqual(row["status"],"NEEDS_INDEPENDENT_EVIDENCE_REVIEW")
        self.assertEqual(row["operationalization_recompile_attempts"],1)
        self.assertEqual(row["design"]["frozen_exact_prediction"],entry["frozen_exact_prediction"])
        self.assertEqual(row["design"]["frozen_same_information_baseline"],entry["frozen_same_information_baseline"])
        reviewed=clear_review(out)
        self.assertEqual(reviewed["entries"][0]["status"],"READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT")

    def test_intrinsic_source_specific_recompile_stays_waiting(self):
        plan=build_provisional_evidence_plan(machine(1));entry=plan["entries"][0]
        state=compile_evidence_designs(plan,{"designs":[design_for(entry,source="SOURCE_SPECIFIC_REQUIRED",mode="PRIMARY_ASSET_REUSE",adapter="PRIMARY_ASSET_ONLY")]})
        payload={"recompiles":[{"candidate_id":"C1","verdict":"INTRINSIC_SOURCE_SPECIFIC","reason":"the frozen prediction explicitly depends on an original source-only variable"}]}
        out=compile_operationalization_recompiles(state,payload,recompiler_model="recompiler")
        self.assertEqual(out["entries"][0]["status"],"WAIT_PRIMARY_ASSET_RELEASE")
        self.assertEqual(out["entries"][0]["operationalization_recompile_attempts"],1)
        self.assertEqual(out["summary"]["operationalization_intrinsic_source_specific"],1)

    def test_first_party_design_requires_anti_bake_in_controls(self):
        plan=build_provisional_evidence_plan(machine(1));d=design_for(plan["entries"][0]);d["anti_bake_in_controls"]=["one"]
        state=compile_evidence_designs(plan,{"designs":[d]})
        self.assertEqual(state["entries"][0]["status"],"HOLD_EVIDENCE_DESIGN_INVALID")
        self.assertIn("first-party-needs-three-anti-bake-in-controls",state["entries"][0]["design_audit"]["errors"])

    def test_inconclusive_opens_only_frozen_single_variable_branch_repair(self):
        plan=build_provisional_evidence_plan(machine(1));state=preflight_ready(clear_review(compile_evidence_designs(plan,{"designs":[design_for(plan["entries"][0])]})))
        row=state["entries"][0]
        receipt={"receipts":[{"candidate_id":row["candidate_id"],"contract_sha256":row["contract_sha256"],"outcome":"INCONCLUSIVE","evidence_manifest_sha256":"b"*64,"protocol_valid":True,"qualified_units":24,"metric_summary":"interval overlaps both frozen predictions"}]}
        branched=adjudicate_evidence_receipts(state,receipt);entry=branched["entries"][0]
        self.assertEqual(entry["status"],"BRANCH_REPAIR_READY")
        repair=design_for(entry);repair["changed_variable"]=entry["branch_repair"]["changed_variable"]
        repaired=compile_evidence_designs(branched,{"designs":[repair]},part=2)
        self.assertEqual(repaired["entries"][0]["tree"]["depth"],1)
        self.assertEqual(repaired["entries"][0]["tree"]["repair_count"],1)
        self.assertEqual(repaired["entries"][0]["status"],"NEEDS_INDEPENDENT_EVIDENCE_REVIEW")
        reviewed_repair=clear_review(repaired)
        self.assertEqual(reviewed_repair["entries"][0]["status"],"READY_FOR_BOUNDED_SUBSTRATE_PREFLIGHT")
        self.assertEqual(preflight_ready(reviewed_repair)["entries"][0]["status"],"READY_FOR_BOUNDED_EVIDENCE_ACQUISITION")
        bad=adjudicate_evidence_receipts(state,receipt);bad_design=design_for(bad["entries"][0]);bad_design["changed_variable"]="change a different variable"
        held=compile_evidence_designs(bad,{"designs":[bad_design]},part=2)
        self.assertIn("branch-repair-changed-variable-mismatch",held["entries"][0]["design_audit"]["errors"])

    def test_completed_slot_promotes_deferred_candidate(self):
        plan=build_provisional_evidence_plan(machine(5));first=plan["entries"][0]
        state=preflight_ready(clear_review(compile_evidence_designs(plan,{"designs":[design_for(first)]})))
        row=state["entries"][0]
        receipt={"receipts":[{"candidate_id":row["candidate_id"],"contract_sha256":row["contract_sha256"],"outcome":"REDUCTION_SUPPORTED","evidence_manifest_sha256":"c"*64,"protocol_valid":True,"qualified_units":16,"metric_summary":"matched baseline explains the frozen prediction"}]}
        out=adjudicate_evidence_receipts(state,receipt)
        promoted=next(r for r in out["entries"] if r["candidate_id"]=="C5")
        self.assertTrue(promoted["design_selected"])
        self.assertEqual(promoted["status"],"NEEDS_BOUNDED_EVIDENCE_DESIGN")

    def test_residual_survival_returns_to_review_not_paper_pass(self):
        plan=build_provisional_evidence_plan(machine(1));state=preflight_ready(clear_review(compile_evidence_designs(plan,{"designs":[design_for(plan["entries"][0])]})))
        row=state["entries"][0]
        receipt={"receipts":[{"candidate_id":row["candidate_id"],"contract_sha256":row["contract_sha256"],"outcome":"RESIDUAL_SURVIVES","evidence_manifest_sha256":"a"*64,"protocol_valid":True,"qualified_units":24,"metric_summary":"matched baseline fails while residual prediction holds"}]}
        out=adjudicate_evidence_receipts(state,receipt)
        self.assertEqual(out["entries"][0]["status"],"RETURN_TO_SEMANTIC_CURRENT_SOURCE_REVIEW")
        self.assertEqual(out["summary"]["residual_survives"],1)
        self.assertEqual(out["summary"]["paper_design_authorized"],0)
        self.assertEqual(validate_evidence_plan(out),[])


if __name__ == "__main__": unittest.main()
