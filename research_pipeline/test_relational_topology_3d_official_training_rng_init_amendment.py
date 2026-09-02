from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJ = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
V13 = ROOT / "experiments/3d_official_training" / f"{OBJ}-official-training-developmental-authority-v13"
V15A = ROOT / "experiments/3d_official_training" / f"{OBJ}-official-training-runtime-amendment-v15a"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OfficialTrainingRNGInitAmendmentV15ATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.amend = json.loads((V15A / "runtime_amendment.json").read_text())

    def test_parent_authority_is_content_addressed(self) -> None:
        self.assertEqual(self.amend["parent_authority_sha256"], sha(V13 / "authority_grant.json"))

    def test_failed_sgp_preflight_is_zero_step_and_pre_forward(self) -> None:
        f = self.amend["observed_failure"]
        self.assertEqual(f["optimizer_steps_committed"], 0)
        self.assertFalse(f["forward_backward_executed"])
        self.assertEqual(f["scientific_outcomes"], 0)

    def test_diagnosis_restores_exact_frozen_init(self) -> None:
        d = self.amend["diagnosis"]
        self.assertNotEqual(
            d["model_initialized_immediately_after_clip_load_sha256"],
            d["frozen_expected_initial_model_state_sha256"],
        )
        self.assertEqual(
            d["model_initialized_after_rng_restore_sha256"],
            d["frozen_expected_initial_model_state_sha256"],
        )
        self.assertEqual(d["parameter_count"], 51_156_834)

    def test_scientific_scope_is_unchanged(self) -> None:
        r = self.amend["repair"]
        for key in (
            "scientific_change", "model_architecture_change", "data_change", "corpus_change",
            "prompt_change", "training_seed_change", "batch_size_change",
            "gradient_accumulation_change", "optimizer_change", "training_step_budget_change",
            "checkpoint_cadence_change", "validation_policy_change", "precision_policy_change",
            "decoder_path_change",
        ):
            self.assertFalse(r[key], key)
        self.assertTrue(self.amend["authority"]["scope_is_identical_to_v13"])
        self.assertFalse(self.amend["authority"]["p1"])
        self.assertEqual(self.amend["authority"]["scientific_outcomes"], 0)

    def test_child_code_hashes_match(self) -> None:
        c = self.amend["child_code"]
        self.assertEqual(c["core_sha256"], sha(ROOT / "research_pipeline/relational_topology_official_training_dev_v15a.py"))
        self.assertEqual(c["training_segment_sha256"], sha(ROOT / "research_pipeline/relational_topology_official_training_dev_run_v15a.py"))
        self.assertEqual(c["entrypoint_sha256"], sha(ROOT / "scripts/run_relational_topology_3d_official_training_developmental_v15a.py"))

    def test_v15a_preserves_decoder_and_changes_only_sgp_init_path(self) -> None:
        old = (ROOT / "research_pipeline/relational_topology_official_training_dev_v14a.py").read_text()
        new = (ROOT / "research_pipeline/relational_topology_official_training_dev_v15a.py").read_text()
        before_old, after_old = old.split("def init_component", 1)
        old_body, suffix_old = after_old.split("\ndef loss_for", 1)
        before_new, after_new = new.split("def init_component", 1)
        new_body, suffix_new = after_new.split("\ndef loss_for", 1)
        self.assertEqual(before_new, before_old)
        self.assertEqual(suffix_new, suffix_old)
        self.assertIn('else:\n        model,opt,ema,text,vq=make_model(source,component,cfg,ds,device,clip,fvq,bounds)', new_body)
        self.assertIn("set_rng()", new_body)
        self.assertIn("CLIPTextModelWithProjection.from_pretrained", new_body)

    def test_run_and_entrypoint_only_retarget_child_module_names(self) -> None:
        old_run = (ROOT / "research_pipeline/relational_topology_official_training_dev_run_v14a.py").read_text()
        new_run = (ROOT / "research_pipeline/relational_topology_official_training_dev_run_v15a.py").read_text()
        self.assertEqual(new_run, old_run.replace("relational_topology_official_training_dev_v14a", "relational_topology_official_training_dev_v15a"))
        old_entry = (ROOT / "scripts/run_relational_topology_3d_official_training_developmental_v14a.py").read_text()
        new_entry = (ROOT / "scripts/run_relational_topology_3d_official_training_developmental_v15a.py").read_text()
        expected = old_entry.replace("relational_topology_official_training_dev_v14a", "relational_topology_official_training_dev_v15a").replace("relational_topology_official_training_dev_run_v14a", "relational_topology_official_training_dev_run_v15a")
        self.assertEqual(new_entry, expected)


if __name__ == "__main__":
    unittest.main()
