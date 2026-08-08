from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

TARGET = 20
CURRENT_IDEAS_JSON = PROJECT_ROOT / "generated" / "current-final-ideas.json"
INTERNAL_REVIEW_JSON = PROJECT_ROOT / "generated" / "final-internal-review-gate.json"
COLLISION_JSON = PROJECT_ROOT / "generated" / "final-collision-recheck.json"
HISTORICAL_R3_JSON = PROJECT_ROOT / "generated" / "r3-final-audit.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "final-advisor-audit.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "final-advisor-audit.js"
REVIEWERS = ("glm-5.2", "deepseek-v4-pro")


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _normalize_verdict(value: Any) -> str:
    verdict = str(value or "pending").strip().lower()
    return verdict if verdict in {"pass", "revise", "block"} else "pending"


def _review_pair(idea_id: str, internal_by_id: dict[str, dict[str, Any]]) -> dict[str, str]:
    raw = internal_by_id.get(idea_id) or {}
    return {name: _normalize_verdict(raw.get(name)) for name in REVIEWERS}


def _aggregate(pair: dict[str, str], collision_status: str) -> str:
    values = list(pair.values())
    if collision_status == "block" or "block" in values:
        return "block"
    if collision_status != "pass" or any(value != "pass" for value in values):
        return "revise"
    return "pass"


def build_final_advisor_audit() -> dict[str, Any]:
    current = _load(CURRENT_IDEAS_JSON)
    internal = _load(INTERNAL_REVIEW_JSON)
    collisions = _load(COLLISION_JSON)
    historical_r3 = _load(HISTORICAL_R3_JSON)

    internal_by_id = {row.get("idea_id"): row for row in internal.get("ideas", []) if row.get("idea_id")}
    collision_by_id = {row.get("idea_id"): row for row in collisions.get("ideas", []) if row.get("idea_id")}
    historical_by_id = {row.get("idea_id"): row for row in historical_r3.get("ideas", []) if row.get("idea_id")}

    rows: list[dict[str, Any]] = []
    for idea in current.get("ideas", []):
        idea_id = idea.get("idea_id")
        if not idea_id:
            continue
        pair = _review_pair(idea_id, internal_by_id)
        collision = collision_by_id.get(idea_id) or {}
        collision_status = _normalize_verdict(collision.get("status"))
        verdict = _aggregate(pair, collision_status)
        rows.append(
            {
                "idea_id": idea_id,
                "revision": idea.get("revision") or "R3.1",
                "verdict": verdict,
                "reviewers": pair,
                "collision_gate": collision_status,
                "collision": {
                    "closest_work": collision.get("closest_work") or [],
                    "surviving_difference": collision.get("surviving_difference") or "",
                    "sources": collision.get("sources") or [],
                },
                "finding": (
                    f"{idea.get('revision') or 'R3.1'} page-facing version received unanimous PASS from GLM-5.2 and DeepSeek V4 Pro; "
                    "the current mechanism then survived the fresh 2026-08-08 primary-source collision recheck."
                    if verdict == "pass"
                    else "Final gate remains unresolved."
                ),
                "historical_r3_verdict": _normalize_verdict((historical_by_id.get(idea_id) or {}).get("verdict")),
            }
        )

    counts = {name: sum(row["verdict"] == name for row in rows) for name in ("pass", "revise", "block")}
    retired = [
        {
            "idea_id": idea_id,
            "reason": "Historical R3 BLOCK; retired from the advisor pool and not counted toward the final 20.",
        }
        for idea_id, row in historical_by_id.items()
        if _normalize_verdict(row.get("verdict")) == "block" and idea_id not in {x["idea_id"] for x in rows}
    ]
    ready = len(rows) == TARGET and counts["pass"] == TARGET and counts["revise"] == 0 and counts["block"] == 0
    return {
        "schema_version": "2.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "review_date": "2026-08-08",
        "scope": "Final pre-advisor gate after R3, R3.1/R3.2 repair, two-model independent recheck, and fresh primary-source collision search of every current idea.",
        "target": TARGET,
        "summary": {
            "total": len(rows),
            **counts,
            "ready": ready,
            "unanimous_internal_pass": sum(all(v == "pass" for v in row["reviewers"].values()) for row in rows),
            "fresh_collision_rechecks": sum(row["collision_gate"] == "pass" for row in rows),
            "targeted_r32_rechecks": sum(row.get("revision") == "R3.2" for row in rows),
        },
        "policy": {
            "no_shortlist_or_ranking": True,
            "r2_is_provenance_only": True,
            "historical_r3_is_diagnostic_only": True,
            "current_page_version_is_r31_or_r32": True,
            "two_independent_internal_reviewers_required": True,
            "review_models": list(REVIEWERS),
            "raw_reviewer_responses_backend_only": True,
            "fresh_primary_source_collision_gate_for_all_current_ideas": True,
            "titles_alone_do_not_establish_novelty": True,
        },
        "retired_from_advisor_pool": retired,
        "ideas": rows,
    }


def write_final_advisor_audit(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
) -> dict[str, Any]:
    payload = build_final_advisor_audit()
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.FINAL_ADVISOR_AUDIT = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(write_final_advisor_audit(), ensure_ascii=False))
