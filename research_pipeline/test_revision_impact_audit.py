from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from .presubmission_freeze import artifact
from .revision_impact_audit import audit_freeze_receipt


class RevisionImpactAuditTest(unittest.TestCase):
    def write_zip(self, path: Path, files: dict[str, str], *, year: int = 2026) -> None:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name, text in sorted(files.items()):
                info = zipfile.ZipInfo(name)
                info.date_time = (year, 1, 1, 0, 0, 0)
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, text.encode("utf-8"))

    def freeze(self, zip_path: Path) -> dict:
        return {
            "paper_id": "REVISION-PAPER",
            "freeze_sha256": "f" * 64,
            "frozen_artifacts": [artifact("source_zip", zip_path)],
        }

    def test_no_change_requires_no_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "source.zip"
            self.write_zip(path, {"main.tex": "A claim.\n", "references.bib": "@article{x,title={X}}\n"})
            result = audit_freeze_receipt(self.freeze(path))
            self.assertEqual(result["status"], "NO_CHANGE")
            self.assertEqual(result["impact_classes"], [])
            self.assertFalse(result["invalidate_pre_submission_freeze"])

    def test_container_metadata_only_is_packaging_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "source.zip"
            files = {"main.tex": "A claim.\n", "references.bib": "@article{x,title={X}}\n"}
            self.write_zip(path, files, year=2026)
            frozen = self.freeze(path)
            self.write_zip(path, files, year=2027)
            result = audit_freeze_receipt(frozen)
            self.assertEqual(result["impact_classes"], ["PACKAGING_ONLY"])
            self.assertEqual(result["minimum_rerun_paper_preparation_gates"], ["submission-package"])
            self.assertEqual(result["minimum_rerun_paper_acceptance_checks"], [])

    def test_tex_whitespace_only_is_format_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "source.zip"
            self.write_zip(path, {"main.tex": "A  claim.\n"})
            frozen = self.freeze(path)
            self.write_zip(path, {"main.tex": "A claim.\n"})
            result = audit_freeze_receipt(frozen)
            self.assertIn("FORMAT_ONLY", result["impact_classes"])
            self.assertIn("visual-story", result["minimum_rerun_paper_preparation_gates"])
            self.assertIn("manuscript-ci", result["minimum_rerun_paper_acceptance_checks"])
            self.assertNotIn("claim-audit", result["minimum_rerun_paper_acceptance_checks"])

    def test_semantic_manuscript_change_reopens_claim_facing_checks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "source.zip"
            self.write_zip(path, {"sections/01_intro.tex": "The effect is 10 percent.\n"})
            frozen = self.freeze(path)
            self.write_zip(path, {"sections/01_intro.tex": "The effect is 20 percent.\n"})
            result = audit_freeze_receipt(frozen)
            self.assertIn("MANUSCRIPT_TEXT", result["impact_classes"])
            self.assertIn("claim-audit", result["minimum_rerun_paper_acceptance_checks"])
            self.assertIn("reader-simulation", result["minimum_rerun_paper_preparation_gates"])
            self.assertFalse(result["new_scientific_experiment_authorized"])

    def test_evidence_change_requires_evidence_review_without_authorizing_experiment(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "supplement.zip"
            self.write_zip(path, {"evidence/result.json": '{"score": 1}\n'})
            frozen = self.freeze(path)
            self.write_zip(path, {"evidence/result.json": '{"score": 2}\n'})
            result = audit_freeze_receipt(frozen)
            self.assertIn("EVIDENCE_DATA", result["impact_classes"])
            self.assertTrue(result["scientific_evidence_review_required"])
            self.assertIn("claim-audit", result["minimum_rerun_paper_acceptance_checks"])
            self.assertIn("reproducibility-bundle", result["minimum_rerun_paper_preparation_gates"])
            self.assertFalse(result["new_scientific_experiment_authorized"])

    def test_legacy_zip_without_expanded_manifest_fails_closed_on_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "source.zip"
            self.write_zip(path, {"main.tex": "A claim.\n"})
            frozen = self.freeze(path)
            frozen["frozen_artifacts"][0].pop("expanded_manifest", None)
            self.write_zip(path, {"main.tex": "A different claim.\n"})
            result = audit_freeze_receipt(frozen)
            self.assertEqual(result["impact_classes"], ["UNCLASSIFIED_LEGACY_FREEZE"])
            self.assertTrue(result["requires_full_preparation_reaudit"])
            self.assertEqual(len(result["minimum_rerun_paper_preparation_gates"]), 8)


if __name__ == "__main__":
    unittest.main()
