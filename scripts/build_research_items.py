#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.research_item_state import (
    build_paper_registry,
    build_research_item_state,
    validate_paper_registry,
    validate_research_item_state,
)

GEN = ROOT / "generated"


def write_pair(name: str, variable: str, payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    (GEN / f"{name}.json").write_text(text, encoding="utf-8")
    (GEN / f"{name}.js").write_text(
        f"window.{variable} = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    research = build_research_item_state()
    paper = build_paper_registry(research)
    errors = validate_research_item_state(research) + validate_paper_registry(paper, research)
    if errors:
        raise SystemExit("ResearchItem/PaperRegistry validation failed:\n- " + "\n- ".join(errors))
    write_pair("research-items", "RESEARCH_ITEM_STATE", research)
    write_pair("paper-registry", "PAPER_REGISTRY", paper)
    print(
        f"PASS research_items={research['summary']['research_items']} "
        f"experiments={research['summary']['experiment_records']} "
        f"portfolio={research['summary']['portfolio_objects']} "
        f"papers={paper['summary']['papers']}"
    )


if __name__ == "__main__":
    main()
