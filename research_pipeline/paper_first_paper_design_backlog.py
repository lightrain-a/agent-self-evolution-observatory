from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .paper_first_problem_gate_queue import DEFAULT_JSON as QUEUE_JSON, load_problem_gate_queue_state
from .research_memory_wiki import compile_research_memory_query_pack, load_research_memory_wiki

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


def _paper_design_memory_precheck(row: dict[str, Any], research_memory: dict[str, Any]) -> dict[str, Any]:
    candidate = row.get("candidate") or {}
    context = {
        "candidate_id": str(row.get("candidate_id") or candidate.get("candidate_id") or ""),
        "title": str(row.get("title") or candidate.get("title") or ""),
        "discovery_lane": str(row.get("discovery_lane") or candidate.get("discovery_lane") or ""),
        "paper_problem": candidate.get("paper_problem") or candidate.get("problem") or candidate.get("scientific_object") or "",
        "novelty_boundary": candidate.get("novelty_boundary") or candidate.get("strongest_reduction") or "",
        "strongest_baseline": candidate.get("strongest_same_information_baseline") or candidate.get("strongest_baseline") or "",
    }
    pack = compile_research_memory_query_pack(research_memory, purpose="PAPER_DESIGN", context=context, max_chars=4800, max_items=16)
    selected = list(pack.get("selected") or [])
    return {
        "purpose": "PAPER_DESIGN",
        "wiki_sha256": str(pack.get("wiki_sha256") or ""),
        "query_pack_sha256": str(pack.get("query_pack_sha256") or ""),
        "selected_memory_ids": list(pack.get("selected_memory_ids") or []),
        "selected": int((pack.get("summary") or {}).get("selected") or 0),
        "review_lessons_selected": sum(str(item.get("kind") or "") == "REVIEW_LESSON" for item in selected if isinstance(item, dict)),
        "memory_is_context_not_scientific_verdict": True,
        "paper_review_patterns_are_prechecks_not_verdicts": True,
        "scientific_authority": False,
        "method_authority": False,
        "experiment_authority": False,
        "p0_authority": False,
        "gpu_authority": False,
    }


def _fingerprint(row: dict[str, Any]) -> str:
    candidate = row.get("candidate") or {}
    evidence = candidate.get("empirical_evidence") or {}
    refs = sorted(str((evidence.get(key) or {}).get("ref") or "") for key in ("source_a", "source_b"))
    material = {"candidate_id":str(row.get("candidate_id") or candidate.get("candidate_id") or ""),"title":str(row.get("title") or candidate.get("title") or ""),"lane":str(row.get("discovery_lane") or candidate.get("discovery_lane") or ""),"source_refs":refs}
    return hashlib.sha256(json.dumps(material,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:20]


def build_paper_design_backlog(queue: dict[str, Any] | None = None, previous: dict[str, Any] | None = None, research_memory: dict[str, Any] | None = None) -> dict[str, Any]:
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
    if by_id:
        research_memory = research_memory or load_research_memory_wiki()
        for entry in by_id.values():
            entry["paper_design_memory_precheck"] = _paper_design_memory_precheck(entry, research_memory)
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
            "paper_design_memory_precheck_required_for_pending_entries": True,
            "paper_design_memory_precheck_is_zero_authority": True,
            "paper_review_memory_is_context_not_scientific_evidence": True,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
        },
        "summary": {"entries": len(entries), "pending_human_paper_design": len(pending), "memory_prechecks": sum(bool(row.get("paper_design_memory_precheck")) for row in entries), "review_lessons_selected": sum(int((row.get("paper_design_memory_precheck") or {}).get("review_lessons_selected") or 0) for row in entries), "method_authorized": 0, "experiment_authorized": 0, "p0_authorized": 0, "gpu_authorized": 0},
        "entries": entries,
        "scientific_authority": False,
    }


def validate_paper_design_backlog(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = state.get("policy") or {}
    summary = state.get("summary") or {}
    entries = [row for row in state.get("entries") or [] if isinstance(row, dict)]
    pending = [row for row in entries if row.get("status") == "AWAIT_HUMAN_PAPER_DESIGN_REVIEW"]
    if len({str(row.get("backlog_id") or "") for row in entries}) != len(entries):
        errors.append("paper-design backlog IDs must be unique")
    if policy.get("paper_design_memory_precheck_required_for_pending_entries") is not True or policy.get("paper_design_memory_precheck_is_zero_authority") is not True or policy.get("paper_review_memory_is_context_not_scientific_evidence") is not True:
        errors.append("paper-design backlog must require zero-authority Research Memory prechecks")
    if any(policy.get(key) is not False for key in ("automatic_method_authority", "automatic_experiment_authority", "automatic_p0_authority", "automatic_gpu_authority")):
        errors.append("paper-design backlog cannot grant downstream authority")
    if int(summary.get("entries") or 0) != len(entries) or int(summary.get("pending_human_paper_design") or 0) != len(pending):
        errors.append("paper-design backlog summary accounting mismatch")
    if int(summary.get("memory_prechecks") or 0) != sum(bool(row.get("paper_design_memory_precheck")) for row in entries):
        errors.append("paper-design memory-precheck accounting mismatch")
    for row in pending:
        precheck = row.get("paper_design_memory_precheck") or {}
        if precheck.get("purpose") != "PAPER_DESIGN" or precheck.get("scientific_authority") is not False or not re.fullmatch(r"[0-9a-f]{64}", str(precheck.get("query_pack_sha256") or "")):
            errors.append(f"pending paper-design entry lacks a valid memory precheck:{row.get('candidate_id')}")
        if any(bool((row.get("authority") or {}).get(key)) for key in ("method", "experiment", "p0", "gpu")):
            errors.append(f"pending paper-design entry leaks downstream authority:{row.get('candidate_id')}")
    return sorted(set(errors))


def load_paper_design_backlog(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = _load(path)
    if payload:
        return payload
    return {"schema_version":"1.0","status":"NOT_RUN","policy":{"paper_design_memory_precheck_required_for_pending_entries":True,"paper_design_memory_precheck_is_zero_authority":True,"paper_review_memory_is_context_not_scientific_evidence":True,"automatic_method_authority":False,"automatic_experiment_authority":False,"automatic_p0_authority":False,"automatic_gpu_authority":False},"summary":{"entries":0,"pending_human_paper_design":0,"memory_prechecks":0,"review_lessons_selected":0,"method_authorized":0,"experiment_authorized":0,"p0_authorized":0,"gpu_authorized":0},"entries":[],"scientific_authority":False}


def write_paper_design_backlog(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS, *, queue_path: Path = QUEUE_JSON) -> dict[str, Any]:
    previous = load_paper_design_backlog(json_path)
    queue = load_problem_gate_queue_state(queue_path)
    state = build_paper_design_backlog(queue, previous)
    errors = validate_paper_design_backlog(state)
    if errors:
        raise ValueError("Invalid Paper Design backlog:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.PAPER_FIRST_PAPER_DESIGN_BACKLOG = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_paper_design_backlog(), ensure_ascii=False, indent=2))
