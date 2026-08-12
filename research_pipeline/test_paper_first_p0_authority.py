from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_p0_promotions import (
    AUTHORITY,
    AUTHORITY_ENV,
    authorized_promotions,
    load_human_authority,
    require_local_validation_authority,
)


class PaperFirstP0AuthorityTest(unittest.TestCase):
    def artifact(self, root: Path, *, lifecycle: bool = True, local: bool = True, ids=None) -> tuple[Path, dict]:
        payload = {
            "schema_version": "1.0",
            "authority_type": "human-paper-first-p0-promotion",
            "decision": "approve",
            "reviewed_by": "human-user",
            "reviewed_at": "2026-08-12T22:50:00+08:00",
            "source_message_ref": "chat-message:test-authority",
            "source_message_sha256": hashlib.sha256(b"explicit human authority").hexdigest(),
            "approved_incubation_ids": ids or ["PF-1", "PF-2"],
            "p0_lifecycle_authorized": lifecycle,
            "local_validation_authorized": local,
        }
        path = root / "authority.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path, payload

    def test_default_repository_state_has_no_paper_first_p0_authority(self) -> None:
        self.assertFalse(AUTHORITY["promotion_authorized"])
        self.assertFalse(AUTHORITY["local_validation_authorized"])
        self.assertEqual(AUTHORITY["authority_status"], "NO_EXPLICIT_USER_P0_PROMOTION_AUTHORITY")
        self.assertIn(AUTHORITY_ENV, AUTHORITY["errors"][0])
        with self.assertRaisesRegex(RuntimeError, "local validation is locked"):
            require_local_validation_authority({"PF-1"})

    def test_external_content_addressed_authority_can_promote_only_named_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path, payload = self.artifact(Path(td), ids=["PF-1", "PF-4"])
            authority = load_human_authority(path)
        self.assertTrue(authority["promotion_authorized"])
        self.assertTrue(authority["local_validation_authorized"])
        self.assertEqual(authority["source_message_sha256"], payload["source_message_sha256"])
        self.assertEqual(set(authorized_promotions(authority)), {
            "future-learnability-preserving-self-evolution",
            "diagnosability-preserving-self-evolution",
        })
        self.assertEqual(require_local_validation_authority({"PF-1", "PF-4"}, authority)["authority_status"], "EXTERNAL_HUMAN_P0_PROMOTION_AUTHORITY_VALID")

    def test_p0_lifecycle_approval_does_not_imply_local_validation_approval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path, _ = self.artifact(Path(td), lifecycle=True, local=False, ids=["PF-1"])
            authority = load_human_authority(path)
        self.assertTrue(authority["promotion_authorized"])
        self.assertFalse(authority["local_validation_authorized"])
        with self.assertRaisesRegex(RuntimeError, "local validation is locked"):
            require_local_validation_authority({"PF-1"}, authority)

    def test_authority_must_cover_every_shared_runner_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path, _ = self.artifact(Path(td), ids=["PF-2", "PF-4"])
            authority = load_human_authority(path)
        with self.assertRaisesRegex(RuntimeError, "PF-6"):
            require_local_validation_authority({"PF-2", "PF-4", "PF-6"}, authority)

    def test_invalid_source_message_hash_cannot_authorize(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path, _ = self.artifact(Path(td))
            payload = json.loads(path.read_text())
            payload["source_message_sha256"] = "not-a-sha"
            path.write_text(json.dumps(payload), encoding="utf-8")
            authority = load_human_authority(path)
        self.assertFalse(authority["promotion_authorized"])
        self.assertIn("invalid-source-message-sha256", authority["errors"])


if __name__ == "__main__":
    unittest.main()
