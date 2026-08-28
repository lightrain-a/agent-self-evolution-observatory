from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "generated" / "constraint-integration-cross-substrate-proposal-20260828.json"
SCENEEVAL_AUDIT = ROOT / "generated" / "sceneeval500-outcome-blind-constraint-audit-20260828.json"
INDEPENDENT_REVIEW = ROOT / "generated" / "constraint-integration-sceneeval-independent-review-20260828.json"
PREREG_DRAFT = ROOT / "generated" / "sceneeval500-prerequisite-coupling-preregistration-draft-20260828.json"
TOPOLOGY_IMPLEMENTATION = ROOT / "generated" / "sceneeval500-logistic-normal-topology-implementation-preflight-20260828.json"
HSM_PREFLIGHT = ROOT / "generated" / "sceneeval500-hsm-released-output-preflight-20260828.json"
HSM_MANIFEST = ROOT / "generated" / "hsm-sceneeval500-release-manifest-20260828.json"
COLLISION = ROOT / "generated" / "constraint-integration-current-source-collision-review-20260828.json"
LEGO_AUDIT = ROOT / "generated" / "lego-bench-outcome-blind-construct-audit-20260828.json"
PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"

EXPECTED_SCENEEVAL_AUDIT_SHA = "a3eaaa0571d51928e70f0094de1d0d4542211de165d1a196135be55df1247e45"
EXPECTED_REVIEW_SHA = "cb82ab4531dd1a76f05af2f027f3213ffc06b9e771beb45007a9446a55186862"
EXPECTED_PREREG_SHA = "269412b2b0ac270de00d1cca60f4e429ca3b48aae5d62359be073a6095abc365"
EXPECTED_TOPOLOGY_IMPLEMENTATION_SHA = "4021b01498c5d6f18219fb1b3f34c4a77d2ed217f6dfeaba1a49cd7a83bb9f5a"
EXPECTED_HSM_PREFLIGHT_SHA = "75053aea6c84b467431066edd6b9cf9e898cdf013adbe0c571dce16645009348"
EXPECTED_HSM_MANIFEST_SHA = "6475bdd1c73a4b810f4bb6ee03e65be85567d07e33c04a15dc272360a829cd55"
EXPECTED_COLLISION_SHA = "05d985e0b526ce36c545e1f6427cb5d3e7646fa3a8d437f5281e632f34aad278"
EXPECTED_LEGO_AUDIT_SHA = "f8e845bb66d5c3ae897e939bb9877c1ae85e0491955a4d099e45d6f8bd7d868d"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ConstraintIntegrationCrossSubstrateProposalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
        self.audit = json.loads(SCENEEVAL_AUDIT.read_text(encoding="utf-8"))
        self.review = json.loads(INDEPENDENT_REVIEW.read_text(encoding="utf-8"))
        self.prereg = json.loads(PREREG_DRAFT.read_text(encoding="utf-8"))
        self.topology_implementation = json.loads(TOPOLOGY_IMPLEMENTATION.read_text(encoding="utf-8"))
        self.hsm = json.loads(HSM_PREFLIGHT.read_text(encoding="utf-8"))
        self.hsm_manifest = json.loads(HSM_MANIFEST.read_text(encoding="utf-8"))
        self.collision = json.loads(COLLISION.read_text(encoding="utf-8"))
        self.plan = json.loads(PLAN.read_text(encoding="utf-8"))

    def test_proposal_is_noncanonical_zero_execution_authority(self) -> None:
        self.assertEqual(
            self.proposal["status"],
            "ZERO_EXECUTION_AUTHORITY_SCENEEVAL_CORE_IMPLEMENTED_HOLD_CALIBRATION_AND_ACCESS",
        )
        self.assertIsNone(self.proposal["canonical_candidate_id"])
        self.assertEqual(self.proposal["generator_admission"], "PENDING")
        self.assertFalse(self.proposal["scientific_authority"])
        self.assertFalse(self.proposal["execution_authority"])
        self.assertEqual(self.proposal["provider_calls_executed"], 5)
        self.assertEqual(self.proposal["review_provider_completed_voting_calls"], 2)
        self.assertEqual(self.proposal["review_provider_nonvoting_confirmed_calls"], 3)
        self.assertEqual(self.proposal["review_connector_indeterminate_invocations"], 1)
        self.assertEqual(self.proposal["scientific_execution_provider_calls"], 0)
        self.assertEqual(self.proposal["gpu_calls_executed"], 0)
        self.assertFalse(any(self.proposal["authority"].values()))
        self.assertEqual(self.proposal["candidate_generator_suite"]["execution_status"], "NOT_AUTHORIZED")
        self.assertEqual(
            self.proposal["method_intervention"]["status"],
            "DEFERRED_UNTIL_PREREGISTRATION_REVIEW_AND_PRIMARY_COUPLING_PASS",
        )

    def test_port010_hold_is_not_replaced_or_reopened(self) -> None:
        relation = self.proposal["relation_to_port010"]
        self.assertEqual(relation["role"], "HYPOTHESIS_SOURCE_ONLY")
        self.assertEqual(relation["port010_effective_status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual(relation["port010_evidence_review"], "BLOCK_BAKE_IN")
        self.assertFalse(relation["port010_reopen_effect"])
        self.assertTrue(relation["benchmark_replacement_cannot_close_or_reopen_port010"])

        rows = [
            row
            for row in self.plan.get("entries") or []
            if row.get("candidate_id") == "PORT-010"
            and row.get("title") == "Complex-description boundary in end-to-end 3D world construction"
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual((row.get("evidence_review") or {}).get("verdict"), "BLOCK_BAKE_IN")
        adjudication = row["release_change_adjudication"]
        self.assertEqual(adjudication["remaining_reopen_components"], ["per_case_outcomes"])
        for key in (
            "offline_replay_tier_authorized",
            "provider_authority",
            "gpu_authority",
            "scientific_execution_authority",
            "scientific_authority",
        ):
            self.assertFalse(adjudication[key])

    def test_sceneeval_construct_is_content_addressed_outcome_blind_and_count_collision_is_rejected(self) -> None:
        self.assertEqual(sha256_file(SCENEEVAL_AUDIT), EXPECTED_SCENEEVAL_AUDIT_SHA)
        construct = self.proposal["construct_preflight"]
        self.assertEqual(construct["artifact_sha256"], EXPECTED_SCENEEVAL_AUDIT_SHA)
        self.assertEqual(self.audit["source"]["instruction_count"], 500)
        self.assertEqual(self.audit["source"]["difficulty_counts"], {"easy": 150, "medium": 200, "hard": 150})
        exposure = self.audit["outcome_exposure"]
        self.assertFalse(exposure["generated_scene_outputs_read"])
        self.assertFalse(exposure["per_case_metric_outputs_read"])
        self.assertFalse(exposure["published_per_case_baseline_scores_read"])
        self.assertFalse(exposure["selection_conditioned_on_generator_performance"])
        raw = self.audit["constructs"]["raw_total_spec_count"]
        self.assertEqual(raw["disposition"], "DIRECT_DIFFICULTY_LOAD_AXIS_NOT_NOVEL_PRIMARY_OBJECT")
        self.assertAlmostEqual(raw["spearman_with_instruction_words"], 0.939932, places=6)
        self.assertAlmostEqual(raw["spearman_with_authored_difficulty"], 0.861922, places=6)
        entropy = self.audit["constructs"]["constraint_type_entropy"]
        self.assertAlmostEqual(entropy["spearman_with_instruction_words"], 0.269006, places=6)
        self.assertFalse(entropy["may_be_primary_scientific_object"])

    def test_sceneeval_measurement_dependency_dag_is_explicit(self) -> None:
        measurement = self.audit["measurement_dependency_preflight"]
        self.assertTrue(measurement["verified"])
        self.assertTrue(measurement["raw_matching_observable"])
        self.assertEqual(measurement["official_semantic_vlm"], "gpt-4o-2024-08-06")
        self.assertFalse(measurement["local_vlm_substitution_is_official_sceneeval"])
        self.assertTrue(all(measurement["checks"].values()))
        self.assertIn("prerequisite/control", measurement["dependency_dag"]["ObjCount"])
        future = self.audit["future_analysis_contract_if_authorized"]
        self.assertEqual(future["primary_outcome_channels"], ["ObjAttr", "OORel", "OARel"])
        self.assertIn("ObjCount", future["prerequisite_control_channel"])
        self.assertIn("N2", future["null_ladder"])
        self.assertIn("scene-level latent frailty", future["null_ladder"]["N2"])

    def test_strict_sceneeval_panel_is_frozen_before_outcomes(self) -> None:
        panel = self.audit["strict_matched_f0"]
        self.assertFalse(panel["selection_uses_outcomes"])
        self.assertTrue(panel["same_total_spec_count"])
        self.assertTrue(panel["same_authored_difficulty"])
        self.assertEqual(panel["max_instruction_word_difference"], 10)
        self.assertEqual(panel["min_type_entropy_difference_bits"], 0.35)
        self.assertEqual(panel["selected_disjoint_pairs"], 52)
        seen: set[int] = set()
        for pair in panel["pairs"]:
            self.assertLessEqual(pair["word_difference"], 10)
            self.assertGreaterEqual(pair["entropy_difference_bits"], 0.35)
            self.assertNotIn(pair["low_entropy_id"], seen)
            self.assertNotIn(pair["high_entropy_id"], seen)
            seen.update({pair["low_entropy_id"], pair["high_entropy_id"]})

    def test_independent_review_requires_revision_and_records_provider_failures(self) -> None:
        self.assertEqual(sha256_file(INDEPENDENT_REVIEW), EXPECTED_REVIEW_SHA)
        self.assertEqual(self.review["status"], "REVISE_BEFORE_PREREGISTRATION")
        self.assertEqual(len(self.review["voting_reviews"]), 2)
        self.assertTrue(all(row["verdict"] == "REVISE_BEFORE_PREREGISTRATION" for row in self.review["voting_reviews"]))
        self.assertEqual(self.review["consensus"]["identifiability"], "CONDITIONAL_AFTER_MEASUREMENT_REVISION")
        accounting = self.review["provider_accounting"]
        self.assertEqual(accounting["completed_voting_review_calls"], 2)
        self.assertEqual(accounting["confirmed_nonvoting_provider_calls"], 3)
        self.assertEqual(accounting["scientific_execution_provider_calls"], 0)
        self.assertEqual(len(self.review["nonvoting_provider_history"]), 4)
        self.assertFalse(self.review["scientific_authority"])
        self.assertFalse(any(self.review["authority"].values()))

    def test_preregistration_draft_freezes_n2_and_power_but_does_not_clear_execution(self) -> None:
        self.assertEqual(sha256_file(PREREG_DRAFT), EXPECTED_PREREG_SHA)
        model = self.prereg["nested_model_contract"]
        self.assertIn("exchangeable correlation matrix", model["N2_strongest_null"])
        self.assertIn("unstructured 3x3 correlation matrix", model["candidate"])
        self.assertIn("exactly two nonexchangeability degrees of freedom", model["nesting"])
        self.assertEqual(
            self.prereg["measurement_contract"]["stage_D_downstream"]["primary_channels"],
            ["ObjAttr", "OORel", "OARel"],
        )
        self.assertEqual(self.prereg["annotation_availability"]["annotated_all_three_scene_count"], 402)
        interpretation = self.prereg["power_design_preflight"]["design_interpretation"]
        self.assertIn("at least 350", interpretation["confirmatory_sensitivity_target"])
        row = next(
            item
            for item in self.prereg["power_design_preflight"]["worst_case_summary"]
            if item["complete_case_scene_count"] == 350 and item["one_pair_topology_increment"] == 0.2
        )
        self.assertGreaterEqual(row["worst_case_power_across_base_correlations"], 0.8)
        gates = self.prereg["gates_after_this_preflight"]
        self.assertTrue(gates["model_revision_satisfied"])
        self.assertTrue(gates["power_preflight_satisfied"])
        self.assertFalse(gates["formal_preregistration_clear"])
        self.assertFalse(self.prereg["scientific_authority"])
        self.assertFalse(self.prereg["execution_authority"])

    def test_topology_likelihood_core_is_synthetic_validated_but_zero_authority(self) -> None:
        self.assertEqual(sha256_file(TOPOLOGY_IMPLEMENTATION), EXPECTED_TOPOLOGY_IMPLEMENTATION_SHA)
        artifact = self.topology_implementation
        self.assertEqual(artifact["status"], "CORE_TOPOLOGY_LIKELIHOOD_SYNTHETIC_PASS")
        contract = artifact["implementation_contract"]
        self.assertEqual(contract["N2_parameter_count_for_covariance"], 4)
        self.assertEqual(contract["candidate_parameter_count_for_covariance"], 6)
        self.assertEqual(contract["candidate_minus_N2_degrees_of_freedom"], 2)
        validation = artifact["synthetic_validation"]
        self.assertEqual(validation["exact_nesting_loglik_absolute_error"], 0.0)
        self.assertLess(validation["exchangeable_null"]["candidate"]["max_exchangeability_deviation"], 0.08)
        self.assertLess(validation["exchangeable_null"]["heldout_candidate_minus_n2_log_likelihood"], 1.5)
        self.assertGreater(validation["nonexchangeable_alternative"]["candidate"]["max_exchangeability_deviation"], 0.20)
        self.assertGreater(validation["nonexchangeable_alternative"]["heldout_candidate_minus_n2_log_likelihood"], 5.0)
        self.assertFalse(artifact["scientific_authority"])
        self.assertFalse(any(artifact["authority"].values()))
        projected = self.proposal["topology_implementation_preflight"]
        self.assertEqual(projected["artifact_sha256"], EXPECTED_TOPOLOGY_IMPLEMENTATION_SHA)
        self.assertFalse(projected["scientific_authority"])

    def test_hsm_release_is_complete_but_gated_and_zero_authority(self) -> None:
        self.assertEqual(sha256_file(HSM_PREFLIGHT), EXPECTED_HSM_PREFLIGHT_SHA)
        self.assertEqual(sha256_file(HSM_MANIFEST), EXPECTED_HSM_MANIFEST_SHA)
        self.assertEqual(self.hsm["status"], "COMPLETE_RELEASE_MANIFEST_GATED_CONTENT_WAIT")
        self.assertEqual(self.hsm_manifest["file_count"], 500)
        self.assertEqual(self.hsm_manifest["dataset_revision"], "a6cd11fa39d56804ea3c4de38a4ab27c74d9edfb")
        ids = [int(row["path"].split("scene_")[1].split(".json")[0]) for row in self.hsm_manifest["files"]]
        self.assertEqual(ids, list(range(500)))
        self.assertFalse(self.hsm["access_probe"]["generated_scene_content_accessible_from_current_69_identity"])
        self.assertEqual(self.hsm["access_probe"]["http_status_for_pinned_scene_0_resolve"], 403)
        self.assertFalse(self.hsm["scientific_authority"])
        self.assertFalse(any(self.hsm["authority"].values()))

    def test_current_source_collision_and_secondary_lego_are_preserved(self) -> None:
        self.assertEqual(sha256_file(COLLISION), EXPECTED_COLLISION_SHA)
        self.assertEqual(sha256_file(LEGO_AUDIT), EXPECTED_LEGO_AUDIT_SHA)
        roles = {row["role"] for row in self.collision["sources"]}
        self.assertIn("DIRECT_BENCHMARK_COLLISION", roles)
        self.assertIn("CROSS_DOMAIN_STRONG_NULL", roles)
        self.assertIn("GENERIC_METHOD_COLLISION", roles)
        secondary = {row["name"]: row for row in self.proposal["secondary_substrates"]}
        self.assertEqual(secondary["LEGO-Bench"]["status"], "CONSTRUCT_CLEAR_RUNTIME_NOT_READY")
        self.assertIn("InstructScene / 3D-FRONT", secondary)
        self.assertIn("prerequisite-aware", self.proposal["current_source_collision_review"]["surviving_primary_object"])


if __name__ == "__main__":
    unittest.main()
