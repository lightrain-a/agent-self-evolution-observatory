from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBJECT = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
V3 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-real-corpus-qualification-v3"
V4 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-real-corpus-balance-qualification-v4"
V11 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-gpu-training-qualification-pass-v11"
V12 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-official-training-developmental-proposal-v12"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OfficialTrainingDevelopmentalProposalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v3 = load(V3 / "adjudication.json")
        cls.v4 = load(V4 / "adjudication.json")
        cls.v11_summary = load(V11 / "qualification_summary.json")
        cls.v11_adj = load(V11 / "adjudication.json")
        cls.proposal = load(V12 / "authority_proposal.json")
        cls.plan = load(V12 / "training_plan.json")
        cls.lockbox = load(V12 / "evaluation_lockbox.json")
        cls.references = load(V12 / "reference_anchors.json")
        cls.novelty = load(V12 / "novelty_recheck.json")
        cls.resources = load(V12 / "resource_budget.json")
        cls.augmentation = load(V12 / "paired_augmentation_audit.json")
        cls.execution = load(V12 / "execution_contract.json")
        cls.adjudication = load(V12 / "adjudication.json")

    def test_proposal_grants_no_official_training_authority(self) -> None:
        self.assertEqual(self.proposal["state"], "OFFICIAL_TRAINING_DEVELOPMENTAL_AUTHORITY_PROPOSAL_ONLY")
        self.assertTrue(self.proposal["proposal"]["authority_requested"])
        self.assertFalse(self.proposal["proposal"]["authority_granted"])
        authority = self.proposal["current_authority"]
        self.assertTrue(authority["gpu_training_qualification_passed"])
        self.assertFalse(authority["official_training_developmental_authority"])
        self.assertFalse(authority["official_training"])
        self.assertFalse(authority["reproduction_evaluation"])
        self.assertFalse(authority["p1"])
        self.assertEqual(authority["scientific_gpu_runs"], 0)
        self.assertEqual(authority["scientific_outcomes"], 0)
        self.assertEqual(
            self.proposal["decision_required"],
            "EXPLICIT_OFFICIAL_TRAINING_DEVELOPMENTAL_AUTHORITY_GRANT",
        )

    def test_v11_gpu_qualification_is_content_addressed_and_passed(self) -> None:
        prereq = self.proposal["prerequisites"]["gpu_training_qualification_v11"]
        self.assertEqual(prereq["summary_sha256"], sha256(V11 / "qualification_summary.json"))
        self.assertEqual(prereq["adjudication_sha256"], sha256(V11 / "adjudication.json"))
        self.assertEqual(prereq["verdict"], self.v11_summary["verdict"])
        self.assertEqual(self.v11_adj["verdict"], "PASS_GPU_TRAINING_QUALIFICATION_ONLY")
        self.assertTrue(prereq["all_required_components_pass"])
        self.assertEqual(prereq["exact_resume_model_diff"], 0.0)
        self.assertEqual(prereq["exact_resume_loss_diff"], 0.0)

    def test_real_corpus_and_balance_parent_hashes_are_exact(self) -> None:
        self.assertEqual(
            self.proposal["prerequisites"]["real_corpus_qualification_v3"]["sha256"],
            sha256(V3 / "adjudication.json"),
        )
        self.assertEqual(
            self.proposal["prerequisites"]["real_corpus_balance_v4"]["sha256"],
            sha256(V4 / "adjudication.json"),
        )
        self.assertTrue(self.v3["verdict"].startswith("PASS_"))
        self.assertTrue(self.v4["verdict"].startswith("PASS_"))

    def test_developmental_training_is_three_models_one_seed_only(self) -> None:
        components = self.plan["components"]
        self.assertEqual(set(components), {"BEDROOM-SG2SC-SHARED", "SGP-12", "SGP-14"})
        for name, row in components.items():
            self.assertEqual(row["training_seed"], 20260901, name)
            self.assertEqual(row["batch_size"], 128, name)
            self.assertEqual(row["gradient_accumulation"], 1, name)
            self.assertEqual(row["logical_optimizer_steps"], 1_000_000, name)
            self.assertEqual(row["checkpoint_every_steps"], 50_000, name)
            self.assertEqual(row["final_checkpoint_policy"], "step-1000000 EMA state; outcome-blind fixed endpoint", name)
            self.assertFalse(row["validation_during_training"], name)
            self.assertFalse(row["scientific_metrics_during_training"], name)
        boundary = self.plan["developmental_scope_boundary"]
        self.assertEqual(boundary["training_seed_count"], 1)
        self.assertEqual(boundary["confirmatory_multi_seed_replication"], "NOT_AUTHORIZED_NOT_INCLUDED")
        self.assertEqual(boundary["reproduction_evaluation"], "NOT_AUTHORIZED_NOT_INCLUDED")
        self.assertEqual(boundary["P1_evaluation"], "NOT_AUTHORIZED_NOT_INCLUDED")

    def test_support_pair_only_varies_training_relation_count_support(self) -> None:
        a = self.plan["components"]["SGP-12"]
        b = self.plan["components"]["SGP-14"]
        self.assertEqual(a["row_count"], b["row_count"])
        self.assertEqual(a["eligible_scene_pool_sha256"], b["eligible_scene_pool_sha256"])
        self.assertEqual(a["training_seed"], b["training_seed"])
        self.assertEqual(a["batch_size"], b["batch_size"])
        self.assertEqual(a["gradient_accumulation"], b["gradient_accumulation"])
        self.assertEqual(a["optimizer"], b["optimizer"])
        self.assertEqual(a["ema"], b["ema"])
        self.assertEqual(a["developmental_runtime_config_sha256"], b["developmental_runtime_config_sha256"])
        self.assertEqual(a["developmental_runtime_config_sha256"], "64ce016dbeb1d3c5cee7174ae05370a5874ae716ed9fe93280b997415b1864d7")
        self.assertEqual(a["logical_optimizer_steps"], b["logical_optimizer_steps"])
        self.assertEqual(a["checkpoint_every_steps"], b["checkpoint_every_steps"])
        self.assertEqual(a["relation_count_support"], [1, 2])
        self.assertEqual(b["relation_count_support"], [1, 2, 3, 4])
        invariants = self.plan["paired_sgp_invariants"]
        self.assertTrue(invariants["same_initial_model_state_hash_required"])
        self.assertEqual(
            invariants["expected_initial_model_state_sha256"],
            "efd8ee84bf36e5ebfc9a191155495d5c540f289e20a117356c4b490a4c2fb3f3",
        )
        self.assertEqual(invariants["expected_parameter_count"], 51156834)
        self.assertTrue(invariants["initialization_precomputed_cpu_only"])
        self.assertEqual(
            invariants["only_intentionally_varied_factor"],
            "TRAINING_RELATION_COUNT_SUPPORT",
        )

    def test_paired_batch128_augmentation_replay_is_exact_outside_prompt_treatment(self) -> None:
        audit = self.augmentation
        self.assertEqual(audit["state"], "PASS_PAIRED_SGP_AUGMENTATION_REPLAY_PREFLIGHT")
        self.assertEqual(audit["optimizer_steps"], 0)
        self.assertEqual(audit["replay_design"]["audited_rows"], 384)
        self.assertTrue(audit["results"]["frozen_structural_order_identical"])
        self.assertTrue(all(audit["results"]["batch_key_hashes_identical"]))
        self.assertTrue(all(audit["results"]["batch_tensor_hashes_identical"]))
        self.assertGreater(audit["results"]["intentional_prompt_differences"], 0)
        rule = audit["future_admission_rule"]
        self.assertTrue(rule["require_same_sampler_order_sha256_between_SGP_12_and_SGP_14"])
        self.assertTrue(rule["require_same_sampler_cursor_between_SGP_12_and_SGP_14"])
        self.assertTrue(rule["require_same_RNG_state_sha256_between_SGP_12_and_SGP_14"])
        self.assertTrue(self.plan["paired_sgp_invariants"]["checkpoint_sampler_and_rng_lineage_must_match_between_arms"])

    def test_exact_batch128_resource_preflight_is_zero_step_and_fail_closed(self) -> None:
        gate = self.plan["pre_optimizer_resource_gate"]
        self.assertTrue(gate["required"])
        self.assertEqual(gate["exact_target_batch_size"], 128)
        self.assertEqual(gate["optimizer_steps"], 0)
        policy = self.resources["failure_policy"]
        self.assertFalse(policy["automatic_batch_reduction"])
        self.assertFalse(policy["automatic_gradient_accumulation_change"])
        self.assertFalse(policy["automatic_mixed_precision_change"])
        self.assertFalse(policy["automatic_multi_gpu_sharding"])

    def test_val_and_test_are_locked_out_of_training(self) -> None:
        adapter = self.plan["deliberate_official_source_adapter"]
        self.assertEqual(adapter["official_instructscene_training_splits"], ["train", "val"])
        self.assertEqual(adapter["developmental_training_splits"], ["train"])
        self.assertFalse(adapter["scientific_treatment_difference_between_SUPPORT_12_and_SUPPORT_14"])
        self.assertTrue(adapter["must_be_disclosed_in_reproduction_reporting"])
        split = self.lockbox["official_split_file"]
        self.assertEqual(split["sha256"], "f8f144f2380668b7db999d1b21b0331ade27b72f7e4892b43da068559ffb6d79")
        self.assertEqual(split["counts"], {"train": 6037, "val": 249, "test": 248})
        controls = self.lockbox["training_leakage_controls"]
        self.assertFalse(controls["val_used_for_training"])
        self.assertFalse(controls["test_used_for_training"])
        self.assertFalse(controls["validation_metrics_during_training"])
        self.assertFalse(controls["test_metrics_during_training"])
        self.assertFalse(controls["checkpoint_selection_from_val_or_test"])
        self.assertEqual(self.lockbox["future_p1_schema_preserved"]["scientific_cases_materialized_now"], 0)
        self.assertEqual(self.lockbox["future_p1_schema_preserved"]["scientific_outcomes_observed_now"], 0)

    def test_stage_specific_reference_policy_does_not_treat_archival_irecall_as_end_to_end(self) -> None:
        anchors = self.references["external_anchors"]
        archival = anchors["instructscene_iclr2024_archival"]
        reproduced = anchors["geoscenegraph_2026_instructscene_reproduction"]
        self.assertEqual(archival["reported_iRecall"], 0.7364)
        self.assertEqual(archival["use"], "DESCRIPTIVE_CONTEXT_ONLY_NOT_A_HARD_END_TO_END_GATE")
        self.assertEqual(reproduced["reported_instructscene_final_layout_iRecall"], 0.3306)
        self.assertEqual(reproduced["reported_instructscene_graph_stage_iRecall"], 0.6653)
        bands = self.references["future_reproduction_qualification_bands"]
        self.assertAlmostEqual(bands["graph_stage_relation_recall"]["frozen_lower_bound"], 0.59877)
        self.assertAlmostEqual(bands["final_layout_relation_iRecall"]["frozen_lower_bound"], 0.2806)
        self.assertFalse(self.references["reproduction_policy"]["authority_now"])
        self.assertTrue(self.references["reproduction_policy"]["no_scientific_effect_estimation"])

    def test_novelty_claims_are_narrowed_after_scene_nat_and_stage_discrepancy(self) -> None:
        self.assertEqual(self.novelty["state"], "NO_DIRECT_COLLISION_CLAIMS_NARROWED_BEFORE_AUTHORITY")
        self.assertFalse(self.novelty["source_drift"]["SceneNAT"]["github_main_drift"])
        self.assertFalse(self.novelty["source_drift"]["InstructScene"]["github_main_drift"])
        residual = self.novelty["surviving_residual_claims"]
        self.assertTrue(any("training-support crossover" in x for x in residual))
        self.assertTrue(any("fixed-count/fixed-token topology" in x for x in residual))
        self.assertTrue(any("predicted-versus-oracle" in x for x in residual))
        surrendered = self.references["claim_boundary"]["surrender"]
        self.assertTrue(any("graph-to-layout attenuation" in x for x in surrendered))
        self.assertTrue(any("5/6" in x for x in surrendered))

    def test_execution_contract_forbids_outcome_leakage_and_silent_restarts(self) -> None:
        observation = self.execution["training_observation_policy"]
        self.assertFalse(observation["loss_may_trigger_early_stop_for_convergence"])
        self.assertFalse(observation["loss_may_select_checkpoint"])
        self.assertFalse(observation["validation_outputs_may_be_generated"])
        self.assertFalse(observation["test_outputs_may_be_generated"])
        self.assertFalse(observation["support_arm_difference_may_be_computed"])
        self.assertFalse(self.execution["resume_contract"]["fresh_restart_from_scratch_if_component_path_exists"])
        self.assertEqual(self.execution["checkpoint_contract"]["cadence_steps"], 50_000)
        self.assertEqual(self.execution["checkpoint_contract"]["mandatory_steps"][-1], 1_000_000)

    def test_prepared_runner_is_hard_bounded_and_authority_gated(self) -> None:
        core = (ROOT / "research_pipeline/relational_topology_official_training_dev.py").read_text()
        runner = (ROOT / "research_pipeline/relational_topology_official_training_dev_run.py").read_text()
        entry = (ROOT / "scripts/run_relational_topology_3d_official_training_developmental.py").read_text()
        self.assertIn('AUTHORITY_NORMALIZED = "OFFICIAL_TRAINING_DEVELOPMENTAL_AUTHORITY_GRANTED"', core)
        self.assertIn('SEED, BATCH, STEPS, CKPT_EVERY = 20260901, 128, 1_000_000, 50_000', core)
        self.assertIn('EXPECTED_INIT = "efd8ee84bf36e5ebfc9a191155495d5c540f289e20a117356c4b490a4c2fb3f3"', core)
        self.assertIn('verify_authority(authority,proposal)', runner.replace(" ", ""))
        self.assertIn('existing segment requires explicit resume; silent restart forbidden', runner)
        self.assertIn('validation_outputs_generated":0', runner.replace(" ", ""))
        self.assertIn('test_outputs_generated":0', runner.replace(" ", ""))
        self.assertIn('--phase', entry)
        self.assertIn('--authority', entry)
        self.assertIn('--resume', entry)
        self.assertIn('EXPECTED_CONFIG_SHA', core)
        self.assertIn('developmental config hash/runtime-layout drift', core)
        prepared = self.proposal["prepared_execution"]
        self.assertEqual(prepared["runner_core_sha256"], hashlib.sha256(core.encode()).hexdigest())
        self.assertEqual(prepared["training_segment_runner_sha256"], hashlib.sha256(runner.encode()).hexdigest())
        self.assertEqual(prepared["entrypoint_sha256"], hashlib.sha256(entry.encode()).hexdigest())
        self.assertFalse(prepared["gpu_preflight_run"])
        self.assertEqual(prepared["optimizer_steps_run"], 0)

    def test_port_010_and_p1_remain_closed(self) -> None:
        for artifact in (self.proposal, self.adjudication):
            self.assertEqual(artifact["port_010"]["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
            self.assertEqual(artifact["port_010"]["evidence_review"], "BLOCK_BAKE_IN")
            self.assertFalse(artifact["port_010"]["changed"])
        self.assertFalse(self.adjudication["official_training_authorized"])
        self.assertFalse(self.adjudication["official_training_started"])
        self.assertFalse(self.adjudication["reproduction_evaluation_authorized"])
        self.assertFalse(self.adjudication["p1_authorized"])
        self.assertEqual(self.adjudication["scientific_outcomes"], 0)


if __name__ == "__main__":
    unittest.main()
