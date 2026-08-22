#!/usr/bin/env python3
"""Build the read-only ProblemGate-passed / pre-ResearchItem candidate registry."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.pre_researchitem_candidate_registry import (
    build_pre_researchitem_candidate_registry,
    validate_pre_researchitem_candidate_registry,
)


def main() -> None:
    registry = build_pre_researchitem_candidate_registry(ROOT)
    errors = validate_pre_researchitem_candidate_registry(registry)
    if errors:
        raise RuntimeError("invalid pre-ResearchItem candidate registry:\n- " + "\n- ".join(errors))
    generated = ROOT / "generated"
    json_path = generated / "pre-researchitem-candidates.json"
    js_path = generated / "pre-researchitem-candidates.js"
    json_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.PRE_RESEARCHITEM_CANDIDATES = " + json.dumps(registry, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(json_path.relative_to(ROOT))
    print(js_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
