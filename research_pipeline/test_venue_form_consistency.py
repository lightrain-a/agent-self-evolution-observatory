from __future__ import annotations

import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from .presubmission_freeze import artifact, build_freeze, digest, publish_freeze
from .submission_handoff import append_handoff, build_handoff_receipt
from .test_presubmission_freeze import PreSubmissionFreezeTest
from .venue_form_consistency import (
    AUDIT_STATUS_PASS,
    AUTHOR_VISIBILITY_ANONYMOUS,
    _openreview_safe_text,
    append_venue_form_audit,
    build_form_contract_template,
    build_venue_form_audit_receipt,
    validate_venue_form_audit_ledger,
    validate_venue_form_audit_receipt,
    verify_current_venue_form_audit,
)


class VenueFormConsistencyTest(unittest.TestCase):
    def fixture(self, root: Path, *, include_ai: bool = True):
        helper = PreSubmissionFreezeTest(methodName="test_artifact_hash_changes_when_bytes_change")
        helper.ready(root)
        paper = root / "paper.pdf"
        paper.write_bytes(b"paper-bytes")
        source = root / "source.zip"
        ai = "\\section*{AI Use Statement}\nAI tools assisted editing.\n" if include_ai else ""
        tex = (
            "\\documentclass{article}\n"
            "\\title{Freeze paper}\n"
            "\\begin{document}\n"
            "\\maketitle\n"
            "\\begin{abstract}Frozen abstract for the venue form.\\end{abstract}\n"
            f"{ai}"
            "\\end{document}\n"
        )
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("main.tex", tex)
        policy = {
            "schema_version": "1.0",
            "venue": "TEST 2027",
            "deadlines_aoe": {"abstract": "2026-09-18", "full_paper": "2026-09-25"},
            "paper_rules": {"ai_use_statement_required": True, "double_blind": True},
            "author_rules": {"all_authors_require_openreview_profile": True},
            "human_only_confirmation_required": True,
            "scientific_authority": False,
            "submission_authority": False,
        }
        policy["snapshot_sha256"] = digest(policy)
        freeze = build_freeze(
            "FREEZE-PAPER",
            [artifact("paper_pdf", paper), artifact("source_zip", source)],
            policy,
            root,
        )
        freeze_ledger = publish_freeze(freeze, root)
        paper_ledger = json.loads((root / "paper-acceptance" / "FREEZE-PAPER.json").read_text())
        handoff = build_handoff_receipt(
            paper_ledger=paper_ledger,
            freeze_ledger=freeze_ledger,
            venue_policy=policy,
        )
        handoff_ledger = append_handoff(root, handoff)
        return paper_ledger, freeze_ledger, handoff_ledger, policy

    def completed_contract(self, template: dict) -> dict:
        contract = copy.deepcopy(template)
        contract["expected_fields"]["keywords"] = ["agents", "memory"]
        contract["expected_fields"]["ai_use_disclosure"] = {
            "used": True,
            "summary": "AI tools assisted editing.",
        }
        return contract

    def snapshot(self, contract: dict) -> dict:
        expected = contract["expected_fields"]
        return {
            "schema_version": "1.0",
            "paper_id": contract["paper_id"],
            "venue": contract["venue"],
            "capture_method": "OPENREVIEW_FINAL_FORM_EXPORT",
            "captured_at": "2026-09-24T12:00:00+00:00",
            "fields": {
                "title": expected["title"],
                "abstract": expected["abstract"],
                "keywords": ["memory", "agents"],
                "author_visibility": AUTHOR_VISIBILITY_ANONYMOUS,
                "ai_use_disclosure": copy.deepcopy(expected["ai_use_disclosure"]),
                "supplement_declared": expected["supplement_declared"],
                "supplement_artifacts": copy.deepcopy(expected["supplement_artifacts"]),
            },
        }

    def test_openreview_metadata_projection_preserves_math_and_maps_text_macros(self) -> None:
        source = r"We formulate \emph{Skill-Taxonomy Representation Invariance}; $R^*(A;q)=\min\{t:q\le Aw\le tq\}$ and W$\rightarrow$W differ in 21.0\% of seeds."
        projected = _openreview_safe_text(source)
        self.assertEqual(
            projected,
            r"We formulate *Skill-Taxonomy Representation Invariance*; $R^*(A;q)=\min\{t:q\le Aw\le tq\}$ and W$\rightarrow$W differ in 21.0% of seeds.",
        )

    def test_openreview_metadata_projection_rejects_unknown_text_mode_macro(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "unsupported OpenReview text-mode"):
            _openreview_safe_text(r"This uses \smallcaps{a source-only macro} outside math.")

    def test_template_is_bound_to_current_frozen_source_and_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            paper, freeze, handoff, policy = self.fixture(Path(td))
            template = build_form_contract_template(
                paper_ledger=paper,
                freeze_ledger=freeze,
                handoff_ledger=handoff,
                venue_policy=policy,
            )
            self.assertEqual(template["schema_version"], "1.1")
            self.assertEqual(template["expected_fields"]["title"], "Freeze paper")
            self.assertEqual(template["expected_fields"]["abstract"], "Frozen abstract for the venue form.")
            self.assertTrue(template["source_evidence"]["ai_use_statement_present"])
            self.assertEqual(template["expected_fields"]["author_visibility"], AUTHOR_VISIBILITY_ANONYMOUS)
            self.assertEqual(template["human_fill_required"], ["expected_fields.keywords", "expected_fields.ai_use_disclosure"])

    def test_pre_projection_form_contract_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            paper, freeze, handoff, policy = self.fixture(Path(td))
            contract = self.completed_contract(build_form_contract_template(
                paper_ledger=paper,
                freeze_ledger=freeze,
                handoff_ledger=handoff,
                venue_policy=policy,
            ))
            contract["schema_version"] = "1.0"
            contract["source_evidence"].pop("openreview_metadata_projection_version", None)
            with self.assertRaisesRegex(RuntimeError, "venue form contract invalid"):
                build_venue_form_audit_receipt(form_contract=contract, form_snapshot=self.snapshot(contract))

    def test_pass_receipt_is_append_only_and_current(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paper, freeze, handoff, policy = self.fixture(root)
            contract = self.completed_contract(build_form_contract_template(
                paper_ledger=paper,
                freeze_ledger=freeze,
                handoff_ledger=handoff,
                venue_policy=policy,
            ))
            receipt = build_venue_form_audit_receipt(form_contract=contract, form_snapshot=self.snapshot(contract))
            self.assertEqual(receipt["status"], AUDIT_STATUS_PASS)
            self.assertTrue(receipt["pass"])
            self.assertTrue(validate_venue_form_audit_receipt(receipt))
            row = append_venue_form_audit(root, receipt)
            row = append_venue_form_audit(root, receipt)
            self.assertEqual(len(row["events"]), 1)
            self.assertEqual(validate_venue_form_audit_ledger(row), [])
            self.assertEqual(verify_current_venue_form_audit(row, handoff, freeze), [])

    def test_stale_abstract_and_visibility_fail_field_level_audit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            paper, freeze, handoff, policy = self.fixture(Path(td))
            contract = self.completed_contract(build_form_contract_template(
                paper_ledger=paper,
                freeze_ledger=freeze,
                handoff_ledger=handoff,
                venue_policy=policy,
            ))
            snapshot = self.snapshot(contract)
            snapshot["fields"]["abstract"] = "Old abstract accidentally left in OpenReview."
            snapshot["fields"]["author_visibility"] = "PUBLIC"
            receipt = build_venue_form_audit_receipt(form_contract=contract, form_snapshot=snapshot)
            self.assertFalse(receipt["pass"])
            self.assertIn("venue-form-field-mismatch:abstract", receipt["blockers"])
            self.assertIn("venue-form-field-mismatch:author_visibility", receipt["blockers"])
            serialized = json.dumps(receipt, ensure_ascii=False)
            self.assertNotIn("Old abstract accidentally left in OpenReview.", serialized)
            self.assertNotIn("Frozen abstract for the venue form.", serialized)

    def test_missing_required_ai_use_statement_blocks_contract_generation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            paper, freeze, handoff, policy = self.fixture(Path(td), include_ai=False)
            with self.assertRaisesRegex(RuntimeError, "venue requires AI-use statement"):
                build_form_contract_template(
                    paper_ledger=paper,
                    freeze_ledger=freeze,
                    handoff_ledger=handoff,
                    venue_policy=policy,
                )


if __name__ == "__main__":
    unittest.main()
