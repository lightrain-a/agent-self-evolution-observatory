from __future__ import annotations

import copy
import unittest
from pathlib import Path

from .evidence_integrity import audit_claim_chain, build_evidence_integrity_state
from .experiment_value_scheduler import build_experiment_value_scheduler
from .external_system_learning import build_external_system_learning_state
from .failure_asset_library import build_failure_asset_library
from .p0_common import load_json
from .literature_retrieval_audit import build_literature_retrieval_audit
from .paper_design_contract import audit_paper_design_contract, build_paper_first_workflow_state
from .protocol_validity import audit_protocol_validity
from .research_capability_registry import build_research_capability_registry
from .research_system_replay import build_research_system_replay
from .scientific_meta_trace import build_scientific_meta_trace


class ResearchLearningLoopTest(unittest.TestCase):
    def config(self) -> dict:
        return load_json(Path(__file__).with_name("p0_a1_confirm_config.json"))

    def test_capability_registry_is_typed_and_least_privilege(self) -> None:
        state = build_research_capability_registry()
        self.assertGreaterEqual(state["summary"]["capabilities"], 9)
        self.assertTrue(state["policy"]["capabilities_are_declared_not_prompt_inferred"])
        self.assertTrue(state["policy"]["least_capable_sufficient_interface_is_preferred"])
        self.assertTrue(state["policy"]["model_or_tool_routing_cannot_escalate_scientific_authority"])
        by_id = {row["id"]: row for row in state["capabilities"]}
        self.assertEqual(by_id["gpu-experiment"]["authority"], "execution-only")
        self.assertEqual(by_id["ai-consultation"]["authority"], "advisory-only")
        self.assertIn("literature-relation-search", by_id)
        self.assertIn("BM25", state["retrieval_router_contract"]["simple_first"])

    def test_literature_audit_separates_deep_wide_relation_and_claim_modes(self) -> None:
        state = build_literature_retrieval_audit({"summary": {"nodes": 100, "edges": 200}}, {"statistics": {"paper_count": 80}})
        self.assertEqual(state["summary"]["retrieval_modes"], 4)
        self.assertEqual(state["summary"]["benchmark_status"], "spec-ready-not-yet-scored")
        self.assertTrue(state["policy"]["deep_and_wide_retrieval_are_distinct_capabilities"])
        self.assertTrue(state["policy"]["citation_verifier_must_be_named_versioned_and_calibrated"])
        self.assertFalse(state["retrieval_qualification"]["benchmark_claim_authority"])

    def test_evidence_integrity_routes_claim_types_and_calibrates_verifier(self) -> None:
        state = build_evidence_integrity_state()
        self.assertEqual(state["summary"]["claim_types"], 5)
        self.assertEqual(state["summary"]["verifier_calibration_status"], "spec-ready-not-yet-calibrated")
        self.assertTrue(state["policy"]["uncalibrated_verifier_cannot_be_treated_as_ground_truth"])
        audit = audit_claim_chain({
            "claim_type": "numeric-result",
            "claim_text": "Accuracy improves by 3pp.",
            "artifact_kinds": ["evaluator-log", "metric-table", "run-provenance"],
        })
        self.assertTrue(audit["passed"])
        broken = audit_claim_chain({"claim_type": "citation", "claim_text": "Prior work supports X.", "artifact_kinds": ["primary-source"]})
        self.assertFalse(broken["passed"])
        self.assertIn("missing-artifact:passage-anchor", broken["blockers"])

    def test_paper_first_contract_orders_novelty_method_plan_before_pilot(self) -> None:
        config = copy.deepcopy(self.config())
        self.assertFalse(audit_paper_design_contract(config)["passed"])
        config["pre_experiment"]["paper_design"] = {
            "novelty": {
                "paper_problem": "a paper-level problem",
                "closest_work": [{"identity": "nearest", "difference": "materially different mechanism", "source_ref": "primary-source"}],
                "novelty_axis": "mechanism",
                "contribution_claim": "a distinct publishable contribution",
                "irreducible_difference": "cannot be reduced to the strongest matched simplification",
                "collision_status": "reviewed",
            },
            "method": {
                "method_name": "paper-first-method",
                "core_mechanism": "mechanism designed before implementation",
                "novelty_to_method_mapping": [{"novelty": "mechanism", "component": "core"}],
                "components": ["core"],
                "strongest_simplification": "matched simple baseline",
                "method_change_rule": "core changes return to novelty/method review",
            },
            "experiment_blueprint": {
                "claim_experiment_matrix": [{"claim_id": "C1", "claim": "core contribution", "local_test": "minimal falsifier", "full_test": "frozen full matrix", "metric": "primary metric", "strongest_baseline": "matched baseline"}],
                "local_validation_scope": "minimal local validation",
                "full_experiment_scope": "all main tables, ablations, replication, efficiency",
                "baseline_matrix": ["matched baseline"],
                "ablation_matrix": ["remove core"],
                "freeze_rule": "freeze method and blueprint before full experiment",
                "experimental_integrity": {
                    "model_and_inference": "freeze model/checkpoint/temperature before outcomes",
                    "prompt_tool_policy": "freeze prompt scaffold and tool/search policy",
                    "task_sample_split": "freeze train/local/hidden splits",
                    "metric_analysis_plan": "freeze metric, aggregation, and statistical test",
                    "randomness_replication_plan": "freeze seeds/replicates and stochastic-agent variance analysis",
                    "stopping_exclusion_rules": "freeze stopping and exclusion rules",
                    "allowed_adaptations": "only implementation repair; core changes create a new contract",
                    "hidden_evaluation_access_policy": "hidden answers and benchmark pages are denied during evaluation",
                },
            },
        }
        audit = audit_paper_design_contract(config)
        self.assertTrue(audit["passed"], audit.get("blockers"))
        workflow = build_paper_first_workflow_state({"cards": [{"paper_design_prerequisite": audit}]})
        self.assertTrue(workflow["policy"]["local_validation_is_for_falsification_not_method_discovery"])
        self.assertTrue(workflow["policy"]["method_change_after_local_validation_invalidates_full_experiment_authority"])
        self.assertEqual(workflow["summary"]["paper_design_passed"], 1)

    def test_protocol_validity_contract(self) -> None:
        audit = audit_protocol_validity(self.config())
        self.assertTrue(audit["passed"], audit.get("blockers"))
        self.assertFalse(audit["is_formal_gate"])
        self.assertEqual(len(audit["checks"]), 7)

    def test_protocol_shortcut_failure_blocks(self) -> None:
        config = copy.deepcopy(self.config())
        config["pre_experiment"]["protocol_validity"]["shortcut_audit"]["passed"] = False
        audit = audit_protocol_validity(config)
        self.assertFalse(audit["passed"])
        self.assertIn("protocol-check-failed:shortcut_audit", audit["blockers"])

    def test_future_persistent_update_requires_effect_realization_without_retroactive_breakage(self) -> None:
        legacy = audit_protocol_validity(self.config())
        self.assertTrue(legacy["passed"])
        self.assertFalse(legacy["applies_to_persistent_update"])
        self.assertEqual(len(legacy["required_checks"]), 7)

        future = copy.deepcopy(self.config())
        future["pre_experiment"]["protocol_validity"]["applies_to_persistent_update"] = True
        missing = audit_protocol_validity(future)
        self.assertFalse(missing["passed"])
        self.assertIn("protocol-check-missing:post_update_effect_realization", missing["blockers"])

        future["pre_experiment"]["protocol_validity"]["post_update_effect_realization"] = {
            "passed": True,
            "evidence": "The updated policy revisits the frozen full decision context and executes the intended state-action intervention.",
        }
        passed = audit_protocol_validity(future)
        self.assertTrue(passed["passed"], passed.get("blockers"))
        self.assertTrue(passed["applies_to_persistent_update"])
        self.assertEqual(len(passed["required_checks"]), 8)

    def test_failure_assets_preserve_scientific_layer(self) -> None:
        state = {"nodes": [
            {"idea_id": "a", "diagnosis": "no-label-variation", "diagnosis_layer": "experiment", "artifact_dir": "/a"},
            {"idea_id": "b", "diagnosis": "matched-simplification-tie", "diagnosis_layer": "scientific-boundary", "artifact_dir": "/b"},
        ]}
        library = build_failure_asset_library(state, {"summary": {"matched_simplification_stops": 3, "substrate_stops": 2}})
        self.assertEqual(library["summary"]["assets"], 2)
        by_diag = {row["diagnosis"]: row for row in library["assets"]}
        self.assertEqual(by_diag["no-label-variation"]["affected_layer"], "experiment")
        self.assertEqual(by_diag["matched-simplification-tie"]["affected_layer"], "method-realization")
        self.assertEqual(by_diag["no-label-variation"]["memory_scope"], "institutional-research-memory")
        self.assertEqual(by_diag["no-label-variation"]["reuse_effectiveness"]["status"], "not-yet-measured")

    def test_scienceworld_scope_lesson_is_institutional_asset_not_parent_evidence(self) -> None:
        state = {"nodes": []}
        post_c2 = {
            "scienceworld_scope_evidence": {
                "f0_decision": "SYMMETRIC_F0_HOLD",
                "f0_sha256": "f0-hash",
                "diagnosis_sha256": "diag-hash",
                "scope_refinement_candidate": "Require post-update full decision-context recurrence and intended intervention realization.",
                "principle_authority": "No retrospective principle certificate may be fabricated.",
                "relationship_to_current_paper": "Cross-surface protocol lesson only; no rescue authority.",
            }
        }
        library = build_failure_asset_library(state, {"summary": {}}, post_c2)
        self.assertEqual(library["summary"]["assets"], 1)
        asset = library["assets"][0]
        self.assertEqual(asset["diagnosis"], "decision-context-support-mismatch")
        self.assertEqual(asset["affected_layer"], "operationalization")
        self.assertEqual(asset["memory_scope"], "institutional-research-memory")
        self.assertEqual(asset["source_decision"], "SYMMETRIC_F0_HOLD")
        self.assertFalse(asset["parent_evidence_for_current_paper"])
        self.assertFalse(asset["can_authorize_current_paper"])
        self.assertIn("core-principle failure", asset["does_not_imply"])

    def test_value_scheduler_prefers_cheap_decisive_falsifier(self) -> None:
        iteration = {"nodes": [{"idea_id": "a", "repair_children": [
            {"operator": "optimization-extension", "child": "train-longer", "changed_variable": "steps", "precondition": "curve not converged"},
            {"operator": "disagreement-mining", "child": "mine-disagreement", "changed_variable": "cases", "precondition": "find disagreement"},
        ]}]}
        scheduler = build_experiment_value_scheduler(iteration, {"principles": [{"idea_id": "a"}]})
        self.assertEqual(scheduler["ranking"][0]["operator"], "disagreement-mining")
        self.assertFalse(scheduler["ranking"][0]["execution_authorized"])

    def test_meta_trace_keeps_raw_trace_separate(self) -> None:
        cert = {"passed": True, "principle_id": "p1", "contract": {"mechanism": "m", "predictions": [{"id": "P"}]}}
        pre = {"cards": [{"idea_id": "a", "blockers": ["baseline-floor"], "principle_certificate_prerequisite": cert}]}
        principle = {"adjudications": [{"principle_id": "p1", "verdict": "EXPERIMENT_DESIGN_REPAIR", "scientific_belief_target": "none"}]}
        iteration = {"nodes": [{"idea_id": "a", "diagnosis": "substrate-degenerate", "repair_children": []}]}
        meta = build_scientific_meta_trace(pre, principle, iteration, {"summary": {"launchable": 0}})
        self.assertEqual(meta["summary"]["principles"], 1)
        self.assertEqual(meta["principles"][0]["next_uncertainty"], "baseline-floor")
        self.assertTrue(meta["policy"]["raw_execution_trace_is_not_scientific_state"])
        self.assertTrue(meta["policy"]["active_scientific_state_is_separate_from_institutional_memory"])
        self.assertTrue(meta["policy"]["cross_surface_evidence_requires_explicit_parent_edge_before_entering_active_scientific_state"])
        self.assertFalse(meta["memory_scopes"]["active_scientific_state"]["time_decay_allowed"])
        self.assertTrue(meta["memory_scopes"]["institutional_research_memory"]["time_decay_allowed"])

    def test_replay_guards_protocol_invalid_negative(self) -> None:
        config = self.config()
        cert = {"passed": True, "contract": config["pre_experiment"]["principle_certificate"]}
        replay = build_research_system_replay({"cards": [{"principle_certificate_prerequisite": cert}]})
        self.assertEqual(replay["summary"]["failed"], 0)
        by_id = {row["case_id"]: row for row in replay["cases"]}
        self.assertEqual(by_id["protocol-invalid-negative"]["actual"], "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED")
        self.assertEqual(by_id["registered-contradiction"]["actual"], "REGISTERED_PREDICTION_REJECTED_COUNTEREXPLANATION_REQUIRED")
        self.assertEqual(by_id["counter-explained-dead-end"]["actual"], "PRINCIPLE_DEAD_END_CERTIFIED")
        self.assertEqual(replay["paper_scale_reproduction"]["status"], "spec-ready-not-yet-run")

    def test_external_system_intake_requires_gap_test(self) -> None:
        state = build_external_system_learning_state()
        self.assertTrue(state["policy"]["every_candidate_design_requires_local_gap_test"])
        self.assertGreaterEqual(state["summary"]["systems_reviewed"], 10)
        self.assertGreaterEqual(state["summary"]["adopted"], 15)
        self.assertEqual(state["summary"]["next_backlog"], 1)
        self.assertEqual([row["system"] for row in state["next_backlog"]],["SAGE-MHFA"])
        mhfa=state["next_backlog"][0]["local_gap_test"]
        self.assertEqual(mhfa["verdict"],"support-insufficient")
        self.assertLess(mhfa["available_individual_failure_assets"],mhfa["minimum_replay_cases"])
        eurek=next(row for row in state["designs"] if row["system"]=="EurekAgent")
        self.assertEqual(eurek["local_gap_test"]["verdict"],"gap-confirmed-and-closed")
        self.assertIn("active experiment authority",eurek["local_gap_test"]["after"])


if __name__ == "__main__":
    unittest.main()
