from __future__ import annotations

import unittest

from .research_system import build_research_system_state, validate_state


class ResearchSystemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_research_system_state()

    def test_state_is_valid_and_iclr_first(self) -> None:
        self.assertEqual(self.state["target_venue"], "ICLR")
        self.assertEqual(validate_state(self.state), [])
        self.assertEqual(self.state["summary"]["passed_ideas"], 26)
        self.assertGreaterEqual(self.state["summary"]["papers"], 200)
        self.assertEqual(self.state["summary"]["v4_candidates"], 28)
        self.assertEqual(self.state["summary"]["v4_finalists"], 16)
        self.assertEqual(self.state["summary"]["v4_revivals"], 8)
        self.assertEqual(self.state["summary"]["v5_candidates"], 36)
        self.assertEqual(self.state["summary"]["v5_finalists"], 32)
        self.assertEqual(self.state["summary"]["v5_revivals"], 8)
        self.assertEqual(self.state["summary"]["v5_external_pass"], 6)
        self.assertEqual(self.state["summary"]["v51_external_pass"], 3)
        self.assertEqual(self.state["summary"]["v52_external_pass"], 1)
        self.assertEqual(self.state["summary"]["v53_external_pass"], 3)
        self.assertEqual(self.state["summary"]["discussion_ready"], 27)
        self.assertEqual(self.state["summary"]["discussion_target"], 20)
        self.assertEqual(self.state["summary"]["final_pass"], 20)
        self.assertEqual(self.state["summary"]["final_revise"], 0)
        self.assertEqual(self.state["summary"]["final_block"], 0)
        self.assertTrue(self.state["summary"]["final_ready"])

    def test_evidence_graph_connects_papers_queries_and_ideas(self) -> None:
        graph = self.state["evidence_graph"]["summary"]
        self.assertGreater(graph["nodes"], self.state["summary"]["papers"])
        self.assertGreater(graph["edges"], self.state["summary"]["papers"])
        self.assertGreaterEqual(graph["ideas_with_semantic_evidence"], 24)
        self.assertIn("idea", graph["node_kinds"])
        self.assertIn("paper", graph["node_kinds"])

    def test_collision_engine_runs_all_pairs(self) -> None:
        collision = self.state["collision_engine"]["summary"]
        self.assertEqual(collision["ideas"], 29)
        self.assertEqual(collision["pairwise_comparisons"], 406)
        self.assertGreater(collision["flagged_pairs"], 0)

    def test_lineage_preserves_branches_and_reviews(self) -> None:
        lineage = self.state["lineage"]["summary"]
        self.assertEqual(lineage["idea_nodes"], 29)
        self.assertEqual(lineage["track_roots"], 8)
        self.assertGreaterEqual(lineage["programmatic_reviews"], 26 * 7)
        self.assertGreaterEqual(lineage["external_reviews"], 1)

    def test_pilot_registry_has_three_phases_per_passed_idea(self) -> None:
        registry = self.state["pilot_registry"]["summary"]
        self.assertEqual(registry["ideas"], 26)
        self.assertEqual(registry["phases"], 78)
        self.assertEqual(registry["invalid_result_files"], 0)
        self.assertEqual(registry["invalid_approval_files"], 0)
        self.assertEqual(registry["p0_authorized"], 0)
        self.assertEqual(registry["pre_p0_ready"], 0)
        self.assertEqual(registry["pre_experiment_ready"], 0)
        self.assertEqual(registry["invalidated_result_files"], sum(bool(item.get("invalidated")) for item in self.state["pilot_registry"].get("invalid_results", [])))
        self.assertEqual(registry["p1_authorized"], 0)
        by_id = {item["idea_id"]: item for item in self.state["pilot_registry"]["ideas"]}
        self.assertEqual(by_id["outcome-equivalent-trajectory-contrast"]["p0_gate_status"], "terminal-merge")
        self.assertEqual(by_id["workflow-generalization-certificate"]["p0_gate_status"], "ready")
        self.assertEqual(by_id["workflow-generalization-certificate"]["terminal_state"], "p0")
        self.assertEqual(by_id["update-trust-region"]["pre_p0_gate_status"], "repair-required")
        self.assertEqual(by_id["budgeted-evolution-controller"]["pre_p0_gate_status"], "repair-required")
        self.assertTrue(self.state["pilot_registry"]["policy"]["p0_execution_requires_pre_p0_pass"])
        self.assertTrue(self.state["pilot_registry"]["policy"]["automatic_p0_to_p1_forbidden"])
        self.assertTrue(self.state["pilot_registry"]["policy"]["p0_pass_requires_explicit_human_approval_before_p1"])

    def test_pre_p0_auditor_blocks_known_nonidentifiable_designs(self) -> None:
        audit = self.state["pre_p0_identifiability"]
        self.assertEqual(audit["summary"]["audited"], 4)
        self.assertEqual(audit["summary"]["execution_ready"], 0)
        by_code = {item["code"]: item for item in audit["nodes"]}
        self.assertIn("representability", by_code["A-1"]["blockers"])
        self.assertIn("target_variation", by_code["A-2"]["blockers"])
        self.assertIn("baseline_disagreement", by_code["B-1"]["blockers"])
        self.assertIn("claim_alignment", by_code["E-1"]["blockers"])

    def test_pre_experiment_compiler_is_eight_gate_and_launch_authoritative(self) -> None:
        compiler = self.state["pre_experiment_compiler"]
        self.assertEqual(len(compiler["gates"]), 8)
        self.assertEqual(compiler["summary"]["compiled_cards"], 4)
        self.assertEqual(compiler["summary"]["paper_design_pass"], 0)
        self.assertEqual(compiler["summary"]["paper_design_blocked"], 4)
        self.assertEqual(compiler["summary"]["execution_ready"], 0)
        self.assertEqual(compiler["summary"]["blocked"], 4)
        self.assertEqual(compiler["summary"]["formal_p0_ready"], 0)
        self.assertEqual(compiler["summary"]["formal_p0_total"], 2)
        self.assertEqual(compiler["summary"]["updater_prerequisite_pass"], 0)
        self.assertEqual(compiler["summary"]["updater_prerequisite_fail"], 4)
        self.assertEqual(compiler["summary"]["research_execution_plans"], 4)
        self.assertTrue(all((card.get("research_execution_plan") or {}).get("execution_authority") is False for card in compiler["cards"]))
        self.assertEqual(compiler["summary"]["gate_failures"]["mechanism_identifiability"], 4)
        self.assertEqual(compiler["summary"]["gate_failures"]["outcome_semantics"], 4)
        self.assertTrue(compiler["policy"]["paper_design_contract_required_before_principle_and_implementation"])
        self.assertTrue(compiler["policy"]["local_validation_cannot_discover_or_redefine_core_method"])
        self.assertTrue(compiler["policy"]["full_experiment_requires_frozen_method_and_experiment_blueprint"])
        self.assertTrue(compiler["policy"]["research_execution_plan_required_before_launch"])
        self.assertTrue(compiler["policy"]["research_execution_plan_is_derived_not_a_formal_gate"])
        self.assertTrue(compiler["policy"]["research_execution_plan_cannot_authorize_execution"])
        self.assertTrue(compiler["policy"]["updater_competence_required_before_gate_1"])
        self.assertTrue(compiler["policy"]["updater_competence_is_not_a_ninth_gate"])
        self.assertTrue(compiler["policy"]["automatic_override_forbidden"])
        self.assertTrue(compiler["policy"]["terminal_outcome_requires_endpoint_headroom_audit"])
        self.assertTrue(compiler["policy"]["execution_cap_censoring_must_be_typed_separately"])
        self.assertTrue(compiler["policy"]["cap_censored_branch_cannot_count_as_natural_terminal_failure"])
        self.assertTrue(self.state["pilot_registry"]["policy"]["p0_execution_requires_pre_experiment_8_of_8"])

    def test_memory_support_workflow_preserves_stage_boundaries(self) -> None:
        workflow = self.state["mem_xfer_workflow"]
        allowed = set(workflow["allowed_statuses"])
        for key in ("offline_analysis", "support_qualification", "full_support", "support_enriched_analysis", "applicability_falsifier", "mechanism_diagnosis", "second_model"):
            self.assertIn(workflow[key]["status"], allowed)
        self.assertIn(workflow["full_table"]["status"], allowed | {"collecting"})
        if workflow["full_support"].get("authorized"):
            self.assertEqual(workflow["support_qualification"]["status"], "support_qualification_pass")
        decision = workflow["support_enriched_analysis"].get("decision") or {}
        if decision.get("method_failure_authorized"):
            self.assertTrue(decision.get("formal_method_experiment_authorized"))
        if workflow["formal_method"].get("authorized"):
            self.assertEqual(workflow["support_enriched_analysis"]["status"], "support_enriched_analysis_complete")
        if workflow["second_model"].get("authorized"):
            self.assertTrue(decision.get("second_model_authorized"))
        self.assertGreater(len(workflow.get("dependencies") or []), 0)

    def test_experiment_iteration_distinguishes_pilot_failure_layers(self) -> None:
        iteration = self.state["experiment_iteration"]
        self.assertEqual(iteration["summary"]["nodes"], 4)
        self.assertEqual(iteration["summary"]["scale_up_allowed"], 0)
        by_code = {item["code"]: item for item in iteration["nodes"]}
        if iteration.get("round1_root"):
            self.assertEqual(by_code["A-1"]["diagnosis"], "representation-signal-mismatch")
            self.assertEqual(by_code["A-2"]["diagnosis"], "no-label-variation")
            self.assertEqual(by_code["B-1"]["diagnosis"], "matched-simplification-tie")
            self.assertEqual(by_code["E-1"]["diagnosis"], "objective-claim-mismatch")
            self.assertFalse(by_code["A-1"]["scientific_belief_update_allowed"])
            self.assertFalse(by_code["A-2"]["scientific_belief_update_allowed"])
            self.assertTrue(by_code["B-1"]["scientific_belief_update_allowed"])
            self.assertFalse(by_code["E-1"]["scientific_belief_update_allowed"])
        else:
            self.assertTrue(all(row["diagnosis"] == "infrastructure-error" for row in by_code.values()))
            self.assertTrue(all(not row["scientific_belief_update_allowed"] for row in by_code.values()))

    def test_repair_queue_contains_structured_blocks(self) -> None:
        queue = self.state["repair_queue"]
        self.assertEqual(queue["summary"]["queued_ideas"], 1)
        self.assertEqual({item["idea_id"] for item in queue["queue"]}, {"update-surface-router"})
        self.assertTrue(all(item["idea_id"] not in self.state["human_terminal_ideas"]["parents"] for item in queue["queue"]))
        self.assertTrue(queue["policy"]["preserve_parent_branch"])
        self.assertFalse(queue["policy"]["automatic_selection_forbidden"])
        self.assertTrue(queue["policy"]["stop_automatic_idea_iteration_at_p0"])
        self.assertFalse(queue["policy"]["terminal_human_parent_repair_forbidden"])
        self.assertTrue(queue["policy"]["absorbed_child_repair_forbidden"])

    def test_reference_components_are_explicit(self) -> None:
        sources = {item["source"] for item in self.state["components"]}
        self.assertIn("ResearchAgent", sources)
        self.assertIn("AI-Researcher", sources)
        self.assertIn("MOOSE-Chem / Deep-Ideation", sources)
        self.assertIn("AI-Scientist-v2", sources)
        self.assertTrue(any("Co-Scientist" in source for source in sources))
        self.assertTrue(any("HypoRefine" in source and "IdeaForge" in source for source in sources))
        self.assertTrue(any("FirstResearch" in source and "Popper" in source for source in sources))
        self.assertTrue(any("Qiushi" in source and "Kosmos" in source for source in sources))
        self.assertTrue(any("ResearchClawBench" in source and "HackDetect" in source for source in sources))
        self.assertIn("External-system intake registry", sources)
        self.assertIn("Biomni / BioMedAgent / PaperQA2", sources)
        self.assertIn("AutoResearchBench / PaperQA2 / SciNetBench / ScientistOne / verifier calibration", sources)
        self.assertIn("Advisor paper-first research contract", sources)
        self.assertEqual(len(self.state["components"]), 27)
        self.assertIn("Human terminal ledger", sources)
        self.assertIn("P0 retrospective economy review", sources)
        self.assertIn("Web GPT + domestic-model independent consultation", sources)
        self.assertIn("Content-addressed AI consultation automation", sources)
        self.assertIn("Unified P0 decision ledger", sources)
        self.assertIn("P0-System v2", sources)
        self.assertEqual(len(self.state["research_governance_v2"]["stages"]), 7)
        self.assertEqual(len(self.state["research_governance_v2"]["paper_first_macro_stages"]), 11)
        architecture = self.state["system_architecture"]
        self.assertEqual(architecture["summary"]["temporal_stages"], 11)
        self.assertEqual(architecture["summary"]["functional_layers"], 6)
        self.assertEqual(architecture["summary"]["assigned_components"], 27)
        self.assertEqual(architecture["summary"]["unassigned_components"], 0)
        self.assertEqual(architecture["summary"]["duplicate_component_keys"], 0)
        self.assertEqual(architecture["summary"]["cross_cutting_controls"], 3)
        self.assertEqual(architecture["summary"]["orphan_cross_cutting_controls"], 0)
        self.assertEqual(self.state["summary"]["methodology_cross_cutting_controls"], 3)
        self.assertEqual(self.state["summary"]["methodology_primary_components_added"], 0)
        self.assertEqual(len({item["key"] for item in self.state["components"]}), 27)
        self.assertTrue(all(item.get("primary_layer") for item in self.state["components"]))
        self.assertTrue(self.state["research_governance_v2"]["policy"]["paper_novelty_precedes_method_design"])
        self.assertTrue(self.state["research_governance_v2"]["policy"]["method_design_precedes_experiment_plan"])
        self.assertTrue(self.state["research_governance_v2"]["policy"]["local_validation_precedes_full_experiment"])
        self.assertTrue(self.state["research_governance_v2"]["policy"]["support_and_method_are_distinct"])
        self.assertTrue(self.state["research_governance_v2"]["policy"]["raw_trace_is_mandatory_for_gpu_runs"])
        self.assertEqual(self.state["summary"]["human_terminal_p0"], 20)
        self.assertEqual(self.state["summary"]["human_terminal_p0_ready"], 0)
        self.assertEqual(self.state["summary"]["p0_admission_active"], 27)
        self.assertEqual(self.state["summary"]["p0_admission_transitioned"], 16)
        self.assertEqual(self.state["summary"]["p0_admission_settings_complete"], 27)
        self.assertEqual(self.state["summary"]["p0_admission_economy_ready"], 0)
        self.assertEqual(self.state["summary"]["p0_economy_matched_simplification_stops"], 19)
        self.assertEqual(self.state["summary"]["p0_economy_substrate_stops"], 4)
        self.assertEqual((self.state["summary"]["p0_batch_parent_p0"],self.state["summary"]["p0_batch_reused_existing"],self.state["summary"]["p0_batch_fresh_cpu_f0"]),(20,13,7))
        self.assertEqual((self.state["summary"]["p0_batch_matched_stops"],self.state["summary"]["p0_batch_upstream_holds"],self.state["summary"]["p0_batch_gpu_candidates"]),(7,0,0))
        self.assertEqual(self.state["summary"]["p0_decision_ledger_launchable"], 0)
        self.assertEqual((self.state["summary"]["paper_first_design_reviewed"], self.state["summary"]["paper_first_design_advance_method"], self.state["summary"]["paper_first_design_revise_problem"], self.state["summary"]["paper_first_design_merge_invariant"], self.state["summary"]["paper_first_design_stop_standalone"]), (4, 1, 1, 1, 1))
        self.assertFalse(self.state["paper_first_design_adjudication"]["policy"]["local_validation_authorized"])
        self.assertEqual(self.state["summary"]["paper_first_pf1_problem_decision"], "STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT")
        self.assertFalse(self.state["summary"]["paper_first_pf1_problem_active"])
        self.assertFalse(self.state["summary"]["paper_first_pf1_method_design_authorized"])
        self.assertEqual(self.state["summary"]["paper_first_pf2_method_decision"], "STOP_CURRENT_RSIC_METHOD_THESIS_KEEP_PROBLEM_PROTOCOL")
        self.assertFalse(self.state["summary"]["paper_first_pf2_method_active"])
        self.assertFalse(self.state["summary"]["paper_first_pf2_experiment_blueprint_authorized"])
        self.assertTrue(self.state["paper_first_pf2_method_adjudication"]["same_information_stop"]["triggered"])
        self.assertEqual((self.state["summary"]["paper_first_pf357_reviewed"],self.state["summary"]["paper_first_pf357_stopped"]),(3,3))
        self.assertEqual(self.state["paper_first_pf357_problem_adjudication"]["summary"]["paper_design_authorized"],0)
        self.assertEqual(self.state["paper_first_pf357_problem_adjudication"]["summary"]["local_validation_authorized"],0)
        fresh=self.state["paper_first_fresh_saturation"]["summary"]
        self.assertEqual(self.state["summary"]["paper_first_fresh_drafts_reviewed"],fresh["drafts_reviewed"])
        self.assertEqual((fresh["survivors"],fresh["stopped"]),(0,fresh["drafts_reviewed"]))
        self.assertEqual(self.state["paper_first_fresh_saturation"]["decision"],"NO_FRESH_SURVIVOR_CURRENT_SCAN")
        self.assertTrue(self.state["paper_first_fresh_saturation"]["policy"]["zero_survivors_is_valid_and_preferred_to_forced_shortlist"])
        self.assertFalse(self.state["paper_first_fresh_saturation"]["policy"]["local_validation_authorized"])
        self.assertFalse(self.state["paper_first_fresh_saturation"]["policy"]["p0_authorized"])
        primary=self.state["paper_first_primary_evidence"]
        self.assertIn(primary["status"],{"NOT_RUN","READY","INSUFFICIENT_PRIMARY_EVIDENCE","STALE_CORPUS_BLOCKED","NO_CORPUS","STATE_UNREADABLE"})
        self.assertFalse(primary["policy"]["candidate_generation_authority"])
        self.assertFalse(primary["policy"]["method_authority"])
        self.assertFalse(primary["policy"]["experiment_authority"])
        if primary["status"]=="READY":
            self.assertTrue(primary["policy"]["primary_publication_age_is_bounded"])
            self.assertLessEqual(float(primary["policy"]["maximum_publication_age_days"]),60.0)
            self.assertTrue(primary["policy"]["fulltext_enrichment_is_optional"])
            self.assertTrue(primary["policy"]["fulltext_snippets_remain_private_data_artifacts"])
            self.assertTrue(primary["policy"]["empirical_fact_candidates_are_not_ground_truth"])
            self.assertTrue(primary["policy"]["fresh_s2_is_augmented_by_preregistered_arxiv_lanes"])
            self.assertTrue(primary["policy"]["arxiv_augmentation_failure_does_not_invalidate_fresh_corpus"])
            self.assertTrue(primary["policy"]["pre_registered_lane_coverage_floor"])
            self.assertTrue(primary["policy"]["lane_coverage_is_discovery_breadth_not_scientific_authority"])
            self.assertGreaterEqual(int(primary["policy"]["lane_floor"]),1)
            self.assertEqual(primary["summary"]["undercovered_lanes"],[])
        generator=self.state["paper_first_problem_generator"]
        self.assertIn(generator["status"],{"NOT_RUN","SKIPPED_INSUFFICIENT_PRIMARY_EVIDENCE","SKIPPED_STALE_PRIMARY_EVIDENCE","GENERATOR_ERROR_ZERO_AUTHORITY","GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE","STATE_UNREADABLE"})
        self.assertTrue(generator["policy"]["zero_candidates_is_valid"])
        self.assertTrue(generator["policy"]["semantic_reviewer_is_block_only"])
        self.assertTrue(generator["policy"]["candidate_inbox_has_zero_scientific_authority"])
        if generator["status"] in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"}:
            self.assertTrue(generator["policy"]["independent_reviewer_must_ground_both_source_claims_to_exact_primary_evidence_excerpts"])
        self.assertEqual((generator["policy"]["automatic_method_authority"],generator["policy"]["automatic_experiment_authority"],generator["policy"]["automatic_p0_authority"]),(False,False,False))
        discovery=self.state["paper_first_problem_discovery_contract"]
        self.assertTrue(discovery["policy"]["contradiction_first_required"])
        self.assertTrue(discovery["policy"]["two_primary_source_facts_required"])
        self.assertTrue(discovery["policy"]["two_mature_theory_baselines_required"])
        self.assertTrue(discovery["policy"]["same_information_nonreducibility_required"])
        self.assertTrue(discovery["policy"]["domain_transfer_veto_required"])
        self.assertEqual(discovery["summary"]["saturation_patterns"],self.state["paper_first_fresh_saturation"]["summary"]["reduction_patterns"])
        self.assertEqual((discovery["summary"]["automatic_method_authority"],discovery["summary"]["automatic_experiment_authority"]),(0,0))
        queue=self.state["paper_first_problem_gate_queue"]
        self.assertEqual((queue["summary"]["submitted"],queue["summary"]["passed_problem_gate"],queue["summary"]["blocked_problem_gate"]),(0,0,0))
        self.assertEqual((queue["summary"]["method_authorized"],queue["summary"]["experiment_authorized"],queue["summary"]["p0_authorized"]),(0,0,0))
        self.assertTrue(queue["policy"]["all_candidates_require_problem_gate"])
        self.assertTrue(queue["policy"]["verified_primary_evidence_registry_required_for_submitted_candidates"])
        self.assertTrue(queue["policy"]["independent_semantic_reduction_review_required"])
        self.assertTrue(queue["policy"]["semantic_reviewer_is_block_only"])
        self.assertTrue(queue["policy"]["problem_gate_pass_only_grants_human_paper_design_eligibility"])
        self.assertEqual(self.state["summary"]["paper_first_p0_promoted"], 0)
        self.assertEqual(self.state["summary"]["paper_first_p0_authority_status"], "NO_EXPLICIT_USER_P0_PROMOTION_AUTHORITY")
        self.assertEqual(self.state["paper_first_p0_authority"]["summary"]["promoted"], 0)
        self.assertEqual(self.state["summary"]["paper_first_p0_f0_quarantined"], 4)
        self.assertEqual((self.state["paper_first_p0_f0"]["summary"]["observed_support_pass"], self.state["paper_first_p0_f0"]["summary"]["observed_support_hold"]), (2, 2))
        self.assertEqual(self.state["paper_first_p0_f0"]["summary"]["method_fail_authorized"], 0)
        premature_method=self.state["paper_first_premature_method_diagnostics"]
        self.assertEqual((premature_method["summary"]["directions"],premature_method["summary"]["completed_diagnostics"],premature_method["summary"]["design_holds"],premature_method["summary"]["same_information_reducibility_findings"]),(2,2,1,2))
        self.assertEqual((premature_method["summary"]["scientifically_authorized"],premature_method["summary"]["p0_lifecycle_mutations"],premature_method["summary"]["full_experiment_authorized"]),(0,0,0))
        self.assertTrue(premature_method["authority"]["cannot_retroactively_authorize"])
        pmd_by={row["incubation_id"]:row for row in premature_method["cards"]}
        self.assertEqual(pmd_by["PF-1"]["v2_observed_method_diagnostic"]["decision"],"STOP_MATCHED_POST_ONLY_EQUIVALENT")
        self.assertEqual(pmd_by["PF-1"]["v2_observed_method_diagnostic"]["selected_proposed"],"c2")
        self.assertEqual(pmd_by["PF-1"]["v2_observed_method_diagnostic"]["selected_same_information_post_only"],"c2")
        self.assertFalse(pmd_by["PF-1"]["v2_observed_method_diagnostic"]["hidden_executed"])
        self.assertEqual(pmd_by["PF-4"]["observed_method_diagnostic"]["decision"],"STOP_MATCHED_SOFT_SCALAR_EQUIVALENT")
        self.assertFalse(pmd_by["PF-4"]["observed_method_diagnostic"]["fresh_gpu_authorized"])
        authority_assets=[row for row in self.state["failure_asset_library"]["assets"] if row.get("diagnosis")=="authority-provenance-mismatch"]
        self.assertEqual(len(authority_assets), 1)
        self.assertFalse(authority_assets[0]["can_authorize_p0"])
        self.assertFalse(authority_assets[0]["can_authorize_method_or_principle"])
        self.assertEqual(self.state["summary"]["ai_consultation_checkpoints"], 5)
        self.assertEqual(self.state["summary"]["ai_consultation_pre_gpu_checkpoints"], 3)
        self.assertFalse(self.state["ai_consultation_clinic"]["policy"]["ai_vote_can_authorize_gpu"])
        self.assertTrue(self.state["ai_consultation_automation"]["policy"]["content_addressed_triggers"])
        self.assertTrue(self.state["ai_consultation_automation"]["policy"]["ai_output_never_authorizes_execution"])
        self.assertEqual(self.state["p0_offline_qualification"]["summary"]["ideas"], 16)
        self.assertEqual(self.state["p0_realizability"]["summary"]["audited"], 14)
        self.assertEqual(self.state["p0_realizability"]["summary"]["synthetic_pass"], 14)
        self.assertEqual(self.state["summary"]["p0_b10_decision"], "STOP_MATCHED_NARY_EQUIVALENT")
        self.assertEqual(self.state["summary"]["p0_a3_decision"], "STOP_CURRENT_SUBSTRATE_UPDATER_INCOMPETENT")
        self.assertEqual(self.state["summary"]["p0_a4_decision"], "STOP_DIRECT_ORDER_AWARE_RISK_EQUIVALENT")
        self.assertEqual(self.state["summary"]["p0_a5_decision"], "STOP_MATCHED_GENERIC_STATE_DIFF_DOMINATES")
        self.assertEqual(self.state["summary"]["p0_a6_decision"], "STOP_MATCHED_GROUP_TESTING_EQUIVALENT")
        self.assertEqual(self.state["summary"]["p0_a7_decision"], "STOP_MATCHED_SHALLOW_RULE_EQUIVALENT")
        self.assertEqual(self.state["summary"]["p0_b2_decision"], "STOP_CURRENT_SUBSTRATE_CONCLUSION_CHANGE_SUPPORT_INSUFFICIENT")
        self.assertEqual(self.state["summary"]["p0_b3_screening_decision"], "SCREENING_SIGNAL_REAL_COINTERACTION_REQUIRED")
        self.assertEqual(self.state["summary"]["p0_b3_support_decision"], "STOP_CURRENT_SUBSTRATE_FRESH_CINTERACTION_SUPPORT_INSUFFICIENT")
        self.assertIsNone(self.state["summary"]["p0_b3_real_decision"])
        self.assertEqual(self.state["summary"]["p0_b5_decision"], "STOP_COMPLEXITY_MATCHED_ILP_EQUIVALENT")
        self.assertEqual(self.state["summary"]["p0_b6_decision"], "STOP_RECENCY_FREQUENCY_POLICY_DOMINATES")
        self.assertEqual(self.state["summary"]["p0_c2_decision"], "STOP_SIMPLE_ANCHOR_RESIDUAL_CALIBRATION_EQUIVALENT")
        self.assertEqual(self.state["summary"]["p0_d1_decision"], "STOP_MATCHED_INTERSECTION_FILTER_EQUIVALENT")
        self.assertEqual(self.state["summary"]["p0_e1_decision"], "STOP_CURRENT_EDIT_TABLE_RANKING_DEGENERATE")
        self.assertEqual(self.state["summary"]["p0_e2_decision"], "STOP_MATCHED_E1_DIRECT_EDIT_EQUIVALENT")
        self.assertEqual(self.state["summary"]["p0_e3_decision"], "STOP_STATEFUL_DETERMINISTIC_PEX_CEILING")
        self.assertEqual(self.state["summary"]["p0_e4_decision"], "STOP_MATCHED_BOOLEAN_RULE_EQUIVALENT")
        self.assertTrue(self.state["p0_offline_qualification"]["policy"]["method_result_from_offline_qualification_forbidden"])
        self.assertEqual(self.state["summary"]["discussion_ready"], 27)
        self.assertEqual(self.state["summary"]["discussion_target"], 20)
        self.assertTrue(self.state["summary"]["final_ready"])
        disabled = [item for item in self.state["components"] if item["status"] == "intentionally-disabled"]
        self.assertEqual(len(disabled), 1)


if __name__ == "__main__":
    unittest.main()
