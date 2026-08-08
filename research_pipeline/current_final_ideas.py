from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SOURCE_JSON = PROJECT_ROOT / "generated" / "r32-final-ideas.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "current-final-ideas.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "current-final-ideas.js"

PUBLIC_FIELDS = (
    "idea_id",
    "revision",
    "title",
    "purpose",
    "importance",
    "core_idea",
    "core_intuition",
    "rationale",
    "method_logic",
    "persistent_update_object",
    "learning_signal",
    "independent_ground_truth",
    "strongest_baseline",
    "matched_resources",
    "decisive_pilot",
    "stop_condition",
    "surviving_claim",
    "collision_boundary",
    "r3_repair_summary",
    "remaining_risk",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_current_final_ideas() -> dict[str, Any]:
    source = _load(SOURCE_JSON)
    rows: list[dict[str, Any]] = []
    for raw in source.get("ideas", []):
        row = {key: raw[key] for key in PUBLIC_FIELDS if key in raw}
        if not row.get("idea_id") or not row.get("revision"):
            raise ValueError("current final idea missing idea_id/revision")
        for key, value in row.items():
            if key == "title" or not isinstance(value, dict) or "en" not in value or "zh" not in value:
                continue
            en = str(value.get("en") or "").strip()
            zh = str(value.get("zh") or "").strip()
            if len(en) >= 160 and len(zh) / max(1, len(en)) < 0.18:
                raise ValueError(f"suspiciously truncated bilingual field: {row['idea_id']} {key}")
        rows.append(row)
    if len(rows) != 20 or len({row["idea_id"] for row in rows}) != 20:
        raise ValueError(f"expected 20 unique current final ideas, got {len(rows)}")
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "backend R3.1/R3.2 finalization; raw reviewer/model metadata removed",
        "count": len(rows),
        "ideas": rows,
    }


def write_current_final_ideas(
    json_path: Path = DEFAULT_JSON,
    js_path: Path = DEFAULT_JS,
) -> dict[str, Any]:
    payload = build_current_final_ideas()
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.CURRENT_FINAL_IDEAS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(write_current_final_ideas(), ensure_ascii=False))
