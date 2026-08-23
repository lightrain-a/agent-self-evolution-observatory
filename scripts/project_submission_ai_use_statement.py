#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_pipeline.paper_venue_compliance_projection import add_ai_use_statement_projection, validate_projection_receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a deterministic submission-source projection that adds an explicit AI Use section before the bibliography. The sealed source is never overwritten and the result requires a new anonymity audit/freeze.")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--source-zip", type=Path, required=True)
    parser.add_argument("--output-zip", type=Path, required=True)
    parser.add_argument("--statement-file", type=Path, required=True)
    parser.add_argument("--main-tex-entry", default="main.tex")
    parser.add_argument("--statement-entry", default="sections/08_ai_use_statement.tex")
    parser.add_argument("--receipt-output", type=Path)
    args = parser.parse_args()
    receipt = add_ai_use_statement_projection(
        paper_id=args.paper_id,
        source_zip=args.source_zip,
        output_zip=args.output_zip,
        statement_text=args.statement_file.read_text(encoding="utf-8"),
        main_tex_entry=args.main_tex_entry,
        statement_entry=args.statement_entry,
    )
    if not validate_projection_receipt(receipt):
        raise RuntimeError("generated venue-compliance projection receipt failed validation")
    if args.receipt_output:
        args.receipt_output.parent.mkdir(parents=True, exist_ok=True)
        args.receipt_output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "paper_id": receipt["paper_id"],
        "source_sha256": receipt["source_sha256"],
        "projected_sha256": receipt["projected_sha256"],
        "statement_sha256": receipt["statement_sha256"],
        "projection_sha256": receipt["projection_sha256"],
        "anonymity_audit_sha256": receipt["anonymity_audit_sha256"],
        "canonical_scientific_artifacts_unchanged": True,
        "requires_new_submission_freeze": True,
        "automatic_refreeze_forbidden": True,
        "submission_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
