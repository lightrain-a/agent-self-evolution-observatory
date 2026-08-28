from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class STRISkillProCarrierArtifactsTest(unittest.TestCase):
    def test_qualification_binds_p0_receipts_and_keeps_claims_closed(self) -> None:
        qualification = json.loads(
            (GENERATED / "asset-first-stri-skillpro-carrier-qualification-20260828.json").read_text(encoding="utf-8")
        )
        p0 = GENERATED / "asset-first-stri-skillpro-p0-projection-result-20260828.json"
        p0b = GENERATED / "asset-first-stri-skillpro-author-p0b-result-20260828.json"
        self.assertEqual(qualification["p0_evidence"]["independent_projection"]["sha256"], sha256(p0))
        self.assertEqual(qualification["p0_evidence"]["author_scheduler_probe"]["sha256"], sha256(p0b))
        self.assertEqual(
            qualification["decision"],
            "QUALIFY_SKILLPRO_AS_PRIMARY_RECENT_FLAGSHIP_CARRIER_FOR_P1_P2_DESIGN",
        )
        boundary = qualification["scientific_boundary"]
        self.assertFalse(boundary["claim_expansion"])
        self.assertFalse(boundary["behavioral_claim_authorized"])
        self.assertFalse(boundary["manuscript_primary_carrier_replacement_authorized"])
        self.assertFalse(boundary["p1_model_execution_authorized_by_this_receipt"])

    def test_p1_p2_contract_is_outcome_blind_and_has_no_execution_authority(self) -> None:
        contract = json.loads(
            (GENERATED / "asset-first-stri-skillpro-p1-p2-contract-20260828.json").read_text(encoding="utf-8")
        )
        focal = contract["p1a_real_evidence_collection"]["focal_seed_skill_selection"]
        self.assertEqual(focal["selected"], "HypothesisElimination")
        self.assertEqual(
            focal["selected_name_sha256"],
            hashlib.sha256(b"HypothesisElimination").hexdigest(),
        )
        arms = [row["name"] for row in contract["p1b_identity_attribution_intervention"]["arms"]]
        self.assertEqual(
            arms,
            ["A_canonical", "B_id_placebo", "C_exact_split", "D_pre_gate_quotient", "E_late_identity_dedup"],
        )
        boundary = contract["scientific_boundary"]
        self.assertFalse(boundary["model_call_authority"])
        self.assertFalse(boundary["gpu_authority"])
        self.assertFalse(boundary["p1_execution_authority"])
        self.assertFalse(boundary["p2_execution_authority"])
        self.assertFalse(boundary["claim_expansion"])

    def test_p0_and_p0b_results_pass_without_behavioral_claims(self) -> None:
        for filename in (
            "asset-first-stri-skillpro-p0-projection-result-20260828.json",
            "asset-first-stri-skillpro-author-p0b-result-20260828.json",
        ):
            result = json.loads((GENERATED / filename).read_text(encoding="utf-8"))
            self.assertTrue(result["all_checks_pass"], filename)
            boundary = result["scientific_boundary"]
            self.assertFalse(boundary["claim_expansion"], filename)
            self.assertFalse(boundary.get("downstream_behavior_claim", boundary.get("behavioral_claim_authorized", False)), filename)
            self.assertEqual(boundary["new_model_calls"], 0, filename)
            self.assertEqual(boundary["new_gpu_runs"], 0, filename)

    def test_runtime_preflight_blocks_model_execution_until_environment_is_qualified(self) -> None:
        preflight = json.loads(
            (GENERATED / "asset-first-stri-skillpro-p1-runtime-preflight-20260828.json").read_text(encoding="utf-8")
        )
        self.assertEqual(preflight["decision"], "P1_MODEL_EXECUTION_BLOCKED_RUNTIME_NOT_QUALIFIED")
        self.assertFalse(preflight["execution_integrity"]["full_author_run_import_ready"])
        self.assertIn("textarena", preflight["best_existing_python_base"]["missing"])
        self.assertEqual(preflight["backend_preflight"]["local_backend"]["released_LocalLLM_vllm_tensor_parallel_size"], 4)
        boundary = preflight["scientific_boundary"]
        self.assertFalse(boundary["p1_execution_authority"])
        self.assertFalse(boundary["runtime_install_authority"])
        self.assertEqual(boundary["new_model_calls"], 0)
        self.assertEqual(boundary["new_gpu_runs"], 0)

    def test_ace_preaudit_is_candidate_only_until_commit_and_operator_are_pinned(self) -> None:
        audit = json.loads(
            (GENERATED / "asset-first-stri-ace-precarrier-audit-20260828.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            audit["decision"],
            "QUALIFY_ACE_AS_SECONDARY_POSITIVE_CONTROL_CANDIDATE_PENDING_PIN_AND_OPERATOR_AUDIT",
        )
        boundary = audit["scientific_boundary"]
        self.assertFalse(boundary["source_pin_complete"])
        self.assertFalse(boundary["ace_experiment_authority"])
        self.assertFalse(boundary["cross_system_generality_authorized"])
        self.assertEqual(boundary["new_model_calls"], 0)
        self.assertEqual(boundary["new_gpu_runs"], 0)

    def test_ace_exact_operator_audit_pins_source_and_rejects_clean_native_positive_control(self) -> None:
        audit = json.loads(
            (GENERATED / "asset-first-stri-ace-operator-audit-20260828.json").read_text(encoding="utf-8")
        )
        self.assertEqual(audit["source"]["commit"], "82709de050e1db6e6ef2f07bcb0393560b94992a")
        self.assertEqual(
            audit["theory_adjudication"]["classification"],
            "STATE_REUNION_REPAIR_PRIMITIVE_PRESENT_NOT_CLEAN_NATIVE_POSITIVE_CONTROL",
        )
        self.assertIn("trusts those returned integers", audit["operator_findings"]["bulletpoint_analyzer"]["critical_integrity_gap"])
        self.assertIn("before optional analyzer reunion", audit["operator_findings"]["current_curator"]["irreversible_seam"])
        boundary = audit["scientific_boundary"]
        self.assertTrue(boundary["source_pin_complete"])
        self.assertTrue(boundary["mechanism_intervention_design_authorized"])
        self.assertFalse(boundary["native_robustness_claim_authorized"])
        self.assertFalse(boundary["ace_behavioral_experiment_authority"])
        self.assertEqual(boundary["new_model_calls"], 0)
        self.assertEqual(boundary["new_gpu_runs"], 0)

    def test_skillpro_runtime_recheck_clears_gpu_occupancy_but_not_execution_gate(self) -> None:
        audit = json.loads(
            (GENERATED / "asset-first-stri-skillpro-runtime-recheck-20260828.json").read_text(encoding="utf-8")
        )
        self.assertEqual(audit["current_host_snapshot"]["visible_gpu_count"], 1)
        self.assertEqual(audit["current_host_snapshot"]["memory_used_mib"], 14)
        self.assertEqual(
            audit["qualification_result"]["author_documented_single_gpu_compatibility_path"],
            "ELIGIBLE_TO_MATERIALIZE",
        )
        self.assertEqual(audit["qualification_result"]["unchanged_source_faithful_path"], "BLOCKED_ON_SINGLE_GPU")
        boundary = audit["scientific_boundary"]
        self.assertTrue(boundary["compatibility_adaptation_materialization_authorized"])
        self.assertFalse(boundary["p1_execution_authority"])
        self.assertFalse(boundary["claim_expansion"])

    def test_runtime_qualification_records_both_compatibility_adaptations_and_keeps_outcomes_closed(self) -> None:
        audit = json.loads(
            (GENERATED / "asset-first-stri-skillpro-p1-runtime-qualification-20260828.json").read_text(encoding="utf-8")
        )
        self.assertTrue(audit["execution_adjudication"]["compatibility_adapted_runtime_qualified"])
        self.assertFalse(audit["execution_adjudication"]["unchanged_source_faithful_execution"])
        self.assertEqual(audit["compatibility_source_copy"]["adapted_local_llm_sha256"], "db4fe6cf91ff5598e0d40b8965368e6d26c5e45611ee372fb6db91ef41d248ae")
        adaptations = audit["compatibility_source_copy"]["adaptations"]
        self.assertEqual(len(adaptations), 2)
        self.assertIn("tensor_parallel_size=4 -> 1", adaptations[0]["change"])
        self.assertIn("swap_space=0", adaptations[1]["change"])
        self.assertEqual(audit["model_freeze"]["role"], "carrier compatibility model; not claimed as the original Skill-Pro paper backbone")
        boundary = audit["scientific_boundary"]
        self.assertEqual(boundary["new_task_outcomes"], 0)
        self.assertEqual(boundary["new_outcome_bearing_model_calls"], 0)
        self.assertFalse(boundary["p1a_collection_authority"])
        self.assertFalse(boundary["p1b_evolution_authority"])

    def test_p1a_authority_is_narrow_and_binds_collection_harness(self) -> None:
        authority = json.loads(
            (GENERATED / "asset-first-stri-skillpro-p1a-execution-authority-20260828.json").read_text(encoding="utf-8")
        )
        harness = ROOT / authority["collection_harness"]["path"]
        self.assertEqual(authority["collection_harness"]["sha256"], sha256(harness))
        self.assertEqual(authority["decision"], "AUTHORIZE_P1A_ONLY_SIX_REAL_EXPERIENCES")
        self.assertEqual(authority["frozen_execution"]["episode_count"], 6)
        self.assertEqual(authority["frozen_execution"]["seed"], 42)
        self.assertEqual(authority["frozen_execution"]["focal_skill"], "HypothesisElimination")
        self.assertTrue(authority["authorization"]["p1a_six_episode_collection"])
        self.assertFalse(authority["authorization"]["p1b_candidate_generation"])
        self.assertFalse(authority["authorization"]["p1b_ppo_gate"])
        self.assertFalse(authority["authorization"]["p2_behavioral_replay"])

    def test_p1a_result_freezes_six_real_valid_experiences(self) -> None:
        result = json.loads(
            (GENERATED / "asset-first-stri-skillpro-p1a-result-20260828.json").read_text(encoding="utf-8")
        )
        self.assertEqual(result["decision"], "P1A_PASS_SIX_REAL_EXPERIENCES_FROZEN")
        self.assertEqual(result["run"]["aggregate_semantic_evidence_sha256"], "a1c0070075d1d27a5cc5b7ea3bb3af4e51d6c077f38f132643565c720f4af2a5")
        self.assertEqual(len(result["episodes"]), 6)
        self.assertTrue(all(row["runtime_valid"] for row in result["episodes"]))
        self.assertEqual(result["aggregate"]["total_transitions"], 80)
        self.assertAlmostEqual(result["aggregate"]["mean_reward"], 2.5 / 6.0)
        self.assertFalse(result["scientific_boundary"]["candidate_generation_executed"])
        self.assertFalse(result["scientific_boundary"]["p2_authorized"])

    def test_p1b_authority_binds_final_harness_and_runtime_adaptations(self) -> None:
        authority = json.loads(
            (GENERATED / "asset-first-stri-skillpro-p1b-execution-authority-20260828.json").read_text(encoding="utf-8")
        )
        harness = ROOT / authority["execution_harness"]["path"]
        self.assertEqual(authority["execution_harness"]["sha256"], sha256(harness))
        self.assertEqual(authority["frozen_author_parameters"]["threshold"], 6)
        self.assertEqual(authority["frozen_author_parameters"]["best_of_n"], 3)
        self.assertEqual(authority["frozen_author_parameters"]["acceptance_margin"], 0.0)
        adaptations = authority["runtime"]["adaptations"]
        self.assertTrue(any("microbatch=1" in item for item in adaptations))
        self.assertTrue(any("0.75 -> 0.55" in item for item in adaptations))
        self.assertEqual(len(authority["runtime"]["failed_pre_candidate_attempt_receipts"]), 3)
        self.assertTrue(authority["authority"]["P1b_model_calls_authorized"])
        self.assertFalse(authority["authority"]["P2_behavioral_replay_authorized"])

    def test_p1_real_evolution_passes_mechanism_but_blocks_behavioral_replay(self) -> None:
        result = json.loads(
            (GENERATED / "asset-first-stri-skillpro-p1-result-20260828.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            result["decision"],
            "P1_MECHANISM_PASS_P2_BLOCKED_NO_EVOLUTION_PRODUCED_POOL_DIFFERENCE",
        )
        self.assertEqual(result["adjudication"]["p1_mechanism"], "PASS")
        self.assertEqual(result["adjudication"]["candidate_acceptance"], "NEGATIVE")
        self.assertEqual(
            result["adjudication"]["p2_behavioral_replay"],
            "BLOCKED_NO_EVOLUTION_PRODUCED_POOL_DIFFERENCE",
        )
        for seed in (42, 43, 44):
            paired = result["paired_computation_equivalence"][f"A_vs_D_seed{seed}"]
            self.assertTrue(paired["all_21_model_prompts_and_raw_outputs_exact"])
            self.assertTrue(paired["all_4_logprob_inputs_and_80_value_vectors_exact"])
            self.assertTrue(paired["j_exact"])
            a = next(row for row in result["arms"]["A_canonical"]["repeats"] if row["seed"] == seed)
            d = next(row for row in result["arms"]["D_pre_gate_quotient"]["repeats"] if row["seed"] == seed)
            self.assertEqual(a["best_j"], d["best_j"])
            self.assertLess(a["best_j"], 0.0)
            self.assertFalse(a["pool_changed"])
            self.assertFalse(d["pool_changed"])
        self.assertEqual(result["arms"]["C_exact_split"]["model_calls"], 0)
        self.assertEqual(result["arms"]["E_late_identity_dedup"]["model_calls"], 0)
        self.assertNotEqual(
            result["arms"]["B_id_placebo"]["best_j"],
            result["arms"]["A_canonical"]["repeats"][0]["best_j"],
        )
        self.assertFalse(result["scientific_boundary"]["p2_execution_authority"])
        self.assertFalse(result["scientific_boundary"]["behavioral_propagation_established"])

    def test_ace_exact_clone_reunion_probe_is_reproducible_and_timing_limited(self) -> None:
        from research_pipeline.asset_first_stri_ace_reunion_probe import build_result

        contract = json.loads(
            (GENERATED / "asset-first-stri-ace-state-reunion-intervention-contract-20260828.json").read_text(encoding="utf-8")
        )
        probe = ROOT / contract["zero_provider_probe"]["path"]
        result_path = ROOT / contract["zero_provider_probe"]["result"]
        stored = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(contract["zero_provider_probe"]["sha256"], sha256(probe))
        self.assertEqual(contract["zero_provider_probe"]["result_sha256"], sha256(result_path))
        self.assertEqual(build_result(), stored)
        self.assertEqual(stored["decision"], "ZERO_PROVIDER_REUNION_OPERATOR_PASS")
        self.assertTrue(stored["checks"]["repair_exactly_matches_canonical_line"])
        self.assertTrue(stored["timing_projection"]["pre_curator_repair_matches_canonical_input"])
        self.assertTrue(stored["timing_projection"]["post_curator_repair_cannot_change_current_curator_input"])
        self.assertFalse(stored["scientific_boundary"]["curator_output_invariance_established"])
        self.assertFalse(stored["scientific_boundary"]["behavioral_effect_established"])
        self.assertFalse(contract["scientific_boundary"]["ace_model_calls_authorized"])


if __name__ == "__main__":
    unittest.main()
