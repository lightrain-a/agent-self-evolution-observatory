from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBJECT = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
V2 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-official-training-license-confirmed-v2"
V3 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-real-corpus-qualification-v3"
V4 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-real-corpus-balance-qualification-v4"
V5 = ROOT / "experiments/3d_official_training" / f"{OBJECT}-gpu-training-qualification-authority-proposal-v5"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GPUQualificationAuthorityProposalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v2_adjudication = load(V2 / "adjudication.json")
        cls.v2_gpu = load(V2 / "gpu_qualification.json")
        cls.v3 = load(V3 / "adjudication.json")
        cls.v4 = load(V4 / "adjudication.json")
        cls.v5 = load(V5 / "authority_proposal.json")

    def test_proposal_is_request_only_and_grants_nothing(self) -> None:
        self.assertEqual(self.v5["state"], "GPU_TRAINING_QUALIFICATION_AUTHORITY_PROPOSAL_ONLY")
        self.assertTrue(self.v5["proposal"]["authority_requested"])
        self.assertFalse(self.v5["proposal"]["authority_granted"])
        authority = self.v5["current_authority"]
        self.assertTrue(authority["data_license_confirmed"])
        self.assertTrue(authority["data_materialization_authority"])
        for key in (
            "gpu_training_qualification_authority", "gpu_authority", "official_training",
            "p1", "p2", "p3",
        ):
            self.assertFalse(authority[key], key)
        self.assertEqual(authority["scientific_gpu_runs"], 0)
        self.assertEqual(authority["scientific_outcomes"], 0)
        self.assertEqual(self.v5["decision_required"], "EXPLICIT_GPU_TRAINING_QUALIFICATION_AUTHORITY_GRANT")

    def test_parent_artifacts_are_exactly_content_addressed(self) -> None:
        parents = self.v5["prerequisites"]
        self.assertEqual(parents["license_confirmed_v2"]["sha256"], sha256(V2 / "adjudication.json"))
        self.assertEqual(parents["real_corpus_qualification_v3"]["sha256"], sha256(V3 / "adjudication.json"))
        self.assertEqual(parents["real_corpus_balance_v4"]["sha256"], sha256(V4 / "adjudication.json"))
        self.assertEqual(parents["license_confirmed_v2"]["verdict"], self.v2_adjudication["verdict"])
        self.assertEqual(parents["real_corpus_qualification_v3"]["verdict"], self.v3["verdict"])
        self.assertEqual(parents["real_corpus_balance_v4"]["verdict"], self.v4["verdict"])

    def test_frozen_real_inputs_match_v3(self) -> None:
        frozen = self.v5["frozen_real_inputs"]
        self.assertEqual(frozen["corpus_jsonl_sha256"], self.v3["content_addresses"]["corpus_jsonl_sha256"])
        self.assertEqual(frozen["eligible_scene_pool_sha256"], self.v3["content_addresses"]["eligible_scene_pool_sha256"])
        self.assertEqual(frozen["excluded_candidate_sha256"], self.v3["content_addresses"]["excluded_candidate_sha256"])
        self.assertEqual(frozen["dataset_revision"], self.v3["dataset_revision"])

    def test_requested_scope_is_the_previously_frozen_v2_scope(self) -> None:
        scope = self.v5["proposal"]["scope_if_granted"]
        self.assertEqual(scope["classification"], self.v2_gpu["classification"])
        self.assertEqual(scope["allowed_scope"], self.v2_gpu["allowed_scope_after_all_gates"])
        self.assertEqual(scope["required_measurements"], self.v2_gpu["required_measurements"])
        self.assertEqual(scope["selection_rule"], self.v2_gpu["selection_rule"])
        self.assertFalse(scope["outcomes_enter_p1"])
        self.assertEqual(scope["scientific_outcomes"], 0)

    def test_real_corpus_prerequisites_pass_and_port_010_is_unchanged(self) -> None:
        self.assertTrue(self.v3["verdict"].startswith("PASS_"))
        self.assertTrue(self.v4["verdict"].startswith("PASS_"))
        self.assertTrue(all(self.v4["gates"].values()))
        self.assertEqual(self.v5["port_010"]["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual(self.v5["port_010"]["evidence_review"], "BLOCK_BAKE_IN")
        self.assertFalse(self.v5["port_010"]["changed"])

    def test_fresh_novelty_recheck_remains_mandatory_before_gpu_run(self) -> None:
        novelty = load(V2 / "novelty_watch.json")
        self.assertTrue(novelty["recheck_required_immediately_before_training_authority"])
        self.assertIn("Recheck SceneNAT novelty/release drift immediately before", self.v5["proposal"]["pre_run_requirement_if_authority_is_later_granted"])


if __name__ == "__main__":
    unittest.main()
