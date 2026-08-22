#!/usr/bin/env python3
"""Build a read-only literature-gap input bundle for later idea generation.

This projection joins the manually curated literature gap registry with the
canonical ResearchItem ledger so downstream generators can collide against
both external published work and the project's own current / terminal work.
It has no scientific or promotion authority.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAPS = ROOT / "literature-idea-mining-data.json"
RESEARCH = ROOT / "generated" / "research-items.json"
OUTPUT = ROOT / "generated" / "literature-idea-mining-input.json"
COLLISION_JS = ROOT / "generated" / "literature-idea-mining-collision.js"


def localized(value):
    if isinstance(value, dict):
        return {"zh": value.get("zh", ""), "en": value.get("en", "")}
    return {"zh": str(value or ""), "en": str(value or "")}


def compact_item(row: dict) -> dict:
    return {
        "code": row.get("code"),
        "category": row.get("category"),
        "title": localized(row.get("title")),
        "scientific_state": row.get("scientific_state"),
        "problem": localized(row.get("problem")),
        "reopen_condition": localized(row.get("reopen_condition")),
        "principle_dead_end_certified": bool(row.get("principle_dead_end_certified", False)),
        "paper_transition": row.get("paper_transition"),
    }


def main() -> None:
    gaps = json.loads(GAPS.read_text(encoding="utf-8"))
    research = json.loads(RESEARCH.read_text(encoding="utf-8"))
    items = research.get("research_items") or []
    item_index = {row.get("code"): compact_item(row) for row in items if row.get("code")}
    directions = {}
    for code, gap in (gaps.get("directions") or {}).items():
        categories = (gaps.get("currentCategoryMap") or {}).get(code, [])
        mapped_codes = [row.get("code") for row in items if row.get("category") in categories and row.get("code")]
        active_codes = [item_code for item_code in mapped_codes if item_index[item_code].get("scientific_state") in {"HOLD", "PAPER_READY"}]
        terminal_codes = [item_code for item_code in mapped_codes if item_index[item_code].get("scientific_state") in {"STOPPED", "MERGED"}]
        directions[code] = {
            "gap": gap,
            "current_categories": categories,
            "current_research_item_codes": mapped_codes,
            "active_or_reopenable_codes": active_codes,
            "terminal_history_codes": terminal_codes,
            "collision_summary": {
                "mapped_research_items": len(mapped_codes),
                "active_or_reopenable": len(active_codes),
                "terminal_history": len(terminal_codes),
                "nearest_published": len(gap.get("nearest") or []),
            },
        }

    payload = {
        "schema_version": "1.0",
        "generated_at": research.get("generated_at"),
        "projection_policy": {
            "read_only": True,
            "scientific_authority": False,
            "experiment_authority": False,
            "promotion_authority": False,
            "gap_is_not_an_idea": True,
            "candidate_must_pass_normal_novelty_and_evidence_gates": True,
            "stopped_or_merged_work_must_not_be_revived_without_reopen_evidence": True,
        },
        "sources": {
            "literature_gap_registry": GAPS.name,
            "research_item_ledger": str(RESEARCH.relative_to(ROOT)),
            "research_item_schema_version": research.get("schema_version"),
            "research_item_source_revision": research.get("source_revision"),
        },
        "basis": gaps.get("basis"),
        "principles": gaps.get("principles") or [],
        "research_items": item_index,
        "directions": directions,
        "intersections": gaps.get("intersections") or [],
        "candidate_contract": gaps.get("candidateContract") or [],
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    collision_projection = {
        "schema_version": "1.0",
        "generated_at": payload["generated_at"],
        "research_items": len(items),
        "source_revision": research.get("source_revision"),
        "directions": {
            code: {
                "current_categories": block["current_categories"],
                "active": [
                    {"code": item_code, "title": item_index[item_code]["title"], "scientific_state": item_index[item_code]["scientific_state"]}
                    for item_code in block["active_or_reopenable_codes"]
                ],
                "mapped_count": block["collision_summary"]["mapped_research_items"],
                "terminal_count": block["collision_summary"]["terminal_history"],
            }
            for code, block in directions.items()
        },
    }
    COLLISION_JS.write_text(
        "window.LITERATURE_IDEA_COLLISIONS = " + json.dumps(collision_projection, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "collision_js": str(COLLISION_JS.relative_to(ROOT)),
        "directions": len(directions),
        "intersections": len(payload["intersections"]),
        "candidate_contract": len(payload["candidate_contract"]),
        "research_items": len(items),
        "active_collision_links": sum(len(v["active_or_reopenable_codes"]) for v in directions.values()),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
