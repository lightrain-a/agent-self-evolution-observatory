from __future__ import annotations

import json
import re
import tempfile
import warnings
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld, prepare_appworld_runtime_root
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v2-20260902.bundle"
SUBSTRATE_CONTRACT = GENERATED / "agent-constraint-externality-capability-substrate-v2-contract-20260902.json"
R2_RESULT = GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r2-20260901.json"
VOID_OUTPUT = GENERATED / "agent-constraint-externality-capability-substrate-invalid-void-r2-20260902.json"
QUAL_OUTPUT = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r2-20260902.json"
R3_CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-qwen37plus-capability-r3-contract-20260902.json"
R3_EXECUTION_ID = "QWEN37PLUS-CAPABILITY-R3-AUTH-SUBSTRATE-V2"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_output(output: Any) -> Any:
    text = str(output).strip()
    if text.startswith("Execution failed"):
        raise RuntimeError(text)
    return json.loads(text)


def login(world: AppWorldToolWorld, app: str, username: str, password: str) -> str:
    result = parse_output(world.execute(app + "__login", {"username": username, "password": password}))
    return str(result["access_token"])


def _todo_tasks(response: dict[str, Any]) -> list[dict[str, Any]]:
    rows = list(response.get("no_section_tasks", []))
    for section in response.get("sections", []):
        rows.extend(section.get("tasks", []))
    return rows


def run_public_oracle(family_id: str) -> dict[str, Any]:
    spec = load_protected_spec(BUNDLE)
    family = next(item for item in spec["families"] if item["family_id"] == family_id)
    arm = next(item for item in family["arms"] if item["coupling_level"] == "LOW")
    with tempfile.TemporaryDirectory() as directory, warnings.catch_warnings():
        warnings.simplefilter("ignore")
        runtime = Path(directory)
        task_id = "acepublicoracle" + family_id.lower().replace("-", "") + "_1"
        materialized = prepare_appworld_runtime_root(APPWORLD_ROOT, runtime, family=family, arm=arm, task_id=task_id)
        world = AppWorldToolWorld(
            runtime_root=runtime,
            task_id=task_id,
            experiment_name="ace-capability-substrate-public-oracle-r2",
            seed=1,
            allowed_apps=set(family["fixture"]["apps"]),
        )
        calls = 0
        try:
            profile = parse_output(world.execute("supervisor__show_profile", {})); calls += 1
            password_rows = parse_output(world.execute("supervisor__show_account_passwords", {})); calls += 1
            active = parse_output(world.execute("supervisor__show_active_task", {})); calls += 1
            username = str(profile["email"])
            passwords = {str(row["account_name"]): str(row["password"]) for row in password_rows}
            if username != "aa_burt@gmail.com" or active["instruction"] != arm["task_instruction"]:
                raise RuntimeError("Public oracle supervisor/task binding mismatch.")

            if family["category"] == "FILE_GMAIL":
                match = re.search(
                    r"^Email (?P<recipient>\S+) with subject (?P<subject>\S+) and attach "
                    r"(?P<first>\S+) and (?P<second>\S+) from (?P<directory>~/[^.]+)\.",
                    arm["task_instruction"],
                )
                if match is None:
                    raise RuntimeError("Public FG oracle could not parse task instruction.")
                fs_token = login(world, "file_system", username, passwords["file_system"]); calls += 1
                gmail_token = login(world, "gmail", username, passwords["gmail"]); calls += 1
                directory_path = match.group("directory")
                parse_output(world.execute("gmail__send_email", {
                    "email_addresses": [match.group("recipient")],
                    "subject": match.group("subject"),
                    "body": "",
                    "attachment_file_paths": [
                        directory_path + "/" + match.group("first"),
                        directory_path + "/" + match.group("second"),
                    ],
                    "file_system_access_token": fs_token,
                    "access_token": gmail_token,
                })); calls += 1
                discoverability = {
                    "recipient_from_instruction": True,
                    "attachment_paths_from_instruction": True,
                    "private_fixture_ids_used": False,
                }
            else:
                match = re.search(
                    r"^Read note (?P<note>\S+)\. Use Inbox todo (?P<todo>\S+) as the file name "
                    r"and write the note content to (?P<directory>~/\S+)\.",
                    arm["task_instruction"],
                )
                if match is None:
                    raise RuntimeError("Public TNF oracle could not parse V2 task instruction.")
                fs_token = login(world, "file_system", username, passwords["file_system"]); calls += 1
                note_token = login(world, "simple_note", username, passwords["simple_note"]); calls += 1
                todo_token = login(world, "todoist", username, passwords["todoist"]); calls += 1

                note_search = parse_output(world.execute("simple_note__search_notes", {
                    "query": match.group("note"), "page_limit": 5, "access_token": note_token,
                })); calls += 1
                exact_notes = [row for row in note_search if row.get("title") == match.group("note")]
                if len(exact_notes) != 1:
                    raise RuntimeError("Exact public note title is not discoverable exactly once.")
                note = parse_output(world.execute("simple_note__show_note", {
                    "note_id": exact_notes[0]["note_id"], "access_token": note_token,
                })); calls += 1

                inbox = parse_output(world.execute("todoist__show_tasks", {
                    "project_id": 0, "access_token": todo_token,
                })); calls += 1
                exact_todos = [row for row in _todo_tasks(inbox) if row.get("title") == match.group("todo")]
                if len(exact_todos) != 1:
                    raise RuntimeError("Exact public Inbox todo title is not discoverable exactly once.")
                parse_output(world.execute("file_system__create_file", {
                    "file_path": match.group("directory").rstrip("/") + "/" + exact_todos[0]["title"] + ".txt",
                    "content": note["content"],
                    "access_token": fs_token,
                })); calls += 1
                discoverability = {
                    "note_id_source": "PUBLIC_SIMPLE_NOTE_EXACT_SEARCH_RESULT",
                    "todo_source": "PUBLIC_TODOIST_INBOX_PROJECT_ID_0",
                    "private_fixture_ids_used": False,
                    "exact_note_rank": note_search.index(exact_notes[0]) + 1,
                }
            evaluation = world.save_and_evaluate(arm)
        finally:
            world.close()
    return {
        "family_id": family_id,
        "category": family["category"],
        "tool_calls": calls,
        "tool_call_cap": 12,
        "within_cap": calls <= 12,
        "target_success": bool(evaluation["target_success"]),
        "non_target_preservation": float(evaluation["non_target_preservation"]),
        "discoverability": discoverability,
        "initial_snapshot_sha256": materialized["initial_snapshot_sha256"],
    }


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    r2 = read_json(R2_RESULT)
    substrate = read_json(SUBSTRATE_CONTRACT)
    if r2.get("status") != "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP":
        raise RuntimeError("Expected sealed Plus R2 floor artifact.")
    if substrate.get("status") != "CAPABILITY_SUBSTRATE_V2_STATIC_REPAIR_READY":
        raise RuntimeError("Capability substrate V2 contract is not ready.")
    oracles = [run_public_oracle("ACE-FG-05"), run_public_oracle("ACE-TNF-05")]
    if not all(
        row["within_cap"]
        and row["target_success"]
        and row["non_target_preservation"] == 1.0
        and row["discoverability"].get("private_fixture_ids_used") is False
        for row in oracles
    ):
        raise RuntimeError("Capability substrate V2 public oracle qualification failed.")

    void_payload: dict[str, Any] = {
        "schema_version": "ace-capability-substrate-invalid-void-r2-v1",
        "object_id": OBJECT_ID,
        "status": "QWEN37PLUS_R2_VOID_SUBSTRATE_DISCOVERABILITY_INVALID",
        "affected_result": {
            "path": str(R2_RESULT.relative_to(ROOT)),
            "sha256": sha256_file(R2_RESULT),
            "model": "qwen3.7-plus",
            "reported_target_success_rate": r2["gate"]["target_success_rate"],
            "reported_tool_loop_completion_rate": r2["gate"]["tool_loop_completion_rate"],
        },
        "objective_defects": [
            "RAW_SIMPLE_NOTE_FIXTURES_EXISTED_IN_NOTES_TABLE_BUT_WERE_ABSENT_FROM_NOTES_FTS",
            "EXACT_PUBLIC_SEARCH_FOR_TARGET_NOTE_RETURNED_UNRELATED_BASE_NOTES",
            "TNF_TASK_REFERENCED_TODO_TITLE_WITHOUT_AGENT_VISIBLE_PROJECT_LOCATOR_WHILE_TODOIST_HAS_NO_GLOBAL_TASK_SEARCH",
            "R1_REACHABILITY_ORACLE_USED_PROTECTED_NOTE_AND_TASK_IDS_AND_THEREFORE_DID_NOT_PROVE_AGENT_VISIBLE_REACHABILITY",
            "FILE_GMAIL_TARGET_BINDING_LOCATED_EMAIL_ROW_BUT_DID_NOT_ENFORCE_RECIPIENT_AND_ATTACHMENT_SEMANTICS",
        ],
        "scientific_interpretation": (
            "The R2 50% capability result is retained as execution evidence but is void for model selection. "
            "At least the TNF half was measured on a substrate where exact note discovery was broken and task location was underspecified."
        ),
        "f0_scientific_outcomes_observed": 0,
        "authority": {"f0": False, "p1": False, "toolsandbox": False, "paper_claim": False},
    }
    void_payload["content_sha256"] = sha256_value(void_payload)

    qual_payload: dict[str, Any] = {
        "schema_version": "ace-capability-substrate-recovery-qualification-r2-v1",
        "object_id": OBJECT_ID,
        "status": "CAPABILITY_SUBSTRATE_V2_PUBLIC_REACHABILITY_PASS",
        "active_protected_bundle": {
            "path": str(BUNDLE.relative_to(ROOT)),
            "sha256": sha256_file(BUNDLE),
        },
        "repair_contract_sha256": sha256_file(SUBSTRATE_CONTRACT),
        "public_oracle_results": oracles,
        "qualification_rules": {
            "no_private_fixture_ids_in_oracle": True,
            "exact_note_public_search_required": True,
            "todo_public_inbox_lookup_required": True,
            "full_semantic_file_gmail_target_evaluation_required": True,
            "oracle_tool_calls_must_be_lte_frozen_cap": 12,
        },
        "provider_requests": 0,
        "f0_scientific_outcomes_observed": 0,
    }
    qual_payload["content_sha256"] = sha256_value(qual_payload)

    r3_payload: dict[str, Any] = {
        "schema_version": "ace-qwen37plus-capability-r3-contract-v1",
        "object_id": OBJECT_ID,
        "execution_id": R3_EXECUTION_ID,
        "status": "QWEN37PLUS_CAPABILITY_R3_AUTHORIZED_AFTER_SUBSTRATE_V2",
        "model": "qwen3.7-plus",
        "reason_for_reexecution": "R2_VOID_DUE_OBJECTIVE_DISCOVERABILITY_AND_EVALUATOR_SUBSTRATE_DEFECTS",
        "active_protected_bundle_sha256": sha256_file(BUNDLE),
        "same_eight_unit_panel": True,
        "same_family_ids": ["ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06"],
        "same_repeats": [1, 2],
        "tool_call_cap": 12,
        "temperature": 0,
        "provider_max_retries": 0,
        "application_retry": False,
        "replacement": False,
        "model_switch": False,
        "threshold_change": False,
        "scientific_target_semantics_change": False,
        "topology_or_coupling_change": False,
        "task_surface_clarification": "TNF TODO LOCATION MADE EXPLICIT AS INBOX",
        "prior_r2_units_count_as_valid_model_selection_measurements": False,
        "void_artifact_sha256": sha256_value(void_payload),
        "qualification_artifact_sha256": sha256_value(qual_payload),
        "authority": {"capability_r3": True, "f0": False, "p1": False, "toolsandbox": False, "paper_claim": False},
    }
    r3_payload["content_sha256"] = sha256_value(r3_payload)
    return void_payload, qual_payload, r3_payload


def main() -> None:
    void_payload, qual_payload, r3_payload = build_artifacts()
    write_json(VOID_OUTPUT, void_payload)
    write_json(QUAL_OUTPUT, qual_payload)
    write_json(R3_CONTRACT_OUTPUT, r3_payload)
    print(json.dumps({
        "void_status": void_payload["status"],
        "qualification_status": qual_payload["status"],
        "r3_status": r3_payload["status"],
        "public_oracles": qual_payload["public_oracle_results"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
