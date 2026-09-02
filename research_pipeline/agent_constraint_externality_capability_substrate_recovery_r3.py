from __future__ import annotations

import json
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
BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v3-20260902.bundle"
V3_CONTRACT = GENERATED / "agent-constraint-externality-capability-substrate-v3-contract-20260902.json"
QUAL_OUTPUT = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r3-20260902.json"
R3_PARTIAL_RUNTIME = ROOT / "runtimes/agent-constraint-externality-qwen37plus-capability-r3-partial-20260902"
R3_PARTIAL_LEDGER = R3_PARTIAL_RUNTIME / "ledger.jsonl"
R3_PARTIAL_VOID = GENERATED / "agent-constraint-externality-capability-r3-partial-void-r1-20260902.json"
FG_REVALIDATION = GENERATED / "agent-constraint-externality-qwen37plus-r2-fg-v2-revalidation-20260902.json"
R4_CONTRACT = GENERATED / "agent-constraint-externality-qwen37plus-capability-r4-partial-contract-20260902.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse(output: Any) -> Any:
    text = str(output).strip()
    if text.startswith("Execution failed"):
        raise RuntimeError(text)
    return json.loads(text)


def login(world: AppWorldToolWorld, app: str, password: str) -> str:
    return str(parse(world.execute(app + "__login", {"username": "aa_burt@gmail.com", "password": password}))["access_token"])


def public_tnf_oracle(family_id: str) -> dict[str, Any]:
    spec = load_protected_spec(BUNDLE)
    family = next(row for row in spec["families"] if row["family_id"] == family_id)
    arm = next(row for row in family["arms"] if row["coupling_level"] == "LOW")
    suffix = family_id[-2:]
    note_title = f"source-note-{suffix}"
    todo_title = f"source-report-{suffix}"
    parent = "~/agent_externality/"
    target_dir = f"~/agent_externality/{family_id.lower()}/"
    expected_file = f"{target_dir}{todo_title}.txt"
    if f"{todo_title}.txt" not in arm["task_instruction"] or target_dir not in arm["task_instruction"]:
        raise RuntimeError("V3 task does not explicitly expose the required .txt filename and target directory.")
    with tempfile.TemporaryDirectory(prefix="ace-v3-public-oracle-") as directory, warnings.catch_warnings():
        warnings.simplefilter("ignore")
        runtime = Path(directory)
        task_id = "acev3oracle" + family_id.lower().replace("-", "") + "_1"
        materialized = prepare_appworld_runtime_root(APPWORLD_ROOT, runtime, family=family, arm=arm, task_id=task_id)
        world = AppWorldToolWorld(runtime_root=runtime, task_id=task_id, experiment_name="ace-capability-substrate-v3-public-oracle", seed=1, allowed_apps=set(family["fixture"]["apps"]))
        calls = 0
        try:
            profile = parse(world.execute("supervisor__show_profile", {})); calls += 1
            passwords_list = parse(world.execute("supervisor__show_account_passwords", {})); calls += 1
            active = parse(world.execute("supervisor__show_active_task", {})); calls += 1
            passwords = {row["account_name"]: row["password"] for row in passwords_list}
            if profile["email"] != "aa_burt@gmail.com" or active["instruction"] != arm["task_instruction"]:
                raise RuntimeError("V3 supervisor/task binding failed.")
            fs = login(world, "file_system", passwords["file_system"]); calls += 1
            note = login(world, "simple_note", passwords["simple_note"]); calls += 1
            todo = login(world, "todoist", passwords["todoist"]); calls += 1
            notes = parse(world.execute("simple_note__search_notes", {"query": note_title, "page_limit": 20, "access_token": note})); calls += 1
            exact_notes = [row for row in notes if row.get("title") == note_title]
            if len(exact_notes) != 1:
                raise RuntimeError("V3 exact note is not uniquely publicly discoverable.")
            note_detail = parse(world.execute("simple_note__show_note", {"note_id": exact_notes[0]["note_id"], "access_token": note})); calls += 1
            inbox = parse(world.execute("todoist__show_tasks", {"project_id": 0, "access_token": todo})); calls += 1
            tasks = list(inbox.get("no_section_tasks", []))
            for section in inbox.get("sections", []):
                tasks.extend(section.get("tasks", []))
            exact_tasks = [row for row in tasks if row.get("title") == todo_title]
            if len(exact_tasks) != 1:
                raise RuntimeError("V3 Inbox todo is not uniquely publicly discoverable.")
            parent_exists = parse(world.execute("file_system__directory_exists", {"directory_path": parent, "access_token": fs})); calls += 1
            target_exists = parse(world.execute("file_system__directory_exists", {"directory_path": target_dir, "access_token": fs})); calls += 1
            if not parent_exists.get("exists") or not target_exists.get("exists"):
                raise RuntimeError("V3 filesystem hierarchy is not publicly visible.")
            parse(world.execute("file_system__create_file", {"file_path": expected_file, "content": note_detail["content"], "access_token": fs})); calls += 1
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
        "parent_directory_publicly_exists": True,
        "target_directory_publicly_exists": True,
        "exact_note_publicly_discovered": True,
        "inbox_todo_publicly_discovered": True,
        "txt_target_explicit_in_instruction": True,
        "private_fixture_ids_used": False,
        "initial_snapshot_sha256": materialized["initial_snapshot_sha256"],
    }


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    v3 = read_json(V3_CONTRACT)
    if v3.get("status") != "CAPABILITY_SUBSTRATE_V3_STATIC_REPAIR_READY":
        raise RuntimeError("V3 static contract is not ready.")
    oracles = [public_tnf_oracle("ACE-TNF-05"), public_tnf_oracle("ACE-TNF-06")]
    if not all(row["within_cap"] and row["target_success"] and row["non_target_preservation"] == 1.0 for row in oracles):
        raise RuntimeError("V3 public oracle qualification failed.")
    qualification: dict[str, Any] = {
        "schema_version": "ace-capability-substrate-recovery-qualification-r3-v1",
        "object_id": OBJECT_ID,
        "status": "CAPABILITY_SUBSTRATE_V3_PUBLIC_REACHABILITY_PASS",
        "active_bundle": {"path": str(BUNDLE.relative_to(ROOT)), "sha256": sha256_file(BUNDLE)},
        "public_oracle_results": oracles,
        "rules": {
            "no_private_fixture_ids": True,
            "directory_parent_and_target_must_exist_via_public_api": True,
            "txt_filename_must_be_agent_visible": True,
            "exact_note_and_inbox_todo_publicly_discoverable": True,
            "oracle_tool_calls_lte_12": True,
        },
        "provider_requests": 0,
        "f0_scientific_outcomes_observed": 0,
    }
    qualification["content_sha256"] = sha256_value(qualification)

    ledger_rows = [json.loads(line) for line in R3_PARTIAL_LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    failures = [row for row in ledger_rows if row.get("event") == "FAILURE"]
    if len(failures) != 4:
        raise RuntimeError("Expected four terminal R3-partial TNF failures for void audit.")
    provider_requests = sum(len(row.get("provider_receipts", [])) for row in failures)
    void_payload: dict[str, Any] = {
        "schema_version": "ace-capability-r3-partial-void-r1-v1",
        "object_id": OBJECT_ID,
        "status": "QWEN37PLUS_R3_PARTIAL_VOID_SUBSTRATE_FILESYSTEM_FILENAME_INVALID",
        "affected_scope": "TNF_RERUN_UNITS_ONLY",
        "affected_units": [row["unit_id"] for row in failures],
        "objective_defects": [
            "FILE_SYSTEM_DIRECTORY_FIXTURE_PATHS_OMITTED_APPWORLD_REQUIRED_TRAILING_SLASH",
            "SYNTHETIC_CHILD_DIRECTORY_EXISTED_WITHOUT_AGENT_EXTERNALITY_PARENT_DIRECTORY",
            "TNF_TASK_REQUIRED_DOT_TXT_IN_EVALUATOR_BUT_DID_NOT_EXPLICITLY_STATE_EXTENSION",
        ],
        "observed_witnesses": {
            "directory_exists_returned_false_for_sqlite_present_directory": True,
            "create_file_without_extension_returned_http_422": True,
        },
        "fg_preserved_measurements_remain_valid": True,
        "fg_revalidation_sha256": sha256_file(FG_REVALIDATION),
        "provider_requests_spent_in_void_tnf_attempt": provider_requests,
        "retry_or_replacement": False,
        "f0_authorized": False,
    }
    void_payload["content_sha256"] = sha256_value(void_payload)

    r4: dict[str, Any] = {
        "schema_version": "ace-qwen37plus-capability-r4-partial-contract-v1",
        "object_id": OBJECT_ID,
        "execution_id": "QWEN37PLUS-CAPABILITY-R4-PARTIAL-SUBSTRATE-V3",
        "status": "QWEN37PLUS_CAPABILITY_R4_PARTIAL_TNF_ONLY_AUTHORIZED",
        "model": "qwen3.7-plus",
        "preserve_fg_measurements": 4,
        "rerun_tnf_measurements": 4,
        "rerun_family_ids": ["ACE-TNF-05", "ACE-TNF-06"],
        "same_repeats": [1, 2],
        "active_bundle_sha256": sha256_file(BUNDLE),
        "qualification_sha256": sha256_value(qualification),
        "void_sha256": sha256_value(void_payload),
        "tool_call_cap": 12,
        "temperature": 0,
        "provider_max_retries": 0,
        "application_retry": False,
        "replacement": False,
        "model_switch": False,
        "threshold_change": False,
        "fg_provider_reexecution": False,
        "f0_authorized": False,
    }
    r4["content_sha256"] = sha256_value(r4)
    return qualification, void_payload, r4


def main() -> None:
    qualification, void_payload, r4 = build()
    write_json(QUAL_OUTPUT, qualification)
    write_json(R3_PARTIAL_VOID, void_payload)
    write_json(R4_CONTRACT, r4)
    print(json.dumps({"qualification": qualification["status"], "void": void_payload["status"], "r4": r4["status"], "oracles": qualification["public_oracle_results"]}, sort_keys=True))


if __name__ == "__main__":
    main()
