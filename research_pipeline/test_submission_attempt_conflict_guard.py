from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from .presubmission_freeze import artifact
from .submission_attempt_lineage import build_attempt_plan, publish_attempt_plan
from .submission_attempt_post_submission import build_attempt_venue_decision
from .submission_attempt_workflow import (
    append_attempt_workflow_receipt,
    attempt_checklist_items,
    build_attempt_actual_submission,
    build_attempt_freeze,
    build_attempt_handoff,
    build_attempt_human_signoff,
    build_attempt_preparation,
    build_attempt_submission_conflict_guard,
    current_attempt_workflow_summary,
    validate_attempt_submission_conflict_guard,
    validate_attempt_workflow_ledger,
)
from .test_paper_preparation_protocol import passing_packet
from .test_submission_attempt_lineage import SubmissionAttemptLineageTest
from .test_submission_attempt_workflow import policy


class SubmissionAttemptConflictGuardTest(unittest.TestCase):
    def parent(self, root: Path) -> dict:
        helper = SubmissionAttemptLineageTest(methodName="test_rejected_paper_can_plan_paper_side_resubmission_without_rewriting_parent")
        ledger, _, _ = helper.learned_fixture(root, "REJECT")
        return ledger

    def plan(self, root: Path, parent: dict, venue: str) -> dict:
        plan = build_attempt_plan(
            paper_ledger=parent,
            target_venue=venue,
            attempt_type="RESUBMISSION",
            revision_categories=("WRITING",),
            scientific_contract_unchanged=True,
        )
        publish_attempt_plan(plan, root)
        return plan

    def signed_attempt(self, root: Path, plan: dict, tag: str):
        package = root / f"child-package-{tag}"
        package.mkdir(parents=True, exist_ok=True)
        pdf = package / "main.pdf"; pdf.write_bytes(f"pdf-{tag}".encode())
        source = package / "source.zip"; source.write_bytes(f"source-{tag}".encode())
        supplement = package / "supplement.zip"; supplement.write_bytes(f"supp-{tag}".encode())
        artifacts = [artifact("paper_pdf", pdf), artifact("source_zip", source), artifact("supplement_zip", supplement)]
        venue_policy = policy(plan["target_venue"])
        prep = build_attempt_preparation(attempt_plan=plan, preparation_packet=passing_packet())
        freeze = build_attempt_freeze(attempt_plan=plan, preparation_receipt=prep, artifacts=artifacts, venue_policy=venue_policy)
        handoff = build_attempt_handoff(attempt_plan=plan, preparation_receipt=prep, freeze_receipt=freeze, venue_policy=venue_policy)
        row = append_attempt_workflow_receipt(root, prep)
        row = append_attempt_workflow_receipt(root, freeze)
        row = append_attempt_workflow_receipt(root, handoff)
        checks = [item["check_id"] for item in attempt_checklist_items(handoff)]
        signoff = build_attempt_human_signoff(
            workflow_ledger=row,
            confirmed_check_ids=checks,
            external_human_confirmation_ref=f"human:signoff:{tag}",
            confirmed_at="2027-01-07T10:00:00+00:00",
            acknowledge_current_artifact_hashes=True,
            acknowledge_actual_submission_not_performed=True,
        )
        row = append_attempt_workflow_receipt(root, signoff)
        return row, signoff, artifacts

    def submit_direct(self, root: Path, row: dict, signoff: dict, artifacts: list[dict], tag: str):
        guard = build_attempt_submission_conflict_guard(root=root, workflow_ledger=row, signoff_receipt=signoff)
        row = append_attempt_workflow_receipt(root, guard)
        self.assertTrue(guard["pass"], guard.get("active_conflicts"))
        submission = build_attempt_actual_submission(
            workflow_ledger=row,
            signoff_receipt=signoff,
            conflict_guard_receipt=guard,
            venue_submission_id=f"submission-{tag}",
            venue_forum_ref=f"venue:submission-{tag}",
            uploaded_artifact_sha256={item["label"]: item["sha256"] for item in artifacts},
            submitted_at="2027-01-08T11:00:00+00:00",
            external_human_submission_authority_ref=f"human:upload:{tag}",
        )
        row = append_attempt_workflow_receipt(root, submission)
        return row, guard, submission

    def two_signed(self, root: Path):
        parent = self.parent(root)
        plan_a = self.plan(root, parent, "ICML 2027")
        plan_b = self.plan(root, parent, "NeurIPS 2027")
        row_a, signoff_a, artifacts_a = self.signed_attempt(root, plan_a, "a")
        row_b, signoff_b, artifacts_b = self.signed_attempt(root, plan_b, "b")
        return parent, (plan_a, row_a, signoff_a, artifacts_a), (plan_b, row_b, signoff_b, artifacts_b)

    def test_active_sibling_blocks_second_real_submission_and_leaves_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, a, b = self.two_signed(root)
            row_a, _, _ = self.submit_direct(root, a[1], a[2], a[3], "a")
            guard_b = build_attempt_submission_conflict_guard(root=root, workflow_ledger=b[1], signoff_receipt=b[2])
            self.assertTrue(validate_attempt_submission_conflict_guard(guard_b))
            self.assertFalse(guard_b["pass"])
            self.assertEqual(guard_b["status"], "ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING")
            self.assertEqual(len(guard_b["active_conflicts"]), 1)
            row_b = append_attempt_workflow_receipt(root, guard_b)
            self.assertEqual(current_attempt_workflow_summary(row_b)["status"], "ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING")
            self.assertEqual(current_attempt_workflow_summary(row_a)["actual_submission_status"], "SUBMITTED")

    def test_pass_guard_becomes_stale_if_sibling_submits_before_append(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, a, b = self.two_signed(root)
            guard_b = build_attempt_submission_conflict_guard(root=root, workflow_ledger=b[1], signoff_receipt=b[2])
            self.assertTrue(guard_b["pass"])
            row_b = append_attempt_workflow_receipt(root, guard_b)
            self.submit_direct(root, a[1], a[2], a[3], "a")
            submission_b = build_attempt_actual_submission(
                workflow_ledger=row_b,
                signoff_receipt=b[2],
                conflict_guard_receipt=guard_b,
                venue_submission_id="submission-b",
                venue_forum_ref="venue:submission-b",
                uploaded_artifact_sha256={item["label"]: item["sha256"] for item in b[3]},
                submitted_at="2027-01-08T11:00:01+00:00",
                external_human_submission_authority_ref="human:upload:b",
            )
            with self.assertRaisesRegex(RuntimeError, "conflict guard stale or blocked"):
                append_attempt_workflow_receipt(root, submission_b)
            fresh = build_attempt_submission_conflict_guard(root=root, workflow_ledger=row_b, signoff_receipt=b[2])
            self.assertFalse(fresh["pass"])

    def test_terminal_reject_releases_sibling_submission_guard(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            parent, a, b = self.two_signed(root)
            row_a, _, _ = self.submit_direct(root, a[1], a[2], a[3], "a")
            blocked = build_attempt_submission_conflict_guard(root=root, workflow_ledger=b[1], signoff_receipt=b[2])
            self.assertFalse(blocked["pass"])
            decision = build_attempt_venue_decision(
                paper_ledger=parent,
                workflow_ledger=row_a,
                decision_id="desk-reject-a",
                source_ref="venue:desk-reject-a",
                received_at="2027-01-09T12:00:00+00:00",
                decision="REJECT",
                decision_text="Desk reject.",
                decision_phase="PRE_REBUTTAL_TERMINAL",
                rebuttal_available=False,
            )
            row_a = append_attempt_workflow_receipt(root, decision)
            self.assertEqual(current_attempt_workflow_summary(row_a)["venue_decision"], "REJECT")
            released = build_attempt_submission_conflict_guard(root=root, workflow_ledger=b[1], signoff_receipt=b[2])
            self.assertTrue(released["pass"], released.get("active_conflicts"))

    def test_guard_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, _, b = self.two_signed(root)
            guard = build_attempt_submission_conflict_guard(root=root, workflow_ledger=b[1], signoff_receipt=b[2])
            bad = copy.deepcopy(guard)
            bad["status"] = "ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING"
            self.assertFalse(validate_attempt_submission_conflict_guard(bad))

    def test_two_concurrent_cli_submissions_yield_exactly_one_success(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, a, b = self.two_signed(root)
            script = Path(__file__).resolve().parents[1] / "scripts" / "record_submission_attempt_actual.py"

            def command(item, tag: str):
                plan, _, _, artifacts = item
                args = [
                    sys.executable, str(script), "--root", str(root), "--attempt-id", plan["attempt_id"],
                    "--venue-submission-id", f"race-{tag}", "--venue-forum-ref", f"venue:race-{tag}",
                    "--submitted-at", "2027-01-08T11:00:00+00:00",
                    "--external-human-submission-authority-ref", f"human:race:{tag}",
                ]
                for artifact_row in artifacts:
                    args.extend(["--uploaded-hash", f"{artifact_row['label']}={artifact_row['sha256']}"])
                return args

            proc_a = subprocess.Popen(command(a, "a"), cwd=Path(__file__).resolve().parents[1], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            proc_b = subprocess.Popen(command(b, "b"), cwd=Path(__file__).resolve().parents[1], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out_a, err_a = proc_a.communicate(timeout=30)
            out_b, err_b = proc_b.communicate(timeout=30)
            self.assertEqual(sorted([proc_a.returncode, proc_b.returncode]), [0, 2], (out_a, err_a, out_b, err_b))

            workflow_dir = root / "paper-submission-attempt-workflows"
            rows = [json.loads((workflow_dir / f"{item[0]['attempt_id']}.json").read_text()) for item in (a, b)]
            submissions = [sum(event.get("event_type") == "attempt-actual-submission" for event in row.get("events") or []) for row in rows]
            blocked_guards = [sum(event.get("event_type") == "attempt-submission-conflict-guard" and (event.get("receipt") or {}).get("pass") is False for event in row.get("events") or []) for row in rows]
            self.assertEqual(sum(submissions), 1, submissions)
            self.assertEqual(sum(value > 0 for value in blocked_guards), 1, blocked_guards)
            self.assertTrue(all(validate_attempt_workflow_ledger(row) == [] for row in rows))
            statuses = sorted(current_attempt_workflow_summary(row)["status"] for row in rows)
            self.assertEqual(statuses, ["ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING", "ATTEMPT_VENUE_SUBMISSION_CONFIRMED"])


if __name__ == "__main__":
    unittest.main()
