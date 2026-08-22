from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .presubmission_freeze import artifact
from .submission_attempt_lineage import build_attempt_plan, publish_attempt_plan
from .submission_attempt_workflow import (
    append_attempt_workflow_receipt,
    attempt_checklist_items,
    build_attempt_actual_submission,
    build_attempt_freeze,
    build_attempt_handoff,
    build_attempt_human_signoff,
    build_attempt_preparation,
    build_attempt_signoff_template,
    current_attempt_workflow_summary,
    validate_attempt_actual_submission,
    validate_attempt_freeze,
    validate_attempt_handoff,
    validate_attempt_human_signoff,
    validate_attempt_preparation,
    validate_attempt_workflow_ledger,
)
from .test_paper_preparation_protocol import passing_packet
from .test_submission_attempt_lineage import SubmissionAttemptLineageTest


def policy(venue: str) -> dict:
    row = {
        "schema_version": "1.0",
        "venue": venue,
        "deadlines_aoe": {"abstract": "2027-01-01", "full_paper": "2027-01-08"},
        "human_only_confirmation_required": True,
    }
    raw = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    row["snapshot_sha256"] = hashlib.sha256(raw).hexdigest()
    return row


class SubmissionAttemptWorkflowTest(unittest.TestCase):
    def safe_attempt(self, root: Path, venue: str = "ICML 2027"):
        helper = SubmissionAttemptLineageTest(methodName="test_rejected_paper_can_plan_paper_side_resubmission_without_rewriting_parent")
        ledger, _, _ = helper.learned_fixture(root, "REJECT")
        plan = build_attempt_plan(
            paper_ledger=ledger,
            target_venue=venue,
            attempt_type="RESUBMISSION",
            revision_categories=("WRITING", "PAPER_POSITIONING"),
            scientific_contract_unchanged=True,
        )
        publish_attempt_plan(plan, root)
        return ledger, plan

    def artifacts(self, root: Path):
        package = root / "child-package"; package.mkdir(parents=True, exist_ok=True)
        pdf = package / "main.pdf"; pdf.write_bytes(b"child-pdf-v1")
        source = package / "source.zip"; source.write_bytes(b"source-v1")
        supplement = package / "supplement.zip"; supplement.write_bytes(b"supp-v1")
        return pdf, [artifact("paper_pdf", pdf), artifact("source_zip", source), artifact("supplement_zip", supplement)]

    def handoff_fixture(self, root: Path):
        parent, plan = self.safe_attempt(root)
        pdf, artifacts = self.artifacts(root)
        venue_policy = policy(plan["target_venue"])
        prep = build_attempt_preparation(attempt_plan=plan, preparation_packet=passing_packet())
        freeze = build_attempt_freeze(attempt_plan=plan, preparation_receipt=prep, artifacts=artifacts, venue_policy=venue_policy)
        handoff = build_attempt_handoff(attempt_plan=plan, preparation_receipt=prep, freeze_receipt=freeze, venue_policy=venue_policy)
        row = append_attempt_workflow_receipt(root, prep)
        row = append_attempt_workflow_receipt(root, freeze)
        row = append_attempt_workflow_receipt(root, handoff)
        return parent, plan, pdf, artifacts, prep, freeze, handoff, row

    def test_attempt_scoped_preparation_freeze_handoff_is_append_only_and_ready(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent, plan = self.safe_attempt(root)
            pdf, artifacts = self.artifacts(root)
            prep = build_attempt_preparation(attempt_plan=plan, preparation_packet=passing_packet())
            self.assertTrue(validate_attempt_preparation(prep))
            freeze = build_attempt_freeze(attempt_plan=plan, preparation_receipt=prep, artifacts=artifacts, venue_policy=policy(plan["target_venue"]))
            self.assertTrue(validate_attempt_freeze(freeze))
            handoff = build_attempt_handoff(attempt_plan=plan, preparation_receipt=prep, freeze_receipt=freeze, venue_policy=policy(plan["target_venue"]))
            self.assertTrue(validate_attempt_handoff(handoff))

            row = append_attempt_workflow_receipt(root, prep)
            row = append_attempt_workflow_receipt(root, freeze)
            row = append_attempt_workflow_receipt(root, handoff)
            row2 = append_attempt_workflow_receipt(root, handoff)
            self.assertEqual(len(row["events"]), 3)
            self.assertEqual(len(row2["events"]), 3)
            self.assertEqual(validate_attempt_workflow_ledger(row2), [])
            summary = current_attempt_workflow_summary(row2)
            self.assertEqual(summary["status"], "ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED")
            self.assertEqual(summary["frozen_artifacts"], 3)
            self.assertTrue(summary["parent_submission_bytes_immutable"])
            self.assertNotIn(str(root), json.dumps(summary))
            workflow = root / "paper-submission-attempt-workflows" / f"{plan['attempt_id']}.json"
            self.assertTrue(workflow.exists())

            canonical = json.loads((root / "paper-acceptance" / f"{parent['paper_id']}.json").read_text())
            before = next(event["receipt"]["submission_receipt_sha256"] for event in parent["events"] if event.get("event_type") == "actual-submission")
            after = next(event["receipt"]["submission_receipt_sha256"] for event in canonical["events"] if event.get("event_type") == "actual-submission")
            self.assertEqual(before, after)
            self.assertEqual(canonical["current_state"], "LEARN")
            self.assertTrue(pdf.exists())

    def test_scientific_reopen_attempt_cannot_enter_machine_preparation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            helper = SubmissionAttemptLineageTest(methodName="test_scientific_change_requires_explicit_reopen_and_never_grants_authority")
            ledger, _, _ = helper.learned_fixture(root, "REJECT")
            plan = build_attempt_plan(
                paper_ledger=ledger,
                target_venue="ICML 2027",
                attempt_type="RESUBMISSION",
                revision_categories=("EXPERIMENT",),
                scientific_contract_unchanged=True,
                new_experiment_requested=True,
            )
            with self.assertRaisesRegex(RuntimeError, "explicit scientific reopen"):
                build_attempt_preparation(attempt_plan=plan, preparation_packet=passing_packet())

    def test_artifact_drift_revokes_attempt_handoff_currentness(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, plan = self.safe_attempt(root)
            pdf, artifacts = self.artifacts(root)
            prep = build_attempt_preparation(attempt_plan=plan, preparation_packet=passing_packet())
            freeze = build_attempt_freeze(attempt_plan=plan, preparation_receipt=prep, artifacts=artifacts, venue_policy=policy(plan["target_venue"]))
            handoff = build_attempt_handoff(attempt_plan=plan, preparation_receipt=prep, freeze_receipt=freeze, venue_policy=policy(plan["target_venue"]))
            row = append_attempt_workflow_receipt(root, prep)
            row = append_attempt_workflow_receipt(root, freeze)
            row = append_attempt_workflow_receipt(root, handoff)
            pdf.write_bytes(b"child-pdf-v2-after-freeze")
            summary = current_attempt_workflow_summary(row)
            self.assertEqual(summary["status"], "ATTEMPT_HANDOFF_STALE")
            self.assertIn("freeze-artifact-drift:paper_pdf", summary["freeze_drift_errors"])

    def test_attempt_workflows_use_distinct_attempt_namespaces(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            helper = SubmissionAttemptLineageTest(methodName="test_child_attempt_must_reference_prior_immutable_attempt")
            ledger, _, _ = helper.learned_fixture(root, "REJECT")
            plans = []
            for venue in ("ICML 2027", "NeurIPS 2027"):
                plan = build_attempt_plan(
                    paper_ledger=ledger,
                    target_venue=venue,
                    attempt_type="RESUBMISSION",
                    revision_categories=("WRITING",),
                    scientific_contract_unchanged=True,
                )
                plans.append(plan)
                prep = build_attempt_preparation(attempt_plan=plan, preparation_packet=passing_packet())
                append_attempt_workflow_receipt(root, prep)
            self.assertNotEqual(plans[0]["attempt_id"], plans[1]["attempt_id"])
            files = sorted((root / "paper-submission-attempt-workflows").glob("*.json"))
            self.assertEqual(len(files), 2)

    def test_target_policy_mismatch_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, plan = self.safe_attempt(root)
            _, artifacts = self.artifacts(root)
            prep = build_attempt_preparation(attempt_plan=plan, preparation_packet=passing_packet())
            with self.assertRaisesRegex(RuntimeError, "target venue"):
                build_attempt_freeze(attempt_plan=plan, preparation_receipt=prep, artifacts=artifacts, venue_policy=policy("Different Venue"))

    def test_workflow_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, plan = self.safe_attempt(root)
            prep = build_attempt_preparation(attempt_plan=plan, preparation_packet=passing_packet())
            row = append_attempt_workflow_receipt(root, prep)
            bad = copy.deepcopy(row)
            bad["events"][0]["receipt"]["status"] = "TAMPERED"
            self.assertIn("attempt-workflow-receipt-invalid", validate_attempt_workflow_ledger(bad))

    def test_attempt_human_signoff_and_actual_submission_are_attempt_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent, plan, _, artifacts, _, freeze, handoff, row = self.handoff_fixture(root)
            template = build_attempt_signoff_template(row)
            required = [item["check_id"] for item in template["required_confirmations"]]
            self.assertEqual(required, [item["check_id"] for item in attempt_checklist_items(handoff)])
            signoff = build_attempt_human_signoff(
                workflow_ledger=row,
                confirmed_check_ids=required,
                external_human_confirmation_ref="human:child-attempt-approval",
                confirmed_at="2027-01-07T10:00:00+00:00",
                acknowledge_current_artifact_hashes=True,
                acknowledge_actual_submission_not_performed=True,
            )
            self.assertTrue(validate_attempt_human_signoff(signoff))
            self.assertTrue(signoff["parent_signoff_reuse_forbidden"])
            row = append_attempt_workflow_receipt(root, signoff)
            self.assertEqual(current_attempt_workflow_summary(row)["status"], "ATTEMPT_HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING")

            uploaded = {item["label"]: item["sha256"] for item in artifacts}
            submission = build_attempt_actual_submission(
                workflow_ledger=row,
                signoff_receipt=signoff,
                venue_submission_id="child-submission-001",
                venue_forum_ref="venue:child-submission-001",
                uploaded_artifact_sha256=uploaded,
                submitted_at="2027-01-08T11:00:00+00:00",
                external_human_submission_authority_ref="human:child-upload-confirmed",
            )
            self.assertTrue(validate_attempt_actual_submission(submission))
            self.assertTrue(submission["parent_submission_receipt_reuse_forbidden"])
            row = append_attempt_workflow_receipt(root, submission)
            summary = current_attempt_workflow_summary(row)
            self.assertEqual(summary["status"], "ATTEMPT_VENUE_SUBMISSION_CONFIRMED")
            self.assertEqual(summary["venue_submission_id"], "child-submission-001")
            self.assertEqual(summary["actual_submission_status"], "SUBMITTED")
            self.assertEqual(validate_attempt_workflow_ledger(row), [])

            canonical = json.loads((root / "paper-acceptance" / f"{parent['paper_id']}.json").read_text())
            self.assertEqual(canonical["current_state"], "LEARN")
            parent_submission = next(event["receipt"] for event in canonical["events"] if event.get("event_type") == "actual-submission")
            self.assertNotEqual(parent_submission["submission_receipt_sha256"], submission["attempt_submission_receipt_sha256"])
            self.assertEqual(freeze["attempt_sha256"], plan["attempt_sha256"])

    def test_attempt_signoff_requires_every_child_confirmation_and_current_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, pdf, _, _, _, handoff, row = self.handoff_fixture(root)
            required = [item["check_id"] for item in attempt_checklist_items(handoff)]
            with self.assertRaisesRegex(RuntimeError, "missing human confirmations"):
                build_attempt_human_signoff(
                    workflow_ledger=row,
                    confirmed_check_ids=required[:-1],
                    external_human_confirmation_ref="human:partial",
                    confirmed_at="2027-01-07T10:00:00+00:00",
                    acknowledge_current_artifact_hashes=True,
                    acknowledge_actual_submission_not_performed=True,
                )
            pdf.write_bytes(b"drift-before-child-signoff")
            with self.assertRaisesRegex(RuntimeError, "handoff is not current"):
                build_attempt_human_signoff(
                    workflow_ledger=row,
                    confirmed_check_ids=required,
                    external_human_confirmation_ref="human:all",
                    confirmed_at="2027-01-07T10:00:00+00:00",
                    acknowledge_current_artifact_hashes=True,
                    acknowledge_actual_submission_not_performed=True,
                )

    def test_attempt_actual_submission_rejects_hash_mismatch_and_stale_signoff(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, pdf, artifacts, _, _, handoff, row = self.handoff_fixture(root)
            required = [item["check_id"] for item in attempt_checklist_items(handoff)]
            signoff = build_attempt_human_signoff(
                workflow_ledger=row,
                confirmed_check_ids=required,
                external_human_confirmation_ref="human:child",
                confirmed_at="2027-01-07T10:00:00+00:00",
                acknowledge_current_artifact_hashes=True,
                acknowledge_actual_submission_not_performed=True,
            )
            row = append_attempt_workflow_receipt(root, signoff)
            bad_uploaded = {item["label"]: item["sha256"] for item in artifacts}
            bad_uploaded["paper_pdf"] = "0" * 64
            with self.assertRaisesRegex(RuntimeError, "hashes do not match"):
                build_attempt_actual_submission(
                    workflow_ledger=row,
                    signoff_receipt=signoff,
                    venue_submission_id="child-002",
                    venue_forum_ref="venue:child-002",
                    uploaded_artifact_sha256=bad_uploaded,
                    submitted_at="2027-01-08T11:00:00+00:00",
                    external_human_submission_authority_ref="human:upload",
                )
            pdf.write_bytes(b"drift-after-signoff-before-submit")
            with self.assertRaisesRegex(RuntimeError, "frozen artifacts are stale"):
                build_attempt_actual_submission(
                    workflow_ledger=row,
                    signoff_receipt=signoff,
                    venue_submission_id="child-002",
                    venue_forum_ref="venue:child-002",
                    uploaded_artifact_sha256={item["label"]: item["sha256"] for item in artifacts},
                    submitted_at="2027-01-08T11:00:00+00:00",
                    external_human_submission_authority_ref="human:upload",
                )

    def test_confirmed_child_submission_remains_historical_when_local_files_change_later(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, pdf, artifacts, _, _, handoff, row = self.handoff_fixture(root)
            required = [item["check_id"] for item in attempt_checklist_items(handoff)]
            signoff = build_attempt_human_signoff(
                workflow_ledger=row,
                confirmed_check_ids=required,
                external_human_confirmation_ref="human:child",
                confirmed_at="2027-01-07T10:00:00+00:00",
                acknowledge_current_artifact_hashes=True,
                acknowledge_actual_submission_not_performed=True,
            )
            row = append_attempt_workflow_receipt(root, signoff)
            submission = build_attempt_actual_submission(
                workflow_ledger=row,
                signoff_receipt=signoff,
                venue_submission_id="child-003",
                venue_forum_ref="venue:child-003",
                uploaded_artifact_sha256={item["label"]: item["sha256"] for item in artifacts},
                submitted_at="2027-01-08T11:00:00+00:00",
                external_human_submission_authority_ref="human:upload",
            )
            row = append_attempt_workflow_receipt(root, submission)
            pdf.write_bytes(b"local-working-copy-changed-after-real-submit")
            summary = current_attempt_workflow_summary(row)
            self.assertEqual(summary["status"], "ATTEMPT_VENUE_SUBMISSION_CONFIRMED")
            self.assertTrue(summary["freeze_drift_errors"])
            self.assertEqual(summary["actual_submission_status"], "SUBMITTED")


if __name__ == "__main__":
    unittest.main()
