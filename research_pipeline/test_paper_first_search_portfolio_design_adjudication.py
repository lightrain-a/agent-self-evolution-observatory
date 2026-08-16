from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_search_portfolio_design_adjudication import (
    _principle_readjudication_rows,
    _shadow_dead_end_memory,
    _terminal_support_hold_rows,
    build_search_portfolio_design_adjudication,
    merge_shadow_terminal_run_memory,
    validate_search_portfolio_design_adjudication,
)


class SearchPortfolioPaperDesignAdjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_search_portfolio_design_adjudication()

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

    def test_shadow_dead_end_memory_cannot_touch_live_discovery(self) -> None:
        memory = self.state["shadow_dead_end_memory"]
        self.assertFalse(memory["scientific_authority"])
        self.assertFalse(memory["live_source_coverage_effect"])
        self.assertTrue(memory["cannot_mutate_canonical_generator_or_queue"])
        self.assertIn("SP-09", {row["source_candidate_id"] for row in memory["blocked_objects"]})
        self.assertNotIn("SP-15", {row["source_candidate_id"] for row in memory["blocked_objects"]})
        self.assertIn("SP-15", {row["source_candidate_id"] for row in memory["hold_objects"]})
        self.assertTrue(all(row["dead_end_certified"] is True and row.get("counter_explanation") for row in memory["blocked_objects"]))

    def test_principle_readjudication_compiles_into_opposite_search_memory(self) -> None:
        payload={"candidate_id":"P06","title":"Coverage quantity","principle_dead_end_certified":True,"dead_end_scope":"coverage-only certificate","principle_diagnosis":{"counter_explanation":{"type":"IMPOSSIBILITY_OR_INVARIANCE","statement":"coverage quantity does not identify relevance","opposite_prediction":"generic uncertainty shift only","opposite_principle":"evidence sufficiency is relevance-conditioned","opposite_search_seed":"search relevance-conditioned evidence debt","scope":"coverage-only certificate","same_information_or_scope_matched":True,"proof_or_structural_witness":True,"evidence_refs":["arXiv:2608.07527"],"alternative_explanations_ruled_out":["execution"],"reopen_condition":"expose relevance-conditioned debt without hidden truth"}}}
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"p06-principle-readjudication-test.json";p.write_text(json.dumps(payload),encoding="utf-8")
            rows=_principle_readjudication_rows([p])
        self.assertEqual(len(rows),1)
        memory=_shadow_dead_end_memory({"latest_run":{"candidates":[]}},prior_hard_veto_rows=[],prior_semantic_rows=[],prior_near_miss_rows=[],principle_readjudication_rows=rows)
        matches=[row for row in memory["blocked_objects"] if str(row.get("basin") or "").startswith("principle-readjudication-")]
        self.assertEqual(len(matches),1)
        self.assertEqual(matches[0]["counter_explanation"]["opposite_search_seed"],"search relevance-conditioned evidence debt")
        self.assertFalse(matches[0]["scientific_authority"])
        self.assertEqual(memory["principle_readjudication_dead_end_count"],1)

    def test_r2_near_miss_preflight_compiles_into_future_shadow_search_memory(self) -> None:
        memory=self.state["shadow_dead_end_memory"]
        rows=[row for row in list(memory["blocked_objects"])+list(memory["hold_objects"]) if str(row.get("basin") or "").startswith("near-miss-")]
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
                self.assertTrue(all(row["dead_end_certified"] is True and row.get("counter_explanation") for row in matches))

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

    def test_non_latest_terminal_run_memory_ingestion_is_idempotent(self) -> None:
        terminal={"run_id":"shadow-parallel-r4b","status":"SHADOW_TERMINAL_COMPLETE","generated_at":"2026-08-14T04:55:40+00:00","stage_manifest_sha256":"b"*64,"scientific_authority":False,"policy":{"shadow_only":True,"canonical_primary_generator_queue_untouched":True},"candidates":[{"candidate_id":"SHADOW-P09-C01","title":"Attribution-conditioned revision routing","search_primitive":"COMPOSITION_INTERACTION","current_source_status":"complete","current_source_verdict":"BLOCK","current_source_reduction_class":"VALID_HARD_VETO","current_source_strongest_reduction":"target-specific revision plus executable validation is already an explicit repair mechanism","current_source_reason":"Current primary work already maps diagnosis to target-specific revision and validation.","current_source_source_refs":["arXiv:2607.27733","arXiv:2606.09071"]}]}
        preflight={"rows":[{"candidate_id":"SHADOW-P04-C01","title":"Confidence-calibrated aggregation","disposition":"HOLD_SUPPORT_UNAVAILABLE","required_unit":"matched candidate answer and confidence sets","asset_audit":"The current primary release does not expose candidate-level confidence traces.","primary_refs":["arXiv:2607.27994"],"reopen_only_if":"The author release exposes candidate-level answers and confidence traces."}]}
        baseline_terminal_holds=int(self.state["summary"].get("near_miss_terminal_support_holds") or 0)
        first=merge_shadow_terminal_run_memory(self.state,terminal,preflight)
        self.assertEqual(validate_search_portfolio_design_adjudication(first),[])
        memory=first["shadow_dead_end_memory"]
        hard=[row for row in memory["blocked_objects"] if row.get("source_run_id")=="shadow-parallel-r4b" and str(row.get("basin") or "").startswith("current-source-hard-veto-")]
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
