from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_search_portfolio_design_adjudication import (
    _continuation_hold_rows,
    _fresh_phenomenon_support_hold_rows,
    _principle_readjudication_rows,
    _shadow_dead_end_memory,
    _terminal_evidence_hold_rows,
    _terminal_support_hold_rows,
    build_search_portfolio_design_adjudication,
    merge_shadow_terminal_run_memory,
    validate_search_portfolio_design_adjudication,
)


class SearchPortfolioPaperDesignAdjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_search_portfolio_design_adjudication()

    def test_continuation_holds_preserve_failure_layer_without_dead_end_authority(self) -> None:
        root=Path(__file__).resolve().parents[1]/"generated"
        paths=[root/"auto1-formulation-continuation-hold-20260818.json",root/"lopd-fixed-budget-continuation-hold-20260818.json"]
        rows=_continuation_hold_rows(paths)
        self.assertEqual(len(rows),2)
        by_id={row["source_candidate_id"]:row for row in rows}
        auto=by_id["AUTO-1-AGENT-SAFETY-20260818T060955Z"]
        self.assertEqual((auto["memory_class"],auto["stop_class"],auto["failure_layer"]),("FORMULATION_HOLD","PROTOCOL_STOP","assumption_scope"))
        self.assertTrue(auto["basin"].startswith("semantic-lane-contract-"))
        self.assertFalse(auto["dead_end_certified"]);self.assertFalse(auto["scientific_authority"])
        lopd=by_id["LOPD-FIXED-BUDGET-LATENT-EXPERIENCE-DECOMPOSITION"]
        self.assertEqual((lopd["memory_class"],lopd["stop_class"],lopd["failure_layer"]),("REOPENABLE_HOLD","SUPPORT_STOP","experiment_identifiability"))
        self.assertEqual(lopd["support_status"],"SOURCE_SPECIFIC_PRIMARY_ASSET_UNAVAILABLE")
        self.assertTrue(lopd["basin"].startswith("near-miss-terminal-support-hold-"))
        self.assertFalse(lopd["dead_end_certified"]);self.assertFalse(lopd["scientific_authority"])

    def test_continuation_holds_enter_hold_memory_and_never_blocked_memory(self) -> None:
        memory=self.state["shadow_search_memory"]
        dead=self.state["shadow_dead_end_memory"]
        blocked={row.get("source_candidate_id") for row in memory.get("closed_objects") or []}
        held={row.get("source_candidate_id"):row for row in memory.get("hold_objects") or []}
        auto_id="AUTO-1-AGENT-SAFETY-20260818T060955Z";lopd_id="LOPD-FIXED-BUDGET-LATENT-EXPERIENCE-DECOMPOSITION"
        self.assertNotIn(auto_id,blocked);self.assertNotIn(lopd_id,blocked)
        self.assertEqual(dead.get("hold_objects"),[])
        self.assertNotIn(auto_id,{row.get("source_candidate_id") for row in dead.get("blocked_objects") or []})
        self.assertNotIn(lopd_id,{row.get("source_candidate_id") for row in dead.get("blocked_objects") or []})
        self.assertEqual(held[auto_id]["memory_class"],"FORMULATION_HOLD")
        self.assertEqual(held[lopd_id]["memory_class"],"REOPENABLE_HOLD")
        self.assertFalse(held[auto_id]["dead_end_certified"]);self.assertFalse(held[lopd_id]["dead_end_certified"])

    def test_exact_fresh_support_hold_is_reopenable_not_dead_end(self) -> None:
        path=Path(__file__).resolve().parents[1]/"generated"/"harnessbank-fresh-phenomenon-support-hold-20260817.json"
        rows=_fresh_phenomenon_support_hold_rows([path])
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertEqual(row["disposition"],"HOLD_SUPPORT_UNAVAILABLE")
        self.assertEqual(row["memory_class"],"REOPENABLE_HOLD")
        self.assertFalse(row["dead_end_certified"])
        self.assertFalse(row["scientific_authority"])
        hold=row["fresh_phenomenon_hold"]
        self.assertEqual(hold["source_ref"],"arXiv:2607.13683")
        self.assertEqual(hold["evidence_sha256"],"03bd345821be718b2b342e2348ab18c44a91146219bdde5db2d909336cb8ce52")
        self.assertFalse(hold["scientific_authority"])

    def test_evodrc_feasibility_credit_is_in_persistent_principle_memory(self) -> None:
        memory=self.state["shadow_search_memory"]
        hits=[row for row in memory.get("closed_objects") or [] if row.get("source_candidate_id")=="EVODRC-FEASIBILITY-CREDIT"]
        self.assertEqual(len(hits),1)
        row=hits[0]
        self.assertEqual(row["memory_class"],"METHOD_REALIZATION_STOP")
        self.assertEqual(row["failure_layer"],"method_realization")
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertTrue(row["search_closure_certified"]);self.assertFalse(row["dead_end_certified"]);self.assertFalse(row["scientific_authority"])
        self.assertEqual(row["search_primitive"],"UNEXPLAINED_BOUNDARY")
        self.assertEqual(row["source_readjudication_artifact"],"generated/evodrc-feasibility-credit-principle-readjudication-20260817.json")
        self.assertTrue(row.get("reopen_only_if"))
        self.assertEqual(row.get("current_source_refs"),["arXiv:2607.20019"])

    def test_static_procedural_cross_regime_contradiction_is_in_persistent_principle_memory(self) -> None:
        memory=self.state["shadow_search_memory"]
        hits=[row for row in memory.get("closed_objects") or [] if row.get("source_candidate_id")=="AUTO-1-STATIC-PROCEDURAL-PRIOR-CROSS-REGIME"]
        self.assertEqual(len(hits),1)
        row=hits[0]
        self.assertEqual(row["memory_class"],"ASSUMPTION_SCOPE_STOP")
        self.assertEqual(row["failure_layer"],"assumption_scope")
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertTrue(row["search_closure_certified"]);self.assertFalse(row["dead_end_certified"]);self.assertFalse(row["scientific_authority"])
        self.assertEqual(row["search_primitive"],"CONTRADICTION")
        self.assertEqual(row["current_source_refs"],["arXiv:2607.01874","arXiv:2607.05297"])
        self.assertEqual(row["source_readjudication_artifact"],"generated/static-procedural-prior-cross-regime-contradiction-principle-readjudication-20260817.json")
        counter=row.get("counter_explanation") or {}
        self.assertEqual(counter.get("type"),"NECESSARY_ASSUMPTION_REFUTED")
        self.assertEqual(counter.get("necessary_assumption_id"),"shared-static-procedural-artifact-treatment")
        self.assertTrue(counter.get("assumption_refuted"))
        self.assertIn("identical static-procedural-artifact intervention",row["reopen_only_if"])

    def test_pa05_skill_validation_transfer_is_in_persistent_principle_memory(self) -> None:
        memory=self.state["shadow_search_memory"]
        hits=[row for row in memory.get("closed_objects") or [] if row.get("source_candidate_id")=="PA-05-SKILL-VALIDATION-TRANSFER"]
        self.assertEqual(len(hits),1)
        row=hits[0]
        self.assertEqual(row["memory_class"],"METHOD_REALIZATION_STOP")
        self.assertEqual(row["failure_layer"],"method_realization")
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertTrue(row["search_closure_certified"]);self.assertFalse(row["dead_end_certified"]);self.assertFalse(row["scientific_authority"])
        self.assertEqual(row["search_primitive"],"UNEXPLAINED_BOUNDARY")
        self.assertEqual(row["source_readjudication_artifact"],"generated/skill-validation-transfer-distribution-shift-principle-readjudication-20260817.json")
        self.assertTrue(row.get("reopen_only_if"))
        counter=row.get("counter_explanation") or {}
        self.assertTrue(counter.get("same_information_reduction_verified"))
        witness=counter.get("exact_reduction_witness") or {}
        self.assertEqual(witness.get("witness_type"),"ALGEBRAIC_REPARAMETERIZATION")
        self.assertFalse(witness.get("requires_experiment_outcome"))
        closure=row.get("fresh_phenomenon_closure") or {}
        self.assertEqual(closure.get("source_ref"),"arXiv:2605.24117")
        self.assertEqual(closure.get("closed_evidence_sha256"),[
            "2892e337780746e547a748c947b379b3c55af09eea1d273ace383b80d2e569ee",
            "7756cb19d009b410df23a289a331e74719d0f372c5d4be84d3ec13a974a68a8c",
            "daaad83e507806a66c1c4dd5911c40b8db5781df4cd22b8f44916e228d4e224c",
        ])
        self.assertFalse(closure.get("scientific_authority"))

    def test_aborted_auto1_relevant_skill_misexecution_is_scoped_principle_dead_end(self) -> None:
        memory=self.state["shadow_search_memory"]
        hits=[row for row in memory.get("closed_objects") or [] if row.get("source_candidate_id")=="AUTO-1-RELEVANT-SKILL-MISEXECUTION"]
        self.assertEqual(len(hits),1)
        row=hits[0]
        self.assertEqual(row["memory_class"],"METHOD_REALIZATION_STOP")
        self.assertEqual(row["failure_layer"],"method_realization")
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertTrue(row["search_closure_certified"]);self.assertFalse(row["dead_end_certified"]);self.assertFalse(row["scientific_authority"])
        self.assertEqual(row["search_primitive"],"CONVERGENT_FAILURE")
        self.assertEqual(row["source_readjudication_artifact"],"generated/auto1-relevant-skill-misexecution-principle-readjudication-20260817.json")
        self.assertEqual(row["current_source_refs"],["arXiv:2608.11888","arXiv:2608.14036"])
        self.assertIn("task-artifact alignment",row["strongest_reduction"])
        self.assertIn("oracle-load",row["reopen_only_if"])
        self.assertEqual(row.get("fresh_phenomenon_closure"),{})

    def test_shadow_counterfactual_survivors_are_conservatively_routed(self) -> None:
        self.assertEqual(validate_search_portfolio_design_adjudication(self.state), [])
        summary = self.state["summary"]
        self.assertEqual(
            (summary["reviewed"], summary["advance_to_method_design"], summary["revise_paper_problem"], summary["stop_standalone"]),
            (2, 0, 1, 1),
        )
        rows = {row["id"]: row for row in self.state["rows"]}
        self.assertEqual(rows["SP-09"]["verdict"], "STOP_STANDALONE_COLLISION_KEEP_CONTEXT_RISK_AXIS")
        self.assertEqual(rows["SP-15"]["verdict"], "REVISE_PAPER_PROBLEM_SUPPORT_INVENTORY_REQUIRED")
        self.assertIn("point-identifiable", rows["SP-15"]["revised_problem"])

    def test_current_closed_basins_are_typed_by_actual_failure_layer(self) -> None:
        memory = self.state["shadow_search_memory"]
        self.assertEqual(memory["closed_basin_count"], 42)
        self.assertEqual(memory["closure_layer_counts"], {
            "problem_novelty": 5,
            "execution": 0,
            "experiment_identifiability": 2,
            "optimization": 0,
            "operationalization": 3,
            "method_realization": 28,
            "assumption_scope": 2,
            "core_principle": 2,
        })
        self.assertEqual(memory["failure_layer_counts"], {
            "execution": 0,
            "experiment_identifiability": 2,
            "optimization": 0,
            "operationalization": 3,
            "method_realization": 28,
            "assumption_scope": 2,
            "core_principle": 2,
        })
        self.assertEqual(memory["principle_dead_end_count"], 2)
        self.assertEqual(memory["core_principle_stop_count"], 2)
        self.assertEqual(memory["broader_core_principle_falsification_count"], 0)
        self.assertEqual(memory["core_principle_dead_end_count"], 2)
        self.assertEqual(len(memory["hold_objects"]), 9)
        self.assertTrue(all(row.get("dead_end_certified") is False for row in memory["hold_objects"]))
        pace = next(row for row in memory["closed_objects"] if row.get("source_candidate_id") == "PA-06-PACE-MECHANISM-REDESIGN-IDENTIFIABILITY")
        self.assertEqual(pace["failure_layer"], "core_principle")
        self.assertEqual(pace["memory_class"], "CORE_PRINCIPLE_STOP")
        self.assertTrue(pace["principle_update_allowed"])
        self.assertFalse(pace["broader_core_principle_falsified"])
        pa01 = next(row for row in memory["closed_objects"] if row.get("source_candidate_id") == "PA-01-EVIDENCE-ECHO")
        self.assertEqual(pa01["memory_class"], "METHOD_REALIZATION_STOP")
        self.assertTrue(pa01["experiment_run_for_this_readjudication"])
        self.assertFalse(pa01["experiment_alone_authorizes_closure"])
        port010 = next(row for row in memory["closed_objects"] if row.get("source_candidate_id") == "PORT-010")
        self.assertEqual(port010["failure_layer"], "core_principle")
        self.assertEqual(port010["memory_class"], "CORE_PRINCIPLE_STOP")
        self.assertTrue(port010["principle_update_allowed"])
        self.assertTrue(port010["dead_end_certified"])
        self.assertFalse(port010["broader_core_principle_falsified"])
        self.assertFalse(port010["experiment_alone_authorizes_closure"])
        self.assertIn("framing", port010["counter_explanation"]["statement"].lower())
        sp09 = next(row for row in memory["closed_objects"] if row.get("source_candidate_id") == "SP-09")
        self.assertEqual(sp09["memory_class"], "PROBLEM_NOVELTY_STOP")
        p04 = next(row for row in memory["closed_objects"] if row.get("source_candidate_id") == "SHADOW-P04-C01")
        self.assertEqual(p04["memory_class"], "PROBLEM_NOVELTY_STOP")
        self.assertEqual(p04["failure_layer"], None)
        self.assertFalse(p04["principle_update_allowed"])
        self.assertFalse(p04["dead_end_certified"])
        self.assertEqual(p04["current_source_refs"], ["arXiv:2608.05810"])

    def test_shadow_counterfactual_pass_does_not_leak_downstream_authority(self) -> None:
        self.assertTrue(self.state["policy"]["source_is_shadow_search_portfolio"])
        self.assertTrue(self.state["policy"]["shadow_queue_has_zero_paper_design_authority"])
        self.assertTrue(self.state["policy"]["cannot_grant_or_revoke_live_paper_design_authority"])
        for row in self.state["rows"]:
            self.assertTrue(row["historical_counterfactual_problem_gate_pass"])
            self.assertFalse(row["live_paper_design_eligible"])
            self.assertTrue(row["counterfactual_problem_gate_pass_does_not_grant_live_paper_design"])
            for key in ("method_design_authorized", "experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized"):
                self.assertFalse(row[key])
        for key in ("method_design_authorized", "experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized"):
            self.assertEqual(self.state["summary"][key], 0)

    def test_search_closure_memory_and_scientific_dead_end_memory_are_separate(self) -> None:
        memory = self.state["shadow_search_memory"]
        dead = self.state["shadow_dead_end_memory"]
        self.assertFalse(memory["scientific_authority"])
        self.assertFalse(memory["live_source_coverage_effect"])
        self.assertTrue(memory["cannot_mutate_canonical_generator_or_queue"])
        self.assertTrue(memory["search_control_only"])
        self.assertNotIn("blocked_objects", memory)
        self.assertIn("SP-09", {row["source_candidate_id"] for row in memory["closed_objects"]})
        self.assertNotIn("SP-15", {row["source_candidate_id"] for row in memory["closed_objects"]})
        self.assertIn("SP-15", {row["source_candidate_id"] for row in memory["hold_objects"]})
        sp15=next(row for row in memory["hold_objects"] if row["source_candidate_id"]=="SP-15")
        self.assertEqual((sp15["memory_class"],sp15["stop_class"],sp15["failure_layer"],sp15["failure_subtype"]),("REOPENABLE_HOLD","SUPPORT_STOP","experiment_identifiability","NO_MATCHED_QUERY_IDENTIFIABILITY_UNIT"))
        self.assertFalse(sp15["dead_end_certified"]); self.assertFalse(sp15["principle_dead_end_certified"]); self.assertFalse(sp15["principle_update_allowed"])
        self.assertTrue(all(row["search_closure_certified"] is True and row.get("counter_explanation") for row in memory["closed_objects"]))
        self.assertEqual(sum(row.get("dead_end_certified") is True for row in memory["closed_objects"]), 2)
        self.assertFalse(dead["scientific_authority"])
        self.assertEqual(dead["persistent_dead_end_authority_scope"], "core_principle-only")
        self.assertTrue(dead["only_principle_stop_may_enter_persistent_dead_end_memory"])
        self.assertEqual(dead.get("hold_objects"), [])
        self.assertEqual([row.get("source_candidate_id") for row in dead.get("blocked_objects") or []], ["PA-06-PACE-MECHANISM-REDESIGN-IDENTIFIABILITY", "PORT-010"])
        self.assertTrue(all(row.get("failure_layer")=="core_principle" and row.get("dead_end_certified") is True for row in dead.get("blocked_objects") or []))
        self.assertEqual(memory.get("inversion_asset_evidence_count"),len(memory.get("inversion_asset_evidence") or []))
        self.assertEqual(memory.get("inversion_asset_search_active_count"),0)
        p01_assets=[row for row in memory.get("inversion_asset_evidence") or [] if str(row.get("asset_ref") or "").startswith("first-party-asset:double-ratchet@")]
        self.assertEqual(len(p01_assets),1)
        self.assertEqual(p01_assets[0]["source_sha256"],"2e996c0b543c03a1f6c68cb06aaa26498d52b36f0775b7b36cf2025783f68ab0")
        self.assertFalse(p01_assets[0]["scientific_authority"])
        autoskill_assets=[row for row in memory.get("inversion_asset_evidence") or [] if str(row.get("asset_ref") or "").startswith("first-party-asset:autoskill@")]
        self.assertEqual(len(autoskill_assets),1)
        self.assertEqual(autoskill_assets[0]["source_sha256"],"0d7553874390685344102cd9654a376a1f1e3e7d7490fa53b48f1f138f3f383b")
        self.assertFalse(autoskill_assets[0]["search_active"])
        self.assertEqual(autoskill_assets[0]["search_closed_by_sha256"],"502ecfdcbfc0aaa364d5ac013fa13735490d42035e4af8fa9762864e335aee10")
        self.assertFalse(autoskill_assets[0]["scientific_authority"])
        self.assertEqual(memory.get("positive_residual_asset_evidence_count"),len(memory.get("positive_residual_asset_evidence") or []))
        positive=[row for row in memory.get("positive_residual_asset_evidence") or [] if str(row.get("asset_ref") or "").startswith("positive-residual-asset:memory-effect-transport-b9-c2")]
        self.assertEqual(len(positive),1)
        self.assertEqual(positive[0]["phenomenon_status"],"SURVIVES_AS_ARCHIVED_PARENT_EVIDENCE")
        self.assertEqual(positive[0]["mechanism_status"],"NO_ACTIVE_MECHANISM_AFTER_LOCAL_TEMPORAL_AND_TREATMENT_SEMANTICS_REDUCTIONS")
        self.assertFalse(positive[0]["search_active"])
        self.assertEqual(memory.get("positive_residual_search_active_count"),0)
        self.assertTrue((positive[0].get("search_contract") or {}).get("prospective_prediction_required"))
        self.assertTrue((positive[0].get("search_contract") or {}).get("temporal_exposure_standalone_branch_closed"))
        self.assertTrue((positive[0].get("search_contract") or {}).get("treatment_semantics_standalone_branch_closed"))
        temporal=[row for row in memory.get("closed_objects") or [] if row.get("source_candidate_id")=="POSITIVE-RESIDUAL-MEMORY-TEMPORAL-EXPOSURE"]
        semantics=[row for row in memory.get("closed_objects") or [] if row.get("source_candidate_id")=="POSITIVE-RESIDUAL-MEMORY-TREATMENT-SEMANTICS"]
        self.assertEqual(len(temporal),1)
        self.assertEqual(len(semantics),1)
        self.assertEqual((temporal[0].get("counter_explanation") or {}).get("opposite_principle"),"Persistent context is a repeated intervention, not a new causal primitive.")
        self.assertIn("part of treatment identity",(semantics[0].get("counter_explanation") or {}).get("opposite_principle",""))
        self.assertTrue((positive[0].get("search_contract") or {}).get("pre_outcome_information_only"))
        self.assertFalse(positive[0]["scientific_authority"])

    def test_principle_readjudication_compiles_into_opposite_search_memory(self) -> None:
        phenomenon_sha="a"*64
        payload={"candidate_id":"P06","title":"Coverage quantity","principle_dead_end_certified":True,"dead_end_scope":"coverage-only certificate","fresh_phenomenon_closure":{"source_ref":"arXiv:2608.07527","closed_evidence_sha256":[phenomenon_sha],"closure_scope":"coverage-count boundary only","scientific_authority":False},"principle_diagnosis":{"counter_explanation":{"type":"IMPOSSIBILITY_OR_INVARIANCE","statement":"coverage quantity does not identify relevance","opposite_prediction":"generic uncertainty shift only","opposite_principle":"evidence sufficiency is relevance-conditioned","opposite_search_seed":"search relevance-conditioned evidence debt","scope":"coverage-only certificate","same_information_or_scope_matched":True,"proof_or_structural_witness":True,"evidence_refs":["arXiv:2608.07527"],"alternative_explanations_ruled_out":["execution"],"reopen_condition":"expose relevance-conditioned debt without hidden truth"}}}
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"p06-principle-readjudication-test.json";p.write_text(json.dumps(payload),encoding="utf-8")
            rows=_principle_readjudication_rows([p])
        self.assertEqual(len(rows),1)
        memory=_shadow_dead_end_memory({"latest_run":{"candidates":[]}},prior_hard_veto_rows=[],prior_semantic_rows=[],prior_near_miss_rows=[],principle_readjudication_rows=rows)
        matches=[row for row in memory["blocked_objects"] if str(row.get("basin") or "").startswith("principle-readjudication-")]
        self.assertEqual(len(matches),1)
        self.assertEqual(matches[0]["counter_explanation"]["opposite_search_seed"],"search relevance-conditioned evidence debt")
        self.assertFalse(matches[0]["scientific_authority"])
        self.assertEqual(matches[0]["fresh_phenomenon_closure"]["closed_evidence_sha256"],[phenomenon_sha])
        self.assertEqual(memory["principle_readjudication_closed_basin_count"],1)
        self.assertEqual(memory["principle_readjudication_dead_end_count"],0)
        self.assertEqual(memory["fresh_phenomenon_closure_count"],1)
        self.assertEqual(memory["fresh_phenomenon_closed_evidence_count"],1)

    def test_principle_closure_supersedes_same_candidate_support_hold(self) -> None:
        phenomenon_sha="a"*64
        payload={"candidate_id":"PA-03-HARNESS-SELECTION-INVERSION","title":"Harness selection inversion","principle_dead_end_certified":True,"dead_end_scope":"aggregate ranking inversion only","fresh_phenomenon_closure":{"source_ref":"arXiv:2607.13683","closed_evidence_sha256":[phenomenon_sha],"closure_scope":"aggregate ranking inversion only","scientific_authority":False},"principle_diagnosis":{"counter_explanation":{"type":"SAME_INFORMATION_REDUCTION","statement":"ordinary adaptive selection explains the current aggregate inversion","opposite_prediction":"noisy selected maxima may regress on fresh data","opposite_principle":"post-selection inference precedes a harness-specific mechanism","opposite_search_seed":"search only for a lineage-level residual","scope":"aggregate ranking inversion only","same_information_or_scope_matched":True,"same_information_reduction_verified":True,"positive_support":True,"evidence_refs":["arXiv:2607.13683"],"alternative_explanations_ruled_out":["execution noise"],"reopen_condition":"release paired lineage and beat a selection-aware baseline"}}}
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"harness-principle-readjudication-test.json";p.write_text(json.dumps(payload),encoding="utf-8")
            rows=_principle_readjudication_rows([p])
        support_hold={"source_candidate_id":"PA-03-HARNESS-SELECTION-INVERSION","basin":"fresh-phenomenon-support-hold-demo","disposition":"HOLD_SUPPORT_UNAVAILABLE","memory_class":"REOPENABLE_HOLD","dead_end_certified":False,"strongest_reduction":"support unavailable; no scientific reduction authorized","current_source_refs":["arXiv:2607.13683"],"evidence_basis":["arXiv:2607.13683"],"reason":"lineage unavailable","reopen_only_if":"release lineage","required_unit":"paired lineage","fresh_phenomenon_hold":{"source_ref":"arXiv:2607.13683","evidence_sha256":phenomenon_sha,"scientific_authority":False},"scientific_authority":False}
        memory=_shadow_dead_end_memory({"latest_run":{"candidates":[]}},prior_hard_veto_rows=[],prior_semantic_rows=[],prior_near_miss_rows=[],principle_readjudication_rows=rows,fresh_phenomenon_support_hold_rows=[support_hold])
        blocked=[row for row in memory["blocked_objects"] if row.get("source_candidate_id")=="PA-03-HARNESS-SELECTION-INVERSION"]
        holds=[row for row in memory["hold_objects"] if row.get("source_candidate_id")=="PA-03-HARNESS-SELECTION-INVERSION"]
        self.assertEqual(len(blocked),1)
        self.assertEqual(blocked[0]["memory_class"],"METHOD_REALIZATION_STOP")
        self.assertEqual(blocked[0]["failure_layer"],"method_realization")
        self.assertFalse(blocked[0]["broader_core_principle_falsified"])
        self.assertEqual(holds,[])

    def test_r2_near_miss_preflight_compiles_into_future_shadow_search_memory(self) -> None:
        memory=self.state["shadow_search_memory"]
        rows=[row for row in list(memory["closed_objects"])+list(memory["hold_objects"]) if str(row.get("basin") or "").startswith("near-miss-")]
        by_candidate={}
        for row in rows:
            by_candidate.setdefault(row["source_candidate_id"],[]).append(row)
        self.assertEqual(memory["near_miss_base_preflight_count"],4)
        self.assertEqual(memory["near_miss_preflight_count"],3)
        self.assertGreaterEqual(memory["near_miss_hold_count"],1)
        self.assertEqual(self.state["summary"]["near_miss_support_holds"],1)
        self.assertEqual(self.state["summary"]["near_miss_current_primary_stops"],2)
        self.assertEqual(self.state["summary"]["near_miss_mature_theory_stops"],1)
        expected={
            "SHADOW-P03-C01":"HOLD_SUPPORT_UNAVAILABLE",
            "SHADOW-P09-C01":"STOP_CURRENT_PRIMARY_COLLISION",
            "SHADOW-P05-C01":"STOP_MATURE_THEORY_REDUCTION",
            "SHADOW-P12-C02":"STOP_CURRENT_PRIMARY_COLLISION",
        }
        for cid,disposition in expected.items():
            matches=[row for row in by_candidate.get(cid,[]) if row.get("disposition")==disposition]
            self.assertTrue(matches,f"missing persistent near-miss receipt {cid}:{disposition}")
            self.assertTrue(all(row["scientific_authority"] is False for row in matches))
            if disposition == "HOLD_SUPPORT_UNAVAILABLE":
                self.assertTrue(all(row["dead_end_certified"] is False for row in matches))
            else:
                self.assertTrue(all(row["search_closure_certified"] is True and row["dead_end_certified"] is False and row.get("counter_explanation") for row in matches))

    def test_current_source_hard_veto_compiles_into_future_shadow_search_memory(self) -> None:
        memory=_shadow_dead_end_memory({"latest_run":{"candidates":[{"candidate_id":"SHADOW-X","title":"Retrieval attribution gap","search_primitive":"IDENTIFIABILITY_GAP","current_source_status":"complete","current_source_verdict":"BLOCK","current_source_reduction_class":"VALID_HARD_VETO","current_source_strongest_reduction":"generic identifiability over an omitted compiled-context variable","current_source_reason":"Current primary work already exposes retrieval and compilation as separate pipeline objects.","current_source_source_refs":["arXiv:2605.10114","arXiv:2608.05604"]}]}},prior_hard_veto_rows=[])
        dynamic=[row for row in memory["blocked_objects"] if row["source_candidate_id"]=="SHADOW-X"]
        self.assertEqual(len(dynamic),1)
        self.assertEqual(memory["current_source_hard_veto_count"],1)
        self.assertEqual(dynamic[0]["search_primitive"],"IDENTIFIABILITY_GAP")
        self.assertIn("omitted compiled-context variable",dynamic[0]["strongest_reduction"])
        self.assertEqual(dynamic[0]["current_source_refs"],["arXiv:2605.10114","arXiv:2608.05604"])
        self.assertFalse(dynamic[0]["scientific_authority"])
        self.assertIn("same-information",dynamic[0]["reopen_only_if"])

    def test_current_source_hard_veto_persists_when_latest_run_has_no_clear_candidate(self) -> None:
        prior={"source_candidate_id":"SHADOW-OLD","basin":"current-source-hard-veto-deadbeefdeadbeef","search_primitive":"IDENTIFIABILITY_GAP","avoid":["old basin"],"strongest_reduction":"generic identifiability over explicit compiled context","current_source_refs":["arXiv:2605.10114"],"reason":"older current-source review blocked it","reopen_only_if":"new same-information residual survives explicit instrumentation","scientific_authority":False}
        memory=_shadow_dead_end_memory({"latest_run":{"candidates":[]}},prior_hard_veto_rows=[prior])
        rows=[row for row in memory["blocked_objects"] if row.get("basin")==prior["basin"]]
        self.assertEqual(len(rows),1)
        self.assertEqual(memory["current_source_hard_veto_count"],1)
        self.assertEqual(memory["current_source_hard_veto_added_from_latest_run"],0)
        self.assertEqual(memory["current_source_hard_veto_inherited"],1)
        self.assertFalse(rows[0]["scientific_authority"])

    def test_terminal_support_hold_compiles_as_reopenable_zero_authority_near_miss(self) -> None:
        rows=_terminal_support_hold_rows({"rows":[{"candidate_id":"SHADOW-HOLD","title":"Unsupported residual","disposition":"HOLD_SUPPORT_UNAVAILABLE","required_unit":"matched released trajectory units","asset_audit":"The current author release does not expose the matched units.","primary_refs":["arXiv:2608.00001"],"reopen_only_if":"The authors release matched trajectory units."}]},run_id="shadow-race",stage_manifest_sha256="a"*64)
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertTrue(row["basin"].startswith("near-miss-terminal-support-hold-"))
        self.assertEqual(row["source_run_id"],"shadow-race")
        self.assertEqual(row["source_stage_manifest_sha256"],"a"*64)
        self.assertEqual(row["disposition"],"HOLD_SUPPORT_UNAVAILABLE")
        self.assertFalse(row["scientific_authority"])
        self.assertIn("release",row["reopen_only_if"].lower())

    def test_terminal_evidence_wait_primary_asset_is_reopenable_hold_not_dead_end(self) -> None:
        plan={"entries":[{"candidate_id":"LOPD-X","title":"Latent token cliff","status":"WAIT_PRIMARY_ASSET_RELEASE","source_refs":["arXiv:2608.13040"],"frozen_falsifier_expression":"replay K={8,16,32,64,128} with source-faithful compressor checkpoints","review_feedback":"Training code and compressor checkpoints required by the frozen comparison are not released."}]}
        rows=_terminal_evidence_hold_rows(plan,run_id="shadow-v10",stage_manifest_sha256="c"*64)
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertEqual(row["memory_class"],"REOPENABLE_HOLD")
        self.assertFalse(row["dead_end_certified"])
        self.assertEqual(row["support_status"],"SOURCE_SPECIFIC_PRIMARY_ASSET_UNAVAILABLE")
        self.assertEqual(row["evidence_basis"],["arXiv:2608.13040"])
        self.assertEqual(row["hold_origin"],"bounded-evidence-acquisition")
        self.assertIn("become available",row["reopen_only_if"])

    def test_non_latest_terminal_run_memory_ingestion_is_idempotent(self) -> None:
        terminal={"run_id":"shadow-parallel-r4b","status":"SHADOW_TERMINAL_COMPLETE","generated_at":"2026-08-14T04:55:40+00:00","stage_manifest_sha256":"b"*64,"scientific_authority":False,"policy":{"shadow_only":True,"canonical_primary_generator_queue_untouched":True},"candidates":[{"candidate_id":"SHADOW-P09-C01","title":"Attribution-conditioned revision routing","search_primitive":"COMPOSITION_INTERACTION","current_source_status":"complete","current_source_verdict":"BLOCK","current_source_reduction_class":"VALID_HARD_VETO","current_source_strongest_reduction":"target-specific revision plus executable validation is already an explicit repair mechanism","current_source_reason":"Current primary work already maps diagnosis to target-specific revision and validation.","current_source_source_refs":["arXiv:2607.27733","arXiv:2606.09071"]}]}
        preflight={"rows":[{"candidate_id":"SHADOW-P04-C01","title":"Confidence-calibrated aggregation","disposition":"HOLD_SUPPORT_UNAVAILABLE","required_unit":"matched candidate answer and confidence sets","asset_audit":"The current primary release does not expose candidate-level confidence traces.","primary_refs":["arXiv:2607.27994"],"reopen_only_if":"The author release exposes candidate-level answers and confidence traces."}]}
        baseline_terminal_holds=int(self.state["summary"].get("near_miss_terminal_support_holds") or 0)
        first=merge_shadow_terminal_run_memory(self.state,terminal,preflight)
        self.assertEqual(validate_search_portfolio_design_adjudication(first),[])
        memory=first["shadow_search_memory"]
        hard=[row for row in memory["closed_objects"] if row.get("source_run_id")=="shadow-parallel-r4b" and str(row.get("basin") or "").startswith("current-source-hard-veto-")]
        holds=[row for row in memory["hold_objects"] if row.get("source_run_id")=="shadow-parallel-r4b" and str(row.get("basin") or "").startswith("near-miss-terminal-support-hold-")]
        self.assertEqual((len(hard),len(holds)),(1,1))
        self.assertEqual(first["summary"]["current_source_hard_veto_added_from_latest_run"],0)
        self.assertEqual(first["summary"]["current_source_hard_veto_added_from_terminal_run"],1)
        self.assertEqual(first["summary"]["near_miss_terminal_support_holds"],baseline_terminal_holds+1)
        self.assertEqual(first["shadow_memory_maintenance"]["last_ingested_run_id"],"shadow-parallel-r4b")
        second=merge_shadow_terminal_run_memory(first,terminal,preflight)
        self.assertEqual(validate_search_portfolio_design_adjudication(second),[])
        self.assertEqual(second["summary"]["shadow_dead_end_objects"],first["summary"]["shadow_dead_end_objects"])
        self.assertEqual(len(second["shadow_memory_maintenance"]["receipts"]),len(first["shadow_memory_maintenance"]["receipts"]))
        self.assertEqual(second["shadow_memory_maintenance"]["receipts"][-1]["hard_veto_added"],0)
        self.assertEqual(second["shadow_memory_maintenance"]["receipts"][-1]["support_hold_added"],0)

    def test_semantic_exact_reduction_block_compiles_without_hardening_soft_collision(self) -> None:
        exact={"candidate_id":"R3-X","title":"layer sign inversion","search_primitive":"UNEXPLAINED_BOUNDARY","semantic_verdict":"BLOCK","semantic_reduction_class":"NEEDS_EXACT_REDUCTION_TEST","semantic_lane_contract_verified":True,"semantic_matched_patterns":["persistent-update-vs-test-time-compute"],"semantic_strongest_reduction":"generic test-time scaling","semantic_exact_reduction_test":"match candidate quality and diversity","semantic_reason":"same-information reduction remains unresolved","semantic_lane_contract_reason":"lane valid","semantic_source_refs":["arXiv:2608.11350"],"semantic_source_claims":["harness improves while raw VLA voting hurts"],"semantic_problem_text":"layer sign inversion under tied budget"}
        soft={"candidate_id":"R3-SOFT","title":"soft only","search_primitive":"UNEXPLAINED_BOUNDARY","semantic_verdict":"BLOCK","semantic_reduction_class":"SOFT_COLLISION","semantic_lane_contract_verified":True,"semantic_strongest_reduction":"generic portfolio diversity","semantic_reason":"soft collision only","semantic_lane_contract_reason":"lane valid","semantic_source_refs":["arXiv:2608.11350"]}
        memory=_shadow_dead_end_memory({"latest_run":{"frozen_pool_sha256":"a"*64,"candidates":[exact,soft]}},prior_hard_veto_rows=[],prior_semantic_rows=[])
        self.assertFalse([row for row in memory["blocked_objects"] if str(row.get("basin") or "").startswith("semantic-")])
        rows=[row for row in memory["hold_objects"] if str(row.get("basin") or "").startswith("semantic-")]
        self.assertEqual(len(rows),1)
        self.assertTrue(rows[0]["basin"].startswith("semantic-exact-reduction-"))
        self.assertEqual(rows[0]["matched_patterns"],["persistent-update-vs-test-time-compute"])
        self.assertIn("match candidate quality",rows[0]["exact_reduction_test"])
        self.assertEqual(rows[0]["evidence_claims"],["harness improves while raw VLA voting hurts"])
        self.assertEqual(rows[0]["problem_text"],"layer sign inversion under tied budget")
        self.assertEqual(rows[0]["frozen_pool_sha256"],"a"*64)
        self.assertEqual(memory["semantic_blocker_count"],0)
        self.assertEqual(memory["semantic_hold_count"],1)
        self.assertEqual(memory["semantic_hold_added_from_latest_run"],1)
        self.assertFalse(rows[0]["dead_end_certified"])
        self.assertFalse(rows[0]["scientific_authority"])

    def test_lane_contract_failure_precedes_exact_reduction_classification(self) -> None:
        candidate={"candidate_id":"R2-LANE","title":"planner executor granularity mismatch","search_primitive":"COMPOSITION_INTERACTION","semantic_verdict":"BLOCK","semantic_reduction_class":"NEEDS_EXACT_REDUCTION_TEST","semantic_lane_contract_verified":False,"semantic_matched_patterns":[],"semantic_strongest_reduction":"generic subgoal distribution shift","semantic_exact_reduction_test":"none","semantic_reason":"lane contract fails before reduction is identified","semantic_lane_contract_reason":"fixed granularity contract is not grounded by the supplied evidence","semantic_source_refs":["arXiv:2608.05999"]}
        memory=_shadow_dead_end_memory({"latest_run":{"frozen_pool_sha256":"a"*64,"candidates":[candidate]}},prior_hard_veto_rows=[],prior_semantic_rows=[])
        self.assertFalse([row for row in memory["blocked_objects"] if str(row.get("basin") or "").startswith("semantic-")])
        rows=[row for row in memory["hold_objects"] if str(row.get("basin") or "").startswith("semantic-")]
        self.assertEqual(len(rows),1)
        self.assertTrue(rows[0]["basin"].startswith("semantic-lane-contract-"))
        self.assertFalse(rows[0]["basin"].startswith("semantic-exact-reduction-"))
        self.assertIn("fixed granularity contract",rows[0]["lane_contract_reason"])

    def test_semantic_lane_contract_block_persists_across_shadow_runs(self) -> None:
        candidate={"candidate_id":"R3-LANE","title":"optimizer threshold","search_primitive":"CONVERGENT_FAILURE","semantic_verdict":"BLOCK","semantic_reduction_class":"SOFT_COLLISION","semantic_lane_contract_verified":False,"semantic_matched_patterns":["model-scaffold-enactability"],"semantic_strongest_reduction":"cross-model instruction compatibility","semantic_exact_reduction_test":"hold budget fixed","semantic_reason":"lane contract fails","semantic_lane_contract_reason":"no shared bounded operational condition","semantic_source_refs":["arXiv:2608.09629","arXiv:2608.11340"]}
        first=_shadow_dead_end_memory({"latest_run":{"candidates":[candidate]}},prior_hard_veto_rows=[],prior_semantic_rows=[])
        row=next(row for row in first["hold_objects"] if str(row.get("basin") or "").startswith("semantic-lane-contract-"))
        self.assertIn("shared bounded operational condition",row["lane_contract_reason"])
        second=_shadow_dead_end_memory({"latest_run":{"candidates":[]}},prior_hard_veto_rows=[],prior_semantic_rows=[row])
        rows=[x for x in second["hold_objects"] if x.get("basin")==row["basin"]]
        self.assertEqual(len(rows),1)
        self.assertEqual(second["semantic_blocker_count"],0)
        self.assertEqual(second["semantic_hold_count"],1)
        self.assertEqual(second["semantic_hold_added_from_latest_run"],0)
        self.assertEqual(second["semantic_hold_inherited"],1)
        self.assertFalse(rows[0]["dead_end_certified"])

    def test_missing_domestic_reviewers_are_recorded_as_missing_not_pass(self) -> None:
        consultation = self.state["advisory_consultation"]
        self.assertFalse(consultation["scientific_authority"])
        self.assertTrue(consultation["failed_or_missing_review_is_not_pass"])
        self.assertTrue(all("missing:" in row["SP-09"] and "missing:" in row["SP-15"] for row in consultation["reviewers"]))

    def test_sp09_has_direct_governance_and_context_collisions(self) -> None:
        row = next(row for row in self.state["rows"] if row["id"] == "SP-09")
        refs = {source["ref"] for source in row["primary_sources"]}
        self.assertTrue({"arXiv:2602.12430", "arXiv:2607.01136", "arXiv:2608.09732", "arXiv:2605.30723"}.issubset(refs))
        self.assertIn("contextual constrained policy", row["cheapest_problem_falsifier"])

    def test_sp15_revision_requires_identifiability_support_before_method(self) -> None:
        row = next(row for row in self.state["rows"] if row["id"] == "SP-15")
        refs = {source["ref"] for source in row["primary_sources"]}
        self.assertTrue({"arXiv:2608.08640", "arXiv:2606.18051", "arXiv:2606.10388", "arXiv:2606.03565"}.issubset(refs))
        self.assertGreaterEqual(len(row["required_problem_revision"]), 6)
        self.assertIn("oracle ranker", " ".join(row["required_problem_revision"]))
        self.assertEqual(self.state["summary"]["support_inventory_required"], 1)


if __name__ == "__main__":
    unittest.main()
