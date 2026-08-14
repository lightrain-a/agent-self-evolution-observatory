from __future__ import annotations

import unittest

from .paper_first_evidence_acquisition import (
    adjudicate_evidence_receipts,
    build_provisional_evidence_plan,
    compile_evidence_designs,
    compile_evidence_reviews,
    compile_substrate_preflight,
    validate_evidence_plan,
)


def machine(rows=2):
    q=[]
    for i in range(rows):
        q.append({
            "candidate_id":f"C{i+1}","title":f"candidate {i+1}","discovery_lane":"UNEXPLAINED_BOUNDARY",
            "source_branch_id":f"B{i+1}","blockers":["reduction-falsifiability-contract-incomplete","unresolved-exact-reduction-test:1"],
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
    checks={"independent_truth_valid":True,"scientific_object_preserved":True,"no_mechanism_bake_in":True,"same_information_baseline_valid":True,"falsifier_not_method_evaluation":True,"outcome_semantics_valid":True,"bounded_budget_valid":True,"prior_support_constraint_respected":True}
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
        checks={"independent_truth_valid":True,"scientific_object_preserved":True,"no_mechanism_bake_in":False,"same_information_baseline_valid":True,"falsifier_not_method_evaluation":True,"outcome_semantics_valid":True,"bounded_budget_valid":True,"prior_support_constraint_respected":True}
        payload={"reviews":[{"candidate_id":"C1","verdict":"BLOCK_BAKE_IN","checks":checks,"reason":"synthetic truth encodes the target mechanism","required_revision":""}]}
        with self.assertRaisesRegex(ValueError,"reviewer must be independent"):
            compile_evidence_reviews(state,payload,reviewer_model="designer")
        held=compile_evidence_reviews(state,payload,reviewer_model="independent")
        self.assertEqual(held["entries"][0]["status"],"HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertFalse(held["entries"][0]["execution_authorized"])

    def test_source_specific_claim_waits_for_primary_asset(self):
        plan=build_provisional_evidence_plan(machine(1))
        d=design_for(plan["entries"][0],source="SOURCE_SPECIFIC_REQUIRED",mode="PRIMARY_ASSET_REUSE",adapter="PRIMARY_ASSET_ONLY")
        state=compile_evidence_designs(plan,{"designs":[d]})
        self.assertEqual(state["entries"][0]["status"],"WAIT_PRIMARY_ASSET_RELEASE")
        self.assertFalse(state["entries"][0]["execution_authorized"])

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
