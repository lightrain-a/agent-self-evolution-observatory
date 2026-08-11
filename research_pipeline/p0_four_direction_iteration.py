from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .config import PROJECT_ROOT

SOURCE = Path(__file__).with_name("p0_four_direction_iteration_20260811.json")
PUBLIC_JSON = PROJECT_ROOT / "generated" / "p0-four-direction-iteration.json"
PUBLIC_JS = PROJECT_ROOT / "generated" / "p0-four-direction-iteration.js"


def build_four_direction_iteration() -> dict[str, Any]:
    row = json.loads(SOURCE.read_text(encoding="utf-8"))
    if set(row.get("ideas") or {}) != {
        "update-trust-region",
        "budgeted-evolution-controller",
        "replicated-effect-memory-gate",
        "cross-task-effect-transport-certificate",
    }:
        raise ValueError("four-direction iteration must contain exactly A1/A2/B8/B9")
    if row.get("policy", {}).get("lifecycle_unchanged") is not True:
        raise ValueError("experiment overlay must not rewrite human lifecycle")
    return row


def write_four_direction_iteration(json_path: Path = PUBLIC_JSON, js_path: Path = PUBLIC_JS) -> dict[str, Any]:
    row = build_four_direction_iteration()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.P0_FOUR_DIRECTION_ITERATION = " + json.dumps(row, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return row
