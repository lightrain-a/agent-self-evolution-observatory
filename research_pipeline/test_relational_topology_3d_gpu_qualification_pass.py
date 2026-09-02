from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBJECT = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
V3 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-real-corpus-qualification-v3"
V5 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-gpu-training-qualification-authority-proposal-v5"
V11 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-gpu-training-qualification-pass-v11"
RUNNER = ROOT / "research_pipeline/relational_topology_gpu_qualification_runner.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GPUTrainingQualificationPassTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v3 = load(V3 / "adjudication.json")
        cls.v5 = load(V5 / "authority_proposal.json")
        cls.summary = load(V11 / "qualification_summary.json")
        cls.adjudication = load(V11 / "adjudication.json")
        cls.grant = load(V11 / "authority_grant.json")
        cls.provenance = load(V11 / "execution_provenance.json")
        cls.checkpoints = load(V11 / "checkpoint_content_addresses.json")

    def test_all_required_components_pass_exact_resume(self) -> None:
        self.assertEqual(self.summary["verdict"], "PASS_GPU_TRAINING_QUALIFICATION_ONLY")
        self.assertTrue(self.summary["all_required_components_pass"])
        self.assertEqual(set(self.summary["components"]), {"BEDROOM-SG2SC-SHARED", "SGP-12", "SGP-14"})
        for component, row in self.summary["components"].items():
            self.assertEqual(row["status"], "PASS", component)
            self.assertEqual(row["resume_status"], "PASS", component)
            self.assertTrue(row["consumed_sequence_identical"], component)
            self.assertTrue(row["sampler_state_identical"], component)
            self.assertTrue(row["optimizer_state_identical"], component)
            self.assertTrue(row["model_state_hash_identical"], component)
            self.assertEqual(row["model_tensor_max_abs_diff"], 0.0, component)
            self.assertEqual(row["loss_trajectory_max_abs_diff"], 0.0, component)
            self.assertEqual(row["resume_tolerance"], 1e-7, component)
            self.assertTrue(row["loss_finite"], component)
            self.assertTrue(row["grad_finite"], component)
            self.assertFalse(row["oom"], component)
            self.assertFalse(row["nan_inf"], component)
            self.assertEqual(row["dataloader_failures"], 0, component)

    def test_scope_stayed_at_smallest_frozen_exact_resume_horizon(self) -> None:
        g = self.grant["grant"]
        self.assertEqual(g["logical_optimizer_steps_per_component"], 100)
        self.assertEqual(g["interrupt_after_step"], 50)
        self.assertEqual(g["resume_compare_at_step"], 100)
        self.assertEqual(g["replayed_suffix_steps_per_component"], 50)
        self.assertEqual(g["batch_size"], 4)
        self.assertEqual(g["gradient_accumulation"], 1)
        self.assertFalse(g["parameter_sweep"])
        self.assertFalse(g["validation_or_scientific_evaluation"])
        self.assertEqual(g["scientific_outcomes"], 0)
        self.assertFalse(g["outcomes_enter_p1"])
        self.assertEqual(self.summary["scope_accounting"]["BEDROOM-SG2SC-SHARED"]["baseline_logical_steps"], 100)
        self.assertTrue(self.summary["scope_accounting"]["BEDROOM-SG2SC-SHARED"]["baseline_not_rerun_in_v11"])

    def test_real_corpus_content_addresses_remain_frozen(self) -> None:
        frozen = self.v5["frozen_real_inputs"]
        observed = self.summary["components"]
        self.assertEqual(observed["SGP-12"]["corpus_sha256"], frozen["corpus_jsonl_sha256"]["IS-SUPPORT-12"])
        self.assertEqual(observed["SGP-14"]["corpus_sha256"], frozen["corpus_jsonl_sha256"]["IS-SUPPORT-14"])
        self.assertEqual(observed["BEDROOM-SG2SC-SHARED"]["corpus_sha256"], frozen["eligible_scene_pool_sha256"])
        self.assertEqual(observed["SGP-12"]["corpus_sha256"], self.v3["content_addresses"]["corpus_jsonl_sha256"]["IS-SUPPORT-12"])
        self.assertEqual(observed["SGP-14"]["corpus_sha256"], self.v3["content_addresses"]["corpus_jsonl_sha256"]["IS-SUPPORT-14"])

    def test_qualification_does_not_open_official_training_or_p1(self) -> None:
        auth = self.summary["authority_after_qualification"]
        self.assertTrue(auth["gpu_training_qualification_passed"])
        self.assertFalse(auth["gpu_authority_for_official_training"])
        self.assertFalse(auth["official_training"])
        for key in ("p1", "p2", "p3"):
            self.assertFalse(auth[key], key)
        self.assertEqual(auth["scientific_gpu_runs"], 0)
        self.assertEqual(auth["scientific_outcomes"], 0)
        self.assertFalse(self.adjudication["official_training_authorized"])
        self.assertFalse(self.adjudication["p1_authorized"])
        self.assertEqual(self.adjudication["scientific_interpretation"], "FORBIDDEN_QUALIFICATION_ONLY")
        self.assertEqual(self.adjudication["next_gate"], "AWAIT_SEPARATE_OFFICIAL_TRAINING_AUTHORITY_DECISION")

    def test_port_010_is_unchanged(self) -> None:
        for artifact in (self.summary, self.adjudication, self.grant):
            self.assertEqual(artifact["port_010"]["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
            self.assertEqual(artifact["port_010"]["evidence_review"], "BLOCK_BAKE_IN")
            self.assertFalse(artifact["port_010"]["changed"])

    def test_executed_runner_is_content_addressed_and_repair_is_non_scientific(self) -> None:
        expected = self.provenance["executed_code"]["runner_v11_sha256"]
        self.assertEqual(expected, "dba40142264ba5e68e98f95365f560a1117ac053eb28a523d1654013a87ba7d9")
        self.assertEqual(sha256(RUNNER), expected)
        v11 = self.provenance["historical_repair_lineage"]["v11"]
        for key in ("model_changed", "data_changed", "seed_changed", "batch_changed", "logical_step_budget_changed", "resume_tolerance_changed"):
            self.assertFalse(v11[key], key)
        self.assertTrue(v11["all_required_components_pass"])

    def test_checkpoint_bytes_stay_external_and_only_addresses_are_committed(self) -> None:
        raw = self.provenance["raw_artifacts"]
        self.assertFalse(raw["checkpoints_committed_to_git"])
        self.assertFalse(raw["loss_trajectories_committed_to_git"])
        self.assertFalse(raw["licensed_corpus_rows_committed_to_git"])
        self.assertTrue(raw["sanitized_hashes_and_aggregates_only"])
        expected_slots = {
            "BEDROOM-SG2SC-SHARED": 3,
            "SGP-12": 3,
            "SGP-14": 3,
        }
        for component, n in expected_slots.items():
            self.assertEqual(len(self.checkpoints[component]), n)
            for digest in self.checkpoints[component].values():
                self.assertEqual(len(digest), 64)
                int(digest, 16)

    def test_driver_metadata_parse_bug_is_explicitly_corrected(self) -> None:
        env = self.summary["environment_correction"]
        self.assertEqual(env["canonical_driver_version_from_nvidia_smi"], "580.173.02")
        self.assertEqual(env["component_summary_driver_parser_status"], "IMPLEMENTATION_METADATA_PARSE_BUG_NON_SCIENTIFIC")
        self.assertFalse(env["training_semantics_affected"])
        self.assertFalse(env["qualification_gate_affected"])


if __name__ == "__main__":
    unittest.main()
