from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
R2_RUNTIME = ROOT / "runtimes/agent-constraint-externality-qwen37plus-capability-r2-20260901"
R2_RESULT = GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r2-20260901.json"
PUBLIC_QUAL = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r2-20260902.json"
OUTPUT = GENERATED / "agent-constraint-externality-capability-r2-root-cause-audit-20260902.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _api_sequence(unit_id: str) -> list[dict[str, str]]:
    unit_root = R2_RUNTIME / "worlds" / unit_id.replace(":", "_").replace("|", "_")
    paths = list(unit_root.glob("experiments/outputs/*/tasks/*/logs/api_calls.jsonl"))
    if len(paths) != 1:
        raise RuntimeError(f"Expected one API log for {unit_id}.")
    rows = [json.loads(line) for line in paths[0].read_text(encoding="utf-8").splitlines() if line.strip()]
    # Never persist request data because auth tokens/passwords may occur there.
    return [{"method": str(row.get("method")), "url": str(row.get("url"))} for row in rows]


def _tnf_input_audit(unit_id: str) -> dict[str, Any]:
    unit_root = R2_RUNTIME / "worlds" / unit_id.replace(":", "_").replace("|", "_")
    task_roots = list((unit_root / "data/tasks").iterdir())
    if len(task_roots) != 1:
        raise RuntimeError(f"Expected one task input root for {unit_id}.")
    db_root = task_roots[0] / "dbs"
    note_id = 930151 if "TNF-05" in unit_id else 930181
    todo_id = 930153 if "TNF-05" in unit_id else 930183
    note_db = sqlite3.connect(db_root / "simple_note.db")
    try:
        note_row = note_db.execute(
            "SELECT id, user_id, title FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        fts_row = note_db.execute(
            "SELECT id, saved_search_text FROM notes_fts WHERE id = ?", (note_id,)
        ).fetchone()
    finally:
        note_db.close()
    todo_db = sqlite3.connect(db_root / "todoist.db")
    try:
        todo_row = todo_db.execute(
            "SELECT id, user_id, project_id, title FROM tasks WHERE id = ?", (todo_id,)
        ).fetchone()
        project_row = todo_db.execute(
            "SELECT id, user_id, name, is_inbox FROM projects WHERE id = ?",
            (todo_row[2],),
        ).fetchone() if todo_row else None
    finally:
        todo_db.close()
    return {
        "target_note_row_present": note_row is not None,
        "target_note_title": note_row[2] if note_row else None,
        "target_note_fts_row_present": fts_row is not None,
        "target_todo_row_present": todo_row is not None,
        "target_todo_title": todo_row[3] if todo_row else None,
        "target_todo_project": {
            "project_id": project_row[0],
            "user_id": project_row[1],
            "name": project_row[2],
            "is_inbox": bool(project_row[3]),
        } if project_row else None,
    }


def build() -> dict[str, Any]:
    r2 = read_json(R2_RESULT)
    public_qual = read_json(PUBLIC_QUAL)
    ledger_rows = [
        json.loads(line)
        for line in (R2_RUNTIME / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    terminals = {
        row["unit_id"]: row
        for row in ledger_rows
        if row.get("event") in {"COMPLETION", "FAILURE"}
    }
    tnf_units = sorted(uid for uid in terminals if "ACE-TNF" in uid)
    fg_units = sorted(uid for uid in terminals if "ACE-FG" in uid)
    if len(tnf_units) != 4 or len(fg_units) != 4:
        raise RuntimeError("R2 audit expects four FG and four TNF terminal units.")

    tnf_evidence: list[dict[str, Any]] = []
    for uid in tnf_units:
        terminal = terminals[uid]
        seq = _api_sequence(uid)
        tnf_evidence.append({
            "unit_id": uid,
            "terminal_event": terminal["event"],
            "failure_message": terminal.get("message"),
            "api_call_count": len(seq),
            "api_sequence": seq,
            "attempted_exact_note_search": any(
                item["url"] == "/simple_note/notes" for item in seq
            ),
            "input_state": _tnf_input_audit(uid),
        })

    fg_evidence: list[dict[str, Any]] = []
    for uid in fg_units:
        terminal = terminals[uid]
        fg_evidence.append({
            "unit_id": uid,
            "terminal_event": terminal["event"],
            "tool_call_count": terminal.get("result", {}).get("tool_call_count"),
            "reported_target_success": terminal.get("result", {}).get("evaluation", {}).get("target_success"),
            "api_call_count": len(_api_sequence(uid)),
        })

    payload: dict[str, Any] = {
        "schema_version": "ace-capability-r2-root-cause-audit-v1",
        "object_id": OBJECT_ID,
        "status": "R2_50_PERCENT_NOT_VALID_MODEL_CAPABILITY_ESTIMATE",
        "r2_result": {
            "path": str(R2_RESULT.relative_to(ROOT)),
            "sha256": sha256_file(R2_RESULT),
            "reported_tool_loop_completion_rate": r2["gate"]["tool_loop_completion_rate"],
            "reported_target_success_rate": r2["gate"]["target_success_rate"],
        },
        "tnf_failure_evidence": tnf_evidence,
        "fg_evidence": fg_evidence,
        "root_causes": [
            {
                "id": "TNF_NOTE_FTS_MISSING",
                "classification": "OBJECTIVE_SUBSTRATE_DEFECT",
                "finding": "Target notes existed in notes table but lacked notes_fts entries, so public exact-title search could not rank/retrieve them as intended.",
            },
            {
                "id": "TNF_TODO_LOCATION_UNDERSPECIFIED",
                "classification": "OBJECTIVE_TASK_DISCOVERABILITY_DEFECT",
                "finding": "Target todos were in Aaron's Inbox, while the instruction named only the todo title and Todoist exposed no global task-search API.",
            },
            {
                "id": "R1_ORACLE_USED_PRIVATE_IDS",
                "classification": "QUALIFICATION_DEFECT",
                "finding": "The prior reachability oracle directly used protected note/task IDs and therefore did not establish agent-visible reachability under the 12-call cap.",
            },
            {
                "id": "FG_EVALUATOR_UNDERSPECIFIED",
                "classification": "MEASUREMENT_DEFECT",
                "finding": "The legacy File/Gmail target binding located an email by sender/subject but did not itself enforce recipient and attachment-name/content semantics.",
            },
        ],
        "public_v2_reachability": {
            "qualification_path": str(PUBLIC_QUAL.relative_to(ROOT)),
            "qualification_sha256": sha256_file(PUBLIC_QUAL),
            "oracle_results": public_qual["public_oracle_results"],
        },
        "scientific_adjudication": {
            "r2_model_selection_valid": False,
            "r2_50_percent_may_be_interpreted_as_plus_capability": False,
            "model_switch_justified_by_r2": False,
            "required_next_test": "REQUALIFY_SAME_QWEN37PLUS_ON_SUBSTRATE_V2",
            "f0_authorized": False,
        },
        "provider_requests_added_by_audit": 0,
        "sensitive_request_arguments_persisted": False,
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = build()
    write_json(OUTPUT, payload)
    print(json.dumps({
        "status": payload["status"],
        "tnf_units": len(payload["tnf_failure_evidence"]),
        "provider_requests_added_by_audit": 0,
        "content_sha256": payload["content_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
