from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings, resolve_experiment_data_root
from .paper_first_problem_discovery_contract import audit_problem_candidate

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-gate-queue.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-problem-gate-queue.js"
INBOX_ENV = "PAPER_FIRST_PROBLEM_CANDIDATE_INBOX"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_inbox_path() -> Path:
    explicit = os.getenv(INBOX_ENV, "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    data_root = resolve_experiment_data_root(StorageSettings.from_env())
    return data_root / "paper-first-problem-discovery" / "candidate-inbox.json"


def load_candidate_inbox(path: Path | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    source = path or default_inbox_path()
    if not source.exists():
        return [], []
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [], [f"inbox-unreadable:{type(error).__name__}"]
    if not isinstance(payload, dict):
        return [], ["inbox-root-must-be-object"]
    rows = payload.get("candidates") or []
    if not isinstance(rows, list):
        return [], ["inbox-candidates-must-be-array"]
    candidates: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"candidate-{index}-must-be-object")
            continue
        candidates.append(row)
    return candidates, errors


def build_problem_gate_queue(inbox_path: Path | None = None) -> dict[str, Any]:
    source = inbox_path or default_inbox_path()
    candidates, inbox_errors = load_candidate_inbox(source)
    audited: list[dict[str, Any]] = []
    passed: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    seen: set[str] = set()
    duplicate_ids: list[str] = []

    for index, candidate in enumerate(candidates):
        cid = str(candidate.get("candidate_id") or f"candidate-{index}")
        if cid in seen:
            duplicate_ids.append(cid)
        seen.add(cid)
        audit = audit_problem_candidate(candidate)
        row = {
            "candidate_id": cid,
            "title": str(candidate.get("title") or ""),
            "audit": audit,
            "paper_design_eligible": bool(audit.get("passed")),
            "authority": {
                "method_design": False,
                "experiment_blueprint": False,
                "local_validation": False,
                "p0": False,
                "gpu": False,
                "full_experiment": False,
            },
        }
        audited.append(row)
        if audit.get("passed"):
            passed.append({
                "candidate_id": cid,
                "title": row["title"],
                "status": "AWAIT_HUMAN_PAPER_DESIGN_REVIEW",
                "paper_design_eligible": True,
                "source_inbox": str(source),
            })
        else:
            blocked.append({
                "candidate_id": cid,
                "title": row["title"],
                "status": "PROBLEM_GATE_BLOCKED",
                "blockers": list(audit.get("blockers") or []),
            })

    if duplicate_ids:
        inbox_errors.append("duplicate-candidate-ids:" + ",".join(sorted(set(duplicate_ids))))
        passed = [row for row in passed if row["candidate_id"] not in set(duplicate_ids)]
        for row in audited:
            if row["candidate_id"] in set(duplicate_ids):
                row["paper_design_eligible"] = False
                row["audit"]["passed"] = False
                row["audit"]["status"] = "PROBLEM_GATE_BLOCKED"
                row["audit"]["blockers"] = sorted(set(list(row["audit"].get("blockers") or []) + ["duplicate-candidate-id"]))

    passed_ids = {row["candidate_id"] for row in passed}
    blocked = [
        {
            "candidate_id": row["candidate_id"],
            "title": row["title"],
            "status": "PROBLEM_GATE_BLOCKED",
            "blockers": list(row["audit"].get("blockers") or []),
        }
        for row in audited
        if row["candidate_id"] not in passed_ids
    ]

    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "source_inbox": str(source),
        "source_exists": source.exists(),
        "policy": {
            "candidate_inbox_is_not_authority": True,
            "all_candidates_require_problem_gate": True,
            "problem_gate_pass_only_grants_human_paper_design_eligibility": True,
            "old_solution_first_discovery_is_archival_input_only": True,
            "zero_candidates_or_zero_passes_is_valid": True,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
        },
        "summary": {
            "submitted": len(candidates),
            "audited": len(audited),
            "passed_problem_gate": len(passed),
            "blocked_problem_gate": len(blocked),
            "paper_design_eligible": len(passed),
            "inbox_errors": len(inbox_errors),
            "method_authorized": 0,
            "experiment_authorized": 0,
            "p0_authorized": 0,
        },
        "inbox_errors": inbox_errors,
        "passed": passed,
        "blocked": blocked,
        "audited": audited,
        "next_action": "Human Paper Design review may inspect passed candidates. Blocked or missing candidates do not create a paper, method, experiment, or P0 lifecycle entry.",
    }


def write_problem_gate_queue(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
    *,
    inbox_path: Path | None = None,
) -> dict[str, Any]:
    state = build_problem_gate_queue(inbox_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PROBLEM_GATE_QUEUE = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_problem_gate_queue(), ensure_ascii=False))
