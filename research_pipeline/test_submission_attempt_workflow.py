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
    build_attempt_freeze,
    build_attempt_handoff,
    build_attempt_preparation,
    current_attempt_workflow_summary,
    validate_attempt_freeze,
    validate_attempt_handoff,
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


if __name__ == "__main__":
    unittest.main()
