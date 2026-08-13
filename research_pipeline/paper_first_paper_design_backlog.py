from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_problem_gate_queue import DEFAULT_JSON as QUEUE_JSON, load_problem_gate_queue_state

DEFAULT_JSON = PROJECT_ROOT / "generated" / "paper-first-paper-design-backlog.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "paper-first-paper-design-backlog.js"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _fingerprint(row: dict[str, Any]) -> str:
    candidate = row.get("candidate") or {}
    evidence = candidate.get("empirical_evidence") or {}
    refs = sorted(str((evidence.get(key) or {}).get("ref") or "") for key in ("source_a", "source_b"))
    material = {"candidate_id":str(row.get("candidate_id") or candidate.get("candidate_id") or ""),"title":str(row.get("title") or candidate.get("title") or ""),"lane":str(row.get("discovery_lane") or candidate.get("discovery_lane") or ""),"source_refs":refs}
    return hashlib.sha256(json.dumps(material,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:20]


def build_paper_design_backlog(queue: dict[str, Any] | None = None, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    queue = queue or load_problem_gate_queue_state()
    previous = previous or {}
    by_id: dict[str, dict[str, Any]] = {}
    for row in previous.get("entries") or []:
        if isinstance(row, dict) and str(row.get("backlog_id") or ""):
            by_id[str(row["backlog_id"])] = dict(row)
    for row in queue.get("passed") or []:
        if not isinstance(row, dict):
            continue
        candidate = row.get("candidate") or {}
        backlog_id = _fingerprint(row)
        by_id[backlog_id] = {
            "backlog_id": backlog_id,
            "candidate_id": str(row.get("candidate_id") or candidate.get("candidate_id") or ""),
            "title": str(row.get("title") or candidate.get("title") or ""),
            "discovery_lane": str(row.get("discovery_lane") or candidate.get("discovery_lane") or ""),
            "status": "AWAIT_HUMAN_PAPER_DESIGN_REVIEW",
            "paper_design_eligible": True,
            "problem_gate_status": str(row.get("status") or "PROBLEM_GATE_PASS"),
            "source_inbox": str(row.get("source_inbox") or ""),
            "source_transaction_id": str(queue.get("discovery_transaction_id") or ""),
            "candidate": candidate,
            "authority": {"paper_design_review": True, "method": False, "experiment": False, "p0": False, "gpu": False},
            "scientific_authority": False,
        }
    entries = sorted(by_id.values(), key=lambda row: (str(row.get("candidate_id") or ""), str(row.get("backlog_id") or "")))
    pending = [row for row in entries if row.get("status") == "AWAIT_HUMAN_PAPER_DESIGN_REVIEW"]
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "policy": {
            "problem_gate_pass_is_durable_until_human_paper_design_resolution": True,
            "volatile_discovery_queue_cannot_erase_backlog": True,
            "backlog_copies_only_problem_gate_passed_candidates": True,
            "paper_design_eligibility_is_not_method_authority": True,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
        },
        "summary": {"entries": len(entries), "pending_human_paper_design": len(pending), "method_authorized": 0, "experiment_authorized": 0, "p0_authorized": 0, "gpu_authorized": 0},
        "entries": entries,
        "scientific_authority": False,
    }


def load_paper_design_backlog(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = _load(path)
    if payload:
        return payload
    return {"schema_version":"1.0","status":"NOT_RUN","policy":{"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False,"automatic_gpu_authority":False},"summary":{"entries":0,"pending_human_paper_design":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0,"gpu_authorized":0},"entries":[],"scientific_authority":False}


def write_paper_design_backlog(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS, *, queue_path: Path = QUEUE_JSON) -> dict[str, Any]:
    previous = load_paper_design_backlog(json_path)
    queue = load_problem_gate_queue_state(queue_path)
    state = build_paper_design_backlog(queue, previous)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PAPER_DESIGN_BACKLOG = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_paper_design_backlog(), ensure_ascii=False, indent=2))
