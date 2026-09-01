from __future__ import annotations

import json
import tempfile
import warnings
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    SUPERVISOR_MAIN_USER_ID,
    prepare_appworld_runtime_root,
)
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-20260831.bundle"
FLASH_RESULT = GENERATED / "agent-constraint-externality-qwen-capability-continuation-r1-result-20260901.json"
PLUS_A1_RESULT = GENERATED / "agent-constraint-externality-qwen37plus-capability-result-a1-20260901.json"
VOID_OUTPUT = GENERATED / "agent-constraint-externality-capability-substrate-invalid-void-r1-20260901.json"
QUAL_OUTPUT = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r1-20260901.json"
R2_CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-qwen37plus-capability-r2-contract-20260901.json"
R2_EXECUTION_ID = "QWEN37PLUS-CAPABILITY-R2-AUTH-SUBSTRATE-RECOVERY"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_output(output: Any) -> Any:
    text = str(output).strip()
    if text.startswith("Execution failed"):
        raise RuntimeError(text)
    return json.loads(text)


def login(world: AppWorldToolWorld, app: str, password: str) -> str:
    result = parse_output(
        world.execute(app + "__login", {"username": "aa_burt@gmail.com", "password": password})
    )
    return str(result["access_token"])


def run_oracle(family_id: str) -> dict[str, Any]:
    spec = load_protected_spec(BUNDLE)
    family = next(item for item in spec["families"] if item["family_id"] == family_id)
    arm = next(item for item in family["arms"] if item["coupling_level"] == "LOW")
    with tempfile.TemporaryDirectory() as directory, warnings.catch_warnings():
        warnings.simplefilter("ignore")
        runtime = Path(directory)
        task_id = "aceoracle" + family_id.lower().replace("-", "") + "_1"
        materialized = prepare_appworld_runtime_root(
            APPWORLD_ROOT, runtime, family=family, arm=arm, task_id=task_id
        )
        world = AppWorldToolWorld(
            runtime_root=runtime,
            task_id=task_id,
            experiment_name="ace-capability-substrate-oracle-r1",
            seed=1,
            allowed_apps=set(family["fixture"]["apps"]),
        )
        calls = 0
        try:
            password_rows = parse_output(world.execute("supervisor__show_account_passwords", {}))
            calls += 1
            passwords = {row["account_name"]: row["password"] for row in password_rows}
            profile = parse_output(world.execute("supervisor__show_profile", {}))
            calls += 1
            active_task = parse_output(world.execute("supervisor__show_active_task", {}))
            calls += 1
            if profile["email"] != "aa_burt@gmail.com" or active_task["instruction"] != arm["task_instruction"]:
                raise RuntimeError("Supervisor identity/active-task oracle binding mismatch.")
            if family_id.startswith("ACE-FG"):
                fs_token = login(world, "file_system", passwords["file_system"]); calls += 1
                gmail_token = login(world, "gmail", passwords["gmail"]); calls += 1
                suffix = family_id[-2:]
                parse_output(world.execute("gmail__send_email", {
                    "email_addresses": ["stmcco@gmail.com"],
                    "subject": f"ACE-FG-{suffix}-delivery",
                    "body": "",
                    "attachment_file_paths": [
                        f"/home/aaron/agent_externality/ace-fg-{suffix}/source-a.txt",
                        f"/home/aaron/agent_externality/ace-fg-{suffix}/source-b.txt",
                    ],
                    "file_system_access_token": fs_token,
                    "access_token": gmail_token,
                })); calls += 1
            else:
                fs_token = login(world, "file_system", passwords["file_system"]); calls += 1
                note_token = login(world, "simple_note", passwords["simple_note"]); calls += 1
                todo_token = login(world, "todoist", passwords["todoist"]); calls += 1
                note_row = next(
                    row for row in family["fixture"]["rows"]
                    if row["app"] == "simple_note" and row["values"]["title"].startswith("source-note")
                )
                todo_row = next(
                    row for row in family["fixture"]["rows"]
                    if row["app"] == "todoist" and row["values"]["title"].startswith("source-report")
                )
                note = parse_output(world.execute("simple_note__show_note", {
                    "note_id": note_row["values"]["id"], "access_token": note_token,
                })); calls += 1
                task = parse_output(world.execute("todoist__show_task", {
                    "task_id": todo_row["values"]["id"], "access_token": todo_token,
                })); calls += 1
                parse_output(world.execute("file_system__create_file", {
                    "file_path": f"~/agent_externality/ace-tnf-{family_id[-2:]}/{task['title']}.txt",
                    "content": note["content"], "access_token": fs_token,
                })); calls += 1
            evaluation = world.save_and_evaluate(arm)
        finally:
            world.close()
    return {
        "family_id": family_id,
        "tool_calls": calls,
        "tool_call_cap": 12,
        "within_cap": calls <= 12,
        "target_success": bool(evaluation["target_success"]),
        "non_target_preservation": float(evaluation["non_target_preservation"]),
        "initial_snapshot_sha256": materialized["initial_snapshot_sha256"],
    }


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    flash = read_json(FLASH_RESULT)
    plus = read_json(PLUS_A1_RESULT)
    if flash["status"] != "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP":
        raise RuntimeError("Expected sealed Flash floor artifact.")
    if plus["status"] != "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP":
        raise RuntimeError("Expected sealed Plus A1 floor artifact.")
    oracles = [run_oracle("ACE-FG-05"), run_oracle("ACE-TNF-05")]
    if not all(row["within_cap"] and row["target_success"] and row["non_target_preservation"] == 1.0 for row in oracles):
        raise RuntimeError("Repaired substrate oracle qualification failed.")

    void_payload: dict[str, Any] = {
        "schema_version": "ace-capability-substrate-invalid-void-r1-v1",
        "object_id": OBJECT_ID,
        "status": "CAPABILITY_RESULTS_VOID_SUBSTRATE_INVALID",
        "classification": "CAPABILITY_SUBSTRATE_AUTH_AND_API_SCHEMA_INVALID",
        "affected_results": [
            {"path": str(FLASH_RESULT.relative_to(ROOT)), "sha256": sha256_file(FLASH_RESULT), "model": "qwen3.7-flash"},
            {"path": str(PLUS_A1_RESULT.relative_to(ROOT)), "sha256": sha256_file(PLUS_A1_RESULT), "model": "qwen3.7-plus"},
        ],
        "defects": [
            "CUSTOM_TASK_COPIED_BASE_SUPERVISOR_DB_WITHOUT_ACTIVE_SUPERVISOR_OR_ACCOUNT_PASSWORD_CONTEXT",
            "CUSTOM_TASK_SPECS_SUPERVISOR_DID_NOT_MATCH_FIXTURE_OWNER_USER_99",
            "RAW_FILE_FIXTURES_OMITTED_NATIVE_COMPRESSED_DATA_AND_API_VISIBLE_TIMESTAMPS",
            "RAW_NOTE_AND_TODO_FIXTURES_OMITTED_SQLMODEL_DEFAULT_FIELDS_REQUIRED_BY_TOOL_API_RESPONSES",
        ],
        "pre_repair_observation": {
            "supervisor_show_profile": "NO_SUPERVISOR_FOUND",
            "supervisor_account_passwords": "EMPTY",
            "fixture_owner_user_id": SUPERVISOR_MAIN_USER_ID,
        },
        "scientific_interpretation": (
            "The prior floor verdicts are retained as execution evidence but are void for model-capability selection, "
            "because the intended tasks were not executable through valid AppWorld authentication/API state."
        ),
        "f0_scientific_outcomes_observed": 0,
        "authority": {"f0": False, "p1": False, "toolsandbox": False, "paper_claim": False},
    }
    void_payload["content_sha256"] = sha256_value(void_payload)

    qual_payload: dict[str, Any] = {
        "schema_version": "ace-capability-substrate-recovery-qualification-r1-v1",
        "object_id": OBJECT_ID,
        "status": "CAPABILITY_SUBSTRATE_RECOVERY_QUALIFICATION_PASS",
        "supervisor_identity": {"main_user_id": 99, "email": "aa_burt@gmail.com"},
        "repair_invariants": {
            "family_panel_changed": False,
            "task_instruction_changed": False,
            "capability_thresholds_changed": False,
            "tool_call_cap_changed": False,
            "model_prompt_changed": False,
        },
        "oracle_results": oracles,
        "source_files": {
            "runtime": {"path": "research_pipeline/agent_constraint_externality_appworld_runtime.py", "sha256": sha256_file(ROOT / "research_pipeline/agent_constraint_externality_appworld_runtime.py")},
            "compiler": {"path": "research_pipeline/appworld_constraint_compiler.py", "sha256": sha256_file(ROOT / "research_pipeline/appworld_constraint_compiler.py")},
        },
        "provider_requests": 0,
        "f0_scientific_outcomes_observed": 0,
    }
    qual_payload["content_sha256"] = sha256_value(qual_payload)

    r2_payload: dict[str, Any] = {
        "schema_version": "ace-qwen37plus-capability-r2-contract-v1",
        "object_id": OBJECT_ID,
        "execution_id": R2_EXECUTION_ID,
        "status": "QWEN37PLUS_CAPABILITY_R2_AUTHORIZED_AFTER_SUBSTRATE_VOID",
        "model": "qwen3.7-plus",
        "reason_for_reexecution": "PRIOR_A1_MEASUREMENTS_VOID_DUE_OBJECTIVE_SUBSTRATE_INVALIDITY",
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
        "task_change": False,
        "void_artifact_sha256": sha256_value(void_payload),
        "qualification_artifact_sha256": sha256_value(qual_payload),
        "prior_a1_units_count_as_scientific_measurements": False,
        "authority": {"capability_r2": True, "f0": False, "p1": False, "toolsandbox": False, "paper_claim": False},
    }
    r2_payload["content_sha256"] = sha256_value(r2_payload)
    return void_payload, qual_payload, r2_payload


def main() -> None:
    void_payload, qual_payload, r2_payload = build_artifacts()
    write_json(VOID_OUTPUT, void_payload)
    write_json(QUAL_OUTPUT, qual_payload)
    write_json(R2_CONTRACT_OUTPUT, r2_payload)
    print(json.dumps({
        "void_status": void_payload["status"],
        "qualification_status": qual_payload["status"],
        "r2_status": r2_payload["status"],
        "oracles": qual_payload["oracle_results"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
