from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .final_advisor_audit import TARGET, build_final_advisor_audit

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

    rows: list[dict[str, Any]] = []
    for idea in current.get("ideas", []):
        idea_id = idea.get("idea_id")
        audit = gate.get(idea_id) or {}
        if audit.get("verdict") != "pass":
            continue
        source = provenance.get(idea_id) or {}
        rows.append(
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

    ready = len(rows) == TARGET and final["summary"].get("ready") is True
    return {
        "schema_version": "2.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target": TARGET,
        "count": len(rows),
        "remaining": max(0, TARGET - len(rows)),
        "ready": ready,
        "final_summary": final["summary"],
        "policy": {
            "strict_final_pass_only": True,
            "r2_is_provenance_only": True,
            "historical_r3_not_counted_as_current_verdict": True,
            "two_model_unanimous_pass_required": True,
            "fresh_primary_source_collision_gate_required": True,
            "supplementary_machine_school_not_counted": True,
            "revise_not_counted": True,
            "block_not_counted": True,
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
