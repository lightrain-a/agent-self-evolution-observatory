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
        self.assertEqual(self.state["summary"]["discussion_ready"], 20)
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
        self.assertEqual(compiler["summary"]["execution_ready"], 0)
        self.assertEqual(compiler["summary"]["blocked"], 4)
        self.assertEqual(compiler["summary"]["formal_p0_ready"], 0)
        self.assertEqual(compiler["summary"]["formal_p0_total"], 2)
        self.assertEqual(compiler["summary"]["updater_prerequisite_pass"], 0)
        self.assertEqual(compiler["summary"]["updater_prerequisite_fail"], 4)
        self.assertEqual(compiler["summary"]["gate_failures"]["mechanism_identifiability"], 4)
        self.assertTrue(compiler["policy"]["updater_competence_required_before_gate_1"])
        self.assertTrue(compiler["policy"]["updater_competence_is_not_a_ninth_gate"])
        self.assertTrue(compiler["policy"]["automatic_override_forbidden"])
        self.assertTrue(self.state["pilot_registry"]["policy"]["p0_execution_requires_pre_experiment_8_of_8"])

    def test_memory_support_workflow_preserves_stage_boundaries(self) -> None:
        workflow = self.state["mem_xfer_workflow"]
        self.assertEqual(workflow["support_qualification"]["status"], "support_qualification_pass")
        self.assertTrue((workflow["full_support"].get("pre_gpu_audit") or {}).get("execution_ready"))
        self.assertIn(workflow["full_support"]["status"], {"full_support_ready", "full_qwen_support_running", "full_qwen_support_checkpoint", "full_support_complete"})
        progress = workflow["full_support"]["progress"]
        if workflow["full_support"]["status"] != "full_support_ready":
            self.assertGreaterEqual(int(progress.get("completed_episodes") or 0), 72)
            self.assertEqual(int(progress.get("total_episodes") or 0), 216)
        if workflow["full_support"].get("provenance_deviation"):
            self.assertEqual(workflow["full_support"]["scientific_authority"], "provisional-only")
        self.assertEqual(workflow["second_model"]["status"], "second_model_hold")
        self.assertFalse(workflow["second_model"]["authorized"])

    def test_experiment_iteration_distinguishes_pilot_failure_layers(self) -> None:
        iteration = self.state["experiment_iteration"]
        self.assertEqual(iteration["summary"]["nodes"], 4)
        self.assertEqual(iteration["summary"]["scale_up_allowed"], 0)
        by_code = {item["code"]: item for item in iteration["nodes"]}
        self.assertEqual(by_code["A-1"]["diagnosis"], "representation-signal-mismatch")
        self.assertEqual(by_code["A-2"]["diagnosis"], "no-label-variation")
        self.assertEqual(by_code["B-1"]["diagnosis"], "matched-simplification-tie")
        self.assertEqual(by_code["E-1"]["diagnosis"], "objective-claim-mismatch")
        self.assertFalse(by_code["A-1"]["scientific_belief_update_allowed"])
        self.assertFalse(by_code["A-2"]["scientific_belief_update_allowed"])
        self.assertTrue(by_code["B-1"]["scientific_belief_update_allowed"])
        self.assertFalse(by_code["E-1"]["scientific_belief_update_allowed"])

    def test_repair_queue_contains_structured_blocks(self) -> None:
        queue = self.state["repair_queue"]
        self.assertEqual(queue["summary"]["queued_ideas"], 1)
        self.assertEqual({item["idea_id"] for item in queue["queue"]}, {"update-surface-router"})
        self.assertTrue(all(item["idea_id"] not in self.state["human_terminal_ideas"]["parents"] for item in queue["queue"]))
        self.assertTrue(queue["policy"]["preserve_parent_branch"])
        self.assertTrue(queue["policy"]["automatic_selection_forbidden"])
        self.assertTrue(queue["policy"]["terminal_human_parent_repair_forbidden"])
        self.assertTrue(queue["policy"]["absorbed_child_repair_forbidden"])

    def test_reference_components_are_explicit(self) -> None:
        sources = {item["source"] for item in self.state["components"]}
        self.assertIn("ResearchAgent", sources)
        self.assertIn("AI-Researcher", sources)
        self.assertIn("MOOSE-Chem / Deep-Ideation", sources)
        self.assertIn("AI-Scientist-v2", sources)
        self.assertTrue(any("Co-Scientist" in source for source in sources))
        self.assertTrue(any("HypoRefine" in source and "IdeaForge" in source for source in sources))
        self.assertEqual(len(self.state["components"]), 13)
        self.assertIn("Human terminal ledger", sources)
        self.assertEqual(self.state["summary"]["human_terminal_p0"], 13)
        self.assertEqual(self.state["summary"]["human_terminal_p0_ready"], 0)
        self.assertEqual(self.state["summary"]["p0_admission_active"], 20)
        self.assertEqual(self.state["summary"]["p0_admission_transitioned"], 16)
        self.assertEqual(self.state["summary"]["p0_admission_settings_complete"], 20)
        self.assertEqual(self.state["p0_offline_qualification"]["summary"]["ideas"], 16)
        self.assertEqual(self.state["p0_realizability"]["summary"]["audited"], 14)
        self.assertEqual(self.state["p0_realizability"]["summary"]["synthetic_pass"], 14)
        self.assertEqual(self.state["summary"]["p0_b10_decision"], "STOP_MATCHED_NARY_EQUIVALENT")
        self.assertTrue(self.state["p0_offline_qualification"]["policy"]["method_result_from_offline_qualification_forbidden"])
        self.assertEqual(self.state["summary"]["discussion_ready"], 20)
        self.assertEqual(self.state["summary"]["discussion_target"], 20)
        self.assertTrue(self.state["summary"]["final_ready"])
        disabled = [item for item in self.state["components"] if item["status"] == "intentionally-disabled"]
        self.assertEqual(len(disabled), 1)


if __name__ == "__main__":
    unittest.main()
