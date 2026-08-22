#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.presubmission_freeze import latest
from research_pipeline.revision_impact_audit import audit_freeze_receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify drift from the current pre-submission freeze and return the minimum paper gates that must be rerun. Read-only.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    path = args.root / "paper-submission-freezes" / f"{args.paper_id}.json"
    if not path.exists():
        parser.error("paper has no pre-submission freeze")
    row = json.loads(path.read_text(encoding="utf-8"))
    event = latest(row, "pre-submission-freeze")
    receipt = event.get("receipt") if isinstance(event.get("receipt"), dict) else {}
    if not receipt:
        parser.error("paper has no current freeze receipt")
    result = audit_freeze_receipt(receipt)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
