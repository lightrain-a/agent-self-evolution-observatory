#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_anonymized_submission_projection import sanitize_submission_zip, validate_projection_receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a deterministic anonymized submission projection by redacting private absolute paths only inside JSON/JSONL metadata. The sealed source ZIP is never overwritten and a new submission freeze remains required.")
    parser.add_argument("--source-zip", type=Path, required=True)
    parser.add_argument("--output-zip", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path)
    args = parser.parse_args()
    receipt = sanitize_submission_zip(source_zip=args.source_zip, output_zip=args.output_zip)
    if not validate_projection_receipt(receipt):
        raise RuntimeError("generated anonymized projection receipt failed validation")
    if args.receipt_output:
        args.receipt_output.parent.mkdir(parents=True, exist_ok=True)
        args.receipt_output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    public = {key: receipt[key] for key in ("status", "source_filename", "source_sha256", "sanitized_filename", "sanitized_sha256", "redaction_count", "anonymity_audit_status", "anonymity_audit_sha256", "projection_sha256", "requires_new_submission_freeze", "automatic_refreeze_forbidden")}
    print(json.dumps(public, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
