from __future__ import annotations

import json
import tempfile
import unittest
import warnings
from pathlib import Path

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld, prepare_appworld_runtime_root
from research_pipeline.agent_constraint_externality_capability_substrate_recovery_r2 import (
    BUNDLE,
    run_public_oracle,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
CONTRACT = ROOT / "generated/agent-constraint-externality-capability-substrate-v2-contract-20260902.json"
VOID = ROOT / "generated/agent-constraint-externality-capability-substrate-invalid-void-r2-20260902.json"
QUAL = ROOT / "generated/agent-constraint-externality-capability-substrate-recovery-qualification-r2-20260902.json"
R3 = ROOT / "generated/agent-constraint-externality-qwen37plus-capability-r3-contract-20260902.json"
ROOT_CAUSE = ROOT / "generated/agent-constraint-externality-capability-r2-root-cause-audit-20260902.json"


def parse(output):
    text = str(output).strip()
    if text.startswith("Execution failed"):
        raise AssertionError(text)
    return json.loads(text)


class CapabilitySubstrateV2Tests(unittest.TestCase):
    def test_v2_bundle_makes_tnf_locator_agent_visible_without_scientific_change(self) -> None:
        spec = load_protected_spec(BUNDLE)
        tnf = [family for family in spec["families"] if family["category"] == "TODO_NOTE_FILE"]
        self.assertEqual(len(tnf), 6)
        for family in tnf:
            self.assertIn("Use Inbox todo ", family["target_instruction"])
            self.assertTrue(all("Use Inbox todo " in arm["task_instruction"] for arm in family["arms"]))
            self.assertEqual({arm["matching"]["tool_budget"] for arm in family["arms"]}, {12})
            self.assertEqual({len(arm["constraints"]) for arm in family["arms"]}, {3})
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "CAPABILITY_SUBSTRATE_V2_STATIC_REPAIR_READY")
        self.assertFalse(contract["protected_plaintext_persisted"])

    def test_public_oracles_use_no_private_fixture_ids_and_fit_frozen_cap(self) -> None:
        fg = run_public_oracle("ACE-FG-05")
        tnf = run_public_oracle("ACE-TNF-05")
        for row in (fg, tnf):
            self.assertTrue(row["within_cap"])
            self.assertTrue(row["target_success"])
            self.assertEqual(row["non_target_preservation"], 1.0)
            self.assertFalse(row["discoverability"]["private_fixture_ids_used"])
        self.assertLessEqual(fg["tool_calls"], 12)
        self.assertLessEqual(tnf["tool_calls"], 12)
        self.assertEqual(tnf["discoverability"]["note_id_source"], "PUBLIC_SIMPLE_NOTE_EXACT_SEARCH_RESULT")
        self.assertEqual(tnf["discoverability"]["todo_source"], "PUBLIC_TODOIST_INBOX_PROJECT_ID_0")

    def test_tnf_exact_note_and_inbox_todo_are_publicly_discoverable(self) -> None:
        spec = load_protected_spec(BUNDLE)
        family = next(f for f in spec["families"] if f["family_id"] == "ACE-TNF-05")
        arm = next(a for a in family["arms"] if a["coupling_level"] == "LOW")
        with tempfile.TemporaryDirectory() as directory, warnings.catch_warnings():
            warnings.simplefilter("ignore")
            runtime = Path(directory)
            prepare_appworld_runtime_root(APPWORLD_ROOT, runtime, family=family, arm=arm, task_id="acetnfdisc_1")
            world = AppWorldToolWorld(
                runtime_root=runtime,
                task_id="acetnfdisc_1",
                experiment_name="ace-tnf-discoverability-test",
                seed=1,
                allowed_apps=set(family["fixture"]["apps"]),
            )
            try:
                profile = parse(world.execute("supervisor__show_profile", {}))
                passwords = {
                    row["account_name"]: row["password"]
                    for row in parse(world.execute("supervisor__show_account_passwords", {}))
                }
                note_token = parse(world.execute("simple_note__login", {
                    "username": profile["email"], "password": passwords["simple_note"],
                }))["access_token"]
                todo_token = parse(world.execute("todoist__login", {
                    "username": profile["email"], "password": passwords["todoist"],
                }))["access_token"]
                notes = parse(world.execute("simple_note__search_notes", {
                    "query": "source-note-05", "page_limit": 5, "access_token": note_token,
                }))
                self.assertEqual(sum(row["title"] == "source-note-05" for row in notes), 1)
                inbox = parse(world.execute("todoist__show_tasks", {
                    "project_id": 0, "access_token": todo_token,
                }))
                tasks = list(inbox.get("no_section_tasks", []))
                for section in inbox.get("sections", []):
                    tasks.extend(section.get("tasks", []))
                self.assertEqual(sum(row["title"] == "source-report-05" for row in tasks), 1)
            finally:
                world.close()

    def test_file_gmail_semantic_evaluator_rejects_missing_attachments(self) -> None:
        spec = load_protected_spec(BUNDLE)
        family = next(f for f in spec["families"] if f["family_id"] == "ACE-FG-05")
        arm = next(a for a in family["arms"] if a["coupling_level"] == "LOW")
        with tempfile.TemporaryDirectory() as directory, warnings.catch_warnings():
            warnings.simplefilter("ignore")
            runtime = Path(directory)
            prepare_appworld_runtime_root(APPWORLD_ROOT, runtime, family=family, arm=arm, task_id="acefgeval_1")
            world = AppWorldToolWorld(
                runtime_root=runtime,
                task_id="acefgeval_1",
                experiment_name="ace-fg-evaluator-test",
                seed=1,
                allowed_apps=set(family["fixture"]["apps"]),
            )
            try:
                profile = parse(world.execute("supervisor__show_profile", {}))
                passwords = {
                    row["account_name"]: row["password"]
                    for row in parse(world.execute("supervisor__show_account_passwords", {}))
                }
                gmail_token = parse(world.execute("gmail__login", {
                    "username": profile["email"], "password": passwords["gmail"],
                }))["access_token"]
                parse(world.execute("gmail__send_email", {
                    "email_addresses": ["stmcco@gmail.com"],
                    "subject": "ACE-FG-05-delivery",
                    "body": "missing attachments on purpose",
                    "access_token": gmail_token,
                }))
                evaluation = world.save_and_evaluate(arm)
                self.assertFalse(evaluation["target_success"])
                self.assertEqual(evaluation["non_target_preservation"], 1.0)
            finally:
                world.close()

    def test_void_qualification_and_r3_contract_are_content_addressed(self) -> None:
        for path, status in (
            (VOID, "QWEN37PLUS_R2_VOID_SUBSTRATE_DISCOVERABILITY_INVALID"),
            (QUAL, "CAPABILITY_SUBSTRATE_V2_PUBLIC_REACHABILITY_PASS"),
            (R3, "QWEN37PLUS_CAPABILITY_R3_AUTHORIZED_AFTER_SUBSTRATE_V2"),
        ):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], status)
            claimed = payload["content_sha256"]
            unsigned = dict(payload)
            unsigned.pop("content_sha256")
            self.assertEqual(claimed, sha256_value(unsigned))
        self.assertFalse(json.loads(R3.read_text())["authority"]["f0"])
        root_cause = json.loads(ROOT_CAUSE.read_text(encoding="utf-8"))
        self.assertEqual(
            root_cause["status"],
            "R2_50_PERCENT_NOT_VALID_MODEL_CAPABILITY_ESTIMATE",
        )
        self.assertFalse(
            root_cause["scientific_adjudication"]["r2_model_selection_valid"]
        )
        self.assertFalse(
            root_cause["scientific_adjudication"]["model_switch_justified_by_r2"]
        )
        self.assertEqual(root_cause["provider_requests_added_by_audit"], 0)
        claimed = root_cause["content_sha256"]
        unsigned = dict(root_cause)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))


if __name__ == "__main__":
    unittest.main()
