from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.behavior_formal_goal_coupling_shared_multitask_panel import (
    DEMO_HORIZON_RESULT_SHA256,
    GR00T_FROZEN_CHECKPOINT,
    OBJECT_ID,
    PARENT_PREREG_SHA256,
    episode_digest,
    selected_episode_ids,
    validate_parent,
)

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "generated/behavior-formal-goal-coupling-two-family-strict-panel-preregistration-20260831.json"
SOURCE = ROOT / "generated/behavior-formal-goal-coupling-shared-multitask-source-qualification-20260831.json"
SUBSET = ROOT / "generated/behavior-formal-goal-coupling-shared-multitask-subset-qualification-20260831.json"
PREREG = ROOT / "generated/behavior-formal-goal-coupling-shared-multitask-panel-preregistration-20260831.json"


class SharedMultitaskPanelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = json.loads(PARENT.read_text(encoding="utf-8"))
        self.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.subset = json.loads(SUBSET.read_text(encoding="utf-8"))
        self.prereg = json.loads(PREREG.read_text(encoding="utf-8"))

    def test_parent_is_exactly_content_addressed(self) -> None:
        parent = validate_parent(PARENT)
        self.assertEqual(parent["panel"]["pair_count"], 13)
        self.assertEqual(parent["panel"]["task_count"], 26)
        self.assertEqual(self.prereg["bindings"]["parent_preregistration_sha256"], PARENT_PREREG_SHA256)

    def test_episode_subset_is_exactly_5200_and_outcome_blind(self) -> None:
        task_indices = [int(x) for x in self.parent["panel"]["task_indices"]]
        ids = selected_episode_ids(task_indices)
        self.assertEqual(len(ids), 5200)
        self.assertEqual(len(set(ids)), 5200)
        self.assertEqual(self.subset["episode_indices_sha256"], episode_digest(task_indices))
        self.assertEqual(self.subset["metadata_columns_read"], ["episode_index", "task_index", "tasks"])
        self.assertFalse(self.subset["policy_outcomes_read"])
        self.assertFalse(self.subset["payload_materialization_authorized"])

    def test_panel_is_inherited_without_pair_or_task_drift(self) -> None:
        self.assertEqual(self.prereg["panel"], self.parent["panel"])
        self.assertTrue(self.prereg["panel"]["task_replacement_forbidden"])
        self.assertTrue(self.prereg["primary_analysis"]["no_pair_dropping"])
        self.assertTrue(self.prereg["primary_analysis"]["no_task_replacement"])
        self.assertEqual(self.prereg["primary_analysis"]["exact_test"], "two-sided sign-flip randomization over all 2^13 = 8192 pair-label assignments")

    def test_resource_reduction_is_52_to_one_training_job(self) -> None:
        resources = self.prereg["resource_reduction"]
        self.assertEqual(resources["task_specific_parent_training_jobs"], 52)
        self.assertEqual(resources["shared_child_training_jobs"], 1)
        self.assertEqual(resources["training_job_reduction"], 51)
        self.assertEqual(resources["evaluation_rollouts_if_later_authorized"], 520)
        self.assertEqual(self.prereg["policy_units"]["pi0.5"]["training_jobs"], 1)
        self.assertEqual(self.prereg["policy_units"]["GR00T N1.7"]["training_jobs"], 0)

    def test_gr00t_terminal_checkpoint_is_frozen_without_shopping(self) -> None:
        groot = self.prereg["policy_units"]["GR00T N1.7"]
        self.assertEqual(groot["checkpoint"], GR00T_FROZEN_CHECKPOINT)
        self.assertEqual(groot["content_address_status"], "PENDING_EXACT_HF_REVISION_AND_REQUIRED_FILE_OID_SIZE_FREEZE")
        self.assertTrue(self.prereg["primary_analysis"]["no_checkpoint_shopping"])

    def test_authority_remains_closed(self) -> None:
        for artifact in (self.source, self.subset, self.prereg):
            self.assertEqual(artifact["object_id"], OBJECT_ID)
            self.assertFalse(artifact["scientific_authority"])
            self.assertFalse(artifact["execution_authority"])
            self.assertFalse(artifact["gpu_authority"])
        self.assertFalse(self.prereg["model_load_authorized"])
        self.assertFalse(self.prereg["policy_training_authorized"])
        self.assertFalse(self.prereg["policy_rollouts_authorized"])
        self.assertFalse(self.prereg["policy_outcomes_read"])

    def test_child_cannot_lower_or_reopen_three_family_parent(self) -> None:
        forbidden = set(self.prereg["claim_boundary"]["forbidden"])
        self.assertIn("lowering or reopening the frozen three-family confirmatory gate", forbidden)
        self.assertIn("three-family or broad cross-policy generalization", forbidden)
        self.assertIn("PORT-010 reopening", forbidden)
        self.assertIn("using this child as evidence that the old three-family gate passed", self.prereg["forbidden_now"])

    def test_demo_horizon_null_is_interpretive_only(self) -> None:
        neg = self.prereg["negative_control"]
        self.assertEqual(neg["sha256"], DEMO_HORIZON_RESULT_SHA256)
        self.assertEqual(neg["frozen_result"], "DEMO_HORIZON_PRIMARY_NOT_SUPPORTED")
        self.assertIn("never a covariate", neg["use"])

    def test_tampered_parent_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "parent.json"
            altered = dict(self.parent)
            altered["status"] = "TAMPERED"
            path.write_text(json.dumps(altered), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_parent(path)


if __name__ == "__main__":
    unittest.main()
