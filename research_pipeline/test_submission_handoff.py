from __future__ import annotations

import copy
import tempfile
import unittest
import zipfile
from pathlib import Path

from .presubmission_freeze import artifact, build_freeze, digest, publish_freeze
from .submission_handoff import (
    HANDOFF_STATUS,
    append_handoff,
    build_handoff_receipt,
    validate_handoff_ledger,
    validate_handoff_receipt,
)
from .test_presubmission_freeze import PreSubmissionFreezeTest


class SubmissionHandoffTest(unittest.TestCase):
    def ready_fixture(self, root: Path):
        helper = PreSubmissionFreezeTest(methodName="test_artifact_hash_changes_when_bytes_change")
        helper.ready(root)
        paper = root / "paper.pdf"
        source = root / "source.zip"
        paper.write_bytes(b"paper-bytes")
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr(
                "main.tex",
                "\\title{Freeze paper}\n\\begin{document}\n\\begin{abstract}Frozen abstract for handoff tests.\\end{abstract}\n\\section*{AI Use Statement}AI tools assisted editing.\n\\end{document}\n",
            )
        policy = {
            "schema_version": "1.0",
            "venue": "TEST 2027",
            "deadlines_aoe": {"abstract": "2026-09-18", "full_paper": "2026-09-25"},
            "paper_rules": {"ai_use_statement_required": True},
            "author_rules": {"all_authors_require_openreview_profile": True},
            "human_only_confirmation_required": True,
            "scientific_authority": False,
            "submission_authority": False,
        }
        policy["snapshot_sha256"] = digest(policy)
        freeze = build_freeze("FREEZE-PAPER", [artifact("paper_pdf", paper), artifact("source_zip", source)], policy, root)
        freeze_ledger = publish_freeze(freeze, root)
        import json
        paper_ledger = json.loads((root / "paper-acceptance" / "FREEZE-PAPER.json").read_text())
        return paper_ledger, freeze_ledger, policy, paper

    def test_handoff_requires_current_freeze_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paper_ledger, freeze_ledger, policy, _ = self.ready_fixture(root)
            receipt = build_handoff_receipt(paper_ledger=paper_ledger, freeze_ledger=freeze_ledger, venue_policy=policy)
            self.assertEqual(receipt["status"], HANDOFF_STATUS)
            self.assertTrue(receipt["must_not_submit_if_hash_mismatch"])
            self.assertTrue(receipt["external_human_submission_authority_required"])
            self.assertTrue(validate_handoff_receipt(receipt))
            self.assertTrue(all("/" not in row["filename"] for row in receipt["frozen_artifacts"]))
            first = append_handoff(root, receipt)
            second = append_handoff(root, receipt)
            self.assertEqual(len(first["events"]), 1)
            self.assertEqual(len(second["events"]), 1)
            self.assertEqual(validate_handoff_ledger(second), [])

    def test_byte_drift_blocks_new_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paper_ledger, freeze_ledger, policy, paper = self.ready_fixture(root)
            paper.write_bytes(b"paper-changed-after-freeze")
            with self.assertRaisesRegex(RuntimeError, "frozen artifacts are stale"):
                build_handoff_receipt(paper_ledger=paper_ledger, freeze_ledger=freeze_ledger, venue_policy=policy)

    def test_policy_or_receipt_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paper_ledger, freeze_ledger, policy, _ = self.ready_fixture(root)
            bad_policy = dict(policy)
            bad_policy["venue"] = "TAMPERED"
            with self.assertRaisesRegex(RuntimeError, "venue policy snapshot digest mismatch"):
                build_handoff_receipt(paper_ledger=paper_ledger, freeze_ledger=freeze_ledger, venue_policy=bad_policy)
            receipt = build_handoff_receipt(paper_ledger=paper_ledger, freeze_ledger=freeze_ledger, venue_policy=policy)
            tampered = copy.deepcopy(receipt)
            tampered["freeze_sha256"] = "0" * 64
            self.assertFalse(validate_handoff_receipt(tampered))


if __name__ == "__main__":
    unittest.main()
