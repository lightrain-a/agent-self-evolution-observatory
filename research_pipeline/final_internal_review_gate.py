from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

CURRENT_JSON = PROJECT_ROOT / "generated" / "current-final-ideas.json"
R31_PANEL_JSON = PROJECT_ROOT / "generated" / "r31-panel-reviews.json"
R32_RECHECK_JSON = PROJECT_ROOT / "generated" / "r32-targeted-recheck.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "final-internal-review-gate.json"
REVIEWERS = ("glm-5.2", "deepseek-v4-pro")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verdict(value: Any) -> str:
    value = str(value or "pending").strip().lower()
    return value if value in {"pass", "revise", "block"} else "pending"


def build_final_internal_review_gate() -> dict[str, Any]:
    current = _load(CURRENT_JSON)
    r31 = _load(R31_PANEL_JSON)
    r32 = _load(R32_RECHECK_JSON)
    r31_reviews = r31.get("reviews") or {}
    r32_by_id = {row.get("idea_id"): row for row in r32.get("ideas", []) if row.get("idea_id")}

    rows: list[dict[str, Any]] = []
    for idea in current.get("ideas", []):
        idea_id = idea.get("idea_id")
        revision = idea.get("revision")
        if not idea_id or revision not in {"R3.1", "R3.2"}:
            raise ValueError(f"invalid current idea identity/revision: {idea_id!r} {revision!r}")
        if revision == "R3.2":
            source = (r32_by_id.get(idea_id) or {}).get("reviewers") or {}
            pair = {name: _verdict(source.get(name)) for name in REVIEWERS}
        else:
            source = r31_reviews.get(idea_id) or {}
            pair = {name: _verdict((source.get(name) or {}).get("verdict")) for name in REVIEWERS}
        rows.append({"idea_id": idea_id, "revision": revision, **pair})

    if len(rows) != 20 or len({row["idea_id"] for row in rows}) != 20:
        raise ValueError(f"expected 20 unique current ideas, got {len(rows)}")
    counts = {
        "unanimous_pass": sum(all(row[name] == "pass" for name in REVIEWERS) for row in rows),
        "block": sum(any(row[name] == "block" for name in REVIEWERS) for row in rows),
    }
    counts["revise"] = len(rows) - counts["unanimous_pass"] - counts["block"]
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "review_date": "2026-08-08",
        "review_models": list(REVIEWERS),
        "policy": {
            "absolute_bar": True,
            "unanimous_pass_required": True,
            "raw_reviewer_responses_backend_only": True,
            "r31_used_only_for_current_r31_versions": True,
            "r32_recheck_overrides_r31_for_current_r32_versions": True,
        },
        "summary": {"total": len(rows), **counts},
        "ideas": rows,
    }


def write_final_internal_review_gate(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_final_internal_review_gate()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_final_internal_review_gate(), ensure_ascii=False))
