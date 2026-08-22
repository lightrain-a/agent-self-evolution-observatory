from __future__ import annotations

import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from .paper_anonymity_audit import (
    BLOCK_STATUS,
    PASS_STATUS,
    audit_double_blind_bundle,
    public_anonymity_audit,
    validate_anonymity_audit_receipt,
)


class PaperAnonymityAuditTest(unittest.TestCase):
    def zip(self, root: Path, name: str, files: dict[str, str]) -> Path:
        path = root / name
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for rel, text in files.items():
                archive.writestr(rel, text)
        return path

    def test_clean_anonymous_source_zip_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.zip(root, "source.zip", {
                "main.tex": r"\documentclass{article}\n\author{Anonymous Authors}\n\begin{document}Anonymous submission.\end{document}",
                "references.bib": "@article{x,title={A Safe Reference},author={Smith, A.},year={2025}}",
                "README.md": "Anonymous supplementary source. No public repository is required for review.",
            })
            receipt = audit_double_blind_bundle(artifacts=[{"label": "source_zip", "path": str(source)}])
            self.assertTrue(validate_anonymity_audit_receipt(receipt))
            self.assertEqual(receipt["status"], PASS_STATUS)
            self.assertTrue(receipt["pass"])
            self.assertEqual(receipt["finding_count"], 0)

    def test_source_identity_commands_email_orcid_and_acknowledgment_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.zip(root, "source.zip", {
                "main.tex": r"\author{Alice Example}\affiliation{Example University}\email{alice@example.edu}\orcid{0000-0002-1825-0097}\section*{Acknowledgments}Thanks to our lab.",
            })
            receipt = audit_double_blind_bundle(artifacts=[{"label": "source_zip", "path": str(source)}])
            self.assertEqual(receipt["status"], BLOCK_STATUS)
            codes = set(receipt["finding_codes"])
            self.assertIn("email-address-present", codes)
            self.assertIn("orcid-present", codes)
            self.assertIn("acknowledgment-section-present", codes)
            self.assertIn("latex-author-affiliation-identity-command-present", codes)

    def test_private_token_is_hashed_and_not_exposed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); token = "Secret Lab Name"
            source = self.zip(root, "source.zip", {"notes.txt": f"internal provenance: {token}"})
            receipt = audit_double_blind_bundle(artifacts=[{"label": "source_zip", "path": str(source)}], private_identity_tokens=[token])
            self.assertEqual(receipt["status"], BLOCK_STATUS)
            self.assertIn("private-identity-token-present", receipt["finding_codes"])
            raw = json.dumps(receipt, ensure_ascii=False)
            public = json.dumps(public_anonymity_audit(receipt), ensure_ascii=False)
            self.assertNotIn(token, raw)
            self.assertNotIn(token, public)
            self.assertNotIn(str(root), raw)

    def test_archive_hidden_vcs_or_editor_metadata_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.zip(root, "source.zip", {".git/config": "[remote]", ".vscode/settings.json": "{}", "main.tex": "anonymous"})
            receipt = audit_double_blind_bundle(artifacts=[{"label": "source_zip", "path": str(source)}])
            self.assertIn("archive-hidden-vcs-or-editor-metadata-present", receipt["finding_codes"])
            self.assertFalse(receipt["pass"])

    def test_absolute_paths_and_nonanonymous_repository_urls_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.zip(root, "source.zip", {"README.md": "Build from /home/alice/project and see https://github.com/alice/private-paper"})
            receipt = audit_double_blind_bundle(artifacts=[{"label": "source_zip", "path": str(source)}])
            codes = set(receipt["finding_codes"])
            self.assertIn("absolute-private-path-present", codes)
            self.assertIn("nonanonymous-repository-url-review-required", codes)

    def test_nonanonymous_repository_url_alone_is_review_warning_not_hard_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.zip(root, "source.zip", {"README.md": "Third-party baseline: https://github.com/example/baseline"})
            receipt = audit_double_blind_bundle(artifacts=[{"label": "source_zip", "path": str(source)}])
            self.assertTrue(receipt["pass"])
            self.assertEqual(receipt["blocking_finding_count"], 0)
            self.assertEqual(receipt["warning_count"], 1)
            self.assertIn("nonanonymous-repository-url-review-required", receipt["warning_codes"])

    def test_pdf_author_metadata_and_pdf_text_are_scanned_without_storing_leak(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); pdf = root / "main.pdf"; pdf.write_bytes(b"%PDF-fake")
            with patch("research_pipeline.paper_anonymity_audit._pdf_info", return_value=({"Author": "Alice Example", "Creator": "LaTeX"}, "Contact alice@example.edu")):
                receipt = audit_double_blind_bundle(artifacts=[{"label": "paper_pdf", "path": str(pdf)}])
            codes = set(receipt["finding_codes"])
            self.assertIn("pdf-author-metadata-not-anonymous", codes)
            self.assertIn("email-address-present", codes)
            self.assertNotIn("Alice Example", json.dumps(receipt))
            self.assertNotIn("alice@example.edu", json.dumps(receipt))

    def test_anonymous_pdf_metadata_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); pdf = root / "main.pdf"; pdf.write_bytes(b"%PDF-fake")
            with patch("research_pipeline.paper_anonymity_audit._pdf_info", return_value=({"Author": "Anonymous Authors", "Creator": "pdfTeX"}, "Anonymous submission")):
                receipt = audit_double_blind_bundle(artifacts=[{"label": "paper_pdf", "path": str(pdf)}])
            self.assertEqual(receipt["status"], PASS_STATUS)
            self.assertTrue(receipt["pass"])

    def test_receipt_tamper_is_detected_and_public_projection_is_minimal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.zip(root, "source.zip", {"main.tex": "anonymous"})
            receipt = audit_double_blind_bundle(artifacts=[{"label": "source_zip", "path": str(source)}])
            bad = copy.deepcopy(receipt); bad["submission_authority"] = True
            self.assertFalse(validate_anonymity_audit_receipt(bad))
            public = public_anonymity_audit(receipt)
            self.assertEqual(public["status"], PASS_STATUS)
            self.assertNotIn("artifact_manifest", public)
            self.assertNotIn("private_identity_token_hashes", public)
            self.assertNotIn("findings", public)


if __name__ == "__main__":
    unittest.main()
