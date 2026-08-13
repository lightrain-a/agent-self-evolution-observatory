from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings
from .paper_first_primary_evidence import load_private_primary_pool, private_primary_pool_path
from .paper_first_problem_discovery_contract import audit_problem_candidate
from .public_state_redaction import redact_private_paths

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-problem-gate-queue.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-problem-gate-queue.js"
INBOX_ENV = "PAPER_FIRST_PROBLEM_CANDIDATE_INBOX"
AUTO_INBOX_ENV = "PAPER_FIRST_PROBLEM_AUTO_CANDIDATE_INBOX"
PRIMARY_POOL_ENV = "PAPER_FIRST_PRIMARY_EVIDENCE_POOL"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _discovery_root(storage: StorageSettings | None = None) -> Path:
    storage = storage or StorageSettings.from_env()
    return storage.data_root / "paper-first-problem-discovery"


def default_inbox_path(storage: StorageSettings | None = None) -> Path:
    explicit = os.getenv(INBOX_ENV, "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    return _discovery_root(storage) / "candidate-inbox.json"


def default_auto_inbox_path(storage: StorageSettings | None = None) -> Path:
    explicit = os.getenv(AUTO_INBOX_ENV, "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    return _discovery_root(storage) / "auto-candidate-inbox.json"


def default_primary_pool_path(storage: StorageSettings | None = None) -> Path:
    explicit = os.getenv(PRIMARY_POOL_ENV, "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    return private_primary_pool_path(storage)


def load_candidate_inbox(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [], [f"inbox-unreadable:{path.name}:{type(error).__name__}"]
    if not isinstance(payload, dict):
        return [], [f"inbox-root-must-be-object:{path.name}"]
    rows = payload.get("candidates") or []
    if not isinstance(rows, list):
        return [], [f"inbox-candidates-must-be-array:{path.name}"]
    candidates: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"candidate-{index}-must-be-object:{path.name}")
            continue
        copied = dict(row)
        copied["_source_inbox"] = str(path)
        candidates.append(copied)
    return candidates, errors


def _primary_registry(path: Path) -> dict[str, dict[str, Any]]:
    pool = load_private_primary_pool(path)
    if not pool:
        return {}
    registry: dict[str, dict[str, Any]] = {}
    for row in pool.get("records") or []:
        if not isinstance(row, dict) or row.get("primary_source_verified") is not True:
            continue
        ref = str(row.get("ref") or "").strip()
        if ref:
            registry[ref] = row
    return registry


def _candidate_snapshot(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        key: candidate.get(key)
        for key in (
            "candidate_id",
            "title",
            "empirical_contradiction",
            "irreducible_object",
            "mature_theory_baselines",
            "same_information_nonreducibility",
            "exact_prediction",
            "strongest_same_information_baseline",
            "domain_transfer_audit",
            "saturation_scan",
            "semantic_reduction_review",
            "cheapest_problem_falsifier",
            "endpoint_headroom_requirement",
        )
    }


def build_problem_gate_queue(
    inbox_path: Path | None = None,
    *,
    auto_inbox_path: Path | None = None,
    primary_pool_path: Path | None = None,
    storage: StorageSettings | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    manual_source = inbox_path or default_inbox_path(storage)
    auto_source = auto_inbox_path or default_auto_inbox_path(storage)
    primary_source = primary_pool_path or default_primary_pool_path(storage)
    sources: list[Path] = []
    for source in (manual_source, auto_source):
        if source not in sources:
            sources.append(source)

    candidates: list[dict[str, Any]] = []
    inbox_errors: list[str] = []
    for source in sources:
        rows, errors = load_candidate_inbox(source)
        candidates.extend(rows)
        inbox_errors.extend(errors)
    registry = _primary_registry(primary_source)

    audited: list[dict[str, Any]] = []
    passed: list[dict[str, Any]] = []
    seen: set[str] = set()
    duplicate_ids: list[str] = []

    for index, candidate in enumerate(candidates):
        cid = str(candidate.get("candidate_id") or f"candidate-{index}")
        if cid in seen:
            duplicate_ids.append(cid)
        seen.add(cid)
        audit = audit_problem_candidate(
            candidate,
            primary_evidence_by_ref=registry,
            require_primary_registry=True,
        )
        snapshot = _candidate_snapshot(candidate)
        row = {
            "candidate_id": cid,
            "title": str(candidate.get("title") or ""),
            "source_inbox": str(candidate.get("_source_inbox") or ""),
            "candidate": snapshot,
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
                "source_inbox": row["source_inbox"],
                "candidate": snapshot,
            })

    if duplicate_ids:
        duplicates = set(duplicate_ids)
        inbox_errors.append("duplicate-candidate-ids:" + ",".join(sorted(duplicates)))
        passed = [row for row in passed if row["candidate_id"] not in duplicates]
        for row in audited:
            if row["candidate_id"] in duplicates:
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
            "source_inbox": row["source_inbox"],
            "blockers": list(row["audit"].get("blockers") or []),
        }
        for row in audited
        if row["candidate_id"] not in passed_ids
    ]

    return {
        "schema_version": "1.1",
        "generated_at": _now(),
        "source_inbox": str(manual_source),
        "source_inboxes": [str(path) for path in sources],
        "primary_evidence_pool": str(primary_source),
        "primary_evidence_records": len(registry),
        "source_exists": any(path.exists() for path in sources),
        "policy": {
            "candidate_inbox_is_not_authority": True,
            "manual_and_auto_inboxes_are_merged": True,
            "verified_primary_evidence_registry_required_for_submitted_candidates": True,
            "independent_semantic_reduction_review_required": True,
            "semantic_reviewer_is_block_only": True,
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
            "primary_evidence_records": len(registry),
            "method_authorized": 0,
            "experiment_authorized": 0,
            "p0_authorized": 0,
        },
        "inbox_errors": inbox_errors,
        "passed": passed,
        "blocked": blocked,
        "audited": audited,
        "next_action": "Human Paper Design review may inspect passed candidates. Blocked, stale, malformed, or missing candidates do not create a paper, method, experiment, or P0 lifecycle entry.",
    }


def write_problem_gate_queue(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
    *,
    inbox_path: Path | None = None,
    auto_inbox_path: Path | None = None,
    primary_pool_path: Path | None = None,
    storage: StorageSettings | None = None,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    state = build_problem_gate_queue(
        inbox_path,
        auto_inbox_path=auto_inbox_path,
        primary_pool_path=primary_pool_path,
        storage=storage,
    )
    public_state = redact_private_paths(state, storage=storage)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(public_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PROBLEM_GATE_QUEUE = " + json.dumps(public_state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_problem_gate_queue(), ensure_ascii=False))
