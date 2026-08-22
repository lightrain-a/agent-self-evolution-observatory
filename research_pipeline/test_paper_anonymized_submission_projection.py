from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from .paper_anonymity_audit import audit_double_blind_bundle
from .paper_anonymized_submission_projection import sanitize_submission_zip, validate_projection_receipt


class PaperAnonymizedSubmissionProjectionTest(unittest.TestCase):
    def source_zip(self, root: Path, *, unsafe_tex: bool = False) -> Path:
        path = root / "source.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("evidence.json", json.dumps({"artifact": {"path": "/data/private/project/evidence.json", "sha256": "a" * 64}, "nested": ["/home/user/run/raw"]}))
            z.writestr("main.tex", "\\author{Anonymous Authors}\n" + ("\\input{/home/user/private.tex}\n" if unsafe_tex else "Anonymous submission\n"))
        return path

    def test_projection_redacts_json_paths_preserves_sealed_source_and_passes_audit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.source_zip(root); before = source.read_bytes(); out = root / "anon.zip"
            receipt = sanitize_submission_zip(source_zip=source, output_zip=out)
            self.assertTrue(validate_projection_receipt(receipt))
            self.assertEqual(source.read_bytes(), before)
            self.assertTrue(receipt["canonical_scientific_artifacts_unchanged"])
            self.assertTrue(receipt["requires_new_submission_freeze"])
            self.assertTrue(receipt["automatic_refreeze_forbidden"])
            self.assertEqual(receipt["redaction_count"], 2)
            with zipfile.ZipFile(out) as z:
                text = z.read("evidence.json").decode()
                self.assertNotIn("/data/private", text); self.assertNotIn("/home/user", text)
                self.assertIn("private-path-ref:sha256:", text)
                manifest = json.loads(z.read("anonymized-submission-projection.json"))
                self.assertEqual(manifest["source_sha256"], hashlib.sha256(before).hexdigest())
                self.assertTrue(manifest["canonical_scientific_artifacts_unchanged"])
            audit = audit_double_blind_bundle(artifacts=[{"label": "sanitized_zip", "path": str(out)}])
            self.assertTrue(audit["pass"]); self.assertEqual(audit["blocking_finding_count"], 0)

    def test_projection_is_deterministic_for_same_source(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.source_zip(root); a = root / "a.zip"; b = root / "b.zip"
            ra = sanitize_submission_zip(source_zip=source, output_zip=a); rb = sanitize_submission_zip(source_zip=source, output_zip=b)
            self.assertEqual(hashlib.sha256(a.read_bytes()).hexdigest(), hashlib.sha256(b.read_bytes()).hexdigest())
            self.assertEqual(ra["changed_entries"], rb["changed_entries"])
            self.assertEqual(ra["redaction_count"], rb["redaction_count"])

    def test_nonmetadata_private_path_requires_manual_repair_and_leaves_no_partial_projection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.source_zip(root, unsafe_tex=True); out = root / "anon.zip"
            with self.assertRaisesRegex(RuntimeError, "non-metadata text"):
                sanitize_submission_zip(source_zip=source, output_zip=out)
            self.assertFalse(out.exists()); self.assertFalse((root / "anon.zip.tmp").exists())

    def test_projection_never_overwrites_source(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.source_zip(root)
            with self.assertRaisesRegex(RuntimeError, "must not overwrite"):
                sanitize_submission_zip(source_zip=source, output_zip=source)

    def test_receipt_tamper_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = self.source_zip(root); receipt = sanitize_submission_zip(source_zip=source, output_zip=root / "anon.zip")
            bad = copy.deepcopy(receipt); bad["automatic_refreeze_forbidden"] = False
            self.assertFalse(validate_projection_receipt(bad))


if __name__ == "__main__":
    unittest.main()
