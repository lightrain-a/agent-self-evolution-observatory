from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.paper_first_evidence_echo_f0_authorized_execute import claim_permit_once


class EvidenceEchoAuthorizedExecuteTest(unittest.TestCase):
    def authority(self) -> dict:
        return {
            "artifact_sha256": hashlib.sha256(b"permit").hexdigest(),
            "source_message_sha256": hashlib.sha256("继续，你把其他的idea继续推进吧".encode("utf-8")).hexdigest(),
        }

    def test_permit_is_single_use_even_for_same_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = claim_permit_once(root, self.authority(), "run-a", "plan-a")
            row = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual("claimed-single-attempt", row["status"])
            self.assertFalse(row["scientific_authority"])
            with self.assertRaisesRegex(RuntimeError, "single-use"):
                claim_permit_once(root, self.authority(), "run-a", "plan-a")

    def test_same_permit_cannot_authorize_different_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            claim_permit_once(root, self.authority(), "run-a", "plan-a")
            with self.assertRaisesRegex(RuntimeError, "run-a"):
                claim_permit_once(root, self.authority(), "run-b", "plan-b")


if __name__ == "__main__":
    unittest.main()
