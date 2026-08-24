from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from .manuscript_integrity_audit import (
    audit_post_draft_integrity,
    build_post_draft_integrity_receipt,
    integrity_findings_to_reviewer_receipt,
    lint_machine_like_prose,
)
from .reviewer_issue_graph import build_reviewer_issue_graph


class ManuscriptIntegrityAuditTest(unittest.TestCase):
    def manifest(self, root: Path) -> dict:
        data = root / "results.json"
        data.write_text('{"accuracy":0.75,"n":40}\n', encoding="utf-8")
        script = root / "make_table.py"
        script.write_text("print('table')\n", encoding="utf-8")
        data_sha = hashlib.sha256(data.read_bytes()).hexdigest()
        script_sha = hashlib.sha256(script.read_bytes()).hexdigest()
        return {
            "manuscript_ref": "paper/main.tex",
            "manuscript_sha256": "a" * 64,
            "manuscript_text": "We define Temporal Skill (TS) at first use. The experiment tests the frozen claim.",
            "content_inventory": {"facts": 1, "citations": 1, "numbers": 1, "tables": 1, "claims": 1, "extraction_complete": True, "extractor_version": "integrity-extractor-v1", "extractor_sha256": "c" * 64},
            "facts": [{"fact_id": "F1", "source_ref": "paper:primary", "source_verified": True, "passage_support_verified": True}],
            "citations": [{"citation_id": "CIT1", "source_ref": "doi:10.test/x", "existence_verified": True, "metadata_identity_verified": True, "passage_support_verified": True, "directionality_verified": True, "scope_verified": True, "contains_numeric_claim": False}],
            "numbers": [{"number_id": "N1", "observed_value": 0.75, "source_value": 0.75, "source_artifact": "results.json", "source_artifact_sha256": data_sha, "source_field": "accuracy"}],
            "tables": [{"table_id": "T1", "generation_script": {"source_artifact": "make_table.py", "source_artifact_sha256": script_sha}, "cells": [{"cell_id": "r1c1", "observed_value": 40, "source_value": 40, "source_artifact": "results.json", "source_artifact_sha256": data_sha, "source_field": "n"}]}],
            "expected_claim_ids": ["K1"],
            "claims": [{"claim_id": "K1", "statement_ref": "sec:results:p2", "evidence_refs": ["results.json#accuracy"], "supported": True}],
            "reader_comprehension": {"terms": [{"term": "Temporal Skill", "first_use_defined": True}], "components": [{"component": "temporal filter", "input_explained": True, "output_explained": True}]},
        }

    def test_complete_manifest_passes_and_is_content_addressed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.manifest(root)
            audit = audit_post_draft_integrity(manifest, project_root=root)
            receipt = build_post_draft_integrity_receipt(manifest, project_root=root)
        self.assertEqual(audit["status"], "PASS_POST_DRAFT_INTEGRITY")
        self.assertTrue(audit["pass"])
        self.assertEqual(len(receipt["receipt_sha256"]), 64)
        self.assertFalse(receipt["scientific_authority"])
        self.assertFalse(receipt["experiment_authority"])

    def test_incomplete_inventory_or_unverified_citation_scope_cannot_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.manifest(root)
            manifest["content_inventory"]["extraction_complete"] = False
            manifest["citations"][0]["scope_verified"] = False
            audit = audit_post_draft_integrity(manifest, project_root=root)
        self.assertIn("content-inventory-extraction-not-complete", audit["hard_blockers"])
        self.assertTrue(any("scope-verified-failed" in item for item in audit["hard_blockers"]))

    def test_wrong_number_and_table_cell_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.manifest(root)
            manifest["numbers"][0]["observed_value"] = 0.76
            manifest["tables"][0]["cells"][0]["observed_value"] = 41
            audit = audit_post_draft_integrity(manifest, project_root=root)
        self.assertFalse(audit["pass"])
        self.assertIn("number:N1:value-mismatch", audit["hard_blockers"])
        self.assertIn("table:T1:cell:r1c1:value-mismatch", audit["hard_blockers"])

    def test_citation_checks_are_separate_and_numeric_scope_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.manifest(root)
            citation = manifest["citations"][0]
            citation.update({"directionality_verified": False, "contains_numeric_claim": True, "numeric_match_verified": False})
            audit = audit_post_draft_integrity(manifest, project_root=root)
        self.assertTrue(any("directionality-verified-failed" in item for item in audit["hard_blockers"]))
        self.assertTrue(any("numeric-match-not-verified" in item for item in audit["hard_blockers"]))

    def test_reader_first_use_and_component_io_are_editorial_not_scientific_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.manifest(root)
            manifest["reader_comprehension"]["terms"][0]["first_use_defined"] = False
            manifest["reader_comprehension"]["components"][0]["output_explained"] = False
            audit = audit_post_draft_integrity(manifest, project_root=root)
        self.assertTrue(audit["integrity_pass"])
        self.assertFalse(audit["editorial_pass"])
        self.assertIn("term-first-use-not-defined:Temporal Skill", audit["editorial_blockers"])
        self.assertFalse(audit["scientific_authority"])

    def test_machine_like_prose_lint_is_not_ai_detector_evasion(self) -> None:
        lint = lint_machine_like_prose("It is worth noting that this comprehensive framework paves the way for future work.")
        self.assertGreater(lint["warning_count"], 0)
        self.assertFalse(lint["ai_detector_evasion_goal"])

    def test_integrity_findings_enter_issue_graph_without_experiment_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.manifest(root)
            manifest["numbers"][0]["observed_value"] = 0.99
            audit = audit_post_draft_integrity(manifest, project_root=root)
        receipt = integrity_findings_to_reviewer_receipt(audit)
        graph = build_reviewer_issue_graph(paper_id="P1", review_receipts=[receipt])
        self.assertGreater(graph["summary"]["issues"], 0)
        self.assertEqual(graph["summary"]["targeted_experiment_proposals"], 0)
        self.assertEqual(graph["summary"]["experiment_authorized"], 0)


if __name__ == "__main__":
    unittest.main()
