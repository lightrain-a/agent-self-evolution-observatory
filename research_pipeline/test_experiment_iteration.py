from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .experiment_iteration import ArtifactBundle, POLICY, build_experiment_iteration_state, diagnose_a1, diagnose_a2, diagnose_b1, diagnose_e1


class ExperimentIterationTest(unittest.TestCase):
    def bundle(self, idea_id: str, decision: dict, *, qualification_pass: bool = True) -> ArtifactBundle:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name)
        (path / "events.jsonl").write_text("{}\n", encoding="utf-8")
        (path / "score-cache.jsonl").write_text("{}\n", encoding="utf-8")
        actual = int((decision.get("cost") or {}).get("new_prompt_scores") or 10)
        plan = {"estimated_unique_prompts": actual}
        protocol = {"code_commit": "abc123", "source_hash": "def456"}
        qualification = {"pass": qualification_pass, "task_success": 0.75}
        return ArtifactBundle(idea_id, path, plan, protocol, qualification, decision)

    def test_a1_converged_chance_fit_is_representation_mismatch(self) -> None:
        decision = {
            "cost": {"new_prompt_scores": 100},
            "a1": {
                "fit_gate": False,
                "fit": {"epochs_ran": 295, "converged": True, "val_auc": 0.5},
                "table": [
                    {"policy": "gain+raw-drift", "harmful": 0, "mean_gain": 0.08},
                    {"policy": "fitted-cross-surface-drift", "harmful": 2, "mean_gain": -0.12},
                ],
            },
        }
        node = diagnose_a1(self.bundle("update-trust-region", decision))
        self.assertEqual(node["diagnosis"], "representation-signal-mismatch")
        self.assertFalse(node["experiment_identifiable"])
        self.assertFalse(node["scientific_belief_update_allowed"])
        self.assertEqual(len(node["repair_children"]), 2)

    def test_a2_no_label_variation_is_not_method_failure(self) -> None:
        decision = {
            "cost": {"new_prompt_scores": 100},
            "a2": {"fit_gate": False, "fit": {"reason": "no-label-variation", "val_auc": 0.5}},
        }
        node = diagnose_a2(self.bundle("budgeted-evolution-controller", decision))
        self.assertEqual(node["diagnosis"], "no-label-variation")
        self.assertFalse(node["experiment_identifiable"])
        self.assertTrue(any(child["operator"] == "target-variation-design" for child in node["repair_children"]))

    def test_b1_equal_decisions_trigger_simplification_tie(self) -> None:
        rows = [
            {"policy": name, "lessons": ["l01", "l02", "l03"], "mean_hidden_effect": 0.0138888889}
            for name in ("single-source", "consensus", "utility-only", "cross-process-robust")
        ]
        decision = {
            "cost": {"new_prompt_scores": 100},
            "estimation_gate": {"pass": True},
            "table": rows,
            "method_go": False,
        }
        node = diagnose_b1(self.bundle("outcome-equivalent-trajectory-contrast", decision))
        self.assertEqual(node["diagnosis"], "matched-simplification-tie")
        self.assertTrue(node["experiment_identifiable"])
        self.assertTrue(node["scientific_belief_update_allowed"])
        self.assertFalse(node["scale_up_allowed"])

    def test_e1_binary_fit_without_ranking_is_objective_mismatch(self) -> None:
        decision = {
            "cost": {"new_prompt_scores": 100},
            "table": {
                "fit_gate": False,
                "fit": {
                    "epochs_ran": 700,
                    "converged": True,
                    "val_auc": 1.0,
                    "calibration_top1_accuracy": 0.0,
                    "global_best_accuracy": 0.0,
                },
            },
        }
        node = diagnose_e1(self.bundle("workflow-generalization-certificate", decision))
        self.assertEqual(node["diagnosis"], "objective-claim-mismatch")
        self.assertFalse(node["experiment_identifiable"])
        self.assertEqual(node["repair_children"][0]["operator"], "objective-child")

    def test_policy_forbids_false_negative_and_auto_scale(self) -> None:
        self.assertTrue(POLICY["underfit_cannot_be_called_scientific_fail"])
        self.assertTrue(POLICY["nonidentifiable_pilot_cannot_update_scientific_belief"])
        self.assertTrue(POLICY["automatic_scale_up_forbidden"])
        self.assertTrue(POLICY["atomic_child_only"])

    def test_real_canonical_state_if_available(self) -> None:
        state = build_experiment_iteration_state()
        self.assertEqual(state["summary"]["nodes"], 4)
        self.assertEqual(state["summary"]["scale_up_allowed"], 0)
        if state["round1_root"]:
            by_code = {node["code"]: node for node in state["nodes"]}
            self.assertEqual(by_code["A-1"]["diagnosis"], "representation-signal-mismatch")
            self.assertEqual(by_code["A-2"]["diagnosis"], "no-label-variation")
            self.assertEqual(by_code["B-1"]["diagnosis"], "matched-simplification-tie")
            self.assertEqual(by_code["E-1"]["diagnosis"], "objective-claim-mismatch")


if __name__ == "__main__":
    unittest.main()
