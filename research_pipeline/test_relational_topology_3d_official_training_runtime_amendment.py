from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJ = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
V12 = ROOT / "experiments/3d_official_training" / f"{OBJ}-official-training-developmental-proposal-v12"
V13 = ROOT / "experiments/3d_official_training" / f"{OBJ}-official-training-developmental-authority-v13"
V14A = ROOT / "experiments/3d_official_training" / f"{OBJ}-official-training-runtime-amendment-v14a"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OfficialTrainingRuntimeAmendmentV14ATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.amend = json.loads((V14A / "runtime_amendment.json").read_text())
        cls.grant = json.loads((V13 / "authority_grant.json").read_text())

    def test_parent_lineage_is_content_addressed(self) -> None:
        self.assertEqual(self.amend["parent_proposal_sha256"], sha(V12 / "authority_proposal.json"))
        self.assertEqual(self.amend["parent_authority_sha256"], sha(V13 / "authority_grant.json"))

    def test_failure_is_pre_model_and_zero_step(self) -> None:
        f = self.amend["observed_failure"]
        self.assertEqual(f["optimizer_steps_committed"], 0)
        self.assertFalse(f["forward_backward_executed"])
        self.assertFalse(f["model_initialized"])
        self.assertEqual(f["scientific_outcomes"], 0)

    def test_scope_is_unchanged(self) -> None:
        r = self.amend["repair"]
        for key in (
            "scientific_change", "model_change", "data_change", "corpus_change",
            "prompt_change", "seed_change", "batch_size_change",
            "gradient_accumulation_change", "optimizer_change",
            "training_step_budget_change", "checkpoint_cadence_change",
            "validation_policy_change", "precision_policy_change",
        ):
            self.assertFalse(r[key], key)
        self.assertTrue(self.amend["authority"]["scope_is_identical_to_v13"])
        self.assertFalse(self.amend["authority"]["p1"])
        self.assertEqual(self.amend["authority"]["scientific_outcomes"], 0)

    def test_child_code_hashes_match(self) -> None:
        code = self.amend["child_code"]
        self.assertEqual(code["core_sha256"], sha(ROOT / "research_pipeline/relational_topology_official_training_dev_v14a.py"))
        self.assertEqual(code["training_segment_sha256"], sha(ROOT / "research_pipeline/relational_topology_official_training_dev_run_v14a.py"))
        self.assertEqual(code["entrypoint_sha256"], sha(ROOT / "scripts/run_relational_topology_3d_official_training_developmental_v14a.py"))

    def test_core_diff_is_only_cuda_reset_adapter(self) -> None:
        old = (ROOT / "research_pipeline/relational_topology_official_training_dev.py").read_text()
        expected = old.replace(
            'atom(root/"claim.json",claim); torch.cuda.reset_peak_memory_stats(device)',
            'atom(root/"claim.json",claim)\n    with torch.cuda.device(device):\n        torch.cuda.reset_peak_memory_stats()',
        )
        new = (ROOT / "research_pipeline/relational_topology_official_training_dev_v14a.py").read_text()
        self.assertEqual(new, expected)

    def test_training_diff_is_only_import_and_cuda_reset_adapter(self) -> None:
        old = (ROOT / "research_pipeline/relational_topology_official_training_dev_run.py").read_text()
        expected = old.replace(
            "from research_pipeline.relational_topology_official_training_dev import",
            "from research_pipeline.relational_topology_official_training_dev_v14a import",
        ).replace(
            "model.train(); torch.cuda.reset_peak_memory_stats(device); wall=time.perf_counter(); last=None",
            "model.train()\n    with torch.cuda.device(device):\n        torch.cuda.reset_peak_memory_stats()\n    wall=time.perf_counter(); last=None",
        )
        new = (ROOT / "research_pipeline/relational_topology_official_training_dev_run_v14a.py").read_text()
        self.assertEqual(new, expected)


if __name__ == "__main__":
    unittest.main()
