from __future__ import annotations

import hashlib
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from research_pipeline.f18_port010_replay_contract import build_binding, validate_binding, validate_replay_receipt


class F18Port010ReplayContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.binding = build_binding()
        self._tmp = tempfile.TemporaryDirectory()
        self.artifact_root = Path(self._tmp.name)
        self.artifact_bytes = b"system-gate-regression-only\n"
        (self.artifact_root / "final_map.json").write_bytes(self.artifact_bytes)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def good_receipt(self) -> dict:
        obj = self.binding["research_object"]
        return {
            "failure_id": "F18",
            "candidate_id": "PORT-010",
            "candidate_snapshot_sha256": obj["candidate_snapshot_sha256"],
            "exact_f0_sha256": self.binding["exact_f0"]["sha256"],
            "replay_status": "PASS",
            "evidence_review_status": "BLOCK_BAKE_IN",
            "authority_source": obj["authorization_scope"]["authority_source"],
            "authority": {"problem_gate": False, "method": False, "experiment": False, "p0": False, "gpu": False, "scientific": False},
            "artifacts": [{
                "path": "final_map.json",
                "sha256": hashlib.sha256(self.artifact_bytes).hexdigest(),
                "provenance": {"frozen_ref": "VibeWorlding-Gym@ec8bdebf285fd4f3f2d7e2c00e5324d63ddaa71d", "generated_by_replay": True},
            }],
        }

    def test_current_canonical_binding_is_zero_authority_hold(self) -> None:
        self.assertEqual(validate_binding(self.binding), [])
        self.assertFalse(self.binding["failure"]["may_create_authority"])
        self.assertFalse(self.binding["exact_f0"]["mutation_from_replay_allowed"])
        self.assertEqual(self.binding["scientific_state"]["scientific_release"], "HOLD")
        source_artifacts = self.binding["research_object"]["source_artifacts"]
        self.assertEqual(len(source_artifacts), 2)
        self.assertEqual(
            {item["declaration_kind"] for item in source_artifacts},
            {"FIRST_PARTY_REPOSITORY", "FIRST_PARTY_DATASET"},
        )

    def test_replay_pass_preserves_scientific_hold_without_review_pass(self) -> None:
        result = validate_replay_receipt(self.binding, self.good_receipt(), self.artifact_root)
        self.assertTrue(result["F18_PORT010_BINDING_PASS"])
        self.assertEqual(result["receipt_integrity"], "PASS")
        self.assertEqual(result["exact_F0_replay"], "PASS")
        self.assertEqual(result["zero_authority_check"], "PASS")
        self.assertEqual(result["hold_preservation"], "PASS")
        self.assertEqual(result["scientific_release"], "HOLD")

    def test_artifact_without_provenance_is_rejected(self) -> None:
        receipt = self.good_receipt()
        receipt["artifacts"][0].pop("provenance")
        result = validate_replay_receipt(self.binding, receipt, self.artifact_root)
        self.assertEqual(result["receipt_integrity"], "REJECT")
        self.assertEqual(result["scientific_release"], "HOLD")
        self.assertTrue(any("provenance" in err for err in result["errors"]))

    def test_receipt_cannot_self_authorize(self) -> None:
        receipt = self.good_receipt()
        receipt["authority"] = True
        result = validate_replay_receipt(self.binding, receipt, self.artifact_root)
        self.assertEqual(result["zero_authority_check"], "REJECT")
        self.assertEqual(result["scientific_release"], "HOLD")

    def test_nonzero_nested_authority_is_rejected(self) -> None:
        receipt = self.good_receipt()
        receipt["authority"]["experiment"] = True
        result = validate_replay_receipt(self.binding, receipt, self.artifact_root)
        self.assertEqual(result["zero_authority_check"], "REJECT")
        self.assertEqual(result["scientific_release"], "HOLD")

    def test_wrong_external_authority_source_is_rejected(self) -> None:
        receipt = self.good_receipt()
        receipt["authority_source"] = "F18:self-issued"
        result = validate_replay_receipt(self.binding, receipt, self.artifact_root)
        self.assertEqual(result["receipt_integrity"], "REJECT")
        self.assertEqual(result["scientific_release"], "HOLD")

    def test_replay_cannot_mutate_exact_f0(self) -> None:
        tampered = deepcopy(self.binding)
        tampered["exact_f0"]["material"]["status"] = "RELEASED"
        errors = validate_binding(tampered)
        self.assertIn("exact-F0 content hash mismatch", errors)

    def test_historical_port010_id_collision_cannot_bind(self) -> None:
        tampered = deepcopy(self.binding)
        tampered["research_object"]["title"] = "historical SkillJack/SkillX residual"
        errors = validate_binding(tampered)
        self.assertIn("PORT-010 object identity/scope mismatch", errors)

    def test_receipt_claiming_review_pass_still_cannot_override_canonical_block(self) -> None:
        receipt = self.good_receipt()
        receipt["evidence_review_status"] = "PASS"
        result = validate_replay_receipt(self.binding, receipt, self.artifact_root)
        self.assertEqual(result["receipt_integrity"], "REJECT")
        self.assertEqual(result["scientific_release"], "HOLD")
        self.assertTrue(any("cannot override canonical review" in err for err in result["errors"]))

    def test_artifact_content_hash_is_verified(self) -> None:
        receipt = self.good_receipt()
        receipt["artifacts"][0]["sha256"] = "0" * 64
        result = validate_replay_receipt(self.binding, receipt, self.artifact_root)
        self.assertEqual(result["receipt_integrity"], "REJECT")
        self.assertTrue(any("content hash mismatch" in err for err in result["errors"]))


if __name__ == "__main__":
    unittest.main()
