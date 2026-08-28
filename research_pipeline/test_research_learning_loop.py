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
from .paper_design_contract import audit_contribution_archetype, audit_paper_design_contract, build_paper_first_workflow_state
from .protocol_validity import audit_protocol_validity
from .research_capability_registry import (
    build_research_capability_registry,
    build_skill_admission_certificate,
    route_research_skills,
)
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

    def test_skill_admission_and_least_privilege_routing_are_zero_authority(self) -> None:
        base = {
            "skill_version": "1.2.0", "source_repository": "https://example.org/research-skills.git",
            "commit_sha": "a" * 40, "license": "MIT", "maintainer": "maintainer",
            "data_access_level": "VERIFIED_ONLY", "execution_mode": "DETERMINISTIC",
            "external_network_access": False, "filesystem_write_access": False, "code_execution": False,
            "gpu_access": False, "secret_access": False, "expected_artifacts": ["audit.json"],
            "smoke": {"passed": True, "artifact_ref": "smoke:sha256:" + "b" * 64},
        }
        citation = build_skill_admission_certificate({**base, "skill_id": "citation-check", "capability_types": ["citation"]})
        broad = build_skill_admission_certificate({**base, "skill_id": "broad-review", "capability_types": ["citation", "reviewing"], "external_network_access": True})
        self.assertEqual(citation["status"], "SKILL_QUALIFIED")
        self.assertFalse(citation["scientific_authority"])
        route = route_research_skills({"capability_types": ["citation"], "max_data_access_level": "VERIFIED_ONLY"}, [broad, citation])
        self.assertEqual(route["status"], "SKILL_ROUTE_READY")
        self.assertEqual(route["selected_skills"][0]["skill_id"], "citation-check")
        self.assertFalse(route["experiment_authority"])
        held = build_skill_admission_certificate({**base, "skill_id": "bad", "capability_types": ["citation"], "commit_sha": "latest"})
        self.assertEqual(held["status"], "SKILL_ADMISSION_HOLD")

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
        self.assertEqual(workflow["schema_version"], "1.1")
        self.assertTrue(workflow["policy"]["local_validation_is_for_falsification_not_method_discovery"])
        self.assertTrue(workflow["policy"]["method_change_after_local_validation_invalidates_full_experiment_authority"])
        self.assertTrue(workflow["policy"]["paper_development_quality_v1_distinguishes_scientific_closure_from_manuscript_maturity"])
        self.assertTrue(workflow["policy"]["current_initial_drafts_are_not_retroactively_demoted_by_new_development_guidance"])
        self.assertEqual(workflow["summary"]["paper_design_passed"], 1)
        self.assertEqual(workflow["summary"]["paper_development_initial_draft_guidance"], 1)

    def test_insight_dominant_archetype_requires_full_insight_evidence_ladder(self) -> None:
        novelty = {
            "contribution_archetype": "INSIGHT_DOMINANT",
            "primary_contribution_type": "insight",
            "problem_importance": "persistent reuse failures affect reliable long-horizon agents",
            "under_explained_observation": "locally correct experience can become harmful after context changes",
            "missing_insight": "reuse validity depends on current applicability, not historical correctness alone",
            "minimal_decisive_test": "hold experience fixed and cross applicability context",
            "minimal_sufficient_intervention": "an applicability check before reuse",
            "mechanism_predictions": "harm concentrates on applicability flips and vanishes when the check rejects reuse",
            "alternative_explanation": "recency/frequency and generic confidence controls",
            "contribution_attribution": {"layers": {
                "problem": {"status": "NEW", "claim": "systematic applicability-flip failure"},
                "insight": {"status": "NEW", "claim": "applicability mediates reuse validity"},
                "method": {"status": "KNOWN", "claim": "simple applicability filter"},
            }},
        }
        blueprint = {"insight_evidence_ladder": [
            {"stage": "E1", "claim_id": "C1", "test": "establish phenomenon"},
            {"stage": "E2", "claim_id": "C1", "test": "matched context controls"},
            {"stage": "E3", "claim_id": "C2", "test": "predict applicability flips", "strongest_baseline": "recency/frequency"},
            {"stage": "E4", "claim_id": "C2", "test": "minimal applicability intervention", "strongest_baseline": "generic confidence filter"},
            {"stage": "E5", "claim_id": "C2", "test": "strongest alternative explanation", "strongest_baseline": "same-information threshold"},
            {"stage": "E6", "claim_id": "C3", "test": "cross-task/model generalization"},
            {"stage": "E7", "claim_id": "C4", "test": "measure boundary conditions"},
        ]}
        audit = audit_contribution_archetype(novelty, blueprint)
        self.assertEqual(audit["status"], "PASS_CONTRIBUTION_ARCHETYPE")
        self.assertEqual(audit["archetype"], "INSIGHT_DOMINANT")
        self.assertEqual(len(audit["insight_evidence_ladder"]), 7)
        self.assertTrue(audit["method_simplicity_is_not_a_blocker"])
        self.assertFalse(audit["scientific_authority"])

        broken = copy.deepcopy(blueprint)
        broken["insight_evidence_ladder"] = broken["insight_evidence_ladder"][:-1]
        blocked = audit_contribution_archetype(novelty, broken)
        self.assertEqual(blocked["status"], "BLOCK_CONTRIBUTION_ARCHETYPE")
        self.assertIn("insight-evidence-ladder-test-missing:E7", blocked["blockers"])

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

    def test_additional_failure_asset_is_zero_authority_and_scope_bound(self) -> None:
        external = {
            "signature": "experiment_identifiability:reference-instability",
            "idea_id": "aux-negative",
            "diagnosis": "reference-instability",
            "affected_layer": "experiment_identifiability",
            "reusable_precheck": "freeze a stable matched reference before interpreting the endpoint",
            "evidence_ref": "private-data://runs/aux/result.json#sha256=abc",
            "does_not_imply": "core-principle failure",
            "reuse_scope": {"measurement": "matched residual"},
            "last_revalidated": "2026-08-23",
            "scientific_authority": False,
        }
        library = build_failure_asset_library({"nodes": []}, {"summary": {}}, additional_assets=[external])
        self.assertEqual(library["summary"]["assets"], 1)
        asset = library["assets"][0]
        self.assertTrue(asset["external_memory_input"])
        self.assertFalse(asset["scientific_authority"])
        self.assertEqual(asset["affected_layer"], "experiment_identifiability")
        self.assertEqual(asset["reuse_scope"]["measurement"], "matched residual")

    def test_canonical_external_failure_asset_index_includes_v19r003_prechecks(self) -> None:
        from .research_system import _load_external_failure_assets

        assets = _load_external_failure_assets()
        by_signature = {row["signature"]: row for row in assets}
        expected = {
            "operationalization:paid-agent-action-turn-nonexecution",
            "operationalization:semantic-action-observability",
        }
        self.assertTrue(expected.issubset(by_signature))
        for signature in expected:
            row = by_signature[signature]
            self.assertFalse(row["scientific_authority"])
            self.assertEqual(row["affected_layer"], "operationalization")
            self.assertIn("V19R-003", row["idea_id"])
            self.assertTrue(row["reusable_precheck"])
        library = build_failure_asset_library({"nodes": []}, {"summary": {}}, additional_assets=assets)
        compiled = {row["signature"]: row for row in library["assets"]}
        self.assertTrue(expected.issubset(compiled))
        self.assertTrue(all(compiled[signature]["external_memory_input"] for signature in expected))
        self.assertTrue(all(compiled[signature]["scientific_authority"] is False for signature in expected))

    def test_canonical_external_failure_asset_index_includes_c1_b14_preexecution_prechecks(self) -> None:
        from .research_system import _load_external_failure_assets

        assets = _load_external_failure_assets()
        by_signature = {row["signature"]: row for row in assets}
        expected_layers = {
            "reproducibility:fixed-seed-monte-carlo-traversal-order": "reproducibility",
            "operationalization:zero-provider-import-time-credential-coupling": "operationalization",
        }
        self.assertTrue(set(expected_layers).issubset(by_signature))
        for signature, layer in expected_layers.items():
            row = by_signature[signature]
            self.assertFalse(row["scientific_authority"])
            self.assertEqual(row["affected_layer"], layer)
            self.assertIn("B14", row["idea_id"])
            self.assertTrue(row["reusable_precheck"])
            self.assertEqual(row["last_revalidated"], "2026-08-25")
            self.assertIn("private-data://runs/d2-proxy-reward-b14-live-native-transport-20260825", row["evidence_ref"])
        library = build_failure_asset_library({"nodes": []}, {"summary": {}}, additional_assets=assets)
        compiled = {row["signature"]: row for row in library["assets"]}
        self.assertTrue(set(expected_layers).issubset(compiled))
        self.assertTrue(all(compiled[signature]["external_memory_input"] for signature in expected_layers))
        self.assertTrue(all(compiled[signature]["scientific_authority"] is False for signature in expected_layers))

    def test_canonical_external_failure_asset_index_includes_port010_embodiedbench_e0_lessons(self) -> None:
        from .research_system import _load_external_failure_assets

        assets = _load_external_failure_assets()
        by_signature = {row["signature"]: row for row in assets}
        expected_layers = {
            "operationalization:outcome-blind-proxy-transfer-failure": "operationalization",
            "operationalization:source-schema-semantics-assumption": "operationalization",
            "experiment_identifiability:proxy-length-and-capability-nonspecificity": "experiment_identifiability",
        }
        self.assertTrue(set(expected_layers).issubset(by_signature))
        for signature, layer in expected_layers.items():
            row = by_signature[signature]
            self.assertFalse(row["scientific_authority"])
            self.assertEqual(row["affected_layer"], layer)
            self.assertIn("PORT-010-E0", row["idea_id"])
            self.assertEqual(row["last_revalidated"], "2026-08-28")
            self.assertIn("port010-embodiedbench-e0-adjudication-20260828.json", row["evidence_ref"])
            self.assertTrue(row["reusable_precheck"])
        library = build_failure_asset_library({"nodes": []}, {"summary": {}}, additional_assets=assets)
        compiled = {row["signature"]: row for row in library["assets"]}
        self.assertTrue(set(expected_layers).issubset(compiled))
        self.assertTrue(all(compiled[signature]["external_memory_input"] for signature in expected_layers))
        self.assertTrue(all(compiled[signature]["scientific_authority"] is False for signature in expected_layers))

    def test_canonical_external_failure_asset_index_includes_behavior_public_outcome_completeness_lessons(self) -> None:
        from .research_system import _load_external_failure_assets

        assets = _load_external_failure_assets()
        by_signature = {row["signature"]: row for row in assets}
        expected_layers = {
            "experiment_identifiability:public-outcome-completeness-shortfall": "experiment_identifiability",
            "operationalization:missing-as-zero-estimand-drift": "operationalization",
        }
        self.assertTrue(set(expected_layers).issubset(by_signature))
        for signature, layer in expected_layers.items():
            row = by_signature[signature]
            self.assertFalse(row["scientific_authority"])
            self.assertEqual(row["affected_layer"], layer)
            self.assertIn("SUCC-C-BEHAVIOR2025", row["idea_id"])
            self.assertEqual(row["last_revalidated"], "2026-08-28")
            self.assertIn("behavior-formal-goal-coupling-2025-public-outcome-adjudication-20260828.json", row["evidence_ref"])
            self.assertTrue(row["reusable_precheck"])
        library = build_failure_asset_library({"nodes": []}, {"summary": {}}, additional_assets=assets)
        compiled = {row["signature"]: row for row in library["assets"]}
        self.assertTrue(set(expected_layers).issubset(compiled))
        self.assertTrue(all(compiled[signature]["external_memory_input"] for signature in expected_layers))
        self.assertTrue(all(compiled[signature]["scientific_authority"] is False for signature in expected_layers))

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
        self.assertEqual(state["summary"]["next_backlog"], 0)
        self.assertEqual(state["next_backlog"], [])
        replica=next(row for row in state["designs"] if row["system"]=="Replica / Faraday")
        self.assertEqual(replica["status"],"adopted");self.assertEqual(replica["local_gap_test"]["verdict"],"gap-confirmed-and-closed");self.assertIn("3/3",replica["local_gap_test"]["after"])
        ahois=next(row for row in state["designs"] if row["system"]=="AHOIS")
        self.assertEqual(ahois["status"],"adopted");self.assertEqual(ahois["local_gap_test"]["verdict"],"gap-confirmed-and-closed");self.assertIn("20-case",ahois["local_gap_test"]["after"])
        notes=next(row for row in state["designs"] if row["system"]=="Notes2Skills")
        self.assertEqual(notes["status"],"adopted");self.assertEqual(notes["local_gap_test"]["verdict"],"gap-confirmed-and-closed");self.assertIn("30/30",notes["local_gap_test"]["after"])
        sgha=next(row for row in state["designs"] if row["system"]=="SGHA")
        self.assertEqual(sgha["status"],"merged-existing");self.assertEqual(sgha["local_gap_test"]["verdict"],"shadow-gap-closed-live-migration-pending");self.assertIn("30/25/20/15/15/10/5",sgha["local_gap_test"]["after"])
        first=next(row for row in state["designs"] if row["system"]=="FirstResearch")
        self.assertEqual(first["status"],"merged-existing");self.assertIn("minimal decisive test",first["design"])
        scideator=next(row for row in state["designs"] if row["system"]=="Scideator")
        self.assertEqual(scideator["status"],"merged-existing");self.assertEqual(scideator["local_gap_test"]["verdict"],"gap-confirmed-in-shadow");self.assertIn("40-case",scideator["local_gap_test"]["after"])
        sage=next(row for row in state["designs"] if row["system"]=="SAGE-MHFA")
        self.assertEqual(sage["status"],"merged-existing")
        mhfa=sage["local_gap_test"]
        self.assertEqual(mhfa["verdict"],"shadow-registry-installed-prospective-replay-pending")
        self.assertGreaterEqual(mhfa["historical_terminalized_failure_labels"],mhfa["minimum_prospective_replay_cases"])
        self.assertEqual(mhfa["prospective_scored_cases"],0)
        self.assertFalse(mhfa["historical_labels_can_backfill_hypotheses"])
        claw=next(row for row in state["designs"] if row["system"]=="Claw AI Lab")
        self.assertEqual(claw["status"],"adopted");self.assertIn("PAPER cannot write validated evidence",claw["local_gap_test"]["after"])
        co_scientist=next(row for row in state["designs"] if row["system"]=="Google AI co-scientist")
        self.assertEqual(co_scientist["status"],"adopted");self.assertIn("NOT_AUTHORIZED",co_scientist["local_gap_test"]["after"])
        robin=next(row for row in state["designs"] if row["system"]=="Robin")
        self.assertEqual(robin["status"],"adopted");self.assertIn("deterministic metrics remain single-path",robin["local_gap_test"]["after"])
        eurek=next(row for row in state["designs"] if row["system"]=="EurekAgent")
        self.assertEqual(eurek["local_gap_test"]["verdict"],"gap-confirmed-and-closed")
        self.assertIn("active experiment authority",eurek["local_gap_test"]["after"])
        scienceflow=next(row for row in state["designs"] if row["system"]=="ScienceFlow")
        self.assertEqual(scienceflow["local_gap_test"]["verdict"],"gap-confirmed-and-closed")
        self.assertIn("HOLD/STOP/MERGED/PAPER_READY",scienceflow["local_gap_test"]["after"])
        skills=next(row for row in state["designs"] if row["system"].startswith("Research skill ecosystems"))
        self.assertEqual(skills["status"],"merged-existing");self.assertFalse(skills["local_gap_test"]["automatic_skill_installation"]);self.assertEqual(skills["local_gap_test"]["external_runtime_dependencies"],0);self.assertIn("seven local typed skills",skills["local_gap_test"]["after"])
        integrity=next(row for row in state["designs"] if row["system"].startswith("Manuscript integrity skill ecosystems"))
        self.assertEqual(integrity["status"],"merged-existing");self.assertFalse(integrity["local_gap_test"]["experiment_authority"])


if __name__ == "__main__":
    unittest.main()
