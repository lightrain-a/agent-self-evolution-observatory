from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .final_advisor_audit import TARGET, build_final_advisor_audit
from .human_terminal_state import build_human_terminal_state

DEFAULT_JSON = PROJECT_ROOT / "generated" / "discussion-ready-ideas.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "discussion-ready-ideas.js"
CURRENT_IDEAS_JSON = PROJECT_ROOT / "generated" / "current-final-ideas.json"

SOURCES = (
    ("main-r2", PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json", "passed_ideas", "external_verdict", "pass"),
    ("v4-r2", PROJECT_ROOT / "generated" / "idea-discovery-v4.json", "review_ranked_finalists", "external_verdict", "pass"),
    ("v5-r2", PROJECT_ROOT / "generated" / "idea-discovery-v5.json", "finalists", "external_verdict", "pass"),
    ("v51-r2", PROJECT_ROOT / "generated" / "idea-discovery-v51.json", "children", "external_verdict", "pass"),
    ("v52-r2", PROJECT_ROOT / "generated" / "idea-discovery-v52.json", "children", "external_verdict", "pass"),
    ("v53-r2", PROJECT_ROOT / "generated" / "idea-discovery-v53.json", "children", "external_verdict", "pass"),
)


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _r2_provenance() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for source, path, key, verdict_key, wanted in SOURCES:
        payload = _load(path)
        candidates = payload.get(key) or ([] if key != "review_ranked_finalists" else payload.get("tournament_finalists", []))
        for row in candidates:
            idea_id = row.get("id")
            if not idea_id or row.get(verdict_key) != wanted or idea_id in result:
                continue
            result[idea_id] = {
                "source": source,
                "rank": row.get("external_rank") or row.get("rank"),
                "parent_ids": row.get("parent_ids") or ([row.get("parent_id")] if row.get("parent_id") else []),
            }
    return result


def build_discussion_portfolio() -> dict[str, Any]:
    current = _load(CURRENT_IDEAS_JSON)
    final = build_final_advisor_audit()
    gate = {row["idea_id"]: row for row in final["ideas"]}
    provenance = _r2_provenance()
    terminal = build_human_terminal_state()

    legacy_rows: list[dict[str, Any]] = []
    for idea in current.get("ideas", []):
        idea_id = idea.get("idea_id")
        audit = gate.get(idea_id) or {}
        if audit.get("verdict") != "pass":
            continue
        source = provenance.get(idea_id) or {}
        legacy_rows.append(
            {
                "source": source.get("source", "r32-final"),
                "id": idea_id,
                "title": idea.get("title") or {},
                "verdict": "pass",
                "revision": idea.get("revision") or audit.get("revision") or "R3.1",
                "rank": source.get("rank"),
                "parent_ids": source.get("parent_ids") or [],
                "reviewed": True,
                "final_verdict": "pass",
                "reviewers": audit.get("reviewers") or {},
                "collision_gate": audit.get("collision_gate", "pending"),
            }
        )

    rows: list[dict[str, Any]] = []
    for idea_id, meta in terminal["parents"].items():
        if meta.get("terminal_state") not in {"p0", "p0-ready"}:
            continue
        rows.append({"source":"human-terminal-parent","id":idea_id,"title":meta.get("final_parent_mechanism") or {},"terminal_state":meta.get("terminal_state"),"human_parent":True,"reviewed":True,"final_verdict":"terminal-human-decision","parent_ids":[]})
    for idea_id, meta in terminal["independent_methods"].items():
        if meta.get("terminal_state") not in {"p0", "p0-ready"}:
            continue
        rows.append({"source":"terminal-independent-method","id":idea_id,"title":meta.get("title") or {},"terminal_state":meta.get("terminal_state"),"human_parent":False,"reviewed":True,"final_verdict":"terminal-human-compatible","parent_ids":[]})
    rows.sort(key=lambda row: (0 if row.get("human_parent") else 1, str(row.get("id"))))
    ready = terminal["summary"].get("human_parents") == 26
    return {
        "schema_version": "2.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target": TARGET,
        "count": len(rows),
        "remaining": max(0, TARGET - len(rows)),
        "ready": ready,
        "final_summary": final["summary"],
        "legacy_r3_final_passes": legacy_rows,
        "policy": {
            "terminal_human_state_is_active_source_of_truth": True,
            "active_states": ["p0", "p0-ready"],
            "merge_and_drop_excluded": True,
            "absorbed_children_excluded_from_advisor_pool": True,
            "independent_terminal_methods_allowed": True,
            "readiness_is_terminalization_not_legacy_pass_count": True,
            "legacy_r3_rows_are_traceability_only": True,
            "legacy_r3_required_two_model_and_collision_gates": True,
            "no_portfolio_shortlist": True,
        },
        "ideas": rows,
    }


def write_discussion_portfolio(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
) -> dict[str, Any]:
    payload = build_discussion_portfolio()
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.DISCUSSION_READY_IDEAS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(write_discussion_portfolio(), ensure_ascii=False))
