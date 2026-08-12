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
                self.assertEqual(card["passed_gates"], 7, (name, card["blockers"]))
                self.assertTrue(card["principle_certificate_prerequisite"]["passed"], name)
                self.assertFalse(card["execution_authorized"], name)
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
                card = compile_from_path(load_json(config_path)["idea_id"], config_path, root)
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
                config = copy.deepcopy(load_json(config_path))
                config["pre_experiment"]["updater_competence"]["passed"] = True
                config["pre_experiment"]["updater_competence"]["status"] = "pass"
                config["pre_experiment"]["updater_competence"]["decision"] = "UPDATER_COMPETENT"
                card = compile_pre_experiment_card(config["idea_id"], config, root)
                self.assertEqual(card["gate_count"], 8, name)
                self.assertEqual(card["passed_gates"], 8, (name, card["blockers"]))
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
        config = copy.deepcopy(load_json(config_path))
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


if __name__ == "__main__":
    unittest.main()
