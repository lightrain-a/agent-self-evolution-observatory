#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "research_pipeline"
FRESH = PIPELINE / "strategy_reopen_c01_fresh_primary_delta.json"
OBJECT = PIPELINE / "strategy_reopen_c01_scientific_object.json"
CLOSEST = PIPELINE / "strategy_reopen_c01_closest_work_review.json"
EXCLUSION = PIPELINE / "strategy_reopen_c01_exclusion_audit.json"
SAME_SUBSTRATE = PIPELINE / "strategy_reopen_c01_same_substrate_qualification.json"
S0 = PIPELINE / "strategy_reopen_c01_s0_metadata_inventory.json"
S0_RECHECK = PIPELINE / "strategy_reopen_c01_s0_public_provenance_recheck.json"
ANNOTATION_PROTOCOL = PIPELINE / "strategy_reopen_c01_annotation_reconstruction_protocol.json"
S0_RELEASE = PIPELINE / "strategy_reopen_c01_s0_independent_reconstruction_release.json"
F0 = PIPELINE / "strategy_reopen_c01_bounded_falsifier_design.json"
TRANSACTION = PIPELINE / "strategy_reopen_c01_candidate_replenishment_transaction.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class StrategyReopenC01ScientificObjectTest(unittest.TestCase):
    def test_source_side_object_is_zero_authority_and_not_projected(self) -> None:
        fresh, obj, closest, exclusion, same_substrate, f0 = map(load, (FRESH, OBJECT, CLOSEST, EXCLUSION, SAME_SUBSTRATE, F0))
        self.assertEqual({fresh["candidate_id"], obj["candidate_id"], closest["candidate_id"], exclusion["candidate_id"], same_substrate["candidate_id"], f0["candidate_id"]}, {"STRATEGY-REOPEN-C01"})
        self.assertEqual(obj["status"], "PRE_RESEARCHITEM_PROBLEM_FROZEN_SUBSTRATE_QUALIFICATION_HOLD")
        self.assertEqual(closest["status"], "PASS_PROVISIONAL_IDENTIFIABILITY_RESIDUAL_ZERO_AUTHORITY")
        self.assertEqual(f0["status"], "DESIGN_FROZEN_EXACT_REPLAY_SUPPORT_HOLD")
        self.assertEqual(
            obj["projection_policy"],
            {
                "frontend": False,
                "pre_researchitem_candidate": False,
                "research_item": False,
                "paper_state": False,
                "reason": "Source-side object freeze is deliberately upstream of Problem-Gate PASS and canonical pre-ResearchItem publication.",
            },
        )
        self.assertEqual(exclusion["status"], "PASS_DISTINCT_SOURCE_SIDE_OBJECT_ZERO_AUTHORITY")
        self.assertEqual(exclusion["canonical_exclusion_bindings"]["closed_basin_source"]["closed_basin_count"], 43)
        self.assertEqual(exclusion["canonical_exclusion_bindings"]["terminal_stop_source"]["terminal_stopped_research_item_count"], 72)
        self.assertEqual(exclusion["rsi_distinctness_witness"]["decision"], "DISTINCT_SCIENTIFIC_OBJECT_NOT_RSI_REOPEN")
        self.assertEqual(same_substrate["status"], "HOLD_EXACT_SOURCE_NATIVE_REPLAY_NOT_YET_QUALIFIED")
        self.assertEqual(same_substrate["current_decision"], "PATH_DEFINED_REMAIN_SUPPORT_HOLD")
        self.assertFalse(same_substrate["execution_authorized"])
        self.assertEqual([row["gate"] for row in same_substrate["qualification_path"]], ["S0_METADATA_ONLY_INVENTORY", "S1_PREFIX_MATERIALIZATION", "S2_SOURCE_NATIVE_RUNTIME_REPLAY", "S3_FORK_INDEPENDENCE_AND_INFORMATION_PARITY", "S4_UNIT_FREEZE", "S5_BOUNDED_F0_RELEASE"])
        for state in (fresh, obj, closest, exclusion, same_substrate, f0):
            self.assertTrue(state["authority"])
            self.assertFalse(any(state["authority"].values()))

        for public_state in (
            ROOT / "generated" / "pre-researchitem-candidates.json",
            ROOT / "generated" / "research-items.json",
            ROOT / "generated" / "paper-registry.json",
        ):
            self.assertNotIn("STRATEGY-REOPEN-C01", public_state.read_text(encoding="utf-8"))

    def test_scientific_object_matches_problem_contract_fields(self) -> None:
        obj = load(OBJECT)
        scientific = obj["scientific_object"]
        required = {
            "estimand",
            "comparator",
            "endpoint",
            "same_information_reducer",
            "reducer_predicted_effect",
            "prespecified_stop_rule",
            "registered_claim_boundary",
            "required_evidence",
            "forbidden_interpretations",
        }
        self.assertTrue(required <= set(scientific))
        self.assertEqual(obj["discovery_primitive"], "IDENTIFIABILITY_GAP")
        self.assertIn("recognition-positive", scientific["estimand"])
        self.assertIn("generic reflection", scientific["comparator"])
        self.assertIn("strategy-family", scientific["endpoint"])
        self.assertIn("ordinary replanning/reflection salience", scientific["same_information_reducer"])
        self.assertIn("STOP", scientific["prespecified_stop_rule"])
        self.assertGreaterEqual(len(scientific["required_evidence"]), 7)
        self.assertGreaterEqual(len(scientific["forbidden_interpretations"]), 8)

        controls = obj["required_controls"]
        self.assertEqual(
            set(controls),
            {
                "same_information",
                "generic_target_rubric_equivalent",
                "direct_existing_artifact",
                "leave_one_context_out",
                "adversarial_negative",
            },
        )
        self.assertFalse(obj["next_gate"]["execution_authorized"])
        self.assertEqual(obj["next_gate"]["name"], "EXACT_TRACE_PREFIX_AND_RUNTIME_SUPPORT_QUALIFICATION")

    def test_fresh_primary_is_new_search_delta_not_ingestion_authority(self) -> None:
        fresh = load(FRESH)
        self.assertEqual(fresh["search_primitive"], "IDENTIFIABILITY_GAP")
        self.assertEqual(fresh["primary_source"]["ref"], "arXiv:2608.19072")
        self.assertFalse(fresh["canonical_primary_evidence_presence"]["present_in_generated_paper_first_primary_evidence_state_at_base"])
        self.assertFalse(fresh["public_support_artifacts"]["bulk_download_authorized"])
        self.assertFalse(fresh["public_support_artifacts"]["proxy_reproduction_authorized"])
        self.assertEqual(len(fresh["primary_source"]["grounded_findings"]), 4)
        self.assertEqual(
            {row["id"] for row in fresh["primary_source"]["grounded_findings"]},
            {
                "F1_STRATEGY_CHANGES_RARE",
                "F2_STRATEGY_ADVICE_NOT_UPTAKEN",
                "F3_PRETRAINING_REVISION_CAPACITY_EXISTS",
                "F4_OBSERVATIONAL_PROXY_INCOMPLETE",
            },
        )

        primary = load(ROOT / "generated" / "paper-first-primary-evidence-state.json")
        self.assertTrue(all(row.get("ref") != "arXiv:2608.19072" for row in primary.get("records", [])))

    def test_closest_work_fails_broad_replanning_claim_but_preserves_narrow_gate(self) -> None:
        closest = load(CLOSEST)
        self.assertEqual(closest["broad_claim"]["decision"], "NOVELTY_FAIL")
        self.assertEqual(closest["direct_source_boundary"]["candidate_residual"], "same-information recognition-versus-reopening decomposition")
        self.assertEqual(closest["strongest_same_information_reduction"]["name"], "generic reflection/replanning salience")
        self.assertTrue(closest["strongest_same_information_reduction"]["stop_priority"])
        reducers = {row["name"] for row in closest["direct_existing_artifact_reducers"]}
        self.assertTrue(
            {
                "progress-stall / patience trigger",
                "scheduled reconsideration",
                "generic critic/replan prompt",
                "local decision-menu placebo",
            }
            <= reducers
        )
        self.assertTrue(closest["nonreducibility_gate"]["hold"].startswith("HOLD rather than STOP"))
        self.assertEqual(closest["closest_work_decision"], "PASS_PROVISIONAL_DIRECT_RESIDUAL_REQUIRES_MATCHED_F0")

    def test_s0_metadata_inventory_fails_closed_before_payload_or_provider_access(self) -> None:
        s0 = load(S0)
        self.assertEqual(s0["stage"], "S0_METADATA_ONLY_INVENTORY")
        self.assertEqual(s0["status"], "HOLD_PAPER_CORPUS_REVISION_AND_ANNOTATION_PROVENANCE_NOT_CLOSED")
        checks = {row["id"]: row["status"] for row in s0["s0_checks"]}
        self.assertEqual(checks["S0A_PUBLIC_DATASET_EXISTS"], "PASS")
        self.assertEqual(checks["S0B_PATH_IDENTIFIERS_EXIST"], "PASS")
        self.assertEqual(checks["S0C_MULTI_CONTEXT_METADATA_HEADROOM"], "PASS")
        self.assertEqual(checks["S0D_EXACT_PAPER_CORPUS_REVISION_PIN"], "HOLD")
        self.assertEqual(checks["S0E_SOURCE_STRATEGY_ANNOTATION_PROVENANCE"], "HOLD")
        self.assertEqual(checks["S0F_EXACT_RUNTIME_REPLAY"], "NOT_EVALUATED_AT_S0")
        self.assertEqual(s0["decision"]["overall"], "HOLD_BEFORE_S1_PREFIX_MATERIALIZATION")
        self.assertEqual(s0["public_provenance_recheck"]["status"], "HOLD_AUTHORITATIVE_PAPER_SNAPSHOT_OR_RECONSTRUCTABLE_ANNOTATION_REQUIRED")
        recheck = load(S0_RECHECK)
        self.assertEqual(recheck["status"], "HOLD_AUTHORITATIVE_PAPER_SNAPSHOT_OR_RECONSTRUCTABLE_ANNOTATION_REQUIRED")
        self.assertEqual(recheck["decision"]["overall"], "KEEP_S0_SUPPORT_HOLD")
        self.assertFalse(recheck["decision"]["scientific_failure"])
        self.assertEqual(len(recheck["only_valid_reopen_paths"]), 2)
        self.assertFalse(any(recheck["authority"].values()))
        self.assertFalse(s0["decision"]["bulk_download_authorized"])
        self.assertFalse(s0["decision"]["prefix_materialization_authorized"])
        self.assertFalse(s0["decision"]["provider_calls_authorized"])
        self.assertFalse(any(s0["authority"].values()))

    def test_independent_annotation_protocol_closes_s0_definition_without_authorizing_s1(self) -> None:
        protocol = load(ANNOTATION_PROTOCOL)
        release = load(S0_RELEASE)
        self.assertEqual(protocol["status"], "FROZEN_BEFORE_TRAJECTORY_PAYLOAD_ACCESS_ZERO_AUTHORITY")
        self.assertEqual(protocol["source_definition"]["source_state"], "s=(k,d,g)")
        self.assertEqual([row["label"] for row in protocol["k_training_family"]["labels"][:5]], ["FULL_SFT", "PEFT", "RL", "PREFERENCE_OPTIMIZATION", "DISTILLATION"])
        self.assertTrue(protocol["d_data_source"]["missing_rule"].endswith("never imputed."))
        self.assertTrue(protocol["strategy_transition_rule"]["no_imputation"])
        self.assertGreaterEqual(protocol["reliability_gate_before_unit_selection"]["minimum_exact_agreement_k"], 0.9)
        self.assertTrue(protocol["f0_endpoint_constraints"]["annotator_blind_to_arm"])
        self.assertFalse(any(protocol["authority"].values()))
        self.assertEqual(release["status"], "PASS_S0_INDEPENDENT_RECONSTRUCTION_REALIZATION_FROZEN_S1_AUTHORITY_HOLD")
        self.assertFalse(release["paper_reproduction_claim"])
        self.assertEqual(release["independent_realization"]["pinned_revision"], "39d3fcd794df51c062c8bd3b7f8523ba707aaeb3")
        self.assertEqual(release["independent_realization"]["annotation_protocol_sha256"], hashlib.sha256(ANNOTATION_PROTOCOL.read_bytes()).hexdigest())
        self.assertEqual(release["decision"]["overall"], "S0_COMPLETE_VIA_INDEPENDENT_RECONSTRUCTION_PATH")
        self.assertEqual(release["decision"]["support_state"], "HOLD_S1_EXPLICIT_SUPPORT_DOWNLOAD_AUTHORITY")
        self.assertFalse(release["next_gate"]["currently_authorized"])
        self.assertFalse(any(release["authority"].values()))

    def test_replenishment_transaction_binds_strict_zero_authority_gate_artifacts(self) -> None:
        tx = load(TRANSACTION)
        self.assertEqual(tx["status"], "STARTED_SOURCE_OBJECT_FROZEN_SUPPORT_HOLD_ZERO_AUTHORITY")
        self.assertEqual(tx["trigger"]["canonical_active_research_items"], 0)
        self.assertEqual(tx["trigger"]["canonical_live_pre_researchitem_candidates"], ["MEMENTO-JOINT-BOUNDARY-CONTROL"])
        self.assertTrue(all(tx["strict_acceptance_contract"].values()))
        self.assertEqual(tx["gate_results"]["problem_gate"], "NOT_RUN_NOT_PASSED")
        self.assertEqual(tx["candidate_disposition"]["decision"], "ACCEPT_INTO_SOURCE_SIDE_QUALIFICATION_QUEUE_ONLY")
        self.assertFalse(tx["candidate_disposition"]["canonical_active_slot_consumed"])
        self.assertFalse(tx["candidate_disposition"]["canonical_pre_researchitem_slot_consumed"])
        self.assertFalse(any(tx["authority"].values()))
        for row in tx["artifact_bindings"]:
            path = ROOT / row["path"]
            self.assertTrue(path.is_file(), row["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"], row["path"])

    def test_f0_is_bounded_same_information_and_cannot_auto_promote(self) -> None:
        f0 = load(F0)
        units = f0["unit_construction"]
        budget = f0["budget"]
        self.assertEqual(units["positive_units"], 12)
        self.assertEqual(units["positive_task_families_min"], 3)
        self.assertEqual(units["adversarial_negative_units"], 6)
        self.assertEqual(
            [row["id"] for row in f0["positive_continuation_arms"]],
            ["A_AUTONOMOUS", "B_GENERIC_REFLECTION", "C_STRATEGY_REOPEN_DECISION", "D_LOCAL_DECISION_PLACEBO"],
        )
        self.assertEqual(f0["negative_control_arms"], ["B_GENERIC_REFLECTION", "C_STRATEGY_REOPEN_DECISION"])
        self.assertEqual(budget["recognition_probe_calls"], 12)
        self.assertEqual(budget["positive_continuation_episodes"], 48)
        self.assertEqual(budget["negative_control_episodes"], 12)
        self.assertEqual(budget["maximum_provider_calls_after_support_pass"], 72)
        self.assertFalse(budget["gpu_required"])
        self.assertFalse(budget["full_training_execution_in_f0"])
        self.assertFalse(f0["substrate"]["proxy_backbone_allowed"])
        self.assertFalse(f0["substrate"]["bulk_dataset_download_before_support_gate"])
        self.assertEqual(f0["object_binding"]["exclusion_audit_path"], "research_pipeline/strategy_reopen_c01_exclusion_audit.json")
        self.assertEqual(f0["object_binding"]["same_substrate_qualification_path"], "research_pipeline/strategy_reopen_c01_same_substrate_qualification.json")
        self.assertTrue(f0["support_qualification_before_any_provider_call"]["required"])
        self.assertEqual(f0["support_qualification_before_any_provider_call"]["canonical_gate_path"], "research_pipeline/strategy_reopen_c01_same_substrate_qualification.json")
        self.assertEqual(f0["support_qualification_before_any_provider_call"]["on_failure"], "HOLD_EXACT_SOURCE_NATIVE_REPLAY_SUPPORT_INSUFFICIENT")
        self.assertIn("C-only", f0["decision_rule"]["go_provisional"])
        self.assertTrue(f0["decision_rule"]["full_experiment_unlock"].startswith("GO_PROVISIONAL plus a separate Problem-Gate adjudication"))
        self.assertEqual(f0["decision"], "DESIGN_ONLY_NO_EXECUTION_AUTHORITY")


if __name__ == "__main__":
    unittest.main()
