#!/usr/bin/env python3
"""Compile the public Stanford R2 objection matrix JSON into a synchronous browser payload."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "generated" / "stanford-r2-objection-matrix.json"
TARGET = ROOT / "generated" / "stanford-r2-objection-matrix.js"


def main() -> int:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    text = "window.STANFORD_R2_OBJECTION_MATRIX = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    TARGET.write_text(text, encoding="utf-8")
    print(f"Wrote {TARGET.relative_to(ROOT)} with {payload['summary']['objections']} objections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
