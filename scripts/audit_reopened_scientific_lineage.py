#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.reopened_scientific_lineage_audit import (
    audit_reopened_scientific_attempt,
    audit_reopened_scientific_portfolio,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit reopened-scientific cross-ledger SHA lineage without granting scientific, experiment, GPU, claim-update, memory-write, or submission authority.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--attempt-sha256", default="")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = audit_reopened_scientific_attempt(args.root, args.attempt_sha256) if args.attempt_sha256 else audit_reopened_scientific_portfolio(args.root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if payload.get("status") in {"FAIL", "REOPENED_SCIENTIFIC_LINEAGE_INVALID"}:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
