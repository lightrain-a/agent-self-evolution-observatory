from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "r3-final-audit.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "r3-final-audit.js"
SOURCE_PARTS = (
    PROJECT_ROOT / "research_pipeline" / "r3_final_audit_part1.json",
    PROJECT_ROOT / "research_pipeline" / "r3_final_audit_part2.json",
)
REVIEWER = "agent-project-web-gpt-r3-final-consistency-area-chair"
REVIEW_DATE = "2026-08-08"
VALID_VERDICTS = {"pass", "revise", "block"}


def _source_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in SOURCE_PARTS:
        rows.extend(json.loads(path.read_text(encoding="utf-8")))
    return rows


def build_r3_final_audit() -> dict[str, Any]:
    ideas = _source_rows()
    counts = {key: sum(row.get("verdict") == key for row in ideas) for key in VALID_VERDICTS}
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "reviewer": REVIEWER,
        "review_date": REVIEW_DATE,
        "scope": "final pre-advisor consistency audit of the 22 independently R2-PASS page-facing ICLR ideas",
        "policy": {
            "r2_is_provenance_not_presumption": True,
            "absolute_bar": True,
            "no_ranking": True,
            "official_primary_sources_only": True,
            "collision_search_cutoff": REVIEW_DATE,
            "pass_requires_no_material_boundary": True,
        },
        "summary": {
            "total": len(ideas),
            "pass": counts["pass"],
            "revise": counts["revise"],
            "block": counts["block"],
            "final_ready": counts["pass"],
        },
        "ideas": ideas,
    }


def validate_r3_final_audit(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ideas = payload.get("ideas") or []
    ids = [row.get("idea_id") for row in ideas]
    if len(ideas) != 22:
        errors.append(f"expected 22 R3 ideas, got {len(ideas)}")
    if len(set(ids)) != len(ids):
        errors.append("duplicate R3 idea_id")
    for row in ideas:
        if row.get("verdict") not in VALID_VERDICTS:
            errors.append(f"invalid verdict for {row.get('idea_id')}: {row.get('verdict')}")
        if row.get("confidence") not in {"low", "medium", "high"}:
            errors.append(f"invalid confidence for {row.get('idea_id')}: {row.get('confidence')}")
        for key in ("finding", "finding_zh", "required_action", "required_action_zh"):
            if not row.get(key):
                errors.append(f"missing {key} for {row.get('idea_id')}")
    summary = payload.get("summary") or {}
    if summary.get("pass", 0) + summary.get("revise", 0) + summary.get("block", 0) != len(ideas):
        errors.append("R3 summary counts do not add up")
    return errors


def write_r3_final_audit(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_r3_final_audit()
    errors = validate_r3_final_audit(payload)
    if errors:
        raise ValueError("; ".join(errors))
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.R3_FINAL_AUDIT = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_r3_final_audit(), ensure_ascii=False, indent=2))
