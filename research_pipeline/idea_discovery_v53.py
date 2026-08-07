from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_PROPOSALS_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v53-proposals.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v53.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "idea-discovery-v53.js"
DEFAULT_EXTERNAL_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v53-external-reviews.json"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_idea_discovery_v53() -> dict[str, Any]:
    proposals = _load(DEFAULT_PROPOSALS_JSON).get("children", [])
    reviews = _load(DEFAULT_EXTERNAL_JSON).get("reviews", {})
    rows: list[dict[str, Any]] = []
    for raw in proposals:
        row = dict(raw)
        rs = reviews.get(row.get("id"), [])
        review = rs[-1] if rs else {}
        row["external_reviews"] = rs
        row["external_review_status"] = "reviewed" if rs else "pending"
        row["external_verdict"] = review.get("verdict", "pending")
        row["external_finding"] = review.get("finding", "")
        row["external_finding_zh"] = review.get("finding_zh", "")
        row["external_required_action"] = review.get("required_action", "")
        row["external_required_action_zh"] = review.get("required_action_zh", "")
        rows.append(row)
    order = {"pass": 0, "revise": 1, "pending": 2, "block": 3}
    rows.sort(key=lambda x: (order.get(x["external_verdict"], 2), x.get("parent_rank", 999), x.get("id", "")))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    summary = {
        "children": len(rows),
        "reviewed": sum(x["external_review_status"] == "reviewed" for x in rows),
        "pending": sum(x["external_review_status"] != "reviewed" for x in rows),
        "pass": sum(x["external_verdict"] == "pass" for x in rows),
        "revise": sum(x["external_verdict"] == "revise" for x in rows),
        "block": sum(x["external_verdict"] == "block" for x in rows),
    }
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target_venue": "ICLR",
        "policy": {
            "only_from_v52_revise_with_single_surviving_boundary": True,
            "target_core_pass": 20,
            "stop_after_target": True,
            "no_block_rename": True,
        },
        "summary": summary,
        "children": rows,
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for row in payload.get("children", []):
        if not row.get("id") or not row.get("parent_id"):
            errors.append("missing id/parent")
            continue
        if row["id"] in seen:
            errors.append(f"duplicate {row['id']}")
        seen.add(row["id"])
        for field in (
            "title", "changed_assumption", "exact_mechanism", "independent_ground_truth",
            "simplest_baseline", "decisive_pilot", "stop_condition", "material_change",
        ):
            value = row.get(field)
            if not isinstance(value, dict) or not value.get("zh") or not value.get("en"):
                errors.append(f"{row['id']} missing {field}")
    return errors


def write_idea_discovery_v53(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_idea_discovery_v53()
    errors = validate(payload)
    if errors:
        raise ValueError("Invalid v5.3:\n- " + "\n- ".join(errors))
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.IDEA_DISCOVERY_V53 = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_idea_discovery_v53()["summary"], ensure_ascii=False))
