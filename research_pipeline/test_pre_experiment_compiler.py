from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .p0_common import load_json
from .pre_experiment_compiler import compile_from_path, compile_pre_experiment_card
from .pre_experiment_specs import GATES


CONFIGS = (
    "p0_a1_screening_config.json",
    "p0_a1_confirm_config.json",
    "p0_a2_screening_config.json",
    "p0_a2_confirm_config.json",
)


def paper_design_contract() -> dict:
    return {
        "novelty": {
            "paper_problem": "Test whether a persistent-update method contributes an irreducible mechanism under a frozen paper claim.",
            "closest_work": [{"identity": "closest-method", "difference": "the proposed mechanism changes a distinct decision variable", "source_ref": "primary-source-placeholder-for-test"}],
            "novelty_axis": "mechanism",
            "contribution_claim": "The method contributes a distinct mechanism rather than a larger implementation.",
            "irreducible_difference": "The strongest matched simplification must make different decisions on preregistered cases.",
            "collision_status": "reviewed",
        },
        "method": {
            "method_name": "test-method",
            "core_mechanism": "a frozen mechanism implementing the novelty claim",
            "novelty_to_method_mapping": [{"novelty": "mechanism", "component": "core"}],
            "components": ["core"],
            "strongest_simplification": "matched simple baseline",
            "method_change_rule": "core changes return to novelty/method review",
        },
        "experiment_blueprint": {
            "claim_experiment_matrix": [{"claim_id": "C1", "claim": "method is irreducible", "local_test": "tiny decisive disagreement test", "full_test": "frozen multi-seed comparison", "metric": "matched advantage", "strongest_baseline": "matched simple baseline"}],
            "local_validation_scope": "minimal decisive pilot only",
            "full_experiment_scope": "full frozen evidence matrix",
            "baseline_matrix": ["matched simple baseline"],
            "ablation_matrix": ["remove core mechanism"],
            "freeze_rule": "freeze method and blueprint before full experiment",
            "experimental_integrity": {
                "model_and_inference": "freeze model/checkpoint/inference settings",
                "prompt_tool_policy": "freeze prompts, tools, and search access",
                "task_sample_split": "freeze local and hidden splits",
                "metric_analysis_plan": "freeze metric and statistical analysis",
                "randomness_replication_plan": "freeze seeds/replicates and stochastic-agent variance analysis",
                "stopping_exclusion_rules": "freeze stopping and exclusions",
                "allowed_adaptations": "implementation-only repairs; core changes require new contract",
                "hidden_evaluation_access_policy": "deny hidden answers and benchmark result pages",
            },
        },
    }



def mark_endpoint_headroom_pass(config: dict) -> dict:
    outcomes = config["pre_experiment"]["outcomes"]
    outcomes["primary_readout_type"] = "terminal-success"
    outcomes["execution_cap_counts_as_terminal_failure"] = False
    if "HORIZON-CENSORED" not in outcomes["allowed"]:
        outcomes["allowed"].append("HORIZON-CENSORED")
    outcomes["endpoint_headroom"] = {
        "passed": True,
        "evidence_id": "unit-test-endpoint-headroom",
        "measured_non_censored_fraction": 0.80,
        "minimum_non_censored_fraction": 0.50,
        "measured_bilateral_cap_fraction": 0.10,
        "maximum_bilateral_cap_fraction": 0.25,
    }
    return config


def qualification() -> dict:
    return {
        "schema_version": "1.0",
        "status": "complete",
        "model_path": "/models/Qwen2.5-7B-Instruct",
        "policy_mode": "react-family",
        "split": "eval_out_of_distribution",
        "num_envs": 134,
        "successes": 41,
        "success_rate": 41 / 134,
        "task_types_with_success": 5,
        "gate": {"stage": "full-qualification", "passed": True, "decision": "qualified"},
    }


class PreExperimentCompilerTest(unittest.TestCase):
    def write_evidence(self, root: Path) -> None:
        target = root / "pre-experiment" / "evidence" / "qualifications" / "qwen25-react-family-ood134.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(qualification()), encoding="utf-8")

    def test_current_frozen_configs_are_blocked_by_retrospective_identifiability_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_evidence(root)
            for name in CONFIGS:
                config_path = Path(__file__).with_name(name)
                idea_id = load_json(config_path)["idea_id"]
                card = compile_from_path(idea_id, config_path, root)
                self.assertEqual(card["gate_count"], 8, name)
                self.assertEqual(card["passed_gates"], 6, (name, card["blockers"]))
                self.assertFalse(card["paper_design_prerequisite"]["passed"], name)
                self.assertIn("paper-design-contract-missing", card["blockers"])
                self.assertTrue(card["principle_certificate_prerequisite"]["passed"], name)
                plan = card["research_execution_plan"]
                self.assertEqual(plan["source_design"], "SCION Research Execution Plan")
                self.assertFalse(plan["execution_authority"])
                self.assertEqual(len(plan["verification_checkpoints"]), 11)
                self.assertIn("gpu-experiment", plan["capability_requirements"])
                self.assertFalse(card["execution_authorized"], name)
                self.assertIn("primary-readout-type-missing-or-unknown", card["blockers"])
                self.assertIn("execution-cap-censoring-policy-invalid", card["blockers"])
                self.assertEqual([row["key"] for row in card["gates"]], [row["key"] for row in GATES])
                if idea_id == "update-trust-region":
                    self.assertIn("retrospective-representability", card["blockers"])
                    self.assertIn("retrospective-tiny_overfit", card["blockers"])
                else:
                    self.assertIn("retrospective-target_variation", card["blockers"])
                    self.assertIn("retrospective-baseline_disagreement", card["blockers"])
                    self.assertIn("retrospective-tiny_overfit", card["blockers"])

    def test_eight_of_eight_does_not_bypass_failed_updater_competence(self) -> None:
        repaired = {"checks": [
            {"key": key, "pass": True, "evidence": "repaired pre-GPU evidence"}
            for key in ("claim_alignment", "target_variation", "baseline_disagreement", "representability", "tiny_overfit", "competence_window", "effect_variation")
        ], "blockers": [], "execution_ready": True, "status": "pass"}
        with tempfile.TemporaryDirectory() as td, patch("research_pipeline.pre_experiment_science.audit_contract", return_value=repaired):
            root = Path(td)
            self.write_evidence(root)
            for name in CONFIGS:
                config_path = Path(__file__).with_name(name)
                config = mark_endpoint_headroom_pass(copy.deepcopy(load_json(config_path)))
                card = compile_pre_experiment_card(config["idea_id"], config, root)
                self.assertEqual(card["gate_count"], 8, name)
                self.assertEqual(card["passed_gates"], 8, (name, card["blockers"]))
                self.assertFalse(card["execution_authorized"], name)
                self.assertFalse(card["updater_competence_prerequisite"]["passed"], name)
                self.assertIn("updater-competence-prerequisite-failed", card["blockers"])

    def test_updater_competence_plus_eight_of_eight_unlocks_execution(self) -> None:
        repaired = {"checks": [
            {"key": key, "pass": True, "evidence": "repaired pre-GPU evidence"}
            for key in ("claim_alignment", "target_variation", "baseline_disagreement", "representability", "tiny_overfit", "competence_window", "effect_variation")
        ], "blockers": [], "execution_ready": True, "status": "pass"}
        with tempfile.TemporaryDirectory() as td, patch("research_pipeline.pre_experiment_science.audit_contract", return_value=repaired):
            root = Path(td)
            self.write_evidence(root)
            for name in CONFIGS:
                config_path = Path(__file__).with_name(name)
                config = mark_endpoint_headroom_pass(copy.deepcopy(load_json(config_path)))
                config["pre_experiment"]["paper_design"] = paper_design_contract()
                config["pre_experiment"]["updater_competence"]["passed"] = True
                config["pre_experiment"]["updater_competence"]["status"] = "pass"
                config["pre_experiment"]["updater_competence"]["decision"] = "UPDATER_COMPETENT"
                card = compile_pre_experiment_card(config["idea_id"], config, root)
                self.assertEqual(card["gate_count"], 8, name)
                self.assertEqual(card["passed_gates"], 8, (name, card["blockers"]))
                self.assertTrue(card["paper_design_prerequisite"]["passed"], name)
                self.assertTrue(card["principle_certificate_prerequisite"]["passed"], name)
                self.assertTrue(card["updater_competence_prerequisite"]["passed"], name)
                self.assertTrue(card["execution_authorized"], name)

    def test_missing_competence_artifact_blocks_launch(self) -> None:
        config_path = Path(__file__).with_name("p0_a1_screening_config.json")
        with tempfile.TemporaryDirectory() as td:
            card = compile_from_path("update-trust-region", config_path, Path(td))
        self.assertFalse(card["execution_authorized"])
        self.assertIn("competence-evidence-file-missing", card["blockers"])

    def test_missing_principle_certificate_blocks_even_otherwise_ready_launch(self) -> None:
        repaired = {"checks": [
            {"key": key, "pass": True, "evidence": "repaired pre-GPU evidence"}
            for key in ("claim_alignment", "target_variation", "baseline_disagreement", "representability", "tiny_overfit", "competence_window", "effect_variation")
        ], "blockers": [], "execution_ready": True, "status": "pass"}
        config_path = Path(__file__).with_name("p0_a1_screening_config.json")
        config = mark_endpoint_headroom_pass(copy.deepcopy(load_json(config_path)))
        config["pre_experiment"].pop("principle_certificate")
        config["pre_experiment"]["updater_competence"]["passed"] = True
        config["pre_experiment"]["updater_competence"]["status"] = "pass"
        with tempfile.TemporaryDirectory() as td, patch("research_pipeline.pre_experiment_science.audit_contract", return_value=repaired):
            root = Path(td)
            self.write_evidence(root)
            card = compile_pre_experiment_card(config["idea_id"], config, root)
        self.assertEqual(card["passed_gates"], 8)
        self.assertFalse(card["execution_authorized"])
        self.assertIn("principle-certificate-missing", card["blockers"])

    def test_unresolvable_threshold_is_caught_before_gpu(self) -> None:
        config_path = Path(__file__).with_name("p0_a1_confirm_config.json")
        config = copy.deepcopy(load_json(config_path))
        config["go_gate"]["max_target_gain_loss"] = 0.02
        for row in config["pre_experiment"]["parameter_provenance"]["entries"]:
            if row["parameter"] == "go_gate.max_target_gain_loss":
                row["value"] = 0.02
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_evidence(root)
            card = compile_pre_experiment_card("update-trust-region", config, root)
        self.assertFalse(card["execution_authorized"])
        self.assertIn("target-gain-threshold-finer-than-observable-resolution", card["blockers"])

    def test_gpu_cap_is_derived_from_measured_throughput(self) -> None:
        config_path = Path(__file__).with_name("p0_a2_confirm_config.json")
        config = copy.deepcopy(load_json(config_path))
        config["resource_cap"]["gpu_hours"] = 3.0
        for row in config["pre_experiment"]["parameter_provenance"]["entries"]:
            if row["parameter"] == "resource_cap.gpu_hours":
                row["value"] = 3.0
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_evidence(root)
            card = compile_pre_experiment_card("budgeted-evolution-controller", config, root)
        self.assertFalse(card["execution_authorized"])
        self.assertIn("gpu-hour-cap-below-worst-case-plus-margin", card["blockers"])

    def test_screening_contract_cannot_allow_method_fail(self) -> None:
        config_path = Path(__file__).with_name("p0_a2_screening_config.json")
        config = copy.deepcopy(load_json(config_path))
        config["pre_experiment"]["outcomes"]["allowed"].append("METHOD-FAIL")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_evidence(root)
            card = compile_pre_experiment_card("budgeted-evolution-controller", config, root)
        self.assertFalse(card["execution_authorized"])
        self.assertIn("screening-must-not-allow-method-fail", card["blockers"])


    def test_terminal_success_requires_headroom_and_typed_censoring(self) -> None:
        config = copy.deepcopy(load_json(Path(__file__).with_name("p0_a1_confirm_config.json")))
        outcomes = config["pre_experiment"]["outcomes"]
        outcomes["primary_readout_type"] = "terminal-success"
        outcomes["execution_cap_counts_as_terminal_failure"] = False
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_evidence(root)
            card = compile_pre_experiment_card("update-trust-region", config, root)
        self.assertIn("terminal-readout-missing-horizon-censored-outcome", card["blockers"])
        self.assertIn("endpoint-headroom-contract-missing", card["blockers"])

    def test_failed_endpoint_headroom_blocks_launch(self) -> None:
        config = mark_endpoint_headroom_pass(copy.deepcopy(load_json(Path(__file__).with_name("p0_a1_confirm_config.json"))))
        headroom = config["pre_experiment"]["outcomes"]["endpoint_headroom"]
        headroom["passed"] = False
        headroom["measured_non_censored_fraction"] = 0.30
        headroom["measured_bilateral_cap_fraction"] = 0.55
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_evidence(root)
            card = compile_pre_experiment_card("update-trust-region", config, root)
        self.assertFalse(card["execution_authorized"])
        self.assertIn("endpoint-headroom-audit-failed", card["blockers"])
        self.assertIn("endpoint-headroom-noncensored-insufficient", card["blockers"])
        self.assertIn("endpoint-headroom-bilateral-cap-too-high", card["blockers"])


if __name__ == "__main__":
    unittest.main()
