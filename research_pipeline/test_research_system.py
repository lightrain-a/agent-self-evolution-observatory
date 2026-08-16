from __future__ import annotations

import copy
import json
import unittest

from .paper_first_relation_coverage import relation_recall_freshness
from .paper_first_discovery_frontier import build_paper_first_discovery_frontier
from .research_system import build_research_system_state, validate_state


class ResearchSystemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_research_system_state()

    def sync_discovery_frontier(self, state: dict) -> dict:
        state["paper_first_discovery_frontier"] = build_paper_first_discovery_frontier(
            primary_state=state.get("paper_first_primary_evidence") or {},
            generator_state=state.get("paper_first_problem_generator") or {},
            queue_state=state.get("paper_first_problem_gate_queue") or {},
            relation_freshness_state=state.get("paper_first_global_relation_freshness") or {},
            relation_admission_state=state.get("paper_first_global_relation_scan_admission") or {},
            shadow_admission_state=state.get("paper_first_shadow_search_admission") or {},
            object_candidate_state=state.get("paper_first_scientific_object_candidate_evidence") or {},
            support_release_watch_state=state.get("paper_first_support_release_watch") or {},
            support_asset_recheck_state=state.get("paper_first_support_asset_recheck_queue") or {},
            shadow_portfolio_state=state.get("paper_first_problem_search_portfolio") or {},
            evidence_migration_state=state.get("paper_first_evidence_migration") or {},
        )
        return state

    def sync_relation_freshness(self, state: dict) -> dict:
        state["paper_first_global_relation_freshness"] = relation_recall_freshness(
            state.get("paper_first_problem_generator") or {},
            state.get("paper_first_global_relation_recall") or {},
        )
        return self.sync_discovery_frontier(state)

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
            self.assertTrue(primary["policy"]["typed_evidence_candidates_are_not_ground_truth"])
            self.assertTrue(primary["policy"]["typed_evidence_is_deterministic_and_bounded"])
            self.assertEqual(primary["policy"]["typed_evidence_extraction_version"],"typed-v1")
            self.assertTrue(primary["policy"]["derived_typed_evidence_reused_only_when_extractor_version_matches"])
            self.assertEqual(set((primary["summary"].get("typed_evidence_candidates") or {}).keys()),{"operational_assumptions","measured_failures","boundary_observations"})
            self.assertTrue(primary["policy"]["empirical_fact_precision_gate"])
            self.assertEqual(primary["policy"]["empirical_fact_extraction_version"],"precision-v2")
            self.assertTrue(primary["policy"]["derived_empirical_facts_reused_only_when_extractor_version_matches"])
            self.assertEqual(sum((primary["summary"].get("empirical_fact_tier_counts") or {}).values()),primary["summary"]["empirical_fact_candidates"])
            self.assertTrue(primary["policy"]["fresh_s2_is_augmented_by_preregistered_arxiv_lanes"])
            self.assertTrue(primary["policy"]["arxiv_augmentation_failure_does_not_invalidate_fresh_corpus"])
            self.assertTrue(primary["policy"]["pre_registered_lane_coverage_floor"])
            self.assertTrue(primary["policy"]["lane_coverage_is_discovery_breadth_not_scientific_authority"])
            self.assertTrue(primary["policy"]["source_coverage_scheduler_is_discovery_only"])
            self.assertTrue(primary["policy"]["source_review_exposure_has_zero_scientific_authority"])
            self.assertTrue(primary["policy"]["portable_source_review_receipts_have_zero_scientific_authority"])
            self.assertTrue(primary["policy"]["private_saturation_ledger_runs_exported_as_zero_authority_portable_receipts"])
            self.assertTrue(primary["policy"]["source_exposure_cannot_skip_generation_or_problem_gate"])
            self.assertTrue(primary["policy"]["source_exposure_does_not_relax_relevance_or_freshness"])
            self.assertTrue(primary["policy"]["source_coverage_exploration_prefers_preregistered_lanes"])
            self.assertTrue(primary["policy"]["source_coverage_saturation_is_compute_control_not_scientific_negative"])
            self.assertTrue(primary["policy"]["new_lane_grounded_source_reopens_generation"])
            self.assertGreaterEqual(int(primary["policy"]["source_coverage_anchor_count"]),1)
            self.assertEqual(int(primary["summary"]["selected_previously_reviewed"])+int(primary["summary"]["selected_unreviewed"]),int(primary["summary"]["selected"]))
            if int(primary["summary"].get("saturation_ledger_runs") or 0)>0 and int(primary["summary"]["selected"])>int(primary["summary"].get("coverage_anchor_count") or 0):
                self.assertTrue(primary["summary"]["source_coverage_scheduler_active"])
            self.assertGreaterEqual(int(primary["policy"]["lane_floor"]),1)
            self.assertEqual(primary["summary"]["undercovered_lanes"],[])
        generator=self.state["paper_first_problem_generator"]
        self.assertIn(generator["status"],{"NOT_RUN","SKIPPED_INSUFFICIENT_PRIMARY_EVIDENCE","SKIPPED_STALE_PRIMARY_EVIDENCE","SKIPPED_SOURCE_COVERAGE_SATURATED","SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE","SKIPPED_SOURCE_CARRIER_PROBE_PENDING","GENERATOR_ERROR_ZERO_AUTHORITY","GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE","STATE_UNREADABLE"})
        self.assertTrue(generator["policy"]["zero_candidates_is_valid"])
        self.assertTrue(generator["policy"]["semantic_reviewer_is_block_only"])
        self.assertTrue(generator["policy"]["candidate_inbox_has_zero_scientific_authority"])
        self.assertTrue(generator["policy"]["generation_notes_are_advisory_not_scientific_authority"])
        self.assertTrue(generator["policy"]["zero_candidate_rationale_required"])
        self.assertTrue(generator["policy"]["discovery_saturation_memory_has_zero_scientific_authority"])
        self.assertFalse((generator.get("saturation_memory") or {}).get("scientific_authority"))
        if generator["status"]=="GENERATED_ZERO_CANDIDATES": self.assertTrue(str(generator.get("generation_notes") or "").strip())
        self.assertTrue(generator["policy"]["multi_lane_discovery_enabled"])
        self.assertEqual(generator["policy"]["allowed_discovery_lanes"],["CONTRADICTION","CONVERGENT_FAILURE","ASSUMPTION_BREAK","UNEXPLAINED_BOUNDARY"])
        self.assertEqual(generator["policy"]["forbidden_discovery_lanes"],["MISSING_CELL","SHARED_LIMITATION","PURE_TOPIC_BRAINSTORM"])
        self.assertIsNot(generator["policy"].get("search_portfolio_enabled"),True)
        self.assertTrue(generator["policy"].get("one_generator_call_max",True))
        self.assertTrue(generator["policy"].get("one_semantic_reviewer_call_max",True))
        self.assertTrue(generator["policy"]["independent_reviewer_must_verify_lane_contract"])
        self.assertTrue(generator["policy"]["source_coverage_saturation_skips_model_call"])
        self.assertTrue(generator["policy"]["source_coverage_saturation_is_compute_control_not_scientific_negative"])
        self.assertTrue(generator["policy"]["new_lane_grounded_primary_source_reopens_generation"])
        self.assertTrue(generator["policy"]["portable_review_receipts_are_scheduler_metadata_only"])
        self.assertTrue(generator["policy"]["portable_review_receipts_have_zero_scientific_authority"])
        self.assertTrue(generator["policy"]["primary_source_coverage_receipts_are_inherited_transactionally"])
        receipts=(generator.get("saturation_memory") or {}).get("portable_review_receipts") or []
        self.assertTrue(all(row.get("scientific_authority") is False for row in receipts))
        if primary.get("summary",{}).get("source_coverage_exhausted"):
            portable_refs={str(ref) for row in receipts for ref in row.get("source_refs") or [] if str(ref).startswith("arXiv:")}
            self.assertGreaterEqual(len(portable_refs),int(primary["summary"].get("prior_reviewed_sources") or 0))
        if generator["status"]=="SKIPPED_SOURCE_COVERAGE_SATURATED":
            self.assertTrue((generator.get("source_coverage") or {}).get("coverage_exhausted"))
            self.assertEqual(int((generator.get("source_coverage") or {}).get("unreviewed_lane_linked_sources") or 0),0)
        if generator["status"] in {"GENERATED_ZERO_CANDIDATES","GENERATED_AWAIT_PROBLEM_GATE"}:
            self.assertTrue(generator["policy"]["independent_reviewer_must_ground_both_source_claims_to_exact_primary_evidence_excerpts"])
        self.assertEqual((generator["policy"]["automatic_method_authority"],generator["policy"]["automatic_experiment_authority"],generator["policy"]["automatic_p0_authority"]),(False,False,False))
        discovery=self.state["paper_first_problem_discovery_contract"]
        self.assertTrue(discovery["policy"]["multi_lane_discovery_required"])
        self.assertFalse(discovery["policy"]["contradiction_first_required"])
        self.assertTrue(discovery["policy"]["contradiction_lane_retained"])
        self.assertEqual(discovery["policy"]["allowed_discovery_lanes"],["CONTRADICTION","CONVERGENT_FAILURE","ASSUMPTION_BREAK","UNEXPLAINED_BOUNDARY"])
        self.assertEqual(discovery["policy"]["search_portfolio_primitives"],["CONTRADICTION","CONVERGENT_FAILURE","ASSUMPTION_BREAK","UNEXPLAINED_BOUNDARY","IDENTIFIABILITY_GAP","MISSING_DECISION_OBJECT","COMPOSITION_INTERACTION","CROSS_DOMAIN_STRUCTURAL_ANALOGY","NEW_CAPABILITY_QUESTION","LONGITUDINAL_EMERGENCE"])
        self.assertTrue(discovery["policy"]["search_portfolio_is_shadow_only"])
        self.assertTrue(discovery["policy"]["search_portfolio_cannot_publish_canonical_generator_or_queue"])
        self.assertTrue(discovery["policy"]["one_content_addressed_pool_allows_at_most_one_live_generator_call"])
        self.assertTrue(discovery["policy"]["one_content_addressed_pool_allows_at_most_one_live_generator_call_per_discovery_operator"])
        self.assertTrue(discovery["policy"]["source_coverage_saturation_reopens_once_on_operator_change"])
        self.assertTrue(discovery["policy"]["single_source_anomaly_first_search_enabled"])
        self.assertTrue(discovery["policy"]["principle_dead_end_inversion_search_enabled"])
        self.assertTrue(discovery["policy"]["dead_end_inversion_requires_certified_counter_explanation"])
        self.assertTrue(discovery["policy"]["dead_end_inversion_is_search_prior_not_scientific_authority"])
        self.assertTrue(discovery["policy"]["dead_end_inversion_requires_fresh_primary_grounding"])
        self.assertTrue(discovery["policy"]["dead_end_inversion_must_satisfy_recorded_reopen_condition"])
        self.assertTrue(discovery["policy"]["first_party_inversion_asset_grounding_enabled"])
        self.assertTrue(discovery["policy"]["first_party_inversion_asset_requires_provenance_manifest"])
        self.assertTrue(discovery["policy"]["first_party_inversion_asset_is_zero_authority_search_evidence"])
        self.assertTrue(discovery["policy"]["first_party_inversion_asset_requires_one_direct_seed_per_shard"])
        self.assertTrue(discovery["policy"]["observed_dependency_graph_is_not_an_identifiability_gap"])
        self.assertTrue(discovery["policy"]["reciprocal_coupling_claim_requires_downstream_residual_beyond_distribution_shift"])
        self.assertTrue(discovery["policy"]["feedback_mechanism_requires_causal_write_path_before_experiment"])
        self.assertEqual(discovery["policy"]["discovery_operator_version"],"anomaly-first-temporal-residual-v7")
        self.assertTrue(discovery["policy"]["positive_residual_search_enabled"])
        self.assertTrue(discovery["policy"]["positive_residual_requires_prospective_pre_outcome_prediction"])
        self.assertTrue(discovery["policy"]["positive_residual_outcome_leakage_forbidden"])
        self.assertEqual(discovery["policy"]["forbidden_discovery_lanes"],["MISSING_CELL","SHARED_LIMITATION","PURE_TOPIC_BRAINSTORM"])
        self.assertTrue(discovery["policy"]["lane_specific_machine_evidence_contract_required"])
        self.assertTrue(discovery["policy"]["no_lane_specific_downstream_relaxation"])
        self.assertTrue(discovery["policy"]["two_mature_theory_baselines_required"])
        self.assertTrue(discovery["policy"]["same_information_nonreducibility_required"])
        self.assertTrue(discovery["policy"]["domain_transfer_veto_required"])
        self.assertEqual(discovery["summary"]["saturation_patterns"],self.state["paper_first_fresh_saturation"]["summary"]["reduction_patterns"])
        self.assertEqual((discovery["summary"]["automatic_method_authority"],discovery["summary"]["automatic_experiment_authority"]),(0,0))
        queue=self.state["paper_first_problem_gate_queue"]; qs=queue["summary"]
        self.assertEqual(qs["audited"],qs["submitted"])
        self.assertEqual(qs["passed_problem_gate"]+qs["blocked_problem_gate"],qs["submitted"])
        self.assertEqual(qs["paper_design_eligible"],qs["passed_problem_gate"])
        self.assertEqual(sum((qs.get("submitted_by_lane") or {}).values()),qs["submitted"])
        self.assertEqual(sum((qs.get("passed_by_lane") or {}).values()),qs["passed_problem_gate"])
        self.assertEqual(sum((qs.get("blocked_by_lane") or {}).values()),qs["blocked_problem_gate"])
        self.assertEqual((qs["method_authorized"],qs["experiment_authorized"],qs["p0_authorized"]),(0,0,0))
        self.assertTrue(queue["policy"]["all_candidates_require_problem_gate"])
        self.assertTrue(queue["policy"]["verified_primary_evidence_registry_required_for_submitted_candidates"])
        self.assertTrue(queue["policy"]["multi_lane_candidate_schema_required"])
        self.assertTrue(queue["policy"]["lane_contract_independent_review_required"])
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

    def test_asset_first_stri_quality_ready_is_separate_from_canonical_problem_gate(self) -> None:
        stri=self.state["asset_first_stri_paper_ready"]
        self.assertEqual(stri["status"],"READY_NARROW_ICLR")
        self.assertEqual((stri.get("summary") or {}).get("paper_ready"),1)
        self.assertEqual(((stri.get("summary") or {}).get("claims_supported"),(stri.get("summary") or {}).get("claims_total")),(3,3))
        self.assertEqual((stri.get("summary") or {}).get("qa_checks_passed"),(stri.get("summary") or {}).get("qa_checks_total"))
        self.assertEqual(stri.get("submission_status"),"READY_TO_SUBMIT_PENDING_HUMAN_AUTHOR_SIGNOFF_AND_OPENREVIEW")
        self.assertEqual((stri.get("summary") or {}).get("official_qa_checks_passed"),(stri.get("summary") or {}).get("official_qa_checks_total"))
        self.assertEqual(((stri.get("summary") or {}).get("main_text_pages"),(stri.get("summary") or {}).get("main_text_page_limit")),(9,9))
        self.assertEqual((stri.get("summary") or {}).get("supplement_ready"),1)
        self.assertEqual((stri.get("summary") or {}).get("human_signoff_pending"),1)
        self.assertEqual((stri.get("summary") or {}).get("new_gpu_evidence_required"),0)
        self.assertEqual((stri.get("summary") or {}).get("paper_quality_v2_passed"),1)
        self.assertEqual((stri.get("summary") or {}).get("paper_quality_source_binding"),1)
        self.assertEqual((stri.get("summary") or {}).get("paper_quality_evidence_debt"),0)
        self.assertEqual((stri.get("summary") or {}).get("canonical_problem_gate_pass_added"),0)
        self.assertFalse(stri["scientific_authority"])
        self.assertTrue(all(value is False for value in (stri.get("authority") or {}).values()))
        self.assertEqual(self.state["summary"]["asset_first_stri_paper_ready"],1)
        self.assertEqual(self.state["summary"]["asset_first_stri_submission_status"],"READY_TO_SUBMIT_PENDING_HUMAN_AUTHOR_SIGNOFF_AND_OPENREVIEW")
        self.assertEqual(self.state["summary"]["asset_first_stri_paper_quality_v2_passed"],1)
        self.assertEqual(self.state["summary"]["asset_first_stri_paper_quality_source_binding"],1)
        self.assertEqual(self.state["summary"]["asset_first_stri_paper_quality_evidence_debt"],0)
        self.assertEqual(self.state["summary"]["asset_first_stri_official_qa_checks_passed"],self.state["summary"]["asset_first_stri_official_qa_checks_total"])
        self.assertEqual((self.state["summary"]["asset_first_stri_main_text_pages"],self.state["summary"]["asset_first_stri_main_text_page_limit"]),(9,9))
        self.assertEqual(self.state["summary"]["asset_first_stri_supplement_ready"],1)
        self.assertEqual(self.state["summary"]["asset_first_stri_human_signoff_pending"],1)
        self.assertEqual(self.state["summary"]["asset_first_stri_canonical_problem_gate_added"],0)
        broken=copy.deepcopy(self.state);broken["asset_first_stri_paper_ready"]["summary"]["canonical_problem_gate_pass_added"]=1
        self.assertTrue(any("asset-first stri" in error.lower() for error in validate_state(broken)))

    def test_live_problem_discovery_rejects_shadow_portfolio_authority_leak(self) -> None:
        broken=copy.deepcopy(self.state)
        broken["paper_first_problem_discovery_contract"]["policy"]["search_portfolio_is_shadow_only"]=False
        self.assertTrue(any("shadow layer" in error for error in validate_state(broken)))
        leaked=copy.deepcopy(self.state)
        leaked["paper_first_problem_generator"]["policy"]["search_portfolio_enabled"]=True
        self.assertTrue(any("canonical problem generator" in error for error in validate_state(leaked)))
        multi=copy.deepcopy(self.state)
        multi["paper_first_problem_generator"]["policy"]["one_generator_call_max"]=False
        self.assertTrue(any("at most one generator call" in error for error in validate_state(multi)))

    def test_shadow_search_admission_is_zero_provider_search_control(self) -> None:
        admission=self.state["paper_first_shadow_search_admission"]
        self.assertFalse(admission["scientific_authority"])
        self.assertEqual((admission.get("summary") or {}).get("automatic_provider_calls_authorized"),0)
        self.assertTrue((admission.get("summary") or {}).get("qualification_allowed"))
        self.assertTrue((admission.get("summary") or {}).get("operator_upgrade_recompile"))
        self.assertFalse((admission.get("summary") or {}).get("same_discovery_operator_version"))
        self.assertTrue((admission.get("policy") or {}).get("admission_never_authorizes_provider_calls"))
        broken=copy.deepcopy(self.state);broken["paper_first_shadow_search_admission"]["summary"]["automatic_provider_calls_authorized"]=1
        self.assertTrue(any("Shadow Search admission" in error for error in validate_state(broken)))

    def test_shadow_continuation_frontier_is_deterministic_zero_authority_wait_or_control(self) -> None:
        frontier=self.state["paper_first_shadow_continuation_frontier"]
        self.assertFalse(frontier["scientific_authority"])
        self.assertEqual(frontier["status"],"READY_FOR_ZERO_PROVIDER_SHADOW_QUALIFICATION")
        self.assertEqual((frontier.get("summary") or {}).get("active_control_actions"),1)
        self.assertEqual((frontier.get("summary") or {}).get("external_wait"),0)
        self.assertEqual(frontier.get("next_control_action"),"canonical-private-pool-shadow-qualification")
        self.assertEqual((frontier.get("summary") or {}).get("automatic_provider_calls_authorized"),0)
        drift=copy.deepcopy(self.state);drift["paper_first_shadow_continuation_frontier"]["status"]="WAIT_EXTERNAL_PRIMARY_CONTENT_CHANGE"
        self.assertTrue(any("deterministic projection" in error for error in validate_state(drift)))
        escalated=copy.deepcopy(self.state);escalated["paper_first_shadow_continuation_frontier"]["summary"]["generator_reopen_authorized"]=1
        self.assertTrue(any("Shadow continuation frontier" in error for error in validate_state(escalated)))

    def test_latest_shadow_terminal_is_fail_closed_and_zero_authority(self) -> None:
        state=copy.deepcopy(self.state)
        state["paper_first_problem_search_portfolio"]={
            "schema_version":"3.2-shadow-import","scientific_authority":False,"policy":{"shadow_only":True},"latest_run_id":"shadow-r2",
            "latest_run":{"status":"SHADOW_TERMINAL_COMPLETE","scientific_authority":False,"policy":{"shadow_only":True,"canonical_primary_generator_queue_untouched":True,"live_source_coverage_effect":False,"current_source_web_receipt_required_after_semantic_clear":True,"missing_or_failed_current_source_reviewer_is_not_pass":True},"summary":{"semantic_clear":1,"current_source_clear":0,"current_source_blocked":1,"current_source_missing":0,"terminal_shadow_survivors":0,"live_paper_design_eligible":0},"authority":{"live_problem_gate":False,"paper_design":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
        }
        self.assertEqual(validate_state(state),[])
        missing=copy.deepcopy(state);missing["paper_first_problem_search_portfolio"]["latest_run"]["summary"]["current_source_missing"]=1
        self.assertTrue(any("completed shadow terminal" in error for error in validate_state(missing)))
        leak=copy.deepcopy(state);leak["paper_first_problem_search_portfolio"]["latest_run"]["authority"]["paper_design"]=True
        self.assertTrue(any("latest shadow run cannot authorize" in error for error in validate_state(leak)))
        inconsistent=copy.deepcopy(state);inconsistent["paper_first_problem_search_portfolio"]["latest_run"]["summary"]["terminal_shadow_survivors"]=1
        self.assertTrue(any("terminal survivors" in error for error in validate_state(inconsistent)))
        accounted=copy.deepcopy(state);latest=accounted["paper_first_problem_search_portfolio"]["latest_run"];latest["schema_version"]="1.1-shadow-run";latest["policy"].update({"execution_loss_is_not_scientific_negative":True,"problem_falsifier_preflight_must_cover_all_eligible_before_terminal_complete":True,"problem_falsifier_hold_is_not_scientific_fail":True});latest["summary"].update({"expansion_requested_shards":20,"expansion_successful_shards":19,"expansion_execution_failures":1,"formulation_requested_shards":12,"formulation_successful_shards":10,"formulation_provider_failures":2,"formulation_parse_failures":0,"formulation_requested_branches":24,"formulation_successful_branches":20,"formulation_execution_censored_branches":4,"problem_falsifier_eligible":4,"problem_falsifier_support_qualified":0,"problem_falsifier_hold_support_unavailable":4,"problem_falsifier_executed":0})
        self.assertEqual(validate_state(accounted),[])
        control_bound=copy.deepcopy(accounted);bound_latest=control_bound["paper_first_problem_search_portfolio"]["latest_run"];bound_latest["schema_version"]="1.2-shadow-run";bound_latest.update({"stage_runner_required_schema":"1.4","control_snapshot_sha256":"a"*64,"qualification_main_commit":"b"*40});bound_latest["policy"].update({"control_snapshot_bound_run":True,"control_snapshot_terminal_provenance_verified":True,"control_snapshot_provenance_is_bounded_sha_only":True})
        self.assertEqual(validate_state(control_bound),[])
        bad_control=copy.deepcopy(control_bound);bad_control["paper_first_problem_search_portfolio"]["latest_run"]["control_snapshot_sha256"]="not-a-sha"
        self.assertTrue(any("schema-1.4 control snapshot" in error for error in validate_state(bad_control)))
        bad_control_schema=copy.deepcopy(control_bound);bad_control_schema["paper_first_problem_search_portfolio"]["latest_run"]["stage_runner_required_schema"]="1.3"
        self.assertTrue(any("schema-1.4 control snapshot" in error for error in validate_state(bad_control_schema)))
        unbound_terminal=copy.deepcopy(control_bound);unbound_terminal["paper_first_problem_search_portfolio"]["latest_run"]["policy"]["control_snapshot_terminal_provenance_verified"]=False
        self.assertTrue(any("terminal gate" in error for error in validate_state(unbound_terminal)))
        incomplete=copy.deepcopy(accounted);incomplete_latest=incomplete["paper_first_problem_search_portfolio"]["latest_run"];incomplete_latest["status"]="SHADOW_TERMINAL_INCOMPLETE_PROBLEM_FALSIFIER_PREFLIGHT";incomplete_latest["summary"].update({"problem_falsifier_support_qualified":0,"problem_falsifier_hold_support_unavailable":0})
        self.assertEqual(validate_state(incomplete),[])
        false_complete=copy.deepcopy(incomplete);false_complete["paper_first_problem_search_portfolio"]["latest_run"]["status"]="SHADOW_TERMINAL_COMPLETE"
        self.assertTrue(any("complete problem-falsifier preflight coverage" in error for error in validate_state(false_complete)))
        routed=copy.deepcopy(accounted);routed_latest=routed["paper_first_problem_search_portfolio"]["latest_run"];routed_latest["policy"].update({"formulation_reduction_pending_is_not_scientific_block_or_pass":True,"machine_rechecks_reduction_pending_before_problem_falsifier":True});routed_latest["summary"].update({"formulation_reduction_pending":4,"machine_reduction_pending":4})
        self.assertEqual(validate_state(routed),[])
        bad_route=copy.deepcopy(routed);bad_route["paper_first_problem_search_portfolio"]["latest_run"]["summary"]["machine_reduction_pending"]=3
        self.assertTrue(any("machine reduction-pending" in error for error in validate_state(bad_route)))
        bad_route_policy=copy.deepcopy(routed);bad_route_policy["paper_first_problem_search_portfolio"]["latest_run"]["policy"]["formulation_reduction_pending_is_not_scientific_block_or_pass"]=False
        self.assertTrue(any("independently rechecked" in error for error in validate_state(bad_route_policy)))
        bad_account=copy.deepcopy(accounted);bad_account["paper_first_problem_search_portfolio"]["latest_run"]["summary"]["formulation_successful_shards"]=11
        self.assertTrue(any("formulation shard accounting" in error for error in validate_state(bad_account)))

    def test_retrieval_incomplete_without_new_lane_source_is_zero_call_compute_control(self) -> None:
        state=copy.deepcopy(self.state);primary=state["paper_first_primary_evidence"];generator=state["paper_first_problem_generator"]
        primary["summary"].update({"source_retrieval_complete":False,"source_coverage_exhausted":False,"unreviewed_lane_linked_sources":0})
        generator["status"]="SKIPPED_SOURCE_RETRIEVAL_INCOMPLETE";generator["summary"].update({"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0});generator["policy"].update({"incomplete_retrieval_without_new_lane_source_skips_model_call":True,"retrieval_incomplete_is_compute_control_not_scientific_negative":True});generator["source_coverage"]={"coverage_exhausted":False,"source_retrieval_complete":False,"unreviewed_lane_linked_sources":0,"carrier_probe_required":False,"carrier_probe_pending":0,"carrier_probe_complete":True,"scientific_authority":False}
        self.sync_discovery_frontier(state)
        self.assertEqual(validate_state(state),[])
        bad=copy.deepcopy(state);bad["paper_first_problem_generator"]["source_coverage"]["source_retrieval_complete"]=True
        self.assertTrue(any("retrieval-incomplete generator state" in error for error in validate_state(bad)))
        nonzero=copy.deepcopy(state);nonzero["paper_first_problem_generator"]["summary"]["generated"]=1
        self.assertTrue(any("retrieval-incomplete skip cannot contain" in error for error in validate_state(nonzero)))

    def test_primary_v11_carrier_probe_pending_is_zero_call_compute_control(self) -> None:
        state=copy.deepcopy(self.state);primary=state["paper_first_primary_evidence"];generator=state["paper_first_problem_generator"]
        primary["schema_version"]="1.1";primary["policy"].update({"no_lane_carrier_probe_enabled":True,"no_lane_carrier_probe_is_existing_object_rescue_only":True,"no_lane_carrier_probe_cannot_create_new_object":True,"no_lane_carrier_probe_has_zero_scientific_authority":True,"no_lane_carrier_probe_failure_prevents_coverage_exhaustion":True,"carrier_probe_pending_skips_live_generator_call":True})
        primary["summary"].update({"source_coverage_exhausted":False,"carrier_probe_required":True,"carrier_probe_pending":2,"carrier_probe_complete":False,"candidate_generation_ready":False})
        primary["carrier_probe"]={"required":True,"attempted":3,"rescued":0,"pending":2,"complete":False,"portable_receipts":[],"scientific_authority":False}
        generator["status"]="SKIPPED_SOURCE_CARRIER_PROBE_PENDING";generator["summary"].update({"generated":0,"written_to_auto_inbox":0,"semantic_clear":0,"semantic_blocked":0});generator["policy"].update({"carrier_probe_pending_skips_model_call":True,"carrier_probe_pending_is_compute_control_not_scientific_negative":True});generator["source_coverage"]={"coverage_exhausted":False,"unreviewed_lane_linked_sources":0,"carrier_probe_required":True,"carrier_probe_pending":2,"carrier_probe_complete":False,"scientific_authority":False}
        self.sync_discovery_frontier(state)
        self.assertEqual(validate_state(state),[])
        exhausted=copy.deepcopy(state);exhausted["paper_first_primary_evidence"]["summary"]["source_coverage_exhausted"]=True
        self.assertTrue(any("carrier-probe backlog" in error for error in validate_state(exhausted)))
        unknown=copy.deepcopy(state);unknown["paper_first_primary_evidence"]["carrier_probe"]["portable_receipts"]=[{"ref":"arXiv:x","primary_sha256":"a"*64,"fulltext_sha256":"b"*64,"classifier_version":"existing-object-carrier-v1","live_rescue_eligible_lanes":["new_object"],"scientific_authority":False}]
        self.assertTrue(any("existing-object receipts" in error for error in validate_state(unknown)))
        scope=copy.deepcopy(state);scope["paper_first_primary_evidence"]["carrier_probe"]["portable_receipts"]=[{"ref":"arXiv:scope","primary_sha256":"a"*64,"fulltext_sha256":"","classifier_version":"existing-object-carrier-v1","probe_outcome":"SCOPE_EXCLUDED_BY_PRIMARY","scope_exclusion_rule":"genetic-network-programming-non-llm-v1","live_rescue_eligible_lanes":[],"scientific_authority":False}]
        self.assertEqual(validate_state(scope),[])
        bad_generator=copy.deepcopy(state);bad_generator["paper_first_problem_generator"]["source_coverage"]["coverage_exhausted"]=True
        self.assertTrue(any("pending generator state" in error for error in validate_state(bad_generator)))

    def test_scientific_object_retrieval_audit_is_public_safe_shadow_only(self) -> None:
        audit=self.state["paper_first_scientific_object_retrieval_audit"]
        self.assertFalse(audit["scientific_authority"])
        self.assertTrue(audit["policy"]["shadow_only"])
        self.assertFalse(audit["policy"]["live_query_set_changed"])
        self.assertTrue(audit["policy"]["candidate_metadata_does_not_count_as_verified_primary_support"])
        self.assertEqual(audit["summary"]["activation_authorized"],0)
        self.assertNotIn('"query"',json.dumps(audit))
        broken=copy.deepcopy(self.state);broken["paper_first_scientific_object_retrieval_audit"]["policy"]["live_query_set_changed"]=True
        self.assertTrue(any("scientific-object retrieval audit" in error for error in validate_state(broken)))
        leaked=copy.deepcopy(self.state);leaked["paper_first_scientific_object_retrieval_audit"]["results"]={"x":{"status":"NO_NEW_SUPPORT_FOUND","ref":"arXiv:secret","scientific_authority":False}}
        self.assertTrue(any("cannot expose private" in error for error in validate_state(leaked)))

    def test_scientific_object_candidate_evidence_is_public_safe_and_zero_exposure(self) -> None:
        evidence=self.state["paper_first_scientific_object_candidate_evidence"]
        self.assertFalse(evidence["scientific_authority"])
        self.assertTrue(evidence["policy"]["shadow_only"])
        self.assertTrue(evidence["policy"]["network_fetch_forbidden"])
        self.assertFalse(evidence["policy"]["source_exposure_effect"])
        self.assertFalse(evidence["policy"]["live_query_effect"])
        self.assertEqual(evidence["summary"]["activation_authorized"],0)
        self.assertNotIn('"ref":',json.dumps(evidence))
        broken=copy.deepcopy(self.state);broken["paper_first_scientific_object_candidate_evidence"]["policy"]["source_exposure_effect"]=True
        self.assertTrue(any("candidate evidence" in error for error in validate_state(broken)))
        leaked=copy.deepcopy(self.state);leaked["paper_first_scientific_object_candidate_evidence"]["results"]={"x":{"ref":"arXiv:secret","scientific_authority":False}}
        self.assertTrue(any("cannot expose private primary" in error for error in validate_state(leaked)))

    def test_support_release_watch_is_public_safe_and_zero_authority(self) -> None:
        watch=copy.deepcopy(self.state["paper_first_support_release_watch"])
        self.assertFalse(watch["scientific_authority"])
        self.assertTrue(watch["policy"]["primary_declared_release_endpoints_only"])
        self.assertTrue(watch["policy"]["related_work_repository_links_are_not_watch_targets"])
        self.assertTrue(watch["policy"]["release_surface_change_only_requests_recheck"])
        self.assertTrue(watch["policy"]["release_watch_cannot_mark_support_qualified"])
        self.assertTrue(watch["policy"]["no_endpoint_primary_refresh_is_primary_source_only"])
        self.assertTrue(watch["policy"]["primary_declaration_refresh_has_zero_source_exposure_effect"])
        self.assertTrue(watch["policy"]["primary_declaration_refresh_cannot_qualify_support"])
        self.assertEqual(int((watch.get("summary") or {}).get("support_qualified") or 0),0)
        self.assertEqual(int((watch.get("summary") or {}).get("generator_reopen_authorized") or 0),0)
        self.assertEqual(int((watch.get("summary") or {}).get("problem_gate_authorized") or 0),0)
        text=json.dumps(watch)
        for marker in ('"rows"','"url"','"source_refs"','"required_unit"','"reopen_only_if"'):
            self.assertNotIn(marker,text)
        state=copy.deepcopy(self.state)
        state.pop("paper_first_shadow_continuation_frontier",None)
        state["paper_first_support_release_watch"]={
            "schema_version":"1.0","status":"SUPPORT_RELEASE_WATCH_COMPLETE","scientific_authority":False,
            "policy":{"scientific_authority":False,"primary_declared_release_endpoints_only":True,"related_work_repository_links_are_not_watch_targets":True,"release_surface_change_only_requests_recheck":True,"release_watch_cannot_mark_support_qualified":True,"release_watch_cannot_reopen_generator_or_problem_gate":True,"release_watch_has_zero_source_exposure_effect":True,"network_checks_are_cooldown_bounded":True,"no_endpoint_primary_refresh_is_primary_source_only":True,"primary_declaration_refresh_has_zero_source_exposure_effect":True,"primary_declaration_refresh_cannot_qualify_support":True,"public_summary_excludes_urls_refs_required_units_and_private_paths":True},
            "summary":{"support_holds":4,"explicit_release_targets":2,"no_explicit_endpoint":2,"recheck_required":1,"support_qualified":0,"generator_reopen_authorized":0,"problem_gate_authorized":0,"primary_declaration_refresh_checked":2,"primary_declaration_refresh_changed":0},
            "status_counts":{"RECHECK_REQUIRED_RELEASE_CHANGED":1},
        }
        self.sync_discovery_frontier(state)
        self.assertEqual(validate_state(state),[])
        escalated=copy.deepcopy(state);escalated["paper_first_support_release_watch"]["summary"]["support_qualified"]=1
        self.assertTrue(any("support release watch cannot authorize" in error for error in validate_state(escalated)))
        leaked=copy.deepcopy(state);leaked["paper_first_support_release_watch"]["rows"]=[{"url":"https://secret.example","required_unit":"secret"}]
        self.assertTrue(any("cannot expose URLs" in error for error in validate_state(leaked)))

    def test_support_asset_recheck_queue_is_public_safe_durable_and_zero_authority(self) -> None:
        queue=copy.deepcopy(self.state["paper_first_support_asset_recheck_queue"])
        self.assertFalse(queue["scientific_authority"])
        self.assertTrue(queue["policy"]["release_change_only_creates_asset_recheck_task"])
        self.assertTrue(queue["policy"]["queue_is_durable_across_release_watch_cooldown"])
        self.assertTrue(queue["policy"]["explicit_asset_resolution_required_to_clear_entry"])
        for key in ("support_qualified","generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized"):
            self.assertEqual(int((queue.get("summary") or {}).get(key) or 0),0)
        self.assertNotIn("entries",queue)
        state=copy.deepcopy(self.state)
        state.pop("paper_first_shadow_continuation_frontier",None)
        state.pop("paper_first_support_asset_recheck_handoff",None)
        state["paper_first_support_asset_recheck_queue"]={
            "schema_version":"1.0","status":"SUPPORT_ASSET_RECHECK_QUEUE_READY","scientific_authority":False,
            "policy":{"scientific_authority":False,"release_change_only_creates_asset_recheck_task":True,"queue_is_durable_across_release_watch_cooldown":True,"queue_only_tracks_current_support_holds":True,"queue_cannot_mark_support_qualified":True,"queue_cannot_reopen_generator_or_problem_gate":True,"queue_cannot_authorize_method_experiment_p0_gpu":True,"explicit_asset_resolution_required_to_clear_entry":True,"automatic_provider_calls_authorized":False,"public_summary_excludes_entries_refs_urls_required_units_and_private_paths":True},
            "summary":{"support_holds":4,"release_recheck_signals":1,"queued":1,"new_triggers":1,"carried_forward":0,"support_qualified":0,"generator_reopen_authorized":0,"problem_gate_authorized":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0,"gpu_authorized":0},
        }
        self.sync_discovery_frontier(state)
        self.assertEqual(validate_state(state),[])
        resolved=copy.deepcopy(state);resolved_queue=resolved["paper_first_support_asset_recheck_queue"];resolved_queue["policy"].update({"asset_resolution_must_bind_latest_trigger_digest":True,"asset_resolution_cannot_mark_support_qualified_or_reopen":True,"support_inventory_recheck_remains_queue_handoff_not_resolution":True});resolved_queue["summary"].update({"queued":0,"resolved":1,"resolution_still_unavailable":1,"resolution_irrelevant_release":0})
        self.sync_discovery_frontier(resolved)
        self.assertEqual(validate_state(resolved),[])
        bad_resolution=copy.deepcopy(resolved);bad_resolution["paper_first_support_asset_recheck_queue"]["policy"]["asset_resolution_must_bind_latest_trigger_digest"]=False
        self.assertTrue(any("durable private-task accounting" in error for error in validate_state(bad_resolution)))
        escalated=copy.deepcopy(state);escalated["paper_first_support_asset_recheck_queue"]["summary"]["generator_reopen_authorized"]=1
        self.assertTrue(any("support asset recheck queue cannot authorize" in error for error in validate_state(escalated)))
        leaked=copy.deepcopy(state);leaked["paper_first_support_asset_recheck_queue"]["entries"]=[{"candidate_id":"secret","required_unit":"secret"}]
        self.assertTrue(any("support asset recheck public state cannot expose" in error for error in validate_state(leaked)))

    def test_support_asset_handoff_is_bounded_to_existing_preflight_and_matches_queue(self) -> None:
        state=copy.deepcopy(self.state)
        state.pop("paper_first_shadow_continuation_frontier",None)
        state["paper_first_support_asset_recheck_queue"]={
            "schema_version":"1.0","status":"SUPPORT_ASSET_RECHECK_QUEUE_READY","scientific_authority":False,
            "policy":{"scientific_authority":False,"release_change_only_creates_asset_recheck_task":True,"queue_is_durable_across_release_watch_cooldown":True,"queue_only_tracks_current_support_holds":True,"queue_cannot_mark_support_qualified":True,"queue_cannot_reopen_generator_or_problem_gate":True,"queue_cannot_authorize_method_experiment_p0_gpu":True,"explicit_asset_resolution_required_to_clear_entry":True,"automatic_provider_calls_authorized":False,"public_summary_excludes_entries_refs_urls_required_units_and_private_paths":True},
            "summary":{"support_holds":4,"release_recheck_signals":1,"queued":1,"new_triggers":1,"carried_forward":0,"support_qualified":0,"generator_reopen_authorized":0,"problem_gate_authorized":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0,"gpu_authorized":0},
        }
        state["paper_first_support_asset_recheck_handoff"]={
            "schema_version":"1.0","status":"SUPPORT_ASSET_RECHECK_HANDOFF_READY","scientific_authority":False,
            "policy":{"scientific_authority":False,"handoff_reuses_existing_problem_falsifier_support_inventory":True,"asset_recheck_cannot_define_a_parallel_support_gate":True,"release_change_is_not_support_qualification":True,"support_inventory_receipt_required_before_any_support_decision":True,"problem_falsifier_preflight_remains_support_authority_boundary":True,"handoff_cannot_execute_falsifier_automatically":True,"handoff_cannot_reopen_generator_or_problem_gate":True,"handoff_cannot_authorize_method_experiment_p0_gpu":True,"automatic_provider_calls_authorized":False,"public_summary_excludes_entries_refs_urls_required_units_and_private_paths":True},
            "summary":{"queued_asset_rechecks":1,"support_inventory_recheck_ready":1,"provenance_incomplete":0,"automatic_execution_authorized":0,"provider_calls_authorized":0,"support_qualified":0,"falsifier_execution_authorized":0,"generator_reopen_authorized":0,"problem_gate_authorized":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0,"gpu_authorized":0},
        }
        self.sync_discovery_frontier(state)
        self.assertEqual(validate_state(state),[])
        mismatch=copy.deepcopy(state);mismatch["paper_first_support_asset_recheck_handoff"]["summary"]["support_inventory_recheck_ready"]=0
        self.assertTrue(any("partition ready/provenance-hold" in error for error in validate_state(mismatch)))
        leak=copy.deepcopy(state);leak["paper_first_support_asset_recheck_handoff"]["entries"]=[{"candidate_id":"secret"}]
        self.assertTrue(any("cannot expose private queue" in error for error in validate_state(leak)))
        escalated=copy.deepcopy(state);escalated["paper_first_support_asset_recheck_handoff"]["summary"]["provider_calls_authorized"]=1
        self.assertTrue(any("cannot authorize provider" in error for error in validate_state(escalated)))

    def test_discovery_frontier_is_trigger_driven_zero_authority_and_consistent(self) -> None:
        frontier=self.state["paper_first_discovery_frontier"]
        evidence_open=int((frontier.get("summary") or {}).get("evidence_internal_open") or 0)
        if evidence_open:
            self.assertEqual(frontier["status"],"EVIDENCE_ACQUISITION_PENDING")
            self.assertEqual(frontier["summary"]["open_internal_frontiers"],1)
        else:
            self.assertIn(frontier["status"],{"WAIT_EXTERNAL_EVIDENCE_TRIGGERS","SHADOW_QUALIFICATION_PENDING"})
        self.assertGreaterEqual(frontier["summary"]["external_triggers"],1)
        for key in ("automatic_model_calls_authorized","automatic_problem_gate_authorized","automatic_method_authorized","automatic_experiment_authorized","automatic_p0_authorized","automatic_gpu_authorized"):
            self.assertEqual(frontier["summary"][key],0)
        self.assertFalse(frontier["scientific_authority"])
        stale=copy.deepcopy(self.state);stale["paper_first_discovery_frontier"]["status"]="LIVE_SOURCE_DISCOVERY_PENDING"
        self.assertTrue(any("frontier must equal the deterministic projection" in error for error in validate_state(stale)))
        escalated=copy.deepcopy(self.state);escalated["paper_first_discovery_frontier"]["summary"]["automatic_model_calls_authorized"]=1
        self.assertTrue(any("discovery frontier cannot authorize" in error for error in validate_state(escalated)))

    def test_canonical_paper_design_backlog_is_durable_but_cannot_escalate_authority(self) -> None:
        state=copy.deepcopy(self.state)
        state["paper_first_paper_design_backlog"]={
            "schema_version":"1.0",
            "policy":{"problem_gate_pass_is_durable_until_human_paper_design_resolution":True,"volatile_discovery_queue_cannot_erase_backlog":True,"paper_design_eligibility_is_not_method_authority":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False,"automatic_gpu_authority":False},
            "summary":{"entries":1,"pending_human_paper_design":1,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0,"gpu_authorized":0},
            "entries":[{"backlog_id":"x","candidate_id":"LIVE-1","status":"AWAIT_HUMAN_PAPER_DESIGN_REVIEW","paper_design_eligible":True,"authority":{"paper_design_review":True,"method":False,"experiment":False,"p0":False,"gpu":False},"scientific_authority":False}],
            "scientific_authority":False,
        }
        self.assertEqual(validate_state(state),[])
        broken=copy.deepcopy(state);broken["paper_first_paper_design_backlog"]["policy"]["automatic_method_authority"]=True
        self.assertTrue(any("Paper-Design backlog cannot authorize" in error for error in validate_state(broken)))

    def test_global_relation_recall_requires_reduction_and_only_residual_can_reopen(self) -> None:
        state=copy.deepcopy(self.state);digest="d"*64
        state["paper_first_global_relation_recall"]={
            "schema_version":"1.1","status":"GLOBAL_RELATION_RECALL_COMPLETE",
            "policy":{"source_coverage_exhaustion_is_not_relation_exhaustion":True,"relation_miner_is_search_control_only":True,"cross_source_recall_supplements_but_does_not_replace_search_portfolio":True,"all_lane_pass_proposals_require_reduction_review":True,"not_reduced_only_reopens_focused_problem_generator":True,"automatic_problem_gate_authority":False,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},
            "summary":{"lane_pass":1,"reduction_reviewed":1,"not_reduced":0,"focused_problem_generator_reopen_required":False,"relation_universe_digest":digest},
            "relation_coverage":{"scientific_authority":False},"proposals":[],
            "last_completed_scan":{"run_id":"relation-1","relation_universe_digest":digest,"scientific_authority":False},"scientific_authority":False,
        }
        self.sync_relation_freshness(state)
        self.assertEqual(validate_state(state),[])
        missing=copy.deepcopy(state);missing["paper_first_global_relation_recall"]["summary"]["reduction_reviewed"]=0
        self.assertTrue(any("lane-PASS global relation proposal" in error for error in validate_state(missing)))
        fake=copy.deepcopy(state);fake["paper_first_global_relation_recall"]["summary"]["focused_problem_generator_reopen_required"]=True
        self.assertTrue(any("focused problem-generator reopen" in error for error in validate_state(fake)))

    def test_relation_v12_delta_scan_requires_bounded_new_endpoint_provenance(self) -> None:
        state=copy.deepcopy(self.state);digest="d"*64
        state["paper_first_global_relation_recall"]={
            "schema_version":"1.2","status":"GLOBAL_RELATION_RECALL_COMPLETE","scientific_authority":False,
            "policy":{"scientific_authority":False,"source_coverage_exhaustion_is_not_relation_exhaustion":True,"relation_miner_is_search_control_only":True,"cross_source_recall_supplements_but_does_not_replace_search_portfolio":True,"all_lane_pass_proposals_require_reduction_review":True,"not_reduced_only_reopens_focused_problem_generator":True,"stale_completed_scan_uses_delta_only_new_endpoint_pairs":True,"delta_only_scan_forbids_old_old_pairs":True,"explicit_manual_writer_admission_required":True,"automatic_problem_gate_authority":False,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False},
            "summary":{"lane_pass":0,"reduction_reviewed":0,"not_reduced":0,"focused_problem_generator_reopen_required":False,"relation_universe_digest":digest},
            "relation_coverage":{"scientific_authority":False},"proposals":[],
            "writer_admission":{"schema_version":"1.0","status":"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN","policy":{"scientific_authority":False,"automatic_model_scan_authority":False,"manual_execution_requires_explicit_operator_flag":True},"summary":{"manual_scan_eligible":True,"automatic_model_scan_authorized":False},"scientific_authority":False},
            "delta_scan":{"enabled":True,"required_new_endpoint_count":12,"required_new_endpoint_digest":"a"*64,"prior_scan_run_id":"prior-run","scientific_authority":False},
            "last_completed_scan":{"run_id":"relation-new","mode":"delta_only_new_endpoint","prior_scan_run_id":"prior-run","required_new_endpoint_count":12,"relation_universe_digest":digest,"scientific_authority":False},
        }
        self.sync_relation_freshness(state)
        self.assertEqual(validate_state(state),[])
        bad_mode=copy.deepcopy(state);bad_mode["paper_first_global_relation_recall"]["last_completed_scan"]["mode"]="full_relation_universe"
        self.assertTrue(any("completed delta-only relation scan" in error for error in validate_state(bad_mode)))
        bad_digest=copy.deepcopy(state);bad_digest["paper_first_global_relation_recall"]["delta_scan"]["required_new_endpoint_digest"]="bad"
        self.assertTrue(any("new-endpoint provenance" in error for error in validate_state(bad_digest)))

    def test_stale_global_relation_scan_cannot_be_current_negative_or_reopen(self) -> None:
        state=copy.deepcopy(self.state)
        stale_digest="b"*64
        relation=state["paper_first_global_relation_recall"]
        relation.setdefault("summary",{})["relation_universe_digest"]=stale_digest
        relation.setdefault("last_completed_scan",{})["relation_universe_digest"]=stale_digest
        self.sync_relation_freshness(state)
        self.assertEqual(state["paper_first_global_relation_freshness"]["status"],"STALE_RELATION_UNIVERSE")
        self.assertEqual(validate_state(state),[])
        false_negative=copy.deepcopy(state);false_negative["paper_first_global_relation_freshness"]["summary"]["current_not_reduced_unknown"]=False
        self.assertTrue(any("stale Global Relation Recall" in error for error in validate_state(false_negative)))
        illegal_reopen=copy.deepcopy(state);illegal_reopen["paper_first_global_relation_freshness"]["summary"]["focused_problem_generator_reopen_allowed"]=True
        self.assertTrue(any("stale Global Relation Recall" in error for error in validate_state(illegal_reopen)))

    def test_relation_freshness_must_match_embedded_generator_and_relation_state(self) -> None:
        state=copy.deepcopy(self.state)
        expected=relation_recall_freshness(state["paper_first_problem_generator"],state["paper_first_global_relation_recall"])
        self.assertEqual(state["paper_first_global_relation_freshness"]["status"],expected["status"])
        stale=copy.deepcopy(state)
        stale["paper_first_global_relation_freshness"]["status"]="STALE_RELATION_UNIVERSE"
        stale["paper_first_global_relation_freshness"]["summary"]["universe_stale"]=True
        self.assertTrue(any("freshness must match embedded Generator and Relation state" in error for error in validate_state(stale)))

    def test_relation_delta_preflight_is_typed_opportunity_only_and_cannot_reopen(self) -> None:
        state=copy.deepcopy(self.state)
        state["paper_first_global_relation_delta_preflight"]={
            "schema_version":"1.0","status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE",
            "policy":{"scientific_authority":False,"deterministic_typed_evidence_delta_only":True,"pair_slots_are_not_lane_valid_pairs":True,"cannot_reopen_generator":True,"cannot_authorize_relation_model_scan":True,"cannot_authorize_problem_gate":True},
            "summary":{"old_reviewed_sources":214,"current_reviewed_sources":226,"new_reviewed_sources":12,"new_empirical_sources":11,"new_assumption_sources":0,"new_failure_sources":11,"new_boundary_sources":8,"model_scan_authorized":False,"focused_generator_reopen_authorized":False},
            "pair_slots":{"failure_failure_slots_touching_new":1782},
            "interpretation":{"assumption_break":"NO_NEW_ASSUMPTION_ENDPOINT","convergent_failure":"NEW_FAILURE_EVIDENCE_PRESENT_LANE_VALIDITY_UNKNOWN"},
            "scientific_authority":False,
        }
        self.assertEqual(validate_state(state),[])
        model=copy.deepcopy(state);model["paper_first_global_relation_delta_preflight"]["summary"]["model_scan_authorized"]=True
        self.assertTrue(any("relation delta preflight" in error for error in validate_state(model)))
        pair=copy.deepcopy(state);pair["paper_first_global_relation_delta_preflight"]["policy"]["pair_slots_are_not_lane_valid_pairs"]=False
        self.assertTrue(any("relation delta preflight" in error for error in validate_state(pair)))

    def test_manual_relation_scan_admission_is_execution_precondition_not_authority(self) -> None:
        state=copy.deepcopy(self.state)
        state["paper_first_global_relation_scan_admission"]={
            "schema_version":"1.0","status":"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN",
            "policy":{"scientific_authority":False,"automatic_model_scan_authority":False,"manual_execution_requires_explicit_operator_flag":True,"manual_eligibility_is_not_scientific_authority":True,"relation_scan_cannot_authorize_problem_gate":True,"relation_scan_cannot_authorize_method_experiment_p0_gpu":True,"preconditions_are_deterministic_search_control_only":True},
            "summary":{"checks":15,"passed":15,"failed":0,"manual_scan_eligible":True,"automatic_model_scan_authorized":False,"new_reviewed_sources":12,"new_empirical_sources":11,"new_assumption_sources":0,"new_failure_sources":11,"new_boundary_sources":8,"current_reviewed_sources":226,"last_scanned_sources":214},
            "failed_check_count":0,"freshness_status":"STALE_RELATION_UNIVERSE","delta_status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE","scientific_authority":False,
        }
        self.sync_discovery_frontier(state)
        self.assertEqual(validate_state(state),[])
        auto=copy.deepcopy(state);auto["paper_first_global_relation_scan_admission"]["summary"]["automatic_model_scan_authorized"]=True
        self.assertTrue(any("manual relation-scan admission" in error for error in validate_state(auto)))
        flag=copy.deepcopy(state);flag["paper_first_global_relation_scan_admission"]["policy"]["manual_execution_requires_explicit_operator_flag"]=False
        self.assertTrue(any("manual relation-scan admission" in error for error in validate_state(flag)))

    def test_v23_problem_deadend_memory_is_zero_authority_and_requires_basin_escape(self) -> None:
        state=copy.deepcopy(self.state); generator=state["paper_first_problem_generator"]
        generator["schema_version"]="2.3"
        generator["policy"].update({"reviewer_blocked_problem_memory_has_zero_scientific_authority":True,"repeated_reduction_basin_requires_search_escape":True,"portable_blocked_problem_memory_is_search_control_only":True,"reviewer_declared_excerpt_source_is_audit_metadata_not_grounding_authority":True,"exact_excerpt_location_is_machine_inferred":True})
        generator.setdefault("saturation_memory",{})["blocked_problem_memory"]={"blocked_candidate_attempts":5,"top_reduction_basin":{"pattern":"procedural-memory-nonmonotonicity","count":5,"fraction":1.0},"repeated_reduction_basin":True,"search_escape_required":True,"portable_blocked_problem_memory":[{"signature_id":"x","scientific_authority":False}],"scientific_authority":False}
        self.assertEqual(validate_state(state),[])
        broken=copy.deepcopy(state); broken["paper_first_problem_generator"]["saturation_memory"]["blocked_problem_memory"]["search_escape_required"]=False
        self.assertTrue(any("repeated problem-reduction basin" in error for error in validate_state(broken)))

    def test_v24_generated_problem_state_requires_complete_zero_authority_lane_search(self) -> None:
        state=copy.deepcopy(self.state); generator=state["paper_first_problem_generator"]
        generator["schema_version"]="2.4"; generator["status"]="GENERATED_ZERO_CANDIDATES"; generator["generation_notes"]="All four lanes were audited and none survives."
        generator["policy"].update({"reviewer_blocked_problem_memory_has_zero_scientific_authority":True,"repeated_reduction_basin_requires_search_escape":True,"portable_blocked_problem_memory_is_search_control_only":True,"reviewer_declared_excerpt_source_is_audit_metadata_not_grounding_authority":True,"exact_excerpt_location_is_machine_inferred":True,"one_generator_call_must_audit_all_discovery_lanes":True,"lane_search_diagnostics_have_zero_scientific_authority":True,"historically_underexplored_lanes_are_searched_first":True,"lane_search_never_requires_candidate":True})
        generator["search_diagnostics"]={"lane_search_priority":["CONTRADICTION","CONVERGENT_FAILURE","UNEXPLAINED_BOUNDARY","ASSUMPTION_BREAK"],"lane_search_complete":True,"lane_search":[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No pair."} for lane in ("CONTRADICTION","CONVERGENT_FAILURE","ASSUMPTION_BREAK","UNEXPLAINED_BOUNDARY")],"scientific_authority":False}
        self.sync_discovery_frontier(state)
        self.assertEqual(validate_state(state),[])
        broken=copy.deepcopy(state); broken["paper_first_problem_generator"]["search_diagnostics"]["lane_search"].pop()
        self.assertTrue(any("complete machine-audited status" in error for error in validate_state(broken)))

    def test_v25_last_completed_lane_search_is_zero_authority_portable_receipt(self) -> None:
        state=copy.deepcopy(self.state);generator=state["paper_first_problem_generator"]
        generator["schema_version"]="2.5";generator["status"]="GENERATED_ZERO_CANDIDATES";generator["generation_notes"]="All four lanes were audited and none survives."
        generator["policy"].update({"reviewer_blocked_problem_memory_has_zero_scientific_authority":True,"repeated_reduction_basin_requires_search_escape":True,"portable_blocked_problem_memory_is_search_control_only":True,"reviewer_declared_excerpt_source_is_audit_metadata_not_grounding_authority":True,"exact_excerpt_location_is_machine_inferred":True,"one_generator_call_must_audit_all_discovery_lanes":True,"lane_search_diagnostics_have_zero_scientific_authority":True,"historically_underexplored_lanes_are_searched_first":True,"lane_search_never_requires_candidate":True,"last_completed_lane_search_is_portable_zero_authority_receipt":True,"terminal_zero_call_skip_preserves_last_completed_lane_search":True})
        priority=["CONTRADICTION","CONVERGENT_FAILURE","UNEXPLAINED_BOUNDARY","ASSUMPTION_BREAK"];rows=[{"lane":lane,"status":"NO_PAIR","source_refs":[],"reason":"No pair."} for lane in priority]
        receipt={"run_id":generator.get("run_id") or "v25-run","generator_status":"GENERATED_ZERO_CANDIDATES","generated_at":"2026-08-13T14:12:22+00:00","lane_search_priority":priority,"lane_search":rows,"generation_notes":"All four lanes audited.","scientific_authority":False}
        generator["run_id"]=receipt["run_id"];generator["search_diagnostics"]={"lane_search_priority":priority,"lane_search_complete":True,"lane_search":rows,"last_completed_lane_search":receipt,"scientific_authority":False}
        self.sync_discovery_frontier(state)
        self.assertEqual(validate_state(state),[])
        broken=copy.deepcopy(state);broken["paper_first_problem_generator"]["search_diagnostics"]["last_completed_lane_search"]["scientific_authority"]=True
        self.assertTrue(any("last completed lane-search receipt is invalid" in error for error in validate_state(broken)))
        stale=copy.deepcopy(state);stale["paper_first_problem_generator"]["search_diagnostics"]["last_completed_lane_search"]["run_id"]="older-run"
        self.assertTrue(any("must refresh the last completed lane-search receipt" in error for error in validate_state(stale)))


if __name__ == "__main__":
    unittest.main()
